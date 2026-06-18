# subset-b-009548 research

Grouped research for xfstests generic shell tests `487` through `617`. Each section preserves the source path and is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/487 -->
# sources/test-tools/xfstests/tests/generic/487

## Purpose

Open a file several times, write to it, fsync on all fds and make sure that they all return 0. Change the device to start throwing errors. Write again on all fds and fsync on all fds. Ensure that we get errors on all of them. Then fsync on all one last time and verify that all return 0.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick eio`. It imports `./common/preamble`, `./common/filter`, `./common/dmerror`. Prerequisite and skip gates include `_require_scratch_nocheck`, `_require_logdev`, `_require_dm_target error`, `_require_fs_space $SCRATCH_MNT $datalen`. Local helper functions: `_cleanup`. External command surfaces and helper binaries visible in the source include `xfs_io`, `mount`. Important harness variables and paths include `SCRATCH_MNT`, `seqres.full`, `tmp`, `seq`, `FSTYP`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch_nocheck`; `btrfs)`; `_notrun "btrfs has a specialized test for this"`; `*)`; `_require_logdev`; `_require_dm_target error`; `unset SCRATCH_RTDEV`; `echo "Format and mount"`; `_scratch_mkfs > $seqres.full 2>&1`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`; injects block-device, power-fail, shutdown, or thin-provisioning behavior to validate recovery paths; uses explicit sync/fsync/remount points to force persistence boundaries. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

writeback error reporting can be missed, over-reported, or cleared at the wrong time. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/487.out`. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/487 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/488 -->
# sources/test-tools/xfstests/tests/generic/488

## Purpose

Test having many file descriptors referring to deleted files open. Regression test for patch "Btrfs: fix ENOSPC caused by orphan items reservations".

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick`. It imports `./common/preamble`, `./common/filter`. Prerequisite and skip gates include `_require_scratch`, `_require_test_program "multi_open_unlink"`. No major local helper functions are defined; the scenario is driven directly by the top-level shell flow. External command surfaces and helper binaries visible in the source include `multi_open_unlink`, `seq`. Important harness variables and paths include `SCRATCH_MNT`, `seqres.full`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch`; `_require_test_program "multi_open_unlink"`; `_scratch_mkfs_sized $((1024 * 1024 * 1024)) >> $seqres.full 2>&1`; `_scratch_mount`; `ulimit -n $((16 * 1024))`; `$here/src/multi_open_unlink -f $SCRATCH_MNT/$seq -n 10000 -s 0`; `echo "Silence is golden"`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

environmental skips and helper availability can dominate failures, so `_require_*` gates are part of the contract. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/488.out`; success is mostly silence after prerequisite and operation checks. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/488 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/489 -->
# sources/test-tools/xfstests/tests/generic/489

## Purpose

Test that xattrs are not lost after calling fsync multiple times with a filesystem commit in between the fsync calls.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick attr log`. It imports `./common/preamble`, `./common/filter`, `./common/dmflakey`, `./common/attr`. Prerequisite and skip gates include `_require_scratch`, `_require_dm_target flakey`, `_require_attrs`, `_require_metadata_journaling $SCRATCH_DEV`. Local helper functions: `_cleanup`. External command surfaces and helper binaries visible in the source include `setfattr`, `xfs_io`, `touch`, `mount`, `od`. Important harness variables and paths include `SCRATCH_MNT`, `SCRATCH_DEV`, `seqres.full`, `tmp`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch`; `_require_dm_target flakey`; `_require_attrs`; `_scratch_mkfs >>$seqres.full 2>&1`; `_require_metadata_journaling $SCRATCH_DEV`; `_init_flakey`; `_scratch_mount`; `touch $SCRATCH_MNT/foobar`; `$SETFATTR_PROG -n user.xa1 -v qwerty $SCRATCH_MNT/foobar`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`; injects block-device, power-fail, shutdown, or thin-provisioning behavior to validate recovery paths; uses explicit sync/fsync/remount points to force persistence boundaries. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

ordering bugs in journal replay or fsync logging can lose metadata or data after simulated power loss. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/489.out`; content dumps/hexdumps expose corruption or unexpected nonzero data. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/489 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/490 -->
# sources/test-tools/xfstests/tests/generic/490

## Purpose

Check that SEEK_DATA works properly for offsets in the middle of large holes. This was broken for ext4 with indirect-block based files and this test checks for that. The problem has been fixed by commit 2ee3ee06a8fd79 "ext4: fix hole length detection in ext4_ind_map_blocks()"

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick rw seek`. It imports `./common/preamble`, `./common/filter`. Prerequisite and skip gates include `_require_test`, `_require_seek_data_hole`, `_require_test_program "seek_sanity_test"`. Local helper functions: `_cleanup`. External command surfaces and helper binaries visible in the source include `seq`. Important harness variables and paths include `TEST_DIR`, `seqres.full`, `tmp`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_test`; `_require_seek_data_hole`; `_require_test_program "seek_sanity_test"`; `_run_seek_sanity_test -s 19 -e 20 $base_test_file > $seqres.full 2>&1 ||`; `_fail "seek sanity check failed!"`.

## State and Persistence Behavior

The test uses the configured test filesystem under `TEST_DIR` without necessarily reformatting it. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

I/O path races may be timing-sensitive and surface only under mmap, direct I/O, io_uring, or fsx replay stress. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/490.out`. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/490 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/491 -->
# sources/test-tools/xfstests/tests/generic/491

## Purpose

Test first read with freeze right after mount. With ext4, this leads to freeze proection bypass WARN_ON in ext4_journal_check_start.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick freeze mount`. It imports `./common/preamble`, `./common/filter`. Prerequisite and skip gates include `_require_scratch`, `_require_freeze`, `_require_command "$TIMEOUT_PROG" "timeout"`. Local helper functions: `_cleanup`. External command surfaces and helper binaries visible in the source include `timeout`, `mount`, `xfs_freeze`. Important harness variables and paths include `SCRATCH_MNT`, `seqres.full`, `tmp`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch`; `_require_freeze`; `_require_command "$TIMEOUT_PROG" "timeout"`; `_scratch_mkfs >>$seqres.full 2>&1`; `_scratch_mount`; `echo "frozen" > $testfile`; `_scratch_cycle_mount "noatime"`; `xfs_freeze -f $SCRATCH_MNT`; `$TIMEOUT_PROG -s KILL 5s cat $testfile`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

environmental skips and helper availability can dominate failures, so `_require_*` gates are part of the contract. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/491.out`. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/491 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/492 -->
# sources/test-tools/xfstests/tests/generic/492

## Purpose

Test the online filesystem label set/get ioctls

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick`. It imports `./common/preamble`, `./common/filter`. Prerequisite and skip gates include `_require_scratch`, `_require_xfs_io_command "label"`, `_require_label_get_max`. No major local helper functions are defined; the scenario is driven directly by the top-level shell flow. External command surfaces and helper binaries visible in the source include `xfs_io`, `seq`, `blkid`, `perl`. Important harness variables and paths include `SCRATCH_MNT`, `SCRATCH_DEV`, `seqres.full`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch`; `_require_xfs_io_command "label"`; `_require_label_get_max`; `_scratch_mkfs > $seqres.full 2>&1`; `_scratch_mount`; `$XFS_IO_PROG -c "label -s label.$seq" $SCRATCH_MNT`; `$XFS_IO_PROG -c "label" $SCRATCH_MNT`; `$XFS_IO_PROG -c "label -c" $SCRATCH_MNT`; `$XFS_IO_PROG -c "label" $SCRATCH_MNT`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

environmental skips and helper availability can dominate failures, so `_require_*` gates are part of the contract. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/492.out`. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/492 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/493 -->
# sources/test-tools/xfstests/tests/generic/493

## Purpose

Check that we can't dedupe a swapfile.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick swap dedupe`. It imports `./common/preamble`, `./common/filter`, `./common/reflink`. Prerequisite and skip gates include `_require_scratch_swapfile`, `_require_scratch_dedupe`. No major local helper functions are defined; the scenario is driven directly by the top-level shell flow. External command surfaces and helper binaries visible in the source include `chattr`, `mount`, `seq`, `mkdir`, `swapon`, `touch`, `cp`, `swapoff`. Important harness variables and paths include `SCRATCH_MNT`, `seqres.full`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch_swapfile`; `_require_scratch_dedupe`; `echo "Format and mount"`; `_scratch_mkfs > $seqres.full 2>&1`; `_scratch_mount >> $seqres.full 2>&1`; `mkdir "$testdir"`; `echo "Initialize file"`; `_format_swapfile "$testdir/file1" $((blocks * blksz)) > /dev/null`; `swapon "$testdir/file1"`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`; temporarily activates swap files and must clean them with `swapoff`. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

active swapfiles must reject extent-changing operations and require page-size/block-size compatibility; shared extent, COW, or dedupe paths can corrupt unrelated file ranges or violate swapfile restrictions. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/493.out`. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/493 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/494 -->
# sources/test-tools/xfstests/tests/generic/494

## Purpose

Test truncation/hole punching of an active swapfile.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick swap punch`. It imports `./common/preamble`, `./common/filter`. Prerequisite and skip gates include `_require_scratch_swapfile`, `_require_xfs_io_command "fpunch"`. No major local helper functions are defined; the scenario is driven directly by the top-level shell flow. External command surfaces and helper binaries visible in the source include `xfs_io`, `mount`, `seq`, `mkdir`, `swapon`, `truncate`, `swapoff`. Important harness variables and paths include `SCRATCH_MNT`, `seqres.full`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch_swapfile`; `_require_xfs_io_command "fpunch"`; `echo "Format and mount"`; `_scratch_mkfs > $seqres.full 2>&1`; `_scratch_mount >> $seqres.full 2>&1`; `mkdir "$testdir"`; `echo "Initialize file"`; `_format_swapfile "$testdir/file1" $((blocks * blksz)) > /dev/null`; `swapon "$testdir/file1"`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`; temporarily activates swap files and must clean them with `swapoff`. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

active swapfiles must reject extent-changing operations and require page-size/block-size compatibility. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/494.out`. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/494 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/495 -->
# sources/test-tools/xfstests/tests/generic/495

## Purpose

Test invalid swap file (with holes)

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick swap`. It imports `./common/preamble`, `./common/filter`. Prerequisite and skip gates include `_require_scratch_swapfile`, `_require_test_program mkswap`, `_require_test_program swapon`, `_require_sparse_files`. No major local helper functions are defined; the scenario is driven directly by the top-level shell flow. External command surfaces and helper binaries visible in the source include `chattr`, `xfs_io`, `mkswap`, `swapon`, `touch`, `chmod`, `truncate`, `swapoff`. Important harness variables and paths include `SCRATCH_MNT`, `seqres.full`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch_swapfile`; `_require_test_program mkswap`; `_require_test_program swapon`; `_require_sparse_files`; `_scratch_mkfs >> $seqres.full 2>&1`; `_scratch_mount`; `blksize=$(_get_file_block_size $SCRATCH_MNT)`; `test $blksize -eq $(getconf PAGE_SIZE) || _notrun "swap file allocation unit size must match page size"`; `touch "$SCRATCH_MNT/swap"`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`; temporarily activates swap files and must clean them with `swapoff`. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

active swapfiles must reject extent-changing operations and require page-size/block-size compatibility. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/495.out`; content dumps/hexdumps expose corruption or unexpected nonzero data. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/495 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/496 -->
# sources/test-tools/xfstests/tests/generic/496

## Purpose

Test various swapfile activation oddities on filesystems that support fallocated swapfiles (for given fs ext4/xfs)

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick swap prealloc`. It imports `./common/preamble`, `./common/filter`. Prerequisite and skip gates include `_require_scratch_swapfile`, `_require_test_program mkswap`, `_require_test_program swapon`, `_require_xfs_io_command "falloc"`. Local helper functions: `_cleanup`, `swapfile_cycle`. External command surfaces and helper binaries visible in the source include `chattr`, `xfs_io`, `mkswap`, `swapon`, `swapoff`, `touch`, `seq`. Important harness variables and paths include `SCRATCH_MNT`, `seqres.full`, `tmp`, `seq`, `FSTYP`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch_swapfile`; `_require_test_program mkswap`; `_require_test_program swapon`; `_require_xfs_io_command "falloc"`; `_scratch_mkfs >>$seqres.full 2>&1`; `_scratch_mount >>$seqres.full 2>&1`; `len=$((2 * 1048576))`; `page_size=$(_get_page_size)`; `echo "fallocate swap" | tee -a $seqres.full`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`; temporarily activates swap files and must clean them with `swapoff`. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

active swapfiles must reject extent-changing operations and require page-size/block-size compatibility. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/496.out`. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/496 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/497 -->
# sources/test-tools/xfstests/tests/generic/497

## Purpose

Test various swapfile activation oddities, having used fcollapse to create discontiguous ranges in the file.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick swap collapse`. It imports `./common/preamble`, `./common/filter`. Prerequisite and skip gates include `_require_scratch_swapfile`, `_require_test_program mkswap`, `_require_test_program swapon`, `_require_xfs_io_command "fcollapse"`. Local helper functions: `_cleanup`, `swapfile_cycle`. External command surfaces and helper binaries visible in the source include `chattr`, `xfs_io`, `mkswap`, `swapon`, `swapoff`. Important harness variables and paths include `SCRATCH_MNT`, `seqres.full`, `tmp`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch_swapfile`; `_require_test_program mkswap`; `_require_test_program swapon`; `_require_xfs_io_command "fcollapse"`; `_scratch_mkfs >>$seqres.full 2>&1`; `_scratch_mount >>$seqres.full 2>&1`; `len=$((2 * 1048576))`; `page_size=$(_get_page_size)`; `echo "large discontig swap" | tee -a $seqres.full`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`; temporarily activates swap files and must clean them with `swapoff`. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

active swapfiles must reject extent-changing operations and require page-size/block-size compatibility. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/497.out`. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/497 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/498 -->
# sources/test-tools/xfstests/tests/generic/498

## Purpose

Test that if we create a new hard link for a file which was previously fsync'ed, fsync a parent directory of the new hard link and power fail, the parent directory exists after mounting the filesystem again.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick log`. It imports `./common/preamble`, `./common/filter`, `./common/dmflakey`. Prerequisite and skip gates include `_require_scratch`, `_require_hardlinks`, `_require_dm_target flakey`, `_require_metadata_journaling $SCRATCH_DEV`. Local helper functions: `_cleanup`. External command surfaces and helper binaries visible in the source include `xfs_io`, `mkdir`, `touch`, `ln`, `mount`. Important harness variables and paths include `SCRATCH_MNT`, `SCRATCH_DEV`, `seqres.full`, `tmp`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch`; `_require_hardlinks`; `_require_dm_target flakey`; `_scratch_mkfs >>$seqres.full 2>&1`; `_require_metadata_journaling $SCRATCH_DEV`; `_init_flakey`; `_scratch_mount`; `mkdir $SCRATCH_MNT/A`; `mkdir $SCRATCH_MNT/B`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`; injects block-device, power-fail, shutdown, or thin-provisioning behavior to validate recovery paths; uses explicit sync/fsync/remount points to force persistence boundaries. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

ordering bugs in journal replay or fsync logging can lose metadata or data after simulated power loss. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/498.out`; success is mostly silence after prerequisite and operation checks. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/498 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/499 -->
# sources/test-tools/xfstests/tests/generic/499

## Purpose

Test a specific sequence of fsx operations that causes an mmap read past eof to return nonzero contents.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick rw collapse zero prealloc mmap`. It imports `./common/preamble`, `./common/punch`. Prerequisite and skip gates include `_require_scratch`, `_require_xfs_io_command "falloc" "-k"`, `_require_xfs_io_command "fcollapse"`, `_require_xfs_io_command "fzero"`. No major local helper functions are defined; the scenario is driven directly by the top-level shell flow. External command surfaces and helper binaries visible in the source include `fsx`, `truncate`, `touch`. Important harness variables and paths include `SCRATCH_MNT`, `seqres.full`, `tmp`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch`; `_require_xfs_io_command "falloc" "-k"`; `_require_xfs_io_command "fcollapse"`; `_require_xfs_io_command "fzero"`; `_scratch_mkfs >>$seqres.full 2>&1`; `_scratch_mount`; `writes a deterministic fsx replay script`; `fallocate 0x77e2 0x5f06 0x269a2 keep_size`; `mapwrite 0x2e7fc 0x42ba 0x3f989`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

I/O path races may be timing-sensitive and surface only under mmap, direct I/O, io_uring, or fsx replay stress. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/499.out`; success is mostly silence after prerequisite and operation checks; fsx/fsstress style stress exits cleanly and emits only filtered diagnostics. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/499 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/500 -->
# sources/test-tools/xfstests/tests/generic/500

## Purpose

Race test running out of data space with concurrent discard operation on dm-thin. If a user constructs a test that loops repeatedly over below steps on dm-thin, block allocation can fail due to discards not having completed yet (Fixed by a685557 dm thin: handle running out of data space vs concurrent discard): 1) fill thin device via filesystem file 2) remove file 3) fstrim And this maybe cause a deadlock when racing a fstrim with a filesystem (XFS) shutdown. (Fixed by 8c81dd46ef3c Force log to disk before reading the AGF during a fstrim)

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto thin trim`. It imports `./common/preamble`, `./common/filter`, `./common/dmthin`. Prerequisite and skip gates include `_require_scratch_nocheck`, `_require_dm_target thin-pool`, `_exclude_fs btrfs`, `_require_batched_discard $SCRATCH_MNT`. Local helper functions: `_cleanup`. External command surfaces and helper binaries visible in the source include `xfs_io`, `fstrim`. Important harness variables and paths include `SCRATCH_MNT`, `seqres.full`, `tmp`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch_nocheck`; `_require_dm_target thin-pool`; `_exclude_fs btrfs`; `_scratch_mkfs >>$seqres.full 2>&1`; `_scratch_mount`; `_require_batched_discard $SCRATCH_MNT`; `_scratch_unmount`; `BACKING_SIZE=$((128 * 1024 * 1024 / 512))	# 128M`; `VIRTUAL_SIZE=$((BACKING_SIZE + 1024))		# 128M + 1k`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`; injects block-device, power-fail, shutdown, or thin-provisioning behavior to validate recovery paths. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

dm-thin exhaustion/discard races can hang or fail depending on kernel/device-mapper fixes. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/500.out`; success is mostly silence after prerequisite and operation checks. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/500 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/501 -->
# sources/test-tools/xfstests/tests/generic/501

## Purpose

Test that if we do a buffered write to a file, fsync it, clone a range from another file into our file that overlaps the previously written range, fsync the file again and then power fail, after we mount again the filesystem, no file data was lost or corrupted.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick clone log`. It imports `./common/preamble`, `./common/filter`, `./common/reflink`, `./common/dmflakey`. Prerequisite and skip gates include `_require_scratch_reflink`, `_require_dm_target flakey`, `_require_metadata_journaling $SCRATCH_DEV`, `_require_congruent_file_oplen $SCRATCH_MNT 2097152`. Local helper functions: `_cleanup`. External command surfaces and helper binaries visible in the source include `xfs_io`, `mount`. Important harness variables and paths include `SCRATCH_MNT`, `SCRATCH_DEV`, `seqres.full`, `tmp`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch_reflink`; `_require_dm_target flakey`; `_scratch_mkfs >>$seqres.full 2>&1`; `_require_metadata_journaling $SCRATCH_DEV`; `_init_flakey`; `_scratch_mount`; `_require_congruent_file_oplen $SCRATCH_MNT 2097152`; `$XFS_IO_PROG -f -s -c "pwrite -S 0x18 0 2M" $SCRATCH_MNT/foo >>$seqres.full`; `$XFS_IO_PROG -f -s -c "pwrite -S 0x20 0 20M" $SCRATCH_MNT/bar >>$seqres.full`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`; injects block-device, power-fail, shutdown, or thin-provisioning behavior to validate recovery paths; uses explicit sync/fsync/remount points to force persistence boundaries. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

ordering bugs in journal replay or fsync logging can lose metadata or data after simulated power loss; shared extent, COW, or dedupe paths can corrupt unrelated file ranges or violate swapfile restrictions. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/501.out`. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/501 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/502 -->
# sources/test-tools/xfstests/tests/generic/502

## Purpose

Test that if we have a file with 2 (or more) hard links in the same parent directory, rename of the hard links, rename one of the other hard links to the old name of the hard link we renamed before, create a new file in the same parent directory with the old name of second hard link we renamed, fsync fsync this new file and power fail, we will be able to mount again the filesystem and the new file and all hard links exist.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick log`. It imports `./common/preamble`, `./common/filter`, `./common/dmflakey`. Prerequisite and skip gates include `_require_scratch`, `_require_hardlinks`, `_require_dm_target flakey`, `_require_metadata_journaling $SCRATCH_DEV`. Local helper functions: `_cleanup`. External command surfaces and helper binaries visible in the source include `xfs_io`, `mount`, `mkdir`, `touch`, `ln`, `mv`. Important harness variables and paths include `SCRATCH_MNT`, `SCRATCH_DEV`, `seqres.full`, `tmp`, `seq`, `FSTYP`, `MOUNT_OPTIONS`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch`; `_require_hardlinks`; `_require_dm_target flakey`; `_scratch_mkfs >>$seqres.full 2>&1`; `_require_metadata_journaling $SCRATCH_DEV`; `export MOUNT_OPTIONS="-o fsync_mode=strict $MOUNT_OPTIONS"`; `_init_flakey`; `_scratch_mount`; `mkdir $SCRATCH_MNT/testdir`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`; injects block-device, power-fail, shutdown, or thin-provisioning behavior to validate recovery paths; uses explicit sync/fsync/remount points to force persistence boundaries. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

ordering bugs in journal replay or fsync logging can lose metadata or data after simulated power loss. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/502.out`. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/502 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/503 -->
# sources/test-tools/xfstests/tests/generic/503

## Purpose

This is a regression test for kernel patch: ext4: handle layout changes to pinned DAX mapping This test exercises each of the DAX paths in ext4 which remove blocks from an inode's block map. This includes things like hole punch, truncate down, etc. This test was written to regression test errors seen with an ext4 + DAX setup, but the test runs fine with or without DAX and with XFS so we don't require the DAX mount option or a specific filesystem for the test.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick dax punch collapse zero prealloc mmap`. It imports `./common/preamble`, `./common/filter`. Prerequisite and skip gates include `_require_test`, `_require_scratch`, `_require_test_program "t_mmap_collision"`, `_require_xfs_io_command "falloc"`, `_require_xfs_io_command "fpunch"`, `_require_xfs_io_command "fcollapse"`, `_require_xfs_io_command "fzero"`. No major local helper functions are defined; the scenario is driven directly by the top-level shell flow. External command surfaces and helper binaries visible in the source include `t_mmap_collision`, `truncate`, `mount`. Important harness variables and paths include `SCRATCH_MNT`, `TEST_DIR`, `seqres.full`, `seq`, `MOUNT_OPTIONS`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_test`; `_require_scratch`; `_require_test_program "t_mmap_collision"`; `_require_xfs_io_command "falloc"`; `_require_xfs_io_command "fpunch"`; `_require_xfs_io_command "fcollapse"`; `_require_xfs_io_command "fzero"`; `_scratch_mkfs >> $seqres.full 2>&1`; `export MOUNT_OPTIONS=""`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`; uses the configured test filesystem under `TEST_DIR` without necessarily reformatting it; depends on per-inode or mount-option DAX state visible through xattrs/statx and mmap/direct-I/O behavior. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

I/O path races may be timing-sensitive and surface only under mmap, direct I/O, io_uring, or fsx replay stress; DAX mount options, inode flags, page-cache invalidation, and statx reporting have filesystem-specific behavior. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/503.out`; success is mostly silence after prerequisite and operation checks. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/503 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/504 -->
# sources/test-tools/xfstests/tests/generic/504

