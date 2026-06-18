# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/tc_flower_l2_miss.sh

Purpose: validates flower `l2_miss` matching on bridge egress for unknown/known unicast, registered/unregistered multicast, link-local multicast, and broadcast traffic.

Important functions are `test_l2_miss_unicast`, `test_l2_miss_multicast_common`, IPv4/IPv6 multicast wrappers, `test_l2_miss_multicast`, `test_l2_miss_ll_multicast_common`, and `test_l2_miss_broadcast`. Setup builds a two-port bridge with clsact on `$swp2`. Tests use bridge FDB and MDB entries to transition between miss and non-miss states.

Control flow adds egress flower filters on `$swp2`, sends crafted traffic from H1 with `$MZ`, checks counters, adds/removes FDB or MDB entries, and retests. Multicast setup enables router-port behavior, bridge querier, valid IPv6 link-local source, and waits for MDB forwarding readiness. State is bridge FDB/MDB/multicast settings, tc filters, and host interfaces. Risks include bridge multicast timing, the empty placeholder `test_l2_miss_multicast_common2`, and exact counter assumptions. Test signals are expected counter transitions for l2_miss 1 vs 0 and explicit broadcast non-miss behavior.
