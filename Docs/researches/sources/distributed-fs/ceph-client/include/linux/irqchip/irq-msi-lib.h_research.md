# sources/distributed-fs/ceph-client/include/linux/irqchip/irq-msi-lib.h

## Purpose
`irq-msi-lib.h` provides shared helpers for irqchip drivers that expose MSI-capable domains and need common bus-token selection and MSI domain-info initialization.

## Important APIs, types, and functions
It defines `MATCH_PCI_MSI` when PCI MSI is enabled, `MATCH_PLATFORM_MSI`, and declares `msi_lib_irq_domain_select` and `msi_lib_init_dev_msi_info`.

## Control flow
IRQ domain `select` callbacks can delegate bus-token matching to `msi_lib_irq_domain_select`. Device MSI setup uses `msi_lib_init_dev_msi_info` to populate `struct msi_domain_info` against a real parent domain.

## State and persistence
No state is declared in the header; MSI domain state is owned by irqdomain/MSI core and drivers.

## Dependencies and integration points
It depends on bit operations, irqdomain, and MSI core. It integrates irqchips with PCI and platform MSI buses.

## Risks and test signals
Risks include wrong bus-token masks when PCI MSI is disabled, mismatched parent domains, and incomplete MSI info initialization. Tests should cover PCI MSI, platform MSI, disabled PCI MSI builds, and domain selection with multiple MSI domains.
