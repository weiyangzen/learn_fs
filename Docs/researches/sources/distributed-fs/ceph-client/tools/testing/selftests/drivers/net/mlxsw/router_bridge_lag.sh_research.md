# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/router_bridge_lag.sh

## Purpose

mlxsw-specific wrapper for the shared router/bridge/LAG forwarding topology test.

## Important APIs, Types, and Functions

Defines `ALL_TESTS` and configuration hooks `config_devlink_reload`, `config_enslave_h1` through `config_enslave_h4`, then sources the generic `net/forwarding/router_bridge_lag.sh` implementation.

## Control Flow

The wrapper injects mlxsw-specific behavior into the shared test: reload the devlink device as part of configuration and provide host-enslavement hooks for the topology. After sourcing, control flow is owned by the common router/bridge/LAG library, which runs configuration waits and IPv4/IPv6 pings.

## State and Persistence Behavior

State is mostly created by the shared implementation: bridges, LAGs, host and switch port masters, routes, and forwarding settings. The wrapper itself only defines hooks and all-tests order.

## Dependencies and Integration Points

The script is part of the Linux kselftest networking suite copied under `sources/distributed-fs/ceph-client`. It depends on root privileges, real mlxsw Spectrum-capable switch ports exposed through `NETIFS`, iproute2 tools, `tc` flower offload, `devlink`, `ethtool`, `jq`, `bc`, kselftest helpers from `tools/testing/selftests/net/forwarding`, and traffic tools such as mausezahn or ping where referenced. It integrates directly with the shared `router_bridge_lag.sh` forwarding test.

## Risks and Edge Cases

Because behavior is delegated, wrapper risk is in hook naming and devlink reload side effects. Any mismatch with the shared library's expected hook names silently changes coverage.

## Test Signals

Signals are the shared library's config, wait, IPv4 ping, and IPv6 ping tests running under the mlxsw hook set.
