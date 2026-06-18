# sources/distributed-fs/ceph-client/arch/sparc/kernel/irq.h

## Purpose
`irq.h` is the local sparc32 IRQ interface shared by platform IRQ implementations and low-level entry code.

## Important APIs, Types, and Functions
It defines `struct irq_bucket`, sun4m hard/soft interrupt bit macros, sun4d IRQ limits, `irq_map`, sun4m interrupt register layouts, feature bits, and `struct sparc_config`. It declares `irq_alloc()`, `irq_link()`, `irq_unlink()`, `handler_irq()`, `leon_get_irqmask()`, `sparc_floppy_irq()`, `sun4m_nmi()`, `sun4d_handler_irq()`, and optional `sun4d_ipi_interrupt()`.

## Control Flow and State
There is no implementation. The header defines how virtual IRQs map from platform hardware identifiers/PILs into linked `irq_bucket` chains, and how platform init functions provide timer and IRQ construction callbacks through `sparc_config`.

## Persistence and Dependencies
Persistent shared state is `irq_map` and `sparc_config`, with external sun4m interrupt-controller MMIO pointers. Dependencies include platform devices and CPU type definitions.

## Integration Points, Risks, and Test Signals
Integration includes `irq_32.c`, sun4m/sun4d/LEON IRQ controller files, trap handlers in `entry.S`, timer setup, and floppy fast interrupt support. Risks are ABI/layout mismatch with assembly and platform files, insufficient `SUN4D_MAX_IRQ`, and incorrect feature flags causing timer misuse. Test signals are platform-specific IRQ init, `/proc/interrupts` counts, timer tick delivery, sun4d virtual IRQ allocation, and SMP IPI handling.
