# Research Group subset-b-009555

This grouped report covers XFS xfstests shell tests 441-538 and 540-602. Each section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/441 -->
# sources/test-tools/xfstests/tests/xfs/441

## Purpose

Regression test for a quota accounting bug when reflinking across EOF of a file in which we forgot dq_attach. This file exercises quota accounting or quota scrub behavior on XFS. It combines scratch quota mount options with block usage, reflink, CoW, or stress operations and compares kernel accounting to user-visible reports.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto quick clone quota` and imports common modules: `preamble`, `reflink`, `quota`, `filter`. Local helper functions: `check_quota`. Key environment variables or shell state names include `du_total`, `qu_total`.

Requirements and feature gates: `_require_quota`, `_require_scratch_reflink`, `_require_cp_reflink`, `_require_user`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_mkfs > "$seqres.full" 2>&1`, `_scratch_mount "-o noquota" >> $seqres.full 2>&1`, `_scratch_unmount`, `_scratch_mount "-o usrquota,grpquota" >> "$seqres.full" 2>&1`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is common/quota, xfs_quota reports, repquota-compatible VFS quota checks, scratch remounts, and any reflink or fsstress helpers used to generate accounting pressure. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is delayed accounting and preallocation state; tests often sync, remount, or force quotacheck so speculative CoW reservations do not look like real regressions. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 441`; `Format and mount (noquota)`; `Create files`; `repquota: Mountpoint (or device) SCRATCH_MNT not found or has no quota enabled.`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/441 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/442 -->
# sources/test-tools/xfstests/tests/xfs/442

## Purpose

Force enable all XFS quotas, run fsstress until the fs runs out of space, and make sure the quotas are still correct when we're done. This is a general regression/stress test for numerous quota bugs with reflink and copy on write. This file exercises quota accounting or quota scrub behavior on XFS. It combines scratch quota mount options with block usage, reflink, CoW, or stress operations and compares kernel accounting to user-visible reports.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto stress clone quota` and imports common modules: `preamble`, `quota`, `filter`, `reflink`. Local helper functions: `check_quota_du_blocks`, `compare_quota_to_du`, `report_quota_blocks`. Key environment variables or shell state names include `du_rep`, `g_rep`, `nr_cpus`, `nr_ops`, `p_rep`, `u_rep`.

Requirements and feature gates: `_require_scratch_reflink`, `_require_quota`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `$XFS_QUOTA_PROG -x -c "report $1" $SCRATCH_MNT | \`, `_scratch_sync`, `echo "Format and fsstress"`, `_scratch_mkfs_sized $((1600 * 1048576)) > $seqres.full 2>&1`, `_scratch_mount >> $seqres.full 2>&1`, `_run_fsstress -w -d $SCRATCH_MNT -n $nr_ops -p $nr_cpus`, `_scratch_unmount`, `_scratch_mount`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is common/quota, xfs_quota reports, repquota-compatible VFS quota checks, scratch remounts, and any reflink or fsstress helpers used to generate accounting pressure. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is delayed accounting and preallocation state; tests often sync, remount, or force quotacheck so speculative CoW reservations do not look like real regressions. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 442`; `Format and fsstress`; `Check quota before remount`; `Check quota after remount`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/442 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/443 -->
# sources/test-tools/xfstests/tests/xfs/443

## Purpose

Regression test for the XFS rmapbt based extent swap algorithm. The extent swap algorithm for rmapbt=1 filesystems unmaps/remaps individual extents to rectify the rmapbt for each extent swapped between inodes. If one of the inodes happens to straddle the extent <-> btree format boundary (which can vary depending on inode size), the unmap/remap sequence can bounce the inodes back and forth between formats many times during the swap. Since extent -> btree format conversion requires a block allocation, this can consume more blocks than expected, lead to block reservation overrun and free space accounting inconsistency. This is a focused xfstests shell regression. It encodes an XFS behavior, userspace-tool contract, or maintenance check as a scratch/test filesystem scenario.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto quick ioctl fsr punch fiemap prealloc` and imports common modules: `preamble`, `filter`, `punch`. Local helper functions: none Key environment variables or shell state names include `file1`, `file2`, `file_blksz`.

Requirements and feature gates: `_require_scratch`, `_require_test_program "punch-alternating"`, `_require_xfs_io_command "falloc"`, `_require_xfs_io_command "fpunch"`, `_require_xfs_io_command "exchangerange"`, `_require_xfs_io_command "fiemap"`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_mkfs | _filter_mkfs >> $seqres.full 2> $tmp.mkfs`, `_scratch_mount`, `$XFS_IO_PROG -fc "falloc 0 $((400 * file_blksz))" $file1`, `$here/src/punch-alternating $file1`, `$XFS_IO_PROG -fc "falloc 0 $((400 * file_blksz))" $file2`, `$here/src/punch-alternating $file2`, `$XFS_IO_PROG -c "fpunch $((i * file_blksz)) $file_blksz" $file2`, `$XFS_IO_PROG -c "exchangerange $file2" $file1`; plus 2 more.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is the xfstests common harness, scratch filesystem lifecycle helpers, xfsprogs commands, and golden-output filtering through `seqres.full` and `.out` files. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is environment sensitivity: missing xfsprogs features, kernel feature flags, scratch geometry, runtime load, or non-normalized diagnostics can produce false failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 443`; `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/443 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/444 -->
# sources/test-tools/xfstests/tests/xfs/444

## Purpose

Make sure XFS can fix a v5 AGFL that wraps over the last block. Refer to commit 96f859d52bcb ("libxfs: pack the agfl header structure so XFS_AGFL_SIZE is correct") for details on the original on-disk format error and the patch "xfs: detect agfl count corruption and reset agfl") for details about the fix. This is a focused xfstests shell regression. It encodes an XFS behavior, userspace-tool contract, or maintenance check as a scratch/test filesystem scenario.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto quick prealloc` and imports common modules: `preamble`, `filter`. Local helper functions: `dump_ag0`, `filter_agfl_reset_printk`, `mount_loop`, `runtest`. Key environment variables or shell state names include `agfl_size`, `bad_agfl_size`, `blksz`, `bno`, `bno_maxrecs`, `cmd`, `dest_pos`, `filesz`, `flcount`, `flfirst`; plus 6 more.

Requirements and feature gates: `_require_check_dmesg`, `_require_scratch`, `_require_test_program "punch-alternating"`, `_require_xfs_io_command "falloc"`, `_require_xfs_db_write_array`, `_require_scratch_xfs_crc`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `if ! _try_scratch_mount >> $seqres.full 2>&1; then`, `$XFS_IO_PROG -f -c "falloc 0 $filesz" $SCRATCH_MNT/a >> $seqres.full 2>&1`, `test -e $SCRATCH_MNT/a && $here/src/punch-alternating $SCRATCH_MNT/a`, `_scratch_unmount 2>&1 | _filter_scratch`, `_scratch_xfs_db -c 'sb 0' -c 'p' -c 'agf 0' -c 'p' -c 'agfl 0' -c 'p'`, `_scratch_mkfs >> $seqres.full`, `sectsize=$(_scratch_xfs_get_metadata_field "sectsize" "sb 0")`, `flfirst=$(_scratch_xfs_get_metadata_field "flfirst" "agf 0")`; plus 9 more.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is the xfstests common harness, scratch filesystem lifecycle helpers, xfsprogs commands, and golden-output filtering through `seqres.full` and `.out` files. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is environment sensitivity: missing xfsprogs features, kernel feature flags, scratch geometry, runtime load, or non-normalized diagnostics can produce false failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 444`; `TEST fix_end`; `TEST fix_start`; `TEST fix_wrap`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/444 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/445 -->
# sources/test-tools/xfstests/tests/xfs/445

## Purpose

Test the XFS filestreams allocator for use-after-free inode access. The filestreams allocator uses the MRU and historically kept around unreferenced inode pointers in each element. These pointers could outlive the inodes they referred to and thus lead to access of freed or reused memory when the MRU element was reaped. Test for this problem by performing filestream allocations against short-lived parent directory inodes. Note that some form of kernel debug mechanism for use-after-free detection (i.e., KASAN) is required for this test to reproduce the original problem. This is because XFS uses a kmem cache for xfs_inode objects which means that the backing pages for freed inodes may still reside in the cache with the freed inodes in a partially initialized state. This is a focused xfstests shell regression. It encodes an XFS behavior, userspace-tool contract, or maintenance check as a scratch/test filesystem scenario.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto quick filestreams prealloc` and imports common modules: `preamble`, `filter`, `filestreams`. Local helper functions: `drop_caches`. Key environment variables or shell state names include `dir`, `pid`.

Requirements and feature gates: `_require_scratch_size $((2*1024*1024)) # kb`, `_require_xfs_io_command "falloc"`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_mkfs_xfs -d agsize=20m,size=2g >> $seqres.full 2>&1`, `_scratch_mount "-o filestreams"`, `$XFS_IO_PROG -fc "falloc $(($i * 20))m 20m" $dir/$i/file`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is the xfstests common harness, scratch filesystem lifecycle helpers, xfsprogs commands, and golden-output filtering through `seqres.full` and `.out` files. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is environment sensitivity: missing xfsprogs features, kernel feature flags, scratch geometry, runtime load, or non-normalized diagnostics can produce false failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 445`; `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/445 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/446 -->
# sources/test-tools/xfstests/tests/xfs/446

## Purpose

checkbashisms on all /bin/sh scripts.  This is a maintainer script. This is a focused xfstests shell regression. It encodes an XFS behavior, userspace-tool contract, or maintenance check as a scratch/test filesystem scenario.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto quick` and imports common modules: `preamble`. Local helper functions: none Key environment variables or shell state names include only standard xfstests variables such as `SCRATCH_MNT`, `SCRATCH_DEV`, `seqres`, and `tmp` are used

Requirements and feature gates: `_require_command "$CHECKBASHISMS_PROG" checkbashisms`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: The command flow is primarily ordinary shell setup and harness completion.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is the xfstests common harness, scratch filesystem lifecycle helpers, xfsprogs commands, and golden-output filtering through `seqres.full` and `.out` files. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is environment sensitivity: missing xfsprogs features, kernel feature flags, scratch geometry, runtime load, or non-normalized diagnostics can produce false failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 446`; `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/446 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/447 -->
# sources/test-tools/xfstests/tests/xfs/447

## Purpose

Exercise mount vs superblock shrinker races. This is a focused xfstests shell regression. It encodes an XFS behavior, userspace-tool contract, or maintenance check as a scratch/test filesystem scenario.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto mount` and imports common modules: `preamble`, `filter`. Local helper functions: `_cleanup`. Key environment variables or shell state names include only standard xfstests variables such as `SCRATCH_MNT`, `SCRATCH_DEV`, `seqres`, and `tmp` are used

Requirements and feature gates: `_require_scratch`, `_require_xfs_sysfs debug/mount_delay`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_mkfs > $seqres.full 2>&1`, `_scratch_mount`, `$XFS_IO_PROG -fxc "pwrite 0 4k" -c fsync \`, `_scratch_unmount`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is the xfstests common harness, scratch filesystem lifecycle helpers, xfsprogs commands, and golden-output filtering through `seqres.full` and `.out` files. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is environment sensitivity: missing xfsprogs features, kernel feature flags, scratch geometry, runtime load, or non-normalized diagnostics can produce false failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 447`; `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/447 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/448 -->
# sources/test-tools/xfstests/tests/xfs/448

## Purpose

Regression test for commit: 46c59736d809 ("xfs: harden directory integrity checks some more") If a malicious XFS contains a block+ format directory wherein the directory inode's core.mode is corrupted, and there are subdirectories of the corrupted directory, an attempt to traverse up the directory tree by running xfs_scrub will crash the kernel in __xfs_dir3_data_check. This file is a targeted corruption regression. It creates a scratch filesystem, mutates a precise XFS metadata field or structure, and then relies on mount, scrub, repair, or verifier behavior to prove the bug stays fixed.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto quick fuzzers` and imports common modules: `preamble`, `filter`, `populate`. Local helper functions: none Key environment variables or shell state names include `dino`, `getmode`, `setmode`, `subdgen`, `subdino`.

Requirements and feature gates: `_require_scratch_nocheck`, `_require_xfs_io_command "scrub"`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_mkfs | _filter_mkfs > $seqres.full 2> $tmp.mkfs`, `_scratch_mount`, `_scratch_unmount`, `subdgen=$(_scratch_xfs_get_metadata_field "core.gen" "inode $subdino")`, `_scratch_xfs_set_metadata_field "core.mode" "$setmode" "inode $dino" >> $seqres.full`, `getmode=$(_scratch_xfs_get_metadata_field "core.mode" "inode $dino")`, `$XFS_IO_PROG -x -c "scrub parent $subdino $subdgen" ${SCRATCH_MNT} >> $seqres.full`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is xfs_db metadata reads/writes, common/fuzzy helpers, scratch mount cycles, and xfstests filters that normalize expected diagnostics. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is tight coupling to on-disk format details; feature gates, block-size calculations, and expected verifier messages must track XFS format changes. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 448`; `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/448 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/449 -->
# sources/test-tools/xfstests/tests/xfs/449

## Purpose

Make sure pretty printed XFS geometry is the same across all programs. This is a focused xfstests shell regression. It encodes an XFS behavior, userspace-tool contract, or maintenance check as a scratch/test filesystem scenario.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto quick` and imports common modules: `preamble`, `filter`. Local helper functions: none Key environment variables or shell state names include only standard xfstests variables such as `SCRATCH_MNT`, `SCRATCH_DEV`, `seqres`, and `tmp` are used

Requirements and feature gates: `_require_scratch_nocheck`, `_require_xfs_spaceman_command "info"`, `_require_command "$XFS_GROWFS_PROG" xfs_growfs`, `_require_xfs_scratch_non_zoned`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_mkfs | sed -e '/Discarding/d' -e '/deprecated/d' > $tmp.mkfs`, `_scratch_xfs_db -c "info" > $tmp.dbinfo`, `if $XFS_DB_PROG --help 2>&1 | grep -q -- '-R rtdev'; then`, `_scratch_mount`, `$XFS_SPACEMAN_PROG -c "info" $SCRATCH_MNT > $tmp.spaceman`, `$XFS_GROWFS_PROG -n $SCRATCH_MNT > $tmp.growfs`, `$XFS_INFO_PROG $SCRATCH_MNT > $tmp.info.mnt`, `$XFS_INFO_PROG $SCRATCH_DEV > $tmp.info.dev`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is the xfstests common harness, scratch filesystem lifecycle helpers, xfsprogs commands, and golden-output filtering through `seqres.full` and `.out` files. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is environment sensitivity: missing xfsprogs features, kernel feature flags, scratch geometry, runtime load, or non-normalized diagnostics can produce false failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 449`; `Silence is golden.`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/449 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/450 -->
# sources/test-tools/xfstests/tests/xfs/450

## Purpose

Make sure that the statfs b_avail counter doesn't change across remount after the rmapbt has grown in size. This is a focused xfstests shell regression. It encodes an XFS behavior, userspace-tool contract, or maintenance check as a scratch/test filesystem scenario.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto quick rmap prealloc` and imports common modules: `preamble`, `filter`. Local helper functions: none Key environment variables or shell state names include `after`, `before`, `blks`, `blksz`, `nr_rmap_per_rmapbt`.

Requirements and feature gates: `_require_xfs_io_command "falloc"`, `_require_test_program "punch-alternating"`, `_require_xfs_scratch_rmapbt`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_mkfs >> $seqres.full`, `_scratch_mount`, `$XFS_IO_PROG -f -c "falloc 0 $((blks * blksz))" $SCRATCH_MNT/a >> $seqres.full`, `$here/src/punch-alternating $SCRATCH_MNT/a`, `_scratch_cycle_mount`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is the xfstests common harness, scratch filesystem lifecycle helpers, xfsprogs commands, and golden-output filtering through `seqres.full` and `.out` files. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is environment sensitivity: missing xfsprogs features, kernel feature flags, scratch geometry, runtime load, or non-normalized diagnostics can produce false failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 450`; `Silence is golden.`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/450 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/451 -->
# sources/test-tools/xfstests/tests/xfs/451

## Purpose

Make sure xfs_repair can repair root inode parent's pointer when it contains a bogus ino when it's using shot form directory This is a focused xfstests shell regression. It encodes an XFS behavior, userspace-tool contract, or maintenance check as a scratch/test filesystem scenario.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto quick metadata repair` and imports common modules: `preamble`, `filter`. Local helper functions: none Key environment variables or shell state names include `prefix`, `rootino`.

Requirements and feature gates: `_require_scratch`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_mkfs >> /dev/null 2>&1`, `rootino=$(_scratch_xfs_get_metadata_field 'rootino' 'sb 0')`, `prefix=$(_scratch_get_sfdir_prefix ${rootino} || \`, `_scratch_xfs_set_metadata_field "${prefix}.hdr.parent.i4" 0 "inode ${rootino}"\`, `_scratch_xfs_repair >> $seqres.full 2>&1`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is the xfstests common harness, scratch filesystem lifecycle helpers, xfsprogs commands, and golden-output filtering through `seqres.full` and `.out` files. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is environment sensitivity: missing xfsprogs features, kernel feature flags, scratch geometry, runtime load, or non-normalized diagnostics can produce false failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 451`; `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/451 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/452 -->
# sources/test-tools/xfstests/tests/xfs/452

## Purpose

Test xfs_db by bad character in field list selector string. The issue has been fixed by xfsprogs 945e47e2. This is a focused xfstests shell regression. It encodes an XFS behavior, userspace-tool contract, or maintenance check as a scratch/test filesystem scenario.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto db` and imports common modules: `preamble`, `filter`. Local helper functions: none Key environment variables or shell state names include `inum`.

Requirements and feature gates: `_require_scratch`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_mkfs_xfs >> $seqres.full 2>&1`, `inum=`_scratch_xfs_get_metadata_field rootino "sb 0"``, `_scratch_xfs_db -c "inode $inum" -c "print core.*"`, `_scratch_xfs_db -c "inode $inum" -c "print core.\\"`, `_scratch_xfs_db -c "inode $inum" -c "print core.\""`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is the xfstests common harness, scratch filesystem lifecycle helpers, xfsprogs commands, and golden-output filtering through `seqres.full` and `.out` files. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is environment sensitivity: missing xfsprogs features, kernel feature flags, scratch geometry, runtime load, or non-normalized diagnostics can produce false failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 452`; `= check bad character * =`; `bad character in field *`; `= check bad character trailing slash =`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/452 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/453 -->
# sources/test-tools/xfstests/tests/xfs/453

## Purpose

Populate a XFS filesystem and fuzz every superblock field. Do not fix the filesystem, to test metadata verifiers. This file belongs to the XFS metadata fuzzing block. It uses populated scratch filesystems and common/fuzzy helpers to mutate a specific on-disk structure, then deliberately exercises verifier behavior with the repair mode encoded in its tags and `_scratch_xfs_fuzz_metadata` arguments.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest dangerous_fuzzers fuzzers_norepair` and imports common modules: `preamble`, `filter`, `populate`, `fuzzy`. Local helper functions: none Key environment variables or shell state names include only standard xfstests variables such as `SCRATCH_MNT`, `SCRATCH_DEV`, `seqres`, and `tmp` are used

Requirements and feature gates: `_require_scratch_xfs_fuzz_fields`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_populate_cached nofill > $seqres.full 2>&1`, `_scratch_xfs_fuzz_metadata '' 'none' 'sb 1' >> $seqres.full`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The important integration surface is xfs_db-driven metadata addressing, cached population images, mount or scrub/repair validation, and the xfstests dangerous_fuzzers gating that keeps destructive corruption tests out of ordinary quick runs. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The main risk is that target metadata layout assumptions can drift as XFS formats evolve; skips and feature requirements must remain accurate so the test corrupts the intended structure instead of producing unrelated mount, xfs_db, or repair failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 453`; `Format and populate`; `Fuzz superblock`; `Done fuzzing superblock`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/453 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/454 -->
# sources/test-tools/xfstests/tests/xfs/454

## Purpose

Populate a XFS filesystem and fuzz every AGF field. Do not fix the filesystem, to test metadata verifiers. This file belongs to the XFS metadata fuzzing block. It uses populated scratch filesystems and common/fuzzy helpers to mutate a specific on-disk structure, then deliberately exercises verifier behavior with the repair mode encoded in its tags and `_scratch_xfs_fuzz_metadata` arguments.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest dangerous_fuzzers fuzzers_norepair` and imports common modules: `preamble`, `filter`, `populate`, `fuzzy`. Local helper functions: none Key environment variables or shell state names include only standard xfstests variables such as `SCRATCH_MNT`, `SCRATCH_DEV`, `seqres`, and `tmp` are used

Requirements and feature gates: `_require_scratch_xfs_fuzz_fields`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_populate_cached nofill > $seqres.full 2>&1`, `_scratch_xfs_fuzz_metadata '' 'none' 'agf 0' >> $seqres.full`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The important integration surface is xfs_db-driven metadata addressing, cached population images, mount or scrub/repair validation, and the xfstests dangerous_fuzzers gating that keeps destructive corruption tests out of ordinary quick runs. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The main risk is that target metadata layout assumptions can drift as XFS formats evolve; skips and feature requirements must remain accurate so the test corrupts the intended structure instead of producing unrelated mount, xfs_db, or repair failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 454`; `Format and populate`; `Fuzz AGF`; `Done fuzzing AGF`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/454 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/455 -->
# sources/test-tools/xfstests/tests/xfs/455

## Purpose

Populate a XFS filesystem and fuzz every AGFL field. Do not fix the filesystem, to test metadata verifiers. This file belongs to the XFS metadata fuzzing block. It uses populated scratch filesystems and common/fuzzy helpers to mutate a specific on-disk structure, then deliberately exercises verifier behavior with the repair mode encoded in its tags and `_scratch_xfs_fuzz_metadata` arguments.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest dangerous_fuzzers fuzzers_norepair` and imports common modules: `preamble`, `filter`, `populate`, `fuzzy`. Local helper functions: none Key environment variables or shell state names include `SCRATCH_XFS_LIST_METADATA_FIELDS`, `flfirst`.

Requirements and feature gates: `_require_scratch_xfs_fuzz_fields`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_populate_cached nofill > $seqres.full 2>&1`, `_scratch_xfs_fuzz_metadata '' 'none' 'agfl 0' >> $seqres.full`, `__scratch_xfs_fuzz_mdrestore`, `flfirst=$(_scratch_xfs_db -c 'agf 0' -c 'p flfirst' | sed -e 's/flfirst = //g')`, `SCRATCH_XFS_LIST_METADATA_FIELDS="bno[${flfirst}]" _scratch_xfs_fuzz_metadata '' 'none' 'agfl 0' >> $seqres.full`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The important integration surface is xfs_db-driven metadata addressing, cached population images, mount or scrub/repair validation, and the xfstests dangerous_fuzzers gating that keeps destructive corruption tests out of ordinary quick runs. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The main risk is that target metadata layout assumptions can drift as XFS formats evolve; skips and feature requirements must remain accurate so the test corrupts the intended structure instead of producing unrelated mount, xfs_db, or repair failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 455`; `Format and populate`; `Fuzz AGFL`; `Done fuzzing AGFL`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/455 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/456 -->
# sources/test-tools/xfstests/tests/xfs/456

## Purpose

Populate a XFS filesystem and fuzz every AGI field. Do not fix the filesystem, to test metadata verifiers. This file belongs to the XFS metadata fuzzing block. It uses populated scratch filesystems and common/fuzzy helpers to mutate a specific on-disk structure, then deliberately exercises verifier behavior with the repair mode encoded in its tags and `_scratch_xfs_fuzz_metadata` arguments.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest dangerous_fuzzers fuzzers_norepair` and imports common modules: `preamble`, `filter`, `populate`, `fuzzy`. Local helper functions: none Key environment variables or shell state names include only standard xfstests variables such as `SCRATCH_MNT`, `SCRATCH_DEV`, `seqres`, and `tmp` are used

Requirements and feature gates: `_require_scratch_xfs_fuzz_fields`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_populate_cached nofill > $seqres.full 2>&1`, `_scratch_xfs_fuzz_metadata '' 'none' 'agi 0' >> $seqres.full`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The important integration surface is xfs_db-driven metadata addressing, cached population images, mount or scrub/repair validation, and the xfstests dangerous_fuzzers gating that keeps destructive corruption tests out of ordinary quick runs. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The main risk is that target metadata layout assumptions can drift as XFS formats evolve; skips and feature requirements must remain accurate so the test corrupts the intended structure instead of producing unrelated mount, xfs_db, or repair failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 456`; `Format and populate`; `Fuzz AGI`; `Done fuzzing AGI`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/456 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/457 -->
# sources/test-tools/xfstests/tests/xfs/457

## Purpose

Populate a XFS filesystem and fuzz every bnobt field. Do not fix the filesystem, to test metadata verifiers. This file belongs to the XFS metadata fuzzing block. It uses populated scratch filesystems and common/fuzzy helpers to mutate a specific on-disk structure, then deliberately exercises verifier behavior with the repair mode encoded in its tags and `_scratch_xfs_fuzz_metadata` arguments.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest dangerous_fuzzers fuzzers_norepair` and imports common modules: `preamble`, `filter`, `populate`, `fuzzy`. Local helper functions: none Key environment variables or shell state names include `path`.

Requirements and feature gates: `_require_scratch_xfs_fuzz_fields`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_populate_cached nofill > $seqres.full 2>&1`, `path="$(_scratch_xfs_find_agbtree_height 'bno' 2)" || \`, `_scratch_xfs_fuzz_metadata '' 'none' "$path" 'addr bnoroot' 'addr ptrs[1]' >> $seqres.full`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The important integration surface is xfs_db-driven metadata addressing, cached population images, mount or scrub/repair validation, and the xfstests dangerous_fuzzers gating that keeps destructive corruption tests out of ordinary quick runs. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The main risk is that target metadata layout assumptions can drift as XFS formats evolve; skips and feature requirements must remain accurate so the test corrupts the intended structure instead of producing unrelated mount, xfs_db, or repair failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 457`; `Format and populate`; `Fuzz bnobt recs`; `Done fuzzing bnobt recs`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/457 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/458 -->
# sources/test-tools/xfstests/tests/xfs/458

## Purpose

Populate a XFS filesystem and fuzz every bnobt key/pointer. Do not fix the filesystem, to test metadata verifiers. This file belongs to the XFS metadata fuzzing block. It uses populated scratch filesystems and common/fuzzy helpers to mutate a specific on-disk structure, then deliberately exercises verifier behavior with the repair mode encoded in its tags and `_scratch_xfs_fuzz_metadata` arguments.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest dangerous_fuzzers fuzzers_norepair` and imports common modules: `preamble`, `filter`, `populate`, `fuzzy`. Local helper functions: none Key environment variables or shell state names include `path`.

Requirements and feature gates: `_require_scratch_xfs_fuzz_fields`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_populate_cached nofill > $seqres.full 2>&1`, `path="$(_scratch_xfs_find_agbtree_height 'bno' 2)" || \`, `_scratch_xfs_fuzz_metadata '' 'none' "$path" 'addr bnoroot' >> $seqres.full`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The important integration surface is xfs_db-driven metadata addressing, cached population images, mount or scrub/repair validation, and the xfstests dangerous_fuzzers gating that keeps destructive corruption tests out of ordinary quick runs. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The main risk is that target metadata layout assumptions can drift as XFS formats evolve; skips and feature requirements must remain accurate so the test corrupts the intended structure instead of producing unrelated mount, xfs_db, or repair failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 458`; `Format and populate`; `Fuzz bnobt keyptr`; `Done fuzzing bnobt keyptr`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/458 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/459 -->
# sources/test-tools/xfstests/tests/xfs/459

## Purpose

Populate a XFS filesystem and fuzz every cntbt field. Do not fix the filesystem, to test metadata verifiers. This file belongs to the XFS metadata fuzzing block. It uses populated scratch filesystems and common/fuzzy helpers to mutate a specific on-disk structure, then deliberately exercises verifier behavior with the repair mode encoded in its tags and `_scratch_xfs_fuzz_metadata` arguments.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest dangerous_fuzzers fuzzers_norepair` and imports common modules: `preamble`, `filter`, `populate`, `fuzzy`. Local helper functions: none Key environment variables or shell state names include `path`.

Requirements and feature gates: `_require_scratch_xfs_fuzz_fields`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_populate_cached nofill > $seqres.full 2>&1`, `path="$(_scratch_xfs_find_agbtree_height 'cnt' 2)" || \`, `_scratch_xfs_fuzz_metadata '' 'none' "$path" 'addr cntroot' 'addr ptrs[1]' >> $seqres.full`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The important integration surface is xfs_db-driven metadata addressing, cached population images, mount or scrub/repair validation, and the xfstests dangerous_fuzzers gating that keeps destructive corruption tests out of ordinary quick runs. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The main risk is that target metadata layout assumptions can drift as XFS formats evolve; skips and feature requirements must remain accurate so the test corrupts the intended structure instead of producing unrelated mount, xfs_db, or repair failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 459`; `Format and populate`; `Fuzz cntbt`; `Done fuzzing cntbt`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/459 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/460 -->
# sources/test-tools/xfstests/tests/xfs/460

## Purpose

Populate a XFS filesystem and fuzz every inobt field. Do not fix the filesystem, to test metadata verifiers. This file belongs to the XFS metadata fuzzing block. It uses populated scratch filesystems and common/fuzzy helpers to mutate a specific on-disk structure, then deliberately exercises verifier behavior with the repair mode encoded in its tags and `_scratch_xfs_fuzz_metadata` arguments.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest dangerous_fuzzers fuzzers_norepair` and imports common modules: `preamble`, `filter`, `populate`, `fuzzy`. Local helper functions: none Key environment variables or shell state names include `path`.

Requirements and feature gates: `_require_scratch_xfs_fuzz_fields`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_populate_cached nofill > $seqres.full 2>&1`, `path="$(_scratch_xfs_find_agbtree_height 'ino' 2)" || \`, `_scratch_xfs_fuzz_metadata '' 'none' "$path" 'addr root' 'addr ptrs[1]' >> $seqres.full`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The important integration surface is xfs_db-driven metadata addressing, cached population images, mount or scrub/repair validation, and the xfstests dangerous_fuzzers gating that keeps destructive corruption tests out of ordinary quick runs. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The main risk is that target metadata layout assumptions can drift as XFS formats evolve; skips and feature requirements must remain accurate so the test corrupts the intended structure instead of producing unrelated mount, xfs_db, or repair failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 460`; `Format and populate`; `Fuzz inobt`; `Done fuzzing inobt`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/460 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/461 -->
# sources/test-tools/xfstests/tests/xfs/461

## Purpose

Populate a XFS filesystem and fuzz every finobt field. Do not fix the filesystem, to test metadata verifiers. This file belongs to the XFS metadata fuzzing block. It uses populated scratch filesystems and common/fuzzy helpers to mutate a specific on-disk structure, then deliberately exercises verifier behavior with the repair mode encoded in its tags and `_scratch_xfs_fuzz_metadata` arguments.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest dangerous_fuzzers fuzzers_norepair` and imports common modules: `preamble`, `filter`, `populate`, `fuzzy`. Local helper functions: none Key environment variables or shell state names include `path`.

Requirements and feature gates: `_require_scratch_xfs_fuzz_fields`, `_require_xfs_finobt`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_populate_cached nofill > $seqres.full 2>&1`, `path="$(_scratch_xfs_find_agbtree_height 'fino' 2)" || \`, `_scratch_xfs_fuzz_metadata '' 'none' "$path" 'addr free_root' 'addr ptrs[1]' >> $seqres.full`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The important integration surface is xfs_db-driven metadata addressing, cached population images, mount or scrub/repair validation, and the xfstests dangerous_fuzzers gating that keeps destructive corruption tests out of ordinary quick runs. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The main risk is that target metadata layout assumptions can drift as XFS formats evolve; skips and feature requirements must remain accurate so the test corrupts the intended structure instead of producing unrelated mount, xfs_db, or repair failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 461`; `Format and populate`; `Fuzz finobt`; `Done fuzzing finobt`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/461 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/462 -->
# sources/test-tools/xfstests/tests/xfs/462

