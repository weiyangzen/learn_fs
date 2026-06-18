<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/pci_link.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/pci_link.c

## Purpose
`pci_link.c` implements the ACPI PCI Interrupt Link Device handler for `PNP0C0F` objects. It discovers possible/current legacy interrupt routes from `_PRS` and `_CRS`, programs a selected IRQ through `_SRS`, disables unused links with `_DIS`, and exposes allocation/free helpers used by ACPI PCI IRQ routing.

## Important APIs, Types, and Functions
The main state types are `struct acpi_pci_link_irq`, which caches active IRQ, trigger, polarity, resource type, possible IRQs, and initialization state, and `struct acpi_pci_link`, which binds that IRQ state to an ACPI device and reference count. Key functions are `acpi_pci_link_get_possible()`, `acpi_pci_link_get_current()`, `acpi_pci_link_set()`, `acpi_pci_link_allocate_irq()`, `acpi_pci_link_free_irq()`, `acpi_irq_penalty_init()`, `acpi_penalize_isa_irq()`, `acpi_isa_irq_available()`, `acpi_penalize_sci_irq()`, and `acpi_pci_link_init()`.

## Control Flow and State
During ACPI scan attach, `acpi_pci_link_add()` allocates link state, walks `_PRS` for IRQ or extended IRQ descriptors, reads `_CRS`, logs the current route, adds the link to `acpi_link_list`, and disables the link until used. Allocation validates the requested index, locks `acpi_link_lock`, picks the active IRQ if it is valid or chooses the lowest-penalty possible IRQ, calls `_SRS`, verifies or overrides `_CRS`, marks the link initialized, increments `refcnt`, and returns trigger/polarity/name/GSI. Resume iterates all links and reprograms initialized referenced links.

## State and Persistence
Persistent state is the global link list, per-link cached IRQ assignment, reference counts, IRQ penalty table, SCI penalty, and `acpi_irq_balance` boot policy. Hardware/firmware state persists in ACPI link device routing after `_SRS`; the driver deliberately keeps cached assignment state even if a link is later disabled.

## Dependencies and Integration Points
The file depends on ACPI resource walking/evaluation, ACPI scan handlers, PCI IRQ routing, system core resume callbacks, boot parameters, and global ACPI IRQ mode flags. It integrates with PNP/ISA IRQ reservation through penalty helpers and with the ACPI PCI routing code that resolves link devices to GSIs.

## Risks and Test Signals
Risks include only supporting one IRQ resource entry per link, firmware returning `_CRS` values outside `_PRS`, global penalty heuristics misrouting shared legacy IRQs, possible refcount underuse because decrement code is disabled under `FUTURE_USE`, and resume assumptions that cached routes remain valid. Test signals are link enumeration logs, correct `acpi_irq_isa=`/`acpi_irq_pci=` behavior, successful PCI device interrupt delivery in PIC and IOAPIC modes, suspend/resume with legacy INTx devices, and no selection of SCI or always-reserved ISA IRQs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/pci_link.c -->
