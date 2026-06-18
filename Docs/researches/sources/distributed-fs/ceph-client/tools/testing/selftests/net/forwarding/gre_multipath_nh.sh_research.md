# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/gre_multipath_nh.sh

## Purpose
`gre_multipath_nh.sh` tests GRE multipath routes implemented with reusable nexthop objects. It covers both IPv4 and IPv6 payload routes using the same nexthop group to GRE devices.

## Important APIs, Functions, and Control Flow
Setup resembles `gre_multipath.sh`, but `sw1_create` creates IPv6 nexthop objects `101` and `102` pointing to `g1a/g1b`, then creates group `103`; both IPv4 and IPv6 routes use `nhid 103`. SW2 builds reverse nexthops `201`, `202`, and group `203`. `multipath4_test` and `multipath6_test` set the appropriate family hash policy to 1, replace nexthop group `103` with requested weights, send UDP traffic from H1 to H2, count path hits with tc filters on `$ul2`, evaluate distribution, and restore the unweighted group.

## State, Dependencies, Integration Points, and Risks
State includes GRE tunnels, nexthop objects and groups, routes by `nhid`, sysctls, tc filters, VLAN subinterfaces, and dual-stack host addressing. Dependencies include iproute2 nexthop support, `lib.sh`, `tc_rule_stats_get`, `$MZ`, and `multipath_eval`. The cleanup order deletes routes before nexthop groups and member nexthops, which is important because active routes reference those objects. Risks include object ID collisions in parallel runs and unsupported nexthop object syntax.

## Test Signals
Signals are IPv4/IPv6 ping success and weighted distribution checks for ECMP, 2:1, and 11:45 cases in each family.
