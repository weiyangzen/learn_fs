<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/hid/hid-apple.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/hid/hid-apple.sh

## Purpose
This wrapper runs the hid-tools Apple keyboard test target.

## Important APIs, Types, And Functions
It exports `TARGET=test_apple_keyboard.py` and invokes `bash ./run-hid-tools-tests.sh`.

## Control Flow
The script delegates all setup, execution, and result handling to the shared hid-tools runner.

## State And Persistence
It only sets an environment variable for the child process.

## Dependencies And Integration Points
It depends on `run-hid-tools-tests.sh`, the `tests` tree, and kernel Apple HID support.

## Risks
Any failure/skip semantics are hidden in the shared runner. Running from the wrong directory breaks the relative runner path.

## Test Signals
The expected signal is the shared runner executing `test_apple_keyboard.py` and propagating its result.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/hid/hid-apple.sh -->
