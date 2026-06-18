# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/selftests/mock_dmabuf.c

## Purpose
Implements an in-memory dma-buf exporter so i915 PRIME import tests can run without another real driver.

## APIs And Control Flow
Defines dma-buf ops for map/unmap, release, vmap/vunmap, and unsupported mmap, plus factory `mock_dmabuf()`. The factory allocates a flexible private object and pages, exports a dma-buf, and stores the private data in `exp_info.priv`. Mapping builds an sg table over pages and calls `dma_map_sgtable()`. Vmap uses `vm_map_ram()`; release drops pages.

## State, Dependencies, Integration, Risks, And Tests
State persists in dma-buf private `struct mock_dmabuf` until release. Dependencies include dma-buf ops, scatterlists, DMA mapping, page allocation, and vmalloc mapping. Used by `i915_gem_dmabuf.c`. Risks are cleanup on partial allocation/map failure and the intentionally unsupported mmap contract. Signals are export/map/vmap failures and PRIME memory-pattern mismatches.
