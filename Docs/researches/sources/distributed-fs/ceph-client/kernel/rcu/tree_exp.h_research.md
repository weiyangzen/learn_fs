# sources/distributed-fs/ceph-client/kernel/rcu/tree_exp.h

## Purpose

`tree_exp.h` implements expedited Tree RCU grace periods inside the `tree.c` translation unit. Expedited grace periods provide the same semantic guarantee as `synchronize_rcu()`, but they aggressively identify and poke CPUs that might still be in pre-existing RCU read-side critical sections. The file also implements expedited variants of the polled and conditional synchronization APIs.

Because this header is included at the end of `tree.c`, it directly uses `rcu_state`, `rcu_data`, the `rcu_node` hierarchy, normal polled-GP helpers, context tracking helpers, stall reporting helpers, NOCB/workqueue state, and preemptible-RCU hooks declared in `tree.h` and defined in `tree.c` or `tree_plugin.h`.

## Important APIs and functions

Sequence helpers:

- `rcu_exp_gp_seq_start()` starts `rcu_state.expedited_sequence` and also starts the expedited snapshot of the combined polled GP state.
- `rcu_exp_gp_seq_endval()` returns the sequence value that will represent the end of the current expedited GP.
- `rcu_exp_gp_seq_end()` ends both the polled expedited snapshot and `expedited_sequence`, then issues a memory barrier to serialize consecutive expedited GPs.
- `rcu_exp_gp_seq_snap()` returns a snapshot cookie and orders caller updates before remote CPUs observe the expedited GP.
- `rcu_exp_gp_seq_done()` tests whether a snapshot has completed.

Tree reset and reporting:

- `sync_exp_reset_tree_hotplug()` propagates newly onlined CPUs into `expmaskinit` up the tree. Offline CPUs are intentionally not cleared from expedited initial masks, so the state is the union of CPUs that have ever been online.
- `sync_exp_reset_tree()` initializes each node's `expmask` from `expmaskinit` and records blocked preemptible tasks in `exp_tasks`.
- `sync_rcu_exp_done()` and `sync_rcu_exp_done_unlocked()` test whether a node has no remaining CPUs and no blocking tasks for the expedited GP.
- `__rcu_report_exp_rnp()`, `rcu_report_exp_rnp()`, `rcu_report_exp_cpu_mult()`, and `rcu_report_exp_rdp()` clear expedited wait bits and propagate completion up the tree, waking the global expedited wait queue if the root completes.

Expedited request funnel and CPU selection:

- `sync_exp_work_done()` tests completion and provides the memory barrier paired with `rcu_seq_end()`.
- `exp_funnel_lock()` lets concurrent callers either piggyback on an existing expedited GP, wait at an intermediate `rcu_node`, or acquire `rcu_state.exp_mutex` and become the worker for a new expedited GP.
- `__sync_rcu_exp_select_node_cpus()` scans one leaf node, treats self/offline/idle CPUs as already quiescent where valid, records context-tracking snapshots, sends IPIs to remaining CPUs via `smp_call_function_single()`, retries races with CPU hotplug, and reports CPUs that went idle or offline.
- `sync_rcu_exp_select_cpus()` resets expedited masks, schedules or directly runs per-leaf CPU selection work, and flushes per-node workers.
- `rcu_exp_sel_wait_wake()` drives a full expedited GP by selecting CPUs and then waiting/waking.

Wait and stall handling:

- `synchronize_rcu_expedited_wait_once()` waits for root completion for a bounded timeout.
- `synchronize_rcu_expedited_wait()` loops until completion, handles nohz-full forced ticks, and emits expedited stall reports through `synchronize_rcu_expedited_stall()`.
- `synchronize_rcu_expedited_stall()` prints CPUs/tasks still blocking the expedited GP, dumps blocking CPU tasks, and optionally prints blocked preemptible reader stacks.
- `rcu_exp_wait_wake()` finishes the expedited GP, ends the sequence, updates per-node `exp_seq_rq`, and wakes all waiters that piggybacked on this sequence.

IPI/deferred-QS handling:

- `rcu_exp_need_qs()` marks the current CPU as owing an expedited QS and requests rescheduling.
- Under `CONFIG_PREEMPT_RCU`, `rcu_exp_handler()` distinguishes CPUs currently inside preemptible RCU read-side critical sections from CPUs that can report immediately. It sets `t->rcu_read_unlock_special.b.exp_hint` for readers that must report at unlock time.
- Without `CONFIG_PREEMPT_RCU`, `rcu_exp_handler()` reports immediately when idle or preempt/BH-enabled and otherwise requests a deferred expedited QS.
- `rcu_print_task_exp_stall()` and `rcu_exp_print_detail_task_stall_rnp()` report task blockers only for preemptible RCU; non-preempt builds return no task blockers.

