# sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/test-sysfs.sh

## Purpose

`test-sysfs.sh` validates the livepatch sysfs interface: permissions, values, object patched state, replace flag, transition state, and stack-order updates as patches are loaded and removed.

## Important APIs, Types, and Functions

It uses `check_sysfs_rights()`, `check_sysfs_value()`, `load_lp()`, `load_mod()`, `disable_lp()`, and modules `test_klp_livepatch`, `test_klp_callbacks_demo`, `test_klp_syscall`, and `test_klp_atomic_replace`.

## Control Flow and State

The script first checks base livepatch directory and file modes/values, then verifies a target module's `patched` file flips from 0 to 1 to 0 across module load/unload. It separately validates `replace=1`, `replace=0`, and stack order renumbering after removing a middle patch.

## Dependencies and Integration Points

It depends on livepatch sysfs layout under `/sys/kernel/livepatch`, module notifier state, `stat`, and exact dmesg checking.

## Risks and Test Signals

Risks include sysfs ABI permission regressions, stale object `patched` values, wrong replace reporting, and stack-order gaps after unload. Signals are exact mode strings, expected file contents, and matching dmesg transcripts.
