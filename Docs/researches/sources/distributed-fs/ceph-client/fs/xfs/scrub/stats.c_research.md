<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/stats.c -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/stats.c

Purpose: implements optional online scrub statistics collection for global and per-mount debugfs reporting. It counts scrub outcomes, repair attempts/successes, retry counts, and accumulated check/repair runtimes per scrub type.

Important APIs and functions: `struct xchk_scrub_stats` stores counters and timing for one scrub type, guarded by a per-type spinlock. `struct xchk_stats` owns the debugfs dentry and an array indexed by `XFS_SCRUB_TYPE_NR`. `name_map[]` maps scrub type numbers to stable debugfs output names. `xchk_stats_format()` emits one line per named scrub type. `xchk_stats_estimate_bufsize()` computes the worst-case output allocation. `xchk_stats_merge_one()` updates a counter bucket from `xfs_scrub_metadata` flags and `xchk_stats_run`. Public entry points allocate/register/free mount stats and set up/tear down global stats.

Control flow: `xfs_scrub_metadata()` accumulates runtime and retry data in `xchk_stats_run` and calls `xchk_stats_merge()` unless the operation ended as `-ENOENT`. Merge updates both `global_stats` and `mp->m_scrub_stats`. Debugfs reads allocate a snapshot buffer, format all stat lines in one pass, and serve it with `simple_read_from_buffer`; reads after position zero return EOF to avoid multi-call garbling. Writing `1` to `clear_stats` resets all counters up to the spinlock field.

State and persistence: stats are in-memory only and disappear on module/mount teardown. Global stats live in static storage; mount stats are allocated under `mp->m_scrub_stats`. Counters are protected by `css_lock`, but formatting reads fields without taking those locks, so debugfs output is a best-effort live snapshot rather than a coherent transaction. The debugfs dentries are attached under a `scrub` directory with `stats` and `clear_stats` files.

Dependencies and integration points: depends on `CONFIG_XFS_ONLINE_SCRUB_STATS`, debugfs helpers, XFS scrub type constants, scrub flags, `ktime_get_ns` timing from `stats.h`, and the mount lifecycle that calls mount stats allocation/free and register/unregister. It must stay aligned with `meta_scrub_ops[]`, trace scrub type names, and the userspace/debugfs tools that parse the fixed text format.

Risks and test signals: risks include missing `name_map` entries when new scrub types are added, integer overflow of long-running 32-bit counters, stale debugfs dentries if unregister/free ordering changes, and snapshot inconsistency during live updates. Buffer-size estimation relies on struct field layout, so adding fields before `css_lock` requires care. Test signals should include stats-disabled builds, mount/global debugfs file presence, clear_stats validation, output line count/name stability, and nonzero counters after clean, corrupt, retry, and repair paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/stats.c -->
