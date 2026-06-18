<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/sched/stats.c -->
# sources/distributed-fs/ceph-client/kernel/sched/stats.c

## Purpose
`stats.c` implements scheduler statistics update helpers and the `/proc/schedstat` seq-file interface. It records wait, sleep, block, I/O wait, runqueue, and scheduling-domain load-balancing counters when schedstats are compiled in and enabled.

## Important APIs, Types, And Functions
The exported internal update functions are `__update_stats_wait_start`, `__update_stats_wait_end`, and `__update_stats_enqueue_sleeper`. `/proc/schedstat` is implemented by `show_schedstat`, `schedstat_start`, `schedstat_next`, `schedstat_stop`, `schedstat_sops`, and `proc_schedstat_init`. The file defines `SCHEDSTAT_VERSION` as 17.

## Control Flow
`__update_stats_wait_start` snapshots `rq_clock(rq)` into `stats->wait_start`; when called for a task with an existing wait start, it stores elapsed wait time. `__update_stats_wait_end` computes a delta from `wait_start`. If the task is migrating, it preserves the delta as the new start so wait time can continue across runqueues; otherwise it emits `trace_sched_stat_wait`, updates max/count/sum, and clears `wait_start`.

`__update_stats_enqueue_sleeper` handles tasks becoming runnable after sleeping or blocking. It consumes `sleep_start` and `block_start`, clamps negative deltas to zero, updates max and sum fields, clears the starts, emits sleep/blocked/iowait tracepoints, accounts scheduler latency, and increments I/O wait counters when `p->in_iowait` is set. The proc reader emits a version/timestamp header followed by one record per online CPU and domain records for each CPU's RCU-protected sched-domain chain.

## State And Persistence
State is held in `struct sched_statistics`, per-runqueue schedstat fields such as `yld_count`, `sched_count`, `ttwu_count`, `rq_cpu_time`, and `rq_sched_info`, plus per-domain counters in `struct sched_domain`. `/proc/schedstat` is a live diagnostic view, not durable persistence.

## Dependencies And Integration Points
The file depends on `sched.h` for runqueue, task, sched-domain, tracepoint, and schedstat macro definitions. It integrates with enqueue/dequeue and sleep paths in fair/core scheduling, trace events `sched_stat_*`, delay accounting through `account_scheduler_latency`, RCU domain traversal, `cpu_online_mask`, seq_file, and procfs registration at `subsys_initcall`.

## Risks And Edge Cases
Statistics rely on rq clocks and caller locking. Migrating tasks are a special case because wait accounting must survive rq changes. Clock skew or negative deltas are handled for sleep/block accounting but not all wait paths. The `/proc/schedstat` format is versioned; changing field order without bumping `SCHEDSTAT_VERSION` breaks tooling. Domain traversal must remain RCU-safe while domains are rebuilt.

## Test Signals
Enable `CONFIG_SCHEDSTATS` and `kernel.sched_schedstats`, run wakeup/sleep/block/I/O workloads, and compare `/proc/schedstat` monotonic counters with tracepoint output. CPU hotplug should not break seq iteration. Tools expecting version 17 should parse header, CPU lines, and domain lines successfully.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/sched/stats.c -->
