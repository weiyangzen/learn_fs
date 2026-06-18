# sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-dma.c

## Purpose
This file provides IPU6 DMA allocation, mmap, SG mapping, unmapping, and cache synchronization. It bridges normal PCI DMA addresses into IPU6 IOVA space through the IPU6 MMU and tracks vmapped allocations so CPU, PCI DMA, and firmware-visible addresses remain correlated.

## Important APIs, types, and functions
`struct vm_info` tracks vmapped pages, IPU6 IOVA, virtual address, size, and list linkage. `ipu6_dma_alloc()` allocates pages, allocates an IOVA range, maps each page for PCI DMA, maps each PCI DMA address into IPU6 MMU, vmap()s pages, and records state. `ipu6_dma_free()` reverses that mapping and invalidates the IPU6 TLB. `ipu6_dma_map_sg()` converts an already PCI-DMA-mapped scatterlist to contiguous IPU6 IOVA entries, while `ipu6_dma_unmap_sg()` restores PCI DMA addresses and unmaps the IPU6 MMU. Sync helpers flush CPU cache ranges; `ipu6_dma_mmap()` inserts allocated pages into userspace VMAs.

## Control flow and integration points
Firmware communication, CPD package directories, firmware image mapping, and ISYS capture queues call these helpers to get firmware-visible memory. SG users first map through generic DMA APIs, then call IPU6 DMA mapping to rewrite SG DMA addresses into IPU6 IOVAs. Free/unmap paths must restore mappings before generic DMA unmap.

## State, persistence, and dependencies
State lives in `mmu->vma_list`, `mmu->dmap->iovad`, and the IPU6 MMU page tables. Dependencies include Linux IOVA allocation, page allocation, vmap/vunmap, cache flushing, scatterlists, PCI DMA APIs, and `ipu6_mmu_map()/unmap()/iova_to_phys()`.

## Risks and test signals
Risks are leaked IOVAs or pages on partial failures, stale cache lines when firmware reads host buffers, unsupported non-zero SG offsets, SG address restoration bugs, TLB invalidation omissions, and mismatched rounded sizes. Test signals include allocation/free stress, SG map/unmap round trips, mmap validation, firmware queue operation, IOMMU fault absence, KASAN/KMEMLEAK runs, and capture buffers surviving queue churn.
