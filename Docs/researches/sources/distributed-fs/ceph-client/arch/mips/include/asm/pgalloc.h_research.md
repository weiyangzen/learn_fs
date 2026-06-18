# sources/distributed-fs/ceph-client/arch/mips/include/asm/pgalloc.h

## sources/distributed-fs/ceph-client/arch/mips/include/asm/pgalloc.h

### Purpose
`pgalloc.h` supplies MIPS page-table allocation and population hooks for the generic MM subsystem. It creates PMD/PUD/P4D population helpers, declares table initializers, and connects page-table memory to TLB freeing.

### Important APIs, Types, And Functions
Important exports are `pmd_populate_kernel`, `pmd_populate`, `pud_populate`, `pgd_init`, `pgd_alloc`, `pmd_alloc_one`, `pud_alloc_one`, `p4d_populate`, and free macros `__pte_free_tlb`, `__pmd_free_tlb`, and `__pud_free_tlb`. It also advertises `__HAVE_ARCH_PMD_ALLOC_ONE` and `__HAVE_ARCH_PUD_ALLOC_ONE`.

### Control Flow
Generic MM calls allocation helpers when a page-table level is needed. MIPS allocates a `ptdesc`, runs the appropriate constructor, initializes invalid entries with `pmd_init` or `pud_init`, and returns the table pointer. Population helpers install child-table addresses into parent entries through architecture setters.

### State, Persistence, Dependencies, And Integration
State is kernel page-table memory, `struct ptdesc` metadata, and per-`mm_struct` accounting; freed tables are deferred through MMU gather/TLB removal. Dependencies include highmem, generic MM, scheduler accounting, `asm-generic/pgalloc.h`, MIPS table setter macros, and folded-level definitions from `pgtable-32.h` or `pgtable-64.h`.

### Risks
Allocation order and folded-level preprocessor branches must match page-table geometry. Missing constructors or wrong GFP flags can break accounting, and freeing the wrong virtual-to-ptdesc address can corrupt page-table lifetime under concurrent TLB teardown.

### Test Signals
Cross-build 32-bit, 64-bit, folded, and huge-page configurations; boot with fork/exec/mmap stress, highmem, memory pressure, and TLB shootdown tests; run page-table debug options when available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/pgalloc.h -->
