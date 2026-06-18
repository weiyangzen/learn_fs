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
