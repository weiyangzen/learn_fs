<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/pgtable-32.c -->
## sources/distributed-fs/ceph-client/arch/mips/mm/pgtable-32.c

### Purpose
`pgtable-32.c` initializes 32-bit MIPS kernel page-table roots and fixed mapping ranges. It seeds invalid page-table pointers into `swapper_pg_dir`, prepares fixmap page-table coverage, and wires permanent kmap page tables when highmem is enabled.

### Important APIs, Types, And Functions
`pgd_init()` fills user PGD entries with `invalid_pte_table`. `pagetable_init()` initializes `swapper_pg_dir`, calls `fixrange_init()` for fixmap and highmem pkmap regions, and assigns `pkmap_page_table` under `CONFIG_HIGHMEM`. `set_pmd_at()` is a transparent hugepage helper that stores a PMD directly.

### Control Flow
Boot calls `pagetable_init()`, which initializes both user and kernel halves of `swapper_pg_dir`, computes the final fixed-address virtual range using `__fix_to_virt()`, and allocates intermediate page tables through `fixrange_init()`. In highmem builds, it repeats range setup for `PKMAP_BASE`, then walks PGD/P4D/PUD/PMD/PTE offsets to remember the permanent kmap PTE page.

### State, Persistence, And Dependencies
Persistent state is the kernel page-table tree rooted at `swapper_pg_dir` plus optional `pkmap_page_table`. The file depends on MIPS pgalloc invalid-table symbols, fixmap constants, highmem constants, and generic Linux MM types.

### Integration Points
This code is selected for 32-bit MIPS page-table setup and feeds fixmap, highmem kmap, TLB refill, and later `pgd_alloc()` behavior. It must match the folded page-table model used by the 32-bit architecture configuration.

### Risks
The unrolled `pgd_init()` assumes `USER_PTRS_PER_PGD` is a multiple of eight. Wrong fixmap or pkmap range alignment would leave early virtual mappings without page tables. Highmem state is especially sensitive because `pkmap_page_table` becomes a shared pointer for permanent kmap operations.

### Test Signals
Useful signals are early boot on 32-bit MIPS with and without `CONFIG_HIGHMEM`, fixmap users such as early ioremap, permanent kmap stress, and transparent hugepage builds verifying `set_pmd_at()` linkage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/pgtable-32.c -->
