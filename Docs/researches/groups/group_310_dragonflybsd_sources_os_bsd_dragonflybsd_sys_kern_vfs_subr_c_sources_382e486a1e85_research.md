# Group Research: group_310_dragonflybsd_sources_os_bsd_dragonflybsd_sys_kern_vfs_subr_c_sources_382e486a1e85

Scope: `Docs/research_subset_a.md`, source tree `sources/os/bsd/dragonflybsd`.

Files read completely:
- `sources/os/bsd/dragonflybsd/sys/kern/vfs_subr.c` (2671 lines)
- `sources/os/bsd/dragonflybsd/sys/kern/vfs_sync.c` (890 lines)
- `sources/os/bsd/dragonflybsd/sys/kern/vfs_synth.c` (136 lines)
- `sources/os/bsd/dragonflybsd/sys/kern/vfs_syscalls.c` (5520 lines)
- `sources/os/bsd/dragonflybsd/sys/kern/vfs_vfsops.c` (321 lines)
- `sources/os/bsd/dragonflybsd/sys/kern/vfs_vm.c` (503 lines)

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/vfs_subr.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/vfs_subr.c

## Role

This is DragonFly BSD's main VFS support file for vnode lifecycle, vnode-buffer association, buffer flush/truncation/sync logic, device vnode aliasing, mount export state, timestamp/attribute helpers, and mount-wide VM page synchronization. It provides the shared machinery that filesystem implementations and syscall paths rely on rather than a single filesystem-specific policy.

## Main Responsibilities

- Initializes VFS-wide vnode sizing in `vfs_subr_init()`, deriving `maxvnodes` from physical memory, `maxproc`, KVA size, and hard min/max bounds.
- Provides common attribute and timestamp helpers via `vfs_timestamp()` and `vattr_null()`, with sysctl-controlled timestamp precision.
- Maintains per-vnode buffer-cache red-black trees:
  - `v_rbhash_tree` for lookup by logical offset.
  - `v_rbclean_tree` and `v_rbdirty_tree` for clean/dirty ownership.
  - `bgetvp()`, `brelvp()`, and `reassignbuf()` attach, detach, and move buffers between trees.
- Implements vnode buffer invalidation, truncation, and flushing:
  - `vinvalbuf()` flushes/invalidates all buffers and optionally persists dirty state first.
  - `vtruncbuf()` destroys buffers beyond EOF and synchronizes remaining metadata.
  - `vfsync()` performs lazy, async, and synchronous multipass dirty-buffer writeback.
- Handles vnode reclamation and revocation:
  - `vclean_vxlocked()` disassociates a vnode from its filesystem, invalidates namecache entries, flushes buffers, deactivates if needed, destroys/deallocates VM objects, and calls `VOP_RECLAIM()`.
  - `vgone_vxlocked()`, `vclean_unlocked()`, `vrecycle()`, and `vrevoke()` build higher-level reclaim/revoke behavior.
- Creates and manages special/device vnodes with `bdevvp()`, `v_associate_rdev()`, `v_release_rdev()`, `addaliasu()`, `count_dev()`, and `vcount()`.
- Initializes vnode VM backing objects in `vinitvmio()`.
- Provides generic permission checking in `vaccess()`.
- Implements VFS sysctl exposure for filesystem configuration records.
- Builds and tears down NFS export address lists using radix trees in `vfs_export()`, `vfs_hang_addrlist()`, `vfs_free_addrlist()`, `vfs_setpublicfs()`, and `vfs_export_lookup()`.
- Performs mount-wide VM page cleaning through `vfs_msync()`.
- Provides miscellaneous VFS helpers: `vfs_unmountall()`, `vfs_flagstostr()`, `vn_gone()`, `vn_todev()`, `vn_isdisk()`, `vn_get_namelen()`, `vop_write_dirent()`, `vn_mark_atime()`, `vfs_inodehashsize()`, and `init_va_filerev()`.

## Synchronization and Lifetime Model

