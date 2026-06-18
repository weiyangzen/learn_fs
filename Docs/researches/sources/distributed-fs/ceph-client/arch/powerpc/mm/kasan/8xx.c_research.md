# sources/distributed-fs/ceph-client/arch/powerpc/mm/kasan/8xx.c

Purpose: provides 8xx-specific KASAN shadow population optimized for 8 MiB, 512 KiB, and 16 KiB mapping capabilities.

Important APIs and control flow: `kasan_init_region()` allocates shadow backing with 8 MiB alignment, maps aligned portions through `kasan_init_shadow_8M()`, falls back to generic shadow page-table initialization for the tail, writes huge or base PTEs, and flushes the kernel TLB range. `kasan_init_shadow_8M()` replaces early shadow PMDs with real PTE pages and marks PMDs as 8 MiB huge mappings.

State and dependencies: state is page-table mappings under `init_mm` and memblock-allocated backing memory. It depends on `kasan_mem_to_shadow()`, early shadow PTE detection, `pte_mkhuge()`, 8xx huge PTE encodings, and TLB flushes. Risks are alignment mistakes around 8 MiB boundaries, partially populated shadow if allocation fails, and stale early shadow aliases. Test signals include 8xx KASAN boot, shadow coverage for lowmem ranges, KASAN fault reports, and TLB flush validation.
