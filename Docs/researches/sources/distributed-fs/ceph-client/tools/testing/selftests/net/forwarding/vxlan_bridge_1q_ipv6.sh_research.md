# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/vxlan_bridge_1q_ipv6.sh

## Purpose

This is the IPv6-underlay version of the VLAN-filtering VXLAN bridge test. It maps VLAN 10 and VLAN 20 to separate VXLAN devices over IPv6 VTEP addresses and validates IPv4 and IPv6 tenant traffic, VLAN-specific flooding, static unicast, reconfiguration, and PVID behavior.

## Important APIs, Types, and Functions

It sources `lib.sh` and `tc_common.sh`. Core functions include `switch_create`, `ns_init_common`, `reapply_config`, `__ping_ipv4`, `__ping_ipv6`, `ping_ipv4`, `ping_ipv6`, `vxlan_flood_test`, `test_flood`, `vxlan_fdb_add_del`, `test_unicast`, and `test_pvid`.

## Control Flow

Setup creates local VLAN subinterfaces carrying both IPv4 and IPv6 tenant addresses, configures IPv6 underlay routes, creates `vx10`/`vx20` with IPv6 zero-checksum receive/transmit support, and builds two remote namespaces with matching VLAN bridges and VXLAN devices. Ping tests install `tc` counters on `rp1` and `swp1` to prove encapsulated IPv6-underlay traffic and decapsulated VLAN tenant traffic traverse the expected devices. Tests are repeated after `reapply_config`.

## State and Persistence Behavior

The script uses temporary bridge, VLAN, VXLAN, veth, namespace, route, address, qdisc, and FDB state. It toggles bridge VLAN entries on `vx10` during `test_pvid`; it does not leave persistent filesystem state.

## Dependencies and Integration Points

It depends on IPv6 VXLAN support, bridge VLAN filtering, `tc` flower filters matching VLAN ethertypes, `tc_common.sh` packet threshold helpers, and standard forwarding selftest infrastructure. It validates the bridge/VXLAN interface between VLAN-aware L2 forwarding and IPv6 tunnel transport.

## Risks and Edge Cases

The script intentionally sends many ping packets to overcome ARP and neighbor-discovery noise. Counter matching for VLAN decapsulation uses `protocol 802.1q` with `vlan_ethtype`, which depends on correct `tc flower` support. The test does not include the dynamic learning coverage present in the IPv4 1Q script.

## Test Signals

Success is IPv4 and IPv6 local/remote ping coverage for VLAN 10 and 20, at least-threshold `tc` counter hits on encapsulated and decapsulated paths, flood counters only on devices in the matching VLAN/VNI, static unicast counters only on the target, and PVID/VLAN membership changes suppressing or restoring remote flooding.
