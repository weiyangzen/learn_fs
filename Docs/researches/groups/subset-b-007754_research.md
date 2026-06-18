# subset-b-007754 Research

Grouped research for OpenAFS UKERNEL support and selected VNOPS files. Each section preserves the source path in the title and is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/UKERNEL/afs_usrops.c -->
# sources/distributed-fs/openafs/src/afs/UKERNEL/afs_usrops.c

## Purpose

`afs_usrops.c` is the core `UKERNEL` user-space glue for libuafs. It emulates enough kernel process, vnode, credential, sleep, VFS, and file descriptor behavior for the OpenAFS cache manager and vnode operations to run inside a pthread-based process instead of a real kernel. It also exposes the public `uafs_*` API surface that presents POSIX-like operations on the AFS tree.

## Important APIs, Types, and Functions

- Global state: `afs_FileTable[MAX_OSI_FILES]`, `afs_FileFlags`, and `afs_FileOffsets` implement the libuafs file descriptor table; `afs_RootVfs`, `afs_RootVnode`, and `afs_CurrentDir` model mounted filesystem state; `afs_mountDir` and `afs_mountDirLen` define the accepted absolute AFS mount prefix; `afs_global_u_key`, `afs_global_procp`, and `afs_global_ucredp` emulate per-thread `u`.
- Locking state: `afs_global_lock`/`afs_global_owner` implement the AFS global lock, `rx_global_lock` mirrors RX locking, and `osi_waitq_lock` protects the wait hash and timed wait lists.
- Initialization and lifecycle: `osi_Init`, `uafs_Setup`, `uafs_ParseArgs`, `uafs_Run`, `uafs_mount`, `uafs_setMountDir`, `uafs_Shutdown`, `uafs_Init`, and `uafs_RxServerProc`.
- Kernel emulation helpers: `usr_uiomove`, `usr_crcopy`, `usr_crget`, `usr_crfree`, `usr_crhold`, `usr_vattr_null`, `uafs_InitThread`, `get_user_struct`, `afs_osi_Sleep`, `afs_osi_Wakeup`, `afs_osi_Wait`, `afs_osi_CheckTimedWaits`, and `lookupname`.
- Cache-file OSI helpers: `osi_UFSOpen`, `osi_UFSClose`, `osi_UFSTruncate`, `afs_osi_Read`, `afs_osi_Write`, `afs_osi_Stat`, `afs_osi_VOP_RDWR`, `afs_osi_Alloc`, `afs_osi_Free`, `osi_AllocLargeSpace`, and `osi_AllocSmallSpace`.
- Path and syscall helpers: `call_syscall`, `fork_syscall`, `uafs_LookupName`, `uafs_LookupLink`, `uafs_LookupParent`, `uafs_LastPath`, `uafs_IsRoot`, and `uafs_afsPathName`.
- Public filesystem operations: `uafs_chdir`, `uafs_mkdir`, `uafs_open`, `uafs_creat`, `uafs_read`, `uafs_pread`, `uafs_pread_nocache`, `uafs_write`, `uafs_pwrite`, `uafs_stat`, `uafs_lstat`, `uafs_fstat`, `uafs_chmod`, `uafs_fchmod`, `uafs_truncate`, `uafs_ftruncate`, `uafs_lseek`, `uafs_fsync`, `uafs_close`, `uafs_link`, `uafs_symlink`, `uafs_readlink`, `uafs_unlink`, `uafs_rename`, `uafs_rmdir`, `uafs_opendir`, `uafs_readdir`, `uafs_getdents`, and `uafs_closedir`.
- PIOCTL/auth/stat APIs: `uafs_SetTokens`, RPC stats enable/disable/clear calls, `uafs_FlushFile`, `uafs_unlog`, `uafs_getcellstatus`, `uafs_getvolquota`, `uafs_setvolquota`, `uafs_statmountpoint`, `uafs_access`, and `uafs_getRights`.

## Control Flow

Initialization begins with `uafs_Setup`, which normalizes the mount directory through `calcMountDir`, calls `osi_Init`, and initializes the afsd cache manager through `afsd_init`. `uafs_ParseArgs` and `uafs_Run` delegate to afsd parsing and runtime startup. `uafs_mount` mounts `afs_RootVfs`, obtains the root vnode with `afs_root`, and sets `afs_CurrentDir`.

Every non-`_r` public filesystem wrapper takes `AFS_GLOCK`, calls the corresponding `_r` implementation, and releases the global lock. The `_r` forms assume the caller has already serialized access. File operations resolve paths with `uafs_LookupName` or `uafs_LookupParent`, call underlying VNOPS such as `afs_create`, `afs_read`, `afs_write`, `afs_getattr`, `afs_setattr`, `afs_remove`, `afs_rename`, or `afs_readdir`, translate OpenAFS errors into `errno`, and manage vnode references with `VN_HOLD`/`VN_RELE`.

`uafs_LookupName` first distinguishes relative paths from absolute paths under the configured mount point. It walks path components, checks directory execute permission through `afs_access`, calls `afs_lookup`, and optionally follows symlinks with a `MAX_OSI_LINKS` loop guard. `uafs_LookupLinkPath` reads a link with `afs_readlink`, detects simple self-loops when a comparison path is provided, and recurses into `uafs_LookupName`.

Open state is stored in the static descriptor arrays. `uafs_open_r` handles `O_CREAT`, `O_EXCL`, `O_TRUNC`, `O_APPEND`, and access checks, calls `afs_open`, and records vnode/flags/offset in the first free slot. Reads and writes build single-element `usr_uio` vectors and update `afs_FileOffsets[fd]` from `uio_offset`.

Sleep/wakeup emulation hashes arbitrary event addresses into `osi_waithash_table`. Sleep releases the AFS global lock if held, waits on an `opr_cv_t`, then reacquires the global lock. Timed waits are placed on a separate list; `afs_osi_CheckTimedWaits` must be driven periodically to signal expired waits because this user-space layer cannot depend on a native timed wait in every target environment.

## State and Persistence Behavior

The file keeps mutable process-wide libuafs state only in memory. Persistent cache state is delegated to afsd, cache files, and the regular host filesystem through `osi_UFSOpen`/`afs_osi_Read`/`afs_osi_Write`. `uafs_SetTokens`, stats controls, flush, quota, cell status, and mountpoint status are implemented by synthetic `Afs_syscall`/`PIOCTL` calls.

Thread-specific `usr_user` records are allocated with `pthread_setspecific`; each thread inherits a copy of the global credential. Credential reference counts are manual. The descriptor table has a hard `MAX_OSI_FILES` limit and is protected only by the AFS global lock discipline. Vnode lifetimes are maintained with `VN_HOLD` and `VN_RELE`; dropping the final ref invokes `afs_inactive`.

## Dependencies and Integration Points

