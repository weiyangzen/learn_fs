# Research: subset-b-007749

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/AIX/osi_vnodeops.c -->
# sources/distributed-fs/openafs/src/afs/AIX/osi_vnodeops.c

## Purpose
This file is the AIX vnode and VFS operation adapter for the OpenAFS cache manager. It translates AIX gnode/vnode/VFS callbacks into the portable AFS operations, manages the AIX VM segment path for file I/O, queues asynchronous buffers for background daemons, and exports both raw and global-lock-wrapped operation tables.

## Important APIs, Types, And Functions
The public vnode entry points are `afs_gn_lookup`, `afs_gn_create`, `afs_gn_open`, `afs_gn_close`, `afs_gn_rdwr`, `afs_gn_fsync`, `afs_gn_fclear`, `afs_gn_ftrunc`, directory mutators, symlink/readlink, `afs_gn_lockctl`, `afs_gn_ioctl`, `afs_gn_strategy`, and unsupported ACL/PCL/revoke slots. `afs_vm_rdwr` is the VM-backed read/write engine, while `afs_direct_rdwr` handles 64-bit offsets beyond `afs_vmMappingEnd`. `afs_gn_vnodeops`, `locked_afs_gn_vnodeops`, `locked_Afs_vfsops`, and `afs_gfs` are the integration objects AIX consumes.

## Control Flow
Most vnode operations acquire arguments in AIX form, compute OpenAFS flags or `vattr` values, call the common `afs_*` function, trace the result, and return AIX errno values. Open/create perform access checks, non-share waiting on `tvp->opens`, fake open setup for NFS translator paths, and truncation if requested. Reads/writes verify the vcache, flush stale pages, save credentials for later daemon work, select VM or direct I/O, fake open/close writes where AIX does not provide normal open/close RPCs, and optionally return fresh attributes. The strategy path receives a linked buffer list, inserts buffers into the global async queue by vnode/subspace/block order, merges compatible adjacent buffers, and wakes the async daemon.

## State And Persistence
State is stored in `struct vcache` fields such as `segid`, `vmh`, `credp`, `opens`, `vc_error`, `f.states` bits (`CDirty`, `CMAPPED`, `CNSHARE`, `CPageHog`), length/date metadata, and the attached AIX gnode segment. Global async I/O state uses `afs_asyncbuf`, `afs_asyncbuf_lock`, `afs_asyncbuf_cv`, and monotonic `afs_biotime`. The file also maintains `vmPageHog` accounting for very large writes. VFS global state is mostly delegated to `Afs_vfsops`, but the locked wrapper tables persist the correct AIX registration view.

## Dependencies And Integration Points
The file depends on AIX vnode, gnode, VM, shared-memory, buffer, and VFS APIs; OpenAFS cache-manager APIs for lookup, access, create, open, read/write, partial writeback, locking, ioctl, and inactive handling; global AFS locking; ICL tracing; and NFS translator credential conventions. It is the AIX platform bridge for normal filesystem syscalls, mmap-like segment use, NFS server reentry, and background cache I/O.

## Risks
The highest-risk behavior is lock and reference ordering around the global AFS lock, vcache locks, AIX VM segment calls, and asynchronous buffer queues. Errors in fake open/close or saved credential handling can corrupt writer counts or use stale credentials. VM/direct mixed I/O near `afs_vmMappingEnd`, page protection around extending writes, quota/error propagation through `vc_error`, and buffer merging in `afs_gn_strategy` are fragile. Many function-pointer casts and AIX-version conditionals make ABI drift risky.

## Test Signals
Useful signals include successful AIX mount/root/statfs/unmount flows, create/open/truncate/close with `FTRUNC` and `FNSHARE`, NFS translator reads/writes, large writes crossing chunk and VM mapping boundaries, mmap/map/unmap reference counts, lockctl get/set/unlock, ioctl redirection, async strategy queue draining, forced shutdown, and recovery from `EDQUOT`/`ENOSPC`. Trace counters (`AFS_STATCNT`) and ICL events should match syscall activity without leaked vnodes, credentials, or buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/AIX/osi_vnodeops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/DARWIN/osi_crypto.c -->
# sources/distributed-fs/openafs/src/afs/DARWIN/osi_crypto.c

## Purpose
Provides the Darwin kernel implementation of OpenAFS random-byte acquisition.

## Important APIs, Types, And Functions
The only function is `osi_readRandom(void *data, afs_size_t len)`, which calls Darwin `read_random(data, len)` and returns zero.

## Control Flow
Callers pass an output buffer and byte count; the function delegates to the kernel random provider and does no retry, length adjustment, or error mapping.

## State And Persistence
There is no local state. Entropy state is wholly owned by the Darwin kernel random subsystem.

## Dependencies And Integration Points
Depends on `<sys/random.h>` and the OpenAFS `afs_size_t` type. It backs higher-level cache-manager code that needs random data without knowing the host kernel API.

## Risks
The function assumes `read_random` cannot fail or that its failure is not externally reported by this API. Buffer validity and sleepability requirements are inherited from Darwin.

## Test Signals
Build coverage is the main signal. Runtime tests should request non-zero random buffers during token/PAG or crypto-related operations and verify the caller does not receive all-zero or uninitialized data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/DARWIN/osi_crypto.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/DARWIN/osi_file.c -->
# sources/distributed-fs/openafs/src/afs/DARWIN/osi_file.c

## Purpose
Implements Darwin cache-file operations for the OpenAFS disk cache. It opens cache vnodes by stored inode/path identity, reads and writes cache data, truncates cache files, obtains metadata, and detects the backing filesystem type.

## Important APIs, Types, And Functions
`afs_InitDualFSCacheOps` classifies HFS, UFS, or APFS cache backing. `VnodeToIno` and `VnodeToDev` extract stable vnode identifiers. `osi_UFSOpen`, `osi_UFSClose`, `osi_UFSTruncate`, `afs_osi_Stat`, `afs_osi_Read`, `afs_osi_Write`, `osi_DisableAtimes`, and `shutdown_osifile` implement the platform `osi_file` contract.

## Control Flow
Initialization inspects a sample cache vnode mount name once and records `afs_CacheFSType`. Opening validates UFS-style cache mode, creates a minimal `afs_osi_credp` if needed, drops the AFS global lock, resolves the vnode via `vnode_open`, `igetinode`, or path-backed cache configuration, reacquires the global lock, then fills an `osi_file`. Reads and writes update `afile->offset`, drop the global lock around `VNOP_READ`/`VNOP_WRITE` or `gop_rdwr`, translate residual counts into bytes transferred, and run completion callbacks after writes. Truncate first stats the file to avoid unnecessary shrinking work.

## State And Persistence
Persistent state includes global `afs_osicred_initialized`, `afs_osi_credp`, `afs_CacheFSType`, `cacheDev`, and `afs_cacheVfsp`. Each `osi_file` persists a vnode reference, current offset, cached size, and optional completion procedure. Backing cache files persist data and metadata in the host filesystem.

## Dependencies And Integration Points
Depends on Darwin vnode attributes, UBC/VNOP I/O, APFS/HFS/UFS identification, `osi_inode.c` inode resolution, OpenAFS small-space allocation, global lock release/reacquire discipline, and cache-manager callers that use `afs_osi_Read`/`Write`.

## Risks
Incorrect cache filesystem detection can make inode/device extraction panic or return wrong cache IDs. The static OSI credential is intentionally artificial and must be cleaned on cold shutdown. The code relies on dropping the global lock around vnode operations to avoid deadlocks. Residual handling, atime suppression, path-backed cache vnodes, and APFS/HFS/UFS conditionals are compatibility-sensitive.

