# Group Research: subset-b-009542

This grouped report covers Btrfs xfstests cases `220` through `300`. Each section preserves the original source path in its title and is bounded by exact reconciliation markers so it can be split into `Docs/researches/<source>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/220 -->
# sources/test-tools/xfstests/tests/btrfs/220

## Purpose
Test all existent mount options of btrfs * device= argument is already being test by btrfs/125 * space cache test already covered by test btrfs/131 Compare the mounted flags with $opt_check. When the comparison fails, $opt is echoed to help to track which option was used to trigger the unexpected results. Mounts using opt ($1), remounts using remount_opt ($2), and remounts again using opt again (1), checking if the mount opts are being enabled/disabled by using _check arguments ($3 and $4). In this subset it primarily covers multi-device, RAID, seed/sprout, or device-management paths, mount and remount option semantics.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick remount`. Requirement and capability gates: line 17: `_require_scratch`. Local helper surface: `cleanup()` (line 19), `test_mount_flags()` (line 28), `test_enable_disable_mount_opt()` (line 67), `test_roundtrip_mount()` (line 100), `test_mount_opt()` (line 119), `test_should_fail()` (line 135), `test_optional_mount_opts()` (line 151), `test_subvol()` (line 167), `test_optional_kernel_features()` (line 193), `test_non_revertible_options()` (line 201), `test_one_shot_options()` (line 222), `test_revertible_options()` (line 233). Important command/API calls include line 34: `opt_check="$2"`; line 39: `if [ "$opt_check" != "$DEFAULT_OPTS" ]; then`; line 48: `opt_check="$opt_check,$stripped"`; line 57: `diff=$(echo "$opt_check,$active_opt" | tr ',' '\n' | sort | grep -v 'rw' | uniq -u)`; line 60: `echo "Unexepcted mount options, checking for '$opt_check' in '$active_opt' using '$opt'"`; line 76: `remount_opt_check="$4"`; line 78: `_scratch_mount "-o $opt"`; line 80: `test_mount_flags $opt $opt_check`; line 84: `test_mount_flags $remount_opt $remount_opt_check`; line 113: `test_enable_disable_mount_opt $opt $opt_check $remount_opt $remount_opt_check`; line 114: `test_enable_disable_mount_opt $remount_opt $remount_opt_check $opt $opt_check`; line 141: `_try_scratch_mount "-o $opt" >/dev/null 2>&1`; line 159: `_try_scratch_mount "-o $opt" >/dev/null 2>&1 || return`; line 163: `test_mount_opt $opt $opt_check`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick remount`, install cleanup if needed, enforce requirements, then formats scratch storage, mounts the test filesystem, creates or deletes subvolumes/snapshots, runs btrfs check or xfstests scratch checks, cycles mounts to force persistence. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Snapshot and subvolume roots are deliberate persistent state used to test root items, received UUIDs, cleaner behavior, and metadata references. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through btrfs-progs. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 220 | Silence is golden`.

## Risks and Edge Cases
device topology tests can expose races in device scan state, degraded mounts, stripe geometry, replacement, and cleanup of scratch device pools; discard tests are sensitive to block-device discard support and whether allocated extents are accidentally punched on replacement devices. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/220 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/221 -->
# sources/test-tools/xfstests/tests/btrfs/221

## Purpose
Test that an incremental send operation emits the correct path for link and rename operation after swapping the names and locations of several inodes in a way that creates a nasty dependency of rename and link operations. Notably one file has its name and location swapped with a directory for which it used to have a directory entry in it. Override the default cleanup function. We want "a" to have a lower inode number than its parent directory, so it was created before the directory and then moved into it. Filesystem looks like:. In this subset it primarily covers Btrfs send/receive stream generation and replay, swapfile activation restrictions.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick send`. Requirement and capability gates: line 26: `_require_test`; line 27: `_require_scratch`; line 28: `_require_fssum`. Local helper surface: `_cleanup()` (line 17). Important command/API calls include line 14: `_begin_fstest auto quick send`; line 20: `rm -fr $send_files_dir`; line 30: `send_files_dir=$TEST_DIR/btrfs-test-$seq`; line 33: `mkdir $send_files_dir`; line 35: `_scratch_mkfs >>$seqres.full 2>&1`; line 36: `_scratch_mount`; line 53: `$BTRFS_UTIL_PROG subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/mysnap1 > /dev/null`; line 56: `$BTRFS_UTIL_PROG send -f $send_files_dir/1.snap $SCRATCH_MNT/mysnap1 2>&1 1>/dev/null | _filter_scratch`; line 82: `$BTRFS_UTIL_PROG subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/mysnap2 > /dev/null`; line 84: `$BTRFS_UTIL_PROG send -p $SCRATCH_MNT/mysnap1 -f $send_files_dir/2.snap $SCRATCH_MNT/mysnap2 2>&1 1>/dev/null | _filter_scratch`; line 87: `$FSSUM_PROG -A -f -w $send_files_dir/1.fssum $SCRATCH_MNT/mysnap1`; line 88: `$FSSUM_PROG -A -f -w $send_files_dir/2.fssum -x $SCRATCH_MNT/mysnap2/mysnap1 $SCRATCH_MNT/mysnap2`; line 97: `$BTRFS_UTIL_PROG receive -f $send_files_dir/1.snap $SCRATCH_MNT > /dev/null`; line 104: `$BTRFS_UTIL_PROG receive -f $send_files_dir/2.snap $SCRATCH_MNT > /dev/null`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick send`, install cleanup if needed, enforce requirements, then formats scratch storage, mounts the test filesystem, creates or deletes subvolumes/snapshots, generates and replays send streams, cycles mounts to force persistence. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. It persists send streams, fssum files, or received subvolumes in a temporary test directory and validates replay on a freshly formatted scratch filesystem. Snapshot and subvolume roots are deliberate persistent state used to test root items, received UUIDs, cleaner behavior, and metadata references. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through btrfs-progs, fssum. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 221 | At subvol SCRATCH_MNT/mysnap1 | At subvol SCRATCH_MNT/mysnap2 | At subvol mysnap1 | OK | OK`.

## Risks and Edge Cases
send-stream ordering bugs can emit invalid paths, clone sources, link records, or parent references that only appear after replaying onto a clean filesystem; swapfile tests rely on cleaner thread and remount commit timing after snapshot deletion. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/221 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/222 -->
# sources/test-tools/xfstests/tests/btrfs/222

## Purpose
Test an incremental send operation after doing a series of changes in a tree such that one inode gets two hardlinks with names and locations swapped with two other inodes that correspond to different directories, and one of these directories is the parent of the other directory. Override the default cleanup function. Filesystem looks like: . (ino 256) |----- f1 (ino 257) |----- f2 (ino 258). In this subset it primarily covers Btrfs send/receive stream generation and replay, swapfile activation restrictions.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick send`. Requirement and capability gates: line 25: `_require_test`; line 26: `_require_scratch`; line 27: `_require_fssum`. Local helper surface: `_cleanup()` (line 16). Important command/API calls include line 13: `_begin_fstest auto quick send`; line 19: `rm -fr $send_files_dir`; line 29: `send_files_dir=$TEST_DIR/btrfs-test-$seq`; line 32: `mkdir $send_files_dir`; line 34: `_scratch_mkfs >>$seqres.full 2>&1`; line 35: `_scratch_mount`; line 50: `$BTRFS_UTIL_PROG subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/mysnap1 > /dev/null`; line 53: `$BTRFS_UTIL_PROG send -f $send_files_dir/1.snap $SCRATCH_MNT/mysnap1 2>&1 1>/dev/null | _filter_scratch`; line 98: `$BTRFS_UTIL_PROG subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/mysnap2 > /dev/null`; line 100: `$BTRFS_UTIL_PROG send -p $SCRATCH_MNT/mysnap1 -f $send_files_dir/2.snap $SCRATCH_MNT/mysnap2 2>&1 1>/dev/null | _filter_scratch`; line 103: `$FSSUM_PROG -A -f -w $send_files_dir/1.fssum $SCRATCH_MNT/mysnap1`; line 104: `$FSSUM_PROG -A -f -w $send_files_dir/2.fssum -x $SCRATCH_MNT/mysnap2/mysnap1 $SCRATCH_MNT/mysnap2`; line 113: `$BTRFS_UTIL_PROG receive -f $send_files_dir/1.snap $SCRATCH_MNT > /dev/null`; line 127: `$BTRFS_UTIL_PROG receive -f $send_files_dir/2.snap $SCRATCH_MNT > /dev/null`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick send`, install cleanup if needed, enforce requirements, then formats scratch storage, mounts the test filesystem, creates or deletes subvolumes/snapshots, generates and replays send streams, cycles mounts to force persistence. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. It persists send streams, fssum files, or received subvolumes in a temporary test directory and validates replay on a freshly formatted scratch filesystem. Snapshot and subvolume roots are deliberate persistent state used to test root items, received UUIDs, cleaner behavior, and metadata references. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through btrfs-progs, fssum. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 222 | At subvol SCRATCH_MNT/mysnap1 | At subvol SCRATCH_MNT/mysnap2 | At subvol mysnap1 | OK | OK`.

## Risks and Edge Cases
send-stream ordering bugs can emit invalid paths, clone sources, link records, or parent references that only appear after replaying onto a clean filesystem; swapfile tests rely on cleaner thread and remount commit timing after snapshot deletion. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/222 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/223 -->
# sources/test-tools/xfstests/tests/btrfs/223

## Purpose
Test that after replacing a device, if we run fstrim against the filesystem we do not trim/discard allocated chunks in the new device. We verify that allocated chunks in the new device were not trim/discarded by mounting the new device only in degraded mode, as this is the easiest way to verify it. Add a test file with some data. Replace the first device, $dev1, with a new device. Run fstrim, it should not trim/discard allocated extents in the new device. Unmount the filesystem. Mount the filesystem in degraded mode using the new device and verify that the. In this subset it primarily covers multi-device, RAID, seed/sprout, or device-management paths, discard/trim behavior.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick replace trim raid`. Requirement and capability gates: line 17: `_require_scratch_dev_pool 3`; line 18: `_require_command "$WIPEFS_PROG" wipefs`; line 27: `_require_batched_discard $SCRATCH_MNT`. Local helper surface: no custom shell functions beyond the linear test body. Important command/API calls include line 13: `_begin_fstest auto quick replace trim raid`; line 17: `_require_scratch_dev_pool 3`; line 18: `_require_command "$WIPEFS_PROG" wipefs`; line 20: `_scratch_dev_pool_get 2`; line 25: `_scratch_pool_mkfs "-m raid1 -d raid1"`; line 26: `_scratch_mount`; line 27: `_require_batched_discard $SCRATCH_MNT`; line 30: `$XFS_IO_PROG -f -c "pwrite -S 0xab 0 10M" $SCRATCH_MNT/foo | _filter_xfs_io`; line 33: `$BTRFS_UTIL_PROG replace start -Bf $dev1 $SPARE_DEV $SCRATCH_MNT >> $seqres.full`; line 39: `_scratch_unmount`; line 45: `_mount -o degraded $SPARE_DEV $SCRATCH_MNT`; line 51: `_scratch_dev_pool_put`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick replace trim raid`, install cleanup if needed, enforce requirements, then mounts the test filesystem, cycles mounts to force persistence. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Multi-device tests allocate scratch pool devices and leave correctness evidence in chunk maps, device registry state, degraded mounts, and btrfs check results. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through btrfs-progs, xfs_io. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 223 | wrote 10485760/10485760 bytes at offset 0 | XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec) | File foo data: | 0000000 ab ab ab ab ab ab ab ab ab ab ab ab ab ab ab ab | * | 10485760`.

## Risks and Edge Cases
device topology tests can expose races in device scan state, degraded mounts, stripe geometry, replacement, and cleanup of scratch device pools; discard tests are sensitive to block-device discard support and whether allocated extents are accidentally punched on replacement devices. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/223 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/224 -->
# sources/test-tools/xfstests/tests/btrfs/224

## Purpose
Test the assign functionality of qgroups Test assign qgroup for submodule with shared extents by reflink Test assign qgroup for submodule without shared extents Test snapshot with assigning qgroup for higher level qgroup success, all done. In this subset it primarily covers quota group accounting, assignment, limits, and rescan behavior, reflink/clone extent sharing, subvolume and snapshot metadata.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick qgroup`. Requirement and capability gates: line 16: `_require_scratch`; line 17: `_require_btrfs_qgroup_report`; line 18: `_require_cp_reflink`. Local helper surface: `assign_shared_test()` (line 21), `assign_no_shared_test()` (line 45), `snapshot_test()` (line 66). Important command/API calls include line 10: `_begin_fstest auto quick qgroup`; line 13: `. ./common/reflink`; line 17: `_require_btrfs_qgroup_report`; line 18: `_require_cp_reflink`; line 23: `_scratch_mkfs > /dev/null 2>&1`; line 24: `_scratch_mount`; line 26: `echo "=== qgroup assign shared test ===" >> $seqres.full`; line 27: `$BTRFS_UTIL_PROG quota enable $SCRATCH_MNT`; line 28: `_qgroup_rescan $SCRATCH_MNT >> $seqres.full`; line 30: `$BTRFS_UTIL_PROG subvolume create $SCRATCH_MNT/a >> $seqres.full`; line 31: `$BTRFS_UTIL_PROG subvolume create $SCRATCH_MNT/b >> $seqres.full`; line 34: `_cp_reflink "$SCRATCH_MNT"/a/file1 "$SCRATCH_MNT"/b/file1`; line 36: `$BTRFS_UTIL_PROG qgroup create 1/100 $SCRATCH_MNT`; line 37: `$BTRFS_UTIL_PROG qgroup assign $SCRATCH_MNT/a 1/100 $SCRATCH_MNT`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick qgroup`, install cleanup if needed, enforce requirements, then formats scratch storage, mounts the test filesystem, creates or deletes subvolumes/snapshots, enables and inspects quota groups, runs btrfs check or xfstests scratch checks, cycles mounts to force persistence. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Snapshot and subvolume roots are deliberate persistent state used to test root items, received UUIDs, cleaner behavior, and metadata references. Quota state persists in qgroup metadata and is forced through rescans, syncs, commits, and filesystem checks. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through btrfs-progs. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 224 | Silence is golden`.

## Risks and Edge Cases
qgroup tests are sensitive to delayed accounting, rescan completion, shared extents, and limit enforcement after transaction commits. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/224 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/225 -->
# sources/test-tools/xfstests/tests/btrfs/225

## Purpose
Test for seed device-delete on a sprouted FS. Steps: Create a seed FS. Add a RW device to make it sprout FS and then delete the seed device. Override the default cleanup function. Mount the seed device and add the rw device Now remount success, all done. In this subset it primarily covers multi-device, RAID, seed/sprout, or device-management paths, mount and remount option semantics.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick volume seed`. Requirement and capability gates: line 28: `_require_test`; line 29: `_require_scratch_dev_pool 2`; line 30: `_require_btrfs_forget_or_module_loadable`. Local helper surface: `_cleanup()` (line 17). Important command/API calls include line 20: `rm -f $tmp.*`; line 21: `_btrfs_rescan_devices`; line 26: `_fixed_by_kernel_commit b5ddcffa3777 "btrfs: fix put of uninitialized kobject after seed device delete"`; line 28: `_require_test`; line 29: `_require_scratch_dev_pool 2`; line 30: `_require_btrfs_forget_or_module_loadable`; line 32: `_scratch_dev_pool_get 2`; line 38: `_mount $seed $SCRATCH_MNT`; line 40: `$XFS_IO_PROG -f -c "pwrite -S 0xab 0 1M" $SCRATCH_MNT/foo > /dev/null`; line 41: `_scratch_unmount`; line 42: `$BTRFS_TUNE_PROG -S 1 $seed`; line 45: `_mount -o ro $seed $SCRATCH_MNT`; line 46: `$BTRFS_UTIL_PROG device add -f $sprout $SCRATCH_MNT >> $seqres.full`; line 50: `_mount $sprout $SCRATCH_MNT`. It documents fixed kernel commit context at line 26: `_fixed_by_kernel_commit b5ddcffa3777 \`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick volume seed`, install cleanup if needed, enforce requirements, then mounts the test filesystem, cycles mounts to force persistence. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Multi-device tests allocate scratch pool devices and leave correctness evidence in chunk maps, device registry state, degraded mounts, and btrfs check results. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through btrfs-progs, xfs_io, btrfstune. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 225 | --- before delete ---- | 0000000 abab abab abab abab abab abab abab abab | * | 4000000 | 0000000 cdcd cdcd cdcd cdcd cdcd cdcd cdcd cdcd | * | 4000000 | ... (15 expected-output lines total)`.

## Risks and Edge Cases
device topology tests can expose races in device scan state, degraded mounts, stripe geometry, replacement, and cleanup of scratch device pools. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/225 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/226 -->
# sources/test-tools/xfstests/tests/btrfs/226

## Purpose
Test several (btrfs specific) scenarios with RWF_NOWAIT writes, cases where they should fail and cases where they should succeed. RWF_NOWAIT only works with direct IO, which requires an inode with nodatasum (otherwise it falls back to buffered IO). Test a write against COW file/extent - should fail with -EAGAIN. Disable the NOCOW attribute of the file just in case MOUNT_OPTIONS has "-o nodatacow". Check no data was written. Create a file with two extents (NOCOW), then create a snapshot, unshare the first extent by writing to it without RWF_NOWAIT, and then attempt to write. In this subset it primarily covers reflink/clone extent sharing, subvolume and snapshot metadata.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick rw snapshot clone prealloc punch`. Requirement and capability gates: line 16: `_require_scratch_reflink`; line 17: `_require_chattr C`; line 18: `_require_odirect`; line 19: `_require_xfs_io_command pwrite -N`; line 20: `_require_xfs_io_command falloc -k`; line 21: `_require_xfs_io_command fpunch`. Local helper surface: no custom shell functions beyond the linear test body. Important command/API calls include line 11: `_begin_fstest auto quick rw snapshot clone prealloc punch`; line 14: `. ./common/reflink`; line 16: `_require_scratch_reflink`; line 19: `_require_xfs_io_command pwrite -N`; line 20: `_require_xfs_io_command falloc -k`; line 23: `_scratch_mkfs >>$seqres.full 2>&1`; line 27: `_scratch_mount -o nodatasum`; line 38: `$XFS_IO_PROG -s -c "pwrite -S 0xab 0 128K" $SCRATCH_MNT/f1 | _filter_xfs_io`; line 39: `$XFS_IO_PROG -d -c "pwrite -N -V 1 -S 0xff 32K 64K" $SCRATCH_MNT/f1`; line 50: `echo "Testing write against extent shared across snapshots"`; line 53: `$XFS_IO_PROG -s -c "pwrite -S 0xab 0 64K" -c "pwrite -S 0xcd 64K 64K" $SCRATCH_MNT/f2 | _filter_xfs_io`; line 57: `_btrfs subvolume snapshot $SCRATCH_MNT $SCRATCH_MNT/snap`; line 61: `$XFS_IO_PROG -s -c "pwrite -S 0xab 0 64K" $SCRATCH_MNT/f2 | _filter_xfs_io`; line 65: `$XFS_IO_PROG -d -c "pwrite -N -V 1 -S 0xff -b 64K 32K 64K" $SCRATCH_MNT/f2`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick rw snapshot clone prealloc punch`, install cleanup if needed, enforce requirements, then formats scratch storage, mounts the test filesystem, creates or deletes subvolumes/snapshots. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Snapshot and subvolume roots are deliberate persistent state used to test root items, received UUIDs, cleaner behavior, and metadata references. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through xfs_io. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 226 | Testing write against COW file | wrote 131072/131072 bytes at offset 0 | XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec) | pwrite: Resource temporarily unavailable | File data after write attempt: | 0000000 ab ab ab ab ab ab ab ab ab ab ab ab ab ab ab ab | * | ... (69 expected-output lines total)`.

## Risks and Edge Cases
NOWAIT writes must not block on COW, extent locking, or allocation and should leave file contents unchanged on EAGAIN paths. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/226 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/227 -->
# sources/test-tools/xfstests/tests/btrfs/227

## Purpose
Test that an incremental send operation succeeds, and produces the correct results, after removing a directory and all its files, unmounting the filesystem, mounting the filesystem again and creating a new file (or directory). Override the default cleanup function. Filesystem looks like: . (ino 256) |----- dir/ (ino 257) |----- file1 (ino 258). In this subset it primarily covers Btrfs send/receive stream generation and replay.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick send`. Requirement and capability gates: line 25: `_require_test`; line 26: `_require_scratch`; line 27: `_require_fssum`. Local helper surface: `_cleanup()` (line 16). Important command/API calls include line 13: `_begin_fstest auto quick send`; line 19: `rm -fr $send_files_dir`; line 29: `send_files_dir=$TEST_DIR/btrfs-test-$seq`; line 32: `mkdir $send_files_dir`; line 34: `_scratch_mkfs >>$seqres.full 2>&1`; line 35: `_scratch_mount`; line 53: `$BTRFS_UTIL_PROG subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/mysnap1 > /dev/null`; line 56: `$BTRFS_UTIL_PROG send -f $send_files_dir/1.snap $SCRATCH_MNT/mysnap1 2>&1 1>/dev/null | _filter_scratch`; line 77: `$BTRFS_UTIL_PROG subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/mysnap2 > /dev/null`; line 79: `$BTRFS_UTIL_PROG send -p $SCRATCH_MNT/mysnap1 -f $send_files_dir/2.snap $SCRATCH_MNT/mysnap2 2>&1 1>/dev/null | _filter_scratch`; line 82: `$FSSUM_PROG -A -f -w $send_files_dir/1.fssum $SCRATCH_MNT/mysnap1`; line 83: `$FSSUM_PROG -A -f -w $send_files_dir/2.fssum -x $SCRATCH_MNT/mysnap2/mysnap1 $SCRATCH_MNT/mysnap2`; line 92: `$BTRFS_UTIL_PROG receive -f $send_files_dir/1.snap $SCRATCH_MNT > /dev/null`; line 107: `$BTRFS_UTIL_PROG receive -f $send_files_dir/2.snap $SCRATCH_MNT > /dev/null`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick send`, install cleanup if needed, enforce requirements, then formats scratch storage, mounts the test filesystem, creates or deletes subvolumes/snapshots, generates and replays send streams, cycles mounts to force persistence. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. It persists send streams, fssum files, or received subvolumes in a temporary test directory and validates replay on a freshly formatted scratch filesystem. Snapshot and subvolume roots are deliberate persistent state used to test root items, received UUIDs, cleaner behavior, and metadata references. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through btrfs-progs, fssum. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 227 | At subvol SCRATCH_MNT/mysnap1 | At subvol SCRATCH_MNT/mysnap2 | At subvol mysnap1 | OK | OK`.

## Risks and Edge Cases
send-stream ordering bugs can emit invalid paths, clone sources, link records, or parent references that only appear after replaying onto a clean filesystem. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/227 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/228 -->
# sources/test-tools/xfstests/tests/btrfs/228

## Purpose
Test correct operation of free objectid related functionality create a new subvolume to validate its objectid is initialized accordingly, the expected value is 256 as this is the first free objectid in a new file system Subvolume creation used to commit the transaction used to create it, but after the patch "btrfs: don't commit transaction for every subvol create", that changed, so sync the fs to commit any open transaction. create new file in the new subvolume to validate its objectid is set as expected. In this subset it primarily covers multi-device, RAID, seed/sprout, or device-management paths, subvolume and snapshot metadata.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick volume`. Requirement and capability gates: line 14: `_require_scratch`; line 15: `_require_btrfs_command inspect-internal dump-tree`. Local helper surface: no custom shell functions beyond the linear test body. Important command/API calls include line 14: `_require_scratch`; line 15: `_require_btrfs_command inspect-internal dump-tree`; line 17: `_scratch_mkfs > /dev/null`; line 18: `_scratch_mount`; line 23: `$BTRFS_UTIL_PROG subvolume create $SCRATCH_MNT/newvol >> $seqres.full 2>&1 || _fail "couldn't create subvol"`; line 29: `$BTRFS_UTIL_PROG filesystem sync $SCRATCH_MNT`; line 31: `$BTRFS_UTIL_PROG inspect-internal dump-tree -t1 $SCRATCH_DEV | grep -q "256 ROOT_ITEM" || _fail "First subvol with id 256 doesn't exist"`; line 36: `touch $SCRATCH_MNT/newvol/file1 || _fail "Cannot create file in new subvol"`; line 39: `sync`; line 43: `$BTRFS_UTIL_PROG inspect-internal dump-tree -t5 $SCRATCH_DEV | grep -A2 "256 DIR_ITEM 1903355334" > $output_file`; line 54: `$BTRFS_UTIL_PROG inspect-internal dump-tree -t256 $SCRATCH_DEV > $output_file`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick volume`, install cleanup if needed, enforce requirements, then formats scratch storage, mounts the test filesystem, creates or deletes subvolumes/snapshots. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Snapshot and subvolume roots are deliberate persistent state used to test root items, received UUIDs, cleaner behavior, and metadata references. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through btrfs-progs. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 228 | Silence is golden`.

## Risks and Edge Cases
the main risk is silent metadata or persistence regression that only appears after remount, receive, check, or explicit content comparison. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/228 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/229 -->
# sources/test-tools/xfstests/tests/btrfs/229

