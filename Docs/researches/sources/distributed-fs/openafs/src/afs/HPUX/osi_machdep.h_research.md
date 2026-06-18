# sources/distributed-fs/openafs/src/afs/HPUX/osi_machdep.h

## sources/distributed-fs/openafs/src/afs/HPUX/osi_machdep.h

Purpose: HP-UX machine-dependent OSI header that maps portable OpenAFS OS abstractions to HP-UX kernel APIs for time, credentials, process identity, vnode I/O, lookup, global locking, sleep/wakeup, SPL, and VM support.

Important APIs/types/functions: defines `afs_ucred_t`, `afs_proc_t`, `osi_Time`, `gop_rdwr`, `gop_lookupname`, `osi_curcred`, `getpid`, `getppid`, `AFS_GLOCK`, `AFS_GUNLOCK`, `ISAFS_GLOCK`, `NETPRI`, `USERPRI`, `afs_osi_Sleep` or function prototypes for HP-UX 11, `osi_NullHandle`, `osi_procname`, and inline `osi_GetTime`.

Control flow: macro control flow differs by HP-UX version. Older HP-UX uses alpha semaphores and direct `sleep`; HP-UX 11 beta semaphore paths call functions in `osi_sleep.c`. MP builds store semaphore save areas in the hash table declared here and implemented in `osi_vnodeops.c`.

State/persistence: declares the global AFS semaphore and per-thread semaphore-save hash hooks. No durable state, but lock ownership controls all AFS kernel state mutation.

Dependencies/integration: includes HP-UX kernel semaphore/process/vfs VM headers and is included indirectly by `afs_osi.h`.

Risks/test signals: incorrect global-lock macros can deadlock or restore wrong semaphore state. Time and credential macros assume `u.u_procp`/`u.u_kthreadp` layout. Test nested AFS calls, sleeps while holding global lock, MP thread concurrency, and HP-UX 10/11 build variants.
