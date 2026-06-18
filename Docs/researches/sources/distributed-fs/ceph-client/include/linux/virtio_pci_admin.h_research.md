# sources/distributed-fs/ceph-client/include/linux/virtio_pci_admin.h

## Purpose
This header declares virtio PCI admin command helpers for device parts and optional legacy IO access mediation.

## Important APIs, types, and functions
APIs include optional legacy helpers for probing legacy IO support, common/device IO read/write, and notify-info lookup, plus `virtio_pci_admin_has_dev_parts()`, `virtio_pci_admin_mode_set()`, object create/destroy, device-parts metadata get, parts get, and parts set.

## Control flow, state, and persistence
Virtio PCI code uses admin queues to change admin mode, create/destroy admin objects, fetch/set device partition metadata, and optionally access legacy fields. State is device-admin runtime state and objects managed by the device.

## Dependencies and integration points
It depends on PCI and scatterlists. It integrates virtio PCI transports with admin queue features for device partitioning and legacy access.

## Risks and test signals
Risks include unsupported admin command paths, scatterlist sizing errors, object ID leaks, and legacy IO access without negotiated support. Tests should cover capability detection, mode setting, object lifecycle, metadata get, parts get/set, and disabled legacy config.