This file is compiled only under `UKERNEL` and depends on `afs/sysincludes.h`, `afsincludes.h`, afsd interfaces, RX internals, cache manager prototypes, bypass-cache helpers, and OpenAFS vnode operations. It is the implementation behind declarations in `afs_usrops.h` and the user-space system abstractions in `sysincludes.h` and `osi_machdep.h`.

It integrates with the rest of OpenAFS by calling `afs_mount`, `afs_root`, `afs_lookup`, `afs_open`, `afs_close`, `afs_read`, `afs_write`, `afs_getattr`, `afs_setattr`, directory VNOPS, PIOCTL handlers via `Afs_syscall`, token management through `ktc_ForgetAllTokens`, and afsd startup through `afsd_init`, `afsd_parse`, and `afsd_run`.

## Risks and Edge Cases

- Several unsupported kernel paths intentionally `usr_assert(0)`, including inode syscalls, generic ioctl fallthrough, buffer completion, and `getf`; callers must not reach them in libuafs.
- Descriptor APIs index `afs_FileTable[fd]` directly without visible range checks, so invalid negative or too-large descriptors can be unsafe if exposed to untrusted callers.
- `uafs_pread_nocache_r` calls `afs_DestroyReq(bparms->areq)` if `afs_CreateReq` fails even though request ownership may not be initialized; this path warrants careful testing.
- Timed waits rely on external polling of `afs_osi_CheckTimedWaits`; forgotten polling can block waiters indefinitely.
- `uafs_getdents_r` releases `AFS_GLOCK` on `EBADF` even though `_r` helpers are expected to be called with the lock already held and not to alter lock state; this asymmetry is a test target.
- Path normalization accepts only paths under `afs_mountDir`; duplicate slash handling is manual and must remain aligned with `calcMountDir`.
- Root operations are guarded inconsistently: some root modifications return `EACCES` directly instead of setting `errno`, unlike most `_r` failures.
- All users are treated as superuser by `afs_osi_suser`/`afs_suser`; authorization must come from AFS tokens/ACLs rather than local privilege checks.

## Test Signals

Useful signals include libuafs smoke tests for setup, parse, run, mount, shutdown, relative and absolute path lookup, symlink loop limits, open/read/write/seek/close offset behavior, descriptor exhaustion, invalid descriptor handling, root mutation rejection, directory stream behavior, PIOCTL token/stat/quota calls, cache-file I/O error propagation, and multi-thread sleep/wakeup with the global lock held and not held.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/UKERNEL/afs_usrops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/UKERNEL/afs_usrops.h -->
# sources/distributed-fs/openafs/src/afs/UKERNEL/afs_usrops.h

## Purpose

`afs_usrops.h` declares the public libuafs user-operation API and the small doubly linked-list macros used by the UKERNEL wait queues. It is the consumer-facing header for `afs_usrops.c`.

## Important APIs, Types, and Functions

The header exposes `afs_cdir`, `afs_LclCellName`, and `afs_osicred_Initialized`, plus lifecycle APIs `uafs_InitThread`, `uafs_Setup`, `uafs_ParseArgs`, `uafs_Run`, `uafs_MountDir`, `uafs_mount`, `uafs_setMountDir`, `uafs_Shutdown`, and `uafs_RxServerProc`.

It declares path/attribute helpers `uafs_LookupName`, `uafs_LookupLink`, `uafs_LookupParent`, `uafs_GetAttr`, `uafs_afsPathName`, `uafs_IsRoot`, and `uafs_statmountpoint_r`; POSIX-like operations for directories, files, symlinks, links, renames, chmod, truncate, fsync, directory streams, access checks, and rights retrieval; token and PIOCTL-style helpers such as `uafs_SetTokens`, RPC stats toggles, and `call_syscall`.

The `DLL_INIT_LIST`, `DLL_INSERT_TAIL`, and `DLL_DELETE` macros manipulate intrusive doubly linked lists by named next/prev members.

## Control Flow

There is no executable control flow in this header. Its shape separates locking wrappers and `_r` variants: public non-`_r` functions acquire the AFS global lock in `afs_usrops.c`, while `_r` variants are intended for callers already inside the UKERNEL lock context.

## State and Persistence Behavior

The header itself owns no state. It defines external access to process-global libuafs state such as the config directory and local cell name. Persistence is entirely downstream in cache manager and host filesystem code.

## Dependencies and Integration Points

When compiled under `KERNEL`, the header includes `afs/sysincludes.h` and `afsincludes.h`, which provide the UKERNEL-renamed vnode, vattr, uio, and credential types. It is used by afsd glue, test programs, and any embedding application that drives libuafs.

## Risks and Edge Cases

The list macros are not type-safe, evaluate their arguments multiple times, and assume the element is present for deletion. The API exposes raw `char *`, integer descriptor, and `struct usr_vnode *` arguments, so ABI stability and caller-side lifetime rules matter.

## Test Signals

Build tests should ensure all declarations match `afs_usrops.c`, especially `_r` variants and platform-dependent structs. Integration tests should compile a small libuafs embedding program that includes this header and exercises setup, path lookup, file I/O, directory reads, token setup, and shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/UKERNEL/afs_usrops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/UKERNEL/afsd_uafs.c -->
# sources/distributed-fs/openafs/src/afs/UKERNEL/afsd_uafs.c

## Purpose

`afsd_uafs.c` adapts the afsd cache-manager startup interface to the UKERNEL/libuafs environment. It supplies afsd callbacks that would normally mount, fork, daemonize, or make syscalls in a kernel-backed client.

## Important APIs, Types, and Functions

- `afsd_mount_afs` sets the libuafs mount directory and calls `uafs_mount`.
- `afsd_set_rx_rtpri` and `afsd_set_afsd_rtpri` are no-op priority hooks.
- `afsd_check_mount` accepts the mount point without host validation.
- `afsd_call_syscall` packages `struct afsd_syscall_args` through `call_syscall(AFSCALL_CALL, ...)`.
- `afsd_fork` starts an afsd callback on a pthread with `usr_thread_create`, then joins or detaches depending on `wait`.
- `afsd_daemon` is a no-op and returns success.

## Control Flow

The afsd runtime calls these hooks during `uafs_Run`/`afsd_run`. Instead of kernel syscalls and process forks, the code stays in-process: mount requests go through libuafs globals, syscall requests go through the UKERNEL `Afs_syscall` shim, and daemon workers become pthreads.

## State and Persistence Behavior

This file keeps no persistent state. It mutates libuafs mount state through `uafs_setMountDir` and `uafs_mount`; thread lifetimes are controlled by join/detach behavior.

## Dependencies and Integration Points

It depends on `afs/sysincludes.h`, `afsincludes.h`, `afs_usrops.h`, afsd headers, and `afs_args.h`. It is only compiled under `UKERNEL`.

## Risks and Edge Cases

`afsd_check_mount` always returns success, so invalid mount names must already be handled in `uafs_setMountDir`. `afsd_fork` reports raw pthread return codes rather than errno-style transformed errors. Daemonization and priority knobs are intentionally ignored, which can affect callers expecting process isolation or scheduling changes.