## Purpose
Test that an incremental send operation correctly issues clone operations for a file that had different parts of one of its extents cloned into itself, at different offsets, and a large part of that extent was overwritten, so all the reflinks only point to subranges of the extent. Override the default cleanup function. Create our test file with a single and large extent (1M) and with different content for different file ranges that will be reflinked later. Now create the base snapshot, which is going to be the parent snapshot for a later incremental send. In this subset it primarily covers Btrfs send/receive stream generation and replay, reflink/clone extent sharing, subvolume and snapshot metadata.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick send clone`. Requirement and capability gates: line 26: `_require_test`; line 27: `_require_scratch_reflink`. Local helper surface: `_cleanup()` (line 16). Important command/API calls include line 13: `_begin_fstest auto quick send clone`; line 19: `rm -fr $send_files_dir`; line 24: `. ./common/reflink`; line 27: `_require_scratch_reflink`; line 29: `send_files_dir=$TEST_DIR/btrfs-test-$seq`; line 32: `mkdir $send_files_dir`; line 34: `_scratch_mkfs >>$seqres.full 2>&1`; line 35: `_scratch_mount`; line 39: `$XFS_IO_PROG -f -c "pwrite -S 0xab 0 128K" -c "pwrite -S 0xcd 128K 128K" -c "pwrite -S 0xef 256K 256K" -c "pwrite -S 0x1a 512K 512K" $SCRATCH_MNT/foobar | _filter_xfs_io`; line 48: `$BTRFS_UTIL_PROG subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/mysnap1 > /dev/null`; line 51: `$BTRFS_UTIL_PROG send -f $send_files_dir/1.snap $SCRATCH_MNT/mysnap1 2>&1 1>/dev/null | _filter_scratch`; line 62: `$XFS_IO_PROG -c "reflink $SCRATCH_MNT/foobar 64K 1M 960K" -c "reflink $SCRATCH_MNT/foobar 0K 512K 256K" -c "reflink $SCRATCH_MNT/foobar 512K 128K 256K" -c "pwrite -S 0x73 384K 640K`; line 68: `$BTRFS_UTIL_PROG subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/mysnap2 > /dev/null`; line 70: `$BTRFS_UTIL_PROG send -p $SCRATCH_MNT/mysnap1 -f $send_files_dir/2.snap $SCRATCH_MNT/mysnap2 2>&1 1>/dev/null | _filter_scratch`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick send clone`, install cleanup if needed, enforce requirements, then formats scratch storage, mounts the test filesystem, creates or deletes subvolumes/snapshots, generates and replays send streams, runs btrfs check or xfstests scratch checks, cycles mounts to force persistence. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. It persists send streams, fssum files, or received subvolumes in a temporary test directory and validates replay on a freshly formatted scratch filesystem. Snapshot and subvolume roots are deliberate persistent state used to test root items, received UUIDs, cleaner behavior, and metadata references. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through btrfs-progs, xfs_io. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 229 | wrote 131072/131072 bytes at offset 0 | XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec) | wrote 131072/131072 bytes at offset 131072 | XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec) | wrote 262144/262144 bytes at offset 262144 | XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec) | wrote 524288/524288 bytes at offset 524288 | ... (24 expected-output lines total)`.

## Risks and Edge Cases
send-stream ordering bugs can emit invalid paths, clone sources, link records, or parent references that only appear after replaying onto a clean filesystem. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/229 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/230 -->
# sources/test-tools/xfstests/tests/btrfs/230

## Purpose
Test if btrfs qgroup would crash if we're modifying the fs after exceeding the limit This test requires specific data space usage, skip if we have compression enabled. Need at least 2GiB Make sure the data reach disk so later qgroup scan can see it Set the limit to just 512MiB, which is way below the existing usage Touch above file, if kernel not patched, it will trigger an ASSERT() Even for patched kernel, we will still get EDQUOT error, but that. In this subset it primarily covers quota group accounting, assignment, limits, and rescan behavior.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick qgroup limit`. Requirement and capability gates: line 18: `_require_no_compress`; line 21: `_require_scratch_size $((2 * 1024 * 1024))`. Local helper surface: no custom shell functions beyond the linear test body. Important command/API calls include line 11: `_begin_fstest auto quick qgroup limit`; line 18: `_require_no_compress`; line 21: `_require_scratch_size $((2 * 1024 * 1024))`; line 22: `_scratch_mkfs > /dev/null 2>&1`; line 23: `_scratch_mount`; line 27: `sync`; line 29: `$BTRFS_UTIL_PROG quota enable $SCRATCH_MNT`; line 30: `_qgroup_rescan $SCRATCH_MNT >> $seqres.full`; line 33: `$BTRFS_UTIL_PROG qgroup limit 512M 0/5 $SCRATCH_MNT`; line 39: `touch $SCRATCH_MNT/file 2>&1 | _filter_scratch`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick qgroup limit`, install cleanup if needed, enforce requirements, then formats scratch storage, mounts the test filesystem, enables and inspects quota groups. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Quota state persists in qgroup metadata and is forced through rescans, syncs, commits, and filesystem checks. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through btrfs-progs. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 230 | touch: setting times of 'SCRATCH_MNT/file': Disk quota exceeded`.

## Risks and Edge Cases
qgroup tests are sensitive to delayed accounting, rescan completion, shared extents, and limit enforcement after transaction commits. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/230 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/231 -->
# sources/test-tools/xfstests/tests/btrfs/231

## Purpose
FSQA Test No. 231 Test that when using the NO_HOLES feature, if we truncate down a file, clone a file range covering only a hole into an offset beyond the current file size, and then fsync the file, after a power failure we get the expected file content and we do not get stale data corresponding to file extents that existed before truncating the file. Override the default cleanup function. Create our test file with 3 extents of 256K and a 256K hole at offset 256K. The file has a size of 1280K. In this subset it primarily covers reflink/clone extent sharing.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick clone log replay`. Requirement and capability gates: line 27: `_require_scratch`; line 28: `_require_btrfs_fs_feature "no_holes"`; line 29: `_require_btrfs_mkfs_feature "no-holes"`; line 30: `_require_dm_target flakey`; line 33: `_require_metadata_journaling $SCRATCH_DEV`. Local helper surface: `_cleanup()` (line 17). Important command/API calls include line 21: `rm -f $tmp.*`; line 27: `_require_scratch`; line 28: `_require_btrfs_fs_feature "no_holes"`; line 29: `_require_btrfs_mkfs_feature "no-holes"`; line 30: `_require_dm_target flakey`; line 32: `_scratch_mkfs -O no-holes >>$seqres.full 2>&1`; line 33: `_require_metadata_journaling $SCRATCH_DEV`; line 35: `_scratch_mount`; line 39: `$XFS_IO_PROG -f -s -c "pwrite -S 0xab -b 256K 0 256K" -c "pwrite -S 0xcd -b 256K 512K 256K" -c "pwrite -S 0xef -b 256K 768K 256K" -c "pwrite -S 0x73 -b 256K 1024K 256K" $SCRATCH_MN`; line 48: `sync`; line 54: `$XFS_IO_PROG -c "truncate 800K" -c "fsync" $SCRATCH_MNT/foobar`; line 58: `$XFS_IO_PROG -c "reflink $SCRATCH_MNT/foobar 256K 1024K 256K" -c "fsync" $SCRATCH_MNT/foobar | _filter_xfs_io`; line 68: `_flakey_drop_and_remount`; line 76: `_scratch_unmount`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick clone log replay`, install cleanup if needed, enforce requirements, then formats scratch storage, mounts the test filesystem, cycles mounts to force persistence. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through xfs_io. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 231 | wrote 262144/262144 bytes at offset 0 | XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec) | wrote 262144/262144 bytes at offset 524288 | XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec) | wrote 262144/262144 bytes at offset 786432 | XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec) | wrote 262144/262144 bytes at offset 1048576 | ... (35 expected-output lines total)`.

## Risks and Edge Cases
the main risk is silent metadata or persistence regression that only appears after remount, receive, check, or explicit content comparison. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/231 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/232 -->
# sources/test-tools/xfstests/tests/btrfs/232

## Purpose
Test that performing io and exhausting qgroup limit won't deadlock. This exercises issues fixed by the following kernel commits: 4f6a49de64fd ("btrfs: unlock extents in btrfs_zero_range in case of quota reservation errors") 4d14c5cde5c2 ("btrfs: don't flush from btrfs_delayed_inode_reserve_metadata") This test requires specific data space usage, skip if we have compression enabled. Make sure the data reach disk so later qgroup scan can see it set the limit to 1 g, leaving us just 100mb of slack space. In this subset it primarily covers quota group accounting, assignment, limits, and rescan behavior.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick qgroup limit`. Requirement and capability gates: line 34: `_require_no_compress`; line 36: `_require_scratch_size $((2 * 1024 * 1024))`. Local helper surface: `writer()` (line 19). Important command/API calls include line 15: `_begin_fstest auto quick qgroup limit`; line 34: `_require_no_compress`; line 36: `_require_scratch_size $((2 * 1024 * 1024))`; line 37: `_scratch_mkfs > /dev/null 2>&1`; line 38: `_scratch_mount`; line 42: `sync`; line 44: `$BTRFS_UTIL_PROG quota enable $SCRATCH_MNT`; line 45: `_qgroup_rescan $SCRATCH_MNT >> $seqres.full`; line 47: `$BTRFS_UTIL_PROG qgroup limit 1G 0/5 $SCRATCH_MNT`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick qgroup limit`, install cleanup if needed, enforce requirements, then formats scratch storage, mounts the test filesystem, enables and inspects quota groups. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Quota state persists in qgroup metadata and is forced through rescans, syncs, commits, and filesystem checks. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through btrfs-progs. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 232 | Silence is golden`.

## Risks and Edge Cases
qgroup tests are sensitive to delayed accounting, rescan completion, shared extents, and limit enforcement after transaction commits. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/232 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/233 -->
# sources/test-tools/xfstests/tests/btrfs/233

## Purpose
FSQA Test No. 233 Test that subvolume deletion is resumed on RW mounts, that it is not performed on RO mounts and that after remounting a filesystem from RO to RW mode, it is performed. Override the default cleanup function. In this subset it primarily covers multi-device, RAID, seed/sprout, or device-management paths, mount and remount option semantics, subvolume and snapshot metadata.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick subvol remount`. Requirement and capability gates: line 26: `_require_scratch`; line 27: `_require_dm_target flakey`; line 28: `_require_btrfs_command inspect-internal dump-tree`; line 31: `_require_metadata_journaling $SCRATCH_DEV`. Local helper surface: `_cleanup()` (line 15), `check_subvol_orphan_item_exists()` (line 35), `check_subvol_orphan_item_not_exists()` (line 43), `check_subvol_btree_exists()` (line 52), `check_subvol_btree_not_exists()` (line 59), `create_subvol_with_orphan()` (line 66). Important command/API calls include line 28: `_require_btrfs_command inspect-internal dump-tree`; line 30: `_scratch_mkfs >>$seqres.full 2>&1`; line 33: `_scratch_mount`; line 35: `check_subvol_orphan_item_exists()`; line 38: `$BTRFS_UTIL_PROG inspect-internal dump-tree -t 1 $SCRATCH_DEV | grep -q 'ORPHAN ORPHAN_ITEM 256'`; line 40: `[ $? -ne 0 ] && echo "subvolume orphan item is missing"`; line 43: `check_subvol_orphan_item_not_exists()`; line 49: `[ $? -eq 0 ] && echo "subvolume orphan item still exists"`; line 52: `check_subvol_btree_exists()`; line 54: `$BTRFS_UTIL_PROG inspect-internal dump-tree $SCRATCH_DEV | grep -q 'file tree key (256 ROOT_ITEM 0)'`; line 56: `[ $? -ne 0 ] && echo "subvolume btree is missing"`; line 59: `check_subvol_btree_not_exists()`; line 63: `[ $? -eq 0 ] && echo "subvolume btree still exists"`; line 68: `$BTRFS_UTIL_PROG subvolume create $SCRATCH_MNT/testsv | _filter_scratch`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick subvol remount`, install cleanup if needed, enforce requirements, then formats scratch storage, mounts the test filesystem, creates or deletes subvolumes/snapshots, runs btrfs check or xfstests scratch checks, cycles mounts to force persistence. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Snapshot and subvolume roots are deliberate persistent state used to test root items, received UUIDs, cleaner behavior, and metadata references. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through btrfs-progs. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 233 | Create subvolume 'SCRATCH_MNT/testsv' | Delete subvolume 'SCRATCH_MNT/testsv' | Create subvolume 'SCRATCH_MNT/testsv' | Delete subvolume 'SCRATCH_MNT/testsv'`.

## Risks and Edge Cases
the main risk is silent metadata or persistence regression that only appears after remount, receive, check, or explicit content comparison. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/233 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/234 -->
# sources/test-tools/xfstests/tests/btrfs/234

## Purpose
Test cases where a direct IO write, with O_DSYNC, can not be done and has to fallback to a buffered write. Create a test file with compression enabled (chattr +c). Now do a buffered write to create compressed extents. Now do the direct IO write with O_DSYNC into a file range that contains compressed extents. It should fallback to buffered IO and succeed. Now try doing a direct IO write, with O_DSYNC, for a range that starts with non-aligned offset. It should also fallback to buffered IO and succeed. Unmount, mount again, and verify we have the expected data. In this subset it primarily covers Btrfs filesystem behavior through xfstests shell orchestration.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick compress rw`. Requirement and capability gates: line 16: `_require_scratch`; line 17: `_require_odirect`; line 18: `_require_btrfs_no_nodatacow`; line 19: `_require_chattr c`. Local helper surface: no custom shell functions beyond the linear test body. Important command/API calls include line 16: `_require_scratch`; line 17: `_require_odirect`; line 18: `_require_btrfs_no_nodatacow`; line 19: `_require_chattr c`; line 21: `_scratch_mkfs >>$seqres.full 2>&1`; line 22: `_scratch_mount`; line 25: `touch $SCRATCH_MNT/foo`; line 29: `$XFS_IO_PROG -s -c "pwrite -S 0xab -b 1M 0 1M" $SCRATCH_MNT/foo | _filter_xfs_io`; line 33: `$XFS_IO_PROG -d -s -c "pwrite -S 0xcd 512K 512K" $SCRATCH_MNT/foo | _filter_xfs_io`; line 37: `$XFS_IO_PROG -f -d -s -c "pwrite -S 0xef 1111 512K" $SCRATCH_MNT/bar | _filter_xfs_io`; line 40: `_scratch_cycle_mount`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick compress rw`, install cleanup if needed, enforce requirements, then formats scratch storage, mounts the test filesystem, cycles mounts to force persistence. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through xfs_io. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 234 | wrote 1048576/1048576 bytes at offset 0 | XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec) | wrote 524288/524288 bytes at offset 524288 | XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec) | wrote 524288/524288 bytes at offset 1111 | XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec) | File foo data: | ... (21 expected-output lines total)`.

## Risks and Edge Cases
the main risk is silent metadata or persistence regression that only appears after remount, receive, check, or explicit content comparison. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/234 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/235 -->
# sources/test-tools/xfstests/tests/btrfs/235

## Purpose
Test that if we set a capability on a file but not on the next files we create, send/receive operations only apply the capability to the first file, the one for which we have set a capability. Override the default cleanup function. Set a capability only on file foo. Note that file foo has a lower inode number then files bar and baz - we want to test that if a file with a lower inode number has a capability set, after a send/receive, the capability is not set on the next files that have higher inode numbers. Now create the base snapshot, which is going to be the parent snapshot for. In this subset it primarily covers Btrfs send/receive stream generation and replay, subvolume and snapshot metadata.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick send`. Requirement and capability gates: line 24: `_require_test`; line 25: `_require_scratch`; line 26: `_require_command "$SETCAP_PROG" setcap`; line 27: `_require_command "$GETCAP_PROG" getcap`. Local helper surface: `_cleanup()` (line 15). Important command/API calls include line 12: `_begin_fstest auto quick send`; line 18: `rm -fr $send_files_dir`; line 19: `rm -f $tmp.*`; line 24: `_require_test`; line 25: `_require_scratch`; line 26: `_require_command "$SETCAP_PROG" setcap`; line 27: `_require_command "$GETCAP_PROG" getcap`; line 29: `send_files_dir=$TEST_DIR/btrfs-test-$seq`; line 32: `mkdir $send_files_dir`; line 34: `_scratch_mkfs >>$seqres.full 2>&1`; line 35: `_scratch_mount`; line 37: `touch $SCRATCH_MNT/foo`; line 38: `touch $SCRATCH_MNT/bar`; line 39: `touch $SCRATCH_MNT/baz`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick send`, install cleanup if needed, enforce requirements, then formats scratch storage, mounts the test filesystem, creates or deletes subvolumes/snapshots, generates and replays send streams, cycles mounts to force persistence. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. It persists send streams, fssum files, or received subvolumes in a temporary test directory and validates replay on a freshly formatted scratch filesystem. Snapshot and subvolume roots are deliberate persistent state used to test root items, received UUIDs, cleaner behavior, and metadata references. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through btrfs-progs. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 235 | At subvol SCRATCH_MNT/mysnap1 | At subvol SCRATCH_MNT/mysnap2 | At subvol mysnap1 | File mysnap1/foo capabilities: | SCRATCH_MNT/mysnap1/foo cap_net_raw=p | File mysnap1/bar capabilities: | File mysnap1/baz capabilities: | ... (17 expected-output lines total)`.

## Risks and Edge Cases
send-stream ordering bugs can emit invalid paths, clone sources, link records, or parent references that only appear after replaying onto a clean filesystem. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/235 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/236 -->
# sources/test-tools/xfstests/tests/btrfs/236

## Purpose
FSQA Test No. 236 Test for fsync data loss after renaming a file or adding a hard link, with a previous fsync of another file, as well as that mtime and ctime are correct. Test both with COW and NOCOW writes. Override the default cleanup function. The comments inside the function mentioning specific inode numbers and IDs (transactions, log commits, etc) are for the case where the function is run on a freshly created filesystem, but the logic and reasoning still applies for future invocations. In this subset it primarily covers Btrfs filesystem behavior through xfstests shell orchestration.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick log`. Requirement and capability gates: line 25: `_require_scratch`; line 26: `_require_dm_target flakey`; line 157: `_require_metadata_journaling $SCRATCH_DEV`. Local helper surface: `_cleanup()` (line 15), `test_fsync()` (line 32). Important command/API calls include line 19: `rm -f $tmp.*`; line 25: `_require_scratch`; line 26: `_require_dm_target flakey`; line 32: `test_fsync()`; line 52: `touch $bar`; line 68: `$XFS_IO_PROG -f -c "pwrite -S 0xab 0 1M" -c "fsync" $baz >>$seqres.full`; line 85: `mv $baz $foo`; line 87: `ln $baz $foo`; line 98: `$XFS_IO_PROG -c "pwrite -S 0xcd 0 1M" $foo >>$seqres.full`; line 103: `$XFS_IO_PROG -c "fsync" $bar`; line 124: `$XFS_IO_PROG -c "fsync" $foo`; line 131: `digest_before=$(_md5_checksum $foo)`; line 132: `mtime_before=$(stat -c %Y $foo)`; line 133: `ctime_before=$(stat -c %Z $foo)`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick log`, install cleanup if needed, enforce requirements, then formats scratch storage, mounts the test filesystem, runs btrfs check or xfstests scratch checks, cycles mounts to force persistence. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through xfs_io. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 236 | Testing fsync after rename with COW writes | Testing fsync after link with COW writes | Testing fsync after rename with NOCOW writes | Testing fsync after link with NOCOW writes`.

## Risks and Edge Cases
the main risk is silent metadata or persistence regression that only appears after remount, receive, check, or explicit content comparison. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/236 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/237 -->
# sources/test-tools/xfstests/tests/btrfs/237

## Purpose
Test that zone autoreclaim works as expected, that is: if the dirty threshold is exceeded the data gets relocated to new block group and the old block group gets deleted. On block group deletion, the underlying device zone also needs to be reset. This test requires specific data space usage, skip if we have compression enabled. Create a minimal FS to kick the reclaim process step 1, fill FS over $fillsize. In this subset it primarily covers multi-device, RAID, seed/sprout, or device-management paths.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick zone balance`. Requirement and capability gates: line 17: `_require_scratch`; line 18: `_require_btrfs_command inspect-internal dump-tree`; line 19: `_require_btrfs_command filesystem sync`; line 20: `_require_command "$BLKZONE_PROG" blkzone`; line 21: `_require_zoned_device "$SCRATCH_DEV"`; line 25: `_require_no_compress`. Local helper surface: `get_data_bg()` (line 27), `get_data_bg_physical()` (line 35). Important command/API calls include line 13: `_begin_fstest auto quick zone balance`; line 17: `_require_scratch`; line 18: `_require_btrfs_command inspect-internal dump-tree`; line 19: `_require_btrfs_command filesystem sync`; line 20: `_require_command "$BLKZONE_PROG" blkzone`; line 21: `_require_zoned_device "$SCRATCH_DEV"`; line 25: `_require_no_compress`; line 29: `$BTRFS_UTIL_PROG inspect-internal dump-tree -t CHUNK $SCRATCH_DEV | grep -A 1 "CHUNK_ITEM" | grep -B 1 "type DATA" | grep -Eo "CHUNK_ITEM [[:digit:]]+" | cut -d ' ' -f 2 | tail -n `; line 38: `$BTRFS_UTIL_PROG inspect-internal dump-tree -t CHUNK $SCRATCH_DEV | grep -A 4 CHUNK_ITEM | grep -A 3 'type DATA\|SINGLE' | grep -Eo 'offset [[:digit:]]+'| cut -d ' ' -f 2 | tail -n`; line 44: `$BLKZONE_PROG report $SCRATCH_DEV | grep -q -e "nw" && _notrun "test is unreliable on devices with conventional zones"`; line 51: `devsize=$(($(_get_device_size $SCRATCH_DEV) * 1024))`; line 54: `_scratch_mkfs_sized $fssize >> $seqres.full 2>&1`; line 56: `_scratch_mkfs >> $seqres.full 2>&1`; line 58: `_scratch_mount -o commit=1 # 1s commit time to speed up test`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick zone balance`, install cleanup if needed, enforce requirements, then formats scratch storage, mounts the test filesystem. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Multi-device tests allocate scratch pool devices and leave correctness evidence in chunk maps, device registry state, degraded mounts, and btrfs check results. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through btrfs-progs, xfs_io. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 237 | Silence is golden`.

## Risks and Edge Cases
device topology tests can expose races in device scan state, degraded mounts, stripe geometry, replacement, and cleanup of scratch device pools. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/237 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/238 -->
# sources/test-tools/xfstests/tests/btrfs/238

## Purpose
Check seed device integrity after fstrim on the sprout device. Mount the seed device and add the rw device Now remount writeable sprout device, create some data and run fstrim Verify seed device is all ok success, all done. In this subset it primarily covers multi-device, RAID, seed/sprout, or device-management paths, mount and remount option semantics, discard/trim behavior.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick seed trim`. Requirement and capability gates: line 16: `_require_command "$BTRFS_TUNE_PROG" btrfstune`; line 17: `_require_fstrim`; line 18: `_require_scratch_dev_pool 2`; line 40: `_require_batched_discard $SCRATCH_MNT`. Local helper surface: no custom shell functions beyond the linear test body. Important command/API calls include line 14: `_fixed_by_kernel_commit 5e753a817b2d "btrfs: fix unmountable seed device after fstrim"`; line 16: `_require_command "$BTRFS_TUNE_PROG" btrfstune`; line 17: `_require_fstrim`; line 18: `_require_scratch_dev_pool 2`; line 19: `_scratch_dev_pool_get 2`; line 25: `_mount $seed $SCRATCH_MNT`; line 27: `$XFS_IO_PROG -f -c "pwrite -S 0xab 0 1M" $SCRATCH_MNT/foo > /dev/null`; line 28: `_scratch_unmount`; line 29: `$BTRFS_TUNE_PROG -S 1 $seed`; line 32: `_mount $seed $SCRATCH_MNT 2>&1 | _filter_ro_mount | _filter_scratch`; line 33: `md5sum $SCRATCH_MNT/foo | _filter_scratch`; line 35: `$BTRFS_UTIL_PROG device add -f $sprout $SCRATCH_MNT >> $seqres.full`; line 39: `_mount $sprout $SCRATCH_MNT`; line 40: `_require_batched_discard $SCRATCH_MNT`. It documents fixed kernel commit context at line 14: `_fixed_by_kernel_commit 5e753a817b2d \`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick seed trim`, install cleanup if needed, enforce requirements, then mounts the test filesystem, runs btrfs check or xfstests scratch checks, cycles mounts to force persistence. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Multi-device tests allocate scratch pool devices and leave correctness evidence in chunk maps, device registry state, degraded mounts, and btrfs check results. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through btrfs-progs, xfs_io, btrfstune, fstrim/discard support. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 238 | mount: device write-protected, mounting read-only | 096003817ad2638000a6836e55866697  SCRATCH_MNT/foo | mount: device write-protected, mounting read-only | 096003817ad2638000a6836e55866697  SCRATCH_MNT/foo`.

## Risks and Edge Cases
device topology tests can expose races in device scan state, degraded mounts, stripe geometry, replacement, and cleanup of scratch device pools; discard tests are sensitive to block-device discard support and whether allocated extents are accidentally punched on replacement devices. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/238 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/239 -->
# sources/test-tools/xfstests/tests/btrfs/239

## Purpose
FSQA Test No. 239 Test a particular scenario where we fsync a directory, then move one of its children directories into another directory and then finally sync the log trees by fsyncing any other inode. We want to check that after a power failure we are able to mount the filesystem and that the moved directory exists only as a child of the directory we moved it into. Override the default cleanup function. The test requires a very specific layout of keys and items in the fs/subvolume btree to trigger a bug. So we want to make sure that on whatever platform we. In this subset it primarily covers multi-device, RAID, seed/sprout, or device-management paths, subvolume and snapshot metadata.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick log`. Requirement and capability gates: line 27: `_require_scratch`; line 28: `_require_dm_target flakey`; line 39: `_require_metadata_journaling $SCRATCH_DEV`. Local helper surface: `_cleanup()` (line 17). Important command/API calls include line 21: `rm -f $tmp.*`; line 27: `_require_scratch`; line 28: `_require_dm_target flakey`; line 38: `_scratch_mkfs "-n 65536" >>$seqres.full 2>&1`; line 39: `_require_metadata_journaling $SCRATCH_DEV`; line 41: `_scratch_mount`; line 44: `mkdir $SCRATCH_MNT/testdir`; line 81: `mkdir $SCRATCH_MNT/testdir/dira`; line 93: `$XFS_IO_PROG -c "fsync" $SCRATCH_MNT`; line 96: `sync`; line 141: `$XFS_IO_PROG -c "fsync" $SCRATCH_MNT/testdir`; line 150: `mv $SCRATCH_MNT/testdir/dira $SCRATCH_MNT/`; line 156: `$XFS_IO_PROG -c "pwrite -S 0xab 0 64K" -c "fsync" $SCRATCH_MNT/testdir/file1 >>$seqres.full`; line 188: `_flakey_drop_and_remount`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick log`, install cleanup if needed, enforce requirements, then formats scratch storage, mounts the test filesystem, cycles mounts to force persistence. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through xfs_io. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 239 | File SCRATCH_MNT/testdir/file1 data: | 0000000 ab ab ab ab ab ab ab ab ab ab ab ab ab ab ab ab | * | 0065536`.

