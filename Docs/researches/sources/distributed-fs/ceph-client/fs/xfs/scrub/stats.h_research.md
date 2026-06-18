<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/stats.h -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/stats.h

Purpose: declares the optional scrub statistics interface used by the dispatcher and mount lifecycle code. When stats are disabled, it compiles the interface away to no-op macros while preserving call sites.

Important APIs and types: `struct xchk_stats_run` is the per-operation accumulator with `scrub_ns`, `repair_ns`, retry count, and repair attempted/succeeded booleans. Under `CONFIG_XFS_ONLINE_SCRUB_STATS`, the header declares global setup/teardown, mount allocation/free, debugfs register/unregister, and `xchk_stats_merge()`. `xchk_stats_now()` and `xchk_stats_elapsed_ns()` use nanosecond time and force at least one nanosecond elapsed if the clock returns the same value.

Control flow: scrub code initializes an `xchk_stats_run`, samples `xchk_stats_now()` around scrub/repair bodies, adds elapsed time, and merges at the end. The disabled configuration makes all helpers constant or no-op so callers need no `#ifdef` guards. The elapsed helper hides clock-resolution behavior from the dispatcher.

State and persistence: the header owns no state directly; the implementation stores in-memory global and per-mount counters. In disabled builds, no state is allocated and elapsed times are always zero. Dependencies include the XFS mount and scrub metadata types in callers, debugfs `dentry`, and kernel timekeeping.

Risks and test signals: the main risk is semantic drift between enabled and disabled builds, especially if callers start relying on side effects from merge or nonzero time values. The one-nanosecond minimum is important for avoiding misleading zero-duration reports. Test signals should include compile tests with stats enabled and disabled, runtime validation that counters increment only in enabled builds, and repair timing coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/stats.h -->