- Per-vnode buffer tree operations are protected by `vp->v_token`.
- Special-device alias lists are protected by the static `spechash_token`.
- Reclamation requires a VX-locked and referenced vnode for `vgone_vxlocked()` and `vclean_vxlocked()`.
- Buffer scans use `RB_SCAN()` callbacks that lock each buffer, revalidate it after the lock, and tolerate races by looping until no matching buffers remain.
- Dirty-buffer transitions integrate with the per-mount syncer: `reassignbuf()` adds dirty vnodes to the syncer worklist and removes them when dirty buffers and dirty vnode flags are gone.
- VM object destruction is careful about object references and pager deallocation; reclaimed vnodes must leave `VOBJBUF` and `VOBJDIRTY` cleared.

## Notable Design Details

- `vinvalbuf()` first waits for tracked writes and runs `VOP_FSYNC()` when `V_SAVE` is requested, then drains clean and dirty buffer trees, waits for write I/O and paging-in-progress, and finally removes VM pages.
- `vfsync()` distinguishes data and metadata by negative logical offsets; synchronous mode uses multiple passes and escalates dependency flushing on the final pass.
- `bgetvp()` can perform invasive overlap checks controlled by `vfs.check_buf_overlap`, useful for debugging filesystems that instantiate overlapping buffers.
- `vclean_vxlocked()` sets `VRECLAIMED` early as an interlock, invalidates namecache aliases, flushes buffers twice around deactivate, and moves the vnode to dead vnode ops.
- `vfs_msync()` uses `vsyncscan()` for filesystems with `MNTK_THR_SYNC`, otherwise scans all mount vnodes, cleaning `VOBJDIRTY` VM objects while respecting `MNTK_NOMSYNC` and `MAP_NOSYNC` semantics where appropriate.

## Cross-File Relationships

- `vfs_sync.c` consumes `VONWORKLST`, `VISDIRTY`, `VOBJDIRTY`, and syncer callbacks used by `reassignbuf()`, `vclrobjdirty()`, and `vfs_msync()`.
- `vfs_syscalls.c` calls helpers such as `vinvalbuf()`, `vfs_msync()`, `vfs_unmountall()`-related unmount logic, `vaccess()` indirectly through VOPs, `vcount()`, `vrevoke()`, `vn_writechk()`-adjacent routines, `vfs_flagstostr()`, and NFS filehandle/export helpers.
- `vfs_vm.c` is the newer VM/buffer coherency path for truncation and extension; `vfs_subr.c` retains the older `vtruncbuf()` path.
- `vfs_vfsops.c` wraps filesystem VFS operations that this file invokes through macros such as `VFS_ROOT()`, `VFS_SYNC()`, `VFS_VPTOFH()`, and `VFS_STATFS()`.

## Research Notes

- This file is core infrastructure, not optional glue. Bugs here affect all filesystems using DragonFly's vnode, buffer-cache, mount, and VM integration contracts.
- The high-risk areas are lock ordering and revalidation in buffer scans, vnode reclamation while references still exist, forced unmount cleanup, and NFS export radix-list lifetime.
- The file exposes several diagnostic sysctls (`debug.numvnodes`, `debug.verbose_reclaims`, `vfs.reassignbufcalls`, `vfs.check_buf_overlap`, `kern.maxvnodes`, `vfs.timestamp_precision`) that are useful when investigating VFS behavior.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/vfs_subr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/vfs_sync.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/vfs_sync.c

## Role

This file implements DragonFly BSD's per-filesystem syncer infrastructure. It schedules delayed vnode writeback, owns the syncer kernel thread state per mount, implements dirty-vnode flag transitions, and creates the synthetic syncer vnode that periodically drives `vfs_msync()` and `VFS_SYNC()`.

## Main Responsibilities

- Defines delayed writeback sysctls and tunables:
  - `kern.syncdelay`
  - `kern.filedelay`
  - `kern.dirdelay`
  - `kern.metadelay`
  - `kern.retrydelay`
  - `debug.rush_requests`
- Maintains a `SYNCER_MAXDELAY` time wheel of `struct synclist` buckets in `struct syncer_ctx`.
- Exposes syncer worklist operations:
  - `vn_syncer_add()`
  - `vn_syncer_remove()`
  - `vn_syncer_count()`
- Tracks vnode dirty flags:
  - `vsetisdirty()` and `vclrisdirty()` for dirty inode state.
  - `vsetobjdirty()` and `vclrobjdirty()` for dirty VM object state.
