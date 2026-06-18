# sources/distributed-fs/ceph-client/arch/arm/include/asm/memory.h

## Purpose
Central ARM memory-layout contract for PAGE_OFFSET, task/module/vmalloc/FDT/vector placement, physical-to-virtual translation, PFN conversion, idmap aliases, and debug-virtual hooks.

## Important APIs, Types, And Functions
Key declarations include extern unsigned long setup_vectors_base(void);; extern unsigned long vectors_base;; extern u64 kernel_sec_start;; extern u64 kernel_sec_end;; extern unsigned long __pv_phys_pfn_offset;; extern u64 __pv_offset;. Important macros/constants include __ASM_ARM_MEMORY_H, PAGE_OFFSET, KERNEL_OFFSET, TASK_SIZE, TASK_SIZE, TASK_UNMAPPED_BASE, TASK_SIZE_26, MODULES_VADDR, MODULES_VADDR, MODULES_END. It depends directly on #include <linux/compiler.h>, #include <linux/const.h>, #include <linux/types.h>, #include <linux/sizes.h>, #include <mach/memory.h>, #include <asm/kasan_def.h>.

## Control Flow
Compile-time CONFIG_MMU, CONFIG_ARM_PATCH_PHYS_VIRT, LPAE, XIP, KASAN, HIGHMEM, and NoMMU branches select constants and inline assembly stubs; runtime phys/virt patching can rewrite pv-table entries before helpers such as __pa, __va, virt_to_phys, and phys_to_virt are used.

## State And Persistence
State is architectural memory-management state: page tables, ASIDs or pending switches, vmalloc sequence counters, physical/virtual offsets, and linker-defined address ranges. The header itself stores no data except declared externs and compile-time constants.

## Dependencies And Integration Points
Integrated with the generic Linux MM, scheduler, exception, and cache/TLB subsystems. Dependencies include #include <linux/compiler.h>, #include <linux/const.h>, #include <linux/types.h>, #include <linux/sizes.h>, #include <mach/memory.h>, #include <asm/kasan_def.h>, CP15 processor helpers, and configuration choices such as CONFIG_MMU, CONFIG_ARM_LPAE, CONFIG_SMP, and CPU feature selections.

## Risks And Edge Cases
Bit definitions and barriers are ABI-critical. Incorrect masks, missing cache/TLB maintenance, wrong ASID handling, or bad user-access bounds can cause silent memory corruption, stale translations, privilege bypass, or hard-to-debug boot failures.

## Test Signals
Signals include ARM allnoconfig/defconfig builds across MMU/NoMMU and LPAE variants, boot tests, vmalloc/module loading, mmap/mprotect/hugetlb where applicable, and MM selftests that exercise faults and TLB shootdowns.