## Test Signals

Exercise afsd startup under libuafs with both waiting and detached callback threads. Verify mount-dir changes take effect, syscall arguments reach `Afs_syscall`, and daemon/priority calls do not fail startup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/UKERNEL/afsd_uafs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/UKERNEL/afsincludes.h -->
# sources/distributed-fs/openafs/src/afs/UKERNEL/afsincludes.h

## Purpose

`afsincludes.h` is the UKERNEL aggregation header for OpenAFS internal headers. It centralizes cache-manager, RX, volume, directory, stats, ACL, callback, and disconnected-mode declarations needed by UKERNEL source files.

## Important APIs, Types, and Functions

The file exports no functions of its own. It includes headers for `afs/stds.h`, `roken`, `opr`, `rx`, `afs_osi`, locks, volume errors/defs, `afsint`, exporter/NFS integration, VLDB, cache-manager core structures, chunk ops, rxkad, protection rights, directory handling, access cache, ICL tracing, stats, prototypes, and disconnected mode.

## Control Flow

There is no runtime control flow. It determines compile-time visibility and include order for UKERNEL files.

## State and Persistence Behavior

No state is defined. State comes from included subsystems such as vcache, dcache, cell config, RX, and disconnected-mode metadata.

## Dependencies and Integration Points

Almost every UKERNEL `.c` file includes this after `afs/sysincludes.h`. It must remain aligned with the symbols needed by `afs_usrops.c`, OSI shims, and VNOPS code compiled in the user-space kernel configuration.

## Risks and Edge Cases

As a broad include umbrella, it can mask missing direct dependencies and increase rebuild scope. Include-order regressions are likely because several OpenAFS headers define platform macros and type aliases.

## Test Signals

The main signal is successful UKERNEL/libuafs compilation across supported user platforms. Include hygiene tests can compile small files with only `afs/sysincludes.h` plus `afsincludes.h` to catch missing or conflicting definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/UKERNEL/afsincludes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/UKERNEL/osi_gcpags.c -->
# sources/distributed-fs/openafs/src/afs/UKERNEL/osi_gcpags.c

## Purpose

`osi_gcpags.c` supplies the UKERNEL implementation of process-to-credential lookup for PAG garbage collection when `AFS_GCPAGS` is enabled.

## Important APIs, Types, and Functions

`afs_osi_proc2cred(afs_proc_t *pr)` returns `pr->p_cred` for a non-null process and `NULL` otherwise. Under UKERNEL, `afs_proc_t` is a preprocessor alias to `struct usr_proc`.

## Control Flow

The function is a direct accessor guarded by `#if AFS_GCPAGS`; there is no allocation, locking, or credential copy.

## State and Persistence Behavior

It returns a pointer to process-owned credential state. The caller must treat the returned credential as borrowed and non-persistent. No state is modified.

## Dependencies and Integration Points

It includes the standard UKERNEL headers and `afs/afs_stats.h`. It is used by PAG cleanup code that needs to inspect process credentials without kernel-native process structures.

## Risks and Edge Cases

The function assumes `p_cred` exists in the UKERNEL process type; other code in `sysincludes.h` defines `struct usr_proc` with `p_ucred`, while this file references `p_cred`, making platform macro compatibility worth checking. There is no refcount increment, so callers must not hold the pointer beyond process lifetime.

## Test Signals

Build with `AFS_GCPAGS` enabled for UKERNEL. Runtime tests should create a `usr_proc` with credentials and ensure PAG cleanup sees the expected pointer without leaking or dereferencing null processes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/UKERNEL/osi_gcpags.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/UKERNEL/osi_groups.c -->
# sources/distributed-fs/openafs/src/afs/UKERNEL/osi_groups.c

## Purpose

`osi_groups.c` implements UKERNEL group-list manipulation for PAG assignment. It adapts OpenAFS PAG encoding into the user-space credential group array.

## Important APIs, Types, and Functions

- `afs_xsetgroups` is unsupported and asserts.
- `afs_getgroups` copies `cred->cr_groups` into a caller-provided `gid_t` array and returns `cr_ngroups`.
- `afs_setgroups` validates `NGROUPS_MAX`, optionally copies the credential with `crcopy`, sets `cr_ngroups`, and writes the new group list.
- `usr_setpag` generates or accepts a PAG value, allocates a small temporary group array, inserts two PAG groups if none are present, encodes the PAG with `afs_get_groups_from_pag`, and updates the credential.

## Control Flow

`usr_setpag` is the public path, used through the `setpag` macro in `sysincludes.h`. It generates a PAG if `pagvalue == -1`, copies current groups, makes room for the two PAG gids when needed, and calls `afs_setgroups`. Cleanup always frees the temporary small-space allocation.

## State and Persistence Behavior

The file mutates only in-memory `usr_ucred` group membership. If `change_parent` is false, a copied credential is installed through the caller's `cred` pointer; otherwise the original credential is changed in place. The PAG persists for that credential until it is replaced or freed.

## Dependencies and Integration Points

It depends on OpenAFS PAG helpers `afs_genpag`, `afs_get_pag_from_groups`, `afs_get_groups_from_pag`, and `crcopy`, plus UKERNEL small-space allocation. It integrates with token identity and request creation through credentials.

## Risks and Edge Cases

`gidset` is allocated with fixed `AFS_SMALLOCSIZ`; group insertion checks byte size before shifting, but `afs_getgroups` must not overflow that buffer if a credential already has many groups. `afs_xsetgroups` intentionally aborts if reached. `pagvalue == -1` is compared against an unsigned `afs_uint32`, relying on wrap semantics.

## Test Signals

Test PAG creation with and without an existing PAG, maximum group counts, `change_parent` true and false, allocation failure, invalid oversized group lists, and round-trip decoding through `afs_get_pag_from_groups`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/UKERNEL/osi_groups.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/UKERNEL/osi_machdep.h -->
# sources/distributed-fs/openafs/src/afs/UKERNEL/osi_machdep.h

## Purpose

`osi_machdep.h` defines UKERNEL-specific OSI machine dependencies. It maps OpenAFS kernel abstractions to user-space types, locks, time functions, lookup helpers, and current-user accessors.

## Important APIs, Types, and Functions

It sets constants such as `MAX_OSI_PATH`, `MAX_OSI_FILES`, `MAX_OSI_LINKS`, `OSI_WAITHASH_SIZE`, and `MAX_HOSTADDR`. It maps `afs_ucred_t` to `struct usr_ucred`, `afs_proc_t` to `struct usr_proc`, and `AFS_KALLOC` to `afs_osi_Alloc`.

It defines time helpers `afs_hz`, `osi_Time`, and inline `osi_GetTime`; lookup macros `gop_lookupname` and `gop_lookupname_user`; global-lock declarations and macros `ISAFS_GLOCK`, `AFS_GLOCK`, `AFS_GUNLOCK`, `AFS_ASSERT_GLOCK`; current user macros `setuerror`, `getuerror`, and `osi_curcred`; and `osi_procname`.

