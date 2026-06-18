# sources/distributed-fs/ceph-client/arch/mips/include/asm/pgtable-32.h

## sources/distributed-fs/ceph-client/arch/mips/include/asm/pgtable-32.h

### Purpose
`pgtable-32.h` defines 32-bit MIPS page-table geometry, folded generic levels, virtual ranges, invalid table handling, PFN/PTE conversion, and swap-PTE encoding. It covers normal 32-bit physical addresses, 36-bit physical address extensions, XPA, R3K TLBs, highmem, and huge-TLB tradeoffs.

### Important APIs, Types, And Functions
Important declarations and macros include `temp_tlb_entry`, `add_temporary_entry`, `PGDIR_SHIFT`, `PGD_TABLE_ORDER`, `PTRS_PER_PGD`, `PTRS_PER_PTE`, `USER_PTRS_PER_PGD`, `VMALLOC_START`, `VMALLOC_END`, `invalid_pte_table`, `pmd_none`, `pmd_bad`, `pmd_present`, `pmd_clear`, `pte_pfn`, `pfn_pte`, `pfn_pmd`, `pte_page`, `__swp_type`, `__swp_offset`, `__swp_entry`, and `_PAGE_SWP_EXCLUSIVE`.

### Control Flow
The generic MM layer evaluates this header at compile time to pick table sizes and folds PUD/PMD levels. Runtime helpers validate or clear PMD entries by comparing against `invalid_pte_table`, create PTEs from PFNs using the active physical-address model, and encode swap entries into non-present PTE bit ranges.

### State, Persistence, Dependencies, And Integration
State is in page-table pages, temporary boot TLB entries, invalid table sentinels, and swap PTE values. Dependencies include `addrspace.h`, `page.h`, cache/fixmap definitions, highmem when configured, and generic no-PMD folding. Integration points are early TLB setup, vmalloc layout, highmem PKMAP placement, swap, huge pages, and generic fault handling.

### Risks
Bit layouts differ sharply across R3K, XPA, 36-bit, and normal builds. Any overlap between swap type/offset/exclusive bits and hardware-valid/global/present bits can corrupt swap or create valid bogus mappings. `PGDIR_SHIFT` changes for huge-page support can silently mis-size page tables if config guards drift.

### Test Signals
Build representative 32-bit MIPS configs with and without highmem, XPA, 36-bit physical addressing, R3K TLB, and huge TLB. Boot mmap/swap/vmalloc/highmem workloads, run hugepage tests where supported, and check early boot paths that call `add_temporary_entry`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/pgtable-32.h -->
