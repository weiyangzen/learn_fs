# sources/distributed-fs/ceph-client/arch/arm/include/asm/pgtable-2level.h

## Purpose
Maps Linux three-level MM expectations onto ARM classic two-level short-descriptor hardware tables, including folded PMDs, Linux shadow PTEs, hardware PTE offsets, software accessed/dirty bits, and memory type encodings.

## Important APIs, Types, And Functions
Key declarations include static inline int pud_none(pud_t pud); static inline int pud_bad(pud_t pud); static inline int pud_present(pud_t pud); static inline void pud_clear(pud_t *pudp); static inline void set_pud(pud_t *pudp, pud_t pud); static inline pmd_t *pmd_offset(pud_t *pud, unsigned long addr). Important macros/constants include _ASM_PGTABLE_2LEVEL_H, __PAGETABLE_PMD_FOLDED, PTRS_PER_PTE, PTRS_PER_PMD, PTRS_PER_PGD, PTE_HWTABLE_PTRS, PTE_HWTABLE_OFF, PTE_HWTABLE_SIZE, MAX_POSSIBLE_PHYSMEM_BITS, PMD_SHIFT.

## Control Flow
The MM layer updates Linux PTE bits; set_pte_ext converts them into adjacent hardware PTE entries. Accessed and dirty are emulated by faulting until handle_pte_fault updates the Linux bits and TLB maintenance observes the changed hardware permissions.

## State And Persistence
State is architectural memory-management state: page tables, ASIDs or pending switches, vmalloc sequence counters, physical/virtual offsets, and linker-defined address ranges. The header itself stores no data except declared externs and compile-time constants.

## Dependencies And Integration Points
Integrated with the generic Linux MM, scheduler, exception, and cache/TLB subsystems. Dependencies include the surrounding ARM architecture build and generic kernel headers, CP15 processor helpers, and configuration choices such as CONFIG_MMU, CONFIG_ARM_LPAE, CONFIG_SMP, and CPU feature selections.

## Risks And Edge Cases
Bit definitions and barriers are ABI-critical. Incorrect masks, missing cache/TLB maintenance, wrong ASID handling, or bad user-access bounds can cause silent memory corruption, stale translations, privilege bypass, or hard-to-debug boot failures.

## Test Signals
Signals include ARM allnoconfig/defconfig builds across MMU/NoMMU and LPAE variants, boot tests, vmalloc/module loading, mmap/mprotect/hugetlb where applicable, and MM selftests that exercise faults and TLB shootdowns.
