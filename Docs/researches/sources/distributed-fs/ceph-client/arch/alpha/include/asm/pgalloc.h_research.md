<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/pgalloc.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/asm/pgalloc.h

**Purpose:** Defines Alpha page-table population helpers and declares `pgd_alloc`. It wires allocated PTE/PMD pages into Alpha's three-level page-table encoding.

**Important APIs/types/functions:** `pmd_populate`, `pmd_populate_kernel`, `pud_populate`, and `pgd_alloc`.

**Control flow:** MM code allocates lower-level tables through generic helpers, then these functions encode physical or kernel virtual table addresses with `pmd_set`/`pud_set`.

**State and persistence behavior:** No independent state; it mutates page-table entries inside an `mm_struct`.

**Dependencies and integration points:** Depends on `asm-generic/pgalloc.h`, `asm/pgtable.h` helpers, page allocator descriptors, and Linux `mm_struct`.

**Risks:** Using the user versus kernel populate variant incorrectly changes whether `page_to_pa()+PAGE_OFFSET` or a direct pointer is encoded. Bad encoding breaks page-table walks.

**Test signals:** Run fork/exec/mmap/page-fault tests, page-table debug checks, and kernel mapping tests on Alpha builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/pgalloc.h -->
