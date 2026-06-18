
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/ip6gre_hier_keys.sh

Purpose: Hierarchical IPv6 GRE tunnel selftest with asymmetric GRE keys. It validates `ikey`/`okey` behavior when tunnel endpoints are bound through separate underlay VRFs.

Important APIs/functions: `setup_prepare` creates SW1 with `ikey 111 okey 222` and SW2 with `ikey 222 okey 111`; tests use `test_traffic_ip4ip6`, `test_traffic_ip6ip6`, `test_mtu_change`, `hier_remote_change`, and `hier_remote_restore`.

Control flow: builds six-interface hierarchical topology, runs IPv4 and IPv6 traffic checks, increases topology MTUs for large IPv6 ping, changes tunnel local/remote addresses on dummy-bound endpoints, validates traffic, restores original addresses, and reruns traffic checks.

State/persistence: creates and deletes dummy devices, per-link VRFs, VLAN underlay links, directional-key `ip6gre` tunnels, routes in overlay/underlay VRFs, and tc statistics filters.

Dependencies/integration: depends on `ip6gre_lib.sh` accepting extra `ip link add type ip6gre` parameters and on common kselftest result aggregation.

Risks: direction-specific key mismatch causes silent one-way failure. Hierarchical cleanup is sensitive to route order and dummy-device existence.

Test signals: tc counters show forwarded inner IPv4 and IPv6 packets across the GRE-over-IPv6 tunnel in both endpoint states, and MTU behavior matches the larger-packet expectations.
