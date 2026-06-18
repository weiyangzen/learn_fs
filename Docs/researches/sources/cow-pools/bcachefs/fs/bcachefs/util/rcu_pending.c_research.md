# File Research: sources/cow-pools/bcachefs/fs/bcachefs/util/rcu_pending.c

This file implements deferred processing of objects after RCU or SRCU grace periods, using per-CPU queues, radix-backed batches, linked-list fallback, and a workqueue drain path.

Core design:
- Each CPU has `struct rcu_pending_pcpu`.
- Pending objects are grouped by grace-period poll state.
- Objects normally go into a `genradix` vector for cache-efficient batch processing.
- If allocation fails or vmalloc-backed kvfree is involved, objects fall back to linked lists.
- A single RCU callback per CPU schedules work and rearms itself while pending objects remain.

Grace-period abstraction:
- Supports normal RCU or SRCU through wrapper helpers:
  - get current state
  - start poll
  - poll completion
  - barrier
  - call RCU/SRCU

Internal data structures:
- `struct rcu_pending_seq`:
  - genradix object vector
  - count
  - cursor
  - grace-period sequence
- `struct rcu_pending_list`:
  - linked-list head/tail
  - grace-period sequence
- `struct rcu_pending_pcpu`:
  - parent pointer
  - lock
  - CPU number
  - darray of radix batches
  - fixed oldstate lists plus one expired list
  - RCU callback
  - work item

Processing:
- `merge_expired_lists()` moves completed lists into the expired list.
- `__process_finished_items()` drains completed radix batches and expired lists outside the spinlock.
- Supported processing modes include:
  - kvfree-style freeing
  - call-rcu-style callback invocation
  - caller-provided `pending->process()` callback
- `rcu_pending_work()` loops until no finished items remain.

Enqueue:
- `__rcu_pending_enqueue()`:
  - picks current CPU pending queue
  - gets current grace-period state
  - optionally processes expired items when sleeping is allowed
  - inserts into radix batch when possible
  - falls back to linked list when allocation fails
  - arms/rearms RCU callback or starts a grace period if callback is already armed
- `rcu_pending_enqueue()` is the public generic enqueue wrapper.

Dequeue:
- `rcu_pending_dequeue()` scans current CPU.
- `rcu_pending_dequeue_from_all()` scans current CPU then all CPUs.
- `rcu_pending_dequeue_where()` and `_from_all_where()` remove the first object accepted by a non-sleeping claim predicate.

Exit/init:
- `rcu_pending_exit()` waits for callbacks/work to drain, checks queues are empty, frees per-CPU state.
- `rcu_pending_init()` allocates per-CPU state, initializes locks/work, stores SRCU pointer and process callback.

Important invariants:
- Per-CPU queue state is protected by `p->lock`.
- Queue draining happens outside the lock.
- Predicate dequeue functions call `try_claim` under lock and require it not to sleep.
- Exit loops through RCU/SRCU barriers and work flushing until no queue is pending or callback is armed.

Research notes:
- This is a sophisticated batching replacement for many individual RCU callbacks.
- The code has explicit kernel/userspace compatibility branches for RCU head linkage.
