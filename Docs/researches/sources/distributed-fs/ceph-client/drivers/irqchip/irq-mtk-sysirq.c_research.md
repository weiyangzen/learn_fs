<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-mtk-sysirq.c -->
## sources/distributed-fs/ceph-client/drivers/irqchip/irq-mtk-sysirq.c

### Purpose
`irq-mtk-sysirq.c` implements the MediaTek SYSIRQ polarity controller. It creates a hierarchy domain above the GIC and uses one or more INTPOL register banks to invert low/falling interrupts before forwarding high/rising types to the parent.

### Important APIs, Types, And Functions
`struct mtk_sysirq_chip_data` stores INTPOL base pointers, per-base word counts, and precomputed hwirq-to-base/word lookup tables. `mtk_sysirq_set_type()` updates the INTPOL bit and delegates converted type to the parent. `mtk_sysirq_domain_alloc()` installs `mtk_sysirq_chip` and allocates parent interrupts.

### Control Flow
Initialization counts MMIO address ranges, maps each range, computes total interrupt capacity from resource sizes, allocates lookup arrays mapping every hwirq to an INTPOL bank and word, creates a hierarchy domain, and initializes the spinlock. Allocation rejects PPIs, sets hwirq/chip for each requested virq, rewrites the fwspec fwnode to the parent, and allocates parent IRQs. Type setting locks the chip, sets the polarity bit for low/falling child types while converting them to high/rising parent types, clears it otherwise, writes the register, and calls the parent `irq_set_type`.

### State, Persistence, And Dependencies
Persistent state is the mapped INTPOL banks, lookup arrays, domain, and hardware polarity bits. It depends on OF resources, parent GIC-style domains, raw spinlocks, and hierarchy IRQ operations.

### Integration Points
SYSIRQ is the polarity adaptation layer for MediaTek external SPIs. Devices reference SYSIRQ while actual interrupt delivery remains through the parent GIC.

### Risks
The lookup construction assumes hwirq numbers densely cover all INTPOL bits. Parent `irq_set_type` is invoked while holding the SYSIRQ raw spinlock, so parent implementations must be IRQ-safe. Only SPI-style specs are accepted.

### Test Signals
Validate multiple register banks, all polarity conversions, parent type propagation, PPI rejection, hwirq values near bank boundaries, cleanup on mapping/allocation errors, and DTs with zero or malformed resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-mtk-sysirq.c -->
