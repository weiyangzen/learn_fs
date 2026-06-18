# sources/distributed-fs/ceph-client/include/linux/irqdomain_defs.h

## Purpose
`irqdomain_defs.h` defines bus-token values used to disambiguate multiple IRQ domains that share the same firmware node but serve different interrupt buses.

## Important APIs, types, and functions
It defines `enum irq_domain_bus_token`, including wired IRQs, generic/PCI/platform/device MSI, nexus, IPI, wakeup, VMD, DMAR, AMDVI, and wired-to-MSI domains.

## Control flow
Domain lookup and selection code compares a firmware node plus bus token to choose the correct domain for a device interrupt specifier.

## State and persistence
No runtime state is declared.

## Dependencies and integration points
It is consumed by irqdomain core, MSI code, PCI/platform/device IRQ setup, IOMMU interrupt remapping domains, and wakeup domains.

## Risks and test signals
Risks include selecting `DOMAIN_BUS_ANY` when a specific token is required and collisions between MSI domain types. Tests should cover systems with multiple domains on one fwnode, PCI MSI/MSI-X, platform MSI, and interrupt remapping.
