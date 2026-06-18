# subset-b-007750 OpenAFS platform research

This grouped report covers the requested FreeBSD, HP-UX, and IRIX OpenAFS platform files. Each section preserves the source path and is bounded for deterministic reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/FBSD/osi_vnodeops.c -->
## sources/distributed-fs/openafs/src/afs/FBSD/osi_vnodeops.c

Purpose: implements the FreeBSD vnode operation vector for AFS, translating FreeBSD VOP calls into the portable OpenAFS vnode/cache routines while handling FreeBSD VM pager integration. It is the main kernel-facing filesystem operation table for FreeBSD clients.

Important APIs/types/functions: `afs_vnodeops` registers handlers for lookup, create, open/close, read/write, `getpages`, `putpages`, ioctl, fsync, directory operations, reclaim, strategy, pathconf, and advisory locks. `GETNAME`/`DROPNAME` copy FreeBSD `componentname` names into NUL-terminated buffers. Compatibility helpers wrap changing FreeBSD VM object/page locking APIs and pbuf allocation. The operation bodies call core AFS APIs such as `afs_lookup`, `afs_create`, `afs_open`, `afs_close`, `afs_access`, `afs_getattr`, `afs_setattr`, `afs_read`, `afs_write`, `afs_remove`, `afs_link`, `afs_rename`, `afs_mkdir`, `afs_rmdir`, `afs_symlink`, `afs_readdir`, `afs_readlink`, `afs_fsync`, `afs_FlushVCache`, `afs_ustrategy`, and `afs_lockctl`.

Control flow: most VOPs acquire `AFS_GLOCK`, call the core AFS implementation with `VTOAFS`/`AFSTOV` conversions, and release the lock before returning. Lookup has special parent-directory lock ordering for `ISDOTDOT`, converts ENOENT during create/rename into `EJUSTRETURN`, and saves names when the namei operation needs them. Rename handles cross-mount rejection, same-vnode removal conversion, explicit vnode reference release, and core `afs_rename`. `getpages` maps FreeBSD VM pages into a pbuf kva range, builds a kernel `uio`, reads through `afs_read`, then marks pages valid/clean. `putpages` maps busy pages, selects a stored writer credential when available, writes via `afs_write`, undirties successful pages, and frees the held credential.

State/persistence: vnode state lives in `struct vcache` and FreeBSD `struct vnode`. Opens, writer credentials, VM object pages, and callback-derived cache state are updated through core AFS calls. Writes and pager writes persist through cache-manager store paths; `vn_pages_remove` invalidates written VM ranges. `reclaim` drops the vnode lock to avoid lock inversion, obtains `afs_xvcache`, calls `afs_FlushVCache`, clears `CVInit`, destroys the vnode object, and clears `v_data`.

Dependencies/integration: depends on FreeBSD VFS, namei, vnode pager, vm_page/vm_object APIs, pmap kva mapping, and OpenAFS global locking. It integrates with FreeBSD `vop_vector` registration and version-specific VM interfaces.

Risks/test signals: high-risk areas are lock ordering in lookup/reclaim/rename, credentials used during pager writeback, partial-page EOF handling, vnode-doomed close behavior, and FreeBSD-version compatibility macros. Test with pathname create/remove/rename/link/symlink, mmap read/write, fsync, forced vnode reclaim, pager writeback from syncer context, directory cookies, and advisory locks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/FBSD/osi_vnodeops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/HPUX/osi_debug.c -->
## sources/distributed-fs/openafs/src/afs/HPUX/osi_debug.c

Purpose: this HP-UX file is effectively an include aggregation unit for AFS debug-related kernel symbols. It pulls in platform and AFS headers but defines no functions or persistent state.

Important APIs/types/functions: there are no local APIs. The included headers expose callback queue, DNLC, stats, sysname, trace, exporter, rx/fcrypt, NFS client, private data, and Vice structures to whatever object context this file was intended to satisfy.

Control flow: none. Loading or compiling the file only validates that the selected HP-UX build environment can include these headers together.

State/persistence: none locally. Any state is in included modules such as tracing, stats, or callback queues.

Dependencies/integration: depends on `afsconfig.h`, `param.h`, HP-UX system includes, OpenAFS internal headers, and RX crypto headers. It likely exists for legacy build/link compatibility rather than runtime logic.

Risks/test signals: risk is header drift: incompatible typedefs, macros, or include ordering can break HP-UX builds. Build-only tests are the meaningful signal; runtime tests are not applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/HPUX/osi_debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/HPUX/osi_file.c -->
## sources/distributed-fs/openafs/src/afs/HPUX/osi_file.c

Purpose: implements HP-UX cache-file operations used by the AFS disk cache when the cache type is UFS. It opens cache inodes, stats/truncates cache files, and performs kernel-space reads and writes through vnode I/O.

Important APIs/types/functions: `osi_UFSOpen`, `afs_osi_Stat`, `osi_UFSClose`, `osi_UFSTruncate`, `osi_DisableAtimes`, `afs_osi_Read`, `afs_osi_Write`, and `shutdown_osifile`. It manages static `afs_osi_cred` and `afs_osicred_initialized`, uses `cacheDev`, `afs_cacheVfsp`, `igetinode`, `VOP_GETATTR`, `VOP_SETATTR`, `gop_rdwr`, and `struct osi_file`.

Control flow: `osi_UFSOpen` verifies UFS cache type, initializes a held static credential, allocates `osi_file`, drops the AFS global lock around `igetinode`, panics on inode lookup failure, unlocks the inode, and stores vnode/size/offset. Reads and writes optionally set the file offset, drop `AFS_GLOCK` around `gop_rdwr`, update offset by transferred bytes, and convert positive kernel errors into negative OpenAFS-style returns. Reads retry up to five times on `EFAULT`; writes warn on `ENOSPC` and invoke an optional completion callback.

State/persistence: persistent state is the UFS cache file contents and inode attributes. `osi_UFSTruncate` only shrinks files after a stat check, temporarily swaps process credentials because HP-UX UFS consults `u.u_cred`, and restores credentials afterward. `osi_DisableAtimes` suppresses atime writes by clearing `IACC`.

