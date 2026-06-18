# sources/distributed-fs/ceph-client/arch/powerpc/kernel/pci_of_scan.c

Purpose: this file builds Linux PCI devices and buses from Open Firmware PCI device-tree nodes. It decodes PCI address cells, creates `pci_dev` objects without config-space enumeration, parses BAR and bridge resources from DT properties, and recursively scans child buses.

Important APIs and functions: `pci_parse_of_flags()` converts OF PCI `phys.hi` address bits into Linux resource and PCI BAR flags. `of_create_pci_dev()` allocates a `pci_dev`, populates IDs, class, revision, config size, OF node, MSI mask, header type, ROM register, and resources, then calls `pci_device_add()`. `of_scan_pci_bridge()` creates or finds child buses and parses bridge `bus-range` and `ranges`. Public scan functions are `of_scan_bus()` and `of_rescan_bus()`.

Control flow: `of_scan_bus()` scans each direct DT child through `of_scan_pci_dev()`. A child must be available and have a valid `reg` property. Existing devices are reused by slot lookup, and EEH-removed nodes are skipped. New devices run early PCI fixups before address parsing. After direct children are created, new bus setup runs `pcibios_setup_bus_self()`, then all PCI bridges are recursively scanned. Rescans skip the bus-self setup for already configured buses.

State and persistence: parsed resources are written into `dev->resource[]` and `bus->resource[]` with bus-to-CPU address translation through `pcibios_bus_to_resource()`. Devices retain OF node references. Bridge bus-number resources are inserted using firmware `bus-range`. Device power and error state start at unknown/normal, and default DMA mask is 32-bit while MSI address mask starts at 64-bit.

Dependencies and integration points: this code is called by `pcibios_scan_phb()` and hotplug rescans. It depends on `pci_dn.c` for DT node PCI metadata, `pci-common.c` for bus setup/resource translation, generic PCI device allocation and bridge scanning, EEH removal markers, and OF property formats.

Risks: the code trusts firmware properties for IDs, class, ranges, and bus numbers. Missing `bus-range` or `ranges` prevents bridge scanning. It supports one IO bridge range and a finite number of memory ranges. `reg` fallback in `of_pci_parse_addrs()` marks resources unset, so later resource assignment behavior is important. Multifunction detection is conservative and may be inaccurate.

Test signals: DT-only probe mode should enumerate all available firmware nodes with correct BARs and bridge windows. Hot-rescan should reuse existing slots and create only new devices. Test unavailable nodes, EEH removed nodes, bridges with multiple memory ranges, ROM resources, and config-space access after `pci_device_add()`.
