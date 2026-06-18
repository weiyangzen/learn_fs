# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/vxlan_bridge_1q_port_8472.sh

## Purpose

This wrapper runs a focused IPv4 VLAN-filtering VXLAN bridge reachability test using UDP port 8472. It guards against regressions where non-default VXLAN ports break VLAN-to-VNI forwarding.

## Important APIs, Types, and Functions

The file sets `VXPORT=8472`, sets `ALL_TESTS` to `ping_ipv4`, and sources `vxlan_bridge_1q.sh`. All topology, cleanup, and ping helpers are inherited from the sourced script.

## Control Flow

After assigning variables, the sourced script executes its normal setup and top-level `test_all`; the inherited `tests_run` sees only the overridden ping test list.

## State and Persistence Behavior

The wrapper owns only shell variable state. The sourced script creates temporary VLAN subinterfaces, bridge/VXLAN devices, namespaces, FDB entries, routes, and qdiscs with the VXLAN devices configured for port 8472.

## Dependencies and Integration Points

It depends on the sibling `vxlan_bridge_1q.sh` file and the full forwarding selftest environment. Its integration point is the VXLAN `dstport` attribute in a VLAN-filtering bridge topology.

## Risks and Edge Cases

The wrapper only checks basic ping reachability, so deeper flood, unicast, learning, and PVID behavior on port 8472 is not covered here.

## Test Signals

Success is the inherited VLAN 10 and VLAN 20 IPv4 local and remote ping matrix passing with `vx10` and `vx20` using UDP port 8472.
