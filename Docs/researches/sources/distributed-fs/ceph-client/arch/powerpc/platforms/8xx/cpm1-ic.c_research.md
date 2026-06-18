# sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/cpm1-ic.c

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/cpm1-ic.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/cpm1-ic.c

### Purpose
Platform driver for the CPM1 interrupt controller and CPM error interrupt on MPC8xx systems.

### Important APIs, Types, And Functions
Defines `struct cpm_pic_data`, irq_chip callbacks `cpm_mask_irq()`, `cpm_unmask_irq()`, `cpm_end_irq()`, cascade helpers `cpm_get_irq()` and `cpm_cascade()`, IRQ-domain ops, `cpm_pic_probe()`, `cpm_pic_driver`, and `cpm_error_driver`. It registers via `arch_initcall(cpm_pic_init)` and `subsys_initcall(cpm_error_init)`.

### Control Flow
The CPM PIC driver probes `fsl,cpm1-pic` or legacy CPM nodes, maps registers, initializes CICR/CIMR, creates a 64-entry IRQ domain, and chains the parent IRQ. The cascade path acknowledges vector selection and dispatches mapped child IRQs. The error driver requests a no-op error IRQ handler.

### State, Persistence, And Dependencies
State includes mapped CPM PIC registers, IRQ domain, chained handler data, and requested error IRQ. No durable persistence. Dependencies include platform devices, OF matching, irq_domain, chained IRQ APIs, and CPM register definitions.

### Integration Points
Exposes CPM peripheral interrupts to Linux drivers and cascades them through the 8xx SIU interrupt system.

### Risks
Vector extraction, mask/eoi bit order, and parent IRQ mapping are interrupt-critical. The no-op error handler intentionally suppresses a known CPM race.

### Test Signals
Probe CPM PIC, trigger SCC/SMC/FEC CPM interrupts, verify mask/unmask/eoi behavior, error IRQ handling, and `/proc/interrupts` mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/cpm1-ic.c -->
