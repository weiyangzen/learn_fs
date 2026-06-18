<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/hid/hid-keyboard.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/hid/hid-keyboard.sh

## Purpose
This wrapper runs generic keyboard HID hid-tools tests.

## Important APIs, Types, And Functions
It exports `TARGET=test_keyboard.py` and invokes `bash ./run-hid-tools-tests.sh`.

## Control Flow
The shared runner owns setup and result handling.

## State And Persistence
Only `TARGET` is set.

## Dependencies And Integration Points
It depends on HID keyboard functionality exposed to hid-tools.

## Risks
Relative path execution assumptions are the only local risk.

## Test Signals
Runner output for `test_keyboard.py` is the meaningful signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/hid/hid-keyboard.sh -->
