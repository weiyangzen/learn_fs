# sources/distributed-fs/ceph-client/include/linux/kcsan-checks.h

## Purpose
Defines explicit Kernel Concurrency Sanitizer access checks, barrier instrumentation hooks, atomic-region annotations, scoped access assertions, and race-property assertion macros.

## Important APIs, Types, And Functions
Access flags include `KCSAN_ACCESS_WRITE`, `COMPOUND`, `ATOMIC`, `ASSERT`, and `SCOPED`. Runtime APIs include `__kcsan_check_access()`, barrier hooks, current-context disable/enable, nestable and flat atomic region markers, `kcsan_atomic_next()`, `kcsan_set_access_mask()`, `struct kcsan_scoped_access`, `kcsan_begin_scoped_access()`, and `kcsan_end_scoped_access()`. Public macros include read/write/read-write checks, atomic checks, and `ASSERT_EXCLUSIVE_WRITER`, scoped variants, `ASSERT_EXCLUSIVE_ACCESS`, and `ASSERT_EXCLUSIVE_BITS`.

## Control Flow
When KCSAN is enabled, explicit checks call the runtime; otherwise they are no-ops. When the current compilation unit has `__SANITIZE_THREAD__`, `kcsan_check_access` maps to the runtime; otherwise header-safe checks are no-ops. Weak-memory barrier instrumentation either emits intercepted atomic signal fences or calls explicit hooks, depending on compiler instrumentation configuration.

## State And Persistence
State is maintained in per-context KCSAN runtime data, including disable counts, atomic-region state, access masks, and scoped access lists. It is diagnostic and non-persistent.

## Dependencies And Integration Points
Depends only on compiler attributes and basic types to keep it includable from low-level headers. Integrates with compiler thread sanitizer instrumentation, LKMM barrier modeling, lockless algorithms, seqlocks, and assertion-heavy concurrency tests.

## Risks
Assertions are diagnostic and do not synchronize memory. Overusing disable or atomic annotations can hide real races. Scoped access cleanup relies on compiler cleanup attributes. Barrier mappings are explicitly arbitrary sanitizer signals, not real C11 memory-order semantics.

## Test Signals
Signals include KCSAN selftests, intentional data race reports, assertion violation reports, scoped cleanup coverage, weak-memory barrier instrumentation, builds with and without `__SANITIZE_THREAD__`, and `CONFIG_KCSAN_IGNORE_ATOMICS` behavior.
