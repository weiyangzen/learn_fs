## sources/distributed-fs/ceph-client/arch/arm/mm/dump.c

### Purpose
Implements ARM kernel page-table dumping and W+X checking through ptdump/debugfs.

### Important APIs, Types, And Functions
Important structures are `pg_state`, `prot_bits`, and `pg_level`. Key routines include `dump_prot`, `note_prot_wx`, `note_page`, `walk_pte`, `walk_pmd`, `walk_pud`, `walk_p4d`, `walk_pgd`, `ptdump_walk_pgd`, `ptdump_check_wx`, and `ptdump_init`. It defines address markers for KASAN shadow, modules, kernel mapping, vmalloc, FDT, fixmap, and vectors.

### Control Flow
`ptdump_init` initializes masks and registers `kernel_page_tables`. Walkers traverse `init_mm` page tables from PGD down to PTE, coalesce adjacent ranges with identical level/domain/protection, print decoded attributes, and optionally count writable-executable mappings.

### State, Dependencies, And Integration
State is static decode tables and marker metadata. Depends on debugfs/seq_file, ARM PTE/PMD bit definitions, domains, fixmap constants, and ptdump core. Integration points are debugfs diagnostics and strict RWX validation via `arm_debug_checkwx`.

### Risks And Test Signals
Risks include stale bit decoding after page-table format changes, bad folded-level handling, and false W+X results if ro/nx bit masks are wrong. Test by reading debugfs `kernel_page_tables`, enabling KASAN and LPAE/non-LPAE builds, and checking boot W+X logs.
