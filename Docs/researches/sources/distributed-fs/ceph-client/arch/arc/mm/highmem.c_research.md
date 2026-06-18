# sources/distributed-fs/ceph-client/arch/arc/mm/highmem.c

Purpose: initializes ARC highmem permanent and temporary mapping page tables.

Important APIs/functions: `kmap_init()` validates address-space constraints and allocates page tables for `PKMAP_BASE` and `FIXMAP_BASE`. `alloc_kmap_pgtable()` allocates a low memory PTE page with memblock and installs it into the kernel PMD.

Control flow: during memory setup, `kmap_init()` checks that vmalloc/fixmap/pkmap fit below `PAGE_OFFSET`, that `LAST_PKMAP` and `FIX_KMAP_SLOTS` fit in one PTE page, then creates dedicated page tables.

State and persistence: initializes global `pkmap_page_table` and kernel page-table entries in `init_mm`. Allocated PTE pages persist for kernel lifetime.

Dependencies and integration: depends on generic highmem/pkmap/fixmap infrastructure, ARC memory layout constants, memblock, page-table allocation helpers, and TLB flushing expectations.

Risks: ARC shares the 0x7z-0x8z kernel virtual range between vmalloc and kmap; mis-sized regions can overlap. The generic pkmap code assumes a single `pkmap_page_table`, limiting concurrent permanent maps.

Test signals: highmem boot, kmap/kmap_local stress, fixmap use, vmalloc coexistence, multi-CPU kmap slots, and build-time assertions.
