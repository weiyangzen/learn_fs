# sources/distributed-fs/ceph-client/include/linux/kmsan_string.h

## Purpose

`kmsan_string.h` centralizes prototypes for KMSAN-provided string/memory routines. It exists so headers that need the MSan function names do not duplicate declarations. The source was read as a complete 21-line file.

## Important APIs, Types, and Functions

The header declares `__msan_memcpy()`, `__msan_memset()`, and `__msan_memmove()`.

## Control Flow

There is no local flow. Instrumented or overridden string operations call into these routines to update both data and KMSAN metadata consistently.

## State and Persistence Behavior

No state is owned here. The declared routines affect KMSAN shadow/origin metadata at runtime.

## Dependencies and Integration Points

It integrates with KMSAN instrumentation and generic string operation declarations. Consumers include headers or C files that must refer to MSan-backed copy/fill/move functions.

## Risks and Edge Cases

Prototype drift from the actual KMSAN runtime implementation would cause build or ABI mismatches. Callers must pass correct byte lengths because metadata propagation follows the requested size.

## Test Signals

KMSAN string operation tests, build coverage for headers that include this file, and metadata propagation checks for memcpy/memset/memmove are useful.
