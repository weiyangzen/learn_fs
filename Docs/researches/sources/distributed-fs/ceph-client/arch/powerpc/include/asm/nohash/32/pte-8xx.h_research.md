<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/32/pte-8xx.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/32/pte-8xx.h

## Purpose
This header defines the MPC8xx PTE and PMD bit layout plus specialized PTE update helpers for the 8xx hardware-assisted software tablewalk model.

## Important APIs, Types, And Functions
It defines 8xx `_PAGE_*` permission/cache/huge/SPS bits, `_PMD_*` page-size and access bits, kernel/user protection combinations, `pte_wrprotect()`, `pte_read()`, `pte_write()`, `pte_mkwrite_novma()`, `pte_mkhuge()`, `ptep_set_wrprotect()`, `__ptep_set_access_flags()`, `__pte_leaf_size()`, `ptep_is_8m_pmdp()`, `number_of_cells_per_pte()`, `__pte_update()`, `pte_update()`, and 16K `ptep_get()`.

## Control Flow
Permission changes flow through `pte_update()`. For huge 8M PMD mappings it updates two PMD-backed PTE ranges; otherwise it updates replicated PTE cells. `__ptep_set_access_flags()` updates accessed/dirty/exec/protection bits and flushes the affected TLB page.

## State And Persistence Behavior
8xx page-table state is unusual: 16K pages duplicate four cells, 512K pages duplicate 128 cells, and 8M mappings duplicate 1024 cells per 4M half. Dirty and access state are software-maintained and reflected into APG/TWC fields during refill.

## Dependencies And Integration Points
It depends on 8xx MMU page-size definitions, `pmd_off()`, `pte_offset_kernel()`, TLB flushing, and `pgtable-masks.h`. It is consumed by generic nohash pgtable operations and 8xx TLB miss handling.

## Risks And Edge Cases
The write-protect encoding is inverted relative to common PTE formats. Replication counts are page-size sensitive and easy to corrupt. 8M PMD-backed mappings alias PMD and PTE pointers, so pointer tests must stay exact.

## Test Signals
Exercise 4K, 16K, 512K, and 8M mappings; run mprotect, COW, hugepage, vmalloc, and TLB flush tests; validate PTE replication under page-table debugging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/32/pte-8xx.h -->
