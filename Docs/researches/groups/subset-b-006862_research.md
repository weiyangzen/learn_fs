# subset-b-006862 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/router_bridge.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/router_bridge.sh

Purpose: builds a two-host IPv4/IPv6 routed topology where one router-side subnet is represented by an 802.1Q-aware Linux bridge. It validates that a bridge netdevice used as an L3 router interface survives slave remastering and PVID changes.

Important functions are `h1_create`, `h2_create`, `router_create`, `config_remaster`, `config_remove_pvid`, `config_add_pvid`, `config_late_pvid`, `ping_ipv4`, and `ping_ipv6`. The script depends on `lib.sh` for `simple_if_init`, `vrf_prepare`, `__addr_add_del`, ping helpers, and cleanup trapping. Control flow assigns four `NETIFS`, creates host VRFs and routes, creates `br1` with `vlan_filtering 1`, enslaves `$swp1`, assigns L3 addresses to `br1` and `$swp2`, enables forwarding, runs `ALL_TESTS`, and unwinds in reverse.

State is kernel networking state only: VRFs, bridge, addresses, routes, forwarding sysctls, and bridge VLAN table entries. Risks include bridge PVID semantics changing when the default VLAN is removed or restored, stale master relationships after failure, and timing sensitivity around `sleep 2`. Test signals are successful pings before/after remastering, expected ping failures after removing the bridge PVID, and restored connectivity after re-adding or late-adding PVID.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/router_bridge.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/router_bridge_1d.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/router_bridge_1d.sh

Purpose: tests routing through two separate 802.1D bridges built on VLAN uppers of one switch port. Host H1 uses VLANs 100 and 200, while H2 has two routed subnets on a plain interface.

Key functions are `h1_create`, `h2_create`, `router_create`, `config_remaster`, `ping_ipv4`, and `ping_ipv6`. `router_create` creates `$swp1.100` and `$swp1.200`, attaches them to `br1` and `br2`, gives each bridge an L3 address, and configures `$swp2` with two destination-side address pairs. The test harness comes from `lib.sh`; route and VLAN manipulation is done with `ip`, `vlan_create`, `__addr_add_del`, and ping helpers.

Control flow is a straight setup, connectivity check, bridge-slave detach/reattach, connectivity check, and cleanup. State is transient VLAN interfaces, bridges, VRFs, routes, and forwarding. Integration is with the shared forwarding selftest topology through `NUM_NETIFS=4`. Risks are ordering-sensitive cleanup of VLAN uppers and bridge masters, plus remaster races requiring `sleep 2`. Test signals are two IPv4 pings and two IPv6 pings, one per VLAN-backed routed path, before and after remastering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/router_bridge_1d.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/router_bridge_1d_lag.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/router_bridge_1d_lag.sh

Purpose: extends the 802.1D bridge-over-VLAN topology to LACP team devices. Host LAGs carry VLAN 100 and 200 traffic, while router-side LAG2 VLAN uppers feed two bridges and LAG3 VLAN uppers carry the routed destination side.

Important functions include `h1_create`, `h2_create`, `router_create`, `config_remaster_lag2`, `config_deslave_swp*`, `config_enslave_swp*`, `config_wait`, and dual-stack ping tests. It requires `REQUIRE_TEAMD=yes`, eight netifs, `team_create lag* lacp`, `vlan_create`, bridge setup, VRF helpers, and forwarding helpers from `lib.sh`.

The control flow creates four LAGs, VLAN uppers, two bridges, static routes, and L3 addresses, then repeatedly removes and restores individual physical slaves from LAG2/LAG3 and remasters LAG2 bridge VLAN uppers. State is LACP team membership, VLAN upper devices, bridge masters, routes, addresses, and forwarding sysctls. No persistent files are written. Risks are high: teamd availability, LACP convergence timing, slave reattach ordering, and cleanup if a slave is left down or unmastered. Test signals are repeated IPv4/IPv6 pings over VLAN 100 and VLAN 200 after each LAG membership mutation, with `setup_wait_dev lag2/lag3` used as the convergence gate.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/router_bridge_1d_lag.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/router_bridge_lag.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/router_bridge_lag.sh

Purpose: validates routing when both hosts and router ports are LACP team devices, with LAG2 enslaved to an 802.1Q-aware bridge and LAG3 operating as a routed interface. It exercises bridge/LAG remastering and physical slave churn.

Key APIs are shell functions `team_create`, `team_destroy`, `simple_if_init`, `__addr_add_del`, `forwarding_enable`, and local mutators `config_deslave`, `config_enslave`, `config_remaster_lag2`, and `config_remaster_lag3`. `ALL_TESTS` can be overridden, and `EXTRA_SOURCE` can inject additional behavior, making this script a reusable base for variants.

Control flow creates host LAG1/LAG4 with VRFs, router LAG2/LAG3, bridge `br1`, static routes, and addresses. The test sequence pings, detaches and reattaches each LAG slave, remasters LAG2 out of and back into the bridge, and temporarily moves LAG3 into the bridge. State is entirely kernel/teamd networking state. Risks include teamd dependency, convergence timing, overridden test lists, and leaving physical ports with changed MAC/master state after failures. Test signals are dual-stack reachability through `lag1` after each mutation and explicit `setup_wait_dev` for LAG readiness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/router_bridge_lag.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/router_bridge_pvid_vlan_upper.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/router_bridge_pvid_vlan_upper.sh

Purpose: checks that creating and deleting a VLAN upper on a bridge for the bridge PVID VLAN does not disturb L3 routing through the bridge itself. H1 is on VLAN 10, `br1` is an 802.1Q bridge with VLAN 10 as PVID, and H2 is routed through `$swp2`.

Important functions are `h1_create`, `h2_create`, `router_create`, `shuffle_pvid`, and ping tests. The script uses `vlan_create`, `bridge vlan add`, `__addr_add_del`, VRF helpers, and forwarding helpers from `lib.sh`.

Control flow creates H1 VLAN 10, creates `br1` with `vlan_filtering 1 vlan_default_pvid 0`, assigns L3 addresses directly to `br1`, marks VLAN 10 `pvid untagged self`, then runs connectivity, creates `br1.10` with an arbitrary address, deletes it, and checks connectivity again. State is temporary bridge/VLAN/address/route state. Risks include bridge self-PVID behavior changing when a VLAN upper is present and address ownership ambiguity between `br1` and `br1.10`. Test signals are IPv4 and IPv6 pings before and after `shuffle_pvid`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/router_bridge_pvid_vlan_upper.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/router_bridge_vlan.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/router_bridge_vlan.sh

