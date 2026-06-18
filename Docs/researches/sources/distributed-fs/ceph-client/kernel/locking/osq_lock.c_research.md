# sources/distributed-fs/ceph-client/kernel/locking/osq_lock.c

## Purpose
Implements the optimistic spin queue used by sleeping locks such as mutexes and rwsems to serialize spinners. It is an MCS-like per-CPU queue that lets only one active spinner contend on the real lock while allowing cancellation when the task needs rescheduling or detects a preempted predecessor.

## Important APIs, Types, and Functions
- `struct optimistic_spin_node` stores `next`, `prev`, `locked`, and encoded CPU id.
- `osq_lock()` enqueues the current CPU and returns true when it acquired the queue or false when it canceled.
- `osq_unlock()` passes the queue token to the next node or clears the tail.
- `osq_wait_next()` stabilizes the next pointer during unlock or unqueue.

## Control Flow
`osq_lock()` initializes the per-CPU node, swaps it into `lock->tail`, and succeeds immediately when the queue was empty. Otherwise it links behind the predecessor and waits on `node->locked` until either the predecessor unlocks or cancellation conditions hold. Cancellation unlinks the node in three steps: detach from `prev->next`, stabilize `next` or tail, then reconnect `prev` and `next`. `osq_unlock()` clears the tail in the uncontended case, otherwise wakes the recorded next node or waits until it can identify one.

## State and Persistence
State is per-CPU static `osq_node` plus the queue tail in `struct optimistic_spin_queue`. It is volatile synchronization state only; no disk persistence.

## Dependencies and Integration Points
Used by mutex and rwsem optimistic spinning. Depends on per-CPU APIs, scheduler `need_resched()`, `vcpu_is_preempted()`, SMP atomics, and memory barriers.

## Risks
The unlink protocol is race-prone: predecessor and successor nodes are static per CPU, but their pointers must be cleared and reconnected in exact order to avoid stale links. This code assumes sleeping locks do not use OSQ from interrupt context and that preemption is disabled while spinning.

## Test Signals
Signals include lock contention stress under `CONFIG_MUTEX_SPIN_ON_OWNER` and `CONFIG_RWSEM_SPIN_ON_OWNER`, preemption/virtualization stress that triggers cancellation, and lockup detection from queue corruption or missed handoff.
