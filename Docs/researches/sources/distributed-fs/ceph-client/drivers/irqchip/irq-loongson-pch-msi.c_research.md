<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-loongson-pch-msi.c -->
## sources/distributed-fs/ceph-client/drivers/irqchip/irq-loongson-pch-msi.c

### Purpose
`irq-loongson-pch-msi.c` provides the Loongson PCH MSI parent domain used by PCI MSI/MSI-X devices. It allocates MSI vector numbers from a bitmap, composes doorbell messages, and forwards masking/ack/affinity operations to the parent interrupt domain.

### Important APIs, Types, And Functions
`struct pch_msi_data` stores the MSI doorbell address, first vector, vector count, bitmap, and lock. `pch_msi_init()` and `pch_msi_init_domains()` create the MSI parent domain. `pch_msi_middle_domain_alloc()` allocates hardware vectors and parent IRQs. `pch_msi_compose_msi_msg()` writes MSI address/data. `get_pch_msi_handle()`, `pch_msi_acpi_init()`, and `pch_msi_acpi_init_avec()` support ACPI lookup and AVEC integration.

### Control Flow
OF setup finds the parent domain, reads the doorbell resource and `loongson,msi-*` vector properties, then creates a parent MSI irqdomain. Allocation reserves a power-of-two bitmap region for the requested MSI count, allocates corresponding parent interrupts, and installs `middle_irq_chip` for each virq. Freeing tears down parent IRQs and releases the bitmap region. ACPI either creates a new fwnode-backed MSI domain or upgrades an AVEC parent domain into an MSI parent.

### State, Persistence, And Dependencies
Persistent state includes per-controller bitmap allocation, doorbell address, global `pch_msi_handle[]`, and the MSI parent ops. It depends on generic MSI infrastructure, `irq-msi-lib.c`, PCI MSI flags, OF PCI metadata, Loongson ACPI tables, and parent vector domains such as HTVEC or AVEC.

### Integration Points
PCI host bridge code can retrieve an MSI fwnode by PCI segment. Downstream PCI MSI device domains select this parent via `msi_lib_irq_domain_select()`.

### Risks
Bitmap allocation uses `get_count_order(num_req)`, so multi-MSI allocations consume aligned power-of-two regions. `nr_pics` and handle arrays assume firmware does not exceed `MAX_IO_PICS`. ACPI fwnode allocation failure is checked in normal init but not explicitly before calling `pch_msi_init()` in every path.

### Test Signals
Exercise single and multi MSI allocation/free, MSI-X, vector exhaustion, ACPI segment lookup, AVEC parent upgrade, MSI message contents, and parent affinity propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-loongson-pch-msi.c -->
