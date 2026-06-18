# subset-b-006058 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/sched/sched.h -->
# sources/distributed-fs/ceph-client/kernel/sched/sched.h

## Purpose
`sched.h` is the private scheduler umbrella header. It defines the core runqueue, scheduling-class, group-scheduling, topology, bandwidth, clock, locking, utilization, pressure, and migration contracts shared by `kernel/sched/*.c`. It is not a public UAPI header; it centralizes scheduler-internal state and inline helpers so the fair, RT, deadline, idle, stop, topology, stats, cpufreq, PSI, cgroup, core-scheduling, and sched_ext code agree on one layout and locking model.

## Important APIs, Types, And Functions
Key policy helpers include `idle_policy`, `normal_policy`, `fair_policy`, `rt_policy`, `dl_policy`, `valid_policy`, `task_has_*_policy`, `cap_scale`, `update_avg`, cgroup weight conversion helpers, and deadline helpers such as `dl_entity_preempt`. Major state types are `struct rt_prio_array`, `struct rt_bandwidth`, `struct dl_bw`, `struct cfs_bandwidth`, `struct task_group`, `struct cfs_rq`, `struct rt_rq`, `struct dl_rq`, `struct root_domain`, `struct rq`, `struct sched_group_capacity`, `struct sched_group`, `struct affinity_context`, `struct sched_class`, and `struct sched_change_ctx`.

The runqueue access and locking API is built around `cpu_rq`, `this_rq`, `task_rq`, `raw_spin_rq_lock*`, `rq_lock*`, `task_rq_lock`, `__task_rq_lock`, `rq_pin_lock`, `rq_unpin_lock`, `rq_repin_lock`, `double_rq_lock`, `double_lock_balance`, and guard-class wrappers. Scheduling-class dispatch is defined by `struct sched_class` and helpers such as `put_prev_task`, `set_next_task`, `put_prev_set_next_task`, `DEFINE_SCHED_CLASS`, `for_each_active_class`, `sched_stop_runnable`, `sched_dl_runnable`, `sched_rt_runnable`, and `sched_fair_runnable`. State-change helpers and declarations include `activate_task`, `deactivate_task`, `enqueue_task`, `dequeue_task`, `wakeup_preempt`, `set_load_weight`, `__sched_setscheduler`, `__sched_setaffinity`, `set_task_rq`, `__set_task_cpu`, `attach_task`, `move_queued_task_locked`, and the `sched_change_begin`/`sched_change_end` RAII pattern.

## Control Flow
Most scheduler C files include this header before manipulating tasks or runqueues. Policy and priority paths use the policy helpers, `__normal_prio`/`__setscheduler_class` declarations, `set_load_weight`, and `sched_change` guards to dequeue a task, mutate its scheduling attributes, and enqueue it consistently. Wakeup and migration paths use `task_rq_lock`, task CPU setters, `select_task_rq` class hooks, `activate_task`, and wake flags such as `WF_TTWU`, `WF_EXEC`, and `WF_FORK`.

Class selection flows through linker-ordered `DEFINE_SCHED_CLASS` sections from highest to lowest priority, with `next_active_class` skipping fair or sched_ext depending on runtime state. Each class supplies hooks for enqueue/dequeue, yielding, preemption, balancing, picking, switching, CPU affinity, hotplug online/offline, ticks, fork/dead callbacks, priority changes, and runtime accounting. Runqueue clock users must hold the rq lock and rely on `update_rq_clock` plus `rq_clock`/`rq_clock_task`; skip flags avoid redundant clock work across schedule and bulk-update loops.

Topology and load-balance code use `for_each_domain`, `highest_flag_domain`, `lowest_flag_domain`, `sched_group_span`, `group_balance_mask`, root-domain refcounting declarations, and per-CPU cache-domain pointers. Utilization users flow through PELT state in `cfs_rq`, `rq->avg_*`, uclamp helpers, deadline bandwidth helpers, cpufreq update callbacks, EAS static key helpers, IRQ-time scaling, and cpuset/affinity contexts.

