<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-mmp.c -->
## sources/distributed-fs/ceph-client/drivers/irqchip/irq-mmp.c

### Purpose
`irq-mmp.c` implements Marvell MMP/PXA-style ICU interrupt handling, including primary ICU dispatch and optional cascaded MMP2 mux interrupt controllers.

### Important APIs, Types, And Functions
`struct icu_chip_data` stores IRQ counts, virtual base, cascade IRQ, mask/status registers, configuration masks, and domain. `mmp_init_bases()` creates the primary domain and static mappings. `mmp_handle_irq()` and `mmp2_handle_irq()` read selected pending hwirqs from CPU-specific selector registers. `icu_mux_irq_demux()` demultiplexes cascaded mux controllers. `icu_irq_chip` provides mask, mask_ack, and unmask.

### Control Flow
Primary initialization maps ICU registers, reads `mrvl,intc-nr-irqs`, creates a linear domain, eagerly maps every hwirq to stable Linux IRQs, configures SoC-specific enable/disable masks, and installs the exception handler. MMP3 may map a second ICU base. Mux initialization interprets the legacy offset-style `reg` property, creates a child domain, maps all mux hwirqs, records optional PMIC clear behavior, and chains the mux parent IRQ. Top-level dispatch reads `PJ1_INT_SEL` or `PJ4_INT_SEL`; mux dispatch loops until no unmasked status bits remain.

### State, Persistence, And Dependencies
Persistent state is held in global ICU bases, `icu_data[]`, virtual IRQ bases, domains, and `max_icu_nr`. It depends on OF resources, ARM exception handling, irqdomain mapping, chained IRQ helpers, and MMP SoC-specific PMIC clear code.

### Integration Points
It is the root interrupt controller for MMP variants and a cascade point for muxed secondary interrupt blocks. Device-tree users may depend on stable legacy-style virq bases due to eager mapping.

### Risks
The driver relies on global arrays and fixed `MAX_ICU_NR`. Mux handling uses virtual IRQ base arithmetic instead of domain lookup. Primary mask operations differ for ICU0 versus mux controllers. Historical `reg` offsets in mux nodes are not normal bus addresses.

### Test Signals
Boot MMP, MMP2, and MMP3 variants; verify primary selector dispatch, mux cascade loops, mask/unmask for ICU0 and mux controllers, PMIC interrupt clear path, malformed `mrvl,intc-nr-irqs` or `reg`, and stable IRQ numbering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-mmp.c -->
