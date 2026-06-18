# sources/distributed-fs/ceph-client/drivers/pci/ats.c

Purpose: implements PCIe ATS plus optional PRI and PASID capability management for IOMMU-facing devices and SR-IOV relationships.

Important APIs/types/functions: `pci_ats_init()`, `pci_ats_supported()`, `pci_prepare_ats()`, `pci_enable_ats()`, `pci_disable_ats()`, `pci_restore_ats_state()`, queue-depth and page-aligned queries; under `CONFIG_PCI_PRI`, PRI init/enable/disable/restore/reset and support/status helpers; under `CONFIG_PCI_PASID`, PASID init/enable/disable/restore/features/max/status helpers.

Control flow/state: init locates extended capability offsets and stores them in `pci_dev`. ATS enable validates support, untrusted status, page shift, PF/VF STU consistency, writes the control register, and sets `ats_enabled`/`ats_stu`; restore replays that state after reset/resume. PRI tracks `pri_enabled`, allocated request count, and PASID-required status, while VFs share PF PRI. PASID requires PF support, EETLP or no-TLP-prefix capability, ACS path isolation, supported feature bits, then writes enable/features into control state.

Dependencies/integration: depends on PCI config access, PCI extended capability definitions, SR-IOV PF/VF helpers, ACS path checks, and IOMMU drivers calling prepare/enable at the right lifecycle point. Risks include enabling translation features on untrusted or non-isolated paths, PF/VF state mismatches, restore after reset missing capability state, and WARN_ON misuse indicating lifecycle bugs. Test signals include IOMMU-driven ATS/PRI/PASID enablement, VF behavior, reset/resume restore, unsupported-feature rejection, and ACS isolation failure paths.
