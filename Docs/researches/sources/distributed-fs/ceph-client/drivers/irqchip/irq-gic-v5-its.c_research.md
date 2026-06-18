<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-gic-v5-its.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-gic-v5-its.c

## Purpose
Implements the GICv5 Interrupt Translation Service used for MSI translation into LPIs. It owns ITS device table setup, per-device interrupt translation tables, MSI parent domain creation, EventID allocation, and OF/ACPI discovery of ITS and translate frames.

## Important APIs, Types, And Functions
`struct gicv5_its_chip_data` stores the ITS MMIO base, fwnode, xarray of registered devices, device-table configuration, MSI domain flags, and non-coherency flag. `struct gicv5_its_dev` represents one MSI requester with DeviceID, ITT configuration, EventID bitmap, event count, and translation-frame physical address. Important helpers include `gicv5_its_init_bases()`, `gicv5_its_init_devtab()`, `gicv5_its_device_register()`, `gicv5_its_alloc_device()`, `gicv5_its_msi_prepare()`, `gicv5_its_irq_domain_alloc()`, `gicv5_its_irq_domain_activate()`, and `gicv5_its_compose_msi_msg()`.

## Control Flow
Probe maps the ITS configuration frame, disables firmware-enabled ITS instances if needed, programs CR1 memory attributes, builds a linear or two-level device table from IDR capabilities, enables ITS CR0, and creates an MSI parent irqdomain above the GICv5 LPI domain. MSI preparation receives DeviceID and translation address through MSI allocation scratchpad, registers a device table entry, allocates an ITT, and stores the device in an xarray. Domain allocation reserves EventIDs, prepares IOMMU MSI translation, allocates parent LPIs, and encodes DeviceID/EventID into the irq hwirq. Activation maps EventID to the parent LPI in the ITT; deactivation clears that ITT entry.

## State And Persistence
State is in kernel memory plus hardware-visible tables. Device table and ITT entries are regular allocated memory exposed to hardware through physical addresses, with explicit cache maintenance for non-coherent ITS instances. `event_map` persists allocated EventID ranges until MSI teardown. Hardware caches are invalidated with ITS INV/SYNC registers, and interrupt translation persists in device/ITT entries until deactivate/free or device unregister.

## Dependencies And Integration Points
The driver depends on GICv5 core LPI domains, `gicv5_wait_for_op*()`, IRS synchronization, MSI library helpers, IOMMU MSI preparation, OF address parsing, ACPI MADT GICv5 ITS/translate records, and IORT domain tokens. It integrates with PCI/platform MSI users through the MSI parent irqdomain and with the GICv5 core through parent LPI allocation and `gicv5_irs_syncr()`.

## Risks
The table layout code is sensitive to DeviceID/EventID bit counts, L2 table sizes, `KMALLOC_MAX_SIZE` capping, and physical address mask fields. A bad cache-maintenance decision can make non-coherent systems lose translations. Fixed-message-data allocations rely on single-IRQ EventIDs. Error paths must unwind xarray entries, bitmaps, ITTs, and device-table validity in the right order.

## Test Signals
Build with GICv5, MSI, OF, ACPI, and IOMMU MSI support. Runtime signals are ITS enable messages, successful MSI allocation for PCI or platform devices, correct `/proc/interrupts` LPI delivery, no `EventID outside of ITT range` or cache-sync timeout logs, working MSI teardown/reallocation, and suspend/resume or driver reprobe without stale device-table entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-gic-v5-its.c -->