## Control Flow

The lock macros are the only executable behavior: `AFS_GLOCK` enters `afs_global_lock` and records the pthread owner; `AFS_GUNLOCK` asserts ownership, clears the owner, and exits the mutex. `osi_GetTime` calls `gettimeofday` and copies seconds/useconds into OpenAFS's 32-bit timeval type.

## State and Persistence Behavior

The header declares `afs_global_owner`, `afs_global_lock`, and `afs_bufferpages`, but does not define them. It relies on thread-local `get_user_struct()` state for current credentials and user error storage.

## Dependencies and Integration Points

It is included through `afs_osi.h` in the UKERNEL build. It is foundational for all UKERNEL files and must match implementations in `afs_usrops.c` and definitions in `sysincludes.h`.

## Risks and Edge Cases

The global-lock owner is a `pthread_t` compared by `==` and cleared with `memset`; that assumes the platform's pthread type tolerates those operations. `osi_Time` has second granularity. `osi_procname` always returns `"(unknown)"`, so diagnostics lose process names in UKERNEL.

## Test Signals

Build and runtime tests should assert that nested lock misuse panics, current credential macros return per-thread credentials, path lookup macros reach `lookupname`, and `osi_GetTime` produces sane wall-clock values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/UKERNEL/osi_machdep.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/UKERNEL/osi_prototypes.h -->
# sources/distributed-fs/openafs/src/afs/UKERNEL/osi_prototypes.h

## Purpose

`osi_prototypes.h` declares exported UKERNEL OSI support functions for VFS and vnode operations.

## Important APIs, Types, and Functions

It declares VFS routines from `osi_vfsops.c`: `afs_statvfs`, `afs_mount`, `afs_unmount`, `afs_root`, `afs_sync`, `afs_statfs`, `afs_mountroot`, and `afs_swapvp`. It declares vnode glue from `osi_vnodeops.c`: `afs_vrdwr` and `afs_inactive`.

## Control Flow

No runtime behavior exists in this header. Its layout mirrors the implementing files and allows common OpenAFS code to call these user-space OSI functions.

## State and Persistence Behavior

No state is defined. Implementations manipulate `afs_globalVFS`, `afs_globalVp`, vnode references, and cache-manager state.

## Dependencies and Integration Points

It depends on UKERNEL types such as `struct vfs`, `struct vnode`, `struct usr_uio`, `struct vcache`, and `afs_ucred_t`, defined through `sysincludes.h` and `osi_machdep.h`.

## Risks and Edge Cases

Prototype drift is the main risk, especially because many VNOP signatures vary by platform. Any mismatch can compile on one platform and fail on another.

## Test Signals

Compile UKERNEL with strict prototypes enabled and ensure every declaration matches its implementation. Link tests should reference each declared function.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/UKERNEL/osi_prototypes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/UKERNEL/osi_vcache.c -->
# sources/distributed-fs/openafs/src/afs/UKERNEL/osi_vcache.c

## Purpose

`osi_vcache.c` implements UKERNEL vnode/vcache allocation, initialization, attachment, and hold helpers used by generic OpenAFS vcache code.

## Important APIs, Types, and Functions

- `osi_TryEvictVCache` flushes a vcache only if its vnode refcount is zero, it has no opens, and it is not marked `CUnlinkedDel`.
- `osi_NewVnode` allocates a `struct vcache`.
- `osi_PrePopulateVCache` zeroes a newly allocated vcache.
- `osi_AttachVnode` is a no-op in UKERNEL.
- `osi_PostPopulateVCache` attaches the global VFS and vnode ops to the embedded vnode and defaults the type to `VREG`.
- `osi_vnhold` increments the vnode refcount through `VN_HOLD`.

## Control Flow

Generic vcache creation calls allocate, prepopulate, and postpopulate hooks around OpenAFS cache initialization. Eviction tests the UKERNEL vnode refcount before calling `afs_FlushVCache`.

## State and Persistence Behavior

The file mutates in-memory vcache/vnode metadata only. It depends on `afs_globalVFS` and `afs_ops` to attach a usable vnode.

## Dependencies and Integration Points

It integrates with vcache management, `AFSTOV`, `VREFCOUNT_GT`, `VN_HOLD`, `vSetType`, and the `Afs_vnodeops` table from `osi_vnodeops.c`.

## Risks and Edge Cases

`osi_AttachVnode` ignores the sequence argument. `osi_NewVnode` returns raw allocated memory and requires the caller to run `osi_PrePopulateVCache`. `osi_PostPopulateVCache` defaults every vnode to regular file until later status processing updates type.

## Test Signals

Test vcache allocation paths, refcount increments, postpopulate ops/VFS assignment, and eviction refusal for open, referenced, or unlinked-delete vcaches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/UKERNEL/osi_vcache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/UKERNEL/osi_vfsops.c -->
# sources/distributed-fs/openafs/src/afs/UKERNEL/osi_vfsops.c

## Purpose

`osi_vfsops.c` provides the UKERNEL VFS operation table and mount/root/statfs shims for the user-space AFS filesystem.

## Important APIs, Types, and Functions

`Afs_vfsops` maps mount, unmount, root, statfs, and sync operations. Global state includes `afs_globalVFS`, `afs_globalVp`, and `afs_rootCellIndex`. Functions are `afs_mount`, `afs_unmount`, `afs_root`, `afs_sync`, `afs_statfs`, `afs_statvfs`, `afs_mountroot`, and `afs_swapvp`.

## Control Flow

`afs_mount` rejects remounts by returning `EBUSY` through `setuerror`, sets VFS block size, and installs AFS magic fsid values. `afs_root` reuses `afs_globalVp` if statted, otherwise initializes a request, checks cache-manager init, fetches the root vcache from `afs_rootFid`, holds it, marks it `VROOT`, and returns its vnode. `afs_unmount` clears the global VFS and calls `afs_shutdown(AFS_WARM)`.

## State and Persistence Behavior

Mount state is process-global and in-memory. The root vcache is deliberately retained in `afs_globalVp`. `statfs`/`statvfs` return synthetic capacity and filesystem identity values rather than querying a backing store.

## Dependencies and Integration Points

The file depends on request creation, `afs_CheckInit`, `afs_GetVCache`, `afs_PutVCache`, `afs_shutdown`, tracing, and UKERNEL VFS/vnode types. It is called by `uafs_mount` and `uafs_statvfs`.

## Risks and Edge Cases

Only one mount is supported. `afs_unmount` does not inspect outstanding vnodes or file descriptors. `afs_statvfs` returns fake free-space values, so applications should not treat them as authoritative quota data.

## Test Signals

