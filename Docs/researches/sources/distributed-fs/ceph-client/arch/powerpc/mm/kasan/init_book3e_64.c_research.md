# sources/distributed-fs/ceph-client/arch/powerpc/mm/kasan/init_book3e_64.c

Purpose: initializes KASAN shadow mappings for 64-bit Book3E PowerPC.

Important APIs and control flow: `kasan_early_init()` builds shared early PTE/PMD/PUD tables pointing all shadow to the early zero page. `kasan_map_kernel_page()` lazily copies early shared tables into private page-table pages before installing a real shadow PTE. `kasan_init_phys_region()` allocates backing pages for each physical memory shadow range. `kasan_init()` maps all memblocks, removes vmalloc zero shadow when enabled, remaps the early shadow page read-only, flushes the shadow TLB range, zeroes the early page, and enables generic KASAN.

State and dependencies: persistent state is page-table content under `init_mm`, early shadow table pages, and memblock-allocated shadow backing. It depends on Book3E page-table geometry, `memblock_alloc_or_panic()`, KASAN vmalloc helpers, and TLB flushing. Risks include failing to break shared early tables before writes, shadow holes for discontiguous memory, and writeable early shadow after init. Test signals include Book3E64 KASAN boot, vmalloc KASAN, sparse memblock layouts, and early fault detection.
