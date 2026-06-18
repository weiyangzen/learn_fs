# File Research: sources/cow-pools/openzfs/module/os/linux/zfs/zfs_vfsops.c

## Read Coverage
Read completely: 2,064 lines, 54,500 bytes.

## Purpose
`zfs_vfsops.c` is the Linux superblock/VFS lifecycle layer for OpenZFS ZPL datasets. It owns the mount-time construction of `zfsvfs_t`, dataset ownership, property callback wiring, root inode setup, ZIL replay, unmount teardown, suspend/resume for rollback/receive, statfs reporting, export file-handle lookup, and module filesystem registration.

## Major Responsibilities
- Allocates and frees Linux-side `vfs_t` mount option containers and `zfsvfs_t` filesystem state.
- Loads ZPL properties and master-node object IDs into `zfsvfs_t`, including root, unlinked set, FUID tables, quota objects, shares directory, normalization, case behavior, SA usage, and xattr mode.
- Registers DSL property callbacks for mounted datasets and maps selected ZFS properties into Linux superblock state.
- Sets up mounted filesystems by creating dataset kstats, opening the ZIL, draining the unlinked set, replaying intent logs, and installing the objset user pointer.
- Implements `zfs_domount()`, `zfs_preumount()`, `zfs_umount()`, and `zfs_remount()` around Linux `struct super_block`.
- Handles ARC-driven dentry/inode pruning and manual alias pruning when kernel shrinkers cannot reclaim enough.
- Implements `statfs`, project quota-aware statfs overrides, root lookup, NFS/export `vget`, and snapshot control-directory file-handle handling.
- Implements mounted filesystem suspend/resume/end paths used by rollback and receive.
- Registers and unregisters the ZPL filesystem type and znode/control-directory subsystems.

## Key Data and Interfaces
- `zfsvfs_t` is the central mounted-dataset state, binding `objset_t`, Linux `super_block`, ZIL, property-derived policy, znode lists, per-object hold locks, kstats, and teardown locks.
- `vfs_t` stores temporary mount-option overrides that can differ from persistent dataset properties.
- `struct super_block` receives ZFS-specific operations: `zpl_super_operations`, `zpl_xattr_handlers`, `zpl_export_operations`, and `zpl_dentry_operations`.
- Uses DSL/DMU interfaces including `dmu_objset_own()`, `dmu_objset_disown()`, `dmu_objset_set_user()`, `zap_lookup()`, `zfs_get_zplprop()`, `sa_setup()`, and `dsl_prop_register()`.
- Uses ZIL interfaces `zil_open()`, `zil_replay()`, `zil_commit_flags()`, `zil_destroy()`, and `zil_close()`.
- Uses Linux shrinker, dentry, inode, backing-device, and mount flags through `super_setup_bdi_name()`, `shrink_dcache_sb()`, `d_prune_aliases()`, `igrab()`, and superblock flag updates.

## Control Flow Highlights
- `zfs_register_callbacks()` preserves temporary mount-option overrides, registers dataset property callbacks, then reapplies the temporary values so mounted behavior can differ from persistent properties.
- `zfsvfs_init()` loads all persistent ZPL metadata and validates dataset/pool compatibility before the filesystem is usable.
- `zfsvfs_create()` owns the dataset and delegates construction to `zfsvfs_create_impl()`, which initializes znode lists, teardown locks, FUID locks, and per-object znode hold AVL trees.
- `zfsvfs_setup()` opens the ZIL, optionally clears readonly during replay, drains the unlinked set before replay, replays the ZIL when enabled and writeable, restores readonly, and installs `os_user_ptr`.
- `zfs_domount()` enforces zone visibility/writeability, handles snapshots as read-only non-replayed mounts, wires superblock operations, creates the root dentry, creates `.zfs` control state for live datasets, and registers ARC prune callbacks.
- `zfsvfs_teardown()` stops unlinked draining, waits for async `zrele` work, blocks VFS operations, closes the ZIL, optionally detaches SA handles for suspended filesystems, marks unmounted state, unregisters properties, waits for dirty txgs, evicts dbufs, and cancels DSL directory waiters.
- `zfs_resume_fs()` rebuilds `zfsvfs_t` state against a refreshed objset, reopens callbacks/ZIL, revalidates every active znode with `zfs_rezget()`, unhashes stale inodes, clears suspended references asynchronously, restarts unlinked draining, and drops cached negative dentries.
- `zfs_vget()` decodes short and long ZFS file handles, handles `.zfs` control/snapshot synthetic IDs, rejects xattr objects, verifies generation numbers, and returns a held inode.

