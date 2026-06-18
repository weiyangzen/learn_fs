<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/virtio_ids.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/virtio_ids.h

Purpose: assigns stable virtio device IDs and transitional PCI IDs used by drivers, devices, hypervisors, and userspace implementations to identify virtio device classes.

Important APIs and types: `VIRTIO_ID_*` constants cover network, block, console, rng, balloon, SCSI, 9p, GPU, input, vsock, crypto, IOMMU, memory, sound, filesystem, pmem, SCMI, I2C, watchdog, GPIO, SPI, and other virtio classes. `VIRTIO_TRANS_ID_*` defines legacy transitional PCI device IDs.

Control flow, state, and persistence: there is no runtime flow or state; IDs are consumed during device enumeration and driver matching.

Dependencies and integration points: included by virtio device-specific UAPI headers, PCI/MMIO transports, QEMU/vhost-style devices, and kernel module alias generation.

Risks and test signals: ID reuse or mismatch can bind the wrong driver or break userspace device emulation. Test with compile-time include users, module alias generation, virtio bus enumeration, and compatibility against the virtio specification registry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/virtio_ids.h -->
