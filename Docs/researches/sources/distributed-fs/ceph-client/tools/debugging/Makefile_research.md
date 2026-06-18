# sources/distributed-fs/ceph-client/tools/debugging/Makefile

Purpose: Installs the shell debugging utility `kernel-chktaint`.

Important APIs, types, and functions: Defines `PREFIX`, `BINDIR`, `INSTALL`, `TARGET`, `all`, empty `clean`, and `install`.

Control flow: `all` depends on the script target. `install` copies it executable to `$(DESTDIR)$(PREFIX)/$(BINDIR)/kernel-chktaint`.

State and persistence: Install writes one executable file to the destination.

Dependencies and integration points: Part of kernel tools install flow. Uses standard `install`.

Risks: `clean` intentionally does nothing because the target is source. Build rule relies on the existing script file.

Test signals: `make install DESTDIR=...` and verifying mode/path.
