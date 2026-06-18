# subset-b-006863 Research

Grouped source research for Linux networking selftests covering VXLAN bridge and routing behavior, GRE, FQ packet limits, HSR/PRP redundancy, hardware timestamp ioctl configuration, and ICMP behavior. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/vxlan_asymmetric.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/vxlan_asymmetric.sh

## Purpose

This selftest builds an IPv4 asymmetric VXLAN routing topology with two bridge VLANs, two L2 VNIs, local and remote hosts, a routed underlay spine, and a peer switch inside `ns1`. It validates that the Linux bridge, VXLAN devices, SVIs, macvlan gateway addresses, static FDB entries, and external-learn neighbor entries support local and remote cross-subnet forwarding in an EVPN-like asymmetric model.

## Important APIs, Types, and Functions

The script is driven by kselftest forwarding helpers from `lib.sh`: `vrf_prepare`, `vrf_create`, `forwarding_enable`, `ping_test`, `mac_get`, `in_ns`, `tc_rule_stats_get`, and `tests_run`. Local helpers include `hx_create`/`hx_destroy` for host VRFs, `switch_create`/`switch_destroy`, `spine_create`/`spine_destroy`, namespace setup helpers, `macs_populate`, `macs_initialize`, `ping_ipv4`, `arp_decap`, `arp_suppression_compare`, and `arp_suppression`. It requires `$ARPING`.

## Control Flow

`setup_prepare` maps six test interfaces, enables VRF and forwarding support, creates the two local hosts, builds the local bridge/VXLAN/SVI switch, creates a veth underlay into `ns1`, builds a spine VRF between the local and namespace VTEPs, creates the remote namespace switch and hosts, then pre-populates FDB and neighbor state on both VTEPs. `tests_run` executes `ping_ipv4`, `arp_decap`, and `arp_suppression`; `trap cleanup EXIT` tears everything down in reverse order.

## State and Persistence Behavior

All state is ephemeral kernel networking state: VRFs, bridge `br1`, VXLAN devices `vx10` and `vx20`, VLAN devices, macvlans with the shared gateway MAC `00:00:5e:00:01:01`, static bridge FDB entries, external-learn neighbor entries, routes, veth pairs, `ns1`, and temporary `tc` filters. The script also changes IPv4 reverse-path filtering with `sysctl_set` and restores it with `sysctl_restore`.

## Dependencies and Integration Points

The test integrates with the forwarding kselftest framework, `iproute2`, bridge VLAN/FDB commands, ARP tooling, `tc flower`, VRF support, VXLAN, macvlan, network namespaces, and veth. It is a user-space regression probe for kernel bridge VXLAN decapsulation, ARP suppression, neighbor lookup, and external-learn FDB behavior.

## Risks and Edge Cases

The topology depends on exact static MAC and neighbor programming; missing cleanup can leave conflicting bridge/VXLAN objects. Hardware offload behavior can affect counter visibility, so the ARP suppression check focuses on `tc` rule deltas. `arp_decap` deliberately removes neighbors to force ARP decapsulation behavior. Reverse-path filtering must be disabled on the SVI/macvlan path or valid asymmetric traffic can be dropped.

## Test Signals

Passing signals are five IPv4 ping paths covering local-to-local, same-VLAN remote, and cross-VLAN remote traffic; successful ping after deleting SVI neighbors; and ARP suppression counter deltas of 0, 1, 2, and 3 for the four neighbor/suppression states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/vxlan_asymmetric.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/vxlan_asymmetric_ipv6.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/vxlan_asymmetric_ipv6.sh

## Purpose

This is the IPv6 counterpart of the asymmetric VXLAN routing test. It builds two L2 VXLAN segments over an IPv6 underlay, routes host traffic through VLAN SVIs and macvlan gateway addresses, and validates local, remote same-VLAN, and remote cross-VLAN connectivity.

## Important APIs, Types, and Functions

It uses `lib.sh` helpers for VRFs, namespace execution, ping, cleanup, forwarding, and MAC discovery, plus `$ARPING` even though the packet path uses IPv6 neighbor entries rather than ARP addresses. Local helpers mirror the IPv4 script: `hx_create`, `switch_create`, `spine_create`, `ns_switch_create`, `macs_populate`, `macs_initialize`, `ping_ipv6`, and `arp_decap`.

## Control Flow

`setup_prepare` assigns six interfaces, creates local host VRFs, creates the local bridge with `vx10` and `vx20`, sets IPv6 VTEP loopback routes through `rp1`/`rp2` and `v1`/`v2`, initializes `ns1`, enables forwarding in the namespace, and installs static FDB/neighbor entries. The test list runs `ping_ipv6` and `arp_decap`, then the exit trap destroys the namespace, spine, VXLANs, SVIs, VRFs, and forwarding state.

## State and Persistence Behavior

Runtime state is entirely temporary: IPv6 addresses and routes, VXLAN devices with `udp6zerocsumrx` and `udp6zerocsumtx`, VLAN bridge membership, macvlan gateway devices, static FDB entries, noarp external-learn neighbor entries, veth links, and netns `ns1`. No files are written.

## Dependencies and Integration Points

The test depends on IPv6 forwarding, Linux bridge VLAN filtering, VXLAN over IPv6, netns/veth, `ip neigh`, and kselftest forwarding helpers. It integrates with the kernel VXLAN and bridge datapath by validating that IPv6-encapsulated VXLAN traffic decapsulates and forwards correctly through VLAN-aware bridge and SVI routing constructs.

## Risks and Edge Cases

The namespace-side SVI setup uses the same IPv6 address on `vlan10`/`vlan10-v` and `vlan20`/`vlan20-v`, which makes the intended virtual gateway behavior sensitive to kernel duplicate-address handling and DAD suppression. Missing `udp6zerocsum*` support or disabled IPv6 forwarding causes false failures. Neighbor deletion in `arp_decap` intentionally stresses decapsulation of discovery traffic despite the IPv4-oriented function name.

## Test Signals

Success is all `ping6_test` calls passing for local and remote host pairs, followed by the same ping matrix passing after remote neighbor entries are removed and restored on the SVI devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/vxlan_asymmetric_ipv6.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/vxlan_bridge_1d.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/vxlan_bridge_1d.sh

## Purpose

This selftest validates VXLAN behavior on a non-VLAN-filtering 802.1D bridge over an IPv4 underlay. It covers host reachability, flooding to multiple remote VTEPs, static unicast FDB selection, tunnel TTL/TOS/ECN behavior, reapplying bridge/VTEP configuration in a different order, and dynamic VXLAN learning and aging.

## Important APIs, Types, and Functions

The script uses `lib.sh` helpers, `ip`, `bridge`, `tc`, `$MZ`, `ping_do`, `payload_template_calc_checksum`, `payload_template_expand_checksum`, `link_stats_rx_errors_get`, and namespace helpers. Major functions include `switch_create`, `vrp2_create`, `ns_init_common`, `reapply_config`, `vxlan_flood_test`, `test_flood`, `vxlan_fdb_add_del`, `test_unicast`, `vxlan_ping_test`, `test_ttl`, `test_tos`, `test_ecn_encap`, `vxlan_encapped_ping_do`, `test_ecn_decap`, and `test_learning`.

## Control Flow

