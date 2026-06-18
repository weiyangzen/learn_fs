<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/io-pgtable-arm.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/io-pgtable-arm.c

Purpose: ARM LPAE IOMMU page-table backend for 32/64-bit stage-1, stage-2, and Mali LPAE formats. It allocates page tables, encodes register configuration, maps/unmaps page ranges, translates IOVAs, walks page tables, and supports dirty-bit harvesting for ARM64 S1.

Important APIs/types/functions: `struct arm_lpae_io_pgtable`, `arm_lpae_alloc_pgtable()`, `arm_64_lpae_alloc_pgtable_s1()`, `arm_64_lpae_alloc_pgtable_s2()`, `arm_32_lpae_alloc_pgtable_s1()`, `arm_32_lpae_alloc_pgtable_s2()`, `arm_mali_lpae_alloc_pgtable()`, `arm_lpae_map_pages()`, `arm_lpae_unmap_pages()`, `arm_lpae_iova_to_phys()`, `arm_lpae_pgtable_walk()`, `arm_lpae_read_and_clear_dirty()`, and the five `io_pgtable_*_init_fns`.

Control flow: allocation restricts page sizes to supported granules, computes levels/start-level/PGD bits, validates quirks, fills TCR/VTCR/MAIR/Mali config, optionally adjusts concatenated stage-2 PGDs, allocates the root table, and publishes TTBR/VTTBR. Mapping validates IOVA/PA/prot, encodes permissions/memory attributes/shareability/XN/NS/AF/DBM, recursively allocates child tables, atomically installs table PTEs, and writes leaf entries. Unmap recursively clears leaves or table entries, flushes partial walks, frees child tables, and records gather pages. Walk helpers visit PTEs for translation, debug walking, or dirty bitmap collection.

State and persistence: backend state includes computed table geometry and root `pgd`; config stores hardware register values. Hardware-visible PTEs persist mappings, table links, dirty/DBM state, and software sync bits for noncoherent walkers.

Dependencies and integration: selected through `io-pgtable.c`; uses `iommu-pages`, DMA mapping for noncoherent page-table sync, generic TLB flush callbacks, dirty bitmap helpers, and ARM LPAE register definitions in `io-pgtable-arm.h`.

Risks: this local source snapshot has duplicate function parameter text and duplicate `return 0;` in places, suggesting a merge/copy issue that may break compilation. Correctness depends on barrier and cache-sync ordering around table install and leaf writes. Partial large-page unmap is rejected. Dirty tracking is limited to ARM64 S1 and writeable-dirty PTE interpretation.

Test signals: KUnit LPAE selftests, map/unmap/translate across 4K/16K/64K granules, stage-1/stage-2 register config validation, noncoherent walk DMA sync, dirty bitmap read-and-clear, custom allocator use, and overlap/partial-unmap rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/io-pgtable-arm.c -->
