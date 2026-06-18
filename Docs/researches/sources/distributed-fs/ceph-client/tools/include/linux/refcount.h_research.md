<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/refcount.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/refcount.h

## Purpose
`refcount.h` implements a saturation-aware reference counter on top of tools `atomic_t`.

## APIs And Flow
It defines `refcount_t`, `REFCOUNT_INIT()`, `refcount_set()`, `refcount_set_release()`, `refcount_read()`, `refcount_inc_not_zero()`, `refcount_inc()`, `refcount_sub_and_test()`, and `refcount_dec_and_test()`. Increment loops use relaxed compare-exchange, reject zero, and saturate at `UINT_MAX`; decrement loops use release compare-exchange, reject saturated counters, detect underflow, and return true on transition to zero.

## State, Dependencies, Risks, Tests
State is the embedded atomic counter. Dependencies are `linux/atomic.h` and `linux/kernel.h`; warnings become `BUG_ON` unless `NDEBUG` disables them. Risks include weaker memory ordering than general atomics, saturated counters intentionally leaking objects, assertions disappearing in release builds, and callers ignoring `__must_check` decrement results. Tests should cover zero increment, saturation, underflow, normal lifecycle, concurrent increment/decrement, and debug versus `NDEBUG` behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/refcount.h -->
