# sources/distributed-fs/ceph-client/include/xen/interface/io/pvcalls.h

Purpose: defines the Xen PV calls socket-like protocol for forwarding socket operations between frontend and backend.

Important APIs/types/functions: `XENBUS_FUNCTIONS_CALLS`, `struct pvcalls_data_intf`, `DEFINE_XEN_FLEX_RING(pvcalls)`, command codes `PVCALLS_SOCKET`, `CONNECT`, `RELEASE`, `BIND`, `LISTEN`, `ACCEPT`, `POLL`, and request/response structs `xen_pvcalls_request` and `xen_pvcalls_response` with `DEFINE_RING_TYPES(xen_pvcalls, ...)`.

Control flow: command requests are placed on a balanced ring and responses echo `req_id` and `cmd` with a return code. Connect and accept can pass grant refs and event channels for per-connection data rings described by `pvcalls_data_intf`, which has separate in/out producer-consumer indexes and error fields.

State and persistence: socket IDs are 64-bit protocol handles. Data rings store stream state, errors, ring order, and grants until the socket is released.

Dependencies and integration points: includes `<linux/net.h>`, generic Xen ring helpers, and grant table types. Integrates with XenBus function discovery, event channels, guest socket APIs, and backend network stack forwarding.

Risks: address storage is fixed at 28 bytes and must match supported socket address families. Dummy union members force cross-architecture size stability; modifying them can break ABI. Data-ring error fields require careful synchronization with producer/consumer indexes.

Test signals: socket/bind/listen/connect/accept/release flows, poll behavior, stream data wraparound over flexible rings, error propagation, and structure size checks across 32-bit and 64-bit builds.
