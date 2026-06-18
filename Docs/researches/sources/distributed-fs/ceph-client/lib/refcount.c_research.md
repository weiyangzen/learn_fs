## sources/distributed-fs/ceph-client/lib/refcount.c

Purpose: out-of-line helpers for hardened `refcount_t` operations that cannot or should not be implemented only as inline atomic wrappers.

Important APIs/functions: `refcount_warn_saturate()` sets the counter to `REFCOUNT_SATURATED` and emits a warning based on saturation type. `refcount_dec_if_one()` performs a release-ordered 1-to-0 transition. `refcount_dec_not_one()` decrements unless the value is 1. `refcount_dec_and_mutex_lock()`, `refcount_dec_and_lock()`, and `refcount_dec_and_lock_irqsave()` acquire the supplied lock only when successfully dropping the last reference.

Control flow: decrement-and-lock helpers first try to decrement non-final references without taking the external lock. If the count is exactly one, they acquire the lock, call `refcount_dec_and_test()`, and release the lock if another reference appeared. Underflow and saturated states warn or behave as leak-preserving safety cases.

State and persistence: state is the caller-owned `refcount_t`; no globals. Saturation deliberately persists to prevent wraparound and likely leaks the object.

Dependencies/integration: depends on mutexes, spinlocks, atomics, and warning infrastructure. Used by kernel objects that need refcount hardening and final-release locking.

Risks/test signals: misuse after count zero reports use-after-free style warnings. Saturation warnings indicate a serious lifetime bug. Memory ordering is release plus control dependency for destruction sequencing.