Dependencies/integration: depends on HP-UX UFS inode/vnode behavior, `afs/osi_inode.h`, OpenAFS stats/tracing, global lock transitions, and current process credential APIs.

Risks/test signals: high risks are credential swapping, panic-on-open-failure semantics, EFAULT retry masking, offset accounting after partial I/O, and atime suppression. Test cache open/read/write/truncate/close, low-space writes, cache inode disappearance, shutdown with null file reads, and HP-UX UFS credential behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/HPUX/osi_file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/HPUX/osi_gcpags.c -->
## sources/distributed-fs/openafs/src/afs/HPUX/osi_gcpags.c

Purpose: implements HP-UX process-table traversal for PAG garbage collection when `AFS_GCPAGS` is enabled. It lets shared AFS code scan active process credentials and count live PAG users.

Important APIs/types/functions: `afs_osi_TraverseProcTable` and `afs_osi_proc2cred`. It calls `afs_GCPAGs_perproc_func`, `p_cred`, `system_proc`, and HP-UX process locking primitives.

Control flow: traversal locks `activeproc_lock`, `sched_lock`, and process credential state with `pcred_lock`, walks the active-process chain via `p_fandx`, skips system processes, locks each process with `mp_mtproc_lock`, calls the generic PAG scanner, then unlocks in reverse order. `afs_osi_proc2cred` returns `p_cred(p)` or no value for NULL.

State/persistence: no persistent state is created; it observes process credentials while locks are held. Results are consumed by shared PAG garbage collection state elsewhere.

Dependencies/integration: tightly coupled to HP-UX private process list and credential locking rules. The comment notes ambiguity between documented `mp_mtproc_lock` and actual `pcred_lock` usage, so it uses both.

Risks/test signals: returning without an explicit NULL for null process is a C compatibility risk. Lock ordering and long scans under global process locks can affect scheduler latency. Test with PAG creation/destruction, many active processes, concurrent `setgroups`, and builds with `AFS_GCPAGS` disabled/enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/HPUX/osi_gcpags.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/HPUX/osi_groups.c -->
## sources/distributed-fs/openafs/src/afs/HPUX/osi_groups.c

Purpose: implements HP-UX PAG embedding in group lists and wraps `setgroups` so existing PAGs survive group-list changes.

Important APIs/types/functions: `Afs_xsetgroups`, `setpag`, static `afs_getgroups`, and static `afs_setgroups`. It uses `PagInCred`, `afs_IsPagId`, `afs_genpag`, `afs_get_pag_from_groups`, `afs_get_groups_from_pag`, `AddPag`, `crdup`, `crfree`, `set_p_cred`, `cred_lock`, and HP-UX `setgroups`.

Control flow: `Afs_xsetgroups` initializes an AFS request from the current credential, calls the real `setgroups`, and restores the previous PAG if the new groups do not already contain one. `setpag` generates a PAG when requested, reads the current groups, shifts the group list by two slots if no PAG is present, writes the encoded PAG into the first two groups, and calls `afs_setgroups`. `afs_setgroups` either duplicates credentials for current-process replacement or edits the parent credential under credential locks.

State/persistence: PAG state is persisted in the first two group slots of HP-UX credentials. Credential pointers may be replaced on the process or modified in place when `change_parent` is true.

Dependencies/integration: integrates with OpenAFS authentication/PAG logic and HP-UX credential internals. Conditional locking handles HP-UX 11 variants.

Risks/test signals: risks include exceeding `NGROUPS`, races when editing shared credentials, preserving PAG through `setgroups`, and compatibility with parent credential mutation. Test `pagsh`, token visibility after `setgroups`, max group counts, multi-threaded credential changes, and both `change_parent` modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/HPUX/osi_groups.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/HPUX/osi_inode.c -->
## sources/distributed-fs/openafs/src/afs/HPUX/osi_inode.c

Purpose: implements HP-UX UFS inode syscalls used by OpenAFS server/salvager tooling to create, open, and adjust special Vice cache/server inodes.

Important APIs/types/functions: `getinode`, `igetinode`, `iforget`, `afs_syscall_icreate`, `afs_syscall_iopen`, and `afs_syscall_iincdec`. It uses HP-UX `iget`, `ialloc`, `iput`, `idrop`, `falloc`, vnode fileops, and inode fields defined in `osi_inode.h`.

Control flow: `getinode` resolves a mount from `vfsp` or `dev`, then calls `iget`. `igetinode` validates allocation, link count, and regular-file type before returning an inode, otherwise sets `u.u_error`. `afs_syscall_icreate` requires superuser, obtains root inode 2, allocates a nearby inode, initializes it as a regular file, sets Vice metadata fields, returns the inode number in `u.u_r.r_val1`, and releases it. `afs_syscall_iopen` validates privilege and inode, allocates a file descriptor, wires vnode-backed file state, increments write count for writable regular files, and calls `putf` for multithreaded processes. `afs_syscall_iincdec` validates Vice magic and volume parameter, adjusts link count, and clears magic when count reaches zero.

State/persistence: persists Vice metadata in repurposed HP-UX inode fields and mutates inode link counts/mode/flags. File descriptor state is installed in the current process.

Dependencies/integration: depends on HP-UX UFS internals, `u.u_error`, OpenAFS superuser checks, and inode field macros from `osi_inode.h`.

Risks/test signals: legacy K&R functions with missing explicit returns are fragile. Risks include inode field aliasing, wrong write-count accounting, link-count underflow, and root-only syscall exposure. Test salvager/fileserver inode create/open/inc/dec paths, multi-threaded descriptor use, invalid inode/dev handling, and non-Vice inode rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/HPUX/osi_inode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/HPUX/osi_inode.h -->
## sources/distributed-fs/openafs/src/afs/HPUX/osi_inode.h

Purpose: defines HP-UX UFS inode metadata layout used by OpenAFS Vice inode operations.

