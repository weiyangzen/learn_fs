# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/router_mpath_nh.sh

Purpose: tests regular nexthop-object ECMP and weighted multipath routing for IPv4 and IPv6, including blackhole nexthops and nexthop hardware/software statistics.

Important functions are `routing_nh_obj`, `multipath4_test`, `multipath6_test`, `multipath_test`, `multipath16_test`, `ping_ipv4_blackhole`, `ping_ipv6_blackhole`, and `nh_stats_test_v4/v6`. `routing_nh_obj` creates nexthops 101/102 and 104/105 on R1, group IDs 103/106, and reciprocal R2 groups 203/206. It sources `router_mpath_nh_lib.sh` for stats and feature probes.

Control flow builds four VRFs (H1, H2, R1, R2), configures link-local and IPv4 nexthop gateways, enables forwarding, creates nexthop objects, and runs pings, weighted traffic distribution tests, blackhole replacement tests, and stats tests. State is VRFs, routes, `ip nexthop` objects, sysctls `fib_multipath_hash_policy`, and link counters. Risks include dependency on `ip nexthop`, mausezahn flow generation, timing in packet counters, and feature variance for 16-bit weights or hardware stats. Test signals are ping success, ping failure with blackhole nhids, `multipath_eval` ratios, and link-vs-nexthop counter agreement.
