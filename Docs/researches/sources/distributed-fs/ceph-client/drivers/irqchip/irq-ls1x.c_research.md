<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-ls1x.c -->
## sources/distributed-fs/ceph-client/drivers/irqchip/irq-ls1x.c

### Purpose
`irq-ls1x.c` implements the Loongson-1 interrupt controller. It provides a 32-interrupt linear generic-chip domain and cascades one parent IRQ into that domain.

### Important APIs, Types, And Functions
`struct ls1x_intc_priv` stores the domain and MMIO base. `ls1x_intc_of_init()` sets up the controller. `ls1x_chained_handle_irq()` demultiplexes status and enable bits. `ls_intc_set_type()` programs edge and polarity registers, then asks the generic IRQ core to switch to the alternate edge or level chip type.

### Control Flow
Initialization maps the controller, parses a parent IRQ, creates a 32-entry linear domain using generic-chip ops, allocates two generic chip types, masks all IRQs, acknowledges pending bits, defaults polarity high, configures level and edge chip variants, and chains the parent IRQ. Dispatch reads `STATUS & EN`, handles each pending bit through the domain, and reports spurious interrupts when empty.

### State, Persistence, And Dependencies
State is the allocated private structure, generic-chip domain, MMIO registers, and chained parent handler. It depends on OF resources, generic IRQ chip helpers, chained IRQ handling, and Loongson-1 register semantics.

### Integration Points
Child devices use the LS1X interrupt domain. The controller sits below a CPU interrupt line or SoC parent described by the first interrupt in device tree.

### Risks
`ls_intc_set_bit()` performs unlocked read-modify-write sequences. Initial generic-chip allocation marks IRQs no-request, no-probe, and no-auto-enable, which is expected for an interrupt controller but can confuse tests that expect automatic enables. Unsupported types return `-EINVAL`.

### Test Signals
Validate parent cascade, all four trigger types, alternate chip selection, mask/ack/unmask register effects, spurious parent interrupts, and malformed DT with missing parent IRQ or MMIO resource.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-ls1x.c -->