Setup creates local hosts `h1`/`h2`, bridge `br1`, underlay routes through `rp1`/`rp2`, remote namespaces `ns1` and `ns2`, and VXLAN devices using multicast-like all-zero FDB entries for remote VTEPs. The default `ALL_TESTS` first validates base reachability and tunnel metadata, then calls `reapply_config` to detach VXLAN and underlay local IP state and reattach them before repeating flooding and unicast tests and running learning coverage.

## State and Persistence Behavior

The script creates temporary VRF and namespace networking state, `clsact` qdiscs, `tc flower` counters, bridge FDB entries, VXLAN device attributes, and generated traffic. `test_learning` temporarily enables VXLAN learning and short bridge/VXLAN aging timers, verifies learned self/master FDB entries, deletes and re-learns them, waits for aging, toggles bridge port learning, then restores nolearning and default aging.

## Dependencies and Integration Points

It integrates with the forwarding selftest harness, Linux bridge, VXLAN, veth, network namespaces, `tc`, `mausezahn`, ping, and ethtool-visible offload behavior. The test is sensitive to both pure software datapath and hardware offload paths because comments explicitly handle `skip_hw`/`skip_sw` counter behavior.

## Risks and Edge Cases

Counter tests tolerate small stray packet counts for ping-based checks but require exact flood/unicast distribution. Hardware offload can double-count trapped traffic, so the script dynamically chooses `skip_sw` or `skip_hw`. ECN decapsulation tests craft raw inner IPv4 packets and expect one invalid ECN combination to increment VXLAN RX errors. The 60-second learning aging phase is timing-sensitive.

## Test Signals

Signals include successful pings to local and both remote hosts, flood counters of 10 packets on all intended destinations, unicast counters only on the selected target, TTL 99 and TOS inheritance matches on egress, all ECN mapping cases, RX error accounting for invalid ECN decap, and learned FDB presence/deletion/aging behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/vxlan_bridge_1d.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/vxlan_bridge_1d_ipv6.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/vxlan_bridge_1d_ipv6.sh

## Purpose

This test validates an 802.1D bridge VXLAN topology where the VXLAN underlay is IPv6 while tenant payloads include both IPv4 and IPv6. It checks local switching, remote encapsulation/decapsulation through IPv6 VTEPs, flooding, static unicast forwarding, TTL/TOS inheritance, ECN handling, and configuration reapplication.

## Important APIs, Types, and Functions

It sources `lib.sh` and `tc_common.sh`. Important helpers include `rp1_set_addr`, `switch_create`, `ns_init_common`, `reapply_config`, `__ping_ipv4`, `__ping_ipv6`, `vxlan_flood_test`, `test_flood`, `vxlan_fdb_add_del`, `test_unicast`, `vxlan_ping_test`, `test_ttl`, `test_tos`, `test_ecn_encap`, `vxlan_encapped_ping_do`, and `test_ecn_decap`.

## Control Flow

Setup builds local hosts with IPv4 and IPv6 addresses, an IPv6 underlay through `rp1`/`rp2`, two remote namespaces connected by veth pairs, and one VXLAN device per bridge. Ping tests install `tc flower` counters on the underlay router and local switch port to prove encapsulated packets use the IPv6 VTEP path and decapsulated replies return through the bridge. After metadata tests, `reapply_config` detaches VXLAN from the bridge and removes/re-adds underlay addresses before repeating core checks.

## State and Persistence Behavior

The test owns temporary bridge, VXLAN, namespace, veth, route, address, `tc`, and FDB state. VXLAN devices use `udp6zerocsumrx`, `udp6zerocsumtx`, `tos inherit`, and `ttl 100`. No persistent files are changed.

## Dependencies and Integration Points

It depends on IPv6 VXLAN support, IPv4 and IPv6 ping tools, `tc_common.sh` packet counters, bridge FDB operations with IPv6 `dst`, and the Linux bridge/VXLAN datapath. It validates interaction between IPv6 underlay routing and L2 tenant forwarding.

## Risks and Edge Cases

The flood tests count ICMPv6 payloads and can be affected by neighbor discovery noise, so ping tests send 100 packets and require at least 100 counter hits. VXLAN ECN decap uses hand-crafted IPv6 inner headers, and the invalid outer CE plus inner non-ECT case must be reported as RX errors. Counter matching relies on hardware/software offload flags behaving as expected.

## Test Signals

Passing output includes IPv4 and IPv6 local/remote pings, underlay encapsulation and local decapsulation `tc` counter hits, exact flood and unicast distribution across local and remote VXLAN devices, TTL/TOS matches, ECN encapsulation mappings, ECN decapsulation mappings, and RX errors for the invalid ECN case.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/vxlan_bridge_1d_ipv6.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/vxlan_bridge_1d_port_8472.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/vxlan_bridge_1d_port_8472.sh

## Purpose

This wrapper reruns a focused subset of the IPv4 802.1D VXLAN bridge test with the non-default UDP destination port 8472. It exists to verify that VXLAN datapath setup and forwarding do not assume the IANA default port 4789.

## Important APIs, Types, and Functions

The file sets `VXPORT=8472`, overrides `ALL_TESTS` to only `ping_ipv4`, and sources `vxlan_bridge_1d.sh`. All topology creation and test functions are inherited from the sourced script.

## Control Flow

After variable assignment, control transfers to `vxlan_bridge_1d.sh`, whose main body creates the full 802.1D topology and runs `test_all`. Because `ALL_TESTS` is pre-set, only the IPv4 reachability matrix runs.

## State and Persistence Behavior

No state is owned directly by the wrapper. The sourced script creates and removes the bridge, VXLAN device, namespaces, routes, veths, qdiscs, and FDB entries, but all VXLAN device creation uses UDP port 8472.

## Dependencies and Integration Points

The wrapper depends on the sibling `vxlan_bridge_1d.sh` path being resolvable from the forwarding selftest directory. It integrates with the same kselftest forwarding and kernel VXLAN infrastructure while parameterizing only the UDP port.

## Risks and Edge Cases

Because the wrapper narrows `ALL_TESTS`, it validates reachability but not flood, unicast, ECN, TOS, TTL, or learning behavior on port 8472. Any change in the sourced script's top-level execution model can affect this wrapper.

## Test Signals

Success is the inherited `ping_ipv4` checks passing with `vx1` created as `dstport 8472`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/vxlan_bridge_1d_port_8472.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/vxlan_bridge_1d_port_8472_ipv6.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/vxlan_bridge_1d_port_8472_ipv6.sh

## Purpose

This wrapper runs the IPv6-underlay 802.1D VXLAN bridge test on UDP port 8472. It validates that both IPv4 and IPv6 tenant ping paths still work when the VXLAN tunnel endpoint uses the legacy/non-default port.

## Important APIs, Types, and Functions

The wrapper sets `VXPORT=8472`, restricts `ALL_TESTS` to `ping_ipv4` and `ping_ipv6`, and sources `vxlan_bridge_1d_ipv6.sh`. All functions and cleanup logic are inherited.

## Control Flow

The sourced script builds the IPv6 underlay topology and runs its normal top-level setup and `test_all`; the preconfigured test list limits execution to reachability checks.

## State and Persistence Behavior

Direct state is limited to exported shell variables. The sourced script creates the full temporary bridge/VXLAN/netns topology, with all VXLAN devices using destination port 8472.

## Dependencies and Integration Points

