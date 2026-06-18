<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/mm/pgtable.c -->
# sources/distributed-fs/ceph-client/arch/riscv/mm/pgtable.c

## Purpose
`pgtable.c` supplies RISC-V page-table helper operations used by generic MM, huge vmap, transparent hugepage, and shadow-stack-aware write helpers.

## Important APIs, Types, And Functions
Functions include `ptep_set_access_flags()`, `ptep_test_and_clear_young()`, runtime `pud_offset()`/`p4d_offset()` for folded levels, huge vmap helpers, PUD/PMD page freeing, `pmdp_collapse_flush()`, `pudp_invalidate()`, `pte_mkwrite()`, and `pmd_mkwrite()`.

## Control Flow
Access-flag updates either set and flush immediately for SVVPTC-sensitive systems or update and rely on `update_mmu_cache()`. Huge vmap functions install/clear huge PUD/PMD mappings and free lower page tables after TLB flush. THP collapse globally flushes the mm because leaf-level conversion semantics require eager fencing. Write helpers choose normal or shadow-stack writable encodings based on VMA flags.

## State And Persistence
It mutates process/kernel page-table entries and accessed bits. No private persistent state exists.

## Dependencies And Integration Points
It depends on RISC-V PTE bit definitions, page-table level enable flags, huge vmap, THP, shadow stack VM flags, TLB flush APIs, and generic MM callers.

## Risks
SVVPTC changes TLB invalidation requirements. Freeing huge-vmap lower tables must happen only after clearing and flushing. Folded level offset helpers must match `pgtable_l4_enabled`/`l5_enabled` runtime state.

## Test Signals
MM selftests for access/young bits, huge vmap, THP collapse, shadow stack mappings, and Sv48/Sv57 runtime folded-level configurations are relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/mm/pgtable.c -->
