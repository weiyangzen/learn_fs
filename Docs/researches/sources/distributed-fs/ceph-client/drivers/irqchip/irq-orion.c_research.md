<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-orion.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-orion.c

## Purpose
`irq-orion.c` supports Marvell Orion interrupt controllers. It contains a root controller for SoC interrupt cause/mask banks and a cascaded bridge controller used behind a parent interrupt.

## Important APIs, Types, and Functions
The main controller uses `orion_handle_irq()` and `orion_irq_init()`. It creates a generic-chip linear domain, one 32-bit generic chip per MMIO resource, and uses `irq_gc_mask_clr_bit`/`irq_gc_mask_set_bit` over `ORION_IRQ_MASK`. The bridge path uses `orion_bridge_irq_handler()`, `orion_bridge_irq_startup()`, and `orion_bridge_irq_init()` with `ORION_BRIDGE_IRQ_CAUSE` and `ORION_BRIDGE_IRQ_MASK`.

## Control Flow
For the root controller, OF address count determines how many 32-source banks exist. Probe creates the domain, maps each resource, masks every source, and installs `orion_handle_irq()` as the architecture handler. The handler iterates all banks, intersects cause with `mask_cache`, takes the highest set bit with `__fls()`, and dispatches it. The bridge controller creates a 32-source or DT-sized domain, maps its parent IRQ, masks and clears all child sources, then installs a chained handler that demultiplexes pending bridge bits.

## State and Persistence
Runtime state is the global `orion_irq_domain`, generic-chip `mask_cache`, and mapped MMIO registers. The driver does not save/restore state explicitly and relies on platform-level retention or boot-time reinitialization.

## Dependencies and Integration Points
It uses OF address and IRQ parsing, `irq_generic_chip_ops`, generic-chip helpers, `request_mem_region()`, `ioremap()`, `set_handle_irq()`, and chained IRQ handling. It is declared for `marvell,orion-intc` and `marvell,orion-bridge-intc`.

## Risks and Edge Cases
The root init path panics on allocation or mapping failures because no interrupt controller is recoverable during early boot. Bridge `IRQ_CAUSE` can assert even while masked, so startup ACKs stale causes before unmasking; missing that ordering would deliver old events. Bridge cleanup paths do not undo prior allocations on later failures because this is early irqchip setup.

## Test Signals
Test by booting with multiple register banks, checking masked sources remain silent, validating bridge startup does not replay stale pending bits, exercising chained parent IRQ delivery, and confirming DT `marvell,#interrupts` sizes the bridge domain correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-orion.c -->
