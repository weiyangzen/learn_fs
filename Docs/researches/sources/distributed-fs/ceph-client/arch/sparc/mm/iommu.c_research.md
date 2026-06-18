# sources/distributed-fs/ceph-client/arch/sparc/mm/iommu.c

Purpose: SPARC32 SBUS IOMMU/DVMA support for systems with IOMMU hardware.

Important APIs/functions: `iommu_init` discovers `iommu` OF nodes and initializes each through `sbus_iommu_init`. DMA operations are split into global-flush and per-page-flush variants: `sbus_iommu_map_phys_gflush/pflush`, `sbus_iommu_map_sg_gflush/pflush`, `sbus_iommu_unmap_phys`, `sbus_iommu_unmap_sg`, and under `CONFIG_SBUS`, `sbus_iommu_alloc/free`. `ld_mmu_iommu` initializes cacheability/PTE permission defaults by CPU type.

Control flow: initialization maps IOMMU registers, enables a 256MB range, allocates and zeroes the IOMMU page table and bitmap, configures page coloring for HyperSPARC, and chooses DMA ops based on `flush_page_for_dma_global`. Mapping rejects MMIO and >256 KiB ranges, optionally flushes CPU cache pages, allocates colored IOMMU slots via `bit_map_string_get`, writes IOPTEs and invalidates IOMMU pages, flushes IOPTE cache lines, and returns a bus address. Unmap clears IOPTEs, invalidates hardware, and frees bitmap slots. Consistent allocation reserves a DVMA resource, maps kernel PTEs with `dvma_prot`, writes non-cacheable or cacheable IOPTEs depending on CPU, flushes cache/TLB, and returns CPU/DMA handles.

State and persistence: per-device `iommu_struct` persists with registers, page table, start/end, and `usemap`. Static `ioperm_noc`, `dvma_prot`, and `viking_flush` influence future mappings. Hardware IOMMU page table state persists until unmapped.

Dependencies/integration: uses OF/platform devices, SBUS IOMMU registers, `bitext` allocator, CPU cache flush routines (`viking_*`, `__flush_page_to_ram`), SPARC DMA resource allocator, and `mm_32.h`.

Risks: partial scatter-gather map failure returns `-EIO` without undoing earlier entries. Cache-coherency choices depend on CPU detection and `flush_page_for_dma_global`. Bitmap exhaustion panics. Consistent allocation/free requires exact DVMA resource and bitmap synchronization.

Test signals: SBUS DMA workloads on Viking/HyperSPARC and non-cache-coherent CPUs, map/unmap stress with page-color constraints, scatter-gather failure injection, >256 KiB rejection, consistent DMA allocation/free, and IOMMU register/page-table inspection.
