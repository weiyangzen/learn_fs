# sources/distributed-fs/ceph-client/net/ipv4/xfrm4_policy.c

## Purpose
This file registers IPv4-specific XFRM policy support. It provides route lookup, source-address selection, XFRM dst construction, PMTU/redirect forwarding, per-net dst ops setup, sysctl registration, and boot-time initialization of IPv4 XFRM state/protocol/policy.

## Important APIs, Types, and Functions
Important functions are `xfrm4_dst_lookup()`, `xfrm4_get_saddr()`, `xfrm4_fill_dst()`, `xfrm4_update_pmtu()`, `xfrm4_redirect()`, `xfrm4_dst_destroy()`, `xfrm4_net_init()`, `xfrm4_net_exit()`, and `xfrm4_init()`. Key structures include `xfrm4_dst_ops_template`, `xfrm4_policy_afinfo`, `xfrm4_net_ops`, `struct xfrm_dst`, and `struct rtable`.

## Control Flow
Policy lookup builds a `flowi4` from XFRM lookup params, including destination, optional source, DSCP, mark, protocol, ports, and L3 master device, then calls IPv4 route output. Source selection reuses this route lookup and reads the chosen `fl4.saddr`. Dst fill copies route metadata into the XFRM dst, holds the output device, and links the route into the uncached list. Per-net init copies dst ops, initializes dst entries, and optionally registers `net/ipv4/xfrm4_gc_thresh`.

## State and Persistence Behavior
Persistent state is per-net `net->xfrm.xfrm4_dst_ops`, optional per-net sysctl header, and XFRM policy AF registration. XFRM dsts persist as route wrappers until destroyed, at which point metrics and uncached route list membership are cleaned up.

## Dependencies and Integration Points
The file depends on IPv4 routing, l3mdev, dst metrics/lifetime management, XFRM policy core, sysctl, pernet operations, IPv4 blackhole routes, and state/protocol initialization in sibling XFRM files.

## Risks
Incorrect route metadata copying can break PMTU, gateway, local/broadcast/multicast flags, or input-route behavior. Per-net sysctl tables must duplicate init-net storage correctly. Device refs and uncached list removal must balance.

## Test Signals
Test policy route lookup with marks, DSCP, source address, L3 master, ports, blackhole route fallback, PMTU/redirect forwarding, per-net sysctl registration and teardown, network namespace creation failure unwinding, and XFRM dst destruction.
