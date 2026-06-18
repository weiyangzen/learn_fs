<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mptcp/pm_kernel.c -->
# sources/distributed-fs/ceph-client/net/mptcp/pm_kernel.c

## Purpose
Implements the default "kernel" MPTCP path-manager backend. It stores per-netns endpoint configuration, handles Generic Netlink endpoint and limit commands, chooses local/remote address pairs for subflow creation, signals ADD_ADDR/RM_ADDR, tracks endpoint ID availability per MPTCP socket, creates port-based listener sockets, and registers the kernel PM ops.

## Important APIs, Types, and Functions
`struct pm_nl_pernet` stores endpoint list, ID bitmap, endpoint counters, and limits. Exported getters include `mptcp_pm_get_endp_signal_max()`, `mptcp_pm_get_endp_subflow_max()`, `mptcp_pm_get_endp_laminar_max()`, `mptcp_pm_get_endp_fullmesh_max()`, `mptcp_pm_get_limit_add_addr_accepted()`, and `mptcp_pm_get_limit_extra_subflows()`. Endpoint selection and connection logic is in `mptcp_pm_create_subflow_or_signal_addr()`, `fill_remote_addresses_vec()`, `fill_local_addresses_vec()`, and `mptcp_pm_nl_add_addr_received()`. Netlink callbacks include add/delete/flush/get/dump address, set/get limits, and set flags. Worker integration is `__mptcp_pm_kernel_worker()`.

## Control Flow
When an MPTCP socket is established, the backend lazily accounts the initial subflow endpoint, announces configured signal endpoints in list order, and creates subflows from configured subflow endpoints until endpoint and subflow limits are reached. Fullmesh endpoints combine a local endpoint with all known remote IDs; laminar endpoints pick one unused laminar local address; the C-flag special case uses subflow endpoints to respond to remote ADD_ADDR when default acceptance would otherwise reject it. Adding an endpoint validates flags/port rules, optionally creates a kernel MPTCP listener for signal-only port endpoints, appends the endpoint with automatic ID allocation, then iterates existing sockets to signal/connect. Removing or flushing endpoints sends RM_ADDR/RM_SUBFLOW and marks IDs available again.

## State and Persistence
Endpoint configuration is per netns in an RCU list protected by `pernet->lock`; entries can hold listener sockets for port endpoints. Per-socket PM state tracks `id_avail_bitmap`, `mpc_endpoint_id`, `local_addr_used`, `add_addr_signaled`, `add_addr_accepted`, and `extra_subflows`. Limits default to two extra subflows and are runtime netlink state.

## Dependencies and Integration Points
Depends on generated PM netlink policies, MPTCP PM common helpers, token table iteration, subflow connect/close helpers, endpoint parsing/fill helpers, socket creation/bind/listen APIs, netns generic storage, RCU, and MIB/event paths. It registers `mptcp_pm_kernel` with the PM registry and is selected by `ctrl.c` defaults.

## Risks
Endpoint ID accounting is complex, especially ID 0 aliasing to the initial subflow, automatic ID allocation, implicit endpoints, and reusing IDs after delete/flush. Fullmesh/laminar/C-flag modes can create too many or too few subflows if counters drift. Port-based endpoints create kernel sockets with special lock classes and must release them after RCU grace periods. Netlink validation must reject invalid flag combinations such as signal+fullmesh or port without signal-only semantics. Iterating all token sockets while adding/removing endpoints must handle sockets disappearing and avoid userspace PM sockets.

## Test Signals
Exercise `ip mptcp endpoint` add/delete/flush/show, automatic and explicit IDs, duplicate addresses, implicit endpoint replacement, port endpoints and listener events, set/get limits, backup/fullmesh flag changes, laminar endpoint selection, C-flag ADD_ADDR handling, endpoint removal sending RM_ADDR/RM_SUBFLOW, per-netns isolation, and stress with concurrent connections while endpoints change.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mptcp/pm_kernel.c -->
