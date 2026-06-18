<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/pci-bridge.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/pci-bridge.h

## Purpose
This header defines PowerPC PCI host bridge state, controller operation hooks, indirect config access helpers, device-tree PCI metadata, and hotplug/resource mapping entry points.

## Important APIs, Types, And Functions
It defines `struct pci_controller_ops`, `struct pci_controller`, indirect config flags, early config read/write helpers, `early_find_capability()`, `setup_indirect_pci()`, indirect read/write helpers, `pci_bus_to_host()`, PowerMac OF lookup, 64-bit `struct pci_dn`, `PCI_DN()`, pci_dn lookup/add/remove APIs, SR-IOV helpers, `pdn_to_eeh_dev()`, bus-node lookup, hotplug add/remove, IO-space map/unmap, PHB node assignment, controller lookup, OF range processing, and controller allocation/free.

## Control Flow
Platform PCI setup allocates a controller, processes OF ranges, installs config ops, scans buses, and uses controller hooks for DMA, probing, MSI, bridge setup, device enable/disable, and shutdown. Hotplug paths add/remove devices and pci_dn records.

## State And Persistence Behavior
`pci_controller` persists per PHB and records bus ranges, IO/memory windows, DMA window, device-tree node, config registers, resources, IOMMU, IRQ domain, and private data. `pci_dn` persists per OF PCI node and tracks PE/IOMMU/SR-IOV/EEH metadata.

## Dependencies And Integration Points
It depends on PCI core, resources, NUMA, IOMMU, device tree, IRQ domains, MSI, EEH, and SR-IOV. It is central to pseries, powernv, embedded, and PowerMac PCI support.

## Risks And Edge Cases
Indirect config quirks avoid real hardware hangs. Dynamic PHB removal must not leave stale pci_dn or IOMMU data. SR-IOV PE/M64 metadata is platform-sensitive. Resource window alignment affects reassignment.

## Test Signals
Run PCI enumeration, early config access, MSI, EEH, SR-IOV, PHB hotplug, IO/memory mmap, OF bus map creation, and dynamic PHB add/remove tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/pci-bridge.h -->
