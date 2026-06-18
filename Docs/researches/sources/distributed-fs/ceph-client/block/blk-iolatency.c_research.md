# sources/distributed-fs/ceph-client/block/blk-iolatency.c

## Purpose
`blk-iolatency.c` implements the cgroup block I/O latency controller as an `rq_qos` policy. It protects configured cgroups by tracking bio latency over rolling windows and throttling peer cgroups when a protected group misses its configured `io.latency` target. The implementation is hierarchy-aware: submit and completion paths walk from the bio's `blkcg_gq` toward the root and apply accounting or throttling at configured ancestors.

## Important APIs, Types, And Functions
Core state lives in `struct blk_iolatency`, `struct iolatency_grp`, `struct child_latency_info`, and `struct latency_stat`. `blk_iolatency_init()` attaches `RQ_QOS_LATENCY` to a disk and activates `blkcg_policy_iolatency`. `blkcg_iolatency_throttle()` is the submit hook, `blkcg_iolatency_done_bio()` is the completion hook, and `blkcg_iolatency_exit()` tears the policy down. Cgroup user interface is provided by `iolatency_files`, especially `iolatency_set_limit()` and `iolatency_print_limit()` for the `latency` file. Policy lifecycle hooks are `iolatency_pd_alloc()`, `iolatency_pd_init()`, `iolatency_pd_offline()`, and `iolatency_pd_free()`.

## Control Flow
On configuration, `iolatency_set_limit()` opens the target block device, initializes the rq-qos policy if needed under `rq_qos_mutex`, prepares the cgroup/device binding, parses `target=<usec>|max`, and updates `min_lat_nsec`. Enabling the first target schedules `enable_work`, which freezes the queue before flipping `enabled` and `QUEUE_FLAG_BIO_ISSUE_TIME` so inflight accounting remains balanced. On bio submission, `blkcg_iolatency_throttle()` checks inherited scale cookies and waits on each group's `rq_wait` unless the bio is issued as root or the task is dying. On completion, `blkcg_iolatency_done_bio()` decrements inflight counters, records latency unless status is `BLK_STS_AGAIN`, rolls the accounting window, and calls `iolatency_check_latencies()` to update parent scale cookies. `blkiolatency_timer_fn()` periodically clears stale scale groups and allows recovery.

## State And Persistence
The controller stores runtime-only kernel state in per-cgroup policy data: per-CPU latency stats, current window stats, `max_depth`, delay accounting, scale cookies, and latency targets. Persistent user-visible state is the configured cgroup file value; there is no on-disk persistence in this file. Atomic counters and spinlocks protect shared fields; queue freezing protects the global enabled toggle from racing with in-flight bio accounting.

## Dependencies And Integration Points
This code integrates with blk-cgroup, rq-qos, blk-stat, blk-mq queue freezing, timer/workqueue infrastructure, memcg delay accounting, bio issue time tracking, and block trace/debug stats. It relies on `bio_issue_as_root_blkg()`, `blkcg_schedule_throttle()`, `blkcg_use_delay()`, and `blkcg_add_delay()` for cgroup semantics and priority-inversion handling.

## Risks And Test Signals
High-risk areas are unbalanced inflight counts when enabling/disabling, scale-cookie races between parent and child groups, incorrect treatment of `issue_as_root`, missed wakeups on depth increases, and latency window math for SSD percentile-style versus rotating mean-latency modes. Useful tests include cgroup hierarchy workloads with competing latency targets, toggling targets while I/O is active, root-issued metadata/swap I/O delay behavior, `BLK_STS_AGAIN` retries, queue freeze/unfreeze stress, and debug-stat output for depth/window/average latency.
