# sources/distributed-fs/ceph-client/tools/arch/xtensa/include/uapi/asm/mman.h

## Purpose
Defines Xtensa mmap, mprotect, and madvise constants needed by tools, including compatibility definitions for constants missing on Xtensa.

## APIs, Types, and Functions
Exports `MADV_*`, `MAP_*`, and `PROT_*` constants, plus compatibility values for `MADV_HWPOISON`, `MADV_SOFT_OFFLINE`, `MAP_32BIT`, and `MAP_UNINITIALIZED`.

## Control Flow, State, and Persistence
No runtime behavior. Constants are preprocessor ABI values consumed at compile time.

## Dependencies and Integration
Used by perf and other tools that need Linux memory-management constants on Xtensa without relying on architecture-incomplete system headers.

## Risks and Test Signals
Risks include mismatch with kernel UAPI values, assigning dummy zero values where code expects a functional flag, and missing future constants. Test signals are Xtensa tool cross-builds and mmap/madvise feature probes that tolerate unsupported compatibility flags.
