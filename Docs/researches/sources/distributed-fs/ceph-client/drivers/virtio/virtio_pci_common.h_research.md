# sources/distributed-fs/ceph-client/drivers/virtio/virtio_pci_common.h

## Purpose
`virtio_pci_common.h` defines the private shared contract for the virtio-pci transport. It centralizes the per-queue, admin-queue, and per-device data structures used by common, legacy, modern, and admin helper files, and declares the cross-file operations that back `virtio_config_ops`.

## Important APIs, types, and functions
- `struct virtio_pci_vq_info` stores a virtqueue pointer, list node, and MSI-X vector.
- `struct virtio_pci_admin_vq` stores admin virtqueue metadata, spinlock, supported command/capability bitmaps, device-parts object limits, ID allocator, name, and queue index.
- `struct virtio_pci_device` embeds `struct virtio_device`, the PCI device, legacy/modern transport union, ISR pointer, queue lists, queue info array, admin VQ, MSI-X bookkeeping, transport callbacks, and optional admin-VQ index callback.
- `to_vp_device()` converts a generic virtio device to the private PCI wrapper.
- Declarations expose shared queue operations, bus naming, affinity operations, legacy/modern probe/remove, VF-to-PF lookup, admin VQ helpers, and admin command execution.
- `VIRTIO_LEGACY_ADMIN_CMD_BITMAP`, `VIRTIO_DEV_PARTS_ADMIN_CMD_BITMAP`, and `VIRTIO_ADMIN_CMD_BITMAP` define the admin command set the driver can negotiate.

## Control flow
The header has no standalone runtime flow, but its callback fields define the dispatch model: common code calls `setup_vq`, `del_vq`, and `config_vector` through function pointers installed by legacy or modern probe. Modern probe may also install `avq_index`, which lets common queue discovery create the admin virtqueue after normal queues.

## State and persistence behavior
The structs declared here are the persistent in-memory state for each virtio-pci function. The header also encodes compile-time policy: legacy admin commands are included only when `CONFIG_VIRTIO_PCI_ADMIN_LEGACY` is enabled; otherwise only device-parts admin commands are negotiated.

## Dependencies and integration points
It depends on Linux PCI, interrupt, spinlock/mutex, virtio, virtio config, virtio ring, and public legacy/modern virtio PCI headers. It is included by all virtio-pci implementation files in this work item and forms their ABI boundary.

## Risks and test signals
Risks include stale struct contracts between common and transport-specific files, admin command bitmap mismatches with device capabilities, MSI-X vector constants that must stay consistent with allocation policy, and array indexing assumptions for `vqs` vs admin queue. Test signals are build coverage under legacy enabled/disabled, admin legacy enabled/disabled, modern-only devices without device config, admin VQ negotiation, queue affinity operations, and SR-IOV helper users.
