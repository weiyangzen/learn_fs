# sources/distributed-fs/ceph-client/include/linux/refcount.h

## Purpose

`refcount.h` defines the kernel's saturating reference-count API. It provides a safer subset of atomic operations for object lifetimes, preventing overflow wraparound into use-after-free and warning on underflow, zero-to-nonzero increments, and leak-prone decrements.

## Important APIs, Types, and Functions

The type is `refcount_t` from `refcount_types.h`. Constants include `REFCOUNT_INIT(n)`, `REFCOUNT_MAX`, and `REFCOUNT_SATURATED`. Saturation warning reasons are enumerated by `enum refcount_saturation_type`, reported through `refcount_warn_saturate()`.

Set/read APIs are `refcount_set()`, `refcount_set_release()`, and `refcount_read()`. Increment/add APIs include `refcount_add_not_zero()`, `refcount_add_not_zero_acquire()`, `refcount_add()`, `refcount_inc_not_zero()`, `refcount_inc_not_zero_acquire()`, and `refcount_inc()`, plus internal variants that return the old value.

Decrement APIs include `refcount_sub_and_test()`, `refcount_dec_and_test()`, and `refcount_dec()`. External helpers handle lock-coupled final drops: `refcount_dec_if_one()`, `refcount_dec_not_one()`, `refcount_dec_and_mutex_lock()`, `refcount_dec_and_lock()`, and `refcount_dec_and_lock_irqsave()`.

## Control Flow

Not-zero add/inc operations use `atomic_try_cmpxchg_*()` loops to avoid acquiring references from zero. Plain add/inc use relaxed fetch-add then warn and saturate on zero or overflow. Decrement-and-test uses release fetch-sub and, on the one-to-zero transition, an acquire barrier via `smp_acquire__after_ctrl_dep()` before returning true to allow object free.

`refcount_dec()` is for cases where zero is not expected; if the old value is one or less it warns and saturates/leaks instead of allowing underflow. Acquire variants are intended for reused memory such as `SLAB_TYPESAFE_BY_RCU` where secondary validation must happen after the refcount is taken.

## State and Persistence Behavior

State is a single `atomic_t refs` in each object. Counters can become saturated at `REFCOUNT_SATURATED` and stay there, intentionally leaking the object rather than risking wraparound. There is no persistent state outside object lifetime.

## Dependencies and Integration Points

The header depends on atomic operations, compiler annotations, limits, spinlock and mutex types, and `refcount_types.h`. It is a common primitive for kernel object lifetimes, RCU-safe lookup patterns, lock-coupled deletion, and driver resource management.

## Risks

Using `refcount_inc()` on a possibly zero counter is a use-after-free bug and triggers warnings. Using relaxed increments without an external lifetime guarantee can expose stale object state. Misusing `refcount_dec()` when final free is expected causes warnings/leaks; final-release callers need `refcount_dec_and_test()` or lock-coupled helpers. Large batched adds can stress the saturation safety assumptions.

## Test Signals

Tests should cover normal inc/dec lifecycles, zero-to-nonzero attempts, overflow saturation, underflow saturation, acquire/release ordering under `SLAB_TYPESAFE_BY_RCU`, and lock helper behavior with mutex/spinlock final drops. KUnit or LKDTM-style tests can assert warnings and leak protection.