## Risks and Edge Cases
the main risk is silent metadata or persistence regression that only appears after remount, receive, check, or explicit content comparison. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/239 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/240 -->
# sources/test-tools/xfstests/tests/btrfs/240

## Purpose
FSQA Test No. 240 Test a scenario where we do several partial writes into multiple preallocated extents across two transactions and with several fsyncs in between. The goal is to check that the fsyncs succeed. This scenario used to trigger an -EIO failure on the last fsync and turn the filesystem to RO mode because of a transaction abort. Override the default cleanup function. Create our test file with 2 preallocated extents. Leave a 1M hole between them to ensure that we get two file extent items that will never be merged into a. In this subset it primarily covers Btrfs filesystem behavior through xfstests shell orchestration.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick prealloc log`. Requirement and capability gates: line 27: `_require_scratch`; line 28: `_require_dm_target flakey`; line 29: `_require_xfs_io_command "falloc"`; line 32: `_require_metadata_journaling $SCRATCH_DEV`. Local helper surface: `_cleanup()` (line 17). Important command/API calls include line 21: `rm -f $tmp.*`; line 27: `_require_scratch`; line 28: `_require_dm_target flakey`; line 29: `_require_xfs_io_command "falloc"`; line 31: `_scratch_mkfs >>$seqres.full 2>&1`; line 32: `_require_metadata_journaling $SCRATCH_DEV`; line 34: `_scratch_mount`; line 42: `$XFS_IO_PROG -f -c "falloc 0 1M" -c "falloc 3M 3M" $SCRATCH_MNT/foobar`; line 70: `$XFS_IO_PROG -c "pwrite -S 0xab 3M 1M" -c "pwrite -S 0xef 5M 1M" -c "fsync" $SCRATCH_MNT/foobar | _filter_xfs_io`; line 77: `sync`; line 95: `$XFS_IO_PROG -c "pwrite -S 0xcd 4M 1M" -c "fsync" $SCRATCH_MNT/foobar | _filter_xfs_io`; line 145: `$XFS_IO_PROG -c "pwrite -S 0xff 0 1M" -c "truncate 5M" -c "fsync" $SCRATCH_MNT/foobar | _filter_xfs_io`; line 155: `_flakey_drop_and_remount`; line 160: `_scratch_unmount`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick prealloc log`, install cleanup if needed, enforce requirements, then formats scratch storage, mounts the test filesystem, cycles mounts to force persistence. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through xfs_io. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 240 | wrote 1048576/1048576 bytes at offset 3145728 | XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec) | wrote 1048576/1048576 bytes at offset 5242880 | XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec) | wrote 1048576/1048576 bytes at offset 4194304 | XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec) | wrote 1048576/1048576 bytes at offset 0 | ... (29 expected-output lines total)`.

## Risks and Edge Cases
the main risk is silent metadata or persistence regression that only appears after remount, receive, check, or explicit content comparison. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/240 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/241 -->
# sources/test-tools/xfstests/tests/btrfs/241

## Purpose
Test that an incremental send operation succeeds, and produces the correct results, after renaming and moving around directories and files with multiple hardlinks, in such a way that one of the files gets the old name and location of a directory and another name (hardlink) with the old name and location of another file that was located in that same directory. Override the default cleanup function. Create our test files and directory. Inode 259 (file3) has two hard links. Filesystem looks like: . (ino 256). In this subset it primarily covers Btrfs send/receive stream generation and replay.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick send`. Requirement and capability gates: line 26: `_require_test`; line 27: `_require_scratch`; line 28: `_require_fssum`. Local helper surface: `_cleanup()` (line 17). Important command/API calls include line 14: `_begin_fstest auto quick send`; line 20: `rm -fr $send_files_dir`; line 30: `send_files_dir=$TEST_DIR/btrfs-test-$seq`; line 33: `mkdir $send_files_dir`; line 35: `_scratch_mkfs >>$seqres.full 2>&1`; line 36: `_scratch_mount`; line 58: `$BTRFS_UTIL_PROG subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/mysnap1 > /dev/null`; line 61: `$BTRFS_UTIL_PROG send -f $send_files_dir/1.snap $SCRATCH_MNT/mysnap1 2>&1 1>/dev/null | _filter_scratch`; line 90: `$BTRFS_UTIL_PROG subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/mysnap2 > /dev/null`; line 92: `$BTRFS_UTIL_PROG send -p $SCRATCH_MNT/mysnap1 -f $send_files_dir/2.snap $SCRATCH_MNT/mysnap2 2>&1 1>/dev/null | _filter_scratch`; line 95: `$FSSUM_PROG -A -f -w $send_files_dir/1.fssum $SCRATCH_MNT/mysnap1`; line 96: `$FSSUM_PROG -A -f -w $send_files_dir/2.fssum -x $SCRATCH_MNT/mysnap2/mysnap1 $SCRATCH_MNT/mysnap2`; line 107: `$BTRFS_UTIL_PROG receive -f $send_files_dir/1.snap $SCRATCH_MNT > /dev/null`; line 133: `$BTRFS_UTIL_PROG receive -f $send_files_dir/2.snap $SCRATCH_MNT > /dev/null`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick send`, install cleanup if needed, enforce requirements, then formats scratch storage, mounts the test filesystem, creates or deletes subvolumes/snapshots, generates and replays send streams, cycles mounts to force persistence. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. It persists send streams, fssum files, or received subvolumes in a temporary test directory and validates replay on a freshly formatted scratch filesystem. Snapshot and subvolume roots are deliberate persistent state used to test root items, received UUIDs, cleaner behavior, and metadata references. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through btrfs-progs, fssum. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 241 | At subvol SCRATCH_MNT/mysnap1 | At subvol SCRATCH_MNT/mysnap2 | At subvol mysnap1 | OK | OK`.

## Risks and Edge Cases
send-stream ordering bugs can emit invalid paths, clone sources, link records, or parent references that only appear after replaying onto a clean filesystem. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/241 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/242 -->
# sources/test-tools/xfstests/tests/btrfs/242

## Purpose
Test that fstrim can run on the degraded filesystem Kernel requires fix for the null pointer deref in btrfs_trim_fs() [patch] btrfs: check for missing device in btrfs_trim_fs Add a test file with some data. Unmount the filesystem. Mount the filesystem in degraded mode Run fstrim, it should skip on the missing device. Verify data integrity as in the golden output. In this subset it primarily covers multi-device, RAID, seed/sprout, or device-management paths, discard/trim behavior.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick volume trim raid`. Requirement and capability gates: line 16: `_require_btrfs_forget_or_module_loadable`; line 17: `_require_scratch_dev_pool 2`; line 24: `_require_batched_discard $SCRATCH_MNT`. Local helper surface: no custom shell functions beyond the linear test body. Important command/API calls include line 16: `_require_btrfs_forget_or_module_loadable`; line 17: `_require_scratch_dev_pool 2`; line 19: `_scratch_dev_pool_get 2`; line 22: `_scratch_pool_mkfs "-m raid1 -d raid1"`; line 23: `_scratch_mount`; line 24: `_require_batched_discard $SCRATCH_MNT`; line 27: `$XFS_IO_PROG -f -c "pwrite -S 0xab 0 10M" $SCRATCH_MNT/foo | _filter_xfs_io`; line 30: `_scratch_unmount`; line 33: `_btrfs_forget_or_module_reload`; line 34: `_mount -o degraded $dev1 $SCRATCH_MNT`; line 43: `_scratch_dev_pool_put`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick volume trim raid`, install cleanup if needed, enforce requirements, then mounts the test filesystem, cycles mounts to force persistence. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Multi-device tests allocate scratch pool devices and leave correctness evidence in chunk maps, device registry state, degraded mounts, and btrfs check results. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through xfs_io. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 242 | wrote 10485760/10485760 bytes at offset 0 | XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec) | File foo data: | 0000000 ab ab ab ab ab ab ab ab ab ab ab ab ab ab ab ab | * | 10485760`.

## Risks and Edge Cases
device topology tests can expose races in device scan state, degraded mounts, stripe geometry, replacement, and cleanup of scratch device pools; discard tests are sensitive to block-device discard support and whether allocated extents are accidentally punched on replacement devices. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/242 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/243 -->
# sources/test-tools/xfstests/tests/btrfs/243

## Purpose
Test that if we explicitly fsync a file that was previously renamed and its size was increased through a truncate operation, after a power failure the file has the size set by truncate operation. In between the truncation and the fsync, there was a rename of another file in the same directory and that file was also fsynced before we fsynced the file that was truncated. Create our test files. Make them durably persisted. Fsync bar, this will be a noop since the file has not yet been modified in the current transaction. The goal here is to clear BTRFS_INODE_NEEDS_FULL_SYNC. In this subset it primarily covers Btrfs filesystem behavior through xfstests shell orchestration.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick log`. Requirement and capability gates: line 26: `_require_scratch`; line 27: `_require_dm_target flakey`; line 32: `_require_metadata_journaling $SCRATCH_DEV`. Local helper surface: `_cleanup()` (line 16). Important command/API calls include line 20: `rm -r -f $tmp.*`; line 26: `_require_scratch`; line 27: `_require_dm_target flakey`; line 29: `rm -f $seqres.full`; line 31: `_scratch_mkfs >>$seqres.full 2>&1`; line 32: `_require_metadata_journaling $SCRATCH_DEV`; line 34: `_scratch_mount`; line 37: `touch $SCRATCH_MNT/foo`; line 38: `$XFS_IO_PROG -f -c "pwrite -S 0xab 0 1M" $SCRATCH_MNT/bar | _filter_xfs_io`; line 41: `sync`; line 46: `$XFS_IO_PROG -c "fsync" $SCRATCH_MNT/bar`; line 49: `mv $SCRATCH_MNT/bar $SCRATCH_MNT/bar2`; line 50: `mv $SCRATCH_MNT/foo $SCRATCH_MNT/foo2`; line 53: `$XFS_IO_PROG -c "truncate 2M" $SCRATCH_MNT/bar2`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick log`, install cleanup if needed, enforce requirements, then formats scratch storage, mounts the test filesystem, cycles mounts to force persistence. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through xfs_io. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 243 | wrote 1048576/1048576 bytes at offset 0 | XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec) | File bar2 content before power failure: | 0000000 ab ab ab ab ab ab ab ab ab ab ab ab ab ab ab ab | * | 1048576 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 | * | ... (15 expected-output lines total)`.

## Risks and Edge Cases
the main risk is silent metadata or persistence regression that only appears after remount, receive, check, or explicit content comparison. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/243 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/244 -->
# sources/test-tools/xfstests/tests/btrfs/244

## Purpose
Make sure "btrfs device remove" won't crash when non-existing devid is provided Override the default cleanup function. _cleanup() { cd / rm -r -f $tmp.* } Above created fs only contains one device with devid 1, device remove 3. In this subset it primarily covers multi-device, RAID, seed/sprout, or device-management paths.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick volume dangerous`. Requirement and capability gates: line 20: `_require_scratch`. Local helper surface: no custom shell functions beyond the linear test body. Important command/API calls include line 20: `_require_scratch`; line 22: `_scratch_mkfs >> $seqres.full 2>&1`; line 23: `_scratch_mount`; line 28: `$BTRFS_UTIL_PROG device remove 3 $SCRATCH_MNT`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick volume dangerous`, install cleanup if needed, enforce requirements, then formats scratch storage, mounts the test filesystem. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Multi-device tests allocate scratch pool devices and leave correctness evidence in chunk maps, device registry state, degraded mounts, and btrfs check results. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through btrfs-progs. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 244 | ERROR: error removing devid 3: No such file or directory`.

## Risks and Edge Cases
device topology tests can expose races in device scan state, degraded mounts, stripe geometry, replacement, and cleanup of scratch device pools. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/244 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/245 -->
# sources/test-tools/xfstests/tests/btrfs/245

## Purpose
Test that idmapped mounts behave correctly with btrfs specific features such as subvolume and snapshot creation and deletion. In this subset it primarily covers multi-device, RAID, seed/sprout, or device-management paths, subvolume and snapshot metadata.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick idmapped subvol`. Requirement and capability gates: line 15: `_require_idmapped_mounts`; line 16: `_require_test`; line 17: `_require_scratch`. Local helper surface: no custom shell functions beyond the linear test body. Important command/API calls include line 15: `_require_idmapped_mounts`; line 16: `_require_test`; line 17: `_require_scratch`; line 19: `_scratch_mkfs >> $seqres.full`; line 20: `_scratch_mount "-o user_subvol_rm_allowed" >> $seqres.full`; line 24: `$here/src/vfs/vfstest --test-btrfs --device "$TEST_DEV" --mountpoint "$TEST_DIR" --scratch-device "$SCRATCH_DEV" --scratch-mountpoint "$SCRATCH_MNT" --fstype "$FSTYP"`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick idmapped subvol`, install cleanup if needed, enforce requirements, then formats scratch storage, mounts the test filesystem. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Multi-device tests allocate scratch pool devices and leave correctness evidence in chunk maps, device registry state, degraded mounts, and btrfs check results. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through standard xfstests common helpers and btrfs-progs. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 245 | Silence is golden`.

## Risks and Edge Cases
device topology tests can expose races in device scan state, degraded mounts, stripe geometry, replacement, and cleanup of scratch device pools. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/245 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/246 -->
# sources/test-tools/xfstests/tests/btrfs/246

## Purpose
Make sure btrfs can create compressed inline extents Override the default cleanup function. If it's subpage case, we don't support inline extents creation for now. This should create compressed inline extent success, all done. In this subset it primarily covers Btrfs filesystem behavior through xfstests shell orchestration.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick compress`. Requirement and capability gates: line 21: `_require_scratch`; line 24: `_require_btrfs_inline_extents_creation`. Local helper surface: `_cleanup()` (line 13). Important command/API calls include line 16: `rm -r -f $tmp.*`; line 21: `_require_scratch`; line 24: `_require_btrfs_inline_extents_creation`; line 26: `_scratch_mkfs > /dev/null`; line 27: `_scratch_mount -o compress,max_inline=2048`; line 30: `$XFS_IO_PROG -f -c "pwrite 0 2048" $SCRATCH_MNT/foobar > /dev/null`; line 31: `ino=$(stat -c %i $SCRATCH_MNT/foobar)`; line 32: `echo "sha256sum before mount cycle"`; line 33: `sha256sum $SCRATCH_MNT/foobar | _filter_scratch`; line 34: `_scratch_cycle_mount`; line 35: `echo "sha256sum after mount cycle"`; line 37: `_scratch_unmount`; line 39: `$BTRFS_UTIL_PROG inspect dump-tree -t 5 $SCRATCH_DEV | grep "($ino EXTENT_DATA 0" -A2 > $tmp.dump-tree`; line 42: `cat $tmp.dump-tree >> $seqres.full`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick compress`, install cleanup if needed, enforce requirements, then formats scratch storage, mounts the test filesystem, cycles mounts to force persistence. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through btrfs-progs, xfs_io. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 246 | sha256sum before mount cycle | 0ca3bfdeda1ef5036bfa5dad078a9f15724e79cf296bd4388cf786bfaf4195d0  SCRATCH_MNT/foobar | sha256sum after mount cycle | 0ca3bfdeda1ef5036bfa5dad078a9f15724e79cf296bd4388cf786bfaf4195d0  SCRATCH_MNT/foobar`.

## Risks and Edge Cases
the main risk is silent metadata or persistence regression that only appears after remount, receive, check, or explicit content comparison. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/246 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/247 -->
# sources/test-tools/xfstests/tests/btrfs/247

## Purpose
Tests rename/exchange behavior when subvolumes are involved. Rename/exchanges across subvolumes are forbidden. This is also a regression test for 3f79f6f6247c ("btrfs: prevent rename2 from exchanging a subvol with a directory from different parents"). Create 2 subvols to use as parents for the rename ops Ensure cross subvol ops are forbidden Prepare a subvolume and a directory whose parents are different subvolumes Ensure exchanging a subvol with a dir when both parents are different fails Test also ordinary renames. In this subset it primarily covers multi-device, RAID, seed/sprout, or device-management paths, subvolume and snapshot metadata.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick rename subvol`. Requirement and capability gates: line 17: `_require_renameat2 exchange`; line 18: `_require_scratch`. Local helper surface: no custom shell functions beyond the linear test body. Important command/API calls include line 17: `_require_renameat2 exchange`; line 18: `_require_scratch`; line 20: `_scratch_mkfs >> $seqres.full 2>&1`; line 21: `_scratch_mount`; line 24: `$BTRFS_UTIL_PROG subvolume create $SCRATCH_MNT/subvol1 1>/dev/null`; line 25: `$BTRFS_UTIL_PROG subvolume create $SCRATCH_MNT/subvol2 1>/dev/null`; line 31: `$BTRFS_UTIL_PROG subvolume create $SCRATCH_MNT/subvol1/sub-subvol 1>/dev/null`; line 32: `mkdir $SCRATCH_MNT/subvol2/dir`; line 41: `echo "subvolumes rename"`; line 51: `mv $SCRATCH_MNT/subvol2/ $SCRATCH_MNT/subvol2.`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick rename subvol`, install cleanup if needed, enforce requirements, then formats scratch storage, mounts the test filesystem, creates or deletes subvolumes/snapshots. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Snapshot and subvolume roots are deliberate persistent state used to test root items, received UUIDs, cleaner behavior, and metadata references. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through btrfs-progs. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 247 | cross-subvol none/none -> No such file or directory | cross-subvol none/regu -> No such file or directory | cross-subvol none/symb -> No such file or directory | cross-subvol none/dire -> No such file or directory | cross-subvol none/tree -> No such file or directory | cross-subvol regu/none -> No such file or directory | cross-subvol regu/regu -> Invalid cross-device link | ... (54 expected-output lines total)`.

## Risks and Edge Cases
the main risk is silent metadata or persistence regression that only appears after remount, receive, check, or explicit content comparison. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/247 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/248 -->
# sources/test-tools/xfstests/tests/btrfs/248

## Purpose
Validate if the sysfs devinfo/<devid>/fsid behaves properly Steps: Create a sprout filesystem (an rw device on top of a seed device) Read the seed and sprout devices fsid from the superblock Validate with the sysfs fsid use the scratch device as a seed device use the spare device as a sprout device create seed device create a sprout device. In this subset it primarily covers multi-device, RAID, seed/sprout, or device-management paths.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick seed volume`. Requirement and capability gates: line 17: `_require_test`; line 18: `_require_scratch_dev_pool 2`; line 19: `_require_btrfs_forget_or_module_loadable`; line 20: `_require_command "$BTRFS_TUNE_PROG" btrfstune`; line 21: `_require_btrfs_command inspect-internal dump-super`; line 22: `_require_btrfs_sysfs_fsid`. Local helper surface: no custom shell functions beyond the linear test body. Important command/API calls include line 17: `_require_test`; line 18: `_require_scratch_dev_pool 2`; line 19: `_require_btrfs_forget_or_module_loadable`; line 20: `_require_command "$BTRFS_TUNE_PROG" btrfstune`; line 21: `_require_btrfs_command inspect-internal dump-super`; line 22: `_require_btrfs_sysfs_fsid`; line 24: `_scratch_dev_pool_get 1`; line 32: `_scratch_pool_mkfs >> $seqres.full 2>&1`; line 33: `$BTRFS_TUNE_PROG -S 1 $seed_dev`; line 34: `_scratch_mount >> $seqres.full 2>&1`; line 37: `$BTRFS_UTIL_PROG device add -f $SPARE_DEV $SCRATCH_MNT >> $seqres.full 2>&1`; line 38: `_scratch_unmount`; line 41: `seedfsid=$($BTRFS_UTIL_PROG inspect-internal dump-super $seed_dev |grep ^fsid | $AWK_PROG '{print $2}')`; line 43: `sproutfsid=$($BTRFS_UTIL_PROG inspect-internal dump-super $SPARE_DEV | grep ^fsid |$AWK_PROG '{print $2}')`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick seed volume`, install cleanup if needed, enforce requirements, then mounts the test filesystem, cycles mounts to force persistence. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Multi-device tests allocate scratch pool devices and leave correctness evidence in chunk maps, device registry state, degraded mounts, and btrfs check results. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through btrfs-progs, btrfstune. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 248 | Silence is golden`.

## Risks and Edge Cases
device topology tests can expose races in device scan state, degraded mounts, stripe geometry, replacement, and cleanup of scratch device pools. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/248 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/249 -->
# sources/test-tools/xfstests/tests/btrfs/249

## Purpose
Validate if the command 'btrfs filesystem usage' works with missing seed device Steps: Create a degraded raid1 seed device Create a sprout filesystem (an rw device on top of a seed device) Dump 'btrfs filesystem usage', check it didn't fail use the scratch devices as seed devices use the spare device as a sprout device create raid1 seed filesystem. In this subset it primarily covers multi-device, RAID, seed/sprout, or device-management paths.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick seed volume raid`. Requirement and capability gates: line 19: `_require_scratch_dev_pool 3`; line 20: `_require_command "$WIPEFS_PROG" wipefs`; line 21: `_require_btrfs_forget_or_module_loadable`. Local helper surface: no custom shell functions beyond the linear test body. Important command/API calls include line 19: `_require_scratch_dev_pool 3`; line 20: `_require_command "$WIPEFS_PROG" wipefs`; line 21: `_require_btrfs_forget_or_module_loadable`; line 22: `_wants_kernel_commit a26d60dedf9a "btrfs: sysfs: add devinfo/fsid to retrieve actual fsid from the device"`; line 24: `_fixed_by_git_commit btrfs-progs 32c2e57c65b9 "btrfs-progs: read fsid from the sysfs in device_is_seed"`; line 27: `_scratch_dev_pool_get 2`; line 37: `_scratch_pool_mkfs "-draid1 -mraid1" >> $seqres.full 2>&1`; line 38: `$BTRFS_TUNE_PROG -S 1 $seed_dev1`; line 40: `_btrfs_forget_or_module_reload`; line 41: `_mount -o degraded $seed_dev2 $SCRATCH_MNT >> $seqres.full 2>&1`; line 44: `$BTRFS_UTIL_PROG device add -f $SPARE_DEV $SCRATCH_MNT >> $seqres.full 2>&1`; line 47: `$BTRFS_UTIL_PROG filesystem usage $SCRATCH_MNT >> $seqres.full`; line 51: `_fail "FAILED: btrfs filesystem usage, ret $ret. Check btrfs.ko and btrfs-progs version."`; line 54: `_scratch_unmount`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick seed volume raid`, install cleanup if needed, enforce requirements, then mounts the test filesystem, cycles mounts to force persistence. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Multi-device tests allocate scratch pool devices and leave correctness evidence in chunk maps, device registry state, degraded mounts, and btrfs check results. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through btrfs-progs, btrfstune. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 249 | Silence is golden`.

## Risks and Edge Cases
device topology tests can expose races in device scan state, degraded mounts, stripe geometry, replacement, and cleanup of scratch device pools. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/249 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/250 -->
# sources/test-tools/xfstests/tests/btrfs/250

## Purpose
Test that if we write to a range of a NOCOW file that has allocated extents and there is not enough available free space for allocating new data extents, the write succeeds. Test for direct IO and buffered IO writes. The patch that fixes the direct IO case has the following subject: "btrfs: fix ENOSPC failure when attempting direct IO write into NOCOW range" Use a small fixed size filesystem so that it's quick to fill it up. Make sure the fs size is > 256M, so that the mixed block groups feature is not enabled by _scatch_mkfs_sized(), because we later want to not have more space available for allocating data extents but still have enough metadata. In this subset it primarily covers Btrfs filesystem behavior through xfstests shell orchestration.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick enospc`. Requirement and capability gates: line 25: `_require_scratch`; line 26: `_require_chattr C`; line 27: `_require_odirect`. Local helper surface: `_cleanup()` (line 17). Important command/API calls include line 20: `rm -r -f $tmp.*`; line 25: `_require_scratch`; line 26: `_require_chattr C`; line 27: `_require_odirect`; line 35: `_scratch_mkfs_sized $fs_size >>$seqres.full 2>&1`; line 36: `_scratch_mount`; line 39: `touch $SCRATCH_MNT/foobar`; line 47: `$XFS_IO_PROG -c "pwrite -S 0xab -b 1M 0 900M" $SCRATCH_MNT/foobar | _filter_xfs_io`; line 53: `$XFS_IO_PROG -d -c "pwrite -S 0xcd -b 10M 0 10M" $SCRATCH_MNT/foobar | _filter_xfs_io`; line 59: `$XFS_IO_PROG -c "pwrite -S 0xef -b 10M 10M 10M" $SCRATCH_MNT/foobar | _filter_xfs_io`; line 63: `_scratch_cycle_mount`; line 67: `echo "File data after mounting again the filesystem:"`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick enospc`, install cleanup if needed, enforce requirements, then formats scratch storage, mounts the test filesystem, cycles mounts to force persistence. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through xfs_io. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 250 | Creating test file with initial data... | wrote 943718400/943718400 bytes at offset 0 | XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec) | Trying direct IO write over allocated space... | wrote 10485760/10485760 bytes at offset 0 | XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec) | Trying buffered IO write over allocated space... | ... (18 expected-output lines total)`.