Purpose: validates an 802.1Q bridge used as an L3 router interface for multiple VLANs, with VLAN 555 initially the bridge PVID and VLAN 777 later selected as the PVID. It confirms that changing bridge self VLAN membership affects expected routed connectivity.

Key functions are `config_555`, `config_777`, `vlan`, `ping_ipv4`, `ping_ipv6`, `ping_ipv4_fails`, `ping_ipv6_fails`, and VLAN-specific ping helpers for VLAN 777. `router_create` disables the default PVID, adds bridge self VLAN 555 as `pvid untagged`, adds switch-port VLANs 555/777, and assigns two L3 address pairs to `br1`; `$swp2` carries two routed destination subnets.

Control flow sets up host VLAN uppers, confirms VLAN 555 connectivity, verifies non-PVID self VLAN add/delete operations, switches the bridge PVID to 777, expects VLAN 555 failures and VLAN 777 success, then restores 555. State is Linux bridge VLAN filtering, VLAN uppers, routes, and forwarding. Risks include self VLAN/PVID edge semantics and tests relying on immediate bridge VLAN table propagation. Test signals include positive and negative ping helpers plus `check_err` validation that non-PVID bridge self VLAN add/delete succeeds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/router_bridge_vlan.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/router_bridge_vlan_upper.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/router_bridge_vlan_upper.sh

Purpose: tests routing through VLAN upper devices on a VLAN-aware bridge. H1 uses VLAN 555, H2 uses VLAN 777, and the router presents `br1.555` and `br1.777` as L3 interfaces over the same bridge.

Important functions are `router_create`, `respin_config`, `ping_ipv4`, and `ping_ipv6`. The bridge is created with `vlan_filtering 1`, both switch ports are enslaved, bridge self and port VLANs are added, then `vlan_create br1 555` and `vlan_create br1 777` create routed upper devices. The script depends on `lib.sh` for VRF, VLAN, address, and ping helpers.

Control flow creates hosts and bridge VLAN uppers, enables forwarding, verifies dual-stack reachability, detaches both bridge slave ports, waits, reattaches them, reapplies VLAN membership, and verifies reachability again. State is bridge membership, bridge VLAN table, VLAN upper devices, routes, addresses, and forwarding sysctls. Risks include VLAN membership being lost across remastering, bridge MAC/address interactions, and cleanup order between VLAN uppers and bridge deletion. Test signals are successful pings from H1 to H2 over IPv4 and IPv6 before and after `respin_config`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/router_bridge_vlan_upper.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/router_bridge_vlan_upper_pvid.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/router_bridge_vlan_upper_pvid.sh

Purpose: validates interaction between bridge self PVID settings and a VLAN upper (`br1.10`) used as the routed interface. H1 sends tagged VLAN 10 traffic, while the router side uses a bridge VLAN upper rather than an address directly on `br1`.

Key functions are `pvid_set_unset`, `pvid_set_move`, `shuffle_vlan`, and dual-stack pings. `router_create` uses `vlan_filtering 1 vlan_default_pvid 0`, adds VLAN 10 to both bridge self and `$swp1`, creates `br1.10`, and assigns router addresses there. `pvid_set_unset` toggles VLAN 10 self PVID, while `pvid_set_move` moves PVID from VLAN 10 to VLAN 20.

Control flow checks connectivity, toggles self PVID, checks again, moves PVID, and checks again. State is transient kernel bridge VLAN/PVID state plus VLAN upper and route state. Risks include accidental PVID changes altering which device receives L3 traffic, lack of assertions inside `shuffle_vlan`, and timing sensitivity from one-second sleeps. Test signals are IPv4/IPv6 pings after each PVID mutation; success means the VLAN upper remains the effective routed endpoint.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/router_bridge_vlan_upper_pvid.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/router_broadcast.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/router_broadcast.sh

Purpose: tests directed broadcast forwarding behavior across a three-interface IPv4 router. It verifies local broadcast replies, forwarded directed broadcasts, and drops for same-subnet or all-hosts broadcast cases under `bc_forwarding`.

Important functions are `bc_forwarding_disable`, `bc_forwarding_enable`, `bc_forwarding_restore`, `ping_test_from`, and `ping_ipv4`. Host setup creates three VRFs and static routes through router interfaces `$rp1`, `$rp2`, and `$rp3`. `ping_test_from` runs `$PING -b` inside the source VRF, greps for the expected reply source, and uses `check_err_fail` for expected success/failure.

Control flow disables `icmp_echo_ignore_broadcasts`, tests with `net.ipv4.conf.*.bc_forwarding=0`, restores, enables forwarding on `all`, `$rp1`, and `$rp2`, and retests expected forwarding and dropping. State is kernel VRF/interface/address/route state and sysctl state saved through `sysctl_set`/`sysctl_restore`. Risks include sysctl leakage on early failure, broadcast ping behavior varying by kernel configuration, and grep-based reply-source assertions. Test signals are many `log_test` entries documenting expected responder: router itself when forwarding is disabled, remote host when enabled, and no reply for same-interface directed broadcasts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/router_broadcast.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/router_mpath_nh.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/router_mpath_nh.sh

Purpose: tests regular nexthop-object ECMP and weighted multipath routing for IPv4 and IPv6, including blackhole nexthops and nexthop hardware/software statistics.

Important functions are `routing_nh_obj`, `multipath4_test`, `multipath6_test`, `multipath_test`, `multipath16_test`, `ping_ipv4_blackhole`, `ping_ipv6_blackhole`, and `nh_stats_test_v4/v6`. `routing_nh_obj` creates nexthops 101/102 and 104/105 on R1, group IDs 103/106, and reciprocal R2 groups 203/206. It sources `router_mpath_nh_lib.sh` for stats and feature probes.

Control flow builds four VRFs (H1, H2, R1, R2), configures link-local and IPv4 nexthop gateways, enables forwarding, creates nexthop objects, and runs pings, weighted traffic distribution tests, blackhole replacement tests, and stats tests. State is VRFs, routes, `ip nexthop` objects, sysctls `fib_multipath_hash_policy`, and link counters. Risks include dependency on `ip nexthop`, mausezahn flow generation, timing in packet counters, and feature variance for 16-bit weights or hardware stats. Test signals are ping success, ping failure with blackhole nhids, `multipath_eval` ratios, and link-vs-nexthop counter agreement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/router_mpath_nh.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/router_mpath_nh_lib.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/router_mpath_nh_lib.sh