## Important Functions
- `zfsvfs_init()` caches ZPL on-disk properties and master-node object IDs into `zfsvfs_t`.
- `zfsvfs_create()` and `zfsvfs_create_impl()` allocate and initialize mounted filesystem state after owning an objset.
- `zfsvfs_setup()` performs mount or resume setup, including unlinked draining and ZIL replay/opening.
- `zfs_domount()` is the main Linux mount entry point.
- `zfs_preumount()`, `zfs_umount()`, and `zfsvfs_teardown()` implement unmount ordering and final release.
- `zfs_remount()` swaps temporary mount options and refreshes callbacks.
- `zfs_statvfs()` and `zfs_statfs_project()` report filesystem and project-quota-limited capacity.
- `zfs_prune()` and `zfs_prune_aliases()` coordinate ARC pressure with Linux inode/dentry reclaim.
- `zfs_suspend_fs()`, `zfs_resume_fs()`, and `zfs_end_fs()` support rollback/receive transitions.
- `zfs_set_version()` and `zfs_set_default_quota()` mutate ZPL version/default quota properties transactionally.
- `zfs_init()` and `zfs_fini()` register/unregister the Linux ZPL filesystem type.

## Invariants and Assumptions
- Mounted VFS operations must be blocked through teardown locks before SA handles, dbufs, ZIL state, or objset ownership are invalidated.
- `zfsvfs->z_os` is owned by the `zfsvfs_t` while the filesystem is mounted or suspended.
- `os_user_ptr` is the active bridge from an objset back to its mounted `zfsvfs_t`; it must be set during setup and cleared during unmount.
- Snapshots are mounted read-only, skip normal ZIL setup/replay, and use deferred unmount timing through snapshot control-directory code.
- Unlinked-set draining must happen before ZIL replay for correctness under ziltest and object reuse scenarios.
- Active znodes must be pinned or processed asynchronously while suspend/resume walks `z_all_znodes`.
- Temporary mount options are represented in `vfs_t` and must survive property callback registration.

## Risks and Edge Cases
- Mount failure paths must avoid double-freeing `zfsvfs_t`, `vfs_t`, objset ownership, and `sb->s_fs_info`.
- Teardown ordering is subtle: async `iput()`, inactive processing, ZIL close, dbuf eviction, and VFS operation blocking can deadlock if reordered.
- Rollback/receive resume can encounter active inodes whose object number now refers to different contents; stale inodes must be unhashed safely.
- Export file handles must distinguish real objects from `.zfs` control-directory synthetic objects and verify generation masks.
- ARC pruning relies on kernel shrinker behavior but has a manual fallback for non-root memory cgroup references.
- Project-quota statfs reporting can observe async accounting races and falls back to estimated object/block usage.
- Readonly handling is layered: persistent readonly property, snapshot status, zone writeability, remount flags, and temporary mount options can all affect behavior.

## Testing Signals
Useful coverage should include:
- Mount and unmount of normal datasets, snapshots, readonly datasets, non-writeable pools, and datasets hidden from a zone.
- Mount failure injection around objset ownership, property lookup, BDI setup, root inode allocation, root dentry allocation, ZIL setup, and callback registration.
- ZIL replay enabled/disabled paths and unlinked-set draining before replay.
- Remount transitions between read-write and read-only, including txg sync on read-only transition.
- Rollback/receive suspend and resume with active files, deleted files, negative dentries, stale object generations, and in-flight async `zrele`.
- NFS/export file-handle lookup for root, normal files, stale generations, xattrs, `.zfs`, and snapshot directories.
- `statfs` with and without project quota, default project quota, project object quota, and async accounting gaps.
- ARC prune callback behavior under memory pressure and when kernel shrinkers reclaim nothing.

## Overall Assessment
This file is the Linux mounted-filesystem control plane for OpenZFS. It does not implement most file operations directly; instead it establishes the safe execution environment for them by owning dataset state, ZIL lifecycle, property policy, superblock wiring, teardown locks, znode hold tables, and rollback/receive transitions. Regressions here tend to be severe: failed mounts, unsafe unmounts, stale inodes after rollback, broken snapshot export behavior, or deadlocks between VFS reclaim, async inode release, and ZFS teardown.
