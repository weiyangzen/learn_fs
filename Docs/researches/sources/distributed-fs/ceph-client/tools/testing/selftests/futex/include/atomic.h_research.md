<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/futex/include/atomic.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/futex/include/atomic.h

## Purpose
This header provides minimal GCC atomic builtin wrappers for futex tests.

## Important APIs, Types, And Functions
It defines `atomic_t` with volatile `int val`, `ATOMIC_INITIALIZER`, and inline functions `atomic_cmpxchg()`, `atomic_inc()`, `atomic_dec()`, and `atomic_set()`.

## Control Flow
Each wrapper directly calls a GCC `__sync_*` builtin or assigns the value for `atomic_set()`.

## State And Persistence
It has no state of its own; callers mutate `atomic_t` objects.

## Dependencies And Integration Points
It is used by PI requeue tests to coordinate waiter counters and flags without pulling in kernel atomic APIs.

## Risks
`atomic_set()` is a plain volatile assignment, not a full barrier. The wrappers are legacy `__sync` builtins rather than C11 atomics.

## Test Signals
Tests using waiter counters should not observe torn or lost increments/decrements under normal pthread concurrency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/futex/include/atomic.h -->
