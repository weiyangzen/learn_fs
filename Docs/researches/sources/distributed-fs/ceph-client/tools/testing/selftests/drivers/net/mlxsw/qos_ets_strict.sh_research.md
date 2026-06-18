# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/qos_ets_strict.sh

## Purpose

ETS strict-priority scheduler validation under mlxsw with measured traffic rates.

## Important APIs, Types, and Functions

Builds a six-netif topology, sources `qos_lib.sh`, and uses devlink pool helpers. Important functions are H1/H2/H3 setup, `switch_create`, `rel`, `run_hi_measure_rate`, and `test_ets_strict`.

## Control Flow

Setup configures hosts, switch ports, ETS qdiscs, traffic priorities, shaping, and devlink buffer/pool state. The test measures baseline and high-priority rates, then verifies strict scheduling behavior by comparing relative throughput while competing traffic is present.

## State and Persistence Behavior

State includes ETS qdisc hierarchy, VLAN priority maps, shapers, devlink pool thresholds, bridge/routing setup, and traffic generator processes.

## Dependencies and Integration Points

The script is part of the Linux kselftest networking suite copied under `sources/distributed-fs/ceph-client`. It depends on root privileges, real mlxsw Spectrum-capable switch ports exposed through `NETIFS`, iproute2 tools, `tc` flower offload, `devlink`, `ethtool`, `jq`, `bc`, kselftest helpers from `tools/testing/selftests/net/forwarding`, and traffic tools such as mausezahn or ping where referenced. It also depends on `qos_lib.sh` rate measurement helpers.

## Risks and Edge Cases

Throughput assertions are inherently noisy and require stable link speed, no external traffic, and correct shaper operation. Hardware generation differences can require xfail gating. Cleanup must remove qdiscs and restore devlink thresholds.

## Test Signals

Signals are ping success, measured rates above expected thresholds, relative-rate checks, and `log_test` for strict ETS.