Purpose: shared helper library for nexthop multipath tests. It validates nexthop group statistics, dispatches software and hardware-stat paths, and probes 16-bit nexthop weight support.

Important functions are `nh_stats_do_test`, `nh_stats_test_dispatch_swhw`, `nh_stats_test_dispatch`, `__nh_stats_test_v4`, `__nh_stats_test_v6`, and `check_nhgw16`. `nh_stats_do_test` generates UDP flows across destination-port ranges, snapshots link TX counters and nexthop group counters, and requires the delta discrepancy to stay below 10 packets. `nh_stats_test_dispatch` checks `ip nexthop help` for `hw_stats`, enables hardware stats with JSON inspection via `jq`, and calls software plus hardware stat checks, with `xfail_on_veth` for unsupported veth hardware paths.

State is not persistent but it mutates nexthop group configuration (`ip nexthop replace ... hw_stats on/off type $nhgtype`) and sysctls in callers. Dependencies include `iproute2` nexthop JSON output, `jq`, `MZ`, link stat helpers, `absval`, and busy test harness logging. Risks include JSON schema drift, hardware stats unavailability, and counter races. Test signals are `log_test "NH stats test ..."` and explicit `check_err` on counter mismatches or failed hardware-stat enablement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/router_mpath_nh_lib.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/router_mpath_nh_res.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/router_mpath_nh_res.sh

Purpose: tests resilient nexthop groups, especially bucket preservation and weight replacement behavior under different idle timers. It mirrors `router_mpath_nh.sh` topology but creates nexthop groups with `type resilient buckets 512`.

Key functions are `routing_nh_obj`, `multipath4_test`, `multipath6_l4_test`, `multipath_test`, `multipath16_test`, and inherited `nh_stats_test_v4/v6`. `multipath_test` runs three phases: idle timer 0 where weight changes should apply immediately, idle timer 120 where active buckets should preserve the original 1:1 distribution, and idle timer 5 where sleeps allow buckets to idle and weight changes to apply.

Control flow creates H1/H2/R1/R2 VRFs, link-local and IPv4 gateway addresses, forwarding, resilient nexthop objects, then traffic distribution and stats tests. State is `ip nexthop` resilient groups, routes, sysctls, link counters, and VRFs. Risks include long sleeps, kernel/iproute2 feature differences, resilient bucket aging timing, and mausezahn traffic not activating enough buckets on slow systems. Test signals are successful pings, `multipath_eval` ratios matching expected immediate or preserved distributions, 16-bit weight feature probe, and inherited software/hardware nexthop stat validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/router_mpath_nh_res.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/router_mpath_seed.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/router_mpath_seed.sh

Purpose: validates `net.ipv4.fib_multipath_hash_seed` behavior and its effect on nexthop selection for IPv4 and IPv6 nexthop groups. It uses ten nexthops per group and hardware stats to detect the active member.

Important functions are `nexthops_create`, `test_mpath_seed_get`, `nh_stats_snapshot`, `get_active_nh`, `probe_nh`, `probe_seed`, `test_mpath_seed`, and `test_mpath_seed_stability`. `nexthops_create` creates IDs 1001-1010 and 2001-2010, group IDs 1000/2000 with `hw_stats on`, and routes through those groups.

Control flow saves the seed sysctl, creates two-router topology, creates nexthops, checks ping reachability, repeatedly writes/reads seed values, probes active nexthop distribution across 100 seed values, and confirms repeated seeds select stable nexthops. State is sysctl, nexthop objects, routes, JSON nexthop stat counters, and VRFs. Risks include hardware stats support, `jq` processing, seed affects both IPv4 and IPv6 expectations, and stats thresholds hiding low packet counts. Test signals are all ten nexthops being hit across seed sweeps, stable selection for fixed seeds, and successful seed set/get checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/router_mpath_seed.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/router_multicast.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/router_multicast.sh

Purpose: tests IPv4/IPv6 multicast routing, reverse path forwarding enforcement, and unresolved multicast route queueing with userspace multicast daemon integration.

Important functions are `create_mcast_sg`, `delete_mcast_sg`, `mcast_v4`, `mcast_v6`, `rpf_v4`, `rpf_v6`, `unres_v4`, and `unres_v6`. Setup calls `adf_mcd_start`, creates three host VRFs with routes, router interfaces `$rp1-$rp3`, ingress qdiscs on hosts and `$rp3`, and enables forwarding. `mc_cli` adds/removes `(S,G)` or `(*,G)` multicast routes.

Control flow installs tc flower counters/drops, emits multicast packets with proper L2 multicast destinations via `$MZ`, checks receiver counters, deletes routes and verifies no further delivery, tests wrong-ingress RPF drops/traps, and tests unresolved queue notifications that cause userspace route installation. State is multicast daemon state, kernel multicast forwarding cache, VRFs, routes, tc filters, and forwarding. Risks include daemon startup, route convergence, skip/offload behavior, and timing around unresolved queue processing. Test signals are exact tc packet counts on H2/H3 and `$rp3`, plus `log_test` entries for multicast delivery, RPF, and unresolved queue behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/router_multicast.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/router_multipath.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/router_multipath.sh

Purpose: baseline ECMP/weighted multipath routing test using classic route nexthop syntax instead of nexthop objects. It covers IPv4 and IPv6 distribution over two router-to-router links.

Important functions are `router1_create`, `router2_create`, `multipath4_test`, `multipath6_test`, and `multipath_test`. R1 and R2 VRFs each install routes with two `nexthop via ... dev ...` clauses. Tests replace those routes with weighted nexthops, generate UDP flows through `$MZ`, compare `$rp12` and `$rp13` TX packet deltas, and call `multipath_eval`.

Control flow creates H1/H2/R1/R2 VRFs, assigns IPv4 and IPv6 addresses including link-local IPv6 nexthop networks, enables forwarding, runs pings, and validates ECMP and two weighted ratios for both address families. State is routes, VRFs, addresses, sysctls `fib_multipath_hash_policy`, and link counters. Risks include enough flow entropy, mausezahn availability, counter timing, and hash-policy restoration. Test signals are ping reachability plus packet-count ratios for 1:1, 2:1, and 11:45 distributions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/router_multipath.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/router_nh.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/router_nh.sh

