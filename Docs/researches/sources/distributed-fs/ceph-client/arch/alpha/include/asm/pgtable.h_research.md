<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/pgtable.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/asm/pgtable.h

**Purpose:** Defines Alpha page-table layout, protection bits, PTE/PMD/PUD transformations, swap-PTE encoding, TLB-update hooks, and vmalloc ranges.

**Important APIs/types/functions:** `set_pte`, `PMD_SHIFT`, `PGDIR_SHIFT`, pointer counts, `VMALLOC_START/END`, `_PAGE_*` flags, `PAGE_*` protections, `pgprot_modify`, `pfn_pte`, `pte_modify`, `pmd_set`, `pud_set`, `pmd_offset`, `pte_offset_kernel`, compaction helpers `ptep_get_and_clear`/`ptep_clear_flush`, swap helpers, and `paging_init`.

**Control flow:** Page fault and mmap code construct PTEs from PFNs plus protection bits, walk PUD/PMD/PTE levels with Alpha-specific address shifts, and use explicit read barriers for dependent page-table loads because Alpha can reorder them. Compaction clear paths flush migrated pages through `migrate_flush_tlb_page`.

**State and persistence behavior:** State is the live page table tree, swap PTE markers, software dirty/accessed bits, and protection flags. The file persists ABI-like layout for core dumps, memory management, and user mappings.

**Dependencies and integration points:** Depends on generic nopud handling, page definitions, processor `TASK_SIZE`, machine-vector layout, setup constants, page table check, and TLB/migration code.

**Risks:** Dirty/accessed bits are partly software conventions. `PHYS_TWIDDLE` exists for legacy X server KSEG-address quirks and can be dangerous if physical address assumptions change. Missing Alpha barriers in page-table walks can expose uninitialized page tables on SMP.

**Test signals:** Run mm selftests, swap/COW/mprotect/exec tests, compaction/migration tests, vmalloc/ioremap tests, and Alpha SMP stress with page-table debug enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/pgtable.h -->