- Creates and stops per-mount syncer threads with `vn_syncer_thr_create()` and `vn_syncer_thr_stop()`.
- Implements `syncer_thread()`, which wakes once per second or on triggers/rush jobs, processes expired vnodes, and invokes `VOP_FSYNC()` with lazy or nowait semantics.
- Provides manual acceleration and triggering:
  - `vn_syncer_one()`
  - `speedup_syncer()`
  - `trigger_syncer_start()`
  - `trigger_syncer_stop()`
  - `trigger_syncer()`
- Implements the syncer vnode VOPs and allocation path:
  - `vfs_allocate_syncvnode()`
  - `sync_fsync()`
  - `sync_inactive()`
  - `sync_reclaim()`
  - `sync_print()`
- Implements `vsyncscan()`, a syncer-list-only vnode scan for filesystems that maintain dirty vnodes on the syncer list and set `MNTK_THR_SYNC`.

## Synchronization and Lifetime Model

- Each mount's `syncer_ctx` owns `sc_token`; it protects `v_synclist`, `VONWORKLST`, the time wheel, and syncer counters.
- `vn_syncer_add()` intentionally depends on the syncer token and must not block in ways that would deadlock callers already in syncer context.
- `vn_syncer_remove()` may reacquire the syncer token, then rechecks dirty flags and dirty-buffer trees before removal.
- `vn_syncer_thr_stop()` sets `SC_FLAG_EXIT`, wakes the thread, and waits for `SC_FLAG_DONE` before destroying the work queue and context.
- `sync_reclaim()` removes the syncer vnode from the worklist during vnode reclamation, asserting that `mp->mnt_syncer` no longer points to it.

## Notable Design Details

- Dirty vnodes are scheduled into a ring bucket based on requested delay; negative delay is used by scan paths to reposition a vnode at an explicit slot.
- File, directory, and metadata delay classes are selected elsewhere, especially by `reassignbuf()` in `vfs_subr.c`.
- `syncer_thread()` moves each vnode to `retrydelay` before attempting fsync. If fsync cannot get the vnode lock in non-forced mode, the vnode remains scheduled for retry.
- A special syncer vnode is itself scheduled on the worklist; its lazy fsync drives full mount-level work through `vfs_msync()` and `VFS_SYNC()`.
- `speedup_syncer()` advances processing under memory pressure or dependency pressure by increasing the global `rushjob` sequence and waking a mount's syncer context.
- `vsyncscan()` scans only syncer-list vnodes rather than the full mount vnode list, which is critical for mounts with very large vnode populations.

## Cross-File Relationships

- `vfs_subr.c` calls `vn_syncer_add()`, `vn_syncer_remove()`, `vclrobjdirty()`, and `vsyncscan()` while moving buffers and cleaning VM pages.
- `vfs_syscalls.c` allocates a syncer vnode during successful mount and decommissions it during unmount.
- `vfs_vfsops.c` stops syncer threads after a successful filesystem unmount wrapper call.
- Filesystem implementations interact through vnode dirty flags, `VOP_FSYNC()`, and mount flags such as `MNTK_THR_SYNC`, `MNTK_NOMSYNC`, and `MNT_RDONLY`.

## Research Notes

- The syncer is a central delayed-write policy component. It intentionally trades immediate persistence for batching, retry, and reduced churn from short-lived files.
- The most important correctness invariants are `VONWORKLST` membership consistency, token discipline around the time wheel, syncer vnode teardown during unmount, and avoiding full vnode-list scans on filesystems that opt into threaded sync.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/vfs_sync.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/vfs_synth.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/vfs_synth.c

## Role

This small file creates and exposes a synthetic devfs-backed lookup root used to obtain device vnodes by name from kernel code. It mounts a private devfs instance during VFS initialization and provides `getsynthvnode()` as the lookup interface.

## Main Responsibilities

- Maintains global synthetic devfs state:
  - `synth_mp`
  - `synth_vp`
  - `synth_inited`
  - `synth_synced`
- Initializes a dummy devfs mount in `synthinit()`:
  - Allocates a root mount with `vfs_rootmountalloc("devfs", "dummy", &synth_mp)`.
  - Mounts it through `VFS_MOUNT()`.
  - Obtains its root vnode through `VFS_ROOT()`.
  - Allocates the mount root namecache handle with `cache_allocroot()`.
  - Drops the temporary root vnode lock/reference and marks the synthetic layer initialized.
