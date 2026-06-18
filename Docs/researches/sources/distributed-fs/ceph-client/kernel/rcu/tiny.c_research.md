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
