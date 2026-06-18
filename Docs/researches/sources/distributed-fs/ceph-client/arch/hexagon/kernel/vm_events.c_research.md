# sources/distributed-fs/ceph-client/arch/hexagon/kernel/vm_events.c

## Purpose

`vm_events.c` bridges VM interrupt events into generic Linux IRQ handling. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

The key API is `arch_do_IRQ`, called from assembly event entry with a populated `pt_regs`. Concrete declarations observed in the file: Includes: `linux/kernel.h`, `linux/sched/debug.h`, `asm/registers.h`, `linux/irq.h`, `linux/hardirq.h`. Types referenced or declared: `pt_regs`. Functions/syscalls: `show_regs`, `arch_do_IRQ`.

## Control Flow, State, And Persistence

Runtime flow enters IRQ context, decodes the IRQ cause, invokes generic IRQ handling, and exits IRQ context for return processing.

## Dependencies And Integration Points

It integrates with `irq_cpu.c`, `vm_entry.S`, generic IRQ core, and hardirq accounting.

## Risks And Test Signals

Risks are wrong IRQ decode, missing irq_enter/exit pairing, or failure under nested interrupts. Test signals are timer/device interrupts and IRQ accounting traces.
 A local static signal for this file is that it has 86 lines and 2449 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
