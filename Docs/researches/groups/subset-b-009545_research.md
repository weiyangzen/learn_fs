# Research Group subset-b-009545

This grouped report covers xfstests generic shell tests `095` through `215`. Each section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/095 -->
# sources/test-tools/xfstests/tests/generic/095

## Purpose

There's a known EIO failure to report collisions between directio and buffered writes to userspace, refer to upstream linux 5a9d929d6e13. So ignore EIO error at here. The test is registered with `_begin_fstest auto quick rw stress mmap` and falls into the AIO/direct I/O, mmap area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `095` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter` and gates execution with `_require_scratch`, `_require_odirect`, `_require_aio`, `_require_fio $fio_config`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 10: `_begin_fstest auto quick rw stress mmap`
- Line 73: `ioengine=mmap`
- Line 92: `$FIO_PROG $fio_config --ignore_error=,EIO --output=$fio_out`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

The primary pass signal is the script reaching `status=0` or `exit $status` with no unexpected command failure, filtered output mismatch, or dmesg warning.

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through none declared. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Timing and alignment make the test susceptible to architecture, page-size, and direct-I/O constraints; dmesg filtering must not hide unrelated warnings. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=$?; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/095 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/096 -->
# sources/test-tools/xfstests/tests/generic/096

## Purpose

Exercise the situation that cause ext4 to BUG_ON() when we use zero range to zero a range which starts within the isize but ends past the isize but still in the same block. This particular problem has only been seen on systems with page_size > block_size. The test is registered with `_begin_fstest auto prealloc quick zero` and falls into the preallocation/unwritten extent, zero range area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `096` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter` and gates execution with `_require_scratch`, `_require_xfs_io_command "fzero"`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 19: `_require_xfs_io_command "fzero"`
- Line 28: `$XFS_IO_PROG -f -c "pwrite 4096 512" -c "fzero 4351 512" $testfile >> $seqres.full 2>&1`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

The primary pass signal is the script reaching `status=0` or `exit $status` with no unexpected command failure, filtered output mismatch, or dmesg warning.

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through none declared. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Range operations have off-by-one and block-boundary risk; the test relies on xfs_io command support and stable filtering of sparse/unwritten output. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/096 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/097 -->
# sources/test-tools/xfstests/tests/generic/097

## Purpose

simple attr tests for EAs: - set - get - list - remove Basic testing. The test is registered with `_begin_fstest attr auto quick` and falls into the xattr area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `097` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/attr`, `. ./common/filter` and gates execution with `_require_test`, `_require_attrs user trusted`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 33: `$SETFATTR_PROG "$@" |& _filter_test_dir`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

- Line 28: `_getfattr --absolute-names "$@" |& _filter_test_dir`
- Line 33: `$SETFATTR_PROG "$@" |& _filter_test_dir`

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through `_cleanup()`, `rm -f $tmp.* $file`. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

The expected output is sensitive to namespace support, user/group setup, mount options, and filtered id/name rendering. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/097 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/098 -->
# sources/test-tools/xfstests/tests/generic/098

## Purpose

size of the file to be persisted after a clean unmount of the filesystem (or after the inode is evicted). This is for the case where all the data following the hole is not yet durably persisted, that is, that data is only present in the page cache. The test is registered with `_begin_fstest auto quick metadata` and falls into the truncate area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `098` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter` and gates execution with `_require_scratch`, `_require_btrfs_fs_feature "no_holes"`, `_require_btrfs_mkfs_feature "no-holes"`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 40: `$XFS_IO_PROG -t -f -c "pwrite -S 0xaa 0 128K" $SCRATCH_MNT/foo | _filter_xfs_io`
- Line 46: `$XFS_IO_PROG -c "pwrite -S 0xbb 256K 32K" $SCRATCH_MNT/foo | _filter_xfs_io`
- Line 61: `$XFS_IO_PROG -c "truncate 160K" $SCRATCH_MNT/foo`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

- Line 40: `$XFS_IO_PROG -t -f -c "pwrite -S 0xaa 0 128K" $SCRATCH_MNT/foo | _filter_xfs_io`
- Line 46: `$XFS_IO_PROG -c "pwrite -S 0xbb 256K 32K" $SCRATCH_MNT/foo | _filter_xfs_io`

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through none declared. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Range operations have off-by-one and block-boundary risk; the test relies on xfs_io command support and stable filtering of sparse/unwritten output. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/098 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/099 -->
# sources/test-tools/xfstests/tests/generic/099

## Purpose

-> 3 extra ACEs: MASK, GROUP, USER -> the GROUP compares with egid of process _and_ the supplementary groups (as found in /etc/group) The test is registered with `_begin_fstest acl auto quick perms` and falls into the ACL/permission, xattr, permission area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `099` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter`, `. ./common/attr` and gates execution with `_require_test`, `_require_runas`, `_require_acls`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 72: `chmod u=rwx file1`
- Line 73: `chmod g=rw- file1`
- Line 74: `chmod o=r-- file1`
- Line 75: `chown $acl1:$acl2 file1`
- Line 92: `chmod u+w file1`
- Line 263: `chown -R 12345:54321 root`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

- Line 81: `chacl -l file1 | _acl_filter_id`
- Line 140: `chacl u::---,g::---,o::---,u:$acl2:r-x file1 2>&1 | _acl_filter_id`
- Line 153: `chacl u::---,g::---,o::---,g:$acl2:r-x file1 2>&1 | _acl_filter_id`
- Line 217: `chacl -l acldir | _acl_filter_id`
- Line 222: `chacl -l file2 | _acl_filter_id`
- Line 229: `chacl -l file3 | _acl_filter_id`

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through `_cleanup()`, `rm -f $tmp.*`. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

The expected output is sensitive to namespace support, user/group setup, mount options, and filtered id/name rendering. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/099 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/100 -->
# sources/test-tools/xfstests/tests/generic/100

## Purpose

Use _populate_fs() in common/rc to create a directory structure. The test is registered with `_begin_fstest udf auto` and falls into the generic filesystem behavior area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `100` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter` and gates execution with `_require_test`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 19: `rm -f $tmp.* $TEMP_DIR/$TAR_FILE`
- Line 35: `rm -rf $POPULATED_DIR`
- Line 36: `rm -f $TEMP_DIR/$TAR_FILE`
- Line 51: `diff -qr $POPULATED_DIR ${TEST_DIR}${POPULATED_DIR}`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

- Line 51: `diff -qr $POPULATED_DIR ${TEST_DIR}${POPULATED_DIR}`

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through `_cleanup()`, `rm -f $tmp.* $TEMP_DIR/$TAR_FILE`. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

The main risk is environmental: missing helper binaries, unsupported mount features, or output filtering drift can turn a filesystem regression into a notrun or false failure. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/100 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/101 -->
# sources/test-tools/xfstests/tests/generic/101

## Purpose

original size or a larger size, then fsyncing it and a power failure happens, the file will have the range [first_truncate_size, last_size[ with all bytes having a value of 0x00 if we read it the next time the filesystem is mounted. The test is registered with `_begin_fstest auto quick metadata log` and falls into the journal/power-failure replay, truncate area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `101` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter`, `. ./common/dmflakey` and gates execution with `_require_scratch`, `_require_dm_target flakey`, `_require_btrfs_fs_feature "no_holes"`, `_require_btrfs_mkfs_feature "no-holes"`, `_require_metadata_journaling $SCRATCH_DEV`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 46: `$XFS_IO_PROG -f -c "pwrite -S 0xaa 0 64K" -c "pwrite -S 0xbb 64K 61K" $SCRATCH_MNT/foo | _filter_xfs_io`
- Line 49: `$XFS_IO_PROG -f -c "pwrite -S 0xee 0 64K" -c "pwrite -S 0xff 64K 61K" $SCRATCH_MNT/bar | _filter_xfs_io`
- Line 59: `$XFS_IO_PROG -c "truncate 64K" -c "truncate 125K" -c "fsync" $SCRATCH_MNT/foo`
- Line 67: `$XFS_IO_PROG -c "truncate 0" -c "truncate 253K" -c "fsync" $SCRATCH_MNT/bar`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

- Line 46: `$XFS_IO_PROG -f -c "pwrite -S 0xaa 0 64K" -c "pwrite -S 0xbb 64K 61K" $SCRATCH_MNT/foo | _filter_xfs_io`
- Line 49: `$XFS_IO_PROG -f -c "pwrite -S 0xee 0 64K" -c "pwrite -S 0xff 64K 61K" $SCRATCH_MNT/bar | _filter_xfs_io`

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through `_cleanup()`, `_cleanup_flakey`, `rm -f $tmp.*`. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

The simulated crash path depends on dm-flakey teardown/remount ordering; a cleanup or remount failure can mask the metadata replay condition being tested. Range operations have off-by-one and block-boundary risk; the test relies on xfs_io command support and stable filtering of sparse/unwritten output. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/101 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/102 -->
# sources/test-tools/xfstests/tests/generic/102

## Purpose

Sometimes writes will failed on NO_SPACE when disk almost full in btrfs. It is long-term problem since very beginning for btrfs The test is registered with `_begin_fstest auto rw` and falls into the generic filesystem behavior area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `102` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter` and gates execution with `_require_scratch`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 30: `$XFS_IO_PROG -f -c "pwrite -b 1m 0 800m" "$SCRATCH_MNT"/file | _filter_xfs_io | _filter_scratch`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

- Line 30: `$XFS_IO_PROG -f -c "pwrite -b 1m 0 800m" "$SCRATCH_MNT"/file | _filter_xfs_io | _filter_scratch`

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through none declared. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

The main risk is environmental: missing helper binaries, unsupported mount features, or output filtering drift can turn a filesystem regression into a notrun or false failure. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/102 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/103 -->
# sources/test-tools/xfstests/tests/generic/103

## Purpose

that resulted in problematic removal of inodes with remote attribute forks without attribute extents. The attribute fork condition is created by attempting to set larger attribute values on a filesystem that is at or near ENOSPC. The test is registered with `_begin_fstest auto quick attr enospc prealloc` and falls into the xattr, ENOSPC, preallocation/unwritten extent area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `103` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/attr` and gates execution with `_require_scratch`, `_require_attrs`, `_require_xfs_io_command "falloc"`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 23: `_require_xfs_io_command "falloc"`
- Line 40: `$XFS_IO_PROG -fc "falloc 0 ${filesizekb}k" $file`
- Line 52: `$XFS_IO_PROG -fc "pwrite 0 64k" $SCRATCH_MNT/attrval > /dev/null 2>&1`
- Line 57: `$SETFATTR_PROG -n user.test -v "`cat $SCRATCH_MNT/attrval`" $SCRATCH_MNT/$seq.$i >> $seqres.full 2>&1`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

The primary pass signal is the script reaching `status=0` or `exit $status` with no unexpected command failure, filtered output mismatch, or dmesg warning.

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through none declared. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

The expected output is sensitive to namespace support, user/group setup, mount options, and filtered id/name rendering. Free-space arithmetic is intentionally tight, so filesystem geometry, reserved blocks, or delayed allocation can change whether ENOSPC appears at the intended point. Range operations have off-by-one and block-boundary risk; the test relies on xfs_io command support and stable filtering of sparse/unwritten output. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/103 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/104 -->
# sources/test-tools/xfstests/tests/generic/104

## Purpose

fsync only one of the files, after the fsync log/journal is replayed all the links exist and the filesystem metadata (directory and file inodes) is in a consistent state. The test is registered with `_begin_fstest auto quick metadata log` and falls into the journal/power-failure replay, hard link area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `104` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter`, `. ./common/dmflakey` and gates execution with `_require_scratch`, `_require_hardlinks`, `_require_dm_target flakey`, `_require_metadata_journaling $SCRATCH_DEV`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 45: `ln $SCRATCH_MNT/testdir/bar $SCRATCH_MNT/testdir/bar_link`
- Line 46: `ln $SCRATCH_MNT/testdir/foo $SCRATCH_MNT/testdir/foo_link`
- Line 47: `$XFS_IO_PROG -c "fsync" $SCRATCH_MNT/testdir/bar`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

- Line 52: `echo "Link count for file foo: $(stat -c %h $SCRATCH_MNT/testdir/foo)"`
- Line 53: `echo "Link count for file bar: $(stat -c %h $SCRATCH_MNT/testdir/bar)"`

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through `_cleanup()`, `_cleanup_flakey`, `rm -f $tmp.*`. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

The simulated crash path depends on dm-flakey teardown/remount ordering; a cleanup or remount failure can mask the metadata replay condition being tested. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/104 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/105 -->
# sources/test-tools/xfstests/tests/generic/105

## Purpose

930290 - xfs directory with no exec perm in ACL denies access and breaks CAPP evaluation which pulls out an earlier mod The test is registered with `_begin_fstest acl auto quick perms` and falls into the ACL/permission, xattr, permission area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `105` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter`, `. ./common/attr` and gates execution with `_require_scratch`, `_require_acls`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 47: `chown $acl1 subdir`
- Line 54: `setfacl -m u:$acl1:r subdir`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

The primary pass signal is the script reaching `status=0` or `exit $status` with no unexpected command failure, filtered output mismatch, or dmesg warning.

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through `_cleanup()`. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

The expected output is sensitive to namespace support, user/group setup, mount options, and filtered id/name rendering. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/105 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/106 -->
# sources/test-tools/xfstests/tests/generic/106

## Purpose

inode, power fail and then mount the filesystem, the hard link we removed does not exists anymore and the filesystem metadata is in a consistent state. The test is registered with `_begin_fstest auto quick metadata log` and falls into the journal/power-failure replay, hard link area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `106` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter`, `. ./common/dmflakey` and gates execution with `_require_scratch`, `_require_hardlinks`, `_require_dm_target flakey`, `_require_metadata_journaling $SCRATCH_DEV`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 37: `ln $SCRATCH_MNT/testdir/foo $SCRATCH_MNT/testdir/bar`
- Line 46: `$XFS_IO_PROG -c "fsync" $SCRATCH_MNT/testdir/foo`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

The primary pass signal is the script reaching `status=0` or `exit $status` with no unexpected command failure, filtered output mismatch, or dmesg warning.

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through `_cleanup()`, `_cleanup_flakey`, `rm -f $tmp.*`. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

The simulated crash path depends on dm-flakey teardown/remount ordering; a cleanup or remount failure can mask the metadata replay condition being tested. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/106 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/107 -->
# sources/test-tools/xfstests/tests/generic/107

## Purpose

parent directories, if we remove one of those links, fsync the file using one of its other links (that has a parent directory different from the one we removed a link from), power fail and then replay the fsync log/journal, the hard link we removed is not available anymore and all the filesystem metadata is in a consistent state. The test is registered with `_begin_fstest auto quick metadata log` and falls into the journal/power-failure replay, hard link area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `107` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter`, `. ./common/dmflakey` and gates execution with `_require_scratch`, `_require_hardlinks`, `_require_dm_target flakey`, `_require_metadata_journaling $SCRATCH_DEV`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 40: `ln $SCRATCH_MNT/foo $SCRATCH_MNT/testdir/foo2`
- Line 41: `ln $SCRATCH_MNT/foo $SCRATCH_MNT/testdir/foo3`
- Line 51: `$XFS_IO_PROG -c "fsync" $SCRATCH_MNT/foo`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

The primary pass signal is the script reaching `status=0` or `exit $status` with no unexpected command failure, filtered output mismatch, or dmesg warning.

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through `_cleanup()`, `_cleanup_flakey`, `rm -f $tmp.*`. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

The simulated crash path depends on dm-flakey teardown/remount ordering; a cleanup or remount failure can mask the metadata replay condition being tested. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/107 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/108 -->
# sources/test-tools/xfstests/tests/generic/108

## Purpose

on partial I/O failure, e.g. a single failed disk in a raid 0 stripe. The test is registered with `_begin_fstest auto quick rw` and falls into the generic filesystem behavior area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `108` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter`, `. ./common/scsi_debug` and gates execution with `_require_scratch_nolvm`, `_require_block_device $SCRATCH_DEV`, `_require_scsi_debug`, `_require_command "$LVM_PROG" lvm`, `_require_non_zoned_device $SCRATCH_DEV`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 22: `$LVM_PROG vgremove -f $vgname >>$seqres.full 2>&1`
- Line 36: `_require_command "$LVM_PROG" lvm`
- Line 62: `$LVM_PROG pvcreate -f $SCSI_DEBUG_DEV $SCRATCH_DEV >>$seqres.full 2>&1 || _notrun "LVM is too stupid for this device"`
- Line 64: `$LVM_PROG vgcreate -f $vgname $SCSI_DEBUG_DEV $SCRATCH_DEV >>$seqres.full 2>&1`
- Line 67: `yes | $LVM_PROG lvcreate -i 2 -I 4m -L ${lvsize}m -n $lvname $vgname >>$seqres.full 2>&1 || _fail "Failed to create LVM lv"`
- Line 78: `$XFS_IO_PROG -f -c "pwrite 0 16M" -c fsync $SCRATCH_MNT/testfile >>$seqres.full`
- Line 85: `$XFS_IO_PROG -c "pwrite -b 1M 0 6M" -c fsync $SCRATCH_MNT/testfile >>$seqres.full`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

The primary pass signal is the script reaching `status=0` or `exit $status` with no unexpected command failure, filtered output mismatch, or dmesg warning.

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through `_cleanup()`, `rm -f $tmp.*`. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

The main risk is environmental: missing helper binaries, unsupported mount features, or output filtering drift can turn a filesystem regression into a notrun or false failure. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/108 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/109 -->
# sources/test-tools/xfstests/tests/generic/109

## Purpose

in XFS where directory entry file type was not updated properly on rename. The test is registered with `_begin_fstest auto metadata dir` and falls into the hard link, rename area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `109` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble` and gates execution with `_require_scratch`, `_require_symlinks`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 36: `ln -s foo ss1`
- Line 37: `ln -s foo ss2`
- Line 38: `ln -s foo ss3`
- Line 39: `ln -s foo sd1`
- Line 40: `ln -s foo sd2`
- Line 42: `mv -T fs1 fd1`
- Line 43: `mv -T fs2 sd1`
- Line 44: `mv -T fs3 ed1`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

The primary pass signal is the script reaching `status=0` or `exit $status` with no unexpected command failure, filtered output mismatch, or dmesg warning.

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through none declared. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

The main risk is environmental: missing helper binaries, unsupported mount features, or output filtering drift can turn a filesystem regression into a notrun or false failure. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/109 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/110 -->
# sources/test-tools/xfstests/tests/generic/110

## Purpose

