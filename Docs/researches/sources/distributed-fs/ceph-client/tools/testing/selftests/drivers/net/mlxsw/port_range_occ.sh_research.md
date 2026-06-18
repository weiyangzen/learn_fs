# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/port_range_occ.sh

## Purpose

Resource occupancy test for mlxsw ACL port-range entries.

## Important APIs, Types, and Functions

Defines a two-netif topology with clsact on SWP1, helper `port_range_occ_get`, and `port_range_occ_test`. It uses `devlink_resource_occ_get` and TC flower rules with UDP destination port ranges.

## Control Flow

Setup creates simple H1/SWP1 interfaces and clsact. The test records port-range resource occupancy, inserts an offloaded flower rule containing a port range, checks that occupancy increases, removes the rule, and verifies occupancy returns to the previous value.

## State and Persistence Behavior

State includes one TC ingress filter, clsact qdisc, simple interface state, and devlink resource counters.

## Dependencies and Integration Points

The script is part of the Linux kselftest networking suite copied under `sources/distributed-fs/ceph-client`. It depends on root privileges, real mlxsw Spectrum-capable switch ports exposed through `NETIFS`, iproute2 tools, `tc` flower offload, `devlink`, `ethtool`, `jq`, `bc`, kselftest helpers from `tools/testing/selftests/net/forwarding`, and traffic tools such as mausezahn or ping where referenced.

## Risks and Edge Cases

The assertion depends on devlink exposing the correct resource name and updating occupancy promptly. If the TC rule is not offloaded, resource occupancy may not change. Cleanup must remove the filter before checking final occupancy.

## Test Signals

Signals are devlink occupancy deltas and TC insertion/removal success.
