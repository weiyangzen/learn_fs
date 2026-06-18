
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/mirror_gre.sh

Purpose: Baseline mirror-to-GRE test for `tc action mirred egress mirror` targeting `gretap` and `ip6gretap` devices.

Important APIs/functions: `setup_prepare`, `test_span_gre_mac`, `test_two_spans`, `test_gretap`, `test_ip6gretap`, `test_gretap_mac`, `test_ip6gretap_mac`; imports mirror helper/topology libraries.

Control flow: builds standard mirror GRE topology, adds IPv4 and IPv6 underlay addresses between SW and H3, installs mirrors on `$swp1` ingress/egress, sends ICMP traffic between H1/H2, and verifies decapsulated packets on H3 tunnel devices. It also tests simultaneous ingress and egress mirrors to different tunnel types.

State/persistence: creates bridge topology, tunnel devices `gt4`/`gt6` and `h3-gt4`/`h3-gt6`, addresses, tc qdiscs/filters, and mirror actions. Cleanup removes addresses and topology.

Dependencies/integration: depends on `mirror_lib.sh`, `mirror_gre_lib.sh`, `mirror_gre_topo_lib.sh`, tc flower/matchall, and `MZ`.

Risks: mirror uninstall helper deletes from `$swp1` regardless of passed `from_dev`, which matches this topology but is a library coupling. Decap verification depends on tc counters on sink devices.

Test signals: ICMP type 8/0 counters on H3 tunnel devices, envelope MAC checks, and continued/failing counters as mirrors are installed/uninstalled.
