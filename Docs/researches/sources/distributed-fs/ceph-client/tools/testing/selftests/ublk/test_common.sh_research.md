# sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_common.sh

## Purpose
This shell library provides shared setup, cleanup, device management, fio workloads, recovery workflows, feature detection, and result reporting for ublk selftests.

## Important APIs, Types, and Functions
Important helpers include `_have_program()`, `_ublk_sleep()`, `_get_disk_dev_t()`, `_get_disk_size()`, `_run_fio_verify_io()`, `_create_backfile()`, `_mkfs_mount_test()`, `_check_root()`, `_prep_test()`, `_cleanup_test()`, `_have_feature()`, `_create_ublk_dev()`, `_add_ublk_dev()`, `_recover_ublk_dev()`, `__ublk_quiesce_dev()`, `__ublk_kill_daemon()`, `_ublk_del_dev()`, `run_io_and_remove()`, `run_io_and_kill_daemon()`, `run_io_and_recover()`, and `_get_metadata_size()`.

## Control Flow
Test scripts source this file, call `_prep_test()` to require root, modprobe `ublk_drv`, create a temp test directory, and log to `/dev/kmsg`. Device creation wraps `kublk add/recover`, captures device IDs, optionally settles udev, and records devices for cleanup. Cleanup deletes tracked devices, removes temporary files, and logs completion. Reusable workflows run fio while deleting, killing, or recovering devices.

## State and Persistence
It manages `UBLK_TEST_DIR`, `UBLK_TMP`, `UBLK_BACKFILES`, and `.ublk_devs`. It creates temporary files/directories, ublk devices, filesystems, mounts, and kernel log messages. Cleanup is best effort.

## Dependencies and Integration Points
It depends on root, `modprobe`, `udevadm`, `fio`, `mkfs.ext4`, `mount`, `lsblk`, `stat`, and the local `kublk`/`metadata_size` binaries. All requested ublk shell tests use it.

## Risks
Cleanup failures can leave ublk devices or temp files. Some helpers use `sed -i`, `kill -9`, and background fio, so signal/error handling is important. Parallel test support uses `JOBS` to alter sleeps and can amplify resource contention.

## Test Signals
The library reports `[PASS]`, `[SKIP]`, or `[FAIL]` through `_show_result()` and exits nonzero on failures. Individual tests rely on its device creation and cleanup correctness.
