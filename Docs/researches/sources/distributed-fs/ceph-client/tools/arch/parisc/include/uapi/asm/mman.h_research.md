# sources/distributed-fs/ceph-client/tools/arch/parisc/include/uapi/asm/mman.h

## Purpose
PARISC mmap/madvise constants for tools.

## Important APIs, Types, and Functions
Defines target-specific `MADV_*`, `MAP_*`, and `PROT_*` values, including `MAP_VARIABLE`, `MAP_HUGETLB`, grow-up/down protections, and compatibility `MAP_32BIT` as 0.

## Control Flow, State, and Persistence
No state; constants drive decoding and compilation.

## Dependencies and Integration Points
Integrated with perf and syscall trace tooling for PARISC.

## Risks and Test Signals
Risk is flag-number drift or missing generic flags because this file does not include the full generic mman header. Test signals are mmap flag decode tests against PARISC UAPI.
