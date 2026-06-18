<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/fscounters.c -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/fscounters.c

Purpose: Scrubs XFS filesystem summary counters by independently aggregating per-AG inode/free-space state and realtime free extents, then comparing those expected values with in-core percpu counters.

Important APIs, types, and functions: Exports `xchk_setup_fscounters()` and `xchk_fscounters()`. Important helpers include `xchk_fscount_warmup()`, `xchk_fscounters_freeze()`, `xchk_fscounters_cleanup()`, `xchk_fscount_btreeblks()`, `xchk_fscount_aggregate_agcounts()`, `xchk_fscount_count_frextents()`, and `xchk_fscount_within_range()`. `XCHK_FSCOUNT_MIN_VARIANCE` defines minimum tolerance for unfrozen scans.

Control flow: Setup optionally enables drain gates for pre-lazysbcount filesystems, allocates `xchk_fscounters`, computes valid inode-count bounds, initializes per-AG state by reading AGI/AGF headers, and freezes the filesystem for repair or try-harder scans. The scrub function snapshots global counters, rejects impossible negative or out-of-range values, aggregates initialized per-AG counters, subtracts per-AG and global reservations plus delayed allocation counters, optionally counts realtime bitmap free extents, and compares expected values against before/after counter sums. Unfrozen mismatches return `-EDEADLOCK` so userspace can retry with stronger freeze permission; frozen mismatches are marked corrupt.

State and persistence: The scrub stores computed expected counters, valid inode ranges, realtime-delalloc adjustment, and freeze state in `sc->buf`. It does not update persistent counters; repair uses the computed state. The freeze cleanup callback thaws the filesystem and logs an emergency if thaw fails.

Dependencies and integration points: Depends on superblock freeze/thaw, mount write protection, percpu counters, per-AG cached AGI/AGF fields, btree block counting for old filesystems, realtime bitmap queries, delayed allocation counters, and scrub error/incomplete handling. It feeds `fscounters_repair.c`.

Risks and test signals: Race tolerance is subtle: lockless aggregation can be perturbed by allocation, inodegc, delayed allocation, and realtime reservations. Test idle and high-churn filesystems, repair with frozen fs, pre-lazysbcount btree-block counting, negative transient free counters, realtime and zoned configurations, per-AG reservation accounting, malformed initialized flags, counter overflow bounds, and retry behavior that sets incomplete instead of repairing from partial data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/fscounters.c -->
