
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/ip6gre_flat.sh

Purpose: IPv6-underlay GRE tunnel selftest for the flat topology without GRE keys. It validates IPv4-in-IPv6 and IPv6-in-IPv6 forwarding, MTU adjustment, and live remote endpoint changes.

Important APIs/functions: `setup_prepare`, `gre_flat`, `gre_mtu_change`, `gre_flat_remote_change`, `cleanup`; imported helpers from `lib.sh` and `ip6gre_lib.sh` such as `forwarding_enable`, `vrf_prepare`, `h1_create`, `sw1_flat_create`, `test_traffic_ip4ip6`, `test_traffic_ip6ip6`, and `flat_remote_change`.

Control flow: declares three `ALL_TESTS`, maps six veth positions into host, overlay, and underlay variables, enables forwarding/VRF rules, creates endpoints and flat switch tunnels, waits, then runs tests. Remote-change test changes both tunnel endpoints, validates traffic, restores old endpoints, and validates again.

State/persistence: mutates global forwarding sysctls, route rules, VRFs, VLANs, `ip6gre` devices `g1a`/`g2a`, addresses, routes, and temporary tc filters installed by library traffic probes. Cleanup tears these down in reverse.

Dependencies/integration: depends on root privileges, iproute2, mausezahn, tc flower counters, and `ip6gre_lib.sh` flat topology semantics. It integrates with kselftest harness variables `RET` and `EXIT_STATUS` through `tests_run`.

Risks: failures can come from stale routes/neighbors, unsupported GRE offload, tc counter timing, or missed cleanup if setup partially fails. The flat topology intentionally mixes default and non-default VRFs, so route-rule ordering from `vrf_prepare` is critical.

Test signals: successful ping-like generated traffic counters on underlay and overlay ports, failed large ping before MTU increase, successful large ping after MTU increase, and successful traffic after both new and restored remote endpoints.
