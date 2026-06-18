# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/qos_pfc.sh

## Purpose

End-to-end Priority Flow Control test for lossless traffic through overflow and PFC pools.

## Important APIs, Types, and Functions

Builds a six-netif topology and documents a two-stage path where priority-1 traffic fills a PFC pool, pauses an upstream port, and drains through shaped egress. It configures devlink pools 0/4, 1/5, 2/6, ETS qdiscs, DCB buffers/PFC, VLAN qos maps, bridges, and shapers.

## Control Flow

Setup creates H1/H2, four switch ports, VLAN 111, two bridge domains, static pool sizes, per-port pool thresholds, ETS scheduling, PFC on SWP3/SWP4, and headroom sizing that accounts for port lanes. The test sends a 10 MB priority-1 burst, samples ingress and egress priority counters, and checks that received bytes closely match sent bytes despite backpressure.

## State and Persistence Behavior

State is extensive runtime QoS state: devlink pool sizes/thresholds, DCB PFC and buffer settings, qdiscs, VLAN devices, bridges, shapers, and ethtool counters. Cleanup restores pools in reverse order and deletes qdiscs/bridges/VLANs.

## Dependencies and Integration Points

The script is part of the Linux kselftest networking suite copied under `sources/distributed-fs/ceph-client`. It depends on root privileges, real mlxsw Spectrum-capable switch ports exposed through `NETIFS`, iproute2 tools, `tc` flower offload, `devlink`, `ethtool`, `jq`, `bc`, kselftest helpers from `tools/testing/selftests/net/forwarding`, and traffic tools such as mausezahn or ping where referenced.

## Risks and Edge Cases

This is one of the most stateful scripts in the group. It is sensitive to cell-size rounding, lane count, shaper rate, pool sizing, pause behavior, and counter precision. Any missed restore can poison subsequent QoS tests.

## Test Signals

Signals are ping reachability, priority-1 ingress/egress byte deltas, percentage bounds for injected traffic, loss check between ingress and egress, and final `log_test PFC`.
