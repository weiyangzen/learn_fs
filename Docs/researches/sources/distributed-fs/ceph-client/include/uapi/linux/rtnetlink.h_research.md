<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/rtnetlink.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/rtnetlink.h

Purpose: defines the core rtnetlink ABI for network link, address, route, neighbor, rule, traffic-control, multicast, nexthop, VLAN, tunnel, and stats messages.

Important APIs, types, and functions: message IDs span `RTM_NEWLINK` through `RTM_GETTUNNEL`; `RTM_NR_MSGTYPES`, `RTM_NR_FAMILIES`, and `RTM_FAM` classify them. `struct rtattr` plus `RTA_*` macros define generic netlink attributes. Route ABI types include `struct rtmsg`, `rt_scope_t`, `rt_class_t`, `rtattr_type_t`, `struct rtnexthop`, `struct rtvia`, `struct rta_cacheinfo`, `RTAX_*` metrics, `struct rta_session`, and multicast stats. Link and TC messages use `struct ifinfomsg`, `prefixmsg`, `tcmsg`, `nduseroptmsg`, `tcamsg`, and TCA/TA access macros. Multicast subscriptions are exported as legacy `RTMGRP_*` masks and modern `enum rtnetlink_groups`.

Control flow: userspace sends netlink messages with an nlmsghdr type in the RTM range, a fixed family-specific struct payload, and a stream of aligned `rtattr` TLVs. The kernel validates lengths with `RTA_OK`/`RTNH_OK`, applies requested mutations or dumps state, and multicasts notifications to rtnetlink groups.

State and persistence behavior: this header has no storage. It serializes mutable kernel networking state: links, addresses, routes, rules, qdiscs/classes/filters/actions, nexthops, multicast DBs, namespaces, tunnels, and statistics. Route attributes may carry cached expiry and counters.

Dependencies and integration points: depends on netlink, link, address, and neighbor UAPI headers. It integrates with iproute2, routing daemons, traffic-control tools, namespace management, kernel FIB/neighbour/link subsystems, and rtnetlink multicast listeners.

Risks and edge cases: ABI compatibility is paramount. Attribute and nexthop parsing must enforce alignment and length. Deprecated values remain visible, legacy group masks differ from modern group IDs, route protocol/table IDs are shared with userspace daemons, and variable-length multipath/encap attributes are common bug sources.

Test signals: netlink selftests and iproute2 round trips for links, addresses, routes, rules, qdiscs, actions, nexthops, VLANs, and tunnels; fuzz malformed attributes; verify multicast notifications; test route dumps with metrics, multipath, encap, offload/trap flags, and strict length checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/rtnetlink.h -->
