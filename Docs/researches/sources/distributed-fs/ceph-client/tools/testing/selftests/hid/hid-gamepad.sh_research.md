<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/hid/hid-gamepad.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/hid/hid-gamepad.sh

## Purpose
This wrapper runs hid-tools gamepad tests.

## Important APIs, Types, And Functions
It exports `TARGET=test_gamepad.py` and calls the shared hid-tools runner.

## Control Flow
Execution is delegated to `run-hid-tools-tests.sh`.

## State And Persistence
Only `TARGET` is set.

## Dependencies And Integration Points
It integrates gamepad HID scenarios with the kselftest HID suite.

## Risks
All environment and dependency checks are external to this wrapper.

## Test Signals
The result is the shared runner's result for `test_gamepad.py`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/hid/hid-gamepad.sh -->
