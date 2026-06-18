<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/laptop/freefall/Makefile -->
# sources/distributed-fs/ceph-client/tools/laptop/freefall/Makefile

Purpose: this Makefile builds and installs the `freefall` laptop disk-protection daemon.

Important APIs/targets: configurable variables include `PREFIX`, `SBINDIR`, and `INSTALL`. `TARGET = freefall`. Pattern rule `%: %.c` compiles with `$(CC) $(CFLAGS) $(LDFLAGS)`. Targets are `all`, `clean`, and `install`.

Control flow: `all` builds `freefall`; `clean` removes it; `install` copies it to `$(DESTDIR)$(PREFIX)/$(SBINDIR)/freefall` with mode 755.

State and persistence: generated executable and installed binary are the only artifacts.

Dependencies/integration: depends on a C compiler and install utility. It deliberately uses standard make variables for distro packaging.

Risks and test signals: test build with custom `CC/CFLAGS/LDFLAGS`, staged install with `DESTDIR`, and clean idempotence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/laptop/freefall/Makefile -->
