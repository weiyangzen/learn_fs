# sources/distributed-fs/ceph-client/arch/microblaze/mm/init.c

Purpose: initializes MicroBlaze physical memory, zones, MMU hardware, kernel mappings, memblock reservations, fixmaps, highmem, and page protection map.

Important APIs and state: globals `mem_init_done`, `klimit`, `memory_start`, `memory_size`, `lowmem_size`, exported PFN bounds, `setup_memory()`, `mem_init()`, `page_is_ram()`, `mmu_init()`, and `protection_map`.

Control flow: `mmu_init()` validates minimum memory and kernel footprint, derives memory bounds from memblock, applies `mem=`, reserves kernel/initrd, sets ZPR, maps RAM, initializes ioremap bounds, initializes MMU contexts, constrains memblock allocation, parses early params, scans reserved memory, reserves CMA, and dumps memblock. `setup_memory()` computes PFN ranges and clears fixmaps.

State and persistence: boot-time globals and page tables persist; `mem_init_done` changes ioremap behavior after memory init.

Dependencies and integration: called from `head.S`; uses `mapin_ram()`, `map_page()`, `mmu_context_init()`, and setup-provided `kernel_tlb`.

Risks and test signals: low memory > `CONFIG_LOWMEM_SIZE` truncation, highmem behavior, and kernel TLB size checks can prevent boot. Test small memory rejection, initrd reservation, `mem=`, CMA, highmem, fixmap clearing, and protection bits.
