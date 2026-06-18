# Research: subset-b-007753 OpenAFS BSD/Solaris OSI and VFS/Vnode Glue

This grouped report covers the requested OpenAFS platform adaptation files. Each section is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/NBSD/osi_vnodeops.c -->
# sources/distributed-fs/openafs/src/afs/NBSD/osi_vnodeops.c

## Purpose
NetBSD vnode operation glue for the OpenAFS cache manager. It registers the `afs_vnodeop_entries` table, allocates NetBSD vnodes for `struct vcache`, bridges NetBSD VOP calls into common AFS routines, and manages UVM/genfs interactions.

## Important APIs, Types, and Functions
Exports `afs_vnodeop_p`, `afs_vnodeop_opv_desc`, and vnode handlers `afs_nbsd_lookup`, `create`, `open`, `close`, `access`, `getattr`, `setattr`, `read`, `write`, `ioctl`, `fsync`, `remove`, `link`, `rename`, `mkdir`, `rmdir`, `symlink`, `readdir`, `readlink`, `inactive`, `reclaim`, `lock`, `unlock`, `bmap`, `strategy`, `pathconf`, and `advlock`. `afs_nbsd_getnewvnode` attaches a `struct nbvdata` to `v_data`, initializes genfs state, and sets vnode size to zero.

## Control Flow
Most VOP handlers translate NetBSD argument structs into calls to core AFS operations under `AFS_GLOCK`. Lookup copies `componentname`, optionally checks the NetBSD name cache, calls `afs_lookup`, and returns locked vnodes while handling dot-dot and create/rename `EJUSTRETURN`. Mutating directory operations copy names, call the corresponding AFS operation, then release or unlock parent/child vnodes according to NetBSD VFS rules. Read/write call `afs_read`/`afs_write`; write updates the UVM vnode size if the file grew. Reclaim flushes the vcache, destroys genfs state, frees `v_data`, and detaches `avc->v`.

## State and Persistence
Persistent state is remote AFS file state and local cache state held in vcaches/dcaches. Local kernel state includes vnode refs, `v_data`, UVM object size, genfs node state, name cache entries, and vcache flags such as `CUnlinked` and `CVInit`. No disk format is owned here.

## Dependencies and Integration Points
Depends on NetBSD VFS, UVM, genfs, `componentname`, `getnewvnode`, lock APIs, and OpenAFS core routines. Integrates with `afs_globalVFS`, `afs_xvcache`, `afs_ustrategy`, `HandleIoctl`, and AFS lockctl. Conditional branches cover NetBSD 5/6 lock and namei API changes.

## Risks
Highest-risk areas are vnode lock ordering during lookup/rename, reference release on error paths, UVM page invalidation via `VNP_UNCACHE`, stale `v_data` during reclaim, and the pathconf function returning `0` even after setting `code = EINVAL`. Kernel API drift across NetBSD releases is also significant.

## Test Signals
Exercise mount/root lookup, create/remove/rename including cross-mount failures, symlink/readlink, readdir with cookies, mmap/read/write file growth, vnode reclaim under cache pressure, advisory locks, fsync, and unlinked-open file behavior. Kernel diagnostics should not report lock assertion or vnode refcount failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/NBSD/osi_vnodeops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/OBSD/osi_crypto.c -->
# sources/distributed-fs/openafs/src/afs/OBSD/osi_crypto.c

## Purpose
OpenBSD random-byte provider for OpenAFS kernel code.

## Important APIs, Types, and Functions
Defines `osi_readRandom(void *data, afs_size_t len)`, which calls `arc4random_buf(data, len)` and returns `0`.

## Control Flow
There is no branching: callers provide a destination buffer and length, OpenBSD kernel random fills the buffer, and success is reported unconditionally.

## State and Persistence
No persistent state is kept here. Entropy state belongs to OpenBSD random facilities.

## Dependencies and Integration Points
Includes `<dev/rndvar.h>` and OpenAFS `afsconfig.h`/`param.h`. Integrates with any OpenAFS code that needs platform-random bytes, such as crypto/session material generation.

## Risks
The function assumes `arc4random_buf` cannot fail and does not validate `data` or `len`. It also provides no accounting or blocking behavior control.

## Test Signals
Build on supported OpenBSD kernels and call through OpenAFS random consumers. A smoke test should verify non-crash behavior for normal nonzero lengths and that symbols resolve in kernel builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/OBSD/osi_crypto.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/OBSD/osi_file.c -->
# sources/distributed-fs/openafs/src/afs/OBSD/osi_file.c

## Purpose
OpenBSD cache-file access layer for disk-backed OpenAFS cache entries stored as UFS files.

## Important APIs, Types, and Functions
Defines `osi_UFSOpen`, `afs_osi_Stat`, `osi_UFSClose`, `osi_UFSTruncate`, `osi_DisableAtimes`, `afs_osi_Read`, `afs_osi_Write`, `afs_osi_MapStrategy`, and `shutdown_osifile`. Uses `struct osi_file`, `struct osi_stat`, `afs_osi_credp`, `cacheDev`, and `afs_cacheVfsp`.

## Control Flow
`osi_UFSOpen` validates UFS cache type, allocates `osi_file`, drops `AFS_GLOCK`, resolves an inode with `VFS_VGET`, unlocks the vnode, records size and offset, and returns the wrapper. Stat/read/write/truncate drop the global lock before VOP or `vn_rdwr` calls, then reacquire it and update cached size/offset. Close releases the vnode and frees the wrapper.

## State and Persistence
Persistent bytes live in the cache file vnode. In-memory state is `osi_file` offset, size, callback proc, and global credential initialization flag. Read/write mutate the backing cache file and update wrapper position.

## Dependencies and Integration Points
Depends on OpenBSD VFS/VOP/vn_rdwr, UFS inode layout variants, `afs_osi_credp`, OpenAFS stats and tracing, and cache type selection via `cacheDiskType`.

## Risks
Kernel locking is delicate because vnode I/O occurs with `AFS_GLOCK` dropped. `osi_UFSOpen` panics on lookup failures, so cache corruption can take down the kernel module. Atime disabling is a stub, so cache reads may update access times. Error return convention converts positive errno to negative byte counts for read/write callers.

