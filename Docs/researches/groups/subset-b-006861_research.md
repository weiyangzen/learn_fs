# subset-b-006861 research

Grouped research for Linux networking selftests under `sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding`. Each section is source-tree aligned and intended for deterministic splitting into `Docs/researches/<source>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/ip6gre_flat.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/ip6gre_flat.sh

Purpose: IPv6-underlay GRE tunnel selftest for the flat topology without GRE keys. It validates IPv4-in-IPv6 and IPv6-in-IPv6 forwarding, MTU adjustment, and live remote endpoint changes.

Important APIs/functions: `setup_prepare`, `gre_flat`, `gre_mtu_change`, `gre_flat_remote_change`, `cleanup`; imported helpers from `lib.sh` and `ip6gre_lib.sh` such as `forwarding_enable`, `vrf_prepare`, `h1_create`, `sw1_flat_create`, `test_traffic_ip4ip6`, `test_traffic_ip6ip6`, and `flat_remote_change`.

Control flow: declares three `ALL_TESTS`, maps six veth positions into host, overlay, and underlay variables, enables forwarding/VRF rules, creates endpoints and flat switch tunnels, waits, then runs tests. Remote-change test changes both tunnel endpoints, validates traffic, restores old endpoints, and validates again.

State/persistence: mutates global forwarding sysctls, route rules, VRFs, VLANs, `ip6gre` devices `g1a`/`g2a`, addresses, routes, and temporary tc filters installed by library traffic probes. Cleanup tears these down in reverse.

Dependencies/integration: depends on root privileges, iproute2, mausezahn, tc flower counters, and `ip6gre_lib.sh` flat topology semantics. It integrates with kselftest harness variables `RET` and `EXIT_STATUS` through `tests_run`.

Risks: failures can come from stale routes/neighbors, unsupported GRE offload, tc counter timing, or missed cleanup if setup partially fails. The flat topology intentionally mixes default and non-default VRFs, so route-rule ordering from `vrf_prepare` is critical.

Test signals: successful ping-like generated traffic counters on underlay and overlay ports, failed large ping before MTU increase, successful large ping after MTU increase, and successful traffic after both new and restored remote endpoints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/ip6gre_flat.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/ip6gre_flat_key.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/ip6gre_flat_key.sh

Purpose: Flat IPv6-underlay GRE tunnel selftest with a shared GRE `key 233`. It confirms keyed tunnel lookup still forwards IPv4 and IPv6 payloads and survives MTU and endpoint changes.

Important APIs/functions: same driver shape as `ip6gre_flat.sh`, but `setup_prepare` calls `sw1_flat_create $ol1 $ul1 key 233` and `sw2_flat_create $ol2 $ul2 key 233`. Test functions are `gre_flat`, `gre_mtu_change`, and `gre_flat_remote_change`.

Control flow: after interface assignment and common VRF/forwarding setup, both tunnel endpoints are created with identical input/output keys. The traffic tests use `test_traffic_ip4ip6` and `test_traffic_ip6ip6`; remote-change temporarily rewrites local/remote tunnel addresses and routing through `flat_remote_change`/`flat_remote_restore`.

State/persistence: creates keyed `ip6gre` devices, VLAN underlay links, overlay routes, and temporary tc counters. Global sysctls and route rules are saved/restored by `lib.sh` helpers.

Dependencies/integration: depends on `ip6gre_lib.sh` supporting opaque extra tunnel arguments and on kernel keyed GRE-over-IPv6 behavior. Uses `tests_run` from kselftest forwarding `lib.sh`.

Risks: asymmetric or missing key support in hardware/software paths can blackhole traffic while unkeyed variants pass. Counter timing and neighbor state remain shared risks with the flat base test.

Test signals: both IPv4-in-IPv6 and IPv6-in-IPv6 packet counters must increment with keyed tunnel devices before and after endpoint changes; MTU test must fail before and pass after raising topology MTUs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/ip6gre_flat_key.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/ip6gre_flat_keys.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/ip6gre_flat_keys.sh

Purpose: Flat IPv6-underlay GRE tunnel selftest using directional keys. SW1 uses `ikey 111 okey 222`, SW2 uses the inverse, validating asymmetric key handling.

Important APIs/functions: `setup_prepare`, `gre_flat`, `gre_mtu_change`, `gre_flat_remote_change`, `cleanup`; extra tunnel arguments are passed through `sw1_flat_create`/`sw2_flat_create` in `ip6gre_lib.sh`.

Control flow: builds the same six-interface flat topology as the unkeyed test, then runs traffic validation for both inner IPv4 and IPv6. Remote-change rewrites tunnel endpoints while keeping key configuration unchanged, then restores original endpoints.

State/persistence: modifies forwarding sysctls, VRF rules, VLANs, keyed `ip6gre` devices, tunnel endpoint addresses, IPv6 routes to tunnel remotes, and tc filters/counters used by traffic tests.

Dependencies/integration: relies on bidirectional `ikey`/`okey` matching in kernel GRE-over-IPv6 and on the common `ip6gre_lib.sh` topology and tc-common counter helpers.

Risks: directional keys make directionality explicit; swapping or normalizing keys incorrectly would cause one direction to fail. The MTU function call passes an unused `gre` argument, tolerated by current `test_mtu_change` but a coupling risk if that helper changes.

Test signals: generated IPv4 and IPv6 traffic must be observed on underlay egress and post-decap overlay egress in both original and changed endpoint states; large IPv6 ping behavior validates MTU propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/ip6gre_flat_keys.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/ip6gre_hier.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/ip6gre_hier.sh

Purpose: IPv6-underlay GRE tunnel selftest for hierarchical VRF topology without keys, where tunnel devices are bound to underlay dummy devices in different VRFs than the overlay.

Important APIs/functions: `setup_prepare` calls `sw1_hierarchical_create` and `sw2_hierarchical_create`; tests are `gre_hier`, `gre_mtu_change`, and `gre_hier_remote_change`; cleanup calls hierarchical destroy helpers.

Control flow: maps six interfaces, enables forwarding/VRF route rules, creates host endpoints, then creates separated overlay and underlay VRFs with dummy-bound `ip6gre` devices. Tests run IPv4/IPv6 payload validation, topology MTU changes, then endpoint rewrite/restore through hierarchical remote helpers.

State/persistence: creates VRFs per endpoint/link, dummy devices `dummy1`/`dummy2`, VLAN underlay links, `g1a`/`g2a` tunnels, routes in both overlay and underlay VRFs, and transient tc counters.

Dependencies/integration: depends on `ip6gre_lib.sh` hierarchical model and kernel support for tunnel `dev dummyX` binding across VRFs.

Risks: route deletion must target the correct VRF; endpoint-change functions update dummy addresses instead of tunnel-device addresses, so mismatched cleanup can leave stale addresses/routes. Hardware offload paths may differ from flat topology.

Test signals: IPv4-in-IPv6 and IPv6-in-IPv6 counters after encapsulation/decapsulation, successful MTU raise behavior, and successful traffic after changing and restoring hierarchical tunnel remotes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/ip6gre_hier.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/ip6gre_hier_key.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/ip6gre_hier_key.sh

Purpose: Hierarchical IPv6 GRE tunnel selftest with shared GRE `key 22`. It combines underlay/overlay VRF separation with keyed GRE lookup.

Important APIs/functions: `setup_prepare` passes `key 22` to both `sw1_hierarchical_create` and `sw2_hierarchical_create`; `gre_hier` uses `test_traffic_ip4ip6` and `test_traffic_ip6ip6`; remote-change helpers are `hier_remote_change` and `hier_remote_restore`.

Control flow: creates host VRFs, hierarchical switch topology, keyed `ip6gre` devices bound to dummy underlay endpoints, validates traffic, changes MTU, rewrites remote endpoints, validates, restores, and validates.

State/persistence: manipulates forwarding sysctls, local route rules, dummy underlay addresses, VLANs, keyed tunnels, VRF routes, and tc clsact/flower counters. Cleanup reverses switch, host, VRF, and forwarding state.

Dependencies/integration: relies on `lib.sh`, `tc_common.sh` via `ip6gre_lib.sh`, and kernel support for keyed ip6gre devices bound to a device in another VRF.

Risks: if key matching or VRF binding is offloaded differently from software, traffic may pass in one path and fail in another. Remote-change tests also depend on updating routes in underlay VRFs after local address changes.

Test signals: both inner protocol traffic checks pass with `key 22`; MTU test transitions from expected failure to success; keyed tunnel remains functional after endpoint changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/ip6gre_hier_key.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/ip6gre_hier_keys.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/ip6gre_hier_keys.sh

Purpose: Hierarchical IPv6 GRE tunnel selftest with asymmetric GRE keys. It validates `ikey`/`okey` behavior when tunnel endpoints are bound through separate underlay VRFs.

Important APIs/functions: `setup_prepare` creates SW1 with `ikey 111 okey 222` and SW2 with `ikey 222 okey 111`; tests use `test_traffic_ip4ip6`, `test_traffic_ip6ip6`, `test_mtu_change`, `hier_remote_change`, and `hier_remote_restore`.

Control flow: builds six-interface hierarchical topology, runs IPv4 and IPv6 traffic checks, increases topology MTUs for large IPv6 ping, changes tunnel local/remote addresses on dummy-bound endpoints, validates traffic, restores original addresses, and reruns traffic checks.

State/persistence: creates and deletes dummy devices, per-link VRFs, VLAN underlay links, directional-key `ip6gre` tunnels, routes in overlay/underlay VRFs, and tc statistics filters.

Dependencies/integration: depends on `ip6gre_lib.sh` accepting extra `ip link add type ip6gre` parameters and on common kselftest result aggregation.

Risks: direction-specific key mismatch causes silent one-way failure. Hierarchical cleanup is sensitive to route order and dummy-device existence.

Test signals: tc counters show forwarded inner IPv4 and IPv6 packets across the GRE-over-IPv6 tunnel in both endpoint states, and MTU behavior matches the larger-packet expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/ip6gre_hier_keys.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/ip6gre_inner_v4_multipath.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/ip6gre_inner_v4_multipath.sh

Purpose: Tests IPv4 payload distribution over `ip6gre` when the IPv6 underlay route uses ECMP or weighted multipath. It specifically enables inner-flow hashing with `net.ipv6.fib_multipath_hash_policy=2`.

Important APIs/functions: topology helpers `h1_create`, `sw1_create`, `sw2_create`, `sw3_create`, `sw4_create`, `h2_create`; tests `ping_ipv4`, `multipath_ipv4`; core evaluator `multipath4_test`.

Control flow: creates a 10-interface chain H1-SW1-SW2-SW3-SW4-H2. SW2 and SW3 connect through VLAN 111/222 parallel paths, with tc flower counters on SW3 ingress. `multipath4_test` changes the SW2 route weights, sends many UDP flows with varied IPv4 source/destination ranges through the tunnel, computes per-VLAN deltas, and calls `multipath_eval`.

State/persistence: creates VRFs, IPv4 host routes, IPv6 underlay addresses, VLANs, `ip6gre` tunnels `g1`/`g2`, multipath IPv6 routes, tc clsact filters, and temporarily changes a sysctl.

Dependencies/integration: relies on `lib.sh` tunnel/VLAN helpers, `MZ` traffic generation, `tc_rule_stats_get`, `multipath_eval`, and `bc` ratio math.

Risks: packet distribution is statistical and can be flaky on slow machines or small samples. A typo in destroy uses `2001:Db8` but IPv6 parsing is case-insensitive. Failure can also indicate kernel hash policy ignoring inner headers.

Test signals: baseline ping to 192.0.4.2 succeeds; ECMP and weighted 2:1 and 11:45 tests produce measured VLAN counter ratios within 15 percent of expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/ip6gre_inner_v4_multipath.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/ip6gre_inner_v6_multipath.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/ip6gre_inner_v6_multipath.sh

Purpose: IPv6 payload counterpart of the inner-flow multipath GRE-over-IPv6 test. It verifies ECMP and weighted multipath distribution when the GRE payload is IPv6.

Important APIs/functions: same topology roles as the IPv4 version; `multipath6_test` sends ranged IPv6 UDP traffic and evaluates counters; `ping_ipv6` and `multipath_ipv6` are the exported tests.

Control flow: builds H1/SW1/SW2/SW3/SW4/H2 topology, adds `ip6gre` tunnels over IPv6 underlay, installs two VLAN underlay paths between SW2 and SW3, and attaches ingress counters for VLAN 111/222. Each multipath case sets hash policy 2, replaces route weights, sends 50 UDP flows across IPv6 source/destination ranges, and checks ratio.

State/persistence: mutates VRFs, IPv6 addresses and routes, VLANs, `ip6gre` tunnel devices, tc qdiscs/filters, and `net.ipv6.fib_multipath_hash_policy`.

Dependencies/integration: uses `lib.sh` helpers, `MZ -6`, tc JSON counter helpers, and `multipath_eval`.

Risks: distribution tolerance is sample-size sensitive. Systems without inner IPv6 hash support for GRE or with different offload behavior can collapse traffic to one path. Cleanup route/address ordering is important.

Test signals: ping6 to 2001:db8:2::2 succeeds; ECMP and weighted 2:1 and 11:45 cases pass measured-versus-expected ratio checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/ip6gre_inner_v6_multipath.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/ip6gre_lib.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/ip6gre_lib.sh

Purpose: Shared library for GRE/IP-in-IP over IPv6 forwarding tests. It defines flat and hierarchical topologies, host setup, traffic probes, MTU changes, and remote endpoint mutation helpers.

Important APIs/functions: `h1_create/destroy`, `h2_create/destroy`, `sw1_flat_create/destroy`, `sw2_flat_create/destroy`, `sw1_hierarchical_create/destroy`, `sw2_hierarchical_create/destroy`, `test_traffic_ip4ip6`, `test_traffic_ip6ip6`, `topo_mtu_change`, `test_mtu_change`, `flat_remote_change/restore`, `hier_remote_change/restore`.

Control flow: driver scripts source this file after `lib.sh`. Topology creation composes VRFs, VLAN 111 underlay, `ip6gre` tunnels, tunnel remote routes, and overlay routes. Traffic tests install tc clsact filters on underlay and decap egress devices, generate 1000 packets with mausezahn, assert counters, then remove filters.

State/persistence: creates device-level state including `g1a`, `g2a`, dummy underlay endpoints, per-device VRFs, VLANs, neighbor entries, IP routes, and sysctl-backed forwarding via callers. It has no durable persistence beyond kernel network state.

Dependencies/integration: imports `lib.sh` and `tc_common.sh`; expects globals `h1`, `h2`, `ol1`, `ol2`, `ul1`, `ul2`, `TC_FLAG`, `MZ`, and `MZ_DELAY` supplied by callers.

Risks: several destroy routines delete specific routes and addresses; partial setup failures can make cleanup noisy. Tests assume tc counters reflect the intended datapath and that neighbor priming avoids first-packet loss.

Test signals: library functions report through `check_err`, `check_fail`, and `log_test`; callers observe packet counter thresholds and ping/MTU behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/ip6gre_lib.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/ipip_flat_gre.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/ipip_flat_gre.sh

Purpose: IPv4 GRE tunnel selftest for the flat topology without GRE keys. It validates basic IPv4 forwarding through GRE and MTU propagation.

Important APIs/functions: `setup_prepare`, `gre_flat4`, `gre_mtu_change`, `cleanup`; imports `lib.sh` and `ipip_lib.sh`, using `sw1_flat_create gre`, `sw2_flat_create gre`, `ping_test`, and `test_mtu_change`.

Control flow: assigns six interfaces to hosts, overlay, and underlay, enables forwarding and VRF route-rule changes, creates endpoints and flat GRE tunnel topology, waits for links, then runs ping and MTU tests.

State/persistence: creates VRFs, VLAN 111 underlay links, GRE devices `g1a`/`g2a`, IPv4 tunnel endpoint routes, overlay routes, and forwarding sysctls. Cleanup reverses all created state.

Dependencies/integration: depends on `ipip_lib.sh` for IPv4 tunnel topology and on `lib.sh` for VRF and ping harness behavior.

Risks: only one payload family is covered; tc counters are not used, so pass signal is reachability. GRE underlay neighbor resolution and route-rule ordering can still affect results.

Test signals: `ping_test $h1 192.0.2.18` succeeds through GRE, and large ping fails before MTU increase but succeeds after topology MTU is raised.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/ipip_flat_gre.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/ipip_flat_gre_key.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/ipip_flat_gre_key.sh

Purpose: Flat IPv4 GRE tunnel test with shared `key 233`, validating keyed GRE over IPv4.

Important APIs/functions: `setup_prepare` invokes `sw1_flat_create gre $ol1 $ul1 key 233` and `sw2_flat_create gre $ol2 $ul2 key 233`; tests are `gre_flat4` and `gre_mtu_change`.

Control flow: creates the flat `ipip_lib.sh` topology, runs one IPv4 reachability test from H1 to H2 through keyed GRE, then runs the common MTU increase test.

State/persistence: sets up VRFs, VLANs, keyed GRE tunnel devices, tunnel endpoint routes, overlay routes, and forwarding sysctls; cleanup calls flat destroy helpers and restores route rules/sysctls.

Dependencies/integration: relies on Linux `ip link add type gre key` support and `ipip_lib.sh` passing extra tunnel arguments.

Risks: shared keyed GRE may fail differently from unkeyed GRE on hardware offload. The script depends on cleanup destroying `g1a`/`g2a` even when setup fails midway.

Test signals: H1 can ping 192.0.2.18 with label "gre flat with key"; MTU behavior matches the common `test_mtu_change` assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/ipip_flat_gre_key.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/ipip_flat_gre_keys.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/ipip_flat_gre_keys.sh

Purpose: Flat IPv4 GRE tunnel selftest with asymmetric keys, validating directional key mapping in an IPv4 underlay.

Important APIs/functions: `setup_prepare`, `gre_flat4`, `gre_mtu_change`, `cleanup`; SW1 is created with `ikey 111 okey 222`, SW2 with `ikey 222 okey 111`.

Control flow: identical to the unkeyed flat GRE test except tunnel creation uses paired directional keys. It performs one H1-to-H2 IPv4 ping through the tunnel and the common large-packet MTU transition test.

State/persistence: creates directional-key GRE tunnels, VLAN underlay, routes, VRFs, and forwarding sysctls. It uses `ipip_lib.sh` cleanup to remove all tunnel and route state.

Dependencies/integration: depends on kernel GRE `ikey`/`okey` support and common kselftest functions in `lib.sh`.

Risks: directionality errors produce blackholes despite correct topology. The test does not explicitly test reverse ping, but ICMP replies exercise the opposite key direction.

Test signals: successful ping to 192.0.2.18 labeled "gre flat with ikey/okey" and passing MTU increase check.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/ipip_flat_gre_keys.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/ipip_hier_gre.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/ipip_hier_gre.sh

Purpose: IPv4 GRE tunnel selftest for hierarchical topology without keys, where tunnel devices are bound through underlay dummy devices in separate VRFs.

Important APIs/functions: `setup_prepare` uses `sw1_hierarchical_create gre` and `sw2_hierarchical_create gre`; tests are `gre_hier4` and `gre_mtu_change`.

Control flow: maps six interfaces, enables forwarding/VRF rules, creates host endpoints and hierarchical switch state, then runs IPv4 ping through GRE and common MTU behavior validation.

State/persistence: creates VRFs, dummy underlay endpoints, VLAN 111 links, GRE tunnels, overlay routes, underlay routes, and forwarding sysctls. Cleanup destroys hierarchical switch state before host and VRF cleanup.

Dependencies/integration: depends on `ipip_lib.sh` hierarchical functions and on `lib.sh` for VRFs/pings.

Risks: topology relies on route separation between overlay and underlay VRFs; wrong route deletion can leave persistent rules/devices. Hardware may not support hierarchical GRE offload equivalently to software.

Test signals: H1 ping to 192.0.2.18 succeeds through hierarchical GRE; MTU test sees expected failure before and success after increasing topology MTU.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/ipip_hier_gre.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/ipip_hier_gre_key.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/ipip_hier_gre_key.sh

Purpose: Hierarchical IPv4 GRE test with shared key `22`, combining underlay/overlay VRF separation with keyed tunnel lookup.

Important APIs/functions: `setup_prepare` passes `key 22` to both hierarchical create helpers; `gre_hier4` uses `ping_test`; `gre_mtu_change` uses `test_mtu_change gre`.

Control flow: creates host VRFs, hierarchical GRE topology, then executes keyed tunnel reachability and MTU transition tests.

State/persistence: creates keyed GRE devices bound through dummy underlay endpoints, VLANs, VRFs, routes, and forwarding sysctls. Cleanup reverses the topology and route-rule changes.

Dependencies/integration: imports `lib.sh` and `ipip_lib.sh`; requires iproute2 and kernel support for `gre key` plus VRF device binding.

Risks: shared key path can expose offload or lookup issues not covered by unkeyed hierarchical GRE. Cleanup must run after `pre_cleanup` even when tests fail.

Test signals: ping through "gre hierarchical with key" succeeds, and MTU behavior passes common assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/ipip_hier_gre_key.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/ipip_hier_gre_keys.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/ipip_hier_gre_keys.sh

Purpose: Hierarchical IPv4 GRE test with asymmetric `ikey`/`okey`, validating directional keys across separated underlay and overlay VRFs.

Important APIs/functions: `setup_prepare`, `gre_hier4`, `gre_mtu_change`, `cleanup`; calls `sw1_hierarchical_create gre ... ikey 111 okey 222` and inverse keys on SW2.

Control flow: builds the standard six-interface hierarchical GRE topology, runs reachability through the keyed tunnel, performs the MTU increase test, and cleans up in reverse.

State/persistence: mutates VRF devices/tables, dummy devices, GRE tunnels, VLANs, IPv4 routes, and forwarding sysctls.

Dependencies/integration: depends on `ipip_lib.sh` tunnel creation accepting directional key arguments and `lib.sh` test harness semantics.

Risks: one-way key mismatch is the central risk; ICMP ping includes reply direction but does not isolate which direction failed. Hierarchical route setup is more sensitive to partial cleanup than flat tests.

Test signals: successful ping labeled "gre hierarchical with ikey/okey" and passing common GRE MTU-change test.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/ipip_hier_gre_keys.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/ipip_lib.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/ipip_lib.sh

Purpose: Shared IPv4 GRE/IP-in-IP topology library for flat and hierarchical tunnel tests.

Important APIs/functions: host helpers `h1_create/destroy`, `h2_create/destroy`; switch helpers `sw1_flat_create/destroy`, `sw2_flat_create/destroy`, `sw1_hierarchical_create/destroy`, `sw2_hierarchical_create/destroy`; MTU helpers `topo_mtu_change` and `test_mtu_change`.

Control flow: callers source this after `lib.sh`, set global interface names, then call create helpers. Flat helpers place overlay and underlay in the same/default VRF on SW1 and bound VRF on SW2. Hierarchical helpers introduce `dummy1`/`dummy2` in underlay VRFs and master GRE devices to overlay VRFs.

State/persistence: creates VRFs, VLAN 111 links, GRE/IPIP tunnel devices `g1a`/`g2a`, dummy devices, IPv4 routes, and addresses. It stores no state outside kernel networking.

Dependencies/integration: expects `lib.sh` functions already loaded. Extra tunnel parameters are passed through to `tunnel_create`, enabling keyed GRE variants.

Risks: cleanup assumes exact route/address state and device names. `test_mtu_change` uses large ping size and route MTU behavior, which can vary across drivers/offloads.

Test signals: callers use ping success and MTU failure/success transition to establish forwarding and MTU propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/ipip_lib.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/ipmr.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/ipmr.c

Purpose: C kselftest for IPv4 multicast routing (`ipmr`) socket and netlink control-plane behavior, added with Google copyright.

Important APIs/types/functions: `FIXTURE(ipmr)`, `FIXTURE_VARIANT(ipmr, ipv4)`, `struct mfc_attr`, `nl_add_rtattr`, `nl_sendmsg_mfc`, fixture setup/teardown, and tests for `MRT_INIT`, VIF add/delete, MFC add/delete, netlink routes, proxy entries, no-VIF errors, netns dismantle, and table flush.

Control flow: fixture unshares a network namespace, opens NETLINK_ROUTE and raw IGMP sockets, creates a veth pair, and records `veth0` ifindex. Tests exercise `setsockopt` multicast routing options and custom RTM_NEWROUTE/RTM_DELROUTE messages with `RTNL_FAMILY_IPMR`, then inspect `/proc/net/ip_mr_vif` or `/proc/net/ip_mr_cache`.

State/persistence: all state is inside the temporary netns: raw socket multicast router state, VIFs, MFC cache entries, veth device, and table-specific multicast routing data. Teardown closes sockets; netns cleanup removes remaining devices/routes.

Dependencies/integration: integrates with `kselftest_harness.h`, Linux multicast routing UAPI headers, rtnetlink, and shell `ip`/`cat`/`grep` via `system`.

Risks: tests depend on root or sufficient namespace privileges and kernel multicast routing support. Netlink helper has a fixed 4 KiB buffer and asserts ACK shape. `pkill` is not used; isolation is stronger than shell tests.

Test signals: kselftest assertions validate zero or expected negative errors (`-ENFILE`, `-ENODEV`, `EADDRNOTAVAIL`) and expected `/proc` entries for VIF/MFC state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/ipmr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/lib.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/lib.sh

Purpose: Core shell harness for forwarding selftests. It provides interface discovery/creation, environment validation, VRF/VLAN/tunnel helpers, sysctl save/restore, packet generation/capture helpers, multicast helpers, and test result aggregation.

Important APIs/functions: `NETIFS`, `require_command` integration, `vrf_prepare/cleanup`, `vrf_create/destroy`, `simple_if_init/fini`, `tunnel_create/destroy`, `vlan_create/destroy`, `team_create/destroy`, stats helpers, `sysctl_set/restore`, `forwarding_enable/restore`, `ping_test`, `ping6_test`, `tests_run`, `check_err` family from parent lib, tcpdump helpers, multicast packet builders, and `multipath_eval`.

Control flow: on source, it loads config, validates root/tools/interfaces, optionally creates veth pairs or driver-conformant remote mappings, then defines helpers. Importing tests define `NUM_NETIFS` and `ALL_TESTS`, perform setup, call `setup_wait`, and invoke `tests_run`.

State/persistence: can create veths, VRFs, VLANs, tunnels, team devices, qdiscs, filters, tcpdump temp files, sysctl snapshots, MAC snapshots, and multicast daemons via helper calls. Most state is restored by explicit test cleanup.

Dependencies/integration: imports `tools/testing/selftests/net/lib.sh`, uses `ip`, `tc`, `jq`, `ethtool`, `mausezahn`, `tcpdump`, `teamd`, `mtools`, `smcrouted`, and kselftest status variables.

Risks: sourcing has side effects such as creating interfaces and exiting on missing prerequisites. Global arrays (`SYSCTL_ORIG`, `MTU_ORIG`, `TARGETS`) and shared `RET`/`EXIT_STATUS` are mutable. Cleanup correctness depends on caller discipline.

Test signals: helpers log pass/fail/skip/xfail through kselftest conventions; this file itself is covered by `lib_sh_test.sh`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/lib.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/lib_sh_test.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/lib_sh_test.sh

Purpose: Unit-style selftest for `lib.sh` result semantics, especially `RET`, `retmsg`, `FAIL_TO_XFAIL`, skip handling, slow-machine xfail behavior, and final `EXIT_STATUS`.

Important APIs/functions: simulated checks `tpass`, `tfail`, `txfail`; simulated tests `pass`, `fail`, `xfail`, `skip`, `slow_xfail`; verifiers `ret_tests_run`, `ret_subtest`, `test_ret`, `exit_status_tests_run`, `exit_status_subtest`, `test_exit_status`.

Control flow: sets `NUM_NETIFS=0`, sources `lib.sh`, then runs two meta-tests. `test_ret` invokes check helpers directly in subshells and asserts resulting return code/message. `test_exit_status` sets `TESTS` and runs `tests_run` in subshells to verify final status precedence.

State/persistence: no network devices are needed. It mutates shell globals `RET`, `EXIT_STATUS`, `retmsg`, `TESTS`, `FAIL_TO_XFAIL`, and `KSFT_MACHINE_SLOW` only within current/subshell contexts.

Dependencies/integration: depends on `lib.sh` being sourceable with zero interfaces and on parent kselftest status constants (`ksft_pass`, `ksft_fail`, `ksft_xfail`, `ksft_skip`).

Risks: because it tests shell-global behavior, accidental leakage between subshell and parent would mask bugs. It traps `pre_cleanup`, not full network cleanup, because no topology is created.

Test signals: logs expected transitions for check return aggregation and final exit status across combinations of pass/fail/xfail/skip and slow-machine flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/lib_sh_test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/local_termination.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/local_termination.sh

Purpose: Validates which unicast, multicast, link-local, VLAN, bridge, and PTP packets are locally terminated by a NIC/bridge/VLAN stack.

Important APIs/functions: constants for test addresses and raw packet payloads; `send_raw`, `send_uc_ipv4`, `check_rcv`, `mc_route_prepare/destroy`, `run_test`; topology helpers for standalone, VLAN, bridge, macvlan, and VLAN-over-bridge scenarios.

Control flow: each scenario builds a topology, starts tcpdump on the receive interface, sends primary-MAC, macvlan-MAC, unknown unicast, joined/unknown IPv4/IPv6 multicast, promisc/allmulti cases, link-local STP/LLDP, and PTP over L2/IPv4/IPv6. It stops tcpdump and matches packet text against expected receipt/nonreceipt patterns.

State/persistence: creates VRFs, VLAN devices, bridge `br0`, macvlan `macvlan0`, multicast routes, multicast memberships via mtools, tcpdump temp files, and toggles promisc/allmulti flags. Cleanup removes topology and route-rule state.

Dependencies/integration: requires mtools (`REQUIRE_MTOOLS=yes`), tcpdump, mausezahn, `has_unicast_flt`, multicast helpers, and `lib.sh`.

Risks: tcpdump text patterns are version-sensitive. Unknown multicast tests are marked xfail in selected cases. PTP checks are skipped for bridge receiver scenarios. Hardware unicast filtering capability changes expectations.

Test signals: per-packet-type `check_rcv` pass/fail logs across standalone, VLAN, VLAN-aware/unaware bridge, VLAN over bridged port, and VLAN over bridge scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/local_termination.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/min_max_mtu.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/min_max_mtu.sh

Purpose: Tests device-reported minimum and maximum MTU constraints and traffic behavior at those limits through VLAN interfaces.

Important APIs/functions: topology helpers `h1_create`, `switch_create`; tests `ping_ipv4`, `ping_ipv6`, `max_mtu_config_test`, `max_mtu_traffic_test`, `min_mtu_config_test`, `min_mtu_traffic_test`; helpers `min_max_mtu_get_if`, `ensure_compatible_min_max_mtu`, `mtu_set_if`, `mtu_set_all_if`, `mtu_restore_all_if`, `mtu_test_ping4`, `mtu_test_ping6`.

Control flow: creates H1 VLAN 10 and switch VLAN 10, validates baseline IPv4/IPv6 pings, then for each netif tries exact min/max MTU and one out-of-range value. Traffic tests set all base and VLAN devices to shared min/max values and send no-fragment pings sized to the MTU.

State/persistence: creates one VRF, VLANs on both links, forwarding sysctls, and saves/restores MTU values through `MTU_ORIG`.

Dependencies/integration: depends on `ip -d -j link show` exposing `min_mtu`/`max_mtu`, `jq`, ping/ping6, and `lib.sh` MTU helpers.

Risks: incompatible min/max MTUs across the two interfaces produce xfail for traffic tests. IPv6 minimum MTU is intentionally not tested at min because IPv6 requires a higher floor. The script uses `ip li` abbreviation, accepted by iproute2.

Test signals: exact min/max MTU configuration succeeds, out-of-range fails, and pings sized to the configured limit pass or fail as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/min_max_mtu.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/mirror_gre.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/mirror_gre.sh

Purpose: Baseline mirror-to-GRE test for `tc action mirred egress mirror` targeting `gretap` and `ip6gretap` devices.

Important APIs/functions: `setup_prepare`, `test_span_gre_mac`, `test_two_spans`, `test_gretap`, `test_ip6gretap`, `test_gretap_mac`, `test_ip6gretap_mac`; imports mirror helper/topology libraries.

Control flow: builds standard mirror GRE topology, adds IPv4 and IPv6 underlay addresses between SW and H3, installs mirrors on `$swp1` ingress/egress, sends ICMP traffic between H1/H2, and verifies decapsulated packets on H3 tunnel devices. It also tests simultaneous ingress and egress mirrors to different tunnel types.

State/persistence: creates bridge topology, tunnel devices `gt4`/`gt6` and `h3-gt4`/`h3-gt6`, addresses, tc qdiscs/filters, and mirror actions. Cleanup removes addresses and topology.

Dependencies/integration: depends on `mirror_lib.sh`, `mirror_gre_lib.sh`, `mirror_gre_topo_lib.sh`, tc flower/matchall, and `MZ`.

Risks: mirror uninstall helper deletes from `$swp1` regardless of passed `from_dev`, which matches this topology but is a library coupling. Decap verification depends on tc counters on sink devices.

Test signals: ICMP type 8/0 counters on H3 tunnel devices, envelope MAC checks, and continued/failing counters as mirrors are installed/uninstalled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/mirror_gre.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/mirror_gre_bound.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/mirror_gre_bound.sh

Purpose: Tests mirror-to-`gretap`/`ip6gretap` when tunnel devices are bound to an underlay dummy device in a separate underlay VRF, modeling overlay/underlay separation.

Important APIs/functions: local topology helpers `h1_create`, `h2_create`, `h3_create`, `switch_create`; tests `test_gretap` and `test_ip6gretap`; helper functions from `mirror_gre_lib.sh`.

Control flow: builds H1/H2 bridge, H3 tunnel endpoints, underlay interface `$swp3`, dummy `ul`, overlay VRF `vrf-ol`, and bound tunnel devices `gt4`/`gt6`. Tests mirror ingress and egress on `$swp1` and verify decap on H3.

State/persistence: creates VRFs, bridge `br1`, dummy `ul`, tunnel devices, H3 sink qdiscs, tc mirror filters, and underlay addresses.

Dependencies/integration: relies on `tunnel_create ... dev ul`, VRF master assignment, and mirror helper assertions.

Risks: destroy order deletes `vrf-ol` before tunnels, so kernel behavior with enslaved devices matters. Bound-tunnel offload support is the likely target risk.

Test signals: mirrored ICMP request/reply traffic is captured on `h3-gt4` and `h3-gt6` for both ingress and egress directions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/mirror_gre_bound.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/mirror_gre_bridge_1d.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/mirror_gre_bridge_1d.sh

Purpose: Tests GRE mirroring when the underlay route points at an 802.1D bridge without VLAN filtering.

Important APIs/functions: `setup_prepare`, `cleanup`, `test_gretap`, `test_ip6gretap`; uses `mirror_gre_topo_create`, `full_test_span_gre_dir`, and manual neighbor replacement.

Control flow: creates standard GRE mirror topology, adds bridge `br2` over `$swp3`, routes GRE remote addresses via `br2`, assigns underlay addresses to `br2` and H3, and verifies gretap/ip6gretap ingress and egress mirroring.

State/persistence: creates `br2`, enslaves `$swp3`, adds IPv4/IPv6 routes and addresses, permanent neighbors during tests, and mirror tc filters.

Dependencies/integration: depends on bridge routing, neighbor entries, mirror helper libs, and tc counters.

Risks: route-to-bridge behavior and neighbor resolution are the focus. Cleanup deletes `br2`, implicitly dropping addresses/routes; explicit route removal is not performed.

Test signals: `full_test_span_gre_dir` observes expected ICMP request/reply on H3 tunnel devices for both tunnel families and directions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/mirror_gre_bridge_1d.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/mirror_gre_bridge_1d_vlan.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/mirror_gre_bridge_1d_vlan.sh

Purpose: Extends the 802.1D bridge underlay test by placing the bridge port over VLAN 555, verifying tagged underlay encapsulation and STP transitions.

Important APIs/functions: `test_vlan_match`, `test_gretap`, `test_ip6gretap`, `test_gretap_stp`, `test_ip6gretap_stp`; uses `full_test_span_gre_dir_vlan` and `full_test_span_gre_stp`.

Control flow: creates standard GRE topology, bridge `br2`, VLAN `$swp3.555` as bridge port, H3 VLAN endpoint, routes GRE remotes via bridge, then tests VLAN match on mirrored GRE traffic and disables/re-enables STP state to confirm mirroring follows bridge port state.

State/persistence: creates VLAN 555 devices, bridge `br2`, addresses/routes, permanent neighbors for STP tests, tc mirror filters, and VLAN capture filters.

Dependencies/integration: depends on bridge/VLAN behavior, ARP/ND neighbor validity, and mirror helper libraries.

Risks: comments note neighbor-state races after mirror installation; tests force permanent neighbors to stabilize STP checks. VLAN ethertype matching differs between IPv4 and IPv6 tunnels.

Test signals: VLAN capture on H3 sees GRE underlay packets with VLAN 555 when allowed; mirrored decap fails while bridge port is disabled and recovers when forwarding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/mirror_gre_bridge_1d_vlan.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/mirror_gre_bridge_1q.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/mirror_gre_bridge_1q.sh

Purpose: Tests GRE mirroring when the underlay route points at a VLAN-aware 802.1Q bridge.

Important APIs/functions: `setup_prepare`, `test_gretap`, `test_ip6gretap`; uses `mirror_gre_topo_create` and `full_test_span_gre_dir`.

Control flow: creates standard topology, temporarily brings `br1` down to adjust VLAN settings, enslaves `$swp3` to `br1`, adds VLAN 555 as bridge self PVID/untagged, assigns underlay addresses to `br1`, routes GRE remotes through it, and creates H3 VLAN 555 endpoint. Tests gretap and ip6gretap ingress/egress mirroring.

State/persistence: mutates existing `br1` from the standard topology, adds VLAN state, routes, H3 VLAN, permanent neighbors, and tc mirror filters.

Dependencies/integration: relies on Linux bridge VLAN filtering and route-to-bridge-device behavior.

Risks: changing bridge PVID while operational is avoided explicitly; cleanup delegates much state to topology destruction and only detaches `$swp3`/H3 VLAN.

Test signals: decapsulated ICMP counters on H3 tunnel endpoints for both GRE families and both mirror directions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/mirror_gre_bridge_1q.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/mirror_gre_bridge_1q_lag.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/mirror_gre_bridge_1q_lag.sh

Purpose: Tests mirror-to-gretap when a VLAN-aware bridge underlay egress is a team/LAG device in loadbalance mode.

Important APIs/functions: `vlan_host_create/destroy`, host helpers, `switch_create/destroy`, `test_lag_slave`, `test_mirror_gretap_first`, `test_mirror_gretap_second`; requires `teamd` and `arping`.

Control flow: creates two VLAN VRFs on `$h1` for H1/H2 roles, H3/H4 underlay receivers, bridge `br1`, team `lag` over `$swp3/$swp4`, route to GRE remote via bridge, and tunnel `gt4`. Each test downs one LAG slave, primes neighbor with arping, verifies mirror traffic reaches the active host, then downs both and verifies no mirror traffic.

State/persistence: creates VLANs 333/555, VRFs, bridge, team device, gretap, routes, forwarding sysctls, trap filters on H3/H4, and mirror/ARP tc filters.

Dependencies/integration: depends on `teamd`, `arping`, bridge/LAG driver behavior, tc counters, and mirror helpers.

Risks: LAG failover and neighbor priming are timing-sensitive. The topology reuses `$h1` for both logical H1 and H2 via VLANs, making route isolation critical.

Test signals: mirror counters on selected host device are `>=10` with one slave active and zero on both H3/H4 when neither slave is usable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/mirror_gre_bridge_1q_lag.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/mirror_gre_changes.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/mirror_gre_changes.sh

Purpose: Exercises dynamic configuration changes affecting mirror-to-gretap/ip6gretap offload and software behavior.

Important APIs/functions: `test_span_gre_ttl`, `test_span_gre_tun_up`, `test_span_gre_egress_up`, `test_span_gre_remote_ip`, `test_span_gre_tun_del`, `test_span_gre_route_del`, plus grouped tests `test_ttl`, `test_tun_up`, `test_egress_up`, `test_remote_ip`, `test_tun_del`, `test_route_del`.

Control flow: standard GRE mirror topology with underlay addresses. Tests install mirrors, then change tunnel TTL, tunnel up/down, egress port up/down, tunnel remote address, delete/recreate tunnel devices, and remove/readd underlay routes, checking mirroring fails and recovers as appropriate.

State/persistence: mutates tunnel attributes, interface state, routes, sysctl `net.ipv6.conf.$swp3.keep_addr_on_down`, and tc mirror/capture filters.

Dependencies/integration: uses `mirror_gre_topo_lib.sh`, `mirror_gre_lib.sh`, ping for neighbor resolution, and tc counters.

Risks: timing after link changes and neighbor resolution can cause flakiness; sleeps are used to stabilize. Recreating tunnels intentionally does not preserve existing mirror binding, so the test reinstalls the mirror.

Test signals: expected zero counters while bad/down/deleted/unrouted state is active and `>=10` counters after correcting the configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/mirror_gre_changes.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/mirror_gre_flower.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/mirror_gre_flower.sh

Purpose: Tests flower ACL-triggered mirroring to gretap/ip6gretap rather than matchall mirroring.

Important APIs/functions: `test_span_gre_dir_acl`, `fail_test_span_gre_dir_acl`, `full_test_span_gre_dir_acl`, `test_gretap`, `test_ip6gretap`.

Control flow: standard GRE topology plus secondary IPv4 addresses on H1/H2. Installs a mirror on `$swp1` with `protocol ip flower dst_ip <match>`, verifies default H1/H2 traffic is not mirrored, verifies traffic to the matched secondary address is mirrored, then uninstalls and verifies mirroring stops.

State/persistence: adds secondary host addresses, underlay addresses, tc flower mirror filters, and capture filters on H3 tunnel endpoints.

Dependencies/integration: depends on `tc flower dst_ip` matching, mirror helper libraries, and MZ-generated ICMP.

Risks: the test only matches IPv4 ACLs even for ip6gretap transport; this is intentional because payload is IPv4. Address overlap with baseline topology must be cleaned up.

Test signals: zero counters for unmatched traffic, positive counters for matched secondary-address traffic, and zero counters after mirror uninstall.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/mirror_gre_flower.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/mirror_gre_lag_lacp.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/mirror_gre_lag_lacp.sh

Purpose: Tests mirror-to-gretap when both switch and receiver underlay paths are LACP team devices and slave transmitability changes.

Important APIs/functions: `vlan_host_create/destroy`, `h3_create_team/destroy_team`, `h3_create/destroy`, `switch_create/destroy`, `test_lag_slave`, `test_mirror_gretap_first`, `test_mirror_gretap_second`.

Control flow: creates VLAN VRFs on `$h1`, LACP team `lag1` on SW, LACP team `lag2` on H3, gretap source `gt4` and destination `gt4-dst`, then installs a VLAN-filtered mirror. Each test removes one receiver slave from team membership, verifies mirroring through the remaining txable slave, removes the other, verifies no traffic, and rebuilds H3 team for next run.

State/persistence: creates two team devices, VRFs, VLANs, gretap devices, routes, tc qdiscs/capture filters, and mirror actions.

Dependencies/integration: requires `teamd`, LACP support, bridge-less routing via team devices, and tc VLAN capture on `gt4-dst`.

Risks: team membership changes are timing-sensitive; comments note mlxsw construction constraints requiring bottom-up team rebuild. This script lacks forwarding_enable because traffic is local/VLAN-routed within VRFs and GRE mirror underlay.

Test signals: `mirror_test` sees 10 mirrored ICMP packets on `gt4-dst` with one txable slave and zero when both slaves are detached.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/mirror_gre_lag_lacp.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/mirror_gre_lib.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/mirror_gre_lib.sh

Purpose: GRE-specific mirror assertion library layered on `mirror_lib.sh`. It standardizes tests against H3-side `h3-<tundev>` decapsulation devices.

Important APIs/functions: `quick_test_span_gre_dir_ips`, `fail_test_span_gre_dir_ips`, `test_span_gre_dir_ips`, `full_test_span_gre_dir_ips`, `full_test_span_gre_dir_vlan_ips`, `quick_test_span_gre_dir`, `fail_test_span_gre_dir`, `full_test_span_gre_dir`, `full_test_span_gre_dir_vlan`, `full_test_span_gre_stp_ips`, `full_test_span_gre_stp`.

Control flow: helpers install mirrors on `$swp1`, call generic span direction tests against `h3-$tundev`, optionally install VLAN capture filters on `$h3`, exercise traffic, uninstall mirrors, and log test names.

State/persistence: creates/removes tc mirror filters and capture filters; STP helper temporarily changes bridge port state disabled/forwarding.

Dependencies/integration: sources `mirror_lib.sh` via `$net_forwarding_dir`, expects globals `$swp1`, `$h1`, `$h2`, `$h3`, and tunnel names from topology scripts.

Risks: helpers assume mirror source is `$swp1` and H3 tunnel device naming convention `h3-<tundev>`. STP tests use sleeps and can be timing-sensitive.

Test signals: packet counter expectations from generic mirror helpers, VLAN capture counter expectations, and fail/pass transitions around STP state changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/mirror_gre_lib.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/mirror_gre_neigh.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/mirror_gre_neigh.sh

Purpose: Tests mirror-to-gretap/ip6gretap behavior when the tunnel remote neighbor entry is initially wrong and later refreshed.

Important APIs/functions: `test_span_gre_neigh`, `test_gretap`, `test_ip6gretap`, setup/cleanup from standard GRE topology.

Control flow: creates standard topology and underlay addresses. For each tunnel/direction, installs an intentionally invalid neighbor MAC for the GRE remote, installs mirror, verifies no decapsulated mirrored traffic, deletes the bad neighbor, verifies ARP/ND reinitialization makes mirroring work, then uninstalls mirror.

State/persistence: mutates neighbor table on `$swp3`, creates tc mirror/capture filters, and uses standard GRE tunnel/bridge state.

Dependencies/integration: depends on neighbor invalidation/refresh behavior, mirror helper counters, and both IPv4 and IPv6 neighbor handling.

Risks: neighbor re-resolution timing can be flaky; tests rely on the subsequent traffic generation to trigger resolution.

Test signals: zero mirrored packets with bad neighbor and positive counters after neighbor deletion for ingress and egress, gretap and ip6gretap.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/mirror_gre_neigh.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/mirror_gre_nh.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/mirror_gre_nh.sh

Purpose: Tests mirror-to-GRE when the tunnel remote endpoint is reachable through a next-hop route rather than a directly attached route.

Important APIs/functions: `setup_prepare`, `test_gretap`, `test_ip6gretap`; uses standard topology plus explicit remote endpoint addressing and routes.

Control flow: disables IPv4 rp_filter, assigns underlay transport addresses on a different subnet, assigns tunnel endpoint addresses to tunnel devices, and for IPv6 preinstalls a next-hop route. IPv4 test verifies no mirroring before adding the route to 192.0.2.130 via H3, then success after adding it. IPv6 test verifies success through preinstalled next-hop route.

State/persistence: mutates rp_filter sysctls, tunnel/underlay addresses, IPv4/IPv6 routes, tc mirror filters, and standard GRE topology state.

Dependencies/integration: relies on route resolution through next-hop and mirror offload updates for indirect remotes.

Risks: comments note IPv6 route ordering limitation for locally specified addresses. A cleanup call includes an extra argument to `sysctl_restore`, harmless in shell but easy to misread.

Test signals: IPv4 mirrored traffic fails before route add and passes after; IPv6 mirrored traffic passes with the configured next-hop route.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/mirror_gre_nh.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/mirror_gre_topo_lib.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/mirror_gre_topo_lib.sh

Purpose: Standard topology library for tests mirroring to `gretap` and `ip6gretap` netdevices.

Important APIs/functions: `mirror_gre_topo_h3_create/destroy`, `mirror_gre_topo_switch_create/destroy`, `mirror_gre_topo_create/destroy`; sources `mirror_topo_lib.sh`.

Control flow: reuses generic H1/H2/bridge topology, extends H3 with decapsulation tunnels `h3-gt4` and `h3-gt6`, and extends switch side with tunnel devices `gt4` and `gt6`. H3 tunnel devices are placed in `v$h3` and configured as matchall sinks for counter-based validation.

State/persistence: creates four tunnel devices, clsact/drop filters on H3-side tunnel devices, and the generic bridge/host topology from `mirror_topo_lib.sh`.

Dependencies/integration: depends on `tunnel_create`, `matchall_sink_create`, VRF created by generic H3 setup, and caller-assigned underlay addresses/routes.

Risks: tunnel devices are created before callers assign underlay addresses; tests must configure routes/addresses separately. Naming conventions are consumed by `mirror_gre_lib.sh`.

Test signals: not a standalone test; downstream tests observe counters on `h3-gt4`/`h3-gt6` after mirror actions to `gt4`/`gt6`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/mirror_gre_topo_lib.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/mirror_gre_vlan.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/mirror_gre_vlan.sh

Purpose: Tests mirror-to-gretap when the tunnel underlay route points at a VLAN device.

Important APIs/functions: `setup_prepare`, `cleanup`, `test_gretap`; imports standard GRE mirror topology and helpers.

Control flow: creates standard topology, adds VLAN 555 on `$swp3` and `$h3`, assigns underlay addresses to VLAN devices, routes GRE remotes via `$swp3.555`, then verifies ingress and egress mirroring to `gt4`.

State/persistence: creates VLAN devices, addresses, routes, tc mirror filters, and standard GRE topology state.

Dependencies/integration: depends on VLAN underlay encapsulation, gretap routing, and mirror helper counters.

Risks: only IPv4 gretap is listed in `ALL_TESTS`; IPv6 underlay address/route is configured but no ip6gretap test runs here. VLAN cleanup via link deletion removes addresses/routes implicitly.

Test signals: decapsulated ICMP request/reply counters on `h3-gt4` for ingress and egress mirror directions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/mirror_gre_vlan.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/mirror_gre_vlan_bridge_1q.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/mirror_gre_vlan_bridge_1q.sh

Purpose: Comprehensive GRE mirror test where the underlay route points at a VLAN upper over a VLAN-aware bridge, including forbidden VLAN, untagged egress, FDB roaming, and STP cases.

Important APIs/functions: `h3_addr_add_del`, `test_vlan_match`, `test_span_gre_forbidden_cpu`, `test_span_gre_forbidden_egress`, `test_span_gre_untagged_egress`, `test_span_gre_fdb_roaming`, `test_gretap_stp`, `test_ip6gretap_stp`, and tunnel-specific wrappers.

Control flow: disables rp_filter, creates standard GRE topology, creates `br1.555` underlay and H3 VLAN endpoint, attaches `$swp3`/`$swp2` to VLAN 555. Tests validate normal mirroring, remove/add bridge self VLAN, remove/add egress VLAN, toggle untagged egress and H3 address placement, force FDB entry to roam to wrong port, and test STP state.

State/persistence: mutates bridge VLAN tables, FDB entries, VLAN devices, routes, rp_filter sysctls, H3 addresses, tc mirror/capture filters, and neighbor/FDB priming via arping.

Dependencies/integration: requires `arping`, bridge VLAN filtering, GRE helper libraries, and tc counters.

Risks: FDB roaming loop retries when ARP/ND reprimes FDB mid-test. Several sleeps stabilize bridge/offload updates. rp_filter is disabled to avoid false failures for untagged egress.

Test signals: expected mirrored packet counters in normal states, zero counters when VLAN/FDB/STP forbids egress, VLAN capture presence/absence when toggling tagged versus untagged egress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/mirror_gre_vlan_bridge_1q.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/mirror_lib.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/mirror_lib.sh

Purpose: Generic mirroring test helper library for tc `mirred egress mirror` validation.

Important APIs/functions: `mirror_install`, `mirror_uninstall`, `is_ipv6`, `mirror_test`, `do_test_span_dir_ips`, `quick_test_span_dir_ips`, `test_span_dir_ips`, `test_span_dir`, `do_test_span_vlan_dir_ips`, `quick_test_span_vlan_dir_ips`, `fail_test_span_vlan_dir_ips`, `quick_test_span_vlan_dir`, `fail_test_span_vlan_dir`.

Control flow: installs tc mirror filters, sends mausezahn ICMP/ICMPv6 traffic from one VRF to another, reads tc rule counters before and after, and checks expected deltas. VLAN helpers install skip_hw VLAN capture filters to avoid double counting.

State/persistence: creates and deletes tc filters on source and capture devices. It relies on topology scripts for qdisc setup and device state.

Dependencies/integration: expects `tc_rule_stats_get`, `icmp_capture_install`, `vlan_capture_install`, `MZ`, and VRF names from `lib.sh`.

Risks: `mirror_uninstall` ignores its `from_dev` argument and always deletes from `$swp1`, so callers must use that convention. Counter comparisons rely on traffic timing and sleep.

Test signals: `mirror_test` checks exact or relational packet deltas and reports via `check_err`; higher-level helpers log direction and VLAN mirror outcomes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/mirror_lib.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/mirror_topo_lib.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/mirror_topo_lib.sh

Purpose: Generic three-host bridge topology for mirroring tests.

Important APIs/functions: `mirror_topo_h1_create/destroy`, `mirror_topo_h2_create/destroy`, `mirror_topo_h3_create/destroy`, `mirror_topo_switch_create/destroy`, `mirror_topo_create/destroy`.

Control flow: creates simple VRF-backed H1 and H2 addresses, H3 sink with clsact qdisc, bridge `br1` with VLAN filtering, `$swp1` and `$swp2` as bridged data ports, `$swp3` as mirror/underlay side port, and clsact on `$swp1`.

State/persistence: creates VRFs through `simple_if_init`, bridge `br1`, qdiscs on H3 and `$swp1`, and master relationships for switch ports.

Dependencies/integration: depends on `lib.sh` helpers and caller globals `h1`, `h2`, `h3`, `swp1`, `swp2`, `swp3`.

Risks: not standalone; callers must call `vrf_prepare` and assign globals. `mirror_topo_switch_destroy` deletes `br1`, implicitly removing bridge VLAN state that callers may add.

Test signals: downstream tests use this topology to generate mirror traffic and capture on H3 or derived devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/mirror_topo_lib.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/mirror_vlan.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/mirror_vlan.sh

Purpose: Tests mirroring to a VLAN device using the generic mirror topology, including tagged traffic preservation.

Important APIs/functions: `setup_prepare`, `test_vlan_dir`, `test_vlan`, `test_tagged_vlan_dir`, `test_tagged_vlan`.

Control flow: creates generic mirror topology, VLAN 555 on `$swp3` and `$h3`, matchall sink on `$h3.555`, VLAN 111 on H1/H2 data path, then mirrors ingress/egress traffic from `$swp1` to `$swp3.555`. Tagged tests verify VLAN 111 traffic appears on H3 VLAN device and not as VLAN 555 payload.

State/persistence: creates VLAN devices, bridge VLAN entries, trap filter on H3, matchall sink qdisc/filter, and tc mirror filters.

Dependencies/integration: uses `mirror_lib.sh`, `mirror_topo_lib.sh`, tc VLAN capture helpers, and VRF/ping helpers from `lib.sh`.

Risks: VLAN stacking/counter interpretation can differ across devices. Tagged test depends on skip_hw capture filters and correct bridge VLAN membership.

Test signals: ICMP direction counters on `$h3.555`, VLAN 111 capture count `>=10`, and VLAN 555 capture count zero for tagged mirror cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/mirror_vlan.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/no_forwarding.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/no_forwarding.sh

Purpose: Verifies traffic is not forwarded between disconnected switch ports under standalone, separate-bridge, and different-PVID bridge configurations.

Important APIs/functions: send helpers for non-IP, IPv4 unicast/multicast, IPv6 unicast/multicast; `check_rcv`, `run_test`, scenario functions `standalone`, `two_bridges`, `one_bridge_two_pvids`, and host setup helpers.

Control flow: builds H1/H2 VRF endpoints and switch ports, starts tcpdump on H2, sends untagged and many VLAN-tagged packet types from H1, stops tcpdump, and asserts none of the expected patterns were received. Scenarios change switch-side isolation but all should prevent forwarding.

State/persistence: creates VRFs, optional bridges `br0`/`br1`, VLAN devices over H1 for test packets, tcpdump temp files, and bridge VLAN entries.

Dependencies/integration: depends on tcpdump pattern output, mausezahn, ping/ping6, `ipv6_lladdr_get`, and `lib.sh`.

Risks: the `vids` array includes duplicate 1000, which repeats coverage but is harmless. Tcpdump output matching is fragile across versions. All tests expect non-forwarding, so any received pattern is a failure.

Test signals: every untagged and tagged unicast/multicast/broadcast/non-IP pattern lookup fails in tcpdump output, logged per packet type.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/no_forwarding.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/pedit_dsfield.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/pedit_dsfield.sh

Purpose: Tests tc pedit rewriting of IPv4 DS field and IPv6 traffic class, including full byte, DSCP-only, ECN-only, and DSCP+ECN chained edits.

Important APIs/functions: topology helpers; `do_test_pedit_dsfield_common`, `do_test_pedit_dsfield`, `do_test_ip_dsfield`, `do_test_ip_dscp`, `do_test_ip_ecn`, `do_test_ip_dscp_ecn`, `do_test_ip6_dsfield`, `do_test_ip6_dscp`, `do_test_ip6_ecn`; exported test wrappers.

Control flow: creates H1-H2 bridge through `$swp1/$swp2`, installs pedit filter at either ingress `$swp1` or egress `$swp2`, installs H2 ingress probe matching rewritten `ip_tos`, sends TCP packets with initial TOS 0x7d, waits for H2 counter, checks pedit rule counter, and removes filters.

State/persistence: creates bridge `br1`, VRFs, clsact qdiscs, pedit/flower filters, and optionally disables `bridge-nf-call-iptables`.

Dependencies/integration: imports `tc_common.sh` for `tc_rule_handle_stats_get`, uses `busywait`, `MZ`, and `lib.sh`.

Risks: `HIT_TIMEOUT` is defined but code uses `TC_HIT_TIMEOUT` from `tc_common.sh`; environment mismatch could affect waits. Exact traffic-class matching can be sensitive to checksum/offload behavior.

Test signals: H2 ingress sees at least 10 packets with expected DS/traffic-class bits and pedit rule counters increment at both ingress and egress loci.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/pedit_dsfield.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/pedit_ip.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/pedit_ip.sh

Purpose: Tests tc pedit rewriting of IPv4 and IPv6 source/destination addresses on bridge ingress and egress.

Important APIs/functions: `do_test_pedit_ip`, `do_test_pedit_ip4`, `do_test_pedit_ip6`, tests `test_ip4_src`, `test_ip4_dst`, `test_ip6_src`, `test_ip6_dst`.

Control flow: creates bridged H1-H2 topology, installs pedit action on `$swp1 ingress` or `$swp2 egress`, installs H2 ingress flower probe matching the rewritten address, sends 10 packets with mausezahn, waits for H2 counter, verifies pedit counter, and removes filters.

State/persistence: creates bridge `br1`, VRFs, clsact qdiscs, pedit/flower filters, and temporarily disables bridge netfilter if present.

Dependencies/integration: uses `tc_common.sh`, `busywait`, `tc_rule_handle_stats_get`, `MZ`, and `lib.sh`.

Risks: rewriting destination addresses to off-subnet values still relies on L2 delivery from mausezahn, not normal routing. Hardware pedit support may differ between ingress and egress.

Test signals: H2 ingress probe receives at least 10 packets with rewritten IPv4/IPv6 src or dst, and the pedit rule records at least 10 hits for both loci.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/pedit_ip.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/pedit_l4port.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/pedit_l4port.sh

Purpose: Tests tc pedit rewriting of TCP and UDP source/destination ports.

Important APIs/functions: `do_test_pedit_l4port_one`, `do_test_pedit_l4port`, exported tests `test_udp_sport`, `test_udp_dport`, `test_tcp_sport`, `test_tcp_dport`.

Control flow: creates bridged H1-H2 topology with clsact qdiscs, installs pedit on `$swp1 ingress` or `$swp2 egress`, installs H2 ingress flower probe matching rewritten L4 port, sends 10 UDP/TCP packets with initial `sp=54321,dp=12345`, and checks H2 and pedit counters.

State/persistence: creates bridge, VRFs, qdiscs, pedit filters, and H2 ingress probe filters. Cleanup removes topology and qdiscs.

Dependencies/integration: depends on `tc_common.sh` counter helpers, `MZ`, and kernel pedit support for TCP/UDP port fields.

Risks: `ALL_TESTS` omits `ping_ipv6` even though function exists; only IPv4 L4 pedit paths are tested. Checksums may be affected by offload but test validates tc-level field match.

Test signals: for ports 1, 11111, and 65535, H2 flower probes and pedit rule counters see at least 10 packets for each protocol/field/locus combination.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/pedit_l4port.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/q_in_vni.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/q_in_vni.sh

Purpose: Tests 802.1ad service VLAN bridging over a VXLAN VNI for IPv4 underlay, including local and two remote namespace VTEPs.

Important APIs/functions: `h1_create/destroy`, `h2_create/destroy`, `rp1_set_addr/unset_addr`, `switch_create/destroy`, `vrp2_create/destroy`, `ns_init_common`, `ns1_create/destroy`, `ns2_create/destroy`, `ping_ipv4`, `test_all`.

Control flow: creates H1/H2 VLAN subinterfaces, switch bridge `br1` with VLAN protocol 802.1ad and VXLAN `vx100`, route peer `rp2`, two veth-backed netns VTEPs each with bridge `br2`, VXLAN, and VLAN host side. Runs pings from H1 to local H2 and two remote namespace hosts.

State/persistence: creates VXLAN devices, bridges, VLANs, veth pairs, netns `ns1`/`ns2`, routes, FDB flood entries, tc qdiscs, forwarding sysctls, and exported `VXPORT`.

Dependencies/integration: depends on network namespaces, VXLAN, bridge VLAN filtering with 802.1ad, `in_ns` helper, and `lib.sh`.

Risks: cleanup must move veth peers back before deleting namespaces. VXLAN UDP port defaults to 4789 but can be overridden. Remote namespace helpers source `lib.sh` with `NUM_NETIFS=0`.

Test signals: pings from H1 to 192.0.2.2, 192.0.2.3, and 192.0.2.4 succeed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/q_in_vni.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/q_in_vni_ipv6.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/q_in_vni_ipv6.sh

Purpose: IPv6 version of the 802.1ad-in-VXLAN VNI test, using IPv6 underlay and IPv6 tenant addresses.

Important APIs/functions: mirrors `q_in_vni.sh` with IPv6 addresses; key functions include `switch_create`, `ns_init_common`, `ns1_create`, `ns2_create`, `ping_ipv6`, and `test_all`.

Control flow: builds local H1/H2 VLAN subinterfaces, bridge `br1` with VXLAN `vx100` using IPv6 local/remote addresses and zero-checksum options, peer router `rp2`, and two remote namespaces with their own bridges/VXLANs/VLAN host sides. Runs ping6 from H1 to local and remote tenant addresses.

State/persistence: creates IPv6 routes, VXLAN devices with `udp6zerocsumrx/tx`, netns, veth pairs, 802.1ad bridges, VLANs, tc qdiscs, FDB entries, and forwarding sysctls.

Dependencies/integration: depends on IPv6 VXLAN support, bridge VLAN filtering, namespace execution via `in_ns`, and `lib.sh`.

Risks: IPv6 zero-checksum options and route ordering can vary by kernel. As with IPv4, namespace cleanup depends on moving veth peers back to init netns.

Test signals: ping6 from H1 to 2001:db8:1::2, 2001:db8:1::3, and 2001:db8:1::4 succeeds, with test output including configured UDP port.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/q_in_vni_ipv6.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/router.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/router.sh

Purpose: Router forwarding selftest for edge-case IPv4/IPv6 forwarding and multicast behavior across two routed links.

Important APIs/functions: `h1_create/destroy`, `h2_create/destroy`, `router_create/destroy`, `start_mcd`, `kill_mcd`, `ping_ipv4`, `ping_ipv6`, `sip_in_class_e`, `create_mcast_sg`, `delete_mcast_sg`, `__mc_mac_mismatch`, `mc_mac_mismatch`, `ipv4_sip_equal_dip`, `ipv6_sip_equal_dip`, `ipv4_dip_link_local`, `ipv4_sip_link_local`.

Control flow: starts `smcrouted`, creates host VRFs and router interfaces, enables forwarding, validates basic IPv4/IPv6 reachability, then sends crafted UDP packets with unusual source/destination properties and uses tc egress filters on `$rp2` to assert forwarding. Multicast tests install S,G routes via `smcroutectl`.

State/persistence: creates VRFs, routes, addresses, clsact qdisc on `$rp2`, multicast daemon temp directory/config/pid, tc filters, neighbor entries, temporary routes, and rp_filter sysctl overrides.

Dependencies/integration: requires `$MCD` (`smcrouted`), `$MC_CLI`, `tc_common.sh`, mausezahn, and root privileges.

Risks: `kill_mcd` uses `pkill $MCD`, which may affect unrelated smcrouted processes. Tests disabling rp_filter must restore it. Multicast behavior depends on daemon availability and table name isolation.

Test signals: basic pings pass; tc counters see five forwarded packets for class-E source, multicast MAC mismatch, source-equals-destination, and IPv4 link-local source/destination cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/router.sh -->
