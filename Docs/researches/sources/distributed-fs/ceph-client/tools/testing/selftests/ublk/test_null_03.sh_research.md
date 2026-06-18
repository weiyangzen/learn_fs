<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_null_03.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_null_03.sh

## Purpose
Runs a basic fio read/write smoke test against the ublk null target in user copy mode.

## Important APIs, Types, and Functions
_add_ublk_dev, _check_add_dev, fio libaio readwrite, _cleanup_test.

## Control Flow
Prepares a null test, creates a ublk null device with optional -z or -u, runs a 256M libaio readwrite fio job, records fio status, then cleans up.

## State and Persistence
No backing store is persisted; the null target discards/serves I/O through the transient ublk device.

## Dependencies and Integration Points
Depends on fio and test_common.sh null target support.

## Risks and Edge Cases
The comment says two disks but the test uses one device; the test is mostly transport/lifecycle coverage rather than data persistence validation.

## Test Signals
Pass is fio exit status 0; missing fio returns the ublk skip code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_null_03.sh -->
