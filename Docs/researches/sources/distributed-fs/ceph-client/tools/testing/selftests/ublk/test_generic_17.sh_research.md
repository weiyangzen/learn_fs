# sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_generic_17.sh

## Purpose
This fault-injection recovery test verifies that a device can be deleted after a recovery daemon dies while only part of a queue's I/O has been fetched.

## Important APIs, Types, and Functions
It uses `_add_ublk_dev -t fault_inject -r 1`, `__ublk_kill_daemon()`, foreground `${UBLK_PROG} recover ... --die_during_fetch 1`, and `_ublk_del_dev()`.

## Control Flow
The script creates a recoverable fault-inject device, kills the daemon and expects the device to become `QUIESCED`, then starts recovery in foreground with `die_during_fetch` enabled. It expects exit code 137 from SIGKILL and then deletes the device, relying on delete to complete only after teardown finishes.

## State and Persistence
It creates a ublk device in recovery mode and intentionally kills daemon processes. Cleanup deletes the device and temp directory.

## Dependencies and Integration Points
It depends on `fault_inject` pre-fetch kill behavior, ublk recovery/quiesce state handling, and daemon teardown paths in kernel and `kublk`.

## Risks
If teardown hangs, `_ublk_del_dev()` may hang until external timeout. The script references `$action` in one error message without defining it, but that does not affect control flow.

## Test Signals
Pass means recovery death produces SIGKILL exit status and device deletion succeeds afterward, proving incomplete recovery teardown completes.
