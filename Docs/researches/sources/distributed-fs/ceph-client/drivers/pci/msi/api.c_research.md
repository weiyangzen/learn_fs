# sources/distributed-fs/ceph-client/drivers/pci/msi/api.c

## Purpose
Exports the driver-facing PCI MSI/MSI-X interrupt APIs. It wraps internal MSI allocation/shutdown logic, supports legacy and modern vector allocation interfaces, dynamic MSI-X vector allocation, affinity queries, cleanup, restore, and global MSI-enabled reporting.

## Important APIs, Types, and Functions
Exported APIs include `pci_enable_msi()`, `pci_disable_msi()`, `pci_msix_vec_count()`, `pci_enable_msix_range()`, `pci_msix_can_alloc_dyn()`, `pci_msix_alloc_irq_at()`, `pci_msix_free_irq()`, `pci_disable_msix()`, `pci_alloc_irq_vectors()`, `pci_alloc_irq_vectors_affinity()`, `pci_irq_vector()`, `pci_irq_get_affinity()`, `pci_free_irq_vectors()`, `pci_restore_msi_state()`, and `pci_msi_enabled()`.

## Control Flow
Legacy MSI enables exactly one vector through `__pci_enable_msi_range()` and stores the Linux IRQ at `dev->irq`; disable shuts down MSI under the MSI descriptor lock and frees MSI IRQs. Legacy MSI-X range allocation validates entries through internal helpers and returns vector counts. Modern vector allocation tries MSI-X first, then MSI, then INTx if allowed and only one vector is required; affinity setup is passed to MSI backends or used to create a single INTx affinity mask. Dynamic MSI-X allocation first verifies MSI-X is enabled and the MSI domain supports dynamic allocation, then allocates or frees one table index. Vector lookup returns `dev->irq` for INTx or MSI descriptor IRQs for MSI/MSI-X.

## State and Persistence Behavior
The APIs mutate `dev->msi_enabled`, `dev->msix_enabled`, MSI descriptors, MSI/MSI-X hardware state, and sometimes `dev->irq`. `pci_restore_msi_state()` writes cached MSI/MSI-X state back after resume or reset. `pci_msi_enabled()` reflects global `pci_msi_enable`.

## Dependencies and Integration Points
Depends on internal `msi.h` helpers, Linux IRQ/MSI domains, IRQ affinity descriptors, MSI descriptor locking, PCI INTx control, and device MSI domain feature flags. It is the main exported surface used by PCI drivers and hotplug code such as PowerNV/SHPC interrupt setup.

## Risks
Legacy MSI/MSI-X APIs coexist with `pci_alloc_irq_vectors()`; drivers must not mix cleanup paths. `pci_free_irq_vectors()` warns against use after `pcim_enable_device()` because managed cleanup can double-free. Dynamic MSI-X is domain-feature-dependent and returns errors in `msi_map.index`. Affinity can be NULL for MSI vectors allocated without affinity descriptors. INTx fallback only works for `min_vecs == 1`.

## Test Signals
Enable/disable legacy MSI, legacy MSI-X range, modern MSI-X/MSI/INTx allocation with and without affinity, vector lookup bounds, affinity query for MSI/MSI-X/INTx, dynamic MSI-X allocate/free, global `pci=nomsi`, resume/reset restore, and managed-device cleanup interactions.
