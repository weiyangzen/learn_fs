<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_loop_05.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_loop_05.sh

## Purpose
Validates ublk loop target two queues operation with fio verify raw block I/O.

## Important APIs, Types, and Functions
_prep_test, _create_backfile, _add_ublk_dev, _check_add_dev, _run_fio_verify_io or _mkfs_mount_test, _cleanup_test.

## Control Flow
Creates a 256M backing file, adds /dev/ublkb* as a loop target with the file and mode-specific flags, runs fio verify raw block I/O, stores the command status in ERR_CODE, and performs common cleanup.

## State and Persistence
State is limited to a temporary backing file, transient ublk block device, and optional mounted filesystem created by test_common.sh.

## Dependencies and Integration Points
Depends on test_common.sh, kublk loop target, and fio for the raw-I/O variants; filesystem variants depend on mkfs/mount helpers.

## Risks and Edge Cases
Failures can leave mounts/devices if cleanup helpers cannot run; fio variants skip when fio is unavailable.

## Test Signals
Pass is the helper return status being zero and _show_result reporting ERR_CODE=0.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_loop_05.sh -->