It depends on `vxlan_bridge_1d_ipv6.sh`, IPv6 VXLAN support, forwarding kselftest helpers, and `tc_common.sh`. The integration point is the VXLAN UDP port attribute across IPv6 underlay encapsulation and decapsulation.

## Risks and Edge Cases

The wrapper does not run the inherited flood, unicast, tunnel metadata, or ECN tests. It mainly guards against regressions where non-default VXLAN UDP ports break basic tunnel reachability.

## Test Signals

Success is inherited IPv4 and IPv6 tenant pings passing through a VXLAN device configured with `dstport 8472`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/vxlan_bridge_1d_port_8472_ipv6.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/vxlan_bridge_1q.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/vxlan_bridge_1q.sh

## Purpose

This selftest validates VXLAN devices attached to an 802.1Q VLAN-filtering bridge over an IPv4 underlay. VLAN 10 and VLAN 20 are mapped to separate VXLAN devices and VNIs, and the test verifies VLAN-scoped local switching, remote flooding, static unicast forwarding, VXLAN learning, FDB aging, and PVID/VLAN membership effects.

## Important APIs, Types, and Functions

The script uses `lib.sh`, `vlan_create`, bridge VLAN/FDB commands, `$MZ`, `tc`, and network namespace helpers. Key functions are `h1_create`, `h2_create`, `switch_create`, `ns_init_common`, `reapply_config`, `ping_ipv4`, `vxlan_flood_test`, `test_flood`, `vxlan_fdb_add_del`, `test_unicast`, `test_pvid`, `__test_learning`, and `test_learning`.

## Control Flow

Setup creates VLAN subinterfaces on local hosts, a VLAN-filtering `br1`, two VXLAN devices `vx10` and `vx20`, tagged local bridge ports, all-zero flood FDB entries for two remote VTEPs, remote namespaces with matching VLAN bridges and VXLAN devices, and cached remote MACs. The default test list runs reachability and flood/unicast checks, reapplies VXLAN/local-IP configuration, repeats checks, then tests learning and PVID mutation.

## State and Persistence Behavior

Temporary state includes VLAN subinterfaces, bridge VLAN membership, VXLAN devices, bridge FDB entries with VLAN-qualified master entries, `tc` qdiscs/counters, namespace veths, and generated packets. `test_learning` modifies VXLAN learning and aging timers, verifies self and VLAN-qualified bridge FDB entries, deletes entries, waits for aging, and restores nolearning/default timers.

## Dependencies and Integration Points

It integrates with Linux bridge VLAN filtering, VXLAN VNI mapping, bridge FDB learning, the forwarding kselftest library, mausezahn, `tc`, and network namespaces. It is a regression test for VLAN-aware bridge offload and software datapath behavior.

## Risks and Edge Cases

Flood counter logic temporarily marks the local destination VLAN untagged so the same ICMP filters can see local and VXLAN traffic. Hardware offload can affect `skip_sw`/`skip_hw` counter installation. PVID toggling verifies that removing PVID or deleting VLAN membership suppresses remote flooding without breaking local delivery. The learning age-out uses sleeps and can be timing-sensitive.

## Test Signals

Passing signals are VLAN 10 and 20 local/remote pings, exact flood distribution only to the matching VNI devices, static unicast delivery to one selected local or remote destination, learned FDB entry presence and aging, learning-off suppression of bridge FDB population, and PVID/VLAN deletion/re-addition affecting remote flooding as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/vxlan_bridge_1q.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/vxlan_bridge_1q_ipv6.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/vxlan_bridge_1q_ipv6.sh

## Purpose

This is the IPv6-underlay version of the VLAN-filtering VXLAN bridge test. It maps VLAN 10 and VLAN 20 to separate VXLAN devices over IPv6 VTEP addresses and validates IPv4 and IPv6 tenant traffic, VLAN-specific flooding, static unicast, reconfiguration, and PVID behavior.

## Important APIs, Types, and Functions

It sources `lib.sh` and `tc_common.sh`. Core functions include `switch_create`, `ns_init_common`, `reapply_config`, `__ping_ipv4`, `__ping_ipv6`, `ping_ipv4`, `ping_ipv6`, `vxlan_flood_test`, `test_flood`, `vxlan_fdb_add_del`, `test_unicast`, and `test_pvid`.

## Control Flow

Setup creates local VLAN subinterfaces carrying both IPv4 and IPv6 tenant addresses, configures IPv6 underlay routes, creates `vx10`/`vx20` with IPv6 zero-checksum receive/transmit support, and builds two remote namespaces with matching VLAN bridges and VXLAN devices. Ping tests install `tc` counters on `rp1` and `swp1` to prove encapsulated IPv6-underlay traffic and decapsulated VLAN tenant traffic traverse the expected devices. Tests are repeated after `reapply_config`.

## State and Persistence Behavior

The script uses temporary bridge, VLAN, VXLAN, veth, namespace, route, address, qdisc, and FDB state. It toggles bridge VLAN entries on `vx10` during `test_pvid`; it does not leave persistent filesystem state.

## Dependencies and Integration Points

It depends on IPv6 VXLAN support, bridge VLAN filtering, `tc` flower filters matching VLAN ethertypes, `tc_common.sh` packet threshold helpers, and standard forwarding selftest infrastructure. It validates the bridge/VXLAN interface between VLAN-aware L2 forwarding and IPv6 tunnel transport.

## Risks and Edge Cases

The script intentionally sends many ping packets to overcome ARP and neighbor-discovery noise. Counter matching for VLAN decapsulation uses `protocol 802.1q` with `vlan_ethtype`, which depends on correct `tc flower` support. The test does not include the dynamic learning coverage present in the IPv4 1Q script.

## Test Signals

Success is IPv4 and IPv6 local/remote ping coverage for VLAN 10 and 20, at least-threshold `tc` counter hits on encapsulated and decapsulated paths, flood counters only on devices in the matching VLAN/VNI, static unicast counters only on the target, and PVID/VLAN membership changes suppressing or restoring remote flooding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/vxlan_bridge_1q_ipv6.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/vxlan_bridge_1q_mc_ul.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/vxlan_bridge_1q_mc_ul.sh

## Purpose

This selftest validates VLAN-aware VXLAN flooding over multicast underlays for both IPv4 and IPv6 tunnel groups. It verifies how VXLAN `group`, `dev`, `mcroute`, and FDB `dst`/`via` settings interact with multicast routing entries for transmit and receive paths, including TX and RX using different logical interfaces.

## Important APIs, Types, and Functions

The script uses the `adf_` deferred-cleanup helper family from `lib.sh`, `mc_cli`, `adf_mcd_start`, `tc_rule_stats_get`, `$MZ`, and bridge/VXLAN commands. Major functions include `install_capture`, `switch_create`, `vx_create`, `vx10_create`, `vx20_create`, `ns_init_common`, `adf_install_broken_sg`, `adf_install_rx`, `adf_install_sg`, `adf_install_sg_sep`, `adf_install_sg_sep_rx`, `adf_install_starg`, `do_test`, `ipv4_do_test_rx`, and the many `ipv*_mcroute*` scenario functions.

## Control Flow

Setup creates a VLAN-filtering bridge on the switch, dummy interfaces `lo10` and `Xlo10`, local VLAN host interfaces, two remote bridge namespaces, and capture filters on remote host-facing links. Each scenario creates the relevant VXLAN device, optionally installs multicast routes, sends 10 VLAN-tagged UDP packets, and compares ingress capture deltas on H2 and H3. RX scenarios use pings to remote tenant hosts and assert whether the second remote host should respond.

