<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma-map-ops.h -->
# sources/distributed-fs/ceph-client/include/linux/dma-map-ops.h

## Purpose
Defines internal DMA mapping operation hooks and helpers for architecture and DMA core implementations. It is not intended for normal drivers using the public DMA API.

## Important APIs, Types, And Functions
`struct dma_map_ops` defines allocation, free, map/unmap phys and SG, sync, mmap, sgtable, mask, mapping-size, and merge-boundary callbacks. The header also declares `get_dma_ops()`, `set_dma_ops()`, CMA helpers, declared/global coherent memory helpers, common mmap/sgtable/remap/page helpers, DMA pool helpers, direct offset setup, coherence helpers, kmalloc DMA-safety helpers, architecture allocation/sync hooks, setup/teardown hooks, DMA debug hooks, and `dma_dummy_ops`.

## Control Flow
The public DMA API resolves per-device or architecture DMA ops, then calls these callbacks or direct/common helpers. Optional configuration blocks compile in CMA, declared coherent memory, global pools, architecture cache sync, direct map overrides, and debug tracing.

## State And Persistence
State includes per-device `dma_ops`, CMA areas, declared coherent pools, global coherent pools, device coherence flags, DMA skip-sync state, and debug mapping tables. It is runtime kernel/platform state.

## Dependencies And Integration Points
Depends on DMA mapping public API, page tables, slab alignment, CMA, architecture hooks, coherent memory pools, and DMA debug. It is the integration point between generic DMA code, IOMMUs, SWIOTLB, and arch-specific cache maintenance.

## Risks And Edge Cases
Normal drivers must not include this header. Non-coherent DMA with unaligned kmalloc buffers can corrupt adjacent cachelines; the bounce heuristics must be respected. Coherent pool fallbacks differ by config. Arch sync hooks may be no-ops on coherent systems. Setup/teardown ordering matters for hotplugged devices.

## Test Signals
Tests should cover builds with and without arch DMA ops, CMA allocation/free, declared/global coherent memory, non-coherent cache sync, kmalloc bounce heuristics, DMA debug mapping dumps, direct-map overrides, and device DMA ops setup/teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma-map-ops.h -->
