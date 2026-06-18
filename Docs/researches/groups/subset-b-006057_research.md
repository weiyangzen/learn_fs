# Research: subset-b-006057

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/sched/features.h -->
# sources/distributed-fs/ceph-client/kernel/sched/features.h

## Purpose
Defines the scheduler feature switches consumed by the core scheduler through the `SCHED_FEAT(name, default)` macro expansion pattern. The file is intentionally macro-only: includers choose whether each entry becomes an enum value, static key, debugfs setting, or generated table entry.

## APIs, Control Flow, and State
The exported surface is the ordered list of feature names and defaults. Important flags include EEVDF/CFS placement controls (`PLACE_LAG`, `PLACE_DEADLINE_INITIAL`, `PLACE_REL_DEADLINE`, `RUN_TO_PARITY`, `PREEMPT_SHORT`, `DELAY_DEQUEUE`, `DELAY_ZERO`), wakeup and locality controls (`NEXT_BUDDY`, `PICK_BUDDY`, `CACHE_HOT_BUDDY`, `WAKEUP_PREEMPTION`), high-resolution tick controls (`HRTICK`, `HRTICK_DL`), remote wakeup queuing (`TTWU_QUEUE`), scheduling-domain scan heuristics (`SIS_UTIL`, `WA_IDLE`, `WA_WEIGHT`, `WA_BIAS`, `NI_RANDOM`, `NI_RATE`), utilization estimation (`UTIL_EST`), RT behavior (`RT_PUSH_IPI`, `RT_RUNTIME_SHARE`), and debug/warning switches. There is no runtime control flow in this header; control flow arises wherever `sched_feat()` gates behavior. Persistent state is external, normally in scheduler feature static keys and the sched debugfs interface when enabled.

## Dependencies and Integration Points
The file depends on scheduler build configuration symbols such as `CONFIG_HRTIMER_REARM_DEFERRED`, `CONFIG_PREEMPT_RT`, and `HAVE_RT_PUSH_IPI`. It integrates with fair scheduling, deadline hrticks, RT push/pull balancing, topology-aware balancing, wakeup placement, PELT/util-est accounting, and scheduler debugging. The order and names are part of the scheduler's internal feature registry, so changes have broad scheduler impact even though this file contains no functions.

## Risks and Test Signals
Risk centers on accidentally changing default scheduler policy, enabling a feature under an incompatible config, or removing a feature still referenced by `sched_feat()`. Good signals are scheduler selftests, boot-time scheduler debugfs inspection, latency and wakeup-preemption benchmarks, RT migration tests, CFS fairness/regression runs, and config matrix builds with and without `PREEMPT_RT`, hrtick support, and RT push IPI support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/sched/features.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/sched/idle.c -->
# sources/distributed-fs/ceph-client/kernel/sched/idle.c

## Purpose
Implements the generic idle thread loop and the idle scheduling class. It connects scheduler idle-task selection to cpuidle governors, tick/nohz management, CPU hotplug death, suspend-to-idle, polling idle, livepatch state updates, and injected idle residency.

## APIs, Control Flow, and State
Externally visible functions include `sched_idle_set_state()`, `cpu_idle_poll_ctrl()`, `default_idle_call()`, `play_idle_precise()`, `cpu_startup_entry()`, `cpu_in_idle()`, and the `DEFINE_SCHED_CLASS(idle)` instance. Optional boot parameters `nohlt` and `hlt` control `cpu_idle_force_poll` when `CONFIG_GENERIC_IDLE_POLL_SETUP` is enabled. The main control path is `cpu_startup_entry()` setting `PF_IDLE` and repeatedly calling `do_idle()`. `do_idle()` enters tickless idle, loops until `need_resched()`, handles offline CPUs through `cpuhp_report_idle_dead()` and `arch_cpu_idle_dead()`, flushes deferred RCU no-cb wakeups, then chooses polling idle or `cpuidle_idle_call()`. `cpuidle_idle_call()` either uses suspend-to-idle/deepest-state logic, asks the cpuidle governor, or falls back to `default_idle_call()`. Exiting idle propagates preemption state, restarts nohz accounting, flushes SMP call functions, schedules away from the idle task, and updates livepatch state.

