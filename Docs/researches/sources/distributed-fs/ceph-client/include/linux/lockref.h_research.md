<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/lockref.h -->
# sources/distributed-fs/ceph-client/include/linux/lockref.h

## Purpose
This header defines `struct lockref`, a combined spinlock and reference count optimized for objects that frequently need atomic refcount updates with fallback locking.

## Important APIs, Types, and Functions
`struct lockref` contains a `union` of `aligned_u64 lock_count` for cmpxchg-capable platforms and a struct with `spinlock_t lock` plus `int count`. APIs include `lockref_init`, `lockref_get`, `lockref_put_return`, `lockref_get_not_zero`, `lockref_put_or_lock`, `lockref_mark_dead`, `lockref_get_not_dead`, and `__lockref_is_dead`.

## Control Flow
Fast paths may use cmpxchg on the combined lock/count word when alignment and architecture support allow it. Slow paths take the embedded spinlock to update count or hold the object while final put processing runs.

## State and Persistence Behavior
State is the object's embedded lock and reference count. A negative count marks a dead object. No persistence exists beyond object lifetime.

## Dependencies and Integration Points
It depends on spinlocks and generated bounds for alignment/size checks. It integrates with dcache and other reference-counted kernel objects that need lock-coupled lifetime transitions.

## Risks and Test Signals
Risks include count underflow, resurrecting dead objects, alignment assumptions for cmpxchg, and missed locking around object teardown. Test signals are refcount stress, lockdep on fallback locks, dcache lifetime tests, and KASAN/UAF detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/lockref.h -->