## State and Persistence Behavior

Temporary state includes VRFs, bridge and VLAN devices, VXLAN multicast devices, dummy interfaces used as multicast route anchors, multicast daemon/client state, multicast route entries, FDB entries, `tc` filters, namespaces, and veth links. `defer` is used heavily so scenario-specific multicast routes and qdiscs are removed when the deferred cleanup scope ends.

## Dependencies and Integration Points

The test depends on multicast routing support, `mc_cli`, IPv4 and IPv6 VXLAN multicast groups, bridge VLAN filtering, FDB entries with `via`, dummy interfaces, and the kselftest forwarding environment. It directly exercises kernel VXLAN multicast route selection, especially when FDB entries supply the group destination or OIF is left to FIB lookup.

## Risks and Edge Cases

IPv6 OIF-zero behavior is sensitive to multicast route selection, so the script installs a `/128` multicast route to make the chosen device deterministic. Some tests intentionally install misleading `(S,G)` routes to ensure non-`mcroute` VXLAN does not follow them. `defer mc_cli remove` arguments must match installed routes; mismatches can leave test environment residue. RX tests distinguish absence of multicast routing from correctly routed flood delivery.

## Test Signals

Passing signals are exact H2/H3 capture deltas for IPv4 and IPv6 no-route, `(S,G)`, `(*,G)`, FDB-driven, OIF-zero, and separate TX/RX cases, plus ping success/failure expectations for RX scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/vxlan_bridge_1q_mc_ul.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/vxlan_bridge_1q_port_8472.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/vxlan_bridge_1q_port_8472.sh

## Purpose

This wrapper runs a focused IPv4 VLAN-filtering VXLAN bridge reachability test using UDP port 8472. It guards against regressions where non-default VXLAN ports break VLAN-to-VNI forwarding.

## Important APIs, Types, and Functions

The file sets `VXPORT=8472`, sets `ALL_TESTS` to `ping_ipv4`, and sources `vxlan_bridge_1q.sh`. All topology, cleanup, and ping helpers are inherited from the sourced script.

## Control Flow

After assigning variables, the sourced script executes its normal setup and top-level `test_all`; the inherited `tests_run` sees only the overridden ping test list.

## State and Persistence Behavior

The wrapper owns only shell variable state. The sourced script creates temporary VLAN subinterfaces, bridge/VXLAN devices, namespaces, FDB entries, routes, and qdiscs with the VXLAN devices configured for port 8472.

## Dependencies and Integration Points

It depends on the sibling `vxlan_bridge_1q.sh` file and the full forwarding selftest environment. Its integration point is the VXLAN `dstport` attribute in a VLAN-filtering bridge topology.

## Risks and Edge Cases

The wrapper only checks basic ping reachability, so deeper flood, unicast, learning, and PVID behavior on port 8472 is not covered here.

## Test Signals

Success is the inherited VLAN 10 and VLAN 20 IPv4 local and remote ping matrix passing with `vx10` and `vx20` using UDP port 8472.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/vxlan_bridge_1q_port_8472.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/vxlan_bridge_1q_port_8472_ipv6.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/vxlan_bridge_1q_port_8472_ipv6.sh

## Purpose

This wrapper runs the IPv6-underlay VLAN-filtering VXLAN bridge ping tests with destination UDP port 8472. It covers both IPv4 and IPv6 tenant pings over the non-default VXLAN port.

## Important APIs, Types, and Functions

The wrapper sets `VXPORT=8472`, overrides `ALL_TESTS` to `ping_ipv4` and `ping_ipv6`, and sources `vxlan_bridge_1q_ipv6.sh`.

## Control Flow

Execution is delegated to the sourced script after variable setup. The inherited setup creates the full IPv6-underlay 1Q topology and runs only the two reachability functions in the overridden test list.

## State and Persistence Behavior

No direct networking state is created in this file. The sourced script creates and destroys all bridge, VLAN, VXLAN, namespace, route, and qdisc state, with `vx10` and `vx20` using UDP port 8472.

## Dependencies and Integration Points

The wrapper depends on `vxlan_bridge_1q_ipv6.sh`, IPv6 VXLAN transport support, and forwarding kselftest helpers. It specifically integrates with the VXLAN port configuration path.

## Risks and Edge Cases

Flood, unicast, and PVID behavior are not run by this wrapper. It will not catch bugs isolated to those behaviors on port 8472.

## Test Signals

Success is inherited IPv4 and IPv6 VLAN 10/20 ping coverage passing through VXLAN devices configured with `dstport 8472`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/vxlan_bridge_1q_port_8472_ipv6.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/vxlan_reserved.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/vxlan_reserved.sh

## Purpose

This selftest verifies how a VXLAN device handles reserved bits in the VXLAN header. It crafts VXLAN UDP packets with clean and intentionally modified reserved bits, then checks whether packets are accepted or counted as VXLAN RX errors according to the device `reserved_bits` mask.

## Important APIs, Types, and Functions

The script uses `lib.sh`, `adf_` helpers, `tc`, `$MZ`, bridge/VXLAN commands, and link statistics. Important functions are `vxlan_header_bytes`, `neg_bytes`, `vxlan_ping_do`, `vxlan_device_add`, `vxlan_all_reserved_bits`, `vxlan_ping_vanilla`, `vxlan_ping_reserved`, `vxlan_ping_test`, `__default_test_do`, `default_test`, `plain_test`, and `reserved_test`.

## Control Flow

Setup creates a host, switch bridge, routed peer, and a VXLAN bridge port. Each test creates `vx1` with a particular `reserved_bits` attribute, sends 10 clean decapsulated ICMP packets and one packet for every reserved header bit, then compares ingress ICMP captures on the host and VXLAN RX error deltas. `in_defer_scope` ensures test-specific VXLAN devices and filters are removed.

## State and Persistence Behavior

Temporary state includes a bridge, VXLAN device, host ingress drop/counter filter, FDB/bridge membership, underlay routes, and crafted packets. No persistent storage is used.

## Dependencies and Integration Points

The test depends on `mausezahn` for byte-level packet crafting, `tc` ingress counters, bridge/VXLAN support, and link RX error statistics. It integrates directly with the kernel VXLAN parser and `reserved_bits` netlink attribute behavior.

## Risks and Edge Cases

The bit numbering is manually encoded into an 8-byte VXLAN header, with bit 4 always treated as the I flag and bits 32-55 as VNI. A mismatch between test bit numbering and kernel semantics would invalidate expectations. The default case expects all 39 non-I/non-VNI bits to be rejected, while selected masks allow exactly one reserved bit.

## Test Signals

Passing signals are 10 accepted clean packets, expected accepted reserved-bit packet counts of 0 or 1 depending on mask, and RX error deltas equal to rejected packet counts for default, plain mask, and selected bit masks 0, 10, 31, 56, and 63.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/vxlan_reserved.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/vxlan_symmetric.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/vxlan_symmetric.sh

## Purpose

This selftest builds an IPv4 symmetric VXLAN routing topology. Unlike the asymmetric test, same-subnet traffic uses L2 VNIs while routed cross-subnet remote traffic uses a separate L3 VNI on VLAN 4001 with static routes through the remote VTEP.