Tests file clone functionality of btrfs ("reflinks"): - Reflink a file - Reflink the reflinked file - Modify the original file - Modify the reflinked file The test is registered with `_begin_fstest auto quick clone fiemap` and falls into the reflink/CoW area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `110` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. common/filter`, `. common/reflink` and gates execution with `_require_test_reflink`, `_require_xfs_io_command "fiemap"`, `_require_cp_reflink`, `_require_test`. Local helpers are `line 37 `_checksum_files() {``. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 27: `_require_test_reflink`
- Line 30: `_require_cp_reflink`
- Line 45: `$XFS_IO_PROG -f -c 'pwrite -S 0x61 0 9000' $testdir1/original >> $seqres.full 2>&1`
- Line 47: `cp --reflink $testdir1/original $testdir1/copy1`
- Line 48: `cp --reflink $testdir1/copy1 $testdir1/copy2`
- Line 49: `_verify_reflink $testdir1/original $testdir1/copy1`
- Line 50: `_verify_reflink $testdir1/original $testdir1/copy2`
- Line 55: `$XFS_IO_PROG -c 'pwrite -S 0x62 0 9000' $testdir1/original >> $seqres.full 2>&1`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

- Line 40: `md5sum $testdir1/$F | _filter_test_dir`
- Line 49: `_verify_reflink $testdir1/original $testdir1/copy1`
- Line 50: `_verify_reflink $testdir1/original $testdir1/copy2`
- Line 51: `echo "Original md5sums:"`
- Line 57: `echo "md5sums after overwriting original:"`
- Line 63: `echo "md5sums after overwriting copy1:"`

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through `_cleanup()`, `rm -f $tmp.* $testdir`. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Block-size congruence, sharing verification, and post-remount checks are critical because unsupported or partially implemented sharing can otherwise look like ordinary copies. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/110 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/111 -->
# sources/test-tools/xfstests/tests/generic/111

## Purpose

Tests file clone functionality of btrfs ("reflinks") on directory trees. - Create directory and subdirectory, each having one file - Create 2 recursive reflinked copies of the tree - Modify the original files - Modify one of the copies The test is registered with `_begin_fstest auto quick clone fiemap` and falls into the reflink/CoW area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `111` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. common/filter`, `. common/reflink` and gates execution with `_require_test_reflink`, `_require_xfs_io_command "fiemap"`, `_require_cp_reflink`, `_require_test`. Local helpers are `line 38 `_checksum_files() {``. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 28: `_require_test_reflink`
- Line 31: `_require_cp_reflink`
- Line 51: `$XFS_IO_PROG -f -c 'pwrite -S 0x61 0 9000' $testdir1/original/file1 >> $seqres.full 2>&1`
- Line 53: `$XFS_IO_PROG -f -c 'pwrite -S 0x62 0 11000' $testdir1/original/subdir/file2 >> $seqres.full 2>&1`
- Line 55: `cp --recursive --reflink $testdir1/original $testdir1/copy1`
- Line 56: `cp --recursive --reflink $testdir1/copy1 $testdir1/copy2`
- Line 58: `_verify_reflink $testdir1/original/file1 $testdir1/copy1/file1`
- Line 59: `_verify_reflink $testdir1/original/subdir/file2 $testdir1/copy1/subdir/file2`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

- Line 43: `md5sum $testdir1/$F | _filter_test_dir`
- Line 58: `_verify_reflink $testdir1/original/file1 $testdir1/copy1/file1`
- Line 59: `_verify_reflink $testdir1/original/subdir/file2 $testdir1/copy1/subdir/file2`
- Line 61: `_verify_reflink $testdir1/original/file1 $testdir1/copy2/file1`
- Line 62: `_verify_reflink $testdir1/original/subdir/file2 $testdir1/copy2/subdir/file2`
- Line 65: `echo "Original md5sums:"`

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through `_cleanup()`, `rm -f $tmp.* $testdir`. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Block-size congruence, sharing verification, and post-remount checks are critical because unsupported or partially implemented sharing can otherwise look like ordinary copies. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/111 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/112 -->
# sources/test-tools/xfstests/tests/generic/112

## Purpose

check if preallocation is supported, xfs_io resvsp command only prints out messages on failure. The test is registered with `_begin_fstest rw aio auto quick` and falls into the AIO/direct I/O, preallocation/unwritten extent, timestamp, rename, fsx random I/O area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `112` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter` and gates execution with `_require_test`, `_require_aio`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 18: `rm -rf $TEST_DIR/fsx.* $tmp.*`
- Line 56: `if ! $FSX_PROG $_param -P "$RESULT_DIR" $FSX_AVOID $seq.$_n &>/dev/null`
- Line 59: `mv "$RESULT_DIR"/$seq.$_n.fsxlog $seqres.$_n.full`
- Line 103: `[ -x $here/ltp/aio-stress ] || _notrun "fsx not built with AIO for this platform"`
- Line 124: `testio=`$XFS_IO_PROG -f -c "resvsp 0 1" $testfile 2>&1``
- Line 142: `rm -f $seq.*.fsx{good,log}`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

The primary pass signal is the script reaching `status=0` or `exit $status` with no unexpected command failure, filtered output mismatch, or dmesg warning.

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through `_cleanup()`. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Timing and alignment make the test susceptible to architecture, page-size, and direct-I/O constraints; dmesg filtering must not hide unrelated warnings. Range operations have off-by-one and block-boundary risk; the test relies on xfs_io command support and stable filtering of sparse/unwritten output. Timestamp resolution and mount options can make the signal weak unless the test accounts for atime/mtime/ctime granularity. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0	# success is the default!; status=1; exit; status=1; exit; exit; exit 0`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/112 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/113 -->
# sources/test-tools/xfstests/tests/generic/113

## Purpose

and the default with multiprocess The test is registered with `_begin_fstest rw aio auto quick` and falls into the AIO/direct I/O, preallocation/unwritten extent area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `113` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter` and gates execution with `_require_test`, `_require_aio`, `_require_odirect`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 18: `rm -f $TEST_DIR/aio-stress.$$.*`
- Line 42: `echo "aio-stress.$_n : $_param"`
- Line 44: `if ! $here/ltp/aio-stress $_param $AIOSTRESS_AVOID -I $_count $_files >>$tmp.out 2>&1`
- Line 46: `echo "    aio-stress (count=$_count) returned $?"`
- Line 60: `[ -x $here/ltp/aio-stress ] || _notrun "aio-stress not built for this platform"`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

The primary pass signal is the script reaching `status=0` or `exit $status` with no unexpected command failure, filtered output mismatch, or dmesg warning.

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through `_cleanup()`. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Timing and alignment make the test susceptible to architecture, page-size, and direct-I/O constraints; dmesg filtering must not hide unrelated warnings. Range operations have off-by-one and block-boundary risk; the test relies on xfs_io command support and stable filtering of sparse/unwritten output. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0	# success is the default!; status=1; exit; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/113 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/114 -->
# sources/test-tools/xfstests/tests/generic/114

## Purpose

We don't mind 512-byte fs blocks; the IOs won't be sub-block, but the test should still pass, even if it doesn't stress the code we're targeting. The test is registered with `_begin_fstest rw aio auto quick` and falls into the AIO/direct I/O area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `114` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter` and gates execution with `_require_test`, `_require_sparse_files`, `_require_aiodio aio-dio-eof-race`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 39: `$AIO_TEST $TEST_DIR/tst-aio-dio-eof-race`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

The primary pass signal is the script reaching `status=0` or `exit $status` with no unexpected command failure, filtered output mismatch, or dmesg warning.

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through `_cleanup()`. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Timing and alignment make the test susceptible to architecture, page-size, and direct-I/O constraints; dmesg filtering must not hide unrelated warnings. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=$?; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/114 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/115 -->
# sources/test-tools/xfstests/tests/generic/115

## Purpose

Moving and deleting cloned ("reflinked") files on btrfs: - Create a file and a reflink - Move both to a directory - Delete the original (moved) file, check that the copy still exists. The test is registered with `_begin_fstest auto quick clone fiemap` and falls into the reflink/CoW, rename area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `115` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink` and gates execution with `_require_test_reflink`, `_require_xfs_io_command "fiemap"`, `_require_cp_reflink`, `_require_test`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 26: `_require_test_reflink`
- Line 29: `_require_cp_reflink`
- Line 37: `$XFS_IO_PROG -f -c 'pwrite -S 0x61 0 9000' $testdir1/original >> $seqres.full`
- Line 39: `cp --reflink $testdir1/original $testdir1/copy`
- Line 41: `_verify_reflink $testdir1/original $testdir1/copy`
- Line 43: `echo "Move orig & reflink copy to subdir and md5sum:"`
- Line 45: `mv $testdir1/original $testdir1/subdir/original_moved`
- Line 46: `mv $testdir1/copy $testdir1/subdir/copy_moved`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

- Line 41: `_verify_reflink $testdir1/original $testdir1/copy`
- Line 43: `echo "Move orig & reflink copy to subdir and md5sum:"`
- Line 47: `_verify_reflink $testdir1/subdir/original_moved $testdir1/subdir/copy_moved`
- Line 50: `md5sum $testdir1/subdir/original_moved | _filter_test_dir`
- Line 51: `md5sum $testdir1/subdir/copy_moved | _filter_test_dir`
- Line 53: `echo "remove orig from subdir and md5sum reflink copy:"`

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through `_cleanup()`, `rm -f $tmp.* $testdir`. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Block-size congruence, sharing verification, and post-remount checks are critical because unsupported or partially implemented sharing can otherwise look like ordinary copies. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/115 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/116 -->
# sources/test-tools/xfstests/tests/generic/116

## Purpose

Ensure that we can reflink parts of two identical files: - Reflink identical parts of two identical files - Check that we still have identical contents The test is registered with `_begin_fstest auto quick clone` and falls into the reflink/CoW area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `116` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink` and gates execution with `_require_test_reflink`, `_require_congruent_file_oplen $TEST_DIR $blksz`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 25: `_require_test_reflink`
- Line 34: `_pwrite_byte 0x61 $((blksz * 2)) $((blksz * 6)) $testdir/file1 >> $seqres.full`
- Line 35: `_pwrite_byte 0x61 $((blksz * 2)) $((blksz * 6)) $testdir/file2 >> $seqres.full`
- Line 46: `_reflink_range $testdir/file1 $((blksz * 4)) $testdir/file2 $((blksz * 4)) $((blksz * 2)) >> $seqres.full`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

- Line 38: `md5sum $testdir/file1 | _filter_test_dir`
- Line 39: `md5sum $testdir/file2 | _filter_test_dir`
- Line 41: `_compare_range $testdir/file1 0 $testdir/file2 0 $((blksz * 8)) || echo "Files do not match"`
- Line 45: `free_before=$(stat -f -c '%a' $testdir)`
- Line 49: `free_after=$(stat -f -c '%a' $testdir)`
- Line 56: `_compare_range $testdir/file1 0 $testdir/file2 0 $((blksz * 4)) || echo "Start sections do not match"`

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through `_cleanup()`, `rm -rf $tmp.* $testdir`. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Block-size congruence, sharing verification, and post-remount checks are critical because unsupported or partially implemented sharing can otherwise look like ordinary copies. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/116 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/117 -->
# sources/test-tools/xfstests/tests/generic/117

## Purpose

Attempt to cause filesystem corruption with serial fsstresses doing extended attributes writes - pv 940655 The test is registered with `_begin_fstest attr auto quick` and falls into the xattr, rename, permission, truncate, fsstress area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `117` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter`, `. ./common/attr` and gates execution with `_require_scratch`, `_require_attrs`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 15: `fss_ops=" -z -f attr_remove=100 -f attr_set=100 -f chown=3 -f creat=4 -f dread=4 -f dwrite=4 -f fdatasync=1 -f fsync=1 -f getdents=1 -f link=1 -f mkdir=2 -f mknod=2 -f read=1 -f readlink=1 -f rename=2 -f rmdir=1 -f setxa`
- Line 59: `mkdir -p $SCRATCH_MNT/fsstress`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

The primary pass signal is the script reaching `status=0` or `exit $status` with no unexpected command failure, filtered output mismatch, or dmesg warning.

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through none declared. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

The expected output is sensitive to namespace support, user/group setup, mount options, and filtered id/name rendering. Range operations have off-by-one and block-boundary risk; the test relies on xfs_io command support and stable filtering of sparse/unwritten output. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=$?; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/117 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/118 -->
# sources/test-tools/xfstests/tests/generic/118

## Purpose

Ensuring that we can reflink non-matching parts of files: - Reflink identical ranges of two different files - Check that the non-linked ranges still do not match - Check that we end up with identical contents in the linked ranges The test is registered with `_begin_fstest auto quick clone` and falls into the reflink/CoW area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `118` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink` and gates execution with `_require_test_reflink`, `_require_congruent_file_oplen $TEST_DIR $blksz`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 26: `_require_test_reflink`
- Line 35: `_pwrite_byte 0x61 $((blksz * 2)) $((blksz * 6)) $testdir/file1 >> $seqres.full`
- Line 36: `_pwrite_byte 0x62 $((blksz * 2)) $((blksz * 6)) $testdir/file2 >> $seqres.full`
- Line 47: `_reflink_range $testdir/file1 $((blksz * 4)) $testdir/file2 $((blksz * 4)) $((blksz * 2)) >> $seqres.full`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

- Line 39: `md5sum $testdir/file1 | _filter_test_dir`
- Line 40: `md5sum $testdir/file2 | _filter_test_dir`
- Line 42: `_compare_range $testdir/file1 0 $testdir/file2 0 $((blksz * 8)) || echo "Files do not match (intentional)"`
- Line 46: `free_before=$(stat -f -c '%a' $testdir)`
- Line 50: `free_after=$(stat -f -c '%a' $testdir)`
- Line 57: `_compare_range $testdir/file1 0 $testdir/file2 0 $((blksz * 4)) || echo "Start sections do not match (intentional)"`

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through `_cleanup()`, `rm -rf $tmp.* $testdir`. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Block-size congruence, sharing verification, and post-remount checks are critical because unsupported or partially implemented sharing can otherwise look like ordinary copies. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/118 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/119 -->
# sources/test-tools/xfstests/tests/generic/119

## Purpose

Reflinking two sets of files together: - Reflink identical parts of two identical files - Reflink identical parts of two other identical files - Reflink identical parts of all four files - Check that we end up with identical contents The test is registered with `_begin_fstest auto quick clone` and falls into the reflink/CoW area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `119` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink` and gates execution with `_require_test_reflink`, `_require_arbitrary_fileset_reflink`, `_require_congruent_file_oplen $TEST_DIR $blksz`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 27: `_require_test_reflink`
- Line 28: `_require_arbitrary_fileset_reflink`
- Line 37: `_pwrite_byte 0x61 0 $((blksz * 8)) $testdir/file1 >> $seqres.full`
- Line 38: `_pwrite_byte 0x62 0 $((blksz * 8)) $testdir/file2 >> $seqres.full`
- Line 39: `_pwrite_byte 0x63 0 $((blksz * 8)) $testdir/file3 >> $seqres.full`
- Line 40: `_pwrite_byte 0x64 0 $((blksz * 8)) $testdir/file4 >> $seqres.full`
- Line 59: `_reflink_range $testdir/file1 0 $testdir/file2 0 $((blksz * 4)) >> $seqres.full`
- Line 60: `_reflink_range $testdir/file3 0 $testdir/file4 0 $((blksz * 4)) >> $seqres.full`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

- Line 43: `md5sum $testdir/file1 | _filter_test_dir`
- Line 44: `md5sum $testdir/file2 | _filter_test_dir`
- Line 45: `md5sum $testdir/file3 | _filter_test_dir`
- Line 46: `md5sum $testdir/file4 | _filter_test_dir`
- Line 48: `_compare_range $testdir/file1 0 $testdir/file2 0 $((blksz * 8)) || echo "Files 1-2 do not match (intentional)"`
- Line 51: `_compare_range $testdir/file1 0 $testdir/file3 0 $((blksz * 8)) || echo "Files 1-3 do not match (intentional)"`

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through `_cleanup()`, `rm -rf $tmp.* $testdir`. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Block-size congruence, sharing verification, and post-remount checks are critical because unsupported or partially implemented sharing can otherwise look like ordinary copies. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/119 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/120 -->
# sources/test-tools/xfstests/tests/generic/120

## Purpose

executable file The test is registered with `_begin_fstest other atime auto quick` and falls into the timestamp area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `120` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter` and gates execution with `_require_scratch`, `_require_atime`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 46: `cp $here/src/lstat64 $SCRATCH_MNT`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

The primary pass signal is the script reaching `status=0` or `exit $status` with no unexpected command failure, filtered output mismatch, or dmesg warning.

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through none declared. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Timestamp resolution and mount options can make the signal weak unless the test accounts for atime/mtime/ctime granularity. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `exit; status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/120 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/121 -->
# sources/test-tools/xfstests/tests/generic/121

## Purpose

Ensure that we can dedupe parts of two files: - Dedupe identical parts of two identical files - Check that still have identical contents The test is registered with `_begin_fstest auto quick clone dedupe` and falls into the reflink/CoW, dedupe area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `121` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink` and gates execution with `_require_test_dedupe`, `_require_congruent_file_oplen $TEST_DIR $blksz`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 25: `_require_test_dedupe`
- Line 34: `_pwrite_byte 0x61 $((blksz * 2)) $((blksz * 6)) $testdir/file1 >> $seqres.full`
- Line 35: `_pwrite_byte 0x61 $((blksz * 2)) $((blksz * 6)) $testdir/file2 >> $seqres.full`
- Line 46: `_dedupe_range $testdir/file1 $((blksz * 4)) $testdir/file2 $((blksz * 4)) $((blksz * 2)) >> $seqres.full`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

- Line 38: `md5sum $testdir/file1 | _filter_test_dir`
- Line 39: `md5sum $testdir/file2 | _filter_test_dir`
- Line 41: `_compare_range $testdir/file1 0 $testdir/file2 0 $((blksz * 8)) || echo "Files 1-2 do not match (intentional)"`
- Line 45: `free_before=$(stat -f -c '%a' $testdir)`
- Line 49: `free_after=$(stat -f -c '%a' $testdir)`
- Line 56: `_compare_range $testdir/file1 0 $testdir/file2 0 $((blksz * 4)) || echo "Start sections do not match"`

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through `_cleanup()`, `rm -rf $tmp.* $testdir`. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Block-size congruence, sharing verification, and post-remount checks are critical because unsupported or partially implemented sharing can otherwise look like ordinary copies. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/121 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/122 -->
# sources/test-tools/xfstests/tests/generic/122

## Purpose

Ensuring that we cannot dedupe non-matching parts of files: - Fail to dedupe non-identical parts of two different files - Check that nothing changes in either file The test is registered with `_begin_fstest auto quick clone dedupe` and falls into the reflink/CoW, dedupe area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `122` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink` and gates execution with `_require_test_dedupe`, `_require_congruent_file_oplen $TEST_DIR $blksz`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 25: `_require_test_dedupe`
- Line 34: `_pwrite_byte 0x61 $((blksz * 2)) $((blksz * 6)) $testdir/file1 >> $seqres.full`
- Line 35: `_pwrite_byte 0x62 $((blksz * 2)) $((blksz * 6)) $testdir/file2 >> $seqres.full`
- Line 46: `_dedupe_range $testdir/file1 $((blksz * 4)) $testdir/file2 $((blksz * 4)) $((blksz * 2)) 2>&1 | _filter_dedupe_error`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

- Line 38: `md5sum $testdir/file1 | _filter_test_dir`
- Line 39: `md5sum $testdir/file2 | _filter_test_dir`
- Line 41: `_compare_range $testdir/file1 0 $testdir/file2 0 "$((blksz * 8))" || echo "Files 1-2 do not match (intentional)"`
- Line 45: `free_before=$(stat -f -c '%a' $testdir)`
- Line 46: `_dedupe_range $testdir/file1 $((blksz * 4)) $testdir/file2 $((blksz * 4)) $((blksz * 2)) 2>&1 | _filter_dedupe_error`
- Line 49: `free_after=$(stat -f -c '%a' $testdir)`

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through `_cleanup()`, `rm -rf $tmp.* $testdir`. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Block-size congruence, sharing verification, and post-remount checks are critical because unsupported or partially implemented sharing can otherwise look like ordinary copies. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/122 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/123 -->
# sources/test-tools/xfstests/tests/generic/123

## Purpose

Make sure user cannot overwrite, append, delete or move a file created by root. Modified CXFSQA test 940960 and 940558. The test is registered with `_begin_fstest perms auto quick` and falls into the rename area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `123` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter` and gates execution with `_require_test`, `_require_user`, `_require_unix_perm_checking`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 50: `_user_do "mv $my_test_subdir/data_coherency.txt $my_test_subdir/data_coherency2.txt"`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

The primary pass signal is the script reaching `status=0` or `exit $status` with no unexpected command failure, filtered output mismatch, or dmesg warning.

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through `_cleanup()`. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

The main risk is environmental: missing helper binaries, unsupported mount features, or output filtering drift can turn a filesystem regression into a notrun or false failure. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0	# success is the default!; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/123 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/124 -->
# sources/test-tools/xfstests/tests/generic/124

## Purpose

pat stands for pattern.  First 8 bytes contains the 64-bit number 0, second is 1, ..., until last 8 bytes (1048568-1048575) contain 131071. patw preallocates the file and then writes the pattern, patr checks it The test is registered with `_begin_fstest pattern auto quick` and falls into the preallocation/unwritten extent area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `124` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter` and gates execution with `_require_test`, `_require_scratch`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 27: `_require_scratch`
- Line 28: `_scratch_mkfs >/dev/null 2>&1`
- Line 29: `_scratch_mount`
- Line 44: `rm $TESTFILE`
- Line 53: `_scratch_unmount`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

The primary pass signal is the script reaching `status=0` or `exit $status` with no unexpected command failure, filtered output mismatch, or dmesg warning.

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through `_cleanup()`, `_cleanup`. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Range operations have off-by-one and block-boundary risk; the test relies on xfs_io command support and stable filtering of sparse/unwritten output. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `exit 1; status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/124 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/125 -->
# sources/test-tools/xfstests/tests/generic/125

## Purpose

don't use $here/src/ftrunc, as we're running it as a regular user, and $here may contain path component that a regular user doesn't have search permission The test is registered with `_begin_fstest other pnfs auto` and falls into the AIO/direct I/O, permission area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `125` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter` and gates execution with `_require_test`, `_require_user`, `_require_odirect`, `_require_chmod`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 19: `_require_chmod`
- Line 30: `chmod a+rw $TESTDIR`
- Line 31: `chmod a+rw $TESTFILE`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

The primary pass signal is the script reaching `status=0` or `exit $status` with no unexpected command failure, filtered output mismatch, or dmesg warning.

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through none declared. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

The expected output is sensitive to namespace support, user/group setup, mount options, and filtered id/name rendering. Timing and alignment make the test susceptible to architecture, page-size, and direct-I/O constraints; dmesg filtering must not hide unrelated warnings. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/125 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/126 -->
# sources/test-tools/xfstests/tests/generic/126

## Purpose

This test is testing filesystem permissions. If the sticky bit is set on the directory, that can affect the outcome. Create a new directory with known permissions in which to run this test. The test is registered with `_begin_fstest perms auto quick` and falls into the permission area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `126` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter` and gates execution with `_require_test`, `_require_chown`, `_require_chmod`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 24: `_require_chown`
- Line 25: `_require_chmod`
- Line 36: `chown 0:0 $testdir`
- Line 37: `chmod 0755 $testdir`
- Line 40: `cp $here/src/testx ./testx.file`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

The primary pass signal is the script reaching `status=0` or `exit $status` with no unexpected command failure, filtered output mismatch, or dmesg warning.

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through `_cleanup()`. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

The expected output is sensitive to namespace support, user/group setup, mount options, and filtered id/name rendering. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/126 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/127 -->
# sources/test-tools/xfstests/tests/generic/127

## Purpose

fsx tests modified from CXFSQA tests - fsx_00_lite - fsx_05_lite_mmap - fsx_10_std, - fsx_15_std_mmap The test is registered with `_begin_fstest rw auto mmap` and falls into the mmap, fsx random I/O area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `127` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter` and gates execution with `_require_test`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 14: `_begin_fstest rw auto mmap`
- Line 31: `_fsx_lite_nommap()`
- Line 33: `dd if=/dev/zero of=$TEST_DIR/fsx_lite_nommap bs=${FSX_FILE_SIZE} count=1 > /dev/null 2>&1`
- Line 34: `if ! $FSX_PROG $FSX_ARGS -L -R -W $FSX_AVOID $TEST_DIR/fsx_lite_nommap > $tmp.output 2>&1`
- Line 36: `echo "$FSX_PROG $FSX_ARGS -L -R -W $TEST_DIR/fsx_lite_nommap"`
- Line 44: `_fsx_lite_mmap()`
- Line 46: `dd if=/dev/zero of=$TEST_DIR/fsx_lite_mmap bs=${FSX_FILE_SIZE} count=1 > /dev/null 2>&1`
- Line 47: `if ! $FSX_PROG $FSX_ARGS -L $FSX_AVOID $TEST_DIR/fsx_lite_mmap > $tmp.output 2>&1`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

The primary pass signal is the script reaching `status=0` or `exit $status` with no unexpected command failure, filtered output mismatch, or dmesg warning.

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through `_cleanup()`, `rm -f $tmp.*`, `_cleanup`. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Timing and alignment make the test susceptible to architecture, page-size, and direct-I/O constraints; dmesg filtering must not hide unrelated warnings. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/127 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/128 -->
# sources/test-tools/xfstests/tests/generic/128

## Purpose

This xfstests generic script exercises permission behavior for the filesystem mounted by the test harness. The test is registered with `_begin_fstest perms auto quick` and falls into the permission area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `128` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter` and gates execution with `_require_scratch`, `_require_user`, `_require_chmod`, `_require_unix_perm_checking`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 18: `_require_chmod`
- Line 25: `cp "$(type -P ls)" $SCRATCH_MNT`
- Line 26: `chmod 700 $SCRATCH_MNT/nosuid`
- Line 27: `chmod 4755 $SCRATCH_MNT/ls`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

The primary pass signal is the script reaching `status=0` or `exit $status` with no unexpected command failure, filtered output mismatch, or dmesg warning.

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through none declared. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

The expected output is sensitive to namespace support, user/group setup, mount options, and filtered id/name rendering. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/128 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/129 -->
# sources/test-tools/xfstests/tests/generic/129

## Purpose

looptests created from CXFSQA test looptest The test is registered with `_begin_fstest rw auto quick` and falls into the permission area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `129` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter` and gates execution with `_require_scratch`, `_require_sparse_files`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 22: `_require_scratch`
- Line 25: `_scratch_mkfs >/dev/null 2>&1`
- Line 26: `_scratch_mount "-o nosuid"`
- Line 28: `mkdir $SCRATCH_MNT/looptest`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

The primary pass signal is the script reaching `status=0` or `exit $status` with no unexpected command failure, filtered output mismatch, or dmesg warning.

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through none declared. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

The expected output is sensitive to namespace support, user/group setup, mount options, and filtered id/name rendering. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/129 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/130 -->
# sources/test-tools/xfstests/tests/generic/130

## Purpose

xfs_io vector read/write and trunc tests. modified from cxfsqa tests - unixfile_basic_block_hole - unixfile_buffer_direct_coherency - unixfile_direct_rw - unixfile_eof_direct - unixfile_fsb_edge - unixfile_open_append - unixfile_open_trunc - unixfile_small_vector_async_rw - unixfile_small_vector_sync_rw The test is registered with `_begin_fstest pattern auto quick` and falls into the AIO/direct I/O, truncate area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `130` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter` and gates execution with `_require_scratch`, `_require_sparse_files`, `_require_odirect`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 33: `$XFS_IO_PROG -f -d -t -c "pwrite -S 0x63 0 65536" -c "truncate 1" -c "pwrite -S 0x41 65536 65536" -c "pread -v 0 131072" $SCRATCH_MNT/eof-zeroing_direct | _filter_xfs_io_unique`
- Line 41: `$XFS_IO_PROG -f -t -c "truncate 8192" -c "pread -v 5000 3000" $SCRATCH_MNT/blackhole | _filter_xfs_io_unique`
- Line 47: `$XFS_IO_PROG -f -t -c "pwrite -S 0x41 8000 1000" -c "pwrite -S 0x57 4000 1000" $SCRATCH_MNT/buff_direct_coherency | _filter_xfs_io_unique`
- Line 51: `$XFS_IO_PROG -d -c "pwrite -S 0x78 20480 4096" -c "pwrite -S 0x79 4096 4096" $SCRATCH_MNT/buff_direct_coherency | _filter_xfs_io_unique`
- Line 55: `$XFS_IO_PROG -c "pread -v 0 9000" $SCRATCH_MNT/buff_direct_coherency | _filter_xfs_io_unique`
- Line 60: `$XFS_IO_PROG -f -d -t -c "pwrite -S 0x78 0 65536" -c "pread -v 0 65536" -c "pwrite -S 0x46 65536 6553600" -c "pread -v 0 6619136" $SCRATCH_MNT/direct_io | _filter_xfs_io_unique`
- Line 66: `$XFS_IO_PROG -d -c "pread -v 0 6619136" $SCRATCH_MNT/direct_io | _filter_xfs_io_unique`
- Line 69: `$XFS_IO_PROG -f -d -t -c "pwrite -S 0x61 0 65536" -c "pread -v 0 65536" -c "pwrite -S 0x62 65536 131072" -c "pread -v 0 131072" $SCRATCH_MNT/async_direct_io | _filter_xfs_io_unique`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

- Line 33: `$XFS_IO_PROG -f -d -t -c "pwrite -S 0x63 0 65536" -c "truncate 1" -c "pwrite -S 0x41 65536 65536" -c "pread -v 0 131072" $SCRATCH_MNT/eof-zeroing_direct | _filter_xfs_io_unique`
- Line 41: `$XFS_IO_PROG -f -t -c "truncate 8192" -c "pread -v 5000 3000" $SCRATCH_MNT/blackhole | _filter_xfs_io_unique`
- Line 47: `$XFS_IO_PROG -f -t -c "pwrite -S 0x41 8000 1000" -c "pwrite -S 0x57 4000 1000" $SCRATCH_MNT/buff_direct_coherency | _filter_xfs_io_unique`
- Line 51: `$XFS_IO_PROG -d -c "pwrite -S 0x78 20480 4096" -c "pwrite -S 0x79 4096 4096" $SCRATCH_MNT/buff_direct_coherency | _filter_xfs_io_unique`
- Line 55: `$XFS_IO_PROG -c "pread -v 0 9000" $SCRATCH_MNT/buff_direct_coherency | _filter_xfs_io_unique`
- Line 60: `$XFS_IO_PROG -f -d -t -c "pwrite -S 0x78 0 65536" -c "pread -v 0 65536" -c "pwrite -S 0x46 65536 6553600" -c "pread -v 0 6619136" $SCRATCH_MNT/direct_io | _filter_xfs_io_unique`

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through none declared. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Timing and alignment make the test susceptible to architecture, page-size, and direct-I/O constraints; dmesg filtering must not hide unrelated warnings. Range operations have off-by-one and block-boundary risk; the test relies on xfs_io command support and stable filtering of sparse/unwritten output. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/130 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/131 -->
# sources/test-tools/xfstests/tests/generic/131

## Purpose

lock test created from CXFSQA test lockfile_simple The test is registered with `_begin_fstest perms auto quick` and falls into the generic filesystem behavior area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `131` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter`, `. ./common/locktest` and gates execution with `_require_test`, `_require_test_fcntl_advisory_locks`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 14: `. ./common/locktest`
- Line 19: `_run_locktest`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

The primary pass signal is the script reaching `status=0` or `exit $status` with no unexpected command failure, filtered output mismatch, or dmesg warning.

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through none declared. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

The main risk is environmental: missing helper binaries, unsupported mount features, or output filtering drift can turn a filesystem regression into a notrun or false failure. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/131 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/132 -->
# sources/test-tools/xfstests/tests/generic/132

## Purpose

xfs_io aligned vector rw created from CXFSQA test unixfile_vector_aligned_rw The test is registered with `_begin_fstest pattern auto` and falls into the generic filesystem behavior area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `132` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter` and gates execution with `_require_scratch`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 22: `$XFS_IO_PROG -f -t -c "pwrite -S 0x63 0 512" -c "pwrite -S 0x64 512 512" -c "pwrite -S 0x65 1024 512" -c "pwrite -S 0x66 1536 512" -c "pwrite -S 0x67 2048 512" -c "pwrite -S 0x68 2560 512" -c "pwrite -S 0x69 3072 512" -c`
- Line 40: `$XFS_IO_PROG -f -c "pwrite -S 0x63 4096 1024" -c "pwrite -S 0x6B 5120 1024" -c "pwrite -S 0x6C 6144 1024" -c "pwrite -S 0x6D 7168 1024" -c "pread -v 0 1024" -c "pread -v 1024 1024" -c "pread -v 2048 1024" -c "pread -v 30`
- Line 54: `$XFS_IO_PROG -f -c "pwrite -S 0x6E 8192 2048" -c "pwrite -S 0x6F 10240 2048" -c "pread -v 0 2048" -c "pread -v 2048 2048" -c "pread -v 4096 2048" -c "pread -v 6144 2048" -c "pread -v 8192 2048" -c "pread -v 10240 2048" $`
- Line 64: `$XFS_IO_PROG -f -c "pwrite -S 0x70 12288 4096" -c "pread -v 0 4096" -c "pread -v 4096 4096" -c "pread -v 8192 4096" -c "pread -v 12288 4096" $SCRATCH_MNT/aligned_vector_rw | _filter_xfs_io_unique`
- Line 71: `$XFS_IO_PROG -f -c "pwrite -S 0x71 16384 8192" -c "pwrite -S 0x72 24576 8192" -c "pread -v 0 8192" -c "pread -v 8192 8192" -c "pread -v 8192 8192" -c "pread -v 16384 8192" $SCRATCH_MNT/aligned_vector_rw | _filter_xfs_io_`
- Line 79: `$XFS_IO_PROG -f -c "pwrite -S 0x73 32768 16384" -c "pwrite -S 0x74 49152 16384" -c "pread -v 0 16384" -c "pread -v 16384 16384" -c "pread -v 32768 16384" -c "pread -v 49152 16384" $SCRATCH_MNT/aligned_vector_rw | _filter`
- Line 87: `$XFS_IO_PROG -f -c "pwrite -S 0x75 65536 32768" -c "pwrite -S 0x76 98304 32768" -c "pread -v 0 32768" -c "pread -v 32768 32768" -c "pread -v 65536 32768" -c "pread -v 98304 32768" $SCRATCH_MNT/aligned_vector_rw | _filter`
- Line 95: `$XFS_IO_PROG -f -c "pwrite -S 0x76 131072 65536" -c "pwrite -S 0x77 196608 65536" -c "pread -v 0 65536" -c "pread -v 65536 65536" -c "pread -v 131072 65536" -c "pread -v 196608 65536" $SCRATCH_MNT/aligned_vector_rw | _fi`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

- Line 22: `$XFS_IO_PROG -f -t -c "pwrite -S 0x63 0 512" -c "pwrite -S 0x64 512 512" -c "pwrite -S 0x65 1024 512" -c "pwrite -S 0x66 1536 512" -c "pwrite -S 0x67 2048 512" -c "pwrite -S 0x68 2560 512" -c "pwrite -S 0x69 3072 512" -c`
- Line 40: `$XFS_IO_PROG -f -c "pwrite -S 0x63 4096 1024" -c "pwrite -S 0x6B 5120 1024" -c "pwrite -S 0x6C 6144 1024" -c "pwrite -S 0x6D 7168 1024" -c "pread -v 0 1024" -c "pread -v 1024 1024" -c "pread -v 2048 1024" -c "pread -v 30`
- Line 54: `$XFS_IO_PROG -f -c "pwrite -S 0x6E 8192 2048" -c "pwrite -S 0x6F 10240 2048" -c "pread -v 0 2048" -c "pread -v 2048 2048" -c "pread -v 4096 2048" -c "pread -v 6144 2048" -c "pread -v 8192 2048" -c "pread -v 10240 2048" $`
- Line 64: `$XFS_IO_PROG -f -c "pwrite -S 0x70 12288 4096" -c "pread -v 0 4096" -c "pread -v 4096 4096" -c "pread -v 8192 4096" -c "pread -v 12288 4096" $SCRATCH_MNT/aligned_vector_rw | _filter_xfs_io_unique`
- Line 71: `$XFS_IO_PROG -f -c "pwrite -S 0x71 16384 8192" -c "pwrite -S 0x72 24576 8192" -c "pread -v 0 8192" -c "pread -v 8192 8192" -c "pread -v 8192 8192" -c "pread -v 16384 8192" $SCRATCH_MNT/aligned_vector_rw | _filter_xfs_io_`
- Line 79: `$XFS_IO_PROG -f -c "pwrite -S 0x73 32768 16384" -c "pwrite -S 0x74 49152 16384" -c "pread -v 0 16384" -c "pread -v 16384 16384" -c "pread -v 32768 16384" -c "pread -v 49152 16384" $SCRATCH_MNT/aligned_vector_rw | _filter`

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through none declared. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

The main risk is environmental: missing helper binaries, unsupported mount features, or output filtering drift can turn a filesystem regression into a notrun or false failure. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/132 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/133 -->
# sources/test-tools/xfstests/tests/generic/133

## Purpose

Concurrent I/O to same file to ensure no deadlocks The test is registered with `_begin_fstest rw auto` and falls into the AIO/direct I/O area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `133` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter` and gates execution with `_require_test`, `_require_odirect`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 19: `$XFS_IO_PROG -f -d -c 'pwrite -b 64k 0 512m' $TEST_DIR/io_test > /dev/null`
- Line 20: `$XFS_IO_PROG -f -c 'pwrite -b 64k 0 512m' $TEST_DIR/io_test >/dev/null &`
- Line 21: `$XFS_IO_PROG -c 'pread -b 64k 0 512m' $TEST_DIR/io_test > /dev/null`
- Line 27: `$XFS_IO_PROG -f -d -c 'pwrite -b 64k 0 512m' $TEST_DIR/io_test >/dev/null &`
- Line 35: `$XFS_IO_PROG -d -c 'pread -b 64k 0 512m' $TEST_DIR/io_test > /dev/null`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

- Line 21: `$XFS_IO_PROG -c 'pread -b 64k 0 512m' $TEST_DIR/io_test > /dev/null`
- Line 35: `$XFS_IO_PROG -d -c 'pread -b 64k 0 512m' $TEST_DIR/io_test > /dev/null`

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through none declared. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Timing and alignment make the test susceptible to architecture, page-size, and direct-I/O constraints; dmesg filtering must not hide unrelated warnings. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/133 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/134 -->
# sources/test-tools/xfstests/tests/generic/134

## Purpose

Ensure that we can reflink the last block of a file whose size isn't block-aligned. - Create two 'a' files file whose size isn't block-aligned. - Create two 'b' files file whose size isn't block-aligned. - Reflink the last block of file1 to the last block in file2 and file3. - Check that files 1-2 match, 3-4 don't match, and that nothing matches 3. - Check that the ends of 1-3 match, and 1-3 do not match the end of file4. The test is registered with `_begin_fstest auto quick clone` and falls into the reflink/CoW area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `134` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink` and gates execution with `_require_test_reflink`, `_require_congruent_file_oplen $TEST_DIR $blksz`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 29: `_require_test_reflink`
- Line 38: `_pwrite_byte 0x61 0 $((blksz + 37)) $testdir/file1 >> $seqres.full`
- Line 39: `_pwrite_byte 0x61 0 $((blksz + 37)) $testdir/file2 >> $seqres.full`
- Line 40: `_pwrite_byte 0x62 0 $((blksz + 37)) $testdir/file3 >> $seqres.full`
- Line 41: `_pwrite_byte 0x62 0 $((blksz + 37)) $testdir/file4 >> $seqres.full`
- Line 62: `_reflink_range $testdir/file1 $blksz $testdir/file2 $blksz 37 >> $seqres.full`
- Line 63: `_reflink_range $testdir/file1 $blksz $testdir/file3 $blksz 37 >> $seqres.full`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

- Line 44: `md5sum $testdir/file1 | _filter_test_dir`
- Line 45: `md5sum $testdir/file2 | _filter_test_dir`
- Line 46: `md5sum $testdir/file3 | _filter_test_dir`
- Line 47: `md5sum $testdir/file4 | _filter_test_dir`
- Line 85: `_compare_range $testdir/file1 $blksz $testdir/file2 $blksz 37 || echo "End sections of files 1-2 do not match"`
- Line 88: `_compare_range $testdir/file1 $blksz $testdir/file3 $blksz 37 || echo "End sections of files 1-3 do not match"`

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through `_cleanup()`, `rm -rf $tmp.* $testdir`. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Block-size congruence, sharing verification, and post-remount checks are critical because unsupported or partially implemented sharing can otherwise look like ordinary copies. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/134 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/135 -->
# sources/test-tools/xfstests/tests/generic/135

## Purpose

Concurrent I/O to same file to ensure no deadlocks The test is registered with `_begin_fstest metadata auto quick` and falls into the AIO/direct I/O, truncate area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `135` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter` and gates execution with `_require_odirect`, `_require_scratch`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 22: `$XFS_IO_PROG -f -c 'pwrite -b 4k -S 0x12 0 4k' $SCRATCH_MNT/async_file > /dev/null`
- Line 25: `$XFS_IO_PROG -f -s -c 'pwrite -b 4k -S 0x34 0 4k' $SCRATCH_MNT/sync_file > /dev/null`
- Line 28: `$XFS_IO_PROG -f -d -c 'pwrite -b 4k -S 0x56 0 4k' $SCRATCH_MNT/direct_file > /dev/null`
- Line 31: `$XFS_IO_PROG -f -c 'pwrite -b 4k -S 0x78 0 4k' $SCRATCH_MNT/trunc_file > /dev/null`
- Line 32: `$XFS_IO_PROG -f -c 'truncate 2k' $SCRATCH_MNT/trunc_file > /dev/null`
- Line 33: `$XFS_IO_PROG -c 'pwrite 1k 0 1k' $SCRATCH_MNT/trunc_file > /dev/null`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

The primary pass signal is the script reaching `status=0` or `exit $status` with no unexpected command failure, filtered output mismatch, or dmesg warning.

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through none declared. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Timing and alignment make the test susceptible to architecture, page-size, and direct-I/O constraints; dmesg filtering must not hide unrelated warnings. Range operations have off-by-one and block-boundary risk; the test relies on xfs_io command support and stable filtering of sparse/unwritten output. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/135 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/136 -->
# sources/test-tools/xfstests/tests/generic/136

## Purpose

Ensure that we can dedupe the last block of a file whose size isn't block-aligned. - Create two 'a' files file whose size isn't block-aligned. - Create two 'b' files file whose size isn't block-aligned. - Dedupe the last block of file1 to the last block in file2 and file3. - Check that files 1-2 match, and that 3-4 match. - Check that the ends of 1-2 and 3-4 match, and that 1-3 don't match. The test is registered with `_begin_fstest auto quick clone dedupe` and falls into the reflink/CoW, dedupe area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `136` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink` and gates execution with `_require_test_dedupe`, `_require_congruent_file_oplen $TEST_DIR $blksz`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 29: `_require_test_dedupe`
- Line 38: `_pwrite_byte 0x61 0 $((blksz + 37)) $testdir/file1 >> $seqres.full`
- Line 39: `_pwrite_byte 0x61 0 $((blksz + 37)) $testdir/file2 >> $seqres.full`
- Line 40: `_pwrite_byte 0x62 0 $((blksz + 37)) $testdir/file3 >> $seqres.full`
- Line 41: `_pwrite_byte 0x62 0 $((blksz + 37)) $testdir/file4 >> $seqres.full`
- Line 63: `_dedupe_range $testdir/file1 $blksz $testdir/file2 $blksz 37 >> $seqres.full`
- Line 65: `_dedupe_range $testdir/file1 $blksz $testdir/file3 $blksz 37 2>&1 | _filter_dedupe_error`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

- Line 44: `md5sum $testdir/file1 | _filter_test_dir`
- Line 45: `md5sum $testdir/file2 | _filter_test_dir`
- Line 46: `md5sum $testdir/file3 | _filter_test_dir`
- Line 47: `md5sum $testdir/file4 | _filter_test_dir`
- Line 65: `_dedupe_range $testdir/file1 $blksz $testdir/file3 $blksz 37 2>&1 | _filter_dedupe_error`
- Line 87: `_compare_range $testdir/file1 $blksz $testdir/file2 $blksz 37 || echo "End sections of files 1-2 do not match"`

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through `_cleanup()`, `rm -rf $tmp.* $testdir`. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Block-size congruence, sharing verification, and post-remount checks are critical because unsupported or partially implemented sharing can otherwise look like ordinary copies. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/136 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/137 -->
# sources/test-tools/xfstests/tests/generic/137

## Purpose

Ensure that we can reflink and dedupe blocks within the same file... - Create a file with three distinct blocks ABB - Reflink block zero to the multiple-of-three blocks - Reflink block one to the multiple-of-five blocks - Dedupe block two to the multiple-of-seven blocks - Check that we successfully avoid deduping with holes, unwritten extents, and non-matches; but actually dedupe real matches. The test is registered with `_begin_fstest auto clone dedupe prealloc` and falls into the reflink/CoW, dedupe, preallocation/unwritten extent area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `137` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink` and gates execution with `_require_test_reflink`, `_require_test_dedupe`, `_require_xfs_io_command "falloc"`, `_require_congruent_file_oplen $TEST_DIR $blksz`. Local helpers are `line 76 `check_block() {``. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 29: `_require_test_reflink`
- Line 30: `_require_test_dedupe`
- Line 31: `_require_xfs_io_command "falloc"`
- Line 40: `_pwrite_byte 0x61 0 $blksz $testdir/file1 >> $seqres.full`
- Line 41: `_pwrite_byte 0x62 $blksz $((blksz * 2)) $testdir/file1 >> $seqres.full`
- Line 45: `echo "fallocate half the file"`
- Line 46: `$XFS_IO_PROG -f -c "falloc $((nr_blks * blksz / 2)) $((nr_blks * blksz / 2))" $testdir/file1 >> $seqres.full`
- Line 50: `_reflink_range $testdir/file1 0 $testdir/file1 $((nr * 3 * blksz)) $blksz >> $seqres.full`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

- Line 69: `md5sum $testdir/file1 | _filter_test_dir`

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through `_cleanup()`, `rm -rf $tmp.* $testdir`. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Block-size congruence, sharing verification, and post-remount checks are critical because unsupported or partially implemented sharing can otherwise look like ordinary copies. Range operations have off-by-one and block-boundary risk; the test relies on xfs_io command support and stable filtering of sparse/unwritten output. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/137 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/138 -->
# sources/test-tools/xfstests/tests/generic/138

## Purpose

Ensuring that copy on write through the page cache works: - Reflink two files together - Write to the beginning, middle, and end - Check that the files are now different where we say they're different. The test is registered with `_begin_fstest auto quick clone` and falls into the reflink/CoW area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `138` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink` and gates execution with `_require_test_reflink`, `_require_cp_reflink`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 26: `_require_test_reflink`
- Line 27: `_require_cp_reflink`
- Line 35: `_pwrite_byte 0x61 0 $((blksz * 48 - 3)) $testdir/file1 >> $seqres.full`
- Line 36: `_cp_reflink $testdir/file1 $testdir/file2 >> $seqres.full`
- Line 37: `_pwrite_byte 0x61 0 $((blksz * 48 - 3)) $testdir/file2.chk >> $seqres.full`
- Line 50: `_pwrite_byte 0x62 0 17 $testdir/file2 >> $seqres.full`
- Line 51: `_pwrite_byte 0x62 0 17 $testdir/file2.chk >> $seqres.full`
- Line 53: `_pwrite_byte 0x62 $((blksz * 16 - 34)) 17 $testdir/file2 >> $seqres.full`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

- Line 41: `md5sum $testdir/file1 | _filter_test_dir`
- Line 42: `md5sum $testdir/file2 | _filter_test_dir`
- Line 43: `md5sum $testdir/file2.chk | _filter_test_dir`
- Line 45: `cmp -s $testdir/file1 $testdir/file2 || echo "file1 and file2 do not match"`
- Line 46: `cmp -s $testdir/file1 $testdir/file2.chk || echo "file1 and file2.chk do not match"`
- Line 47: `cmp -s $testdir/file2 $testdir/file2.chk || echo "file1 and file2.chk do not match"`

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through `_cleanup()`, `rm -rf $tmp.* $testdir`. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Block-size congruence, sharing verification, and post-remount checks are critical because unsupported or partially implemented sharing can otherwise look like ordinary copies. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/138 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/139 -->
# sources/test-tools/xfstests/tests/generic/139

## Purpose

Ensuring that copy on write in direct-io mode works: - Reflink two files together - Write to the beginning, middle, and end in direct-io mode - Check that the files are now different where we say they're different. The test is registered with `_begin_fstest auto quick clone` and falls into the reflink/CoW, AIO/direct I/O area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `139` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink` and gates execution with `_require_test_reflink`, `_require_cp_reflink`, `_require_odirect 512`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 26: `_require_test_reflink`
- Line 27: `_require_cp_reflink`
- Line 36: `_pwrite_byte 0x61 0 $((blksz * 48 - 3)) $testdir/file1 >> $seqres.full`
- Line 37: `_cp_reflink $testdir/file1 $testdir/file2 >> $seqres.full`
- Line 38: `_pwrite_byte 0x61 0 $((blksz * 48 - 3)) $testdir/file2.chk >> $seqres.full`
- Line 51: `_pwrite_byte 0x62 0 $blksz $testdir/file2 -d >> $seqres.full`
- Line 52: `_pwrite_byte 0x62 0 $blksz $testdir/file2.chk -d >> $seqres.full`
- Line 54: `_pwrite_byte 0x62 $((blksz * 16 - 512)) 512 $testdir/file2 -d >> $seqres.full`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

- Line 42: `md5sum $testdir/file1 | _filter_test_dir`
- Line 43: `md5sum $testdir/file2 | _filter_test_dir`
- Line 44: `md5sum $testdir/file2.chk | _filter_test_dir`
- Line 46: `cmp -s $testdir/file1 $testdir/file2 || echo "file1 and file2 should match"`
- Line 47: `cmp -s $testdir/file1 $testdir/file2.chk || echo "file1 and file2.chk should match"`
- Line 48: `cmp -s $testdir/file2 $testdir/file2.chk || echo "file2 and file2.chk should match"`

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through `_cleanup()`, `rm -rf $tmp.* $testdir`. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Block-size congruence, sharing verification, and post-remount checks are critical because unsupported or partially implemented sharing can otherwise look like ordinary copies. Timing and alignment make the test susceptible to architecture, page-size, and direct-I/O constraints; dmesg filtering must not hide unrelated warnings. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/139 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/140 -->
# sources/test-tools/xfstests/tests/generic/140

## Purpose

Ensuring that mmap copy on write through the page cache works: - Reflink two files together - Write to the beginning, middle, and end - Check that the files are now different where we say they're different. The test is registered with `_begin_fstest auto quick clone mmap` and falls into the reflink/CoW, mmap area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `140` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink` and gates execution with `_require_test_reflink`, `_require_cp_reflink`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 13: `_begin_fstest auto quick clone mmap`
- Line 26: `_require_test_reflink`
- Line 27: `_require_cp_reflink`
- Line 35: `_pwrite_byte 0x61 0 $((blksz * 48 - 3)) $testdir/file1 >> $seqres.full`
- Line 36: `_cp_reflink $testdir/file1 $testdir/file2 >> $seqres.full`
- Line 37: `_pwrite_byte 0x61 0 $((blksz * 48 - 3)) $testdir/file2.chk >> $seqres.full`
- Line 49: `echo "mmap CoW the second file"`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

- Line 41: `md5sum $testdir/file1 | _filter_test_dir`
- Line 42: `md5sum $testdir/file2 | _filter_test_dir`
- Line 43: `md5sum $testdir/file2.chk | _filter_test_dir`
- Line 45: `cmp -s $testdir/file1 $testdir/file2 || echo "file1 and file2 do not match"`
- Line 46: `cmp -s $testdir/file1 $testdir/file2.chk || echo "file1 and file2.chk do not match"`
- Line 47: `cmp -s $testdir/file2 $testdir/file2.chk || echo "file2 and file2.chk do not match"`

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through `_cleanup()`, `rm -rf $tmp.* $testdir`. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Block-size congruence, sharing verification, and post-remount checks are critical because unsupported or partially implemented sharing can otherwise look like ordinary copies. Timing and alignment make the test susceptible to architecture, page-size, and direct-I/O constraints; dmesg filtering must not hide unrelated warnings. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/140 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/141 -->
# sources/test-tools/xfstests/tests/generic/141

## Purpose

create file, mmap a region and mmap read it The test is registered with `_begin_fstest rw auto quick mmap` and falls into the mmap area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `141` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter` and gates execution with `_require_scratch`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 10: `_begin_fstest rw auto quick mmap`
- Line 21: `file=$SCRATCH_MNT/mmap`
- Line 23: `$XFS_IO_PROG -f -c "pwrite 0 1024k" -c "mmap 64k 64k" -c "mread -r" $file > /dev/null`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

The primary pass signal is the script reaching `status=0` or `exit $status` with no unexpected command failure, filtered output mismatch, or dmesg warning.

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through none declared. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Timing and alignment make the test susceptible to architecture, page-size, and direct-I/O constraints; dmesg filtering must not hide unrelated warnings. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/141 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/142 -->
# sources/test-tools/xfstests/tests/generic/142

## Purpose

Ensure that reflinking a file N times and CoWing the copies leaves the original intact. - Create a file and record its hash - Create some reflink copies - Rewrite all the reflink copies - Compare the contents of the original file The test is registered with `_begin_fstest auto quick clone` and falls into the reflink/CoW area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `142` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink` and gates execution with `_require_test_reflink`, `_require_cp_reflink`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 28: `_require_test_reflink`
- Line 29: `_require_cp_reflink`
- Line 39: `_pwrite_byte 0x61 0 $((blksz * 256)) $testdir/file1 >> $seqres.full`
- Line 47: `_cp_reflink $testdir/file1 $testdir/file$i`
- Line 53: `_pwrite_byte 0x62 0 $((blksz * 256)) $testdir/file$i >> $seqres.full`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

- Line 42: `md5sum $testdir/file1 | _filter_test_dir`
- Line 59: `md5sum $testdir/file2 | _filter_test_dir`

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through `_cleanup()`, `rm -rf $tmp.* $testdir`. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Block-size congruence, sharing verification, and post-remount checks are critical because unsupported or partially implemented sharing can otherwise look like ordinary copies. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/142 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/143 -->
# sources/test-tools/xfstests/tests/generic/143

## Purpose

Ensure that reflinking a file N times and DIO CoWing the copies leaves the original intact. - Create a file and record its hash - Create some reflink copies - Rewrite all the reflink copies w/ directio - Compare the contents of the original file The test is registered with `_begin_fstest auto quick clone` and falls into the reflink/CoW, AIO/direct I/O area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `143` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink` and gates execution with `_require_test_reflink`, `_require_cp_reflink`, `_require_odirect`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 28: `_require_test_reflink`
- Line 29: `_require_cp_reflink`
- Line 40: `_pwrite_byte 0x61 0 $((blksz * 256)) $testdir/file1 >> $seqres.full`
- Line 48: `_cp_reflink $testdir/file1 $testdir/file$i`
- Line 54: `_pwrite_byte 0x62 0 $((blksz * 256)) $testdir/file$i -d >> $seqres.full`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

- Line 43: `md5sum $testdir/file1 | _filter_test_dir`
- Line 60: `md5sum $testdir/file2 | _filter_test_dir`

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through `_cleanup()`, `rm -rf $tmp.* $testdir`. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Block-size congruence, sharing verification, and post-remount checks are critical because unsupported or partially implemented sharing can otherwise look like ordinary copies. Timing and alignment make the test susceptible to architecture, page-size, and direct-I/O constraints; dmesg filtering must not hide unrelated warnings. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/143 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/144 -->
# sources/test-tools/xfstests/tests/generic/144

## Purpose

Ensure that fallocate steps around reflinked ranges: - Reflink parts of two files together - Fallocate all the other sparse space. - Check that the reflinked areas are still there. The test is registered with `_begin_fstest auto quick clone prealloc` and falls into the reflink/CoW, preallocation/unwritten extent, truncate area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `144` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink` and gates execution with `_require_test_reflink`, `_require_cp_reflink`, `_require_xfs_io_command "falloc"`, `_require_xfs_io_command "truncate"`, `_require_congruent_file_oplen $TEST_DIR $blksz`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 26: `_require_test_reflink`
- Line 27: `_require_cp_reflink`
- Line 28: `_require_xfs_io_command "falloc"`
- Line 29: `_require_xfs_io_command "truncate"`
- Line 38: `_pwrite_byte 0x61 0 $((blksz * 5 + 37)) $testdir/file1 >> $seqres.full`
- Line 40: `_reflink_range $testdir/file1 $blksz $testdir/file2 $blksz $((blksz * 4 + 37)) >> $seqres.full`
- Line 43: `$XFS_IO_PROG -f -c "truncate $((blksz * 5 + 37))" $testdir/file3 >> $seqres.full`
- Line 44: `_reflink_range $testdir/file1 0 $testdir/file3 0 $blksz >> $seqres.full`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

- Line 55: `md5sum $testdir/file1 | _filter_test_dir`
- Line 56: `md5sum $testdir/file2 | _filter_test_dir`
- Line 57: `md5sum $testdir/file3 | _filter_test_dir`
- Line 58: `md5sum $testdir/file4 | _filter_test_dir`
- Line 59: `md5sum $testdir/file5 | _filter_test_dir`
- Line 61: `_compare_range $testdir/file1 $blksz $testdir/file2 $blksz $((blksz * 4 + 37)) || echo "shared parts of files 1-2 changed"`

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through `_cleanup()`, `rm -rf $tmp.* $testdir`. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Block-size congruence, sharing verification, and post-remount checks are critical because unsupported or partially implemented sharing can otherwise look like ordinary copies. Range operations have off-by-one and block-boundary risk; the test relies on xfs_io command support and stable filtering of sparse/unwritten output. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/144 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/145 -->
# sources/test-tools/xfstests/tests/generic/145

## Purpose

Ensure that collapse range steps around reflinked ranges: - Create three reflink clones of a file - Collapse the start, middle, and end of the reflink range of each of the three files, respectively - Check that the reflinked areas are still there. The test is registered with `_begin_fstest auto quick clone collapse prealloc` and falls into the reflink/CoW, preallocation/unwritten extent, collapse range area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `145` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink` and gates execution with `_require_test_reflink`, `_require_cp_reflink`, `_require_xfs_io_command "falloc"`, `_require_xfs_io_command "fcollapse"`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 27: `_require_test_reflink`
- Line 28: `_require_cp_reflink`
- Line 29: `_require_xfs_io_command "falloc"`
- Line 30: `_require_xfs_io_command "fcollapse"`
- Line 38: `_pwrite_byte 0x61 0 $blksz $testdir/file1 >> $seqres.full`
- Line 39: `_pwrite_byte 0x62 $blksz $blksz $testdir/file1 >> $seqres.full`
- Line 40: `_pwrite_byte 0x63 $((blksz * 2)) $blksz $testdir/file1 >> $seqres.full`
- Line 42: `_cp_reflink $testdir/file1 $testdir/file2`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

- Line 64: `md5sum $testdir/file1 | _filter_test_dir`
- Line 65: `md5sum $testdir/file2 | _filter_test_dir`
- Line 66: `md5sum $testdir/file3 | _filter_test_dir`
- Line 67: `md5sum $testdir/file4 | _filter_test_dir`
- Line 68: `md5sum $testdir/file2.chk | _filter_test_dir`
- Line 69: `md5sum $testdir/file3.chk | _filter_test_dir`

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through `_cleanup()`, `rm -rf $tmp.* $testdir`. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Block-size congruence, sharing verification, and post-remount checks are critical because unsupported or partially implemented sharing can otherwise look like ordinary copies. Range operations have off-by-one and block-boundary risk; the test relies on xfs_io command support and stable filtering of sparse/unwritten output. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/145 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/146 -->
# sources/test-tools/xfstests/tests/generic/146

## Purpose

Ensure that punch-hole steps around reflinked ranges: - Create three reflink clones of a file - Punch the start, middle, and end of the reflink range of each of the three files, respectively - Check that the reflinked areas are still there. The test is registered with `_begin_fstest auto quick clone punch` and falls into the reflink/CoW, hole punching area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `146` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink` and gates execution with `_require_test_reflink`, `_require_cp_reflink`, `_require_xfs_io_command "fpunch"`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 27: `_require_test_reflink`
- Line 28: `_require_cp_reflink`
- Line 29: `_require_xfs_io_command "fpunch"`
- Line 37: `_pwrite_byte 0x61 0 $blksz $testdir/file1 >> $seqres.full`
- Line 38: `_pwrite_byte 0x62 $blksz $blksz $testdir/file1 >> $seqres.full`
- Line 39: `_pwrite_byte 0x63 $((blksz * 2)) $blksz $testdir/file1 >> $seqres.full`
- Line 41: `_cp_reflink $testdir/file1 $testdir/file2`
- Line 42: `_cp_reflink $testdir/file1 $testdir/file3`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

- Line 58: `md5sum $testdir/file1 | _filter_test_dir`
- Line 59: `md5sum $testdir/file2 | _filter_test_dir`
- Line 60: `md5sum $testdir/file3 | _filter_test_dir`
- Line 61: `md5sum $testdir/file4 | _filter_test_dir`
- Line 62: `md5sum $testdir/file2.chk | _filter_test_dir`
- Line 63: `md5sum $testdir/file3.chk | _filter_test_dir`

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through `_cleanup()`, `rm -rf $tmp.* $testdir`. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Block-size congruence, sharing verification, and post-remount checks are critical because unsupported or partially implemented sharing can otherwise look like ordinary copies. Range operations have off-by-one and block-boundary risk; the test relies on xfs_io command support and stable filtering of sparse/unwritten output. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/146 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/147 -->
# sources/test-tools/xfstests/tests/generic/147

## Purpose

Ensure that insert range steps around reflinked ranges: - Create three reflink clones of a file - Insert into the start, middle, and end of the reflink range of each of the three files, respectively - Check that the reflinked areas are still there. The test is registered with `_begin_fstest auto quick clone insert` and falls into the reflink/CoW, insert range area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `147` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink` and gates execution with `_require_test_reflink`, `_require_cp_reflink`, `_require_xfs_io_command "finsert"`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 27: `_require_test_reflink`
- Line 28: `_require_cp_reflink`
- Line 29: `_require_xfs_io_command "finsert"`
- Line 37: `_pwrite_byte 0x61 0 $blksz $testdir/file1 >> $seqres.full`
- Line 38: `_pwrite_byte 0x62 $blksz $blksz $testdir/file1 >> $seqres.full`
- Line 39: `_pwrite_byte 0x63 $((blksz * 2)) $blksz $testdir/file1 >> $seqres.full`
- Line 41: `_cp_reflink $testdir/file1 $testdir/file2`
- Line 42: `_cp_reflink $testdir/file1 $testdir/file3`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

- Line 61: `md5sum $testdir/file1 | _filter_test_dir`
- Line 62: `md5sum $testdir/file2 | _filter_test_dir`
- Line 63: `md5sum $testdir/file3 | _filter_test_dir`
- Line 64: `md5sum $testdir/file4 | _filter_test_dir`
- Line 65: `md5sum $testdir/file2.chk | _filter_test_dir`
- Line 66: `md5sum $testdir/file3.chk | _filter_test_dir`

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through `_cleanup()`, `rm -rf $tmp.* $testdir`. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Block-size congruence, sharing verification, and post-remount checks are critical because unsupported or partially implemented sharing can otherwise look like ordinary copies. Range operations have off-by-one and block-boundary risk; the test relies on xfs_io command support and stable filtering of sparse/unwritten output. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/147 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/148 -->
# sources/test-tools/xfstests/tests/generic/148

## Purpose

Ensure that truncating the last block in a reflinked file CoWs appropriately: - Create a file that doesn't end on a block boundary - Create two reflink clones of the file - Shorten one of the clones with truncate - Lengthen the other clone with truncate - Check that the reflinked areas are still there. The test is registered with `_begin_fstest auto quick clone` and falls into the reflink/CoW, truncate area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `148` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink` and gates execution with `_require_test_reflink`, `_require_cp_reflink`, `_require_xfs_io_command "truncate"`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 28: `_require_test_reflink`
- Line 29: `_require_cp_reflink`
- Line 30: `_require_xfs_io_command "truncate"`
- Line 38: `_pwrite_byte 0x61 0 $blksz $testdir/file1 >> $seqres.full`
- Line 39: `_pwrite_byte 0x62 $blksz 37 $testdir/file1 >> $seqres.full`
- Line 41: `_cp_reflink $testdir/file1 $testdir/file2`
- Line 42: `_cp_reflink $testdir/file1 $testdir/file3`
- Line 44: `_pwrite_byte 0x61 0 $blksz $testdir/file2.chk >> $seqres.full`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

- Line 52: `md5sum $testdir/file1 | _filter_test_dir`
- Line 53: `md5sum $testdir/file2 | _filter_test_dir`
- Line 54: `md5sum $testdir/file3 | _filter_test_dir`
- Line 55: `md5sum $testdir/file2.chk | _filter_test_dir`
- Line 56: `md5sum $testdir/file3.chk | _filter_test_dir`
- Line 87: `cmp -s $testdir/file2 $testdir/file2.chk || echo "file2 and file2.chk do not match"`

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through `_cleanup()`, `rm -rf $tmp.* $testdir`. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Block-size congruence, sharing verification, and post-remount checks are critical because unsupported or partially implemented sharing can otherwise look like ordinary copies. Range operations have off-by-one and block-boundary risk; the test relies on xfs_io command support and stable filtering of sparse/unwritten output. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/148 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/149 -->
# sources/test-tools/xfstests/tests/generic/149

## Purpose

Ensure that zero-range steps around reflinked ranges: - Create three reflink clones of a file - Zero-range the start, middle, and end of the reflink range of each of the three files, respectively - Check that the reflinked areas are still there. The test is registered with `_begin_fstest auto quick clone zero` and falls into the reflink/CoW, zero range area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `149` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink` and gates execution with `_require_test_reflink`, `_require_cp_reflink`, `_require_xfs_io_command "fzero"`, `_require_congruent_file_oplen $TEST_DIR $blksz`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 27: `_require_test_reflink`
- Line 28: `_require_cp_reflink`
- Line 29: `_require_xfs_io_command "fzero"`
- Line 38: `_pwrite_byte 0x61 0 $blksz $testdir/file1 >> $seqres.full`
- Line 39: `_pwrite_byte 0x62 $blksz $blksz $testdir/file1 >> $seqres.full`
- Line 40: `_pwrite_byte 0x63 $((blksz * 2)) $blksz $testdir/file1 >> $seqres.full`
- Line 42: `_cp_reflink $testdir/file1 $testdir/file2`
- Line 43: `_cp_reflink $testdir/file1 $testdir/file3`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

- Line 59: `md5sum $testdir/file1 | _filter_test_dir`
- Line 60: `md5sum $testdir/file2 | _filter_test_dir`
- Line 61: `md5sum $testdir/file3 | _filter_test_dir`
- Line 62: `md5sum $testdir/file4 | _filter_test_dir`
- Line 63: `md5sum $testdir/file2.chk | _filter_test_dir`
- Line 64: `md5sum $testdir/file3.chk | _filter_test_dir`

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through `_cleanup()`, `rm -rf $tmp.* $testdir`. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Block-size congruence, sharing verification, and post-remount checks are critical because unsupported or partially implemented sharing can otherwise look like ordinary copies. Range operations have off-by-one and block-boundary risk; the test relies on xfs_io command support and stable filtering of sparse/unwritten output. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/149 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/150 -->
# sources/test-tools/xfstests/tests/generic/150

## Purpose

Ensure that reflinking a file N times doesn't eat a lot of blocks - Create a file and record fs block usage - Create some reflink copies - Compare fs block usage to before The test is registered with `_begin_fstest auto quick clone` and falls into the reflink/CoW area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `150` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink` and gates execution with `_require_test_reflink`, `_require_cp_reflink`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 26: `_require_test_reflink`
- Line 27: `_require_cp_reflink`
- Line 40: `_pwrite_byte 0x61 0 $sz $testdir/file1 >> $seqres.full`
- Line 46: `_cp_reflink $testdir/file1 $testdir/file.$i`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

- Line 42: `free_blocks0=$(stat -f $testdir -c '%f')`
- Line 49: `free_blocks1=$(stat -f $testdir -c '%f')`

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through `_cleanup()`, `rm -rf $tmp.* $testdir`. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Block-size congruence, sharing verification, and post-remount checks are critical because unsupported or partially implemented sharing can otherwise look like ordinary copies. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/150 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/151 -->
# sources/test-tools/xfstests/tests/generic/151

## Purpose

Ensure that deleting all copies of a file reflinked N times releases the blocks - Record fs block usage (0) - Create a file and some reflink copies - Record fs block usage (1) - Delete some copies of the file - Record fs block usage (2) - Delete all copies of the file - Compare fs block usage to (2), (1), and (0) The test is registered with `_begin_fstest auto quick clone` and falls into the reflink/CoW area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `151` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink` and gates execution with `_require_test_reflink`, `_require_cp_reflink`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 30: `_require_test_reflink`
- Line 31: `_require_cp_reflink`
- Line 45: `_pwrite_byte 0x61 0 $sz $testdir/file1 >> $seqres.full`
- Line 50: `_cp_reflink $testdir/file1 $testdir/file.$i`
- Line 52: `_cp_reflink $testdir/file1 $testdir/survivor`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

- Line 42: `free_blocks0=$(stat -f $testdir -c '%f')`
- Line 54: `free_blocks1=$(stat -f $testdir -c '%f')`
- Line 59: `free_blocks2=$(stat -f $testdir -c '%f')`
- Line 64: `free_blocks3=$(stat -f $testdir -c '%f')`

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through `_cleanup()`, `rm -rf $tmp.* $testdir`. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Block-size congruence, sharing verification, and post-remount checks are critical because unsupported or partially implemented sharing can otherwise look like ordinary copies. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/151 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/152 -->
# sources/test-tools/xfstests/tests/generic/152

## Purpose

Ensure that punching all copies of a file reflinked N times releases the blocks - Record fs block usage (0) - Create a file and some reflink copies - Record fs block usage (1) - Punch some blocks of the copies - Record fs block usage (2) - Punch all blocks of the copies - Compare fs block usage to (2), (1), and (0) The test is registered with `_begin_fstest auto quick clone punch` and falls into the reflink/CoW, hole punching area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `152` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink` and gates execution with `_require_test_reflink`, `_require_cp_reflink`, `_require_xfs_io_command "fpunch"`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 30: `_require_test_reflink`
- Line 31: `_require_cp_reflink`
- Line 32: `_require_xfs_io_command "fpunch"`
- Line 46: `_pwrite_byte 0x61 0 $sz $testdir/file1 >> $seqres.full`
- Line 51: `_cp_reflink $testdir/file1 $testdir/file$i`
- Line 57: `$XFS_IO_PROG -f -c "fpunch 0 $sz" $testdir/file2`
- Line 58: `$XFS_IO_PROG -f -c "fpunch 0 $((sz / 2))" $testdir/file3`
- Line 59: `$XFS_IO_PROG -f -c "fpunch $((sz / 2)) $((sz / 2))" $testdir/file4`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

- Line 43: `free_blocks0=$(stat -f $testdir -c '%f')`
- Line 54: `free_blocks1=$(stat -f $testdir -c '%f')`
- Line 61: `free_blocks2=$(stat -f $testdir -c '%f')`
- Line 69: `free_blocks3=$(stat -f $testdir -c '%f')`

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through `_cleanup()`, `rm -rf $tmp.* $testdir`. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Block-size congruence, sharing verification, and post-remount checks are critical because unsupported or partially implemented sharing can otherwise look like ordinary copies. Range operations have off-by-one and block-boundary risk; the test relies on xfs_io command support and stable filtering of sparse/unwritten output. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/152 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/153 -->
# sources/test-tools/xfstests/tests/generic/153

## Purpose

Ensure that collapse-range on all copies of a file reflinked N times releases the blocks - Record fs block usage (0) - Create a file and some reflink copies - Record fs block usage (1) - Collapse-range some blocks of the copies - Record fs block usage (2) - Truncate all blocks of the copies - Compare fs block usage to (2), (1), and (0) The test is registered with `_begin_fstest auto quick clone collapse` and falls into the reflink/CoW, collapse range, truncate area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `153` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink` and gates execution with `_require_test_reflink`, `_require_cp_reflink`, `_require_xfs_io_command "fcollapse"`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 30: `_require_test_reflink`
- Line 31: `_require_cp_reflink`
- Line 32: `_require_xfs_io_command "fcollapse"`
- Line 46: `_pwrite_byte 0x61 0 $sz $testdir/file1 >> $seqres.full`
- Line 51: `_cp_reflink $testdir/file1 $testdir/file$i`
- Line 57: `$XFS_IO_PROG -f -c "fcollapse 0 $(((blks - 1) * blksz))" $testdir/file2`
- Line 58: `$XFS_IO_PROG -f -c "fcollapse 0 $((sz / 2))" $testdir/file3`
- Line 59: `$XFS_IO_PROG -f -c "fcollapse $((sz / 2)) $(( ((blks / 2) - 1) * blksz))" $testdir/file4`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

- Line 43: `free_blocks0=$(stat -f $testdir -c '%f')`
- Line 54: `free_blocks1=$(stat -f $testdir -c '%f')`
- Line 61: `free_blocks2=$(stat -f $testdir -c '%f')`
- Line 68: `free_blocks3=$(stat -f $testdir -c '%f')`

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through `_cleanup()`, `rm -rf $tmp.* $testdir`. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Block-size congruence, sharing verification, and post-remount checks are critical because unsupported or partially implemented sharing can otherwise look like ordinary copies. Range operations have off-by-one and block-boundary risk; the test relies on xfs_io command support and stable filtering of sparse/unwritten output. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/153 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/154 -->
# sources/test-tools/xfstests/tests/generic/154

## Purpose

Ensure that CoW on all copies of a file reflinked N times increases block count - Record fs block usage (0) - Create a file and some reflink copies - Record fs block usage (1) - CoW some blocks of the copies - Record fs block usage (2) - CoW all the rest of the blocks of the copies - Compare fs block usage to (2), (1), and (0) The test is registered with `_begin_fstest auto quick clone` and falls into the reflink/CoW area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `154` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink` and gates execution with `_require_test_reflink`, `_require_cp_reflink`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 30: `_require_test_reflink`
- Line 31: `_require_cp_reflink`
- Line 45: `_pwrite_byte 0x61 0 $sz $testdir/file1 >> $seqres.full`
- Line 50: `_cp_reflink $testdir/file1 $testdir/file$i`
- Line 56: `_pwrite_byte 0x62 0 $sz $testdir/file2 >> $seqres.full`
- Line 57: `_pwrite_byte 0x63 0 $((sz / 2)) $testdir/file3 >> $seqres.full`
- Line 58: `_pwrite_byte 0x64 $((sz / 2)) $((sz / 2)) $testdir/file4 >> $seqres.full`
- Line 64: `_pwrite_byte 0x63 0 $sz $testdir/file3 >> $seqres.full`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

- Line 41: `free_blocks0=$(stat -f $testdir -c '%f')`
- Line 53: `free_blocks1=$(stat -f $testdir -c '%f')`
- Line 60: `free_blocks2=$(stat -f $testdir -c '%f')`
- Line 67: `free_blocks3=$(stat -f $testdir -c '%f')`
- Line 72: `free_blocks4=$(stat -f $testdir -c '%f')`

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through `_cleanup()`, `rm -rf $tmp.* $testdir`. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Block-size congruence, sharing verification, and post-remount checks are critical because unsupported or partially implemented sharing can otherwise look like ordinary copies. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/154 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/155 -->
# sources/test-tools/xfstests/tests/generic/155

## Purpose

Ensure that CoW on all copies of a file reflinked N times increases block count - Record fs block usage (0) - Create a file and some reflink copies - Record fs block usage (1) - CoW some blocks of the copies - Record fs block usage (2) - CoW all the rest of the blocks of the copies - Compare fs block usage to (2), (1), and (0) The test is registered with `_begin_fstest auto quick clone zero` and falls into the reflink/CoW, AIO/direct I/O, zero range area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `155` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink` and gates execution with `_require_test_reflink`, `_require_cp_reflink`, `_require_xfs_io_command "fzero"`, `_require_odirect`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 32: `_require_test_reflink`
- Line 33: `_require_cp_reflink`
- Line 34: `_require_xfs_io_command "fzero"`
- Line 49: `_pwrite_byte 0x61 0 $sz $testdir/file1 >> $seqres.full`
- Line 54: `_cp_reflink $testdir/file1 $testdir/file$i`
- Line 60: `$XFS_IO_PROG -f -c "fzero 0 $sz" $testdir/file2 >> $seqres.full`
- Line 61: `_pwrite_byte 0x63 0 $((sz / 2)) $testdir/file3 -d >> $seqres.full`
- Line 67: `_pwrite_byte 0x62 0 $sz $testdir/file2 -d >> $seqres.full`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

- Line 46: `free_blocks0=$(stat -f $testdir -c '%f')`
- Line 57: `free_blocks1=$(stat -f $testdir -c '%f')`
- Line 64: `free_blocks2=$(stat -f $testdir -c '%f')`
- Line 71: `free_blocks3=$(stat -f $testdir -c '%f')`
- Line 76: `free_blocks4=$(stat -f $testdir -c '%f')`

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through `_cleanup()`, `rm -rf $tmp.* $testdir`. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Block-size congruence, sharing verification, and post-remount checks are critical because unsupported or partially implemented sharing can otherwise look like ordinary copies. Timing and alignment make the test susceptible to architecture, page-size, and direct-I/O constraints; dmesg filtering must not hide unrelated warnings. Range operations have off-by-one and block-boundary risk; the test relies on xfs_io command support and stable filtering of sparse/unwritten output. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/155 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/156 -->
# sources/test-tools/xfstests/tests/generic/156

## Purpose

Ensure that fallocate on reflinked files actually CoWs the shared blocks. - Record fs block usage (0) - Create a file and some reflink copies - Record fs block usage (1) - funshare half of one of the copies - Record fs block usage (2) - funshare all of the copies - Record fs block usage (3) - rewrite the original file - Record fs block usage (4) The test is registered with `_begin_fstest auto quick clone unshare` and falls into the reflink/CoW, xattr, preallocation/unwritten extent area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `156` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`, `. ./common/reflink` and gates execution with `_require_test_reflink`, `_require_cp_reflink`, `_require_xfs_io_command "funshare"`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 37: `_require_test_reflink`
- Line 38: `_require_cp_reflink`
- Line 53: `_pwrite_byte 0x61 0 $sz $testdir/file1 >> $seqres.full`
- Line 58: `_cp_reflink $testdir/file1 $testdir/file$i`
- Line 64: `$XFS_IO_PROG -f -c "funshare 0 $((sz / 2))" $testdir/file2`
- Line 68: `$XFS_IO_PROG -f -c "funshare 0 $sz" $testdir/file2`
- Line 69: `$XFS_IO_PROG -f -c "funshare 0 $sz" $testdir/file3`
- Line 74: `$XFS_IO_PROG -f -c "funshare 0 $sz" $testdir/file4`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

- Line 50: `free_blocks0=$(stat -f $testdir -c '%f')`
- Line 61: `free_blocks1=$(stat -f $testdir -c '%f')`
- Line 71: `free_blocks2=$(stat -f $testdir -c '%f')`
- Line 77: `free_blocks3=$(stat -f $testdir -c '%f')`
- Line 82: `free_blocks4=$(stat -f $testdir -c '%f')`

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through `_cleanup()`, `rm -rf $tmp.* $testdir`. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Block-size congruence, sharing verification, and post-remount checks are critical because unsupported or partially implemented sharing can otherwise look like ordinary copies. The expected output is sensitive to namespace support, user/group setup, mount options, and filtered id/name rendering. Range operations have off-by-one and block-boundary risk; the test relies on xfs_io command support and stable filtering of sparse/unwritten output. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/156 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/157 -->
# sources/test-tools/xfstests/tests/generic/157

## Purpose

Check that various invalid reflink scenarios are rejected. The test is registered with `_begin_fstest auto quick clone` and falls into the reflink/CoW, xattr area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `157` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`, `. ./common/reflink` and gates execution with `_require_test_reflink`, `_require_scratch_reflink`, `_require_mknod`. Local helpers are `line 60 `_filter_enotty() {``, `line 64 `_filter_einval() {``. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 24: `_require_test_reflink`
- Line 25: `_require_scratch_reflink`
- Line 47: `_pwrite_byte 0x61 0 $sz $testdir1/file1 >> $seqres.full`
- Line 48: `_pwrite_byte 0x61 0 $sz $testdir1/file2 >> $seqres.full`
- Line 49: `_pwrite_byte 0x61 0 $sz $testdir2/file1 >> $seqres.full`
- Line 50: `_pwrite_byte 0x61 0 $sz $testdir2/file2 >> $seqres.full`
- Line 69: `_reflink_range $testdir1/file1 0 $testdir2/file1 0 $blksz`
- Line 72: `_reflink_range $testdir1/file1 37 $testdir1/file1 59 23`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

- Line 44: `free_blocks0=$(stat -f $testdir1 -c '%f')`
- Line 87: `_reflink_range $testdir1/file1 0 $testdir1/dir1 0 $blksz 2>&1 | _filter_test_dir`
- Line 90: `_reflink_range $testdir1/file1 0 $testdir1/dev1 0 $blksz 2>&1 | _filter_enotty`
- Line 93: `_reflink_range $testdir1/file1 0 $testdir1/fifo1 0 $blksz -n 2>&1 | _filter_enotty`
- Line 96: `_reflink_range $testdir1/file1 0 $testdir1/file3 0 $blksz -a 2>&1 | _filter_einval`

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through `_cleanup()`, `rm -rf $tmp.* $testdir1`. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Block-size congruence, sharing verification, and post-remount checks are critical because unsupported or partially implemented sharing can otherwise look like ordinary copies. The expected output is sensitive to namespace support, user/group setup, mount options, and filtered id/name rendering. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/157 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/158 -->
# sources/test-tools/xfstests/tests/generic/158

## Purpose

Check that various invalid dedupe scenarios are rejected. The test is registered with `_begin_fstest auto quick clone dedupe` and falls into the reflink/CoW, dedupe, xattr area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `158` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`, `. ./common/reflink` and gates execution with `_require_test_dedupe`, `_require_scratch_dedupe`, `_require_mknod`. Local helpers are `line 61 `_filter_enotty() {``, `line 66 `_filter_eperm() {``. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 24: `_require_test_dedupe`
- Line 25: `_require_scratch_dedupe`
- Line 47: `_pwrite_byte 0x61 0 $sz $testdir1/file1 >> $seqres.full`
- Line 48: `_pwrite_byte 0x61 0 $sz $testdir1/file2 >> $seqres.full`
- Line 49: `_pwrite_byte 0x61 0 $sz $testdir1/file3 >> $seqres.full`
- Line 50: `_pwrite_byte 0x61 0 $sz $testdir2/file1 >> $seqres.full`
- Line 51: `_pwrite_byte 0x61 0 $sz $testdir2/file2 >> $seqres.full`
- Line 62: `_filter_dedupe_error | sed -e 's/Inappropriate ioctl for device/Invalid argument/g'`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

- Line 44: `free_blocks0=$(stat -f $testdir1 -c '%f')`
- Line 62: `_filter_dedupe_error | sed -e 's/Inappropriate ioctl for device/Invalid argument/g'`
- Line 67: `_filter_dedupe_error | sed -e 's/Permission denied/Invalid argument/g'`
- Line 72: `_dedupe_range $testdir1/file1 0 $testdir2/file1 0 $blksz 2>&1 | _filter_dedupe_error`
- Line 76: `_dedupe_range $testdir1/file1 37 $testdir1/file1 59 23 2>&1 | _filter_dedupe_error`
- Line 80: `_dedupe_range $testdir1/file1 0 $testdir1/file1 1 $((blksz * 2)) 2>&1 | _filter_dedupe_error`

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through `_cleanup()`, `rm -rf $tmp.* $testdir1`. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Block-size congruence, sharing verification, and post-remount checks are critical because unsupported or partially implemented sharing can otherwise look like ordinary copies. The expected output is sensitive to namespace support, user/group setup, mount options, and filtered id/name rendering. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/158 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/159 -->
# sources/test-tools/xfstests/tests/generic/159

## Purpose

Check that we can't reflink immutable files The test is registered with `_begin_fstest auto quick clone` and falls into the reflink/CoW, xattr area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `159` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`, `. ./common/reflink` and gates execution with `_require_chattr i`, `_require_test_reflink`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 25: `_require_test_reflink`
- Line 40: `_pwrite_byte 0x61 0 $sz $testdir1/file1 >> $seqres.full`
- Line 41: `_pwrite_byte 0x61 0 $sz $testdir1/file2 >> $seqres.full`
- Line 51: `_reflink_range $testdir1/file1 0 $testdir1/file2 0 $blksz 2>&1 | do_filter_output`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

- Line 37: `free_blocks0=$(stat -f $testdir1 -c '%f')`
- Line 51: `_reflink_range $testdir1/file1 0 $testdir1/file2 0 $blksz 2>&1 | do_filter_output`

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through `_cleanup()`, `rm -rf $tmp.* $testdir1`. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Block-size congruence, sharing verification, and post-remount checks are critical because unsupported or partially implemented sharing can otherwise look like ordinary copies. The expected output is sensitive to namespace support, user/group setup, mount options, and filtered id/name rendering. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/159 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/160 -->
# sources/test-tools/xfstests/tests/generic/160

## Purpose

Check that we can't dedupe immutable files The test is registered with `_begin_fstest auto quick clone dedupe` and falls into the reflink/CoW, dedupe, xattr area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `160` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`, `. ./common/reflink` and gates execution with `_require_chattr i`, `_require_test_dedupe`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 25: `_require_test_dedupe`
- Line 40: `_pwrite_byte 0x61 0 $sz $testdir1/file1 >> $seqres.full`
- Line 41: `_pwrite_byte 0x61 0 $sz $testdir1/file2 >> $seqres.full`
- Line 51: `_dedupe_range $testdir1/file1 0 $testdir1/file2 0 $blksz 2>&1 | do_filter_output`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

- Line 37: `free_blocks0=$(stat -f $testdir1 -c '%f')`
- Line 51: `_dedupe_range $testdir1/file1 0 $testdir1/file2 0 $blksz 2>&1 | do_filter_output`

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through `_cleanup()`, `rm -rf $tmp.* $testdir1`. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Block-size congruence, sharing verification, and post-remount checks are critical because unsupported or partially implemented sharing can otherwise look like ordinary copies. The expected output is sensitive to namespace support, user/group setup, mount options, and filtered id/name rendering. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/160 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/161 -->
# sources/test-tools/xfstests/tests/generic/161

## Purpose

This xfstests generic script exercises reflink/CoW behavior for the filesystem mounted by the test harness. The test is registered with `_begin_fstest auto quick clone` and falls into the reflink/CoW area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `161` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink` and gates execution with `_require_scratch_reflink`, `_require_cp_reflink`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 26: `_require_scratch_reflink`
- Line 27: `_require_cp_reflink`
- Line 41: `_pwrite_byte 0x61 0 $((loops * blksz)) $testdir/file1 >> $seqres.full`
- Line 42: `_cp_reflink $testdir/file1 $testdir/file2`
- Line 47: `_pwrite_byte 0x62 0 $((loops * blksz)) $testdir/file1 >> $seqres.full`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

The primary pass signal is the script reaching `status=0` or `exit $status` with no unexpected command failure, filtered output mismatch, or dmesg warning.

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through `_cleanup()`, `rm -rf $tmp.*`. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Block-size congruence, sharing verification, and post-remount checks are critical because unsupported or partially implemented sharing can otherwise look like ordinary copies. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/161 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/162 -->
# sources/test-tools/xfstests/tests/generic/162

## Purpose

This xfstests generic script exercises reflink/CoW, dedupe behavior for the filesystem mounted by the test harness. The test is registered with `_begin_fstest auto quick clone dedupe` and falls into the reflink/CoW, dedupe area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `162` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink` and gates execution with `_require_scratch_dedupe`, `_require_congruent_file_oplen $SCRATCH_MNT $blksz`. Local helpers are `line 48 `overwrite() {``. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 26: `_require_scratch_dedupe`
- Line 44: `_pwrite_byte 0x61 0 $((loops * blksz)) $testdir/file1 >> $seqres.full`
- Line 45: `_pwrite_byte 0x61 0 $((loops * blksz)) $testdir/file2 >> $seqres.full`
- Line 51: `_pwrite_byte 0x61 $((i * blksz)) $blksz $testdir/file2 >> $seqres.full`
- Line 60: `_dedupe_range   $testdir/file1 $((i * blksz)) $testdir/file2 $((i * blksz)) $blksz >> $seqres.full`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

The primary pass signal is the script reaching `status=0` or `exit $status` with no unexpected command failure, filtered output mismatch, or dmesg warning.

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through `_cleanup()`, `rm -rf $tmp.*`. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Block-size congruence, sharing verification, and post-remount checks are critical because unsupported or partially implemented sharing can otherwise look like ordinary copies. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/162 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/163 -->
# sources/test-tools/xfstests/tests/generic/163

## Purpose

This xfstests generic script exercises reflink/CoW, dedupe behavior for the filesystem mounted by the test harness. The test is registered with `_begin_fstest auto quick clone dedupe` and falls into the reflink/CoW, dedupe area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `163` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink` and gates execution with `_require_scratch_dedupe`, `_require_congruent_file_oplen $SCRATCH_MNT $blksz`. Local helpers are `line 48 `overwrite() {``. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 26: `_require_scratch_dedupe`
- Line 44: `_pwrite_byte 0x61 0 $((loops * blksz)) $testdir/file1 >> $seqres.full`
- Line 45: `_pwrite_byte 0x61 0 $((loops * blksz)) $testdir/file2 >> $seqres.full`
- Line 51: `_pwrite_byte 0x61 $((i * blksz)) $blksz $testdir/file1 >> $seqres.full`
- Line 60: `_dedupe_range   $testdir/file1 $((i * blksz)) $testdir/file2 $((i * blksz)) $blksz >> $seqres.full`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

The primary pass signal is the script reaching `status=0` or `exit $status` with no unexpected command failure, filtered output mismatch, or dmesg warning.

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through `_cleanup()`, `rm -rf $tmp.*`. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Block-size congruence, sharing verification, and post-remount checks are critical because unsupported or partially implemented sharing can otherwise look like ordinary copies. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/163 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/164 -->
# sources/test-tools/xfstests/tests/generic/164

## Purpose

target file. The test is registered with `_begin_fstest auto clone` and falls into the reflink/CoW area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `164` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink` and gates execution with `_require_scratch_reflink`, `_require_cp_reflink`, `_require_congruent_file_oplen $SCRATCH_MNT $blksz`. Local helpers are `line 51 `fbytes() {``, `line 55 `reader() {``. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 27: `_require_scratch_reflink`
- Line 28: `_require_cp_reflink`
- Line 46: `_pwrite_byte 0x61 0 $((loops * blksz)) $testdir/file1 >> $seqres.full`
- Line 47: `_pwrite_byte 0x62 0 $((loops * blksz)) $testdir/file2 >> $seqres.full`
- Line 48: `_cp_reflink $testdir/file1 $testdir/file3`
- Line 65: `_reflink_range  $testdir/file1 $((i * blksz)) $testdir/file3 $((i * blksz)) $blksz >> $seqres.full`
- Line 70: `_reflink_range  $testdir/file2 $((i * blksz)) $testdir/file3 $((i * blksz)) $blksz >> $seqres.full`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

The primary pass signal is the script reaching `status=0` or `exit $status` with no unexpected command failure, filtered output mismatch, or dmesg warning.

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through `_cleanup()`, `rm -rf $tmp.*`. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Block-size congruence, sharing verification, and post-remount checks are critical because unsupported or partially implemented sharing can otherwise look like ordinary copies. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/164 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/165 -->
# sources/test-tools/xfstests/tests/generic/165

## Purpose

target file. The test is registered with `_begin_fstest auto clone` and falls into the reflink/CoW, AIO/direct I/O area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `165` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink` and gates execution with `_require_scratch_reflink`, `_require_cp_reflink`, `_require_odirect`, `_require_congruent_file_oplen $SCRATCH_MNT $blksz`. Local helpers are `line 52 `fbytes() {``, `line 56 `reader() {``. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 27: `_require_scratch_reflink`
- Line 28: `_require_cp_reflink`
- Line 47: `_pwrite_byte 0x61 0 $((loops * blksz)) $testdir/file1 >> $seqres.full`
- Line 48: `_pwrite_byte 0x62 0 $((loops * blksz)) $testdir/file2 >> $seqres.full`
- Line 49: `_cp_reflink $testdir/file1 $testdir/file3`
- Line 66: `_reflink_range  $testdir/file1 $((i * blksz)) $testdir/file3 $((i * blksz)) $blksz >> $seqres.full`
- Line 71: `_reflink_range  $testdir/file2 $((i * blksz)) $testdir/file3 $((i * blksz)) $blksz >> $seqres.full`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

The primary pass signal is the script reaching `status=0` or `exit $status` with no unexpected command failure, filtered output mismatch, or dmesg warning.

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through `_cleanup()`, `rm -rf $tmp.*`. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Block-size congruence, sharing verification, and post-remount checks are critical because unsupported or partially implemented sharing can otherwise look like ordinary copies. Timing and alignment make the test susceptible to architecture, page-size, and direct-I/O constraints; dmesg filtering must not hide unrelated warnings. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/165 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/166 -->
# sources/test-tools/xfstests/tests/generic/166

## Purpose

We rate limit the snapshot creator to one snapshot per full file write.  this limits the runtime on slow devices, whilst not substantially reducing the the number of snapshots taken on fast devices. The test is registered with `_begin_fstest auto clone` and falls into the reflink/CoW, AIO/direct I/O, ENOSPC area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `166` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink` and gates execution with `_require_scratch_reflink`, `_require_cp_reflink`, `_require_odirect`. Local helpers are `line 55 `snappy() {``. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 27: `_require_scratch_reflink`
- Line 28: `_require_cp_reflink`
- Line 47: `_pwrite_byte 0x61 0 $((loops * blksz)) $testdir/file1 >> $seqres.full`
- Line 62: `out="$(_cp_reflink $testdir/file1 $testdir/snap_$n 2>&1)"`
- Line 75: `_pwrite_byte 0x63 $((i * blksz)) $blksz -d $testdir/file1 >> $seqres.full`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

The primary pass signal is the script reaching `status=0` or `exit $status` with no unexpected command failure, filtered output mismatch, or dmesg warning.

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through `_cleanup()`, `rm -rf $tmp.*`. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Block-size congruence, sharing verification, and post-remount checks are critical because unsupported or partially implemented sharing can otherwise look like ordinary copies. Timing and alignment make the test susceptible to architecture, page-size, and direct-I/O constraints; dmesg filtering must not hide unrelated warnings. Free-space arithmetic is intentionally tight, so filesystem geometry, reserved blocks, or delayed allocation can change whether ENOSPC appears at the intended point. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/166 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/167 -->
# sources/test-tools/xfstests/tests/generic/167

## Purpose

the source of a reflink operation. The test is registered with `_begin_fstest auto clone` and falls into the reflink/CoW, ENOSPC area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `167` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink` and gates execution with `_require_scratch_reflink`, `_require_cp_reflink`. Local helpers are `line 49 `snappy() {``. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 27: `_require_scratch_reflink`
- Line 28: `_require_cp_reflink`
- Line 45: `_pwrite_byte 0x61 0 $((loops * blksz)) $testdir/file1 >> $seqres.full`
- Line 52: `out="$(_cp_reflink $testdir/file1 $testdir/snap_$n 2>&1)"`
- Line 64: `_pwrite_byte 0x63 $((i * blksz)) $blksz $testdir/file1 >> $seqres.full`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

The primary pass signal is the script reaching `status=0` or `exit $status` with no unexpected command failure, filtered output mismatch, or dmesg warning.

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through `_cleanup()`, `rm -rf $tmp.*`. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Block-size congruence, sharing verification, and post-remount checks are critical because unsupported or partially implemented sharing can otherwise look like ordinary copies. Free-space arithmetic is intentionally tight, so filesystem geometry, reserved blocks, or delayed allocation can change whether ENOSPC appears at the intended point. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/167 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/168 -->
# sources/test-tools/xfstests/tests/generic/168

## Purpose

the target of a reflink operation. The test is registered with `_begin_fstest auto clone` and falls into the reflink/CoW, AIO/direct I/O area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `168` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink` and gates execution with `_require_scratch_reflink`, `_require_congruent_file_oplen $SCRATCH_MNT $blksz`. Local helpers are `line 51 `overwrite() {``. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 28: `_require_scratch_reflink`
- Line 46: `_pwrite_byte 0x61 0 $((loops * blksz)) $testdir/file1 >> $seqres.full`
- Line 47: `_pwrite_byte 0x62 0 $((loops * blksz)) $testdir/file2 >> $seqres.full`
- Line 54: `_pwrite_byte 0x63 $((i * blksz)) $blksz $testdir/file2 >> $seqres.full`
- Line 64: `_reflink_range  $testdir/file1 $((i * blksz)) $testdir/file2 $((i * blksz)) $blksz >> $seqres.full`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

The primary pass signal is the script reaching `status=0` or `exit $status` with no unexpected command failure, filtered output mismatch, or dmesg warning.

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through `_cleanup()`, `rm -rf $tmp.*`. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Block-size congruence, sharing verification, and post-remount checks are critical because unsupported or partially implemented sharing can otherwise look like ordinary copies. Timing and alignment make the test susceptible to architecture, page-size, and direct-I/O constraints; dmesg filtering must not hide unrelated warnings. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/168 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/169 -->
# sources/test-tools/xfstests/tests/generic/169

## Purpose

This xfstests generic script exercises generic filesystem behavior behavior for the filesystem mounted by the test harness. The test is registered with `_begin_fstest rw metadata auto quick` and falls into the generic filesystem behavior area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `169` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter` and gates execution with `_require_scratch`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 36: `$XFS_IO_PROG -a -c "pwrite 0 5k" -c "fsync" -c "pwrite 5k 5k" -c "fsync" -c "pwrite 10k 5k" -c "fsync" -c "stat" $SCRATCH_MNT/testfile | _show_wrote_and_stat_only`
- Line 47: `$XFS_IO_PROG -r -c "stat" $SCRATCH_MNT/testfile | _show_wrote_and_stat_only`
- Line 51: `$XFS_IO_PROG -f -c "pwrite 0 5" -c s -c "pwrite 5 5" -c "stat" $SCRATCH_MNT/nextfile | _show_wrote_and_stat_only`
- Line 60: `$XFS_IO_PROG -r -c "stat" $SCRATCH_MNT/nextfile | _show_wrote_and_stat_only`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

The primary pass signal is the script reaching `status=0` or `exit $status` with no unexpected command failure, filtered output mismatch, or dmesg warning.

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through none declared. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

The main risk is environmental: missing helper binaries, unsupported mount features, or output filtering drift can turn a filesystem regression into a notrun or false failure. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/169 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/170 -->
# sources/test-tools/xfstests/tests/generic/170

## Purpose

the target of a reflink operation. The test is registered with `_begin_fstest auto clone` and falls into the reflink/CoW, AIO/direct I/O area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `170` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink` and gates execution with `_require_scratch_reflink`, `_require_odirect`, `_require_congruent_file_oplen $SCRATCH_MNT $blksz`. Local helpers are `line 52 `overwrite() {``. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 28: `_require_scratch_reflink`
- Line 47: `_pwrite_byte 0x61 0 $((loops * blksz)) $testdir/file1 >> $seqres.full`
- Line 48: `_pwrite_byte 0x62 0 $((loops * blksz)) $testdir/file2 >> $seqres.full`
- Line 55: `_pwrite_byte 0x63 $((i * blksz)) $blksz -d $testdir/file2 >> $seqres.full`
- Line 65: `_reflink_range  $testdir/file1 $((i * blksz)) $testdir/file2 $((i * blksz)) $blksz >> $seqres.full`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

The primary pass signal is the script reaching `status=0` or `exit $status` with no unexpected command failure, filtered output mismatch, or dmesg warning.

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through `_cleanup()`, `rm -rf $tmp.*`. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Block-size congruence, sharing verification, and post-remount checks are critical because unsupported or partially implemented sharing can otherwise look like ordinary copies. Timing and alignment make the test susceptible to architecture, page-size, and direct-I/O constraints; dmesg filtering must not hide unrelated warnings. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/170 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/171 -->
# sources/test-tools/xfstests/tests/generic/171

## Purpose

Reflink a file, use up the rest of the space, then try to observe ENOSPC while copy-on-writing the file via the page cache. The test is registered with `_begin_fstest auto quick clone` and falls into the reflink/CoW, xattr, ENOSPC area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `171` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/populate`, `. ./common/filter`, `. ./common/attr`, `. ./common/reflink` and gates execution with `_require_scratch_reflink`, `_require_cp_reflink`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 26: `_require_scratch_reflink`
- Line 27: `_require_cp_reflink`
- Line 50: `_pwrite_byte 0x61 0 $((blksz * nr_blks)) $testdir/bigfile >> $seqres.full 2>&1`
- Line 51: `_cp_reflink $testdir/bigfile $testdir/clonefile`
- Line 60: `out="$(_pwrite_byte 0x62 0 $((blksz * nr_blks)) $testdir/bigfile 2>&1 | _filter_xfs_io_error)"`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

- Line 55: `nr_free=$(stat -f -c '%f' $testdir)`
- Line 60: `out="$(_pwrite_byte 0x62 0 $((blksz * nr_blks)) $testdir/bigfile 2>&1 | _filter_xfs_io_error)"`

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through `_cleanup()`, `rm -rf $tmp.* $testdir1`. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Block-size congruence, sharing verification, and post-remount checks are critical because unsupported or partially implemented sharing can otherwise look like ordinary copies. The expected output is sensitive to namespace support, user/group setup, mount options, and filtered id/name rendering. Free-space arithmetic is intentionally tight, so filesystem geometry, reserved blocks, or delayed allocation can change whether ENOSPC appears at the intended point. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/171 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/172 -->
# sources/test-tools/xfstests/tests/generic/172

## Purpose

Reflink a file that uses more than half of the space, then try to observe ENOSPC while copy-on-writing the file via the page cache. The test is registered with `_begin_fstest auto quick clone` and falls into the reflink/CoW, xattr, ENOSPC area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `172` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/populate`, `. ./common/filter`, `. ./common/attr`, `. ./common/reflink` and gates execution with `_require_scratch_reflink`, `_require_cp_reflink`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 26: `_require_scratch_reflink`
- Line 27: `_require_cp_reflink`
- Line 48: `_pwrite_byte 0x61 0 $file_size $testdir/bigfile >> $seqres.full 2>&1`
- Line 49: `_cp_reflink $testdir/bigfile $testdir/clonefile`
- Line 57: `out="$(_pwrite_byte 0x62 0 $file_size $testdir/bigfile 2>&1 | _filter_xfs_io_error)"`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

- Line 57: `out="$(_pwrite_byte 0x62 0 $file_size $testdir/bigfile 2>&1 | _filter_xfs_io_error)"`

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through `_cleanup()`, `rm -rf $tmp.* $testdir1`. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Block-size congruence, sharing verification, and post-remount checks are critical because unsupported or partially implemented sharing can otherwise look like ordinary copies. The expected output is sensitive to namespace support, user/group setup, mount options, and filtered id/name rendering. Free-space arithmetic is intentionally tight, so filesystem geometry, reserved blocks, or delayed allocation can change whether ENOSPC appears at the intended point. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/172 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/173 -->
# sources/test-tools/xfstests/tests/generic/173

## Purpose

Reflink a file, use up the rest of the space, then try to observe ENOSPC while copy-on-writing the file via mmap. The test is registered with `_begin_fstest auto quick clone mmap` and falls into the reflink/CoW, xattr, mmap, ENOSPC area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `173` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/populate`, `. ./common/filter`, `. ./common/attr`, `. ./common/reflink` and gates execution with `_require_scratch_reflink`, `_require_cp_reflink`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 11: `_begin_fstest auto quick clone mmap`
- Line 26: `_require_scratch_reflink`
- Line 27: `_require_cp_reflink`
- Line 50: `_pwrite_byte 0x61 0 $((blksz * nr_blks)) $testdir/bigfile >> $seqres.full 2>&1`
- Line 51: `_cp_reflink $testdir/bigfile $testdir/clonefile`
- Line 59: `echo "mmap CoW the big file"`
- Line 65: `echo "mmap CoW should have failed with SIGBUS, got SIG$(kill -l $err)"`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

- Line 55: `nr_free=$(stat -f -c '%f' $testdir)`

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through `_cleanup()`, `rm -rf $tmp.* $testdir1`. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Block-size congruence, sharing verification, and post-remount checks are critical because unsupported or partially implemented sharing can otherwise look like ordinary copies. The expected output is sensitive to namespace support, user/group setup, mount options, and filtered id/name rendering. Timing and alignment make the test susceptible to architecture, page-size, and direct-I/O constraints; dmesg filtering must not hide unrelated warnings. Free-space arithmetic is intentionally tight, so filesystem geometry, reserved blocks, or delayed allocation can change whether ENOSPC appears at the intended point. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/173 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/174 -->
# sources/test-tools/xfstests/tests/generic/174

## Purpose

Reflink a file, use up the rest of the space, then try to observe ENOSPC while copy-on-writing the file via direct-io. The test is registered with `_begin_fstest auto quick clone` and falls into the reflink/CoW, xattr, AIO/direct I/O, ENOSPC area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `174` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/populate`, `. ./common/filter`, `. ./common/attr`, `. ./common/reflink` and gates execution with `_require_scratch_reflink`, `_require_cp_reflink`, `_require_odirect`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 26: `_require_scratch_reflink`
- Line 27: `_require_cp_reflink`
- Line 51: `_pwrite_byte 0x61 0 $((blksz * nr_blks)) $testdir/bigfile >> $seqres.full 2>&1`
- Line 52: `_cp_reflink $testdir/bigfile $testdir/clonefile`
- Line 61: `out="$(_pwrite_byte 0x62 0 $((blksz * nr_blks)) $testdir/bigfile -d 2>&1 | _filter_xfs_io_error)"`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

- Line 56: `nr_free=$(stat -f -c '%f' $testdir)`
- Line 61: `out="$(_pwrite_byte 0x62 0 $((blksz * nr_blks)) $testdir/bigfile -d 2>&1 | _filter_xfs_io_error)"`

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through `_cleanup()`, `rm -rf $tmp.* $testdir1`. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Block-size congruence, sharing verification, and post-remount checks are critical because unsupported or partially implemented sharing can otherwise look like ordinary copies. The expected output is sensitive to namespace support, user/group setup, mount options, and filtered id/name rendering. Timing and alignment make the test susceptible to architecture, page-size, and direct-I/O constraints; dmesg filtering must not hide unrelated warnings. Free-space arithmetic is intentionally tight, so filesystem geometry, reserved blocks, or delayed allocation can change whether ENOSPC appears at the intended point. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/174 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/175 -->
# sources/test-tools/xfstests/tests/generic/175

## Purpose

See how well reflink handles reflinking the same block a million times. The test is registered with `_begin_fstest auto clone` and falls into the reflink/CoW, xattr area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `175` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`, `. ./common/reflink` and gates execution with `_require_scratch_reflink`, `_require_cp_reflink`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 17: `_require_scratch_reflink`
- Line 18: `_require_cp_reflink`
- Line 31: `_pwrite_byte 0x61 0 $blksz "$testdir/file1" >> "$seqres.full"`
- Line 38: `_reflink_range "$testdir/file1" 0 "$testdir/file1" $n $n >> "$seqres.full"`
- Line 46: `_reflink_range "$testdir/file1" 0 "$testdir/file2" 0 $bytes >> "$seqres.full"`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

The primary pass signal is the script reaching `status=0` or `exit $status` with no unexpected command failure, filtered output mismatch, or dmesg warning.

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through none declared. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Block-size congruence, sharing verification, and post-remount checks are critical because unsupported or partially implemented sharing can otherwise look like ordinary copies. The expected output is sensitive to namespace support, user/group setup, mount options, and filtered id/name rendering. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/175 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/176 -->
# sources/test-tools/xfstests/tests/generic/176

## Purpose

Setup for one million blocks, but we'll accept stress testing down to 2^17 blocks... that should be plenty for anyone. The test is registered with `_begin_fstest auto clone punch` and falls into the reflink/CoW, xattr, hole punching area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `176` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`, `. ./common/reflink` and gates execution with `_require_scratch_reflink`, `_require_cp_reflink`, `_require_xfs_io_command "fpunch"`, `_require_test_program "punch-alternating"`. Local helpers are `line 37 `calc_space() {``. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 17: `_require_scratch_reflink`
- Line 18: `_require_cp_reflink`
- Line 19: `_require_xfs_io_command "fpunch"`
- Line 50: `$XFS_IO_PROG -f -c "pwrite -S 0x61 -b 4194304 0 $((2 ** (fnr + 1) * blksz))" "$testdir/file1" >> "$seqres.full"`
- Line 59: `_reflink_range "$testdir/file1" 0 "$testdir/file2" 0 $bytes >> "$seqres.full"`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

- Line 34: `free_blocks=$(stat -f -c '%a' "$testdir")`

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through none declared. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Block-size congruence, sharing verification, and post-remount checks are critical because unsupported or partially implemented sharing can otherwise look like ordinary copies. The expected output is sensitive to namespace support, user/group setup, mount options, and filtered id/name rendering. Range operations have off-by-one and block-boundary risk; the test relies on xfs_io command support and stable filtering of sparse/unwritten output. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/176 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/177 -->
# sources/test-tools/xfstests/tests/generic/177

## Purpose

Create out test file with some data and then fsync it. We do the fsync only to make sure the last fsync we do in this test triggers the fast code path of btrfs' fsync implementation, a condition necessary to trigger the bug btrfs had. The test is registered with `_begin_fstest auto quick prealloc metadata punch log fiemap` and falls into the journal/power-failure replay, preallocation/unwritten extent, hole punching area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `177` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter`, `. ./common/punch`, `. ./common/dmflakey` and gates execution with `_require_scratch`, `_require_xfs_io_command "fpunch"`, `_require_xfs_io_command "fiemap"`, `_require_dm_target flakey`, `_require_metadata_journaling $SCRATCH_DEV`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 30: `_require_xfs_io_command "fpunch"`
- Line 45: `$XFS_IO_PROG -f -c "pwrite -S 0xaa 0K $(($BLOCK_SIZE * 32))" -c "fsync" $SCRATCH_MNT/foobar | _filter_xfs_io_blocks_modified`
- Line 50: `$XFS_IO_PROG -c "fpunch $(($BLOCK_SIZE * 24)) $(($BLOCK_SIZE * 8))" $SCRATCH_MNT/foobar`
- Line 54: `$XFS_IO_PROG -c "fpunch $(($BLOCK_SIZE * 16)) $(($BLOCK_SIZE * 32))" $SCRATCH_MNT/foobar`
- Line 58: `$XFS_IO_PROG -c "fpunch $(($BLOCK_SIZE * 8)) $(($BLOCK_SIZE * 24))" $SCRATCH_MNT/foobar`
- Line 62: `$XFS_IO_PROG -c "fsync" $SCRATCH_MNT/foobar`
- Line 68: `$XFS_IO_PROG -c "fiemap -v" $SCRATCH_MNT/foobar | _filter_fiemap $BLOCK_SIZE`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

- Line 45: `$XFS_IO_PROG -f -c "pwrite -S 0xaa 0K $(($BLOCK_SIZE * 32))" -c "fsync" $SCRATCH_MNT/foobar | _filter_xfs_io_blocks_modified`
- Line 68: `$XFS_IO_PROG -c "fiemap -v" $SCRATCH_MNT/foobar | _filter_fiemap $BLOCK_SIZE`

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through `_cleanup()`, `_cleanup_flakey`, `rm -f $tmp.*`. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

The simulated crash path depends on dm-flakey teardown/remount ordering; a cleanup or remount failure can mask the metadata replay condition being tested. Range operations have off-by-one and block-boundary risk; the test relies on xfs_io command support and stable filtering of sparse/unwritten output. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/177 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/178 -->
# sources/test-tools/xfstests/tests/generic/178

## Purpose

Ensure that punch-hole doesn't clobber CoW. The test is registered with `_begin_fstest auto quick clone punch` and falls into the reflink/CoW, hole punching area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `178` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink` and gates execution with `_require_test_reflink`, `_require_cp_reflink`, `_require_xfs_io_command "fpunch"`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 23: `_require_test_reflink`
- Line 24: `_require_cp_reflink`
- Line 25: `_require_xfs_io_command "fpunch"`
- Line 35: `_pwrite_byte 0x61 0 $filesize $testdir/file1 >> $seqres.full`
- Line 37: `_cp_reflink $testdir/file1 $testdir/file2`
- Line 44: `_pwrite_byte 0x62 0 $((blksz * 256)) $testdir/file2 >> $seqres.full`
- Line 45: `$XFS_IO_PROG -f -c "fpunch $blksz $((blksz * 254))" $testdir/file2`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

- Line 40: `md5sum $testdir/file1 | _filter_test_dir`
- Line 41: `md5sum $testdir/file2 | _filter_test_dir`

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through `_cleanup()`, `rm -rf $tmp.* $testdir`. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Block-size congruence, sharing verification, and post-remount checks are critical because unsupported or partially implemented sharing can otherwise look like ordinary copies. Range operations have off-by-one and block-boundary risk; the test relies on xfs_io command support and stable filtering of sparse/unwritten output. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/178 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/179 -->
# sources/test-tools/xfstests/tests/generic/179

## Purpose

Ensure that unaligned punch-hole steps around reflinked ranges: - Create a reflink clone of a file - Perform an unaligned punch in the middle of the file. - Check that the reflinked areas are still there. The test is registered with `_begin_fstest auto quick clone punch` and falls into the reflink/CoW, hole punching area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `179` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink` and gates execution with `_require_test_reflink`, `_require_cp_reflink`, `_require_xfs_io_command "fpunch"`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 26: `_require_test_reflink`
- Line 27: `_require_cp_reflink`
- Line 28: `_require_xfs_io_command "fpunch"`
- Line 36: `_pwrite_byte 0x61 0 $((blksz * 3)) $testdir/file1 >> $seqres.full`
- Line 38: `_cp_reflink $testdir/file1 $testdir/file2`
- Line 40: `_pwrite_byte 0x61 0 $((blksz * 3)) $testdir/file2.chk >> $seqres.full`
- Line 41: `_pwrite_byte 0x00 $((blksz - 17)) $((blksz + 17)) $testdir/file2.chk >> $seqres.full`
- Line 53: `echo "fpunch files"`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

- Line 44: `md5sum $testdir/file1 | _filter_test_dir`
- Line 45: `md5sum $testdir/file2 | _filter_test_dir`
- Line 46: `md5sum $testdir/file2.chk | _filter_test_dir`
- Line 68: `cmp -s $testdir/file2 $testdir/file2.chk || echo "file2 and file2.chk do not match"`

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through `_cleanup()`, `rm -rf $tmp.* $testdir`. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Block-size congruence, sharing verification, and post-remount checks are critical because unsupported or partially implemented sharing can otherwise look like ordinary copies. Range operations have off-by-one and block-boundary risk; the test relies on xfs_io command support and stable filtering of sparse/unwritten output. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/179 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/180 -->
# sources/test-tools/xfstests/tests/generic/180

## Purpose

Ensure that unaligned zero-range steps around reflinked ranges: - Create a reflink clone of a file - Perform an unaligned zero-range in the middle of the file. - Check that the reflinked areas are still there. The test is registered with `_begin_fstest auto quick clone zero` and falls into the reflink/CoW, zero range area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `180` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink` and gates execution with `_require_test_reflink`, `_require_cp_reflink`, `_require_xfs_io_command "fzero"`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 26: `_require_test_reflink`
- Line 27: `_require_cp_reflink`
- Line 28: `_require_xfs_io_command "fzero"`
- Line 36: `_pwrite_byte 0x61 0 $((blksz * 3)) $testdir/file1 >> $seqres.full`
- Line 38: `_cp_reflink $testdir/file1 $testdir/file2`
- Line 40: `_pwrite_byte 0x61 0 $((blksz * 3)) $testdir/file2.chk >> $seqres.full`
- Line 41: `_pwrite_byte 0x00 $((blksz - 17)) $((blksz + 17)) $testdir/file2.chk >> $seqres.full`
- Line 53: `echo "fzero files"`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

- Line 44: `md5sum $testdir/file1 | _filter_test_dir`
- Line 45: `md5sum $testdir/file2 | _filter_test_dir`
- Line 46: `md5sum $testdir/file2.chk | _filter_test_dir`
- Line 68: `cmp -s $testdir/file2 $testdir/file2.chk || echo "file2 and file2.chk do not match"`

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through `_cleanup()`, `rm -rf $tmp.* $testdir`. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Block-size congruence, sharing verification, and post-remount checks are critical because unsupported or partially implemented sharing can otherwise look like ordinary copies. Range operations have off-by-one and block-boundary risk; the test relies on xfs_io command support and stable filtering of sparse/unwritten output. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/180 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/181 -->
# sources/test-tools/xfstests/tests/generic/181

## Purpose

- Create a file. - Try to reflink "zero" bytes. - Check that the reflink happened. The test is registered with `_begin_fstest auto quick clone` and falls into the reflink/CoW area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `181` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink` and gates execution with `_require_test_reflink`, `_require_cp_reflink`, `_require_congruent_file_oplen $TEST_DIR $blksz`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 26: `_require_test_reflink`
- Line 27: `_require_cp_reflink`
- Line 36: `_pwrite_byte 0x61 0 $((blksz * 256)) $testdir/file1 >> $seqres.full`
- Line 37: `_pwrite_byte 0x62 0 $((blksz * 256)) $testdir/file2 >> $seqres.full`
- Line 38: `_pwrite_byte 0x62 0 $((blksz * 2)) $testdir/file2.chk >> $seqres.full`
- Line 39: `_pwrite_byte 0x61 $((blksz * 2)) $((blksz * 255)) $testdir/file2.chk >> $seqres.full`
- Line 40: `_reflink_range $testdir/file1 $blksz $testdir/file2 $((blksz * 2)) 0 >> $seqres.full`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

- Line 43: `md5sum $testdir/file1 | _filter_test_dir`
- Line 44: `md5sum $testdir/file2 | _filter_test_dir`
- Line 45: `md5sum $testdir/file2.chk | _filter_test_dir`
- Line 53: `cmp -s $testdir/file2 $testdir/file2.chk || echo "file2 and file2.chk do not match"`

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through `_cleanup()`, `rm -rf $tmp.* $testdir`. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Block-size congruence, sharing verification, and post-remount checks are critical because unsupported or partially implemented sharing can otherwise look like ordinary copies. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/181 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/182 -->
# sources/test-tools/xfstests/tests/generic/182

## Purpose

- Create a file. - Try to dedupe "zero" bytes. - Check that the dedupe happened and nothing changed. The test is registered with `_begin_fstest auto quick clone dedupe` and falls into the reflink/CoW, dedupe area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `182` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink` and gates execution with `_require_test_dedupe`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 26: `_require_test_dedupe`
- Line 34: `_pwrite_byte 0x61 0 $((blksz * 256)) $testdir/file1 >> $seqres.full`
- Line 35: `_pwrite_byte 0x62 0 $((blksz * 257)) $testdir/file2 >> $seqres.full`
- Line 36: `_pwrite_byte 0x62 0 $((blksz * 257)) $testdir/file2.chk >> $seqres.full`
- Line 37: `_dedupe_range $testdir/file1 $blksz $testdir/file2 $((blksz * 2)) 0 >> $seqres.full`
- Line 54: `_pwrite_byte 0x61 0 $((blksz * 256)) $testdir/file2 >> $seqres.full`
- Line 55: `_pwrite_byte 0x61 0 $((blksz * 256)) $testdir/file2.chk >> $seqres.full`
- Line 73: `_pwrite_byte 0x61 0 $((blksz * 257)) $testdir/file2 >> $seqres.full`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

- Line 40: `md5sum $testdir/file1 | _filter_test_dir`
- Line 41: `md5sum $testdir/file2 | _filter_test_dir`
- Line 42: `md5sum $testdir/file2.chk | _filter_test_dir`
- Line 50: `cmp -s $testdir/file2 $testdir/file2.chk || echo "file2 and file2.chk do not match"`

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through `_cleanup()`, `rm -rf $tmp.* $testdir`. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Block-size congruence, sharing verification, and post-remount checks are critical because unsupported or partially implemented sharing can otherwise look like ordinary copies. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/182 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/183 -->
# sources/test-tools/xfstests/tests/generic/183

## Purpose

Ensuring that copy on write in direct-io mode works when the CoW range originally covers multiple extents. - Create two files - Reflink the odd blocks of the first file into a third file. - Reflink the even blocks of the second file into the third file. - directio CoW across the halfway mark. - Check that the files are now different where we say they're different. The test is registered with `_begin_fstest auto quick clone` and falls into the reflink/CoW, AIO/direct I/O area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `183` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink` and gates execution with `_require_scratch_reflink`, `_require_odirect`, `_require_congruent_file_oplen $SCRATCH_MNT $blksz`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 29: `_require_scratch_reflink`
- Line 44: `_pwrite_byte 0x61 0 $filesize $testdir/file1 >> $seqres.full`
- Line 45: `_pwrite_byte 0x62 0 $filesize $testdir/file2 >> $seqres.full`
- Line 47: `_reflink_range $testdir/file1 $((blksz * f)) $testdir/file3 $((blksz * f)) $blksz >> $seqres.full`
- Line 48: `_pwrite_byte 0x61 $((blksz * f)) $blksz $testdir/file3.chk >> $seqres.full`
- Line 51: `_reflink_range $testdir/file2 $((blksz * f)) $testdir/file3 $((blksz * f)) $blksz >> $seqres.full`
- Line 52: `_pwrite_byte 0x62 $((blksz * f)) $blksz $testdir/file3.chk >> $seqres.full`
- Line 65: `$XFS_IO_PROG -d -f -c "pwrite -S 0x63 -b $cowsz $cowoff $cowsz" $testdir/file3 >> $seqres.full`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

- Line 57: `md5sum $testdir/file1 | _filter_scratch`
- Line 58: `md5sum $testdir/file2 | _filter_scratch`
- Line 59: `md5sum $testdir/file3 | _filter_scratch`
- Line 60: `md5sum $testdir/file3.chk | _filter_scratch`

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through `_cleanup()`, `rm -rf $tmp.* $testdir`. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Block-size congruence, sharing verification, and post-remount checks are critical because unsupported or partially implemented sharing can otherwise look like ordinary copies. Timing and alignment make the test susceptible to architecture, page-size, and direct-I/O constraints; dmesg filtering must not hide unrelated warnings. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/183 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/184 -->
# sources/test-tools/xfstests/tests/generic/184

## Purpose

check mknod makes working nodes. The test is registered with `_begin_fstest metadata auto quick` and falls into the permission area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `184` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter` and gates execution with `_require_test`, `_require_mknod`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 20: `chmod 666 $TEST_DIR/null`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

The primary pass signal is the script reaching `status=0` or `exit $status` with no unexpected command failure, filtered output mismatch, or dmesg warning.

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through none declared. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

The expected output is sensitive to namespace support, user/group setup, mount options, and filtered id/name rendering. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=$?; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/184 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/185 -->
# sources/test-tools/xfstests/tests/generic/185

## Purpose

Ensuring that copy on write in buffered mode works when the CoW range originally covers multiple extents. - Create two files - Reflink the odd blocks of the first file into a third file. - Reflink the even blocks of the second file into the third file. - CoW across the halfway mark. - Check that the files are now different where we say they're different. The test is registered with `_begin_fstest auto quick clone` and falls into the reflink/CoW area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `185` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink` and gates execution with `_require_scratch_reflink`, `_require_congruent_file_oplen $SCRATCH_MNT $blksz`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 29: `_require_scratch_reflink`
- Line 43: `_pwrite_byte 0x61 0 $filesize $testdir/file1 >> $seqres.full`
- Line 44: `_pwrite_byte 0x62 0 $filesize $testdir/file2 >> $seqres.full`
- Line 46: `_reflink_range $testdir/file1 $((blksz * f)) $testdir/file3 $((blksz * f)) $blksz >> $seqres.full`
- Line 47: `_pwrite_byte 0x61 $((blksz * f)) $blksz $testdir/file3.chk >> $seqres.full`
- Line 50: `_reflink_range $testdir/file2 $((blksz * f)) $testdir/file3 $((blksz * f)) $blksz >> $seqres.full`
- Line 51: `_pwrite_byte 0x62 $((blksz * f)) $blksz $testdir/file3.chk >> $seqres.full`
- Line 64: `_pwrite_byte 0x63 $cowoff $cowsz $testdir/file3 >> $seqres.full`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

- Line 56: `md5sum $testdir/file1 | _filter_scratch`
- Line 57: `md5sum $testdir/file2 | _filter_scratch`
- Line 58: `md5sum $testdir/file3 | _filter_scratch`
- Line 59: `md5sum $testdir/file3.chk | _filter_scratch`

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through `_cleanup()`, `rm -rf $tmp.* $testdir`. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Block-size congruence, sharing verification, and post-remount checks are critical because unsupported or partially implemented sharing can otherwise look like ordinary copies. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/185 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/186 -->
# sources/test-tools/xfstests/tests/generic/186

## Purpose

Ensuring that copy on write in buffered mode works when free space is heavily fragmented. - Create two files - Reflink the odd blocks of the first file into a third file. - Reflink the even blocks of the second file into the third file. - Try to fragment the free space by allocating a huge file and punching out every other block. - CoW across the halfway mark. - Check that the files are now different where we say they're different. The test is registered with `_begin_fstest auto clone punch prealloc` and falls into the reflink/CoW, preallocation/unwritten extent, hole punching, truncate area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `186` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink` and gates execution with `_require_scratch_reflink`, `_require_cp_reflink`, `_require_xfs_io_command "falloc"`, `_require_xfs_io_command "fpunch"`, `_require_congruent_file_oplen $SCRATCH_MNT $blksz`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 31: `_require_scratch_reflink`
- Line 32: `_require_cp_reflink`
- Line 33: `_require_xfs_io_command "falloc"`
- Line 34: `_require_xfs_io_command "fpunch"`
- Line 45: `$XFS_IO_PROG -fc "truncate $filesize" $file`
- Line 51: `$XFS_IO_PROG -fc "falloc -k $(( (f - 1) * chunksizemb))m ${chunksizemb}m" $file`
- Line 62: `$XFS_IO_PROG -fc "falloc -k 0 ${filesizemb}m" $file`
- Line 66: `$XFS_IO_PROG -fc "pwrite -S 0x65 0 $avail" ${file}`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

- Line 102: `md5sum $testdir/file1 | _filter_scratch`
- Line 103: `md5sum $testdir/file2 | _filter_scratch`
- Line 104: `md5sum $testdir/file3 | _filter_scratch`
- Line 105: `md5sum $testdir/file3.chk | _filter_scratch`

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through `_cleanup()`. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Block-size congruence, sharing verification, and post-remount checks are critical because unsupported or partially implemented sharing can otherwise look like ordinary copies. Range operations have off-by-one and block-boundary risk; the test relies on xfs_io command support and stable filtering of sparse/unwritten output. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/186 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/187 -->
# sources/test-tools/xfstests/tests/generic/187

## Purpose

Ensuring that copy on write in directio mode works when free space is heavily fragmented. - Create two files - Reflink the odd blocks of the first file into a third file. - Reflink the even blocks of the second file into the third file. - Try to fragment the free space by allocating a huge file and punching out every other block. - CoW across the halfway mark. - Check that the files are now different where we say they're different. The test is registered with `_begin_fstest auto clone punch prealloc` and falls into the reflink/CoW, AIO/direct I/O, preallocation/unwritten extent, hole punching, truncate area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `187` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink` and gates execution with `_require_scratch_reflink`, `_require_cp_reflink`, `_require_xfs_io_command "falloc"`, `_require_xfs_io_command "fpunch"`, `_require_odirect`, `_require_congruent_file_oplen $SCRATCH_MNT $blksz`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 37: `_require_scratch_reflink`
- Line 38: `_require_cp_reflink`
- Line 39: `_require_xfs_io_command "falloc"`
- Line 40: `_require_xfs_io_command "fpunch"`
- Line 51: `$XFS_IO_PROG -fc "truncate $filesize" $file`
- Line 57: `$XFS_IO_PROG -fc "falloc -k $(( (f - 1) * chunksizemb))m ${chunksizemb}m" $file`
- Line 68: `$XFS_IO_PROG -fc "falloc -k 0 ${filesizemb}m" $file`
- Line 72: `$XFS_IO_PROG -fc "pwrite -S 0x65 0 $avail" ${file}`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

- Line 108: `md5sum $testdir/file1 | _filter_scratch`
- Line 109: `md5sum $testdir/file2 | _filter_scratch`
- Line 110: `md5sum $testdir/file3 | _filter_scratch`
- Line 111: `md5sum $testdir/file3.chk | _filter_scratch`

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through `_cleanup()`. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Block-size congruence, sharing verification, and post-remount checks are critical because unsupported or partially implemented sharing can otherwise look like ordinary copies. Timing and alignment make the test susceptible to architecture, page-size, and direct-I/O constraints; dmesg filtering must not hide unrelated warnings. Range operations have off-by-one and block-boundary risk; the test relies on xfs_io command support and stable filtering of sparse/unwritten output. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/187 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/188 -->
# sources/test-tools/xfstests/tests/generic/188

## Purpose

Ensuring that copy on write in direct-io mode works when the CoW range originally covers multiple extents, some unwritten, some not. - Create a file and fallocate a second file. - Reflink the odd blocks of the first file into the second file. - directio CoW across the halfway mark, starting with the unwritten extent. - Check that the files are now different where we say they're different. The test is registered with `_begin_fstest auto quick clone prealloc` and falls into the reflink/CoW, AIO/direct I/O, preallocation/unwritten extent area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `188` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink` and gates execution with `_require_scratch_reflink`, `_require_xfs_io_command "falloc"`, `_require_odirect`, `_require_congruent_file_oplen $SCRATCH_MNT $blksz`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 28: `_require_scratch_reflink`
- Line 29: `_require_xfs_io_command "falloc"`
- Line 44: `_weave_reflink_unwritten $blksz $nr $testdir/file1 $testdir/file3 >> $seqres.full`
- Line 55: `$XFS_IO_PROG -d -f -c "pwrite -S 0x63 -b $cowsz $cowoff $cowsz" $testdir/file3 >> $seqres.full`
- Line 56: `_pwrite_byte 0x63 $cowoff $cowsz $testdir/file3.chk >> $seqres.full`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

- Line 48: `md5sum $testdir/file1 | _filter_scratch`
- Line 49: `md5sum $testdir/file3 | _filter_scratch`
- Line 50: `md5sum $testdir/file3.chk | _filter_scratch`

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through `_cleanup()`, `rm -rf $tmp.* $testdir`. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Block-size congruence, sharing verification, and post-remount checks are critical because unsupported or partially implemented sharing can otherwise look like ordinary copies. Timing and alignment make the test susceptible to architecture, page-size, and direct-I/O constraints; dmesg filtering must not hide unrelated warnings. Range operations have off-by-one and block-boundary risk; the test relies on xfs_io command support and stable filtering of sparse/unwritten output. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/188 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/189 -->
# sources/test-tools/xfstests/tests/generic/189

## Purpose

Ensuring that copy on write in buffered mode works when the CoW range originally covers multiple extents, some unwritten, some not. - Create a file and fallocate a second file. - Reflink the odd blocks of the first file into the second file. - CoW across the halfway mark, starting with the unwritten extent. - Check that the files are now different where we say they're different. The test is registered with `_begin_fstest auto quick clone prealloc` and falls into the reflink/CoW, preallocation/unwritten extent area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `189` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink` and gates execution with `_require_scratch_reflink`, `_require_xfs_io_command "falloc"`, `_require_congruent_file_oplen $SCRATCH_MNT $blksz`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 28: `_require_scratch_reflink`
- Line 29: `_require_xfs_io_command "falloc"`
- Line 43: `_weave_reflink_unwritten $blksz $nr $testdir/file1 $testdir/file3 >> $seqres.full`
- Line 54: `$XFS_IO_PROG -f -c "pwrite -S 0x63 -b $cowsz $cowoff $cowsz" $testdir/file3 >> $seqres.full`
- Line 55: `_pwrite_byte 0x63 $cowoff $cowsz $testdir/file3.chk >> $seqres.full`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

- Line 47: `md5sum $testdir/file1 | _filter_scratch`
- Line 48: `md5sum $testdir/file3 | _filter_scratch`
- Line 49: `md5sum $testdir/file3.chk | _filter_scratch`

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through `_cleanup()`, `rm -rf $tmp.* $testdir`. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Block-size congruence, sharing verification, and post-remount checks are critical because unsupported or partially implemented sharing can otherwise look like ordinary copies. Range operations have off-by-one and block-boundary risk; the test relies on xfs_io command support and stable filtering of sparse/unwritten output. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/189 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/190 -->
# sources/test-tools/xfstests/tests/generic/190

## Purpose

Ensuring that copy on write in direct-io mode works when the CoW range originally covers multiple extents, some holes, some not. - Create a file and truncate a second file. - Reflink the odd blocks of the first file into the second file. - directio CoW across the halfway mark, starting with the unwritten extent. - Check that the files are now different where we say they're different. The test is registered with `_begin_fstest auto quick clone prealloc` and falls into the reflink/CoW, AIO/direct I/O, preallocation/unwritten extent, truncate area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `190` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink` and gates execution with `_require_scratch_reflink`, `_require_xfs_io_command "falloc"`, `_require_odirect`, `_require_congruent_file_oplen $SCRATCH_MNT $blksz`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 28: `_require_scratch_reflink`
- Line 29: `_require_xfs_io_command "falloc"`
- Line 44: `_weave_reflink_holes $blksz $nr $testdir/file1 $testdir/file3 >> $seqres.full`
- Line 55: `$XFS_IO_PROG -d -f -c "pwrite -S 0x63 -b $cowsz $cowoff $cowsz" $testdir/file3 >> $seqres.full`
- Line 56: `_pwrite_byte 0x63 $cowoff $cowsz $testdir/file3.chk >> $seqres.full`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

- Line 48: `md5sum $testdir/file1 | _filter_scratch`
- Line 49: `md5sum $testdir/file3 | _filter_scratch`
- Line 50: `md5sum $testdir/file3.chk | _filter_scratch`

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through `_cleanup()`, `rm -rf $tmp.* $testdir`. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Block-size congruence, sharing verification, and post-remount checks are critical because unsupported or partially implemented sharing can otherwise look like ordinary copies. Timing and alignment make the test susceptible to architecture, page-size, and direct-I/O constraints; dmesg filtering must not hide unrelated warnings. Range operations have off-by-one and block-boundary risk; the test relies on xfs_io command support and stable filtering of sparse/unwritten output. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/190 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/191 -->
# sources/test-tools/xfstests/tests/generic/191

## Purpose

Ensuring that copy on write in buffered mode works when the CoW range originally covers multiple extents, some holes, some not. - Create a file and truncate a second file. - Reflink the odd blocks of the first file into the second file. - CoW across the halfway mark, starting with the unwritten extent. - Check that the files are now different where we say they're different. The test is registered with `_begin_fstest auto quick clone prealloc` and falls into the reflink/CoW, preallocation/unwritten extent, truncate area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `191` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink` and gates execution with `_require_scratch_reflink`, `_require_xfs_io_command "falloc"`, `_require_congruent_file_oplen $SCRATCH_MNT $blksz`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 28: `_require_scratch_reflink`
- Line 29: `_require_xfs_io_command "falloc"`
- Line 43: `_weave_reflink_holes $blksz $nr $testdir/file1 $testdir/file3 >> $seqres.full`
- Line 54: `$XFS_IO_PROG -f -c "pwrite -S 0x63 -b $cowsz $cowoff $cowsz" $testdir/file3 >> $seqres.full`
- Line 55: `_pwrite_byte 0x63 $cowoff $cowsz $testdir/file3.chk >> $seqres.full`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

- Line 47: `md5sum $testdir/file1 | _filter_scratch`
- Line 48: `md5sum $testdir/file3 | _filter_scratch`
- Line 49: `md5sum $testdir/file3.chk | _filter_scratch`

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through `_cleanup()`, `rm -rf $tmp.* $testdir`. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Block-size congruence, sharing verification, and post-remount checks are critical because unsupported or partially implemented sharing can otherwise look like ordinary copies. Range operations have off-by-one and block-boundary risk; the test relies on xfs_io command support and stable filtering of sparse/unwritten output. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/191 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/192 -->
# sources/test-tools/xfstests/tests/generic/192

## Purpose

Preload every binary used between sampling time1 and time2 so that loading them has minimal overhead even if the root fs is hosted over a slow network. Also don't put pipe and tee creation in that critical section. The test is registered with `_begin_fstest atime auto` and falls into the timestamp area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `192` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter` and gates execution with `_require_test`, `_require_atime`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 16: `stat -c %X $1`
- Line 28: `rm -f $testfile`
- Line 48: `_test_cycle_mount`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

- Line 16: `stat -c %X $1`

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through none declared. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Timestamp resolution and mount options can make the signal weak unless the test accounts for atime/mtime/ctime granularity. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/192 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/193 -->
# sources/test-tools/xfstests/tests/generic/193

## Purpose

For some tests we need a secondary group for the qa_user.  Currently that's not available in the framework, so the tests using it are commented out. The test is registered with `_begin_fstest metadata auto quick perms` and falls into the xattr, permission, truncate area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `193` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter` and gates execution with `_require_test`, `_require_user`, `_require_chown`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 29: `chown ${qa_user}:${qa_user} $test_user`
- Line 52: `_require_chown`
- Line 71: `echo "user: chown root owned file to qa_user (should fail)"`
- Line 72: `_su ${qa_user} -c "chown ${qa_user} $test_root" 2>&1 | _filter_files`
- Line 74: `echo "user: chown root owned file to root (should fail)"`
- Line 75: `_su ${qa_user} -c "chown root $test_root" 2>&1 | _filter_files`
- Line 77: `echo "user: chown qa_user owned file to qa_user (should succeed)"`
- Line 78: `_su ${qa_user} -c "chown ${qa_user} $test_user"`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

- Line 72: `_su ${qa_user} -c "chown ${qa_user} $test_root" 2>&1 | _filter_files`
- Line 75: `_su ${qa_user} -c "chown root $test_root" 2>&1 | _filter_files`
- Line 82: `_su ${qa_user} -c "chown root $test_user" 2>&1 | _filter_files`
- Line 125: `_su ${qa_user} -c "chmod a+r $test_root" 2>&1 | _filter_files`
- Line 147: `stat -c '%A' $test_user`
- Line 186: `echo -n "before: "; stat -c '%A' $test_user`

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through `_cleanup_files()`, `_cleanup_files`. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

The expected output is sensitive to namespace support, user/group setup, mount options, and filtered id/name rendering. Range operations have off-by-one and block-boundary risk; the test relies on xfs_io command support and stable filtering of sparse/unwritten output. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/193 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/194 -->
# sources/test-tools/xfstests/tests/generic/194

## Purpose

Ensuring that copy on write in direct-io mode works when the CoW range originally covers multiple extents, some delalloc, some not. - Create a file. - Reflink the odd blocks of the first file into the second file. - Buffered write the even blocks of the second file. - directio CoW across the halfway mark, starting with the unwritten extent. - Check that the files are now different where we say they're different. The test is registered with `_begin_fstest auto quick clone prealloc` and falls into the reflink/CoW, AIO/direct I/O, preallocation/unwritten extent area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `194` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink` and gates execution with `_require_scratch_reflink`, `_require_scratch_delalloc`, `_require_xfs_io_command "falloc"`, `_require_odirect`, `_require_congruent_file_oplen $SCRATCH_MNT $blksz`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 29: `_require_scratch_reflink`
- Line 31: `_require_xfs_io_command "falloc"`
- Line 46: `_weave_reflink_holes $blksz $nr $testdir/file1 $testdir/file3 >> $seqres.full`
- Line 57: `_weave_reflink_holes_delalloc $blksz $nr $testdir/file3 >> $seqres.full`
- Line 58: `$XFS_IO_PROG -d -f -c "pwrite -S 0x63 -b $cowsz $cowoff $cowsz" $testdir/file3 >> $seqres.full`
- Line 59: `_pwrite_byte 0x63 $cowoff $cowsz $testdir/file3.chk >> $seqres.full`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

- Line 50: `md5sum $testdir/file1 | _filter_scratch`
- Line 51: `md5sum $testdir/file3 | _filter_scratch`
- Line 52: `md5sum $testdir/file3.chk | _filter_scratch`

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through `_cleanup()`, `rm -rf $tmp.* $testdir`. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Block-size congruence, sharing verification, and post-remount checks are critical because unsupported or partially implemented sharing can otherwise look like ordinary copies. Timing and alignment make the test susceptible to architecture, page-size, and direct-I/O constraints; dmesg filtering must not hide unrelated warnings. Range operations have off-by-one and block-boundary risk; the test relies on xfs_io command support and stable filtering of sparse/unwritten output. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/194 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/195 -->
# sources/test-tools/xfstests/tests/generic/195

## Purpose

Ensuring that copy on write in buffered mode works when the CoW range originally covers multiple extents, some delalloc, some not. - Create a file. - Reflink the odd blocks of the first file into the second file. - Buffered write the even blocks of the second file. - CoW across the halfway mark, starting with the unwritten extent. - Check that the files are now different where we say they're different. The test is registered with `_begin_fstest auto quick clone prealloc` and falls into the reflink/CoW, preallocation/unwritten extent area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `195` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink` and gates execution with `_require_scratch_reflink`, `_require_scratch_delalloc`, `_require_xfs_io_command "falloc"`, `_require_congruent_file_oplen $SCRATCH_MNT $blksz`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 29: `_require_scratch_reflink`
- Line 31: `_require_xfs_io_command "falloc"`
- Line 45: `_weave_reflink_holes $blksz $nr $testdir/file1 $testdir/file3 >> $seqres.full`
- Line 56: `_weave_reflink_holes_delalloc $blksz $nr $testdir/file3 >> $seqres.full`
- Line 57: `$XFS_IO_PROG -f -c "pwrite -S 0x63 -b $cowsz $cowoff $cowsz" $testdir/file3 >> $seqres.full`
- Line 58: `_pwrite_byte 0x63 $cowoff $cowsz $testdir/file3.chk >> $seqres.full`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

- Line 49: `md5sum $testdir/file1 | _filter_scratch`
- Line 50: `md5sum $testdir/file3 | _filter_scratch`
- Line 51: `md5sum $testdir/file3.chk | _filter_scratch`

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through `_cleanup()`, `rm -rf $tmp.* $testdir`. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Block-size congruence, sharing verification, and post-remount checks are critical because unsupported or partially implemented sharing can otherwise look like ordinary copies. Range operations have off-by-one and block-boundary risk; the test relies on xfs_io command support and stable filtering of sparse/unwritten output. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/195 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/196 -->
# sources/test-tools/xfstests/tests/generic/196

## Purpose

Ensuring that copy on write in direct-io mode works when the CoW range originally covers multiple extents, some regular, some not. - Create two files. - Reflink the odd blocks of the first file into the second file. - directio CoW across the halfway mark, starting with the unwritten extent. - Check that the files are now different where we say they're different. The test is registered with `_begin_fstest auto quick clone prealloc` and falls into the reflink/CoW, AIO/direct I/O, preallocation/unwritten extent area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `196` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink` and gates execution with `_require_scratch_reflink`, `_require_xfs_io_command "falloc"`, `_require_odirect`, `_require_congruent_file_oplen $SCRATCH_MNT $blksz`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 28: `_require_scratch_reflink`
- Line 29: `_require_xfs_io_command "falloc"`
- Line 44: `_weave_reflink_regular $blksz $nr $testdir/file1 $testdir/file3 >> $seqres.full`
- Line 55: `$XFS_IO_PROG -d -f -c "pwrite -S 0x63 -b $cowsz $cowoff $cowsz" $testdir/file3 >> $seqres.full`
- Line 56: `_pwrite_byte 0x63 $cowoff $cowsz $testdir/file3.chk >> $seqres.full`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

- Line 48: `md5sum $testdir/file1 | _filter_scratch`
- Line 49: `md5sum $testdir/file3 | _filter_scratch`
- Line 50: `md5sum $testdir/file3.chk | _filter_scratch`

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through `_cleanup()`, `rm -rf $tmp.* $testdir`. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Block-size congruence, sharing verification, and post-remount checks are critical because unsupported or partially implemented sharing can otherwise look like ordinary copies. Timing and alignment make the test susceptible to architecture, page-size, and direct-I/O constraints; dmesg filtering must not hide unrelated warnings. Range operations have off-by-one and block-boundary risk; the test relies on xfs_io command support and stable filtering of sparse/unwritten output. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/196 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/197 -->
# sources/test-tools/xfstests/tests/generic/197

## Purpose

Ensuring that copy on write in buffered mode works when the CoW range originally covers multiple extents, some regular, some not. - Create two files. - Reflink the odd blocks of the first file into the second file. - CoW across the halfway mark, starting with the unwritten extent. - Check that the files are now different where we say they're different. The test is registered with `_begin_fstest auto quick clone prealloc` and falls into the reflink/CoW, preallocation/unwritten extent area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `197` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink` and gates execution with `_require_scratch_reflink`, `_require_xfs_io_command "falloc"`, `_require_congruent_file_oplen $SCRATCH_MNT $blksz`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 28: `_require_scratch_reflink`
- Line 29: `_require_xfs_io_command "falloc"`
- Line 43: `_weave_reflink_regular $blksz $nr $testdir/file1 $testdir/file3 >> $seqres.full`
- Line 54: `$XFS_IO_PROG -f -c "pwrite -S 0x63 -b $cowsz $cowoff $cowsz" $testdir/file3 >> $seqres.full`
- Line 55: `_pwrite_byte 0x63 $cowoff $cowsz $testdir/file3.chk >> $seqres.full`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

- Line 47: `md5sum $testdir/file1 | _filter_scratch`
- Line 48: `md5sum $testdir/file3 | _filter_scratch`
- Line 49: `md5sum $testdir/file3.chk | _filter_scratch`

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through `_cleanup()`, `rm -rf $tmp.* $testdir`. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Block-size congruence, sharing verification, and post-remount checks are critical because unsupported or partially implemented sharing can otherwise look like ordinary copies. Range operations have off-by-one and block-boundary risk; the test relies on xfs_io command support and stable filtering of sparse/unwritten output. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/197 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/198 -->
# sources/test-tools/xfstests/tests/generic/198

## Purpose

See also https://bugzilla.redhat.com/show_bug.cgi?id=217098 The test is registered with `_begin_fstest auto aio quick` and falls into the AIO/direct I/O area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `198` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter` and gates execution with `_require_aiodio aiodio_sparse2`, `_require_test`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 23: `$AIO_TEST "$TEST_DIR/aiodio_sparse"`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

The primary pass signal is the script reaching `status=0` or `exit $status` with no unexpected command failure, filtered output mismatch, or dmesg warning.

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through none declared. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Timing and alignment make the test susceptible to architecture, page-size, and direct-I/O constraints; dmesg filtering must not hide unrelated warnings. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=$?; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/198 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/199 -->
# sources/test-tools/xfstests/tests/generic/199

## Purpose

Ensuring that copy on write in direct-io mode works when the CoW range originally covers multiple extents, some unwritten, some not. - Create a file with the following repeating sequence of blocks: 1. reflinked 2. unwritten 3. hole 4. regular block 5. delalloc - directio CoW across the halfway mark, starting with the unwritten extent. - Check that the files are now different where we say they're different. The test is registered with `_begin_fstest auto quick clone punch prealloc` and falls into the reflink/CoW, AIO/direct I/O, preallocation/unwritten extent, hole punching area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `199` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink` and gates execution with `_require_scratch_reflink`, `_require_scratch_delalloc`, `_require_xfs_io_command "falloc"`, `_require_xfs_io_command "fpunch"`, `_require_cp_reflink`, `_require_odirect`, `_require_congruent_file_oplen $SCRATCH_MNT $blksz`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 32: `_require_scratch_reflink`
- Line 34: `_require_xfs_io_command "falloc"`
- Line 35: `_require_xfs_io_command "fpunch"`
- Line 36: `_require_cp_reflink`
- Line 51: `_weave_reflink_rainbow $blksz $nr $testdir/file1 $testdir/file3 >> $seqres.full`
- Line 62: `_weave_reflink_rainbow_delalloc $blksz $nr $testdir/file3 >> $seqres.full`
- Line 64: `$XFS_IO_PROG -d -f -c "pwrite -S 0x63 -b $cowsz $cowoff $cowsz" $testdir/file3 >> $seqres.full`
- Line 65: `_pwrite_byte 0x63 $cowoff $cowsz $testdir/file3.chk >> $seqres.full`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

- Line 55: `md5sum $testdir/file1 | _filter_scratch`
- Line 56: `md5sum $testdir/file3 | _filter_scratch`
- Line 57: `md5sum $testdir/file3.chk | _filter_scratch`

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through `_cleanup()`, `rm -rf $tmp.* $testdir`. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Block-size congruence, sharing verification, and post-remount checks are critical because unsupported or partially implemented sharing can otherwise look like ordinary copies. Timing and alignment make the test susceptible to architecture, page-size, and direct-I/O constraints; dmesg filtering must not hide unrelated warnings. Range operations have off-by-one and block-boundary risk; the test relies on xfs_io command support and stable filtering of sparse/unwritten output. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/199 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/200 -->
# sources/test-tools/xfstests/tests/generic/200

## Purpose

Ensuring that copy on write in buffered mode works when the CoW range originally covers multiple extents, some unwritten, some not. - Create a file with the following repeating sequence of blocks: 1. reflinked 2. unwritten 3. hole 4. regular block 5. delalloc - CoW across the halfway mark, starting with the unwritten extent. - Check that the files are now different where we say they're different. The test is registered with `_begin_fstest auto quick clone punch prealloc` and falls into the reflink/CoW, AIO/direct I/O, preallocation/unwritten extent, hole punching area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `200` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink` and gates execution with `_require_scratch_reflink`, `_require_scratch_delalloc`, `_require_xfs_io_command "falloc"`, `_require_xfs_io_command "fpunch"`, `_require_cp_reflink`, `_require_odirect`, `_require_congruent_file_oplen $SCRATCH_MNT $blksz`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 32: `_require_scratch_reflink`
- Line 34: `_require_xfs_io_command "falloc"`
- Line 35: `_require_xfs_io_command "fpunch"`
- Line 36: `_require_cp_reflink`
- Line 51: `_weave_reflink_rainbow $blksz $nr $testdir/file1 $testdir/file3 >> $seqres.full`
- Line 62: `_weave_reflink_rainbow_delalloc $blksz $nr $testdir/file3 >> $seqres.full`
- Line 64: `$XFS_IO_PROG -f -c "pwrite -S 0x63 -b $cowsz $cowoff $cowsz" $testdir/file3 >> $seqres.full`
- Line 65: `_pwrite_byte 0x63 $cowoff $cowsz $testdir/file3.chk >> $seqres.full`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

- Line 55: `md5sum $testdir/file1 | _filter_scratch`
- Line 56: `md5sum $testdir/file3 | _filter_scratch`
- Line 57: `md5sum $testdir/file3.chk | _filter_scratch`

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through `_cleanup()`, `rm -rf $tmp.* $testdir`. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Block-size congruence, sharing verification, and post-remount checks are critical because unsupported or partially implemented sharing can otherwise look like ordinary copies. Timing and alignment make the test susceptible to architecture, page-size, and direct-I/O constraints; dmesg filtering must not hide unrelated warnings. Range operations have off-by-one and block-boundary risk; the test relies on xfs_io command support and stable filtering of sparse/unwritten output. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/200 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/201 -->
# sources/test-tools/xfstests/tests/generic/201

## Purpose

See what happens if we dirty a lot of pages via CoW and immediately unlink the file. The test is registered with `_begin_fstest auto quick clone prealloc` and falls into the reflink/CoW, preallocation/unwritten extent area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `201` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink` and gates execution with `_require_scratch_reflink`, `_require_xfs_io_command "falloc"`, `_require_congruent_file_oplen $SCRATCH_MNT $blksz`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 24: `_require_scratch_reflink`
- Line 25: `_require_xfs_io_command "falloc"`
- Line 39: `_pwrite_byte 0x61 0 $filesize $testdir/file1 >> $seqres.full`
- Line 40: `_pwrite_byte 0x62 0 $filesize $testdir/file3 >> $seqres.full`
- Line 41: `_pwrite_byte 0x62 0 $filesize $testdir/file3.chk >> $seqres.full`
- Line 43: `_reflink_range $testdir/file1 $((blksz * f)) $testdir/file3 $((blksz * f)) $blksz >> $seqres.full`
- Line 44: `_pwrite_byte 0x61 $((blksz * f)) $blksz $testdir/file3.chk >> $seqres.full`
- Line 56: `$XFS_IO_PROG -f -c "pwrite -S 0x63 -b $cowsz $cowoff $cowsz" $testdir/file3 >> $seqres.full`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

- Line 49: `md5sum $testdir/file1 | _filter_scratch`
- Line 50: `md5sum $testdir/file3 | _filter_scratch`
- Line 51: `md5sum $testdir/file3.chk | _filter_scratch`

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through `_cleanup()`, `rm -rf $tmp.* $testdir`. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Block-size congruence, sharing verification, and post-remount checks are critical because unsupported or partially implemented sharing can otherwise look like ordinary copies. Range operations have off-by-one and block-boundary risk; the test relies on xfs_io command support and stable filtering of sparse/unwritten output. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/201 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/202 -->
# sources/test-tools/xfstests/tests/generic/202

## Purpose

See what happens if we CoW across not-block-aligned EOF. The test is registered with `_begin_fstest auto quick clone` and falls into the reflink/CoW area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `202` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink` and gates execution with `_require_scratch_reflink`, `_require_cp_reflink`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 23: `_require_scratch_reflink`
- Line 24: `_require_cp_reflink`
- Line 35: `_pwrite_byte 0x61 0 $((blksz + 17)) $testdir/file1 >> $seqres.full`
- Line 36: `_cp_reflink $testdir/file1 $testdir/file2`
- Line 37: `_pwrite_byte 0x61 0 $((blksz + 17)) $testdir/file2.chk >> $seqres.full`
- Line 46: `$XFS_IO_PROG -f -c "pwrite -S 0x63 $((blksz + 17)) 17" $testdir/file2 >> $seqres.full`
- Line 47: `$XFS_IO_PROG -f -c "pwrite -S 0x63 $((blksz + 17)) 17" $testdir/file2.chk >> $seqres.full`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

- Line 41: `md5sum $testdir/file1 | _filter_scratch`
- Line 42: `md5sum $testdir/file2 | _filter_scratch`
- Line 43: `md5sum $testdir/file2.chk | _filter_scratch`

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through `_cleanup()`, `rm -rf $tmp.* $testdir`. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Block-size congruence, sharing verification, and post-remount checks are critical because unsupported or partially implemented sharing can otherwise look like ordinary copies. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/202 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/203 -->
# sources/test-tools/xfstests/tests/generic/203

## Purpose

See what happens if we DIO CoW across not-block-aligned EOF. The test is registered with `_begin_fstest auto quick clone` and falls into the reflink/CoW, AIO/direct I/O area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `203` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink` and gates execution with `_require_scratch_reflink`, `_require_cp_reflink`, `_require_odirect`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 23: `_require_scratch_reflink`
- Line 24: `_require_cp_reflink`
- Line 36: `_pwrite_byte 0x61 0 $((blksz + 17)) $testdir/file1 >> $seqres.full`
- Line 37: `_cp_reflink $testdir/file1 $testdir/file2`
- Line 38: `_pwrite_byte 0x61 0 $((blksz + 17)) $testdir/file2.chk >> $seqres.full`
- Line 47: `$XFS_IO_PROG -d -f -c "pwrite -S 0x63 $blksz $blksz" $testdir/file2 >> $seqres.full`
- Line 48: `$XFS_IO_PROG -f -c "pwrite -S 0x63 $blksz $blksz" $testdir/file2.chk >> $seqres.full`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

- Line 42: `md5sum $testdir/file1 | _filter_scratch`
- Line 43: `md5sum $testdir/file2 | _filter_scratch`
- Line 44: `md5sum $testdir/file2.chk | _filter_scratch`

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through `_cleanup()`, `rm -rf $tmp.* $testdir`. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Block-size congruence, sharing verification, and post-remount checks are critical because unsupported or partially implemented sharing can otherwise look like ordinary copies. Timing and alignment make the test susceptible to architecture, page-size, and direct-I/O constraints; dmesg filtering must not hide unrelated warnings. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/203 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/204 -->
# sources/test-tools/xfstests/tests/generic/204

## Purpose

For xfs, we need to handle the different default log sizes that different versions of mkfs create. All should be valid with a 16MB log, so use that. And v4/512 v5/1k xfs don't have enough free inodes, set imaxpct=50 at mkfs time solves this problem. The test is registered with `_begin_fstest metadata rw auto` and falls into the ENOSPC area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `204` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter` and gates execution with `_require_scratch`. Local helpers are `line 57 `filter() {``. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 15: `_require_scratch`
- Line 24: `_scratch_mkfs_sized $SIZE 2> /dev/null > $tmp.mkfs.raw`
- Line 26: `_scratch_mount`
- Line 35: `space=$(stat -f -c '%f * %S' $SCRATCH_MNT | $BC_PROG)`
- Line 55: `_scratch_resvblks $resv_blks >> $seqres.full 2>&1`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

- Line 35: `space=$(stat -f -c '%f * %S' $SCRATCH_MNT | $BC_PROG)`

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through none declared. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Free-space arithmetic is intentionally tight, so filesystem geometry, reserved blocks, or delayed allocation can change whether ENOSPC appears at the intended point. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/204 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/205 -->
# sources/test-tools/xfstests/tests/generic/205

## Purpose

This test is dependent on the system page size, so we cannot use md5 in the golden output; we can only compare to a check file. The test is registered with `_begin_fstest auto quick clone` and falls into the reflink/CoW, truncate area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `205` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink` and gates execution with `_require_scratch_reflink`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 27: `_require_scratch_reflink`
- Line 43: `_pwrite_byte 0x61 0 $pagesz $testdir/file1 >> $seqres.full`
- Line 45: `$XFS_IO_PROG -f -c "truncate $pagesz" $testdir/file2 >> $seqres.full`
- Line 46: `$XFS_IO_PROG -f -c "truncate $pagesz" $testdir/file2.chk >> $seqres.full`
- Line 48: `_pwrite_byte 0x61 $blksz $blksz $testdir/file2 >> $seqres.full`
- Line 49: `_pwrite_byte 0x61 $blksz $blksz $testdir/file2.chk >> $seqres.full`
- Line 51: `_pwrite_byte 0x61 $((blksz * 3)) $blksz $testdir/file2 >> $seqres.full`
- Line 52: `_pwrite_byte 0x61 $((blksz * 3)) $blksz $testdir/file2.chk >> $seqres.full`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

- Line 59: `! cmp -s $testdir/file1 $testdir/file2 || _fail "file1 and file2 don't match."`
- Line 60: `cmp -s $testdir/file2 $testdir/file2.chk || _fail "file2 and file2.chk don't match."`

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through `_cleanup()`, `rm -rf $tmp.* $testdir`. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Block-size congruence, sharing verification, and post-remount checks are critical because unsupported or partially implemented sharing can otherwise look like ordinary copies. Range operations have off-by-one and block-boundary risk; the test relies on xfs_io command support and stable filtering of sparse/unwritten output. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/205 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/206 -->
# sources/test-tools/xfstests/tests/generic/206

## Purpose

This test is dependent on the system page size, so we cannot use md5 in the golden output; we can only compare to a check file. The test is registered with `_begin_fstest auto quick clone` and falls into the reflink/CoW, AIO/direct I/O, truncate area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `206` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink` and gates execution with `_require_scratch_reflink`, `_require_odirect`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 27: `_require_scratch_reflink`
- Line 44: `_pwrite_byte 0x61 0 $pagesz $testdir/file1 >> $seqres.full`
- Line 46: `$XFS_IO_PROG -f -c "truncate $pagesz" $testdir/file2 >> $seqres.full`
- Line 47: `$XFS_IO_PROG -f -c "truncate $pagesz" $testdir/file2.chk >> $seqres.full`
- Line 49: `_pwrite_byte 0x61 $blksz $blksz $testdir/file2 >> $seqres.full`
- Line 50: `_pwrite_byte 0x61 $blksz $blksz $testdir/file2.chk >> $seqres.full`
- Line 52: `_pwrite_byte 0x61 $((blksz * 3)) $blksz $testdir/file2 >> $seqres.full`
- Line 53: `_pwrite_byte 0x61 $((blksz * 3)) $blksz $testdir/file2.chk >> $seqres.full`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

- Line 60: `! cmp -s $testdir/file1 $testdir/file2 || _fail "file1 and file2 don't match."`
- Line 61: `cmp -s $testdir/file2 $testdir/file2.chk || _fail "file2 and file2.chk don't match."`

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through `_cleanup()`, `rm -rf $tmp.* $testdir`. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Block-size congruence, sharing verification, and post-remount checks are critical because unsupported or partially implemented sharing can otherwise look like ordinary copies. Timing and alignment make the test susceptible to architecture, page-size, and direct-I/O constraints; dmesg filtering must not hide unrelated warnings. Range operations have off-by-one and block-boundary risk; the test relies on xfs_io command support and stable filtering of sparse/unwritten output. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/206 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/207 -->
# sources/test-tools/xfstests/tests/generic/207

## Purpose

Run aio-dio-extend-stat - test race in dio aio completion The test is registered with `_begin_fstest auto aio quick` and falls into the AIO/direct I/O area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `207` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter` and gates execution with `_require_test`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 18: `_run_aiodio aio-dio-extend-stat`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

The primary pass signal is the script reaching `status=0` or `exit $status` with no unexpected command failure, filtered output mismatch, or dmesg warning.

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through none declared. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Timing and alignment make the test susceptible to architecture, page-size, and direct-I/O constraints; dmesg filtering must not hide unrelated warnings. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `exit $status`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/207 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/208 -->
# sources/test-tools/xfstests/tests/generic/208

## Purpose

Run aio-dio-invalidate-failure - test race in read cache invalidation The test is registered with `_begin_fstest auto aio` and falls into the AIO/direct I/O area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `208` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter` and gates execution with `_require_test`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 18: `_run_aiodio aio-dio-invalidate-failure`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

The primary pass signal is the script reaching `status=0` or `exit $status` with no unexpected command failure, filtered output mismatch, or dmesg warning.

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through none declared. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Timing and alignment make the test susceptible to architecture, page-size, and direct-I/O constraints; dmesg filtering must not hide unrelated warnings. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `exit $status`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/208 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/209 -->
# sources/test-tools/xfstests/tests/generic/209

## Purpose

Run aio-dio-invalidate-readahead - test sync DIO invalidation of readahead The test is registered with `_begin_fstest auto aio` and falls into the AIO/direct I/O area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `209` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter` and gates execution with `_require_test`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 18: `_run_aiodio aio-dio-invalidate-readahead`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

The primary pass signal is the script reaching `status=0` or `exit $status` with no unexpected command failure, filtered output mismatch, or dmesg warning.

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through none declared. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Timing and alignment make the test susceptible to architecture, page-size, and direct-I/O constraints; dmesg filtering must not hide unrelated warnings. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `exit $status`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/209 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/210 -->
# sources/test-tools/xfstests/tests/generic/210

## Purpose

Run aio-dio-subblock-eof-read - test AIO read of last block of DIO file The test is registered with `_begin_fstest auto aio quick` and falls into the AIO/direct I/O area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `210` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter` and gates execution with `_require_test`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 18: `_run_aiodio aio-dio-subblock-eof-read`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

The primary pass signal is the script reaching `status=0` or `exit $status` with no unexpected command failure, filtered output mismatch, or dmesg warning.

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through none declared. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Timing and alignment make the test susceptible to architecture, page-size, and direct-I/O constraints; dmesg filtering must not hide unrelated warnings. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `exit $status`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/210 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/211 -->
# sources/test-tools/xfstests/tests/generic/211

## Purpose

Use a 512M fs so that it's fast to fill it with data but not too small such that on btrfs it results in a fs with mixed block groups - we want to have dedicated block groups for data and metadata, so that after filling all the data block groups we can do a NOCOW write with mmap (if we have enough free metadata space available). The test is registered with `_begin_fstest auto quick rw mmap` and falls into the reflink/CoW, mmap, ENOSPC area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `211` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter` and gates execution with `_require_scratch`, `_require_inplace_writes $SCRATCH_MNT`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 12: `_begin_fstest auto quick rw mmap`
- Line 18: `_fixed_by_fs_commit btrfs 6599716de2d6 "btrfs: fix -ENOSPC mmap write failure on NOCOW files/extents"`
- Line 36: `$XFS_IO_PROG -c "pwrite -S 0xab 0 1M" $SCRATCH_MNT/foobar | _filter_xfs_io`
- Line 45: `dd if=/dev/zero of=$SCRATCH_MNT/filler bs=$blksz >>$seqres.full 2>&1`
- Line 48: `$XFS_IO_PROG -c "mmap -w 0 1M" -c "mwrite -S 0xcd 0 1M" -c "munmap" $SCRATCH_MNT/foobar`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

- Line 36: `$XFS_IO_PROG -c "pwrite -S 0xab 0 1M" $SCRATCH_MNT/foobar | _filter_xfs_io`

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through none declared. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Block-size congruence, sharing verification, and post-remount checks are critical because unsupported or partially implemented sharing can otherwise look like ordinary copies. Timing and alignment make the test susceptible to architecture, page-size, and direct-I/O constraints; dmesg filtering must not hide unrelated warnings. Free-space arithmetic is intentionally tight, so filesystem geometry, reserved blocks, or delayed allocation can change whether ENOSPC appears at the intended point. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `implicit harness exit status`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/211 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/212 -->
# sources/test-tools/xfstests/tests/generic/212

## Purpose

Run aio-io-setup-with-nonwritable-context-pointer - The test is registered with `_begin_fstest auto aio quick` and falls into the AIO/direct I/O area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `212` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter` and gates execution with `_require_test`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 19: `_run_aiodio aio-io-setup-with-nonwritable-context-pointer`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

The primary pass signal is the script reaching `status=0` or `exit $status` with no unexpected command failure, filtered output mismatch, or dmesg warning.

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through none declared. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Timing and alignment make the test susceptible to architecture, page-size, and direct-I/O constraints; dmesg filtering must not hide unrelated warnings. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `exit $status`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/212 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/213 -->
# sources/test-tools/xfstests/tests/generic/213

## Purpose

generic, but xfs_io's fallocate must work only Linux supports fallocate The test is registered with `_begin_fstest rw auto prealloc quick enospc` and falls into the ENOSPC, preallocation/unwritten extent, truncate area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `213` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter` and gates execution with `_require_test`, `_require_xfs_io_command "falloc"`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 23: `[ -n "$XFS_IO_PROG" ] || _notrun "xfs_io executable not found"`
- Line 26: `_require_xfs_io_command "falloc"`
- Line 33: `$XFS_IO_PROG -f -c 'falloc 0 1g' -c 'truncate 100' $TEST_DIR/ouch`
- Line 37: `$XFS_IO_PROG -f -c 'falloc 0 1g' -c 'truncate 1g' $TEST_DIR/ouch`
- Line 41: `$XFS_IO_PROG -f -c 'falloc 0 1g' -c 'truncate 2g' $TEST_DIR/ouch`
- Line 45: `$XFS_IO_PROG -f -c 'falloc 0 1g' -c 'falloc 2g 1m' -c 'truncate 3g' $TEST_DIR/ouch`
- Line 49: `echo "We should get: fallocate: No space left on device"`
- Line 53: `$XFS_IO_PROG -f -c "falloc 0 ${toobig}k" $TEST_DIR/ouch`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

The primary pass signal is the script reaching `status=0` or `exit $status` with no unexpected command failure, filtered output mismatch, or dmesg warning.

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through none declared. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Free-space arithmetic is intentionally tight, so filesystem geometry, reserved blocks, or delayed allocation can change whether ENOSPC appears at the intended point. Range operations have off-by-one and block-boundary risk; the test relies on xfs_io command support and stable filtering of sparse/unwritten output. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/213 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/214 -->
# sources/test-tools/xfstests/tests/generic/214

## Purpose

We don't remove files after they are written to check for subsequent fs corruption at the end The test is registered with `_begin_fstest rw auto prealloc quick` and falls into the AIO/direct I/O, preallocation/unwritten extent, truncate area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `214` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter` and gates execution with `_require_test`, `_require_xfs_io_command "falloc"`, `_require_odirect`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 29: `[ -n "$XFS_IO_PROG" ] || _notrun "xfs_io executable not found"`
- Line 33: `_require_xfs_io_command "falloc"`
- Line 43: `echo "=== falloc & read  ==="`
- Line 44: `$XFS_IO_PROG -f -c 'falloc 0 4096' -c 'pread -v 0 4096' $TEST_DIR/test214-1 | _filter_xfs_io_unique`
- Line 52: `echo "=== falloc, write beginning, read ==="`
- Line 53: `$XFS_IO_PROG -f -c 'falloc 0 512' -c 'pwrite 0 1' -c 'pread -v 0 512' $TEST_DIR/test214-2 | _filter_xfs_io_unique`
- Line 60: `echo "=== falloc, write middle, read ==="`
- Line 61: `$XFS_IO_PROG -f -c 'falloc 0 512' -c 'pwrite 256 1' -c 'pread -v 0 512' $TEST_DIR/test214-3 | _filter_xfs_io_unique`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

- Line 44: `$XFS_IO_PROG -f -c 'falloc 0 4096' -c 'pread -v 0 4096' $TEST_DIR/test214-1 | _filter_xfs_io_unique`
- Line 53: `$XFS_IO_PROG -f -c 'falloc 0 512' -c 'pwrite 0 1' -c 'pread -v 0 512' $TEST_DIR/test214-2 | _filter_xfs_io_unique`
- Line 61: `$XFS_IO_PROG -f -c 'falloc 0 512' -c 'pwrite 256 1' -c 'pread -v 0 512' $TEST_DIR/test214-3 | _filter_xfs_io_unique`
- Line 69: `$XFS_IO_PROG -f -c 'falloc 0 512' -c 'pwrite 511 1' -c 'pread -v 0 512' $TEST_DIR/test214-4 | _filter_xfs_io_unique`
- Line 87: `$XFS_IO_PROG -f -c 'falloc         0x0     0x65C00' -c 'pwrite -S 0xAA 0x12000 0x10000' -c 'fsync' -c 'truncate 0x16000' $TEST_DIR/test214-5 | _filter_xfs_io_unique`
- Line 95: `$XFS_IO_PROG -f -d -c 'pread -v 0 0x16000' $TEST_DIR/test214-5 | _filter_xfs_io_unique`

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through `_cleanup()`, `rm -f $tmp.*`. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Timing and alignment make the test susceptible to architecture, page-size, and direct-I/O constraints; dmesg filtering must not hide unrelated warnings. Range operations have off-by-one and block-boundary risk; the test relies on xfs_io command support and stable filtering of sparse/unwritten output. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/214 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/215 -->
# sources/test-tools/xfstests/tests/generic/215

## Purpose

Based on the testcase in http://bugzilla.kernel.org/show_bug.cgi?id=2645 The test is registered with `_begin_fstest auto metadata quick mmap` and falls into the mmap, timestamp area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `215` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter` and gates execution with `_require_test`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 12: `_begin_fstest auto metadata quick mmap`
- Line 26: `testfile=$TEST_DIR/tst.mmap`
- Line 30: `dd if=/dev/zero of=$testfile count=4096`
- Line 38: `echo "writing via mmap"`
- Line 39: `$XFS_IO_PROG -f -c 'mmap 0 4096' -c 'mwrite 0 4096' $testfile | _filter_xfs_io_unique`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

- Line 32: `mtime1=`stat -c "%Y" $testfile``
- Line 33: `ctime1=`stat -c "%Z" $testfile``
- Line 39: `$XFS_IO_PROG -f -c 'mmap 0 4096' -c 'mwrite 0 4096' $testfile | _filter_xfs_io_unique`
- Line 44: `mtime2=`stat -c "%Y" $testfile``
- Line 45: `ctime2=`stat -c "%Z" $testfile``

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through `_cleanup()`. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

Timing and alignment make the test susceptible to architecture, page-size, and direct-I/O constraints; dmesg filtering must not hide unrelated warnings. Timestamp resolution and mount options can make the signal weak unless the test accounts for atime/mtime/ctime granularity. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/215 -->
