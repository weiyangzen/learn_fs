<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/srv6_end_dt6_l3vpn_test.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/srv6_end_dt6_l3vpn_test.sh

## Purpose

`srv6_end_dt6_l3vpn_test.sh` validates SRv6 `End.DT6` for IPv6 L3VPN service over an IPv6 underlay with two isolated tenants.

## Important APIs, Types, and Functions

It mirrors the DT4/DT46 topology helpers but uses IPv6 host addresses, proxy NDP, IPv6 forwarding, and `encap seg6local action End.DT6 vrftable`. Encapsulation routes target host `/128` routes in tenant VRFs.

## Control Flow

After root, `ip`, and VRF checks, setup creates router and host namespaces, connects hosts through per-tenant VRFs, installs bidirectional SRv6 policies and localsid rules, and runs router connectivity, host-to-gateway, same-tenant VPN, and cross-tenant isolation tests.

## State and Persistence Behavior

All namespace, veth, VRF, route, rule, and sysctl changes are temporary and cleaned at script end. IPv6 DAD is disabled in relevant namespaces to avoid timing delays.

## Dependencies and Integration Points

It depends on SRv6 End.DT6, VRF, IPv6 forwarding, proxy NDP, and iproute2 seg6 support. It integrates decapsulated IPv6 packet lookup into the specified VRF table.

## Risks and Edge Cases

Like the other DT tests, missing End.DT6 support is not preflighted separately. Proxy NDP is required for host L2 reachability. Overlapping tenant IPv6 prefixes make isolation tests meaningful but can complicate diagnosis.

## Test Signals

Expected success is all IPv6 same-tenant and host-gateway pings passing, all cross-tenant pings failing, and zero failed tests in the summary.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/srv6_end_dt6_l3vpn_test.sh -->