## Test Signals
Exercise cache initialization on HFS/UFS/APFS where supported, cache file open by inode/path, read/write offset advancement, truncate-to-smaller behavior, stat results, cold shutdown credential cleanup, and failure paths where cache files vanish. Kernel logs should not show `UFSOpen` panics for valid cache entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/DARWIN/osi_file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/DARWIN/osi_gcpags.c -->
# sources/distributed-fs/openafs/src/afs/DARWIN/osi_gcpags.c

## Purpose
Supports PAG garbage collection on Darwin by exposing process traversal and process-to-credential conversion when `AFS_GCPAGS` is enabled.

## Important APIs, Types, And Functions
`afs_osi_TraverseProcTable` walks non-system, non-zombie processes on pre-Darwin 8 kernels. `afs_osi_proc2cred` returns a credential snapshot for a process, using `proc_ucred` on Darwin 8+ or `pcred_readlock` on older kernels.

## Control Flow
The traversal callback filters process states and invokes `afs_GCPAGs_perproc_func`. Credential conversion copies uid and group data into a static `afs_ucred_t` on Darwin variants that require a stable OpenAFS credential view.

## State And Persistence
There is no durable state. Darwin 8+ and older implementations use a static credential copy, so returned pointers are overwritten by subsequent calls.

## Dependencies And Integration Points
Depends on Darwin process lists, process credential APIs, OpenAFS PAG scanner code, `PagInCred` consumers, and group-layout conventions.

## Risks
Static credential storage is not reentrant. Process state and credential lifetimes can race with exit or credential mutation, so the code copies only a small credential subset. Darwin 8+ lacks an in-file process table traversal implementation, so external scanner behavior must supply process iteration.

## Test Signals
Enable `AFS_GCPAGS`, create and destroy processes with PAG-bearing credentials, and confirm stale PAGs are reclaimed while live user processes retain tokens. Concurrency tests should look for corrupted group copies or crashes during process exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/DARWIN/osi_gcpags.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/DARWIN/osi_groups.c -->
# sources/distributed-fs/openafs/src/afs/DARWIN/osi_groups.c

## Purpose
Implements Darwin PAG placement in process group lists for older kernels and preserves PAGs across `setgroups`. On Darwin 8+ this path is stubbed with `EINVAL`.

## Important APIs, Types, And Functions
`Afs_xsetgroups` wraps native `setgroups` so an existing PAG can be restored. `setpag` inserts or updates the two group slots that encode a PAG. Static helpers `afs_getgroups` and `afs_setgroups` copy and install group arrays into process credentials.

## Control Flow
`Afs_xsetgroups` snapshots the current credential, initializes an AFS request to capture the caller PAG uid, runs native `setgroups`, then if the new credential lacks a PAG and the saved uid is a PAG, calls `AddPag` to restore it. `setpag` generates a PAG if requested, shifts group entries to make room when slots 1 and 2 do not already encode a PAG, writes encoded groups, and installs the credential on the process and optionally its parent.

## State And Persistence
The persistent state is the process credential group list. The file mutates `cr_ngroups`, `cr_groups`, and `proc->p_cred->pc_ucred`, with reference counts around replacement.

## Dependencies And Integration Points
Depends on Darwin credential locking, OpenAFS PAG encoding helpers, native `setgroups`, request initialization, and `AddPag`. It integrates authentication state with Unix group-list semantics.

## Risks
Credential replacement is kernel-version-sensitive and disabled on Darwin 8+ because the older method is not suitable. Group shifting can fail with `E2BIG`. Parent credential changes are potentially surprising and must be explicitly requested. Incorrect refcounting would leak or prematurely free credentials.

## Test Signals
On supported older Darwin builds, test `setpag`, `setgroups` after `klog`, maximum-group handling, parent-changing calls, and PAG preservation after applications modify supplementary groups. Darwin 8+ tests should expect `setpag` failure from this implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/DARWIN/osi_groups.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/DARWIN/osi_inode.c -->
# sources/distributed-fs/openafs/src/afs/DARWIN/osi_inode.c

## Purpose
Resolves host filesystem inodes into vnodes for Darwin cache-file access and stubs unsupported inode syscalls.

## Important APIs, Types, And Functions
`getinode` opens a vnode by device and inode, using `/.vol/<dev>/<inode>` with `vnode_open` on Darwin 8+ or `VFS_VGET`/mount-list search on older kernels. `igetinode` validates type, mode, nlink, and attributes before returning a cache vnode. `iforget` handles older vnode disposal. `afs_syscall_icreate`, `afs_syscall_iopen`, and `afs_syscall_iincdec` return unsupported errors.

## Control Flow
Modern Darwin constructs a `/.vol` path, opens it read/write in the AFS OSI context, validates the vnode type, fetches mode/nlink/size with `vnode_getattr`, rejects unallocated or unlinked entries, and returns the vnode. Older Darwin searches mounted UFS/HFS filesystems if no mount was supplied, calls `VFS_VGET`, validates `v_type`, attributes, and links, then unlocks or releases the vnode as needed.

## State And Persistence
The file does not persist its own data. It relies on host filesystem inode metadata and on global cache mount/device state passed by callers.

## Dependencies And Integration Points
Depends on Darwin vnode, mount, UFS/HFS internals for older kernels, `afs_osi_credp`, `afs_CacheFSType`, and `osi_file.c` cache open paths.

## Risks
The `/.vol` path representation and device/inode formatting must match Darwin behavior. Older mount-list scanning is fragile across filesystem implementations. Returning invalid, unlinked, or wrong-type vnodes would corrupt cache access. The unsupported inode syscalls must remain unreachable or callers must handle `ENOTSUP`/`EOPNOTSUPP`.

## Test Signals
Open valid and deleted cache files by inode, verify bad type/mode/nlink rejection, exercise HFS/UFS older paths if built, and confirm unsupported inode syscalls fail cleanly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/DARWIN/osi_inode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/DARWIN/osi_inode.h -->
# sources/distributed-fs/openafs/src/afs/DARWIN/osi_inode.h

## Purpose
Defines Darwin-specific inode metadata macros used by OpenAFS server/salvager-style inode code and cache compatibility paths.

## Important APIs, Types, And Functions
The header defines `BAD_IGET`, Darwin `VICEMAGIC`, `DI_VICEP3`, `I_VICEP3`, mappings from inode/dinode fields to OpenAFS vice fields, and `IS_*`, `CLEAR_*` magic macros.

## Control Flow
There is no executable control flow. Code includes this header to read, test, or clear OpenAFS magic metadata in UFS-like inode structures.

## State And Persistence
State is persisted in host inode or dinode fields such as flags, generation, uid, gid, and spare slots. The macros encode how OpenAFS overlays vice metadata onto those fields.

## Dependencies And Integration Points
Depends on Darwin inode/dinode layouts used by older cache/server code. It is included by `osi_inode.c` and related cache-file code.

## Risks
The field aliases are only valid for the expected filesystem structure layout. Using them with APFS or incompatible Darwin UFS/HFS internals would read or modify unrelated metadata.

## Test Signals
Builds using legacy inode access should compile against the expected kernel headers. Salvager or cache compatibility tests should verify vice magic detection and clearing on known test inodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/DARWIN/osi_inode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/DARWIN/osi_machdep.h -->
# sources/distributed-fs/openafs/src/afs/DARWIN/osi_machdep.h

## Purpose
Defines the Darwin OS-interface layer that adapts generic OpenAFS kernel code to Darwin process, credential, vnode, VFS, lock, uio, time, and cache APIs.

## Important APIs, Types, And Functions
Important definitions include `vop_cred`, `vop_proc`, `cn_cred`, vnode and VFS compatibility macros, `afs_ucred_t`, `afs_proc_t`, `VN_HOLD`, `VN_RELE`, `gop_rdwr`, `AFS_GLOCK`, `AFS_GUNLOCK`, `ISAFS_GLOCK`, cache filesystem type constants, `osi_curproc`, `osi_curcred`, `afsio_*` wrappers, `IsAfsVnode`, `vSetType`, `osi_procname`, and inline `osi_GetTime`.

