# sources/compression/xz/src/xz/Makefile.am

## Purpose
Automake rules for building and installing the main `xz` command, optional list-mode sources, compatibility symlinks, Windows resources, and translated man-page aliases.

## Important APIs, Types, And Functions
Build variables:
- `bin_PROGRAMS = xz`.
- `xz_SOURCES` lists command modules, headers, and common tuklib helpers.
- `COND_MAIN_DECODER` adds `list.c/.h`.
- `COND_W32` adds resource file.
- `xz_CPPFLAGS` include locale/common/liblzma API paths.
- `xz_LDADD` links liblzma, optional gnulib, and intl.
- `xzlinks` includes `unxz`, `xzcat`, and optional LZMA Utils names.
- Install/uninstall hooks create/remove executable and man-page symlinks.

## Control Flow
Automake compiles the main program, conditionally includes decoder list support and Windows resource compilation, links libraries in the required order, installs `xz.1`, and creates symlinks for executable aliases and man-page aliases. Uninstall removes those aliases and man pages.

## State And Persistence
Installation mutates bindir and mandir through files/symlinks. No runtime state.

## Dependencies And Integration Points
Integrates with liblzma, common tuklib code, gnulib, gettext/NLS, Windows resource compiler, and po4a translated man directories.

## Risks
Source list must stay synchronized with actual command modules. Link order around `libgnu.a` and `LTLIBINTL` matters. Install hooks rely on shell portability and Automake internals. Optional alias support changes installed surface area.

## Test Signals
`make`, `make check`, `make install/uninstall DESTDIR=...`, builds with/without main decoder, with/without LZMA links, NLS translated man pages, program-name transforms, and Windows resource builds.
