<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/io-pgtable-dart.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/io-pgtable-dart.c

Purpose: Apple DART/DART2 IOMMU page-table backend. It allocates top-level TTBR tables, creates intermediate tables, maps/unmaps fixed-size pages, translates IOVAs, and encodes DART1/DART2 protection and physical-address formats.

Important APIs/types/functions: `struct dart_io_pgtable`, `apple_dart_alloc_pgtable()`, `apple_dart_free_pgtable()`, `dart_map_pages()`, `dart_unmap_pages()`, `dart_iova_to_phys()`, `dart_alloc_pgtable()`, and exported `io_pgtable_apple_dart_init_fns`.

Control flow: allocation requires coherent walks, OAS 36 or 42, IAS <= OAS, and page size exactly 4K or 16K. It computes level count, top-table count, and bits per level, allocates each TTBR root table, and fills `apple_dart_cfg`. Mapping validates fixed page size, PA range, and read/write permission, walks/allocates intermediate tables with atomic install, then installs leaf PTEs for as many entries as fit in the last table. Unmap finds the last-level table, clears valid PTEs, and records TLB pages. Translation walks to the last-level PTE and adds page offset.

State and persistence: state is `pgd[]`, level geometry, and DART PTEs. PTEs include valid bit, DART1/DART2 no-read/no-write/no-cache bits, DART1 subpage allow range, and encoded physical address.

Dependencies and integration: selected through `io-pgtable.c` for `APPLE_DART` and `APPLE_DART2`; uses `iommu-pages`, atomic cmpxchg, generic TLB gather, and Apple DART driver config.

Risks: only coherent page-table walks are supported. `pgsize_bitmap` is treated as a single fixed page size, not a bitmap of alternatives. Intermediate tables are not freed on individual unmaps, only full free. Address encoding differs between DART generations and must match hardware.

Test signals: DART1 and DART2 map/unmap/translate, 4K and 16K roots, multi-TTBR DART1 coverage, invalid IAS/OAS/page-size rejection, overlap map rejection, and teardown freeing all allocated levels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/io-pgtable-dart.c -->
