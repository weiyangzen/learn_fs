# sources/distributed-fs/ceph-client/arch/powerpc/mm/pgtable_32.c

## Purpose
This file contains 32-bit PowerPC page-table setup helpers for early ioremap, kernel page mapping, low-memory RAM mapping, and strict kernel permission changes for init text and rodata.

## Important APIs, Types, And Functions
Key functions are `early_ioremap_init()`, `early_alloc_pgtable()`, `early_pte_alloc_kernel()`, `map_kernel_page()`, `mapin_ram()`, `mark_initmem_nx()`, and under strict RWX `mark_rodata_ro()`. The file owns `early_fixmap_pagetable[]`.

## Control Flow
`early_ioremap_init()` populates fixmap PMDs with the static early PTE table and then calls `early_ioremap_setup()`. `map_kernel_page()` finds the kernel PMD, allocates a PTE via slab or memblock depending on boot phase, asserts an existing valid/hash PTE is not overwritten, installs the PFN PTE, and issues a write barrier. `mapin_ram()` iterates memblock ranges below `total_lowmem`, lets `mmu_mapin_ram()` map platform-supported block ranges first, then maps remaining pages individually with executable permissions only for core kernel text. `mark_initmem_nx()` and `mark_rodata_ro()` delegate to block-map MMU helpers when possible or use set-memory APIs.

## State And Persistence
The file builds persistent kernel page-table entries in `init_mm` and static fixmap early tables. Permission changes persist in kernel mappings after init.

## Dependencies And Integration Points
It depends on memblock, early ioremap, fixmap constants, `pmd_off_k()`, PTE allocation, `set_pte_at()`, platform `mmu_mapin_ram()`, `v_block_mapped()`, `mmu_mark_initmem_nx()`, `mmu_mark_rodata_ro()`, and generic set-memory functions.

## Risks And Test Signals
Risks include early fixmap table size/index mismatches, overwriting existing mappings, wrong executable permission for kernel text/data, and divergence between block mappings and page-table mappings. Test signals include 32-bit boot with early ioremap, strict kernel RWX, module RWX warnings on hash MMU, lowmem holes, and initmem permission transitions.
