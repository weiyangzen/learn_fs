# Research Group subset-b-006860

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/bridge_mdb.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/bridge_mdb.sh

## Purpose
`bridge_mdb.sh` is a Linux networking kselftest for bridge multicast database (MDB) configuration and forwarding behavior. It builds a two-host, two-port VLAN-aware bridge topology with host VLAN devices on VID 10 and VID 20, enables bridge multicast snooping with IGMPv3 and MLDv2, and verifies host entries, port entries, source-specific multicast entries, dumps, flush filters, data-plane forwarding, control-packet learning, and snooping-disable cleanup.

## Important APIs, Functions, and Control Flow
The script is driven by `ALL_TESTS="cfg_test fwd_test ctrl_test disable_test"`, `tests_run`, and `trap cleanup EXIT` from `lib.sh`. Topology setup is in `h1_create`, `h2_create`, `switch_create`, `setup_prepare`, and `cleanup`; it uses `simple_if_init`, `vlan_create`, `vrf_prepare`, `forwarding_enable`, tc `clsact`, and `bridge vlan` commands.

Configuration coverage is split by entry class. `cfg_test_host_common` validates host MDB entries on `port br0` for IPv4, IPv6, and L2 multicast. `cfg_test_port_common` validates basic add/replace/delete, protocol attributes, VLAN omission semantics, port-down behavior, disabled-snooping errors, and invalid VLAN rejection. `__cfg_test_port_ip_star_g` covers `(*,G)` source-list behavior, permanent/temp timers, include/exclude filter modes, protocol replacement, source-list replacement, star-exclude auto-added `(S,G)` entries, invalid group/source cases, and a 31-source limit. `__cfg_test_port_ip_sg` covers explicit `(S,G)` entries. `cfg_test_dump_common` stress-creates two bridge devices with 32 dummy ports and 256 groups each through `bridge -b`. `cfg_test_flush` exercises `bridge mdb flush` with no filters, `port`, `vid`, `permanent`, `nopermanent`, `proto`, and unsupported VXLAN-style filters.

Forwarding tests use tc flower counters. Host-entry tests attach an ingress filter on `br0` and expect local reception only with a matching host MDB. Port-entry tests disable multicast flooding on `$swp2`, then verify that include/exclude source lists determine whether mausezahn traffic reaches `$h2`. `ctrl_igmpv3_is_in_test` and `ctrl_mldv2_is_in_test` send crafted IGMPv3/MLDv2 MODE_IS_INCLUDE reports using helper packet builders, proving temporary entries learn additional sources while permanent entries are immune. `disable_test` toggles `mcast_snooping` off for both 802.1q and 802.1d modes and verifies only temporary multicast entries are flushed.

## State, Dependencies, Integration Points, and Risks
State is kernel-resident: bridge devices, VLAN membership, MDB records, timers, tc filters, VRF routes, multicast snooping flags, and sysctl forwarding state. Cleanup reverses topology and forwarding, but the large dump subtest creates additional bridges/dummy devices and relies on its own cleanup path. External dependencies include `ip`, `bridge`, `tc`, `jq`, mausezahn `$MZ`, `tc_common.sh`, and recent iproute2 MDB `flush` support. Timing-sensitive sections use `sleep 10` around querier startup and snooping re-enable; failures can be caused by slow multicast timer convergence, unsupported bridge JSON fields, or missing packet generators.

## Test Signals
Pass/fail signals come from `check_err`, `check_fail`, `check_err_fail`, tc packet counters, `bridge mdb get/show`, `bridge -d -s mdb` timer text, JSON parsing with `jq`, and the final kselftest `$EXIT_STATUS`. A skip occurs if `bridge mdb help` lacks `flush`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/bridge_mdb.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/bridge_mdb_host.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/bridge_mdb_host.sh

## Purpose
`bridge_mdb_host.sh` is a focused kselftest for host MDB entries, meaning MDB entries whose port is the bridge device itself (`port br0`). It verifies add, display, delete, and default/permanent flag semantics for IPv4, IPv6, and raw L2 multicast host groups.

## Important APIs, Functions, and Control Flow
`ALL_TESTS` contains only `mdb_add_del_test`. `setup_prepare` assigns `$h1` and `$swp1`, prepares VRFs, configures `$h1` with IPv4 and IPv6 addresses, creates `br0` with multicast snooping enabled, enslaves `$swp1`, and brings the bridge and port up. `do_mdb_add_del` is the core helper. It runs `bridge mdb add dev br0 port br0 grp $group $flag`, checks `bridge mdb show dev br0` for the group and expected flag, deletes the entry, and checks that the group disappears. If no flag is supplied it expects `temp`, which is the default for IP multicast host entries. `mdb_add_del_test` calls the helper for a permanent L2 group and temporary IPv4/IPv6 groups.

## State, Dependencies, Integration Points, and Risks
State is limited to one bridge, one bridge slave, one host namespace/VRF endpoint, and the MDB entries under test. The script depends on `lib.sh`, `ip`, `bridge`, grep text output, and kselftest helper functions. It is intentionally narrow and does not test forwarding; it tests userspace/kernel MDB host-entry configuration behavior. The main risk is reliance on textual `bridge mdb show` formatting for flag detection rather than JSON output.

