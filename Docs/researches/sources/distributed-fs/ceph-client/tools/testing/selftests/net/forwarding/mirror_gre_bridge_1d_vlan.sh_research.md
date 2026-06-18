
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/mirror_gre_bridge_1d_vlan.sh

Purpose: Extends the 802.1D bridge underlay test by placing the bridge port over VLAN 555, verifying tagged underlay encapsulation and STP transitions.

Important APIs/functions: `test_vlan_match`, `test_gretap`, `test_ip6gretap`, `test_gretap_stp`, `test_ip6gretap_stp`; uses `full_test_span_gre_dir_vlan` and `full_test_span_gre_stp`.

Control flow: creates standard GRE topology, bridge `br2`, VLAN `$swp3.555` as bridge port, H3 VLAN endpoint, routes GRE remotes via bridge, then tests VLAN match on mirrored GRE traffic and disables/re-enables STP state to confirm mirroring follows bridge port state.

State/persistence: creates VLAN 555 devices, bridge `br2`, addresses/routes, permanent neighbors for STP tests, tc mirror filters, and VLAN capture filters.

Dependencies/integration: depends on bridge/VLAN behavior, ARP/ND neighbor validity, and mirror helper libraries.

Risks: comments note neighbor-state races after mirror installation; tests force permanent neighbors to stabilize STP checks. VLAN ethertype matching differs between IPv4 and IPv6 tunnels.

Test signals: VLAN capture on H3 sees GRE underlay packets with VLAN 555 when allowed; mirrored decap fails while bridge port is disabled and recovers when forwarding.
