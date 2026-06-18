# Research: sources/distributed-fs/ceph-client/kernel/sched/fair.c

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-006055`: lines 1-9419, `Docs/researches/chunks/subset-b-006055_research.md`
- `subset-b-006056`: lines 9420-14312, `Docs/researches/chunks/subset-b-006056_research.md`

## Chunk Research

### subset-b-006055: lines 1-9419

# sources/distributed-fs/ceph-client/kernel/sched/fair.c lines 1-9419

## Scope

This chunk covers the first 9,419 lines of the Linux fair scheduler implementation carried in the Ceph client kernel source snapshot. It starts at the file header and includes CFS/EEVDF tunables, weighted virtual-runtime math, group-scheduling hierarchy helpers, PELT load tracking, automatic NUMA balancing and memory-tiering policy, group share propagation, CFS bandwidth throttling, enqueue/dequeue, wakeup CPU selection, utilization and energy-aware placement, migration hooks, wakeup preemption, task picking, put-prev, and yield handling. The mapped range ends inside the introductory comment for the load-balancing machinery; the actual periodic/new-idle load balancer implementation continues after this chunk.

Although this repository is Ceph-oriented, this file is generic kernel scheduler infrastructure. Ceph kernel threads, messenger workqueues, and CephFS client tasks are scheduled through it, but no Ceph filesystem protocol logic is implemented here.

## Purpose

`kernel/sched/fair.c` implements the fair scheduling class for `SCHED_NORMAL`, `SCHED_BATCH`, and `SCHED_IDLE` tasks. In this chunk it:

- Maintains CFS runqueue state (`struct cfs_rq`) and schedulable entities (`struct sched_entity`) using EEVDF: eligible entities are selected by earliest virtual deadline, while virtual lag and weighted average virtual runtime preserve fairness.
- Tracks hierarchical task-group runqueues, group entities, idle groups, per-runqueue leaf lists, and task-group load contributions when `CONFIG_FAIR_GROUP_SCHED` is enabled.
- Updates PELT load, runnable, utilization, and utilization-estimate signals used by scheduling, load balancing, cpufreq/schedutil, utilization clamping, misfit detection, and energy-aware scheduling.
- Implements automatic NUMA balancing: scan scheduling, PTE hinting work, fault accounting, numa-group formation, preferred-node selection, page migration decisions, and task migration or swap choices.
- Enforces CFS bandwidth quotas for cgroups through per-task-group quota pools, per-CPU `cfs_rq` runtime accounting, throttled limbo lists, hrtimer replenishment, slack redistribution, async remote unthrottling, and CPU hotplug cleanup.
- Provides the fair scheduling class callbacks for enqueue, dequeue, CPU selection on wake/fork/exec, migration accounting, task death, affinity changes, wakeup preemption, picking the next task, putting the previous task, and `sched_yield()` / `yield_to()`.

The code is hot-path scheduler code. Many helpers run under `rq->lock`, with IRQs disabled, during context switch, in wakeup paths, or from hrtimer/task-work callbacks.

## Important APIs, Types, And Functions

Tunables and capacity helpers:

- `sysctl_sched_tunable_scaling`, `sysctl_sched_base_slice`, `normalized_sysctl_sched_base_slice`, and `sysctl_sched_migration_cost` control EEVDF slice/deadline and wakeup preemption thresholds.
- `sched_fair_sysctls[]` registers `sched_cfs_bandwidth_slice_us` and `numa_balancing_promote_rate_limit_MBps` when the matching configs are enabled.
- `sched_update_scaling()` and `sched_init_granularity()` rescale `sched_base_slice` based on online CPU count and `SCHED_TUNABLESCALING_*`.
- `fits_capacity()`, `capacity_greater()`, `capacity_of()`, `get_actual_cpu_capacity()`, `util_fits_cpu()`, and `task_fits_cpu()` compare task utilization and uclamp hints with CPU capacity, hardware pressure, and cpufreq pressure.
- `arch_asym_cpu_priority()` is a weak default used by asymmetric packing logic outside this chunk.

EEVDF and runqueue tree machinery:

- `calc_delta_fair()` and `__calc_delta()` convert real runtime to weighted virtual runtime using `struct load_weight`. The 32-bit path caches inverse weights; the 64-bit path uses direct division.
- `avg_vruntime()`, `avg_vruntime_weight()`, `entity_key()`, `sum_w_vruntime_add()`, `sum_w_vruntime_sub()`, and `update_zero_vruntime()` maintain a stable weighted-average virtual time for each `cfs_rq`.
- `entity_lag()`, `update_entity_lag()`, `vruntime_eligible()`, and `entity_eligible()` compute bounded virtual lag and decide whether an entity is owed service.
- `update_deadline()`, `place_entity()`, `set_protect_slice()`, `update_protect_slice()`, `protect_slice()`, and `cancel_protect_slice()` maintain EEVDF request sizes, virtual deadlines, lag-preserving placement, and run-to-parity slice protection.
- `__enqueue_entity()`, `__dequeue_entity()`, `__pick_root_entity()`, `__pick_first_entity()`, `__pick_last_entity()`, and `pick_eevdf()` manage the augmented rb-tree ordered by virtual deadline and augmented with minimum vruntime plus min/max slice values.
- `min_vruntime_update()` and `RB_DECLARE_CALLBACKS(... min_vruntime_cb ...)` maintain rb-tree augmentation after insert, erase, and propagation.

Group scheduling:

- `for_each_sched_entity()`, `list_add_leaf_cfs_rq()`, `list_del_leaf_cfs_rq()`, `assert_list_leaf_cfs_rq()`, `find_matching_se()`, `parent_entity()`, `is_same_group()`, `tg_is_idle()`, `cfs_rq_is_idle()`, and `se_is_idle()` abstract task-group hierarchy traversal and idle-group behavior.
- `calc_group_shares()` and `update_cfs_group()` approximate hierarchical group shares from `tg->shares`, `cfs_rq->load.weight`, `cfs_rq->avg.load_avg`, and `tg->load_avg`.
- `update_tg_load_avg()`, `clear_tg_load_avg()`, `update_tg_cfs_util()`, `update_tg_cfs_runnable()`, `update_tg_cfs_load()`, `add_tg_cfs_propagate()`, `propagate_entity_load_avg()`, and `skip_blocked_update()` propagate PELT changes from child group runqueues to their parent group entities.

PELT, utilization, and stats:

- `init_entity_runnable_average()` and `post_init_entity_util_avg()` seed new task and group entity load/utilization state.
- `update_se()`, `update_curr_common()`, `update_curr()`, and `update_curr_fair()` account runtime to the donor/current task, update `sum_exec_runtime`, trace runtime, cgroup CPU time, `vruntime`, deadlines, CFS quota runtime, and lazy rescheduling.
- `update_stats_*_fair()` helpers maintain schedstat wait/sleep/block/slice metrics when schedstats are enabled.
- `update_cfs_rq_load_avg()`, `attach_entity_load_avg()`, `detach_entity_load_avg()`, `update_load_avg()`, `sync_entity_load_avg()`, and `remove_entity_load_avg()` keep entity and runqueue PELT windows synchronized during enqueue, dequeue, migration, and task exit.
- `migrate_se_pelt_lag()` estimates missed PELT decay when a task leaves an idle CPU whose clock may be stale.
- `task_util()`, `task_runnable()`, `task_util_est()`, `util_est_enqueue()`, `util_est_dequeue()`, and `util_est_update()` maintain EWMA-based utilization estimates.
- `cpu_util()`, `cpu_util_cfs()`, `cpu_util_cfs_boost()`, `cpu_util_without()`, `effective_cpu_util()`, and `sched_cpu_util()` expose CFS/RT/DL/IRQ/uclamp-adjusted CPU utilization to cpufreq, EAS, and balancing code.

NUMA balancing and memory tiering:

- `struct numa_group`, `struct numa_stats`, and `struct task_numa_env` carry NUMA group fault state, per-node load/util snapshots, and migration search state.
- `task_numa_fault()`, `task_numa_group()`, `task_numa_placement()`, `numa_group_count_active_nodes()`, `preferred_group_nid()`, and `update_task_scan_period()` aggregate hinting faults, detect shared/private memory, form task groups, select preferred nodes, and adapt scan periods.
- `task_numa_work()`, `task_tick_numa()`, `init_numa_balancing()`, `reset_ptenuma_scan()`, and `vma_is_accessed()` schedule and perform task-work PTE scanning with VMA filtering, per-VMA PID activity tracking, scan offsets, and overhead throttling.
- `should_numa_migrate_memory()`, `numa_hint_fault_latency()`, `pgdat_free_space_enough()`, `numa_promotion_rate_limit()`, and `numa_promotion_adjust_threshold()` decide page migration, including memory-tiering promotion based on hotness, fast-memory free space, and per-node promotion throughput.
- `task_numa_migrate()`, `task_numa_find_cpu()`, `task_numa_compare()`, `task_numa_assign()`, `numa_migrate_preferred()`, and `update_numa_stats()` choose CPU migration or task swap targets while respecting load balance, cpumasks, idle CPUs, active NUMA groups, and source/destination node pressure.
- `task_numa_free()` releases or resets per-task NUMA fault arrays and drops `numa_group` references.

CFS bandwidth control:

- `cfs_bandwidth_usage_inc()`, `cfs_bandwidth_usage_dec()`, and `cfs_bandwidth_used()` gate quota code with a static key when jump labels are available.
- `init_cfs_bandwidth()`, `destroy_cfs_bandwidth()`, `start_cfs_bandwidth()`, `init_cfs_rq_runtime()`, `update_runtime_enabled()`, and `unthrottle_offline_cfs_rqs()` initialize timers/lists, handle CPU online/offline, and clean remote unthrottle work.
- `__refill_cfs_bandwidth_runtime()`, `__assign_cfs_rq_runtime()`, `assign_cfs_rq_runtime()`, `account_cfs_rq_runtime()`, `check_enqueue_throttle()`, and `check_cfs_rq_runtime()` debit runtime and trigger throttling when a quota is exhausted.
- `throttle_cfs_rq()`, `unthrottle_cfs_rq()`, `tg_throttle_down()`, `tg_unthrottle_up()`, `record_throttle_clock()`, `task_throttle_setup_work()`, and `throttle_cfs_rq_work()` move over-quota runqueues/tasks into throttled state, freeze PELT clocks, defer user-return task throttling, and re-enqueue limbo tasks.
- `distribute_cfs_runtime()`, `__unthrottle_cfs_rq_async()`, `unthrottle_cfs_rq_async()`, `__cfsb_csd_unthrottle()`, `sched_cfs_period_timer()`, `do_sched_cfs_period_timer()`, `sched_cfs_slack_timer()`, and `do_sched_cfs_slack_timer()` replenish and distribute quota across throttled `cfs_rq`s using hrtimers, RCU lists, per-rq locks, and remote CSD callbacks.
- `return_cfs_rq_runtime()` and `__return_cfs_rq_runtime()` return excess local runtime to the task-group pool and may start slack redistribution.
- `cfs_task_bw_constrained()` and `sched_fair_update_stop_tick()` integrate CFS quotas with nohz-full tick dependency handling.

Scheduling-class operations and CPU selection:

- `enqueue_entity()`, `dequeue_entity()`, `requeue_delayed_entity()`, `set_delayed()`, `clear_delayed()`, `set_next_entity()`, `put_prev_entity()`, `pick_next_entity()`, and `entity_tick()` are the core entity-level enqueue/dequeue/pick/tick operations.
- `enqueue_task_fair()`, `dequeue_entities()`, and `dequeue_task_fair()` update hierarchical `h_nr_*` counters, utilization estimates, group slices, overutilized state, delayed-dequeue state, throttling state, and `rq->nr_running`.
- `wake_affine_idle()`, `wake_affine_weight()`, `wake_affine()`, `wake_wide()`, `record_wakee()`, `sched_balance_find_dst_group_cpu()`, `sched_balance_find_dst_cpu()`, `select_idle_core()`, `select_idle_smt()`, `select_idle_cpu()`, `select_idle_capacity()`, and `select_idle_sibling()` implement the wakeup fast path across current/previous CPUs, LLC domains, SMT siblings, asymmetric capacity domains, cpuset masks, and core-scheduling cookies.
- `struct energy_env`, `eenv_task_busy_time()`, `eenv_pd_busy_time()`, `eenv_pd_max_util()`, `compute_energy()`, and `find_energy_efficient_cpu()` implement the Energy Aware Scheduling candidate evaluation path using performance domains and the energy model.
- `select_task_rq_fair()` is the fair-class CPU selection callback for wake, fork, and exec. It tries current-CPU hints, EAS when the root domain is not overutilized, wake-affine cache locality, slow-domain balancing, and idle-sibling search.
- `migrate_task_rq_fair()`, `task_dead_fair()`, `set_task_max_allowed_capacity()`, and `set_cpus_allowed_fair()` handle migration PELT detachment, NUMA scan-period resets, delayed-dequeue cleanup at task death, and affinity-driven misfit metadata.
- `wakeup_preempt_fair()`, `set_next_buddy()`, `set_preempt_buddy()`, and `preempt_sync()` decide whether a newly woken task should preempt the current donor task.
- `pick_task_fair()`, `pick_next_task_fair()`, `fair_server_pick_task()`, `fair_server_init()`, `put_prev_task_fair()`, `yield_task_fair()`, and `yield_to_task_fair()` connect entity picking to the scheduler core, deadline-server fair scheduling support, and yield semantics.

## Control Flow

Normal wakeup enqueue starts in `select_task_rq_fair()` and `enqueue_task_fair()`. CPU selection first handles explicit current-CPU wakeups, then may choose an energy-efficient CPU if the root domain is not overutilized. If EAS does not return a CPU, the code considers wake-affine locality between the waker CPU and previous CPU, slow-domain idlest-group selection for fork/exec/balance flags, and idle-sibling scanning in LLC or asymmetric-capacity domains. Enqueue then updates util-est before schedutil signals, walks from the task entity up the group hierarchy, places each new entity using lag-aware EEVDF placement, attaches/updates PELT state, recomputes group shares, updates hierarchical runnable/queued/idle counters, starts the fair deadline server for the first queued entity, increments `rq->nr_running`, updates overutilized state, and arms hrtick if configured.

Runtime accounting flows through `update_curr()`. It accounts elapsed `rq_clock_task()` time to the selected donor entity, updates task/group runtime statistics, cgroup CPU time, `vruntime`, and virtual deadlines. Runtime is debited from CFS bandwidth quota when enabled. If the entity consumes its requested slice, loses slice protection, or quota expires, the current task is lazily rescheduled and buddy hints are cleared.

Task selection is EEVDF-based. `pick_task_fair()` starts at the root `cfs_rq`, updates the current entity if it is still queued, checks quota throttling, and repeatedly calls `pick_next_entity()` / `pick_eevdf()` down group runqueues until it reaches a task entity. `pick_eevdf()` uses the augmented rb-tree to prune ineligible subtrees by minimum vruntime and chooses the eligible entity with the earliest virtual deadline, while optionally preserving the current entity during protected slice intervals. If a selected entity is delayed-dequeued, it is actually dequeued and the pick restarts.

Context switch setup is optimized for group scheduling. `pick_next_task_fair()` can avoid putting and setting the entire hierarchy when previous and next tasks share ancestors; it walks only the divergent portions, calling `put_prev_entity()` and `set_next_entity()` as needed. If no fair task is runnable, it may call `sched_balance_newidle()` before returning idle or `RETRY_TASK`.

Dequeue starts in `dequeue_task_fair()` and `dequeue_entities()`. The code handles already-throttled tasks separately, updates util-est EWMA on sleep, walks up the entity hierarchy, and calls `dequeue_entity()` for each level. `dequeue_entity()` may intentionally delay a sleeping ineligible entity when `DELAY_DEQUEUE` is enabled: it updates lag, marks `sched_delayed`, and keeps the entity competing on the rb-tree until it becomes eligible. Complete dequeue updates PELT, schedstats, lag, relative deadline state, rb-tree membership, hierarchical counts, returned quota runtime, group shares, idle PELT clocks, and throttled hierarchy clocks.

CFS bandwidth control runs in both scheduler and timer paths. When runtime is exhausted, `account_cfs_rq_runtime()` requests another slice from the task group pool; if none is available, `check_cfs_rq_runtime()` / `throttle_cfs_rq()` put the `cfs_rq` on the bandwidth's throttled list and walk the task-group subtree to increment throttle counts and freeze PELT clocks. Period hrtimers refill quota in `sched_cfs_period_timer()` and call `distribute_cfs_runtime()` to give positive runtime to throttled runqueues. Local unthrottles happen directly; remote unthrottles are queued on `rq->cfsb_csd_list` and processed through `smp_call_function_single_async()`. Limbo tasks are re-enqueued during `tg_unthrottle_up()`.

Automatic NUMA balancing has a tick-to-task-work-to-fault feedback loop. `task_tick_numa()` checks task runtime against `numa_scan_period` and queues `task_numa_work()` with `task_work_add()`. The task work scans eligible VMAs under `mmap_read_trylock()`, marks ranges `PROT_NONE` via `change_prot_numa()`, records scan offsets and per-VMA PID activity, and caps overhead by charging additional `node_stamp` runtime. Later hinting faults call `task_numa_fault()`, which allocates fault arrays if needed, classifies private/shared/local/remote faults, can join numa groups, periodically updates placement, and records fault buckets. Placement uses weighted task/group faults to set `numa_preferred_nid` and may migrate or swap tasks toward preferred nodes.

Energy-aware wakeup placement evaluates performance domains when the root domain is not already overutilized. `find_energy_efficient_cpu()` synchronizes the waking task's PELT signal, skips zero-util non-boosted tasks, selects max-spare-capacity candidates in each performance domain, computes base energy and candidate energy using `compute_energy()`, and prefers CPUs that fit uclamp/capacity requirements with lower energy deltas than the previous CPU.

Wakeup preemption compares the current donor entity and wakee at a common group level. It avoids preemption for non-fair wakees, already-rescheduled tasks, throttled wakees, batch/idle policy wakees, fork wakeups, and delayed-dequeue wakees. It can override slice protection for idle-to-non-idle preemption or shorter-slice wakees, can nominate a next buddy, and ultimately asks EEVDF whether the wakee would be picked. If so, it cancels protection as needed and requests lazy reschedule.

Yield handling is intentionally simple. `yield_task_fair()` updates the current entity and, only if it is eligible, forfeits the remaining virtual slice by moving `vruntime` to `deadline` and refreshing the deadline. `yield_to_task_fair()` nominates the target as next buddy if it is on a runnable fair queue, then calls normal yield.

## State And Persistence Behavior

Most state is in memory and lifetime-bound to tasks, runqueues, task groups, VMAs, NUMA groups, and cgroup CPU bandwidth objects. There is no disk persistence in this chunk.

Persistent scheduler state includes:

- Per-task `sched_entity` fields such as `load`, `avg`, `vruntime`, `deadline`, `slice`, `custom_slice`, `vlag`, `vprot`, `rel_deadline`, `sched_delayed`, `exec_start`, and `sum_exec_runtime`.
- Per-CPU `cfs_rq` fields such as the augmented `tasks_timeline`, `curr`, `next`, `load`, `avg`, `sum_w_vruntime`, `sum_weight`, `zero_vruntime`, hierarchical queued/runnable/idle counters, PELT idle/throttle timestamps, quota runtime, and throttled lists.
- Per-rq fair state such as `cfs_tasks`, leaf `cfs_rq` lists, `nr_numa_running`, `nr_preferred_running`, `misfit_task_load`, nohz masks, CFS bandwidth CSD queues, and root-domain `overutilized`.
- Per-task-group state such as `shares`, `load_avg`, per-CPU `cfs_rq`/group-entity arrays, `cfs_bandwidth` quota/period/burst/runtime counters, throttled lists, and hierarchical quota.
- PELT state persists across sleep and migration so blocked load can influence placement and frequency decisions. Removed task contributions are staged in `cfs_rq->removed` and folded into a later `update_cfs_rq_load_avg()`.
- Util-est state persists on tasks and root CFS runqueues. Task util estimates are marked with `UTIL_AVG_UNCHANGED` to avoid repeated EWMA updates during one activation.
- NUMA state persists in task fields (`numa_faults`, locality buckets, `numa_scan_period`, `numa_scan_seq`, `node_stamp`, `numa_preferred_nid`, `numa_group`) and mm/VMA fields (`numa_next_scan`, `numa_scan_offset`, `numa_scan_seq`, `vma->numab_state`). `task_numa_free()` either resets or frees this state depending on whether the task is exiting finally.
- NUMA groups are refcounted, protected by RCU, and store aggregate fault arrays, total faults, active node counts, and max CPU faults. Tasks join/leave groups by moving their fault contributions under group locks.
- Memory-tiering promotion state persists in `pgdat` counters and threshold/rate-limit fields such as `nbp_rl_start`, `nbp_rl_nr_cand`, `nbp_th_start`, `nbp_th_nr_cand`, and `nbp_threshold`.
- CFS bandwidth state persists across periods in `cfs_bandwidth` counters (`runtime`, `runtime_snap`, `nr_periods`, `nr_throttled`, `throttled_time`, `burst_time`, `nr_burst`, `idle`, `period_active`, `slack_started`). Per-`cfs_rq` throttling persists until runtime is replenished and the hierarchy is unthrottled.

Locking and memory ordering are integral to persistence. Runqueue-local scheduling state is generally protected by `rq->lock`; task-group bandwidth pools use `cfs_b->lock`; NUMA groups use `ng->lock` plus RCU; PELT idle-clock copies use paired 64/32 copy helpers and memory barriers; task-work sentinels prevent duplicate NUMA or throttle work; throttled lists are RCU-walked when timers distribute runtime.

## Dependencies And Integration Points

This chunk depends on scheduler core types and helpers from `kernel/sched/sched.h`, `stats.h`, `autogroup.h`, and `pelt.h`, plus kernel headers for topology, cpumasks, energy model, cpuidle, memory policy, mm/VMA walking, cgroups, PSI, refcounts, task work, hrtimers, RCU, and rb-tree augmentation.

Important integration points include:

- Scheduler core: `struct sched_class fair_sched_class`, `rq` locking, `add_nr_running()`, `sub_nr_running()`, `resched_curr_lazy()`, `resched_curr()`, `put_prev_set_next_task()`, `task_rq_lock()`, `migrate_task_to()`, `migrate_swap()`, `set_cpus_allowed_common()`, `__block_task()`, and scheduler feature flags.
- Deadline server support: `dl_server_update()`, `dl_server_start()`, `dl_server_init()`, and `__put_prev_set_next_dl_server()` let fair work be served through a deadline-server entity.
- PELT and tracing: `__update_load_avg_*()`, `get_pelt_divider()`, `cfs_rq_clock_pelt()`, `update_idle_cfs_rq_clock_pelt()`, `trace_pelt_*`, `trace_sched_stat_runtime()`, `trace_sched_compute_energy_tp()`, and NUMA tracepoints.
- Cpufreq and uclamp: `cpufreq_update_util()`, `sugov_effective_cpu_perf()`, `uclamp_eff_value()`, `uclamp_rq_get()`, `uclamp_rq_is_idle()`, and root-domain overutilized tracking.
- CPU topology and load balancing: scheduler domains (`sd_llc`, `sd_asym_cpucapacity`, `sd_numa`), sched groups, performance domains, SMT masks, cluster/static keys, core-scheduling cookie checks, and CPU capacity/asymmetry lists.
- Energy model: `em_cpu_energy()` consumes `struct perf_domain` and `em_perf_domain` data for EAS placement.
- NUMA/mm: `node_distance()`, `sched_numa_topology_type`, `mmap_read_trylock()`, VMA iteration, `vma_migratable()`, `vma_policy_mof()`, `change_prot_numa()`, hugetlb checks, cpuset mems, memory tiers, folio cpupid/access-time helpers, and page migration fault flags.
- Cgroups and bandwidth: task groups, cgroup CPU quota fields, `walk_tg_tree_from()`, `task_groups` RCU list, cgroup CPU accounting, `cfs_task_bw_constrained()`, and nohz-full tick dependency bits.
- CPU hotplug/nohz: online/active CPU masks, `tick_nohz_full_cpu()`, `tick_nohz_dep_set_cpu()`, nohz idle masks, per-CPU load-balance masks, and offline unthrottle handling.
- Security/observability indirectly: scheduler tracepoints, schedstats, PSI/cgroup accounting, and sysctls expose behavior to userspace and observability tools. Ceph workloads interact here as ordinary tasks/kthreads whose latency, NUMA locality, cgroup quota, and CPU frequency behavior are shaped by these paths.

## Risks And Edge Cases

EEVDF arithmetic is precision-sensitive. `avg_vruntime()` uses relative weighted sums to avoid overflow, and 64-bit eligibility may require `__int128` or overflow fallback. Reweighting and placement deliberately preserve lag and relative deadlines; small mistakes can create unfair service, negative lag amplification, or rb-tree order/augmentation corruption.

Delayed dequeue is semantically subtle. A sleeping ineligible entity can remain on the runqueue as `sched_delayed` until it becomes eligible, but special dequeue paths, throttling, task death, and enqueue requeue paths must clear or complete the delayed state exactly once. The comments around `__block_task()` warn that the task pointer may become invalid after delayed dequeue completion.

Group scheduling requires bottom-up leaf-list ordering. `list_add_leaf_cfs_rq()` uses `tmp_alone_branch` to keep child `cfs_rq`s before parents; throttling/unthrottling during enqueue can disturb this if list updates are reordered.

PELT state can drift across migration, idle, throttling, and removal. The code compensates for stale idle clocks, freezes PELT while throttled, stores removed contributions under a separate lock, and aligns entity/cfs_rq PELT windows on attach. Incorrect ordering can inflate util, lose blocked load, or mislead schedutil/EAS.

Runtime accounting has proxy-exec details. `update_se()` accounts task runtime to `rq->curr` while CFS scheduling selection can be based on `rq->donor`; cgroup time is charged to the donor. Confusing these roles can break CPU time accounting.

CFS bandwidth throttling has several races. Runtime can become available while a runqueue is committing to throttle; remote unthrottle CSD callbacks can race with group destruction; throttled tasks can be moved between groups while task-work throttling is pending; and offline CPUs need forced unthrottle because their task clock no longer advances.

NUMA balancing is intentionally approximate and racy. `mm->numa_scan_seq` is updated without exclusive mmap ownership, VMA PID activity is a sampling filter, task/group fault arrays are decayed over long windows, and migration decisions must avoid ping-pong from small improvements. The code includes hysteresis, scan-period backoff, and active-node handling to avoid instability.

Memory-tiering promotion can hurt latency if rate limits or hotness thresholds are wrong. `should_numa_migrate_memory()` bypasses normal private/shared logic for slow-memory pages, adjusts thresholds based on promotion candidates, and treats plentiful fast-memory free space specially. Bugs here can over-promote cold pages or strand hot pages.

Wakeup CPU selection balances competing goals: cache locality, idle search cost, SMT/core idleness, asymmetric capacity, uclamp hints, core-scheduling cookies, EAS energy, and cpuset constraints. Using stale PELT/util-est or ignoring masks can place work on disallowed, overutilized, or energy-inefficient CPUs.

Wakeup preemption must preserve EEVDF fairness while serving latency. `WF_SYNC`, `PREEMPT_SHORT`, next-buddy nomination, idle-policy checks, and slice protection all interact. Overeager preemption can harm throughput and fairness; under-preemption can hurt interactive latency.

The range ends before the actual load-balancing algorithms. This chunk declares and calls `sched_balance_newidle()` and includes the first lines of the load-balancing overview, but imbalance computation, detach/attach balancing, nohz idle balance, and related structures are outside this report.

## Test Signals

Useful validation signals for this chunk include:

- Scheduler selftests and kernel builds across `CONFIG_FAIR_GROUP_SCHED`, `CONFIG_CFS_BANDWIDTH`, `CONFIG_NUMA_BALANCING`, `CONFIG_SCHED_SMT`, `CONFIG_SCHED_HRTICK`, `CONFIG_NO_HZ_COMMON`, `CONFIG_NO_HZ_FULL`, `CONFIG_UCLAMP_TASK`, EAS/energy-model, cgroup, and non-64-bit configurations.
- Lockdep, KCSAN, KASAN, UBSAN, RCU stall detection, and scheduler debug under heavy fork/exec/wake/sleep/migrate/yield workloads.
- Fairness tests that compare service ratios across nice levels, custom slices, task groups, idle policy tasks, delayed dequeue, yield/yield_to, and mixed SCHED_NORMAL/SCHED_BATCH/SCHED_IDLE workloads.
- EEVDF-specific tests for eligibility, deadline ordering, run-to-parity slice protection, lag preservation across enqueue/dequeue/reweight, and rb-tree augmentation after insertion/removal.
- PELT/utilization tests across task sleep/wake, CPU migration after long idle, task exit removal, group propagation, throttled PELT clocks, util-est EWMA updates, and schedutil frequency changes.
- CFS bandwidth cgroup tests for quota exhaustion, hierarchical quotas, burst accounting, throttled limbo tasks, remote unthrottle, slack redistribution, period timer overrun scaling, nohz-full tick dependency, CPU hotplug while throttled, and group destruction with pending CSD work.
- NUMA balancing tests for PTE scan cadence, VMA skip reasons, per-VMA PID activity, task group formation, preferred node convergence, task migration/swap, scan-period backoff, cpuset mems restrictions, and `task_numa_free()` cleanup.
- Memory-tiering tests for hot slow-memory page promotion, promotion rate limiting, dynamic threshold adjustment, fast-memory free-space bypass, invalid cpupid handling, and migration denial to memoryless nodes.
- Wakeup placement tests covering `WF_CURRENT_CPU`, `WF_SYNC`, fork/exec paths, wake-wide detection, wake-affine idle/weight choices, idle sibling search, SMT idle-core tracking, asymmetric-capacity CPU fitting, uclamp min/max constraints, core-scheduling cookies, and cpuset masks.
- EAS tests comparing chosen CPUs and `trace_sched_compute_energy` output under different performance domains, IRQ pressure, uclamp hints, RT/DL load, overutilized root-domain state, and zero-util forked tasks.
- Preemption tests for non-fair wakees, idle-to-normal preemption, batch/idle policy non-preemption, shorter-slice `PREEMPT_SHORT`, delayed wakees, next-buddy behavior, and lazy reschedule requests.

## Chunk Boundary Notes

This chunk contains the fair-class local scheduling, wakeup placement, NUMA, PELT, EAS, and bandwidth machinery up to the start of the load-balancing section. The following chunk should cover the load-balancer data structures and algorithms that satisfy the fairness equations introduced at lines 9403-9419, plus the final `fair_sched_class` registration and remaining lifecycle hooks.

### subset-b-006056: lines 9420-14312

# sources/distributed-fs/ceph-client/kernel/sched/fair.c lines 9420-14312

## Scope

This chunk covers the later `kernel/sched/fair.c` implementation for CFS load balancing, blocked-load decay, periodic and newly-idle balancing, NOHZ idle load balancing, active balance CPU stopper work, sched-core fairness comparison, CFS scheduler-class callbacks, fair task-group allocation and share/idle updates, debug/stat output, and fair-class initialization.

The range starts in the explanatory block for CFS load balance complexity and cgroup weighting, then defines the balancing environment and migration helpers. It ends with `init_sched_fair_class()`, which allocates per-CPU masks, initializes CFS bandwidth cross-calls, opens `SCHED_SOFTIRQ`, and initializes NOHZ idle-balance state.

## Purpose

The code in this chunk is the main CFS balancing and lifecycle control plane. Its primary job is to keep runnable fair-class work distributed across scheduling domains while respecting task affinity, CPU capacity, NUMA locality, cache-hotness, cgroup hierarchy, CFS bandwidth throttling, SMT/core-scheduling constraints, asymmetric CPU priorities, energy-aware scheduling boundaries, and tickless idle CPUs.

Major responsibilities include:

- Deciding whether a task can be migrated from one runqueue to another.
- Detaching CFS tasks from a source runqueue and attaching them to a destination runqueue.
- Updating PELT blocked load/utilization for CFS, RT, deadline, IRQ, and hardware load signals.
- Summarizing sched-group and sched-domain load, utilization, capacity, runnable count, idle CPUs, misfit tasks, overutilization, NUMA placement, and SMT/asymmetric-packing states.
- Choosing a busiest source group and source runqueue, computing the imbalance quantity, and selecting a migration mode: load, utilization, task count, or misfit task.
- Running periodic balance from `SCHED_SOFTIRQ`, aggressive newly-idle balance before a CPU goes idle, and NOHZ idle balance on behalf of CPUs with stopped ticks.
- Falling back to active balancing via CPU stopper work when normal pull balancing cannot move a currently running or otherwise hard-to-pull task.
- Maintaining CFS scheduler-class hooks for ticks, priority changes, task policy/group transitions, next-task setup, group allocation, group share changes, and debug output.

## Important APIs, Types, and Functions

- `max_load_balance_interval` caps the domain balance interval and is scaled by `update_max_interval()` as online CPU count grows.
- `enum group_type` ranks sched groups by pull priority: spare capacity, fully busy, misfit task, SMT balance, asymmetric packing, affinity imbalance, and overloaded.
- `enum migration_type` tells `detach_tasks()` whether `env->imbalance` is measured as load, utilization, task count, or one misfit task.
- `struct lb_env` carries a single balancing pass: sched domain, source/destination runqueues and CPUs, destination group mask, current imbalance, allowed CPU mask, balancing flags, iteration counters, NUMA queue class, migration type, idle state, and detached task list.
- `task_hot()` blocks migrations that would likely lose cache locality. It treats idle-policy tasks and SMT siblings as cold, honors `CACHE_HOT_BUDDY`, `sysctl_sched_migration_cost`, and core-scheduling cookie compatibility.
- `migrate_degrades_locality()` under `CONFIG_NUMA_BALANCING` compares source and destination nodes against task or NUMA-group fault weights and preferred node state. It can return negative to encourage migration to the preferred node.
- `task_is_ineligible_on_dst_cpu()` avoids moving a lag-ineligible entity onto a queued destination CFS runqueue when `PLACE_LAG` is enabled, except after balance failures.
- `can_migrate_task()` is the migration gate. It rejects delayed-dequeued tasks for non-load balancing, throttled CFS hierarchies, ineligible lag placement, per-CPU kthreads, blocked proxy-exec tasks, CPU-affinity misses, current/running donors, cache-hot tasks, and NUMA-locality regressions unless active balance or repeated failures justify migration.
- `detach_task()`, `detach_one_task()`, `detach_tasks()`, and `attach_tasks()` implement the actual move. They deactivate tasks on the source rq, change `task_cpu`, keep detached tasks on `env->tasks`, then attach them under the destination rq lock.
- `__update_blocked_others()`, `__update_blocked_fair()`, `update_cfs_rq_h_load()`, `task_h_load()`, and `__sched_balance_update_blocked_averages()` maintain decayed load/utilization and hierarchical task load for balancing and cgroup accounting.
- `struct sg_lb_stats` and `struct sd_lb_stats` are the statistics aggregates for group-level and domain-level balancing decisions.
- `scale_rt_capacity()`, `update_cpu_capacity()`, and `update_group_capacity()` compute CFS-available capacity after RT, deadline, IRQ, hardware, and child-domain capacity accounting.
- `group_has_capacity()`, `group_is_overloaded()`, `group_classify()`, `sched_group_asym()`, `smt_balance()`, and `sibling_imbalance()` classify groups and determine whether spare capacity, SMT pressure, asym packing, misfit tasks, or overload should drive balancing.
- `update_sg_lb_stats()`, `update_sd_pick_busiest()`, and `update_sd_lb_stats()` gather CPU/runqueue signals across sched groups, update root-domain overloaded/overutilized flags, select a busiest group, and update select-idle scan hints.
- `sched_balance_find_dst_group()` is the wakeup-side idlest-group selector. It compares local and candidate groups while accounting for affinity, core cookies, NUMA preference, capacity fitting, idle CPUs, and average load.
- `calculate_imbalance()` converts group classifications into the concrete `env->migration_type` and `env->imbalance`.
- `sched_balance_find_src_group()` decides whether the domain is actually imbalanced and returns the busiest source group when pulling work is warranted.
- `sched_balance_find_src_rq()` picks the busiest runqueue inside a source group according to the active migration mode and NUMA queue class.
- `need_active_balance()` and `active_load_balance_cpu_stop()` escalate to CPU stopper context for asym packing, hard imbalance, reduced-capacity single-task CPUs, and misfit tasks.
- `should_we_balance()` elects which CPU in a group performs a periodic balance pass, preferring newly idle CPUs, idle cores before idle SMT siblings, then the group balance CPU.
- `sched_balance_rq()` is the main balancing transaction. It builds `lb_env`, serializes large domains when needed, finds source group/rq, detaches and attaches tasks, handles pinned tasks and alternate destinations, updates balance stats, triggers active balance, and backs off domain intervals.
- `sched_balance_domains()` walks scheduling domains on periodic softirq ticks, updates new-idle cost decay, runs due balances, and computes `rq->next_balance`.
- NOHZ helpers `find_new_ilb()`, `kick_ilb()`, `nohz_balancer_kick()`, `nohz_balance_enter_idle()`, `nohz_balance_exit_idle()`, `_nohz_idle_balance()`, `nohz_idle_balance()`, `nohz_run_idle_balance()`, and `nohz_newidle_balance()` coordinate idle-load balancing and blocked-load decay for tickless idle CPUs.
- `sched_balance_newidle()` is invoked as a CPU is about to go idle. It unlocks the rq, updates blocked averages, walks domains with `CPU_NEWLY_IDLE`, tracks balancing cost, and may return success, failure, or a signal to restart class picking.
- `sched_balance_softirq()` and `sched_balance_trigger()` wire periodic/NOHZ balancing to `SCHED_SOFTIRQ`.
- `rq_online_fair()` and `rq_offline_fair()` update fair scheduler sysctls/runtime state and repair throttled/offline cgroup state around CPU hotplug.
- Under `CONFIG_SCHED_CORE`, `task_tick_core()`, `se_fi_update()`, `task_vruntime_update()`, `cfs_prio_less()`, and `task_is_throttled_fair()` integrate CFS with core scheduling, forced idle, cookie-compatible priority comparisons, and throttled hierarchy checks.
- `task_tick_fair()`, `task_fork_fair()`, `prio_changed_fair()`, `switching_from_fair()`, `switched_from_fair()`, `switched_to_fair()`, `set_next_task_fair()`, and `get_rr_interval_fair()` are scheduler-class callbacks for fair tasks.
- Fair group scheduling APIs `alloc_fair_sched_group()`, `free_fair_sched_group()`, `online_fair_sched_group()`, `unregister_fair_sched_group()`, `init_tg_cfs_entry()`, `sched_group_set_shares()`, and `sched_group_set_idle()` allocate per-CPU group CFS runqueues/entities and update group weights/idle state.
- `DEFINE_SCHED_CLASS(fair)` registers the fair scheduling class methods used by the scheduler core.
- `print_cfs_stats()` and `show_numa_stats()` expose CFS and NUMA placement state for scheduler diagnostics.
- `init_sched_fair_class()` allocates per-CPU balance/select masks, initializes CFS bandwidth callback state, opens the scheduler balance softirq, and initializes NOHZ global timing/mask state.

## Control Flow

Periodic balancing starts with `sched_balance_trigger()`, usually from the scheduler tick. If the runqueue has a real sched domain and the CPU is active, it raises `SCHED_SOFTIRQ` when `rq->next_balance` is due and may also call `nohz_balancer_kick()` so a busy CPU can request idle-load balancing by an idle housekeeping CPU.

`sched_balance_softirq()` first services pending NOHZ work with `nohz_idle_balance()`. If the current idle CPU was kicked to balance for other tickless CPUs, `_nohz_idle_balance()` updates blocked averages and optionally calls `sched_balance_domains()` for each idle runqueue. Otherwise, the normal path updates the local CPU's blocked averages and walks domains through `sched_balance_domains()`.

`sched_balance_domains()` walks the CPU's sched-domain hierarchy under RCU. For each domain it decays measured new-idle balance cost, checks whether the domain interval has elapsed, and invokes `sched_balance_rq()` when due. It updates `sd->last_balance`, recalculates the next balance deadline, and stores the earliest deadline in `rq->next_balance`.

`sched_balance_rq()` performs a single domain balancing transaction. It initializes `lb_env`, intersects the domain span with `cpu_active_mask`, elects whether this CPU should balance via `should_we_balance()`, optionally acquires the global `sched_balance_running` serialization for `SD_SERIALIZE`, and calls `sched_balance_find_src_group()` to decide if a source group should be pulled from. If a group is found, `sched_balance_find_src_rq()` picks the source runqueue and the code attempts to detach tasks from it.

Task detachment is source-rq locked. `detach_tasks()` walks the source `cfs_tasks` list from the tail, gates candidates through `can_migrate_task()`, subtracts their hierarchical load or estimated util or task count from `env->imbalance`, deactivates accepted tasks, and links them onto `env->tasks`. It periodically breaks out with `LBF_NEED_BREAK` to limit long rq lock hold times, and newly-idle balancing on preemptible kernels stops after one detached task to reduce latency. After the source rq is unlocked, `attach_tasks()` locks the destination rq and enqueues all detached tasks.

Pinned-affinity handling is integrated into the same loop. If a task cannot run on the current destination CPU but can run on another CPU in the destination group, `can_migrate_task()` records `LBF_DST_PINNED` and `new_dst_cpu`; `sched_balance_rq()` can then retarget the same source rq to that alternate destination. If every considered task is pinned, the code removes that source CPU from the candidate mask, may retry another source, and leaves parent-domain imbalance state set so a wider domain can try.

If normal detachment fails, `sched_balance_rq()` increments failure accounting and may queue active balancing. `need_active_balance()` returns true for asymmetric packing, repeated task-count imbalance, a single runnable task on a reduced-capacity source CPU, or a misfit task. When eligible, the source rq's `active_balance` flag and `push_cpu` are set and `stop_one_cpu_nowait()` schedules `active_load_balance_cpu_stop()` on the source CPU. The stopper revalidates CPU activity, locates a spanning domain, detaches one task with `LBF_ACTIVE_LB`, clears the active-balance flag, and attaches the task to the target rq.

The busiest-group decision is multi-stage. `update_sd_lb_stats()` calls `update_sg_lb_stats()` for every sched group, including the local group. Group stats include CFS load/util/runnable signals, total runnable tasks, idle CPUs, capacity, overutilization, NUMA counters, misfit load, asymmetric-packing opportunity, and SMT contention. `group_classify()` assigns a `group_type`; `update_sd_pick_busiest()` compares candidate groups according to type-specific rules. `sched_balance_find_src_group()` then applies higher-level policy: EAS performance domains can suppress load balance while not overutilized, misfit/asym/affinity-imbalanced groups force balance, overloaded groups compare average load against the domain average and imbalance percentage, and non-overloaded groups require idle local capacity and meaningful idle-CPU differences.

Newly-idle balancing runs when `schedule()` is about to switch to idle. `sched_balance_newidle()` sets `idle_stamp`, avoids work if wakeups are pending or the CPU is inactive, unpins and unlocks the rq, updates blocked averages, then walks domains with `CPU_NEWLY_IDLE`. It uses `sd->max_newidle_lb_cost`, `rq->avg_idle`, and optional `NI_RANDOM` throttling to avoid spending more time balancing than the CPU is likely to remain idle. It reacquires the rq lock, converts races with enqueued CFS work into apparent success, and asks higher scheduler classes to restart if needed.

NOHZ idle balance tracks CPUs whose ticks are stopped. `nohz_balance_enter_idle()` marks the rq as tick-stopped, adds the CPU to `nohz.idle_cpus_mask`, updates shared LLC busy counts, and sets global blocked-load/next-update flags with memory barriers so the idle-balance owner observes either the CPU mask or the pending flags. `nohz_balancer_kick()` decides whether a busy CPU should request blocked-load updates or full load balance based on pending blocked load, local runnable count, reduced capacity, asymmetric packing, misfit tasks, and LLC busy count. `_nohz_idle_balance()` then iterates idle CPUs, updates their blocked averages, optionally balances domains, records the next deadline, and restores `nohz.has_blocked_load` if any idle rq still has decaying load.

The class callback path at the end connects this balancing machinery to scheduler events. `task_tick_fair()` ticks each entity in a task's group hierarchy, runs NUMA balancing when enabled, updates misfit/overutilization state, and invokes core-scheduling tick logic. `set_next_task_fair()` installs the next entity through every ancestor CFS runqueue, accounts CFS bandwidth runtime, starts high-resolution tick enforcement when needed, updates misfit state, and updates tick-stopping decisions.

## State and Persistence Behavior

Balancing state in `struct lb_env`, `struct sg_lb_stats`, and `struct sd_lb_stats` is transient per balance pass. Detached tasks are temporarily removed from the source rq and linked on `env->tasks` until `attach_tasks()` or `attach_one_task()` places them on the destination rq.

Persistent scheduler-domain state is updated by balancing outcomes. `sd->balance_interval` backs off after pinned or balanced failures and resets to `sd->min_interval` after imbalance. `sd->nr_balance_failed` accumulates repeated periodic failures, enabling hotter or more aggressive migrations, but newly-idle and misfit balances avoid polluting this counter. `sd->last_balance`, `sd->max_newidle_lb_cost`, `sd->last_decay_max_lb_cost`, `sd->newidle_*` counters, `sgc->capacity`, `sgc->min_capacity`, `sgc->max_capacity`, and parent `sgc->imbalance` persist across passes.

Runqueue state persists across ticks and hotplug. This chunk reads and updates `rq->cpu_capacity`, `rq->has_blocked_load`, `rq->last_blocked_load_update_tick`, `rq->next_balance`, `rq->idle_stamp`, `rq->max_idle_balance_cost`, `rq->nohz_tick_stopped`, `rq->active_balance`, `rq->push_cpu`, `rq->cfs_tasks`, `rq->cfs.h_nr_runnable`, and class-specific load/utilization averages. `rq->active_balance_work` persists as CPU-stopper work storage.

Root-domain state is shared across balancing CPUs. `set_rd_overloaded()` and `set_rd_overutilized()` persist root-domain overload/overutilization signals used by new-idle and EAS decisions. Overutilization can be set by child domains and cleared only from root-domain balance.

NOHZ state persists globally in `nohz.idle_cpus_mask`, per-CPU `nohz_flags`, `nohz.next_balance`, `nohz.next_blocked`, `nohz.has_blocked_load`, and `nohz.needs_update`. The code uses atomic bit operations and barriers to coordinate idle CPUs entering/leaving the mask with asynchronous kicks and blocked-load updates.

CFS group scheduling state persists in `task_group` arrays of per-CPU `cfs_rq` and `sched_entity` objects. Group shares and idle state are protected by `shares_mutex`, while per-rq mutations use rq locks. Group allocation initializes per-CPU CFS runqueues, entity hierarchy links, bandwidth state, runnable averages, and default weights; unregister removes delayed entities, load averages, bandwidth state, and leaf-list membership.

Core-scheduling forced-idle state persists in CFS runqueues through `zero_vruntime_fi` and `forceidle_seq`. `se_fi_update()` lazily refreshes these values through the entity hierarchy so `cfs_prio_less()` can compare tasks from sibling runqueues under forced idle without globally synchronizing every CFS runqueue.

## Dependencies and Integration Points

- Scheduler topology: `struct sched_domain`, `struct sched_group`, `struct sched_group_capacity`, group masks, domain flags such as `SD_NUMA`, `SD_ASYM_CPUCAPACITY`, `SD_ASYM_PACKING`, `SD_SHARE_CPUCAPACITY`, `SD_SHARE_LLC`, `SD_PREFER_SIBLING`, `SD_SERIALIZE`, and `SD_BALANCE_NEWIDLE`.
- Runqueue locking and task migration: `rq_lock*()`, `raw_spin_rq_lock*()`, `rq_unpin_lock()`, `rq_repin_lock()`, `deactivate_task()`, `attach_task()`, `attach_one_task()`, `set_task_cpu()`, `task_on_cpu()`, and `task_current_donor()`.
- PELT/load tracking: `update_cfs_rq_load_avg()`, `update_load_avg()`, `update_tg_load_avg()`, `attach_entity_load_avg()`, `detach_entity_load_avg()`, `cfs_rq_load_avg()`, `cpu_load()`, `cpu_util_cfs()`, `cpu_util_cfs_boost()`, `cpu_runnable()`, `task_util_est()`, `cpu_util_rt()`, `cpu_util_dl()`, `cpu_util_irq()`, `hw_load_avg()`, and `cpufreq_update_util()`.
- Cgroup and bandwidth scheduling: `CONFIG_FAIR_GROUP_SCHED`, `task_group`, `cfs_rq`, `sched_entity`, `init_cfs_bandwidth()`, `destroy_cfs_bandwidth()`, `init_cfs_rq_runtime()`, `account_cfs_rq_runtime()`, `lb_throttled_hierarchy()`, `throttled_hierarchy()`, `unthrottle_offline_cfs_rqs()`, and `clear_tg_offline_cfs_rqs()`.
- NUMA balancing: `CONFIG_NUMA_BALANCING`, `sched_numa_balancing`, `task_numa_fault` data, `numa_group`, `numa_preferred_nid`, `node_distance()`, `task_weight()`, `group_weight()`, `adjust_numa_imbalance()`, `task_tick_numa()`, and NUMA debug output.
- CPU capacity/asymmetry and EAS: `capacity_of()`, `get_actual_cpu_capacity()`, `arch_scale_cpu_capacity()`, `capacity_greater()`, `task_fits_cpu()`, `sched_energy_enabled()`, performance domains in `rq->rd->pd`, `set_task_max_allowed_capacity()`, overutilization state, and misfit task tracking.
- SMT and core scheduling: `sched_smt_active()`, `is_core_idle()`, `cpu_smt_mask()`, `sched_core_cookie_match()`, `sched_group_cookie_match()`, `sched_core_enabled()`, core force-idle counters/sequences, and `cfs_prio_less()`.
- Tick and softirq infrastructure: `open_softirq(SCHED_SOFTIRQ, sched_balance_softirq)`, `raise_softirq()`, scheduler tick callbacks, high-resolution fair tick support, full dynticks tick offload, `smp_call_function_single_async()`, and CPU stopper work.
- CPU hotplug and housekeeping: `cpu_active_mask`, `cpu_active()`, `num_online_cpus()`, housekeeping masks for `HK_TYPE_KERNEL_NOISE`, rq online/offline callbacks, and null-domain handling.
- Diagnostics and accounting: `schedstat_*`, tracepoint `trace_sched_cpu_capacity_tp()`, `print_cfs_rq()`, `print_numa_stats()`, `seq_file`, and scheduler feature/static-branch controls.

## Risks and Edge Cases

- Migration eligibility is intentionally conservative. Relaxing checks around `sched_delayed`, throttled hierarchies, `PLACE_LAG`, per-CPU kthreads, proxy-exec blocking, current tasks, core cookies, or cache-hot tasks can cause unfair placement, bandwidth violations, lock-order surprises, or security/isolation issues under core scheduling.
- Source and destination rq locking is split by design. Detached tasks are marked migrating between unlock and attach; changing that ordering can race task lookup, wakeups, or CPU affinity updates.
- `detach_tasks()` must make progress on `env->imbalance`. Hierarchical cgroup load can be zero, so the code clamps task load to at least one. Removing that guard can make the loop rely only on `loop_max` and scan excessive tasks.
- `LBF_NEED_BREAK` limits long source-rq lock holds. Ignoring it can create latency spikes on large runqueues, especially for newly-idle balancing.
- Pinned-task and alternate-destination handling is subtle. `LBF_DST_PINNED`, `LBF_ALL_PINNED`, `LBF_SOME_PINNED`, and parent `sgc->imbalance` must remain consistent or balancing can oscillate, miss affinity-constrained overload, or repeatedly target CPUs that cannot run the tasks.
- `sd->nr_balance_failed` intentionally excludes newly-idle and misfit failures. Counting those paths would make ordinary idle probes and capacity fixes trigger cache-hot override or active balance too aggressively.
- Group classification depends on capacity, utilization, runnable time, idle CPU counts, and EAS overutilization state. Small formula changes can alter whether the code chooses `migrate_load`, `migrate_util`, or `migrate_task`, with visible performance and energy effects.
- Asymmetric CPU capacity and asymmetric packing often bypass normal average-load fairness. Bugs here can push work from high-capacity CPUs to low-capacity CPUs or fail to pack tasks onto preferred CPUs.
- SMT handling deliberately prefers idle cores over idle SMT siblings in some domains. Reordering `should_we_balance()` or SMT group comparisons can reduce throughput by creating avoidable shared-core contention.
- NUMA classification (`regular`, `remote`, `all`) can skip an otherwise busiest rq to preserve locality. Incorrect classification can either harm locality or prevent convergence when enough load cannot be moved.
- NOHZ state uses atomics, barriers, and unlocked updates to avoid high-frequency idle entry/exit bottlenecks. Weakening the barriers around `idle_cpus_mask`, `has_blocked_load`, and `needs_update` can lose blocked-load updates or idle-balance kicks.
- `_nohz_idle_balance()` aborts if the balancing CPU stops being idle and needs rescheduling. Continuing to scan all idle CPUs in that case can add wakeup latency on the CPU that must run work.
- Newly-idle balance runs with the local rq temporarily unlocked while the current task is still on CPU. The code depends on preemption/IRQ state and restart checks; changes here can race higher-priority class enqueue or schedule-class picking.
- Active balance runs in CPU stopper context after a delay. It must revalidate CPU activity, source CPU identity, `active_balance`, and source rq runnable count before detaching. Missing revalidation can migrate from offline or stale CPUs.
- Fair group unregister handles delayed group entities and leaf CFS rq lists. Failure to dequeue delayed entities or remove decayed cfs_rqs can leave stale load and break group destruction assumptions.
- `sched_group_set_idle()` adjusts hierarchical idle counts only while queued entities remain on rq and stops once an idle parent already accounts for the delta. Misaccounting here affects idle group weights and runnable idle-task counts across the hierarchy.
- Core forced-idle vruntime comparison assumes lazy propagation of `zero_vruntime_fi` through the relevant entity hierarchy. Comparing tasks without refreshing sibling CFS runqueues can choose the wrong cookie-compatible task.

## Test Signals

- Periodic balance tests should cover domain interval expiry, `rq->next_balance` updates, `SD_SERIALIZE` skip behavior, group-balance CPU election, idle-core preference over idle SMT siblings, balance interval backoff, and reset after successful moves.
- Migration eligibility tests should cover CPU affinity misses, alternate destination selection, all-pinned source queues, delayed-dequeued entities, throttled cgroup hierarchies, per-CPU kthreads, blocked proxy-exec tasks, current/donor tasks, cache-hot candidates, core-cookie mismatch, and forced active-balance migration.
- Detach/attach tests should verify load/util/task/misfit imbalance accounting, minimum load progress for cgroup hierarchies, `LB_MIN`, `shr_bound()` relaxation after failures, `LBF_NEED_BREAK`, preemptible newly-idle one-task detachment, and list integrity of `rq->cfs_tasks` plus `env->tasks`.
- Group classification tests should exercise spare, fully busy, overloaded, misfit, SMT balance, asym packing, and group-imbalanced states under varying capacities, runnable counts, EAS overutilization, IRQ/RT/DL pressure, and affinity constraints.
- Source selection tests should validate NUMA `fbq_type` filtering, asymmetric-capacity single-task rejection, asymmetric-priority source rejection, and the different busiest-rq metrics for `migrate_load`, `migrate_util`, `migrate_task`, and `migrate_misfit`.
- NUMA tests should cover preferred-node retention, preferred-node migration, idle CPU locality override, group versus task fault weights, `adjust_numa_imbalance()`, wakeup idlest-group preferred-node selection, and `show_numa_stats()` output.
- NOHZ tests should cover idle enter/exit mask updates, blocked-load updates while tick-stopped, busy CPU kicks for overloaded/reduced-capacity/asym/misfit/LLC states, duplicate kick suppression with `NOHZ_KICK_MASK`, abort when the ILB CPU needs rescheduling, and direct `nohz_run_idle_balance()` before idle.
- Newly-idle tests should cover `ttwu_pending` early return, inactive CPU rejection, average-idle cost gating, `NI_RANDOM` throttling, update of `sd->max_newidle_lb_cost`, racing CFS enqueue while rq is unlocked, higher-class modification restart, and `nohz_newidle_balance()` kick setup on failure.
- Active-balance tests should cover asym-packing force migration, reduced-capacity single task, repeated task imbalance, misfit migration, active_balance flag serialization, stale CPU/offline revalidation, and successful `attach_one_task()` after stopper detachment.
- Fair group tests should cover task-group allocation failure cleanup, per-CPU entity/rq initialization, online attach with throttle sync, unregister of delayed group entities, leaf-list removal, share clamping and root rejection, idle group rejection for shares, idle toggle hierarchy count propagation, and idle-group weight changes.
- Class callback tests should cover remote `task_tick_fair()`, queued tick behavior, NUMA tick invocation, misfit and overutilized updates, core forced-idle reschedule, priority-change preemption, switching from delayed fair entities, switching to fair from RT, `set_next_task_fair()` group hierarchy setup, and RR interval calculation.
- Initialization tests should cover successful allocation of per-CPU `load_balance_mask`, `select_rq_mask`, and `should_we_balance_tmpmask`; CFS bandwidth callback setup; `SCHED_SOFTIRQ` registration; and NOHZ initial `next_balance`, `next_blocked`, and idle mask allocation.

## Chunk Boundary Notes

This chunk is the tail control-plane section of `fair.c`. Earlier chunks define the core CFS entity placement, enqueue/dequeue, wakeup preemption, PELT helpers, bandwidth throttling internals, NUMA fault handling, misfit tracking, CPU selection fast paths, and many helpers referenced here. The final per-file research should merge this chunk with those earlier sections so the full fair-scheduler lifecycle reads from entity accounting and wakeup CPU selection through load balancing, tick handling, cgroup management, and scheduler-class registration.
