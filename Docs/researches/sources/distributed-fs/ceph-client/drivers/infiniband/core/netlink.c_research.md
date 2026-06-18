# sources/distributed-fs/ceph-client/drivers/infiniband/core/netlink.c

## Purpose
`netlink.c` is the generic NETLINK_RDMA dispatcher for RDMA core. It registers per-client callback tables, validates RDMA netlink message client/op IDs, autoloads protocol modules, enforces admin permissions, dispatches doit and dump callbacks, and provides unicast/multicast helpers plus per-net namespace socket setup.

## Important APIs, types, and functions
- `rdma_nl_register()` and `rdma_nl_unregister()` publish and remove callback tables for RDMA netlink clients.
- `rdma_nl_chk_listeners()`, `rdma_nl_unicast()`, `rdma_nl_unicast_wait()`, and `rdma_nl_multicast()` wrap kernel netlink operations for RDMA users.
- `ibnl_put_msg()` and `ibnl_put_attr()` are exported helpers for legacy RDMA netlink message construction.
- `rdma_nl_rcv_msg()` validates a message, obtains the callback table, checks `RDMA_NL_ADMIN_PERM`, and selects dump or doit handling.
- `rdma_nl_rcv_skb()` is a local variant of `netlink_rcv_skb()` that also permits non-request LS responses.
- `rdma_nl_net_init()` and `rdma_nl_net_exit()` create and release each namespace's NETLINK_RDMA socket.

## Control flow
`rdma_nl_init()` initializes one rwsem per RDMA netlink client. Callback tables are stored with release semantics and protected against unregister by the per-client rwsem. On receive, the code extracts client and op from `nlmsg_type`, checks bounds with `is_nl_msg_valid()`, takes the client read lock, autoloads `rdma-netlink-subsys-%u` once if no table exists, and dispatches the callback if present.

For most clients, `NLM_F_DUMP` selects `netlink_dump_start()` and regular requests call `.doit`. IWCM is still forced through dump handling for compatibility. LS is special because LS responses overload a netlink flag and because RDMA_NL_LS is allowed to receive kernel-initiated response messages without `NLM_F_REQUEST`.

## State and persistence
Global state is `rdma_nl_types[]`, one callback table pointer and rwsem per client. Per-net namespace state is the `NETLINK_RDMA` socket in `struct rdma_dev_net`. No durable state is stored.

## Dependencies and integration points
This file depends on Linux netlink core, network namespaces, RDMA net namespace helpers, `rdma/rdma_netlink.h` protocol definitions, module autoloading, and callbacks registered by IWCM, LS, NLDEV, and other RDMA netlink clients. NLDEV is the only client allowed outside `init_net` in this version.

## Risks
- The hard-coded `max_num_ops` table must be updated with new RDMA netlink clients; the `BUILD_BUG_ON` catches only client-count changes.
- Callback unregister waits for in-flight commands, but callback implementations must still manage their own object lifetimes.
- Permission is enforced at the callback-table flag level. New admin operations must set `RDMA_NL_ADMIN_PERM`.
- Non-init net namespace support is intentionally restricted; expanding it requires auditing callbacks for namespace-safe object lookup.
- LS and IWCM compatibility branches are easy to break if generic netlink dispatch is simplified.

## Test signals
- Module load/unload tests should verify `rdma_nl_exit()` does not warn about registered callback tables.
- Netlink fuzzing should cover invalid client/op values, missing callbacks, malformed headers, dump vs doit flags, ACK paths, and permission denial.
- Namespace tests should confirm NLDEV works outside init_net and other clients are rejected.
- Listener and multicast tests should verify `RDMA_NL_GROUP_NOTIFY` behavior with and without subscribers.
