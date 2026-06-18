<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/pgtable-64.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/pgtable-64.h

Purpose: Defines RV64 Sv39/Sv48/Sv57 page-table geometry, upper-level entry types, hugepage support, NAPOT contiguous mappings, and vendor/cache memory-type bits.

Important APIs/types/functions: Important items include `pgtable_l4_enabled`, `pgtable_l5_enabled`, `PGDIR/P4D/PUD/PMD_*` geometry, `p4d_t`, `pud_t`, `pmd_t`, `pud_*`, `p4d_*`, `pgd_*`, `pfn_pmd()`, `pfn_pud()`, `riscv_page_mtmask()`, `riscv_page_nocache()`, and NAPOT helpers.

Control flow: Most helpers test presence/leaf/bad state, set entries with `WRITE_ONCE`, convert entries to lower page-table pointers or pages, and select Svpbmt versus T-Head PMA memory-type bits at runtime.

State and persistence: Persistent state is limited to global booleans selecting 4-level or 5-level page tables; entries encode PFN, leaf, user, and memory-type state.

Dependencies and integration points: Depends on cpufeature/errata alternatives, Svpbmt/Svnapot config, T-Head PMA alternatives, and the common `pgtable.h` PTE helpers.

Risks: Level folding, PFN masking, NAPOT order decoding, and memory-type selection are boot- and data-corruption sensitive.

Test signals: RV64 boots across Sv39/Sv48/Sv57, hugepage and NAPOT mappings, ioremap cacheability, T-Head errata machines, and page-table debug.

Source read size: 406 lines, 9738 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/pgtable-64.h -->
