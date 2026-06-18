## sources/distributed-fs/ceph-client/arch/arm/mm/mm.h

### Purpose
Private ARM MM header shared by memory-management implementation files for fixed alias addresses, top-level PTE helpers, memory type descriptors, static ioremap metadata, and boot memory globals.

### Important APIs, Types, And Functions
Defines `COPYPAGE_MINICACHE`, `COPYPAGE_V6_FROM`, `COPYPAGE_V6_TO`, `FLUSH_ALIAS_START`, `VM_ARM_SECTION_MAPPING`, `VM_ARM_STATIC_MAPPING`, `VM_ARM_EMPTY_MAPPING`, and `VM_ARM_MTYPE`. Provides inline `set_top_pte` and `get_top_pte`. Defines `struct mem_type` and `struct static_vm`; declares `top_pmd`, `icache_size`, `get_mem_type`, `__flush_dcache_folio`, `static_vmlist`, `find_static_vm_vaddr`, `add_static_vm_early`, `arm_lowmem_limit`, DMA limits, `bootmem_init`, `arm_mm_memblock_reserve`, `dma_contiguous_remap`, and `__clear_cr`.

### Control Flow
Header-only inline control is limited to PTE installation/lookup in the top PMD plus local TLB flush. Other content is shared declarations.

### State, Dependencies, And Integration
State is external and owned by `mmu.c`, `ioremap.c`, `init.c`, and related files. Integrates fixed alias page-copy/flush code, ioremap metadata, DMA remap setup, and boot memory initialization.

### Risks And Test Signals
Risks include overlapping fixed virtual aliases, stale top-PTE TLB entries, and flag collisions in `vm_struct->flags`. Test builds across MMU/NOMMU, highmem, VIPT aliasing copy/flush paths, and ioremap section/static mapping paths.
