## sources/distributed-fs/ceph-client/arch/mips/pci/pci-ip27.c

### Purpose
This SGI IP27/IP29 support file provides NUMA node mapping for PCI buses and a final IOC3 fixup needed to enable an ethernet PHY on specific IP29 system boards.

### Important APIs, Types, And Functions
With `CONFIG_NUMA`, `pcibus_to_node()` returns the `bridge_controller` NASID and is exported. `ip29_fixup_phy()` reads the IOC3 subsystem ID and writes the remote hub LED register for matching IP29 system board devices. `DECLARE_PCI_FIXUP_FINAL()` binds the fixup to SGI IOC3 devices.

### Control Flow
During PCI final fixups, IOC3 devices call `ip29_fixup_phy()`. The function exits unless the bus is on NASID 1, then reads `PCI_SUBSYSTEM_VENDOR_ID` and enables the PHY only for `IOC3_SUBSYS_IP29_SYSBOARD`.

### State, Persistence, And Dependencies
The persistent effect is a remote hub register write through `REMOTE_HUB_S()`. Dependencies are SGI SN address, hub, IOC3, and bridge-controller definitions.

### Integration Points
The file works with `pci-xtalk-bridge.c`, which creates `bridge_controller` instances, and with Linux PCI fixup infrastructure.

### Risks
The fixup is board-specific and assumes NASID 1 is the second module requiring the PHY action. Incorrect subsystem-ID emulation in bridge code would suppress or misapply it.

### Test Signals
On IP29 hardware, check IOC3 ethernet link/PHY availability on the second module and confirm `pcibus_to_node()` reports expected NASIDs under NUMA.
