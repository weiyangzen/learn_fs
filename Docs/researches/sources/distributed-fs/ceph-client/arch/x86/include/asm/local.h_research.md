# sources/distributed-fs/ceph-client/arch/x86/include/asm/local.h

## Purpose
Implements x86 `local_t`, a per-CPU/local counter API backed by `atomic_long_t` but using non-lock-prefixed instructions where safe.

## Important APIs, Types, And Functions
Defines `local_t`, `LOCAL_INIT()`, `local_read()`, `local_set()`, `local_inc()`, `local_dec()`, `local_add()`, `local_sub()`, condition helpers such as `local_sub_and_test()`, `local_add_negative()`, return-value helpers, `local_cmpxchg()`, `local_try_cmpxchg()`, `local_xchg()`, `local_add_unless()`, and `local_inc_not_zero()`. The `__local_*` macros alias the same operations.

## Control Flow
Simple add/sub/inc/dec emit inline x86 arithmetic on memory. Tests use `GEN_*_RMWcc` helpers to derive flags. Return-value add uses `xadd`, while exchange and add-unless loop with local compare-exchange until successful or blocked by the sentinel value.

## State And Persistence
State is the counter value in memory, generally used for CPU-local data. It is not globally synchronized unless callers enforce locality or locking.

## Dependencies And Integration Points
Depends on Linux per-CPU and atomic APIs plus x86 asm helper macros. It integrates with generic local counter users and x86 optimized atomic primitives.

## Risks And Edge Cases
These are not a replacement for inter-CPU atomic operations. Misusing them on shared data can race. `local_xchg()` intentionally avoids locked `xchg` for performance, so correctness relies on locality.

## Test Signals
Atomic/local API compile tests, lockless counter stress tests under preemption-disabled use, and x86-32/x86-64 build coverage provide signal.
