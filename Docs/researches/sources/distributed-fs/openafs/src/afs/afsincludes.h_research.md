# sources/distributed-fs/openafs/src/afs/afsincludes.h

Purpose: aggregate AFS kernel/cache-manager headers in a consistent order, with a UKERNEL redirect. It is the project-local counterpart to `sysincludes.h`.

Important APIs/types: defines only the include guard `AFS_INCLUDES_H`; it exports no functions. It includes AFS core headers such as `afs/stds.h`, `roken.h`, `afs/opr.h`, `rx/rx.h`, `afs/afs_osi.h`, `afs/lock.h`, `volerrors.h`, `voldefs.h`, `afsint.h`, `exporter.h`, `vldbint.h`, `afs.h`, `afs_chunkops.h`, `rxkad.h`, `prs_fs.h`, `dir.h`, `afs_axscache.h`, `icl.h`, `afs_stats.h`, `afs_prototypes.h`, and `discon.h`.

Control flow: compile-time only. For `UKERNEL`, it delegates to `UKERNEL/afsincludes.h`; otherwise it selects OS-specific `osi_vfs.h` and `osi_machdep.h` includes and normalizes Linux macro conflicts by undefining `TRUE`, `FALSE`, `__NFDBITS`, and `__FDMASK` before protocol headers.

State and persistence: none.

Dependencies and integration points: included by major cache-manager C files after `sysincludes.h`, making it the common dependency surface for OpenAFS structs, RPC interfaces, locking, errors, stats, and prototypes.

Risks: include order changes can break kernel builds because OS headers and AFS protocol headers define overlapping names. Linux macro undefines are compatibility-sensitive. Adding new headers here increases rebuild scope and can introduce platform-only compile errors.

Test signals: build matrix across Linux, Darwin, BSD, AIX/HPUX/Solaris/SGI where supported; verify no duplicate macro/type conflicts and that UKERNEL builds continue to use the alternate include set.
