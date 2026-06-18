<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-loongson-pch-lpc.c -->
## sources/distributed-fs/ceph-client/drivers/irqchip/irq-loongson-pch-lpc.c

### Purpose
`irq-loongson-pch-lpc.c` implements the Loongson LS7A LPC interrupt controller. It provides a legacy 1:1 domain for 16 LPC/ISA-style IRQs and cascades a single parent IRQ from the PCH PIC.

### Important APIs, Types, And Functions
`struct pch_lpc` carries MMIO base, domain, lock, and saved control/enable/polarity registers. `pch_lpc_init()` is the shared OF/ACPI initializer. `lpc_irq_dispatch()` demultiplexes enabled status bits. `lpc_irq_ack()`, `lpc_irq_mask()`, `lpc_irq_unmask()`, and `lpc_irq_set_type()` implement `pch_lpc_irq_chip`. `pch_lpc_acpi_init()` maps the parent cascade using the parent domain.

### Control Flow
Initialization maps MMIO, rejects a controller that appears disabled by returning all ones in enable/status, creates a legacy domain for IRQs 0-15, resets control/enables/status, chains the parent IRQ, publishes `pch_lpc_handle`, and registers syscore PM. Dispatch intersects `LPC_INT_ENA` and `LPC_INT_STS`, handles each set bit in the LPC domain, and reports spurious parent interrupts when no enabled status exists.

### State, Persistence, And Dependencies
State is the singleton `pch_lpc_priv`, the fwnode handle, saved registers for resume, and the chained parent mapping. It depends on Loongson PCH PIC as parent, irqdomain legacy mapping, OF/ACPI firmware, and syscore PM.

### Integration Points
This is the legacy LPC leaf beneath PCH PIC. ACPI creation is triggered by `irq-loongson-pch-pic.c` after the first PCH PIC domain is created.

### Risks
The domain is fixed to 16 entries while reset clears 18 status bits, reflecting hardware behavior but worth regression testing. `lpc_irq_set_type()` ignores non-level requests by returning success without changing the handler. Singleton state prevents multiple LPC controllers.

### Test Signals
Check IRQ0-15 legacy mappings, ACPI and OF parent cascade mapping, level-high/level-low polarity, disabled-controller detection, spurious parent IRQs, and suspend/resume preservation of control, enable, and polarity registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-loongson-pch-lpc.c -->