## Purpose

Regression test case for kernel patch: fs/lock: skip lock owner pid translation in case we are in init_pid_ns Open new fd by exec shell built-in, then require exclusive lock by flock(1) command. Checking /proc/locks for the lock info.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick locks`. It imports `./common/preamble`, `./common/filter`. Prerequisite and skip gates include `_require_test`, `_require_command "$FLOCK_PROG" "flock"`. Local helper functions: `_cleanup`. External command surfaces and helper binaries visible in the source include `flock`, `seq`, `touch`, `stat`, `mkdir`, `mount`, `grep`. Important harness variables and paths include `TEST_DIR`, `seqres.full`, `tmp`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_test`; `_require_command "$FLOCK_PROG" "flock"`; `touch $testfile`; `tf_inode=$(stat -c %i $testfile)`; `echo inode $tf_inode >> $seqres.full`; `exec {test_fd}> $testfile`; `mkdir -p "$move_proc"`; `mount --move /proc "$move_proc"`; `flock -x $test_fd`.

## State and Persistence Behavior

The test uses the configured test filesystem under `TEST_DIR` without necessarily reformatting it. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

environmental skips and helper availability can dominate failures, so `_require_*` gates are part of the contract. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/504.out`; success is mostly silence after prerequisite and operation checks; grep-based checks assert expected metadata or data is still visible. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/504 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/505 -->
# sources/test-tools/xfstests/tests/generic/505

## Purpose

This testcase is trying to test recovery flow of generic filesystem, w/ below steps, once uid or gid changes, after we fsync that file, we can expect that uid/gid can be recovered after sudden power-cuts. 1. touch testfile; 1.1 sync (optional) 2. chown 100 testfile; 3. chgrp 100 testfile; 4. xfs_io -f testfile -c "fsync"; 5. godown; 6. umount; 7. mount; 8. check uid/gid

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest shutdown auto quick metadata`. It imports `./common/preamble`, `./common/filter`. Prerequisite and skip gates include `_require_scratch`, `_require_scratch_shutdown`, `_require_metadata_journaling $SCRATCH_DEV`. Local helper functions: `do_check`. External command surfaces and helper binaries visible in the source include `xfs_io`, `touch`, `chown`, `chgrp`, `umount`, `mount`, `stat`. Important harness variables and paths include `SCRATCH_MNT`, `SCRATCH_DEV`, `seqres.full`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch`; `_require_scratch_shutdown`; `_scratch_mkfs >/dev/null 2>&1`; `_require_metadata_journaling $SCRATCH_DEV`; `stat_opt='-c "uid: %u, gid: %g"'`; `echo "Silence is golden"`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`; injects block-device, power-fail, shutdown, or thin-provisioning behavior to validate recovery paths; uses explicit sync/fsync/remount points to force persistence boundaries. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

ordering bugs in journal replay or fsync logging can lose metadata or data after simulated power loss. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/505.out`; success is mostly silence after prerequisite and operation checks. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/505 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/506 -->
# sources/test-tools/xfstests/tests/generic/506

## Purpose

This testcase is trying to test recovery flow of generic filesystem, w/ below steps, once project id changes, after we fsync that file, we can expect that project id can be recovered after sudden power-cuts. 1. touch testfile; 1.1 sync (optional) 2. chattr -p 100 testfile; 3. xfs_io -f testfile -c "fsync"; 4. godown; 5. umount; 6. mount; 7. check project id

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest shutdown auto quick metadata quota`. It imports `./common/preamble`, `./common/filter`, `./common/quota`. Prerequisite and skip gates include `_require_scratch`, `_require_quota`, `_require_scratch_shutdown`, `_require_metadata_journaling $SCRATCH_DEV`, `_require_prjquota $SCRATCH_DEV`. Local helper functions: `do_check`. External command surfaces and helper binaries visible in the source include `xfs_io`, `touch`, `umount`, `mount`. Important harness variables and paths include `SCRATCH_MNT`, `SCRATCH_DEV`, `seqres.full`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch`; `_require_quota`; `_require_scratch_shutdown`; `_scratch_mkfs >/dev/null 2>&1`; `_scratch_enable_pquota`; `_require_metadata_journaling $SCRATCH_DEV`; `_qmount_option "prjquota"`; `_qmount`; `_require_prjquota $SCRATCH_DEV`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`; injects block-device, power-fail, shutdown, or thin-provisioning behavior to validate recovery paths; uses explicit sync/fsync/remount points to force persistence boundaries; enables quota accounting/enforcement state and adjusts grace timers or ownership/project metadata. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

ordering bugs in journal replay or fsync logging can lose metadata or data after simulated power loss; quota timer and enforcement semantics vary by filesystem and userspace quota tooling. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/506.out`; success is mostly silence after prerequisite and operation checks. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/506 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/507 -->
# sources/test-tools/xfstests/tests/generic/507

## Purpose

This testcase is trying to test recovery flow of generic filesystem, w/ below steps, once i_flags changes, after we fsync that file, we can expect that i_flags can be recovered after sudden power-cuts. 1. touch testfile; 1.1 sync (optional) 2. chattr +[ASai] testfile 3. xfs_io -f testfile -c "fsync"; 4. godown; 5. umount; 6. mount; 7. check i_flags 8. chattr -[ASai] testfile 9. xfs_io -f testfile -c "fsync"; 10. godown; 11. umount; 12. mount; 13. check i_flags

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest shutdown auto quick metadata`. It imports `./common/preamble`, `./common/filter`. Prerequisite and skip gates include `_require_command "$LSATTR_PROG" lasttr`, `_require_command "$CHATTR_PROG" chattr`, `_require_chattr ASai`, `_require_scratch`, `_require_scratch_shutdown`, `_require_metadata_journaling $SCRATCH_DEV`. Local helper functions: `_cleanup`, `do_check`. External command surfaces and helper binaries visible in the source include `chattr`, `lsattr`, `xfs_io`, `touch`, `umount`, `mount`. Important harness variables and paths include `SCRATCH_MNT`, `SCRATCH_DEV`, `seqres.full`, `tmp`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_command "$LSATTR_PROG" lasttr`; `_require_command "$CHATTR_PROG" chattr`; `_require_chattr ASai`; `_require_scratch`; `_require_scratch_shutdown`; `_scratch_mkfs >/dev/null 2>&1`; `_require_metadata_journaling $SCRATCH_DEV`; `echo "Silence is golden"`; `opts="A S a i"`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`; injects block-device, power-fail, shutdown, or thin-provisioning behavior to validate recovery paths; uses explicit sync/fsync/remount points to force persistence boundaries. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

ordering bugs in journal replay or fsync logging can lose metadata or data after simulated power loss. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/507.out`; success is mostly silence after prerequisite and operation checks. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/507 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/508 -->
# sources/test-tools/xfstests/tests/generic/508

## Purpose

This testcase is trying to test recovery flow of generic filesystem, it needs creation time support on specified filesystem. With below steps, once the file is created, creation time attribute should be valid on the file, after we fsync that file, it expects creation time can be recovered after sudden power-cuts. 1. touch testfile; 1.1 sync (optional) 2. xfs_io -f testfile -c "fsync"; 3. godown; 4. umount; 5. mount; 6. check creation time

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest shutdown auto quick metadata`. It imports `./common/preamble`, `./common/filter`. Prerequisite and skip gates include `_require_test_lsattr`, `_require_statx`, `_require_xfs_io_command "statx" "-v"`, `_require_scratch`, `_require_scratch_shutdown`, `_require_scratch_btime`, `_require_metadata_journaling $SCRATCH_DEV`. Local helper functions: `do_check`. External command surfaces and helper binaries visible in the source include `xfs_io`, `touch`, `umount`, `mount`, `grep`. Important harness variables and paths include `SCRATCH_MNT`, `SCRATCH_DEV`, `seqres.full`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_test_lsattr`; `_require_statx`; `_require_xfs_io_command "statx" "-v"`; `_require_scratch`; `_require_scratch_shutdown`; `_require_scratch_btime`; `_scratch_mkfs >/dev/null 2>&1`; `_require_metadata_journaling $SCRATCH_DEV`; `echo "Silence is golden"`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`; injects block-device, power-fail, shutdown, or thin-provisioning behavior to validate recovery paths; uses explicit sync/fsync/remount points to force persistence boundaries. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

ordering bugs in journal replay or fsync logging can lose metadata or data after simulated power loss. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/508.out`; success is mostly silence after prerequisite and operation checks; grep-based checks assert expected metadata or data is still visible. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/508 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/509 -->
# sources/test-tools/xfstests/tests/generic/509

## Purpose

Test that if we fsync a tmpfile, without adding a hard link to it, and then power fail, we will be able to mount the filesystem without triggering any crashes, warnings or corruptions.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick log`. It imports `./common/preamble`, `./common/filter`, `./common/dmflakey`. Prerequisite and skip gates include `_require_scratch`, `_require_xfs_io_command "-T"`, `_require_dm_target flakey`, `_require_metadata_journaling $SCRATCH_DEV`. Local helper functions: `_cleanup`. External command surfaces and helper binaries visible in the source include `xfs_io`, `mount`. Important harness variables and paths include `SCRATCH_MNT`, `SCRATCH_DEV`, `seqres.full`, `tmp`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch`; `_require_xfs_io_command "-T"`; `_require_dm_target flakey`; `_scratch_mkfs >>$seqres.full 2>&1`; `_require_metadata_journaling $SCRATCH_DEV`; `_init_flakey`; `_scratch_mount`; `$XFS_IO_PROG -T -c "pwrite -S 0xab 0 64K" -c "fsync" $SCRATCH_MNT | _filter_xfs_io`; `_flakey_drop_and_remount`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`; injects block-device, power-fail, shutdown, or thin-provisioning behavior to validate recovery paths; uses explicit sync/fsync/remount points to force persistence boundaries. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

ordering bugs in journal replay or fsync logging can lose metadata or data after simulated power loss. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/509.out`. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/509 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/510 -->
# sources/test-tools/xfstests/tests/generic/510

## Purpose

Test that if we move a file from a directory B to a directory A, replace directory B with directory A, fsync the file and then power fail, after mounting the filesystem the file has a single parent, named B and there is no longer any directory with the name A.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick log`. It imports `./common/preamble`, `./common/filter`, `./common/dmflakey`. Prerequisite and skip gates include `_require_scratch`, `_require_dm_target flakey`, `_require_metadata_journaling $SCRATCH_DEV`. Local helper functions: `_cleanup`. External command surfaces and helper binaries visible in the source include `xfs_io`, `mkdir`, `touch`, `mv`, `mount`. Important harness variables and paths include `SCRATCH_MNT`, `SCRATCH_DEV`, `seqres.full`, `tmp`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch`; `_require_dm_target flakey`; `_scratch_mkfs >>$seqres.full 2>&1`; `_require_metadata_journaling $SCRATCH_DEV`; `_init_flakey`; `_scratch_mount`; `mkdir $SCRATCH_MNT/testdir`; `mkdir $SCRATCH_MNT/testdir/A`; `mkdir $SCRATCH_MNT/testdir/B`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`; injects block-device, power-fail, shutdown, or thin-provisioning behavior to validate recovery paths; uses explicit sync/fsync/remount points to force persistence boundaries. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

ordering bugs in journal replay or fsync logging can lose metadata or data after simulated power loss. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/510.out`. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/510 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/511 -->
# sources/test-tools/xfstests/tests/generic/511

## Purpose

Test a specific sequence of fsx operations that causes an mmap read past eof to return nonzero contents.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick rw zero prealloc mmap`. It imports `./common/preamble`, `./common/punch`. Prerequisite and skip gates include `_require_scratch`, `_require_xfs_io_command "falloc" "-k"`, `_require_xfs_io_command "fzero"`. No major local helper functions are defined; the scenario is driven directly by the top-level shell flow. External command surfaces and helper binaries visible in the source include `xfs_io`, `fsx`, `truncate`, `touch`. Important harness variables and paths include `SCRATCH_MNT`, `seqres.full`, `tmp`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch`; `_require_xfs_io_command "falloc" "-k"`; `_require_xfs_io_command "fzero"`; `_scratch_mkfs_sized $((1024 * 1024 * 256)) >>$seqres.full 2>&1`; `_scratch_mount`; `$XFS_IO_PROG -fc "pwrite 0 256m" -c fsync $SCRATCH_MNT/file >>$seqres.full 2>&1`; `rm -f $SCRATCH_MNT/file`; `writes a deterministic fsx replay script`; `truncate 0x0 0x1f0d6 0x380e1`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`; uses explicit sync/fsync/remount points to force persistence boundaries. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

I/O path races may be timing-sensitive and surface only under mmap, direct I/O, io_uring, or fsx replay stress. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/511.out`; success is mostly silence after prerequisite and operation checks; fsx/fsstress style stress exits cleanly and emits only filtered diagnostics. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/511 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/512 -->
# sources/test-tools/xfstests/tests/generic/512

## Purpose

Test that if we have a very small file, with a size smaller than the block size, then fallocate a very small range within the block size but past the file's current size, fsync the file and then power fail, after mounting the filesystem all the file data is there and the file size is correct.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick log prealloc`. It imports `./common/preamble`, `./common/filter`, `./common/dmflakey`. Prerequisite and skip gates include `_require_scratch`, `_require_xfs_io_command "falloc"`, `_require_dm_target flakey`, `_require_metadata_journaling $SCRATCH_DEV`. Local helper functions: `_cleanup`. External command surfaces and helper binaries visible in the source include `xfs_io`, `mount`, `od`. Important harness variables and paths include `SCRATCH_MNT`, `SCRATCH_DEV`, `seqres.full`, `tmp`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch`; `_require_xfs_io_command "falloc"`; `_require_dm_target flakey`; `_scratch_mkfs >>$seqres.full 2>&1`; `_require_metadata_journaling $SCRATCH_DEV`; `_init_flakey`; `_scratch_mount`; `$XFS_IO_PROG -f -c "pwrite -S 0xb6 0 21" -c "falloc 40 40" -c "fsync" $SCRATCH_MNT/foobar | _filter_xfs_io`; `_flakey_drop_and_remount`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`; injects block-device, power-fail, shutdown, or thin-provisioning behavior to validate recovery paths; uses explicit sync/fsync/remount points to force persistence boundaries. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

ordering bugs in journal replay or fsync logging can lose metadata or data after simulated power loss. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/512.out`; content dumps/hexdumps expose corruption or unexpected nonzero data. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/512 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/513 -->
# sources/test-tools/xfstests/tests/generic/513

## Purpose

Ensure that ctime is updated and capabilities are cleared when reflinking.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick clone`. It imports `./common/preamble`, `./common/filter`, `./common/reflink`, `./common/attr`. Prerequisite and skip gates include `_require_scratch_reflink`, `_require_command "$GETCAP_PROG" getcap`, `_require_command "$SETCAP_PROG" setcap`, `_require_attrs security`. No major local helper functions are defined; the scenario is driven directly by the top-level shell flow. External command surfaces and helper binaries visible in the source include `getcap`, `setcap`, `xfs_io`, `stat`, `sleep`. Important harness variables and paths include `SCRATCH_MNT`, `seqres.full`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch_reflink`; `_require_command "$GETCAP_PROG" getcap`; `_require_command "$SETCAP_PROG" setcap`; `_require_attrs security`; `_scratch_mkfs >>$seqres.full 2>&1`; `_scratch_mount`; `$XFS_IO_PROG -f -c "pwrite -S 0x18 0 1m" $SCRATCH_MNT/foo >>$seqres.full`; `$XFS_IO_PROG -f -c "pwrite -S 0x20 0 1m" $SCRATCH_MNT/bar >>$seqres.full`; `$SETCAP_PROG cap_setgid,cap_setuid+ep $SCRATCH_MNT/bar`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

shared extent, COW, or dedupe paths can corrupt unrelated file ranges or violate swapfile restrictions. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/513.out`; success is mostly silence after prerequisite and operation checks. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/513 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/514 -->
# sources/test-tools/xfstests/tests/generic/514

## Purpose

Ensure that file size resource limits are respected when reflinking.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick clone`. It imports `./common/preamble`, `./common/filter`, `./common/reflink`. Prerequisite and skip gates include `_require_scratch_reflink`, `_require_user`. No major local helper functions are defined; the scenario is driven directly by the top-level shell flow. External command surfaces and helper binaries visible in the source include `xfs_io`, `chmod`. Important harness variables and paths include `SCRATCH_MNT`, `seqres.full`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch_reflink`; `_require_user`; `_scratch_mkfs >>$seqres.full 2>&1`; `_scratch_mount`; `chmod a+rwx $SCRATCH_MNT`; `$XFS_IO_PROG -f -c "pwrite -S 0x18 0 1m" $SCRATCH_MNT/foo >>$seqres.full`; `_su -s/bin/bash - $qa_user -c "ulimit -f 64 ; $XFS_IO_PROG -f -c \"reflink $SCRATCH_MNT/foo\" $SCRATCH_MNT/bar" >> $seqres.full 2>&1`; `sz="$(_get_filesize $SCRATCH_MNT/bar)"`; `echo "Oddball file size $sz??"`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

shared extent, COW, or dedupe paths can corrupt unrelated file ranges or violate swapfile restrictions. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/514.out`; success is mostly silence after prerequisite and operation checks; content dumps/hexdumps expose corruption or unexpected nonzero data. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/514 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/515 -->
# sources/test-tools/xfstests/tests/generic/515

## Purpose

Ensure that reflinking into a file well beyond EOF zeroes everything between the old EOF and the start of the newly linked chunk. This is an adaptation of a reproducer script that Eric Sandeen formulated from a stale data exposure bug uncovered by shared/010.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick clone prealloc`. It imports `./common/preamble`, `./common/filter`, `./common/reflink`. Prerequisite and skip gates include `_require_scratch_reflink`, `_require_xfs_io_command "falloc"`, `_require_congruent_file_oplen $SCRATCH_MNT $blksz`. No major local helper functions are defined; the scenario is driven directly by the top-level shell flow. External command surfaces and helper binaries visible in the source include `xfs_io`, `stat`, `od`. Important harness variables and paths include `SCRATCH_MNT`, `SCRATCH_DEV`, `seqres.full`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch_reflink`; `_require_xfs_io_command "falloc"`; `$XFS_IO_PROG -c "pwrite -S 0x58 -b 1m 0 300m" $SCRATCH_DEV >> $seqres.full`; `_scratch_mkfs_sized $((300 * 1048576)) >>$seqres.full 2>&1`; `_scratch_mount`; `_require_congruent_file_oplen $SCRATCH_MNT $blksz`; `$XFS_IO_PROG -f -c "pwrite -S 0x72 0 $blksz" $DONOR1 >> $seqres.full`; `$XFS_IO_PROG -f -c "falloc -k $((blksz*2)) $blksz" -c "pwrite -S 0x57 $((blksz*16)) 8192" -c "fdatasync" -c 'stat' -c "reflink $DONOR1 0 ...`; `od -tx1 -Ad -c $TARGET >> $seqres.full`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`; uses explicit sync/fsync/remount points to force persistence boundaries. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

shared extent, COW, or dedupe paths can corrupt unrelated file ranges or violate swapfile restrictions. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/515.out`; content dumps/hexdumps expose corruption or unexpected nonzero data. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/515 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/516 -->
# sources/test-tools/xfstests/tests/generic/516

## Purpose

Ensuring that we cannot dedupe non-matching parts of files: - Fail to dedupe non-identical parts of two different files - Check that nothing changes in either file

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick dedupe clone fiemap`. It imports `./common/preamble`, `./common/filter`, `./common/reflink`. Prerequisite and skip gates include `_require_test_dedupe`, `_require_congruent_file_oplen $TEST_DIR $blksz`. Local helper functions: `_cleanup`. External command surfaces and helper binaries visible in the source include `seq`, `mkdir`, `stat`. Important harness variables and paths include `TEST_DIR`, `seqres.full`, `tmp`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_test_dedupe`; `rm -rf $testdir`; `mkdir $testdir`; `echo "Create the original files"`; `_require_congruent_file_oplen $TEST_DIR $blksz`; `_pwrite_byte 0x61 $((blksz * 2)) $((blksz * 6)) $testdir/file1 >> $seqres.full`; `_pwrite_byte 0x61 $((blksz * 2)) $((blksz * 6)) $testdir/file2 >> $seqres.full`; `_pwrite_byte 0x62 $(((blksz * 6) - 33)) 1 $testdir/file2 >> $seqres.full`; `_test_cycle_mount`.

## State and Persistence Behavior

The test uses the configured test filesystem under `TEST_DIR` without necessarily reformatting it. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

shared extent, COW, or dedupe paths can corrupt unrelated file ranges or violate swapfile restrictions. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/516.out`. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/516 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/517 -->
# sources/test-tools/xfstests/tests/generic/517

## Purpose

Test that deduplication of an entire file that has a size that is not aligned to the filesystem's block size into the middle of a different file does not corrupt the destination's file data by reflinking the last (eof) block.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick dedupe clone`. It imports `./common/preamble`, `./common/filter`, `./common/reflink`. Prerequisite and skip gates include `_require_scratch_dedupe`. No major local helper functions are defined; the scenario is driven directly by the top-level shell flow. External command surfaces and helper binaries visible in the source include `xfs_io`, `od`, `mount`. Important harness variables and paths include `SCRATCH_MNT`, `seqres.full`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch_dedupe`; `_scratch_mkfs >>$seqres.full 2>&1`; `_scratch_mount`; `$XFS_IO_PROG -f -c "pwrite -S 0x6b 0 524388" -c "pwrite -S 0xae 524388 256K" $SCRATCH_MNT/foo | _filter_xfs_io`; `$XFS_IO_PROG -f -c "pwrite -S 0x6b 0 131172" $SCRATCH_MNT/bar | _filter_xfs_io`; `echo "File content before first deduplication:"`; `od -A d -t x1 $SCRATCH_MNT/foo`; `$XFS_IO_PROG -c "dedupe $SCRATCH_MNT/bar 0 64K 131172" $SCRATCH_MNT/foo | _filter_xfs_io`; `echo "File content after first deduplication and before unmounting:"`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

