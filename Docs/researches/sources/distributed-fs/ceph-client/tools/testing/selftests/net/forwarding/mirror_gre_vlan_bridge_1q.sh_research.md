
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/mirror_gre_vlan_bridge_1q.sh

Purpose: Comprehensive GRE mirror test where the underlay route points at a VLAN upper over a VLAN-aware bridge, including forbidden VLAN, untagged egress, FDB roaming, and STP cases.

Important APIs/functions: `h3_addr_add_del`, `test_vlan_match`, `test_span_gre_forbidden_cpu`, `test_span_gre_forbidden_egress`, `test_span_gre_untagged_egress`, `test_span_gre_fdb_roaming`, `test_gretap_stp`, `test_ip6gretap_stp`, and tunnel-specific wrappers.

Control flow: disables rp_filter, creates standard GRE topology, creates `br1.555` underlay and H3 VLAN endpoint, attaches `$swp3`/`$swp2` to VLAN 555. Tests validate normal mirroring, remove/add bridge self VLAN, remove/add egress VLAN, toggle untagged egress and H3 address placement, force FDB entry to roam to wrong port, and test STP state.

State/persistence: mutates bridge VLAN tables, FDB entries, VLAN devices, routes, rp_filter sysctls, H3 addresses, tc mirror/capture filters, and neighbor/FDB priming via arping.

Dependencies/integration: requires `arping`, bridge VLAN filtering, GRE helper libraries, and tc counters.

Risks: FDB roaming loop retries when ARP/ND reprimes FDB mid-test. Several sleeps stabilize bridge/offload updates. rp_filter is disabled to avoid false failures for untagged egress.

Test signals: expected mirrored packet counters in normal states, zero counters when VLAN/FDB/STP forbids egress, VLAN capture presence/absence when toggling tagged versus untagged egress.