## Test Signals
Open, stat, read, write, truncate, and close cache files; validate offsets and size tracking; simulate missing cache inode; verify shutdown clears credential initialization only on cold shutdown; run with lock diagnostics to catch GLOCK/VOP misuse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/OBSD/osi_file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/OBSD/osi_gcpags.c -->
# sources/distributed-fs/openafs/src/afs/OBSD/osi_gcpags.c

## Purpose
OpenBSD support for garbage-collecting PAGs by mapping processes to credentials when `AFS_GCPAGS` is enabled.

## Important APIs, Types, and Functions
Defines `afs_osi_proc2cred(afs_proc_t *pr)` under `#if AFS_GCPAGS`. It returns `pr->p_cred` or `NULL`.

## Control Flow
The function guards null process pointers and otherwise returns the process credential pointer directly. There is no process traversal in this file.

## State and Persistence
No state is owned here. It exposes live OpenBSD process credential state to common PAG GC code.

## Dependencies and Integration Points
Depends on OpenBSD `struct proc` layout as aliased by `afs_proc_t`, and OpenAFS PAG GC code that calls `afs_osi_proc2cred`.

## Risks
Returned credentials are borrowed live kernel pointers with no explicit refcounting here. Process or credential lifetime assumptions must be supplied by the traversal caller.

## Test Signals
Build with and without `AFS_GCPAGS`. PAG GC tests should confirm null process handling and correct credential visibility for live processes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/OBSD/osi_gcpags.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/OBSD/osi_groups.c -->
# sources/distributed-fs/openafs/src/afs/OBSD/osi_groups.c

## Purpose
OpenBSD PAG preservation and creation logic around `setgroups`, implemented by storing PAG identifiers in supplemental groups.

## Important APIs, Types, and Functions
Exports `Afs_xsetgroups` and `setpag`. Internal helpers are `afs_getgroups` and `afs_setgroups`. Uses `afs_genpag`, `afs_IsPagId`, `afs_get_pag_from_groups`, `afs_get_groups_from_pag`, `PagInCred`, and `AddPag`.

## Control Flow
`Afs_xsetgroups` initializes a request under GLOCK, calls the real `setgroups`, then restores the caller's previous PAG if the new credentials do not already contain one. `setpag` generates a PAG if requested, copies the current group list, ensures there is space for two PAG gids at positions 1 and 2, writes the encoded PAG gids, and installs the modified groups via `afs_setgroups`.

## State and Persistence
State is stored in process credentials, either by copying credentials when `change_parent` is false or modifying the supplied credential pointer. No disk persistence exists.

## Dependencies and Integration Points
Depends on OpenBSD `struct ucred`, `struct proc`, `crcopy`, syscall argument layout, and OpenAFS PAG helpers. Hooked from OpenBSD VFS init by replacing `SYS_setgroups`.

## Risks
Group-list capacity is limited by `NGROUPS`; adding a PAG can fail with `E2BIG`. The two-gid PAG encoding assumes specific group ordering. Credential copying and `p_rcred` aliases are kernel-version sensitive.

