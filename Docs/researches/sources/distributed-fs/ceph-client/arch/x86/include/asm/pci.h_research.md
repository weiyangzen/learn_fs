# sources/distributed-fs/ceph-client/arch/x86/include/asm/pci.h

Purpose: defines x86 architecture data and hooks for the generic PCI subsystem, including per-root-bus metadata, PCI domain/NUMA lookup, MSI fwnode retrieval, VMD detection, legacy IRQ routing, mmap policy, early quirks, and IOMMU allocation.

Important APIs, types, and functions: `struct pci_sysdata` holds `domain`, `node`, optional ACPI companion, IOMMU private data, MSI fwnode, and VMD root device. Inline helpers include `to_pci_sysdata()`, `pci_domain_nr()`, `pci_proc_domain()`, `_pci_root_bus_fwnode()`, `is_vmd()`, `__pcibus_to_node()`, and `cpumask_of_pcibus()`. Externs include `pci_routeirq`, `noioapicquirk`, `noioapicreroute`, `pcibios_assign_all_busses()`, `pci_legacy_init()`, `pci_mem_start`, `pcibios_enabled`, `pcibios_scan_root()`, IRQ routing table helpers, `pci_dev_has_default_msi_parent_domain()`, `early_quirks()`, and `pci_iommu_alloc()`.

Control flow: generic PCI code calls architecture hooks during root-bus scanning, domain reporting, MSI domain assignment, mmap setup, early quirk execution, and IRQ routing. NUMA helpers map bus node metadata to CPU masks.

State and persistence: persistent hardware state is managed elsewhere; this header exposes runtime metadata embedded in each PCI bus. Globals configure boot-time PCI policy.

Dependencies and integration points: depends on generic PCI, ACPI, MSI IRQ domains, VMD, NUMA, PAT/memtype, and x86 IOMMU setup.

Risks: incorrect `pci_sysdata` initialization mislabels domains, NUMA nodes, IOMMU domains, MSI routing, or VMD membership. Legacy IRQ routing globals affect old systems and boot parameters.

Test signals: PCI enumeration with multiple domains, ACPI and legacy init paths, VMD root domains, MSI interrupt delivery, NUMA locality of PCI devices, PCI resource mmap with write-combining, and early quirk behavior.
