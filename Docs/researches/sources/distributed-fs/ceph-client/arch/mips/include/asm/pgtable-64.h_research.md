# sources/distributed-fs/ceph-client/arch/mips/include/asm/pgtable-64.h

## sources/distributed-fs/ceph-client/arch/mips/include/asm/pgtable-64.h

### Purpose
`pgtable-64.h` defines 64-bit MIPS page-table geometry across two-, three-, and four-level layouts. It calculates PGD/PUD/PMD shifts and orders for page sizes from 4 KiB through 64 KiB, defines vmalloc/module ranges, invalid table sentinels, folded/non-folded table types, PFN conversion, and swap-PTE encoding.

### Important APIs, Types, And Functions
Key exports include `PGDIR_SHIFT`, `PMD_SHIFT`, `PUD_SHIFT`, `PTRS_PER_*`, `USER_PTRS_PER_PGD`, `VMALLOC_START`, `VMALLOC_END`, `MODULES_VADDR`, `invalid_pte_table`, `invalid_pmd_table`, `invalid_pud_table`, `p4d_none`, `p4d_bad`, `p4d_present`, `p4d_clear`, `p4d_pgtable`, `set_p4d`, `pmd_none`, `pmd_bad`, `pmd_present`, `pmd_clear`, `pud_none`, `pud_bad`, `pud_present`, `pud_clear`, `pud_pgtable`, `pte_pfn`, `pfn_pte`, `pfn_pmd`, `mk_swap_pte`, and swap conversion macros.

### Control Flow
Compile-time branches select generic folded-level headers and compute table shape from `CONFIG_PGTABLE_LEVELS`, page size, and 48-bit virtual-address support. Runtime inline helpers compare entries against invalid sentinel tables, clear levels back to sentinels, and derive child-table or page addresses for generic MM walkers.

### State, Persistence, Dependencies, And Integration
State lives in page-table pages, invalid table arrays, TLB-visible PTE/PMD values, and swap entries. Dependencies include `linux/compiler.h`, `linux/linkage.h`, MIPS address-space/page/cache/fixmap headers, and generic no-level wrappers. Integration covers vmalloc, module loading in 32-bit-compatible segments, THP/hugetlb PMDs via `pgtable.h`, and generic MM page-table walking.

### Risks
The matrix of page sizes, VA bits, and folded levels is easy to desynchronize from generic MM expectations. `VMALLOC_END` depends on `cpu_vmbits` and table fanout; mistakes can expose unmapped holes or collide with fixmap/module space. Swap bit allocation must avoid hardware and soft-dirty/exclusive bits.

### Test Signals
Cross-build 64-bit MIPS with 4K/16K/64K pages, 2/3/4-level tables, and `CONFIG_MIPS_VA_BITS_48`; run vmalloc, module load, swap, fork/mmap, and hugepage/THP tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/pgtable-64.h -->
