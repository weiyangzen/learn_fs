# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/router_mpath_nh_res.sh

Purpose: tests resilient nexthop groups, especially bucket preservation and weight replacement behavior under different idle timers. It mirrors `router_mpath_nh.sh` topology but creates nexthop groups with `type resilient buckets 512`.

Key functions are `routing_nh_obj`, `multipath4_test`, `multipath6_l4_test`, `multipath_test`, `multipath16_test`, and inherited `nh_stats_test_v4/v6`. `multipath_test` runs three phases: idle timer 0 where weight changes should apply immediately, idle timer 120 where active buckets should preserve the original 1:1 distribution, and idle timer 5 where sleeps allow buckets to idle and weight changes to apply.

Control flow creates H1/H2/R1/R2 VRFs, link-local and IPv4 gateway addresses, forwarding, resilient nexthop objects, then traffic distribution and stats tests. State is `ip nexthop` resilient groups, routes, sysctls, link counters, and VRFs. Risks include long sleeps, kernel/iproute2 feature differences, resilient bucket aging timing, and mausezahn traffic not activating enough buckets on slow systems. Test signals are successful pings, `multipath_eval` ratios matching expected immediate or preserved distributions, 16-bit weight feature probe, and inherited software/hardware nexthop stat validation.
