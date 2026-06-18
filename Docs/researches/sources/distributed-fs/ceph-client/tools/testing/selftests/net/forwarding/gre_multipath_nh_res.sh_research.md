# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/gre_multipath_nh_res.sh

## Purpose
`gre_multipath_nh_res.sh` tests GRE weighted multipath through resilient nexthop groups. It is parallel to `gre_multipath_nh.sh` but creates groups with `type resilient buckets 512 idle_timer 0` and replaces them as resilient groups.

## Important APIs, Functions, and Control Flow
Topology and host setup match the non-resilient nexthop-object variant. `sw1_create` and `sw2_create` add member nexthops to GRE devices, create resilient group objects `103` and `203`, and route both IPv4 and IPv6 prefixes through those groups. `multipath4_test` and `multipath6_test` set family hash policy to 1, replace group `103` with weighted resilient members, send UDP traffic, count VLAN path hits through tc, evaluate observed ratio, and restore the resilient group without weights.

## State, Dependencies, Integration Points, and Risks
State includes resilient nexthop buckets, idle timer configuration, GRE devices, dual-stack routes, tc counters, and sysctls. Dependencies are the same as the non-resilient version plus kernel/iproute2 support for resilient nexthop groups. Distribution can be affected by resilient bucket assignment, so expected ratios depend on `multipath_eval` tolerances and bucket count.

## Test Signals
Signals are ping success and path packet ratios matching 1:1, 2:1, and 11:45 for IPv4 and IPv6 through resilient nexthop groups.
