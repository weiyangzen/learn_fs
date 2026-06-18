<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/hid/hid-sony.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/hid/hid-sony.sh

## Purpose
This wrapper runs Sony/PlayStation HID hid-tools tests.

## Important APIs, Types, And Functions
It exports `TARGET=test_sony.py` and calls the shared runner.

## Control Flow
All test work is in `run-hid-tools-tests.sh` and the Python target.

## State And Persistence
It sets only the target environment variable.

## Dependencies And Integration Points
It depends on Sony/PlayStation HID and force-feedback related config as applicable.

## Risks
Vendor-specific kernel support controls whether the target can pass.

## Test Signals
Runner output for `test_sony.py` is the result signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/hid/hid-sony.sh -->
