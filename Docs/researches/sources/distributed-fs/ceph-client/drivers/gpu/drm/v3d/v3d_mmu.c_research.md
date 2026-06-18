<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/v3d/v3d_mmu.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/v3d/v3d_mmu.c

Purpose: Manages V3D's single-level GPU page table: MMU/TLB flush, page-table base setup, PTE insertion for BO scatterlists, and PTE removal.

Important APIs/types/functions: PTE flag constants include valid, writable, bigpage, and superpage bits. `v3d_mmu_flush_all()` flushes MMUC and clears MMU TLB with waits. `v3d_mmu_set_page_table()` writes page-table base, enables invalid/write/cap abort+interrupt behavior, configures illegal-address scratch page, enables MMUC, and flushes. `v3d_mmu_insert_ptes()` walks BO SG DMA entries, emits 4K/64K/1M PTEs when aligned, and flushes. `v3d_mmu_remove_ptes()` zeros BO PTEs and flushes.

Control flow: GEM init sets the page table once; BO creation inserts PTEs after DRM MM range allocation; BO free removes them before range release. Each insert/remove globally flushes the MMU.

State and persistence: State is the device-wide page-table DMA allocation, scratch page, and hardware MMU registers. No per-process address spaces are used.

Dependencies and integration points: Integrates DRM GEM shmem SG tables, V3D BO offsets from DRM MM, DMA addresses, V3D register macros, and wait helpers.

Risks and test signals: The design shares one address space and notes GMP client isolation is not implemented. Risks include PTE alignment mistakes, DMA address width BUG_ON, global flush timeouts, and stale mappings. Tests should cover 4K/64K/1M mappings, scatterlist boundaries, removal, MMU fault IRQs, and BO churn under workload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/v3d/v3d_mmu.c -->
