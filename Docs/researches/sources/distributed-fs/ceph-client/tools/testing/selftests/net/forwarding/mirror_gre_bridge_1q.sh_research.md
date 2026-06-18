
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/mirror_gre_bridge_1q.sh

Purpose: Tests GRE mirroring when the underlay route points at a VLAN-aware 802.1Q bridge.

Important APIs/functions: `setup_prepare`, `test_gretap`, `test_ip6gretap`; uses `mirror_gre_topo_create` and `full_test_span_gre_dir`.

Control flow: creates standard topology, temporarily brings `br1` down to adjust VLAN settings, enslaves `$swp3` to `br1`, adds VLAN 555 as bridge self PVID/untagged, assigns underlay addresses to `br1`, routes GRE remotes through it, and creates H3 VLAN 555 endpoint. Tests gretap and ip6gretap ingress/egress mirroring.

State/persistence: mutates existing `br1` from the standard topology, adds VLAN state, routes, H3 VLAN, permanent neighbors, and tc mirror filters.

Dependencies/integration: relies on Linux bridge VLAN filtering and route-to-bridge-device behavior.

Risks: changing bridge PVID while operational is avoided explicitly; cleanup delegates much state to topology destruction and only detaches `$swp3`/H3 VLAN.

Test signals: decapsulated ICMP counters on H3 tunnel endpoints for both GRE families and both mirror directions.
