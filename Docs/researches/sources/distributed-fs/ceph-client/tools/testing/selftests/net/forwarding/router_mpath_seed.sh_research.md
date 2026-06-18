# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/router_mpath_seed.sh

Purpose: validates `net.ipv4.fib_multipath_hash_seed` behavior and its effect on nexthop selection for IPv4 and IPv6 nexthop groups. It uses ten nexthops per group and hardware stats to detect the active member.

Important functions are `nexthops_create`, `test_mpath_seed_get`, `nh_stats_snapshot`, `get_active_nh`, `probe_nh`, `probe_seed`, `test_mpath_seed`, and `test_mpath_seed_stability`. `nexthops_create` creates IDs 1001-1010 and 2001-2010, group IDs 1000/2000 with `hw_stats on`, and routes through those groups.

Control flow saves the seed sysctl, creates two-router topology, creates nexthops, checks ping reachability, repeatedly writes/reads seed values, probes active nexthop distribution across 100 seed values, and confirms repeated seeds select stable nexthops. State is sysctl, nexthop objects, routes, JSON nexthop stat counters, and VRFs. Risks include hardware stats support, `jq` processing, seed affects both IPv4 and IPv6 expectations, and stats thresholds hiding low packet counts. Test signals are all ten nexthops being hit across seed sweeps, stable selection for fixed seeds, and successful seed set/get checks.