## Purpose

Populate a XFS filesystem and fuzz every rmapbt field. Do not fix the filesystem, to test metadata verifiers. This file belongs to the XFS metadata fuzzing block. It uses populated scratch filesystems and common/fuzzy helpers to mutate a specific on-disk structure, then deliberately exercises verifier behavior with the repair mode encoded in its tags and `_scratch_xfs_fuzz_metadata` arguments.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest dangerous_fuzzers fuzzers_norepair` and imports common modules: `preamble`, `filter`, `populate`, `fuzzy`. Local helper functions: none Key environment variables or shell state names include `path`.

Requirements and feature gates: `_require_xfs_scratch_rmapbt`, `_require_scratch_xfs_fuzz_fields`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_populate_cached nofill > $seqres.full 2>&1`, `path="$(_scratch_xfs_find_agbtree_height 'rmap' 2)" || \`, `_scratch_xfs_fuzz_metadata '' 'none' "$path" 'addr rmaproot' 'addr ptrs[1]' >> $seqres.full`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The important integration surface is xfs_db-driven metadata addressing, cached population images, mount or scrub/repair validation, and the xfstests dangerous_fuzzers gating that keeps destructive corruption tests out of ordinary quick runs. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The main risk is that target metadata layout assumptions can drift as XFS formats evolve; skips and feature requirements must remain accurate so the test corrupts the intended structure instead of producing unrelated mount, xfs_db, or repair failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 462`; `Format and populate`; `Fuzz rmapbt recs`; `Done fuzzing rmapbt recs`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/462 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/463 -->
# sources/test-tools/xfstests/tests/xfs/463

## Purpose

Populate a XFS filesystem and fuzz every rmapbt key/pointer field. Do not fix the filesystem, to test metadata verifiers. This file belongs to the XFS metadata fuzzing block. It uses populated scratch filesystems and common/fuzzy helpers to mutate a specific on-disk structure, then deliberately exercises verifier behavior with the repair mode encoded in its tags and `_scratch_xfs_fuzz_metadata` arguments.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest dangerous_fuzzers fuzzers_norepair` and imports common modules: `preamble`, `filter`, `populate`, `fuzzy`. Local helper functions: none Key environment variables or shell state names include `path`.

Requirements and feature gates: `_require_xfs_scratch_rmapbt`, `_require_scratch_xfs_fuzz_fields`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_populate_cached nofill > $seqres.full 2>&1`, `path="$(_scratch_xfs_find_agbtree_height 'rmap' 2)" || \`, `_scratch_xfs_fuzz_metadata '' 'none' "$path" 'addr rmaproot' >> $seqres.full`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The important integration surface is xfs_db-driven metadata addressing, cached population images, mount or scrub/repair validation, and the xfstests dangerous_fuzzers gating that keeps destructive corruption tests out of ordinary quick runs. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The main risk is that target metadata layout assumptions can drift as XFS formats evolve; skips and feature requirements must remain accurate so the test corrupts the intended structure instead of producing unrelated mount, xfs_db, or repair failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 463`; `Format and populate`; `Fuzz rmapbt keyptr`; `Done fuzzing rmapbt keyptr`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/463 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/464 -->
# sources/test-tools/xfstests/tests/xfs/464

## Purpose

Populate a XFS filesystem and fuzz every refcountbt key/pointer field. Do not fix the filesystem, to test metadata verifiers. This file belongs to the XFS metadata fuzzing block. It uses populated scratch filesystems and common/fuzzy helpers to mutate a specific on-disk structure, then deliberately exercises verifier behavior with the repair mode encoded in its tags and `_scratch_xfs_fuzz_metadata` arguments.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest dangerous_fuzzers fuzzers_norepair` and imports common modules: `preamble`, `filter`, `populate`, `fuzzy`, `reflink`. Local helper functions: none Key environment variables or shell state names include `path`.

Requirements and feature gates: `_require_scratch_reflink`, `_require_scratch_xfs_fuzz_fields`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_populate_cached nofill > $seqres.full 2>&1`, `path="$(_scratch_xfs_find_agbtree_height 'refcnt' 2)" || \`, `_scratch_xfs_fuzz_metadata '' 'none' "$path" 'addr refcntroot' >> $seqres.full`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The important integration surface is xfs_db-driven metadata addressing, cached population images, mount or scrub/repair validation, and the xfstests dangerous_fuzzers gating that keeps destructive corruption tests out of ordinary quick runs. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The main risk is that target metadata layout assumptions can drift as XFS formats evolve; skips and feature requirements must remain accurate so the test corrupts the intended structure instead of producing unrelated mount, xfs_db, or repair failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 464`; `Format and populate`; `Fuzz refcountbt`; `Done fuzzing refcountbt`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/464 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/465 -->
# sources/test-tools/xfstests/tests/xfs/465

## Purpose

Populate a XFS filesystem and fuzz every btree-format directory inode field. Do not fix the filesystem, to test metadata verifiers. This file belongs to the XFS metadata fuzzing block. It uses populated scratch filesystems and common/fuzzy helpers to mutate a specific on-disk structure, then deliberately exercises verifier behavior with the repair mode encoded in its tags and `_scratch_xfs_fuzz_metadata` arguments.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest dangerous_fuzzers fuzzers_norepair` and imports common modules: `preamble`, `filter`, `populate`, `fuzzy`. Local helper functions: none Key environment variables or shell state names include `inum`.

Requirements and feature gates: `_require_scratch_xfs_fuzz_fields`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_populate_cached nofill > $seqres.full 2>&1`, `_scratch_mount`, `_scratch_unmount`, `_scratch_xfs_fuzz_metadata '' 'none' "inode ${inum}" >> $seqres.full`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The important integration surface is xfs_db-driven metadata addressing, cached population images, mount or scrub/repair validation, and the xfstests dangerous_fuzzers gating that keeps destructive corruption tests out of ordinary quick runs. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The main risk is that target metadata layout assumptions can drift as XFS formats evolve; skips and feature requirements must remain accurate so the test corrupts the intended structure instead of producing unrelated mount, xfs_db, or repair failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 465`; `Format and populate`; `Find btree-format dir inode`; `Fuzz inode`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/465 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/466 -->
# sources/test-tools/xfstests/tests/xfs/466

## Purpose

Populate a XFS filesystem and fuzz every extents-format file inode field. Do not fix the filesystem, to test metadata verifiers. This file belongs to the XFS metadata fuzzing block. It uses populated scratch filesystems and common/fuzzy helpers to mutate a specific on-disk structure, then deliberately exercises verifier behavior with the repair mode encoded in its tags and `_scratch_xfs_fuzz_metadata` arguments.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest dangerous_fuzzers fuzzers_norepair` and imports common modules: `preamble`, `filter`, `populate`, `fuzzy`. Local helper functions: none Key environment variables or shell state names include `inum`.

Requirements and feature gates: `_require_scratch_xfs_fuzz_fields`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_populate_cached nofill > $seqres.full 2>&1`, `_scratch_mount`, `_scratch_unmount`, `_scratch_xfs_fuzz_metadata '' 'none' "inode ${inum}" >> $seqres.full`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The important integration surface is xfs_db-driven metadata addressing, cached population images, mount or scrub/repair validation, and the xfstests dangerous_fuzzers gating that keeps destructive corruption tests out of ordinary quick runs. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The main risk is that target metadata layout assumptions can drift as XFS formats evolve; skips and feature requirements must remain accurate so the test corrupts the intended structure instead of producing unrelated mount, xfs_db, or repair failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 466`; `Format and populate`; `Find extents-format file inode`; `Fuzz inode`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/466 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/467 -->
# sources/test-tools/xfstests/tests/xfs/467

## Purpose

Populate a XFS filesystem and fuzz every btree-format file inode field. Do not fix the filesystem, to test metadata verifiers. This file belongs to the XFS metadata fuzzing block. It uses populated scratch filesystems and common/fuzzy helpers to mutate a specific on-disk structure, then deliberately exercises verifier behavior with the repair mode encoded in its tags and `_scratch_xfs_fuzz_metadata` arguments.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest dangerous_fuzzers fuzzers_norepair` and imports common modules: `preamble`, `filter`, `populate`, `fuzzy`. Local helper functions: none Key environment variables or shell state names include `inum`.

Requirements and feature gates: `_require_scratch_xfs_fuzz_fields`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_populate_cached nofill > $seqres.full 2>&1`, `_scratch_mount`, `_scratch_unmount`, `_scratch_xfs_fuzz_metadata '' 'none' "inode ${inum}" >> $seqres.full`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The important integration surface is xfs_db-driven metadata addressing, cached population images, mount or scrub/repair validation, and the xfstests dangerous_fuzzers gating that keeps destructive corruption tests out of ordinary quick runs. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The main risk is that target metadata layout assumptions can drift as XFS formats evolve; skips and feature requirements must remain accurate so the test corrupts the intended structure instead of producing unrelated mount, xfs_db, or repair failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 467`; `Format and populate`; `Find btree-format file inode`; `Fuzz inode`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/467 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/468 -->
# sources/test-tools/xfstests/tests/xfs/468

## Purpose

Populate a XFS filesystem and fuzz every bmbt block field. Do not fix the filesystem, to test metadata verifiers. This file belongs to the XFS metadata fuzzing block. It uses populated scratch filesystems and common/fuzzy helpers to mutate a specific on-disk structure, then deliberately exercises verifier behavior with the repair mode encoded in its tags and `_scratch_xfs_fuzz_metadata` arguments.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest dangerous_fuzzers fuzzers_norepair` and imports common modules: `preamble`, `filter`, `populate`, `fuzzy`. Local helper functions: none Key environment variables or shell state names include `inode_ver`, `inum`.

Requirements and feature gates: `_require_scratch_xfs_fuzz_fields`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_populate_cached nofill > $seqres.full 2>&1`, `_scratch_mount`, `_scratch_unmount`, `inode_ver=$(_scratch_xfs_get_metadata_field "core.version" "inode ${inum}")`, `_scratch_xfs_fuzz_metadata '' 'none' "inode ${inum}" "addr u${inode_ver}.bmbt.ptrs[1]" >> $seqres.full`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The important integration surface is xfs_db-driven metadata addressing, cached population images, mount or scrub/repair validation, and the xfstests dangerous_fuzzers gating that keeps destructive corruption tests out of ordinary quick runs. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The main risk is that target metadata layout assumptions can drift as XFS formats evolve; skips and feature requirements must remain accurate so the test corrupts the intended structure instead of producing unrelated mount, xfs_db, or repair failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 468`; `Format and populate`; `Find bmbt block`; `Fuzz bmbt`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/468 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/469 -->
# sources/test-tools/xfstests/tests/xfs/469

## Purpose

Populate a XFS filesystem and fuzz every symlink remote block field. Do not fix the filesystem, to test metadata verifiers. This file belongs to the XFS metadata fuzzing block. It uses populated scratch filesystems and common/fuzzy helpers to mutate a specific on-disk structure, then deliberately exercises verifier behavior with the repair mode encoded in its tags and `_scratch_xfs_fuzz_metadata` arguments.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest dangerous_fuzzers fuzzers_norepair` and imports common modules: `preamble`, `filter`, `populate`, `fuzzy`. Local helper functions: none Key environment variables or shell state names include `inum`.

Requirements and feature gates: `_require_scratch_xfs_fuzz_fields`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_populate_cached nofill > $seqres.full 2>&1`, `_scratch_mount`, `_scratch_unmount`, `_scratch_xfs_fuzz_metadata '' 'none' "inode ${inum}" 'dblock 0' >> $seqres.full`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The important integration surface is xfs_db-driven metadata addressing, cached population images, mount or scrub/repair validation, and the xfstests dangerous_fuzzers gating that keeps destructive corruption tests out of ordinary quick runs. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The main risk is that target metadata layout assumptions can drift as XFS formats evolve; skips and feature requirements must remain accurate so the test corrupts the intended structure instead of producing unrelated mount, xfs_db, or repair failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 469`; `Format and populate`; `Find symlink remote block`; `Fuzz symlink remote block`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/469 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/470 -->
# sources/test-tools/xfstests/tests/xfs/470

## Purpose

Populate a XFS filesystem and fuzz every inline directory inode field. Do not fix the filesystem, to test metadata verifiers. This file belongs to the XFS metadata fuzzing block. It uses populated scratch filesystems and common/fuzzy helpers to mutate a specific on-disk structure, then deliberately exercises verifier behavior with the repair mode encoded in its tags and `_scratch_xfs_fuzz_metadata` arguments.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest dangerous_fuzzers fuzzers_norepair` and imports common modules: `preamble`, `filter`, `populate`, `fuzzy`. Local helper functions: none Key environment variables or shell state names include `inum`.

Requirements and feature gates: `_require_scratch_xfs_fuzz_fields`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_populate_cached nofill > $seqres.full 2>&1`, `_scratch_mount`, `_scratch_unmount`, `_scratch_xfs_fuzz_metadata '' 'none' "inode ${inum}" >> $seqres.full`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The important integration surface is xfs_db-driven metadata addressing, cached population images, mount or scrub/repair validation, and the xfstests dangerous_fuzzers gating that keeps destructive corruption tests out of ordinary quick runs. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The main risk is that target metadata layout assumptions can drift as XFS formats evolve; skips and feature requirements must remain accurate so the test corrupts the intended structure instead of producing unrelated mount, xfs_db, or repair failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 470`; `Format and populate`; `Find inline-format dir inode`; `Fuzz inline-format dir inode`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/470 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/471 -->
# sources/test-tools/xfstests/tests/xfs/471

## Purpose

Populate a XFS filesystem and fuzz every block-format dir block field. Do not fix the filesystem, to test metadata verifiers. This file belongs to the XFS metadata fuzzing block. It uses populated scratch filesystems and common/fuzzy helpers to mutate a specific on-disk structure, then deliberately exercises verifier behavior with the repair mode encoded in its tags and `_scratch_xfs_fuzz_metadata` arguments.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest dangerous_fuzzers fuzzers_norepair` and imports common modules: `preamble`, `filter`, `populate`, `fuzzy`. Local helper functions: none Key environment variables or shell state names include `inum`.

Requirements and feature gates: `_require_scratch_xfs_fuzz_fields`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_populate_cached nofill > $seqres.full 2>&1`, `_scratch_mount`, `_scratch_unmount`, `_scratch_xfs_fuzz_metadata '' 'none' "inode ${inum}" 'dblock 0' >> $seqres.full`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The important integration surface is xfs_db-driven metadata addressing, cached population images, mount or scrub/repair validation, and the xfstests dangerous_fuzzers gating that keeps destructive corruption tests out of ordinary quick runs. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The main risk is that target metadata layout assumptions can drift as XFS formats evolve; skips and feature requirements must remain accurate so the test corrupts the intended structure instead of producing unrelated mount, xfs_db, or repair failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 471`; `Format and populate`; `Find data-format dir block`; `Fuzz data-format dir block`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/471 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/472 -->
# sources/test-tools/xfstests/tests/xfs/472

## Purpose

Populate a XFS filesystem and fuzz every data-format dir block field. Do not fix the filesystem, to test metadata verifiers. This file belongs to the XFS metadata fuzzing block. It uses populated scratch filesystems and common/fuzzy helpers to mutate a specific on-disk structure, then deliberately exercises verifier behavior with the repair mode encoded in its tags and `_scratch_xfs_fuzz_metadata` arguments.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest dangerous_fuzzers fuzzers_norepair` and imports common modules: `preamble`, `filter`, `populate`, `fuzzy`. Local helper functions: none Key environment variables or shell state names include `blk_sz`, `inum`.

Requirements and feature gates: `_require_scratch_xfs_fuzz_fields`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_populate_cached nofill > $seqres.full 2>&1`, `_scratch_mount`, `_scratch_unmount`, `_scratch_xfs_fuzz_metadata '' 'none' "inode ${inum}" "dblock 0" >> $seqres.full`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The important integration surface is xfs_db-driven metadata addressing, cached population images, mount or scrub/repair validation, and the xfstests dangerous_fuzzers gating that keeps destructive corruption tests out of ordinary quick runs. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The main risk is that target metadata layout assumptions can drift as XFS formats evolve; skips and feature requirements must remain accurate so the test corrupts the intended structure instead of producing unrelated mount, xfs_db, or repair failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 472`; `Format and populate`; `Find data-format dir block`; `Fuzz data-format dir block`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/472 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/473 -->
# sources/test-tools/xfstests/tests/xfs/473

## Purpose

Populate a XFS filesystem and fuzz every leaf1-format dir block field. Do not fix the filesystem, to test metadata verifiers. This file belongs to the XFS metadata fuzzing block. It uses populated scratch filesystems and common/fuzzy helpers to mutate a specific on-disk structure, then deliberately exercises verifier behavior with the repair mode encoded in its tags and `_scratch_xfs_fuzz_metadata` arguments.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest dangerous_fuzzers fuzzers_norepair` and imports common modules: `preamble`, `filter`, `populate`, `fuzzy`. Local helper functions: none Key environment variables or shell state names include `blk_sz`, `inum`, `leaf_offset`.

Requirements and feature gates: `_require_scratch_xfs_fuzz_fields`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_populate_cached nofill > $seqres.full 2>&1`, `_scratch_mount`, `_scratch_unmount`, `_scratch_xfs_fuzz_metadata '' 'none' "inode ${inum}" "dblock ${leaf_offset}" >> $seqres.full`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The important integration surface is xfs_db-driven metadata addressing, cached population images, mount or scrub/repair validation, and the xfstests dangerous_fuzzers gating that keeps destructive corruption tests out of ordinary quick runs. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The main risk is that target metadata layout assumptions can drift as XFS formats evolve; skips and feature requirements must remain accurate so the test corrupts the intended structure instead of producing unrelated mount, xfs_db, or repair failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 473`; `Format and populate`; `Find leaf1-format dir block`; `Fuzz leaf1-format dir block`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/473 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/474 -->
# sources/test-tools/xfstests/tests/xfs/474

## Purpose

Populate a XFS filesystem and fuzz every leafn-format dir block field. Do not fix the filesystem, to test metadata verifiers. This file belongs to the XFS metadata fuzzing block. It uses populated scratch filesystems and common/fuzzy helpers to mutate a specific on-disk structure, then deliberately exercises verifier behavior with the repair mode encoded in its tags and `_scratch_xfs_fuzz_metadata` arguments.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest dangerous_fuzzers fuzzers_norepair` and imports common modules: `preamble`, `filter`, `populate`, `fuzzy`. Local helper functions: none Key environment variables or shell state names include `blk_sz`, `inum`, `leaf_offset`.

Requirements and feature gates: `_require_scratch_xfs_fuzz_fields`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_populate_cached nofill > $seqres.full 2>&1`, `_scratch_mount`, `_scratch_unmount`, `_scratch_xfs_fuzz_metadata '' 'none' "inode ${inum}" "dblock ${leaf_offset}" >> $seqres.full`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The important integration surface is xfs_db-driven metadata addressing, cached population images, mount or scrub/repair validation, and the xfstests dangerous_fuzzers gating that keeps destructive corruption tests out of ordinary quick runs. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The main risk is that target metadata layout assumptions can drift as XFS formats evolve; skips and feature requirements must remain accurate so the test corrupts the intended structure instead of producing unrelated mount, xfs_db, or repair failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 474`; `Format and populate`; `Find leafn-format dir block`; `Fuzz leafn-format dir block`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/474 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/475 -->
# sources/test-tools/xfstests/tests/xfs/475

## Purpose

Populate a XFS filesystem and fuzz every node-format dir block field. Do not fix the filesystem, to test metadata verifiers. This file belongs to the XFS metadata fuzzing block. It uses populated scratch filesystems and common/fuzzy helpers to mutate a specific on-disk structure, then deliberately exercises verifier behavior with the repair mode encoded in its tags and `_scratch_xfs_fuzz_metadata` arguments.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest dangerous_fuzzers fuzzers_norepair` and imports common modules: `preamble`, `filter`, `populate`, `fuzzy`. Local helper functions: none Key environment variables or shell state names include `blk_sz`, `inum`, `leaf_offset`.

Requirements and feature gates: `_require_scratch_xfs_fuzz_fields`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_populate_cached nofill > $seqres.full 2>&1`, `_scratch_mount`, `_scratch_unmount`, `_scratch_xfs_fuzz_metadata '' 'none' "inode ${inum}" "dblock ${leaf_offset}" >> $seqres.full`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The important integration surface is xfs_db-driven metadata addressing, cached population images, mount or scrub/repair validation, and the xfstests dangerous_fuzzers gating that keeps destructive corruption tests out of ordinary quick runs. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The main risk is that target metadata layout assumptions can drift as XFS formats evolve; skips and feature requirements must remain accurate so the test corrupts the intended structure instead of producing unrelated mount, xfs_db, or repair failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 475`; `Format and populate`; `Find node-format dir block`; `Fuzz node-format dir block`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/475 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/476 -->
# sources/test-tools/xfstests/tests/xfs/476

## Purpose

Populate a XFS filesystem and fuzz every freeindex-format dir block field. Do not fix the filesystem, to test metadata verifiers. This file belongs to the XFS metadata fuzzing block. It uses populated scratch filesystems and common/fuzzy helpers to mutate a specific on-disk structure, then deliberately exercises verifier behavior with the repair mode encoded in its tags and `_scratch_xfs_fuzz_metadata` arguments.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest dangerous_fuzzers fuzzers_norepair` and imports common modules: `preamble`, `filter`, `populate`, `fuzzy`. Local helper functions: none Key environment variables or shell state names include `blk_sz`, `inum`, `leaf_offset`.

Requirements and feature gates: `_require_scratch_xfs_fuzz_fields`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_populate_cached nofill > $seqres.full 2>&1`, `_scratch_mount`, `_scratch_unmount`, `_scratch_xfs_fuzz_metadata '' 'none' "inode ${inum}" "dblock ${leaf_offset}" >> $seqres.full`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The important integration surface is xfs_db-driven metadata addressing, cached population images, mount or scrub/repair validation, and the xfstests dangerous_fuzzers gating that keeps destructive corruption tests out of ordinary quick runs. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The main risk is that target metadata layout assumptions can drift as XFS formats evolve; skips and feature requirements must remain accurate so the test corrupts the intended structure instead of producing unrelated mount, xfs_db, or repair failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 476`; `Format and populate`; `Find freeindex-format dir block`; `Fuzz freeindex-format dir block`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/476 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/477 -->
# sources/test-tools/xfstests/tests/xfs/477

## Purpose

Populate a XFS filesystem and fuzz every inline attr inode field. Do not fix the filesystem, to test metadata verifiers. This file belongs to the XFS metadata fuzzing block. It uses populated scratch filesystems and common/fuzzy helpers to mutate a specific on-disk structure, then deliberately exercises verifier behavior with the repair mode encoded in its tags and `_scratch_xfs_fuzz_metadata` arguments.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest dangerous_fuzzers fuzzers_norepair` and imports common modules: `preamble`, `filter`, `populate`, `fuzzy`. Local helper functions: none Key environment variables or shell state names include `inum`.

Requirements and feature gates: `_require_scratch_xfs_fuzz_fields`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_populate_cached nofill > $seqres.full 2>&1`, `_scratch_mount`, `_scratch_unmount`, `_scratch_xfs_fuzz_metadata '' 'none' "inode ${inum}" >> $seqres.full`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The important integration surface is xfs_db-driven metadata addressing, cached population images, mount or scrub/repair validation, and the xfstests dangerous_fuzzers gating that keeps destructive corruption tests out of ordinary quick runs. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The main risk is that target metadata layout assumptions can drift as XFS formats evolve; skips and feature requirements must remain accurate so the test corrupts the intended structure instead of producing unrelated mount, xfs_db, or repair failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 477`; `Format and populate`; `Find inline-format attr inode`; `Fuzz inline-format attr inode`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/477 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/478 -->
# sources/test-tools/xfstests/tests/xfs/478

## Purpose

Populate a XFS filesystem and fuzz every leaf-format attr block field. Do not fix the filesystem, to test metadata verifiers. This file belongs to the XFS metadata fuzzing block. It uses populated scratch filesystems and common/fuzzy helpers to mutate a specific on-disk structure, then deliberately exercises verifier behavior with the repair mode encoded in its tags and `_scratch_xfs_fuzz_metadata` arguments.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest dangerous_fuzzers fuzzers_norepair` and imports common modules: `preamble`, `filter`, `populate`, `fuzzy`. Local helper functions: none Key environment variables or shell state names include `inum`.

Requirements and feature gates: `_require_scratch_xfs_fuzz_fields`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_populate_cached nofill > $seqres.full 2>&1`, `_scratch_mount`, `_scratch_unmount`, `_scratch_xfs_fuzz_metadata '' 'none' "inode ${inum}" 'ablock 0' >> $seqres.full`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The important integration surface is xfs_db-driven metadata addressing, cached population images, mount or scrub/repair validation, and the xfstests dangerous_fuzzers gating that keeps destructive corruption tests out of ordinary quick runs. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The main risk is that target metadata layout assumptions can drift as XFS formats evolve; skips and feature requirements must remain accurate so the test corrupts the intended structure instead of producing unrelated mount, xfs_db, or repair failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 478`; `Format and populate`; `Find leaf-format attr block`; `Fuzz leaf-format attr block`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/478 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/479 -->
# sources/test-tools/xfstests/tests/xfs/479

## Purpose

Populate a XFS filesystem and fuzz every node-format attr block field. Do not fix the filesystem, to test metadata verifiers. This file belongs to the XFS metadata fuzzing block. It uses populated scratch filesystems and common/fuzzy helpers to mutate a specific on-disk structure, then deliberately exercises verifier behavior with the repair mode encoded in its tags and `_scratch_xfs_fuzz_metadata` arguments.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest dangerous_fuzzers fuzzers_norepair` and imports common modules: `preamble`, `filter`, `populate`, `fuzzy`. Local helper functions: none Key environment variables or shell state names include `inum`.

Requirements and feature gates: `_require_scratch_xfs_fuzz_fields`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_populate_cached nofill > $seqres.full 2>&1`, `_scratch_mount`, `_scratch_unmount`, `_scratch_xfs_fuzz_metadata '' 'none' "inode ${inum}" "ablock 0" >> $seqres.full`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The important integration surface is xfs_db-driven metadata addressing, cached population images, mount or scrub/repair validation, and the xfstests dangerous_fuzzers gating that keeps destructive corruption tests out of ordinary quick runs. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The main risk is that target metadata layout assumptions can drift as XFS formats evolve; skips and feature requirements must remain accurate so the test corrupts the intended structure instead of producing unrelated mount, xfs_db, or repair failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 479`; `Format and populate`; `Find node-format attr block`; `Fuzz node-format attr block`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/479 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/480 -->
# sources/test-tools/xfstests/tests/xfs/480

## Purpose

Populate a XFS filesystem and fuzz every external attr block field. Do not fix the filesystem, to test metadata verifiers. This file belongs to the XFS metadata fuzzing block. It uses populated scratch filesystems and common/fuzzy helpers to mutate a specific on-disk structure, then deliberately exercises verifier behavior with the repair mode encoded in its tags and `_scratch_xfs_fuzz_metadata` arguments.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest dangerous_fuzzers fuzzers_norepair` and imports common modules: `preamble`, `filter`, `populate`, `fuzzy`. Local helper functions: none Key environment variables or shell state names include `inum`.

Requirements and feature gates: `_require_scratch_xfs_fuzz_fields`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_populate_cached nofill > $seqres.full 2>&1`, `_scratch_mount`, `_scratch_unmount`, `_scratch_xfs_fuzz_metadata '' 'none' "inode ${inum}" "ablock 1" >> $seqres.full`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The important integration surface is xfs_db-driven metadata addressing, cached population images, mount or scrub/repair validation, and the xfstests dangerous_fuzzers gating that keeps destructive corruption tests out of ordinary quick runs. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The main risk is that target metadata layout assumptions can drift as XFS formats evolve; skips and feature requirements must remain accurate so the test corrupts the intended structure instead of producing unrelated mount, xfs_db, or repair failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 480`; `Format and populate`; `Find external attr block`; `Fuzz external attr block`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/480 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/481 -->
# sources/test-tools/xfstests/tests/xfs/481

## Purpose

Populate a XFS filesystem and fuzz every rtrmapbt record field. Do not fix the filesystem, to test metadata verifiers. This file belongs to the XFS metadata fuzzing block. It uses populated scratch filesystems and common/fuzzy helpers to mutate a specific on-disk structure, then deliberately exercises verifier behavior with the repair mode encoded in its tags and `_scratch_xfs_fuzz_metadata` arguments.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest dangerous_fuzzers fuzzers_norepair realtime` and imports common modules: `preamble`, `filter`, `populate`, `fuzzy`. Local helper functions: none Key environment variables or shell state names include `inode_ver`, `path`.

Requirements and feature gates: `_require_realtime`, `_require_xfs_scratch_rmapbt`, `_require_scratch_xfs_fuzz_fields`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_populate_cached nofill > $seqres.full 2>&1`, `path="$(_scratch_xfs_find_rgbtree_height 'rmap' 2)" || \`, `inode_ver=$(_scratch_xfs_get_metadata_field "core.version" "path -m $path")`, `_scratch_xfs_fuzz_metadata '' 'none' "path -m $path" "addr u${inode_ver}.rtrmapbt.ptrs[1]" >> $seqres.full`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The important integration surface is xfs_db-driven metadata addressing, cached population images, mount or scrub/repair validation, and the xfstests dangerous_fuzzers gating that keeps destructive corruption tests out of ordinary quick runs. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The main risk is that target metadata layout assumptions can drift as XFS formats evolve; skips and feature requirements must remain accurate so the test corrupts the intended structure instead of producing unrelated mount, xfs_db, or repair failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 481`; `Format and populate`; `Fuzz rtrmapbt recs`; `Done fuzzing rtrmapbt recs`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/481 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/482 -->
# sources/test-tools/xfstests/tests/xfs/482

## Purpose

Populate a XFS filesystem and fuzz every rtrmapbt key/pointer field. Do not fix the filesystem, to test metadata verifiers. This file belongs to the XFS metadata fuzzing block. It uses populated scratch filesystems and common/fuzzy helpers to mutate a specific on-disk structure, then deliberately exercises verifier behavior with the repair mode encoded in its tags and `_scratch_xfs_fuzz_metadata` arguments.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest dangerous_fuzzers fuzzers_norepair realtime` and imports common modules: `preamble`, `filter`, `populate`, `fuzzy`. Local helper functions: none Key environment variables or shell state names include `path`.

Requirements and feature gates: `_require_realtime`, `_require_xfs_scratch_rmapbt`, `_require_scratch_xfs_fuzz_fields`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_populate_cached nofill > $seqres.full 2>&1`, `path="$(_scratch_xfs_find_rgbtree_height 'rmap' 2)" || \`, `_scratch_xfs_fuzz_metadata '(rtrmapbt)' 'offline' "path -m $path" >> $seqres.full`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The important integration surface is xfs_db-driven metadata addressing, cached population images, mount or scrub/repair validation, and the xfstests dangerous_fuzzers gating that keeps destructive corruption tests out of ordinary quick runs. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The main risk is that target metadata layout assumptions can drift as XFS formats evolve; skips and feature requirements must remain accurate so the test corrupts the intended structure instead of producing unrelated mount, xfs_db, or repair failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 482`; `Format and populate`; `Fuzz rtrmapbt keyptrs`; `Done fuzzing rtrmapbt keyptrs`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/482 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/483 -->
# sources/test-tools/xfstests/tests/xfs/483

