<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/pgtable-be-types.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/pgtable-be-types.h

## Purpose
This header defines big-endian PowerPC page-table C types and raw/value conversion helpers for PTE, PMD, PUD, PGD, pgprot, and real PTE records.

## Important APIs, Types, And Functions
It defines big-endian `pte_t`, `pmd_t`, `pud_t`, `pgd_t`, `pgprot_t`, `real_pte_t`, constructors `__pte()`, `__pmd()`, `__pud()`, `__pgd()`, raw constructors, value/raw accessors, and atomic compare-exchange helpers `pte_xchg()` and `pmd_xchg()`.

## Control Flow
Inline accessors convert between CPU-endian unsigned long values and stored big-endian table entries. Exchange helpers use `__cmpxchg_u64()` on raw table storage.

## State And Persistence Behavior
Persistent page-table state is stored in big-endian fields. For 64K hash configurations, `real_pte_t` carries an additional hash index.

## Dependencies And Integration Points
It depends on `asm/cmpxchg.h` and endian conversion helpers. It integrates with page-table walkers and atomic PTE/PMD update paths on big-endian builds.

## Risks And Edge Cases
Mixing raw and converted values can corrupt page tables. Atomic exchange compares raw big-endian storage. Type layout must match assembly and MMU expectations.

## Test Signals
Build big-endian PPC64/Book3S configs, run page-table atomic update stress, huge/64K page tests, and endian-sensitive swap/mmap tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/pgtable-be-types.h -->
