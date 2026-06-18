# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/qos_lib.sh

## Purpose

Small shared QoS measurement helper library.

## Important APIs, Types, and Functions

Exports `check_rate` and `measure_rate`. `check_rate` compares measured ingress/egress rates against expectations, while `measure_rate` samples ethtool byte counters over time and returns human-readable or numeric throughput values for callers.

## Control Flow

Callers pass devices, counters, and labels. The helpers sample counters, sleep, calculate rates with `bc`/shell arithmetic, and report errors through kselftest `check_err` style functions.

## State and Persistence Behavior

State is invocation-local except for reading interface counters. It does not modify network configuration.

## Dependencies and Integration Points

Depends on ethtool-stat helper functions from the broader forwarding library, `sleep`, arithmetic tools, and caller-provided logging/check functions.

## Risks and Edge Cases

Counter wrap, low traffic volume, or asynchronous counter updates can skew rates. The helpers assume the named counters exist on the target devices and that no unrelated traffic contaminates measurements.

## Test Signals

Signals are returned rate values and caller-visible check failures when measured throughput falls outside expected bounds.