- Resolves device names with `getsynthvnode()`:
  - Asserts the synthetic mount is initialized.
  - Calls `sync_devs()` on the first two lookups to ensure devfs/disks are populated.
  - Performs `nlookup_init_root()` relative to the synthetic devfs root.
  - Returns a VX-locked/refd vnode via `vget(vp, LK_EXCLUSIVE)`.

## Synchronization and Lifetime Model

- Initialization is performed via `SYSINIT(synthinit, SI_SUB_VFS, SI_ORDER_ANY, ...)`, so callers expect the synthetic mount to exist after VFS startup.
- `getsynthvnode()` transfers the namecache result out of `nlookupdata`, then unlocks the namecache handle after `vget()`.
- The returned vnode is locked and referenced; callers must release it with the normal vnode path.

## Cross-File Relationships

- Uses the general mount operation wrappers/macros implemented around `VFS_MOUNT()` and `VFS_ROOT()`.
- Relies on DragonFly namecache/nlookup primitives that are heavily used by `vfs_syscalls.c`.
- Produces regular vnodes that flow into the same vnode lifecycle machinery described in `vfs_subr.c`.

## Research Notes

- This is a specialized kernel convenience layer, not a general synthetic filesystem implementation.
- Error handling is intentionally strict during init: failure to allocate, mount, or root the devfs instance panics.
- Runtime lookup failures are nonfatal and return `NULL`, with warnings for errors other than `ENOENT`.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/vfs_synth.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/vfs_syscalls.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/vfs_syscalls.c

## Role

This is the main VFS syscall implementation file. It translates user-visible filesystem syscalls into DragonFly's namecache, mount, vnode, VOP, and VFS operation layers. It contains mount/unmount, statfs/statvfs, path traversal state changes, file creation/removal/link/rename, attribute changes, timestamps, truncation, fsync, directory reading, filehandle operations, extended attributes, realpath, and posix fallocate.

## Main Responsibilities

- Mount lifecycle:
  - `sys_mount()` handles privilege/capability checks, user mounts, jail restrictions, module autoload, mount updates, new mount allocation, `VFS_MOUNT()`, mount-list insertion, root namecache setup, `checkdirs()`, syncer vnode allocation, and `VFS_START()`.
  - `sys_unmount()` resolves the target and calls `dounmount()`.
  - `dounmount()` serializes unmount, handles forced unmount process cleanup, syncs, stops/decommissions the syncer vnode, calls `VFS_UNMOUNT()`, tears down journals, vnode ops, namecache mount handles, credentials, mount refs, and notifies kqueue.
  - `vfs_unmountall()` is in `vfs_subr.c`, but its callback uses `dounmount()` from this file.
- Mount and filesystem control/statistics:
  - `sys_sync()`, `sync_callback()`
  - `sys_quotactl()`
  - `sys_mountctl()` and `kern_mountctl()`
  - `kern_statfs()`, `sys_statfs()`, `kern_fstatfs()`, `sys_fstatfs()`
  - `kern_statvfs()`, `sys_statvfs()`, `kern_fstatvfs()`, `sys_fstatvfs()`
  - `sys_getfsstat()` and `sys_getvfsstat()`
- Current/root directory changes:
  - `sys_fchdir()`, `kern_chdir()`, `sys_chdir()`
  - `kern_chroot()`, `sys_chroot()`, `sys_chroot_kernel()`
  - `checkvp_chdir()` validates directory and execute access.
  - `chroot_refuse_vdir_fds()` and `chroot_allow_open_directories` mitigate fchdir-based chroot escapes.
- Open and node creation:
  - `kern_open()`, `sys_open()`, `sys_openat()`
  - `kern_mknod()`, `sys_mknod()`, `sys_mknodat()`
  - `kern_mkfifo()`, `sys_mkfifo()`, `sys_mkfifoat()`
  - `kern_mkdir()`, `sys_mkdir()`, `sys_mkdirat()`
- Links, symlinks, rename, and deletion:
  - `kern_link()`, `sys_link()`, `sys_linkat()`
  - `kern_symlink()`, `sys_symlink()`, `sys_symlinkat()`
  - `sys_undelete()`
  - `kern_unlink()`, `sys_unlink()`, `sys_unlinkat()`
  - `kern_rename()`, `sys_rename()`, `sys_renameat()`
  - `kern_rmdir()`, `sys_rmdir()`
