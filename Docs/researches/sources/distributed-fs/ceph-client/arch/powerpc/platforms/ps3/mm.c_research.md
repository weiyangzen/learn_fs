## sources/distributed-fs/ceph-client/arch/powerpc/platforms/ps3/mm.c

### Purpose
`mm.c` manages PS3 LV1 virtual address spaces, high memory regions, physical-to-LPAR translation, and PS3 DMA/IOMMU region mapping for system-bus and IOC0 devices.

### Important APIs, Types, And Functions
Core types are `struct map`, `struct mem_region`, and `struct dma_chunk`. Important APIs are exported `ps3_mm_phys_to_lpar()`, `ps3_mm_vas_create()`, `ps3_mm_vas_destroy()`, `ps3_mm_init()`, `ps3_mm_shutdown()`, `ps3_dma_region_init()`, `ps3_dma_region_create()`, `ps3_dma_region_free()`, `ps3_dma_map()`, and `ps3_dma_unmap()`. Internal ops implement SB dynamic/linear DMA and IOC0 IOPTE mappings.

### Control Flow
Early memory init reads repository RAM info, restores or allocates one highmem LV1 region, records it in the repository when enabled, adjusts total memory, and adds highmem to memblock. VAS creation queries LV1 address region capabilities, constructs/selects a virtual address space with configured HTAB size and large page support, and returns the HTAB size. DMA init chooses operation tables by device type and config. Dynamic SB DMA allocates LV1 DMA regions and maps chunks on demand; linear SB maps RAM up front; IOC0 allocates IO segments and writes IOPTEs per page.

### State, Persistence, And Dependencies
Global `map` persists real memory, high memory, VAS id, and HTAB size. DMA regions persist bus address, page size, chunk lists, locks, and device references. Dependencies include LV1 memory/VAS/DMA/IOPTE calls, repository highmem helpers, memblock, Cell IOPTE flags, and Linux DMA mask APIs.

### Integration Points
HTAB code uses `ps3_mm_phys_to_lpar()` and memory teardown. Device registration initializes DMA regions for system-bus and IOC0 devices, and PS3 drivers use map/unmap wrappers.

### Risks
The implementation assumes one highmem region and real memory base zero. Dynamic DMA chunk overlap logic BUGs on multi-chunk overlaps. IOC0 mapping has FIXME comments around length limits and reuse. Kexec teardown runs with MMU off and calls panic on LV1 cleanup failures.

### Test Signals
Boot memory map, highmem repository restore/create, kexec/kdump cleanup, SB and IOC0 DMA map/unmap stress, dynamic vs linear DMA configs, and large-page boundary cases validate behavior.
