# sources/distributed-fs/ceph-client/fs/ubifs/sysfs.c

## Purpose
`sysfs.c` exposes per-mounted-UBIFS error counters under the kernel `/sys/fs/ubifs/...` hierarchy. It creates one kobject per mounted UBIFS instance and provides read-only attributes for magic, node, and CRC error counters stored in `struct ubifs_stats_info`.

## Important APIs, Types, And Functions
`enum attr_id_t` identifies supported attributes. `struct ubifs_attr` wraps a kernel `struct attribute` with the UBIFS attribute id. `UBIFS_ATTR_FUNC()` declares `errors_magic`, `errors_crc`, and `errors_node` as mode `0444`. `ubifs_attr_show()` maps each attribute id to a `sysfs_emit()` of `sbi->stats` counters.

`ubifs_sysfs_register()` allocates `c->stats`, constructs the per-volume name from `UBIFS_DFS_DIR_NAME`, initializes `c->kobj` under the global `ubifs_kset`, and publishes the per-instance attribute group. `ubifs_sysfs_unregister()` deletes and puts the kobject, waits for the release completion, and frees stats. `ubifs_sysfs_init()` registers the global `ubifs` kset below `fs_kobj`; `ubifs_sysfs_exit()` unregisters it.

## Control Flow
Module init calls `ubifs_sysfs_init()` before filesystem registration. Each successful mount path calls `ubifs_sysfs_register()` early in `mount_ubifs()`, before most media reads that may increment counters. On mount failure or unmount, `ubifs_sysfs_unregister()` tears down the kobject and stats allocation. The kobject release callback completes `c->kobj_unregister`, allowing unregister to wait until sysfs has dropped the object.

## State And Persistence
All state is in memory. The exposed counters are not persistent across mount cycles. The kobject lifetime is tied to `struct ubifs_info`; the release completion protects teardown from freeing `c->stats` and proceeding while sysfs still owns the kobject.

## Dependencies And Integration Points
This file depends on kernel kobject/kset/sysfs APIs, `fs_kobj`, and UBIFS mount state (`c->vi`, `c->kobj`, `c->stats`). `super.c` calls global init/exit and per-mount register/unregister. Lower-level IO and validation code update `c->stats` counters that this file exposes.

## Risks And Edge Cases
The generated sysfs name must fit `UBIFS_DFS_DIR_LEN`; overflow returns `-EINVAL`. Register failure must call `kobject_put()` and wait for release before freeing stats. Unregister assumes registration succeeded and should be paired with the mount paths that allocated `c->stats`. Attribute reads return zero for unknown ids, but only known attributes are installed.

## Test Signals
Signals include `/sys/fs/ubifs` kset creation/removal at module init/exit, per-volume directory creation on mount, read-only output for the three error attributes, counter changes after injected magic/node/CRC errors, long-name bounds checks, and fault injection for stats allocation or `kobject_init_and_add()` failure.
