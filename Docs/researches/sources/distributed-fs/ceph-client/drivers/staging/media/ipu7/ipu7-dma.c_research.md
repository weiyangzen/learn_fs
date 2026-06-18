# sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-dma.c

## Purpose

This file implements IPU7 DMA/IOMMU helpers that allocate coherent-ish shared buffers, map scatterlists into the IPU IOVA space, synchronize caches, mmap allocated buffers to userspace, and free/unmap IOVAs.

## Important APIs, Types, and Functions

Public APIs are `ipu7_dma_alloc()`, `ipu7_dma_free()`, `ipu7_dma_mmap()`, `ipu7_dma_map_sg()`, `ipu7_dma_unmap_sg()`, sgtable wrappers, and cache sync helpers. Internal `struct vm_info` tracks allocated pages, IPU IOVA, virtual mapping, and size. Helpers allocate/free page arrays and locate `vm_info` by IOVA.

## Control Flow

Allocation reserves an IOVA, allocates/splits pages, zeroes and optionally flushes them, maps each page for PCI DMA, maps PCI DMA addresses into IPU MMU, vmaps pages, records `vm_info`, and returns CPU virtual address plus IPU DMA handle. Free reverses the process: find IOVA/vm info, remove list entry, vunmap, unmap PCI DMA and IPU MMU, clear/free pages, invalidate TLB, free IOVA, and free metadata. SG mapping validates zero offsets, counts pages, allocates or reserves an IOVA region, maps each SG DMA address into IPU MMU, then rewrites SG DMA addresses to IPU IOVAs; unmap restores PCI DMA addresses from MMU translations before unmapping.

## State and Persistence Behavior

Allocated buffers persist in `mmu->vma_list` until freed. IOVAs are allocated from `mmu->dmap->iovad`; IPU MMU mappings persist until explicit unmap and TLB invalidation.

## Dependencies and Integration Points

It depends on Linux DMA mapping, IOVA allocator, scatterlists, vmalloc/vmap, cache flushing, and IPU7 MMU helpers. Boot/syscom and ISYS config use `ipu7_dma_alloc()`; video queues use SG mapping.

## Risks and Edge Cases

Manual page/IOVA bookkeeping is delicate. Several invalid-state `WARN_ON()` paths return early in free and can leak if state is inconsistent. SG entries with non-zero offsets are unsupported. `ipu7_dma_map_sg()` returns `0` for allocation failure, following DMA map convention but requiring callers to treat zero as failure. Reserved firmware code region mapping is special.

## Test Signals

Stress allocate/free, partial allocation failure, mmap, SG map/unmap with multi-page buffers, non-zero offset rejection, reserved firmware region mapping, TLB invalidation, and cache sync visibility to firmware.