## Control Flow
Most entries are macros that change how generic code compiles. Modern Darwin maps credential and vnode operations to KPI functions such as `kauth_cred_*`, `vnode_*`, `vfs_*`, and `ubc_msync`. Global lock macros assert non-recursive ownership by the current thread, acquire/release a Darwin lock, and maintain `afs_global_owner`.

## State And Persistence
The header references global lock state (`afs_global_lock`, `afs_global_owner`), VFS typenum, `afs_osi_ctxtp`, feature toggles (`afs_darwin_realmodes`, `afs_darwin_fsevents`), and cache filesystem identity. It does not allocate state directly.

## Dependencies And Integration Points
This header is pulled in through `afs_osi.h` and is foundational for all Darwin files in this group. It bridges OpenAFS to Darwin KPI, legacy BSD kernel APIs, UBC, and KAUTH credentials.

## Risks
Macro-level ABI adaptation is brittle: wrong version guards can silently compile code against the wrong vnode/credential semantics. The global lock assertions assume no recursive entry. `osi_curcred` maps to `afs_osi_credp`, which is not always the current user credential.

## Test Signals
Successful builds across supported Darwin version macros, lock assertion coverage, vnode type/mount detection, credential ref/unref paths, and mount/root/vnode operations all validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/DARWIN/osi_machdep.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/DARWIN/osi_misc.c -->
# sources/distributed-fs/openafs/src/afs/DARWIN/osi_misc.c

## Purpose
Collects Darwin miscellaneous OS glue: pathname lookup, superuser checks, partial uio copying, reusable VFS context handling, fsevent permission notifications, and the character-device ioctl bridge for modern Darwin.

## Important APIs, Types, And Functions
`darwin_notify_perms` synthesizes permission-change notifications for directory vnodes. `osi_lookupname_user` and `osi_lookupname` resolve paths. `afs_suser` tests superuser privilege. `afsio_partialcopy` builds a bounded duplicate uio. `get_vfs_context` and `put_vfs_context` manage `afs_osi_ctxtp`. `afs_cdev_nop_openclose` and `afs_cdev_ioctl` expose syscall forwarding through `/dev/openafs_ioctl`.

## Control Flow
Permission notification walks the vcache hash under the AFS global lock, skips dead, non-directory, dynroot, mount-point, or reclaiming vnodes, obtains vnode refs, marks `CEvent`, drops the lock, calls `vnode_setattr`, then resumes scanning. Lookup uses `vnode_lookup` with optional no-follow on modern Darwin and `namei` on older kernels. VFS-context acquisition serializes reuse by process/thread and sleeps if another owner is active. The cdev ioctl validates 32/64-bit ioctl command shape, calls `afs3_syscall`, and writes the return value into the user ABI structure.

## State And Persistence
Persistent globals are `afs_osi_ctxtp`, `afs_osi_ctxtp_initialized`, `vfs_context_owner`, `vfs_context_curproc`, and `vfs_context_ref`. `darwin_notify_perms` temporarily mutates vcache `CEvent`.

## Dependencies And Integration Points
Depends on Darwin VFS context, vnode lookup/setattr, proc bitness APIs, devfs cdev registration from `osi_module.c`, OpenAFS vcache hash tables, token events, and syscall dispatcher `afs3_syscall`.

## Risks
The vcache scan releases and reacquires locks while walking mutable lists, so reference discipline is critical. VFS context ownership can deadlock if put/get imbalance occurs. The ioctl ABI must match both 32-bit and 64-bit user structures. Fake fsevents intentionally mask some internal activity and can confuse permission observers if overused.

## Test Signals
Test path lookup with follow/no-follow, cdev syscall forwarding from 32/64-bit tools, token obtain/discard fsevent behavior, concurrent VFS context use, and shutdown with no leaked context references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/DARWIN/osi_misc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/DARWIN/osi_module.c -->
# sources/distributed-fs/openafs/src/afs/DARWIN/osi_module.c

## Purpose
Implements Darwin kext load and unload for OpenAFS, registering the AFS VFS type, vnode operation vectors, syscall or cdev entry points, locks, and devfs node.

## Important APIs, Types, And Functions
`afs_modload` initializes OSI state and registers either `vfs_fsadd` plus `openafs_ioctl` cdev on Darwin 8+ or legacy `vfsconf_add` and syscall table hooks on older kernels. `afs_modunload` unregisters those resources. `KMOD_EXPLICIT_DECL` exposes the kext entry points.

## Control Flow
Modern load initializes mutex infrastructure, creates `afs_global_lock`, registers `afs_vfsentry`, installs cdev switch callbacks, and creates a devfs node. Failures unwind cdev, VFS, mutex, and lock setup. Legacy load registers `afs_vfsconf`, checks syscall availability, and replaces `setgroups` and `AFS_SYSCALL`. Unload refuses while mounted or initialized/shutting down, removes VFS/cdev or restores syscall table entries, and frees locks.

## State And Persistence
Persistent kernel module state includes `afs_vfstable`, cdev major/devfs handle, global lock allocation, legacy `afs_vfsconf`, and modified syscall table entries. The mounted filesystem state `afs_globalVFS` blocks unload.

## Dependencies And Integration Points
Depends on Mach kmod, Darwin VFS registration, devfs/cdev APIs, OpenAFS `osi_Init`, `afs_vfsops`, vnode op descriptors, syscall dispatcher, and group wrapper.

## Risks
Partial load failures must unwind in exact reverse order. Legacy syscall table patching is invasive and must be restored. Unload gating must avoid removing VFS or cdev while active mounts or initialized cache-manager state remain.

## Test Signals
Load/unload kext with no mount, mount then verify unload fails, use `/dev/openafs_ioctl`, verify VFS type appears, and force load-failure paths where cdev or VFS registration is unavailable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/DARWIN/osi_module.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/DARWIN/osi_prototypes.h -->
# sources/distributed-fs/openafs/src/afs/DARWIN/osi_prototypes.h

## Purpose
Declares Darwin-specific OSI support routines used across OpenAFS platform files.

## Important APIs, Types, And Functions
The header declares `darwin_notify_perms`, lookup helpers, `afs_suser`, VFS context get/put, signal-mask helpers, VM helpers, and Darwin vnode creation/finalization helpers.

## Control Flow
There is no executable flow. It provides compile-time contracts between `osi_misc.c`, `osi_sleep.c`, `osi_vm.c`, `osi_vnodeops.c`, and generic OpenAFS code.

## State And Persistence
No state is allocated here; declarations expose routines that manage vcache, vnode, UBC, and VFS-context state elsewhere.

## Dependencies And Integration Points
Depends on Darwin kernel types such as `user_addr_t`, `uio_seg`, `vnode`, `vcache`, and `componentname`. It is the include boundary for Darwin-only helpers.

## Risks
Prototype drift would cause ABI mismatches, especially for `afs_darwin_finalizevnode` and cdev/syscall-adjacent helpers. Conditional availability must match implementation guards.

## Test Signals
Full Darwin builds with warnings enabled are the primary signal; link failures would reveal missing or mismatched support routines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/DARWIN/osi_prototypes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/DARWIN/osi_sleep.c -->
# sources/distributed-fs/openafs/src/afs/DARWIN/osi_sleep.c

## Purpose
Implements Darwin sleep, timed sleep, wakeup, cancellation, and event-hash primitives used by OpenAFS while coordinating with the AFS global lock.

