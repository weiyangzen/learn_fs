
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/mirror_gre_vlan.sh

Purpose: Tests mirror-to-gretap when the tunnel underlay route points at a VLAN device.

Important APIs/functions: `setup_prepare`, `cleanup`, `test_gretap`; imports standard GRE mirror topology and helpers.

Control flow: creates standard topology, adds VLAN 555 on `$swp3` and `$h3`, assigns underlay addresses to VLAN devices, routes GRE remotes via `$swp3.555`, then verifies ingress and egress mirroring to `gt4`.

State/persistence: creates VLAN devices, addresses, routes, tc mirror filters, and standard GRE topology state.

Dependencies/integration: depends on VLAN underlay encapsulation, gretap routing, and mirror helper counters.

Risks: only IPv4 gretap is listed in `ALL_TESTS`; IPv6 underlay address/route is configured but no ip6gretap test runs here. VLAN cleanup via link deletion removes addresses/routes implicitly.

Test signals: decapsulated ICMP request/reply counters on `h3-gt4` for ingress and egress mirror directions.
