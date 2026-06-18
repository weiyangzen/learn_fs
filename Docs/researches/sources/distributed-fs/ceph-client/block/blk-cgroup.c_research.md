# sources/distributed-fs/ceph-client/block/blk-cgroup.c

## Purpose

`blk-cgroup.c` implements the common block I/O cgroup controller. It owns blkcg CSS allocation/free, per-queue/per-cgroup `blkcg_gq` lifetime, policy registration and activation, cgroup I/O statistics, bio-to-cgroup association, optional punted bio submission, writeback lifetime coordination, and delay-based throttling.

## Important APIs, Types, And Functions

Global state includes `blkcg_root`, `blkcg_root_css`, `blkcg_policy[]`, `all_blkcgs`, `blkcg_debug_stats`, and `blkg_stat_lock`. Important lifecycle functions are `blkg_alloc()`, `blkg_create()`, `blkg_lookup_create()`, `blkg_destroy()`, `blkg_destroy_all()`, `blkg_release()`, `__blkg_release()`, and `blkg_free_workfn()`.

Public APIs include `bio_blkcg_css()`, `blkcg_print_blkgs()`, `blkg_conf_*()` helpers, `blkcg_pin_online()`, `blkcg_unpin_online()`, `blkg_init_queue()`, `blkcg_init_disk()`, `blkcg_exit_disk()`, `blkcg_activate_policy()`, `blkcg_deactivate_policy()`, `blkcg_policy_register()`, `blkcg_policy_unregister()`, `blkcg_maybe_throttle_current()`, `blkcg_schedule_throttle()`, `blkcg_add_delay()`, `bio_associate_blkg_from_css()`, `bio_associate_blkg()`, `bio_clone_blkg_association()`, `blk_cgroup_bio_start()`, and `blk_cgroup_congested()`.

## Control Flow, State, And Persistence

Each `blkcg_gq` associates a blkcg with a request queue. Creation allocates the object, percpu ref, iostat sets, request-queue reference, optional async bio state, and active policy data. `blkg_create()` links parent blkgs, runs policy init/online callbacks, inserts into blkcg radix/hlist and queue lists, and marks the blkg online. Lookups use the root blkg, per-blkcg hint, or radix tree and create missing parents before children.

Destruction offlines policy data, removes radix/hlist entries, clears hints, kills the percpu ref, flushes pending stats during RCU release, drops CSS refs, and schedules sleepable free work. Queue/disk init creates root blkg and disk exit destroys all blkgs plus throttling state.

`blk_cgroup_bio_start()` updates non-root default-hierarchy stats, accounting bytes once per split chain with `BIO_CGROUP_ACCT`, increments I/O counts, queues the percpu iostat on a lockless list, and notifies cgroup rstat. Flush drains only queued stats and propagates deltas up parents. Root stats are synthesized from disk-wide stats.

Policy register/activate/deactivate/unregister manage per-cgroup and per-blkg policy data under documented mutex and lock ordering. Bio association finds or creates the closest live blkg for the bio's disk and stores a reference in `bio->bi_blkg`; clone association preserves the source CSS.

Delay throttling accumulates delay per blkg, schedules resume-time checks, walks ancestors for the largest delay, clamps normal delay, optionally enters PSI memstall, and sleeps killably.

## Dependencies And Integration Points

The file integrates cgroup core, block devices, request queues, blk-mq queue freezing, backing-dev names, writeback, blk-throttle, blk-ioprio, PSI, task resume notifications, radix trees, RCU, percpu refs, lockless lists, seq_file, and disk stats. `bio.c`, BFQ, throttling, ioprio, and cgroupfs all depend on these paths.

## Risks And Test Signals

Lock ordering is critical: queue lock generally nests outside blkcg lock, with special reverse lock handling during cgroup destruction. Stat flushing depends on `lqueued`, memory barriers, u64 stats seqcounts, RCU, and rstat ordering. Bio association must handle dying cgroups by falling back to ancestors. Test cgroup churn under I/O, queue rebind, policy activation failures, io.stat root/non-root correctness, split bio accounting, writeback-delayed destruction, delay throttling, and lockdep.
