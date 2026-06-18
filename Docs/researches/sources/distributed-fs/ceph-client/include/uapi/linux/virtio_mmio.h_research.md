<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/virtio_mmio.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/virtio_mmio.h

Purpose: defines the memory-mapped register layout for virtio MMIO transport devices used primarily by platform and embedded virtual machines.

Important APIs and types: register offsets cover magic/version/device/vendor IDs, feature selection, driver feature selection, queue selection, queue size, queue ready, notifications, interrupt status/ack, status, 64-bit queue descriptor/avail/used addresses, shared memory selection, config generation, and per-device config space. Interrupt bits are `VIRTIO_MMIO_INT_VRING` and `VIRTIO_MMIO_INT_CONFIG`.

Control flow, state, and persistence: the driver validates magic/version, negotiates features, configures queues, writes queue addresses, sets status, notifies queues, and acknowledges interrupts. Registers reflect volatile transport state only.

Dependencies and integration points: consumed by virtio-mmio drivers, device tree/ACPI platform enumeration, and virtio core queue setup.

Risks and test signals: risks include offset regressions, legacy page-size/PFN handling, config generation races, and 64-bit address half ordering. Test modern and legacy devices, shared memory regions, interrupt ack, queue reset paths, and config-change reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/virtio_mmio.h -->
