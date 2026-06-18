# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/vxlan_bridge_1d_ipv6.sh

## Purpose

This test validates an 802.1D bridge VXLAN topology where the VXLAN underlay is IPv6 while tenant payloads include both IPv4 and IPv6. It checks local switching, remote encapsulation/decapsulation through IPv6 VTEPs, flooding, static unicast forwarding, TTL/TOS inheritance, ECN handling, and configuration reapplication.

## Important APIs, Types, and Functions

It sources `lib.sh` and `tc_common.sh`. Important helpers include `rp1_set_addr`, `switch_create`, `ns_init_common`, `reapply_config`, `__ping_ipv4`, `__ping_ipv6`, `vxlan_flood_test`, `test_flood`, `vxlan_fdb_add_del`, `test_unicast`, `vxlan_ping_test`, `test_ttl`, `test_tos`, `test_ecn_encap`, `vxlan_encapped_ping_do`, and `test_ecn_decap`.

## Control Flow

Setup builds local hosts with IPv4 and IPv6 addresses, an IPv6 underlay through `rp1`/`rp2`, two remote namespaces connected by veth pairs, and one VXLAN device per bridge. Ping tests install `tc flower` counters on the underlay router and local switch port to prove encapsulated packets use the IPv6 VTEP path and decapsulated replies return through the bridge. After metadata tests, `reapply_config` detaches VXLAN from the bridge and removes/re-adds underlay addresses before repeating core checks.

## State and Persistence Behavior

The test owns temporary bridge, VXLAN, namespace, veth, route, address, `tc`, and FDB state. VXLAN devices use `udp6zerocsumrx`, `udp6zerocsumtx`, `tos inherit`, and `ttl 100`. No persistent files are changed.

## Dependencies and Integration Points

It depends on IPv6 VXLAN support, IPv4 and IPv6 ping tools, `tc_common.sh` packet counters, bridge FDB operations with IPv6 `dst`, and the Linux bridge/VXLAN datapath. It validates interaction between IPv6 underlay routing and L2 tenant forwarding.

## Risks and Edge Cases

The flood tests count ICMPv6 payloads and can be affected by neighbor discovery noise, so ping tests send 100 packets and require at least 100 counter hits. VXLAN ECN decap uses hand-crafted IPv6 inner headers, and the invalid outer CE plus inner non-ECT case must be reported as RX errors. Counter matching relies on hardware/software offload flags behaving as expected.

## Test Signals

Passing output includes IPv4 and IPv6 local/remote pings, underlay encapsulation and local decapsulation `tc` counter hits, exact flood and unicast distribution across local and remote VXLAN devices, TTL/TOS matches, ECN encapsulation mappings, ECN decapsulation mappings, and RX errors for the invalid ECN case.
