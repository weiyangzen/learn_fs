# sources/distributed-fs/glusterfs/glusterfsd/src/Makefile.am

Purpose: Automake rules for building and installing the GlusterFS daemon binaries: `glusterfsd`, conditionally `gf_attach`, plus compatibility symlinks `glusterfs` and `glusterd`.

Important build declarations: `sbin_PROGRAMS` always includes `glusterfsd`; under `WITH_SERVER`, it also includes `gf_attach` and repeats `glusterfsd`. `glusterfsd_SOURCES` are `glusterfsd.c` and `glusterfsd-mgmt.c`; `gf_attach_SOURCES` is `gf_attach.c`. Both link against `libglusterfs`, RPC libraries, and XDR libraries; `gf_attach` also links `libgfapi`. `noinst_HEADERS` lists daemon-private headers. `AM_CPPFLAGS` injects config paths (`DATADIR`, `CONFDIR`, `XLATORDIR`, `LIBEXECDIR`) and include paths for libglusterfs, RPC, XDR, NFS/server, protocol/server, and API headers.

Control flow: A dependency rule forces `libglusterfs.la` to build before daemon linking. `install-data-local` creates runtime/log directories and installs symlinks: `glusterfs -> glusterfsd`, and under `WITH_SERVER`, `glusterd -> glusterfsd`. `uninstall-local` removes those symlinks.

State and persistence: Persists installed binaries, symlinks, and directories under `$(localstatedir)/run`, `$(localstatedir)/run/gluster`, and `$(localstatedir)/log/glusterfs`.

Dependencies and integration: This is the build integration point for daemon startup (`glusterfsd.c`), management RPC (`glusterfsd-mgmt.c`), and brick attach helper (`gf_attach.c`). Compile-time macros define the runtime paths consumed by the C code.

Risks: The conditional `sbin_PROGRAMS += glusterfsd gf_attach` duplicates `glusterfsd` when `WITH_SERVER` is enabled; Automake usually tolerates this but it is fragile. Symlink install/remove uses `rm -f` and `ln -s`, so package scripts must ensure correct permissions and paths.

Test signals: `make`, `make install DESTDIR=...`, and package builds with and without `WITH_SERVER` should verify program lists, link dependencies, and symlink creation.
