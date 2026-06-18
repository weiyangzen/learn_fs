# File Research: sources/cow-pools/openzfs/module/os/freebsd/zfs/zfs_vfsops.c

## Purpose

Implements the FreeBSD VFS integration layer for ZFS. It defines ZFS mount operations, filesystem setup/teardown, property callbacks, quota handling, statfs/root/vget/export support, suspend/resume for rollback/receive, module initialization/finalization, and jail-specific ZFS parameters.

## VFS Registration and Global State

- Defines `struct vfsops zfs_vfsops` with:
  - mount, unmount, root, cached root, statfs, vget, sync, check export, file-handle-to-vnode, and quotactl hooks.
- Registers with `VFS_SET(zfs_vfsops, zfs, VFCF_DELEGADMIN | VFCF_JAIL | optional flags)`.
- Sysctls:
  - `vfs.zfs.super_owner`
  - `vfs.zfs.debug`
  - `vfs.zfs.version.acl`
  - `vfs.zfs.version.spa`
  - `vfs.zfs.version.zpl`
- Tracks mounted filesystems through `zfs_active_fs_count`.

## Temporary Property and Quota Support

- `zfs_get_temporary_prop()`
  - Reads mount-option overrides for properties such as atime, devices, exec, setuid, readonly, xattr, and nbmand.
  - Reports `"temporary"` as setpoint when a mount option overrides the dataset value.
- `zfs_getquota()`
  - Reads user/group quota and used ZAP objects.
  - Falls back to default user/group quota when no explicit quota exists.
  - Fills FreeBSD `dqblk64`.
- `zfs_quotactl()`
  - Maps FreeBSD quota commands/types to ZFS user/group quota properties.
  - Supports quota size query, quota-on as no-op, quota-off as unsupported, set quota, and get quota.
  - Uses `zfs_enter()`/`zfs_exit()` around operations.

## Sync and Readonly

- `zfs_is_readonly()`
  - Checks `VFS_RDONLY`.
- `zfs_sync()`
  - No-ops during panic and for `MNT_LAZY`.
  - For one filesystem, commits ZIL unless rebooting with suspended pool.
  - For global sync, calls `spa_sync_allpools()`.

## Property Callbacks

Registered callbacks keep `zfsvfs_t` and FreeBSD mount flags/options aligned with dataset properties:

- `atime_changed_cb()`
- `relatime_changed_cb()`
- `xattr_changed_cb()`
- `blksz_changed_cb()`
- `readonly_changed_cb()`
- `setuid_changed_cb()`
- `exec_changed_cb()`
- `nbmand_changed_cb()`
- `snapdir_changed_cb()`
- `acl_mode_changed_cb()`
- `acl_inherit_changed_cb()`
- `acl_type_changed_cb()`
- `longname_changed_cb()`

`zfs_register_callbacks()` preserves explicit mount-option overrides, registers DSL property callbacks, handles `nbmand` specially under DSL pool config lock, and restores temporary mount option state after registration.

## zfsvfs Creation and Setup

- `zfsvfs_init()`
  - Reads on-disk ZPL state into `zfsvfs_t`:
    - ZPL version, normalization, UTF-8-only, case mode, ACL type.
    - FUID and SA feature use.
    - default user/group/project quotas and object quotas.
    - root object, unlinked set, quota objects, FUID object, shares directory.
  - Sets up SA framework and optional SA upgrade callback.
  - Determines `z_use_namecache` based on normalization/case rules.
- `zfsvfs_create()`
  - Rejects overly long dataset names for FreeBSD `statfs.f_mntfromname`.
  - Owns the DMU objset with readonly forced for snapshots.
- `zfsvfs_create_impl()`
  - Initializes locks, znode list, teardown locks, FUID lock, object hold mutexes, and unlinked-drain task.
  - Calls `zfsvfs_init()`.
- `zfsvfs_setup()`
  - Rejects writes to incompatible encrypted objsets.
  - Registers callbacks.
  - On mounting:
    - Creates dataset kstats.
    - Opens ZIL.
    - Temporarily clears readonly during replay.
    - Drains unlinked set for writable filesystems.
    - Replays or destroys ZIL depending on `zil_replay_disable`.
  - Sets objset user pointer to `zfsvfs`.

## Mount Flow

- `zfs_mount()`
  - Reads dataset name from `from` option.
  - Handles delegated administration and `zfs_super_owner`.
  - Parses leading `!` as checkpoint rewind request.
  - Allows certain `.zfs` snapshot mounts with jail parameter permission.
  - Enforces privilege, delegated mount permission, mountpoint ownership/write checks, and jail dataset visibility.
  - Handles remount by re-registering callbacks under teardown write lock.
  - For root mount, imports the root pool with optional checkpoint rewind.
  - Calls `zfs_domount()`.