Exported public APIs:

- `synchronize_rcu_expedited()` is the main blocking expedited GP primitive.
- `start_poll_synchronize_rcu_expedited()` and `start_poll_synchronize_rcu_expedited_full()` snapshot state and arrange for an expedited GP if needed.
- `cond_synchronize_rcu_expedited()` and `cond_synchronize_rcu_expedited_full()` wait only if the supplied cookie has not already seen a full normal or expedited GP.

`sync_rcu_do_polled_gp()` is the workqueue bridge for polled expedited requests. It repeatedly invokes `synchronize_rcu_expedited()` until the normal polled cookie completes, then clears the per-node request if no longer needed.

## Control flow

`synchronize_rcu_expedited()` first rejects use from RCU read-side critical sections via lockdep warnings. In earliest boot, `rcu_blocking_is_gp()` allows a vacuous GP and simply advances the expedited sequence. If expedited GPs are globally disabled or normal-only policy is active, it falls back to `synchronize_rcu_normal()`.

In the runtime expedited path, the caller takes a snapshot with `rcu_exp_gp_seq_snap()`. `exp_funnel_lock()` then either returns true because another task completed the needed GP, blocks behind another in-progress expedited GP at a node wait queue, or returns false with `rcu_state.exp_mutex` held so the caller owns the new expedited GP. The owner starts the sequence, then either runs `rcu_exp_sel_wait_wake()` directly during scheduler initialization or before the expedited worker exists, or queues `wait_rcu_exp_gp()` to the global expedited kworker. The original caller waits on the root's sequence-indexed `exp_wq[]` until `sync_exp_work_done()` sees completion, then unlocks `exp_mutex`.

`sync_rcu_exp_select_cpus()` prepares the tree with `sync_exp_reset_tree()`. For each leaf node with a nonzero `expmask`, it uses a per-node expedited worker when available and useful, but falls back to direct execution for early boot, non-running scheduler state, or the last leaf. Each leaf worker calls `__sync_rcu_exp_select_node_cpus()`. That function first checks each target CPU under the leaf lock: current CPU, CPUs no longer in the online mask, and CPUs already in extended quiescent states are added to a local report mask. CPUs still potentially active get a context-tracking snapshot and are later sent an IPI. Before sending or after IPI failure, it rechecks whether the CPU passed through idle/offline state to avoid unnecessary or invalid IPIs.

The remote `rcu_exp_handler()` is the critical fast path. If the CPU is not in an RCU read-side critical section and is in a context where it can report, it calls `rcu_report_exp_rdp()`. If it cannot report immediately, it sets the per-CPU expedited no-QS bit and urgent-QS state so a later context switch, scheduler tick, or read-unlock path will report. For preemptible readers, it sets the current task's expedited unlock-special hint while holding the leaf node lock if the leaf still waits on this CPU.

Waiting is centralized in `synchronize_rcu_expedited_wait()`. It first gives nohz-full CPUs a short chance to complete, then forces `TICK_DEP_BIT_RCU_EXP` on CPUs still blocking the GP if necessary. It waits repeatedly on the expedited swait queue and, on timeout, emits stall diagnostics, invokes the stall notifier chain, and honors `panic_on_rcu_stall()`.

Completion uses `rcu_exp_wait_wake()`. It serializes wakeup with `exp_wake_mutex`, ends the expedited sequence, updates all `exp_seq_rq` values that lag behind the completed sequence, issues a memory barrier before wakeups, and wakes all per-node wait queues for the sequence index. This lets later callers piggyback safely and prevents sequence-wrap confusion.

The polled expedited API starts with the normal combined state from `get_state_synchronize_rcu()`. If that state is not already complete, it records the request under the current leaf node's `exp_poll_lock` and queues `exp_poll_wq` on `rcu_gp_wq`. The work item drives expedited GPs until the normal polling cookie completes, which allows callers to poll with the same `poll_state_synchronize_rcu()` function used by normal polling.

## State and persistence behavior

Expedited state is in memory and layered on the normal Tree RCU topology:

- `rcu_state.expedited_sequence` is the primary expedited GP sequence counter.
- `rcu_state.exp_mutex` serializes expedited GP execution. `exp_wake_mutex` serializes completion wakeups with the start of the next expedited GP.
- `rcu_state.expedited_wq` wakes the owner waiting for root completion.
- Each `rcu_node` has `expmask`, `expmaskinit`, and `expmaskinitnext` for expedited CPU/task wait state, plus `exp_seq_rq` and `exp_wq[4]` for funnel-lock waiters.
- Each leaf `rcu_node` has `rew` and optional `exp_kworker` for parallel CPU selection.
- Each `rcu_data` uses `cpu_no_qs.b.exp`, `exp_watching_snap`, and `rcu_forced_tick_exp` to track per-CPU expedited obligations.
- `exp_seq_poll_rq` and `exp_poll_wq` hold outstanding polled expedited work per node.

