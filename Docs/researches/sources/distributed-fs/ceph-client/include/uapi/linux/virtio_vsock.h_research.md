<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/virtio_vsock.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/virtio_vsock.h

Purpose: defines the virtio transport packet format and config values for AF_VSOCK communication between guests, hosts, hypervisors, and nested VMs.

Important APIs and types: feature `VIRTIO_VSOCK_F_SEQPACKET` gates sequenced packet sockets. `struct virtio_vsock_config` exposes the guest CID. `struct virtio_vsock_hdr` carries source/destination CIDs and ports, payload length, socket type, operation, flags, buffer allocation, and forward count. Operations cover request, response, reset, shutdown, read/write, credit update, and credit request. Flags mark shutdown direction and seqpacket end markers.

Control flow, state, and persistence: connections handshake with request/response/RST, payloads use RW packets, and credit fields implement flow control. Socket state lives in vsock core and transport queues.

Dependencies and integration points: included by vsockmon and virtio-vsock drivers; integrates with AF_VSOCK sockets, socket diagnostics, and hypervisor transports.

Risks and test signals: risks include credit accounting bugs, CID/port confusion, seqpacket boundary loss, reset handling, and packed layout drift. Test stream and seqpacket connect, shutdown, flow-control exhaustion, transport reset events, and packet capture decoding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/virtio_vsock.h -->
