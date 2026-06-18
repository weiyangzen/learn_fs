# sources/distributed-fs/ceph-client/kernel/dma/coherent.c

## Purpose
This file implements reserved coherent DMA memory pools, both per-device and optional global pools. It lets platform or device-tree code declare memory regions that `dma_alloc_coherent()` can allocate from, and supports freeing and mmap of allocations from those pools.

## Important APIs, Types, And Functions
`struct dma_coherent_mem` stores virtual base, device DMA base, PFN base, page count, bitmap, spinlock, and whether device DMA PFN offset should be used. Public APIs include `dma_declare_coherent_memory()`, `dma_release_coherent_memory()`, `dma_alloc_from_dev_coherent()`, `dma_release_from_dev_coherent()`, `dma_mmap_from_dev_coherent()`, and optional global-pool helpers. Device-tree hooks are `rmem_dma_setup()`, `rmem_dma_device_init()`, and `rmem_dma_device_release()`.

## Control Flow
Initialization remaps the physical range with write-combining attributes, allocates a bitmap, and assigns the pool to a device or global pointer. Allocation finds a free bitmap region of the requested order under a spinlock, computes DMA and CPU addresses, unlocks, and zeroes memory. Release validates the virtual address range and releases the bitmap region. Mmap checks that the requested VMA fits inside the allocation before calling `remap_pfn_range()`. Reserved-memory setup rejects reusable pools and records `linux,dma-default` for global coherent memory when configured.

## State, Persistence, And Dependencies
Per-device state is `dev->dma_mem`; global state is `dma_coherent_default_memory` and early reserved-memory base/size. Pool allocation state is a bitmap protected by a spinlock. Dependencies include memremap/memunmap, bitmap allocation, device DMA masks, `phys_to_dma()`, reserved-memory OF hooks, and VMA remapping.

## Integration Points
Direct DMA allocation and mmap paths consult these helpers before falling back to generic pages. Device tree `shared-dma-pool` regions bind devices to coherent pools through reserved memory ops. `CONFIG_DMA_GLOBAL_POOL` provides a default pool for non-coherent direct allocations.

## Risks
Only one coherent pool can be assigned to a device. Pool size is stored as an `int` number of pages. Range checks must prevent mmap outside the pool. Reserved memory beyond a device mask only warns, so a misconfigured platform can still fail later. Global pool initialization depends on early reserved-memory discovery order.

## Test Signals
Test per-device declare/allocate/free/mmap/release, overlapping double assignment returning `-EBUSY`, allocation exhaustion, device mask warnings, global `linux,dma-default`, and reserved-memory attach/detach.
