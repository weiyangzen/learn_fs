<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-madera.c -->
## sources/distributed-fs/ceph-client/drivers/irqchip/irq-madera.c

### Purpose
`irq-madera.c` exposes Cirrus Logic Madera codec interrupt status bits as Linux IRQs through the regmap IRQ framework. It is an MFD child driver for Madera codecs rather than a memory-mapped SoC interrupt controller.

### Important APIs, Types, And Functions
`madera_irqs[]` maps `MADERA_IRQ_*` IDs to status register offsets and masks. `madera_irq_chip` describes the regmap IRQ chip with status, mask, ack bases, runtime PM, and 32 status registers. `madera_irq_probe()` determines host IRQ polarity, programs codec polarity when needed, and calls `regmap_add_irq_chip()`. PM callbacks temporarily disable/re-enable the host IRQ across suspend phases.

### Control Flow
Probe gets the parent `struct madera`, determines IRQ flags from platform data or the existing host IRQ descriptor, rejects edge-triggered host IRQs, optionally switches codec IRQ polarity for active-high hosts, registers the regmap IRQ chip with `IRQF_ONESHOT`, and stores the IRQ device pointer for sibling MFD users. Remove clears the pointer and unregisters the regmap IRQ chip. Sleep PM disables the host IRQ before runtime PM becomes unavailable, re-enables it during noirq for wake events, disables it again on resume_noirq, and finally re-enables normal handling.

### State, Persistence, And Dependencies
Persistent state lives in the parent MFD `struct madera`: regmap, host IRQ, IRQ data, platform IRQ flags, and `irq_dev`. The driver depends on regmap IRQ support, runtime PM, Madera register definitions, and parent MFD probe ordering.

### Integration Points
Sibling codec components consume IRQs from the regmap domain created here. The parent MFD supplies the physical IRQ and register map.

### Risks
Host IRQs must be level-triggered because the codec status/mask model is serviced through regmap. Suspend ordering is delicate: interrupts are enabled in noirq only for wake-capable handling. Polarity defaults to active-low if firmware/platform data is silent.

### Test Signals
Probe with active-low and active-high host IRQs, reject edge-triggered hosts, validate regmap child IRQ delivery for representative status bits, runtime PM access during IRQ handling, suspend wake behavior, and remove cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-madera.c -->
