# sources/distributed-fs/ceph-client/arch/powerpc/mm/init_32.c

Purpose: performs 32-bit PowerPC MMU initialization, lowmem sizing, linear RAM mapping, early ioremap base setup, KASAN setup, and KUP enablement.

Important APIs and control flow: `MMU_init()` computes `total_memory`, `total_lowmem`, and `lowmem_end_addr` from memblock and `memstart_addr`; allows e500 to reduce lowmem to CAM coverage; enforces configured lowmem limits; calls `MMU_init_hw()`, `mapin_ram()`, initializes `ioremap_bot`, unmaps boot text if applicable, runs `kasan_mmu_init()`, enables KUP, patches MMU feature fixups, and raises the memblock allocation limit to mapped lowmem.

State and dependencies: state includes `total_memory`, `total_lowmem`, `lowmem_end_addr`, `__max_low_memory`, `boot_mapsize`, optional `virt_phys_offset`, and `agp_special_page`. It depends on platform progress callbacks, nohash/hash-specific `MMU_init_hw()` and `mapin_ram()`, memblock limits, KASAN, KUP, and feature fixup patching. Risks are mapping less memory than later allocators assume, wrong highmem enforcement, e500 CAM mis-sizing, and KASAN/KUP ordering regressions. Test signals are 32-bit boots across 8xx/44x/e500/book3s, highmem configs, relocatable kernels, and early ioremap warnings.