Test successful mount/root/statvfs/unmount, remount rejection, root vnode reuse, warm shutdown invocation, and behavior when `afs_CheckInit` or root vcache fetch fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/UKERNEL/osi_vfsops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/UKERNEL/osi_vm.c -->
# sources/distributed-fs/openafs/src/afs/UKERNEL/osi_vm.c

## Purpose

`osi_vm.c` supplies UKERNEL stubs for VM and page-cache hooks required by shared OpenAFS code. In user-space libuafs there is no kernel VM cache to flush, truncate, or smush.

## Important APIs, Types, and Functions

The file defines `osi_VM_Truncate`, `osi_VM_FlushVCache`, `osi_VM_StoreAllSegments`, `osi_VM_TryToSmush`, and `osi_VM_FlushPages`. All are no-ops except `osi_VM_FlushVCache`, which returns success.

## Control Flow

There is no substantive control flow. Calls return immediately.

## State and Persistence Behavior

No state is read or written. File data persistence is handled through dcache and cache-file paths, not kernel VM pages.

## Dependencies and Integration Points

The functions satisfy the OSI VM hook contract used by generic OpenAFS vnode and cache code. They include UKERNEL and stats headers for compatibility.

## Risks and Edge Cases

Shared code that assumes VM hooks flush dirty memory must not rely on these stubs in UKERNEL. Data consistency must be covered by `afs_StoreAllSegments`, dcache writes, and explicit file operation paths.

## Test Signals

Build coverage is the main signal. Runtime tests should verify truncation, writeback, close, and fsync behavior through libuafs operations rather than these no-op hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/UKERNEL/osi_vm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/UKERNEL/osi_vnodeops.c -->
# sources/distributed-fs/openafs/src/afs/UKERNEL/osi_vnodeops.c

## Purpose

`osi_vnodeops.c` wires generic OpenAFS vnode operations into the UKERNEL `usr_vnodeops` table and provides read/write and inactive adapters.

## Important APIs, Types, and Functions

- `afs_vrdwr` dispatches `UIO_WRITE` to `afs_write` and all other directions to `afs_read`.
- `afs_inactive` ignores shutdown, asserts the vcache refcount is zero, and calls `afs_InactiveVCache`.
- `Afs_vnodeops` maps open, close, rdwr, getattr, setattr, access, lookup, create, remove, link, rename, mkdir, rmdir, readdir, symlink, readlink, fsync, inactive, and lockctl to OpenAFS implementations, with unsupported bmap/strategy/bread/brelse/ioctl entries set to bad ops/noops.
- `afs_ops` points at `Afs_vnodeops`.

## Control Flow

UKERNEL vnode callers dereference `v_op` set by `osi_PostPopulateVCache`. Read/write calls enter `afs_vrdwr`, which adapts `usr_uio` and credentials to `afs_read`/`afs_write`. Vnode release in `VN_RELE` eventually calls `afs_inactive`.

## State and Persistence Behavior

The operation table is static process state. `afs_inactive` can trigger vcache cleanup and state transitions in generic cache-manager code. Read/write persistence is handled by the underlying OpenAFS data paths.

## Dependencies and Integration Points

It integrates `sysincludes.h`'s `struct usr_vnodeops` with VNOPS implementations from `src/afs/VNOPS` and with vcache lifecycle code.

## Risks and Edge Cases

Unsupported vnode operations intentionally route to `afs_badop`; callers must not expect block-device or buffer-cache behavior in UKERNEL. `afs_vrdwr` treats anything other than `UIO_WRITE` as read, so direction values must be normalized.

## Test Signals

Test vnode operation table completeness, libuafs read/write paths, final-reference release calling inactive, and bad-op behavior for unsupported operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/UKERNEL/osi_vnodeops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/UKERNEL/sysincludes.h -->
# sources/distributed-fs/openafs/src/afs/UKERNEL/sysincludes.h

## Purpose

`sysincludes.h` is the central UKERNEL compatibility header. It includes user-space system headers, renames kernel structure names to `usr_*`, defines kernel constants and macros, and declares user-space replacements for vnode, VFS, uio, credential, network-interface, and directory types.

## Important APIs, Types, and Functions

Key macro groups include kernel-to-user renames (`vnode` to `usr_vnode`, `vfs` to `usr_vfs`, `vattr` to `usr_vattr`, `uio` to `usr_uio`, `crget` to `usr_crget`), vnode/file constants (`VREG`, `VDIR`, `VLNK`, `FREAD`, `FWRITE`, `FTRUNC`, `LOCK_*`, `UIO_*`, buffer flags), copy helpers (`copyin`, `copyout`, `copyinstr`, `copyoutstr`), thread helpers (`usr_thread_create`, `usr_thread_sleep`), assertion/panic helpers, and vnode reference macros `VN_HOLD` and `VN_RELE`.

Important structs are `usr_statfs`, `usr_vattr`, `usr_vnode`, `usr_inode`, `usr_fileops`, `usr_file`, `usr_flock`, `usr_proc`, `usr_uio`, `usr_buf`, `usr_vnodeops`, `usr_fs`, `usr_mount`, `usr_vfsops`, `usr_vfs`, network-interface structs, `min_direct`, `usr_ucred`, `usr_user`, `usr_dirent`, and `usr_DIR`.

## Control Flow

Most content is compile-time adaptation. Runtime behavior appears in inline/macros: `panic` prints and asserts; `usr_thread_create` initializes pthread attributes, sets a fixed stack size, starts a thread, and destroys attributes; `usr_thread_sleep` calculates an absolute timeout and waits on a shared condition; `VN_RELE` asserts the AFS global lock, decrements the vnode count, and calls `afs_inactive` at zero.

## State and Persistence Behavior

The header declares global sleep primitives, network-interface lists, `usr_rx_port`, credential/user accessors, and file helpers. It stores no persistent data itself. `usr_user` and `usr_ucred` define the in-memory identity state that drives request creation and PAG/token behavior.

## Dependencies and Integration Points

This file must be included before OpenAFS internals that expect kernel types. It integrates with `afs_usrops.c` implementations of credentials, per-thread user state, sleep, and file operations, plus `osi_machdep.h` current-credential macros.

## Risks and Edge Cases

- Heavy macro renaming can cause surprising symbol substitutions and include-order sensitivity.
- `pid_t` is redefined to `int`, and `getpid()` is mapped to a pthread-derived value, which changes process identity semantics.
- `VN_RELE` requires the AFS global lock and calls into inactive cleanup from a macro.
- `usr_thread_create` uses a fixed stack size, which may be insufficient for deep call paths or excessive for many worker threads.
- Several kernel constants are simplified and may not match every host platform's values.

## Test Signals

The most valuable tests are cross-platform UKERNEL builds, compile checks for struct layout assumptions, thread creation/sleep tests, vnode refcount/inactive tests, credential copy/free tests, and integration tests that include system and OpenAFS headers in the same order as production.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/UKERNEL/sysincludes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/VNOPS/afs_vnop_access.c -->
# sources/distributed-fs/openafs/src/afs/VNOPS/afs_vnop_access.c

