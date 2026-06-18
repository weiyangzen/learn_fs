# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/qos_dscp_bridge.sh

## Purpose

DSCP-to-priority QoS classification test for bridged mlxsw traffic.

## Important APIs, Types, and Functions

Defines H1/H2 bridge setup, `ping_ipv4`, `dscp_ping_test`, and `test_dscp`. It uses IPv4 ping/traffic with selected DSCP values and observes priority counters or forwarding behavior through the shared library.

## Control Flow

Setup creates two hosts connected through switch bridge ports. `dscp_ping_test` sends traffic with chosen DSCP values and validates the expected priority mapping. `test_dscp` runs the configured DSCP cases after confirming basic connectivity.

## State and Persistence Behavior

State includes bridge membership, addresses/routes, DSCP/prio maps, and interface counters. Cleanup removes bridge and host state.

## Dependencies and Integration Points

The script is part of the Linux kselftest networking suite copied under `sources/distributed-fs/ceph-client`. It depends on root privileges, real mlxsw Spectrum-capable switch ports exposed through `NETIFS`, iproute2 tools, `tc` flower offload, `devlink`, `ethtool`, `jq`, `bc`, kselftest helpers from `tools/testing/selftests/net/forwarding`, and traffic tools such as mausezahn or ping where referenced.

## Risks and Edge Cases

Results depend on DSCP preservation across the bridge path and on the driver's current DSCP-to-priority map. Any previous QoS map changes can leak into this test if cleanup fails.

## Test Signals

Signals are successful ping and per-DSCP classification checks in `test_dscp`.
