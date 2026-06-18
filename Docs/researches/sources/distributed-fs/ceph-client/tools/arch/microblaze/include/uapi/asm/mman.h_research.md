# sources/distributed-fs/ceph-client/tools/arch/microblaze/include/uapi/asm/mman.h

## Purpose
MicroBlaze tools mmap compatibility wrapper.

## Important APIs, Types, and Functions
Includes generic mman definitions and supplies `MAP_32BIT` as 0.

## Control Flow, State, and Persistence
No state or control flow.

## Dependencies and Integration Points
Used by perf/tools cross-architecture code.

## Risks and Test Signals
Risk is placeholder constants hiding architecture-specific gaps. Test signals are MicroBlaze tools builds and mmap flag decode checks.
