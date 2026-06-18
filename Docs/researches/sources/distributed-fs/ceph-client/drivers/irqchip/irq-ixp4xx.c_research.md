<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-ixp4xx.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-ixp4xx.c

## Purpose
Implements the Intel IXP4xx interrupt controller for 32-source and 64-source SoC variants, including the primary exception IRQ handler and a hierarchical irqdomain suitable for child GPIO irqchips.

## Important APIs, Types, And Functions
`struct ixp4xx_irq` stores MMIO base, variant flag, irqchip, and domain. Important functions are `ixp4xx_of_init_irq()`, `ixp4xx_irq_setup()`, `ixp4xx_handle_irq()`, `ixp4xx_irq_mask()`, `ixp4xx_irq_unmask()`, `ixp4xx_set_irq_type()`, and hierarchical domain translate/alloc callbacks.

## Control Flow
OF init maps the controller, detects whether the compatible has the upper 32 IRQ registers, routes sources to IRQ rather than FIQ, disables all inputs, creates a linear domain of 32 or 64 hwirqs, and installs `ixp4xx_handle_irq()`. Runtime handling reads `ICIP`, dispatches all low pending bits, then reads `ICIP2` and dispatches high bits on 64-source variants.

## State And Persistence
A single static `ixirq` represents the controller. Hardware mask state lives in ICMR/ICMR2; FIQ routing is disabled by writing ICLR/ICLR2. No PM callbacks or saved masks are present.

## Dependencies And Integration Points
It depends on ARM exception handling, OF mapping, hierarchical irqdomains, and compatibles `intel,ixp42x-interrupt`, `ixp43x`, `ixp45x`, and `ixp46x`. GPIO IRQ users can allocate below this domain.

## Risks
Only level-high interrupts are accepted. The controller is represented by one global instance. High-register handling must be correct for IXP43x/45x/46x, while 42x only has 32 sources. The TODO notes that some legacy consumers may not call set_type.

## Test Signals
Test 32-source and 64-source hardware, low/high register pending dispatch, mask/unmask for hwirqs below and above 32, level-high type enforcement, GPIO child irqchip integration, and boot-time primary handler installation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-ixp4xx.c -->
