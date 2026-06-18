# sources/distributed-fs/ceph-client/fs/nilfs2/sysfs.c

## Purpose
This file implements NILFS2 sysfs support. It creates the global `/sys/fs/nilfs2` kset, a global `features` group, per-mounted-device groups named by `sb->s_id`, per-device subgroups for mounted snapshots, checkpoints, segments, superblock state, and segment-constructor state, plus per-snapshot kobjects.

## Important APIs, Types, And Functions
The public entry points are `nilfs_sysfs_init()`, `nilfs_sysfs_exit()`, `nilfs_sysfs_create_device_group()`, `nilfs_sysfs_delete_device_group()`, `nilfs_sysfs_create_snapshot_group()`, and `nilfs_sysfs_delete_snapshot_group()`. Macro families `NILFS_DEV_INT_GROUP_OPS`, `NILFS_DEV_INT_GROUP_TYPE`, and `NILFS_DEV_INT_GROUP_FNS` generate repetitive sysfs show/store plumbing for internal device subgroups. Attribute callbacks expose data from `struct the_nilfs`, `struct nilfs_root`, `nilfs_cpfile_get_stat()`, `nilfs_sufile_get_stat()`, `nilfs_sufile_get_ncleansegs()`, and raw NILFS superblock fields.

## Control Flow
Module initialization creates the root kset under `fs_kobj`, then adds the `features` attribute group. Mount-time `nilfs_sysfs_create_device_group()` allocates `nilfs_sysfs_dev_subgroups`, initializes the device kobject, and creates subgroups in a strict order: mounted snapshots, checkpoints, segments, superblock, and segctor. Error paths unwind previously-created groups in reverse. Snapshot groups are attached either as `current_checkpoint` under the device group for checkpoint zero, or by checkpoint number under `mounted_snapshots`.

## State, Persistence, And Dependencies
Sysfs files are live views of in-memory and on-disk state rather than persistent files. Reads use `ns_sem`, `ns_segctor_sem`, `ns_last_segment_lock`, and metadata semaphores as appropriate. The only writable attribute is `superblock/sb_update_frequency`; its store parser clamps values below `NILFS_SB_FREQ` and updates `nilfs->ns_sb_update_freq` under `ns_sem`.

## Integration Points
`the_nilfs.c` calls the device-group creator after loading metadata files and calls deletion during failed mount cleanup. `nilfs_find_or_create_root()` and `nilfs_put_root()` create/delete snapshot groups. The exported telemetry is consumed by userspace monitoring, diagnostics, and filesystem administration tools.

## Risks
Kobject lifetime is the main risk: subgroups use `kobject_put()` and release completions, but this file does not wait on the completions directly. Any mismatch between creation order and deletion order can leak or expose stale sysfs nodes. Attribute callbacks also assume required metadata inodes and raw superblock pointers are valid while sysfs is visible. `nilfs_dev_volume_name_show()` uses `scnprintf()` with the raw field size, so malformed non-NUL-terminated volume names should be treated carefully by reviewers.

## Test Signals
Useful signals are mount/unmount cycles, fault injection in each subgroup creation step, reads of every sysfs attribute while segment construction and checkpoint creation are active, writes of `sb_update_frequency` including invalid and too-small values, snapshot mount/unmount tests, and KASAN/KCSAN runs around kobject teardown.
