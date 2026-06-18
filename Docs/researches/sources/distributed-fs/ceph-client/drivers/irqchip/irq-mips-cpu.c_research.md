<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-mips-cpu.c -->
## sources/distributed-fs/ceph-client/drivers/irqchip/irq-mips-cpu.c

### Purpose
`irq-mips-cpu.c` implements the base MIPS CPU interrupt controller for the eight CP0 interrupt lines. It also optionally exposes software interrupt lines as an IPI domain on MIPS MT systems.

### Important APIs, Types, And Functions
`mips_cpu_irq_controller` masks/unmasks CP0 status interrupt bits. `mips_mt_cpu_irq_controller` adds MIPS MT software interrupt ack/startup and IPI send support. `plat_irq_dispatch()` is the weak default top-level dispatcher. `mips_cpu_intc_map()` maps hwirqs to percpu handlers. `mips_cpu_register_ipi_domain()` creates a two-entry IPI hierarchy domain when `CONFIG_GENERIC_IRQ_IPI` is enabled.

### Control Flow
Initialization clears all CP0 interrupt mask and cause bits, creates a legacy 8-entry IRQ domain, and optionally registers the IPI domain. The default dispatcher computes `cause & status & ST0_IM`, reports spurious interrupts if none are pending, then processes highest-priority pending bits, routing software interrupts through the IPI domain and others through the CPU domain. Mask/unmask operations set or clear CP0 status bits with hazard barriers.

### State, Persistence, And Dependencies
Persistent state is the CPU IRQ domain, optional IPI domain, and per-domain bitmap state for allocated software IPIs. It depends on MIPS CP0 register helpers, MIPS MT VPE manipulation, generic IPI support, and architecture setup constants.

### Integration Points
This is the fallback/root CPU interrupt controller for MIPS systems and can be the parent for higher-level interrupt controllers such as MIPS GIC.

### Risks
Software interrupt IPIs are only valid for sibling VPEs on the local core. `plat_irq_dispatch()` is weak and may be replaced by platform code, so behavior varies. Vector interrupt mode installs the same dispatch handler per hardware line. The IPI allocator has only two hardware slots.

### Test Signals
Boot with and without MIPS MT, software interrupt IPI send/receive, CP0 mask/unmask behavior, spurious dispatch accounting, vector interrupt handler setup, and exhaustion of the two IPI slots.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-mips-cpu.c -->
