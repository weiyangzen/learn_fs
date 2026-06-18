# sources/distributed-fs/ceph-client/include/linux/kcsan.h

## Purpose
Declares the main KCSAN runtime context structure and initialization entry point. It complements `kcsan-checks.h`, which contains the public access-check macros.

## Important APIs, Types, And Functions
With `CONFIG_KCSAN`, `struct kcsan_ctx` stores disable counters, scoped-disable count, `atomic_next`, nestable atomic depth, flat atomic state, access mask, scoped access list, and optional weak-memory reorder access. `kcsan_init()` initializes runtime state. Disabled builds provide a no-op initializer.

## Control Flow
KCSAN initializes during boot, then compiler and explicit checks consult per-task or per-CPU context. Atomic and disable annotations update fields in `kcsan_ctx`, while scoped checks track active ranges in the list.

## State And Persistence
`kcsan_ctx` is per thread of execution: tasks store it in `task_struct`, and interrupts use internal per-CPU storage. The state is diagnostic runtime state and is not persistent.

## Dependencies And Integration Points
Depends on `kcsan-checks.h` and basic types. Integrates with scheduler task state, interrupt contexts, compiler instrumentation, and weak-memory race modeling.

## Risks
Incorrect context nesting can suppress or over-report races. Flat and nestable atomic regions are intentionally independent to support seqlock patterns; mixing them incorrectly in annotations can skew reports.

## Test Signals
KCSAN boot initialization, per-task context reset, interrupt-context coverage, nested atomic annotations, scoped access lists, weak-memory reorder checks, and disabled-build no-op behavior are the main signals.