## Purpose

`afs_vnop_access.c` implements AFS vnode access checks. It translates Unix `VREAD`/`VWRITE`/`VEXEC` access requests into AFS protection rights, combines directory ACL rights with file owner/mode restrictions, handles fakestat and disconnected-mode constraints, and exposes a UKERNEL helper for retrieving rights.

## Important APIs, Types, and Functions

- `fileModeMap` maps owner mode-bit combinations to AFS read/write rights that should be masked off.
- `afs_GetAccessBits` returns which requested AFS rights are available from `anyAccess`, per-PAG access cache, or a server `FetchStatus` result.
- `afs_AccessOK` determines whether a vcache grants all requested AFS rights, using directory ACLs for files and ACL-only checks for directories/foreign vnodes.
- `afs_access` is the vnode access operation for Unix modes.
- Under `UKERNEL`, `afs_getRights` verifies the vcache and returns `afs_GetAccessBits` for a requested rights mask.

## Control Flow

`afs_access` creates a `vrequest`, enters the disconnected lock, evaluates fakestat/mountpoint state, verifies the vcache unless a readdir-specific bypass applies, rejects writes to read-only volumes, rejects disconnected writes when disconnected write mode is unavailable, and then maps Unix mode bits. Directory execute maps to `PRSFS_LOOKUP`; directory write accepts insert or delete; regular-file execute requires read plus owner execute bit handling; writes and reads call `afs_AccessOK`.

`afs_AccessOK` handles directories directly from ACL rights. For files, it resolves parent directory rights when parent fid metadata exists, optionally fetches file administer rights, grants read/write when insert and administer imply ownership, and then applies Unix owner mode-bit masks.

## State and Persistence Behavior

This file reads and updates access-related cache state indirectly. `afs_GetAccessBits` consults `avc->f.anyAccess`, `avc->Access`, user token state, and may refresh status through `afs_FetchStatus`. It does not persist state itself but may cause access cache/status changes inside fetch/verify paths.

## Dependencies and Integration Points

It depends on vcache status, per-user token records, `afs_FindAxs`, `afs_FindUser`, `afs_FetchStatus`, fakestat helpers, disconnected-mode macros, NFS translator flags, and `afs_CheckCode`. UKERNEL `uafs_access` and `uafs_getRights` call into this file.

## Risks and Edge Cases

Parentless files assume directory rights are OK (`0xffffffff`), called out as a race condition. Disconnected mode denies rights that would require a server access fetch. NFS translator compatibility includes special handling for anonymous-owner writes and execute-as-read. `afs_InReadDir` deliberately grants only lookup/read to avoid recursive fetch-status problems.

## Test Signals

Test directory and file access under combinations of ACLs, mode bits, owner/admin rights, read-only volumes, bad/missing tokens, foreign cells, fakestat mountpoints, disconnected read-only and disconnected write mode, NFS translator credentials, and active readdir.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/VNOPS/afs_vnop_access.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/VNOPS/afs_vnop_attrs.c -->
# sources/distributed-fs/openafs/src/afs/VNOPS/afs_vnop_attrs.c

## Purpose

`afs_vnop_attrs.c` implements vnode attribute retrieval and update. It converts OpenAFS vcache metadata to Unix `vattr`, verifies and fetches status when needed, maps Unix attribute updates into AFS store-status requests, handles truncation/writeback, and supports disconnected-mode attribute updates.

## Important APIs, Types, and Functions

- `afs_CopyOutAttrs` copies cached vcache metadata to a platform `vattr`, including mode, uid/gid, fsid, inode number, link count, size, times, dataversion-derived subsecond/gen fields, block size, and block count.
- `afs_getattr` is the vnode getattr operation.
- `afs_VAttrToAS` converts a `vattr` update mask to `struct AFSStoreStatus`.
- `afs_setattr` is the vnode setattr operation.
- `afs_CreateAttr` and `afs_DestroyAttr` allocate/free `struct vattr` from small-space allocation.

## Control Flow

`afs_getattr` handles fakestat mountpoints first, returns cached attributes for hint/UBC cases on some platforms, otherwise enters the disconnected lock, verifies uncached status, flushes pages/text where needed, copies attributes, and performs NFS exporter mode/inode adjustments.

`afs_setattr` creates a request, evaluates fakestat, rejects read-only volumes, checks write permission for size changes, rejects disconnected writes unless write-disconnected mode is active, converts attributes to `AFSStoreStatus`, and handles truncation/growth. Size changes mark the vcache dirty, truncate or extend segments, optionally store segments asynchronously, update modtime, flush text, and then either call `afs_WriteVCache` online or `afs_WriteVCacheDiscon` offline.

## State and Persistence Behavior

Getattr reads from vcache status and may verify/fetch freshness. Setattr mutates vcache state, dcache segments, dirty flags, dataversions, modtime, callback freshness, and remote fileserver status. In disconnected write mode it records local state for later replay. Attribute allocation uses UKERNEL/OSI small-space memory.

## Dependencies and Integration Points

It depends on fakestat, disconnected locking, vcache verification, access checks, segment truncation/extension/store, `afs_WriteVCache`, `afs_WriteVCacheDiscon`, NFS exporter state, cell SUID policy, volume lookup for mountpoint roots, and platform vnode/page-cache helpers.

## Risks and Edge Cases

Dataversion is encoded into subsecond fields differently per platform. SUID/SGID bits are masked for no-SUID cells. Size changes have complex interactions with dirty state, store timing, NFS translator writer counts, and disconnected mode. If online `afs_WriteVCache` fails after local mutation, the vcache is marked stale but callers still need robust error handling.

## Test Signals

Test getattr on regular files, directories, mountpoints, fake-stat mountpoints, root vnodes, no-SUID cells, NFS-exported paths, and stale vcaches. Test setattr for chmod, chown, chgrp, mtime, truncate shrink/grow, read-only volumes, disconnected read-only, disconnected write replay, and store failure stale marking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/VNOPS/afs_vnop_attrs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/VNOPS/afs_vnop_create.c -->
# sources/distributed-fs/openafs/src/afs/VNOPS/afs_vnop_create.c

## Purpose

`afs_vnop_create.c` implements file creation and open-with-create behavior, including existing-file handling, server `CreateFile` RPCs, dcache directory updates, disconnected-mode fake fid creation, callback optimism, and local directory consistency through `afs_LocalHero`.

## Important APIs, Types, and Functions

- `afs_create` creates or opens a file in a directory vcache.
- `afs_LocalHero` decides whether a directory dcache can be locally updated after a successful mutating RPC by checking callback freshness and expected data version.

Important internal state includes `OutFidStatus`, `OutDirStatus`, `InStatus`, `newFid`, parent dcache `tdc`, callback counters `afs_evenCBs`/`afs_evenZaps` or foreign-cell equivalents, and disconnected dirty flags.

## Control Flow

