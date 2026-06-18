<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/64/pgtable-4k.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/64/pgtable-4k.h

## Purpose
This header defines 4K-page 64-bit nohash page-table geometry, folded P4D behavior, and P4D accessors.

## Important APIs, Types, And Functions
It includes `asm-generic/pgtable-nop4d.h`, defines PTE/PMD/PUD/PGD index sizes, table sizes, `PTRS_PER_*`, `PMD_SHIFT`, `PUD_SHIFT`, `PGDIR_SHIFT`, masks, `p4d_none()`, `p4d_bad()`, `p4d_present()`, `p4d_pgtable()`, `p4d_clear()`, `p4d_pte()`, `pte_p4d()`, `p4d_page()`, `pud_ERROR()`, and `remap_4k_pfn()`.

## Control Flow
There is no independent runtime flow. Page-table walking and mapping code use the accessors to traverse from folded P4D to PUD and to remap individual 4K PFNs through generic `remap_pfn_range()`.

## State And Persistence Behavior
The header defines how P4D entries store child table addresses. It does not own state, but its geometry determines all 64-bit nohash page-table allocation sizes and address coverage.

## Dependencies And Integration Points
It is included by `nohash/64/pgtable.h` and depends on generic folded-level definitions and the page-table type definitions selected earlier.

## Risks And Edge Cases
Index-size changes alter the virtual address range and slab cache sizes. `p4d_bad()` treats zero as bad, consistent with folded semantics, but callers must not use it as a generic corruption detector for non-present entries.

## Test Signals
Build 64-bit nohash 4K page configs, run mmap/remap tests, inspect folded P4D walks, and validate page-table debug output for PUD/P4D transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/64/pgtable-4k.h -->
