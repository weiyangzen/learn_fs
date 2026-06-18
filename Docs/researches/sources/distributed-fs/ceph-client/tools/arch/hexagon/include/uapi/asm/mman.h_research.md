# sources/distributed-fs/ceph-client/tools/arch/hexagon/include/uapi/asm/mman.h

## Purpose
Hexagon tools mmap compatibility shim.

## Important APIs, Types, and Functions
Includes generic mman definitions and defines absent `MAP_32BIT` as 0.

## Control Flow, State, and Persistence
No control flow or state; it is a preprocessor normalization header.

## Dependencies and Integration Points
Used by perf/tools code that refers to common mmap flag names across architectures.

## Risks and Test Signals
Risk is confusing placeholder zero with supported Hexagon behavior. Test signals are Hexagon tools builds and flag-printing tests.
