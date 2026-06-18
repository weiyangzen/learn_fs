<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/firmware/fw_run_tests.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/firmware/fw_run_tests.sh

## Purpose
This top-level firmware selftest runner orchestrates namespace, filesystem, fallback, and upload tests under several emulated firmware loader configurations.

## Important APIs, Types, And Functions
It sources `fw_lib.sh`, defines `run_tests()`, `run_test_config_0001()`, `run_test_config_0002()`, and `run_test_config_0003()`, and toggles fallback behavior through `proc_set_force_sysfs_fallback()` and `proc_set_ignore_sysfs_fallback()`.

## Control Flow
The script requires modules/setup, runs `fw_namespace $DIR/trigger_request`, then either runs three emulated configurations when `force_sysfs_fallback` exists or runs the three subtests once under the current kernel config. Each config calls `fw_filesystem.sh`, `fw_fallback.sh`, and `fw_upload.sh`.

## State And Persistence
It mutates proc firmware fallback toggles and relies on subtests to restore per-test settings. The exported `HAS_FW_*` variables are recalculated by `fw_lib.sh`.

## Dependencies And Integration Points
It integrates all firmware selftest scripts and the compiled namespace helper. It requires the `test_firmware` module and root privileges through `check_mods()`.

## Risks
Because it uses `set -e`, an unhandled failure in any subtest aborts later configurations. Running all emulations changes global firmware loader proc knobs between subtests, making cleanup ordering important.

## Test Signals
A successful run prints the namespace `OK` and completes filesystem, fallback, and upload tests for each supported/emulated configuration without leaving proc knobs forced.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/firmware/fw_run_tests.sh -->
