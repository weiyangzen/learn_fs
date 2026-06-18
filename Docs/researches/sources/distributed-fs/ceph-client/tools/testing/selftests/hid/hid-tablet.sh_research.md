<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/hid/hid-tablet.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/hid/hid-tablet.sh

## Purpose
This wrapper runs generic HID tablet hid-tools tests.

## Important APIs, Types, And Functions
It exports `TARGET=test_tablet.py` and invokes `bash ./run-hid-tools-tests.sh`.

## Control Flow
The wrapper delegates fully to the shared runner.

## State And Persistence
It only sets `TARGET`.

## Dependencies And Integration Points
It integrates tablet HID test coverage into kselftest.

## Risks
No local validation exists for tablet support or hid-tools availability.

## Test Signals
The shared runner's result for `test_tablet.py` is the expected signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/hid/hid-tablet.sh -->
