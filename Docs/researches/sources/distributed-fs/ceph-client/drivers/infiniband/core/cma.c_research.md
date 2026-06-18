<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/cma.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/core/cma.c

## Purpose

`cma.c` implements the kernel RDMA Connection Manager Agent. It translates the public `rdma_cm_id` API into device selection, address and route resolution, port binding, listen/connect/accept/reject/disconnect operations, QP initialization, multicast join/leave, netdevice change notifications, and IB/iWARP CM event delivery. It is the bridge between ULPs using `rdma_cm.h` and the lower RDMA address, SA, IB CM, iWARP CM, GID cache, net namespace, neighbour, and netdevice subsystems.

## Important APIs, types, and functions

The key internal objects are `struct cma_device`, `struct cma_pernet`, `struct rdma_bind_list`, `struct cma_work`, `struct cma_multicast`, `struct cma_hdr`, and `struct cma_req_info`. The private CM identifier state lives in `struct rdma_id_private` from `cma_priv.h`, while per-net port-space xarrays live in `struct cma_pernet`.

Important exported APIs include `__rdma_create_kernel_id()`, `rdma_create_user_id()`, `rdma_destroy_id()`, `rdma_create_qp()`, `rdma_destroy_qp()`, `rdma_init_qp_attr()`, `rdma_bind_addr()`, `rdma_resolve_addr()`, `rdma_resolve_route()`, `rdma_set_ib_path()`, `rdma_listen()`, `rdma_connect()`, `rdma_connect_locked()`, `rdma_accept()`, `rdma_reject()`, `rdma_disconnect()`, `rdma_join_multicast()`, `rdma_leave_multicast()`, `rdma_resolve_ib_service()`, `rdma_read_gids()`, and option setters for service type, ACK timeout, minimum RNR timer, address reuse, AF-only matching, and node-type restriction.

Important internal paths are `cma_acquire_dev_by_src_ip()`, `cma_validate_port()`, `cma_ib_acquire_dev()`, `cma_iw_acquire_dev()`, `cma_resolve_ib_dev()`, `cma_ib_id_from_event()`, `cma_find_listener()`, `cma_work_handler()`, `addr_handler()`, `cma_query_handler()`, `cma_ib_handler()`, `cma_iw_handler()`, `cma_ib_req_handler()`, `iw_conn_req_handler()`, `cma_process_remove()`, and the `cma_add_one()`/`cma_remove_one()` RDMA client callbacks. The module also exports configfs-facing helpers for default RoCE GID type and TOS.

## Control flow

Module initialization allocates an ordered `rdma_cm` workqueue, registers per-net xarray state, registers with the SA client, netdevice notifier, netevent notifier, RDMA device client, and finally configfs. When an RDMA device appears, `cma_add_one()` creates a `cma_device`, initializes per-port default RoCE GID type and TOS, attaches it to `dev_list`, and spawns per-device listeners for any wildcard listeners on `listen_any_list`.

A typical active connection starts with ID creation in `RDMA_CM_IDLE`, optional binding through `rdma_bind_addr()`, address resolution through `rdma_resolve_addr()`, route resolution through `rdma_resolve_route()`, and connection through `rdma_connect()` or `rdma_connect_locked()`. Address resolution either binds loopback, resolves AF_IB directly, or calls `rdma_resolve_ip()` and later `addr_handler()`. Device acquisition validates GID attributes, net namespace access, port protocol, bound netdevice, and VLAN/RoCE/iWARP details before attaching a `cma_device`. Route resolution uses SA path records for IB, constructs path records locally for RoCE, and queues immediate completion for iWARP. Connection uses IB CM REQ/SIDR or iWARP connect, formatting `cma_hdr` private data for IP-based IB CM requests.

A passive path binds a port in a per-net xarray, transitions to `RDMA_CM_LISTEN`, and either creates a transport-specific listener on a bound device or creates internal per-device IDs for wildcard listeners. IB CM and iWARP request callbacks create child IDs, copy address and path information, acquire the matched device/port/GID, deliver `RDMA_CM_EVENT_CONNECT_REQUEST`, and then let the consumer accept or reject. Established, rejected, disconnected, unreachable, and timewait events are translated from lower CM events and delivered under `handler_mutex`.

