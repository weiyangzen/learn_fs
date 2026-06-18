# File Research: sources/cow-pools/bcachefs-tools/fs/util/rcu_pending.h

Purpose: Public declarations for the RCU-pending batching facility.

Key APIs and behavior:
- `struct rcu_pending` stores per-CPU state, optional SRCU domain, and process callback.
- Declares enqueue, dequeue, dequeue-from-all, predicate dequeue, init, and exit functions.
- `rcu_pending_process_fn` receives the parent pending queue and object `rcu_head`.

Integration:
- Implemented by `rcu_pending.c`.
- Includes `<linux/rcupdate.h>` and forward-declares per-CPU internals.

Risks and invariants:
- Callers must initialize with `rcu_pending_init()` and drain with `rcu_pending_exit()`.
- Predicate callbacks run with internal queue lock held and must not sleep.
