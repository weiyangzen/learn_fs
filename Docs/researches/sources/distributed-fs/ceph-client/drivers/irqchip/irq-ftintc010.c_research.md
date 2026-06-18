# sources/distributed-fs/ceph-client/drivers/irqchip/irq-ftintc010.c

## Purpose
Implements the Faraday FTINTC010 interrupt controller, used by Gemini and Moxart variants, as a 32-line ARM root IRQ controller.

## Important APIs, Types, and Functions
`struct ft010_irq_data` stores MMIO base, chip, and domain. Chip callbacks are `ft010_irq_mask()`, `ft010_irq_unmask()`, `ft010_irq_ack()`, and `ft010_irq_set_type()`. `ft010_irqchip_handle_irq()` dispatches status bits. `ft010_of_init_irq()` performs OF initialization.

## Control Flow
Init disables CPU idle polling because of platform idle issues, maps registers, disables IRQ/FIQ masks, creates a simple domain, and installs the root handler. Domain map installs the chip with `handle_bad_irq` until a type is selected. The root handler loops while status is nonzero and handles the lowest pending bit.

## State and Persistence
Static `firq` holds singleton state. Hardware mask, clear, mode, polarity, and status registers persist line configuration. Type setup updates mode/polarity and swaps the Linux flow handler to level or edge.

## Dependencies and Integration Points
Depends on OF irqchip declarations for Faraday/Gemini/Moxart compatibles, ARM root IRQ handling, cpu idle control, and one/two-cell xlate.

## Risks and Test Signals
Risks include `WARN` but continued operation on failed mapping, default bad handlers until type setup, idle polling side effects, and unsupported trigger values returning success after installing bad handler. Test signals are trigger programming per line, status loop draining, IRQ/FIQ masks disabled at boot, and no unexpected idle regressions.
