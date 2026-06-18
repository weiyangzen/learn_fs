<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-mscc-ocelot.c -->
## sources/distributed-fs/ceph-client/drivers/irqchip/irq-mscc-ocelot.c

### Purpose
`irq-mscc-ocelot.c` implements Microsemi/Microchip VCore-III internal CPU interrupt controllers for Ocelot, Serval, Luton, and Jaguar2 SoCs. It uses generic IRQ chips with SoC-specific register offsets.

### Important APIs, Types, And Functions
`struct chip_props` describes register offsets, flags, and IRQ count per SoC. `vcoreiii_irq_init()` is the shared initializer. `ocelot_irq_handler()` demultiplexes the `INTR_IDENT` register. `ocelot_irq_unmask()` handles edge sticky clearing for controllers with trigger registers.

### Control Flow
Initialization parses the parent IRQ, creates a linear domain, allocates one generic chip, maps MMIO, configures ack/mask/unmask register callbacks according to SoC flags, masks and acks all interrupts, optionally enables the IRQ0 output path, stores properties in domain host data, and chains the parent. Dispatch reads the destination interrupt identification register and handles each set hwirq from highest bit downward. Unmask clears sticky state for edge-mode interrupts before setting enable bits.

### State, Persistence, And Dependencies
State is the generic chip, mapped MMIO, domain host data pointing to static SoC properties, and parent chain. Dependencies include OF matching, generic-chip APIs, chained IRQ helpers, and SoC register semantics.

### Integration Points
This is the internal interrupt controller feeding a parent CPU interrupt line on VCore-III SoCs. Child devices use normal domain mappings created from device tree.

### Risks
SoC register offsets differ and incorrect matching causes wrong MMIO writes. The unmask path reads two trigger register replicas to infer edge mode; this is hardware-specific. Luton needs an explicit output enable bit. There is no runtime remove path for early irqchip declarations.

### Test Signals
Validate all four compatibles, trigger/sticky clearing behavior, parent cascade delivery, generic-chip mask/ack registers, Luton output enable, and empty/invalid parent IRQ handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-mscc-ocelot.c -->
