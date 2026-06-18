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
