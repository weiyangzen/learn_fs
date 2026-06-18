# sources/distributed-fs/ceph-client/arch/powerpc/mm/kasan/init_book3s_64.c

Purpose: initializes KASAN for 64-bit Book3S PowerPC, restricted to radix MMU.

Important APIs and control flow: `kasan_init()` exits with a warning if early radix is not enabled. Otherwise it maps shadow backing for each physical memblock through `map_kernel_page()`, rebuilds early shadow PTE/PMD/PUD tables, maps early zero shadow over iomap and vmemmap shadow ranges, remaps the zero page read-only, clears it with `memset()`, enables reporting through `init_task.kasan_depth`, and calls generic KASAN init. Early and late hooks are empty because Book3S64 enables virtual memory late.

State and dependencies: state includes radix kernel page tables, early shadow page/table arrays, memblock allocations, and generic KASAN state. It depends on radix address layout constants, `map_kernel_page()`, `kasan_populate_early_shadow()`, and memblock ranges. Risks are silently disabled KASAN on hash, incorrect shadow range boundaries around vmalloc/vmemmap, and cache-info sensitivity during early clear. Test signals include Book3S64 radix KASAN boot, hash warning behavior, KASAN vmalloc tests, and physical memblock shadow coverage.
