# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/router_scale.sh

## Purpose

Scale helper for programming many routes through a two-port mlxsw router.

## Important APIs, Types, and Functions

Defines `router_h1_create`, `router_h2_create`, `router_create`, `router_routes_create`, `router_routes_destroy`, `wait_for_routes`, `router_test`, and cleanup. It creates host routes and many switch routes, then verifies reachability/offload behavior.

## Control Flow

Setup creates H1/H2 with routed subnets and switch router ports. `router_routes_create` programs a requested number of routes, `wait_for_routes` waits for programming/offload to settle, and `router_test` validates behavior for the count and expected-failure mode. Cleanup deletes routes and tears down router/host state.

## State and Persistence Behavior

State includes large route tables, host routes, router-port addresses, forwarding sysctls, and any offload state associated with the programmed routes.

## Dependencies and Integration Points

The script is part of the Linux kselftest networking suite copied under `sources/distributed-fs/ceph-client`. It depends on root privileges, real mlxsw Spectrum-capable switch ports exposed through `NETIFS`, iproute2 tools, `tc` flower offload, `devlink`, `ethtool`, `jq`, `bc`, kselftest helpers from `tools/testing/selftests/net/forwarding`, and traffic tools such as mausezahn or ping where referenced.

## Risks and Edge Cases

Scale route insertion can be slow and resource-dependent. Expected counts must match ASIC route capacity and profile. If route cleanup misses entries, later scale iterations can start from a polluted table.

## Test Signals

Signals are successful route insertion or expected failure, route wait completion, and traffic/reachability validation from the helper.
