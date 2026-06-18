# sources/distributed-fs/ceph-client/fs/xfs/xfs_sysfs.h

## Purpose

`sources/distributed-fs/ceph-client/fs/xfs/xfs_sysfs.h` defines the small XFS wrapper API around Linux kobjects. It provides ktype declarations, conversion helpers, init/delete helpers with completion-based release synchronization, and per-mount sysfs init/delete declarations. The source was read as a complete 58-line file for this report.

## Important APIs, Types, and Functions

Important declarations are `xfs_dbg_ktype`, `xfs_log_ktype`, `xfs_stats_ktype`, `xfs_mount_sysfs_init`, and `xfs_mount_sysfs_del`. Important inline helpers are `to_kobj`, `xfs_sysfs_release`, `xfs_sysfs_init`, and `xfs_sysfs_del`.

## Control Flow

`xfs_sysfs_init` selects the parent kobject, initializes the completion, calls `kobject_init_and_add`, and drops the kobject if add fails. `xfs_sysfs_del` removes the kobject, puts the reference, and waits for the release callback to complete. `xfs_sysfs_release` completes the per-object completion when the Linux kobject lifetime actually ends.

## State and Persistence Behavior

The header manages runtime kobject lifetime state embedded in `struct xfs_kobj`. It does not persist anything to disk; the completion only synchronizes teardown with kobject release.

## Dependencies and Integration Points

The header depends on Linux kobject and completion primitives through included XFS platform headers. It integrates with `xfs_sysfs.c`, global stats/debug/log kobjects, and per-mount sysfs setup in mount code.

## Risks and Edge Cases

All embedded `struct xfs_kobj` users must have a valid `complete` field and must not be freed before `xfs_sysfs_del` returns. Failed `kobject_init_and_add` paths rely on `kobject_put` to trigger release. Double deletion or deleting never-added kobjects would break the completion/lifetime contract.

## Test Signals

Build coverage plus mount/unmount leak checks, kobject reference debugging, sysfs removal races, and failure injection around `kobject_init_and_add` are the primary signals.