## Purpose

Populate a XFS filesystem and fuzz every refcountbt field. Do not fix the filesystem, to test metadata verifiers. This file belongs to the XFS metadata fuzzing block. It uses populated scratch filesystems and common/fuzzy helpers to mutate a specific on-disk structure, then deliberately exercises verifier behavior with the repair mode encoded in its tags and `_scratch_xfs_fuzz_metadata` arguments.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest dangerous_fuzzers fuzzers_norepair` and imports common modules: `preamble`, `filter`, `populate`, `fuzzy`, `reflink`. Local helper functions: none Key environment variables or shell state names include `path`.

Requirements and feature gates: `_require_scratch_reflink`, `_require_scratch_xfs_fuzz_fields`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_populate_cached nofill > $seqres.full 2>&1`, `path="$(_scratch_xfs_find_agbtree_height 'refcnt' 2)" || \`, `_scratch_xfs_fuzz_metadata '' 'none' "$path" 'addr refcntroot' 'addr ptrs[1]' >> $seqres.full`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The important integration surface is xfs_db-driven metadata addressing, cached population images, mount or scrub/repair validation, and the xfstests dangerous_fuzzers gating that keeps destructive corruption tests out of ordinary quick runs. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The main risk is that target metadata layout assumptions can drift as XFS formats evolve; skips and feature requirements must remain accurate so the test corrupts the intended structure instead of producing unrelated mount, xfs_db, or repair failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 483`; `Format and populate`; `Fuzz refcountbt`; `Done fuzzing refcountbt`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/483 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/484 -->
# sources/test-tools/xfstests/tests/xfs/484

## Purpose

Populate a XFS filesystem and fuzz every btree-format attr inode field. Do not fix the filesystem, to test metadata verifiers. This file belongs to the XFS metadata fuzzing block. It uses populated scratch filesystems and common/fuzzy helpers to mutate a specific on-disk structure, then deliberately exercises verifier behavior with the repair mode encoded in its tags and `_scratch_xfs_fuzz_metadata` arguments.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest dangerous_fuzzers fuzzers_norepair` and imports common modules: `preamble`, `filter`, `populate`, `fuzzy`. Local helper functions: none Key environment variables or shell state names include `inum`.

Requirements and feature gates: `_require_scratch_xfs_fuzz_fields`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_populate_cached nofill > $seqres.full 2>&1`, `_scratch_mount`, `_scratch_unmount`, `_scratch_xfs_fuzz_metadata '' 'none' "inode ${inum}" >> $seqres.full`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The important integration surface is xfs_db-driven metadata addressing, cached population images, mount or scrub/repair validation, and the xfstests dangerous_fuzzers gating that keeps destructive corruption tests out of ordinary quick runs. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The main risk is that target metadata layout assumptions can drift as XFS formats evolve; skips and feature requirements must remain accurate so the test corrupts the intended structure instead of producing unrelated mount, xfs_db, or repair failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 484`; `Format and populate`; `Find btree-format attr inode`; `Fuzz inode`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/484 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/485 -->
# sources/test-tools/xfstests/tests/xfs/485

## Purpose

Populate a XFS filesystem and fuzz every blockdev inode field. Do not fix the filesystem, to test metadata verifiers. This file belongs to the XFS metadata fuzzing block. It uses populated scratch filesystems and common/fuzzy helpers to mutate a specific on-disk structure, then deliberately exercises verifier behavior with the repair mode encoded in its tags and `_scratch_xfs_fuzz_metadata` arguments.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest dangerous_fuzzers fuzzers_norepair` and imports common modules: `preamble`, `filter`, `populate`, `fuzzy`. Local helper functions: none Key environment variables or shell state names include `inum`.

Requirements and feature gates: `_require_scratch_xfs_fuzz_fields`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_populate_cached nofill > $seqres.full 2>&1`, `_scratch_mount`, `_scratch_unmount`, `_scratch_xfs_fuzz_metadata '' 'none' "inode ${inum}" >> $seqres.full`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The important integration surface is xfs_db-driven metadata addressing, cached population images, mount or scrub/repair validation, and the xfstests dangerous_fuzzers gating that keeps destructive corruption tests out of ordinary quick runs. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The main risk is that target metadata layout assumptions can drift as XFS formats evolve; skips and feature requirements must remain accurate so the test corrupts the intended structure instead of producing unrelated mount, xfs_db, or repair failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 485`; `Format and populate`; `Find blockdev inode`; `Fuzz inode`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/485 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/486 -->
# sources/test-tools/xfstests/tests/xfs/486

## Purpose

Populate a XFS filesystem and fuzz every local-format symlink inode field. Do not fix the filesystem, to test metadata verifiers. This file belongs to the XFS metadata fuzzing block. It uses populated scratch filesystems and common/fuzzy helpers to mutate a specific on-disk structure, then deliberately exercises verifier behavior with the repair mode encoded in its tags and `_scratch_xfs_fuzz_metadata` arguments.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest dangerous_fuzzers fuzzers_norepair` and imports common modules: `preamble`, `filter`, `populate`, `fuzzy`. Local helper functions: none Key environment variables or shell state names include `inum`.

Requirements and feature gates: `_require_scratch_xfs_fuzz_fields`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_populate_cached nofill > $seqres.full 2>&1`, `_scratch_mount`, `_scratch_unmount`, `_scratch_xfs_fuzz_metadata '' 'none' "inode ${inum}" >> $seqres.full`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The important integration surface is xfs_db-driven metadata addressing, cached population images, mount or scrub/repair validation, and the xfstests dangerous_fuzzers gating that keeps destructive corruption tests out of ordinary quick runs. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The main risk is that target metadata layout assumptions can drift as XFS formats evolve; skips and feature requirements must remain accurate so the test corrupts the intended structure instead of producing unrelated mount, xfs_db, or repair failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 486`; `Format and populate`; `Find local-format symlink inode`; `Fuzz inode`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/486 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/487 -->
# sources/test-tools/xfstests/tests/xfs/487

## Purpose

Populate a XFS filesystem and fuzz every user dquot field. Do not fix the filesystem, to test metadata verifiers. This file belongs to the XFS metadata fuzzing block. It uses populated scratch filesystems and common/fuzzy helpers to mutate a specific on-disk structure, then deliberately exercises verifier behavior with the repair mode encoded in its tags and `_scratch_xfs_fuzz_metadata` arguments.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest dangerous_fuzzers fuzzers_norepair` and imports common modules: `preamble`, `filter`, `populate`, `fuzzy`, `quota`. Local helper functions: none Key environment variables or shell state names include only standard xfstests variables such as `SCRATCH_MNT`, `SCRATCH_DEV`, `seqres`, and `tmp` are used

Requirements and feature gates: `_require_scratch_xfs_fuzz_fields`, `_require_quota`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_populate_cached nofill > $seqres.full 2>&1`, `_scratch_mount`, `$here/src/feature -U $SCRATCH_DEV || _notrun "user quota disabled"`, `_scratch_unmount`, `_scratch_xfs_set_quota_fuzz_ids`, `_scratch_xfs_fuzz_metadata '' 'none' "dquot -u $id" >> $seqres.full`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The important integration surface is xfs_db-driven metadata addressing, cached population images, mount or scrub/repair validation, and the xfstests dangerous_fuzzers gating that keeps destructive corruption tests out of ordinary quick runs. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The main risk is that target metadata layout assumptions can drift as XFS formats evolve; skips and feature requirements must remain accurate so the test corrupts the intended structure instead of producing unrelated mount, xfs_db, or repair failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 487`; `Format and populate`; `Fuzz user 0 dquot`; `Done fuzzing dquot`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/487 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/488 -->
# sources/test-tools/xfstests/tests/xfs/488

## Purpose

Populate a XFS filesystem and fuzz every group dquot field. Do not fix the filesystem, to test metadata verifiers. This file belongs to the XFS metadata fuzzing block. It uses populated scratch filesystems and common/fuzzy helpers to mutate a specific on-disk structure, then deliberately exercises verifier behavior with the repair mode encoded in its tags and `_scratch_xfs_fuzz_metadata` arguments.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest dangerous_fuzzers fuzzers_norepair` and imports common modules: `preamble`, `filter`, `populate`, `fuzzy`, `quota`. Local helper functions: none Key environment variables or shell state names include only standard xfstests variables such as `SCRATCH_MNT`, `SCRATCH_DEV`, `seqres`, and `tmp` are used

Requirements and feature gates: `_require_scratch_xfs_fuzz_fields`, `_require_quota`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_populate_cached nofill > $seqres.full 2>&1`, `_scratch_mount`, `$here/src/feature -G $SCRATCH_DEV || _notrun "group quota disabled"`, `_scratch_unmount`, `_scratch_xfs_set_quota_fuzz_ids`, `_scratch_xfs_fuzz_metadata '' 'none' "dquot -g $id" >> $seqres.full`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The important integration surface is xfs_db-driven metadata addressing, cached population images, mount or scrub/repair validation, and the xfstests dangerous_fuzzers gating that keeps destructive corruption tests out of ordinary quick runs. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The main risk is that target metadata layout assumptions can drift as XFS formats evolve; skips and feature requirements must remain accurate so the test corrupts the intended structure instead of producing unrelated mount, xfs_db, or repair failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 488`; `Format and populate`; `Fuzz group 0 dquot`; `Done fuzzing dquot`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/488 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/489 -->
# sources/test-tools/xfstests/tests/xfs/489

## Purpose

Populate a XFS filesystem and fuzz every project dquot field. Do not fix the filesystem, to test metadata verifiers. This file belongs to the XFS metadata fuzzing block. It uses populated scratch filesystems and common/fuzzy helpers to mutate a specific on-disk structure, then deliberately exercises verifier behavior with the repair mode encoded in its tags and `_scratch_xfs_fuzz_metadata` arguments.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest dangerous_fuzzers fuzzers_norepair` and imports common modules: `preamble`, `filter`, `populate`, `fuzzy`, `quota`. Local helper functions: none Key environment variables or shell state names include only standard xfstests variables such as `SCRATCH_MNT`, `SCRATCH_DEV`, `seqres`, and `tmp` are used

Requirements and feature gates: `_require_scratch_xfs_fuzz_fields`, `_require_quota`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_populate_cached nofill > $seqres.full 2>&1`, `_scratch_mount`, `$here/src/feature -P $SCRATCH_DEV || _notrun "project quota disabled"`, `_scratch_unmount`, `_scratch_xfs_set_quota_fuzz_ids`, `_scratch_xfs_fuzz_metadata '' 'none' "dquot -p $id" >> $seqres.full`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The important integration surface is xfs_db-driven metadata addressing, cached population images, mount or scrub/repair validation, and the xfstests dangerous_fuzzers gating that keeps destructive corruption tests out of ordinary quick runs. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The main risk is that target metadata layout assumptions can drift as XFS formats evolve; skips and feature requirements must remain accurate so the test corrupts the intended structure instead of producing unrelated mount, xfs_db, or repair failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 489`; `Format and populate`; `Fuzz project 0 dquot`; `Done fuzzing dquot`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/489 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/490 -->
# sources/test-tools/xfstests/tests/xfs/490

## Purpose

Test a corruption when the directory structure and the inobt thinks the inode is free, but the inode on disk thinks it is still in use. This case test same bug (upstream linux commit ee457001ed6c) as xfs/132, but through different code path. This is a focused xfstests shell regression. It encodes an XFS behavior, userspace-tool contract, or maintenance check as a scratch/test filesystem scenario.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto quick` and imports common modules: `preamble`, `filter`. Local helper functions: `filter_dmesg`. Key environment variables or shell state names include `agcount`, `agi`, `blksz`, `fmask`, `freecount`, `inum`.

Requirements and feature gates: `_require_scratch_nocheck`, `_require_xfs_mkfs_finobt`, `_require_xfs_nocrc`, `_require_no_xfs_debug`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `local warn1="Internal error xfs_trans_cancel.*fs/xfs/xfs_trans\.c.*"`, `sed -e "s#$warn1#Intentional error in xfs_trans_cancel#"`, `_scratch_mkfs_xfs -m crc=0,finobt=0 | _filter_mkfs 2>$tmp.mkfs >> $seqres.full`, `blksz=$(_scratch_xfs_get_sb_field blocksize)`, `agcount=$(_scratch_xfs_get_sb_field agcount)`, `_scratch_mount $mount_opt`, `$XFS_IO_PROG -fc "pwrite 0 $blksz" -c fsync $SCRATCH_MNT/dir/testfile >> $seqres.full`, `_scratch_unmount`; plus 6 more.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is the xfstests common harness, scratch filesystem lifecycle helpers, xfsprogs commands, and golden-output filtering through `seqres.full` and `.out` files. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is environment sensitivity: missing xfsprogs features, kernel feature flags, scratch geometry, runtime load, or non-normalized diagnostics can produce false failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 490`; `SCRATCH_MNT/dir/newfile: Structure needs cleaning`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/490 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/491 -->
# sources/test-tools/xfstests/tests/xfs/491

## Purpose

Test detection & fixing of bad summary block counts at mount time. This file is a targeted corruption regression. It creates a scratch filesystem, mutates a precise XFS metadata field or structure, and then relies on mount, scrub, repair, or verifier behavior to prove the bug stays fixed.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto quick fuzzers` and imports common modules: `preamble`, `filter`. Local helper functions: none Key environment variables or shell state names include `avail`, `dblocks`, `total`.

Requirements and feature gates: `_require_scratch`, `_require_scratch_xfs_features LAZYSBCOUNT`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_mkfs > $seqres.full 2>&1`, `_scratch_mount >> $seqres.full 2>&1`, `_scratch_unmount`, `dblocks=$(_scratch_xfs_get_metadata_field dblocks 'sb 0')`, `_scratch_xfs_set_metadata_field fdblocks $((dblocks * 2)) 'sb 0' > $seqres.full 2>&1`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is xfs_db metadata reads/writes, common/fuzzy helpers, scratch mount cycles, and xfstests filters that normalize expected diagnostics. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is tight coupling to on-disk format details; feature gates, block-size calculations, and expected verifier messages must track XFS format changes. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 491`; `Format and mount`; `Fuzz fdblocks`; `Detection and Correction`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/491 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/492 -->
# sources/test-tools/xfstests/tests/xfs/492

## Purpose

Test detection & fixing of bad summary inode counts at mount time. This file is a targeted corruption regression. It creates a scratch filesystem, mutates a precise XFS metadata field or structure, and then relies on mount, scrub, repair, or verifier behavior to prove the bug stays fixed.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto quick fuzzers` and imports common modules: `preamble`, `filter`. Local helper functions: none Key environment variables or shell state names include `avail`, `icount`, `total`.

Requirements and feature gates: `_require_scratch`, `_require_scratch_xfs_features LAZYSBCOUNT`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_mkfs > $seqres.full 2>&1`, `_scratch_mount >> $seqres.full 2>&1`, `_scratch_unmount`, `icount=$(_scratch_xfs_get_metadata_field icount 'sb 0')`, `_scratch_xfs_set_metadata_field ifree $((icount * 2)) 'sb 0' > $seqres.full 2>&1`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is xfs_db metadata reads/writes, common/fuzzy helpers, scratch mount cycles, and xfstests filters that normalize expected diagnostics. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is tight coupling to on-disk format details; feature gates, block-size calculations, and expected verifier messages must track XFS format changes. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 492`; `Format and mount`; `Fuzz ifree`; `Detection and Correction`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/492 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/493 -->
# sources/test-tools/xfstests/tests/xfs/493

## Purpose

Test detection & fixing of bad summary block counts at mount time. Corrupt the AGFs to test mount failure when mount-fixing fails. This file is a targeted corruption regression. It creates a scratch filesystem, mutates a precise XFS metadata field or structure, and then relies on mount, scrub, repair, or verifier behavior to prove the bug stays fixed.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto quick fuzzers` and imports common modules: `preamble`, `filter`. Local helper functions: none Key environment variables or shell state names include `aglen`, `avail`, `dblocks`, `total`.

Requirements and feature gates: `_require_scratch_nocheck`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_mkfs > $seqres.full 2>&1`, `_scratch_mount >> $seqres.full 2>&1`, `_scratch_unmount`, `dblocks=$(_scratch_xfs_get_metadata_field dblocks 'sb 0')`, `_scratch_xfs_set_metadata_field fdblocks $((dblocks * 2)) 'sb 0' > $seqres.full 2>&1`, `aglen=$(_scratch_xfs_get_metadata_field length 'agf 0')`, `_scratch_xfs_set_metadata_field btreeblks $aglen 'agf 0' > $seqres.full 2>&1`, `if _try_scratch_mount >> $seqres.full 2>&1; then`; plus 1 more.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is xfs_db metadata reads/writes, common/fuzzy helpers, scratch mount cycles, and xfstests filters that normalize expected diagnostics. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is tight coupling to on-disk format details; feature gates, block-size calculations, and expected verifier messages must track XFS format changes. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 493`; `Format and mount`; `Fuzz fdblocks and btreeblks`; `Detection and Correction`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/493 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/494 -->
# sources/test-tools/xfstests/tests/xfs/494

## Purpose

Ensure that xfsprogs crc32 works correctly via xfs_io crc32cselftest command. This is a focused xfstests shell regression. It encodes an XFS behavior, userspace-tool contract, or maintenance check as a scratch/test filesystem scenario.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto quick` and imports common modules: `preamble`, `filter`. Local helper functions: `filter_selftest`. Key environment variables or shell state names include only standard xfstests variables such as `SCRATCH_MNT`, `SCRATCH_DEV`, `seqres`, and `tmp` are used

Requirements and feature gates: `_require_xfs_io_command "crc32cselftest"`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `$XFS_IO_PROG -c 'crc32cselftest' | filter_selftest`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is the xfstests common harness, scratch filesystem lifecycle helpers, xfsprogs commands, and golden-output filtering through `seqres.full` and `.out` files. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is environment sensitivity: missing xfsprogs features, kernel feature flags, scratch geometry, runtime load, or non-normalized diagnostics can produce false failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 494`; `crc32c: tests passed, 225944 bytes in XXX usec`; `Silence is golden.`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/494 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/495 -->
# sources/test-tools/xfstests/tests/xfs/495

## Purpose

Test for two related regressions -- first, check that repair doesn't repeatedly rebuild directories with a single leafn block; and check that repair also doesn't crash when it hits a corrupt da btree with a zero before pointer. This is a focused xfstests shell regression. It encodes an XFS behavior, userspace-tool contract, or maintenance check as a scratch/test filesystem scenario.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto quick repair` and imports common modules: `preamble`, `filter`, `populate`, `fuzzy`. Local helper functions: `filter_nbrepair`, `run_repair`. Key environment variables or shell state names include `blk_sz`, `inum`, `leaf_offset`.

Requirements and feature gates: `_require_scratch_nocheck`, `_require_populate_commands`, `_require_xfs_db_command "fuzz"`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_populate_cached nofill >> $seqres.full 2>&1`, `_scratch_xfs_repair > $tmp.repair 2>&1`, `_scratch_mount`, `_scratch_unmount`, `_scratch_xfs_fuzz_metadata_field "nbtree[0].before" "zeroes" "inode ${inum}" \`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is the xfstests common harness, scratch filesystem lifecycle helpers, xfsprogs commands, and golden-output filtering through `seqres.full` and `.out` files. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is environment sensitivity: missing xfsprogs features, kernel feature flags, scratch geometry, runtime load, or non-normalized diagnostics can produce false failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 495`; `Format and populate`; `Check leafn rebuilds`; `Fuzz nbtree[0].before to zero`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/495 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/496 -->
# sources/test-tools/xfstests/tests/xfs/496

## Purpose

Populate a XFS filesystem and fuzz every single-leafn-format dir block field. Use xfs_repair to fix the corruption. This file is one of the single-leafn directory block fuzzing variants. The three variants share the same target object and differ by whether corruption is repaired offline, repaired online, or left unrepaired for verifier coverage.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest dangerous_fuzzers repair fuzzers_repair` and imports common modules: `preamble`, `filter`, `populate`, `fuzzy`. Local helper functions: none Key environment variables or shell state names include `blk_sz`, `inum`, `leaf_offset`.

Requirements and feature gates: `_require_scratch_xfs_fuzz_fields`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_populate_cached nofill > $seqres.full 2>&1`, `_scratch_mount`, `_scratch_unmount`, `_scratch_xfs_fuzz_metadata '' 'offline' "inode ${inum}" "dblock ${leaf_offset}" >> $seqres.full`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is the populated `S_IFDIR.FMT_LEAFN` directory, calculated directory leaf block offset, and common/fuzzy repair-mode selection. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is false coverage if the populated image no longer creates a single-leafn directory at the expected offset, or if online repair support is not actually present when the tag implies it. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 496`; `Format and populate`; `Find single-leafn-format dir block`; `Fuzz single-leafn-format dir block`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/496 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/497 -->
# sources/test-tools/xfstests/tests/xfs/497

## Purpose

Populate a XFS filesystem and fuzz every single-leafn-format dir block field. Use xfs_scrub to fix the corruption. This file is one of the single-leafn directory block fuzzing variants. The three variants share the same target object and differ by whether corruption is repaired offline, repaired online, or left unrepaired for verifier coverage.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest dangerous_fuzzers scrub fuzzers_online_repair` and imports common modules: `preamble`, `filter`, `populate`, `fuzzy`. Local helper functions: none Key environment variables or shell state names include `blk_sz`, `inum`, `leaf_offset`.

Requirements and feature gates: `_require_scratch_xfs_fuzz_fields`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_populate_cached nofill > $seqres.full 2>&1`, `_scratch_mount`, `_scratch_unmount`, `_scratch_xfs_fuzz_metadata '' 'online' "inode ${inum}" "dblock ${leaf_offset}" >> $seqres.full`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is the populated `S_IFDIR.FMT_LEAFN` directory, calculated directory leaf block offset, and common/fuzzy repair-mode selection. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is false coverage if the populated image no longer creates a single-leafn directory at the expected offset, or if online repair support is not actually present when the tag implies it. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 497`; `Format and populate`; `Find single-leafn-format dir block`; `Fuzz single-leafn-format dir block`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/497 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/498 -->
# sources/test-tools/xfstests/tests/xfs/498

## Purpose

Populate a XFS filesystem and fuzz every single-leafn-format dir block field. Do not fix the filesystem, to test metadata verifiers. This file is one of the single-leafn directory block fuzzing variants. The three variants share the same target object and differ by whether corruption is repaired offline, repaired online, or left unrepaired for verifier coverage.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest dangerous_fuzzers fuzzers_norepair` and imports common modules: `preamble`, `filter`, `populate`, `fuzzy`. Local helper functions: none Key environment variables or shell state names include `blk_sz`, `inum`, `leaf_offset`.

Requirements and feature gates: `_require_scratch_xfs_fuzz_fields`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_populate_cached nofill > $seqres.full 2>&1`, `_scratch_mount`, `_scratch_unmount`, `_scratch_xfs_fuzz_metadata '' 'none' "inode ${inum}" "dblock ${leaf_offset}" >> $seqres.full`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is the populated `S_IFDIR.FMT_LEAFN` directory, calculated directory leaf block offset, and common/fuzzy repair-mode selection. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is false coverage if the populated image no longer creates a single-leafn directory at the expected offset, or if online repair support is not actually present when the tag implies it. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 498`; `Format and populate`; `Find single-leafn-format dir block`; `Fuzz single-leafn-format dir block`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/498 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/499 -->
# sources/test-tools/xfstests/tests/xfs/499

## Purpose

Look for stringified constants in the __print_symbolic format strings, which suggest that we forgot to TRACE_DEFINE_ENUM somewhere, which causes incomplete ftrace reporting. This is a focused xfstests shell regression. It encodes an XFS behavior, userspace-tool contract, or maintenance check as a scratch/test filesystem scenario.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto quick` and imports common modules: `preamble`, `tracing`. Local helper functions: none Key environment variables or shell state names include `cprog`, `ftrace_dir`, `oprog`, `sedprog`.

Requirements and feature gates: `_require_ftrace`, `_require_command "$CC_PROG" "cc"`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: The command flow is primarily ordinary shell setup and harness completion.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is the xfstests common harness, scratch filesystem lifecycle helpers, xfsprogs commands, and golden-output filtering through `seqres.full` and `.out` files. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is environment sensitivity: missing xfsprogs features, kernel feature flags, scratch geometry, runtime load, or non-normalized diagnostics can produce false failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 499`; `Compiler errors imply missing TRACE_DEFINE_ENUM.`; `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/499 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/500 -->
# sources/test-tools/xfstests/tests/xfs/500

## Purpose

Make sure we can't format a filesystem with insane extent hints. This is a focused xfstests shell regression. It encodes an XFS behavior, userspace-tool contract, or maintenance check as a scratch/test filesystem scenario.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto quick mkfs prealloc mkfs` and imports common modules: `preamble`. Local helper functions: none Key environment variables or shell state names include `testfile`.

Requirements and feature gates: `_require_scratch_nocheck`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_mkfs -d extszinherit=8388608 >> $seqres.full 2>&1`, `if _scratch_mkfs_xfs_supported -m crc=1,reflink=1 >> $seqres.full 2>&1; then`, `_scratch_mkfs -m reflink=1,crc=1 -d cowextsize=8388608 >> $seqres.full 2>&1`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is the xfstests common harness, scratch filesystem lifecycle helpers, xfsprogs commands, and golden-output filtering through `seqres.full` and `.out` files. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is environment sensitivity: missing xfsprogs features, kernel feature flags, scratch geometry, runtime load, or non-normalized diagnostics can produce false failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 500`; `silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/500 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/501 -->
# sources/test-tools/xfstests/tests/xfs/501

## Purpose

Stress test creating a lot of unlinked O_TMPFILE files and recovering them after a crash, checking that we don't blow up the filesystem.  This is sort of a performance test for the xfs unlinked inode backref patchset. Here we force the use of the slow iunlink bucket walk code in a single threaded situation. This file is part of the unlinked-inode stress coverage for O_TMPFILE and the iunlink fallback path. It opens many unlinked files, injects fallback behavior, and validates cleanup through unmount/remount.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto quick unlink` and imports common modules: `preamble`, `inject`. Local helper functions: `_cleanup`, `injector`. Key environment variables or shell state names include `after`, `before`, `delay_knob`, `knob`, `max_allowable_files`, `max_files`, `nr`, `testfile`.

Requirements and feature gates: `_require_xfs_io_error_injection "iunlink_fallback"`, `_require_xfs_sysfs debug/log_recovery_delay`, `_require_scratch`, `_require_test_program "t_open_tmpfiles"`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_mkfs $(_scratch_mkfs_concurrency_options) >> $seqres.full 2>&1`, `_scratch_mount`, `$here/src/t_open_tmpfiles $SCRATCH_MNT $(_scratch_shutdown_handle) >> $seqres.full`, `_scratch_unmount`, `knob="$(_find_xfs_mountdev_errortag_knob "${SCRATCH_DEV}" iunlink_fallback)"`, `echo "unable to set iunlink_fallback?"`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is the `t_open_tmpfiles` helper, error injection knobs from common/inject, scratch mkfs concurrency options, process file descriptor limits, and unlinked-list log recovery. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is resource sensitivity: file-max, ulimit, CPU count, load factor, and delayed log recovery can change runtime sharply or mask the intended iunlink fallback path. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 501`; `silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/501 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/502 -->
# sources/test-tools/xfstests/tests/xfs/502

## Purpose

Stress test creating a lot of unlinked O_TMPFILE files and closing them all at once, checking that we don't blow up the filesystem.  This is sort of a performance test for the xfs unlinked inode backref patchset. Here we force the use of the slow iunlink bucket walk code, using every CPU possible. This file is part of the unlinked-inode stress coverage for O_TMPFILE and the iunlink fallback path. It opens many unlinked files, injects fallback behavior, and validates cleanup through unmount/remount.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto quick unlink` and imports common modules: `preamble`, `inject`, `filter`. Local helper functions: none Key environment variables or shell state names include `after`, `before`, `max_allowable_files`, `max_files`, `nr_cpus`, `testfile`.

Requirements and feature gates: `_require_xfs_io_error_injection "iunlink_fallback"`, `_require_scratch`, `_require_test_program "t_open_tmpfiles"`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_mkfs $(_scratch_mkfs_concurrency_options) | _filter_mkfs 2> $tmp.mkfs > /dev/null`, `_scratch_mount`, `_scratch_inject_error "iunlink_fallback" "2"`, `$here/src/t_open_tmpfiles $SCRATCH_MNT/$i >> $seqres.full &`, `_scratch_unmount`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is the `t_open_tmpfiles` helper, error injection knobs from common/inject, scratch mkfs concurrency options, process file descriptor limits, and unlinked-list log recovery. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is resource sensitivity: file-max, ulimit, CPU count, load factor, and delayed log recovery can change runtime sharply or mask the intended iunlink fallback path. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 502`; `silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/502 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/503 -->
# sources/test-tools/xfstests/tests/xfs/503

## Purpose

Populate a XFS filesystem and ensure that metadump and mdrestore all work properly. This file validates metadump/mdrestore round trips. It creates a populated or feature-specific filesystem, emits metadumps with option combinations, restores them, and checks the restored scratch filesystem.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto metadump` and imports common modules: `preamble`, `filter`, `populate`, `metadump`. Local helper functions: `_cleanup`. Key environment variables or shell state names include `copy_file`, `metadump_file`, `testdir`.

Requirements and feature gates: `_require_command "$XFS_MDRESTORE_PROG" "xfs_mdrestore"`, `_require_loop`, `_require_scratch_nocheck`, `_require_populate_commands`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_xfs_cleanup_verify_metadump`, `_xfs_skip_online_rebuild`, `_xfs_skip_offline_rebuild`, `_xfs_setup_verify_metadump`, `_scratch_populate_cached nofill > $seqres.full 2>&1`, `_xfs_verify_metadumps`, `_xfs_verify_metadumps '-a'`, `_xfs_verify_metadumps '-o'`; plus 1 more.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is xfs_metadump, xfs_mdrestore, loop or scratch restore plumbing, populated test images, and online/offline rebuild skips used to keep verification focused on dump fidelity. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is that obfuscation, feature flags, or restore-device setup can turn a metadata serialization regression into an environment failure; restored filesystems must always be checked after each option variant. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 503`; `Format and populate`; `metadump and mdrestore`; `metadump a and mdrestore`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/503 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/504 -->
# sources/test-tools/xfstests/tests/xfs/504

## Purpose

