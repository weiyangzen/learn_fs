<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-renesas-irqc.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-renesas-irqc.c

## Purpose
`irq-renesas-irqc.c` implements the Renesas IRQC platform driver, a demultiplexer for up to 32 external interrupts with configurable level/edge detection and wake propagation to parent IRQs.

## Important APIs, Types, and Functions
`struct irqc_priv` stores mapped registers, CPU interrupt base, per-line parent IRQs, generic chip, irqdomain, device, and wakeup counter. `irqc_irq_set_type()` writes `IRQC_CONFIG(n)` sense bits, `irqc_irq_set_wake()` propagates wake to the requested parent IRQ, and `irqc_irq_handler()` checks and clears `DETECT_STATUS` before dispatching a child domain IRQ. Probe/remove/suspend are `irqc_probe()`, `irqc_remove()`, and `irqc_suspend()`.

## Control Flow
Probe enables runtime PM, collects one to 32 parent IRQ resources, maps MMIO, creates a linear generic-chip domain, configures the generic chip to use `IRQC_EN_SET`/`IRQC_EN_STS`, installs set-type and set-wake callbacks, associates the PM device, and requests each parent IRQ with the demux handler. The handler validates the hardware detect bit for its line, clears it by writing the bit back, and dispatches through `generic_handle_domain_irq()`.

## State and Persistence
State is per device instance. The generic chip tracks masks in hardware enable/status registers, while `wakeup_path` records wake-enabled children for suspend. There is no explicit register cache for trigger type or enable state across power loss.

## Dependencies and Integration Points
The driver depends on platform resources, runtime PM, generic IRQ chips with nested-lock init, irqdomain linear mapping, and OF compatible `renesas,irqc`. It registers at `postcore_initcall()`.

## Risks and Edge Cases
`IRQC_EN_STS` is used as the disable register for generic-chip masking, so hardware semantics must match mask-disable helper expectations. Every child line needs a parent IRQ resource; missing optional resources terminate enumeration. Wake count imbalance or parent wake failure is not rolled back.

## Test Signals
Validate all supported trigger types, per-line detect clear, one-line and multi-line instances, runtime PM activation, wake propagation, generic-chip mask/unmask register writes, and clean domain removal on probe failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-renesas-irqc.c -->
