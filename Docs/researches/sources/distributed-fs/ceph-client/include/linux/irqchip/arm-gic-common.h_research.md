# sources/distributed-fs/ceph-client/include/linux/irqchip/arm-gic-common.h

## Purpose
`arm-gic-common.h` holds shared ARM GIC constants and declarations used by multiple GIC versions, currently default interrupt priority and GICv2m MSI initialization.

## Important APIs, types, and functions
It defines `GICD_INT_DEF_PRI` and declares `gicv2m_init(struct fwnode_handle *parent_handle, struct irq_domain *parent)`.

## Control flow
GIC drivers include this header to use a common distributor priority and to initialize GICv2m MSI frames under a parent irqdomain.

## State and persistence
No state is defined in the header.

## Dependencies and integration points
It includes `arm-vgic-info.h` and forward-declares irqdomain/fwnode types. It integrates GIC interrupt controllers with MSI child domains and KVM VGIC metadata.

## Risks and test signals
Risks include priority mismatches across GIC versions and failed GICv2m child-domain setup. Tests should cover GICv2m probing from DT/ACPI, MSI allocation under a GIC parent, and priority programming consistency.
