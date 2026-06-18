<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/pci/pci_fixup.c -->
# sources/distributed-fs/ceph-client/arch/s390/pci/pci_fixup.c

Purpose: This small fixup file applies an s390-specific PCI quirk to IBM ISM devices so their BARs are not mmap-capable.

Important APIs/types/functions: The only helper is `zpci_ism_bar_no_mmap(struct pci_dev *pdev)`, registered with `DECLARE_PCI_FIXUP_HEADER` for IBM vendor/device IDs matching ISM.

Control flow: During PCI header fixup, matching devices iterate over their resources and clear mmap permission flags from BAR resources. This prevents user mappings for device memory that should be accessed through the s390-specific path or not exposed at all.

State and persistence: The persistent effect is mutation of PCI resource flags in the kernel's `pci_dev` resource array. There is no separate state.

Dependencies and integration points: It depends on generic PCI fixup registration and IBM device IDs. It integrates with the resource permission checks used later by sysfs/resource mmap and user-space MMIO paths.

Risks and test signals: Overmatching would unnecessarily block mmap for unrelated devices; undermatching would leave unsafe mappings available for ISM. Tests are PCI enumeration of ISM hardware, inspection of resource mmap permissions, and negative coverage for non-ISM IBM devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/pci/pci_fixup.c -->