## State And Persistence
State is entirely in kernel memory. `struct rq` is per-CPU and holds runnable counts, current/donor tasks, class runqueues, root-domain and sched-domain pointers, clocks, nohz flags, bandwidth and hotplug fields, load averages, stats counters, uclamp buckets, PSI/IRQ/cpufreq accounting, active-balance work, and optional core-scheduling or sched_ext state. `struct root_domain` persists across scheduler-domain partitions through refcounts and RCU, carrying RT and deadline overload masks, `cpupri`, `cpudl`, deadline bandwidth, overutilization, and optional performance-domain lists. `struct task_group` mirrors cgroup scheduler state and owns per-CPU fair/RT entities and runqueues. `sched_group` and `sched_group_capacity` model domain group spans and capacity data. No filesystem persistence is performed by this header.

## Dependencies And Integration Points
The header includes many kernel subsystems: cpuset, cgroup, autogroup, cpufreq, PSI, rseq, hrtimer, stop_machine, workqueues, static keys, seq/proc, lockdep, RCU, NUMA, topology, tracepoints, delay accounting, and architecture barriers/capacity hooks. It integrates with `cpupri.h`, `cpudeadline.h`, `stats.h`, `ext.h`, public `linux/sched/*` headers, scheduler sysctls, scheduler debugfs/sysctl update hooks, BPF sched_ext when enabled, RT mutex priority inheritance, deadline admission control, nohz full tick dependencies, membarrier, IRQ time accounting, and restartable sequences through mm CID helpers.

## Risks And Edge Cases
The highest risks are layout and locking invariants. `struct rq` and class hook contracts are hot-path and configuration-sensitive; incorrect field use can break SMP scheduling, PI, hotplug, or core scheduling. RQ clock reads require the rq lock and a recent clock update. Task migration requires careful ordering around `p->on_rq`, `p->pi_lock`, rq locks, and `set_task_cpu` memory barriers. Double-rq locking must respect CPU/core ordering to avoid ABBA deadlocks. Optional features such as `CONFIG_SCHED_CORE`, `CONFIG_FAIR_GROUP_SCHED`, `CONFIG_CFS_BANDWIDTH`, `CONFIG_RT_GROUP_SCHED`, `CONFIG_UCLAMP_TASK`, `CONFIG_NUMA`, `CONFIG_SCHED_MM_CID`, and `CONFIG_SCHED_CLASS_EXT` change both layouts and behavior. Static keys such as schedstats, sched_uclamp, sched_asym_cpucapacity, sched_cluster_active, and sched_energy_present must only be toggled from safe contexts.

## Test Signals
Useful signals are kernel scheduler selftests, lockdep/RCU torture, CPU hotplug stress, cgroup scheduler tests, deadline/RT admission tests, cpuset affinity tests, schedstats/proc output checks, nohz full workloads, sched_ext build/runtime tests, PREEMPT_RT builds, and multi-architecture compile coverage. Runtime traces should show balanced enqueue/dequeue counts, no rq-clock warnings, no lockdep inversions, valid `sched_domain` debug output, stable PSI/sched_info accounting, and no WARNs in migration, core scheduling, or mm CID paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/sched/sched.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/sched/smp.h -->
# sources/distributed-fs/ceph-client/kernel/sched/smp.h

## Purpose
`smp.h` is a small scheduler-internal bridge for SMP callback handling. It declares scheduler-facing hooks used by wakeup and generic SMP call-function code while keeping non-SMP builds cheap.

## Important APIs, Types, And Functions
The file declares `sched_ttwu_pending(void *arg)`, which drains pending try-to-wake-up work, and `call_function_single_prep_ipi(int cpu)`, which prepares a target CPU for a single-function IPI. Under `CONFIG_SMP` it declares `flush_smp_call_function_queue`; otherwise it provides an empty inline stub.

## Control Flow
SMP wakeup paths can queue remote wakeups or function callbacks, prepare an IPI, and later run `sched_ttwu_pending` or flush the call-function queue on the destination CPU. Non-SMP builds compile callers against the same names but elide queue flushing.

## State And Persistence
This header defines no storage. State lives in per-CPU wake lists and SMP call-function queues owned by scheduler core and generic SMP code.

## Dependencies And Integration Points
It depends only on `linux/types.h` and scheduler/SMP implementation files. It integrates with try-to-wake-up batching, remote IPI delivery, and generic `smp_call_function_single` queue processing.

## Risks And Edge Cases
The declarations are small, but call ordering is sensitive: pending wakeups must be flushed before a CPU goes idle, offline, or assumes there is no runnable work. The non-SMP stub must not hide code that depends on side effects.

