# sources/distributed-fs/ceph-client/arch/powerpc/mm/nohash/tlb_64e.c

## Purpose
This file performs early MMU and TLB setup for 64-bit Book3E systems. It discovers supported hardware page sizes, configures hardware tablewalk mode for e6500-style processors, sets default MAS4 behavior, bolts the early linear map into TLBCAMs, and constrains usable memory to what the early nohash mapping can cover.

## Important APIs, Types, And Functions
Global state includes `mmu_vmemmap_psize`, `book3e_htw_mode`, `linear_map_top`, and `extlb_level_exc`; the internal `mmu_pte_psize` chooses the PTE-page TLB size. Key functions are `tlb_flush_pgtable()`, `setup_page_sizes()`, `early_init_this_mmu()`, `early_init_mmu_global()`, `early_mmu_set_memory_limit()`, `early_init_mmu()`, `early_init_mmu_secondary()`, and `setup_initial_memory_limit()`.

## Control Flow
Boot CPU init calls `early_init_mmu_global()` to set a 4K vmemmap page size, inspect `MMUCFG`, `TLB0CFG`, `TLB1CFG`, `TLB1PS`, and `EPTCFG`, mark supported direct or indirect page sizes, optionally patch TLB miss vectors to e6500 handlers, set `linear_map_top` to DRAM end, and initialize `ioremap_bot`. `early_init_this_mmu()` programs MAS4, selects 2M PTE pages in e6500 tablewalk mode or the virtual page size otherwise, maps a quarter of TLB1 CAMs for the linear map once per core, and synchronizes. Boot then enforces the linear-map memory limit. Secondary CPUs only run the per-core MMU setup.

## State And Persistence
Page-size flags in `mmu_psize_defs[]`, `book3e_htw_mode`, MAS4, and TLBCAM mappings persist for runtime TLB miss handling. `linear_map_top` becomes both a mapping bound for low-level handlers and a memory availability limit.

## Dependencies And Integration Points
This file is tightly coupled to Book3E SPRs, `map_mem_in_cams()`, exception patching via `patch_exception()`, memblock, and assembly handlers in `tlb_low_64e.S`. `tlb_flush_pgtable()` integrates page-table freeing with indirect TLB entry invalidation and calls `__flush_tlb_page()`.

## Risks And Test Signals
Major risks are misdetecting hardware tablewalk capability, using unsupported page size combinations, mapping insufficient linear memory, and failing to invalidate indirect entries when PTE pages are freed. Useful tests boot e6500 and non-HTW Book3E variants, verify memory above the bolted range is excluded, exercise vmemmap/page-table free paths, and confirm patched exception vectors handle user, kernel, and hugepage misses.
