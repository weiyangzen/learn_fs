# File Research: sources/cow-pools/bcachefs/fs/bcachefs/util/rcu_pending.h

This header exposes the `rcu_pending` deferred-processing API.

Types:
- `rcu_pending_process_fn`: callback invoked with the pending object and an `rcu_head`.
- `struct rcu_pending`:
  - per-CPU state pointer
  - optional SRCU struct
  - process callback

Public functions:
- Enqueue:
  - `rcu_pending_enqueue()`
- Dequeue:
  - `rcu_pending_dequeue()`
  - `rcu_pending_dequeue_from_all()`
  - `rcu_pending_dequeue_where()`
  - `rcu_pending_dequeue_from_all_where()`
- Lifecycle:
  - `rcu_pending_exit()`
  - `rcu_pending_init()`

Important behavior:
- Passing an SRCU pointer switches the implementation from RCU to SRCU grace periods.
- Dequeue-where predicates are used to claim only selected pending objects.

Research notes:
- The header hides batching and grace-period mechanics from users; callers see a deferred-processing queue keyed by RCU completion.
