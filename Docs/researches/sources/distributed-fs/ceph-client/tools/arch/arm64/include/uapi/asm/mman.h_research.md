# sources/distributed-fs/ceph-client/tools/arch/arm64/include/uapi/asm/mman.h

## Purpose
Perf/tools compatibility wrapper for arm64 memory-management constants.

## Important APIs, Types, and Functions
Includes `uapi/asm-generic/mman.h` and defines missing `MAP_32BIT` as 0 because arm64 does not implement that x86-specific mapping flag.

## Control Flow, State, and Persistence
No runtime behavior. It normalizes preprocessing so generic tools code can reference `MAP_32BIT` unconditionally.

## Dependencies and Integration Points
Integrated by tools/perf and other copied UAPI users that expect a common mmap constant set.

## Risks and Test Signals
Risk is treating zero as a real supported flag rather than a harmless no-op placeholder. Test signals are cross-architecture tools builds and mmap flag formatting tests.
