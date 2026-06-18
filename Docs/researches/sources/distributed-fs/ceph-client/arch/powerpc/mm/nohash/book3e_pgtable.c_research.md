# sources/distributed-fs/ceph-client/arch/powerpc/mm/nohash/book3e_pgtable.c

Purpose: implements Book3E nohash kernel page-table mapping helpers and vmemmap mapping for sparse memory.

Important APIs and control flow: `vmemmap_create_mapping()` writes repeated PTEs with the configured vmemmap page-size encoding. `early_alloc_pgtable()` allocates low DMA-reachable page-table pages through memblock before slab. `map_kernel_page()` walks or allocates PGD/P4D/PUD/PMD/PTE levels using slab allocators after boot or memblock before boot, installs the PTE, and issues a write barrier. `__patch_exception()` patches the second instruction of an exception vector branch to preserve single-step semantics.

State and dependencies: state is kernel page-table contents and optional vmemmap mappings. Dependencies include Book3E page-size encodings, memblock, generic page-table allocators, text patching, sparsemem, and interrupt vector symbols. Risks are page-size encoding overflow, early allocation outside accessible memory, missing synchronization after mapping, and incorrect exception branch patch offsets. Test signals include early ioremap users, vmemmap population, memory hotplug builds, exception vector patching, and Book3E64 boot.
