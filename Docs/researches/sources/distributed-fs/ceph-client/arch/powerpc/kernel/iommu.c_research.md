# sources/distributed-fs/ceph-client/arch/powerpc/kernel/iommu.c

## Purpose
Implements bus-independent PowerPC dynamic DMA/IOMMU TCE mapping management, including table allocation, bitmap pools, SG mapping, coherent allocations, kdump preservation, debugfs/fault injection, and SPAPR IOMMU API integration.

## Important APIs, Types, And Functions
Major functions include `iommu_init_table`, `iommu_table_clear`, `iommu_table_reserve_pages`, `iommu_table_in_use`, `iommu_tce_table_get`, `iommu_tce_table_put`, `iommu_map_phys`, `iommu_unmap_phys`, `iommu_alloc_coherent`, `iommu_free_coherent`, `ppc_iommu_map_sg`, `ppc_iommu_unmap_sg`, `iommu_direction_to_tce_perm`, `iommu_register_group`, `iommu_add_device`, `iommu_flush_tce`, `iommu_tce_check_ioba`, `iommu_tce_check_gpa`, `iommu_tce_xchg_no_kill`, `iommu_tce_kill`, `ppc_iommu_register_device`, and `ppc_iommu_unregister_device`. Internal allocation is centered on `iommu_range_alloc`, `iommu_alloc`, `__iommu_free`, and per-table `iommu_pool` locks.

## Control Flow
Boot parameters configure virtual merging and optional fault injection. Table initialization allocates the bitmap, reserves forbidden pages, splits large tables into hashed small pools plus a large-allocation pool, clears or preserves TCEs depending on kdump/fadump state, and registers debugfs. Mapping allocates bitmap space, calls table operations to install TCEs, flushes if required, and uses memory barriers before hardware can DMA. SG mapping allocates per input segment, optionally merges contiguous DMA ranges, and backs out all successful allocations on failure. Unmap clears hardware TCEs and bitmap bits. IOMMU API support creates groups/domains and registers SPAPR TCE IOMMU devices for PHBs.

## State And Persistence
Persistent in-memory state includes each `iommu_table` bitmap, pool hints and spinlocks, kref, reserved range metadata, table operation pointers, debugfs entries, per-CPU pool hashes, fault-injection attributes, device `archdata.fail_iommu`, and IOMMU groups/domains. Hardware-visible state is the TCE table programmed by platform `it_ops`. Kdump paths may intentionally preserve first-kernel TCEs in the bitmap.

## Dependencies And Integration Points
Depends on DMA mapping core, scatterlist APIs, PowerPC PCI/VIO/platform TCE operations, `iommu-helper`, crash dump/fadump detection, debugfs, fault injection, generic IOMMU API, VFIO/SPAPR TCE ownership callbacks, PCI hose list, and platform-specific `iommu_table_ops`.

## Risks And Edge Cases
Risks include bitmap/hardware TCE mismatch, allocation fragmentation, mask and segment-boundary constraints, SG merge correctness, transient `set` failures and backout, kdump preserving too many or too few TCEs, reserved MMIO32 windows, reference lifetime of tables and IOMMU groups, and ownership transitions between platform and blocked domains. The allocator assumes `nr_pools` is power-of-two for hash masking.

## Test Signals
Signals include DMA API tests, high-throughput SG DMA, boundary/mask-limited devices, coherent allocation/free stress, driver bind/unbind leak checks, kdump/fadump boot with active DMA mappings, debugfs table weight, `fail_iommu` injection, VFIO/SPAPR TCE tests, IOMMU group sysfs presence, and cross-platform pseries/powernv/VIO/PCI coverage.
