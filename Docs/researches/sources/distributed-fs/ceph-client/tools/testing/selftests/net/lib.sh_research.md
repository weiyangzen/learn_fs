# sources/distributed-fs/ceph-client/tools/testing/selftests/net/lib.sh

## Purpose
This Bash library is the shared harness for Linux networking selftests. It provides kselftest status constants, namespace setup and cleanup, wait helpers, test result aggregation, tc/qdisc counter utilities, netdevsim helpers, and automatically deferred cleanup wrappers for temporary network configuration.

## Important APIs and Functions
The exported surface is function-oriented. `setup_ns`, `cleanup_ns`, `cleanup_all_ns`, and `in_all_ns` manage randomly suffixed network namespaces through the global `NS_LIST`. `busywait`, `slowwait`, `busywait_for_counter`, and `slowwait_for_counter` poll commands until predicates succeed. `ksft_status_merge`, `ksft_exit_status_merge`, `log_test`, `check_err`, `check_fail`, `check_err_fail`, `xfail`, `xfail_on_slow`, `omit_on_slow`, and `xfail_on_veth` implement kselftest-style pass/fail/skip/xfail result handling. `create_netdevsim`, `create_netdevsim_port`, and `cleanup_netdevsim` manipulate the netdevsim bus. `tc_rule_stats_get`, `tc_rule_handle_stats_get`, `tc_set_flower_counter`, and `tc_get_flower_counter` read or create tc statistics. The `adf_*` functions wrap `ip`, `bridge`, and route changes with deferred reversal.

## Control Flow and State
Tests source this file, call setup functions, then either run individual checks or invoke `tests_run`, which executes `TESTS` or `ALL_TESTS` inside `in_defer_scope`. State is persisted only in shell globals: `NS_LIST`, `EXIT_STATUS`, `RET`, `retmsg`, and `FAIL_TO_XFAIL`. Namespace cleanup kills remaining namespace processes before deleting namespaces and busy-waits for disappearance. Deferred cleanup comes from `lib/sh/defer.sh`, so changes made with `adf_*` are unwound in reverse scope order.

## Dependencies and Integration
The library assumes Bash, `iproute2`, `jq`, `tc`, `bridge`, `sysctl`, `modprobe`, `udevadm`, `netdevsim`, and kselftest exit conventions. It is integrated by many shell tests under `tools/testing/selftests/net`, including the lwt and macvlan scripts in this subset.

## Risks and Test Signals
The helpers require root and kernel namespace support. `eval` is used for namespace variable assignment and deferred command execution, so callers must pass trusted arguments. `mktemp -u` creates names before use and can theoretically race, though randomized names reduce collisions. Successful tests usually emit formatted `TEST:` lines and use `EXIT_STATUS`; failure signals include nonzero `RET`, failed namespace deletion warnings, tc counter mismatches, or skipped tests when required tools are absent.
