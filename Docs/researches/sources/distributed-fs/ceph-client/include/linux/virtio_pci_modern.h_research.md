# sources/distributed-fs/ceph-client/include/linux/virtio_pci_modern.h

## Purpose
This header defines the helper interface and mapped capability state for modern virtio PCI devices.

## Important APIs, types, and functions
Key type is `virtio_pci_modern_device`, storing PCI device, mapped common/notify/isr/device/shared/admin capabilities, notify geometry, device ID, and modern-only state. Helpers include endian-safe MMIO reads/writes, feature get/set, generation/status access, queue vector/address/enable/size/count/reset helpers, notify mapping, probe/remove, and admin virtqueue index/number helpers.

## Control flow, state, and persistence
Probe locates and maps modern PCI capabilities, drivers negotiate extended features through select registers, configure queues via common config, map notify regions, and read/write device config through mapped BARs. Runtime state is PCI capability mapping, queue configuration, status, generation, and notification offsets.

## Dependencies and integration points
It depends on PCI, virtio config, and virtio PCI UAPI headers. It integrates modern virtio PCI transport, admin queues, shared memory regions, and virtio core feature/config operations.

## Risks and test signals
Risks include wrong BAR/offset mapping, notify multiplier errors, feature select misuse, queue reset semantics, and non-atomic two-part 64-bit writes. Tests should cover capability discovery, feature banks, queue setup/reset, notify mapping, config generation, status transitions, and admin queue discovery.
