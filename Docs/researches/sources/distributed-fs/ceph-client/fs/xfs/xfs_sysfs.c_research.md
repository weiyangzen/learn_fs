# sources/distributed-fs/ceph-client/fs/xfs/xfs_sysfs.c

## Purpose

`sources/distributed-fs/ceph-client/fs/xfs/xfs_sysfs.c` implements XFS sysfs kobject support and attributes for global debug controls, global and per-mount stats, log state, metadata I/O error retry policy, fail-at-unmount behavior, and zoned filesystem controls. The source was read as a complete 892-line file for this report.

## Important APIs, Types, and Functions

Important types and helpers include `struct xfs_sysfs_attr`, `to_attr`, `xfs_sysfs_object_show`, `xfs_sysfs_object_store`, `xfs_sysfs_ops`, `xfs_mp_ktype`, optional `xfs_dbg_ktype`, `xfs_stats_ktype`, `xfs_log_ktype`, `xfs_error_cfg_ktype`, `xfs_error_ktype`, `struct xfs_error_init`, and `xfs_zoned_ktype`. Important exported functions are `xfs_mount_sysfs_init`, `xfs_mount_sysfs_del`, and `xfs_error_get_cfg`. Attribute handlers cover debug knobs, `stats`, `stats_clear`, log head/tail/grant heads, `max_retries`, `retry_timeout_seconds`, `fail_at_unmount`, `max_open_zones`, `nr_open_zones`, and `zonegc_low_space`.

## Control Flow

Generic sysfs show/store dispatch converts Linux attributes to `struct xfs_sysfs_attr` and calls the attribute-specific function. `xfs_mount_sysfs_init` creates `.../xfs/<dev>/`, then child kobjects for `stats`, `error`, the `fail_at_unmount` file, metadata error policy entries for default/EIO/ENOSPC/ENODEV, and optional `zoned` attributes. `xfs_error_sysfs_init_class` initializes each errno policy kobject and seeds retry defaults. `xfs_mount_sysfs_del` removes zoned, error policy, metadata, error, stats, and mount kobjects in reverse. `xfs_error_get_cfg` maps runtime errno values to the configured retry policy.

## State and Persistence Behavior

Sysfs objects are runtime kernel objects attached to global or per-mount XFS state. Stats attributes read and clear per-CPU stats. Log attributes report live log head/tail/grant atomic state. Error policy attributes mutate `mp->m_error_cfg[class][errno]`, converting `-1` to `XFS_ERR_RETRY_FOREVER` and seconds to jiffies. Zoned attributes expose live open-zone counters and allow `zonegc_low_space` changes that wake zone GC. None of these settings are persisted by this file.

## Dependencies and Integration Points

The file depends on Linux kobject/sysfs APIs, `xfs_sysfs.h`, `xfs_stats_format`, `xfs_stats_clearall`, log internals, mount structures, XFS error policy definitions, realtime/zoned configuration, and zone GC wakeup. It is called from mount/unmount paths in `xfs_mount.c` and global setup in `xfs_super.c` through ktypes.

## Risks and Edge Cases

Attribute validation is critical because these files mutate live filesystem behavior. Retry timeout rejects values less than `-1` or greater than one day; max retries rejects less than `-1`; fail-at-unmount and debug boolean knobs reject invalid values; zoned low-space percentages reject values over 100. The init error path must unwind partially created kobjects, and deletion assumes all kobjects were initialized consistently. Debug-only attributes must match `struct xfs_globals` guards.

## Test Signals

Signals include sysfs tree presence after mount, stats read/clear behavior, log LSN/grant attributes changing under load, metadata error policy read/write validation, fail-at-unmount testing, zoned attribute presence only on zoned RT filesystems, `zonegc_low_space` wakeup behavior, and mount-failure injection to verify kobject unwind.
