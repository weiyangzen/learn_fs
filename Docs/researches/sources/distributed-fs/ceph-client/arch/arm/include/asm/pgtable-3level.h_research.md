# sources/distributed-fs/ceph-client/arch/arm/include/asm/pgtable-3level.h

## Purpose
Implements ARM LPAE three-level page-table layout, 64-bit Linux PTE bits, huge PMD handling, PTE comparison rules, and PMD permission/dirty/accessed helpers.

## Important APIs, Types, And Functions
Key declarations include static inline pmd_t *pud_pgtable(pud_t pud); static inline pte_t pte_mkspecial(pte_t pte); static inline pmd_t pmd_##fn(pmd_t pmd) { pmd_val(pmd) op; return pmd; }; static inline pmd_t pmd_mkinvalid(pmd_t pmd); static inline pmd_t pmd_modify(pmd_t pmd, pgprot_t newprot); static inline void set_pmd_at(struct mm_struct *mm, unsigned long addr,. Important macros/constants include _ASM_PGTABLE_3LEVEL_H, PTRS_PER_PTE, PTRS_PER_PMD, PTRS_PER_PGD, PTE_HWTABLE_PTRS, PTE_HWTABLE_OFF, PTE_HWTABLE_SIZE, MAX_POSSIBLE_PHYSMEM_BITS, PGDIR_SHIFT, PMD_SHIFT.

## Control Flow
PUD and PMD entries are cleaned/flushed for table-walk visibility; set_pmd_at adjusts validity and write permission based on PROT_NONE, dirty, and writable state, then writes non-global section descriptors for user mappings.

## State And Persistence
State is architectural memory-management state: page tables, ASIDs or pending switches, vmalloc sequence counters, physical/virtual offsets, and linker-defined address ranges. The header itself stores no data except declared externs and compile-time constants.

## Dependencies And Integration Points
Integrated with the generic Linux MM, scheduler, exception, and cache/TLB subsystems. Dependencies include the surrounding ARM architecture build and generic kernel headers, CP15 processor helpers, and configuration choices such as CONFIG_MMU, CONFIG_ARM_LPAE, CONFIG_SMP, and CPU feature selections.

## Risks And Edge Cases
Bit definitions and barriers are ABI-critical. Incorrect masks, missing cache/TLB maintenance, wrong ASID handling, or bad user-access bounds can cause silent memory corruption, stale translations, privilege bypass, or hard-to-debug boot failures.

## Test Signals
Signals include ARM allnoconfig/defconfig builds across MMU/NoMMU and LPAE variants, boot tests, vmalloc/module loading, mmap/mprotect/hugetlb where applicable, and MM selftests that exercise faults and TLB shootdowns.
