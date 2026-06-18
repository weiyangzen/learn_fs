# sources/distributed-fs/ceph-client/arch/microblaze/mm/pgtable.c

Purpose: builds and manipulates MicroBlaze kernel page tables, ioremap mappings, physical-address lookup, RAM linear mapping, early PTE allocation, and fixmaps.

Important APIs and state: exported `ioremap_bot`; globals `ioremap_base`, `ioremap_bot`; functions `ioremap()`, `iounmap()`, `map_page()`, `mapin_ram()`, `iopa()`, `pte_alloc_one_kernel()`, and `__set_fixmap()`.

Control flow: `__ioremap()` rejects remapping normal RAM after `mem_init_done`, allocates vmalloc or early downward ioremap space, maps pages with guarded/no-cache flags, and returns offset-adjusted virtual address. `map_page()` allocates kernel PTEs and invalidates TLB after boot. `mapin_ram()` maps lowmem with write permissions outside kernel text. `iopa()` walks page tables for current or init mm.

State and persistence: mutates kernel page tables, ioremap virtual allocation state, and TLB entries.

Dependencies and integration: used by MMU init, drivers, PCI, fixmap, and DMA translation paths.

Risks and test signals: `iounmap()` range check appears unusual and may skip some vmalloc areas. Early PTE allocation is bounded by `memory_start + kernel_tlb`. Test early/late ioremap, RAM remap rejection, fixmaps, iopa for user/kernel addresses, and text page permissions.
