# sources/distributed-fs/ceph-client/tools/testing/selftests/x86/bugs/its_sysfs.py

## Purpose

`its_sysfs.py` validates the `/sys/devices/system/cpu/vulnerabilities/indirect_target_selection` status string against CPU features and kernel command-line mitigation choices.

## Important APIs, Types, and Functions

The script imports all helpers from `common.py`, reads `bug = "indirect_target_selection"`, and defines expected strings for aligned thunks, retpoline plus RSB stuffing, VM-exit-only vulnerability, and vulnerable state. `check_mitigation()` implements the policy matrix. It uses `basic_checks_sufficient()` for common `Not affected` and explicit disabled/vulnerable cases.

## Control Flow

The script prints a kselftest header, sets a one-test plan, prints the found mitigation string, and then either lets `basic_checks_sufficient()` report a result or runs `check_mitigation()`. The detailed checker compares the exact mitigation string against command-line options such as `indirect_target_selection=stuff`, `indirect_target_selection=vmexit`, Spectre v2 retpoline status, retbleed stuffing status, and CPU feature text `its_native_only`.

## State and Persistence Behavior

The script is read-only. It reads `/proc/cpuinfo`, `/proc/cmdline`, and vulnerability sysfs files.

## Dependencies and Integration Points

It depends on the Python kselftest framework and the shared `common.py` helpers. It is also used as the guest payload by `its_permutations.py`.

## Risks and Edge Cases

The logic uses exact mitigation strings, so wording changes in sysfs can produce unknown/fail results. Multiple independent `if` blocks in `check_mitigation()` can fall through to `bug_status_unknown()` after a failure path unless an earlier branch returns. Missing sysfs files are handled through common helper behavior.

## Test Signals

The expected signal is one kselftest result: pass for matching mitigation policy, fail with found/expected diagnostics for inconsistent sysfs text, or unknown status diagnostics for unrecognized strings.