## Important APIs, Types, and Functions

It uses forwarding helpers from `lib.sh` and local helpers `hx_create`, `switch_create`, `spine_create`, `ns_switch_create`, `__l2_vni_init`, `l2_vni_init`, `__l3_vni_init`, `l3_vni_init`, and `ping_ipv4`. It configures `vx10`, `vx20`, and `vx4001`.

## Control Flow

`setup_prepare` creates local hosts and switch, an underlay veth to `ns1`, a spine VRF, remote namespace hosts and switch, then installs L2 VNI FDB/neighbor entries and L3 VNI FDB/neighbor/route entries on both VTEPs. `ping_ipv4` validates local switching, same-VLAN remote traffic, and cross-VLAN remote traffic. Cleanup removes the namespace, spine, VTEP, bridge, VRF, and host state.

## State and Persistence Behavior

The script creates temporary bridge/VXLAN/SVI/macvlan/VRF/netns state. L3 VNI state includes `vlan4001`, `vx4001`, static FDB entries for the remote L3 VNI MAC, noarp neighbor entries for VTEP IPs on `vlan4001`, and per-host `/32` routes in `vrf-green` via the remote VTEP.

## Dependencies and Integration Points

It depends on bridge VLAN filtering, VXLAN, VRF routing, macvlan gateway addresses, veth namespaces, IPv4 routing, and the forwarding kselftest framework. It exercises the kernel path where bridged L2 VXLAN and routed L3 VNI traffic coexist on the same bridge.

## Risks and Edge Cases

Static programming must match both local and namespace MACs exactly. The L3 VNI has no `remote` argument on creation; delivery relies on FDB entries and routes. Reverse-path filtering is disabled for SVI/macvlan devices to avoid drops in the symmetric routing path.

## Test Signals

Success is the five IPv4 ping checks passing: local-to-local, remote same-VLAN for both VLANs, and remote cross-VLAN in both directions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/vxlan_symmetric.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/vxlan_symmetric_ipv6.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/vxlan_symmetric_ipv6.sh

## Purpose

This is the IPv6 symmetric VXLAN routing test. It validates L2 VNIs for same-subnet traffic and an L3 VNI on VLAN 4001 for routed remote IPv6 host routes across IPv6 VTEP endpoints.

## Important APIs, Types, and Functions

The script uses `lib.sh` helpers plus local functions mirroring the IPv4 symmetric test: `hx_create`, `switch_create`, `spine_create`, `ns_switch_create`, `__l2_vni_init`, `l2_vni_init`, `__l3_vni_init`, `l3_vni_init`, and `ping_ipv6`. VXLAN devices use `udp6zerocsumrx` and `udp6zerocsumtx`.

## Control Flow

Setup creates local and namespace hosts, VLAN-aware bridges, `vx10`, `vx20`, `vx4001`, IPv6 underlay routes through a spine VRF, and static L2 and L3 VNI programming. It also enables forwarding inside `ns1`. The only test function runs the five IPv6 ping paths, then cleanup reverses the topology.

## State and Persistence Behavior

Temporary state includes IPv6 addresses, routes, bridge VLAN entries, VXLAN devices, VRFs, macvlans, noarp external-learn neighbor entries, static bridge FDB entries, and host routes with `/128` prefixes through `vlan4001`.

## Dependencies and Integration Points

It depends on IPv6 routing and forwarding, VXLAN over IPv6, bridge VLAN filtering, VRFs, macvlan, and kselftest forwarding helpers. It verifies kernel integration of IPv6 VXLAN L2 and L3 VNI datapaths.

## Risks and Edge Cases

The namespace-side SVI/macvlan addresses intentionally overlap on each VLAN, so DAD and forwarding settings are important. L3 VNI route correctness depends on exact `/128` routes and VTEP neighbor entries. A missing IPv6 forwarding enable in the namespace would break remote routed paths.

## Test Signals

Success is all `ping6_test` calls passing for local, remote same-VLAN, and remote cross-VLAN paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/vxlan_symmetric_ipv6.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/fq_band_pktlimit.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/fq_band_pktlimit.sh

## Purpose

This selftest verifies that the `fq` qdisc enforces its packet limit per band rather than globally. It queues delayed IPv6 UDP packets into one priority band, fills that band, then sends traffic in a different priority band to prove it has its own quota.

## Important APIs, Types, and Functions

The script uses `in_netns.sh`, `ip`, `tc`, and the local `cmsg_sender` helper with `SO_TXTIME`. The only local helper is `die`, which reports a failed expectation and exits nonzero.

## Control Flow

If invoked without arguments, the script re-executes itself inside a private namespace. In the subprocess, it creates `dummy0`, assigns an IPv6 route, installs `tc qdisc ... fq ... limit 10`, sends three batches of 20 delayed packets, captures `tc -s qdisc` output after each batch, sleeps past the delay, captures final stats, prints all stats, and greps for expected sent/drop counts.

## State and Persistence Behavior

State is isolated to the private namespace: a dummy link, IPv6 address and route, `fq` qdisc state, delayed queued packets, and qdisc statistics. No persistent files are modified.

## Dependencies and Integration Points

It depends on `in_netns.sh`, `cmsg_sender`, IPv6, dummy netdev, `tc fq`, and `SO_TXTIME` scheduling. It integrates with the kernel fair queueing scheduler and packet priority band selection.

## Risks and Edge Cases

The test assumes delayed packets remain queued while subsequent batches are sent; timing is controlled by a 400000 microsecond delay and 0.6 second sleep. Grep-based statistic matching depends on stable `tc -s qdisc` output formatting. If `cmsg_sender` cannot set the desired priority or txtime, band isolation will not be tested correctly.

## Test Signals

Expected stats are 10 drops after the first 20 packets in one band, 30 drops after another 20 in the same band, 40 drops after sending 20 in priority band 7, and finally 20 packets sent with 40 dropped after queued packets become eligible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/fq_band_pktlimit.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/gre_gso.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/gre_gso.sh

## Purpose

This selftest verifies GRE over IPv6 GSO/TSO behavior by copying a large random file through GRE tunnel endpoints and checking that TCP transfer succeeds with both TSO enabled and disabled.

## Important APIs, Types, and Functions

It sources `lib.sh` and defines `setup`, `cleanup`, `get_linklocal`, `gre_create_tun`, `gre_gst_test_checks`, `gre6_gso_test`, `gre_gso_test`, `usage`, and `log_test`. It uses `ip tunnel`, `socat`, `ss`, `ethtool -K tso`, `dd`, `timeout`, and namespace helpers.

## Control Flow

The main parser handles `-t`, pause, and verbose flags, validates root and required commands, cleans stale state, then runs `gre_gso_test`. That creates a namespace and veth pair, generates a 2 MiB random file, derives link-local IPv6 addresses on both veth endpoints, creates matching `ip6gre` tunnels, assigns IPv4 and IPv6 addresses to the tunnel, starts a `socat` listener in the namespace, copies the file with TSO enabled, disables TSO on the outer veth, copies again to exercise GSO, restores TSO, and cleans up.

## State and Persistence Behavior

Temporary state includes a namespace, veth pair, `gre1` tunnel devices in both namespaces, tunnel IP addresses, a random temporary file, a background `socat` listener PID, and ethtool TSO feature state on `veth0`. Cleanup removes the temp file, kills the listener, deletes links, and removes the namespace.