## Test Signals
Verify `setpag` for empty and full group lists, preservation of existing PAGs across `setgroups`, successful credential copy when not changing parent, and behavior when `ngroups + 2 > NGROUPS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/OBSD/osi_groups.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/OBSD/osi_inode.h -->
# sources/distributed-fs/openafs/src/afs/OBSD/osi_inode.h

## Purpose
Placeholder OpenBSD inode interface header.

## Important APIs, Types, and Functions
Defines only include guards and no macros, declarations, or types.

## Control Flow
None.

## State and Persistence
None.

## Dependencies and Integration Points
The empty header lets shared OpenAFS code include a platform `osi_inode.h` without conditional include logic, even though OpenBSD does not implement the inode syscall helpers here.

## Risks
Callers expecting inode helper declarations from this header will not get compile-time prototypes. Its emptiness is intentional only if OpenBSD inode syscalls remain unsupported.

## Test Signals
Compile OpenBSD kernel module paths that include `afs/osi_inode.h`; confirm unsupported inode calls are resolved to stubs elsewhere.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/OBSD/osi_inode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/OBSD/osi_machdep.h -->
# sources/distributed-fs/openafs/src/afs/OBSD/osi_machdep.h

## Purpose
OpenBSD OSI machine-dependent compatibility header that maps OpenAFS portable names to OpenBSD kernel types, locks, VFS/vnode fields, allocation, credentials, time, and lookup helpers.

## Important APIs, Types, and Functions
Defines `afs_proc_t`, `afs_ucred_t`, vnode/uio/VFS field macros, `AFS_KALLOC`, `AFS_KFREE`, `BSD_KMALLOC`, `BSD_KFREE`, `AFS_GLOCK`, `AFS_GUNLOCK`, `ISAFS_GLOCK`, `osi_InitGlock`, `NETPRI`, `USERPRI`, `IsAfsVnode`, `vType`, `vSetVfsp`, `vSetType`, `osi_GetTime`, and prototypes for `afs_obsd_lookupname`, `afs_obsd_getnewvnode`, and `afs_vget`.

## Control Flow
This header is compile-time control flow: OpenBSD release macros select old or new allocation APIs, lock-manager signatures, global-lock implementation, and vnode operation table shape.

## State and Persistence
Declares external global lock state (`afs_global_lock`, sometimes `afs_global_owner`) and references live process and credential state through macros. No persistent data is stored.

## Dependencies and Integration Points
Tightly integrated with OpenBSD kernel headers and with common OpenAFS code included via `afs_osi.h`. It is the contract that lets generic AFS code compile on OpenBSD.

## Risks
Macro indirection can hide side effects, particularly `getpid()` returning `curproc` and `afs_suser(x)` ignoring its argument. Kernel-version drift in lock and VOP APIs can silently break builds. The global owner tracking path asserts ownership manually.

## Test Signals
Compile across supported OpenBSD releases, enable lock diagnostics, exercise memory allocation while GLOCK is held, and validate VFS/vnode macros through mount/root/read/write flows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/OBSD/osi_machdep.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/OBSD/osi_misc.c -->
# sources/distributed-fs/openafs/src/afs/OBSD/osi_misc.c

## Purpose
Miscellaneous OpenBSD OSI helpers for superuser checks, kernel allocation, and unsupported inode syscalls.

## Important APIs, Types, and Functions
Defines `afs_osi_suser`, `osi_obsd_Alloc`, `osi_obsd_Free`, and stubs `afs_syscall_icreate`, `afs_syscall_iopen`, `afs_syscall_iincdec` returning `EINVAL`.

## Control Flow
`afs_osi_suser` wraps OpenBSD `suser`/`suser_ucred` and normalizes success to true. Allocators choose `malloc/free` or legacy `MALLOC/FREE` depending on OpenBSD version. Sleeping allocations drop `AFS_GLOCK` if currently held, then reacquire it.

## State and Persistence
No owned persistent state. Allocation uses kernel heap type `M_AFSGENERIC`. Inode syscall stubs do not modify state.

## Dependencies and Integration Points
Used by `osi_machdep.h` macros for `AFS_KALLOC` and privilege checks. Depends on OpenBSD malloc APIs and process accounting fields.

## Risks
Dropping GLOCK around allocation allows concurrent AFS state changes, so callers must tolerate that. The `afs_suser` macro in the header always checks current credentials, not necessarily the passed credential. Inode syscall stubs mean server/salvager inode operations are unsupported on this platform.

## Test Signals
Privilege tests for root/non-root callers, allocation tests under held and unheld GLOCK, build checks for both legacy and newer OpenBSD allocation APIs, and explicit tests that inode syscalls fail cleanly with `EINVAL`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/OBSD/osi_misc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/OBSD/osi_prototypes.h -->
# sources/distributed-fs/openafs/src/afs/OBSD/osi_prototypes.h

## Purpose
Placeholder OpenBSD OSI prototypes header.

## Important APIs, Types, and Functions
Contains only an include guard and a stale comment saying "macos support routines"; it declares nothing.

## Control Flow
None.

## State and Persistence
None.

## Dependencies and Integration Points
Provides a platform header name expected by shared include paths without exporting OpenBSD-specific prototypes.

## Risks
The misleading comment and lack of prototypes can hide missing declarations until compile/link time.

## Test Signals
Build OpenBSD kernel module with warnings enabled for missing prototypes and verify consumers do not rely on declarations from this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/OBSD/osi_prototypes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/OBSD/osi_sleep.c -->
# sources/distributed-fs/openafs/src/afs/OBSD/osi_sleep.c

## Purpose
OpenBSD wait, sleep, timed sleep, wakeup, and time primitives for common OpenAFS code.

## Important APIs, Types, and Functions
Defines `osi_Time`, `afs_osi_CancelWait`, `afs_osi_Wait`, `afs_osi_TimedSleep`, `afs_osi_Sleep`, `afs_osi_SleepSig`, and `afs_osi_Wakeup`. Maintains `afs_evhasht[AFS_EVHASHSIZE]` and `afs_evhashcnt`.

## Control Flow
`afs_osi_Wait` computes a deadline, records the current process in the optional wait handle, drops GLOCK, and uses `tsleep` on a static wait variable until timeout, signal, or cancellation. Event sleep maps arbitrary event addresses into `afs_event_t` entries with sequence counters. Timed sleep records the current sequence, sleeps with `tsleep`, and treats unchanged sequence as interruption/timeout handling.

## State and Persistence
In-memory event hash entries are allocated and reused; each tracks event pointer, refcount, next pointer, and sequence. Wait handles store the sleeping process pointer. No persistent storage.

## Dependencies and Integration Points
Depends on OpenBSD `tsleep`, `wakeup`, `getmicrotime`, timer macros, and OpenAFS global lock discipline. Common AFS code uses this for cache waits, daemon coordination, and cancellation.

## Risks
Event entries are never freed, only reused when refcount reaches zero. Race behavior depends on GLOCK protection around event refcounts. `afs_osi_SleepSig` ignores signals and returns 0.

## Test Signals
Test timeout, interruptible wait, cancellation, wakeup sequencing, repeated event reuse, and lock assertions that sleep paths drop/reacquire GLOCK correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/OBSD/osi_sleep.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/OBSD/osi_vcache.c -->
# sources/distributed-fs/openafs/src/afs/OBSD/osi_vcache.c

## Purpose
OpenBSD vcache allocation, vnode attachment, vnode hold, and eviction helpers.

## Important APIs, Types, and Functions
Defines `osi_TryEvictVCache`, `osi_NewVnode`, `osi_PrePopulateVCache`, `osi_AttachVnode`, `osi_PostPopulateVCache`, and `osi_vnhold`.

## Control Flow
Eviction checks zero vnode refs, no opens, and not `CUnlinkedDel`; then drops GLOCK and calls `vgone`, causing vnode reclaim and `afs_FlushVCache`. Allocation creates a zero-prepared `struct vcache`. Attachment temporarily releases `afs_xvcache` and GLOCK to call `afs_obsd_getnewvnode`, then re-acquires and initializes the vcache rwlock. Post-populate sets mount and regular-file type.

## State and Persistence
Manages in-memory `struct vcache` and its associated `struct vnode`. No disk persistence.

## Dependencies and Integration Points
Depends on OpenBSD vnode lifecycle (`vgone`, `getnewvnode`, `vget`) and `afs_xvcache`. Works with `OBSD/osi_vfsops.c` for vnode allocation and `OBSD/osi_vnodeops.c` for reclaim.

## Risks
Dropping global/vcache locks during vnode allocation permits races, so `seq` and higher-level cache population must guard reuse. Eviction relies on accurate ref/open counts.

## Test Signals
Cache pressure eviction, vnode creation/reclaim, root vnode holds, unlinked-open file behavior, and lock-order diagnostics around `osi_AttachVnode`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/OBSD/osi_vcache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/OBSD/osi_vfsops.c -->
# sources/distributed-fs/openafs/src/afs/OBSD/osi_vfsops.c

## Purpose
OpenBSD VFS and loadable-kernel-module glue for mounting AFS, obtaining the root vnode, registering syscalls, and loading/unloading vnode/VFS operations.

## Important APIs, Types, and Functions
Defines `afs_vfsops`, `afs_obsd_lookupname`, `afs_mount`, `afs_unmount`, `afs_root`, `afs_statfs`, `afs_sync`, `afs_vget`, `afsinit`, `afs_vfs_load`, `afs_vfs_unload`, and `libafs_lkmentry`. Also provides unsupported `quotactl`, `sysctl`, export, and file-handle conversion stubs.

## Control Flow
Mount rejects updates and remounts, sets global VFS and statfs fields, and returns fake capacity. Root initializes an AFS request, checks CM init, fetches `afs_rootFid`, holds it as `afs_globalVp`, sets `VROOT`, and returns it locked. Unmount rejects busy vnodes, releases the global root, flushes, runs cold shutdown, and restores stolen syscall entries. Module load registers vnode ops and memory type names; unload refuses while AFS is active and restores syscall state.

## State and Persistence
Global kernel state includes `afs_globalVFS`, `afs_globalVp`, `lkmid`, `old_sysent`, VFS config, memory type names, and modified `sysent` entries. Persistent filesystem state is remote AFS, not local here.

## Dependencies and Integration Points
Depends on OpenBSD VFS/LKM/namei/syscall internals, common AFS init/shutdown, `afs3_syscall`, `afs_xioctl`, `Afs_xsetgroups`, and vnode ops from `OBSD/osi_vnodeops.c`.

## Risks
Patching syscall tables is invasive and must be restored exactly. Unmount busy checks only v_usecount and does not support forced unmount. Root vnode over-holding is controlled by compile-time behavior. VFS API drift is high risk.

## Test Signals
Load/unload cycles, mount/remount rejection, root lookup, statfs values, busy unmount, syscall interception/restoration, and module unload refusal while root vnode or ioctl hook is active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/OBSD/osi_vfsops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/OBSD/osi_vm.c -->
# sources/distributed-fs/openafs/src/afs/OBSD/osi_vm.c

## Purpose
OpenBSD VM/cache coherency helpers for flushing, invalidating, and resizing vnode pages associated with AFS vcaches.

## Important APIs, Types, and Functions
Defines `osi_VM_FlushVCache`, `osi_VM_StoreAllSegments`, `osi_VM_TryToSmush`, `osi_VM_FlushPages`, and `osi_VM_Truncate`.

## Control Flow
Flush paths drop GLOCK and call `cache_purge` plus `uvm_vnp_uncache`, then reacquire GLOCK. Try-to-smush temporarily releases the vcache write lock around `osi_VM_FlushVCache`. FlushPages purges pages and resets UVM size to the vcache length. Truncate calls `uvm_vnp_setsize`.

## State and Persistence
Mutates OpenBSD VM page cache and vnode UVM size only. Does not itself write dirty pages back to servers; `osi_VM_StoreAllSegments` is a no-op.

## Dependencies and Integration Points
Depends on OpenBSD UVM, name cache purge, common AFS vcache locks, callback revocation paths, flush commands, and truncation flows.

## Risks
No-op store-all means callers must not rely on this function to persist dirty data on OpenBSD. Flush functions drop locks, so concurrent page creation can occur after return. The Solaris-style `activeV` comment notes stronger behavior elsewhere than OpenBSD provides.

## Test Signals
Callback revocation should purge stale pages, truncation should adjust mapped size, cache recycle should not retain stale UVM pages, and concurrent readers/writers should not panic under UVM assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/OBSD/osi_vm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/OBSD/osi_vnodeops.c -->
# sources/distributed-fs/openafs/src/afs/OBSD/osi_vnodeops.c

## Purpose
OpenBSD vnode operation table and VOP wrappers that adapt OpenBSD vnode calls to common OpenAFS cache-manager operations.

## Important APIs, Types, and Functions
Defines either `struct vops afs_vops` for newer OpenBSD or `afs_vnodeop_p`/`afs_vnodeop_entries` for older kernels. Handlers include `afs_obsd_lookup`, `create`, `open`, `close`, `access`, `getattr`, `setattr`, `read`, `write`, `ioctl`, `select`, `fsync`, `remove`, `link`, `rename`, `mkdir`, `rmdir`, `symlink`, `readdir`, `readlink`, `inactive`, `reclaim`, `lock`, `unlock`, `bmap`, `strategy`, `print`, `islocked`, `pathconf`, and `advlock`.

## Control Flow
Name-based operations use `GETNAME`/`DROPNAME` to copy component names. Lookup calls `afs_lookup`, maps create/rename ENOENT to `EJUSTRETURN`, and returns the child locked while respecting parent lock flags. File operations wrap `afs_open`, `afs_close`, `afs_read`, `afs_write`, and metadata routines under GLOCK. Mutating directory operations release vnode refs carefully after core AFS calls. Strategy constructs a kernel `uio` over the buffer and calls `afs_rdwr`.

## State and Persistence
Maintains vnode locks, refs, namei buffers, vcache locks, and AFS file/cache state. Write invalidates VM pages first. Reclaim flushes vcaches but leaves on-disk cache data.

## Dependencies and Integration Points
Depends on OpenBSD VFS/vnode/namei APIs, `lockmgr`, OpenAFS core vnode operations, `afs_xvcache`, and platform macros from `osi_machdep.h`.

## Risks
Error-path reference handling in lookup/rename/link/remove is high risk. `afs_obsd_select` always returns ready. Strategy manually releases `tvc->lock` and vnode refs, so caller assumptions must match. Kernel-version conditionals increase maintenance cost.

## Test Signals
Vnode operation regression tests for lookup/create/remove/rename, lock/unlock recursion, mmap/write stale-page behavior, buffer strategy reads/writes, advlock, pathconf, and busy vnode reclaim under cache pressure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/OBSD/osi_vnodeops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/SOLARIS/osi_crypto.c -->
# sources/distributed-fs/openafs/src/afs/SOLARIS/osi_crypto.c

## Purpose
Solaris random-byte provider for OpenAFS kernel code.

## Important APIs, Types, and Functions
Defines `osi_readRandom(void *data, afs_size_t len)`, which calls `random_get_pseudo_bytes(data, len)` and returns `0`.

## Control Flow
Straight-line wrapper around Solaris kernel pseudo-random bytes.

## State and Persistence
No state is owned in this file. Random state is owned by the Solaris kernel.

## Dependencies and Integration Points
Includes `<sys/random.h>`. Used by common OpenAFS crypto/random consumers.

## Risks
Uses pseudo-random API and reports success unconditionally. No validation of buffer pointer or length is performed.

## Test Signals
Solaris kernel build symbol resolution and random consumer smoke tests that request nonzero random material.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/SOLARIS/osi_crypto.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/SOLARIS/osi_file.c -->
# sources/distributed-fs/openafs/src/afs/SOLARIS/osi_file.c

## Purpose
Solaris cache-file access layer for disk-backed OpenAFS cache entries, supporting UFS, optional VXFS, and path-based cache vnode lookup.

## Important APIs, Types, and Functions
Defines `afs_InitDualFSCacheOps`, `VnodeToIno`, `VnodeToDev`, `VnodeToSize`, `osi_VxfsOpen`, `osi_UfsOpen`, `osi_UFSOpen`, `afs_osi_Stat`, `osi_UFSClose`, `osi_UFSTruncate`, `osi_DisableAtimes`, `afs_osi_Read`, `afs_osi_Write`, `afs_osi_MapStrategy`, and `shutdown_osifile`.

## Control Flow
Cache open initializes root credentials, chooses VXFS or UFS, and either looks up by path (`AFS_CACHE_VNODE_PATH`) or calls `igetinode`. Stat/truncate/read/write drop GLOCK around VOP or `vn_rdwr` calls. Reads update offsets and disable UFS atimes; writes update offsets and invoke callback procs. Dual FS detection uses `VFS_STATVFS` and `modlookup("vxfs", "vx_vp_byino")`.

## State and Persistence
Persistent bytes are Solaris cache vnodes. In-memory state includes `afs_osicred_initialized`, `afs_CacheFSType`, `vxfs_vx_vp_byino`, wrapper offsets/sizes/proc callbacks, and credential pointer `afs_osi_credp`.

## Dependencies and Integration Points
Depends on Solaris VFS/VOP, UFS inode helpers from `SOLARIS/osi_inode.c`, optional VXFS module symbols, root credentials, and OpenAFS cache type flags.

## Risks
Many failures panic, especially inode/path lookup failures during cache open. Atime disabling touches UFS internals and is disabled for vnode-path caches. VXFS and UFS symbol lookup are kernel-version sensitive. Path buffer is fixed at 1024 bytes.

## Test Signals
Open/read/write/stat/truncate cache files for UFS and path-backed cache, optional VXFS open if configured, atime suppression on UFS, missing cache file behavior, and cold shutdown reset of credential initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/SOLARIS/osi_file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/SOLARIS/osi_gcpags.c -->
# sources/distributed-fs/openafs/src/afs/SOLARIS/osi_gcpags.c

## Purpose
Solaris PAG garbage-collection support: traverse active processes and expose process credentials.

## Important APIs, Types, and Functions
Defines `afs_osi_TraverseProcTable` and `afs_osi_proc2cred` under `AFS_GCPAGS`.

## Control Flow
Traversal iterates `practive` via `p_next` and calls `afs_GCPAGs_perproc_func` for each process. Credential lookup returns `pr->p_cred` or `NULL`.

## State and Persistence
No owned state. Reads live process table and credential pointers.

## Dependencies and Integration Points
Depends on Solaris process-list globals and OpenAFS common PAG GC callback. Used to identify PAGs no longer referenced by active processes.

## Risks
Traversal has implicit process table locking assumptions not visible in this file. Returned credentials are borrowed pointers. Process-list APIs are historically unstable.

## Test Signals
Build with `AFS_GCPAGS`, run PAG GC under process churn, verify null handling, and ensure traversal does not race or panic on active-process list changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/SOLARIS/osi_gcpags.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/SOLARIS/osi_groups.c -->
# sources/distributed-fs/openafs/src/afs/SOLARIS/osi_groups.c

## Purpose
Solaris PAG implementation around `setgroups`, supporting both legacy two-gid PAG encoding and newer one-group PAG encoding.

## Important APIs, Types, and Functions
Exports `afs_xsetgroups`, `setpag`, and, under `AFS_PAG_ONEGROUP_ENV`, `osi_get_group_pag`. Internal helpers include `pag_to_gidset`, `afs_getgroups`, and `afs_setgroups`.

## Control Flow
`afs_xsetgroups` initializes a request from process credentials, calls Solaris `setgroups`, then restores a previously established PAG if the new credentials lack one. `setpag` generates a PAG if needed, allocates a group array sized by `ngroups_max`, locks `curproc->p_crlock`, reads existing groups, encodes the PAG, and calls `afs_setgroups`, which may copy credentials and broadcasts them to all process threads via `crset`.

## State and Persistence
Mutates process credentials and supplemental group lists. No disk state. The encoding location differs: one-gid mode can place a PAG in any group slot; legacy mode writes two gids at the front.

## Dependencies and Integration Points
Depends on Solaris credential APIs (`crgetgroups`, `crsetgroups`, `crcopy`, `crset`), process credential locks, syscall interception in `osi_vfsops.c`, and OpenAFS PAG helpers.

## Risks
Credential lock release is delegated to `afs_setgroups`, so all error paths must be exact. Group-list sizes can be large on Solaris 11, requiring heap allocation instead of small-space allocation. Legacy group ordering can conflict with OS group sorting.

## Test Signals
Setpag on empty/full/large group lists, one-gid and two-gid builds, setgroups PAG preservation, credential propagation to all threads, and error handling when allocation or capacity checks fail.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/SOLARIS/osi_groups.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/SOLARIS/osi_inode.c -->
# sources/distributed-fs/openafs/src/afs/SOLARIS/osi_inode.c

## Purpose
Solaris UFS inode syscall support for OpenAFS server/cache inode operations, including inode creation, open-by-inode, and link-count increment/decrement.

## Important APIs, Types, and Functions
Defines `getinode`, `igetinode`, `afs_syscall_icreate`, `afs_syscall_iopen`, and `afs_syscall_iincdec`. Uses UFS function pointers `ufs_iallocp`, `ufs_iupdatp`, `ufs_igetp`, `ufs_itimes_nolockp`, plus `CrSync` and `IncSync`.

## Control Flow
`getinode` resolves a VFS by device, enters quota lock if present, and calls `ufs_iget`. `igetinode` validates allocation, link count, and regular-file mode, optionally adds a fake DNLC entry. `icreate` checks superuser, opens root inode, allocates a new inode near a hint, stamps VICEMAGIC and vice metadata fields, syncs, and returns the inode number. `iopen` opens an existing inode into a file descriptor. `iincdec` validates VICEMAGIC, adjusts link count, clears magic on zero, and syncs if configured.

## State and Persistence
Mutates persistent UFS inode metadata: mode, link count, vice fields, timestamps, and magic values. Also creates process file descriptors for opened inodes and DNLC aliases.

## Dependencies and Integration Points
Depends on Solaris UFS internals and symbols resolved in `SOLARIS/osi_vfsops.c`, credential privilege checks, vnode/file descriptor APIs, and `SOLARIS/osi_inode.h` macros.

## Risks
This code reaches deep into UFS private structures and symbol pointers; missing symbols degrade functionality. Incorrect vice field packing can orphan cache/server data. Superuser checks gate destructive inode operations. Endianness and 32/64-bit rval handling are sensitive.

## Test Signals
Privileged icreate/iopen/iincdec round trips, non-root EPERM, link count decrement to zero clearing VICEMAGIC and DNLC alias, 32-bit and 64-bit syscall return values, and missing UFS symbol warnings at module init.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/SOLARIS/osi_inode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/SOLARIS/osi_inode.h -->
# sources/distributed-fs/openafs/src/afs/SOLARIS/osi_inode.h

## Purpose
Solaris inode metadata macros for OpenAFS inode-based server/cache support.

## Important APIs, Types, and Functions
Defines `BAD_IGET`, `VICEMAGIC`, vice field accessors for disk and in-core inodes, `IS_VICEMAGIC`, `IS_DVICEMAGIC`, `CLEAR_VICEMAGIC`, `CLEAR_DVICEMAGIC`, and cache FS type constants `AFS_SUN_UFS_CACHE` and optional `AFS_SUN_VXFS_CACHE`.

## Control Flow
No runtime control flow; all behavior is macro expansion.

## State and Persistence
Macros read and write persistent inode fields repurposed for OpenAFS vice metadata and magic markers.

## Dependencies and Integration Points
Used by `SOLARIS/osi_inode.c` and `SOLARIS/osi_file.c`. Depends on Solaris UFS inode member names and compile-time VXFS availability.

## Risks
Repurposing inode uid/gid/gen/flags fields is tightly coupled to UFS layouts. A structure change can corrupt metadata or make `IS_VICEMAGIC` unreliable.

## Test Signals
Compile against target Solaris UFS headers, create and inspect VICEMAGIC inodes, clear magic on link-count zero, and validate salvager/server interpretation of vice fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/SOLARIS/osi_inode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/SOLARIS/osi_ioctl.c -->
# sources/distributed-fs/openafs/src/afs/SOLARIS/osi_ioctl.c

## Purpose
Solaris 11 `/dev/afs` ioctl emulation for the older AFS syscall interface.

## Important APIs, Types, and Functions
Under `AFS_SUN511_ENV`, defines character-device callbacks `devafs_open`, `devafs_close`, `devafs_ioctl`, `devafs_getinfo`, `devafs_attach`, `devafs_detach`, `afs_devops`, and `afs_modldrv`.

## Control Flow
Open/close validate minor number and character-device open type. Ioctl accepts `VIOC_SYSCALL` and `VIOC_SYSCALL32`, copies user args with `ddi_copyin`, maps them into `struct afssysa`, calls `Afs_syscall`, and returns either syscall error or `rv.r_val1`. Attach creates the minor node `afs`; detach removes properties and the minor node.

## State and Persistence
Global `devafs_dip` tracks the attached device instance. No persistent data is stored.

## Dependencies and Integration Points
Depends on Solaris DDI/DDK character device APIs and `Afs_syscall`. Integrated into module linkage from `SOLARIS/osi_vfsops.c` for Solaris 11.

## Risks
Only a single minor is supported. Return-value mapping treats successful `Afs_syscall` rval as an error code for ioctl callers. Copyin mode and 32/64-bit struct layouts must match userland.

## Test Signals
Solaris 11 attach creates `/dev/afs`, invalid minors fail, both 32-bit and native ioctl paths dispatch to AFS syscall, and detach removes the minor without leaving `devafs_dip` stale.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/SOLARIS/osi_ioctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/SOLARIS/osi_kstat.c -->
# sources/distributed-fs/openafs/src/afs/SOLARIS/osi_kstat.c

## Purpose
Solaris kstat provider exposing OpenAFS cache-manager parameters, cache statistics, and Rx network statistics.

## Important APIs, Types, and Functions
Defines kstat data structs `afs_param_kstat`, `afs_cache_kstat`, `afs_rx_kstat`, update handlers `afs_param_ks_update`, `afs_cache_ks_update`, `afs_rx_ks_update`, and lifecycle functions `afs_kstat_init`/`afs_kstat_shutdown`.

## Control Flow
Initialization creates virtual named kstats `openafs:param`, `openafs:cache`, and `openafs:rx`, fills primary cell name, assigns update callbacks, adjusts string data size, and installs each kstat if creation succeeds. Update callbacks reject writes with `EACCES` and copy values from `cm_initParams`, `afs_stats_cmperf`, global cache counters, `AFSVersion`, and `rx_stats`. Shutdown deletes installed kstats and clears pointers.

## State and Persistence
Maintains static kstat handles and static `cellname`. Exposes live counters but does not persist them.

## Dependencies and Integration Points
Depends on Solaris kstat, OpenAFS cell/cache/stat structures, Rx atomic stats, and AFS global lock precondition noted for init.

## Risks
Virtual kstat structs must match named count and string sizing. Some Rx fields are atomic and some are not, so snapshots are approximate. Missing primary cell becomes `-UNKNOWN-`.

## Test Signals
After module init, `kstat` should list all three groups. Reads should update counters and reject writes. Shutdown should remove kstats. Validate cell/version strings and representative cache/Rx counters under activity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/SOLARIS/osi_kstat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/SOLARIS/osi_machdep.h -->
# sources/distributed-fs/openafs/src/afs/SOLARIS/osi_machdep.h

## Purpose
Solaris machine-dependent OSI header mapping generic OpenAFS kernel code to Solaris credentials, time, global locking, VFS helpers, large-file checks, and interface structures.

## Important APIs, Types, and Functions
Defines `afs_ucred_t`, `afs_proc_t`, `osi_Time`, `gop_rdwr`, `gop_lookupname`, `afs_suser`, `AFS_GLOCK`, `AFS_GUNLOCK`, `ISAFS_GLOCK`, `osi_InitGlock`, lock flag aliases, `IO_APPEND`, `IO_SYNC`, `AfsLargeFileUio`, `AfsLargeFileSize`, `struct afs_ifinfo`, `osi_procname`, and `osi_GetTime`.

## Control Flow
Compile-time feature macros choose `gethrestime` versus `hrestime`, secpolicy-aware superuser checks, Solaris 10 interface declarations, and 64-bit model support.

## State and Persistence
Declares external `kmutex_t afs_global_lock`, Solaris taskq/interface locks, and reads kernel time/process state. No persistent storage.

## Dependencies and Integration Points
Included through `afs_osi.h` by Solaris platform files and common OpenAFS code. It provides the core GLOCK contract used across Solaris vnode, VFS, file, and VM layers.

## Risks
Large-file macros inspect Solaris-private `uio` fields in non-64-bit clients. `osi_Time` can depend on different kernel time APIs by release. Global-lock macros are simple mutex operations, so callers must not recurse.

## Test Signals
Compile Solaris 9/10/11 variants, verify GLOCK ownership assertions, large-file rejection in 32-bit clients, time retrieval, and NFS translator module path checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/SOLARIS/osi_machdep.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/SOLARIS/osi_prototypes.h -->
# sources/distributed-fs/openafs/src/afs/SOLARIS/osi_prototypes.h

## Purpose
Solaris OSI prototype header for platform functions shared across Solaris source files.

## Important APIs, Types, and Functions
Declares `afs_putpage`, `afs_putapage`, and `afs_xsetgroups`, with Solaris 11 signature variants using `caller_context_t` and `int64_t` syscall returns.

## Control Flow
No runtime flow; preprocessor selects ABI-specific prototypes.

## State and Persistence
None.

## Dependencies and Integration Points
Ensures `SOLARIS/osi_vm.c`, `osi_vnodeops.c`, and syscall/VFS code agree on signatures for pageout and setgroups interception.

## Risks
Prototype drift can cause kernel ABI mismatches. Solaris 11 and older signatures differ in size types and caller context handling.

## Test Signals
Build all Solaris release targets with warnings for incompatible declarations, especially `afs_putpage` and `afs_xsetgroups`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/SOLARIS/osi_prototypes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/SOLARIS/osi_sleep.c -->
# sources/distributed-fs/openafs/src/afs/SOLARIS/osi_sleep.c

## Purpose
Solaris wait, sleep, timed sleep, signalable sleep, wakeup, and wait-handle primitives for OpenAFS.

## Important APIs, Types, and Functions
Defines `afs_osi_InitWaitHandle`, `afs_osi_CancelWait`, `afs_osi_Wait`, `afs_osi_Sleep`, `afs_osi_SleepSig`, `afs_osi_TimedSleep`, and `afs_osi_Wakeup`. Maintains `afs_evhasht[AFS_EVHASHSIZE]`.

## Control Flow
Wait handles store `curthread`; cancellation clears the pointer and wakes a static wait variable. Event addresses are hashed to `afs_event_t` entries with condition variables and sequence counters. Sleeps wait on the event condvar while GLOCK is held by using `cv_wait`/`cv_wait_sig` on `afs_global_lock`. Timed sleep converts milliseconds to lbolt deadlines and uses timed condvar waits.

## State and Persistence
In-memory event table entries track event pointer, refcount, sequence, next pointer, and Solaris condition variable. No persistent state.

## Dependencies and Integration Points
Depends on Solaris condition variables, `afs_global_lock`, lbolt/DDI time APIs, and common AFS wait/event users.

## Risks
Event entries are reused but not freed. `afs_osi_Wakeup` calls `afs_getevent`, which creates an event entry even for wakeups with no sleepers. Return value currently always returns 0 despite tracking `ret`.

## Test Signals
Timed wait timeout and signal behavior, cancellation, wakeup broadcast to multiple sleepers, event reuse under churn, and lock assertions around condvar waits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/SOLARIS/osi_sleep.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/SOLARIS/osi_vcache.c -->
# sources/distributed-fs/openafs/src/afs/SOLARIS/osi_vcache.c

## Purpose
Solaris vcache and vnode lifecycle helpers, including eviction, allocation, initialization, attachment, and hold semantics.

## Important APIs, Types, and Functions
Defines `osi_TryEvictVCache`, `osi_NewVnode`, `osi_PrePopulateVCache`, `osi_AttachVnode`, `osi_PostPopulateVCache`, and `osi_vnhold`.

## Control Flow
Eviction calls `afs_FlushVCache` only when vnode refs are zero, no opens exist, and the file is not in unlinked-delete state. Pre-population clears the vcache, initializes `multiPage`, vcache locks, and pre-Solaris-11 `v_data`. Solaris 11 attachment allocates a vnode with `vn_alloc`. Post-populate assigns vnode ops, VFS, regular type, and holds the VFS. `osi_vnhold` increments `v_count` and holds the VFS when transitioning from zero.

## State and Persistence
Manages in-memory vcache, vnode, locks, multipage queue, vnode refcount, and VFS refcount. No disk persistence.

## Dependencies and Integration Points
Depends on Solaris vnode allocation, `afs_ops` from vnodeops registration, `afs_globalVFS`, and VM multi-page conflict logic in `osi_vm.c`/`osi_vnodeops.c`.

## Risks
VFS holds must match vnode refs or unmount will hang/leak. Pre-Solaris-11 `v_data` workaround for KAIO is fragile. Eviction depends on exact ref/open counts and `afs_FlushVCache` behavior.

## Test Signals
Vcache allocation/population, vnode refcount zero-to-one transitions, unmount with root vnode release, cache eviction under pressure, and Solaris 11 `vn_alloc` path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/SOLARIS/osi_vcache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/SOLARIS/osi_vfsops.c -->
# sources/distributed-fs/openafs/src/afs/SOLARIS/osi_vfsops.c

## Purpose
Solaris VFS/module glue for the OpenAFS filesystem, syscall/ioctl hooks, root vnode acquisition, VFS operation registration, UFS/NFS translator symbol lookup, and module lifecycle.

## Important APIs, Types, and Functions
Defines `afs_mount`, `afs_unmount`, `gafs_freevfs`, `afs_root`, `afs_statvfs`, `afs_sync`, `afs_vget`, `afs_mountroot`, `afs_swapvp`, `afsinit`, `_init`, `_info`, `_fini`, and operation tables/templates. Tracks syscall originals and UFS/NFS function pointers.

## Control Flow
Mount checks privileges, rejects remount, initializes `afs_globalVFS`, fsid, block size, and dev. Unmount checks privilege, rejects forced unmount, enforces VFS/root vnode refcount constraints, marks VFS unmounted, and releases root. Root fetches or refreshes `afs_globalVp`, carefully drops covered-vnode lock if an RPC may occur, holds the root vnode, and sets `VROOT`. `afsinit` hooks setgroups/ioctl syscalls, registers VFS/vnode ops, looks up NFS translator and UFS symbols, and marks initialized. `_init` verifies required modules, initializes locks, installs module linkage, and restores hooks on failure.

## State and Persistence
Global state includes `afs_globalVFS`, `afs_globalVp`, `afsfstype`, syscall hook originals, UFS function pointers, NFS translator pointers, module init flag, and VFS/vnode op registrations.

## Dependencies and Integration Points
Depends on Solaris module subsystem, VFS op registration (`vfs_setfsops`, `vn_make_ops`), syscall tables, `modlookup`, UFS, optional `nfssrv`, `osi_ioctl.c` for Solaris 11 `/dev/afs`, and common AFS init/shutdown.

## Risks
Syscall table patching and restoration are high risk, especially 32-bit table variants. Module loading depends on UFS and optional NFS modules being present. Root acquisition includes lock dropping to avoid deadlocks. Unmount depends on exact refcounts.

## Test Signals
Module load/unload success/failure paths, missing UFS/NFS modules, mount permission checks, duplicate mount rejection, root vnode retrieval, statvfs values, busy unmount, syscall hook restoration, and Solaris 10/11 op registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/SOLARIS/osi_vfsops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/SOLARIS/osi_vm.c -->
# sources/distributed-fs/openafs/src/afs/SOLARIS/osi_vm.c

## Purpose
Solaris VM coherency helpers for flushing, invalidating, storing, and truncating pages for AFS vcaches and dcaches.

## Important APIs, Types, and Functions
Defines `osi_VM_GetDownD`, `osi_VM_MultiPageConflict`, `osi_VM_FlushVCache`, `osi_VM_StoreAllSegments`, `osi_VM_TryToSmush`, `osi_VM_FlushPages`, `osi_VM_PreTruncate`, and `osi_VM_Truncate`.

## Control Flow
`GetDownD` invalidates pages for a specific dcache chunk by calling `afs_putpage` outside GLOCK. `MultiPageConflict` checks whether a dcache chunk overlaps any active multipage getpage range. `FlushVCache` rejects busy refs/opens/locks, invalidates all vnode pages with `pvn_vplist_dirty`, verifies no pages remain, destroys rwlock, and frees stored creds. Store/smush use `pvn_vplist_dirty` with `afs_putapage`. PreTruncate zeros the unused tail of the final page. Truncate invalidates pages beyond new EOF.

## State and Persistence
Mutates Solaris page cache, vcache `credp`, rwlock lifecycle, and global `afs_pvn_vptrunc` counter. It does not directly persist data to the AFS server except through `afs_putapage`/cache writes.

## Dependencies and Integration Points
Depends on Solaris VM/page/pvn APIs, `afs_putpage`/`afs_putapage` from vnodeops, vcache multipage queues, `afs_indexFlags`, and cache eviction/truncation paths.

## Risks
Incorrect page invalidation can deadlock with multipage faults or leave stale cache pages. Lock preconditions are strict and differ by function. `FlushVCache` destroys `rwlock`, so callers must ensure no later users remain.

## Test Signals
Mapped read/write files, dcache eviction during multipage faults, callback flush, truncate to non-page-aligned length, cache pressure reclaim, read-only volume page handling, and lock-order stress tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/SOLARIS/osi_vm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/SOLARIS/osi_vnodeops.c -->
# sources/distributed-fs/openafs/src/afs/SOLARIS/osi_vnodeops.c

## Purpose
Solaris vnode operations for OpenAFS, including VM page-in/page-out, segmap read/write, mmap, lock, pathconf, and wrappers from Solaris VOPs to common AFS operations.

## Important APIs, Types, and Functions
Defines `afs_fc2errno`, `afs_addmap`, `afs_delmap`, `afs_vmread`, `afs_vmwrite`, `afs_getpage`, `afs_GetOnePage`, `afs_putpage`, `afs_putapage`, `afs_nfsrdwr`, `afs_map`, `afs_pathconf`, `afs_ioctl`, `afs_rwlock`, `afs_rwunlock`, `afs_seek`, `afs_frlock`, `afs_space`, `afs_dump`, `afs_cmp`, `afs_realvp`, `afs_pageio`, `afs_dumpctl`, security-attribute stubs, `gafs_*` wrappers, `afs_inactive`, `gafs_inactive`, `gafs_fid`, and vnode op tables/templates.

## Control Flow
Read/write VOPs require the vcache rwlock and call `afs_nfsrdwr` under GLOCK. `afs_getpage` dispatches single pages to `afs_GetOnePage`; multipage faults register a range in `avc->multiPage` so cache eviction avoids deadlocking on already locked pages. `afs_GetOnePage` resolves/validates dcaches, creates or looks up pages, performs `afs_ustrategy` reads, marks page flags, and prefetches next chunks. `afs_putpage` gathers dirty pages and calls `afs_putapage`; read-only volume pages use a panic-on-dirty dummy callback. `afs_nfsrdwr` performs segmap-backed I/O, handles append/ulimit/large-file checks, fake opens, dirty state, partial writes, and NFS translator credentials. `gafs_*` functions wrap core AFS operations in GLOCK for the Solaris vnode ABI.

## State and Persistence
Mutates vcache length/date/dirty/mapped flags, dcache flags, `afs_indexFlags` page bits, Solaris pages, stored NFS translator credentials, vnode/VFS refs, and remote/cache data through core AFS calls. Inactive decrements Solaris vnode count and releases VFS refs.

## Dependencies and Integration Points
Depends on Solaris VM (`page_*`, `pvn_*`, `segmap_*`), VFS/vnode ABI variants for Solaris 10/11, common OpenAFS cache manager, `SOLARIS/osi_vm.c`, `SOLARIS/osi_vcache.c`, Rx/NFS translator request handling, and `afs_ops` registration in VFS init.

## Risks
This is a high-risk concurrency file. Page locks, vcache locks, dcache locks, GLOCK, and segmap faults must occur in the intended order. Dirty-page accounting and read-only volume pageout are correctness-sensitive. `afs_nfsrdwr` changes file length before data movement for writes and must clean up through fake close/partial writes on error.

## Test Signals
Mapped read/write, large multipage faults, cache eviction during faults, write past EOF, append and ulimit behavior, dirty page flush, read-only volume mmap, NFS translator credential reads, inactive after exec, frlock/space truncation, pathconf, and Solaris 10/11 vnode op registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/SOLARIS/osi_vnodeops.c -->