## Risks and Edge Cases
the main risk is silent metadata or persistence regression that only appears after remount, receive, check, or explicit content comparison. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/250 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/251 -->
# sources/test-tools/xfstests/tests/btrfs/251

## Purpose
Test if btrfs will crash when using compress-force mount option against incompressible data Read the content from urandom to a known safe location Make sure we didn't get short write success, all done. In this subset it primarily covers mount and remount option semantics.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick compress dangerous`. Requirement and capability gates: line 15: `_require_scratch`. Local helper surface: `workload()` (line 27). Important command/API calls include line 15: `_require_scratch`; line 20: `$XFS_IO_PROG -f -c "pwrite -i /dev/urandom 0 $pagesize" "$tmp.good" > /dev/null`; line 32: `_scratch_mkfs -s "$pagesize">> $seqres.full`; line 33: `_scratch_mount -o compress-force="$compression"`; line 34: `cp "$tmp.good" "$SCRATCH_MNT/$compression"`; line 37: `_scratch_cycle_mount`; line 40: `if [ "$(_md5_checksum $tmp.good)" != "$(_md5_checksum $SCRATCH_MNT/$compression)" ]; then`; line 46: `_scratch_unmount`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick compress dangerous`, install cleanup if needed, enforce requirements, then formats scratch storage, mounts the test filesystem, runs btrfs check or xfstests scratch checks, cycles mounts to force persistence. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through xfs_io. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 251 | === Testing compress-force=lzo === | OK | === Testing compress-force=zstd === | OK | === Testing compress-force=zlib === | OK`.

## Risks and Edge Cases
the main risk is silent metadata or persistence regression that only appears after remount, receive, check, or explicit content comparison. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/251 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/252 -->
# sources/test-tools/xfstests/tests/btrfs/252

## Purpose
Test that send and balance can run in parallel, without failures and producing correct results. Before kernel 5.3 it was possible to run both operations in parallel, however it was buggy and caused sporadic failures due to races, so it was disabled in kernel 5.3 by commit 9e967495e0e0ae ("Btrfs: prevent send failures and crashes due to concurrent relocation"). There is a now a patch that enables both operations to safely run in parallel, and it has the following subject: "btrfs: make send work with concurrent block group relocation" This also serves the purpose of testing a succession of incremental send. In this subset it primarily covers Btrfs send/receive stream generation and replay.

## Important APIs, Types, and Functions
The fstest declaration is `auto send balance stress`. Requirement and capability gates: line 44: `_require_scratch_size $(($LOAD_FACTOR * 6 * 1024 * 1024))`; line 45: `_require_fssum`. Local helper surface: `_cleanup()` (line 25), `balance_loop()` (line 47). Important command/API calls include line 23: `_begin_fstest auto send balance stress`; line 28: `if [ ! -z $balance_pid ]; then`; line 29: `kill $balance_pid &> /dev/null`; line 30: `wait $balance_pid`; line 47: `balance_loop()`; line 52: `_run_btrfs_balance_start $SCRATCH_MNT > /dev/null`; line 57: `_scratch_mkfs >> $seqres.full 2>&1`; line 58: `_scratch_mount`; line 60: `num_snapshots=$((10 + $LOAD_FACTOR * 2))`; line 61: `avg_ops_per_snapshot=$((1000 * LOAD_FACTOR))`; line 62: `total_fsstress_ops=$((num_snapshots * avg_ops_per_snapshot))`; line 65: `snapshots_dir="$SCRATCH_MNT/snapshots"`; line 66: `dest_dir="$SCRATCH_MNT/received"`; line 69: `mkdir -p "$snapshots_dir"`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto send balance stress`, install cleanup if needed, enforce requirements, then formats scratch storage, mounts the test filesystem, creates or deletes subvolumes/snapshots, generates and replays send streams, runs btrfs check or xfstests scratch checks. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. It persists send streams, fssum files, or received subvolumes in a temporary test directory and validates replay on a freshly formatted scratch filesystem. Snapshot and subvolume roots are deliberate persistent state used to test root items, received UUIDs, cleaner behavior, and metadata references. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through btrfs-progs, fssum, fsstress. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 252 | Silence is golden`.

## Risks and Edge Cases
send-stream ordering bugs can emit invalid paths, clone sources, link records, or parent references that only appear after replaying onto a clean filesystem. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/252 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/253 -->
# sources/test-tools/xfstests/tests/btrfs/253

## Purpose
Test the new /sys/fs/btrfs/<uuid>/allocation/<block-type>/chunk_size setting. This setting allows the admin to change the chunk size setting for the next allocation. Test 1: Allocate storage for all three block types (data, metadata and system) with the default chunk size. Test 2: Set a new chunk size to double the default size and allocate space for all new block types with the new chunk size. In this subset it primarily covers Btrfs filesystem behavior through xfstests shell orchestration.

## Important APIs, Types, and Functions
The fstest declaration is `auto`. Requirement and capability gates: line 79: `_require_test`; line 80: `_require_scratch`; line 82: `_require_non_zoned_device "$SCRATCH_DEV"`; line 93: `_require_fs_sysfs allocation/metadata/chunk_size`; line 94: `_require_fs_sysfs allocation/metadata/force_chunk_alloc`. Local helper surface: `parse_size_string()` (line 37), `device_size()` (line 47), `free_space()` (line 59), `alloc_size()` (line 72). Important command/API calls include line 47: `device_size() {`; line 79: `_require_test`; line 80: `_require_scratch`; line 82: `_require_non_zoned_device "$SCRATCH_DEV"`; line 85: `rm -f "${seqres}.full"`; line 89: `_scratch_mkfs_sized $((10 * 1024 * 1024 * 1024)) >> $seqres.full 2>&1`; line 90: `_scratch_mount >> $seqres.full 2>&1`; line 93: `_require_fs_sysfs allocation/metadata/chunk_size`; line 94: `_require_fs_sysfs allocation/metadata/force_chunk_alloc`; line 98: `device_size DEVICE_SIZE_MB`; line 202: `_fail "Cannot find allocation size for partial block allocation."`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto`, install cleanup if needed, enforce requirements, then formats scratch storage, mounts the test filesystem. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Multi-device tests allocate scratch pool devices and leave correctness evidence in chunk maps, device registry state, degraded mounts, and btrfs check results. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through standard xfstests common helpers and btrfs-progs. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 253 | Capture default chunk sizes. | First allocation. | Second allocation. | Calculate request size so last memory allocation cannot be completely fullfilled. | Third allocation. | Force allocation of system block type must fail. | No space left on device | ... (11 expected-output lines total)`.

## Risks and Edge Cases
device topology tests can expose races in device scan state, degraded mounts, stripe geometry, replacement, and cleanup of scratch device pools. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/253 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/254 -->
# sources/test-tools/xfstests/tests/btrfs/254

## Purpose
Test if the kernel can free the stale device entries. Override the default cleanup function. Use a known it is much easier to debug. In this subset it primarily covers multi-device, RAID, seed/sprout, or device-management paths.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick volume raid`. Requirement and capability gates: line 32: `_require_scratch_dev_pool 3`; line 33: `_require_block_device $SCRATCH_DEV`; line 34: `_require_dm_target linear`; line 35: `_require_btrfs_forget_or_module_loadable`; line 36: `_require_scratch_nocheck`; line 37: `_require_command "$WIPEFS_PROG" wipefs`. Local helper surface: `cleanup_dmdev()` (line 15), `_cleanup()` (line 20), `setup_dmdev()` (line 45), `test_forget()` (line 65), `test_add_device()` (line 82). Important command/API calls include line 17: `_dmsetup_remove $node`; line 23: `rm -f $tmp.*`; line 24: `_unmount $seq_mnt > /dev/null 2>&1`; line 25: `rm -rf $seq_mnt > /dev/null 2>&1`; line 32: `_require_scratch_dev_pool 3`; line 33: `_require_block_device $SCRATCH_DEV`; line 34: `_require_dm_target linear`; line 35: `_require_btrfs_forget_or_module_loadable`; line 36: `_require_scratch_nocheck`; line 37: `_require_command "$WIPEFS_PROG" wipefs`; line 38: `_check_minimal_fs_size $((1024 * 1024 * 1024))`; line 40: `_fixed_by_kernel_commit 770c79fb6550 "btrfs: harden identification of a stale device"`; line 43: `_scratch_dev_pool_get 3`; line 55: `_dmsetup_create $node --table "$table" || _fail "setup dm device failed"`. It documents fixed kernel commit context at line 40: `_fixed_by_kernel_commit 770c79fb6550 \`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick volume raid`, install cleanup if needed, enforce requirements, then mounts the test filesystem, runs btrfs check or xfstests scratch checks, cycles mounts to force persistence. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Multi-device tests allocate scratch pool devices and leave correctness evidence in chunk maps, device registry state, degraded mounts, and btrfs check results. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through btrfs-progs. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 254 | Label: none  uuid: <UUID> | 	Total devices <NUM> FS bytes used <SIZE> | 	devid <DEVID> size <SIZE> used <SIZE> path SCRATCH_DEV | 	*** Some devices missing`.

## Risks and Edge Cases
device topology tests can expose races in device scan state, degraded mounts, stripe geometry, replacement, and cleanup of scratch device pools. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/254 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/255 -->
# sources/test-tools/xfstests/tests/btrfs/255

## Purpose
Confirm that disabling quota during balance does not hang. The deadlock is fixed by kernel patch titled: btrfs: fix deadlock between quota disable and qgroup rescan worker Fill 40% of the device or 2GB Run btrfs balance and quota enable/disable in parallel. In this subset it primarily covers quota group accounting, assignment, limits, and rescan behavior, multi-device, RAID, seed/sprout, or device-management paths.

## Important APIs, Types, and Functions
The fstest declaration is `auto qgroup balance`. Requirement and capability gates: line 15: `_require_scratch`. Local helper surface: no custom shell functions beyond the linear test body. Important command/API calls include line 13: `_begin_fstest auto qgroup balance`; line 15: `_require_scratch`; line 17: `_scratch_mkfs >> $seqres.full 2>&1`; line 18: `_scratch_mount`; line 24: `devsize=$(($(_get_device_size $SCRATCH_DEV) * 512))`; line 35: `_btrfs_stress_balance $SCRATCH_MNT >> $seqres.full &`; line 36: `balance_pid=$!`; line 37: `echo $balance_pid >> $seqres.full`; line 39: `$BTRFS_UTIL_PROG quota enable $SCRATCH_MNT`; line 40: `$BTRFS_UTIL_PROG quota disable $SCRATCH_MNT`; line 43: `_btrfs_kill_stress_balance_pid $balance_pid`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto qgroup balance`, install cleanup if needed, enforce requirements, then formats scratch storage, mounts the test filesystem, enables and inspects quota groups. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Quota state persists in qgroup metadata and is forced through rescans, syncs, commits, and filesystem checks. Multi-device tests allocate scratch pool devices and leave correctness evidence in chunk maps, device registry state, degraded mounts, and btrfs check results. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through btrfs-progs. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 255 | Silence is golden`.

## Risks and Edge Cases
qgroup tests are sensitive to delayed accounting, rescan completion, shared extents, and limit enforcement after transaction commits; device topology tests can expose races in device scan state, degraded mounts, stripe geometry, replacement, and cleanup of scratch device pools. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/255 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/256 -->
# sources/test-tools/xfstests/tests/btrfs/256

## Purpose
Test that defragging files with very small sizes works and does not result in any crash, hang or corruption. The regression is fixed by a patch with the following subject: "btrfs: fix too long loop when defragging a 1 byte file" Test file sizes of 0, 1, 512, 1K, 2K, 4K, 8K, 16K, 32K and 64K bytes. Create the files and compute their checksums. Compute the checksums. Now defrag each file. Verify the checksums after the defrag operations. In this subset it primarily covers Btrfs filesystem behavior through xfstests shell orchestration.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick defrag`. Requirement and capability gates: line 25: `_require_scratch`; line 26: `_require_fssum`. Local helper surface: `_cleanup()` (line 17). Important command/API calls include line 20: `rm -r -f $tmp.*`; line 25: `_require_scratch`; line 26: `_require_fssum`; line 28: `_scratch_mkfs >> $seqres.full 2>&1`; line 29: `_scratch_mount`; line 31: `checksums_file="$TEST_DIR/btrfs-test-$seq-checksums"`; line 40: `$XFS_IO_PROG -f -c "pwrite -S $byte 0 $sz" "$SCRATCH_MNT/f_$sz" >> $seqres.full`; line 44: `$FSSUM_PROG -A -f -w "$checksums_file" "$SCRATCH_MNT"`; line 51: `$BTRFS_UTIL_PROG filesystem defragment "$SCRATCH_MNT/f_$sz" > /dev/null`; line 55: `$FSSUM_PROG -r "$checksums_file" "$SCRATCH_MNT"`; line 59: `_scratch_cycle_mount`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick defrag`, install cleanup if needed, enforce requirements, then formats scratch storage, mounts the test filesystem, runs btrfs check or xfstests scratch checks, cycles mounts to force persistence. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through btrfs-progs, xfs_io, fssum. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 256 | OK | OK`.

## Risks and Edge Cases
the main risk is silent metadata or persistence regression that only appears after remount, receive, check, or explicit content comparison. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/256 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/257 -->
# sources/test-tools/xfstests/tests/btrfs/257

## Purpose
Make sure btrfs doesn't defrag preallocated extents, nor lone extents before preallocated extents. Override the default cleanup function. _cleanup() { cd / rm -r -f $tmp.* } We rely on specific extent layout, don't run on compress. In this subset it primarily covers Btrfs filesystem behavior through xfstests shell orchestration.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick defrag prealloc fiemap`. Requirement and capability gates: line 23: `_require_scratch`; line 26: `_require_btrfs_no_compress`; line 29: `_require_btrfs_support_sectorsize 4096`; line 30: `_require_xfs_io_command "falloc"`; line 31: `_require_xfs_io_command "fiemap"`. Local helper surface: no custom shell functions beyond the linear test body. Important command/API calls include line 23: `_require_scratch`; line 26: `_require_btrfs_no_compress`; line 29: `_require_btrfs_support_sectorsize 4096`; line 30: `_require_xfs_io_command "falloc"`; line 31: `_require_xfs_io_command "fiemap"`; line 33: `_scratch_mkfs -s 4k >> $seqres.full 2>&1`; line 36: `_scratch_mount -o datacow`; line 44: `$XFS_IO_PROG -f -c "pwrite 0 4k" -c sync -c "falloc 4k 12k" "$SCRATCH_MNT/foobar" >> $seqres.full`; line 48: `$XFS_IO_PROG -c "fiemap -v" "$SCRATCH_MNT/foobar" >> $seqres.full`; line 55: `$BTRFS_UTIL_PROG filesystem defrag "$SCRATCH_MNT/foobar" >> $seqres.full`; line 56: `sync`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick defrag prealloc fiemap`, install cleanup if needed, enforce requirements, then formats scratch storage, mounts the test filesystem. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through btrfs-progs, xfs_io. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 257 | Silence is golden`.

## Risks and Edge Cases
the main risk is silent metadata or persistence regression that only appears after remount, receive, check, or explicit content comparison. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/257 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/258 -->
# sources/test-tools/xfstests/tests/btrfs/258

## Purpose
Make sure btrfs auto defrag can properly defrag clusters which has hole in the middle Needs 4K sectorsize, as larger sectorsize can change the file layout. Need datacow to show which range is defragged, and we're testing autodefrag Create a layout where we have fragmented extents at [0, 64k) (sync write in reserve order), then a hole at [64k, 128k) Now trigger autodefrag, autodefrag is triggered in the cleaner thread, which will be woken up by commit thread. In this subset it primarily covers mount and remount option semantics.

## Important APIs, Types, and Functions
The fstest declaration is `auto defrag quick fiemap remount`. Requirement and capability gates: line 15: `_require_scratch`; line 16: `_require_xfs_io_command "fiemap"`; line 19: `_require_btrfs_support_sectorsize 4096`. Local helper surface: no custom shell functions beyond the linear test body. Important command/API calls include line 11: `_begin_fstest auto defrag quick fiemap remount`; line 15: `_require_scratch`; line 16: `_require_xfs_io_command "fiemap"`; line 19: `_require_btrfs_support_sectorsize 4096`; line 21: `_scratch_mkfs >> $seqres.full`; line 25: `_scratch_mount -o datacow,autodefrag`; line 29: `$XFS_IO_PROG -f -s -c "pwrite 48k 16k" -c "pwrite 32k 16k" -c "pwrite 16k 16k" -c "pwrite 0 16k" $SCRATCH_MNT/foobar >> $seqres.full`; line 34: `old_csum=$(_md5_checksum $SCRATCH_MNT/foobar)`; line 36: `$XFS_IO_PROG -c "fiemap -v" "$SCRATCH_MNT/foobar" >> $seqres.full`; line 44: `_scratch_remount commit=1`; line 46: `sync`; line 48: `new_csum=$(_md5_checksum $SCRATCH_MNT/foobar)`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto defrag quick fiemap remount`, install cleanup if needed, enforce requirements, then formats scratch storage, mounts the test filesystem, runs btrfs check or xfstests scratch checks. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through xfs_io. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 258 | Silence is golden`.

## Risks and Edge Cases
the main risk is silent metadata or persistence regression that only appears after remount, receive, check, or explicit content comparison. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/258 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/259 -->
# sources/test-tools/xfstests/tests/btrfs/259

## Purpose
Make sure btrfs defrag ioctl won't defrag compressed extents which are already at their max capacity. Btrfs uses 128K as max extent size for compressed extents, this would result several compressed extents all at their max size success, all done. In this subset it primarily covers Btrfs filesystem behavior through xfstests shell orchestration.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick defrag fiemap compress`. Requirement and capability gates: line 15: `_require_scratch`; line 16: `_require_xfs_io_command "fiemap"`. Local helper surface: no custom shell functions beyond the linear test body. Important command/API calls include line 15: `_require_scratch`; line 16: `_require_xfs_io_command "fiemap"`; line 18: `_scratch_mkfs >> $seqres.full`; line 20: `_scratch_mount -o compress`; line 24: `$XFS_IO_PROG -f -c "pwrite -S 0xee 0 16m" -c sync $SCRATCH_MNT/foobar >> $seqres.full`; line 27: `old_csum=$(_md5_checksum $SCRATCH_MNT/foobar)`; line 30: `$XFS_IO_PROG -c "fiemap -v" "$SCRATCH_MNT/foobar" >> $seqres.full`; line 31: `$XFS_IO_PROG -c "fiemap -v" "$SCRATCH_MNT/foobar" > $tmp.before`; line 33: `$BTRFS_UTIL_PROG filesystem defrag "$SCRATCH_MNT/foobar" >> $seqres.full`; line 34: `sync`; line 36: `new_csum=$(_md5_checksum $SCRATCH_MNT/foobar)`; line 40: `$XFS_IO_PROG -c "fiemap -v" "$SCRATCH_MNT/foobar" > $tmp.after`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick defrag fiemap compress`, install cleanup if needed, enforce requirements, then formats scratch storage, mounts the test filesystem, runs btrfs check or xfstests scratch checks. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through btrfs-progs, xfs_io. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 259 | Silence is golden`.

## Risks and Edge Cases
the main risk is silent metadata or persistence regression that only appears after remount, receive, check, or explicit content comparison. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/259 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/260 -->
# sources/test-tools/xfstests/tests/btrfs/260

## Purpose
Make sure "btrfs filesystem defragment" can still convert the compression algorithm of all regular extents. Override the default cleanup function. _cleanup() { cd / rm -r -f $tmp.* } Unlike file extents whose btrfs specific attributes need to be grabbed from. In this subset it primarily covers Btrfs filesystem behavior through xfstests shell orchestration.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick defrag compress prealloc fiemap`. Requirement and capability gates: line 22: `_require_scratch`; line 23: `_require_xfs_io_command "fiemap" "ranged"`; line 24: `_require_xfs_io_command "falloc"`; line 25: `_require_btrfs_command inspect-internal dump-tree`; line 79: `_require_btrfs_support_sectorsize 4096`. Local helper surface: `get_inode_number()` (line 27), `get_file_extent()` (line 34), `check_file_extent()` (line 45), `check_hole()` (line 62). Important command/API calls include line 24: `_require_xfs_io_command "falloc"`; line 25: `_require_btrfs_command inspect-internal dump-tree`; line 41: `$BTRFS_UTIL_PROG inspect-internal dump-tree -t 5 $SCRATCH_DEV | grep -A4 "$file_extent_key"`; line 45: `check_file_extent()`; line 62: `check_hole()`; line 81: `_scratch_mkfs -s 4k >> $seqres.full 2>&1`; line 84: `_scratch_mount -o compress=lzo`; line 87: `$XFS_IO_PROG -f -c "pwrite 0 1m" "$SCRATCH_MNT/large" >> $seqres.full`; line 93: `$XFS_IO_PROG -f -c "pwrite 0 16k" -c "pwrite 32k 16k" -c "pwrite 64k 16k" "$SCRATCH_MNT/fragment" >> $seqres.full`; line 100: `$XFS_IO_PROG -c "falloc 16k 16k" "$SCRATCH_MNT/fragment"`; line 106: `check_file_extent "$SCRATCH_MNT/large" 0 "compression 2"`; line 109: `check_file_extent "$SCRATCH_MNT/fragment" 0 "compression 2"`; line 112: `check_file_extent "$SCRATCH_MNT/fragment" 16384 "type 2"`; line 115: `check_file_extent "$SCRATCH_MNT/fragment" 32768 "compression 2"`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick defrag compress prealloc fiemap`, install cleanup if needed, enforce requirements, then formats scratch storage, mounts the test filesystem, runs btrfs check or xfstests scratch checks. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through btrfs-progs, xfs_io. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 260 | Silence is golden`.

## Risks and Edge Cases
the main risk is silent metadata or persistence regression that only appears after remount, receive, check, or explicit content comparison. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/260 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/261 -->
# sources/test-tools/xfstests/tests/btrfs/261

## Purpose
Make sure btrfs raid profiles can handling one corrupted device without affecting the consistency of the fs. success, all done. In this subset it primarily covers multi-device, RAID, seed/sprout, or device-management paths, scrub detection and repair paths.

## Important APIs, Types, and Functions
The fstest declaration is `auto volume raid scrub`. Requirement and capability gates: line 13: `_require_scratch_dev_pool 4`; line 15: `_require_fssum`. Local helper surface: `prepare_fs()` (line 17), `workload()` (line 46). Important command/API calls include line 11: `_begin_fstest auto volume raid scrub`; line 13: `_require_scratch_dev_pool 4`; line 14: `_btrfs_get_profile_configs replace-missing`; line 15: `_require_fssum`; line 24: `_scratch_pool_mkfs $mkfs_opts -b 1G >> $seqres.full 2>&1`; line 30: `_scratch_mount -o compress=no`; line 33: `$XFS_IO_PROG -f -c "pwrite -S 0xfe 0 400M" $SCRATCH_MNT/garbage > /dev/null 2>&1`; line 39: `sync`; line 42: `$FSSUM_PROG -A -f -w $tmp.saved_fssum $SCRATCH_MNT`; line 43: `_scratch_unmount`; line 51: `_scratch_dev_pool_get 4`; line 53: `rm -f -- $tmp.saved_fssum`; line 58: `$XFS_IO_PROG -c "pwrite 1M 1023M" $SCRATCH_DEV > /dev/null 2>&1`; line 60: `_scratch_mount`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto volume raid scrub`, install cleanup if needed, enforce requirements, then mounts the test filesystem, runs scrub or checks scrub reports, cycles mounts to force persistence. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Multi-device tests allocate scratch pool devices and leave correctness evidence in chunk maps, device registry state, degraded mounts, and btrfs check results. Corruption is injected below the filesystem and then validated after scrub, remount, or direct device reads. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through btrfs-progs, xfs_io, fssum. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 261 | Silence is golden`.

## Risks and Edge Cases
device topology tests can expose races in device scan state, degraded mounts, stripe geometry, replacement, and cleanup of scratch device pools; scrub repair signals depend on precise logical-to-physical mapping and can miss corruption if checksum, parity, or duplicate-copy selection regresses. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/261 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/262 -->
# sources/test-tools/xfstests/tests/btrfs/262

## Purpose
Test that running qgroup enable, create, destroy, and disable commands in parallel doesn't result in a deadlock, a crash or any filesystem inconsistency. success, all done. In this subset it primarily covers quota group accounting, assignment, limits, and rescan behavior.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick qgroup`. Requirement and capability gates: line 17: `_require_scratch`. Local helper surface: no custom shell functions beyond the linear test body. Important command/API calls include line 12: `_begin_fstest auto quick qgroup`; line 17: `_require_scratch`; line 19: `_scratch_mkfs > /dev/null 2>&1`; line 20: `_scratch_mount`; line 23: `$BTRFS_UTIL_PROG quota enable $SCRATCH_MNT 2>> $seqres.full &`; line 24: `$BTRFS_UTIL_PROG qgroup create 1/0 $SCRATCH_MNT 2>> $seqres.full &`; line 25: `$BTRFS_UTIL_PROG qgroup destroy 1/0 $SCRATCH_MNT 2>> $seqres.full &`; line 26: `$BTRFS_UTIL_PROG quota disable $SCRATCH_MNT 2>> $seqres.full &`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick qgroup`, install cleanup if needed, enforce requirements, then formats scratch storage, mounts the test filesystem, enables and inspects quota groups. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Quota state persists in qgroup metadata and is forced through rescans, syncs, commits, and filesystem checks. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through btrfs-progs. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 262 | Silence is golden`.