State is per-CPU and transient: polling bits on the idle task, `rq` idle state, tick/nohz state, cpuidle selected state/residency, `PF_IDLE`, and injected-idle hrtimer state. The idle sched class never migrates idle tasks, warns if they are dequeued/scheduled incorrectly, updates idle runtime and deadline-server idle accounting, and marks scheduler-ext idle transitions.

## Dependencies and Integration Points
Depends on cpuidle, clockevents broadcast idle, RCU dynticks, CPU hotplug, scheduler core, livepatch, hrtimers, tracepoints, and architecture hooks (`arch_cpu_idle_*`). Integration points include tick stopping/restarting, suspend-to-idle QoS latency, cpuidle governors, PREEMPT need-resched propagation, `SCHED_CLASS(idle)` callbacks, and `play_idle_precise()` users that temporarily force a kernel thread into controlled idle.

## Risks and Test Signals
The main risks are missed reschedule/timer events around interrupt-disabled idle entry, polling-bit ordering bugs, tick/nohz imbalance, CPU hotplug dead-loop mistakes, cpuidle governor misuse during s2idle, and illegal sleeps from the idle thread. Test signals include suspend-to-idle/resume cycles, CPU hotplug stress, NO_HZ_FULL and tick-broadcast tests, idle residency/cpuidle trace validation, livepatch while idle, lockdep/RCU stall testing, and RT/kthread callers of `play_idle_precise()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/sched/idle.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/sched/isolation.c -->
# sources/distributed-fs/ceph-client/kernel/sched/isolation.c

## Purpose
Manages housekeeping CPU masks for CPU isolation. It parses `nohz_full=` and `isolcpus=` boot parameters, maintains which CPUs may run general kernel housekeeping work, and lets subsystems route work away from isolated CPUs.

## APIs, Control Flow, and State
Public helpers include `housekeeping_enabled()`, `housekeeping_cpumask()`, `housekeeping_any_cpu()`, `housekeeping_affine()`, `housekeeping_test_cpu()`, `housekeeping_update()`, and `housekeeping_init()`. The backing state is a static `struct housekeeping` containing RCU-protected cpumasks indexed by `enum hk_type` and an enabled bitmask. `housekeeping_overridden` is a static key exported for fast callers that need to skip isolation logic when no override exists.

Boot setup flows through `housekeeping_nohz_full_setup()` and `housekeeping_isolcpus_setup()`, which parse CPU lists and flags for domain isolation, managed IRQ isolation, and kernel-noise/nohz isolation. `housekeeping_setup()` builds the inverse housekeeping mask from the user-provided isolated mask, ensures at least one present housekeeping CPU remains, validates consistency between `nohz_full=` and `isolcpus=`, stores boot-time memblock cpumasks, and invokes `tick_nohz_full_setup()` for kernel-noise isolation. `housekeeping_init()` later converts memblock cpumasks to kmalloc-backed masks. `housekeeping_update()` dynamically updates the domain housekeeping mask, synchronizes RCU, and notifies PCI, memcg, vmstat, unbound workqueue, timer migration, and kthread housekeeping users.

## Dependencies and Integration Points
Depends on cpumasks, RCU, static keys, lockdep, cpusets, CPU hotplug locking, bootmem/memblock allocation, workqueues, timers, PCI, memcg, vmstat, and nohz full. It integrates with scheduler domain construction, unbound workqueue affinity, timer migration isolation, kthread placement, managed interrupts, and cgroup/cpuset partition updates.

## Risks and Test Signals
Risks include leaving no online housekeeping CPU, mismatched `nohz_full` and `isolcpus` masks, unsafe RCU cpumask replacement, lockdep coverage gaps for domain masks, stale subsystem affinity after updates, and timer/workqueue work running on isolated CPUs. Test signals include boot-parameter parsing tests, NO_HZ_FULL workloads, cpuset partition updates under hotplug, workqueue/kthread affinity inspection, timer migration tests, managed IRQ affinity checks, and lockdep/RCU testing around `housekeeping_update()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/sched/isolation.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/sched/loadavg.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/sched/loadavg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/sched/membarrier.c -->
# sources/distributed-fs/ceph-client/kernel/sched/membarrier.c

