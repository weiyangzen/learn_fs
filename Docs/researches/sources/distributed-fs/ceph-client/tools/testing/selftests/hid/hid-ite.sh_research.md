<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/hid/hid-ite.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/hid/hid-ite.sh

## Purpose
This wrapper runs ITE keyboard HID hid-tools tests.

## Important APIs, Types, And Functions
It exports `TARGET=test_ite_keyboard.py` and invokes the shared runner.

## Control Flow
No local logic beyond delegation.

## State And Persistence
It sets one environment variable.

## Dependencies And Integration Points
It depends on ITE HID support and the hid-tools test harness.

## Risks
Missing vendor driver support should be handled by the target/runner rather than this wrapper.

## Test Signals
The expected signal is successful execution or an appropriate skip/fail for `test_ite_keyboard.py`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/hid/hid-ite.sh -->