Important APIs/types/functions: defines `BAD_IGET`, `VICEMAGIC`, `DI_VICEP3`, `I_VICE3`, UID extraction helpers, aliases for `i_vicemagic`, `i_vicep1..4`, `di_vicemagic`, `di_vicep1..4`, magic tests/clear macros, and the `igetinode` prototype.

Control flow: no runtime control flow; macro expansion maps OpenAFS fields onto HP-UX inode/dinode members.

State/persistence: persists AFS volume/vnode/uniquifier/data fields in inode spare, generation, flag, and UID msb/lsb fields. The comment explains `VICEMAGIC` is placed in `ic_flags` to interact with HP-UX large-UID handling.

Dependencies/integration: consumed by HP-UX inode and file cache code plus server/salvager paths that interpret Vice inodes.

Risks/test signals: field aliasing is architecture/compiler sensitive and can conflict with native UFS semantics. Test by creating Vice inodes, running salvager/list-inode tooling, verifying metadata survives reboot/fsck, and checking large UID behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/HPUX/osi_inode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/HPUX/osi_machdep.h -->
## sources/distributed-fs/openafs/src/afs/HPUX/osi_machdep.h

Purpose: HP-UX machine-dependent OSI header that maps portable OpenAFS OS abstractions to HP-UX kernel APIs for time, credentials, process identity, vnode I/O, lookup, global locking, sleep/wakeup, SPL, and VM support.

Important APIs/types/functions: defines `afs_ucred_t`, `afs_proc_t`, `osi_Time`, `gop_rdwr`, `gop_lookupname`, `osi_curcred`, `getpid`, `getppid`, `AFS_GLOCK`, `AFS_GUNLOCK`, `ISAFS_GLOCK`, `NETPRI`, `USERPRI`, `afs_osi_Sleep` or function prototypes for HP-UX 11, `osi_NullHandle`, `osi_procname`, and inline `osi_GetTime`.

Control flow: macro control flow differs by HP-UX version. Older HP-UX uses alpha semaphores and direct `sleep`; HP-UX 11 beta semaphore paths call functions in `osi_sleep.c`. MP builds store semaphore save areas in the hash table declared here and implemented in `osi_vnodeops.c`.

State/persistence: declares the global AFS semaphore and per-thread semaphore-save hash hooks. No durable state, but lock ownership controls all AFS kernel state mutation.

Dependencies/integration: includes HP-UX kernel semaphore/process/vfs VM headers and is included indirectly by `afs_osi.h`.

Risks/test signals: incorrect global-lock macros can deadlock or restore wrong semaphore state. Time and credential macros assume `u.u_procp`/`u.u_kthreadp` layout. Test nested AFS calls, sleeps while holding global lock, MP thread concurrency, and HP-UX 10/11 build variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/HPUX/osi_machdep.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/HPUX/osi_misc.c -->
## sources/distributed-fs/openafs/src/afs/HPUX/osi_misc.c

Purpose: provides HP-UX-specific miscellaneous support, currently just a safe superuser check wrapper.

Important APIs/types/functions: `afs_suser(afs_ucred_t *credp)` saves `u.u_error`, calls HP-UX `suser()`, restores `u.u_error`, and returns the privilege result.

Control flow: straight-line error preservation around `suser`.

State/persistence: no persistent state. It deliberately avoids changing process errno while testing privilege.

Dependencies/integration: used by privileged inode/syscall paths that require superuser checks but must not clobber caller-visible error state.

Risks/test signals: semantics depend on HP-UX `suser()` return convention. Test privileged and unprivileged calls to inode syscalls and verify failed privilege checks do not overwrite unrelated `u.u_error`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/HPUX/osi_misc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/HPUX/osi_prototypes.h -->
## sources/distributed-fs/openafs/src/afs/HPUX/osi_prototypes.h

Purpose: HP-UX OSI prototype placeholder.

Important APIs/types/functions: only include guards are defined; no prototypes are exported locally.

Control flow: none.

State/persistence: none.

Dependencies/integration: included by platform build logic expecting an `osi_prototypes.h` file for each port.

Risks/test signals: risk is absence of prototypes hiding implicit-int or K&R declarations in legacy HP-UX code. Build warnings are the only meaningful signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/HPUX/osi_prototypes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/HPUX/osi_sleep.c -->
## sources/distributed-fs/openafs/src/afs/HPUX/osi_sleep.c

Purpose: implements HP-UX sleep, timed wait, wakeup, and wait-handle cancellation abstractions for OpenAFS.

Important APIs/types/functions: `afs_osi_CallProc`, `afs_osi_CancelProc`, `AfsWaitHack`, `afs_osi_InitWaitHandle`, `afs_osi_CancelWait`, `afs_osi_Wait`, `afs_osi_SleepSig`, `afs_osi_TimedSleep`, `afs_osi_Sleep`, and `afs_osi_Wakeup`. HP-UX 11 paths use `get_sleep_lock`; older paths use a static `waitV`.

Control flow: waits set a wait-handle process marker, schedule `AfsWaitHack` with `timeout`, sleep on either the handle/local event or `waitV`, cancel the timeout, and loop until timeout or cancellation. Cancellation clears the handle marker and wakes the event. HP-UX 11 functions explicitly drop/reacquire `AFS_GLOCK` around `sleep` because beta semaphores do not auto-release.

State/persistence: transient wait-handle state is stored in `achandle->proc`. No durable state. Timeout IDs are returned from HP-UX timeout APIs but not stored in the handle.

Dependencies/integration: depends on HP-UX `timeout`, `untimeout`, `sleep`, `wakeup`, sleep locks, and global lock semantics from `osi_machdep.h`.

Risks/test signals: risks include missed wakeups, cancellation races, timeout precision, and sleeping with incorrect global-lock state. Test timed sleeps, signal/cancel waits, wakeups before and during sleep, HP-UX 10 vs 11 builds, and shutdown paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/HPUX/osi_sleep.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/HPUX/osi_vcache.c -->
## sources/distributed-fs/openafs/src/afs/HPUX/osi_vcache.c

Purpose: implements HP-UX vcache/vnode allocation and attachment hooks for the portable AFS vcache layer.

