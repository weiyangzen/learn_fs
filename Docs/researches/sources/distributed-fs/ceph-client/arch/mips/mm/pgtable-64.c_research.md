<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/pgtable-64.c -->
## sources/distributed-fs/ceph-client/arch/mips/mm/pgtable-64.c

### Purpose
`pgtable-64.c` initializes 64-bit MIPS top-level and folded or unfolded invalid page-table layers. It prepares invalid PGD/PUD/PMD entries and creates page-table coverage for fixed mappings.

### Important APIs, Types, And Functions
`pgd_init()` fills a PGD page with `invalid_pud_table`, `invalid_pmd_table`, or `invalid_pte_table` depending on folded levels. `pmd_init()` and `pud_init()` initialize invalid lower-level tables when those levels exist. `pagetable_init()` initializes the swapper root and invalid tables, then calls `fixrange_init()`. `pmd_init()` is exported for GPL modules when PMD tables are not folded.

### Control Flow
Boot initializes `swapper_pg_dir`, optionally initializes `invalid_pud_table` and `invalid_pmd_table`, and then computes a PMD-aligned fixmap start from `__fix_to_virt(__end_of_fixed_addresses - 1)`. `fixrange_init()` allocates the tables needed for the fixmap range.

### State, Persistence, And Dependencies
The durable state is the initial kernel page-table hierarchy and invalid-table sentinel contents. Dependencies include the MIPS pgalloc table symbols, folded-level macros, fixmap constants, and TLB flush/MM headers.

### Integration Points
The file is the 64-bit counterpart of `pgtable-32.c` and must agree with `pgd_alloc()`, TLB refill code, hardware page-table walker setup, and the configured number of page-table levels.

### Risks
The initialization loops rely on table counts that are multiples of eight. A mismatch between folded-level configuration and chosen invalid table would send page-table walks into the wrong sentinel table. Fixmap range errors affect early exception, ioremap, and per-CPU fixed mappings.

### Test Signals
Boot 64-bit MIPS with folded and three-level page-table configurations, use fixmap-heavy early boot paths, and verify module users of exported `pmd_init()` on non-folded PMD builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/pgtable-64.c -->
