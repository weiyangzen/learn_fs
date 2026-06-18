<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/msi.h -->
# sources/distributed-fs/ceph-client/include/linux/msi.h

## Purpose
`msi.h` defines low-level Message Signaled Interrupt data structures and APIs for interrupt core, PCI/MSI core, MSI domains, IOMMU/VFIO/NTB-style low-level consumers, and architecture integration. Driver-facing lookup APIs are intentionally separated into `msi_api.h`.

## Important APIs, Types, and Functions
Core message and descriptor types include `struct msi_msg`, `struct pci_msi_desc`, `union msi_domain_cookie`, `struct msi_desc_data`, `struct msi_desc`, `enum msi_desc_filter`, and `struct msi_dev_domain`. Descriptor APIs include `msi_setup_device_data()`, descriptor locking helpers and guard, `msi_domain_first_desc()`, `msi_first_desc()`, `msi_next_desc()`, iteration macros, `msi_desc_set_iommu_msi_iova()`, `msi_msg_set_addr()`, `msi_domain_insert_msi_desc()`, `msi_insert_msi_desc()`, and descriptor free-range helpers.

Generic MSI domain support defines `struct msi_domain_ops`, `struct msi_domain_info`, `struct msi_domain_template`, MSI domain flags, chip flags, `struct msi_parent_ops`, parent/domain creation APIs, device-domain creation/removal/matching, IRQ allocation/free range APIs, `msi_domain_alloc_irq_at()`, `msi_get_domain_info()`, platform MSI helpers, and `msi_device_has_isolated_msi()`. PCI-specific helpers include MSI message read/write/mask/unmask and domain helpers under `CONFIG_PCI_MSI`.

## Control Flow and State
Device MSI setup creates per-device descriptor storage and optional per-device IRQ domains. Allocation inserts descriptors, maps hardware or software indices to Linux IRQs, initializes domain/chip callbacks, and writes MSI messages. Free paths tear down IRQs and descriptors by domain/range. Descriptor iteration requires the MSI descriptor mutex. IOMMU MSI address override flows through `msi_desc_set_iommu_msi_iova()` and `msi_msg_set_addr()`.

## State and Persistence Behavior
MSI state is runtime per-device interrupt state. Descriptors cache the last programmed MSI message, affinity, IRQ number, domain-specific cookies, PCI attributes, optional sysfs attributes, and IOMMU address override. It persists while MSI interrupts are allocated.

## Dependencies and Integration Points
It depends on irq domains, IRQ chips, CPU masks, device model, PCI, sysfs, architecture MSI types, IOMMU MSI support, Xen fallback paths, and platform MSI. It is central to PCI/MSI-X, IMS, per-device domains, VFIO, and interrupt remapping.

## Risks
Regular drivers should not store `msi_desc` pointers; lifetime and locking are controlled by MSI core. Missing descriptor locks can race allocation/free. Domain flags must match parent capabilities. MSI address programming with IOMMU shifts is easy to corrupt. Config stubs must preserve behavior when generic or PCI MSI is disabled.

## Test Signals
PCI MSI and MSI-X allocation/free, dynamic MSI-X, affinity changes, suspend/resume restore, IOMMU interrupt remapping, sysfs MSI entries, Xen/fallback configurations, descriptor lockdep, and builds with generic MSI disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/msi.h -->
