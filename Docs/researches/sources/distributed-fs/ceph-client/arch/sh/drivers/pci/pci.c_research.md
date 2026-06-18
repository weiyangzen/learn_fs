# sources/distributed-fs/ceph-client/arch/sh/drivers/pci/pci.c



Source read size: 302 lines, 7047 bytes.



Purpose: generic SH PCI host bridge registration, root-bus scanning, resource alignment, status reporting, and legacy I/O mapping.

Important APIs/types/functions: `register_pci_controller()`, `pcibios_scanbus()`, `pcibios_init()`, `pcibios_align_resource()`, `pcibios_report_status()`, `__pci_ioport_map()`, exported `PCIBIOS_MIN_IO` and `PCIBIOS_MIN_MEM`, `pci_config_lock`, and `pci_scan_mutex`.

Control flow: controllers register resources and are chained into a hose list; subsys init scans each hose with `pci_scan_root_bus_bridge()`, sizes/assigns bridge resources, and adds devices. Late registrations scan under a mutex. Status reporting walks either early config space or enumerated bus trees.

State and persistence: global hose list, next bus number/domain flag, initialized flag, resource reservations, bus pointers, and I/O map bases persist for runtime PCI access.

Dependencies and integration points: integrates SH `pci_channel` controllers with generic PCI core, resource trees, swizzle/map IRQ hooks, and non-generic I/O port mapping.

Risks and test signals: multiple domains require valid `io_map_base`; bus-number rollover toggles domain info; resource conflicts skip scanning. Test multi-controller systems, late controller registration, I/O port mapping, resource alignment, and error status reporting.
