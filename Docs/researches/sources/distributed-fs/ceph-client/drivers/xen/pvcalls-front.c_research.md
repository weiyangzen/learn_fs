# sources/distributed-fs/ceph-client/drivers/xen/pvcalls-front.c

## Purpose
`pvcalls-front.c` implements the Xen PV Calls frontend socket shim. It exports socket-operation helpers that replace selected IPv4 stream socket operations with protocol requests sent to a backend over Xenbus command rings and per-connection grant-backed data rings.

## Important APIs, types, and functions
Public exports are `pvcalls_front_socket`, `pvcalls_front_connect`, `pvcalls_front_bind`, `pvcalls_front_listen`, `pvcalls_front_accept`, `pvcalls_front_sendmsg`, `pvcalls_front_recvmsg`, `pvcalls_front_poll`, and `pvcalls_front_release`. `struct pvcalls_bedata` stores the command ring, grant ref, IRQ, socket list, and response slots. `struct sock_mapping` stores active or passive socket state, including grant refs, data-ring pointers, wait queues, status and inflight flags. Important internals include `pvcalls_front_event_handler`, `alloc_active_ring`, `create_active`, `__write_ring`, `__read_ring`, passive/active poll helpers, and xenbus probe/remove/change callbacks.

## Control flow
Probe validates backend protocol version and capabilities, allocates a shared command ring, grants it to the backend, binds an event channel, writes xenstore keys, and enters `Initialised`. Socket creation allocates a mapping and sends `PVCALLS_SOCKET`. Connect and accept allocate active data rings, grant pages to the backend, send ring references and event channels, then wait for command responses. Send/receive operate directly on the active ring with memory barriers and IRQ notification. Bind/listen/accept/poll operate on passive socket command requests and wait queues. Release sends `PVCALLS_RELEASE`, waits for backend acknowledgement, then tears down mappings after refcounted in-flight operations drain. Remove disconnects the frontend, wakes blocked users, and frees all mappings.

## State and persistence
State is runtime-only and tied to a single supported front/back connection. `pvcalls_front_dev` and `pvcalls_refcount` gate global device lifetime. Each socket stores its `sock_mapping` in `sock->sk->sk_send_head`. Active mappings own grant references, event-channel IRQs, data-ring pages, and mutexes for read/write serialization. Passive mappings track bind/listen state and single inflight accept/poll operations. No persistent storage is written.

## Dependencies and integration points
The frontend depends on Xenbus, grant tables, event channels, Xen flex-ring macros, Linux socket APIs, wait queues, atomics, and the local `pvcalls-front.h` declarations. It integrates with higher-level networking code by exporting socket operation helpers and with the backend through xenstore keys `version`, `ring-ref`, and `port`.

## Risks and test signals
Risks include using `sk_send_head` as private storage, single backend limitation, ring index validation, blocking waits without backend progress, shared-memory ordering, refcount drain loops, nonblocking accept state, grant leak on partial setup, and disconnect while send/receive waits. Test signals include IPv4 stream connect/send/recv, passive bind/listen/accept, `MSG_DONTWAIT`, `poll`, backend removal while operations are active, malformed backend responses, full data rings, unsupported socket flags, and repeated release paths.
