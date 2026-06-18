# sources/distributed-fs/ceph-client/arch/powerpc/mm/pgtable_64.c

## Purpose
This file provides 64-bit PowerPC page-table globals and helpers. For Book3S 64 it exports runtime page-table geometry, partition/process table pointers, kernel virtual region bounds, vmemmap, and PTE fragment sizing. It also provides page-descriptor helpers for upper-level entries and strict RWX dispatch.

## Important APIs, Types, And Functions
Global symbols include `process_tb`, `partition_tb`, `__pte_index_size`, `__pmd_index_size`, `__pud_index_size`, `__pgd_index_size`, table sizes, value-bit sizes, virtual region bounds, `vmemmap`, `__pte_frag_nr`, and `__pte_frag_size_shift`. Functions include `p4d_page()` when PUD is not folded, `pud_page()`, `pmd_page()`, `mark_rodata_ro()`, and `mark_initmem_nx()`.

## Control Flow
The page helper functions distinguish leaf huge mappings from pointers to lower-level tables. For leaf entries they return `pte_page()` from the converted PTE; for table pointers they return `virt_to_page()` on the next-level table address. Strict RWX functions choose radix or hash implementations at runtime, with a feature check for `MMU_FTR_KERNEL_RO` before trying to mark rodata read-only.

## State And Persistence
The exported geometry variables define the runtime page-table layout and are consumed across the architecture. `process_tb` and `partition_tb` persist as ISA 3.0 translation structures. Region-bound globals persist as the canonical Book3S64 kernel virtual layout.

## Dependencies And Integration Points
This file integrates Book3S64 radix/hash setup code, vmalloc/vmemmap helpers, hugetlb/huge-vmap page lookup, and strict RWX implementations `radix__mark_*` and `hash__mark_*`.

## Risks And Test Signals
Risks include returning wrong `struct page` for leaf huge-vmap entries, stale exported geometry values, and silently failing strict RWX when CPU features cannot enforce it. Test signals include vmalloc-to-page on huge vmap, radix and hash boots, strict RWX verification, and Book3S64 page table geometry self-consistency.
