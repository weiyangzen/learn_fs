<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-sa11x0.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-sa11x0.c

## Purpose
`irq-sa11x0.c` implements generic IRQ handling for SA11x0 systems without device tree. It maps the 32 internal interrupt controller sources, handles root dispatch, wake control, and syscore save/restore.

## Important APIs, Types, and Functions
Global state is `iobase`, `sa1100_normal_irqdomain`, and `sa1100irq_state`. Chip callbacks are `sa1100_mask_irq()`, `sa1100_unmask_irq()`, and `sa1100_set_wake()`. Domain mapping is `sa1100_normal_irqdomain_map()`. PM callbacks are `sa1100irq_suspend()` and `sa1100irq_resume()`. Root dispatch is `sa1100_handle_irq()`, and legacy init is `sa11x0_init_irq_nodt()`.

## Control Flow
`sa11x0_init_irq_nodt()` maps the interrupt controller, disables all IRQs, configures all sources as IRQ rather than FIQ, sets `ICCR` for wait-on-irq behavior, creates a simple 32-entry domain using the supplied legacy IRQ base, and installs the root handler. The handler repeatedly reads pending and mask registers, dispatches the first set enabled interrupt, and stops when no enabled pending bits remain.

## State and Persistence
Suspend caches `ICMR`, `ICLR`, and `ICCR`, marks state saved, and disables GPIO-based interrupts by preserving only upper internal-mask bits. Resume restores cached control, level, and mask registers. Wake configuration is delegated to `sa11x0_sc_set_wake()`.

## Dependencies and Integration Points
The file depends on legacy SA1100 platform init, `soc/sa1100/pwer.h`, syscore ops, irqdomain one/two-cell translation, architecture root IRQ handler setup, and the public `irq-sa11x0.h` init declaration.

## Risks and Edge Cases
It is nodt-only and assumes a single controller. `irq_ack` masks the source because internal IRQs generally need no explicit ACK; GPIO IRQs are handled elsewhere. Suspend masking of GPIO-based interrupts uses a fixed `0xfffff000` boundary, so source numbering must match SA1100 hardware.

## Test Signals
Validate legacy boot with correct IRQ base, root dispatch ordering, mask/unmask register updates, wake enable propagation, suspend/resume register restore, and no FIQ routing after initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-sa11x0.c -->
