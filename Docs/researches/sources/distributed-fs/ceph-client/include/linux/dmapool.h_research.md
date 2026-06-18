# sources/distributed-fs/ceph-client/include/linux/dmapool.h

## Purpose
This header declares DMA-coherent memory pool APIs for allocating many fixed-size DMA-able objects such as descriptors. It provides both explicit lifetime and device-managed variants.

## Important APIs, types, and functions
The main API is `dma_pool_create_node()`, `dma_pool_create()`, `dma_pool_destroy()`, `dma_pool_alloc()`, `dma_pool_zalloc()`, and `dma_pool_free()`. Managed variants are `dmam_pool_create()` and `dmam_pool_destroy()`. `struct dma_pool` is opaque.

## Control flow, state, and persistence
Pool state is owned by the implementation. Creation binds a pool to a device, object size, alignment, boundary, and NUMA node. Allocation returns a CPU virtual address plus DMA address handle; free requires both the virtual address and DMA address. Managed pools persist until explicit managed destroy or device resource release.

## Dependencies and integration points
It depends on NUMA node definitions, scatterlist declarations, and I/O mapping headers. It is consumed by DMA controller, USB, network, and storage drivers that need coherent descriptor memory.

## Risks and test signals
When `CONFIG_HAS_DMA` is disabled all creation/allocation helpers become no-op stubs returning `NULL`, so callers must handle failure. Tests should verify alignment and boundary guarantees, zeroing through `dma_pool_zalloc()`, freeing with matching handles, and device-managed cleanup on driver detach.
