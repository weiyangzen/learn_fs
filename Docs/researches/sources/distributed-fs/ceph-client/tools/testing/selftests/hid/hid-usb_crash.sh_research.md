<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/hid/hid-usb_crash.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/hid/hid-usb_crash.sh

## Purpose
This wrapper runs HID USB crash regression tests from hid-tools.

## Important APIs, Types, And Functions
It exports `TARGET=test_usb_crash.py` and calls the shared runner.

## Control Flow
No local control flow beyond delegation.

## State And Persistence
It only mutates the environment for the child process.

## Dependencies And Integration Points
It depends on USB HID support and the hid-tools test harness.

## Risks
The wrapper does not isolate crash-regression effects; any safety/skip handling must be in the shared runner and target tests.

## Test Signals
The shared runner should execute `test_usb_crash.py` and return its kselftest result.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/hid/hid-usb_crash.sh -->