## Test Signals
Signals include SMP wakeup stress, CPU hotplug tests, lockdep around remote wake queues, and build coverage for both `CONFIG_SMP=y` and `CONFIG_SMP=n`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/sched/smp.h -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/sched/stop_task.c -->
# sources/distributed-fs/ceph-client/kernel/sched/stop_task.c

## Purpose
`stop_task.c` implements the scheduler class for per-CPU stop tasks used by `stop_machine` and CPU control paths. Stop tasks are the highest-priority scheduler entities: once runnable they preempt everything else and are not themselves preempted by normal classes.

## Important APIs, Types, And Functions
The file defines the `stop_sched_class` through `DEFINE_SCHED_CLASS(stop)`. Class hooks include `select_task_rq_stop`, `balance_stop`, `wakeup_preempt_stop`, `set_next_task_stop`, `pick_task_stop`, `enqueue_task_stop`, `dequeue_task_stop`, `yield_task_stop`, `put_prev_task_stop`, `task_tick_stop`, `switching_to_stop`, `prio_changed_stop`, and `update_curr_stop`.

## Control Flow
Stop tasks never migrate through this class; `select_task_rq_stop` returns the current task CPU. `pick_task_stop` returns `rq->stop` only when `sched_stop_runnable(rq)` says the stop task is queued. Enqueue/dequeue simply adjusts `rq->nr_running`. `set_next_task_stop` records `exec_start`; `put_prev_task_stop` updates common current-runtime accounting. Yield, switching into the class, and priority changes are treated as impossible and call `BUG()`.

## State And Persistence
The class uses per-runqueue `rq->stop`, `rq->nr_running`, and the stop task's `se.exec_start`. It does not allocate or persist state.

## Dependencies And Integration Points
It depends on `sched.h`, the scheduler class linker ordering, `sched_stop_runnable`, runqueue runnable accounting, `update_curr_common`, `set_cpus_allowed_common`, and the stop-machine infrastructure that creates and wakes per-CPU stop tasks.

## Risks And Edge Cases
This class relies on strong invariants: stop tasks must not yield, change class, change priority, or migrate through normal balancing. Violating those invariants triggers `BUG()` and can panic the kernel. Empty tick/update hooks are intentional because stop tasks are special control threads, but runtime accounting must still be advanced when switching away.

## Test Signals
Signals include CPU hotplug, stop_machine users, active balancing, migration stopper workloads, lockdep during stopper execution, and absence of `BUG()` paths. Build/link ordering should place stop above deadline, RT, fair, and idle classes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/sched/stop_task.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/sched/swait.c -->
# sources/distributed-fs/ceph-client/kernel/sched/swait.c

## Purpose
`swait.c` implements simple wait queues, a lighter wait primitive used by kernel code that needs exclusive waiters and small, predictable wakeup behavior. It backs APIs declared in `<linux/swait.h>`.

## Important APIs, Types, And Functions
The exported functions are `__init_swait_queue_head`, `swake_up_locked`, `swake_up_one`, `swake_up_all`, `prepare_to_swait_exclusive`, `prepare_to_swait_event`, and `finish_swait`. Internal helpers include `swake_up_all_locked`, `__prepare_to_swait`, and `__finish_swait`.

## Control Flow
Initialization sets up the raw spinlock lockdep class and waiter list. `__prepare_to_swait` records `current` in the waiter and appends it if not already linked. `prepare_to_swait_exclusive` and `prepare_to_swait_event` take the queue lock, enqueue the waiter, and set task state; the event variant removes the waiter and returns `-ERESTARTSYS` if the target state is interruptible and a signal is pending.

Wakeup is FIFO over `q->task_list`. `swake_up_locked` wakes the first waiter with `try_to_wake_up(..., TASK_NORMAL, wake_flags)` and removes it. `swake_up_one` wraps that under IRQ-safe locking. `swake_up_all_locked` repeatedly wakes while the caller already holds the lock; `swake_up_all` splices the list to a temporary list and drops/reacquires the lock between wakeups to bound lock hold time, so it is not for IRQ-disabled regions. Finish paths set the current task running and remove the waiter if still linked.

## State And Persistence
State is only the in-memory `swait_queue_head` raw spinlock and linked list of `swait_queue` entries, each pointing at a task. There is no persistence beyond the lifetime of the wait queue and wait entries.

## Dependencies And Integration Points
The implementation depends on `sched.h`, task states, `try_to_wake_up`, `wake_up_state`, raw spinlocks, lockdep, linked lists, signal-state checks, and exported symbol infrastructure. It integrates with completions and other kernel primitives that choose simple wait queues over full wait queues.

