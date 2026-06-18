# sources/distributed-fs/ceph-client/drivers/misc/lkdtm/refcount.c

## Purpose
`refcount.c` exercises `refcount_t` hardening behavior across overflow, zero, underflow, saturated-value operations, and performance comparison with `atomic_t`.

## Important APIs, Types, and Functions
Helper checkers are `overflow_check()`, `check_zero()`, `check_negative()`, `check_from_zero()`, and `check_saturated()`. Crashtypes cover `refcount_inc/add/inc_not_zero/add_not_zero`, `dec`, `dec_and_test`, `sub_and_test`, saturated cases, and timing tests `lkdtm_ATOMIC_TIMING()` and `lkdtm_REFCOUNT_TIMING()`.

## Control Flow
Each test initializes a local `refcount_t` at a boundary value, performs a known-good operation when useful, then performs the bad operation and checks whether the counter saturated, stayed pinned, reset unsafely, or wrapped. Timing tests run large increment/decrement loops and verify the terminal count.

## State and Persistence
All tested counters are local stack variables. No persistent state is used.

## Dependencies and Integration Points
Uses `<linux/refcount.h>`, `REFCOUNT_MAX`, `REFCOUNT_SATURATED`, and LKDTM category registration. Timing examples can be driven through debugfs and `perf stat`.

## Risks
These tests assume kernel `refcount_t` semantics and warn/fail around alternatives. Timing tests intentionally run very long loops. Some behaviors allow more than one acceptable protected outcome, such as saturation or zero pinning.

## Test Signals
Signals include saturation on overflow/underflow, no increment from zero through protected APIs, no movement from saturated values, warnings rather than wraparound, and timing tests ending with synchronized up/down cycles.
