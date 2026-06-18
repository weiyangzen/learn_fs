<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/virtio_pcidev.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/virtio_pcidev.h

Purpose: defines a virtio protocol for virtual PCI device operations, letting a device backend receive config, MMIO/PIO, interrupt, MSI, and PME messages.

Important APIs and types: `enum virtio_pcidev_ops` names config read/write, MMIO read/write/memset, INTx, MSI, and PME operations. `struct virtio_pcidev_msg` carries operation, BAR, size, address, and variable payload data; scalar fields are native endian while many payload values are little endian.

Control flow, state, and persistence: a frontend emits operation messages for PCI access and interrupt signaling; the backend fills read data or consumes write data. Persistent state is the emulated PCI device configuration and BAR content outside this header.

Dependencies and integration points: integrates with virtio transport, PCI emulation, interrupt routing, and hypervisor/device-model code.

Risks and test signals: risks include native-endian vs little-endian confusion, invalid access sizes, BAR bounds, and interrupt message ordering. Test config read/write widths, MMIO variable sizes, memset, INTx/MSI delivery, and PME notification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/virtio_pcidev.h -->