## Risks And Edge Cases
Wait entries must be initialized and finished correctly; stale list linkage can corrupt the queue or cause missed wakeups. `swake_up_locked` assumes the caller holds the queue lock. `swake_up_all` deliberately cannot be used with IRQs disabled because it may release the lock between wakeups. The wake return value is ignored because an already-running waiter should still observe its condition, but callers must use condition loops correctly.

## Test Signals
Useful signals are completion tests, signal-interrupted waits, lockdep on raw-spin use, IRQ-context users of `swake_up_all_locked`, and stress that repeatedly enqueues, wakes one, wakes all, times out, and finishes waiters without list corruption or missed wakeups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/sched/swait.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/sched/syscalls.c -->
# sources/distributed-fs/ceph-client/kernel/sched/syscalls.c

## Purpose
`syscalls.c` implements user-visible and kernel-internal scheduler control entry points: nice values, scheduler policy and priority changes, extended scheduler attributes, CPU affinity, yield operations, priority range queries, and RR interval queries. It is the main validation and permission layer between UAPI scheduler calls and internal scheduler state changes.

## Important APIs, Types, And Functions
Priority helpers are `__normal_prio`, `normal_prio`, `effective_prio`, `set_user_nice`, `is_nice_reduction`, `can_nice`, and `task_prio`. Task lookup helpers are `find_process_by_pid`, `find_get_task`, and the `find_get_task` guard class. Scheduler-change internals include `__setscheduler_params`, `check_same_owner`, `__setscheduler_dl_pi`, `uclamp_validate`, `uclamp_reset`, `__setscheduler_uclamp`, `user_check_sched_setscheduler`, `__sched_setscheduler`, `_sched_setscheduler`, `sched_setscheduler`, `sched_setattr`, `sched_setattr_nocheck`, and `sched_setscheduler_nocheck`.

Kernel convenience APIs include `sched_set_fifo`, `sched_set_fifo_low`, `sched_set_fifo_secondary`, and `sched_set_normal`. Syscalls include `nice`, `sched_setscheduler`, `sched_setparam`, `sched_setattr`, `sched_getscheduler`, `sched_getparam`, `sched_getattr`, `sched_setaffinity`, `sched_getaffinity`, `sched_yield`, `sched_get_priority_max`, `sched_get_priority_min`, `sched_rr_get_interval`, and the 32-bit time compat RR interval syscall. Affinity helpers include `dl_task_check_affinity`, `__sched_setaffinity`, `sched_setaffinity`, `get_user_cpu_mask`, and `sched_getaffinity`. Yield helpers are `do_sched_yield`, `yield`, and `yield_to`.

## Control Flow
Nice changes validate range and permissions, lock the task's runqueue, and either only store `static_prio` for RT/deadline tasks or use a `sched_change` scope to update static priority, load weight, and effective priority for fair-class tasks. Policy changes first validate policy, flags, priority ranges, deadline parameters, user permissions, LSM hooks, and uclamp values. Deadline transitions take `cpuset_lock` because admission control depends on stable cpuset/root-domain spans. With the task rq locked, `__sched_setscheduler` rejects stop tasks, checks sched_ext policy acceptance, short-circuits no-op changes, enforces RT-group and deadline admission rules, handles policy races by retrying, computes the new class and priority including PI effects, then uses `sched_change` to dequeue, update policy parameters, class, priority, deadline PI state, uclamp, and enqueue flags. Balance callbacks are spliced under preemption disabled and run after unlocking.

`sched_setattr` copies the extensible `sched_attr` ABI with size negotiation, `KEEP_POLICY`, and `KEEP_PARAMS` handling. Getters run under RCU and security checks, returning policy, reset-on-fork, deadline/RT/fair fields, custom CFS slice, and uclamp request values. Affinity setting copies the user mask, verifies ownership or namespace capability, intersects with cpuset constraints, checks deadline root-domain coverage, calls `__set_cpus_allowed_ptr`, and retries against concurrent cpuset changes. Yield locks the current rq, increments schedstat yield counters, calls the class yield hook, unlocks, and schedules; `yield_to` double-locks source and target runqueues and delegates to class-specific `yield_to_task` when both tasks are compatible.

