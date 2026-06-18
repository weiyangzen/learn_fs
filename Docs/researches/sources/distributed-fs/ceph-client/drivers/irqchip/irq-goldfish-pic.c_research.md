<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-goldfish-pic.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-goldfish-pic.c

## Purpose
Implements the 32-source Goldfish virtual platform PIC for MIPS/Goldfish systems as a cascaded interrupt controller behind one parent IRQ.

## Important APIs, Types, And Functions
`struct goldfish_pic_data` stores the MMIO base and legacy irqdomain. `goldfish_pic_of_init()` maps resources, allocates a generic chip named `GFPIC`, configures enable/disable registers, creates the legacy domain, and installs `goldfish_pic_cascade()`. The cascade handler reads `GFPIC_REG_IRQ_PENDING`, handles each set bit, and dispatches through `generic_handle_domain_irq()`.

## Control Flow
OF init maps the parent IRQ and register block, disables all PIC interrupts, sets generic chip callbacks to `irq_gc_unmask_enable_reg` and `irq_gc_mask_disable_reg`, creates a 32-entry legacy domain rooted at hardware base 8, and chains the parent IRQ. Runtime cascade drains all pending bits from high to low using `__fls()`.

## State And Persistence
State is limited to the allocated private struct, generic chip mask cache, irqdomain, and MMIO enable/disable state. There is no suspend/resume handler or dynamic allocation after initialization.

## Dependencies And Integration Points
It depends on OF IRQ/address parsing, generic irqchip helpers, chained IRQ support, and the `google,goldfish-pic` compatible. It integrates with the parent interrupt controller through a single parent IRQ and exposes child IRQs via a one-cell legacy domain.

## Risks
The fixed `GFPIC_IRQ_BASE` can conflict if platform IRQ numbering assumptions change. The cascade handler does not mask while dispatching each source, so level sources depend on child handlers and hardware state behaving normally. Error unwinding must dispose the parent mapping and destroy the generic chip.

## Test Signals
Boot a Goldfish DT platform, confirm parent cascade registration, map all 32 child interrupts, trigger multiple pending bits simultaneously, verify mask/unmask MMIO effects, and test init failure paths with missing parent IRQ or MMIO resource.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-goldfish-pic.c -->
