# sources/distributed-fs/ceph-client/tools/testing/selftests/sysctl/sysctl.sh

## Purpose
Runs a comprehensive shell-based suite against the proc sysctl interface and the `test_sysctl` kernel test module. It validates numeric, string, bitmap, boot parameter, registration, mount-point, empty-directory, and u8 range-check behavior.

## Important APIs, Types, And Functions
Important globals include `ALL_TESTS`, `SYSCTL`, `PROD_SYSCTL`, `WRITES_STRICT`, `PAGE_SIZE`, `MAX_DIGITS`, `INT_MAX`, `UINT_MAX`, `TARGET`, `TEST_STR`, `ORIG`, and `rc`. Setup helpers are `test_reqs()`, `allow_user_defaults()`, `check_production_sysctl_writes_strict()`, and `load_req_mod()`. Validation helpers include `reset_vals()`, `set_orig()`, `verify()`, `verify_diff_proc_file()`, `check_failure()`, `run_numerictests()`, `run_wideint_tests()`, `run_limit_digit*()`, `run_stringtests()`, and `run_bitmaptest()`. Test entry points are `sysctl_test_0001()` through `sysctl_test_0012()`.

## Control Flow
The script requires root plus `perl`, `getconf`, and `diff`, sets defaults, forces or checks `kernel/sysctl_writes_strict`, loads `test_sysctl` if `/proc/sys/debug/test_sysctl` is missing, installs an EXIT trap to restore the original target and writes-strict value, then parses CLI arguments. Default mode runs all enabled tests from `ALL_TESTS`; `-t`, `-s`, `-c`, and `-w` select count or watch modes. Individual tests construct `TARGET`, reset it, save original values, then run reusable numeric/string/bitmap boundary tests or direct structural checks.

## State And Persistence
The script mutates live sysctl files under `/proc/sys/debug/test_sysctl` and may temporarily set `/proc/sys/kernel/sysctl_writes_strict` to `1`, restoring the old value in `test_finish()`. It uses temporary files from `mktemp` for expected data and proc dumps. Module loading can persist the `test_sysctl` module beyond the script's lifetime.

## Dependencies And Integration Points
Depends on root privileges, debug test sysctl module or built-in support, production procfs, shell utilities, dmesg for u8 range checks, and kselftest skip code 4. It integrates with `Makefile` as `TEST_PROGS`.

## Risks
The script touches a production sysctl setting and must restore it reliably; abrupt termination outside the EXIT trap could leave strict writes changed. Some variables are unquoted in tests, which is typical here but fragile. `run_bitmaptest()` uses random lengths and bit ranges, making exact failures less reproducible. Boot-parameter test 0007 is skipped unless the kernel was booted with the expected built-in parameter. dmesg-based checks can be polluted by previous runs.

## Test Signals
Signals include successful write/verify/reset cycles, strict rejection of out-of-range wide integer inputs, PAGE_SIZE space-prefix boundary behavior, string maxlen/null-termination checks, bitmap round-trip diff, expected skips for unavailable boot-param conditions, correct missing directories for unregister/mount error tests, and exactly one u8 over/under range warning in dmesg.
