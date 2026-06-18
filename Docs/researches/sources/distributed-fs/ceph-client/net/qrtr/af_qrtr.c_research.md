# sources/distributed-fs/ceph-client/net/qrtr/af_qrtr.c

## Purpose
`af_qrtr.c` implements the AF_QIPCRTR socket family and the QRTR endpoint core. It manages local QRTR sockets/ports, remote endpoint nodes, packet header parsing/serialization, broadcast/local/remote routing, and QRTR transmit flow control.

## Important APIs, Types, And Functions
Public endpoint APIs are `qrtr_endpoint_register()`, `qrtr_endpoint_unregister()`, and `qrtr_endpoint_post()`. Socket operations include `qrtr_create()`, `qrtr_bind()`, `qrtr_connect()`, `qrtr_sendmsg()`, `qrtr_recvmsg()`, `qrtr_getname()`, `qrtr_ioctl()`, and `qrtr_release()`. Core structures include `struct qrtr_sock`, `struct qrtr_node`, `struct qrtr_tx_flow`, packet headers `qrtr_hdr_v1`/`qrtr_hdr_v2`, and skb control block `struct qrtr_cb`.

## Control Flow
Endpoint drivers register a `struct qrtr_endpoint` with an `xmit` callback. Registration allocates a `qrtr_node`, initializes flow-control xarray and RX queue, optionally assigns a node id, links it into the global node list, and stores the node in the endpoint. Incoming endpoint data enters `qrtr_endpoint_post()`, which validates alignment and header version, extracts source/destination/type/confirm fields, validates payload size and control packet constraints, assigns node ids learned from packets, handles `QRTR_TYPE_RESUME_TX`, or queues the skb to the destination port socket.

Outgoing socket data flows through `qrtr_sendmsg()`. The socket is autobound if needed, destination is selected from msg name or connected peer, and routing chooses broadcast, local enqueue, or node enqueue. Remote sends call `qrtr_node_enqueue()`, which runs `qrtr_tx_wait()` flow control, prepends a v1 QRTR header, pads to 4-byte alignment, and invokes the endpoint `xmit` callback under `ep_lock`. Local and broadcast enqueue copy/queue skbs to local sockets and all known nodes.

Receive dequeues datagrams, returns the source address, and sends a resume-tx control packet if the incoming packet requested confirmation. Endpoint unregister clears the endpoint pointer, emits BYE notifications for all node ids backed by the endpoint, wakes flow-control waiters, and drops the node reference.

## State And Persistence
Global runtime state includes `qrtr_local_nid`, `qrtr_nodes` radix tree, `qrtr_all_nodes` broadcast list, and `qrtr_ports` xarray. Per-node state includes endpoint pointer, kref, nid, flow-control entries, and rx queue. Per-socket state includes bound local sockaddr and connected peer. State is volatile and reset on module unload or socket/endpoint release.

## Dependencies And Integration Points
The file registers `AF_QIPCRTR` as a datagram socket family and initializes QRTR nameservice via `qrtr_ns_init()`. Transport drivers in `mhi.c`, `smd.c`, and `tun.c` use the endpoint API. It uses Linux socket, skb, radix-tree, xarray, RCU, mutex, and waitqueue primitives.

## Risks
Packet parser correctness is critical because endpoint transports pass raw remote data. Flow-control waiters can stall if resume packets are lost; `qrtr_tx_flow_failed()` mitigates lost confirm messages. Node unregister races are controlled by `ep_lock`, node refs, and wakeups, but endpoint removal still stresses blocked senders. Port assignment treats control port as xarray index 0 and requires capability checks for privileged low ports. Broadcast copies may partially fail under memory pressure.

## Test Signals
Coverage should include v1/v2 packet parsing, malformed size/alignment/control packets, auto node assignment, bridge node assignment through NEW_SERVER, local/broadcast/remote send routing, flow-control low/high watermark behavior, resume-tx handling, endpoint unregister wakeups, privileged port binding, socket release DEL_CLIENT broadcast, `TIOCINQ`/`TIOCOUTQ`, and module init failure unwind.
