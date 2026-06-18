# sources/distributed-fs/ceph-client/drivers/soc/ti/ti_sci_inta_msi.c

## Purpose
This file provides MSI-domain helper support for TI SCI Interrupt Aggregator based MSI users. It creates an MSI IRQ domain with TI-SCI INTA bus token semantics and allocates MSI descriptors from TI-SCI resource ranges.

## Important APIs, Types, And Functions
Exported APIs are `ti_sci_inta_msi_create_irq_domain` and `ti_sci_inta_msi_domain_alloc_irqs`. Internal helpers are no-op MSI message callbacks, `ti_sci_inta_msi_update_chip_ops`, and `ti_sci_inta_msi_alloc_descs`.

## Control Flow
Domain creation patches the provided IRQ chip operations to delegate resource, type, mask, unmask, and ack operations to the parent domain, installs no-op compose/write MSI message hooks, enables `MSI_FLAG_FREE_MSI_DESCS`, creates the MSI domain, and marks its bus token as `DOMAIN_BUS_TI_SCI_INTA_MSI`. IRQ allocation requires a nonnegative platform device ID, sets up MSI device data, inserts descriptors for all primary and secondary TI-SCI resource ranges, then allocates all IRQs while holding the MSI descriptors lock.

## State And Persistence
The file stores no global state. State is held in MSI descriptors attached to the device and the created IRQ domain. Firmware resource ranges define the persistent MSI index space.

## Dependencies And Integration Points
It depends on Linux MSI/IRQ-domain core, TI-SCI resource descriptions, platform device IDs, and parent interrupt domains. K3 Ring Accelerator uses it to allocate ring IRQs from `ti,sci-rm-range-gp-rings`.

## Risks And Test Signals
Risks include platform IDs not being set before allocation, descriptor insertion failure requiring cleanup, resource range gaps, and no-op MSI message hooks being inappropriate for non-INTA users. Test signals include domain bus-token lookup success, allocated virqs for each resource index, and downstream `msi_get_virq` returning valid ring interrupts.
