# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/port_range_scale.sh

## Purpose

Scale helper for inserting many offloaded flower rules with expanding UDP destination port ranges.

## Important APIs, Types, and Functions

This sourced helper defines `PORT_RANGE_NUM_NETIFS`, setup/cleanup, `port_range_rules_create`, `__port_range_test`, and `port_range_test`. It writes a temporary TC batch file containing `flower skip_sw ip_proto udp dst_port 1-N` rules.

## Control Flow

Setup prepares H1/SWP1 and clsact. The test first checks offload capability, then inserts the requested rule count, optionally expecting failure. It reads `tc -j filter show` and counts filters with `options.in_hw == true` to ensure the offload count matches the requested count.

## State and Persistence Behavior

State includes a temp batch file, many TC ingress filters, clsact qdisc, VRF/simple interface state, and JSON parsed TC state.

## Dependencies and Integration Points

The script is part of the Linux kselftest networking suite copied under `sources/distributed-fs/ceph-client`. It depends on root privileges, real mlxsw Spectrum-capable switch ports exposed through `NETIFS`, iproute2 tools, `tc` flower offload, `devlink`, `ethtool`, `jq`, `bc`, kselftest helpers from `tools/testing/selftests/net/forwarding`, and traffic tools such as mausezahn or ping where referenced.

## Risks and Edge Cases

Partial batch insertion can make counts differ from both success and failure expectations. JSON shape from `tc -j` is assumed. Port-range resource limits vary by ASIC and profile, so callers must pass the correct `count` and `should_fail` values.

## Test Signals

Signals are TC batch exit status and JSON offload count equality, with `check_err_fail` handling expected-failure lanes.