## Risks and Edge Cases
qgroup tests are sensitive to delayed accounting, rescan completion, shared extents, and limit enforcement after transaction commits. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/262 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/263 -->
# sources/test-tools/xfstests/tests/btrfs/263

## Purpose
Make sure btrfs autodefrag will not defrag ranges which won't reduce defragmentation. Needs fixed 4K sector size, or the file layout will not match the expected result. Create the initial layout, with a large 64K extent for later fragments. Need to bump the generation by one, as autodefrag uses the last modified generation of a subvolume. Without this generation bump, autodefrag will defrag the whole file, not only the new write. Remount to autodefrag. In this subset it primarily covers multi-device, RAID, seed/sprout, or device-management paths, mount and remount option semantics, subvolume and snapshot metadata.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick defrag fiemap remount`. Requirement and capability gates: line 15: `_require_scratch`; line 16: `_require_xfs_io_command "fiemap" "ranged"`; line 20: `_require_btrfs_support_sectorsize 4096`. Local helper surface: no custom shell functions beyond the linear test body. Important command/API calls include line 11: `_begin_fstest auto quick defrag fiemap remount`; line 15: `_require_scratch`; line 16: `_require_xfs_io_command "fiemap" "ranged"`; line 20: `_require_btrfs_support_sectorsize 4096`; line 22: `_scratch_mkfs >> $seqres.full`; line 24: `_scratch_mount -o noautodefrag`; line 27: `$XFS_IO_PROG -f -c "pwrite 0 64K" -c sync "$SCRATCH_MNT/foobar" >> $seqres.full`; line 32: `touch "$SCRATCH_MNT/trash"`; line 33: `sync`; line 36: `_scratch_remount autodefrag`; line 39: `$XFS_IO_PROG -c "pwrite 16K 4K" -c sync "$SCRATCH_MNT/foobar" >> $seqres.full`; line 42: `$XFS_IO_PROG -c "fiemap -v" "$SCRATCH_MNT/foobar" >> $seqres.full`; line 44: `old_csum=$(_md5_checksum "$SCRATCH_MNT/foobar")`; line 50: `_scratch_remount commit=1`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick defrag fiemap remount`, install cleanup if needed, enforce requirements, then formats scratch storage, mounts the test filesystem, runs btrfs check or xfstests scratch checks. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through xfs_io. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 263 | Silence is golden`.

## Risks and Edge Cases
the main risk is silent metadata or persistence regression that only appears after remount, receive, check, or explicit content comparison. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/263 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/264 -->
# sources/test-tools/xfstests/tests/btrfs/264

## Purpose
Compression and nodatacow are mutually exclusive. Besides ioctl, there is another way to setting compression via xattrs, and shouldn't produce invalid combinations. To prevent mix any compression-related options with nodatacow, FS_NOCOMP_FL is also rejected by ioctl as well as FS_COMPR_FL on nodatacow files. To align with it, no and none are also unacceptable in this test. The regression is fixed by a patch with the following subject: btrfs: do not allow compression on nodatacow files FS_NOCOMP_FL bit isn't recognized by chattr/lsattr before e2fsprogs 1.46.2. In this subset it primarily covers Btrfs filesystem behavior through xfstests shell orchestration.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick compress attr`. Requirement and capability gates: line 24: `_require_scratch`; line 25: `_require_attrs`; line 26: `_require_chattr C`. Local helper surface: no custom shell functions beyond the linear test body. Important command/API calls include line 24: `_require_scratch`; line 25: `_require_attrs`; line 26: `_require_chattr C`; line 28: `_scratch_mkfs >>$seqres.full 2>&1`; line 29: `_scratch_mount`; line 34: `$SETFATTR_PROG -n "btrfs.compression" -v "$2" "$1" |& _filter_scratch`; line 40: `check_compression() # $1: filename`; line 45: `echo "$1: Compression is set" | _filter_scratch`; line 47: `echo "$1: Compression is not set" | _filter_scratch`; line 55: `touch "$test_file"`; line 59: `check_compression "$test_file"`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick compress attr`, install cleanup if needed, enforce requirements, then formats scratch storage, mounts the test filesystem, runs btrfs check or xfstests scratch checks. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through standard xfstests common helpers and btrfs-progs. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 264 | SCRATCH_MNT/foo: Compression is set | SCRATCH_MNT/foo: Compression is not set | SCRATCH_MNT/foo: Compression is set | SCRATCH_MNT/foo: Compression is not set | SCRATCH_MNT/foo: Compression is set | setfattr: SCRATCH_MNT/bar: Invalid argument | setfattr: SCRATCH_MNT/bar: Invalid argument | ... (11 expected-output lines total)`.

## Risks and Edge Cases
the main risk is silent metadata or persistence regression that only appears after remount, receive, check, or explicit content comparison. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/264 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/265 -->
# sources/test-tools/xfstests/tests/btrfs/265

## Purpose
Test that btrfs raid repair on a raid1c3 profile can repair corruption on two mirrors for the same logical offset. No data checksums for NOCOW and NODATACOW cases, so can't detect corruption and repair data. Overwriting data is forbidden on a zoned block device We need to ensure a fixed extent size and we corrupt by writing directly to the device, so skip if compression is enabled. step 1, create a raid1 btrfs which contains one 128k file. step 2, corrupt the first 64k of one copy (on SCRATCH_DEV which is the first. In this subset it primarily covers multi-device, RAID, seed/sprout, or device-management paths, logical-to-inode extent resolution.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick read_repair raid`. Requirement and capability gates: line 16: `_require_scratch_dev_pool 3`; line 20: `_require_btrfs_no_nodatacow`; line 21: `_require_btrfs_no_nodatasum`; line 22: `_require_odirect`; line 24: `_require_non_zoned_device "${SCRATCH_DEV}"`; line 27: `_require_no_compress`. Local helper surface: no custom shell functions beyond the linear test body. Important command/API calls include line 16: `_require_scratch_dev_pool 3`; line 20: `_require_btrfs_no_nodatacow`; line 21: `_require_btrfs_no_nodatasum`; line 22: `_require_odirect`; line 24: `_require_non_zoned_device "${SCRATCH_DEV}"`; line 27: `_require_no_compress`; line 29: `_scratch_dev_pool_get 3`; line 34: `_scratch_pool_mkfs $mkfs_opts >>$seqres.full 2>&1`; line 36: `_scratch_mount`; line 38: `$XFS_IO_PROG -f -d -c "pwrite -S 0xaa -b 128K 0 128K" "$SCRATCH_MNT/foobar" | _filter_xfs_io_offset`; line 47: `sync`; line 49: `logical=$(_btrfs_get_first_logical $SCRATCH_MNT/foobar)`; line 51: `physical1=$(_btrfs_get_physical ${logical} 1)`; line 52: `devpath1=$(_btrfs_get_device_path ${logical} 1)`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick read_repair raid`, install cleanup if needed, enforce requirements, then mounts the test filesystem, runs btrfs check or xfstests scratch checks, cycles mounts to force persistence. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Multi-device tests allocate scratch pool devices and leave correctness evidence in chunk maps, device registry state, degraded mounts, and btrfs check results. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through xfs_io. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 265 | step 1......mkfs.btrfs | wrote 131072/131072 bytes | XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec) | step 2......corrupt file extent | step 3......repair the bad copy | step 4......check if the repair worked | XXXXXXXX:  aa aa aa aa aa aa aa aa aa aa aa aa aa aa aa aa  ................ | ... (75 expected-output lines total)`.

## Risks and Edge Cases
device topology tests can expose races in device scan state, degraded mounts, stripe geometry, replacement, and cleanup of scratch device pools. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/265 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/266 -->
# sources/test-tools/xfstests/tests/btrfs/266

## Purpose
Test that btrfs buffered read repair on a raid1c3 profile can repair interleaving errors on all mirrors. No data checksums for NOCOW and NODATACOW cases, so can't detect corruption and repair data. Overwriting data is forbidden on a zoned block device We need to ensure a fixed extent size and we corrupt by writing directly to the device, so skip if compression is enabled. step 1, create a raid1 btrfs which contains one 128k file. step 2, corrupt 64k in each copy. In this subset it primarily covers multi-device, RAID, seed/sprout, or device-management paths.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick read_repair raid`. Requirement and capability gates: line 19: `_require_btrfs_no_nodatacow`; line 20: `_require_btrfs_no_nodatasum`; line 21: `_require_scratch_dev_pool 3`; line 23: `_require_odirect`; line 25: `_require_non_zoned_device "${SCRATCH_DEV}"`; line 28: `_require_no_compress`. Local helper surface: no custom shell functions beyond the linear test body. Important command/API calls include line 19: `_require_btrfs_no_nodatacow`; line 20: `_require_btrfs_no_nodatasum`; line 21: `_require_scratch_dev_pool 3`; line 23: `_require_odirect`; line 25: `_require_non_zoned_device "${SCRATCH_DEV}"`; line 28: `_require_no_compress`; line 30: `_scratch_dev_pool_get 3`; line 35: `_scratch_pool_mkfs $mkfs_opts >>$seqres.full 2>&1`; line 37: `_scratch_mount`; line 39: `$XFS_IO_PROG -f -d -c "pwrite -S 0xaa -b 256K 0 256K" "$SCRATCH_MNT/foobar" | _filter_xfs_io_offset`; line 47: `sync`; line 49: `logical=$(_btrfs_get_first_logical $SCRATCH_MNT/foobar)`; line 51: `physical1=$(_btrfs_get_physical ${logical} 1)`; line 52: `devpath1=$(_btrfs_get_device_path ${logical} 1)`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick read_repair raid`, install cleanup if needed, enforce requirements, then mounts the test filesystem, runs btrfs check or xfstests scratch checks, cycles mounts to force persistence. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Multi-device tests allocate scratch pool devices and leave correctness evidence in chunk maps, device registry state, degraded mounts, and btrfs check results. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through xfs_io. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 266 | step 1......mkfs.btrfs | wrote 262144/262144 bytes | XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec) | step 2......corrupt file extent | step 3......repair the bad copy | step 4......check if the repair worked | XXXXXXXX:  aa aa aa aa aa aa aa aa aa aa aa aa aa aa aa aa  ................ | ... (109 expected-output lines total)`.

## Risks and Edge Cases
device topology tests can expose races in device scan state, degraded mounts, stripe geometry, replacement, and cleanup of scratch device pools. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/266 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/267 -->
# sources/test-tools/xfstests/tests/btrfs/267

## Purpose
Test that btrfs direct IO read repair on a raid1c3 profile can repair interleaving errors on all mirrors. No data checksums for NOCOW and NODATACOW cases, so can't detect corruption and repair data. Overwriting data is forbidden on a zoned block device We need to ensure a fixed extent size and we corrupt by writing directly to the device, so skip if compression is enabled. step 1, create a raid1 btrfs which contains one 128k file. step 2, corrupt 64k in each copy. In this subset it primarily covers multi-device, RAID, seed/sprout, or device-management paths.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick read_repair raid`. Requirement and capability gates: line 17: `_require_scratch_dev_pool 3`; line 21: `_require_btrfs_no_nodatacow`; line 22: `_require_btrfs_no_nodatasum`; line 23: `_require_odirect`; line 25: `_require_non_zoned_device "${SCRATCH_DEV}"`; line 28: `_require_no_compress`. Local helper surface: no custom shell functions beyond the linear test body. Important command/API calls include line 17: `_require_scratch_dev_pool 3`; line 21: `_require_btrfs_no_nodatacow`; line 22: `_require_btrfs_no_nodatasum`; line 23: `_require_odirect`; line 25: `_require_non_zoned_device "${SCRATCH_DEV}"`; line 28: `_require_no_compress`; line 30: `_scratch_dev_pool_get 3`; line 35: `_scratch_pool_mkfs $mkfs_opts >>$seqres.full 2>&1`; line 37: `_scratch_mount`; line 39: `$XFS_IO_PROG -f -d -c "pwrite -S 0xaa -b 256K 0 256K" "$SCRATCH_MNT/foobar" | _filter_xfs_io_offset`; line 47: `sync`; line 49: `logical=$(_btrfs_get_first_logical $SCRATCH_MNT/foobar)`; line 51: `physical1=$(_btrfs_get_physical ${logical} 1)`; line 52: `devpath1=$(_btrfs_get_device_path ${logical} 1)`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick read_repair raid`, install cleanup if needed, enforce requirements, then mounts the test filesystem, runs btrfs check or xfstests scratch checks, cycles mounts to force persistence. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Multi-device tests allocate scratch pool devices and leave correctness evidence in chunk maps, device registry state, degraded mounts, and btrfs check results. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through xfs_io. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 267 | step 1......mkfs.btrfs | wrote 262144/262144 bytes | XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec) | step 2......corrupt file extent | step 3......repair the bad copy | step 4......check if the repair worked | XXXXXXXX:  aa aa aa aa aa aa aa aa aa aa aa aa aa aa aa aa  ................ | ... (109 expected-output lines total)`.

## Risks and Edge Cases
device topology tests can expose races in device scan state, degraded mounts, stripe geometry, replacement, and cleanup of scratch device pools. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/267 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/268 -->
# sources/test-tools/xfstests/tests/btrfs/268

## Purpose
Test that btrfs read repair on a raid1 profile won't loop forever if data is corrupted on both mirrors and can't be recovered. No data checksums for NOCOW and NODATACOW cases, so can't detect corruption and repair data. We need to ensure a fixed extent size and we corrupt by writing directly to the device, so skip if compression is enabled. ensure btrfs-map-logical sees the tree updates success, all done. In this subset it primarily covers multi-device, RAID, seed/sprout, or device-management paths, logical-to-inode extent resolution.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick read_repair raid`. Requirement and capability gates: line 16: `_require_scratch`; line 17: `_require_odirect`; line 20: `_require_btrfs_no_nodatacow`; line 21: `_require_btrfs_no_nodatasum`; line 22: `_require_non_zoned_device "${SCRATCH_DEV}" # no overwrites on zoned devices`; line 23: `_require_scratch_dev_pool 2`; line 27: `_require_no_compress`. Local helper surface: no custom shell functions beyond the linear test body. Important command/API calls include line 16: `_require_scratch`; line 17: `_require_odirect`; line 20: `_require_btrfs_no_nodatacow`; line 21: `_require_btrfs_no_nodatasum`; line 22: `_require_non_zoned_device "${SCRATCH_DEV}" # no overwrites on zoned devices`; line 23: `_require_scratch_dev_pool 2`; line 24: `_scratch_dev_pool_get 2`; line 27: `_require_no_compress`; line 31: `_scratch_pool_mkfs "-d raid1 -b 1G" >>$seqres.full 2>&1`; line 32: `_scratch_mount`; line 34: `$XFS_IO_PROG -f -d -c "pwrite -S 0xaa -b 256K 0 256K" "$SCRATCH_MNT/foobar" | _filter_xfs_io_offset`; line 39: `sync`; line 41: `logical=$(_btrfs_get_first_logical $SCRATCH_MNT/foobar)`; line 43: `physical1=$(_btrfs_get_physical ${logical} 1)`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick read_repair raid`, install cleanup if needed, enforce requirements, then mounts the test filesystem, cycles mounts to force persistence. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Multi-device tests allocate scratch pool devices and leave correctness evidence in chunk maps, device registry state, degraded mounts, and btrfs check results. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through xfs_io. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 268 | step 1......mkfs.btrfs | wrote 262144/262144 bytes | XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec) | step 2......corrupt file extent | step 3......try to repair | pread: Input/output error`.

## Risks and Edge Cases
device topology tests can expose races in device scan state, degraded mounts, stripe geometry, replacement, and cleanup of scratch device pools. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/268 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/269 -->
# sources/test-tools/xfstests/tests/btrfs/269

## Purpose
Test btrfs read repair over tricky stripe boundaries on the raid10 profile: | stripe 0 | stripe 2 mirror 1 | I/O FAIL | GOOD mirror 2 | GOOD | CSUM FAIL No data checksums for NOCOW and NODATACOW cases, so can't detect corruption and repair data. We need to ensure a fixed extent size and we corrupt by writing directly to the device, so skip if compression is enabled. ensure btrfs-map-logical sees the tree updates. In this subset it primarily covers multi-device, RAID, seed/sprout, or device-management paths, logical-to-inode extent resolution.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick read_repair raid`. Requirement and capability gates: line 20: `_require_scratch`; line 21: `_require_odirect`; line 24: `_require_btrfs_no_nodatacow`; line 25: `_require_btrfs_no_nodatasum`; line 26: `_require_non_zoned_device "${SCRATCH_DEV}" # no overwrites on zoned devices`; line 29: `_require_no_compress`; line 30: `_require_scratch_dev_pool 4`. Local helper surface: no custom shell functions beyond the linear test body. Important command/API calls include line 20: `_require_scratch`; line 21: `_require_odirect`; line 24: `_require_btrfs_no_nodatacow`; line 25: `_require_btrfs_no_nodatasum`; line 26: `_require_non_zoned_device "${SCRATCH_DEV}" # no overwrites on zoned devices`; line 29: `_require_no_compress`; line 30: `_require_scratch_dev_pool 4`; line 31: `_scratch_dev_pool_get 4`; line 35: `_scratch_pool_mkfs "-d raid10 -b 1G" >>$seqres.full 2>&1`; line 36: `_scratch_mount`; line 38: `$XFS_IO_PROG -f -d -c "pwrite -S 0xaa -b 128K 0 128K" "$SCRATCH_MNT/foobar" | _filter_xfs_io_offset`; line 43: `sync`; line 45: `logical=$(_btrfs_get_first_logical $SCRATCH_MNT/foobar)`; line 47: `physical1=$(_btrfs_get_physical ${logical} 1)`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick read_repair raid`, install cleanup if needed, enforce requirements, then mounts the test filesystem, runs btrfs check or xfstests scratch checks, cycles mounts to force persistence. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Multi-device tests allocate scratch pool devices and leave correctness evidence in chunk maps, device registry state, degraded mounts, and btrfs check results. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through xfs_io. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 269 | step 1......mkfs.btrfs | wrote 131072/131072 bytes | XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec) | step 2......corrupt file extent | step 3......repair the bad copy | step 4......check if the repair worked | XXXXXXXX:  aa aa aa aa aa aa aa aa aa aa aa aa aa aa aa aa  ................ | ... (41 expected-output lines total)`.

## Risks and Edge Cases
device topology tests can expose races in device scan state, degraded mounts, stripe geometry, replacement, and cleanup of scratch device pools. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/269 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/270 -->
# sources/test-tools/xfstests/tests/btrfs/270

## Purpose
Regression test for btrfs buffered read repair of compressed data. Create a file with all data being compressed success, all done. In this subset it primarily covers multi-device, RAID, seed/sprout, or device-management paths.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick read_repair compress raid`. Requirement and capability gates: line 14: `_require_scratch`; line 15: `_require_btrfs_command inspect-internal dump-tree`; line 16: `_require_non_zoned_device "${SCRATCH_DEV}" # no overwrites on zoned devices`; line 17: `_require_scratch_dev_pool 2`. Local helper surface: `get_physical()` (line 20), `get_devid()` (line 29), `get_device_path()` (line 38). Important command/API calls include line 14: `_require_scratch`; line 15: `_require_btrfs_command inspect-internal dump-tree`; line 16: `_require_non_zoned_device "${SCRATCH_DEV}" # no overwrites on zoned devices`; line 17: `_require_scratch_dev_pool 2`; line 18: `_scratch_dev_pool_get 2`; line 24: `$BTRFS_UTIL_PROG inspect-internal dump-tree -t 3 $SCRATCH_DEV | grep $logical -A 6 | $AWK_PROG "(\$1 ~ /stripe/ && \$3 ~ /devid/ && \$2 ~ /$stripe/) { print \$6 }"`; line 33: `$BTRFS_UTIL_PROG inspect-internal dump-tree -t 3 $SCRATCH_DEV | grep $logical -A 6 | $AWK_PROG "(\$1 ~ /stripe/ && \$3 ~ /devid/ && \$2 ~ /$stripe/) { print \$4 }"`; line 38: `get_device_path()`; line 46: `_check_minimal_fs_size $(( 1024 * 1024 * 1024 ))`; line 47: `_scratch_pool_mkfs "-d raid1 -b 1G" >>$seqres.full 2>&1`; line 48: `_scratch_mount -ocompress`; line 51: `$XFS_IO_PROG -f -c "pwrite -S 0xaa -W -b 128K 0 128K" "$SCRATCH_MNT/foobar" | _filter_xfs_io_offset`; line 54: `logical_in_btrfs=$(_btrfs_get_first_logical $SCRATCH_MNT/foobar)`; line 55: `physical=$(get_physical ${logical_in_btrfs} 1)`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick read_repair compress raid`, install cleanup if needed, enforce requirements, then mounts the test filesystem, runs btrfs check or xfstests scratch checks, cycles mounts to force persistence. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Multi-device tests allocate scratch pool devices and leave correctness evidence in chunk maps, device registry state, degraded mounts, and btrfs check results. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through btrfs-progs, xfs_io. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 270 | step 1......mkfs.btrfs | wrote 131072/131072 bytes | XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec) | step 2......corrupt file extent | step 3......repair the bad copy | step 4......check if the repair worked`.

## Risks and Edge Cases
device topology tests can expose races in device scan state, degraded mounts, stripe geometry, replacement, and cleanup of scratch device pools. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/270 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/271 -->
# sources/test-tools/xfstests/tests/btrfs/271

