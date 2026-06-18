# sources/distributed-fs/ceph-client/include/linux/virtio_pci_legacy.h

## Purpose
This header defines the helper interface for legacy virtio PCI devices using IO BAR configuration space.

## Important APIs, types, and functions
Key type is `virtio_pci_legacy_device`, storing the PCI device, ISR mapping, and legacy IO config mapping. APIs include probe/remove, get/set features, generation/status access, queue selection/size/address/enable/notify, config vector, queue vector, config-space read/write, device reset, and deletion helpers.

## Control flow, state, and persistence
The legacy transport probes PCI IO resources, maps legacy config and ISR areas, negotiates 32/64-bit features as supported, programs queue PFNs/vectors, and tears down mappings on remove. State is PCI IO mapping and runtime queue/status/config values.

## Dependencies and integration points
It depends on PCI and virtio PCI UAPI definitions. It integrates legacy virtio PCI transport code with the generic virtio core.

## Risks and test signals
Risks include IO BAR mapping failure, legacy endian assumptions, queue PFN programming mistakes, and MSI-X vector handling. Tests should cover legacy probe/remove, feature negotiation, queue setup, config read/write, interrupt status, reset, and absent IO resources.