## Dependencies and Integration Points

The test depends on root, `ip`, `socat`, `ss`, `ethtool`, GRE/IP6GRE kernel support, veth link-local IPv6 addresses, and the kselftest namespace helpers. It integrates with the kernel GRE tunnel, segmentation offload, and TCP data paths.

## Risks and Edge Cases

The listener readiness loop increments an undeclared `i` and has no explicit timeout, so a failed listener can hang. `timeout 1 socat` assumes the file transfer completes quickly. Link-local address discovery must succeed on both veth endpoints. The cleanup kills `$PID` if set, which is important after failed transfers.

## Test Signals

Success is two `log_test` OK entries for GREv6 carrying IPv4 and two for GREv6 carrying IPv6: one copy with TSO and one copy with software GSO after disabling TSO.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/gre_gso.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/gre_ipv6_lladdr.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/gre_ipv6_lladdr.sh

## Purpose

This selftest verifies IPv6 link-local address generation and multicast route creation on GRE and GRETAP devices for multiple address-generation modes and underlay endpoint combinations.

## Important APIs, Types, and Functions

The script sources `lib.sh` and defines `exit_cleanup_all`, `setup_basenet`, `check_ipv6_device_config`, `test_gre_device`, `test_gre4`, `test_gre6`, and `usage`. It uses `ip link add type gre/ip6gre/gretap/ip6gretap`, per-interface `net.ipv6.conf.*.addr_gen_mode`, `stable_secret`, and route/address inspection.

## Control Flow

The script creates one namespace, enables loopback underlay addresses, then tests IPv4-underlay GRE and GRETAP and IPv6-underlay IP6GRE and IP6GRETAP. For each tunnel type, it iterates `eui64`, `none`, `stable-privacy`, and `random` modes across fixed local/remote and `any` endpoint combinations. Each device is brought up, checked, brought down, link-local generation is disabled and then re-enabled while up, checked again, and deleted.

## State and Persistence Behavior

All state is temporary inside `NS0`: loopback underlay addresses, one `gretest` device at a time, sysctl values for `addr_gen_mode` and `stable_secret`, link-local addresses, and kernel local multicast routes. The exit trap removes the namespace.

## Dependencies and Integration Points

It depends on GRE, IP6GRE, GRETAP, IP6GRETAP, IPv6 sysctl support, namespace helpers, and kernel local multicast route generation. It integrates with IPv6 interface address generation logic for tunnel netdevices.

## Risks and Edge Cases

The `none` mode expects no link-local address but still expects the ff00::/8 multicast route to exist. Stable privacy mode requires a configured `stable_secret`. The test uses grep matching for `stable-privacy` in address output, so output format changes can affect it.

## Test Signals

Each scenario logs two checks: initial configuration after link-up and update after re-enabling generation on an already-up device. Success means expected presence or absence of `fe80::` and presence of an ff00::/8 local multicast route for `gretest`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/gre_ipv6_lladdr.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/hsr/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/hsr/Makefile

## Purpose

This kselftest Makefile registers the HSR/PRP network selftest scripts and shared helper file with the top-level selftests build/run framework.

## Important APIs, Types, and Functions

It sets `top_srcdir`, defines `TEST_PROGS` as `hsr_ping.sh`, `hsr_redbox.sh`, `link_faults.sh`, and `prp_ping.sh`, adds `hsr_common.sh` to `TEST_FILES`, and includes `../../lib.mk`.

## Control Flow

There is no runtime control flow. `lib.mk` consumes the `TEST_PROGS` and `TEST_FILES` variables to install or run the scripts as part of kselftest.

## State and Persistence Behavior

The file only affects build metadata. It does not create runtime network state.

## Dependencies and Integration Points

It integrates the HSR tests with kselftest infrastructure and ensures the common shell helper is copied with the test programs.

## Risks and Edge Cases

Adding a script without listing it in `TEST_PROGS` would omit it from kselftest runs. Removing `hsr_common.sh` from `TEST_FILES` would break installed test execution outside the source tree.

## Test Signals

Build/install signals are that `make -C tools/testing/selftests/net/hsr` includes all four scripts and the common helper in the generated test set.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/hsr/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/hsr/config -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/hsr/config

## Purpose

This config fragment declares kernel configuration requirements for the HSR/PRP selftests.

## Important APIs, Types, and Functions

It requests `CONFIG_BRIDGE=y`, `CONFIG_HSR=y`, `CONFIG_IPV6=y`, `CONFIG_NET_SCH_NETEM=m`, `CONFIG_VETH=y`, and `CONFIG_VLAN_8021Q=m`.

## Control Flow

There is no executable control flow. The selftest build or configuration tooling reads these symbols as prerequisites.

## State and Persistence Behavior

The file is static metadata and owns no runtime state.

## Dependencies and Integration Points

It integrates with kselftest configuration checking. The listed options map directly to HSR/PRP device creation, veth namespaces, bridge RedBox tests, IPv6 ping tests, VLAN subinterface tests, and netem fault injection.

## Risks and Edge Cases

If a symbol is missing or built incompatibly, scripts may skip, fail during setup, or fail only in optional phases such as VLAN or netem fault tests. Module symbols require loadable module availability at runtime.

## Test Signals

A configured kernel satisfying these symbols should be able to create the topologies used by the HSR test scripts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/hsr/config -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/hsr/hsr_common.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/hsr/hsr_common.sh

## Purpose

This shell library provides shared helpers for HSR and PRP kselftests: IP version detection, short ping checks, longer duplicate/loss-sensitive ping checks, failure stopping, and prerequisite validation.

## Important APIs, Types, and Functions

It sources `../lib.sh`, initializes `ret` and `ksft_skip`, and defines `is_v6`, `do_ping`, `do_ping_long`, `stop_if_error`, and `check_prerequisites`. It expects caller-defined namespace variables and an `ipv6` boolean.

## Control Flow

Callers source this file, then use `check_prerequisites`, create namespaces/topologies, and call `do_ping` or `do_ping_long`. IPv6 pings are skipped when `ipv6=false`; failures set global `ret=1`, and `stop_if_error` exits if any previous check failed.

## State and Persistence Behavior

It owns only shell variables and returns. It does not create network state directly, but its ping helpers observe connectivity and duplicate/loss behavior in caller-created namespaces.

## Dependencies and Integration Points

It depends on `../lib.sh`, `ip`, `ping`, namespace names from `setup_ns`, and the kselftest return code convention. It is the shared integration layer for `hsr_ping.sh`, `hsr_redbox.sh`, and `prp_ping.sh`.

## Risks and Edge Cases

`do_ping_long` parses localized ping output after forcing `LANG=C`, but format changes can still break duplicate/loss detection. The sed expression expects two-digit transmitted/received fields for 10-packet runs. IPv6 checks silently return success when IPv6 is disabled, which is intentional for `-4` modes.

## Test Signals

Signals are process return codes from ping, exact long-ping parsing for `10 transmitted 10 received 0% loss`, and `ret` remaining zero across caller test phases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/hsr/hsr_common.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/hsr/hsr_ping.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/hsr/hsr_ping.sh

## Purpose

This selftest verifies basic HSRv0 and HSRv1 connectivity in a three-node redundant ring, including optional VLAN-over-HSR connectivity. It checks both IPv4 and IPv6 unless `-4` disables IPv6.

