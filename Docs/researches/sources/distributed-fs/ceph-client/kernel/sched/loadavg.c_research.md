# sources/distributed-fs/ceph-client/kernel/sched/loadavg.c

## Purpose
Computes the global Unix-style load average (`avenrun`) from distributed per-runqueue runnable and uninterruptible task counts, with special handling for tickless/NO_HZ CPUs.

## APIs, Control Flow, and State
Exports and important functions include `avenrun`, `calc_load_tasks`, `calc_load_update`, `get_avenrun()`, `calc_load_fold_active()`, `calc_load_n()`, `calc_global_load()`, `calc_global_load_tick()`, and NO_HZ helpers `calc_load_nohz_start()`, `calc_load_nohz_remote()`, and `calc_load_nohz_stop()` when `CONFIG_NO_HZ_COMMON` is enabled. The core algorithm folds per-CPU deltas from `rq->nr_running + rq->nr_uninterruptible` into `calc_load_tasks` instead of scanning every CPU at each sample. Every `LOAD_FREQ`, `calc_global_load()` reads the global active count and updates one-, five-, and fifteen-minute exponentially decayed fixed-point averages.

The NO_HZ path keeps two `calc_load_nohz[]` delta buckets and an index. CPUs entering tickless mode fold their pending active delta into the current write bucket; the global updater reads the old bucket and flips indices with memory barriers so old and new windows do not alias. If the global updater falls behind, `calc_global_nohz()` catches up multiple missed intervals with `calc_load_n()`. Persistent state is limited to global atomics and `rq->calc_load_active` / `rq->calc_load_update` snapshots; the exported values are estimates and intentionally read without locking.

## Dependencies and Integration Points
Depends on scheduler runqueue counters, jiffies, fixed-point load macros from scheduler headers, atomic longs, memory barriers, and NO_HZ scheduler hooks. It integrates with `/proc/loadavg`, scheduler ticks, tickless idle/full dynticks, and any consumer of `get_avenrun()` or exported `avenrun`.

## Risks and Test Signals
Risks include off-by-one sample-window errors, lost or double-counted NO_HZ deltas, signed underflow from per-CPU uninterruptible accounting, stale load after long tickless intervals, and memory-order mistakes around index flipping. Test signals include `/proc/loadavg` behavior under CPU hotplug and NO_HZ idle, stress with many CPUs and many sleeping/runnable tasks, full-dynticks workloads, comparison against expected exponential decay, and scheduler tick tracing to confirm `calc_global_load_tick()` cadence.
