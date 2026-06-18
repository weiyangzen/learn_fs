<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/Makefile -->
# sources/distributed-fs/ceph-client/arch/powerpc/mm/Makefile

## Purpose
This Makefile selects the architecture-specific PowerPC memory-management objects.

## Important APIs, types, and functions
The base `obj-y` list builds faults, memory init, page tables, access helpers, page attributes, ioremap, context, DRMEM, and cache flush support. Conditional directories include `nohash/`, `book3s32/`, `book3s64/`, `ptdump/`, and `kasan/`.

## Control flow
Kbuild adds objects by `BITS` and feature configs such as `CONFIG_PPC_MMU_NOHASH`, `CONFIG_PPC_BOOK3S_32`, `CONFIG_PPC_BOOK3S_64`, NUMA, hugetlb, noncoherent cache, coprocessor base, PTDUMP, and KASAN.

## State and persistence behavior
No runtime state exists; it controls build composition.

## Dependencies and integration points
It is the top-level PowerPC MM build integration point under `arch/powerpc/mm`.

## Risks and edge cases
Incorrect conditional selection can omit platform-critical MMU code or include incompatible hash/nohash implementations.

## Test signals
Build matrix success across 32/64-bit, Book3S, nohash, KASAN, NUMA, and hugetlb configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/Makefile -->
