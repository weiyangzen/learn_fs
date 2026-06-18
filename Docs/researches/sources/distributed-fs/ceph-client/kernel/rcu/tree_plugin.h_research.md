# sources/distributed-fs/ceph-client/kernel/rcu/tree_plugin.h

## Purpose
`tree_plugin.h` supplies configuration-dependent tree-RCU behavior, especially the differences between preemptible RCU and non-preemptible RCU. It implements blocked-reader tracking, RCU read-side entry/exit, context-switch quiescent-state reporting, deferred quiescent states, priority boosting, callback kthread priority setup, and NO_HZ_FULL helper policy. It is a private include for tree RCU rather than a standalone translation unit.

## Important APIs, Types, and Functions
- Offload state check: `rcu_rdp_is_offloaded()` validates that callers read NOCB state only under safe synchronization.
- Boot announcement: `rcu_bootup_announce_oddness()` and `rcu_bootup_announce()` report selected RCU features and non-default tuning.
- Preemptible RCU path: `rcu_preempt_ctxt_queue()`, `rcu_note_context_switch()`, `__rcu_read_lock()`, `__rcu_read_unlock()`, `rcu_preempt_deferred_qs_irqrestore()`, `rcu_read_unlock_special()`, `exit_rcu()`, and `dump_blkd_tasks()` maintain blocked-reader state.
- Non-preemptible path: `rcu_qs()`, `rcu_all_qs()`, `rcu_note_context_switch()`, and `rcu_read_unlock_strict()` provide quiescent-state reporting without blocked-reader lists.
- Boosting: `rcu_boost()`, `rcu_boost_kthread()`, `rcu_initiate_boost()`, `rcu_preempt_boost_start_gp()`, and `rcu_spawn_one_boost_kthread()` implement priority boosting for tasks blocking RCU grace periods.
- Kthread/NO_HZ helpers: `rcu_cpu_kthread_setup()`, `rcu_is_callbacks_kthread()`, `rcu_nohz_full_cpu()`, and `rcu_bind_gp_kthread()`.

## Control Flow
In preemptible builds, `__rcu_read_lock()` increments the current task nesting counter and `__rcu_read_unlock()` decrements it. If the outermost unlock sees special work, `rcu_read_unlock_special()` either handles it immediately or defers it through softirq, scheduler reschedule, or IRQ work depending on interrupt, softirq, and expedited-GP conditions.

When a task context-switches inside an RCU read-side critical section, `rcu_note_context_switch()` queues the task into the leaf `rcu_node->blkd_tasks` list via `rcu_preempt_ctxt_queue()`. That queueing chooses list position based on whether normal and/or expedited grace periods are already blocked. Later, `rcu_preempt_deferred_qs_irqrestore()` removes the task from blocked lists, advances `gp_tasks`, `exp_tasks`, and `boost_tasks`, reports unblocked quiescent states, and drops artificial boost mutex ownership if needed.

In non-preemptible builds, context-switch and clock-tick paths only report CPU quiescent states because readers cannot be preempted into `blkd_tasks`. `rcu_all_qs()` handles urgent quiescent-state requests and can force a momentary extended quiescent state when the core asks for a heavy QS.

Boosting starts when a GP has waited past `boost_time`, when callback overload or strict GP mode demands it, or when an expedited GP is blocked. The boost kthread fabricates an `rt_mutex` held by the blocked task, locks it to donate priority, and relies on the task to release/deboost when it exits the read-side critical section.

## State and Persistence
State is in current task fields (`rcu_read_lock_nesting`, `rcu_read_unlock_special`, `rcu_node_entry`, `rcu_blocked_node`), per-CPU `rcu_data` (`cpu_no_qs`, deferred QS irq_work state, callback kthread task/activity), and `rcu_node` fields (`blkd_tasks`, `gp_tasks`, `exp_tasks`, `boost_tasks`, `boost_time`, boost kthread state, `qsmask`, `expmask`). There is no durable persistence; all state is scheduler/RCU runtime state.

## Dependencies and Integration Points
This code integrates tightly with the scheduler (`rcu_note_context_switch()`), lockdep, irq_work, softirq processing, task exit, RCU grace-period core, expedited GP code, NOCB callback threads, `rtmutex_common.h`, CPU isolation/housekeeping, and tracepoints. Exported read-lock/unlock functions are used by the kernel-wide RCU API, while private helpers are called from `tree.c` and other RCU internals.

## Risks
The highest risks are incorrect blocked-reader list placement, missed deferred quiescent-state reporting, lock ordering around `rcu_node->lock`, and stale task state during boosting. False positives in expedited handling are tolerated, but false negatives can stall grace periods. Boosting uses artificial rtmutex ownership and must stay synchronized with task exit and unlock paths. Non-preemptible and preemptible variants share names with different semantics, so configuration-specific test coverage is important.

## Test Signals
Signals include rcutorture preemptible/non-preemptible scenarios, expedited GP torture, lockdep warnings from read-side misuse, RCU boost kthread activity, traces for `rcu_preempt_task` and unlock events, scheduler context-switch warnings for voluntary switches inside RCU read-side sections, and stall reports that include blocked task lists or boost counters.
