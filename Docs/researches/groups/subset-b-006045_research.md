# Research: subset-b-006045

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/rcu/srcutree.c -->
# sources/distributed-fs/ceph-client/kernel/rcu/srcutree.c

## Purpose
Implements the hierarchical SRCU backend used when sleepable RCU must scale beyond the tiny/uniprocessor implementation. This file owns dynamic and static `srcu_struct` initialization, per-CPU reader counters, segmented callback queues, SRCU grace-period sequencing, callback invocation, barriers, expedited/current-grace-period handling, runtime conversion from small to big combining-tree mode, torture/debug reporting, early boot work deferral, and module notifier support for statically declared SRCU domains in loadable modules.

## Important APIs, Types, and Functions
The exported construction/destruction APIs are `init_srcu_struct()`, `init_srcu_struct_fast()`, `init_srcu_struct_fast_updown()`, their lockdep-aware `__init_srcu_struct*()` forms, and `cleanup_srcu_struct()`. The reader primitives exported from this implementation are `__srcu_read_lock()`, `__srcu_read_unlock()`, and the `CONFIG_NEED_SRCU_NMI_SAFE` atomic variants `__srcu_read_lock_nmisafe()` and `__srcu_read_unlock_nmisafe()`. Update-side and polling APIs include `call_srcu()`, `synchronize_srcu()`, `synchronize_srcu_expedited()`, `get_state_synchronize_srcu()`, `start_poll_synchronize_srcu()`, `poll_state_synchronize_srcu()`, `srcu_barrier()`, `srcu_expedite_current()`, and `srcu_batches_completed()`.

The core state is split between `struct srcu_struct`, its `struct srcu_usage` support object, per-CPU `struct srcu_data`, optional combining-tree `struct srcu_node` nodes, two `srcu_ctr` counter ranks, and `rcu_segcblist` callback lists. Important internal functions are `init_srcu_struct_fields()`, `init_srcu_struct_data()`, `init_srcu_struct_nodes()`, `check_init_srcu_struct()`, `srcu_gp_start_if_needed()`, `srcu_funnel_gp_start()`, `srcu_funnel_exp_start()`, `srcu_advance_state()`, `srcu_gp_start()`, `srcu_gp_end()`, `srcu_flip()`, `try_check_zero()`, `srcu_readers_active_idx_check()`, `process_srcu()`, `srcu_reschedule()`, `srcu_invoke_callbacks()`, `srcu_irq_work()`, and `srcu_delay_timer()`.

Module parameters tune behavior: `exp_holdoff` controls auto-expedite holdoff, `counter_wrap_check` controls counter-wrap cleanup frequency, `convert_to_big`/`big_cpu_lim`/`small_contention_lim` control small-to-big sizing, and `srcu_retry_check_delay`, `srcu_max_nodelay_phase`, and `srcu_max_nodelay` control grace-period retry pacing.

## Control Flow
Initialization builds the `srcu_usage` object, per-CPU `srcu_data`, locks, delayed work, irq work, barrier state, sequence numbers, and optionally the combining tree. Statically allocated SRCU domains defer full initialization until first update-side use through `check_init_srcu_struct()`, which serializes the first-use path on the statically initialized support lock. Early boot callback work is collected on `srcu_boot_list` until `srcu_init()` marks SRCU ready and queues pending work to `rcu_gp_wq`.

Reader entry snapshots `ssp->srcu_ctrp`, increments the selected per-CPU lock counter, executes the required barrier, and returns the counter index. Reader exit executes the matching barrier and increments the unlock counter for the saved index. NMI-safe readers use atomic long operations and atomic memory barriers.

`call_srcu()` validates the `rcu_head`, stores the callback function, and calls `srcu_gp_start_if_needed()`. That helper enters a short NMI-safe SRCU read-side section to prevent sequence wrap while it enqueues/accelerates callbacks, snapshots the target grace-period sequence, records per-CPU and per-node grace-period demand, optionally marks the target expedited, and wakes or starts the grace-period worker. The funnel functions propagate requests up the optional `srcu_node` tree and then to the top-level `srcu_usage` sequence counters.

