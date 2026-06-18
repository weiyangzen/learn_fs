<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/32/pgalloc.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/32/pgalloc.h

## Purpose
This header supplies 32-bit nohash page-table allocation glue for the effectively two-level PowerPC layout, where PMD allocation is folded away and PMD entries point at PTE storage.

## Important APIs, Types, And Functions
`pmd_free()` and `__pmd_free_tlb()` are no-ops because no real separately allocated PMD pages exist. `pmd_populate_kernel()` and `pmd_populate()` encode a PTE table pointer into the PMD, using a kernel virtual address on BookE and a physical address on non-BookE, with `_PMD_PRESENT` and optionally `_PMD_USER`.

## Control Flow
Generic memory-management code calls these helpers while constructing page tables. The only branch is the BookE/non-BookE address encoding decision.

## State And Persistence Behavior
No state is owned here. The helpers persist encoded PTE-table addresses in the caller's PMD/PGD slot until the mapping is cleared or the containing page table is freed by upper-layer code.

## Dependencies And Integration Points
It depends on `linux/threads.h`, `linux/slab.h`, `__pa()`, and platform `_PMD_*` masks from the selected nohash PTE header. It is included through `asm/nohash/pgalloc.h`.

## Risks And Edge Cases
Using physical addresses on BookE or virtual addresses on non-BookE would break TLB-miss tablewalks. `_PMD_USER` matters for user PTE pages on non-BookE. The no-op free helpers rely on the folded layout remaining true.

## Test Signals
Cross-build 32-bit nohash BookE and non-BookE configs, fault user and kernel pages, unmap ranges under TLB gather, and validate PMD contents with debug page-table checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/32/pgalloc.h -->
