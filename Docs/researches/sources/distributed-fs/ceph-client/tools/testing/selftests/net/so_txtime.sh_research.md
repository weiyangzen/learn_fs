<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/so_txtime.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/so_txtime.sh

## Purpose

`so_txtime.sh` is the regression wrapper for `SO_TXTIME`. It creates two network namespaces connected by veth, configures addresses and qdiscs, and runs paired TX/RX instances of `so_txtime`.

## Important APIs, Types, and Functions

Functions are `cleanup`, `run_test`, `do_test`, and `do_fail_test`. The script uses `ip netns`, `ip link`, IPv4/IPv6 address assignment, `tc qdisc`, `date +%s%N --date`, and `ip netns exec`.

## Control Flow

After namespace/veth setup, it installs `fq` on the TX veth and runs several expected-success monotonic-clock tests. Then it attempts to replace the qdisc with `etf clockid CLOCK_TAI delta 400000`; if supported, it runs expected-failure and expected-success TAI tests. TX and RX are synchronized with a start time 0.1 seconds in the future.

## State and Persistence Behavior

All network devices, addresses, and qdiscs are namespace-scoped. Cleanup deletes both namespaces. The script accumulates `ret` and may convert failures to success under `KSFT_MACHINE_SLOW` when not a skip.

## Dependencies and Integration Points

It depends on root privileges, veth, IPv4/IPv6, `tc` support for `fq` and optionally `etf`, GNU `date --date`, and the `so_txtime` binary. It integrates `SO_TXTIME` with qdisc scheduling behavior.

## Risks and Edge Cases

`set -e` is disabled during test execution so individual failures accumulate. Timing is tight and can be noisy on slow or virtualized machines. If `etf` is unavailable, the script returns skip only if no earlier failure occurred.

## Test Signals

Success prints `OK. All tests passed`. Important signals include expected immediate-send behavior, delayed delivery order, reordered txtime delivery, ETF rejecting invalid or missed txtime cases, and proper skip when ETF is not supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/so_txtime.sh -->