shared extent, COW, or dedupe paths can corrupt unrelated file ranges or violate swapfile restrictions. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/517.out`; content dumps/hexdumps expose corruption or unexpected nonzero data. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/517 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/518 -->
# sources/test-tools/xfstests/tests/generic/518

## Purpose

Test that we can not clone a range from a file A into the middle of a file B when the range includes the last block of file A and file A's size is not aligned with the filesystem's block size. Allowing such case would lead to data corruption since the data between EOF and the end of its block is undefined.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick clone`. It imports `./common/preamble`, `./common/filter`, `./common/reflink`. Prerequisite and skip gates include `_require_scratch_reflink`. No major local helper functions are defined; the scenario is driven directly by the top-level shell flow. External command surfaces and helper binaries visible in the source include `xfs_io`, `mount`, `od`. Important harness variables and paths include `SCRATCH_MNT`, `seqres.full`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch_reflink`; `_scratch_mkfs >>$seqres.full 2>&1`; `_scratch_mount`; `foo_size=$((256 * 1024 + 100)) # 256Kb + 100 bytes`; `$XFS_IO_PROG -f -c "pwrite -S 0x3c 0 $foo_size" $SCRATCH_MNT/foo | _filter_xfs_io`; `$XFS_IO_PROG -f -c "pwrite -S 0xb5 0 $bar_size" $SCRATCH_MNT/bar | _filter_xfs_io`; `$XFS_IO_PROG -c "reflink $SCRATCH_MNT/foo 0 512K $foo_size" $SCRATCH_MNT/bar`; `_scratch_cycle_mount`; `echo "File content after failed reflink:"`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

shared extent, COW, or dedupe paths can corrupt unrelated file ranges or violate swapfile restrictions. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/518.out`; content dumps/hexdumps expose corruption or unexpected nonzero data. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/518 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/519 -->
# sources/test-tools/xfstests/tests/generic/519

## Purpose

Verify if there's physical address overlap returned by FIBMAP, cover: 79b3dbe4adb3 fs: fix iomap_bmap position calculation

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick fiemap`. It imports `./common/preamble`, `./common/filter`. Prerequisite and skip gates include `_require_scratch`, `_require_fibmap`, `_require_filefrag_options "es"`. Local helper functions: `verify_filefrag`. External command surfaces and helper binaries visible in the source include `xfs_io`, `seq`, `truncate`. Important harness variables and paths include `SCRATCH_MNT`, `seqres.full`, `tmp`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch`; `_require_fibmap`; `_require_filefrag_options "es"`; `' $tmp.filefrag`; `_scratch_mkfs > $seqres.full 2>&1`; `_scratch_mount`; `echo "== FIBMAP on empty file =="`; `$XFS_IO_PROG -f -c "truncate 0" $testfile > /dev/null`; `verify_filefrag`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

environmental skips and helper availability can dominate failures, so `_require_*` gates are part of the contract. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/519.out`. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/519 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/520 -->
# sources/test-tools/xfstests/tests/generic/520

## Purpose

Test case created by CrashMonkey Test if we create a hard link to a file and persist either of the files, all the names persist.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick log`. It imports `./common/preamble`, `./common/filter`, `./common/dmflakey`. Prerequisite and skip gates include `_require_scratch_nocheck`, `_require_dm_target flakey`, `_require_metadata_journaling $SCRATCH_DEV`. Local helper functions: `_cleanup`, `clean_dir`, `check_consistency`, `test_link_fsync`, `test_link_sync`. External command surfaces and helper binaries visible in the source include `xfs_io`, `grep`, `stat`, `mkdir`, `touch`, `ln`. Important harness variables and paths include `SCRATCH_MNT`, `SCRATCH_DEV`, `seqres.full`, `tmp`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `fssize=$((2**20 * 256))`; `_require_scratch_nocheck`; `_require_dm_target flakey`; `_scratch_mkfs_sized $fssize >> $seqres.full 2>&1`; `_require_metadata_journaling $SCRATCH_DEV`; `_init_flakey`; `stat_opt='-c "blocks: %b size: %s inode: %i links: %h"'`; `fsync_names[0]="./ foo bar"`; `fsync_names[1]="./ foo bar A A/bar A/foo"`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`; injects block-device, power-fail, shutdown, or thin-provisioning behavior to validate recovery paths; uses explicit sync/fsync/remount points to force persistence boundaries. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

ordering bugs in journal replay or fsync logging can lose metadata or data after simulated power loss. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/520.out`; grep-based checks assert expected metadata or data is still visible. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/520 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/521 -->
# sources/test-tools/xfstests/tests/generic/521

## Purpose

Long-soak directio fsx test

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest soak long_rw smoketest`. It imports `./common/preamble`, `./common/filter`. Prerequisite and skip gates include `_require_test`, `_require_odirect`. No major local helper functions are defined; the scenario is driven directly by the top-level shell flow. External command surfaces and helper binaries visible in the source include `feature`, `seq`. Important harness variables and paths include `TEST_DIR`, `seq`, `TIME_FACTOR`, `LOAD_FACTOR`, `SOAK_DURATION`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_test`; `_require_odirect`; `nr_ops=$((1000000 * TIME_FACTOR))`; `op_sz=$((128000 * LOAD_FACTOR))`; `min_dio_sz=$($here/src/feature -s)`; `fsx_args+=(-N $nr_ops)`; `fsx_args+=(-p $((nr_ops / 100)))`; `fsx_args+=(-o $op_sz)`; `fsx_args+=(-l $file_sz)`.

## State and Persistence Behavior

The test uses the configured test filesystem under `TEST_DIR` without necessarily reformatting it. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

I/O path races may be timing-sensitive and surface only under mmap, direct I/O, io_uring, or fsx replay stress. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/521.out`; success is mostly silence after prerequisite and operation checks; fsx/fsstress style stress exits cleanly and emits only filtered diagnostics. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/521 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/522 -->
# sources/test-tools/xfstests/tests/generic/522

## Purpose

Long-soak buffered fsx test

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest soak long_rw smoketest`. It imports `./common/preamble`, `./common/filter`. Prerequisite and skip gates include `_require_test`. No major local helper functions are defined; the scenario is driven directly by the top-level shell flow. External command surfaces and helper binaries visible in the source include `seq`. Important harness variables and paths include `TEST_DIR`, `seq`, `TIME_FACTOR`, `LOAD_FACTOR`, `SOAK_DURATION`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_test`; `nr_ops=$((1000000 * TIME_FACTOR))`; `op_sz=$((128000 * LOAD_FACTOR))`; `fsx_args+=(-N $nr_ops)`; `fsx_args+=(-p $((nr_ops / 100)))`; `fsx_args+=(-o $op_sz)`; `fsx_args+=(-l $file_sz)`; `test -n "$SOAK_DURATION" && fsx_args+=(--duration="$SOAK_DURATION")`; `run_fsx "${fsx_args[@]}" | sed -e '/^fsx.*/d'`.

## State and Persistence Behavior

The test uses the configured test filesystem under `TEST_DIR` without necessarily reformatting it. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

I/O path races may be timing-sensitive and surface only under mmap, direct I/O, io_uring, or fsx replay stress. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/522.out`; success is mostly silence after prerequisite and operation checks; fsx/fsstress style stress exits cleanly and emits only filtered diagnostics. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/522 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/523 -->
# sources/test-tools/xfstests/tests/generic/523

## Purpose

Check that xattrs can have slashes in their name.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick attr`. It imports `./common/preamble`, `./common/attr`, `./common/filter`. Prerequisite and skip gates include `_require_scratch`, `_require_attrs`. No major local helper functions are defined; the scenario is driven directly by the top-level shell flow. External command surfaces and helper binaries visible in the source include `setfattr`, `touch`. Important harness variables and paths include `SCRATCH_MNT`, `seqres.full`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch`; `_require_attrs`; `_scratch_mkfs >> $seqres.full 2>&1`; `_scratch_mount`; `echo "set attr"`; `touch $file`; `$SETFATTR_PROG -n "user.boo/hoo" -v "woof" $file`; `echo "check attr"`; `_getfattr -d --absolute-names $file | _filter_scratch`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

environmental skips and helper availability can dominate failures, so `_require_*` gates are part of the contract. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/523.out`. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/523 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/524 -->
# sources/test-tools/xfstests/tests/generic/524

## Purpose

Test XFS page writeback code for races with the cached file mapping. XFS caches the file -> block mapping for a full extent once it is initially looked up. The cached mapping is used for all subsequent pages in the same writeback cycle that cover the associated extent. Under certain conditions, it is possible for concurrent operations on the file to invalidate the cached mapping without the knowledge of writeback. Writeback ends up sending I/O to a partly stale mapping and potentially leaving delalloc blocks in the current mapping unconverted.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick`. It imports `./common/preamble`. Prerequisite and skip gates include `_require_scratch`, `_require_test_program "feature"`, `_require_xfs_io_command "sync_range"`. No major local helper functions are defined; the scenario is driven directly by the top-level shell flow. External command surfaces and helper binaries visible in the source include `xfs_io`, `feature`, `seq`, `truncate`, `wait`, `mount`. Important harness variables and paths include `SCRATCH_MNT`, `seqres.full`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch`; `_require_test_program "feature"`; `_require_xfs_io_command "sync_range"`; `_scratch_mkfs >> $seqres.full 2>&1 || _fail "mkfs failed"`; `_scratch_mount`; `pagesize=`$here/src/feature -s``; `truncsize=$((filesize - pagesize))`; `$XFS_IO_PROG -fc "truncate 0" $file`; `$XFS_IO_PROG -c "truncate $filesize" -c fsync $file`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`; uses explicit sync/fsync/remount points to force persistence boundaries. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

environmental skips and helper availability can dominate failures, so `_require_*` gates are part of the contract. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/524.out`; success is mostly silence after prerequisite and operation checks. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/524 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/525 -->
# sources/test-tools/xfstests/tests/generic/525

## Purpose

All Rights Reserved. Check that high-offset reads and writes work. This is a variant of test generic/466 for filesystems that do not support mkfs_sized.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick rw`. It imports `./common/preamble`, `./common/filter`. Prerequisite and skip gates include `_require_scratch`. No major local helper functions are defined; the scenario is driven directly by the top-level shell flow. External command surfaces and helper binaries visible in the source include `bc`, `xfs_io`, `truncate`. Important harness variables and paths include `SCRATCH_MNT`, `seqres.full`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch`; `_scratch_mkfs >>$seqres.full 2>&1`; `_scratch_mount`; `echo "++ Create the original files" >> $seqres.full`; `bigoff=$(echo "2^63 - 2" | $BC_PROG)`; `len=$(echo "2^63 - 1" | $BC_PROG)`; `$XFS_IO_PROG -f -c "truncate $len" $testdir/file0 >> $seqres.full 2>&1`; `_notrun "filesystem does not support huge file size"`; `_pwrite_byte 0x61 $bigoff 1 $testdir/file1 >> $seqres.full`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

I/O path races may be timing-sensitive and surface only under mmap, direct I/O, io_uring, or fsx replay stress. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/525.out`. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/525 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/526 -->
# sources/test-tools/xfstests/tests/generic/526

## Purpose

Test that after a combination of file renames, linking and creating a new file with the old name of a renamed file, if we fsync the new file, after a power failure we are able to mount the filesystem and all file names correspond to the correct inodes.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick log`. It imports `./common/preamble`, `./common/filter`, `./common/dmflakey`. Prerequisite and skip gates include `_require_scratch`, `_require_hardlinks`, `_require_dm_target flakey`, `_require_metadata_journaling $SCRATCH_DEV`. Local helper functions: `_cleanup`. External command surfaces and helper binaries visible in the source include `xfs_io`, `mount`, `mkdir`, `mv`, `ln`. Important harness variables and paths include `SCRATCH_MNT`, `SCRATCH_DEV`, `seqres.full`, `tmp`, `seq`, `FSTYP`, `MOUNT_OPTIONS`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch`; `_require_hardlinks`; `_require_dm_target flakey`; `_scratch_mkfs >>$seqres.full 2>&1`; `_require_metadata_journaling $SCRATCH_DEV`; `export MOUNT_OPTIONS="-o fsync_mode=strict $MOUNT_OPTIONS"`; `_init_flakey`; `_scratch_mount`; `mkdir $SCRATCH_MNT/testdir`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`; injects block-device, power-fail, shutdown, or thin-provisioning behavior to validate recovery paths; uses explicit sync/fsync/remount points to force persistence boundaries. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

ordering bugs in journal replay or fsync logging can lose metadata or data after simulated power loss. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/526.out`. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/526 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/527 -->
# sources/test-tools/xfstests/tests/generic/527

## Purpose

Test that after a combination of file renames, deletions, linking and creating new files with names that were previously deleted, if we fsync the new file, after a power failure we are able to mount the filesystem and all file names correspond to the correct inodes.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick log`. It imports `./common/preamble`, `./common/filter`, `./common/dmflakey`. Prerequisite and skip gates include `_require_scratch`, `_require_hardlinks`, `_require_dm_target flakey`, `_require_metadata_journaling $SCRATCH_DEV`. Local helper functions: `_cleanup`. External command surfaces and helper binaries visible in the source include `xfs_io`, `mount`, `mkdir`, `ln`, `mv`. Important harness variables and paths include `SCRATCH_MNT`, `SCRATCH_DEV`, `seqres.full`, `tmp`, `seq`, `FSTYP`, `MOUNT_OPTIONS`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch`; `_require_hardlinks`; `_require_dm_target flakey`; `_scratch_mkfs >>$seqres.full 2>&1`; `_require_metadata_journaling $SCRATCH_DEV`; `export MOUNT_OPTIONS="-o fsync_mode=strict $MOUNT_OPTIONS"`; `_init_flakey`; `_scratch_mount`; `mkdir $SCRATCH_MNT/testdir`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`; injects block-device, power-fail, shutdown, or thin-provisioning behavior to validate recovery paths; uses explicit sync/fsync/remount points to force persistence boundaries. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

ordering bugs in journal replay or fsync logging can lose metadata or data after simulated power loss. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/527.out`. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/527 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/528 -->
# sources/test-tools/xfstests/tests/generic/528

## Purpose

Check that statx btime (aka creation time) is plausibly close to when we created a file. A bug caught during code review of xfs patches revealed that there weren't any sanity checks of the btime values.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick`. It imports `./common/preamble`, `./common/attr`, `./common/filter`. Prerequisite and skip gates include `_require_test`, `_require_xfs_io_command "statx" "-r"`, `_require_btime`. Local helper functions: `_cleanup`. External command surfaces and helper binaries visible in the source include `xfs_io`, `seq`, `touch`, `grep`, `stat`. Important harness variables and paths include `TEST_DIR`, `tmp`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_test`; `_require_xfs_io_command "statx" "-r"`; `_require_btime`; `rm -f $testfile`; `now=$(date +%s)`; `touch $testfile`; `btime=$(date +%s -d "$($XFS_IO_PROG -c "statx -v -m $STATX_BTIME" $testfile | grep 'stat.btime =' | cut -d '=' -f 2)")`; `test -n "$btime" || echo "error: did not see btime in output??"`; `_within_tolerance "btime" "$btime" "$now" 1 5 -v`.

## State and Persistence Behavior

The test uses the configured test filesystem under `TEST_DIR` without necessarily reformatting it. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

environmental skips and helper availability can dominate failures, so `_require_*` gates are part of the contract. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/528.out`; grep-based checks assert expected metadata or data is still visible. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/528 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/529 -->
# sources/test-tools/xfstests/tests/generic/529

## Purpose

Regression test for a bug where XFS corrupts memory if the listxattr buffer is a particularly well crafted size on a filesystem that supports posix acls.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick acl attr`. It imports `./common/preamble`, `./common/attr`. Prerequisite and skip gates include `_require_acls`, `_require_scratch`, `_require_test_program "t_attr_corruption"`. No major local helper functions are defined; the scenario is driven directly by the top-level shell flow. External command surfaces and helper binaries visible in the source include `t_attr_corruption`. Important harness variables and paths include `SCRATCH_MNT`, `seqres.full`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_acls`; `_require_scratch`; `_require_test_program "t_attr_corruption"`; `_scratch_mkfs >> $seqres.full 2>&1`; `_scratch_mount`; `$here/src/t_attr_corruption $SCRATCH_MNT`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

environmental skips and helper availability can dominate failures, so `_require_*` gates are part of the contract. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/529.out`. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/529 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/530 -->
# sources/test-tools/xfstests/tests/generic/530

## Purpose

Stress test creating a lot of unlinked O_TMPFILE files and recovering them after a crash, checking that we don't blow up the filesystem. This is sort of a performance test for the xfs unlinked inode backref patchset, but it applies to most other filesystems. Use only a single CPU to test the single threaded situation.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick shutdown unlink`. It imports `./common/preamble`. Prerequisite and skip gates include `_require_scratch`, `_require_scratch_shutdown`, `_require_metadata_journaling`, `_require_test_program "t_open_tmpfiles"`. No major local helper functions are defined; the scenario is driven directly by the top-level shell flow. External command surfaces and helper binaries visible in the source include `t_open_tmpfiles`, `sort`, `seq`, `umount`. Important harness variables and paths include `SCRATCH_MNT`, `TEST_DIR`, `seqres.full`, `tmp`, `seq`, `LOAD_FACTOR`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch`; `_require_scratch_shutdown`; `_require_metadata_journaling`; `_require_test_program "t_open_tmpfiles"`; `_scratch_mkfs $(_scratch_mkfs_concurrency_options) >> $seqres.full 2>&1`; `_scratch_mount`; `max_files=$((50000 * LOAD_FACTOR))`; `max_allowable_files=$(( $(cat /proc/sys/fs/file-max) / 2 ))`; `test $max_allowable_files -gt 0 && test $max_files -gt $max_allowable_files && max_files=$max_allowable_files`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`; uses the configured test filesystem under `TEST_DIR` without necessarily reformatting it; injects block-device, power-fail, shutdown, or thin-provisioning behavior to validate recovery paths. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

ordering bugs in journal replay or fsync logging can lose metadata or data after simulated power loss. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/530.out`. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/530 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/531 -->
# sources/test-tools/xfstests/tests/generic/531

## Purpose

Stress test creating a lot of unlinked O_TMPFILE files and closing them all at once, checking that we don't blow up the filesystem. This is sort of a performance test for the xfs unlinked inode backref patchset, but it applies to most other filesystems. Use every CPU possible to stress the filesystem.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick unlink`. It imports `./common/preamble`. Prerequisite and skip gates include `_require_scratch`, `_require_xfs_io_command "-T"`, `_require_test_program "t_open_tmpfiles"`. No major local helper functions are defined; the scenario is driven directly by the top-level shell flow. External command surfaces and helper binaries visible in the source include `t_open_tmpfiles`, `sort`, `seq`, `mkdir`, `wait`, `umount`. Important harness variables and paths include `SCRATCH_MNT`, `TEST_DIR`, `seqres.full`, `tmp`, `seq`, `LOAD_FACTOR`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch`; `_require_xfs_io_command "-T"`; `_require_test_program "t_open_tmpfiles"`; `_scratch_mkfs $(_scratch_mkfs_concurrency_options) >> $seqres.full 2>&1`; `_scratch_mount`; `nr_cpus=$(( $(getconf _NPROCESSORS_ONLN) * 2 ))`; `max_files=$((50000 * LOAD_FACTOR))`; `max_allowable_files=$(( $(cat /proc/sys/fs/file-max) / $nr_cpus / 2 ))`; `test $max_allowable_files -gt 0 && test $max_files -gt $max_allowable_files && max_files=$max_allowable_files`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`; uses the configured test filesystem under `TEST_DIR` without necessarily reformatting it. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

environmental skips and helper availability can dominate failures, so `_require_*` gates are part of the contract. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/531.out`. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/531 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/532 -->
# sources/test-tools/xfstests/tests/generic/532

## Purpose

Regression test for a bug where XFS fails to set statx attributes_mask but sets attribute flags anyway, which is fixed by commit 1b9598c8fb99 ("xfs: fix reporting supported extra file attributes for statx()")

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick`. It imports `./common/preamble`. Prerequisite and skip gates include `_require_test`. Local helper functions: `_cleanup`, `get_attributes`, `get_attributes_mask`, `check_statx_attributes`. External command surfaces and helper binaries visible in the source include `xfs_io`, `chattr`, `grep`, `stat`, `seq`, `touch`. Important harness variables and paths include `TEST_DIR`, `seqres.full`, `tmp`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_test`; `echo "Silence is golden"`; `touch $testfile`; `check_statx_attributes`; `check_statx_attributes`; `$CHATTR_PROG -i $testfile`; `check_statx_attributes`; `$CHATTR_PROG -a $testfile`.

## State and Persistence Behavior

The test uses the configured test filesystem under `TEST_DIR` without necessarily reformatting it. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

environmental skips and helper availability can dominate failures, so `_require_*` gates are part of the contract. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/532.out`; success is mostly silence after prerequisite and operation checks; grep-based checks assert expected metadata or data is still visible. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/532 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/533 -->
# sources/test-tools/xfstests/tests/generic/533

## Purpose

FS QA Test No. 526. Simple attr smoke tests for user EAs, dereived from generic/097.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick attr`. It imports `./common/preamble`, `./common/attr`, `./common/filter`. Prerequisite and skip gates include `_require_test`, `_require_attrs`. Local helper functions: `getfattr`, `setfattr`. External command surfaces and helper binaries visible in the source include `setfattr`, `seq`, `touch`, `umount`, `mount`. Important harness variables and paths include `TEST_DIR`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_test`; `_require_attrs`; `echo -e "\ncreate file foo.$seq"`; `rm -f $file`; `touch $file`; `echo -e "\nshould be no EAs for foo.$seq:"`; `getfattr -d $file`; `echo -e "\nset EA <NOISE,woof>:"`; `setfattr -n user.NOISE -v woof $file`.

## State and Persistence Behavior

The test uses the configured test filesystem under `TEST_DIR` without necessarily reformatting it. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

environmental skips and helper availability can dominate failures, so `_require_*` gates are part of the contract. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/533.out`. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/533 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/534 -->
# sources/test-tools/xfstests/tests/generic/534

## Purpose

Test that if we truncate a file to reduce its size, rename it and then fsync it, after a power failure the file has a correct size and name.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick log`. It imports `./common/preamble`, `./common/filter`, `./common/dmflakey`. Prerequisite and skip gates include `_require_scratch`, `_require_dm_target flakey`, `_require_metadata_journaling $SCRATCH_DEV`. Local helper functions: `_cleanup`. External command surfaces and helper binaries visible in the source include `xfs_io`, `truncate`, `mv`, `mount`, `od`. Important harness variables and paths include `SCRATCH_MNT`, `SCRATCH_DEV`, `seqres.full`, `tmp`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch`; `_require_dm_target flakey`; `_scratch_mkfs >>$seqres.full 2>&1`; `_require_metadata_journaling $SCRATCH_DEV`; `_init_flakey`; `_scratch_mount`; `$XFS_IO_PROG -f -c "pwrite -S 0xab 0 8000" -c "fsync" -c "truncate 3000" $SCRATCH_MNT/foo | _filter_xfs_io`; `mv $SCRATCH_MNT/foo $SCRATCH_MNT/bar`; `$XFS_IO_PROG -c "fsync" $SCRATCH_MNT/bar`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`; injects block-device, power-fail, shutdown, or thin-provisioning behavior to validate recovery paths; uses explicit sync/fsync/remount points to force persistence boundaries. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

