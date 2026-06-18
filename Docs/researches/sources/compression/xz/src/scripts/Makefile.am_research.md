# sources/compression/xz/src/scripts/Makefile.am

## Purpose
Automake rules for installing shell wrapper scripts (`xzdiff`, `xzgrep`, `xzmore`, `xzless`), compatibility symlinks, and translated man page symlinks.

## Important APIs, Types, And Functions
Build variables:
- `nodist_bin_SCRIPTS = xzdiff xzgrep xzmore xzless`.
- `dist_man_MANS` lists four man pages.
- `links` maps target-link pairs for xzcmp/xzegrep/xzfgrep and optional LZMA-compatible names.
- `install-exec-hook`, `install-data-hook`, and `uninstall-hook`.

## Control Flow
Install hooks create executable symlinks in bindir, install translated man pages if available, and create man-page symlinks matching executable aliases. Uninstall hooks remove symlinks and man-page aliases.

## State And Persistence
Installation mutates bindir and mandir contents through symlinks and installed man pages.

## Dependencies And Integration Points
Uses Automake transforms, `LN_S`, gettext/po4a man directories, and `COND_LZMALINKS`.

## Risks
Shell quoting around transformed names and directories must remain portable. Man-page symlinks are only made when target man page exists. Hooks rely on Automake internals for translated man installation.

## Test Signals
`make install/uninstall DESTDIR=...` with and without `COND_LZMALINKS`, with NLS translated man directories, and with program name transforms.