## Purpose
Test btrfs write error propagation and reporting on the raid1 profile. btrfs counts errors per IO, assuming the data is merged that'll be 1 IO, then the log tree block and then the log root tree block and then the super block. We should see at least 4 failed IO's, but with subpage blocksize we could see more if the log blocks end up on the same page, or if the data IO gets split at all. success, all done. In this subset it primarily covers multi-device, RAID, seed/sprout, or device-management paths.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick raid`. Requirement and capability gates: line 15: `_require_scratch`; line 16: `_require_fail_make_request`; line 17: `_require_scratch_dev_pool 2`. Local helper surface: no custom shell functions beyond the linear test body. Important command/API calls include line 15: `_require_scratch`; line 16: `_require_fail_make_request`; line 17: `_require_scratch_dev_pool 2`; line 18: `_scratch_dev_pool_get 2`; line 20: `_check_minimal_fs_size $(( 1024 * 1024 * 1024 ))`; line 21: `_scratch_pool_mkfs "-m raid1 -d raid1 -b 1G" >> $seqres.full 2>&1`; line 23: `_scratch_mount`; line 31: `$XFS_IO_PROG -f -c "pwrite -W -S 0xaa 0 8K" $SCRATCH_MNT/foobar | _filter_xfs_io`; line 39: `errs=$($BTRFS_UTIL_PROG device stats $SCRATCH_DEV | $AWK_PROG '/write_io_errs/ { print $2 }')`; line 46: `$XFS_IO_PROG -c "pread -v 0 8K" $SCRATCH_MNT/foobar | _filter_xfs_io_offset`; line 51: `$XFS_IO_PROG -f -c "pwrite -W -S 0xbb 0 8K" $SCRATCH_MNT/foobar | _filter_xfs_io`; line 57: `_scratch_dev_pool_put`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick raid`, install cleanup if needed, enforce requirements, then mounts the test filesystem, runs btrfs check or xfstests scratch checks. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Multi-device tests allocate scratch pool devices and leave correctness evidence in chunk maps, device registry state, degraded mounts, and btrfs check results. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through btrfs-progs, xfs_io. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 271 | Allow global fail_make_request feature | Step 1: writing with one failing mirror: | wrote 8192/8192 bytes at offset 0 | XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec) | Step 2: verify that the data reads back fine: | XXXXXXXX:  aa aa aa aa aa aa aa aa aa aa aa aa aa aa aa aa  ................ | XXXXXXXX:  aa aa aa aa aa aa aa aa aa aa aa aa aa aa aa aa  ................ | ... (523 expected-output lines total)`.

## Risks and Edge Cases
device topology tests can expose races in device scan state, degraded mounts, stripe geometry, replacement, and cleanup of scratch device pools. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/271 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/272 -->
# sources/test-tools/xfstests/tests/btrfs/272

## Purpose
Regression test for btrfs incremental send issue where a link instruction is sent against an existing path, causing btrfs receive to fail. This issue is fixed by the following linux kernel btrfs patch: commit 3aa5bd367fa5a3 ("btrfs: send: fix sending link commands for existing file paths") Create a file and 2000 hard links to the same inode Create a snapshot for a full send operation Remove 2000 hard links and re-create the last 1000 links Create another snapshot for an incremental send operation. In this subset it primarily covers Btrfs send/receive stream generation and replay, subvolume and snapshot metadata.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick send`. Requirement and capability gates: line 20: `_require_test`; line 21: `_require_scratch`; line 22: `_require_fssum`. Local helper surface: no custom shell functions beyond the linear test body. Important command/API calls include line 16: `_begin_fstest auto quick send`; line 18: `_fixed_by_kernel_commit 3aa5bd367fa5a3 "btrfs: send: fix sending link commands for existing file paths"`; line 24: `send_files_dir=$TEST_DIR/btrfs-test-$seq`; line 26: `rm -fr $send_files_dir`; line 27: `mkdir $send_files_dir`; line 29: `_scratch_mkfs >>$seqres.full 2>&1`; line 30: `_scratch_mount`; line 33: `_btrfs subvolume create $SCRATCH_MNT/vol`; line 40: `_btrfs subvolume snapshot -r $SCRATCH_MNT/vol $SCRATCH_MNT/snap1`; line 41: `_btrfs send -f $send_files_dir/1.snap $SCRATCH_MNT/snap1`; line 52: `_btrfs subvolume snapshot -r $SCRATCH_MNT/vol $SCRATCH_MNT/snap2`; line 53: `_btrfs send -p $SCRATCH_MNT/snap1 -f $send_files_dir/2.snap $SCRATCH_MNT/snap2`; line 56: `$FSSUM_PROG -A -f -w $send_files_dir/1.fssum $SCRATCH_MNT/snap1`; line 57: `$FSSUM_PROG -A -f -w $send_files_dir/2.fssum -x $SCRATCH_MNT/snap2/snap1 $SCRATCH_MNT/snap2`. It documents fixed kernel commit context at line 18: `_fixed_by_kernel_commit 3aa5bd367fa5a3 \`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick send`, install cleanup if needed, enforce requirements, then formats scratch storage, mounts the test filesystem, creates or deletes subvolumes/snapshots, generates and replays send streams, cycles mounts to force persistence. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. It persists send streams, fssum files, or received subvolumes in a temporary test directory and validates replay on a freshly formatted scratch filesystem. Snapshot and subvolume roots are deliberate persistent state used to test root items, received UUIDs, cleaner behavior, and metadata references. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through fssum. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 272 | OK | OK`.

## Risks and Edge Cases
send-stream ordering bugs can emit invalid paths, clone sources, link records, or parent references that only appear after replaying onto a clean filesystem. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/272 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/273 -->
# sources/test-tools/xfstests/tests/btrfs/273

## Purpose
Test that an active zone is properly reclaimed to allow the further allocations, even if the active zones are mostly filled. Override the default cleanup function. which is further fixed by This test requires specific data space usage, skip if we have compression enabled. Fill the zones leaving the last 1MB. In this subset it primarily covers subvolume and snapshot metadata.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick snapshot zone`. Requirement and capability gates: line 31: `_require_zoned_device "$SCRATCH_DEV"`; line 32: `_require_limited_active_zones "$SCRATCH_DEV"`; line 34: `_require_command "$BLKZONE_PROG" blkzone`; line 35: `_require_btrfs_command inspect-internal dump-tree`; line 39: `_require_no_compress`. Local helper surface: `_cleanup()` (line 14), `fill_active_zones()` (line 46), `workout()` (line 66), `stress_data_bgs()` (line 79), `stress_data_bgs_2()` (line 85), `get_meta_bgs()` (line 104), `stress_metadata_bgs()` (line 112). Important command/API calls include line 11: `_begin_fstest auto quick snapshot zone`; line 31: `_require_zoned_device "$SCRATCH_DEV"`; line 32: `_require_limited_active_zones "$SCRATCH_DEV"`; line 34: `_require_command "$BLKZONE_PROG" blkzone`; line 35: `_require_btrfs_command inspect-internal dump-tree`; line 39: `_require_no_compress`; line 54: `$BTRFS_UTIL_PROG filesystem sync ${SCRATCH_MNT}`; line 69: `_scratch_mkfs >/dev/null 2>&1`; line 70: `_scratch_mount`; line 75: `_scratch_unmount`; line 76: `_check_btrfs_filesystem ${SCRATCH_DEV}`; line 81: `dd if=/dev/zero of=${SCRATCH_MNT}/large bs=64M count=1 oflag=sync >>$seqres.full 2>&1`; line 87: `dd if=/dev/zero of=${SCRATCH_MNT}/large bs=64M count=10 conv=fsync >>$seqres.full 2>&1 &`; line 91: `dd if=/dev/zero of=${SCRATCH_MNT}/large2 bs=64M count=10 conv=fsync >>$seqres.full 2>&1 &`. It documents fixed kernel commit context at line 26: `_fixed_by_kernel_commit 2ce543f47843 \`. It documents fixed kernel commit context at line 29: `_fixed_by_kernel_commit d5b81ced74af \`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick snapshot zone`, install cleanup if needed, enforce requirements, then formats scratch storage, mounts the test filesystem, creates or deletes subvolumes/snapshots, runs btrfs check or xfstests scratch checks, cycles mounts to force persistence. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Snapshot and subvolume roots are deliberate persistent state used to test root items, received UUIDs, cleaner behavior, and metadata references. Multi-device tests allocate scratch pool devices and leave correctness evidence in chunk maps, device registry state, degraded mounts, and btrfs check results. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through btrfs-progs. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 273 | Silence is golden`.

## Risks and Edge Cases
device topology tests can expose races in device scan state, degraded mounts, stripe geometry, replacement, and cleanup of scratch device pools. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/273 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/274 -->
# sources/test-tools/xfstests/tests/btrfs/274

## Purpose
Test that we can not delete a subvolume that has an active swap file. Output differs with different btrfs-progs versions and some display multiple lines on failure like this for example: ERROR: Could not destroy subvolume/snapshot: Operation not permitted WARNING: deletion failed with EPERM, send may be in progress Delete subvolume (no-commit): '/home/fdmanana/btrfs-tests/scratch_1/subvol' So just redirect all output to the .full file and check the command's exit status instead. success, all done. In this subset it primarily covers Btrfs send/receive stream generation and replay, multi-device, RAID, seed/sprout, or device-management paths, swapfile activation restrictions, subvolume and snapshot metadata.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick swap subvol`. Requirement and capability gates: line 23: `_require_scratch_swapfile`. Local helper surface: `_cleanup()` (line 12). Important command/API calls include line 15: `rm -f $tmp.*`; line 16: `test -n "$swap_file" && swapoff $swap_file &> /dev/null`; line 23: `_require_scratch_swapfile`; line 25: `_scratch_mkfs >> $seqres.full 2>&1`; line 26: `_scratch_mount`; line 29: `$BTRFS_UTIL_PROG subvolume create $SCRATCH_MNT/subvol | _filter_scratch`; line 33: `_swapon_file $swap_file`; line 35: `echo "Attempting to delete subvolume with swap file enabled..."`; line 45: `$BTRFS_UTIL_PROG subvolume delete $SCRATCH_MNT/subvol >> $seqres.full 2>&1 && echo "subvolume deletion successful, expected failure!"`; line 49: `swapoff $swap_file`; line 51: `echo "Attempting to delete subvolume after disabling swap file..."`; line 52: `$BTRFS_UTIL_PROG subvolume delete $SCRATCH_MNT/subvol >> $seqres.full 2>&1 || echo "subvolume deletion failure, expected success!"`. It documents fixed kernel commit context at line 21: `_fixed_by_kernel_commit 60021bd754c6ca \`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick swap subvol`, install cleanup if needed, enforce requirements, then formats scratch storage, mounts the test filesystem, creates or deletes subvolumes/snapshots. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Snapshot and subvolume roots are deliberate persistent state used to test root items, received UUIDs, cleaner behavior, and metadata references. Swapfile state is persistent inode extent state plus runtime swapon/swapoff activation status. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through btrfs-progs, swap tools. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 274 | Create subvolume 'SCRATCH_MNT/subvol' | Creating and activating swap file... | Attempting to delete subvolume with swap file enabled... | Disabling swap file... | Attempting to delete subvolume after disabling swap file...`.

## Risks and Edge Cases
send-stream ordering bugs can emit invalid paths, clone sources, link records, or parent references that only appear after replaying onto a clean filesystem; swapfile tests rely on cleaner thread and remount commit timing after snapshot deletion. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/274 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/275 -->
# sources/test-tools/xfstests/tests/btrfs/275

## Purpose
Test that no xattr can be changed once btrfs property is set to RO. Create a test file. Attempt to change values of RO (property) filesystem. Check the values of RO (property) filesystem are not changed. Attempt to remove xattr from RO (property) filesystem. Check if xattr still exist. Change filesystem property RO to false Change the xattrs after RO is false. Get the changed values. In this subset it primarily covers Btrfs filesystem behavior through xfstests shell orchestration.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick attr`. Requirement and capability gates: line 17: `_require_attrs`; line 18: `_require_btrfs_command "property"`; line 19: `_require_scratch`. Local helper surface: `set_xattr()` (line 26), `get_xattr()` (line 34), `del_xattr()` (line 41). Important command/API calls include line 15: `_fixed_by_kernel_commit b51111271b03 "btrfs: check if root is readonly while setting security xattr"`; line 17: `_require_attrs`; line 18: `_require_btrfs_command "property"`; line 19: `_require_scratch`; line 21: `_scratch_mkfs >> $seqres.full 2>&1`; line 22: `_scratch_mount`; line 29: `$SETFATTR_PROG -n "user.one" -v $value $FILENAME 2>&1 | _filter_scratch`; line 30: `$SETFATTR_PROG -n "security.one" -v $value $FILENAME 2>&1 | _filter_scratch`; line 31: `$SETFATTR_PROG -n "trusted.one" -v $value $FILENAME 2>&1 | _filter_scratch`; line 36: `_getfattr --absolute-names -n "user.one" $FILENAME 2>&1 | _filter_scratch`; line 37: `_getfattr --absolute-names -n "security.one" $FILENAME 2>&1 | _filter_scratch`; line 38: `_getfattr --absolute-names -n "trusted.one" $FILENAME 2>&1 | _filter_scratch`; line 43: `$SETFATTR_PROG -x "user.one" $FILENAME 2>&1 | _filter_scratch`; line 44: `$SETFATTR_PROG -x "security.one" $FILENAME 2>&1 | _filter_scratch`. It documents fixed kernel commit context at line 15: `_fixed_by_kernel_commit b51111271b03 \`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick attr`, install cleanup if needed, enforce requirements, then formats scratch storage, mounts the test filesystem, runs btrfs check or xfstests scratch checks. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through btrfs-progs. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 275 | ro=true | setfattr: SCRATCH_MNT/foo: Read-only file system | setfattr: SCRATCH_MNT/foo: Read-only file system | setfattr: SCRATCH_MNT/foo: Read-only file system | # file: SCRATCH_MNT/foo | user.one="1" |  | ... (39 expected-output lines total)`.

## Risks and Edge Cases
the main risk is silent metadata or persistence regression that only appears after remount, receive, check, or explicit content comparison. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/275 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/276 -->
# sources/test-tools/xfstests/tests/btrfs/276

## Purpose
Verify that fiemap correctly reports the sharedness of extents for a file with a very large number of extents, spanning many b+tree leaves in the fs tree, and when the file's subvolume was snapshoted. Count the number of shared extents for the whole test file or just for a given range. Count the number of non shared extents for the whole test file or just for a given range. Create a file with 2000 extents, and a fs tree with a height of at least 3 (root node at level 2). We want to verify later that fiemap correctly reports. In this subset it primarily covers multi-device, RAID, seed/sprout, or device-management paths, mount and remount option semantics, subvolume and snapshot metadata.

## Important APIs, Types, and Functions
The fstest declaration is `auto snapshot fiemap remount`. Requirement and capability gates: line 18: `_require_scratch`; line 19: `_require_xfs_io_command "fiemap" "ranged"`; line 20: `_require_attrs`; line 21: `_require_odirect`. Local helper surface: `fiemap_test_file()` (line 26), `count_shared_extents()` (line 39), `count_not_shared_extents()` (line 54). Important command/API calls include line 12: `_begin_fstest auto snapshot fiemap remount`; line 18: `_require_scratch`; line 19: `_require_xfs_io_command "fiemap" "ranged"`; line 20: `_require_attrs`; line 21: `_require_odirect`; line 23: `_scratch_mkfs >> $seqres.full 2>&1`; line 24: `_scratch_mount`; line 33: `$XFS_IO_PROG -c "fiemap -v $offset $len" $SCRATCH_MNT/foo | grep -v 'hole' | tail -n +3`; line 77: `$XFS_IO_PROG -f -d -c "pwrite -b $ext_size $i $ext_size" $SCRATCH_MNT/foo > /dev/null &`; line 101: `sync`; line 107: `_btrfs subvolume snapshot $SCRATCH_MNT $SCRATCH_MNT/snap`; line 116: `$XFS_IO_PROG -d -c "pwrite -b $ext_size 512K $ext_size" -d -c "pwrite -b $ext_size 249M $ext_size" $SCRATCH_MNT/snap/foo | _filter_xfs_io`; line 133: `$BTRFS_UTIL_PROG subvolume delete -c $SCRATCH_MNT/snap | _filter_btrfs_subvol_delete`; line 140: `_scratch_remount commit=1`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto snapshot fiemap remount`, install cleanup if needed, enforce requirements, then formats scratch storage, mounts the test filesystem, creates or deletes subvolumes/snapshots. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Snapshot and subvolume roots are deliberate persistent state used to test root items, received UUIDs, cleaner behavior, and metadata references. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through btrfs-progs, xfs_io. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 276 | Number of non-shared extents in the whole file: 2000 | Number of shared extents in the whole file: 2000 | wrote 65536/65536 bytes at offset 524288 | XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec) | wrote 65536/65536 bytes at offset 261095424 | XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec) | Number of non-shared extents in the whole file: 2 | ... (13 expected-output lines total)`.

## Risks and Edge Cases
the main risk is silent metadata or persistence regression that only appears after remount, receive, check, or explicit content comparison. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/276 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/277 -->
# sources/test-tools/xfstests/tests/btrfs/277

## Purpose
Test sendstreams involving fs-verity enabled files. Override the default cleanup function. In this subset it primarily covers Btrfs send/receive stream generation and replay, fs-verity metadata and recovery behavior.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick verity send`. Requirement and capability gates: line 23: `_require_scratch_verity`; line 24: `_require_fsverity_builtin_signatures`; line 25: `_require_command "$SETCAP_PROG" setcap`; line 26: `_require_command "$GETCAP_PROG" getcap`; line 27: `_require_btrfs_send_version 3`. Local helper surface: `_cleanup()` (line 13), `_test_send_verity()` (line 37). Important command/API calls include line 10: `_begin_fstest auto quick verity send`; line 27: `_require_btrfs_send_version 3`; line 37: `_test_send_verity() {`; line 42: `_scratch_mkfs >> $seqres.full`; line 43: `_scratch_mount`; line 44: `echo -e "\nverity send/recv test: sig: $sig salt: $salt"`; line 47: `echo "create subvolume"`; line 48: `$BTRFS_UTIL_PROG subvolume create $subv >> $seqres.full`; line 50: `$XFS_IO_PROG -fc "pwrite -q -S 0x58 0 12288" $fsv_file`; line 80: `echo "set subvolume read only"`; line 82: `echo "send subvolume"`; line 83: `$BTRFS_UTIL_PROG send $subv -f $stream -q --proto=3 >> $seqres.full`; line 90: `echo "receive sendstream"`; line 91: `$BTRFS_UTIL_PROG receive $SCRATCH_MNT -f $stream -q >> $seqres.full`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick verity send`, install cleanup if needed, enforce requirements, then formats scratch storage, mounts the test filesystem, creates or deletes subvolumes/snapshots, generates and replays send streams, runs btrfs check or xfstests scratch checks, cycles mounts to force persistence. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. It persists send streams, fssum files, or received subvolumes in a temporary test directory and validates replay on a freshly formatted scratch filesystem. Snapshot and subvolume roots are deliberate persistent state used to test root items, received UUIDs, cleaner behavior, and metadata references. fs-verity state persists in inode items, Merkle tree extents, descriptor items, orphan cleanup, and read-time verification failures. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through btrfs-progs, xfs_io. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 277 |  | verity send/recv test: sig: false salt: false | create subvolume | create file | enable verity | modify other properties | set subvolume read only | ... (59 expected-output lines total)`.

## Risks and Edge Cases
send-stream ordering bugs can emit invalid paths, clone sources, link records, or parent references that only appear after replaying onto a clean filesystem; fs-verity tests intentionally corrupt on-disk items, so mount recovery and error reporting must distinguish expected EIO from metadata damage. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/277 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/278 -->
# sources/test-tools/xfstests/tests/btrfs/278

## Purpose
Regression test for btrfs incremental send issue when processing inodes with no links This issue is fixed by the following linux kernel btrfs patch: commit 9ed0a72e5b355d ("btrfs: send: fix failures when processing inodes with no links") Creating the first snapshot looks like: . (ino 256) |--- deleted.file (ino 257) |--- deleted.dir/ (ino 258). In this subset it primarily covers Btrfs send/receive stream generation and replay, subvolume and snapshot metadata.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick send`. Requirement and capability gates: line 20: `_require_test`; line 21: `_require_scratch`; line 22: `_require_btrfs_command "property"`; line 23: `_require_fssum`. Local helper surface: no custom shell functions beyond the linear test body. Important command/API calls include line 16: `_begin_fstest auto quick send`; line 18: `_fixed_by_kernel_commit 9ed0a72e5b355d "btrfs: send: fix failures when processing inodes with no links"`; line 25: `send_files_dir=$TEST_DIR/btrfs-test-$seq`; line 27: `rm -fr $send_files_dir`; line 28: `mkdir $send_files_dir`; line 30: `_scratch_mkfs >>$seqres.full 2>&1`; line 31: `_scratch_mount`; line 32: `_btrfs subvolume create $SCRATCH_MNT/vol`; line 54: `_btrfs subvolume snapshot -r $SCRATCH_MNT/vol $SCRATCH_MNT/snap1`; line 73: `_btrfs subvolume snapshot -r $SCRATCH_MNT/vol $SCRATCH_MNT/snap2`; line 140: `_btrfs send -f $send_files_dir/1.snap $SCRATCH_MNT/snap1`; line 182: `_btrfs send -p $SCRATCH_MNT/snap1 -f $send_files_dir/2.snap $SCRATCH_MNT/snap2`; line 185: `$FSSUM_PROG -A -f -w $send_files_dir/1.fssum $SCRATCH_MNT/snap1`; line 186: `$FSSUM_PROG -A -f -w $send_files_dir/2.fssum -x $SCRATCH_MNT/snap2/snap1 $SCRATCH_MNT/snap2`. It documents fixed kernel commit context at line 18: `_fixed_by_kernel_commit 9ed0a72e5b355d \`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick send`, install cleanup if needed, enforce requirements, then formats scratch storage, mounts the test filesystem, creates or deletes subvolumes/snapshots, generates and replays send streams, cycles mounts to force persistence. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. It persists send streams, fssum files, or received subvolumes in a temporary test directory and validates replay on a freshly formatted scratch filesystem. Snapshot and subvolume roots are deliberate persistent state used to test root items, received UUIDs, cleaner behavior, and metadata references. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through btrfs-progs, fssum. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 278 | OK | OK`.

## Risks and Edge Cases
send-stream ordering bugs can emit invalid paths, clone sources, link records, or parent references that only appear after replaying onto a clean filesystem. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/278 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/279 -->
# sources/test-tools/xfstests/tests/btrfs/279

## Purpose
Test that if we have two files with shared extents, after removing one of the files, if we do a fiemap against the other file, it does not report extents as shared anymore. This exercises the processing of delayed references for data extents in the backref walking code, used by fiemap to determine if an extent is shared. Create two test subvolumes, we'll reflink files between them. success, all done. In this subset it primarily covers multi-device, RAID, seed/sprout, or device-management paths, reflink/clone extent sharing, subvolume and snapshot metadata.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick subvol fiemap clone`. Requirement and capability gates: line 21: `_require_scratch_reflink`; line 22: `_require_cp_reflink`; line 23: `_require_xfs_io_command "fiemap"`. Local helper surface: `run_test()` (line 28). Important command/API calls include line 18: `. ./common/reflink`; line 21: `_require_scratch_reflink`; line 22: `_require_cp_reflink`; line 23: `_require_xfs_io_command "fiemap"`; line 34: `$XFS_IO_PROG -f -c "pwrite 0 64K" $file_path_1 | _filter_xfs_io`; line 35: `_cp_reflink $file_path_1 $file_path_2`; line 37: `if [ $do_sync -eq 1 ]; then`; line 38: `sync`; line 41: `echo "Fiemap of $file_path_1 before deleting $file_path_2:" | _filter_scratch`; line 43: `$XFS_IO_PROG -c "fiemap -v" $file_path_1 | _filter_fiemap_flags`; line 45: `rm -f $file_path_2`; line 47: `echo "Fiemap of $file_path_1 after deleting $file_path_2:" | _filter_scratch`; line 52: `_scratch_mkfs >> $seqres.full 2>&1`; line 53: `_scratch_mount`. It documents fixed kernel commit context at line 25: `_fixed_by_kernel_commit 4fc7b5722824 \`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick subvol fiemap clone`, install cleanup if needed, enforce requirements, then formats scratch storage, mounts the test filesystem, creates or deletes subvolumes/snapshots. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Snapshot and subvolume roots are deliberate persistent state used to test root items, received UUIDs, cleaner behavior, and metadata references. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through btrfs-progs, xfs_io. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 279 | Create subvolume 'SCRATCH_MNT/subv1' | Create subvolume 'SCRATCH_MNT/subv2' |  | Testing with same subvolume and without transaction commit |  | wrote 65536/65536 bytes at offset 0 | XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec) | ... (39 expected-output lines total)`.

## Risks and Edge Cases
the main risk is silent metadata or persistence regression that only appears after remount, receive, check, or explicit content comparison. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/279 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/280 -->
# sources/test-tools/xfstests/tests/btrfs/280

## Purpose
Test that if we have a large file, with file extent items spanning several leaves in the fs tree, and that is shared due to a snapshot, if we COW one of the extents, doing a fiemap will report the respective file range as not shared. This exercises the processing of delayed references for metadata extents in the backref walking code, used by fiemap to determine if an extent is shared. We use compression because it's a very quick way to create a file with a very large number of extents (compression limits the maximum extent size to 128K) and while using very little disk space. In this subset it primarily covers subvolume and snapshot metadata.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick compress snapshot fiemap defrag`. Requirement and capability gates: line 21: `_require_scratch`; line 22: `_require_xfs_io_command "fiemap"`. Local helper surface: no custom shell functions beyond the linear test body. Important command/API calls include line 16: `_begin_fstest auto quick compress snapshot fiemap defrag`; line 21: `_require_scratch`; line 22: `_require_xfs_io_command "fiemap"`; line 27: `_scratch_mkfs >> $seqres.full 2>&1`; line 31: `_scratch_mount -o compress`; line 36: `$XFS_IO_PROG -f -c "pwrite -b 1M 0 128M" $SCRATCH_MNT/foo | _filter_xfs_io`; line 44: `$BTRFS_UTIL_PROG filesystem defrag "$SCRATCH_MNT/foo" >> $seqres.full`; line 47: `_btrfs subvolume snapshot $SCRATCH_MNT $SCRATCH_MNT/snap`; line 52: `$XFS_IO_PROG -c "fiemap -v" $SCRATCH_MNT/foo | _filter_fiemap_flags 1`; line 55: `echo "Overwriting file range [120M, 120M + 128K) in the snapshot"`; line 57: `$XFS_IO_PROG -c "pwrite -b 128K 120M 128K" $SCRATCH_MNT/snap/foo | _filter_xfs_io`; line 60: `$XFS_IO_PROG -c "fsync" $SCRATCH_MNT/snap/foo`; line 63: `echo "File foo fiemap after COWing extent in the snapshot:"`. It documents fixed kernel commit context at line 24: `_fixed_by_kernel_commit 943553ef9b51 \`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick compress snapshot fiemap defrag`, install cleanup if needed, enforce requirements, then formats scratch storage, mounts the test filesystem, creates or deletes subvolumes/snapshots. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Snapshot and subvolume roots are deliberate persistent state used to test root items, received UUIDs, cleaner behavior, and metadata references. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through btrfs-progs, xfs_io. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 280 | wrote 134217728/134217728 bytes at offset 0 | XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec) |  | File foo fiemap before COWing extent: |  | 0: [0..261887]: shared|encoded | 1: [261888..262143]: shared|encoded|last | ... (20 expected-output lines total)`.

## Risks and Edge Cases
the main risk is silent metadata or persistence regression that only appears after remount, receive, check, or explicit content comparison. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/280 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/281 -->
# sources/test-tools/xfstests/tests/btrfs/281

## Purpose
Test that if we have a snapshot with a compressed extent that is partially shared between two files, one of them has a size that is not sector size aligned, we create a v2 send stream for the snapshot with compressed data, and then apply that stream to another filesystem, the operation succeeds and no data is missing. Also check that the file that had a reference to the whole extent gets two compressed extents in the new filesystem, with only one of them being shared (reflinked). Compression can't happen with nodatasum, so skip the test. File foo has a size of 65K, which is not sector size aligned for any. In this subset it primarily covers Btrfs send/receive stream generation and replay, reflink/clone extent sharing, subvolume and snapshot metadata.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick send compress clone fiemap`. Requirement and capability gates: line 22: `_require_test`; line 23: `_require_scratch_reflink`; line 24: `_require_btrfs_send_version 2`; line 25: `_require_xfs_io_command "fiemap"`; line 26: `_require_fssum`; line 27: `_require_btrfs_no_nodatacow`; line 29: `_require_btrfs_no_nodatasum`. Local helper surface: no custom shell functions beyond the linear test body. Important command/API calls include line 16: `_begin_fstest auto quick send compress clone fiemap`; line 19: `. ./common/reflink`; line 23: `_require_scratch_reflink`; line 24: `_require_btrfs_send_version 2`; line 31: `_fixed_by_kernel_commit a11452a3709e "btrfs: send: avoid unaligned encoded writes when attempting to clone range"`; line 34: `send_files_dir=$TEST_DIR/btrfs-test-$seq`; line 35: `send_stream=$send_files_dir/snap.stream`; line 36: `snap_fssum=$send_files_dir/snap.fssum`; line 38: `rm -fr $send_files_dir`; line 39: `mkdir $send_files_dir`; line 41: `_scratch_mkfs >> $seqres.full 2>&1`; line 42: `_scratch_mount -o compress`; line 46: `$XFS_IO_PROG -f -c "pwrite -S 0xab 0 65K" $SCRATCH_MNT/foo | _filter_xfs_io`; line 49: `$XFS_IO_PROG -f -c "pwrite -S 0xcd 0 128K" $SCRATCH_MNT/bar | _filter_xfs_io`. It documents fixed kernel commit context at line 31: `_fixed_by_kernel_commit a11452a3709e \`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick send compress clone fiemap`, install cleanup if needed, enforce requirements, then formats scratch storage, mounts the test filesystem, creates or deletes subvolumes/snapshots, generates and replays send streams, cycles mounts to force persistence. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. It persists send streams, fssum files, or received subvolumes in a temporary test directory and validates replay on a freshly formatted scratch filesystem. Snapshot and subvolume roots are deliberate persistent state used to test root items, received UUIDs, cleaner behavior, and metadata references. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through btrfs-progs, xfs_io, fssum. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 281 | wrote 66560/66560 bytes at offset 0 | XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec) | wrote 131072/131072 bytes at offset 0 | XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec) | linked 65536/65536 bytes at offset 0 | XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec) | Creating snapshot and a send stream for it... | ... (16 expected-output lines total)`.

## Risks and Edge Cases
send-stream ordering bugs can emit invalid paths, clone sources, link records, or parent references that only appear after replaying onto a clean filesystem. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/281 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/282 -->
# sources/test-tools/xfstests/tests/btrfs/282

## Purpose
Make sure scrub speed limitation works as expected. For direct IO without falling back to buffered IO. For data checksum verification during scrub We want at least 10G for the scratch device. Make sure we can create scrub progress data file Check if we have the sysfs interface first. Create a NOCOW file and do direct IO for 4 seconds to measure the performance. The only way to reach real disk performance is direct IO without falling back to buffered IO, thus requiring NOCOW. In this subset it primarily covers multi-device, RAID, seed/sprout, or device-management paths, scrub detection and repair paths.

## Important APIs, Types, and Functions
The fstest declaration is `auto scrub`. Requirement and capability gates: line 24: `_require_odirect`; line 25: `_require_chattr C`; line 27: `_require_btrfs_no_nodatasum`; line 30: `_require_scratch_size $(( 10 * 1024 * 1024))`. Local helper surface: `_cleanup()` (line 12). Important command/API calls include line 10: `_begin_fstest auto scrub`; line 20: `_wants_kernel_commit eb3b50536642 "btrfs: scrub: per-device bandwidth control"`; line 39: `_scratch_mkfs >> $seqres.full 2>&1`; line 40: `_scratch_mount`; line 47: `if [ ! -f "${devinfo_dir}/scrub_speed_max" ]; then`; line 48: `_notrun "No sysfs interface for scrub speed throttle"`; line 57: `$XFS_IO_PROG -d -c "pwrite -b 128K 0 1E" "$SCRATCH_MNT/filler" >> $seqres.full 2>&1 &`; line 70: `_notrun "Storage too fast, unreliable scrub speed"`; line 82: `$XFS_IO_PROG -c "pwrite -i /dev/urandom 0 $size" $SCRATCH_MNT/filler >> $seqres.full`; line 88: `$BTRFS_UTIL_PROG scrub start -B $SCRATCH_MNT >> $seqres.full`; line 102: `init_speed=$($BTRFS_UTIL_PROG scrub status --raw $SCRATCH_MNT | grep "Rate:" | $AWK_PROG '{print $2}' | cut -f1 -d\/)`; line 107: `_notrun "btrfs-progs doesn't support scrub rate reporting"`; line 114: `echo "$target_speed" > "${devinfo_dir}/scrub_speed_max"`; line 118: `speed=$($BTRFS_UTIL_PROG scrub status --raw $SCRATCH_MNT | grep "Rate:" | $AWK_PROG '{print $2}' | cut -f1 -d\/)`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto scrub`, install cleanup if needed, enforce requirements, then formats scratch storage, mounts the test filesystem, runs scrub or checks scrub reports, cycles mounts to force persistence. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Multi-device tests allocate scratch pool devices and leave correctness evidence in chunk maps, device registry state, degraded mounts, and btrfs check results. Corruption is injected below the filesystem and then validated after scrub, remount, or direct device reads. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through btrfs-progs, xfs_io. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 282 | Silence is golden`.

## Risks and Edge Cases
device topology tests can expose races in device scan state, degraded mounts, stripe geometry, replacement, and cleanup of scratch device pools; scrub repair signals depend on precise logical-to-physical mapping and can miss corruption if checksum, parity, or duplicate-copy selection regresses. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/282 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/283 -->
# sources/test-tools/xfstests/tests/btrfs/283

## Purpose
Test that send operations do the best cloning decisions when we have extents that are shared but some files refer to the full extent while others refer to only a section of the extent. When using compression, btrfs limits the extent size to 128K, so do not do larger writes and then expect larger extents, as that would break the test if we are run with compression enabled through $MOUNT_OPTIONS (resulting in mismatch with the golden output). Now clone file foo twice, which will make the 128K extent shared 3 times. Overwrite the second half of file foo. In this subset it primarily covers Btrfs send/receive stream generation and replay, reflink/clone extent sharing.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick send clone fiemap`. Requirement and capability gates: line 18: `_require_test`; line 19: `_require_scratch_reflink`; line 20: `_require_cp_reflink`; line 21: `_require_xfs_io_command "fiemap"`; line 22: `_require_fssum`. Local helper surface: no custom shell functions beyond the linear test body. Important command/API calls include line 12: `_begin_fstest auto quick send clone fiemap`; line 15: `. ./common/reflink`; line 19: `_require_scratch_reflink`; line 20: `_require_cp_reflink`; line 24: `_wants_kernel_commit c7499a64dcf6 "btrfs: send: optimize clone detection to increase extent sharing"`; line 30: `_notrun "Couldn't find queue path for zoned device"`; line 37: `send_files_dir=$TEST_DIR/btrfs-test-$seq`; line 38: `send_stream=$send_files_dir/snap.stream`; line 39: `snap_fssum=$send_files_dir/snap.fssum`; line 41: `rm -fr $send_files_dir`; line 42: `mkdir $send_files_dir`; line 44: `_scratch_mkfs >> $seqres.full 2>&1`; line 45: `_scratch_mount`; line 51: `$XFS_IO_PROG -f -c "pwrite -S 0xab -b 128K 0 128K" $SCRATCH_MNT/foo | _filter_xfs_io`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick send clone fiemap`, install cleanup if needed, enforce requirements, then formats scratch storage, mounts the test filesystem, creates or deletes subvolumes/snapshots, generates and replays send streams, cycles mounts to force persistence. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. It persists send streams, fssum files, or received subvolumes in a temporary test directory and validates replay on a freshly formatted scratch filesystem. Snapshot and subvolume roots are deliberate persistent state used to test root items, received UUIDs, cleaner behavior, and metadata references. Multi-device tests allocate scratch pool devices and leave correctness evidence in chunk maps, device registry state, degraded mounts, and btrfs check results. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through btrfs-progs, xfs_io, fssum. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 283 | wrote 131072/131072 bytes at offset 0 | XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec) | wrote 65536/65536 bytes at offset 65536 | XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec) | Creating snapshot and a send stream for it... | At subvol SCRATCH_MNT/snap | Creating a new filesystem to receive the send stream... | ... (25 expected-output lines total)`.