- Access, stat, pathconf, readlink:
  - `kern_access()`, `sys_access()`, `sys_eaccess()`, `sys_faccessat()`
  - `kern_stat()`, `sys_stat()`, `sys_lstat()`, `sys_fstatat()`
  - `sys_pathconf()`, `sys_lpathconf()`
  - `kern_readlink()`, `sys_readlink()`, `sys_readlinkat()`
- Attribute mutation:
  - `setfflags()`, `sys_chflags()`, `sys_lchflags()`, `sys_fchflags()`, `sys_chflagsat()`
  - `setfmode()`, `kern_chmod()`, chmod syscall variants
  - `setfown()`, `kern_chown()`, chown syscall variants
  - `getutimes()`, `getutimens()`, `setutimes()`, `kern_utimes()`, `kern_futimens()`, `kern_futimes()`, `kern_utimensat()`, and all utimes/futimes/utimens syscall variants.
- File size and persistence:
  - `kern_truncate()`, `sys_truncate()`
  - `kern_ftruncate()`, `sys_ftruncate()`
  - `kern_fsync()`, `sys_fsync()`, `sys_fdatasync()`
- Directory and descriptor utilities:
  - `kern_lseek()`, `sys_lseek()`
  - `kern_getdirentries()`, `sys_getdirentries()`, `sys_getdents()`
  - `sys_umask()`
- Revocation and NFS filehandles:
  - `sys_revoke()`
  - `sys_getfh()`
  - `sys_fhopen()`
  - `sys_fhstat()`
  - `sys_fhstatfs()`
  - `sys_fhstatvfs()`
- Extended attributes:
  - `sys_extattrctl()`
  - `sys_extattr_set_file()`
  - `sys_extattr_get_file()`
  - `sys_extattr_delete_file()`
- Path visibility and capability helpers:
  - `chroot_visible_mnt()`
  - `get_fscap()`
  - `sys___realpath()`
  - `kern_posix_fallocate()` and `sys_posix_fallocate()`

## Synchronization and Lifetime Model

- Name resolution is built around `struct nlookupdata` and `struct nchandle`; syscalls initialize lookup context, set flags such as `NLC_FOLLOW`, `NLC_CREATE`, `NLC_DELETE`, `NLC_REFDVP`, `NLC_SHAREDLOCK`, and then release through `nlookup_done()` or `nlookup_done_at()`.
- Vnode references and locks are handled explicitly through `cache_vget()`, `cache_vref()`, `vget()`, `vput()`, `vrele()`, `vn_lock()`, and `vn_unlock()`.
- Mount lifetime is protected through mount holds/drops, mount busy/unbusy, the mount list interlock, `mp->mnt_token`, and `mp->mnt_lock`.
- File descriptor operations use `holdfp()`, `holdvnode()`, `falloc()`, `fdalloc()`, `fsetfd()`, `fdrop()`, and `dropfp()`.
- Forced unmount scans all processes, drops matching text namecache handles, and may signal processes using the mount.
- Rename has extensive race handling: it tracks namecache generation counters, locks four namecache entries, retries on generation/ripout races, uses `mnt_renlock` for directory renames, and rejects mount point renames.

## Notable Design Details

- `sys_mount()` chooses capabilities based on filesystem type using `get_fscap()`, enforces jail restrictions for user mounts, prevents non-root NFS export, and silently adds `MNT_NOSUID | MNT_NODEV` for non-root mounts.
- Mount updates preserve previous `mnt_flag` and `mnt_kern_flag` so failed updates can roll back.
- `dounmount()` supports a quick-halt path for selected pseudo filesystems through `MNTK_QUICKHALT`.
- `checkdirs()` updates process current/root directories when a new filesystem is mounted over a directory already used by processes.
- Statfs paths are adjusted through `mount_path()` so chrooted processes see mount paths relative to their root.
- `getfsstat` and filehandle statfs paths filter mount visibility with `chroot_visible_mnt()`.
- `kern_open()` lets `vn_open()` replace the allocated file pointer, supports shared vnode locks where possible, and handles `O_EXLOCK`/`O_SHLOCK`.
- Hardlink restrictions are controlled by `security.hardlink_check_uid` and `security.hardlink_check_gid`.
- `kern_access()` and `kern_stat()` retry after `ESTALE` by forcing namecache re-resolution.
- `kern_fsync()` cleans VM pages first unless the mount has `MNTK_NOMSYNC`, then calls full or data-only VOP fsync and finally `buf_fsync()`.
- `sys_fhopen()` is explicitly protected by a restricted-root capability check because filehandle-to-open is a major security boundary.

