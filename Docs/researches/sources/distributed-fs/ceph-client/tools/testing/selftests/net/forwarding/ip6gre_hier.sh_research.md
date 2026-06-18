
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/ip6gre_hier.sh

Purpose: IPv6-underlay GRE tunnel selftest for hierarchical VRF topology without keys, where tunnel devices are bound to underlay dummy devices in different VRFs than the overlay.

Important APIs/functions: `setup_prepare` calls `sw1_hierarchical_create` and `sw2_hierarchical_create`; tests are `gre_hier`, `gre_mtu_change`, and `gre_hier_remote_change`; cleanup calls hierarchical destroy helpers.

Control flow: maps six interfaces, enables forwarding/VRF route rules, creates host endpoints, then creates separated overlay and underlay VRFs with dummy-bound `ip6gre` devices. Tests run IPv4/IPv6 payload validation, topology MTU changes, then endpoint rewrite/restore through hierarchical remote helpers.

State/persistence: creates VRFs per endpoint/link, dummy devices `dummy1`/`dummy2`, VLAN underlay links, `g1a`/`g2a` tunnels, routes in both overlay and underlay VRFs, and transient tc counters.

Dependencies/integration: depends on `ip6gre_lib.sh` hierarchical model and kernel support for tunnel `dev dummyX` binding across VRFs.

Risks: route deletion must target the correct VRF; endpoint-change functions update dummy addresses instead of tunnel-device addresses, so mismatched cleanup can leave stale addresses/routes. Hardware offload paths may differ from flat topology.

Test signals: IPv4-in-IPv6 and IPv6-in-IPv6 counters after encapsulation/decapsulation, successful MTU raise behavior, and successful traffic after changing and restoring hierarchical tunnel remotes.
