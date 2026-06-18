<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/srv6_end_dt46_l3vpn_test.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/srv6_end_dt46_l3vpn_test.sh

## Purpose

`srv6_end_dt46_l3vpn_test.sh` validates SRv6 `End.DT46` behavior for dual-stack IPv4/IPv6 L3VPNs. It builds two tenant VPNs across two SRv6 routers and verifies same-tenant connectivity and cross-tenant isolation for both IP families.

## Important APIs, Types, and Functions

The script sources `lib.sh` and uses `setup_ns`/`cleanup_all_ns`. Major functions are `log_test`, `cleanup`, `setup_rt_networking`, `setup_hs`, `setup_vpn_config`, `setup`, connectivity check helpers, `router_tests`, `host2gateway_tests`, `host_vpn_tests`, and `host_vpn_isolation_tests`. It uses `ip -6 route ... encap seg6 mode encap`, `encap seg6local action End.DT46 vrftable`, VRF devices, IPv6 rules to a localsid table, proxy ARP/NDP, and unreachable defaults.

## Control Flow

Startup requires root, `ip`, and VRF strict-mode support. `setup` creates a veth underlay between `rt_1` and `rt_2`, creates four host namespaces for tenants 100 and 200, attaches hosts to router VRFs, and installs bidirectional SRv6 encapsulation and decapsulation routes. It then pings router underlay, host-to-gateway paths, same-tenant VPN paths, and all cross-tenant combinations expecting failure.

## State and Persistence Behavior

All route, VRF, veth, sysctl, and namespace state is temporary. Cleanup deletes underlay links and all namespaces. Per-tenant VRF tables 100 and 200 and localsid table 90 exist only inside router namespaces.

## Dependencies and Integration Points

It depends on SRv6, seg6local `End.DT46`, VRF strict mode, IPv4/IPv6 forwarding, proxy ARP/NDP, and iproute2 SRv6 syntax. It integrates with kernel SRv6 decapsulation into VRF table lookup for both IPv4 and IPv6 inner packets.

## Risks and Edge Cases

The script assumes fixed tenant IDs and overlapping host prefixes across tenants, so VRF isolation is central. If proxy ARP/NDP or unreachable default routes are misconfigured, failures can look like SRv6 bugs. It checks feature presence only for VRF, not specifically `End.DT46` before setup.

## Test Signals

Success is zero failures in the printed summary. Critical signals are IPv4 and IPv6 host connectivity within tenant 100 and 200, host-to-gateway reachability, router underlay reachability, and expected ping failures between tenants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/srv6_end_dt46_l3vpn_test.sh -->
