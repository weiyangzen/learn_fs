<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-mvebu-pic.c -->
## sources/distributed-fs/ceph-client/drivers/irqchip/irq-mvebu-pic.c

### Purpose
`irq-mvebu-pic.c` implements the Marvell Armada 7K/8K PIC, a per-CPU cascaded interrupt controller with 32 local interrupts and one parent per-CPU IRQ.

### Important APIs, Types, And Functions
`struct mvebu_pic` stores MMIO base, parent IRQ, domain, and platform device. `mvebu_pic_probe()` maps resources, creates the domain, chains the parent, and enables the per-CPU IRQ on all CPUs. `mvebu_pic_handle_cascade_irq()` dispatches cause bits. `mvebu_pic_chip` masks, unmasks, EOIs, and prints the device name.

### Control Flow
Probe maps MMIO, parses the parent IRQ, creates a 32-entry linear domain, installs the chained parent handler and handler data, calls `on_each_cpu()` to reset the PIC and enable the per-CPU parent IRQ, and stores drvdata. Domain mapping marks each virq as percpu devid and uses `handle_percpu_devid_irq`. Cascade handling reads `PIC_CAUSE` and handles every set bit in the domain. Remove disables the per-CPU parent on each CPU and removes the domain.

### State, Persistence, And Dependencies
State is devm-managed controller data, MMIO mask/cause registers, per-CPU parent enable state, and the IRQ domain. Dependencies include platform driver binding, OF IRQ parsing, per-CPU IRQ APIs, chained IRQ handling, and seq-file printing.

### Integration Points
The PIC feeds per-CPU interrupt sources into Linux on Armada 7K/8K. Child interrupts are represented as per-CPU device IRQs.

### Risks
Mask register semantics are inverted from many controllers: reset writes zero to mask and the mask callback sets bits. Cascade dispatch does not mask cause with enable/mask state, so hardware cause behavior must be reliable. Parent IRQ setup uses separate `irq_set_chained_handler()` and `irq_set_handler_data()` calls.

### Test Signals
Validate per-CPU enable/disable on all CPUs, cause-bit dispatch, EOI writes, mask/unmask semantics, remove cleanup, parent IRQ parse failures, and `/proc/interrupts` chip printing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-mvebu-pic.c -->
