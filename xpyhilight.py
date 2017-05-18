"""xPyHilight v0.8b

A script for Xchat, HexChat and Xchat-WDK to log highlights
in a separate window.

It does not output anything publically.

Installation:
-------------
The script is ready to go out of the box, but there are some
settings you could modify if felt needed.
Settings are described below.
Drop the file to ~/.config/hexchat/addons or load it in client
via Window -> Plugins and Scripts menu.

Dependencies:
-------------
* Python	2.7.3	<http://python.org/>
* Python	3	<http://python.org/>

"""

__module_name__ 		= "xPyHilight"
__module_version__ 		= "0.8c"
__module_description__ 	= "Keeps track of highlights"

import xchat
from time import strftime

##
# The name of the window where highlights are logged.
#
# Must not be a valid IRC channel- or nickname as it may then collide 
# with an actual entity.
##
WINDOW_NAME = "(Highlights)"

##
# The default value for the /SET VARIABLE `tab_new_to_front`.
#
# The plugin temporarily changes the setting and will set it
# to this value afterwards.
#
# Find out the default value by executing the following command:
# /SET tab_new_to_front
##
DEFAULT_SET_VALUE = 2

##
# Time formatting.
#
# Must comply with the parameter passed to time.strftime()
# <http://docs.python.org/2/library/time.html#time.strftime>
##
TIME_FORMAT = "%H:%M:%S"

##
# The text formatting for the logger.
#
# The dict items correspond to Xchat Text Events:
# MESSAGE: Channel Msg Hilight
# ACTION: Channel Action Hilight
#
# Both of these must be defined.
#
# Values must be a tuple with 2 items, where the first
# item is the left hand side and the second the
# right hand side of the separator.
#
# Each value is used with the String formatting operator (%)
# with named mappings.
# <http://docs.python.org/2/library/stdtypes.html#string-formatting>
#
# The following information is available:
# - channel
# - time
# - mode
# - nick
# - text
# All of them are sent to both tuple items,
# and any of them can be omitted.
#
# IRC specific text formatting codes can be represented
# as specified:
#
# Type				HEX		OCT
# -----------------------------
# Bold				0x02	002
# Color				0x03	003  (with 2 digits after, f.ex. \00304 = color 4)
# Underlined		0x1F	037
# Reverse/Italic	0x16	026
# Out/Escape		0x0F	017
##
OUT = {
	"MESSAGE": ("%(channel)s", "\00321[%(time)s] <\002%(mode)s%(nick)s\002> %(text)s\017"),
	"ACTION": ("%(channel)s", "\00321[%(time)s] * \002%(mode)s%(nick)s\002 %(text)s\017")
}

##
# Specifies whether highlights should only be logged when
# you are away.
##
ONLY_AWAY = False

def catch_hilight(word, word_eol, userdata):
	if ONLY_AWAY:
		# If you are not away
		if xchat.get_info("away") is None:
			return xchat.EAT_NONE

	channel = xchat.get_info("channel")
	server = xchat.get_info("server")  # used to find the context
	timestamp = strftime(TIME_FORMAT)
	nick, message = word[:2]
	mode = word[2] if len(word) >= 3 else ""

	data = {
		"channel": channel,
		"time": timestamp,
		"mode": mode,
		"nick": nick,
		"text": message
	}

	# Turns off automatic focusing of new tabs.
	xchat.command("set -quiet tab_new_to_front 0")
	# Opens a new window if there is none already.
	xchat.command("query -nofocus %s" % WINDOW_NAME)
	# Resets the focusing settings.
	xchat.command("set -quiet tab_new_to_front %d" % DEFAULT_SET_VALUE)
	# Fetches the context object of the window.
	context = xchat.find_context(server=server, channel=WINDOW_NAME)

	if context is not None:
		context.emit_print("Generic Message",
						   OUT[userdata][0] % data,
						   OUT[userdata][1] % data
						)
	else:  # this should never happen
		xchat.emit_print("Generic Message",
						 __module_name__,
						 "Unknown error: Unable to create context object"
					)

	return xchat.EAT_NONE

xchat.hook_print("Channel Msg Hilight", catch_hilight, userdata="MESSAGE")
xchat.hook_print("Channel Action Hilight", catch_hilight, userdata="ACTION")

print(__module_name__, __module_version__, "script loaded\003")