`afs_create` validates name length, AFS entry-name legality, and unsupported special file types. It evaluates fakestat, verifies the parent directory, rejects read-only and disconnected-read-only cases, fetches the parent directory dcache, and write-locks the parent. If the name already exists in the dcache, exclusive create returns `EEXIST`; non-exclusive create obtains the existing vcache, checks requested read/write rights, and performs truncation via `afs_setattr` when requested.

If the name does not exist, online mode sends `RXAFS_CreateFile` through `afs_Conn`/`afs_Analyze`; an `EEXIST` race in non-exclusive mode falls back to lookup. Disconnected write mode generates a fake fid. After a successful create, the parent dcache is updated through `afs_dir_Create` when disconnected or `afs_LocalHero` confirms data-version consistency. The new vcache is then found or created under `afs_xvcache`, callback/status is installed if optimistic callback counters still match, and disconnected creates are marked dirty.

`afs_LocalHero` compares server `AFSFetchStatus` data version with the expected dcache version plus an increment. If valid, it marks the dcache entry modified and updates version; otherwise it zaps the dcache and purges directory name lookup cache.

## State and Persistence Behavior

Online creates persist via the fileserver RPC and then opportunistically update local directory dcache. Disconnected creates persist only as local fake-fid vcaches and dirty records until replay. Parent link counts and child status are updated locally when possible. Callback queue state may be installed optimistically or invalidated if races occurred.

## Dependencies and Integration Points

The file depends on access checks, dcache directory functions, vcache hash/creation, callback queue, volume lookup, RX fileserver RPCs, disconnected-mode helpers, mariner logging, and `afs_setattr` for truncation of existing files. `uafs_open_r` calls this path for `O_CREAT`.

## Risks and Edge Cases

Create races are explicitly complex: existing dcache entries with unique zero require lookup, non-exclusive `EEXIST` falls back to lookup, and callback optimism relies on global callback/zap counters. If `afs_GetDCache` returns null, the function returns `EIO` to avoid repeated status calls. Disconnected fake fid handling must avoid collisions and replay conflicts. Existing-file truncation temporarily marks `CCreating`.

## Test Signals

Test exclusive/non-exclusive create, create existing regular file with and without truncate, unsupported special types, invalid names, overlong names, read-only volumes, disconnected read-only, disconnected write fake-fid creation/replay, callback race invalidation, dcache update failure, and create/lookup races returning `EEXIST`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/VNOPS/afs_vnop_create.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/VNOPS/afs_vnop_dirops.c -->
# sources/distributed-fs/openafs/src/afs/VNOPS/afs_vnop_dirops.c

## Purpose

`afs_vnop_dirops.c` implements directory creation and removal for OpenAFS vnode operations, including online fileserver RPCs, disconnected write-mode local directories, parent dcache edits, link count updates, and dnlc invalidation.

## Important APIs, Types, and Functions

- `afs_mkdir` creates a directory under a parent vcache.
- `afs_rmdir` removes a directory entry from a parent vcache.

Both functions use `struct vrequest`, `struct dcache`, `struct vcache`, `AFSStoreStatus`, `AFSFetchStatus`, fakestat state, RX connections, and disconnected-mode dirty helpers.

## Control Flow

`afs_mkdir` validates name length and legality, evaluates fakestat, verifies the parent, rejects read-only and disconnected-read-only operation, builds an `InStatus`, obtains the parent dcache, and locks the parent. Online mode sends `RXAFS_MakeDir`; disconnected write mode generates a fake fid. The parent dcache is updated via `afs_dir_Create` if disconnected or if `afs_LocalHero` validates the server status. Online mode then fetches the new directory vcache; disconnected mode creates a new vcache, generates status, creates an empty `.`/`..` dcache via `afs_dir_MakeDir`, updates length, and marks it `VDisconCreate`.

`afs_rmdir` validates name length, evaluates fakestat and parent freshness, rejects read-only and disconnected-read-only cases, obtains the parent dcache, optionally finds the target vcache, and online sends `RXAFS_RemoveDir`. Disconnected mode requires local dcache and target vcache, rejects non-empty directories by link count, creates a shadow parent dir if needed, and decrements parent link count. It then deletes the parent dcache entry, purges dnlc state, marks or removes disconnected dirty records, and clears `CUnique` on the removed vcache.

## State and Persistence Behavior

Online mkdir/rmdir persist through fileserver RPCs and update parent dcache/link count when local freshness allows. Disconnected writes persist as local dcache/vcache changes plus dirty operation records for later replay. Directory dcache contents and link counts are mutated under locks.

## Dependencies and Integration Points

This file depends on `afs_LocalHero` from create, directory package functions `afs_dir_Create`, `afs_dir_Delete`, and `afs_dir_MakeDir`, RX RPCs `MakeDir`/`RemoveDir`, dcache/vcache lookup, fakestat, disconnected helpers, dnlc purge/remove, and `afs_CheckCode`.

## Risks and Edge Cases

Disconnected `rmdir` relies on link count to decide emptiness, which can be stale if local state is inconsistent. Mountpoint-directory comments indicate incomplete disconnected handling for mountpoints. Parent dcache absence in disconnected mode results in `ENETDOWN`. Dcache update surprises zap directory caches, so callers must tolerate subsequent refetches.

## Test Signals

Test mkdir/rmdir online success, invalid and overlong names, read-only volumes, disconnected read-only rejection, disconnected write create/remove/replay, local empty directory construction, non-empty directory rejection, shadow directory creation, dnlc purge, and failures in parent dcache acquisition or new dcache creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/VNOPS/afs_vnop_dirops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/VNOPS/afs_vnop_fid.c -->
# sources/distributed-fs/openafs/src/afs/VNOPS/afs_vnop_fid.c

## Purpose

`afs_vnop_fid.c` implements platform-specific vnode-to-filehandle conversion for NFS export paths. It is excluded from UKERNEL and compiled only for platforms defining `AFS_VNOP_FID_ENV`.

## Important APIs, Types, and Functions

The primary function is `afs_fid`, with signatures varying across AIX, SunOS, and other platforms. It builds either a compact `SmallFid` containing volume, vnode, cell index, and unique bits, or a magic translator fid containing the vnode address and `AFS_XLATOR_MAGIC`. Counters `afs_fid_vnodeoverflow` and `afs_fid_uniqueoverflow` track values too large for the compact fields.

## Control Flow

If shutting down, `afs_fid` returns `EIO`. If NFS root-only mode is off, or the vnode is `/afs`, or AIX translator credentials request it, the function builds a `SmallFid`. Otherwise it builds a magic fid so unsupported submounts fail or are ignored unless translated. Depending on platform, it writes into a supplied `struct fid` or allocates one with `AFS_KALLOC`.

## State and Persistence Behavior

No filesystem state is changed except overflow counters and possible vnode refcount hold in magic-fid paths. The returned fid is a transient handle used by NFS/export layers.

