# sources/distributed-fs/ceph-client/arch/m68k/kernel/irq.c

## Purpose

`irq.c` is the common IRQ entry shim and interrupt accounting support for m68k. It converts low-level architecture interrupt entry into generic Linux IRQ handling and provides the architecture-specific `/proc/interrupts` error line.

## Important APIs, Types, and Functions

`asmlinkage void do_IRQ(int irq, struct pt_regs *regs)` wraps `generic_handle_irq()`. `atomic_t irq_err_count` counts unexpected or spurious interrupts. `int arch_show_interrupts(struct seq_file *p, int prec)` prints the `ERR` line.

## Control Flow

The low-level interrupt path calls `do_IRQ()` with a decoded IRQ number and register frame. `do_IRQ()` installs `regs` through `set_irq_regs()`, calls `irq_enter()`, dispatches to the generic handler with `generic_handle_irq(irq)`, calls `irq_exit()`, and restores the previous IRQ register context.

## State and Persistence Behavior

This file persists only the global atomic `irq_err_count`. Per-CPU IRQ context state is temporarily swapped around each interrupt by `set_irq_regs()`.

## Dependencies and Integration Points

It depends on generic IRQ accounting and dispatch APIs, `struct pt_regs` from `<asm/traps.h>`, and `ints.c::handle_badint()` for incrementing `irq_err_count`. `/proc/interrupts` calls `arch_show_interrupts()` through generic seq-file code.

## Risks and Edge Cases

If low-level entry passes an out-of-range IRQ, generic IRQ code will handle the error path but the architecture shim has no local range check. Missing `set_irq_regs()` restoration would confuse nested interrupt diagnostics; this implementation restores unconditionally after `irq_exit()`.

## Test Signals

Interrupt-heavy boot, timer IRQ delivery, nested IRQ tracing, and `/proc/interrupts` should show normal device counts plus a stable `ERR` line. Triggering a bad vector should increment `irq_err_count`.
