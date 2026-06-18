# sources/distributed-fs/ceph-client/tools/arch/sh/include/uapi/asm/mman.h

## Purpose
SH tools mmap compatibility wrapper.

## Important APIs, Types, and Functions
Includes generic mman definitions and defines missing `MAP_32BIT` as 0.

## Control Flow, State, and Persistence
No runtime behavior.

## Dependencies and Integration Points
Integrated with perf/tools mmap flag handling.

## Risks and Test Signals
Risk is placeholder misuse. Test signals are SH tools builds and flag decode checks.
