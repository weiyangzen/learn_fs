
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/mirror_gre_bridge_1d.sh

Purpose: Tests GRE mirroring when the underlay route points at an 802.1D bridge without VLAN filtering.

Important APIs/functions: `setup_prepare`, `cleanup`, `test_gretap`, `test_ip6gretap`; uses `mirror_gre_topo_create`, `full_test_span_gre_dir`, and manual neighbor replacement.

Control flow: creates standard GRE mirror topology, adds bridge `br2` over `$swp3`, routes GRE remote addresses via `br2`, assigns underlay addresses to `br2` and H3, and verifies gretap/ip6gretap ingress and egress mirroring.

State/persistence: creates `br2`, enslaves `$swp3`, adds IPv4/IPv6 routes and addresses, permanent neighbors during tests, and mirror tc filters.

Dependencies/integration: depends on bridge routing, neighbor entries, mirror helper libs, and tc counters.

Risks: route-to-bridge behavior and neighbor resolution are the focus. Cleanup deletes `br2`, implicitly dropping addresses/routes; explicit route removal is not performed.

Test signals: `full_test_span_gre_dir` observes expected ICMP request/reply on H3 tunnel devices for both tunnel families and directions.