ordering bugs in journal replay or fsync logging can lose metadata or data after simulated power loss. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/534.out`; content dumps/hexdumps expose corruption or unexpected nonzero data. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/534 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/535 -->
# sources/test-tools/xfstests/tests/generic/535

## Purpose

This testcase is trying to test recovery flow of generic filesystem, w/ below steps, once i_mode changes, after we fsync that file, we can expect that i_mode can be recovered after sudden power-cuts. 1. touch testfile or mkdir testdir 2. chmod 777 testfile/testdir 3. sync 4. chmod 755 testfile/testdir 5. fsync testfile/testdir 6. record last i_mode 7. flakey drop 8. remount 9. check i_mode

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick log`. It imports `./common/preamble`, `./common/filter`, `./common/dmflakey`. Prerequisite and skip gates include `_require_scratch`, `_require_dm_target flakey`, `_require_metadata_journaling $SCRATCH_DEV`. Local helper functions: `_cleanup`, `do_check`. External command surfaces and helper binaries visible in the source include `xfs_io`, `touch`, `mkdir`, `chmod`, `stat`. Important harness variables and paths include `SCRATCH_MNT`, `SCRATCH_DEV`, `seqres.full`, `tmp`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch`; `_require_dm_target flakey`; `_scratch_mkfs >/dev/null 2>&1`; `_require_metadata_journaling $SCRATCH_DEV`; `_init_flakey`; `echo "Silence is golden"`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`; injects block-device, power-fail, shutdown, or thin-provisioning behavior to validate recovery paths; uses explicit sync/fsync/remount points to force persistence boundaries. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

ordering bugs in journal replay or fsync logging can lose metadata or data after simulated power loss. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/535.out`; success is mostly silence after prerequisite and operation checks; content dumps/hexdumps expose corruption or unexpected nonzero data. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/535 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/536 -->
# sources/test-tools/xfstests/tests/generic/536

## Purpose

Test a some write patterns for stale data exposure after a crash. XFS is historically susceptible to this problem in the window between delalloc to physical extent conversion and writeback completion.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick rw shutdown`. It imports `./common/preamble`. Prerequisite and skip gates include `_require_scratch`, `_require_scratch_shutdown`, `_require_metadata_journaling`. No major local helper functions are defined; the scenario is driven directly by the top-level shell flow. External command surfaces and helper binaries visible in the source include `xfs_io`, `grep`. Important harness variables and paths include `SCRATCH_MNT`, `seqres.full`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch`; `_require_scratch_shutdown`; `_require_metadata_journaling`; `_scratch_mkfs_sized $((1024 * 1024 * 100)) >> $seqres.full 2>&1`; `_scratch_mount`; `$XFS_IO_PROG -f -c "pwrite -S 0xab 0 100m" -c fsync $SCRATCH_MNT/spc >> $seqres.full 2>&1`; `rm -f $SCRATCH_MNT/spc`; `$XFS_IO_PROG -c fsync $SCRATCH_MNT`; `$XFS_IO_PROG -fc "pwrite 0 256k" -c "sync_range -w 252k 4k" -c "sync_range -a 252k 4k" $SCRATCH_MNT/file.1 >> $seqres.full 2>&1`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`; injects block-device, power-fail, shutdown, or thin-provisioning behavior to validate recovery paths; uses explicit sync/fsync/remount points to force persistence boundaries. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

ordering bugs in journal replay or fsync logging can lose metadata or data after simulated power loss; I/O path races may be timing-sensitive and surface only under mmap, direct I/O, io_uring, or fsx replay stress. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/536.out`; content dumps/hexdumps expose corruption or unexpected nonzero data; grep-based checks assert expected metadata or data is still visible. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/536 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/537 -->
# sources/test-tools/xfstests/tests/generic/537

## Purpose

Ensure that we can't call fstrim on filesystems mounted norecovery, because FSTRIM implementations use free space metadata to drive the discard requests and we told the filesystem not to make sure the metadata are up to date. The following patches fixed the bug on ext4, xfs and btrfs ext4: prohibit fstrim in norecovery mode xfs: prohibit fstrim in norecovery mode Btrfs: do not allow trimming when a fs is mounted with the nologreplay option

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick trim`. It imports `./common/preamble`, `./common/filter`, `./common/quota`. Prerequisite and skip gates include `_require_scratch`, `_require_fstrim`, `_require_metadata_journaling $SCRATCH_DEV`. No major local helper functions are defined; the scenario is driven directly by the top-level shell flow. External command surfaces and helper binaries visible in the source include `fstrim`, `mount`. Important harness variables and paths include `SCRATCH_MNT`, `SCRATCH_DEV`, `seqres.full`, `seq`, `FSTYP`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch`; `_require_fstrim`; `_scratch_mkfs > $seqres.full 2>&1`; `_require_metadata_journaling $SCRATCH_DEV`; `echo "fstrim on regular mount"`; `_scratch_mount >> $seqres.full 2>&1`; `$FSTRIM_PROG -v $SCRATCH_MNT >> $seqres.full 2>&1 || _notrun "FSTRIM not supported"`; `_scratch_unmount`; `echo "fstrim on ro mount"`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`; enables quota accounting/enforcement state and adjusts grace timers or ownership/project metadata. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

environmental skips and helper availability can dominate failures, so `_require_*` gates are part of the contract. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/537.out`; grep-based checks assert expected metadata or data is still visible. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/537 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/538 -->
# sources/test-tools/xfstests/tests/generic/538

## Purpose

Non-block-aligned direct AIO write test with an initial truncate i_size. Uncover "ext4: Fix data corruption caused by unaligned direct AIO": (Ext4 needs to serialize unaligned direct AIO because the zeroing of partial blocks of two competing unaligned AIOs can result in data corruption. However it decides not to serialize if the potentially unaligned aio is past i_size with the rationale that no pending writes are possible past i_size. Unfortunately if the i_size is not block aligned and the second unaligned write lands past i_size, but still into the same block, it has the potential of corrupting the previous unaligned write to the same block.)

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick aio`. It imports `./common/preamble`, `./common/filter`. Prerequisite and skip gates include `_require_test`, `_require_aiodio aio-dio-write-verify`. No major local helper functions are defined; the scenario is driven directly by the top-level shell flow. External command surfaces and helper binaries visible in the source include `min_dio_alignment`, `truncate`, `seq`. Important harness variables and paths include `TEST_DIR`, `TEST_DEV`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_test`; `_require_aiodio aio-dio-write-verify`; `diosize=`$here/src/min_dio_alignment $TEST_DIR $TEST_DEV``; `blocksize=`_get_block_size $TEST_DIR``; `bufsize=$((blocksize * 2))`; `truncsize=$((bufsize+diosize))`; `_notrun "Need device logical block size($diosize) < fs block size($blocksize)"`; `rm -rf $localfile 2>/dev/null`; `$AIO_TEST -a size=$bufsize,off=0 -a size=$bufsize,off=$bufsize $localfile`.

## State and Persistence Behavior

The test uses the configured test filesystem under `TEST_DIR` without necessarily reformatting it. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

environmental skips and helper availability can dominate failures, so `_require_*` gates are part of the contract. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/538.out`; success is mostly silence after prerequisite and operation checks. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/538 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/539 -->
# sources/test-tools/xfstests/tests/generic/539

## Purpose

Check that SEEK_HOLE can find a punched hole.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick punch seek`. It imports `./common/preamble`. Prerequisite and skip gates include `_require_test`, `_require_seek_data_hole`, `_require_xfs_io_command "fpunch"`, `_require_test_program "seek_sanity_test"`. Local helper functions: `_cleanup`. External command surfaces and helper binaries visible in the source include `seq`. Important harness variables and paths include `TEST_DIR`, `seqres.full`, `tmp`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_test`; `_require_seek_data_hole`; `_require_xfs_io_command "fpunch"`; `_require_test_program "seek_sanity_test"`; `echo "Silence is golden"`; `_run_seek_sanity_test -s 21 -e 21 $base_test_file > $seqres.full 2>&1 ||`; `_fail "seek sanity check failed!"`.

## State and Persistence Behavior

The test uses the configured test filesystem under `TEST_DIR` without necessarily reformatting it. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

environmental skips and helper availability can dominate failures, so `_require_*` gates are part of the contract. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/539.out`; success is mostly silence after prerequisite and operation checks. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/539 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/540 -->
# sources/test-tools/xfstests/tests/generic/540

## Purpose

Ensuring that reflinking works when the destination range covers multiple extents, some unwritten, some not: - Create a file with the following repeating sequence of blocks: 1. reflinked 2. unwritten 3. hole 4. regular block 5. delalloc - reflink across the halfway mark, starting with the unwritten extent. - Check that the files are now different where we say they're different.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick clone fiemap prealloc`. It imports `./common/preamble`, `./common/filter`, `./common/reflink`. Prerequisite and skip gates include `_require_scratch_reflink`, `_require_scratch_delalloc`, `_require_xfs_io_command "falloc"`, `_require_congruent_file_oplen $SCRATCH_MNT $blksz`. No major local helper functions are defined; the scenario is driven directly by the top-level shell flow. External command surfaces and helper binaries visible in the source include `filefrag`, `xfs_io`, `mount`, `seq`, `mkdir`. Important harness variables and paths include `SCRATCH_MNT`, `seqres.full`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch_reflink`; `_require_scratch_delalloc`; `_require_xfs_io_command "falloc"`; `echo "Format and mount"`; `_scratch_mkfs > $seqres.full 2>&1`; `_scratch_mount >> $seqres.full 2>&1`; `mkdir $testdir`; `echo "Create the original files"`; `_require_congruent_file_oplen $SCRATCH_MNT $blksz`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

shared extent, COW, or dedupe paths can corrupt unrelated file ranges or violate swapfile restrictions. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/540.out`. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/540 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/541 -->
# sources/test-tools/xfstests/tests/generic/541

## Purpose

Ensuring that reflinking works when the source range covers multiple extents, some unwritten, some not: - Create a file with the following repeating sequence of blocks: 1. reflinked 2. unwritten 3. hole 4. regular block 5. delalloc - reflink across the halfway mark, starting with the unwritten extent. - Check that the files are now different where we say they're different.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick clone fiemap prealloc`. It imports `./common/preamble`, `./common/filter`, `./common/reflink`. Prerequisite and skip gates include `_require_scratch_reflink`, `_require_scratch_delalloc`, `_require_xfs_io_command "falloc"`, `_require_congruent_file_oplen $SCRATCH_MNT $blksz`. No major local helper functions are defined; the scenario is driven directly by the top-level shell flow. External command surfaces and helper binaries visible in the source include `filefrag`, `xfs_io`, `mount`, `seq`, `mkdir`, `cp`. Important harness variables and paths include `SCRATCH_MNT`, `seqres.full`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch_reflink`; `_require_scratch_delalloc`; `_require_xfs_io_command "falloc"`; `echo "Format and mount"`; `_scratch_mkfs > $seqres.full 2>&1`; `_scratch_mount >> $seqres.full 2>&1`; `mkdir $testdir`; `echo "Create the original files"`; `_require_congruent_file_oplen $SCRATCH_MNT $blksz`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

shared extent, COW, or dedupe paths can corrupt unrelated file ranges or violate swapfile restrictions. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/541.out`. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/541 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/542 -->
# sources/test-tools/xfstests/tests/generic/542

## Purpose

Ensuring that reflinking works when the destination range covers multiple extents, some unwritten, some not: - Create a file with the following repeating sequence of blocks: 1. reflinked 2. unwritten 3. hole 4. regular block 5. delalloc - reflink across the halfway mark, starting with the unwritten extent. - Check that the files are now different where we say they're different.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick clone fiemap prealloc`. It imports `./common/preamble`, `./common/filter`, `./common/reflink`. Prerequisite and skip gates include `_require_scratch_reflink`, `_require_scratch_delalloc`, `_require_xfs_io_command "falloc"`, `_require_congruent_file_oplen $SCRATCH_MNT $blksz`. No major local helper functions are defined; the scenario is driven directly by the top-level shell flow. External command surfaces and helper binaries visible in the source include `filefrag`, `xfs_io`, `mount`, `seq`, `mkdir`. Important harness variables and paths include `SCRATCH_MNT`, `seqres.full`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch_reflink`; `_require_scratch_delalloc`; `_require_xfs_io_command "falloc"`; `echo "Format and mount"`; `_scratch_mkfs > $seqres.full 2>&1`; `_scratch_mount >> $seqres.full 2>&1`; `mkdir $testdir`; `echo "Create the original files"`; `_require_congruent_file_oplen $SCRATCH_MNT $blksz`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

shared extent, COW, or dedupe paths can corrupt unrelated file ranges or violate swapfile restrictions. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/542.out`. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/542 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/543 -->
# sources/test-tools/xfstests/tests/generic/543

## Purpose

Ensuring that reflinking works when the source range covers multiple extents, some unwritten, some not: - Create a file with the following repeating sequence of blocks: 1. reflinked 2. unwritten 3. hole 4. regular block 5. delalloc - reflink across the halfway mark, starting with the unwritten extent. - Check that the files are now different where we say they're different.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick clone fiemap prealloc`. It imports `./common/preamble`, `./common/filter`, `./common/reflink`. Prerequisite and skip gates include `_require_scratch_reflink`, `_require_scratch_delalloc`, `_require_xfs_io_command "falloc"`, `_require_congruent_file_oplen $SCRATCH_MNT $blksz`. No major local helper functions are defined; the scenario is driven directly by the top-level shell flow. External command surfaces and helper binaries visible in the source include `filefrag`, `xfs_io`, `mount`, `seq`, `mkdir`, `truncate`. Important harness variables and paths include `SCRATCH_MNT`, `seqres.full`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch_reflink`; `_require_scratch_delalloc`; `_require_xfs_io_command "falloc"`; `echo "Format and mount"`; `_scratch_mkfs > $seqres.full 2>&1`; `_scratch_mount >> $seqres.full 2>&1`; `mkdir $testdir`; `echo "Create the original files"`; `_require_congruent_file_oplen $SCRATCH_MNT $blksz`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

shared extent, COW, or dedupe paths can corrupt unrelated file ranges or violate swapfile restrictions. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/543.out`. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/543 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/544 -->
# sources/test-tools/xfstests/tests/generic/544

## Purpose

Ensure that we can reflink from a file with a higher inode number to a lower inode number and vice versa. Mix it up by doing this test with inodes that already share blocks and inodes that don't share blocks. This tests both double-inode locking order correctness as well as stressing things like ocfs2 which have per-inode sharing groups and therefore have to check that we don't try to link data between disjoint sharing groups.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick clone`. It imports `./common/preamble`, `./common/filter`, `./common/reflink`. Prerequisite and skip gates include `_require_scratch_reflink`, `_require_cp_reflink`, `_require_congruent_file_oplen $SCRATCH_MNT $blksz`. Local helper functions: `inum`, `create_files`, `check_files`, `test_files`, `dummy_share`, `mutual_dummy_share`, `ann`. External command surfaces and helper binaries visible in the source include `mount`, `seq`, `mkdir`, `stat`, `touch`, `mv`. Important harness variables and paths include `SCRATCH_MNT`, `seqres.full`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch_reflink`; `_require_cp_reflink`; `echo "Format and mount"`; `_scratch_mkfs > $seqres.full 2>&1`; `_scratch_mount >> $seqres.full 2>&1`; `_require_congruent_file_oplen $SCRATCH_MNT $blksz`; `mkdir $testdir`; `ann "low to high, neither share"`; `create_files`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

shared extent, COW, or dedupe paths can corrupt unrelated file ranges or violate swapfile restrictions. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/544.out`. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/544 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/545 -->
# sources/test-tools/xfstests/tests/generic/545

## Purpose

Check that we can't set the FS_APPEND_FL and FS_IMMUTABLE_FL inode flags without capbility CAP_LINUX_IMMUTABLE

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick cap`. It imports `./common/preamble`, `./common/filter`, `./common/attr`. Prerequisite and skip gates include `_require_test`, `_require_chattr i`, `_require_chattr a`, `_require_command "$CAPSH_PROG" "capsh"`. Local helper functions: `_cleanup`, `do_filter_output`. External command surfaces and helper binaries visible in the source include `chattr`, `capsh`, `seq`, `mkdir`, `touch`, `grep`. Important harness variables and paths include `TEST_DIR`, `tmp`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_test`; `_require_chattr i`; `_require_chattr a`; `_require_command "$CAPSH_PROG" "capsh"`; `rm -rf $workdir`; `mkdir $workdir`; `echo "Create the original files"`; `touch $workdir/file1`; `touch $workdir/file2`.

## State and Persistence Behavior

The test uses the configured test filesystem under `TEST_DIR` without necessarily reformatting it. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

environmental skips and helper availability can dominate failures, so `_require_*` gates are part of the contract. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/545.out`; grep-based checks assert expected metadata or data is still visible. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/545 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/546 -->
# sources/test-tools/xfstests/tests/generic/546

## Purpose

Test when a fs is full we can still: - Do buffered write into a unpopulated preallocated extent - Clone the untouched part of that preallocated extent - Fsync - No data loss even power loss happens after fsync All operations above should not fail.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick clone enospc log prealloc`. It imports `./common/preamble`, `./common/filter`, `./common/reflink`, `./common/dmflakey`. Prerequisite and skip gates include `_require_xfs_io_command "falloc"`, `_require_scratch_reflink`, `_require_dm_target flakey`, `_require_metadata_journaling $SCRATCH_DEV`, `_require_congruent_file_oplen $SCRATCH_MNT 4096`. Local helper functions: `_cleanup`. External command surfaces and helper binaries visible in the source include `xfs_io`. Important harness variables and paths include `SCRATCH_MNT`, `SCRATCH_DEV`, `seqres.full`, `tmp`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_xfs_io_command "falloc"`; `_require_scratch_reflink`; `_require_dm_target flakey`; `_scratch_mkfs_sized $((512 * 1024 * 1024)) >> $seqres.full 2>&1`; `_require_metadata_journaling $SCRATCH_DEV`; `_init_flakey`; `_scratch_mount`; `_require_congruent_file_oplen $SCRATCH_MNT 4096`; `$XFS_IO_PROG -f -c 'falloc 8k 64m' "$SCRATCH_MNT/foobar" >> $seqres.full`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`; injects block-device, power-fail, shutdown, or thin-provisioning behavior to validate recovery paths; uses explicit sync/fsync/remount points to force persistence boundaries. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

ordering bugs in journal replay or fsync logging can lose metadata or data after simulated power loss; shared extent, COW, or dedupe paths can corrupt unrelated file ranges or violate swapfile restrictions. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/546.out`. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/546 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/547 -->
# sources/test-tools/xfstests/tests/generic/547

## Purpose

Run fsstress, fsync every file and directory, simulate a power failure and then verify that all files and directories exist, with the same data and metadata they had before the power failure.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick log`. It imports `./common/preamble`, `./common/filter`, `./common/dmflakey`. Prerequisite and skip gates include `_require_test`, `_require_scratch`, `_require_fssum`, `_require_dm_target flakey`, `_require_metadata_journaling $SCRATCH_DEV`. Local helper functions: `_cleanup`. External command surfaces and helper binaries visible in the source include `xfs_io`, `fssum`, `fsstress`, `seq`, `mkdir`, `mount`. Important harness variables and paths include `SCRATCH_MNT`, `SCRATCH_DEV`, `TEST_DIR`, `seqres.full`, `tmp`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_test`; `_require_scratch`; `_require_fssum`; `_require_dm_target flakey`; `rm -fr $fssum_files_dir`; `mkdir $fssum_files_dir`; `_scratch_mkfs >>$seqres.full 2>&1`; `_require_metadata_journaling $SCRATCH_DEV`; `_init_flakey`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`; uses the configured test filesystem under `TEST_DIR` without necessarily reformatting it; injects block-device, power-fail, shutdown, or thin-provisioning behavior to validate recovery paths; uses explicit sync/fsync/remount points to force persistence boundaries. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

ordering bugs in journal replay or fsync logging can lose metadata or data after simulated power loss. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/547.out`; fssum before/after comparison validates tree integrity. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/547 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/548 -->
# sources/test-tools/xfstests/tests/generic/548

## Purpose

Verify ciphertext for v1 encryption policies that use AES-256-XTS to encrypt file contents and AES-256-CTS-CBC to encrypt file names.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick encrypt`. It imports `./common/preamble`, `./common/filter`, `./common/encrypt`. Prerequisite and skip gates include feature gates are delegated to sourced helpers or nested helper routines. No major local helper functions are defined; the scenario is driven directly by the top-level shell flow. External command surfaces and helper binaries visible in the source include standard shell utilities plus xfstests helper functions. Important harness variables and paths include the standard xfstests environment variables.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_verify_ciphertext_for_encryption_policy AES-256-XTS AES-256-CTS-CBC`.

## State and Persistence Behavior

The test creates encrypted directories/files and manipulates fscrypt keys or nonce/ciphertext metadata. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

fscrypt policy/key support and raw metadata inspection differ across filesystems and kernel versions. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/548.out`. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/548 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/549 -->
# sources/test-tools/xfstests/tests/generic/549

## Purpose

Verify ciphertext for v1 encryption policies that use AES-128-CBC-ESSIV to encrypt file contents and AES-128-CTS-CBC to encrypt file names.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick encrypt`. It imports `./common/preamble`, `./common/filter`, `./common/encrypt`. Prerequisite and skip gates include feature gates are delegated to sourced helpers or nested helper routines. No major local helper functions are defined; the scenario is driven directly by the top-level shell flow. External command surfaces and helper binaries visible in the source include standard shell utilities plus xfstests helper functions. Important harness variables and paths include the standard xfstests environment variables.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_verify_ciphertext_for_encryption_policy AES-128-CBC-ESSIV AES-128-CTS-CBC`.

## State and Persistence Behavior

The test creates encrypted directories/files and manipulates fscrypt keys or nonce/ciphertext metadata. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

fscrypt policy/key support and raw metadata inspection differ across filesystems and kernel versions. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/549.out`. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/549 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/550 -->
# sources/test-tools/xfstests/tests/generic/550

## Purpose

Verify ciphertext for v1 encryption policies that use Adiantum to encrypt file contents and file names.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick encrypt`. It imports `./common/preamble`, `./common/filter`, `./common/encrypt`. Prerequisite and skip gates include feature gates are delegated to sourced helpers or nested helper routines. No major local helper functions are defined; the scenario is driven directly by the top-level shell flow. External command surfaces and helper binaries visible in the source include standard shell utilities plus xfstests helper functions. Important harness variables and paths include the standard xfstests environment variables.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_verify_ciphertext_for_encryption_policy Adiantum Adiantum`; `_verify_ciphertext_for_encryption_policy Adiantum Adiantum direct`.

## State and Persistence Behavior

The test creates encrypted directories/files and manipulates fscrypt keys or nonce/ciphertext metadata. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

fscrypt policy/key support and raw metadata inspection differ across filesystems and kernel versions. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/550.out`. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/550 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/551 -->
# sources/test-tools/xfstests/tests/generic/551

## Purpose

Randomly direct AIO write&verify stress test

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto stress aio`. It imports `./common/preamble`, `./common/filter`. Prerequisite and skip gates include `_require_scratch`, `_require_aiodio aio-dio-write-verify`. Local helper functions: `do_test`. External command surfaces and helper binaries visible in the source include `min_dio_alignment`, `grep`. Important harness variables and paths include `SCRATCH_MNT`, `SCRATCH_DEV`, `seqres.full`, `tmp`, `seq`, `FSTYP`, `LOAD_FACTOR`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch`; `_require_aiodio aio-dio-write-verify`; `_scratch_mkfs > $seqres.full 2>&1`; `_scratch_mount`; `diosize=`$here/src/min_dio_alignment $SCRATCH_MNT $SCRATCH_DEV``; `free_size_k=`df -kP $SCRATCH_MNT | grep -v Filesystem | awk '{print $4}'``; `max_io_size_b=$((32 * 1024))`; `max_io_size_b=$((free_size_k * 1024 / 2 / diosize))`; `testimes=$((LOAD_FACTOR * 100))`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

