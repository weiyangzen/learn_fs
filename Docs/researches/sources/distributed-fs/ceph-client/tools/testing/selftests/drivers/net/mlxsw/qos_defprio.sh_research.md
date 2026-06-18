# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/qos_defprio.sh

## Purpose

QoS default priority test for bridged traffic on mlxsw.

## Important APIs, Types, and Functions

Creates a two-netif bridge-like topology with H1 and SWP1 and defines `ping_ipv4`, `__test_defprio`, and `test_defprio`. It uses `ip link` VLAN priority maps or traffic-class counters through shared helpers.

## Control Flow

Setup initializes host/switch interfaces and forwarding context. The ping test confirms reachability. The default-priority test changes default priority handling, sends traffic, and verifies packets are accounted in the expected priority/queue path before restoring defaults.

## State and Persistence Behavior

State is limited to link priority/QoS settings, simple interface state, routes, and temporary counters.

## Dependencies and Integration Points

The script is part of the Linux kselftest networking suite copied under `sources/distributed-fs/ceph-client`. It depends on root privileges, real mlxsw Spectrum-capable switch ports exposed through `NETIFS`, iproute2 tools, `tc` flower offload, `devlink`, `ethtool`, `jq`, `bc`, kselftest helpers from `tools/testing/selftests/net/forwarding`, and traffic tools such as mausezahn or ping where referenced.

## Risks and Edge Cases

Default priority behavior is affected by VLAN tagging, ingress/egress qos maps, and driver defaults. Counter assertions can fail if previous tests leave priority maps or if traffic is classified before the setting takes effect.

## Test Signals

Signals are ping success and counter/log checks in `test_defprio`.
