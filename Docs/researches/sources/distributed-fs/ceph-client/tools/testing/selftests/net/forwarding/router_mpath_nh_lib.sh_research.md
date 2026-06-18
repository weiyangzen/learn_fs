# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/router_mpath_nh_lib.sh

Purpose: shared helper library for nexthop multipath tests. It validates nexthop group statistics, dispatches software and hardware-stat paths, and probes 16-bit nexthop weight support.

Important functions are `nh_stats_do_test`, `nh_stats_test_dispatch_swhw`, `nh_stats_test_dispatch`, `__nh_stats_test_v4`, `__nh_stats_test_v6`, and `check_nhgw16`. `nh_stats_do_test` generates UDP flows across destination-port ranges, snapshots link TX counters and nexthop group counters, and requires the delta discrepancy to stay below 10 packets. `nh_stats_test_dispatch` checks `ip nexthop help` for `hw_stats`, enables hardware stats with JSON inspection via `jq`, and calls software plus hardware stat checks, with `xfail_on_veth` for unsupported veth hardware paths.

State is not persistent but it mutates nexthop group configuration (`ip nexthop replace ... hw_stats on/off type $nhgtype`) and sysctls in callers. Dependencies include `iproute2` nexthop JSON output, `jq`, `MZ`, link stat helpers, `absval`, and busy test harness logging. Risks include JSON schema drift, hardware stats unavailability, and counter races. Test signals are `log_test "NH stats test ..."` and explicit `check_err` on counter mismatches or failed hardware-stat enablement.
