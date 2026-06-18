## sources/distributed-fs/ceph-client/arch/arm/mm/ioremap.c

### Purpose
Implements ARM physical-to-kernel virtual remapping for MMIO, cached/WC device memory, executable external memory, memremap, static mappings, PCI IO space, and vmalloc page-table synchronization.

### Important APIs, Types, And Functions
Important state is `static_vmlist`, `arch_ioremap_caller`, and PCI `pci_ioremap_mem_type`. Key functions include `find_static_vm_vaddr`, `add_static_vm_early`, `ioremap_page`, `__check_vmalloc_seq`, `__arm_ioremap_caller`, `__arm_ioremap_pfn`, `ioremap`, `ioremap_cache`, `ioremap_wc`, `__arm_ioremap_exec`, `__arm_iomem_set_ro`, `arch_memremap_wb`, `iounmap`, `pci_remap_iospace`, `pci_remap_cfgspace`, and `early_ioremap_init`.

### Control Flow
Static mappings are registered early and reused when an ioremap request fits the same physical range and memory type. Dynamic ioremap validates wraparound, memory type, RAM attribute conflicts, and high-address alignment, allocates vmalloc space, then maps via section/supersection optimization on safe UP non-LPAE builds or page mappings otherwise. `iounmap` ignores static mappings and specially tears down section mappings before `vunmap`.

### State, Dependencies, And Integration
State is sorted static VM metadata and vmalloc sequence counters in `init_mm.context`. Depends on memblock, vmap/vmalloc, page-table helpers, cache/TLB flushing, KASAN vmalloc shadow syncing, PCI mapping constants, and `mmu.c` memory types. Integrates with drivers, early IO, PCI, memremap, and per-mm vmalloc fault avoidance.

### Risks And Test Signals
Risks include mapping RAM with conflicting attributes, stale per-mm vmalloc PGDs, static mapping overlap mistakes, section unmap races, and high physical address alignment failures. Test driver probe/remove loops, static map reuse, KASAN_VMALLOC, SMP vs UP section paths, PCI IO remap, and invalid ioremap inputs.
