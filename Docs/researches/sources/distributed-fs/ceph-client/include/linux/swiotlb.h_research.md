<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/swiotlb.h -->
# sources/distributed-fs/ceph-client/include/linux/swiotlb.h

## Purpose

`swiotlb.h` declares the Software I/O TLB bounce-buffer interface used by DMA mapping code when devices cannot directly address memory or when restricted/encrypted DMA pools are required. It describes pool layout, initialization, mapping, unmapping, sync, and restricted allocation helpers.

## Important APIs, types, and functions

Constants define flags, segment size, slab size, and default pool size. `struct io_tlb_pool` describes one pool, including physical range, virtual address, slots, areas, dynamic list membership, and transient status. `struct io_tlb_mem` describes per-device/default allocator state, dynamic growth, limits, locks, work, and debug counters. APIs include early/late initialization, memory attribute updates, device init, pool lookup, force-bounce checks, map/unmap/sync helpers, allocation-state queries, default range queries, info printing, and restricted-pool `swiotlb_alloc()`/`free()`.

## Control flow

DMA mapping code maps a physical buffer through `swiotlb_tbl_map_single()`/`swiotlb_map()` when bouncing is needed. Later unmap and sync helpers first call `swiotlb_find_pool()`; if the address is a bounce buffer, they copy/sync and free slots. Dynamic configurations can find pools through `__swiotlb_find_pool()` after checking `dev->dma_uses_io_tlb` with a read barrier.

## State and persistence behavior

Pool state persists for the boot lifetime or until dynamic pool teardown. Slot and area metadata track allocation. Device state lives in `dev->dma_io_tlb_mem` and `dev->dma_uses_io_tlb`. Debug counters track current and high-water usage. Bounce buffers contain transient copies of DMA data.

## Dependencies and integration points

It depends on device DMA metadata, DMA direction enums, init, spinlocks, workqueues, RCU/list support for dynamic pools, and optional debugfs/restricted DMA pool configs. It integrates with DMA direct/IOMMU paths, memory encryption, confidential computing, and restricted DMA pool allocation.

## Risks and test signals

Risks include missing syncs causing data corruption, pool lookup races without barriers, wrong direction handling, insufficient pool size, dynamic pool lifetime bugs, restricted-pool null dereferences, and assuming SWIOTLB is active in stub builds. Tests should cover mapping/unmapping in all DMA directions, forced bounce, addressing-limited devices, dynamic pool growth/free, encrypted memory remapping, restricted pool allocation, debugfs counters, and CONFIG_SWIOTLB disabled stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/swiotlb.h -->
