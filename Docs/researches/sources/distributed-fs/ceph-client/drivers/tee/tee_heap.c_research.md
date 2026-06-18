<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/tee_heap.c -->
# sources/distributed-fs/ceph-client/drivers/tee/tee_heap.c

## Purpose

`tee_heap.c` implements optional DMA-BUF heap support for TEE protected memory and a static protected-memory pool implementation. It lets TEE drivers expose named protected DMA heaps and translate DMA-BUF allocations back into `tee_shm` objects for secure-world sharing.

## Important APIs, Types, and Functions

When `CONFIG_TEE_DMABUF_HEAPS` is enabled, `struct tee_dma_heap` tracks a heap ID, kref, protected memory pool, owning `tee_device`, shutdown state, and mutex. `struct tee_heap_buffer` stores exported buffer size, pool offset, scatter-gather table, and heap pointer. DMA-BUF ops include `tee_heap_attach()`, `tee_heap_detach()`, `tee_heap_map_dma_buf()`, `tee_heap_unmap_dma_buf()`, and `tee_heap_buf_free()`. `tee_dma_heap_alloc()` allocates from the protected pool and exports a DMA-BUF.

Exported APIs are `tee_device_register_dma_heap()`, `tee_device_put_all_dma_heaps()`, and `tee_heap_update_from_dma_buf()`. Static protected-memory APIs include `tee_protmem_static_pool_alloc()` and ops for alloc/free/update/destroy backed by `gen_pool`.

## Control Flow

A TEE driver registers a protected-memory pool under a known heap ID. The first registration creates a named DMA heap such as `protected,secure-video`; later registrations can reuse a heap entry after shutdown cleared its device pointer. Userspace allocates DMA-BUFs from that heap, and `tee_dma_heap_alloc()` gets a heap reference, allocates protected memory into an SG table, exports a DMA-BUF, and drops the heap reference when the DMA-BUF is released. Registering a DMA-BUF as TEE shared memory calls `tee_heap_update_from_dma_buf()`, which verifies the DMA-BUF ops and owning device, then asks the pool to fill the `tee_shm` physical/security fields.

## State and Persistence Behavior

State is runtime-only in a global xarray keyed by `enum tee_dma_heap_id`, per-heap krefs and shutdown flags, and per-DMA-BUF SG tables. Static protected pools keep a gen_pool and base physical address until destroyed. Device unregister calls `tee_device_put_all_dma_heaps()` to mark matching heaps shutting down and drop the device/pool reference when no buffers remain.

## Dependencies and Integration Points

This file depends on DMA-BUF heap APIs, scatterlist and DMA mapping helpers, xarray, kref, gen_pool, and TEE protected-memory pool interfaces from `tee_core.h`. It integrates with `tee_shm.c` through `tee_shm_register_fd()` and `tee_heap_update_from_dma_buf()`, and with generic TEE device unregister in `tee_core.c`.

## Risks and Edge Cases

The disabled-config stubs return `-EINVAL`, so callers must degrade cleanly when DMA-BUF heaps are not built. Heap reuse after shutdown depends on mutex-protected `teedev` and `pool` replacement; leaked DMA-BUFs keep the old pool alive through krefs. `tee_heap_update_from_dma_buf()` rejects DMA-BUFs not produced by this exact ops table and from other TEE devices, which is correct but can surprise cross-device users. Static pool allocation does not round the requested size before `gen_pool_alloc()`, so callers/pools must provide appropriate sizes. Protected memory may be inaccessible to the kernel while lent to TEE, so CPU mappings and DMA sync assumptions must remain constrained.

## Test Signals

Tests should cover heap registration, duplicate registration, unregister while buffers are open, DMA-BUF allocate/export/release, attach/map/unmap/detach on multiple devices, `tee_shm_register_fd()` for valid and invalid DMA-BUFs, static pool alignment and PFN validation, pool exhaustion, and disabled `CONFIG_TEE_DMABUF_HEAPS` behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/tee_heap.c -->
