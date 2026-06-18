# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/gre_inner_v6_multipath.sh

## Purpose
`gre_inner_v6_multipath.sh` is the IPv6 payload counterpart to the inner GRE multipath test. It verifies that IPv6 traffic carried inside IPv4 GRE is distributed across weighted underlay paths according to inner-flow hashing.

## Important APIs, Functions, and Control Flow
The topology mirrors the IPv4 version but gives H1/H2 IPv6 overlay subnets while keeping the GRE underlay IPv4. GRE tunnels `g1/g2` connect SW1 and SW4; SW2 has an ECMP route to the remote GRE endpoint via VLAN 111/222 paths; SW3 counts those paths with tc filters. `multipath6_test` sets `net.ipv4.fib_multipath_hash_policy=2` because the underlay lookup is IPv4, replaces the remote endpoint route with weighted nexthops, generates IPv6 UDP flows with source/destination ranges, computes tc counter deltas, and calls `multipath_eval`. `multipath_ipv6` runs 1:1, 2:1, and 11:45 cases.

## State, Dependencies, Integration Points, and Risks
State includes IPv6 host routes through GRE, IPv4 tunnel endpoint routes, tc filters, VLAN path counters, and the IPv4 multipath hash sysctl. Dependencies are `lib.sh`, GRE tunnel helpers, mausezahn IPv6 support, `tc_rule_stats_get`, and `multipath_eval`. The test is sensitive to packet volume and timing because weighted distribution is inferred from sampled counters.

## Test Signals
Signals are successful IPv6 ping through the tunnel and weighted distribution checks for each multipath weight pair.
