# sources/distributed-fs/ceph-client/kernel/sched/pelt.c

## Purpose
Implements Per Entity Load Tracking (PELT), the exponentially decayed runnable/load/utilization accounting used by CFS entities, CFS runqueues, RT/DL runqueues, IRQ time, and hardware pressure.

## APIs, Control Flow, and State
Important exported scheduler-internal functions are `__update_load_avg_blocked_se()`, `__update_load_avg_se()`, `__update_load_avg_cfs_rq()`, `update_rt_rq_load_avg()`, `update_dl_rq_load_avg()`, `update_hw_load_avg()`, `update_irq_load_avg()`, and `update_other_load_avgs()`. The core math is `decay_load()`, `accumulate_sum()`, `___update_load_sum()`, and `___update_load_avg()`. Time is converted to 1024 ns units, split into PELT periods, decayed using the generated `runnable_avg_yN_inv[]` table, then normalized with `get_pelt_divider()` to update `load_avg`, `runnable_avg`, and `util_avg`.

State persists in each `struct sched_avg`: sums, averages, `period_contrib`, `last_update_time`, and utilization-estimation flags. CFS entity updates account whether an entity is queued, runnable, and current. CFS runqueue updates aggregate load weight and runnable count. RT and DL updates track binary running time as utilization. Optional hardware pressure uses `load_avg`, while IRQ accounting pessimistically inserts interrupt runtime just before the current update because IRQ time is not part of `clock_task`. `update_other_load_avgs()` refreshes all non-fair-class signals while the runqueue is locked and its clock is current.

## Dependencies and Integration Points
Depends on `pelt.h`, generated `sched-pelt.h`, runqueue clocks, capacity/frequency scaling hooks, tracepoints, CFS/RT/DL scheduler classes, hardware-pressure support, IRQ time accounting, and util-estimation flags. Its outputs feed task placement, load balancing, cpufreq utilization updates, cgroup scheduling, and capacity-aware scheduling.

## Risks and Test Signals
Risks include arithmetic overflow or truncation in decayed sums, bad handling of negative clock deltas during sched-clock initialization, stale `UTIL_AVG_UNCHANGED` flags, incorrect capacity invariance, IRQ-time double accounting, and divergence between generated PELT constants and formulas. Test signals include scheduler PELT tracepoints, cpufreq utilization tests, CFS group scheduling benchmarks, RT/DL utilization tracking, IRQ-heavy workloads, frequency/capacity invariance tests on heterogeneous systems, and builds regenerating `sched-pelt.h` from `Documentation/scheduler/sched-pelt`.