The grace-period state machine runs from workqueue context. `srcu_gp_start()` moves `srcu_gp_seq` from idle into `SRCU_STATE_SCAN1`. `srcu_advance_state()` waits for readers on the old counter rank, flips `srcu_ctrp`, advances to `SRCU_STATE_SCAN2`, waits for readers on the other rank, and calls `srcu_gp_end()`. `srcu_gp_end()` ends the sequence, releases `srcu_gp_mutex`, schedules per-CPU callback invocation for completed segments, updates node callback markers, prevents stale per-CPU needed counters from wrapping too far, starts a follow-on grace period when needed, and advances any in-progress transition to `SRCU_SIZE_BIG`. `process_srcu()` computes a delay based on expedited state, current grace-period age, and no-delay throttles, then calls `srcu_reschedule()`.

Callback invocation is separated from grace-period advancement. `srcu_invoke_callbacks()` advances a per-CPU segmented callback list to the current completed sequence, extracts ready callbacks, invokes them with bottom halves disabled, fixes the list length, and reschedules itself if more callbacks are ready. `srcu_barrier()` serializes with other barriers, entrains one marker callback onto each callback list that currently has callbacks, waits for the marker completion count, and then ends the barrier sequence.

## State and Persistence Behavior
State is in memory only. SRCU domains persist for the lifetime of their owning object or static/module lifetime and must be cleaned up explicitly if dynamically initialized. Key persistent-in-memory fields are `srcu_gp_seq`, `srcu_gp_seq_needed`, `srcu_gp_seq_needed_exp`, `srcu_last_gp_end`, `srcu_size_state`, per-CPU segmented callback queues, per-CPU lock/unlock counters, per-node callback masks, barrier sequence/count/completion state, and expedite-current state in `srcu_ec_state`.

The small mode uses a boot CPU or local per-CPU callback queue before the combining tree is fully initialized. The big mode allocates `srcu_node` geometry derived from generic RCU tree geometry and tracks callback/grace-period demand hierarchically. Cleanup refuses to free active domains: it warns and leaks instead of freeing if there are active readers, callbacks, an active grace period, or mismatched needed/completed sequences.

## Dependencies and Integration Points
This file depends on Linux workqueues, timers, irq work, per-CPU allocation, raw spinlocks, mutexes, completions, module notifiers, `rcu_seq`, lockdep, `rcu_segcblist`, and generic RCU helpers from `rcu.h`. It integrates with public SRCU APIs declared in `<linux/srcu.h>`, RCU callback debugging, rcutorture via `srcutorture_get_gp_data()` and `srcu_torture_stats_print()`, module load/unload via `srcu_module_notify()`, early boot via `early_initcall(srcu_bootup_announce)` and `srcu_init()`, and RCU workqueues through `rcu_gp_wq`.

Consumers include subsystems that need sleepable readers and explicit SRCU domains, such as notifier chains, tracing/BPF-related paths, device subsystems, filesystem code, and module statics declared with SRCU macros.

## Risks and Edge Cases
The highest-risk area is memory ordering across reader counter increments, counter-rank flips, grace-period completion, and callback invocation; the file contains several paired barriers (`B`, `C`, `D`, `E`, and polling barriers) whose removal or weakening can create use-after-free or premature callback execution. Sequence wrap is intentionally managed by entering an SRCU read-side section while starting a grace period and by periodically clamping per-CPU needed counters; changes here can break polling APIs or callback acceleration.

Other risks include duplicate callback queueing, cleanup while callbacks/readers remain active, static SRCU first-use races, early boot queuing before workqueues are ready, transition races between small and big sizing states, expedited grace-period starvation or CPU-bound no-delay looping, callback invocation reentrancy around `srcu_barrier()`, NMI-unsafe reader use from NMI context, and module unload paths freeing per-CPU storage while statically allocated SRCU state is still active.

## Test Signals
Useful signals are `rcutorture` SRCU scenarios, `srcutorture_get_gp_data()` sequence progression, `srcu_torture_stats_print()` counter/callback output, lockdep warnings for illegal same-domain `synchronize_srcu()` and mixed reader flavors, debug-object warnings for duplicate `rcu_head` queueing, module load/unload tests using static SRCU domains, expedited and normal `synchronize_srcu()` latency tests, polling API wrap/regression tests, `srcu_barrier()` tests with callbacks on multiple CPUs, cleanup tests that intentionally leave readers/callbacks active, and boot logs from `srcu_bootup_announce()` and `srcu_init()` sizing decisions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/rcu/srcutree.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/rcu/sync.c -->
# sources/distributed-fs/ceph-client/kernel/rcu/sync.c

## Purpose
Provides `rcu_sync`, a small state-machine helper for lightweight reader/writer coordination. Updaters use it to force readers off a fast path during a write-side interval and then allow fast-path readers again only after the required RCU grace period. The design batches closely spaced enter/exit cycles so repeated writers do not always pay a fresh grace-period cost.

