<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/vsockmon.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/vsockmon.h

Purpose: defines the packet capture header and enums for the vsockmon AF_VSOCK monitoring device.

Important APIs and types: `struct af_vsockmon_hdr` records source/destination CIDs and ports, operation, transport type, and transport header length. Operations include unknown, connect, disconnect, control, and payload. Transport values include no-info and virtio, where the transport header is `struct virtio_vsock_hdr`.

Control flow, state, and persistence: captured records contain vsockmon header, optional transport header, and payload for payload operations. The monitor snapshots traffic; no persistent state is defined here.

Dependencies and integration points: depends on `virtio_vsock.h` and integrates with packet capture tooling, AF_PACKET-like monitoring, and vsock transport debugging.

Risks and test signals: risks include length misparsing, missing payload for non-payload ops, and transport-specific header drift. Test capture of connect/disconnect/control/payload packets, virtio header decoding, and truncated capture handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/vsockmon.h -->
