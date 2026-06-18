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
