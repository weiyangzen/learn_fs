# sources/distributed-fs/ceph-client/drivers/vhost/vsock.c

## Purpose
`vsock.c` implements the vhost transport for AF_VSOCK. It exposes `/dev/vhost-vsock`, binds a guest CID to a vhost device, moves packets between virtio-vsock queues and the host vsock core, and provides host-to-guest and guest-to-host transport operations.

## Important APIs, types, and functions
The central type is `struct vhost_vsock`, containing `struct vhost_dev`, two virtqueues, namespace state, CID hash linkage, a host-to-guest SKB queue, send work, reply accounting, and negotiated seqpacket state. Important functions are `vhost_transport_send_pkt`, `vhost_transport_do_send_pkt`, `vhost_vsock_handle_tx_kick`, `vhost_vsock_start`, `vhost_vsock_stop`, `vhost_vsock_set_cid`, `vhost_vsock_set_features`, `vhost_vsock_dev_ioctl`, open/release handlers, and module init/exit registration.

## Control flow
Open allocates a large `vhost_vsock`, initializes two queues and vhost core state, and stores it in `file->private_data`. Userspace sets owner/rings/features/CID through ioctls and starts the device. Host-to-guest packets are queued by CID lookup, then `send_pkt_work` drains SKBs into RX virtqueue buffers. Guest-to-host packets arrive on TX kicks, are copied from descriptors into SKBs, address-validated, and delivered to `virtio_transport_recv_pkt`. Release removes the CID from the global hash, waits for RCU readers, resets orphaned sockets, stops/flushed vhost, purges SKBs, and frees resources.

## State and persistence
Runtime state includes per-open queue configuration, CID hash membership, network namespace reference, pending SKBs, `queued_replies`, and negotiated features. It does not persist beyond device lifetime. Mutexes protect vhost/vq changes; a global mutex plus RCU protects CID lookup.

## Dependencies and integration points
The file integrates with vhost core, virtio-vsock packet helpers, AF_VSOCK transport registration, miscdevice operations, network namespaces, eventfd-backed virtqueues, and optional vhost IOTLB backend feature negotiation.

## Risks and test signals
Risks include CID collisions across namespaces, bad packet lengths, malformed descriptor direction, reply-queue starvation, partial RX buffer splitting for seqpacket EOM/EOR flags, teardown races with socket lookup, and feature/IOTLB mismatch. Test signals include vhost-vsock ioctl tests, namespace-isolated CIDs, stream and seqpacket traffic, oversized packet splitting, queue exhaustion/restart, orphan reset on release, and malformed guest descriptors.
