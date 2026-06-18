# sources/distributed-fs/ceph-client/arch/um/drivers/virt-pci.c Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/virt-pci.c -->
## sources/distributed-fs/ceph-client/arch/um/drivers/virt-pci.c

### Purpose
This file implements the UML virtual PCI host bridge. It maps synthetic config/BAR spaces through `logic_iomem`, supports endpoint registration, and provides a small MSI domain.

### Important APIs, Types, And Functions
Key APIs are `um_pci_device_register()`, `um_pci_device_unregister()`, platform registration helpers, logic_iomem map callbacks, config/BAR operation dispatchers, MSI message composition, IRQ-domain allocation/free, and `pci_root_bus_fwnode()`.

### Control Flow
Device init registers config/iomem/platform windows, allocates a host bridge and MSI domain, maps per-slot config windows, and probes the PCI bus. Registered devices occupy one of eight slots and trigger rescans. Config/BAR accesses recover the endpoint and call its `um_pci_ops`.

### State, Persistence, And Dependencies
State is global: bridge, fwnode, IRQ domain, eight device slots, platform device pointer, mapped config windows, and MSI allocation bitmap. Dependencies include PCI core, MSI helpers, `logic_iomem`, UML IRQ allocation, and `virt-pci.h`.

### Integration Points And Risks
Risks include eight-device and no-multifunction limits, simplistic INTx mapping, init-failure cleanup gaps for ioremaps, MSI vector exhaustion, and trusting endpoint callbacks. Integration is used by VFIO and PCI-over-virtio.

### Test Signals
Test enumeration, slot exhaustion, register/unregister, config/BAR width validation, MSI allocation/free, platform window mapping, OF node lookup, and removal during rescan.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/virt-pci.c -->
