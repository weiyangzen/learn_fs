<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/io-pgtable-arm-v7s.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/io-pgtable-arm-v7s.c

Purpose: ARMv7 short-descriptor IOMMU page-table backend supporting 32-bit and MediaTek-extended formats, two-level table allocation, mapping/unmapping, translation lookup, cache synchronization, and optional built-in selftests.

Important APIs/types/functions: `struct arm_v7s_io_pgtable`, `arm_v7s_alloc_pgtable()`, `arm_v7s_map_pages()`, `arm_v7s_unmap_pages()`, `arm_v7s_iova_to_phys()`, `arm_v7s_free_pgtable()`, and exported `io_pgtable_arm_v7s_init_fns`. Helpers cover PTE encoding, contiguous section/page handling, MediaTek high PA bits, and table install.

Control flow: allocation validates IAS/OAS and quirks, creates an L2 table slab, restricts page sizes, prepares PRRR/NMRR/TCR/TTBR config, allocates an L1 table, and returns ops. Mapping descends from L1 to L2 as needed, allocating synchronized tables, then installs one or more leaf PTEs. Unmapping rejects partial unmap of contiguous large entries, clears PTEs, frees child tables for table entries, and records TLB gather pages. Translation walks levels until a leaf or invalid PTE.

State and persistence: persistent backend state is the L1 `pgd`, L2 slab cache, and encoded register values in `io_pgtable_cfg`. PTEs persist hardware-visible mappings and may encode contiguous large entries or MediaTek high-address bits.

Dependencies and integration: used by IOMMU drivers selecting `ARM_V7S`; depends on DMA mapping for noncoherent walkers, kmem caches, generic io-pgtable callbacks, and optional `CONFIG_IOMMU_IO_PGTABLE_ARMV7S_SELFTEST`.

Risks: contiguous entries cannot be partially unmapped. Table physical addresses must fit PTE format unless MediaTek TTBR extension is enabled. Noncoherent sync ordering is critical. Permission handling can be disabled by quirk, so callers must understand hardware protection. Selftest-only overlap warnings differ from normal runtime behavior.

Test signals: built-in selftest with 4K/64K/1M/16M sizes, MediaTek quirk configurations, noncoherent table walks, overlap map rejection, contiguous entry full unmap, and translation after map/unmap.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/io-pgtable-arm-v7s.c -->
