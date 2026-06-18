# sources/distributed-fs/ceph-client/arch/hexagon/kernel/irq_cpu.c

## Purpose

`irq_cpu.c` implements the Hexagon CPU interrupt chip, with mask, unmask, EOI, wake, and `init_IRQ` logic over HVM interrupt operations. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

The important callbacks are `mask_irq_num`, `unmask_irq`, `eoi_irq`, `set_wake`, and the `irq_chip` registered for CPU interrupts. Concrete declarations observed in the file: Includes: `linux/interrupt.h`, `asm/irq.h`, `asm/hexagon_vm.h`. Types referenced or declared: `irq_data`, `irq_chip`. Functions/syscalls: `mask_irq`, `mask_irq_num`, `unmask_irq`, `eoi_irq`, `set_wake`, `init_IRQ`.

## Control Flow, State, And Persistence

Interrupt setup initializes the IRQ chip, while runtime IRQ flow masks/unmasks/posts EOI through `__vmintop_*` operations.

## Dependencies And Integration Points

It depends on generic IRQ core and `asm/hexagon_vm.h`; it integrates with `vm_events.c`, SMP IPIs, and timer IRQs.

## Risks And Test Signals

Risks are wrong interrupt numbers, missing EOI, or unsafe wake semantics. Test signals are timer interrupts, IPIs, device IRQ delivery, and `/proc/interrupts` progression.
 A local static signal for this file is that it has 78 lines and 2180 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