## Purpose
Implements the `membarrier(2)` syscall commands that force memory-ordering points across threads, processes, restartable sequences, and architecture core-synchronization paths. It bridges userspace ABI requests to scheduler runqueue state and inter-processor interrupts.

## APIs, Control Flow, and State
The file defines `SYSCALL_DEFINE3(membarrier)`, `membarrier_exec_mmap()`, and `membarrier_update_current_mm()`. Supported command bits are built from UAPI `MEMBARRIER_CMD_*` values, conditionally including sync-core and RSEQ commands. Registration commands set bits in `mm->membarrier_state` and call `sync_runqueues_membarrier_state()` so currently running threads using that `mm` have matching `rq->membarrier_state`. `membarrier_exec_mmap()` clears state during exec and updates the current runqueue.

Expedited global and private commands take a full barrier before and after targeting CPUs. `membarrier_global_expedited()` scans online CPUs whose runqueue state advertises global expedited registration and whose current task has an `mm`, then sends `ipi_mb()`. `membarrier_private_expedited()` verifies the caller's registration, optionally selects `ipi_sync_core()` or `ipi_rseq()`, targets either all CPUs currently running the caller's `mm` or a specific CPU for RSEQ, and waits for the IPI callbacks. The IPI callbacks provide full barriers, deferred core sync, or RSEQ event forcing. A mutex serializes IPI command execution; CPU hotplug and RCU locks stabilize target CPUs and `rq->curr`.

## Dependencies and Integration Points
Depends on UAPI membarrier definitions, `mm_struct`, scheduler runqueues, CPU hotplug read locks, RCU, cpumasks, SMP call functions, sync-core arch hooks, RSEQ, and nohz full query behavior. Integration points are the syscall table, exec/mmap lifecycle, context switch updates through `membarrier_update_current_mm()`, scheduler barriers around `rq->curr`, and userspace runtimes that use membarrier for memory reclamation, JIT synchronization, or RSEQ aborts.

## Risks and Test Signals
This is memory-model-sensitive code. Risks include missing pre/post barriers, targeting stale or wrong `mm` users, CPU hotplug races, incorrect nohz-full compatibility for global commands, registration bits becoming visible out of order, sync-core running too late, and RSEQ CPU-target validation errors. Test signals include Linux membarrier selftests, RSEQ selftests, litmus-style ordering tests, CPU hotplug stress while issuing commands, single-thread and multi-`CLONE_VM` cases, nohz_full configurations, and architecture sync-core validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/sched/membarrier.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/sched/pelt.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/sched/pelt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/sched/pelt.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/sched/pelt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/sched/psi.c -->
# sources/distributed-fs/ceph-client/kernel/sched/psi.c

## Purpose
Implements Pressure Stall Information (PSI) for CPU, memory, IO, and optional IRQ pressure. It tracks task stalls as per-CPU time buckets, aggregates them into averages and totals, exposes `/proc/pressure/*`, and supports pollable threshold triggers for system and cgroup pressure.

## APIs, Control Flow, and State
Initialization flows through `psi_init()` and `psi_proc_init()`, honoring the `psi=` boot parameter and cgroup PSI enablement. Runtime scheduler hooks include `psi_task_change()`, `psi_task_switch()`, `psi_account_irqtime()`, `psi_memstall_enter()`, `psi_memstall_leave()`, and cgroup hooks `psi_cgroup_alloc()`, `psi_cgroup_free()`, `cgroup_move_task()`, and `psi_cgroup_restart()`. User-visible APIs are `psi_show()`, `psi_trigger_create()`, `psi_trigger_destroy()`, `psi_trigger_poll()`, and the proc file operations for `pressure/io`, `pressure/memory`, `pressure/cpu`, and optionally `pressure/irq`.

