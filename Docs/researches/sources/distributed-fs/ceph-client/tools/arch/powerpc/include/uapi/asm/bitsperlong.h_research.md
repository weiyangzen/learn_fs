# sources/distributed-fs/ceph-client/tools/arch/powerpc/include/uapi/asm/bitsperlong.h

## Purpose
PowerPC UAPI word-size selector for tools.

## Important APIs, Types, and Functions
Includes generic bits-per-long definitions; architecture selection is left to the generic/compiler environment.

## Control Flow, State, and Persistence
No runtime flow.

## Dependencies and Integration Points
Integrated by copied PowerPC UAPI headers and tools.

## Risks and Test Signals
Risk is relying on generic behavior across 32/64-bit ABI modes. Test signals are ppc32 and ppc64 preprocessing/build coverage.
