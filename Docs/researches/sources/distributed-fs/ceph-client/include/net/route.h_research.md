# sources/distributed-fs/ceph-client/include/net/route.h

Purpose: declares IPv4 routing cache/dst structures, route lookup helpers, PMTU/redirect APIs, address-type helpers, uncached route management, and socket connection route setup helpers.

Important APIs and types: `struct rtable` embeds `dst_entry` first and stores generation, flags/type, input/output bit, gateway use/family/address, ingress ifindex, and PMTU lock/value. Helpers derive route scope/TOS from sockets, access skb rtable, determine input/output route, choose nexthop, initialize flowi4 from sockets, lookup output/input routes, update PMTU/redirect, classify address types, allocate/clone/release routes, map TOS to priority, connect/newports route lookup, get ingress ifindex/hoplimit, and resolve gateway neighbours.

Control flow: output callers build `flowi4`, perform route lookup, optionally redo lookup after port allocation for IPsec/rules, attach dst to skb/socket, and release with `ip_rt_put()`. Input callers run route input under RCU and force dst ref if successful.

State and persistence: route dst entries, uncached lists, per-net generation/cache stats, PMTU metrics, and neighbour references are runtime state.

Dependencies and integration points: depends on dst, FIB, inetpeer, flow, inet sockets, ARP/NDISC, DSCP, LSM flow classification, rtnetlink, XFRM/no-xfrm route flags, and IPv6 gateway neighbours.

Risks and test signals: risks include dst/rtable layout assumptions, RCU/refcount mistakes in input route forcing, incomplete flow keys bypassing rules, IPsec route redo omissions, gateway family handling, and PMTU lock bit packing. Test output/input lookups, policy routing, source routing options, port allocation route redo, PMTU/redirect, blackhole routes, IPv6 gateway nexthop, uncached route cleanup, and namespace/device teardown.
