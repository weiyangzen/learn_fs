# sources/distributed-fs/ceph-client/arch/arm/include/asm/pgtable-2level-hwdef.h

## Purpose
Defines short-descriptor ARM page-table hardware bit encodings for PMD section entries, PTE small pages, domains, access permissions, TEX/C/B memory types, and execute-never flags.

## Important APIs, Types, And Functions
Important macros/constants include _ASM_PGTABLE_2LEVEL_HWDEF_H, PMD_TYPE_MASK, PMD_TYPE_FAULT, PMD_TYPE_TABLE, PMD_TYPE_SECT, PMD_PXNTABLE, PMD_BIT4, PMD_DOMAIN(x), PMD_DOMAIN_MASK, PMD_PROTECTION.

## Control Flow
Low-level MM code combines these constants with Linux PTE bits when cpu_set_pte_ext writes the hardware half of a two-level page table.

## State And Persistence
State is architectural memory-management state: page tables, ASIDs or pending switches, vmalloc sequence counters, physical/virtual offsets, and linker-defined address ranges. The header itself stores no data except declared externs and compile-time constants.

## Dependencies And Integration Points
Integrated with the generic Linux MM, scheduler, exception, and cache/TLB subsystems. Dependencies include the surrounding ARM architecture build and generic kernel headers, CP15 processor helpers, and configuration choices such as CONFIG_MMU, CONFIG_ARM_LPAE, CONFIG_SMP, and CPU feature selections.

## Risks And Edge Cases
Bit definitions and barriers are ABI-critical. Incorrect masks, missing cache/TLB maintenance, wrong ASID handling, or bad user-access bounds can cause silent memory corruption, stale translations, privilege bypass, or hard-to-debug boot failures.

## Test Signals
Signals include ARM allnoconfig/defconfig builds across MMU/NoMMU and LPAE variants, boot tests, vmalloc/module loading, mmap/mprotect/hugetlb where applicable, and MM selftests that exercise faults and TLB shootdowns.