## Important APIs, Types, And Functions
Public routines include `afs_osi_InitWaitHandle`, `afs_osi_CancelWait`, `afs_osi_Wait`, `afs_osi_Sleep`, `afs_osi_SleepSig`, `afs_osi_TimedSleep`, `afs_osi_Wakeup`, `afs_osi_fullSigMask`, `afs_osi_fullSigRestore`, and `shutdown_osisleep`. `afs_getevent` maintains `afs_event_t` records in `afs_evhasht`.

## Control Flow
Wait handles store a process marker and use a shared `waitV` event. Event sleeps hash the event address, increment a refcount, snapshot a sequence number, drop the global lock while blocked on `msleep`, `sleep`, or `tsleep`, and resume when `afs_osi_Wakeup` increments the sequence. Timed sleep converts milliseconds to timespec or ticks and returns interrupt/timeout status. Shutdown walks event buckets and frees zero-refcount events.

## State And Persistence
Persistent state includes `afs_evhasht`, `afs_evhashcnt`, per-event sequence/refcount, and Darwin 8+ per-event mutex/owner fields. Wait handles persist a cancellation marker.

## Dependencies And Integration Points
Depends on Darwin sleep APIs, global lock macros, lock group `openafs_lck_grp`, OpenAFS allocation helpers, and all cache-manager code that waits for daemon, request, or vnode events.

## Risks
The event hash relies on pointer identity and sequence counters; missed wakeups can occur if refcounts or sequences are mishandled. Darwin 8+ event mutex owner assertions are strict. `afs_osi_TimedSleep` maps unchanged sequence to `EINTR`, which callers must interpret correctly. Shutdown can only free events with zero refcount.

## Test Signals
Exercise timed waits, cancelled waits, multi-waiter wakeups, interruptible sleeps, shutdown cleanup, and lock assertions under load. Repeated token, cache, and background daemon activity should not leak event records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/DARWIN/osi_sleep.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/DARWIN/osi_vcache.c -->
# sources/distributed-fs/openafs/src/afs/DARWIN/osi_vcache.c

## Purpose
Provides Darwin vcache allocation, vnode attachment, eviction, and hold helpers for OpenAFS.

## Important APIs, Types, And Functions
`osi_NewVnode`, `osi_PrePopulateVCache`, `osi_AttachVnode`, `osi_PostPopulateVCache`, `osi_TryEvictVCache`, and `osi_vnhold` implement the platform vcache lifecycle.

## Control Flow
Allocation creates a zeroable `struct vcache` and clears `v`. Pre-populate zeros the structure. Attach drops the vcache lock and AFS global lock, calls `afs_darwin_getnewvnode`, reacquires locks, and initializes the per-vcache vnode lock. Post-populate sets mount/type defaults, using `VNON` on modern Darwin until finalization. Eviction recycles vnodes with no visible refs/opens/unlinked-delete state, dropping global locks around `vnode_recycle` or `vgone`.

## State And Persistence
State lives in `vcache->v`, per-vcache `rwlock`, vnode refs/iocounts, `CUnlinkedDel`, and Darwin vnode lifecycle flags such as `CDeadVnode`.

## Dependencies And Integration Points
Depends on `osi_vnodeops.c` for `afs_darwin_getnewvnode`, Darwin vnode recycling APIs, global `afs_xvcache`, and generic OpenAFS vcache allocation/population code.

## Risks
Eviction correctness depends on distinguishing usecounts from iocounts. Dropping and reacquiring locks during vnode allocation/recycle creates races that are mitigated by rechecking `avc->v`. Incorrect initial vnode type can expose incomplete vnodes to VFS.

## Test Signals
Stress vcache creation/reuse/reclaim, lookup races, unlinked file deletion, vnode recycling under memory pressure, and shutdown. Lockdep/assertion failures around `afs_xvcache` are important signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/DARWIN/osi_vcache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/DARWIN/osi_vfsops.c -->
# sources/distributed-fs/openafs/src/afs/DARWIN/osi_vfsops.c

## Purpose
Implements Darwin VFS operations for mounting, unmounting, rooting, statfs/getattr, sysctl, and operation-vector initialization for the OpenAFS filesystem.

## Important APIs, Types, And Functions
Key functions are `afs_mount`, `afs_unmount`, `afs_root`, older `afs_vget`/`afs_vfs_vget`, `afs_statfs`, modern `afs_vfs_getattr`, `afs_sysctl_int`, `afs_sysctl`, `afs_init`, and the exported `afs_vfsops` table. Globals include `afs_globalVp`, `afs_globalVFS`, `afs_vfs_typenum`, `afs_darwin_realmodes`, and `afs_darwin_fsevents`.

## Control Flow
Mount rejects updates/remount conflicts, records `afs_globalVFS`, sets I/O sizing and fsid, fills mount names, optionally resolves a named volume into a root fid stored in mount private data, and marks the VFS auth-opaque on modern Darwin. Root either reuses a cached global root vcache or initializes a request, checks AFS initialization, gets the desired root fid, finalizes the vnode, handles global root replacement races, and returns a vnode reference. Unmount frees mount-private root fids or, for the main mount, requires force to drop the global root, flush vnodes, clear `afs_globalVFS`, and warm-shutdown AFS. Statfs and getattr advertise fake capacity and capabilities. Sysctl exposes Darwin feature toggles.

## State And Persistence
Persistent state is the global mount pointer, cached root vcache, mount-private alternate root fid, VFS typenum, and sysctl feature variables. `afs_globalVp` intentionally holds the root around until unmount.

## Dependencies And Integration Points
Depends on Darwin VFS APIs, OpenAFS volume lookup, cell lookup, root fid handling, vcache acquisition, `afs_darwin_finalizevnode`, sysctl constants, and the vnode operation table from `osi_vnodeops.c`.

## Risks
Only one main AFS mount is supported; remounts return busy. Root vnode races are explicitly retried and can leak refs if mishandled. Named-volume mount private data stores allocated root fids and uses `(qaddr_t)-1` as a sentinel during unmount. Fake capacity/capability reporting must remain compatible with userland expectations.

## Test Signals
Mount `/afs`, mount named volumes, root lookup, statfs/getattr capability queries, sysctl reads/writes for Darwin toggles, forced and non-forced unmount behavior, and vnode flush during shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/DARWIN/osi_vfsops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/DARWIN/osi_vm.c -->
# sources/distributed-fs/openafs/src/afs/DARWIN/osi_vm.c

## Purpose
Implements Darwin UBC/VM cache synchronization primitives for vcache recycling, storeback, invalidation, truncation, and setup.

## Important APIs, Types, And Functions
Exports `osi_VM_FlushVCache`, `osi_VM_StoreAllSegments`, `osi_VM_TryToSmush`, `osi_VM_FlushPages`, `osi_VM_Truncate`, `osi_VM_NukePages`, and `osi_VM_Setup`.

## Control Flow
Flush-vcache purges name cache for the vnode. Store-all drops the vcache lock and global lock, pushes dirty UBC pages with `ubc_msync_range` or `ubc_pushdirty`, then restores locks. Try-to-smush similarly drops locks and invalidates UBC contents. Flush-pages invalidates pages and updates UBC size if the vcache has valid stat data. Truncate sets UBC size to the new length. Setup initializes UBC info and size on older Darwin when the vnode is valid and stat data is available.

## State And Persistence
State is the vnode UBC object and size, dirty page state, name cache entries, and vcache length/stat bits. `osi_VM_NukePages` is intentionally empty.

## Dependencies And Integration Points
Depends on Darwin UBC APIs, vnode cache purge, global lock choreography, and generic OpenAFS callbacks that revoke callbacks, truncate files, store dirty segments, or recycle vcaches.

## Risks
Dropping locks around UBC calls allows concurrent page creation, as comments note. Size synchronization depends on `CStatd` and may be stale when stat data is invalid. Modern and older UBC APIs differ significantly. Empty `osi_VM_NukePages` means callers must tolerate no targeted invalidation.