## Cross-File Relationships

- Uses `vinvalbuf()`, `vfs_msync()`, `vcount()`, `vrevoke()`, `vfs_allocate_syncvnode()`, and many vnode helpers from `vfs_subr.c`.
- Uses syncer lifecycle and syncer vnode behavior from `vfs_sync.c`.
- Uses operation wrappers implemented in `vfs_vfsops.c` through `VFS_MOUNT()`, `VFS_START()`, `VFS_UNMOUNT()`, `VFS_STATFS()`, `VFS_STATVFS()`, `VFS_FHTOVP()`, `VFS_VPTOFH()`, and `VFS_EXTATTRCTL()`.
- Depends on VM coherency through `vfs_msync()`, vnode objects, and filesystem-specific VOP truncate/allocation behavior that may call into `vfs_vm.c`.

## Research Notes

- This file is the syscall boundary for most VFS behavior, so it combines user-copy validation, capability checks, path resolution, vnode locking, filesystem calls, and cleanup.
- The highest-risk areas are unmount teardown, rename races, chroot visibility/security, filehandle syscalls, mount update rollback, and descriptor/vnode reference ownership on error paths.
- The code heavily prefers shared `kern_*` helpers so classic syscalls and `*at` variants share semantics.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/vfs_syscalls.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/vfs_vfsops.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/vfs_vfsops.c

## Role

This file implements the wrapper functions for mount-level VFS operations stored in `mp->mnt_op` or `vfc->vfc_vfsops`. Its main job is to centralize MPSAFE handling around filesystem VFS callbacks.

## Main Responsibilities

- Wraps mount operations:
  - `vfs_mount()`
  - `vfs_start()`
  - `vfs_unmount()`
  - `vfs_root()`
  - `vfs_quotactl()`
  - `vfs_statfs()`
  - `vfs_statvfs()`
  - `vfs_sync()`
  - `vfs_vget()`
  - `vfs_fhtovp()`
  - `vfs_checkexp()`
  - `vfs_vptofh()`
  - `vfs_extattrctl()`
- Wraps filesystem type lifecycle operations:
  - `vfs_init()`
  - `vfs_uninit()`
- Handles mount credentials during mount:
  - `vfs_mount()` stores a held credential in `mp->mnt_cred` if not already present, preserving jail/prison association.
- Handles accounting lifecycle:
  - `vfs_start()` calls `VFS_ACINIT()` for non-update mounts after successful start.
  - `vfs_unmount()` calls `VFS_ACDONE()` before invoking filesystem unmount.
- Stops the per-mount syncer thread after a successful filesystem unmount.

## Synchronization and MPSAFE Model

- Most wrappers use `VFS_MPLOCK_DECLARE`, `VFS_MPLOCK()`, `VFS_MPLOCK_FLAG()`, and `VFS_MPUNLOCK()` around the underlying filesystem callback.
- `vfs_start()` uses `VFS_MPLOCK_FLAG(mp, MNTK_ST_MPSAFE)`, allowing a distinct MPSAFE flag for start operations.
- `vfs_init()` and `vfs_uninit()` call filesystem type operations directly rather than locking a mount.

## Notable Design Details

- `vfs_start()` translates `EMOUNTEXIT` to success after the callback, matching DragonFly's mount-start control semantics.
- `vfs_unmount()` captures `mp->mnt_kern_flag` into a local `flags` variable but does not use it; this appears to be vestigial or preserved for debug/build history.
- `vfs_vptofh()` locks based on `vp->v_mount`, since the operation is vnode-derived rather than passed a mount explicitly.

## Cross-File Relationships

