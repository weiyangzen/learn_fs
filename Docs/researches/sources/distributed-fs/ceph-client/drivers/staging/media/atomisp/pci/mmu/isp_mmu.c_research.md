# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/mmu/isp_mmu.c

Purpose: `sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/mmu/isp_mmu.c` implements the generic AtomISP two-level ISP MMU page-table manager: page-table allocation/free, map, unmap, remap detection, error logging, initialization, TLB-range fallback, and teardown.

Important APIs, types, and functions: Important local symbols: `free_mmu_map`, `atomisp_get_pte`, `atomisp_set_pte`, `isp_pte_to_pgaddr`, `isp_pgaddr_to_pte_valid`, `alloc_page_table`, `free_page_table`, `mmu_remap_error`, `mmu_unmap_l2_pte_error`, `mmu_unmap_l1_pte_error`, `mmu_unmap_l1_pt_error`, `mmu_l2_map`, `mmu_l1_map`, `mmu_map` Types and constants: No named structs or enums are introduced here.; `NR_PAGES_2GB`

Control flow: Mapping lazily allocates an uncached DMA32 L1 table, allocates L2 tables on demand, writes valid PTEs for each ISP virtual page, and rolls back partial maps on error. Unmapping clears L2 PTEs, decrements per-L1 refcounts, frees empty L2 tables, and teardown frees all remaining tables.

State and persistence behavior: State is in-memory page tables, `mmu->l1_pte`, `base_address`, L2 refcounts, callback pointers, and hardware TLB/cache state. There is no persistence after driver teardown.

Dependencies and integration points: The code depends on Linux page allocation, DMA32 constraints, x86 cacheability APIs, AtomISP device logging, `struct isp_mmu_client`, PTE macros, and hardware invalidation through `ia_css_mmu_invalidate_cache()`.

Risks and edge cases: Rollback calls back into unmap while holding mapping context, refcount underflow is possible after invalid unmaps, and failure paths depend on correct page alignment and PTE validity masks.

Test signals: Test mapping/unmapping across L1 boundaries, duplicate mappings, partial allocation failure rollback, invalid unmap diagnostics, DMA32 allocation failure, init validation for missing callbacks/masks, exit with populated tables, and TLB flush behavior.
