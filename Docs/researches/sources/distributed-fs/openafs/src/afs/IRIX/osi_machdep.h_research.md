# sources/distributed-fs/openafs/src/afs/IRIX/osi_machdep.h

## sources/distributed-fs/openafs/src/afs/IRIX/osi_machdep.h

Purpose: IRIX machine-dependent OSI header mapping portable OpenAFS concepts to IRIX kernel locks, credentials, VFS/vnode behavior descriptors, process/thread identity, time, sleep primitives, and vnode operation argument conversion.

Important APIs/types/functions: defines `afs_ucred_t`, `afs_proc_t`, `osi_Time`, lookup and rdwr macros, `AFS_GLOCK`, `AFS_GUNLOCK`, `ISAFS_GLOCK`, `AFS_MUTEX_ENTER`, `cv_wait`, `cv_timedwait`, `osi_InitGlock`, `afs_suser`, `OSI_GET_CURRENT_*` accessors, `OSI_GET_LOCKID`, and `OSI_VN/VC/VFS_*` behavior descriptor conversion macros.

Control flow: MP builds use a real `afs_global_lock` mutex with assertions against recursive ownership; non-MP builds compile global locking away. CV macros release and reacquire the global lock through IRIX sv primitives. VOP wrappers use behavior descriptors instead of direct vnode pointers.

State/persistence: declares/uses `afs_global_lock` and thread identity values for rwlock ownership debugging. No durable state.

Dependencies/integration: depends on IRIX sema, pda, flock, process, uthread, behavior descriptor, and capability APIs. It is central to all IRIX platform files.

Risks/test signals: recursive lock assertions, mutex owner edge cases, behavior descriptor conversions, and credential macros are all kernel-version sensitive. Test MP and non-MP builds, sleep/wakeup under global lock, vnode/VFS operation dispatch, and rwlock owner tracking.
