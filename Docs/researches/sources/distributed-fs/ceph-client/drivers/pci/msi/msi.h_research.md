# sources/distributed-fs/ceph-client/drivers/pci/msi/msi.h

## Purpose
Provides the private PCI MSI/MSI-X declarations and inline helpers shared by MSI implementation files. It centralizes mask/unmask behavior, MSI-X table address computation, vector-control writes, feature probing declarations, and legacy fallback prototypes.

## APIs, Types, And Functions
Defines `msix_table_size()`, `pci_msi_mask()`, `pci_msi_unmask()`, `pci_msix_desc_addr()`, `pci_msix_write_vector_ctrl()`, `pci_msix_mask()`, `pci_msix_unmask()`, `__pci_msi_mask_desc()`, `__pci_msi_unmask_desc()`, and `msi_multi_mask()`. It declares core lifecycle functions such as `__pci_enable_msi_range()`, `__pci_enable_msix_range()`, shutdown/restore/free helpers, `pci_msi_domain_supports()`, and per-device domain setup.

## Control Flow
Inline helpers dispatch on descriptor type: MSI-X uses table vector-control writes and optional read flushes, while MSI uses config-space mask registers through `pci_msi_update_mask()`. `msi_multi_mask()` computes a full mask for all vectors in a multi-MSI descriptor while guarding against oversized shifts.

## State And Persistence
The header manipulates cached descriptor fields: `pci.mask_base`, `pci.msix_ctrl`, `pci.msi_mask`, `pci.msi_attrib`, and `msi_index`. No persistent state is introduced.

## Dependencies And Integration
Included by `msi.c`, `irqdomain.c`, and `legacy.c`. It depends on `linux/pci.h`, `linux/msi.h`, PCI MSI/MSI-X register constants, and `CONFIG_PCI_MSI_ARCH_FALLBACKS` for fallback declarations or warning stubs.

## Risks And Test Signals
Risks include missing write flushes, stale `msix_ctrl` cache, incorrect mask semantics for devices without per-vector masking, and shift overflow in multi-MSI masks. Test signals are MSI/MSI-X mask/unmask stress, vector-control cache validation, devices without mask support, and builds with and without arch fallback support.
