# sources/distributed-fs/ceph-client/drivers/net/nlmon.c

Purpose: implements the `nlmon` virtual netdevice used to monitor netlink traffic through the netlink tap infrastructure.

Important APIs/types/functions: `struct nlmon` wraps `struct netlink_tap`. `nlmon_open()` registers the tap with `netlink_add_tap()`, `nlmon_close()` removes it, `nlmon_xmit()` accounts and frees transmitted skbs, and `nlmon_setup()` configures netdev type, features, stats, MTU bounds, and ops.

Control flow: module init registers rtnl link kind `nlmon`. Creating a device calls setup. Opening stores the netdev and module in the tap and adds it to netlink. Closing removes it. Captured/tapped packets are delivered through the netdev infrastructure, while explicit transmit on the device only updates length stats and drops the skb. Module exit unregisters the rtnl link ops.

State and persistence: per-device state is only the tap object in netdev private memory and per-CPU lstats. No persistent state exists.

Dependencies and integration: integrates with `netlink_add_tap()`/`netlink_remove_tap()`, rtnl link ops, ethtool link reporting, ARPHRD_NETLINK, and netdevice stats.

Risks: address assignment is rejected because the device is not Ethernet. The MTU is a soft netlink-message size default, not a hardware constraint. The tap must be removed on close to avoid stale module/netdev references.

Test signals: create `nlmon`, bring it up/down, observe netlink traffic with packet capture, verify `IFLA_ADDRESS` validation fails, check stats after traffic, and unload while devices are closed.
