
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/ip6gre_hier_key.sh

Purpose: Hierarchical IPv6 GRE tunnel selftest with shared GRE `key 22`. It combines underlay/overlay VRF separation with keyed GRE lookup.

Important APIs/functions: `setup_prepare` passes `key 22` to both `sw1_hierarchical_create` and `sw2_hierarchical_create`; `gre_hier` uses `test_traffic_ip4ip6` and `test_traffic_ip6ip6`; remote-change helpers are `hier_remote_change` and `hier_remote_restore`.

Control flow: creates host VRFs, hierarchical switch topology, keyed `ip6gre` devices bound to dummy underlay endpoints, validates traffic, changes MTU, rewrites remote endpoints, validates, restores, and validates.

State/persistence: manipulates forwarding sysctls, local route rules, dummy underlay addresses, VLANs, keyed tunnels, VRF routes, and tc clsact/flower counters. Cleanup reverses switch, host, VRF, and forwarding state.

Dependencies/integration: relies on `lib.sh`, `tc_common.sh` via `ip6gre_lib.sh`, and kernel support for keyed ip6gre devices bound to a device in another VRF.

Risks: if key matching or VRF binding is offloaded differently from software, traffic may pass in one path and fail in another. Remote-change tests also depend on updating routes in underlay VRFs after local address changes.

Test signals: both inner protocol traffic checks pass with `key 22`; MTU test transitions from expected failure to success; keyed tunnel remains functional after endpoint changes.
