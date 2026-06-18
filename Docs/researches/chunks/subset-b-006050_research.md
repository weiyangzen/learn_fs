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
