<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/pgtable-types.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/pgtable-types.h

## Purpose
This header defines native-endian PowerPC page-table C types and constructors for non-big-endian-specialized builds, with strict type checking where needed.

## Important APIs, Types, And Functions
It controls `STRICT_MM_TYPECHECKS`, defines `pte_t` including the special 8xx 16K four-cell form, `__pte()`, `pte_val()`, 64-bit `pmd_t`/`pud_t` and accessors, `pgd_t` including 85xx 64-bit PGDs, `__pgd()`, `pgprot_t`, `real_pte_t`, and Book3S64 `pte_xchg()`.

## Control Flow
Inline constructors/accessors wrap or unwrap primitive values. `pte_xchg()` performs atomic PTE compare-exchange on Book3S64.

## State And Persistence Behavior
The type definitions determine the in-memory layout of page tables. 8xx 16K PTEs persist four replicated basic values inside one logical `pte_t`.

## Dependencies And Integration Points
It depends on `pte_basic_t`, Kconfig MMU/page options, optional `asm/cmpxchg.h`, and is consumed by all page-table code.

## Risks And Edge Cases
Strict type checking differs by 32/64-bit and sparse checker builds. 85xx PGD width and 8xx multi-cell PTEs are special cases that generic code must respect.

## Test Signals
Cross-build sparse/normal, PPC32/PPC64, 8xx 16K, 85xx, and Book3S64 configs; run page-table access and atomic update tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/pgtable-types.h -->
