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