State is organized around `struct psi_group` for the system and each cgroup. Each group owns per-CPU `struct psi_group_cpu` counters, cumulative totals for average and poll aggregators, decaying averages, trigger lists, delayed work for two-second average sampling, and optional real-time polling state driven by a `psimon` kthread and timer. Per-task `psi_flags` and `in_memstall` describe current stall state. `psi_group_change()` is the hot path: under the runqueue lock and per-CPU seqcount, it updates task counters, derives SOME/FULL/NONIDLE state masks, records elapsed time in old states, schedules trigger polling if needed, and wakes the periodic average worker. `collect_percpu_times()` locklessly snapshots per-CPU buckets with seqcounts, weights pressure by non-idle time, and updates group totals. `update_averages()` feeds totals into 10s/60s/300s fixed-point averages while capping samples at one period. Trigger windows track growth and signal via wait queues or kernfs notifications.

## Dependencies and Integration Points
Depends on scheduler runqueue locking, `cpu_clock()`/`sched_clock()`, workqueues, timers, kthreads, seqcounts, procfs, cgroups/kernfs, capability checks, IRQ time accounting, and PSI public headers. Integration points include scheduler enqueue/dequeue/switch hooks, memory reclaim/refault paths around memstall sections, cgroup migration, `/proc/pressure` monitoring, cgroup pressure files, and privileged low-latency PSI polling.

## Risks and Test Signals
Risks include underflow or inconsistent `psi_flags`, races between task migration and memstall state, stale cgroup state during migration, seqcount sampling drift, trigger leaks during cgroup/file teardown, excessive unprivileged polling cost, missed rtpoll events due to memory-order mistakes, and misreported FULL semantics for system CPU pressure. Test signals include PSI kernel selftests, polling trigger tests with privileged and unprivileged windows, cgroup migration under load, memory reclaim and IO stall workloads, IRQ accounting validation, procfs read/write/poll tests, race testing with cgroup deletion, and booting with `psi=0`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/sched/psi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/sched/rq-offsets.c -->
# sources/distributed-fs/ceph-client/kernel/sched/rq-offsets.c

## Purpose
Generates build-time offsets for fields in `struct rq` needed by low-level or architecture code. This file is compiled as a small kbuild helper rather than linked into normal scheduler runtime.

## APIs, Control Flow, and State
The file defines `COMPILE_OFFSETS`, includes kbuild offset helpers and `sched.h`, and has a single `main()` that emits `DEFINE(RQ_nr_pinned, offsetof(struct rq, nr_pinned));`. There is no runtime kernel control flow and no persistent runtime state. The only output is a generated constant representing the offset of `rq.nr_pinned`.

## Dependencies and Integration Points
Depends on `linux/kbuild.h`, `linux/types.h`, `offsetof`, and the exact layout of `struct rq` in `sched.h`. It integrates with the kernel build's generated-offset mechanism and any low-level code or tooling that consumes `RQ_nr_pinned`.

## Risks and Test Signals
Risks are build failures or silent ABI/layout mismatches if `struct rq` changes and consumers are not updated. Since the helper has no runtime behavior, signals are compile success, generated-offset diffs, allmodconfig/architecture builds that use the offset, and tests for features that consume `rq->nr_pinned` through generated assembly constants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/sched/rq-offsets.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/sched/rt.c -->
# sources/distributed-fs/ceph-client/kernel/sched/rt.c

## Purpose
Implements the real-time scheduling class for `SCHED_FIFO` and `SCHED_RR`. It manages priority queues, runtime throttling, RT group scheduling, push/pull migration, round-robin slices, scheduler-class callbacks, sysctls, and cgroup RT bandwidth controls.

## APIs, Control Flow, and State
Global tunables include `sched_rr_timeslice`, `sysctl_sched_rt_period`, and `sysctl_sched_rt_runtime`, with sysctl handlers for `/proc/sys/kernel/sched_rt_period_us`, `sched_rt_runtime_us`, and `sched_rr_timeslice_ms`. Initialization and group helpers include `init_rt_rq()`, `init_rt_bandwidth()`, `alloc_rt_sched_group()`, `free_rt_sched_group()`, `unregister_rt_sched_group()`, `init_tg_rt_entry()`, `sched_group_set_rt_runtime()`, `sched_group_set_rt_period()`, `sched_rt_can_attach()`, `init_sched_rt_class()`, and `print_rt_stats()`.

