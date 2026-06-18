<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/virtio_net.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/virtio_net.h

Purpose: defines the full virtio network device ABI: feature bits, config space, packet header formats, control virtqueue commands, RSS/hash configuration, notification coalescing, and device statistics replies.

Important APIs and types: `VIRTIO_NET_F_*` covers checksum, GSO/TSO/UFO/USO, merged receive buffers, status, control virtqueue, VLAN, MAC, multiqueue, RSS/hash, RSC, standby, speed/duplex, UDP tunnel GSO, notification coalescing, and device stats. `struct virtio_net_config` exposes MAC, status, queue pairs, MTU, speed, duplex, and RSS limits. Packet metadata is in `struct virtio_net_hdr_v1`, hash/tunnel variants, and legacy headers. Control classes configure RX mode, MAC filters, VLAN filters, announce ACK, multiqueue/RSS/hash, guest offloads, coalescing, and stats.

Control flow, state, and persistence: data queues carry packet buffers prefixed by virtio net headers; the control queue changes filtering, queue steering, offloads, and coalescing. Runtime state lives in the device and driver netdev, not in the header.

Dependencies and integration points: depends on virtio IDs/config/types and Ethernet constants; integrates with Linux netdev, ethtool offloads/stats, NAPI, XDP-adjacent receive paths, and vhost/QEMU backends.

Risks and test signals: high-risk areas are packed layout, endian conversion, variable-length RSS/hash structs, feature-gated header sizes, offload correctness, MAC/VLAN filter semantics, and stats reply parsing. Test feature matrices, checksum/GSO variants, multiqueue resize, RSS indirection, hash reports, coalescing, and legacy compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/virtio_net.h -->
