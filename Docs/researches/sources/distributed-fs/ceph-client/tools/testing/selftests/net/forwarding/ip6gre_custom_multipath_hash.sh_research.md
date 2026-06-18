# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/ip6gre_custom_multipath_hash.sh

## Purpose
`ip6gre_custom_multipath_hash.sh` validates custom multipath hashing for traffic carried inside an IPv6 GRE tunnel. It mirrors the IPv4 GRE custom hash test but uses IPv6 underlay tunnel endpoints and `net.ipv6.fib_multipath_hash_policy`.

## Important APIs, Functions, and Control Flow
The topology has H1/H2 overlay networks, an IP6GRE tunnel pair `g1/g2`, and a two-path IPv6 underlay between tunnel endpoints through SW2/SW3 with VLAN 111 and 222. SW3 attaches tc filters on `$ul32` to count path use. Flow generators vary inner IPv4 and IPv6 source/destination addresses, ports, and IPv6 flow label. `custom_hash_test` compares tc counter deltas and classifies distribution as balanced or unbalanced using a plus/minus 20 percent window.

`custom_hash` sets `net.ipv6.fib_multipath_hash_policy=3`, runs IPv4-overlay and IPv6-overlay inner-field tests, then restores it. `custom_hash_v4` sets IPv6 hash field masks for inner IPv4 source/destination and ports, while raising IPv4 neighbor thresholds for destination churn. `custom_hash_v6` tests inner IPv6 source/destination, flow label, and ports with IPv6 neighbor thresholds. The chosen sysctl family is IPv6 because the underlay lookup to the remote tunnel endpoint is IPv6.

## State, Dependencies, Integration Points, and Risks
State includes IP6GRE tunnels, IPv6 underlay ECMP routes, VRFs, VLAN path counters, `net.ipv6` multipath hash sysctls, neighbor GC thresholds, and high-volume generated traffic. Dependencies include IP6GRE support, `lib.sh`, tunnel helpers, mausezahn, ping6, `bc`, and tc stats helpers. Risks include statistical imbalance, packet loss under high generated flow counts, and sysctl restoration if the run is interrupted.

## Test Signals
Signals are IPv4/IPv6 overlay ping success and per-field balanced/unbalanced assertions from tc path counters.