Asynchronous transitions are serialized through `cma_wq` and `cma_work_handler()`, which performs guarded state transitions before invoking the consumer event handler. Device removal sets IDs to `RDMA_CM_DEVICE_REMOVAL`, sends a removal event, cancels outstanding address, route, or listen operations, and waits for reference completion. Netdevice bonding failover and neighbour updates queue address-change or unreachable events for affected IDs.

## State and persistence

State is in memory only. `rdma_id_private.state` is the central FSM, protected by both `handler_mutex` and a spinlock for selected transitions. ID lifetime uses `refcount_t` plus `completion`, and device lifetime uses `cma_device.refcount` plus `completion`. Per-net port bindings are stored in xarrays keyed by RDMA port space and service number. Device attachments are tracked in `cma_device->id_list`; wildcard listens are tracked in `listen_any_list`; RoCE neighbour monitoring uses the `id_table` red-black tree keyed by bound ifindex and destination IP. Route data, service records, path records, multicast state, GID attrs, and AH attributes are dynamically allocated and released on destroy or leave.

No disk persistence is performed. Configfs changes to default RoCE mode/TOS are runtime-only fields in `cma_device`. Hardware and network state enter through GID cache lookups, SA queries, neighbour updates, netdevice state, and lower CM IDs.

## Dependencies and integration points

The file depends on Linux net namespaces, routing, IPv4/IPv6, VLAN, neighbour, netdevice notifier, workqueue, xarray, rbtree, random, mutex/spinlock/refcount/completion APIs, and RDMA core headers. It integrates with `rdma_addr` for address resolution, `ib_sa` for path/service/multicast records, `ib_cm` for IB CM and SIDR, `iw_cm` for iWARP, GID cache helpers from `core_priv.h`, resource tracking, configfs helpers in `cma_configfs.c`, and tracepoints in `cma_trace.h`. External consumers are kernel RDMA ULPs and user CM plumbing that allocate IDs, receive CM events, and call exported connection APIs.

## Risks

The main risk is concurrency. State changes cross interrupt, workqueue, notifier, CM callback, consumer callback, and destroy contexts, so `handler_mutex`, spinlocks, reference counting, and completion waits must stay paired. Device removal is especially sensitive because callbacks may destroy IDs while removal is in progress. Port binding correctness depends on per-net xarray locking, `reuseaddr`, AF-only semantics, wildcard address matching, service-ID mapping for AF_IB, and privileged-port checks. RoCE handling is sensitive to GID type selection, VLAN and traffic-class mapping, bound netdevice lifetime, neighbour updates, IPv6 link-local scope, and net namespace migration. Private-data header sizing uses offset arithmetic and must not overflow. Multicast join/leave must pair SA multicast, RoCE IGMP, queued work, and AH attribute destruction correctly.

Subtle bugs can also come from one-based versus `rdma_start_port()` port indexing, GID attr reference leaks, stale `dev_put()` calls, address-family mismatches, event-handler return semantics that destroy IDs, or lower CM IDs left attached after send failures.

## Test signals

Useful signals are clean RDMA CM module load/unload, configfs registration, RDMA device add/remove with no leaks or deadlocks, and resource tracking showing expected CM IDs. Functional tests should cover active/passive RC over IB, RoCE, and iWARP; UD SIDR; wildcard listen across multiple devices; bind/reuse/AF-only combinations; IPv4, IPv6, IPv6 link-local, AF_IB, loopback, and specific-source binds; route failure and timeout paths; consumer rejection private data; ECE connect/accept; QP auto transitions; multicast join/leave for IB and RoCE; bonding failover and neighbour MAC-change events; net namespace teardown; and device hot removal during address, route, connect, listen, and multicast operations. Kernel tracepoints under `rdma_cma` and debug messages should show coherent transitions with no WARNs, leaked refs, or stuck work items.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/cma.c -->