## Test Signals
Read/write through mapped and unmapped paths, callback revocation, `fs flush`, truncation, dirty storeback on close/fsync, and vcache recycling should show correct file contents and no stale UBC pages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/DARWIN/osi_vm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/DARWIN/osi_vnodeops.c -->
# sources/distributed-fs/openafs/src/afs/DARWIN/osi_vnodeops.c

## Purpose
This is the Darwin vnode operation layer for OpenAFS. It maps Darwin VNOP/VOP callbacks to common OpenAFS file, directory, VM, lock, ioctl, and vnode-lifecycle operations, and provides special modern-Darwin handling for incomplete/dead vnodes and vnode finalization.

## Important APIs, Types, And Functions
The file exports `afs_vnodeop_entries`, `afs_vnodeop_opv_desc`, modern `afs_dead_vnodeop_entries`, and handlers for lookup, create, open, close, access, getattr, setattr, read/write, pagein/pageout, ioctl, select, mmap, fsync, remove, link, rename, mkdir/rmdir, symlink, readdir, readlink, inactive, reclaim, pathconf, advlock, block/offset conversion, and older lock/bmap/strategy/print/cmap support. `darwin_vn_hold`, `afs_darwin_getnewvnode`, and `afs_darwin_finalizevnode` manage vnode references and replacement.

## Control Flow
Vnode operations usually extract component names, acquire the AFS global lock, call the corresponding `afs_*` routine, release the lock, and repair Darwin vnode/name-cache state. Lookup uses `cache_lookup` on modern Darwin, filters internal fsevent contexts, handles create/rename `EJUSTRETURN`, and finalizes returned vcaches into real vnodes. Open calls `afs_open` and flushes pages; close calls `afs_close` and forces trace/error processing. Access maps KAUTH actions to AFS ACL bits, includes fakestat/dropbox special cases, and returns Darwin errno semantics. Pagein maps the UPL, builds a kernel uio, reads via `afs_read`, zero-fills short reads, and commits or aborts the UPL. Pageout validates bounds, maps the UPL, fake-opens the vcache, writes via `afs_write`, fake-closes it, and commits/aborts. Rename includes a modern cross-volume fallback through a background `BOP_MOVE`.

## State And Persistence
State spans vnode op vectors, dead-vnode op vectors, vnode fsnode pointers, vcache state bits (`CMAPPED`, `CEvent`, `CUnlinked`, `CVInit`, `CDeadVnode`), UBC size/page state, name cache entries, fake dirty/shadow vnode refs during finalization, and vcache hash/reclaim lists. Modern finalization replaces a temporary VNON dead vnode with a correctly typed vnode.

## Dependencies And Integration Points
Depends on Darwin VFS/VNOP, UPL/UBC, KAUTH, name cache, OpenAFS common operations, fakestat, background request queue, vcache lifecycle locks, and `osi_vfsops.c` mount state. It is the main Darwin syscall-facing integration point.

## Risks
Reference and lock ordering is the dominant risk: vnode iocounts/usecounts, AFS global lock, vcache locks, name-cache state, and UPL commit/abort must stay balanced. Dead-vnode finalization can race reclaim and must not touch a freed vcache after failure. Access semantics intentionally include Finder/dropbox/fsevents compatibility exceptions. Pageout must not extend files and must zero partial EOF pages. Rename cross-volume fallback depends on background daemon completion.

## Test Signals
Run full filesystem syscall coverage on Darwin: lookup/create/open/read/write/close, Finder resource-fork behavior, KAUTH access checks, pagein/pageout under memory pressure, remove/recycle unlinked files, rename including cross-volume mount-point fallback, readdir cookies/flags, advisory locks, reclaim under vcache pressure, and kext unload after all vnodes are gone.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/DARWIN/osi_vnodeops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/DFBSD/osi_gcpags.c -->
# sources/distributed-fs/openafs/src/afs/DFBSD/osi_gcpags.c

## Purpose
Provides DragonFly BSD PAG garbage-collection credential access when `AFS_GCPAGS` is enabled.

## Important APIs, Types, And Functions
`afs_osi_proc2cred(afs_proc_t *pr)` returns `pr->p_cred` for a process, or `NULL` for a null process pointer.

## Control Flow
The function performs a null check and directly exposes the process credential pointer; there is no process traversal implementation in this file.

## State And Persistence
No local state is stored. Returned credential state belongs to the process.

## Dependencies And Integration Points
Depends on DragonFly process credential layout and OpenAFS PAG scanner code that consumes process credentials.

## Risks
Returning a live credential pointer means lifetime and locking must be valid in the caller. Unlike Darwin/FreeBSD snapshots, this path does not copy credentials or filter process states.

## Test Signals
Enable PAG GC and verify process credentials can be inspected without crashes during token cleanup, including process-exit races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/DFBSD/osi_gcpags.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/DFBSD/osi_inode.h -->
# sources/distributed-fs/openafs/src/afs/DFBSD/osi_inode.h

## Purpose
This file is an intentionally empty DragonFly BSD inode-compatibility header in this source snapshot.

## Important APIs, Types, And Functions
It declares no macros, types, or functions.

## Control Flow
There is no executable control flow.

## State And Persistence
No state is defined.

## Dependencies And Integration Points
Its presence satisfies include paths that expect a platform `osi_inode.h` for every BSD variant.

## Risks
Any code that expects DragonFly-specific inode macros from this header would fail to compile. The empty file implies either the platform does not support those inode operations or definitions come from elsewhere.

## Test Signals
DragonFly BSD builds are the primary signal. Include-only compilation should succeed for code paths that do not require inode metadata macros.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/DFBSD/osi_inode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/DFBSD/osi_machdep.h -->
# sources/distributed-fs/openafs/src/afs/DFBSD/osi_machdep.h

## Purpose
Defines the minimal DragonFly BSD OSI machine-dependent time helper for OpenAFS.

## Important APIs, Types, And Functions
The header provides inline `osi_GetTime(osi_timeval32_t *atv)`, which calls `microtime` and copies seconds and microseconds.

## Control Flow
Callers pass an output timeval; the inline helper fetches current kernel time and assigns fields.

## State And Persistence
No local state is maintained.

## Dependencies And Integration Points
Depends on DragonFly `microtime` and OpenAFS `osi_timeval32_t`. It is included through `afs_osi.h`.

## Risks
Only time retrieval is defined here; other platform macros must be defined by common BSD headers or elsewhere. Time truncation into 32-bit fields may matter on long-lived systems.

## Test Signals
DragonFly builds and runtime timestamping in cache manager events should validate the helper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/DFBSD/osi_machdep.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/DFBSD/osi_prototypes.h -->
# sources/distributed-fs/openafs/src/afs/DFBSD/osi_prototypes.h

## Purpose
Provides the DragonFly BSD platform prototypes include guard for OpenAFS.

## Important APIs, Types, And Functions
No routines are declared in this snapshot.

## Control Flow
There is no executable flow.

## State And Persistence
No state is defined.

## Dependencies And Integration Points
The header is an include boundary for platform-specific helpers, even though this platform currently exposes none here.

## Risks
Missing prototypes can hide implicit-declaration problems if DragonFly-specific support functions are later added without updating this header.

## Test Signals
Compiler warnings and full DragonFly builds are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/DFBSD/osi_prototypes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/FBSD/opt_posix.h -->
# sources/distributed-fs/openafs/src/afs/FBSD/opt_posix.h

## Purpose
Defines FreeBSD POSIX option macros needed by OpenAFS kernel compilation.

## Important APIs, Types, And Functions
The file defines `P1003_1B` and `_KPOSIX_PRIORITY_SCHEDULING` to `1`.