Purpose: sanity test for simple `ip nexthop` objects used by both IPv4 and IPv6 routes. It creates AF_INET6 nexthop objects bound to router ports and uses them for connected network routes.

Important functions are `router_create`, `routing_nh_obj`, `ping_ipv4`, and `ping_ipv6`. The router has two interfaces with clsact on `$rp2`; `routing_nh_obj` creates nexthop IDs 101 and 102 as IPv6-family device nexthops, then replaces routes for both IPv4 and IPv6 prefixes with `nhid` references.

Control flow creates H1/H2 VRFs and static host routes through router addresses, creates router interfaces and addresses, enables forwarding, installs nexthop objects, and runs dual-stack pings. State is kernel nexthop table, routes, clsact qdisc, VRFs, and forwarding. Risks include kernels without nexthop object support, AF_INET6 nexthop behavior for IPv4 route references, and cleanup not explicitly deleting nexthop IDs in this script. Test signals are only successful IPv4 and IPv6 pings through the `nhid` routes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/router_nh.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/router_vid_1.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/router_vid_1.sh

Purpose: validates routing over VLAN ID 1 on host and router interfaces. VLAN 1 can have special bridge/default-PVID associations, so this script exercises plain routed VLAN uppers with ID 1.

Key functions are `h1_create`, `h2_create`, `router_create`, `ping_ipv4`, and `ping_ipv6`. Hosts create VRFs manually and use `vlan_create $h1 1 vrf-h1` and `vlan_create $h2 1 vrf-h2`; router ports `$rp1` and `$rp2` each create `$rp*.1` VLAN devices with IPv4 and IPv6 addresses.

Control flow creates host VLAN uppers in VRFs, adds routes via router VLAN addresses, creates router VLAN uppers and addresses, enables forwarding, then runs pings. State is VLAN ID 1 netdevices, VRFs, routes, and forwarding sysctls. Risks include VLAN 1 treatment differing from other VLAN IDs, route deletion requiring matching nexthop parameters, and cleanup order if VLAN devices fail to create. Test signals are IPv4 ping from `$h1.1` to H2 and IPv6 ping from `$h1.1` to H2.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/router_vid_1.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/sch_ets.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/sch_ets.sh

Purpose: veth/slowpath driver for the shared ETS qdisc test core. It configures a TBF bottleneck so the ETS scheduler on `$swp2` must arbitrate over competing VLAN-prioritized streams.

The script sources `sch_ets_core.sh`, sets `lib_dir=.`, defines `ALL_TESTS`, implements `switch_create`, and implements the `collect_stats` callback required by `sch_ets_tests.sh`. `switch_create` calls `ets_switch_create`, then adds `tc qdisc add dev $swp2 root handle 1: tbf rate 1Gbit burst 1Mbit latency 100ms`, sets `PARENT="parent 1:"`, and defers TBF cleanup.

Control flow is delegated to `ets_run` from the core. State is qdisc hierarchy on `$swp2`, bridge/VLAN topology from the core, traffic generators started by the test library, and deferred cleanup scopes. Integration is intentionally callback-based so driver-specific offload variants can reuse the same tests. Risks are bottleneck calibration, timing on slow systems, and stats collection depending on qdisc class byte counters. Test signals come from `ping_ipv4`, priomap mode, classifier mode, strict, mixed, DWRR, and plug tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/sch_ets.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/sch_ets_core.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/sch_ets_core.sh

Purpose: common topology and qdisc-control layer for ETS scheduler tests. It builds three VLAN streams, bridge forwarding between `$swp1` and `$swp2`, and provides callbacks used by `sch_ets_tests.sh`.

Important functions are `sip`, `dip`, `ets_start_traffic`, `priomap_mode`, `classifier_mode`, `ets_change_qdisc_priomap`, `ets_change_qdisc_classifier`, `ets_delete_qdisc`, `h1_create`, `h2_create`, `ets_switch_create`, `setup_prepare`, `ping_ipv4`, and `ets_run`. It sources `lib.sh` and `sch_ets_tests.sh`, sets `PARENT` and `QDISC_DEV`, and uses `defer` heavily for cleanup.

Control flow creates VLANs 10-12 on H1/H2 and switch ports, maps egress/ingress 802.1p priorities, creates one bridge per VLAN, then test modes install ETS either with priomap or with `basic` classifier filters mapping meta priorities to ETS classes. State is VLAN interfaces, bridge devices, qdisc/classifier state, MTU changes, and background traffic processes. Risks include deferred cleanup dependency, qdisc mode global `ETS_CHANGE_QDISC`, and needing overcommitment from the driver. Test signals are ping success per VLAN and scheduler ratio assertions supplied by `sch_ets_tests.sh`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/sch_ets_core.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/sch_ets_tests.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/sch_ets_tests.sh

Purpose: reusable assertion library for ETS qdisc behavior. It interprets ETS band configuration, starts stream traffic, samples per-band stats, and checks strict-priority and DWRR scheduling ratios.

Important functions include `qdisc_describe`, `strict_eval`, `notraf_eval`, `__ets_dwrr_test`, `ets_qdisc_setup`, `ets_set_*`, `ets_change_quantum`, `ets_test_strict`, `ets_test_mixed`, `ets_test_dwrr`, and `ets_test_plug`. It expects callbacks/global variables from a driver: `put`, `collect_stats`, `ets_start_traffic`, and `ets_change_qdisc`. The `WS` array models each band, with zero meaning strict and nonzero values meaning DWRR quantum.

Control flow for a test sets qdisc shape, starts selected traffic streams in a defer scope, sleeps, samples counters twice, computes deltas/total, and checks that strict traffic dominates, lower strict bands are starved, or DWRR ratios match configured quanta through `multipath_eval`. State is the shell `WS` array, qdisc configuration, and background traffic. Risks include timing sensitivity, `bc` availability, low traffic counts, and strict thresholds of >95% or <5%. Test signals are `log_test` for band ratios and failures from `check_err`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/sch_ets_tests.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/sch_red.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/sch_red.sh

Purpose: tests RED and ECN qdisc behavior under a controlled bottleneck. It verifies marking, early drop, nodrop mode, and qevents that mirror marked or dropped packets.

