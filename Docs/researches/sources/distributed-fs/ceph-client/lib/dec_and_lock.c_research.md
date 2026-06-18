# sources/distributed-fs/ceph-client/lib/dec_and_lock.c

## Purpose
Provides helpers that decrement an atomic reference count and return with a lock held if the decrement reaches zero, making the decrement-to-zero and lock acquisition effectively atomic for object teardown.

## APIs, Types, and Functions
Exports `atomic_dec_and_lock()`, `_atomic_dec_and_lock_irqsave()`, `atomic_dec_and_raw_lock()`, and `_atomic_dec_and_raw_lock_irqsave()`. The APIs accept an `atomic_t *` plus either `spinlock_t *` or `raw_spinlock_t *`; irqsave variants also receive a flags pointer populated when the lock is acquired.

## Control Flow
Each helper first tries `atomic_add_unless(atomic, -1, 1)`. If the counter was not one, the decrement succeeds and the function returns `0` with no lock held. If the counter may drop to zero, it takes the relevant lock, performs `atomic_dec_and_test()`, and returns `1` with the lock held if zero was reached. If another racer changed the count, it unlocks and returns `0`.

## State and Persistence
The only persistent state mutation is the caller's atomic counter. Lock state is returned to the caller only on success; callers must release it. No global state is maintained.

## Dependencies and Integration Points
Depends on Linux atomic and spinlock APIs and is exported for refcounted object teardown paths that need a final-reference lock, such as list removal or shared object destruction.

## Risks and Test Signals
Risks include callers treating it as equivalent to `atomic_dec_and_test()` followed by locking, forgetting to unlock on a `1` return, misusing irqsave flags when the function returns `0`, and underflowing invalid counters. Test signals include refcount teardown race tests, lockdep assertions for returned lock ownership, and stress tests with concurrent put/free operations.
