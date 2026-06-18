# sources/distributed-fs/ceph-client/kernel/rcu/rcu.h

## Purpose
`kernel/rcu/rcu.h` is an internal shared header for RCU implementations. It provides grace-period sequence arithmetic, debug-object hooks for `rcu_head`, stall suppression/ftrace dump helpers, RCU tree geometry iteration, ordered rcu_node locking wrappers, and declarations/stubs shared across tiny, tree, SRCU, tasks, torture, lazy, and NOCB paths.

## Important APIs, types, and functions
Sequence helpers include `rcu_seq_ctr()`, `rcu_seq_state()`, `rcu_seq_set_state()`, `rcu_seq_start()`, `rcu_seq_endval()`, `rcu_seq_end()`, `rcu_seq_snap()`, `rcu_seq_current()`, `rcu_seq_started()`, `rcu_seq_done()`, `rcu_seq_done_exact()`, `rcu_seq_completed_gp()`, `rcu_seq_new_gp()`, and `rcu_seq_diff()`. Debug helpers include `debug_rcu_head_queue()`, `debug_rcu_head_unqueue()`, `debug_rcu_head_callback()`, and `rcu_barrier_cb_is_done()`. Tree helpers include `rcu_init_levelspread()`, node iteration macros, and raw spinlock wrappers ending in `_rcu_node`.

## Control flow
Grace-period updaters call `rcu_seq_start()` before a GP and `rcu_seq_end()` afterward; waiters take snapshots with `rcu_seq_snap()` and poll for completion. Tree RCU code uses breadth-first and leaf iteration macros to traverse `rcu_state.node[]`. Tree-level locking must go through wrappers that add `smp_mb__after_unlock_lock()` to preserve ordering while moving across different node locks.

## State and persistence behavior
The header manipulates sequence counters whose low bits encode state and high bits encode completed grace periods. It references global RCU state such as fanout settings, stall controls, GP kthreads, lazy callback timing, torture data, and CPU-online tracking, but does not allocate state itself.

## Dependencies and integration points
It depends on trace events, slab/debug objects, RCU node tree definitions, ftrace, lockdep, tiny/tree configuration, tasks RCU, SRCU, NOCB, lazy RCU, torture, and architecture support for context tracking and CPU rescheduling.

## Risks and invariants
Sequence arithmetic must handle wraparound and state-bit masking. `rcu_seq_done_exact()` intentionally avoids the broad ULONG guard band for full polling APIs because root and global GP sequences can lag. rcu_node lock wrappers are required for transitive ordering across the tree; bypassing them can break GP visibility. Debug-object hooks must stay cheap or compiled out when disabled.

## Test signals
RCU torture, SRCU torture, tasks-RCU torture, stall warning tests, polled GP API tests, KCSAN/lockdep, tiny/tree build matrices, and wraparound simulation via torture controls are the best coverage.