The class is exposed through `DEFINE_SCHED_CLASS(rt)`. Enqueue/dequeue paths update RT entities through hierarchical `sched_rt_entity` chains, maintain per-priority lists and bitmaps, track `rt_nr_running`, `rr_nr_running`, boosted counts, highest priority, runqueue `nr_running`, cpufreq utilization, schedstats, and pushable-task plists. Picking chooses the first set priority bitmap entry, recursing through group runqueues to a task. Wakeup/preemption compares RT priorities and can reschedule or attempt equal-priority migration. `task_tick_rt()` accounts runtime, runs the RT watchdog, and rotates `SCHED_RR` tasks when their slice expires.

Runtime bandwidth control uses `struct rt_bandwidth` hrtimers and per-`rt_rq` `rt_time`, `rt_runtime`, and `rt_throttled`. `update_curr_rt()` charges execution time and throttles groups that exceed runtime; `do_sched_rt_period_timer()` replenishes runtime, unthrottles queues, and restarts or idles the period timer. Optional runtime sharing borrows spare bandwidth across root-domain CPUs. Group schedulability validation ensures child runtime ratios do not exceed parent or global RT bandwidth and prevents starving existing RT tasks.

SMP balancing tracks overloaded RT runqueues in root-domain `rto_mask`/`rto_count` and CPU priority arrays. Push paths select migratable queued RT tasks and move them to lower-priority CPUs; pull paths inspect overloaded CPUs when a CPU lowers priority. With `HAVE_RT_PUSH_IPI`, root-domain IRQ work serializes push requests to reduce lock contention on large systems. CPU online/offline callbacks update overload state, runtime, and `cpupri`.

## Dependencies and Integration Points
Depends on scheduler core, PELT, root domains, `cpupri`, cpumasks, hrtimers, cgroups/task groups, sysctl, cpufreq updates, POSIX RT CPU timers, utilization clamping, scheduler core scheduling throttling hooks, stop-machine CPU push helpers, and feature flags such as `RT_RUNTIME_SHARE` and `RT_PUSH_IPI`. It integrates with task policy changes, affinity changes, CPU hotplug, cgroup CPU controller files, deadline global bandwidth validation, and scheduler debug output.

## Risks and Test Signals
Risks are high because this code is latency and correctness critical: RT throttling can starve or overrun tasks, push/pull migration can race with affinity and migration-disabled sections, priority queue counts can desynchronize, group runtime changes can violate hierarchy constraints, IPI push loops can create latency storms, and RR timeslice changes can regress fairness. Test signals include RT scheduler selftests, `rt-tests` latency workloads, cgroup RT bandwidth tests, CPU hotplug with RT load, affinity/migration-disabled stress, SCHED_RR timeslice tests, sysctl validation including rollback, lockdep on double runqueue locking, POSIX `RLIMIT_RTTIME` tests, PREEMPT_RT builds, and heterogeneous capacity/uclamp placement tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/sched/rt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/sched/sched-pelt.h -->
# sources/distributed-fs/ceph-client/kernel/sched/sched-pelt.h

## Purpose
Provides generated constants for PELT decay math. It is produced from `Documentation/scheduler/sched-pelt` and included by `pelt.h`/`pelt.c` to avoid recalculating decay coefficients at runtime.

## APIs, Control Flow, and State
The header defines `runnable_avg_yN_inv[]`, `LOAD_AVG_PERIOD`, and `LOAD_AVG_MAX`. There are no functions or branches. `decay_load()` indexes the 32-entry table to apply the inverse decay coefficient for the sub-period remainder after accounting for whole PELT periods. `LOAD_AVG_PERIOD` fixes the half-life relationship at 32 periods, and `LOAD_AVG_MAX` is the maximum geometric-series sum used for normalization.

## Dependencies and Integration Points
Depends only on Linux fixed-width types. It integrates directly with `pelt.c` decay calculations and indirectly with every scheduler user of PELT load/utilization averages. The "do not modify" comment means the authoritative source is the generator/documentation, not manual edits here.

## Risks and Test Signals
Risks include hand-edited constants drifting from the intended PELT curve, table length mismatches with `LOAD_AVG_PERIOD`, and overflow/precision regressions in consumers. Test signals are successful scheduler builds, PELT trace comparisons before/after regeneration, running the documented generator, and workload tests that validate expected utilization half-life and convergence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/sched/sched-pelt.h -->
