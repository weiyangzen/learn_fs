# sources/distributed-fs/ceph-client/arch/x86/include/asm/pci_x86.h

Purpose: centralizes low-level x86 PCI probing policy, legacy IRQ routing structures, raw PCI config access backends, MMCONFIG region management, and x86-specific PCI init hook defaults.

Important APIs, types, and functions: defines `PCI_PROBE_*` and policy flags such as `PCI_ASSIGN_ALL_BUSSES`, `PCI_USE__CRS`, `PCI_NOASSIGN_BARS`, and `PCI_USE_E820`. It declares `pci_probe`, `pirq_table_addr`, `pci_bf_sort_state`, `pcibios_resource_survey()`, `pcibios_set_cache_line_size()`, `pcibios_last_bus`, `pci_root_ops`, `pcibios_scan_specific_bus()`, IRQ routing structs `irq_info`, `irq_routing_table`, `irt_routing_table`, raw ops `struct pci_raw_ops`, `raw_pci_ops`, `raw_pci_ext_ops`, `pci_mmcfg`, `pci_direct_conf1`, probe/init hooks, MMCONFIG region struct and functions, `pci_mmcfg_list`, and `mmio_config_read/write[bwl]()`.

Control flow: boot PCI initialization selects BIOS, direct config, or MMCONFIG access based on flags and DMI/ACPI checks. MMCONFIG helpers add/map/unmap regions. Raw ops provide read/write callbacks for generic PCI config access. Inline MMIO config helpers force `%eax/%ax/%al` for AMD Fam10h requirements.

State and persistence: global probe flags, raw ops pointers, config lock, PIRQ data, and MMCONFIG list are runtime state. Writes affect PCI config hardware.

Dependencies and integration points: ties together arch PCI files, ACPI, DMI, PCI IRQ routing, MMCONFIG resource tracking, direct PCI config, and legacy BIOS support.

Risks: probe flags can disable resource assignment or select unsafe access methods. MMCONFIG mapping must avoid invalid firmware ranges. Raw config access must be locked and respect AMD register constraints. PIRQ table layout is packed firmware ABI.

Test signals: boot with `pci=` options, ACPI and non-ACPI systems, MMCONFIG insert/delete, direct config fallback, PIRQ routing, DMI quirks, AMD Fam10h MMIO config accesses, and PCI resource allocation regression tests.
