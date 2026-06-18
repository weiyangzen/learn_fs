# sources/distributed-fs/ceph-client/drivers/infiniband/core/roce_gid_mgmt.c

## Purpose
`roce_gid_mgmt.c` keeps RoCE GID cache entries synchronized with Linux netdevice and IP address state. It reacts to Ethernet device registration, link, address, MAC, upper/lower, VLAN, and bonding changes, then adds or removes default and IP-derived GIDs for every relevant RoCE port.

## Important APIs, types, and functions
- `roce_gid_type_mask_support()` maps port RoCE capabilities to supported GID types.
- `rdma_roce_rescan_device()` and `rdma_roce_rescan_port()` enumerate netdevices and rebuild GIDs.
- `roce_del_all_netdev_gids()` deletes all cached GIDs for a netdevice.
- Notifier handlers: `netdevice_event()`, `inetaddr_event()`, and `inet6addr_event()`.
- Work handlers: `netdevice_event_work_handler()` and `update_gid_event_work_handler()`.
- Filter/callback helpers model RDMA netdevice relationships, upper devices, VLAN real devices, and bond active/inactive slave state.
- Lifecycle functions are `roce_gid_mgmt_init()` and `roce_gid_mgmt_cleanup()`.

## Control flow and behavior
Initialization creates an ordered `gid-cache-wq`, registers IPv4/IPv6 address notifiers, then registers the netdevice notifier last so existing devices can be enumerated without missing address events. Netdevice and address notifications only queue work; the work handlers later enumerate all RoCE netdevices and invoke add/delete callbacks under safer context. Address events convert IPv4/IPv6 socket addresses into GIDs and add/delete them for matching RoCE devices. Netdevice events compose up to three commands, such as deleting stale IP GIDs, adding default GIDs, and adding upper-device GIDs for bond masters.

## State, persistence, and dependencies
Persistent state is the global ordered workqueue and notifier registrations. Per-event work items hold netdevice references with `dev_hold()` until the queued work releases them. GID state itself lives in the IB cache via `ib_cache_gid_add()`, `ib_cache_gid_del()`, `ib_cache_gid_set_default_gid()`, and `ib_cache_gid_del_all_netdev_gids()`.

## Integration points
This file sits between Linux networking (`net_device`, RCU upper-dev walking, bonding, VLANs, inet/inet6 address notifiers, rtnl/net namespace iteration) and RDMA cache/core helpers (`ib_enum_all_roce_netdevs`, `ib_enum_roce_netdev`, `ib_device_get_netdev`, `rdma_ip2gid`). It is essential for RoCE address handle creation and userspace visibility of GID table contents.

## Risks and test signals
Risks include missed netdevice events due to notifier ordering, stale netdevice references, incorrect bond failover handling, duplicate default GIDs, RCU misuse while walking upper devices, and GID cache churn during unregister. Test signals include RoCE GID table changes after IP add/delete, VLAN creation/removal, bond enslave/release/failover, MAC address changes, namespace movement, IPv6 enabled/disabled builds, and module unload with pending work.
