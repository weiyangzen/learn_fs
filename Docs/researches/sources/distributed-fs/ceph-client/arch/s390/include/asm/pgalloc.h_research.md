# sources/distributed-fs/ceph-client/arch/s390/include/asm/pgalloc.h

Purpose: This header defines s390 page-table allocation/free/populate helpers for CRST and PTE tables, ASCE upgrades, vmemmap mapping allocation, and deferred PTE freeing.

Important APIs/types/functions: `CRST_ALLOC_ORDER`, `crst_table_alloc/free`, `page_table_alloc/free`, `crst_table_init()`, `crst_table_upgrade()`, `check_asce_limit()`, `p4d/pud/pmd/pgd_alloc_one` and free helpers, populate helpers, PTE allocation/free macros, `pte_free_defer()`, `vmem_map_init()`, `vmem_crst_alloc()`, `vmem_pte_alloc()`, `base_asce_alloc()`, and `base_asce_free()` are exposed.

Control flow: MM code allocates CRST tables, initializes them with the correct empty entry for their level, upgrades ASCE limits when a mapping exceeds the current address-space size, populates parent entries with physical table addresses, and frees tables unless the level is folded.

State and persistence: Persistent state is page-table memory owned by an `mm_struct` or vmem/base ASCE mapping. Constructors/destructors update generic page-table accounting/checking metadata.

Dependencies and integration points: It depends on `pgtable.h` folding and entry encodings, Linux MM allocation hooks, page-table constructors, and vmemmap/base ASCE code.

Risks and test signals: Incorrect folded-level handling or ASCE upgrade failure can corrupt address spaces. Tests should cover fork/exit page-table allocation, mmap above current ASCE limit, vmemmap add/remove, THP split/collapse interactions, and page-table-check builds.
