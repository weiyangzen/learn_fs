# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/vxlan_symmetric_ipv6.sh

## Purpose

This is the IPv6 symmetric VXLAN routing test. It validates L2 VNIs for same-subnet traffic and an L3 VNI on VLAN 4001 for routed remote IPv6 host routes across IPv6 VTEP endpoints.

## Important APIs, Types, and Functions

The script uses `lib.sh` helpers plus local functions mirroring the IPv4 symmetric test: `hx_create`, `switch_create`, `spine_create`, `ns_switch_create`, `__l2_vni_init`, `l2_vni_init`, `__l3_vni_init`, `l3_vni_init`, and `ping_ipv6`. VXLAN devices use `udp6zerocsumrx` and `udp6zerocsumtx`.

## Control Flow

Setup creates local and namespace hosts, VLAN-aware bridges, `vx10`, `vx20`, `vx4001`, IPv6 underlay routes through a spine VRF, and static L2 and L3 VNI programming. It also enables forwarding inside `ns1`. The only test function runs the five IPv6 ping paths, then cleanup reverses the topology.

## State and Persistence Behavior

Temporary state includes IPv6 addresses, routes, bridge VLAN entries, VXLAN devices, VRFs, macvlans, noarp external-learn neighbor entries, static bridge FDB entries, and host routes with `/128` prefixes through `vlan4001`.

## Dependencies and Integration Points

It depends on IPv6 routing and forwarding, VXLAN over IPv6, bridge VLAN filtering, VRFs, macvlan, and kselftest forwarding helpers. It verifies kernel integration of IPv6 VXLAN L2 and L3 VNI datapaths.

## Risks and Edge Cases

The namespace-side SVI/macvlan addresses intentionally overlap on each VLAN, so DAD and forwarding settings are important. L3 VNI route correctness depends on exact `/128` routes and VTEP neighbor entries. A missing IPv6 forwarding enable in the namespace would break remote routed paths.

## Test Signals

Success is all `ping6_test` calls passing for local, remote same-VLAN, and remote cross-VLAN paths.