Key functions are `get_qdisc_backlog`, `get_nmarked`, `get_qdisc_npackets`, `get_nmirrored`, `send_packets`, `build_backlog`, `check_marking`, `check_mirroring`, `do_ecn_test`, `do_ecn_nodrop_test`, `do_red_test`, `do_red_qevent_test`, `do_ecn_qevent_test`, and `install_qdisc`. Setup creates a bridge with three switch ports, 10 Mbit TBF on H1 and `$swp3`, jumbo MTUs, and a dummy `_drop_test` mirror target.

Control flow starts steady traffic from H1, injects additional traffic from H2 to create backlog on a RED child qdisc under TBF, then samples RED counters and mirror counters. State is qdisc hierarchy, dummy link stats, bridge topology, traffic processes, and MTUs. Risks include rate/backlog calibration, slow system xfails, reliance on qdisc JSON/stat fields, and process cleanup. Test signals are backlog construction success/failure, marking percentage thresholds, early-drop behavior, and mirror counter deltas for qevents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/sch_red.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/sch_tbf_core.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/sch_tbf_core.sh

Purpose: shared topology and measurement code for TBF shaper tests. It builds two VLAN streams through bridge VLANs and measures received bytes at H2 to validate configured shaping rates.

Important functions are `ipaddr`, `host_create`, `h1_create`, `h2_create`, `switch_create`, `setup_prepare`, `ping_ipv4`, `tbf_get_counter`, `__tbf_test`, and `do_tbf_test`. H2 installs clsact and flower filters for VLAN IDs 10 and 11 so per-stream ingress byte counters can be sampled. The switch creates `br10` and `br11`, VLAN uppers on `$swp1/$swp2`, and priority mappings.

Control flow sets up hosts, VLANs, qdisc counters, and bridges; driver scripts install actual TBF/qdisc hierarchies; `do_tbf_test` starts traffic, waits for burst drain, computes rate over 10 seconds, and requires measured rate within +/-5%. State is qdisc state supplied by drivers, VLAN/bridge topology, counters, MTUs, and background traffic. Risks include rate measurement noise, slow system xfails, and needing sufficient traffic saturation. Test signals are ping reachability and `log_test "TC ... TBF rate ..."` with failure details from `check_err`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/sch_tbf_core.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/sch_tbf_ets.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/sch_tbf_ets.sh

Purpose: thin driver selecting ETS as the parent qdisc for shared TBF-under-class tests. It sets `QDISC="ets strict"` and sources `sch_tbf_etsprio.sh`.

There are no local functions. All setup, traffic generation, qdisc installation, and assertions are inherited from `sch_tbf_core.sh` and `sch_tbf_etsprio.sh`. The important integration contract is the `QDISC` shell variable: `sch_tbf_etsprio.sh` expands it into `tc qdisc ... $QDISC 3 priomap 2 1 0`, producing an ETS qdisc with strict bands.

Control flow is entirely delegated to the sourced script, which eventually runs `setup_prepare`, `setup_wait`, and `tests_run`. State and cleanup are also delegated. Risks are that a change in the shared script could break this wrapper silently, and ETS syntax support is required in `tc`/kernel. Test signals are inherited: ping, per-class TBF rates for VLAN 10 and 11, and root-TBF-under-ETS behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/sch_tbf_ets.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/sch_tbf_etsprio.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/sch_tbf_etsprio.sh

Purpose: shared driver for testing TBF beneath classful ETS or PRIO qdiscs, and classful qdiscs beneath a root TBF. It is parameterized by `QDISC` from wrappers.

Important functions are `tbf_test_one`, `tbf_test`, and `tbf_root_test`. It sources `sch_tbf_core.sh`, derives `QDISC_TYPE`, installs class-level TBF qdiscs at `10:3` and `10:2` for 400/800 Mbit measurements, and tests a root TBF with child classful qdisc and `bfifo` leaves.

