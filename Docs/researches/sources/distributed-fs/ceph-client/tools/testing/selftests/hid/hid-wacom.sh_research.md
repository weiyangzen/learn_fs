<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/hid/hid-wacom.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/hid/hid-wacom.sh

## Purpose
This wrapper runs Wacom generic HID hid-tools tests.

## Important APIs, Types, And Functions
It exports `TARGET=test_wacom_generic.py` and invokes `bash ./run-hid-tools-tests.sh`.

## Control Flow
Execution is delegated to the shared hid-tools runner.

## State And Persistence
It only sets the test target environment variable.

## Dependencies And Integration Points
It depends on Wacom HID support and the shared hid-tools test suite.

## Risks
The wrapper has no local dependency checks and assumes the relative runner exists.

## Test Signals
The expected signal is the shared runner result for `test_wacom_generic.py`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/hid/hid-wacom.sh -->
