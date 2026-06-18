<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/virtio_scmi.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/virtio_scmi.h

Purpose: defines feature bits and virtqueue indexes for transporting ARM SCMI protocol messages over virtio.

Important APIs and types: `VIRTIO_SCMI_F_P2A_CHANNELS` advertises platform-to-agent notifications or delayed responses, and `VIRTIO_SCMI_F_SHARED_MEMORY` advertises statistics shared memory. Queue indexes define TX command queue, RX event queue, and maximum queue count.

Control flow, state, and persistence: SCMI commands flow on the TX queue and asynchronous events or delayed responses flow on RX when negotiated. The header owns no protocol state; SCMI agents/platform firmware maintain it.

Dependencies and integration points: depends on virtio types and integrates Linux SCMI transports, firmware protocol stacks, and virtio core.

Risks and test signals: risks include queue-index mismatch, missing notification support, and shared-memory feature drift. Test SCMI command/response, delayed responses, event delivery, stats region negotiation, and operation without P2A channels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/virtio_scmi.h -->
