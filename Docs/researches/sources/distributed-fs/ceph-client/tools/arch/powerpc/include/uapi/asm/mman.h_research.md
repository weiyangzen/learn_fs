# sources/distributed-fs/ceph-client/tools/arch/powerpc/include/uapi/asm/mman.h

## Purpose
PowerPC tools mman constant shim.

## Important APIs, Types, and Functions
Defines target-specific `MAP_DENYWRITE`, `MAP_EXECUTABLE`, `MAP_GROWSDOWN`, `MAP_LOCKED`, `MAP_NORESERVE`, includes generic common mman constants, and supplies missing `MAP_32BIT` as 0.

## Control Flow, State, and Persistence
No runtime state; constants are compile-time ABI values.

## Dependencies and Integration Points
Integrated with perf and syscall tracing for PowerPC.

## Risks and Test Signals
Risk is flag-value drift or treating `MAP_32BIT` as supported. Test signals are flag decode checks against PowerPC UAPI.
