<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/hid/hid-mouse.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/hid/hid-mouse.sh

## Purpose
This wrapper runs generic HID mouse hid-tools tests.

## Important APIs, Types, And Functions
It exports `TARGET=test_mouse.py` and calls the shared runner.

## Control Flow
No local branching; all behavior is delegated.

## State And Persistence
It only mutates the child environment.

## Dependencies And Integration Points
It integrates mouse HID scenarios into the kselftest HID suite.

## Risks
The wrapper provides no local dependency checks.

## Test Signals
Expected pass/fail/skip is produced by the shared runner for `test_mouse.py`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/hid/hid-mouse.sh -->