## Risks and Edge Cases
send-stream ordering bugs can emit invalid paths, clone sources, link records, or parent references that only appear after replaying onto a clean filesystem; device topology tests can expose races in device scan state, degraded mounts, stripe geometry, replacement, and cleanup of scratch device pools. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/283 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/284 -->
# sources/test-tools/xfstests/tests/btrfs/284

## Purpose
Test btrfs send stream v2, sending and receiving compressed data without decompression at the sending side. The size needed is variable as it depends on the specific randomized operations from fsstress and on the value of $LOAD_FACTOR. But require at least $LOAD_FACTOR * 1G, just to be on the safe side. Redirect stdout to the .full file and make it not part of the golden output. This is because the number of available compression algorithms may vary across kernel versions, so the number of times we are running this function is variable. In this subset it primarily covers Btrfs send/receive stream generation and replay, subvolume and snapshot metadata.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick send compress snapshot`. Requirement and capability gates: line 13: `_require_btrfs_send_version 2`; line 14: `_require_test`; line 18: `_require_scratch_size $(($LOAD_FACTOR * 1 * 1024 * 1024))`; line 19: `_require_fssum`. Local helper surface: `run_send_test()` (line 35). Important command/API calls include line 11: `_begin_fstest auto quick send compress snapshot`; line 13: `_require_btrfs_send_version 2`; line 21: `_fixed_by_git_commit btrfs-progs e3209f8792f4 "btrfs-progs: receive: fix a corruption when decompressing zstd extents"`; line 23: `_fixed_by_git_commit btrfs-progs 6f4a51886b37 "btrfs-progs: receive: fix silent data loss after fall back from encoded write"`; line 26: `send_files_dir=$TEST_DIR/btrfs-test-$seq`; line 28: `rm -fr $send_files_dir`; line 29: `mkdir $send_files_dir`; line 35: `run_send_test()`; line 44: `_scratch_mkfs >> $seqres.full 2>&1`; line 45: `_scratch_mount -o compress=$algo`; line 47: `snapshot_cmd="$BTRFS_UTIL_PROG subvolume snapshot -r $SCRATCH_MNT"`; line 48: `snapshot_cmd="$snapshot_cmd $SCRATCH_MNT/snap1"`; line 52: `_run_fsstress -d $SCRATCH_MNT -p 1 -n $((LOAD_FACTOR * 200)) -w -x "$snapshot_cmd"`; line 55: `$BTRFS_UTIL_PROG subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/snap2 >> $seqres.full`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick send compress snapshot`, install cleanup if needed, enforce requirements, then formats scratch storage, mounts the test filesystem, creates or deletes subvolumes/snapshots, generates and replays send streams, runs btrfs check or xfstests scratch checks, cycles mounts to force persistence. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. It persists send streams, fssum files, or received subvolumes in a temporary test directory and validates replay on a freshly formatted scratch filesystem. Snapshot and subvolume roots are deliberate persistent state used to test root items, received UUIDs, cleaner behavior, and metadata references. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through btrfs-progs, fssum, fsstress. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 284 | Silence is golden`.

## Risks and Edge Cases
send-stream ordering bugs can emit invalid paths, clone sources, link records, or parent references that only appear after replaying onto a clean filesystem. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/284 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/285 -->
# sources/test-tools/xfstests/tests/btrfs/285

## Purpose
Test that mounting a btrfs filesystem properly loads block group size classes. Write files with extents in each size class Sync to force the extent allocation cycle mount to drop the block group cache Another write causes us to actually load the block groups success, all done. In this subset it primarily covers Btrfs filesystem behavior through xfstests shell orchestration.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick`. Requirement and capability gates: line 17: `_require_scratch`; line 18: `_require_btrfs_fs_sysfs`; line 19: `_require_fs_sysfs allocation/data/size_classes`. Local helper surface: `sysfs_size_classes()` (line 12). Important command/API calls include line 17: `_require_scratch`; line 18: `_require_btrfs_fs_sysfs`; line 19: `_require_fs_sysfs allocation/data/size_classes`; line 26: `_scratch_mkfs >/dev/null`; line 27: `_scratch_mount`; line 29: `$XFS_IO_PROG -fc "pwrite -q 0 $small" $f.small`; line 30: `$XFS_IO_PROG -fc "pwrite -q 0 $medium" $f.medium`; line 31: `$XFS_IO_PROG -fc "pwrite -q 0 $large" $f.large`; line 33: `sync`; line 37: `_scratch_cycle_mount`; line 40: `$XFS_IO_PROG -fc "pwrite -q 0 $large" $f.large.2`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick`, install cleanup if needed, enforce requirements, then formats scratch storage, mounts the test filesystem, cycles mounts to force persistence. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through xfs_io. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 285 | Silence is golden`.

## Risks and Edge Cases
the main risk is silent metadata or persistence regression that only appears after remount, receive, check, or explicit content comparison. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/285 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/286 -->
# sources/test-tools/xfstests/tests/btrfs/286

## Purpose
Make sure btrfs dev-replace on missing device won't cause data corruption for NODATASUM data. success, all done. In this subset it primarily covers multi-device, RAID, seed/sprout, or device-management paths.

## Important APIs, Types, and Functions
The fstest declaration is `auto replace raid`. Requirement and capability gates: line 15: `_require_command "$WIPEFS_PROG" wipefs`; line 17: `_require_fssum`; line 18: `_require_scratch_dev_pool 5`. Local helper surface: `workload()` (line 22). Important command/API calls include line 11: `_begin_fstest auto replace raid`; line 15: `_require_command "$WIPEFS_PROG" wipefs`; line 16: `_btrfs_get_profile_configs replace-missing`; line 17: `_require_fssum`; line 18: `_require_scratch_dev_pool 5`; line 19: `_scratch_dev_pool_get 4`; line 28: `rm -f $tmp.fssum`; line 29: `_scratch_pool_mkfs "$profile" >> $seqres.full 2>&1`; line 32: `_scratch_mount -o nodatasum`; line 35: `sync`; line 39: `$FSSUM_PROG -n -d -f -w $tmp.fssum $SCRATCH_MNT`; line 40: `_scratch_unmount`; line 46: `_scratch_mount -o degraded,nodatasum`; line 49: `echo "=== Verify the contents before replace ===" >> $seqres.full`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto replace raid`, install cleanup if needed, enforce requirements, then mounts the test filesystem, cycles mounts to force persistence. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Multi-device tests allocate scratch pool devices and leave correctness evidence in chunk maps, device registry state, degraded mounts, and btrfs check results. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through btrfs-progs, fssum. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 286 | Silence is golden`.

## Risks and Edge Cases
device topology tests can expose races in device scan state, degraded mounts, stripe geometry, replacement, and cleanup of scratch device pools. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/286 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/287 -->
# sources/test-tools/xfstests/tests/btrfs/287

## Purpose
Test btrfs' logical to inode ioctls (v1 and v2). This is a test case to test the logical to ino ioctl in general but it also serves as a regression a test for an issue fixed by the following commit. The IDs of the snapshots (roots) we create may vary if we are using the free space tree or not for example (mkfs options -R free-space-tree and -R ^free-space-tree). So replace their IDs with names so that we don't get golden output mismatches if we are using features that create other roots. Create a file with two extents: 1) One 4M extent covering the file range [0, 4M). In this subset it primarily covers multi-device, RAID, seed/sprout, or device-management paths, reflink/clone extent sharing, logical-to-inode extent resolution, subvolume and snapshot metadata.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick snapshot clone prealloc punch logical_resolve`. Requirement and capability gates: line 15: `_require_btrfs_scratch_logical_resolve_v2`; line 16: `_require_scratch_reflink`; line 17: `_require_xfs_io_command "falloc"`; line 18: `_require_xfs_io_command "fpunch"`. Local helper surface: `query_logical_ino()` (line 25), `filter_snapshot_ids()` (line 34). Important command/API calls include line 10: `_begin_fstest auto quick snapshot clone prealloc punch logical_resolve`; line 13: `. ./common/reflink`; line 16: `_require_scratch_reflink`; line 17: `_require_xfs_io_command "falloc"`; line 27: `$BTRFS_UTIL_PROG inspect-internal logical-resolve -P $* $SCRATCH_MNT`; line 34: `filter_snapshot_ids()`; line 39: `_scratch_mkfs >> $seqres.full || _fail "mkfs failed"`; line 40: `_scratch_mount`; line 46: `$XFS_IO_PROG -f -c "falloc 0 4M" -c "falloc 4M 4M" $SCRATCH_MNT/foo`; line 61: `$XFS_IO_PROG -c "reflink $SCRATCH_MNT/foo 0 $sz_8m $sz_8m" $SCRATCH_MNT/foo | _filter_xfs_io`; line 64: `$XFS_IO_PROG -c "reflink $SCRATCH_MNT/foo 0 $sz_16m $sz_8m" $SCRATCH_MNT/foo | _filter_xfs_io`; line 113: `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/snap1`; line 114: `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/snap2`; line 122: `query_logical_ino $first_extent_bytenr | filter_snapshot_ids`. It documents fixed kernel commit context at line 22: `_fixed_by_kernel_commit 0cad8f14d70c \`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick snapshot clone prealloc punch logical_resolve`, install cleanup if needed, enforce requirements, then formats scratch storage, mounts the test filesystem, creates or deletes subvolumes/snapshots. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Snapshot and subvolume roots are deliberate persistent state used to test root items, received UUIDs, cleaner behavior, and metadata references. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through btrfs-progs, xfs_io. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 287 | resolve first extent: | inode 257 offset 0 root 5 | resolve second extent: | inode 257 offset 4194304 root 5 | linked 8388608/8388608 bytes at offset 8388608 | XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec) | linked 8388608/8388608 bytes at offset 16777216 | ... (89 expected-output lines total)`.

## Risks and Edge Cases
device topology tests can expose races in device scan state, degraded mounts, stripe geometry, replacement, and cleanup of scratch device pools. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/287 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/288 -->
# sources/test-tools/xfstests/tests/btrfs/288

## Purpose
Make sure btrfs-scrub respects the read-only flag. Overwriting data is forbidden on a zoned block device Step 1, create a raid btrfs with one 128K file Step 2, corrupt one mirror so we can still repair the fs. ensure btrfs-map-logical sees the tree updates Step 3, do a read-only scrub, which should not fix the corruption. Step 4, make sure the corruption is still there success, all done. In this subset it primarily covers multi-device, RAID, seed/sprout, or device-management paths, scrub detection and repair paths, logical-to-inode extent resolution.

## Important APIs, Types, and Functions
The fstest declaration is `auto repair quick volume scrub`. Requirement and capability gates: line 14: `_require_scratch_dev_pool 2`; line 16: `_require_odirect`; line 18: `_require_non_zoned_device "${SCRATCH_DEV}"`. Local helper surface: no custom shell functions beyond the linear test body. Important command/API calls include line 10: `_begin_fstest auto repair quick volume scrub`; line 14: `_require_scratch_dev_pool 2`; line 16: `_require_odirect`; line 18: `_require_non_zoned_device "${SCRATCH_DEV}"`; line 20: `_fixed_by_kernel_commit 1f2030ff6e49 "btrfs: scrub: respect the read-only flag during repair"`; line 23: `_scratch_dev_pool_get 2`; line 27: `_scratch_pool_mkfs -d raid1 -b 1G >> $seqres.full 2>&1`; line 28: `_scratch_mount`; line 30: `$XFS_IO_PROG -f -d -c "pwrite -S 0xaa -b 128K 0 128K" "$SCRATCH_MNT/foobar" | _filter_xfs_io`; line 36: `sync`; line 38: `logical=$(_btrfs_get_first_logical $SCRATCH_MNT/foobar)`; line 40: `physical1=$(_btrfs_get_physical ${logical} 1)`; line 41: `devpath1=$(_btrfs_get_device_path ${logical} 1)`; line 43: `_scratch_unmount`. It documents fixed kernel commit context at line 20: `_fixed_by_kernel_commit 1f2030ff6e49 \`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto repair quick volume scrub`, install cleanup if needed, enforce requirements, then mounts the test filesystem, runs scrub or checks scrub reports, cycles mounts to force persistence. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Multi-device tests allocate scratch pool devices and leave correctness evidence in chunk maps, device registry state, degraded mounts, and btrfs check results. Corruption is injected below the filesystem and then validated after scrub, remount, or direct device reads. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through btrfs-progs, xfs_io. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 288 | step 1......mkfs.btrfs | wrote 131072/131072 bytes at offset 0 | XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec) | step 2......corrupt one mirror | step 3......do a read-only scrub | step 4......verify the corruption is not repaired |   the first 16 bytes of the extent at mirror 1: | ... (9 expected-output lines total)`.

## Risks and Edge Cases
device topology tests can expose races in device scan state, degraded mounts, stripe geometry, replacement, and cleanup of scratch device pools; scrub repair signals depend on precise logical-to-physical mapping and can miss corruption if checksum, parity, or duplicate-copy selection regresses. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/288 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/289 -->
# sources/test-tools/xfstests/tests/btrfs/289

## Purpose
Make sure btrfs-scrub reports errors correctly for repaired sectors. No data checksums for NOCOW and NODATACOW cases, so can't detect corruption and repair data. Overwriting data is forbidden on a zoned block device We need to ensure a fixed extent size and we corrupt by writing directly to the device, so skip if compression is enabled. The errors reported would be in the unit of sector, thus the number is dependent on the sectorsize. Create a single btrfs with DUP data profile, and create one 128K file. In this subset it primarily covers multi-device, RAID, seed/sprout, or device-management paths, scrub detection and repair paths.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick scrub repair`. Requirement and capability gates: line 14: `_require_scratch`; line 17: `_require_btrfs_no_nodatacow`; line 18: `_require_btrfs_no_nodatasum`; line 20: `_require_odirect`; line 22: `_require_non_zoned_device "${SCRATCH_DEV}"`; line 25: `_require_no_compress`; line 28: `_require_btrfs_support_sectorsize 4096`. Local helper surface: no custom shell functions beyond the linear test body. Important command/API calls include line 10: `_begin_fstest auto quick scrub repair`; line 14: `_require_scratch`; line 17: `_require_btrfs_no_nodatacow`; line 18: `_require_btrfs_no_nodatasum`; line 20: `_require_odirect`; line 22: `_require_non_zoned_device "${SCRATCH_DEV}"`; line 25: `_require_no_compress`; line 28: `_require_btrfs_support_sectorsize 4096`; line 30: `_fixed_by_kernel_commit 79b8ee702c91 "btrfs: scrub: also report errors hit during the initial read"`; line 34: `_scratch_mkfs -s 4k -d dup -b 1G >> $seqres.full 2>&1`; line 35: `_scratch_mount`; line 36: `$XFS_IO_PROG -f -d -c "pwrite -S 0xaa -b 128K 0 128K" "$SCRATCH_MNT/foobar" > /dev/null`; line 38: `sync`; line 40: `logical=$(_btrfs_get_first_logical "$SCRATCH_MNT/foobar")`. It documents fixed kernel commit context at line 30: `_fixed_by_kernel_commit 79b8ee702c91 \`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick scrub repair`, install cleanup if needed, enforce requirements, then formats scratch storage, mounts the test filesystem, runs scrub or checks scrub reports, cycles mounts to force persistence. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Multi-device tests allocate scratch pool devices and leave correctness evidence in chunk maps, device registry state, degraded mounts, and btrfs check results. Corruption is injected below the filesystem and then validated after scrub, remount, or direct device reads. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through btrfs-progs, xfs_io. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 289 | Silence is golden`.

## Risks and Edge Cases
device topology tests can expose races in device scan state, degraded mounts, stripe geometry, replacement, and cleanup of scratch device pools; scrub repair signals depend on precise logical-to-physical mapping and can miss corruption if checksum, parity, or duplicate-copy selection regresses. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/289 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/290 -->
# sources/test-tools/xfstests/tests/btrfs/290

## Purpose
Test btrfs support for fsverity. This test extends the generic fsverity testing by corrupting inline extents, preallocated extents, holes, and the Merkle descriptor in a btrfs-aware way. Override the default cleanup function. We exercise corrupting an inline extent and inline extents can't be created with nodatacow, we get instead a regular file extent item and if we attempt to corrupt its disk_bytenr field with btrfs-corrupt-block we fail tree-checker validation at mount time resulting in failure to mount and the following in dmesg:. In this subset it primarily covers fs-verity metadata and recovery behavior.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick verity prealloc`. Requirement and capability gates: line 25: `_require_scratch_verity`; line 26: `_require_scratch_nocheck`; line 27: `_require_odirect`; line 28: `_require_xfs_io_command "falloc"`; line 29: `_require_xfs_io_command "pread"`; line 30: `_require_xfs_io_command "pwrite"`; line 31: `_require_btrfs_corrupt_block "value"`; line 32: `_require_btrfs_corrupt_block "offset"`; line 44: `_require_btrfs_no_nodatacow`. Local helper surface: `_cleanup()` (line 18), `get_ino()` (line 47), `validate()` (line 52), `corrupt_inline()` (line 63), `corrupt_prealloc_to_reg()` (line 77), `corrupt_reg_to_prealloc()` (line 94), `corrupt_punch_hole()` (line 107), `corrupt_plug_hole()` (line 124), `corrupt_verity_descriptor()` (line 139), `corrupt_root_hash()` (line 154), `corrupt_merkle_tree()` (line 167). Important command/API calls include line 26: `_require_scratch_nocheck`; line 28: `_require_xfs_io_command "falloc"`; line 30: `_require_xfs_io_command "pwrite"`; line 31: `_require_btrfs_corrupt_block "value"`; line 32: `_require_btrfs_corrupt_block "offset"`; line 65: `$XFS_IO_PROG -fc "pwrite -q -S 0x58 0 42" $f`; line 72: `_scratch_mount`; line 79: `$XFS_IO_PROG -fc "falloc 0 12k" $f`; line 89: `head -c 5 /dev/zero | tr '\0' X | _fsv_scratch_corrupt_bytes $f 0`; line 96: `$XFS_IO_PROG -fc "pwrite -q -S 0x58 0 12288" $f`; line 109: `$XFS_IO_PROG -fc "pwrite -q -S 0x58 0 192k" $f`; line 113: `$XFS_IO_PROG -fc "pwrite -q -S 0x59 64k 64k" $f`; line 128: `$XFS_IO_PROG -fc "falloc 64k 64k" $f`; line 139: `corrupt_verity_descriptor() {`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick verity prealloc`, install cleanup if needed, enforce requirements, then formats scratch storage, mounts the test filesystem, runs btrfs check or xfstests scratch checks, cycles mounts to force persistence. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. fs-verity state persists in inode items, Merkle tree extents, descriptor items, orphan cleanup, and read-time verification failures. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through xfs_io, btrfs-corrupt-block. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 290 | inl | pread: Input/output error | pread: Input/output error | prealloc | pread: Input/output error | pread: Input/output error | reg | ... (25 expected-output lines total)`.

