# sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_cmdbuf.c

## Purpose
Implements a write-combined DMA command buffer suballocator used by etnaviv kernel ring buffers and submitted command buffers.

## Important APIs, Types, and Functions
Defines private `struct etnaviv_cmdbuf_suballoc` with DMA address, CPU mapping, granule bitmap, mutex, waitqueue, and free-space flag. Exports allocation/lifetime (`etnaviv_cmdbuf_suballoc_new/destroy`), IOMMU map/unmap, per-cmdbuf allocation/free, and VA/PA translation helpers.

## Control Flow
The suballocator allocates a 512 KiB DMA WC region split into 4 KiB granules. `etnaviv_cmdbuf_init()` computes a power-of-two region order, finds a free bitmap region, waits up to 10 seconds if none is available, and returns a CPU pointer at the suballocation offset. Free releases the bitmap region and wakes waiters. Mapping delegates to etnaviv IOMMU suballoc VA helpers.

## State and Persistence
The DMA WC allocation persists for the DRM device lifetime. Individual cmdbufs persist until `etnaviv_cmdbuf_free`. Bitmap state tracks granule ownership; `free_space` is a wakeup hint.

## Dependencies and Integration Points
Created in `etnaviv_bind`, mapped into IOMMU contexts, used by GPU ring setup, submit path, and flop reset payload allocation. Depends on DMA mapping APIs and etnaviv MMU helpers.

## Risks
Power-of-two bitmap allocation can fragment capacity. Timeout waiting for space indicates leaked or long-lived command buffers. Missing free causes submit stalls. DMA mask assumptions are enforced in platform probe.

## Test Signals
High-concurrency submit stress, timeout logs, IOMMU mapping validation, command buffer VA/PA debug output, and leak checks around submit completion are useful.
