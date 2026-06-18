<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/smbdirect.h -->
# sources/distributed-fs/ceph-client/include/linux/smbdirect.h

## Purpose
`smbdirect.h` declares the in-kernel SMB Direct transport interface, mapping SMB over RDMA concepts to socket-like operations. It provides connection setup, negotiated parameter access, send/receive APIs, RDMA read/write memory registration, logging callbacks, and legacy proc diagnostics.

## Important APIs, Types, and Functions
Protocol-facing types are `struct smbdirect_buffer_descriptor_v1`, matching the MS-SMBD buffer descriptor with little-endian offset/token/length, and `struct smbdirect_socket_parameters`, which stores negotiation and transport limits such as timeouts, credits, max send/recv sizes, max RDMA read/write size, FRMR depth, keepalive settings, and port-range flags. Opaque runtime types are `struct smbdirect_socket`, `struct smbdirect_send_batch`, and `struct smbdirect_mr_io`.

Important APIs include RDMA capability helpers `smbdirect_netdev_rdma_capable_node_type()` and `smbdirect_frwr_is_supported()`, socket creation for active and accepted connections, parameter and kernel setting setters/getters, logging setup, connection state/wait helpers, bind/connect/listen/accept/shutdown/release, batched and iterator send functions, receive, send-drain wait, RDMA transmit, memory registration/deregistration, descriptor fill, and debug proc output.

## Control Flow
Active clients create a kernel SMB Direct socket, set initial negotiated parameters and kernel polling/GFP settings, bind if needed, then connect or connect synchronously. Servers create accepting sockets from RDMA CM IDs or listen and accept through the SMB Direct API. Data flow uses send batches or iterator sends for SMB messages, `recvmsg` for receive, and RDMA transmit/register APIs for direct read/write payloads. Memory registration returns an opaque MR object, fills buffer descriptors for the peer, and must be deregistered after use. Logging callbacks let upper layers filter and format events by level and class.

## State and Persistence Behavior
Connection parameters are negotiated at setup and are documented as stable unless explicitly changed. Runtime connection state, credits, pending sends, keepalive timers, registered memory, and RDMA resources live inside opaque socket/MR structures. No disk persistence exists; descriptors are wire-format transient structures.

## Dependencies and Integration Points
The header depends on Linux types, networking namespaces, netdevices, sockets, RDMA CM, InfiniBand attributes, RDMA read/write helpers, scatter/gather iterators, `seq_file`, and proto accept arguments. It integrates with SMB client/server code, RDMA core, network-device capability discovery, and diagnostics/logging paths.

## Risks and Test Signals
Risks include endian/packing mistakes in wire descriptors, negotiated size/credit mismatches, MR lifetime leaks, invalid remote keys, send batching flush errors, blocking waits during teardown, keepalive timeout races, and RDMA capability misdetection. Test signals include SMB Direct negotiation tests, RDMA loopback or soft-RoCE transfers, MR registration/deregistration leak checks, credit exhaustion tests, disconnect/reconnect handling, logging class coverage, and proc debug output consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/smbdirect.h -->
