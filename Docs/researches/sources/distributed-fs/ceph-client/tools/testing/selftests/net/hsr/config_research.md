# sources/distributed-fs/ceph-client/tools/testing/selftests/net/hsr/config

## Purpose

This config fragment declares kernel configuration requirements for the HSR/PRP selftests.

## Important APIs, Types, and Functions

It requests `CONFIG_BRIDGE=y`, `CONFIG_HSR=y`, `CONFIG_IPV6=y`, `CONFIG_NET_SCH_NETEM=m`, `CONFIG_VETH=y`, and `CONFIG_VLAN_8021Q=m`.

## Control Flow

There is no executable control flow. The selftest build or configuration tooling reads these symbols as prerequisites.

## State and Persistence Behavior

The file is static metadata and owns no runtime state.

## Dependencies and Integration Points

It integrates with kselftest configuration checking. The listed options map directly to HSR/PRP device creation, veth namespaces, bridge RedBox tests, IPv6 ping tests, VLAN subinterface tests, and netem fault injection.

## Risks and Edge Cases

If a symbol is missing or built incompatibly, scripts may skip, fail during setup, or fail only in optional phases such as VLAN or netem fault tests. Module symbols require loadable module availability at runtime.

## Test Signals

A configured kernel satisfying these symbols should be able to create the topologies used by the HSR test scripts.
