# sources/distributed-fs/ceph-client/tools/arch/mips/include/uapi/asm/mman.h

## Purpose
MIPS tools mmap/madvise constant shim.

## Important APIs, Types, and Functions
Defines MIPS-specific `MADV_*`, `MAP_*`, and `PROT_*` values plus missing perf compatibility placeholders `MADV_SOFT_OFFLINE`, `MAP_32BIT`, and `MAP_UNINITIALIZED`.

## Control Flow, State, and Persistence
No runtime flow; constants are consumed by tools when decoding mmap flags or compiling common code.

## Dependencies and Integration Points
Integrated with perf and syscall tracing for MIPS target semantics.

## Risks and Test Signals
Risk is value drift from MIPS UAPI or accidentally treating compatibility zeros as supported target flags. Test signals are mmap flag formatting tests and cross-checks against kernel UAPI.