Important APIs/types/functions: `osi_TryEvictVCache`, `osi_NewVnode`, `osi_PrePopulateVCache`, `osi_AttachVnode`, `osi_PostPopulateVCache`, and `osi_vnhold`.

Control flow: eviction checks that the vcache has no references, no opens, and is not pending unlinked deletion before calling `afs_FlushVCache`. New vnodes are allocated as `struct vcache`. Pre-population zeroes the vcache and initializes `flushDV` to `AFS_MAXDV`. Post-population assigns `afs_ops`, `afs_globalVFS`, and regular-file type. Hold increments the vnode reference.

State/persistence: initializes in-memory vcache/vnode state only. Persistent file state is managed elsewhere.

Dependencies/integration: depends on HP-UX vnode fields, global VFS from `osi_vfsops.c`, OpenAFS vcache state flags, and `afs_ops` from `osi_vnodeops.c`.

Risks/test signals: simplistic `osi_AttachVnode` and default `VREG` type rely on later core AFS setup. Test vcache allocation/reuse, vnode reference counts, root vnode setup, and eviction under open/unlinked/reference states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/HPUX/osi_vcache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/HPUX/osi_vfs.h -->
## sources/distributed-fs/openafs/src/afs/HPUX/osi_vfs.h

Purpose: provides small HP-UX VFS compatibility definitions for OpenAFS.

Important APIs/types/functions: defines `LOCK_SH`, `LOCK_EX`, `LOCK_NB`, `LOCK_UN`, maps `d_fileno` to `d_ino`, and defines `splclock()` as `spl7()`.

Control flow: none.

State/persistence: none.

Dependencies/integration: used by HP-UX vnode and lock code that expects BSD-like flock constants and dirent field names.

Risks/test signals: constants must match HP-UX lockf/flock expectations. Test advisory lock translation and directory entry consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/HPUX/osi_vfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/HPUX/osi_vfsops.c -->
## sources/distributed-fs/openafs/src/afs/HPUX/osi_vfsops.c

Purpose: implements HP-UX VFS operations and module/syscall registration for mounting AFS.

Important APIs/types/functions: `afs_mount`, `afs_unmount`, `afs_root`, `afs_statfs`, `afs_sync`, `afs_vget`, `afs_getmount`, `Afs_vfsops`, `osi_InitGlock`, `afs_load`, and `afsc_link`. It defines `afs_globalVFS`, `afs_globalVp`, `afs_mountpath`, `afs_global_sema`, and `afs_vfs_slot`.

Control flow: mount rejects remounts, initializes VFS block size/fsid/name, stores mount path, and initializes translator support. Unmount clears global VFS and calls warm shutdown. Root reuses a cached statted root vcache or fetches `afs_rootFid`, holds and marks it `VROOT`, and returns the vnode. Statfs returns fake free space. Vget initializes an AFS request and delegates to `afs_osi_vget`. `afsc_link` initializes OSI, registers VFS type, installs `Afs_syscall`, and replaces system `setgroups` with `Afs_xsetgroups`.

State/persistence: keeps global mount/root vnode pointers and mount path. Global lock semaphore state persists while the module is loaded.

Dependencies/integration: depends on HP-UX VFS registration, dynamic kernel module structures for 11.23, syscall table patching, OpenAFS root fid/cache init, and optional non-filesystem translator.

Risks/test signals: risks include global single-mount assumptions, syscall replacement safety, stale root vcache, unmount with references, and glock initialization race. Test mount/unmount/remount, root lookup, statfs, NFS translator setup, syscall dispatch, and setgroups interception.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/HPUX/osi_vfsops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/HPUX/osi_vm.c -->
## sources/distributed-fs/openafs/src/afs/HPUX/osi_vm.c

Purpose: provides HP-UX VM/cache invalidation hooks for the generic AFS vcache layer.

Important APIs/types/functions: `osi_VM_FlushVCache`, `osi_VM_StoreAllSegments`, `osi_VM_TryToSmush`, `osi_VM_FlushPages`, and `osi_VM_Truncate`.

Control flow: flush-vcache returns `EBUSY` if reference count or opens indicate active use. Store/flush/truncate page hooks are mostly no-ops. `osi_VM_TryToSmush` purges delayed write buffers and invalidates free buffers unless the vnode is marked text.

State/persistence: affects HP-UX buffer cache state for AFS vnodes through `mpurge` and `binvalfree`; does not directly persist data.

Dependencies/integration: called by shared AFS cache invalidation, callback revocation, truncation, and vcache recycling paths. Depends on HP-UX vnode flags and buffer cache APIs.

Risks/test signals: no-op flush/truncate hooks may leave stale mapped pages on workloads that rely on VM invalidation. Test callback revocation, `fs flush`, truncation, mapped-file reads after server-side changes, and vcache recycling under references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/HPUX/osi_vm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/HPUX/osi_vnodeops.c -->
## sources/distributed-fs/openafs/src/afs/HPUX/osi_vnodeops.c

Purpose: implements the HP-UX vnode operation table, file operations, VM pagein/pageout glue, ioctl/readdir conversion, and per-thread semaphore-save hash needed by the AFS global lock.

Important APIs/types/functions: `Afs_vnodeops`, `afs_fileops`, `afs_lockf`, `afs_bread`, `afs_brelse`, `afs_bmap`, `afs_inactive`, many `mp_afs_*` wrappers, `afs_pagein`, `afs_pageout`, `afs_mapdbd`, `afs_vm_checkpage`, `afs_hp_strategy`, `afs_pathconf`, `afs_readdir`, `afs_readdir3`, and hash functions `afsHash`, `afsHashInsertFind`, `afsHashFind`, `afsHashRelease`. Vnode wrappers call core AFS operations under `AFS_GLOCK`.

