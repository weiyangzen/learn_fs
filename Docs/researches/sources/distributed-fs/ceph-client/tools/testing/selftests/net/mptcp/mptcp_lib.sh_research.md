# sources/distributed-fs/ceph-client/tools/testing/selftests/net/mptcp/mptcp_lib.sh

## Purpose
`mptcp_lib.sh` is the shared support library for MPTCP shell selftests. It standardizes kselftest return codes, colored status output, TAP result collection, feature gating, namespace lifecycle, transfer-file checks, timeout cleanup, MPTCP event capture, and path-manager command abstraction.

## Important APIs, Types, And Functions
The script exports event constants such as `MPTCP_LIB_EVENT_ESTABLISHED`, address-family constants, and global result state arrays such as `MPTCP_LIB_SUBTESTS`. Result helpers include `mptcp_lib_result_pass()`, `mptcp_lib_result_fail()`, `mptcp_lib_result_skip()`, `mptcp_lib_result_code()`, and `mptcp_lib_result_print_all_tap()`. Feature and environment helpers include `mptcp_lib_check_mptcp()`, `mptcp_lib_check_kallsyms()`, `mptcp_lib_kallsyms_has()`, `mptcp_lib_kversion_ge()`, and `mptcp_lib_check_tools()`. Runtime helpers include `mptcp_lib_ns_init()`, `mptcp_lib_ns_exit()`, `mptcp_lib_wait_timeout()`, `mptcp_lib_kill_group_wait()`, `mptcp_lib_nstat_init()`, `mptcp_lib_get_counter()`, `mptcp_lib_make_file()`, and PM wrappers such as `mptcp_lib_pm_nl_add_endpoint()`.

## Control Flow
Consumers source the library, call feature checks, create namespaces with `mptcp_lib_ns_init()`, run subtests, and report results through TAP helpers. The TAP path increments ids, detects duplicate subtest names, tracks elapsed time since the previous result, and treats flaky subtests as ignored unless `SELFTESTS_MPTCP_LIB_OVERRIDE_FLAKY=1` is set. Namespace initialization delegates to `setup_ns` from the parent `lib.sh`, then enables `net.mptcp.enabled` in each namespace. PM wrappers dispatch either to `ip -n <ns> mptcp ...` after `mptcp_lib_set_ip_mptcp()` or to `./pm_nl_ctl` through `ip netns exec`.

## State, Persistence, And Dependencies
State is process-global shell state: result arrays, counters, color variables, selected PM backend, and temporary `nstat` histories under `/tmp/<namespace>.nstat` and `/tmp/<namespace>.out`. Cleanup helpers remove those nstat files and namespaces. The library depends on `../lib.sh` for generic kselftest namespace utilities and on external tools selected by each test (`ip`, `tc`, `ss`, iptables variants).

## Integration Points
Nearly every shell script in the MPTCP selftest directory relies on this file for output and guard behavior. It bridges higher-level tests to `pm_nl_ctl.c`, `ip mptcp`, `mptcp_connect`, `ss`, and MPTCP MIB counters. Event parsing helpers are coupled to the textual format emitted by `pm_nl_ctl events`.

## Risks
Because it is sourced, all variables and functions share the caller's shell namespace. PM wrapper argument parsing uses positional scans and limited quoting, reflecting compatibility with existing tests. Kallsyms and kernel-version checks are only approximations for feature support, so backports can need `SELFTESTS_MPTCP_LIB_NO_KVERSION_CHECK=1`. Counter reads from `nstat` can be missing on older kernels, causing skips or feature-expectation failures.

## Test Signals
The library's direct signals are TAP output, `[ OK ]`, `[SKIP]`, `[FAIL]`/`[IGNO]` lines, duplicate-result diagnostics, and printed socket/nstat diagnostics. For callers, reliable signals are correct namespace setup/cleanup, successful tool detection, valid transfer comparison, expected PM output formatting, and non-empty event/counter values when a feature is required.