environmental skips and helper availability can dominate failures, so `_require_*` gates are part of the contract. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/551.out`; success is mostly silence after prerequisite and operation checks; grep-based checks assert expected metadata or data is still visible. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/551 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/552 -->
# sources/test-tools/xfstests/tests/generic/552

## Purpose

Check that if we write some data to a file, its inode gets evicted (while its parent directory's inode is not evicted due to being in use), then we rename the file and fsync it, after a power failure the file data is not lost.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick log`. It imports `./common/preamble`, `./common/filter`, `./common/dmflakey`. Prerequisite and skip gates include `_require_scratch`, `_require_odirect`, `_require_dm_target flakey`, `_require_metadata_journaling $SCRATCH_DEV`. Local helper functions: `_cleanup`. External command surfaces and helper binaries visible in the source include `xfs_io`, `mkdir`, `touch`, `sleep`, `mv`, `kill`, `wait`, `od`. Important harness variables and paths include `SCRATCH_MNT`, `SCRATCH_DEV`, `seqres.full`, `tmp`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch`; `_require_odirect`; `_require_dm_target flakey`; `_scratch_mkfs >>$seqres.full 2>&1`; `_require_metadata_journaling $SCRATCH_DEV`; `_init_flakey`; `_scratch_mount`; `mkdir $SCRATCH_MNT/dir`; `touch $SCRATCH_MNT/dir/foo`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`; injects block-device, power-fail, shutdown, or thin-provisioning behavior to validate recovery paths; uses explicit sync/fsync/remount points to force persistence boundaries. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

ordering bugs in journal replay or fsync logging can lose metadata or data after simulated power loss. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/552.out`; content dumps/hexdumps expose corruption or unexpected nonzero data. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/552 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/553 -->
# sources/test-tools/xfstests/tests/generic/553

## Purpose

Check that we cannot copy_file_range() to an immutable file This is a regression test for kernel commit: 96e6e8f4a68d ("vfs: add missing checks to copy_file_range")

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick copy_range`. It imports `./common/preamble`, `./common/filter`. Prerequisite and skip gates include `_require_test`, `_require_xfs_io_command "copy_range"`, `_require_xfs_io_command "chattr" "i"`. Local helper functions: `_cleanup`. External command surfaces and helper binaries visible in the source include `xfs_io`, `seq`, `mkdir`. Important harness variables and paths include `TEST_DIR`, `seqres.full`, `tmp`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_register_cleanup "_cleanup" BUS`; `_require_test`; `_require_xfs_io_command "copy_range"`; `_require_xfs_io_command "chattr" "i"`; `rm -rf $workdir`; `mkdir $workdir`; `$XFS_IO_PROG -f -c "pwrite -S 0x61 0 128k" $workdir/file >> $seqres.full 2>&1`; `echo immutable file returns EPERM`; `$XFS_IO_PROG -f -c "pwrite -S 0x61 0 64k" -c fsync $workdir/immutable | _filter_xfs_io`.

## State and Persistence Behavior

The test uses the configured test filesystem under `TEST_DIR` without necessarily reformatting it; uses explicit sync/fsync/remount points to force persistence boundaries. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

environmental skips and helper availability can dominate failures, so `_require_*` gates are part of the contract. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/553.out`. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/553 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/554 -->
# sources/test-tools/xfstests/tests/generic/554

## Purpose

Check that we cannot copy_file_range() to a swapfile This is a regression test for kernel commit: 96e6e8f4a68d ("vfs: add missing checks to copy_file_range")

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick copy_range swap`. It imports `./common/preamble`, `./common/filter`. Prerequisite and skip gates include `_require_scratch`, `_require_xfs_io_command "copy_range"`, `_require_scratch_swapfile`. No major local helper functions are defined; the scenario is driven directly by the top-level shell flow. External command surfaces and helper binaries visible in the source include `xfs_io`, `swapoff`. Important harness variables and paths include `SCRATCH_MNT`, `seqres.full`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_register_cleanup "_cleanup" BUS`; `_require_scratch`; `_require_xfs_io_command "copy_range"`; `_require_scratch_swapfile`; `_scratch_mkfs >>$seqres.full 2>&1`; `_scratch_mount`; `$XFS_IO_PROG -f -c "pwrite -S 0x61 0 128k" $SCRATCH_MNT/file >> $seqres.full 2>&1`; `echo swap files return ETXTBUSY`; `_format_swapfile $SCRATCH_MNT/swapfile 16m > /dev/null`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`; temporarily activates swap files and must clean them with `swapoff`. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

active swapfiles must reject extent-changing operations and require page-size/block-size compatibility. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/554.out`. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/554 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/555 -->
# sources/test-tools/xfstests/tests/generic/555

## Purpose

Check that we can't set FS_XFLAG_APPEND and FS_XFLAG_IMMUTABLE inode flags without capbility CAP_LINUX_IMMUTABLE. This test uses xfs_io chattr, rather than the (e2fsprogs) chattr program to exercise the FS_IOC_FSSETXATTR ioctl.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick cap`. It imports `./common/preamble`, `./common/filter`, `./common/attr`. Prerequisite and skip gates include `_require_test`, `_require_xfs_io_command "chattr" "ia"`, `_require_command "$CAPSH_PROG" "capsh"`. Local helper functions: `_cleanup`, `do_filter_output`. External command surfaces and helper binaries visible in the source include `xfs_io`, `capsh`, `seq`, `mkdir`, `touch`, `grep`. Important harness variables and paths include `TEST_DIR`, `tmp`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_test`; `_require_xfs_io_command "chattr" "ia"`; `_require_command "$CAPSH_PROG" "capsh"`; `rm -rf $workdir`; `mkdir $workdir`; `echo "Create the original files"`; `touch $workdir/file1`; `touch $workdir/file2`; `echo "Try to xfs_io chattr +ia with capabilities CAP_LINUX_IMMUTABLE"`.

## State and Persistence Behavior

The test uses the configured test filesystem under `TEST_DIR` without necessarily reformatting it. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

environmental skips and helper availability can dominate failures, so `_require_*` gates are part of the contract. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/555.out`; grep-based checks assert expected metadata or data is still visible. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/555 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/556 -->
# sources/test-tools/xfstests/tests/generic/556

## Purpose

Test the basic functionality of filesystems with case-insensitive support.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick casefold`. It imports `./common/preamble`, `./common/filter`, `./common/casefold`, `./common/attr`. Prerequisite and skip gates include `_require_scratch_nocheck`, `_require_scratch_casefold`, `_require_symlinks`, `_require_check_dmesg`, `_require_attrs`. Local helper functions: `filter_touch`, `basic_create_lookup`, `bad_basic_create_lookup`, `test_casefold_lookup`, `test_bad_casefold_lookup`, `do_create_and_remove`, `test_create_and_remove`, `test_casefold_flag_basic`, `test_casefold_flag_removal`, `test_casefold_flag_inheritance`, `test_nesting_sensitive_insensitive_tree_simple`, `test_nesting_sensitive_insensitive_tree_complex`, `test_symlink_with_inexact_name`, `do_test_name_preserve`, `test_name_preserve`, `do_test_dir_name_preserve`, `test_dir_name_preserve`, `test_name_reuse`, `test_create_with_same_name`, `test_file_rename`, `test_toplevel_dir_rename`, `test_casefold_openfd`, `test_casefold_openfd2`, `test_hard_link_lookups`, `test_xattrs_lookups`, `test_lookup_large_directory`, `test_strict_mode_invalid_filename`. External command surfaces and helper binaries visible in the source include `touch`, `mkdir`, `ln`, `mv`, `stat`, `seq`, `mount`. Important harness variables and paths include `SCRATCH_MNT`, `SCRATCH_DEV`, `seqres.full`, `tmp`, `seq`, `FSTYP`, `MOUNT_OPTIONS`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch_nocheck`; `_require_scratch_casefold`; `_require_symlinks`; `_require_check_dmesg`; `_require_attrs`; `sdev="\($(_short_dev ${SCRATCH_DEV})\)"`; `pt_file1=$(echo -e "coração")`; `pt_file2=$(echo -e "corac\xcc\xa7\xc3\xa3o" | tr a-z A-Z)`; `fr_file2=$(echo -e "french_caf\xc3\xa9.txt")`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`; uses explicit sync/fsync/remount points to force persistence boundaries. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

environmental skips and helper availability can dominate failures, so `_require_*` gates are part of the contract. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/556.out`. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/556 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/557 -->
# sources/test-tools/xfstests/tests/generic/557

## Purpose

Test that if we fsync a file, evict its inode, unlink it and then fsync its parent directory, after a power failure the file does not exists.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick log`. It imports `./common/preamble`, `./common/filter`, `./common/dmflakey`. Prerequisite and skip gates include `_require_scratch`, `_require_dm_target flakey`, `_require_metadata_journaling $SCRATCH_DEV`. Local helper functions: `_cleanup`. External command surfaces and helper binaries visible in the source include `xfs_io`, `mkdir`, `touch`, `sleep`, `kill`, `wait`. Important harness variables and paths include `SCRATCH_MNT`, `SCRATCH_DEV`, `seqres.full`, `tmp`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch`; `_require_dm_target flakey`; `_scratch_mkfs >>$seqres.full 2>&1`; `_require_metadata_journaling $SCRATCH_DEV`; `_init_flakey`; `_scratch_mount`; `mkdir $SCRATCH_MNT/dir`; `touch $SCRATCH_MNT/dir/foo`; `$XFS_IO_PROG -c "fsync" $SCRATCH_MNT/dir/foo`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`; injects block-device, power-fail, shutdown, or thin-provisioning behavior to validate recovery paths; uses explicit sync/fsync/remount points to force persistence boundaries. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

ordering bugs in journal replay or fsync logging can lose metadata or data after simulated power loss. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/557.out`; success is mostly silence after prerequisite and operation checks. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/557 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/558 -->
# sources/test-tools/xfstests/tests/generic/558

## Purpose

FS QA Test No. generic/558 Stress test fs by using up all inodes and check fs. Also a regression test for xfsprogs commit d586858 xfs_repair: fix sibling pointer tests in verify_dir2_path()

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto enospc`. It imports `./common/preamble`, `./common/filter`. Prerequisite and skip gates include `_require_inode_limits`, `_require_scratch`. Local helper functions: `create_file`. External command surfaces and helper binaries visible in the source include `df`, `feature`, `mkdir`, `wait`. Important harness variables and paths include `SCRATCH_MNT`, `seqres.full`, `seq`, `LOAD_FACTOR`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_inode_limits`; `_require_scratch`; `echo "Silence is golden"`; `_scratch_mkfs_sized $((1024 * 1024 * 1024)) >>$seqres.full 2>&1`; `_scratch_mount`; `free_inodes=$(_get_free_inode $SCRATCH_MNT)`; `free_inodes=$(( ( (free_inodes + 999) / 1000) * 1000 ))`; `nr_cpus=$(( $($here/src/feature -o) * 4 * LOAD_FACTOR ))`; `echo "free inodes: $free_inodes nr_cpus: $nr_cpus" >> $seqres.full`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

environmental skips and helper availability can dominate failures, so `_require_*` gates are part of the contract. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/558.out`; success is mostly silence after prerequisite and operation checks. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/558 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/559 -->
# sources/test-tools/xfstests/tests/generic/559

## Purpose

FS QA Test generic/559 Dedupe a single big file and verify integrity

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto stress dedupe`. It imports `./common/preamble`, `./common/filter`, `./common/reflink`. Prerequisite and skip gates include `_require_scratch_duperemove`. No major local helper functions are defined; the scenario is driven directly by the top-level shell flow. External command surfaces and helper binaries visible in the source include `xfs_io`, `duperemove`, `seq`, `mount`, `umount`. Important harness variables and paths include `SCRATCH_MNT`, `seqres.full`, `tmp`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch_duperemove`; `fssize=$((2 * 1024 * 1024 * 1024))`; `_scratch_mkfs_sized $fssize > $seqres.full 2>&1`; `_scratch_mount >> $seqres.full 2>&1`; `$XFS_IO_PROG -f -c "pwrite -S 0x55 0 $fssize" $SCRATCH_MNT/${seq}.file >> $seqres.full 2>&1`; `md5sum $SCRATCH_MNT/${seq}.file > ${tmp}.md5sum`; `echo "= before cycle mount ="`; `$DUPEREMOVE_PROG -dr --dedupe-options=same -b 1048576 $SCRATCH_MNT/ >>$seqres.full 2>&1`; `md5sum -c --quiet ${tmp}.md5sum`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

shared extent, COW, or dedupe paths can corrupt unrelated file ranges or violate swapfile restrictions. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/559.out`. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/559 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/560 -->
# sources/test-tools/xfstests/tests/generic/560

## Purpose

FS QA Test generic/560 Iterate dedupe integrity test. Copy an original data0 several times (d0 -> d1, d1 -> d2, ... dn-1 -> dn), dedupe dataN everytime before copy. At last, verify dataN same with data0.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto stress dedupe`. It imports `./common/preamble`, `./common/filter`, `./common/reflink`. Prerequisite and skip gates include `_require_scratch_duperemove`. No major local helper functions are defined; the scenario is driven directly by the top-level shell flow. External command surfaces and helper binaries visible in the source include `duperemove`, `cp`, `mkdir`, `grep`, `mount`. Important harness variables and paths include `SCRATCH_MNT`, `seqres.full`, `tmp`, `seq`, `TIME_FACTOR`, `LOAD_FACTOR`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch_duperemove`; `_scratch_mkfs > $seqres.full 2>&1`; `_scratch_mount >> $seqres.full 2>&1`; `function iterate_dedup_verify()`; `local src=$srcdir`; `local dest=$dupdir/1`; `cp -a $src $dest`; `_run_fsstress $fsstress_opts -d $noisedir -n 200 -p $((5 * LOAD_FACTOR))`; `$DUPEREMOVE_PROG -dr --dedupe-options=same $dupdir >/dev/null 2>$seqres.full`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

shared extent, COW, or dedupe paths can corrupt unrelated file ranges or violate swapfile restrictions. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/560.out`; grep-based checks assert expected metadata or data is still visible. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/560 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/561 -->
# sources/test-tools/xfstests/tests/generic/561

## Purpose

FS QA Test generic/561 Dedup & random I/O race test, do multi-threads fsstress and dedupe on same directory/files

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto stress dedupe unreliable_in_parallel`. It imports `./common/preamble`, `./common/filter`, `./common/reflink`. Prerequisite and skip gates include `_require_scratch_duperemove`. Local helper functions: `_cleanup`. External command surfaces and helper binaries visible in the source include `duperemove`, `fsstress`, `wait`, `mkdir`, `seq`, `cp`, `touch`, `sleep`, `umount`, `mount`. Important harness variables and paths include `SCRATCH_MNT`, `TEST_DIR`, `seqres.full`, `tmp`, `seq`, `TIME_FACTOR`, `LOAD_FACTOR`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch_duperemove`; `_scratch_mkfs > $seqres.full 2>&1`; `_scratch_mount >> $seqres.full 2>&1`; `function end_test()`; `_kill_fsstress`; `rm -f $dupe_run`; `_pkill $dedup_bin >/dev/null 2>&1`; `wait $dedup_pids`; `rm -f $dedup_prog`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`; uses the configured test filesystem under `TEST_DIR` without necessarily reformatting it. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

shared extent, COW, or dedupe paths can corrupt unrelated file ranges or violate swapfile restrictions. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/561.out`; success is mostly silence after prerequisite and operation checks. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/561 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/562 -->
# sources/test-tools/xfstests/tests/generic/562

## Purpose

Test that if we clone a file with some large extents into a file that has many small extents, when the fs is nearly full, the clone operation does not fail and produces the correct result.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto clone punch`. It imports `./common/preamble`, `./common/filter`, `./common/reflink`. Prerequisite and skip gates include `_require_scratch_reflink`, `_require_test_program "punch-alternating"`, `_require_xfs_io_command "fpunch"`. No major local helper functions are defined; the scenario is driven directly by the top-level shell flow. External command surfaces and helper binaries visible in the source include `xfs_io`, `punch-alternating`, `grep`, `mount`, `od`. Important harness variables and paths include `SCRATCH_MNT`, `seqres.full`, `tmp`, `seq`, `FSTYP`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_fixed_by_fs_commit xfs 7ce31f20a077 "xfs: don't drop errno values when we fail to ficlone the entire range"`; `_require_scratch_reflink`; `_require_test_program "punch-alternating"`; `_require_xfs_io_command "fpunch"`; `_scratch_mkfs_sized $((590 * 1024 * 1024)) >>$seqres.full 2>&1`; `_scratch_mount`; `$XFS_IO_PROG -f -c "pwrite -S 0xe5 -b $file_size 0 $file_size" $SCRATCH_MNT/foo >>/dev/null`; `$here/src/punch-alternating $SCRATCH_MNT/foo >> $seqres.full`; `$XFS_IO_PROG -f -c "pwrite -S 0xc7 -b $file_size 0 $file_size" $SCRATCH_MNT/bar >>/dev/null`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

shared extent, COW, or dedupe paths can corrupt unrelated file ranges or violate swapfile restrictions. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/562.out`; content dumps/hexdumps expose corruption or unexpected nonzero data; grep-based checks assert expected metadata or data is still visible. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/562 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/563 -->
# sources/test-tools/xfstests/tests/generic/563

## Purpose

This test verifies that cgroup aware writeback properly accounts I/Os in various scenarios. We perform reads/writes from different combinations of cgroups and verify that pages are accounted against the group that brought them into cache.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick`. It imports `./common/preamble`, `./common/filter`, `./common/cgroup2`. Prerequisite and skip gates include `_require_scratch_nocheck`, `_require_cgroup2 io`, `_require_loop`, `_require_block_device $SCRATCH_DEV`, `_require_non_zoned_device ${SCRATCH_DEV}`. Local helper functions: `_cleanup`, `check_cg`, `switch_cg`, `reset`. External command surfaces and helper binaries visible in the source include `xfs_io`, `seq`, `stat`, `grep`, `mkdir`, `umount`, `mount`. Important harness variables and paths include `SCRATCH_MNT`, `SCRATCH_DEV`, `seqres.full`, `tmp`, `seq`, `FSTYP`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch_nocheck`; `_require_cgroup2 io`; `_require_loop`; `_require_block_device $SCRATCH_DEV`; `_require_non_zoned_device ${SCRATCH_DEV}`; `iosize=$((1024 * 1024 * 16))`; `loop_dev=$(_create_loop_device_like_bdev $SCRATCH_DEV $SCRATCH_DEV)`; `smajor=$((0x`stat -L -c %t $loop_dev`))`; `sminor=$((0x`stat -L -c %T $loop_dev`))`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`; uses explicit sync/fsync/remount points to force persistence boundaries. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

environmental skips and helper availability can dominate failures, so `_require_*` gates are part of the contract. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/563.out`; grep-based checks assert expected metadata or data is still visible. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/563 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/564 -->
# sources/test-tools/xfstests/tests/generic/564

## Purpose

Exercise copy_file_range() syscall error conditions. This is a regression test for kernel commit: 96e6e8f4a68d ("vfs: add missing checks to copy_file_range")

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick copy_range`. It imports `./common/preamble`, `./common/filter`. Prerequisite and skip gates include `_require_test`, `_require_loop`, `_require_mknod`, `_require_xfs_io_command "copy_range"`, `_require_xfs_io_command "copy_range" "-f"`. Local helper functions: `_cleanup`, `do_rlimit_copy`. External command surfaces and helper binaries visible in the source include `xfs_io`, `seq`, `mkdir`, `truncate`, `grep`. Important harness variables and paths include `TEST_DIR`, `seqres.full`, `tmp`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_register_cleanup "_cleanup" BUS`; `_require_test`; `_require_loop`; `_require_mknod`; `_require_xfs_io_command "copy_range"`; `_require_xfs_io_command "copy_range" "-f"`; `rm -rf $testdir`; `mkdir $testdir`; `$XFS_IO_PROG -f -c "pwrite -S 0x61 0 128k" $testdir/file >> $seqres.full 2>&1`.

## State and Persistence Behavior

The test uses the configured test filesystem under `TEST_DIR` without necessarily reformatting it. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

environmental skips and helper availability can dominate failures, so `_require_*` gates are part of the contract. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/564.out`; grep-based checks assert expected metadata or data is still visible. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/564 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/565 -->
# sources/test-tools/xfstests/tests/generic/565

## Purpose

Exercise copy_file_range() across devices supported by some filesystems since kernel commit: 5dae222a5ff0 vfs: allow copy_file_range to copy across devices

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick copy_range`. It imports `./common/preamble`, `./common/filter`. Prerequisite and skip gates include `_require_test`, `_require_scratch`, `_require_xfs_io_command "copy_range"`. No major local helper functions are defined; the scenario is driven directly by the top-level shell flow. External command surfaces and helper binaries visible in the source include `xfs_io`, `seq`, `mkdir`, `grep`. Important harness variables and paths include `SCRATCH_MNT`, `TEST_DIR`, `seqres.full`, `seq`, `FSTYP`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_register_cleanup "_cleanup" BUS`; `_require_test`; `_require_scratch`; `_require_xfs_io_command "copy_range"`; `_scratch_mkfs >>$seqres.full 2>&1`; `_scratch_mount`; `rm -rf $testdir`; `mkdir $testdir`; `$XFS_IO_PROG -f -c "pwrite -S 0x61 0 128k" $testdir/file >> $seqres.full 2>&1`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`; uses the configured test filesystem under `TEST_DIR` without necessarily reformatting it. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

environmental skips and helper availability can dominate failures, so `_require_*` gates are part of the contract. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/565.out`; grep-based checks assert expected metadata or data is still visible. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/565 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/566 -->
# sources/test-tools/xfstests/tests/generic/566

## Purpose

Regression test for chgrp returning to userspace with ILOCK held after a hard quota error. This causes the filesystem to hang if kernel is not patched. This test goes with commit 1fb254aa983bf ("xfs: fix missing ILOCK unlock when xfs_setattr_nonsize fails due to EDQUOT")

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick quota metadata`. It imports `./common/preamble`, `./common/quota`, `./common/filter`. Prerequisite and skip gates include `_require_scratch`, `_require_quota`, `_require_xfs_quota_foreign`, `_require_user`. Local helper functions: `_cleanup`. External command surfaces and helper binaries visible in the source include `xfs_quota`, `xfs_io`, `chgrp`, `mkdir`, `chown`. Important harness variables and paths include `SCRATCH_MNT`, `seqres.full`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch`; `_require_quota`; `_require_xfs_quota_foreign`; `_require_user`; `_qmount_option "grpquota"`; `_scratch_mkfs > $seqres.full`; `_qmount`; `mkdir -p $dir`; `chown $qa_user $dir`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`; enables quota accounting/enforcement state and adjusts grace timers or ownership/project metadata. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

quota timer and enforcement semantics vary by filesystem and userspace quota tooling. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/566.out`. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/566 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/567 -->
# sources/test-tools/xfstests/tests/generic/567

