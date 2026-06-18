# File Research: sources/block-storage/devicemapper-rs/src/testing/loopbacked.rs

## Purpose
Creates loopback-backed block devices for integration-style tests.

## Key APIs
`test_with_spec(count, test)`, internal `LoopTestDev`, `get_devices`, `write_sectors`, and `wipe_sectors`.

## Behavior
Creates sparse 1 GiB files in a tempdir, attaches loop devices, wipes the first MiB to remove leftover DM metadata, passes paths to the test closure, catches panics, runs cleanup, and detaches loop devices on drop.

## Notes
Uses `unwrap` heavily because it is test-only. `test_with_spec` unwraps the test result before cleanup result, so a panic plus cleanup failure reports the panic first.
