# sources/distributed-fs/ceph-client/include/rdma/rdma_cm.h

Purpose: Kernel RDMA Connection Manager API for address and route resolution, QP association, connection setup/teardown, and multicast membership across IB, RoCE, and iWARP.

Important APIs/types/functions: `enum rdma_cm_event_type`, `struct rdma_addr`, `struct rdma_route`, `struct rdma_conn_param`, `struct rdma_ud_param`, `struct rdma_cm_event`, `rdma_cm_event_handler`, `struct rdma_cm_id`, and APIs for create/destroy ID, restrict node type, bind/resolve address, resolve route/service, create/destroy QP, initialize QP attributes, connect/connect_ece, listen, accept/accept_ece, notify, reject, disconnect, join/leave multicast, set TOS/reuseaddr/afonly/ACK/RNR options, get service ID, reject-message helpers, `rdma_read_gids`, and `rdma_iw_cm_id`.

Control flow: Active side creates an ID, resolves address, resolves service/route or supplies an IB path, creates/associates a QP, and connects. Passive side binds, listens, receives request events, and accepts or rejects. Event callbacks serialize on the ID mutex and may sleep, but must not call `rdma_destroy_id` on the passed/listen ID; nonzero return destroys the ID.

State and persistence behavior: `rdma_cm_id` stores runtime device, context, QP, route, port space, QP type, port, and net work state. Destroying an ID cancels in-flight asynchronous operations. Device removal requires clients to release associated resources.

Dependencies and integration points: Depends on Linux sockets/IPv6, RDMA address resolution, IB SA, uapi RDMA CM, verbs QPs, and iWARP CM. Used by RDMA ULPs for connection management.

Risks: Callback lifetime restrictions, QP-before-ID destroy ordering, asynchronous resolution races, device removal cleanup, and small private-data limits are key hazards. `rdma_read_gids` is compatibility-only.

Test signals: Active/passive connection success and failures, ECE negotiation, route resolution errors, QP auto-transition, callback nonzero destruction, multicast join/leave, reject data extraction, device removal, and option ordering.
