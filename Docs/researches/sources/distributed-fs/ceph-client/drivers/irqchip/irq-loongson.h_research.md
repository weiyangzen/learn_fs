<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-loongson.h -->
## sources/distributed-fs/ceph-client/drivers/irqchip/irq-loongson.h

### Purpose
`irq-loongson.h` is the local coordination header for Loongson irqchip drivers. It declares cross-driver ACPI initialization hooks and lookup helpers used to build the Loongson interrupt hierarchy from MADT subtables.

### Important APIs, Types, And Functions
The header declares `find_pch_pic()`, `liointc_acpi_init()`, `eiointc_acpi_init()`, `avecintc_acpi_init()`, `htvec_acpi_init()`, `pch_lpc_acpi_init()`, `pch_pic_acpi_init()`, `pch_msi_acpi_init()`, and `pch_msi_acpi_init_avec()`. These functions pass `struct irq_domain *` parent domains and Loongson ACPI MADT structure pointers between independent driver files.

### Control Flow
There is no executable control flow in the header. It enables staged initialization: CPU/local controllers create parent domains, parse ACPI subtables, and call the next-level controller's init function with the new parent domain and firmware data.

### State, Persistence, And Dependencies
The header owns no state. It depends on Linux IRQ domain declarations and architecture ACPI MADT type definitions being visible to including C files.

### Integration Points
It is included by Loongson LIOINTC, HTVEC, PCH PIC, PCH LPC, PCH MSI, and related controllers so they can form a firmware-described cascade without exposing symbols through a broader public header.

### Risks
Because it is a private header, signature drift across driver files would be caught at compile time. The real risk is initialization-order coupling: callers assume global domains such as LIOINTC or HTVEC have already been created.

### Test Signals
Build coverage with `CONFIG_ACPI`, `CONFIG_OF`, AVEC/EIOINTC combinations, and Loongson platforms using PCH PIC, PCH LPC, and PCH MSI ensures all declarations match their definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-loongson.h -->
