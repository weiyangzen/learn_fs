# sources/distributed-fs/ceph-client/fs/xfs/xfs_stats.c

## Purpose

`sources/distributed-fs/ceph-client/fs/xfs/xfs_stats.c` implements XFS runtime statistics formatting, clearing, and legacy procfs compatibility. It owns the global `xfsstats` instance and provides the text output consumed by `/sys/fs/xfs/stats/stats`, per-mount stats kobjects, and `/proc/fs/xfs/stat` symlink compatibility. The source was read as a complete 179-line file for this report.

## Important APIs, Types, and Functions

Important symbols are `struct xstats xfsstats`, `counter_val`, `xfs_stats_format`, `xfs_stats_clearall`, `xfs_init_procfs`, and `xfs_cleanup_procfs`. With quota and procfs enabled, the file also implements `xqm_proc_show` and `xqmstat_proc_show` for legacy quota stats. `xfs_stats_format` emits grouped counters using an internal `xstats_entry` table whose endpoints are derived from `xfsstats_offset(...)`; the high-precision 64-bit counters are emitted separately.

## Control Flow

Stats reads enter through sysfs or procfs and call `xfs_stats_format`. The formatter walks every declared stats group, sums the selected 32-bit counter index across all possible CPUs with `counter_val`, appends a line per group, then separately sums the 64-bit byte/relog counters across CPUs. Stats clearing enters through sysfs `stats_clear` or sysctl `stats_clear`, calls `xfs_stats_clearall`, logs a notice, and zeroes each per-CPU stats object while preserving stateful inode counters.

## State and Persistence Behavior

Statistics are in-memory per-CPU counters. The global `xfsstats.xs_stats` is allocated during module initialization, and each mounted filesystem owns another `mp->m_stats.xs_stats`. Values do not persist across module unload or reboot. `xfs_stats_clearall` intentionally preserves `xs_inodes_active` and `xs_inodes_meta` because they represent current state rather than historical events.

## Dependencies and Integration Points

The implementation depends on XFS platform wrappers, Linux per-CPU iteration, procfs, sysfs, quota configuration, and `xfs_notice`. It integrates with `xfs_sysfs.c` for normal stats exposure, `xfs_sysctl.c` for global clear support, and `xfs_super.c` module init/exit for procfs creation and removal.

## Risks and Edge Cases

The formatting table must match `struct __xfsstats` layout and endpoint order; adding counters without updating endpoints can mislabel or hide stats. The `PATH_MAX` output buffer convention constrains formatting even as counters grow. Clearing loops over possible CPUs and disables preemption around each zeroing operation, but consumers can still observe racing snapshots because these are diagnostic counters, not transactional data.

## Test Signals

Useful signals include building with and without `CONFIG_PROC_FS` and `CONFIG_XFS_QUOTA`, reading `/sys/fs/xfs/stats/stats`, clearing via sysfs and sysctl, verifying active/meta inode counters survive clear, and checking legacy `/proc/fs/xfs/stat`, `xqmstat`, and `xqm` entries when enabled.