Control flow: standard vnode operations are thin MP-safe wrappers around `afs_open`, `afs_close`, `afs_rdwr`, lookup/create/remove/link/rename/mkdir/rmdir/readdir/symlink/readlink/fsync/lock/fid. Buffer read uses fake buffers for RFS/NFS translator behavior. `afs_pagein` initializes HP-UX VM fault info, verifies EOF, reserves memory, expands I/O ranges, flushes overlapping blocks, issues `syncpageio`, handles holes for writable mappings, marks DBDs, and returns page counts or SIGBUS. `afs_pageout` scans dirty page ranges, builds buffers, protects pages, flushes stale buffers, writes with `asyncpageio`, handles vhand credential substitution, and updates VM stats. `afs_hp_strategy` maps buffers to kernel space and calls `afs_rdwr`.

State/persistence: vnode ops mutate AFS cache/server-visible state via generic AFS calls. VM operations persist dirty mapped pages back to AFS through strategy/pageout paths. The semaphore hash stores per-thread saved `sv_sema_t` state for global-lock release/reacquire across call chains.

Dependencies/integration: deeply coupled to HP-UX VM internals (`vfspage_t`, DBD/VFD, regions, pregions), buffer cache, vnodeops layout, syscall/fileops, OpenAFS global lock, and version-specific HP-UX 11 headers.

Risks/test signals: very high risk from VM empire locking, pageout credentials, fake buffer lifetime, directory entry conversion sizing, semaphore hash leaks/races, and version-dependent vnodeops slots. Test mmap read/write/page faults, pageout under memory pressure, ENOSPC write accounting, directory listings in 32/64-bit callers, lockf translation, NFS translator paths, and multi-threaded global-lock nesting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/HPUX/osi_vnodeops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/IRIX/osi_crypto.c -->
## sources/distributed-fs/openafs/src/afs/IRIX/osi_crypto.c

Purpose: supplies the IRIX implementation of kernel random-byte generation, but the implementation is intentionally unsupported.

Important APIs/types/functions: `osi_readRandom(void *data, afs_size_t len)` calls `osi_Panic` with a message that the platform lacks a kernel cryptographic PRNG, then returns 0 only for compiler flow.

Control flow: unconditional panic.

State/persistence: none.

Dependencies/integration: used by OpenAFS crypto/rand consumers if they request kernel randomness on IRIX.

Risks/test signals: any feature requiring kernel random bytes will panic the kernel on IRIX. Test signal is negative: callers must avoid this path or provide another platform implementation before enabling crypto features needing randomness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/IRIX/osi_crypto.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/IRIX/osi_file.c -->
## sources/distributed-fs/openafs/src/afs/IRIX/osi_file.c

Purpose: implements IRIX cache-file operations for AFS UFS-type disk cache, backed by XFS vnode lookup and generic vnode I/O.

Important APIs/types/functions: `afs_XFSIGetVnode`, `osi_UFSOpen`, `afs_osi_Stat`, `osi_UFSClose`, `osi_UFSTruncate`, `afs_osi_Read`, `afs_osi_Write`, `afs_osi_MapStrategy`, and `shutdown_osifile`. Uses `xfs_igetinode`, `XFS_ITOV`, `AFS_VOP_GETATTR`, `AFS_VOP_SETATTR`, `gop_rdwr`, `VnodeToSize`, static `afs_osi_cred`, `cacheDev`, and `afs_cacheVfsp`.

Control flow: open verifies UFS cache type, initializes a held static credential, allocates `osi_file`, drops `AFS_GLOCK`, resolves the cache inode to an XFS vnode, restores the lock, and records vnode size/offset. Stat/truncate call IRIX VOP wrappers with attribute masks. Read/write build kernel-space vnode I/O through `gop_rdwr`, update offsets on success, trace read errors, return negative errors for failures, and call optional completion callbacks after writes.

State/persistence: persistent cache data lives in XFS files addressed by inode number. Truncation shrinks files via `AFS_VOP_SETATTR`. File offsets and optional callbacks are per-`osi_file` in-memory state.

Dependencies/integration: depends on IRIX XFS inode helpers from `osi_inode.c`, behavior-safe VOP macros from `osi_vfs.h`, and OpenAFS global lock transitions.

Risks/test signals: risks include panics on missing cache inodes, mismatch between UFS cache naming and XFS-only implementation, negative error conversion, and static credential lifetime. Test cache open/stat/read/write/truncate/close, missing inode handling, XFS cache devices, and shutdown reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/IRIX/osi_file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/IRIX/osi_gcpags.c -->
## sources/distributed-fs/openafs/src/afs/IRIX/osi_gcpags.c

Purpose: intended to implement IRIX process traversal for PAG garbage collection, but it is incomplete.

Important APIs/types/functions: `SGI_ProcScanFunc`, `afs_osi_TraverseProcTable`, and `afs_osi_proc2cred`.

Control flow: when `AFS_GCPAGS` is enabled, traversal calls `procscan(SGI_ProcScanFunc, afs_GCPAGs_perproc_func)`. The scan callback currently returns 0 without invoking its argument, and `afs_osi_proc2cred` always returns NULL.

State/persistence: no state is maintained and no live credentials are exposed to PAG GC.

Dependencies/integration: tied to IRIX `procscan` and the shared `afs_GCPAGs_perproc_func` contract, but the TODO indicates the integration is not functional.

Risks/test signals: PAG garbage collection on IRIX may never see process credentials, causing token/PAG accounting leaks or premature cleanup depending on caller behavior. Test with `AFS_GCPAGS`, PAG creation, process exit, token cleanup, and instrumentation proving the generic per-process callback is invoked.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/IRIX/osi_gcpags.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/IRIX/osi_groups.c -->
## sources/distributed-fs/openafs/src/afs/IRIX/osi_groups.c

Purpose: implements IRIX PAG handling in credentials, including coexistence with SGI DFS PAG conventions and `setgroups` interception.

Important APIs/types/functions: `fixup_pags`, `osi_DFSGetPagFromCred`, `Afs_xsetgroups`, `setpag`, `afs_getgroups`, and `afs_setgroups`. Uses `crdup`, `crfree`, `estgroups`, `OSI_GET_CURRENT_CRED`, `OSI_GET_CURRENT_PROCP`, `PagInCred`, `afs_get_pag_from_groups`, and `afs_get_groups_from_pag`.