- These wrappers are the concrete functions behind many `VFS_*` macro calls used by `vfs_syscalls.c`, `vfs_subr.c`, and `vfs_synth.c`.
- `vfs_unmount()` interacts with the syncer infrastructure from `vfs_sync.c` by calling `vn_syncer_thr_stop()` after successful unmount.
- `vfs_mount()` stores mount credentials later used by jail and unmount visibility checks in `vfs_syscalls.c`.

## Research Notes

- This is a small but important abstraction layer. It ensures filesystem implementations do not each duplicate MP-lock wrapping and mount accounting hooks.
- Changes here affect every filesystem VFS operation dispatch path.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/vfs_vfsops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/vfs_vm.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/vfs_vm.c

## Role

This file implements newer VFS/VM coherency helpers for truncating and extending vnode-backed files. It keeps VM object sizing aligned with the final buffer cache buffer rather than the exact byte EOF, simplifying interactions for filesystems with fixed-size or offset-based buffers such as NFS and HAMMER.

## Main Responsibilities

- Provides `nvtruncbuf()` for truncation:
  - Computes the logical offset beyond which buffers must be destroyed.
  - Removes clean and dirty buffers beyond the new EOF-covering buffer.
  - Calls `nvnode_pager_setsize()` to update vnode and VM object size.
  - Zero-fills the portion of the last buffer beyond EOF unless `NVEXTF_TRIVIAL` is set.
  - Optionally writes the zero-filled buffer with `buwrite()` when `NVEXTF_BUWRITE` is set, otherwise uses `bdwrite()`.
  - Fsyncs remaining metadata buffers with negative logical offsets for nonzero truncations.
  - Waits for tracked writes and repeats cleanup to catch buffers instantiated by concurrent VM/page activity.
- Provides `nvextendbuf()` for extension:
  - Updates VM object sizing with `nvnode_pager_setsize()`.
  - Zero-fills the old EOF-straddling buffer unless `NVEXTF_TRIVIAL` is set.
  - Clears cached raw disk offsets so future writes remap correctly.
- Provides `nvnode_pager_setsize()`:
  - Updates `vp->v_filesize`.
  - Sets `vp->v_object->size` to include the last buffer containing EOF.
  - Removes VM pages beyond the last EOF-covering buffer on shrink.
  - Unmaps user-visible pages beyond the byte-granular EOF while preserving pages still covered by the last buffer.

## Synchronization and Lifetime Model

- `nvtruncbuf()` takes `vp->v_token` while scanning buffer trees.
- Buffer callbacks lock each buffer, revalidate clean/dirty state, vnode ownership, and logical offset after lock acquisition, then invalidate or write as needed.
- `nvnode_pager_setsize()` holds the VM object while adjusting object size and pages.
- VM page unmapping loops use `vm_page_lookup_busy_wait()`, `vm_page_protect(VM_PROT_NONE)`, `vm_page_wakeup()`, and `lwkt_yield()` to avoid long monopolization.

## Notable Design Details

- The VM object may remain larger than byte EOF so it covers the full last buffer. Userland faults beyond EOF are prevented by unmapping/protecting pages rather than invalidating the buffer-covered VM pages.
- Zero-filling uses delayed/write-behind semantics to avoid races where a clean buffer could be discarded and reread before the filesystem completes allocation or truncation.
- Dirty range fields are adjusted when zeroing a buffer already marked `B_DELWRI`.
- Both truncation and extension clear `bp->b_bio2.bio_offset` to `NOOFFSET`, forcing remapping for filesystems that avoid overwriting existing physical blocks.

## Cross-File Relationships

- This file is the newer counterpart to `vtruncbuf()` and `vnode_pager_setsize()` paths still present in `vfs_subr.c`.
- Filesystem implementations call these helpers when they adopt the newer VFS/VM coherency contract.
- It depends on the same vnode buffer trees and buffer flags maintained by `bgetvp()`, `brelvp()`, and `reassignbuf()` in `vfs_subr.c`.
- It participates in the same dirty-buffer and write-tracking ecosystem used by `vfs_sync.c`.

## Research Notes

- The key semantic point is buffer-granular VM object coverage with page-granular user visibility enforcement.
- High-risk areas are partial-buffer zeroing, dirty range preservation, concurrent buffer instantiation during VM cleanup, and filesystems passing correct old/new block sizes and block offsets.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/vfs_vm.c -->