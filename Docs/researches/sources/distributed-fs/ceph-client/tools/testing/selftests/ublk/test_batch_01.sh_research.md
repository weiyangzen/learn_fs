# sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_batch_01.sh

## Purpose
This shell test exercises basic `UBLK_F_BATCH_IO` behavior for loop and stripe targets.

## Important APIs, Types, and Functions
It sources `test_common.sh`, checks `_have_feature "BATCH_IO"`, uses `_prep_test`, `_create_backfile`, `_add_ublk_dev`, `_mkfs_mount_test`, `_cleanup_test`, and `_show_result`.

## Control Flow
The script skips without batch support, creates two 256 MiB backing files, adds a loop device with `-q 2 -b`, mounts/formats it, then adds a stripe device with `-b --auto_zc` over two files and runs the mount test.

## State and Persistence
Temporary backing files and ublk devices are created and removed by common cleanup.

## Dependencies and Integration Points
It depends on root, ublk driver, `kublk`, batch feature support, mkfs/mount helpers, and loop/stripe target implementations.

## Risks
Filesystem creation and mount require root and available ext4 tooling. The second device uses auto-zc with batch, so kernel feature mismatches can skip/fail.

## Test Signals
Pass means batch I/O supports basic filesystem operations for loop and stripe targets.
