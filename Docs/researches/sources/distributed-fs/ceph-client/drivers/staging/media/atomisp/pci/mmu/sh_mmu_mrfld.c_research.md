# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/mmu/sh_mmu_mrfld.c

Purpose: `sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/mmu/sh_mmu_mrfld.c` defines the Merrifield/Silicon Hive ISP3000 MMU client adapter, converting physical addresses to PTEs and page-directory bases and flushing the hardware cache/TLB.

Important APIs, types, and functions: Important local symbols: `sh_phys_to_pte`, `sh_pte_to_phys`, `sh_get_pd_base`, `sh_tlb_flush` Types and constants: `isp_mmu_client`; `MERR_VALID_PTE_MASK`

Control flow: `sh_mmu_mrfld` supplies callbacks used by `isp_mmu_init()`: `phys_to_pte`, `pte_to_phys`, `get_pd_base`, and `tlb_flush_all`.

State and persistence behavior: State is in-memory page tables, `mmu->l1_pte`, `base_address`, L2 refcounts, callback pointers, and hardware TLB/cache state. There is no persistence after driver teardown.

Dependencies and integration points: The code depends on Linux page allocation, DMA32 constraints, x86 cacheability APIs, AtomISP device logging, `struct isp_mmu_client`, PTE macros, and hardware invalidation through `ia_css_mmu_invalidate_cache()`.

Risks and edge cases: The valid-bit mask is hardware-specific; using this client on the wrong MMU generation would translate addresses incorrectly.

Test signals: Test mapping/unmapping across L1 boundaries, duplicate mappings, partial allocation failure rollback, invalid unmap diagnostics, DMA32 allocation failure, init validation for missing callbacks/masks, exit with populated tables, and TLB flush behavior.