`sync_exp_reset_tree_hotplug()` commits newly onlined CPUs but intentionally does not remove offline CPUs from `expmaskinit`. That design avoids missing CPUs that have ever participated while allowing offline or idle checks to clear them quickly during selection.

Memory ordering is explicit. `rcu_exp_gp_seq_snap()` orders caller updates before the expedited GP is requested; `rcu_exp_gp_seq_end()` and `sync_exp_work_done()` provide completion ordering; and leaf selection relies on context-tracking acquire loads plus the lock/unlock chain through the `rcu_node` tree.

## Dependencies and integration points

This file depends heavily on `tree.c` internals:

- Normal GP/poll helpers: `rcu_poll_gp_seq_start_unlocked()`, `rcu_poll_gp_seq_end_unlocked()`, `get_state_synchronize_rcu()`, `poll_state_synchronize_rcu()`, and `synchronize_rcu_normal()`.
- Context and dynticks helpers: `ct_rcu_watching_cpu_acquire()`, `rcu_watching_snap_in_eqs()`, `rcu_watching_snap_stopped_since()`, `rcu_is_cpu_rrupt_from_idle()`, and nohz-full tick dependency APIs.
- Preemptible-RCU hooks: `rcu_preempt_depth()`, `rcu_preempt_has_tasks()`, task blocked-reader lists, and `rcu_read_unlock_special`.
- Stall/reporting infrastructure: `rcu_exp_jiffies_till_stall_check()`, `rcu_stall_is_suppressed()`, `rcu_stall_notifier_call_chain()`, `trace_rcu_stall_warning()`, `panic_on_rcu_stall()`, `dump_cpu_task()`, and `sched_show_task()`.
- Kthread workers and workqueues: global `rcu_exp_gp_kworker`, per-node `exp_kworker`, and `rcu_gp_wq`.
- CPU hotplug and SMP IPI mechanisms: `cpu_online()`, `smp_call_function_single()`, and per-node `qsmaskinitnext` checks.

The exported expedited APIs integrate with the public RCU API surface and may be selected indirectly by `synchronize_rcu()` when `rcu_gp_is_expedited()` is true.

## Risks and correctness concerns

Expedited RCU is intentionally aggressive, so most risks involve races with CPU state changes:

- `__sync_rcu_exp_select_node_cpus()` must recheck context-tracking snapshots and online masks around IPI attempts. Treating an IPI failure as a quiescent state without confirming hotplug state can shorten a GP incorrectly.
- The `exp_funnel_lock()` protocol relies on `exp_seq_rq`, per-node wait queues, and `exp_mutex` to avoid duplicate expedited GPs while still letting followers wait. Incorrect sequence comparisons can strand waiters or allow overlapping expedited GPs.
- The four-entry `exp_wq[]` array is indexed by sequence counter bits. Wakeups must update `exp_seq_rq` and issue barriers before waking to avoid missed completion on wrap-prone low bits.
- Preemptible-RCU `rcu_exp_handler()` must check `rnp->expmask` under the lock before setting task unlock-special hints, because the expedited GP can complete concurrently.
- Forced ticks for nohz-full expedited waiters must be cleared in `rcu_report_exp_cpu_mult()` when the corresponding CPU reports. Leaking `TICK_DEP_BIT_RCU_EXP` harms isolation and power behavior.
- Stall diagnostics run while expedited GP progress is impaired and sometimes while holding locks. The code touches watchdogs in task-detail printing to reduce hard-lockup risk.

## Test signals

Useful validation includes:

- `rcutorture` expedited scenarios, especially with `CONFIG_PREEMPT_RCU`, `CONFIG_NO_HZ_FULL`, hotplug, and high CPU counts.
- Concurrent loops of `synchronize_rcu_expedited()`, `synchronize_rcu()`, `start_poll_synchronize_rcu_expedited()`, and `cond_synchronize_rcu_expedited()` to stress piggybacking and sequence wakeups.
- CPU hotplug while expedited GPs are in flight, watching for WARNs in `__sync_rcu_exp_select_node_cpus()`, stuck `expmask` bits, or expedited stalls.
- nohz-full isolation tests confirming forced expedited ticks are set only for blocking CPUs and cleared after reporting.
- Preemptible reader tests that block in RCU read-side critical sections during expedited GPs, validating `exp_tasks`, task stall printing, and unlock-special reporting.
- Tracepoint checks for `rcu_exp_grace_period` and `rcu_exp_funnel_lock` transitions: `snap`, `start`, `reset`, `select`, `startwait`, `end`, and `endwake`.
