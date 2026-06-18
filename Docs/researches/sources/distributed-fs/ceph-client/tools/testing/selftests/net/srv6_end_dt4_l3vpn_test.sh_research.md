<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/srv6_end_dt4_l3vpn_test.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/srv6_end_dt4_l3vpn_test.sh

## Purpose

`srv6_end_dt4_l3vpn_test.sh` validates SRv6 `End.DT4` for IPv4 L3VPN service over an IPv6 underlay with two tenants.

## Important APIs, Types, and Functions

It has the same structural helpers as the DT46 script but configures only IPv4 host addressing and `encap seg6local action End.DT4 vrftable`. It uses VRFs, localsid table 90, IPv6 underlay routes, IPv4 proxy ARP, and `ip route ... encap seg6 mode encap` for IPv4 host routes.

## Control Flow

The script creates two router namespaces connected by veth, four host namespaces in tenants 100 and 200, per-tenant VRFs on each router, bidirectional SRv6 policies for same-tenant host pairs, and then runs router, host-gateway, same-tenant, and cross-tenant ping checks.

## State and Persistence Behavior

State is limited to temporary namespaces and devices. VRF tables 100/200 and localsid table 90 are namespace-local. Cleanup deletes links and namespaces after summary.

## Dependencies and Integration Points

Dependencies include root, `ip`, VRF strict mode, SRv6 End.DT4 support, IPv6 forwarding underlay, IPv4 forwarding in routers, and proxy ARP. It integrates IPv4 inner packet decapsulation with VRF route lookup.

## Risks and Edge Cases

The test does not run IPv6 host payloads; it uses IPv6 only for the SRv6 transport. The repeated `veth-t100`/`veth-t200` names in different namespaces are intentional. Feature detection may skip only VRF absence, so missing End.DT4 appears as setup/test failure.

## Test Signals

Success means same-tenant IPv4 pings pass in both directions, gateway pings pass, router underlay pings pass, and cross-tenant pings fail as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/srv6_end_dt4_l3vpn_test.sh -->
