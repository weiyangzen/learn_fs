# sources/distributed-fs/ceph-client/arch/arm/include/asm/pgtable-hwdef.h

## Purpose
Selects the correct ARM page-table hardware-definition header for either LPAE three-level or classic two-level MMU builds.

## Important APIs, Types, And Functions
Important macros/constants include _ASMARM_PGTABLE_HWDEF_H. It depends directly on #include <asm/pgtable-3level-hwdef.h>, #include <asm/pgtable-2level-hwdef.h>.

## Control Flow
The include path is compile-time only and gives pgtable.h a uniform set of descriptor constants.

## State And Persistence
State is architectural memory-management state: page tables, ASIDs or pending switches, vmalloc sequence counters, physical/virtual offsets, and linker-defined address ranges. The header itself stores no data except declared externs and compile-time constants.

## Dependencies And Integration Points
Integrated with the generic Linux MM, scheduler, exception, and cache/TLB subsystems. Dependencies include #include <asm/pgtable-3level-hwdef.h>, #include <asm/pgtable-2level-hwdef.h>, CP15 processor helpers, and configuration choices such as CONFIG_MMU, CONFIG_ARM_LPAE, CONFIG_SMP, and CPU feature selections.

## Risks And Edge Cases
Bit definitions and barriers are ABI-critical. Incorrect masks, missing cache/TLB maintenance, wrong ASID handling, or bad user-access bounds can cause silent memory corruption, stale translations, privilege bypass, or hard-to-debug boot failures.

## Test Signals
Signals include ARM allnoconfig/defconfig builds across MMU/NoMMU and LPAE variants, boot tests, vmalloc/module loading, mmap/mprotect/hugetlb where applicable, and MM selftests that exercise faults and TLB shootdowns.
