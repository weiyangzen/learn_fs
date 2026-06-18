# Research: sources/compression/xz/src/xz/private.h
## sources/compression/xz/src/xz/private.h

Purpose: Central private include for the xz command-line front-end implementation.

Important contents: Includes generated/system definitions, threading abstraction, liblzma, common POSIX/stdio headers, gettext/progname/exit/multibyte tuklib helpers, Windows headers when needed, stdio descriptor fallbacks, `USE_SIGTSTP_HANDLER` feature detection, and all local module headers (`main`, `mytime`, `coder`, `message`, `args`, `hardware`, `file_io`, `options`, `sandbox`, `signals`, `suffix`, `util`, optional `list`).

Control flow and integration: Nearly every `.c` file in this set includes `private.h`, making it the compile-time dependency hub and enforcing header ordering.

State and persistence: No runtime state, but it defines macros and declarations that shape runtime behavior, especially SIGTSTP support and Windows descriptor compatibility.

Risks: Include-order changes can break dependencies such as `hardware.h` needing `enum operation_mode`, list declarations only with decoders, or Windows macro setup before `windows.h`. Broad inclusion increases rebuild and coupling.

Test signals: Build matrix across POSIX, Windows/MSVC, MinGW, decoder/encoder disabled, threading enabled/disabled, SIGALRM/SIGTSTP availability, and NLS/multibyte configurations.
