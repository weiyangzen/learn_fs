# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/vxlan_bridge_1d_port_8472_ipv6.sh

## Purpose

This wrapper runs the IPv6-underlay 802.1D VXLAN bridge test on UDP port 8472. It validates that both IPv4 and IPv6 tenant ping paths still work when the VXLAN tunnel endpoint uses the legacy/non-default port.

## Important APIs, Types, and Functions

The wrapper sets `VXPORT=8472`, restricts `ALL_TESTS` to `ping_ipv4` and `ping_ipv6`, and sources `vxlan_bridge_1d_ipv6.sh`. All functions and cleanup logic are inherited.

## Control Flow

The sourced script builds the IPv6 underlay topology and runs its normal top-level setup and `test_all`; the preconfigured test list limits execution to reachability checks.

## State and Persistence Behavior

Direct state is limited to exported shell variables. The sourced script creates the full temporary bridge/VXLAN/netns topology, with all VXLAN devices using destination port 8472.

## Dependencies and Integration Points

It depends on `vxlan_bridge_1d_ipv6.sh`, IPv6 VXLAN support, forwarding kselftest helpers, and `tc_common.sh`. The integration point is the VXLAN UDP port attribute across IPv6 underlay encapsulation and decapsulation.

## Risks and Edge Cases

The wrapper does not run the inherited flood, unicast, tunnel metadata, or ECN tests. It mainly guards against regressions where non-default VXLAN UDP ports break basic tunnel reachability.

## Test Signals

Success is inherited IPv4 and IPv6 tenant pings passing through a VXLAN device configured with `dstport 8472`.