## Risks and Edge Cases
fs-verity tests intentionally corrupt on-disk items, so mount recovery and error reporting must distinguish expected EIO from metadata damage. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/290 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/291 -->
# sources/test-tools/xfstests/tests/btrfs/291

## Purpose
Test btrfs consistency after each FUA while enabling verity on a file This test works by following the pattern in log-writes/replay-individual.sh: 1. run a workload (verity + sync) while logging to the log device 2. replay an entry to the replay device 3. snapshot the replay device to the snapshot device 4. run destructive tests on the snapshot device (e.g. mount with orphans) 5. goto 2 Override the default cleanup function. In this subset it primarily covers multi-device, RAID, seed/sprout, or device-management paths, fs-verity metadata and recovery behavior, subvolume and snapshot metadata.

## Important APIs, Types, and Functions
The fstest declaration is `auto verity recoveryloop`. Requirement and capability gates: line 36: `_require_scratch`; line 37: `_require_test`; line 38: `_require_loop`; line 39: `_require_log_writes`; line 40: `_require_dm_target snapshot`; line 41: `_require_command $LVM_PROG lvm`; line 42: `_require_scratch_verity`; line 43: `_require_btrfs_command inspect-internal dump-tree`; line 44: `_require_test_program "log-writes/replay-log"`. Local helper surface: `_cleanup()` (line 19), `sync_loop()` (line 47), `dump_tree()` (line 57), `count_item()` (line 62), `count_merkle_items()` (line 68). Important command/API calls include line 16: `_begin_fstest auto verity recoveryloop`; line 22: `_log_writes_cleanup &> /dev/null`; line 26: `rm -f $img`; line 27: `_restore_fsverity_signatures`; line 33: `. ./common/verity`; line 36: `_require_scratch`; line 37: `_require_test`; line 38: `_require_loop`; line 39: `_require_log_writes`; line 40: `_require_dm_target snapshot`; line 41: `_require_command $LVM_PROG lvm`; line 42: `_require_scratch_verity`; line 43: `_require_btrfs_command inspect-internal dump-tree`; line 44: `_require_test_program "log-writes/replay-log"`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto verity recoveryloop`, install cleanup if needed, enforce requirements, then mounts the test filesystem, creates or deletes subvolumes/snapshots, cycles mounts to force persistence. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Snapshot and subvolume roots are deliberate persistent state used to test root items, received UUIDs, cleaner behavior, and metadata references. Multi-device tests allocate scratch pool devices and leave correctness evidence in chunk maps, device registry state, degraded mounts, and btrfs check results. fs-verity state persists in inode items, Merkle tree extents, descriptor items, orphan cleanup, and read-time verification failures. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through btrfs-progs, xfs_io, dm-log-writes. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 291 | Silence is golden`.

## Risks and Edge Cases
device topology tests can expose races in device scan state, degraded mounts, stripe geometry, replacement, and cleanup of scratch device pools; fs-verity tests intentionally corrupt on-disk items, so mount recovery and error reporting must distinguish expected EIO from metadata damage. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/291 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/292 -->
# sources/test-tools/xfstests/tests/btrfs/292

## Purpose
Test btrfs behavior with large chunks (size beyond 4G) for basic read-write and discard. This test focus on RAID0. Make sure each device has at least 2G. Btrfs has a limits on per-device stripe length of 1G. Double that so that we can ensure a RAID0 data chunk with 6G size. We disable async/sync auto discard, so that btrfs won't try to cache the discard result which can cause unexpected skip for some trim range. Fill the data chunk with 5G data. In this subset it primarily covers multi-device, RAID, seed/sprout, or device-management paths, discard/trim behavior.

## Important APIs, Types, and Functions
The fstest declaration is `auto raid volume trim`. Requirement and capability gates: line 16: `_require_scratch_dev_pool 6`; line 17: `_require_fstrim`; line 43: `_require_batched_discard $SCRATCH_MNT`. Local helper surface: no custom shell functions beyond the linear test body. Important command/API calls include line 16: `_require_scratch_dev_pool 6`; line 17: `_require_fstrim`; line 21: `_scratch_dev_pool_get 6`; line 33: `_scratch_dev_pool_put`; line 34: `_notrun "device $i is too small, need at least 2G"`; line 38: `_scratch_pool_mkfs -m raid1 -d raid0 >> $seqres.full 2>&1`; line 42: `_scratch_mount -o nodiscard`; line 43: `_require_batched_discard $SCRATCH_MNT`; line 47: `$XFS_IO_PROG -f -c "pwrite -i /dev/urandom 0 $filesize" $SCRATCH_MNT/file_$i > /dev/null`; line 50: `sync`; line 52: `$BTRFS_UTIL_PROG filesystem df $SCRATCH_MNT >> $seqres.full`; line 54: `_scratch_unmount`; line 57: `$BTRFS_UTIL_PROG check --check-data-csum $SCRATCH_DEV >> $seqres.full 2>&1`; line 65: `rm -rf - "$SCRATCH_MNT/*[02468]"`. It documents fixed kernel commit context at line 18: `_fixed_by_kernel_commit a7299a18a179 \`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto raid volume trim`, install cleanup if needed, enforce requirements, then mounts the test filesystem, runs btrfs check or xfstests scratch checks, cycles mounts to force persistence. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Multi-device tests allocate scratch pool devices and leave correctness evidence in chunk maps, device registry state, degraded mounts, and btrfs check results. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through btrfs-progs, xfs_io, fstrim/discard support. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 292 | Silence is golden`.

## Risks and Edge Cases
device topology tests can expose races in device scan state, degraded mounts, stripe geometry, replacement, and cleanup of scratch device pools; discard tests are sensitive to block-device discard support and whether allocated extents are accidentally punched on replacement devices. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/292 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/293 -->
# sources/test-tools/xfstests/tests/btrfs/293

## Purpose
Test that if we have a subvolume with a non-active swap file, we can not activate it if there are any snapshots. Also test that after all the snapshots are removed, we will be able to activate the swapfile. We deleted the snapshot and committed the transaction used to delete it (-c), but all its extents are actually only deleted in the background, by the cleaner kthread. So remount, which wakes up the cleaner kthread, with a commit interval of 1 second and sleep for 1.1 seconds - after this we are guaranteed all extents of the snapshot were deleted. No more snapshots, we should be able to activate the swap file. In this subset it primarily covers multi-device, RAID, seed/sprout, or device-management paths, swapfile activation restrictions, mount and remount option semantics, subvolume and snapshot metadata.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick swap snapshot remount`. Requirement and capability gates: line 25: `_require_scratch_swapfile`. Local helper surface: `_cleanup()` (line 14). Important command/API calls include line 12: `_begin_fstest auto quick swap snapshot remount`; line 27: `_scratch_mkfs >> $seqres.full 2>&1`; line 28: `_scratch_mount`; line 33: `echo "Creating first snapshot..."`; line 34: `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/snap1`; line 35: `echo "Creating second snapshot..."`; line 36: `_btrfs subvolume snapshot $SCRATCH_MNT $SCRATCH_MNT/snap2`; line 38: `echo "Activating swap file... (should fail due to snapshots)"`; line 39: `_swapon_file $swap_file 2>&1 | _filter_scratch`; line 41: `echo "Deleting first snapshot..."`; line 42: `$BTRFS_UTIL_PROG subvolume delete -c $SCRATCH_MNT/snap1 | _filter_btrfs_subvol_delete`; line 49: `echo "Remounting and waiting for cleaner thread to remove the first snapshot..."`; line 53: `echo "Activating swap file... (should fail due to snapshot)"`; line 56: `echo "Deleting second snapshot..."`. It documents fixed kernel commit context at line 23: `_fixed_by_kernel_commit deccae40e4b3 \`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick swap snapshot remount`, install cleanup if needed, enforce requirements, then formats scratch storage, mounts the test filesystem, creates or deletes subvolumes/snapshots. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Snapshot and subvolume roots are deliberate persistent state used to test root items, received UUIDs, cleaner behavior, and metadata references. Swapfile state is persistent inode extent state plus runtime swapon/swapoff activation status. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through btrfs-progs, swap tools. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 293 | Creating first snapshot... | Creating second snapshot... | Activating swap file... (should fail due to snapshots) | swapon: SCRATCH_MNT/swapfile: swapon failed: Invalid argument | Deleting first snapshot... | Delete subvolume 'SCRATCH_MNT/snap1' | Remounting and waiting for cleaner thread to remove the first snapshot... | ... (15 expected-output lines total)`.

## Risks and Edge Cases
swapfile tests rely on cleaner thread and remount commit timing after snapshot deletion. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/293 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/294 -->
# sources/test-tools/xfstests/tests/btrfs/294

## Purpose
Test btrfs write behavior with large RAID56 chunks (size beyond 4G). No zoned support for RAID56 yet. Make sure each device has at least 2G. Btrfs has a limits on per-device stripe length of 1G. Double that so that we can ensure a RAID6 data chunk with 6G size. success, all done. In this subset it primarily covers multi-device, RAID, seed/sprout, or device-management paths.

## Important APIs, Types, and Functions
The fstest declaration is `auto raid volume`. Requirement and capability gates: line 16: `_require_non_zoned_device "${SCRATCH_DEV}"`; line 18: `_require_scratch_dev_pool 8`. Local helper surface: `workload()` (line 29). Important command/API calls include line 16: `_require_non_zoned_device "${SCRATCH_DEV}"`; line 18: `_require_scratch_dev_pool 8`; line 24: `_scratch_dev_pool_get 8`; line 33: `_scratch_pool_mkfs -m raid1 -d $data_profile >> $seqres.full 2>&1`; line 34: `_scratch_mount`; line 35: `$XFS_IO_PROG -f -c "pwrite -b 1m 0 $datasize" $SCRATCH_MNT/foobar > /dev/null`; line 38: `sync`; line 41: `$BTRFS_UTIL_PROG filesystem df $SCRATCH_MNT >> $seqres.full`; line 42: `_scratch_unmount`; line 45: `$BTRFS_UTIL_PROG check --check-data-csum $SCRATCH_DEV >> $seqres.full 2>&1`; line 47: `_scratch_dev_pool_put`; line 59: `_notrun "device $i is too small, need at least 2G"`. It documents fixed kernel commit context at line 19: `_fixed_by_kernel_commit a7299a18a179 \`. It documents fixed kernel commit context at line 21: `_fixed_by_kernel_commit cb091225a538 \`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto raid volume`, install cleanup if needed, enforce requirements, then mounts the test filesystem, runs btrfs check or xfstests scratch checks, cycles mounts to force persistence. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Multi-device tests allocate scratch pool devices and leave correctness evidence in chunk maps, device registry state, degraded mounts, and btrfs check results. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through btrfs-progs, xfs_io. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 294 | Silence is golden`.

## Risks and Edge Cases
device topology tests can expose races in device scan state, degraded mounts, stripe geometry, replacement, and cleanup of scratch device pools. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/294 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/295 -->
# sources/test-tools/xfstests/tests/btrfs/295

## Purpose
Make sure btrfs handles critical errors gracefully during mount. Directly writing to the device, which may not work with a zoned device Use single metadata profile so we only need to corrupt one copy of tree block mount may lead to crash Re-create the fs to avoid false alert from the corrupted fs. success, all done. In this subset it primarily covers multi-device, RAID, seed/sprout, or device-management paths.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick dangerous`. Requirement and capability gates: line 13: `_require_scratch`; line 15: `_require_non_zoned_device "$SCRATCH_DEV"`. Local helper surface: no custom shell functions beyond the linear test body. Important command/API calls include line 13: `_require_scratch`; line 15: `_require_non_zoned_device "$SCRATCH_DEV"`; line 18: `_scratch_mkfs -m single > $seqres.full`; line 20: `logical_root=$($BTRFS_UTIL_PROG inspect dump-tree -t root "$SCRATCH_DEV" | grep leaf | head -n1 | cut -f2 -d\ )`; line 22: `physical_root=$(_btrfs_get_physical $logical_root 1)`; line 30: `_try_scratch_mount >> $seqres.full 2>&1`; line 35: `_scratch_mkfs -m single >> $seqres.full`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick dangerous`, install cleanup if needed, enforce requirements, then formats scratch storage, mounts the test filesystem. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Multi-device tests allocate scratch pool devices and leave correctness evidence in chunk maps, device registry state, degraded mounts, and btrfs check results. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through btrfs-progs. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 295 | Silence is golden`.

## Risks and Edge Cases
device topology tests can expose races in device scan state, degraded mounts, stripe geometry, replacement, and cleanup of scratch device pools. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/295 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/296 -->
# sources/test-tools/xfstests/tests/btrfs/296

## Purpose
Make sure that per-fs features sysfs interface get properly updated when a new feature is added. We need the global features support Make sure we have support RAID1C34 first Go the very basic profile first, so that even older progs can support it. First we need per-fs features directory Make sure the per-fs features doesn't include raid1c34 Balance to RAID1C3 Sync before checking for sysfs update during cleaner_kthread(). In this subset it primarily covers multi-device, RAID, seed/sprout, or device-management paths.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick balance raid`. Requirement and capability gates: line 13: `_require_scratch_dev_pool 3`; line 18: `_require_btrfs_fs_sysfs`. Local helper surface: no custom shell functions beyond the linear test body. Important command/API calls include line 11: `_begin_fstest auto quick balance raid`; line 13: `_require_scratch_dev_pool 3`; line 14: `_fixed_by_kernel_commit b7625f461da6 "btrfs: sysfs: update fs features directory asynchronously"`; line 18: `_require_btrfs_fs_sysfs`; line 26: `_scratch_dev_pool_get 3`; line 29: `_scratch_pool_mkfs -m dup -d single >> $seqres.full 2>&1`; line 31: `_scratch_mount`; line 46: `$BTRFS_UTIL_PROG balance start -mconvert=raid1c3 "$SCRATCH_MNT" >> $seqres.full`; line 49: `sync`; line 59: `_scratch_unmount`; line 60: `_scratch_dev_pool_put`. It documents fixed kernel commit context at line 14: `_fixed_by_kernel_commit b7625f461da6 \`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick balance raid`, install cleanup if needed, enforce requirements, then mounts the test filesystem, cycles mounts to force persistence. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Multi-device tests allocate scratch pool devices and leave correctness evidence in chunk maps, device registry state, degraded mounts, and btrfs check results. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through btrfs-progs. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 296 | Silence is golden`.

## Risks and Edge Cases
device topology tests can expose races in device scan state, degraded mounts, stripe geometry, replacement, and cleanup of scratch device pools. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/296 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/297 -->
# sources/test-tools/xfstests/tests/btrfs/297

## Purpose
Make sure btrfs scrub can fix parity stripe corruption We need to ensure a fixed extent size and we corrupt by writing directly to the device, so skip if compression is enabled. If neither raid5 or raid6 are supported do _notrun. In this subset it primarily covers multi-device, RAID, seed/sprout, or device-management paths, scrub detection and repair paths.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick raid scrub`. Requirement and capability gates: line 14: `_require_odirect`; line 15: `_require_non_zoned_device "${SCRATCH_DEV}"`; line 16: `_require_scratch_dev_pool 3`; line 19: `_require_no_compress`. Local helper surface: `workload()` (line 29). Important command/API calls include line 10: `_begin_fstest auto quick raid scrub`; line 15: `_require_non_zoned_device "${SCRATCH_DEV}"`; line 21: `_fixed_by_kernel_commit 486c737f7fdc "btrfs: raid56: always verify the P/Q contents for scrub"`; line 25: `if ! _check_btrfs_raid_type raid5 && ! _check_btrfs_raid_type raid6; then`; line 34: `if ! _check_btrfs_raid_type $profile; then`; line 39: `echo "=== Testing $nr_devs devices $profile ===" >> $seqres.full`; line 45: `_scratch_mount -o space_cache=v2`; line 48: `$XFS_IO_PROG -f -d -c "pwrite -S 0xaa -b 64K 0 64K" "$SCRATCH_MNT/foobar" > /dev/null`; line 57: `devpath_p=$(_btrfs_get_device_path ${logical} 2)`; line 63: `$XFS_IO_PROG -d -c "pwrite -S 0xff -b 64K $physical_p 64K" $devpath_p > /dev/null`; line 68: `$BTRFS_UTIL_PROG scrub start -BdR $SCRATCH_MNT >> $seqres.full 2>&1`; line 75: `echo "The first 16 bytes of parity stripe after scrub:" >> $seqres.full`; line 86: `$BTRFS_UTIL_PROG check --check-data-csum $SCRATCH_DEV >> $seqres.full 2>&1`; line 88: `echo "Error detected after the scrub"`. It documents fixed kernel commit context at line 21: `_fixed_by_kernel_commit 486c737f7fdc \`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick raid scrub`, install cleanup if needed, enforce requirements, then mounts the test filesystem, runs scrub or checks scrub reports, runs btrfs check or xfstests scratch checks, cycles mounts to force persistence. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Multi-device tests allocate scratch pool devices and leave correctness evidence in chunk maps, device registry state, degraded mounts, and btrfs check results. Corruption is injected below the filesystem and then validated after scrub, remount, or direct device reads. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through btrfs-progs, xfs_io. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 297 | Silence is golden`.

## Risks and Edge Cases
device topology tests can expose races in device scan state, degraded mounts, stripe geometry, replacement, and cleanup of scratch device pools; scrub repair signals depend on precise logical-to-physical mapping and can miss corruption if checksum, parity, or duplicate-copy selection regresses. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/297 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/298 -->
# sources/test-tools/xfstests/tests/btrfs/298

## Purpose
Check if the device scan registers for a single-device seed and drops it from the kernel if it is eventually marked as non-seed. success, all done. In this subset it primarily covers multi-device, RAID, seed/sprout, or device-management paths.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick seed`. Requirement and capability gates: line 13: `_require_command "$BTRFS_TUNE_PROG" btrfstune`; line 14: `_require_command "$WIPEFS_PROG" wipefs`; line 15: `_require_scratch_dev_pool 2`. Local helper surface: no custom shell functions beyond the linear test body. Important command/API calls include line 13: `_require_command "$BTRFS_TUNE_PROG" btrfstune`; line 14: `_require_command "$WIPEFS_PROG" wipefs`; line 15: `_require_scratch_dev_pool 2`; line 16: `_scratch_dev_pool_get 1`; line 22: `echo "#setup seed sprout device" >> $seqres.full`; line 23: `_scratch_mkfs "-b 300M" >> $seqres.full 2>&1 || _fail "Fail to make SCRATCH_DEV with -b 300M"`; line 25: `$BTRFS_TUNE_PROG -S 1 $SCRATCH_DEV`; line 26: `_scratch_mount >> $seqres.full 2>&1`; line 27: `$BTRFS_UTIL_PROG device add $SPARE_DEV $SCRATCH_MNT >> $seqres.full`; line 28: `_scratch_unmount`; line 29: `$BTRFS_UTIL_PROG device scan --forget`; line 31: `echo "#Scan seed device and check using mount" >> $seqres.full`; line 32: `$BTRFS_UTIL_PROG device scan $SCRATCH_DEV >> $seqres.full`; line 33: `_mount $SPARE_DEV $SCRATCH_MNT`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick seed`, install cleanup if needed, enforce requirements, then formats scratch storage, mounts the test filesystem, runs btrfs check or xfstests scratch checks, cycles mounts to force persistence. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Multi-device tests allocate scratch pool devices and leave correctness evidence in chunk maps, device registry state, degraded mounts, and btrfs check results. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through btrfs-progs, btrfstune. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 298 | Silence is golden`.

## Risks and Edge Cases
device topology tests can expose races in device scan state, degraded mounts, stripe geometry, replacement, and cleanup of scratch device pools. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/298 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/299 -->
# sources/test-tools/xfstests/tests/btrfs/299

## Purpose
Given a file with extents: [0 : 4096) (inline) [4096 : N] (prealloc) if a user uses the ioctl BTRFS_IOC_LOGICAL_INO[_V2] asking for the file of the non-inline extent, it results in reading the offset field of the inline extent, which is meaningless (it is full of user data..). If we are particularly lucky, it can be past the end of the extent buffer, resulting in a crash. This test creates that circumstance and asserts that logical inode resolution is still successful. In this subset it primarily covers logical-to-inode extent resolution.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick preallocrw logical_resolve`. Requirement and capability gates: line 20: `_require_scratch`; line 21: `_require_xfs_io_command "falloc" "-k"`; line 22: `_require_btrfs_command inspect-internal logical-resolve`; line 25: `_require_btrfs_no_nodatacow`. Local helper surface: no custom shell functions beyond the linear test body. Important command/API calls include line 20: `_require_scratch`; line 21: `_require_xfs_io_command "falloc" "-k"`; line 22: `_require_btrfs_command inspect-internal logical-resolve`; line 25: `_require_btrfs_no_nodatacow`; line 44: `_scratch_mkfs "--nodesize 64k" >> $seqres.full || _fail "mkfs failed"`; line 45: `_scratch_mount`; line 51: `$XFS_IO_PROG -fc "pwrite -q 0 1024" $f.inl.$i`; line 55: `$XFS_IO_PROG -fc "pwrite -q 0 1" $f.inl-var.$i`; line 58: `$XFS_IO_PROG -fc "falloc -k 0 1m" $f.evil`; line 59: `$XFS_IO_PROG -fc fsync $f.evil`; line 64: `$XFS_IO_PROG -fc "pwrite -q 0 1024" $f.inl.2.$i`; line 69: `logical=$(_btrfs_get_file_extent_item_bytenr $f.evil 0)`; line 75: `$XFS_IO_PROG -fc "pwrite -q 0 23" $f.evil`; line 81: `sync`. It documents fixed kernel commit context at line 26: `_fixed_by_kernel_commit 560840afc3e6 \`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick preallocrw logical_resolve`, install cleanup if needed, enforce requirements, then formats scratch storage, mounts the test filesystem. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through xfs_io. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 299 | Silence is golden`.

## Risks and Edge Cases
the main risk is silent metadata or persistence regression that only appears after remount, receive, check, or explicit content comparison. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/299 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/300 -->
# sources/test-tools/xfstests/tests/btrfs/300

## Purpose
Validate that snapshots taken while in a remapped namespace preserve the permissions of the user. _user_do executes each command as $qa_user in its own subshell. unshare sets the namespace for the running shell. The test must run in one user subshell to preserve the namespace over multiple commands. In this subset it primarily covers subvolume and snapshot metadata.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick subvol snapshot`. Requirement and capability gates: line 18: `_require_test`; line 19: `_require_user`; line 20: `_require_group`; line 21: `_require_unix_perm_checking`; line 22: `_require_unshare --keep-caps --map-auto --map-root-user`. Local helper surface: `cleanup()` (line 25). Important command/API calls include line 12: `_begin_fstest auto quick subvol snapshot`; line 15: `_fixed_by_kernel_commit 94628ad94408 "btrfs: copy dir permission and time when creating a stub subvolume"`; line 18: `_require_test`; line 19: `_require_user`; line 20: `_require_group`; line 21: `_require_unix_perm_checking`; line 22: `_require_unshare --keep-caps --map-auto --map-root-user`; line 26: `rm -rf $test_dir`; line 28: `rm -rf $tmp.*`; line 32: `mkdir $test_dir`; line 41: `unshare --user --keep-caps --map-auto --map-root-user;`; line 42: `$BTRFS_UTIL_PROG subvolume create subvol;`; line 43: `touch subvol/{1,2,3};`; line 44: `$BTRFS_UTIL_PROG subvolume create subvol/subsubvol;`. It documents fixed kernel commit context at line 15: `_fixed_by_kernel_commit 94628ad94408 \`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick subvol snapshot`, install cleanup if needed, enforce requirements, then creates or deletes subvolumes/snapshots, runs btrfs check or xfstests scratch checks. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Snapshot and subvolume roots are deliberate persistent state used to test root items, received UUIDs, cleaner behavior, and metadata references. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through btrfs-progs, user namespace support. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 300 | Create subvolume './subvol' | Create subvolume 'subvol/subsubvol' | drwxr-xr-x fsgqa fsgqa ./ | drwxr-xr-x fsgqa fsgqa ./subvol | -rw-r--r-- fsgqa fsgqa ./subvol/1 | -rw-r--r-- fsgqa fsgqa ./subvol/2 | -rw-r--r-- fsgqa fsgqa ./subvol/3 | ... (17 expected-output lines total)`.

## Risks and Edge Cases
the main risk is silent metadata or persistence regression that only appears after remount, receive, check, or explicit content comparison. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/300 -->
