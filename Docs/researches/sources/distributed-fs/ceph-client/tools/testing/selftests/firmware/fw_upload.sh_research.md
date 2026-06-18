<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/firmware/fw_upload.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/firmware/fw_upload.sh

## Purpose
This script validates the firmware upload sysfs interface using the `test_firmware` driver, covering registration, data transfer, cancellation, error injection, size rejection, and multiple upload devices.

## Important APIs, Types, And Functions
Important helpers are `upload_finish()`, `upload_fw()`, `verify_fw()`, `inject_error()`, `await_status()`, `await_idle()`, `expect_error()`, `random_firmware()`, `test_upload_cancel()`, `test_error_handling()`, and `test_fw_too_big()`. It uses `$DIR/upload_register`, `$DIR/upload_unregister`, `$DIR/<name>/loading`, `$DIR/<name>/data`, `$DIR/<name>/status`, `$DIR/<name>/error`, `$DIR/<name>/cancel`, `$DIR/config_upload_name`, and `$DIR/upload_read`.

## Control Flow
After upload support verification, it registers three firmware upload devices. It injects user-abort at each progress state, injects all defined hardware/error codes at each progress state, tests oversized firmware, uploads random firmware to three devices, verifies readback, then unregisters them.

## State And Persistence
It creates kernel upload device instances, temporary random files under `/tmp`, and sysfs upload state. `upload_finish()` unregisters remaining devices through an EXIT trap.

## Dependencies And Integration Points
It requires `CONFIG_FW_UPLOAD`, the `test_firmware` upload test ABI, root, `dd`, `/dev/urandom`, and `fw_lib.sh`.

## Risks
The polling loop in `await_status()` is short and assumes status changes within about 50 milliseconds. Random firmware temp files for successful uploads are not explicitly removed after verification. Error strings must match the kernel test driver's exact accepted values.

## Test Signals
Pass signals include correct cancellation errors of form `<state>:user-abort`, correct injected errors for every state/error pair, `preparing:invalid-file-size` for too-large upload, and byte-for-byte readback of all three random firmware images.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/firmware/fw_upload.sh -->
