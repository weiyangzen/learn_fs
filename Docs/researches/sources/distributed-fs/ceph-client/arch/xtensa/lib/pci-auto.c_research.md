# sources/distributed-fs/ceph-client/arch/xtensa/lib/pci-auto.c

Purpose: Provides a legacy PCI bus autoconfiguration scanner for Xtensa host controllers.

Important APIs, types, and functions: `pciauto_bus_scan()`, `pciauto_setup_bars()`, `pciauto_setup_irq()`, `pciauto_prescan_setup_bridge()`, `pciauto_postscan_setup_bridge()`, static `pciauto_dev`, `pciauto_bus`, and upper I/O/memory allocation cursors.

Control flow: Initializes allocation cursors from controller resources, scans devfn values, skips host bridge, handles multifunction devices, sizes/writes BARs downward from upper limits, maps IRQ pins, recurses into PCI-to-PCI bridges after temporary bus numbering, then programs bridge windows and command bits.

State and persistence: Writes PCI config space, mutates static allocation cursors and synthetic `pci_dev/pci_bus` objects, and returns highest subordinate bus number.

Dependencies and integration: Depends on `struct pci_controller` config ops/resources/map_irq from Xtensa PCI bridge support, generic PCI config accessors, and PCI class/header constants.

Risks: Static globals make concurrent scans unsafe; 64-bit BARs are forced below 4GB; bridge window arithmetic allocates downward and can underflow if resources are undersized; modern PCI core expectations may differ.

Test signals: PCI-enabled board boot, endpoint BAR assignment, bridge recursion, multifunction devices, IRQ line programming, resource exhaustion cases, and comparison with `lspci -vv`.
