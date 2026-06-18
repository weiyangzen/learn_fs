<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/mm/ioremap.c -->
# sources/distributed-fs/ceph-client/arch/openrisc/mm/ioremap.c

## Purpose
Provides OpenRISC kernel PTE page allocation for ioremap, including early boot before normal memory allocation is ready.

## Important APIs, Types, And Functions
`pte_alloc_one_kernel(struct mm_struct *mm)` returns `__pte_alloc_one_kernel()` after `mem_init_done`, otherwise allocates a page from memblock.

## Control Flow
Ioremap/fixmap page-table creation calls this allocator. Early callers get memblock-backed PTE pages; later callers use normal kernel PTE allocation.

## State And Persistence
Allocates PTE pages that persist as kernel page tables.

## Dependencies And Integration Points
Depends on `mem_init_done` from `mm/init.c`, memblock, vmalloc/ioremap, pgalloc, and TLB flushing by callers.

## Risks
Early allocations are never freed through normal paths. Incorrect `mem_init_done` timing can call unavailable allocators or leak memblock pages.

## Test Signals
Early serial console ioremap, later driver ioremap, fixmap setup, and boot with `mem_init_done` transition.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/mm/ioremap.c -->
