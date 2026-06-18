# sources/distributed-fs/ceph-client/fs/xfs/xfs_stats.h

## Purpose

`sources/distributed-fs/ceph-client/fs/xfs/xfs_stats.h` defines the XFS statistics ABI used by the rest of the filesystem. It lays out every 32-bit and 64-bit counter, provides offset helpers for table-based btree stats, declares formatting/clearing/procfs functions, and defines macros that update both global and per-mount counter sets. The source was read as a complete 230-line file for this report.

## Important APIs, Types, and Functions

Important declarations include `enum __XBTS_*` btree counter offsets, `struct __xfsstats`, `struct xfsstats`, `xfsstats_offset`, `XFS_STATS_CALC_INDEX`, `XFS_STATS_INC`, `XFS_STATS_DEC`, `XFS_STATS_ADD`, `XFS_STATS_INC_OFF`, `XFS_STATS_DEC_OFF`, `XFS_STATS_ADD_OFF`, `xfs_stats_format`, `xfs_stats_clearall`, and `extern struct xstats xfsstats`. Procfs functions are declared when `CONFIG_PROC_FS` is enabled and stubbed otherwise.

## Control Flow

This header has no runtime control flow by itself. Other XFS code invokes the update macros inline at event sites; each macro resolves the current CPU's global stats object and the current mount's stats object, then updates the same field or array offset in both. Formatting and clear entry points are implemented by `xfs_stats.c`.

## State and Persistence Behavior

The file defines the in-memory layout for per-CPU stats. `struct xfsstats` overlays the named `struct __xfsstats` with a 32-bit array for offset-based access up to the quota counter boundary, while 64-bit counters remain named fields. Counters are volatile kernel diagnostics and are not persisted to disk.

## Dependencies and Integration Points

The header depends on `<linux/percpu.h>` and the broader XFS mount/stat types available through including translation units. It is consumed by allocation, btree, inode, buffer, quota, log, zoned, and sysfs code. The btree cursor code uses `XFS_STATS_CALC_INDEX` so cursor instances can carry a base stats index and increment fixed offsets.

## Risks and Edge Cases

The stats structure is an observable diagnostic ABI because userspace tools parse the exported text. Counter order, array bounds, and group endpoints must be changed carefully. `XFS_STATS_DEC_OFF` as written references the offset element without decrementing, so any caller expecting offset decrement behavior would not get it. Update macros assume a valid `mp` and allocated `mp->m_stats.xs_stats`.

## Test Signals

Compile coverage across quota/procfs configurations, static analysis for offset bounds, runtime stats smoke tests that exercise representative update macros, and userspace parser checks for `/sys/fs/xfs/stats/stats` output are the best signals.
