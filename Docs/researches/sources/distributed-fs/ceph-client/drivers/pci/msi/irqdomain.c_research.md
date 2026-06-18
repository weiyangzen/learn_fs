# sources/distributed-fs/ceph-client/drivers/pci/msi/irqdomain.c

## Purpose
Provides the irqdomain-backed PCI MSI/MSI-X integration layer. It decides whether a device should allocate interrupts through a hierarchical MSI irqdomain or the legacy architecture hooks, defines per-device MSI and MSI-X domain templates, and maps PCI requester IDs through OF/IORT firmware data for MSI routing.

## APIs, Types, And Functions
The externally used entry points are `pci_msi_setup_msi_irqs()`, `pci_msi_teardown_msi_irqs()`, `pci_setup_msi_device_domain()`, `pci_setup_msix_device_domain()`, `pci_msi_domain_supports()`, `pci_msi_domain_get_msi_rid()`, `pci_msi_map_rid_ctlr_node()`, `pci_msi_get_device_domain()`, and exported `pci_msix_prepare_desc()`. The file defines MSI and MSI-X `msi_domain_template` instances whose irq chip callbacks mask, unmask, startup, shutdown, and write MSI messages.

## Control Flow
Setup first checks `dev_get_msi_domain()` and uses `msi_domain_alloc_irqs_all_locked()` for hierarchical domains, otherwise falling back to `pci_msi_legacy_setup_msi_irqs()`. Device-domain setup refuses cross-mode creation when MSI-X/MSI is already enabled, reuses a matching per-device domain, removes the opposite-mode domain, and creates a new domain from the relevant template. Runtime IRQ operations mask/unmask the PCI MSI/MSI-X descriptor and conditionally call parent irqchip startup/shutdown or mask/unmask based on parent feature flags. RID mapping walks DMA aliases, chooses a usable alias RID, then applies OF `msi-map` or ACPI IORT translation.

## State And Persistence
State is in kernel memory only: device MSI domains attached to `struct device`, `msi_desc` fields, `msi_domain_info` flags, and firmware-derived fwnodes. Per-device MSI/MSI-X domains persist until device removal or until switching between MSI and MSI-X domain modes.

## Dependencies And Integration
Depends on generic MSI core helpers, irqdomain hierarchy support, `msi.h`, OF IRQ/MSI mapping, and ACPI IORT. It integrates directly with `msi.c` descriptor preparation/message programming and with architecture/irqchip parent domains that advertise `supported_flags` or global `msi_domain_info` flags.

## Risks And Test Signals
Risks include incorrect legacy fallback selection, stale per-device domain replacement when switching MSI modes, parent chip startup/shutdown mismatches, multi-MSI vector bit calculations, and DMA alias/RID translation errors on bridges or IOMMU-backed systems. Test signals include MSI and MSI-X enable/disable on hierarchical and legacy platforms, dynamic MSI-X allocation, OF `msi-map` and ACPI IORT routing, DMA alias devices, suspend/resume restore, and IRQ mask/unmask behavior under interrupt load.