Create a filesystem label with emoji and confusing unicode characters to make sure that these special things actually work on xfs.  In theory it should allow this (labels are a sequence of arbitrary bytes) even if the user implications are horrifying. This is a focused xfstests shell regression. It encodes an XFS behavior, userspace-tool contract, or maintenance check as a scratch/test filesystem scenario.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto quick mkfs label` and imports common modules: `preamble`, `filter`. Local helper functions: `filter_scrub`, `maybe_scrub`, `testlabel`. Key environment variables or shell state names include `output`, `want_scrub`.

Requirements and feature gates: `_require_scratch_nocheck`, `_require_xfs_io_command 'label'`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_mkfs > /dev/null`, `_scratch_mount`, `_check_xfs_scrub_does_unicode "$SCRATCH_MNT" "$SCRATCH_DEV" && want_scrub=yes`, `_scratch_unmount`, `echo "xfs_scrub output:" >> $seqres.full`, `_scratch_mkfs -L "$label" >> $seqres.full 2>&1`, `_scratch_mount >> $seqres.full 2>&1`, `local actual_label="$($XFS_IO_PROG -c label $SCRATCH_MNT)"`; plus 4 more.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is the xfstests common harness, scratch filesystem lifecycle helpers, xfsprogs commands, and golden-output filtering through `seqres.full` and `.out` files. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is environment sensitivity: missing xfsprogs features, kernel feature flags, scratch geometry, runtime load, or non-normalized diagnostics can produce false failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 504`; `Silence is golden.`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/504 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/505 -->
# sources/test-tools/xfstests/tests/xfs/505

## Purpose

Ensure all xfs_spaceman commands are documented. This is a focused xfstests shell regression. It encodes an XFS behavior, userspace-tool contract, or maintenance check as a scratch/test filesystem scenario.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto quick spaceman` and imports common modules: `preamble`. Local helper functions: none Key environment variables or shell state names include `MANPAGE`.

Requirements and feature gates: `_require_command "$XFS_SPACEMAN_PROG" "xfs_spaceman"`, `_require_command "$MAN_PROG" man`, `_require_command "$(type -P $CAT)" $CAT`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `MANPAGE=$($MAN_PROG --path xfs_spaceman)`, `for COMMAND in `$XFS_SPACEMAN_PROG -c help $TEST_DIR | awk '{print $1}' | grep -v "^Use"`; do`, `echo "$COMMAND not documented in the xfs_spaceman manpage"`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is the xfstests common harness, scratch filesystem lifecycle helpers, xfsprogs commands, and golden-output filtering through `seqres.full` and `.out` files. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is environment sensitivity: missing xfsprogs features, kernel feature flags, scratch geometry, runtime load, or non-normalized diagnostics can produce false failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 505`; `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/505 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/506 -->
# sources/test-tools/xfstests/tests/xfs/506

## Purpose

Basic tests of the xfs_spaceman health command. This file exercises XFS online scrub, health reporting, or repair-adjacent behavior. It uses the xfstests scratch device plus xfs_scrub or xfs_spaceman commands to turn metadata health into a test oracle.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto quick health` and imports common modules: `preamble`, `fuzzy`, `filter`. Local helper functions: `query`, `query_health`, `query_sick`. Key environment variables or shell state names include only standard xfstests variables such as `SCRATCH_MNT`, `SCRATCH_DEV`, `seqres`, and `tmp` are used

Requirements and feature gates: `_require_scratch_nocheck`, `_require_scrub`, `_require_xfs_spaceman_command "health"`, `_require_scratch_xfs_scrub`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_mkfs > $seqres.full 2>&1`, `_scratch_mount`, `_scratch_cycle_mount # make sure we haven't run quotacheck on this mount`, `$XFS_SPACEMAN_PROG -c "health" $SCRATCH_MNT`, `_scratch_scrub -n >> $seqres.full`, `$XFS_SPACEMAN_PROG -c "$@" $SCRATCH_MNT | tee -a $seqres.full`, `_scratch_unmount`, `_scratch_xfs_db -x -c 'sb 1' -c 'fuzz -d magicnum random' >> $seqres.full`; plus 1 more.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is common/fuzzy, xfs_io scrub commands, xfs_spaceman health output, scratch remounts, and feature-specific scrub prerequisites. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is that online health state is cached and feature-dependent; the scripts force mount cycles or explicit scrub passes to avoid reading stale state. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 506`; `Health status has not been collected for this filesystem.`; `Please run xfs_scrub(8) to remedy this situation.`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/506 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/507 -->
# sources/test-tools/xfstests/tests/xfs/507

## Purpose

Regression test for kernel commit: 394aafdc15da ("xfs: widen inode delalloc block counter to 64-bits") Try to overflow i_delayed_blks by setting the largest cowextsize hint possible, creating a sparse file with a single byte every cowextsize bytes, reflinking it, and retouching every written byte to see if we can create enough speculative COW reservations to overflow i_delayed_blks. This is a focused xfstests shell regression. It encodes an XFS behavior, userspace-tool contract, or maintenance check as a scratch/test filesystem scenario.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto clone` and imports common modules: `preamble`, `reflink`, `filter`. Local helper functions: `_cleanup`, `count_file_fork_blocks`, `count_fork_blocks`. Key environment variables or shell state names include `LARGE_SCRATCH_DEV`, `MAXEXTLEN`, `allocated_fsblocks`, `allocated_stat_blocks`, `attrblocks`, `blks_needed`, `blksz`, `cowblocks`, `cowextsize_bytes`, `curr_cowextsize_str`; plus 6 more.

Requirements and feature gates: `_require_scratch_reflink`, `_require_cp_reflink`, `_require_loop`, `_require_xfs_debug	# needed for xfs_bmap -c`, `_require_congruent_file_oplen $SCRATCH_MNT $((MAXEXTLEN * fs_blksz))`, `_require_fs_space $SCRATCH_MNT 1234567`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_mkfs > "$seqres.full" 2>&1`, `_scratch_mount`, `$XFS_IO_PROG -f -c "truncate $loop_file_sz" $loop_file`, `curr_cowextsize_str="$($XFS_IO_PROG -c 'cowextsize' "$huge_file")"`, `$XFS_IO_PROG -c "pwrite $off 1" "$huge_file" > /dev/null`, `$XFS_IO_PROG -c "bmap $args -l -p -v" "$huge_file" > $tmp.extents`, `LARGE_SCRATCH_DEV=yes _check_xfs_filesystem $loop_dev none none`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is the xfstests common harness, scratch filesystem lifecycle helpers, xfsprogs commands, and golden-output filtering through `seqres.full` and `.out` files. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is environment sensitivity: missing xfsprogs features, kernel feature flags, scratch geometry, runtime load, or non-normalized diagnostics can produce false failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 507`; `Format and mount`; `Create crazy huge file`; `Reflink crazy huge file`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/507 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/508 -->
# sources/test-tools/xfstests/tests/xfs/508

## Purpose

Test project quota inheritance flag, uncover xfsprogs bug fixed by xfsprogs commit b136f48b19a5 ("xfs_quota: fix false error reporting of project inheritance flag is not set") This file exercises quota accounting or quota scrub behavior on XFS. It combines scratch quota mount options with block usage, reflink, CoW, or stress operations and compares kernel accounting to user-visible reports.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto quick quota` and imports common modules: `preamble`, `filter`, `quota`. Local helper functions: `do_quota_nospc`, `filter_xfs_pquota`. Key environment variables or shell state names include `QUOTA_CMD`.

Requirements and feature gates: `_require_scratch`, `_require_xfs_quota`, `_require_prjquota $SCRATCH_DEV`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `QUOTA_CMD="$XFS_QUOTA_PROG -D $tmp.projects -P $tmp.projid"`, `filter_xfs_pquota()`, `$XFS_IO_PROG -t -f -c "pwrite 0 50m" $file 2>&1 >/dev/null | \`, `_filter_xfs_io_error`, `_scratch_mkfs_xfs >>$seqres.full 2>&1`, `_scratch_supports_rtquota && \`, `$QUOTA_CMD -x -c 'project -c test' $SCRATCH_MNT | filter_xfs_pquota`, `$XFS_IO_PROG -x -c "chattr -P" $SCRATCH_MNT/dir`; plus 1 more.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is common/quota, xfs_quota reports, repquota-compatible VFS quota checks, scratch remounts, and any reflink or fsstress helpers used to generate accounting pressure. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is delayed accounting and preallocation state; tests often sync, remount, or force quotacheck so speculative CoW reservations do not look like real regressions. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 508`; `== The parent directory has Project inheritance bit by default ==`; `Checking project test (path [SCR_MNT]/dir)...`; `Processed 1 ([PROJECTS_FILE] and cmdline) paths for project test with recursion depth infinite (-1).`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/508 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/509 -->
# sources/test-tools/xfstests/tests/xfs/509

## Purpose

Use the xfs_io bulkstat utility to verify bulkstat finds all inodes in a filesystem.  Test under various inode counts, inobt record layouts and bulkstat batch sizes.  Test v1 and v5 ioctls explicitly, as well as the ioctl version autodetection code in libfrog. This is a focused xfstests shell regression. It encodes an XFS behavior, userspace-tool contract, or maintenance check as a scratch/test filesystem scenario.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto ioctl` and imports common modules: `preamble`, `filter`. Local helper functions: `bstat_compare`, `bstat_count`, `bstat_perag_count`, `bstat_test`, `bstat_versions`, `count_metadir_files`, `inumbers_ag`, `inumbers_count`, `inumbers_fs`. Key environment variables or shell state names include `DIRCOUNT`, `INOCOUNT`, `METADATA_FILES`, `bs_root`, `bs_root_out`, `expect`, `has_v5`, `nr`, `stat_root`.

Requirements and feature gates: `_require_scratch`, `_require_xfs_io_command bulkstat`, `_require_xfs_io_command bulkstat_single`, `_require_xfs_io_command inumbers`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `echo "$tag($v_tag): passing \"$v_flag\" to bulkstat" >> $seqres.full`, `echo -n "bulkstat $tag($v_tag): "`, `$XFS_IO_PROG -c "bulkstat -n $batchsize $v_flag" $SCRATCH_MNT | grep ino | wc -l`, `local agcount=$(_xfs_mount_agcount $SCRATCH_MNT)`, `$XFS_IO_PROG -c "bulkstat -a $ag -n $batchsize $v_flag" $SCRATCH_MNT`, `$XFS_IO_PROG -c "inumbers -a $ag -n $batchsize $v_flag" $mount`, `$XFS_IO_PROG -c "inumbers $v_flag" "$dir" | grep alloccount | \`, `_scratch_cycle_mount`; plus 8 more.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is the xfstests common harness, scratch filesystem lifecycle helpers, xfsprogs commands, and golden-output filtering through `seqres.full` and `.out` files. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is environment sensitivity: missing xfsprogs features, kernel feature flags, scratch geometry, runtime load, or non-normalized diagnostics can produce false failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 509`; `expect 2057`; `bulkstat 4096 all(default): 2057`; `bulkstat 4096 all(v1): 2057`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/509 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/510 -->
# sources/test-tools/xfstests/tests/xfs/510

## Purpose

Regression test for a long-standing bug in BULKSTAT and INUMBERS where the kernel fails to write thew new @lastip value back to userspace if @ocount is NULL. This is a regression test for commit f16fe3ecde62 ("xfs: bulkstat should copy lastip whenever userspace supplies one") This is a focused xfstests shell regression. It encodes an XFS behavior, userspace-tool contract, or maintenance check as a scratch/test filesystem scenario.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto ioctl quick` and imports common modules: `preamble`, `filter`. Local helper functions: none Key environment variables or shell state names include only standard xfstests variables such as `SCRATCH_MNT`, `SCRATCH_DEV`, `seqres`, and `tmp` are used

Requirements and feature gates: `_require_test_program "bulkstat_null_ocount"`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `$here/src/bulkstat_null_ocount $TEST_DIR`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is the xfstests common harness, scratch filesystem lifecycle helpers, xfsprogs commands, and golden-output filtering through `seqres.full` and `.out` files. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is environment sensitivity: missing xfsprogs features, kernel feature flags, scratch geometry, runtime load, or non-normalized diagnostics can produce false failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 510`; `Silence is golden.`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/510 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/511 -->
# sources/test-tools/xfstests/tests/xfs/511

## Purpose

Test statfs when project quota is set. Uncover de7243057 fs/xfs: fix f_ffree value for statfs when project quota is set This file exercises quota accounting or quota scrub behavior on XFS. It combines scratch quota mount options with block usage, reflink, CoW, or stress operations and compares kernel accounting to user-visible reports.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto quick quota` and imports common modules: `preamble`, `filter`, `quota`. Local helper functions: `_cleanup`. Key environment variables or shell state names include `file_nblocks`, `quota_cmd`.

Requirements and feature gates: `_require_scratch`, `_require_xfs_quota`, `_require_prjquota $SCRATCH_DEV`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_unmount`, `_scratch_mkfs >/dev/null 2>&1`, `_scratch_enable_pquota`, `$XFS_IO_PROG -f -c "pwrite 0 65536" -c syncfs $SCRATCH_MNT/t/file >>$seqres.full`, `quota_cmd="$XFS_QUOTA_PROG -x"`, `_scratch_supports_rtquota && \`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is common/quota, xfs_quota reports, repquota-compatible VFS quota checks, scratch remounts, and any reflink or fsstress helpers used to generate accounting pressure. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is delayed accounting and preallocation state; tests often sync, remount, or force quotacheck so speculative CoW reservations do not look like real regressions. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 511`; `File Inodes IUsed 1K-blocks Used`; `SCRATCH_MNT/t 53 2 102400 64`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/511 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/512 -->
# sources/test-tools/xfstests/tests/xfs/512

## Purpose

Ensure that removing the access ACL through the XFS-specific attr name removes the cached ACL as well This is a focused xfstests shell regression. It encodes an XFS behavior, userspace-tool contract, or maintenance check as a scratch/test filesystem scenario.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto quick acl attr` and imports common modules: `preamble`, `filter`, `attr`. Local helper functions: `_cleanup`. Key environment variables or shell state names include `FILE`.

Requirements and feature gates: `_require_test`, `_require_runas`, `_require_acls`, `_require_attrs`, `_require_user`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: The command flow is primarily ordinary shell setup and harness completion.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is the xfstests common harness, scratch filesystem lifecycle helpers, xfsprogs commands, and golden-output filtering through `seqres.full` and `.out` files. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is environment sensitivity: missing xfsprogs features, kernel feature flags, scratch geometry, runtime load, or non-normalized diagnostics can produce false failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 512`; `No ACL:`; `Permission denied`; `With ACL:`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/512 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/513 -->
# sources/test-tools/xfstests/tests/xfs/513

## Purpose

XFS mount options sanity check, refer to 'man 5 xfs'. This is a focused xfstests shell regression. It encodes an XFS behavior, userspace-tool contract, or maintenance check as a scratch/test filesystem scenario.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto mount prealloc` and imports common modules: `preamble`, `filter`. Local helper functions: `_cleanup`, `_do_test`, `do_mkfs`, `do_test`, `filter_loop`, `filter_xfs_opt`, `force_unmount`, `get_mount_info`, `is_dev_mounted`. Key environment variables or shell state names include `LOOP_IMG`, `LOOP_MNT`, `LOOP_SPARE_IMG`, `MKFS_OPTIONS`, `info`, `loop_dev`, `loop_spare_dev`, `pagesz`, `rc`.

Requirements and feature gates: `_require_test`, `_require_loop`, `_require_xfs_io_command "falloc"`. Recorded fix annotations: `_fixed_by_kernel_commit 237d7887ae72 xfs: show the proper user quota options`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `$XFS_IO_PROG -f -c "truncate 32g" $LOOP_IMG`, `$XFS_IO_PROG -f -c "truncate 1g" $LOOP_SPARE_IMG`, `filter_xfs_opt()`, `echo -n " \"$i\"" | filter_loop | filter_xfs_opt | tee -a $seqres.full`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is the xfstests common harness, scratch filesystem lifecycle helpers, xfsprogs commands, and golden-output filtering through `seqres.full` and `.out` files. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is environment sensitivity: missing xfsprogs features, kernel feature flags, scratch geometry, runtime load, or non-normalized diagnostics can produce false failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 513`; `** create loop device`; `** create loop log device`; `** create loop mount point`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/513 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/514 -->
# sources/test-tools/xfstests/tests/xfs/514

## Purpose

Ensure all xfs_db commands are documented. This is a focused xfstests shell regression. It encodes an XFS behavior, userspace-tool contract, or maintenance check as a scratch/test filesystem scenario.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto quick db` and imports common modules: `preamble`. Local helper functions: `_cleanup`. Key environment variables or shell state names include `MANPAGE`, `file`.

Requirements and feature gates: `_require_command "$XFS_DB_PROG" "xfs_db"`, `_require_command "$MAN_PROG" man`, `_require_test`, `_require_command "$(type -P $CAT)" $CAT`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `MANPAGE=$($MAN_PROG --path xfs_db)`, `for COMMAND in `$XFS_DB_PROG -x -c help $file | awk '{print $1}' | grep -v "^Use"`; do`, `echo "$COMMAND not documented in the xfs_db manpage"`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is the xfstests common harness, scratch filesystem lifecycle helpers, xfsprogs commands, and golden-output filtering through `seqres.full` and `.out` files. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is environment sensitivity: missing xfsprogs features, kernel feature flags, scratch geometry, runtime load, or non-normalized diagnostics can produce false failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 514`; `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/514 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/515 -->
# sources/test-tools/xfstests/tests/xfs/515

## Purpose

Ensure all xfs_quota commands are documented. This file exercises quota accounting or quota scrub behavior on XFS. It combines scratch quota mount options with block usage, reflink, CoW, or stress operations and compares kernel accounting to user-visible reports.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto quick quota` and imports common modules: `preamble`. Local helper functions: `_cleanup`. Key environment variables or shell state names include `MANPAGE`.

Requirements and feature gates: `_require_command "$XFS_QUOTA_PROG" "xfs_quota"`, `_require_command "$MAN_PROG" man`, `_require_test`, `_require_command "$(type -P $CAT)" $CAT`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `MANPAGE=$($MAN_PROG --path xfs_quota)`, `for COMMAND in `$XFS_QUOTA_PROG -x -c help $file | awk '{print $1}' | grep -v "^Use"`; do`, `echo "$COMMAND not documented in the xfs_quota manpage"`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is common/quota, xfs_quota reports, repquota-compatible VFS quota checks, scratch remounts, and any reflink or fsstress helpers used to generate accounting pressure. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is delayed accounting and preallocation state; tests often sync, remount, or force quotacheck so speculative CoW reservations do not look like real regressions. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 515`; `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/515 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/516 -->
# sources/test-tools/xfstests/tests/xfs/516

## Purpose

Update sunit and width and make sure that the filesystem still passes xfs_repair afterwards. This is a focused xfstests shell regression. It encodes an XFS behavior, userspace-tool contract, or maintenance check as a scratch/test filesystem scenario.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto quick` and imports common modules: `preamble`, `fuzzy`. Local helper functions: `__test_mount_opts`, `_cleanup`, `log`, `test_repair_detection`, `test_su_opts`, `test_sunit_opts`. Key environment variables or shell state names include `run_scrub`.

Requirements and feature gates: `_require_scratch_nocheck`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_supports_xfs_scrub $TEST_DIR $TEST_DEV && run_scrub=1`, `_try_scratch_mount "$@" >> $seqres.full 2>&1 && mounted=1`, `_scratch_scrub -n >> $seqres.full`, `_scratch_unmount`, `_scratch_xfs_repair -n >> $seqres.full 2>&1 || \`, `_scratch_xfs_get_sb_field unit >> $seqres.full`, `_scratch_xfs_get_sb_field width >> $seqres.full`, `_scratch_xfs_repair >> $seqres.full 2>&1`; plus 6 more.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is the xfstests common harness, scratch filesystem lifecycle helpers, xfsprogs commands, and golden-output filtering through `seqres.full` and `.out` files. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is environment sensitivity: missing xfsprogs features, kernel feature flags, scratch geometry, runtime load, or non-normalized diagnostics can produce false failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 516`; `Test: no raid parameters`; `Test: 256k stripe unit; 4x stripe width`; `Test: 256k stripe unit; 5x stripe width`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/516 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/517 -->
# sources/test-tools/xfstests/tests/xfs/517

## Purpose

Race freeze and fsmap for a while to see if we crash or livelock. This is a focused xfstests shell regression. It encodes an XFS behavior, userspace-tool contract, or maintenance check as a scratch/test filesystem scenario.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto quick fsmap freeze` and imports common modules: `preamble`, `filter`, `fuzzy`, `inject`. Local helper functions: `_cleanup`. Key environment variables or shell state names include only standard xfstests variables such as `SCRATCH_MNT`, `SCRATCH_DEV`, `seqres`, and `tmp` are used

Requirements and feature gates: `_require_xfs_scratch_rmapbt`, `_require_xfs_io_command "fsmap"`, `_require_xfs_stress_scrub`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_begin_fstest auto quick fsmap freeze`, `_scratch_xfs_stress_scrub_cleanup`, `_scratch_mkfs > "$seqres.full" 2>&1`, `_scratch_mount`, `_scratch_xfs_stress_scrub -f -i 'fsmap -v'`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is the xfstests common harness, scratch filesystem lifecycle helpers, xfsprogs commands, and golden-output filtering through `seqres.full` and `.out` files. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is environment sensitivity: missing xfsprogs features, kernel feature flags, scratch geometry, runtime load, or non-normalized diagnostics can produce false failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 517`; `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/517 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/518 -->
# sources/test-tools/xfstests/tests/xfs/518

## Purpose

Make sure that the quota default grace period and maximum warning limits survive quotacheck. This file exercises quota accounting or quota scrub behavior on XFS. It combines scratch quota mount options with block usage, reflink, CoW, or stress operations and compares kernel accounting to user-visible reports.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto quick quota` and imports common modules: `preamble`, `filter`, `quota`. Local helper functions: none Key environment variables or shell state names include only standard xfstests variables such as `SCRATCH_MNT`, `SCRATCH_DEV`, `seqres`, and `tmp` are used

Requirements and feature gates: `_require_scratch`, `_require_quota`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_mkfs > $seqres.full`, `_scratch_mount >> $seqres.full`, `$XFS_QUOTA_PROG -x -c 'timer -u 300m' $SCRATCH_MNT`, `$XFS_QUOTA_PROG -x -c 'state -u' $SCRATCH_MNT | grep 'grace time'`, `_scratch_unmount`, `_scratch_xfs_repair >> $seqres.full 2>&1`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is common/quota, xfs_quota reports, repquota-compatible VFS quota checks, scratch remounts, and any reflink or fsstress helpers used to generate accounting pressure. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is delayed accounting and preallocation state; tests often sync, remount, or force quotacheck so speculative CoW reservations do not look like real regressions. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 518`; `Blocks grace time: [0 days 05:00:00]`; `Inodes grace time: [0 days 05:00:00]`; `Realtime Blocks grace time: [0 days 05:00:00]`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/518 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/519 -->
# sources/test-tools/xfstests/tests/xfs/519

## Purpose

Make sure that reflink forces the log out if we mount with wsync.  We test that it actually forced the log by immediately shutting down the fs without flushing the log and then remounting to check file contents. This is a focused xfstests shell regression. It encodes an XFS behavior, userspace-tool contract, or maintenance check as a scratch/test filesystem scenario.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto quick clone` and imports common modules: `preamble`, `filter`, `reflink`. Local helper functions: none Key environment variables or shell state names include only standard xfstests variables such as `SCRATCH_MNT`, `SCRATCH_DEV`, `seqres`, and `tmp` are used

Requirements and feature gates: `_require_scratch_reflink`, `_require_cp_reflink`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_mkfs > $seqres.full`, `_scratch_mount -o wsync >> $seqres.full`, `$XFS_IO_PROG -f -c 'pwrite -S 0x58 0 1m -b 1m' $SCRATCH_MNT/a >> $seqres.full`, `$XFS_IO_PROG -f -c 'pwrite -S 0x59 0 1m -b 1m' $SCRATCH_MNT/c >> $seqres.full`, `_scratch_sync`, `$XFS_IO_PROG -x -c "reflink $SCRATCH_MNT/a" -c 'shutdown' $SCRATCH_MNT/b >> $seqres.full`, `_scratch_cycle_mount wsync`, `$XFS_IO_PROG -x -c "reflink $SCRATCH_MNT/a" -c 'shutdown' $SCRATCH_MNT/d >> $seqres.full`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is the xfstests common harness, scratch filesystem lifecycle helpers, xfsprogs commands, and golden-output filtering through `seqres.full` and `.out` files. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is environment sensitivity: missing xfsprogs features, kernel feature flags, scratch geometry, runtime load, or non-normalized diagnostics can produce false failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 519`; `test reflink flag not set`; `310f146ce52077fcd3308dcbe7632bb2  SCRATCH_MNT/a`; `310f146ce52077fcd3308dcbe7632bb2  SCRATCH_MNT/b`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/519 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/520 -->
# sources/test-tools/xfstests/tests/xfs/520

## Purpose

Verify kernel doesn't hang when mounting a crafted image with bad agf.freeblks metadata due to CVE-2020-12655. Also, check if commit d0c7feaf8767 ("xfs: add agf freeblocks verify in xfs_agf_verify") is included in the current kernel. This is a focused xfstests shell regression. It encodes an XFS behavior, userspace-tool contract, or maintenance check as a scratch/test filesystem scenario.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto quick clone` and imports common modules: `preamble`, `filter`. Local helper functions: `_cleanup`, `force_crafted_metadata`. Key environment variables or shell state names include `bigval`, `fsdsopt`.

Requirements and feature gates: `_require_check_dmesg`, `_require_scratch_nocheck`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_unmount > /dev/null 2>&1`, `_scratch_mkfs_xfs -f $fsdsopt "$4" >> $seqres.full 2>&1`, `_scratch_xfs_set_metadata_field "$1" "$2" "$3" >> $seqres.full 2>&1`, `_try_scratch_mount >> $seqres.full 2>&1 && mounted=1`, `_scratch_sync`, `_scratch_mkfs_xfs_supported -m reflink=1 >> $seqres.full 2>&1 && \`, `_scratch_mkfs_xfs_supported -m rmapbt=1 >> $seqres.full 2>&1 && \`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is the xfstests common harness, scratch filesystem lifecycle helpers, xfsprogs commands, and golden-output filtering through `seqres.full` and `.out` files. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is environment sensitivity: missing xfsprogs features, kernel feature flags, scratch geometry, runtime load, or non-normalized diagnostics can produce false failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 520`; `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/520 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/521 -->
# sources/test-tools/xfstests/tests/xfs/521

## Purpose

Tests xfs_growfs on the realtime volume to make sure none of it blows up. This is a regression test for the following patches: xfs: Set xfs_buf type flag when growing summary/bitmap files xfs: Set xfs_buf's b_ops member when zeroing bitmap/summary files xfs: fix realtime bitmap/summary file truncation when growing rt volume xfs: make xfs_growfs_rt update secondary superblocks xfs: annotate grabbing the realtime bitmap/summary locks in growfs This is a focused xfstests shell regression. It encodes an XFS behavior, userspace-tool contract, or maintenance check as a scratch/test filesystem scenario.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto quick realtime growfs` and imports common modules: `preamble`, `filter`. Local helper functions: none Key environment variables or shell state names include `after`, `before`, `fsbsize`, `testdir`.

Requirements and feature gates: `_require_realtime`, `_require_scratch`, `_require_scratch_size $((400 * 1024))`, `_require_xfs_scratch_non_zoned`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_mkfs -r size=100m > $seqres.full`, `_scratch_mount`, `_xfs_force_bdev realtime $testdir`, `$XFS_INFO_PROG $SCRATCH_MNT >> $seqres.full`, `$XFS_GROWFS_PROG -R $((400 * 1024 * 1024 / fsbsize)) $SCRATCH_MNT 2>&1 | \`, `_scratch_cycle_mount`, `_check_scratch_fs`, `_scratch_unmount`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is the xfstests common harness, scratch filesystem lifecycle helpers, xfsprogs commands, and golden-output filtering through `seqres.full` and `.out` files. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is environment sensitivity: missing xfsprogs features, kernel feature flags, scratch geometry, runtime load, or non-normalized diagnostics can produce false failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 521`; `Format and mount 100m rt volume`; `Check rt volume stats`; `Create some files`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/521 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/522 -->
# sources/test-tools/xfstests/tests/xfs/522

## Purpose

Feed valid mkfs config files to the mkfs parser to ensure that they are recognized as valid. This is a focused xfstests shell regression. It encodes an XFS behavior, userspace-tool contract, or maintenance check as a scratch/test filesystem scenario.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto quick mkfs` and imports common modules: `preamble`, `filter`. Local helper functions: `_cleanup`, `test_mkfs_config`. Key environment variables or shell state names include `cfgfile`, `def_cfgfile`, `fsimg`, `reflink`.

Requirements and feature gates: `_require_test`, `_require_scratch_nocheck`, `_require_xfs_mkfs_cfgfile`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `$XFS_IO_PROG -c "truncate 20t" -f $fsimg`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is the xfstests common harness, scratch filesystem lifecycle helpers, xfsprogs commands, and golden-output filtering through `seqres.full` and `.out` files. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is environment sensitivity: missing xfsprogs features, kernel feature flags, scratch geometry, runtime load, or non-normalized diagnostics can produce false failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 522`; `Simplest config file`; `Piped-in config file`; `Full line comment`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/522 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/523 -->
# sources/test-tools/xfstests/tests/xfs/523

## Purpose

Feed invalid mkfs config files to the mkfs parser to ensure that they are recognized as invalid. This is a focused xfstests shell regression. It encodes an XFS behavior, userspace-tool contract, or maintenance check as a scratch/test filesystem scenario.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto quick mkfs` and imports common modules: `preamble`, `filter`. Local helper functions: `_cleanup`, `test_mkfs_config`. Key environment variables or shell state names include `cfgfile`, `def_cfgfile`, `fsimg`.

Requirements and feature gates: `_require_test`, `_require_scratch_nocheck`, `_require_xfs_mkfs_cfgfile`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `$XFS_IO_PROG -c "truncate 20t" -f $fsimg`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is the xfstests common harness, scratch filesystem lifecycle helpers, xfsprogs commands, and golden-output filtering through `seqres.full` and `.out` files. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is environment sensitivity: missing xfsprogs features, kernel feature flags, scratch geometry, runtime load, or non-normalized diagnostics can produce false failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 523`; `Spaces in a section name`; `Spaces in the middle of a key name`; `Invalid value`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/523 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/524 -->
# sources/test-tools/xfstests/tests/xfs/524

## Purpose

Test formatting with a well known config file. This is a focused xfstests shell regression. It encodes an XFS behavior, userspace-tool contract, or maintenance check as a scratch/test filesystem scenario.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto quick mkfs` and imports common modules: `preamble`, `filter`. Local helper functions: `_cleanup`. Key environment variables or shell state names include `def_cfgfile`, `fsimg`.

Requirements and feature gates: `_require_test`, `_require_scratch_nocheck`, `_require_xfs_mkfs_cfgfile`, `_require_non_zoned_device $SCRATCH_DEV`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `$XFS_IO_PROG -c "truncate 20t" -f $fsimg`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is the xfstests common harness, scratch filesystem lifecycle helpers, xfsprogs commands, and golden-output filtering through `seqres.full` and `.out` files. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is environment sensitivity: missing xfsprogs features, kernel feature flags, scratch geometry, runtime load, or non-normalized diagnostics can produce false failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 524`; `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/524 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/525 -->
# sources/test-tools/xfstests/tests/xfs/525

## Purpose

Test formatting with a config file that contains conflicting options. This is a focused xfstests shell regression. It encodes an XFS behavior, userspace-tool contract, or maintenance check as a scratch/test filesystem scenario.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto quick mkfs` and imports common modules: `preamble`, `filter`. Local helper functions: `_cleanup`. Key environment variables or shell state names include `def_cfgfile`.