Control flow: `Afs_xsetgroups` records old AFS and DFS PAGs, calls native `setgroups`, then uses `fixup_pags` to rebuild credentials if the new group list dropped old PAGs. `fixup_pags` copies user groups, detects new AFS PAG in the first two groups and DFS PAG in the last group, prepends/appends old PAGs if needed, and returns a replacement credential only when changed. `setpag` mirrors other AFS ports by inserting encoded AFS PAG groups at the front. `afs_setgroups` duplicates or edits credentials and installs them with `estgroups`.

State/persistence: AFS PAGs persist in the first two groups; DFS PAGs may persist in the last group. Credential group count `cr_ngroups` is authoritative on IRIX.

Dependencies/integration: integrates with IRIX credential management, SGI DFS compatibility, OpenAFS PAG generation, and syscall replacement in `osi_vfsops.c`.

Risks/test signals: risks include group overflow against `ngroups_max`, preserving both AFS and DFS PAGs, user copyin failures, and credential replacement races. Test AFS and DFS PAG coexistence, `setgroups` with/without PAG slots, max groups, token inheritance, and failed copyin paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/IRIX/osi_groups.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/IRIX/osi_idbg.c -->
## sources/distributed-fs/openafs/src/afs/IRIX/osi_idbg.c

Purpose: implements IRIX IDBG debugger commands for inspecting AFS vcache, VFS list, and user/token state.

Important APIs/types/functions: `printflags`, `idbg_prafsnode`, `idbg_afsvfslist`, `idbg_pruser`, and `idbg_afsuser`. It uses `qprintf`, `VLRU`, `afs_calc_inum`, `VN_GET_PGCNT`, `afs_users`, `afs_FindToken`, and RXKAD token structures.

Control flow: debug entry points acquire `AFS_GLOCK`, print selected structures, and release the lock. `idbg_afsvfslist` walks the vcache LRU from tail to head and prints vnode type/ref/page/map/inode data. `idbg_afsuser` either dumps all hash buckets when passed `-1` or one specific `unixuser`.

State/persistence: read-only diagnostics over live kernel AFS state. No mutation except lock acquisition.

Dependencies/integration: registered by `Afs_init` in `osi_vfsops.c` via `idbg_addfunc`. Depends on IRIX IDBG and OpenAFS internal structure layout.

Risks/test signals: debug code can crash if handed stale pointers or if structure layouts drift. Token printing must avoid assuming a KAD token exists; this file checks for NULL. Test IDBG commands on active/inactive vcaches and users, with and without tokens.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/IRIX/osi_idbg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/IRIX/osi_inode.c -->
## sources/distributed-fs/openafs/src/afs/IRIX/osi_inode.c

Purpose: implements IRIX inode syscalls for OpenAFS server/salvager operation, focusing on XFS-backed Vice inode creation, opening, link-count adjustment, and listing metadata.

Important APIs/types/functions: `afsidestroy`, `xfs_getinode`, `xfs_igetinode`, `xfs_icreatename64`, `afs_syscall_icreatename64`, `afs_syscall_iopen`, `iopen`, `iopen64`, `xfs_iincdec64`, `iincdec64`, `afs_syscall_iinc64`, `afs_syscall_idec64`, and `afs_syscall_ilistinode64`. Legacy EFS `getinode`, `igetinode`, `icreate`, and `afs_syscall_icreate` return `ENOSYS`; `iinc`/`idec` return `ENOTSUP`.

Control flow: XFS lookup resolves a VFS by device, calls `xfs_iget`, unlocks the inode, validates vnode attributes, and returns an XFS inode/vnode. `xfs_icreatename64` copies a base path, builds/locates a per-volume AFS inode directory, creates it with root attributes if needed, creates a hidden file with a base64 name/tag, stores AFS parameters in root XFS attributes, sets mode/uid/gid markers, returns the inode number, and cleans up partial files/directories on failure. Link-count changes verify magic and volume id via uid/gid/mode, update encoded link bits, or remove the hidden file and possibly its empty volume directory when count reaches zero. Listing reads XFS attributes and vnode stats into `i_list_inode_t`.

State/persistence: persists Vice inode metadata in XFS extended attributes and namespace files, with uid clipped to RW volume id and gid set to `XFS_VICEMAGIC`; link count is encoded in mode bits.

Dependencies/integration: depends on IRIX XFS internals, `afs/xfsattrs.h`, VOP attribute wrappers, volume create mutex, OpenAFS syscall registration, base64 naming, and root-only privilege checks.

Risks/test signals: high risk around cleanup after partial creates, directory create/remove races, 64-bit inode composition, XFS attribute version mismatches, link-count overflow above 7, and legacy unsupported syscall callers. Test fileserver inode create/open/inc/dec/list, volume special directories, concurrent vos create/zap, invalid attribute versions, and 32/64-bit syscall entry points.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/IRIX/osi_inode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/IRIX/osi_inode.h -->
## sources/distributed-fs/openafs/src/afs/IRIX/osi_inode.h

Purpose: defines IRIX inode metadata constants and layout notes for AFS server/salvager support.

Important APIs/types/functions: defines `BAD_IGET`, `XFS_VICEMAGIC`, `DI_VICEP3`, `I_VICE3`, masks for SGI inode fields, `struct afsparms`, and `dmag` for disk inode extent magic access.

Control flow: none; this is a macro/type header.

State/persistence: documents two metadata schemes: XFS uses `XFS_VICEMAGIC`; older EFS-style inodes use unused `ex_magic` fields plus `di_version` to encode volume, vnode, uniquifier, data version, and special inode metadata.

Dependencies/integration: used by `osi_inode.c` and any IRIX salvager/fileserver code interpreting Vice inode parameters.

Risks/test signals: on-disk field packing is filesystem-version sensitive. Test list/create/increment/decrement tooling across XFS and any legacy EFS expectations, and verify masks do not truncate required volume/vnode data unexpectedly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/IRIX/osi_inode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/IRIX/osi_machdep.h -->
## sources/distributed-fs/openafs/src/afs/IRIX/osi_machdep.h

