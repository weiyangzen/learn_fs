# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/devlink_trap_policer.sh

## Purpose

Validation of mlxsw devlink trap policer configuration limits and runtime policing behavior.

## Important APIs, Types, and Functions

Creates a routed IPv4 topology with large MTUs and a blackhole route whose trap action is set to `trap`. Key functions are `rate_limits_test`, `burst_limits_test`, `trap_rate_get`, `policer_drop_rate_get`, `rate_test`, and `burst_test`. It uses `devlink trap policer set`, trap and policer statistics, mausezahn traffic, and deferred cleanup helpers from the forwarding library.

## Control Flow

Setup reloads devlink to reset trap settings, prepares VRFs, raises MTUs, configures router ports, adds a blackhole route, and traps `blackhole_route`. Limit tests try invalid and boundary policer rate/burst values. Runtime tests set policer parameters, generate traffic toward the blackhole destination, sample accepted trap rate and policer drop rate over time, and check that configured rate/burst materially affect observed counters.

## State and Persistence Behavior

State includes devlink trap policer rate/burst values, blackhole route, MTU changes, trap action, VRFs, and background traffic. The script uses `defer` extensively so state unwinds even from mid-test failure.

## Dependencies and Integration Points

The script is part of the Linux kselftest networking suite copied under `sources/distributed-fs/ceph-client`. It depends on root privileges, real mlxsw Spectrum-capable switch ports exposed through `NETIFS`, iproute2 tools, `tc` flower offload, `devlink`, `ethtool`, `jq`, `bc`, kselftest helpers from `tools/testing/selftests/net/forwarding`, and traffic tools such as mausezahn or ping where referenced.

## Risks and Edge Cases

Rate assertions are timing-sensitive and depend on CPU scheduling, traffic generator stability, hardware counter update cadence, and default policer indexing. Boundary values are mlxsw ABI assumptions; firmware changes can shift limits. Devlink reload can disrupt unrelated device state if run on a shared test system.

## Test Signals

Signals are explicit pass/fail for rejected invalid values, accepted min/max values, measured trap packet rate, measured policer drop rate, and `log_test` entries for rate and burst behavior.
