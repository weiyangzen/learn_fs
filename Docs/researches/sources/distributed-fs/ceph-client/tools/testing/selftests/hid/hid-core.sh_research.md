<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/hid/hid-core.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/hid/hid-core.sh

## Purpose
This wrapper runs core HID hid-tools tests.

## Important APIs, Types, And Functions
It exports `TARGET=test_hid_core.py` and calls `bash ./run-hid-tools-tests.sh`.

## Control Flow
The wrapper has no local branching; the shared runner performs the test.

## State And Persistence
It only sets `TARGET`.

## Dependencies And Integration Points
It depends on core HID, UHID/hidraw support as required by hid-tools, and the shared runner.

## Risks
Relative invocation requires the script to run from the HID selftest directory.

## Test Signals
Pass/fail/skip comes from `test_hid_core.py` through the shared runner.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/hid/hid-core.sh -->
