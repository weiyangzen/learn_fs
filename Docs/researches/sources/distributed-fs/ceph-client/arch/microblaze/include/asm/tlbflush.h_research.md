# sources/distributed-fs/ceph-client/arch/microblaze/include/asm/tlbflush.h

## Purpose

declares local/global TLB flush helpers

## Important APIs, Types, and Functions

Source read size: 53 lines, 1687 bytes. Includes: `linux/sched.h`, `linux/threads.h`,
`asm/processor.h`, `asm/mmu.h`, `asm/page.h`. Defined functions: `local_flush_tlb_all`,
`local_flush_tlb_mm`, `local_flush_tlb_page`, `local_flush_tlb_range`, `flush_tlb_pgtables`.
Declared functions: `Copyright`. Key macros/defines: `_ASM_MICROBLAZE_TLBFLUSH_H`, `__tlbia()`,
`__tlbie(x)`, `flush_tlb_kernel_range(start, end)`, `update_mmu_cache_range(vmf, vma, addr, ptep,
nr)`, `update_mmu_cache(vma, addr, pte)`, `flush_tlb_all`, `flush_tlb_mm`, `flush_tlb_page`,
`flush_tlb_range`. External symbols referenced/declared: `_tlbie`, `_tlbia`.

## Control Flow and Behavior

the header provides macros, inline functions, type definitions, or declarations that are expanded
into core MicroBlaze kernel, MM, entry, scheduler, IRQ, tracing, or driver code

## State and Persistence

state is generally compile-time definitions; inline helpers may manipulate MSR bits, TLB entries,
page tables, CPU registers, user memory, or task/thread state at runtime

## Dependencies and Integration Points

integrates with asm-generic fallbacks, MicroBlaze low-level assembly, generic
MM/scheduler/IRQ/syscall/cache subsystems, and device-tree platform code

## Risks and Test Signals

because these headers sit on architecture-wide interfaces, small changes can break boot or ABI
assumptions; allmodconfig builds plus targeted MM, uaccess, futex, signal, and tracing tests are
signals