## Purpose

FS QA Test No. generic/567 Test mapped writes against punch-hole to ensure we get the data correctly written. This can expose data corruption bugs on filesystems where the block size is smaller than the page size. (generic/029 is a similar test but for truncate.)

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick rw punch mmap`. It imports `./common/preamble`, `./common/filter`. Prerequisite and skip gates include `_require_scratch`, `_require_xfs_io_command "fpunch"`. No major local helper functions are defined; the scenario is driven directly by the top-level shell flow. External command surfaces and helper binaries visible in the source include `xfs_io`, `truncate`. Important harness variables and paths include `SCRATCH_MNT`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch`; `_require_xfs_io_command "fpunch"`; `_scratch_mkfs > /dev/null 2>&1`; `_scratch_mount`; `$XFS_IO_PROG -t -f -c "pwrite -S 0x58 0 12288" -c "mmap -rw 0 12288" -c "mwrite -S 0x5a 2048 8192" -c "fpunch 2048 8192" -c "mwrite -S 0x...`; `echo "==== Pre-Remount ==="`; `_hexdump $testfile`; `_scratch_cycle_mount`; `echo "==== Post-Remount =="`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

I/O path races may be timing-sensitive and surface only under mmap, direct I/O, io_uring, or fsx replay stress. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/567.out`; content dumps/hexdumps expose corruption or unexpected nonzero data. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/567 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/568 -->
# sources/test-tools/xfstests/tests/generic/568

## Purpose

FS QA Test No. generic/568 Test that fallocating an unaligned range allocates all blocks touched by that range

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick rw prealloc`. It imports `./common/preamble`, `./common/filter`. Prerequisite and skip gates include `_require_xfs_io_command "falloc"`. Local helper functions: `_cleanup`. External command surfaces and helper binaries visible in the source include `xfs_io`, `seq`, `stat`. Important harness variables and paths include `TEST_DIR`, `tmp`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_xfs_io_command "falloc"`; `block_size=$(_get_file_block_size "$TEST_DIR")`; `$XFS_IO_PROG -f -c "falloc $((block_size - 1)) 2" "$testfile"`; `allocated_size_before=$(($(stat -c '%b * %B' "$testfile")))`; `$XFS_IO_PROG -c "pwrite $((block_size - 1)) 2" "$testfile" | _filter_xfs_io | sed -e "s/$((block_size - 1))/block_size - 1/"`; `allocated_size_after=$(($(stat -c '%b * %B' "$testfile")))`; `echo "ERROR: File grew from ${allocated_size_before} B to" "${allocated_size_after} B when writing to the fallocated range."`; `echo "OK: File did not grow."`.

## State and Persistence Behavior

The test uses the configured test filesystem under `TEST_DIR` without necessarily reformatting it. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

I/O path races may be timing-sensitive and surface only under mmap, direct I/O, io_uring, or fsx replay stress. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/568.out`. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/568 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/569 -->
# sources/test-tools/xfstests/tests/generic/569

## Purpose

Check that we can't modify a file that's an active swap file.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick rw swap prealloc mmap`. It imports `./common/preamble`, `./common/filter`. Prerequisite and skip gates include `_require_xfs_io_command "falloc"`, `_require_test_program swapon`, `_require_scratch_swapfile`, `_require_odirect`. Local helper functions: `_cleanup`. External command surfaces and helper binaries visible in the source include `xfs_io`, `swapon`, `swapoff`, `seq`, `truncate`. Important harness variables and paths include `SCRATCH_MNT`, `seqres.full`, `tmp`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_xfs_io_command "falloc"`; `_require_test_program swapon`; `_require_scratch_swapfile`; `_require_odirect`; `_scratch_mkfs > $seqres.full 2>&1`; `_scratch_mount >> $seqres.full 2>&1`; `_format_swapfile $testfile 20m > /dev/null`; `echo "verb $verb"`; `"$here/src/swapon" -v $verb $testfile`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`; temporarily activates swap files and must clean them with `swapoff`. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

active swapfiles must reject extent-changing operations and require page-size/block-size compatibility; I/O path races may be timing-sensitive and surface only under mmap, direct I/O, io_uring, or fsx replay stress. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/569.out`. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/569 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/570 -->
# sources/test-tools/xfstests/tests/generic/570

## Purpose

Check that we can't modify a block device that's an active swap device.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick rw swap mmap`. It imports `./common/preamble`, `./common/filter`. Prerequisite and skip gates include `_require_test_program swapon`, `_require_scratch_nocheck`, `_require_block_device $SCRATCH_DEV`, `_require_odirect`, `_require_non_zoned_device "$SCRATCH_DEV"`. Local helper functions: `_cleanup`. External command surfaces and helper binaries visible in the source include `mkswap`, `xfs_io`, `swapon`, `swapoff`. Important harness variables and paths include `SCRATCH_DEV`, `seqres.full`, `tmp`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_test_program swapon`; `_require_scratch_nocheck`; `_require_block_device $SCRATCH_DEV`; `_require_odirect`; `_require_non_zoned_device "$SCRATCH_DEV"`; `test -e /dev/snapshot && _notrun "userspace hibernation to swap is enabled"`; `$MKSWAP_PROG "$SCRATCH_DEV" >> $seqres.full`; `echo "verb $verb"`; `"$here/src/swapon" -v $verb $SCRATCH_DEV`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`; temporarily activates swap files and must clean them with `swapoff`. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

active swapfiles must reject extent-changing operations and require page-size/block-size compatibility; I/O path races may be timing-sensitive and surface only under mmap, direct I/O, io_uring, or fsx replay stress. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/570.out`. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/570 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/571 -->
# sources/test-tools/xfstests/tests/generic/571

## Purpose

lease test

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick`. It imports `./common/preamble`, `./common/filter`, `./common/locktest`. Prerequisite and skip gates include `_require_test`, `_require_test_fcntl_advisory_locks`, `_require_test_fcntl_setlease`. No major local helper functions are defined; the scenario is driven directly by the top-level shell flow. External command surfaces and helper binaries visible in the source include standard shell utilities plus xfstests helper functions. Important harness variables and paths include the standard xfstests environment variables.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_test`; `_require_test_fcntl_advisory_locks`; `_require_test_fcntl_setlease`; `_run_leasetest`.

## State and Persistence Behavior

The test creates temporary test data and relies on xfstests cleanup plus `$seqres.full` diagnostics for persistence evidence. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

environmental skips and helper availability can dominate failures, so `_require_*` gates are part of the contract. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/571.out`. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/571 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/572 -->
# sources/test-tools/xfstests/tests/generic/572

## Purpose

FS QA Test generic/572 This is a basic fs-verity test which verifies: - conditions for enabling verity - verity files have correct contents and size - can't change contents of verity files, but can change metadata - can retrieve a verity file's digest via FS_IOC_MEASURE_VERITY

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick verity`. It imports `./common/preamble`, `./common/filter`, `./common/verity`. Prerequisite and skip gates include `_require_scratch_verity`. Local helper functions: `_cleanup`, `filter_output`, `verify_data_readable`. External command surfaces and helper binaries visible in the source include `fsverity`, `xfs_io`, `mkdir`, `perl`, `sleep`, `kill`, `wait`, `mv`, `ln`, `chmod`, `chown`, `cp`. Important harness variables and paths include `SCRATCH_MNT`, `seqres.full`, `tmp`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch_verity`; `_disable_fsverity_signatures`; `_scratch_mkfs_verity &>> $seqres.full`; `_scratch_mount`; `_fsv_scratch_begin_subtest "Enabling verity on file with verity already enabled fails with EEXIST"`; `_fsv_create_enable_file $fsv_file`; `echo "(trying again)"`; `_fsv_enable $fsv_file |& filter_output`; `_fsv_scratch_begin_subtest "Enabling verity with invalid hash algorithm fails with EINVAL"`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

environmental skips and helper availability can dominate failures, so `_require_*` gates are part of the contract. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/572.out`; content dumps/hexdumps expose corruption or unexpected nonzero data. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/572 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/573 -->
# sources/test-tools/xfstests/tests/generic/573

## Purpose

FS QA Test generic/573 Test access controls on the fs-verity ioctls. FS_IOC_MEASURE_VERITY is allowed on any file, whereas FS_IOC_ENABLE_VERITY requires write access.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick verity`. It imports `./common/preamble`, `./common/filter`, `./common/verity`. Prerequisite and skip gates include `_require_scratch_verity`, `_require_user`, `_require_chattr ia`. Local helper functions: `_cleanup`. External command surfaces and helper binaries visible in the source include `fsverity`, `chattr`, `chmod`. Important harness variables and paths include `SCRATCH_MNT`, `seqres.full`, `tmp`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch_verity`; `_require_user`; `_require_chattr ia`; `_disable_fsverity_signatures`; `_scratch_mkfs_verity &>> $seqres.full`; `_scratch_mount`; `_fsv_scratch_begin_subtest "FS_IOC_ENABLE_VERITY doesn't require root"`; `echo foo > $fsv_file`; `chmod 666 $fsv_file`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

environmental skips and helper availability can dominate failures, so `_require_*` gates are part of the contract. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/573.out`; content dumps/hexdumps expose corruption or unexpected nonzero data. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/573 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/574 -->
# sources/test-tools/xfstests/tests/generic/574

## Purpose

FS QA Test generic/574 Test corrupting verity files. This test corrupts various parts of the contents of a verity file, or parts of its Merkle tree, by writing directly to the block device. It verifies that this causes I/O errors when the relevant part of the contents is later read by any means.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick verity mmap`. It imports `./common/preamble`, `./common/filter`, `./common/verity`. Prerequisite and skip gates include `_require_scratch_verity`, `_require_fsverity_corruption`. Local helper functions: `_cleanup`, `setup_zeroed_file`, `corruption_test`, `corrupt_eof_block_test`, `test_block_size`. External command surfaces and helper binaries visible in the source include `cp`, `grep`, `mount`, `seq`. Important harness variables and paths include `SCRATCH_MNT`, `seqres.full`, `tmp`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch_verity`; `_disable_fsverity_signatures`; `_require_fsverity_corruption`; `_scratch_mkfs_verity &>> $seqres.full`; `_scratch_mount`; `_fsv_scratch_begin_subtest "Testing block_size=FSV_BLOCK_SIZE"`; `test_block_size $FSV_BLOCK_SIZE`; `_fsv_scratch_begin_subtest "Testing block_size=$block_size if supported"`; `continue # Skip redundant test case.`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

I/O path races may be timing-sensitive and surface only under mmap, direct I/O, io_uring, or fsx replay stress. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/574.out`; grep-based checks assert expected metadata or data is still visible. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/574 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/575 -->
# sources/test-tools/xfstests/tests/generic/575

## Purpose

FS QA Test generic/575 Test that fs-verity is using the correct file digest values. This test verifies that fs-verity is doing its Merkle tree-based hashing correctly, i.e. that it hasn't been broken by a change.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick verity`. It imports `./common/preamble`, `./common/filter`, `./common/verity`. Prerequisite and skip gates include `_require_scratch_verity`. Local helper functions: `_cleanup`, `test_alg_with_block_size`. External command surfaces and helper binaries visible in the source include `cp`. Important harness variables and paths include `SCRATCH_MNT`, `seqres.full`, `tmp`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch_verity`; `_disable_fsverity_signatures`; `_scratch_mkfs_verity &>> $seqres.full`; `_scratch_mount`; `algs=(sha256 sha512)`; `block_sizes=(1024 4096)`; `salts=('' '' '' '--salt=' '--salt=f3c93fa6fb828c0e1587e5714ecf6f56')`; `sha256:f2cca36b9b1b7f07814e4284b10121809133e7cb9c4528c8f6846e85fc624ffa`; `sha256:ea08590a4fe9c3d6c9dafe0eedacd9dffff8f24e24f1865ee3af132a495ab087`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

environmental skips and helper availability can dominate failures, so `_require_*` gates are part of the contract. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/575.out`. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/575 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/576 -->
# sources/test-tools/xfstests/tests/generic/576

## Purpose

FS QA Test generic/576 Test using fs-verity and fscrypt simultaneously. This primarily verifies correct ordering of the hooks for each feature: fscrypt needs to be first.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick verity encrypt`. It imports `./common/preamble`, `./common/filter`, `./common/verity`, `./common/encrypt`. Prerequisite and skip gates include `_require_scratch_verity`, `_require_scratch_encryption`, `_require_command "$KEYCTL_PROG" keyctl`, `_require_fsverity_corruption`. Local helper functions: `_cleanup`. External command surfaces and helper binaries visible in the source include `keyctl`, `xfs_io`, `mkdir`, `cp`, `mount`. Important harness variables and paths include `SCRATCH_MNT`, `seqres.full`, `tmp`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch_verity`; `_require_scratch_encryption`; `_require_command "$KEYCTL_PROG" keyctl`; `_require_fsverity_corruption`; `_disable_fsverity_signatures`; `_scratch_mkfs_encrypted_verity &>> $seqres.full`; `_scratch_mount`; `_init_session_keyring`; `keydesc=$(_generate_session_encryption_key)`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`; creates encrypted directories/files and manipulates fscrypt keys or nonce/ciphertext metadata. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

fscrypt policy/key support and raw metadata inspection differ across filesystems and kernel versions. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/576.out`. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/576 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/577 -->
# sources/test-tools/xfstests/tests/generic/577

## Purpose

FS QA Test generic/577 Test the fs-verity built-in signature verification support.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick verity`. It imports `./common/preamble`, `./common/filter`, `./common/verity`. Prerequisite and skip gates include `_require_scratch_verity`, `_require_fsverity_builtin_signatures`. Local helper functions: `_cleanup`, `sign`, `reset_fsv_file`. External command surfaces and helper binaries visible in the source include `cp`. Important harness variables and paths include `SCRATCH_MNT`, `seqres.full`, `tmp`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch_verity`; `_require_fsverity_builtin_signatures`; `_scratch_mkfs_verity &>> $seqres.full`; `_scratch_mount`; `echo -e "\n# Generating certificates and private keys"`; `_fsv_generate_cert $keyfile$suffix $certfile$suffix $certfileder$suffix`; `echo -e "\n# Clearing fs-verity keyring"`; `_fsv_clear_keyring`; `echo -e "\n# Loading first certificate into fs-verity keyring"`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

environmental skips and helper availability can dominate failures, so `_require_*` gates are part of the contract. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/577.out`. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/577 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/578 -->
# sources/test-tools/xfstests/tests/generic/578

## Purpose

Make sure that we can handle multiple mmap writers to the same file.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick rw clone fiemap mmap`. It imports `./common/preamble`, `./common/filter`, `./common/reflink`. Prerequisite and skip gates include `_require_test_program "mmap-write-concurrent"`, `_require_command "$FILEFRAG_PROG" filefrag`, `_require_xfs_io_command "fiemap"`, `_require_test_reflink`, `_require_cp_reflink`, `_require_congruent_file_oplen $TEST_DIR $blksz`. Local helper functions: `_cleanup`, `compare`. External command surfaces and helper binaries visible in the source include `filefrag`, `mmap-write-concurrent`, `seq`, `od`, `mkdir`, `grep`. Important harness variables and paths include `TEST_DIR`, `seqres.full`, `tmp`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_test_program "mmap-write-concurrent"`; `_require_command "$FILEFRAG_PROG" filefrag`; `_require_xfs_io_command "fiemap"`; `_require_test_reflink`; `_require_cp_reflink`; `rm -rf $testdir`; `mkdir $testdir`; `echo "Create the original files"`; `_require_congruent_file_oplen $TEST_DIR $blksz`.

## State and Persistence Behavior

The test uses the configured test filesystem under `TEST_DIR` without necessarily reformatting it. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

shared extent, COW, or dedupe paths can corrupt unrelated file ranges or violate swapfile restrictions; I/O path races may be timing-sensitive and surface only under mmap, direct I/O, io_uring, or fsx replay stress. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/578.out`; content dumps/hexdumps expose corruption or unexpected nonzero data; grep-based checks assert expected metadata or data is still visible. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/578 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/579 -->
# sources/test-tools/xfstests/tests/generic/579

## Purpose

FS QA Test generic/579 Stress test for fs-verity. This tests enabling fs-verity on multiple files concurrently with concurrent readers on those files (with reads occurring before, during, and after the fs-verity enablement), while fsstress is also running on the same filesystem.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto stress verity`. It imports `./common/preamble`, `./common/filter`, `./common/verity`. Prerequisite and skip gates include `_require_scratch_verity`. Local helper functions: `_cleanup`. External command surfaces and helper binaries visible in the source include `fsstress`, `touch`, `wait`, `cp`, `sleep`, `grep`. Important harness variables and paths include `SCRATCH_MNT`, `seqres.full`, `tmp`, `seq`, `TIME_FACTOR`, `LOAD_FACTOR`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch_verity`; `_disable_fsverity_signatures`; `_scratch_mkfs_verity &>> $seqres.full`; `_scratch_mount`; `nproc_enabler=$((4 * LOAD_FACTOR))`; `nproc_reader=$((6 * LOAD_FACTOR))`; `nproc_stress=$((3 * LOAD_FACTOR))`; `runtime=$((20 * TIME_FACTOR))`; `head -c $fsv_file_size /dev/urandom > $orig_file`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`; uses explicit sync/fsync/remount points to force persistence boundaries. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

environmental skips and helper availability can dominate failures, so `_require_*` gates are part of the contract. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/579.out`; success is mostly silence after prerequisite and operation checks; grep-based checks assert expected metadata or data is still visible. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/579 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/580 -->
# sources/test-tools/xfstests/tests/generic/580

## Purpose

FS QA Test generic/580 Basic test of the fscrypt filesystem-level encryption keyring and v2 encryption policies.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick encrypt`. It imports `./common/preamble`, `./common/filter`, `./common/encrypt`. Prerequisite and skip gates include `_require_scratch_encryption -v 2`. Local helper functions: `test_with_policy_version`. External command surfaces and helper binaries visible in the source include `xfs_io`, `mkdir`. Important harness variables and paths include `SCRATCH_MNT`, `seqres.full`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `echo`; `_require_scratch_encryption -v 2`; `_scratch_mkfs_encrypted &>> $seqres.full`; `_scratch_mount`; `test_with_policy_version 1`; `test_with_policy_version 2`; `echo "# Trying to remove absent key"`; `_rm_enckey $SCRATCH_MNT abcdabcdabcdabcd`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`; creates encrypted directories/files and manipulates fscrypt keys or nonce/ciphertext metadata. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

fscrypt policy/key support and raw metadata inspection differ across filesystems and kernel versions. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/580.out`. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/580 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/581 -->
# sources/test-tools/xfstests/tests/generic/581

## Purpose

FS QA Test No. generic/581 Test non-root use of the fscrypt filesystem-level encryption keyring and v2 encryption policies.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick encrypt`. It imports `./common/preamble`, `./common/filter`, `./common/encrypt`. Prerequisite and skip gates include `_require_user`, `_require_scratch_encryption -v 2`. Local helper functions: `_cleanup`. External command surfaces and helper binaries visible in the source include `seq`, `chmod`, `mkdir`, `grep`, `sleep`. Important harness variables and paths include `SCRATCH_MNT`, `seqres.full`, `tmp`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `echo`; `_require_user`; `_require_scratch_encryption -v 2`; `_scratch_mkfs_encrypted &>> $seqres.full`; `_scratch_mount`; `raw_key+="\\x$(printf "%02x" $i)"`; `chmod 777 $SCRATCH_MNT`; `_user_do "mkdir $dir"`; `echo "# Setting v1 policy as regular user (should succeed)"`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`; creates encrypted directories/files and manipulates fscrypt keys or nonce/ciphertext metadata. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

fscrypt policy/key support and raw metadata inspection differ across filesystems and kernel versions. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/581.out`; content dumps/hexdumps expose corruption or unexpected nonzero data; grep-based checks assert expected metadata or data is still visible. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/581 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/582 -->
# sources/test-tools/xfstests/tests/generic/582

## Purpose

FS QA Test No. generic/582 Verify ciphertext for v2 encryption policies that use AES-256-XTS to encrypt file contents and AES-256-CTS-CBC to encrypt file names. This is the same as generic/548, except using v2 policies.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick encrypt`. It imports `./common/preamble`, `./common/filter`, `./common/encrypt`. Prerequisite and skip gates include feature gates are delegated to sourced helpers or nested helper routines. No major local helper functions are defined; the scenario is driven directly by the top-level shell flow. External command surfaces and helper binaries visible in the source include standard shell utilities plus xfstests helper functions. Important harness variables and paths include the standard xfstests environment variables.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_verify_ciphertext_for_encryption_policy AES-256-XTS AES-256-CTS-CBC v2`.

## State and Persistence Behavior

The test creates encrypted directories/files and manipulates fscrypt keys or nonce/ciphertext metadata. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

fscrypt policy/key support and raw metadata inspection differ across filesystems and kernel versions. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/582.out`. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/582 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/583 -->
# sources/test-tools/xfstests/tests/generic/583

## Purpose

FS QA Test No. generic/583 Verify ciphertext for v2 encryption policies that use AES-128-CBC-ESSIV to encrypt file contents and AES-128-CTS-CBC to encrypt file names. This is the same as generic/549, except using v2 policies.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick encrypt`. It imports `./common/preamble`, `./common/filter`, `./common/encrypt`. Prerequisite and skip gates include feature gates are delegated to sourced helpers or nested helper routines. No major local helper functions are defined; the scenario is driven directly by the top-level shell flow. External command surfaces and helper binaries visible in the source include standard shell utilities plus xfstests helper functions. Important harness variables and paths include the standard xfstests environment variables.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_verify_ciphertext_for_encryption_policy AES-128-CBC-ESSIV AES-128-CTS-CBC v2`.

## State and Persistence Behavior

The test creates encrypted directories/files and manipulates fscrypt keys or nonce/ciphertext metadata. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

fscrypt policy/key support and raw metadata inspection differ across filesystems and kernel versions. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/583.out`. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/583 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/584 -->
# sources/test-tools/xfstests/tests/generic/584

## Purpose

FS QA Test No. generic/584 Verify ciphertext for v2 encryption policies that use Adiantum to encrypt file contents and file names. This is the same as generic/550, except using v2 policies.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick encrypt`. It imports `./common/preamble`, `./common/filter`, `./common/encrypt`. Prerequisite and skip gates include feature gates are delegated to sourced helpers or nested helper routines. No major local helper functions are defined; the scenario is driven directly by the top-level shell flow. External command surfaces and helper binaries visible in the source include standard shell utilities plus xfstests helper functions. Important harness variables and paths include the standard xfstests environment variables.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_verify_ciphertext_for_encryption_policy Adiantum Adiantum v2`; `_verify_ciphertext_for_encryption_policy Adiantum Adiantum v2 direct`.

## State and Persistence Behavior

The test creates encrypted directories/files and manipulates fscrypt keys or nonce/ciphertext metadata. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

