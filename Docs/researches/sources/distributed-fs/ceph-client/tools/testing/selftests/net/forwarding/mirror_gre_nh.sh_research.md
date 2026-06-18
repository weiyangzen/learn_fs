
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/mirror_gre_nh.sh

Purpose: Tests mirror-to-GRE when the tunnel remote endpoint is reachable through a next-hop route rather than a directly attached route.

Important APIs/functions: `setup_prepare`, `test_gretap`, `test_ip6gretap`; uses standard topology plus explicit remote endpoint addressing and routes.

Control flow: disables IPv4 rp_filter, assigns underlay transport addresses on a different subnet, assigns tunnel endpoint addresses to tunnel devices, and for IPv6 preinstalls a next-hop route. IPv4 test verifies no mirroring before adding the route to 192.0.2.130 via H3, then success after adding it. IPv6 test verifies success through preinstalled next-hop route.

State/persistence: mutates rp_filter sysctls, tunnel/underlay addresses, IPv4/IPv6 routes, tc mirror filters, and standard GRE topology state.

Dependencies/integration: relies on route resolution through next-hop and mirror offload updates for indirect remotes.

Risks: comments note IPv6 route ordering limitation for locally specified addresses. A cleanup call includes an extra argument to `sysctl_restore`, harmless in shell but easy to misread.

Test signals: IPv4 mirrored traffic fails before route add and passes after; IPv6 mirrored traffic passes with the configured next-hop route.
