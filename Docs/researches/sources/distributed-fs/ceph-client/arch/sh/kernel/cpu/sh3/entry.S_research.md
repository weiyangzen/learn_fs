# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh3/entry.S

## Purpose
`entry.S` is the SH3 low-level exception, TLB miss, syscall/interrupt return, and register save/restore path. It owns the VBR layout used when the CPU enters kernel mode from faults or interrupts.

## Important APIs, Types, And Functions
Exported entry labels include `tlb_miss_load`, `tlb_miss_store`, `initial_page_write`, `tlb_protection_violation_*`, `address_error_*`, `restore_regs`, `save_regs`, `save_low_regs`, `handle_interrupt`, `exception_none`, and `vbr_base`. It includes `../../entry-common.S` for common return/syscall logic.

## Control Flow
TLB miss entries set a fault code and call `handle_tlbmiss()`, falling back to `do_page_fault()` on failure. General exceptions enter at VBR offset `0x100`, call `prepare_stack()`, save registers, look up `exception_handling_table`, and jump to the handler with `ret_from_exception` as return. Interrupts enter at `0x600`, save state, derive IRQ from `INTEVT`, call `do_IRQ()` for valid hard IRQs, or dispatch special events like NMI through the exception table.

## State And Persistence
The code persists process-visible register state on the kernel stack in the layout expected by ptrace and signal code. It manipulates SR bank, BL/RB/IMASK bits, SSR/SPC, PR, GBR, MACH/MACL, and banked registers.

## Dependencies And Integration Points
It depends on `asm-offsets.h`, thread-info layout, MMU context definitions, `entry-macros.S`, C handlers such as `handle_tlbmiss`, `do_page_fault`, `do_address_error`, `do_IRQ`, and the exception table from `ex.S`.

## Risks
This code is extremely ABI-sensitive: stack layout changes must match ptrace/signal offsets. Delay-slot and bank switching errors can corrupt register state. Interrupt masking logic directly affects IRQ tracing and preemption behavior.

## Test Signals
Signals include successful boot to userspace, syscall tests, page-fault/COW tests, IRQ load tests, ptrace register validation, and hibernation or exception stress on SH3/SH4 paths that reuse this file.
