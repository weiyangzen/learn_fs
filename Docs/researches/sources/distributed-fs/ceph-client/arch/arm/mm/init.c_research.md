## sources/distributed-fs/ceph-client/arch/arm/mm/init.c

### Purpose
Handles ARM memory initialization around memblock reservation, DMA zone limits, initrd tags, highmem limits, init memory freeing, strict kernel permissions, and executable memory ranges.

### Important APIs, Types, And Functions
Key entry points include `__clear_cr`, `setup_dma_zone`, `arch_zone_limits_init`, `pfn_valid`, `arm_memblock_steal`, `arm_memblock_init`, `bootmem_init`, `arch_mm_preinit`, `free_initmem`, `free_initrd_mem`, and `execmem_arch_setup`. Strict RWX support uses `section_perm`, `section_update`, `set_section_perms`, `fix_kernmem_perms`, and `mark_rodata_ro`.

### Control Flow
Boot reserves kernel/initrd/page tables/platform regions, scans reserved FDT memory, reserves CMA, freezes memblock stealing, finds PFN limits, and performs early memtest. Preinit checks address layout and initializes SWIOTLB for LPAE when needed. After init, strict RWX uses `stop_machine` to update section permissions across process page tables, then init memory is poisoned and freed.

### State, Dependencies, And Integration
Persistent state includes DMA zone limit globals, `arm_memblock_steal_permitted`, and `execmem_info`. Depends on memblock, initrd/FDT, CMA, SWIOTLB, stop_machine, set_memory, ptdump, and machine descriptors. Integrates with zone setup, bootmem, module/JIT executable allocation, and rodata hardening.

### Risks And Test Signals
Risks include incorrect PFN validity near rounded pageblocks, DMA zone mis-sizing, freeing reserved memory, strict-permission section misalignment, and initrd poisoning bounds. Test boot on highmem/LPAE/non-LPAE systems, initrd load/free, DMA mask allocations, strict RWX W+X checks, and module allocation.
