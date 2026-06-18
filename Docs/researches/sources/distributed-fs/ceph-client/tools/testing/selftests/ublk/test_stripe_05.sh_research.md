<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_stripe_05.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_stripe_05.sh

## Purpose
Validates ublk stripe target using two 256M backing files with user-copy two-queue fio verify.

## Important APIs, Types, and Functions
_create_backfile, _add_ublk_dev -t stripe, _run_fio_verify_io or _mkfs_mount_test.

## Control Flow
Creates two backfiles, adds a stripe device with mode-specific queue/copy flags, runs either 512M fio verify over the combined device or filesystem mount smoke coverage, then cleans up.

## State and Persistence
Temporary backfiles hold the striped data for the test duration; the ublk device maps both files.

## Dependencies and Integration Points
Depends on test_common.sh, stripe target, fio for verify cases, and filesystem helpers for mount cases.

## Risks and Edge Cases
Stripe tests assume exact combined size and that both backfiles are available; filesystem tests do not verify cross-file data distribution directly.

## Test Signals
Pass is helper status 0 and cleanup completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_stripe_05.sh -->
