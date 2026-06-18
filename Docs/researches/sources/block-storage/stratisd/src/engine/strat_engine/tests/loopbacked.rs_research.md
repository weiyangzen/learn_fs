# File Research: sources/block-storage/stratisd/src/engine/strat_engine/tests/loopbacked.rs

## Purpose
Implements the loop-device based test harness for strat-engine tests. It creates sparse backing files, attaches loop devices, runs tests under specified device-count/size constraints, and performs cleanup.

## Main Components
- `DeviceLimits` describes loopback test runs:
  - `Exactly(count, size)`
  - `Range(lower, upper, size)`
- `LoopTestDev` owns a `LoopDevice` and backing `File`.
- `LoopTestDev::new()` creates a sparse file, truncates it to the requested sector size, attaches it to a free loop device, and syncs the backing file.
- `LoopTestDev::grow()` doubles backing-file length and updates loop capacity.
- `Drop for LoopTestDev` detaches the loop device.
- `test_with_spec()` runs a test over all device-count cases.
- `test_device_grow_with_spec()` runs a pre-grow test, doubles the first loop device, then runs a post-grow test.

## Behavior
The default loopback size is 1 GiB. For `Range`, the harness runs both lower and upper counts. Before each run it initializes logging, registers the Clevis token handler once, creates devices under `$HOME/.stratis_loopback`, calls shared cleanup, and catches test panics.

If `NO_TEST_CLEAN_UP=1`, loop devices are intentionally leaked via `forget()` and cleanup is skipped for debugging. Otherwise it removes Stratis DM devices, unmounts test filesystems, and deletes the temporary loopback directory.

## Research Notes
This harness enables destructive storage tests without external disks. It is the loopback counterpart to `tests/real.rs` and is used heavily by pool and thinpool tests.
