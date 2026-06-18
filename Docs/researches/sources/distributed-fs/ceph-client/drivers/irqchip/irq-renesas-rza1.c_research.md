<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-renesas-rza1.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-renesas-rza1.c

## Purpose
`irq-renesas-rza1.c` drives the Renesas RZ/A1 IRQC, a hierarchical controller that configures eight local IRQ inputs and forwards them to a parent GIC according to an `interrupt-map`.

## Important APIs, Types, and Functions
`struct rza1_irqc_priv` stores the device, MMIO base, local irqchip, hierarchical domain, and parsed parent interrupt map. IRQ callbacks are `rza1_irqc_eoi()` and `rza1_irqc_set_type()`. Domain operations are `rza1_irqc_translate()` and `rza1_irqc_alloc()`. `rza1_irqc_parse_map()` reads `interrupt-map`, and probe/remove are `rza1_irqc_probe()`/`rza1_irqc_remove()`.

## Control Flow
Probe maps MMIO, locates the parent GIC domain, parses `interrupt-map` entries in child hwirq order, sets up an irqchip that delegates mask/unmask/retrigger to the parent but locally handles EOI and trigger type, and creates an eight-entry hierarchical domain. Allocation installs the chip for the local hwirq and forwards allocation to the stored parent fwspec. EOI clears `IRQRR` only when the pending bit is set, then EOIs the parent.

## State and Persistence
The parsed parent map is per-device software state. Hardware state is the 16-bit control and request registers. There is no power-management cache or persistent configuration.

## Dependencies and Integration Points
It depends on OF interrupt-map parsing, parent GIC hierarchy, ARM GIC binding cells, irqdomain hierarchy, platform driver registration, and parent irqchip helper callbacks.

## Risks and Edge Cases
`rza1_irqc_parse_map()` requires the `interrupt-map` entries to appear in exact child IRQ order and to target the discovered GIC node. Only low level and edge falling/rising/both are supported; high level is not accepted by local hardware. `rza1_irqc_eoi()` writes all request bits except the current one, so hardware write semantics are critical.

## Test Signals
Test all eight inputs, interrupt-map ordering validation, parent GIC allocation, level-low and edge modes, EOI clearing of `IRQRR`, and removal-domain cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-renesas-rza1.c -->
