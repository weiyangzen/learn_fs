# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/vxlan_bridge_1q_port_8472_ipv6.sh

## Purpose

This wrapper runs the IPv6-underlay VLAN-filtering VXLAN bridge ping tests with destination UDP port 8472. It covers both IPv4 and IPv6 tenant pings over the non-default VXLAN port.

## Important APIs, Types, and Functions

The wrapper sets `VXPORT=8472`, overrides `ALL_TESTS` to `ping_ipv4` and `ping_ipv6`, and sources `vxlan_bridge_1q_ipv6.sh`.

## Control Flow

Execution is delegated to the sourced script after variable setup. The inherited setup creates the full IPv6-underlay 1Q topology and runs only the two reachability functions in the overridden test list.

## State and Persistence Behavior

No direct networking state is created in this file. The sourced script creates and destroys all bridge, VLAN, VXLAN, namespace, route, and qdisc state, with `vx10` and `vx20` using UDP port 8472.

## Dependencies and Integration Points

The wrapper depends on `vxlan_bridge_1q_ipv6.sh`, IPv6 VXLAN transport support, and forwarding kselftest helpers. It specifically integrates with the VXLAN port configuration path.

## Risks and Edge Cases

Flood, unicast, and PVID behavior are not run by this wrapper. It will not catch bugs isolated to those behaviors on port 8472.

## Test Signals

Success is inherited IPv4 and IPv6 VLAN 10/20 ping coverage passing through VXLAN devices configured with `dstport 8472`.
