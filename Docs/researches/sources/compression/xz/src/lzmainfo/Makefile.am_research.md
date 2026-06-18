# sources/compression/xz/src/lzmainfo/Makefile.am

## Purpose
Automake rules for building, linking, installing, and uninstalling the `lzmainfo` compatibility tool and its man pages.

## Important APIs, Types, And Functions
Build variables:
- `bin_PROGRAMS = lzmainfo`.
- `lzmainfo_SOURCES` includes `lzmainfo.c` and common tuklib helpers.
- Conditional `lzmainfo_w32res.rc` for Windows.
- `lzmainfo_CPPFLAGS` includes locale/common/liblzma API paths.
- `lzmainfo_LDADD` links liblzma, optional gnulib, and intl.
- `dist_man_MANS = lzmainfo.1`.
- Hooks install/uninstall translated man pages.

## Control Flow
Automake builds the binary, compiles Windows resources when needed, and custom install hooks iterate translated man directories, invoking `install-man` with overridden man variables. Uninstall hook removes translated man pages.

## State And Persistence
No runtime state. Installation creates binary and man page artifacts.

## Dependencies And Integration Points
Integrates with top-level gettext/NLS, gnulib, liblzma, Windows resource compiler, and po4a translated man page layout.

## Risks
Install hooks rely on Automake internals and shell loops. Translated man installation depends on directory presence. Link order places `LTLIBINTL` after libgnu as needed.

## Test Signals
`make`, `make install DESTDIR=...`, `make uninstall`, Windows resource builds, and NLS enabled/disabled builds.
