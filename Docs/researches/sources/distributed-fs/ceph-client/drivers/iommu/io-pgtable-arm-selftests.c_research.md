<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/io-pgtable-arm-selftests.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/io-pgtable-arm-selftests.c

Purpose: KUnit tests for ARM LPAE IOMMU page-table operations.

Important APIs/types/functions: `arm_lpae_do_selftests()` is the KUnit case; `arm_lpae_run_tests()` exercises `alloc_io_pgtable_ops()`, `map_pages`, `unmap_pages`, and `iova_to_phys` for `ARM_64_LPAE_S1` and `ARM_64_LPAE_S2`. Dummy TLB callbacks validate cookie and page-size arguments.

Control flow: the test registers a KUnit device, constructs coherent-walk configs with `IO_PGTABLE_QUIRK_NO_WARN`, iterates 4K/16K/64K granule page-size sets and IAS/OAS combinations, allocates both S1 and S2 page tables, verifies empty translations, maps distinct granularities, rejects overlapping maps, verifies translation offsets, unmaps/remaps, and tests the last largest supported page of the IAS.

State and persistence: state is per-test `io_pgtable_cfg`, dummy cookie, temporary page tables, and pass/fail counters. Page tables are freed after each format pass.

Dependencies and integration: depends on KUnit, `io-pgtable-arm.h`, generic io-pgtable allocation, and ARM LPAE backend availability.

Risks: early return on failure may skip `free_io_pgtable_ops()` for the failing case. The test covers core map/unmap/translate behavior but not dirty tracking, custom allocators, noncoherent walks, or all quirks.

Test signals: KUnit suite `io-pgtable-arm-test`, pass/fail summary, overlap rejection, boundary mapping near `1 << ias`, and KASAN/KMEMLEAK for allocation/free balance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/io-pgtable-arm-selftests.c -->
