<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/vxlan/vxlan_multicast.c -->
# sources/distributed-fs/ceph-client/drivers/net/vxlan/vxlan_multicast.c

## Purpose
`vxlan_multicast.c` manages underlay multicast group membership for VXLAN sockets. It joins and leaves IPv4 IGMP or IPv6 multicast groups for the device default remote group and, when VNI filtering is enabled, for per-VNI remote groups.

## Important APIs, Types, and Functions
- `vxlan_igmp_join()` and `vxlan_igmp_leave()` perform the family-specific socket multicast join/leave operations using the VXLAN UDP socket and target interface index.
- `vxlan_group_used()` determines whether another running VXLAN device sharing the same socket still needs a multicast group, avoiding premature leave.
- `vxlan_group_used_by_vnifilter()` checks default and per-VNI remote groups for VNI-filter devices.
- `vxlan_multicast_join()` joins the default group and then per-VNI groups when `VXLAN_F_VNIFILTER` is set.
- `vxlan_multicast_leave()` leaves the default group only when it is no longer used, then leaves eligible per-VNI groups.

## Control Flow
On device open, `vxlan_core.c` calls `vxlan_multicast_join()`. If the default remote address is multicast, it calls `vxlan_igmp_join()` using `default_dst.remote_ifindex`, treating `-EADDRINUSE` as success. For VNI-filter devices it then scans the VNI group list and joins multicast per-VNI remote groups that differ from the default group. If any per-VNI join fails, the function rolls back previous joins in the group list.

On device stop or group change, `vxlan_multicast_leave()` checks whether the default multicast group is still used by another running VXLAN device sharing the relevant socket and interface. If not, it leaves the group. VNI-filter leave then scans per-VNI nodes and leaves each multicast group that is no longer used by another device or VNI.

## State and Persistence Behavior
The file does not allocate persistent driver state. It mutates multicast membership state held by the kernel socket/network stack. Decisions are based on live `vxlan_net` device lists, socket refcounts, running state, default destination, and VNI-filter lists. State disappears when sockets/devices are released.

## Dependencies and Integration Points
The code depends on `ip_mc_join_group()`, `ip_mc_leave_group()`, `ipv6_sock_mc_join()`, `ipv6_sock_mc_drop()`, socket locking, rtnl dereference rules, and VXLAN private helpers. It is called from device open/stop, VNI-filter group update/delete paths, and changelink default group updates.

## Risks and Edge Cases
- Shared sockets mean group membership must not be dropped while any other VXLAN device or VNI on the socket still uses the group.
- The family is derived from the device default remote address; mixed or incorrectly initialized address families could make the wrong socket path run.
- VNI-filter scans use `list_for_each_entry_safe()` under RTNL assumptions; callers must hold appropriate serialization.
- Rollback in `vxlan_multicast_join_vnigrp()` leaves all earlier matching groups up to the last successful node; changes to iteration order could alter rollback coverage.
- IPv6 paths are compile-time gated by `CONFIG_IPV6`.

## Test Signals
- Bring up/down VXLAN devices with IPv4 and IPv6 multicast remotes and confirm IGMP/MLD membership changes.
- Open multiple VXLAN devices sharing a socket/group and verify stopping one device does not drop membership needed by the other.
- Add/delete per-VNI multicast groups on a VNI-filter device while up and verify joins/leaves and rollback on injected errors.
- Change default multicast remote/interface through rtnetlink and check leave/join ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/vxlan/vxlan_multicast.c -->
