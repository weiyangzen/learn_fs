<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-mips-gic.c -->
## sources/distributed-fs/ceph-client/drivers/irqchip/irq-mips-gic.c

### Purpose
`irq-mips-gic.c` implements the MIPS Global Interrupt Controller. It handles shared external interrupts, local per-VPE interrupts, EIC routing, per-cluster register access, SMP affinity, optional IPI domains, and CPU hotplug startup.

### Important APIs, Types, And Functions
Global state includes `mips_gic_base`, `gic_irq_domain`, shared interrupt count, CPU pin, per-CPU pending masks, and IPI reservation bitmaps. `gic_of_init()` initializes hardware and domains. `gic_handle_shared_int()` and `gic_handle_local_int()` dispatch pending interrupts. `gic_set_type()` and `gic_set_affinity()` program polarity, trigger, dual-edge, VP routing, and per-CPU masks. `gic_register_ipi_domain()` allocates per-CPU shared vectors for IPIs.

### Control Flow
Init selects an available CPU vector, maps or inherits the GIC base, enables the GIC through the CM when present, reads shared interrupt capacity, installs either an EIC vector handler or a chained CPU IRQ handler, creates a domain covering local plus shared hwirqs, registers IPIs, records the EIC bind callback, resets shared interrupt polarity/trigger/masks in every cluster, and registers CPU hotplug startup. Dispatch first handles local pending/masked bits, then reads shared pending bitmaps, intersects with the current CPU's software mask, and handles each mapped hwirq. Allocation maps local interrupts to percpu handlers or shared interrupts to routed level chips.

### State, Persistence, And Dependencies
State includes hardware routing registers, per-CPU shared masks, all-VPE local interrupt metadata, IPI reserved/available bitmaps, and CPU hotplug callbacks. Dependencies include MIPS CM/CPS support, GIC register accessors, OF bindings, cpuhotplug, SMP affinity, and generic IRQ/IPI infrastructure.

### Integration Points
The GIC can replace direct CPU interrupt handling, supplies timer/perf/FDC local IRQ mappings, exports `gic_get_c0_*_int()` helpers, and provides a DOMAIN_BUS_IPI domain for SMP cross-calls.

### Risks
Cluster redirection locking is subtle; wrong effective affinity can program the wrong cluster. IPI allocation reserves shared vectors that must not collide with normal shared IRQs. Local interrupts that are not routable fall back to CPU IRQs or fail mapping. `gic_ipi_domain_alloc()` checks availability using a loop that is sensitive to the requested count and base index.

### Test Signals
Test VEIC and non-VEIC boot, inherited and DT-specified base addresses, shared IRQ type/affinity changes across clusters, CPU hotplug restoring local masks, IPI allocation/free/send, reserved vector conflicts, timer/perf/FDC helper mappings, and spurious or masked shared interrupts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-mips-gic.c -->
