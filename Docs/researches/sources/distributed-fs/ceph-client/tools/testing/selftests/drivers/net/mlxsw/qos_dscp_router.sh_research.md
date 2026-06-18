# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/qos_dscp_router.sh

## Purpose

DSCP rewrite and priority behavior tests for routed mlxsw traffic.

## Important APIs, Types, and Functions

Defines reprioritization helpers `zero` and `three`, H1/H2 routed setup, `dscp_ping_test`, `test_update`, `test_no_update`, `test_pedit_norewrite`, and `test_dscp_leftover`. It uses route forwarding plus DSCP and pedit behavior.

## Control Flow

Setup creates two routed host interfaces and switch router ports. The tests send DSCP-marked traffic through the router, optionally apply reprioritization or pedit-style modifications, and check whether DSCP-derived priority is updated, left unchanged, or cleared as expected.

## State and Persistence Behavior

State includes router addresses/routes, QoS/DSCP maps, pedit or prioritization rules, counters, and forwarding sysctls.

## Dependencies and Integration Points

The script is part of the Linux kselftest networking suite copied under `sources/distributed-fs/ceph-client`. It depends on root privileges, real mlxsw Spectrum-capable switch ports exposed through `NETIFS`, iproute2 tools, `tc` flower offload, `devlink`, `ethtool`, `jq`, `bc`, kselftest helpers from `tools/testing/selftests/net/forwarding`, and traffic tools such as mausezahn or ping where referenced.

## Risks and Edge Cases

The tricky cases are update-vs-no-update and leftover DSCP state after edits. Hardware may classify before or after rewrite depending on pipeline behavior, so the expected results encode mlxsw-specific semantics.

## Test Signals

Signals are ping reachability and classification checks from `dscp_ping_test` under each named scenario.
