# File Research: sources/cow-pools/openzfs/lib/libzfs/libzfs_mount.c

## Scope

Implements libzfs mount, unmount, share, unshare, pool-wide dataset enable/disable, mountpoint ordering, and namespace-property support.

## APIs And Behavior

- `zfs_is_namespace_prop()` and `zfs_namespace_prop_flag()` identify properties that require mount namespace updates.
- `is_mounted()` and `zfs_is_mounted()` query the libzfs mnttab cache.
- `zfs_is_mountable()` rejects non-filesystems, `mountpoint=none/legacy`, `canmount=off`, global-zone attempts for zoned datasets, and redacted datasets unless forced.
- `zfs_mount()` and `zfs_mount_at()` build mount options from properties, force readonly for readonly-imported pools, optionally load encryption keys, add `zfsutil`, create mountpoint directories, enforce overlay/empty-directory rules, call `do_mount()`, and update the mnttab cache.
- `zfs_unmount()` unshares first, unmounts with `do_unmount()`, updates the cache, optionally unloads encryption-root keys, and disables zvol OS state.
- `zfs_unmountall()` and `zfs_unshareall()` use changelists for recursive mount/share-sensitive teardown.
- `zfs_share()`, `zfs_is_shared()`, `zfs_unshare()`, `zfs_commit_shares()`, and `zfs_truncate_shares()` wrap libshare NFS/SMB protocol operations based on `sharenfs` and `sharesmb`.
- `remove_mountpoint()` removes default or inherited mountpoint directories after dataset destruction/disable.
- `zpool_enable_datasets()` gathers eligible filesystems, mounts them in mountpoint order with optional parallelism, then serially shares them.
- `zpool_disable_datasets()` walks current mnttab entries for a pool, sorts mountpoints deepest-first, unshares, unmounts, removes eligible directories, and calls OS-specific disable logic.
- `zfs_foreach_mountpoint()` sorts by mountpoint and zone state, then dispatches callbacks serially or through a taskq that preserves parent-before-child mount ordering.

## State And Dependencies

The file depends on mnttab cache helpers, libshare, zone APIs, crypto key helpers, zpool properties, OS-specific `do_mount()`/`do_unmount()`/zvol hooks, changelists, task queues, mount constants, and filesystem stat/readdir calls.

## Risks And Invariants

Parent mountpoints must be processed before descendants; the custom comparator and task dispatch logic enforce that. Libshare is treated as not thread-safe, so sharing is serialized even when mounting is parallel. Mount option synthesis deliberately avoids current mount-option overrides by reading raw property nvlists. Unmount failures attempt to restore sharing where possible.