## Control Flow
There is no runtime flow.

## State And Persistence
No state is stored.

## Dependencies And Integration Points
Included by FreeBSD kernel code expecting POSIX scheduling feature macros.

## Risks
Hard-coded feature macros may not match all target FreeBSD kernels, but they preserve compatibility with code that conditionally compiles POSIX scheduling support.

## Test Signals
Successful FreeBSD builds are the signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/FBSD/opt_posix.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/FBSD/osi_crypto.c -->
# sources/distributed-fs/openafs/src/afs/FBSD/osi_crypto.c

## Purpose
Provides the FreeBSD implementation of OpenAFS random-byte acquisition.

## Important APIs, Types, And Functions
`osi_readRandom(void *data, afs_size_t len)` calls FreeBSD `read_random(data, len)` and returns zero.

## Control Flow
The function delegates directly to the kernel random subsystem and reports success unconditionally.

## State And Persistence
No local state is kept; entropy state is kernel-owned.

## Dependencies And Integration Points
Depends on `<sys/random.h>` and supports generic OpenAFS code needing random bytes.

## Risks
No error or short-read handling is surfaced. Callers must provide valid kernel buffers.

## Test Signals
Build and runtime calls that require random data should complete and receive non-deterministic contents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/FBSD/osi_crypto.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/FBSD/osi_file.c -->
# sources/distributed-fs/openafs/src/afs/FBSD/osi_file.c

## Purpose
Implements FreeBSD cache-file I/O for OpenAFS, including opening cache vnodes by inode, stat/read/write/truncate operations, atime suppression, and shutdown reset.

## Important APIs, Types, And Functions
Exports `osi_UFSOpen`, `afs_osi_Stat`, `osi_UFSClose`, `osi_UFSTruncate`, `osi_DisableAtimes`, `afs_osi_Read`, `afs_osi_Write`, `afs_osi_MapStrategy`, and `shutdown_osifile`.

## Control Flow
`osi_UFSOpen` validates UFS cache mode, allocates `osi_file`, drops the AFS global lock, calls `VFS_VGET`, rejects `VNON`, unlocks the vnode, and records size/offset. Stat and truncate lock the cache vnode around `VOP_GETATTR`/`VOP_SETATTR`. Read/write set the offset, drop the global lock around `gop_rdwr`, convert residuals to bytes transferred, update the offset, and trace negative errors. MapStrategy simply invokes the supplied strategy routine.

## State And Persistence
Global state includes `afs_osicred_initialized`, `cacheDev`, and `afs_cacheVfsp`. Per-open state is the `osi_file` vnode, size, offset, and completion callback. The host UFS file persists cached data.

## Dependencies And Integration Points
Depends on FreeBSD vnode, UFS inode, `vn_rdwr` through `gop_rdwr`, OpenAFS global lock, cache manager `osi_file` contract, and FreeBSD credential `afs_osi_credp`.

## Risks
The code assumes UFS inode internals (`VTOI(vp)->i_size`, `IN_ACCESS`). Lock dropping around vnode I/O must be balanced. Reads during shutdown return `-EIO` instead of panicking, but other null write paths panic. Version-dependent residual type matters.

## Test Signals
Open cache files, read/write data and offsets, truncate only when shrinking, stat metadata, suppress atime changes, invoke write callbacks, and run warm/cold shutdown without credential-state corruption.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/FBSD/osi_file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/FBSD/osi_gcpags.c -->
# sources/distributed-fs/openafs/src/afs/FBSD/osi_gcpags.c

## Purpose
Implements FreeBSD process traversal and credential snapshotting for OpenAFS PAG garbage collection.

## Important APIs, Types, And Functions
`afs_osi_TraverseProcTable` walks `allproc` and calls `afs_GCPAGs_perproc_func`. `afs_osi_proc2cred` copies uid and groups from a live process credential into a static `afs_ucred_t`.

## Control Flow
Traversal skips embryonic, zombie, and system processes. Credential conversion accepts sleeping, running, and stopped processes, locks credentials for reading, copies uid/group fields, unlocks, and returns the static copy.

## State And Persistence
No durable state is stored. The static credential copy is overwritten on each call.

## Dependencies And Integration Points
Depends on FreeBSD process lists, `pcred_readlock`, OpenAFS group/PAG encoding, and the PAG GC scanner.

## Risks
Static returned credentials are not reentrant. Process state can change while scanning. The implementation copies only uid/groups, so callers needing richer credential fields cannot rely on it.

## Test Signals
Token/PAG GC with many process states, concurrent process exit, and repeated credential scans should reclaim stale PAGs without crashes or corrupted group lists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/FBSD/osi_gcpags.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/FBSD/osi_groups.c -->
# sources/distributed-fs/openafs/src/afs/FBSD/osi_groups.c

## Purpose
Provides FreeBSD PAG preservation around `setgroups` and a partial `setpag` implementation for encoding PAGs in supplementary groups.

## Important APIs, Types, And Functions
`Afs_xsetgroups` wraps `sys_setgroups`. `setpag` generates/inserts a PAG group pair. Static `afs_getgroups` copies group arrays, while `afs_setgroups` is currently a stub returning zero.

## Control Flow
`Afs_xsetgroups` duplicates the thread credential, initializes an AFS request to capture existing PAG identity, invokes native `sys_setgroups`, then if the new credential lacks a PAG and the saved uid encodes one, calls `AddPag`. `setpag` allocates a group buffer sized by `ngroups_max + 1`, shifts existing groups to create slots 1 and 2 if needed, writes encoded PAG groups, and calls the stubbed `afs_setgroups`.

## State And Persistence
Intended persistent state is the thread credential group list, but this file's `afs_setgroups` stub does not install the modified groups. Temporary group arrays are allocated with `osi_Alloc`.

## Dependencies And Integration Points
Depends on FreeBSD thread/sysproto `setgroups`, OpenAFS PAG helpers, credential duplication, and `AddPag`.

## Risks
The `setpag` path appears incomplete because `afs_setgroups` returns success without mutating credentials. This can make PAG creation appear successful while not changing process groups, depending on how `AddPag` is implemented for FreeBSD. Group buffer sizing and slot assumptions also require care.

## Test Signals
Explicitly test `setpag` result by checking `PagInCred` after the call, not just return code. Also test `setgroups` after PAG creation, maximum group counts, and failure cleanup of allocated group buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/FBSD/osi_groups.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/FBSD/osi_inode.c -->
# sources/distributed-fs/openafs/src/afs/FBSD/osi_inode.c

## Purpose
Resolves FreeBSD UFS inode numbers into kernel inode/vnode objects for cache-file access and stubs unsupported inode syscalls.

## Important APIs, Types, And Functions
`getinode` locates a mounted UFS filesystem and calls `VFS_VGET`. `igetinode` validates allocated regular inodes. `afs_syscall_icreate`, `afs_syscall_iopen`, and `afs_syscall_iincdec` return `EOPNOTSUPP`.

## Control Flow
If no mount is supplied, `getinode` scans the mount list under `mountlist_mtx` for a UFS mount matching the device, then calls `VFS_VGET`. `igetinode` rejects zero-mode, zero-link, or non-regular inodes, releasing the vnode on failure and returning the inode pointer on success.

## State And Persistence
No local persistent state. It observes host UFS inode fields such as `i_mode` and `i_nlink`.

## Dependencies And Integration Points
Depends on FreeBSD UFS structures, mount list locking, cdev device identity, and cache-file code that needs inode-to-vnode conversion.

## Risks
The implementation is tied to UFS internals and does not support non-UFS cache filesystems. Mount-list iteration and `VFS_VGET` signatures vary across FreeBSD versions. Unsupported inode syscalls must not be required by modern callers.

