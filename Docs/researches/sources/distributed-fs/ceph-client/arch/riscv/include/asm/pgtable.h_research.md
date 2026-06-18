<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/pgtable.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/pgtable.h

Purpose: Implements the main RISC-V Linux page-table contract: virtual address layout, page protections, PTE/PMD/PUD/PGD conversion helpers, TLB cache update hooks, THP helpers, swap encoding, and task-size definitions.

Important APIs/types/functions: Key APIs include `pte_pfn()`, `pfn_pte()`, `pte_present()`, `pte_accessible()`, `pte_modify()`, `set_ptes()`, `ptep_get_and_clear()`, `ptep_set_wrprotect()`, `pgprot_noncached()`, `pgprot_writecombine()`, THP `pmd*`/`pud*` helpers, swap macros, `update_mmu_cache_range()`, `set_pgd_safe()`, and `set_p4d_safe()`.

Control flow: The header computes MMU layout from Sv32/Sv39/Sv48/Sv57, builds protection constants, mutates PTEs with `WRITE_ONCE`/atomic exchange, flushes icache for executable mappings, and issues local SFENCE.VMA for new valid mappings unless Svvptc makes invalid-entry caching safe.

State and persistence: Persistent state includes global page directories, early page-table allocation callbacks, `satp_mode`, early DTB pointers, and every live page-table entry. It also encodes swap type/offset/exclusive/soft-dirty/uffd-wp state in non-present PTEs.

Dependencies and integration points: Integrates with generic Linux MM, TLB flush, page-table check, cpufeature, compat task sizing, THP, NUMA balancing, Svnapot, Svadu/Svade A/D semantics, and T-Head PMA alternatives.

Risks: This is high-risk memory-management code. Incorrect address-space sizing, missing SFENCE, bad A/D assumptions, incorrect shadow-stack write-protect handling, or swap-bit collisions can cause memory corruption or security bugs.

Test signals: RISC-V MM boot tests, mmap limit tests, fork/exec, swap, THP collapse/split, NUMA balancing, userfaultfd, soft-dirty, icache coherency, KASAN, page_table_check, and vendor-extension systems are strong signals.

Source read size: 1288 lines, 32232 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/pgtable.h -->
