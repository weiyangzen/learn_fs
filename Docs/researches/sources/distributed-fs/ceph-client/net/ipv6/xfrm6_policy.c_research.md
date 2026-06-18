# sources/distributed-fs/ceph-client/net/ipv6/xfrm6_policy.c

## Purpose
Registers IPv6 address-family support for generic XFRM policy and destination handling. It provides route lookup, source address selection, transformed destination population/destruction, PMTU/redirect forwarding to underlying routes, per-net sysctl setup, and IPv6 XFRM init/teardown orchestration.

## Important APIs, types, and functions
Key structures are `xfrm6_dst_ops_template`, `xfrm6_policy_afinfo`, and `xfrm6_net_ops`. Important functions include `xfrm6_dst_lookup`, `xfrm6_get_saddr`, `xfrm6_fill_dst`, `xfrm6_update_pmtu`, `xfrm6_redirect`, `xfrm6_dst_destroy`, `xfrm6_dst_ifdown`, `xfrm6_net_init`, `xfrm6_net_exit`, `xfrm6_init`, and `xfrm6_fini`.

## Control flow
Policy lookup uses `xfrm6_dst_lookup` to build a `flowi6` from XFRM lookup params, including l3mdev, mark, addresses, protocol, and ULI fields, then calls `ip6_route_output` and returns either the route or its error. Source selection performs the same route lookup, obtains the IPv6 device, and calls `ipv6_dev_get_saddr`. Destination fill copies IPv6 route flags, gateway, destination/source route entries, route cookie, device ref, and idev ref into `xfrm_dst`, then adds it to the IPv6 uncached route list.

Net namespace initialization copies destination ops from the template, randomizes the secret, initializes sysctl when enabled, and registers pernet operations. Global init registers AF policy info, initializes protocol handlers, registers tunnel handlers for ESP/AH/IPCOMP, and unwinds in reverse on failure.

## State and persistence behavior
Per-net state includes `net->xfrm.xfrm6_dst_ops`, sysctl header/table storage, route operation secret, and destination GC threshold. XFRM destination objects hold device and `inet6_dev` references and uncached-route membership. No persistent storage exists.

## Dependencies and integration points
Depends on IPv6 route output, addrconf source selection, l3mdev, XFRM policy core, XFRM protocol/tunnel registration, sysctl, pernet operations, and IPv6 blackhole routing. `xfrm6_dst_ifdown` integrates with network-device teardown by switching affected idev references to loopback.

## Risks and test signals
Risks include route/device ref leaks, sysctl table lifetime bugs in non-init netns, uncached route list imbalance, wrong l3mdev/mark propagation, and init unwind mismatches. Test IPsec policy routing in multiple netns and VRFs, `xfrm6_gc_thresh` sysctl, interface down events with active XFRM routes, PMTU/redirect propagation, source address selection, and init failure injection around protocol/tunnel registration.