## State And Persistence
The file mutates task fields such as `policy`, `rt_priority`, `static_prio`, `prio`, `normal_prio`, `sched_class`, `sched_reset_on_fork`, `timer_slack_ns`, deadline parameters, CFS slice/load weight, uclamp requests, and CPU affinity/user masks. It also updates runqueue yield stats, deadline root-domain bandwidth accounting through called helpers, and task cpuset-constrained CPU masks. All state is in-memory process and scheduler state.

## Dependencies And Integration Points
It depends on scheduler internals from `sched.h`, autogroup declarations, UAPI `sched_attr`, cpuset APIs, LSM hooks `security_task_*`, capabilities and namespaces, user-copy helpers, RT mutex PI, deadline bandwidth/admission code, sched_ext hooks, utilization clamping, cgroup RT bandwidth, RCU, task reference counting, runqueue locks, balance callbacks, and cpumask allocation/copying. Public integration points are Linux scheduler syscalls and exported kernel helpers used by stop_machine, IRQ threading, kthreads, and other kernel subsystems.

## Risks And Edge Cases
Policy changes are race-prone because target tasks can change policy, migrate, exit, or have PI state while validation is in progress. Deadline admission requires cpuset stability and full root-domain affinity unless admission control is disabled or the task is special schedutil/deadline server work. Uclamp validation must handle `-1` reset values and enable the static key outside scheduler locks. `sched_copy_attr` must preserve ABI compatibility and reject too-small uclamp-aware structures. Affinity changes race with cpuset updates and must restore/adjust `user_cpus_ptr` semantics. Yield is not a progress guarantee, and `yield_to` must avoid use-after-free by requiring an externally stable target task.

## Test Signals
Use scheduler syscall tests for invalid policies, priorities, flags, attr sizes, keep flags, reset-on-fork, uclamp min/max, deadline runtime/deadline/period, permission failures, LSM denials, RLIMIT_NICE/RTPRIO, and affinity masks smaller than cpuset or deadline root domains. Stress with concurrent policy changes, CPU hotplug, cpuset moves, PI boosting, sched_ext configurations, and namespace capability checks. Runtime signals include correct `/proc/<pid>/sched` fields, `sched_getattr` round trips, expected errno values, no lockdep warnings, and stable behavior under PREEMPT_RT.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/sched/syscalls.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/sched/topology.c -->
# sources/distributed-fs/ceph-client/kernel/sched/topology.c

## Purpose
`topology.c` builds, validates, attaches, tears down, and repartitions scheduler domains, groups, capacities, root domains, NUMA masks, asymmetry data, and optional energy-aware scheduling performance domains. It is the scheduler's topology adaptation layer for boot, CPU hotplug, cpuset partitioning, architecture topology changes, NUMA changes, and EAS enablement.

## Important APIs, Types, And Functions
External entry points include `sched_domains_mutex_lock`, `sched_domains_mutex_unlock`, `rebuild_sched_domains_energy`, `rq_attach_root`, `sched_get_rd`, `sched_put_rd`, `init_defrootdomain`, `group_balance_cpu`, `sched_update_asym_prefer_cpu`, `set_sched_topology`, `find_numa_distance`, `arch_sched_node_distance`, `sched_init_numa`, `sched_update_numa`, `sched_domains_numa_masks_set`, `sched_domains_numa_masks_clear`, `sched_numa_find_closest`, `sched_numa_find_nth_cpu`, `sched_numa_hop_mask`, `alloc_sched_domains`, `free_sched_domains`, `sched_init_domains`, `partition_sched_domains`, and weak `arch_update_cpu_topology`.

Major internal helpers include sched-domain debugging functions, `sd_degenerate`, `sd_parent_degenerate`, EAS helpers `sched_is_eas_possible`, `pd_init`, `build_perf_domains`, `sched_energy_set`, root-domain allocation/free helpers, `cpu_attach_domain`, group builders `build_balance_mask`, `build_group_from_child_sched_domain`, `init_overlap_sched_group`, `find_descended_sibling`, `build_overlap_sched_groups`, `get_group`, `build_sched_groups`, `init_sched_groups_capacity`, asymmetry helpers, allocation helpers `__sdt_alloc`, `__sds_alloc`, `__visit_domain_allocation_hell`, `claim_allocations`, domain initialization `sd_init`, `build_sched_domain`, `topology_span_sane`, `adjust_numa_imbalance`, `build_sched_domains`, `detach_destroy_domains`, and `partition_sched_domains_locked`.

