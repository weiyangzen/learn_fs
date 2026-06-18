# sources/distributed-fs/ceph-client/tools/time/udelay_test.sh

## Purpose
`udelay_test.sh` is a shell-based kernel self-test driver for the `udelay_test` module. It writes delay values into `/sys/kernel/debug/udelay_test`, records the module's reported results, and fails if any reported line contains `FAIL`.

## Important APIs, Types, and Functions
The script defines `MODULE_NAME=udelay_test` and `UDELAY_PATH=/sys/kernel/debug/udelay_test`. `setup()` loads the module with `/sbin/modprobe -q` and creates a `mktemp` output file. `test_one()` writes one delay value and appends the sysfs output through `tee`. `cleanup()` removes the temp file and unloads the module. A trap runs cleanup on exit.

## Control Flow
After setup, the script tests delays from 1 to 199 by 1, 200 to 490 by 10, and 500 to 2000 by 100. It then counts lines containing `FAIL` in the temporary output. If `grep -c FAIL` succeeds, it prints an error and returns `1`; otherwise it exits with the default `retcode`.

## State and Persistence
Transient state is the temp file path and the loaded kernel module. Persistent system impact is limited to loading/unloading the module and writing debugfs control values. Cleanup is trap-based.

## Dependencies and Integration Points
The script needs bash, root or sufficient privileges, debugfs mounted at `/sys/kernel/debug`, `/sbin/modprobe`, the `udelay_test` kernel module, `mktemp`, `tee`, and `grep`.

## Risks and Edge Cases
`retcode` is not initialized before `exit $retcode`, so a fully passing run may exit with an empty argument, which shell treats like `exit` with the status of the last command. That is usually zero after a non-matching `grep`, but it is implicit. If setup fails, writes can fail later rather than giving a precise setup error. `mktemp` failure is not checked. Cleanup unloads the module even if it was loaded before the test.

## Test Signals
Run as root with debugfs mounted and confirm pass/fail exit status. Inject a fake `FAIL` line or use a debugfs fixture to verify failure reporting. Also test missing module, missing debugfs, and interrupted execution to verify cleanup behavior.