Purpose: IRIX machine-dependent OSI header mapping portable OpenAFS concepts to IRIX kernel locks, credentials, VFS/vnode behavior descriptors, process/thread identity, time, sleep primitives, and vnode operation argument conversion.

Important APIs/types/functions: defines `afs_ucred_t`, `afs_proc_t`, `osi_Time`, lookup and rdwr macros, `AFS_GLOCK`, `AFS_GUNLOCK`, `ISAFS_GLOCK`, `AFS_MUTEX_ENTER`, `cv_wait`, `cv_timedwait`, `osi_InitGlock`, `afs_suser`, `OSI_GET_CURRENT_*` accessors, `OSI_GET_LOCKID`, and `OSI_VN/VC/VFS_*` behavior descriptor conversion macros.

Control flow: MP builds use a real `afs_global_lock` mutex with assertions against recursive ownership; non-MP builds compile global locking away. CV macros release and reacquire the global lock through IRIX sv primitives. VOP wrappers use behavior descriptors instead of direct vnode pointers.

State/persistence: declares/uses `afs_global_lock` and thread identity values for rwlock ownership debugging. No durable state.

Dependencies/integration: depends on IRIX sema, pda, flock, process, uthread, behavior descriptor, and capability APIs. It is central to all IRIX platform files.

Risks/test signals: recursive lock assertions, mutex owner edge cases, behavior descriptor conversions, and credential macros are all kernel-version sensitive. Test MP and non-MP builds, sleep/wakeup under global lock, vnode/VFS operation dispatch, and rwlock owner tracking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/IRIX/osi_machdep.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/IRIX/osi_misc.c -->
## sources/distributed-fs/openafs/src/afs/IRIX/osi_misc.c

Purpose: miscellaneous IRIX support for OpenAFS, including semaphore-name formatting, optional vnode glue NUMA detection, and platform identifier export.

Important APIs/types/functions: `afs_mpservice`, `makesname`, optional `afs_init_kernel_config`, and global `afs_ipno`. Uses IRIX inventory APIs under `AFS_SGI_VNODE_GLUE`.

Control flow: `makesname` truncates prefix and decimal vnode number into `METER_NAMSZ` without relying on unavailable kernel `snprintf`. `afs_init_kernel_config` initializes once under `afs_init_kern_lock`, optionally probes CPU board inventory for IP27/IP35 NUMA systems, and sets `afs_is_numa_arch`.

State/persistence: stores one-time vnode glue initialization state, NUMA flag, and compile-time IP platform number. Semaphore names are transient initialization data.

Dependencies/integration: used by `osi_vcache.c` for named semaphores and by `osi_vfs.h` vnode-shape shims when SGI vnode glue is enabled.

Risks/test signals: semaphore names may not be unique due to length truncation; NUMA detection depends on inventory data and compile-time platform macros. Test vcache allocation on many vnode numbers, NUMA/non-NUMA IRIX systems, and repeated init calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/IRIX/osi_misc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/IRIX/osi_prototypes.h -->
## sources/distributed-fs/openafs/src/afs/IRIX/osi_prototypes.h

Purpose: IRIX OSI prototype placeholder.

Important APIs/types/functions: only the `_OSI_PROTOTYPES_H_` include guard is present.

Control flow: none.

State/persistence: none.

Dependencies/integration: satisfies platform include conventions.

Risks/test signals: absence of prototypes can hide legacy implicit declarations in adjacent IRIX files. Build warnings/errors are the relevant signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/IRIX/osi_prototypes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/IRIX/osi_sleep.c -->
## sources/distributed-fs/openafs/src/afs/IRIX/osi_sleep.c

Purpose: implements IRIX event-based sleep, timed sleep, wakeup, and wait-handle cancellation for OpenAFS.

Important APIs/types/functions: `afs_osi_InitWaitHandle`, `afs_osi_CancelWait`, `afs_osi_Wait`, `afs_getevent`, `afs_osi_Sleep`, `afs_osi_SleepSig`, `afs_osi_TimedSleep`, and `afs_osi_Wakeup`. It maintains `afs_evhasht` and `afs_evhashcnt` of `afs_event_t` entries.

Control flow: event addresses hash to condition-variable entries. Sleep records the current sequence and waits until wakeup increments it. Timed sleep computes a `timespec` and uses interruptible `sv_timedwait_sig` when requested, otherwise `cv_timedwait`. Wakeup gets the event, increments sequence, broadcasts if more than one reference exists, and releases it. Wait handles use static `waitV` for cancellation wakeups.

State/persistence: in-memory event table entries persist and are reused; refcounts manage active sleepers but entries are not freed. Wait handles store current thread pointer or zero when cancelled.

Dependencies/integration: depends on IRIX condition variables/state vectors and `afs_global_lock` from machdep macros.

Risks/test signals: risks include event table growth, missed wakeups if refcounts/sequence are wrong, interrupt handling, and global-lock reacquisition. Test timed waits, cancellation, multiple waiters on same event, signal-interruptible sleeps, and high churn event addresses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/IRIX/osi_sleep.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/IRIX/osi_vcache.c -->
## sources/distributed-fs/openafs/src/afs/IRIX/osi_vcache.c

Purpose: implements IRIX vcache/vnode allocation and initialization, including IRIX behavior descriptors and page-cache structures.

Important APIs/types/functions: `osi_TryEvictVCache`, `osi_NewVnode`, `osi_PrePopulateVCache`, `osi_AttachVnode`, `osi_PostPopulateVCache`, and `osi_vnhold`.

Control flow: new vcaches are allocated, zeroed, assigned a unique vnode number, initialized with a named rw semaphore, and later populated with behavior descriptors, behavior head, mapping pointers, trace state, bitlocks, file lock mutex, buffer lock, page cache, VFS/type, page counters, vnode lists, and default fields. Eviction only flushes vcaches without refs, opens, or unlinked-delete state.

State/persistence: all state is in-memory vnode/vcache infrastructure. `afsvnumbers` monotonically supplies vnode numbers; semaphores and mutexes live with the vcache.

Dependencies/integration: depends on `makesname`, `Afs_vnodeops`, `afs_globalVFS`, IRIX behavior and vnode page-cache APIs, and OpenAFS vcache state.