## Control Flow
At boot, `sched_init_domains` allocates temporary masks, refreshes architecture topology and asymmetry data, creates a default domain partition from housekeeping CPUs, and calls `build_sched_domains`. Building domains allocates per-topology-level `sched_domain`, `sched_group`, `sched_group_capacity`, shared LLC data, and a root domain. For each CPU it walks topology levels bottom-up, initializes spans and flags with `sd_init`, attaches child/parent links, applies relax-domain attributes, and stops when the domain spans the whole partition. It then validates non-NUMA topology spans, builds normal or overlapping NUMA sched groups, attaches shared LLC state, initializes group capacity/core/asymmetry data, attaches domains and root domains to runqueues via `cpu_attach_domain`, and toggles static keys for asymmetric capacity and cluster support.

`cpu_attach_domain` prunes degenerate parent/child domains, transfers shared state when appropriate, attaches the root domain to the rq, swaps the RCU-protected `rq->sd`, dirties sched-domain sysctls, schedules old domain destruction through RCU, and updates per-CPU cache-domain shortcuts. Domain repartitioning in `partition_sched_domains_locked` compares new cpuset-provided partitions and attributes against current partitions, detaches deleted domains, builds new ones, rebuilds EAS performance domains when needed, updates current partition arrays, refreshes debugfs, and rebuilds deadline root-domain accounting.

NUMA initialization records unique firmware and optional architecture-modified distances, builds per-hop per-node cpumasks, appends NODE/NUMA topology levels to the default topology, classifies topology type, and exposes closest/Nth CPU and hop-mask helpers under RCU. EAS setup checks asymmetric capacity, SMT absence, frequency invariance, cpufreq readiness, sysctl state, and energy model availability before attaching performance-domain lists to each root domain and toggling `sched_energy_present`.

## State And Persistence
State is in memory and protected by `sched_domains_mutex`, CPU hotplug serialization, RCU, refcounts, and rq locks. Persistent runtime objects include per-runqueue `rq->sd` and `rq->rd`, `def_root_domain`, current domain partition arrays `doms_cur`, `ndoms_cur`, and `dattr_cur`, fallback domain masks, per-CPU cache-domain shortcuts (`sd_llc`, `sd_numa`, `sd_asym_*`, IDs and sizes), global asymmetry capacity list, NUMA distance arrays and masks, topology level arrays, EAS static key/sysctl state, root-domain performance-domain lists, and sched-domain shared/group capacity objects. Objects are freed after RCU grace periods where readers can traverse domain trees locklessly.

## Dependencies And Integration Points
The file depends on scheduler internals in `sched.h`, cpumask APIs, CPU hotplug/cpuset partitioning, housekeeping CPU masks, NUMA distance APIs, architecture topology hooks, energy model and schedutil cpufreq integration, static keys, RCU, sysctl, debugfs/sysctl refresh hooks, deadline bandwidth accounting, RT/deadline root-domain helpers, CPU capacity hooks, SMT/cluster/core/package topology masks, isolation masks, bsearch for NUMA CPU ordering, and kernel allocation APIs. It is consumed by fair balancing, wakeup CPU selection, EAS, NUMA balancing, RT push/pull, deadline admission, CPU hotplug, and cpuset exclusive partitioning.

## Risks And Edge Cases
Topology rebuilds are high risk because they change structures read from scheduler hot paths under RCU. Allocation failures must free only unclaimed objects; `claim_allocations` prevents live domain/group storage from being freed. Non-NUMA topology masks must be equal or disjoint; partial overlap breaks group circular lists. NUMA domains intentionally overlap and require balance masks to avoid duplicate or unreachable balancing paths. Degenerate domains must be removed without losing shared flags or group capacity references. CPU hotplug can require NUMA topology rebuild when the first CPU of a node comes online or the last goes offline. EAS must not enable on unsupported SMT, missing EM, non-invariant frequency, or cpufreq-not-ready configurations. Static key reference counts for asymmetry/cluster must match attach/detach.

## Test Signals
Key signals are successful boot across SMT, cluster, MC, NUMA, asymmetric-capacity, isolated-CPU, and non-NUMA systems; `sched_verbose` domain debug output without span/group errors; CPU hotplug stress; cpuset partition rebuild tests; NUMA distance and hop-mask tests; EAS sysctl toggling and energy-model validation; lockdep/RCU validation during domain rebuild; deadline and RT balancing after root-domain changes; and no leaks or double frees in failure-injection allocation tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/sched/topology.c -->
