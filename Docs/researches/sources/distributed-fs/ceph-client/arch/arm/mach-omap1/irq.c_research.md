<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/irq.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/irq.c

## Purpose
Implements the OMAP1 MPU interrupt controller integration, including bank selection per SoC, legacy irqdomain creation, interrupt dispatch, masking, wake support, and bank-specific trigger setup.

## Important APIs, Types, and Functions
Key entry points are `omap1_init_irq()` and IRQ entry `omap1_handle_irq()`. Internal helpers include `omap_ack_irq()`, `omap_mask_ack_irq()`, `omap_irq_set_cfg()`, `omap_alloc_gc()`, and bank MMIO accessors.

## Control Flow
Initialization chooses interrupt banks based on `cpu_is_*`, ioremaps each bank, allocates legacy IRQ descriptors/domain, masks and clears banks, programs ILR trigger/priority values from `trigger_map`, installs generic irqchips, unmasks the L2 cascade, and sets the ARM IRQ handler. The IRQ handler loops pending L1 interrupts, resolves FIQ/IRQ source registers, follows the L2 cascade when needed, and calls `generic_handle_domain_irq()`.

## State and Persistence Behavior
Static state tracks `irq_banks`, `irq_bank_count`, `omap_l2_irq`, and `domain`; each bank tracks mapped base, trigger map, and wake-enable cache via generic irqchip.

## Dependencies and Integration Points
Depends on `irqs.h` numbering, `hardware.h` register offsets, ARM exception dispatch, generic irqchip, irqdomain legacy mapping, and revision detection from `id.c`.

## Risks
Wrong CPU detection or trigger maps can leave interrupts masked, mis-triggered, or routed to wrong Linux IRQs. The code assumes at least two banks when clearing L2/control state. Ioremap failure returns early without a full IRQ controller.

## Test Signals
Boot each enabled OMAP1 family and verify timer, GPIO, UART, DMA, I2C, and cascade IRQs arrive. Suspend tests should cover `irq_set_wake`. Negative testing can force ioremap/allocation failure in fault-injection builds.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/irq.c -->
