# sources/distributed-fs/ceph-client/include/rdma/rdma_netlink.h

Purpose: RDMA netlink registration and messaging API for kernel RDMA subsystems, notifications, and dynamic RDMA link operations.

Important APIs/types/functions: `struct rdma_nl_cbs`, `enum rdma_nl_flags`, `MODULE_ALIAS_RDMA_NETLINK`, `rdma_nl_register`, `rdma_nl_unregister`, `ibnl_put_msg`, `ibnl_put_attr`, `rdma_nl_unicast`, `rdma_nl_unicast_wait`, `rdma_nl_multicast`, `rdma_nl_chk_listeners`, `rdma_nl_notify_event`, `struct rdma_link_ops`, `rdma_link_register`, `rdma_link_unregister`, `MODULE_ALIAS_RDMA_LINK`, and `MODULE_ALIAS_RDMA_CLIENT`.

Control flow: Subsystems register callback tables by uapi index. Netlink requests dispatch to `doit` or `dump`; producers allocate messages in skbs, append attributes, and send by PID or multicast group. Link providers register `newlink` and `dellink` handlers.

State and persistence behavior: Runtime registry of callbacks/link ops and transient skb messages. Userspace reconstructs state through dumps; the API itself does not persist settings.

Dependencies and integration points: Depends on Linux netlink, RDMA uapi netlink definitions, and `ib_verbs.h`. Integrates with rdma userspace tooling, resource/counter control, device notifications, and soft/link drivers.

Risks: Mutating callbacks need correct admin-permission flags. Attribute type/length mismatches break uapi. Wrong subsystem/client/op indexes disrupt userspace. Multicast paths must tolerate no listeners.

Test signals: Register/unregister, admin permission enforcement, doit/dump dispatch, malformed attributes, unicast wait behavior, multicast listener/no-listener cases, event notification payloads, and link module alias autoload.