fscrypt policy/key support and raw metadata inspection differ across filesystems and kernel versions. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/584.out`. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/584 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/585 -->
# sources/test-tools/xfstests/tests/generic/585

## Purpose

Regression test for: bc56ad8c74b8: ("xfs: Fix deadlock between AGI and AGF with RENAME_WHITEOUT")

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto rename`. It imports `./common/preamble`, `./common/filter`, `./common/renameat2`. Prerequisite and skip gates include `_require_scratch`, `_require_renameat2 whiteout`. No major local helper functions are defined; the scenario is driven directly by the top-level shell flow. External command surfaces and helper binaries visible in the source include `fsstress`. Important harness variables and paths include `SCRATCH_MNT`, `seqres.full`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch`; `_require_renameat2 whiteout`; `_scratch_mkfs > $seqres.full 2>&1 || _fail "mkfs failed"`; `_scratch_mount >> $seqres.full 2>&1`; `_run_fsstress -z -n 150 -p 100 -f mknod=5 -f rwhiteout=5 -d $SCRATCH_MNT/fsstress`; `echo Silence is golden`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

environmental skips and helper availability can dominate failures, so `_require_*` gates are part of the contract. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/585.out`; success is mostly silence after prerequisite and operation checks. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/585 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/586 -->
# sources/test-tools/xfstests/tests/generic/586

## Purpose

Race an appending aio dio write to the second block of a file while simultaneously fallocating to the first block. Make sure that we end up with a two-block file.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick rw prealloc`. It imports `./common/preamble`. Prerequisite and skip gates include `_require_aiodio "aio-dio-append-write-fallocate-race"`, `_require_test`, `_require_xfs_io_command "falloc"`. Local helper functions: `_cleanup`. External command surfaces and helper binaries visible in the source include `seq`. Important harness variables and paths include `TEST_DIR`, `seqres.full`, `tmp`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_aiodio "aio-dio-append-write-fallocate-race"`; `_require_test`; `_require_xfs_io_command "falloc"`; `$AIO_TEST $testfile 100 >> $seqres.full`; `echo Silence is golden.`.

## State and Persistence Behavior

The test uses the configured test filesystem under `TEST_DIR` without necessarily reformatting it. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

I/O path races may be timing-sensitive and surface only under mmap, direct I/O, io_uring, or fsx replay stress. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/586.out`; success is mostly silence after prerequisite and operation checks. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/586 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/587 -->
# sources/test-tools/xfstests/tests/generic/587

## Purpose

Regression test to ensure that dquots are attached to the inode when we're performing unwritten extent conversion after a directio write and the extent mapping btree splits. On an unpatched kernel, the quota accounting will be become incorrect. This test accompanies the commit 2815a16d7ff623 "xfs: attach dquots and reserve quota blocks during unwritten conversion".

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick rw prealloc quota`. It imports `./common/preamble`, `./common/filter`, `./common/quota`. Prerequisite and skip gates include `_require_user`, `_require_quota`, `_require_xfs_io_command "falloc"`, `_require_scratch`, `_require_odirect`. Local helper functions: `check_quota_accounting`. External command surfaces and helper binaries visible in the source include `xfs_io`, `awk`, `stat`, `grep`, `seq`, `touch`, `chown`, `mount`. Important harness variables and paths include `SCRATCH_MNT`, `seqres.full`, `tmp`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_user`; `_require_quota`; `_require_xfs_io_command "falloc"`; `_require_scratch`; `_require_odirect`; `writes a deterministic fsx replay script`; `printf("%s: quota blocks %dKiB, expected %dKiB!\n", qa_user, \$2, blocks);`; `ENDL`; `_scratch_mkfs > $seqres.full`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`; enables quota accounting/enforcement state and adjusts grace timers or ownership/project metadata. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

I/O path races may be timing-sensitive and surface only under mmap, direct I/O, io_uring, or fsx replay stress; quota timer and enforcement semantics vary by filesystem and userspace quota tooling. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/587.out`; success is mostly silence after prerequisite and operation checks; grep-based checks assert expected metadata or data is still visible. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/587 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/588 -->
# sources/test-tools/xfstests/tests/generic/588

## Purpose

Test that if we clone part of an extent from a file to itself at different offset, fsync it, rewrite (COW) part of the extent from the former offset, fsync it again, power fail and then mount the filesystem, we are able to read the whole file and it has the correct data.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick log clone`. It imports `./common/preamble`, `./common/filter`, `./common/reflink`, `./common/dmflakey`. Prerequisite and skip gates include `_require_scratch_reflink`, `_require_dm_target flakey`, `_require_metadata_journaling $SCRATCH_DEV`, `_require_congruent_file_oplen $SCRATCH_MNT 65536`. Local helper functions: `_cleanup`. External command surfaces and helper binaries visible in the source include `xfs_io`, `mount`. Important harness variables and paths include `SCRATCH_MNT`, `SCRATCH_DEV`, `seqres.full`, `tmp`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch_reflink`; `_require_dm_target flakey`; `_scratch_mkfs >>$seqres.full 2>&1`; `_require_metadata_journaling $SCRATCH_DEV`; `_init_flakey`; `_scratch_mount`; `_require_congruent_file_oplen $SCRATCH_MNT 65536`; `$XFS_IO_PROG -f -c "pwrite -S 0xa3 0 256K" -c "fsync" -c "pwrite -S 0xc7 256K 256K" $SCRATCH_MNT/foobar | _filter_xfs_io`; `$XFS_IO_PROG -c "reflink $SCRATCH_MNT/foobar 320K 0K 64K" -c "fsync" $SCRATCH_MNT/foobar | _filter_xfs_io`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`; injects block-device, power-fail, shutdown, or thin-provisioning behavior to validate recovery paths; uses explicit sync/fsync/remount points to force persistence boundaries. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

ordering bugs in journal replay or fsync logging can lose metadata or data after simulated power loss; shared extent, COW, or dedupe paths can corrupt unrelated file ranges or violate swapfile restrictions. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/588.out`. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/588 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/589 -->
# sources/test-tools/xfstests/tests/generic/589

## Purpose

Test mount shared subtrees, verify the move semantics: --------------------------------------------------------------------------- | MOVE MOUNT OPERATION | |************************************************************************** |source(A)->| shared | private | slave | unbindable | | dest(B) | | | | | | | | | | | | | v | | | | | |************************************************************************** | shared | shared | shared | shared & slave | invalid | | | | | | | |non-shared| shared | private | slave | unbindable | *************************************************************************** NOTE: moving a mount residing under a shared mount is invalid. -----------------------------------------------------------------------

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto mount`. It imports `./common/preamble`, `./common/filter`. Prerequisite and skip gates include `_require_test`, `_require_scratch`, `_require_local_device $SCRATCH_DEV`. Local helper functions: `_cleanup`, `fs_stress`, `find_mnt`, `start_test`, `end_test`, `move_run`, `move_test`. External command surfaces and helper binaries visible in the source include `mount`, `seq`, `mkdir`, `sort`. Important harness variables and paths include `SCRATCH_DEV`, `TEST_DIR`, `seqres.full`, `tmp`, `seq`, `FSTYP`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_test`; `_require_scratch`; `_require_local_device $SCRATCH_DEV`; `rm -rf $SRCHEAD $DSTHEAD`; `mkdir $SRCHEAD $DSTHEAD 2>>$seqres.full`; `_mount --make-shared $TEST_DIR`; `move_test`; `_mount --make-private $TEST_DIR`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`; uses the configured test filesystem under `TEST_DIR` without necessarily reformatting it; uses explicit sync/fsync/remount points to force persistence boundaries. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

environmental skips and helper availability can dominate failures, so `_require_*` gates are part of the contract. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/589.out`. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/589 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/590 -->
# sources/test-tools/xfstests/tests/generic/590

## Purpose

Tests writing into big fallocates. Based on an XFS RT subvolume specific test now split into xfs/650.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto prealloc preallocrw`. It imports `./common/preamble`, `./common/filter`. Prerequisite and skip gates include `_require_xfs_io_command "falloc"`, `_require_fs_space "$SCRATCH_MNT" $((filesz / 1024))`. No major local helper functions are defined; the scenario is driven directly by the top-level shell flow. External command surfaces and helper binaries visible in the source include `xfs_io`, `truncate`. Important harness variables and paths include `SCRATCH_MNT`, `seqres.full`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_xfs_io_command "falloc"`; `maxextlen=$((0x1fffff))`; `_scratch_mkfs >>$seqres.full 2>&1`; `_scratch_mount`; `_require_fs_space "$SCRATCH_MNT" $((filesz / 1024))`; `$XFS_IO_PROG -c "falloc 0 $filesz" -c fsync -f "$SCRATCH_MNT/file"`; `$XFS_IO_PROG -c "pwrite -b 1M -W 0 $(((maxextlen + 2 - rextsize) * bs))" "$SCRATCH_MNT/file" >> "$seqres.full"`; `$XFS_IO_PROG -c "truncate 0" -c fsync "$SCRATCH_MNT/file"`; `_scratch_unmount`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`; uses explicit sync/fsync/remount points to force persistence boundaries. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

I/O path races may be timing-sensitive and surface only under mmap, direct I/O, io_uring, or fsx replay stress. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/590.out`; success is mostly silence after prerequisite and operation checks. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/590 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/591 -->
# sources/test-tools/xfstests/tests/generic/591

## Purpose

Test using splice() to read from pipes.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick rw pipe splice`. It imports `./common/preamble`. Prerequisite and skip gates include `_require_test`, `_require_odirect`, `_require_test_program "splice-test"`. Local helper functions: `_cleanup`. External command surfaces and helper binaries visible in the source include `min_dio_alignment`, `splice-test`. Important harness variables and paths include `TEST_DIR`, `TEST_DEV`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_test`; `_require_odirect`; `_require_test_program "splice-test"`; `diosize=`$here/src/min_dio_alignment $TEST_DIR $TEST_DEV``; `$here/src/splice-test -s $diosize -r $TEST_DIR/a`; `$here/src/splice-test -rd $TEST_DIR/a`; `$here/src/splice-test -s $diosize $TEST_DIR/a`; `$here/src/splice-test -d $TEST_DIR/a`.

## State and Persistence Behavior

The test uses the configured test filesystem under `TEST_DIR` without necessarily reformatting it. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

I/O path races may be timing-sensitive and surface only under mmap, direct I/O, io_uring, or fsx replay stress. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/591.out`. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/591 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/592 -->
# sources/test-tools/xfstests/tests/generic/592

## Purpose

Verify ciphertext for v2 encryption policies that use the IV_INO_LBLK_64 flag and use AES-256-XTS to encrypt file contents and AES-256-CTS-CBC to encrypt file names.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick encrypt`. It imports `./common/preamble`, `./common/filter`, `./common/encrypt`. Prerequisite and skip gates include feature gates are delegated to sourced helpers or nested helper routines. No major local helper functions are defined; the scenario is driven directly by the top-level shell flow. External command surfaces and helper binaries visible in the source include standard shell utilities plus xfstests helper functions. Important harness variables and paths include the standard xfstests environment variables.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_verify_ciphertext_for_encryption_policy AES-256-XTS AES-256-CTS-CBC v2 iv_ino_lblk_64`.

## State and Persistence Behavior

The test creates encrypted directories/files and manipulates fscrypt keys or nonce/ciphertext metadata. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

fscrypt policy/key support and raw metadata inspection differ across filesystems and kernel versions. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/592.out`. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/592 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/593 -->
# sources/test-tools/xfstests/tests/generic/593

## Purpose

Test adding a key to a filesystem's fscrypt keyring via an "fscrypt-provisioning" keyring key. This is an alternative to the normal method where the raw key is given directly.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick encrypt`. It imports `./common/preamble`, `./common/filter`, `./common/encrypt`. Prerequisite and skip gates include `_require_scratch_encryption -v 2`, `_require_command "$KEYCTL_PROG" keyctl`, `_require_add_enckey_by_key_id $SCRATCH_MNT`. Local helper functions: `test_with_policy_version`. External command surfaces and helper binaries visible in the source include `keyctl`, `xfs_io`, `mkdir`. Important harness variables and paths include `SCRATCH_MNT`, `seqres.full`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch_encryption -v 2`; `_require_command "$KEYCTL_PROG" keyctl`; `_init_session_keyring`; `_scratch_mkfs_encrypted &>> $seqres.full`; `_scratch_mount`; `_require_add_enckey_by_key_id $SCRATCH_MNT`; `test_with_policy_version 1`; `test_with_policy_version 2`; `echo`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`; creates encrypted directories/files and manipulates fscrypt keys or nonce/ciphertext metadata. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

fscrypt policy/key support and raw metadata inspection differ across filesystems and kernel versions. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/593.out`; content dumps/hexdumps expose corruption or unexpected nonzero data. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/593 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/594 -->
# sources/test-tools/xfstests/tests/generic/594

## Purpose

Test per-type(user, group and project) filesystem quota timers, make sure each of grace time can be set/get properly.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick quota`. It imports `./common/preamble`, `./common/filter`, `./common/quota`. Prerequisite and skip gates include `_require_scratch`, `_require_setquota_project`, `_require_quota`, `_require_prjquota $SCRATCH_DEV`. Local helper functions: `filter_repquota`. External command surfaces and helper binaries visible in the source include `mount`, `setquota`, `grep`. Important harness variables and paths include `SCRATCH_MNT`, `SCRATCH_DEV`, `seqres.full`, `seq`, `FSTYP`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch`; `_require_setquota_project`; `_require_scratch_xfs_crc`; `_require_quota`; `_scratch_mkfs >$seqres.full 2>&1`; `_scratch_enable_pquota`; `_qmount_option "usrquota,grpquota,prjquota"`; `_qmount`; `_require_prjquota $SCRATCH_DEV`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`; enables quota accounting/enforcement state and adjusts grace timers or ownership/project metadata. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

quota timer and enforcement semantics vary by filesystem and userspace quota tooling. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/594.out`; content dumps/hexdumps expose corruption or unexpected nonzero data; grep-based checks assert expected metadata or data is still visible. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/594 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/595 -->
# sources/test-tools/xfstests/tests/generic/595

## Purpose

Regression test for a bug in the FS_IOC_REMOVE_ENCRYPTION_KEY ioctl fixed by commit 2b4eae95c736 ("fscrypt: don't evict dirty inodes after removing key"). This bug could cause writes to encrypted files to be lost if they raced with the corresponding fscrypt master key being removed. With f2fs, this bug could also crash the kernel.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick encrypt`. It imports `./common/preamble`, `./common/filter`, `./common/encrypt`. Prerequisite and skip gates include `_require_scratch_encryption -v 2`, `_require_command "$KEYCTL_PROG" keyctl`. Local helper functions: `_cleanup`. External command surfaces and helper binaries visible in the source include `keyctl`, `touch`, `wait`, `mkdir`, `sleep`, `stat`. Important harness variables and paths include `SCRATCH_MNT`, `seqres.full`, `tmp`, `seq`, `TIME_FACTOR`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch_encryption -v 2`; `_require_command "$KEYCTL_PROG" keyctl`; `_scratch_mkfs_encrypted &>> $seqres.full`; `_scratch_mount`; `runtime=$((4 * TIME_FACTOR))`; `mkdir $dir`; `_set_encpolicy $dir $TEST_KEY_IDENTIFIER`; `_add_enckey $SCRATCH_MNT "$TEST_RAW_KEY"`; `echo -e "\n# Single-threaded reproducer"`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`; creates encrypted directories/files and manipulates fscrypt keys or nonce/ciphertext metadata. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

fscrypt policy/key support and raw metadata inspection differ across filesystems and kernel versions. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/595.out`; content dumps/hexdumps expose corruption or unexpected nonzero data. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/595 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/596 -->
# sources/test-tools/xfstests/tests/generic/596

## Purpose

Regression test for the bug fixed by commit 10a98cb16d80 ("xfs: clear PF_MEMALLOC before exiting xfsaild thread"). If the bug exists, a kernel WARNING should be triggered. See the commit message for details.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick`. It imports `./common/preamble`, `./common/filter`. Prerequisite and skip gates include `_require_bsd_process_accounting`, `_require_chattr S`, `_require_test`, `_require_scratch`. Local helper functions: `_cleanup`. External command surfaces and helper binaries visible in the source include `accton`, `chattr`, `seq`, `touch`. Important harness variables and paths include `TEST_DIR`, `seqres.full`, `tmp`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_bsd_process_accounting`; `_require_chattr S`; `_require_test`; `_require_scratch`; `rm -f $accounting_file`; `touch $accounting_file`; `$CHATTR_PROG +S $accounting_file`; `_scratch_mkfs &>> $seqres.full`; `$ACCTON_PROG $accounting_file >> $seqres.full`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`; uses the configured test filesystem under `TEST_DIR` without necessarily reformatting it; uses explicit sync/fsync/remount points to force persistence boundaries. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

environmental skips and helper availability can dominate failures, so `_require_*` gates are part of the contract. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/596.out`; success is mostly silence after prerequisite and operation checks. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/596 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/597 -->
# sources/test-tools/xfstests/tests/generic/597

## Purpose

Test protected_symlink and protected_hardlink sysctls

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick perms`. It imports `./common/preamble`, `./common/filter`. Prerequisite and skip gates include `_require_test`, `_require_sysctl_variable fs.protected_symlinks`, `_require_sysctl_variable fs.protected_hardlinks`, `_require_user fsgqa2`, `_require_group fsgqa2`, `_require_user fsgqa`, `_require_group fsgqa`, `_require_symlinks`. Local helper functions: `_cleanup`, `test_symlink`, `test_hardlink`, `setup_tree`. External command surfaces and helper binaries visible in the source include `seq`, `sysctl`, `ln`, `chown`, `chmod`, `mkdir`. Important harness variables and paths include `TEST_DIR`, `tmp`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_test`; `_require_sysctl_variable fs.protected_symlinks`; `_require_sysctl_variable fs.protected_hardlinks`; `_require_user fsgqa2`; `_require_group fsgqa2`; `_require_user fsgqa`; `_require_group fsgqa`; `_require_symlinks`; `SYMLINK_PROTECTION=`sysctl -n fs.protected_symlinks``.

## State and Persistence Behavior

The test uses the configured test filesystem under `TEST_DIR` without necessarily reformatting it. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

environmental skips and helper availability can dominate failures, so `_require_*` gates are part of the contract. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/597.out`; content dumps/hexdumps expose corruption or unexpected nonzero data. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/597 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/598 -->
# sources/test-tools/xfstests/tests/generic/598

## Purpose

Test protected_regular and protected_fifos sysctls

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick perms`. It imports `./common/preamble`, `./common/filter`. Prerequisite and skip gates include `_require_test`, `_require_sysctl_variable fs.protected_regular`, `_require_sysctl_variable fs.protected_fifos`, `_require_user fsgqa2`, `_require_group fsgqa2`, `_require_user fsgqa`, `_require_group fsgqa`, `_require_chmod`. Local helper functions: `_cleanup`, `test_access`, `setup_tree`. External command surfaces and helper binaries visible in the source include `xfs_io`, `seq`, `sysctl`, `chmod`, `mkdir`, `chown`. Important harness variables and paths include `TEST_DIR`, `tmp`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_test`; `_require_sysctl_variable fs.protected_regular`; `_require_sysctl_variable fs.protected_fifos`; `_require_user fsgqa2`; `_require_group fsgqa2`; `_require_user fsgqa`; `_require_group fsgqa`; `_require_chmod`; `REGULAR_PROTECTION=`sysctl -n fs.protected_regular``.

## State and Persistence Behavior

The test uses the configured test filesystem under `TEST_DIR` without necessarily reformatting it. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

environmental skips and helper availability can dominate failures, so `_require_*` gates are part of the contract. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/598.out`; content dumps/hexdumps expose corruption or unexpected nonzero data. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/598 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/599 -->
# sources/test-tools/xfstests/tests/generic/599

## Purpose

All Rights Reserved. Test data integrity for ro remount.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick remount shutdown`. It imports `./common/preamble`, `./common/filter`. Prerequisite and skip gates include `_require_fssum`, `_require_scratch`, `_require_scratch_shutdown`. No major local helper functions are defined; the scenario is driven directly by the top-level shell flow. External command surfaces and helper binaries visible in the source include `fssum`, `mkdir`. Important harness variables and paths include `SCRATCH_MNT`, `tmp`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_fssum`; `_require_scratch`; `_require_scratch_shutdown`; `_scratch_mkfs &>/dev/null`; `_scratch_mount`; `mkdir $localdir`; `_scratch_sync`; `$FSSUM_PROG -ugomAcdES -f -w $tmp.fssum $localdir`; `_scratch_remount ro`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`; injects block-device, power-fail, shutdown, or thin-provisioning behavior to validate recovery paths; uses explicit sync/fsync/remount points to force persistence boundaries. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

ordering bugs in journal replay or fsync logging can lose metadata or data after simulated power loss. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/599.out`; fssum before/after comparison validates tree integrity. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/599 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/600 -->
# sources/test-tools/xfstests/tests/generic/600

## Purpose

Test individual user ID quota grace period extension This is the linux quota-tools version of the test This test only exercises user quota because it's not known whether the filesystem can set individual grace timers for each quota type

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick quota`. It imports `./common/preamble`, `./common/filter`, `./common/quota`. Prerequisite and skip gates include `_require_scratch`, `_require_quota`, `_require_user`, `_require_setquota_project`. No major local helper functions are defined; the scenario is driven directly by the top-level shell flow. External command surfaces and helper binaries visible in the source include `setquota`, `touch`, `sleep`, `grep`. Important harness variables and paths include `SCRATCH_MNT`, `seqres.full`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch`; `_require_quota`; `_require_user`; `_require_setquota_project`; `_scratch_mkfs >$seqres.full 2>&1`; `_qmount_option "usrquota"`; `_qmount`; `echo "Silence is golden"`; `setquota -t -u 0 1 $SCRATCH_MNT`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`; enables quota accounting/enforcement state and adjusts grace timers or ownership/project metadata. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

quota timer and enforcement semantics vary by filesystem and userspace quota tooling. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/600.out`; success is mostly silence after prerequisite and operation checks; content dumps/hexdumps expose corruption or unexpected nonzero data; grep-based checks assert expected metadata or data is still visible. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/600 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/601 -->
# sources/test-tools/xfstests/tests/generic/601

## Purpose

Test individual user ID quota grace period extension This is the xfs_quota version of the test This test only exercises user quota because it's not known whether the filesystem can set individual grace timers for each quota type

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick quota`. It imports `./common/preamble`, `./common/filter`, `./common/quota`. Prerequisite and skip gates include `_require_scratch`, `_require_quota`, `_require_user`, `_require_xfs_quota_foreign`, `_require_setquota_project`. No major local helper functions are defined; the scenario is driven directly by the top-level shell flow. External command surfaces and helper binaries visible in the source include `xfs_quota`, `setquota`, `grep`, `touch`, `sleep`. Important harness variables and paths include `SCRATCH_MNT`, `seqres.full`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch`; `_require_quota`; `_require_user`; `_require_xfs_quota_foreign`; `_require_setquota_project`; `_scratch_mkfs >$seqres.full 2>&1`; `_qmount_option "usrquota"`; `_qmount`; `echo "Silence is golden"`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`; enables quota accounting/enforcement state and adjusts grace timers or ownership/project metadata. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