## Test Signals
Open valid and invalid cache inodes, deleted inodes, non-regular files, and absent devices. Build against target FreeBSD UFS headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/FBSD/osi_inode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/FBSD/osi_inode.h -->
# sources/distributed-fs/openafs/src/afs/FBSD/osi_inode.h

## Purpose
Defines FreeBSD UFS inode/dinode field mappings used to store and inspect OpenAFS vice metadata.

## Important APIs, Types, And Functions
The header defines `BAD_IGET`, FreeBSD `VICEMAGIC`, `DI_VICEP3`, `I_VICE3`, fake inode sizing, mount-list lock macros, aliases for inode and dinode vice fields, inode-number block/cylinder macros (`itoo`, `itog`, `itod`), and magic test/clear macros.

## Control Flow
There is no runtime flow; it is a macro contract.

## State And Persistence
Persistent state is encoded in UFS inode/dinode fields such as spare words, uid/gid, and old id fields. The macros define OpenAFS interpretation of that metadata.

## Dependencies And Integration Points
Depends on FreeBSD UFS `struct inode`, `struct dinode`, filesystem geometry macros, and legacy server/salvager cache code.

## Risks
UFS layout changes or non-UFS cache filesystems invalidate these aliases. Several fields are repurposed from spare or old-id slots, so collisions with filesystem changes are possible.

## Test Signals
Builds against target FreeBSD UFS headers and salvager/cache tests that set, detect, and clear vice magic on controlled inodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/FBSD/osi_inode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/FBSD/osi_machdep.h -->
# sources/distributed-fs/openafs/src/afs/FBSD/osi_machdep.h

## Purpose
Defines the FreeBSD OSI machine-dependent adaptation layer for OpenAFS, including vnode/VFS macros, global locking, credentials, privileges, memory allocation hooks, and time helpers.

## Important APIs, Types, And Functions
Key definitions include `osi_Time`, `afs_hz`, `afs_ucred_t`, `afs_proc_t`, vnode type helpers, `IsAfsVnode`, `osi_vinvalbuf`, lookup macro redirects, `afs_osi_Alloc_NoSleep`, `VN_RELE`, `VN_HOLD`, FreeBSD privilege wrappers for `afs_suser`, process/credential macros, `gop_rdwr`, `AFS_GLOCK`, `AFS_GUNLOCK`, `ISAFS_GLOCK`, `osi_InitGlock`, `osi_procname`, and inline `osi_GetTime`.

## Control Flow
The global lock macros assert mutex ownership/non-ownership and lock or unlock `afs_global_mtx`. Privilege macros call `priv_check` for OpenAFS admin and daemon privileges. `osi_GetTime` fetches `microtime`.

## State And Persistence
References persistent globals `afs_global_mtx`, `afs_global_owner`, and pbuf accounting/UMA state. It does not allocate state directly.

## Dependencies And Integration Points
Included via `afs_osi.h` by FreeBSD platform and generic OpenAFS code. Depends on FreeBSD vnode, mutex, privilege, time, thread, and buffer APIs.

## Risks
Macro adaptation must track FreeBSD API changes. `afs_suser` requires both configured privileges, so privilege policy changes affect admin operations. Global-lock assertions are non-recursive and will panic on incorrect nesting.

## Test Signals
Full FreeBSD builds, privilege checks for admin/daemon operations, lock assertion tests, vnode operation dispatch, and cache I/O through `gop_rdwr`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/FBSD/osi_machdep.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/FBSD/osi_misc.c -->
# sources/distributed-fs/openafs/src/afs/FBSD/osi_misc.c

## Purpose
Provides FreeBSD miscellaneous helpers for path lookup, kernel allocation, freeing, and vcache in-use checks.

## Important APIs, Types, And Functions
Exports `osi_lookupname`, `osi_fbsd_alloc`, `osi_fbsd_free`, and `osi_fbsd_checkinuse`.

## Control Flow
`osi_lookupname` drops the AFS global lock if held, builds a FreeBSD `nameidata` lookup with follow/no-follow flags, calls `namei`, returns the vnode, frees pathname buffers, and restores the global lock. Allocation optionally drops the global lock for blocking `malloc(M_WAITOK)` or uses nonblocking `M_NOWAIT`. `osi_fbsd_checkinuse` requires the vnode interlock, rejects vcaches with vnode usecount, opens, or held AFS locks.

## State And Persistence
No local persistent state; allocations use the `M_AFS` malloc type defined in `osi_module.c`. The in-use check observes vnode and vcache state.

## Dependencies And Integration Points
Depends on FreeBSD `namei`, malloc, vnode interlocks, OpenAFS global lock, and vcache recycling code in `osi_vcache.c`/`osi_vm.c`.

## Risks
Path lookup returns a referenced vnode and relies on callers to release it. Dropping the global lock around namei/allocation opens races that callers must tolerate. `osi_fbsd_checkinuse` enforces strict recycling conditions; stale `opens` counts can prevent reclamation.

## Test Signals
Lookup existing/missing paths with both follow modes, allocation under memory pressure, vcache recycle checks with active refs/opens/locks, and lock assertion coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/FBSD/osi_misc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/FBSD/osi_module.c -->
# sources/distributed-fs/openafs/src/afs/FBSD/osi_module.c

## Purpose
Registers the FreeBSD AFS filesystem module and defines the OpenAFS malloc type.

## Important APIs, Types, And Functions
`MALLOC_DEFINE(M_AFS, "afsmisc", ...)` defines the allocation bucket. `VFS_SET(afs_vfsops, afs, VFCF_NETWORK)` registers the VFS module using the `afs_vfsops` table.

## Control Flow
There is no explicit load/unload function here; FreeBSD module registration is declarative through `VFS_SET`.

## State And Persistence
Persistent kernel module state is managed by the FreeBSD VFS module framework and the `M_AFS` allocator statistics.

## Dependencies And Integration Points
Depends on `afs_vfsops` from `osi_vfsops.c`, FreeBSD module/VFS macros, and allocation users in `osi_misc.c`.

## Risks
Registration correctness depends on `afs_vfsops` and module metadata matching FreeBSD expectations. The module is marked `VFCF_NETWORK`, affecting mount semantics.

## Test Signals
Kernel module load should expose the `afs` VFS type, allocation statistics should use `afsmisc`, and mount should dispatch into `afs_vfsops`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/FBSD/osi_module.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/FBSD/osi_prototypes.h -->
# sources/distributed-fs/openafs/src/afs/FBSD/osi_prototypes.h

## Purpose
Declares FreeBSD-specific OSI helper routines used outside their implementation files.

## Important APIs, Types, And Functions
Declares `osi_lookupname`, `osi_fbsd_alloc`, `osi_fbsd_free`, and `osi_fbsd_checkinuse`.

## Control Flow
There is no executable flow.

## State And Persistence
No state is declared directly; prototypes expose helpers that interact with vnode, allocation, and vcache state.

## Dependencies And Integration Points
Depends on FreeBSD `uio_seg`, `vnode`, `size_t`, and OpenAFS `vcache` types. Included by generic/platform code requiring these helpers.

## Risks
Prototype mismatch would break path lookup, memory allocation, or vcache eviction integration.

## Test Signals
FreeBSD builds with warnings enabled should show no implicit declarations or incompatible pointer warnings for these helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/FBSD/osi_prototypes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/FBSD/osi_sleep.c -->
# sources/distributed-fs/openafs/src/afs/FBSD/osi_sleep.c

## Purpose
Implements FreeBSD wait-handle, event sleep, timed sleep, and wakeup primitives for OpenAFS.

## Important APIs, Types, And Functions
Exports `afs_osi_InitWaitHandle`, `afs_osi_CancelWait`, `afs_osi_Wait`, `afs_osi_Sleep`, `afs_osi_SleepSig`, `afs_osi_TimedSleep`, and `afs_osi_Wakeup`. Static `afs_getevent` maintains event records in `afs_evhasht`.

