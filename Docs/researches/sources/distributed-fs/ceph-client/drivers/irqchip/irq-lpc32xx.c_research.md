<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-lpc32xx.c -->
## sources/distributed-fs/ceph-client/drivers/irqchip/irq-lpc32xx.c

### Purpose
`irq-lpc32xx.c` supports the NXP LPC32xx main interrupt controller and secondary interrupt controllers. The MIC installs the CPU-level IRQ handler; SIC instances cascade from parent IRQs into separate linear domains.

### Important APIs, Types, And Functions
`struct lpc32xx_irq_chip` stores MMIO base, physical address, and domain. `lpc32xx_of_ic_init()` initializes MIC or SIC nodes. `lpc32xx_handle_irq()` is the top-level exception handler. `lpc32xx_sic_handler()` is the chained handler for SICs. `lpc32xx_irq_set_type()` programs polarity and edge/level registers and switches the Linux handler.

### Control Flow
The OF initializer maps registers, creates a 32-entry linear domain, and either records the MIC and calls `set_handle_irq()` or chains every parsed parent IRQ for a SIC. It then masks all interrupts and defaults polarity/type registers to low-level behavior. Runtime dispatch reads `STAT`, loops set bits, and routes them through the correct domain. Mask/unmask update the `MASK` register, and ack writes the hwirq bit to `RAW`.

### State, Persistence, And Dependencies
Persistent state is per-controller MMIO/domain state plus the global MIC pointer. It depends on OF resources, chained IRQ helpers, ARM exception handling, irqdomains, and seq-file chip printing.

### Integration Points
The driver is the interrupt root for LPC32xx when handling MIC interrupts and a cascaded controller for SIC nodes. Device-tree child interrupt specifiers use two-cell irqdomain translation.

### Risks
Register read-modify-write operations are not explicitly locked; callers rely on IRQ core serialization for descriptor operations. SIC handlers do not report empty status as spurious. The MIC global must be initialized before top-level dispatch can be used.

### Test Signals
Boot with MIC and multiple SIC nodes, verify edge and level polarity changes, IRQ ack/mask/unmask behavior, nested SIC delivery, `/proc/interrupts` chip names, and malformed DT resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-lpc32xx.c -->