Risks/test signals: high-risk initialization order: missing behavior setup, lock init, or pcache reinit can crash later VOP/VM paths. Test vcache allocation/reuse, vnode hold/release, page-cache reclaim, vnode tracing builds, and eviction with mapped/dirty pages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/IRIX/osi_vcache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/IRIX/osi_vfs.h -->
## sources/distributed-fs/openafs/src/afs/IRIX/osi_vfs.h

Purpose: IRIX VFS/vnode compatibility header for OpenAFS, hiding XFS, behavior-descriptor, page-cache, vnode-layout, and directory/lock differences.

Important APIs/types/functions: defines XFS conversion macros (`XFS_VTOI`, `XFS_ITOV`), `xfs_iget` prototype, `VnodeToIno/Dev/Size` prototypes, page operation macros (`PTOSSVP`, `PFLUSHVP`, etc.), VOP wrapper macros (`AFS_VOP_*`), `AFS_VN_OPEN`, vnode dirty/mapped/page-count accessors, flock constants, `afs_fid2_t` for checkpoint restart, and compatibility aliases such as `ucred` to `cred`.

Control flow: macro wrappers optionally prevent behavior insertion around VOP calls when `AFS_SGI_VNODE_GLUE` is enabled, with NUMA-specific behavior. Vnode field accessors select between native vnode layout and `vnode1_t` shim depending on `afs_is_numa_arch`.

State/persistence: no direct state, but macros read/write vnode page-cache fields and behavior heads.

Dependencies/integration: included by most IRIX platform files, especially file, inode, VM, vcache, and vfsops implementations.

Risks/test signals: version/layout shims are fragile; wrong NUMA detection or behavior locking can corrupt vnode state. Test with and without `AFS_SGI_VNODE_GLUE`, NUMA and non-NUMA systems, XFS VOP calls, page flush/invalidate operations, and checkpoint fid vget.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/IRIX/osi_vfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/IRIX/osi_vfsops.c -->
## sources/distributed-fs/openafs/src/afs/IRIX/osi_vfsops.c

Purpose: implements IRIX AFS filesystem initialization, VFS operations, syscall hook installation, IDBG hook registration, mount/root/statfs/sync/vget behavior, and MP wrappers.

Important APIs/types/functions: `Afs_init`, `afs_mount`, `afs_unmount`, `afs_root`, `afs_statfs`, `afs_sync`, `afs_vget`, MP wrapper functions, `Afs_vfsops`, and globals `afs_globalVFS`, `afs_globalVp`, `afs_fstype`, `afs_rxlock`, `afs_vfs_bhv`.

Control flow: initialization calls `osi_Init`, records fstype, sets exported operation pointers, installs AFS syscalls (`AFS_SYSCALL`, `AFS_PIOCTL`, `AFS_SETPAG`, inode syscalls), replaces `setgroupsp`, and registers IDBG commands. Mount requires superuser and directory mountpoint, rejects remounts, initializes VFS fsid/type/dev, and inserts a behavior. Unmount flushes all vcaches from `VLRU`, handles the root vnode specially, clears globals, warms shutdown, and removes VFS behavior. Root fetches or reuses `afs_rootFid`. Sync walks active dirty vcaches, obtains nonblocking or blocking rwlocks, flushes/invalidates pages according to sync flags, and restarts if `vcachegen` changes. Vget handles checkpoint fids or delegates to `afs_osi_vget`.

State/persistence: global VFS/root vnode cache, syscall table hooks, setgroups hook, IDBG hooks, VFS behavior state, and AFS fstype are maintained while loaded.

Dependencies/integration: deeply coupled to IRIX VFS behavior APIs, syscall table layout, OpenAFS vcache list/locks, VM page flush macros, credential APIs, and optional SGI vnode glue.

Risks/test signals: risks include unsafe syscall replacement, unmount with referenced/dirty vcaches, sync races while `VLRU` mutates, root vnode reference manipulation, and checkpoint fid conversion. Test mount/unmount under active files, sync flags, dirty mmap flush, syscall dispatch, setgroups PAG preservation, IDBG registration, and CKPT restart fids.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/IRIX/osi_vfsops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/IRIX/osi_vm.c -->
## sources/distributed-fs/openafs/src/afs/IRIX/osi_vm.c

Purpose: implements IRIX VM and page-cache integration for AFS vcache recycling, callback invalidation, storeback, fsync invalidation, and truncation.

Important APIs/types/functions: `osi_VM_FlushVCache`, `osi_VM_TryToSmush`, `osi_VM_FSyncInval`, `osi_VM_StoreAllSegments`, `osi_VM_FlushPages`, and `osi_VM_Truncate`.

Control flow: flush-vcache rejects active refs, opens, locks, waiters, and vnodes in inactive transition. It tosses all pages, checks for no pages/mappings/dirty buffers, cleans file locks, reclaims/frees vnode page-cache state, removes behavior descriptors, destroys locks, and resets vnode flags. Store-all releases the vcache write lock and global lock, repeatedly flushes delayed pages with `pdflush`, calls `PFLUSHVP`, falls back to `PINVALFREE` on error, reacquires locks, and warns on failed storeback for linked files. Smush/remap paths drop locks before `remapf`/`PTOSSVP`. FlushPages remaps and tosses all pages; truncate tosses pages beyond length.

State/persistence: manipulates IRIX VM page cache, dirty-page lists, vnode file locks, behavior heads, and vcache lock ownership. Store paths persist dirty mapped data to the AFS cache/server path via page flush operations.

Dependencies/integration: depends on IRIX vnode page-cache APIs, behavior descriptors, file lock cleanup, OpenAFS vcache locks, and macros in `osi_vfs.h`.

Risks/test signals: very high-risk due to assertions around no dirty/mapped pages, lock dropping/reacquisition, and vnode reclaim ordering. Test vcache recycle after mmap, callback revocation, fsync with invalidation, truncation, dirty mmap last-close storeback, file locks, and error injection in page flush.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/IRIX/osi_vm.c -->
