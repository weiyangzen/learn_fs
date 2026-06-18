# sources/distributed-fs/ceph-client/include/trace/events/vsock_virtio_transport_common.h

Purpose: Instruments virtio-vsock packet allocation and receive paths.

Important APIs/types/functions: Defines `virtio_transport_alloc_pkt` and `virtio_transport_recv_pkt`, capturing virtio-vsock header fields such as source/destination CID/port, length, type, operation, flags, buffer allocation size, and return status.

Control flow: Virtio-vsock transport code emits allocation traces when constructing packets and receive traces when packets arrive. TP assignment snapshots packet header state before later queueing or freeing changes it.

State/persistence: Packet state remains owned by virtio-vsock transport; trace buffers persist copies of header metadata.

Dependencies/integration: Depends on virtio-vsock transport structs and tracepoint infrastructure; integrated with host/guest vsock diagnostics.

Risks: Header field semantics are protocol ABI. Incorrect formatting or reading freed packets would break debugging and stability.

Test signals: Run vsock connect/send/receive tests with trace events enabled and verify packet op/type/length sequences.
