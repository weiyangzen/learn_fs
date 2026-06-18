<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/dart_iommu.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/dart_iommu.c

Purpose: dynamic DMA mapping support for Apple U3/U4 and IBM CPC925 DART IOMMUs.

Important APIs/types/functions: early entry `iommu_init_early_dart()`, optional restore `iommu_dart_restore()`, IOMMU table ops `dart_build()`, `dart_free()`, `dart_flush()`, hardware helpers `dart_tlb_invalidate_all()`, `dart_tlb_invalidate_one()`, `dart_cache_sync()`, `allocate_dart()`, `dart_init()`, and PCI setup hooks `pci_dma_bus_setup_dart()`, `pci_dma_dev_setup_dart()`, `iommu_bypass_supported_dart()`.

Control flow: early init finds `u3-dart` or `u4-dart`, skips if IOMMU is disabled or not needed for small memory without force, maps registers, allocates a 16 MiB-aligned table below 2 GiB plus a dummy page, fills invalid entries with the dummy mapping, writes table base/size/control registers, flushes DART TLB, installs PCI controller DMA setup hooks, and switches PCI DMA ops to IOMMU. Mapping writes valid RPN entries, cache-syncs them, then invalidates per-entry on U4 or marks U3 dirty for later full flush. Freeing writes dummy entries and cache-syncs. U4 PCIe devices with sufficient masks can bypass through a 40-bit offset.

State and persistence: global MMIO pointer, table base/size, dummy invalid value, `iommu_table_dart`, initialized/dirty flags, and U4 flag persist for the life of the kernel. DART table contents represent active DMA mappings.

Dependencies and integration points: depends on memblock early allocation, OF address discovery, PCI controller ops, common PowerPC IOMMU code, cache flush primitives, PCI DMA ops, suspend `ppc_md.iommu_restore`, and command-line IOMMU policy.

Risks: DART hardware is cache-incoherent, so missing `dart_cache_sync()` can cause stale translations. TLB flush loops can panic on stuck hardware. The dummy page workaround avoids HT bridge prefetch corruption; removing it risks data corruption. Bypass support must be limited to U4 PCIe devices with a large enough DMA mask.

Test signals: boot logs showing DART initialized, PCI devices DMAing correctly above 1 GiB, IOMMU map/free stress, U4 bypass for 40-bit devices, suspend/resume DMA after restore, and no DART TLB flush panics validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/dart_iommu.c -->