## Important APIs, Types, and Functions
The public API is `rcu_sync_init()`, `rcu_sync_enter()`, `rcu_sync_exit()`, and `rcu_sync_dtor()` for `struct rcu_sync` from `<linux/rcu_sync.h>`. Internal states are `GP_IDLE`, `GP_ENTER`, `GP_PASSED`, `GP_EXIT`, and `GP_REPLAY`. `rss_lock` aliases `gp_wait.lock`, so the waitqueue lock also protects `gp_state` and `gp_count`. `rcu_sync_call()` queues `cb_head` with `call_rcu_hurry()`, and `rcu_sync_func()` is the RCU callback that advances the state machine and wakes waiters.

## Control Flow
`rcu_sync_init()` zeroes the structure and initializes the waitqueue. `rcu_sync_enter()` takes `rss_lock`, observes the current state, transitions an idle structure to `GP_ENTER`, increments `gp_count`, and drops the lock. The first entrant synchronously waits for `synchronize_rcu()` and then directly invokes `rcu_sync_func()` to mark that all pre-existing readers have been pushed through a grace period. Later entrants wait until `gp_state >= GP_PASSED`, avoiding redundant grace-period waits when another writer already paid the cost.

`rcu_sync_exit()` decrements `gp_count`. When the last active writer exits from `GP_PASSED`, it changes the state to `GP_EXIT` and queues the callback; that callback will run after a grace period and restore `GP_IDLE`. If a new exit sequence overlaps a callback already queued in `GP_EXIT`, exit marks `GP_REPLAY` so `rcu_sync_func()` requeues itself for another post-exit grace period rather than allowing readers back too early.

`rcu_sync_func()` handles three cases under lock: if writers are active (`gp_count` nonzero), it records `GP_PASSED` and wakes waiters; if it sees `GP_REPLAY`, it changes back to `GP_EXIT` and queues another callback; otherwise it marks `GP_IDLE`, allowing readers to use their fast paths. `rcu_sync_dtor()` normalizes `GP_REPLAY` to `GP_EXIT`, waits for outstanding callbacks via `rcu_barrier()` when not idle, and warns if the object fails to return idle.

## State and Persistence Behavior
The state is in-memory and embedded in the caller-owned `struct rcu_sync`. `gp_state` represents the state-machine phase, `gp_count` counts active write-side users, `gp_wait` wakes entrants waiting for the initial grace period, and `cb_head` is reused for queued RCU callbacks. No persistent storage exists. Correct lifetime requires `rcu_sync_dtor()` before freeing an object that might have a pending callback.

## Dependencies and Integration Points
The file depends on generic RCU (`synchronize_rcu()`, `call_rcu_hurry()`, `rcu_barrier()`), waitqueue locking/wakeup, spinlock IRQ-save sections, scheduler declarations, and the public `rcu_sync_is_idle()` style reader-side checks supplied by `<linux/rcu_sync.h>`. It integrates with subsystems that maintain a fast reader path but need to temporarily exclude it for updates, commonly percpu-rwsem-like and file-system or memory-management synchronization helpers.

## Risks and Edge Cases
The key risk is state-machine drift: `GP_REPLAY` exists specifically to avoid a close enter/exit pair racing with the post-exit callback and re-enabling fast readers too early. `rcu_sync_enter()` directly invokes `rcu_sync_func()` after `synchronize_rcu()`, so callback-state assumptions must remain valid even though that path is not an asynchronous RCU callback invocation. Destructor misuse while `gp_count` is nonzero or `gp_state == GP_PASSED` indicates callers are destroying an active synchronization domain. Because the callback head is embedded and reused, queuing discipline must ensure only one relevant RCU callback is pending for a given state.

## Test Signals
Tests should stress nested and concurrent `rcu_sync_enter()`/`rcu_sync_exit()` pairs, rapid enter/exit replay races, destruction with and without pending callbacks, and reader fast-path checks around each transition. Runtime signals include WARNs for impossible `gp_state` values, nonzero `gp_count` at destruction, and failure to return to `GP_IDLE` after `rcu_barrier()`. Lockdep and RCU callback debugging are useful for double-queue and lifetime issues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/rcu/sync.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/rcu/tasks.h -->
# sources/distributed-fs/ceph-client/kernel/rcu/tasks.h

