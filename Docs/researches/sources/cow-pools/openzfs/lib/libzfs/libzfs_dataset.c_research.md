# File Research: sources/cow-pools/openzfs/lib/libzfs/libzfs_dataset.c

## Scope

Core libzfs dataset implementation. It validates dataset/snapshot/bookmark names, opens and duplicates dataset handles, loads objset/property state, validates and sets properties, creates/destroys/clones/promotes/snapshots/rolls back/renames datasets, manages holds and delegated permissions, handles user/group/project quota properties, and computes zvol reservation sizing.

## APIs And Behavior

- `zfs_validate_name()`, `zfs_name_valid()`, and helpers enforce ZFS dataset, snapshot, bookmark, and pool naming rules with specific libzfs auxiliary errors.
- `make_dataset_handle()`, `make_dataset_handle_zc()`, `make_dataset_simple_handle_zc()`, `make_bookmark_handle()`, `zfs_open()`, `zfs_handle_dup()`, and `zfs_close()` construct and manage `zfs_handle_t` objects backed by `ZFS_IOC_OBJSET_STATS`, `ZFS_IOC_OBJSET_RECVD_PROPS`, bookmark enumeration, and cached zpool handles.
- Property validation is centralized in `zfs_valid_proplist()`, including user properties, user/group/project quotas, readonly/set-once checks, type applicability, mount/share zoning restrictions, encryption key properties, record/vol block sizes, volume sizing, UTF-8/normalization coupling, and `refreservation=auto`.
- `zfs_prop_set_list_flags()` gathers changelists for mount/share-sensitive properties, applies `ZFS_IOC_SET_PROP`, reports per-property failures, refreshes stats, and calls `zfs_mount_setattr()` for namespace properties such as atime, devices, exec, readonly, setuid, xattr, and nbmand.
- `zfs_prop_inherit()` handles both user-property inheritance and native property inheritance, using changelists and remount updates where needed.
- `zfs_prop_get()`, `zfs_prop_get_int()`, `zfs_prop_get_numeric()`, and `zfs_prop_get_recvd()` translate raw nvlists and objset stats into display values, including temporary mount-option overrides from `/proc/self/mounts`, clone/redaction snapshot formatting, GUID/txg literal handling, mountpoint inheritance plus altroot handling, and received-property mode.
- `zfs_create()`, `zfs_clone()`, `zfs_snapshot()`, `zfs_snapshot_nvl()`, `zfs_destroy()`, `zfs_destroy_snaps()`, `zfs_destroy_snaps_nvl()`, `zfs_promote()`, `zfs_rollback()`, and `zfs_rename()` wrap libzfs_core/kernel operations with parent checks, type checks, crypto checks, recursive behavior, changelists, and user-facing error translation.
- `zfs_hold()`, `zfs_hold_nvl()`, `zfs_release()`, `zfs_get_holds()`, `zfs_get_fsacl()`, and `zfs_set_fsacl()` implement snapshot holds and delegated ACL access.
- `zfs_userspace()` and `zfs_prop_get_userquota*()` query user/group/project usage and quota values through userspace accounting ioctls.
- `zvol_volsize_to_reservation()` models zvol reservation requirements, including RAIDZ/dRAID allocation overhead, metadata blocks, and copies.

## State And Dependencies

The file depends on `libzfs_impl.h`, `libzfs_core`, ZFS ioctls, nvlists, ZFS property metadata, zpool handles, changelists, mount/share helpers, crypto helpers, zone checks, user/group lookup, optional idmap/MLS label support, and kernel objset stats.

## Risks And Invariants

Dataset handles cache property nvlists and mount options, so callers must refresh when they need current kernel state. Changelist prefix/postfix ordering is essential around property changes, rename, rollback, and unmount/remount behavior. Volume reservation logic must stay synchronized with kernel/vdev accounting and the referenced test-suite shell implementation. Userquota property decoding depends on local passwd/group/idmap resolution and zone rules, so the same property string can fail or encode differently across environments.
