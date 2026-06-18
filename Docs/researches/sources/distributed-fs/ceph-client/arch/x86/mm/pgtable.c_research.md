# sources/distributed-fs/ceph-client/arch/x86/mm/pgtable.c

## Purpose
`pgtable.c` provides x86 page-table allocation, freeing, PGD synchronization, access-bit operations, fixmap installation, huge-vmap helpers, and shadow-stack-aware write-protection helpers. It is the architecture layer between generic MM and x86 paging details.

## Important APIs, Types, and Functions
Key APIs include `pte_alloc_one()`, `___pte_free_tlb()`, `___pmd_free_tlb()`, `___pud_free_tlb()`, `___p4d_free_tlb()`, `pgd_alloc()`, `pgd_free()`, `ptep_set_access_flags()`, transparent-hugepage access helpers, `reserve_top_address()`, `native_set_fixmap()`, `pud_set_huge()`, `pmd_set_huge()`, huge-entry clear/free helpers, `pte_mkwrite()`, `pmd_mkwrite()`, and `arch_check_zapped_pte/pmd/pud()`. `physical_mask` is exported when dynamic physical masks are configured.

## Control Flow and State
PGD allocation creates the top-level table, preallocates PMDs where PAE and PTI require them, invokes paravirt allocation hooks, and adds the PGD to `pgd_list` under `pgd_lock` so kernel mapping changes can be synchronized. Freeing tears down preallocated PMDs, removes list membership, releases paravirt state, and frees the PGD. Access-flag helpers update PTE/PMD/PUD entries only when generic MM needs hardware-visible write/accessed changes. Fixmap setup resolves a fixed-address index to a virtual address and installs a sanitized PTE through `set_pte_vaddr()`. Huge-vmap helpers install or clear PMD/PUD huge mappings only when MTRR cache modes are uniform.

## State and Persistence
Persistent state includes each `mm_struct` PGD, preallocated kernel/user PMDs for PAE/PTI, the global `pgd_list`, per-table paravirt allocation state, `fixmaps_set`, `__FIXADDR_TOP`, and page-table page reference/accounting counters. Page aging state lives in hardware accessed bits that this file can test and clear.

## Dependencies and Integration Points
Dependencies include `asm/pgalloc.h`, paravirt hooks, `mmu_gather`, transparent hugepage support, fixmap code, MTRR type lookup, PTI helpers, shadow-stack PTE encodings, and generic mmap/fault/unmap paths.

## Risks and Test Signals
Risks include partial PGD prepopulation visible to `pgd_list` walkers, missing CR3 reloads in PAE, freeing page-table pages before TLB invalidation, huge mapping over non-uniform MTRR ranges, and mishandling shadow-stack dirty/write encodings. Test signals include fork/exec/exit page-table stress, PAE and PTI boot tests, vmalloc/ioremap huge-vmap behavior, THP access-bit tests, fixmap users, and CET shadow-stack selftests.
