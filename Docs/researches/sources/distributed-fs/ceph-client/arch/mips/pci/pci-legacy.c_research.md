## sources/distributed-fs/ceph-client/arch/mips/pci/pci-legacy.c

### Purpose
This is the core legacy MIPS PCI framework for platforms that register `struct pci_controller` objects. It queues controllers, requests their resources, scans buses, assigns or claims resources, handles OF ranges, and provides PCI BIOS hooks.

### Important APIs, Types, And Functions
Important state includes the private `controllers` list, `pci_initialized`, and `pci_scan_mutex`. Public functions include `pci_address_to_pio()`, `pcibios_align_resource()`, `pci_load_of_ranges()`, `pcibios_get_phb_of_node()`, `register_pci_controller()`, `pcibios_enable_device()`, `pcibios_fixup_bus()`, and `pcibios_setup()`. `pcibios_scanbus()` performs the actual root-bus allocation and enumeration.

### Control Flow
Platform code calls `register_pci_controller()`, which requests memory and I/O resources, appends the hose to the list, and immediately scans if the subsystem has already initialized. `subsys_initcall(pcibios_init)` scans all queued controllers. Scanning builds a `pci_host_bridge`, attaches resource windows with offsets, sets sysdata, bus number, ops, swizzle and IRQ callbacks, scans the root bus, assigns or claims resources depending on `PCI_PROBE_ONLY`, configures child PCIe settings, and adds devices.

### State, Persistence, And Dependencies
Persistent kernel state includes registered host bridges, resource-tree entries, bus numbers, and PCI devices. OF support stores the controller node and maps I/O ranges. Dependencies include Linux PCI host-bridge helpers, MIPS `struct pci_controller`, platform `pcibios_map_irq()` and `pcibios_plat_dev_init()`, and optional platform `pcibios_plat_setup`.

### Integration Points
Most legacy platform files in this subset call `register_pci_controller()` or `pci_load_of_ranges()`. It is the bridge from MIPS board-specific setup to generic Linux PCI enumeration.

### Risks
Resource conflicts silently skip bus scans after warnings. `need_domain_info` is global and becomes sticky after bus-number overflow or nonzero domain use. Late controller registration is serialized but still depends on platform resources being complete.

### Test Signals
Validate multiple controllers, `PCI_PROBE_ONLY` versus assignment modes, OF range loading, domain numbering after bus number wrap, and resource-conflict handling.
