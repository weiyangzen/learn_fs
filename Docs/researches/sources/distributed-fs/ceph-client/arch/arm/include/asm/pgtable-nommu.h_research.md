# sources/distributed-fs/ceph-client/arch/arm/include/asm/pgtable-nommu.h

## Purpose
Provides NoMMU pgtable constants and stubs so generic memory-management code can compile without hardware translation tables.

## Important APIs, Types, And Functions
Key declarations include typedef pte_t *pte_addr_t;; extern unsigned int kobjsize(const void *objp);. Important macros/constants include _ASMARM_PGTABLE_NOMMU_H, pgd_present(pgd), pgd_none(pgd), pgd_bad(pgd), pgd_clear(pgdp), PGDIR_SHIFT, PGDIR_SIZE, PGDIR_MASK, PAGE_NONE, PAGE_SHARED. It depends directly on #include <linux/slab.h>, #include <asm/processor.h>, #include <asm/page.h>.

## Control Flow
Most page protection and pte helpers collapse to direct values or no-ops because NoMMU mappings are not changed through page tables.

## State And Persistence
State is architectural memory-management state: page tables, ASIDs or pending switches, vmalloc sequence counters, physical/virtual offsets, and linker-defined address ranges. The header itself stores no data except declared externs and compile-time constants.

## Dependencies And Integration Points
Integrated with the generic Linux MM, scheduler, exception, and cache/TLB subsystems. Dependencies include #include <linux/slab.h>, #include <asm/processor.h>, #include <asm/page.h>, CP15 processor helpers, and configuration choices such as CONFIG_MMU, CONFIG_ARM_LPAE, CONFIG_SMP, and CPU feature selections.

## Risks And Edge Cases
Bit definitions and barriers are ABI-critical. Incorrect masks, missing cache/TLB maintenance, wrong ASID handling, or bad user-access bounds can cause silent memory corruption, stale translations, privilege bypass, or hard-to-debug boot failures.

## Test Signals
Signals include ARM allnoconfig/defconfig builds across MMU/NoMMU and LPAE variants, boot tests, vmalloc/module loading, mmap/mprotect/hugetlb where applicable, and MM selftests that exercise faults and TLB shootdowns.
