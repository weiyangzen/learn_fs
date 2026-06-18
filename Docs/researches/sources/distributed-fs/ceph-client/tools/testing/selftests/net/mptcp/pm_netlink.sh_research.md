# sources/distributed-fs/ceph-client/tools/testing/selftests/net/mptcp/pm_netlink.sh

## Purpose
`pm_netlink.sh` is a path-manager netlink smoke and compatibility test. It validates endpoint add/get/dump/delete/flush behavior, endpoint id allocation and wraparound, flag changes, hard limits, duplicate handling, and receive/subflow limit setting for both `pm_nl_ctl` and optionally `ip mptcp`.

## Important APIs, Types, And Functions
The script sources `mptcp_lib.sh` and uses PM abstraction helpers for endpoint and limit operations. Local helpers include `format_limits()`, `get_limits()`, `format_endpoints()`, `get_endpoint()`, `change_address()`, `set_limits()`, `add_endpoint()`, `del_endpoint()`, `flush_endpoint()`, `show_endpoints()`, `change_endpoint()`, and `check()`. It uses `mptcp_lib_check_output()` to compare command stdout and return codes.

## Control Flow
After `-i` option parsing, it creates one namespace, captures default limits, and runs a linear sequence of assertions. It starts with empty endpoint dumps, adds simple and flagged endpoints, deletes one, verifies duplicate-add errors, fills endpoint ids through the hard limit, exercises ids `10..255`, flushes, and checks that unknown flags are ignored only by `pm_nl_ctl`. It then validates invalid limit updates do not change defaults, sets limits to `8/8`, tests explicit ids and id wraparound, and changes endpoint flags through `backup`, `nobackup`, and optionally `fullmesh`/`nofullmesh`/combined flags.

## State, Persistence, And Dependencies
State is contained in one temporary namespace, one stderr temp file, and the namespace-local MPTCP endpoint/limit tables. Cleanup removes the namespace and temp file. The test depends on MPTCP sysctls, `ip`, and either in-tree `pm_nl_ctl` or system `ip mptcp`.

## Integration Points
This is the focused PM netlink CLI/API conformance script used by the selftest suite. It exercises the formatting wrappers in `mptcp_lib.sh`, the `pm_nl_ctl.c` implementation, and the kernel path-manager UAPI. With `-i`, it cross-checks that `ip mptcp` output can be normalized to expected strings.

## Risks
The assertions compare exact stdout, so formatting changes in `ip mptcp` or `pm_nl_ctl` can fail the test even if kernel behavior is correct. The `unknown` flag case is intentionally not available through `ip mptcp`. Default limits are only asserted when `SELFTESTS_MPTCP_LIB_EXPECT_ALL_FEATURES=1`, which avoids false failures on older kernels but can hide default drift in normal runs.

## Test Signals
Pass signals are exact expected output and return codes for each `check()` plus final TAP output. Failures show command stderr or unexpected stdout. Important failure classes are duplicate address acceptance, id allocator regressions, hard-limit violations, incorrect flag changes, and limit-set validation bugs.