## Important APIs, Types, and Functions

It sources `hsr_common.sh` and defines `usage`, `do_ping_tests`, `setup_hsr_interfaces`, `setup_vlan_interfaces`, `run_ping_tests`, and `run_vlan_tests`. It uses `ip link add type hsr`, veth pairs, explicit slave MAC addresses, VLAN subinterfaces, `ethtool -k` for `vlan-challenged`, and the common ping helpers.

## Control Flow

The script parses options, checks prerequisites, traps namespace cleanup, then creates three namespaces. It sets up HSRv0, runs base and VLAN tests, recreates namespaces, sets up HSRv1, and repeats the same tests. `do_ping_tests` first checks pairwise short pings, waits for debugfs HSR node table merge, then runs longer pings to detect duplicates or loss.

## State and Persistence Behavior

Runtime state includes namespaces `ns1`/`ns2`/`ns3`, three veth links forming a ring, `hsr1`/`hsr2`/`hsr3`, IPv4/IPv6 addresses, optional VLAN devices `hsr*.2`, and debugfs node table observations. Cleanup removes namespaces.

## Dependencies and Integration Points

It depends on HSR kernel support, veth, IPv6, VLAN support, debugfs HSR node tables, `ethtool`, and the selftest namespace library. It integrates with kernel HSR duplicate discard and supervision frame processing.

## Risks and Edge Cases

The wait for merged node table entries uses `/sys/kernel/debug/hsr/hsr*/node_table`; missing debugfs or changed output can cause timing issues. VLAN tests run only when any queried HSR device reports `vlan-challenged` as `off`. The IPv6 ns3-to-ns2 initial ping appears to target `dead:beef:$netid::2`, duplicating one pair, which may reduce matrix coverage.

## Test Signals

Success is all short and long IPv4/IPv6 pings passing for HSRv0 and HSRv1, no duplicate packets in 10-packet long pings, and optional VLAN ping tests passing when supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/hsr/hsr_ping.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/hsr/hsr_redbox.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/hsr/hsr_redbox.sh

## Purpose

This selftest validates HSR RedBox behavior, where an HSR node with an interlink connects a redundant HSR network to singly attached nodes through a bridge. It focuses on IPv4 connectivity between HSR nodes and SAN-side hosts.

## Important APIs, Types, and Functions

It sources `hsr_common.sh` with `ipv6=false` and defines `do_complete_ping_test` and `setup_hsr_interfaces`. It uses `ip link help hsr` to check for `INTERLINK`, veth pairs, a bridge in `ns3`, `ip link add type hsr ... interlink`, and common ping helpers.

## Control Flow

The script checks prerequisites, creates five namespaces, sets up HSRv1 with `ns2` as the RedBox containing `hsr2` and interlink `ns2eth3`, builds a bridge in `ns3` to SAN hosts `ns4` and `ns5`, then runs short connectivity pings, waits for HSR management frames, and runs long pings between SAN and HSR endpoints.

## State and Persistence Behavior

Temporary state includes five namespaces, five veth pairs, bridge `ns3br1`, HSR devices `hsr1` and `hsr2`, an HSR interlink, fixed MAC addresses, and IPv4 addresses. Cleanup removes all namespaces.

## Dependencies and Integration Points

It depends on HSR interlink support in iproute2 and the kernel, bridge support, veth, and HSR duplicate filtering. It integrates with the RedBox path between HSR and standard Ethernet segments.

## Risks and Edge Cases

If `ip link help hsr` lacks `INTERLINK`, the script exits 0 rather than using the kselftest skip code. The five-second wait is a fixed delay rather than an explicit node table condition. Shared MAC assignment on `ns3` bridge ports models bridge behavior but can obscure debugging if the topology changes.

## Test Signals

Success is short pings among HSR and SAN endpoints, followed by long pings with no loss or duplicates between SAN hosts and `hsr1` through the RedBox.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/hsr/hsr_redbox.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/hsr/link_faults.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/hsr/link_faults.sh

## Purpose

This selftest validates HSRv0, HSRv1, and PRP resilience under clean operation, a live link cut, packet loss, high packet loss, and packet reordering. It uses rapid pings to verify zero packet loss and bounded duplicate delivery during fault recovery.

## Important APIs, Types, and Functions

The script sources `../lib.sh` and defines `setup_hsr_topo`, `setup_prp_topo`, `wait_for_hsr_node_table`, `setup_topo`, `check_ping`, `test_clean`, `test_cut_link`, `test_packet_loss`, `test_reordering`, protocol-specific wrappers, and `cleanup`. It uses `ip link add type hsr`, veth, `tc netem`, debugfs HSR node tables, and `tests_run`.

## Control Flow

`tests_run` executes all protocol/fault combinations in `ALL_TESTS`. Each test creates a fresh topology, waits for HSR node table merge when needed, injects the fault if any, runs `check_ping` from node1 to node2 with 400 pings at 10 ms intervals, parses duplicate and loss counts, and logs the result. Cleanup removes namespaces between tests through the exit trap and `pre_cleanup` behavior in the harness.

## State and Persistence Behavior

State is temporary namespaces, veth links, HSR/PRP devices, IPv4 addresses, debugfs observations, and netem qdiscs on selected links. Fault tests add delay/loss/reorder qdiscs or bring one link down during ping.

## Dependencies and Integration Points

It depends on HSR, PRP mode through `proto 1`, veth, `tc netem`, debugfs HSR node table, and kselftest logging. It integrates with kernel duplicate discard, supervision table merging, and redundant path failover.

## Risks and Edge Cases

`check_ping` parses human ping output for duplicates and packet loss. The accepted duplicate threshold is 40 for impairment tests and 0 for clean/cut-link tests. Timing is important: the fault is injected two seconds into a five-second ping run, and netem delay must create a queue for reordering.

## Test Signals

Passing signals are zero packet loss for all tests, duplicates not exceeding the configured threshold, and successful node table merge before HSR tests proceed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/hsr/link_faults.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/hsr/prp_ping.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/hsr/prp_ping.sh

## Purpose

This selftest verifies basic PRP connectivity between two nodes connected by two parallel LANs, including optional VLAN-over-PRP connectivity. It checks IPv4 and IPv6 unless `-4` is supplied.

## Important APIs, Types, and Functions

It sources `hsr_common.sh` and defines `usage`, `setup_prp_interfaces`, `setup_vlan_interfaces`, `do_ping_tests`, `run_ping_tests`, and `run_vlan_ping_tests`. It creates PRP devices through `ip link add type hsr ... proto 1`.

## Control Flow

The script parses options, checks prerequisites, creates two namespaces, adds parallel veth pairs `vethA` and `vethB`, creates `prp1` and `prp2`, assigns IPv4/IPv6 addresses, brings links up, runs base ping tests, then conditionally creates VLAN subinterfaces and repeats the ping tests for network id 2.

## State and Persistence Behavior

Temporary state includes namespaces `node1` and `node2`, two veth pairs, PRP devices, IPv4/IPv6 addresses, optional VLAN devices `prp1.2` and `prp2.2`, and ping-observed connectivity state. Cleanup removes namespaces.

## Dependencies and Integration Points

It depends on HSR driver PRP mode, veth, IPv6, VLAN support, `ethtool`, and the shared HSR common helpers. It validates the kernel PRP duplicate handling and LAN A/B redundancy in a minimal topology.

