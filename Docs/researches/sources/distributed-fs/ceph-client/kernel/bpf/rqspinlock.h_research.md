# sources/distributed-fs/ceph-client/kernel/bpf/rqspinlock.h

## Purpose
`rqspinlock.h` provides the small helper needed by the resilient queued spinlock slow path to update only the tail portion of a qspinlock word while preserving the current locked and pending bits. It is local support code for `rqspinlock.c`, not a general public BPF API.

## Important APIs, Types, and Functions
The header includes `../locking/qspinlock.h` and defines one inline helper, `try_cmpxchg_tail(struct qspinlock *lock, u32 tail, u32 new_tail)`. The function repeatedly reads `lock->val`, verifies that the observed `_Q_TAIL_MASK` still equals the caller's expected `tail`, combines the current `_Q_LOCKED_PENDING_MASK` bits with `new_tail`, and attempts `atomic_try_cmpxchg_relaxed()`.

## Control Flow
Callers use this helper when the queue head needs to clean up or replace the queue tail, especially during resilient timeout handling. If another waiter has already changed the tail, the helper returns `false` immediately. If only the locked/pending bits changed, the helper recomputes the new composite word and retries until the relaxed cmpxchg succeeds or the tail becomes stale.

## State and Persistence Behavior
The helper does not own state. It modifies the qspinlock's atomic 32-bit word in place. The design intentionally preserves volatile locked/pending state observed during the retry loop while replacing only the tail code.

## Dependencies and Integration Points
The helper depends on qspinlock bit layout macros such as `_Q_TAIL_MASK` and `_Q_LOCKED_PENDING_MASK`, plus Linux atomic operations. `rqspinlock.c` uses it when a timed-out MCS queue head attempts to reset the tail to zero without requiring 16-bit cmpxchg support on all architectures.

## Risks and Test Signals
The main risk is lock-word corruption if qspinlock bit masks or layout change without updating this helper. Ordering is relaxed by design and relies on the `smp_wmb()` before `xchg_tail()` and on initialized MCS node visibility, so tests should stress timeout cleanup under concurrent lock/unlock and pending-bit churn. Build coverage across architectures without 16-bit cmpxchg is also important.
