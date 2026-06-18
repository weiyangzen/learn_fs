# subset-b-009546 research

Grouped research report for xfstests generic tests 216 through 366. Each section preserves the source path in the title and is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/216 -->
# sources/test-tools/xfstests/tests/generic/216

## Purpose

See what happens if we CoW blocks 2-4 of a page's worth of blocks when the second block is a unwritten block This test is dependent on the system page size, so we cannot use md5 in the golden output; we can only compare to a check file. It is registered with `_begin_fstest auto quick clone prealloc` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `216` plus `_begin_fstest auto quick clone prealloc`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`. Capability gates: `_require_scratch_reflink`, `_require_xfs_io_command "falloc"`. Local functions: `_cleanup`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 30: `pagesz=$(getconf PAGE_SIZE)`
- Line 31: `blksz=$((pagesz / 4))`
- Line 37: `testdir=$SCRATCH_MNT/test-$seq`
- Line 40: `real_blksz=$(_get_file_block_size $testdir)`
- Line 73: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 33 `echo "Format and mount"`, line 43 `echo "Create the original files"`, line 59 `echo "Compare files"`, line 63 `echo "CoW and unmount"`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 20: `rm -rf $tmp.* $testdir`
- Line 27: `_require_scratch_reflink`
- Line 28: `_require_xfs_io_command "falloc"`
- Line 33: `echo "Format and mount"`
- Line 34: `_scratch_mkfs_blocksized $blksz > $seqres.full 2>&1`
- Line 35: `_scratch_mount >> $seqres.full 2>&1`
- Line 38: `mkdir $testdir`
- Line 44: `_pwrite_byte 0x61 0 $pagesz $testdir/file1 >> $seqres.full`
- Line 46: `$XFS_IO_PROG -f -c "truncate $pagesz" $testdir/file2 >> $seqres.full`
- Line 47: `$XFS_IO_PROG -f -c "truncate $pagesz" $testdir/file2.chk >> $seqres.full`
- Line 49: `$XFS_IO_PROG -f -c "falloc -k $blksz $blksz" $testdir/file2 >> $seqres.full`
- Line 50: `_pwrite_byte 0x00 $blksz $blksz $testdir/file2.chk >> $seqres.full`
- Line 52: `$XFS_IO_PROG -f -c "falloc -k $((blksz * 3)) $blksz" $testdir/file2 >> $seqres.full`
- Line 70: `cmp -s $testdir/file2 $testdir/file2.chk || _fail "file2 and file2.chk don't match."`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Cycle-mount calls force metadata and extent state through unmount/remount persistence before validation. Temporary files are rooted at `$tmp.*` and removed by the local or default cleanup path. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `clone`, `prealloc`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`, and uses capability gates such as `_require_scratch_reflink`, `_require_xfs_io_command "falloc"`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Reflink coverage is sensitive to extent alignment, delayed allocation, unwritten extents, and page-size dependent block geometry, so comparisons against check files are the main correctness guard.
- Several checks can intentionally call `_notrun`; this is expected for unsupported geometry or feature combinations and should be distinguished from a failing assertion.

## Test Signals

The pass signal is byte-for-byte `cmp` checks against companion files, explicit `_fail` assertions. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/216 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/217 -->
# sources/test-tools/xfstests/tests/generic/217

## Purpose

See what happens if we DIO CoW blocks 2-4 of a page's worth of blocks when the second block is a unwritten block This test is dependent on the system page size, so we cannot use md5 in the golden output; we can only compare to a check file. It is registered with `_begin_fstest auto quick clone prealloc` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `217` plus `_begin_fstest auto quick clone prealloc`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`. Capability gates: `_require_scratch_reflink`, `_require_xfs_io_command "falloc"`, `_require_odirect`. Local functions: `_cleanup`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 31: `pagesz=$(getconf PAGE_SIZE)`
- Line 32: `blksz=$((pagesz / 4))`
- Line 38: `testdir=$SCRATCH_MNT/test-$seq`
- Line 41: `real_blksz=$(_get_file_block_size $testdir)`
- Line 74: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 34 `echo "Format and mount"`, line 44 `echo "Create the original files"`, line 60 `echo "Compare files"`, line 64 `echo "CoW and unmount"`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 20: `rm -rf $tmp.* $testdir`
- Line 27: `_require_scratch_reflink`
- Line 28: `_require_xfs_io_command "falloc"`
- Line 34: `echo "Format and mount"`
- Line 35: `_scratch_mkfs_blocksized $blksz > $seqres.full 2>&1`
- Line 36: `_scratch_mount >> $seqres.full 2>&1`
- Line 39: `mkdir $testdir`
- Line 45: `_pwrite_byte 0x61 0 $pagesz $testdir/file1 >> $seqres.full`
- Line 47: `$XFS_IO_PROG -f -c "truncate $pagesz" $testdir/file2 >> $seqres.full`
- Line 48: `$XFS_IO_PROG -f -c "truncate $pagesz" $testdir/file2.chk >> $seqres.full`
- Line 50: `$XFS_IO_PROG -f -c "falloc -k $blksz $blksz" $testdir/file2 >> $seqres.full`
- Line 51: `_pwrite_byte 0x00 $blksz $blksz $testdir/file2.chk >> $seqres.full`
- Line 53: `$XFS_IO_PROG -f -c "falloc -k $((blksz * 3)) $blksz" $testdir/file2 >> $seqres.full`
- Line 71: `cmp -s $testdir/file2 $testdir/file2.chk || _fail "file2 and file2.chk don't match."`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Cycle-mount calls force metadata and extent state through unmount/remount persistence before validation. Temporary files are rooted at `$tmp.*` and removed by the local or default cleanup path. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `clone`, `prealloc`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`, and uses capability gates such as `_require_scratch_reflink`, `_require_xfs_io_command "falloc"`, `_require_odirect`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Reflink coverage is sensitive to extent alignment, delayed allocation, unwritten extents, and page-size dependent block geometry, so comparisons against check files are the main correctness guard.
- Direct I/O paths can be affected by device sector size, alignment, cache invalidation, and filesystem-specific serialization between buffered and direct writes.
- Several checks can intentionally call `_notrun`; this is expected for unsupported geometry or feature combinations and should be distinguished from a failing assertion.

## Test Signals

The pass signal is byte-for-byte `cmp` checks against companion files, explicit `_fail` assertions. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/217 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/218 -->
# sources/test-tools/xfstests/tests/generic/218

## Purpose

See what happens if we CoW blocks 2-4 of a page's worth of blocks when the second block is a hole This test is dependent on the system page size, so we cannot use md5 in the golden output; we can only compare to a check file. It is registered with `_begin_fstest auto quick clone prealloc` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `218` plus `_begin_fstest auto quick clone prealloc`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`. Capability gates: `_require_scratch_reflink`, `_require_xfs_io_command "falloc"`. Local functions: `_cleanup`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 30: `pagesz=$(getconf PAGE_SIZE)`
- Line 31: `blksz=$((pagesz / 4))`
- Line 37: `testdir=$SCRATCH_MNT/test-$seq`
- Line 40: `real_blksz=$(_get_file_block_size $testdir)`
- Line 67: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 33 `echo "Format and mount"`, line 43 `echo "Create the original files"`, line 53 `echo "Compare files"`, line 57 `echo "CoW and unmount"`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 20: `rm -rf $tmp.* $testdir`
- Line 27: `_require_scratch_reflink`
- Line 28: `_require_xfs_io_command "falloc"`
- Line 33: `echo "Format and mount"`
- Line 34: `_scratch_mkfs_blocksized $blksz > $seqres.full 2>&1`
- Line 35: `_scratch_mount >> $seqres.full 2>&1`
- Line 38: `mkdir $testdir`
- Line 44: `_pwrite_byte 0x61 0 $pagesz $testdir/file1 >> $seqres.full`
- Line 46: `$XFS_IO_PROG -f -c "truncate $pagesz" $testdir/file2 >> $seqres.full`
- Line 47: `$XFS_IO_PROG -f -c "truncate $pagesz" $testdir/file2.chk >> $seqres.full`
- Line 49: `_reflink_range $testdir/file1 $blksz $testdir/file2 $((blksz * 2)) $blksz >> $seqres.full`
- Line 50: `_pwrite_byte 0x61 $((blksz * 2)) $blksz $testdir/file2.chk >> $seqres.full`
- Line 51: `_scratch_cycle_mount`
- Line 64: `cmp -s $testdir/file2 $testdir/file2.chk || _fail "file2 and file2.chk don't match."`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Cycle-mount calls force metadata and extent state through unmount/remount persistence before validation. Temporary files are rooted at `$tmp.*` and removed by the local or default cleanup path. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `clone`, `prealloc`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`, and uses capability gates such as `_require_scratch_reflink`, `_require_xfs_io_command "falloc"`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Reflink coverage is sensitive to extent alignment, delayed allocation, unwritten extents, and page-size dependent block geometry, so comparisons against check files are the main correctness guard.
- Several checks can intentionally call `_notrun`; this is expected for unsupported geometry or feature combinations and should be distinguished from a failing assertion.

## Test Signals

The pass signal is byte-for-byte `cmp` checks against companion files, explicit `_fail` assertions. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/218 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/219 -->
# sources/test-tools/xfstests/tests/generic/219

## Purpose

Simple quota accounting test for direct/buffered/mmap IO. It is registered with `_begin_fstest auto quota quick mmap` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `219` plus `_begin_fstest auto quota quick mmap`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/quota`. Capability gates: `_require_scratch`, `_require_quota`, `_require_user`, `_require_group`, `_require_odirect`. Local functions: `test_files`, `check_usage`, `_round_up_to_fs_blksz`, `test_accounting`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 37: `wroteblocks=$1`
- Line 38: `wrotefiles=$2`
- Line 65: `io_sz=$(_round_up_to_fs_blksz 48)`
- Line 66: `sz=$(( io_sz * 3 ))`
- Line 84: `id=$qa_user`
- Line 86: `id=$qa_group`
- Line 104: `type=u`
- Line 113: `type=g`

## Control Flow

The visible phases are driven by echo markers such as line 25 `echo; echo "### create files, setting up ownership (type=$type)"`, line 41 `echo "Too few blocks used (type=$type)"`, line 44 `echo "Too many blocks used (type=$type)"`, line 46 `echo "Bad number of inodes used (type=$type)"`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 11: `_begin_fstest auto quota quick mmap`
- Line 17: `_require_scratch`
- Line 26: `rm -f $SCRATCH_MNT/{buffer,direct,mmap}`
- Line 28: `chown $qa_user $SCRATCH_MNT/{buffer,direct,mmap}`
- Line 30: `for file in $SCRATCH_MNT/{buffer,direct,mmap}; do`
- Line 68: `echo "### some controlled buffered, direct and mmapd IO (type=$type)"`
- Line 72: `$XFS_IO_PROG -c 'pwrite 0 48k' -d \`
- Line 75: `$SCRATCH_MNT/mmap >>$seqres.full 2>&1 &`
- Line 80: `$here/src/lstat64 $file | head -2 | _filter_scratch`
- Line 92: `_scratch_unmount 2>/dev/null`
- Line 94: `_scratch_mount "-o usrquota,grpquota"`
- Line 96: `quotacheck -u -g $SCRATCH_MNT 2>/dev/null`
- Line 98: `_scratch_unmount`
- Line 116: `_scratch_unmount 2>/dev/null`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Quota state is persistent filesystem metadata manipulated through `quotacheck`, `quotaon`, `setquota`, and `repquota` across user and group modes. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quota`, `quick`, `mmap`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/quota`, and uses capability gates such as `_require_scratch`, `_require_quota`, `_require_user`, `_require_group`, `_require_odirect`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Quota tests depend on kernel quota mode, grace-period timing, and the qa user/group setup; stale quota files or unsupported VFS quota behavior can turn a real failure into a notrun or noisy output mismatch.
- Direct I/O paths can be affected by device sector size, alignment, cache invalidation, and filesystem-specific serialization between buffered and direct writes.
- mmap tests rely on page-cache writeback, timestamp granularity, and correct handling of dirty mappings across fsync, sync, or remount boundaries.

## Test Signals

The pass signal is quota usage/enforcement reports, stat/lstat metadata output. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/219 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/220 -->
# sources/test-tools/xfstests/tests/generic/220

## Purpose

See what happens if we DIO CoW blocks 2-4 of a page's worth of blocks when the second block is a unwritten block This test is dependent on the system page size, so we cannot use md5 in the golden output; we can only compare to a check file. It is registered with `_begin_fstest auto quick clone prealloc` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `220` plus `_begin_fstest auto quick clone prealloc`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`. Capability gates: `_require_scratch_reflink`, `_require_xfs_io_command "falloc"`, `_require_odirect`. Local functions: `_cleanup`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 31: `pagesz=$(getconf PAGE_SIZE)`
- Line 32: `blksz=$((pagesz / 4))`
- Line 38: `testdir=$SCRATCH_MNT/test-$seq`
- Line 41: `real_blksz=$(_get_file_block_size $testdir)`
- Line 68: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 34 `echo "Format and mount"`, line 44 `echo "Create the original files"`, line 54 `echo "Compare files"`, line 58 `echo "CoW and unmount"`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 20: `rm -rf $tmp.* $testdir`
- Line 27: `_require_scratch_reflink`
- Line 28: `_require_xfs_io_command "falloc"`
- Line 34: `echo "Format and mount"`
- Line 35: `_scratch_mkfs_blocksized $blksz > $seqres.full 2>&1`
- Line 36: `_scratch_mount >> $seqres.full 2>&1`
- Line 39: `mkdir $testdir`
- Line 45: `_pwrite_byte 0x61 0 $pagesz $testdir/file1 >> $seqres.full`
- Line 47: `$XFS_IO_PROG -f -c "truncate $pagesz" $testdir/file2 >> $seqres.full`
- Line 48: `$XFS_IO_PROG -f -c "truncate $pagesz" $testdir/file2.chk >> $seqres.full`
- Line 50: `_reflink_range $testdir/file1 $blksz $testdir/file2 $((blksz * 2)) $blksz >> $seqres.full`
- Line 51: `_pwrite_byte 0x61 $((blksz * 2)) $blksz $testdir/file2.chk >> $seqres.full`
- Line 52: `_scratch_cycle_mount`
- Line 65: `cmp -s $testdir/file2 $testdir/file2.chk || _fail "file2 and file2.chk don't match."`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Cycle-mount calls force metadata and extent state through unmount/remount persistence before validation. Temporary files are rooted at `$tmp.*` and removed by the local or default cleanup path. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `clone`, `prealloc`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`, and uses capability gates such as `_require_scratch_reflink`, `_require_xfs_io_command "falloc"`, `_require_odirect`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Reflink coverage is sensitive to extent alignment, delayed allocation, unwritten extents, and page-size dependent block geometry, so comparisons against check files are the main correctness guard.
- Direct I/O paths can be affected by device sector size, alignment, cache invalidation, and filesystem-specific serialization between buffered and direct writes.
- Several checks can intentionally call `_notrun`; this is expected for unsupported geometry or feature combinations and should be distinguished from a failing assertion.

## Test Signals

The pass signal is byte-for-byte `cmp` checks against companion files, explicit `_fail` assertions. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/220 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/221 -->
# sources/test-tools/xfstests/tests/generic/221

## Purpose

Check ctime updates when calling futimens without UTIME_OMIT for the mtime entry Based on a bug report and testcase from Eric Blake <ebb9@byu.net>. It is registered with `_begin_fstest auto metadata quick` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `221` plus `_begin_fstest auto metadata quick`. Imported libraries: `. ./common/preamble`. Capability gates: `_require_test`. Local functions: none. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 23: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 19 `echo "Silence is golden."`. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 17: `_require_test`

## State and Persistence Behavior

Primary state lives under `$TEST_DIR`, making this a test-device workload rather than a scratch-device destructive test. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `metadata`, `quick`, imports `. ./common/preamble`, and uses capability gates such as `_require_test`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- The main risk is environment drift: missing helper binaries, unsupported filesystem operations, or output formatting changes can make the test skip or fail without indicating a filesystem regression.

## Test Signals

The pass signal is silence from the helper program and final `status=0`. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/221 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/222 -->
# sources/test-tools/xfstests/tests/generic/222

## Purpose

See what happens if we CoW blocks 2-4 of a page's worth of blocks when the second block is delalloc This test is dependent on the system page size, so we cannot use md5 in the golden output; we can only compare to a check file. It is registered with `_begin_fstest auto quick clone prealloc` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `222` plus `_begin_fstest auto quick clone prealloc`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`. Capability gates: `_require_scratch_reflink`, `_require_xfs_io_command "falloc"`. Local functions: `_cleanup`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 30: `pagesz=$(getconf PAGE_SIZE)`
- Line 31: `blksz=$((pagesz / 4))`
- Line 37: `testdir=$SCRATCH_MNT/test-$seq`
- Line 40: `real_blksz=$(_get_file_block_size $testdir)`
- Line 73: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 33 `echo "Format and mount"`, line 43 `echo "Create the original files"`, line 53 `echo "Compare files"`, line 57 `echo "CoW and unmount"`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 20: `rm -rf $tmp.* $testdir`
- Line 27: `_require_scratch_reflink`
- Line 28: `_require_xfs_io_command "falloc"`
- Line 33: `echo "Format and mount"`
- Line 34: `_scratch_mkfs_blocksized $blksz > $seqres.full 2>&1`
- Line 35: `_scratch_mount >> $seqres.full 2>&1`
- Line 38: `mkdir $testdir`
- Line 44: `_pwrite_byte 0x61 0 $pagesz $testdir/file1 >> $seqres.full`
- Line 46: `$XFS_IO_PROG -f -c "truncate $pagesz" $testdir/file2 >> $seqres.full`
- Line 47: `$XFS_IO_PROG -f -c "truncate $pagesz" $testdir/file2.chk >> $seqres.full`
- Line 49: `_reflink_range $testdir/file1 $blksz $testdir/file2 $((blksz * 2)) $blksz >> $seqres.full`
- Line 50: `_pwrite_byte 0x61 $((blksz * 2)) $blksz $testdir/file2.chk >> $seqres.full`
- Line 51: `_scratch_cycle_mount`
- Line 70: `cmp -s $testdir/file2 $testdir/file2.chk || _fail "file2 and file2.chk don't match."`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Cycle-mount calls force metadata and extent state through unmount/remount persistence before validation. Temporary files are rooted at `$tmp.*` and removed by the local or default cleanup path. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `clone`, `prealloc`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`, and uses capability gates such as `_require_scratch_reflink`, `_require_xfs_io_command "falloc"`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Reflink coverage is sensitive to extent alignment, delayed allocation, unwritten extents, and page-size dependent block geometry, so comparisons against check files are the main correctness guard.
- Several checks can intentionally call `_notrun`; this is expected for unsupported geometry or feature combinations and should be distinguished from a failing assertion.

## Test Signals

The pass signal is byte-for-byte `cmp` checks against companion files, explicit `_fail` assertions. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/222 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/223 -->
# sources/test-tools/xfstests/tests/generic/223

## Purpose

File alignment tests. It is registered with `_begin_fstest auto quick prealloc` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `223` plus `_begin_fstest auto quick prealloc`. Imported libraries: `. ./common/preamble`, `. ./common/filter`. Capability gates: `_require_scratch`, `_require_xfs_io_command "falloc"`. Local functions: none. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 19: `BLOCKSIZE=4096`
- Line 70: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 25 `echo "=== mkfs with su $SUNIT_BLOCKS blocks x 4 ==="`, line 38 `echo "=== Testing size ${SIZE_MULT}*${SUNIT_K}k on ${SUNIT_K}k stripe ==="`, line 53 `echo "=== Testing size 1g falloc on ${SUNIT_K}k stripe ==="`, line 61 `echo "=== Testing size 1073745920 falloc on ${SUNIT_K}k stripe ==="`. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 16: `_require_scratch`
- Line 17: `_require_xfs_io_command "falloc"`
- Line 26: `_scratch_mkfs_geom $SUNIT_BYTES 4 $BLOCKSIZE >> $seqres.full 2>&1`
- Line 27: `_scratch_mount`
- Line 40: `$XFS_IO_PROG -f -c "falloc 0 $SIZE" \`
- Line 41: `$SCRATCH_MNT/file-$FILE-$SIZE-falloc \`
- Line 43: `$XFS_IO_PROG -f -c "pwrite -b $SIZE 0 $SIZE" \`
- Line 46: `$here/src/t_stripealign $SCRATCH_MNT/file-$FILE-$SIZE-falloc \`
- Line 47: `$SUNIT_BLOCKS | _filter_scratch`
- Line 49: `$SUNIT_BLOCKS | _filter_scratch`
- Line 53: `echo "=== Testing size 1g falloc on ${SUNIT_K}k stripe ==="`
- Line 54: `$XFS_IO_PROG -f -c "falloc 0 1g" \`
- Line 55: `$SCRATCH_MNT/file-1g-falloc >> $seqres.full 2>&1`
- Line 67: `_scratch_unmount`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `prealloc`, imports `. ./common/preamble`, `. ./common/filter`, and uses capability gates such as `_require_scratch`, `_require_xfs_io_command "falloc"`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- The main risk is environment drift: missing helper binaries, unsupported filesystem operations, or output formatting changes can make the test skip or fail without indicating a filesystem regression.

## Test Signals

The pass signal is silence from the helper program and final `status=0`. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/223 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/224 -->
# sources/test-tools/xfstests/tests/generic/224

## Purpose

Delayed allocation at ENOSPC test Derived from a test case from Lachlan McIlroy and improved to reliably trigger a BUG in xfs_get_blocks(). Despite this XFS focus, the test can to run on any filesystem to exercise ENOSPC behaviour make a 1GB filesystem set the reserved block pool to almost empty for XFS. It is registered with `_begin_fstest auto` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `224` plus `_begin_fstest auto`. Imported libraries: `. ./common/preamble`, `. ./common/filter`. Capability gates: `_require_scratch`. Local functions: `_cleanup`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 39: `FILES=1000`
- Line 65: `status=$?`

## Control Flow

The visible phases are driven by echo markers such as line 58 `echo "*** Silence is golden ***"`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 20: `rm -f $tmp.*`
- Line 21: `rm -f $SCRATCH_MNT/testfile.*`
- Line 28: `_require_scratch`
- Line 31: `_scratch_mkfs_sized `expr 1024 \* 1024 \* 1024` > $seqres.full 2>&1`
- Line 32: `_scratch_mount >> $seqres.full 2>&1`
- Line 36: `$XFS_IO_PROG -x -c "resblks 4" $SCRATCH_MNT >> $seqres.full 2>&1`
- Line 48: `$XFS_IO_PROG -f -c "truncate 10485760" $SCRATCH_MNT/testfile.$i`
- Line 49: `dd if=/dev/zero of=$SCRATCH_MNT/testfile.$i bs=4k conv=notrunc`
- Line 55: `dd of=/dev/null if=$SCRATCH_MNT/testfile.$i bs=512k iflag=direct > /dev/null 2>&1 &`
- Line 62: `_scratch_unmount`
- Line 63: `_check_dmesg _filter_aiodio_dmesg`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Temporary files are rooted at `$tmp.*` and removed by the local or default cleanup path. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, imports `. ./common/preamble`, `. ./common/filter`, and uses capability gates such as `_require_scratch`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Direct I/O paths can be affected by device sector size, alignment, cache invalidation, and filesystem-specific serialization between buffered and direct writes.
- ENOSPC cases are deliberately capacity-sensitive and can expose allocator, reservation, or delayed-allocation leaks only when scratch sizing and reserved blocks match the scenario.

## Test Signals

The pass signal is post-test dmesg scanning. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/224 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/225 -->
# sources/test-tools/xfstests/tests/generic/225

## Purpose

Run the fiemap (file extent mapping) tester. It is registered with `_begin_fstest auto quick fiemap` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `225` plus `_begin_fstest auto quick fiemap`. Imported libraries: `. ./common/preamble`, `. ./common/filter`. Capability gates: `_require_scratch`, `_require_odirect`, `_require_xfs_io_command "fiemap"`, `_require_test_program "fiemap-tester"`. Local functions: none. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 22: `fiemapfile=$SCRATCH_MNT/$seq.fiemap`
- Line 23: `fiemaplog=$SCRATCH_MNT/$seq.log`
- Line 27: `seed=`date +%s``
- Line 38: `status=$?`
- Line 45: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 29 `echo "using seed $seed" >> $fiemaplog`, line 31 `echo "fiemap run without preallocation, with sync"`, line 42 `echo "fiemap run without preallocation or sync"`. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 10: `_begin_fstest auto quick fiemap`
- Line 15: `_require_scratch`
- Line 17: `_require_xfs_io_command "fiemap"`
- Line 19: `_scratch_mkfs > /dev/null 2>&1`
- Line 20: `_scratch_mount > /dev/null 2>&1`
- Line 22: `fiemapfile=$SCRATCH_MNT/$seq.fiemap`
- Line 23: `fiemaplog=$SCRATCH_MNT/$seq.log`
- Line 25: `_require_test_program "fiemap-tester"`
- Line 29: `echo "using seed $seed" >> $fiemaplog`
- Line 31: `echo "fiemap run without preallocation, with sync"`
- Line 32: `$here/src/fiemap-tester -q -S -s $seed -p 0 -r 200 $fiemapfile 2>&1 | tee -a $fiemaplog`
- Line 35: `if grep -q "Operation not supported" $fiemaplog; then`
- Line 42: `echo "fiemap run without preallocation or sync"`
- Line 43: `$here/src/fiemap-tester -q -s $seed -p 0 -r 200 $fiemapfile 2>&1 | tee -a $fiemaplog`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `fiemap`, imports `. ./common/preamble`, `. ./common/filter`, and uses capability gates such as `_require_scratch`, `_require_odirect`, `_require_xfs_io_command "fiemap"`, `_require_test_program "fiemap-tester"`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Direct I/O paths can be affected by device sector size, alignment, cache invalidation, and filesystem-specific serialization between buffered and direct writes.
- Extent-map output is formatted and filtered, but the test still depends on stable extent flags, logical block addressing, and filesystem support for the ioctl under test.
- Several checks can intentionally call `_notrun`; this is expected for unsupported geometry or feature combinations and should be distinguished from a failing assertion.

## Test Signals

The pass signal is filtered extent-map output. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/225 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/226 -->
# sources/test-tools/xfstests/tests/generic/226

## Purpose

Test for prealloc space leaks by rewriting the same file in a loop Buffer size argument supplied to xfs_io "pwrite" command. It is registered with `_begin_fstest auto enospc` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `226` plus `_begin_fstest auto enospc`. Imported libraries: `. ./common/preamble`. Capability gates: `_require_scratch`, `_require_odirect`. Local functions: none. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 23: `loops=16`
- Line 26: `buffer="-b $(expr 512 \* 1024)"`
- Line 50: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 19 `echo "--> mkfs 256m filesystem"`, line 28 `echo "--> $loops buffered 64m writes in a loop"`, line 30 `echo -n "$I "`, line 36 `echo`. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 14: `_require_scratch`
- Line 18: `_scratch_unmount 2>/dev/null`
- Line 20: `_scratch_mkfs_sized `expr 256 \* 1024 \* 1024` >> $seqres.full 2>&1`
- Line 21: `_scratch_mount`
- Line 31: `$XFS_IO_PROG -f \`
- Line 33: `rm -f $SCRATCH_MNT/test`
- Line 37: `_scratch_cycle_mount`
- Line 42: `$XFS_IO_PROG -f -d \`
- Line 44: `rm -f $SCRATCH_MNT/test`
- Line 48: `_scratch_unmount`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Cycle-mount calls force metadata and extent state through unmount/remount persistence before validation. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `enospc`, imports `. ./common/preamble`, and uses capability gates such as `_require_scratch`, `_require_odirect`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Direct I/O paths can be affected by device sector size, alignment, cache invalidation, and filesystem-specific serialization between buffered and direct writes.
- ENOSPC cases are deliberately capacity-sensitive and can expose allocator, reservation, or delayed-allocation leaks only when scratch sizing and reserved blocks match the scenario.

## Test Signals

The pass signal is silence from the helper program and final `status=0`. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/226 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/227 -->
# sources/test-tools/xfstests/tests/generic/227

## Purpose

See what happens if we DIO CoW blocks 2-4 of a page's worth of blocks when the second block is delalloc This test is dependent on the system page size, so we cannot use md5 in the golden output; we can only compare to a check file. It is registered with `_begin_fstest auto quick clone prealloc` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `227` plus `_begin_fstest auto quick clone prealloc`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`. Capability gates: `_require_scratch_reflink`, `_require_xfs_io_command "falloc"`, `_require_odirect`. Local functions: `_cleanup`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 31: `pagesz=$(getconf PAGE_SIZE)`
- Line 32: `blksz=$((pagesz / 4))`
- Line 38: `testdir=$SCRATCH_MNT/test-$seq`
- Line 41: `real_blksz=$(_get_file_block_size $testdir)`
- Line 74: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 34 `echo "Format and mount"`, line 44 `echo "Create the original files"`, line 54 `echo "Compare files"`, line 58 `echo "CoW and unmount"`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 20: `rm -rf $tmp.* $testdir`
- Line 27: `_require_scratch_reflink`
- Line 28: `_require_xfs_io_command "falloc"`
- Line 34: `echo "Format and mount"`
- Line 35: `_scratch_mkfs_blocksized $blksz > $seqres.full 2>&1`
- Line 36: `_scratch_mount >> $seqres.full 2>&1`
- Line 39: `mkdir $testdir`
- Line 45: `_pwrite_byte 0x61 0 $pagesz $testdir/file1 >> $seqres.full`
- Line 47: `$XFS_IO_PROG -f -c "truncate $pagesz" $testdir/file2 >> $seqres.full`
- Line 48: `$XFS_IO_PROG -f -c "truncate $pagesz" $testdir/file2.chk >> $seqres.full`
- Line 50: `_reflink_range $testdir/file1 $blksz $testdir/file2 $((blksz * 2)) $blksz >> $seqres.full`
- Line 51: `_pwrite_byte 0x61 $((blksz * 2)) $blksz $testdir/file2.chk >> $seqres.full`
- Line 52: `_scratch_cycle_mount`
- Line 71: `cmp -s $testdir/file2 $testdir/file2.chk || _fail "file2 and file2.chk don't match."`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Cycle-mount calls force metadata and extent state through unmount/remount persistence before validation. Temporary files are rooted at `$tmp.*` and removed by the local or default cleanup path. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `clone`, `prealloc`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`, and uses capability gates such as `_require_scratch_reflink`, `_require_xfs_io_command "falloc"`, `_require_odirect`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Reflink coverage is sensitive to extent alignment, delayed allocation, unwritten extents, and page-size dependent block geometry, so comparisons against check files are the main correctness guard.
- Direct I/O paths can be affected by device sector size, alignment, cache invalidation, and filesystem-specific serialization between buffered and direct writes.
- Several checks can intentionally call `_notrun`; this is expected for unsupported geometry or feature combinations and should be distinguished from a failing assertion.

## Test Signals

The pass signal is byte-for-byte `cmp` checks against companion files, explicit `_fail` assertions. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/227 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/228 -->
# sources/test-tools/xfstests/tests/generic/228

## Purpose

Check if fallocate respects RLIMIT_FSIZE generic, but xfs_io's fallocate must work only Linux supports fallocate Sanity check to see if fallocate works Check if we have good enough space available Set the FSIZE ulimit to 100MB and check xfs_io will receive SIGXFSZ signal, if not handled it will trigger a coredump And in bash 5.3.x, bash will always output the command/script triggering the. It is registered with `_begin_fstest rw auto prealloc quick` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `228` plus `_begin_fstest rw auto prealloc quick`. Imported libraries: `. ./common/preamble`. Capability gates: `_require_test`, `_require_xfs_io_command "falloc"`. Local functions: none. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 22: `avail=`df -P $TEST_DIR | awk 'END {print $4}'``
- Line 27: `flim=`ulimit -f``
- Line 48: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 31 `echo "File size limit is now set to 100 MB."`, line 32 `echo "Let us try to preallocate 101 MB. This should fail."`, line 42 `echo "Let us now try to preallocate 50 MB. This should succeed."`, line 46 `echo "Test over."`. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 14: `_require_test`
- Line 16: `[ -n "$XFS_IO_PROG" ] || _notrun "xfs_io executable not found"`
- Line 19: `_require_xfs_io_command "falloc"`
- Line 22: `avail=`df -P $TEST_DIR | awk 'END {print $4}'``
- Line 26: `ulimit -f 102400`
- Line 27: `flim=`ulimit -f``
- Line 28: `[ "$flim" != "unlimited" ] || _notrun "Unable to set FSIZE ulimit"`
- Line 29: `[ "$flim" -eq 102400 ] || _notrun "FSIZE ulimit is not correct (100 MB)"`
- Line 39: `bash -c "trap '' SIGXFSZ; $XFS_IO_PROG -f -c 'falloc 0 101m' $TEST_DIR/ouch"`
- Line 40: `rm -f $TEST_DIR/ouch`
- Line 43: `$XFS_IO_PROG -f -c 'falloc 0 50m' $TEST_DIR/ouch`
- Line 44: `rm -f $TEST_DIR/ouch`

## State and Persistence Behavior

Primary state lives under `$TEST_DIR`, making this a test-device workload rather than a scratch-device destructive test. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `rw`, `auto`, `prealloc`, `quick`, imports `. ./common/preamble`, and uses capability gates such as `_require_test`, `_require_xfs_io_command "falloc"`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- The main risk is environment drift: missing helper binaries, unsupported filesystem operations, or output formatting changes can make the test skip or fail without indicating a filesystem regression.
- Several checks can intentionally call `_notrun`; this is expected for unsupported geometry or feature combinations and should be distinguished from a failing assertion.

## Test Signals

The pass signal is silence from the helper program and final `status=0`. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/228 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/229 -->
# sources/test-tools/xfstests/tests/generic/229

## Purpose

See what happens if we CoW blocks 2-4 of a page's worth of blocks when the surrounding blocks vary between unwritten/regular/delalloc/hole This test is dependent on the system page size, so we cannot use md5 in the golden output; we can only compare to a check file. It is registered with `_begin_fstest auto quick clone prealloc` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `229` plus `_begin_fstest auto quick clone prealloc`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`. Capability gates: `_require_scratch_reflink`, `_require_xfs_io_command "falloc"`. Local functions: `_cleanup`, `runtest`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 30: `pagesz=$(getconf PAGE_SIZE)`
- Line 31: `blksz=$((pagesz / 4))`
- Line 37: `testdir=$SCRATCH_MNT/test-$seq`
- Line 40: `real_blksz=$(_get_file_block_size $testdir)`
- Line 45: `b2=$1`
- Line 46: `b4=$2`
- Line 47: `dir=$3`
- Line 131: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 33 `echo "Format and mount"`, line 44 `echo "runtest $1 $2"`, line 49 `echo "Create the original files"`, line 86 `echo "Compare files"`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 20: `rm -rf $tmp.* $testdir`
- Line 28: `_require_xfs_io_command "falloc"`
- Line 34: `_scratch_mkfs_blocksized $blksz > $seqres.full 2>&1`
- Line 38: `mkdir $testdir`
- Line 51: `_pwrite_byte 0x61 0 $pagesz $dir/file1 >> $seqres.full`
- Line 54: `$XFS_IO_PROG -f -c "truncate $pagesz" $dir/file2.chk >> $seqres.full`
- Line 59: `_pwrite_byte 0x61 $blksz $blksz $dir/file2.chk >> $seqres.full`
- Line 63: `_pwrite_byte 0x00 $blksz $blksz $dir/file2.chk >> $seqres.full`
- Line 72: `_pwrite_byte 0x61 $((blksz * 3)) $blksz $dir/file2.chk >> $seqres.full`
- Line 76: `_pwrite_byte 0x00 $((blksz * 3)) $blksz $dir/file2.chk >> $seqres.full`
- Line 83: `_pwrite_byte 0x61 $((blksz * 2)) $blksz $dir/file2.chk >> $seqres.full`
- Line 87: `! cmp -s $dir/file1 $dir/file2 || _fail "file1 and file2 don't match."`
- Line 90: `echo "CoW and unmount"`
- Line 107: `cmp -s $dir/file2 $dir/file2.chk || _fail "file2 and file2.chk don't match."`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Cycle-mount calls force metadata and extent state through unmount/remount persistence before validation. Temporary files are rooted at `$tmp.*` and removed by the local or default cleanup path. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `clone`, `prealloc`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`, and uses capability gates such as `_require_scratch_reflink`, `_require_xfs_io_command "falloc"`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Reflink coverage is sensitive to extent alignment, delayed allocation, unwritten extents, and page-size dependent block geometry, so comparisons against check files are the main correctness guard.
- Several checks can intentionally call `_notrun`; this is expected for unsupported geometry or feature combinations and should be distinguished from a failing assertion.

## Test Signals

The pass signal is byte-for-byte `cmp` checks against companion files, explicit `_fail` assertions. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/229 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/230 -->
# sources/test-tools/xfstests/tests/generic/230

## Purpose

Simple quota enforcement test. It is registered with `_begin_fstest auto quota quick` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `230` plus `_begin_fstest auto quota quick`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/quota`. Capability gates: `_require_scratch`, `_require_quota`, `_require_user`. Local functions: `test_files`, `test_enforcement`, `cleanup_files`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 96: `grace=2`
- Line 104: `BLOCK_SIZE=$(_get_file_block_size $SCRATCH_MNT)`
- Line 118: `type=u`
- Line 127: `type=g`
- Line 133: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 23 `echo; echo "### create files, setting up ownership (type=$type)"`, line 32 `echo "### some buffered IO (type=$type)"`, line 33 `echo "--- initiating IO..." >>$seqres.full`, line 35 `echo "Write 225 blocks..."`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 11: `_begin_fstest auto quota quick`
- Line 18: `_require_quota`
- Line 27: `chmod 777 $SCRATCH_MNT 2>/dev/null`
- Line 39: `repquota -$type $SCRATCH_MNT | grep -v "^root" >>$seqres.full 2>&1`
- Line 45: `repquota -$type $SCRATCH_MNT | grep -v "^root" >>$seqres.full 2>&1`
- Line 54: `_filter_xfs_io_error | tee -a $seqres.full`
- Line 61: `_filter_xfs_io_error | tee -a $seqres.full`
- Line 68: `_su $qa_user -c "touch $SCRATCH_MNT/file3 $SCRATCH_MNT/file4" \`
- Line 75: `setquota -$type $qa_user -T $grace $grace $SCRATCH_MNT 2>/dev/null`
- Line 79: `repquota -$type $SCRATCH_MNT | grep -v "^root" >>$seqres.full 2>&1`
- Line 85: `_filter_scratch | tee -a $seqres.full`
- Line 99: `_qmount_option 'defaults'`
- Line 103: `_force_vfs_quota_testing $SCRATCH_MNT`
- Line 131: `_scratch_unmount 2>/dev/null`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Quota state is persistent filesystem metadata manipulated through `quotacheck`, `quotaon`, `setquota`, and `repquota` across user and group modes. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quota`, `quick`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/quota`, and uses capability gates such as `_require_scratch`, `_require_quota`, `_require_user`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Quota tests depend on kernel quota mode, grace-period timing, and the qa user/group setup; stale quota files or unsupported VFS quota behavior can turn a real failure into a notrun or noisy output mismatch.

## Test Signals

The pass signal is quota usage/enforcement reports. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/230 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/231 -->
# sources/test-tools/xfstests/tests/generic/231

## Purpose

Run fsx with quotas enabled and verify accounted quotas in the end Derived from test 127. It is registered with `_begin_fstest auto quota` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `231` plus `_begin_fstest auto quota`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/quota`. Capability gates: `_require_scratch`, `_require_quota`, `_require_user`. Local functions: `_fsx`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 17: `FSX_FILE_SIZE=64000000`
- Line 18: `FSX_ARGS="-q -l $FSX_FILE_SIZE -o 65536 -N 20000"`
- Line 22: `tasks=$1`
- Line 25: `SEED=$RANDOM`
- Line 55: `status=1`
- Line 61: `status=1`
- Line 67: `status=1`
- Line 73: `status=1`

## Control Flow

The visible phases are driven by echo markers such as line 23 `echo "=== FSX Standard Mode, Memory Mapping, $tasks Tasks ==="`, line 28 `echo "ltp/fsx $FSX_ARGS -S $SEED $SCRATCH_MNT/fsx_file$i" >>$seqres.full`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 11: `_begin_fstest auto quota`
- Line 15: `. ./common/quota`
- Line 20: `_fsx()`
- Line 28: `echo "ltp/fsx $FSX_ARGS -S $SEED $SCRATCH_MNT/fsx_file$i" >>$seqres.full`
- Line 29: `_su $qa_user -c "ltp/fsx $FSX_ARGS -S $SEED \`
- Line 30: `$FSX_AVOID $SCRATCH_MNT/fsx_file$i" >$tmp.output$i 2>&1 &`
- Line 39: `$XFS_IO_PROG -c 'fsync' $SCRATCH_MNT/fsx_file$i`
- Line 45: `_require_scratch`
- Line 46: `_require_quota`
- Line 49: `_scratch_mkfs >> $seqres.full 2>&1`
- Line 50: `_qmount_option "usrquota,grpquota"`
- Line 51: `_qmount`
- Line 53: `if ! _fsx 1; then`
- Line 91: `_scratch_unmount 2>/dev/null`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Quota state is persistent filesystem metadata manipulated through `quotacheck`, `quotaon`, `setquota`, and `repquota` across user and group modes. Temporary files are rooted at `$tmp.*` and removed by the local or default cleanup path. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quota`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/quota`, and uses capability gates such as `_require_scratch`, `_require_quota`, `_require_user`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Quota tests depend on kernel quota mode, grace-period timing, and the qa user/group setup; stale quota files or unsupported VFS quota behavior can turn a real failure into a notrun or noisy output mismatch.
- Stress tests are randomized or high-iteration workloads, so seeds, scaling helpers, timeouts, and captured stderr are important for reproducibility.

## Test Signals

The pass signal is quota usage/enforcement reports, stress-tool exit status and captured logs. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/231 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/232 -->
# sources/test-tools/xfstests/tests/generic/232

## Purpose

Run fsstress with quotas enabled and verify accounted quotas in the end Derived from test 231. It is registered with `_begin_fstest auto quota stress` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `232` plus `_begin_fstest auto quota stress`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/quota`. Capability gates: `_require_scratch`, `_require_quota`. Local functions: `_filter_num`, `_fsstress`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 31: `out=$SCRATCH_MNT/fsstress.$$`
- Line 32: `count=2000`
- Line 33: `args=`_scale_fsstress_args -d $out -n $count -p 7``
- Line 39: `status=1`
- Line 53: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 27 `echo ""`, line 28 `echo "Testing fsstress"`, line 29 `echo ""`, line 35 `echo "fsstress $args" >> $seqres.full`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 11: `_begin_fstest auto quota stress`
- Line 15: `. ./common/quota`
- Line 17: `_filter_num()`
- Line 25: `_fsstress()`
- Line 28: `echo "Testing fsstress"`
- Line 31: `out=$SCRATCH_MNT/fsstress.$$`
- Line 33: `args=`_scale_fsstress_args -d $out -n $count -p 7``
- Line 35: `echo "fsstress $args" >> $seqres.full`
- Line 36: `if ! _run_fsstress $args`
- Line 38: `echo " fsstress $args returned $?"`
- Line 43: `_require_scratch`
- Line 44: `_require_quota`
- Line 46: `_scratch_mkfs > $seqres.full 2>&1`
- Line 52: `_scratch_unmount`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Quota state is persistent filesystem metadata manipulated through `quotacheck`, `quotaon`, `setquota`, and `repquota` across user and group modes. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quota`, `stress`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/quota`, and uses capability gates such as `_require_scratch`, `_require_quota`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Quota tests depend on kernel quota mode, grace-period timing, and the qa user/group setup; stale quota files or unsupported VFS quota behavior can turn a real failure into a notrun or noisy output mismatch.
- Direct I/O paths can be affected by device sector size, alignment, cache invalidation, and filesystem-specific serialization between buffered and direct writes.
- Stress tests are randomized or high-iteration workloads, so seeds, scaling helpers, timeouts, and captured stderr are important for reproducibility.

## Test Signals

The pass signal is quota usage/enforcement reports, stress-tool exit status and captured logs. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/232 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/233 -->
# sources/test-tools/xfstests/tests/generic/233

## Purpose

Run fsstress with quotas enabled and limits set low and verify accounted quotas in the end Derived from test 231. It is registered with `_begin_fstest auto quota stress` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `233` plus `_begin_fstest auto quota stress`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/quota`. Capability gates: `_require_scratch`, `_require_quota`, `_require_user`. Local functions: `_filter_num`, `_fsstress`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 32: `out=$SCRATCH_MNT/fsstress.$$`
- Line 33: `count=5000`
- Line 34: `args=`_scale_fsstress_args -z \`
- Line 53: `status=1`
- Line 69: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 28 `echo ""`, line 29 `echo "Testing fsstress"`, line 30 `echo ""`, line 48 `echo "fsstress $args" >> $seqres.full`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 12: `_begin_fstest auto quota stress`
- Line 16: `. ./common/quota`
- Line 18: `_filter_num()`
- Line 26: `_fsstress()`
- Line 29: `echo "Testing fsstress"`
- Line 32: `out=$SCRATCH_MNT/fsstress.$$`
- Line 34: `args=`_scale_fsstress_args -z \`
- Line 35: `-f rmdir=20 -f link=10 -f creat=10 -f mkdir=10 -f unlink=20 -f symlink=10 \`
- Line 36: `-f rename=10 -f fsync=2 -f write=15 -f dwrite=15 \`
- Line 44: `ulimit -l unlimited`
- Line 48: `echo "fsstress $args" >> $seqres.full`
- Line 49: `if ! _su $qa_user -c "ltp/fsstress $args" | tee -a $seqres.full | _filter_num`
- Line 51: `echo " fsstress $args returned $?"`
- Line 68: `_scratch_unmount`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Quota state is persistent filesystem metadata manipulated through `quotacheck`, `quotaon`, `setquota`, and `repquota` across user and group modes. Temporary files are rooted at `$tmp.*` and removed by the local or default cleanup path. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quota`, `stress`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/quota`, and uses capability gates such as `_require_scratch`, `_require_quota`, `_require_user`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Quota tests depend on kernel quota mode, grace-period timing, and the qa user/group setup; stale quota files or unsupported VFS quota behavior can turn a real failure into a notrun or noisy output mismatch.
- Direct I/O paths can be affected by device sector size, alignment, cache invalidation, and filesystem-specific serialization between buffered and direct writes.
- Stress tests are randomized or high-iteration workloads, so seeds, scaling helpers, timeouts, and captured stderr are important for reproducibility.
- Symlink persistence tests are metadata-focused and can fail through lost directory updates, wrong target payloads, or fast/slow symlink representation differences.

## Test Signals

The pass signal is quota usage/enforcement reports, stress-tool exit status and captured logs. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/233 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/234 -->
# sources/test-tools/xfstests/tests/generic/234

## Purpose

Stress setquota and setinfo handling. It is registered with `_begin_fstest auto quota` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `234` plus `_begin_fstest auto quota`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/quota`. Capability gates: `_require_scratch`, `_require_quota`. Local functions: `test_setting`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 20: `count=2000`
- Line 21: `procs=5`
- Line 22: `idmod=200000`
- Line 23: `seed=$RANDOM`
- Line 24: `RANDOM=$seed`
- Line 30: `OP=$(($RANDOM%22))`
- Line 31: `UG=$(($OP%2))`
- Line 32: `OP=$(($OP/2))`

## Control Flow

The visible phases are driven by echo markers such as line 19 `echo; echo "### test limits and info setting"`, line 25 `echo "Starting test with procs=$procs, idmod=$idmod, and seed=$seed" >>$seqres.full`, line 61 `echo "### done with testing"`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 11: `_begin_fstest auto quota`
- Line 15: `. ./common/quota`
- Line 39: `setquota -t -$type $j $j $SCRATCH_MNT`
- Line 49: `setquota -$type $ID $j $j $j $j $SCRATCH_MNT`
- Line 56: `setquota -$type $ID 0 0 0 0 $SCRATCH_MNT`
- Line 64: `_require_scratch`
- Line 65: `_require_quota`
- Line 68: `_scratch_mkfs >> $seqres.full 2>&1`
- Line 69: `_scratch_mount "-o usrquota,grpquota"`
- Line 70: `quotacheck -u -g $SCRATCH_MNT 2>/dev/null`
- Line 71: `quotaon -u -g $SCRATCH_MNT 2>/dev/null`
- Line 73: `_scratch_unmount`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Quota state is persistent filesystem metadata manipulated through `quotacheck`, `quotaon`, `setquota`, and `repquota` across user and group modes. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quota`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/quota`, and uses capability gates such as `_require_scratch`, `_require_quota`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Quota tests depend on kernel quota mode, grace-period timing, and the qa user/group setup; stale quota files or unsupported VFS quota behavior can turn a real failure into a notrun or noisy output mismatch.
- Stress tests are randomized or high-iteration workloads, so seeds, scaling helpers, timeouts, and captured stderr are important for reproducibility.

## Test Signals

The pass signal is silence from the helper program and final `status=0`. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/234 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/235 -->
# sources/test-tools/xfstests/tests/generic/235

## Purpose

Test whether quota gets properly reenabled after remount read-write. It is registered with `_begin_fstest auto quota quick` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `235` plus `_begin_fstest auto quota quick`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/quota`. Capability gates: `_require_scratch`, `_require_quota`, `_require_user`. Local functions: `do_repquota`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 53: `status=0`

## Control Flow

Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 11: `_begin_fstest auto quota quick`
- Line 15: `. ./common/quota`
- Line 17: `_require_scratch`
- Line 18: `_require_quota`
- Line 21: `do_repquota()`
- Line 23: `repquota -u -g $SCRATCH_MNT | grep -v -E '^root|^$' | _filter_scratch`
- Line 27: `_scratch_mkfs >> $seqres.full 2>&1`
- Line 28: `_scratch_mount "-o usrquota,grpquota"`
- Line 29: `quotacheck -u -g $SCRATCH_MNT 2>/dev/null`
- Line 30: `quotaon $SCRATCH_MNT 2>/dev/null`
- Line 32: `touch $SCRATCH_MNT/testfile`
- Line 33: `chown $qa_user:$qa_user $SCRATCH_MNT/testfile`
- Line 35: `do_repquota`
- Line 51: `_scratch_unmount 2>/dev/null`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Quota state is persistent filesystem metadata manipulated through `quotacheck`, `quotaon`, `setquota`, and `repquota` across user and group modes. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quota`, `quick`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/quota`, and uses capability gates such as `_require_scratch`, `_require_quota`, `_require_user`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Quota tests depend on kernel quota mode, grace-period timing, and the qa user/group setup; stale quota files or unsupported VFS quota behavior can turn a real failure into a notrun or noisy output mismatch.

## Test Signals

The pass signal is quota usage/enforcement reports. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/235 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/236 -->
# sources/test-tools/xfstests/tests/generic/236

## Purpose

Check ctime updated or not if file linked See also http://marc.info/?l=linux-btrfs&m=127434439020230&w=2 create a file and get its ctime create a link to a file and get existing file's ctime check ctime updated. It is registered with `_begin_fstest auto quick metadata` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `236` plus `_begin_fstest auto quick metadata`. Imported libraries: `. ./common/preamble`. Capability gates: `_require_hardlinks`, `_require_test`. Local functions: `_cleanup`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 28: `ctime=`stat -c %Z $TEST_DIR/ouch``
- Line 33: `ctime2=`stat -c %Z $TEST_DIR/ouch``
- Line 45: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 37 `echo "ctime: $ctime -> $ctime2 "`, line 38 `echo "Fatal error: ctime not updated after link"`, line 43 `echo "Test over."`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 16: `rm -f $TEST_DIR/ouch*`
- Line 22: `_require_test`
- Line 24: `rm -f $TEST_DIR/ouch*`
- Line 27: `touch $TEST_DIR/ouch`
- Line 28: `ctime=`stat -c %Z $TEST_DIR/ouch``
- Line 33: `ctime2=`stat -c %Z $TEST_DIR/ouch``

## State and Persistence Behavior

Primary state lives under `$TEST_DIR`, making this a test-device workload rather than a scratch-device destructive test. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `metadata`, imports `. ./common/preamble`, and uses capability gates such as `_require_hardlinks`, `_require_test`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- The main risk is environment drift: missing helper binaries, unsupported filesystem operations, or output formatting changes can make the test skip or fail without indicating a filesystem regression.

## Test Signals

The pass signal is stat/lstat metadata output. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/236 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/237 -->
# sources/test-tools/xfstests/tests/generic/237

## Purpose

Check user B can setfacl a file which belongs to user A See also http://marc.info/?l=linux-btrfs&m=127434445620298&w=2 only Linux supports fallocate get dir. It is registered with `_begin_fstest auto quick acl perms` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `237` plus `_begin_fstest auto quick acl perms`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`. Capability gates: `_require_test`, `_require_runas`, `_require_acls`. Local functions: `_cleanup`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 46: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 41 `echo "Expect to FAIL"`, line 44 `echo "Test over."`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 21: `rm -f $tmp.*`
- Line 22: `[ -n "$TEST_DIR" ] && rm -rf $TEST_DIR/$seq.dir1`
- Line 26: `_require_test`
- Line 34: `rm -rf $seq.dir1`
- Line 35: `mkdir $seq.dir1`
- Line 38: `touch file1`
- Line 39: `chown $acl1:$acl1 file1`

## State and Persistence Behavior

Primary state lives under `$TEST_DIR`, making this a test-device workload rather than a scratch-device destructive test. Temporary files are rooted at `$tmp.*` and removed by the local or default cleanup path. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `acl`, `perms`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`, and uses capability gates such as `_require_test`, `_require_runas`, `_require_acls`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- The main risk is environment drift: missing helper binaries, unsupported filesystem operations, or output formatting changes can make the test skip or fail without indicating a filesystem regression.

## Test Signals

The pass signal is silence from the helper program and final `status=0`. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/237 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/238 -->
# sources/test-tools/xfstests/tests/generic/238

## Purpose

See what happens if we DIO CoW blocks 2-4 of a page's worth of blocks when the surrounding blocks vary between unwritten/regular/delalloc/hole This test is dependent on the system page size, so we cannot use md5 in the golden output; we can only compare to a check file. It is registered with `_begin_fstest auto quick clone prealloc` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `238` plus `_begin_fstest auto quick clone prealloc`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`. Capability gates: `_require_scratch_reflink`, `_require_xfs_io_command "falloc"`, `_require_odirect`. Local functions: `_cleanup`, `runtest`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 31: `pagesz=$(getconf PAGE_SIZE)`
- Line 32: `blksz=$((pagesz / 4))`
- Line 38: `testdir=$SCRATCH_MNT/test-$seq`
- Line 41: `real_blksz=$(_get_file_block_size $testdir)`
- Line 46: `b2=$1`
- Line 47: `b4=$2`
- Line 48: `dir=$3`
- Line 132: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 34 `echo "Format and mount"`, line 45 `echo "runtest $1 $2"`, line 50 `echo "Create the original files"`, line 87 `echo "Compare files"`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 20: `rm -rf $tmp.* $testdir`
- Line 28: `_require_xfs_io_command "falloc"`
- Line 35: `_scratch_mkfs_blocksized $blksz > $seqres.full 2>&1`
- Line 39: `mkdir $testdir`
- Line 52: `_pwrite_byte 0x61 0 $pagesz $dir/file1 >> $seqres.full`
- Line 55: `$XFS_IO_PROG -f -c "truncate $pagesz" $dir/file2.chk >> $seqres.full`
- Line 60: `_pwrite_byte 0x61 $blksz $blksz $dir/file2.chk >> $seqres.full`
- Line 64: `_pwrite_byte 0x00 $blksz $blksz $dir/file2.chk >> $seqres.full`
- Line 73: `_pwrite_byte 0x61 $((blksz * 3)) $blksz $dir/file2.chk >> $seqres.full`
- Line 77: `_pwrite_byte 0x00 $((blksz * 3)) $blksz $dir/file2.chk >> $seqres.full`
- Line 84: `_pwrite_byte 0x61 $((blksz * 2)) $blksz $dir/file2.chk >> $seqres.full`
- Line 88: `! cmp -s $dir/file1 $dir/file2 || _fail "file1 and file2 don't match."`
- Line 91: `echo "CoW and unmount"`
- Line 108: `cmp -s $dir/file2 $dir/file2.chk || _fail "file2 and file2.chk don't match."`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Cycle-mount calls force metadata and extent state through unmount/remount persistence before validation. Temporary files are rooted at `$tmp.*` and removed by the local or default cleanup path. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `clone`, `prealloc`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`, and uses capability gates such as `_require_scratch_reflink`, `_require_xfs_io_command "falloc"`, `_require_odirect`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Reflink coverage is sensitive to extent alignment, delayed allocation, unwritten extents, and page-size dependent block geometry, so comparisons against check files are the main correctness guard.
- Direct I/O paths can be affected by device sector size, alignment, cache invalidation, and filesystem-specific serialization between buffered and direct writes.
- Several checks can intentionally call `_notrun`; this is expected for unsupported geometry or feature combinations and should be distinguished from a failing assertion.

## Test Signals

The pass signal is byte-for-byte `cmp` checks against companion files, explicit `_fail` assertions. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/238 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/239 -->
# sources/test-tools/xfstests/tests/generic/239

## Purpose

Read from a sparse file immedialy after filling a hole to test for races in unwritten extent conversion. It is registered with `_begin_fstest auto aio rw` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `239` plus `_begin_fstest auto aio rw`. Imported libraries: `. ./common/preamble`, `. ./common/filter`. Capability gates: `_require_test`, `_require_sparse_files`, `_require_aiodio aio-dio-hole-filling-race`. Local functions: `_cleanup`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 34: `status=$?`

## Control Flow

The visible phases are driven by echo markers such as line 28 `echo "Silence is golden"`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 17: `rm -f $TEST_DIR/tst-aio-dio-sparse-unwritten`
- Line 24: `_require_test`

## State and Persistence Behavior

Primary state lives under `$TEST_DIR`, making this a test-device workload rather than a scratch-device destructive test. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `aio`, `rw`, imports `. ./common/preamble`, `. ./common/filter`, and uses capability gates such as `_require_test`, `_require_sparse_files`, `_require_aiodio aio-dio-hole-filling-race`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- The main risk is environment drift: missing helper binaries, unsupported filesystem operations, or output formatting changes can make the test skip or fail without indicating a filesystem regression.

## Test Signals

The pass signal is silence from the helper program and final `status=0`. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/239 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/240 -->
# sources/test-tools/xfstests/tests/generic/240

## Purpose

Test that non-block-aligned aio+dio into holes does not leave zero'd out portions of the file QEMU IO to a file-backed device with misaligned partitions can send this sort of IO This test need only be run in the case where the logical block size of the device can be smaller than the file system block size. It is registered with `_begin_fstest auto aio quick rw` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `240` plus `_begin_fstest auto aio quick rw`. Imported libraries: `. ./common/preamble`, `. ./common/filter`. Capability gates: `_require_test`, `_require_sparse_files`, `_require_aiodio aiodio_sparse2`. Local functions: none. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 32: `logical_block_size=`$here/src/min_dio_alignment $TEST_DIR $TEST_DEV``
- Line 33: `fs_block_size=`_get_block_size $TEST_DIR``
- Line 34: `file_size=$((8 * $fs_block_size))`
- Line 44: `status=$?`

## Control Flow

The visible phases are driven by echo markers such as line 27 `echo "Silence is golden."`. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 23: `_require_test`
- Line 30: `rm -f $TEST_DIR/aiodio_sparse`

## State and Persistence Behavior

Primary state lives under `$TEST_DIR`, making this a test-device workload rather than a scratch-device destructive test. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `aio`, `quick`, `rw`, imports `. ./common/preamble`, `. ./common/filter`, and uses capability gates such as `_require_test`, `_require_sparse_files`, `_require_aiodio aiodio_sparse2`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- The main risk is environment drift: missing helper binaries, unsupported filesystem operations, or output formatting changes can make the test skip or fail without indicating a filesystem regression.
- Several checks can intentionally call `_notrun`; this is expected for unsupported geometry or feature combinations and should be distinguished from a failing assertion.

## Test Signals

The pass signal is silence from the helper program and final `status=0`. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/240 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/241 -->
# sources/test-tools/xfstests/tests/generic/241

## Purpose

Run parallel dbench & check for filesystem corruption This corrupted ext4 inode bitmaps due to races at one point. It is registered with `_begin_fstest auto` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `241` plus `_begin_fstest auto`. Imported libraries: `. ./common/preamble`, `. ./common/filter`. Capability gates: `_require_test`. Local functions: none. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 29: `status=$?`

## Control Flow

The visible phases are driven by echo markers such as line 21 `echo "Silence is golden."`. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 17: `_require_test`
- Line 24: `rm -rf $TEST_DIR/dbench`
- Line 25: `mkdir $TEST_DIR/dbench`

## State and Persistence Behavior

Primary state lives under `$TEST_DIR`, making this a test-device workload rather than a scratch-device destructive test. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, imports `. ./common/preamble`, `. ./common/filter`, and uses capability gates such as `_require_test`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Direct I/O paths can be affected by device sector size, alignment, cache invalidation, and filesystem-specific serialization between buffered and direct writes.
- Several checks can intentionally call `_notrun`; this is expected for unsupported geometry or feature combinations and should be distinguished from a failing assertion.

## Test Signals

The pass signal is silence from the helper program and final `status=0`. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/241 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/242 -->
# sources/test-tools/xfstests/tests/generic/242

## Purpose

Reflink two large files and CoW them in big chunks This test is dependent on the system page size, so we cannot use md5 in the golden output; we can only compare to a check file. It is registered with `_begin_fstest auto clone` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `242` plus `_begin_fstest auto clone`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`. Capability gates: `_require_scratch_reflink`, `_require_cp_reflink`. Local functions: `_cleanup`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 33: `testdir=$SCRATCH_MNT/test-$seq`
- Line 36: `blksz=65536`
- Line 37: `nr=6400`
- Line 38: `filesize=$((blksz * nr))`
- Line 39: `bufnr=1280`
- Line 40: `bufsize=$((blksz * bufnr))`
- Line 42: `free_blocks=$(stat -f -c '%a' $testdir)`
- Line 43: `real_blksz=$(_get_block_size $testdir)`

## Control Flow

The visible phases are driven by echo markers such as line 29 `echo "Format and mount"`, line 48 `echo "Create the original files"`, line 54 `echo "Compare files"`, line 59 `echo "CoW and unmount"`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 19: `rm -rf $tmp.* $testdir`
- Line 26: `_require_scratch_reflink`
- Line 27: `_require_cp_reflink`
- Line 29: `echo "Format and mount"`
- Line 30: `_scratch_mkfs > $seqres.full 2>&1`
- Line 31: `_scratch_mount >> $seqres.full 2>&1`
- Line 34: `mkdir $testdir`
- Line 42: `free_blocks=$(stat -f -c '%a' $testdir)`
- Line 49: `$XFS_IO_PROG -f -c "pwrite -S 0x61 -b $bufsize 0 $filesize" $testdir/file1 >> $seqres.full`
- Line 50: `_cp_reflink $testdir/file1 $testdir/file2 >> $seqres.full`
- Line 51: `$XFS_IO_PROG -f -c "pwrite -S 0x61 -b $bufsize 0 $filesize" $testdir/file2.chk >> $seqres.full`
- Line 52: `_scratch_cycle_mount`
- Line 55: `md5sum $testdir/file1 | _filter_scratch`
- Line 67: `md5sum $testdir/file2.chk | _filter_scratch`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Cycle-mount calls force metadata and extent state through unmount/remount persistence before validation. Temporary files are rooted at `$tmp.*` and removed by the local or default cleanup path. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `clone`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`, and uses capability gates such as `_require_scratch_reflink`, `_require_cp_reflink`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Reflink coverage is sensitive to extent alignment, delayed allocation, unwritten extents, and page-size dependent block geometry, so comparisons against check files are the main correctness guard.
- Several checks can intentionally call `_notrun`; this is expected for unsupported geometry or feature combinations and should be distinguished from a failing assertion.

## Test Signals

The pass signal is filtered `md5sum` output. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/242 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/243 -->
# sources/test-tools/xfstests/tests/generic/243

## Purpose

Reflink two large files and DIO CoW them in big chunks This test is dependent on the system page size, so we cannot use md5 in the golden output; we can only compare to a check file. It is registered with `_begin_fstest auto clone` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `243` plus `_begin_fstest auto clone`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`. Capability gates: `_require_scratch_reflink`, `_require_cp_reflink`, `_require_odirect`. Local functions: `_cleanup`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 34: `testdir=$SCRATCH_MNT/test-$seq`
- Line 37: `blksz=65536`
- Line 38: `nr=6400`
- Line 39: `filesize=$((blksz * nr))`
- Line 40: `bufnr=1280`
- Line 41: `bufsize=$((blksz * bufnr))`
- Line 43: `free_blocks=$(stat -f -c '%a' $testdir)`
- Line 44: `real_blksz=$(_get_block_size $testdir)`

## Control Flow

The visible phases are driven by echo markers such as line 30 `echo "Format and mount"`, line 49 `echo "Create the original files"`, line 55 `echo "Compare files"`, line 60 `echo "CoW and unmount"`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 19: `rm -rf $tmp.* $testdir`
- Line 26: `_require_scratch_reflink`
- Line 27: `_require_cp_reflink`
- Line 30: `echo "Format and mount"`
- Line 31: `_scratch_mkfs > $seqres.full 2>&1`
- Line 32: `_scratch_mount >> $seqres.full 2>&1`
- Line 35: `mkdir $testdir`
- Line 43: `free_blocks=$(stat -f -c '%a' $testdir)`
- Line 50: `$XFS_IO_PROG -f -c "pwrite -S 0x61 -b $bufsize 0 $filesize" $testdir/file1 >> $seqres.full`
- Line 51: `_cp_reflink $testdir/file1 $testdir/file2 >> $seqres.full`
- Line 52: `$XFS_IO_PROG -f -c "pwrite -S 0x61 -b $bufsize 0 $filesize" $testdir/file2.chk >> $seqres.full`
- Line 53: `_scratch_cycle_mount`
- Line 56: `md5sum $testdir/file1 | _filter_scratch`
- Line 68: `md5sum $testdir/file2.chk | _filter_scratch`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Cycle-mount calls force metadata and extent state through unmount/remount persistence before validation. Temporary files are rooted at `$tmp.*` and removed by the local or default cleanup path. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `clone`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`, and uses capability gates such as `_require_scratch_reflink`, `_require_cp_reflink`, `_require_odirect`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Reflink coverage is sensitive to extent alignment, delayed allocation, unwritten extents, and page-size dependent block geometry, so comparisons against check files are the main correctness guard.
- Direct I/O paths can be affected by device sector size, alignment, cache invalidation, and filesystem-specific serialization between buffered and direct writes.
- Several checks can intentionally call `_notrun`; this is expected for unsupported geometry or feature combinations and should be distinguished from a failing assertion.

## Test Signals

The pass signal is filtered `md5sum` output. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/243 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/244 -->
# sources/test-tools/xfstests/tests/generic/244

## Purpose

test out "sparse" quota ids retrieved by Q_GETNEXTQUOTA Designed to use the new Q_GETNEXTQUOTA quotactl. It is registered with `_begin_fstest auto quick quota` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `244` plus `_begin_fstest auto quick quota`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/quota`. Capability gates: `_require_quota`, `_require_scratch`, `_require_getnextquota`. Local functions: `_cleanup`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 32: `TYPES="u g"`
- Line 33: `MOUNT_OPTIONS="-o usrquota,grpquota"`
- Line 45: `ITERATIONS=100`
- Line 49: `ID=`od -N 4 -t uI -An /dev/urandom | tr -d " "``
- Line 77: `NEXT=1`
- Line 80: `Q=`$here/src/test-nextquota -i $NEXT -${TYPE} -d $SCRATCH_DEV` \`
- Line 86: `NEXT=`echo "$Q" | grep ^id | awk '{print $NF}' | head -n 1``
- Line 93: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 37 `echo "Launch all quotas"`, line 50 `echo $ID >> $tmp.1`, line 79 `echo "Trying ID $NEXT expecting $ID" >> $seqres.full`, line 82 `echo $Q >> $seqres.full`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 12: `_begin_fstest auto quick quota`
- Line 19: `rm -f $tmp.*`
- Line 24: `. ./common/quota`
- Line 27: `_require_quota`
- Line 28: `_require_scratch`
- Line 30: `_scratch_mkfs >> $seqres.full 2>&1`
- Line 33: `MOUNT_OPTIONS="-o usrquota,grpquota"`
- Line 34: `_qmount`
- Line 35: `_require_getnextquota`
- Line 37: `echo "Launch all quotas"`
- Line 60: `setquota -${TYPE} $ID $ID $ID $ID $ID $SCRATCH_MNT`
- Line 61: `touch ${SCRATCH_MNT}/${ID}`
- Line 62: `chown ${ID} ${SCRATCH_MNT}/${ID}`
- Line 81: `|| _fail "test-nextquota failed: $Q"`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Quota state is persistent filesystem metadata manipulated through `quotacheck`, `quotaon`, `setquota`, and `repquota` across user and group modes. Temporary files are rooted at `$tmp.*` and removed by the local or default cleanup path. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `quota`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/quota`, and uses capability gates such as `_require_quota`, `_require_scratch`, `_require_getnextquota`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Quota tests depend on kernel quota mode, grace-period timing, and the qa user/group setup; stale quota files or unsupported VFS quota behavior can turn a real failure into a notrun or noisy output mismatch.
- Direct I/O paths can be affected by device sector size, alignment, cache invalidation, and filesystem-specific serialization between buffered and direct writes.

## Test Signals

The pass signal is explicit `_fail` assertions. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/244 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/245 -->
# sources/test-tools/xfstests/tests/generic/245

## Purpose

Check that directory renames onto non-empty targets fail Based on a bug report and testcase from Vlado Plaga <rechner@vlado-do.de> According to the rename(2) manpage you can get either EEXIST or ENOTEMPTY as an error for trying to rename a non-empty directory, so just catch the error for ENOTMEMPTY and replace it with the EEXIST output so that either result passes Also, mv v9.4+ modified error message when a nonempty destination directory fails to be overwriteen. It is registered with `_begin_fstest auto quick dir` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `245` plus `_begin_fstest auto quick dir`. Imported libraries: `. ./common/preamble`, `. ./common/filter`. Capability gates: `_require_test`. Local functions: `_cleanup`, `_filter_directory_not_empty`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 19: `dir=$TEST_DIR/test-mv`
- Line 49: `status=0`

## Control Flow

Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 17: `_require_test`
- Line 24: `rm -rf $dir`
- Line 32: `_filter_directory_not_empty()`
- Line 39: `mkdir $dir`
- Line 41: `mkdir $dir/aa`
- Line 42: `mkdir $dir/ab`
- Line 43: `touch $dir/aa/1`
- Line 44: `mkdir $dir/ab/aa`
- Line 45: `touch $dir/ab/aa/2`
- Line 47: `mv $dir/ab/aa/ $dir 2>&1 | _filter_test_dir | _filter_directory_not_empty`

## State and Persistence Behavior

Primary state lives under `$TEST_DIR`, making this a test-device workload rather than a scratch-device destructive test. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `dir`, imports `. ./common/preamble`, `. ./common/filter`, and uses capability gates such as `_require_test`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Direct I/O paths can be affected by device sector size, alignment, cache invalidation, and filesystem-specific serialization between buffered and direct writes.

## Test Signals

The pass signal is silence from the helper program and final `status=0`. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/245 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/246 -->
# sources/test-tools/xfstests/tests/generic/246

## Purpose

Check that truncation after failed writes does not zero too much data Based on a bug report and testcase from Marius Tolzmann <tolzmann@molgen.mpg.de>. It is registered with `_begin_fstest auto quick rw mmap` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `246` plus `_begin_fstest auto quick rw mmap`. Imported libraries: `. ./common/preamble`, `. ./common/filter`. Capability gates: `_require_test`. Local functions: `_cleanup`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 20: `file=$TEST_DIR/mmap-writev`
- Line 33: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 29 `echo -n "cccccccccc" > $file`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 13: `_begin_fstest auto quick rw mmap`
- Line 18: `_require_test`
- Line 20: `file=$TEST_DIR/mmap-writev`
- Line 25: `rm -rf $file`
- Line 26: `rm -rf $file.NEW`
- Line 30: `$here/src/t_mmap_writev $file $file.NEW`

## State and Persistence Behavior

Primary state lives under `$TEST_DIR`, making this a test-device workload rather than a scratch-device destructive test. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `rw`, `mmap`, imports `. ./common/preamble`, `. ./common/filter`, and uses capability gates such as `_require_test`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- mmap tests rely on page-cache writeback, timestamp granularity, and correct handling of dirty mappings across fsync, sync, or remount boundaries.

## Test Signals

The pass signal is silence from the helper program and final `status=0`. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/246 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/247 -->
# sources/test-tools/xfstests/tests/generic/247

## Purpose

Test for race between direct I/O and mmap Modify as appropriate this test leaves a 512MB file around if we abort the test during the run via a reboot or kernel panic. Hence just name the file $seq so that we can always clean up on the next run and not leave large stale files around on the testdir that can lead to ENOSPC issues over time. It is registered with `_begin_fstest auto quick rw mmap` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `247` plus `_begin_fstest auto quick rw mmap`. Imported libraries: `. ./common/preamble`, `. ./common/filter`. Capability gates: `_require_test`. Local functions: `_cleanup`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 33: `testfile=$TEST_DIR/$seq`
- Line 36: `loops=500`
- Line 37: `iosize=1048576`
- Line 49: `start=`expr $loops - 1``
- Line 52: `offset=`expr $i \* $iosize``
- Line 66: `status=$?`

## Control Flow

The visible phases are driven by echo markers such as line 59 `echo "Silence is golden."`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 10: `_begin_fstest auto quick rw mmap`
- Line 18: `rm -f $tmp.* $testfile`
- Line 27: `_require_test`
- Line 34: `rm -f $testfile`
- Line 40: `dd if=/dev/zero of=$testfile bs=$iosize count=$loops &> /dev/null`
- Line 42: `_test_sync`
- Line 45: `dd if=/dev/zero of=$testfile oflag=direct bs=$iosize count=$loops conv=notrunc &> /dev/null &`
- Line 53: `$XFS_IO_PROG -f -c "mmap -w $offset $iosize" -c "mwrite $offset $iosize" $testfile`
- Line 63: `_test_unmount`
- Line 64: `_check_dmesg _filter_aiodio_dmesg`

## State and Persistence Behavior

Primary state lives under `$TEST_DIR`, making this a test-device workload rather than a scratch-device destructive test. Temporary files are rooted at `$tmp.*` and removed by the local or default cleanup path. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `rw`, `mmap`, imports `. ./common/preamble`, `. ./common/filter`, and uses capability gates such as `_require_test`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Direct I/O paths can be affected by device sector size, alignment, cache invalidation, and filesystem-specific serialization between buffered and direct writes.
- mmap tests rely on page-cache writeback, timestamp granularity, and correct handling of dirty mappings across fsync, sync, or remount boundaries.
- ENOSPC cases are deliberately capacity-sensitive and can expose allocator, reservation, or delayed-allocation leaks only when scratch sizing and reserved blocks match the scenario.

## Test Signals

The pass signal is post-test dmesg scanning. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/247 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/248 -->
# sources/test-tools/xfstests/tests/generic/248

## Purpose

Test for pwrite hang problem when writing from mmaped buffer of the same page Modify as appropriate success, all done. It is registered with `_begin_fstest auto quick rw mmap` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `248` plus `_begin_fstest auto quick rw mmap`. Imported libraries: `. ./common/preamble`, `. ./common/filter`. Capability gates: `_require_test`. Local functions: `_cleanup`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 26: `TESTFILE=$TEST_DIR/test_file`
- Line 27: `TEST_PROG=$here/src/pwrite_mmap_blocked`
- Line 32: `status=0`

## Control Flow

Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 10: `_begin_fstest auto quick rw mmap`
- Line 16: `rm -f $tmp.* $TESTFILE`
- Line 24: `_require_test`
- Line 27: `TEST_PROG=$here/src/pwrite_mmap_blocked`

## State and Persistence Behavior

Primary state lives under `$TEST_DIR`, making this a test-device workload rather than a scratch-device destructive test. Temporary files are rooted at `$tmp.*` and removed by the local or default cleanup path. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `rw`, `mmap`, imports `. ./common/preamble`, `. ./common/filter`, and uses capability gates such as `_require_test`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- mmap tests rely on page-cache writeback, timestamp granularity, and correct handling of dirty mappings across fsync, sync, or remount boundaries.

## Test Signals

The pass signal is silence from the helper program and final `status=0`. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/248 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/249 -->
# sources/test-tools/xfstests/tests/generic/249

## Purpose

simple splice(2) test. It is registered with `_begin_fstest auto quick rw` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `249` plus `_begin_fstest auto quick rw`. Imported libraries: `. ./common/preamble`, `. ./common/filter`. Capability gates: `_require_test`. Local functions: `_cleanup`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 27: `SRC=$TEST_DIR/$seq.src`
- Line 28: `DST=$TEST_DIR/$seq.dst`
- Line 36: `status=$?`

## Control Flow

The visible phases are driven by echo markers such as line 25 `echo "Feel the serenity."`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 16: `rm -f $tmp.*`
- Line 17: `rm -f $SRC $DST`
- Line 23: `_require_test`
- Line 30: `$XFS_IO_PROG -f -c "pwrite -S 0xa5a55a5a 0 32768k" -c fsync $SRC >> $seqres.full 2>&1`
- Line 32: `$XFS_IO_PROG -f -c "sendfile -i $SRC 0 32768k" -c fsync $DST >> $seqres.full 2>&1`

## State and Persistence Behavior

Primary state lives under `$TEST_DIR`, making this a test-device workload rather than a scratch-device destructive test. Temporary files are rooted at `$tmp.*` and removed by the local or default cleanup path. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `rw`, imports `. ./common/preamble`, `. ./common/filter`, and uses capability gates such as `_require_test`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- The main risk is environment drift: missing helper binaries, unsupported filesystem operations, or output formatting changes can make the test skip or fail without indicating a filesystem regression.

## Test Signals

The pass signal is explicit `_fail` assertions. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/249 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/250 -->
# sources/test-tools/xfstests/tests/generic/250

## Purpose

Create an unwritten extent, set up dm-error, try a DIO write, then make sure we can't read back old disk contents Disable the scratch rt device to avoid test failures relating to the rt bitmap consuming all the free space in our small data device. It is registered with `_begin_fstest auto quick prealloc rw eio` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `250` plus `_begin_fstest auto quick prealloc rw eio`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/dmerror`. Capability gates: `_require_scratch`, `_require_dm_target error`, `_require_xfs_io_command "falloc"`, `_require_odirect`, `_require_fs_space $SCRATCH_MNT $((filesize / 1024 * 5 / 4))`. Local functions: `_cleanup`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 34: `fssize=$((196 * 1048576))`
- Line 43: `testdir=$SCRATCH_MNT/test-$seq`
- Line 46: `blksz=65536`
- Line 47: `nr=640`
- Line 48: `bufnr=128`
- Line 49: `filesize=$((blksz * nr))`
- Line 50: `bufsize=$((blksz * bufnr))`
- Line 81: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 35 `echo "Format and mount"`, line 54 `echo "Create the original files"`, line 59 `echo "Compare files"`, line 62 `echo "Write and unmount"`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 17: `rm -rf $tmp.* $testdir`
- Line 25: `_require_scratch`
- Line 27: `_require_xfs_io_command "falloc"`
- Line 36: `$XFS_IO_PROG -d -c "pwrite -S 0x69 -b 1048576 0 $fssize" $SCRATCH_DEV >> $seqres.full`
- Line 38: `_dmerror_init`
- Line 40: `_dmerror_unmount`
- Line 44: `mkdir $testdir`
- Line 56: `_dmerror_unmount`
- Line 60: `md5sum $testdir/file2 | _filter_scratch`
- Line 63: `$XFS_IO_PROG -f -c "pwrite -S 0x63 $bufsize 1" $testdir/file2 >> $seqres.full`
- Line 65: `_dmerror_load_error_table`
- Line 68: `_dmerror_load_working_table`
- Line 70: `_dmerror_mount`
- Line 78: `_repair_scratch_fs >> $seqres.full`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Temporary files are rooted at `$tmp.*` and removed by the local or default cleanup path. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `prealloc`, `rw`, `eio`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/dmerror`, and uses capability gates such as `_require_scratch`, `_require_dm_target error`, `_require_xfs_io_command "falloc"`, `_require_odirect`, `_require_fs_space $SCRATCH_MNT $((filesize / 1024 * 5 / 4))`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Direct I/O paths can be affected by device sector size, alignment, cache invalidation, and filesystem-specific serialization between buffered and direct writes.

## Test Signals

The pass signal is filtered `md5sum` output. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/250 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/251 -->
# sources/test-tools/xfstests/tests/generic/251

## Purpose

This test was created in order to verify filesystem FITRIM implementation By many concurrent copy and remove operations and checking that files does not change after copied into SCRATCH_MNT test if FITRIM implementation corrupts the filesystem (data/metadata). It is registered with `_begin_fstest ioctl trim auto` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `251` plus `_begin_fstest ioctl trim auto`. Imported libraries: `. ./common/preamble`, `. ./common/filter`. Capability gates: `_require_scratch`, `_require_batched_discard $SCRATCH_MNT`. Local functions: `_cleanup`, `_destroy`, `_destroy_fstrim`, `_fail`, `set_minlen_constraints`, `set_length_constraints`, `fstrim_loop`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 15: `tmp=`mktemp -d``
- Line 18: `mypid=$$`
- Line 106: `fsize=$(_discard_max_offset_kb "$SCRATCH_MNT" "$SCRATCH_DEV")`
- Line 110: `step=$((RANDOM*$RANDOM+4))`
- Line 114: `minlen=$(( (RANDOM * (RANDOM % 2 + 1)) % FSTRIM_MAX_MINLEN ))`
- Line 118: `start=$RANDOM`
- Line 121: `fpid=$!`
- Line 127: `fpid=$!`

## Control Flow

The visible phases are driven by echo markers such as line 50 `echo "$1"`, line 178 `echo "MINLEN max=$FSTRIM_MAX_MINLEN min=$FSTRIM_MIN_MINLEN" >> $seqres.full`, line 179 `echo "LENGTH max=$FSTRIM_MAX_LEN min=$FSTRIM_MIN_LEN" >> $seqres.full`, line 193 `echo -n "Running the test: "`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 23: `_require_scratch`
- Line 24: `_scratch_mkfs >/dev/null 2>&1`
- Line 25: `_scratch_mount`
- Line 31: `rm -rf $tmp`
- Line 36: `kill $pids $fstrim_pid 2> /dev/null`
- Line 38: `rm -rf $tmp`
- Line 43: `test -n "$fpid" && kill $fpid 2> /dev/null`
- Line 45: `rm -f $tmp.fstrim_loop`
- Line 51: `kill $mypid 2> /dev/null`
- Line 133: `rm -f $tmp.fstrim_loop`
- Line 139: `find -P . -xdev -type f -print0 | xargs -0 md5sum | sort -o $tmp/stress.$$.$p`
- Line 146: `rm -f $tmp/stress.$$.$p`
- Line 162: `rm -rf $SCRATCH_MNT/$p`
- Line 205: `test -e "$tmp.fstrim_loop" && truncate -s 0 $tmp.fstrim_loop`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Temporary files are rooted at `$tmp.*` and removed by the local or default cleanup path. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `ioctl`, `trim`, `auto`, imports `. ./common/preamble`, `. ./common/filter`, and uses capability gates such as `_require_scratch`, `_require_batched_discard $SCRATCH_MNT`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Direct I/O paths can be affected by device sector size, alignment, cache invalidation, and filesystem-specific serialization between buffered and direct writes.
- Thin-provisioning tests depend on device-mapper target behavior, pool exhaustion semantics, and correct cleanup of temporary block devices.
- Stress tests are randomized or high-iteration workloads, so seeds, scaling helpers, timeouts, and captured stderr are important for reproducibility.
- Several checks can intentionally call `_notrun`; this is expected for unsupported geometry or feature combinations and should be distinguished from a failing assertion.

## Test Signals

The pass signal is filtered `md5sum` output, stress-tool exit status and captured logs, explicit `_fail` assertions. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/251 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/252 -->
# sources/test-tools/xfstests/tests/generic/252

## Purpose

Create an unwritten extent, set up dm-error, try an AIO DIO write, then make sure we can't read back old disk contents Disable the scratch rt device to avoid test failures relating to the rt bitmap consuming all the free space in our small data device. It is registered with `_begin_fstest auto quick prealloc rw eio` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `252` plus `_begin_fstest auto quick prealloc rw eio`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/dmerror`. Capability gates: `_require_scratch`, `_require_dm_target error`, `_require_xfs_io_command "falloc"`, `_require_aiodio "aiocp"`, `_require_fs_space $SCRATCH_MNT $((filesize / 1024 * 5 / 4))`. Local functions: `_cleanup`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 29: `AIO_TEST="$here/src/aio-dio-regress/aiocp"`
- Line 35: `fssize=$((196 * 1048576))`
- Line 44: `testdir=$SCRATCH_MNT/test-$seq`
- Line 47: `blksz=65536`
- Line 48: `nr=640`
- Line 49: `bufnr=128`
- Line 50: `filesize=$((blksz * nr))`
- Line 51: `bufsize=$((blksz * bufnr))`

## Control Flow

The visible phases are driven by echo markers such as line 36 `echo "Format and mount"`, line 56 `echo "Create the original files"`, line 61 `echo "Compare files"`, line 64 `echo "CoW and unmount"`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 17: `rm -rf $tmp.* $testdir $TEST_DIR/moo`
- Line 25: `_require_scratch`
- Line 27: `_require_xfs_io_command "falloc"`
- Line 37: `$XFS_IO_PROG -d -c "pwrite -S 0x69 -b 1048576 0 $fssize" $SCRATCH_DEV >> $seqres.full`
- Line 39: `_dmerror_init`
- Line 41: `_dmerror_unmount`
- Line 45: `mkdir $testdir`
- Line 58: `_dmerror_unmount`
- Line 62: `md5sum $testdir/file2 | _filter_scratch`
- Line 65: `$XFS_IO_PROG -f -c "pwrite -S 0x63 $bufsize 1" $testdir/file2 >> $seqres.full`
- Line 67: `_scratch_sync`
- Line 70: `_filter_flakey_EIO "write missed bytes expect 8388608 got 0"`
- Line 72: `_dmerror_unmount`
- Line 81: `_repair_scratch_fs >> $seqres.full`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. It may also use `$TEST_DIR` for non-destructive helper programs or limit checks. Temporary files are rooted at `$tmp.*` and removed by the local or default cleanup path. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `prealloc`, `rw`, `eio`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/dmerror`, and uses capability gates such as `_require_scratch`, `_require_dm_target error`, `_require_xfs_io_command "falloc"`, `_require_aiodio "aiocp"`, `_require_fs_space $SCRATCH_MNT $((filesize / 1024 * 5 / 4))`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Direct I/O paths can be affected by device sector size, alignment, cache invalidation, and filesystem-specific serialization between buffered and direct writes.
- Crash-recovery tests require dm-flakey behavior and metadata journaling; failures can appear as lost directory entries, stale content, or mount-time recovery errors.

## Test Signals

The pass signal is filtered `md5sum` output. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/252 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/253 -->
# sources/test-tools/xfstests/tests/generic/253

## Purpose

Truncate a file at midway through a CoW region This test is dependent on the system page size, so we cannot use md5 in the golden output; we can only compare to a check file. It is registered with `_begin_fstest auto quick clone` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `253` plus `_begin_fstest auto quick clone`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`. Capability gates: `_require_scratch_reflink`, `_require_cp_reflink`, `_require_xfs_io_command "truncate"`. Local functions: none. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 27: `testdir=$SCRATCH_MNT/test-$seq`
- Line 30: `blksz=65536`
- Line 31: `nr=4`
- Line 32: `filesize=$((blksz * nr))`
- Line 57: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 23 `echo "Format and mount"`, line 34 `echo "Create the original files"`, line 40 `echo "Compare files"`, line 45 `echo "CoW and unmount"`. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 19: `_require_scratch_reflink`
- Line 20: `_require_cp_reflink`
- Line 21: `_require_xfs_io_command "truncate"`
- Line 23: `echo "Format and mount"`
- Line 24: `_scratch_mkfs > $seqres.full 2>&1`
- Line 25: `_scratch_mount >> $seqres.full 2>&1`
- Line 28: `mkdir $testdir`
- Line 35: `_pwrite_byte 0x61 0 $filesize $testdir/file1 >> $seqres.full`
- Line 36: `_cp_reflink $testdir/file1 $testdir/file2 >> $seqres.full`
- Line 37: `_pwrite_byte 0x61 0 $filesize $testdir/file2.chk >> $seqres.full`
- Line 38: `_scratch_cycle_mount`
- Line 41: `md5sum $testdir/file1 | _filter_scratch`
- Line 42: `md5sum $testdir/file2 | _filter_scratch`
- Line 54: `md5sum $testdir/file2.chk | _filter_scratch`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Cycle-mount calls force metadata and extent state through unmount/remount persistence before validation. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `clone`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`, and uses capability gates such as `_require_scratch_reflink`, `_require_cp_reflink`, `_require_xfs_io_command "truncate"`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Reflink coverage is sensitive to extent alignment, delayed allocation, unwritten extents, and page-size dependent block geometry, so comparisons against check files are the main correctness guard.

## Test Signals

The pass signal is filtered `md5sum` output. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/253 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/254 -->
# sources/test-tools/xfstests/tests/generic/254

## Purpose

Punch a file at midway through a CoW region This test is dependent on the system page size, so we cannot use md5 in the golden output; we can only compare to a check file. It is registered with `_begin_fstest auto quick clone punch` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `254` plus `_begin_fstest auto quick clone punch`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`. Capability gates: `_require_scratch_reflink`, `_require_cp_reflink`, `_require_xfs_io_command "fpunch"`. Local functions: none. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 27: `testdir=$SCRATCH_MNT/test-$seq`
- Line 30: `blksz=65536`
- Line 31: `nr=5`
- Line 32: `filesize=$((blksz * nr))`
- Line 57: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 23 `echo "Format and mount"`, line 34 `echo "Create the original files"`, line 40 `echo "Compare files"`, line 45 `echo "CoW and unmount"`. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 19: `_require_scratch_reflink`
- Line 20: `_require_cp_reflink`
- Line 21: `_require_xfs_io_command "fpunch"`
- Line 23: `echo "Format and mount"`
- Line 24: `_scratch_mkfs > $seqres.full 2>&1`
- Line 25: `_scratch_mount >> $seqres.full 2>&1`
- Line 28: `mkdir $testdir`
- Line 35: `_pwrite_byte 0x61 0 $filesize $testdir/file1 >> $seqres.full`
- Line 36: `_cp_reflink $testdir/file1 $testdir/file2 >> $seqres.full`
- Line 37: `_pwrite_byte 0x61 0 $filesize $testdir/file2.chk >> $seqres.full`
- Line 38: `_scratch_cycle_mount`
- Line 41: `md5sum $testdir/file1 | _filter_scratch`
- Line 42: `md5sum $testdir/file2 | _filter_scratch`
- Line 54: `md5sum $testdir/file2.chk | _filter_scratch`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Cycle-mount calls force metadata and extent state through unmount/remount persistence before validation. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `clone`, `punch`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`, and uses capability gates such as `_require_scratch_reflink`, `_require_cp_reflink`, `_require_xfs_io_command "fpunch"`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Reflink coverage is sensitive to extent alignment, delayed allocation, unwritten extents, and page-size dependent block geometry, so comparisons against check files are the main correctness guard.

## Test Signals

The pass signal is filtered `md5sum` output. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/254 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/255 -->
# sources/test-tools/xfstests/tests/generic/255

## Purpose

Test Generic fallocate hole punching Standard punch hole tests Delayed allocation punch hole tests Multi hole punch tests Delayed allocation multi punch hole tests. It is registered with `_begin_fstest auto quick prealloc punch fiemap` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `255` plus `_begin_fstest auto quick prealloc punch fiemap`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/punch`. Capability gates: `_require_test`, `_require_xfs_io_command "fpunch"`, `_require_xfs_io_command "falloc"`, `_require_xfs_io_command "fiemap"`. Local functions: none. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 21: `testfile=$TEST_DIR/255.$$`
- Line 35: `status=0 ; exit`

## Control Flow

The script runs linearly after the harness and requirement checks. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 10: `_begin_fstest auto quick prealloc punch fiemap`
- Line 16: `_require_test`
- Line 17: `_require_xfs_io_command "fpunch"`
- Line 18: `_require_xfs_io_command "falloc"`
- Line 19: `_require_xfs_io_command "fiemap"`
- Line 24: `_test_generic_punch falloc fpunch fpunch fiemap _filter_hole_fiemap $testfile`
- Line 27: `_test_generic_punch -d falloc fpunch fpunch fiemap _filter_hole_fiemap $testfile`
- Line 30: `_test_generic_punch -k falloc fpunch fpunch fiemap _filter_hole_fiemap $testfile`
- Line 33: `_test_generic_punch -d -k falloc fpunch fpunch fiemap _filter_hole_fiemap $testfile`

## State and Persistence Behavior

Primary state lives under `$TEST_DIR`, making this a test-device workload rather than a scratch-device destructive test. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `prealloc`, `punch`, `fiemap`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/punch`, and uses capability gates such as `_require_test`, `_require_xfs_io_command "fpunch"`, `_require_xfs_io_command "falloc"`, `_require_xfs_io_command "fiemap"`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Direct I/O paths can be affected by device sector size, alignment, cache invalidation, and filesystem-specific serialization between buffered and direct writes.
- Extent-map output is formatted and filtered, but the test still depends on stable extent flags, logical block addressing, and filesystem support for the ioctl under test.

## Test Signals

The pass signal is filtered extent-map output. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/255 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/256 -->
# sources/test-tools/xfstests/tests/generic/256

## Purpose

Test Full File System Hole Punching _test_full_fs_punch() This function will test that a hole may be punched even when the file system is full. Reserved blocks should be used to allow a punch hole to proceed even when there is not enough blocks to further fragment the file. To test this, this function will fragment the file system by punching holes in regular intervals and filling the file system between punches. It is registered with `_begin_fstest auto quick punch` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `256` plus `_begin_fstest auto quick punch`. Imported libraries: `. ./common/preamble`, `. ./common/populate`, `. ./common/filter`, `. ./common/punch`. Capability gates: `_require_xfs_io_command "fpunch"`, `_require_scratch`, `_require_user`, `_require_test`. Local functions: `_test_full_fs_punch`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 23: `testfile=$TEST_DIR/256.$$`
- Line 60: `start_time="$(date +%s)"`
- Line 61: `stop_time=$(( start_time + (30 * TIME_FACTOR) ))`
- Line 75: `rc=$?`
- Line 81: `hole_offset=$(( $hole_offset + $hole_len + $hole_interval ))`
- Line 95: `block_size=`_get_block_size $SCRATCH_MNT``
- Line 98: `status=0 ; exit`

## Control Flow

The visible phases are driven by echo markers such as line 50 `echo "USAGE: _test_full_fs_punch hole_len hole_interval iterations file_name block_size"`, line 77 `echo Punch hole failed`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 18: `_require_xfs_io_command "fpunch"`
- Line 19: `_require_scratch`
- Line 21: `_require_test`
- Line 35: `_test_full_fs_punch()`
- Line 50: `echo "USAGE: _test_full_fs_punch hole_len hole_interval iterations file_name block_size"`
- Line 54: `rm -f $file_name &> /dev/null`
- Line 56: `$XFS_IO_PROG -f -c "pwrite 0 $file_len" \`
- Line 57: `-c "fsync" $file_name &> /dev/null`
- Line 58: `chmod 666 $file_name`
- Line 74: `_user_do "$XFS_IO_PROG -f -c \"fpunch $hole_offset $hole_len\" $file_name"`
- Line 89: `_scratch_unmount &> /dev/null`
- Line 90: `_scratch_mkfs_sized $(( 1536 * 1024 * 1024 )) &> /dev/null`
- Line 91: `_scratch_mount`
- Line 96: `_test_full_fs_punch $(( $block_size * 2 )) $block_size 500 $SCRATCH_MNT/252.$$ $block_size`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. It may also use `$TEST_DIR` for non-destructive helper programs or limit checks. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `punch`, imports `. ./common/preamble`, `. ./common/populate`, `. ./common/filter`, `. ./common/punch`, and uses capability gates such as `_require_xfs_io_command "fpunch"`, `_require_scratch`, `_require_user`, `_require_test`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- The main risk is environment drift: missing helper binaries, unsupported filesystem operations, or output formatting changes can make the test skip or fail without indicating a filesystem regression.

## Test Signals

The pass signal is silence from the helper program and final `status=0`. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/256 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/257 -->
# sources/test-tools/xfstests/tests/generic/257

## Purpose

Check that no duplicate d_off values are returned and that those values are seekable. Most work is done by the C program here success, all done. It is registered with `_begin_fstest dir auto quick` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `257` plus `_begin_fstest dir auto quick`. Imported libraries: `. ./common/preamble`, `. ./common/filter`. Capability gates: `_require_test`. Local functions: `_cleanup`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 31: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 30 `echo "*** done"`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 15: `rm -rf $TEST_DIR/ttt`
- Line 21: `_require_test`
- Line 23: `mkdir $TEST_DIR/ttt`
- Line 25: `touch $TEST_DIR/ttt/$n;`

## State and Persistence Behavior

Primary state lives under `$TEST_DIR`, making this a test-device workload rather than a scratch-device destructive test. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `dir`, `auto`, `quick`, imports `. ./common/preamble`, `. ./common/filter`, and uses capability gates such as `_require_test`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- The main risk is environment drift: missing helper binaries, unsupported filesystem operations, or output formatting changes can make the test skip or fail without indicating a filesystem regression.

## Test Signals

The pass signal is silence from the helper program and final `status=0`. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/257 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/258 -->
# sources/test-tools/xfstests/tests/generic/258

## Purpose

Test timestamps prior to epoch On 64-bit, ext2/3/4 was sign-extending when read from disk See also commit 4d7bf11d649c72621ca31b8ea12b9c94af380e63 Create a file with a timestamp prior to the epoch Should yield -315593940 (prior to epoch) unmount, remount, and check the timestamp. It is registered with `_begin_fstest auto quick bigtime` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `258` plus `_begin_fstest auto quick bigtime`. Imported libraries: `. ./common/preamble`. Capability gates: `_require_test`, `_require_negative_timestamps`. Local functions: none. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 19: `TESTFILE=$TEST_DIR/timestamp-test.txt`
- Line 26: `ts=`stat -c %X $TESTFILE``
- Line 38: `ts=`stat -c %X $TESTFILE``
- Line 44: `status=0 ; exit`

## Control Flow

The visible phases are driven by echo markers such as line 22 `echo "Creating file with timestamp of Jan 1, 1960"`, line 25 `echo "Testing for negative seconds since epoch"`, line 28 `echo "Timestamp wrapped: $ts"`, line 33 `echo "Remounting to flush cache"`. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 16: `_require_test`
- Line 23: `touch -t 196001010101 $TESTFILE`
- Line 26: `ts=`stat -c %X $TESTFILE``
- Line 33: `echo "Remounting to flush cache"`
- Line 34: `_test_cycle_mount`
- Line 38: `ts=`stat -c %X $TESTFILE``

## State and Persistence Behavior

Primary state lives under `$TEST_DIR`, making this a test-device workload rather than a scratch-device destructive test. Cycle-mount calls force metadata and extent state through unmount/remount persistence before validation. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `bigtime`, imports `. ./common/preamble`, and uses capability gates such as `_require_test`, `_require_negative_timestamps`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- The main risk is environment drift: missing helper binaries, unsupported filesystem operations, or output formatting changes can make the test skip or fail without indicating a filesystem regression.

## Test Signals

The pass signal is stat/lstat metadata output, explicit `_fail` assertions. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/258 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/259 -->
# sources/test-tools/xfstests/tests/generic/259

## Purpose

fzero a file at midway through a CoW region This test is dependent on the system page size, so we cannot use md5 in the golden output; we can only compare to a check file. It is registered with `_begin_fstest auto quick clone zero` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `259` plus `_begin_fstest auto quick clone zero`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`. Capability gates: `_require_scratch_reflink`, `_require_cp_reflink`, `_require_xfs_io_command "fzero"`. Local functions: none. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 27: `testdir=$SCRATCH_MNT/test-$seq`
- Line 30: `blksz=65536`
- Line 31: `nr=5`
- Line 32: `filesize=$((blksz * nr))`
- Line 57: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 23 `echo "Format and mount"`, line 34 `echo "Create the original files"`, line 40 `echo "Compare files"`, line 45 `echo "CoW and unmount"`. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 19: `_require_scratch_reflink`
- Line 20: `_require_cp_reflink`
- Line 21: `_require_xfs_io_command "fzero"`
- Line 23: `echo "Format and mount"`
- Line 24: `_scratch_mkfs > $seqres.full 2>&1`
- Line 25: `_scratch_mount >> $seqres.full 2>&1`
- Line 28: `mkdir $testdir`
- Line 35: `_pwrite_byte 0x61 0 $filesize $testdir/file1 >> $seqres.full`
- Line 36: `_cp_reflink $testdir/file1 $testdir/file2 >> $seqres.full`
- Line 37: `_pwrite_byte 0x61 0 $filesize $testdir/file2.chk >> $seqres.full`
- Line 38: `_scratch_cycle_mount`
- Line 41: `md5sum $testdir/file1 | _filter_scratch`
- Line 42: `md5sum $testdir/file2 | _filter_scratch`
- Line 54: `md5sum $testdir/file2.chk | _filter_scratch`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Cycle-mount calls force metadata and extent state through unmount/remount persistence before validation. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `clone`, `zero`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`, and uses capability gates such as `_require_scratch_reflink`, `_require_cp_reflink`, `_require_xfs_io_command "fzero"`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Reflink coverage is sensitive to extent alignment, delayed allocation, unwritten extents, and page-size dependent block geometry, so comparisons against check files are the main correctness guard.

## Test Signals

The pass signal is filtered `md5sum` output. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/259 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/260 -->
# sources/test-tools/xfstests/tests/generic/260

## Purpose

Purpose of this test is to check FITRIM argument handling to make sure that the argument processing is right and that it does not overflow All these tests should return EINVAL since the start is beyond the end of. It is registered with `_begin_fstest auto quick trim` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `260` plus `_begin_fstest auto quick trim`. Imported libraries: `. ./common/preamble`, `. ./common/filter`. Capability gates: `_require_math`, `_require_scratch`, `_require_batched_discard $SCRATCH_MNT`. Local functions: none. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 13: `status=0`
- Line 14: `chpid=0`
- Line 15: `mypid=$$`
- Line 28: `fssize=$(_discard_max_offset_kb "$SCRATCH_MNT" "$SCRATCH_DEV")`
- Line 30: `beyond_eofs=$(_math "$fssize*2048")`
- Line 31: `max_64bit=$(_math "2^64 - 1")`
- Line 39: `out=$($FSTRIM_PROG -o $beyond_eofs $SCRATCH_MNT 2>&1)`
- Line 44: `out=$($FSTRIM_PROG -o $beyond_eofs -l1M $SCRATCH_MNT 2>&1)`

## Control Flow

The visible phases are driven by echo markers such as line 38 `echo "[+] Start beyond the end of fs (should fail)"`, line 41 `echo $out | _filter_scratch`, line 43 `echo "[+] Start beyond the end of fs with len set (should fail)"`, line 46 `echo $out | _filter_scratch`. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 22: `_require_scratch`
- Line 23: `_scratch_mkfs >/dev/null 2>&1`
- Line 24: `_scratch_mount`
- Line 41: `echo $out | _filter_scratch`
- Line 46: `echo $out | _filter_scratch`
- Line 51: `echo $out | _filter_scratch`
- Line 56: `echo $out | _filter_scratch`
- Line 58: `_scratch_unmount`
- Line 59: `_scratch_mkfs >/dev/null 2>&1`
- Line 60: `_scratch_mount`
- Line 78: `_scratch_unmount`
- Line 79: `_scratch_mkfs >/dev/null 2>&1`
- Line 80: `_scratch_mount`
- Line 171: `bytes=$($FSTRIM_PROG -v -l$len $SCRATCH_MNT | _filter_fstrim)`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `trim`, imports `. ./common/preamble`, `. ./common/filter`, and uses capability gates such as `_require_math`, `_require_scratch`, `_require_batched_discard $SCRATCH_MNT`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Direct I/O paths can be affected by device sector size, alignment, cache invalidation, and filesystem-specific serialization between buffered and direct writes.

## Test Signals

The pass signal is silence from the helper program and final `status=0`. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/260 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/261 -->
# sources/test-tools/xfstests/tests/generic/261

## Purpose

fcollapse a file at midway through a CoW region This test is dependent on the system page size, so we cannot use md5 in the golden output; we can only compare to a check file. It is registered with `_begin_fstest auto quick clone collapse` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `261` plus `_begin_fstest auto quick clone collapse`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`. Capability gates: `_require_scratch_reflink`, `_require_cp_reflink`, `_require_xfs_io_command "fcollapse"`. Local functions: none. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 27: `testdir=$SCRATCH_MNT/test-$seq`
- Line 30: `blksz=65536`
- Line 31: `nr=5`
- Line 32: `filesize=$((blksz * nr))`
- Line 57: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 23 `echo "Format and mount"`, line 34 `echo "Create the original files"`, line 40 `echo "Compare files"`, line 45 `echo "CoW and unmount"`. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 19: `_require_scratch_reflink`
- Line 20: `_require_cp_reflink`
- Line 23: `echo "Format and mount"`
- Line 24: `_scratch_mkfs > $seqres.full 2>&1`
- Line 25: `_scratch_mount >> $seqres.full 2>&1`
- Line 28: `mkdir $testdir`
- Line 35: `_pwrite_byte 0x61 0 $filesize $testdir/file1 >> $seqres.full`
- Line 36: `_cp_reflink $testdir/file1 $testdir/file2 >> $seqres.full`
- Line 37: `_pwrite_byte 0x61 0 $filesize $testdir/file2.chk >> $seqres.full`
- Line 38: `_scratch_cycle_mount`
- Line 41: `md5sum $testdir/file1 | _filter_scratch`
- Line 42: `md5sum $testdir/file2 | _filter_scratch`
- Line 43: `md5sum $testdir/file2.chk | _filter_scratch`
- Line 54: `md5sum $testdir/file2.chk | _filter_scratch`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Cycle-mount calls force metadata and extent state through unmount/remount persistence before validation. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `clone`, `collapse`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`, and uses capability gates such as `_require_scratch_reflink`, `_require_cp_reflink`, `_require_xfs_io_command "fcollapse"`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Reflink coverage is sensitive to extent alignment, delayed allocation, unwritten extents, and page-size dependent block geometry, so comparisons against check files are the main correctness guard.

## Test Signals

The pass signal is filtered `md5sum` output. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/261 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/262 -->
# sources/test-tools/xfstests/tests/generic/262

## Purpose

finsert a file at midway through a CoW region This test is dependent on the system page size, so we cannot use md5 in the golden output; we can only compare to a check file. It is registered with `_begin_fstest auto quick clone insert` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `262` plus `_begin_fstest auto quick clone insert`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`. Capability gates: `_require_scratch_reflink`, `_require_cp_reflink`, `_require_xfs_io_command "finsert"`. Local functions: none. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 27: `testdir=$SCRATCH_MNT/test-$seq`
- Line 30: `blksz=65536`
- Line 31: `nr=4`
- Line 32: `filesize=$((blksz * nr))`
- Line 60: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 23 `echo "Format and mount"`, line 34 `echo "Create the original files"`, line 40 `echo "Compare files"`, line 45 `echo "CoW and unmount"`. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 19: `_require_scratch_reflink`
- Line 20: `_require_cp_reflink`
- Line 23: `echo "Format and mount"`
- Line 24: `_scratch_mkfs > $seqres.full 2>&1`
- Line 25: `_scratch_mount >> $seqres.full 2>&1`
- Line 28: `mkdir $testdir`
- Line 35: `_pwrite_byte 0x61 0 $filesize $testdir/file1 >> $seqres.full`
- Line 36: `_cp_reflink $testdir/file1 $testdir/file2 >> $seqres.full`
- Line 37: `_pwrite_byte 0x61 0 $filesize $testdir/file2.chk >> $seqres.full`
- Line 38: `_scratch_cycle_mount`
- Line 41: `md5sum $testdir/file1 | _filter_scratch`
- Line 42: `md5sum $testdir/file2 | _filter_scratch`
- Line 43: `md5sum $testdir/file2.chk | _filter_scratch`
- Line 57: `md5sum $testdir/file2.chk | _filter_scratch`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Cycle-mount calls force metadata and extent state through unmount/remount persistence before validation. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `clone`, `insert`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`, and uses capability gates such as `_require_scratch_reflink`, `_require_cp_reflink`, `_require_xfs_io_command "finsert"`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Reflink coverage is sensitive to extent alignment, delayed allocation, unwritten extents, and page-size dependent block geometry, so comparisons against check files are the main correctness guard.

## Test Signals

The pass signal is filtered `md5sum` output. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/262 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/263 -->
# sources/test-tools/xfstests/tests/generic/263

## Purpose

fsx exercising direct IO vs sub-block buffered I/O. It is registered with `_begin_fstest rw auto quick` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `263` plus `_begin_fstest rw auto quick`. Imported libraries: `. ./common/preamble`, `. ./common/filter`. Capability gates: `_require_test`, `_require_odirect`. Local functions: none. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 18: `psize=`$here/src/feature -s``
- Line 19: `bsize=`$here/src/min_dio_alignment $TEST_DIR $TEST_DEV``
- Line 24: `status=0`

## Control Flow

The script runs linearly after the harness and requirement checks. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 15: `_require_test`
- Line 21: `run_fsx -N 10000 -o 8192 -l 500000 -r PSIZE -t BSIZE -w BSIZE -Z`
- Line 22: `run_fsx -N 10000 -o 128000 -l 500000 -r PSIZE -t BSIZE -w BSIZE -Z`

## State and Persistence Behavior

Primary state lives under `$TEST_DIR`, making this a test-device workload rather than a scratch-device destructive test. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `rw`, `auto`, `quick`, imports `. ./common/preamble`, `. ./common/filter`, and uses capability gates such as `_require_test`, `_require_odirect`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Direct I/O paths can be affected by device sector size, alignment, cache invalidation, and filesystem-specific serialization between buffered and direct writes.
- Stress tests are randomized or high-iteration workloads, so seeds, scaling helpers, timeouts, and captured stderr are important for reproducibility.

## Test Signals

The pass signal is stress-tool exit status and captured logs. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/263 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/264 -->
# sources/test-tools/xfstests/tests/generic/264

## Purpose

fallocate a file at midway through a CoW region This test is dependent on the system page size, so we cannot use md5 in the golden output; we can only compare to a check file. It is registered with `_begin_fstest auto quick clone unshare` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `264` plus `_begin_fstest auto quick clone unshare`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`. Capability gates: `_require_scratch_reflink`, `_require_cp_reflink`, `_require_xfs_io_command "funshare"`. Local functions: none. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 27: `testdir=$SCRATCH_MNT/test-$seq`
- Line 30: `blksz=65536`
- Line 31: `nr=5`
- Line 32: `filesize=$((blksz * nr))`
- Line 57: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 23 `echo "Format and mount"`, line 34 `echo "Create the original files"`, line 40 `echo "Compare files"`, line 45 `echo "CoW and unmount"`. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 19: `_require_scratch_reflink`
- Line 20: `_require_cp_reflink`
- Line 23: `echo "Format and mount"`
- Line 24: `_scratch_mkfs > $seqres.full 2>&1`
- Line 25: `_scratch_mount >> $seqres.full 2>&1`
- Line 28: `mkdir $testdir`
- Line 35: `_pwrite_byte 0x61 0 $filesize $testdir/file1 >> $seqres.full`
- Line 36: `_cp_reflink $testdir/file1 $testdir/file2 >> $seqres.full`
- Line 37: `_pwrite_byte 0x61 0 $filesize $testdir/file2.chk >> $seqres.full`
- Line 38: `_scratch_cycle_mount`
- Line 41: `md5sum $testdir/file1 | _filter_scratch`
- Line 42: `md5sum $testdir/file2 | _filter_scratch`
- Line 43: `md5sum $testdir/file2.chk | _filter_scratch`
- Line 54: `md5sum $testdir/file2.chk | _filter_scratch`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Cycle-mount calls force metadata and extent state through unmount/remount persistence before validation. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `clone`, `unshare`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`, and uses capability gates such as `_require_scratch_reflink`, `_require_cp_reflink`, `_require_xfs_io_command "funshare"`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Reflink coverage is sensitive to extent alignment, delayed allocation, unwritten extents, and page-size dependent block geometry, so comparisons against check files are the main correctness guard.

## Test Signals

The pass signal is filtered `md5sum` output. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/264 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/265 -->
# sources/test-tools/xfstests/tests/generic/265

## Purpose

Test CoW behavior when the write temporarily fails. It is registered with `_begin_fstest auto quick clone eio` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `265` plus `_begin_fstest auto quick clone eio`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`, `. ./common/dmerror`. Capability gates: `_require_scratch_reflink`, `_require_cp_reflink`, `_require_dm_target error`, `_require_fs_space $SCRATCH_MNT $((filesize / 1024 * 3 * 5 / 4))`. Local functions: `_cleanup`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 34: `testdir=$SCRATCH_MNT/test-$seq`
- Line 37: `blksz=65536`
- Line 38: `nr=640`
- Line 39: `bufnr=128`
- Line 40: `filesize=$((blksz * nr))`
- Line 41: `bufsize=$((blksz * bufnr))`
- Line 58: `urk=$($XFS_IO_PROG -f -c "pwrite -S 0x63 -b $bufsize 0 $filesize" \`
- Line 76: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 29 `echo "Format and mount"`, line 45 `echo "Create the original files"`, line 51 `echo "Compare files"`, line 55 `echo "CoW and unmount"`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 16: `rm -rf $tmp.*`
- Line 25: `_require_scratch_reflink`
- Line 27: `_require_dm_target error`
- Line 30: `_scratch_mkfs > $seqres.full 2>&1`
- Line 32: `_dmerror_mount >> $seqres.full 2>&1`
- Line 46: `$XFS_IO_PROG -f -c "pwrite -S 0x61 -b $bufsize 0 $filesize" $testdir/file1 >> $seqres.full`
- Line 48: `_dmerror_unmount`
- Line 52: `md5sum $testdir/file1 | _filter_scratch`
- Line 55: `echo "CoW and unmount"`
- Line 57: `_dmerror_load_error_table`
- Line 59: `-c "fdatasync" $testdir/file2 2>&1)`
- Line 64: `_dmerror_unmount`
- Line 68: `md5sum $testdir/file1 | _filter_scratch`
- Line 73: `_repair_scratch_fs >> $seqres.full`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Temporary files are rooted at `$tmp.*` and removed by the local or default cleanup path. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `clone`, `eio`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`, `. ./common/dmerror`, and uses capability gates such as `_require_scratch_reflink`, `_require_cp_reflink`, `_require_dm_target error`, `_require_fs_space $SCRATCH_MNT $((filesize / 1024 * 3 * 5 / 4))`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Reflink coverage is sensitive to extent alignment, delayed allocation, unwritten extents, and page-size dependent block geometry, so comparisons against check files are the main correctness guard.

## Test Signals

The pass signal is filtered `md5sum` output, explicit `_fail` assertions. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/265 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/266 -->
# sources/test-tools/xfstests/tests/generic/266

## Purpose

Test CoW behavior when the write permanently fails. It is registered with `_begin_fstest auto quick clone eio` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `266` plus `_begin_fstest auto quick clone eio`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`, `. ./common/dmerror`. Capability gates: `_require_scratch_reflink`, `_require_cp_reflink`, `_require_dm_target error`, `_require_fs_space $SCRATCH_MNT $((filesize / 1024 * 3 * 5 / 4))`. Local functions: `_cleanup`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 34: `testdir=$SCRATCH_MNT/test-$seq`
- Line 37: `blksz=65536`
- Line 38: `nr=640`
- Line 39: `bufnr=128`
- Line 40: `filesize=$((blksz * nr))`
- Line 41: `bufsize=$((blksz * bufnr))`
- Line 58: `urk=$($XFS_IO_PROG -f -c "pwrite -S 0x63 -b $bufsize 0 $filesize" \`
- Line 73: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 29 `echo "Format and mount"`, line 45 `echo "Create the original files"`, line 51 `echo "Compare files"`, line 55 `echo "CoW and unmount"`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 16: `rm -rf $tmp.*`
- Line 17: `_dmerror_cleanup`
- Line 25: `_require_scratch_reflink`
- Line 26: `_require_cp_reflink`
- Line 27: `_require_dm_target error`
- Line 29: `echo "Format and mount"`
- Line 30: `_scratch_mkfs > $seqres.full 2>&1`
- Line 31: `_dmerror_init`
- Line 32: `_dmerror_mount >> $seqres.full 2>&1`
- Line 35: `mkdir $testdir`
- Line 46: `$XFS_IO_PROG -f -c "pwrite -S 0x61 -b $bufsize 0 $filesize" $testdir/file1 >> $seqres.full`
- Line 47: `_cp_reflink $testdir/file1 $testdir/file2 >> $seqres.full`
- Line 48: `_dmerror_unmount`
- Line 70: `md5sum $testdir/file1 | _filter_scratch`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Temporary files are rooted at `$tmp.*` and removed by the local or default cleanup path. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `clone`, `eio`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`, `. ./common/dmerror`, and uses capability gates such as `_require_scratch_reflink`, `_require_cp_reflink`, `_require_dm_target error`, `_require_fs_space $SCRATCH_MNT $((filesize / 1024 * 3 * 5 / 4))`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Reflink coverage is sensitive to extent alignment, delayed allocation, unwritten extents, and page-size dependent block geometry, so comparisons against check files are the main correctness guard.

## Test Signals

The pass signal is filtered `md5sum` output, explicit `_fail` assertions. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/266 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/267 -->
# sources/test-tools/xfstests/tests/generic/267

## Purpose

Test CoW behavior when the write temporarily fails and we unmount. It is registered with `_begin_fstest auto quick clone eio` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `267` plus `_begin_fstest auto quick clone eio`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`, `. ./common/dmerror`. Capability gates: `_require_scratch_reflink`, `_require_cp_reflink`, `_require_dm_target error`, `_require_fs_space $SCRATCH_MNT $((filesize / 1024 * 3 * 5 / 4))`. Local functions: `_cleanup`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 34: `testdir=$SCRATCH_MNT/test-$seq`
- Line 37: `blksz=65536`
- Line 38: `nr=640`
- Line 39: `bufnr=128`
- Line 40: `filesize=$((blksz * nr))`
- Line 41: `bufsize=$((blksz * bufnr))`
- Line 73: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 29 `echo "Format and mount"`, line 45 `echo "Create the original files"`, line 51 `echo "Compare files"`, line 55 `echo "CoW and unmount"`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 16: `rm -rf $tmp.*`
- Line 25: `_require_scratch_reflink`
- Line 27: `_require_dm_target error`
- Line 30: `_scratch_mkfs > $seqres.full 2>&1`
- Line 32: `_dmerror_mount >> $seqres.full 2>&1`
- Line 46: `$XFS_IO_PROG -f -c "pwrite -S 0x61 -b $bufsize 0 $filesize" $testdir/file1 >> $seqres.full`
- Line 48: `_dmerror_unmount`
- Line 52: `md5sum $testdir/file1 | _filter_scratch`
- Line 55: `echo "CoW and unmount"`
- Line 57: `_dmerror_load_error_table`
- Line 59: `_dmerror_load_working_table`
- Line 61: `_dmerror_unmount`
- Line 65: `md5sum $testdir/file1 | _filter_scratch`
- Line 70: `_repair_scratch_fs >> $seqres.full`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Temporary files are rooted at `$tmp.*` and removed by the local or default cleanup path. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `clone`, `eio`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`, `. ./common/dmerror`, and uses capability gates such as `_require_scratch_reflink`, `_require_cp_reflink`, `_require_dm_target error`, `_require_fs_space $SCRATCH_MNT $((filesize / 1024 * 3 * 5 / 4))`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Reflink coverage is sensitive to extent alignment, delayed allocation, unwritten extents, and page-size dependent block geometry, so comparisons against check files are the main correctness guard.

## Test Signals

The pass signal is filtered `md5sum` output. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/267 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/268 -->
# sources/test-tools/xfstests/tests/generic/268

## Purpose

Test CoW behavior when the write temporarily fails but the userspace program writes again. It is registered with `_begin_fstest auto quick clone eio` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `268` plus `_begin_fstest auto quick clone eio`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`, `. ./common/dmerror`. Capability gates: `_require_scratch_reflink`, `_require_cp_reflink`, `_require_dm_target error`, `_require_fs_space $SCRATCH_MNT $((filesize / 1024 * 3 * 5 / 4))`. Local functions: `_cleanup`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 35: `testdir=$SCRATCH_MNT/test-$seq`
- Line 38: `blksz=65536`
- Line 39: `nr=640`
- Line 40: `bufnr=128`
- Line 41: `filesize=$((blksz * nr))`
- Line 42: `bufsize=$((blksz * bufnr))`
- Line 59: `urk=$($XFS_IO_PROG -f -c "pwrite -S 0x63 -b $bufsize 0 $filesize" \`
- Line 79: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 30 `echo "Format and mount"`, line 46 `echo "Create the original files"`, line 52 `echo "Compare files"`, line 56 `echo "CoW and unmount"`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 17: `rm -rf $tmp.*`
- Line 26: `_require_scratch_reflink`
- Line 28: `_require_dm_target error`
- Line 31: `_scratch_mkfs > $seqres.full 2>&1`
- Line 33: `_dmerror_mount >> $seqres.full 2>&1`
- Line 47: `$XFS_IO_PROG -f -c "pwrite -S 0x61 -b $bufsize 0 $filesize" $testdir/file1 >> $seqres.full`
- Line 49: `_dmerror_unmount`
- Line 53: `md5sum $testdir/file1 | _filter_scratch`
- Line 56: `echo "CoW and unmount"`
- Line 58: `_dmerror_load_error_table`
- Line 60: `-c "fdatasync" $testdir/file2 2>&1)`
- Line 66: `$XFS_IO_PROG -f -c "pwrite -S 0x64 -b $bufsize 0 $filesize" -c "fdatasync" $testdir/file2 >> $seqres.full 2>&1`
- Line 68: `_dmerror_mount`
- Line 76: `_repair_scratch_fs >> $seqres.full`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Temporary files are rooted at `$tmp.*` and removed by the local or default cleanup path. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `clone`, `eio`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`, `. ./common/dmerror`, and uses capability gates such as `_require_scratch_reflink`, `_require_cp_reflink`, `_require_dm_target error`, `_require_fs_space $SCRATCH_MNT $((filesize / 1024 * 3 * 5 / 4))`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Reflink coverage is sensitive to extent alignment, delayed allocation, unwritten extents, and page-size dependent block geometry, so comparisons against check files are the main correctness guard.

## Test Signals

The pass signal is filtered `md5sum` output, explicit `_fail` assertions. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/268 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/269 -->
# sources/test-tools/xfstests/tests/generic/269

## Purpose

Run fsstress and ENOSPC hitters in parallel, check fs consistency at the end Disable all sync operations to get higher load. It is registered with `_begin_fstest auto rw prealloc ioctl enospc stress` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `269` plus `_begin_fstest auto rw prealloc ioctl enospc stress`. Imported libraries: `. ./common/preamble`, `. ./common/filter`. Capability gates: `_require_scratch`. Local functions: `_workout`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 15: `FSSTRESS_AVOID="$FSSTRESS_AVOID -ffsync=0 -fsync=0 -ffdatasync=0"`
- Line 21: `num_iterations=10`
- Line 22: `enospc_time=2`
- Line 23: `out=$SCRATCH_MNT/fsstress.$$`
- Line 24: `args=`_scale_fsstress_args -p128 -n999999999 -f setattr=1 -d $out``
- Line 51: `status=1`
- Line 54: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 18 `echo ""`, line 19 `echo "Run fsstress"`, line 20 `echo ""`, line 25 `echo "fsstress $args" >> $seqres.full`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 15: `FSSTRESS_AVOID="$FSSTRESS_AVOID -ffsync=0 -fsync=0 -ffdatasync=0"`
- Line 19: `echo "Run fsstress"`
- Line 23: `out=$SCRATCH_MNT/fsstress.$$`
- Line 24: `args=`_scale_fsstress_args -p128 -n999999999 -f setattr=1 -d $out``
- Line 25: `echo "fsstress $args" >> $seqres.full`
- Line 26: `_run_fsstress_bg $args`
- Line 27: `echo "Run dd writers in parallel"`
- Line 35: `echo "Killing fsstress process..." >> $seqres.full`
- Line 36: `_kill_fsstress`
- Line 39: `_require_scratch`
- Line 41: `_scratch_mkfs_sized $((512 * 1024 * 1024)) >> $seqres.full 2>&1`
- Line 42: `_scratch_mount`
- Line 45: `_scratch_unmount 2>/dev/null`
- Line 50: `echo "failed to umount"`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `rw`, `prealloc`, `ioctl`, `enospc`, `stress`, imports `. ./common/preamble`, `. ./common/filter`, and uses capability gates such as `_require_scratch`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Direct I/O paths can be affected by device sector size, alignment, cache invalidation, and filesystem-specific serialization between buffered and direct writes.
- ENOSPC cases are deliberately capacity-sensitive and can expose allocator, reservation, or delayed-allocation leaks only when scratch sizing and reserved blocks match the scenario.
- Stress tests are randomized or high-iteration workloads, so seeds, scaling helpers, timeouts, and captured stderr are important for reproducibility.

## Test Signals

The pass signal is stress-tool exit status and captured logs. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/269 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/270 -->
# sources/test-tools/xfstests/tests/generic/270

## Purpose

Run fsstress and ENOSPC hitters in parallel, check quota and fs consistency at the end Disable all sync operations to get higher load. It is registered with `_begin_fstest auto quota rw prealloc ioctl enospc stress` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `270` plus `_begin_fstest auto quota rw prealloc ioctl enospc stress`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/quota`, `. ./common/attr`. Capability gates: `_require_quota`, `_require_user`, `_require_scratch`, `_require_command "$SETCAP_PROG" setcap`, `_require_attrs security`. Local functions: `_workout`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 19: `FSSTRESS_AVOID="$FSSTRESS_AVOID -ffsync=0 -fsync=0 -ffdatasync=0"`
- Line 25: `num_iterations=10`
- Line 26: `enospc_time=2`
- Line 27: `out=$SCRATCH_MNT/fsstress.$$`
- Line 28: `args=`_scale_fsstress_args -p128 -n999999999 -f setattr=1 $FSSTRESS_AVOID -d $out``
- Line 41: `_FSSTRESS_PID=$!`
- Line 48: `of=$SCRATCH_MNT/SPACE_CONSUMER bs=1M " \`
- Line 75: `status=1`

## Control Flow

The visible phases are driven by echo markers such as line 22 `echo ""`, line 23 `echo "Run fsstress"`, line 24 `echo ""`, line 29 `echo "fsstress $args" >> $seqres.full`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 11: `_begin_fstest auto quota rw prealloc ioctl enospc stress`
- Line 15: `. ./common/quota`
- Line 19: `FSSTRESS_AVOID="$FSSTRESS_AVOID -ffsync=0 -fsync=0 -ffdatasync=0"`
- Line 23: `echo "Run fsstress"`
- Line 27: `out=$SCRATCH_MNT/fsstress.$$`
- Line 28: `args=`_scale_fsstress_args -p128 -n999999999 -f setattr=1 $FSSTRESS_AVOID -d $out``
- Line 29: `echo "fsstress $args" >> $seqres.full`
- Line 31: `cp $FSSTRESS_PROG $tmp.fsstress.bin`
- Line 32: `$SETCAP_PROG cap_chown=epi $tmp.fsstress.bin`
- Line 39: `ulimit -l unlimited`
- Line 40: `_su $qa_user -c "$tmp.fsstress.bin $args" > /dev/null 2>&1 &`
- Line 43: `echo "Run dd writers in parallel"`
- Line 47: `_su $qa_user -c "dd if=/dev/zero \`
- Line 81: `echo "failed to umount"`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Quota state is persistent filesystem metadata manipulated through `quotacheck`, `quotaon`, `setquota`, and `repquota` across user and group modes. Temporary files are rooted at `$tmp.*` and removed by the local or default cleanup path. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quota`, `rw`, `prealloc`, `ioctl`, `enospc`, `stress`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/quota`, `. ./common/attr`, and uses capability gates such as `_require_quota`, `_require_user`, `_require_scratch`, `_require_command "$SETCAP_PROG" setcap`, `_require_attrs security`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Quota tests depend on kernel quota mode, grace-period timing, and the qa user/group setup; stale quota files or unsupported VFS quota behavior can turn a real failure into a notrun or noisy output mismatch.
- Direct I/O paths can be affected by device sector size, alignment, cache invalidation, and filesystem-specific serialization between buffered and direct writes.
- ENOSPC cases are deliberately capacity-sensitive and can expose allocator, reservation, or delayed-allocation leaks only when scratch sizing and reserved blocks match the scenario.
- Stress tests are randomized or high-iteration workloads, so seeds, scaling helpers, timeouts, and captured stderr are important for reproducibility.

## Test Signals

The pass signal is quota usage/enforcement reports, stress-tool exit status and captured logs. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/270 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/271 -->
# sources/test-tools/xfstests/tests/generic/271

## Purpose

Test DIO CoW behavior when the write temporarily fails. It is registered with `_begin_fstest auto quick clone eio` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `271` plus `_begin_fstest auto quick clone eio`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`, `. ./common/dmerror`. Capability gates: `_require_scratch_reflink`, `_require_cp_reflink`, `_require_dm_target error`, `_require_odirect`, `_require_fs_space $SCRATCH_MNT $((filesize / 1024 * 3 * 5 / 4))`. Local functions: `_cleanup`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 35: `testdir=$SCRATCH_MNT/test-$seq`
- Line 38: `blksz=65536`
- Line 39: `nr=640`
- Line 40: `bufnr=128`
- Line 41: `filesize=$((blksz * nr))`
- Line 42: `bufsize=$((blksz * bufnr))`
- Line 59: `urk=$($XFS_IO_PROG -d -f -c "pwrite -S 0x63 -b $bufsize 0 $filesize" $testdir/file2 2>&1)`
- Line 75: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 30 `echo "Format and mount"`, line 46 `echo "Create the original files"`, line 52 `echo "Compare files"`, line 56 `echo "CoW and unmount"`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 16: `rm -rf $tmp.*`
- Line 17: `_dmerror_cleanup`
- Line 25: `_require_scratch_reflink`
- Line 26: `_require_cp_reflink`
- Line 27: `_require_dm_target error`
- Line 30: `echo "Format and mount"`
- Line 31: `_scratch_mkfs > $seqres.full 2>&1`
- Line 32: `_dmerror_init`
- Line 33: `_dmerror_mount >> $seqres.full 2>&1`
- Line 36: `mkdir $testdir`
- Line 47: `$XFS_IO_PROG -f -c "pwrite -S 0x61 -b $bufsize 0 $filesize" $testdir/file1 >> $seqres.full`
- Line 48: `_cp_reflink $testdir/file1 $testdir/file2 >> $seqres.full`
- Line 49: `_dmerror_unmount`
- Line 72: `_repair_scratch_fs >> $seqres.full`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Temporary files are rooted at `$tmp.*` and removed by the local or default cleanup path. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `clone`, `eio`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`, `. ./common/dmerror`, and uses capability gates such as `_require_scratch_reflink`, `_require_cp_reflink`, `_require_dm_target error`, `_require_odirect`, `_require_fs_space $SCRATCH_MNT $((filesize / 1024 * 3 * 5 / 4))`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Reflink coverage is sensitive to extent alignment, delayed allocation, unwritten extents, and page-size dependent block geometry, so comparisons against check files are the main correctness guard.
- Direct I/O paths can be affected by device sector size, alignment, cache invalidation, and filesystem-specific serialization between buffered and direct writes.

## Test Signals

The pass signal is filtered `md5sum` output, explicit `_fail` assertions. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/271 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/272 -->
# sources/test-tools/xfstests/tests/generic/272

## Purpose

Test DIO CoW behavior when the write permanently fails. It is registered with `_begin_fstest auto quick clone eio` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `272` plus `_begin_fstest auto quick clone eio`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`, `. ./common/dmerror`. Capability gates: `_require_scratch_reflink`, `_require_cp_reflink`, `_require_dm_target error`, `_require_odirect`, `_require_fs_space $SCRATCH_MNT $((filesize / 1024 * 3 * 5 / 4))`. Local functions: `_cleanup`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 35: `testdir=$SCRATCH_MNT/test-$seq`
- Line 38: `blksz=65536`
- Line 39: `nr=640`
- Line 40: `bufnr=128`
- Line 41: `filesize=$((blksz * nr))`
- Line 42: `bufsize=$((blksz * bufnr))`
- Line 59: `urk=$($XFS_IO_PROG -d -f -c "pwrite -S 0x63 -b $bufsize 0 $filesize" $testdir/file2 2>&1)`
- Line 73: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 30 `echo "Format and mount"`, line 46 `echo "Create the original files"`, line 52 `echo "Compare files"`, line 56 `echo "CoW and unmount"`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 16: `rm -rf $tmp.*`
- Line 17: `_dmerror_cleanup`
- Line 25: `_require_scratch_reflink`
- Line 26: `_require_cp_reflink`
- Line 27: `_require_dm_target error`
- Line 30: `echo "Format and mount"`
- Line 31: `_scratch_mkfs > $seqres.full 2>&1`
- Line 32: `_dmerror_init`
- Line 33: `_dmerror_mount >> $seqres.full 2>&1`
- Line 36: `mkdir $testdir`
- Line 47: `$XFS_IO_PROG -f -c "pwrite -S 0x61 -b $bufsize 0 $filesize" $testdir/file1 >> $seqres.full`
- Line 48: `_cp_reflink $testdir/file1 $testdir/file2 >> $seqres.full`
- Line 49: `_dmerror_unmount`
- Line 70: `md5sum $testdir/file1 | _filter_scratch`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Temporary files are rooted at `$tmp.*` and removed by the local or default cleanup path. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `clone`, `eio`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`, `. ./common/dmerror`, and uses capability gates such as `_require_scratch_reflink`, `_require_cp_reflink`, `_require_dm_target error`, `_require_odirect`, `_require_fs_space $SCRATCH_MNT $((filesize / 1024 * 3 * 5 / 4))`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Reflink coverage is sensitive to extent alignment, delayed allocation, unwritten extents, and page-size dependent block geometry, so comparisons against check files are the main correctness guard.
- Direct I/O paths can be affected by device sector size, alignment, cache invalidation, and filesystem-specific serialization between buffered and direct writes.

## Test Signals

The pass signal is filtered `md5sum` output, explicit `_fail` assertions. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/272 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/273 -->
# sources/test-tools/xfstests/tests/generic/273

## Purpose

reservation test with heavy cp workload creator. It is registered with `_begin_fstest auto rw` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `273` plus `_begin_fstest auto rw`. Imported libraries: `. ./common/preamble`, `. ./common/filter`. Capability gates: `_require_scratch`. Local functions: `_cleanup`, `_threads_set`, `_file_create`, `_porter`, `_do_workload`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 14: `status=0 # success is the default!`
- Line 26: `threads=50`
- Line 27: `count=2`
- Line 31: `_cpu_num=`$here/src/feature -o``
- Line 32: `threads=$(($_cpu_num * 50))`
- Line 35: `threads=200`
- Line 41: `block_size=$1`
- Line 42: `_i=0`

## Control Flow

The visible phases are driven by echo markers such as line 46 `echo "mkdir origin err"`, line 84 `echo "mkdir sub_xxx err"`, line 92 `echo "_porter $_suffix not complete"`, line 121 `echo "------------------------------"`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 20: `rm -rf $tmp.*`
- Line 21: `_scratch_unmount`
- Line 44: `if ! mkdir $SCRATCH_MNT/origin`
- Line 46: `echo "mkdir origin err"`
- Line 71: `dd if=/dev/zero of=file_$_i bs=$block_size count=$_count >/dev/null 2>&1`
- Line 82: `if ! mkdir $SCRATCH_MNT/sub_$_suffix`
- Line 84: `echo "mkdir sub_xxx err"`
- Line 95: `_scratch_sync`
- Line 119: `_require_scratch`
- Line 125: `_scratch_unmount 2>/dev/null`
- Line 126: `_scratch_mkfs_sized $((2 * 1024 * 1024 * 1024)) >>$seqres.full 2>&1`
- Line 127: `_scratch_mount`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Temporary files are rooted at `$tmp.*` and removed by the local or default cleanup path. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `rw`, imports `. ./common/preamble`, `. ./common/filter`, and uses capability gates such as `_require_scratch`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Direct I/O paths can be affected by device sector size, alignment, cache invalidation, and filesystem-specific serialization between buffered and direct writes.

## Test Signals

The pass signal is silence from the helper program and final `status=0`. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/273 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/274 -->
# sources/test-tools/xfstests/tests/generic/274

## Purpose

preallocation test: Preallocate space to a file, and fill the rest of the fs to 100% Then test a write into that preallocated space, which should succeed creator Compression can exhaust metadata space here for btrfs and cause spurious failurs because we hit a metadata ENOSPC, skip if we have compression enabled. It is registered with `_begin_fstest auto rw prealloc enospc` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `274` plus `_begin_fstest auto rw prealloc enospc`. Imported libraries: `. ./common/preamble`, `. ./common/filter`. Capability gates: `_require_scratch`, `_require_xfs_io_command "falloc" "-k"`, `_require_no_compress`. Local functions: `_cleanup`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 16: `status=0 # success is the default!`

## Control Flow

The visible phases are driven by echo markers such as line 35 `echo "------------------------------"`, line 36 `echo "preallocation test"`, line 37 `echo "------------------------------"`, line 49 `echo "Fill fs with 1M IOs; ENOSPC expected" >> $seqres.full`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 22: `rm -f $tmp.*`
- Line 23: `_scratch_unmount`
- Line 28: `_require_scratch`
- Line 29: `_require_xfs_io_command "falloc" "-k"`
- Line 39: `_scratch_unmount 2>/dev/null`
- Line 40: `_scratch_mkfs_sized $((2 * 1024 * 1024 * 1024)) >>$seqres.full 2>&1`
- Line 41: `_scratch_mount`
- Line 44: `$XFS_IO_PROG -f -c "pwrite 0 64k" -c "falloc -k 64k 64m" $SCRATCH_MNT/test \`
- Line 50: `dd if=/dev/zero of=$SCRATCH_MNT/tmp1 bs=1M >>$seqres.full 2>&1`
- Line 52: `dd if=/dev/zero of=$SCRATCH_MNT/tmp2 bs=4K >>$seqres.full 2>&1`
- Line 53: `_scratch_sync`
- Line 56: `dd if=/dev/zero of=$SCRATCH_MNT/tmp3 bs=4K oflag=sync >>$seqres.full 2>&1`
- Line 59: `df $SCRATCH_MNT >>$seqres.full 2>&1`
- Line 77: `_scratch_sync`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Temporary files are rooted at `$tmp.*` and removed by the local or default cleanup path. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `rw`, `prealloc`, `enospc`, imports `. ./common/preamble`, `. ./common/filter`, and uses capability gates such as `_require_scratch`, `_require_xfs_io_command "falloc" "-k"`, `_require_no_compress`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- ENOSPC cases are deliberately capacity-sensitive and can expose allocator, reservation, or delayed-allocation leaks only when scratch sizing and reserved blocks match the scenario.

## Test Signals

The pass signal is explicit `_fail` assertions. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/274 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/275 -->
# sources/test-tools/xfstests/tests/generic/275

## Purpose

The posix write test. When write size is larger than disk free size, should write as much as possible until ENOSPC creator This test requires specific data space usage, skip if we have compression enabled. It is registered with `_begin_fstest auto rw enospc` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `275` plus `_begin_fstest auto rw enospc`. Imported libraries: `. ./common/preamble`, `. ./common/filter`. Capability gates: `_require_scratch`, `_require_no_compress`. Local functions: `_cleanup`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 44: `later_file=$SCRATCH_MNT/later`
- Line 71: `_freespace=`$DF_PROG -k $SCRATCH_MNT | tail -n 1 | awk '{print $5}'``
- Line 81: `_filesize=`_get_filesize $later_file``
- Line 86: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 30 `echo "------------------------------"`, line 31 `echo "write until ENOSPC test"`, line 32 `echo "------------------------------"`, line 63 `echo "Pre rm space:" >> $seqres.full`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 19: `_scratch_unmount`
- Line 24: `_require_scratch`
- Line 34: `_scratch_unmount 2>/dev/null`
- Line 35: `_scratch_mkfs_sized $((2 * 1024 * 1024 * 1024)) >>$seqres.full 2>&1`
- Line 36: `_scratch_mount`
- Line 45: `touch $later_file`
- Line 47: `touch $SCRATCH_MNT/tmp$i`
- Line 52: `dd if=/dev/zero of=$SCRATCH_MNT/tmp1 bs=256K count=1 >>$seqres.full 2>&1`
- Line 56: `dd if=/dev/zero of=$SCRATCH_MNT/tmp2 bs=1M >>$seqres.full 2>&1`
- Line 57: `_scratch_sync`
- Line 58: `dd if=/dev/zero of=$SCRATCH_MNT/tmp3 bs=4K >>$seqres.full 2>&1`
- Line 59: `_scratch_sync`
- Line 61: `dd if=/dev/zero of=$SCRATCH_MNT/tmp4 bs=4K oflag=sync >>$seqres.full 2>&1`
- Line 78: `du $later_file >>$seqres.full`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `rw`, `enospc`, imports `. ./common/preamble`, `. ./common/filter`, and uses capability gates such as `_require_scratch`, `_require_no_compress`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Direct I/O paths can be affected by device sector size, alignment, cache invalidation, and filesystem-specific serialization between buffered and direct writes.
- ENOSPC cases are deliberately capacity-sensitive and can expose allocator, reservation, or delayed-allocation leaks only when scratch sizing and reserved blocks match the scenario.

## Test Signals

The pass signal is explicit `_fail` assertions. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/275 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/276 -->
# sources/test-tools/xfstests/tests/generic/276

## Purpose

Test DIO CoW behavior when the write temporarily fails and we unmount. It is registered with `_begin_fstest auto quick clone eio` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `276` plus `_begin_fstest auto quick clone eio`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`, `. ./common/dmerror`. Capability gates: `_require_scratch_reflink`, `_require_cp_reflink`, `_require_dm_target error`, `_require_odirect`, `_require_fs_space $SCRATCH_MNT $((filesize / 1024 * 3 * 5 / 4))`. Local functions: `_cleanup`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 35: `testdir=$SCRATCH_MNT/test-$seq`
- Line 38: `blksz=65536`
- Line 39: `nr=640`
- Line 40: `bufnr=128`
- Line 41: `filesize=$((blksz * nr))`
- Line 42: `bufsize=$((blksz * bufnr))`
- Line 75: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 30 `echo "Format and mount"`, line 46 `echo "Create the original files"`, line 52 `echo "Compare files"`, line 56 `echo "CoW and unmount"`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 16: `rm -rf $tmp.*`
- Line 25: `_require_scratch_reflink`
- Line 27: `_require_dm_target error`
- Line 31: `_scratch_mkfs > $seqres.full 2>&1`
- Line 33: `_dmerror_mount >> $seqres.full 2>&1`
- Line 47: `$XFS_IO_PROG -f -c "pwrite -S 0x61 -b $bufsize 0 $filesize" $testdir/file1 >> $seqres.full`
- Line 49: `_dmerror_unmount`
- Line 53: `md5sum $testdir/file1 | _filter_scratch`
- Line 56: `echo "CoW and unmount"`
- Line 58: `_dmerror_load_error_table`
- Line 61: `_dmerror_load_working_table`
- Line 63: `_dmerror_unmount`
- Line 67: `md5sum $testdir/file1 | _filter_scratch`
- Line 72: `_repair_scratch_fs >> $seqres.full`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Temporary files are rooted at `$tmp.*` and removed by the local or default cleanup path. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `clone`, `eio`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`, `. ./common/dmerror`, and uses capability gates such as `_require_scratch_reflink`, `_require_cp_reflink`, `_require_dm_target error`, `_require_odirect`, `_require_fs_space $SCRATCH_MNT $((filesize / 1024 * 3 * 5 / 4))`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Reflink coverage is sensitive to extent alignment, delayed allocation, unwritten extents, and page-size dependent block geometry, so comparisons against check files are the main correctness guard.
- Direct I/O paths can be affected by device sector size, alignment, cache invalidation, and filesystem-specific serialization between buffered and direct writes.

## Test Signals

The pass signal is filtered `md5sum` output. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/276 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/277 -->
# sources/test-tools/xfstests/tests/generic/277

## Purpose

Check if ctime update caused by chattr is written to disk. It is registered with `_begin_fstest auto ioctl quick metadata` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `277` plus `_begin_fstest auto ioctl quick metadata`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`. Capability gates: `_require_scratch`, `_require_chattr A`. Local functions: `_cleanup`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 30: `ctime1=`stat -c %z $SCRATCH_MNT/tmp``
- Line 35: `ctime2=`stat -c %z $SCRATCH_MNT/tmp``
- Line 38: `ctime3=`stat -c %z $SCRATCH_MNT/tmp``
- Line 45: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 41 `echo "error: ctime not updated after chattr"`, line 43 `echo "error: on disk ctime not updated"`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 15: `rm -f $SCRATCH_MNT/tmp*`
- Line 22: `_require_scratch`
- Line 25: `_scratch_mkfs > /dev/null 2>&1`
- Line 26: `_scratch_mount`
- Line 28: `touch $SCRATCH_MNT/tmp`
- Line 29: `_scratch_cycle_mount`
- Line 30: `ctime1=`stat -c %z $SCRATCH_MNT/tmp``
- Line 35: `ctime2=`stat -c %z $SCRATCH_MNT/tmp``
- Line 37: `_scratch_cycle_mount`
- Line 38: `ctime3=`stat -c %z $SCRATCH_MNT/tmp``

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Cycle-mount calls force metadata and extent state through unmount/remount persistence before validation. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `ioctl`, `quick`, `metadata`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`, and uses capability gates such as `_require_scratch`, `_require_chattr A`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- The main risk is environment drift: missing helper binaries, unsupported filesystem operations, or output formatting changes can make the test skip or fail without indicating a filesystem regression.

## Test Signals

The pass signal is stat/lstat metadata output. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/277 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/278 -->
# sources/test-tools/xfstests/tests/generic/278

## Purpose

Test DIO CoW behavior when the write temporarily fails but the userspace program writes again. It is registered with `_begin_fstest auto quick clone eio` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `278` plus `_begin_fstest auto quick clone eio`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`, `. ./common/dmerror`. Capability gates: `_require_scratch_reflink`, `_require_cp_reflink`, `_require_dm_target error`, `_require_odirect`, `_require_fs_space $SCRATCH_MNT $((filesize / 1024 * 3 * 5 / 4))`. Local functions: `_cleanup`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 36: `testdir=$SCRATCH_MNT/test-$seq`
- Line 39: `blksz=65536`
- Line 40: `nr=640`
- Line 41: `filesize=$((blksz * nr))`
- Line 42: `bufnr=128`
- Line 43: `bufsize=$((blksz * bufnr))`
- Line 60: `urk=$($XFS_IO_PROG -d -f -c "pwrite -S 0x63 -b $bufsize 0 $filesize" $testdir/file2 2>&1)`
- Line 79: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 31 `echo "Format and mount"`, line 47 `echo "Create the original files"`, line 53 `echo "Compare files"`, line 57 `echo "CoW and unmount"`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 17: `rm -rf $tmp.*`
- Line 26: `_require_scratch_reflink`
- Line 28: `_require_dm_target error`
- Line 32: `_scratch_mkfs > $seqres.full 2>&1`
- Line 34: `_dmerror_mount >> $seqres.full 2>&1`
- Line 48: `$XFS_IO_PROG -f -c "pwrite -S 0x61 -b $bufsize 0 $filesize" $testdir/file1 >> $seqres.full`
- Line 50: `_dmerror_unmount`
- Line 54: `md5sum $testdir/file1 | _filter_scratch`
- Line 57: `echo "CoW and unmount"`
- Line 59: `_dmerror_load_error_table`
- Line 63: `_dmerror_load_working_table`
- Line 67: `_dmerror_unmount`
- Line 71: `md5sum $testdir/file1 | _filter_scratch`
- Line 76: `_repair_scratch_fs >> $seqres.full`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Temporary files are rooted at `$tmp.*` and removed by the local or default cleanup path. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `clone`, `eio`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`, `. ./common/dmerror`, and uses capability gates such as `_require_scratch_reflink`, `_require_cp_reflink`, `_require_dm_target error`, `_require_odirect`, `_require_fs_space $SCRATCH_MNT $((filesize / 1024 * 3 * 5 / 4))`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Reflink coverage is sensitive to extent alignment, delayed allocation, unwritten extents, and page-size dependent block geometry, so comparisons against check files are the main correctness guard.
- Direct I/O paths can be affected by device sector size, alignment, cache invalidation, and filesystem-specific serialization between buffered and direct writes.

## Test Signals

The pass signal is filtered `md5sum` output, explicit `_fail` assertions. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/278 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/279 -->
# sources/test-tools/xfstests/tests/generic/279

## Purpose

Test mmap CoW behavior when the write temporarily fails. It is registered with `_begin_fstest auto quick clone eio mmap` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `279` plus `_begin_fstest auto quick clone eio mmap`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`, `. ./common/dmerror`. Capability gates: `_require_scratch_reflink`, `_require_cp_reflink`, `_require_dm_target error`, `_require_fs_space $SCRATCH_MNT $((filesize / 1024 * 3 * 5 / 4))`. Local functions: `_cleanup`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 34: `testdir=$SCRATCH_MNT/test-$seq`
- Line 37: `blksz=65536`
- Line 38: `nr=640`
- Line 39: `bufnr=128`
- Line 40: `filesize=$((blksz * nr))`
- Line 41: `bufsize=$((blksz * bufnr))`
- Line 79: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 29 `echo "Format and mount"`, line 45 `echo "Create the original files"`, line 51 `echo "Compare files"`, line 55 `echo "CoW and unmount"`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 10: `_begin_fstest auto quick clone eio mmap`
- Line 17: `_dmerror_cleanup`
- Line 26: `_require_cp_reflink`
- Line 29: `echo "Format and mount"`
- Line 31: `_dmerror_init`
- Line 35: `mkdir $testdir`
- Line 47: `_cp_reflink $testdir/file1 $testdir/file2 >> $seqres.full`
- Line 49: `_dmerror_mount`
- Line 53: `md5sum $testdir/file2 | _filter_scratch`
- Line 56: `_scratch_sync`
- Line 61: `ulimit -c 0`
- Line 63: `-c "msync -s 0 $filesize" $testdir/file2 >> $seqres.full 2>&1`
- Line 67: `_dmerror_unmount`
- Line 76: `_repair_scratch_fs >> $seqres.full`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. It may also use `$TEST_DIR` for non-destructive helper programs or limit checks. Temporary files are rooted at `$tmp.*` and removed by the local or default cleanup path. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `clone`, `eio`, `mmap`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`, `. ./common/dmerror`, and uses capability gates such as `_require_scratch_reflink`, `_require_cp_reflink`, `_require_dm_target error`, `_require_fs_space $SCRATCH_MNT $((filesize / 1024 * 3 * 5 / 4))`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Reflink coverage is sensitive to extent alignment, delayed allocation, unwritten extents, and page-size dependent block geometry, so comparisons against check files are the main correctness guard.
- mmap tests rely on page-cache writeback, timestamp granularity, and correct handling of dirty mappings across fsync, sync, or remount boundaries.

## Test Signals

The pass signal is filtered `md5sum` output. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/279 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/280 -->
# sources/test-tools/xfstests/tests/generic/280

## Purpose

Test quota vs. suspend/freeze deadlock, dcdbed85 quota: Fix deadlock with suspend and quotas Modify as appropriate. It is registered with `_begin_fstest auto quota freeze` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `280` plus `_begin_fstest auto quota freeze`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/quota`. Capability gates: `_require_scratch`, `_require_quota`, `_require_freeze`. Local functions: `_cleanup`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 42: `pid=$!`
- Line 51: `status=0`

## Control Flow

Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 11: `_begin_fstest auto quota freeze`
- Line 18: `[ -n "$pid" ] && kill -9 $pid 2>/dev/null`
- Line 21: `rm -f $tmp.*`
- Line 26: `. ./common/quota`
- Line 28: `_require_scratch`
- Line 29: `_require_quota`
- Line 35: `_scratch_unmount 2>/dev/null`
- Line 36: `_scratch_mkfs >> $seqres.full 2>&1`
- Line 37: `_scratch_mount "-o usrquota,grpquota"`
- Line 38: `quotacheck -u -g $SCRATCH_MNT 2>/dev/null`
- Line 39: `quotaon $SCRATCH_MNT 2>/dev/null`
- Line 41: `setquota -u root 1 2 3 4 $SCRATCH_MNT &`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Quota state is persistent filesystem metadata manipulated through `quotacheck`, `quotaon`, `setquota`, and `repquota` across user and group modes. Temporary files are rooted at `$tmp.*` and removed by the local or default cleanup path. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quota`, `freeze`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/quota`, and uses capability gates such as `_require_scratch`, `_require_quota`, `_require_freeze`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Quota tests depend on kernel quota mode, grace-period timing, and the qa user/group setup; stale quota files or unsupported VFS quota behavior can turn a real failure into a notrun or noisy output mismatch.

## Test Signals

The pass signal is silence from the helper program and final `status=0`. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/280 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/281 -->
# sources/test-tools/xfstests/tests/generic/281

## Purpose

Test mmap CoW behavior when the write permanently fails. It is registered with `_begin_fstest auto quick clone eio mmap` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `281` plus `_begin_fstest auto quick clone eio mmap`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`, `. ./common/dmerror`. Capability gates: `_require_scratch_reflink`, `_require_cp_reflink`, `_require_dm_target error`, `_require_fs_space $SCRATCH_MNT $((filesize / 1024 * 3 * 5 / 4))`. Local functions: `_cleanup`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 34: `testdir=$SCRATCH_MNT/test-$seq`
- Line 37: `blksz=65536`
- Line 38: `nr=640`
- Line 39: `bufnr=128`
- Line 40: `filesize=$((blksz * nr))`
- Line 41: `bufsize=$((blksz * bufnr))`
- Line 77: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 29 `echo "Format and mount"`, line 45 `echo "Create the original files"`, line 51 `echo "Compare files"`, line 55 `echo "CoW and unmount"`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 10: `_begin_fstest auto quick clone eio mmap`
- Line 17: `_dmerror_cleanup`
- Line 26: `_require_cp_reflink`
- Line 29: `echo "Format and mount"`
- Line 31: `_dmerror_init`
- Line 35: `mkdir $testdir`
- Line 47: `_cp_reflink $testdir/file1 $testdir/file2 >> $seqres.full`
- Line 49: `_dmerror_mount`
- Line 53: `md5sum $testdir/file2 | _filter_scratch`
- Line 56: `_scratch_sync`
- Line 61: `ulimit -c 0`
- Line 63: `-c "msync -s 0 $filesize" $testdir/file2 >> $seqres.full 2>&1`
- Line 69: `_dmerror_cleanup`
- Line 74: `md5sum $testdir/file1 | _filter_scratch`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. It may also use `$TEST_DIR` for non-destructive helper programs or limit checks. Temporary files are rooted at `$tmp.*` and removed by the local or default cleanup path. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `clone`, `eio`, `mmap`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`, `. ./common/dmerror`, and uses capability gates such as `_require_scratch_reflink`, `_require_cp_reflink`, `_require_dm_target error`, `_require_fs_space $SCRATCH_MNT $((filesize / 1024 * 3 * 5 / 4))`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Reflink coverage is sensitive to extent alignment, delayed allocation, unwritten extents, and page-size dependent block geometry, so comparisons against check files are the main correctness guard.
- mmap tests rely on page-cache writeback, timestamp granularity, and correct handling of dirty mappings across fsync, sync, or remount boundaries.

## Test Signals

The pass signal is filtered `md5sum` output. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/281 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/282 -->
# sources/test-tools/xfstests/tests/generic/282

## Purpose

Test mmap CoW behavior when the write temporarily fails and we unmount. It is registered with `_begin_fstest auto quick clone eio mmap` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `282` plus `_begin_fstest auto quick clone eio mmap`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`, `. ./common/dmerror`. Capability gates: `_require_scratch_reflink`, `_require_cp_reflink`, `_require_dm_target error`, `_require_fs_space $SCRATCH_MNT $((filesize / 1024 * 3 * 5 / 4))`. Local functions: `_cleanup`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 34: `testdir=$SCRATCH_MNT/test-$seq`
- Line 37: `blksz=65536`
- Line 38: `nr=640`
- Line 39: `bufnr=128`
- Line 40: `filesize=$((blksz * nr))`
- Line 41: `bufsize=$((blksz * bufnr))`
- Line 80: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 29 `echo "Format and mount"`, line 45 `echo "Create the original files"`, line 51 `echo "Compare files"`, line 55 `echo "CoW and unmount"`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 10: `_begin_fstest auto quick clone eio mmap`
- Line 17: `_dmerror_cleanup`
- Line 26: `_require_cp_reflink`
- Line 29: `echo "Format and mount"`
- Line 31: `_dmerror_init`
- Line 35: `mkdir $testdir`
- Line 47: `_cp_reflink $testdir/file1 $testdir/file2 >> $seqres.full`
- Line 49: `_dmerror_mount`
- Line 53: `md5sum $testdir/file2 | _filter_scratch`
- Line 56: `_scratch_sync`
- Line 61: `ulimit -c 0`
- Line 63: `-c "mwrite -S 0x63 0 $filesize" $testdir/file2 >> $seqres.full 2>&1`
- Line 67: `rm -rf $testdir/file2 >> $seqres.full 2>&1`
- Line 77: `_repair_scratch_fs >> $seqres.full`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. It may also use `$TEST_DIR` for non-destructive helper programs or limit checks. Temporary files are rooted at `$tmp.*` and removed by the local or default cleanup path. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `clone`, `eio`, `mmap`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`, `. ./common/dmerror`, and uses capability gates such as `_require_scratch_reflink`, `_require_cp_reflink`, `_require_dm_target error`, `_require_fs_space $SCRATCH_MNT $((filesize / 1024 * 3 * 5 / 4))`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Reflink coverage is sensitive to extent alignment, delayed allocation, unwritten extents, and page-size dependent block geometry, so comparisons against check files are the main correctness guard.
- mmap tests rely on page-cache writeback, timestamp granularity, and correct handling of dirty mappings across fsync, sync, or remount boundaries.

## Test Signals

The pass signal is filtered `md5sum` output. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/282 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/283 -->
# sources/test-tools/xfstests/tests/generic/283

## Purpose

Test mmap CoW behavior when the write temporarily fails but the userspace program writes again. It is registered with `_begin_fstest auto quick clone eio mmap` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `283` plus `_begin_fstest auto quick clone eio mmap`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`, `. ./common/dmerror`. Capability gates: `_require_scratch_reflink`, `_require_cp_reflink`, `_require_dm_target error`, `_require_fs_space $SCRATCH_MNT $((filesize / 1024 * 3 * 5 / 4))`. Local functions: `_cleanup`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 35: `testdir=$SCRATCH_MNT/test-$seq`
- Line 38: `blksz=65536`
- Line 39: `nr=640`
- Line 40: `bufnr=128`
- Line 41: `filesize=$((blksz * nr))`
- Line 42: `bufsize=$((blksz * bufnr))`
- Line 85: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 30 `echo "Format and mount"`, line 46 `echo "Create the original files"`, line 52 `echo "Compare files"`, line 56 `echo "CoW and unmount"`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 11: `_begin_fstest auto quick clone eio mmap`
- Line 18: `_dmerror_cleanup`
- Line 27: `_require_cp_reflink`
- Line 30: `echo "Format and mount"`
- Line 32: `_dmerror_init`
- Line 36: `mkdir $testdir`
- Line 48: `_cp_reflink $testdir/file1 $testdir/file2 >> $seqres.full`
- Line 50: `_dmerror_mount`
- Line 54: `md5sum $testdir/file2 | _filter_scratch`
- Line 57: `_scratch_sync`
- Line 62: `ulimit -c 0`
- Line 64: `-c "msync -s 0 $filesize" $testdir/file2 2>&1`
- Line 69: `_dmerror_load_working_table`
- Line 82: `_repair_scratch_fs >> $seqres.full`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. It may also use `$TEST_DIR` for non-destructive helper programs or limit checks. Temporary files are rooted at `$tmp.*` and removed by the local or default cleanup path. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `clone`, `eio`, `mmap`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`, `. ./common/dmerror`, and uses capability gates such as `_require_scratch_reflink`, `_require_cp_reflink`, `_require_dm_target error`, `_require_fs_space $SCRATCH_MNT $((filesize / 1024 * 3 * 5 / 4))`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Reflink coverage is sensitive to extent alignment, delayed allocation, unwritten extents, and page-size dependent block geometry, so comparisons against check files are the main correctness guard.
- mmap tests rely on page-cache writeback, timestamp granularity, and correct handling of dirty mappings across fsync, sync, or remount boundaries.

## Test Signals

The pass signal is filtered `md5sum` output, explicit `_fail` assertions. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/283 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/284 -->
# sources/test-tools/xfstests/tests/generic/284

## Purpose

Ensuring that copy on write in buffered mode to the source file when the CoW range covers regular unshared and regular shared blocks - Create two files - Reflink the odd blocks of the first file into the second file - CoW the first file across the halfway mark, starting with the regular extent - Check that the files are now different where we say they're different. It is registered with `_begin_fstest auto quick clone prealloc` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `284` plus `_begin_fstest auto quick clone prealloc`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`. Capability gates: `_require_scratch_reflink`, `_require_xfs_io_command "falloc"`, `_require_congruent_file_oplen $SCRATCH_MNT $blksz`. Local functions: none. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 29: `testdir=$SCRATCH_MNT/test-$seq`
- Line 33: `blksz=65536`
- Line 35: `nr=64`
- Line 36: `filesize=$((blksz * nr))`
- Line 46: `cowoff=$((filesize / 4))`
- Line 47: `cowsz=$((filesize / 2))`
- Line 58: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 25 `echo "Format and mount"`, line 32 `echo "Create the original files"`, line 40 `echo "Compare files"`, line 45 `echo "CoW across the transition"`. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 22: `_require_scratch_reflink`
- Line 23: `_require_xfs_io_command "falloc"`
- Line 25: `echo "Format and mount"`
- Line 26: `_scratch_mkfs > $seqres.full 2>&1`
- Line 27: `_scratch_mount >> $seqres.full 2>&1`
- Line 30: `mkdir $testdir`
- Line 37: `_sweave_reflink_regular $blksz $nr $testdir/file1 $testdir/file3 >> $seqres.full`
- Line 38: `_scratch_cycle_mount`
- Line 41: `md5sum $testdir/file1 | _filter_scratch`
- Line 42: `md5sum $testdir/file3 | _filter_scratch`
- Line 43: `md5sum $testdir/file1.chk | _filter_scratch`
- Line 48: `$XFS_IO_PROG -f -c "pwrite -S 0x63 -b $cowsz $cowoff $cowsz" $testdir/file1 >> $seqres.full`
- Line 49: `_pwrite_byte 0x63 $cowoff $cowsz $testdir/file1.chk >> $seqres.full`
- Line 55: `md5sum $testdir/file1.chk | _filter_scratch`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Cycle-mount calls force metadata and extent state through unmount/remount persistence before validation. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `clone`, `prealloc`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`, and uses capability gates such as `_require_scratch_reflink`, `_require_xfs_io_command "falloc"`, `_require_congruent_file_oplen $SCRATCH_MNT $blksz`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Reflink coverage is sensitive to extent alignment, delayed allocation, unwritten extents, and page-size dependent block geometry, so comparisons against check files are the main correctness guard.

## Test Signals

The pass signal is filtered `md5sum` output. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/284 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/285 -->
# sources/test-tools/xfstests/tests/generic/285

## Purpose

SEEK_DATA/SEEK_HOLE sanity tests Improved by Jeff.liu@oracle.com Creater: josef@redhat.com. It is registered with `_begin_fstest auto rw seek` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `285` plus `_begin_fstest auto rw seek`. Imported libraries: `. ./common/preamble`, `. ./common/filter`. Capability gates: `_require_test`, `_require_seek_data_hole`, `_require_test_program "seek_sanity_test"`. Local functions: `_cleanup`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 23: `BASE_TEST_FILE=$TEST_DIR/seek_sanity_testfile`
- Line 37: `status=0`

## Control Flow

Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 20: `_require_test`
- Line 23: `BASE_TEST_FILE=$TEST_DIR/seek_sanity_testfile`
- Line 25: `_require_test_program "seek_sanity_test"`
- Line 30: `rm -f $BASE_TEST_FILE*`
- Line 33: `_run_seek_sanity_test $BASE_TEST_FILE > $seqres.full 2>&1 ||`

## State and Persistence Behavior

Primary state lives under `$TEST_DIR`, making this a test-device workload rather than a scratch-device destructive test. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `rw`, `seek`, imports `. ./common/preamble`, `. ./common/filter`, and uses capability gates such as `_require_test`, `_require_seek_data_hole`, `_require_test_program "seek_sanity_test"`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- The main risk is environment drift: missing helper binaries, unsupported filesystem operations, or output formatting changes can make the test skip or fail without indicating a filesystem regression.

## Test Signals

The pass signal is explicit `_fail` assertions. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/285 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/286 -->
# sources/test-tools/xfstests/tests/generic/286

## Purpose

SEEK_DATA/SEEK_HOLE copy tests seek_copy_test_01: tests file with holes and written data extents verify results: 1. file size is identical 2. perform cmp(1) to compare SRC and DEST file byte by byte. It is registered with `_begin_fstest auto quick other seek prealloc` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `286` plus `_begin_fstest auto quick other seek prealloc`. Imported libraries: `. ./common/preamble`, `. ./common/filter`. Capability gates: `_require_test`, `_require_xfs_io_command "falloc"`, `_require_seek_data_hole`, `_require_test_program "seek_copy_test"`. Local functions: `_cleanup`, `test01`, `test02`, `test03`, `test04`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 20: `src=$TEST_DIR/seek_copy_testfile`
- Line 21: `dest=$TEST_DIR/seek_copy_testfile.dest`
- Line 39: `write_cmd="-c \"truncate 100m\""`
- Line 41: `offset=$(($i * $((1 << 20))))`
- Line 42: `write_cmd="$write_cmd -c \"pwrite $offset 1m\""`
- Line 67: `write_cmd="-c \"truncate 200m\""`
- Line 69: `offset=$(($((6 << 20)) + $i * $((1 << 20))))`
- Line 70: `write_cmd="$write_cmd -c \"falloc $offset 3m\" -c \"pwrite $offset 1m\""`

## Control Flow

The visible phases are driven by echo markers such as line 45 `echo "*** test01() create sparse file ***" >>$seqres.full`, line 48 `echo "*** test01() create sparse file done ***" >>$seqres.full`, line 49 `echo >>$seqres.full`, line 73 `echo "*** test02() create sparse file ***" >>$seqres.full`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 16: `_require_test`
- Line 17: `_require_xfs_io_command "falloc"`
- Line 20: `src=$TEST_DIR/seek_copy_testfile`
- Line 21: `dest=$TEST_DIR/seek_copy_testfile.dest`
- Line 23: `_require_test_program "seek_copy_test"`
- Line 28: `rm -f $src $dest`
- Line 37: `rm -f $src $dest`
- Line 39: `write_cmd="-c \"truncate 100m\""`
- Line 51: `$here/src/seek_copy_test $src $dest`
- Line 56: `cmp $src $dest || _fail "TEST01: file bytes check failed"`
- Line 65: `rm -rf $src $dest`
- Line 67: `write_cmd="-c \"truncate 200m\""`
- Line 70: `write_cmd="$write_cmd -c \"falloc $offset 3m\" -c \"pwrite $offset 1m\""`
- Line 168: `cmp $src $dest || _fail "TEST04: file bytes check failed"`

## State and Persistence Behavior

Primary state lives under `$TEST_DIR`, making this a test-device workload rather than a scratch-device destructive test. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `other`, `seek`, `prealloc`, imports `. ./common/preamble`, `. ./common/filter`, and uses capability gates such as `_require_test`, `_require_xfs_io_command "falloc"`, `_require_seek_data_hole`, `_require_test_program "seek_copy_test"`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- The main risk is environment drift: missing helper binaries, unsupported filesystem operations, or output formatting changes can make the test skip or fail without indicating a filesystem regression.

## Test Signals

The pass signal is explicit `_fail` assertions. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/286 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/287 -->
# sources/test-tools/xfstests/tests/generic/287

## Purpose

Ensuring that copy on write in directio mode to the source file when the CoW range covers regular unshared and regular shared blocks - Create two files - Reflink the odd blocks of the first file into the second file - dio CoW the first file across the halfway mark, starting with the regular extent - Check that the files are now different where we say they're different. It is registered with `_begin_fstest auto quick clone prealloc` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `287` plus `_begin_fstest auto quick clone prealloc`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`. Capability gates: `_require_scratch_reflink`, `_require_xfs_io_command "falloc"`, `_require_odirect`, `_require_congruent_file_oplen $SCRATCH_MNT $blksz`. Local functions: none. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 30: `testdir=$SCRATCH_MNT/test-$seq`
- Line 34: `blksz=65536`
- Line 36: `nr=64`
- Line 37: `filesize=$((blksz * nr))`
- Line 47: `cowoff=$((filesize / 4))`
- Line 48: `cowsz=$((filesize / 2))`
- Line 59: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 26 `echo "Format and mount"`, line 33 `echo "Create the original files"`, line 41 `echo "Compare files"`, line 46 `echo "CoW across the transition"`. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 22: `_require_scratch_reflink`
- Line 23: `_require_xfs_io_command "falloc"`
- Line 26: `echo "Format and mount"`
- Line 27: `_scratch_mkfs > $seqres.full 2>&1`
- Line 28: `_scratch_mount >> $seqres.full 2>&1`
- Line 31: `mkdir $testdir`
- Line 38: `_sweave_reflink_regular $blksz $nr $testdir/file1 $testdir/file3 >> $seqres.full`
- Line 39: `_scratch_cycle_mount`
- Line 42: `md5sum $testdir/file1 | _filter_scratch`
- Line 43: `md5sum $testdir/file3 | _filter_scratch`
- Line 44: `md5sum $testdir/file1.chk | _filter_scratch`
- Line 49: `$XFS_IO_PROG -d -f -c "pwrite -S 0x63 -b $cowsz $cowoff $cowsz" $testdir/file1 >> $seqres.full`
- Line 50: `_pwrite_byte 0x63 $cowoff $cowsz $testdir/file1.chk >> $seqres.full`
- Line 56: `md5sum $testdir/file1.chk | _filter_scratch`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Cycle-mount calls force metadata and extent state through unmount/remount persistence before validation. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `clone`, `prealloc`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`, and uses capability gates such as `_require_scratch_reflink`, `_require_xfs_io_command "falloc"`, `_require_odirect`, `_require_congruent_file_oplen $SCRATCH_MNT $blksz`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Reflink coverage is sensitive to extent alignment, delayed allocation, unwritten extents, and page-size dependent block geometry, so comparisons against check files are the main correctness guard.
- Direct I/O paths can be affected by device sector size, alignment, cache invalidation, and filesystem-specific serialization between buffered and direct writes.

## Test Signals

The pass signal is filtered `md5sum` output. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/287 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/288 -->
# sources/test-tools/xfstests/tests/generic/288

## Purpose

This check the FITRIM argument handling in the corner case where length is smaller than block size or zero. It is registered with `_begin_fstest auto quick ioctl trim` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `288` plus `_begin_fstest auto quick ioctl trim`. Imported libraries: `. ./common/preamble`, `. ./common/filter`. Capability gates: `_require_scratch`, `_require_batched_discard $SCRATCH_MNT`. Local functions: none. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 13: `status=0`
- Line 26: `out=$("$FSTRIM_PROG" -v -o0 -l0 $SCRATCH_MNT 2>&1)`
- Line 31: `out=$("$FSTRIM_PROG" -v -o0 -l100 $SCRATCH_MNT 2>&1)`

## Control Flow

The visible phases are driven by echo markers such as line 25 `echo "[+] Length is zero (should fail)"`, line 28 `echo $out | _filter_scratch`, line 30 `echo "[+] Length is smaller than block size (should fail)"`, line 33 `echo $out | _filter_scratch`. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 19: `_require_scratch`
- Line 21: `_scratch_mkfs >/dev/null 2>&1`
- Line 22: `_scratch_mount`
- Line 28: `echo $out | _filter_scratch`
- Line 33: `echo $out | _filter_scratch`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `ioctl`, `trim`, imports `. ./common/preamble`, `. ./common/filter`, and uses capability gates such as `_require_scratch`, `_require_batched_discard $SCRATCH_MNT`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- The main risk is environment drift: missing helper binaries, unsupported filesystem operations, or output formatting changes can make the test skip or fail without indicating a filesystem regression.

## Test Signals

The pass signal is silence from the helper program and final `status=0`. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/288 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/289 -->
# sources/test-tools/xfstests/tests/generic/289

## Purpose

Ensuring that copy on write in buffered mode to the source file when the CoW range covers unwritten and regular shared blocks - Create two files - fallocate the first file - Write the odd blocks of the first file - Reflink the odd blocks of the first file into the second file - CoW the first file across the halfway mark, starting with the regular extent - Check that the files are now different where we say they're different. It is registered with `_begin_fstest auto quick clone prealloc` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `289` plus `_begin_fstest auto quick clone prealloc`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`. Capability gates: `_require_scratch_reflink`, `_require_xfs_io_command "falloc"`, `_require_congruent_file_oplen $SCRATCH_MNT $blksz`. Local functions: none. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 31: `testdir=$SCRATCH_MNT/test-$seq`
- Line 35: `blksz=65536`
- Line 37: `nr=64`
- Line 38: `filesize=$((blksz * nr))`
- Line 48: `cowoff=$((filesize / 4))`
- Line 49: `cowsz=$((filesize / 2))`
- Line 60: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 27 `echo "Format and mount"`, line 34 `echo "Create the original files"`, line 42 `echo "Compare files"`, line 47 `echo "CoW across the transition"`. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 24: `_require_scratch_reflink`
- Line 25: `_require_xfs_io_command "falloc"`
- Line 27: `echo "Format and mount"`
- Line 28: `_scratch_mkfs > $seqres.full 2>&1`
- Line 29: `_scratch_mount >> $seqres.full 2>&1`
- Line 32: `mkdir $testdir`
- Line 39: `_sweave_reflink_unwritten $blksz $nr $testdir/file1 $testdir/file3 >> $seqres.full`
- Line 40: `_scratch_cycle_mount`
- Line 43: `md5sum $testdir/file1 | _filter_scratch`
- Line 44: `md5sum $testdir/file3 | _filter_scratch`
- Line 45: `md5sum $testdir/file1.chk | _filter_scratch`
- Line 50: `$XFS_IO_PROG -f -c "pwrite -S 0x63 -b $cowsz $cowoff $cowsz" $testdir/file1 >> $seqres.full`
- Line 51: `_pwrite_byte 0x63 $cowoff $cowsz $testdir/file1.chk >> $seqres.full`
- Line 57: `md5sum $testdir/file1.chk | _filter_scratch`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Cycle-mount calls force metadata and extent state through unmount/remount persistence before validation. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `clone`, `prealloc`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`, and uses capability gates such as `_require_scratch_reflink`, `_require_xfs_io_command "falloc"`, `_require_congruent_file_oplen $SCRATCH_MNT $blksz`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Reflink coverage is sensitive to extent alignment, delayed allocation, unwritten extents, and page-size dependent block geometry, so comparisons against check files are the main correctness guard.

## Test Signals

The pass signal is filtered `md5sum` output. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/289 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/290 -->
# sources/test-tools/xfstests/tests/generic/290

## Purpose

Ensuring that copy on write in directio mode to the source file when the CoW range covers unwritten and regular shared blocks - Create two files - fallocate the first file - Write the odd blocks of the first file - Reflink the odd blocks of the first file into the second file - DIO CoW the first file across the halfway mark, starting with the regular extent - Check that the files are now different where we say they're different. It is registered with `_begin_fstest auto quick clone prealloc` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `290` plus `_begin_fstest auto quick clone prealloc`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`. Capability gates: `_require_scratch_reflink`, `_require_xfs_io_command "falloc"`, `_require_odirect`, `_require_congruent_file_oplen $SCRATCH_MNT $blksz`. Local functions: none. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 32: `testdir=$SCRATCH_MNT/test-$seq`
- Line 36: `blksz=65536`
- Line 38: `nr=64`
- Line 39: `filesize=$((blksz * nr))`
- Line 49: `cowoff=$((filesize / 4))`
- Line 50: `cowsz=$((filesize / 2))`
- Line 61: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 28 `echo "Format and mount"`, line 35 `echo "Create the original files"`, line 43 `echo "Compare files"`, line 48 `echo "CoW across the transition"`. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 24: `_require_scratch_reflink`
- Line 25: `_require_xfs_io_command "falloc"`
- Line 28: `echo "Format and mount"`
- Line 29: `_scratch_mkfs > $seqres.full 2>&1`
- Line 30: `_scratch_mount >> $seqres.full 2>&1`
- Line 33: `mkdir $testdir`
- Line 40: `_sweave_reflink_unwritten $blksz $nr $testdir/file1 $testdir/file3 >> $seqres.full`
- Line 41: `_scratch_cycle_mount`
- Line 44: `md5sum $testdir/file1 | _filter_scratch`
- Line 45: `md5sum $testdir/file3 | _filter_scratch`
- Line 46: `md5sum $testdir/file1.chk | _filter_scratch`
- Line 51: `$XFS_IO_PROG -d -f -c "pwrite -S 0x63 -b $cowsz $cowoff $cowsz" $testdir/file1 >> $seqres.full`
- Line 52: `_pwrite_byte 0x63 $cowoff $cowsz $testdir/file1.chk >> $seqres.full`
- Line 58: `md5sum $testdir/file1.chk | _filter_scratch`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Cycle-mount calls force metadata and extent state through unmount/remount persistence before validation. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `clone`, `prealloc`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`, and uses capability gates such as `_require_scratch_reflink`, `_require_xfs_io_command "falloc"`, `_require_odirect`, `_require_congruent_file_oplen $SCRATCH_MNT $blksz`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Reflink coverage is sensitive to extent alignment, delayed allocation, unwritten extents, and page-size dependent block geometry, so comparisons against check files are the main correctness guard.
- Direct I/O paths can be affected by device sector size, alignment, cache invalidation, and filesystem-specific serialization between buffered and direct writes.

## Test Signals

The pass signal is filtered `md5sum` output. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/290 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/291 -->
# sources/test-tools/xfstests/tests/generic/291

## Purpose

Ensuring that copy on write in buffered mode to the source file when the CoW range covers holes and regular shared blocks - Create two files - Truncate the first file - Write the odd blocks of the first file - Reflink the odd blocks of the first file into the second file - CoW the first file across the halfway mark, starting with the regular extent - Check that the files are now different where we say they're different. It is registered with `_begin_fstest auto quick clone prealloc` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `291` plus `_begin_fstest auto quick clone prealloc`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`. Capability gates: `_require_scratch_reflink`, `_require_xfs_io_command "falloc"`, `_require_congruent_file_oplen $SCRATCH_MNT $blksz`. Local functions: none. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 31: `testdir=$SCRATCH_MNT/test-$seq`
- Line 35: `blksz=65536`
- Line 37: `nr=64`
- Line 38: `filesize=$((blksz * nr))`
- Line 48: `cowoff=$((filesize / 4))`
- Line 49: `cowsz=$((filesize / 2))`
- Line 60: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 27 `echo "Format and mount"`, line 34 `echo "Create the original files"`, line 42 `echo "Compare files"`, line 47 `echo "CoW across the transition"`. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 24: `_require_scratch_reflink`
- Line 25: `_require_xfs_io_command "falloc"`
- Line 27: `echo "Format and mount"`
- Line 28: `_scratch_mkfs > $seqres.full 2>&1`
- Line 29: `_scratch_mount >> $seqres.full 2>&1`
- Line 32: `mkdir $testdir`
- Line 39: `_sweave_reflink_holes $blksz $nr $testdir/file1 $testdir/file3 >> $seqres.full`
- Line 40: `_scratch_cycle_mount`
- Line 43: `md5sum $testdir/file1 | _filter_scratch`
- Line 44: `md5sum $testdir/file3 | _filter_scratch`
- Line 45: `md5sum $testdir/file1.chk | _filter_scratch`
- Line 50: `$XFS_IO_PROG -f -c "pwrite -S 0x63 -b $cowsz $cowoff $cowsz" $testdir/file1 >> $seqres.full`
- Line 51: `_pwrite_byte 0x63 $cowoff $cowsz $testdir/file1.chk >> $seqres.full`
- Line 57: `md5sum $testdir/file1.chk | _filter_scratch`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Cycle-mount calls force metadata and extent state through unmount/remount persistence before validation. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `clone`, `prealloc`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`, and uses capability gates such as `_require_scratch_reflink`, `_require_xfs_io_command "falloc"`, `_require_congruent_file_oplen $SCRATCH_MNT $blksz`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Reflink coverage is sensitive to extent alignment, delayed allocation, unwritten extents, and page-size dependent block geometry, so comparisons against check files are the main correctness guard.

## Test Signals

The pass signal is filtered `md5sum` output. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/291 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/292 -->
# sources/test-tools/xfstests/tests/generic/292

## Purpose

Ensuring that copy on write in directio mode to the source file when the CoW range covers holes and regular shared blocks - Create two files - Truncate the first file - Write the odd blocks of the first file - Reflink the odd blocks of the first file into the second file - DIO CoW the first file across the halfway mark, starting with the regular extent - Check that the files are now different where we say they're different. It is registered with `_begin_fstest auto quick clone prealloc` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `292` plus `_begin_fstest auto quick clone prealloc`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`. Capability gates: `_require_scratch_reflink`, `_require_xfs_io_command "falloc"`, `_require_odirect`, `_require_congruent_file_oplen $SCRATCH_MNT $blksz`. Local functions: none. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 32: `testdir=$SCRATCH_MNT/test-$seq`
- Line 36: `blksz=65536`
- Line 38: `nr=64`
- Line 39: `filesize=$((blksz * nr))`
- Line 49: `cowoff=$((filesize / 4))`
- Line 50: `cowsz=$((filesize / 2))`
- Line 61: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 28 `echo "Format and mount"`, line 35 `echo "Create the original files"`, line 43 `echo "Compare files"`, line 48 `echo "CoW across the transition"`. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 24: `_require_scratch_reflink`
- Line 25: `_require_xfs_io_command "falloc"`
- Line 28: `echo "Format and mount"`
- Line 29: `_scratch_mkfs > $seqres.full 2>&1`
- Line 30: `_scratch_mount >> $seqres.full 2>&1`
- Line 33: `mkdir $testdir`
- Line 40: `_sweave_reflink_holes $blksz $nr $testdir/file1 $testdir/file3 >> $seqres.full`
- Line 41: `_scratch_cycle_mount`
- Line 44: `md5sum $testdir/file1 | _filter_scratch`
- Line 45: `md5sum $testdir/file3 | _filter_scratch`
- Line 46: `md5sum $testdir/file1.chk | _filter_scratch`
- Line 51: `$XFS_IO_PROG -d -f -c "pwrite -S 0x63 -b $cowsz $cowoff $cowsz" $testdir/file1 >> $seqres.full`
- Line 52: `_pwrite_byte 0x63 $cowoff $cowsz $testdir/file1.chk >> $seqres.full`
- Line 58: `md5sum $testdir/file1.chk | _filter_scratch`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Cycle-mount calls force metadata and extent state through unmount/remount persistence before validation. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `clone`, `prealloc`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`, and uses capability gates such as `_require_scratch_reflink`, `_require_xfs_io_command "falloc"`, `_require_odirect`, `_require_congruent_file_oplen $SCRATCH_MNT $blksz`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Reflink coverage is sensitive to extent alignment, delayed allocation, unwritten extents, and page-size dependent block geometry, so comparisons against check files are the main correctness guard.
- Direct I/O paths can be affected by device sector size, alignment, cache invalidation, and filesystem-specific serialization between buffered and direct writes.

## Test Signals

The pass signal is filtered `md5sum` output. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/292 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/293 -->
# sources/test-tools/xfstests/tests/generic/293

## Purpose

Ensuring that copy on write in buffered mode to the source file when the CoW range covers delalloc blocks and regular shared blocks - Create two files - Truncate the first file - Write the odd blocks of the first file - Reflink the odd blocks of the first file into the second file - Write the even blocks of the first file - CoW the first file across the halfway mark, starting with the regular extent - Check that the files are now different where we say they're different. It is registered with `_begin_fstest auto quick clone prealloc` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `293` plus `_begin_fstest auto quick clone prealloc`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`. Capability gates: `_require_scratch_reflink`, `_require_scratch_delalloc`, `_require_xfs_io_command "falloc"`, `_require_congruent_file_oplen $SCRATCH_MNT $blksz`. Local functions: none. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 33: `testdir=$SCRATCH_MNT/test-$seq`
- Line 37: `blksz=65536`
- Line 39: `nr=64`
- Line 40: `filesize=$((blksz * nr))`
- Line 50: `cowoff=$((filesize / 4))`
- Line 51: `cowsz=$((filesize / 2))`
- Line 63: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 29 `echo "Format and mount"`, line 36 `echo "Create the original files"`, line 44 `echo "Compare files"`, line 49 `echo "CoW across the transition"`. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 25: `_require_scratch_reflink`
- Line 26: `_require_scratch_delalloc`
- Line 27: `_require_xfs_io_command "falloc"`
- Line 29: `echo "Format and mount"`
- Line 30: `_scratch_mkfs > $seqres.full 2>&1`
- Line 31: `_scratch_mount >> $seqres.full 2>&1`
- Line 34: `mkdir $testdir`
- Line 41: `_sweave_reflink_holes $blksz $nr $testdir/file1 $testdir/file3 >> $seqres.full`
- Line 42: `_scratch_cycle_mount`
- Line 45: `md5sum $testdir/file1 | _filter_scratch`
- Line 46: `md5sum $testdir/file3 | _filter_scratch`
- Line 47: `md5sum $testdir/file1.chk | _filter_scratch`
- Line 52: `_sweave_reflink_holes_delalloc $blksz $nr $testdir/file1 >> $seqres.full`
- Line 60: `md5sum $testdir/file1.chk | _filter_scratch`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Cycle-mount calls force metadata and extent state through unmount/remount persistence before validation. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `clone`, `prealloc`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`, and uses capability gates such as `_require_scratch_reflink`, `_require_scratch_delalloc`, `_require_xfs_io_command "falloc"`, `_require_congruent_file_oplen $SCRATCH_MNT $blksz`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Reflink coverage is sensitive to extent alignment, delayed allocation, unwritten extents, and page-size dependent block geometry, so comparisons against check files are the main correctness guard.

## Test Signals

The pass signal is filtered `md5sum` output. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/293 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/294 -->
# sources/test-tools/xfstests/tests/generic/294

## Purpose

Tests for EEXIST (not EROFS) for inode creations, if we ask to create an already-existing entity on an RO filesystem NFS will optimize away the on-the-wire lookup before attempting to create a new file (since that means an extra round trip). It is registered with `_begin_fstest auto quick` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `294` plus `_begin_fstest auto quick`. Imported libraries: `. ./common/preamble`, `. ./common/filter`. Capability gates: `_require_scratch`, `_require_symlinks`, `_require_mknod`. Local functions: `_create_files`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 27: `THIS_TEST_DIR=$SCRATCH_MNT/$seq.test`
- Line 47: `status=0`

## Control Flow

Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 21: `_require_scratch`
- Line 25: `_scratch_mkfs > $seqres.full 2>&1 || _fail "Could not mkfs scratch device"`
- Line 31: `mknod $THIS_TEST_DIR/testnode c 1 3 2>&1 | _filter_mknod`
- Line 32: `mkdir $THIS_TEST_DIR/testdir`
- Line 33: `touch $THIS_TEST_DIR/testtarget`
- Line 34: `ln -s $THIS_TEST_DIR/testtarget $THIS_TEST_DIR/testlink 2>&1 | _filter_ln`
- Line 37: `_scratch_mount`
- Line 39: `rm -rf $THIS_TEST_DIR`
- Line 40: `mkdir $THIS_TEST_DIR || _fail "Could not create dir for test"`
- Line 42: `_create_files 2>&1 | _filter_scratch`
- Line 43: `_try_scratch_mount -o remount,ro || _fail "Could not remount scratch readonly"`
- Line 44: `_create_files 2>&1 | _filter_scratch`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, imports `. ./common/preamble`, `. ./common/filter`, and uses capability gates such as `_require_scratch`, `_require_symlinks`, `_require_mknod`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Symlink persistence tests are metadata-focused and can fail through lost directory updates, wrong target payloads, or fast/slow symlink representation differences.

## Test Signals

The pass signal is explicit `_fail` assertions. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/294 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/295 -->
# sources/test-tools/xfstests/tests/generic/295

## Purpose

Ensuring that copy on write in directio mode to the source file when the CoW range covers delalloc blocks and regular shared blocks - Create two files - Truncate the first file - Write the odd blocks of the first file - Reflink the odd blocks of the first file into the second file - Write the even blocks of the first file - DIO CoW the first file across the halfway mark, starting with the regular extent - Check that the files are now different where we say they're different. It is registered with `_begin_fstest auto quick clone prealloc` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `295` plus `_begin_fstest auto quick clone prealloc`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`. Capability gates: `_require_scratch_reflink`, `_require_scratch_delalloc`, `_require_xfs_io_command "falloc"`, `_require_odirect`, `_require_congruent_file_oplen $SCRATCH_MNT $blksz`. Local functions: none. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 34: `testdir=$SCRATCH_MNT/test-$seq`
- Line 38: `blksz=65536`
- Line 40: `nr=64`
- Line 41: `filesize=$((blksz * nr))`
- Line 51: `cowoff=$((filesize / 4))`
- Line 52: `cowsz=$((filesize / 2))`
- Line 64: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 30 `echo "Format and mount"`, line 37 `echo "Create the original files"`, line 45 `echo "Compare files"`, line 50 `echo "CoW across the transition"`. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 25: `_require_scratch_reflink`
- Line 26: `_require_scratch_delalloc`
- Line 27: `_require_xfs_io_command "falloc"`
- Line 30: `echo "Format and mount"`
- Line 31: `_scratch_mkfs > $seqres.full 2>&1`
- Line 32: `_scratch_mount >> $seqres.full 2>&1`
- Line 35: `mkdir $testdir`
- Line 42: `_sweave_reflink_holes $blksz $nr $testdir/file1 $testdir/file3 >> $seqres.full`
- Line 43: `_scratch_cycle_mount`
- Line 46: `md5sum $testdir/file1 | _filter_scratch`
- Line 47: `md5sum $testdir/file3 | _filter_scratch`
- Line 48: `md5sum $testdir/file1.chk | _filter_scratch`
- Line 53: `_sweave_reflink_holes_delalloc $blksz $nr $testdir/file1 >> $seqres.full`
- Line 61: `md5sum $testdir/file1.chk | _filter_scratch`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Cycle-mount calls force metadata and extent state through unmount/remount persistence before validation. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `clone`, `prealloc`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`, and uses capability gates such as `_require_scratch_reflink`, `_require_scratch_delalloc`, `_require_xfs_io_command "falloc"`, `_require_odirect`, `_require_congruent_file_oplen $SCRATCH_MNT $blksz`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Reflink coverage is sensitive to extent alignment, delayed allocation, unwritten extents, and page-size dependent block geometry, so comparisons against check files are the main correctness guard.
- Direct I/O paths can be affected by device sector size, alignment, cache invalidation, and filesystem-specific serialization between buffered and direct writes.

## Test Signals

The pass signal is filtered `md5sum` output. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/295 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/296 -->
# sources/test-tools/xfstests/tests/generic/296

## Purpose

- Create two reflinked files a byte longer than a block - Rewrite the whole file. It is registered with `_begin_fstest auto quick clone` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `296` plus `_begin_fstest auto quick clone`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`. Capability gates: `_require_scratch_reflink`, `_require_cp_reflink`, `_require_fs_space $SCRATCH_MNT $((filesize / 1024 * 3 * 5 / 4))`. Local functions: none. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 24: `testdir=$SCRATCH_MNT/test-$seq`
- Line 27: `blksz=65536`
- Line 28: `nr=128`
- Line 29: `filesize=$((blksz * nr))`
- Line 30: `bufnr=16`
- Line 31: `bufsize=$((blksz * bufnr))`
- Line 33: `real_blksz=$(_get_block_size "$testdir")`
- Line 58: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 20 `echo "Format and mount"`, line 36 `echo "Create the original files"`, line 42 `echo "Compare files"`, line 47 `echo "CoW and unmount"`. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 17: `_require_scratch_reflink`
- Line 18: `_require_cp_reflink`
- Line 20: `echo "Format and mount"`
- Line 21: `_scratch_mkfs > $seqres.full 2>&1`
- Line 22: `_scratch_mount >> $seqres.full 2>&1`
- Line 25: `mkdir $testdir`
- Line 37: `$XFS_IO_PROG -f -c "pwrite -S 0x61 -b $bufsize 0 $((filesize + 1))" $testdir/file1 >> $seqres.full`
- Line 38: `_cp_reflink $testdir/file1 $testdir/file2 >> $seqres.full`
- Line 39: `$XFS_IO_PROG -f -c "pwrite -S 0x61 -b $bufsize 0 $((filesize + 1))" $testdir/file2.chk >> $seqres.full`
- Line 40: `_scratch_cycle_mount`
- Line 43: `md5sum $testdir/file1 | _filter_scratch`
- Line 44: `md5sum $testdir/file2 | _filter_scratch`
- Line 45: `md5sum $testdir/file2.chk | _filter_scratch`
- Line 55: `md5sum $testdir/file2.chk | _filter_scratch`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Cycle-mount calls force metadata and extent state through unmount/remount persistence before validation. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `clone`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`, and uses capability gates such as `_require_scratch_reflink`, `_require_cp_reflink`, `_require_fs_space $SCRATCH_MNT $((filesize / 1024 * 3 * 5 / 4))`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Reflink coverage is sensitive to extent alignment, delayed allocation, unwritten extents, and page-size dependent block geometry, so comparisons against check files are the main correctness guard.

## Test Signals

The pass signal is filtered `md5sum` output. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/296 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/297 -->
# sources/test-tools/xfstests/tests/generic/297

## Purpose

See how well reflink handles ^C in the middle of a slow reflink. It is registered with `_begin_fstest auto clone` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `297` plus `_begin_fstest auto clone`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`, `. ./common/reflink`. Capability gates: `_require_scratch_reflink`, `_require_cp_reflink`, `_require_command "$TIMEOUT_PROG" "timeout"`. Local functions: `_cleanup`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 34: `testdir=$SCRATCH_MNT/test-$seq`
- Line 38: `blksz="$(_get_block_size $testdir)"`
- Line 41: `fnr=26 # 2^26 reflink extents should be enough to find a slow op?`
- Line 42: `timeout=8 # guarantee a good long run...`
- Line 46: `n=$(( (2 ** i) * blksz))`
- Line 50: `before=$(stat -c '%Y' $TEST_DIR/before)`
- Line 51: `after=$(stat -c '%Y' $TEST_DIR/after)`
- Line 52: `delta=$((after - before))`

## Control Flow

The visible phases are driven by echo markers such as line 30 `echo "Format and mount"`, line 37 `echo "Create a one block file"`, line 43 `echo "Find a reflink size that takes a long time"`, line 45 `echo " ++ Reflink size $i, $((2 ** i)) blocks" >> $seqres.full`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 16: `rm -rf $tmp.* $TEST_DIR/before $TEST_DIR/after`
- Line 24: `_require_scratch_reflink`
- Line 25: `_require_cp_reflink`
- Line 30: `echo "Format and mount"`
- Line 31: `_scratch_mkfs > $seqres.full 2>&1`
- Line 32: `_scratch_mount >> $seqres.full 2>&1`
- Line 35: `mkdir $testdir`
- Line 39: `_pwrite_byte 0x61 0 $blksz $testdir/file1 >> $seqres.full`
- Line 47: `touch $TEST_DIR/before`
- Line 48: `$XFS_IO_PROG -f -c "reflink $testdir/file1 0 $n $n" $testdir/file1 >> $seqres.full 2>&1`
- Line 49: `touch $TEST_DIR/after`
- Line 50: `before=$(stat -c '%Y' $TEST_DIR/before)`
- Line 51: `after=$(stat -c '%Y' $TEST_DIR/after)`
- Line 64: `after=$(stat -c '%Y' $TEST_DIR/after)`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. It may also use `$TEST_DIR` for non-destructive helper programs or limit checks. Temporary files are rooted at `$tmp.*` and removed by the local or default cleanup path. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `clone`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`, `. ./common/reflink`, and uses capability gates such as `_require_scratch_reflink`, `_require_cp_reflink`, `_require_command "$TIMEOUT_PROG" "timeout"`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Reflink coverage is sensitive to extent alignment, delayed allocation, unwritten extents, and page-size dependent block geometry, so comparisons against check files are the main correctness guard.
- Several checks can intentionally call `_notrun`; this is expected for unsupported geometry or feature combinations and should be distinguished from a failing assertion.

## Test Signals

The pass signal is stat/lstat metadata output, explicit `_fail` assertions. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/297 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/298 -->
# sources/test-tools/xfstests/tests/generic/298

## Purpose

See how well reflink handles SIGKILL in the middle of a slow reflink. It is registered with `_begin_fstest auto clone` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `298` plus `_begin_fstest auto clone`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`, `. ./common/reflink`. Capability gates: `_require_scratch_reflink`, `_require_cp_reflink`, `_require_command "$TIMEOUT_PROG" "timeout"`. Local functions: `_cleanup`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 34: `testdir=$SCRATCH_MNT/test-$seq`
- Line 38: `blksz="$(_get_block_size $testdir)"`
- Line 41: `fnr=26 # 2^26 reflink extents should be enough to find a slow op?`
- Line 42: `timeout=8 # guarantee a good long run...`
- Line 46: `n=$(( (2 ** i) * blksz))`
- Line 50: `before=$(stat -c '%Y' $TEST_DIR/before)`
- Line 51: `after=$(stat -c '%Y' $TEST_DIR/after)`
- Line 52: `delta=$((after - before))`

## Control Flow

The visible phases are driven by echo markers such as line 30 `echo "Format and mount"`, line 37 `echo "Create a one block file"`, line 43 `echo "Find a reflink size that takes a long time"`, line 45 `echo " ++ Reflink size $i, $((2 ** i)) blocks" >> $seqres.full`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 16: `rm -rf $tmp.* $TEST_DIR/before $TEST_DIR/after`
- Line 24: `_require_scratch_reflink`
- Line 25: `_require_cp_reflink`
- Line 30: `echo "Format and mount"`
- Line 31: `_scratch_mkfs > $seqres.full 2>&1`
- Line 32: `_scratch_mount >> $seqres.full 2>&1`
- Line 35: `mkdir $testdir`
- Line 39: `_pwrite_byte 0x61 0 $blksz $testdir/file1 >> $seqres.full`
- Line 47: `touch $TEST_DIR/before`
- Line 48: `$XFS_IO_PROG -f -c "reflink $testdir/file1 0 $n $n" $testdir/file1 >> $seqres.full 2>&1`
- Line 49: `touch $TEST_DIR/after`
- Line 50: `before=$(stat -c '%Y' $TEST_DIR/before)`
- Line 51: `after=$(stat -c '%Y' $TEST_DIR/after)`
- Line 64: `after=$(stat -c '%Y' $TEST_DIR/after)`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. It may also use `$TEST_DIR` for non-destructive helper programs or limit checks. Temporary files are rooted at `$tmp.*` and removed by the local or default cleanup path. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `clone`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`, `. ./common/reflink`, and uses capability gates such as `_require_scratch_reflink`, `_require_cp_reflink`, `_require_command "$TIMEOUT_PROG" "timeout"`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Reflink coverage is sensitive to extent alignment, delayed allocation, unwritten extents, and page-size dependent block geometry, so comparisons against check files are the main correctness guard.
- Several checks can intentionally call `_notrun`; this is expected for unsupported geometry or feature combinations and should be distinguished from a failing assertion.

## Test Signals

The pass signal is stat/lstat metadata output, explicit `_fail` assertions. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/298 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/299 -->
# sources/test-tools/xfstests/tests/generic/299

## Purpose

AIO/DIO stress test Run random AIO/DIO activity and fallocate/truncate simultaneously Test will operate on huge sparsed files so ENOSPC is expected. It is registered with `_begin_fstest auto aio enospc rw stress prealloc` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `299` plus `_begin_fstest auto aio enospc rw stress prealloc`. Imported libraries: `. ./common/preamble`, `. ./common/filter`. Capability gates: `_require_test`, `_require_scratch`, `_require_odirect`, `_require_aio`, `_require_block_device $SCRATCH_DEV`, `_require_xfs_io_command "falloc"`, `_require_fio $fio_config`. Local functions: none. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 14: `fio_config=$tmp.fio`
- Line 15: `fio_out=$tmp.fio.out`
- Line 27: `NUM_JOBS=$((4*LOAD_FACTOR))`
- Line 28: `BLK_DEV_SIZE=`blockdev --getsz $SCRATCH_DEV``
- Line 29: `FILE_SIZE=$((BLK_DEV_SIZE * 512))`
- Line 31: `max_file_size=$(_get_max_file_size $TEST_DIR)`
- Line 33: `FILE_SIZE=$max_file_size`
- Line 42: `ioengine=libaio`

## Control Flow

The visible phases are driven by echo markers such as line 102 `echo ""`, line 103 `echo "Run fio with random aio-dio pattern"`, line 104 `echo ""`, line 108 `echo "Start fallocate/truncate loop"`. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 14: `fio_config=$tmp.fio`
- Line 15: `fio_out=$tmp.fio.out`
- Line 20: `_require_test`
- Line 21: `_require_scratch`
- Line 25: `_require_xfs_io_command "falloc"`
- Line 36: `cat >$fio_config <<EOF`
- Line 52: `fallocate=none`
- Line 73: `verify_async=4`
- Line 88: `verify_async=4`
- Line 97: `_require_fio $fio_config`
- Line 99: `_scratch_mkfs >> $seqres.full 2>&1`
- Line 100: `_scratch_mount`
- Line 103: `echo "Run fio with random aio-dio pattern"`
- Line 124: `cat $fio_out >> $seqres.full`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. It may also use `$TEST_DIR` for non-destructive helper programs or limit checks. Temporary files are rooted at `$tmp.*` and removed by the local or default cleanup path. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `aio`, `enospc`, `rw`, `stress`, `prealloc`, imports `. ./common/preamble`, `. ./common/filter`, and uses capability gates such as `_require_test`, `_require_scratch`, `_require_odirect`, `_require_aio`, `_require_block_device $SCRATCH_DEV`, `_require_xfs_io_command "falloc"`, `_require_fio $fio_config`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Direct I/O paths can be affected by device sector size, alignment, cache invalidation, and filesystem-specific serialization between buffered and direct writes.
- Block-device fallocate tests rely on scsi_debug discard/write-same emulation and logical-sector alignment, not normal mounted filesystem behavior.
- ENOSPC cases are deliberately capacity-sensitive and can expose allocator, reservation, or delayed-allocation leaks only when scratch sizing and reserved blocks match the scenario.
- Stress tests are randomized or high-iteration workloads, so seeds, scaling helpers, timeouts, and captured stderr are important for reproducibility.

## Test Signals

The pass signal is stress-tool exit status and captured logs. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/299 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/300 -->
# sources/test-tools/xfstests/tests/generic/300

## Purpose

AIO/DIO stress test Run random AIO/DIO activity and fallocate/punch_hole simultaneously Test will operate on huge sparsed file so ENOSPC is expected xfs_io is not required for this test, but it's the best way to verify the test system supports fallocate() for allocation and hole punching. It is registered with `_begin_fstest auto aio enospc preallocrw stress punch` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `300` plus `_begin_fstest auto aio enospc preallocrw stress punch`. Imported libraries: `. ./common/preamble`, `. ./common/filter`. Capability gates: `_require_scratch`, `_require_odirect`, `_require_aio`, `_require_block_device $SCRATCH_DEV`, `_require_xfs_io_command "falloc"`, `_require_xfs_io_command "fpunch"`, `_require_fio $fio_config`. Local functions: none. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 14: `fio_config=$tmp.fio`
- Line 15: `fio_out=$tmp.fio.out`
- Line 30: `NUM_JOBS=$((4*LOAD_FACTOR))`
- Line 31: `BLK_DEV_SIZE=`blockdev --getsz $SCRATCH_DEV``
- Line 33: `BLK_DEV_SIZE=1048576`
- Line 35: `FS_SIZE=$((BLK_DEV_SIZE * 512))`
- Line 46: `directory=${SCRATCH_MNT}`
- Line 47: `filesize=${FS_SIZE}`

## Control Flow

The visible phases are driven by echo markers such as line 114 `echo ""`, line 115 `echo "Run fio with random aio-dio pattern"`, line 116 `echo ""`. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 14: `fio_config=$tmp.fio`
- Line 15: `fio_out=$tmp.fio.out`
- Line 20: `_require_scratch`
- Line 27: `_require_xfs_io_command "falloc"`
- Line 28: `_require_xfs_io_command "fpunch"`
- Line 37: `cat >$fio_config <<EOF`
- Line 54: `fallocate=none`
- Line 72: `[falloc_raicer]`
- Line 73: `ioengine=falloc`
- Line 82: `ioengine=falloc`
- Line 101: `verify_async=4`
- Line 109: `_require_fio $fio_config`
- Line 111: `_scratch_mkfs_sized $FS_SIZE >> $seqres.full 2>&1`
- Line 119: `cat $fio_out >> $seqres.full`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Temporary files are rooted at `$tmp.*` and removed by the local or default cleanup path. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `aio`, `enospc`, `preallocrw`, `stress`, `punch`, imports `. ./common/preamble`, `. ./common/filter`, and uses capability gates such as `_require_scratch`, `_require_odirect`, `_require_aio`, `_require_block_device $SCRATCH_DEV`, `_require_xfs_io_command "falloc"`, `_require_xfs_io_command "fpunch"`, `_require_fio $fio_config`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Direct I/O paths can be affected by device sector size, alignment, cache invalidation, and filesystem-specific serialization between buffered and direct writes.
- Block-device fallocate tests rely on scsi_debug discard/write-same emulation and logical-sector alignment, not normal mounted filesystem behavior.
- ENOSPC cases are deliberately capacity-sensitive and can expose allocator, reservation, or delayed-allocation leaks only when scratch sizing and reserved blocks match the scenario.
- Stress tests are randomized or high-iteration workloads, so seeds, scaling helpers, timeouts, and captured stderr are important for reproducibility.

## Test Signals

The pass signal is stress-tool exit status and captured logs. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/300 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/301 -->
# sources/test-tools/xfstests/tests/generic/301

## Purpose

Test fragmentation after a lot of random CoW: - Create two reflinked files - Buffered write to random offsets to scatter CoW reservations - Check the number of extents. It is registered with `_begin_fstest auto quick clone fiemap` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `301` plus `_begin_fstest auto quick clone fiemap`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`. Capability gates: `_require_scratch_reflink`, `_require_cp_reflink`, `_require_xfs_io_command "fiemap"`, `_require_fs_space $SCRATCH_MNT $((filesize / 1024 * 3 * 5 / 4))`. Local functions: none. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 27: `testdir=$SCRATCH_MNT/test-$seq`
- Line 30: `blksz=65536`
- Line 31: `nr=128`
- Line 32: `filesize=$((blksz * nr))`
- Line 33: `bufnr=16`
- Line 34: `bufsize=$((blksz * bufnr))`
- Line 37: `real_blksz=$(_get_block_size $testdir)`
- Line 38: `internal_blks=$((filesize / real_blksz))`

## Control Flow

The visible phases are driven by echo markers such as line 23 `echo "Format and mount"`, line 40 `echo "Create the original files"`, line 45 `echo "Compare files"`, line 49 `echo "CoW and unmount"`. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 13: `_begin_fstest auto quick clone fiemap`
- Line 19: `_require_scratch_reflink`
- Line 20: `_require_cp_reflink`
- Line 21: `_require_xfs_io_command "fiemap"`
- Line 23: `echo "Format and mount"`
- Line 24: `_scratch_mkfs > $seqres.full 2>&1`
- Line 25: `_scratch_mount >> $seqres.full 2>&1`
- Line 28: `mkdir $testdir`
- Line 41: `$XFS_IO_PROG -f -c "pwrite -S 0x61 -b $bufsize 0 $((filesize + 1))" $testdir/file1 >> $seqres.full`
- Line 42: `_cp_reflink $testdir/file1 $testdir/file2 >> $seqres.full`
- Line 43: `_scratch_cycle_mount`
- Line 46: `md5sum $testdir/file1 | _filter_scratch`
- Line 47: `md5sum $testdir/file2 | _filter_scratch`
- Line 56: `md5sum $testdir/file1 | _filter_scratch`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Cycle-mount calls force metadata and extent state through unmount/remount persistence before validation. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `clone`, `fiemap`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`, and uses capability gates such as `_require_scratch_reflink`, `_require_cp_reflink`, `_require_xfs_io_command "fiemap"`, `_require_fs_space $SCRATCH_MNT $((filesize / 1024 * 3 * 5 / 4))`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Reflink coverage is sensitive to extent alignment, delayed allocation, unwritten extents, and page-size dependent block geometry, so comparisons against check files are the main correctness guard.
- Extent-map output is formatted and filtered, but the test still depends on stable extent flags, logical block addressing, and filesystem support for the ioctl under test.

## Test Signals

The pass signal is filtered `md5sum` output, filtered extent-map output. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/301 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/302 -->
# sources/test-tools/xfstests/tests/generic/302

## Purpose

Test fragmentation after a lot of random CoW: - Create two reflinked files - Directio write to random offsets to scatter CoW reservations - Check the number of extents. It is registered with `_begin_fstest auto quick clone fiemap` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `302` plus `_begin_fstest auto quick clone fiemap`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`. Capability gates: `_require_scratch_reflink`, `_require_cp_reflink`, `_require_xfs_io_command "fiemap"`, `_require_odirect`, `_require_fs_space $SCRATCH_MNT $((filesize / 1024 * 3 * 5 / 4))`. Local functions: none. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 28: `testdir=$SCRATCH_MNT/test-$seq`
- Line 31: `blksz=65536`
- Line 32: `nr=128`
- Line 33: `filesize=$((blksz * nr))`
- Line 34: `bufnr=16`
- Line 35: `bufsize=$((blksz * bufnr))`
- Line 38: `real_blksz=$(_get_block_size $testdir)`
- Line 39: `internal_blks=$((filesize / real_blksz))`

## Control Flow

The visible phases are driven by echo markers such as line 24 `echo "Format and mount"`, line 41 `echo "Create the original files"`, line 46 `echo "Compare files"`, line 50 `echo "CoW and unmount"`. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 13: `_begin_fstest auto quick clone fiemap`
- Line 19: `_require_scratch_reflink`
- Line 20: `_require_cp_reflink`
- Line 21: `_require_xfs_io_command "fiemap"`
- Line 24: `echo "Format and mount"`
- Line 25: `_scratch_mkfs > $seqres.full 2>&1`
- Line 26: `_scratch_mount >> $seqres.full 2>&1`
- Line 29: `mkdir $testdir`
- Line 42: `$XFS_IO_PROG -f -c "pwrite -S 0x61 -b $bufsize 0 $((filesize + 1))" $testdir/file1 >> $seqres.full`
- Line 43: `_cp_reflink $testdir/file1 $testdir/file2 >> $seqres.full`
- Line 44: `_scratch_cycle_mount`
- Line 47: `md5sum $testdir/file1 | _filter_scratch`
- Line 48: `md5sum $testdir/file2 | _filter_scratch`
- Line 57: `md5sum $testdir/file1 | _filter_scratch`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Cycle-mount calls force metadata and extent state through unmount/remount persistence before validation. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `clone`, `fiemap`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`, and uses capability gates such as `_require_scratch_reflink`, `_require_cp_reflink`, `_require_xfs_io_command "fiemap"`, `_require_odirect`, `_require_fs_space $SCRATCH_MNT $((filesize / 1024 * 3 * 5 / 4))`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Reflink coverage is sensitive to extent alignment, delayed allocation, unwritten extents, and page-size dependent block geometry, so comparisons against check files are the main correctness guard.
- Direct I/O paths can be affected by device sector size, alignment, cache invalidation, and filesystem-specific serialization between buffered and direct writes.
- Extent-map output is formatted and filtered, but the test still depends on stable extent flags, logical block addressing, and filesystem support for the ioctl under test.

## Test Signals

The pass signal is filtered `md5sum` output, filtered extent-map output. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/302 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/303 -->
# sources/test-tools/xfstests/tests/generic/303

## Purpose

Check that high-offset reflinks work. It is registered with `_begin_fstest auto quick clone` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `303` plus `_begin_fstest auto quick clone`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`, `. ./common/reflink`. Capability gates: `_require_test_reflink`, `_require_cp_reflink`. Local functions: `_cleanup`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 28: `testdir=$TEST_DIR/test-$seq`
- Line 32: `bigoff=9223372036854775806`
- Line 33: `len=9223372036854775807`
- Line 34: `bigoff_64k=9223372036854710272 # bigoff rounded down to 64k`
- Line 73: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 27 `echo "Format and mount"`, line 31 `echo "Create the original files"`, line 40 `echo "Reflink large single byte file"`, line 43 `echo "Reflink large empty file"`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 16: `rm -rf $tmp.* $testdir`
- Line 24: `_require_test_reflink`
- Line 25: `_require_cp_reflink`
- Line 27: `echo "Format and mount"`
- Line 29: `mkdir $testdir`
- Line 35: `$XFS_IO_PROG -f -c "truncate $len" $testdir/file0 >> $seqres.full`
- Line 36: `test -s $testdir/file0 || _notrun "High offset ftruncate failed"`
- Line 37: `_pwrite_byte 0x61 $bigoff 1 $testdir/file1 >> $seqres.full`
- Line 38: `_pwrite_byte 0x61 1048575 1 $testdir/file2 >> $seqres.full`
- Line 41: `_cp_reflink $testdir/file1 $testdir/file3 >> $seqres.full`
- Line 44: `_cp_reflink $testdir/file0 $testdir/file4 >> $seqres.full`
- Line 47: `_reflink_range $testdir/file1 0 $testdir/file5 4611686018427322368 $len >> $seqres.full`
- Line 50: `_reflink_range $testdir/file1 $bigoff_64k $testdir/file6 1048576 65535 >> $seqres.full`
- Line 69: `$XFS_IO_PROG -c "pread -v -q 1114110 1" $testdir/file6`

## State and Persistence Behavior

Primary state lives under `$TEST_DIR`, making this a test-device workload rather than a scratch-device destructive test. Cycle-mount calls force metadata and extent state through unmount/remount persistence before validation. Temporary files are rooted at `$tmp.*` and removed by the local or default cleanup path. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `clone`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`, `. ./common/reflink`, and uses capability gates such as `_require_test_reflink`, `_require_cp_reflink`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Reflink coverage is sensitive to extent alignment, delayed allocation, unwritten extents, and page-size dependent block geometry, so comparisons against check files are the main correctness guard.
- Several checks can intentionally call `_notrun`; this is expected for unsupported geometry or feature combinations and should be distinguished from a failing assertion.

## Test Signals

The pass signal is silence from the helper program and final `status=0`. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/303 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/304 -->
# sources/test-tools/xfstests/tests/generic/304

## Purpose

Check that high-offset dedupes work. It is registered with `_begin_fstest auto quick clone dedupe` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `304` plus `_begin_fstest auto quick clone dedupe`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`, `. ./common/reflink`. Capability gates: `_require_test_dedupe`, `_require_cp_reflink`. Local functions: `_cleanup`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 28: `testdir=$TEST_DIR/test-$seq`
- Line 32: `bigoff=9223372036854775806`
- Line 33: `len=9223372036854775807`
- Line 34: `bigoff_64k=9223372036854710272 # bigoff rounded down to 64k`
- Line 81: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 27 `echo "Format and mount"`, line 31 `echo "Create the original files"`, line 41 `echo "Dedupe large single byte file"`, line 45 `echo "Dedupe large empty file"`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 16: `rm -rf $tmp.* $testdir`
- Line 25: `_require_cp_reflink`
- Line 29: `mkdir $testdir`
- Line 36: `test -s $testdir/file0 || _notrun "High offset ftruncate failed"`
- Line 38: `_pwrite_byte 0x61 $bigoff 1 $testdir/file3 >> $seqres.full`
- Line 42: `_dedupe_range $testdir/file1 $bigoff_64k $testdir/file3 $bigoff_64k 65536 \`
- Line 46: `_dedupe_range $testdir/file0 0 $testdir/file4 0 $len \`
- Line 50: `_dedupe_range $testdir/file1 0 $testdir/file5 4611686018427322368 $len \`
- Line 54: `_dedupe_range $testdir/file1 $bigoff_64k $testdir/file6 1048576 65535 \`
- Line 58: `_dedupe_range $testdir/file2 524288 $testdir/file7 0 1048576 \`
- Line 62: `_dedupe_range $testdir/file2 524288 $testdir/file8 0 $len \`
- Line 66: `_dedupe_range $testdir/file2 $bigoff_64k $testdir/file9 0 $bigoff_64k \`
- Line 70: `_test_cycle_mount`
- Line 77: `$XFS_IO_PROG -c "pread -v -q 1114110 1" $testdir/file6`

## State and Persistence Behavior

Primary state lives under `$TEST_DIR`, making this a test-device workload rather than a scratch-device destructive test. Cycle-mount calls force metadata and extent state through unmount/remount persistence before validation. Temporary files are rooted at `$tmp.*` and removed by the local or default cleanup path. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `clone`, `dedupe`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`, `. ./common/reflink`, and uses capability gates such as `_require_test_dedupe`, `_require_cp_reflink`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Reflink coverage is sensitive to extent alignment, delayed allocation, unwritten extents, and page-size dependent block geometry, so comparisons against check files are the main correctness guard.
- Several checks can intentionally call `_notrun`; this is expected for unsupported geometry or feature combinations and should be distinguished from a failing assertion.

## Test Signals

The pass signal is silence from the helper program and final `status=0`. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/304 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/305 -->
# sources/test-tools/xfstests/tests/generic/305

## Purpose

Ensure that quota charges us for reflinking a file and that we're not charged for buffered copy on write. It is registered with `_begin_fstest auto quick clone fiemap` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `305` plus `_begin_fstest auto quick clone fiemap`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`, `. ./common/quota`. Capability gates: `_require_scratch_reflink`, `_require_cp_reflink`, `_require_xfs_io_command "fiemap"`, `_require_quota`, `_require_nobody`, `_require_user`. Local functions: none. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 33: `testdir=$SCRATCH_MNT/test-$seq`
- Line 36: `sz=4194304`
- Line 67: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 25 `echo "Format and mount"`, line 37 `echo "Create the original files"`, line 48 `echo "Change file ownership"`, line 54 `echo "CoW one of the files"`. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 11: `_begin_fstest auto quick clone fiemap`
- Line 18: `_require_scratch_reflink`
- Line 20: `_require_xfs_io_command "fiemap"`
- Line 25: `echo "Format and mount"`
- Line 27: `export MOUNT_OPTIONS="-o usrquota,grpquota $MOUNT_OPTIONS"`
- Line 29: `_force_vfs_quota_testing $SCRATCH_MNT`
- Line 31: `quotaon $SCRATCH_MNT 2> /dev/null`
- Line 38: `$XFS_IO_PROG -f -c "pwrite -S 0x61 -b $sz 0 $sz" $testdir/file1 >> $seqres.full`
- Line 40: `_cp_reflink $testdir/file1 $testdir/file3 >> $seqres.full`
- Line 42: `chown nobody $testdir/urk`
- Line 44: `chown $qa_user $testdir/erk`
- Line 46: `_scratch_cycle_mount`
- Line 50: `chown $qa_user $testdir/file2`
- Line 64: `_report_quota_blocks $SCRATCH_MNT`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Cycle-mount calls force metadata and extent state through unmount/remount persistence before validation. Quota state is persistent filesystem metadata manipulated through `quotacheck`, `quotaon`, `setquota`, and `repquota` across user and group modes. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `clone`, `fiemap`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`, `. ./common/quota`, and uses capability gates such as `_require_scratch_reflink`, `_require_cp_reflink`, `_require_xfs_io_command "fiemap"`, `_require_quota`, `_require_nobody`, `_require_user`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Quota tests depend on kernel quota mode, grace-period timing, and the qa user/group setup; stale quota files or unsupported VFS quota behavior can turn a real failure into a notrun or noisy output mismatch.
- Reflink coverage is sensitive to extent alignment, delayed allocation, unwritten extents, and page-size dependent block geometry, so comparisons against check files are the main correctness guard.
- Extent-map output is formatted and filtered, but the test still depends on stable extent flags, logical block addressing, and filesystem support for the ioctl under test.

## Test Signals

The pass signal is filtered extent-map output. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/305 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/306 -->
# sources/test-tools/xfstests/tests/generic/306

## Purpose

Test RW open of a device on a RO fs Modify as appropriate. It is registered with `_begin_fstest auto quick rw` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `306` plus `_begin_fstest auto quick rw`. Imported libraries: `. ./common/preamble`, `. ./common/filter`. Capability gates: `_require_scratch`, `_require_test`, `_require_symlinks`, `_require_mknod`. Local functions: `_cleanup`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 30: `DEVNULL=$SCRATCH_MNT/devnull`
- Line 31: `DEVZERO=$SCRATCH_MNT/devzero`
- Line 32: `SYMLINK=$SCRATCH_MNT/symlink`
- Line 33: `BINDFILE=$SCRATCH_MNT/bindfile`
- Line 34: `TARGET=$TEST_DIR/target`
- Line 76: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 50 `echo "== try to create new file"`, line 52 `echo "== pwrite to null device"`, line 54 `echo "== pread from zero device"`, line 57 `echo "== truncating write to null device"`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 15: `_unmount $BINDFILE`
- Line 17: `rm -f $tmp.*`
- Line 25: `_require_scratch`
- Line 26: `_require_test`
- Line 36: `_scratch_mkfs > $seqres.full 2>&1`
- Line 37: `_scratch_mount`
- Line 39: `rm -f $DEVNULL $DEVZERO`
- Line 43: `touch $BINDFILE || _fail "Could not create bind mount file"`
- Line 44: `touch $TARGET || _fail "Could not create symlink target"`
- Line 45: `ln -s $TARGET $SYMLINK`
- Line 47: `_scratch_remount ro || _fail "Could not remount scratch readonly"`
- Line 51: `touch $SCRATCH_MNT/this_should_fail 2>&1 | _filter_scratch`
- Line 53: `$XFS_IO_PROG -c "pwrite 0 512" $DEVNULL | _filter_xfs_io`
- Line 73: `$XFS_IO_PROG -t -c "pwrite 0 512" $BINDFILE | _filter_xfs_io`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. It may also use `$TEST_DIR` for non-destructive helper programs or limit checks. Temporary files are rooted at `$tmp.*` and removed by the local or default cleanup path. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `rw`, imports `. ./common/preamble`, `. ./common/filter`, and uses capability gates such as `_require_scratch`, `_require_test`, `_require_symlinks`, `_require_mknod`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Symlink persistence tests are metadata-focused and can fail through lost directory updates, wrong target payloads, or fast/slow symlink representation differences.

## Test Signals

The pass signal is explicit `_fail` assertions. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/306 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/307 -->
# sources/test-tools/xfstests/tests/generic/307

## Purpose

Check if ctime is updated and written to disk after setfacl Regression test for the following extN commits c6ac12a ext4: update ctime when changing the file's permission by setfacl 30e2bab ext3: update ctime when changing the file's permission by setfacl 523825b ext2: update ctime when changing the file's permission by setfacl Based on test 277. It is registered with `_begin_fstest auto quick acl` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `307` plus `_begin_fstest auto quick acl`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`. Capability gates: `_require_scratch`, `_require_acls`. Local functions: `_cleanup`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 30: `testfile=$SCRATCH_MNT/testfile.$seq`
- Line 42: `ctime1=`stat -c %Z $testfile``
- Line 46: `ctime2=`stat -c %Z $testfile``
- Line 49: `ctime3=`stat -c %Z $testfile``
- Line 56: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 35 `echo "Silence is golden"`, line 52 `echo "error: ctime not updated after setfacl"`, line 54 `echo "error: on disk ctime not updated"`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 23: `rm -f $testfile`
- Line 32: `_require_scratch`
- Line 37: `_scratch_mkfs >/dev/null 2>&1`
- Line 38: `_scratch_mount >/dev/null 2>&1`
- Line 40: `touch $testfile`
- Line 41: `_scratch_cycle_mount`
- Line 42: `ctime1=`stat -c %Z $testfile``
- Line 46: `ctime2=`stat -c %Z $testfile``
- Line 48: `_scratch_cycle_mount`
- Line 49: `ctime3=`stat -c %Z $testfile``

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Cycle-mount calls force metadata and extent state through unmount/remount persistence before validation. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `acl`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`, and uses capability gates such as `_require_scratch`, `_require_acls`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- The main risk is environment drift: missing helper binaries, unsupported filesystem operations, or output formatting changes can make the test skip or fail without indicating a filesystem regression.

## Test Signals

The pass signal is stat/lstat metadata output. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/307 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/308 -->
# sources/test-tools/xfstests/tests/generic/308

## Purpose

Regression test for commit: f17722f ext4: Fix max file size and logical block counting of extent format file On unpatched ext4, if an extent exists which includes the block right before the maximum file offset, and the block for the maximum file offset is written, the kernel panics On patched ext4, the write would get EFBIG since we lower s_maxbytes by one fs block. It is registered with `_begin_fstest auto quick` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `308` plus `_begin_fstest auto quick`. Imported libraries: `. ./common/preamble`, `. ./common/filter`. Capability gates: `_require_test`. Local functions: `_cleanup`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 23: `testfile=$TEST_DIR/testfile.$seq`
- Line 29: `block_size=`_get_block_size $TEST_DIR``
- Line 38: `offset=$(((2**32 - 2) * $block_size))`
- Line 42: `offset=$(((2**32 - 1) * $block_size))`
- Line 46: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 27 `echo "Silence is golden"`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 17: `rm -f $testfile`
- Line 25: `_require_test`
- Line 39: `$XFS_IO_PROG -f -c "pwrite $offset $block_size" -c fsync $testfile >$seqres.full 2>&1`
- Line 43: `$XFS_IO_PROG -f -c "pwrite $offset $block_size" -c fsync $testfile >>$seqres.full 2>&1`

## State and Persistence Behavior

Primary state lives under `$TEST_DIR`, making this a test-device workload rather than a scratch-device destructive test. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, imports `. ./common/preamble`, `. ./common/filter`, and uses capability gates such as `_require_test`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- The main risk is environment drift: missing helper binaries, unsupported filesystem operations, or output formatting changes can make the test skip or fail without indicating a filesystem regression.

## Test Signals

The pass signal is silence from the helper program and final `status=0`. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/308 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/309 -->
# sources/test-tools/xfstests/tests/generic/309

## Purpose

Test directory mtime and ctime are updated when moving a file onto an existing file in the directory Regression test for commit: 0b23076 ext3: fix update of mtime and ctime on rename. It is registered with `_begin_fstest auto quick` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `309` plus `_begin_fstest auto quick`. Imported libraries: `. ./common/preamble`, `. ./common/filter`. Capability gates: `_require_test`. Local functions: `_cleanup`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 16: `status=0 # success is the default!`
- Line 37: `mtime1=`stat -c %Y $TEST_DIR/testdir_$seq``
- Line 38: `ctime1=`stat -c %Z $TEST_DIR/testdir_$seq``
- Line 43: `mtime2=`stat -c %Y $TEST_DIR/testdir_$seq``
- Line 44: `ctime2=`stat -c %Z $TEST_DIR/testdir_$seq``

## Control Flow

The visible phases are driven by echo markers such as line 31 `echo "Silence is golden"`, line 47 `echo "mtime not updated"`, line 51 `echo "ctime not updated"`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 22: `rm -rf $TEST_DIR/testdir_$seq`
- Line 23: `rm -f $TEST_DIR/testfile.$seq`
- Line 29: `_require_test`
- Line 33: `mkdir -p $TEST_DIR/testdir_$seq`
- Line 34: `touch $TEST_DIR/testdir_$seq/testfile`
- Line 35: `touch $TEST_DIR/testfile.$seq`
- Line 37: `mtime1=`stat -c %Y $TEST_DIR/testdir_$seq``
- Line 38: `ctime1=`stat -c %Z $TEST_DIR/testdir_$seq``
- Line 41: `mv $TEST_DIR/testfile.$seq $TEST_DIR/testdir_$seq/testfile`
- Line 43: `mtime2=`stat -c %Y $TEST_DIR/testdir_$seq``
- Line 44: `ctime2=`stat -c %Z $TEST_DIR/testdir_$seq``

## State and Persistence Behavior

Primary state lives under `$TEST_DIR`, making this a test-device workload rather than a scratch-device destructive test. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, imports `. ./common/preamble`, `. ./common/filter`, and uses capability gates such as `_require_test`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Direct I/O paths can be affected by device sector size, alignment, cache invalidation, and filesystem-specific serialization between buffered and direct writes.

## Test Signals

The pass signal is stat/lstat metadata output. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/309 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/310 -->
# sources/test-tools/xfstests/tests/generic/310

## Purpose

Check if there are two threads,one keeps calling read() or lseek(), and the other calling readdir(), both on the same directory fd Testing on ext3: with dir_index disabled results in the following dmesg output: (also occurs when testing ext2 and ext4) EXT3-fs error (device sdb): ext3_readdir: bad entry in directory #1134241: rec_len % 4 != 0 - offset=2704, inode=16973836, rec_len=12850, name_len=52 EXT3-fs error (device sdb): ext3_readdir: bad entry in directory #1134241: directory entry across blocks - offset=1672, inode=16973836, rec_len=14132, name_len=57 The filesystem mount option 'errors=' will define the behavior when an error is encountered. (see mount manpage) The test is based on a testcase from Li Zefan <lizefan@huawei.com> http://marc.info/?l=linux-kernel&m=136123703211869&w=2. It is registered with `_begin_fstest auto` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `310` plus `_begin_fstest auto`. Imported libraries: `. ./common/preamble`, `. ./common/filter`. Capability gates: `_require_test`. Local functions: `_cleanup`, `check_kernel_bug`, `_test_read`, `_test_lseek`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 45: `nr_bug=`dmesg | grep -c "kernel BUG"``
- Line 46: `nr_null=`dmesg | grep -c "kernel NULL pointer dereference"``
- Line 47: `nr_warning=`dmesg | grep -c "^WARNING"``
- Line 48: `nr_lockdep=`dmesg | grep -c "possible recursive locking detected"``
- Line 53: `new_bug=`dmesg | grep -c "kernel BUG"``
- Line 54: `new_null=`dmesg | grep -c "kernel NULL pointer dereference"``
- Line 55: `new_warning=`dmesg | grep -c "^WARNING"``
- Line 56: `new_lockdep=`dmesg | grep -c "possible recursive locking detected"``

## Control Flow

The visible phases are driven by echo markers such as line 113 `echo "*** done"`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 32: `_pkill -9 $seq.t_readdir > /dev/null 2>&1`
- Line 34: `rm -rf $TEST_DIR/tmp`
- Line 35: `rm -f $tmp.*`
- Line 41: `_require_test`
- Line 77: `mkdir -p $SEQ_DIR`
- Line 79: `touch $SEQ_DIR/$n`
- Line 82: `_test_read()`
- Line 86: `_pkill -PIPE $seq.t_readdir_1`
- Line 95: `_test_lseek()`
- Line 100: `_pkill -PIPE $seq.t_readdir_2`
- Line 109: `_test_read`
- Line 110: `_test_lseek`

## State and Persistence Behavior

Primary state lives under `$TEST_DIR`, making this a test-device workload rather than a scratch-device destructive test. Temporary files are rooted at `$tmp.*` and removed by the local or default cleanup path. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, imports `. ./common/preamble`, `. ./common/filter`, and uses capability gates such as `_require_test`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Direct I/O paths can be affected by device sector size, alignment, cache invalidation, and filesystem-specific serialization between buffered and direct writes.

## Test Signals

The pass signal is silence from the helper program and final `status=0`. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/310 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/311 -->
# sources/test-tools/xfstests/tests/generic/311

## Purpose

Run various fsync tests with dm flakey in freeze() mode and non freeze() mode. The idea is that we do random writes and randomly fsync and verify that after a fsync() followed by a freeze()+failure or just failure that the file is correct. We remount the file system after the failure so that the file system can do whatever cleanup it needs to and md5sum the file to make sure it matches hat it was before the failure. We also fsck to make sure the file system is consistent The fsync tester just random writes into prealloc or not, and then fsync()s randomly or sync()'s randomly and then fsync()'s before exit. There are a few tests that were handcrafted to reproduce bugs in btrfs, so it's also a regression test of sorts. It is registered with `_begin_fstest auto metadata log prealloc` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `311` plus `_begin_fstest auto metadata log prealloc`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/dmflakey`. Capability gates: `_require_scratch_nocheck`, `_require_odirect`, `_require_dm_target flakey`, `_require_xfs_io_command "falloc"`, `_require_test_program "fsync-tester"`, `_require_metadata_journaling $SCRATCH_DEV`. Local functions: `_cleanup`, `_run_test`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 43: `SEED=1`
- Line 44: `testfile=$SCRATCH_MNT/$seq.fsync`
- Line 49: `test_num=$1`
- Line 51: `direct_opt=""`
- Line 81: `buffered=0`
- Line 82: `direct=1`
- Line 85: `lockfs=1`
- Line 86: `SEED=$i`

## Control Flow

The visible phases are driven by echo markers such as line 87 `echo "Running test $i buffered, normal suspend"`, line 89 `echo "Running test $i direct, normal suspend"`, line 93 `echo "Running test $i buffered, nolockfs"`, line 95 `echo "Running test $i direct, nolockfs"`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 33: `_require_scratch_nocheck`
- Line 35: `_require_dm_target flakey`
- Line 39: `_require_xfs_io_command "falloc"`
- Line 41: `_require_test_program "fsync-tester"`
- Line 44: `testfile=$SCRATCH_MNT/$seq.fsync`
- Line 46: `_run_test()`
- Line 54: `$here/src/fsync-tester -s $SEED -t $test_num $direct_opt $testfile`
- Line 55: `[ $? -ne 0 ] && _fatal "fsync tester exited abnormally"`
- Line 59: `_scratch_unmount`
- Line 63: `_scratch_mount`
- Line 67: `_scratch_unmount`
- Line 68: `_check_scratch_fs`
- Line 71: `_scratch_mount`
- Line 96: `_run_test $i $direct`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. dm-flakey is used to simulate a dropped write / power-fail boundary and then remount for recovery checks. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `metadata`, `log`, `prealloc`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/dmflakey`, and uses capability gates such as `_require_scratch_nocheck`, `_require_odirect`, `_require_dm_target flakey`, `_require_xfs_io_command "falloc"`, `_require_test_program "fsync-tester"`, `_require_metadata_journaling $SCRATCH_DEV`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Direct I/O paths can be affected by device sector size, alignment, cache invalidation, and filesystem-specific serialization between buffered and direct writes.
- Crash-recovery tests require dm-flakey behavior and metadata journaling; failures can appear as lost directory entries, stale content, or mount-time recovery errors.

## Test Signals

The pass signal is filtered `md5sum` output. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/311 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/312 -->
# sources/test-tools/xfstests/tests/generic/312

## Purpose

ENOSPC in fallocate(2) could corrupt ext4 when file size > 4G Regression test for commit 29ae07b ext4: Fix overflow caused by missing cast in ext4_fallocate() 5G in byte fallocate(2) a 6G(> 4G) file on a 5G fs. It is registered with `_begin_fstest auto quick prealloc enospc` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `312` plus `_begin_fstest auto quick prealloc enospc`. Imported libraries: `. ./common/preamble`, `. ./common/filter`. Capability gates: `_require_xfs_io_command "falloc"`, `_require_scratch`. Local functions: none. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 22: `fssize=$((2**30 * 5))`
- Line 33: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 27 `echo "Silence is golden"`. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 18: `_require_xfs_io_command "falloc"`
- Line 19: `_require_scratch`
- Line 24: `_scratch_mkfs_sized $fssize >>$seqres.full 2>&1`
- Line 25: `_scratch_mount >>$seqres.full 2>&1`
- Line 30: `$XFS_IO_PROG -f -c "falloc 0 6g" $SCRATCH_MNT/testfile.$seq >>$seqres.full 2>&1`
- Line 32: `_scratch_unmount`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `prealloc`, `enospc`, imports `. ./common/preamble`, `. ./common/filter`, and uses capability gates such as `_require_xfs_io_command "falloc"`, `_require_scratch`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- ENOSPC cases are deliberately capacity-sensitive and can expose allocator, reservation, or delayed-allocation leaks only when scratch sizing and reserved blocks match the scenario.

## Test Signals

The pass signal is silence from the helper program and final `status=0`. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/312 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/313 -->
# sources/test-tools/xfstests/tests/generic/313

## Purpose

Check ctime and mtime are updated on truncate(2) and ftruncate(2) Regression test for commit: 3972f26 btrfs: update timestamps on truncate(). It is registered with `_begin_fstest auto quick` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `313` plus `_begin_fstest auto quick`. Imported libraries: `. ./common/preamble`, `. ./common/filter`. Capability gates: `_require_test`. Local functions: `_cleanup`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 27: `testfile=$TEST_DIR/testfile.$seq`
- Line 33: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 29 `echo "Silence is golden"`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 19: `rm -f $testfile`
- Line 25: `_require_test`
- Line 31: `$here/src/t_truncate_cmtime $testfile 2>&1`

## State and Persistence Behavior

Primary state lives under `$TEST_DIR`, making this a test-device workload rather than a scratch-device destructive test. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, imports `. ./common/preamble`, `. ./common/filter`, and uses capability gates such as `_require_test`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- The main risk is environment drift: missing helper binaries, unsupported filesystem operations, or output formatting changes can make the test skip or fail without indicating a filesystem regression.

## Test Signals

The pass signal is silence from the helper program and final `status=0`. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/313 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/314 -->
# sources/test-tools/xfstests/tests/generic/314

## Purpose

Test SGID inheritance on subdirectories Make dir owned by qa user, and an unrelated group: Make parent dir sgid Make subdir Subdir should have inherited sgid. It is registered with `_begin_fstest auto quick perms` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `314` plus `_begin_fstest auto quick perms`. Imported libraries: `. ./common/preamble`, `. ./common/filter`. Capability gates: `_require_test`, `_require_user`, `_require_chown`, `_require_sgid_inheritance`. Local functions: none. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 35: `status=0`

## Control Flow

The script runs linearly after the harness and requirement checks. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 15: `_require_test`
- Line 17: `_require_chown`
- Line 20: `rm -rf $TEST_DIR/$seq-dir`
- Line 23: `mkdir $TEST_DIR/$seq-dir`
- Line 24: `chown $qa_user:12345 $TEST_DIR/$seq-dir`
- Line 27: `chmod 2775 $TEST_DIR/$seq-dir`
- Line 30: `_su $qa_user -c "umask 022; mkdir $TEST_DIR/$seq-dir/subdir"`
- Line 33: `_ls_l $TEST_DIR/$seq-dir/ | grep -v total | _filter_test_dir | awk '{print $1,$NF}'`

## State and Persistence Behavior

Primary state lives under `$TEST_DIR`, making this a test-device workload rather than a scratch-device destructive test. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `perms`, imports `. ./common/preamble`, `. ./common/filter`, and uses capability gates such as `_require_test`, `_require_user`, `_require_chown`, `_require_sgid_inheritance`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Direct I/O paths can be affected by device sector size, alignment, cache invalidation, and filesystem-specific serialization between buffered and direct writes.

## Test Signals

The pass signal is silence from the helper program and final `status=0`. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/314 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/315 -->
# sources/test-tools/xfstests/tests/generic/315

## Purpose

fallocate/truncate tests with FALLOC_FL_KEEP_SIZE option Verify if the disk space is released after truncating a file back to the old smaller size. Before Linux 3.10, Btrfs/OCFS2 are test failed in this case Modify as appropriate Check the current avaliable disk space on $TEST_DIR 1024KiB at least Preallocate half size of the available disk space to a file starts from offset 0 with FALLOC_FL_KEEP_SIZE option on the test file system. It is registered with `_begin_fstest auto quick rw prealloc` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `315` plus `_begin_fstest auto quick rw prealloc`. Imported libraries: `. ./common/preamble`, `. ./common/filter`. Capability gates: `_require_test`, `_require_xfs_io_command "falloc" "-k"`. Local functions: none. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 15: `status=0 # success is the default!`
- Line 29: `avail_begin=`df -P $TEST_DIR | awk 'END {print $4}'``
- Line 39: `fsize=`_get_filesize $TEST_DIR/testfile.$seq``
- Line 47: `avail_done=`df -P $TEST_DIR | awk 'END {print $4}'``

## Control Flow

The visible phases are driven by echo markers such as line 25 `echo "Slience is golden"`. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 22: `_require_test`
- Line 23: `_require_xfs_io_command "falloc" "-k"`
- Line 29: `avail_begin=`df -P $TEST_DIR | awk 'END {print $4}'``
- Line 35: `$XFS_IO_PROG -f -c 'falloc -k 0 $(($avail_begin/2))' \`
- Line 43: `truncate -s 0 $TEST_DIR/testfile.$seq`
- Line 44: `_test_sync`
- Line 47: `avail_done=`df -P $TEST_DIR | awk 'END {print $4}'``

## State and Persistence Behavior

Primary state lives under `$TEST_DIR`, making this a test-device workload rather than a scratch-device destructive test. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `rw`, `prealloc`, imports `. ./common/preamble`, `. ./common/filter`, and uses capability gates such as `_require_test`, `_require_xfs_io_command "falloc" "-k"`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Thin-provisioning tests depend on device-mapper target behavior, pool exhaustion semantics, and correct cleanup of temporary block devices.
- Several checks can intentionally call `_notrun`; this is expected for unsupported geometry or feature combinations and should be distinguished from a failing assertion.

## Test Signals

The pass signal is explicit `_fail` assertions. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/315 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/316 -->
# sources/test-tools/xfstests/tests/generic/316

## Purpose

Test Generic fallocate hole punching w/o unwritten extent Standard punch hole tests Delayed allocation punch hole tests Multi hole punch tests Delayed allocation multi punch hole tests success, all done. It is registered with `_begin_fstest auto quick punch fiemap` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `316` plus `_begin_fstest auto quick punch fiemap`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/punch`. Capability gates: `_require_test`, `_require_xfs_io_command "fpunch"`, `_require_xfs_io_command "fiemap"`. Local functions: none. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 21: `testfile=$TEST_DIR/$seq.$$`
- Line 36: `status=0`

## Control Flow

The script runs linearly after the harness and requirement checks. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 10: `_begin_fstest auto quick punch fiemap`
- Line 17: `_require_test`
- Line 18: `_require_xfs_io_command "fpunch"`
- Line 19: `_require_xfs_io_command "fiemap"`
- Line 24: `_test_generic_punch -u pwrite fpunch fpunch fiemap _filter_hole_fiemap $testfile`
- Line 27: `_test_generic_punch -u -d pwrite fpunch fpunch fiemap _filter_hole_fiemap $testfile`
- Line 30: `_test_generic_punch -u -k pwrite fpunch fpunch fiemap _filter_hole_fiemap $testfile`
- Line 33: `_test_generic_punch -u -d -k pwrite fpunch fpunch fiemap _filter_hole_fiemap $testfile`

## State and Persistence Behavior

Primary state lives under `$TEST_DIR`, making this a test-device workload rather than a scratch-device destructive test. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `punch`, `fiemap`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/punch`, and uses capability gates such as `_require_test`, `_require_xfs_io_command "fpunch"`, `_require_xfs_io_command "fiemap"`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Direct I/O paths can be affected by device sector size, alignment, cache invalidation, and filesystem-specific serialization between buffered and direct writes.
- Extent-map output is formatted and filtered, but the test still depends on stable extent flags, logical block addressing, and filesystem support for the ioctl under test.

## Test Signals

The pass signal is filtered extent-map output. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/316 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/317 -->
# sources/test-tools/xfstests/tests/generic/317

## Purpose

Check uid/gid to/from disk with a user namespace. A new file will be created from inside a userns. We check that the uid/gid is correct from both inside the userns and also from init_user_ns We will then unmount and remount the file system and check the uid/gid from both inside the userns and from init_user_ns to show that the correct uid was flushed and brought back from disk only Linux supports user namespace. It is registered with `_begin_fstest auto metadata quick` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `317` plus `_begin_fstest auto metadata quick`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`. Capability gates: `_require_scratch`, `_require_user`, `_require_ugid_map`, `_require_userns`, `_require_chown`, `_require_use_local_uidgid`. Local functions: `_cleanup`, `_filter_output`, `_print_numeric_uid`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 28: `file=$SCRATCH_MNT/file1`
- Line 40: `qa_user_id=`id -u $qa_user``
- Line 82: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 51 `echo "From init_user_ns"`, line 54 `echo "From user_ns"`, line 62 `echo "*** MKFS ***" >>$seqres.full`, line 63 `echo "" >>$seqres.full`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 21: `_scratch_unmount >/dev/null 2>&1`
- Line 34: `_require_scratch`
- Line 38: `_require_chown`
- Line 42: `_filter_output()`
- Line 52: `$here/src/lstat64 $file |head -3 |_filter_output`
- Line 58: `$here/src/nsexec -s -U -M "0 $qa_user_id 1000" -G "0 $qa_user_id 1000" src/lstat64 $file |head -3 |_filter_output`
- Line 61: `_scratch_unmount >/dev/null 2>&1`
- Line 64: `_scratch_mkfs >>$seqres.full 2>&1 || _fail "mkfs failed"`
- Line 65: `_scratch_mount`
- Line 66: `chmod 777 $SCRATCH_MNT`
- Line 69: `$here/src/nsexec -s -U -M "0 $qa_user_id 1000" -G "0 $qa_user_id 1000" touch $file`
- Line 74: `echo "*** Remounting ***"`
- Line 76: `_scratch_sync`
- Line 81: `_scratch_unmount >/dev/null 2>&1`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Cycle-mount calls force metadata and extent state through unmount/remount persistence before validation. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `metadata`, `quick`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`, and uses capability gates such as `_require_scratch`, `_require_user`, `_require_ugid_map`, `_require_userns`, `_require_chown`, `_require_use_local_uidgid`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- The main risk is environment drift: missing helper binaries, unsupported filesystem operations, or output formatting changes can make the test skip or fail without indicating a filesystem regression.
- Several checks can intentionally call `_notrun`; this is expected for unsupported geometry or feature combinations and should be distinguished from a failing assertion.

## Test Signals

The pass signal is stat/lstat metadata output, explicit `_fail` assertions. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/317 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/318 -->
# sources/test-tools/xfstests/tests/generic/318

## Purpose

Check get/set ACLs to/from disk with a user namespace. A new file will be created and ACLs set on it from both inside a userns and from init_user_ns. We check that the ACL is is correct from both inside the userns and also from init_user_ns. We will then unmount and remount the file system and check the ACL from both inside the userns and from init_user_ns to show that the correct uid/gid in the ACL was flushed and brought back from disk only Linux supports user namespace. It is registered with `_begin_fstest acl attr auto quick perms` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `318` plus `_begin_fstest acl attr auto quick perms`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`. Capability gates: `_require_scratch`, `_require_acls`, `_require_ugid_map`, `_require_userns`. Local functions: `_cleanup`, `_getfacl_filter_nsid`, `_print_getfacls`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 29: `nsexec=$here/src/nsexec`
- Line 30: `file=$SCRATCH_MNT/file1`
- Line 39: `ns_acl1=0`
- Line 40: `ns_acl2=`expr $acl2 - $acl1``
- Line 41: `ns_acl3=`expr $acl3 - $acl1``
- Line 90: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 59 `echo "From init_user_ns"`, line 62 `echo "From user_ns"`, line 67 `echo "*** MKFS ***" >>$seqres.full`, line 68 `echo "" >>$seqres.full`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 22: `_scratch_unmount >/dev/null 2>&1`
- Line 34: `_require_scratch`
- Line 43: `_getfacl_filter_nsid()`
- Line 60: `getfacl --absolute-names -n $file 2>/dev/null | _filter_scratch | _getfacl_filter_id`
- Line 63: `$nsexec -U -M "0 $acl1 1000" -G "0 $acl1 1000" getfacl --absolute-names -n $file 2>/dev/null | _filter_scratch | _getfacl_filter_nsid`
- Line 66: `_scratch_unmount >/dev/null 2>&1`
- Line 69: `_scratch_mkfs >>$seqres.full 2>&1 || _fail "mkfs failed"`
- Line 70: `_scratch_mount`
- Line 72: `touch $file`
- Line 73: `chown $acl1:$acl1 $file`
- Line 82: `echo "*** Remounting ***"`
- Line 84: `_scratch_sync`
- Line 85: `_scratch_cycle_mount >>$seqres.full 2>&1 || _fail "remount failed"`
- Line 89: `_scratch_unmount >/dev/null 2>&1`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Cycle-mount calls force metadata and extent state through unmount/remount persistence before validation. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `acl`, `attr`, `auto`, `quick`, `perms`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`, and uses capability gates such as `_require_scratch`, `_require_acls`, `_require_ugid_map`, `_require_userns`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- The main risk is environment drift: missing helper binaries, unsupported filesystem operations, or output formatting changes can make the test skip or fail without indicating a filesystem regression.

## Test Signals

The pass signal is explicit `_fail` assertions. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/318 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/319 -->
# sources/test-tools/xfstests/tests/generic/319

## Purpose

Regression test to make sure a directory inherits the default ACL from its parent directory. This test was motivated by an issue reported by a btrfs user. That issue is fixed and described by the following btrfs kernel patch: https://patchwork.kernel.org/patch/3046931/ success, all done. It is registered with `_begin_fstest acl auto quick perms` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `319` plus `_begin_fstest acl auto quick perms`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`. Capability gates: `_require_acls`, `_require_scratch`. Local functions: none. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 35: `status=0`

## Control Flow

The script runs linearly after the harness and requirement checks. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 22: `_require_scratch`
- Line 24: `_scratch_mkfs > /dev/null 2>&1`
- Line 25: `_scratch_mount`
- Line 27: `mkdir $SCRATCH_MNT/testdir`
- Line 29: `getfacl -n --absolute-names $SCRATCH_MNT/testdir | _filter_scratch`
- Line 31: `mkdir $SCRATCH_MNT/testdir/testsubdir`
- Line 32: `getfacl -n --absolute-names $SCRATCH_MNT/testdir/testsubdir | _filter_scratch`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `acl`, `auto`, `quick`, `perms`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`, and uses capability gates such as `_require_acls`, `_require_scratch`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Direct I/O paths can be affected by device sector size, alignment, cache invalidation, and filesystem-specific serialization between buffered and direct writes.

## Test Signals

The pass signal is silence from the helper program and final `status=0`. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/319 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/320 -->
# sources/test-tools/xfstests/tests/generic/320

## Purpose

heavy rm workload Regression test for commit: 9a3a5da xfs: check for stale inode before acquiring iflock on push Based on generic/273. It is registered with `_begin_fstest auto rw` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `320` plus `_begin_fstest auto rw`. Imported libraries: `. ./common/preamble`, `. ./common/filter`. Capability gates: `_require_scratch`. Local functions: `threads_set`, `file_create`, `worker`, `do_workload`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 23: `threads=100`
- Line 24: `count=2`
- Line 25: `fs_size=$((2 * 1024 * 1024 * 1024))`
- Line 26: `ORIGIN=$SCRATCH_MNT/origin`
- Line 30: `threads=$((LOAD_FACTOR * 100))`
- Line 33: `threads=200`
- Line 39: `i=0`
- Line 42: `disksize=$(($fs_size / 3))`

## Control Flow

The visible phases are driven by echo markers such as line 78 `echo "Silence is golden"`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 21: `_require_scratch`
- Line 40: `mkdir $ORIGIN`
- Line 45: `$XFS_IO_PROG -f -c "pwrite 0 $((4096*count))" \`
- Line 55: `mkdir $SCRATCH_MNT/sub_$suffix`
- Line 58: `rm -rf $SCRATCH_MNT/sub_$suffix`
- Line 80: `_scratch_mkfs_sized $fs_size >>$seqres.full 2>&1`
- Line 81: `_scratch_mount >>$seqres.full 2>&1`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `rw`, imports `. ./common/preamble`, `. ./common/filter`, and uses capability gates such as `_require_scratch`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- The main risk is environment drift: missing helper binaries, unsupported filesystem operations, or output formatting changes can make the test skip or fail without indicating a filesystem regression.

## Test Signals

The pass signal is silence from the helper program and final `status=0`. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/320 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/321 -->
# sources/test-tools/xfstests/tests/generic/321

## Purpose

Runs various dir fsync tests to cover fsync'ing directory corner cases Btrfs wasn't making sure the directory survived fsync. It is registered with `_begin_fstest auto quick metadata log` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `321` plus `_begin_fstest auto quick metadata log`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/dmflakey`. Capability gates: `_require_scratch_nocheck`, `_require_dm_target flakey`, `_require_metadata_journaling $SCRATCH_DEV`. Local functions: `_cleanup`, `_clean_working_dir`, `_directory_test`, `_rename_test`, `_replay_rename_test`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 108: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 37 `echo "fsync new directory"`, line 53 `echo "rename fsync test"`, line 75 `echo "replay rename fsync test"`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 17: `rm -f $tmp.*`
- Line 29: `_scratch_mount`
- Line 35: `_directory_test()`
- Line 39: `mkdir $SCRATCH_MNT/bar`
- Line 45: `_scratch_unmount`
- Line 53: `echo "rename fsync test"`
- Line 56: `mkdir $SCRATCH_MNT/bar`
- Line 59: `$XFS_IO_PROG -c "fsync" $SCRATCH_MNT/bar`
- Line 66: `_scratch_unmount`
- Line 75: `echo "replay rename fsync test"`
- Line 78: `mkdir $SCRATCH_MNT/bar`
- Line 81: `$XFS_IO_PROG -c "fsync" $SCRATCH_MNT/bar`
- Line 89: `_flakey_drop_and_remount`
- Line 106: `_replay_rename_test`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. dm-flakey is used to simulate a dropped write / power-fail boundary and then remount for recovery checks. Temporary files are rooted at `$tmp.*` and removed by the local or default cleanup path. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `metadata`, `log`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/dmflakey`, and uses capability gates such as `_require_scratch_nocheck`, `_require_dm_target flakey`, `_require_metadata_journaling $SCRATCH_DEV`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Direct I/O paths can be affected by device sector size, alignment, cache invalidation, and filesystem-specific serialization between buffered and direct writes.
- Crash-recovery tests require dm-flakey behavior and metadata journaling; failures can appear as lost directory entries, stale content, or mount-time recovery errors.

## Test Signals

The pass signal is silence from the helper program and final `status=0`. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/321 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/322 -->
# sources/test-tools/xfstests/tests/generic/322

## Purpose

Runs various rename fsync tests to cover some rename fsync corner cases Btrfs wasn't making sure the new file after rename survived the fsync. It is registered with `_begin_fstest auto quick metadata log` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `322` plus `_begin_fstest auto quick metadata log`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/dmflakey`. Capability gates: `_require_scratch_nocheck`, `_require_dm_target flakey`, `_require_metadata_journaling $SCRATCH_DEV`. Local functions: `_cleanup`, `_clean_working_dir`, `_rename_test`, `_write_after_fsync_rename_test`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 79: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 35 `echo "fsync rename test"`, line 55 `echo "fsync rename test"`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 22: `_require_scratch_nocheck`
- Line 27: `_scratch_mount`
- Line 29: `_scratch_unmount`
- Line 35: `echo "fsync rename test"`
- Line 37: `$XFS_IO_PROG -f -c "pwrite 0 1M" -c "fsync" $SCRATCH_MNT/foo \`
- Line 40: `$XFS_IO_PROG -c "fsync" $SCRATCH_MNT/bar`
- Line 43: `_flakey_drop_and_remount`
- Line 46: `_scratch_unmount`
- Line 53: `_write_after_fsync_rename_test()`
- Line 56: `_scratch_mount`
- Line 58: `-c "sync_range -b 2M 1M" $SCRATCH_MNT/foo >> $seqres.full 2>&1`
- Line 60: `$XFS_IO_PROG -c "fsync" $SCRATCH_MNT/bar`
- Line 63: `_flakey_drop_and_remount`
- Line 77: `_write_after_fsync_rename_test`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. dm-flakey is used to simulate a dropped write / power-fail boundary and then remount for recovery checks. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `metadata`, `log`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/dmflakey`, and uses capability gates such as `_require_scratch_nocheck`, `_require_dm_target flakey`, `_require_metadata_journaling $SCRATCH_DEV`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Crash-recovery tests require dm-flakey behavior and metadata journaling; failures can appear as lost directory entries, stale content, or mount-time recovery errors.

## Test Signals

The pass signal is filtered `md5sum` output. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/322 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/323 -->
# sources/test-tools/xfstests/tests/generic/323

## Purpose

Run aio-last-ref-held-by-io - last put of ioctx not in process context. We've had a couple of instances in the past where having the last reference to an ioctx be held by the IO (instead of the process) would cause problems (hung system, crashes) This can emit cpu affinity setting failures that aren't considered test failures but cause golden image failures. Redirect the test output to $seqres.full so that it is captured but doesn't directly cause test failures. It is registered with `_begin_fstest auto aio stress` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `323` plus `_begin_fstest auto aio stress`. Imported libraries: `. ./common/preamble`, `. ./common/filter`. Capability gates: `_require_test`, `_require_aiodio aio-last-ref-held-by-io`. Local functions: none. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 23: `testfile=$TEST_DIR/aio-testfile`
- Line 39: `status=0`

## Control Flow

The script runs linearly after the harness and requirement checks. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 19: `_require_test`
- Line 24: `$XFS_IO_PROG -ftc "pwrite 0 10m" $testfile | _filter_xfs_io`

## State and Persistence Behavior

Primary state lives under `$TEST_DIR`, making this a test-device workload rather than a scratch-device destructive test. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `aio`, `stress`, imports `. ./common/preamble`, `. ./common/filter`, and uses capability gates such as `_require_test`, `_require_aiodio aio-last-ref-held-by-io`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Direct I/O paths can be affected by device sector size, alignment, cache invalidation, and filesystem-specific serialization between buffered and direct writes.
- Stress tests are randomized or high-iteration workloads, so seeds, scaling helpers, timeouts, and captured stderr are important for reproducibility.

## Test Signals

The pass signal is silence from the helper program and final `status=0`. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/323 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/324 -->
# sources/test-tools/xfstests/tests/generic/324

## Purpose

Sanity check for defrag utility. It is registered with `_begin_fstest auto fsr quick defrag prealloc` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `324` plus `_begin_fstest auto fsr quick defrag prealloc`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/defrag`. Capability gates: `_require_scratch`, `_require_defrag`, `_require_xfs_io_command "falloc"`. Local functions: `_workout`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 12: `PIDS=""`
- Line 24: `nr=$1`
- Line 38: `patt=`printf "0x%x" $i``
- Line 52: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 25 `echo "Defragment file with $nr * 2 fragments"`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 18: `_require_scratch`
- Line 20: `_require_xfs_io_command "falloc"`
- Line 29: `$XFS_IO_PROG -f -c "falloc $((409600*i)) 4k" \`
- Line 33: `$XFS_IO_PROG -c "falloc 0 $((204800*nr))" \`
- Line 34: `$SCRATCH_MNT/test.$nr | _filter_xfs_io`
- Line 39: `$XFS_IO_PROG -c "pwrite -S $patt $((i*123400)) 1234" \`
- Line 40: `$SCRATCH_MNT/test.$nr | _filter_xfs_io`
- Line 47: `_scratch_mkfs >> $seqres.full 2>&1`
- Line 48: `_scratch_mount`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `fsr`, `quick`, `defrag`, `prealloc`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/defrag`, and uses capability gates such as `_require_scratch`, `_require_defrag`, `_require_xfs_io_command "falloc"`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- The main risk is environment drift: missing helper binaries, unsupported filesystem operations, or output formatting changes can make the test skip or fail without indicating a filesystem regression.

## Test Signals

The pass signal is silence from the helper program and final `status=0`. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/324 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/325 -->
# sources/test-tools/xfstests/tests/generic/325

## Purpose

Make some pages/extents of a file dirty, do a ranged fsync that covers only some of the dirty pages/extents, and then do a regular fsync (or another ranged fsync that covers the remaining dirty pages/extents) Verify after that all extents were persisted This test is motivated by a btrfs issue where the first ranged fsync would prevent the following fsync from persisting the remaining dirty pages/extents. This was fixed by the following btrfs kernel patch: Btrfs: fix fsync data loss after a ranged fsync. It is registered with `_begin_fstest auto quick data log mmap` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `325` plus `_begin_fstest auto quick data log mmap`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/dmflakey`. Capability gates: `_require_scratch`, `_require_dm_target flakey`, `_require_metadata_journaling $SCRATCH_DEV`. Local functions: `_cleanup`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 74: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 64 `echo "File content before crash/reboot:"`, line 69 `echo "File content after crash/reboot and fs mount:"`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 19: `_begin_fstest auto quick data log mmap`
- Line 31: `_require_scratch`
- Line 32: `_require_dm_target flakey`
- Line 34: `_scratch_mkfs >> $seqres.full 2>&1`
- Line 37: `_scratch_mount`
- Line 40: `$XFS_IO_PROG -f -c "pwrite -S 0xff 0 256K" $SCRATCH_MNT/foo | _filter_xfs_io`
- Line 45: `_scratch_sync`
- Line 55: `$XFS_IO_PROG \`
- Line 56: `-c "mmap -w 0 256K" \`
- Line 57: `-c "mwrite -S 0xaa 0 4K" \`
- Line 58: `-c "mwrite -S 0xbb 252K 4K" \`
- Line 59: `-c "msync -s 0K 64K" \`
- Line 60: `-c "msync -s 192K 64K" \`
- Line 72: `_scratch_unmount`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. dm-flakey is used to simulate a dropped write / power-fail boundary and then remount for recovery checks. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `data`, `log`, `mmap`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/dmflakey`, and uses capability gates such as `_require_scratch`, `_require_dm_target flakey`, `_require_metadata_journaling $SCRATCH_DEV`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- mmap tests rely on page-cache writeback, timestamp granularity, and correct handling of dirty mappings across fsync, sync, or remount boundaries.
- Crash-recovery tests require dm-flakey behavior and metadata journaling; failures can appear as lost directory entries, stale content, or mount-time recovery errors.

## Test Signals

The pass signal is silence from the helper program and final `status=0`. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/325 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/326 -->
# sources/test-tools/xfstests/tests/generic/326

## Purpose

Ensure that quota charges us for reflinking a file and that we're not charged for directio copy on write. It is registered with `_begin_fstest auto quick clone fiemap` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `326` plus `_begin_fstest auto quick clone fiemap`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`, `. ./common/quota`. Capability gates: `_require_scratch_reflink`, `_require_cp_reflink`, `_require_xfs_io_command "fiemap"`, `_require_quota`, `_require_nobody`, `_require_odirect`, `_require_user`. Local functions: none. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 34: `testdir=$SCRATCH_MNT/test-$seq`
- Line 37: `sz=4194304`
- Line 68: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 26 `echo "Format and mount"`, line 38 `echo "Create the original files"`, line 49 `echo "Change file ownership"`, line 55 `echo "CoW one of the files"`. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 11: `_begin_fstest auto quick clone fiemap`
- Line 18: `_require_scratch_reflink`
- Line 20: `_require_xfs_io_command "fiemap"`
- Line 26: `echo "Format and mount"`
- Line 28: `export MOUNT_OPTIONS="-o usrquota,grpquota $MOUNT_OPTIONS"`
- Line 30: `_force_vfs_quota_testing $SCRATCH_MNT`
- Line 32: `quotaon $SCRATCH_MNT 2> /dev/null`
- Line 39: `$XFS_IO_PROG -f -c "pwrite -S 0x61 -b $sz 0 $sz" $testdir/file1 >> $seqres.full`
- Line 41: `_cp_reflink $testdir/file1 $testdir/file3 >> $seqres.full`
- Line 43: `chown nobody $testdir/urk`
- Line 45: `chown $qa_user $testdir/erk`
- Line 47: `_scratch_cycle_mount`
- Line 51: `chown $qa_user $testdir/file2`
- Line 65: `_report_quota_blocks $SCRATCH_MNT`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Cycle-mount calls force metadata and extent state through unmount/remount persistence before validation. Quota state is persistent filesystem metadata manipulated through `quotacheck`, `quotaon`, `setquota`, and `repquota` across user and group modes. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `clone`, `fiemap`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`, `. ./common/quota`, and uses capability gates such as `_require_scratch_reflink`, `_require_cp_reflink`, `_require_xfs_io_command "fiemap"`, `_require_quota`, `_require_nobody`, `_require_odirect`, `_require_user`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Quota tests depend on kernel quota mode, grace-period timing, and the qa user/group setup; stale quota files or unsupported VFS quota behavior can turn a real failure into a notrun or noisy output mismatch.
- Reflink coverage is sensitive to extent alignment, delayed allocation, unwritten extents, and page-size dependent block geometry, so comparisons against check files are the main correctness guard.
- Direct I/O paths can be affected by device sector size, alignment, cache invalidation, and filesystem-specific serialization between buffered and direct writes.
- Extent-map output is formatted and filtered, but the test still depends on stable extent flags, logical block addressing, and filesystem support for the ioctl under test.

## Test Signals

The pass signal is filtered extent-map output. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/326 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/327 -->
# sources/test-tools/xfstests/tests/generic/327

## Purpose

Ensure that we can't go over the hard block limit when reflinking. It is registered with `_begin_fstest auto quick clone fiemap` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `327` plus `_begin_fstest auto quick clone fiemap`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`, `. ./common/quota`. Capability gates: `_require_scratch_reflink`, `_require_cp_reflink`, `_require_xfs_io_command "fiemap"`, `_require_quota`, `_require_nobody`, `_require_user`. Local functions: none. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 32: `testdir=$SCRATCH_MNT/test-$seq`
- Line 35: `sz=1048576`
- Line 55: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 24 `echo "Format and mount"`, line 36 `echo "Create the original files"`, line 44 `echo "Set hard quota to prevent third reflink"`, line 48 `echo "Try to reflink again"`. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 10: `_begin_fstest auto quick clone fiemap`
- Line 15: `. ./common/quota`
- Line 17: `_require_scratch_reflink`
- Line 18: `_require_cp_reflink`
- Line 19: `_require_xfs_io_command "fiemap"`
- Line 20: `_require_quota`
- Line 24: `echo "Format and mount"`
- Line 25: `_scratch_mkfs > $seqres.full 2>&1`
- Line 26: `export MOUNT_OPTIONS="-o usrquota,grpquota $MOUNT_OPTIONS"`
- Line 27: `_scratch_mount >> $seqres.full 2>&1`
- Line 28: `_force_vfs_quota_testing $SCRATCH_MNT`
- Line 29: `quotacheck -u -g $SCRATCH_MNT 2> /dev/null`
- Line 30: `quotaon $SCRATCH_MNT 2> /dev/null`
- Line 52: `_report_quota_blocks $SCRATCH_MNT`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Cycle-mount calls force metadata and extent state through unmount/remount persistence before validation. Quota state is persistent filesystem metadata manipulated through `quotacheck`, `quotaon`, `setquota`, and `repquota` across user and group modes. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `clone`, `fiemap`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`, `. ./common/quota`, and uses capability gates such as `_require_scratch_reflink`, `_require_cp_reflink`, `_require_xfs_io_command "fiemap"`, `_require_quota`, `_require_nobody`, `_require_user`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Quota tests depend on kernel quota mode, grace-period timing, and the qa user/group setup; stale quota files or unsupported VFS quota behavior can turn a real failure into a notrun or noisy output mismatch.
- Reflink coverage is sensitive to extent alignment, delayed allocation, unwritten extents, and page-size dependent block geometry, so comparisons against check files are the main correctness guard.
- Extent-map output is formatted and filtered, but the test still depends on stable extent flags, logical block addressing, and filesystem support for the ioctl under test.

## Test Signals

The pass signal is filtered extent-map output. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/327 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/328 -->
# sources/test-tools/xfstests/tests/generic/328

## Purpose

Ensure that we can't go over the hard block limit when CoWing a file. It is registered with `_begin_fstest auto quick clone fiemap` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `328` plus `_begin_fstest auto quick clone fiemap`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`, `. ./common/quota`. Capability gates: `_require_scratch_reflink`, `_require_cp_reflink`, `_require_xfs_io_command "fiemap"`, `_require_quota`, `_require_nobody`, `_require_odirect`, `_require_user`. Local functions: none. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 33: `testdir=$SCRATCH_MNT/test-$seq`
- Line 36: `sz=4194304`
- Line 75: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 25 `echo "Format and mount"`, line 37 `echo "Create the original files"`, line 46 `echo "Set hard quota to prevent rewrite"`, line 50 `echo "Try to dio write the whole file"`. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 10: `_begin_fstest auto quick clone fiemap`
- Line 17: `_require_scratch_reflink`
- Line 19: `_require_xfs_io_command "fiemap"`
- Line 25: `echo "Format and mount"`
- Line 27: `export MOUNT_OPTIONS="-o usrquota,grpquota $MOUNT_OPTIONS"`
- Line 29: `_force_vfs_quota_testing $SCRATCH_MNT`
- Line 31: `quotaon $SCRATCH_MNT 2> /dev/null`
- Line 38: `$XFS_IO_PROG -f -c "pwrite -S 0x61 -b $sz 0 $sz" $testdir/file1 >> $seqres.full`
- Line 40: `_cp_reflink $testdir/file1 $testdir/file2 >> $seqres.full`
- Line 42: `_report_quota_blocks $SCRATCH_MNT`
- Line 44: `quotaon $SCRATCH_MNT 2> /dev/null`
- Line 47: `setquota -u $qa_user 0 1024 0 0 $SCRATCH_MNT`
- Line 51: `_su $qa_user -c '$XFS_IO_PROG -d -c "pwrite 0 '$((sz+65536))'" '$testdir'/file1' 2>&1 >> $seqres.full | \`
- Line 72: `_report_quota_blocks $SCRATCH_MNT`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Cycle-mount calls force metadata and extent state through unmount/remount persistence before validation. Quota state is persistent filesystem metadata manipulated through `quotacheck`, `quotaon`, `setquota`, and `repquota` across user and group modes. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `clone`, `fiemap`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`, `. ./common/quota`, and uses capability gates such as `_require_scratch_reflink`, `_require_cp_reflink`, `_require_xfs_io_command "fiemap"`, `_require_quota`, `_require_nobody`, `_require_odirect`, `_require_user`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Quota tests depend on kernel quota mode, grace-period timing, and the qa user/group setup; stale quota files or unsupported VFS quota behavior can turn a real failure into a notrun or noisy output mismatch.
- Reflink coverage is sensitive to extent alignment, delayed allocation, unwritten extents, and page-size dependent block geometry, so comparisons against check files are the main correctness guard.
- Direct I/O paths can be affected by device sector size, alignment, cache invalidation, and filesystem-specific serialization between buffered and direct writes.
- Extent-map output is formatted and filtered, but the test still depends on stable extent flags, logical block addressing, and filesystem support for the ioctl under test.

## Test Signals

The pass signal is filtered extent-map output. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/328 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/329 -->
# sources/test-tools/xfstests/tests/generic/329

## Purpose

Test AIO DIO CoW behavior when the write temporarily fails. It is registered with `_begin_fstest auto quick clone eio` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `329` plus `_begin_fstest auto quick clone eio`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`, `. ./common/dmerror`. Capability gates: `_require_scratch_reflink`, `_require_cp_reflink`, `_require_dm_target error`, `_require_aiodio "aiocp"`, `_require_fs_space $SCRATCH_MNT $((filesize / 1024 * 3 * 5 / 4))`. Local functions: `_cleanup`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 35: `testdir=$SCRATCH_MNT/test-$seq`
- Line 38: `blksz=65536`
- Line 39: `nr=640`
- Line 40: `bufnr=128`
- Line 41: `filesize=$((blksz * nr))`
- Line 42: `bufsize=$((blksz * bufnr))`
- Line 43: `alignment=`$here/src/min_dio_alignment $TEST_DIR $TEST_DEV``
- Line 78: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 30 `echo "Format and mount"`, line 47 `echo "Create the original files"`, line 53 `echo "Compare files"`, line 57 `echo "CoW and unmount"`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 16: `rm -rf $tmp.* $TEST_DIR/moo`
- Line 25: `_require_scratch_reflink`
- Line 27: `_require_dm_target error`
- Line 31: `_scratch_mkfs > $seqres.full 2>&1`
- Line 33: `_dmerror_mount >> $seqres.full 2>&1`
- Line 48: `$XFS_IO_PROG -f -c "pwrite -S 0x61 -b $bufsize 0 $filesize" $testdir/file1 >> $seqres.full`
- Line 50: `_dmerror_unmount`
- Line 54: `md5sum $testdir/file1 | _filter_scratch`
- Line 57: `echo "CoW and unmount"`
- Line 59: `$XFS_IO_PROG -f -c "pwrite -S 0x63 -b $bufsize 0 $filesize" $TEST_DIR/moo >> $seqres.full`
- Line 61: `_dmerror_load_error_table`
- Line 64: `_dmerror_load_working_table`
- Line 66: `_dmerror_mount`
- Line 75: `_repair_scratch_fs >> $seqres.full`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. It may also use `$TEST_DIR` for non-destructive helper programs or limit checks. Temporary files are rooted at `$tmp.*` and removed by the local or default cleanup path. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `clone`, `eio`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`, `. ./common/dmerror`, and uses capability gates such as `_require_scratch_reflink`, `_require_cp_reflink`, `_require_dm_target error`, `_require_aiodio "aiocp"`, `_require_fs_space $SCRATCH_MNT $((filesize / 1024 * 3 * 5 / 4))`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Reflink coverage is sensitive to extent alignment, delayed allocation, unwritten extents, and page-size dependent block geometry, so comparisons against check files are the main correctness guard.
- Direct I/O paths can be affected by device sector size, alignment, cache invalidation, and filesystem-specific serialization between buffered and direct writes.
- Crash-recovery tests require dm-flakey behavior and metadata journaling; failures can appear as lost directory entries, stale content, or mount-time recovery errors.

## Test Signals

The pass signal is filtered `md5sum` output. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/329 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/330 -->
# sources/test-tools/xfstests/tests/generic/330

## Purpose

Test AIO DIO CoW behavior. It is registered with `_begin_fstest auto quick clone` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `330` plus `_begin_fstest auto quick clone`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`. Capability gates: `_require_scratch_reflink`, `_require_cp_reflink`, `_require_aiodio "aiocp"`, `_require_fs_space $SCRATCH_MNT $((filesize / 1024 * 3 * 5 / 4))`. Local functions: `_cleanup`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 31: `testdir=$SCRATCH_MNT/test-$seq`
- Line 34: `blksz=65536`
- Line 35: `nr=640`
- Line 36: `bufnr=128`
- Line 37: `filesize=$((blksz * nr))`
- Line 38: `bufsize=$((blksz * bufnr))`
- Line 39: `alignment=`$here/src/min_dio_alignment $TEST_DIR $TEST_DEV``
- Line 68: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 27 `echo "Format and mount"`, line 43 `echo "Create the original files"`, line 48 `echo "Compare files"`, line 52 `echo "CoW and unmount"`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 16: `rm -rf $tmp.* $TEST_DIR/moo`
- Line 23: `_require_scratch_reflink`
- Line 24: `_require_cp_reflink`
- Line 27: `echo "Format and mount"`
- Line 28: `_scratch_mkfs > $seqres.full 2>&1`
- Line 29: `_scratch_mount >> $seqres.full 2>&1`
- Line 32: `mkdir $testdir`
- Line 44: `$XFS_IO_PROG -f -c "pwrite -S 0x61 -b $bufsize 0 $filesize" $testdir/file1 >> $seqres.full`
- Line 45: `_cp_reflink $testdir/file1 $testdir/file2 >> $seqres.full`
- Line 46: `_scratch_cycle_mount`
- Line 49: `md5sum $testdir/file1 | _filter_scratch`
- Line 50: `md5sum $testdir/file2 | _filter_scratch`
- Line 52: `echo "CoW and unmount"`
- Line 65: `_repair_scratch_fs >> $seqres.full`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. It may also use `$TEST_DIR` for non-destructive helper programs or limit checks. Cycle-mount calls force metadata and extent state through unmount/remount persistence before validation. Temporary files are rooted at `$tmp.*` and removed by the local or default cleanup path. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `clone`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`, and uses capability gates such as `_require_scratch_reflink`, `_require_cp_reflink`, `_require_aiodio "aiocp"`, `_require_fs_space $SCRATCH_MNT $((filesize / 1024 * 3 * 5 / 4))`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Reflink coverage is sensitive to extent alignment, delayed allocation, unwritten extents, and page-size dependent block geometry, so comparisons against check files are the main correctness guard.
- Direct I/O paths can be affected by device sector size, alignment, cache invalidation, and filesystem-specific serialization between buffered and direct writes.

## Test Signals

The pass signal is filtered `md5sum` output. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/330 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/331 -->
# sources/test-tools/xfstests/tests/generic/331

## Purpose

Test AIO CoW behavior when the write temporarily fails. It is registered with `_begin_fstest auto quick clone eio` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `331` plus `_begin_fstest auto quick clone eio`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`, `. ./common/dmerror`. Capability gates: `_require_scratch_reflink`, `_require_cp_reflink`, `_require_dm_target error`, `_require_aiodio "aiocp"`, `_require_fs_space $SCRATCH_MNT $((filesize / 1024 * 3 * 5 / 4))`. Local functions: `_cleanup`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 29: `AIO_TEST="$here/src/aio-dio-regress/aiocp"`
- Line 36: `testdir=$SCRATCH_MNT/test-$seq`
- Line 39: `blksz=65536`
- Line 40: `nr=640`
- Line 41: `bufnr=128`
- Line 42: `filesize=$((blksz * nr))`
- Line 43: `bufsize=$((blksz * bufnr))`
- Line 67: `write_failed=1`

## Control Flow

The visible phases are driven by echo markers such as line 31 `echo "Format and mount"`, line 47 `echo "Create the original files"`, line 53 `echo "Compare files"`, line 57 `echo "CoW and unmount"`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 16: `rm -rf $tmp.* $TEST_DIR/moo`
- Line 25: `_require_scratch_reflink`
- Line 27: `_require_dm_target error`
- Line 32: `_scratch_mkfs > $seqres.full 2>&1`
- Line 34: `_dmerror_mount >> $seqres.full 2>&1`
- Line 48: `$XFS_IO_PROG -f -c "pwrite -S 0x61 -b $bufsize 0 $filesize" $testdir/file1 >> $seqres.full`
- Line 50: `_dmerror_unmount`
- Line 54: `md5sum $testdir/file1 | _filter_scratch`
- Line 57: `echo "CoW and unmount"`
- Line 59: `$XFS_IO_PROG -f -c "pwrite -S 0x63 -b $bufsize 0 $filesize" $TEST_DIR/moo >> $seqres.full`
- Line 65: `_dmerror_load_error_table`
- Line 69: `_filter_flakey_EIO "fdatasync: Input/output error" | \`
- Line 75: `_dmerror_unmount`
- Line 85: `_repair_scratch_fs >> $seqres.full`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. It may also use `$TEST_DIR` for non-destructive helper programs or limit checks. Temporary files are rooted at `$tmp.*` and removed by the local or default cleanup path. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `clone`, `eio`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`, `. ./common/dmerror`, and uses capability gates such as `_require_scratch_reflink`, `_require_cp_reflink`, `_require_dm_target error`, `_require_aiodio "aiocp"`, `_require_fs_space $SCRATCH_MNT $((filesize / 1024 * 3 * 5 / 4))`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Reflink coverage is sensitive to extent alignment, delayed allocation, unwritten extents, and page-size dependent block geometry, so comparisons against check files are the main correctness guard.
- Direct I/O paths can be affected by device sector size, alignment, cache invalidation, and filesystem-specific serialization between buffered and direct writes.
- Crash-recovery tests require dm-flakey behavior and metadata journaling; failures can appear as lost directory entries, stale content, or mount-time recovery errors.

## Test Signals

The pass signal is filtered `md5sum` output, explicit `_fail` assertions. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/331 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/332 -->
# sources/test-tools/xfstests/tests/generic/332

## Purpose

Test AIO CoW behavior. It is registered with `_begin_fstest auto quick clone` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `332` plus `_begin_fstest auto quick clone`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`. Capability gates: `_require_scratch_reflink`, `_require_cp_reflink`, `_require_aiodio "aiocp"`, `_require_fs_space $SCRATCH_MNT $((filesize / 1024 * 3 * 5 / 4))`. Local functions: `_cleanup`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 26: `AIO_TEST="$here/src/aio-dio-regress/aiocp"`
- Line 32: `testdir=$SCRATCH_MNT/test-$seq`
- Line 35: `blksz=65536`
- Line 36: `nr=640`
- Line 37: `bufnr=128`
- Line 38: `filesize=$((blksz * nr))`
- Line 39: `bufsize=$((blksz * bufnr))`
- Line 68: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 28 `echo "Format and mount"`, line 43 `echo "Create the original files"`, line 48 `echo "Compare files"`, line 52 `echo "CoW and unmount"`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 16: `rm -rf $tmp.* $TEST_DIR/moo`
- Line 23: `_require_scratch_reflink`
- Line 24: `_require_cp_reflink`
- Line 28: `echo "Format and mount"`
- Line 29: `_scratch_mkfs > $seqres.full 2>&1`
- Line 30: `_scratch_mount >> $seqres.full 2>&1`
- Line 33: `mkdir $testdir`
- Line 44: `$XFS_IO_PROG -f -c "pwrite -S 0x61 -b $bufsize 0 $filesize" $testdir/file1 >> $seqres.full`
- Line 45: `_cp_reflink $testdir/file1 $testdir/file2 >> $seqres.full`
- Line 46: `_scratch_cycle_mount`
- Line 49: `md5sum $testdir/file1 | _filter_scratch`
- Line 50: `md5sum $testdir/file2 | _filter_scratch`
- Line 52: `echo "CoW and unmount"`
- Line 65: `_repair_scratch_fs >> $seqres.full`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. It may also use `$TEST_DIR` for non-destructive helper programs or limit checks. Cycle-mount calls force metadata and extent state through unmount/remount persistence before validation. Temporary files are rooted at `$tmp.*` and removed by the local or default cleanup path. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `clone`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`, and uses capability gates such as `_require_scratch_reflink`, `_require_cp_reflink`, `_require_aiodio "aiocp"`, `_require_fs_space $SCRATCH_MNT $((filesize / 1024 * 3 * 5 / 4))`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Reflink coverage is sensitive to extent alignment, delayed allocation, unwritten extents, and page-size dependent block geometry, so comparisons against check files are the main correctness guard.

## Test Signals

The pass signal is filtered `md5sum` output. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/332 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/333 -->
# sources/test-tools/xfstests/tests/generic/333

## Purpose

Test for races or FS corruption when trying to hit ENOSPC while DIO writing to a file that's also the source of a reflink operation. It is registered with `_begin_fstest auto clone` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `333` plus `_begin_fstest auto clone`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`. Capability gates: `_require_scratch_reflink`, `_require_cp_reflink`, `_require_odirect`. Local functions: `_cleanup`, `snappy`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 35: `testdir=$SCRATCH_MNT/test-$seq`
- Line 36: `finished_file=$tmp.finished`
- Line 38: `abort_file=$tmp.abort`
- Line 42: `loops=1024`
- Line 43: `nr_loops=$((loops - 1))`
- Line 44: `blksz=65536`
- Line 53: `n=0`
- Line 55: `out="$(_cp_reflink $testdir/file1 $testdir/snap_$n 2>&1)"`

## Control Flow

The visible phases are driven by echo markers such as line 31 `echo "Format and mount"`, line 46 `echo "Initialize file"`, line 47 `echo >> $seqres.full`, line 57 `echo $out | grep -q "No space left" && break`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 19: `rm -rf $tmp.*`
- Line 27: `_require_scratch_reflink`
- Line 28: `_require_cp_reflink`
- Line 31: `echo "Format and mount"`
- Line 32: `_scratch_mkfs_sized $((400 * 1048576)) > $seqres.full 2>&1`
- Line 33: `_scratch_mount >> $seqres.full 2>&1`
- Line 37: `rm -rf $finished_file`
- Line 39: `rm -rf $abort_file`
- Line 40: `mkdir $testdir`
- Line 48: `_pwrite_byte 0x61 0 $((loops * blksz)) $testdir/file1 >> $seqres.full`
- Line 49: `_scratch_cycle_mount`
- Line 55: `out="$(_cp_reflink $testdir/file1 $testdir/snap_$n 2>&1)"`
- Line 62: `touch $abort_file`
- Line 77: `touch $finished_file`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Cycle-mount calls force metadata and extent state through unmount/remount persistence before validation. Temporary files are rooted at `$tmp.*` and removed by the local or default cleanup path. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `clone`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`, and uses capability gates such as `_require_scratch_reflink`, `_require_cp_reflink`, `_require_odirect`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Reflink coverage is sensitive to extent alignment, delayed allocation, unwritten extents, and page-size dependent block geometry, so comparisons against check files are the main correctness guard.
- Direct I/O paths can be affected by device sector size, alignment, cache invalidation, and filesystem-specific serialization between buffered and direct writes.
- ENOSPC cases are deliberately capacity-sensitive and can expose allocator, reservation, or delayed-allocation leaks only when scratch sizing and reserved blocks match the scenario.

## Test Signals

The pass signal is silence from the helper program and final `status=0`. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/333 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/334 -->
# sources/test-tools/xfstests/tests/generic/334

## Purpose

Test for races or FS corruption when trying to hit ENOSPC while writing to a file that's also the source of a reflink operation. It is registered with `_begin_fstest auto clone` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `334` plus `_begin_fstest auto clone`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`. Capability gates: `_require_scratch_reflink`, `_require_cp_reflink`. Local functions: `_cleanup`, `snappy`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 34: `testdir=$SCRATCH_MNT/test-$seq`
- Line 35: `finished_file=$tmp.finished`
- Line 37: `abort_file=$tmp.abort`
- Line 41: `loops=1024`
- Line 42: `nr_loops=$((loops - 1))`
- Line 43: `blksz=65536`
- Line 52: `n=0`
- Line 54: `out="$(_cp_reflink $testdir/file1 $testdir/snap_$n 2>&1)"`

## Control Flow

The visible phases are driven by echo markers such as line 30 `echo "Format and mount"`, line 45 `echo "Initialize file"`, line 46 `echo >> $seqres.full`, line 56 `echo $out | grep -q "No space left" && break`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 19: `rm -rf $tmp.*`
- Line 27: `_require_scratch_reflink`
- Line 28: `_require_cp_reflink`
- Line 30: `echo "Format and mount"`
- Line 31: `_scratch_mkfs_sized $((400 * 1048576)) > $seqres.full 2>&1`
- Line 32: `_scratch_mount >> $seqres.full 2>&1`
- Line 36: `rm -rf $finished_file`
- Line 38: `rm -rf $abort_file`
- Line 39: `mkdir $testdir`
- Line 47: `_pwrite_byte 0x61 0 $((loops * blksz)) $testdir/file1 >> $seqres.full`
- Line 48: `_scratch_cycle_mount`
- Line 54: `out="$(_cp_reflink $testdir/file1 $testdir/snap_$n 2>&1)"`
- Line 61: `touch $abort_file`
- Line 76: `touch $finished_file`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Cycle-mount calls force metadata and extent state through unmount/remount persistence before validation. Temporary files are rooted at `$tmp.*` and removed by the local or default cleanup path. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `clone`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`, and uses capability gates such as `_require_scratch_reflink`, `_require_cp_reflink`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Reflink coverage is sensitive to extent alignment, delayed allocation, unwritten extents, and page-size dependent block geometry, so comparisons against check files are the main correctness guard.
- ENOSPC cases are deliberately capacity-sensitive and can expose allocator, reservation, or delayed-allocation leaks only when scratch sizing and reserved blocks match the scenario.

## Test Signals

The pass signal is silence from the helper program and final `status=0`. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/334 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/335 -->
# sources/test-tools/xfstests/tests/generic/335

## Purpose

Test that if we move one file between directories, fsync the parent directory of the old directory, power fail and remount the filesystem, the file is not lost and it's located at the destination directory Create our test directories and the file we will later check if it has disappeared. It is registered with `_begin_fstest auto quick metadata log` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `335` plus `_begin_fstest auto quick metadata log`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/dmflakey`. Capability gates: `_require_scratch`, `_require_dm_target flakey`, `_require_metadata_journaling $SCRATCH_DEV`. Local functions: `_cleanup`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 78: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 61 `echo "Filesystem content before power failure:"`, line 72 `echo "Filesystem content after power failure:"`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 19: `rm -f $tmp.*`
- Line 26: `_require_scratch`
- Line 27: `_require_dm_target flakey`
- Line 29: `_scratch_mkfs >>$seqres.full 2>&1`
- Line 32: `_scratch_mount`
- Line 36: `mkdir -p $SCRATCH_MNT/a/b`
- Line 37: `mkdir $SCRATCH_MNT/c`
- Line 38: `touch $SCRATCH_MNT/a/b/foo`
- Line 41: `_scratch_sync`
- Line 44: `mv $SCRATCH_MNT/a/b/foo $SCRATCH_MNT/c/`
- Line 49: `touch $SCRATCH_MNT/a/bar`
- Line 50: `$XFS_IO_PROG -c "fsync" $SCRATCH_MNT/a`
- Line 58: `$XFS_IO_PROG -c "fsync" $SCRATCH_MNT/c/foo`
- Line 76: `_scratch_unmount`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. dm-flakey is used to simulate a dropped write / power-fail boundary and then remount for recovery checks. Temporary files are rooted at `$tmp.*` and removed by the local or default cleanup path. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `metadata`, `log`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/dmflakey`, and uses capability gates such as `_require_scratch`, `_require_dm_target flakey`, `_require_metadata_journaling $SCRATCH_DEV`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Direct I/O paths can be affected by device sector size, alignment, cache invalidation, and filesystem-specific serialization between buffered and direct writes.
- Crash-recovery tests require dm-flakey behavior and metadata journaling; failures can appear as lost directory entries, stale content, or mount-time recovery errors.
- Thin-provisioning tests depend on device-mapper target behavior, pool exhaustion semantics, and correct cleanup of temporary block devices.

## Test Signals

The pass signal is silence from the helper program and final `status=0`. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/335 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/336 -->
# sources/test-tools/xfstests/tests/generic/336

## Purpose

Test that if we have a file F1 with two links, one in a directory A and the other in directory B, if we remove the link in directory B, move some other file F2 from directory B into directory C, fsync inode F1, power fail and remount the filesystem, file F2 exists and is located only in directory C unreliable_in_parallel: external sync operations can change what is synced to the log before the flakey device drops writes. hence post-remount file contents can be different to what the test expects. It is registered with `_begin_fstest auto quick metadata log unreliable_in_parallel` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `336` plus `_begin_fstest auto quick metadata log unreliable_in_parallel`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/dmflakey`. Capability gates: `_require_scratch`, `_require_hardlinks`, `_require_dm_target flakey`, `_require_metadata_journaling $SCRATCH_DEV`. Local functions: `_cleanup`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 75: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 60 `echo "Filesystem content before power failure:"`, line 69 `echo "Filesystem content after power failure:"`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 25: `rm -f $tmp.*`
- Line 32: `_require_scratch`
- Line 34: `_require_dm_target flakey`
- Line 36: `_scratch_mkfs >>$seqres.full 2>&1`
- Line 39: `_scratch_mount`
- Line 43: `mkdir $SCRATCH_MNT/a`
- Line 44: `mkdir $SCRATCH_MNT/b`
- Line 45: `mkdir $SCRATCH_MNT/c`
- Line 46: `touch $SCRATCH_MNT/a/foo`
- Line 47: `ln $SCRATCH_MNT/a/foo $SCRATCH_MNT/b/foo_link`
- Line 48: `touch $SCRATCH_MNT/b/bar`
- Line 51: `_scratch_sync`
- Line 55: `mv $SCRATCH_MNT/b/bar $SCRATCH_MNT/c/`
- Line 73: `_scratch_unmount`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. dm-flakey is used to simulate a dropped write / power-fail boundary and then remount for recovery checks. Temporary files are rooted at `$tmp.*` and removed by the local or default cleanup path. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `metadata`, `log`, `unreliable_in_parallel`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/dmflakey`, and uses capability gates such as `_require_scratch`, `_require_hardlinks`, `_require_dm_target flakey`, `_require_metadata_journaling $SCRATCH_DEV`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Direct I/O paths can be affected by device sector size, alignment, cache invalidation, and filesystem-specific serialization between buffered and direct writes.
- Crash-recovery tests require dm-flakey behavior and metadata journaling; failures can appear as lost directory entries, stale content, or mount-time recovery errors.
- Thin-provisioning tests depend on device-mapper target behavior, pool exhaustion semantics, and correct cleanup of temporary block devices.

## Test Signals

The pass signal is silence from the helper program and final `status=0`. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/336 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/337 -->
# sources/test-tools/xfstests/tests/generic/337

## Purpose

Test that the filesystem's implementation of the listxattrs system call lists all the xattrs an inode has Create our test file with a few xattrs. The first 3 xattrs have a name that when given as input to a crc32c function result in the same checksum. This made btrfs list only one of the xattrs through listxattrs system call (because it packs xattrs with the same name checksum into the same btree item) Now call getfattr with --dump, which calls the listxattrs system call It should list all the xattrs we have set before. It is registered with `_begin_fstest auto quick attr metadata` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `337` plus `_begin_fstest auto quick attr metadata`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`. Capability gates: `_require_scratch`, `_require_attrs`. Local functions: none. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 38: `status=0`

## Control Flow

The script runs linearly after the harness and requirement checks. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 17: `_require_scratch`
- Line 20: `_scratch_mkfs >>$seqres.full 2>&1`
- Line 21: `_scratch_mount`
- Line 27: `touch $SCRATCH_MNT/testfile`
- Line 36: `_getfattr --absolute-names --dump $SCRATCH_MNT/testfile | _filter_scratch`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `attr`, `metadata`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`, and uses capability gates such as `_require_scratch`, `_require_attrs`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Thin-provisioning tests depend on device-mapper target behavior, pool exhaustion semantics, and correct cleanup of temporary block devices.

## Test Signals

The pass signal is silence from the helper program and final `status=0`. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/337 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/338 -->
# sources/test-tools/xfstests/tests/generic/338

## Purpose

Test I/O on dm error device Motivated by an ext4 bug that crashes kernel on error path when trying to update atime If SCRATCH_DEV is not a valid block device, FSTYP cannot be mkfs'ed either. It is registered with `_begin_fstest auto quick rw eio` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `338` plus `_begin_fstest auto quick rw eio`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/dmerror`. Capability gates: `_require_scratch_nocheck # fs went down with a dirty log, don't check it`, `_require_dm_target error`, `_require_block_device $SCRATCH_DEV`. Local functions: `_cleanup`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 52: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 32 `echo "Silence is golden"`, line 45 `echo 3 > /proc/sys/vm/drop_caches`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 19: `rm -f $tmp.*`
- Line 20: `_dmerror_cleanup`
- Line 27: `_require_scratch_nocheck # fs went down with a dirty log, don't check it`
- Line 28: `_require_dm_target error`
- Line 34: `_scratch_mkfs >>$seqres.full 2>&1`
- Line 35: `_dmerror_init`
- Line 39: `_dmerror_mount "-o strictatime"`
- Line 40: `_dmerror_load_error_table`
- Line 49: `$XFS_IO_PROG -fc "pwrite 0 1M" $SCRATCH_MNT/testfile >>$seqres.full 2>&1`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Temporary files are rooted at `$tmp.*` and removed by the local or default cleanup path. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `rw`, `eio`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/dmerror`, and uses capability gates such as `_require_scratch_nocheck # fs went down with a dirty log, don't check it`, `_require_dm_target error`, `_require_block_device $SCRATCH_DEV`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Block-device fallocate tests rely on scsi_debug discard/write-same emulation and logical-sector alignment, not normal mounted filesystem behavior.

## Test Signals

The pass signal is silence from the helper program and final `status=0`. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/338 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/339 -->
# sources/test-tools/xfstests/tests/generic/339

## Purpose

Test that directory hash entries are place in the correct order commit f5ea110 ("xfs: add CRCs to dir2/da node blocks") left the directory with incorrect hash ordering check the scratch device remove all test dirs and let test harness check scratch fs again. It is registered with `_begin_fstest auto dir` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `339` plus `_begin_fstest auto dir`. Imported libraries: `. ./common/preamble`, `. ./common/filter`. Capability gates: `_require_scratch`, `_require_test_program "dirhash_collide"`. Local functions: none. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 25: `testdir=$SCRATCH_MNT/$seq.$$`
- Line 38: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 23 `echo "Silence is golden"`. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 17: `_require_scratch`
- Line 18: `_require_test_program "dirhash_collide"`
- Line 20: `_scratch_mkfs >>$seqres.full 2>&1`
- Line 21: `_scratch_mount`
- Line 26: `mkdir -p $testdir`
- Line 30: `_scratch_unmount`
- Line 31: `_check_scratch_fs`
- Line 34: `_scratch_mount`
- Line 35: `rm -rf $testdir`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `dir`, imports `. ./common/preamble`, `. ./common/filter`, and uses capability gates such as `_require_scratch`, `_require_test_program "dirhash_collide"`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Direct I/O paths can be affected by device sector size, alignment, cache invalidation, and filesystem-specific serialization between buffered and direct writes.

## Test Signals

The pass signal is silence from the helper program and final `status=0`. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/339 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/340 -->
# sources/test-tools/xfstests/tests/generic/340

## Purpose

Test mmap writing races from racing threads. It is registered with `_begin_fstest auto mmap` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `340` plus `_begin_fstest auto mmap`. Imported libraries: `. ./common/preamble`. Capability gates: `_require_scratch`, `_require_test_program "holetest"`. Local functions: none. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 24: `status=0`

## Control Flow

The script runs linearly after the harness and requirement checks. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 10: `_begin_fstest auto mmap`
- Line 14: `_require_scratch`
- Line 15: `_require_test_program "holetest"`
- Line 17: `_scratch_mkfs >>$seqres.full 2>&1`
- Line 18: `_scratch_mount`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `mmap`, imports `. ./common/preamble`, and uses capability gates such as `_require_scratch`, `_require_test_program "holetest"`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- mmap tests rely on page-cache writeback, timestamp granularity, and correct handling of dirty mappings across fsync, sync, or remount boundaries.

## Test Signals

The pass signal is silence from the helper program and final `status=0`. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/340 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/341 -->
# sources/test-tools/xfstests/tests/generic/341

## Purpose

Test that if we rename a directory, create a new file or directory that has the old name of our former directory and is a child of the same parent directory, fsync the new inode, power fail and mount the filesystem, we see our first directory with the new name and no files under it were lost. It is registered with `_begin_fstest auto quick metadata log` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `341` plus `_begin_fstest auto quick metadata log`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/dmflakey`. Capability gates: `_require_scratch`, `_require_dm_target flakey`, `_require_metadata_journaling $SCRATCH_DEV`. Local functions: `_cleanup`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 66: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 41 `echo "File digests before power failure:"`, line 57 `echo "Directory a/ contents after log replay:"`, line 60 `echo "File digests after log replay:"`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 20: `rm -f $tmp.*`
- Line 27: `_require_scratch`
- Line 28: `_require_dm_target flakey`
- Line 30: `_scratch_mkfs >>$seqres.full 2>&1`
- Line 33: `_scratch_mount`
- Line 35: `mkdir -p $SCRATCH_MNT/a/x`
- Line 36: `$XFS_IO_PROG -f -c "pwrite -S 0xaf 0 32K" $SCRATCH_MNT/a/x/foo | _filter_xfs_io`
- Line 37: `$XFS_IO_PROG -f -c "pwrite -S 0xba 0 32K" $SCRATCH_MNT/a/x/bar | _filter_xfs_io`
- Line 39: `_scratch_sync`
- Line 42: `md5sum $SCRATCH_MNT/a/x/foo | _filter_scratch`
- Line 43: `md5sum $SCRATCH_MNT/a/x/bar | _filter_scratch`
- Line 49: `mv $SCRATCH_MNT/a/x $SCRATCH_MNT/a/y`
- Line 50: `mkdir $SCRATCH_MNT/a/x`
- Line 65: `_scratch_unmount`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. dm-flakey is used to simulate a dropped write / power-fail boundary and then remount for recovery checks. Temporary files are rooted at `$tmp.*` and removed by the local or default cleanup path. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `metadata`, `log`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/dmflakey`, and uses capability gates such as `_require_scratch`, `_require_dm_target flakey`, `_require_metadata_journaling $SCRATCH_DEV`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Direct I/O paths can be affected by device sector size, alignment, cache invalidation, and filesystem-specific serialization between buffered and direct writes.
- Crash-recovery tests require dm-flakey behavior and metadata journaling; failures can appear as lost directory entries, stale content, or mount-time recovery errors.
- Thin-provisioning tests depend on device-mapper target behavior, pool exhaustion semantics, and correct cleanup of temporary block devices.

## Test Signals

The pass signal is filtered `md5sum` output. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/341 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/342 -->
# sources/test-tools/xfstests/tests/generic/342

## Purpose

Test that if we rename a file, create a new file that has the old name of the other file and is a child of the same parent directory, fsync the new inode, power fail and mount the filesystem, we do not lose the first file and that file has the name it was renamed to. It is registered with `_begin_fstest auto quick metadata log` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `342` plus `_begin_fstest auto quick metadata log`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/dmflakey`. Capability gates: `_require_scratch`, `_require_dm_target flakey`, `_require_metadata_journaling $SCRATCH_DEV`. Local functions: `_cleanup`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 68: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 51 `echo "File digests before log replay:"`, line 59 `echo "Directory a/ contents after log replay:"`, line 62 `echo "File digests after log replay:"`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 20: `rm -f $tmp.*`
- Line 27: `_require_scratch`
- Line 28: `_require_dm_target flakey`
- Line 30: `_scratch_mkfs >>$seqres.full 2>&1`
- Line 34: `export MOUNT_OPTIONS="-o fsync_mode=strict $MOUNT_OPTIONS"`
- Line 38: `_scratch_mount`
- Line 40: `mkdir $SCRATCH_MNT/a`
- Line 41: `$XFS_IO_PROG -f -c "pwrite -S 0xf1 0 16K" $SCRATCH_MNT/a/foo | _filter_xfs_io`
- Line 43: `_scratch_sync`
- Line 47: `mv $SCRATCH_MNT/a/foo $SCRATCH_MNT/a/bar`
- Line 48: `$XFS_IO_PROG -f -c "pwrite -S 0xba 0 16K" $SCRATCH_MNT/a/foo | _filter_xfs_io`
- Line 49: `$XFS_IO_PROG -c "fsync" $SCRATCH_MNT/a/foo`
- Line 52: `md5sum $SCRATCH_MNT/a/foo | _filter_scratch`
- Line 67: `_scratch_unmount`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. dm-flakey is used to simulate a dropped write / power-fail boundary and then remount for recovery checks. Temporary files are rooted at `$tmp.*` and removed by the local or default cleanup path. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `metadata`, `log`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/dmflakey`, and uses capability gates such as `_require_scratch`, `_require_dm_target flakey`, `_require_metadata_journaling $SCRATCH_DEV`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Direct I/O paths can be affected by device sector size, alignment, cache invalidation, and filesystem-specific serialization between buffered and direct writes.
- Crash-recovery tests require dm-flakey behavior and metadata journaling; failures can appear as lost directory entries, stale content, or mount-time recovery errors.
- Thin-provisioning tests depend on device-mapper target behavior, pool exhaustion semantics, and correct cleanup of temporary block devices.

## Test Signals

The pass signal is filtered `md5sum` output. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/342 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/343 -->
# sources/test-tools/xfstests/tests/generic/343

## Purpose

Test that if we create a hard link for a file F in some directory A, then move some directory or file B from its parent directory C into directory A, fsync file F, power fail and mount the filesystem, the directory/file B is located only at directory A and both links for file F exist. It is registered with `_begin_fstest auto quick metadata log` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `343` plus `_begin_fstest auto quick metadata log`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/dmflakey`. Capability gates: `_require_scratch`, `_require_hardlinks`, `_require_dm_target flakey`, `_require_metadata_journaling $SCRATCH_DEV`. Local functions: `_cleanup`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 60: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 56 `echo "Filesystem contents after log replay:"`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 20: `rm -f $tmp.*`
- Line 27: `_require_scratch`
- Line 29: `_require_dm_target flakey`
- Line 31: `_scratch_mkfs >>$seqres.full 2>&1`
- Line 34: `_scratch_mount`
- Line 37: `mkdir $SCRATCH_MNT/x`
- Line 38: `mkdir $SCRATCH_MNT/y`
- Line 39: `touch $SCRATCH_MNT/x/foo`
- Line 40: `mkdir $SCRATCH_MNT/y/z`
- Line 41: `touch $SCRATCH_MNT/y/foo2`
- Line 44: `_scratch_sync`
- Line 50: `ln $SCRATCH_MNT/x/foo $SCRATCH_MNT/x/bar`
- Line 51: `mv $SCRATCH_MNT/y/z $SCRATCH_MNT/x/z`
- Line 59: `_scratch_unmount`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. dm-flakey is used to simulate a dropped write / power-fail boundary and then remount for recovery checks. Temporary files are rooted at `$tmp.*` and removed by the local or default cleanup path. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `metadata`, `log`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/dmflakey`, and uses capability gates such as `_require_scratch`, `_require_hardlinks`, `_require_dm_target flakey`, `_require_metadata_journaling $SCRATCH_DEV`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Direct I/O paths can be affected by device sector size, alignment, cache invalidation, and filesystem-specific serialization between buffered and direct writes.
- Crash-recovery tests require dm-flakey behavior and metadata journaling; failures can appear as lost directory entries, stale content, or mount-time recovery errors.
- Thin-provisioning tests depend on device-mapper target behavior, pool exhaustion semantics, and correct cleanup of temporary block devices.

## Test Signals

The pass signal is silence from the helper program and final `status=0`. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/343 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/344 -->
# sources/test-tools/xfstests/tests/generic/344

## Purpose

Test races between mmap from racing threads when pages are prefaulted, Test races between mmap and buffered writes when pages are prefaulted. It is registered with `_begin_fstest auto mmap` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `344` plus `_begin_fstest auto mmap`. Imported libraries: `. ./common/preamble`. Capability gates: `_require_scratch`, `_require_test_program "holetest"`. Local functions: none. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 26: `status=0`

## Control Flow

The script runs linearly after the harness and requirement checks. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 11: `_begin_fstest auto mmap`
- Line 15: `_require_scratch`
- Line 16: `_require_test_program "holetest"`
- Line 18: `_scratch_mkfs >>$seqres.full 2>&1`
- Line 19: `_scratch_mount`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `mmap`, imports `. ./common/preamble`, and uses capability gates such as `_require_scratch`, `_require_test_program "holetest"`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- mmap tests rely on page-cache writeback, timestamp granularity, and correct handling of dirty mappings across fsync, sync, or remount boundaries.

## Test Signals

The pass signal is silence from the helper program and final `status=0`. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/344 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/345 -->
# sources/test-tools/xfstests/tests/generic/345

## Purpose

Test races between mmap from racing processes with and without prefaulting. It is registered with `_begin_fstest auto mmap` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `345` plus `_begin_fstest auto mmap`. Imported libraries: `. ./common/preamble`. Capability gates: `_require_scratch`, `_require_test_program "holetest"`. Local functions: none. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 25: `status=0`

## Control Flow

The script runs linearly after the harness and requirement checks. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 10: `_begin_fstest auto mmap`
- Line 14: `_require_scratch`
- Line 15: `_require_test_program "holetest"`
- Line 17: `_scratch_mkfs >>$seqres.full 2>&1`
- Line 18: `_scratch_mount`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `mmap`, imports `. ./common/preamble`, and uses capability gates such as `_require_scratch`, `_require_test_program "holetest"`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- mmap tests rely on page-cache writeback, timestamp granularity, and correct handling of dirty mappings across fsync, sync, or remount boundaries.

## Test Signals

The pass signal is silence from the helper program and final `status=0`. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/345 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/346 -->
# sources/test-tools/xfstests/tests/generic/346

## Purpose

Test races between mmap and normal writes from racing threads. It is registered with `_begin_fstest auto quick rw mmap` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `346` plus `_begin_fstest auto quick rw mmap`. Imported libraries: `. ./common/preamble`. Capability gates: `_require_scratch`, `_require_test_program "holetest"`. Local functions: none. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 24: `status=0`

## Control Flow

The script runs linearly after the harness and requirement checks. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 10: `_begin_fstest auto quick rw mmap`
- Line 14: `_require_scratch`
- Line 15: `_require_test_program "holetest"`
- Line 17: `_scratch_mkfs >>$seqres.full 2>&1`
- Line 18: `_scratch_mount`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `rw`, `mmap`, imports `. ./common/preamble`, and uses capability gates such as `_require_scratch`, `_require_test_program "holetest"`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- mmap tests rely on page-cache writeback, timestamp granularity, and correct handling of dirty mappings across fsync, sync, or remount boundaries.

## Test Signals

The pass signal is silence from the helper program and final `status=0`. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/346 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/347 -->
# sources/test-tools/xfstests/tests/generic/347

## Purpose

Test very basic thin device usage, exhaustion, and growth. It is registered with `_begin_fstest auto quick rw thin` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `347` plus `_begin_fstest auto quick rw thin`. Imported libraries: `. ./common/preamble`, `. ./common/dmthin`. Capability gates: `_require_scratch_nocheck`, `_require_dm_target thin-pool`. Local functions: `_cleanup`, `_setup_thin`, `_workout`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 13: `BACKING_SIZE=$((500 * 1024 * 1024 / 512)) # 500M`
- Line 14: `VIRTUAL_SIZE=$((10 * $BACKING_SIZE)) # 5000M`
- Line 15: `GROW_SIZE=$((100 * 1024 * 1024 / 512)) # 100M`
- Line 62: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 60 `echo "=== completed"`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 20: `_dmthin_cleanup`
- Line 21: `rm -f $tmp.*`
- Line 26: `_dmthin_init $BACKING_SIZE $VIRTUAL_SIZE`
- Line 27: `_dmthin_set_queue`
- Line 28: `_dmthin_mkfs`
- Line 29: `_dmthin_mount`
- Line 36: `$XFS_IO_PROG -f -c "pwrite -W 0 1M" $SCRATCH_MNT/file$I &>/dev/null`
- Line 39: `_scratch_sync`
- Line 41: `_dmthin_grow $GROW_SIZE`
- Line 45: `$XFS_IO_PROG -f -c "pwrite 0 1M" $SCRATCH_MNT/file$I &>/dev/null`
- Line 52: `_require_scratch_nocheck`
- Line 53: `_require_dm_target thin-pool`
- Line 57: `_dmthin_check_fs`
- Line 58: `_dmthin_cleanup`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Temporary files are rooted at `$tmp.*` and removed by the local or default cleanup path. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `rw`, `thin`, imports `. ./common/preamble`, `. ./common/dmthin`, and uses capability gates such as `_require_scratch_nocheck`, `_require_dm_target thin-pool`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Thin-provisioning tests depend on device-mapper target behavior, pool exhaustion semantics, and correct cleanup of temporary block devices.

## Test Signals

The pass signal is silence from the helper program and final `status=0`. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/347 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/348 -->
# sources/test-tools/xfstests/tests/generic/348

## Purpose

Test creating a symlink, fsync its parent directory, power fail and mount again the filesystem. After these steps the symlink should exist and its content must match what we specified when we created it (must not be empty or point to something else). It is registered with `_begin_fstest auto quick metadata` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `348` plus `_begin_fstest auto quick metadata`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/dmflakey`. Capability gates: `_require_scratch`, `_require_symlinks`, `_require_dm_target flakey`, `_require_metadata_journaling $SCRATCH_DEV`. Local functions: `_cleanup`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 58: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 53 `echo "Symlink contents after log replay:"`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 20: `rm -f $tmp.*`
- Line 27: `_require_scratch`
- Line 29: `_require_dm_target flakey`
- Line 31: `_scratch_mkfs >>$seqres.full 2>&1`
- Line 34: `_scratch_mount`
- Line 36: `mkdir $SCRATCH_MNT/testdir1`
- Line 38: `_scratch_sync`
- Line 43: `ln -s $SCRATCH_MNT/foo1 $SCRATCH_MNT/testdir1/bar1`
- Line 44: `$XFS_IO_PROG -c fsync $SCRATCH_MNT/testdir1`
- Line 45: `mkdir $SCRATCH_MNT/testdir2`
- Line 46: `ln -s $SCRATCH_MNT/foo2 $SCRATCH_MNT/testdir2/bar2`
- Line 47: `$XFS_IO_PROG -c fsync $SCRATCH_MNT/testdir2`
- Line 51: `_flakey_drop_and_remount`
- Line 57: `_scratch_unmount`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. dm-flakey is used to simulate a dropped write / power-fail boundary and then remount for recovery checks. Temporary files are rooted at `$tmp.*` and removed by the local or default cleanup path. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `metadata`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/dmflakey`, and uses capability gates such as `_require_scratch`, `_require_symlinks`, `_require_dm_target flakey`, `_require_metadata_journaling $SCRATCH_DEV`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Direct I/O paths can be affected by device sector size, alignment, cache invalidation, and filesystem-specific serialization between buffered and direct writes.
- Crash-recovery tests require dm-flakey behavior and metadata journaling; failures can appear as lost directory entries, stale content, or mount-time recovery errors.
- Thin-provisioning tests depend on device-mapper target behavior, pool exhaustion semantics, and correct cleanup of temporary block devices.
- Symlink persistence tests are metadata-focused and can fail through lost directory updates, wrong target payloads, or fast/slow symlink representation differences.

## Test Signals

The pass signal is symlink target reads. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/348 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/349 -->
# sources/test-tools/xfstests/tests/generic/349

## Purpose

Test fallocate(ZERO_RANGE) on a block device, which should be able to WRITE SAME (or equivalent) the range. It is registered with `_begin_fstest blockdev rw zero` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `349` plus `_begin_fstest blockdev rw zero`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/scsi_debug`. Capability gates: `_require_scsi_debug`, `_require_xfs_io_command "fzero"`. Local functions: none. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 23: `dev=$(_get_scsi_debug_dev 512 512 0 4 "lbpws=1 lbpws10=1")`
- Line 40: `zod=$(_get_max_lfs_filesize)`
- Line 50: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 22 `echo "Create and format"`, line 26 `echo "Zero range"`, line 29 `echo "Zero range without keep_size"`, line 32 `echo "Zero range past EOD"`. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 20: `_require_xfs_io_command "fzero"`
- Line 24: `_pwrite_byte 0x62 0 4m $dev >> $seqres.full`
- Line 27: `$XFS_IO_PROG -c "fzero -k 512k 1m" $dev`
- Line 30: `$XFS_IO_PROG -c "fzero 384k 64k" $dev`
- Line 33: `$XFS_IO_PROG -c "fzero -k 3m 4m" $dev`
- Line 36: `md5sum $dev | sed -e "s|$dev|SCSI_DEBUG_DEV|g"`
- Line 41: `$XFS_IO_PROG -c "fzero -k 0 $zod" $dev`
- Line 44: `md5sum $dev | sed -e "s|$dev|SCSI_DEBUG_DEV|g"`

## State and Persistence Behavior

The script has little persistent state beyond the files it creates and the xfstests result logs. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `blockdev`, `rw`, `zero`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/scsi_debug`, and uses capability gates such as `_require_scsi_debug`, `_require_xfs_io_command "fzero"`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Block-device fallocate tests rely on scsi_debug discard/write-same emulation and logical-sector alignment, not normal mounted filesystem behavior.

## Test Signals

The pass signal is filtered `md5sum` output. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/349 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/350 -->
# sources/test-tools/xfstests/tests/generic/350

## Purpose

Test fallocate(PUNCH_HOLE) on a block device, which should be able to zero-TRIM (or equivalent) the range. It is registered with `_begin_fstest blockdev rw punch` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `350` plus `_begin_fstest blockdev rw punch`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/scsi_debug`. Capability gates: `_require_scsi_debug`, `_require_xfs_io_command "fpunch"`. Local functions: none. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 23: `dev=$(_get_scsi_debug_dev 512 512 0 4 "lbpws=1 lbpws10=1")`
- Line 37: `zod=$(_get_max_lfs_filesize)`
- Line 47: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 22 `echo "Create and format"`, line 26 `echo "Zero punch"`, line 29 `echo "Punch range past EOD"`, line 32 `echo "Check contents"`. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 20: `_require_xfs_io_command "fpunch"`
- Line 24: `_pwrite_byte 0x62 0 4m $dev >> $seqres.full`
- Line 27: `$XFS_IO_PROG -c "fpunch 512k 1m" $dev`
- Line 30: `$XFS_IO_PROG -c "fpunch 3m 4m" $dev`
- Line 33: `md5sum $dev | sed -e "s|$dev|SCSI_DEBUG_DEV|g"`
- Line 38: `$XFS_IO_PROG -c "fpunch 0 $zod" $dev`
- Line 41: `md5sum $dev | sed -e "s|$dev|SCSI_DEBUG_DEV|g"`

## State and Persistence Behavior

The script has little persistent state beyond the files it creates and the xfstests result logs. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `blockdev`, `rw`, `punch`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/scsi_debug`, and uses capability gates such as `_require_scsi_debug`, `_require_xfs_io_command "fpunch"`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Block-device fallocate tests rely on scsi_debug discard/write-same emulation and logical-sector alignment, not normal mounted filesystem behavior.

## Test Signals

The pass signal is filtered `md5sum` output. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/350 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/351 -->
# sources/test-tools/xfstests/tests/generic/351

## Purpose

Test the unsupported fallocate flags on a block device. No collapse or insert range, no regular fallocate, no forgetting keep-space on zero range, no punching past EOD, no requests that aren't aligned with the logicalsector size, and make sure the fallbacks work for devices that don't support write_same or discard. It is registered with `_begin_fstest blockdev rw punch collapse insert zero prealloc` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `351` plus `_begin_fstest blockdev rw punch collapse insert zero prealloc`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/scsi_debug`. Capability gates: `_require_scsi_debug`, `_require_xfs_io_command "falloc"`, `_require_xfs_io_command "finsert"`, `_require_xfs_io_command "fcollapse"`, `_require_xfs_io_command "fzero"`, `_require_xfs_io_command "fpunch"`. Local functions: none. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 30: `dev=$(_get_scsi_debug_dev 4096 4096 0 4 "lbpws=1 lbpws10=1")`
- Line 51: `zod=$(_get_max_lfs_filesize)`
- Line 73: `dev=$(_get_scsi_debug_dev 512 512 0 4 "lbpws=0 lbpws10=0 lbpu=0 write_same_length=0 unmap_max_blocks=0")`
- Line 90: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 29 `echo "Create and format"`, line 34 `echo "Regular fallocate"`, line 37 `echo "Insert range"`, line 40 `echo "Collapse range"`. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 23: `_require_xfs_io_command "falloc"`
- Line 26: `_require_xfs_io_command "fzero"`
- Line 27: `_require_xfs_io_command "fpunch"`
- Line 31: `_pwrite_byte 0x62 0 4m $dev >> $seqres.full`
- Line 32: `$XFS_IO_PROG -c "fsync" $dev`
- Line 34: `echo "Regular fallocate"`
- Line 35: `$XFS_IO_PROG -c "falloc 64k 64k" $dev`
- Line 38: `$XFS_IO_PROG -c "finsert 128k 64k" $dev`
- Line 41: `$XFS_IO_PROG -c "fcollapse 256k 64k" $dev`
- Line 44: `$XFS_IO_PROG -c "fzero -k 512 512" $dev`
- Line 47: `$XFS_IO_PROG -c "fpunch 512 512" $dev`
- Line 52: `$XFS_IO_PROG -c "fzero -k 512k $zod" $dev`
- Line 55: `$XFS_IO_PROG -c "fzero 512k $zod" $dev`
- Line 84: `md5sum $dev | sed -e "s|$dev|SCSI_DEBUG_DEV|g"`

## State and Persistence Behavior

The script has little persistent state beyond the files it creates and the xfstests result logs. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `blockdev`, `rw`, `punch`, `collapse`, `insert`, `zero`, `prealloc`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/scsi_debug`, and uses capability gates such as `_require_scsi_debug`, `_require_xfs_io_command "falloc"`, `_require_xfs_io_command "finsert"`, `_require_xfs_io_command "fcollapse"`, `_require_xfs_io_command "fzero"`, `_require_xfs_io_command "fpunch"`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Block-device fallocate tests rely on scsi_debug discard/write-same emulation and logical-sector alignment, not normal mounted filesystem behavior.

## Test Signals

The pass signal is filtered `md5sum` output. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/351 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/352 -->
# sources/test-tools/xfstests/tests/generic/352

## Purpose

Test fiemap ioctl on heavily deduped file This test case will check if reserved extent map searching go without problem and return correct SHARED flag Which btrfs will soft lock up and return wrong shared flag Modify as appropriate The size is too small, this will result in an inline extent and then reflink will simply be a copy on btrfs, so exclude compression. It is registered with `_begin_fstest auto clone fiemap` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `352` plus `_begin_fstest auto clone fiemap`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`, `. ./common/punch`. Capability gates: `_require_scratch_reflink`, `_require_xfs_io_command "fiemap"`, `_require_no_compress`, `_require_congruent_file_oplen $SCRATCH_MNT $blocksize`. Local functions: none. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 33: `blocksize=$(_get_file_block_size $SCRATCH_MNT)`
- Line 35: `file="$SCRATCH_MNT/tmp"`
- Line 39: `orig_nr=8192`
- Line 40: `orig_blocksize=4096`
- Line 41: `orig_last_extent=$(($orig_nr * $orig_blocksize / 512))`
- Line 42: `orig_end=$(($orig_last_extent + $orig_blocksize / 512 - 1))`
- Line 45: `nr=$(($orig_nr * $LOAD_FACTOR))`
- Line 46: `last_extent=$(($nr * $blocksize / 512))`

## Control Flow

The script runs linearly after the harness and requirement checks. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 14: `_begin_fstest auto clone fiemap`
- Line 23: `_require_scratch_reflink`
- Line 24: `_require_xfs_io_command "fiemap"`
- Line 30: `_scratch_mkfs > /dev/null 2>&1`
- Line 31: `_scratch_mount`
- Line 50: `_pwrite_byte 0xcdcdcdcd 0 $blocksize $file > /dev/null`
- Line 55: `_reflink_range $file 0 $file $(($i * $blocksize)) $blocksize > /dev/null`
- Line 60: `$XFS_IO_PROG -c "fiemap -v" $file | _filter_fiemap_flags > $tmp.out`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Temporary files are rooted at `$tmp.*` and removed by the local or default cleanup path. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `clone`, `fiemap`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`, `. ./common/punch`, and uses capability gates such as `_require_scratch_reflink`, `_require_xfs_io_command "fiemap"`, `_require_no_compress`, `_require_congruent_file_oplen $SCRATCH_MNT $blocksize`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Reflink coverage is sensitive to extent alignment, delayed allocation, unwritten extents, and page-size dependent block geometry, so comparisons against check files are the main correctness guard.
- Extent-map output is formatted and filtered, but the test still depends on stable extent flags, logical block addressing, and filesystem support for the ioctl under test.

## Test Signals

The pass signal is filtered extent-map output. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/352 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/353 -->
# sources/test-tools/xfstests/tests/generic/353

## Purpose

Check if fiemap ioctl returns correct SHARED flag on reflinked file before and after sync the fs Btrfs has a bug in checking shared extent, which can only handle metadata already committed to disk, but not delayed extent tree modification This caused SHARED flag only occurs after sync Modify as appropriate. It is registered with `_begin_fstest auto quick clone fiemap` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `353` plus `_begin_fstest auto quick clone fiemap`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`, `. ./common/punch`. Capability gates: `_require_scratch_reflink`, `_require_xfs_io_command "fiemap"`. Local functions: none. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 30: `blocksize=$(_get_file_block_size $SCRATCH_MNT)`
- Line 32: `file1="$SCRATCH_MNT/file1"`
- Line 33: `file2="$SCRATCH_MNT/file2"`
- Line 34: `extmap1="$SCRATCH_MNT/extmap1"`
- Line 35: `extmap2="$SCRATCH_MNT/extmap2"`
- Line 60: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 57 `echo "Silence is golden"`. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 15: `_begin_fstest auto quick clone fiemap`
- Line 24: `_require_scratch_reflink`
- Line 25: `_require_xfs_io_command "fiemap"`
- Line 27: `_scratch_mkfs > /dev/null 2>&1`
- Line 28: `_scratch_mount`
- Line 38: `_pwrite_byte 0xcdcdcdcd 0 $blocksize $file1 > /dev/null`
- Line 41: `_reflink_range $file1 0 $file2 0 $blocksize > /dev/null`
- Line 44: `$XFS_IO_PROG -c "fiemap -v" $file1 | _filter_fiemap_flags > $extmap1`
- Line 45: `$XFS_IO_PROG -c "fiemap -v" $file2 | _filter_fiemap_flags > $extmap2`
- Line 47: `cmp -s $extmap1 $extmap2 || echo "mismatched extent maps before sync"`
- Line 51: `_scratch_sync`
- Line 52: `$XFS_IO_PROG -c "fiemap -v" $file1 | _filter_fiemap_flags > $extmap1`
- Line 53: `$XFS_IO_PROG -c "fiemap -v" $file2 | _filter_fiemap_flags > $extmap2`
- Line 55: `cmp -s $extmap1 $extmap2 || echo "mismatched extent maps after sync"`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `clone`, `fiemap`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`, `. ./common/punch`, and uses capability gates such as `_require_scratch_reflink`, `_require_xfs_io_command "fiemap"`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Reflink coverage is sensitive to extent alignment, delayed allocation, unwritten extents, and page-size dependent block geometry, so comparisons against check files are the main correctness guard.
- Extent-map output is formatted and filtered, but the test still depends on stable extent flags, logical block addressing, and filesystem support for the ioctl under test.

## Test Signals

The pass signal is byte-for-byte `cmp` checks against companion files, filtered extent-map output. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/353 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/354 -->
# sources/test-tools/xfstests/tests/generic/354

## Purpose

Test races between private file mapping faults from racing processes or threads. It is registered with `_begin_fstest auto` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `354` plus `_begin_fstest auto`. Imported libraries: `. ./common/preamble`. Capability gates: `_require_scratch`, `_require_test_program "holetest"`. Local functions: none. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 26: `status=0`

## Control Flow

The script runs linearly after the harness and requirement checks. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 15: `_require_scratch`
- Line 16: `_require_test_program "holetest"`
- Line 18: `_scratch_mkfs >>$seqres.full 2>&1`
- Line 19: `_scratch_mount`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, imports `. ./common/preamble`, and uses capability gates such as `_require_scratch`, `_require_test_program "holetest"`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- The main risk is environment drift: missing helper binaries, unsupported filesystem operations, or output formatting changes can make the test skip or fail without indicating a filesystem regression.

## Test Signals

The pass signal is silence from the helper program and final `status=0`. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/354 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/355 -->
# sources/test-tools/xfstests/tests/generic/355

## Purpose

Test clear of suid/sgid on direct write create testfile and set base ownership & permission. It is registered with `_begin_fstest auto quick perms` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `355` plus `_begin_fstest auto quick perms`. Imported libraries: `. ./common/preamble`, `. ./common/filter`. Capability gates: `_require_test`, `_require_user`, `_require_odirect`, `_require_chown`. Local functions: `do_io`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 20: `testfile=$TEST_DIR/$seq.test`
- Line 65: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 29 `echo "Check that suid/sgid bits are cleared after direct write"`, line 32 `echo "this is a test" >> $testfile`, line 36 `echo "== with no exec perm"`, line 38 `echo -n "before: "; stat -c '%A' $testfile`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 15: `_require_test`
- Line 18: `_require_chown`
- Line 21: `rm -f $testfile`
- Line 25: `_su $qa_user -c "$XFS_IO_PROG -d -c 'pwrite 0 4k' $testfile" \`
- Line 33: `chmod 644 $testfile`
- Line 34: `chown $qa_user:$qa_user $testfile`
- Line 37: `chmod ug+s $testfile`
- Line 38: `echo -n "before: "; stat -c '%A' $testfile`
- Line 40: `echo -n "after: "; stat -c '%A' $testfile`
- Line 43: `chmod ug+s $testfile`
- Line 44: `chmod u+x $testfile`
- Line 45: `echo -n "before: "; stat -c '%A' $testfile`
- Line 47: `echo -n "after: "; stat -c '%A' $testfile`
- Line 62: `echo -n "after: "; stat -c '%A' $testfile`

## State and Persistence Behavior

Primary state lives under `$TEST_DIR`, making this a test-device workload rather than a scratch-device destructive test. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `perms`, imports `. ./common/preamble`, `. ./common/filter`, and uses capability gates such as `_require_test`, `_require_user`, `_require_odirect`, `_require_chown`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Direct I/O paths can be affected by device sector size, alignment, cache invalidation, and filesystem-specific serialization between buffered and direct writes.

## Test Signals

The pass signal is stat/lstat metadata output. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/355 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/356 -->
# sources/test-tools/xfstests/tests/generic/356

## Purpose

Check that we can't reflink a swapfile. It is registered with `_begin_fstest auto quick clone swap` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `356` plus `_begin_fstest auto quick clone swap`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`. Capability gates: `_require_scratch_swapfile`, `_require_scratch_reflink`, `_require_cp_reflink`. Local functions: `_cleanup`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 34: `testdir=$SCRATCH_MNT/test-$seq`
- Line 37: `blocks=160`
- Line 38: `blksz=65536`
- Line 54: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 30 `echo "Format and mount"`, line 40 `echo "Initialize file"`, line 47 `echo "Try to reflink"`, line 50 `echo "Tear it down"`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 18: `rm -rf $tmp.*`
- Line 26: `_require_scratch_swapfile`
- Line 27: `_require_scratch_reflink`
- Line 28: `_require_cp_reflink`
- Line 30: `echo "Format and mount"`
- Line 31: `_scratch_mkfs > $seqres.full 2>&1`
- Line 32: `_scratch_mount >> $seqres.full 2>&1`
- Line 35: `mkdir $testdir`
- Line 42: `swapon $testdir/file1`
- Line 44: `touch "$testdir/file2"`
- Line 48: `_cp_reflink $testdir/file1 $testdir/file2 2>&1 | _filter_scratch`
- Line 51: `swapoff $testdir/file1`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Swap activation state is external to normal file contents, so cleanup and negative-result filtering are important to avoid leaking an active swapfile. Temporary files are rooted at `$tmp.*` and removed by the local or default cleanup path. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `clone`, `swap`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`, and uses capability gates such as `_require_scratch_swapfile`, `_require_scratch_reflink`, `_require_cp_reflink`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Reflink coverage is sensitive to extent alignment, delayed allocation, unwritten extents, and page-size dependent block geometry, so comparisons against check files are the main correctness guard.
- Swapfile tests depend on kernel restrictions around swap activation, holes, and shared extents; cleanup must avoid leaving swap enabled.

## Test Signals

The pass signal is silence from the helper program and final `status=0`. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/356 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/357 -->
# sources/test-tools/xfstests/tests/generic/357

## Purpose

Check that we can't swapon a reflinked file For NFS, a reflink is just a CLONE operation, and after that point it's dealt with by the server. It is registered with `_begin_fstest auto quick clone swap` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `357` plus `_begin_fstest auto quick clone swap`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`. Capability gates: `_require_scratch_swapfile`, `_require_scratch_reflink`, `_require_cp_reflink`. Local functions: `_cleanup`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 39: `testdir=$SCRATCH_MNT/test-$seq`
- Line 42: `blocks=160`
- Line 43: `blksz=65536`
- Line 57: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 35 `echo "Format and mount"`, line 45 `echo "Initialize file"`, line 51 `echo "Try to swapon"`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 18: `rm -rf $tmp.*`
- Line 31: `_require_scratch_swapfile`
- Line 32: `_require_scratch_reflink`
- Line 33: `_require_cp_reflink`
- Line 35: `echo "Format and mount"`
- Line 36: `_scratch_mkfs > $seqres.full 2>&1`
- Line 37: `_scratch_mount >> $seqres.full 2>&1`
- Line 40: `mkdir $testdir`
- Line 47: `touch "$testdir/file2"`
- Line 49: `_cp_reflink $testdir/file1 $testdir/file2 2>&1 | _filter_scratch`
- Line 51: `echo "Try to swapon"`
- Line 52: `swapon $testdir/file1 2>&1 | _filter_scratch`
- Line 54: `swapoff $testdir/file1 >> $seqres.full 2>&1`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Swap activation state is external to normal file contents, so cleanup and negative-result filtering are important to avoid leaking an active swapfile. Temporary files are rooted at `$tmp.*` and removed by the local or default cleanup path. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `clone`, `swap`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`, and uses capability gates such as `_require_scratch_swapfile`, `_require_scratch_reflink`, `_require_cp_reflink`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Reflink coverage is sensitive to extent alignment, delayed allocation, unwritten extents, and page-size dependent block geometry, so comparisons against check files are the main correctness guard.
- Swapfile tests depend on kernel restrictions around swap activation, holes, and shared extents; cleanup must avoid leaving swap enabled.

## Test Signals

The pass signal is silence from the helper program and final `status=0`. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/357 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/358 -->
# sources/test-tools/xfstests/tests/generic/358

## Purpose

Share an extent amongst a bunch of files such that the refcount stays the same while the rate of change of the set of owners is steadily increasing. For example, an extent of 32 blocks is owned by 32 files. At block 1, change one of the owners. At block 2, change 2 of the owners, and so on. It is registered with `_begin_fstest auto quick clone` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `358` plus `_begin_fstest auto quick clone`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`. Capability gates: `_require_scratch_reflink`, `_require_congruent_file_oplen $SCRATCH_MNT $blksz`. Local functions: `_cleanup`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 36: `testdir=$SCRATCH_MNT/test-$seq`
- Line 39: `blocks=64`
- Line 40: `blksz=65536`
- Line 59: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 32 `echo "Format and mount"`, line 43 `echo "Initialize file"`, line 46 `echo "Share the file n-ways"`, line 55 `echo "Check output"`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 22: `rm -rf $tmp.*`
- Line 30: `_require_scratch_reflink`
- Line 32: `echo "Format and mount"`
- Line 33: `_scratch_mkfs > $seqres.full 2>&1`
- Line 34: `_scratch_mount >> $seqres.full 2>&1`
- Line 37: `mkdir $testdir`
- Line 44: `_pwrite_byte 0x61 0 $((blocks * blksz)) $testdir/file >> $seqres.full`
- Line 48: `_reflink_range $testdir/file 0 $testdir/file$nr.0 0 $((nr * blksz)) >> $seqres.full`
- Line 50: `_reflink_range $testdir/file $((nnr * blksz)) $testdir/file$nr.$nnr $((nnr * blksz)) $blksz >> $seqres.full`
- Line 53: `_scratch_cycle_mount`
- Line 56: `md5sum $testdir/file $testdir/file*.0 | _filter_scratch`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Cycle-mount calls force metadata and extent state through unmount/remount persistence before validation. Temporary files are rooted at `$tmp.*` and removed by the local or default cleanup path. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `clone`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`, and uses capability gates such as `_require_scratch_reflink`, `_require_congruent_file_oplen $SCRATCH_MNT $blksz`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Reflink coverage is sensitive to extent alignment, delayed allocation, unwritten extents, and page-size dependent block geometry, so comparisons against check files are the main correctness guard.

## Test Signals

The pass signal is filtered `md5sum` output. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/358 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/359 -->
# sources/test-tools/xfstests/tests/generic/359

## Purpose

Make sure that the reference counting mechanism can handle the case where we share the first 1/4 of an extent with a file, share the last 1/4 of the extent with a second file, share the first half of the extent with N files, and share the second half of the extent with a different set of N files. The key point here is to test that we handle the case where a refcount extent record doesn't coincide exactly with the block mapping records. It is registered with `_begin_fstest auto quick clone` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `359` plus `_begin_fstest auto quick clone`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`. Capability gates: `_require_scratch_reflink`, `_require_congruent_file_oplen $SCRATCH_MNT $blksz`. Local functions: `_cleanup`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 38: `testdir=$SCRATCH_MNT/test-$seq`
- Line 41: `blocks=64`
- Line 42: `blksz=65536`
- Line 44: `nr=4`
- Line 45: `halfway=$((blocks / 2 * blksz))`
- Line 46: `quarter=$((blocks / 4 * blksz))`
- Line 73: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 34 `echo "Format and mount"`, line 48 `echo "Initialize file"`, line 51 `echo "Share the first half of the extent"`, line 56 `echo "Share the last half of the extent"`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 24: `rm -rf $tmp.*`
- Line 32: `_require_scratch_reflink`
- Line 34: `echo "Format and mount"`
- Line 35: `_scratch_mkfs > $seqres.full 2>&1`
- Line 36: `_scratch_mount >> $seqres.full 2>&1`
- Line 39: `mkdir $testdir`
- Line 49: `_pwrite_byte 0x61 0 $((blocks * blksz)) $testdir/file >> $seqres.full`
- Line 53: `_reflink_range $testdir/file 0 $testdir/file$nr.0 0 $halfway >> $seqres.full`
- Line 58: `_reflink_range $testdir/file $halfway $testdir/file$nr.1 0 $halfway >> $seqres.full`
- Line 62: `_reflink_range $testdir/file 0 $testdir/file.2 0 $quarter >> $seqres.full`
- Line 65: `_reflink_range $testdir/file $((quarter * 3)) $testdir/file.3 0 $quarter >> $seqres.full`
- Line 67: `_scratch_cycle_mount`
- Line 70: `md5sum $testdir/file $testdir/file* | _filter_scratch`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Cycle-mount calls force metadata and extent state through unmount/remount persistence before validation. Temporary files are rooted at `$tmp.*` and removed by the local or default cleanup path. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `clone`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`, and uses capability gates such as `_require_scratch_reflink`, `_require_congruent_file_oplen $SCRATCH_MNT $blksz`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Reflink coverage is sensitive to extent alignment, delayed allocation, unwritten extents, and page-size dependent block geometry, so comparisons against check files are the main correctness guard.

## Test Signals

The pass signal is filtered `md5sum` output. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/359 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/360 -->
# sources/test-tools/xfstests/tests/generic/360

## Purpose

Test symlink to very long path, check symlink file contains correct path Create a symlink points to a very long path, so that the path could not be hold in inode Check symlink contains the correct path 1023 chars are a bit long for golden image output, compute the md5 checksum success, all done. It is registered with `_begin_fstest auto quick metadata` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `360` plus `_begin_fstest auto quick metadata`. Imported libraries: `. ./common/preamble`, `. ./common/filter`. Capability gates: `_require_test`, `_require_symlinks`. Local functions: none. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 18: `linkfile=$TEST_DIR/$seq.symlink`
- Line 21: `FNAME=$(perl -e 'print "a"x254')`
- Line 32: `status=0`

## Control Flow

The script runs linearly after the harness and requirement checks. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 15: `_require_test`
- Line 19: `rm -f $linkfile`
- Line 25: `ln -s $FNAME/$FNAME/$FNAME/$FNAME $linkfile`
- Line 29: `readlink $linkfile | md5sum`

## State and Persistence Behavior

Primary state lives under `$TEST_DIR`, making this a test-device workload rather than a scratch-device destructive test. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `metadata`, imports `. ./common/preamble`, `. ./common/filter`, and uses capability gates such as `_require_test`, `_require_symlinks`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Symlink persistence tests are metadata-focused and can fail through lost directory updates, wrong target payloads, or fast/slow symlink representation differences.

## Test Signals

The pass signal is filtered `md5sum` output, symlink target reads. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/360 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/361 -->
# sources/test-tools/xfstests/tests/generic/361

## Purpose

Test remount on I/O errors XFS had a bug to hang on remount in this case, this kernel commit fix the issue 5cb13dc cancel the setfilesize transation when io error happen create a small filesystem to hold another filesystem image. It is registered with `_begin_fstest auto quick` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `361` plus `_begin_fstest auto quick`. Imported libraries: `. ./common/preamble`, `. ./common/filter`. Capability gates: `_require_scratch`, `_require_block_device $SCRATCH_DEV`, `_require_loop`, `_require_sparse_files`. Local functions: `_cleanup`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 38: `fs_img=$SCRATCH_MNT/fs.img`
- Line 39: `fs_mnt=$SCRATCH_MNT/mnt`
- Line 44: `loop_dev=$(_create_loop_device $fs_img)`
- Line 49: `dname=$(_short_dev $loop_dev)`
- Line 63: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 50 `echo 0 | tee /sys/fs/xfs/$dname/error/*/*/* > /dev/null`, line 62 `echo "Silence is golden"`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 19: `_unmount $fs_mnt &>> /dev/null`
- Line 22: `rm -f $tmp.*`
- Line 28: `_require_scratch`
- Line 34: `_scratch_mkfs_sized $((512 * 1024 * 1024)) >>$seqres.full 2>&1`
- Line 35: `_scratch_mount`
- Line 40: `$XFS_IO_PROG -fc "truncate 1g" $fs_img >>$seqres.full 2>&1`
- Line 41: `mkdir -p $fs_mnt`
- Line 46: `_mount -t $FSTYP $loop_dev $fs_mnt`
- Line 52: `$XFS_IO_PROG -fc "pwrite 0 520m" $fs_mnt/testfile >>$seqres.full 2>&1`
- Line 55: `$MOUNT_PROG -o remount,ro $fs_mnt >>$seqres.full 2>&1`
- Line 57: `_unmount $fs_mnt &>/dev/null`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Temporary files are rooted at `$tmp.*` and removed by the local or default cleanup path. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, imports `. ./common/preamble`, `. ./common/filter`, and uses capability gates such as `_require_scratch`, `_require_block_device $SCRATCH_DEV`, `_require_loop`, `_require_sparse_files`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- The main risk is environment drift: missing helper binaries, unsupported filesystem operations, or output formatting changes can make the test skip or fail without indicating a filesystem regression.

## Test Signals

The pass signal is silence from the helper program and final `status=0`. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/361 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/362 -->
# sources/test-tools/xfstests/tests/generic/362

## Purpose

Test that doing a direct IO append write to a file when the input buffer was not yet faulted in, does not result in an incorrect file size NFS forbade open with O_APPEND|O_DIRECT On error the test program writes messages to stderr, causing a golden output mismatch and making the test fail success, all done. It is registered with `_begin_fstest auto quick` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `362` plus `_begin_fstest auto quick`. Imported libraries: `. ./common/preamble`. Capability gates: `_require_test`, `_require_odirect`, `_require_test_program dio-append-buf-fault`. Local functions: none. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 29: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 28 `echo "Silence is golden"`. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 16: `_require_test`
- Line 18: `_require_test_program dio-append-buf-fault`

## State and Persistence Behavior

Primary state lives under `$TEST_DIR`, making this a test-device workload rather than a scratch-device destructive test. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, imports `. ./common/preamble`, and uses capability gates such as `_require_test`, `_require_odirect`, `_require_test_program dio-append-buf-fault`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Direct I/O paths can be affected by device sector size, alignment, cache invalidation, and filesystem-specific serialization between buffered and direct writes.

## Test Signals

The pass signal is silence from the helper program and final `status=0`. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/362 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/363 -->
# sources/test-tools/xfstests/tests/generic/363

## Purpose

Run fsx with EOF pollution enabled. This provides test coverage for partial EOF page/block zeroing for operations that change file size on failure, replace -q with -d to see post-eof writes in the dump output. It is registered with `_begin_fstest rw auto` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `363` plus `_begin_fstest rw auto`. Imported libraries: `. ./common/preamble`. Capability gates: `_require_test`. Local functions: none. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 24: `status=0`

## Control Flow

The script runs linearly after the harness and requirement checks. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 14: `_require_test`
- Line 22: `run_fsx "-q -S 0 -e 1 -N 100000"`

## State and Persistence Behavior

The script has little persistent state beyond the files it creates and the xfstests result logs. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `rw`, `auto`, imports `. ./common/preamble`, and uses capability gates such as `_require_test`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Direct I/O paths can be affected by device sector size, alignment, cache invalidation, and filesystem-specific serialization between buffered and direct writes.
- Stress tests are randomized or high-iteration workloads, so seeds, scaling helpers, timeouts, and captured stderr are important for reproducibility.

## Test Signals

The pass signal is stress-tool exit status and captured logs. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/363 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/364 -->
# sources/test-tools/xfstests/tests/generic/364

## Purpose

Test that a program that has 2 threads using the same file descriptor and concurrently doing direct IO writes and fsync doesn't trigger any crash or deadlock Triggers very frequently with kernel config CONFIG_BTRFS_ASSERT=y On error the test program writes messages to stderr, causing a golden output mismatch and making the test fail success, all done. It is registered with `_begin_fstest auto quick` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `364` plus `_begin_fstest auto quick`. Imported libraries: `. ./common/preamble`. Capability gates: `_require_test`, `_require_odirect`, `_require_test_program dio-write-fsync-same-fd`, `_require_command "$TIMEOUT_PROG" timeout`. Local functions: none. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 29: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 28 `echo "Silence is golden"`. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 14: `_require_test`
- Line 16: `_require_test_program dio-write-fsync-same-fd`
- Line 21: `"btrfs: fix race between direct IO write and fsync when using same fd"`
- Line 25: `$TIMEOUT_PROG 10s $here/src/dio-write-fsync-same-fd $TEST_DIR/dio-write-fsync-same-fd`

## State and Persistence Behavior

Primary state lives under `$TEST_DIR`, making this a test-device workload rather than a scratch-device destructive test. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, imports `. ./common/preamble`, and uses capability gates such as `_require_test`, `_require_odirect`, `_require_test_program dio-write-fsync-same-fd`, `_require_command "$TIMEOUT_PROG" timeout`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Direct I/O paths can be affected by device sector size, alignment, cache invalidation, and filesystem-specific serialization between buffered and direct writes.

## Test Signals

The pass signal is silence from the helper program and final `status=0`. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/364 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/365 -->
# sources/test-tools/xfstests/tests/generic/365

## Purpose

Regression test for sub-fsblock key handling errors in GETFSMAP This makes sure there is free space surrounded by allocated blocks, which is needed for some sub tests. It is registered with `_begin_fstest auto rmap fsmap` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `365` plus `_begin_fstest auto rmap fsmap`. Imported libraries: `. ./common/preamble`, `. ./common/filter`. Capability gates: `_require_xfs_io_command "fsmap"`, `_require_xfs_io_command "falloc"`, `_require_xfs_io_command "fpunch"`, `_require_scratch`. Local functions: `find_freesp`, `filter_fsmap`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 29: `blksz=$(_get_block_size "$SCRATCH_MNT")`
- Line 56: `freesp="$(find_freesp)"`
- Line 58: `freesp_start="$(echo "$freesp" | cut -d ':' -f 1)"`
- Line 59: `freesp_end="$(echo "$freesp" | cut -d ':' -f 2)"`
- Line 86: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 60 `echo "$freesp:$freesp_start:$freesp_end" >> $seqres.full`, line 62 `echo "test incorrect setting of high key"`, line 65 `echo "test missing free space extent"`, line 69 `echo "test whatever came before freesp"`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 10: `_begin_fstest auto rmap fsmap`
- Line 13: `"xfs: Fix the owner setting issue for rmap query in xfs fsmap"`
- Line 15: `"xfs: Fix missing interval for missing_owner in xfs fsmap"`
- Line 21: `_require_xfs_io_command "fsmap"`
- Line 22: `_require_xfs_io_command "falloc"`
- Line 23: `_require_xfs_io_command "fpunch"`
- Line 24: `_require_scratch`
- Line 26: `_scratch_mkfs >> $seqres.full`
- Line 27: `_scratch_mount`
- Line 36: `$XFS_IO_PROG -fc 'falloc 0 3M' -c 'fpunch 1M 1M' -c 'fsync' $SCRATCH_MNT/f`
- Line 38: `$XFS_IO_PROG -c 'fsmap' $SCRATCH_MNT >> $seqres.full`
- Line 41: `$XFS_IO_PROG -c 'fsmap -d' $SCRATCH_MNT | tr '.[]:' ' ' | \`
- Line 46: `filter_fsmap() {`
- Line 83: `filter_fsmap`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `rmap`, `fsmap`, imports `. ./common/preamble`, `. ./common/filter`, and uses capability gates such as `_require_xfs_io_command "fsmap"`, `_require_xfs_io_command "falloc"`, `_require_xfs_io_command "fpunch"`, `_require_scratch`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Direct I/O paths can be affected by device sector size, alignment, cache invalidation, and filesystem-specific serialization between buffered and direct writes.
- Extent-map output is formatted and filtered, but the test still depends on stable extent flags, logical block addressing, and filesystem support for the ioctl under test.
- Several checks can intentionally call `_notrun`; this is expected for unsupported geometry or feature combinations and should be distinguished from a failing assertion.

## Test Signals

The pass signal is filtered extent-map output. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/365 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/366 -->
# sources/test-tools/xfstests/tests/generic/366

## Purpose

Test if mixed direct read, direct write and buffered write on the same file will hang the filesystem This is exposed by an incoming btrfs feature, which allows a folio to be partial uptodate if the buffered write range is block aligned but not yet full folio aligned Such behavior makes btrfs to hang reliably under generic/095 This is the extracted minimal reproducer for 4k block size and 64K page size. It is registered with `_begin_fstest auto quick rw` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `366` plus `_begin_fstest auto quick rw`. Imported libraries: `. ./common/preamble`, `. ./common/filter`. Capability gates: `_require_scratch`, `_require_odirect 512 # see fio job1 config below`, `_require_aio`, `_require_fio $fio_config`. Local functions: none. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 29: `iterations=$((32 * LOAD_FACTOR))`
- Line 31: `fio_config=$tmp.fio`
- Line 32: `fio_out=$tmp.fio.out`
- Line 33: `blksz=`$here/src/min_dio_alignment $SCRATCH_MNT $SCRATCH_DEV``
- Line 36: `bs=8k`
- Line 37: `iodepth=1`
- Line 38: `randrepeat=1`
- Line 39: `size=256k`

## Control Flow

The visible phases are driven by echo markers such as line 98 `echo "=== fio $i/$iterations ===" >> $seqres.full`, line 102 `echo "Silence is golden"`. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 22: `_require_scratch`
- Line 23: `_require_odirect 512 # see fio job1 config below`
- Line 31: `fio_config=$tmp.fio`
- Line 32: `fio_out=$tmp.fio.out`
- Line 34: `cat >$fio_config <<EOF`
- Line 43: `ioengine=sync`
- Line 58: `_require_fio $fio_config`
- Line 61: `_scratch_mkfs >>$seqres.full 2>&1`
- Line 62: `_scratch_mount`
- Line 92: `$FIO_PROG $fio_config --ignore_error=,EIO --output=$fio_out`
- Line 94: `_scratch_unmount`
- Line 96: `_check_dmesg _filter_aiodio_dmesg`
- Line 98: `echo "=== fio $i/$iterations ===" >> $seqres.full`
- Line 99: `cat $fio_out >> $seqres.full`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Temporary files are rooted at `$tmp.*` and removed by the local or default cleanup path. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `rw`, imports `. ./common/preamble`, `. ./common/filter`, and uses capability gates such as `_require_scratch`, `_require_odirect 512 # see fio job1 config below`, `_require_aio`, `_require_fio $fio_config`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Direct I/O paths can be affected by device sector size, alignment, cache invalidation, and filesystem-specific serialization between buffered and direct writes.

## Test Signals

The pass signal is post-test dmesg scanning, stress-tool exit status and captured logs. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/366 -->
