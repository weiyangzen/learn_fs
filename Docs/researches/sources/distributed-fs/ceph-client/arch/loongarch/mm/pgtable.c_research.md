<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/mm/pgtable.c -->
## sources/distributed-fs/ceph-client/arch/loongarch/mm/pgtable.c

### Purpose
`pgtable.c` provides LoongArch page-table allocation, initialization, virtual-to-page helpers, PMD update flushing, and early page-table setup.

### Important APIs, Types, And Functions
Functions include `dmw_virt_to_page()`, `tlb_virt_to_page()`, `pgd_alloc()`, `pgd_init()`, optional `pmd_init()`, optional `pud_init()`, `kernel_pte_init()`, `set_pmd_at()`, and `pagetable_init()`.

### Control Flow
`pgd_alloc()` allocates a user PGD, initializes all entries to invalid tables, then copies kernel entries from `init_mm` above `USER_PTRS_PER_PGD`. Table init functions fill entries with the appropriate invalid next-level table or `_PAGE_GLOBAL`. `set_pmd_at()` writes the PMD and flushes all TLBs. `pagetable_init()` initializes swapper/invalid tables and, under highmem, allocates pkmap/fixmap PTE ranges and records `pkmap_page_table`.

### State, Persistence, And Dependencies
Persistent state is page-table memory, invalid-table globals from `init.c`, and highmem pkmap metadata. Dependencies include LoongArch folded page-table configuration, `asm/pgalloc.h`, `asm/fixmap.h`, and TLB flushes.

### Integration Points
Generic MM calls `pgd_alloc()` for new processes. `init.c` allocates kernel PTEs and owns invalid table storage. TLB handlers depend on these table layouts and invalid pointers.

### Risks
Invalid table pointers must be valid kernel virtual addresses and match folded-level configuration. `set_pmd_at()` flushes globally, which is safe but costly. Copying kernel PGD entries must avoid leaking user-space entries.

### Test Signals
Boot across page-table levels, fork/exec stress, highmem/fixmap tests, page-table debug checks, and TLB handler validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/mm/pgtable.c -->
