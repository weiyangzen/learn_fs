# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/qos_mc_aware.sh

## Purpose

Tests multicast-aware buffer admission so multicast overload does not unduly degrade unicast traffic, and vice versa.

## Important APIs, Types, and Functions

Defines a six-netif topology with H1/H2/H3, bridge domains, VLAN 111, pool-threshold tuning, `run_uc_measure_rate`, `test_mc_aware`, and `test_uc_aware`. It uses mausezahn, ping/ARP, ethtool per-priority counters, TBF/prio qdiscs, and `qos_lib.sh`.

## Control Flow

Setup configures unicast and multicast/ARP traffic paths, maps traffic to distinct priorities, shapes the egress side, and deliberately makes ingress quotas smaller than egress quotas. `test_mc_aware` measures UC throughput with and without MC overload and checks degradation bounds. `test_uc_aware` sends broadcast ARPs while UC overload is present and verifies responses continue to pass.

## State and Persistence Behavior

State includes bridges, VLAN priority maps, qdiscs, devlink pool thresholds, per-priority counters, and traffic generator loops. Defer cleanup restores thresholds and qdiscs.

## Dependencies and Integration Points

The script is part of the Linux kselftest networking suite copied under `sources/distributed-fs/ceph-client`. It depends on root privileges, real mlxsw Spectrum-capable switch ports exposed through `NETIFS`, iproute2 tools, `tc` flower offload, `devlink`, `ethtool`, `jq`, `bc`, kselftest helpers from `tools/testing/selftests/net/forwarding`, and traffic tools such as mausezahn or ping where referenced. It uses `qos_lib.sh` for rate measurement.

## Risks and Edge Cases

Rate-based checks are noisy and can fail on slow links, non-isolated hardware, or counter drift. The intended degradation window is narrow, so shaper and pool configuration must be exact. ARP/broadcast behavior also depends on bridge learning and flooding state.

## Test Signals

Signals are measured ingress/egress UC and MC throughput, bounded degradation percentages, and successful ARP response counts under overload.
