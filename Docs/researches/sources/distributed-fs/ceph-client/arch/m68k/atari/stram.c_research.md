# sources/distributed-fs/ceph-client/arch/m68k/atari/stram.c

Purpose: allocator for Atari ST-RAM, needed by hardware that can only DMA to the low ST-RAM region.

Important APIs are `atari_stram_init()`, `atari_stram_reserve_pages()`, `atari_stram_to_virt()`, `atari_stram_to_phys()`, `atari_stram_alloc()`, and `atari_stram_free()`. The early parameter `stram_pool=` sets the pool size, defaulting to 1 MiB.

Control flow determines whether the kernel is loaded in ST-RAM by checking the first memory block. If so, `atari_stram_reserve_pages()` uses `memblock_alloc_low()` early and requests the resource. If the kernel is not in ST-RAM, `atari_stram_map_pages()` later reserves a physical pool starting at page 1 and maps it with `ioremap()`, computing a virtual offset. Alloc/free use `allocate_resource()` and `lookup_resource()` inside `stram_pool`.

State includes `kernel_in_stram`, `stram_pool`, `pool_size`, and `stram_virt_offset`. Resource entries track individual allocations.

Dependencies include `m68k_memory`, memblock, ioremap, resource management, Atari hardware assumptions, and exported symbols for DMA-constrained drivers.

Risks and test signals: the non-kernel-in-ST-RAM path skips page 0 because early memory is supervisor-only; wrong offset translation breaks DMA. Test both boot placement modes, `stram_pool=` parsing, allocate/free accounting, and drivers requiring ST-RAM buffers.