## Purpose
Implements task-based RCU flavors behind conditional compilation: generic callback/grace-period machinery for Tasks RCU-like mechanisms, classic `RCU Tasks`, `RCU Tasks Rude`, and the `RCU Tasks Trace` SRCU-fast mapping. These mechanisms define grace periods in terms of task scheduling, voluntary context switches, exit handling, user/idle transitions, or forced scheduler activity rather than ordinary RCU read-side primitives. They are primarily used by tracing, BPF, and other code that modifies or observes execution paths such as function preambles and tracing hooks.

## Important APIs, Types, and Functions
The central generic types are `struct rcu_tasks_percpu`, which owns one per-CPU segmented callback list, lazy timer, urgent grace-period counter, work/irq-work wakeups, barrier marker, blocked/exiting task lists, CPU/index metadata, and backpointer; and `struct rcu_tasks`, which owns wait state, locks, grace-period state, kthread pointer, lazy settings, function pointers for flavor-specific grace-period phases, callback queue scaling controls, barrier state, names, and sequence counters. `DEFINE_RCU_TASKS()` declares a flavor-specific per-CPU array and top-level `struct rcu_tasks`.

Generic callback APIs and worker logic include `cblist_init_generic()`, `call_rcu_tasks_generic()`, `rcu_tasks_need_gpcb()`, `rcu_tasks_one_gp()`, `rcu_tasks_kthread()`, `synchronize_rcu_tasks_generic()`, `rcu_spawn_tasks_kthread_generic()`, `rcu_barrier_tasks_generic()`, `rcu_tasks_invoke_cbs()`, and `rcu_tasks_invoke_cbs_wq()`. Debug/torture support includes `set_tasks_gp_state()`, `tasks_gp_state_getname()`, `show_rcu_tasks_generic_gp_kthread()`, and `rcu_tasks_torture_stats_print_generic()`.

Classic Tasks RCU exports `call_rcu_tasks()`, `synchronize_rcu_tasks()`, `rcu_barrier_tasks()`, `show_rcu_tasks_classic_gp_kthread()`, `rcu_tasks_torture_stats_print()`, `get_rcu_tasks_gp_kthread()`, `rcu_tasks_get_gp_data()`, `exit_tasks_rcu_start()`, and `exit_tasks_rcu_finish()`. Its flavor hooks are `rcu_tasks_pregp_step()`, `rcu_tasks_pertask()`, `rcu_tasks_postscan()`, `check_all_holdout_tasks()`, and `rcu_tasks_postgp()`.

Rude Tasks RCU uses `rcu_tasks_rude_wait_gp()` with `schedule_on_each_cpu()` and exports `synchronize_rcu_tasks_rude()`, `show_rcu_tasks_rude_gp_kthread()`, `rcu_tasks_rude_torture_stats_print()`, `get_rcu_tasks_rude_gp_kthread()`, and `rcu_tasks_rude_get_gp_data()`. Trace Tasks RCU maps to `DEFINE_SRCU_FAST(rcu_tasks_trace_srcu_struct)` and exports that SRCU object when `CONFIG_TASKS_TRACE_RCU` is enabled.

## Control Flow
At early init, `tasks_cblist_init_generic()` initializes callback lists while interrupts are disabled and before multiple CPUs are online. `rcu_init_tasks_generic()` then spawns configured flavor kthreads and runs optional prove-RCU self-tests. Each flavor kthread initializes lazy timers, publishes `kthread_ptr`, waits for callback demand, runs one flavor-specific grace period when needed, invokes callbacks, and sleeps briefly to avoid tight looping.

`call_rcu_tasks_generic()` chooses a callback queue based on CPU ID and the current enqueue-shift/limit, queues the `rcu_head` on that per-CPU segmented list, marks urgent grace periods for synchronous wait callbacks or list-size thresholds, arms a lazy timer when allowed, and wakes the kthread through irq work. It can expand from a single queue to per-CPU queueing when lock contention exceeds `rcu_task_contend_lim`. `rcu_tasks_need_gpcb()` advances and accelerates callback lists, decides whether callback invocation or a grace period is needed, decrements urgent counts, and can collapse back toward CPU-0-only queueing after a grace period when callback load falls below `rcu_task_collapse_lim`.

For classic Tasks RCU, `rcu_tasks_wait_gp()` runs a hook pipeline. `rcu_tasks_pregp_step()` first calls `synchronize_rcu()` to order task state transitions. The tasklist scan calls `rcu_tasks_pertask()` for runnable non-idle tasks other than current, pins each holdout with `get_task_struct()`, snapshots `nvcsw`, sets `rcu_tasks_holdout`, and adds it to the holdout list. `rcu_tasks_postscan()` adds exiting tasks from per-CPU exit lists to cover the blind spot after tasklist removal and before the final dead schedule. The holdout loop repeatedly sleeps with backoff, calls `check_all_holdout_tasks()`, requests urgent quiescent states for holdouts, and emits stall reports. `rcu_tasks_postgp()` finishes with another `synchronize_rcu()` so scheduler-state observations and exit-path regions are ordered before grace-period completion.

