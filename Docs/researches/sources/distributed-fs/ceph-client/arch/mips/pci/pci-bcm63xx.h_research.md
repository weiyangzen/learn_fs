## sources/distributed-fs/ceph-client/arch/mips/pci/pci-bcm63xx.h

### Purpose
This header provides BCM63xx PCI support declarations shared by the platform setup file and low-level PCI ops. It centralizes CardBus IDSEL policy, PCIe bus-number constants, external PCI ops declarations, and the shared I/O-space remap pointer.

### Important APIs, Types, And Functions
It defines `CARDBUS_PCI_IDSEL`, `PCIE_BUS_BRIDGE`, and `PCIE_BUS_DEVICE`. It declares `bcm63xx_pci_ops`, `bcm63xx_cb_ops`, `bcm63xx_pcie_ops`, and `pci_iospace_start`.

### Control Flow
There is no runtime control flow. The definitions influence how `pci-bcm63xx.c` registers controllers and how `ops-bcm63xx.c` forms config accesses.

### State, Persistence, And Dependencies
The header depends on BCM63xx CPU, I/O, register, and PCI device definitions. `pci_iospace_start` is initialized by the legacy PCI setup path and consumed by config ops.

### Integration Points
It is the contract between host-controller resource setup and config-space operations. CardBus support depends on reserving an otherwise normal PCI IDSEL value.

### Risks
Changing `CARDBUS_PCI_IDSEL` can conflict with real boards. Mismatched PCIe bus constants would break bridge/device config targeting.

### Test Signals
Build coverage with and without `CONFIG_CARDBUS`, plus PCIe config reads on BCM6328/6362 and legacy PCI config reads on older SoCs, validate the header contract.
