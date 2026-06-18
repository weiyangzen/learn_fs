<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-loongson-pch-pic.c -->
## sources/distributed-fs/ceph-client/drivers/irqchip/irq-loongson-pch-pic.c

### Purpose
`irq-loongson-pch-pic.c` implements the Loongson PCH PIC, a hierarchical interrupt controller that maps PCH GSIs through HT vector IDs. It supports multiple I/O PICs and provides ACPI helpers to locate a PIC by GSI range.

### Important APIs, Types, And Functions
`struct pch_pic` stores MMIO base, child domain, vector base/count, GSI base, lock, saved mask/polarity/edge registers, and a software hwirq-to-hardware-bit table. `pch_pic_init()` creates the hierarchy. `pch_pic_domain_translate()` assigns table slots. `pch_pic_alloc()` programs `PCH_INT_HTVEC()` and allocates parent vectors. `find_pch_pic()` and `pch_pic_acpi_init()` are ACPI integration points.

### Control Flow
Initialization maps registers, clears the software table to undefined, derives vector count, creates a hierarchical domain under the parent, resets route/vector/mask/clear/HTMSI state, records the domain handle, and registers syscore hooks for the first PIC. Translation converts OF hwirqs or ACPI GSIs into table indices, assigning a new table slot when needed. Allocation writes the HT vector number for the hardware bit, allocates the parent hwirq, and installs `pch_pic_irq_chip`. Mask, unmask, ack, and type operations update mask/clear/edge/polarity registers and propagate parent operations.

### State, Persistence, And Dependencies
State persists in global `pch_pic_priv[]`, `pch_pic_handle[]`, `nr_pics`, per-PIC route tables, and saved PM registers. It depends on parent HTVEC/AVEC domains, Loongson ACPI MADT BIO/LPC PIC structures, irqdomain hierarchy, and syscore PM.

### Integration Points
This is the parent for Loongson LPC PIC on ACPI systems and for normal PCH device interrupts. MSI is separate but shares parent vector infrastructure.

### Risks
The software table decouples firmware hwirq/GSI from hardware bit and must remain stable after allocation. `pch_pic_reset()` writes routes for all 64 table indices, including undefined entries at early boot. `nr_pics` lacks explicit bound checks before storing. Suspend/resume iterates all registered PICs and assumes their pointers are valid.

### Test Signals
Validate GSI-to-PIC lookup, repeated translation of the same GSI, table exhaustion, type changes and handler switching, parent allocation failure cleanup, ACPI LPC cascade creation, and resume restoration of mask/edge/polarity registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-loongson-pch-pic.c -->