`exit_tasks_rcu_start()` and `exit_tasks_rcu_finish()` bracket the fragile portion of task exit by adding/removing the current task to a per-CPU `rtp_exit_list`; `rcu_tasks_postscan()` consumes these lists. `rcu_barrier_tasks_generic()` entrains a barrier callback on each active queue and waits for its completion count, mirroring `rcu_barrier()`. The rude flavor skips tasklist scanning and instead uses `schedule_on_each_cpu()` to induce scheduler activity on all online CPUs, batching callers through the generic kthread/callback machinery.

## State and Persistence Behavior
State is kernel-resident and exists for boot lifetime. Per-flavor state includes `tasks_gp_seq`, `gp_state`, `gp_start`, `gp_jiffies`, callback queue limits, lazy timer state, urgent GP counters, barrier sequence/count/completion, and the kthread pointer. Per-task temporary state includes `rcu_tasks_holdout`, `rcu_tasks_holdout_list`, `rcu_tasks_nvcsw`, `rcu_tasks_idle_cpu`, and exit-list linkage. Callback queue scaling state persists and adapts at runtime: the system starts with a limited enqueue set, expands under contention if `rcu_task_cb_adjust` is enabled, and collapses after low-load periods and a confirming RCU grace period.

No disk persistence exists. Task references acquired during holdout scans are released when the holdout is cleared. Exit-list state is owned by the current exiting task and must be removed before the final non-preemptible exit section.

## Dependencies and Integration Points
This header is included into the RCU implementation and depends on `rcu_segcblist`, generic RCU sequencing/polling, rcuwait, kthreads, workqueues, irq work, timers, scheduler/tasklist iteration, task reference counting, `schedule_on_each_cpu()`, cpumasks, completions, lockdep, module parameters, and SRCU for the trace flavor. Integration points include tracing and BPF synchronization, function-patching/profiling hooks, task exit, nohz-full idle tracking through task fields, rcutorture status APIs, prove-RCU boot self-tests, and boot/core initcalls.

## Risks and Edge Cases
Classic Tasks RCU has a large correctness surface around task state sampling. Missing the exit-list blind spot, mishandling `nvcsw` snapshots, or misclassifying idle/offline tasks can end a grace period before a task reaches a safe state. The stall logic intentionally requests urgent quiescent states and reports holdouts, but long-running non-voluntary kernel execution can still make grace periods very long. Queue scaling is lock-sensitive: changing enqueue/dequeue limits without the RCU handoff in `percpu_dequeue_gpseq` can strand callbacks on queues no longer scanned. Lazy timers and urgent GP counters trade latency for batching and can hide progress bugs if callbacks remain non-urgent too long.

Other risks include invoking synchronous waits before scheduler activation, callback head misuse/double queueing, barrier callbacks racing with callback invocation, kthread creation failure, excessive IPIs/context switches from rude grace periods, architecture gating around `CONFIG_ARCH_WANTS_NO_INSTR`, and conditional-compile combinations where generic helpers are present but one or more flavor exports are absent.

## Test Signals
Signals include boot self-tests under `CONFIG_PROVE_RCU`, `rcutorture` Tasks/Tasks Rude/Tasks Trace scenarios, `show_rcu_tasks_*_gp_kthread()` output, `rcu_tasks_*_get_gp_data()` sequence progression, stall logs from `rcu_task_stall_timeout` and `rcu_task_stall_info`, callback count/torture stats output, task-exit stress tests that exercise `exit_tasks_rcu_start()`/`finish()`, nohz-full idle transition tests, lock contention tests that force queue expansion/collapse, barrier tests with callbacks on multiple queues, and tracing/BPF attach-detach workloads that depend on Tasks RCU grace periods.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/rcu/tasks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/rcu/tiny.c -->
# sources/distributed-fs/ceph-client/kernel/rcu/tiny.c

## Purpose
Implements Tiny RCU, the minimal uniprocessor RCU backend for small non-SMP configurations. It manages a single global callback list, advances grace-period state on quiescent states, invokes callbacks from the RCU softirq, provides synchronous and polling grace-period APIs, and initializes RCU plus generic Tasks RCU callback-list support for tiny builds.

