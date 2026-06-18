# sources/distributed-fs/ceph-client/kernel/sched/pelt.h

## Purpose
Declares PELT update entry points and inline clock/accounting helpers shared by scheduler classes. It is the internal scheduler header that connects PELT math in `pelt.c` with runqueue clock scaling and CFS bandwidth handling.

## APIs, Control Flow, and State
The header declares CFS entity/runqueue update functions, RT/DL load-average updates, optional hardware-pressure and IRQ updates, and `update_other_load_avgs()`. Inline helpers include `get_pelt_divider()`, `cfs_se_util_change()`, `rq_clock_pelt()`, `_update_idle_rq_clock_pelt()`, `update_rq_clock_pelt()`, `update_idle_rq_clock_pelt()`, `update_idle_cfs_rq_clock_pelt()`, and `cfs_rq_clock_pelt()`. The control flow is inline and called while holding runqueue locks: non-idle elapsed time is scaled by CPU capacity and frequency, idle runqueues resynchronize PELT clock to task clock, and fully utilized runqueues accumulate `lost_idle_time` so reduced-capacity execution does not create false idle signal.

State touched here lives in `struct rq` (`clock_pelt`, `lost_idle_time`, `clock_idle`, `clock_pelt_idle`, class averages), `struct cfs_rq` throttling clock fields, and `struct sched_avg` flags. With CFS bandwidth enabled, CFS runqueue PELT clocks subtract throttled time and record idle throttling snapshots.

## Dependencies and Integration Points
Depends on `sched.h`, generated PELT constants, lockdep runqueue assertions, architecture capacity/frequency scaling, CFS bandwidth config, hardware pressure config, and IRQ average config. Integration points include fair scheduling, RT/DL load updates, idle transitions in `idle.c`, migration lag handling through `clock_pelt_idle`, cgroup throttling, and utilization estimation.

## Risks and Test Signals
Risks include using PELT clocks without an updated/locked runqueue clock, incorrect memory ordering for idle clock snapshots used by migration, lost-idle misaccounting on saturated CPUs, and cgroup throttling time leaking into runnable averages. Test signals include lockdep assertions, CFS bandwidth throttle/unthrottle tests, CPU capacity/frequency invariance tests, migration benchmarks, PELT tracepoints, and scheduler behavior after idle-to-busy transitions.
