# sources/distributed-fs/ceph-client/kernel/locking/mcs_spinlock.h research

## Purpose
`mcs_spinlock.h` implements the generic Mellor-Crummey and Scott queue spinlock helper used by kernel locking code that needs fair handoff and local spinning. Instead of all waiters spinning on a shared word, each waiter enqueues a per-call node and spins on its own `node->locked` field, reducing cacheline bouncing under contention.

## Important APIs, Types, and Functions
The header includes `asm/mcs_spinlock.h`, which supplies `struct mcs_spinlock` and may override architecture-specific waiting/wakeup macros. If not overridden, `arch_mcs_spin_lock_contended(l)` uses `smp_cond_load_acquire(l, VAL)` to wait with acquire semantics, and `arch_mcs_spin_unlock_contended(l)` uses `smp_store_release(l, 1)` to hand the lock to the next waiter.

The public inline functions are `mcs_spin_lock(struct mcs_spinlock **lock, struct mcs_spinlock *node)` and `mcs_spin_unlock(struct mcs_spinlock **lock, struct mcs_spinlock *node)`. The caller owns the node lifetime and must pass the same node to unlock that was used to lock.

## Control Flow
`mcs_spin_lock()` initializes the caller's node, atomically exchanges the queue tail with the node, and returns immediately if there was no predecessor. If there was a predecessor, it stores itself in `prev->next` and waits until the predecessor sets `node->locked`.

`mcs_spin_unlock()` first reads `node->next`. If no successor is visible, it attempts `cmpxchg_release(lock, node, NULL)` to release an uncontended or not-yet-linked tail. If the compare-exchange fails, a successor has enqueued but not yet linked itself into `node->next`, so unlock waits until `next` appears. It then wakes the successor by storing release to `next->locked`.

## State and Persistence Behavior
The lock state is the shared tail pointer plus transient per-waiter nodes. The header does not allocate memory or maintain global state. Correctness depends on the caller keeping each node stable while queued and not reusing it until after unlock. The comments explicitly note that the acquire/release pair is not a full cross-CPU memory barrier on all architectures; callers that require a full barrier after unlock-lock pairing must use `smp_mb__after_unlock_lock()` after lock acquisition.

## Dependencies and Integration Points
This header depends on architecture definitions for `struct mcs_spinlock` and optional arch hooks. It uses atomic exchange, compare-exchange release, `READ_ONCE`, `WRITE_ONCE`, `cpu_relax`, and SMP acquire/release primitives. Queue spinlock implementations and other scalable locking algorithms can build on these helpers.

## Risks and Edge Cases
Passing a non-local or reused node can corrupt the queue. Unlocking with a different node than was used for acquisition can leave waiters stuck. The small handoff race where a successor is tail-visible but has not set `prev->next` is handled by the wait loop in unlock; removing that loop would lose wakeups. Architecture overrides must preserve acquire/release semantics and should not introduce pure busy waiting where the architecture expects wait instructions.

## Test Signals
Stress tests should show FIFO handoff under contention and no shared-cacheline storm comparable to test-and-set locks. Memory-ordering tests should cover critical-section visibility, and architecture lock tests should include the race where unlock observes no `next` but `cmpxchg_release()` fails.
