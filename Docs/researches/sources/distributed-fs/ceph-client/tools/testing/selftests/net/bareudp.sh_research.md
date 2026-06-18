# sources/distributed-fs/ceph-client/tools/testing/selftests/net/bareudp.sh

Purpose: End-to-end test of BAREUDP tunnel devices transporting IPv4, IPv6, and MPLS over UDPv4 and UDPv6 underlays.

Important APIs/types/functions: Uses four namespaces, veth chain topology, `ip link add type bareudp`, `tc flower` + `tunnel_key` + `mirred` actions, MPLS sysctls/routes, IPv4/IPv6 forwarding sysctls, and ping reachability tests.

Control flow: The script checks iproute2 BAREUDP support and ping6 fallback, creates four namespaces in a chain, configures underlay veths and ingress qdiscs, sets overlay addresses/routes for IPv4, IPv6, and MPLS, then runs `test_overlay` for IPv4, IPv6, IPv4 multiproto, and MPLS unicast. Each overlay creates bareudp devices in the middle namespaces, programs encapsulation filters for UDPv4, pings, deletes filters, reprograms filters for UDPv6, pings again, then removes devices.

State and persistence behavior: Creates temporary namespaces, veths, bareudp devices, qdiscs, filters, routes, MPLS labels, and forwarding sysctls. Trap cleanup removes all namespaces.

Dependencies and integration points: Requires root, BAREUDP kernel/iproute2 support, `tc` tunnel actions, MPLS routing support for MPLS cases, IPv6, and kselftest `lib.sh`.

Risks: Multi-protocol tunnel behavior, MPLS support, and `tc` action availability vary by kernel config. The script sets `ERR=4` during setup so setup failures report SKIP rather than FAIL. Route/filter cleanup must run between underlay variants to avoid cross-test contamination.

Test signals: Printed `[ OK ]` ping tests for IPv4, IPv6, and MPLS over UDPv4/UDPv6 indicate successful encapsulation and decapsulation.
