## sources/distributed-fs/openafs/src/afs/NBSD/osi_machdep.h

Purpose: central NetBSD OSI compatibility header mapping OpenAFS portable kernel abstractions to NetBSD kernel types, functions, locks, credentials, syscall args, vnode/VFS fields, and time/string helpers.

Important APIs/types/macros: defines `RXK_LISTENER_ENV`, `AFS_DIRENT`, `osi_vfs`/mount field aliases, `VN_HOLD`, `VN_RELE`, `struct afs_sysargs`, uio field aliases and `AFS_UIOSYS`/`AFS_UIOUSER`, `afs_proc_t`, `osi_curproc`, `getpid`, `afs_ucred_t`, credential accessors and ref/free macros, `afs_hz`, `osi_Time`, string helpers, `printk`, `setgroups`, `UVM`, lookup wrappers, GLOCK macros, `SPLVAR`/`NETPRI`/`USERPRI`, `enum vcexcl`, vnode type setters, `IsAfsVnode`, `SetAfsVnode`, `AFS_USE_NBSD_NAMECACHE`, and inline `osi_GetTime`.

Control flow: no standalone runtime flow, but macros expand into real lock/credential/time behavior throughout the NetBSD port. GLOCK implementation differs by `AFS_GLOBAL_SUNLOCK` and NetBSD version: NetBSD 5+ uses `kmutex_t`, older code uses `struct lock`, and a fallback branch asserts GLOCK as always true.

Dependencies and integration: included indirectly by `afs_osi.h`. It depends on NetBSD kernel headers for locks, mutexes, rwlocks, syscall args, kauth, vnode/mount structures, and time. It declares `afs_nbsd_lookupname` and `afs_nbsd_getnewvnode`, tying into `osi_vfsops.c` and `osi_vcache.c`.

State and persistence: no storage itself, but determines how global locking, credentials, process identity, vnode fields, and time are accessed.

Risks: macro-heavy OS ports are fragile under kernel API changes. Duplicate `ISAFS_GLOCK` definitions in conditional branches, older lock APIs, and field aliases can break silently at compile time or create lock assertion gaps. Credential macros map directly to kauth APIs and must match NetBSD lifecycle rules.

Test signals: full NetBSD build matrix, lock-debug kernels, credential/PAG tests, vnode creation/access, lookupname calls, uio read/write paths, and time-dependent callbacks.
