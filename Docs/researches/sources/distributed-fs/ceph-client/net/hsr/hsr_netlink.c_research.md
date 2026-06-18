## sources/distributed-fs/ceph-client/net/hsr/hsr_netlink.c

Purpose: implements the rtnetlink link type `hsr` and a generic-netlink family named `HSR`. It creates and destroys HSR/PRP master devices, exposes configured slave/interlink/protocol metadata, emits ring/node notifications, and serves node status/list queries from userspace.

Important APIs/types/functions: `hsr_policy` validates rtnl attributes such as `IFLA_HSR_SLAVE1`, `IFLA_HSR_SLAVE2`, `IFLA_HSR_INTERLINK`, `IFLA_HSR_VERSION`, and `IFLA_HSR_PROTOCOL`. `hsr_newlink()` resolves slave devices in the target namespace, validates they differ, handles optional interlink, maps `HSR_PROTOCOL_PRP` to `PRP_V1`, rejects PRP+interlink, and calls `hsr_dev_finalize()`. `hsr_dellink()` synchronously deletes timers, tears down debugfs, ports, self-node, node tables, and queues unregister. `hsr_fill_info()` reports slave/interlink ifindexes, supervision address, sequence number, version, and protocol. Generic-netlink operations include `hsr_nl_ringerror()`, `hsr_nl_nodedown()`, `hsr_get_node_status()`, and `hsr_get_node_list()`.

Control flow and state: link creation is RTNL-driven and depends on already allocated netdev private storage. Deletion stops timers before freeing state that timer callbacks may reference. Node queries take `rcu_read_lock()`, find the master by ifindex, allocate a reply skb, pull data from `hsr_get_node_data()` or `hsr_get_next_node()`, then unicast replies. Node-list dump restarts with a preserved position when an skb fills.

Dependencies and integration points: integrates with `rtnl_link_ops`, `genl_family`, `hsr_device`, `hsr_framereg`, debugfs helpers, node database helpers, and UAPI `hsr_netlink.h`. Notifications use multicast group `hsr-network`.

Risks: several notification paths allocate with `GFP_ATOMIC` and only warn on failure, so userspace observability is best-effort. `hsr_get_node_status()` and `hsr_get_node_list()` return netlink acks with `-EINVAL` but otherwise often return `0`, matching legacy generic-netlink behavior but making caller-side diagnostics coarse. Correct RCU lifetime depends on keeping all netdev/node lookups inside the read-side section.

Test signals: create/delete `ip link add type hsr` variants, PRP creation rejection cases, `ip -d link show`, and generic-netlink node status/list queries. Ring-error/node-down paths need fault or topology tests because they are asynchronous notifications.