## Risks and Edge Cases

VLAN tests run only if either PRP device reports non-`vlan-challenged`; that condition may be broad if one side supports VLAN and the other does not. MAC addresses are explicitly set only on LAN A and copied by PRP semantics. Long ping parsing inherits the common helper's output-format assumptions.

## Test Signals

Success is short and long IPv4/IPv6 pings in both directions with no duplicate/loss indication, plus optional VLAN ping success when supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/hsr/prp_ping.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/hwtstamp_config.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/hwtstamp_config.c

## Purpose

This small C utility gets or sets a network interface hardware timestamping configuration through `SIOCGHWTSTAMP` and `SIOCSHWTSTAMP`. It is a kselftest helper for exercising the kernel hwtstamp ioctl ABI.

## Important APIs, Types, and Functions

Important functions are `lookup_value`, `lookup_name`, `list_names`, `usage`, and `main`. It uses `struct ifreq`, `struct hwtstamp_config`, `socket(AF_INET, SOCK_DGRAM, 0)`, and `ioctl` with `SIOCGHWTSTAMP` or `SIOCSHWTSTAMP`. It maps names for `HWTSTAMP_TX_OFF`, `HWTSTAMP_TX_ON`, `HWTSTAMP_TX_ONESTEP_SYNC`, and the supported `HWTSTAMP_FILTER_*` values.

## Control Flow

`main` validates either `if_name` alone or `if_name tx_type rx_filter`, parses names case-insensitively for set mode, opens a datagram socket, fills `ifr_name` and `ifr_data`, performs the ioctl, then prints flags, tx type, and rx filter using symbolic names when known. Invalid usage returns 2, socket/ioctl failures return 1, success returns 0.

## State and Persistence Behavior

The program has only stack-local state. In set mode it requests persistent kernel/device timestamp configuration for the named interface until changed by another ioctl or device reset. In get mode it only reads kernel state.

## Dependencies and Integration Points

It depends on Linux networking headers, `kselftest.h` for `ARRAY_SIZE`, and an interface/driver implementing the hwtstamp ioctl. It integrates with userspace tests that need a simple readable way to configure or inspect hardware timestamping.

## Risks and Edge Cases

Interface names at or above `IFNAMSIZ` are rejected. Unknown numeric ioctl-returned values are printed as integers. The program does not close the socket explicitly before exit, which is harmless. Some drivers may coerce requested filters or reject unsupported modes with errno.

## Test Signals

Signals are exit code 0 plus printed `flags`, `tx_type`, and `rx_filter` for supported get/set operations; exit code 2 for invalid names or arguments; and ioctl errno output for unsupported devices or permissions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/hwtstamp_config.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/icmp.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/icmp.sh

## Purpose

This selftest verifies that an IPv4 ICMP unreachable generated in a namespace without an IPv4 source address uses the dummy source address `192.0.0.8` specified by RFC 7600 instead of `0.0.0.0`.

## Important APIs, Types, and Functions

The script sources `lib.sh`, defines constants for two namespaces and routes, creates `cleanup`, and uses `setup_ns`, `ip route add ... via inet6`, sysctl, `ping`, `tcpdump`, `awk`, and namespace helpers.

## Control Flow

The script creates namespaces `NS1` and `NS2`, connects them with a veth, assigns IPv4 only to NS1 and IPv6 to both ends, installs IPv4 routes via IPv6 next hops, enables IPv4 forwarding and disables ICMP rate limiting in NS2, starts a ping from NS1 to an unreachable IPv4 address behind NS2, captures the first non-echo ICMP packet with tcpdump, extracts the source IP, and compares it to `192.0.0.8`.

## State and Persistence Behavior

Temporary state includes namespaces, veth, addresses, routes, sysctls in NS2, a temporary capture file, and background ping/tcpdump processes. Cleanup removes the temp file and namespaces.

## Dependencies and Integration Points

It depends on IPv4 routes via IPv6 nexthops, `tcpdump`, ping, network namespaces, and kernel ICMP source address selection. It integrates with the kernel behavior for ICMP errors when no IPv4 address is available in the generating namespace.

## Risks and Edge Cases

The topology comment appears to list NS1's IPv6 address as NS2's address in one line, but the commands use distinct `2001:db8:1::1` and `::2`. The test assumes tcpdump sees exactly one relevant ICMP response before timeout. If ICMP rate limiting or forwarding settings fail, the response can be missing.

## Test Signals

Success prints `OK` and exits 0 when tcpdump shows `192.0.0.8` as the ICMP response source. Any other source prints a failure message and exits 1.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/icmp.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/icmp_redirect.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/icmp_redirect.sh

## Purpose

This selftest validates IPv4 and IPv6 ICMP redirect route exceptions and their interaction with PMTU exceptions, legacy routes, nexthop objects, and optional VRF routing. It models a host initially routed through `r1` to reach `h2`, then changes `r1` to forward back through the host-facing network via `r2`, causing redirects toward `h1`.

## Important APIs, Types, and Functions

The script sources `lib.sh` and defines logging helpers, `run_cmd`, `get_linklocal`, `cleanup`, `create_vrf`, `setup`, `change_h2_mtu`, `check_exception`, `run_ping`, route helpers for legacy and nexthop-object modes, `check_connectivity`, `do_test`, and `usage`. It uses `ip route get`, `ip nexthop`, VRF devices, bridges, sysctls for redirects and forwarding, ping/ping6, and MTU changes.

## Control Flow

The main path selects a ping6 binary, parses `-p`/`-v`, then runs four scenarios: legacy routing without VRF, legacy routing with VRF, nexthop-object routing without VRF if supported, and nexthop-object routing with VRF. Each scenario rebuilds namespaces and topology, installs initial routes, verifies connectivity, changes `r1` routes to trigger redirects, sends pings, checks cached redirect exceptions, lowers MTU to create PMTU exceptions, resets routes, checks cleanup of exceptions, then tests MTU-before-redirect ordering.

## State and Persistence Behavior

State is temporary namespaces `h1`, `h2`, `r1`, `r2`; veth links; bridge `br0`; optional VRF `red` with table 1111; IPv4/IPv6 addresses and routes; sysctls for redirects/forwarding; nexthop objects in new mode; route cache exceptions; and MTU settings on the h2/r2 link. Cleanup removes namespaces between scenarios.

## Dependencies and Integration Points

It depends on network namespaces, bridge, VRF, IPv4/IPv6 forwarding, ICMP redirects, route exception cache behavior, PMTU handling, optional nexthop object support, and `ping`. It integrates with kernel route exception formatting and redirect acceptance logic.

## Risks and Edge Cases

Assertions parse `ip route get` output strings such as `cache <redirected> expires ... mtu ...`, so output format changes can cause false failures. IPv6 redirect checks are marked XFAIL-capable in some cases through `log_test`'s fourth argument. VRF mode rewrites rule priority 0 lookup behavior and must be isolated by namespace cleanup. Link-local gateway discovery is required for IPv6 redirects.

## Test Signals

Success is counted through `log_test`: IPv4 and IPv6 redirect exceptions appear when expected, PMTU exceptions appear with MTU 1300, reset routes clear redirect/MTU cache state, MTU plus redirect ordering preserves both attributes, and basic connectivity remains intact after redirects and resets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/icmp_redirect.sh -->
