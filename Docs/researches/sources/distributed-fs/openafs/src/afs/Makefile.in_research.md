## sources/distributed-fs/openafs/src/afs/Makefile.in

Purpose: automake-style makefile fragment for generating and installing common AFS client headers, trace catalogs, and unified error/message sources.

Important targets and outputs: `all` delegates to `depinstall`. `generated` builds `afs_trace.h`, `afs_trace.msf`, `unified_afs.c`, and `unified_afs.h`. The `afs_trace.*` and `unified_afs.*` targets run `COMPILE_ET_H`/`COMPILE_ET_C` against `.et` inputs. `afszcm.cat` invokes `GENCAT` with OS-specific flags. `depinstall`, `install`, and `dest` install headers such as `afs.h`, `afs_consts.h`, `afs_stats.h`, `exporter.h`, `nfsclient.h`, `sysctl.h`, generated headers, and the platform-specific `${MKAFS_OSTYPE}/osi_inode.h`. Linux installs also copy `${MKAFS_OSTYPE}/osi_vfs.h`. `clean` removes generated and object artifacts.

Control flow: make dependencies ensure generated trace/error artifacts exist before install. The `case ${SYS_NAME}` blocks handle catalog generation syntax differences for SGI, Linux/umlinux, Darwin, and other systems, and selectively install VFS headers only on Linux.

Dependencies and integration: depends on `Makefile.config`, `Makefile.lwp`, configured variables (`TOP_OBJDIR`, `TOP_INCDIR`, `DESTDIR`, `includedir`, `afsdatadir`, `DEST`, `SYS_NAME`, `MKAFS_OSTYPE`), install tools, error-table compilers, `GENCAT`, and `Makefile.version`. It integrates the `src/afs` headers into both build-tree dependency includes and staged installation trees.

State and persistence: writes generated C/header/message catalog files and installed header/catalog copies. No runtime state.

Risks: OS-specific `gencat` flags and install paths can diverge. The `install` and `dest` targets have parallel but not identical destination roots, so changes must be mirrored. Platform header selection via `${MKAFS_OSTYPE}` is sensitive to configure output. Linux-only `osi_vfs.h` installation is guarded with `|| true`, which can hide missing-file issues.

Test signals: `make depinstall`, `make generated`, staged `make install DESTDIR=...`, `make dest`, catalog generation on Linux/Darwin/other targets, clean regeneration, and include-tree checks for `afs/osi_inode.h`, `afs/osi_vfs.h` on Linux, and generated `unified_afs.h`/`afs_trace.h`.