## Dependencies and Integration Points

It depends on cell lookup for `cellIndex`, global root vnode `afs_globalVp`, `afs_NFSRootOnly`, platform `struct fid`, `SmallFid`, and NFS translator credential checks. It integrates with export/mountd/NFS lookup paths outside UKERNEL.

## Risks and Edge Cases

The compact fid stores only limited cell, vnode, and unique bits, so overflow is counted but still truncates information. Magic fids include vnode addresses and require careful refcount handling. Platform signature differences make prototype drift risky. Because this file is not compiled for UKERNEL, grouped research should not treat it as part of libuafs runtime.

## Test Signals

Platform NFS export tests should verify root-only and submount behavior, SmallFid round trips, overflow counter increments, magic fid rejection/translation, shutdown `EIO`, and AIX iauth behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/VNOPS/afs_vnop_fid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/VNOPS/afs_vnop_flock.c -->
# sources/distributed-fs/openafs/src/afs/VNOPS/afs_vnop_flock.c

## Purpose

`afs_vnop_flock.c` implements AFS whole-file locking and maps local `fcntl` lock requests to fileserver lock RPCs. It tracks local simple locks, handles shared/exclusive lock compatibility, exposes get-lock queries, and deliberately degrades byte-range locks to warnings/success.

## Important APIs, Types, and Functions

- `lockIdSet` stores the current process identity into an `AFS_FLOCK` or `SimpleLocks`, with platform-specific pid/sysid handling and UKERNEL using `get_user_struct()->u_procp->p_pid`.
- `lockIdcmp2` checks whether a flock identity differs from a simple lock or all locks on a vcache.
- `HandleFlock` performs whole-file lock, unlock, upgrade, downgrade, retry, and server RPC logic.
- `afs_lockctl` is the vnode lock-control entry point for `F_GETLK`, `F_SETLK`, and `F_SETLKW`.
- `HandleGetLock` reports whether a requested lock would be blocked.
- `GetFlockCount` asks the fileserver for lock count through `RXAFS_FetchStatus`.
- `DoLockWarning` rate-limits warnings for ignored byte-range locks.

## Control Flow

`afs_lockctl` creates a request, evaluates fakestat, handles `F_GETLK` through `HandleGetLock`, rejects write locks on read-only volumes, normalizes Java's maximum `l_len` to whole-file, warns and succeeds for true byte-range locks, maps `F_RDLCK`/`F_WRLCK`/`F_UNLCK` to `LOCK_SH`/`LOCK_EX`/`LOCK_UN`, applies nonblocking flags, and calls `HandleFlock`.

`HandleFlock` write-locks the vcache. Unlock removes matching local simple locks and releases the server lock with `RXAFS_ReleaseLock` when local count reaches zero; exclusive unlock first stores dirty segments synchronously and retries checks because store can drop locks. Lock acquisition handles local compatibility, same-process exclusive regrabs, shared/exclusive upgrade/downgrade, server `RXAFS_SetLock` for first local lock, wait/retry for blocking requests, and local simple-lock record insertion.

`HandleGetLock` answers from local `flockCount`/`slocks` when possible and calls `GetFlockCount` when server state is needed. `GetFlockCount` uses a nonblocking request flag and treats RPC failures as unlocked.

## State and Persistence Behavior

Lock state lives in `avc->flockCount`, `avc->slocks`, and platform-specific owner fields such as AIX `ownslock`. Server-visible locks persist in fileserver state until released or timed out. Unlock of exclusive locks flushes dirty file segments to the server before releasing.

## Dependencies and Integration Points

It depends on vcache locks, RX fileserver RPCs `SetLock`, `ReleaseLock`, and `FetchStatus`, request creation, fakestat, disconnected-mode flags, `afs_StoreAllSegments`, process identity macros, and warning/logging helpers. `Afs_vnodeops.vn_lockctl` points here in UKERNEL.

## Risks and Edge Cases

Byte-range locks are not enforced across machines and are reported as success after warning. Disconnected lock acquisition pretends success, while release can return `ENETDOWN`, which can mask cross-client conflicts. `HandleGetLock` contains duplicated write-lock decision blocks, increasing maintenance risk. RPC failure in `GetFlockCount` lies that the file is unlocked. Lock upgrades are intentionally limited and process-identity comparisons vary by platform.

## Test Signals

Test shared and exclusive locks, nonblocking conflicts, blocking retry/interruption, same-process reentrant exclusive lock, shared-to-exclusive upgrade, exclusive-to-shared downgrade, unlock by child/parent rules, read-only volume behavior, byte-range warning rate limiting, disconnected locking, and dirty segment store before exclusive unlock.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/VNOPS/afs_vnop_flock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/VNOPS/afs_vnop_link.c -->
# sources/distributed-fs/openafs/src/afs/VNOPS/afs_vnop_link.c

## Purpose

`afs_vnop_link.c` implements hard-link creation for OpenAFS vnode operations. It validates source and destination compatibility, calls the fileserver `Link` RPC, updates the parent directory dcache when safe, and marks the linked file vcache stale.

## Important APIs, Types, and Functions

The single exported operation is `afs_link`, with argument order varying by platform. It uses `struct vrequest`, parent dcache `tdc`, `OutFidStatus`, `OutDirStatus`, fakestat states for both source and directory, and `RXAFS_Link`.

## Control Flow

`afs_link` creates a request, initializes fakestat state, enters disconnected lock, evaluates source and destination directory fakestat, rejects cross-cell or cross-volume links with `EXDEV`, rejects overlong names, verifies the destination directory, rejects read-only volumes, and rejects all disconnected mode with `ENETDOWN`. It obtains the parent dcache, write-locks the parent, sends `RXAFS_Link`, and on success uses `afs_LocalHero` to decide whether to insert the new name into the parent dcache. It then releases the parent lock, write-locks the source file, and marks it stale because the precise new link count may not be authoritative.

## State and Persistence Behavior

Online hard links persist via fileserver RPC. The parent directory dcache may be updated locally if its data version matches the server response. The source vcache is invalidated so link count/status can be refetched. There is no disconnected-write support for hard links in this implementation.

## Dependencies and Integration Points

It depends on fakestat, vcache verification, disconnected locking, RX connections and `afs_Analyze`, directory dcache functions, `afs_LocalHero`, `afs_StaleVCache`, and `afs_CheckCode`. `uafs_link_r` resolves source and destination and calls this operation.

## Risks and Edge Cases

Hard links are prohibited across cells or volumes. Disconnected mode always fails, unlike create/mkdir/rmdir. The file status response is not trusted for link count because concurrent changes can occur while the file is not locked across the RPC. Parent dcache update failure zaps the cache.

## Test Signals

Test successful hard link, cross-volume `EXDEV`, overlong names, read-only volumes, disconnected failure, parent dcache update success and zap paths, source vcache stale marking, and concurrent link/unlink status refresh.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/VNOPS/afs_vnop_link.c -->
