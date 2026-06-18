# sources/distributed-fs/ceph-client/arch/sparc/kernel/iommu-common.c

## Purpose
`iommu-common.c` implements shared bitmap/pool allocation for SPARC IOMMU mapping tables. It is derived from the powerpc allocator and supports per-pool hints, optional large allocation pool, segment-boundary constraints, and lazy flush callbacks.

## Important APIs, Types, and Functions
Public functions are `iommu_tbl_pool_init()`, `iommu_tbl_range_alloc()`, and `iommu_tbl_range_free()`. Internal helpers manage `IOMMU_NEED_FLUSH`, per-CPU pool hashes, and mapping entry-to-pool selection.

## Control Flow and State
Initialization hashes CPUs to pools, sets table shift and flush callback, configures pool count, flags, pool size, hints, and optional top-quarter large pool. Allocation chooses a pool from per-CPU hash or the large pool, honors a caller handle if it is inside the pool, clamps to device DMA mask, computes boundary constraints, calls `iommu_area_alloc()`, retries from pool starts and across pools, marks flush-needed on wrap/failure, and invokes `lazy_flush()` before reusing wrapped space. Free computes or accepts an entry index, finds the owning pool, and clears the bitmap range under the pool lock.

## Persistence and Dependencies
Persistent state lives in `struct iommu_map_table`: bitmap, pools, hints, flags, table base/shift, and lazy flush callback. Dependencies include `iommu-helper`, DMA segment-boundary helpers, per-CPU hashes, and spinlocks.

## Integration Points, Risks, and Test Signals
Used by sparc64 IOMMU DMA mapping code and potentially other SPARC IOMMU users. Risks include pool size assumptions when `nr_pools` is not power-of-two, DMA mask limit edge cases, lazy flush ordering, and bitmap leaks after failed multi-segment maps. Test signals are DMA map/unmap stress, SG merging with boundaries, low DMA mask devices, large allocations, and no bitmap exhaustion after repeated failures.
