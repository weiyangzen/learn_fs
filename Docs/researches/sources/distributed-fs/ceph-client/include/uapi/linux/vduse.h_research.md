# sources/distributed-fs/ceph-client/include/uapi/linux/vduse.h

## Purpose
Defines the ioctl and read/write control-message ABI for VDUSE, which lets userspace implement virtio devices and attach them through the vDPA infrastructure.

## Important APIs, Types, And Constants
`VDUSE_BASE` selects the ioctl type. API versions `0` and `1` distinguish base support from virtqueue groups and address-space IDs. Control-device ioctls get/set API version and create/destroy named devices. `struct vduse_dev_config` describes device name, virtio vendor/device ids, features, virtqueue count/alignment, optional group and ASID counts, config-space size, and variable config bytes.

Device ioctls manage IOTLB and virtqueue state. IOTLB structs describe IOVA ranges, mmap offsets, permissions, userspace memory registrations, capabilities, and v2 ASID-aware variants. Feature/config ioctls get negotiated features, update config space, and inject config interrupts. Virtqueue structs configure queue index, max size, group, split/packed state, descriptor/driver/device addresses, readiness, kick eventfds, and queue interrupt injection. Read/write control messages use `enum vduse_req_type` and request/response structs for getting vq state, setting virtio status, updating IOTLB ranges, and setting vq group ASIDs.

## Control Flow, State, And Persistence
Userspace first negotiates API version on `/dev/vduse/control`, creates a device, opens `/dev/vduse/$NAME`, sets up queues and IOTLB mappings, attaches through vDPA, then services kernel requests read from the device node and writes responses. Persistent runtime state includes created VDUSE devices, virtqueue configuration/readiness, eventfd bindings, IOVA mappings, negotiated features, config space, device status, and per-group ASIDs until destroyed or closed.

## Dependencies And Integration Points
Depends on `<linux/types.h>` and ioctl macros via normal UAPI context. It integrates with virtio drivers, vDPA bus attachment, eventfd notification, mmap/file-descriptor based IOVA access, userspace device emulators, and IOMMU/IOTLB update flows.

## Risks And Test Signals
Risks include unvalidated flexible-array sizes, page-alignment errors, IOVA overlap/ASID mistakes, stale eventfds, incorrect split versus packed queue state, request/response ID mismatches, and failure to zero reserved fields for forward compatibility. Tests should cover API negotiation, create/destroy lifetime, queue setup before attachment, IOTLB register/deregister/get-fd paths, ASID-aware v2 paths, config IRQ injection, vq kick/irq eventfds, and read/write request handling under malformed inputs.