Requirements and feature gates: `_require_test`, `_require_scratch_nocheck`, `_require_xfs_mkfs_cfgfile`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: The command flow is primarily ordinary shell setup and harness completion.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is the xfstests common harness, scratch filesystem lifecycle helpers, xfsprogs commands, and golden-output filtering through `seqres.full` and `.out` files. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is environment sensitivity: missing xfsprogs features, kernel feature flags, scratch geometry, runtime load, or non-normalized diagnostics can produce false failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 525`; `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/525 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/526 -->
# sources/test-tools/xfstests/tests/xfs/526

## Purpose

Test formatting with conflicts between the config file and the cli. This is a focused xfstests shell regression. It encodes an XFS behavior, userspace-tool contract, or maintenance check as a scratch/test filesystem scenario.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto quick mkfs` and imports common modules: `preamble`, `filter`. Local helper functions: `_cleanup`. Key environment variables or shell state names include `cfgfile`.

Requirements and feature gates: `_require_test`, `_require_scratch_nocheck`, `_require_xfs_mkfs_cfgfile`, `_require_xfs_nocrc`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: The command flow is primarily ordinary shell setup and harness completion.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is the xfstests common harness, scratch filesystem lifecycle helpers, xfsprogs commands, and golden-output filtering through `seqres.full` and `.out` files. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is environment sensitivity: missing xfsprogs features, kernel feature flags, scratch geometry, runtime load, or non-normalized diagnostics can produce false failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 526`; `rmapbt not supported without CRC support`; `rmapbt not supported without CRC support`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/526 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/527 -->
# sources/test-tools/xfstests/tests/xfs/527

## Purpose

Regression test for incorrect validation of ondisk dquot type flags when we're switching between group and project quotas while mounting a V4 filesystem.  This test doesn't actually force the creation of a V4 fs because even V5 filesystems ought to be able to switch between the two without triggering corruption errors. The appropriate XFS patch is: xfs: fix incorrect root dquot corruption error when switching group/project quota types unreliable_in_parallel: dmesg check can pick up corruptions from other tests. Need to filter corruption reports by short scratch dev name. This file exercises quota accounting or quota scrub behavior on XFS. It combines scratch quota mount options with block usage, reflink, CoW, or stress operations and compares kernel accounting to user-visible reports.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto quick quota unreliable_in_parallel` and imports common modules: `preamble`, `quota`. Local helper functions: none Key environment variables or shell state names include only standard xfstests variables such as `SCRATCH_MNT`, `SCRATCH_DEV`, `seqres`, and `tmp` are used

Requirements and feature gates: `_require_xfs_debug`, `_require_quota`, `_require_scratch`, `_require_check_dmesg`, `_require_prjquota $SCRATCH_DEV`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_mkfs > $seqres.full`, `$here/src/feature -G $SCRATCH_DEV || echo "group quota didn't mount?"`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is common/quota, xfs_quota reports, repquota-compatible VFS quota checks, scratch remounts, and any reflink or fsstress helpers used to generate accounting pressure. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is delayed accounting and preallocation state; tests often sync, remount, or force quotacheck so speculative CoW reservations do not look like real regressions. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 527`; `Format filesystem`; `Mount with project quota`; `Mount with group quota`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/527 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/528 -->
# sources/test-tools/xfstests/tests/xfs/528

## Purpose

Make sure that regular fallocate functions work ok when the realtime extent size is and isn't a power of 2. This is a focused xfstests shell regression. It encodes an XFS behavior, userspace-tool contract, or maintenance check as a scratch/test filesystem scenario.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto quick insert zero collapse punch rw realtime` and imports common modules: `preamble`, `filter`. Local helper functions: `check_file`, `log`, `mk_file`, `test_ops`. Key environment variables or shell state names include only standard xfstests variables such as `SCRATCH_MNT`, `SCRATCH_DEV`, `seqres`, and `tmp` are used

Requirements and feature gates: `_require_command "$FILEFRAG_PROG" filefrag`, `_require_xfs_io_command "fpunch"`, `_require_xfs_io_command "fzero"`, `_require_xfs_io_command "fcollapse"`, `_require_xfs_io_command "finsert"`, `_require_realtime`, `_require_scratch`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `$XFS_IO_PROG -f \`, `_scratch_mkfs -r extsize=$rextsize >> $seqres.full`, `_try_scratch_mount || \`, `_xfs_force_bdev realtime $SCRATCH_MNT`, `$XFS_IO_PROG -f -c "falloc 0 $sz" $SCRATCH_MNT/falloc >> $seqres.full`, `$XFS_IO_PROG -f -c "fcollapse $rextsize $rextsize" $SCRATCH_MNT/collapse >> $seqres.full`, `$XFS_IO_PROG -f -c "finsert $rextsize $rextsize" $SCRATCH_MNT/insert >> $seqres.full`, `$XFS_IO_PROG -f -c "fzero $rextsize $rextsize" $SCRATCH_MNT/zero >> $seqres.full`; plus 10 more.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is the xfstests common harness, scratch filesystem lifecycle helpers, xfsprogs commands, and golden-output filtering through `seqres.full` and `.out` files. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is environment sensitivity: missing xfsprogs features, kernel feature flags, scratch geometry, runtime load, or non-normalized diagnostics can produce false failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 528`; `Format rtextsize=262144`; `Test regular write, rextsize=262144`; `2dce060217cb2293dde96f7fdb3b9232  SCRATCH_MNT/write`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/528 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/529 -->
# sources/test-tools/xfstests/tests/xfs/529

## Purpose

Verify that XFS does not cause inode fork's extent count to overflow when adding a single extent while there's no possibility of splitting an existing mapping. This file exercises quota accounting or quota scrub behavior on XFS. It combines scratch quota mount options with block usage, reflink, CoW, or stress operations and compares kernel accounting to user-visible reports.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto quick quota prealloc` and imports common modules: `preamble`, `filter`, `quota`, `inject`, `populate`. Local helper functions: none Key environment variables or shell state names include `bsize`, `fillerdir`, `nextents`, `nr_blks`, `nr_free_blks`, `nr_quotas`, `nr_quotas_per_block`, `selector`, `testfile`.

Requirements and feature gates: `_require_scratch`, `_require_xfs_quota`, `_require_xfs_debug`, `_require_test_program "punch-alternating"`, `_require_xfs_io_command "falloc"`, `_require_xfs_io_error_injection "reduce_max_iextents"`, `_require_xfs_io_error_injection "bmap_alloc_minlen_extent"`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_mkfs_sized $((512 * 1024 * 1024)) >> $seqres.full`, `_scratch_mount -o uquota >> $seqres.full`, `_xfs_force_bdev data $SCRATCH_MNT`, `_scratch_inject_error reduce_max_iextents 1`, `$XFS_IO_PROG -f -s -c "pwrite $((i * bsize)) $bsize" $testfile \`, `nextents=$(_xfs_get_fsxattr nextents $testfile)`, `_scratch_inject_error reduce_max_iextents 0`, `$XFS_IO_PROG -f -c "falloc $((i * bsize)) $bsize" $testfile \`; plus 6 more.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is common/quota, xfs_quota reports, repquota-compatible VFS quota checks, scratch remounts, and any reflink or fsstress helpers used to generate accounting pressure. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is delayed accounting and preallocation state; tests often sync, remount, or force quotacheck so speculative CoW reservations do not look like real regressions. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 529`; `Format and mount fs`; `* Delalloc to written extent conversion`; `Inject reduce_max_iextents error tag`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/529 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/530 -->
# sources/test-tools/xfstests/tests/xfs/530

## Purpose

Verify that XFS does not cause bitmap/summary inode fork's extent count to overflow when growing an the realtime volume of the filesystem. This is a focused xfstests shell regression. It encodes an XFS behavior, userspace-tool contract, or maintenance check as a scratch/test filesystem scenario.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto quick realtime growfs` and imports common modules: `preamble`, `filter`, `inject`, `populate`. Local helper functions: none Key environment variables or shell state names include `fillerdir`, `formatted_blksz`, `fsbsize`, `nextents`, `nr_bitmap_blks`, `nr_bits`, `nr_free_blks`, `rtdevsz`, `rtextsz`, `selector`.

Requirements and feature gates: `_require_scratch`, `_require_realtime`, `_require_xfs_debug`, `_require_test_program "punch-alternating"`, `_require_xfs_io_error_injection "reduce_max_iextents"`, `_require_xfs_io_error_injection "bmap_alloc_minlen_extent"`, `_require_xfs_has_feature "$SCRATCH_MNT" realtime`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_mkfs | _filter_mkfs >> $seqres.full 2> $tmp.mkfs`, `_try_scratch_mkfs_xfs \`, `_try_scratch_mount || _notrun "Couldn't mount crafted fs"`, `$here/src/punch-alternating $fillerdir/$dentry >> $seqres.full`, `_scratch_inject_error reduce_max_iextents 1`, `_scratch_inject_error bmap_alloc_minlen_extent 1`, `$XFS_GROWFS_PROG -R $((rtdevsize / fsbsize)) $SCRATCH_MNT \`, `_scratch_unmount >> $seqres.full`; plus 4 more.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is the xfstests common harness, scratch filesystem lifecycle helpers, xfsprogs commands, and golden-output filtering through `seqres.full` and `.out` files. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is environment sensitivity: missing xfsprogs features, kernel feature flags, scratch geometry, runtime load, or non-normalized diagnostics can produce false failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 530`; `* Test extending rt inodes`; `Format and mount rt volume`; `Consume free space`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/530 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/531 -->
# sources/test-tools/xfstests/tests/xfs/531

## Purpose

Verify that XFS does not cause inode fork's extent count to overflow when punching out an extent. This is a focused xfstests shell regression. It encodes an XFS behavior, userspace-tool contract, or maintenance check as a scratch/test filesystem scenario.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto quick punch zero insert collapse` and imports common modules: `preamble`, `filter`, `inject`. Local helper functions: none Key environment variables or shell state names include `bsize`, `nextents`, `nr_blks`, `testfile`.

Requirements and feature gates: `_require_scratch`, `_require_xfs_debug`, `_require_xfs_io_command "fpunch"`, `_require_xfs_io_command "finsert"`, `_require_xfs_io_command "fcollapse"`, `_require_xfs_io_command "fzero"`, `_require_xfs_io_error_injection "reduce_max_iextents"`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_mkfs >> $seqres.full`, `_scratch_mount >> $seqres.full`, `_scratch_inject_error reduce_max_iextents 1`, `$XFS_IO_PROG -f -s \`, `$XFS_IO_PROG -f -c "$op $((i * bsize)) $bsize" $testfile \`, `nextents=$(_xfs_get_fsxattr nextents $testfile)`, `_scratch_inject_error reduce_max_iextents 0`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is the xfstests common harness, scratch filesystem lifecycle helpers, xfsprogs commands, and golden-output filtering through `seqres.full` and `.out` files. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is environment sensitivity: missing xfsprogs features, kernel feature flags, scratch geometry, runtime load, or non-normalized diagnostics can produce false failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 531`; `Format and mount fs`; `* fpunch regular file`; `Create $testfile`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/531 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/532 -->
# sources/test-tools/xfstests/tests/xfs/532

## Purpose

Verify that XFS does not cause inode fork's extent count to overflow when adding/removing xattrs. This is a focused xfstests shell regression. It encodes an XFS behavior, userspace-tool contract, or maintenance check as a scratch/test filesystem scenario.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto quick attr` and imports common modules: `preamble`, `filter`, `attr`, `inject`, `populate`. Local helper functions: none Key environment variables or shell state names include `attr`, `attr_len`, `bsize`, `end`, `fillerdir`, `last`, `naextents`, `nr_attrs`, `nr_free_blks`, `start`; plus 1 more.

Requirements and feature gates: `_require_scratch`, `_require_attrs`, `_require_xfs_debug`, `_require_test_program "punch-alternating"`, `_require_xfs_io_error_injection "reduce_max_iextents"`, `_require_xfs_io_error_injection "bmap_alloc_minlen_extent"`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_mkfs_sized $((1024 * 1024 * 1024)) >> $seqres.full`, `_scratch_mount >> $seqres.full`, `_xfs_force_bdev data $SCRATCH_MNT`, `$here/src/punch-alternating $fillerdir/$dentry >> $seqres.full`, `_scratch_inject_error bmap_alloc_minlen_extent 1`, `_scratch_inject_error reduce_max_iextents 1`, `naextents=$(_xfs_get_fsxattr naextents $testfile)`, `_scratch_inject_error reduce_max_iextents 0`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is the xfstests common harness, scratch filesystem lifecycle helpers, xfsprogs commands, and golden-output filtering through `seqres.full` and `.out` files. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is environment sensitivity: missing xfsprogs features, kernel feature flags, scratch geometry, runtime load, or non-normalized diagnostics can produce false failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 532`; `Format and mount fs`; `Consume free space`; `Create fragmented filesystem`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/532 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/533 -->
# sources/test-tools/xfstests/tests/xfs/533

## Purpose

Regression test for xfsprogs commit f4afdcb0ad11 ("xfs_db: clean up the salvage read callsites in set_cur()") This case test xfs_db whether can get the new magicnum field value even we just have corrupted this field value. This is a focused xfstests shell regression. It encodes an XFS behavior, userspace-tool contract, or maintenance check as a scratch/test filesystem scenario.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto quick db` and imports common modules: `preamble`. Local helper functions: none Key environment variables or shell state names include only standard xfstests variables such as `SCRATCH_MNT`, `SCRATCH_DEV`, `seqres`, and `tmp` are used

Requirements and feature gates: `_require_scratch_nocheck`, `_require_scratch_xfs_crc`. Recorded fix annotations: `_fixed_by_git_commit xfsprogs f4afdcb0ad11 xfs_db: clean up the salvage read callsites in set_cur()`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `"xfs_db: clean up the salvage read callsites in set_cur()"`, `_scratch_mkfs_xfs >>$seqres.full 2>&1`, `_scratch_xfs_set_metadata_field "magicnum" "0" "sb 1"`, `_scratch_xfs_get_metadata_field "magicnum" "sb 1" 2>&1 | \`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is the xfstests common harness, scratch filesystem lifecycle helpers, xfsprogs commands, and golden-output filtering through `seqres.full` and `.out` files. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is environment sensitivity: missing xfsprogs features, kernel feature flags, scratch geometry, runtime load, or non-normalized diagnostics can produce false failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 533`; `Allowing write of corrupted data with good CRC`; `magicnum = 0`; `bad magic number`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/533 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/534 -->
# sources/test-tools/xfstests/tests/xfs/534

## Purpose

Verify that XFS does not cause inode fork's extent count to overflow when writing to an unwritten extent. This is a focused xfstests shell regression. It encodes an XFS behavior, userspace-tool contract, or maintenance check as a scratch/test filesystem scenario.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto quick prealloc` and imports common modules: `preamble`, `filter`, `inject`. Local helper functions: none Key environment variables or shell state names include `bsize`, `nextents`, `nr_blks`, `testfile`, `xfs_io_flag`.

Requirements and feature gates: `_require_scratch`, `_require_xfs_debug`, `_require_xfs_io_command "falloc"`, `_require_xfs_io_error_injection "reduce_max_iextents"`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_mkfs_sized $((1024 * 1024 * 1024)) >> $seqres.full`, `_scratch_mount >> $seqres.full`, `$XFS_IO_PROG -f -c "falloc 0 $((nr_blks * bsize))" $testfile >> $seqres.full`, `xfs_io_flag=""`, `xfs_io_flag="-d"`, `_scratch_inject_error reduce_max_iextents 1`, `$XFS_IO_PROG -f -s $xfs_io_flag -c "pwrite $((i * bsize)) $bsize" \`, `nextents=$(_xfs_get_fsxattr nextents $testfile)`; plus 1 more.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is the xfstests common harness, scratch filesystem lifecycle helpers, xfsprogs commands, and golden-output filtering through `seqres.full` and `.out` files. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is environment sensitivity: missing xfsprogs features, kernel feature flags, scratch geometry, runtime load, or non-normalized diagnostics can produce false failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 534`; `Format and mount fs`; `* Buffered write to unwritten extent`; `Fallocate 15 blocks`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/534 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/535 -->
# sources/test-tools/xfstests/tests/xfs/535

## Purpose

Verify that XFS does not cause inode fork's extent count to overflow when writing to a shared extent. This is a focused xfstests shell regression. It encodes an XFS behavior, userspace-tool contract, or maintenance check as a scratch/test filesystem scenario.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto quick clone unshare` and imports common modules: `preamble`, `filter`, `reflink`, `inject`. Local helper functions: none Key environment variables or shell state names include `bsize`, `dstfile`, `nextents`, `nr_blks`, `srcfile`.

Requirements and feature gates: `_require_scratch`, `_require_scratch_reflink`, `_require_xfs_debug`, `_require_xfs_io_command "reflink"`, `_require_xfs_io_command "funshare"`, `_require_xfs_io_error_injection "reduce_max_iextents"`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_mkfs_sized $((512 * 1024 * 1024)) >> $seqres.full`, `_scratch_mount >> $seqres.full`, `_scratch_inject_error reduce_max_iextents 1`, `$XFS_IO_PROG -f -c "pwrite -b $((nr_blks * bsize)) 0 $((nr_blks * bsize))" \`, `$XFS_IO_PROG -f -s -c "pwrite $((i * bsize)) $bsize" $dstfile \`, `nextents=$(_xfs_get_fsxattr nextents $dstfile)`, `_scratch_inject_error reduce_max_iextents 0`, `$XFS_IO_PROG -f -s -c "funshare $((i * bsize)) $bsize" $dstfile \`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is the xfstests common harness, scratch filesystem lifecycle helpers, xfsprogs commands, and golden-output filtering through `seqres.full` and `.out` files. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is environment sensitivity: missing xfsprogs features, kernel feature flags, scratch geometry, runtime load, or non-normalized diagnostics can produce false failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 535`; `Format and mount fs`; `Inject reduce_max_iextents error tag`; `Create a $srcfile having an extent of length 15 blocks`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/535 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/536 -->
# sources/test-tools/xfstests/tests/xfs/536

## Purpose

Verify that XFS does not cause inode fork's extent count to overflow when remapping extents from one file's inode fork to another. This is a focused xfstests shell regression. It encodes an XFS behavior, userspace-tool contract, or maintenance check as a scratch/test filesystem scenario.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto quick clone` and imports common modules: `preamble`, `filter`, `reflink`, `inject`. Local helper functions: none Key environment variables or shell state names include `bsize`, `dstfile`, `nextents`, `nr_blks`, `srcfile`.

Requirements and feature gates: `_require_scratch`, `_require_scratch_reflink`, `_require_xfs_debug`, `_require_xfs_io_command "reflink"`, `_require_xfs_io_error_injection "reduce_max_iextents"`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_mkfs >> $seqres.full`, `_scratch_mount >> $seqres.full`, `$XFS_IO_PROG -f -c "pwrite -b $((nr_blks * bsize)) 0 $((nr_blks * bsize))" \`, `_scratch_inject_error reduce_max_iextents 1`, `nextents=$(_xfs_get_fsxattr nextents $dstfile)`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is the xfstests common harness, scratch filesystem lifecycle helpers, xfsprogs commands, and golden-output filtering through `seqres.full` and `.out` files. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is environment sensitivity: missing xfsprogs features, kernel feature flags, scratch geometry, runtime load, or non-normalized diagnostics can produce false failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 536`; `* Reflink remap extents`; `Format and mount fs`; `Create $srcfile having an extent of length 15 blocks`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/536 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/537 -->
# sources/test-tools/xfstests/tests/xfs/537

## Purpose

Verify that XFS does not cause inode fork's extent count to overflow when swapping forks between files This is a focused xfstests shell regression. It encodes an XFS behavior, userspace-tool contract, or maintenance check as a scratch/test filesystem scenario.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto quick collapse swapext` and imports common modules: `preamble`, `filter`, `inject`. Local helper functions: none Key environment variables or shell state names include `bsize`, `donor_nr_exts`, `donorfile`, `nextents`, `src_nr_exts`, `srcfile`, `start_offset`.

Requirements and feature gates: `_require_scratch`, `_require_xfs_debug`, `_require_xfs_scratch_rmapbt`, `_require_xfs_io_command "fcollapse"`, `_require_xfs_io_command "swapext"`, `_require_xfs_io_error_injection "reduce_max_iextents"`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_mkfs >> $seqres.full`, `_scratch_mount >> $seqres.full`, `$XFS_IO_PROG -f -s -c "pwrite -b $((17 * bsize)) 0 $((17 * bsize))" $donorfile \`, `$XFS_IO_PROG -f -c "fcollapse $start_offset $bsize" $donorfile >> $seqres.full`, `$XFS_IO_PROG -f -s -c "pwrite -b $((18 * bsize)) 0 $((18 * bsize))" $srcfile \`, `$XFS_IO_PROG -f -c "fcollapse $start_offset $bsize" $srcfile >> $seqres.full`, `donor_nr_exts=$(_xfs_get_fsxattr nextents $donorfile)`, `src_nr_exts=$(_xfs_get_fsxattr nextents $srcfile)`; plus 4 more.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is the xfstests common harness, scratch filesystem lifecycle helpers, xfsprogs commands, and golden-output filtering through `seqres.full` and `.out` files. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is environment sensitivity: missing xfsprogs features, kernel feature flags, scratch geometry, runtime load, or non-normalized diagnostics can produce false failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 537`; `* Swap extent forks`; `Format and mount fs`; `Create $donorfile having an extent of length 67 blocks`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/537 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/538 -->
# sources/test-tools/xfstests/tests/xfs/538

## Purpose

Execute fsstress with bmap_alloc_minlen_extent error tag enabled. This is a focused xfstests shell regression. It encodes an XFS behavior, userspace-tool contract, or maintenance check as a scratch/test filesystem scenario.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto stress` and imports common modules: `preamble`, `filter`, `inject`, `populate`. Local helper functions: none Key environment variables or shell state names include `bsize`, `fillerdir`, `nr_free_blks`.

Requirements and feature gates: `_require_scratch`, `_require_xfs_debug`, `_require_test_program "punch-alternating"`, `_require_xfs_io_error_injection "bmap_alloc_minlen_extent"`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_mkfs_sized $((1024 * 1024 * 1024)) >> $seqres.full`, `_scratch_mount >> $seqres.full`, `_xfs_force_bdev data $SCRATCH_MNT`, `$here/src/punch-alternating $fillerdir/$dentry >> $seqres.full`, `_scratch_inject_error bmap_alloc_minlen_extent 1`, `echo "Execute fsstress"`, `_run_fsstress -d $SCRATCH_MNT \`, `$(_scale_fsstress_args -p 75 -n 1000) \`; plus 2 more.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is the xfstests common harness, scratch filesystem lifecycle helpers, xfsprogs commands, and golden-output filtering through `seqres.full` and `.out` files. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is environment sensitivity: missing xfsprogs features, kernel feature flags, scratch geometry, runtime load, or non-normalized diagnostics can produce false failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 538`; `Format and mount fs`; `Consume free space`; `Create fragmented filesystem`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/538 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/540 -->
# sources/test-tools/xfstests/tests/xfs/540

## Purpose

Functional test for xfsprogs commit: 5f062427 ("xfs_repair: validate alignment of inherited rt extent hints") This xfs_repair patch detects directories that are configured to propagate their realtime and extent size hints to newly created realtime files when the hint size isn't aligned to the size of a realtime extent. Since this is a test of userspace tool functionality, we don't need kernel support, which in turn means that we omit _require_realtime.  Note that XFS allows users to configure realtime extent size geometry and set RTINHERIT flags even if the filesystem itself does not have a realtime volume attached. This file is a targeted corruption regression. It creates a scratch filesystem, mutates a precise XFS metadata field or structure, and then relies on mount, scrub, repair, or verifier behavior to prove the bug stays fixed.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto repair fuzzers` and imports common modules: `preamble`, `filter`. Local helper functions: none Key environment variables or shell state names include `rootino`, `rtextsz_blks`.

Requirements and feature gates: `_require_scratch`, `_require_xfs_scratch_non_zoned`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_mkfs_xfs -r extsize=7b | _filter_mkfs > $seqres.full 2>$tmp.mkfs`, `_scratch_mount >> $seqres.full 2>&1`, `_scratch_unmount`, `_scratch_xfs_set_metadata_field core.extsize $((rtextsz_blks + 1)) "inode $rootino" >> $seqres.full`, `_scratch_xfs_set_metadata_field core.rtinherit 1 "inode $rootino" >> $seqres.full`, `_scratch_xfs_set_metadata_field core.extszinherit 1 "inode $rootino" >> $seqres.full`, `_scratch_xfs_db -x -c "inode $rootino" -c 'print' >> $seqres.full`, `_scratch_xfs_repair -n >> $seqres.full 2>&1 && \`; plus 1 more.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is xfs_db metadata reads/writes, common/fuzzy helpers, scratch mount cycles, and xfstests filters that normalize expected diagnostics. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is tight coupling to on-disk format details; feature gates, block-size calculations, and expected verifier messages must track XFS format changes. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 540`; `Format and mount`; `Misconfigure the root directory`; `Detect misconfigured directory`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/540 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/541 -->
# sources/test-tools/xfstests/tests/xfs/541

## Purpose