## Test Signals
The signal is a sequence of `check_err` and `check_err_fail` assertions plus `log_test "MDB add/del group ..."`. Any failure to add, observe, delete, or remove an MDB record increments `RET` and contributes to `$EXIT_STATUS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/bridge_mdb_host.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/bridge_mdb_max.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/bridge_mdb_max.sh

## Purpose
`bridge_mdb_max.sh` validates bridge multicast group accounting and `mcast_max_groups` limit enforcement. It runs the same logical checks across 802.1d bridges, VLAN-filtering 802.1q bridges, and VLAN-filtering bridges with `mcast_vlan_snooping 1`, and across both explicit configuration (`bridge mdb`) and packet-driven control paths (IGMPv3/MLDv2 reports).

## Important APIs, Functions, and Control Flow
The top-level tests are `test_8021d`, `test_8021q`, `test_8021qvs`, and `test_mdb_count_warning`. Setup creates two hosts with VLAN subinterfaces, then each top-level test creates and destroys the bridge mode it needs. `switch_create_8021d`, `switch_create_8021q`, and `switch_create_8021qvs` configure snooping, VLANs, fastleave, and per-VLAN MLD/IGMP versions.

Entry creation is abstracted. `cfg4_entries_add/del` and `cfg6_entries_add/del` program MDB include entries with source lists via `bridge mdb`. `ctl4_entries_add/del` and `ctl6_entries_add/del` send IGMPv3/MLDv2 reports and leaves/done packets through mausezahn, then verify the number of created MDB lines. `bridge_port_ngroups_get`, `bridge_port_maxgroups_get`, `bridge_port_vlan_ngroups_get`, and `bridge_port_vlan_maxgroups_get` parse `bridge -j -d link/vlan` output through `jq`. Matching setters use `bridge link set ... mcast_max_groups` and `bridge vlan set ... mcast_max_groups`.

The test matrix is built from reusable suites: `test_ngroups_reporting` checks counters increment and decrement; `test_ngroups_cross_vlan` checks per-VLAN counters are isolated; `test_maxgroups_zero` verifies zero means unlimited; `test_maxgroups_zero_cross_vlan` verifies port and per-VLAN maximums are independent; `test_maxgroups_too_low` checks setting a max below current count rejects further additions without blocking additions after count drops; `test_maxgroups_too_many_entries` checks failed over-limit operations leave counters unchanged; `test_maxgroups_too_many_cross_vlan` combines aggregate port and per-VLAN limits. `test_vlan_attributes` verifies per-VLAN attributes only exist when VLAN snooping is active. `test_toggle_vlan_snooping` checks counters and maximums survive toggling `mcast_vlan_snooping`.

## State, Dependencies, Integration Points, and Risks
State spans bridge MDB entries, per-port and per-VLAN multicast accounting, bridge snooping flags, timer-driven control-packet state, and dmesg. The script uses `lib.sh`, `tc_common.sh`, `bridge`, `ip`, `jq`, mausezahn, multicast packet builder helpers, and kernel support advertised by `bridge link help` for `mcast_max_groups`. It reads `dmesg` to ensure no `br_multicast_port_ngroups_dec` warning appears, so prior warnings in the ring buffer can contaminate results. Control-path tests can partially add entries before hitting a limit, so cleanup explicitly deletes possible committed entries.

## Test Signals
Signals are JSON bridge counter comparisons, explicit return-code checks, error-message matching for `mcast_max_groups`, tc/mausezahn-driven MDB creation counts, and dmesg warning absence. The script skips when iproute2 lacks `mcast_max_groups` support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/bridge_mdb_max.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/bridge_mdb_port_down.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/bridge_mdb_port_down.sh

## Purpose
`bridge_mdb_port_down.sh` verifies permanent MDB entries can be added to a bridge port while that port is administratively down, remain present across link up/down transitions, forward traffic after the port comes up, and stop forwarding after deletion.

## Important APIs, Functions, and Control Flow
`add_del_to_port_down` is the only test. It disables `$swp2`, adds `bridge mdb add dev br0 port "$swp2" grp 239.10.10.10 permanent`, brings the port up, and uses `mcast_packet_test` from `lib.sh` to ensure multicast traffic from `$h1` reaches `$h2`. It then brings `$swp2` down again, confirms `bridge mdb show` still reports a permanent entry, deletes the entry while down, brings the port up, and expects multicast forwarding to fail.

Setup creates two hosts, a bridge with `mcast_snooping 1` and `mcast_querier 1`, enslaves two switch ports, disables multicast flooding on `$swp2`, and sleeps for bridge multicast grace-time behavior before testing.

## State, Dependencies, Integration Points, and Risks
The tested state is a permanent MDB entry on a down bridge slave and the bridge’s forwarding behavior once that slave becomes live. Dependencies include `ip`, `bridge`, `lib.sh`, `mcast_packet_test`, and mausezahn/packet capture support behind that helper. The hard-coded `sleep 10` mitigates bridge startup flooding grace period; reducing it could make the negative forwarding checks flaky.

## Test Signals
Success requires add/delete return codes to pass, `bridge mdb show` to retain the permanent group while the port is down, and `mcast_packet_test` to invert from forwarded after add to not forwarded after delete.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/bridge_mdb_port_down.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/bridge_mld.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/bridge_mld.sh

## Purpose
`bridge_mld.sh` is a packet-driven MLDv2 bridge snooping state-machine test. It feeds fixed MLDv2 report packets into a bridge and validates `(*,G)` source-list state, `(S,G)` forwarding entries, include/exclude transitions, blocked-source behavior, timeout behavior, automatic star-exclude entries, and per-VLAN snooping interaction with STP state.

## Important APIs, Functions, and Control Flow
The script defines fixed hexadecimal packet payloads for MLDv2 MODE_IS_INCLUDE, MODE_IS_EXCLUDE, CHANGE_TO_EXCLUDE, ALLOW_NEW_SOURCES, and BLOCK_OLD_SOURCES reports against group `ff02::cc`. `switch_create` configures `br0` with multicast snooping, a querier, MLDv2, shortened query response/startup intervals, and two bridge ports. `mldv2include_prepare` sends an include report, then checks JSON MDB output for a source-list `(*,G)` entry in include mode and calls `brmcast_check_sg_entries`. `mldv2exclude_prepare` builds from include state to exclude state and validates source states.

Individual tests cover transitions: include plus ALLOW, include plus IS_IN, include plus IS_EX, include to exclude, exclude plus ALLOW, exclude plus IS_IN, exclude plus IS_EX, exclude to exclude, include/exclude plus BLOCK, and exclude timeout back to include. Forwarding checks use `brmcast_check_sg_fwding` for allowed and blocked source sets. `mldv2star_ex_auto_add_test` verifies that a later `(S,G)` learned on another port also creates an `added_by_star_ex` entry for the existing `(*,G)` exclude port. `mldv2per_vlan_snooping_stp_test` enables VLAN filtering and `mcast_vlan_snooping`, changes port or VLAN STP state from disabled/blocking to forwarding, and checks multicast xstats for transmitted MLDv2 queries.

## State, Dependencies, Integration Points, and Risks
State lives in bridge MDB source lists, per-source timers, per-source forwarding/block flags, bridge multicast timers, per-VLAN global multicast settings, STP state, and multicast xstats. Dependencies include `lib.sh`, `jq`, `ip -j stats`, `bridge -j -d -s mdb`, mausezahn, and helper functions such as `brmcast_check_sg_entries`, `brmcast_check_sg_state`, and `brmcast_check_sg_fwding`. Timing is central: tests sleep after report injection and deliberately shorten last-member and membership intervals. Risks include brittle fixed packet payloads, environment-specific multicast timer jitter, and xstats availability differences.

## Test Signals
Signals are JSON MDB predicates over `grp`, `source_list`, `filter_mode`, `src`, `port`, and `flags`, forwarding helper results for allowed/blocked sources, xstats deltas for MLD query transmission, and normal kselftest `RET`/`EXIT_STATUS` aggregation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/bridge_mld.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/bridge_port_isolation.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/bridge_port_isolation.sh

## Purpose
`bridge_port_isolation.sh` verifies Linux bridge port isolation. Two bridge ports are configured as isolated and a third as non-isolated; the script checks unicast reachability and flooding rules.

## Important APIs, Functions, and Control Flow
`switch_create` creates `br0`, enslaves three switch ports, sets `$swp1` and `$swp2` to `type bridge_slave isolated on`, explicitly sets `$swp3` isolation off, and brings bridge and ports up. `ping_ipv4` and `ping_ipv6` expect traffic from host 1 to host 2 to fail because both ingress/egress ports are isolated, while traffic from non-isolated host 3 to host 2 must succeed. `flooding` uses `flood_test_do` to ensure unknown unicast from isolated host 1 is not flooded to isolated host 2, but unknown unicast from non-isolated host 3 is flooded.

## State, Dependencies, Integration Points, and Risks
State is per-port bridge isolation plus bridge FDB/flood behavior. The script depends on `CHECK_TC=yes`, `lib.sh`, ping helpers, and flooding helpers that use tc/mausezahn. The primary risk is false failure when the kernel or iproute2 lacks bridge slave isolation support; `check_err` on the setup commands catches this as a test failure rather than a skip.

## Test Signals
The pass criteria are explicit `check_fail` for disallowed pings, `check_err` for allowed pings, and flood helper results matching the isolated/non-isolated path expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/bridge_port_isolation.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/bridge_sticky_fdb.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/bridge_sticky_fdb.sh

## Purpose
`bridge_sticky_fdb.sh` tests bridge FDB `sticky` behavior. It verifies that a sticky static FDB entry can survive deletion of the static master record in a way that still prevents learning/movement from an incoming frame on another port.

## Important APIs, Functions, and Control Flow
The topology is a simple two-port bridge with hosts directly connected. `sticky` adds `TEST_MAC` on `$swp1` with `bridge fdb add ... master static sticky`, deletes the corresponding static sticky entry for VLAN 1, sends an ARP frame from `$h2` using source MAC `TEST_MAC`, and then queries JSON FDB output for a record on `$swp1`. The expected behavior is that the sticky FDB record remains anchored on `$swp1` despite the frame arriving from `$h2`.

## State, Dependencies, Integration Points, and Risks
State is bridge FDB state, the sticky flag, and one mausezahn-generated ARP packet. Dependencies include `bridge -j fdb`, `jq`, `$MZ`, and `lib.sh`. The test assumes the default VLAN context reported as VLAN 1 for bridge FDB operations. If bridge FDB JSON schema or default VLAN handling changes, the jq predicate can fail despite equivalent behavior.

## Test Signals
The test passes when the FDB add succeeds and `bridge -j fdb show br br0 brport $swp1` contains `TEST_MAC` after a packet with that source was injected from the other host.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/bridge_sticky_fdb.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/bridge_vlan_aware.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/bridge_vlan_aware.sh

## Purpose
`bridge_vlan_aware.sh` exercises baseline bridge behavior with `vlan_filtering 1`: IPv4/IPv6 forwarding, FDB learning, unknown unicast flooding, VLAN deletion effects, externally learned FDB behavior, handling of non-802.1Q TPIDs, 802.1p VID 0 traffic, and dropping untagged/priority-tagged traffic when no PVID exists.

## Important APIs, Functions, and Control Flow
Setup creates a VLAN-aware bridge with ageing time from `LOW_AGEING_TIME` and multicast snooping disabled, then enslaves two ports. `ping_ipv4`, `ping_ipv6`, `learning`, and `flooding` delegate to common `lib.sh` helpers. `vlan_deletion` adds and deletes VID 10 on `$swp1` and confirms default PVID forwarding is unaffected. `extern_learn` adds an `extern_learn` FDB entry, waits longer than bridge ageing time to prove it does not age out, sends a frame from the other host with that MAC, and verifies the external entry roams.

`other_tpid` installs a tc ingress filter on `$h2`, sends an 802.1ad outer tag followed by 802.1Q inner tag through `$h1`, and verifies the bridge treats it as untagged under a bridge configured for 802.1Q protocol. It then removes the PVID and confirms the same traffic no longer forwards. `8021p` and `8021p_do` verify VID 0 priority-tagged traffic is accepted with default PVID 1 and after changing the bridge default PVID to 10. `drop_untagged` removes PVID behavior through several paths and checks both untagged ping and 802.1p reception fail, including after port down/up and re-enslave.

## State, Dependencies, Integration Points, and Risks
State includes bridge VLAN membership, default PVID, FDB attributes, ageing timer, tc filters, promiscuous mode, and NIC VLAN filtering offloads disabled through `ethtool -K`. Dependencies include `CHECK_TC=yes`, `jq`, `tc`, mausezahn, ethtool, and bridge/FDB JSON support. Timing risk exists in `extern_learn`, which sleeps for ageing time plus ten seconds. Offload behavior can affect `other_tpid`, which compensates by matching self addresses and disabling rx VLAN filters.

## Test Signals
Signals come from ping helpers, learning/flood helpers, grep/JQ FDB checks, tc packet counters, and inverted checks for dropped untagged/802.1p traffic when no PVID is present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/bridge_vlan_aware.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/bridge_vlan_mcast.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/bridge_vlan_mcast.sh

## Purpose
`bridge_vlan_mcast.sh` validates per-VLAN multicast snooping controls and statistics on a VLAN-aware bridge. It checks global VLAN multicast option visibility/defaults, per-VLAN snooping enable/disable, querier behavior, IGMP/MLD version selection, timer knobs, router-port behavior, membership expiration, and automatic disablement when VLAN filtering is turned off.

## Important APIs, Functions, and Control Flow
Setup creates VLAN subinterfaces on both hosts, a VLAN-filtering bridge with multicast snooping and querier enabled, installs `clsact` on bridge ports, adds VLANs 10 and 11 to both ports, then enables `mcast_vlan_snooping`. `vlmc_v2join_test` adds an IPv4 multicast `autojoin` address on `$h2.10`, waits, and checks for a VID 10 MDB entry, with an `expect` flag for positive and negative cases. `vlmc_control_test` checks `bridge -j vlan global show` default `mcast_snooping`, disables it on VID 10, and verifies joins no longer create MDB entries.

`vlmc_query_cnt_setup`, `vlmc_query_cnt_xstats`, and `vlmc_check_query` use tc egress filters plus bridge multicast xstats to count tagged IGMP or MLD general queries. The querier/version/startup/query interval tests set per-VLAN global options and validate query counts. Other timer tests validate default and mutable values for last-member, membership, querier, query, and query-response intervals. `vlmc_router_port_test` checks per-port VLAN `mcast_router`, sets one port as router and the other non-router, sends unknown multicast from `br0`, and verifies flooding only to the router port. `vlmc_filtering_test` disables bridge VLAN filtering and expects `mcast_vlan_snooping` to be disabled.

## State, Dependencies, Integration Points, and Risks
State includes per-VLAN global multicast attributes, per-port VLAN router flags, MDB entries with `vid`, host `autojoin` memberships, tc filter counters, bridge xstats, and bridge link info. Dependencies include `lib.sh`, `tc_rule_stats_get`, `jq`, `bridge vlan global`, `ip -j link xstats`, mausezahn, and per-VLAN multicast support in kernel/iproute2. Timer/count tests use sleeps from 1 to 5 seconds and can be sensitive to scheduler latency. Some tests create a temporary `br1` and reparent `$h1`, so cleanup must restore host addressing.

## Test Signals
Pass/fail signals are JSON predicates over `bridge vlan global show`, `bridge -j -d vlan show`, `bridge -j mdb show`, tc filter packet counts, xstats deltas, and link-info checks for `mcast_vlan_snooping`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/bridge_vlan_mcast.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/bridge_vlan_unaware.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/bridge_vlan_unaware.sh

## Purpose
`bridge_vlan_unaware.sh` verifies baseline bridge forwarding with VLAN filtering disabled. It specifically ensures that manipulating bridge VLAN/PVID metadata on a port does not affect VLAN-unaware forwarding.

## Important APIs, Functions, and Control Flow
Setup creates `br0` without `vlan_filtering`, with low ageing time and multicast snooping disabled, then enslaves two ports and configures two hosts. `ping_ipv4`, `ping_ipv6`, `learning`, and `flooding` delegate to common helpers. `pvid_change` adds VID 3 as PVID/untagged on `$swp1`, confirms IPv4 and IPv6 still work, deletes VID 3, and confirms connectivity still works.

## State, Dependencies, Integration Points, and Risks
State is mostly bridge membership, FDB learning, and optional VLAN metadata that should be ignored by VLAN-unaware forwarding. Dependencies include `lib.sh`, ping helpers, learning/flooding helpers, and normal bridge VLAN commands even though VLAN filtering is off. Risk is low; failures generally indicate a regression where bridge VLAN state leaks into VLAN-unaware forwarding.

## Test Signals
Signals are ping success, learning helper success, flooding helper success, and repeated connectivity after PVID add/delete operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/bridge_vlan_unaware.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/config -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/config

## Purpose
`config` is a Kconfig fragment for the forwarding selftest suite. It lists kernel options and modules needed by bridge, tunnel, VRF, traffic-control, BPF, netfilter, routing, and virtual-interface tests in this directory.

## Important APIs, Types, and Integration Points
The file is declarative rather than executable. It requests core namespace and interface support (`CONFIG_NET_NS`, `CONFIG_NAMESPACES`, `CONFIG_VETH`, `CONFIG_DUMMY`, `CONFIG_MACVLAN`, `CONFIG_NET_VRF`), bridge features (`CONFIG_BRIDGE`, `CONFIG_BRIDGE_VLAN_FILTERING`, `CONFIG_BRIDGE_IGMP_SNOOPING`), IPv4/IPv6 forwarding and multicast routing features, GRE/IPIP/VXLAN tunnels, VLAN 802.1Q, team load-balancing, XFRM user API, nf_tables/conntrack/flowtable, BPF syscall and cgroup BPF, and many tc classifiers/actions/qdiscs (`flower`, `u32`, `matchall`, `mirred`, `vlan`, `skbedit`, `police`, `ingress`, `prio`, `tbf`, etc.).

## State, Dependencies, Risks, and Test Signals
There is no runtime state or control flow. The file integrates with kselftest build/config tooling that can merge fragments into a kernel config. Missing options translate into skipped or failed runtime tests in scripts that expect bridge snooping, VRFs, tunnels, tc filters, or packet manipulation modules. The main risk is configuration drift: new forwarding tests may require additional kernel symbols, and stale entries may mask missing coverage until runtime.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/config -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/custom_multipath_hash.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/custom_multipath_hash.sh

## Purpose
`custom_multipath_hash.sh` tests native IPv4 and IPv6 ECMP distribution when the kernel is configured for custom multipath hashing. It verifies that only the fields selected by `fib_multipath_hash_fields` affect path selection.

## Important APIs, Functions, and Control Flow
The script builds an eight-interface topology: H1, SW1, two parallel routed links, SW2, and H2. SW1 and SW2 each have multipath routes for the opposite host subnet. `ping_ipv4` and `ping_ipv6` establish baseline reachability. Flow generators vary exactly one field at a time: source IPv4, destination IPv4, UDP source/destination ports, source IPv6, destination IPv6, IPv6 flow label, and UDP ports.

`custom_hash_test` snapshots TX packet counters on SW1’s two path interfaces, runs a generator, computes per-path deltas, calculates percentage imbalance through `bc`, and expects it to be within plus/minus 20 percent for balanced cases or outside that range for unbalanced cases. `custom_hash_v4` sets `net.ipv4.fib_multipath_hash_policy=3`, raises IPv4 neighbor GC thresholds for high destination churn, then tests field masks `0x0001`, `0x0002`, `0x0010`, and `0x0020`. `custom_hash_v6` does the same for `net.ipv6` and additionally tests flow label mask `0x0008`.

## State, Dependencies, Integration Points, and Risks
State includes VRFs, routes, sysctls, neighbor GC thresholds, link counters, and generated traffic. Dependencies include `lib.sh`, `$MZ`, `$PING6`, `bc`, `ip vrf exec`, and sysctl save/restore helpers. The test is statistical: insufficient traffic, noisy counters, packet loss, or neighbor churn can make balance thresholds flaky. It restores sysctls after each family-specific suite.

## Test Signals
Signals are ping success plus `custom_hash_test` balance assertions and logged packet deltas. A mismatch between selected hash field and observed balanced/unbalanced distribution fails the test.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/custom_multipath_hash.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/devlink_lib.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/devlink_lib.sh

## Purpose
`devlink_lib.sh` is a shared shell library for forwarding selftests that need devlink resources, shared-buffer state, trap/policer statistics, trap actions, and devlink port discovery. It is not a standalone test; it provides helpers and performs up-front capability checks.

## Important APIs, Functions, and Control Flow
On source, the library resolves `DEVLINK_DEV` from `DEVLINK_DEV` env or from the first test interface, verifies it is registered and PCI-backed, records `DEVLINK_VIDDID`, and skips if iproute2 lacks `resource`, `trap`, or `dev info` support. Resource helpers include `devlink_resource_names_to_path`, `devlink_resource_get`, `devlink_resource_size_get/set`, `devlink_resource_occ_get`, and `devlink_reload`.

Shared-buffer helpers save, set, and restore port-pool thresholds, pool size/thtype, and traffic-class bind pool/threshold. They store originals in associative array `DEVLINK_ORIG` to allow explicit restore after reinterpretation-sensitive changes. Trap helpers enumerate traps/groups, read trap type/action/group/metadata, set trap or group action, read rx packet/byte/drop counters, test idle stats, enable/disable all traps, run exception/drop behavior checks, clean up packet generators and tc filters, and test stat increments. Policer helpers read policer count, rate, burst, dropped counter, and group policer binding. Port helpers map netdev to devlink port, locate CPU port, and read shared-buffer cell/pool sizes.

## State, Dependencies, Integration Points, and Risks
State includes devlink device selection, saved shared-buffer attributes, trap actions, group actions, policer counters, and potentially pending resource sizes until `devlink_reload`. Dependencies include `devlink`, `jq`, `lspci`, `udevadm`, `tc_check_packets`, `kill_process`, and kselftest `check_err`/`check_fail`. Since the library exits with kselftest skip codes during source-time capability checks, consumers must source it only when devlink hardware is expected. A notable code risk is that `devlink_resource_size_set` reports `$size` in its error message even though the local variable is `new_size`.

## Test Signals
Consumers get reusable pass/fail signals through return codes and helper assertions: trap stats idle/non-idle, dropped packet counters, tc packet absence for drop tests, resource occupancy/size values, and restored shared-buffer settings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/devlink_lib.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/dual_vxlan_bridge.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/dual_vxlan_bridge.sh

## Purpose
`dual_vxlan_bridge.sh` tests two independent VXLAN-backed bridge services in one topology: an 802.1ad VLAN-filtering VXLAN bridge and an 802.1d-style VXLAN bridge carrying a VLAN subinterface. It verifies local hosts can reach remote hosts placed in separate network namespaces through VXLAN tunnels and bridge FDB flooding entries.

## Important APIs, Functions, and Control Flow
The script accepts `VXPORT` from the environment, defaulting to 4789. Host setup creates `$h1.10` and `$h2.20`, with tc `clsact` on host devices. `switch_create` builds `br1` as VLAN-filtering 802.1ad with PVID 100 and `br2` as VLAN-unaware, sets bridge MACs to physical switch-port MACs, configures underlay address/routes on `$rp1`, creates `vx100` and `vx200` with `nolearning`, `noudpcsum`, `tos inherit`, and static all-zero FDB append entries toward remote VTEPs. `$swp1` joins `br1`; `$swp2.20` joins `br2`.

`vrp2_create` creates the software underlay peer with veths `v1/v2` and `v3/v4`. `ns_init_common` is exported and run inside `ns1` and `ns2` to configure underlay addresses, `br3`, veth pair `w1/w2`, a VXLAN device, remote FDB entries, host VLAN endpoint, and routes. `ns1_create` configures the 802.1ad/VLAN 100 side; `ns2_create` configures the 802.1d/VLAN 20 side. `ping_ipv4` checks `$h1` to remote `192.0.2.3` and `$h2` to remote `192.0.2.4`.

## State, Dependencies, Integration Points, and Risks
State spans the root namespace, VRFs, two network namespaces, veths, VXLAN devices, bridge FDB entries, VLAN subinterfaces, underlay routes, and tc qdiscs. Dependencies include `lib.sh`, VXLAN kernel support, namespace support, `bridge fdb append`, and stable names `ns1`, `ns2`, `br1`, `br2`, `br3`, `vx100`, `vx200`. Cleanup moves namespace veth peers back before deleting namespaces. Risk is relatively high because a failed mid-setup can leave namespaces or named devices behind; static names also collide with parallel runs.

## Test Signals
The only data-plane signals are the two IPv4 `ping_test` calls, plus setup command failures captured by the kselftest helpers. `test_all` logs the UDP VXLAN port before invoking `tests_run`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/dual_vxlan_bridge.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/fib_offload_lib.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/fib_offload_lib.sh

## Purpose
`fib_offload_lib.sh` is a shared library of FIB offload behavior tests. It verifies which IPv4/IPv6 routes should be programmed in hardware, represented in `ip route` JSON by the absence or presence of the `trap` flag, across route add/append/prepend/replace/delete/replay/flush scenarios.

## Important APIs, Functions, and Control Flow
The primitive `__fib_trap_check` runs `ip -n $ns -j -p -$family route show $route` and uses `jq` to test whether route flags contain `trap`. `fib_trap_check` wraps it in `busywait`; `fib4_trap_check` and `fib6_trap_check` specialize by address family. Test functions then create dummy devices in a supplied namespace, manipulate routes, call trap checks, log a subtest, and delete dummy devices.

IPv4 coverage includes identical routes with append/prepend ordering, TOS priority, metric priority, route replace, delete promotion to the next lowest metric, shared-leaf prefix-length routes, devlink reload replay for metric/TOS/prefix length, and flush-on-device-delete. IPv6 coverage includes single route add, metric priority, append without `nexthop`, replace single, multipath metric/append/replace, appending multipath to a non-multipath route, delete variants for single and multipath routes including replacement by next route type, and devlink reload replay for single and multipath routes.

## State, Dependencies, Integration Points, and Risks
State is isolated to the caller-provided namespace plus dummy devices, route entries, route flags, and devlink reload side effects. Dependencies include `ip`, `jq`, `busywait`, `check_err`, `log_test`, and a devlink device argument for replay tests. Consumers must create the namespace and arrange hardware/offload support before calling these functions. Risks include route string matching sensitivity, hardware drivers that use different offload/trap timing, and cleanup gaps if a function fails before deleting dummy devices.

## Test Signals
The signal is whether the expected route is offloaded (`trap` absent) or trapped/not offloaded (`trap` present) within the busywait window. Each scenario has explicit `check_err` messages indicating the violated route ordering or replay rule.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/fib_offload_lib.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/gre_custom_multipath_hash.sh -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/gre_custom_multipath_hash.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/gre_inner_v4_multipath.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/gre_inner_v4_multipath.sh

## Purpose
`gre_inner_v4_multipath.sh` tests IPv4-over-GRE-over-IPv4 weighted ECMP. It validates that underlay multipath selection can hash on inner IPv4 traffic when `fib_multipath_hash_policy=2`.

## Important APIs, Functions, and Control Flow
The topology places H1 and H2 behind GRE endpoints SW1 and SW4, with SW2/SW3 forming two underlay paths distinguished by VLAN 111 and 222. `sw1_create` and `sw4_create` create GRE tunnel devices and route host subnets through them. `sw2_create` installs the ECMP route toward the remote GRE endpoint; `sw3_create` installs return routes and tc ingress filters on `$ul32` to count traffic per VLAN path.

`multipath4_test` sets `net.ipv4.fib_multipath_hash_policy=2`, replaces SW2’s route to the remote tunnel endpoint with weights supplied by the caller, sends mausezahn UDP traffic with varying inner IPv4 source/destination ranges, reads tc counters, and calls `multipath_eval`. `multipath_ipv4` runs ECMP, 2:1, and 11:45 weight cases. `ping_ipv4` confirms tunnel reachability first.

## State, Dependencies, Integration Points, and Risks
State includes four VRFs, GRE tunnels, underlay routes, VLAN subinterfaces, tc filters, and IPv4 hash policy sysctl. Dependencies include `lib.sh`, tunnel helpers, `tc_rule_stats_get`, `multipath_eval`, `$MZ`, and weighted multipath route support. Risks are statistical variance in distribution and cleanup sensitivity because static tunnel names `g1/g2` and VLAN IDs are reused.

## Test Signals
Signals are IPv4 ping success and `multipath_eval` comparing observed VLAN path packet deltas against requested weights.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/gre_inner_v4_multipath.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/gre_inner_v6_multipath.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/gre_inner_v6_multipath.sh

## Purpose
`gre_inner_v6_multipath.sh` is the IPv6 payload counterpart to the inner GRE multipath test. It verifies that IPv6 traffic carried inside IPv4 GRE is distributed across weighted underlay paths according to inner-flow hashing.

## Important APIs, Functions, and Control Flow
The topology mirrors the IPv4 version but gives H1/H2 IPv6 overlay subnets while keeping the GRE underlay IPv4. GRE tunnels `g1/g2` connect SW1 and SW4; SW2 has an ECMP route to the remote GRE endpoint via VLAN 111/222 paths; SW3 counts those paths with tc filters. `multipath6_test` sets `net.ipv4.fib_multipath_hash_policy=2` because the underlay lookup is IPv4, replaces the remote endpoint route with weighted nexthops, generates IPv6 UDP flows with source/destination ranges, computes tc counter deltas, and calls `multipath_eval`. `multipath_ipv6` runs 1:1, 2:1, and 11:45 cases.

## State, Dependencies, Integration Points, and Risks
State includes IPv6 host routes through GRE, IPv4 tunnel endpoint routes, tc filters, VLAN path counters, and the IPv4 multipath hash sysctl. Dependencies are `lib.sh`, GRE tunnel helpers, mausezahn IPv6 support, `tc_rule_stats_get`, and `multipath_eval`. The test is sensitive to packet volume and timing because weighted distribution is inferred from sampled counters.

## Test Signals
Signals are successful IPv6 ping through the tunnel and weighted distribution checks for each multipath weight pair.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/gre_inner_v6_multipath.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/gre_multipath.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/gre_multipath.sh

## Purpose
`gre_multipath.sh` tests weighted ECMP where the route itself forwards IPv4 traffic to two GRE tunnel devices. Unlike the inner-hash tests, the multipath route’s nexthops are the GRE devices `g1a` and `g1b`.

## Important APIs, Functions, and Control Flow
Setup creates H1/SW1/SW2/H2, two VLAN underlay paths, and two GRE tunnel pairs with distinct local/remote endpoint addresses. SW1 routes the H2 subnet through a multipath route with `nexthop dev g1a` and `nexthop dev g1b`; SW2 configures reverse tunnels and tc ingress filters on `$ul2` for VLAN IDs 111/222. `multipath4_test` sets `net.ipv4.fib_multipath_hash_policy=1`, replaces the route with caller-supplied weights on `g1a/g1b`, sends UDP traffic varying destination port, reads VLAN path counters, evaluates weights, then restores route/sysctl. `multipath_ipv4` runs ECMP and two weighted cases.

## State, Dependencies, Integration Points, and Risks
State includes GRE devices, route nexthops, VLAN underlay, tc filters, VRFs, and IPv4 hash policy sysctl. Dependencies include `lib.sh`, `tunnel_create`, `tc_rule_stats_get`, `$MZ`, and `multipath_eval`. Risks are statistical distribution variance and possible route/tunnel cleanup leftovers if interrupted.

## Test Signals
Signals are baseline IPv4 ping and observed tc counter ratios matching 1:1, 2:1, and 11:45 route weights.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/gre_multipath.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/gre_multipath_nh.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/gre_multipath_nh.sh

## Purpose
`gre_multipath_nh.sh` tests GRE multipath routes implemented with reusable nexthop objects. It covers both IPv4 and IPv6 payload routes using the same nexthop group to GRE devices.

## Important APIs, Functions, and Control Flow
Setup resembles `gre_multipath.sh`, but `sw1_create` creates IPv6 nexthop objects `101` and `102` pointing to `g1a/g1b`, then creates group `103`; both IPv4 and IPv6 routes use `nhid 103`. SW2 builds reverse nexthops `201`, `202`, and group `203`. `multipath4_test` and `multipath6_test` set the appropriate family hash policy to 1, replace nexthop group `103` with requested weights, send UDP traffic from H1 to H2, count path hits with tc filters on `$ul2`, evaluate distribution, and restore the unweighted group.

## State, Dependencies, Integration Points, and Risks
State includes GRE tunnels, nexthop objects and groups, routes by `nhid`, sysctls, tc filters, VLAN subinterfaces, and dual-stack host addressing. Dependencies include iproute2 nexthop support, `lib.sh`, `tc_rule_stats_get`, `$MZ`, and `multipath_eval`. The cleanup order deletes routes before nexthop groups and member nexthops, which is important because active routes reference those objects. Risks include object ID collisions in parallel runs and unsupported nexthop object syntax.

## Test Signals
Signals are IPv4/IPv6 ping success and weighted distribution checks for ECMP, 2:1, and 11:45 cases in each family.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/gre_multipath_nh.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/gre_multipath_nh_res.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/gre_multipath_nh_res.sh

## Purpose
`gre_multipath_nh_res.sh` tests GRE weighted multipath through resilient nexthop groups. It is parallel to `gre_multipath_nh.sh` but creates groups with `type resilient buckets 512 idle_timer 0` and replaces them as resilient groups.

## Important APIs, Functions, and Control Flow
Topology and host setup match the non-resilient nexthop-object variant. `sw1_create` and `sw2_create` add member nexthops to GRE devices, create resilient group objects `103` and `203`, and route both IPv4 and IPv6 prefixes through those groups. `multipath4_test` and `multipath6_test` set family hash policy to 1, replace group `103` with weighted resilient members, send UDP traffic, count VLAN path hits through tc, evaluate observed ratio, and restore the resilient group without weights.

## State, Dependencies, Integration Points, and Risks
State includes resilient nexthop buckets, idle timer configuration, GRE devices, dual-stack routes, tc counters, and sysctls. Dependencies are the same as the non-resilient version plus kernel/iproute2 support for resilient nexthop groups. Distribution can be affected by resilient bucket assignment, so expected ratios depend on `multipath_eval` tolerances and bucket count.

## Test Signals
Signals are ping success and path packet ratios matching 1:1, 2:1, and 11:45 for IPv4 and IPv6 through resilient nexthop groups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/gre_multipath_nh_res.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/ip6_forward_instats_vrf.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/ip6_forward_instats_vrf.sh

## Purpose
`ip6_forward_instats_vrf.sh` verifies that IPv6 forwarding error statistics are charged to the incoming router interface when forwarding occurs inside a VRF. It checks normal IPv6 forwarding plus four specific `Ip6In*` counters.

## Important APIs, Functions, and Control Flow
Setup creates H1, a router VRF with ingress `$rtr1` and egress `$rtr2`, and H2. H2 and `$rtr2` MTUs are set to 1280. `require_command $TROUTE6` enforces traceroute6 availability. `ipv6_ping` verifies baseline H1-to-H2 reachability. `ipv6_in_too_big_err` snapshots `Ip6InTooBigErrors` on `$rtr1`, sends a ping larger than the egress MTU, and expects the counter to increase. `ipv6_in_hdr_err` uses traceroute6 to send hop-limit-constrained traffic and checks `Ip6InHdrErrors`. `ipv6_in_addr_err` temporarily disables global IPv6 forwarding while sending a packet and expects `Ip6InAddrErrors`. `ipv6_in_discard` installs a forwarding XFRM block policy, sends a ping, removes the policy, and expects `Ip6InDiscards`.

## State, Dependencies, Integration Points, and Risks
State includes VRFs, IPv6 routes, MTU overrides, global IPv6 forwarding sysctl, and transient XFRM policy. Dependencies include `lib.sh`, `ipv6_stats_get`, `master_name_get`, `$PING6`, traceroute6, and XFRM support. The test temporarily writes `net.ipv6.conf.all.forwarding` directly rather than through `sysctl_set`, so interruption during `ipv6_in_addr_err` could leave forwarding disabled until cleanup or external repair.

## Test Signals
Each counter test compares pre/post `ipv6_stats_get` values and requires a non-zero delta. Baseline ping uses `ping6_test`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/ip6_forward_instats_vrf.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/ip6gre_custom_multipath_hash.sh -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/ip6gre_custom_multipath_hash.sh -->
