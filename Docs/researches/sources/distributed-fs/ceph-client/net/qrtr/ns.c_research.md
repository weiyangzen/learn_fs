# sources/distributed-fs/ceph-client/net/qrtr/ns.c

## Purpose
`ns.c` implements the QRTR nameservice/control-plane socket. It tracks nodes, advertised services, and lookup subscribers, then broadcasts or unicasts service lifecycle notifications using QRTR control packets.

## Important APIs, Types, And Functions
External lifecycle APIs are `qrtr_ns_init()` and `qrtr_ns_remove()`. Important types are `struct qrtr_server_filter`, `struct qrtr_lookup`, `struct qrtr_server`, and nameservice-local `struct qrtr_node`. Important helpers include `node_get()`, `server_match()`, `server_add()`, `server_del()`, `service_announce_new()`, `service_announce_del()`, `lookup_notify()`, `announce_servers()`, and command handlers for HELLO, BYE, DEL_CLIENT, NEW_SERVER, DEL_SERVER, NEW_LOOKUP, and DEL_LOOKUP.

## Control Flow
Initialization creates a kernel AF_QIPCRTR datagram socket, creates an ordered workqueue, hooks `sk_data_ready`, binds to `QRTR_PORT_CTRL`, records the local node id, and broadcasts HELLO. Data-ready queues `qrtr_ns_worker()`, which drains control packets with `kernel_recvmsg(MSG_DONTWAIT)`, decodes `qrtr_ctrl_pkt.cmd`, emits tracepoints, and dispatches command handlers.

HELLO replies with HELLO and local server announcements. NEW_SERVER adds or replaces a server entry and broadcasts local services; it also notifies matching lookups. DEL_SERVER removes a service. DEL_CLIENT removes lookups and the service for a closing port, and notifies local servers. BYE removes all servers for a remote node and notifies local servers. NEW_LOOKUP accepts only local observers, stores the lookup with bounded count, sends current matches, then sends an empty end-of-list notification. DEL_LOOKUP removes matching subscriptions.

Removal restores the original data-ready callback, cancels work, destroys the workqueue, restores module references that were dropped after creating the in-module kernel socket, and releases the socket.

## State And Persistence
Global nameservice state is `nodes` xarray, `node_count`, and `qrtr_ns` singleton fields: kernel socket, broadcast address, lookup list/count, workqueue/work item, saved callback, and local node id. Each node owns an xarray of services keyed by port and a bounded server count. This state is memory-only and rebuilt after module load.

## Dependencies And Integration Points
The file integrates with AF_QIPCRTR sockets, `qrtr_ctrl_pkt` ABI, kernel send/receive APIs, ordered workqueues, socket callbacks, module reference accounting, and QRTR tracepoints.

## Risks
The nameservice has explicit caps (`QRTR_NS_MAX_NODES`, `QRTR_NS_MAX_SERVERS`, `QRTR_NS_MAX_LOOKUPS`) to prevent unbounded memory growth; exceeding them drops new state. Spoofing checks exist for DEL_CLIENT and local server unregister, but other control traffic relies on QRTR node/port routing semantics. The worker serializes through an ordered workqueue but list/xarray state is not protected by a broad lock, so callback/work ordering is important. Module refcount manipulation is delicate because the kernel socket is owned by the same module.

## Test Signals
Coverage should include HELLO exchange, service add/replace/delete, lookup subscription and end-of-list notification, BYE cleanup, DEL_CLIENT spoof rejection, local-only NEW_LOOKUP restriction, cap enforcement, invalid command handling, data-ready restoration on init failure/remove, and module unload after nameservice socket creation.
