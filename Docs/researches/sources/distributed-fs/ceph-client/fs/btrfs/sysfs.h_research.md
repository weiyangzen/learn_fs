# sources/distributed-fs/ceph-client/fs/btrfs/sysfs.h

## Purpose

`sysfs.h` declares the Btrfs sysfs API used by mount, unmount, device, allocation, qgroup, and module lifecycle code. It also defines the public enum used to classify compatibility feature sets.

## Important APIs, Types, And Functions

- `enum btrfs_feature_set` identifies `FEAT_COMPAT`, `FEAT_COMPAT_RO`, and `FEAT_INCOMPAT`, with `FEAT_MAX` as the array bound.
- Feature reporting: `btrfs_printable_features()` and `btrfs_feature_set_name()`.
- Global lifecycle: `btrfs_init_sysfs()` and `btrfs_exit_sysfs()`.
- Fsid and mount lifecycle: `btrfs_sysfs_add_fsid()`, `btrfs_sysfs_remove_fsid()`, `btrfs_sysfs_add_mounted()`, `btrfs_sysfs_remove_mounted()`, and `btrfs_sysfs_update_sprout_fsid()`.
- Device lifecycle: `btrfs_sysfs_add_device()`, `btrfs_sysfs_remove_device()`, `btrfs_sysfs_update_devid()`, and `btrfs_kobject_uevent()`.
- Allocation lifecycle: `btrfs_sysfs_add_block_group_type()`, `btrfs_sysfs_add_space_info_type()`, and `btrfs_sysfs_remove_space_info()`.
- Qgroup lifecycle: `btrfs_sysfs_add_qgroups()`, `btrfs_sysfs_del_qgroups()`, `btrfs_sysfs_add_one_qgroup()`, and `btrfs_sysfs_del_one_qgroup()`.
- Read policy parsing: `btrfs_read_policy_to_enum()`, plus experimental module-parameter helpers under `CONFIG_BTRFS_EXPERIMENTAL`.

## Control Flow

The header does not implement behavior, but its API grouping mirrors the expected flow: initialize global sysfs during module setup, add an fsid directory during device discovery, enrich it on mount, add/remove device and allocation children as runtime state changes, expose qgroups when initialized, and tear down mounted and base fsid state during unmount or module exit.

## State And Persistence Behavior

The declarations expose functions that mutate kobject state embedded in `btrfs_fs_devices`, `btrfs_device`, `btrfs_space_info`, and `btrfs_qgroup`. Some sysfs store handlers behind these declarations can update superblock-derived state through transaction commit scheduling, but the header itself only defines the interface contract.

## Dependencies And Integration Points

The file forward-declares Btrfs and block-layer structures to keep include coupling low and includes only basic kernel types, compiler annotations, and kobject definitions. It is the integration boundary between `sysfs.c` and other Btrfs modules such as volumes, disk-io, qgroups, block groups, and mount lifecycle code.

## Risks

Because kobjects are embedded in long-lived Btrfs structures, callers must respect add/remove pairing and avoid using sysfs helpers on partially initialized objects. The conditional experimental read-policy declarations also require call sites to be guarded consistently by `CONFIG_BTRFS_EXPERIMENTAL`.

## Test Signals

Compile-time coverage verifies prototypes and configuration guards. Runtime signals are expected sysfs directory creation/removal for fsid, devices, allocation types, qgroups, and mounted attributes.
