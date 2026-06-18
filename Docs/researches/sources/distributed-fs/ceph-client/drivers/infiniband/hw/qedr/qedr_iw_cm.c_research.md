# sources/distributed-fs/ceph-client/drivers/infiniband/hw/qedr/qedr_iw_cm.c

## Purpose
`qedr_iw_cm.c` implements QEDR's iWARP connection-management glue between Linux `iw_cm` and QED firmware. It handles active connects, passive listens, accept/reject, MPA events, address/VLAN/MAC resolution, iWARP QP reference management, and asynchronous disconnect/close/error events.

## Important APIs, Types, And Functions
The exported RDMA core callbacks are `qedr_iw_connect`, `qedr_iw_create_listen`, `qedr_iw_destroy_listen`, `qedr_iw_accept`, `qedr_iw_reject`, `qedr_iw_qp_add_ref`, `qedr_iw_qp_rem_ref`, and `qedr_iw_get_qp`. Internal callbacks include `qedr_iw_event_handler`, `qedr_iw_mpa_request`, `qedr_iw_active_complete`, `qedr_iw_passive_complete`, `qedr_iw_disconnect_event`, `qedr_iw_disconnect_worker`, `qedr_iw_close_event`, and `qedr_iw_qp_event`.

## Control Flow
For active connect, the code validates ports, allocates an endpoint, loads and references the QP from `dev->qps`, references the `iw_cm_id`, fills QED CM info from IPv4 or IPv6 socket addresses, resolves VLAN and neighbor MAC, computes MSS from the initial iWARP MTU, sets private data/ORD/IRD/QP fields, sets a wait-for-connect bit, and calls `iwarp_connect`. Passive listen allocates a listener, references the CM ID, fills listen parameters from local address and VLAN, and calls `iwarp_create_listen`. MPA request allocates an endpoint and reports `IW_CM_EVENT_CONNECT_REQUEST` with provider data. Accept attaches a QP to that endpoint and calls `iwarp_accept`; reject sends `iwarp_reject` with no QP.

Firmware events are translated into iw_cm or ib_qp events. Active/passive complete signals `qp->iwarp_cm_comp` and sends established/connect-reply events. Disconnect is deferred to `dev->iwarp_wq` because it modifies QP state and calls the upper CM event handler outside atomic callback context. Close drops the endpoint reference. Fatal QP events become `IB_EVENT_QP_FATAL` or `IB_EVENT_QP_ACCESS_ERR`.

## State And Persistence Behavior
State is held in `qedr_iw_ep`, `qedr_iw_listener`, QP krefs/completions, CM ID references, and the `dev->qps` xarray. Endpoint krefs own QP and CM ID references until close or failure. Bits in `qp->iwarp_cm_flags` prevent duplicate connect/disconnect transitions. There is no persistent state.

## Dependencies And Integration Points
The file depends on Linux IPv4/IPv6 route and neighbor APIs, VLAN helper APIs, `iw_cm`, QED iWARP operations, and QEDR private QP/device state. It is registered from `main.c` only for iWARP devices.

## Risks And Test Signals
Risks include refcount imbalance across active failure, passive reject, disconnect work, and close ordering; stale neighbor entries causing unresolved MACs while returning success; address-family corner cases when IPv6 is disabled; and races between QP destruction and CM callbacks. Test signals include active/passive iWARP connection tests for IPv4 and IPv6, private-data propagation, accept/reject paths, listener teardown under pending connects, disconnect while QP destroy waits on completions, route-neighbor miss behavior, VLAN interfaces, and lockdep/KASAN refcount stress.
