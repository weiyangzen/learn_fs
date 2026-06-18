<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/atomic64_test.c -->
# sources/distributed-fs/ceph-client/lib/atomic64_test.c

## Purpose
Provides a load-time testsuite for `atomic_t` and `atomic64_t` operations, especially the generic 64-bit atomic implementation.

## APIs, Types, and Functions
The module defines test macros for plain, return, fetch, exchange, compare-exchange, increment, and decrement families across relaxed/acquire/release variants. Functions are `test_atomic()`, `test_atomic64()`, `test_atomics_init()`, and an empty `test_atomics_exit()`.

## Control Flow, State, and Persistence
On module init, it runs deterministic checks against known constants. Each macro initializes an atomic variable, performs an operation, calculates the expected C result, and uses `BUG_ON()` or `WARN()` when the observed value or return differs. On x86 it prints platform feature information for CX8 and SSE. There is no persistent state after init other than module load status.

## Dependencies and Integration
Depends on `linux/atomic.h`, init/module support, BUG/WARN helpers, and optional x86 CPU feature headers. Built by `lib/Makefile` when `CONFIG_ATOMIC64_SELFTEST` is set.

## Risks and Test Signals
Risks include tests being destructive because `BUG_ON()` can crash a system, limited coverage of concurrency and memory ordering, and architecture-specific feature print assumptions. Its own pass/fail output is the primary signal; additional useful signals are running under generic atomic64 configs, native atomic64 architectures, SMP stress, KCSAN, and lockdep.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/atomic64_test.c -->
