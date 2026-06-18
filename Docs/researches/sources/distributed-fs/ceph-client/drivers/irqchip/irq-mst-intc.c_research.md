<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-mst-intc.c -->
## sources/distributed-fs/ceph-client/drivers/irqchip/irq-mst-intc.c

### Purpose
`irq-mst-intc.c` implements the MStar/MediaTek MST interrupt controller, a hierarchical SPI adapter that masks, polarity-inverts, and optionally EOIs interrupts before forwarding them to a parent GIC-like controller.

### Important APIs, Types, And Functions
`struct mst_intc_chip_data` stores MMIO base, hwirq range mapping, lock, `no_eoi`, and PM list state. `mst_intc_domain_translate()` validates GIC-style OF specs. `mst_intc_domain_alloc()` installs `mst_intc_chip` and allocates the shifted parent SPI range. `mst_irq_chip_set_type()` programs reverse polarity and forces parent level-high. PM helpers save and restore polarity registers.

### Control Flow
OF init finds the parent domain, reads `mstar,irqs-map-range`, maps registers, records `irq_start` and `nr_irqs`, creates a hierarchy domain, and adds the controller to a global PM list. Allocation rejects PPIs, maps local hwirqs to parent `irq_start + hwirq`, and always passes `IRQ_TYPE_LEVEL_HIGH` to the parent because the MST block latches/normalizes signals. Mask/unmask set or clear bits in `INTC_MASK`, EOI sets `INTC_EOI` unless disabled, and type programming controls `INTC_REV_POLARITY`.

### State, Persistence, And Dependencies
State includes per-controller chip data, hardware polarity/mask/eoi registers, and a global suspend list guarded by syscore callbacks. Dependencies include OF hierarchy domains, GIC-style interrupt cells, syscore PM, and raw spinlocks.

### Integration Points
This driver is inserted between device SPIs and the parent interrupt controller. It maps a local range onto a contiguous parent SPI range specified by firmware.

### Risks
The parent always sees level-high, so local edge semantics rely on MST latching and EOI. `mstar,intc-no-eoi` changes completion semantics and must match hardware. PM only saves polarity, not mask state. Range math must match firmware's parent SPI numbering.

### Test Signals
Validate `mstar,irqs-map-range`, reject PPI specs, trigger all supported polarity/type modes, verify EOI/no-EOI behavior, parent allocation parameters, suspend/resume polarity restore, and multiple controller instances on the PM list.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-mst-intc.c -->