quota timer and enforcement semantics vary by filesystem and userspace quota tooling. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/601.out`; success is mostly silence after prerequisite and operation checks; content dumps/hexdumps expose corruption or unexpected nonzero data; grep-based checks assert expected metadata or data is still visible. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/601 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/602 -->
# sources/test-tools/xfstests/tests/generic/602

## Purpose

Verify ciphertext for v2 encryption policies that use the IV_INO_LBLK_32 flag and use AES-256-XTS to encrypt file contents and AES-256-CTS-CBC to encrypt file names.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick encrypt`. It imports `./common/preamble`, `./common/filter`, `./common/encrypt`. Prerequisite and skip gates include feature gates are delegated to sourced helpers or nested helper routines. No major local helper functions are defined; the scenario is driven directly by the top-level shell flow. External command surfaces and helper binaries visible in the source include standard shell utilities plus xfstests helper functions. Important harness variables and paths include the standard xfstests environment variables.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_verify_ciphertext_for_encryption_policy AES-256-XTS AES-256-CTS-CBC v2 iv_ino_lblk_32`.

## State and Persistence Behavior

The test creates encrypted directories/files and manipulates fscrypt keys or nonce/ciphertext metadata. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

fscrypt policy/key support and raw metadata inspection differ across filesystems and kernel versions. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/602.out`. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/602 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/603 -->
# sources/test-tools/xfstests/tests/generic/603

## Purpose

Test per-type(user, group and project) filesystem quota timers, make sure enforcement

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick quota`. It imports `./common/preamble`, `./common/filter`, `./common/quota`. Prerequisite and skip gates include `_require_scratch`, `_require_setquota_project`, `_require_quota`, `_require_user`, `_require_group`, `_require_prjquota $SCRATCH_DEV`. Local helper functions: `_cleanup`, `init_files`, `cleanup_files`, `filter_enospc_edquot`, `test_grace`. External command surfaces and helper binaries visible in the source include `xfs_io`, `seq`, `touch`, `chown`, `chgrp`, `chmod`, `grep`, `setquota`, `sleep`, `truncate`, `mkdir`. Important harness variables and paths include `SCRATCH_MNT`, `SCRATCH_DEV`, `seqres.full`, `tmp`, `seq`, `FSTYP`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch`; `_require_scratch_xfs_crc`; `_require_setquota_project`; `_require_quota`; `_require_user`; `_require_group`; `_scratch_mkfs >$seqres.full 2>&1`; `_scratch_enable_pquota`; `_qmount_option "usrquota,grpquota,prjquota"`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`; uses explicit sync/fsync/remount points to force persistence boundaries; enables quota accounting/enforcement state and adjusts grace timers or ownership/project metadata. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

quota timer and enforcement semantics vary by filesystem and userspace quota tooling. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/603.out`; content dumps/hexdumps expose corruption or unexpected nonzero data; grep-based checks assert expected metadata or data is still visible. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/603 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/604 -->
# sources/test-tools/xfstests/tests/generic/604

## Purpose

Evicting dirty inodes can take a long time during umount. Check that a new mount racing with such a delayed umount succeeds.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick mount`. It imports `./common/preamble`, `./common/filter`. Prerequisite and skip gates include `_exclude_fs overlay`, `_require_scratch`. No major local helper functions are defined; the scenario is driven directly by the top-level shell flow. External command surfaces and helper binaries visible in the source include `xfs_io`, `umount`, `mount`, `seq`, `sleep`, `wait`. Important harness variables and paths include `SCRATCH_MNT`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_exclude_fs overlay`; `_require_scratch`; `_scratch_mkfs > /dev/null 2>&1`; `_scratch_mount`; `$XFS_IO_PROG -f -c "pwrite 0 4K" $SCRATCH_MNT/$i >/dev/null`; `_scratch_unmount &`; `sleep 0.01s ; _scratch_mount`; `wait`; `echo "Silence is golden"`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

environmental skips and helper availability can dominate failures, so `_require_*` gates are part of the contract. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/604.out`; success is mostly silence after prerequisite and operation checks. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/604 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/605 -->
# sources/test-tools/xfstests/tests/generic/605

## Purpose

Test per-inode DAX flag by mmap direct/buffered IO.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto attr quick dax prealloc mmap`. It imports `./common/preamble`, `./common/filter`. Prerequisite and skip gates include `_require_hugepages`, `_require_scratch_dax_mountopt "dax=always"`, `_require_test_program "feature"`, `_require_test_program "t_mmap_dio"`, `_require_dax_iflag`, `_require_xfs_io_command "falloc"`. Local helper functions: `prep_directories`, `prep_files`, `t_both_dax`, `t_nondax_to_dax`, `t_dax_to_nondax`, `t_both_nondax`, `t_dax_flag_mmap_dio`, `do_tests`. External command surfaces and helper binaries visible in the source include `xfs_io`, `t_mmap_dio`, `feature`, `mkdir`, `mount`. Important harness variables and paths include `SCRATCH_MNT`, `seqres.full`, `seq`, `MOUNT_OPTIONS`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_hugepages`; `_require_scratch_dax_mountopt "dax=always"`; `_require_test_program "feature"`; `_require_test_program "t_mmap_dio"`; `_require_dax_iflag`; `_require_xfs_io_command "falloc"`; `_scratch_mkfs_geom $(_get_hugepagesize) 1 >> $seqres.full 2>&1`; `tsize=$((128 * 1024 * 1024))`; `export MOUNT_OPTIONS=""`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`; depends on per-inode or mount-option DAX state visible through xattrs/statx and mmap/direct-I/O behavior. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

I/O path races may be timing-sensitive and surface only under mmap, direct I/O, io_uring, or fsx replay stress; DAX mount options, inode flags, page-cache invalidation, and statx reporting have filesystem-specific behavior. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/605.out`; success is mostly silence after prerequisite and operation checks. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/605 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/606 -->
# sources/test-tools/xfstests/tests/generic/606

## Purpose

By the following cases, verify if statx() can query S_DAX flag on regular file correctly. 1) With dax=always option, FS_XFLAG_DAX is ignored and S_DAX flag always exists on regular file. 2) With dax=inode option, setting/clearing FS_XFLAG_DAX can change S_DAX flag on regular file. 3) With dax=never option, FS_XFLAG_DAX is ignored and S_DAX flag never exists on regular file.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto attr quick dax`. It imports `./common/preamble`, `./common/filter`. Prerequisite and skip gates include `_require_scratch_dax_mountopt "dax=always"`, `_require_dax_iflag`, `_require_xfs_io_command "statx" "-r"`. Local helper functions: `test_s_dax`, `do_tests`. External command surfaces and helper binaries visible in the source include `xfs_io`, `mkdir`, `touch`. Important harness variables and paths include `SCRATCH_MNT`, `seqres.full`, `seq`, `MOUNT_OPTIONS`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch_dax_mountopt "dax=always"`; `_require_dax_iflag`; `_require_xfs_io_command "statx" "-r"`; `echo "Silence is golden"`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`; depends on per-inode or mount-option DAX state visible through xattrs/statx and mmap/direct-I/O behavior. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

DAX mount options, inode flags, page-cache invalidation, and statx reporting have filesystem-specific behavior. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/606.out`; success is mostly silence after prerequisite and operation checks. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/606 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/607 -->
# sources/test-tools/xfstests/tests/generic/607

## Purpose

Verify the inheritance behavior of FS_XFLAG_DAX flag in various combinations. 1) New files and directories automatically inherit FS_XFLAG_DAX from their parent directory. 2) cp operation make files and directories inherit the FS_XFLAG_DAX from new parent directory. 3) mv operation make files and directories preserve the FS_XFLAG_DAX from old parent directory. In addition, setting/clearing FS_XFLAG_DAX flag is not impacted by dax mount options.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto attr quick dax`. It imports `./common/preamble`, `./common/filter`. Prerequisite and skip gates include `_require_scratch`, `_require_dax_iflag`, `_require_xfs_io_command "lsattr" "-v"`. Local helper functions: `test_xflag_inheritance1`, `test_xflag_inheritance2`, `test_xflag_inheritance3`, `test_xflag_inheritance4`, `test_xflag_inheritance5`, `do_xflag_tests`, `do_tests`. External command surfaces and helper binaries visible in the source include `xfs_io`, `cp`, `mv`, `mount`, `grep`, `mkdir`, `touch`, `seq`. Important harness variables and paths include `SCRATCH_MNT`, `TEST_DIR`, `seqres.full`, `seq`, `FSTYP`, `MOUNT_OPTIONS`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch`; `_require_dax_iflag`; `_require_xfs_io_command "lsattr" "-v"`; `output="$($XFS_IO_PROG -c "lsattr -v" $TEST_DIR 2>&1)"`; `echo "$output" | grep -q "Inappropriate ioctl for device" && _notrun "$FSTYP: FSGETXATTR not supported on directories."`; `echo "Silence is golden"`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`; uses the configured test filesystem under `TEST_DIR` without necessarily reformatting it; depends on per-inode or mount-option DAX state visible through xattrs/statx and mmap/direct-I/O behavior. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

DAX mount options, inode flags, page-cache invalidation, and statx reporting have filesystem-specific behavior. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/607.out`; success is mostly silence after prerequisite and operation checks; grep-based checks assert expected metadata or data is still visible. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/607 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/608 -->
# sources/test-tools/xfstests/tests/generic/608

## Purpose

FS QA Test 608 Toggling FS_XFLAG_DAX on an existing file can make S_DAX on the file change immediately when all applications close the file. It's a regression test for: 'commit 77573fa310d9 ("fs: Kill DCACHE_DONTCACHE dentry even if DCACHE_REFERENCED is set")' Write data into a file and then enable DAX on the file immediately, the written data which is still in the buffer should be synchronized to disk instead of discarded when the corresponding inode is evicted. It's a regression test for: 'commit 88149082bb8e ("fs: Handle I_DONTCACHE in iput_final() instead of generic_drop_inode()"'

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto attr quick dax`. It imports `./common/preamble`, `./common/filter`. Prerequisite and skip gates include `_require_scratch_dax_mountopt "dax=always"`, `_require_dax_iflag`, `_require_xfs_io_command "lsattr" "-v"`, `_require_xfs_io_command "statx" "-r"`. Local helper functions: `test_enable_dax`, `test_disable_dax`, `test_buffered_data_lost`, `do_tests`. External command surfaces and helper binaries visible in the source include `xfs_io`, `touch`, `mkdir`, `grep`. Important harness variables and paths include `SCRATCH_MNT`, `seqres.full`, `seq`, `MOUNT_OPTIONS`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch_dax_mountopt "dax=always"`; `_require_dax_iflag`; `_require_xfs_io_command "lsattr" "-v"`; `_require_xfs_io_command "statx" "-r"`; `_scratch_mkfs >> $seqres.full 2>&1`; `export MOUNT_OPTIONS=""`; `echo "Silence is golden"`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`; uses explicit sync/fsync/remount points to force persistence boundaries; depends on per-inode or mount-option DAX state visible through xattrs/statx and mmap/direct-I/O behavior. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

DAX mount options, inode flags, page-cache invalidation, and statx reporting have filesystem-specific behavior. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/608.out`; success is mostly silence after prerequisite and operation checks; grep-based checks assert expected metadata or data is still visible. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/608 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/609 -->
# sources/test-tools/xfstests/tests/generic/609

## Purpose

iomap can call generic_write_sync() if we're O_DSYNC, so write a basic test to exercise O_DSYNC so any unsuspecting file systems will get lockdep warnings if their locking isn't compatible.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick rw`. It imports `./common/preamble`, `./common/filter`. Prerequisite and skip gates include `_require_test`, `_require_xfs_io_command "pwrite"`, `_require_odirect`. Local helper functions: `_cleanup`. External command surfaces and helper binaries visible in the source include `xfs_io`. Important harness variables and paths include `TEST_DIR`, `tmp`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_test`; `_require_xfs_io_command "pwrite"`; `_require_odirect`; `$XFS_IO_PROG -f -d -s -c "pwrite 0 64k" $TEST_DIR/file | _filter_xfs_io`.

## State and Persistence Behavior

The test uses the configured test filesystem under `TEST_DIR` without necessarily reformatting it; uses explicit sync/fsync/remount points to force persistence boundaries. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

I/O path races may be timing-sensitive and surface only under mmap, direct I/O, io_uring, or fsx replay stress. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/609.out`. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/609 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/610 -->
# sources/test-tools/xfstests/tests/generic/610

## Purpose

Test a fallocate() zero range operation against a large file range for which there are many small extents allocated. Verify the operation does not fail and the respective range return zeroes on subsequent reads.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick prealloc zero punch`. It imports `./common/preamble`, `./common/filter`. Prerequisite and skip gates include `_require_scratch`, `_require_xfs_io_command "fzero"`, `_require_xfs_io_command "fpunch"`, `_require_test_program "punch-alternating"`. No major local helper functions are defined; the scenario is driven directly by the top-level shell flow. External command surfaces and helper binaries visible in the source include `xfs_io`, `punch-alternating`, `od`. Important harness variables and paths include `SCRATCH_MNT`, `seqres.full`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch`; `_require_xfs_io_command "fzero"`; `_require_xfs_io_command "fpunch"`; `_require_test_program "punch-alternating"`; `_scratch_mkfs >>$seqres.full 2>&1`; `_scratch_mount`; `$XFS_IO_PROG -f -c "pwrite -S 0xab -b 10M 0 100M" $SCRATCH_MNT/foobar >>$seqres.full`; `$here/src/punch-alternating $SCRATCH_MNT/foobar >>$seqres.full`; `_scratch_sync`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`; uses explicit sync/fsync/remount points to force persistence boundaries. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

environmental skips and helper availability can dominate failures, so `_require_*` gates are part of the contract. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/610.out`; content dumps/hexdumps expose corruption or unexpected nonzero data. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/610 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/611 -->
# sources/test-tools/xfstests/tests/generic/611

## Purpose

Verify that metadata won't get corrupted when extended attribute name of size one is set. This test verifies the problem fixed in kernel with commit f4020438fab0 ("xfs: fix boundary test in xfs_attr_shortform_verify")

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick attr`. It imports `./common/preamble`, `./common/filter`, `./common/attr`. Prerequisite and skip gates include `_require_scratch`, `_require_attrs`. No major local helper functions are defined; the scenario is driven directly by the top-level shell flow. External command surfaces and helper binaries visible in the source include `touch`, `grep`. Important harness variables and paths include `SCRATCH_MNT`, `seqres.full`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch`; `_require_attrs`; `_scratch_mkfs > $seqres.full 2>&1`; `_scratch_mount`; `touch "${localfile}"`; `"${SETFATTR_PROG}" -n user.a "${localfile}"`; `_scratch_cycle_mount`; `_getfattr --absolute-names -n user.a $localfile | grep 'user.a'`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

environmental skips and helper availability can dominate failures, so `_require_*` gates are part of the contract. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/611.out`; grep-based checks assert expected metadata or data is still visible. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/611 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/612 -->
# sources/test-tools/xfstests/tests/generic/612

## Purpose

Regression test for reflink corruption present as of: 78f0cc9d55cb "xfs: don't use delalloc extents for COW on files with extsize hints" and (inadvertently) fixed as of: 36adcbace24e "xfs: fill out the srcmap in iomap_begin" upstream, and in the 5.4 stable tree with: aee38af574a1 "xfs: trim IO to found COW extent limit"

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick clone`. It imports `./common/preamble`, `./common/filter`, `./common/reflink`. Prerequisite and skip gates include `_require_test`, `_require_test_reflink`. No major local helper functions are defined; the scenario is driven directly by the top-level shell flow. External command surfaces and helper binaries visible in the source include `xfs_io`, `seq`, `mkdir`, `cp`, `mount`. Important harness variables and paths include `TEST_DIR`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_test`; `_require_test_reflink`; `mkdir -p $DIR`; `rm -f $DIR/a $DIR/b`; `$XFS_IO_PROG -c "extsize 1048576" $DIR >/dev/null 2>&1`; `$XFS_IO_PROG -c "cowextsize 1048576" $DIR >/dev/null 2>&1`; `echo "Create file b"`; `$XFS_IO_PROG -f -c "pwrite -S 0x0 0 2m" -c fsync $DIR/b | _filter_xfs_io`; `echo "Reflink copy from b to a"`.

## State and Persistence Behavior

The test uses the configured test filesystem under `TEST_DIR` without necessarily reformatting it; uses explicit sync/fsync/remount points to force persistence boundaries. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

shared extent, COW, or dedupe paths can corrupt unrelated file ranges or violate swapfile restrictions. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/612.out`; content dumps/hexdumps expose corruption or unexpected nonzero data. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/612 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/613 -->
# sources/test-tools/xfstests/tests/generic/613

## Purpose

Test that encryption nonces are unique and random, where randomness is approximated as "incompressible by the xz program". An encryption nonce is the 16-byte value that the filesystem generates for each encrypted file. These nonces must be unique in order to cause different files to be encrypted differently, which is an important security property. In practice, they need to be random to achieve that; and it's easy enough to test for both uniqueness and randomness, so we test for both.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick encrypt`. It imports `./common/preamble`, `./common/filter`, `./common/encrypt`. Prerequisite and skip gates include `_require_scratch_encryption -v 2`, `_require_get_encryption_nonce_support`, `_require_command "$XZ_PROG" xz`. No major local helper functions are defined; the scenario is driven directly by the top-level shell flow. External command surfaces and helper binaries visible in the source include `xz`, `mkdir`, `stat`, `touch`, `sort`, `uniq`. Important harness variables and paths include `SCRATCH_MNT`, `SCRATCH_DEV`, `seqres.full`, `tmp`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch_encryption -v 2`; `_require_get_encryption_nonce_support`; `_require_command "$XZ_PROG" xz`; `_scratch_mkfs_encrypted &>> $seqres.full`; `_scratch_mount`; `echo -e "\n# Adding encryption keys"`; `_add_enckey $SCRATCH_MNT "$TEST_RAW_KEY"`; `_add_enckey $SCRATCH_MNT "$TEST_RAW_KEY" -d $TEST_KEY_DESCRIPTOR`; `echo -e "\n# Creating encrypted files and directories"`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`; creates encrypted directories/files and manipulates fscrypt keys or nonce/ciphertext metadata. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

fscrypt policy/key support and raw metadata inspection differ across filesystems and kernel versions. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/613.out`. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/613 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/614 -->
# sources/test-tools/xfstests/tests/generic/614

## Purpose

Test that after doing a memory mapped write to an empty file, a call to stat(2) reports a non-zero number of used blocks.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick rw mmap`. It imports `./common/preamble`, `./common/filter`. Prerequisite and skip gates include `_require_scratch`, `_require_scratch_delalloc`. No major local helper functions are defined; the scenario is driven directly by the top-level shell flow. External command surfaces and helper binaries visible in the source include `xfs_io`, `stat`, `truncate`. Important harness variables and paths include `SCRATCH_MNT`, `seqres.full`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch`; `_require_scratch_delalloc`; `_scratch_mkfs >>$seqres.full 2>&1`; `_scratch_mount`; `$XFS_IO_PROG -f -c "truncate 64K" -c "mmap -w 0 64K" -c "mwrite -S 0xab 0 64K" -c "munmap" $SCRATCH_MNT/foobar | _filter_xfs_io`; `blocks_used=$(stat -c %b $SCRATCH_MNT/foobar)`; `echo "error: stat(2) reported 0 used blocks"`; `echo "Silence is golden"`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

I/O path races may be timing-sensitive and surface only under mmap, direct I/O, io_uring, or fsx replay stress. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/614.out`; success is mostly silence after prerequisite and operation checks. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/614 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/615 -->
# sources/test-tools/xfstests/tests/generic/615

## Purpose

Test that if we keep overwriting an entire file, either with buffered writes or direct IO writes, the number of used blocks reported by stat(2) is never zero while writeback is in progress.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick rw`. It imports `./common/preamble`, `./common/filter`. Prerequisite and skip gates include `_require_scratch`, `_require_odirect`. Local helper functions: `stat_loop`. External command surfaces and helper binaries visible in the source include `xfs_io`, `stat`, `touch`, `kill`, `wait`. Important harness variables and paths include `SCRATCH_MNT`, `seqres.full`, `tmp`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch`; `_require_odirect`; `_scratch_mkfs >>$seqres.full 2>&1`; `_scratch_mount`; `$XFS_IO_PROG -f -s -c "pwrite -b 64K 0 64K" $SCRATCH_MNT/foo > /dev/null`; `touch $loop_file`; `stat_loop $SCRATCH_MNT/foo &`; `echo "Testing buffered writes"`; `break`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

I/O path races may be timing-sensitive and surface only under mmap, direct I/O, io_uring, or fsx replay stress. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/615.out`. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/615 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/616 -->
# sources/test-tools/xfstests/tests/generic/616

## Purpose

IO_URING soak buffered fsx test, copy from generic/522 but reduce the number fsx ops to limit the testing time to be an auto group test.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto rw io_uring stress soak`. It imports `./common/preamble`, `./common/filter`. Prerequisite and skip gates include `_require_test`, `_require_io_uring`. No major local helper functions are defined; the scenario is driven directly by the top-level shell flow. External command surfaces and helper binaries visible in the source include `seq`. Important harness variables and paths include `TEST_DIR`, `seq`, `TIME_FACTOR`, `LOAD_FACTOR`, `SOAK_DURATION`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_test`; `_require_io_uring`; `nr_ops=$((100000 * TIME_FACTOR))`; `op_sz=$((128000 * LOAD_FACTOR))`; `fsx_args=(-S 0)`; `fsx_args+=(-U)`; `fsx_args+=(-q)`; `fsx_args+=(-N $nr_ops)`; `fsx_args+=(-p $((nr_ops / 100)))`.

## State and Persistence Behavior

The test uses the configured test filesystem under `TEST_DIR` without necessarily reformatting it. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

I/O path races may be timing-sensitive and surface only under mmap, direct I/O, io_uring, or fsx replay stress. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/616.out`; success is mostly silence after prerequisite and operation checks; fsx/fsstress style stress exits cleanly and emits only filtered diagnostics. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/616 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/617 -->
# sources/test-tools/xfstests/tests/generic/617

## Purpose

IO_URING soak direct-IO fsx test, copy from generic/521 but reduce the number fsx ops to limit the testing time to be an auto group test.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto rw io_uring stress soak`. It imports `./common/preamble`, `./common/filter`. Prerequisite and skip gates include `_require_test`, `_require_odirect`, `_require_io_uring`. No major local helper functions are defined; the scenario is driven directly by the top-level shell flow. External command surfaces and helper binaries visible in the source include `feature`, `seq`. Important harness variables and paths include `TEST_DIR`, `seq`, `TIME_FACTOR`, `LOAD_FACTOR`, `SOAK_DURATION`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_test`; `_require_odirect`; `_require_io_uring`; `nr_ops=$((20000 * TIME_FACTOR))`; `op_sz=$((128000 * LOAD_FACTOR))`; `min_dio_sz=$($here/src/feature -s)`; `fsx_args=(-S 0)`; `fsx_args+=(-U)`; `fsx_args+=(-q)`.

## State and Persistence Behavior

The test uses the configured test filesystem under `TEST_DIR` without necessarily reformatting it. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

I/O path races may be timing-sensitive and surface only under mmap, direct I/O, io_uring, or fsx replay stress. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/617.out`; success is mostly silence after prerequisite and operation checks; fsx/fsstress style stress exits cleanly and emits only filtered diagnostics. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/617 -->
