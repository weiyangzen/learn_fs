# File Research: sources/block-storage/vdo/utils/vdo/man/Makefile

Installs VDO utility man pages.

Key details:
- `INSTALLFILES` includes manpages for `adaptlvm`, all built VDO utilities, and `vdorecover`.
- `all` and `clean` are no-ops.
- `install` creates `$(DESTDIR)/$(mandir)/man8` and installs each manpage mode `644`.
- Defaults `mandir` to `/usr/man`.

Risk notes:
- The install path is `$(DESTDIR)/$(mandir)`, so if `mandir` is absolute the double slash is harmless but nonstandard-looking.
