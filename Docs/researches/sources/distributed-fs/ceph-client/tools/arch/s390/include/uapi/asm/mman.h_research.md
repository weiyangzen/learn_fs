# sources/distributed-fs/ceph-client/tools/arch/s390/include/uapi/asm/mman.h

## Purpose
s390 tools mmap compatibility wrapper.

## Important APIs, Types, and Functions
Includes generic mman definitions and defines missing `MAP_32BIT` as 0.

## Control Flow, State, and Persistence
No state; preprocessor-only normalization.

## Dependencies and Integration Points
Integrated with perf/tools common mmap flag code.

## Risks and Test Signals
Risk is treating zero as an actual s390 flag. Test signals are s390 tools build and flag decode tests.
