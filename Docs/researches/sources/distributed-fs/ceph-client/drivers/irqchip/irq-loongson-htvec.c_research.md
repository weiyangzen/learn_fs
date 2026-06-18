<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-loongson-htvec.c -->
## sources/distributed-fs/ceph-client/drivers/irqchip/irq-loongson-htvec.c

### Purpose
`irq-loongson-htvec.c` implements the Loongson HyperTransport vector interrupt controller. It exposes a linear domain over 32 vectors per parent line and cascades parent interrupts from firmware into edge-style Linux IRQs. It also acts as the ACPI cascade point for Loongson PCH PIC and MSI controllers.

### Important APIs, Types, And Functions
`struct htvec` stores parent count, MMIO base, IRQ domain, lock, and saved enable registers. `htvec_init()` is the shared OF/ACPI initializer. `htvec_domain_alloc()` maps one-cell firmware specs to `htvec_irq_chip`. `htvec_irq_dispatch()` fans out pending vector bits. `htvec_acpi_init()` allocates an ACPI fwnode and then parses BIO PIC and MSI PIC MADT subtables.

### Control Flow
OF setup reads the MMIO resource and up to eight parent IRQs, then calls `htvec_init()`. ACPI setup maps cascade entries through the parent domain. Initialization creates a linear domain sized at `32 * num_parents`, resets all cause/enable registers, chains each parent IRQ, stores the global private pointer, and registers syscore suspend/resume hooks. Dispatch scans every parent cause register and handles `bit + 32 * parent_index`; ack writes the bit to the cause register and mask/unmask update the corresponding enable register under `htvec_lock`.

### State, Persistence, And Dependencies
State includes `htvec_priv`, enable-register save slots, chained handlers, and the domain fwnode. Dependencies include irqdomain hierarchy/translation helpers, OF and ACPI MADT parsing, MMIO, syscore PM, and the Loongson PCH helper declarations in `irq-loongson.h`.

### Integration Points
The domain is the parent for PCH PIC and PCH MSI vector allocations on Loongson platforms. ACPI cascade parsing creates those downstream domains after HTVEC exists.

### Risks
The global singleton is assumed by ACPI parsers. OF setup does not explicitly reject zero parents before `htvec_init()`, so malformed firmware can create an empty domain. Type handling is fixed to `handle_edge_irq`; downstream code must configure devices accordingly. Multi-parent dispatch scans all cause registers for every chained entry.

### Test Signals
Validate OF and ACPI boot, parent IRQ fan-out across all eight vector groups, mask/unmask and ack register writes, suspend/resume preservation of enables, and ACPI creation of PCH PIC/MSI child domains.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-loongson-htvec.c -->