Regression test for kernel commits: 83193e5ebb01 ("xfs: correct the narrative around misaligned rtinherit/extszinherit dirs") 5aa5b278237f ("xfs: don't expose misaligned extszinherit hints to userspace") 0e2af9296f4f ("xfs: improve FSGROWFSRT precondition checking") 0925fecc5574 ("xfs: fix an integer overflow error in xfs_growfs_rt") b102a46ce16f ("xfs: detect misaligned rtinherit directory extent size hints") Test for xfs_growfs to make sure that we can add a realtime device and set its extent size hint at the same time. This is a focused xfstests shell regression. It encodes an XFS behavior, userspace-tool contract, or maintenance check as a scratch/test filesystem scenario.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto quick realtime growfs` and imports common modules: `preamble`, `filter`. Local helper functions: none Key environment variables or shell state names include `SCRATCH_RTDEV`, `XFS_MAX_RTEXTSIZE`, `after_extszhint`, `after_rtextsz_blocks`, `file_extszhint`, `grow_extszhint`, `new_extszhint`, `new_rtextsz`, `new_rtextsz_blocks`, `res`; plus 1 more.

Requirements and feature gates: `_require_realtime`, `_require_scratch`, `_require_xfs_scratch_non_zoned`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `SCRATCH_RTDEV="" _scratch_mkfs | _filter_mkfs 2> $tmp.mkfs >> $seqres.full`, `_try_scratch_mount || _notrun "Can't mount file system"`, `if [ $new_rtextsz -gt $XFS_MAX_RTEXTSIZE ]; then`, `$XFS_IO_PROG -c 'chattr +t' -c "extsize $new_extszhint" $SCRATCH_MNT`, `after_extszhint=$($XFS_IO_PROG -c 'stat' $SCRATCH_MNT | \`, `echo $XFS_GROWFS_PROG -e $new_rtextsz_blocks -r $SCRATCH_MNT >> $seqres.full`, `$XFS_GROWFS_PROG -e $new_rtextsz_blocks -r $SCRATCH_MNT >> $seqres.full 2> $tmp.growfs`, `grow_extszhint=$($XFS_IO_PROG -c 'stat' $SCRATCH_MNT | \`; plus 5 more.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is the xfstests common harness, scratch filesystem lifecycle helpers, xfsprogs commands, and golden-output filtering through `seqres.full` and `.out` files. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is environment sensitivity: missing xfsprogs features, kernel feature flags, scratch geometry, runtime load, or non-normalized diagnostics can produce false failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 541`; `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/541 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/542 -->
# sources/test-tools/xfstests/tests/xfs/542

## Purpose

Test that COW writeback that overlaps non-shared delalloc blocks does not leave around stale delalloc blocks on I/O failure. This triggers assert failures and free space accounting corruption on XFS. Fixed by upstream kernel commit 5ca5916b6bc9 ("xfs: punch out data fork delalloc blocks on COW writeback failure"). This is a focused xfstests shell regression. It encodes an XFS behavior, userspace-tool contract, or maintenance check as a scratch/test filesystem scenario.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto quick clone` and imports common modules: `preamble`, `reflink`, `dmflakey`. Local helper functions: `_cleanup`. Key environment variables or shell state names include `blksz`, `len`.

Requirements and feature gates: `_require_scratch_reflink`, `_require_cp_reflink`, `_require_xfs_io_command "cowextsize"`, `_require_flakey_with_error_writes`. Recorded fix annotations: `_fixed_by_kernel_commit 5ca5916b6bc9 xfs: punch out data fork delalloc blocks on COW writeback failure`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_mkfs >> $seqres.full`, `_scratch_mount`, `$XFS_IO_PROG -c "cowextsize $((blksz * 2))" $SCRATCH_MNT >> $seqres.full`, `$XFS_IO_PROG -fc "pwrite $blksz $blksz" $SCRATCH_MNT/file1 >> $seqres.full`, `$XFS_IO_PROG -fc "reflink $SCRATCH_MNT/file1" \`, `$XFS_IO_PROG -c "pwrite 0 $len" \`, `_scratch_unmount`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is the xfstests common harness, scratch filesystem lifecycle helpers, xfsprogs commands, and golden-output filtering through `seqres.full` and `.out` files. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is environment sensitivity: missing xfsprogs features, kernel feature flags, scratch geometry, runtime load, or non-normalized diagnostics can produce false failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 542`; `sync_file_range: Input/output error`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/542 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/543 -->
# sources/test-tools/xfstests/tests/xfs/543

## Purpose

Regression test for xfsprogs commit: 99c78777 ("mkfs: prevent corruption of passed-in suboption string values") This is a focused xfstests shell regression. It encodes an XFS behavior, userspace-tool contract, or maintenance check as a scratch/test filesystem scenario.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto quick mkfs` and imports common modules: `preamble`. Local helper functions: `_cleanup`. Key environment variables or shell state names include `cfgfile`, `options`, `size`, `su`, `sw`.

Requirements and feature gates: `_require_test`, `_require_xfs_mkfs_cfgfile`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `$XFS_IO_PROG -f -c "truncate 1g" $TEST_DIR/fubar.img`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is the xfstests common harness, scratch filesystem lifecycle helpers, xfsprogs commands, and golden-output filtering through `seqres.full` and `.out` files. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is environment sensitivity: missing xfsprogs features, kernel feature flags, scratch geometry, runtime load, or non-normalized diagnostics can produce false failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 543`; `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/543 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/544 -->
# sources/test-tools/xfstests/tests/xfs/544

## Purpose

Regression test for commit: 0717c1c ("xfsdump: intercept bind mount targets") This is a focused xfstests shell regression. It encodes an XFS behavior, userspace-tool contract, or maintenance check as a scratch/test filesystem scenario.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto quick dump` and imports common modules: `preamble`, `filter`, `dump`. Local helper functions: `_cleanup`. Key environment variables or shell state names include only standard xfstests variables such as `SCRATCH_MNT`, `SCRATCH_DEV`, `seqres`, and `tmp` are used

Requirements and feature gates: No explicit `_require_*` gates are present beyond the harness defaults.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: The command flow is primarily ordinary shell setup and harness completion.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is the xfstests common harness, scratch filesystem lifecycle helpers, xfsprogs commands, and golden-output filtering through `seqres.full` and `.out` files. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is environment sensitivity: missing xfsprogs features, kernel feature flags, scratch geometry, runtime load, or non-normalized diagnostics can produce false failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 544`; `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/544 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/545 -->
# sources/test-tools/xfstests/tests/xfs/545

## Purpose

Create a filesystem which contains an inode with a lower number than the root inode. Ensure that xfsdump/xfsrestore handles this. This is a focused xfstests shell regression. It encodes an XFS behavior, userspace-tool contract, or maintenance check as a scratch/test filesystem scenario.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto quick dump prealloc` and imports common modules: `preamble`, `dump`. Local helper functions: none Key environment variables or shell state names include `fake_inum`, `inums`, `root_inum`.

Requirements and feature gates: `_require_xfs_io_command "falloc"`, `_require_scratch`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `inums=($(_scratch_xfs_create_fake_root))`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is the xfstests common harness, scratch filesystem lifecycle helpers, xfsprogs commands, and golden-output filtering through `seqres.full` and `.out` files. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is environment sensitivity: missing xfsprogs features, kernel feature flags, scratch geometry, runtime load, or non-normalized diagnostics can produce false failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 545`; `Creating directory system to dump using fsstress.`; `-----------------------------------------------`; `fsstress : -f link=10 -f creat=10 -f mkdir=10 -f truncate=5 -f symlink=10`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/545 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/546 -->
# sources/test-tools/xfstests/tests/xfs/546

## Purpose

Regression test for kernel commits: 5679897eb104 ("vfs: make sync_filesystem return errors from ->sync_fs") 2d86293c7075 ("xfs: return errors in xfs_fs_sync_fs") During a code inspection, I noticed that sync_filesystem ignores the return value of the ->sync_fs calls that it makes.  sync_filesystem, in turn is used by the syncfs(2) syscall to persist filesystem changes to disk.  This means that syncfs(2) does not capture internal filesystem errors that are neither visible from the block device (e.g. media error) nor recorded in s_wb_err. XFS historically returned 0 from ->sync_fs even if there were log failures, so that had to be corrected as well. The kernel commits above fix this problem, so this test tries to trigger the bug by using the shutdown ioctl on a clean, freshly mounted filesystem in the hope that the EIO generated as a result of the filesystem being shut down is only visible via ->sync_fs. This is a focused xfstests shell regression. It encodes an XFS behavior, userspace-tool contract, or maintenance check as a scratch/test filesystem scenario.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto quick shutdown` and imports common modules: `preamble`. Local helper functions: none Key environment variables or shell state names include only standard xfstests variables such as `SCRATCH_MNT`, `SCRATCH_DEV`, `seqres`, and `tmp` are used

Requirements and feature gates: `_require_scratch_nocheck`, `_require_scratch_shutdown_and_syncfs`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_mount`, `_scratch_shutdown_and_syncfs`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is the xfstests common harness, scratch filesystem lifecycle helpers, xfsprogs commands, and golden-output filtering through `seqres.full` and `.out` files. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is environment sensitivity: missing xfsprogs features, kernel feature flags, scratch geometry, runtime load, or non-normalized diagnostics can produce false failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 546`; `syncfs: Input/output error`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/546 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/547 -->
# sources/test-tools/xfstests/tests/xfs/547

## Purpose

Verify that correct inode extent count fields are populated with and without nrext64 feature. This is a focused xfstests shell regression. It encodes an XFS behavior, userspace-tool contract, or maintenance check as a scratch/test filesystem scenario.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto quick metadata` and imports common modules: `preamble`, `filter`, `attr`, `inject`, `populate`. Local helper functions: none Key environment variables or shell state names include `MKFS_OPTIONS`, `acnt`, `attr`, `attr_len`, `bsize`, `dcnt`, `fillerdir`, `fs_size`, `nr_attrs`, `nr_blks`; plus 2 more.

Requirements and feature gates: `_require_scratch`, `_require_xfs_nrext64`, `_require_attrs`, `_require_xfs_debug`, `_require_xfs_db_command path`, `_require_test_program "punch-alternating"`, `_require_xfs_io_error_injection "bmap_alloc_minlen_extent"`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `MKFS_OPTIONS="-i nrext64=${nrext64} $MKFS_OPTIONS" _scratch_mkfs_sized $fs_size \`, `_scratch_mount >> $seqres.full`, `_xfs_force_bdev data $SCRATCH_MNT`, `$XFS_IO_PROG -f -c "pwrite 0 $((nr_blks * bsize))" $testfile \`, `$here/src/punch-alternating $testfile`, `$here/src/punch-alternating $fillerdir/$dentry >> $seqres.full`, `_scratch_inject_error bmap_alloc_minlen_extent 1`, `_scratch_unmount >> $seqres.full`; plus 2 more.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is the xfstests common harness, scratch filesystem lifecycle helpers, xfsprogs commands, and golden-output filtering through `seqres.full` and `.out` files. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is environment sensitivity: missing xfsprogs features, kernel feature flags, scratch geometry, runtime load, or non-normalized diagnostics can produce false failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 547`; `* Verify extent counter fields with nrext64=0 option`; `Add blocks to test file's data fork`; `Consume free space`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/547 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/548 -->
# sources/test-tools/xfstests/tests/xfs/548

## Purpose

Test to verify upgrade of an existing V5 filesystem to support large extent counters. This is a focused xfstests shell regression. It encodes an XFS behavior, userspace-tool contract, or maintenance check as a scratch/test filesystem scenario.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto quick metadata` and imports common modules: `preamble`, `filter`, `attr`, `inject`, `populate`. Local helper functions: none Key environment variables or shell state names include `acnt`, `attr`, `attr_len`, `bsize`, `dcnt`, `fillerdir`, `nr_attrs`, `nr_blks`, `nr_free_blks`, `orig_acnt`; plus 2 more.

Requirements and feature gates: `_require_scratch`, `_require_xfs_nrext64`, `_require_attrs`, `_require_xfs_debug`, `_require_xfs_db_command path`, `_require_test_program "punch-alternating"`, `_require_xfs_io_error_injection "bmap_alloc_minlen_extent"`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_mkfs_sized $((512 * 1024 * 1024)) >> $seqres.full`, `_scratch_mount >> $seqres.full`, `$XFS_IO_PROG -f -c "pwrite 0 $((nr_blks * bsize))" $testfile \`, `$here/src/punch-alternating $testfile`, `$here/src/punch-alternating $fillerdir/$dentry >> $seqres.full`, `_scratch_inject_error bmap_alloc_minlen_extent 1`, `_scratch_unmount >> $seqres.full`, `orig_dcnt=$(_scratch_xfs_get_metadata_field core.nextents \`; plus 4 more.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is the xfstests common harness, scratch filesystem lifecycle helpers, xfsprogs commands, and golden-output filtering through `seqres.full` and `.out` files. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is environment sensitivity: missing xfsprogs features, kernel feature flags, scratch geometry, runtime load, or non-normalized diagnostics can produce false failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 548`; `Add blocks to file's data fork`; `Consume free space`; `Create fragmented filesystem`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/548 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/549 -->
# sources/test-tools/xfstests/tests/xfs/549

## Purpose

Regression test for xfsprogs commit 50dba8189b1f ("mkfs: terminate getsubopt arrays properly") This case test mkfs.xfs whether can terminate getsubopt arrays properly. If not, it will trigger segmentation fault. This is a focused xfstests shell regression. It encodes an XFS behavior, userspace-tool contract, or maintenance check as a scratch/test filesystem scenario.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto quick mkfs` and imports common modules: `preamble`. Local helper functions: none Key environment variables or shell state names include only standard xfstests variables such as `SCRATCH_MNT`, `SCRATCH_DEV`, `seqres`, and `tmp` are used

Requirements and feature gates: `_require_test`. Recorded fix annotations: `_fixed_by_git_commit xfsprogs 50dba8189b1f mkfs: terminate getsubopt arrays properly`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: The command flow is primarily ordinary shell setup and harness completion.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is the xfstests common harness, scratch filesystem lifecycle helpers, xfsprogs commands, and golden-output filtering through `seqres.full` and `.out` files. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is environment sensitivity: missing xfsprogs features, kernel feature flags, scratch geometry, runtime load, or non-normalized diagnostics can produce false failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 549`; `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/549 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/550 -->
# sources/test-tools/xfstests/tests/xfs/550

## Purpose

Test memory failure mechanism when dax enabled This is a focused xfstests shell regression. It encodes an XFS behavior, userspace-tool contract, or maintenance check as a scratch/test filesystem scenario.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto quick dax mmap` and imports common modules: `preamble`, `filter`, `reflink`. Local helper functions: none Key environment variables or shell state names include `filesize`, `testdir`.

Requirements and feature gates: `_require_check_dmesg`, `_require_scratch_reflink`, `_require_cp_reflink`, `_require_xfs_scratch_rmapbt`, `_require_scratch_dax_mountopt "dax"`, `_require_test_program "t_mmap_cow_memory_failure"`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_mkfs > $seqres.full 2>&1`, `_scratch_mount "-o dax" >> $seqres.full 2>&1`, `_scratch_cycle_mount "dax"`, `$here/src/t_mmap_cow_memory_failure -s1 -S1 -R $testdir/testfile -P $testdir/testfile`, `$here/src/t_mmap_cow_memory_failure -s2 -S2 -R $testdir/testfile -P $testdir/testfile`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is the xfstests common harness, scratch filesystem lifecycle helpers, xfsprogs commands, and golden-output filtering through `seqres.full` and `.out` files. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is environment sensitivity: missing xfsprogs features, kernel feature flags, scratch geometry, runtime load, or non-normalized diagnostics can produce false failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 550`; `Format and mount`; `Create the original files`; `Inject memory failure (1 page)`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/550 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/551 -->
# sources/test-tools/xfstests/tests/xfs/551

## Purpose

Test memory failure mechanism when dax and reflink working together This is a focused xfstests shell regression. It encodes an XFS behavior, userspace-tool contract, or maintenance check as a scratch/test filesystem scenario.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto quick clone dax mmap` and imports common modules: `preamble`, `filter`, `reflink`. Local helper functions: none Key environment variables or shell state names include `filesize`, `testdir`.

Requirements and feature gates: `_require_check_dmesg`, `_require_scratch_reflink`, `_require_cp_reflink`, `_require_xfs_scratch_rmapbt`, `_require_scratch_dax_mountopt "dax"`, `_require_test_program "t_mmap_cow_memory_failure"`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_mkfs > $seqres.full 2>&1`, `_scratch_mount "-o dax" >> $seqres.full 2>&1`, `_scratch_cycle_mount "dax"`, `$here/src/t_mmap_cow_memory_failure -s1 -S1 -R $testdir/testfile -P $testdir/poisonfile`, `$here/src/t_mmap_cow_memory_failure -s2 -S2 -R $testdir/testfile -P $testdir/poisonfile`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is the xfstests common harness, scratch filesystem lifecycle helpers, xfsprogs commands, and golden-output filtering through `seqres.full` and `.out` files. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is environment sensitivity: missing xfsprogs features, kernel feature flags, scratch geometry, runtime load, or non-normalized diagnostics can produce false failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 551`; `Format and mount`; `Create the original files`; `Inject memory failure (1 page)`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/551 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/552 -->
# sources/test-tools/xfstests/tests/xfs/552

## Purpose

Test memory failure mechanism when dax and reflink working together test for partly reflinked file This is a focused xfstests shell regression. It encodes an XFS behavior, userspace-tool contract, or maintenance check as a scratch/test filesystem scenario.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto quick clone dax mmap` and imports common modules: `preamble`, `filter`, `reflink`. Local helper functions: none Key environment variables or shell state names include `blksz`, `nr`, `testdir`.

Requirements and feature gates: `_require_check_dmesg`, `_require_scratch_reflink`, `_require_xfs_scratch_rmapbt`, `_require_scratch_dax_mountopt "dax"`, `_require_test_program "t_mmap_cow_memory_failure"`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_mkfs > $seqres.full 2>&1`, `_scratch_mount "-o dax" >> $seqres.full 2>&1`, `_scratch_cycle_mount "dax"`, `$here/src/t_mmap_cow_memory_failure -s1 -S1 -R $testdir/testfile -P $testdir/poisonfile`, `$here/src/t_mmap_cow_memory_failure -s2 -S2 -R $testdir/testfile -P $testdir/poisonfile`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is the xfstests common harness, scratch filesystem lifecycle helpers, xfsprogs commands, and golden-output filtering through `seqres.full` and `.out` files. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is environment sensitivity: missing xfsprogs features, kernel feature flags, scratch geometry, runtime load, or non-normalized diagnostics can produce false failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 552`; `Format and mount`; `Create the original files`; `Inject memory failure (1 page)`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/552 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/553 -->
# sources/test-tools/xfstests/tests/xfs/553

## Purpose

Test to check if a direct write on a delalloc extent present in CoW fork can result in an ENOSPC error. This is a focused xfstests shell regression. It encodes an XFS behavior, userspace-tool contract, or maintenance check as a scratch/test filesystem scenario.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto quick clone` and imports common modules: `preamble`, `reflink`, `inject`. Local helper functions: none Key environment variables or shell state names include `blksz`, `destination`, `fragmented_file`, `source`.

Requirements and feature gates: `_require_scratch_reflink`, `_require_xfs_debug`, `_require_test_program "punch-alternating"`, `_require_xfs_io_error_injection "bmap_alloc_minlen_extent"`, `_require_xfs_io_command "reflink"`, `_require_xfs_io_command "cowextsize"`. Recorded fix annotations: `_fixed_by_kernel_commit d62113303d691 xfs: Fix false ENOSPC when performing direct write on a delalloc extent in cow fork`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_mkfs >> $seqres.full`, `_scratch_mount >> $seqres.full`, `$XFS_IO_PROG -f -c "pwrite 0 $((blksz * 8192))" $source >> $seqres.full`, `$XFS_IO_PROG -f -c "reflink $source" $destination >> $seqres.full`, `$XFS_IO_PROG -c "cowextsize $((blksz * 4096))" $destination >> $seqres.full`, `$XFS_IO_PROG -f -c "pwrite 0 $((blksz * 16384))" $fragmented_file \`, `_scratch_sync`, `$here/src/punch-alternating $fragmented_file >> $seqres.full`; plus 3 more.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is the xfstests common harness, scratch filesystem lifecycle helpers, xfsprogs commands, and golden-output filtering through `seqres.full` and `.out` files. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is environment sensitivity: missing xfsprogs features, kernel feature flags, scratch geometry, runtime load, or non-normalized diagnostics can produce false failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 553`; `Format and mount fs`; `Create source file`; `Reflink destination file with source file`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/553 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/554 -->
# sources/test-tools/xfstests/tests/xfs/554

## Purpose

Create a filesystem which contains an inode with a lower number than the root inode. Set the lower number to a dump file as the root inode and ensure that 'xfsrestore -x' handles this wrong inode. This is a focused xfstests shell regression. It encodes an XFS behavior, userspace-tool contract, or maintenance check as a scratch/test filesystem scenario.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto quick dump prealloc` and imports common modules: `preamble`, `dump`. Local helper functions: none Key environment variables or shell state names include `fake_inum`, `inums`, `root_inum`.

Requirements and feature gates: `_require_xfs_io_command "falloc"`, `_require_scratch`, `_require_xfsrestore_xflag`. Recorded fix annotations: `_fixed_by_git_commit xfsdump XXXXXXXXXXXX xfsrestore: fix rootdir due to xfsdump bulkstat misuse`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `"XXXXXXXXXXXX xfsrestore: fix rootdir due to xfsdump bulkstat misuse"`, `inums=($(_scratch_xfs_create_fake_root))`, `$here/src/fake-dump-rootino $dump_file $fake_inum`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is the xfstests common harness, scratch filesystem lifecycle helpers, xfsprogs commands, and golden-output filtering through `seqres.full` and `.out` files. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is environment sensitivity: missing xfsprogs features, kernel feature flags, scratch geometry, runtime load, or non-normalized diagnostics can produce false failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 554`; `Creating directory system to dump using fsstress.`; `-----------------------------------------------`; `fsstress : -f link=10 -f creat=10 -f mkdir=10 -f truncate=5 -f symlink=10`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/554 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/555 -->
# sources/test-tools/xfstests/tests/xfs/555

## Purpose

Corrupt xfs sb_inopblock, make sure no crash. This's a test coverage of 392c6de98af1 ("xfs: sanitize sb_inopblock in xfs_mount_validate_sb") This is a focused xfstests shell regression. It encodes an XFS behavior, userspace-tool contract, or maintenance check as a scratch/test filesystem scenario.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto quick` and imports common modules: `preamble`. Local helper functions: none Key environment variables or shell state names include only standard xfstests variables such as `SCRATCH_MNT`, `SCRATCH_DEV`, `seqres`, and `tmp` are used

Requirements and feature gates: `_require_scratch`. Recorded fix annotations: `_fixed_by_kernel_commit 392c6de98af1 xfs: sanitize sb_inopblock in xfs_mount_validate_sb`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `"xfs: sanitize sb_inopblock in xfs_mount_validate_sb"`, `_scratch_mkfs >>$seqres.full`, `_scratch_xfs_set_metadata_field "inopblock" "500" "sb 0" >> $seqres.full`, `_try_scratch_mount 2>> $seqres.full && _fail "mount should not succeed!"`, `_scratch_xfs_repair >> $seqres.full 2>&1`, `_scratch_xfs_repair -n >> $seqres.full 2>&1 || echo "fs isn't fixed!"`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is the xfstests common harness, scratch filesystem lifecycle helpers, xfsprogs commands, and golden-output filtering through `seqres.full` and `.out` files. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is environment sensitivity: missing xfsprogs features, kernel feature flags, scratch geometry, runtime load, or non-normalized diagnostics can produce false failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 555`; `corrupt inopblock of sb 0`; `try to mount ...`; `no crash or hang`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/555 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/556 -->
# sources/test-tools/xfstests/tests/xfs/556

## Purpose

Check xfs_scrub's media scan can actually return diagnostic information for media errors in file data extents. This file exercises XFS online scrub, health reporting, or repair-adjacent behavior. It uses the xfstests scratch device plus xfs_scrub or xfs_spaceman commands to turn metadata health into a test oracle.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto quick scrub eio` and imports common modules: `preamble`, `fuzzy`, `filter`, `dmerror`. Local helper functions: `_cleanup`, `filter_scrub_errors`. Key environment variables or shell state names include `awk_len_prog`, `bad_len`, `bad_sector`, `bmap_str`, `errordev`, `file_blksz`, `fs_blksz`, `kernel_sectors_per_device_lba`, `kernel_sectors_per_fs_block`, `len`; plus 5 more.

Requirements and feature gates: `_require_scratch`, `_require_scratch_xfs_crc`, `_require_scrub`, `_require_dm_target error`, `_require_xfs_scratch_non_zoned`, `_require_scratch_xfs_scrub`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_mkfs >> $seqres.full`, `_scratch_mount`, `_scratch_unmount`, `$XFS_IO_PROG -f -c "pwrite -S 0x58 0 $((4 * file_blksz))" -c "fsync" $victim >> $seqres.full`, `if _xfs_is_realtime_file $victim; then`, `if ! _xfs_has_feature $SCRATCH_MNT rtgroups; then`, `bmap_str="$($XFS_IO_PROG -c "bmap -elpv" $victim | grep "^[[:space:]]*0:")"`, `logical_block_size=`$here/src/min_dio_alignment $SCRATCH_MNT $SCRATCH_DEV``; plus 2 more.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is common/fuzzy, xfs_io scrub commands, xfs_spaceman health output, scratch remounts, and feature-specific scrub prerequisites. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is that online health state is cached and feature-dependent; the scripts force mount cycles or explicit scrub passes to avoid reading stale state. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 556`; `Scrub for injected media error (single threaded)`; `Unfixable Error: SCRATCH_MNT/a: media error at data offset 2FSB length 1FSB.`; `SCRATCH_MNT: unfixable errors found: 1`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/556 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/557 -->
# sources/test-tools/xfstests/tests/xfs/557

## Purpose

This is a test for: bf3cb3944792 (xfs: allow single bulkstat of special inodes) Create a filesystem which contains an inode with a lower number than the root inode. Then verify that XFS_BULK_IREQ_SPECIAL_ROOT gets the correct root inode number. This is a focused xfstests shell regression. It encodes an XFS behavior, userspace-tool contract, or maintenance check as a scratch/test filesystem scenario.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto quick prealloc` and imports common modules: `preamble`. Local helper functions: none Key environment variables or shell state names include `bulkstat_root_inum`, `fake_inum`, `inums`, `root_inum`.

Requirements and feature gates: `_require_xfs_io_command "falloc"`, `_require_xfs_io_command "bulkstat_single"`, `_require_scratch`. Recorded fix annotations: `_fixed_by_kernel_commit 817644fa4525 xfs: get root inode correctly at bulkstat`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `"xfs: get root inode correctly at bulkstat"`, `inums=($(_scratch_xfs_create_fake_root))`, `bulkstat_root_inum=$($XFS_IO_PROG -c 'bulkstat_single root' $SCRATCH_MNT | grep bs_ino | awk '{print $3;}')`, `echo "bulkstat_root_inum: $bulkstat_root_inum" >> $seqres.full`, `if [ $root_inum -ne $bulkstat_root_inum ]; then`, `echo "root ino mismatch: expected:${root_inum}, actual:${bulkstat_root_inum}"`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is the xfstests common harness, scratch filesystem lifecycle helpers, xfsprogs commands, and golden-output filtering through `seqres.full` and `.out` files. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is environment sensitivity: missing xfsprogs features, kernel feature flags, scratch geometry, runtime load, or non-normalized diagnostics can produce false failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 557`; `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/557 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/558 -->
# sources/test-tools/xfstests/tests/xfs/558

## Purpose

This is a regression test for a data corruption bug that existed in XFS' copy on write code between 4.9 and 4.19.  The root cause is a concurrency bug wherein we would drop ILOCK_SHARED after querying the CoW fork in xfs_map_cow and retake it before querying the data fork in xfs_map_blocks.  If a second thread changes the CoW fork mappings between the two calls, it's possible for xfs_map_blocks to return a zero-block mapping, which results in writeback being elided for that block.  Elided writeback of dirty data results in silent loss of writes. Worse yet, kernels from that era still used buffer heads, which means that an elided writeback leaves the page clean but the bufferheads dirty.  Due to a naïve optimization in mark_buffer_dirty, the SetPageDirty call is elided if the bufferhead is dirty, which means that a subsequent rewrite of the data block will never result in the page being marked dirty, and all subsequent writes are lost. It turns out that Christoph Hellwig unwittingly fixed the race in commit 5c665e5b5af6 ("xfs: remove xfs_map_cow"), and no testcase was ever written. Four years later, we hit it on a production 4.14 kernel.  This testcase relies on a debugging knob that introduces artificial delays into writeback. Before the race, the file blocks 0-1 are not shared and blocks 2-5 are shared.  There are no extents in CoW fork. Two threads race like this: Thread 1 (writeback block 0)     | Thread 2  (write to block 2) ---------------------------------|-------------------------------- | 1. Check if block 0 in CoW fork  | from xfs_map_cow.             | | 2. Block 0 not found in CoW      | fork; the block is considered | not shared.                   | | 3. xfs_map_blocks looks up data  | fork to get a map covering    | block 0.                      | | 4. It gets a data fork mapping   | for block 0 with length 2.    | | | 1. A buffered write to block 2 sees |    that it is a shared block and no |    extent covers block 2 in CoW fork. | |    It creates a new CoW fork mapping. |    Due to the cowextsize, the new |    extent starts at block 0 with |    length 128. | | 5. It lookup CoW fork again to   | trim the map (0, 2) to a      | shared block boundary.        | | 5a. It finds (0, 128) in CoW fork| 5b. It trims the data fork map   | from (0, 1) to (0, 0) (!!!)  | | 6. The xfs_imap_valid call after | the xfs_map_blocks call checks| if the mapping (0, 0) covers  | block 0.  The result is "NO". | | 7. Since block 0 has no physical | block mapped, it's not added  | to the ioend.  This is the    | first problem.                | | 8. xfs_add_to_ioend usually      | clears the bufferhead dirty   | flag  Because this is skipped,| we leave the page clean with  | the associated buffer head(s) | dirty (the second problem).   | Now the dirty state is        | inconsistent. On newer kernels, this is also a functionality test for the ifork sequence counter because the writeback completions will change the data fork and force revalidations of the wb mapping. This is a focused xfstests shell regression. It encodes an XFS behavior, userspace-tool contract, or maintenance check as a scratch/test filesystem scenario.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto quick clone` and imports common modules: `preamble`, `reflink`, `inject`, `tracing`. Local helper functions: `_cleanup`, `wait_for_errortag`. Key environment variables or shell state names include `blksz`, `file_blksz`, `min_blksz`, `saw_invalidation`, `sentryfile`, `tracefile`.

Requirements and feature gates: `_require_ftrace`, `_require_xfs_io_error_injection "wb_delay_ms"`, `_require_scratch_reflink`, `_require_cp_reflink`, `_require_no_xfs_always_cow`, `_require_pagecache_access $SCRATCH_MNT`, `_require_congruent_file_oplen $SCRATCH_MNT $blksz`. Recorded fix annotations: `_fixed_by_kernel_commit 5c665e5b5af6 "xfs: remove xfs_map_cow"`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_fixed_by_kernel_commit 5c665e5b5af6 "xfs: remove xfs_map_cow"`, `_scratch_mkfs >> $seqres.full`, `_scratch_mount >> $seqres.full`, `$XFS_IO_PROG -c 'chattr -x' $SCRATCH_MNT &> $seqres.full`, `$XFS_IO_PROG -c 'cowextsize 1m' $SCRATCH_MNT`, `_scratch_sync`, `_scratch_cycle_mount`, `_scratch_inject_error "wb_delay_ms" 500`; plus 5 more.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is the xfstests common harness, scratch filesystem lifecycle helpers, xfsprogs commands, and golden-output filtering through `seqres.full` and `.out` files. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is environment sensitivity: missing xfsprogs features, kernel feature flags, scratch geometry, runtime load, or non-normalized diagnostics can produce false failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 558`; `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/558 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/559 -->
# sources/test-tools/xfstests/tests/xfs/559

## Purpose

This is a regression test for a data corruption bug that existed in iomap's buffered write routines. This is a focused xfstests shell regression. It encodes an XFS behavior, userspace-tool contract, or maintenance check as a scratch/test filesystem scenario.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto quick rw mmap` and imports common modules: `preamble`, `inject`, `tracing`. Local helper functions: `_cleanup`, `wait_for_errortag`. Key environment variables or shell state names include `base_pagesize`, `blksz`, `blocks`, `dirty_offset`, `dirty_pageoff`, `filesz`, `max_writesize`, `saw_invalidation`, `sentryfile`, `tracefile`; plus 1 more.

Requirements and feature gates: `_require_ftrace`, `_require_xfs_io_command "falloc"`, `_require_xfs_io_error_injection "write_delay_ms"`, `_require_scratch`, `_require_pagecache_access $SCRATCH_MNT`. Recorded fix annotations: `_fixed_by_kernel_commit 304a68b9c63b xfs: use iomap_valid method to detect stale cached iomaps`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_mkfs >> $seqres.full`, `_scratch_mount >> $seqres.full`, `$XFS_IO_PROG -c 'chattr -x' $SCRATCH_MNT &> $seqres.full`, `$XFS_IO_PROG -f -c "falloc 0 $filesz" $SCRATCH_MNT/file >> $seqres.full`, `_scratch_cycle_mount`, `$XFS_IO_PROG -c "pwrite -S 0x58 $dirty_offset 1" $SCRATCH_MNT/file >> $seqres.full`, `_scratch_inject_error "write_delay_ms" 500`, `_ftrace_record_events 'xfs_iomap_invalid'`; plus 4 more.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is the xfstests common harness, scratch filesystem lifecycle helpers, xfsprogs commands, and golden-output filtering through `seqres.full` and `.out` files. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is environment sensitivity: missing xfsprogs features, kernel feature flags, scratch geometry, runtime load, or non-normalized diagnostics can produce false failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 559`; `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/559 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/560 -->
# sources/test-tools/xfstests/tests/xfs/560

## Purpose

Race GETFSMAP and ro remount for a while to see if we crash or livelock. This file belongs to the scrub stress race suite. It formats and mounts scratch XFS, starts common/xfs stress-scrub orchestration, and races fsstress or fsx style mutation against one scrub or online-repair target.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto quick fsmap remount` and imports common modules: `preamble`, `filter`, `fuzzy`, `xfs`. Local helper functions: `_cleanup`. Key environment variables or shell state names include only standard xfstests variables such as `SCRATCH_MNT`, `SCRATCH_DEV`, `seqres`, and `tmp` are used

Requirements and feature gates: `_require_xfs_scratch_rmapbt`, `_require_xfs_io_command "fsmap"`, `_require_xfs_stress_scrub`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_begin_fstest auto quick fsmap remount`, `_scratch_xfs_stress_scrub_cleanup`, `_scratch_mkfs > "$seqres.full" 2>&1`, `_scratch_mount`, `_scratch_xfs_stress_scrub -r 5 -i 'fsmap -v'`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is `_scratch_xfs_stress_scrub`, its cleanup hook, selected scrub command strings, fsstress operation exclusion flags, and feature gates for realtime, quota, reflink, attributes, rmapbt, or finobt when required. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is nondeterminism: the expected signal is absence of crashes, livelocks, and scrub infrastructure failures, so runtime, load factor, feature availability, and cleanup correctness matter more than fixed stdout. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 560`; `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/560 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/561 -->
# sources/test-tools/xfstests/tests/xfs/561

## Purpose

Race xfs_scrub in check-only mode and ro remount for a while to see if we crash or livelock. This file belongs to the scrub stress race suite. It formats and mounts scratch XFS, starts common/xfs stress-scrub orchestration, and races fsstress or fsx style mutation against one scrub or online-repair target.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest scrub fsstress_scrub` and imports common modules: `preamble`, `filter`, `fuzzy`, `xfs`. Local helper functions: `_cleanup`. Key environment variables or shell state names include only standard xfstests variables such as `SCRATCH_MNT`, `SCRATCH_DEV`, `seqres`, and `tmp` are used

Requirements and feature gates: `_require_scratch`, `_require_xfs_stress_scrub`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_begin_fstest scrub fsstress_scrub`, `_scratch_xfs_stress_scrub_cleanup &> /dev/null`, `_scratch_remount rw`, `_scratch_mkfs > "$seqres.full" 2>&1`, `_scratch_mount`, `_scratch_xfs_stress_scrub -r 5 -S '-n'`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is `_scratch_xfs_stress_scrub`, its cleanup hook, selected scrub command strings, fsstress operation exclusion flags, and feature gates for realtime, quota, reflink, attributes, rmapbt, or finobt when required. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is nondeterminism: the expected signal is absence of crashes, livelocks, and scrub infrastructure failures, so runtime, load factor, feature availability, and cleanup correctness matter more than fixed stdout. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 561`; `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/561 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/562 -->
# sources/test-tools/xfstests/tests/xfs/562

## Purpose

Race xfs_scrub in check-only mode and freeze for a while to see if we crash or livelock. This file belongs to the scrub stress race suite. It formats and mounts scratch XFS, starts common/xfs stress-scrub orchestration, and races fsstress or fsx style mutation against one scrub or online-repair target.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest scrub fsstress_scrub` and imports common modules: `preamble`, `filter`, `fuzzy`, `xfs`. Local helper functions: `_cleanup`. Key environment variables or shell state names include only standard xfstests variables such as `SCRATCH_MNT`, `SCRATCH_DEV`, `seqres`, and `tmp` are used

Requirements and feature gates: `_require_scratch`, `_require_xfs_stress_scrub`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_begin_fstest scrub fsstress_scrub`, `_scratch_xfs_stress_scrub_cleanup &> /dev/null`, `_scratch_remount rw`, `_scratch_mkfs > "$seqres.full" 2>&1`, `_scratch_mount`, `_scratch_xfs_stress_scrub -f -S '-n'`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is `_scratch_xfs_stress_scrub`, its cleanup hook, selected scrub command strings, fsstress operation exclusion flags, and feature gates for realtime, quota, reflink, attributes, rmapbt, or finobt when required. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is nondeterminism: the expected signal is absence of crashes, livelocks, and scrub infrastructure failures, so runtime, load factor, feature availability, and cleanup correctness matter more than fixed stdout. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 562`; `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/562 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/563 -->
# sources/test-tools/xfstests/tests/xfs/563

## Purpose

Race xfs_scrub in force-repair mdoe and freeze for a while to see if we crash or livelock. This file belongs to the scrub stress race suite. It formats and mounts scratch XFS, starts common/xfs stress-scrub orchestration, and races fsstress or fsx style mutation against one scrub or online-repair target.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest online_repair fsstress_online_repair` and imports common modules: `preamble`, `filter`, `fuzzy`, `xfs`, `inject`. Local helper functions: `_cleanup`. Key environment variables or shell state names include only standard xfstests variables such as `SCRATCH_MNT`, `SCRATCH_DEV`, `seqres`, and `tmp` are used

Requirements and feature gates: `_require_scratch`, `_require_xfs_stress_online_repair`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_begin_fstest online_repair fsstress_online_repair`, `_scratch_xfs_stress_scrub_cleanup &> /dev/null`, `_scratch_remount rw`, `_scratch_mkfs > "$seqres.full" 2>&1`, `_scratch_mount`, `_scratch_xfs_stress_online_repair -f -S '-k'`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is `_scratch_xfs_stress_scrub`, its cleanup hook, selected scrub command strings, fsstress operation exclusion flags, and feature gates for realtime, quota, reflink, attributes, rmapbt, or finobt when required. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is nondeterminism: the expected signal is absence of crashes, livelocks, and scrub infrastructure failures, so runtime, load factor, feature availability, and cleanup correctness matter more than fixed stdout. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 563`; `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/563 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/564 -->
# sources/test-tools/xfstests/tests/xfs/564

## Purpose

Race xfs_scrub in force-repair mode and ro remount for a while to see if we crash or livelock. This file belongs to the scrub stress race suite. It formats and mounts scratch XFS, starts common/xfs stress-scrub orchestration, and races fsstress or fsx style mutation against one scrub or online-repair target.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest online_repair fsstress_online_repair` and imports common modules: `preamble`, `filter`, `fuzzy`, `xfs`, `inject`. Local helper functions: `_cleanup`. Key environment variables or shell state names include only standard xfstests variables such as `SCRATCH_MNT`, `SCRATCH_DEV`, `seqres`, and `tmp` are used

Requirements and feature gates: `_require_scratch`, `_require_xfs_stress_online_repair`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_begin_fstest online_repair fsstress_online_repair`, `_scratch_xfs_stress_scrub_cleanup &> /dev/null`, `_scratch_remount rw`, `_scratch_mkfs > "$seqres.full" 2>&1`, `_scratch_mount`, `_scratch_xfs_stress_online_repair -r 5 -S '-k'`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is `_scratch_xfs_stress_scrub`, its cleanup hook, selected scrub command strings, fsstress operation exclusion flags, and feature gates for realtime, quota, reflink, attributes, rmapbt, or finobt when required. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is nondeterminism: the expected signal is absence of crashes, livelocks, and scrub infrastructure failures, so runtime, load factor, feature availability, and cleanup correctness matter more than fixed stdout. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 564`; `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/564 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/565 -->
# sources/test-tools/xfstests/tests/xfs/565

## Purpose

Race fsx and xfs_scrub in read-only mode for a while to see if we crash or livelock. This file belongs to the scrub stress race suite. It formats and mounts scratch XFS, starts common/xfs stress-scrub orchestration, and races fsstress or fsx style mutation against one scrub or online-repair target.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto scrub fsstress_scrub` and imports common modules: `preamble`, `filter`, `fuzzy`, `inject`, `xfs`. Local helper functions: `_cleanup`. Key environment variables or shell state names include only standard xfstests variables such as `SCRATCH_MNT`, `SCRATCH_DEV`, `seqres`, and `tmp` are used

Requirements and feature gates: `_require_scratch`, `_require_xfs_stress_scrub`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_begin_fstest auto scrub fsstress_scrub`, `_scratch_xfs_stress_scrub_cleanup &> /dev/null`, `_scratch_mkfs > "$seqres.full" 2>&1`, `_scratch_mount`, `_scratch_xfs_stress_scrub -S '-n' -X 'fsx'`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is `_scratch_xfs_stress_scrub`, its cleanup hook, selected scrub command strings, fsstress operation exclusion flags, and feature gates for realtime, quota, reflink, attributes, rmapbt, or finobt when required. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is nondeterminism: the expected signal is absence of crashes, livelocks, and scrub infrastructure failures, so runtime, load factor, feature availability, and cleanup correctness matter more than fixed stdout. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 565`; `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/565 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/566 -->
# sources/test-tools/xfstests/tests/xfs/566

## Purpose

Race fsx and xfs_scrub in force-repair mode for a while to see if we crash or livelock. This file belongs to the scrub stress race suite. It formats and mounts scratch XFS, starts common/xfs stress-scrub orchestration, and races fsstress or fsx style mutation against one scrub or online-repair target.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto online_repair fsstress_online_repair` and imports common modules: `preamble`, `filter`, `fuzzy`, `inject`, `xfs`. Local helper functions: `_cleanup`. Key environment variables or shell state names include only standard xfstests variables such as `SCRATCH_MNT`, `SCRATCH_DEV`, `seqres`, and `tmp` are used

Requirements and feature gates: `_require_scratch`, `_require_xfs_stress_online_repair`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_begin_fstest auto online_repair fsstress_online_repair`, `_scratch_xfs_stress_scrub_cleanup &> /dev/null`, `_scratch_mkfs > "$seqres.full" 2>&1`, `_scratch_mount`, `_scratch_xfs_stress_online_repair -S '-k' -X 'fsx'`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is `_scratch_xfs_stress_scrub`, its cleanup hook, selected scrub command strings, fsstress operation exclusion flags, and feature gates for realtime, quota, reflink, attributes, rmapbt, or finobt when required. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is nondeterminism: the expected signal is absence of crashes, livelocks, and scrub infrastructure failures, so runtime, load factor, feature availability, and cleanup correctness matter more than fixed stdout. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 566`; `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/566 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/567 -->
# sources/test-tools/xfstests/tests/xfs/567

## Purpose

Tests `xfsrestore -x` which handles an wrong inode in a dump, with the multi-level dumps where we hit an issue during development. This procedure is cribbed from: xfs/064: test multilevel dump and restores with hardlinks This file exercises xfsdump/xfsrestore multi-level restore behavior with the `-x` option for dumps containing a wrong or fake inode. It derives from older dump/restore tests but narrows the scenario to a restore regression.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto dump` and imports common modules: `preamble`, `dump`. Local helper functions: `_cleanup`, `_ls_size_filter`. Key environment variables or shell state names include `dumpfile`, `fake_inum`, `i`, `inums`, `opt`, `root_inum`.

Requirements and feature gates: `_require_xfs_io_command "falloc"`, `_require_scratch`, `_require_xfsrestore_xflag`. Recorded fix annotations: `_fixed_by_git_commit xfsdump XXXXXXXXXXXX xfsrestore: fix rootdir due to xfsdump bulkstat misuse`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `"XXXXXXXXXXXX xfsrestore: fix rootdir due to xfsdump bulkstat misuse"`, `inums=($(_scratch_xfs_create_fake_root))`, `find $SCRATCH_MNT -exec $here/src/lstat64 {} \; | sed 's/(00.*)//' >$tmp.dates.$i`, `$here/src/fake-dump-rootino $dumpfile $fake_inum`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is xfsdump/xfsrestore, hardlink and incremental dump state, scratch population, and deterministic directory listing filters used to compare restored trees. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is output instability from inode numbers, directory sizes, quota state, and dump timestamps; the script filters variable fields and disables quotas where needed. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 567`; `Creating directory system of hardlinks to incrementally dump.`; `creating hardlink file1_h1 to file1`; `creating hardlink file1_h2 to file1`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/567 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/568 -->
# sources/test-tools/xfstests/tests/xfs/568

## Purpose

Tests `xfsrestore -x` which handles an wrong inode in a dump, with the multi-level dumps where we hit an issue during development. This procedure is cribbed from: xfs/065: Testing incremental dumps and cumulative restores with different operations for each level This file exercises xfsdump/xfsrestore multi-level restore behavior with the `-x` option for dumps containing a wrong or fake inode. It derives from older dump/restore tests but narrows the scenario to a restore regression.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto dump` and imports common modules: `preamble`, `filter`, `dump`, `quota`. Local helper functions: `_cleanup`, `_list_dir`. Key environment variables or shell state names include `LC_COLLATE`, `__dir`, `dumpfile`, `fake_inum`, `i`, `inums`, `num_dumps`, `opt`, `root_inum`.

Requirements and feature gates: `_require_xfs_io_command "falloc"`, `_require_scratch`, `_require_xfsrestore_xflag`. Recorded fix annotations: `_fixed_by_git_commit xfsdump XXXXXXXXXXXX xfsrestore: fix rootdir due to xfsdump bulkstat misuse`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `find $__dir -exec $here/src/lstat64 -t {} \; |\`, `"XXXXXXXXXXXX xfsrestore: fix rootdir due to xfsdump bulkstat misuse"`, `_scratch_mkfs_xfs >> $seqres.full`, `_scratch_mount`, `$here/src/feature -U $SCRATCH_DEV && \`, `$here/src/feature -G $SCRATCH_DEV && \`, `$here/src/feature -P $SCRATCH_DEV && \`, `_scratch_unmount`; plus 2 more.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is xfsdump/xfsrestore, hardlink and incremental dump state, scratch population, and deterministic directory listing filters used to compare restored trees. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is output instability from inode numbers, directory sizes, quota state, and dump timestamps; the script filters variable fields and disables quotas where needed. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 568`; `Do the incremental dumps`; `Listing of what files we have at level 0:`; `dumpdir/addeddir1 XXX drwxr-xr-x 0,0`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/568 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/569 -->
# sources/test-tools/xfstests/tests/xfs/569

## Purpose

Check for any installed example mkfs config files and validate that mkfs.xfs can properly use them. This is a focused xfstests shell regression. It encodes an XFS behavior, userspace-tool contract, or maintenance check as a scratch/test filesystem scenario.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest mkfs` and imports common modules: `preamble`. Local helper functions: none Key environment variables or shell state names include only standard xfstests variables such as `SCRATCH_MNT`, `SCRATCH_DEV`, `seqres`, and `tmp` are used

Requirements and feature gates: `_require_scratch_nocheck`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: The command flow is primarily ordinary shell setup and harness completion.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is the xfstests common harness, scratch filesystem lifecycle helpers, xfsprogs commands, and golden-output filtering through `seqres.full` and `.out` files. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is environment sensitivity: missing xfsprogs features, kernel feature flags, scratch geometry, runtime load, or non-normalized diagnostics can produce false failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 569`; `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/569 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/570 -->
# sources/test-tools/xfstests/tests/xfs/570

## Purpose

Race fsstress and superblock scrub for a while to see if we crash or livelock. This file belongs to the scrub stress race suite. It formats and mounts scratch XFS, starts common/xfs stress-scrub orchestration, and races fsstress or fsx style mutation against one scrub or online-repair target.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest scrub fsstress_scrub` and imports common modules: `preamble`, `filter`, `fuzzy`, `inject`, `xfs`. Local helper functions: `_cleanup`. Key environment variables or shell state names include only standard xfstests variables such as `SCRATCH_MNT`, `SCRATCH_DEV`, `seqres`, and `tmp` are used

Requirements and feature gates: `_require_scratch`, `_require_xfs_stress_scrub`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_begin_fstest scrub fsstress_scrub`, `_scratch_xfs_stress_scrub_cleanup &> /dev/null`, `_scratch_mkfs > "$seqres.full" 2>&1`, `_scratch_mount`, `_scratch_xfs_stress_scrub -s "scrub sb %agno%"`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is `_scratch_xfs_stress_scrub`, its cleanup hook, selected scrub command strings, fsstress operation exclusion flags, and feature gates for realtime, quota, reflink, attributes, rmapbt, or finobt when required. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is nondeterminism: the expected signal is absence of crashes, livelocks, and scrub infrastructure failures, so runtime, load factor, feature availability, and cleanup correctness matter more than fixed stdout. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 570`; `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/570 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/571 -->
# sources/test-tools/xfstests/tests/xfs/571

## Purpose

Race fsstress and AGF scrub for a while to see if we crash or livelock. This file belongs to the scrub stress race suite. It formats and mounts scratch XFS, starts common/xfs stress-scrub orchestration, and races fsstress or fsx style mutation against one scrub or online-repair target.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest scrub fsstress_scrub` and imports common modules: `preamble`, `filter`, `fuzzy`, `inject`, `xfs`. Local helper functions: `_cleanup`. Key environment variables or shell state names include only standard xfstests variables such as `SCRATCH_MNT`, `SCRATCH_DEV`, `seqres`, and `tmp` are used

Requirements and feature gates: `_require_scratch`, `_require_xfs_stress_scrub`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_begin_fstest scrub fsstress_scrub`, `_scratch_xfs_stress_scrub_cleanup &> /dev/null`, `_scratch_mkfs > "$seqres.full" 2>&1`, `_scratch_mount`, `_scratch_xfs_stress_scrub -s "scrub agf %agno%"`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is `_scratch_xfs_stress_scrub`, its cleanup hook, selected scrub command strings, fsstress operation exclusion flags, and feature gates for realtime, quota, reflink, attributes, rmapbt, or finobt when required. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is nondeterminism: the expected signal is absence of crashes, livelocks, and scrub infrastructure failures, so runtime, load factor, feature availability, and cleanup correctness matter more than fixed stdout. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 571`; `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/571 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/572 -->
# sources/test-tools/xfstests/tests/xfs/572

## Purpose

Race fsstress and AGFL scrub for a while to see if we crash or livelock. This file belongs to the scrub stress race suite. It formats and mounts scratch XFS, starts common/xfs stress-scrub orchestration, and races fsstress or fsx style mutation against one scrub or online-repair target.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest scrub fsstress_scrub` and imports common modules: `preamble`, `filter`, `fuzzy`, `inject`, `xfs`. Local helper functions: `_cleanup`. Key environment variables or shell state names include only standard xfstests variables such as `SCRATCH_MNT`, `SCRATCH_DEV`, `seqres`, and `tmp` are used

Requirements and feature gates: `_require_scratch`, `_require_xfs_stress_scrub`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_begin_fstest scrub fsstress_scrub`, `_scratch_xfs_stress_scrub_cleanup &> /dev/null`, `_scratch_mkfs > "$seqres.full" 2>&1`, `_scratch_mount`, `_scratch_xfs_stress_scrub -s "scrub agfl %agno%"`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is `_scratch_xfs_stress_scrub`, its cleanup hook, selected scrub command strings, fsstress operation exclusion flags, and feature gates for realtime, quota, reflink, attributes, rmapbt, or finobt when required. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is nondeterminism: the expected signal is absence of crashes, livelocks, and scrub infrastructure failures, so runtime, load factor, feature availability, and cleanup correctness matter more than fixed stdout. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 572`; `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/572 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/573 -->
# sources/test-tools/xfstests/tests/xfs/573

## Purpose

Race fsstress and AGI scrub for a while to see if we crash or livelock. This file belongs to the scrub stress race suite. It formats and mounts scratch XFS, starts common/xfs stress-scrub orchestration, and races fsstress or fsx style mutation against one scrub or online-repair target.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest scrub fsstress_scrub` and imports common modules: `preamble`, `filter`, `fuzzy`, `inject`, `xfs`. Local helper functions: `_cleanup`. Key environment variables or shell state names include only standard xfstests variables such as `SCRATCH_MNT`, `SCRATCH_DEV`, `seqres`, and `tmp` are used

Requirements and feature gates: `_require_scratch`, `_require_xfs_stress_scrub`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_begin_fstest scrub fsstress_scrub`, `_scratch_xfs_stress_scrub_cleanup &> /dev/null`, `_scratch_mkfs > "$seqres.full" 2>&1`, `_scratch_mount`, `_scratch_xfs_stress_scrub -s "scrub agi %agno%"`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is `_scratch_xfs_stress_scrub`, its cleanup hook, selected scrub command strings, fsstress operation exclusion flags, and feature gates for realtime, quota, reflink, attributes, rmapbt, or finobt when required. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is nondeterminism: the expected signal is absence of crashes, livelocks, and scrub infrastructure failures, so runtime, load factor, feature availability, and cleanup correctness matter more than fixed stdout. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 573`; `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/573 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/574 -->
# sources/test-tools/xfstests/tests/xfs/574

## Purpose

Race fsstress and freespace by block btree scrub for a while to see if we crash or livelock. This file belongs to the scrub stress race suite. It formats and mounts scratch XFS, starts common/xfs stress-scrub orchestration, and races fsstress or fsx style mutation against one scrub or online-repair target.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest scrub fsstress_scrub` and imports common modules: `preamble`, `filter`, `fuzzy`, `inject`, `xfs`. Local helper functions: `_cleanup`. Key environment variables or shell state names include only standard xfstests variables such as `SCRATCH_MNT`, `SCRATCH_DEV`, `seqres`, and `tmp` are used

Requirements and feature gates: `_require_scratch`, `_require_xfs_stress_scrub`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_begin_fstest scrub fsstress_scrub`, `_scratch_xfs_stress_scrub_cleanup &> /dev/null`, `_scratch_mkfs > "$seqres.full" 2>&1`, `_scratch_mount`, `_scratch_xfs_stress_scrub -s "scrub bnobt %agno%"`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is `_scratch_xfs_stress_scrub`, its cleanup hook, selected scrub command strings, fsstress operation exclusion flags, and feature gates for realtime, quota, reflink, attributes, rmapbt, or finobt when required. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is nondeterminism: the expected signal is absence of crashes, livelocks, and scrub infrastructure failures, so runtime, load factor, feature availability, and cleanup correctness matter more than fixed stdout. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 574`; `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/574 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/575 -->
# sources/test-tools/xfstests/tests/xfs/575

## Purpose

Race fsstress and free space by length btree scrub for a while to see if we crash or livelock. This file belongs to the scrub stress race suite. It formats and mounts scratch XFS, starts common/xfs stress-scrub orchestration, and races fsstress or fsx style mutation against one scrub or online-repair target.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest scrub fsstress_scrub` and imports common modules: `preamble`, `filter`, `fuzzy`, `inject`, `xfs`. Local helper functions: `_cleanup`. Key environment variables or shell state names include only standard xfstests variables such as `SCRATCH_MNT`, `SCRATCH_DEV`, `seqres`, and `tmp` are used

Requirements and feature gates: `_require_scratch`, `_require_xfs_stress_scrub`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_begin_fstest scrub fsstress_scrub`, `_scratch_xfs_stress_scrub_cleanup &> /dev/null`, `_scratch_mkfs > "$seqres.full" 2>&1`, `_scratch_mount`, `_scratch_xfs_stress_scrub -s "scrub cntbt %agno%"`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is `_scratch_xfs_stress_scrub`, its cleanup hook, selected scrub command strings, fsstress operation exclusion flags, and feature gates for realtime, quota, reflink, attributes, rmapbt, or finobt when required. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is nondeterminism: the expected signal is absence of crashes, livelocks, and scrub infrastructure failures, so runtime, load factor, feature availability, and cleanup correctness matter more than fixed stdout. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 575`; `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/575 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/576 -->
# sources/test-tools/xfstests/tests/xfs/576

## Purpose

Race fsstress and inode btree scrub for a while to see if we crash or livelock. This file belongs to the scrub stress race suite. It formats and mounts scratch XFS, starts common/xfs stress-scrub orchestration, and races fsstress or fsx style mutation against one scrub or online-repair target.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest scrub fsstress_scrub` and imports common modules: `preamble`, `filter`, `fuzzy`, `inject`, `xfs`. Local helper functions: `_cleanup`. Key environment variables or shell state names include only standard xfstests variables such as `SCRATCH_MNT`, `SCRATCH_DEV`, `seqres`, and `tmp` are used

Requirements and feature gates: `_require_scratch`, `_require_xfs_stress_scrub`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_begin_fstest scrub fsstress_scrub`, `_scratch_xfs_stress_scrub_cleanup &> /dev/null`, `_scratch_mkfs > "$seqres.full" 2>&1`, `_scratch_mount`, `_scratch_xfs_stress_scrub -x 'dir' -s "scrub inobt %agno%"`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is `_scratch_xfs_stress_scrub`, its cleanup hook, selected scrub command strings, fsstress operation exclusion flags, and feature gates for realtime, quota, reflink, attributes, rmapbt, or finobt when required. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is nondeterminism: the expected signal is absence of crashes, livelocks, and scrub infrastructure failures, so runtime, load factor, feature availability, and cleanup correctness matter more than fixed stdout. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 576`; `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/576 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/577 -->
# sources/test-tools/xfstests/tests/xfs/577

## Purpose

Race fsstress and free inode btree scrub for a while to see if we crash or livelock. This file belongs to the scrub stress race suite. It formats and mounts scratch XFS, starts common/xfs stress-scrub orchestration, and races fsstress or fsx style mutation against one scrub or online-repair target.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest scrub fsstress_scrub` and imports common modules: `preamble`, `filter`, `fuzzy`, `inject`, `xfs`. Local helper functions: `_cleanup`. Key environment variables or shell state names include only standard xfstests variables such as `SCRATCH_MNT`, `SCRATCH_DEV`, `seqres`, and `tmp` are used

Requirements and feature gates: `_require_scratch`, `_require_xfs_stress_scrub`, `_require_xfs_has_feature "$SCRATCH_MNT" finobt`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_begin_fstest scrub fsstress_scrub`, `_scratch_xfs_stress_scrub_cleanup &> /dev/null`, `_scratch_mkfs > "$seqres.full" 2>&1`, `_scratch_mount`, `_scratch_xfs_stress_scrub -x 'dir' -s "scrub finobt %agno%"`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is `_scratch_xfs_stress_scrub`, its cleanup hook, selected scrub command strings, fsstress operation exclusion flags, and feature gates for realtime, quota, reflink, attributes, rmapbt, or finobt when required. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is nondeterminism: the expected signal is absence of crashes, livelocks, and scrub infrastructure failures, so runtime, load factor, feature availability, and cleanup correctness matter more than fixed stdout. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 577`; `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/577 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/578 -->
# sources/test-tools/xfstests/tests/xfs/578

## Purpose

Race fsstress and reverse mapping btree scrub for a while to see if we crash or livelock. This file belongs to the scrub stress race suite. It formats and mounts scratch XFS, starts common/xfs stress-scrub orchestration, and races fsstress or fsx style mutation against one scrub or online-repair target.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest scrub fsstress_scrub` and imports common modules: `preamble`, `filter`, `fuzzy`, `inject`, `xfs`. Local helper functions: `_cleanup`. Key environment variables or shell state names include only standard xfstests variables such as `SCRATCH_MNT`, `SCRATCH_DEV`, `seqres`, and `tmp` are used

Requirements and feature gates: `_require_scratch`, `_require_xfs_stress_scrub`, `_require_xfs_has_feature "$SCRATCH_MNT" rmapbt`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_begin_fstest scrub fsstress_scrub`, `_scratch_xfs_stress_scrub_cleanup &> /dev/null`, `_scratch_mkfs > "$seqres.full" 2>&1`, `_scratch_mount`, `_scratch_xfs_stress_scrub -s "scrub rmapbt %agno%"`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is `_scratch_xfs_stress_scrub`, its cleanup hook, selected scrub command strings, fsstress operation exclusion flags, and feature gates for realtime, quota, reflink, attributes, rmapbt, or finobt when required. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is nondeterminism: the expected signal is absence of crashes, livelocks, and scrub infrastructure failures, so runtime, load factor, feature availability, and cleanup correctness matter more than fixed stdout. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 578`; `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/578 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/579 -->
# sources/test-tools/xfstests/tests/xfs/579

## Purpose

Race fsstress and reference count btree scrub for a while to see if we crash or livelock. This file belongs to the scrub stress race suite. It formats and mounts scratch XFS, starts common/xfs stress-scrub orchestration, and races fsstress or fsx style mutation against one scrub or online-repair target.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest scrub fsstress_scrub` and imports common modules: `preamble`, `filter`, `fuzzy`, `inject`, `xfs`, `reflink`. Local helper functions: `_cleanup`. Key environment variables or shell state names include only standard xfstests variables such as `SCRATCH_MNT`, `SCRATCH_DEV`, `seqres`, and `tmp` are used

Requirements and feature gates: `_require_scratch`, `_require_xfs_stress_scrub`, `_require_xfs_has_feature "$SCRATCH_MNT" reflink`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_begin_fstest scrub fsstress_scrub`, `_scratch_xfs_stress_scrub_cleanup &> /dev/null`, `_scratch_mkfs > "$seqres.full" 2>&1`, `_scratch_mount`, `_scratch_xfs_stress_scrub -s "scrub refcountbt %agno%"`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is `_scratch_xfs_stress_scrub`, its cleanup hook, selected scrub command strings, fsstress operation exclusion flags, and feature gates for realtime, quota, reflink, attributes, rmapbt, or finobt when required. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is nondeterminism: the expected signal is absence of crashes, livelocks, and scrub infrastructure failures, so runtime, load factor, feature availability, and cleanup correctness matter more than fixed stdout. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 579`; `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/579 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/580 -->
# sources/test-tools/xfstests/tests/xfs/580

## Purpose

Race fsstress and fscounter scrub on the realtime device for a while to see if we crash or livelock. This file belongs to the scrub stress race suite. It formats and mounts scratch XFS, starts common/xfs stress-scrub orchestration, and races fsstress or fsx style mutation against one scrub or online-repair target.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest scrub fsstress_scrub` and imports common modules: `preamble`, `filter`, `fuzzy`, `inject`, `xfs`. Local helper functions: `_cleanup`. Key environment variables or shell state names include only standard xfstests variables such as `SCRATCH_MNT`, `SCRATCH_DEV`, `seqres`, and `tmp` are used

Requirements and feature gates: `_require_realtime`, `_require_scratch`, `_require_xfs_stress_scrub`, `_require_xfs_has_feature "$SCRATCH_MNT" realtime`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_begin_fstest scrub fsstress_scrub`, `_scratch_xfs_stress_scrub_cleanup &> /dev/null`, `_scratch_mkfs > "$seqres.full" 2>&1`, `_scratch_mount`, `_xfs_force_bdev realtime $SCRATCH_MNT`, `_scratch_xfs_stress_scrub -s 'scrub fscounters'`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is `_scratch_xfs_stress_scrub`, its cleanup hook, selected scrub command strings, fsstress operation exclusion flags, and feature gates for realtime, quota, reflink, attributes, rmapbt, or finobt when required. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is nondeterminism: the expected signal is absence of crashes, livelocks, and scrub infrastructure failures, so runtime, load factor, feature availability, and cleanup correctness matter more than fixed stdout. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 580`; `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/580 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/581 -->
# sources/test-tools/xfstests/tests/xfs/581

## Purpose

Race fsstress and realtime bitmap scrub for a while to see if we crash or livelock. This file belongs to the scrub stress race suite. It formats and mounts scratch XFS, starts common/xfs stress-scrub orchestration, and races fsstress or fsx style mutation against one scrub or online-repair target.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest scrub fsstress_scrub` and imports common modules: `preamble`, `filter`, `fuzzy`, `inject`, `xfs`. Local helper functions: `_cleanup`. Key environment variables or shell state names include only standard xfstests variables such as `SCRATCH_MNT`, `SCRATCH_DEV`, `seqres`, and `tmp` are used

Requirements and feature gates: `_require_realtime`, `_require_scratch`, `_require_xfs_stress_scrub`, `_require_xfs_has_feature "$SCRATCH_MNT" realtime`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_begin_fstest scrub fsstress_scrub`, `_scratch_xfs_stress_scrub_cleanup &> /dev/null`, `_scratch_mkfs > "$seqres.full" 2>&1`, `_scratch_mount`, `if _xfs_has_feature "$SCRATCH_MNT" rtgroups; then`, `_scratch_xfs_stress_scrub -s "scrub rtbitmap %rgno%"`, `elif xfs_io -c 'help scrub' | grep -q rgsuper; then`, `_scratch_xfs_stress_scrub -s "scrub rtbitmap 0"`; plus 1 more.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is `_scratch_xfs_stress_scrub`, its cleanup hook, selected scrub command strings, fsstress operation exclusion flags, and feature gates for realtime, quota, reflink, attributes, rmapbt, or finobt when required. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is nondeterminism: the expected signal is absence of crashes, livelocks, and scrub infrastructure failures, so runtime, load factor, feature availability, and cleanup correctness matter more than fixed stdout. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 581`; `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/581 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/582 -->
# sources/test-tools/xfstests/tests/xfs/582

## Purpose

Race fsstress and realtime summary scrub for a while to see if we crash or livelock. This file belongs to the scrub stress race suite. It formats and mounts scratch XFS, starts common/xfs stress-scrub orchestration, and races fsstress or fsx style mutation against one scrub or online-repair target.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest scrub fsstress_scrub` and imports common modules: `preamble`, `filter`, `fuzzy`, `inject`, `xfs`. Local helper functions: `_cleanup`. Key environment variables or shell state names include only standard xfstests variables such as `SCRATCH_MNT`, `SCRATCH_DEV`, `seqres`, and `tmp` are used

Requirements and feature gates: `_require_realtime`, `_require_scratch`, `_require_xfs_stress_scrub`, `_require_xfs_has_feature "$SCRATCH_MNT" realtime`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_begin_fstest scrub fsstress_scrub`, `_scratch_xfs_stress_scrub_cleanup &> /dev/null`, `_scratch_mkfs > "$seqres.full" 2>&1`, `_scratch_mount`, `if _xfs_has_feature "$SCRATCH_MNT" rtgroups; then`, `_scratch_xfs_stress_scrub -s "scrub rtsummary %rgno%"`, `elif xfs_io -c 'help scrub' | grep -q rgsuper; then`, `_scratch_xfs_stress_scrub -s "scrub rtsummary 0"`; plus 1 more.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is `_scratch_xfs_stress_scrub`, its cleanup hook, selected scrub command strings, fsstress operation exclusion flags, and feature gates for realtime, quota, reflink, attributes, rmapbt, or finobt when required. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is nondeterminism: the expected signal is absence of crashes, livelocks, and scrub infrastructure failures, so runtime, load factor, feature availability, and cleanup correctness matter more than fixed stdout. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 582`; `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/582 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/583 -->
# sources/test-tools/xfstests/tests/xfs/583

## Purpose

Race fsstress and user quota scrub for a while to see if we crash or livelock. This file belongs to the scrub stress race suite. It formats and mounts scratch XFS, starts common/xfs stress-scrub orchestration, and races fsstress or fsx style mutation against one scrub or online-repair target.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest scrub fsstress_scrub` and imports common modules: `preamble`, `filter`, `fuzzy`, `inject`, `xfs`, `quota`. Local helper functions: `_cleanup`. Key environment variables or shell state names include only standard xfstests variables such as `SCRATCH_MNT`, `SCRATCH_DEV`, `seqres`, and `tmp` are used

Requirements and feature gates: `_require_scratch`, `_require_xfs_stress_scrub`, `_require_xfs_quota_acct_enabled "$SCRATCH_DEV" usrquota`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_begin_fstest scrub fsstress_scrub`, `_scratch_xfs_stress_scrub_cleanup &> /dev/null`, `_scratch_mkfs > "$seqres.full" 2>&1`, `_scratch_mount`, `_scratch_xfs_stress_scrub -s "scrub usrquota"`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is `_scratch_xfs_stress_scrub`, its cleanup hook, selected scrub command strings, fsstress operation exclusion flags, and feature gates for realtime, quota, reflink, attributes, rmapbt, or finobt when required. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is nondeterminism: the expected signal is absence of crashes, livelocks, and scrub infrastructure failures, so runtime, load factor, feature availability, and cleanup correctness matter more than fixed stdout. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 583`; `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/583 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/584 -->
# sources/test-tools/xfstests/tests/xfs/584

## Purpose

Race fsstress and group quota scrub for a while to see if we crash or livelock. This file belongs to the scrub stress race suite. It formats and mounts scratch XFS, starts common/xfs stress-scrub orchestration, and races fsstress or fsx style mutation against one scrub or online-repair target.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest scrub fsstress_scrub` and imports common modules: `preamble`, `filter`, `fuzzy`, `inject`, `xfs`, `quota`. Local helper functions: `_cleanup`. Key environment variables or shell state names include only standard xfstests variables such as `SCRATCH_MNT`, `SCRATCH_DEV`, `seqres`, and `tmp` are used

Requirements and feature gates: `_require_scratch`, `_require_xfs_stress_scrub`, `_require_xfs_quota_acct_enabled "$SCRATCH_DEV" grpquota`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_begin_fstest scrub fsstress_scrub`, `_scratch_xfs_stress_scrub_cleanup &> /dev/null`, `_scratch_mkfs > "$seqres.full" 2>&1`, `_scratch_mount`, `_scratch_xfs_stress_scrub -s "scrub grpquota"`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is `_scratch_xfs_stress_scrub`, its cleanup hook, selected scrub command strings, fsstress operation exclusion flags, and feature gates for realtime, quota, reflink, attributes, rmapbt, or finobt when required. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is nondeterminism: the expected signal is absence of crashes, livelocks, and scrub infrastructure failures, so runtime, load factor, feature availability, and cleanup correctness matter more than fixed stdout. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 584`; `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/584 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/585 -->
# sources/test-tools/xfstests/tests/xfs/585

## Purpose

Race fsstress and project quota scrub for a while to see if we crash or livelock. This file belongs to the scrub stress race suite. It formats and mounts scratch XFS, starts common/xfs stress-scrub orchestration, and races fsstress or fsx style mutation against one scrub or online-repair target.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest scrub fsstress_scrub` and imports common modules: `preamble`, `filter`, `fuzzy`, `inject`, `xfs`, `quota`. Local helper functions: `_cleanup`. Key environment variables or shell state names include only standard xfstests variables such as `SCRATCH_MNT`, `SCRATCH_DEV`, `seqres`, and `tmp` are used

Requirements and feature gates: `_require_scratch`, `_require_xfs_stress_scrub`, `_require_xfs_quota_acct_enabled "$SCRATCH_DEV" prjquota`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_begin_fstest scrub fsstress_scrub`, `_scratch_xfs_stress_scrub_cleanup &> /dev/null`, `_scratch_mkfs > "$seqres.full" 2>&1`, `_scratch_mount`, `_scratch_xfs_stress_scrub -s "scrub prjquota"`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is `_scratch_xfs_stress_scrub`, its cleanup hook, selected scrub command strings, fsstress operation exclusion flags, and feature gates for realtime, quota, reflink, attributes, rmapbt, or finobt when required. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is nondeterminism: the expected signal is absence of crashes, livelocks, and scrub infrastructure failures, so runtime, load factor, feature availability, and cleanup correctness matter more than fixed stdout. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 585`; `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/585 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/586 -->
# sources/test-tools/xfstests/tests/xfs/586

## Purpose

Race fsstress and summary counters scrub for a while to see if we crash or livelock. This file belongs to the scrub stress race suite. It formats and mounts scratch XFS, starts common/xfs stress-scrub orchestration, and races fsstress or fsx style mutation against one scrub or online-repair target.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest scrub fsstress_scrub` and imports common modules: `preamble`, `filter`, `fuzzy`, `inject`, `xfs`. Local helper functions: `_cleanup`. Key environment variables or shell state names include only standard xfstests variables such as `SCRATCH_MNT`, `SCRATCH_DEV`, `seqres`, and `tmp` are used

Requirements and feature gates: `_require_scratch`, `_require_xfs_stress_scrub`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_begin_fstest scrub fsstress_scrub`, `_scratch_xfs_stress_scrub_cleanup &> /dev/null`, `_scratch_mkfs > "$seqres.full" 2>&1`, `_scratch_mount`, `_scratch_xfs_stress_scrub -s "scrub fscounters"`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is `_scratch_xfs_stress_scrub`, its cleanup hook, selected scrub command strings, fsstress operation exclusion flags, and feature gates for realtime, quota, reflink, attributes, rmapbt, or finobt when required. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is nondeterminism: the expected signal is absence of crashes, livelocks, and scrub infrastructure failures, so runtime, load factor, feature availability, and cleanup correctness matter more than fixed stdout. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 586`; `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/586 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/587 -->
# sources/test-tools/xfstests/tests/xfs/587

## Purpose

Race fsstress and inode record scrub for a while to see if we crash or livelock. This file belongs to the scrub stress race suite. It formats and mounts scratch XFS, starts common/xfs stress-scrub orchestration, and races fsstress or fsx style mutation against one scrub or online-repair target.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest scrub fsstress_scrub` and imports common modules: `preamble`, `filter`, `fuzzy`, `inject`, `xfs`. Local helper functions: `_cleanup`. Key environment variables or shell state names include only standard xfstests variables such as `SCRATCH_MNT`, `SCRATCH_DEV`, `seqres`, and `tmp` are used

Requirements and feature gates: `_require_scratch`, `_require_xfs_stress_scrub`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_begin_fstest scrub fsstress_scrub`, `_scratch_xfs_stress_scrub_cleanup &> /dev/null`, `_scratch_mkfs > "$seqres.full" 2>&1`, `_scratch_mount`, `_scratch_xfs_stress_scrub -s "scrub inode" -t "%file%"`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is `_scratch_xfs_stress_scrub`, its cleanup hook, selected scrub command strings, fsstress operation exclusion flags, and feature gates for realtime, quota, reflink, attributes, rmapbt, or finobt when required. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is nondeterminism: the expected signal is absence of crashes, livelocks, and scrub infrastructure failures, so runtime, load factor, feature availability, and cleanup correctness matter more than fixed stdout. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 587`; `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/587 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/588 -->
# sources/test-tools/xfstests/tests/xfs/588

## Purpose

Race fsstress and data fork scrub for a while to see if we crash or livelock. This file belongs to the scrub stress race suite. It formats and mounts scratch XFS, starts common/xfs stress-scrub orchestration, and races fsstress or fsx style mutation against one scrub or online-repair target.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest scrub fsstress_scrub` and imports common modules: `preamble`, `filter`, `fuzzy`, `inject`, `xfs`. Local helper functions: `_cleanup`. Key environment variables or shell state names include only standard xfstests variables such as `SCRATCH_MNT`, `SCRATCH_DEV`, `seqres`, and `tmp` are used

Requirements and feature gates: `_require_scratch`, `_require_xfs_stress_scrub`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_begin_fstest scrub fsstress_scrub`, `_scratch_xfs_stress_scrub_cleanup &> /dev/null`, `_scratch_mkfs > "$seqres.full" 2>&1`, `_scratch_mount`, `_scratch_xfs_stress_scrub -s "scrub bmapbtd" -t "%datafile%"`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is `_scratch_xfs_stress_scrub`, its cleanup hook, selected scrub command strings, fsstress operation exclusion flags, and feature gates for realtime, quota, reflink, attributes, rmapbt, or finobt when required. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is nondeterminism: the expected signal is absence of crashes, livelocks, and scrub infrastructure failures, so runtime, load factor, feature availability, and cleanup correctness matter more than fixed stdout. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 588`; `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/588 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/589 -->
# sources/test-tools/xfstests/tests/xfs/589

## Purpose

Race fsstress and attr fork scrub for a while to see if we crash or livelock. This file belongs to the scrub stress race suite. It formats and mounts scratch XFS, starts common/xfs stress-scrub orchestration, and races fsstress or fsx style mutation against one scrub or online-repair target.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest scrub fsstress_scrub` and imports common modules: `preamble`, `filter`, `fuzzy`, `inject`, `xfs`, `attr`. Local helper functions: `_cleanup`. Key environment variables or shell state names include only standard xfstests variables such as `SCRATCH_MNT`, `SCRATCH_DEV`, `seqres`, and `tmp` are used

Requirements and feature gates: `_require_scratch`, `_require_attrs`, `_require_xfs_stress_scrub`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_begin_fstest scrub fsstress_scrub`, `_scratch_xfs_stress_scrub_cleanup &> /dev/null`, `_scratch_mkfs > "$seqres.full" 2>&1`, `_scratch_mount`, `_scratch_xfs_stress_scrub -x 'xattr' -s "scrub bmapbta" -t "%attrfile%"`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is `_scratch_xfs_stress_scrub`, its cleanup hook, selected scrub command strings, fsstress operation exclusion flags, and feature gates for realtime, quota, reflink, attributes, rmapbt, or finobt when required. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is nondeterminism: the expected signal is absence of crashes, livelocks, and scrub infrastructure failures, so runtime, load factor, feature availability, and cleanup correctness matter more than fixed stdout. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 589`; `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/589 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/590 -->
# sources/test-tools/xfstests/tests/xfs/590

## Purpose

Race fsstress and cow fork scrub for a while to see if we crash or livelock. This file belongs to the scrub stress race suite. It formats and mounts scratch XFS, starts common/xfs stress-scrub orchestration, and races fsstress or fsx style mutation against one scrub or online-repair target.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest scrub fsstress_scrub` and imports common modules: `preamble`, `filter`, `fuzzy`, `inject`, `xfs`, `reflink`. Local helper functions: `_cleanup`. Key environment variables or shell state names include only standard xfstests variables such as `SCRATCH_MNT`, `SCRATCH_DEV`, `seqres`, and `tmp` are used

Requirements and feature gates: `_require_scratch`, `_require_xfs_stress_scrub`, `_require_xfs_has_feature "$SCRATCH_MNT" reflink`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_begin_fstest scrub fsstress_scrub`, `_scratch_xfs_stress_scrub_cleanup &> /dev/null`, `_scratch_mkfs > "$seqres.full" 2>&1`, `_scratch_mount`, `_scratch_xfs_stress_scrub -s "scrub bmapbtc" -t "%cowfile%"`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is `_scratch_xfs_stress_scrub`, its cleanup hook, selected scrub command strings, fsstress operation exclusion flags, and feature gates for realtime, quota, reflink, attributes, rmapbt, or finobt when required. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is nondeterminism: the expected signal is absence of crashes, livelocks, and scrub infrastructure failures, so runtime, load factor, feature availability, and cleanup correctness matter more than fixed stdout. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 590`; `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/590 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/591 -->
# sources/test-tools/xfstests/tests/xfs/591

## Purpose

Race fsstress and directory scrub for a while to see if we crash or livelock. This file belongs to the scrub stress race suite. It formats and mounts scratch XFS, starts common/xfs stress-scrub orchestration, and races fsstress or fsx style mutation against one scrub or online-repair target.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest scrub fsstress_scrub` and imports common modules: `preamble`, `filter`, `fuzzy`, `inject`, `xfs`. Local helper functions: `_cleanup`. Key environment variables or shell state names include only standard xfstests variables such as `SCRATCH_MNT`, `SCRATCH_DEV`, `seqres`, and `tmp` are used

Requirements and feature gates: `_require_scratch`, `_require_xfs_stress_scrub`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_begin_fstest scrub fsstress_scrub`, `_scratch_xfs_stress_scrub_cleanup &> /dev/null`, `_scratch_mkfs > "$seqres.full" 2>&1`, `_scratch_mount`, `_scratch_xfs_stress_scrub -x 'dir' -s "scrub directory" -t "%dir%"`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is `_scratch_xfs_stress_scrub`, its cleanup hook, selected scrub command strings, fsstress operation exclusion flags, and feature gates for realtime, quota, reflink, attributes, rmapbt, or finobt when required. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is nondeterminism: the expected signal is absence of crashes, livelocks, and scrub infrastructure failures, so runtime, load factor, feature availability, and cleanup correctness matter more than fixed stdout. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 591`; `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/591 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/592 -->
# sources/test-tools/xfstests/tests/xfs/592

## Purpose

Race fsstress and extended attributes scrub for a while to see if we crash or livelock. This file belongs to the scrub stress race suite. It formats and mounts scratch XFS, starts common/xfs stress-scrub orchestration, and races fsstress or fsx style mutation against one scrub or online-repair target.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest scrub fsstress_scrub` and imports common modules: `preamble`, `filter`, `fuzzy`, `inject`, `xfs`, `attr`. Local helper functions: `_cleanup`. Key environment variables or shell state names include only standard xfstests variables such as `SCRATCH_MNT`, `SCRATCH_DEV`, `seqres`, and `tmp` are used

Requirements and feature gates: `_require_scratch`, `_require_attrs`, `_require_xfs_stress_scrub`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_begin_fstest scrub fsstress_scrub`, `_scratch_xfs_stress_scrub_cleanup &> /dev/null`, `_scratch_mkfs > "$seqres.full" 2>&1`, `_scratch_mount`, `_scratch_xfs_stress_scrub -x 'xattr' -s "scrub xattr" -t "%attrfile%"`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is `_scratch_xfs_stress_scrub`, its cleanup hook, selected scrub command strings, fsstress operation exclusion flags, and feature gates for realtime, quota, reflink, attributes, rmapbt, or finobt when required. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is nondeterminism: the expected signal is absence of crashes, livelocks, and scrub infrastructure failures, so runtime, load factor, feature availability, and cleanup correctness matter more than fixed stdout. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 592`; `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/592 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/593 -->
# sources/test-tools/xfstests/tests/xfs/593

## Purpose

Race fsstress and parent pointers scrub for a while to see if we crash or livelock. This file belongs to the scrub stress race suite. It formats and mounts scratch XFS, starts common/xfs stress-scrub orchestration, and races fsstress or fsx style mutation against one scrub or online-repair target.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest scrub fsstress_scrub` and imports common modules: `preamble`, `filter`, `fuzzy`, `inject`, `xfs`. Local helper functions: `_cleanup`. Key environment variables or shell state names include only standard xfstests variables such as `SCRATCH_MNT`, `SCRATCH_DEV`, `seqres`, and `tmp` are used

Requirements and feature gates: `_require_scratch`, `_require_xfs_stress_scrub`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_begin_fstest scrub fsstress_scrub`, `_scratch_xfs_stress_scrub_cleanup &> /dev/null`, `_scratch_mkfs > "$seqres.full" 2>&1`, `_scratch_mount`, `_scratch_xfs_stress_scrub -s "scrub parent" -t "%dir%"`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is `_scratch_xfs_stress_scrub`, its cleanup hook, selected scrub command strings, fsstress operation exclusion flags, and feature gates for realtime, quota, reflink, attributes, rmapbt, or finobt when required. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is nondeterminism: the expected signal is absence of crashes, livelocks, and scrub infrastructure failures, so runtime, load factor, feature availability, and cleanup correctness matter more than fixed stdout. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 593`; `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/593 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/594 -->
# sources/test-tools/xfstests/tests/xfs/594

## Purpose

Race fsstress and symlink scrub for a while to see if we crash or livelock. We can't open symlink files directly for scrubbing, so we use xfs_scrub(8). This file belongs to the scrub stress race suite. It formats and mounts scratch XFS, starts common/xfs stress-scrub orchestration, and races fsstress or fsx style mutation against one scrub or online-repair target.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest scrub fsstress_scrub` and imports common modules: `preamble`, `filter`, `fuzzy`, `inject`, `xfs`. Local helper functions: `_cleanup`. Key environment variables or shell state names include `XFS_SCRUB_PHASE`.

Requirements and feature gates: `_require_scratch`, `_require_xfs_stress_scrub`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_begin_fstest scrub fsstress_scrub`, `_scratch_xfs_stress_scrub_cleanup &> /dev/null`, `_scratch_mkfs > "$seqres.full" 2>&1`, `_scratch_mount`, `XFS_SCRUB_PHASE=3 _scratch_xfs_stress_scrub -x 'symlink' -S '-n'`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is `_scratch_xfs_stress_scrub`, its cleanup hook, selected scrub command strings, fsstress operation exclusion flags, and feature gates for realtime, quota, reflink, attributes, rmapbt, or finobt when required. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is nondeterminism: the expected signal is absence of crashes, livelocks, and scrub infrastructure failures, so runtime, load factor, feature availability, and cleanup correctness matter more than fixed stdout. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 594`; `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/594 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/595 -->
# sources/test-tools/xfstests/tests/xfs/595

## Purpose

Race fsstress and special file scrub for a while to see if we crash or livelock.  We can't open special files directly for scrubbing, so we use xfs_scrub(8). This file belongs to the scrub stress race suite. It formats and mounts scratch XFS, starts common/xfs stress-scrub orchestration, and races fsstress or fsx style mutation against one scrub or online-repair target.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest scrub fsstress_scrub` and imports common modules: `preamble`, `filter`, `fuzzy`, `inject`, `xfs`. Local helper functions: `_cleanup`. Key environment variables or shell state names include `XFS_SCRUB_PHASE`.

Requirements and feature gates: `_require_scratch`, `_require_xfs_stress_scrub`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_begin_fstest scrub fsstress_scrub`, `_scratch_xfs_stress_scrub_cleanup &> /dev/null`, `_scratch_mkfs > "$seqres.full" 2>&1`, `_scratch_mount`, `XFS_SCRUB_PHASE=3 _scratch_xfs_stress_scrub -x 'mknod' -S '-n'`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is `_scratch_xfs_stress_scrub`, its cleanup hook, selected scrub command strings, fsstress operation exclusion flags, and feature gates for realtime, quota, reflink, attributes, rmapbt, or finobt when required. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is nondeterminism: the expected signal is absence of crashes, livelocks, and scrub infrastructure failures, so runtime, load factor, feature availability, and cleanup correctness matter more than fixed stdout. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 595`; `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/595 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/596 -->
# sources/test-tools/xfstests/tests/xfs/596

## Purpose

growfs QA tests - repeatedly fill/grow the rt volume of the filesystem check the filesystem contents after each operation.  This is the rt equivalent of xfs/041. This is the realtime-device equivalent of a growfs fill-and-verify test. It repeatedly fills the filesystem, grows the realtime volume to specific sizes, remounts, and checks the file manifest.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest growfs ioctl auto` and imports common modules: `preamble`, `filter`. Local helper functions: `_cleanup`, `_fill`. Key environment variables or shell state names include `_do_die_on_error`, `grow_size`, `onemeginblocks`, `rtsize`.

Requirements and feature gates: `_require_scratch`, `_require_realtime`, `_require_no_large_scratch_dev`, `_require_xfs_scratch_non_zoned`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_unmount`, `_scratch_unmount 2>/dev/null`, `"$here/src/fill2fs --verbose --dir=$1 --seed=0 --filesize=65536 --stddev=32768 --list=- >>$tmp.manifest"`, `_scratch_mkfs_xfs -rsize=${rtsize}m | _filter_mkfs 2> "$tmp.mkfs" >> $seqres.full`, `_scratch_mount`, `_xfs_force_bdev realtime $SCRATCH_MNT`, `_do "Grow filesystem to ${size}m" "xfs_growfs -R $grow_size $SCRATCH_MNT"`, `_do "_scratch_unmount"`; plus 2 more.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is realtime scratch devices, `xfs_growfs -R`, fill2fs/fill2fs_check manifests, non-zoned constraints, and forced realtime allocation. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is capacity and geometry sensitivity: realtime extents, zoned-device alignment, and manifest durability must line up or the test can fail before exercising growfs correctness. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 596`; `Make 32 megabyte rt filesystem on SCRATCH_DEV and mount... done`; `Fill filesystem... done`; `Grow filesystem to 33m... done`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/596 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/597 -->
# sources/test-tools/xfstests/tests/xfs/597

## Purpose

Make sure that the kernel and userspace agree on which byte sequences are ASCII uppercase letters, and how to convert them. This file targets ASCII case-insensitive directory semantics. It builds leaf-format directories or attributes with names that stress kernel/userspace case folding and obfuscation behavior.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto ci dir` and imports common modules: `preamble`, `filter`. Local helper functions: none Key environment variables or shell state names include `dblksz`, `dirsz`, `i`, `name`, `nr_dirents`.

Requirements and feature gates: `_require_scratch`, `_require_xfs_mkfs_ciname`, `_require_xfs_ciname`. Recorded fix annotations: `_fixed_by_kernel_commit a9248538facc xfs: stabilize the dirent name transformation function used for ascii-ci dir hash computation`, `_fixed_by_kernel_commit 9dceccc5822f xfs: use the directory name hash function for dir scrubbing`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_mkfs -n version=ci > $seqres.full`, `_scratch_mount`, `dblksz=$(_xfs_get_dir_blocksize "$SCRATCH_MNT")`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is mkfs `-n version=ci`, XFS case-insensitive name helpers, directory block sizing, metadump or repair verification, and locale-sensitive byte generation. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is locale and name-transformation drift; the script requires `LANG=C` where byte generation must not become UTF-8 text processing. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 597`; `ln: failed to create hard link 'SCRATCH_MNT/lol/'$'\340': File exists`; `ln: failed to create hard link 'SCRATCH_MNT/lol/'$'\341': File exists`; `ln: failed to create hard link 'SCRATCH_MNT/lol/'$'\342': File exists`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/597 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/598 -->
# sources/test-tools/xfstests/tests/xfs/598

## Purpose

Make sure that metadump obfuscation works for filesystems with ascii-ci enabled. This file validates metadump/mdrestore round trips. It creates a populated or feature-specific filesystem, emits metadumps with option combinations, restores them, and checks the restored scratch filesystem.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto dir ci` and imports common modules: `preamble`. Local helper functions: `_cleanup`. Key environment variables or shell state names include `dblksz`, `dirsz`, `i`, `metadump_file`, `metadump_file_a`, `metadump_file_ao`, `metadump_file_o`, `name`, `nr_dirents`, `testdir`.

Requirements and feature gates: `_require_test`, `_require_scratch`, `_require_xfs_mkfs_ciname`, `_require_xfs_ciname`, `_require_scratch_xfs_mdrestore`. Recorded fix annotations: `_fixed_by_git_commit xfsprogs 10a01bcd xfs_db: fix metadump name obfuscation for ascii-ci filesystems`, `_fixed_by_kernel_commit a9248538facc xfs: stabilize the dirent name transformation function used for ascii-ci dir hash computation`, `_fixed_by_kernel_commit 9dceccc5822f xfs: use the directory name hash function for dir scrubbing`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `"xfs_db: fix metadump name obfuscation for ascii-ci filesystems"`, `_scratch_mkfs -n version=ci > $seqres.full`, `_scratch_mount`, `dblksz=$(_xfs_get_dir_blocksize "$SCRATCH_MNT")`, `_scratch_unmount`, `_scratch_xfs_metadump $metadump_file >> $seqres.full`, `_scratch_xfs_metadump $metadump_file_a -a >> $seqres.full`, `_scratch_xfs_metadump $metadump_file_o -o >> $seqres.full`; plus 6 more.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is xfs_metadump, xfs_mdrestore, loop or scratch restore plumbing, populated test images, and online/offline rebuild skips used to keep verification focused on dump fidelity. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is that obfuscation, feature flags, or restore-device setup can turn a metadata serialization regression into an environment failure; restored filesystems must always be checked after each option variant. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 598`; `metadump`; `metadump a`; `metadump o`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/598 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/599 -->
# sources/test-tools/xfstests/tests/xfs/599

## Purpose

Make sure that the kernel and utilities can handle large numbers of dirhash collisions in both the directory and extended attribute structures. This started as a regression test for the new 'hashcoll' function in xfs_db, but became a regression test for an xfs_repair bug affecting hashval checks applied to the second and higher node levels of a dabtree. This file creates extreme directory and xattr hash-collision trees to validate kernel and xfsprogs handling of deep dabtrees with repeated hash values.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto dir` and imports common modules: `preamble`. Local helper functions: `filter_hashvals`. Key environment variables or shell state names include `attr_count`, `attr_db_args`, `blksz`, `crash_attrs`, `crash_dir`, `da_node_block_offset`, `da_records_per_block`, `dblksz`, `dir_count`, `dir_db_args`; plus 3 more.

Requirements and feature gates: `_require_xfs_db_command "hashcoll"`, `_require_xfs_db_command "path"`, `_require_scratch`. Recorded fix annotations: `_fixed_by_git_commit xfsprogs b7b81f336ac xfs_repair: fix incorrect dabtree hashval comparison`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `"xfs_repair: fix incorrect dabtree hashval comparison"`, `_scratch_mkfs > $seqres.full`, `_scratch_mount`, `dblksz=$(_xfs_get_dir_blocksize "$SCRATCH_MNT")`, `_scratch_xfs_db -r -c "hashcoll -n $nr_dirents -p $crash_dir $longname"`, `_scratch_xfs_db -r -c "hashcoll -a -n $nr_attrs -p $crash_attrs $longname"`, `_scratch_unmount`, `dir_count="$(_scratch_xfs_db "${dir_db_args[@]}" -c 'print lhdr.count' | awk '{print $3}')"`; plus 3 more.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is xfs_db `hashcoll` and `path`, directory/attribute dabtree addressing, hash-value inspection, remount coverage, and later repair checks. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is that directory block sizing or name length assumptions may fail to create a two-level dabtree, which would leave the repair hash comparison path untested. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 599`; `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/599 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/600 -->
# sources/test-tools/xfstests/tests/xfs/600

## Purpose

Regression test for an agbno overflow bug in XFS GETFSMAP involving an fsmap_advance call.  Userspace can indicate that a GETFSMAP call is actually a continuation of a previous call by setting the "low" key to the last record returned by the previous call. If the last record returned by GETFSMAP is a non-shareable extent at the end of an AG and the AG size is exactly a power of two, the startblock in the low key of the rmapbt query can be set to a value larger than EOAG.  When this happens, GETFSMAP will return EINVAL instead of returning records for the next AG. This is a focused xfstests shell regression. It encodes an XFS behavior, userspace-tool contract, or maintenance check as a scratch/test filesystem scenario.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto quick fsmap` and imports common modules: `preamble`, `filter`. Local helper functions: none Key environment variables or shell state names include `desired_agsize`.

Requirements and feature gates: `_require_xfs_io_command fsmap`, `_require_xfs_scratch_rmapbt`. Recorded fix annotations: `_fixed_by_git_commit kernel cfa2df68b7ce xfs: fix an agbno overflow in __xfs_getfsmap_datadev`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_begin_fstest auto quick fsmap`, `"xfs: fix an agbno overflow in __xfs_getfsmap_datadev"`, `_scratch_mkfs | _filter_mkfs 2> $tmp.mkfs >> $seqres.full`, `_scratch_mkfs -d "agsize=${desired_agsize}b" | _filter_mkfs 2> $tmp.mkfs >> $seqres.full`, `_scratch_mount`, `$XFS_IO_PROG -c 'fsmap -n 1024 -v' $SCRATCH_MNT >> $tmp.big`, `$XFS_IO_PROG -c 'fsmap -n 1 -v' $SCRATCH_MNT >> $tmp.small`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is the xfstests common harness, scratch filesystem lifecycle helpers, xfsprogs commands, and golden-output filtering through `seqres.full` and `.out` files. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is environment sensitivity: missing xfsprogs features, kernel feature flags, scratch geometry, runtime load, or non-normalized diagnostics can produce false failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 600`; `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/600 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/601 -->
# sources/test-tools/xfstests/tests/xfs/601

## Purpose

Populate a XFS filesystem and ensure that xfs_copy works properly. This is a focused xfstests shell regression. It encodes an XFS behavior, userspace-tool contract, or maintenance check as a scratch/test filesystem scenario.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto copy` and imports common modules: `preamble`, `filter`, `populate`. Local helper functions: `_cleanup`. Key environment variables or shell state names include `copy_file`, `testdir`.

Requirements and feature gates: `_require_xfs_copy`, `_require_scratch_nocheck`, `_require_populate_commands`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_xfs_skip_online_rebuild`, `_xfs_skip_offline_rebuild`, `_scratch_populate_cached nofill > $seqres.full 2>&1`, `$XFS_COPY_PROG $SCRATCH_DEV $copy_file >> $seqres.full`, `$XFS_COPY_PROG $copy_file $SCRATCH_DEV >> $seqres.full`, `_scratch_mount`, `_check_scratch_fs`, `_scratch_unmount`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is the xfstests common harness, scratch filesystem lifecycle helpers, xfsprogs commands, and golden-output filtering through `seqres.full` and `.out` files. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is environment sensitivity: missing xfsprogs features, kernel feature flags, scratch geometry, runtime load, or non-normalized diagnostics can produce false failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 601`; `Format and populate`; `copy`; `recopy`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/601 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/602 -->
# sources/test-tools/xfstests/tests/xfs/602

## Purpose

Test using runtime code to fix unlinked inodes on a clean filesystem that never got cleaned up. This file tests runtime repair of synthesized unlinked-inode lists on a clean filesystem. It creates iunlink buckets with xfs_db, then checks recovery through normal runtime, bulkstat, and optional quotacheck paths.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto quick unlink` and imports common modules: `preamble`, `filter`, `fuzzy`, `quota`. Local helper functions: `__repair_check_scratch`, `exercise_scratch`, `final_check_scratch`, `format_scratch`. Key environment variables or shell state names include `IUNLINK_BUCKETLEN`, `MOUNT_OPTIONS`, `XFS_AGI_UNLINKED_BUCKETS`, `orig_mount_options`, `res`.

Requirements and feature gates: `_require_xfs_db_command iunlink`, `_require_scratch_nocheck	# we'll run repair ourselves`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_mkfs -d agcount=1 | _filter_mkfs 2> "${tmp}.mkfs" >> $seqres.full`, `local nr_iunlinks="$((IUNLINK_BUCKETLEN * XFS_AGI_UNLINKED_BUCKETS))"`, `readarray -t BADINODES < <(_scratch_xfs_db -x -c "iunlink -n $nr_iunlinks" | awk '{print $4}')`, `_scratch_xfs_repair -o force_geometry -n 2>&1 | \`, `_scratch_mount`, `_scratch_unmount`, `echo "+ Part 1: See if bulkstat can recover the unlinked list" | tee -a $seqres.full`, `$XFS_IO_PROG -c 'bulkstat' $SCRATCH_MNT > /dev/null`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is xfs_db `iunlink`, one-AG scratch geometry, unlinked bucket constants, bulkstat, quota mount options, and offline repair in no-modify mode as the final oracle. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is that quotacheck or offline repair can clean up too early or report geometry complaints unrelated to iunlink recovery, so the script controls quota state and uses force_geometry for checking. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 602`; `+ Part 0: See if runtime can recover the unlinked list`; `+ Part 1: See if bulkstat can recover the unlinked list`; `+ Part 2: See if quotacheck can recover the unlinked list`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/602 -->
