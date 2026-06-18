# Research: sources/distributed-fs/ceph-client/kernel/sched/core.c

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-006049`: lines 1-9875, `Docs/researches/chunks/subset-b-006049_research.md`
- `subset-b-006050`: lines 9876-11236, `Docs/researches/chunks/subset-b-006050_research.md`

## Chunk Research

### subset-b-006049: lines 1-9875

# sources/distributed-fs/ceph-client/kernel/sched/core.c lines 1-9875

## Scope and Purpose

This chunk covers the first 9,875 lines of `kernel/sched/core.c`, the central Linux scheduler implementation in this Ceph client kernel source tree. It defines the scheduler's global/per-CPU state, runqueue locking rules, wakeup and migration paths, task fork and initial wakeup handling, the main `__schedule()` context-switch path, preemption entry points, CPU hotplug scheduler hooks, scheduler initialization, and the beginning of cgroup scheduler control handling.

The file is the integration point for scheduler classes (`stop`, `deadline`, `rt`, `fair`, optional `ext`, and `idle`) rather than a complete policy implementation by itself. It coordinates class callbacks, task/runqueue state transitions, time accounting, PSI and schedstat updates, CPU affinity, cgroups, utilization clamping, core scheduling, proxy execution, and CPU hotplug. The line-range ends inside the CFS bandwidth section after `tg_get_cfs_burst()` begins; later lines continue quota/burst validation and cgroup file registration.

## Important State, Types, and Global Controls

- `DEFINE_PER_CPU_SHARED_ALIGNED(struct rq, runqueues)` is the authoritative per-CPU scheduler state. Helpers use `cpu_rq(cpu)`, `this_rq()`, `rq->curr`, `rq->donor`, `rq->idle`, `rq->nr_running`, class-specific sub-runqueues, and optional core-scheduling fields.
- `scheduler_running`, `sysctl_sched_features`, `sysctl_sched_nr_migrate`, `sysctl_resched_latency_warn_ms`, and `sysctl_resched_latency_warn_once` expose global scheduler behavior and diagnostics.
- Optional static keys gate major fast-path features: `__sched_core_enabled`, `__sched_proxy_exec`, `sched_uclamp_used`, `sched_schedstats`, `sched_numa_balancing`, and dynamic preemption keys/static calls.
- Task state serialization revolves around `p->pi_lock`, `rq->__lock`/`rq->lock`, `p->__state`, `p->saved_state`, `p->on_rq`, `p->on_cpu`, `p->cpus_ptr`, `p->cpus_mask`, `p->migration_pending`, `p->wake_cpu`, `p->sched_class`, and class-specific embedded entities.
- `struct affinity_context`, `struct migration_arg`, and `struct set_affinity_pending` are the core local data structures for CPU affinity and migrate-disable interactions.
- `struct task_group`, `root_task_group`, `task_groups`, `task_group_cache`, and `task_group_lock` begin the cgroup scheduler integration. The chunk includes task group allocation, online/offline/release/free, task movement, uclamp group propagation, weight controls, and the start of CFS bandwidth controls.

## Scheduler Core and Runqueue Locking

The opening comments establish lock ordering and state ownership. Normal scheduling state is serialized by `rq->lock`; external task changes generally use `task_rq_lock()` to take both `p->pi_lock` and the task's rq lock. `p->on_rq` distinguishes not queued, queued, and migrating states, while `p->on_cpu` is used to order wakeups against the previous CPU's context-switch tail.

`raw_spin_rq_lock_nested()`, `raw_spin_rq_trylock()`, and `double_rq_lock()` abstract runqueue locking. With core scheduling enabled, multiple SMT siblings may share a lock pointer through `rq->core`, so these helpers retry if the effective lock changes during acquisition. This is paired with `__sched_core_enable()` using `synchronize_rcu()` before flipping online runqueues.

`___task_rq_lock()` and `_task_rq_lock()` repeatedly sample `task_rq(p)` and wait out `TASK_ON_RQ_MIGRATING` so callers see a stable task/runqueue association. Their memory-ordering comments are part of the scheduler's correctness contract: migrations store `p->on_rq = MIGRATING`, issue a write barrier via `__set_task_cpu()`, then update CPU assignment before releasing the rq lock.

## Clock, Tick, and Reschedule Signals

`update_rq_clock()` reads `sched_clock_cpu()`, updates `rq->clock`, and delegates task-clock accounting to `update_rq_clock_task()`. That helper subtracts IRQ time and paravirtual steal time from task execution time, updates delay accounting, PELT clocks, and optional IRQ/load average data.

High-resolution scheduler tick support is implemented behind `CONFIG_SCHED_HRTICK`. `hrtick_start()` bounds tiny delays to at least 10us, defers timer operations when inside schedule, and uses a CSD/IPI for remote rq timers. `hrtick_schedule_enter()` and `hrtick_schedule_exit()` synchronize hrtimer rearming and cancellation around the main scheduler lock handoff.

`__resched_curr()`, `resched_curr()`, `resched_curr_lazy()`, and `resched_cpu()` set `TIF_NEED_RESCHED` or `TIF_NEED_RESCHED_LAZY` on the current task of a target rq. For remote CPUs the code avoids unnecessary IPIs when idle polling state promises progress, and it traces `sched_set_need_resched_tp`.

NOHZ integration includes `get_nohz_timer_target()`, `wake_up_idle_cpu()`, `wake_up_full_nohz_cpu()`, `wake_up_nohz_cpu()`, `nohz_csd_func()`, and `sched_can_stop_tick()`. These functions choose housekeeping CPUs, kick idle/full-dynticks CPUs, queue scheduler softirqs for nohz idle balance, and decide whether the periodic tick can stop based on DL/RT/CFS/SCX runnable state and bandwidth constraints.

## Wake Queues and Wakeup Control Flow

Wake queues use `__wake_q_add()`, `wake_q_add()`, `wake_q_add_safe()`, and `wake_up_q()` to batch wakeups while preserving task references. The `wake_q_node` insertion uses `cmpxchg_relaxed()` plus explicit barriers to ensure a pending wakeup cannot miss the queued state.

The primary wakeup path is `try_to_wake_up()`. Its control flow is:

1. Disable preemption and add `WF_TTWU`.
2. Special-case `p == current` without taking locks, relying on program order and current's local state.
3. For other tasks, take `p->pi_lock`, issue `smp_mb__after_spinlock()`, and match `p->__state` or `p->saved_state` via `ttwu_state_match()`.
4. If already queued, use `ttwu_runnable()` to mark the state running and possibly preempt current.
5. Otherwise set `TASK_WAKING`, wait for `p->on_cpu` to clear or queue a remote wake list, select an allowed CPU, update PSI/I/O wait state if migrated, call `set_task_cpu()`, and enqueue through `ttwu_queue()`.

Remote wakeups may be delegated through `ttwu_queue_wakelist()` and `sched_ttwu_pending()` to avoid remote runqueue bouncing. `ttwu_queue_cond()` only uses this path when SCX permits queued wakeup, the target CPU is active, the task remains allowed there, and cache/topology/idleness heuristics justify it.

`ttwu_do_activate()` handles enqueue flags, `rq->nr_uninterruptible`, I/O wait accounting, `activate_task()`, `wakeup_preempt()`, state transition to `TASK_RUNNING`, and optional class `task_woken()` callbacks. Wakeup statistics are collected by `ttwu_stat()` when schedstats are enabled.

## Enqueue, Dequeue, and Utilization Clamp

`enqueue_task()` and `dequeue_task()` are the generic class dispatch wrappers. They update rq clocks unless told not to, maintain uclamp rq buckets, invoke class `enqueue_task`/`dequeue_task`, update PSI and sched_info, and update core-scheduling rb-trees when enabled.

`activate_task()` and `deactivate_task()` set `p->on_rq` around enqueue/dequeue. Deactivation marks `TASK_ON_RQ_MIGRATING` first because other paths rely on this temporary state before task CPU changes.

Utilization clamp support tracks effective `UCLAMP_MIN`/`UCLAMP_MAX` at task and rq levels. Key helpers include `uclamp_eff_get()`, `uclamp_eff_value()`, `uclamp_rq_inc_id()`, `uclamp_rq_dec_id()`, `uclamp_rq_inc()`, `uclamp_rq_dec()`, `uclamp_update_active()`, and `init_uclamp()`. The fast path is disabled until userspace or cgroups enable `sched_uclamp_used`. Slow-path sysctl updates are serialized by `uclamp_mutex`; group-aware updates propagate through cgroup descendants and refresh runnable tasks.

## CPU Affinity and Migration

CPU affinity is managed by `set_cpus_allowed_common()`, `do_set_cpus_allowed()`, `__set_cpus_allowed_ptr()`, `__set_cpus_allowed_ptr_locked()`, `set_cpus_allowed_ptr()`, `set_cpus_allowed_force()`, `restrict_cpus_allowed_ptr()`, `force_compatible_cpus_allowed_ptr()`, and `relax_compatible_cpus_allowed_ptr()`.

Migration control is careful because runnable migration, waking migration, migrate-disable regions, CPU hotplug, and concurrent affinity changes overlap. `move_queued_task()` removes a queued task from one rq, changes CPU, releases the old rq lock, locks the destination rq, activates the task, and checks preemption. `migration_cpu_stop()` runs in a CPU stopper thread to force a task off a CPU or update `wake_cpu`; it completes a `set_affinity_pending` when a blocked migrate-disable request can finally be resolved. `affine_move_task()` coordinates pending completions, stopper work, current-task migrate-enable, and waiters.

`is_cpu_allowed()` distinguishes userspace tasks, regular kernel threads, per-CPU kthreads, migrate-disabled tasks, online CPUs, active CPUs, and dying CPUs. `select_fallback_rq()` recovers from invalid affinity by preferring same-node allowed CPUs, cpuset fallbacks, then a forced possible CPU mask. `select_task_rq()` delegates placement to the current scheduling class when migration is possible, then validates against hotplug/affinity.

NUMA-related migration appears in `migrate_swap()`, `migrate_swap_stop()`, `migrate_task_to()`, and `sched_setnuma()`. These paths use CPU stopper operations and double rq locking to safely exchange or move tasks.

## Fork, Initial Wakeup, and Task Lifetime

`__sched_fork()` clears scheduler state for a new task: `on_rq`, CFS entity runtime/vruntime fields, DL/RT/SCX state, schedstats, preempt notifiers, NUMA data, wake entry type, and migration pending state. `sched_fork()` marks the task `TASK_NEW`, resets inherited PI boosting, handles `sched_reset_on_fork`, selects the initial scheduling class, initializes runnable average, preempt count, and pushable structures.

`sched_cgroup_fork()` assigns the task group under `p->pi_lock`, sets the initial CPU without migration callbacks, invokes class `task_fork()`, and hands off to SCX fork handling. `sched_post_fork()` performs mm concurrency-ID, uclamp, and SCX post-fork hooks. `wake_up_new_task()` moves the new task to `TASK_RUNNING`, selects its fork CPU after cpuset/hotplug constraints are stable, initializes utilization average, enqueues it with `ENQUEUE_INITIAL`, traces `sched_wakeup_new`, and may preempt the current task.

Task exit cleanup is coupled to the final schedule. `do_task_dead()` sets `TASK_DEAD` and never returns; `finish_task_switch()` observes `TASK_DEAD`, calls class `task_dead`, SCX and cgroup death hooks, releases the stack, and drops the final task reference.

## Main Scheduling and Context Switch Path

`__schedule()` is the central scheduler entry. It is called with preemption disabled and is driven by explicit blocking, `TIF_NEED_RESCHED`, or preemption return paths. Its main sequence is:

1. Trace scheduler entry and run `schedule_debug()`.
2. Disable IRQs, note RCU context switch, and apply `migrate_disable_switch()`.
3. Lock the local rq, issue a post-spinlock full barrier, enter hrtick schedule mode, and update rq clock.
4. For non-preemptive sleeps, call `try_to_block_task()` unless proxy execution needs the blocked task to remain queued.
5. Pick the next donor/task with `pick_next_task()`, using class-specific callbacks, core-scheduling selection, and optional proxy-execution owner following.
6. Clear resched flags, reset latency tracking, and either switch or simply unlock if `prev == next`.
7. On a switch, update `rq->curr`, switch counters, PSI, tracepoints, and call `context_switch()`.

`context_switch()` calls `prepare_task_switch()`, handles lazy TLB and `switch_mm_irqs_off()`, updates membarrier and rseq/mm-cid state, performs the scheduler lock handoff with `prepare_lock_switch()`, calls `switch_to()`, then returns through `finish_task_switch()`. The lock handoff is intentionally unusual: the previous task enters `switch_to()` with the rq lock held, and the next task releases it in `finish_lock_switch()`.

`__pick_next_task()` optimizes the all-fair-class case, otherwise balances from the previous class down and iterates active scheduling classes. Under `CONFIG_SCHED_CORE`, `pick_next_task()` performs SMT-wide cookie matching, forced-idle accounting, sibling rescheduling, and optional cookie stealing via `sched_core_balance()`.

## Core Scheduling and Proxy Execution

Core scheduling maintains per-core rb-trees of cookied tasks with `sched_core_enqueue()`, `sched_core_dequeue()`, `sched_core_find()`, and `sched_core_next()`. It toggles online/offline CPUs with `__sched_core_flip()`, refcounts activation through `sched_core_get()`/`sched_core_put()`, and handles core leader changes during CPU hotplug. Its main risk area is ensuring sibling picks are cookie-compatible while maintaining forced-idle accounting and not leaving stale `core_pick` pointers across hotplug.

Proxy execution is enabled by `CONFIG_SCHED_PROXY_EXEC` and the `sched_proxy_exec` boot arg. It lets the scheduler run a lock owner as execution context while a blocked donor contributes scheduling priority. `find_proxy_task()` follows `task->blocked_on -> mutex owner` chains under mutex wait locks and blocked locks. It can deactivate donors, migrate blocked donors to owner CPUs, force-return tasks to their normal CPU selection, or schedule idle when migration/wakeup races need to resolve. This area has complex lifetime constraints: the code repeatedly clears rq references before dropping locks so another CPU cannot use a donor after it was migrated or dequeued.

## Preemption, Cond Resched, and RT Mutex Priority Inheritance

Public scheduling entry points include `schedule()`, `schedule_idle()`, `schedule_user()`, `schedule_preempt_disabled()`, `preempt_schedule()`, `preempt_schedule_notrace()`, `preempt_schedule_irq()`, and `default_wake_function()`. `__schedule_loop()` repeats while `need_resched()` remains set.

Dynamic preemption supports `none`, `voluntary`, `full`, and optional `lazy`. `sched_dynamic_mode()`, `sched_dynamic_update()`, `setup_preempt_mode()`, `preempt_dynamic_init()`, and `preempt_model_str()` update static calls or static keys for `cond_resched`, `might_resched`, preempt schedule trampolines, IRQ-exit reschedule, and lazy preemption.

`__cond_resched()`, `dynamic_cond_resched()`, `dynamic_might_resched()`, `__cond_resched_lock()`, `__cond_resched_rwlock_read()`, and `__cond_resched_rwlock_write()` provide voluntary scheduling points and lock break paths.

`rt_mutex_pre_schedule()`, `rt_mutex_schedule()`, `rt_mutex_post_schedule()`, and `rt_mutex_setprio()` integrate priority inheritance. `rt_mutex_setprio()` updates effective priority/class under task and rq locks, handles DL/RT/Fair class transitions, updates DL PI entities, and uses `sched_change` guards to dequeue/requeue when necessary.

## CPU Hotplug, Idle, and Initialization

`init_idle()` configures per-CPU idle tasks as running, per-CPU kernel threads, assigns CPU affinity, sets `rq->idle`, `rq->donor`, `rq->curr`, and initializes idle preempt count, tracing, vtime, and command name.

CPU hotplug hooks include `sched_cpu_activate()`, `sched_cpu_deactivate()`, `sched_cpu_starting()`, `sched_cpu_wait_empty()`, and `sched_cpu_dying()`. They update `cpu_active`, sched domains, cpusets, NUMA masks, SCX state, rq online/offline status, SMT/core-scheduling state, nohz participation, remote tick offload, CFS/DL/RT state, and hotplug push behavior.

`balance_push()` and related callbacks force non-per-CPU/non-migrate-disabled tasks off a CPU going inactive. The outgoing CPU waits in `balance_hotplug_wait()` until only the hotplug/idle condition remains and no pinned tasks are present. `sched_cpu_dying()` validates `rq->nr_running == 1`, dumps queued tasks on failure, stops DL servers, migrates load-average state, clears hrtick, and resets core-scheduling pointers.

`sched_init()` performs early scheduler setup: validates scheduler class ordering, allocates root group arrays, initializes root bandwidth and task group structures, initializes every possible rq, attaches the default root domain, initializes CFS/RT/DL runqueues, hrtick/nohz/hotplug state, fair and ext servers, core-scheduling fields, scratch cpumasks, boot idle task state, PSI, uclamp, dynamic preemption, and finally sets `scheduler_running = 1`. `sched_init_smp()` later initializes NUMA/domain state, moves init to a housekeeping CPU, initializes scheduler granularity/classes/DL servers, and marks SMP scheduler initialization complete.

## Cgroup Scheduler Integration in This Chunk

The chunk includes the `CONFIG_CGROUP_SCHED` control-plane skeleton:

- `sched_create_group()`, `sched_online_group()`, `sched_destroy_group()`, `sched_release_group()`, and free/unregister helpers allocate, expose, unlink, and RCU-free task groups.
- `sched_move_task()` changes a task's `sched_task_group` and class-specific group entity under `task_rq_lock()`, then reschedules or wakeup-preempts if the move affected a running/queued task.
- cgroup CSS callbacks allocate root or child task groups, online/offline SCX state, release/free scheduler groups, validate RT attach constraints, attach tasks, and cancel SCX attach.
- `cpu_util_update_eff()` propagates effective uclamp caps through cgroup descendants while holding `uclamp_mutex` and RCU read lock, and updates runnable tasks when effective clamps change.
- `cpu_uclamp_{min,max}_{read,write}` parse and print cgroup uclamp percentages or `max`.
- group weight controls map cgroup weights to fair shares and SCX weights.
- The CFS bandwidth section begins with `tg_set_cfs_bandwidth()`, which validates schedulability, toggles global CFS bandwidth usage, updates period/quota/burst under the bandwidth lock, restarts bandwidth timers, updates every online `cfs_rq`, and unthrottles throttled runqueues if needed. The chunk ends before the rest of CFS bandwidth read/write and cftype registration.

## Dependencies and Integration Points

This code depends on architecture context-switch/MM hooks (`switch_to`, `switch_mm_irqs_off`, `arch_start_context_switch`, `finish_arch_post_lock_switch`), scheduler class implementations in sibling files, `sched.h`, `stats.h`, `pelt.h`, SMP/nohz/topology helpers, cpuset/cgroup/kernfs APIs, workqueue and io-wq worker hooks, block plug flushing, PSI, perf events, delay accounting, RCU, membarrier, rseq, lockdep, livepatch, high-resolution timers, CPU stopper APIs, static keys/static calls, and optional SCX scheduler extension hooks.

Externally visible APIs exported or broadly consumed from this chunk include `schedule`, `preempt_schedule`, `preempt_schedule_notrace`, `wake_up_process`, `default_wake_function`, `set_cpus_allowed_ptr`, `migrate_disable`, `migrate_enable`, `kick_process`, `single_task_running`, `io_schedule`, `io_schedule_timeout`, `sched_show_task`, `__might_sleep`, `__might_resched`, `__cant_sleep`, `__cant_migrate`, and scheduler tracepoint exports.

Tracepoints and diagnostics are first-class integration surfaces: `trace_sched_switch`, `trace_sched_wakeup`, `trace_sched_waking`, `trace_sched_migrate_task`, `trace_sched_set_need_resched_tp`, schedstats, PSI, sysrq state dumps, lockdep checks, WARN/BUG assertions, and boot/sysctl knobs are heavily used to expose or guard scheduler behavior.

## State and Persistence Behavior

Most state is in-memory kernel state with no filesystem persistence. Persistent-from-boot controls include boot arguments such as `sched_proxy_exec`, `schedstats=`, `resched_latency_warn_ms=`, and `preempt=`, plus sysctl/cgroup writes that mutate live scheduler state. Per-task accounting such as `sum_exec_runtime`, `nr_migrations`, `nvcsw/nivcsw`, wakeup stats, uclamp requests, affinity masks, and task group membership persists for the lifetime of a task. Per-rq clocks, runqueue counts, CFS bandwidth state, nohz flags, and core-scheduling state persist for CPU/rq lifetime and are reinitialized or migrated during CPU hotplug.

RCU is used as a deferred persistence/lifetime mechanism for task groups and task references after final switches. Several updates rely on grace periods before state can be safely reused or freed, especially scheduler core toggling, cgroup group teardown, and CPU active mask changes.

## Risks and Correctness Hotspots

- Wakeup and schedule barriers are fragile. Incorrect ordering around `p->__state`, `p->on_rq`, `p->on_cpu`, `rq->curr`, or `task_cpu(p)` can cause missed wakeups, running a task on the wrong CPU, or use-after-free after task exit.
- Migrate-disable plus affinity changes require `set_affinity_pending` completion discipline. Races between concurrent `set_cpus_allowed_ptr()`, `migrate_enable()`, CPU stopper execution, and hotplug can deadlock callers or leave tasks on disallowed CPUs if the pending state is mishandled.
- Core scheduling must keep sibling picks cookie-compatible and clear stale `core_pick`/`core_dl_server` state on hotplug or sequence changes. Forced-idle accounting is especially sensitive to reschedule edges.
- Proxy execution has high complexity around blocked-owner chains, mutex wait locks, donor/current separation, rq lock dropping, migration of blocked scheduling contexts, and PROXY_WAKING return paths.
- Cgroup task group teardown uses multiple RCU phases. Calling unregister/free too early can race with stats printing, CFS throttling/unthrottling, or class callbacks.
- Scheduler initialization and CPU hotplug have strict ordering with cpusets, sched domains, rq online flags, nohz tick offload, and class online/offline callbacks.
- Dynamic preemption updates must avoid invalid transient states in static calls/keys, hence the deliberate enable-before-switch sequence.
- The chunk contains many config-dependent paths. Behavior can differ materially under `CONFIG_PREEMPT_RT`, `CONFIG_SCHED_CORE`, `CONFIG_SCHED_PROXY_EXEC`, `CONFIG_SCHED_CLASS_EXT`, `CONFIG_UCLAMP_TASK_GROUP`, `CONFIG_NO_HZ_FULL`, and cgroup bandwidth options.

## Test and Validation Signals

Useful validation signals for this code include scheduler tracepoints (`sched_switch`, `sched_wakeup`, `sched_waking`, `sched_migrate_task`, need-resched tracehooks), lockdep, DEBUG_PREEMPT, DEBUG_ATOMIC_SLEEP, schedstats, PSI counters, sysrq task dumps, CPU hotplug stress, cpuset/cgroup migration tests, RT mutex PI tests, affinity/migrate-disable stress, nohz/full-dynticks tests, hrtick timing tests, and cgroup uclamp/CFS bandwidth write-read behavior.

Runtime warning sites provide targeted fault signals: scheduling while atomic, sleeping in invalid context, assuming atomic/non-migratable context, corrupted scheduler preempt count, dying CPU not vacated, unexpected rq/core state, unbalanced uclamp buckets, invalid CPU affinity, and scheduler class ordering assertions during boot.

For this repository's later merge lane, the main unresolved boundary is that CFS bandwidth handling continues after line 9,875. Whole-file research should merge this chunk with subsequent chunks before making final statements about all CPU cgroup files, quota/burst parsing, cgroup v2 `cpu.max`, RT group cgroup files, and later mm concurrency-ID code.

### subset-b-006050: lines 9876-11236

# sources/distributed-fs/ceph-client/kernel/sched/core.c lines 9876-11236

## Scope

This chunk covers the tail of CPU scheduler cgroup control-file wiring, exported scheduler debugging and priority-weight helpers, the main `CONFIG_SCHED_MM_CID` lifecycle implementation for restartable-sequences memory-map concurrency IDs, and the generic `sched_change_begin()`/`sched_change_end()` helper pair used to change task scheduling properties while preserving runqueue state.

The range begins immediately after `tg_get_cfs_burst()` computes burst runtime in microseconds and ends at the close of `sched_change_end()`. Earlier chunks define most task-group allocation, attach, uclamp, and CFS bandwidth mutation helpers; this chunk validates and exposes those controls through cgroup files, then transitions into lower-level scheduler state used during fork, exit, exec, affinity updates, context switch, and class/priority changes.

## Purpose

The cgroup portion turns scheduler task-group state into cgroup v1 and v2 CPU controller ABI files. It handles CFS bandwidth hierarchy validation, period/quota/burst read and write paths, legacy RT runtime control registration, CPU weight and nice conversion, idle group flags, cgroup v2 `cpu.max` parsing, and cgroup-level throttling statistics. It also keeps sched_ext (`scx`) group metadata in sync after successful bandwidth, weight, and idle updates.

The middle utility portion exposes task dump diagnostics, the canonical nice-to-weight tables used by fair scheduling, and a tracepoint wrapper for `sched_update_nr_running`.

The MM CID portion manages per-`mm_struct` concurrency identifiers for rseq. It dynamically switches each process between per-task CID ownership and per-CPU CID ownership as the number of users and allowed CPUs changes. The implementation is designed to avoid CID exhaustion and rq-lock livelock during ownership-mode changes by using an explicit transition bit, short rq-locked fixup sections, bitmap allocation, irq-work/workqueue deferral for affinity-triggered changes, and exec/fork/exit hooks.

The final `sched_change` portion provides a standardized, scoped pattern for temporarily removing a task from scheduler accounting, allowing callers to mutate scheduling properties, then restoring the task and invoking class callbacks in the correct order.

## Important APIs, Types, and Functions

- `struct cfs_schedulable_data` carries the task group whose period/quota is being tested plus the proposed `period` and `quota` values.
- `normalize_cfs_quota()` converts a group's quota/period to the normalized bandwidth ratio used for hierarchical validation, substituting proposed values for the target group and returning `RUNTIME_INF` for unlimited quotas.
- `tg_cfs_schedulable_down()` is the downward `walk_tg_tree()` callback that computes and stores `cfs_bandwidth.hierarchical_quota`. On cgroup v2 it clamps each child to the nearest finite ancestor; on cgroup v1 it rejects a finite child quota larger than a finite parent quota.
- `__cfs_schedulable()` prepares proposed CFS bandwidth values, converts finite nanosecond inputs to microseconds for ratio math, enters RCU, and walks the task-group tree with `tg_cfs_schedulable_down()`.
- `cpu_cfs_stat_show()`, `cpu_cfs_local_stat_show()`, `cpu_extra_stat_show()`, and `cpu_local_stat_show()` expose throttling, burst, and optional schedstat wait-sum counters through cgroup stat files. `throttled_time_self()` aggregates per-CPU `cfs_rq->throttled_clock_self_time` with `READ_ONCE()`.
- `tg_bandwidth()` abstracts bandwidth reads across `CONFIG_CFS_BANDWIDTH`: with CFS bandwidth it reads `task_group.cfs_bandwidth`, and without it it reads sched_ext bandwidth fields.
- `tg_set_bandwidth()` validates user-supplied period/quota/burst values, rejects root-group changes, bounds microsecond-to-nanosecond conversion, enforces a 1 ms minimum and 1 s maximum period, rejects quota/burst overflow against `MAX_BW`, calls `tg_set_cfs_bandwidth()` when present, and updates `scx_group_set_bandwidth()` after success.
- `cpu_period_read_u64()`, `cpu_quota_read_s64()`, `cpu_burst_read_u64()`, `cpu_period_write_u64()`, `cpu_quota_write_s64()`, and `cpu_burst_write_u64()` implement legacy `cpu.cfs_period_us`, `cpu.cfs_quota_us`, and `cpu.cfs_burst_us` accessors. Negative quota writes become `RUNTIME_INF`, and reading `RUNTIME_INF` as `s64` yields `-1`.
- `cpu_rt_runtime_*()` and `cpu_rt_period_*()` forward legacy RT group scheduler files to `sched_group_set_rt_runtime()`, `sched_group_rt_runtime()`, `sched_group_set_rt_period()`, and `sched_group_rt_period()`.
- `DEFINE_STATIC_KEY_* (rt_group_sched)`, `setup_rt_group_sched()`, and `cpu_rt_group_init()` implement the `rt_group_sched=` boot parameter and conditionally register legacy RT cgroup files with `cgroup_add_legacy_cftypes()`.
- `cpu_idle_read_s64()` and `cpu_idle_write_s64()` expose task-group idle scheduling state and propagate successful changes to sched_ext with `scx_group_set_idle()`.
- `cpu_weight_read_u64()`, `cpu_weight_write_u64()`, `cpu_weight_nice_read_s64()`, and `cpu_weight_nice_write_s64()` implement cgroup v2 CPU weight files. They translate between cgroup weight, scheduler load weight, and nice values, and use `array_index_nospec()` before indexing `sched_prio_to_weight[]`.
- `cpu_period_quota_print()` and `cpu_period_quota_parse()` format and parse cgroup v2 `cpu.max` as `"max period"` or `"quota period"`, preserving the caller's prior period when the user supplies only a quota token.
- `cpu_max_show()` and `cpu_max_write()` expose `cpu.max`; `cpu.max.burst` reuses the burst read/write helpers.
- `cpu_legacy_files[]`, `rt_group_files[]`, `cpu_files[]`, and `cpu_cgrp_subsys` bind the CPU controller callbacks and file tables into cgroup core. The subsystem is `early_init` and `threaded`, with attach/cancel/online/offline/free callbacks defined outside this chunk.
- `dump_cpu_task()` dumps a target CPU's current task. In hardirq context on the current CPU it prefers interrupt registers from `get_irq_regs()` and `show_regs()`; otherwise it tries `trigger_single_cpu_backtrace()` before falling back to `sched_show_task(cpu_curr(cpu))`.
- `sched_prio_to_weight[]` and `sched_prio_to_wmult[]` are the canonical 40-entry nice-level weight and reciprocal tables used by fair scheduling load calculations.
- `call_trace_sched_update_nr_running()` is a small exported wrapper around `trace_sched_update_nr_running_tp()`.
- `struct mm_mm_cid`, `struct mm_cid_pcpu`, `task_struct::mm_cid`, `mm_cidmask(mm)`, and `mm_cpus_allowed(mm)` are the core MM CID state carriers. The local code assumes helpers from `sched.h`, including `mm_get_cid()`, `mm_unset_cid_on_task()`, `mm_drop_cid_on_cpu()`, `cid_on_task()`, `cid_on_cpu()`, `cid_in_transit()`, `cid_to_transit_cid()`, and `cpu_cid_to_cid()`.
- `__mm_update_max_cids()` recomputes the desired maximum CID count from `min(nr_cpus_allowed, users)` plus a 25 percent allowance, capped by `num_possible_cpus()`.
- `mm_cid_calc_pcpu_thrs()` computes the user-count threshold for switching back from per-CPU to per-task ownership. It never returns zero because zero means per-CPU mode is disabled.
- `mm_update_max_cids()` is the locked mode-change decider. It clears deferred updates, recomputes `max_cids`, updates `pcpu_thrs`, flips `MM_CID_ONCPU | MM_CID_TRANSIT` when the ownership mode must change, and issues an `smp_mb()` before fixups can acquire rq locks.
- `mm_update_cpus_allowed()` grows the per-mm allowed-CPU superset after affinity changes. If widening allowed CPUs makes per-CPU mode inefficient enough to switch back, it queues hard irq-work that schedules process-context work.
- `mm_cid_complete_transit()` pairs the fixup completion with an `smp_mb()` before clearing the transition mode.
- `mm_cid_transit_to_task()` and `mm_cid_transit_to_cpu()` mark a currently owned CID as transitional and mirror it into the per-CPU slot.
- `mm_cid_fixup_cpus_to_tasks()` walks all possible CPUs under each CPU's rq lock, transfers CPU-owned CIDs to currently running tasks that share the `mm`, or drops stale CPU-owned CIDs back to the bitmap pool, then completes transition to task mode.
- `mm_cid_fixup_task_to_cpu()` and `mm_cid_fixup_tasks_to_cpus()` walk the per-mm user task list under `mm_cid.mutex`, lock each task's rq, transfer running task-owned CIDs into CPU ownership, or drop non-running task CIDs, then complete transition to per-CPU mode.
- `sched_mm_cid_add_user()`, `sched_mm_cid_fork()`, `sched_mm_cid_remove_user()`, `__sched_mm_cid_exit()`, and `sched_mm_cid_exit()` implement fork/add-user and exit/remove-user paths, including last-user cleanup and mode-transition fixups.
- `sched_mm_cid_before_execve()` and `sched_mm_cid_after_execve()` disable and reactivate MM CID allocation across exec.
- `mm_cid_irq_work()` and `mm_cid_work_fn()` bridge affinity-change requests from rq-lock nesting constraints into process-context transition fixups.
- `mm_init_cid()` initializes all MM CID fields, locks, irq-work/workqueue items, the user list, the allowed CPU mask, and the CID bitmap for a new `mm_struct`.
- `sched_change_begin()` snapshots a task's queue/running/class/priority state while the rq lock is held, updates the rq clock if needed, calls class `switching_from()`/`switched_from()` around dequeue for class changes, dequeues queued tasks, and calls `put_prev_task()` for the running current-donor case.
- `sched_change_end()` restores the task after property mutation: it calls class `switching_to()`, re-enqueues or makes the task current again, calls `switched_to()` for class changes, handles class promotion/degradation preemption effects, or calls `prio_changed()` for same-class priority changes.

## Control Flow

CFS bandwidth feasibility starts with a proposed period/quota update, normally from the earlier `tg_set_cfs_bandwidth()` path. `__cfs_schedulable()` packages the proposed values, converts finite nanosecond values to microseconds, and walks the task-group tree under RCU. Each child callback normalizes the target or current group quota to a common ratio and combines it with the parent's `hierarchical_quota`. On cgroup v2 the child inherits or clamps to the finite parent constraint; on cgroup v1 a finite child over a finite parent fails with `-EINVAL`. Successful traversal leaves every visited `cfs_bandwidth.hierarchical_quota` updated for scheduler fast paths that need to know whether a task is constrained by an ancestor.

Cgroup bandwidth file writes preserve untouched fields by reading the current task-group bandwidth first, then call `tg_set_bandwidth()` with one changed value. The validator rejects root writes, values too large to convert to nanoseconds, too-small period/quota values, period values above 1 second, quotas above `MAX_BW`, and finite bursts that exceed quota or make quota-plus-burst overflow the bandwidth representation. With CFS bandwidth enabled, the CFS bandwidth state is updated first; sched_ext is notified only when that succeeds. Without CFS bandwidth, reads and successful writes operate only through the sched_ext bandwidth fields.

Cgroup stat flow differs between legacy and unified interfaces. Legacy `cpu.stat` reports raw nanosecond `throttled_time` and `burst_time`, plus `nr_periods`, `nr_throttled`, optional schedstat `wait_sum`, and `nr_bursts`. Legacy `cpu.stat.local` reports raw local throttled time. The cgroup v2 extra-stat callbacks report `throttled_usec` and `burst_usec`, converting from nanoseconds before printing, and the local-stat callback reports `throttled_usec` for self-throttling only.

The cgroup v2 weight flow validates the ABI range `[CGROUP_WEIGHT_MIN, CGROUP_WEIGHT_MAX]`, converts to scheduler weight, applies `sched_group_set_shares()`, and updates sched_ext with the original cgroup weight after success. The `weight.nice` read path scans `sched_prio_to_weight[]` until the distance to the current task-group weight stops improving, then converts the closest priority index back to nice. The write path validates nice range, converts nice to the static weight-table index with speculation-safe indexing, applies scaled scheduler shares, and reports the equivalent cgroup weight to sched_ext.

RT group files are added late only when `rt_group_sched_enabled()` is true. The static key defaults from Kconfig and can be overridden by the `rt_group_sched=` boot parameter. Registration uses a `subsys_initcall()` and emits a warning on cgroup file registration failure instead of failing boot.

The CPU cgroup subsystem object combines all of these files with lifecycle callbacks from earlier code. Legacy cgroup v1 sees `shares`, optional `idle`, CFS bandwidth files, CFS stats, RT files if registered, and optional uclamp files. The default cgroup v2 file table exposes `weight`, `weight.nice`, `idle`, `max`, `max.burst`, and optional uclamp files, all hidden from the root where marked `CFTYPE_NOT_ON_ROOT`.

MM CID mode changes start when fork, exit, or affinity changes alter `mm_cid.users` or `mm_cid.nr_cpus_allowed`. `mm_update_max_cids()` decides whether the current per-task/per-CPU mode matches the new threshold. If not, it toggles mode with `MM_CID_TRANSIT` set and publishes that state with a memory barrier before any fixup starts. During transition, scheduler switch-in/out helpers from `sched.h` can allocate, transfer, or drop temporary CIDs without waiting for the whole process to be fixed up.

Fork calls `sched_mm_cid_fork()` from `sched_post_fork()`. The first user initializes a task-owned CID and mirrors it into this CPU's per-CPU slot for execve continuity. Later users are added to `mm_cid.user_list`; if no mode change is needed the child receives a task CID in per-task mode or no immediate CID in per-CPU mode. If adding the user crosses a threshold, the current task's CID is first marked transitional under `mm_cid.lock`, then the caller runs the appropriate fixup outside the raw spinlock: task-to-CPU mode walks tasks, and CPU-to-task mode walks CPUs. After switching from per-CPU to per-task during fork, the new task obtains its task CID after the CPU walk completes.

Exit calls `sched_mm_cid_exit()` if the task has an active MM CID. For multi-user MMs, it removes the task under `mm_cid.lock`, handles any switch-back request, drops a current CPU-owned CID if needed, then runs the CPU-to-task fixup. For the last user, it may transfer the current task CID to task form for execve continuity, removes the user, then synchronizes pending irq-work and cancels process-context work because no future user can queue more MM CID work.

Affinity changes call `mm_update_cpus_allowed()` with a thread's allowed mask. The per-mm allowed mask is a growing superset, so the function ORs the new mask into `mm_cpus_allowed(mm)` and returns if the weight did not change. In per-CPU mode, a larger allowed set may lower the back-to-task threshold enough to require a deferred fixup. The code sets `update_deferred` once and queues irq-work; the irq-work unconditionally schedules the work item because `schedule_work()` cannot safely run while `mm_cid.lock` is nested inside `rq::lock`. The work function rechecks users and deferred state under `mm_cid.mutex` and `mm_cid.lock`, lets fork/exit win if they already handled the change, then performs CPU-to-task fixup.

Execve uses the same exit/fork hooks as teardown and reactivation. `sched_mm_cid_before_execve()` deactivates the old identity, and `sched_mm_cid_after_execve()` adds the task back if it still has an `mm`. `mm_init_cid()` sets the initial state for a new `mm` before any users are added.

The `sched_change` control flow is deliberately symmetrical. Begin asserts the rq lock, normalizes flags to include `DEQUEUE_NOCLOCK` after updating the rq clock, runs class pre-dequeue callbacks when `DEQUEUE_CLASS` is requested, snapshots whether the task is queued or running, records old priority for same-class changes, then removes the task from scheduling visibility. End asserts the same rq lock, warns if class changed without `ENQUEUE_CLASS`, runs class pre-enqueue callbacks, restores the task to queue/current state, and then invokes either class-change callbacks plus preemption handling or same-class `prio_changed()`.

## State and Persistence Behavior

Task-group bandwidth state persists in `struct task_group` and its embedded `struct cfs_bandwidth` or sched_ext fields. This chunk reads and updates `period`, `quota`, `burst`, `hierarchical_quota`, throttling counters, burst counters, and per-CPU `cfs_rq` self-throttling clocks. User-visible cgroup writes are persistent until a later cgroup write or task-group destruction.

The CPU cgroup file tables are static data. Which entries become visible depends on compile-time configuration and the RT static key. `cpu_cgrp_subsys` persists as the cgroup subsystem registration object for CPU scheduling control.

The scheduler weight tables are static global constants. They are part of the scheduler ABI in practice because cgroup weight/nice conversion and fair scheduling load calculations depend on their exact values.

MM CID persistent state lives in `mm->mm_cid`: `max_cids`, `mode`, `nr_cpus_allowed`, `users`, `pcpu_thrs`, `update_deferred`, `lock`, `mutex`, `irq_work`, `work`, `user_list`, per-CPU CID storage, the allowed CPU mask, and the CID allocation bitmap. Each participating task stores active/list/CID state in `task_struct::mm_cid`.

MM CID bitmap bits persist while a CID is owned by a task or CPU. Task-owned CIDs are dropped by `mm_unset_cid_on_task()`. CPU-owned CIDs are dropped by `mm_drop_cid_on_cpu()`, which clears the ONCPU bit in per-CPU storage before clearing the bitmap bit. Transitional CIDs are temporary and are either completed into the new ownership mode or dropped on schedule-out if the transition is still active.

`mm_cid.mode` is a process-wide state machine: `0` means per-task ownership, `MM_CID_ONCPU` means per-CPU ownership, and either mode ORed with `MM_CID_TRANSIT` means fixup is in progress. `pcpu_thrs` is both the per-CPU-mode switch-back threshold and the boolean indicator for whether per-CPU mode should be active.

Deferred affinity handling persists only through `mm_cid.update_deferred`, `irq_work`, and `work`. Last-user exit synchronizes and cancels both paths to avoid dangling references to an `mm` with no users.

`sched_change_ctx` is per-CPU scratch state. It must not persist beyond the begin/end pair and assumes the task remains protected by its rq lock. It records enough old state to restore queueing idempotently and to notify the old or new scheduler class correctly.

## Dependencies and Integration Points

- Cgroup core: `struct cftype`, `struct cgroup_subsys`, `seq_file`, `kernfs_open_file`, `seq_css()`, `of_css()`, `css_tg()`, `CFTYPE_NOT_ON_ROOT`, `cgroup_subsys_on_dfl()`, `cgroup_add_legacy_cftypes()`, and root/default hierarchy semantics.
- CFS bandwidth: `struct cfs_bandwidth`, `tg_get_cfs_period()`, `tg_get_cfs_quota()`, `tg_get_cfs_burst()`, `tg_set_cfs_bandwidth()`, `walk_tg_tree()`, `to_ratio()`, `RUNTIME_INF`, `MAX_BW`, `BW_UNIT`, and per-CPU `struct cfs_rq` throttling fields.
- Sched_ext integration: `scx_group_set_bandwidth()`, `scx_group_set_idle()`, `scx_group_set_weight()`, and `task_group.scx` bandwidth mirrors when CFS bandwidth is absent.
- Fair scheduling and task groups: `sched_group_set_shares()`, `tg_weight()`, `scale_load()`, `sched_weight_to_cgroup()`, `sched_weight_from_cgroup()`, `sched_prio_to_weight[]`, `sched_prio_to_wmult[]`, and idle group state.
- RT group scheduling: `sched_group_set_rt_runtime()`, `sched_group_rt_runtime()`, `sched_group_set_rt_period()`, `sched_group_rt_period()`, static branches, Kconfig defaults, and the `rt_group_sched=` early boot parameter.
- Uclamp: this chunk only wires `cpu_uclamp_min_show/write` and `cpu_uclamp_max_show/write`; parsing and storage are in the preceding chunk.
- Diagnostics and tracing: `get_irq_regs()`, `show_regs()`, `trigger_single_cpu_backtrace()`, `sched_show_task()`, `cpu_curr()`, and `trace_sched_update_nr_running_tp()`.
- Rseq/MM CID: rseq ABI state, `task_struct::mm_cid`, `mm_struct::mm_cid`, `rseq_sched_set_ids_changed()`, `rseq_sched_switch_event()`, `mm_cid_switch_to()` from `sched.h`, and context switch ordering after `switch_mm_irqs_off()`.
- Locking primitives: `mm_cid.mutex`, `mm_cid.lock`, rq locks, task rq locks, RCU guards, scoped guard helpers, raw spinlocks with IRQ state, irq-work, workqueues, and explicit `smp_mb()` ordering across mode transitions.
- CPU topology and masks: `num_possible_cpus()`, `for_each_possible_cpu()`, `cpumask_weighted_or()`, `cpumask_copy()`, `task_cpu()`, `this_cpu_ptr()`, `per_cpu_ptr()`, and per-CPU MM CID storage.
- Fork/exit/exec/scheduler lifecycle: `sched_post_fork()`, failed fork cleanup paths, `sched_mm_cid_before_execve()`, `sched_mm_cid_after_execve()`, task exit, affinity changes, and context switching.
- Scheduler class API: `dequeue_task()`, `enqueue_task()`, `put_prev_task()`, `set_next_task()`, `task_on_rq_queued()`, `task_current_donor()`, class callbacks `switching_from`, `switched_from`, `switching_to`, `switched_to`, `get_prio`, `prio_changed`, `wakeup_preempt`, `sched_class_above()`, `resched_curr()`, and `rq->next_class`.

## Risks and Edge Cases

- CFS hierarchy validation has different cgroup v1 and cgroup v2 semantics. Accidentally applying v2 clamping to v1 would silently accept invalid child-over-parent quotas; applying v1 rejection to v2 would reject valid unified-hierarchy configurations that rely on ancestor clamping.
- `__cfs_schedulable()` mutates `hierarchical_quota` while walking. Any future error path or partial walk behavior must preserve the scheduler's expectation that this cached value reflects the current effective ancestor limit.
- Bandwidth values cross unit domains. The validators must reject values that overflow microsecond-to-nanosecond conversion or bandwidth shifting, and `RUNTIME_INF` must be kept out of finite arithmetic such as `burst + quota`.
- The minimum quota/period rule intentionally rejects too-small quota and period values to avoid large arrears and exit starvation after throttling. Relaxing it can produce long throttle recovery stalls.
- `cpu_period_quota_parse()` allows a single-token write by preserving the caller-provided period. Callers must initialize `*period_us_p` to the current period before parsing, as `cpu_max_write()` does.
- Legacy and cgroup v2 stats use different units and field names. Reusing one printer for both can break user-space ABI expectations around `throttled_time` nanoseconds versus `throttled_usec` microseconds.
- `cpu_weight_nice_read_s64()` assumes the weight table is monotonic enough for the first non-improving distance to identify the closest nice value. Weight-table changes need to preserve this property or adjust the search.
- `array_index_nospec()` protects the nice-to-weight index after range validation. Removing it would reopen speculative out-of-bounds exposure on a user-controlled nice value.
- RT group file registration depends on a static key set by early boot parsing. Changing registration timing could expose files after cgroup setup in an unexpected hierarchy state.
- `dump_cpu_task()` must avoid trying to IPI-backtrace the same CPU from hardirq when register state is directly available. The hardirq/current-CPU branch is important for diagnostic reliability.
- MM CID mode transitions depend on the transition bit and memory barriers. If the mode store is reordered after fixups, schedule-in code under rq lock can observe stale mode and allocate/transfer CIDs incorrectly.
- The CID bitmap is intentionally not protected by `mm_cid.lock`; allocation and drop use atomic bit operations. Any code that assumes the spinlock serializes the bitmap can create races or CID leaks.
- `mm_cid.mutex` serializes fork/exit and mode transitions, while `mm_cid.lock` nests inside it and inside rq locking for affinity updates. Inverting this order risks deadlock with scheduler paths.
- Fixup walks intentionally hold rq locks only for short sections. Expanding work inside `mm_cid_fixup_cpus_to_tasks()` or `mm_cid_fixup_task_to_cpu()` can harm real-time latency and block scheduler progress.
- Per-task to per-CPU transition can livelock if task CIDs are directly transferred without the transitional drop behavior. The two-phase transition is specifically there to avoid CID-space exhaustion while tasks migrate during fixup.
- Per-CPU to per-task transition has the symmetric risk when multiple tasks schedule on the same CPU before the CPU walk reaches it. The transition bit lets schedule-out drop temporary CIDs instead of exhausting the bitmap.
- `mm_update_cpus_allowed()` only grows the per-mm allowed mask. Tests or callers expecting shrink behavior will not see `nr_cpus_allowed` decrease until a new `mm` is created.
- The affinity deferred-work path intentionally uses irq-work as a bridge. Calling `schedule_work()` directly while nested under rq-lock-related paths can interact badly with wakeup locking.
- Last-user exit must synchronize irq-work and cancel work. Missing this can leave queued work with a reference to an `mm` after all users have gone away.
- Execve relies on the first-user fork path mirroring the CID into the per-CPU slot and on last-user exit preserving continuity for the current task. Incorrect cleanup can leave stale rseq CID state across exec.
- `sched_change_begin()` and `sched_change_end()` use a per-CPU context, so nested use on the same CPU would overwrite state. Callers need the scoped pattern to remain non-nested unless the implementation changes.
- Scheduler class changes require matched dequeue/enqueue class flags. The begin path warns on upper flag bits, and the end path warns if the class changed without `ENQUEUE_CLASS`; ignoring these warnings can cause missed class callbacks or stale class runqueue state.
- The running-task case must call `put_prev_task()` before mutation and `set_next_task()` after restoration. Missing either side can desynchronize the current task's scheduler-class state.
- Class promotion while running calls the old `rq->next_class->wakeup_preempt()` and updates `rq->next_class`; class degradation forces `resched_curr()`. Reordering or dropping this can leave a lower-priority running task in place after policy changes.

## Test Signals

- CFS bandwidth hierarchy tests should cover finite child below parent, finite child above finite parent on cgroup v1 returning `-EINVAL`, cgroup v2 ancestor clamping, unlimited child inheriting a finite parent, unlimited root, and nested updates after a parent quota change.
- Bandwidth ABI tests should write legacy `cpu.cfs_period_us`, `cpu.cfs_quota_us`, `cpu.cfs_burst_us`, cgroup v2 `cpu.max`, and `cpu.max.burst`, checking root rejection, negative quota as unlimited, single-token `cpu.max` preserving period, quota/burst overflow rejection, 1 ms lower bound, 1 s period upper bound, and sched_ext mirror updates after success.
- Stat tests should verify legacy `cpu.stat` raw nanosecond fields, optional `wait_sum` only with schedstats and non-root task groups, cgroup v2 `throttled_usec`/`burst_usec` conversion, and local throttling aggregation across possible CPUs.
- Weight tests should cover min/max cgroup weight bounds, conversion round trips, `weight.nice` range rejection, closest-nice readback for in-between weights, and sched_ext weight update only after `sched_group_set_shares()` succeeds.
- RT group tests should boot with `rt_group_sched=0` and `rt_group_sched=1`, confirming legacy RT files are hidden or registered as expected, and should cover invalid boot parameter values producing the warning path.
- Uclamp wiring tests should confirm legacy and cgroup v2 min/max files use the preceding chunk's parser/show functions and remain hidden from root where marked.
- `dump_cpu_task()` tests should exercise same-CPU hardirq register dump, successful remote backtrace, and fallback `sched_show_task()` output for a CPU whose backtrace trigger fails.
- MM CID fork tests should cover first user allocation, additional user in per-task mode, crossing into per-CPU mode, task-list fixup for running and sleeping tasks, failed fork cleanup, and children with `mm == NULL`.
- MM CID exit tests should cover removing a non-last user without mode change, switching back to task mode as users drop below threshold, dropping a current CPU-owned CID, last-user cleanup, and synchronization of pending irq-work/work.
- MM CID affinity tests should widen a thread's CPU mask in per-task and per-CPU modes, verify the per-mm allowed mask only grows, confirm deferred work is queued once, and check that fork/exit can clear `update_deferred` before the work function runs.
- MM CID context-switch tests should validate rseq CID updates in both ownership modes, transitional CID drop on schedule-out, convergence into `max_cids`, and ordering relative to `switch_mm_irqs_off()` and `rseq_sched_switch_event()`.
- Execve tests should call before/after hooks around an exec path and confirm CID deactivation/reactivation without stale active-list entries or leaked bitmap bits.
- Locking tests should run lockdep with fork/exit/affinity/context-switch stress to catch incorrect nesting between `mm_cid.mutex`, `mm_cid.lock`, rq locks, and task rq locks.
- `sched_change` tests should mutate same-class priority for queued, running, and sleeping tasks, checking dequeue/enqueue pairing and `prio_changed()` old-priority delivery.
- Scheduler class-change tests should cover promotion and degradation of a running task, verify `switching_from`/`switched_from`/`switching_to`/`switched_to` order, ensure `resched_curr()` happens on degradation, and confirm the warning path catches class changes without `ENQUEUE_CLASS`.

## Chunk Boundary Notes

The cgroup code in this chunk relies on earlier task-group allocation, attach, CFS bandwidth mutation, share-setting, and uclamp parsing code. The MM CID implementation relies on helpers in `sched.h` and on context-switch hooks earlier in `core.c`; later chunks and other files provide architecture rseq exposure and user-space ABI behavior. The final per-file research should merge this with the preceding `kernel/sched/core.c` chunk so CPU controller lifecycle, fork/exit scheduling hooks, and MM CID context-switch behavior are presented as one continuous scheduler core implementation.
