# sources/distributed-fs/ceph-client/arch/microblaze/include/asm/mmu.h

## Purpose

defines the MicroBlaze MMU context, TLB, and page-table support data

## Important APIs, Types, and Functions

Source read size: 119 lines, 4052 bytes. Declared functions: `_tlbie`. Key macros/defines:
`_ASM_MICROBLAZE_MMU_H`, `PP_RWXX`, `PP_RWRX`, `PP_RWRW`, `PP_RXRX`, `MICROBLAZE_TLB_SIZE`,
`MICROBLAZE_TLB_SKIP`, `MICROBLAZE_LMB_TLB_ID`, `TLB_LO`, `TLB_HI`, `TLB_DATA`, `TLB_TAG`,
`TLB_EPN_MASK`, `TLB_PAGESZ_MASK`, `TLB_PAGESZ(x)`, `PAGESZ_1K`, `PAGESZ_4K`, `PAGESZ_16K`,
`PAGESZ_64K`, `PAGESZ_256K`, `PAGESZ_1M`, `PAGESZ_4M`, `PAGESZ_16M`, `TLB_VALID`; plus 11 more.
Types visible in this file: `mm_context_t`. External symbols referenced/declared: `_tlbie`,
`_tlbia`, `tlb_skip`.

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
