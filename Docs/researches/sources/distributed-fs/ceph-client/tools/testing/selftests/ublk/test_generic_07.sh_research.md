# sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_generic_07.sh

## Purpose
This test validates `UBLK_F_NEED_GET_DATA` mode on the loop target.

## Important APIs, Types, and Functions
It uses `_create_backfile`, `_add_ublk_dev -t loop -q 2 -g`, `_run_fio_verify_io()`, and `_mkfs_mount_test()`.

## Control Flow
The script skips without fio, creates a 256 MiB backing file, adds a loop device with get-data mode, runs fio write/verify across 256 MiB, then formats/mounts the device if fio succeeds.

## State and Persistence
Temporary backing file and ublk device are cleaned up by common cleanup.

## Dependencies and Integration Points
It depends on `kublk` handling `UBLK_IO_RES_NEED_GET_DATA`, loop target user data flow, fio, and ext4 mount tooling.

## Risks
The test exercises extra data fetch sequencing and can expose missing user-copy/data-copy transitions. It requires root and sufficient temp storage.

## Test Signals
Pass means fio verify and filesystem mount both succeed in get-data mode.