## Important APIs, Types, and Functions
The file-local `struct rcu_ctrlblk` stores `rcucblist`, `donetail`, `curtail`, and `gp_seq`. The global instance starts with `gp_seq = 0 - 300UL` to avoid early special values. Exported APIs include `rcu_barrier()`, `rcu_qs()`, `rcu_sched_clock_irq()`, `synchronize_rcu()`, `call_rcu()`, `get_completed_synchronize_rcu_full()`, `get_state_synchronize_rcu()`, `start_poll_synchronize_rcu()`, `poll_state_synchronize_rcu()`, optional torture helpers `rcutorture_gather_gp_seqs()` and `rcutorture_format_gp_seqs()`, and `rcu_init()`. Internal helpers are `rcu_reclaim_tiny()` and `rcu_process_callbacks()`.

## Control Flow
`call_rcu()` validates the callback head with debug objects, initializes `func` and `next`, appends it to the global callback tail under local IRQ disable, and forces rescheduling if called from the idle task so a quiescent state can occur. `rcu_qs()` runs with local interrupts disabled, marks all callbacks up to `curtail` as done by moving `donetail`, raises `RCU_SOFTIRQ` when callbacks become ready, increments `gp_seq` by two, and restores interrupts. `rcu_sched_clock_irq()` reports a quiescent state on user-mode ticks and otherwise requests rescheduling when callbacks are waiting, encouraging a future quiescent state.

The softirq handler `rcu_process_callbacks()` detaches the done portion of the global callback list under local IRQ disable, repairs `rcucblist`, `donetail`, and `curtail`, then invokes callbacks one by one through `rcu_reclaim_tiny()`. `rcu_reclaim_tiny()` wraps callback invocation with RCU callback lockdep/debug tracing, clears `head->func`, and calls the callback function.

`synchronize_rcu()` checks for illegal use inside RCU read-side critical sections, disables preemption, increments `gp_seq` by two, and re-enables preemption. On uniprocessor tiny RCU, a legal caller is itself a quiescent state, so no waiting is needed. Polling APIs return and compare `gp_seq`, with `start_poll_synchronize_rcu()` also nudging the idle CPU to schedule if needed. `rcu_barrier()` delegates to `wait_rcu_gp(call_rcu_hurry)`. `rcu_init()` registers the softirq handler, runs early boot tests, and initializes generic Tasks RCU callback lists.

## State and Persistence Behavior
All state is in the single static `rcu_ctrlblk`. `rcucblist` points to queued callbacks, `curtail` points at the append location, `donetail` points at the split between pending and ready callbacks, and `gp_seq` is the grace-period/polling cookie. There is no per-CPU state beyond the assumption that only one CPU exists. State persists for the boot lifetime and is not written to disk.

## Dependencies and Integration Points
Tiny RCU depends on softirqs, local IRQ disabling, scheduler tick/quiescent-state hooks, preemption control, callback debug helpers, tracepoints, `wait_rcu_gp()`, and RCU lockdep maps. It integrates with generic RCU public APIs used by the rest of the kernel in non-SMP builds, rcutorture sequence formatting, early boot tests, and `tasks_cblist_init_generic()` for Tasks RCU support.

## Risks and Edge Cases
The implementation relies on uniprocessor assumptions; applying it to SMP would be incorrect because callback readiness and grace-period advancement are global and not per-CPU. Callback list pointer manipulation is delicate: `donetail`, `curtail`, and `rcucblist` must remain consistent when ready callbacks are detached. `call_rcu()` from idle needs a reschedule nudge or callbacks can wait indefinitely for a quiescent state. `synchronize_rcu()` is intentionally lightweight but only valid because legal calls are quiescent states on UP; lockdep warnings are the main guard against illegal read-side use. Polling cookies are simple sequence values and can wrap faster than tree RCU in tiny configurations.

## Test Signals
Relevant tests are tiny/non-SMP boot tests through `rcu_early_boot_tests()`, rcutorture tiny RCU scenarios, callback enqueue/invoke ordering tests, debug-object double-queue warnings from `call_rcu()`, lockdep warnings for illegal `synchronize_rcu()` calls, softirq execution checks for `RCU_SOFTIRQ`, idle-callback progress tests, and polling API tests that compare `get_state_synchronize_rcu()`, `start_poll_synchronize_rcu()`, and `poll_state_synchronize_rcu()` behavior across quiescent states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/rcu/tiny.c -->
