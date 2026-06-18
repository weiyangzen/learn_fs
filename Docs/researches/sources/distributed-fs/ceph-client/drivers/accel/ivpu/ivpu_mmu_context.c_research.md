<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_mmu_context.c -->
## sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_mmu_context.c

### Purpose
`ivpu_mmu_context.c` manages per-context VPU virtual address spaces. It allocates and frees four-level page tables, maps and unmaps scatter-gather tables into VPU addresses, changes page permissions, manages VPU virtual address ranges with `drm_mm`, and initializes global/reserved/user contexts.

### Important APIs, Types, And Functions
Public APIs include `ivpu_mmu_context_init()`, `ivpu_mmu_context_fini()`, global and reserved context init/fini helpers, `ivpu_mmu_context_insert_node()`, `ivpu_mmu_context_remove_node()`, `ivpu_mmu_context_map_sgt()`, `ivpu_mmu_context_unmap_sgt()`, and `ivpu_mmu_context_set_pages_ro()`. Internal helpers lazily ensure PGD/PUD/PMD/PTE pages, map 4K or contiguous 64K pages, split contiguous mappings, set read-only bits, and free nested page-table allocations.

### Control Flow
Mapping validates context, page alignment, and 48-bit VPU address range, builds protection bits, locks the context, walks each DMA scatterlist segment, maps pages using 64K contiguous entries when aligned and enabled, checks the scatterlist covers the BO size exactly, installs the context descriptor on first map, flushes write-combining buffers, unlocks, and invalidates the TLB. Unmapping clears PTEs to a dummy invalid physical address and invalidates the TLB. Read-only conversion optionally splits boundary 64K contiguous mappings, sets RO bits over the range, flushes, and invalidates.

### State, Persistence, And Dependencies
Each `struct ivpu_mmu_context` owns a mutex, `drm_mm`, `struct ivpu_mmu_pgtable`, CD-valid flag, and SSID. Page tables are highmem pages mapped write-combining and DMA-mapped bidirectionally. Dependencies include DRM MM address allocation, DMA mapping, vmalloc/vmap, cache attribute changes, `ivpu_mmu_cd_set()/clear()`, and hardware address ranges from `vdev->hw`.

### Integration Points
GEM BO binding uses this layer to map BO scatter-gather memory before job submission. File contexts use user/dma/shave ranges; the global context covers runtime through shave ranges; the reserved context installs an empty root table to deliberately fault reserved accesses. `ivpu_mmu.c` consumes page-table roots via context descriptors and handles TLB invalidation.

### Risks
Partial-map error handling unmaps only the accumulated SG size and relies on page table structures remaining valid. Contiguous 64K mappings must be split before partial RO conversion or permissions can affect neighboring pages. Page-table allocation uses nested pointer arrays sized as page-table entry counts; allocation failures must unwind correctly. TLB invalidation failures after unmap are warning-only, which can leave stale translations until a later invalidation or reset.

### Test Signals
Exercise small and large BO maps, unaligned VPU address rejection, scatterlist too-small/too-large rejection, 64K contiguous page mapping and disabled-contiguous mode, read-only conversion at aligned and unaligned-within-64K boundaries, context teardown after partial failure, reserved context fault behavior, and repeated runtime suspend/resume with existing contexts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_mmu_context.c -->
