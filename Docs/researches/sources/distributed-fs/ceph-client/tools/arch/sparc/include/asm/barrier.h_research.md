# sources/distributed-fs/ceph-client/tools/arch/sparc/include/asm/barrier.h

## Purpose
SPARC tools barrier dispatcher.

## Important APIs, Types, and Functions
Includes `barrier_64.h` when compiling for 64-bit SPARC and `barrier_32.h` otherwise.

## Control Flow, State, and Persistence
No state; compile-time architecture macros select the implementation.

## Dependencies and Integration Points
Integrated by tools code including `<asm/barrier.h>` on SPARC.

## Risks and Test Signals
Risk is incorrect macro detection in cross builds. Test signals are sparc32 and sparc64 preprocessing/build checks.
