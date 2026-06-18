# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/gre_multipath.sh

## Purpose
`gre_multipath.sh` tests weighted ECMP where the route itself forwards IPv4 traffic to two GRE tunnel devices. Unlike the inner-hash tests, the multipath route’s nexthops are the GRE devices `g1a` and `g1b`.

## Important APIs, Functions, and Control Flow
Setup creates H1/SW1/SW2/H2, two VLAN underlay paths, and two GRE tunnel pairs with distinct local/remote endpoint addresses. SW1 routes the H2 subnet through a multipath route with `nexthop dev g1a` and `nexthop dev g1b`; SW2 configures reverse tunnels and tc ingress filters on `$ul2` for VLAN IDs 111/222. `multipath4_test` sets `net.ipv4.fib_multipath_hash_policy=1`, replaces the route with caller-supplied weights on `g1a/g1b`, sends UDP traffic varying destination port, reads VLAN path counters, evaluates weights, then restores route/sysctl. `multipath_ipv4` runs ECMP and two weighted cases.

## State, Dependencies, Integration Points, and Risks
State includes GRE devices, route nexthops, VLAN underlay, tc filters, VRFs, and IPv4 hash policy sysctl. Dependencies include `lib.sh`, `tunnel_create`, `tc_rule_stats_get`, `$MZ`, and `multipath_eval`. Risks are statistical distribution variance and possible route/tunnel cleanup leftovers if interrupted.

## Test Signals
Signals are baseline IPv4 ping and observed tc counter ratios matching 1:1, 2:1, and 11:45 route weights.
