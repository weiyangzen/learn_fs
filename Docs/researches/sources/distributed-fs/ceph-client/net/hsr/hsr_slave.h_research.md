## sources/distributed-fs/ceph-client/net/hsr/hsr_slave.h

Purpose: declares the HSR/PRP port-management API and inline helpers for recovering `struct hsr_port` from a slave netdevice under RTNL or RCU protection.

Important APIs/types/functions: declares `hsr_add_port()`, `hsr_del_port()`, `hsr_port_exists()`, and `hsr_invalid_dan_ingress_frame()`. `hsr_port_get_rtnl()` asserts RTNL and returns `rtnl_dereference(dev->rx_handler_data)` only when the device has the HSR RX handler. `hsr_port_get_rcu()` similarly returns `rcu_dereference(dev->rx_handler_data)` for RCU read-side callers. Both helpers rely on `hsr_port_exists()` comparing the registered RX handler to the HSR handler.

Control flow and state: the header does not mutate state. It encodes the core lifetime contract: `rx_handler_data` is meaningful only while the HSR RX handler is installed, and dereference mode must match the caller's lock context.

Dependencies and integration points: includes skb/netdevice/rtnetlink headers and `hsr_main.h`. Used by `hsr_slave.c` and other HSR modules needing to identify slave ownership.

Risks: callers that use `hsr_port_get_rcu()` outside an RCU read-side critical section can race with `hsr_del_port()` and `kfree_rcu()`. `hsr_port_get_rtnl()` must not be called without RTNL. The helper returns `NULL` for non-HSR devices and must be checked.

Test signals: lockdep coverage around RTNL/RCU callers, port add/delete races, and negative lookups on non-HSR netdevices.
