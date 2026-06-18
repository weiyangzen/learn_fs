# sources/distributed-fs/ceph-client/drivers/irqchip/irq-davinci-cp-intc.c

## Purpose
Implements TI DaVinci/Common Platform Interrupt Controller as a legacy root IRQ controller.

## Important APIs, Types, and Functions
Globals store MMIO base and irqdomain. The chip callbacks are `davinci_cp_intc_ack_irq()`, mask/unmask, and `davinci_cp_intc_set_irq_type()`. `davinci_cp_intc_handle_irq()` reads the prioritized interrupt register. `davinci_cp_intc_do_init()` performs hardware and domain initialization.

## Control Flow
OF init reads `ti,intc-size` and MMIO resource. Hardware init requests/maps registers, disables global/host/system interrupts, clears status, sets normal/no-nesting mode, enables host IRQ, maps all priorities to channel 7, allocates legacy descriptors, creates a legacy domain, installs the root handler, and enables global interrupts. Dispatch reads GPIR and handles the indicated IRQ unless the NONE bit signals spurious.

## State and Persistence
Hardware enable, status, polarity, type, channel-map, host, and global registers persist controller configuration. Software state is global base/domain only; no mask cache is kept.

## Dependencies and Integration Points
Depends on OF, legacy irq descriptor allocation, ARM exception handling, and one/two-cell xlate. It integrates as a root controller for TI cp_intc-based SoCs.

## Risks and Test Signals
Risks include unexplained nIRQ disable during mask, fixed edge handler despite programmable level/edge type, missing cleanup after request/map failures, and priority/channel defaults. Test signals are no spurious GPIR NONE messages, correct polarity/type writes for DT/requested triggers, and IRQ counts for cp_intc children.