- `zfs_domount()`
  - Creates `zfsvfs`, attaches it to the mount, sets FreeBSD mount flags, constructs fsid, and initializes feature flags.
  - For snapshots:
    - Forces noatime and readonly.
    - Reads xattr and acltype properties.
    - Marks `z_issnap`.
    - Disables objset sync.
  - For normal filesystems, calls `zfsvfs_setup()`.
  - Enables named attributes on newer FreeBSD when compatible.
  - Sets mounted-from name and creates `.zfs` control directory for non-snapshots.
  - Increments active filesystem count on success.

## Unmount and Teardown

- `zfsvfs_teardown()`
  - Waits for zrele taskq progress.
  - Takes teardown locks.
  - Purges name cache when not unmounting.
  - Closes ZIL.
  - Finalizes znode DMU handles.
  - On unmount, marks `z_unmounted` and releases teardown locks.
  - Unregisters property callbacks, syncs dirty objsets when needed, evicts dbufs, and cancels DSL directory waiters.
- `zfs_umount()`
  - Checks unmount privilege or delegated mount permission.
  - Unmounts snapshots under `.zfs`.
  - For forced unmount, marks filesystem unmounted before `vflush(FORCECLOSE)`.
  - Flushes vnodes, cancels/drains deferred unlinked drain task, tears down `zfsvfs`, clears objset user pointer, disowns objset, destroys `.zfs`, and frees VFS state.
- `zfs_freevfs()`
  - Frees `zfsvfs` and decrements active count.

## VFS Operations

- `zfs_statfs()`
  - Reports ZFS capacity, available blocks, object counts, fs type, mount names, and max filename length.
- `zfs_root()`
  - Fetches root znode by `zfsvfs->z_root`, then locks and returns the vnode.
- `zfs_vget()`
  - Converts inode/object number to vnode.
  - Refuses virtual `.zfs` entries and shares directory with `EOPNOTSUPP` for NFS fallback.
  - Rejects unlinked znodes.
  - Sets named-attribute vnode flags on newer FreeBSD.
- `zfs_checkexp()`
  - Delegates export checks to parent filesystem mount for snapshots.
- `zfs_fhtovp()`
  - Converts short/long ZFS file handles into vnodes.
  - Handles snapshot objset ids in long fids through `zfsctl_lookup_objset()`.
  - Handles `.zfs` and snapshot directory virtual objects through control-directory lookup.
  - Validates object generation against file-handle generation.
  - Creates vnode VM object before returning.

## Suspend, Resume, and End

- `zfs_suspend_fs()`
  - Blocks VOPs and tears down `z_os` for rollback/receive style operations, leaving teardown locks held on success.
- `zfs_resume_fs(zfsvfs_t *zfsvfs, dsl_dataset_t *ds)`
  - Reacquires objset from the owned dataset.
  - Reinitializes zfsvfs and setup state.
  - Reopens ZIL and callbacks.
  - Attempts `zfs_rezget()` on all active znodes.
  - Releases teardown locks.
  - Forces unmount if setup fails.
- `zfs_end_fs()`
  - Releases teardown locks and force-unmounts a suspended filesystem.
  - Marks it unmounted.

## Version and Default Quota Mutation

- `zfs_set_version()`
  - Validates requested ZPL version.
  - Updates `ZPL_VERSION_STR`.
  - Creates SA master object and registers SA upgrade callback when upgrading to SA support.
  - Logs history and updates in-memory version/feature flags.
- `zfs_set_default_quota()`
  - Updates or removes default quota properties in `MASTER_NODE_OBJ`.
  - Updates corresponding cached `zfsvfs` default quota field.

## Module Lifecycle and ARC/Vnode Pressure

- `zfs_init()`
  - Prints filesystem version.
  - Initializes `.zfs`, znode cache/vnode ops, i386 vnode tuning, DMU objset type handler, `zfsvfs_taskq`, VNLRU marker/lock, and ARC prune callback.
- `zfs_fini()`
  - Removes prune callback, frees marker, destroys lock/taskq, finalizes `.zfs` and znodes, and restores vnode tuning.
- `zfs_busy()`
  - Reports whether any ZFS filesystems remain active.
- `zfs_prune_task()`
  - Called by ARC pruning to free ZFS vnodes through FreeBSD VNLRU.

## Jail Parameters

- Defines per-prison `struct zfs_jailparam` with `mount_snapshot`.
- Provides OSD jail methods:
  - create, get, set, check, destroy.
- Supports `zfs=inherit/new` and `zfs.mount_snapshot`.
- Prevents child jails from gaining more snapshot-mount permission than parent.
- Registers/deregisters jail OSD slot through `SYSINIT`/`SYSUNINIT`.

## Rename/Mount Name Support

- `zfsvfs_update_fromname()`
  - Walks FreeBSD mount list and updates `f_mntfromname` for renamed datasets and descendants/snapshots.

## Important Cross-File Interactions

- Calls `zfs_unlinked_drain()` from `zfs_dir.c`.
- Creates and destroys `.zfs` control directory via `zfsctl_*`.
- Depends on znode initialization and lookup functions from FreeBSD ZFS vnode/znode layers.
- Coordinates with DSL/DMU/ZIL/SPA layers for objset ownership, property callbacks, replay, sync, and pool state.
