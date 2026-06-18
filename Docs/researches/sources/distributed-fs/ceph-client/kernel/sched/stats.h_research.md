<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/sched/stats.h -->
# sources/distributed-fs/ceph-client/kernel/sched/stats.h

## Purpose
`stats.h` provides inline scheduler statistics, sched_info, and PSI integration helpers. It hides configuration differences so scheduler hot paths can call accounting helpers without open-coding `CONFIG_SCHEDSTATS`, `CONFIG_SCHED_INFO`, and `CONFIG_PSI` branches.

## Important APIs, Types, And Functions
For schedstats, it declares `sched_schedstats`, `schedstat_enabled`, `__schedstat_*`, `schedstat_*`, `schedstat_val`, `schedstat_val_or_zero`, `rq_sched_info_arrive`, `rq_sched_info_depart`, `rq_sched_info_dequeue`, `__update_stats_wait_start`, `__update_stats_wait_end`, `__update_stats_enqueue_sleeper`, and `check_schedstat_required`. For group scheduling it defines `struct sched_entity_stats` and `__schedstats_from_se`.

For PSI it declares `psi_task_change`, `psi_task_switch`, optional `psi_account_irqtime`, and inline hooks `psi_enqueue`, `psi_dequeue`, `psi_ttwu_dequeue`, and `psi_sched_switch`. For sched_info it defines `sched_info_enqueue`, `sched_info_dequeue`, `sched_info_arrive`, `sched_info_depart`, and `sched_info_switch`; disabled builds compile to no-ops.

## Control Flow
Schedstat macros either update fields unconditionally with the `__` forms or only when the static key is enabled with the regular forms. `check_schedstat_required` warns once if schedstat-dependent tracepoints are active without schedstats enabled. `__schedstats_from_se` maps a sched entity to task stats or group-entity stats depending on `CONFIG_FAIR_GROUP_SCHED`.

PSI hooks translate scheduler events into pressure-state transitions. `psi_enqueue` distinguishes wakeups, runnable migrations, and migration of delayed sleeping tasks; `psi_dequeue` skips saved dequeues and lets switch handling process normal sleeps; `psi_ttwu_dequeue` clears persistent sleep states when wakeup migration removes a task from the old queue; `psi_sched_switch` delegates to the PSI core. Sched_info hooks timestamp queue entry, arrival on CPU, and departure, updating per-task run-delay extrema and per-rq aggregate delay/runtime.

## State And Persistence
State lives in `struct sched_statistics`, `struct sched_info`, `task_struct` PSI flags, task `in_iowait`/`in_memstall` flags, group entity statistics, and rq aggregate sched_info fields. There is no durable persistence; all data is in-memory runtime accounting.

## Dependencies And Integration Points
This header depends on `sched.h` definitions, static keys, tracepoint enabled predicates, PSI core APIs, task/rq locking helpers, `ktime_get_real_ts64`, and cgroup fair scheduling layouts. It integrates with enqueue/dequeue/switch paths, tracepoints, `/proc/schedstat`, PSI user-visible pressure metrics, delay accounting, and task migration/wakeup code.

## Risks And Edge Cases
Accounting is lock-sensitive and must match scheduler state transitions exactly. PSI has subtle distinctions between sleeps, runnable migrations, delayed dequeue, and wakeup migration; clearing or setting the wrong flags can corrupt pressure totals. Sched_info relies on rq clocks and cross-CPU dequeue correction for skew. Disabled configuration stubs must preserve type compatibility and avoid evaluating expensive arguments unexpectedly.

## Test Signals
Use schedstats-enabled runs, PSI stress tests, cgroup pressure workloads, task migration stress, and tracepoint checks. Look for consistent run-delay extrema in `/proc/<pid>/sched`, monotonic `/proc/schedstat`, correct PSI totals during I/O and memory stalls, and absence of warnings from `check_schedstat_required` when schedstats are intentionally enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/sched/stats.h -->
