# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/qos_headroom.sh

## Purpose

DCB headroom and buffer-size validation for mlxsw lossless/lossy priority groups and TC qdisc mode.

## Important APIs, Types, and Functions

With zero cabled netifs, selects `$NETIF_NO_CABLE` and defines getters/checkers for priority-to-PG/PFC/TC mapping, buffer size, total buffer size, and tests for defaults, DCB ETS, MTU, TC MTU, PFC, TC priority map, TC sizes, internal buffers, and TC internal buffers.

## Control Flow

Each test applies DCB ETS/PFC or TC qdisc configuration, reads DCB buffer state and devlink cell size/total buffer data, and checks expected size/mapping relationships. PFC cases turn priorities 5-7 lossless and vary cable delay. Internal buffer tests add SPAN/mirror qdiscs and ensure invisible buffer accounting changes and restores correctly.

## State and Persistence Behavior

State includes DCB ETS/PFC settings, DCB buffer sizes, MTU changes, TC qdisc roots/clsact filters, mirred actions, and devlink buffer accounting. Cleanup calls `pre_cleanup` and individual tests restore their settings.

## Dependencies and Integration Points

The script is part of the Linux kselftest networking suite copied under `sources/distributed-fs/ceph-client`. It depends on root privileges, real mlxsw Spectrum-capable switch ports exposed through `NETIFS`, iproute2 tools, `tc` flower offload, `devlink`, `ethtool`, `jq`, `bc`, kselftest helpers from `tools/testing/selftests/net/forwarding`, and traffic tools such as mausezahn or ping where referenced.

## Risks and Edge Cases

This suite is sensitive to cell-size rounding, hardware headroom formulas, port lane count, DCB tool behavior, and hidden internal buffers. Missing restore after an early failure can affect many later QoS tests.

## Test Signals

Signals are exact or relational `check_*` assertions for priority maps and buffer sizes, plus `log_test` messages for each buffer/headroom scenario.
