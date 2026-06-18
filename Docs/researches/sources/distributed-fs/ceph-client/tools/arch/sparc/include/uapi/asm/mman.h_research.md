# sources/distributed-fs/ceph-client/tools/arch/sparc/include/uapi/asm/mman.h

## Purpose
SPARC tools mman constant shim.

## Important APIs, Types, and Functions
Defines SPARC-specific `MAP_DENYWRITE`, `MAP_EXECUTABLE`, `MAP_GROWSDOWN`, `MAP_LOCKED`, and `MAP_NORESERVE`, includes generic common mman constants, and supplies `MAP_32BIT` as 0.

## Control Flow, State, and Persistence
No state; constants support compilation and flag decoding.

## Dependencies and Integration Points
Integrated by perf/tools and syscall trace paths for SPARC.

## Risks and Test Signals
Risk is flag-value drift or placeholder misuse. Test signals are mmap flag decode checks against SPARC UAPI.
