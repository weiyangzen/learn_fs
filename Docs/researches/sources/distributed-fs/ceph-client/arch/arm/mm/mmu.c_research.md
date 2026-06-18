## sources/distributed-fs/ceph-client/arch/arm/mm/mmu.c

### Purpose
Builds ARM MMU memory type tables, early and final kernel mappings, fixmaps, vectors, lowmem/kernel mappings, device/static IO mappings, and page-table setup for boot.

### Important APIs, Types, And Functions
Important globals are `top_pmd`, `user_pmd_table`, `pgprot_user`, `pgprot_kernel`, `mem_types`, `protection_map`, `vmalloc_size`, and `arm_lowmem_limit`. Major functions include `init_default_cache_policy`, early params `cachepolicy/nocache/nowb/ecc/vmalloc`, `get_mem_type`, `early_fixmap_init`, `__set_fixmap`, `build_mem_type_table`, mapping builders `alloc_init_*`, `create_mapping_late`, `iotable_init`, `vm_reserve_area_early`, `adjust_lowmem_bounds`, `arm_mm_memblock_reserve`, `devicemaps_init`, `kmap_init`, `map_lowmem`, `map_kernel`, `early_paging_init`, `early_fixmap_shutdown`, `paging_init`, `early_mm_init`, and `set_ptes`.

### Control Flow
Early MM init derives memory/cache attributes from CPU architecture, cache policy, SMP, TEX remap, LPAE, domains, ECC, and initial PMD attributes. Boot then adjusts lowmem/vmalloc bounds, clears unsafe page-table regions, maps lowmem around kernel sections, maps executable and non-executable kernel sections, remaps DMA/CMA regions, converts early fixmap entries to normal mappings, maps vectors/FDT/cache-flush regions/platform IO, initializes kmap/fixmap PTEs, and finishes bootmem. `set_ptes` synchronizes I/D cache for user executable mappings and marks user PTEs non-global.

### State, Dependencies, And Integration
Persistent state includes memory type/protection tables, top PMD pointer, vmalloc sizing, and lowmem limit. Depends on memblock, machine descriptors, fixmap, page-table allocation, CPU/cache type detection, FDT/ATAGS, TCM, DMA contiguous remap, KASAN-aware layout, and fault early abort enabling. Integrates with nearly every ARM MM path: ioremap, DMA, page faults, mmap, modules, vectors, and strict permissions.

### Risks And Test Signals
Risks include conflicting memory attributes, wrong section/supersection alignment, clearing needed early mappings, lowmem truncation errors, cache policy changes after boot tables, LPAE physical offset fixup failures, and user/kernel PTE permission mistakes. Test boot across LPAE/non-LPAE, SMP/UP, highmem, XIP, KASAN, vmalloc size overrides, static IO maps, `/proc/iomem`/ptdump output, DMA/CMA remap, module loading, and executable mmap coherency.
