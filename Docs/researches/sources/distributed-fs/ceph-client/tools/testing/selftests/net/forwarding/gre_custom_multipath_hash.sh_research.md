# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/gre_custom_multipath_hash.sh

## Purpose
`gre_custom_multipath_hash.sh` validates custom multipath hashing for traffic carried inside an IPv4 GRE tunnel. The underlay has two ECMP paths between tunnel endpoints; the test confirms selected inner packet fields drive distribution when `net.ipv4.fib_multipath_hash_policy=3`.

## Important APIs, Functions, and Control Flow
The topology has H1 and H2 behind SW1/SW4, a GRE tunnel pair `g1/g2`, and an underlay routed through SW2/SW3 with two VLAN paths. SW3 installs tc flower ingress filters on `$ul32` for VLAN IDs 111 and 222 to count path use. Flow generators vary inner IPv4/IPv6 source/destination addresses, UDP source/destination ports, and IPv6 flow label. `custom_hash_test` snapshots tc counters, sends traffic, computes path deltas and percent imbalance with `bc`, and checks balanced or unbalanced expectation.

`custom_hash` sets IPv4 custom hash policy, runs `custom_hash_v4` and `custom_hash_v6`, then restores it. The field masks use inner-field bits: `0x0040` inner source IP, `0x0080` inner destination IP, `0x0200` inner flowlabel, `0x0400` inner source port, and `0x0800` inner destination port. Neighbor GC thresholds are raised for families where generated destinations create many neighbor entries.

## State, Dependencies, Integration Points, and Risks
State includes GRE tunnel devices, VRF routes, underlay ECMP route, VLAN subinterfaces, tc counters, sysctl hash policy/fields, neighbor GC thresholds, and generated overlay traffic. Dependencies include `lib.sh`, tunnel helpers, `tc_rule_stats_get`, `$MZ`, `$PING6`, `bc`, and kernel support for inner-field hashing. Risks are statistical balance flakiness, counter noise, and stale sysctls if cleanup is interrupted. The IPv6 overlay tests intentionally program IPv4 fib multipath hash fields because the underlay route between GRE endpoints is IPv4.

## Test Signals
Signals are ping reachability plus per-field balanced/unbalanced assertions from tc VLAN path counters. Logged packet deltas show the observed distribution.