## Control Flow
Wait handles use FreeBSD condition variables under `afs_global_mtx`; waits convert milliseconds to ticks and call `cv_timedwait` or `cv_timedwait_sig`. Address-based event sleeps hash the event pointer, snapshot a sequence, and sleep on the address with `msleep` until `afs_osi_Wakeup` increments the sequence and calls `wakeup`.

## State And Persistence
Persistent state includes per-wait-handle condition variables and initialization flags, global event hash `afs_evhasht`, per-event sequence/refcount, and `afs_evhashcnt`.

## Dependencies And Integration Points
Depends on FreeBSD `cv_*`, `msleep`, `wakeup`, `tvtohz`, `afs_global_mtx`, and generic OpenAFS daemon/request wait code.

## Risks
Wait handles are lazily initialized in some paths, noted as questionable by comments. Event records are allocated no-sleep and are not freed here. Return codes from `cv_timedwait`/`msleep` must be interpreted consistently by callers.

## Test Signals
Exercise timed waits, interruptible waits, cancel waits, event wakeups with multiple waiters, and long-running daemon workloads for event-hash growth or missed wakeups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/FBSD/osi_sleep.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/FBSD/osi_vcache.c -->
# sources/distributed-fs/openafs/src/afs/FBSD/osi_vcache.c

## Purpose
Implements FreeBSD vcache allocation, vnode attachment, eviction, post-population, and safe vnode holds for OpenAFS.

## Important APIs, Types, And Functions
Exports `osi_TryEvictVCache`, `osi_NewVnode`, `osi_PrePopulateVCache`, `osi_AttachVnode`, `osi_PostPopulateVCache`, and version-dependent `osi_vnhold`.

## Control Flow
Eviction tries to lock the vnode interlock, checks in-use state, skips doomed vnodes as already evicted, holds the vnode, drops AFS locks, attempts nonblocking exclusive `vn_lock`, calls `vrecycle`, unlocks/drops, then restores AFS locks. Attach drops AFS locks, calls `getnewvnode`, inserts into the mount queue if needed, restores locks, handles rare races where another thread already attached a vnode, assigns `v_data`, and initializes the vcache lock.

## State And Persistence
State lives in `vcache->v`, vnode `v_data`, vnode mount queue membership, per-vcache `rwlock`, and vnode hold/reference counts.

## Dependencies And Integration Points
Depends on FreeBSD vnode lifecycle APIs, `afs_globalVFS`, `afs_vnodeops`, `osi_fbsd_checkinuse`, `afs_xvcache`, and generic OpenAFS vcache management.

## Risks
Reference and interlock ordering around `vrecycle` is delicate. `osi_AttachVnode` documents a possible race if `avc->v` becomes non-null while locks were dropped. Version-specific `vref`/`vrefl` handling must avoid holding doomed vnodes.

## Test Signals
Stress vcache creation and reclamation under memory pressure, vnode recycle races, mount queue insertion, `AFS_IS_DOOMED` paths, and `osi_vnhold` on active and doomed vnodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/FBSD/osi_vcache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/FBSD/osi_vfsops.c -->
# sources/distributed-fs/openafs/src/afs/FBSD/osi_vfsops.c

## Purpose
Implements FreeBSD VFS operations for OpenAFS: module init/uninit, mount, cmount, unmount, root, statfs, sync, syscall registration, and pbuf pool setup.

## Important APIs, Types, And Functions
Key functions are `afs_init`, `afs_uninit`, `afs_statfs`, `afs_omount`, `afs_mount`, `afs_cmount`, `afs_unmount`, `afs_root`, `afs_sync`, and the exported `struct vfsops afs_vfsops`. Globals include `afs_globalVp`, `afs_globalVFS`, `afs_pbuf_zone` or `afs_pbuf_freecnt`, and the `afs_syscalls` helper table.

## Control Flow
Initialization registers `AFS_SYSCALL`, calls `osi_Init`, and creates pbuf resources. Mount rejects updates and existing global mounts, records `afs_globalVFS`, sets block size/fsid/mount names, marks the mount non-local/MPSAFE as needed, and fills statfs. Root duplicates the current credential, obtains or reuses `afs_globalVp`, handles races while replacing the global root, drops the global lock around `vget`, revalidates the global root after lock reacquisition, marks `VV_ROOT`, and returns the vnode. Unmount drops the root vcache if forced or unreferenced, flushes remaining vnodes, clears `afs_globalVFS`, and performs warm shutdown.

## State And Persistence
Persistent state includes the singleton global mount, cached root vcache, registered syscall helper, pbuf resources, and fake statfs values. Root vnode references intentionally persist until unmount.

## Dependencies And Integration Points
Depends on FreeBSD VFS/module/syscall helper APIs, OpenAFS initialization/shutdown, root fid lookup, vcache/vnode lifecycle, pbuf allocation used by vnode operations, and `osi_module.c` registration.

## Risks
Singleton mount assumptions reject multiple mounts. Root acquisition deliberately drops locks and must revalidate to avoid races. Uninit must refuse while mounted. Version guards around `vget`, syscall helper registration, and pbuf allocation are ABI-sensitive.

## Test Signals
Module load/unload, syscall registration conflict, mount/remount rejection, root lookup races, statfs contents, forced and normal unmount, warm shutdown, and pbuf resource cleanup should all be exercised.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/FBSD/osi_vfsops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/FBSD/osi_vm.c -->
# sources/distributed-fs/openafs/src/afs/FBSD/osi_vm.c

## Purpose
Implements FreeBSD VM and buffer-cache synchronization for OpenAFS vcaches, including page cleaning, invalidation, callback flush, truncation, and vcache recycle checks.

## Important APIs, Types, And Functions
Exports `osi_VM_FlushVCache`, `osi_VM_StoreAllSegments`, `osi_VM_TryToSmush`, `osi_VM_FlushPages`, and `osi_VM_Truncate`. Helpers/macros wrap vnode locking and version-specific VM object write locks and dirty checks.

## Control Flow
Flush-vcache locks the vnode interlock, calls `osi_fbsd_checkinuse`, holds the vnode, drops the global lock, purges name cache, restores locks, and drops the hold. Store-all asserts the vnode is locked, checks `v_object` dirty state, drops the vcache/global locks, write-locks the VM object, synchronously cleans pages, then restores locks. Try-to-smush rejects doomed vnodes, ensures an exclusive vnode lock, cleans VM pages, retries `vinvalbuf(V_SAVE)` up to five times, restores prior lock state, and reacquires the global lock. Flush-pages removes VM pages and invalidates buffers. Truncate calls `vnode_pager_setsize`.

## State And Persistence
State includes vnode `v_object`/`v_bufobj.bo_object`, dirty page flags, buffer cache contents, vnode interlock/lock state, vcache locks, and vnode pager size.

## Dependencies And Integration Points
Depends on FreeBSD VM object APIs, vnode/buffer invalidation, `osi_fbsd_checkinuse`, OpenAFS callback invalidation, file storeback, truncation, and vcache recycling paths.

## Risks
The file comments emphasize FreeBSD vnode/VM locking protocol drift. Calling with someone else's exclusive lock panics in smush. `OBJPC_SYNC` choices trade correctness/performance. `osi_VM_FlushPages` asserts the vnode is locked and will fail if generic callers violate that contract.

## Test Signals
Dirty mmap/writeback, callback revocation, `fs flush`, truncation, vnode recycle under cache pressure, concurrent page faults, and FreeBSD-version builds should validate this file. Watch for `TryToSmush retrying vinvalbuf` warnings and lock assertion failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/FBSD/osi_vm.c -->
