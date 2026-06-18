<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/firmware/fw_fallback.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/firmware/fw_fallback.sh

## Purpose
This script tests firmware loader sysfs fallback behavior, including manual loading, cancellation, timeout handling, custom fallback triggers, and signal behavior for synchronous requests.

## Important APIs, Types, And Functions
Core helpers are `load_fw()`, `load_fw_cancel()`, `load_fw_custom()`, `load_fw_custom_cancel()`, `load_fw_fallback_with_child()`, `test_syfs_timeout()`, `run_sysfs_main_tests()`, and `run_sysfs_custom_load_tests()`. It manipulates `$DIR/trigger_request`, `$DIR/trigger_custom_fallback`, per-request `loading` and `data` files, `/sys/class/firmware/timeout`, and `/dev/test_firmware`.

## Control Flow
The script sources `fw_lib.sh`, checks modules/config, prepares a temporary firmware file, and installs `test_finish` as cleanup. It blocks kernel requests in the background, waits for the fallback directory to appear, writes `1`, data, and `0` to complete loads, or `-1` to cancel. Main tests run only when fallback support is detected; custom load tests run separately.

## State And Persistence
It mutates firmware class timeout, sysfs fallback request directories, `/dev/test_firmware` contents, and temp files. Cleanup restores timeout/path/proc fallback defaults and removes temporary firmware data.

## Dependencies And Integration Points
It requires root, `test_firmware`, firmware loader user helper fallback support for main fallback tests, and the shared environment exported by `fw_lib.sh`.

## Risks
Distribution udev rules that immediately cancel firmware fallback requests can make the timeout test fail. The script relies on polling loops with short countdowns and assumes request names do not collide with installed firmware.

## Test Signals
Expected signals are timeout failure for nonexistent firmware, mismatched content when intentionally loading the script, successful manual load of the temp firmware, successful cancel paths, SIGCHLD not canceling sync firmware requests, and custom fallback load/cancel success.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/firmware/fw_fallback.sh -->
