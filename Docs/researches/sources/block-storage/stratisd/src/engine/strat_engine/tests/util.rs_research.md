# File Research: sources/block-storage/stratisd/src/engine/strat_engine/tests/util.rs

## Purpose
Provides shared cleanup and failure-injection utilities for strat-engine tests.

## Main Components
- `cleanup_errors` module defines test-cleanup `Error` and `Result`.
- `dm_stratis_devices_remove()` removes Stratis-related device-mapper devices.
- `stratis_filesystems_unmount()` unmounts mount points containing `stratis`.
- `clean_up()` combines unmount and DM-device cleanup.
- `FailDevice` creates a controllable DM device that can switch part of its table between linear and error targets.

## Cleanup Behavior
`dm_stratis_devices_remove()` settles udev, initializes DM, lists DM devices, and repeatedly attempts removal while progress is made. It targets names starting with:
- `stratis-1`
- `stratis_fail_device`
- `stratis_test_device`

Removal retries each device several times. Remaining devices produce a chained cleanup error.

`stratis_filesystems_unmount()` scans `/proc/self/mountinfo` and lazily unmounts mount points whose path contains `stratis`.

## Failure Device Behavior
`FailDevice::new()` creates a DM linear mapping over a backing device. `start_failing(num_sectors_after_start)` reloads the table with an initial `error` target region followed by a linear region. `stop_failing()` restores a fully linear table. `Drop` resumes the device if suspended and removes it.

## Research Notes
This file is critical for test isolation. It handles the messy state left by failed storage tests and provides deterministic device errors for negative-path testing.