Control flow starts with inherited topology setup, runs ping, installs a root ETS/PRIO qdisc with three bands, measures per-class TBF rates, then replaces root with a 400 Mbit TBF and installs ETS/PRIO below it so both VLAN streams should be capped at 400 Mbit. State is qdisc hierarchy and inherited VLAN/bridge/traffic state. Risks include qdisc syntax differences between ETS and PRIO, class ID mapping (`10:3` for VLAN 10 and `10:2` for VLAN 11), and rate tolerance on slow environments. Test signals are inherited `do_tbf_test` rate checks and log names identifying `root-$QDISC_TYPE-tbf` and `root-tbf-$QDISC_TYPE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/sch_tbf_etsprio.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/sch_tbf_prio.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/sch_tbf_prio.sh

Purpose: thin wrapper selecting PRIO as the classful qdisc for the shared TBF class tests. It sets `QDISC="prio bands"` and sources `sch_tbf_etsprio.sh`.

The file has no local functions or cleanup. Its only API surface is the `QDISC` variable, which causes the shared script to create a `prio bands 3 priomap 2 1 0` qdisc. All topology, qdisc layering, traffic generation, and assertions come from `sch_tbf_core.sh` and `sch_tbf_etsprio.sh`.

Control flow is delegated at source time to the shared script, which handles optional `sch_tbf_pre_hook`, setup, wait, test execution, and exit status. State is inherited qdisc/bridge/VLAN state. Risks are wrapper fragility if shared scripts assume ETS-only behavior, class ID mapping mismatches, and kernel/tc support for PRIO class hierarchy. Test signals are ping success, 400/800 Mbit per-band TBF rates under PRIO, and 400 Mbit root TBF behavior for both streams.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/sch_tbf_prio.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/sch_tbf_root.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/sch_tbf_root.sh

Purpose: tests a standalone root TBF qdisc on `$swp2` using the shared TBF topology and measurement helpers. It verifies a single 400 Mbit shaping rate.

Important functions are `tbf_test_one` and `tbf_test`. The script sources `sch_tbf_core.sh`, optionally calls `sch_tbf_pre_hook`, installs `tc qdisc replace dev $swp2 root handle 108: tbf rate 400Mbit burst 128K limit 1M`, defers cleanup, and calls `do_tbf_test 10 400`.

Control flow is inherited setup, wait, ping, `tbf_test`, cleanup. State is the root TBF qdisc plus inherited VLAN/bridge topology, counters, traffic processes, and MTUs. Risks include rate measurement variance, insufficient traffic saturation, and optional pre-hook altering environment. Test signals are successful ping over VLANs and a measured VLAN 10 ingress byte rate within +/-5% of 400 Mbit, logged as `TC 0: TBF rate 400Mbit`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/sch_tbf_root.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/skbedit_priority.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/skbedit_priority.sh

Purpose: verifies that `tc action skbedit priority` on ingress or egress changes skb priority before PRIO qdisc classification on `$swp2`.

Important functions are `switch_create`, `test_skbedit_priority_one`, `test_ingress`, and `test_egress`. Setup builds a VLAN-aware bridge, attaches `$swp1/$swp2`, adds clsact to both switch ports, and installs `prio bands 8 priomap 7 6 5 4 3 2 1 0` on `$swp2`. `test_skbedit_priority_one` adds a flower rule at a supplied locus, sends ten UDP packets, waits for the expected PRIO class packet counter, and checks the tc rule counter.

Control flow runs ping, then loops priority 0-7 for ingress on `$swp1` and egress on `$swp2`, expecting class `10:(8-prio)`. State is qdiscs, tc filters, bridge membership, and counters. Risks include priority-to-band mapping assumptions, timing via `HIT_TIMEOUT`, and needing clean filter deletion per iteration. Test signals are class packet count increases and skbedit rule hit counters for every priority/locus combination.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/skbedit_priority.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/tc_actions.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/tc_actions.sh

Purpose: broad tc action coverage for flower/matchall classifiers, including `gact`, `mirred`, `trap`, connection tracking/NAT with egress-to-ingress redirect, and VLAN push chains. It runs once in software (`skip_hw`) and again in hardware-offload mode (`skip_sw`) when available.

Important functions are `mirred_egress_test`, `gact_drop_and_ok_test`, `gact_trap_test`, `mirred_egress_to_ingress_test`, `mirred_egress_to_ingress_tcp_test`, `ingress_2nd_vlan_push`, and `egress_2nd_vlan_push`. It requires `ncat`, sources `tc_common.sh`, and manipulates MAC addresses on switch ports so redirected frames are accepted by hosts.

Control flow creates two host VRFs and two switch-facing simple interfaces with clsact, installs filters, generates packets with `$MZ` or `ncat`, checks counters, deletes filters, then repeats after `tc_offload_check`. State is tc filters/actions, temporary sparse files for TCP test, conntrack NAT state, qdiscs, and modified port MACs. Risks include offload support variance, temp-file cleanup, NAT/ct module availability, and exact counter timing. Test signals are tc rule counters, `cmp` of TCP payload, expected drop/pass behavior, and double-VLAN chain matches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/tc_actions.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/tc_chains.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/tc_chains.sh

Purpose: tests tc chain behavior for flower filters: unreachable chains, `goto chain`, chain create/show/delete JSON output, and template enforcement. It runs in software and optionally offload mode.

Important functions are `unreachable_chain_test`, `gact_goto_chain_test`, `create_destroy_chain`, and `template_filter_fits`. Setup creates two hosts, clsact on H2, captures MAC addresses, and checks chain support with `check_tc_chain_support`. `create_destroy_chain` uses `tc -j chain` plus `jq` to verify chain IDs.

Control flow adds filters in non-default chains, sends one packet with `$MZ`, checks whether counters did or did not increment, validates chain lifecycle commands, then tests that filters must match per-chain templates. State is tc chains/templates/filters and host VRFs. Risks include iproute2 JSON differences, template cleanup when insertions intentionally fail, and offload behavior under `skip_sw`. Test signals are exact counter expectations for default vs chain 1 filters, `jq` selection success, expected failures for template-mismatched filters, and repeated execution after `tc_offload_check`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/tc_chains.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/tc_common.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/tc_common.sh

Purpose: small shared helper library for tc selftests. It sets `CHECK_TC=yes`, defines a configurable `TC_HIT_TIMEOUT`, and provides busywait wrappers around tc rule packet counters.

The exported functions are `tc_check_packets`, `tc_check_at_least_x_packets`, and `tc_check_packets_hitting`. Each accepts a tc location string such as `dev $h2 ingress` or `block 22`, a rule handle, and optionally a target count. They call `busywait "$TC_HIT_TIMEOUT" until_counter_is ... tc_rule_handle_stats_get "$id" "$handle"`.

Control flow is just helper invocation by other scripts. State is not mutated except through the implied read of tc statistics; the timeout can be overridden by environment or config before sourcing. Dependencies are `lib.sh` functions `busywait`, `until_counter_is`, and `tc_rule_handle_stats_get`, plus a working `tc` command because `CHECK_TC` signals the harness to require it. Risks include equality checks being brittle when extra packets arrive and timeout too short for slow/offloaded hardware paths. Test signals are the helper return codes used by caller `check_err`/`check_fail`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/tc_common.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/tc_flower.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/tc_flower.sh

Purpose: comprehensive flower classifier match test for Ethernet, IPv4, VLAN PCP/VID, TOS/TTL/fragment flags, ingress device, MPLS fields and label-stack entries, and ERSPAN options. It runs with `skip_hw` and optionally `skip_sw`.

Important functions include `match_dst_mac_test`, `match_src_mac_test`, `match_dst_ip_test`, `match_src_ip_test`, `match_ip_flags_test`, `match_pcp_test`, `match_vlan_test`, `match_ip_tos_test`, `match_ip_ttl_test`, `match_indev_test`, `mpls_lse`, `match_mpls_*`, and `match_erspan_opts_test`. Setup creates H1/H2 addresses, clsact on H2, and caches MACs.

Control flow adds pairs or sets of flower filters, sends crafted packets with `$MZ`, checks counters for correct and incorrect filters, removes filters, and repeats in offload mode when supported. MPLS tests manually construct LSE bytes because mausezahn cannot build MPLS in L2 mode; ERSPAN tests create tunnel devices and match decap metadata. State is tc filters, VLAN/tunnel devices, clsact qdisc, and host VRFs. Risks include feature probes, exact packet crafting, offload support, and high counter expectations for the MPLS LSE matrix. Test signals are exact tc packet counters and support-skip helpers for MPLS/ERSPAN.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/tc_flower.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/tc_flower_cfm.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/tc_flower_cfm.sh

Purpose: tests flower classifier support for Connectivity Fault Management (CFM) fields: opcode, MD level, and combined level/opcode matching.

Important functions are `u8_to_hex`, `generate_cfm_hdr`, `match_cfm_opcode`, `match_cfm_level`, and `match_cfm_level_and_opcode`. `generate_cfm_hdr` assembles CFM header bytes from MD level, opcode, flags, and TLV offset. Setup creates two simple interfaces, clsact on H2, and caches MACs.

Control flow installs CFM protocol flower filters with handles, sends raw Ethernet frames using `$MZ` with Ethertype `0x8902` and generated headers, checks exact counters for matching and non-matching filters, and deletes filters. State is only tc filters and qdisc state plus the host interfaces. Dependencies are `tc_common.sh`, `lib.sh`, and `MZ`. Risks include raw packet formatting mistakes, tc/iproute2 support for `protocol cfm` and `flower cfm`, and repeated `pref 1` use relying on handles to distinguish filters. Test signals are exact counter values and `log_test` entries for opcode, level, and combined matches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/tc_flower_cfm.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/tc_flower_l2_miss.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/tc_flower_l2_miss.sh

Purpose: validates flower `l2_miss` matching on bridge egress for unknown/known unicast, registered/unregistered multicast, link-local multicast, and broadcast traffic.

Important functions are `test_l2_miss_unicast`, `test_l2_miss_multicast_common`, IPv4/IPv6 multicast wrappers, `test_l2_miss_multicast`, `test_l2_miss_ll_multicast_common`, and `test_l2_miss_broadcast`. Setup builds a two-port bridge with clsact on `$swp2`. Tests use bridge FDB and MDB entries to transition between miss and non-miss states.

Control flow adds egress flower filters on `$swp2`, sends crafted traffic from H1 with `$MZ`, checks counters, adds/removes FDB or MDB entries, and retests. Multicast setup enables router-port behavior, bridge querier, valid IPv6 link-local source, and waits for MDB forwarding readiness. State is bridge FDB/MDB/multicast settings, tc filters, and host interfaces. Risks include bridge multicast timing, the empty placeholder `test_l2_miss_multicast_common2`, and exact counter assumptions. Test signals are expected counter transitions for l2_miss 1 vs 0 and explicit broadcast non-miss behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/tc_flower_l2_miss.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/tc_flower_port_range.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/tc_flower_port_range.sh

Purpose: tests flower source/destination port range matching for IPv4/IPv6 and UDP/TCP on ingress and egress, plus a drop case for IPv4 UDP.

Important functions are `__test_port_range`, `test_port_range_ipv4_udp`, `test_port_range_ipv4_tcp`, `test_port_range_ipv6_udp`, `test_port_range_ipv6_tcp`, and `test_port_range_ipv4_udp_drop`. Setup creates a two-port bridge with clsact on both switch ports and simple dual-stack hosts.

Control flow installs matching filters for `src_port 100-200` and `dst_port 300-400`, sends packets at min/mid/max and out-of-range values with `$MZ`, and checks counters remain at exactly three for matches. The drop test installs an ingress drop filter for source ports 2000-3000 and checks that only in-range packets hit. State is bridge, clsact qdiscs, and tc filters. Risks include protocol naming (`ipv4`/`ipv6` and `udp`/`tcp`), exact counter checks, and out-of-range traffic still traversing other state. Test signals are tc packet counters for ingress and egress filters and `log_test` per protocol family.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/tc_flower_port_range.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/tc_flower_router.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/tc_flower_router.sh

Purpose: tests flower `indev` matching on router egress, ensuring a filter on the outgoing router port can match the original ingress interface after routing.

Important functions are `h1_create`, `h2_create`, `h3_create`, `router_create`, and `match_indev_egress_test`. The router has three interfaces, clsact on `$rp3`, and forwarding enabled. Hosts have VRFs and routes so H1 and H2 both send routed traffic to H3 through `$rp3`.

Control flow installs two egress filters on `$rp3`: one matching `indev $rp1`, one matching `indev $rp2`, sends traffic from H1 and H2, and checks that only the filter corresponding to the actual ingress router port increments. State is routes, VRFs, clsact, tc filters, and cached MACs. Risks include offload-only execution: after setup the script calls `tc_offload_check` and only runs tests when offload is available, so software-only environments skip behavior. Test signals are tc counters for handles 101/102 under `skip_sw` and a log entry for indev egress matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/tc_flower_router.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/tc_mpls_l2vpn.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/tc_mpls_l2vpn.sh

Purpose: builds a two-node Ethernet-over-MPLS L2VPN using tc actions rather than IP routing. It verifies plain Ethernet traffic can be encapsulated into MPLS, transported, decapsulated, and returned symmetrically.

Important functions are `ler1_create`, `ler2_create`, and `mpls_forward_eth`. Each LER installs ingress qdiscs on edge and MPLS-facing interfaces. Edge ingress uses `matchall`, `action mpls mac_push label ...`, `action vlan push_eth dst_mac ... src_mac ...`, and `mirred egress redirect`. MPLS ingress matches `protocol mpls_uc flower mpls_label ...`, pops outer Ethernet and MPLS (`protocol teb`), and redirects back to the edge.

Control flow creates H1/H2 VRFs, caches MPLS interface MACs, installs LER actions, pings IPv4 and IPv6 between hosts, then optionally repeats after `tc_offload_check` with `skip_sw` although local filters do not use `$tcflags`. State is tc qdiscs/actions and interface up/down state. Risks include MPLS action support, offload mismatch, MAC push/pop correctness, and cleanup if qdisc creation partially fails. Test signals are successful IPv4 and IPv6 pings through the MPLS L2VPN.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/tc_mpls_l2vpn.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/tc_police.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/tc_police.sh

Purpose: tests tc `police` action for bit-rate, shared policer index, mirroring after policing, packet-rate policing, and MTU policing in ingress and egress directions.

Important functions are `police_common_test`, `police_rx_test`, `police_tx_test`, `police_shared_test`, `police_mirror_common_test`, `police_pps_common_test`, `police_mtu_common_test`, and wrappers for rx/tx variants. Setup creates a three-interface router and three hosts, clsact on router `$rp1/$rp2` and destination hosts H2/H3, and forwarding routes from H1 to H2/H3.

Control flow installs police filters at router ingress or egress, sends continuous mausezahn UDP traffic, samples H2/H3 tc counters for 10 seconds, computes rates with +/-10% tolerance, and validates overlimits for MTU policing. Shared policer tests reuse `index 10` across rx and tx filters. State is tc filters/actions, clsact qdiscs, routes, forwarding, background traffic, and counters. Risks include timing/rate noise, process cleanup via `kill_process %%`, offload variation, and policing semantics for `drop/pipe` plus mirror. Test signals are measured bit rates, packet rates, mirror rates, overlimit counts, and expected conform packet counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/tc_police.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/tc_shblocks.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/tc_shblocks.sh

Purpose: tests tc shared blocks (`ingress_block`/`egress_block`) and flower `indev` matching within a shared block across two switch ports.

Important functions are `shared_block_test` and `match_indev_test`. Setup creates two host interfaces and two switch interfaces with the same IP/MAC presentation, attaches clsact to `$swp1` and `$swp2` using `ingress_block 22 egress_block 23`, and normalizes `$swp2` MAC to `$swp1` for traffic symmetry.

Control flow checks shared block support, runs software mode and optionally offload mode. `shared_block_test` adds a filter to block 22 and verifies packets arriving through both ports hit the same counter. `match_indev_test` adds two block filters distinguished by `indev $swp1` vs `$swp2` and checks each packet hits the correct one. State is shared block filters, qdiscs, interface MAC override, and host VRFs. Risks include global block ID collisions, MAC restoration, and offload support. Test signals are exact `tc_check_packets "block 22"` counts and log entries for shared block and indev matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/tc_shblocks.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/tc_taprio.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/tc_taprio.sh

Purpose: offloaded TAPRIO time-aware scheduler test using PTP, ETF/TXTIME, and `isochron` traffic. It checks gate open/closed behavior, max-SDU enforcement, and tolerance of PHC clock jumps.

Important functions are `ptp_setup`, `txtime_setup`, `taprio_replace`, `probe_path_delay`, `run_test`, `run_subtests`, `test_taprio_after_ptp`, `test_max_sdu`, `test_clock_jump_backward`, and `test_clock_jump_backward_forward`. It sources `tsn_lib.sh`, requires `python3`, and uses `tc_offload_check`. Setup builds a VLAN-aware bridge, static FDB, H1 txtime qdiscs, PTP sync, and path-delay calibration from isochron reports processed by Python/numpy.

Control flow calibrates path delay, installs TAPRIO schedules with gates for priorities 6/5/4, sends scheduled packets, counts received packets, computes median delay, and validates expected pass/fail. State is ptp4l/phc2sys processes, TAPRIO/ETF/MQPRIO/clsact qdiscs, temporary isochron data/Python files, bridge VLAN/FDB state, and PHC time. Risks are high: hardware offload, PHC synchronization, external tools, CPU frequency manipulation, timing thresholds, and cleanup of background processes. Test signals are packet reception counts, median-delay bounds, ping after clock jumps, and max-SDU pass/fail.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/tc_taprio.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/tc_tunnel_key.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/tc_tunnel_key.sh

Purpose: tests `tc action tunnel_key ... nofrag` on VXLAN external tunnel egress. It verifies packets smaller than MTU are encapsulated and oversized packets are not fragmented when `nofrag` is set, but do fragment when the flag is cleared.

Important functions are `h1_create`, `switch_create`, and `tunnel_key_nofrag_test`. H1 creates external VXLAN `h1-et`, adds clsact, adjusts MTUs so 930-byte inner packets fit and 931-byte packets exceed the tunnel MTU, and checks iproute2 support for `nofrag`.

Control flow installs flower filters on `$swp1` ingress for UDP encapsulated packets with `ip_flags nofrag`, `firstfrag`, and `nofirstfrag`. It adds a matchall egress filter on `h1-et` with tunnel_key set and `nofrag index 10`, sends packets, checks counters, changes the action to remove `nofrag`, sends again, and validates fragmentation counters. State is tunnel device, qdiscs, tc action index 10, MTUs, forwarding, and modified switch-port MACs. Risks include MTU arithmetic, feature support, double spaces in some counter IDs, and cleanup after action mutation. Test signals are exact tc counters for nofrag vs first/non-first fragments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/tc_tunnel_key.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/tc_vlan_modify.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/tc_vlan_modify.sh

Purpose: verifies `tc action vlan modify id` can translate VLAN IDs at bridge ingress or egress to connect two otherwise separated VLAN endpoints.

Important functions are `switch_create`, `vlan_modify_ingress`, and `vlan_modify_egress`. H1 has base addresses and VLAN 85; H2 has base addresses and VLAN 65. The bridge is VLAN-aware with both VLANs admitted on both switch ports, and clsact on `$swp1/$swp2`.

Control flow first confirms pings from `$h1.85` to `$h2.65` fail for IPv4 and IPv6. In ingress mode it installs filters on each switch-port ingress to rewrite incoming VLAN IDs to the peer VLAN, then expects pings to succeed. In egress mode it rewrites on egress with opposite IDs and expects success. State is bridge VLAN table, VLAN uppers, tc filters, and VRFs. Risks include bridge VLAN membership masking modify failures, filter protocol `all` applying broadly, and cleanup order. Test signals are negative `ping_do`/`ping6_do` before filters and positive checks after VLAN modify filters, logged separately for ingress and egress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/tc_vlan_modify.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/tsn_lib.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/tsn_lib.sh

Purpose: shared TSN helper library for TAPRIO/isochron tests. It manages linuxptp processes, CPU frequency stabilization, isochron send/receive runs, and waiting for TAPRIO admin schedule activation.

Important functions are `phc2sys_start/stop`, `ptp4l_start/stop`, `cpufreq_max/restore`, `isochron_recv_start/stop`, `isochron_do`, `isochron_report_num_received`, and `taprio_wait_for_admin`. It conditionally requires `isochron`, `phc2sys`, `ptp4l`, and `phc_ctl` based on `REQUIRE_ISOCHRON` and `REQUIRE_LINUXPTP`. Dynamic global variable names track per-interface logs and PIDs.

Control flow helpers start realtime-priority daemons with temporary log files, start an isochron receiver, run `isochron send` in L2 or L4 mode with TXTIME and PTP UDS options, stop receiver, and restore CPU frequency. State includes background process PIDs, temp logs, CPU scaling governor/min frequency, generated isochron output files supplied by callers, and external TAPRIO wait script invocation under `tc-testing/scripts`. Risks include dynamic variable indirection, missing cpufreq sysfs, unbound PIDs if startup fails, stale temp logs, and hardcoded stats port 5000. Test signals are successful command exits and received-packet counts from `isochron_report_num_received`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/tsn_lib.sh -->
