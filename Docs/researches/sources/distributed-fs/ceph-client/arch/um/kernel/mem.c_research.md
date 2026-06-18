# sources/distributed-fs/ceph-client/arch/um/kernel/mem.c Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/kernel/mem.c -->
## sources/distributed-fs/ceph-client/arch/um/kernel/mem.c

### Purpose
This file initializes UML memory-management state after early physical memory setup.

### Important APIs, Types, And Functions
It implements optional KASAN init, defines `swapper_pg_dir`, `kmalloc_ok`, `arch_mm_preinit()`, `mem_init()`, `arch_zone_limits_init()`, no-op `free_initmem()`, `pgd_alloc()`, `uml_kmalloc()`, the protection map, and `mark_rodata_ro()`.

### Control Flow
Preinit enables KASAN after jump labels, maps/frees the post-brk reserved area into memblock, updates `uml_reserved` and PFN bounds, and later enables normal kmalloc. `pgd_alloc()` copies kernel-half PGD entries into new mms.

### State, Persistence, And Dependencies
State includes swapper page directory, `kmalloc_ok`, brk boundary, memblock zones, PFN limits, protection map, and rodata page permissions. Dependencies include memblock, slab, KASAN, UML address layout, `map_memory()`, host `sbrk()`, and pgtable helpers.

### Integration Points And Risks
Risks include early allocation ordering, brk/reserved mapping correctness, no freeing of kernel image initmem, KASAN enable timing, and rodata alignment. Integration is with generic mm boot and page-table allocation.

### Test Signals
Boot with KASAN on/off, varied memory sizes, fork/exec PGD copying, rodata write protection, and early allocation paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/kernel/mem.c -->
