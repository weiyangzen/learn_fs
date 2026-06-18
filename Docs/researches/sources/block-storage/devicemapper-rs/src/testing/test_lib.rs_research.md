# File Research: sources/block-storage/devicemapper-rs/src/testing/test_lib.rs

## Purpose
Provides integration-test utilities for DM cleanup, block-device sizing, XFS commands, udev settling, and test identifiers.

## Key APIs
`DM::list_test_devices`, `blkdev_size`, `xfs_create_fs`, `xfs_set_uuid`, `udev_settle`, `test_name`, `test_uuid`, `test_string`, and `clean_up`.

## Behavior
Uses `BLKGETSIZE64` ioctl for byte size. Maintains a lazily-created global `DM` context for cleanup. Test names append `_dm-rs_test_delme`. Cleanup unmounts mount points containing the suffix and repeatedly removes matching DM devices while progress is made.

## Error Handling
Command failures include stdout and stderr. Cleanup uses a local error enum with chained context for IO, procfs, nix, string, and DM failures.

## Notes
Requires host tools such as `mkfs.xfs`, `xfs_admin`, and `udevadm` for relevant tests.
