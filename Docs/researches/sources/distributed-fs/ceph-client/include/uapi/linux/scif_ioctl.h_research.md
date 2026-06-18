<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/scif_ioctl.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/scif_ioctl.h

Purpose: defines the Intel SCIF character-device ioctl ABI for connecting MIC endpoints, sending messages, registering memory windows, performing remote copies, and using fences.

Important APIs, types, and functions: endpoint identity is `struct scif_port_id`. Ioctl payloads include `scifioctl_connect`, `scifioctl_accept`, `scifioctl_msg`, `scifioctl_reg`, `scifioctl_unreg`, `scifioctl_copy`, `scifioctl_fence_mark`, `scifioctl_fence_signal`, and `scifioctl_node_ids`. Ioctl commands range from `SCIF_BIND`, `SCIF_LISTEN`, `SCIF_CONNECT`, and `SCIF_ACCEPT*` through send/recv, memory registration, read/write, vector read/write, node discovery, and fence operations.

Control flow: userspace opens a SCIF endpoint, binds/listens or connects to a node/port, exchanges messages, registers local memory ranges, performs local/remote offset-based copies or virtual copies, and synchronizes DMA visibility with fences.

State and persistence behavior: endpoint connection state, registered windows, fence marks, and DMA mappings live in the SCIF driver and hardware/peer state. The ioctl structs are transient copy_from_user/copy_to_user payloads carrying user addresses as `__u64`.

Dependencies and integration points: depends on fixed-width Linux types and ioctl command macros from included kernel headers. It integrates with Intel MIC/MPSS SCIF drivers, DMA mapping, file descriptor endpoint lifetimes, and node topology discovery.

Risks and edge cases: all user pointers are encoded as 64-bit integers, so compat handling must be explicit. Offset/length overflow, stale remote registrations, fence pointer validity, endpoint teardown during DMA, and blocking accept/recv semantics are high-risk areas.

Test signals: connect/listen/accept pairs, send/recv length accounting, registration/unregistration bounds, DMA copy to/from remote windows, vector copy, fence mark/wait/signal, node discovery, invalid user addresses, and disconnect during active operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/scif_ioctl.h -->
