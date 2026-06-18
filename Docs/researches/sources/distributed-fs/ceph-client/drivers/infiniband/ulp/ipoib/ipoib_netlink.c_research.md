# sources/distributed-fs/ceph-client/drivers/infiniband/ulp/ipoib/ipoib_netlink.c

## Purpose
`ipoib_netlink.c` registers the rtnl link type `ipoib` so userspace can create, delete, inspect, and change IPoIB child links through netlink instead of the legacy sysfs child interface.

## Important APIs, Types, And Functions
`ipoib_policy` defines `IFLA_IPOIB_PKEY`, `IFLA_IPOIB_MODE`, and `IFLA_IPOIB_UMCAST` as `u16` attributes. `ipoib_fill_info()` emits P_Key, connected/datagram mode, and umcast state. `ipoib_changelink()` applies mode and umcast changes. `ipoib_new_child_link()` validates `IFLA_LINK`, rejects child-of-child creation, initializes the new netdev with `ipoib_intf_init()`, calls `__ipoib_vlan_add()` with `IPOIB_RTNL_CHILD`, and then applies optional attributes. `ipoib_del_child_link()` queues child unregister. `ipoib_get_link_ops()`, `ipoib_netlink_init()`, and `ipoib_netlink_fini()` expose and register the static `rtnl_link_ops`.

## Control Flow And State
Newlink resolves the parent by ifindex in the target link netns, defaults the child P_Key to the parent P_Key when not specified, and uses the same child add core as VLAN/sysfs creation but with `IPOIB_RTNL_CHILD` so duplicate P_Keys are allowed and proprietary sysfs child attributes are skipped. Changelink delegates mode strings to `ipoib_set_mode()`, which may temporarily drop/reacquire rtnl, and toggles umcast directly. `fill_info` serializes the current state from `priv->pkey` and flag bits.

## Dependencies And Integration Points
The file depends on rtnetlink, netdevice lookup, IPoIB constants from `if_link.h`, and driver APIs from `ipoib.h`. It is registered at module init in `ipoib_main.c` and used by child creation in both the generic rtnl path and `ipoib_add_port()` where the ops pointer/priv size can be adjusted to match lower RDMA netdev private size.

## Risks And Test Signals
Risks include parent lookup across namespaces, child-of-child rejection, cleanup when `ipoib_changelink()` fails after registration, duplicate P_Key semantics differing from legacy sysfs, and `ipoib_set_mode()` lock behavior under rtnl. Test signals include `ip link add link ib0 name ib0.X type ipoib pkey ...`, `ip link set type ipoib mode connected/datagram umcast`, `ip -d link show`, duplicate RTNL child P_Keys, deletion of children, and invalid parent/type/attribute values.
