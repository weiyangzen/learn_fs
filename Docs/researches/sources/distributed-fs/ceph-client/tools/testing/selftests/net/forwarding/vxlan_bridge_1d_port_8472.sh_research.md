# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/vxlan_bridge_1d_port_8472.sh

## Purpose

This wrapper reruns a focused subset of the IPv4 802.1D VXLAN bridge test with the non-default UDP destination port 8472. It exists to verify that VXLAN datapath setup and forwarding do not assume the IANA default port 4789.

## Important APIs, Types, and Functions

The file sets `VXPORT=8472`, overrides `ALL_TESTS` to only `ping_ipv4`, and sources `vxlan_bridge_1d.sh`. All topology creation and test functions are inherited from the sourced script.

## Control Flow

After variable assignment, control transfers to `vxlan_bridge_1d.sh`, whose main body creates the full 802.1D topology and runs `test_all`. Because `ALL_TESTS` is pre-set, only the IPv4 reachability matrix runs.

## State and Persistence Behavior

No state is owned directly by the wrapper. The sourced script creates and removes the bridge, VXLAN device, namespaces, routes, veths, qdiscs, and FDB entries, but all VXLAN device creation uses UDP port 8472.

## Dependencies and Integration Points

The wrapper depends on the sibling `vxlan_bridge_1d.sh` path being resolvable from the forwarding selftest directory. It integrates with the same kselftest forwarding and kernel VXLAN infrastructure while parameterizing only the UDP port.

## Risks and Edge Cases

Because the wrapper narrows `ALL_TESTS`, it validates reachability but not flood, unicast, ECN, TOS, TTL, or learning behavior on port 8472. Any change in the sourced script's top-level execution model can affect this wrapper.

## Test Signals

Success is the inherited `ping_ipv4` checks passing with `vx1` created as `dstport 8472`.
