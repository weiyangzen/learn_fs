<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-rda-intc.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-rda-intc.c

## Purpose
`irq-rda-intc.c` is the root interrupt controller driver for RDA8810PL SoCs. It exposes 32 level-triggered interrupt sources to the Linux generic IRQ subsystem.

## Important APIs, Types, and Functions
Global state is `rda_intc_base` and `rda_irq_domain`. Chip callbacks are `rda_intc_mask_irq()`, `rda_intc_unmask_irq()`, and `rda_intc_set_type()`. `rda_handle_irq()` reads `RDA_INTC_FINALSTATUS` and dispatches pending bits. `rda_irq_map()` installs `rda_irq_chip`, and `rda8810_intc_init()` maps registers, masks all sources, creates the domain, and installs the root handler.

## Control Flow
Early OF init maps the controller with `of_io_request_and_map()`, writes `RDA_IRQ_MASK_ALL` to the mask-clear register, creates a 32-entry linear domain, and calls `set_handle_irq()`. During an IRQ exception, `rda_handle_irq()` reads final masked status, repeatedly handles the highest set bit through `generic_handle_domain_irq()`, and clears the bit from the local software copy.

## State and Persistence
The controller has volatile mask and status registers. The driver does not keep per-interrupt software state beyond the irqdomain and mapped base address. No suspend cache is provided.

## Dependencies and Integration Points
It depends on OF irqchip declaration for `rda,8810pl-intc`, Linux irqdomain one-cell translation, ARM exception handler plumbing, and `handle_level_irq`.

## Risks and Edge Cases
`rda_intc_set_type()` accepts high or low level trigger requests only; edge trigger consumers fail. Initialization cleanup only unmaps on domain allocation failure and does not release the requested region explicitly. The root handler assumes final status is already mask-filtered by hardware.

## Test Signals
Boot-time domain creation, mask/unmask register writes, rejection of edge-triggered DT consumers, correct highest-bit dispatch, and no repeated level IRQs after the device deasserts are the key validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-rda-intc.c -->
