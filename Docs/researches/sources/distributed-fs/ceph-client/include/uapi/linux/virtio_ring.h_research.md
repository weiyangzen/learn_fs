<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/virtio_ring.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/virtio_ring.h

Purpose: defines the split and packed virtqueue ring ABI shared by virtio drivers and devices.

Important APIs and types: descriptor flags include NEXT, WRITE, and INDIRECT; packed ring flags encode avail/used bits and event suppression. Feature bits include `VIRTIO_RING_F_INDIRECT_DESC` and `VIRTIO_RING_F_EVENT_IDX`. `struct vring_desc`, `vring_avail`, `vring_used_elem`, `vring_used`, and `struct vring` define split-ring memory layout. Helpers `vring_init()`, `vring_size()`, and `vring_need_event()` calculate layout and event decisions. Packed descriptors use `struct vring_packed_desc` and `struct vring_packed_desc_event`.

Control flow, state, and persistence: guests publish descriptor chains through avail rings, devices consume and return used elements, and both sides use index/event suppression to reduce notifications. Ring state is shared memory and volatile across device reset.

Dependencies and integration points: consumed by virtio core, vhost, KVM-backed devices, and userspace virtio implementations.

Risks and test signals: high risk lies in alignment, wraparound arithmetic, event-index logic, descriptor ownership, endian mode, and indirect descriptor validation. Test split/packed rings, 16-bit index wrap, notification suppression, indirect chains, malformed descriptors, and legacy layout sizing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/virtio_ring.h -->
