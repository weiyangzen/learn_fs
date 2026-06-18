<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/hid/hid-multitouch.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/hid/hid-multitouch.sh

## Purpose
This wrapper runs HID multitouch hid-tools tests.

## Important APIs, Types, And Functions
It exports `TARGET=test_multitouch.py` and invokes the shared runner.

## Control Flow
The script delegates directly to `run-hid-tools-tests.sh`.

## State And Persistence
It only sets `TARGET`.

## Dependencies And Integration Points
It depends on HID multitouch kernel support and hid-tools.

## Risks
Missing multitouch support should be represented in runner output; the wrapper itself cannot distinguish it.

## Test Signals
The meaningful signal is the shared runner result for `test_multitouch.py`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/hid/hid-multitouch.sh -->
