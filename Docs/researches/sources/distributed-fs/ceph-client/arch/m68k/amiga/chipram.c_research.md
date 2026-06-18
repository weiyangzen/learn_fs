# sources/distributed-fs/ceph-client/arch/m68k/amiga/chipram.c

Purpose: resource-managed allocator for Amiga Chip RAM, the DMA-visible memory required by custom chips.

Important APIs are `amiga_chip_init()`, `amiga_chip_alloc()`, `amiga_chip_alloc_res()`, `amiga_chip_free()`, and `amiga_chip_avail()`. `amiga_chip_init()` creates a `chipram_res` range from `CHIP_PHYSADDR` through `amiga_chip_size`, attaches it to `iomem_resource`, and initializes the atomic available count. Allocations are page-aligned and use `allocate_resource()`; returns are converted through `ZTWO_VADDR()`.

State is `amiga_chip_size`, the `chipram_res` resource tree, and atomic `chipavail`. Allocations made with caller-owned resources may be permanent during early boot; `amiga_chip_alloc()` allocates a `struct resource` that can later be freed.

Dependencies include `amigahw` presence bits, `iomem_resource`, Zorro II address translation macros, resource management, and slab allocation. Integration supports audio waveform memory, framebuffer/video, and drivers requiring Chip RAM before or after normal allocation is available.

Risks and test signals: freeing an untracked pointer is reported and ignored; early permanent allocations intentionally cannot always be freed. Off-by-one resource ranges or wrong physical/virtual translation would break DMA. Test with Amiga boot hardware list, repeated allocate/free calls from a driver, and `amiga_chip_avail()` accounting.
