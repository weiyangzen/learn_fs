<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/pci.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/pci.c

### Purpose
`pci.c` implements Orion5x PCIe and legacy PCI host-controller setup, config-space access, resource window setup, IRQ fallback mapping, and root-complex fixups.

### Important APIs, Types, And Functions
Public APIs are `orion5x_pcie_id()`, `orion5x_pci_disable()`, `orion5x_pci_set_cardbus_mode()`, `orion5x_pci_sys_setup()`, `orion5x_pci_sys_scan_bus()`, and `orion5x_pci_map_irq()`. Important internal pieces include `pcie_ops`, `pci_ops`, config access locks, `pcie_setup()`, `pci_setup()`, `orion5x_setup_pci_wins()`, and `rc_pci_fixup()`.

### Control Flow
PCIe setup initializes the controller, applies the Orion-1/NAS config-read workaround when needed, remaps IO space, and adds memory resources. Legacy PCI setup programs DDR decode windows, enables master/slave, forces host ordering, remaps IO space, and adds memory resources. Scan setup assigns bridge ops for controller 0 as PCIe and controller 1 as legacy PCI unless disabled.

### State, Persistence, And Dependencies
Persistent state includes PCI/PCIe bus numbering, resource windows, MBUS workaround window, host bridge resources, root-complex class fixups, and `orion5x_pci_disabled`/CardBus flags. Dependencies include plat-orion PCIe helpers, MVEBU MBUS DRAM info, Linux PCI core, and common register bit helpers.

### Integration Points
Board files provide `hw_pci` descriptors that call these setup/scan helpers and add board-specific IRQ mapping.

### Risks
Config cycles require spinlock atomicity. The workaround path only supports non-extended config space. Resource allocation failures panic. Bus-number logic and CardBus filtering are hardware-specific and easy to regress.

### Test Signals
PCIe endpoint enumeration, legacy PCI card enumeration, CardBus mode, Orion-1/NAS workaround boards, and root-complex resource/class fixups should all be validated.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/pci.c -->
