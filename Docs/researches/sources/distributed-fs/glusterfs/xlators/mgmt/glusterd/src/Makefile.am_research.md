# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/Makefile.am

Purpose: defines how the `glusterd` management translator shared module is compiled, linked, installed, and given generated preprocessor paths.

Important APIs/types/functions: guarded by `WITH_SERVER`, `xlator_LTLIBRARIES = glusterd.la`; module install path is `$(libdir)/glusterfs/$(PACKAGE_VERSION)/xlator/mgmt`. `glusterd_la_SOURCES` lists core daemon, op-state-machine, volume, brick, bitrot, geo-rep, snapshot, service, connection, ganesha, and snapshot backend sources. `noinst_HEADERS` lists internal headers. `AM_CPPFLAGS` defines include paths and runtime constants such as `SBIN_DIR`, `DATADIR`, `CONFDIR`, `GANESHA_PREFIX`, and `SYNCDAEMON_COMPILE`.

Control flow: Automake compiles all listed sources into `glusterd.la`, links libglusterfs, RPC/XDR libraries, XML, crypto, userspace-RCU, dl, and management-specific libs. `install-data-hook` optionally moves existing `/etc/glusterd` state into `GLUSTERD_WORKDIR` and symlinks the old config path.

State and persistence behavior: the build file itself has no runtime state, but it defines paths that glusterd code uses for persistent workdir/config, shared storage ganesha config, and libexec helpers. The install hook can mutate installation-time glusterd state layout.

Dependencies and integration points: integrates many glusterd source files into one xlator module and binds external dependencies (`libglusterfs`, `libgfrpc`, `libgfxdr`, XML, OpenSSL, URCU). Ganesha code depends on `CONFDIR` and `GANESHA_PREFIX` from this file.

Risks and edge cases: source/header list drift causes missing symbols or stale files in dist builds. Hard-coded generated path macros must match deployment packaging. The install hook uses shell commands with `DESTDIR`/`sysconfdir`/`GLUSTERD_WORKDIR`; packaging should validate symlink behavior.

Test signals: build with and without `WITH_SERVER`, `make distcheck`, link checks for all glusterd symbols, install tests for workdir migration, and package tests validating generated path macros.
