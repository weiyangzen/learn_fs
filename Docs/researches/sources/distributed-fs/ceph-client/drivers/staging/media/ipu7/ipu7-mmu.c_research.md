# sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-mmu.c

## Purpose
Implements the IPU7 MMU/IOMMU page-table management and hardware initialization used by IPU child devices. It builds a two-level 4 KiB page-table hierarchy, maps and unmaps IOVA ranges, programs MMU/ZLX hardware blocks, invalidates TLBs, manages a trash-buffer IOVA range, and creates/destroys DMA mapping domains.

## Important APIs, Types, and Functions
Exported functions are `ipu7_mmu_hw_init()`, `ipu7_mmu_hw_cleanup()`, `ipu7_mmu_iova_to_phys()`, `ipu7_mmu_map()`, `ipu7_mmu_unmap()`, `ipu7_mmu_init()`, and `ipu7_mmu_cleanup()`. Important internals include `tlb_invalidate()`, dummy page/table allocation, `l2_map()`, `l2_unmap()`, `allocate_trash_buffer()`, `__mmu_at_init()`, `__mmu_zlx_init()`, `ipu7_mmu_alloc()`, `alloc_dma_mapping()`, and `ipu7_mmu_destroy()`.

## Control Flow
Initialization validates hardware variants, copies MMU block descriptors with MMIO base offsets, allocates an IOVA domain and `ipu7_mmu_info`, creates a dummy page, dummy L2 table, L1 table initialized to dummy L2, and per-L1 L2 pointer array. Runtime hardware init writes page-table base, user info bits, refill/collapse/ZLX configuration, TLB stream block sizes, UAO plane mappings, IRQ masks, allocates/maps the trash range if needed, and marks the MMU ready. Mapping validates alignment, allocates L2 tables on first use, maps them for DMA, writes L1/L2 PTEs, and flushes cache lines. Unmapping resets L2 entries to dummy page PTEs. TLB invalidation writes invalidate registers and polls completion while `ready` is true.

## State and Persistence Behavior
`ipu7_mmu_info` owns software page tables, dummy PTEs, aperture bounds, pgsize bitmap, lock, and DMA mapping backpointer. `ipu7_mmu` owns copied hardware descriptors, MMID, DMA mapping, trash page DMA/IOVA, ready flag/lock, and invalidate callback. Hardware register state persists between runtime PM init/cleanup; software tables persist until `ipu7_mmu_cleanup()`.

## Dependencies and Integration Points
Depends on PCI DMA mapping, Linux IOVA allocator, cache flushing, register constants from `ipu7-mmu.h`, platform secure-mode firmware address limits, and IPU DMA integration. ISYS runtime resume calls `ipu7_mmu_hw_init()` and suspend calls `ipu7_mmu_hw_cleanup()`.

## Risks and Test Signals
Risks include error unwind in `l2_map()` using adjusted `iova/paddr`, `ipu7_mmu_iova_to_phys()` assuming an allocated L2 table, cache coherency of page-table writes, trash-buffer cleanup correctness, and no explicit TLB invalidation inside map/unmap paths unless callers invoke the callback. Test aligned/unaligned map and unmap, crossing L1 boundaries, allocation failure unwind, secure vs non-secure apertures, runtime PM init/cleanup loops, TLB invalidate timeout logging, and IOVA-to-physical lookups for dummy/unmapped ranges.
