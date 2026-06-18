# sources/distributed-fs/openafs/src/gtx/Makefile.in

## Purpose
Builds the OpenAFS gtx display-independent window toolkit, installs its public headers, and links several test programs.

## Important APIs, Types, And Functions
The default target builds `liboafs_gtx.la`, `libgtx.a`, and installs headers for curses, dumb, X11, frame, input, keymap, light/text objects, object dictionary, text circular buffers, and window abstractions. Test targets include `object_test`, `screen_test`, `curses_test`, `cb_test`, and `gtxtest`.

## Control Flow
The makefile compiles toolkit modules into libtool objects, links shared/static libraries against rxkad, fsint, cmd, util, opr, and lwp compatibility libraries, then links test binaries with curses and platform libraries. Install/dest targets copy `libgtx.a` and headers into configured AFS lib/include directories.

## State And Persistence
Build outputs include libtool artifacts, static library, test binaries, installed headers, and generated version files. Clean removes objects, libraries, tests, core files, and version output.

## Dependencies And Integration Points
GTX is a UI abstraction used by older OpenAFS tools/tests. It integrates curses, a dumb backend, a mostly stub X11 backend, object/frame/keymap infrastructure, and text buffers.

## Risks And Test Signals
The toolkit is legacy C with K&R-style tests and backend-specific dependencies. Test signals are successful builds with and without curses/X11 headers, header installation, static/shared link success, and manual test execution in a terminal.
