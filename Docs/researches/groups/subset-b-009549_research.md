# subset-b-009549 research

Grouped research for xfstests generic 618 through 746. Each section preserves the original source path and is wrapped for reconciliation splitting.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/618 -->
# sources/test-tools/xfstests/tests/generic/618

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/618`. Verify that forkoff can be returned as 0 properly if it isn't able to fit inline for XFS. However, this test is fs-neutral and can be done quickly so leave it in generic This test verifies the problem fixed in kernel with commit ada49d64fb35 ("xfs: fix forkoff miscalculation related to XFS_LITINO(mp)") It is registered with `_begin_fstest auto quick attr`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 57 source line(s).
- Harness registration: `_begin_fstest auto quick attr`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/attr`.
- Capability and skip gates: `_require_scratch`, `_require_attrs user`, `_require_no_xfs_bug_on_assert`.
- Local shell functions: none visible.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `MKFS_OPTIONS="$MKFS_OPTIONS -i size=512"`
- `localfile="${SCRATCH_MNT}/testfile"`

## Control Flow

- Capability gating runs first through `_require_scratch`, `_require_attrs user`, `_require_no_xfs_bug_on_assert`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- Key operational lines include:
- `line 35: _scratch_mkfs > $seqres.full 2>&1`
- `line 36: _scratch_mount`
- `line 50: _scratch_cycle_mount`
- `line 53: _getfattr --absolute-names -ebase64 -d $localfile | tail -n +2 | sort`
- `line 55: _scratch_unmount`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Extended attributes are part of the persistent state being created, replayed, or verified. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick attr`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/attr`), and the golden-output file `sources/test-tools/xfstests/tests/generic/618.out` (4 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_scratch`, `_require_attrs user`, `_require_no_xfs_bug_on_assert`.

## Risks and Edge Cases

- Most failures should surface as unexpected output, nonzero helper status, or harness `_fail`/`_notrun` behavior.

## Test Signals

The paired `.out` file has 4 line(s); its first visible signals are: 'QA output created by 618;...'. Runtime pass/fail is also signaled by post-remount or failure-injection persistence checks. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/618 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/619 -->
# sources/test-tools/xfstests/tests/generic/619

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/619`. ENOSPC regression test in a multi-threaded scenario. Test allocation strategies of the file system and validate space anomalies as reported by the system versus the allocated by the program. The test is motivated by a bug in ext4 systems where-in ENOSPC is reported by the file system even though enough space for allocations is available[1]. [1]: https://patchwork.ozlabs.org/patch/1294003 Linux kernel patch series that fixes the above regression: 53f86b170dfa ("ext4: mballoc: add blocks to PA list under same spinlock after allocating blocks") cf5e2ca6c990 ("ext4: mballoc: refactor ext4_mb_discard_preallocations()") 07b5b8e1ac40 ("ext4: mballoc: introduce pcpu seqcnt for freeing PA to improve ENOSPC handling")... It is registered with `_begin_fstest auto rw enospc prealloc`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 189 source line(s).
- Harness registration: `_begin_fstest auto rw enospc prealloc`.
- Imported common libraries: `./common/preamble`, `./common/filter`.
- Capability and skip gates: `_require_scratch`, `_require_test_program "t_enospc"`, `_require_xfs_io_command "falloc"`.
- Local shell functions: `debug`, `calc_thread_cnt`, `run_testcase`.
- External `$here/src` helpers: `$here/src/t_enospc -t $thread_cnt -s $file_ratio_unit -r $file_ratio -p $SCRATCH_MNT $extra_args >> $seqres.full`.
- Notable variables and constants:
- `FS_SIZE=$((240*1024*1024)) # 240MB`
- `DEBUG=1 # set to 0 to disable debug statements in shell and c-prog`
- `FACT=0.7`
- `FALLOCATE=1`
- `FTRUNCATE=2`
- `SMALL_FILE_SIZE=$((512 * 1024)) # in Bytes`
- `BIG_FILE_SIZE=$((1536 * 1024)) # in Bytes`
- `MIX_FILE_SIZE=$((2048 * 1024)) # (BIG + SMALL small file size)`
- `IFS=',' read -ra fratio <<< $file_ratio`
- `file_ratio_cnt=${#fratio[@]}`
- `tot_avail_size=$($DF_PROG --block-size=1 $SCRATCH_MNT | $AWK_PROG 'FNR == 2 { print $5 }')`
- `avail_size=$(echo $tot_avail_size*$disk_saturation | $BC_PROG)`

## Control Flow

- Capability gating runs first through `_require_scratch`, `_require_test_program "t_enospc"`, `_require_xfs_io_command "falloc"`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- User-visible phase markers include:
- `line 53: echo "$1" >> $seqres.full`
- `line 83: echo ${thread_cnt}`
- `line 153: echo "FAIL: Aborted assertion faliure"`
- `line 156: echo "FAIL: ENOSPC BUS faliure"`
- `line 158: echo "$test_name failed at iteration count: $i"`
- `line 159: echo "$($DF_PROG -h $SCRATCH_MNT)"`
- `line 160: echo "Allocated: $alloc_per% Used: $use_per%"`
- `line 187: echo "Silence is golden"`
- Key operational lines include:
- `line 48: _require_xfs_io_command "falloc"`
- `line 134: _scratch_mkfs_sized $FS_SIZE >> $seqres.full 2>&1`
- `line 135: _scratch_mount`
- `line 166: _scratch_unmount`
- `line 175: "Small-file-fallocate-test:$SMALL_FILE_SIZE:1:$FACT:$FALLOCATE:3"`
- `line 176: "Big-file-fallocate-test:$BIG_FILE_SIZE:1:$FACT:$FALLOCATE:3"`
- `line 177: "Mix-file-fallocate-test:$MIX_FILE_SIZE:0.75,0.25:$FACT:$FALLOCATE:3"`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto rw enospc prealloc`, common helper libraries (`./common/preamble`, `./common/filter`), and the golden-output file `sources/test-tools/xfstests/tests/generic/619.out` (2 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_scratch`, `_require_test_program "t_enospc"`, `_require_xfs_io_command "falloc"`.

## Risks and Edge Cases

- ENOSPC-sensitive timing can vary with allocator geometry, free-space accounting, delayed allocation, and background reservations.

## Test Signals

The paired `.out` file has 2 line(s); its first visible signals are: 'QA output created by 619; Silence is golden'. Runtime pass/fail is primarily the command exit status plus golden-output comparison. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/619 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/620 -->
# sources/test-tools/xfstests/tests/generic/620

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/620`. Since the test is not specific to ext4, hence adding it to generic. Add this test to check for regression which was reported when ext4 bmap aops was moved to use iomap APIs. jbd2 calls bmap() kernel function from fs/inode.c which was failing since iomap_bmap() implementation earlier returned 0 for block addr > INT_MAX. This regression was fixed with following kernel commit commit b75dfde1212 ("fibmap: Warn and return an error in case of block > INT_MAX") It is registered with `_begin_fstest auto mount quick`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 53 source line(s).
- Harness registration: `_begin_fstest auto mount quick`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/dmhugedisk`.
- Capability and skip gates: `_require_scratch_size_nocheck $((4 * 1024 * 1024)) #kB`, `_require_scratch_16T_support`, `_require_dmhugedisk`.
- Local shell functions: `_cleanup`.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `sectors=$((2*1024*1024*1024*17))`
- `chunk_size=128`
- `testfile=$SCRATCH_MNT/testfile-$seq`

## Control Flow

- Capability gating runs first through `_require_scratch_size_nocheck $((4 * 1024 * 1024)) #kB`, `_require_scratch_16T_support`, `_require_dmhugedisk`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- Key operational lines include:
- `line 24: _dmhugedisk_cleanup`
- `line 34: _require_scratch_size_nocheck $((4 * 1024 * 1024)) #kB`
- `line 35: _require_scratch_16T_support`
- `line 36: _require_dmhugedisk`
- `line 43: _dmhugedisk_init $sectors $chunk_size`
- `line 44: _mkfs_dev $DMHUGEDISK_DEV`
- `line 45: _mount $DMHUGEDISK_DEV $SCRATCH_MNT || _fail "mount failed for $DMHUGEDISK_DEV $SCRATCH_MNT"`
- `line 48: $XFS_IO_PROG -fc "pwrite -S 0xaa 0 1m" -c "fsync" $testfile | _filter_xfs_io`
- `line 50: _dmhugedisk_cleanup`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Synthetic block-device state can be introduced through device-mapper, loop, SCSI debug, or huge-device helpers and must be cleaned even on failure. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto mount quick`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/dmhugedisk`), and the golden-output file `sources/test-tools/xfstests/tests/generic/620.out` (3 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_scratch_size_nocheck $((4 * 1024 * 1024)) #kB`, `_require_scratch_16T_support`, `_require_dmhugedisk`.

## Risks and Edge Cases

- Most failures should surface as unexpected output, nonzero helper status, or harness `_fail`/`_notrun` behavior.

## Test Signals

The paired `.out` file has 3 line(s); its first visible signals are: 'QA output created by 620; wrote 1048576/1048576 bytes at offset 0; XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec)'. Runtime pass/fail is also signaled by xfstests output filters. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/620 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/621 -->
# sources/test-tools/xfstests/tests/generic/621

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/621`. Test for a race condition where a duplicate filename could be created in an encrypted directory while the directory's encryption key was being added concurrently. This is a regression test for the following kernel commits: 968dd6d0c6d6 ("fscrypt: fix race allowing rename() and link() of ciphertext dentries") 75d18cd1868c ("ext4: prevent creating duplicate encrypted filenames") bfc2b7e85189 ("f2fs: prevent creating duplicate encrypted filenames") 76786a0f0834 ("ubifs: prevent creating duplicate encrypted filenames") The first commit fixed the bug for the rename() and link() syscalls. The others fixed the bug for the other syscalls that create new filenames. Note, the bug wasn't actually reproducible on f2fs.... It is registered with `_begin_fstest auto quick encrypt`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 157 source line(s).
- Harness registration: `_begin_fstest auto quick encrypt`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/encrypt`, `./common/renameat2`.
- Capability and skip gates: `_require_scratch_encryption -v 2`, `_require_renameat2 noreplace`.
- Local shell functions: `_cleanup`.
- External `$here/src` helpers: `if $here/src/renameat2 -n $dir/50 $dir/100 &> /dev/null; then`.
- Notable variables and constants:
- `runtime=$((5 * TIME_FACTOR))`
- `dir=$SCRATCH_MNT/dir`
- `inode=$(stat -c %i $dir/100)`
- `new_inode=$(stat -c %i $dir/100)`

## Control Flow

- Capability gating runs first through `_require_scratch_encryption -v 2`, `_require_renameat2 noreplace`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 62: echo -e "\n# Creating encrypted directory containing files"`
- `line 79: echo -e "\n# Starting duplicate filename creator process"`
- `line 105: echo -e "\n# Starting add/remove enckey process"`
- `line 115: echo -e "\n# Running for a few seconds..."`
- `line 117: echo -e "\n# Stopping subprocesses"`
- `line 126: echo -e "\n# Checking for duplicate filenames via readdir"`
- `line 129: echo -e "\n# Checking for unexpected change in inode number"`
- `line 132: echo "Dentry changed inode number $inode => $new_inode!"`
- Key operational lines include:
- `line 53: _require_scratch_encryption -v 2`
- `line 54: _require_renameat2 noreplace`
- `line 56: _scratch_mkfs_encrypted &>> $seqres.full`
- `line 57: _scratch_mount`
- `line 64: _add_enckey $SCRATCH_MNT "$TEST_RAW_KEY"`
- `line 65: _set_encpolicy $dir $TEST_KEY_IDENTIFIER`
- `line 71: inode=$(stat -c %i $dir/100)`
- `line 86: while [ ! -e $tmp.done ]; do`
- `line 99: if $here/src/renameat2 -n $dir/50 $dir/100 &> /dev/null; then`
- `line 109: while [ ! -e $tmp.done ]; do`
- `line 110: _add_enckey $SCRATCH_MNT "$TEST_RAW_KEY" > /dev/null`
- `line 111: _rm_enckey $SCRATCH_MNT $TEST_KEY_IDENTIFIER > /dev/null`
- `line 121: _add_enckey $SCRATCH_MNT "$TEST_RAW_KEY" > /dev/null`
- `line 130: new_inode=$(stat -c %i $dir/100)`
- `line 145: echo -e "\n# Checking for duplicate filenames via fsck"`
- `line 146: _scratch_unmount`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Encryption policy/key state is created during the test and used to check no-key/key-present transitions. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick encrypt`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/encrypt`, `./common/renameat2`), and the golden-output file `sources/test-tools/xfstests/tests/generic/621.out` (21 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_scratch_encryption -v 2`, `_require_renameat2 noreplace`.

## Risks and Edge Cases

- Feature gates depend on kernel, userspace tool, and filesystem support; unsupported features correctly produce `_notrun`.
- Directory mutation and rename races depend on dentry-cache timing and may need repeated attempts to expose regressions.

## Test Signals

The paired `.out` file has 21 line(s); its first visible signals are: 'QA output created by 621; # Creating encrypted directory containing files; Added encryption key with identifier 69b2f6edeee720cce0577937eb8a6751'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands, hang/race detection through background work, loops, or timeout windows. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/621 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/622 -->
# sources/test-tools/xfstests/tests/generic/622

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/622`. Test that when the lazytime mount option is enabled, updates to atime, mtime, and ctime are persisted in (at least) the four cases when they should be: - The inode needs to be updated for some change unrelated to file timestamps - Userspace calls fsync(), syncfs(), or sync() - The inode is evicted from memory - More than dirtytime_expire_seconds have elapsed This is in part a regression test for kernel commit 1e249cb5b7fc ("fs: fix lazytime expiration handling in __writeback_single_inode()"). This test failed on XFS without that commit. It is registered with `_begin_fstest auto shutdown metadata atime`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 238 source line(s).
- Harness registration: `_begin_fstest auto shutdown metadata atime`.
- Imported common libraries: `./common/preamble`, `./common/filter`.
- Capability and skip gates: `_require_scratch`, `_require_scratch_shutdown`, `_require_metadata_journaling`, `_require_xfs_io_command "pwrite"`, `_require_xfs_io_command "fsync"`, `_require_xfs_io_command "syncfs"`.
- Local shell functions: `restore_expiration_settings`, `__expire_inodes`, `expire_inodes`, `expire_timestamps`, `_cleanup`, `get_timestamp`, `do_test`.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `DIRTY_EXPIRE_CENTISECS_ORIG=$(</proc/sys/vm/dirty_expire_centisecs)`
- `DIRTY_WRITEBACK_CENTISECS_ORIG=$(</proc/sys/vm/dirty_writeback_centisecs)`
- `DIRTYTIME_EXPIRE_SECONDS_ORIG=$(</proc/sys/vm/dirtytime_expire_seconds)`
- `file=$SCRATCH_MNT/file`
- `expected_time=$(get_timestamp ctime)`

## Control Flow

- Capability gating runs first through `_require_scratch`, `_require_scratch_shutdown`, `_require_metadata_journaling`, `_require_xfs_io_command "pwrite"`, `_require_xfs_io_command "fsync"`, plus 1 more.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 28: echo "$DIRTY_EXPIRE_CENTISECS_ORIG" > /proc/sys/vm/dirty_expire_centisecs`
- `line 29: echo "$DIRTY_WRITEBACK_CENTISECS_ORIG" > /proc/sys/vm/dirty_writeback_centisecs`
- `line 30: echo "$DIRTYTIME_EXPIRE_SECONDS_ORIG" > /proc/sys/vm/dirtytime_expire_seconds`
- `line 37: echo 1 > /proc/sys/vm/dirty_expire_centisecs`
- `line 38: echo 1 > /proc/sys/vm/dirty_writeback_centisecs`
- `line 57: echo 1 > /proc/sys/vm/dirtytime_expire_seconds`
- `line 118: echo -e "\n# Testing that lazytime $timestamp_type update is persisted by $persist_method"`
- `line 165: echo "FAIL: $timestamp_type didn't increase after updating it (in-memory)"`
- Key operational lines include:
- `line 80: _require_scratch_shutdown`
- `line 91: _scratch_mkfs &>> $seqres.full`
- `line 92: _scratch_mount`
- `line 96: $XFS_IO_PROG -f $file -c "pwrite 0 100" > /dev/null`
- `line 110: stat -c "%.9${arg}" $file | tr -d '.'`
- `line 127: _scratch_cycle_mount lazytime,strictatime`
- `line 129: _scratch_cycle_mount lazytime`
- `line 154: $XFS_IO_PROG -f $file -c "pwrite 0 100" > /dev/null`
- `line 155: $XFS_IO_PROG -f $file -c "pwrite 0 100" > /dev/null`
- `line 187: $XFS_IO_PROG -r $file -c fsync`
- `line 191: $XFS_IO_PROG $SCRATCH_MNT -c syncfs`
- `line 213: _scratch_shutdown -f`
- `line 217: _scratch_cycle_mount`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto shutdown metadata atime`, common helper libraries (`./common/preamble`, `./common/filter`), and the golden-output file `sources/test-tools/xfstests/tests/generic/622.out` (37 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_scratch`, `_require_scratch_shutdown`, `_require_metadata_journaling`, `_require_xfs_io_command "pwrite"`, `_require_xfs_io_command "fsync"`, `_require_xfs_io_command "syncfs"`.

## Risks and Edge Cases

- Failure-injection paths can leave mounts or synthetic device tables behind if cleanup is interrupted.

## Test Signals

The paired `.out` file has 37 line(s); its first visible signals are: 'QA output created by 622; # Testing that lazytime atime update is persisted by other_inode_change; # Testing that lazytime atime update is persisted by sync'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands, hang/race detection through background work, loops, or timeout windows, post-remount or failure-injection persistence checks. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/622 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/623 -->
# sources/test-tools/xfstests/tests/generic/623

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/623`. Test a write fault scenario on a shutdown fs. It is registered with `_begin_fstest auto quick shutdown mmap`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 34 source line(s).
- Harness registration: `_begin_fstest auto quick shutdown mmap`.
- Imported common libraries: `./common/preamble`, `./common/filter`.
- Capability and skip gates: `_fixed_by_fs_commit xfs e4826691cc7e "xfs: restore shutdown check in mapped write fault path"`, `_require_scratch_nocheck`, `_require_xfs_io_shutdown`.
- Local shell functions: none visible.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `file=$SCRATCH_MNT/file`

## Control Flow

- Capability gating runs first through `_fixed_by_fs_commit xfs e4826691cc7e "xfs: restore shutdown check in mapped write fault path"`, `_require_scratch_nocheck`, `_require_xfs_io_shutdown`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- Key operational lines include:
- `line 10: _begin_fstest auto quick shutdown mmap`
- `line 17: _require_scratch_nocheck`
- `line 20: _scratch_mkfs &>> $seqres.full`
- `line 21: _scratch_mount`
- `line 27: $XFS_IO_PROG -fc "pwrite 0 4k" -c fsync $file | _filter_xfs_io`
- `line 29: $XFS_IO_PROG -x -c "mmap 0 4k" -c "mwrite 0 4k" -c shutdown -c fsync \`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick shutdown mmap`, common helper libraries (`./common/preamble`, `./common/filter`), and the golden-output file `sources/test-tools/xfstests/tests/generic/623.out` (4 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_fixed_by_fs_commit xfs e4826691cc7e "xfs: restore shutdown check in mapped write fault path"`, `_require_scratch_nocheck`, `_require_xfs_io_shutdown`.

## Risks and Edge Cases

- Failure-injection paths can leave mounts or synthetic device tables behind if cleanup is interrupted.
- mmap/page-fault regressions are often race-prone and may manifest as hangs rather than clean command failures.

## Test Signals

The paired `.out` file has 4 line(s); its first visible signals are: 'QA output created by 623; wrote 4096/4096 bytes at offset 0; XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec); fsync: Input/output error'. Runtime pass/fail is also signaled by xfstests output filters, hang/race detection through background work, loops, or timeout windows. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/623 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/624 -->
# sources/test-tools/xfstests/tests/generic/624

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/624`. Test retrieving the Merkle tree and fs-verity descriptor of a verity file using FS_IOC_READ_VERITY_METADATA. It is registered with `_begin_fstest auto quick verity`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 122 source line(s).
- Harness registration: `_begin_fstest auto quick verity`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/verity`.
- Capability and skip gates: `_require_scratch_verity`, `_require_fsverity_dump_metadata $fsv_file`.
- Local shell functions: `_cleanup`, `test_block_size`.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `fsv_orig_file=$SCRATCH_MNT/file`
- `fsv_file=$SCRATCH_MNT/file.fsv`

## Control Flow

- Capability gating runs first through `_require_scratch_verity`, `_require_fsverity_dump_metadata $fsv_file`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 72: echo "Measure returned $actual_file_digest but expected $expected_file_digest"`
- `line 78: echo "Dumped Merkle tree didn't match"`
- `line 86: echo "Dumped Merkle tree (in chunks) didn't match"`
- `line 92: echo "Dumped descriptor didn't match"`
- `line 100: echo "Dumped descriptor (in chunks) didn't match"`
- `line 114: echo "block_size=$block_size is unsupported" >> $seqres.full`
- Key operational lines include:
- `line 24: _require_scratch_verity`
- `line 29: _scratch_mkfs_verity &>> $seqres.full`
- `line 30: _scratch_mount`
- `line 31: _fsv_create_enable_file $fsv_file`
- `line 49: _fsv_enable $fsv_file "${tree_params[@]}"`
- `line 62: local expected_file_digest=$(_fsv_digest $fsv_orig_file \`
- `line 70: local actual_file_digest=$(_fsv_measure $fsv_file)`
- `line 76: _fsv_dump_merkle_tree $fsv_file > $tmp.merkle_tree.actual`
- `line 77: if ! cmp $tmp.merkle_tree.expected $tmp.merkle_tree.actual; then`
- `line 83: _fsv_dump_merkle_tree $fsv_file --offset=$i --length=997`
- `line 85: if ! cmp $tmp.merkle_tree.expected $tmp.merkle_tree.actual; then`
- `line 90: _fsv_dump_descriptor $fsv_file > $tmp.descriptor.actual`
- `line 91: if ! cmp $tmp.descriptor.expected $tmp.descriptor.actual; then`
- `line 97: _fsv_dump_descriptor $fsv_file --offset=$i --length=13`
- `line 99: if ! cmp $tmp.descriptor.expected $tmp.descriptor.actual; then`
- `line 106: _fsv_scratch_begin_subtest "Testing block_size=FSV_BLOCK_SIZE"`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. fs-verity metadata, signatures, or Merkle trees become durable file metadata and are compared against userspace-computed expectations. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick verity`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/verity`), and the golden-output file `sources/test-tools/xfstests/tests/generic/624.out` (11 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_scratch_verity`, `_require_fsverity_dump_metadata $fsv_file`.

## Risks and Edge Cases

- Feature gates depend on kernel, userspace tool, and filesystem support; unsupported features correctly produce `_notrun`.

## Test Signals

The paired `.out` file has 11 line(s); its first visible signals are: 'QA output created by 624; # Testing block_size=FSV_BLOCK_SIZE; # Testing block_size=1024 if supported'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands, hang/race detection through background work, loops, or timeout windows. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/624 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/625 -->
# sources/test-tools/xfstests/tests/generic/625

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/625`. Test retrieving the built-in signature of a verity file using FS_IOC_READ_VERITY_METADATA. This is separate from the other tests for FS_IOC_READ_VERITY_METADATA because the fs-verity built-in signature support is optional. It is registered with `_begin_fstest auto quick verity`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 50 source line(s).
- Harness registration: `_begin_fstest auto quick verity`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/verity`.
- Capability and skip gates: `_require_scratch_verity`, `_require_fsverity_builtin_signatures`, `_require_fsverity_dump_metadata $fsv_file`.
- Local shell functions: none visible.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `fsv_file=$SCRATCH_MNT/file`
- `sig_size=$(stat -c %s $tmp.sig)`

## Control Flow

- Capability gating runs first through `_require_scratch_verity`, `_require_fsverity_builtin_signatures`, `_require_fsverity_dump_metadata $fsv_file`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 25: echo -e "\n# Setting up signed verity file"`
- `line 30: echo foo > $fsv_file`
- `line 35: echo -e "\n# Dumping and comparing signature"`
- `line 41: echo -e "\n# Dumping and comparing signature (in chunks)"`
- Key operational lines include:
- `line 19: _require_scratch_verity`
- `line 22: _scratch_mkfs_verity &>> $seqres.full`
- `line 23: _scratch_mount`
- `line 26: _fsv_generate_cert $tmp.key $tmp.cert $tmp.cert.der`
- `line 27: _fsv_clear_keyring`
- `line 28: _fsv_load_cert $tmp.cert.der`
- `line 31: _fsv_sign $fsv_file $tmp.sig --key=$tmp.key --cert=$tmp.cert >> $seqres.full`
- `line 32: _fsv_enable $fsv_file --signature=$tmp.sig`
- `line 36: _fsv_dump_signature $fsv_file > $tmp.sig2`
- `line 39: cmp $tmp.sig $tmp.sig2`
- `line 42: sig_size=$(stat -c %s $tmp.sig)`
- `line 44: _fsv_dump_signature $fsv_file --offset=$i --length=13`
- `line 46: cmp $tmp.sig $tmp.sig2`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. fs-verity metadata, signatures, or Merkle trees become durable file metadata and are compared against userspace-computed expectations. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick verity`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/verity`), and the golden-output file `sources/test-tools/xfstests/tests/generic/625.out` (7 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_scratch_verity`, `_require_fsverity_builtin_signatures`, `_require_fsverity_dump_metadata $fsv_file`.

## Risks and Edge Cases

- Feature gates depend on kernel, userspace tool, and filesystem support; unsupported features correctly produce `_notrun`.

## Test Signals

The paired `.out` file has 7 line(s); its first visible signals are: 'QA output created by 625; # Setting up signed verity file; # Dumping and comparing signature'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands, hang/race detection through background work, loops, or timeout windows. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/625 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/626 -->
# sources/test-tools/xfstests/tests/generic/626

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/626`. Test RENAME_WHITEOUT on filesystem without space to create one more inodes. This is a regression test for kernel commit: 6b4b8e6b4ad8 ("ext4: ext4: fix bug for rename with RENAME_WHITEOUT") It is registered with `_begin_fstest auto quick rename enospc`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 56 source line(s).
- Harness registration: `_begin_fstest auto quick rename enospc`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/populate`, `./common/renameat2`.
- Capability and skip gates: `_require_scratch`, `_require_renameat2 whiteout`.
- Local shell functions: none visible.
- External `$here/src` helpers: `$here/src/renameat2 -w $SCRATCH_MNT/srcfile$i $SCRATCH_MNT/dstfile$i >> $seqres.full 2>&1`.
- Notable variables and constants:
- `NR_FILE=$((4 * 64))`
- `nr_free=$(stat -f -c '%f' $SCRATCH_MNT)`
- `blksz="$(_get_block_size $SCRATCH_MNT)"`

## Control Flow

- Capability gating runs first through `_require_scratch`, `_require_renameat2 whiteout`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 53: echo "Silence is golden"`
- Key operational lines include:
- `line 21: _require_renameat2 whiteout`
- `line 23: _scratch_mkfs_sized $((256 * 1024 * 1024)) >> $seqres.full 2>&1`
- `line 24: _scratch_mount`
- `line 32: nr_free=$(stat -f -c '%f' $SCRATCH_MNT)`
- `line 45: $here/src/renameat2 -w $SCRATCH_MNT/srcfile$i $SCRATCH_MNT/dstfile$i >> $seqres.full 2>&1`
- `line 47: _scratch_cycle_mount`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick rename enospc`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/populate`, `./common/renameat2`), and the golden-output file `sources/test-tools/xfstests/tests/generic/626.out` (2 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_scratch`, `_require_renameat2 whiteout`.

## Risks and Edge Cases

- ENOSPC-sensitive timing can vary with allocator geometry, free-space accounting, delayed allocation, and background reservations.
- Directory mutation and rename races depend on dentry-cache timing and may need repeated attempts to expose regressions.

## Test Signals

The paired `.out` file has 2 line(s); its first visible signals are: 'QA output created by 626; Silence is golden'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands, post-remount or failure-injection persistence checks. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/626 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/627 -->
# sources/test-tools/xfstests/tests/generic/627

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/627`. AIO/DIO stress test Run random AIO/DIO activity on an file system with unwritten regions This test verifies that the an unwritten extent is properly marked as written after writing into it. There was a hard-to-hit bug which would occasionally trigger with ext4 for which this test was a reproducer. This has been fixed after moving ext4 to use iomap for Direct I/O's, although as of this writing, there are still some occasional failures on ext4 when block size < page size. It is registered with `_begin_fstest auto aio rw stress prealloc`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 90 source line(s).
- Harness registration: `_begin_fstest auto aio rw stress prealloc`.
- Imported common libraries: `./common/preamble`, `./common/filter`.
- Capability and skip gates: `_require_test`, `_require_scratch`, `_require_odirect`, `_require_aio`, `_require_block_device $SCRATCH_DEV`, `_require_fio $fio_config`, `_require_xfs_io_command "falloc"`.
- Local shell functions: none visible.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `fio_config=$tmp.fio`
- `fio_out=$tmp.fio.out`
- `NUM_JOBS=$((4*LOAD_FACTOR))`
- `BLK_DEV_SIZE=`blockdev --getsz $SCRATCH_DEV``
- `FILE_SIZE=$(((BLK_DEV_SIZE * 512) * 3 / 4))`
- `max_file_size=$((5 * 1024 * 1024 * 1024))`
- `FILE_SIZE=$max_file_size`
- `SIZE=$((FILE_SIZE / 2))`
- `ioengine=libaio`
- `bs=128k`
- `directory=${SCRATCH_MNT}`
- `filesize=${FILE_SIZE}`

## Control Flow

- Capability gating runs first through `_require_test`, `_require_scratch`, `_require_odirect`, `_require_aio`, `_require_block_device $SCRATCH_DEV`, plus 2 more.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- User-visible phase markers include:
- `line 82: echo ""`
- `line 83: echo "Run fio with random aio-dio pattern"`
- `line 84: echo ""`
- Key operational lines include:
- `line 22: fio_config=$tmp.fio`
- `line 23: fio_out=$tmp.fio.out`
- `line 44: cat >$fio_config <<EOF`
- `line 57: fallocate=native`
- `line 76: _require_fio $fio_config`
- `line 77: _require_xfs_io_command "falloc"`
- `line 79: _scratch_mkfs >> $seqres.full 2>&1`
- `line 80: _scratch_mount`
- `line 83: echo "Run fio with random aio-dio pattern"`
- `line 85: cat $fio_config >> $seqres.full`
- `line 86: $FIO_PROG $fio_config --output=$fio_out`
- `line 87: cat $fio_out >> $seqres.full`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto aio rw stress prealloc`, common helper libraries (`./common/preamble`, `./common/filter`), and the golden-output file `sources/test-tools/xfstests/tests/generic/627.out` (4 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_test`, `_require_scratch`, `_require_odirect`, `_require_aio`, `_require_block_device $SCRATCH_DEV`, `_require_fio $fio_config`, `_require_xfs_io_command "falloc"`.

## Risks and Edge Cases

- Direct/AIO coverage depends on alignment, device logical block size, page size, and filesystem direct-I/O semantics.

## Test Signals

The paired `.out` file has 4 line(s); its first visible signals are: 'QA output created by 627; Run fio with random aio-dio pattern'. Runtime pass/fail is primarily the command exit status plus golden-output comparison. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/627 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/628 -->
# sources/test-tools/xfstests/tests/generic/628

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/628`. Make sure that reflink forces the log out if we open the file with O_SYNC or set FS_XFLAG_SYNC on the file. We test that it actually forced the log by using dm-error to shut down the fs without flushing the log and then remounting to check file contents. This is a regression test for commit 5ffce3cc22a0 ("xfs: force the log after remapping a synchronous-writes file") It is registered with `_begin_fstest auto quick rw clone eio`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 108 source line(s).
- Harness registration: `_begin_fstest auto quick rw clone eio`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/reflink`, `./common/dmerror`.
- Capability and skip gates: `_require_scratch_reflink`, `_require_dm_target error`, `_require_xfs_io_command "chattr" "s"`, `_require_cp_reflink`, `_require_metadata_journaling $SCRATCH_DEV`.
- Local shell functions: `_cleanup`.
- External `$here/src` helpers: none visible.

## Control Flow

- Capability gating runs first through `_require_scratch_reflink`, `_require_dm_target error`, `_require_xfs_io_command "chattr" "s"`, `_require_cp_reflink`, `_require_metadata_journaling $SCRATCH_DEV`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 43: echo "test o_sync write"`
- `line 61: echo "test reflink flag not set o_sync"`
- `line 71: echo "test reflink flag already set o_sync"`
- `line 88: echo "test reflink flag not set iflag"`
- `line 98: echo "test reflink flag already set iflag"`
- Key operational lines include:
- `line 21: _dmerror_unmount`
- `line 22: _dmerror_cleanup`
- `line 30: _require_scratch_reflink`
- `line 33: _require_cp_reflink`
- `line 36: _scratch_mkfs > $seqres.full`
- `line 38: _dmerror_init`
- `line 39: _dmerror_mount`
- `line 44: $XFS_IO_PROG -x -f -s -c "pwrite -S 0x58 0 1m -b 1m" $SCRATCH_MNT/0 >> $seqres.full`
- `line 45: _dmerror_load_error_table`
- `line 46: _dmerror_unmount`
- `line 47: _dmerror_load_working_table`
- `line 48: _dmerror_mount`
- `line 49: md5sum $SCRATCH_MNT/0 | _filter_scratch`
- `line 52: $XFS_IO_PROG -f -c 'pwrite -S 0x58 0 1m -b 1m' $SCRATCH_MNT/a >> $seqres.full`
- `line 53: $XFS_IO_PROG -f -c 'pwrite -S 0x59 0 1m -b 1m' $SCRATCH_MNT/c >> $seqres.full`
- `line 54: _cp_reflink $SCRATCH_MNT/a $SCRATCH_MNT/e`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Synthetic block-device state can be introduced through device-mapper, loop, SCSI debug, or huge-device helpers and must be cleaned even on failure. Extended attributes are part of the persistent state being created, replayed, or verified. Shared extent or atomic-update state is exercised, so correctness depends on clone/dedupe/exchange persistence and metadata ordering. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick rw clone eio`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/reflink`, `./common/dmerror`), and the golden-output file `sources/test-tools/xfstests/tests/generic/628.out` (15 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_scratch_reflink`, `_require_dm_target error`, `_require_xfs_io_command "chattr" "s"`, `_require_cp_reflink`, `_require_metadata_journaling $SCRATCH_DEV`.

## Risks and Edge Cases

- Failure-injection paths can leave mounts or synthetic device tables behind if cleanup is interrupted.
- Shared-extent and exchange operations can expose stale data, permission-bit, or log-ordering bugs that only appear after remount/recovery.

## Test Signals

The paired `.out` file has 15 line(s); its first visible signals are: 'QA output created by 628; test o_sync write; 310f146ce52077fcd3308dcbe7632bb2  SCRATCH_MNT/0; test reflink flag not set o_sync; 310f146ce52077fcd3308dcbe7632bb2  SCRATCH_MNT/a'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands, xfstests output filters, post-remount or failure-injection persistence checks. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/628 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/629 -->
# sources/test-tools/xfstests/tests/generic/629

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/629`. Make sure that copy_file_range forces the log out if we open the file with O_SYNC or set FS_XFLAG_SYNC on the file. We test that it actually forced the log by using dm-error to shut down the fs without flushing the log and then remounting to check file contents. This is a regression test for commit 5ffce3cc22a0 ("xfs: force the log after remapping a synchronous-writes file") It is registered with `_begin_fstest auto quick rw copy_range eio`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 83 source line(s).
- Harness registration: `_begin_fstest auto quick rw copy_range eio`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/dmerror`.
- Capability and skip gates: `_require_scratch`, `_require_dm_target error`, `_require_xfs_io_command "chattr" "s"`, `_require_xfs_io_command "copy_range"`, `_require_metadata_journaling $SCRATCH_DEV`.
- Local shell functions: `_cleanup`.
- External `$here/src` helpers: none visible.

## Control Flow

- Capability gating runs first through `_require_scratch`, `_require_dm_target error`, `_require_xfs_io_command "chattr" "s"`, `_require_xfs_io_command "copy_range"`, `_require_metadata_journaling $SCRATCH_DEV`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 42: echo "test o_sync write"`
- `line 57: echo "test unaligned copy range o_sync"`
- `line 73: echo "test unaligned copy range iflag"`
- Key operational lines include:
- `line 14: _begin_fstest auto quick rw copy_range eio`
- `line 21: _dmerror_unmount`
- `line 22: _dmerror_cleanup`
- `line 32: _require_xfs_io_command "copy_range"`
- `line 35: _scratch_mkfs > $seqres.full`
- `line 37: _dmerror_init`
- `line 38: _dmerror_mount`
- `line 43: $XFS_IO_PROG -x -f -s -c "pwrite -S 0x58 0 1m -b 1m" $SCRATCH_MNT/0 >> $seqres.full`
- `line 44: _dmerror_load_error_table`
- `line 45: _dmerror_unmount`
- `line 46: _dmerror_load_working_table`
- `line 47: _dmerror_mount`
- `line 48: md5sum $SCRATCH_MNT/0 | _filter_scratch`
- `line 51: $XFS_IO_PROG -f -c 'pwrite -S 0x58 0 1m -b 1m' $SCRATCH_MNT/a >> $seqres.full`
- `line 53: _scratch_sync`
- `line 58: $XFS_IO_PROG -x -s -c "copy_range -s 13 -d 13 -l 1048550 $SCRATCH_MNT/a" $SCRATCH_MNT/b >> $seqres.full`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Synthetic block-device state can be introduced through device-mapper, loop, SCSI debug, or huge-device helpers and must be cleaned even on failure. Extended attributes are part of the persistent state being created, replayed, or verified. Shared extent or atomic-update state is exercised, so correctness depends on clone/dedupe/exchange persistence and metadata ordering. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick rw copy_range eio`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/dmerror`), and the golden-output file `sources/test-tools/xfstests/tests/generic/629.out` (9 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_scratch`, `_require_dm_target error`, `_require_xfs_io_command "chattr" "s"`, `_require_xfs_io_command "copy_range"`, `_require_metadata_journaling $SCRATCH_DEV`.

## Risks and Edge Cases

- Failure-injection paths can leave mounts or synthetic device tables behind if cleanup is interrupted.
- Shared-extent and exchange operations can expose stale data, permission-bit, or log-ordering bugs that only appear after remount/recovery.

## Test Signals

The paired `.out` file has 9 line(s); its first visible signals are: 'QA output created by 629; test o_sync write; 310f146ce52077fcd3308dcbe7632bb2  SCRATCH_MNT/0; test unaligned copy range o_sync; 310f146ce52077fcd3308dcbe7632bb2  SCRATCH_MNT/a'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands, xfstests output filters, post-remount or failure-injection persistence checks. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/629 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/630 -->
# sources/test-tools/xfstests/tests/generic/630

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/630`. Make sure that mmap and file writers racing with FIDEDUPERANGE cannot write to the file after the dedupe prep function has decided that the file contents are identical and we can therefore go ahead with the remapping. It is registered with `_begin_fstest auto quick rw dedupe clone mmap`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 35 source line(s).
- Harness registration: `_begin_fstest auto quick rw dedupe clone mmap`.
- Imported common libraries: `./common/preamble`, `./common/reflink`.
- Capability and skip gates: `_require_scratch_dedupe`, `_require_test_program "deduperace"`.
- Local shell functions: none visible.
- External `$here/src` helpers: `$here/src/deduperace -c $SCRATCH_MNT -n $nr_ops`, `$here/src/deduperace -c $SCRATCH_MNT -n $nr_ops -w`.
- Notable variables and constants:
- `nr_ops=$((TIME_FACTOR * 10000))`

## Control Flow

- Capability gating runs first through `_require_scratch_dedupe`, `_require_test_program "deduperace"`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- User-visible phase markers include:
- `line 32: echo Silence is golden.`
- Key operational lines include:
- `line 12: _begin_fstest auto quick rw dedupe clone mmap`
- `line 17: _require_scratch_dedupe`
- `line 18: _require_test_program "deduperace"`
- `line 23: _scratch_mkfs > $seqres.full`
- `line 24: _scratch_mount`
- `line 27: $here/src/deduperace -c $SCRATCH_MNT -n $nr_ops`
- `line 30: $here/src/deduperace -c $SCRATCH_MNT -n $nr_ops -w`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Shared extent or atomic-update state is exercised, so correctness depends on clone/dedupe/exchange persistence and metadata ordering. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick rw dedupe clone mmap`, common helper libraries (`./common/preamble`, `./common/reflink`), and the golden-output file `sources/test-tools/xfstests/tests/generic/630.out` (2 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_scratch_dedupe`, `_require_test_program "deduperace"`.

## Risks and Edge Cases

- mmap/page-fault regressions are often race-prone and may manifest as hangs rather than clean command failures.
- Shared-extent and exchange operations can expose stale data, permission-bit, or log-ordering bugs that only appear after remount/recovery.

## Test Signals

The paired `.out` file has 2 line(s); its first visible signals are: 'QA output created by 630; Silence is golden.'. Runtime pass/fail is primarily the command exit status plus golden-output comparison. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/630 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/631 -->
# sources/test-tools/xfstests/tests/generic/631

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/631`. Reproducer for a deadlock in xfs_rename reported by Wenli Xie. When overlayfs is running on top of xfs and the user unlinks a file in the overlay, overlayfs will create a whiteout inode and ask us to "rename" the whiteout file atop the one being unlinked. If the file being unlinked loses its one nlink, we then have to put the inode on the unlinked list. This requires us to grab the AGI buffer of the whiteout inode to take it off the unlinked list (which is where whiteouts are created) and to grab the AGI buffer of the file being deleted. If the whiteout was created in a higher numbered AG than the file being deleted, we'll lock the AGIs in the wrong order and deadlock. Note that this test doesn't do anything... It is registered with `_begin_fstest auto rw whiteout rename`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 103 source line(s).
- Harness registration: `_begin_fstest auto rw whiteout rename`.
- Imported common libraries: `./common/preamble`, `./common/attr`.
- Capability and skip gates: `_require_scratch`, `_require_attrs trusted`, `_exclude_fs overlay`, `_require_extra_fs overlay`, `_fixed_by_fs_commit xfs 6da1b4b1ab36 "xfs: fix an ABBA deadlock in xfs_rename"`.
- Local shell functions: `_cleanup`, `stop_workers`, `worker`.
- External `$here/src` helpers: none visible.

## Control Flow

- Capability gating runs first through `_require_scratch`, `_require_attrs trusted`, `_exclude_fs overlay`, `_require_extra_fs overlay`, `_fixed_by_fs_commit xfs 6da1b4b1ab36 "xfs: fix an ABBA deadlock in xfs_rename"`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- User-visible phase markers include:
- `line 54: echo salts > $SCRATCH_MNT/lowerdir/etc/access.conf`
- `line 100: echo Silence is golden.`
- Key operational lines include:
- `line 46: _scratch_mkfs >> $seqres.full`
- `line 47: _scratch_mount`
- `line 61: while [ "$(ls $SCRATCH_MNT/workers/ | wc -l)" -gt 0 ]; do`
- `line 88: _unmount $mergedir`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Extended attributes are part of the persistent state being created, replayed, or verified. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto rw whiteout rename`, common helper libraries (`./common/preamble`, `./common/attr`), and the golden-output file `sources/test-tools/xfstests/tests/generic/631.out` (2 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_scratch`, `_require_attrs trusted`, `_exclude_fs overlay`, `_require_extra_fs overlay`, `_fixed_by_fs_commit xfs 6da1b4b1ab36 "xfs: fix an ABBA deadlock in xfs_rename"`.

## Risks and Edge Cases

- Feature gates depend on kernel, userspace tool, and filesystem support; unsupported features correctly produce `_notrun`.
- Directory mutation and rename races depend on dentry-cache timing and may need repeated attempts to expose regressions.

## Test Signals

The paired `.out` file has 2 line(s); its first visible signals are: 'QA output created by 631; Silence is golden.'. Runtime pass/fail is also signaled by hang/race detection through background work, loops, or timeout windows. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/631 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/632 -->
# sources/test-tools/xfstests/tests/generic/632

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/632`. Regression test to verify that creating a series of detached mounts, attaching them to the filesystem, and unmounting them does not trigger an integer overflow in ns->mounts causing the kernel to block any new mounts in count_mounts() and returning ENOSPC because it falsely assumes that the maximum number of mounts in the mount namespace has been reached, i.e. it thinks it can't fit the new mounts into the mount namespace anymore. Kernel commit ee2e3f50629f ("mount: fix mounting of detached mounts onto targets that reside on shared mounts") fixed the bug. It is registered with `_begin_fstest auto quick mount`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 31 source line(s).
- Harness registration: `_begin_fstest auto quick mount`.
- Imported common libraries: `./common/preamble`.
- Capability and skip gates: `_require_test`, `_require_test_program "detached_mounts_propagation"`.
- Local shell functions: none visible.
- External `$here/src` helpers: `$here/src/detached_mounts_propagation $TEST_DIR >> $seqres.full`.

## Control Flow

- Capability gating runs first through `_require_test`, `_require_test_program "detached_mounts_propagation"`.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- User-visible phase markers include:
- `line 30: echo silence is golden`
- Key operational lines include:
- `line 25: _mount --make-shared $TEST_DIR`
- `line 28: _mount --make-private $TEST_DIR`

## State and Persistence Behavior

Uses the configured xfstests test area or an explicitly created loop/image mount rather than always reformatting the scratch device. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick mount`, common helper libraries (`./common/preamble`), and the golden-output file `sources/test-tools/xfstests/tests/generic/632.out` (2 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_test`, `_require_test_program "detached_mounts_propagation"`.

## Risks and Edge Cases

- Most failures should surface as unexpected output, nonzero helper status, or harness `_fail`/`_notrun` behavior.

## Test Signals

The paired `.out` file has 2 line(s); its first visible signals are: 'QA output created by 632; silence is golden'. Runtime pass/fail is primarily the command exit status plus golden-output comparison. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/632 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/633 -->
# sources/test-tools/xfstests/tests/generic/633

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/633`. Test that idmapped mounts behave correctly. It is registered with `_begin_fstest auto quick atime attr cap idmapped io_uring mount perms rw unlink`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 24 source line(s).
- Harness registration: `_begin_fstest auto quick atime attr cap idmapped io_uring mount perms rw unlink`.
- Imported common libraries: `./common/preamble`, `./common/filter`.
- Capability and skip gates: `_require_test`, `_require_chown`.
- Local shell functions: none visible.
- External `$here/src` helpers: `$here/src/vfs/vfstest --test-core --device "$TEST_DEV" \`.

## Control Flow

- Capability gating runs first through `_require_test`, `_require_chown`.
- User-visible phase markers include:
- `line 18: echo "Silence is golden"`

## State and Persistence Behavior

Uses the configured xfstests test area or an explicitly created loop/image mount rather than always reformatting the scratch device. Extended attributes are part of the persistent state being created, replayed, or verified. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick atime attr cap idmapped io_uring mount perms rw unlink`, common helper libraries (`./common/preamble`, `./common/filter`), and the golden-output file `sources/test-tools/xfstests/tests/generic/633.out` (2 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_test`, `_require_chown`.

## Risks and Edge Cases

- Feature gates depend on kernel, userspace tool, and filesystem support; unsupported features correctly produce `_notrun`.

## Test Signals

The paired `.out` file has 2 line(s); its first visible signals are: 'QA output created by 633; Silence is golden'. Runtime pass/fail is primarily the command exit status plus golden-output comparison. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/633 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/634 -->
# sources/test-tools/xfstests/tests/generic/634

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/634`. Make sure we can store and retrieve timestamps on the extremes of the date ranges supported by userspace, and the common places where overflows can happen. This differs from generic/402 in that we don't constrain ourselves to the range that the filesystem claims to support; we attempt various things that /userspace/ can parse, and then check that the vfs clamps and persists the values correctly. NOTE: Old kernels (pre 5.4) allow filesystems to truncate timestamps silently when writing timestamps to disk! This test detects this silent truncation and fails. If you see a failure on such a kernel, contact your distributor for an update. It is registered with `_begin_fstest auto quick atime bigtime`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 106 source line(s).
- Harness registration: `_begin_fstest auto quick atime bigtime`.
- Imported common libraries: `./common/preamble`.
- Capability and skip gates: `_require_scratch`.
- Local shell functions: `touchme`, `report`.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `test_bigdates=1`
- `test_statx=1`
- `test_statx=0`
- `TZ=UTC stat -c '%y %Y %n' "${file}"`

## Control Flow

- Capability gating runs first through `_require_scratch`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 41: echo "Userspace support of large timestamps: $test_bigdates" >> $seqres.full`
- `line 42: echo "xfs_io support of statx: $test_statx" >> $seqres.full`
- `line 48: echo "$arg" > $SCRATCH_MNT/t_$name`
- `line 55: echo "${file}: $(cat "${file}")"`
- `line 89: echo before >> $seqres.full`
- `line 96: echo after >> $seqres.full`
- `line 104: echo Silence is golden.`
- Key operational lines include:
- `line 28: _scratch_mkfs > $seqres.full`
- `line 29: _scratch_mount`
- `line 37: ($XFS_IO_PROG -c 'help statx' | grep -q 'Print raw statx' && \`
- `line 38: $XFS_IO_PROG -c 'statx -r' $SCRATCH_MNT 2>/dev/null | grep -q 'stat.mtime') || \`
- `line 56: TZ=UTC stat -c '%y %Y %n' "${file}"`
- `line 58: $XFS_IO_PROG -c 'statx -r' "${file}" | grep 'stat.mtime'`
- `line 93: _scratch_cycle_mount`
- `line 101: cmp -s $tmp.before_remount $tmp.after_remount`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick atime bigtime`, common helper libraries (`./common/preamble`), and the golden-output file `sources/test-tools/xfstests/tests/generic/634.out` (2 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_scratch`.

## Risks and Edge Cases

- Most failures should surface as unexpected output, nonzero helper status, or harness `_fail`/`_notrun` behavior.

## Test Signals

The paired `.out` file has 2 line(s); its first visible signals are: 'QA output created by 634; Silence is golden.'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands, hang/race detection through background work, loops, or timeout windows, post-remount or failure-injection persistence checks. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/634 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/635 -->
# sources/test-tools/xfstests/tests/generic/635

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/635`. Make sure we can store and retrieve timestamps on the extremes of the date ranges supported by userspace, and the common places where overflows can happen. This test also ensures that the timestamps are persisted correctly after a shutdown. This differs from generic/402 in that we don't constrain ourselves to the range that the filesystem claims to support; we attempt various things that /userspace/ can parse, and then check that the vfs clamps and persists the values correctly. NOTE: Old kernels (pre 5.4) allow filesystems to truncate timestamps silently when writing timestamps to disk! This test detects this silent truncation and fails. If you see a failure on such a kernel, contact your distributor for an... It is registered with `_begin_fstest auto quick atime bigtime shutdown`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 109 source line(s).
- Harness registration: `_begin_fstest auto quick atime bigtime shutdown`.
- Imported common libraries: `./common/preamble`.
- Capability and skip gates: `_require_scratch`, `_require_scratch_shutdown`, `_require_metadata_journaling`.
- Local shell functions: `touchme`, `report`.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `test_bigdates=1`
- `test_statx=1`
- `test_statx=0`
- `TZ=UTC stat -c '%y %Y %n' "${file}"`

## Control Flow

- Capability gating runs first through `_require_scratch`, `_require_scratch_shutdown`, `_require_metadata_journaling`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 44: echo "Userspace support of large timestamps: $test_bigdates" >> $seqres.full`
- `line 45: echo "xfs_io support of statx: $test_statx" >> $seqres.full`
- `line 51: echo "$arg" > $SCRATCH_MNT/t_$name`
- `line 58: echo "${file}: $(cat "${file}")"`
- `line 92: echo before >> $seqres.full`
- `line 100: echo after >> $seqres.full`
- Key operational lines include:
- `line 28: _require_scratch_shutdown`
- `line 31: _scratch_mkfs > $seqres.full`
- `line 32: _scratch_mount`
- `line 40: ($XFS_IO_PROG -c 'help statx' | grep -q 'Print raw statx' && \`
- `line 41: $XFS_IO_PROG -c 'statx -r' $SCRATCH_MNT 2>/dev/null | grep -q 'stat.mtime') || \`
- `line 59: TZ=UTC stat -c '%y %Y %n' "${file}"`
- `line 61: $XFS_IO_PROG -c 'statx -r' "${file}" | grep 'stat.mtime'`
- `line 96: _scratch_shutdown -f`
- `line 97: _scratch_cycle_mount`
- `line 105: cmp -s $tmp.before_crash $tmp.after_crash`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick atime bigtime shutdown`, common helper libraries (`./common/preamble`), and the golden-output file `sources/test-tools/xfstests/tests/generic/635.out` (1 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_scratch`, `_require_scratch_shutdown`, `_require_metadata_journaling`.

## Risks and Edge Cases

- Failure-injection paths can leave mounts or synthetic device tables behind if cleanup is interrupted.

## Test Signals

The paired `.out` file has 1 line(s); its first visible signals are: 'QA output created by 635'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands, hang/race detection through background work, loops, or timeout windows, post-remount or failure-injection persistence checks. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/635 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/636 -->
# sources/test-tools/xfstests/tests/generic/636

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/636`. Test invalid swap files. Empty swap file (only swap header) It is registered with `_begin_fstest auto quick swap`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 32 source line(s).
- Harness registration: `_begin_fstest auto quick swap`.
- Imported common libraries: `./common/preamble`, `./common/filter`.
- Capability and skip gates: `_require_scratch_swapfile`, `_require_test_program mkswap`, `_require_test_program swapon`.
- Local shell functions: none visible.
- External `$here/src` helpers: `"$here/src/mkswap" "$SCRATCH_MNT/swap"`, `"$here/src/swapon" "$SCRATCH_MNT/swap"`.

## Control Flow

- Capability gating runs first through `_require_scratch_swapfile`, `_require_test_program mkswap`, `_require_test_program swapon`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- Key operational lines include:
- `line 16: _require_scratch_swapfile`
- `line 20: _scratch_mkfs >> $seqres.full 2>&1`
- `line 21: _scratch_mount`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick swap`, common helper libraries (`./common/preamble`, `./common/filter`), and the golden-output file `sources/test-tools/xfstests/tests/generic/636.out` (2 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_scratch_swapfile`, `_require_test_program mkswap`, `_require_test_program swapon`.

## Risks and Edge Cases

- Most failures should surface as unexpected output, nonzero helper status, or harness `_fail`/`_notrun` behavior.

## Test Signals

The paired `.out` file has 2 line(s); its first visible signals are: 'QA output created by 636; swapon: Invalid argument'. Runtime pass/fail is primarily the command exit status plus golden-output comparison. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/636 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/637 -->
# sources/test-tools/xfstests/tests/generic/637

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/637`. Check that directory modifications to an open dir are observed by a new open fd It is registered with `_begin_fstest auto quick dir`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 45 source line(s).
- Harness registration: `_begin_fstest auto quick dir`.
- Imported common libraries: `./common/preamble`, `./common/filter`.
- Capability and skip gates: `_require_test`.
- Local shell functions: none visible.
- External `$here/src` helpers: `$here/src/t_dir_offset2 $testdir $bufsize "+0" 2>&1 >> $seqres.full || \`, `$here/src/t_dir_offset2 $testdir $bufsize "-${n}0" 2>&1 >> $seqres.full || \`.
- Notable variables and constants:
- `testdir=$TEST_DIR/test-$seq`
- `bufsize=200`

## Control Flow

- Capability gating runs first through `_require_test`.
- User-visible phase markers include:
- `line 25: echo -e "\nCreate file 0 in an open dir:" >> $seqres.full`
- `line 27: echo "Missing created file in open dir (see $seqres.full for details)"`
- `line 38: echo -e "\nRemove file ${n}0 in an open dir:" >> $seqres.full`
- `line 40: echo "Found unlinked files in open dir (see $seqres.full for details)"`
- `line 44: echo "Silence is golden"`

## State and Persistence Behavior

Uses the configured xfstests test area or an explicitly created loop/image mount rather than always reformatting the scratch device. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick dir`, common helper libraries (`./common/preamble`, `./common/filter`), and the golden-output file `sources/test-tools/xfstests/tests/generic/637.out` (2 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_test`.

## Risks and Edge Cases

- Most failures should surface as unexpected output, nonzero helper status, or harness `_fail`/`_notrun` behavior.

## Test Signals

The paired `.out` file has 2 line(s); its first visible signals are: 'QA output created by 637; Silence is golden'. Runtime pass/fail is primarily the command exit status plus golden-output comparison. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/637 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/638 -->
# sources/test-tools/xfstests/tests/generic/638

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/638`. This case mmaps several pages of a file, alloc pages, copy data with pages overlapping, e.g: +-----------------------+ | (copy) | | V +---------------+---------------+------------ |AAAA| ........ |AAAA| ... |AAAA|AAAA| +---------------+---------------+------------ | ^ | (copy) | +------------+ This's a regression test cover kernel commit: 4f06dd92b5d0 ("fuse: fix write deadlock") It is registered with `_begin_fstest auto quick rw mmap`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 39 source line(s).
- Harness registration: `_begin_fstest auto quick rw mmap`.
- Imported common libraries: `./common/preamble`, `./common/filter`.
- Capability and skip gates: `_require_test`, `_require_test_program "t_mmap_writev_overlap"`.
- Local shell functions: none visible.
- External `$here/src` helpers: `$here/src/t_mmap_writev_overlap -b $pagesize -c 2 -l 64 $testfile`.
- Notable variables and constants:
- `pagesize=`getconf PAGE_SIZE``
- `testfile=$TEST_DIR/mmap-writev-overlap`

## Control Flow

- Capability gating runs first through `_require_test`, `_require_test_program "t_mmap_writev_overlap"`.
- User-visible phase markers include:
- `line 36: echo "Silence is golden"`
- Key operational lines include:
- `line 23: _begin_fstest auto quick rw mmap`
- `line 29: _require_test_program "t_mmap_writev_overlap"`
- `line 32: testfile=$TEST_DIR/mmap-writev-overlap`
- `line 33: $XFS_IO_PROG -f -c "truncate 0" $testfile`
- `line 34: $here/src/t_mmap_writev_overlap -b $pagesize -c 2 -l 64 $testfile`

## State and Persistence Behavior

Uses the configured xfstests test area or an explicitly created loop/image mount rather than always reformatting the scratch device. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick rw mmap`, common helper libraries (`./common/preamble`, `./common/filter`), and the golden-output file `sources/test-tools/xfstests/tests/generic/638.out` (2 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_test`, `_require_test_program "t_mmap_writev_overlap"`.

## Risks and Edge Cases

- mmap/page-fault regressions are often race-prone and may manifest as hangs rather than clean command failures.

## Test Signals

The paired `.out` file has 2 line(s); its first visible signals are: 'QA output created by 638; Silence is golden'. Runtime pass/fail is primarily the command exit status plus golden-output comparison. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/638 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/639 -->
# sources/test-tools/xfstests/tests/generic/639

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/639`. Open a file and write a little data to it. Unmount (to clean out the cache) and then mount again. Then write some data to it beyond the EOF and ensure the result is correct. Prompted by a bug in ceph_write_begin that was fixed by commit 827a746f405d. It is registered with `_begin_fstest auto quick rw`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 37 source line(s).
- Harness registration: `_begin_fstest auto quick rw`.
- Imported common libraries: `./common/preamble`, `./common/filter`.
- Capability and skip gates: `_require_test`.
- Local shell functions: none visible.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `testfile="$TEST_DIR/test_write_begin.$$"`

## Control Flow

- Capability gating runs first through `_require_test`.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 33: echo "The result should be 64 bytes filled with 0xcd:"`
- Key operational lines include:
- `line 24: $XFS_IO_PROG -f -c "pwrite -q 0 32" $testfile`
- `line 30: $XFS_IO_PROG -c "pwrite -q 32 32" $testfile`
- `line 34: _hexdump $testfile`

## State and Persistence Behavior

Uses the configured xfstests test area or an explicitly created loop/image mount rather than always reformatting the scratch device. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick rw`, common helper libraries (`./common/preamble`, `./common/filter`), and the golden-output file `sources/test-tools/xfstests/tests/generic/639.out` (5 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_test`.

## Risks and Edge Cases

- Most failures should surface as unexpected output, nonzero helper status, or harness `_fail`/`_notrun` behavior.

## Test Signals

The paired `.out` file has 5 line(s); its first visible signals are: 'QA output created by 639; The result should be 64 bytes filled with 0xcd:; 000000 cd cd cd cd cd cd cd cd cd cd cd cd cd cd cd cd  >................<; *; 000040'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/639 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/640 -->
# sources/test-tools/xfstests/tests/generic/640

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/640`. Test that if we fsync a directory A, evict A's inode, move one file from directory A to a directory B, fsync some other inode that is not directory A, B or any inode inside these two directories, and then power fail, the file that was moved is not lost. It is registered with `_begin_fstest auto quick log`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 99 source line(s).
- Harness registration: `_begin_fstest auto quick log`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/dmflakey`.
- Capability and skip gates: `_require_scratch`, `_require_dm_target flakey`, `_require_metadata_journaling $SCRATCH_DEV`.
- Local shell functions: `_cleanup`.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `foo_in_a=0`
- `foo_in_b=0`
- `foo_in_a=1`
- `foo_in_b=1`

## Control Flow

- Capability gating runs first through `_require_scratch`, `_require_dm_target flakey`, `_require_metadata_journaling $SCRATCH_DEV`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- User-visible phase markers include:
- `line 38: echo -n "hello world" > $SCRATCH_MNT/A/foo`
- `line 50: echo 2 > /proc/sys/vm/drop_caches`
- `line 78: echo "File foo data: $(cat $SCRATCH_MNT/A/foo)"`
- `line 83: echo "File foo data: $(cat $SCRATCH_MNT/B/foo)"`
- `line 88: echo "File foo found in A/ and B/"`
- `line 90: echo "File foo is missing"`
- Key operational lines include:
- `line 18: _cleanup_flakey`
- `line 30: _scratch_mkfs >>$seqres.full 2>&1`
- `line 32: _init_flakey`
- `line 33: _scratch_mount`
- `line 41: _scratch_sync`
- `line 45: $XFS_IO_PROG -c "fsync" $SCRATCH_MNT/A`
- `line 58: $XFS_IO_PROG -c "fsync" $SCRATCH_MNT/baz`
- `line 61: _flakey_drop_and_remount`
- `line 97: _scratch_unmount`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Synthetic block-device state can be introduced through device-mapper, loop, SCSI debug, or huge-device helpers and must be cleaned even on failure. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick log`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/dmflakey`), and the golden-output file `sources/test-tools/xfstests/tests/generic/640.out` (2 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_scratch`, `_require_dm_target flakey`, `_require_metadata_journaling $SCRATCH_DEV`.

## Risks and Edge Cases

- Failure-injection paths can leave mounts or synthetic device tables behind if cleanup is interrupted.

## Test Signals

The paired `.out` file has 2 line(s); its first visible signals are: 'QA output created by 640; File foo data: hello world'. Runtime pass/fail is also signaled by post-remount or failure-injection persistence checks. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/640 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/641 -->
# sources/test-tools/xfstests/tests/generic/641

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/641`. Test small swapfile which doesn't contain even a single page-aligned contiguous range of blocks. This case covered commit 5808fecc5723 ("iomap: Fix negative assignment to unsigned sis->pages in iomap_swapfile_activate"). It is registered with `_begin_fstest auto quick swap collapse`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 75 source line(s).
- Harness registration: `_begin_fstest auto quick swap collapse`.
- Imported common libraries: `./common/preamble`, `./common/filter`.
- Capability and skip gates: `_require_scratch`, `_require_scratch_swapfile`, `_require_test_program mkswap`, `_require_test_program swapon`, `_require_xfs_io_command fcollapse`, `_notrun "Can't make filesystem block size < page size."`, `_notrun "Can't force 1024-byte file block size."`.
- Local shell functions: `make_unaligned_swapfile`.
- External `$here/src` helpers: `$here/src/mkswap $fname`, `$here/src/swapon $swapfile`.
- Notable variables and constants:
- `psize=`_get_page_size``
- `bsize=`_get_file_block_size $SCRATCH_MNT``
- `bsize=`_get_file_block_size $SCRATCH_MNT``
- `swapfile=$SCRATCH_MNT/$seq.swapfile`
- `swapsize=$(awk -v fname="$swapfile" '{if ($1~fname) print $3}' /proc/swaps)`
- `swapsize=$((swapsize * 1024))`
- `filesize=$(_get_filesize $swapfile)`

## Control Flow

- Capability gating runs first through `_require_scratch`, `_require_scratch_swapfile`, `_require_test_program mkswap`, `_require_test_program swapon`, `_require_xfs_io_command fcollapse`, plus 2 more.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- User-visible phase markers include:
- `line 68: echo "Allocated swap size($swapsize) shouldn't be greater than swapfile size($filesize)"`
- Key operational lines include:
- `line 18: _require_scratch_swapfile`
- `line 30: $XFS_IO_PROG -f -t -c "pwrite 0 $(((psize + bsize) * n))" $fname >> $seqres.full 2>&1`
- `line 32: $XFS_IO_PROG -c "fcollapse $(((psize - bsize) * i)) $bsize" $fname`
- `line 39: _scratch_mkfs >> $seqres.full 2>&1`
- `line 40: _scratch_mount`
- `line 46: _scratch_unmount`
- `line 47: _scratch_mkfs_blocksized 1024 >> $seqres.full 2>&1`
- `line 51: _scratch_mount`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick swap collapse`, common helper libraries (`./common/preamble`, `./common/filter`), and the golden-output file `sources/test-tools/xfstests/tests/generic/641.out` (2 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_scratch`, `_require_scratch_swapfile`, `_require_test_program mkswap`, `_require_test_program swapon`, `_require_xfs_io_command fcollapse`, `_notrun "Can't make filesystem block size < page size."`, `_notrun "Can't force 1024-byte file block size."`.

## Risks and Edge Cases

- Most failures should surface as unexpected output, nonzero helper status, or harness `_fail`/`_notrun` behavior.

## Test Signals

The paired `.out` file has 2 line(s); its first visible signals are: 'QA output created by 641; swapon: Invalid argument'. Runtime pass/fail is primarily the command exit status plus golden-output comparison. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/641 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/642 -->
# sources/test-tools/xfstests/tests/generic/642

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/642`. Run an extended attributes fsstress run with multiple threads to shake out bugs in the xattr code. It is registered with `_begin_fstest auto soak attr long_rw stress smoketest`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 49 source line(s).
- Harness registration: `_begin_fstest auto soak attr long_rw stress smoketest`.
- Imported common libraries: `./common/preamble`.
- Capability and skip gates: `_require_scratch`.
- Local shell functions: none visible.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `nr_cpus=$((LOAD_FACTOR * 4))`
- `nr_ops=$((70000 * TIME_FACTOR))`
- `args=('-z' '-S' 'c')`

## Control Flow

- Capability gating runs first through `_require_scratch`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- User-visible phase markers include:
- `line 17: echo "Silence is golden."`
- Key operational lines include:
- `line 19: _scratch_mkfs > $seqres.full 2>&1`
- `line 20: _scratch_mount >> $seqres.full 2>&1`
- `line 35: for verb in getfattr listfattr; do`
- `line 41: args+=('-f' "setfattr=20")`
- `line 45: _run_fsstress "${args[@]}" -d $SCRATCH_MNT -n $nr_ops -p $nr_cpus`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Extended attributes are part of the persistent state being created, replayed, or verified. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto soak attr long_rw stress smoketest`, common helper libraries (`./common/preamble`), and the golden-output file `sources/test-tools/xfstests/tests/generic/642.out` (2 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_scratch`.

## Risks and Edge Cases

- Most failures should surface as unexpected output, nonzero helper status, or harness `_fail`/`_notrun` behavior.

## Test Signals

The paired `.out` file has 2 line(s); its first visible signals are: 'QA output created by 642; Silence is golden.'. Runtime pass/fail is primarily the command exit status plus golden-output comparison. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/642 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/643 -->
# sources/test-tools/xfstests/tests/generic/643

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/643`. Regression test for commit: 36ca7943ac18 ("mm/swap: consider max pages in iomap_swapfile_add_extent") Xu Yu found that the iomap swapfile activation code failed to constrain itself to activating however many swap pages that the mm asked us for. This is an deviation in behavior from the classic swapfile code. It also leads to kernel memory corruption if the swapfile is cleverly constructed. It is registered with `_begin_fstest auto swap`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 62 source line(s).
- Harness registration: `_begin_fstest auto swap`.
- Imported common libraries: `./common/preamble`, `./common/filter`.
- Capability and skip gates: `_require_scratch_swapfile`.
- Local shell functions: `_cleanup`.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `swapfile=$SCRATCH_MNT/386spart.par`
- `before_blocks=$(_format_swapfile $swapfile 1m)`
- `page_size=$(getconf PAGE_SIZE)`
- `after_blocks=$(swapon --show --bytes |grep $swapfile | awk '{print $3}')`
- `page_variance=$(( page_size / 512 ))`

## Control Flow

- Capability gating runs first through `_require_scratch_swapfile`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- User-visible phase markers include:
- `line 59: echo "pagesize: $page_size; before: $before_blocks; after: $after_blocks" >> $seqres.full`
- Key operational lines include:
- `line 29: _require_scratch_swapfile`
- `line 31: _scratch_mkfs >> $seqres.full`
- `line 32: _scratch_mount >> $seqres.full`
- `line 43: $XFS_IO_PROG -f -c 'pwrite 1m 1m' $swapfile >> $seqres.full`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto swap`, common helper libraries (`./common/preamble`, `./common/filter`), and the golden-output file `sources/test-tools/xfstests/tests/generic/643.out` (2 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_scratch_swapfile`.

## Risks and Edge Cases

- Most failures should surface as unexpected output, nonzero helper status, or harness `_fail`/`_notrun` behavior.

## Test Signals

The paired `.out` file has 2 line(s); its first visible signals are: 'QA output created by 643; swap blocks is in range'. Runtime pass/fail is primarily the command exit status plus golden-output comparison. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/643 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/644 -->
# sources/test-tools/xfstests/tests/generic/644

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/644`. Test that fscaps on idmapped mounts behave correctly. It is registered with `_begin_fstest auto quick cap idmapped mount`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 25 source line(s).
- Harness registration: `_begin_fstest auto quick cap idmapped mount`.
- Imported common libraries: `./common/preamble`, `./common/filter`.
- Capability and skip gates: `_require_idmapped_mounts`, `_require_test`.
- Local shell functions: none visible.
- External `$here/src` helpers: `$here/src/vfs/vfstest --test-fscaps-regression \`.

## Control Flow

- Capability gating runs first through `_require_idmapped_mounts`, `_require_test`.
- User-visible phase markers include:
- `line 19: echo "Silence is golden"`

## State and Persistence Behavior

Uses the configured xfstests test area or an explicitly created loop/image mount rather than always reformatting the scratch device. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick cap idmapped mount`, common helper libraries (`./common/preamble`, `./common/filter`), and the golden-output file `sources/test-tools/xfstests/tests/generic/644.out` (2 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_idmapped_mounts`, `_require_test`.

## Risks and Edge Cases

- Feature gates depend on kernel, userspace tool, and filesystem support; unsupported features correctly produce `_notrun`.

## Test Signals

The paired `.out` file has 2 line(s); its first visible signals are: 'QA output created by 644; Silence is golden'. Runtime pass/fail is primarily the command exit status plus golden-output comparison. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/644 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/645 -->
# sources/test-tools/xfstests/tests/generic/645

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/645`. Test that idmapped mounts behave correctly with complex user namespaces. It is registered with `_begin_fstest auto quick idmapped mount`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 28 source line(s).
- Harness registration: `_begin_fstest auto quick idmapped mount`.
- Imported common libraries: `./common/preamble`, `./common/filter`.
- Capability and skip gates: `_require_idmapped_mounts`, `_require_test`, `_require_chown`, `_wants_kernel_commit dacfd001eaf2 "fs/mnt_idmapping.c: Return -EINVAL when no map is written"`.
- Local shell functions: none visible.
- External `$here/src` helpers: `$here/src/vfs/vfstest --test-nested-userns \`.

## Control Flow

- Capability gating runs first through `_require_idmapped_mounts`, `_require_test`, `_require_chown`, `_wants_kernel_commit dacfd001eaf2 "fs/mnt_idmapping.c: Return -EINVAL when no map is written"`.
- User-visible phase markers include:
- `line 22: echo "Silence is golden"`

## State and Persistence Behavior

Uses the configured xfstests test area or an explicitly created loop/image mount rather than always reformatting the scratch device. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick idmapped mount`, common helper libraries (`./common/preamble`, `./common/filter`), and the golden-output file `sources/test-tools/xfstests/tests/generic/645.out` (2 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_idmapped_mounts`, `_require_test`, `_require_chown`, `_wants_kernel_commit dacfd001eaf2 "fs/mnt_idmapping.c: Return -EINVAL when no map is written"`.

## Risks and Edge Cases

- Feature gates depend on kernel, userspace tool, and filesystem support; unsupported features correctly produce `_notrun`.

## Test Signals

The paired `.out` file has 2 line(s); its first visible signals are: 'QA output created by 645; Silence is golden'. Runtime pass/fail is primarily the command exit status plus golden-output comparison. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/645 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/646 -->
# sources/test-tools/xfstests/tests/generic/646

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/646`. Testcase for kernel commit: 50d25484bebe xfs: sync lazy sb accounting on quiesce of read-only mounts After shutdown and readonly mount, a following read-write mount would get wrong number of available blocks. This is caused by unmounting the log on a readonly filesystem doesn't log the sb counters. It is registered with `_begin_fstest auto quick recoveryloop shutdown`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 44 source line(s).
- Harness registration: `_begin_fstest auto quick recoveryloop shutdown`.
- Imported common libraries: `./common/preamble`.
- Capability and skip gates: `_fixed_by_fs_commit xfs 50d25484bebe "xfs: sync lazy sb accounting on quiesce of read-only mounts"`, `_require_scratch`, `_require_scratch_shutdown`, `_require_metadata_journaling`.
- Local shell functions: none visible.
- External `$here/src` helpers: none visible.

## Control Flow

- Capability gating runs first through `_fixed_by_fs_commit xfs 50d25484bebe "xfs: sync lazy sb accounting on quiesce of read-only mounts"`, `_require_scratch`, `_require_scratch_shutdown`, `_require_metadata_journaling`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- User-visible phase markers include:
- `line 28: echo Testing > $SCRATCH_MNT/testfile`
- `line 42: echo "Silence is golden"`
- Key operational lines include:
- `line 21: _require_scratch_shutdown`
- `line 23: _scratch_mkfs > $seqres.full 2>&1`
- `line 25: _scratch_mount`
- `line 31: _scratch_shutdown -f`
- `line 33: _scratch_cycle_mount ro`
- `line 34: _scratch_cycle_mount`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Synthetic block-device state can be introduced through device-mapper, loop, SCSI debug, or huge-device helpers and must be cleaned even on failure. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick recoveryloop shutdown`, common helper libraries (`./common/preamble`), and the golden-output file `sources/test-tools/xfstests/tests/generic/646.out` (2 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_fixed_by_fs_commit xfs 50d25484bebe "xfs: sync lazy sb accounting on quiesce of read-only mounts"`, `_require_scratch`, `_require_scratch_shutdown`, `_require_metadata_journaling`.

## Risks and Edge Cases

- Failure-injection paths can leave mounts or synthetic device tables behind if cleanup is interrupted.

## Test Signals

The paired `.out` file has 2 line(s); its first visible signals are: 'QA output created by 646; Silence is golden'. Runtime pass/fail is also signaled by post-remount or failure-injection persistence checks. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/646 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/647 -->
# sources/test-tools/xfstests/tests/generic/647

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/647`. Trigger page faults in the same file during read and write It is registered with `_begin_fstest auto quick mmap`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 33 source line(s).
- Harness registration: `_begin_fstest auto quick mmap`.
- Imported common libraries: `./common/preamble`, `./common/filter`.
- Capability and skip gates: `_require_test`, `_require_odirect`, `_require_test_program mmap-rw-fault`.
- Local shell functions: `_cleanup`.
- External `$here/src` helpers: `$here/src/mmap-rw-fault $TEST_DIR/mmap-rw-fault.tmp`.

## Control Flow

- Capability gating runs first through `_require_test`, `_require_odirect`, `_require_test_program mmap-rw-fault`.
- User-visible phase markers include:
- `line 28: echo "Silence is golden"`
- Key operational lines include:
- `line 10: _begin_fstest auto quick mmap`
- `line 17: rm -f $TEST_DIR/mmap-rw-fault.tmp`
- `line 26: _require_test_program mmap-rw-fault`
- `line 30: $here/src/mmap-rw-fault $TEST_DIR/mmap-rw-fault.tmp`

## State and Persistence Behavior

Uses the configured xfstests test area or an explicitly created loop/image mount rather than always reformatting the scratch device. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick mmap`, common helper libraries (`./common/preamble`, `./common/filter`), and the golden-output file `sources/test-tools/xfstests/tests/generic/647.out` (2 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_test`, `_require_odirect`, `_require_test_program mmap-rw-fault`.

## Risks and Edge Cases

- Direct/AIO coverage depends on alignment, device logical block size, page size, and filesystem direct-I/O semantics.
- mmap/page-fault regressions are often race-prone and may manifest as hangs rather than clean command failures.

## Test Signals

The paired `.out` file has 2 line(s); its first visible signals are: 'QA output created by 647; Silence is golden'. Runtime pass/fail is primarily the command exit status plus golden-output comparison. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/647 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/648 -->
# sources/test-tools/xfstests/tests/generic/648

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/648`. Test nested log recovery with repeated (simulated) disk failures. We kick off fsstress on a loopback filesystem mounted on the scratch fs, then switch out the underlying scratch device with dm-error to see what happens when the disk goes down. Having taken down both fses in this manner, remount them and repeat. This test simulates VM hosts crashing to try to shake out CoW bugs in writeback on the host that cause VM guests to fail to recover. It is registered with `_begin_fstest shutdown auto log metadata eio recoveryloop`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 141 source line(s).
- Harness registration: `_begin_fstest shutdown auto log metadata eio recoveryloop`.
- Imported common libraries: `./common/preamble`, `./common/dmerror`, `./common/reflink`.
- Capability and skip gates: `_require_scratch_reflink`, `_require_cp_reflink`, `_require_dm_target error`, `_require_loop`, `_require_metadata_journaling $SCRATCH_DEV`.
- Local shell functions: `_cleanup`, `snap_loop_fs`.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `scratch_freesp_bytes=$(_get_available_space $SCRATCH_MNT)`
- `loopimg_bytes=$((scratch_freesp_bytes / 3))`
- `loopimg=$SCRATCH_MNT/testfs`
- `loopmnt=$tmp.mount`
- `scratch_aliveflag=$tmp.runsnap`
- `snap_aliveflag=$tmp.snapping`
- `is_unmounted=1`
- `is_unmounted=0`

## Control Flow

- Capability gating runs first through `_require_scratch_reflink`, `_require_cp_reflink`, `_require_dm_target error`, `_require_loop`, `_require_metadata_journaling $SCRATCH_DEV`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- User-visible phase markers include:
- `line 41: echo "Silence is golden."`
- `line 134: echo "final scratch mount failed"`
- Key operational lines include:
- `line 19: _kill_fsstress`
- `line 21: _unmount $loopmnt 2>/dev/null`
- `line 24: _dmerror_unmount`
- `line 25: _dmerror_cleanup`
- `line 36: _require_scratch_reflink`
- `line 37: _require_cp_reflink`
- `line 43: _scratch_mkfs >> $seqres.full 2>&1`
- `line 45: _dmerror_init`
- `line 46: _dmerror_mount`
- `line 54: _mkfs_dev $loopimg`
- `line 64: while [ -e "$scratch_aliveflag" ]; do`
- `line 66: _cp_reflink $loopimg $loopimg.a`
- `line 76: if ! _mount $loopimg $loopmnt -o loop; then`
- `line 83: _run_fsstress_bg -d "$loopmnt" -n 999999 -p "$((LOAD_FACTOR * 4))"`
- `line 95: _dmerror_load_error_table`
- `line 97: _kill_fsstress`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Synthetic block-device state can be introduced through device-mapper, loop, SCSI debug, or huge-device helpers and must be cleaned even on failure. Shared extent or atomic-update state is exercised, so correctness depends on clone/dedupe/exchange persistence and metadata ordering. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest shutdown auto log metadata eio recoveryloop`, common helper libraries (`./common/preamble`, `./common/dmerror`, `./common/reflink`), and the golden-output file `sources/test-tools/xfstests/tests/generic/648.out` (2 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_scratch_reflink`, `_require_cp_reflink`, `_require_dm_target error`, `_require_loop`, `_require_metadata_journaling $SCRATCH_DEV`.

## Risks and Edge Cases

- Failure-injection paths can leave mounts or synthetic device tables behind if cleanup is interrupted.
- Shared-extent and exchange operations can expose stale data, permission-bit, or log-ordering bugs that only appear after remount/recovery.

## Test Signals

The paired `.out` file has 2 line(s); its first visible signals are: 'QA output created by 648; Silence is golden.'. Runtime pass/fail is also signaled by hang/race detection through background work, loops, or timeout windows, post-remount or failure-injection persistence checks. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/648 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/649 -->
# sources/test-tools/xfstests/tests/generic/649

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/649`. Regression test for commit: 72a048c1056a ("xfs: only set IOMAP_F_SHARED when providing a srcmap to a write") If a user creates a sparse shared region in a file, convinces XFS to create a copy-on-write delayed allocation reservation spanning both the shared blocks and the holes, and then calls the fallocate unshare command to unshare the entire sparse region, XFS incorrectly tells iomap that the delalloc blocks for the holes are shared, which causes it to error out while trying to unshare a hole. It is registered with `_begin_fstest auto clone unshare punch`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 78 source line(s).
- Harness registration: `_begin_fstest auto clone unshare punch`.
- Imported common libraries: `./common/preamble`, `./common/reflink`, `./common/filter`.
- Capability and skip gates: `_fixed_by_fs_commit xfs 72a048c1056a "xfs: only set IOMAP_F_SHARED when providing a srcmap to a write"`, `_require_cp_reflink`, `_require_test_reflink`, `_require_test_program "punch-alternating"`, `_require_xfs_io_command "fpunch"	# make sure punch-alt can do its job`, `_require_xfs_io_command "funshare"`.
- Local shell functions: `_cleanup`.
- External `$here/src` helpers: `$here/src/punch-alternating -o 1 $file2`.
- Notable variables and constants:
- `file1=$TEST_DIR/$seq/a`
- `file2=$TEST_DIR/$seq/b`
- `f1sum0="$(md5sum $file1 | _filter_test_dir)"`
- `f2sum0="$(md5sum $file2 | _filter_test_dir)"`
- `f1sum1="$(md5sum $file1 | _filter_test_dir)"`
- `f2sum1="$(md5sum $file2 | _filter_test_dir)"`
- `f1sum2="$(md5sum $file1 | _filter_test_dir)"`
- `f2sum2="$(md5sum $file2 | _filter_test_dir)"`

## Control Flow

- Capability gating runs first through `_fixed_by_fs_commit xfs 72a048c1056a "xfs: only set IOMAP_F_SHARED when providing a srcmap to a write"`, `_require_cp_reflink`, `_require_test_reflink`, `_require_test_program "punch-alternating"`, `_require_xfs_io_command "fpunch"	# make sure punch-alt can do its job`, plus 1 more.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 76: echo Silence is golden`
- Key operational lines include:
- `line 37: _require_cp_reflink`
- `line 38: _require_test_reflink`
- `line 48: $XFS_IO_PROG -f -c "pwrite -S 0x58 -b 10m 0 10m" $file1 >> $seqres.full`
- `line 50: f1sum0="$(md5sum $file1 | _filter_test_dir)"`
- `line 52: _cp_reflink $file1 $file2`
- `line 55: f2sum0="$(md5sum $file2 | _filter_test_dir)"`
- `line 58: test "$FSTYP" = "xfs" && $XFS_IO_PROG -c 'cowextsize 0' $file2`
- `line 59: $XFS_IO_PROG -c "funshare 0 10m" $file2`
- `line 61: f1sum1="$(md5sum $file1 | _filter_test_dir)"`
- `line 62: f2sum1="$(md5sum $file2 | _filter_test_dir)"`
- `line 69: f1sum2="$(md5sum $file1 | _filter_test_dir)"`
- `line 70: f2sum2="$(md5sum $file2 | _filter_test_dir)"`

## State and Persistence Behavior

Uses the configured xfstests test area or an explicitly created loop/image mount rather than always reformatting the scratch device. Shared extent or atomic-update state is exercised, so correctness depends on clone/dedupe/exchange persistence and metadata ordering. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto clone unshare punch`, common helper libraries (`./common/preamble`, `./common/reflink`, `./common/filter`), and the golden-output file `sources/test-tools/xfstests/tests/generic/649.out` (2 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_fixed_by_fs_commit xfs 72a048c1056a "xfs: only set IOMAP_F_SHARED when providing a srcmap to a write"`, `_require_cp_reflink`, `_require_test_reflink`, `_require_test_program "punch-alternating"`, `_require_xfs_io_command "fpunch"	# make sure punch-alt can do its job`, `_require_xfs_io_command "funshare"`.

## Risks and Edge Cases

- Shared-extent and exchange operations can expose stale data, permission-bit, or log-ordering bugs that only appear after remount/recovery.

## Test Signals

The paired `.out` file has 2 line(s); its first visible signals are: 'QA output created by 649; Silence is golden'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands, xfstests output filters, hang/race detection through background work, loops, or timeout windows. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/649 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/650 -->
# sources/test-tools/xfstests/tests/generic/650

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/650`. Run an all-writes fsstress run with multiple threads while exercising CPU hotplugging to shake out bugs in the write path. It is registered with `_begin_fstest auto rw stress soak`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 91 source line(s).
- Harness registration: `_begin_fstest auto rw stress soak`.
- Imported common libraries: `./common/preamble`.
- Capability and skip gates: `_fixed_by_fs_commit xfs ecd49f7a36fb "xfs: fix per-cpu CIL structure aggregation racing with dying cpus"`, `_require_test`.
- Local shell functions: `_cleanup`, `exercise_cpu_hotplug`.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `sysfs_cpu_dir="/sys/devices/system/cpu"`
- `nrcpus=$(getconf _NPROCESSORS_CONF)`
- `hotplug_cpus=()`
- `nr_hotplug_cpus="${#hotplug_cpus[@]}"`
- `stress_dir="$TEST_DIR/$seq"`
- `sentinel_file=$tmp.hotplug`
- `fsstress_args=(-w -d $stress_dir)`
- `nr_cpus=$((LOAD_FACTOR * nr_hotplug_cpus))`
- `nr_ops=$((2500 * TIME_FACTOR))`

## Control Flow

- Capability gating runs first through `_fixed_by_fs_commit xfs ecd49f7a36fb "xfs: fix per-cpu CIL structure aggregation racing with dying cpus"`, `_require_test`.
- User-visible phase markers include:
- `line 22: echo 1 > "$i" 2>/dev/null`
- `line 36: echo "$action" > "$sysfs_cpu_dir/cpu$cpu/online" 2>/dev/null`
- `line 56: echo "Silence is golden."`
- Key operational lines include:
- `line 19: _kill_fsstress`
- `line 31: while [ -e $sentinel_file ]; do`
- `line 62: fsstress_args=(-w -d $stress_dir)`
- `line 68: fsstress_args+=(-p $nr_cpus)`
- `line 71: fsstress_args+=(--duration="$((SOAK_DURATION / 10))")`
- `line 74: fsstress_args+=(--duration=3)`
- `line 78: fsstress_args+=(-n $nr_ops)`
- `line 82: _run_fsstress "${fsstress_args[@]}"`

## State and Persistence Behavior

Uses the configured xfstests test area or an explicitly created loop/image mount rather than always reformatting the scratch device. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto rw stress soak`, common helper libraries (`./common/preamble`), and the golden-output file `sources/test-tools/xfstests/tests/generic/650.out` (2 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_fixed_by_fs_commit xfs ecd49f7a36fb "xfs: fix per-cpu CIL structure aggregation racing with dying cpus"`, `_require_test`.

## Risks and Edge Cases

- Most failures should surface as unexpected output, nonzero helper status, or harness `_fail`/`_notrun` behavior.

## Test Signals

The paired `.out` file has 2 line(s); its first visible signals are: 'QA output created by 650; Silence is golden.'. Runtime pass/fail is also signaled by hang/race detection through background work, loops, or timeout windows. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/650 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/651 -->
# sources/test-tools/xfstests/tests/generic/651

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/651`. See what happens if we MMAP CoW blocks 2-4 of a page's worth of blocks when the second block is a regular block. (MMAP version of generic/205,206) This test is dependent on the system page size, so we cannot use md5 in the golden output; we can only compare to a check file. It is registered with `_begin_fstest auto quick clone mmap`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 67 source line(s).
- Harness registration: `_begin_fstest auto quick clone mmap`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/reflink`.
- Capability and skip gates: `_require_scratch_reflink`.
- Local shell functions: none visible.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `pagesz=$(getconf PAGE_SIZE)`
- `blksz=$((pagesz / 4))`
- `testdir=$SCRATCH_MNT/test-$seq`
- `real_blksz=$(_get_file_block_size $testdir)`

## Control Flow

- Capability gating runs first through `_require_scratch_reflink`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 24: echo "Format and mount"`
- `line 34: echo "Create the original files"`
- `line 50: echo "Compare files"`
- `line 54: echo "CoW and unmount"`
- `line 61: echo "Compare files"`
- Key operational lines include:
- `line 13: _begin_fstest auto quick clone mmap`
- `line 19: _require_scratch_reflink`
- `line 25: _scratch_mkfs_blocksized $blksz > $seqres.full 2>&1`
- `line 26: _scratch_mount >> $seqres.full 2>&1`
- `line 37: $XFS_IO_PROG -f -c "truncate $pagesz" $testdir/file2 >> $seqres.full`
- `line 38: $XFS_IO_PROG -f -c "truncate $pagesz" $testdir/file2.chk >> $seqres.full`
- `line 46: _reflink_range $testdir/file1 $blksz $testdir/file2 $((blksz * 2)) $blksz >> $seqres.full`
- `line 48: _scratch_cycle_mount`
- `line 51: cmp -s $testdir/file1 $testdir/file2 && echo "file1 and file2 should not match."`
- `line 52: cmp -s $testdir/file2 $testdir/file2.chk || echo "file2 and file2.chk don't match."`
- `line 55: $XFS_IO_PROG -f -c "mmap 0 $pagesz" \`
- `line 57: $XFS_IO_PROG -f -c "mmap 0 $pagesz" \`
- `line 59: _scratch_cycle_mount`
- `line 62: cmp -s $testdir/file1 $testdir/file2 && echo "file1 and file2 should not match."`
- `line 63: cmp -s $testdir/file2 $testdir/file2.chk || echo "file2 and file2.chk don't match."`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Shared extent or atomic-update state is exercised, so correctness depends on clone/dedupe/exchange persistence and metadata ordering. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick clone mmap`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/reflink`), and the golden-output file `sources/test-tools/xfstests/tests/generic/651.out` (6 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_scratch_reflink`.

## Risks and Edge Cases

- mmap/page-fault regressions are often race-prone and may manifest as hangs rather than clean command failures.
- Shared-extent and exchange operations can expose stale data, permission-bit, or log-ordering bugs that only appear after remount/recovery.

## Test Signals

The paired `.out` file has 6 line(s); its first visible signals are: 'QA output created by 651; Format and mount; Create the original files; Compare files; CoW and unmount'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands, hang/race detection through background work, loops, or timeout windows, post-remount or failure-injection persistence checks. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/651 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/652 -->
# sources/test-tools/xfstests/tests/generic/652

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/652`. See what happens if we MMAP CoW blocks 2-4 of a page's worth of blocks when the second block is a unwritten block. (MMAP version of generic/216,217) This test is dependent on the system page size, so we cannot use md5 in the golden output; we can only compare to a check file. It is registered with `_begin_fstest auto quick clone prealloc mmap`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 68 source line(s).
- Harness registration: `_begin_fstest auto quick clone prealloc mmap`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/reflink`.
- Capability and skip gates: `_require_scratch_reflink`, `_require_xfs_io_command "falloc"`.
- Local shell functions: none visible.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `pagesz=$(getconf PAGE_SIZE)`
- `blksz=$((pagesz / 4))`
- `testdir=$SCRATCH_MNT/test-$seq`
- `real_blksz=$(_get_file_block_size $testdir)`

## Control Flow

- Capability gating runs first through `_require_scratch_reflink`, `_require_xfs_io_command "falloc"`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 25: echo "Format and mount"`
- `line 35: echo "Create the original files"`
- `line 51: echo "Compare files"`
- `line 55: echo "CoW and unmount"`
- `line 62: echo "Compare files"`
- Key operational lines include:
- `line 13: _begin_fstest auto quick clone prealloc mmap`
- `line 19: _require_scratch_reflink`
- `line 20: _require_xfs_io_command "falloc"`
- `line 26: _scratch_mkfs_blocksized $blksz > $seqres.full 2>&1`
- `line 27: _scratch_mount >> $seqres.full 2>&1`
- `line 38: $XFS_IO_PROG -f -c "truncate $pagesz" $testdir/file2 >> $seqres.full`
- `line 39: $XFS_IO_PROG -f -c "truncate $pagesz" $testdir/file2.chk >> $seqres.full`
- `line 41: $XFS_IO_PROG -f -c "falloc -k $blksz $blksz" $testdir/file2 >> $seqres.full`
- `line 44: $XFS_IO_PROG -f -c "falloc -k $((blksz * 3)) $blksz" $testdir/file2 >> $seqres.full`
- `line 47: _reflink_range $testdir/file1 $blksz $testdir/file2 $((blksz * 2)) $blksz >> $seqres.full`
- `line 49: _scratch_cycle_mount`
- `line 52: cmp -s $testdir/file1 $testdir/file2 && echo "file1 and file2 should not match."`
- `line 53: cmp -s $testdir/file2 $testdir/file2.chk || echo "file2 and file2.chk don't match."`
- `line 56: $XFS_IO_PROG -f -c "mmap 0 $pagesz" \`
- `line 58: $XFS_IO_PROG -f -c "mmap 0 $pagesz" \`
- `line 60: _scratch_cycle_mount`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Shared extent or atomic-update state is exercised, so correctness depends on clone/dedupe/exchange persistence and metadata ordering. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick clone prealloc mmap`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/reflink`), and the golden-output file `sources/test-tools/xfstests/tests/generic/652.out` (6 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_scratch_reflink`, `_require_xfs_io_command "falloc"`.

## Risks and Edge Cases

- mmap/page-fault regressions are often race-prone and may manifest as hangs rather than clean command failures.
- Shared-extent and exchange operations can expose stale data, permission-bit, or log-ordering bugs that only appear after remount/recovery.

## Test Signals

The paired `.out` file has 6 line(s); its first visible signals are: 'QA output created by 652; Format and mount; Create the original files; Compare files; CoW and unmount'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands, hang/race detection through background work, loops, or timeout windows, post-remount or failure-injection persistence checks. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/652 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/653 -->
# sources/test-tools/xfstests/tests/generic/653

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/653`. See what happens if we MMAP CoW blocks 2-4 of a page's worth of blocks when the second block is a hole. (MMAP version of generic/218,220) This test is dependent on the system page size, so we cannot use md5 in the golden output; we can only compare to a check file. It is registered with `_begin_fstest auto quick clone prealloc mmap`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 62 source line(s).
- Harness registration: `_begin_fstest auto quick clone prealloc mmap`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/reflink`.
- Capability and skip gates: `_require_scratch_reflink`, `_require_xfs_io_command "falloc"`.
- Local shell functions: none visible.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `pagesz=$(getconf PAGE_SIZE)`
- `blksz=$((pagesz / 4))`
- `testdir=$SCRATCH_MNT/test-$seq`
- `real_blksz=$(_get_file_block_size $testdir)`

## Control Flow

- Capability gating runs first through `_require_scratch_reflink`, `_require_xfs_io_command "falloc"`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 25: echo "Format and mount"`
- `line 35: echo "Create the original files"`
- `line 45: echo "Compare files"`
- `line 49: echo "CoW and unmount"`
- `line 56: echo "Compare files"`
- Key operational lines include:
- `line 13: _begin_fstest auto quick clone prealloc mmap`
- `line 19: _require_scratch_reflink`
- `line 20: _require_xfs_io_command "falloc"`
- `line 26: _scratch_mkfs_blocksized $blksz > $seqres.full 2>&1`
- `line 27: _scratch_mount >> $seqres.full 2>&1`
- `line 38: $XFS_IO_PROG -f -c "truncate $pagesz" $testdir/file2 >> $seqres.full`
- `line 39: $XFS_IO_PROG -f -c "truncate $pagesz" $testdir/file2.chk >> $seqres.full`
- `line 41: _reflink_range $testdir/file1 $blksz $testdir/file2 $((blksz * 2)) $blksz >> $seqres.full`
- `line 43: _scratch_cycle_mount`
- `line 46: cmp -s $testdir/file1 $testdir/file2 && echo "file1 and file2 should not match."`
- `line 47: cmp -s $testdir/file2 $testdir/file2.chk || echo "file2 and file2.chk don't match."`
- `line 50: $XFS_IO_PROG -f -c "mmap 0 $pagesz" \`
- `line 52: $XFS_IO_PROG -f -c "mmap 0 $pagesz" \`
- `line 54: _scratch_cycle_mount`
- `line 57: cmp -s $testdir/file1 $testdir/file2 && echo "file1 and file2 should not match."`
- `line 58: cmp -s $testdir/file2 $testdir/file2.chk || echo "file2 and file2.chk don't match."`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Shared extent or atomic-update state is exercised, so correctness depends on clone/dedupe/exchange persistence and metadata ordering. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick clone prealloc mmap`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/reflink`), and the golden-output file `sources/test-tools/xfstests/tests/generic/653.out` (6 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_scratch_reflink`, `_require_xfs_io_command "falloc"`.

## Risks and Edge Cases

- mmap/page-fault regressions are often race-prone and may manifest as hangs rather than clean command failures.
- Shared-extent and exchange operations can expose stale data, permission-bit, or log-ordering bugs that only appear after remount/recovery.

## Test Signals

The paired `.out` file has 6 line(s); its first visible signals are: 'QA output created by 653; Format and mount; Create the original files; Compare files; CoW and unmount'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands, hang/race detection through background work, loops, or timeout windows, post-remount or failure-injection persistence checks. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/653 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/654 -->
# sources/test-tools/xfstests/tests/generic/654

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/654`. See what happens if we MMAP CoW blocks 2-4 of a page's worth of blocks when the second block is delalloc. (MMAP version of generic/222,227) This test is dependent on the system page size, so we cannot use md5 in the golden output; we can only compare to a check file. It is registered with `_begin_fstest auto quick clone fiemap prealloc mmap`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 72 source line(s).
- Harness registration: `_begin_fstest auto quick clone fiemap prealloc mmap`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/reflink`.
- Capability and skip gates: `_require_scratch_reflink`, `_require_xfs_io_command "falloc"`, `_notrun "test requires delayed allocation writes"`.
- Local shell functions: none visible.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `pagesz=$(getconf PAGE_SIZE)`
- `blksz=$((pagesz / 4))`
- `testdir=$SCRATCH_MNT/test-$seq`
- `real_blksz=$(_get_file_block_size $testdir)`

## Control Flow

- Capability gating runs first through `_require_scratch_reflink`, `_require_xfs_io_command "falloc"`, `_notrun "test requires delayed allocation writes"`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 25: echo "Format and mount"`
- `line 35: echo "Create the original files"`
- `line 45: echo "Compare files"`
- `line 49: echo "CoW and unmount"`
- `line 66: echo "Compare files"`
- Key operational lines include:
- `line 13: _begin_fstest auto quick clone fiemap prealloc mmap`
- `line 19: _require_scratch_reflink`
- `line 20: _require_xfs_io_command "falloc"`
- `line 26: _scratch_mkfs_blocksized $blksz > $seqres.full 2>&1`
- `line 27: _scratch_mount >> $seqres.full 2>&1`
- `line 38: $XFS_IO_PROG -f -c "truncate $pagesz" $testdir/file2 >> $seqres.full`
- `line 39: $XFS_IO_PROG -f -c "truncate $pagesz" $testdir/file2.chk >> $seqres.full`
- `line 41: _reflink_range $testdir/file1 $blksz $testdir/file2 $((blksz * 2)) $blksz >> $seqres.full`
- `line 43: _scratch_cycle_mount`
- `line 46: cmp -s $testdir/file1 $testdir/file2 && echo "file1 and file2 should not match."`
- `line 47: cmp -s $testdir/file2 $testdir/file2.chk || echo "file2 and file2.chk don't match."`
- `line 60: $XFS_IO_PROG -f -c "mmap 0 $pagesz" \`
- `line 62: $XFS_IO_PROG -f -c "mmap 0 $pagesz" \`
- `line 64: _scratch_cycle_mount`
- `line 67: cmp -s $testdir/file1 $testdir/file2 && echo "file1 and file2 should not match."`
- `line 68: cmp -s $testdir/file2 $testdir/file2.chk || echo "file2 and file2.chk don't match."`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Shared extent or atomic-update state is exercised, so correctness depends on clone/dedupe/exchange persistence and metadata ordering. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick clone fiemap prealloc mmap`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/reflink`), and the golden-output file `sources/test-tools/xfstests/tests/generic/654.out` (6 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_scratch_reflink`, `_require_xfs_io_command "falloc"`, `_notrun "test requires delayed allocation writes"`.

## Risks and Edge Cases

- mmap/page-fault regressions are often race-prone and may manifest as hangs rather than clean command failures.
- Shared-extent and exchange operations can expose stale data, permission-bit, or log-ordering bugs that only appear after remount/recovery.

## Test Signals

The paired `.out` file has 6 line(s); its first visible signals are: 'QA output created by 654; Format and mount; Create the original files; Compare files; CoW and unmount'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands, hang/race detection through background work, loops, or timeout windows, post-remount or failure-injection persistence checks. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/654 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/655 -->
# sources/test-tools/xfstests/tests/generic/655

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/655`. See what happens if we MMAP CoW blocks 2-4 of a page's worth of blocks when the surrounding blocks vary between unwritten/regular/delalloc/hole. (MMAP version of generic/229,238) This test is dependent on the system page size, so we cannot use md5 in the golden output; we can only compare to a check file. It is registered with `_begin_fstest auto quick clone fiemap prealloc mmap`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 131 source line(s).
- Harness registration: `_begin_fstest auto quick clone fiemap prealloc mmap`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/reflink`.
- Capability and skip gates: `_require_scratch_reflink`, `_require_xfs_io_command "falloc"`, `_notrun "test requires delayed allocation writes"`, `_notrun "test requires delayed allocation writes"`.
- Local shell functions: `runtest`.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `pagesz=$(getconf PAGE_SIZE)`
- `blksz=$((pagesz / 4))`
- `testdir=$SCRATCH_MNT/test-$seq`
- `real_blksz=$(_get_file_block_size $testdir)`
- `b2=$1`
- `b4=$2`
- `dir=$3`

## Control Flow

- Capability gating runs first through `_require_scratch_reflink`, `_require_xfs_io_command "falloc"`, `_notrun "test requires delayed allocation writes"`, `_notrun "test requires delayed allocation writes"`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 26: echo "Format and mount"`
- `line 37: echo "runtest $1 $2"`
- `line 42: echo "Create the original files"`
- `line 79: echo "Compare files"`
- `line 83: echo "CoW and unmount"`
- `line 108: echo "Compare files"`
- Key operational lines include:
- `line 14: _begin_fstest auto quick clone fiemap prealloc mmap`
- `line 20: _require_scratch_reflink`
- `line 21: _require_xfs_io_command "falloc"`
- `line 27: _scratch_mkfs_blocksized $blksz > $seqres.full 2>&1`
- `line 28: _scratch_mount >> $seqres.full 2>&1`
- `line 46: $XFS_IO_PROG -f -c "truncate $pagesz" $dir/file2 >> $seqres.full`
- `line 47: $XFS_IO_PROG -f -c "truncate $pagesz" $dir/file2.chk >> $seqres.full`
- `line 55: $XFS_IO_PROG -f -c "falloc -k $blksz $blksz" $dir/file2 >> $seqres.full`
- `line 68: $XFS_IO_PROG -f -c "falloc -k $((blksz * 3)) $blksz" $dir/file2 >> $seqres.full`
- `line 75: _reflink_range $dir/file1 $blksz $dir/file2 $((blksz * 2)) $blksz >> $seqres.full`
- `line 77: _scratch_cycle_mount`
- `line 80: cmp -s $dir/file1 $dir/file2 && echo "file1 and file2 should not match."`
- `line 81: cmp -s $dir/file2 $dir/file2.chk || echo "file2 and file2.chk don't match."`
- `line 102: $XFS_IO_PROG -f -c "mmap 0 $pagesz" \`
- `line 104: $XFS_IO_PROG -f -c "mmap 0 $pagesz" \`
- `line 106: _scratch_cycle_mount`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Shared extent or atomic-update state is exercised, so correctness depends on clone/dedupe/exchange persistence and metadata ordering. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick clone fiemap prealloc mmap`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/reflink`), and the golden-output file `sources/test-tools/xfstests/tests/generic/655.out` (62 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_scratch_reflink`, `_require_xfs_io_command "falloc"`, `_notrun "test requires delayed allocation writes"`, `_notrun "test requires delayed allocation writes"`.

## Risks and Edge Cases

- mmap/page-fault regressions are often race-prone and may manifest as hangs rather than clean command failures.
- Shared-extent and exchange operations can expose stale data, permission-bit, or log-ordering bugs that only appear after remount/recovery.

## Test Signals

The paired `.out` file has 62 line(s); its first visible signals are: 'QA output created by 655; Format and mount; runtest regular delalloc; Create the original files; Compare files'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands, hang/race detection through background work, loops, or timeout windows, post-remount or failure-injection persistence checks. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/655 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/656 -->
# sources/test-tools/xfstests/tests/generic/656

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/656`. This is a test for the fix commit 968219708108 ("fs: handle circular mappings correctly") in Linux. It verifies that setattr for {g,u}id work correctly. It is registered with `_begin_fstest auto attr cap idmapped mount perms`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 32 source line(s).
- Harness registration: `_begin_fstest auto attr cap idmapped mount perms`.
- Imported common libraries: `./common/preamble`, `./common/filter`.
- Capability and skip gates: `_require_idmapped_mounts`, `_require_test`, `_require_chown`, `_require_user fsgqa`, `_require_user fsgqa2`, `_require_group fsgqa`, `_require_group fsgqa2`.
- Local shell functions: none visible.
- External `$here/src` helpers: `$here/src/vfs/vfstest --test-setattr-fix-968219708108 \`.

## Control Flow

- Capability gating runs first through `_require_idmapped_mounts`, `_require_test`, `_require_chown`, `_require_user fsgqa`, `_require_user fsgqa2`, plus 2 more.
- User-visible phase markers include:
- `line 26: echo "Silence is golden"`

## State and Persistence Behavior

Uses the configured xfstests test area or an explicitly created loop/image mount rather than always reformatting the scratch device. Extended attributes are part of the persistent state being created, replayed, or verified. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto attr cap idmapped mount perms`, common helper libraries (`./common/preamble`, `./common/filter`), and the golden-output file `sources/test-tools/xfstests/tests/generic/656.out` (2 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_idmapped_mounts`, `_require_test`, `_require_chown`, `_require_user fsgqa`, `_require_user fsgqa2`, `_require_group fsgqa`, `_require_group fsgqa2`.

## Risks and Edge Cases

- Feature gates depend on kernel, userspace tool, and filesystem support; unsupported features correctly produce `_notrun`.

## Test Signals

The paired `.out` file has 2 line(s); its first visible signals are: 'QA output created by 656; Silence is golden'. Runtime pass/fail is primarily the command exit status plus golden-output comparison. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/656 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/657 -->
# sources/test-tools/xfstests/tests/generic/657

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/657`. Ensuring that copy on write in mmap mode works when the CoW range originally covers multiple extents. (MMAP version of generic/185,183) - Create two files - Reflink the odd blocks of the first file into a third file. - Reflink the even blocks of the second file into the third file. - mmap CoW across the halfway mark. - Check that the files are now different where we say they're different. It is registered with `_begin_fstest auto quick clone mmap`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 68 source line(s).
- Harness registration: `_begin_fstest auto quick clone mmap`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/reflink`.
- Capability and skip gates: `_require_scratch_reflink`.
- Local shell functions: none visible.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `testdir=$SCRATCH_MNT/test-$seq`
- `blksz=65536`
- `nr=64`
- `filesize=$((blksz * nr))`
- `cowoff=$((filesize / 4))`
- `cowsz=$((filesize / 2))`
- `mmapsz=$((cowoff + cowsz))`

## Control Flow

- Capability gating runs first through `_require_scratch_reflink`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 23: echo "Format and mount"`
- `line 30: echo "Create the original files"`
- `line 46: echo "Compare files"`
- `line 52: echo "mmap CoW across the transition"`
- `line 60: echo "Compare files"`
- Key operational lines include:
- `line 15: _begin_fstest auto quick clone mmap`
- `line 21: _require_scratch_reflink`
- `line 24: _scratch_mkfs > $seqres.full 2>&1`
- `line 25: _scratch_mount >> $seqres.full 2>&1`
- `line 37: _reflink_range $testdir/file1 $((blksz * f)) $testdir/file3 $((blksz * f)) $blksz >> $seqres.full`
- `line 41: _reflink_range $testdir/file2 $((blksz * f)) $testdir/file3 $((blksz * f)) $blksz >> $seqres.full`
- `line 44: _scratch_cycle_mount`
- `line 47: md5sum $testdir/file1 | _filter_scratch`
- `line 48: md5sum $testdir/file2 | _filter_scratch`
- `line 49: md5sum $testdir/file3 | _filter_scratch`
- `line 50: md5sum $testdir/file3.chk | _filter_scratch`
- `line 52: echo "mmap CoW across the transition"`
- `line 55: mmapsz=$((cowoff + cowsz))`
- `line 56: _mwrite_byte 0x63 $cowoff $cowsz $mmapsz $testdir/file3 >> $seqres.full`
- `line 57: _mwrite_byte 0x63 $cowoff $cowsz $mmapsz $testdir/file3.chk >> $seqres.full`
- `line 58: _scratch_cycle_mount`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Shared extent or atomic-update state is exercised, so correctness depends on clone/dedupe/exchange persistence and metadata ordering. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick clone mmap`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/reflink`), and the golden-output file `sources/test-tools/xfstests/tests/generic/657.out` (14 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_scratch_reflink`.

## Risks and Edge Cases

- mmap/page-fault regressions are often race-prone and may manifest as hangs rather than clean command failures.
- Shared-extent and exchange operations can expose stale data, permission-bit, or log-ordering bugs that only appear after remount/recovery.

## Test Signals

The paired `.out` file has 14 line(s); its first visible signals are: 'QA output created by 657; Format and mount; Create the original files; Compare files; bdbcf02ee0aa977795a79d25fcfdccb1  SCRATCH_MNT/test-657/file1'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands, xfstests output filters, post-remount or failure-injection persistence checks. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/657 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/658 -->
# sources/test-tools/xfstests/tests/generic/658

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/658`. Ensuring that copy on write in mmap mode works when the CoW range originally covers multiple extents, some regular, some not. (MMAP version of generic/197,196) - Create two files. - Reflink the odd blocks of the first file into the second file. - mmap CoW across the halfway mark, starting with the unwritten extent. - Check that the files are now different where we say they're different. It is registered with `_begin_fstest auto quick clone prealloc mmap`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 58 source line(s).
- Harness registration: `_begin_fstest auto quick clone prealloc mmap`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/reflink`.
- Capability and skip gates: `_require_scratch_reflink`, `_require_xfs_io_command "falloc"`.
- Local shell functions: none visible.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `testdir=$SCRATCH_MNT/test-$seq`
- `blksz=65536`
- `nr=64`
- `filesize=$((blksz * nr))`
- `cowoff=$((filesize / 4))`
- `cowsz=$((filesize / 2))`
- `mmapsz=$((cowoff + cowsz))`

## Control Flow

- Capability gating runs first through `_require_scratch_reflink`, `_require_xfs_io_command "falloc"`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 24: echo "Format and mount"`
- `line 31: echo "Create the original files"`
- `line 38: echo "Compare files"`
- `line 43: echo "mmap CoW across the transition"`
- `line 51: echo "Compare files"`
- Key operational lines include:
- `line 15: _begin_fstest auto quick clone prealloc mmap`
- `line 21: _require_scratch_reflink`
- `line 22: _require_xfs_io_command "falloc"`
- `line 25: _scratch_mkfs > $seqres.full 2>&1`
- `line 26: _scratch_mount >> $seqres.full 2>&1`
- `line 35: _weave_reflink_regular $blksz $nr $testdir/file1 $testdir/file3 >> $seqres.full`
- `line 36: _scratch_cycle_mount`
- `line 39: md5sum $testdir/file1 | _filter_scratch`
- `line 40: md5sum $testdir/file3 | _filter_scratch`
- `line 41: md5sum $testdir/file3.chk | _filter_scratch`
- `line 43: echo "mmap CoW across the transition"`
- `line 46: mmapsz=$((cowoff + cowsz))`
- `line 47: _mwrite_byte 0x63 $cowoff $cowsz $mmapsz $testdir/file3 >> $seqres.full`
- `line 48: _mwrite_byte 0x63 $cowoff $cowsz $mmapsz $testdir/file3.chk >> $seqres.full`
- `line 49: _scratch_cycle_mount`
- `line 52: md5sum $testdir/file1 | _filter_scratch`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Shared extent or atomic-update state is exercised, so correctness depends on clone/dedupe/exchange persistence and metadata ordering. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick clone prealloc mmap`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/reflink`), and the golden-output file `sources/test-tools/xfstests/tests/generic/658.out` (12 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_scratch_reflink`, `_require_xfs_io_command "falloc"`.

## Risks and Edge Cases

- mmap/page-fault regressions are often race-prone and may manifest as hangs rather than clean command failures.
- Shared-extent and exchange operations can expose stale data, permission-bit, or log-ordering bugs that only appear after remount/recovery.

## Test Signals

The paired `.out` file has 12 line(s); its first visible signals are: 'QA output created by 658; Format and mount; Create the original files; Compare files; bdbcf02ee0aa977795a79d25fcfdccb1  SCRATCH_MNT/test-658/file1'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands, xfstests output filters, post-remount or failure-injection persistence checks. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/658 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/659 -->
# sources/test-tools/xfstests/tests/generic/659

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/659`. Ensuring that copy on write in mmap mode works when the CoW range originally covers multiple extents, some unwritten, some not. (MMAP version of generic/189,188) - Create a file and fallocate a second file. - Reflink the odd blocks of the first file into the second file. - mmap CoW across the halfway mark, starting with the unwritten extent. - Check that the files are now different where we say they're different. It is registered with `_begin_fstest auto quick clone prealloc mmap`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 58 source line(s).
- Harness registration: `_begin_fstest auto quick clone prealloc mmap`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/reflink`.
- Capability and skip gates: `_require_scratch_reflink`, `_require_xfs_io_command "falloc"`.
- Local shell functions: none visible.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `testdir=$SCRATCH_MNT/test-$seq`
- `blksz=65536`
- `nr=64`
- `filesize=$((blksz * nr))`
- `cowoff=$((filesize / 4))`
- `cowsz=$((filesize / 2))`
- `mmapsz=$((cowoff + cowsz))`

## Control Flow

- Capability gating runs first through `_require_scratch_reflink`, `_require_xfs_io_command "falloc"`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 24: echo "Format and mount"`
- `line 31: echo "Create the original files"`
- `line 38: echo "Compare files"`
- `line 43: echo "mmap CoW across the transition"`
- `line 51: echo "Compare files"`
- Key operational lines include:
- `line 15: _begin_fstest auto quick clone prealloc mmap`
- `line 21: _require_scratch_reflink`
- `line 22: _require_xfs_io_command "falloc"`
- `line 25: _scratch_mkfs > $seqres.full 2>&1`
- `line 26: _scratch_mount >> $seqres.full 2>&1`
- `line 35: _weave_reflink_unwritten $blksz $nr $testdir/file1 $testdir/file3 >> $seqres.full`
- `line 36: _scratch_cycle_mount`
- `line 39: md5sum $testdir/file1 | _filter_scratch`
- `line 40: md5sum $testdir/file3 | _filter_scratch`
- `line 41: md5sum $testdir/file3.chk | _filter_scratch`
- `line 43: echo "mmap CoW across the transition"`
- `line 46: mmapsz=$((cowoff + cowsz))`
- `line 47: _mwrite_byte 0x63 $cowoff $cowsz $mmapsz $testdir/file3 >> $seqres.full`
- `line 48: _mwrite_byte 0x63 $cowoff $cowsz $mmapsz $testdir/file3.chk >> $seqres.full`
- `line 49: _scratch_cycle_mount`
- `line 52: md5sum $testdir/file1 | _filter_scratch`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Shared extent or atomic-update state is exercised, so correctness depends on clone/dedupe/exchange persistence and metadata ordering. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick clone prealloc mmap`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/reflink`), and the golden-output file `sources/test-tools/xfstests/tests/generic/659.out` (12 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_scratch_reflink`, `_require_xfs_io_command "falloc"`.

## Risks and Edge Cases

- mmap/page-fault regressions are often race-prone and may manifest as hangs rather than clean command failures.
- Shared-extent and exchange operations can expose stale data, permission-bit, or log-ordering bugs that only appear after remount/recovery.

## Test Signals

The paired `.out` file has 12 line(s); its first visible signals are: 'QA output created by 659; Format and mount; Create the original files; Compare files; bdbcf02ee0aa977795a79d25fcfdccb1  SCRATCH_MNT/test-659/file1'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands, xfstests output filters, post-remount or failure-injection persistence checks. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/659 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/660 -->
# sources/test-tools/xfstests/tests/generic/660

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/660`. Ensuring that copy on write in mmap mode works when the CoW range originally covers multiple extents, some holes, some not. (MMAP version of generic/191,190) - Create a file and truncate a second file. - Reflink the odd blocks of the first file into the second file. - mmap CoW across the halfway mark, starting with the unwritten extent. - Check that the files are now different where we say they're different. It is registered with `_begin_fstest auto quick clone prealloc mmap`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 58 source line(s).
- Harness registration: `_begin_fstest auto quick clone prealloc mmap`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/reflink`.
- Capability and skip gates: `_require_scratch_reflink`, `_require_xfs_io_command "falloc"`.
- Local shell functions: none visible.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `testdir=$SCRATCH_MNT/test-$seq`
- `blksz=65536`
- `nr=64`
- `filesize=$((blksz * nr))`
- `cowoff=$((filesize / 4))`
- `cowsz=$((filesize / 2))`
- `mmapsz=$((cowoff + cowsz))`

## Control Flow

- Capability gating runs first through `_require_scratch_reflink`, `_require_xfs_io_command "falloc"`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 24: echo "Format and mount"`
- `line 31: echo "Create the original files"`
- `line 38: echo "Compare files"`
- `line 43: echo "mmap CoW across the transition"`
- `line 51: echo "Compare files"`
- Key operational lines include:
- `line 15: _begin_fstest auto quick clone prealloc mmap`
- `line 21: _require_scratch_reflink`
- `line 22: _require_xfs_io_command "falloc"`
- `line 25: _scratch_mkfs > $seqres.full 2>&1`
- `line 26: _scratch_mount >> $seqres.full 2>&1`
- `line 35: _weave_reflink_holes $blksz $nr $testdir/file1 $testdir/file3 >> $seqres.full`
- `line 36: _scratch_cycle_mount`
- `line 39: md5sum $testdir/file1 | _filter_scratch`
- `line 40: md5sum $testdir/file3 | _filter_scratch`
- `line 41: md5sum $testdir/file3.chk | _filter_scratch`
- `line 43: echo "mmap CoW across the transition"`
- `line 46: mmapsz=$((cowoff + cowsz))`
- `line 47: _mwrite_byte 0x63 $cowoff $cowsz $mmapsz $testdir/file3 >> $seqres.full`
- `line 48: _mwrite_byte 0x63 $cowoff $cowsz $mmapsz $testdir/file3.chk >> $seqres.full`
- `line 49: _scratch_cycle_mount`
- `line 52: md5sum $testdir/file1 | _filter_scratch`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Shared extent or atomic-update state is exercised, so correctness depends on clone/dedupe/exchange persistence and metadata ordering. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick clone prealloc mmap`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/reflink`), and the golden-output file `sources/test-tools/xfstests/tests/generic/660.out` (12 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_scratch_reflink`, `_require_xfs_io_command "falloc"`.

## Risks and Edge Cases

- mmap/page-fault regressions are often race-prone and may manifest as hangs rather than clean command failures.
- Shared-extent and exchange operations can expose stale data, permission-bit, or log-ordering bugs that only appear after remount/recovery.

## Test Signals

The paired `.out` file has 12 line(s); its first visible signals are: 'QA output created by 660; Format and mount; Create the original files; Compare files; bdbcf02ee0aa977795a79d25fcfdccb1  SCRATCH_MNT/test-660/file1'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands, xfstests output filters, post-remount or failure-injection persistence checks. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/660 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/661 -->
# sources/test-tools/xfstests/tests/generic/661

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/661`. Ensuring that copy on write in mmap mode works when the CoW range originally covers multiple extents, some delalloc, some not. (MMAP version of generic/195,194) - Create a file. - Reflink the odd blocks of the first file into the second file. - Buffered write the even blocks of the second file. - mmap CoW across the halfway mark, starting with the unwritten extent. - Check that the files are now different where we say they're different. It is registered with `_begin_fstest auto quick clone prealloc mmap`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 61 source line(s).
- Harness registration: `_begin_fstest auto quick clone prealloc mmap`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/reflink`.
- Capability and skip gates: `_require_scratch_reflink`, `_require_scratch_delalloc`, `_require_xfs_io_command "falloc"`.
- Local shell functions: none visible.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `testdir=$SCRATCH_MNT/test-$seq`
- `blksz=65536`
- `nr=64`
- `filesize=$((blksz * nr))`
- `cowoff=$((filesize / 4))`
- `cowsz=$((filesize / 2))`
- `mmapsz=$((cowoff + cowsz))`

## Control Flow

- Capability gating runs first through `_require_scratch_reflink`, `_require_scratch_delalloc`, `_require_xfs_io_command "falloc"`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 26: echo "Format and mount"`
- `line 33: echo "Create the original files"`
- `line 40: echo "Compare files"`
- `line 45: echo "mmap CoW across the transition"`
- `line 54: echo "Compare files"`
- Key operational lines include:
- `line 16: _begin_fstest auto quick clone prealloc mmap`
- `line 22: _require_scratch_reflink`
- `line 23: _require_scratch_delalloc`
- `line 24: _require_xfs_io_command "falloc"`
- `line 27: _scratch_mkfs > $seqres.full 2>&1`
- `line 28: _scratch_mount >> $seqres.full 2>&1`
- `line 37: _weave_reflink_holes $blksz $nr $testdir/file1 $testdir/file3 >> $seqres.full`
- `line 38: _scratch_cycle_mount`
- `line 41: md5sum $testdir/file1 | _filter_scratch`
- `line 42: md5sum $testdir/file3 | _filter_scratch`
- `line 43: md5sum $testdir/file3.chk | _filter_scratch`
- `line 45: echo "mmap CoW across the transition"`
- `line 48: _weave_reflink_holes_delalloc $blksz $nr $testdir/file3 >> $seqres.full`
- `line 49: mmapsz=$((cowoff + cowsz))`
- `line 50: _mwrite_byte 0x63 $cowoff $cowsz $mmapsz $testdir/file3 >> $seqres.full`
- `line 51: _mwrite_byte 0x63 $cowoff $cowsz $mmapsz $testdir/file3.chk >> $seqres.full`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Shared extent or atomic-update state is exercised, so correctness depends on clone/dedupe/exchange persistence and metadata ordering. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick clone prealloc mmap`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/reflink`), and the golden-output file `sources/test-tools/xfstests/tests/generic/661.out` (12 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_scratch_reflink`, `_require_scratch_delalloc`, `_require_xfs_io_command "falloc"`.

## Risks and Edge Cases

- mmap/page-fault regressions are often race-prone and may manifest as hangs rather than clean command failures.
- Shared-extent and exchange operations can expose stale data, permission-bit, or log-ordering bugs that only appear after remount/recovery.

## Test Signals

The paired `.out` file has 12 line(s); its first visible signals are: 'QA output created by 661; Format and mount; Create the original files; Compare files; bdbcf02ee0aa977795a79d25fcfdccb1  SCRATCH_MNT/test-661/file1'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands, xfstests output filters, post-remount or failure-injection persistence checks. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/661 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/662 -->
# sources/test-tools/xfstests/tests/generic/662

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/662`. Ensuring that copy on write in mmap mode works when the CoW range originally covers multiple extents, mixed with reflinked, unwritten, hole, regular and delalloc blocks. (MMAP version of generic/200,199) - Create a file with the following repeating sequence of blocks: 1. reflinked 2. unwritten 3. hole 4. regular block 5. delalloc - mmap CoW across the halfway mark, starting with the unwritten extent. - Check that the files are now different where we say they're different. It is registered with `_begin_fstest auto quick clone punch prealloc mmap`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 66 source line(s).
- Harness registration: `_begin_fstest auto quick clone punch prealloc mmap`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/reflink`.
- Capability and skip gates: `_require_scratch_reflink`, `_require_scratch_delalloc`, `_require_xfs_io_command "falloc"`, `_require_xfs_io_command "fpunch"`.
- Local shell functions: none visible.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `testdir=$SCRATCH_MNT/test-$seq`
- `blksz=65536`
- `nr=64`
- `filesize=$((blksz * nr))`
- `cowoff=$((filesize / 4))`
- `cowsz=$((filesize / 2))`
- `mmapsz=$((cowoff + cowsz))`

## Control Flow

- Capability gating runs first through `_require_scratch_reflink`, `_require_scratch_delalloc`, `_require_xfs_io_command "falloc"`, `_require_xfs_io_command "fpunch"`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 31: echo "Format and mount"`
- `line 38: echo "Create the original files"`
- `line 45: echo "Compare files"`
- `line 50: echo "mmap CoW across the transition"`
- `line 60: echo "Compare files"`
- Key operational lines include:
- `line 20: _begin_fstest auto quick clone punch prealloc mmap`
- `line 26: _require_scratch_reflink`
- `line 27: _require_scratch_delalloc`
- `line 28: _require_xfs_io_command "falloc"`
- `line 32: _scratch_mkfs > $seqres.full 2>&1`
- `line 33: _scratch_mount >> $seqres.full 2>&1`
- `line 42: _weave_reflink_rainbow $blksz $nr $testdir/file1 $testdir/file3 >> $seqres.full`
- `line 43: _scratch_cycle_mount`
- `line 46: md5sum $testdir/file1 | _filter_scratch`
- `line 47: md5sum $testdir/file3 | _filter_scratch`
- `line 48: md5sum $testdir/file3.chk | _filter_scratch`
- `line 50: echo "mmap CoW across the transition"`
- `line 53: _weave_reflink_rainbow_delalloc $blksz $nr $testdir/file3 >> $seqres.full`
- `line 55: mmapsz=$((cowoff + cowsz))`
- `line 56: _mwrite_byte 0x63 $cowoff $cowsz $mmapsz $testdir/file3 >> $seqres.full`
- `line 57: _mwrite_byte 0x63 $cowoff $cowsz $mmapsz $testdir/file3.chk >> $seqres.full`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Shared extent or atomic-update state is exercised, so correctness depends on clone/dedupe/exchange persistence and metadata ordering. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick clone punch prealloc mmap`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/reflink`), and the golden-output file `sources/test-tools/xfstests/tests/generic/662.out` (12 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_scratch_reflink`, `_require_scratch_delalloc`, `_require_xfs_io_command "falloc"`, `_require_xfs_io_command "fpunch"`.

## Risks and Edge Cases

- mmap/page-fault regressions are often race-prone and may manifest as hangs rather than clean command failures.
- Shared-extent and exchange operations can expose stale data, permission-bit, or log-ordering bugs that only appear after remount/recovery.

## Test Signals

The paired `.out` file has 12 line(s); its first visible signals are: 'QA output created by 662; Format and mount; Create the original files; Compare files; bdbcf02ee0aa977795a79d25fcfdccb1  SCRATCH_MNT/test-662/file1'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands, xfstests output filters, post-remount or failure-injection persistence checks. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/662 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/663 -->
# sources/test-tools/xfstests/tests/generic/663

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/663`. Ensuring that copy on write in mmap mode to the source file when the CoW range covers regular unshared and regular shared blocks. (MMAP version of generic/284,287) - Create two files. - Reflink the odd blocks of the first file into the second file. - mmap CoW the first file across the halfway mark, starting with the regular extent. - Check that the files are now different where we say they're different. It is registered with `_begin_fstest auto quick clone prealloc mmap`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 59 source line(s).
- Harness registration: `_begin_fstest auto quick clone prealloc mmap`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/reflink`.
- Capability and skip gates: `_require_scratch_reflink`, `_require_xfs_io_command "falloc"`.
- Local shell functions: none visible.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `testdir=$SCRATCH_MNT/test-$seq`
- `blksz=65536`
- `nr=64`
- `filesize=$((blksz * nr))`
- `cowoff=$((filesize / 4))`
- `cowsz=$((filesize / 2))`
- `mmapsz=$((cowoff + cowsz))`

## Control Flow

- Capability gating runs first through `_require_scratch_reflink`, `_require_xfs_io_command "falloc"`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 25: echo "Format and mount"`
- `line 32: echo "Create the original files"`
- `line 39: echo "Compare files"`
- `line 44: echo "mmap CoW across the transition"`
- `line 52: echo "Compare files"`
- Key operational lines include:
- `line 16: _begin_fstest auto quick clone prealloc mmap`
- `line 22: _require_scratch_reflink`
- `line 23: _require_xfs_io_command "falloc"`
- `line 26: _scratch_mkfs > $seqres.full 2>&1`
- `line 27: _scratch_mount >> $seqres.full 2>&1`
- `line 36: _sweave_reflink_regular $blksz $nr $testdir/file1 $testdir/file3 >> $seqres.full`
- `line 37: _scratch_cycle_mount`
- `line 40: md5sum $testdir/file1 | _filter_scratch`
- `line 41: md5sum $testdir/file3 | _filter_scratch`
- `line 42: md5sum $testdir/file1.chk | _filter_scratch`
- `line 44: echo "mmap CoW across the transition"`
- `line 47: mmapsz=$((cowoff + cowsz))`
- `line 48: _mwrite_byte 0x63 $cowoff $cowsz $mmapsz $testdir/file1 >> $seqres.full`
- `line 49: _mwrite_byte 0x63 $cowoff $cowsz $mmapsz $testdir/file1.chk >> $seqres.full`
- `line 50: _scratch_cycle_mount`
- `line 53: md5sum $testdir/file1 | _filter_scratch`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Shared extent or atomic-update state is exercised, so correctness depends on clone/dedupe/exchange persistence and metadata ordering. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick clone prealloc mmap`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/reflink`), and the golden-output file `sources/test-tools/xfstests/tests/generic/663.out` (12 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_scratch_reflink`, `_require_xfs_io_command "falloc"`.

## Risks and Edge Cases

- mmap/page-fault regressions are often race-prone and may manifest as hangs rather than clean command failures.
- Shared-extent and exchange operations can expose stale data, permission-bit, or log-ordering bugs that only appear after remount/recovery.

## Test Signals

The paired `.out` file has 12 line(s); its first visible signals are: 'QA output created by 663; Format and mount; Create the original files; Compare files; bdbcf02ee0aa977795a79d25fcfdccb1  SCRATCH_MNT/test-663/file1'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands, xfstests output filters, post-remount or failure-injection persistence checks. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/663 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/664 -->
# sources/test-tools/xfstests/tests/generic/664

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/664`. Ensuring that copy on write in mmap mode to the source file when the CoW range covers unwritten and regular shared blocks. (MMAP version of generic/289,290) - Create two files. - fallocate the first file. - Write the odd blocks of the first file. - Reflink the odd blocks of the first file into the second file. - mmap CoW the first file across the halfway mark, starting with the regular extent. - Check that the files are now different where we say they're different. It is registered with `_begin_fstest auto quick clone prealloc mmap`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 61 source line(s).
- Harness registration: `_begin_fstest auto quick clone prealloc mmap`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/reflink`.
- Capability and skip gates: `_require_scratch_reflink`, `_require_xfs_io_command "falloc"`.
- Local shell functions: none visible.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `testdir=$SCRATCH_MNT/test-$seq`
- `blksz=65536`
- `nr=64`
- `filesize=$((blksz * nr))`
- `cowoff=$((filesize / 4))`
- `cowsz=$((filesize / 2))`
- `mmapsz=$((cowoff + cowsz))`

## Control Flow

- Capability gating runs first through `_require_scratch_reflink`, `_require_xfs_io_command "falloc"`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 27: echo "Format and mount"`
- `line 34: echo "Create the original files"`
- `line 41: echo "Compare files"`
- `line 46: echo "mmap CoW across the transition"`
- `line 54: echo "Compare files"`
- Key operational lines include:
- `line 18: _begin_fstest auto quick clone prealloc mmap`
- `line 24: _require_scratch_reflink`
- `line 25: _require_xfs_io_command "falloc"`
- `line 28: _scratch_mkfs > $seqres.full 2>&1`
- `line 29: _scratch_mount >> $seqres.full 2>&1`
- `line 38: _sweave_reflink_unwritten $blksz $nr $testdir/file1 $testdir/file3 >> $seqres.full`
- `line 39: _scratch_cycle_mount`
- `line 42: md5sum $testdir/file1 | _filter_scratch`
- `line 43: md5sum $testdir/file3 | _filter_scratch`
- `line 44: md5sum $testdir/file1.chk | _filter_scratch`
- `line 46: echo "mmap CoW across the transition"`
- `line 49: mmapsz=$((cowoff + cowsz))`
- `line 50: _mwrite_byte 0x63 $cowoff $cowsz $mmapsz $testdir/file1 >> $seqres.full`
- `line 51: _mwrite_byte 0x63 $cowoff $cowsz $mmapsz $testdir/file1.chk >> $seqres.full`
- `line 52: _scratch_cycle_mount`
- `line 55: md5sum $testdir/file1 | _filter_scratch`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Shared extent or atomic-update state is exercised, so correctness depends on clone/dedupe/exchange persistence and metadata ordering. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick clone prealloc mmap`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/reflink`), and the golden-output file `sources/test-tools/xfstests/tests/generic/664.out` (12 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_scratch_reflink`, `_require_xfs_io_command "falloc"`.

## Risks and Edge Cases

- mmap/page-fault regressions are often race-prone and may manifest as hangs rather than clean command failures.
- Shared-extent and exchange operations can expose stale data, permission-bit, or log-ordering bugs that only appear after remount/recovery.

## Test Signals

The paired `.out` file has 12 line(s); its first visible signals are: 'QA output created by 664; Format and mount; Create the original files; Compare files; b8a8a88d4c143f79900c4b4e79aa3e37  SCRATCH_MNT/test-664/file1'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands, xfstests output filters, post-remount or failure-injection persistence checks. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/664 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/665 -->
# sources/test-tools/xfstests/tests/generic/665

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/665`. Ensuring that copy on write in mmap mode to the source file when the CoW range covers holes and regular shared blocks. (MMAP version of generic/291,292) - Create two files. - Truncate the first file. - Write the odd blocks of the first file. - Reflink the odd blocks of the first file into the second file. - mmap CoW the first file across the halfway mark, starting with the regular extent. - Check that the files are now different where we say they're different. It is registered with `_begin_fstest auto quick clone prealloc mmap`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 61 source line(s).
- Harness registration: `_begin_fstest auto quick clone prealloc mmap`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/reflink`.
- Capability and skip gates: `_require_scratch_reflink`, `_require_xfs_io_command "falloc"`.
- Local shell functions: none visible.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `testdir=$SCRATCH_MNT/test-$seq`
- `blksz=65536`
- `nr=64`
- `filesize=$((blksz * nr))`
- `cowoff=$((filesize / 4))`
- `cowsz=$((filesize / 2))`
- `mmapsz=$((cowoff + cowsz))`

## Control Flow

- Capability gating runs first through `_require_scratch_reflink`, `_require_xfs_io_command "falloc"`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 27: echo "Format and mount"`
- `line 34: echo "Create the original files"`
- `line 41: echo "Compare files"`
- `line 46: echo "mmap CoW across the transition"`
- `line 54: echo "Compare files"`
- Key operational lines include:
- `line 18: _begin_fstest auto quick clone prealloc mmap`
- `line 24: _require_scratch_reflink`
- `line 25: _require_xfs_io_command "falloc"`
- `line 28: _scratch_mkfs > $seqres.full 2>&1`
- `line 29: _scratch_mount >> $seqres.full 2>&1`
- `line 38: _sweave_reflink_holes $blksz $nr $testdir/file1 $testdir/file3 >> $seqres.full`
- `line 39: _scratch_cycle_mount`
- `line 42: md5sum $testdir/file1 | _filter_scratch`
- `line 43: md5sum $testdir/file3 | _filter_scratch`
- `line 44: md5sum $testdir/file1.chk | _filter_scratch`
- `line 46: echo "mmap CoW across the transition"`
- `line 49: mmapsz=$((cowoff + cowsz))`
- `line 50: _mwrite_byte 0x63 $cowoff $cowsz $mmapsz $testdir/file1 >> $seqres.full`
- `line 51: _mwrite_byte 0x63 $cowoff $cowsz $mmapsz $testdir/file1.chk >> $seqres.full`
- `line 52: _scratch_cycle_mount`
- `line 55: md5sum $testdir/file1 | _filter_scratch`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Shared extent or atomic-update state is exercised, so correctness depends on clone/dedupe/exchange persistence and metadata ordering. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick clone prealloc mmap`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/reflink`), and the golden-output file `sources/test-tools/xfstests/tests/generic/665.out` (12 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_scratch_reflink`, `_require_xfs_io_command "falloc"`.

## Risks and Edge Cases

- mmap/page-fault regressions are often race-prone and may manifest as hangs rather than clean command failures.
- Shared-extent and exchange operations can expose stale data, permission-bit, or log-ordering bugs that only appear after remount/recovery.

## Test Signals

The paired `.out` file has 12 line(s); its first visible signals are: 'QA output created by 665; Format and mount; Create the original files; Compare files; b8a8a88d4c143f79900c4b4e79aa3e37  SCRATCH_MNT/test-665/file1'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands, xfstests output filters, post-remount or failure-injection persistence checks. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/665 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/666 -->
# sources/test-tools/xfstests/tests/generic/666

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/666`. Ensuring that copy on write in mmap mode to the source file when the CoW range covers delalloc blocks and regular shared blocks. (MMAP version of generic/293,295) - Create two files. - Truncate the first file. - Write the odd blocks of the first file. - Reflink the odd blocks of the first file into the second file. - Write the even blocks of the first file. - mmap CoW the first file across the halfway mark, starting with the regular extent. - Check that the files are now different where we say they're different. It is registered with `_begin_fstest auto quick clone prealloc mmap`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 64 source line(s).
- Harness registration: `_begin_fstest auto quick clone prealloc mmap`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/reflink`.
- Capability and skip gates: `_require_scratch_reflink`, `_require_scratch_delalloc`, `_require_xfs_io_command "falloc"`.
- Local shell functions: none visible.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `testdir=$SCRATCH_MNT/test-$seq`
- `blksz=65536`
- `nr=64`
- `filesize=$((blksz * nr))`
- `cowoff=$((filesize / 4))`
- `cowsz=$((filesize / 2))`
- `mmapsz=$((cowoff + cowsz))`

## Control Flow

- Capability gating runs first through `_require_scratch_reflink`, `_require_scratch_delalloc`, `_require_xfs_io_command "falloc"`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 29: echo "Format and mount"`
- `line 36: echo "Create the original files"`
- `line 43: echo "Compare files"`
- `line 48: echo "mmap CoW across the transition"`
- `line 57: echo "Compare files"`
- Key operational lines include:
- `line 19: _begin_fstest auto quick clone prealloc mmap`
- `line 25: _require_scratch_reflink`
- `line 26: _require_scratch_delalloc`
- `line 27: _require_xfs_io_command "falloc"`
- `line 30: _scratch_mkfs > $seqres.full 2>&1`
- `line 31: _scratch_mount >> $seqres.full 2>&1`
- `line 40: _sweave_reflink_holes $blksz $nr $testdir/file1 $testdir/file3 >> $seqres.full`
- `line 41: _scratch_cycle_mount`
- `line 44: md5sum $testdir/file1 | _filter_scratch`
- `line 45: md5sum $testdir/file3 | _filter_scratch`
- `line 46: md5sum $testdir/file1.chk | _filter_scratch`
- `line 48: echo "mmap CoW across the transition"`
- `line 51: _sweave_reflink_holes_delalloc $blksz $nr $testdir/file1 >> $seqres.full`
- `line 52: mmapsz=$((cowoff + cowsz))`
- `line 53: _mwrite_byte 0x63 $cowoff $cowsz $mmapsz $testdir/file1 >> $seqres.full`
- `line 54: _mwrite_byte 0x63 $cowoff $cowsz $mmapsz $testdir/file1.chk >> $seqres.full`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Shared extent or atomic-update state is exercised, so correctness depends on clone/dedupe/exchange persistence and metadata ordering. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick clone prealloc mmap`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/reflink`), and the golden-output file `sources/test-tools/xfstests/tests/generic/666.out` (12 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_scratch_reflink`, `_require_scratch_delalloc`, `_require_xfs_io_command "falloc"`.

## Risks and Edge Cases

- mmap/page-fault regressions are often race-prone and may manifest as hangs rather than clean command failures.
- Shared-extent and exchange operations can expose stale data, permission-bit, or log-ordering bugs that only appear after remount/recovery.

## Test Signals

The paired `.out` file has 12 line(s); its first visible signals are: 'QA output created by 666; Format and mount; Create the original files; Compare files; b8a8a88d4c143f79900c4b4e79aa3e37  SCRATCH_MNT/test-666/file1'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands, xfstests output filters, post-remount or failure-injection persistence checks. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/666 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/667 -->
# sources/test-tools/xfstests/tests/generic/667

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/667`. Ensuring that copy on write in buffered mode works when the CoW range originally covers multiple extents, mixed with reflinked, unwritten, hole, regular and delalloc blocks. - Create a file with the following repeating sequence of blocks: 1. reflinked 2. unwritten 3. hole 4. regular block 5. delalloc - CoW across the halfway mark, starting with the unwritten extent. - Check that the files are now different where we say they're different. It is registered with `_begin_fstest auto quick clone punch prealloc`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 64 source line(s).
- Harness registration: `_begin_fstest auto quick clone punch prealloc`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/reflink`.
- Capability and skip gates: `_require_scratch_reflink`, `_require_scratch_delalloc`, `_require_xfs_io_command "falloc"`, `_require_xfs_io_command "fpunch"`.
- Local shell functions: none visible.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `testdir=$SCRATCH_MNT/test-$seq`
- `blksz=65536`
- `nr=64`
- `filesize=$((blksz * nr))`
- `cowoff=$((filesize / 4))`
- `cowsz=$((filesize / 2))`

## Control Flow

- Capability gating runs first through `_require_scratch_reflink`, `_require_scratch_delalloc`, `_require_xfs_io_command "falloc"`, `_require_xfs_io_command "fpunch"`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 30: echo "Format and mount"`
- `line 37: echo "Create the original files"`
- `line 44: echo "Compare files"`
- `line 49: echo "CoW across the transition"`
- `line 58: echo "Compare files"`
- Key operational lines include:
- `line 25: _require_scratch_reflink`
- `line 26: _require_scratch_delalloc`
- `line 27: _require_xfs_io_command "falloc"`
- `line 31: _scratch_mkfs > $seqres.full 2>&1`
- `line 32: _scratch_mount >> $seqres.full 2>&1`
- `line 41: _sweave_reflink_rainbow $blksz $nr $testdir/file1 $testdir/file3 >> $seqres.full`
- `line 42: _scratch_cycle_mount`
- `line 45: md5sum $testdir/file1 | _filter_scratch`
- `line 46: md5sum $testdir/file3 | _filter_scratch`
- `line 47: md5sum $testdir/file1.chk | _filter_scratch`
- `line 52: _sweave_reflink_rainbow_delalloc $blksz $nr $testdir/file1 >> $seqres.full`
- `line 54: $XFS_IO_PROG -f -c "pwrite -S 0x63 -b $cowsz $cowoff $cowsz" $testdir/file1 >> $seqres.full`
- `line 56: _scratch_cycle_mount`
- `line 59: md5sum $testdir/file1 | _filter_scratch`
- `line 60: md5sum $testdir/file3 | _filter_scratch`
- `line 61: md5sum $testdir/file1.chk | _filter_scratch`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Shared extent or atomic-update state is exercised, so correctness depends on clone/dedupe/exchange persistence and metadata ordering. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick clone punch prealloc`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/reflink`), and the golden-output file `sources/test-tools/xfstests/tests/generic/667.out` (12 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_scratch_reflink`, `_require_scratch_delalloc`, `_require_xfs_io_command "falloc"`, `_require_xfs_io_command "fpunch"`.

## Risks and Edge Cases

- Shared-extent and exchange operations can expose stale data, permission-bit, or log-ordering bugs that only appear after remount/recovery.

## Test Signals

The paired `.out` file has 12 line(s); its first visible signals are: 'QA output created by 667; Format and mount; Create the original files; Compare files; 6366fd359371414186688a0ef6988893  SCRATCH_MNT/test-667/file1'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands, xfstests output filters, post-remount or failure-injection persistence checks. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/667 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/668 -->
# sources/test-tools/xfstests/tests/generic/668

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/668`. Ensuring that copy on write in direct-io mode works when the CoW range originally covers multiple extents, mixed with reflinked, unwritten, hole, regular and delalloc blocks. - Create a file with the following repeating sequence of blocks: 1. reflinked 2. unwritten 3. hole 4. regular block 5. delalloc - directio CoW across the halfway mark, starting with the unwritten extent. - Check that the files are now different where we say they're different. It is registered with `_begin_fstest auto quick clone punch prealloc`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 65 source line(s).
- Harness registration: `_begin_fstest auto quick clone punch prealloc`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/reflink`.
- Capability and skip gates: `_require_scratch_reflink`, `_require_scratch_delalloc`, `_require_xfs_io_command "falloc"`, `_require_xfs_io_command "fpunch"`, `_require_odirect`.
- Local shell functions: none visible.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `testdir=$SCRATCH_MNT/test-$seq`
- `blksz=65536`
- `nr=64`
- `filesize=$((blksz * nr))`
- `cowoff=$((filesize / 4))`
- `cowsz=$((filesize / 2))`

## Control Flow

- Capability gating runs first through `_require_scratch_reflink`, `_require_scratch_delalloc`, `_require_xfs_io_command "falloc"`, `_require_xfs_io_command "fpunch"`, `_require_odirect`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 31: echo "Format and mount"`
- `line 38: echo "Create the original files"`
- `line 45: echo "Compare files"`
- `line 50: echo "directio CoW across the transition"`
- `line 59: echo "Compare files"`
- Key operational lines include:
- `line 25: _require_scratch_reflink`
- `line 26: _require_scratch_delalloc`
- `line 27: _require_xfs_io_command "falloc"`
- `line 32: _scratch_mkfs > $seqres.full 2>&1`
- `line 33: _scratch_mount >> $seqres.full 2>&1`
- `line 42: _sweave_reflink_rainbow $blksz $nr $testdir/file1 $testdir/file3 >> $seqres.full`
- `line 43: _scratch_cycle_mount`
- `line 46: md5sum $testdir/file1 | _filter_scratch`
- `line 47: md5sum $testdir/file3 | _filter_scratch`
- `line 48: md5sum $testdir/file1.chk | _filter_scratch`
- `line 53: _sweave_reflink_rainbow_delalloc $blksz $nr $testdir/file1 >> $seqres.full`
- `line 55: $XFS_IO_PROG -d -f -c "pwrite -S 0x63 -b $cowsz $cowoff $cowsz" $testdir/file1 >> $seqres.full`
- `line 57: _scratch_cycle_mount`
- `line 60: md5sum $testdir/file1 | _filter_scratch`
- `line 61: md5sum $testdir/file3 | _filter_scratch`
- `line 62: md5sum $testdir/file1.chk | _filter_scratch`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Shared extent or atomic-update state is exercised, so correctness depends on clone/dedupe/exchange persistence and metadata ordering. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick clone punch prealloc`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/reflink`), and the golden-output file `sources/test-tools/xfstests/tests/generic/668.out` (12 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_scratch_reflink`, `_require_scratch_delalloc`, `_require_xfs_io_command "falloc"`, `_require_xfs_io_command "fpunch"`, `_require_odirect`.

## Risks and Edge Cases

- Direct/AIO coverage depends on alignment, device logical block size, page size, and filesystem direct-I/O semantics.
- Shared-extent and exchange operations can expose stale data, permission-bit, or log-ordering bugs that only appear after remount/recovery.

## Test Signals

The paired `.out` file has 12 line(s); its first visible signals are: 'QA output created by 668; Format and mount; Create the original files; Compare files; 6366fd359371414186688a0ef6988893  SCRATCH_MNT/test-668/file1'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands, xfstests output filters, post-remount or failure-injection persistence checks. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/668 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/669 -->
# sources/test-tools/xfstests/tests/generic/669

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/669`. Ensuring that copy on write in mmap mode works when the CoW range originally covers multiple extents, mixed with reflinked, unwritten, hole, regular and delalloc blocks. - Create a file with the following repeating sequence of blocks: 1. reflinked 2. unwritten 3. hole 4. regular block 5. delalloc - mmap CoW across the halfway mark, starting with the unwritten extent. - Check that the files are now different where we say they're different. It is registered with `_begin_fstest auto quick clone punch prealloc mmap`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 65 source line(s).
- Harness registration: `_begin_fstest auto quick clone punch prealloc mmap`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/reflink`.
- Capability and skip gates: `_require_scratch_reflink`, `_require_scratch_delalloc`, `_require_xfs_io_command "falloc"`, `_require_xfs_io_command "fpunch"`.
- Local shell functions: none visible.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `testdir=$SCRATCH_MNT/test-$seq`
- `blksz=65536`
- `nr=64`
- `filesize=$((blksz * nr))`
- `cowoff=$((filesize / 4))`
- `cowsz=$((filesize / 2))`
- `mmapsz=$((cowoff + cowsz))`

## Control Flow

- Capability gating runs first through `_require_scratch_reflink`, `_require_scratch_delalloc`, `_require_xfs_io_command "falloc"`, `_require_xfs_io_command "fpunch"`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 30: echo "Format and mount"`
- `line 37: echo "Create the original files"`
- `line 44: echo "Compare files"`
- `line 49: echo "mmap CoW across the transition"`
- `line 59: echo "Compare files"`
- Key operational lines include:
- `line 19: _begin_fstest auto quick clone punch prealloc mmap`
- `line 25: _require_scratch_reflink`
- `line 26: _require_scratch_delalloc`
- `line 27: _require_xfs_io_command "falloc"`
- `line 31: _scratch_mkfs > $seqres.full 2>&1`
- `line 32: _scratch_mount >> $seqres.full 2>&1`
- `line 41: _sweave_reflink_rainbow $blksz $nr $testdir/file1 $testdir/file3 >> $seqres.full`
- `line 42: _scratch_cycle_mount`
- `line 45: md5sum $testdir/file1 | _filter_scratch`
- `line 46: md5sum $testdir/file3 | _filter_scratch`
- `line 47: md5sum $testdir/file1.chk | _filter_scratch`
- `line 49: echo "mmap CoW across the transition"`
- `line 52: _sweave_reflink_rainbow_delalloc $blksz $nr $testdir/file1 >> $seqres.full`
- `line 54: mmapsz=$((cowoff + cowsz))`
- `line 55: _mwrite_byte 0x63 $cowoff $cowsz $mmapsz $testdir/file1 >> $seqres.full`
- `line 56: _mwrite_byte 0x63 $cowoff $cowsz $mmapsz $testdir/file1.chk >> $seqres.full`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Shared extent or atomic-update state is exercised, so correctness depends on clone/dedupe/exchange persistence and metadata ordering. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick clone punch prealloc mmap`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/reflink`), and the golden-output file `sources/test-tools/xfstests/tests/generic/669.out` (12 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_scratch_reflink`, `_require_scratch_delalloc`, `_require_xfs_io_command "falloc"`, `_require_xfs_io_command "fpunch"`.

## Risks and Edge Cases

- mmap/page-fault regressions are often race-prone and may manifest as hangs rather than clean command failures.
- Shared-extent and exchange operations can expose stale data, permission-bit, or log-ordering bugs that only appear after remount/recovery.

## Test Signals

The paired `.out` file has 12 line(s); its first visible signals are: 'QA output created by 669; Format and mount; Create the original files; Compare files; 6366fd359371414186688a0ef6988893  SCRATCH_MNT/test-669/file1'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands, xfstests output filters, post-remount or failure-injection persistence checks. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/669 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/670 -->
# sources/test-tools/xfstests/tests/generic/670

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/670`. Test for races or FS corruption between reflink and mmap reading the target file. (MMAP version of generic/164,165) It is registered with `_begin_fstest auto clone mmap`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 74 source line(s).
- Harness registration: `_begin_fstest auto clone mmap`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/reflink`.
- Capability and skip gates: `_require_scratch_reflink`, `_require_cp_reflink`.
- Local shell functions: `fbytes`, `reader`.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `testdir=$SCRATCH_MNT/test-$seq`
- `finished_file=$tmp.finished`
- `loops=512`
- `nr_loops=$((loops - 1))`
- `blksz=65536`

## Control Flow

- Capability gating runs first through `_require_scratch_reflink`, `_require_cp_reflink`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- User-visible phase markers include:
- `line 21: echo "Format and mount"`
- `line 34: echo "Initialize files"`
- `line 35: echo >> $seqres.full`
- `line 54: echo "Reflink and mmap reread the files!"`
- `line 68: echo "Finished reflinking"`
- Key operational lines include:
- `line 10: _begin_fstest auto clone mmap`
- `line 18: _require_scratch_reflink`
- `line 19: _require_cp_reflink`
- `line 22: _scratch_mkfs > $seqres.full 2>&1`
- `line 23: _scratch_mount >> $seqres.full 2>&1`
- `line 38: _cp_reflink $testdir/file1 $testdir/file3`
- `line 39: _scratch_cycle_mount`
- `line 49: while [ ! -e $finished_file ]; do`
- `line 54: echo "Reflink and mmap reread the files!"`
- `line 58: _reflink_range $testdir/file1 $((i * blksz)) \`
- `line 63: _reflink_range $testdir/file2 $((i * blksz)) \`
- `line 68: echo "Finished reflinking"`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Shared extent or atomic-update state is exercised, so correctness depends on clone/dedupe/exchange persistence and metadata ordering. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto clone mmap`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/reflink`), and the golden-output file `sources/test-tools/xfstests/tests/generic/670.out` (5 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_scratch_reflink`, `_require_cp_reflink`.

## Risks and Edge Cases

- mmap/page-fault regressions are often race-prone and may manifest as hangs rather than clean command failures.
- Shared-extent and exchange operations can expose stale data, permission-bit, or log-ordering bugs that only appear after remount/recovery.

## Test Signals

The paired `.out` file has 5 line(s); its first visible signals are: 'QA output created by 670; Format and mount; Initialize files; Reflink and mmap reread the files!; Finished reflinking'. Runtime pass/fail is also signaled by hang/race detection through background work, loops, or timeout windows, post-remount or failure-injection persistence checks. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/670 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/671 -->
# sources/test-tools/xfstests/tests/generic/671

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/671`. Test for races or FS corruption when mmap writing to a file that's also the source of a reflink operation. (MMAP version of generic/167,166) It is registered with `_begin_fstest auto clone mmap`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 63 source line(s).
- Harness registration: `_begin_fstest auto clone mmap`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/reflink`.
- Capability and skip gates: `_require_scratch_reflink`, `_require_cp_reflink`.
- Local shell functions: `snappy`.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `testdir=$SCRATCH_MNT/test-$seq`
- `finished_file=$tmp.finished`
- `loops=1024`
- `nr_loops=$((loops - 1))`
- `blksz=65536`
- `n=0`
- `out="$(_cp_reflink $testdir/file1 $testdir/snap_$n 2>&1)"`
- `res=$?`
- `n=$((n + 1))`

## Control Flow

- Capability gating runs first through `_require_scratch_reflink`, `_require_cp_reflink`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- User-visible phase markers include:
- `line 21: echo "Format and mount"`
- `line 34: echo "Initialize file"`
- `line 35: echo >> $seqres.full`
- `line 45: echo "$out" | grep -q "No space left" && break`
- `line 52: echo "Snapshot a file undergoing mmap rewrite"`
- Key operational lines include:
- `line 10: _begin_fstest auto clone mmap`
- `line 18: _require_scratch_reflink`
- `line 19: _require_cp_reflink`
- `line 22: _scratch_mkfs > $seqres.full 2>&1`
- `line 23: _scratch_mount >> $seqres.full 2>&1`
- `line 37: _scratch_cycle_mount`
- `line 42: while [ ! -e $finished_file ]; do`
- `line 43: out="$(_cp_reflink $testdir/file1 $testdir/snap_$n 2>&1)"`
- `line 52: echo "Snapshot a file undergoing mmap rewrite"`
- `line 55: $XFS_IO_PROG -f -c "mmap -rw $((i * blksz)) $blksz" \`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Shared extent or atomic-update state is exercised, so correctness depends on clone/dedupe/exchange persistence and metadata ordering. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto clone mmap`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/reflink`), and the golden-output file `sources/test-tools/xfstests/tests/generic/671.out` (4 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_scratch_reflink`, `_require_cp_reflink`.

## Risks and Edge Cases

- mmap/page-fault regressions are often race-prone and may manifest as hangs rather than clean command failures.
- Shared-extent and exchange operations can expose stale data, permission-bit, or log-ordering bugs that only appear after remount/recovery.

## Test Signals

The paired `.out` file has 4 line(s); its first visible signals are: 'QA output created by 671; Format and mount; Initialize file; Snapshot a file undergoing mmap rewrite'. Runtime pass/fail is also signaled by hang/race detection through background work, loops, or timeout windows, post-remount or failure-injection persistence checks. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/671 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/672 -->
# sources/test-tools/xfstests/tests/generic/672

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/672`. Test for races or FS corruption when mmap writing to a file that's also the target of a reflink operation. (MMAP version of generic/168,170) It is registered with `_begin_fstest auto clone mmap`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 63 source line(s).
- Harness registration: `_begin_fstest auto clone mmap`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/reflink`.
- Capability and skip gates: `_require_scratch_reflink`.
- Local shell functions: `overwrite`.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `testdir=$SCRATCH_MNT/test-$seq`
- `finished_file=$tmp.finished`
- `loops=1024`
- `nr_loops=$((loops - 1))`
- `blksz=65536`

## Control Flow

- Capability gating runs first through `_require_scratch_reflink`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- User-visible phase markers include:
- `line 20: echo "Format and mount"`
- `line 33: echo "Initialize files"`
- `line 34: echo >> $seqres.full`
- `line 49: echo "Reflink and mmap write the target"`
- Key operational lines include:
- `line 10: _begin_fstest auto clone mmap`
- `line 18: _require_scratch_reflink`
- `line 21: _scratch_mkfs > $seqres.full 2>&1`
- `line 22: _scratch_mount >> $seqres.full 2>&1`
- `line 37: _scratch_cycle_mount`
- `line 41: while [ ! -e $finished_file ]; do`
- `line 43: $XFS_IO_PROG -f -c "mmap -rw $((i * blksz)) $blksz" \`
- `line 49: echo "Reflink and mmap write the target"`
- `line 53: _reflink_range $testdir/file1 $((i * blksz)) \`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Shared extent or atomic-update state is exercised, so correctness depends on clone/dedupe/exchange persistence and metadata ordering. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto clone mmap`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/reflink`), and the golden-output file `sources/test-tools/xfstests/tests/generic/672.out` (4 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_scratch_reflink`.

## Risks and Edge Cases

- mmap/page-fault regressions are often race-prone and may manifest as hangs rather than clean command failures.
- Shared-extent and exchange operations can expose stale data, permission-bit, or log-ordering bugs that only appear after remount/recovery.

## Test Signals

The paired `.out` file has 4 line(s); its first visible signals are: 'QA output created by 672; Format and mount; Initialize files; Reflink and mmap write the target'. Runtime pass/fail is also signaled by hang/race detection through background work, loops, or timeout windows, post-remount or failure-injection persistence checks. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/672 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/673 -->
# sources/test-tools/xfstests/tests/generic/673

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/673`. Functional test for dropping suid and sgid bits as part of a reflink. It is registered with `_begin_fstest auto clone quick perms`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 117 source line(s).
- Harness registration: `_begin_fstest auto clone quick perms`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/reflink`.
- Capability and skip gates: `_require_user`, `_require_scratch_reflink`, `_require_congruent_file_oplen $SCRATCH_MNT 1048576`.
- Local shell functions: `setup_testfile`, `commit_and_check`.
- External `$here/src` helpers: none visible.

## Control Flow

- Capability gating runs first through `_require_user`, `_require_scratch_reflink`, `_require_congruent_file_oplen $SCRATCH_MNT 1048576`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 52: echo`
- `line 56: echo "Test 1 - qa_user, non-exec file"`
- `line 62: echo "Test 2 - qa_user, group-exec file"`
- `line 68: echo "Test 3 - qa_user, user-exec file"`
- `line 74: echo "Test 4 - qa_user, all-exec file"`
- `line 80: echo "Test 5 - root, non-exec file"`
- `line 86: echo "Test 6 - root, group-exec file"`
- `line 92: echo "Test 7 - root, user-exec file"`
- Key operational lines include:
- `line 19: _require_scratch_reflink`
- `line 21: _scratch_mkfs >> $seqres.full`
- `line 22: _scratch_mount`
- `line 31: _scratch_sync`
- `line 37: md5sum $SCRATCH_MNT/a | _filter_scratch`
- `line 38: stat -c '%a %A %n' $SCRATCH_MNT/a | _filter_scratch`
- `line 40: local cmd="$XFS_IO_PROG -c 'reflink $SCRATCH_MNT/b 0 0 1m' $SCRATCH_MNT/a"`
- `line 47: _scratch_cycle_mount`
- `line 48: md5sum $SCRATCH_MNT/a | _filter_scratch`
- `line 49: stat -c '%a %A %n' $SCRATCH_MNT/a | _filter_scratch`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Shared extent or atomic-update state is exercised, so correctness depends on clone/dedupe/exchange persistence and metadata ordering. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto clone quick perms`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/reflink`), and the golden-output file `sources/test-tools/xfstests/tests/generic/673.out` (61 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_user`, `_require_scratch_reflink`, `_require_congruent_file_oplen $SCRATCH_MNT 1048576`.

## Risks and Edge Cases

- Shared-extent and exchange operations can expose stale data, permission-bit, or log-ordering bugs that only appear after remount/recovery.

## Test Signals

The paired `.out` file has 61 line(s); its first visible signals are: 'QA output created by 673; Test 1 - qa_user, non-exec file; 310f146ce52077fcd3308dcbe7632bb2  SCRATCH_MNT/a; 6666 -rwSrwSrw- SCRATCH_MNT/a; 3784de23efab7a2074c9ec66901e39e5  SCRATCH_MNT/a'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands, xfstests output filters, post-remount or failure-injection persistence checks. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/673 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/674 -->
# sources/test-tools/xfstests/tests/generic/674

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/674`. Functional test for dropping suid and sgid bits as part of a deduplication. It is registered with `_begin_fstest auto clone quick perms dedupe`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 116 source line(s).
- Harness registration: `_begin_fstest auto clone quick perms dedupe`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/reflink`.
- Capability and skip gates: `_require_user`, `_require_scratch_dedupe`, `_require_xfs_io_command dedupe`, `_require_congruent_file_oplen $SCRATCH_MNT 1048576`.
- Local shell functions: `setup_testfile`, `commit_and_check`.
- External `$here/src` helpers: none visible.

## Control Flow

- Capability gating runs first through `_require_user`, `_require_scratch_dedupe`, `_require_xfs_io_command dedupe`, `_require_congruent_file_oplen $SCRATCH_MNT 1048576`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 56: echo "before: $before_freesp; after: $after_freesp" >> $seqres.full`
- `line 58: echo "expected more free space after dedupe"`
- `line 62: echo`
- `line 67: echo "Test 1 - qa_user, non-exec file"`
- `line 73: echo "Test 2 - qa_user, group-exec file"`
- `line 79: echo "Test 3 - qa_user, user-exec file"`
- `line 85: echo "Test 4 - qa_user, all-exec file"`
- `line 91: echo "Test 5 - root, non-exec file"`
- Key operational lines include:
- `line 10: _begin_fstest auto clone quick perms dedupe`
- `line 19: _require_scratch_dedupe`
- `line 20: _require_xfs_io_command dedupe`
- `line 22: _scratch_mkfs >> $seqres.full`
- `line 23: _scratch_mount`
- `line 32: _scratch_sync`
- `line 38: md5sum $SCRATCH_MNT/a | _filter_scratch`
- `line 39: stat -c '%a %A %n' $SCRATCH_MNT/a | _filter_scratch`
- `line 43: local cmd="$XFS_IO_PROG -c 'dedupe $SCRATCH_MNT/b 0 0 1m' $SCRATCH_MNT/a"`
- `line 50: _scratch_cycle_mount`
- `line 51: md5sum $SCRATCH_MNT/a | _filter_scratch`
- `line 52: stat -c '%a %A %n' $SCRATCH_MNT/a | _filter_scratch`
- `line 58: echo "expected more free space after dedupe"`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Shared extent or atomic-update state is exercised, so correctness depends on clone/dedupe/exchange persistence and metadata ordering. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto clone quick perms dedupe`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/reflink`), and the golden-output file `sources/test-tools/xfstests/tests/generic/674.out` (49 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_user`, `_require_scratch_dedupe`, `_require_xfs_io_command dedupe`, `_require_congruent_file_oplen $SCRATCH_MNT 1048576`.

## Risks and Edge Cases

- Shared-extent and exchange operations can expose stale data, permission-bit, or log-ordering bugs that only appear after remount/recovery.

## Test Signals

The paired `.out` file has 49 line(s); its first visible signals are: 'QA output created by 674; Test 1 - qa_user, non-exec file; 310f146ce52077fcd3308dcbe7632bb2  SCRATCH_MNT/a; 6666 -rwSrwSrw- SCRATCH_MNT/a; 310f146ce52077fcd3308dcbe7632bb2  SCRATCH_MNT/a'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands, xfstests output filters, post-remount or failure-injection persistence checks. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/674 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/675 -->
# sources/test-tools/xfstests/tests/generic/675

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/675`. Functional test for dropping suid and sgid capabilities as part of a reflink. It is registered with `_begin_fstest auto clone quick`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 71 source line(s).
- Harness registration: `_begin_fstest auto clone quick`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/reflink`, `./common/attr`.
- Capability and skip gates: `_require_user`, `_require_command "$GETCAP_PROG" getcap`, `_require_command "$SETCAP_PROG" setcap`, `_require_scratch_reflink`, `_require_attrs security`, `_require_congruent_file_oplen $SCRATCH_MNT 1048576`.
- Local shell functions: `setup_testfile`, `commit_and_check`.
- External `$here/src` helpers: none visible.

## Control Flow

- Capability gating runs first through `_require_user`, `_require_command "$GETCAP_PROG" getcap`, `_require_command "$SETCAP_PROG" setcap`, `_require_scratch_reflink`, `_require_attrs security`, plus 1 more.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 56: echo`
- `line 60: echo "Test 1 - qa_user"`
- `line 65: echo "Test 2 - root"`
- Key operational lines include:
- `line 22: _require_scratch_reflink`
- `line 25: _scratch_mkfs >> $seqres.full`
- `line 26: _scratch_mount`
- `line 36: _scratch_sync`
- `line 42: stat -c '%a %A %n' $SCRATCH_MNT/a | _filter_scratch`
- `line 45: local cmd="$XFS_IO_PROG -c 'reflink $SCRATCH_MNT/b 0 0 1m' $SCRATCH_MNT/a"`
- `line 52: stat -c '%a %A %n' $SCRATCH_MNT/a | _filter_scratch`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Extended attributes are part of the persistent state being created, replayed, or verified. Shared extent or atomic-update state is exercised, so correctness depends on clone/dedupe/exchange persistence and metadata ordering. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto clone quick`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/reflink`, `./common/attr`), and the golden-output file `sources/test-tools/xfstests/tests/generic/675.out` (13 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_user`, `_require_command "$GETCAP_PROG" getcap`, `_require_command "$SETCAP_PROG" setcap`, `_require_scratch_reflink`, `_require_attrs security`, `_require_congruent_file_oplen $SCRATCH_MNT 1048576`.

## Risks and Edge Cases

- Shared-extent and exchange operations can expose stale data, permission-bit, or log-ordering bugs that only appear after remount/recovery.

## Test Signals

The paired `.out` file has 13 line(s); its first visible signals are: 'QA output created by 675; Test 1 - qa_user; 777 -rwxrwxrwx SCRATCH_MNT/a; SCRATCH_MNT/a cap_setgid,cap_setuid=ep; 777 -rwxrwxrwx SCRATCH_MNT/a'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands, xfstests output filters. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/675 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/676 -->
# sources/test-tools/xfstests/tests/generic/676

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/676`. Test that filesystem properly handles seeking in directory both to valid and invalid positions. This is a regression test for a48fc69fe658 ("udf: Fix crash after seekdir") It is registered with `_begin_fstest auto quick`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 39 source line(s).
- Harness registration: `_begin_fstest auto quick`.
- Imported common libraries: `./common/preamble`.
- Capability and skip gates: `_require_test`, `_require_test_program "t_readdir_3"`.
- Local shell functions: `_cleanup`.
- External `$here/src` helpers: `$here/src/t_readdir_3 $dir $files $seed >> $seqres.full`.
- Notable variables and constants:
- `dir=$TEST_DIR/$seq-dir`
- `files=4000`
- `seed=$RANDOM`

## Control Flow

- Capability gating runs first through `_require_test`, `_require_test_program "t_readdir_3"`.
- User-visible phase markers include:
- `line 34: echo "Using seed $seed" >> $seqres.full`

## State and Persistence Behavior

Uses the configured xfstests test area or an explicitly created loop/image mount rather than always reformatting the scratch device. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick`, common helper libraries (`./common/preamble`), and the golden-output file `sources/test-tools/xfstests/tests/generic/676.out` (2 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_test`, `_require_test_program "t_readdir_3"`.

## Risks and Edge Cases

- Most failures should surface as unexpected output, nonzero helper status, or harness `_fail`/`_notrun` behavior.

## Test Signals

The paired `.out` file has 2 line(s); its first visible signals are: 'QA output created by 676; All tests passed'. Runtime pass/fail is primarily the command exit status plus golden-output comparison. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/676 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/677 -->
# sources/test-tools/xfstests/tests/generic/677

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/677`. Test that after a full fsync of a file with preallocated extents beyond the file's size, if a power failure happens, the preallocated extents still exist after we mount the filesystem. It is registered with `_begin_fstest auto quick log prealloc fiemap`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 87 source line(s).
- Harness registration: `_begin_fstest auto quick log prealloc fiemap`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/dmflakey`, `./common/punch`.
- Capability and skip gates: `_require_scratch`, `_require_dm_target flakey`, `_require_xfs_io_command "falloc" "-k"`, `_require_xfs_io_command "fiemap"`, `_require_odirect`, `_require_metadata_journaling $SCRATCH_DEV`, `_require_congruent_file_oplen $SCRATCH_MNT 1048576`.
- Local shell functions: `_cleanup`.
- External `$here/src` helpers: none visible.

## Control Flow

- Capability gating runs first through `_require_scratch`, `_require_dm_target flakey`, `_require_xfs_io_command "falloc" "-k"`, `_require_xfs_io_command "fiemap"`, `_require_odirect`, plus 2 more.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- User-visible phase markers include:
- `line 80: echo "List of extents after power failure:"`
- Key operational lines include:
- `line 16: _cleanup_flakey`
- `line 28: _require_xfs_io_command "falloc" "-k"`
- `line 34: _scratch_mkfs >>$seqres.full 2>&1`
- `line 36: _init_flakey`
- `line 37: _scratch_mount`
- `line 53: $XFS_IO_PROG -f -d -c "pwrite -b 4K 0 16M" $SCRATCH_MNT/foo | _filter_xfs_io`
- `line 58: $XFS_IO_PROG -c "falloc -k 16M 1M" $SCRATCH_MNT/foo`
- `line 59: $XFS_IO_PROG -c "falloc -k 20M 1M" $SCRATCH_MNT/foo`
- `line 65: _scratch_sync`
- `line 72: $XFS_IO_PROG -c "pwrite 0 4K" -c "fsync" $SCRATCH_MNT/foo | _filter_xfs_io`
- `line 76: _flakey_drop_and_remount`
- `line 81: $XFS_IO_PROG -c "fiemap -v" $SCRATCH_MNT/foo | _filter_fiemap`
- `line 83: _scratch_unmount`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Synthetic block-device state can be introduced through device-mapper, loop, SCSI debug, or huge-device helpers and must be cleaned even on failure. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick log prealloc fiemap`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/dmflakey`, `./common/punch`), and the golden-output file `sources/test-tools/xfstests/tests/generic/677.out` (10 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_scratch`, `_require_dm_target flakey`, `_require_xfs_io_command "falloc" "-k"`, `_require_xfs_io_command "fiemap"`, `_require_odirect`, `_require_metadata_journaling $SCRATCH_DEV`, `_require_congruent_file_oplen $SCRATCH_MNT 1048576`.

## Risks and Edge Cases

- Direct/AIO coverage depends on alignment, device logical block size, page size, and filesystem direct-I/O semantics.
- Failure-injection paths can leave mounts or synthetic device tables behind if cleanup is interrupted.

## Test Signals

The paired `.out` file has 10 line(s); its first visible signals are: 'QA output created by 677; wrote 16777216/16777216 bytes at offset 0; XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec); wrote 4096/4096 bytes at offset 0; XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec)'. Runtime pass/fail is also signaled by xfstests output filters, post-remount or failure-injection persistence checks. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/677 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/678 -->
# sources/test-tools/xfstests/tests/generic/678

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/678`. Test doing a read, with io_uring, over a file range that includes multiple extents. The read operation triggers page faults when accessing all pages of the read buffer except for the pages corresponding to the first extent. Then verify that the operation results in reading all the extents and returns the correct data. It is registered with `_begin_fstest auto quick io_uring`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 37 source line(s).
- Harness registration: `_begin_fstest auto quick io_uring`.
- Imported common libraries: `./common/preamble`, `./common/filter`.
- Capability and skip gates: `_require_test`, `_require_odirect`, `_require_io_uring`, `_require_test_program uring_read_fault`.
- Local shell functions: `_cleanup`.
- External `$here/src` helpers: `$here/src/uring_read_fault $TEST_DIR/uring_read_fault.tmp`.

## Control Flow

- Capability gating runs first through `_require_test`, `_require_odirect`, `_require_io_uring`, `_require_test_program uring_read_fault`.
- User-visible phase markers include:
- `line 36: echo "Silence is golden"`

## State and Persistence Behavior

Uses the configured xfstests test area or an explicitly created loop/image mount rather than always reformatting the scratch device. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick io_uring`, common helper libraries (`./common/preamble`, `./common/filter`), and the golden-output file `sources/test-tools/xfstests/tests/generic/678.out` (2 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_test`, `_require_odirect`, `_require_io_uring`, `_require_test_program uring_read_fault`.

## Risks and Edge Cases

- Direct/AIO coverage depends on alignment, device logical block size, page size, and filesystem direct-I/O semantics.
- mmap/page-fault regressions are often race-prone and may manifest as hangs rather than clean command failures.

## Test Signals

The paired `.out` file has 2 line(s); its first visible signals are: 'QA output created by 678; Silence is golden'. Runtime pass/fail is primarily the command exit status plus golden-output comparison. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/678 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/679 -->
# sources/test-tools/xfstests/tests/generic/679

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/679`. Test that if we call fallocate against a file range that has a mix of holes and written extents, the fallocate succeeds if the filesystem has enough free space to allocate extents for the holes. It is registered with `_begin_fstest auto quick prealloc fiemap`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 60 source line(s).
- Harness registration: `_begin_fstest auto quick prealloc fiemap`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/punch`.
- Capability and skip gates: `_require_scratch`, `_require_xfs_io_command "falloc"`, `_require_xfs_io_command "fiemap"`, `_exclude_fs xfs`.
- Local shell functions: none visible.
- External `$here/src` helpers: none visible.

## Control Flow

- Capability gating runs first through `_require_scratch`, `_require_xfs_io_command "falloc"`, `_require_xfs_io_command "fiemap"`, `_exclude_fs xfs`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- User-visible phase markers include:
- `line 50: echo -n "Number of unwritten extents in the file: "`
- `line 55: echo "File content after fallocate:"`
- Key operational lines include:
- `line 19: _require_xfs_io_command "falloc"`
- `line 31: _scratch_mkfs_sized $((1024 * 1024 * 1024)) >>$seqres.full 2>&1`
- `line 32: _scratch_mount`
- `line 36: $XFS_IO_PROG -f -c "pwrite -S 0xab 0 200M" \`
- `line 44: $XFS_IO_PROG -c "falloc 0 600M" $SCRATCH_MNT/foobar`
- `line 48: _scratch_cycle_mount`
- `line 51: $XFS_IO_PROG -c "fiemap -v" $SCRATCH_MNT/foobar | _filter_fiemap | \`
- `line 55: echo "File content after fallocate:"`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick prealloc fiemap`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/punch`), and the golden-output file `sources/test-tools/xfstests/tests/generic/679.out` (20 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_scratch`, `_require_xfs_io_command "falloc"`, `_require_xfs_io_command "fiemap"`, `_exclude_fs xfs`.

## Risks and Edge Cases

- Most failures should surface as unexpected output, nonzero helper status, or harness `_fail`/`_notrun` behavior.

## Test Signals

The paired `.out` file has 20 line(s); its first visible signals are: 'QA output created by 679; wrote 209715200/209715200 bytes at offset 0; XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec); wrote 209715200/209715200 bytes at offset 210763776; XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec)'. Runtime pass/fail is also signaled by post-remount or failure-injection persistence checks. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/679 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/680 -->
# sources/test-tools/xfstests/tests/generic/680

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/680`. Test for the Dirty Pipe vulnerability (CVE-2022-0847) caused by an uninitialized "pipe_buffer.flags" variable, which fixed by: 9d2231c5d74e ("lib/iov_iter: initialize "flags" in new pipe_buffer") It is registered with `_begin_fstest auto quick`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 46 source line(s).
- Harness registration: `_begin_fstest auto quick`.
- Imported common libraries: `./common/preamble`.
- Capability and skip gates: `_require_test`, `_require_user`, `_require_chmod`, `_require_test_program "splice2pipe"`.
- Local shell functions: none visible.
- External `$here/src` helpers: `$here/src/splice2pipe $localfile 1 "AAAAAAAABBBBBBBB"`, `cp $here/src/splice2pipe $tmp.splice2pipe`.
- Notable variables and constants:
- `localfile=$TEST_DIR/testfile.$seq`

## Control Flow

- Capability gating runs first through `_require_test`, `_require_user`, `_require_chmod`, `_require_test_program "splice2pipe"`.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 27: echo "Test privileged user:"`
- `line 40: echo "Test unprivileged user:"`
- Key operational lines include:
- `line 24: $XFS_IO_PROG -f -t -c "pwrite 0 4k -S 0xff" $localfile >> $seqres.full 2>&1`
- `line 30: _hexdump $localfile`
- `line 34: $XFS_IO_PROG -f -t -c "pwrite 0 4k -S 0xff" $localfile >> $seqres.full 2>&1`
- `line 42: _hexdump $localfile`

## State and Persistence Behavior

Uses the configured xfstests test area or an explicitly created loop/image mount rather than always reformatting the scratch device. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick`, common helper libraries (`./common/preamble`), and the golden-output file `sources/test-tools/xfstests/tests/generic/680.out` (9 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_test`, `_require_user`, `_require_chmod`, `_require_test_program "splice2pipe"`.

## Risks and Edge Cases

- Most failures should surface as unexpected output, nonzero helper status, or harness `_fail`/`_notrun` behavior.

## Test Signals

The paired `.out` file has 9 line(s); its first visible signals are: 'QA output created by 680; Test privileged user:; 000000 ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff  >................<; *; 001000'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/680 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/681 -->
# sources/test-tools/xfstests/tests/generic/681

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/681`. Ensure that unprivileged userspace hits EDQUOT while linking files into a directory when the directory's quota limits have been exceeded. Regression test for commit: 871b9316e7a7 ("xfs: reserve quota for dir expansion when linking/unlinking files") It is registered with `_begin_fstest auto quick quota`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 69 source line(s).
- Harness registration: `_begin_fstest auto quick quota`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/quota`.
- Capability and skip gates: `_require_quota`, `_require_user`, `_require_scratch`.
- Local shell functions: none visible.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `blocksize=$(_get_dir_block_size $SCRATCH_MNT)`
- `scratchdir=$SCRATCH_MNT/dir`
- `scratchfile=$SCRATCH_MNT/file`
- `total_size=$((blocksize * 2))`
- `dirents=$((total_size / 255))`
- `name=$(printf "x%0254d" $i)`
- `name=$(printf "y%0254d" $i)`

## Control Flow

- Capability gating runs first through `_require_quota`, `_require_user`, `_require_scratch`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- User-visible phase markers include:
- `line 47: echo "set up quota" >> $seqres.full`
- `line 51: echo $(ls $scratchdir | wc -l) files in $scratchdir >> $seqres.full`
- `line 55: echo "fail quota" >> $seqres.full`
- `line 63: echo $(ls $scratchdir | wc -l) files in $scratchdir >> $seqres.full`
- `line 67: echo Silence is golden`
- Key operational lines include:
- `line 27: _scratch_mkfs > "$seqres.full" 2>&1`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick quota`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/quota`), and the golden-output file `sources/test-tools/xfstests/tests/generic/681.out` (3 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_quota`, `_require_user`, `_require_scratch`.

## Risks and Edge Cases

- Most failures should surface as unexpected output, nonzero helper status, or harness `_fail`/`_notrun` behavior.

## Test Signals

The paired `.out` file has 3 line(s); its first visible signals are: "QA output created by 681; ln: failed to create hard link 'SCRATCH_MNT/dir/yXXX': Disk quota exceeded; Silence is golden". Runtime pass/fail is primarily the command exit status plus golden-output comparison. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/681 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/682 -->
# sources/test-tools/xfstests/tests/generic/682

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/682`. Ensure that unprivileged userspace hits EDQUOT while moving files into a directory when the directory's quota limits have been exceeded. Regression test for commit: 41667260bc84 ("xfs: reserve quota for target dir expansion when renaming files") It is registered with `_begin_fstest auto quick quota`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 79 source line(s).
- Harness registration: `_begin_fstest auto quick quota`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/quota`.
- Capability and skip gates: `_require_quota`, `_require_user`, `_require_scratch`.
- Local shell functions: `_filter_mv_output`.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `blocksize=$(_get_dir_block_size $SCRATCH_MNT)`
- `scratchdir=$SCRATCH_MNT/dir`
- `scratchfile=$SCRATCH_MNT/file`
- `stagedir=$SCRATCH_MNT/staging`
- `total_size=$((blocksize * 2))`
- `dirents=$((total_size / 255))`
- `name=$(printf "x%0254d" $i)`
- `name=$(printf "y%0254d" $i)`

## Control Flow

- Capability gating runs first through `_require_quota`, `_require_user`, `_require_scratch`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- User-visible phase markers include:
- `line 48: echo "set up quota" >> $seqres.full`
- `line 52: echo $(ls $scratchdir | wc -l) files in $scratchdir >> $seqres.full`
- `line 64: echo "fail quota" >> $seqres.full`
- `line 73: echo $(ls $scratchdir | wc -l) files in $scratchdir >> $seqres.full`
- `line 77: echo Silence is golden`
- Key operational lines include:
- `line 27: _scratch_mkfs > "$seqres.full" 2>&1`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick quota`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/quota`), and the golden-output file `sources/test-tools/xfstests/tests/generic/682.out` (3 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_quota`, `_require_user`, `_require_scratch`.

## Risks and Edge Cases

- Most failures should surface as unexpected output, nonzero helper status, or harness `_fail`/`_notrun` behavior.

## Test Signals

The paired `.out` file has 3 line(s); its first visible signals are: "QA output created by 682; mv: cannot overwrite 'SCRATCH_MNT/dir/yXXX': Disk quota exceeded; Silence is golden". Runtime pass/fail is primarily the command exit status plus golden-output comparison. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/682 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/683 -->
# sources/test-tools/xfstests/tests/generic/683

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/683`. Functional test for dropping suid and sgid bits as part of a fallocate. It is registered with `_begin_fstest auto clone quick perms prealloc`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 125 source line(s).
- Harness registration: `_begin_fstest auto clone quick perms prealloc`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/reflink`.
- Capability and skip gates: `_require_user`, `_require_test`, `_require_xfs_io_command $verb`, `_require_congruent_file_oplen $TEST_DIR 65536`.
- Local shell functions: `_cleanup`, `setup_testfile`, `commit_and_check`.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `verb=falloc`
- `junk_dir=$TEST_DIR/$seq`
- `junk_file=$junk_dir/a`

## Control Flow

- Capability gating runs first through `_require_user`, `_require_test`, `_require_xfs_io_command $verb`, `_require_congruent_file_oplen $TEST_DIR 65536`.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 60: echo`
- `line 64: echo "Test 1 - qa_user, non-exec file $verb"`
- `line 70: echo "Test 2 - qa_user, group-exec file $verb"`
- `line 76: echo "Test 3 - qa_user, user-exec file $verb"`
- `line 82: echo "Test 4 - qa_user, all-exec file $verb"`
- `line 88: echo "Test 5 - root, non-exec file $verb"`
- `line 94: echo "Test 6 - root, group-exec file $verb"`
- `line 100: echo "Test 7 - root, user-exec file $verb"`
- Key operational lines include:
- `line 27: verb=falloc`
- `line 48: stat -c '%a %A %n' $junk_file | _filter_test_dir`
- `line 50: local cmd="$XFS_IO_PROG -c '$command $start $end' $junk_file"`
- `line 57: stat -c '%a %A %n' $junk_file | _filter_test_dir`

## State and Persistence Behavior

Uses the configured xfstests test area or an explicitly created loop/image mount rather than always reformatting the scratch device. Shared extent or atomic-update state is exercised, so correctness depends on clone/dedupe/exchange persistence and metadata ordering. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto clone quick perms prealloc`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/reflink`), and the golden-output file `sources/test-tools/xfstests/tests/generic/683.out` (41 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_user`, `_require_test`, `_require_xfs_io_command $verb`, `_require_congruent_file_oplen $TEST_DIR 65536`.

## Risks and Edge Cases

- Shared-extent and exchange operations can expose stale data, permission-bit, or log-ordering bugs that only appear after remount/recovery.

## Test Signals

The paired `.out` file has 41 line(s); its first visible signals are: 'QA output created by 683; Test 1 - qa_user, non-exec file falloc; 6666 -rwSrwSrw- TEST_DIR/683/a; 666 -rw-rw-rw- TEST_DIR/683/a'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands, xfstests output filters. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/683 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/684 -->
# sources/test-tools/xfstests/tests/generic/684

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/684`. Functional test for dropping suid and sgid bits as part of a fpunch. It is registered with `_begin_fstest auto clone quick perms punch`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 125 source line(s).
- Harness registration: `_begin_fstest auto clone quick perms punch`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/reflink`.
- Capability and skip gates: `_require_user`, `_require_test`, `_require_xfs_io_command $verb`, `_require_congruent_file_oplen $TEST_DIR 65536`.
- Local shell functions: `_cleanup`, `setup_testfile`, `commit_and_check`.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `verb=fpunch`
- `junk_dir=$TEST_DIR/$seq`
- `junk_file=$junk_dir/a`

## Control Flow

- Capability gating runs first through `_require_user`, `_require_test`, `_require_xfs_io_command $verb`, `_require_congruent_file_oplen $TEST_DIR 65536`.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 60: echo`
- `line 64: echo "Test 1 - qa_user, non-exec file $verb"`
- `line 70: echo "Test 2 - qa_user, group-exec file $verb"`
- `line 76: echo "Test 3 - qa_user, user-exec file $verb"`
- `line 82: echo "Test 4 - qa_user, all-exec file $verb"`
- `line 88: echo "Test 5 - root, non-exec file $verb"`
- `line 94: echo "Test 6 - root, group-exec file $verb"`
- `line 100: echo "Test 7 - root, user-exec file $verb"`
- Key operational lines include:
- `line 48: stat -c '%a %A %n' $junk_file | _filter_test_dir`
- `line 50: local cmd="$XFS_IO_PROG -c '$command $start $end' $junk_file"`
- `line 57: stat -c '%a %A %n' $junk_file | _filter_test_dir`

## State and Persistence Behavior

Uses the configured xfstests test area or an explicitly created loop/image mount rather than always reformatting the scratch device. Shared extent or atomic-update state is exercised, so correctness depends on clone/dedupe/exchange persistence and metadata ordering. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto clone quick perms punch`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/reflink`), and the golden-output file `sources/test-tools/xfstests/tests/generic/684.out` (41 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_user`, `_require_test`, `_require_xfs_io_command $verb`, `_require_congruent_file_oplen $TEST_DIR 65536`.

## Risks and Edge Cases

- Shared-extent and exchange operations can expose stale data, permission-bit, or log-ordering bugs that only appear after remount/recovery.

## Test Signals

The paired `.out` file has 41 line(s); its first visible signals are: 'QA output created by 684; Test 1 - qa_user, non-exec file fpunch; 6666 -rwSrwSrw- TEST_DIR/684/a; 666 -rw-rw-rw- TEST_DIR/684/a'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands, xfstests output filters. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/684 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/685 -->
# sources/test-tools/xfstests/tests/generic/685

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/685`. Functional test for dropping suid and sgid bits as part of a fzero. It is registered with `_begin_fstest auto clone quick perms zero`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 125 source line(s).
- Harness registration: `_begin_fstest auto clone quick perms zero`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/reflink`.
- Capability and skip gates: `_require_user`, `_require_test`, `_require_xfs_io_command $verb`, `_require_congruent_file_oplen $TEST_DIR 65536`.
- Local shell functions: `_cleanup`, `setup_testfile`, `commit_and_check`.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `verb=fzero`
- `junk_dir=$TEST_DIR/$seq`
- `junk_file=$junk_dir/a`

## Control Flow

- Capability gating runs first through `_require_user`, `_require_test`, `_require_xfs_io_command $verb`, `_require_congruent_file_oplen $TEST_DIR 65536`.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 60: echo`
- `line 64: echo "Test 1 - qa_user, non-exec file $verb"`
- `line 70: echo "Test 2 - qa_user, group-exec file $verb"`
- `line 76: echo "Test 3 - qa_user, user-exec file $verb"`
- `line 82: echo "Test 4 - qa_user, all-exec file $verb"`
- `line 88: echo "Test 5 - root, non-exec file $verb"`
- `line 94: echo "Test 6 - root, group-exec file $verb"`
- `line 100: echo "Test 7 - root, user-exec file $verb"`
- Key operational lines include:
- `line 48: stat -c '%a %A %n' $junk_file | _filter_test_dir`
- `line 50: local cmd="$XFS_IO_PROG -c '$command $start $end' $junk_file"`
- `line 57: stat -c '%a %A %n' $junk_file | _filter_test_dir`

## State and Persistence Behavior

Uses the configured xfstests test area or an explicitly created loop/image mount rather than always reformatting the scratch device. Shared extent or atomic-update state is exercised, so correctness depends on clone/dedupe/exchange persistence and metadata ordering. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto clone quick perms zero`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/reflink`), and the golden-output file `sources/test-tools/xfstests/tests/generic/685.out` (41 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_user`, `_require_test`, `_require_xfs_io_command $verb`, `_require_congruent_file_oplen $TEST_DIR 65536`.

## Risks and Edge Cases

- Shared-extent and exchange operations can expose stale data, permission-bit, or log-ordering bugs that only appear after remount/recovery.

## Test Signals

The paired `.out` file has 41 line(s); its first visible signals are: 'QA output created by 685; Test 1 - qa_user, non-exec file fzero; 6666 -rwSrwSrw- TEST_DIR/685/a; 666 -rw-rw-rw- TEST_DIR/685/a'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands, xfstests output filters. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/685 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/686 -->
# sources/test-tools/xfstests/tests/generic/686

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/686`. Functional test for dropping suid and sgid bits as part of a finsert. It is registered with `_begin_fstest auto clone insert quick perms`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 125 source line(s).
- Harness registration: `_begin_fstest auto clone insert quick perms`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/reflink`.
- Capability and skip gates: `_require_user`, `_require_test`, `_require_xfs_io_command $verb`, `_require_congruent_file_oplen $TEST_DIR 65536`.
- Local shell functions: `_cleanup`, `setup_testfile`, `commit_and_check`.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `verb=finsert`
- `junk_dir=$TEST_DIR/$seq`
- `junk_file=$junk_dir/a`

## Control Flow

- Capability gating runs first through `_require_user`, `_require_test`, `_require_xfs_io_command $verb`, `_require_congruent_file_oplen $TEST_DIR 65536`.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 60: echo`
- `line 64: echo "Test 1 - qa_user, non-exec file $verb"`
- `line 70: echo "Test 2 - qa_user, group-exec file $verb"`
- `line 76: echo "Test 3 - qa_user, user-exec file $verb"`
- `line 82: echo "Test 4 - qa_user, all-exec file $verb"`
- `line 88: echo "Test 5 - root, non-exec file $verb"`
- `line 94: echo "Test 6 - root, group-exec file $verb"`
- `line 100: echo "Test 7 - root, user-exec file $verb"`
- Key operational lines include:
- `line 27: verb=finsert`
- `line 48: stat -c '%a %A %n' $junk_file | _filter_test_dir`
- `line 50: local cmd="$XFS_IO_PROG -c '$command $start $end' $junk_file"`
- `line 57: stat -c '%a %A %n' $junk_file | _filter_test_dir`

## State and Persistence Behavior

Uses the configured xfstests test area or an explicitly created loop/image mount rather than always reformatting the scratch device. Shared extent or atomic-update state is exercised, so correctness depends on clone/dedupe/exchange persistence and metadata ordering. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto clone insert quick perms`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/reflink`), and the golden-output file `sources/test-tools/xfstests/tests/generic/686.out` (41 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_user`, `_require_test`, `_require_xfs_io_command $verb`, `_require_congruent_file_oplen $TEST_DIR 65536`.

## Risks and Edge Cases

- Shared-extent and exchange operations can expose stale data, permission-bit, or log-ordering bugs that only appear after remount/recovery.

## Test Signals

The paired `.out` file has 41 line(s); its first visible signals are: 'QA output created by 686; Test 1 - qa_user, non-exec file finsert; 6666 -rwSrwSrw- TEST_DIR/686/a; 666 -rw-rw-rw- TEST_DIR/686/a'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands, xfstests output filters. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/686 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/687 -->
# sources/test-tools/xfstests/tests/generic/687

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/687`. Functional test for dropping suid and sgid bits as part of a fcollapse. It is registered with `_begin_fstest auto clone quick perms collapse`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 125 source line(s).
- Harness registration: `_begin_fstest auto clone quick perms collapse`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/reflink`.
- Capability and skip gates: `_require_user`, `_require_test`, `_require_xfs_io_command $verb`, `_require_congruent_file_oplen $TEST_DIR 65536`.
- Local shell functions: `_cleanup`, `setup_testfile`, `commit_and_check`.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `verb=fcollapse`
- `junk_dir=$TEST_DIR/$seq`
- `junk_file=$junk_dir/a`

## Control Flow

- Capability gating runs first through `_require_user`, `_require_test`, `_require_xfs_io_command $verb`, `_require_congruent_file_oplen $TEST_DIR 65536`.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 60: echo`
- `line 64: echo "Test 1 - qa_user, non-exec file $verb"`
- `line 70: echo "Test 2 - qa_user, group-exec file $verb"`
- `line 76: echo "Test 3 - qa_user, user-exec file $verb"`
- `line 82: echo "Test 4 - qa_user, all-exec file $verb"`
- `line 88: echo "Test 5 - root, non-exec file $verb"`
- `line 94: echo "Test 6 - root, group-exec file $verb"`
- `line 100: echo "Test 7 - root, user-exec file $verb"`
- Key operational lines include:
- `line 48: stat -c '%a %A %n' $junk_file | _filter_test_dir`
- `line 50: local cmd="$XFS_IO_PROG -c '$command $start $end' $junk_file"`
- `line 57: stat -c '%a %A %n' $junk_file | _filter_test_dir`

## State and Persistence Behavior

Uses the configured xfstests test area or an explicitly created loop/image mount rather than always reformatting the scratch device. Shared extent or atomic-update state is exercised, so correctness depends on clone/dedupe/exchange persistence and metadata ordering. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto clone quick perms collapse`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/reflink`), and the golden-output file `sources/test-tools/xfstests/tests/generic/687.out` (41 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_user`, `_require_test`, `_require_xfs_io_command $verb`, `_require_congruent_file_oplen $TEST_DIR 65536`.

## Risks and Edge Cases

- Shared-extent and exchange operations can expose stale data, permission-bit, or log-ordering bugs that only appear after remount/recovery.

## Test Signals

The paired `.out` file has 41 line(s); its first visible signals are: 'QA output created by 687; Test 1 - qa_user, non-exec file fcollapse; 6666 -rwSrwSrw- TEST_DIR/687/a; 666 -rw-rw-rw- TEST_DIR/687/a'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands, xfstests output filters. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/687 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/688 -->
# sources/test-tools/xfstests/tests/generic/688

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/688`. Functional test for dropping capability bits as part of an fallocate. It is registered with `_begin_fstest auto prealloc quick`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 78 source line(s).
- Harness registration: `_begin_fstest auto prealloc quick`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/attr`.
- Capability and skip gates: `_require_user`, `_require_command "$GETCAP_PROG" getcap`, `_require_command "$SETCAP_PROG" setcap`, `_require_xfs_io_command falloc`, `_require_test`, `_require_congruent_file_oplen $TEST_DIR 65536`, `_require_attrs security`.
- Local shell functions: `_cleanup`, `setup_testfile`, `commit_and_check`.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `junk_dir=$TEST_DIR/$seq`
- `junk_file=$junk_dir/a`

## Control Flow

- Capability gating runs first through `_require_user`, `_require_command "$GETCAP_PROG" getcap`, `_require_command "$SETCAP_PROG" setcap`, `_require_xfs_io_command falloc`, `_require_test`, plus 2 more.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 63: echo`
- `line 67: echo "Test 1 - qa_user"`
- `line 72: echo "Test 2 - root"`
- Key operational lines include:
- `line 28: _require_xfs_io_command falloc`
- `line 49: stat -c '%a %A %n' $junk_file | _filter_test_dir`
- `line 52: local cmd="$XFS_IO_PROG -c 'falloc 0 64k' $junk_file"`
- `line 59: stat -c '%a %A %n' $junk_file | _filter_test_dir`

## State and Persistence Behavior

Uses the configured xfstests test area or an explicitly created loop/image mount rather than always reformatting the scratch device. Extended attributes are part of the persistent state being created, replayed, or verified. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto prealloc quick`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/attr`), and the golden-output file `sources/test-tools/xfstests/tests/generic/688.out` (13 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_user`, `_require_command "$GETCAP_PROG" getcap`, `_require_command "$SETCAP_PROG" setcap`, `_require_xfs_io_command falloc`, `_require_test`, `_require_congruent_file_oplen $TEST_DIR 65536`, `_require_attrs security`.

## Risks and Edge Cases

- Most failures should surface as unexpected output, nonzero helper status, or harness `_fail`/`_notrun` behavior.

## Test Signals

The paired `.out` file has 13 line(s); its first visible signals are: 'QA output created by 688; Test 1 - qa_user; 777 -rwxrwxrwx TEST_DIR/688/a; TEST_DIR/688/a cap_setgid,cap_setuid=ep; 777 -rwxrwxrwx TEST_DIR/688/a'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands, xfstests output filters. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/688 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/689 -->
# sources/test-tools/xfstests/tests/generic/689

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/689`. Test that setting POSIX ACLs in userns-mountable filesystems works. Regression test for commit: 705191b03d50 ("fs: fix acl translation") It is registered with `_begin_fstest auto quick perms idmapped`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 33 source line(s).
- Harness registration: `_begin_fstest auto quick perms idmapped`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/attr`.
- Capability and skip gates: `_require_test`, `_require_idmapped_mounts`, `_require_acls`, `_require_user fsgqa`, `_require_group fsgqa`.
- Local shell functions: none visible.
- External `$here/src` helpers: `$here/src/vfs/vfstest --test-setxattr-fix-705191b03d50 \`.

## Control Flow

- Capability gating runs first through `_require_test`, `_require_idmapped_mounts`, `_require_acls`, `_require_user fsgqa`, `_require_group fsgqa`.
- User-visible phase markers include:
- `line 27: echo "Silence is golden"`

## State and Persistence Behavior

Uses the configured xfstests test area or an explicitly created loop/image mount rather than always reformatting the scratch device. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick perms idmapped`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/attr`), and the golden-output file `sources/test-tools/xfstests/tests/generic/689.out` (2 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_test`, `_require_idmapped_mounts`, `_require_acls`, `_require_user fsgqa`, `_require_group fsgqa`.

## Risks and Edge Cases

- Feature gates depend on kernel, userspace tool, and filesystem support; unsupported features correctly produce `_notrun`.

## Test Signals

The paired `.out` file has 2 line(s); its first visible signals are: 'QA output created by 689; Silence is golden'. Runtime pass/fail is primarily the command exit status plus golden-output comparison. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/689 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/690 -->
# sources/test-tools/xfstests/tests/generic/690

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/690`. Test that if we fsync a directory, create a symlink inside it, rename the symlink, fsync again the directory and then power fail, after the filesystem is mounted again, the symlink exists with the new name and it has the correct content. On btrfs this used to result in the symlink being empty (i_size 0), and it was fixed by kernel commit: d0e64a981fd841 ("btrfs: always log symlinks in full mode") It is registered with `_begin_fstest auto quick log`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 87 source line(s).
- Harness registration: `_begin_fstest auto quick log`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/dmflakey`.
- Capability and skip gates: `_require_scratch`, `_require_symlinks`, `_require_dm_target flakey`, `_require_metadata_journaling $SCRATCH_DEV`.
- Local shell functions: `_cleanup`.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `symlink_content=$(readlink "$SCRATCH_MNT"/testdir/baz | _filter_scratch)`

## Control Flow

- Capability gating runs first through `_require_scratch`, `_require_symlinks`, `_require_dm_target flakey`, `_require_metadata_journaling $SCRATCH_DEV`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- User-visible phase markers include:
- `line 59: echo -n > "$SCRATCH_MNT"/testdir/foo`
- `line 81: echo "symlink content: ${symlink_content}"`
- Key operational lines include:
- `line 22: _cleanup_flakey`
- `line 46: _scratch_mkfs >>$seqres.full 2>&1`
- `line 48: _init_flakey`
- `line 49: _scratch_mount`
- `line 55: _scratch_sync`
- `line 62: $XFS_IO_PROG -c "fsync" "$SCRATCH_MNT"/testdir`
- `line 71: $XFS_IO_PROG -c "fsync" "$SCRATCH_MNT"/testdir`
- `line 75: _flakey_drop_and_remount`
- `line 83: _scratch_unmount`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Synthetic block-device state can be introduced through device-mapper, loop, SCSI debug, or huge-device helpers and must be cleaned even on failure. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick log`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/dmflakey`), and the golden-output file `sources/test-tools/xfstests/tests/generic/690.out` (2 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_scratch`, `_require_symlinks`, `_require_dm_target flakey`, `_require_metadata_journaling $SCRATCH_DEV`.

## Risks and Edge Cases

- Failure-injection paths can leave mounts or synthetic device tables behind if cleanup is interrupted.

## Test Signals

The paired `.out` file has 2 line(s); its first visible signals are: 'QA output created by 690; symlink content: SCRATCH_MNT/testdir/foo'. Runtime pass/fail is also signaled by post-remount or failure-injection persistence checks. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/690 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/691 -->
# sources/test-tools/xfstests/tests/generic/691

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/691`. Make sure filesystem quota works well, after soft limits are exceeded. The fs quota should allow more space allocation before exceeding hard limits and with in grace time. But different with other similar testing, this case tries to write many small files, to cover bc37e4fb5cac (xfs: revert "xfs: actually bump warning counts when we send warnings"). If there's a behavior change some day, this case might help to detect that too. It is registered with `_begin_fstest auto quota`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 109 source line(s).
- Harness registration: `_begin_fstest auto quota`.
- Imported common libraries: `./common/preamble`, `./common/quota`.
- Capability and skip gates: `_require_scratch`, `_require_quota`, `_require_user`, `_require_group`, `_require_prjquota $SCRATCH_DEV`.
- Local shell functions: `_cleanup`, `filter_quota`, `exercise`.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `projid=$seq`
- `file=$SCRATCH_MNT/t/testfile`

## Control Flow

- Capability gating runs first through `_require_scratch`, `_require_quota`, `_require_user`, `_require_group`, `_require_prjquota $SCRATCH_DEV`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- User-visible phase markers include:
- `line 63: echo "= Test type=$type quota =" >>$seqres.full`
- `line 86: echo "Unexpected error (type=$type)!"`
- Key operational lines include:
- `line 38: _scratch_mkfs >$seqres.full 2>&1`
- `line 39: _scratch_enable_pquota`
- `line 64: _scratch_unmount`
- `line 65: _scratch_mkfs >>$seqres.full 2>&1`
- `line 67: _scratch_enable_pquota`
- `line 80: _su $qa_user -c "$XFS_IO_PROG -f -t -c 'pwrite 0 2m' -c fsync ${file}.0" >>$seqres.full`
- `line 84: _su "$qa_user" -c "$XFS_IO_PROG -f -c 'pwrite 0 1m' -c fsync ${file}.$i" >>$seqres.full`
- `line 94: _su $qa_user -c "$XFS_IO_PROG -f -t -c 'pwrite 0 100m' -c fsync ${file}.hard.0" 2>&1 >/dev/null | filter_quota $type`
- `line 96: _su "$qa_user" -c "$XFS_IO_PROG -f -c 'pwrite 0 1m' -c fsync ${file}.hard.$i" 2>&1 | filter_quota $type`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quota`, common helper libraries (`./common/preamble`, `./common/quota`), and the golden-output file `sources/test-tools/xfstests/tests/generic/691.out` (34 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_scratch`, `_require_quota`, `_require_user`, `_require_group`, `_require_prjquota $SCRATCH_DEV`.

## Risks and Edge Cases

- Most failures should surface as unexpected output, nonzero helper status, or harness `_fail`/`_notrun` behavior.

## Test Signals

The paired `.out` file has 34 line(s); its first visible signals are: 'QA output created by 691; Error: Disk quota exceeded; Error: Disk quota exceeded; Error: Disk quota exceeded; Error: Disk quota exceeded'. Runtime pass/fail is primarily the command exit status plus golden-output comparison. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/691 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/692 -->
# sources/test-tools/xfstests/tests/generic/692

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/692`. fs-verity requires the filesystem to decide how it stores the Merkle tree, which can be quite large. It is convenient to treat the Merkle tree as past EOF, and ext4, f2fs, and btrfs do so in at least some fashion. This leads to an edge case where a large file can be under the file system file size limit, but trigger EFBIG on enabling fs-verity. Test enabling verity on some large files to exercise EFBIG logic for filesystems with fs-verity specific limits. It is registered with `_begin_fstest auto quick verity`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 83 source line(s).
- Harness registration: `_begin_fstest auto quick verity`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/verity`.
- Capability and skip gates: `_require_test`, `_require_math`, `_require_scratch_verity`, `_require_fsverity_max_file_size_limit`.
- Local shell functions: `_cleanup`.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `fsv_file=$SCRATCH_MNT/file.fsv`
- `max_sz=$(_get_max_file_size $SCRATCH_MNT)`
- `bs=$FSV_BLOCK_SIZE`
- `hash_size=32 # SHA-256`
- `hashes_per_block=$(echo "scale=30; $bs/$hash_size" | $BC -q)`
- `a=$(echo "scale=30; 1/($hashes_per_block^2)" | $BC -q)`
- `r=$(echo "scale=30; 1/$hashes_per_block" | $BC -q)`
- `nonleaves_relative_size=$(echo "scale=30; $a/(1-$r)" | $BC -q)`
- `sz=$(echo "$max_sz/(1+$nonleaves_relative_size)" | $BC -q)`
- `sz=$(echo "$sz - 65536 - $bs*11" | $BC -q)`

## Control Flow

- Capability gating runs first through `_require_test`, `_require_math`, `_require_scratch_verity`, `_require_fsverity_max_file_size_limit`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- Key operational lines include:
- `line 32: _require_scratch_verity`
- `line 36: _scratch_mkfs_verity &>> $seqres.full`
- `line 37: _scratch_mount`
- `line 42: _fsv_scratch_begin_subtest "way too big: fail on first merkle block"`
- `line 44: _fsv_enable $fsv_file |& _filter_scratch`
- `line 77: _fsv_scratch_begin_subtest "still too big: fail on first invalid merkle block"`
- `line 79: _fsv_enable $fsv_file |& _filter_scratch`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. fs-verity metadata, signatures, or Merkle trees become durable file metadata and are compared against userspace-computed expectations. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick verity`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/verity`), and the golden-output file `sources/test-tools/xfstests/tests/generic/692.out` (7 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_test`, `_require_math`, `_require_scratch_verity`, `_require_fsverity_max_file_size_limit`.

## Risks and Edge Cases

- Feature gates depend on kernel, userspace tool, and filesystem support; unsupported features correctly produce `_notrun`.

## Test Signals

The paired `.out` file has 7 line(s); its first visible signals are: "QA output created by 692; # way too big: fail on first merkle block; ERROR: FS_IOC_ENABLE_VERITY failed on 'SCRATCH_MNT/file.fsv': File too large". Runtime pass/fail is also signaled by xfstests output filters, hang/race detection through background work, loops, or timeout windows. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/692 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/693 -->
# sources/test-tools/xfstests/tests/generic/693

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/693`. Verify ciphertext for v2 encryption policies that use AES-256-XTS to encrypt file contents and AES-256-HCTR2 to encrypt file names. HCTR2 was introduced in kernel commit 6b2a51ff03bf ("fscrypt: Add HCTR2 support for filename encryption") It is registered with `_begin_fstest auto quick encrypt`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 29 source line(s).
- Harness registration: `_begin_fstest auto quick encrypt`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/encrypt`.
- Capability and skip gates: none visible.
- Local shell functions: none visible.
- External `$here/src` helpers: none visible.

## Control Flow

- After harness setup, the script executes its helper or shell reproducer and lets the xfstests runner compare output and exit status.
- Key operational lines include:
- `line 21: _verify_ciphertext_for_encryption_policy AES-256-XTS AES-256-HCTR2 v2`
- `line 22: _verify_ciphertext_for_encryption_policy AES-256-XTS AES-256-HCTR2 \`
- `line 24: _verify_ciphertext_for_encryption_policy AES-256-XTS AES-256-HCTR2 \`

## State and Persistence Behavior

Uses the configured xfstests test area or an explicitly created loop/image mount rather than always reformatting the scratch device. Encryption policy/key state is created during the test and used to check no-key/key-present transitions. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick encrypt`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/encrypt`), and the golden-output file `sources/test-tools/xfstests/tests/generic/693.out` (16 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: none visible.

## Risks and Edge Cases

- Feature gates depend on kernel, userspace tool, and filesystem support; unsupported features correctly produce `_notrun`.

## Test Signals

The paired `.out` file has 16 line(s); its first visible signals are: 'QA output created by 693; Verifying ciphertext with parameters:; contents_encryption_mode: AES-256-XTS; filenames_encryption_mode: AES-256-HCTR2'. Runtime pass/fail is primarily the command exit status plus golden-output comparison. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/693 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/694 -->
# sources/test-tools/xfstests/tests/generic/694

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/694`. Verify that i_blocks for files larger than 4 GiB have correct values. This test verifies the problem fixed in kernel with commit 0c336d6e33f4 exfat: fix incorrect loading of i_blocks for large files It is registered with `_begin_fstest auto`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 56 source line(s).
- Harness registration: `_begin_fstest auto`.
- Imported common libraries: `./common/preamble`.
- Capability and skip gates: `_fixed_by_kernel_commit 0c336d6e33f4 "exfat: fix incorrect loading of i_blocks for large file"`, `_require_test`, `_require_fs_space $TEST_DIR $((4 * 1024 * 1024)) #kB`.
- Local shell functions: `_cleanup`.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `junk_dir=$TEST_DIR/$seq`
- `junk_file=$junk_dir/junk`
- `iblocks=`stat -c '%b' $junk_file``
- `iblocks_after_remount=`stat -c '%b' $junk_file``

## Control Flow

- Capability gating runs first through `_fixed_by_kernel_commit 0c336d6e33f4 "exfat: fix incorrect loading of i_blocks for large file"`, `_require_test`, `_require_fs_space $TEST_DIR $((4 * 1024 * 1024)) #kB`.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 29: echo "Silence is golden"`
- `line 37: echo "Could not create 4G test file"`
- `line 51: echo "Number of blocks needs to be same: $iblocks, $iblocks_after_remount"`
- Key operational lines include:
- `line 44: iblocks=`stat -c '%b' $junk_file``
- `line 48: iblocks_after_remount=`stat -c '%b' $junk_file``

## State and Persistence Behavior

Uses the configured xfstests test area or an explicitly created loop/image mount rather than always reformatting the scratch device. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto`, common helper libraries (`./common/preamble`), and the golden-output file `sources/test-tools/xfstests/tests/generic/694.out` (2 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_fixed_by_kernel_commit 0c336d6e33f4 "exfat: fix incorrect loading of i_blocks for large file"`, `_require_test`, `_require_fs_space $TEST_DIR $((4 * 1024 * 1024)) #kB`.

## Risks and Edge Cases

- Most failures should surface as unexpected output, nonzero helper status, or harness `_fail`/`_notrun` behavior.

## Test Signals

The paired `.out` file has 2 line(s); its first visible signals are: 'QA output created by 694; Silence is golden'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/694 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/695 -->
# sources/test-tools/xfstests/tests/generic/695

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/695`. Test that if we punch a hole adjacent to an existing hole, fsync the file and then power fail, the new hole exists after mounting again the filesystem. This is motivated by a regression on btrfs, fixed by the commit mentioned below, when not using the no-holes feature (which is enabled by default since btrfs-progs 5.15). It is registered with `_begin_fstest auto quick log punch fiemap`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 90 source line(s).
- Harness registration: `_begin_fstest auto quick log punch fiemap`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/dmflakey`, `./common/punch`.
- Capability and skip gates: `_fixed_by_fs_commit btrfs e6e3dec6c3c288 "btrfs: update generation of hole file extent item when merging holes"`, `_require_scratch`, `_require_dm_target flakey`, `_require_xfs_io_command "fpunch"`, `_require_xfs_io_command "fiemap"`, `_require_metadata_journaling $SCRATCH_DEV`, `_require_congruent_file_oplen $SCRATCH_MNT $((2 * 1024 * 1024))`.
- Local shell functions: `_cleanup`.
- External `$here/src` helpers: none visible.

## Control Flow

- Capability gating runs first through `_fixed_by_fs_commit btrfs e6e3dec6c3c288 "btrfs: update generation of hole file extent item when merging holes"`, `_require_scratch`, `_require_dm_target flakey`, `_require_xfs_io_command "fpunch"`, `_require_xfs_io_command "fiemap"`, plus 2 more.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 78: echo "File layout after power failure:"`
- `line 83: echo "File content after power failure:"`
- Key operational lines include:
- `line 19: _cleanup_flakey`
- `line 35: _scratch_mkfs >>$seqres.full 2>&1`
- `line 37: _init_flakey`
- `line 38: _scratch_mount`
- `line 49: $XFS_IO_PROG -f -c "truncate 12M" \`
- `line 54: _scratch_sync`
- `line 65: $XFS_IO_PROG -c "fpunch 2M 2M" \`
- `line 71: _flakey_drop_and_remount`
- `line 79: $XFS_IO_PROG -c "fiemap -v" $SCRATCH_MNT/foobar | _filter_fiemap`
- `line 84: _hexdump $SCRATCH_MNT/foobar`
- `line 86: _scratch_unmount`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Synthetic block-device state can be introduced through device-mapper, loop, SCSI debug, or huge-device helpers and must be cleaned even on failure. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick log punch fiemap`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/dmflakey`, `./common/punch`), and the golden-output file `sources/test-tools/xfstests/tests/generic/695.out` (15 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_fixed_by_fs_commit btrfs e6e3dec6c3c288 "btrfs: update generation of hole file extent item when merging holes"`, `_require_scratch`, `_require_dm_target flakey`, `_require_xfs_io_command "fpunch"`, `_require_xfs_io_command "fiemap"`, `_require_metadata_journaling $SCRATCH_DEV`, `_require_congruent_file_oplen $SCRATCH_MNT $((2 * 1024 * 1024))`.

## Risks and Edge Cases

- Failure-injection paths can leave mounts or synthetic device tables behind if cleanup is interrupted.

## Test Signals

The paired `.out` file has 15 line(s); its first visible signals are: 'QA output created by 695; wrote 8388608/8388608 bytes at offset 2097152; XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec); File layout after power failure:; 0: [0..8191]: hole'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands, post-remount or failure-injection persistence checks. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/695 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/696 -->
# sources/test-tools/xfstests/tests/generic/696

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/696`. Test S_ISGID stripping whether works correctly when call process uses umask(S_IXGRP). It is also a regression test for commit ac6800e279a2 ("fs: Add missing umask strip in vfs_tmpfile") commit 1639a49ccdce ("fs: move S_ISGID stripping into the vfs_*() helpers") It is registered with `_begin_fstest auto quick cap idmapped mount perms rw unlink`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 47 source line(s).
- Harness registration: `_begin_fstest auto quick cap idmapped mount perms rw unlink`.
- Imported common libraries: `./common/preamble`, `./common/filter`.
- Capability and skip gates: `_require_test`, `_require_scratch`, `_require_chmod`, `_fixed_by_kernel_commit ac6800e279a2 "fs: Add missing umask strip in vfs_tmpfile" 1639a49ccdce "fs: move S_ISGID stripping into the vfs_*() helpers"`.
- Local shell functions: none visible.
- External `$here/src` helpers: `$here/src/vfs/vfstest --test-setgid-create-umask \`.

## Control Flow

- Capability gating runs first through `_require_test`, `_require_scratch`, `_require_chmod`, `_fixed_by_kernel_commit ac6800e279a2 "fs: Add missing umask strip in vfs_tmpfile" 1639a49ccdce "fs: move S_ISGID stripping into the vfs_*() helpers"`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- User-visible phase markers include:
- `line 45: echo "Silence is golden"`
- Key operational lines include:
- `line 27: _scratch_mkfs >$seqres.full 2>&1`
- `line 41: _try_scratch_mount >>$seqres.full 2>&1 && \`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick cap idmapped mount perms rw unlink`, common helper libraries (`./common/preamble`, `./common/filter`), and the golden-output file `sources/test-tools/xfstests/tests/generic/696.out` (2 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_test`, `_require_scratch`, `_require_chmod`, `_fixed_by_kernel_commit ac6800e279a2 "fs: Add missing umask strip in vfs_tmpfile" 1639a49ccdce "fs: move S_ISGID stripping into the vfs_*() helpers"`.

## Risks and Edge Cases

- Feature gates depend on kernel, userspace tool, and filesystem support; unsupported features correctly produce `_notrun`.

## Test Signals

The paired `.out` file has 2 line(s); its first visible signals are: 'QA output created by 696; Silence is golden'. Runtime pass/fail is also signaled by hang/race detection through background work, loops, or timeout windows. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/696 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/697 -->
# sources/test-tools/xfstests/tests/generic/697

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/697`. Test S_ISGID stripping whether works correctly when call process uses posix acl. It is also a regression test for commit 1639a49ccdce ("fs: move S_ISGID stripping into the vfs_*() helpers") It is registered with `_begin_fstest auto quick cap acl idmapped mount perms rw unlink`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 30 source line(s).
- Harness registration: `_begin_fstest auto quick cap acl idmapped mount perms rw unlink`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/attr`.
- Capability and skip gates: `_require_test`, `_require_acls`, `_fixed_by_kernel_commit 1639a49ccdce "fs: move S_ISGID stripping into the vfs_*() helpers"`.
- Local shell functions: none visible.
- External `$here/src` helpers: `$here/src/vfs/vfstest --test-setgid-create-acl \`.

## Control Flow

- Capability gating runs first through `_require_test`, `_require_acls`, `_fixed_by_kernel_commit 1639a49ccdce "fs: move S_ISGID stripping into the vfs_*() helpers"`.
- User-visible phase markers include:
- `line 28: echo "Silence is golden"`

## State and Persistence Behavior

Uses the configured xfstests test area or an explicitly created loop/image mount rather than always reformatting the scratch device. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick cap acl idmapped mount perms rw unlink`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/attr`), and the golden-output file `sources/test-tools/xfstests/tests/generic/697.out` (2 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_test`, `_require_acls`, `_fixed_by_kernel_commit 1639a49ccdce "fs: move S_ISGID stripping into the vfs_*() helpers"`.

## Risks and Edge Cases

- Feature gates depend on kernel, userspace tool, and filesystem support; unsupported features correctly produce `_notrun`.

## Test Signals

The paired `.out` file has 2 line(s); its first visible signals are: 'QA output created by 697; Silence is golden'. Runtime pass/fail is primarily the command exit status plus golden-output comparison. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/697 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/698 -->
# sources/test-tools/xfstests/tests/generic/698

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/698`. Test that users can changed group ownership of a file they own to a group they are a member of. Regression test for commit: 168f91289340 ("fs: account for group membership") It is registered with `_begin_fstest auto quick perms attr idmapped mount`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 115 source line(s).
- Harness registration: `_begin_fstest auto quick perms attr idmapped mount`.
- Imported common libraries: `./common/preamble`.
- Capability and skip gates: `_fixed_by_kernel_commit 168f91289340 "fs: account for group membership"`, `_require_scratch`, `_require_chown`, `_require_idmapped_mounts`, `_require_test_program "vfs/mount-idmapped"`, `_require_user fsgqa2`, `_require_group fsgqa2`, `_require_user fsgqa`, `_require_group fsgqa`.
- Local shell functions: `_cleanup`, `setup_tree`, `setup_idmapped_mnt`, `change_group_ownership`, `run_base_test`, `run_idmapped_test`.
- External `$here/src` helpers: `$here/src/vfs/mount-idmapped \`.
- Notable variables and constants:
- `user_foo=`id -u fsgqa``
- `group_foo=`id -g fsgqa``
- `user_bar=`id -u fsgqa2``
- `group_bar=`id -g fsgqa2``

## Control Flow

- Capability gating runs first through `_fixed_by_kernel_commit 168f91289340 "fs: account for group membership"`, `_require_scratch`, `_require_chown`, `_require_idmapped_mounts`, `_require_test_program "vfs/mount-idmapped"`, plus 4 more.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 91: echo ""`
- `line 92: echo "base test"`
- `line 100: echo ""`
- `line 101: echo "base idmapped test"`
- Key operational lines include:
- `line 20: _unmount $SCRATCH_MNT/target-mnt 2>/dev/null`
- `line 21: _unmount $SCRATCH_MNT 2>/dev/null`
- `line 30: _require_test_program "vfs/mount-idmapped"`
- `line 59: $here/src/vfs/mount-idmapped \`
- `line 75: stat -c '%U:%G' $path`
- `line 77: stat -c '%U:%G' $path`
- `line 79: stat -c '%U:%G' $path`
- `line 105: _scratch_mkfs >> $seqres.full`
- `line 106: _scratch_mount`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Extended attributes are part of the persistent state being created, replayed, or verified. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick perms attr idmapped mount`, common helper libraries (`./common/preamble`), and the golden-output file `sources/test-tools/xfstests/tests/generic/698.out` (19 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_fixed_by_kernel_commit 168f91289340 "fs: account for group membership"`, `_require_scratch`, `_require_chown`, `_require_idmapped_mounts`, `_require_test_program "vfs/mount-idmapped"`, `_require_user fsgqa2`, `_require_group fsgqa2`, `_require_user fsgqa`, plus 1 more.

## Risks and Edge Cases

- Feature gates depend on kernel, userspace tool, and filesystem support; unsupported features correctly produce `_notrun`.

## Test Signals

The paired `.out` file has 19 line(s); its first visible signals are: 'QA output created by 698; base test; fsgqa:fsgqa2; fsgqa'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/698 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/699 -->
# sources/test-tools/xfstests/tests/generic/699

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/699`. This's copied from generic/698, extend it to test overlayfs on top of idmapped mounts specifically. It is registered with `_begin_fstest auto quick perms attr idmapped mount`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 166 source line(s).
- Harness registration: `_begin_fstest auto quick perms attr idmapped mount`.
- Imported common libraries: `./common/preamble`.
- Capability and skip gates: `_exclude_fs overlay`, `_require_extra_fs overlay`, `_require_scratch`, `_require_chown`, `_require_idmapped_mounts`, `_require_test_program "vfs/mount-idmapped"`, `_require_user fsgqa2`, `_require_group fsgqa2`, `_require_user fsgqa`, `_require_group fsgqa`, plus 1 more.
- Local shell functions: `_cleanup`, `setup_tree`, `setup_idmapped_mnt`, `change_group_ownership`, `reset_ownership`, `setup_overlayfs`, `setup_overlayfs_idmapped_lower_metacopy_off`, `setup_overlayfs_idmapped_lower_metacopy_on`, `reset_overlayfs`, `run_overlayfs_idmapped_lower_metacopy_off`, `run_overlayfs_idmapped_lower_metacopy_on`.
- External `$here/src` helpers: `$here/src/vfs/mount-idmapped \`.
- Notable variables and constants:
- `user_foo=`id -u fsgqa``
- `group_foo=`id -g fsgqa``
- `user_bar=`id -u fsgqa2``
- `group_bar=`id -g fsgqa2``
- `lower="$SCRATCH_MNT/target-mnt"`
- `upper="$SCRATCH_MNT/ovl-upper"`
- `work="$SCRATCH_MNT/ovl-work"`
- `merge="$SCRATCH_MNT/ovl-merge"`

## Control Flow

- Capability gating runs first through `_exclude_fs overlay`, `_require_extra_fs overlay`, `_require_scratch`, `_require_chown`, `_require_idmapped_mounts`, plus 6 more.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 90: echo ""`
- `line 91: echo "reset ownership"`
- `line 131: echo ""`
- `line 132: echo "overlayfs idmapped lower metacopy off"`
- `line 145: echo ""`
- `line 146: echo "overlayfs idmapped lower metacopy on"`
- Key operational lines include:
- `line 17: _unmount $SCRATCH_MNT/target-mnt`
- `line 18: _unmount $SCRATCH_MNT/ovl-merge 2>/dev/null`
- `line 19: _unmount $SCRATCH_MNT 2>/dev/null`
- `line 29: _require_test_program "vfs/mount-idmapped"`
- `line 58: $here/src/vfs/mount-idmapped \`
- `line 74: stat -c '%U:%G' $path`
- `line 76: stat -c '%U:%G' $path`
- `line 78: stat -c '%U:%G' $path`
- `line 93: stat -c '%u:%g' $path`
- `line 95: stat -c '%u:%g' $path`
- `line 101: _mount -t overlay -o lowerdir=$lower,upperdir=$upper,workdir=$work \`
- `line 120: _unmount $SCRATCH_MNT/ovl-merge 2>/dev/null`
- `line 152: _scratch_mkfs >> $seqres.full`
- `line 153: _scratch_mount`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Extended attributes are part of the persistent state being created, replayed, or verified. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick perms attr idmapped mount`, common helper libraries (`./common/preamble`), and the golden-output file `sources/test-tools/xfstests/tests/generic/699.out` (27 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_exclude_fs overlay`, `_require_extra_fs overlay`, `_require_scratch`, `_require_chown`, `_require_idmapped_mounts`, `_require_test_program "vfs/mount-idmapped"`, `_require_user fsgqa2`, `_require_group fsgqa2`, plus 3 more.

## Risks and Edge Cases

- Feature gates depend on kernel, userspace tool, and filesystem support; unsupported features correctly produce `_notrun`.

## Test Signals

The paired `.out` file has 27 line(s); its first visible signals are: 'QA output created by 699; overlayfs idmapped lower metacopy off; fsgqa:fsgqa2; fsgqa'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/699 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/700 -->
# sources/test-tools/xfstests/tests/generic/700

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/700`. Verify selinux label can be kept after RENAME_WHITEOUT. This is a regression test for: 70b589a37e1a ("xfs: add selinux labels to whiteout inodes") It is registered with `_begin_fstest auto quick rename attr whiteout`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 62 source line(s).
- Harness registration: `_begin_fstest auto quick rename attr whiteout`.
- Imported common libraries: `./common/preamble`, `./common/attr`, `./common/renameat2`.
- Capability and skip gates: `_require_scratch`, `_require_attrs`, `_require_renameat2 whiteout`, `_fixed_by_fs_commit xfs 70b589a37e1a "xfs: add selinux labels to whiteout inodes"`, `_notrun "Require selinux to be enabled"`.
- Local shell functions: `get_selinux_label`.
- External `$here/src` helpers: `$here/src/renameat2 -w $SCRATCH_MNT/f1 $SCRATCH_MNT/f2`.
- Notable variables and constants:
- `label=$(_getfattr --absolute-names -n security.selinux $@ | sed -n 's/security.selinux=\"\(.*\)\"/\1/p')`
- `label1=$(get_selinux_label $SCRATCH_MNT/f1)`
- `label2=$(get_selinux_label $SCRATCH_MNT/f2)`

## Control Flow

- Capability gating runs first through `_require_scratch`, `_require_attrs`, `_require_renameat2 whiteout`, `_fixed_by_fs_commit xfs 70b589a37e1a "xfs: add selinux labels to whiteout inodes"`, `_notrun "Require selinux to be enabled"`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- User-visible phase markers include:
- `line 33: echo $label`
- `line 47: echo "Before RENAME_WHITEOUT" >> $seqres.full`
- `line 51: echo "After RENAME_WHITEOUT" >> $seqres.full`
- `line 56: echo "$label1 != $label2"`
- `line 59: echo "Silence is golden"`
- Key operational lines include:
- `line 20: _require_renameat2 whiteout`
- `line 29: label=$(_getfattr --absolute-names -n security.selinux $@ | sed -n 's/security.selinux=\"\(.*\)\"/\1/p')`
- `line 36: _scratch_mkfs >> $seqres.full 2>&1`
- `line 44: _scratch_mount`
- `line 50: $here/src/renameat2 -w $SCRATCH_MNT/f1 $SCRATCH_MNT/f2`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Extended attributes are part of the persistent state being created, replayed, or verified. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick rename attr whiteout`, common helper libraries (`./common/preamble`, `./common/attr`, `./common/renameat2`), and the golden-output file `sources/test-tools/xfstests/tests/generic/700.out` (2 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_scratch`, `_require_attrs`, `_require_renameat2 whiteout`, `_fixed_by_fs_commit xfs 70b589a37e1a "xfs: add selinux labels to whiteout inodes"`, `_notrun "Require selinux to be enabled"`.

## Risks and Edge Cases

- Directory mutation and rename races depend on dentry-cache timing and may need repeated attempts to expose regressions.

## Test Signals

The paired `.out` file has 2 line(s); its first visible signals are: 'QA output created by 700; Silence is golden'. Runtime pass/fail is primarily the command exit status plus golden-output comparison. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/700 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/701 -->
# sources/test-tools/xfstests/tests/generic/701

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/701`. Verify that i_blocks for truncated files larger than 4 GiB have correct values. This test verifies the problem fixed in kernel with commit 92fba084b79e exfat: fix i_blocks for files truncated over 4 GiB It is registered with `_begin_fstest auto`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 50 source line(s).
- Harness registration: `_begin_fstest auto`.
- Imported common libraries: `./common/preamble`, `./common/filter`.
- Capability and skip gates: `_fixed_by_fs_commit exfat 92fba084b79e "exfat: fix i_blocks for files truncated over 4 GiB"`, `_require_test`, `_require_fs_space $TEST_DIR $((5 * 1024 * 1024)) #kB`.
- Local shell functions: `_cleanup`.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `junk_dir=$TEST_DIR/$seq`
- `junk_file=$junk_dir/junk`
- `block_size=`stat -c '%B' $junk_file``
- `iblocks_after_truncate=`stat -c '%b' $junk_file``
- `iblocks_expected=$((4 * 1024 * 1024 * 1024 / $block_size))`

## Control Flow

- Capability gating runs first through `_fixed_by_fs_commit exfat 92fba084b79e "exfat: fix i_blocks for files truncated over 4 GiB"`, `_require_test`, `_require_fs_space $TEST_DIR $((5 * 1024 * 1024)) #kB`.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 37: echo "Could not create 5G test file"`
- Key operational lines include:
- `line 42: block_size=`stat -c '%B' $junk_file``
- `line 43: iblocks_after_truncate=`stat -c '%b' $junk_file``

## State and Persistence Behavior

Uses the configured xfstests test area or an explicitly created loop/image mount rather than always reformatting the scratch device. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto`, common helper libraries (`./common/preamble`, `./common/filter`), and the golden-output file `sources/test-tools/xfstests/tests/generic/701.out` (2 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_fixed_by_fs_commit exfat 92fba084b79e "exfat: fix i_blocks for files truncated over 4 GiB"`, `_require_test`, `_require_fs_space $TEST_DIR $((5 * 1024 * 1024)) #kB`.

## Risks and Edge Cases

- Most failures should surface as unexpected output, nonzero helper status, or harness `_fail`/`_notrun` behavior.

## Test Signals

The paired `.out` file has 2 line(s); its first visible signals are: 'QA output created by 701; Number of allocated blocks after truncate is in range'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/701 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/702 -->
# sources/test-tools/xfstests/tests/generic/702

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/702`. Test that if we have two consecutive extents and only one of them is cloned, then fiemap correctly reports which one is shared and reports the other as not shared. It is registered with `_begin_fstest auto quick clone fiemap`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 91 source line(s).
- Harness registration: `_begin_fstest auto quick clone fiemap`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/reflink`.
- Capability and skip gates: `_fixed_by_fs_commit btrfs ac3c0d36a2a2f7 "btrfs: make fiemap more efficient and accurate reporting extent sharedness"`, `_require_scratch_reflink`, `_require_xfs_io_command "fiemap"`, `_require_congruent_file_oplen $SCRATCH_MNT $((128 * 1024))`.
- Local shell functions: `fiemap_test_file`.
- External `$here/src` helpers: none visible.

## Control Flow

- Capability gating runs first through `_fixed_by_fs_commit btrfs ac3c0d36a2a2f7 "btrfs: make fiemap more efficient and accurate reporting extent sharedness"`, `_require_scratch_reflink`, `_require_xfs_io_command "fiemap"`, `_require_congruent_file_oplen $SCRATCH_MNT $((128 * 1024))`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- User-visible phase markers include:
- `line 55: echo "Creating file foo"`
- `line 61: echo "Cloning first extent of file foo to file bar"`
- `line 67: echo "fiemap of file foo:"`
- `line 74: echo "Creating file foo2"`
- `line 80: echo "Cloning second extent of file foo2 to file bar2"`
- `line 86: echo "fiemap of file foo2:"`
- Key operational lines include:
- `line 20: _require_scratch_reflink`
- `line 43: $XFS_IO_PROG -c "fiemap -v" $filepath | tail -n +3 | \`
- `line 48: _scratch_mkfs >> $seqres.full`
- `line 49: _scratch_mount`
- `line 56: $XFS_IO_PROG -f -c "pwrite -b 128K 0 128K" -c "fsync" \`
- `line 62: $XFS_IO_PROG -f -c "reflink $SCRATCH_MNT/foo 0 0 128K" $SCRATCH_MNT/bar | \`
- `line 75: $XFS_IO_PROG -f -c "pwrite -b 128K 0 128K" -c "fsync" \`
- `line 81: $XFS_IO_PROG -f -c "reflink $SCRATCH_MNT/foo2 128K 0 128K" $SCRATCH_MNT/bar2 | \`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Shared extent or atomic-update state is exercised, so correctness depends on clone/dedupe/exchange persistence and metadata ordering. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick clone fiemap`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/reflink`), and the golden-output file `sources/test-tools/xfstests/tests/generic/702.out` (23 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_fixed_by_fs_commit btrfs ac3c0d36a2a2f7 "btrfs: make fiemap more efficient and accurate reporting extent sharedness"`, `_require_scratch_reflink`, `_require_xfs_io_command "fiemap"`, `_require_congruent_file_oplen $SCRATCH_MNT $((128 * 1024))`.

## Risks and Edge Cases

- Shared-extent and exchange operations can expose stale data, permission-bit, or log-ordering bugs that only appear after remount/recovery.

## Test Signals

The paired `.out` file has 23 line(s); its first visible signals are: 'QA output created by 702; Creating file foo; wrote 131072/131072 bytes at offset 0; XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec); wrote 131072/131072 bytes at offset 131072'. Runtime pass/fail is primarily the command exit status plus golden-output comparison. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/702 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/703 -->
# sources/test-tools/xfstests/tests/generic/703

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/703`. Test that direct IO writes with io_uring and O_DSYNC are durable if a power failure happens after they complete. It is registered with `_begin_fstest auto quick log prealloc io_uring`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 101 source line(s).
- Harness registration: `_begin_fstest auto quick log prealloc io_uring`.
- Imported common libraries: `./common/preamble`, `./common/dmflakey`.
- Capability and skip gates: `_fixed_by_fs_commit btrfs 8184620ae212 "btrfs: fix lost file sync on direct IO write with nowait and dsync iocb"`, `_require_scratch_size $((512 * 1024))`, `_require_odirect`, `_require_io_uring`, `_require_dm_target flakey`, `_require_xfs_io_command "falloc"`, `_require_fio $fio_config`, `_require_metadata_journaling $SCRATCH_DEV`, `_require_congruent_file_oplen $SCRATCH_MNT $((64 * 1024))`, `_require_chattr C`.
- Local shell functions: `_cleanup`.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `fio_config=$tmp.fio`
- `fio_out=$tmp.fio.out`
- `test_file="${SCRATCH_MNT}/foo"`
- `ioengine=io_uring`
- `direct=1`
- `bs=64K`
- `sync=1`
- `filename=$test_file`
- `rw=randwrite`
- `runtime=10`
- `digest_before=$(_md5_checksum $test_file)`
- `digest_after=$(_md5_checksum $test_file)`

## Control Flow

- Capability gating runs first through `_fixed_by_fs_commit btrfs 8184620ae212 "btrfs: fix lost file sync on direct IO write with nowait and dsync iocb"`, `_require_scratch_size $((512 * 1024))`, `_require_odirect`, `_require_io_uring`, `_require_dm_target flakey`, plus 5 more.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- User-visible phase markers include:
- `line 74: echo -e "Running fio with config:\n" >> $seqres.full`
- `line 79: echo -e "\nOutput from fio:\n" >> $seqres.full`
- `line 91: echo "Error: not all file data got persisted."`
- `line 92: echo "Digest before power failure: $digest_before"`
- `line 93: echo "Digest after power failure: $digest_after"`
- `line 99: echo "Silence is golden"`
- Key operational lines include:
- `line 15: _cleanup_flakey`
- `line 22: fio_config=$tmp.fio`
- `line 23: fio_out=$tmp.fio.out`
- `line 32: _require_scratch_size $((512 * 1024))`
- `line 36: _require_xfs_io_command "falloc"`
- `line 38: cat >$fio_config <<EOF`
- `line 50: _require_fio $fio_config`
- `line 52: _scratch_mkfs >>$seqres.full 2>&1`
- `line 54: _init_flakey`
- `line 55: _scratch_mount`
- `line 69: $XFS_IO_PROG -c "falloc 0 256M" $test_file`
- `line 72: _scratch_sync`
- `line 74: echo -e "Running fio with config:\n" >> $seqres.full`
- `line 75: cat $fio_config >> $seqres.full`
- `line 77: $FIO_PROG $fio_config --output=$fio_out`
- `line 79: echo -e "\nOutput from fio:\n" >> $seqres.full`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Synthetic block-device state can be introduced through device-mapper, loop, SCSI debug, or huge-device helpers and must be cleaned even on failure. Extended attributes are part of the persistent state being created, replayed, or verified. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick log prealloc io_uring`, common helper libraries (`./common/preamble`, `./common/dmflakey`), and the golden-output file `sources/test-tools/xfstests/tests/generic/703.out` (2 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_fixed_by_fs_commit btrfs 8184620ae212 "btrfs: fix lost file sync on direct IO write with nowait and dsync iocb"`, `_require_scratch_size $((512 * 1024))`, `_require_odirect`, `_require_io_uring`, `_require_dm_target flakey`, `_require_xfs_io_command "falloc"`, `_require_fio $fio_config`, `_require_metadata_journaling $SCRATCH_DEV`, plus 2 more.

## Risks and Edge Cases

- Direct/AIO coverage depends on alignment, device logical block size, page size, and filesystem direct-I/O semantics.
- Failure-injection paths can leave mounts or synthetic device tables behind if cleanup is interrupted.

## Test Signals

The paired `.out` file has 2 line(s); its first visible signals are: 'QA output created by 703; Silence is golden'. Runtime pass/fail is also signaled by post-remount or failure-injection persistence checks. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/703 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/704 -->
# sources/test-tools/xfstests/tests/generic/704

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/704`. Make sure logical-sector sized O_DIRECT write is allowed It is registered with `_begin_fstest auto quick`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 53 source line(s).
- Harness registration: `_begin_fstest auto quick`.
- Imported common libraries: `./common/preamble`, `./common/scsi_debug`.
- Capability and skip gates: `_fixed_by_fs_commit xfs 7c71ee78031c "xfs: allow logical-sector sized O_DIRECT"`, `_require_scsi_debug`, `_require_test`, `_require_block_device $TEST_DEV`.
- Local shell functions: `_cleanup`.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `size=$(_small_fs_size_mb 256)`
- `SCSI_DEBUG_DEV=`_get_scsi_debug_dev 4096 512 0 $size``
- `SCSI_DEBUG_MNT="$TEST_DIR/scsi_debug_$seq"`

## Control Flow

- Capability gating runs first through `_fixed_by_fs_commit xfs 7c71ee78031c "xfs: allow logical-sector sized O_DIRECT"`, `_require_scsi_debug`, `_require_test`, `_require_block_device $TEST_DEV`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- User-visible phase markers include:
- `line 34: echo "Get a device with 4096 physical sector size and 512 logical sector size"`
- `line 38: echo "mkfs and mount"`
- `line 45: echo "DIO read/write 512 bytes"`
- Key operational lines include:
- `line 17: [ -d "$SCSI_DEBUG_MNT" ] && _unmount $SCSI_DEBUG_MNT 2>/dev/null`
- `line 39: _mkfs_dev $SCSI_DEBUG_DEV || _fail "Can't make $FSTYP on scsi_debug device"`
- `line 43: run_check _mount $SCSI_DEBUG_DEV $SCSI_DEBUG_MNT`
- `line 48: $XFS_IO_PROG -d -f -c "pwrite 0 512" $SCSI_DEBUG_MNT/testfile >> $seqres.full`
- `line 49: $XFS_IO_PROG -d -c "pread 0 512" $SCSI_DEBUG_MNT/testfile >> $seqres.full`

## State and Persistence Behavior

Uses the configured xfstests test area or an explicitly created loop/image mount rather than always reformatting the scratch device. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Synthetic block-device state can be introduced through device-mapper, loop, SCSI debug, or huge-device helpers and must be cleaned even on failure. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick`, common helper libraries (`./common/preamble`, `./common/scsi_debug`), and the golden-output file `sources/test-tools/xfstests/tests/generic/704.out` (6 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_fixed_by_fs_commit xfs 7c71ee78031c "xfs: allow logical-sector sized O_DIRECT"`, `_require_scsi_debug`, `_require_test`, `_require_block_device $TEST_DEV`.

## Risks and Edge Cases

- Direct/AIO coverage depends on alignment, device logical block size, page size, and filesystem direct-I/O semantics.
- Failure-injection paths can leave mounts or synthetic device tables behind if cleanup is interrupted.

## Test Signals

The paired `.out` file has 6 line(s); its first visible signals are: 'QA output created by 704; Get a device with 4096 physical sector size and 512 logical sector size; 4096; 512; mkfs and mount'. Runtime pass/fail is also signaled by hang/race detection through background work, loops, or timeout windows. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/704 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/705 -->
# sources/test-tools/xfstests/tests/generic/705

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/705`. Test an issue in the truncate codepath where on-disk inode sizes are logged prematurely via the free eofblocks path on file close. It is registered with `_begin_fstest auto shutdown`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 44 source line(s).
- Harness registration: `_begin_fstest auto shutdown`.
- Imported common libraries: `./common/preamble`.
- Capability and skip gates: `_require_scratch`, `_require_scratch_shutdown`, `_require_metadata_journaling`, `_require_command "$FILEFRAG_PROG" filefrag`.
- Local shell functions: none visible.
- External `$here/src` helpers: none visible.

## Control Flow

- Capability gating runs first through `_require_scratch`, `_require_scratch_shutdown`, `_require_metadata_journaling`, `_require_command "$FILEFRAG_PROG" filefrag`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- User-visible phase markers include:
- `line 20: echo "Create many small files with one extent at least"`
- `line 25: echo "Shutdown the fs suddently"`
- `line 28: echo "Cycle mount"`
- `line 31: echo "Check file's (di_size > 0) extents"`
- `line 36: echo " - $f get no extents, but its di_size > 0"`
- Key operational lines include:
- `line 14: _require_scratch_shutdown`
- `line 17: _scratch_mkfs > $seqres.full 2>&1`
- `line 18: _scratch_mount`
- `line 22: $XFS_IO_PROG -f -c "pwrite 0 4k" $SCRATCH_MNT/file.$i >/dev/null 2>&1`
- `line 26: _scratch_shutdown`
- `line 29: _scratch_cycle_mount`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto shutdown`, common helper libraries (`./common/preamble`), and the golden-output file `sources/test-tools/xfstests/tests/generic/705.out` (5 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_scratch`, `_require_scratch_shutdown`, `_require_metadata_journaling`, `_require_command "$FILEFRAG_PROG" filefrag`.

## Risks and Edge Cases

- Failure-injection paths can leave mounts or synthetic device tables behind if cleanup is interrupted.

## Test Signals

The paired `.out` file has 5 line(s); its first visible signals are: "QA output created by 705; Create many small files with one extent at least; Shutdown the fs suddently; Cycle mount; Check file's (di_size > 0) extents". Runtime pass/fail is also signaled by post-remount or failure-injection persistence checks. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/705 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/706 -->
# sources/test-tools/xfstests/tests/generic/706

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/706`. Test that seeking for data on a 1 byte file works correctly, the returned offset should be 0 if the start offset is 0. It is registered with `_begin_fstest auto quick seek`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 34 source line(s).
- Harness registration: `_begin_fstest auto quick seek`.
- Imported common libraries: `./common/preamble`.
- Capability and skip gates: `_fixed_by_fs_commit btrfs 2f2e84ca6066 "btrfs: fix off-by-one in delalloc search during lseek"`, `_require_test`, `_require_seek_data_hole`, `_require_test_program "seek_sanity_test"`.
- Local shell functions: `_cleanup`.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `test_file=$TEST_DIR/seek_sanity_testfile.$seq`

## Control Flow

- Capability gating runs first through `_fixed_by_fs_commit btrfs 2f2e84ca6066 "btrfs: fix off-by-one in delalloc search during lseek"`, `_require_test`, `_require_seek_data_hole`, `_require_test_program "seek_sanity_test"`.
- User-visible phase markers include:
- `line 32: echo "Silence is golden"`

## State and Persistence Behavior

Uses the configured xfstests test area or an explicitly created loop/image mount rather than always reformatting the scratch device. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick seek`, common helper libraries (`./common/preamble`), and the golden-output file `sources/test-tools/xfstests/tests/generic/706.out` (2 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_fixed_by_fs_commit btrfs 2f2e84ca6066 "btrfs: fix off-by-one in delalloc search during lseek"`, `_require_test`, `_require_seek_data_hole`, `_require_test_program "seek_sanity_test"`.

## Risks and Edge Cases

- Most failures should surface as unexpected output, nonzero helper status, or harness `_fail`/`_notrun` behavior.

## Test Signals

The paired `.out` file has 2 line(s); its first visible signals are: 'QA output created by 706; Silence is golden'. Runtime pass/fail is primarily the command exit status plus golden-output comparison. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/706 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/707 -->
# sources/test-tools/xfstests/tests/generic/707

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/707`. This is a test verifying whether the filesystem can gracefully handle modifying of a directory while it is being moved, in particular the cases where directory format changes It is registered with `_begin_fstest auto`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 70 source line(s).
- Harness registration: `_begin_fstest auto`.
- Imported common libraries: `./common/preamble`.
- Capability and skip gates: `_require_scratch`, `_fixed_by_fs_commit udf f950fd052913 "udf: Protect rename against modification of moved directory"`.
- Local shell functions: `_cleanup`, `create_files`.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `loops=$((100*TIME_FACTOR))`
- `files=500`
- `moves=500`
- `start_dir=$PWD`
- `BGPID=$!`

## Control Flow

- Capability gating runs first through `_require_scratch`, `_fixed_by_fs_commit udf f950fd052913 "udf: Protect rename against modification of moved directory"`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- User-visible phase markers include:
- `line 45: echo -n > somewhatlongerfilename$i`
- `line 68: echo "Silence is golden"`
- Key operational lines include:
- `line 21: _scratch_mkfs >>$seqres.full 2>&1`
- `line 22: _scratch_mount`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto`, common helper libraries (`./common/preamble`), and the golden-output file `sources/test-tools/xfstests/tests/generic/707.out` (2 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_scratch`, `_fixed_by_fs_commit udf f950fd052913 "udf: Protect rename against modification of moved directory"`.

## Risks and Edge Cases

- Directory mutation and rename races depend on dentry-cache timing and may need repeated attempts to expose regressions.

## Test Signals

The paired `.out` file has 2 line(s); its first visible signals are: 'QA output created by 707; Silence is golden'. Runtime pass/fail is primarily the command exit status plus golden-output comparison. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/707 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/708 -->
# sources/test-tools/xfstests/tests/generic/708

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/708`. Test iomap direct_io partial writes. Create a reasonably large file, then run a program which mmaps it, touches the first page, then dio writes it to a second file. This can result in a page fault reading from the mmapped dio write buffer and thus the iomap direct_io partial write codepath. It is registered with `_begin_fstest quick auto mmap`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 36 source line(s).
- Harness registration: `_begin_fstest quick auto mmap`.
- Imported common libraries: `./common/preamble`.
- Capability and skip gates: `_fixed_by_fs_commit btrfs b73a6fd1b1ef "btrfs: split partial dio bios before submit"`, `_require_test`, `_require_odirect`, `_require_test_program dio-buf-fault`.
- Local shell functions: none visible.
- External `$here/src` helpers: `$here/src/dio-buf-fault $src $dst > /dev/null || _fail "failed doing the dio copy"`.
- Notable variables and constants:
- `src=$TEST_DIR/dio-buf-fault-$seq.src`
- `dst=$TEST_DIR/dio-buf-fault-$seq.dst`

## Control Flow

- Capability gating runs first through `_fixed_by_fs_commit btrfs b73a6fd1b1ef "btrfs: split partial dio bios before submit"`, `_require_test`, `_require_odirect`, `_require_test_program dio-buf-fault`.
- User-visible phase markers include:
- `line 28: echo "Silence is golden"`
- Key operational lines include:
- `line 15: _begin_fstest quick auto mmap`
- `line 30: $XFS_IO_PROG -fc "pwrite -q -S 0xcd 0 $((2 * 1024 * 1024))" $src`

## State and Persistence Behavior

Uses the configured xfstests test area or an explicitly created loop/image mount rather than always reformatting the scratch device. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest quick auto mmap`, common helper libraries (`./common/preamble`), and the golden-output file `sources/test-tools/xfstests/tests/generic/708.out` (2 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_fixed_by_fs_commit btrfs b73a6fd1b1ef "btrfs: split partial dio bios before submit"`, `_require_test`, `_require_odirect`, `_require_test_program dio-buf-fault`.

## Risks and Edge Cases

- Direct/AIO coverage depends on alignment, device logical block size, page size, and filesystem direct-I/O semantics.
- mmap/page-fault regressions are often race-prone and may manifest as hangs rather than clean command failures.

## Test Signals

The paired `.out` file has 2 line(s); its first visible signals are: 'QA output created by 708; Silence is golden'. Runtime pass/fail is primarily the command exit status plus golden-output comparison. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/708 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/709 -->
# sources/test-tools/xfstests/tests/generic/709

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/709`. Can we use exchangerange to make the quota accounting incorrect? It is registered with `_begin_fstest auto quick fiexchange quota`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 54 source line(s).
- Harness registration: `_begin_fstest auto quick fiexchange quota`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/quota`.
- Capability and skip gates: `_require_xfs_io_command exchangerange`, `_require_user`, `_require_nobody`, `_require_quota`, `_require_xfs_quota`, `_require_scratch`.
- Local shell functions: none visible.
- External `$here/src` helpers: none visible.

## Control Flow

- Capability gating runs first through `_require_xfs_io_command exchangerange`, `_require_user`, `_require_nobody`, `_require_quota`, `_require_xfs_quota`, plus 1 more.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 34: echo before exchangerange >> $seqres.full`
- `line 46: echo after exchangerange >> $seqres.full`
- Key operational lines include:
- `line 16: _require_xfs_io_command exchangerange`
- `line 24: _scratch_mkfs > $seqres.full`
- `line 29: $XFS_IO_PROG -f -c 'pwrite -S 0x58 0 256k -b 1m' $SCRATCH_MNT/a >> $seqres.full`
- `line 31: $XFS_IO_PROG -f -c 'pwrite -S 0x59 0 64k -b 64k' -c 'truncate 256k' $SCRATCH_MNT/b >> $seqres.full`
- `line 34: echo before exchangerange >> $seqres.full`
- `line 36: stat $SCRATCH_MNT/* >> $seqres.full`
- `line 42: $XFS_IO_PROG -c "exchangerange $SCRATCH_MNT/b" $SCRATCH_MNT/a &> $tmp.swap`
- `line 46: echo after exchangerange >> $seqres.full`
- `line 48: stat $SCRATCH_MNT/* >> $seqres.full`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Shared extent or atomic-update state is exercised, so correctness depends on clone/dedupe/exchange persistence and metadata ordering. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick fiexchange quota`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/quota`), and the golden-output file `sources/test-tools/xfstests/tests/generic/709.out` (3 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_xfs_io_command exchangerange`, `_require_user`, `_require_nobody`, `_require_quota`, `_require_xfs_quota`, `_require_scratch`.

## Risks and Edge Cases

- Shared-extent and exchange operations can expose stale data, permission-bit, or log-ordering bugs that only appear after remount/recovery.

## Test Signals

The paired `.out` file has 3 line(s); its first visible signals are: 'QA output created by 709; Comparing user usage; Comparing group usage'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands, hang/race detection through background work, loops, or timeout windows. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/709 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/710 -->
# sources/test-tools/xfstests/tests/generic/710

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/710`. Can we use exchangerange to exceed the quota enforcement? It is registered with `_begin_fstest auto quick fiexchange quota`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 54 source line(s).
- Harness registration: `_begin_fstest auto quick fiexchange quota`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/quota`.
- Capability and skip gates: `_require_xfs_io_command exchangerange`, `_require_user`, `_require_nobody`, `_require_quota`, `_require_xfs_quota`, `_require_scratch`.
- Local shell functions: none visible.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `extra_limits="rtbhard=70k"`

## Control Flow

- Capability gating runs first through `_require_xfs_io_command exchangerange`, `_require_user`, `_require_nobody`, `_require_quota`, `_require_xfs_quota`, plus 1 more.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 39: echo before exchangerange >> $seqres.full`
- `line 46: echo after exchangerange >> $seqres.full`
- Key operational lines include:
- `line 16: _require_xfs_io_command exchangerange`
- `line 24: _scratch_mkfs > $seqres.full`
- `line 29: $XFS_IO_PROG -f -c 'pwrite -S 0x58 0 256k -b 1m' $SCRATCH_MNT/a >> $seqres.full`
- `line 31: $XFS_IO_PROG -f -c 'pwrite -S 0x59 0 64k -b 64k' -c 'truncate 256k' $SCRATCH_MNT/b >> $seqres.full`
- `line 35: _scratch_supports_rtquota && \`
- `line 39: echo before exchangerange >> $seqres.full`
- `line 41: stat $SCRATCH_MNT/* >> $seqres.full`
- `line 44: $XFS_IO_PROG -c "exchangerange $SCRATCH_MNT/b" $SCRATCH_MNT/a`
- `line 46: echo after exchangerange >> $seqres.full`
- `line 48: stat $SCRATCH_MNT/* >> $seqres.full`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Shared extent or atomic-update state is exercised, so correctness depends on clone/dedupe/exchange persistence and metadata ordering. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick fiexchange quota`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/quota`), and the golden-output file `sources/test-tools/xfstests/tests/generic/710.out` (4 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_xfs_io_command exchangerange`, `_require_user`, `_require_nobody`, `_require_quota`, `_require_xfs_quota`, `_require_scratch`.

## Risks and Edge Cases

- Shared-extent and exchange operations can expose stale data, permission-bit, or log-ordering bugs that only appear after remount/recovery.

## Test Signals

The paired `.out` file has 4 line(s); its first visible signals are: 'QA output created by 710; exchangerange: Disk quota exceeded; Comparing user usage; Comparing group usage'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands, hang/race detection through background work, loops, or timeout windows. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/710 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/711 -->
# sources/test-tools/xfstests/tests/generic/711

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/711`. Make sure that swapext won't touch a swap file. It is registered with `_begin_fstest auto quick swapext`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 46 source line(s).
- Harness registration: `_begin_fstest auto quick swapext`.
- Imported common libraries: `./common/preamble`, `./common/filter`.
- Capability and skip gates: `_require_xfs_io_command swapext`, `_require_test`.
- Local shell functions: `_cleanup`.
- External `$here/src` helpers: `$here/src/punch-alternating $dir/a`.
- Notable variables and constants:
- `dir=$TEST_DIR/test-$seq`

## Control Flow

- Capability gating runs first through `_require_xfs_io_command swapext`, `_require_test`.
- Key operational lines include:
- `line 30: $XFS_IO_PROG -f -c 'pwrite -S 0x58 0 32m -b 1m' -c fsync $dir/a >> $seqres.full`
- `line 32: $XFS_IO_PROG -f -c 'pwrite -S 0x58 0 32m -b 1m' -c fsync $dir/a >> $seqres.full`
- `line 35: $XFS_IO_PROG -f -c 'pwrite -S 0x59 0 32m -b 1m' $dir/b >> $seqres.full`
- `line 41: $XFS_IO_PROG -c "swapext $dir/b" $dir/a 2>&1 | \`

## State and Persistence Behavior

Uses the configured xfstests test area or an explicitly created loop/image mount rather than always reformatting the scratch device. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick swapext`, common helper libraries (`./common/preamble`, `./common/filter`), and the golden-output file `sources/test-tools/xfstests/tests/generic/711.out` (2 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_xfs_io_command swapext`, `_require_test`.

## Risks and Edge Cases

- Most failures should surface as unexpected output, nonzero helper status, or harness `_fail`/`_notrun` behavior.

## Test Signals

The paired `.out` file has 2 line(s); its first visible signals are: 'QA output created by 711; swapext: Text file busy'. Runtime pass/fail is primarily the command exit status plus golden-output comparison. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/711 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/712 -->
# sources/test-tools/xfstests/tests/generic/712

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/712`. Make sure that exchangerange modifies ctime and not mtime of the file. It is registered with `_begin_fstest auto quick fiexchange`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 57 source line(s).
- Harness registration: `_begin_fstest auto quick fiexchange`.
- Imported common libraries: `./common/preamble`, `./common/filter`.
- Capability and skip gates: `_require_test_program punch-alternating`, `_require_xfs_io_command exchangerange`, `_require_test`.
- Local shell functions: `_cleanup`.
- External `$here/src` helpers: `$here/src/punch-alternating $dir/a`.
- Notable variables and constants:
- `dir=$TEST_DIR/test-$seq`
- `old_mtime="$(echo $(stat -c '%y' $dir/a $dir/b))"`
- `old_ctime="$(echo $(stat -c '%z' $dir/a $dir/b))"`
- `new_mtime="$(echo $(stat -c '%y' $dir/a $dir/b))"`
- `new_ctime="$(echo $(stat -c '%z' $dir/a $dir/b))"`

## Control Flow

- Capability gating runs first through `_require_test_program punch-alternating`, `_require_xfs_io_command exchangerange`, `_require_test`.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 35: echo before >> $seqres.full`
- `line 45: echo after >> $seqres.full`
- `line 55: echo Silence is golden.`
- Key operational lines include:
- `line 23: _require_xfs_io_command exchangerange`
- `line 30: $XFS_IO_PROG -f -c 'pwrite -S 0x58 0 256k -b 1m' $dir/a >> $seqres.full`
- `line 32: $XFS_IO_PROG -f -c 'pwrite -S 0x59 0 256k -b 1m' $dir/b >> $seqres.full`
- `line 36: md5sum $dir/a $dir/b >> $seqres.full`
- `line 37: old_mtime="$(echo $(stat -c '%y' $dir/a $dir/b))"`
- `line 38: old_ctime="$(echo $(stat -c '%z' $dir/a $dir/b))"`
- `line 39: stat -c '%y %Y %z %Z' $dir/a $dir/b >> $seqres.full`
- `line 42: $XFS_IO_PROG -c "exchangerange $dir/b" $dir/a`
- `line 46: md5sum $dir/a $dir/b >> $seqres.full`
- `line 47: new_mtime="$(echo $(stat -c '%y' $dir/a $dir/b))"`
- `line 48: new_ctime="$(echo $(stat -c '%z' $dir/a $dir/b))"`
- `line 49: stat -c '%y %Y %z %Z' $dir/a $dir/b >> $seqres.full`

## State and Persistence Behavior

Uses the configured xfstests test area or an explicitly created loop/image mount rather than always reformatting the scratch device. Shared extent or atomic-update state is exercised, so correctness depends on clone/dedupe/exchange persistence and metadata ordering. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick fiexchange`, common helper libraries (`./common/preamble`, `./common/filter`), and the golden-output file `sources/test-tools/xfstests/tests/generic/712.out` (2 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_test_program punch-alternating`, `_require_xfs_io_command exchangerange`, `_require_test`.

## Risks and Edge Cases

- Shared-extent and exchange operations can expose stale data, permission-bit, or log-ordering bugs that only appear after remount/recovery.

## Test Signals

The paired `.out` file has 2 line(s); its first visible signals are: 'QA output created by 712; Silence is golden.'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/712 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/713 -->
# sources/test-tools/xfstests/tests/generic/713

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/713`. Test exchangerange between ranges of two different files. It is registered with `_begin_fstest auto quick fiexchange`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 99 source line(s).
- Harness registration: `_begin_fstest auto quick fiexchange`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/reflink`.
- Capability and skip gates: `_require_xfs_io_command exchangerange ' -s 64k -l 64k'`, `_require_xfs_io_command "falloc"`, `_require_test`, `_require_congruent_file_oplen $TEST_DIR $blksz`.
- Local shell functions: `_cleanup`, `filesnap`, `test_exchangerange_once`, `test_exchangerange_two`.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `dir=$TEST_DIR/test-$seq`
- `blksz=65536`
- `nrblks=57`

## Control Flow

- Capability gating runs first through `_require_xfs_io_command exchangerange ' -s 64k -l 64k'`, `_require_xfs_io_command "falloc"`, `_require_test`, `_require_congruent_file_oplen $TEST_DIR $blksz`.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 28: echo "$1"`
- `line 42: echo`
- Key operational lines include:
- `line 23: _require_xfs_io_command exchangerange ' -s 64k -l 64k'`
- `line 24: _require_xfs_io_command "falloc"`
- `line 30: md5sum $2 $3 | _filter_test_dir`
- `line 32: md5sum $2 | _filter_test_dir`
- `line 36: test_exchangerange_once() {`
- `line 37: filesnap "$1: before exchangerange" $dir/$3 $dir/$4`
- `line 38: $XFS_IO_PROG -c "exchangerange $2 $dir/$3" $dir/$4`
- `line 39: filesnap "$1: after exchangerange" $dir/$3 $dir/$4`
- `line 45: test_exchangerange_two() {`
- `line 47: test_exchangerange_once "$*: samerange" \`
- `line 51: test_exchangerange_once "$*: diffrange" \`
- `line 55: test_exchangerange_once "$*: overlap" \`
- `line 69: test_exchangerange_two "simple"`
- `line 75: test_exchangerange_once "unalignedeof" "" a b`
- `line 81: test_exchangerange_two "rainbow"`
- `line 85: $XFS_IO_PROG -f -c "pwrite -S 0x58 0 $((blksz * nrblks))" \`

## State and Persistence Behavior

Uses the configured xfstests test area or an explicitly created loop/image mount rather than always reformatting the scratch device. Shared extent or atomic-update state is exercised, so correctness depends on clone/dedupe/exchange persistence and metadata ordering. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick fiexchange`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/reflink`), and the golden-output file `sources/test-tools/xfstests/tests/generic/713.out` (86 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_xfs_io_command exchangerange ' -s 64k -l 64k'`, `_require_xfs_io_command "falloc"`, `_require_test`, `_require_congruent_file_oplen $TEST_DIR $blksz`.

## Risks and Edge Cases

- Shared-extent and exchange operations can expose stale data, permission-bit, or log-ordering bugs that only appear after remount/recovery.

## Test Signals

The paired `.out` file has 86 line(s); its first visible signals are: 'QA output created by 713; simple: samerange: before exchangerange; db85d578204631f2b4eb1e73974253c2  TEST_DIR/test-713/b; d0425612f15c6071022cf7127620f63d  TEST_DIR/test-713/a; simple: samerange: after exchangerange'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands, xfstests output filters. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/713 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/714 -->
# sources/test-tools/xfstests/tests/generic/714

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/714`. Test exchangerange between ranges of two different files, when one of the files is shared. It is registered with `_begin_fstest auto quick fiexchange`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 115 source line(s).
- Harness registration: `_begin_fstest auto quick fiexchange`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/reflink`.
- Capability and skip gates: `_require_xfs_io_command exchangerange`, `_require_xfs_io_command "falloc"`, `_require_test_reflink`, `_require_congruent_file_oplen $TEST_DIR $blksz`.
- Local shell functions: `_cleanup`, `filesnap`, `test_exchangerange_once`, `test_exchangerange_two`.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `dir=$TEST_DIR/test-$seq`
- `blksz=65536`
- `nrblks=57`

## Control Flow

- Capability gating runs first through `_require_xfs_io_command exchangerange`, `_require_xfs_io_command "falloc"`, `_require_test_reflink`, `_require_congruent_file_oplen $TEST_DIR $blksz`.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 29: echo "$1"`
- `line 43: echo`
- `line 60: echo "overwrite A and B entirely"`
- `line 67: echo`
- `line 106: echo "overwrite C entirely"`
- Key operational lines include:
- `line 24: _require_xfs_io_command exchangerange`
- `line 25: _require_xfs_io_command "falloc"`
- `line 26: _require_test_reflink`
- `line 31: md5sum $2 $3 | _filter_test_dir`
- `line 33: md5sum $2 | _filter_test_dir`
- `line 37: test_exchangerange_once() {`
- `line 38: filesnap "$1: before exchangerange" $dir/$3 $dir/$4`
- `line 39: $XFS_IO_PROG -c "exchangerange $2 $dir/$3" $dir/$4`
- `line 40: filesnap "$1: after exchangerange" $dir/$3 $dir/$4`
- `line 46: test_exchangerange_two() {`
- `line 48: test_exchangerange_once "$*: samerange" \`
- `line 52: test_exchangerange_once "$*: diffrange" \`
- `line 56: test_exchangerange_once "$*: overlap" \`
- `line 61: md5sum $dir/sharea | _filter_test_dir`
- `line 62: $XFS_IO_PROG -c "pwrite -S 0x60 0 $((blksz * nrblks))" $dir/a >> $seqres.full`
- `line 63: $XFS_IO_PROG -c "pwrite -S 0x60 0 $((blksz * nrblks))" $dir/b >> $seqres.full`

## State and Persistence Behavior

Uses the configured xfstests test area or an explicitly created loop/image mount rather than always reformatting the scratch device. Shared extent or atomic-update state is exercised, so correctness depends on clone/dedupe/exchange persistence and metadata ordering. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick fiexchange`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/reflink`), and the golden-output file `sources/test-tools/xfstests/tests/generic/714.out` (90 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_xfs_io_command exchangerange`, `_require_xfs_io_command "falloc"`, `_require_test_reflink`, `_require_congruent_file_oplen $TEST_DIR $blksz`.

## Risks and Edge Cases

- Shared-extent and exchange operations can expose stale data, permission-bit, or log-ordering bugs that only appear after remount/recovery.

## Test Signals

The paired `.out` file has 90 line(s); its first visible signals are: 'QA output created by 714; simple: samerange: before exchangerange; db85d578204631f2b4eb1e73974253c2  TEST_DIR/test-714/b; d0425612f15c6071022cf7127620f63d  TEST_DIR/test-714/a; simple: samerange: after exchangerange'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands, xfstests output filters. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/714 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/715 -->
# sources/test-tools/xfstests/tests/generic/715

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/715`. Test exchangerange between two files of unlike size. It is registered with `_begin_fstest auto quick fiexchange`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 77 source line(s).
- Harness registration: `_begin_fstest auto quick fiexchange`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/reflink`.
- Capability and skip gates: `_require_xfs_io_command exchangerange ' -s 64k -l 64k'`, `_require_test`.
- Local shell functions: `_cleanup`, `filesnap`, `test_exchangerange_once`.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `len=""`
- `len="-l $((blksz * len))"`
- `cmd="exchangerange -s $((blksz * a_off)) -d $((blksz * b_off)) $len $dir/a"`
- `dir=$TEST_DIR/test-$seq`
- `blksz=65536`

## Control Flow

- Capability gating runs first through `_require_xfs_io_command exchangerange ' -s 64k -l 64k'`, `_require_test`.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 27: echo "$1"`
- `line 56: echo "$cmd" >> $seqres.full`
- `line 62: echo`
- Key operational lines include:
- `line 23: _require_xfs_io_command exchangerange ' -s 64k -l 64k'`
- `line 29: md5sum $2 $3 | _filter_test_dir`
- `line 31: md5sum $2 | _filter_test_dir`
- `line 35: test_exchangerange_once() {`
- `line 53: filesnap "$tag: before exchangerange" $dir/a $dir/b`
- `line 55: cmd="exchangerange -s $((blksz * a_off)) -d $((blksz * b_off)) $len $dir/a"`
- `line 57: $XFS_IO_PROG -c "$cmd" $dir/b`
- `line 58: filesnap "$tag: after exchangerange" $dir/a $dir/b`
- `line 69: test_exchangerange_once "last 5 blocks" 27 37 22 32 5`
- `line 71: test_exchangerange_once "whole file to eof" 27 37 0 0 EOF`
- `line 73: test_exchangerange_once "blocks 30-40" 27 37 30 30 10`

## State and Persistence Behavior

Uses the configured xfstests test area or an explicitly created loop/image mount rather than always reformatting the scratch device. Shared extent or atomic-update state is exercised, so correctness depends on clone/dedupe/exchange persistence and metadata ordering. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick fiexchange`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/reflink`), and the golden-output file `sources/test-tools/xfstests/tests/generic/715.out` (32 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_xfs_io_command exchangerange ' -s 64k -l 64k'`, `_require_test`.

## Risks and Edge Cases

- Shared-extent and exchange operations can expose stale data, permission-bit, or log-ordering bugs that only appear after remount/recovery.

## Test Signals

The paired `.out` file has 32 line(s); its first visible signals are: 'QA output created by 715; last 5 blocks: before exchangerange; 207ea56e0ccbf50d38fd3a2d842aa170  TEST_DIR/test-715/a; eb58941d31f5be1e4e22df8c536dd490  TEST_DIR/test-715/b; last 5 blocks: after exchangerange'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands, xfstests output filters. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/715 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/716 -->
# sources/test-tools/xfstests/tests/generic/716

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/716`. Test atomic file updates when (a) the length is the same; (b) the length is different; and (c) someone modifies the original file and we need to cancel the update. The file contents are cloned into the staging file, and some of the contents are updated. It is registered with `_begin_fstest auto quick fiexchange`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 121 source line(s).
- Harness registration: `_begin_fstest auto quick fiexchange`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/reflink`.
- Capability and skip gates: `_require_xfs_io_command exchangerange`, `_require_xfs_io_command startupdate`, `_require_test_reflink`, `_require_test`.
- Local shell functions: `_cleanup`, `filesnap`, `mkfile`.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `dir=$TEST_DIR/test-$seq`
- `blksz=65536`
- `nrblks=64`

## Control Flow

- Capability gating runs first through `_require_xfs_io_command exchangerange`, `_require_xfs_io_command startupdate`, `_require_test_reflink`, `_require_test`.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 32: echo "$1"`
- `line 58: echo`
- `line 72: echo`
- `line 85: echo`
- `line 99: echo`
- `line 117: echo`
- Key operational lines include:
- `line 26: _require_xfs_io_command exchangerange`
- `line 27: _require_xfs_io_command startupdate`
- `line 28: _require_test_reflink`
- `line 33: md5sum $2 | _filter_test_dir`
- `line 51: $XFS_IO_PROG \`
- `line 52: -c 'startupdate' \`
- `line 54: -c 'commitupdate -q' \`
- `line 64: $XFS_IO_PROG \`
- `line 65: -c 'startupdate' \`
- `line 68: -c 'commitupdate -q' \`
- `line 78: $XFS_IO_PROG \`
- `line 79: -c 'startupdate' \`
- `line 81: -c 'commitupdate -q' \`
- `line 92: $XFS_IO_PROG \`
- `line 93: -c 'startupdate' \`
- `line 95: -c 'cancelupdate' \`

## State and Persistence Behavior

Uses the configured xfstests test area or an explicitly created loop/image mount rather than always reformatting the scratch device. Shared extent or atomic-update state is exercised, so correctness depends on clone/dedupe/exchange persistence and metadata ordering. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick fiexchange`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/reflink`), and the golden-output file `sources/test-tools/xfstests/tests/generic/716.out` (48 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_xfs_io_command exchangerange`, `_require_xfs_io_command startupdate`, `_require_test_reflink`, `_require_test`.

## Risks and Edge Cases

- Shared-extent and exchange operations can expose stale data, permission-bit, or log-ordering bugs that only appear after remount/recovery.

## Test Signals

The paired `.out` file has 48 line(s); its first visible signals are: 'QA output created by 716; before commit; d712f003e9d467e063cda1baf319b928  TEST_DIR/test-716/a; wrote 56320/56320 bytes at offset 45056; XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec)'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands, xfstests output filters. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/716 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/717 -->
# sources/test-tools/xfstests/tests/generic/717

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/717`. Try invalid parameters to see if they fail. It is registered with `_begin_fstest auto quick fiexchange`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 95 source line(s).
- Harness registration: `_begin_fstest auto quick fiexchange`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/reflink`.
- Capability and skip gates: `_require_xfs_io_command exchangerange`, `_require_xfs_io_command startupdate`, `_require_test`, `_require_scratch`, `_require_chattr i`.
- Local shell functions: `_cleanup`.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `dir=$TEST_DIR/test-$seq`
- `blksz=65536`
- `nrblks=64`

## Control Flow

- Capability gating runs first through `_require_xfs_io_command exchangerange`, `_require_xfs_io_command startupdate`, `_require_test`, `_require_scratch`, `_require_chattr i`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- User-visible phase markers include:
- `line 40: echo Immutable files`
- `line 44: echo Readonly files`
- `line 47: echo Directories`
- `line 50: echo Unaligned ranges`
- `line 53: echo file1 range entirely beyond EOF`
- `line 56: echo file2 range entirely beyond EOF`
- `line 59: echo Both ranges entirely beyond EOF`
- `line 62: echo file1 range crossing EOF`
- Key operational lines include:
- `line 23: _require_xfs_io_command exchangerange`
- `line 24: _require_xfs_io_command startupdate`
- `line 34: _scratch_mkfs >> $seqres.full`
- `line 35: _scratch_mount`
- `line 41: $XFS_IO_PROG -c 'chattr +i' -c "exchangerange $dir/b" $dir/a`
- `line 45: $XFS_IO_PROG -r -c "exchangerange $dir/b" $dir/a`
- `line 48: $XFS_IO_PROG -c "exchangerange $dir/b" $dir`
- `line 51: $XFS_IO_PROG -c "exchangerange -s 37 -d 61 -l 17 $dir/b" $dir/a`
- `line 54: $XFS_IO_PROG -c "exchangerange -s $(( blksz * (nrblks + 500) )) -d 0 -l $blksz $dir/b" $dir/a`
- `line 57: $XFS_IO_PROG -c "exchangerange -d $(( blksz * (nrblks + 500) )) -s 0 -l $blksz $dir/b" $dir/a`
- `line 60: $XFS_IO_PROG -c "exchangerange -d $(( blksz * (nrblks + 500) )) -s $(( blksz * (nrblks + 500) )) -l $blksz $dir/b" $dir/a`
- `line 63: $XFS_IO_PROG -c "exchangerange -s $(( blksz * (nrblks - 1) )) -d 0 -l $((2 * blksz)) $dir/b" $dir/a`
- `line 66: $XFS_IO_PROG -c "exchangerange -d $(( blksz * (nrblks - 1) )) -s 0 -l $((2 * blksz)) $dir/b" $dir/a`
- `line 69: $XFS_IO_PROG -c "exchangerange -d $(( blksz * (nrblks - 1) )) -s $(( blksz * (nrblks - 1) )) -l $((blksz * 2)) $dir/b" $dir/a`
- `line 74: $XFS_IO_PROG -c "exchangerange -d 0 -s $(( blksz * nrblks )) -l 37 $dir/b" $dir/a`
- `line 77: $XFS_IO_PROG -c "exchangerange -s 0 -d $(( blksz * nrblks )) -l 37 $dir/b" $dir/a`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Extended attributes are part of the persistent state being created, replayed, or verified. Shared extent or atomic-update state is exercised, so correctness depends on clone/dedupe/exchange persistence and metadata ordering. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick fiexchange`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/reflink`), and the golden-output file `sources/test-tools/xfstests/tests/generic/717.out` (31 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_xfs_io_command exchangerange`, `_require_xfs_io_command startupdate`, `_require_test`, `_require_scratch`, `_require_chattr i`.

## Risks and Edge Cases

- Shared-extent and exchange operations can expose stale data, permission-bit, or log-ordering bugs that only appear after remount/recovery.

## Test Signals

The paired `.out` file has 31 line(s); its first visible signals are: 'QA output created by 717; Immutable files; exchangerange: Operation not permitted; Readonly files; exchangerange: Bad file descriptor'. Runtime pass/fail is primarily the command exit status plus golden-output comparison. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/717 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/718 -->
# sources/test-tools/xfstests/tests/generic/718

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/718`. Make sure exchangerange honors RLIMIT_FSIZE. It is registered with `_begin_fstest auto quick fiexchange`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 47 source line(s).
- Harness registration: `_begin_fstest auto quick fiexchange`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/reflink`.
- Capability and skip gates: `_require_xfs_io_command exchangerange`, `_require_test`.
- Local shell functions: `_cleanup`.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `dir=$TEST_DIR/test-$seq`
- `blksz=65536`
- `nrblks=64`

## Control Flow

- Capability gating runs first through `_require_xfs_io_command exchangerange`, `_require_test`.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- Key operational lines include:
- `line 23: _require_xfs_io_command exchangerange`
- `line 35: md5sum $dir/a $dir/b | _filter_test_dir`
- `line 42: $XFS_IO_PROG -c "exchangerange $dir/b" $dir/a`
- `line 43: md5sum $dir/a $dir/b | _filter_test_dir`

## State and Persistence Behavior

Uses the configured xfstests test area or an explicitly created loop/image mount rather than always reformatting the scratch device. Shared extent or atomic-update state is exercised, so correctness depends on clone/dedupe/exchange persistence and metadata ordering. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick fiexchange`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/reflink`), and the golden-output file `sources/test-tools/xfstests/tests/generic/718.out` (6 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_xfs_io_command exchangerange`, `_require_test`.

## Risks and Edge Cases

- Shared-extent and exchange operations can expose stale data, permission-bit, or log-ordering bugs that only appear after remount/recovery.

## Test Signals

The paired `.out` file has 6 line(s); its first visible signals are: 'QA output created by 718; d712f003e9d467e063cda1baf319b928  TEST_DIR/test-718/a; 901e136269b8d283d311697b7c6dc1f2  TEST_DIR/test-718/b; exchangerange: Invalid argument; d712f003e9d467e063cda1baf319b928  TEST_DIR/test-718/a'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands, xfstests output filters. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/718 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/719 -->
# sources/test-tools/xfstests/tests/generic/719

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/719`. Test atomic file replacement when (a) the length is the same; (b) the length is different; and (c) someone modifies the original file and we need to cancel the update. The staging file is created empty, which implies that the caller wants a full file replacement. It is registered with `_begin_fstest auto quick fiexchange`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 104 source line(s).
- Harness registration: `_begin_fstest auto quick fiexchange`.
- Imported common libraries: `./common/preamble`, `./common/filter`.
- Capability and skip gates: `_require_xfs_io_command exchangerange`, `_require_xfs_io_command startupdate '-e'`, `_require_test`.
- Local shell functions: `_cleanup`, `filesnap`, `mkfile`.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `dir=$TEST_DIR/test-$seq`
- `blksz=65536`
- `nrblks=64`

## Control Flow

- Capability gating runs first through `_require_xfs_io_command exchangerange`, `_require_xfs_io_command startupdate '-e'`, `_require_test`.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 30: echo "$1"`
- `line 56: echo`
- `line 69: echo`
- `line 82: echo`
- `line 100: echo`
- Key operational lines include:
- `line 25: _require_xfs_io_command exchangerange`
- `line 26: _require_xfs_io_command startupdate '-e'`
- `line 31: md5sum $2 | _filter_test_dir`
- `line 49: $XFS_IO_PROG \`
- `line 50: -c 'startupdate -e' \`
- `line 52: -c 'commitupdate -q' \`
- `line 62: $XFS_IO_PROG \`
- `line 63: -c 'startupdate -e' \`
- `line 65: -c 'commitupdate -q' \`
- `line 75: $XFS_IO_PROG \`
- `line 76: -c 'startupdate -e' \`
- `line 78: -c 'commitupdate -q' \`
- `line 89: $XFS_IO_PROG \`
- `line 91: -c 'startupdate -e ' \`
- `line 96: -c 'commitupdate -q' \`

## State and Persistence Behavior

Uses the configured xfstests test area or an explicitly created loop/image mount rather than always reformatting the scratch device. Shared extent or atomic-update state is exercised, so correctness depends on clone/dedupe/exchange persistence and metadata ordering. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick fiexchange`, common helper libraries (`./common/preamble`, `./common/filter`), and the golden-output file `sources/test-tools/xfstests/tests/generic/719.out` (40 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_xfs_io_command exchangerange`, `_require_xfs_io_command startupdate '-e'`, `_require_test`.

## Risks and Edge Cases

- Shared-extent and exchange operations can expose stale data, permission-bit, or log-ordering bugs that only appear after remount/recovery.

## Test Signals

The paired `.out` file has 40 line(s); its first visible signals are: 'QA output created by 719; before commit; d712f003e9d467e063cda1baf319b928  TEST_DIR/test-719/a; wrote 4194304/4194304 bytes at offset 0; XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec)'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands, xfstests output filters. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/719 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/720 -->
# sources/test-tools/xfstests/tests/generic/720

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/720`. Stress testing with a lot of extents. It is registered with `_begin_fstest auto quick fiexchange`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 57 source line(s).
- Harness registration: `_begin_fstest auto quick fiexchange`.
- Imported common libraries: `./common/preamble`, `./common/filter`.
- Capability and skip gates: `_require_xfs_io_command exchangerange`, `_require_test_program punch-alternating`, `_require_test`, `_require_fs_space $TEST_DIR $(( (2 * blksz * nrblks) / 1024 ))`.
- Local shell functions: `_cleanup`.
- External `$here/src` helpers: `$here/src/punch-alternating $dir/a`, `$here/src/punch-alternating -o 1 $dir/b`.
- Notable variables and constants:
- `dir=$TEST_DIR/test-$seq`
- `blksz=$(_get_file_block_size $TEST_DIR)`
- `nrblks=$((LOAD_FACTOR * 100000))`
- `md5_a="$(md5sum < $dir/a)"`
- `md5_b="$(md5sum < $dir/b)"`

## Control Flow

- Capability gating runs first through `_require_xfs_io_command exchangerange`, `_require_test_program punch-alternating`, `_require_test`, `_require_fs_space $TEST_DIR $(( (2 * blksz * nrblks) / 1024 ))`.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 47: echo "md5_a=$md5_a" >> $seqres.full`
- `line 48: echo "md5_b=$md5_b" >> $seqres.full`
- `line 54: echo "Silence is golden!"`
- Key operational lines include:
- `line 22: _require_xfs_io_command exchangerange`
- `line 41: md5_a="$(md5sum < $dir/a)"`
- `line 42: md5_b="$(md5sum < $dir/b)"`
- `line 44: $XFS_IO_PROG -c "exchangerange $dir/b" $dir/a`
- `line 49: md5sum $dir/a $dir/b >> $seqres.full`
- `line 51: test "$(md5sum < $dir/b)" = "$md5_a" || echo "file b does not match former a"`
- `line 52: test "$(md5sum < $dir/a)" = "$md5_b" || echo "file a does not match former b"`

## State and Persistence Behavior

Uses the configured xfstests test area or an explicitly created loop/image mount rather than always reformatting the scratch device. Shared extent or atomic-update state is exercised, so correctness depends on clone/dedupe/exchange persistence and metadata ordering. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick fiexchange`, common helper libraries (`./common/preamble`, `./common/filter`), and the golden-output file `sources/test-tools/xfstests/tests/generic/720.out` (2 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_xfs_io_command exchangerange`, `_require_test_program punch-alternating`, `_require_test`, `_require_fs_space $TEST_DIR $(( (2 * blksz * nrblks) / 1024 ))`.

## Risks and Edge Cases

- Shared-extent and exchange operations can expose stale data, permission-bit, or log-ordering bugs that only appear after remount/recovery.

## Test Signals

The paired `.out` file has 2 line(s); its first visible signals are: 'QA output created by 720; Silence is golden!'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/720 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/721 -->
# sources/test-tools/xfstests/tests/generic/721

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/721`. Test non-root atomic file updates when (a) the file contents are cloned into the staging file; and (b) when the staging file is created empty. It is registered with `_begin_fstest auto quick fiexchange`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 125 source line(s).
- Harness registration: `_begin_fstest auto quick fiexchange`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/reflink`.
- Capability and skip gates: `_require_xfs_io_command startupdate`, `_require_test_reflink`, `_require_test`, `_require_user`.
- Local shell functions: `_cleanup`, `filesnap`, `mkfile`.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `dir=$TEST_DIR/test-$seq`
- `blksz=65536`
- `nrblks=64`
- `cmd="$XFS_IO_PROG \`
- `cmd="$XFS_IO_PROG \`
- `cmd="$XFS_IO_PROG \`
- `cmd="$XFS_IO_PROG \`
- `cmd="$XFS_IO_PROG \`

## Control Flow

- Capability gating runs first through `_require_xfs_io_command startupdate`, `_require_test_reflink`, `_require_test`, `_require_user`.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 30: echo "$1"`
- `line 58: echo`
- `line 73: echo`
- `line 87: echo`
- `line 102: echo`
- `line 121: echo`
- Key operational lines include:
- `line 24: _require_xfs_io_command startupdate`
- `line 25: _require_test_reflink`
- `line 31: md5sum $2 | _filter_test_dir`
- `line 50: cmd="$XFS_IO_PROG \`
- `line 51: -c 'startupdate' \`
- `line 53: -c 'commitupdate -q' \`
- `line 64: cmd="$XFS_IO_PROG \`
- `line 65: -c 'startupdate' \`
- `line 68: -c 'commitupdate -q' \`
- `line 79: cmd="$XFS_IO_PROG \`
- `line 80: -c 'startupdate' \`
- `line 82: -c 'commitupdate -q' \`
- `line 94: cmd="$XFS_IO_PROG \`
- `line 95: -c 'startupdate' \`
- `line 97: -c 'cancelupdate' \`
- `line 109: cmd="$XFS_IO_PROG \`

## State and Persistence Behavior

Uses the configured xfstests test area or an explicitly created loop/image mount rather than always reformatting the scratch device. Shared extent or atomic-update state is exercised, so correctness depends on clone/dedupe/exchange persistence and metadata ordering. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick fiexchange`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/reflink`), and the golden-output file `sources/test-tools/xfstests/tests/generic/721.out` (48 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_xfs_io_command startupdate`, `_require_test_reflink`, `_require_test`, `_require_user`.

## Risks and Edge Cases

- Shared-extent and exchange operations can expose stale data, permission-bit, or log-ordering bugs that only appear after remount/recovery.

## Test Signals

The paired `.out` file has 48 line(s); its first visible signals are: 'QA output created by 721; before commit; d712f003e9d467e063cda1baf319b928  TEST_DIR/test-721/a; wrote 56320/56320 bytes at offset 45056; XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec)'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands, xfstests output filters. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/721 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/722 -->
# sources/test-tools/xfstests/tests/generic/722

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/722`. Test exchangerange with the fsync flag flushes everything to disk before the call returns. It is registered with `_begin_fstest auto quick fiexchange`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 56 source line(s).
- Harness registration: `_begin_fstest auto quick fiexchange`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/reflink`.
- Capability and skip gates: `_require_test_program "punch-alternating"`, `_require_xfs_io_command exchangerange`, `_require_scratch`, `_require_scratch_shutdown`, `_require_metadata_journaling`.
- Local shell functions: none visible.
- External `$here/src` helpers: `$here/src/punch-alternating $SCRATCH_MNT/a`, `$here/src/punch-alternating $SCRATCH_MNT/b`.
- Notable variables and constants:
- `old_a=$(md5sum $SCRATCH_MNT/a | awk '{print $1}')`
- `old_b=$(md5sum $SCRATCH_MNT/b | awk '{print $1}')`
- `new_a=$(md5sum $SCRATCH_MNT/a | awk '{print $1}')`
- `new_b=$(md5sum $SCRATCH_MNT/b | awk '{print $1}')`

## Control Flow

- Capability gating runs first through `_require_test_program "punch-alternating"`, `_require_xfs_io_command exchangerange`, `_require_scratch`, `_require_scratch_shutdown`, `_require_metadata_journaling`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 33: echo "md5 a: $old_a md5 b: $old_b" >> $seqres.full`
- `line 38: echo swap >> $seqres.full`
- `line 45: echo "md5 a: $new_a md5 b: $new_b" >> $seqres.full`
- `line 54: echo Silence is golden`
- Key operational lines include:
- `line 18: _require_xfs_io_command exchangerange`
- `line 20: _require_scratch_shutdown`
- `line 23: _scratch_mkfs >> $seqres.full`
- `line 24: _scratch_mount`
- `line 31: old_a=$(md5sum $SCRATCH_MNT/a | awk '{print $1}')`
- `line 32: old_b=$(md5sum $SCRATCH_MNT/b | awk '{print $1}')`
- `line 39: $XFS_IO_PROG -c "exchangerange -f $SCRATCH_MNT/a" $SCRATCH_MNT/b`
- `line 40: _scratch_shutdown`
- `line 41: _scratch_cycle_mount`
- `line 43: new_a=$(md5sum $SCRATCH_MNT/a | awk '{print $1}')`
- `line 44: new_b=$(md5sum $SCRATCH_MNT/b | awk '{print $1}')`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Shared extent or atomic-update state is exercised, so correctness depends on clone/dedupe/exchange persistence and metadata ordering. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick fiexchange`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/reflink`), and the golden-output file `sources/test-tools/xfstests/tests/generic/722.out` (2 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_test_program "punch-alternating"`, `_require_xfs_io_command exchangerange`, `_require_scratch`, `_require_scratch_shutdown`, `_require_metadata_journaling`.

## Risks and Edge Cases

- Failure-injection paths can leave mounts or synthetic device tables behind if cleanup is interrupted.
- Shared-extent and exchange operations can expose stale data, permission-bit, or log-ordering bugs that only appear after remount/recovery.

## Test Signals

The paired `.out` file has 2 line(s); its first visible signals are: 'QA output created by 722; Silence is golden'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands, post-remount or failure-injection persistence checks. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/722 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/723 -->
# sources/test-tools/xfstests/tests/generic/723

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/723`. Test exchangerange with the dry run flag doesn't change anything. It is registered with `_begin_fstest auto quick fiexchange`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 69 source line(s).
- Harness registration: `_begin_fstest auto quick fiexchange`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/reflink`.
- Capability and skip gates: `_require_test_program "punch-alternating"`, `_require_xfs_io_command exchangerange`, `_require_scratch`.
- Local shell functions: `_cleanup`.
- External `$here/src` helpers: `$here/src/punch-alternating $SCRATCH_MNT/a`, `$here/src/punch-alternating $SCRATCH_MNT/b`.
- Notable variables and constants:
- `old_a=$(md5sum $SCRATCH_MNT/a | awk '{print $1}')`
- `old_b=$(md5sum $SCRATCH_MNT/b | awk '{print $1}')`
- `new_a=$(md5sum $SCRATCH_MNT/a | awk '{print $1}')`
- `new_b=$(md5sum $SCRATCH_MNT/b | awk '{print $1}')`
- `new_a=$(md5sum $SCRATCH_MNT/a | awk '{print $1}')`
- `new_b=$(md5sum $SCRATCH_MNT/b | awk '{print $1}')`

## Control Flow

- Capability gating runs first through `_require_test_program "punch-alternating"`, `_require_xfs_io_command exchangerange`, `_require_scratch`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 38: echo "md5 a: $old_a md5 b: $old_b" >> $seqres.full`
- `line 42: echo dry run swap >> $seqres.full`
- `line 48: echo "md5 a: $new_a md5 b: $new_b" >> $seqres.full`
- `line 55: echo actual swap >> $seqres.full`
- `line 61: echo "md5 a: $new_a md5 b: $new_b" >> $seqres.full`
- `line 67: echo Silence is golden`
- Key operational lines include:
- `line 24: _require_xfs_io_command exchangerange`
- `line 27: _scratch_mkfs >> $seqres.full`
- `line 28: _scratch_mount`
- `line 32: $XFS_IO_PROG -c 'truncate 2m' $SCRATCH_MNT/a`
- `line 36: old_a=$(md5sum $SCRATCH_MNT/a | awk '{print $1}')`
- `line 37: old_b=$(md5sum $SCRATCH_MNT/b | awk '{print $1}')`
- `line 43: $XFS_IO_PROG -c "exchangerange -n -f $SCRATCH_MNT/a" $SCRATCH_MNT/b`
- `line 44: _scratch_cycle_mount`
- `line 46: new_a=$(md5sum $SCRATCH_MNT/a | awk '{print $1}')`
- `line 47: new_b=$(md5sum $SCRATCH_MNT/b | awk '{print $1}')`
- `line 56: $XFS_IO_PROG -c "exchangerange -f $SCRATCH_MNT/a" $SCRATCH_MNT/b`
- `line 57: _scratch_cycle_mount`
- `line 59: new_a=$(md5sum $SCRATCH_MNT/a | awk '{print $1}')`
- `line 60: new_b=$(md5sum $SCRATCH_MNT/b | awk '{print $1}')`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Shared extent or atomic-update state is exercised, so correctness depends on clone/dedupe/exchange persistence and metadata ordering. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick fiexchange`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/reflink`), and the golden-output file `sources/test-tools/xfstests/tests/generic/723.out` (2 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_test_program "punch-alternating"`, `_require_xfs_io_command exchangerange`, `_require_scratch`.

## Risks and Edge Cases

- Shared-extent and exchange operations can expose stale data, permission-bit, or log-ordering bugs that only appear after remount/recovery.

## Test Signals

The paired `.out` file has 2 line(s); its first visible signals are: 'QA output created by 723; Silence is golden'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands, post-remount or failure-injection persistence checks. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/723 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/724 -->
# sources/test-tools/xfstests/tests/generic/724

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/724`. Test scatter-gather atomic file writes. We create a temporary file, write sparsely to it, then use XFS_EXCHANGE_RANGE_FILE1_WRITTEN flag to swap atomicallly only the ranges that we wrote. It is registered with `_begin_fstest auto quick fiexchange`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 52 source line(s).
- Harness registration: `_begin_fstest auto quick fiexchange`.
- Imported common libraries: `./common/preamble`, `./common/filter`.
- Capability and skip gates: `_require_xfs_io_command exchangerange`, `_require_scratch`, `_require_congruent_file_oplen $SCRATCH_MNT 65536`.
- Local shell functions: `_cleanup`.
- External `$here/src` helpers: none visible.

## Control Flow

- Capability gating runs first through `_require_xfs_io_command exchangerange`, `_require_scratch`, `_require_congruent_file_oplen $SCRATCH_MNT 65536`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 43: echo swap | tee -a $seqres.full`
- Key operational lines include:
- `line 24: _require_xfs_io_command exchangerange`
- `line 27: _scratch_mkfs >> $seqres.full`
- `line 28: _scratch_mount`
- `line 35: $XFS_IO_PROG -f -c 'truncate 1m' $SCRATCH_MNT/b`
- `line 39: md5sum $SCRATCH_MNT/a | _filter_scratch`
- `line 40: md5sum $SCRATCH_MNT/b | _filter_scratch`
- `line 44: $XFS_IO_PROG -c "exchangerange -f -w $SCRATCH_MNT/b" $SCRATCH_MNT/a`
- `line 45: _scratch_cycle_mount`
- `line 47: md5sum $SCRATCH_MNT/a | _filter_scratch`
- `line 48: md5sum $SCRATCH_MNT/b | _filter_scratch`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Shared extent or atomic-update state is exercised, so correctness depends on clone/dedupe/exchange persistence and metadata ordering. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick fiexchange`, common helper libraries (`./common/preamble`, `./common/filter`), and the golden-output file `sources/test-tools/xfstests/tests/generic/724.out` (6 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_xfs_io_command exchangerange`, `_require_scratch`, `_require_congruent_file_oplen $SCRATCH_MNT 65536`.

## Risks and Edge Cases

- Shared-extent and exchange operations can expose stale data, permission-bit, or log-ordering bugs that only appear after remount/recovery.

## Test Signals

The paired `.out` file has 6 line(s); its first visible signals are: 'QA output created by 724; 310f146ce52077fcd3308dcbe7632bb2  SCRATCH_MNT/a; c9fb827e2e3e579dc2a733ddad486d1d  SCRATCH_MNT/b; swap; e9cbfe8489a68efaa5fcf40cf3106118  SCRATCH_MNT/a'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands, xfstests output filters, post-remount or failure-injection persistence checks. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/724 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/725 -->
# sources/test-tools/xfstests/tests/generic/725

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/725`. Test scatter-gather atomic file commits. Use the startupdate command to create a temporary file, write sparsely to it, then commitupdate -h to perform the scattered update. It is registered with `_begin_fstest auto quick fiexchange`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 55 source line(s).
- Harness registration: `_begin_fstest auto quick fiexchange`.
- Imported common libraries: `./common/preamble`, `./common/filter`.
- Capability and skip gates: `_require_xfs_io_command exchangerange`, `_require_xfs_io_command startupdate '-e'`, `_require_scratch`, `_require_congruent_file_oplen $SCRATCH_MNT 65536`.
- Local shell functions: `_cleanup`.
- External `$here/src` helpers: none visible.

## Control Flow

- Capability gating runs first through `_require_xfs_io_command exchangerange`, `_require_xfs_io_command startupdate '-e'`, `_require_scratch`, `_require_congruent_file_oplen $SCRATCH_MNT 65536`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 38: echo commit | tee -a $seqres.full`
- Key operational lines include:
- `line 24: _require_xfs_io_command exchangerange`
- `line 25: _require_xfs_io_command startupdate '-e'`
- `line 28: _scratch_mkfs >> $seqres.full`
- `line 29: _scratch_mount`
- `line 34: _scratch_sync`
- `line 35: md5sum $SCRATCH_MNT/a | _filter_scratch`
- `line 39: $XFS_IO_PROG \`
- `line 41: -c 'startupdate -e' \`
- `line 46: -c 'commitupdate -h -k' \`
- `line 49: _scratch_cycle_mount`
- `line 51: md5sum $SCRATCH_MNT/a | _filter_scratch`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Shared extent or atomic-update state is exercised, so correctness depends on clone/dedupe/exchange persistence and metadata ordering. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick fiexchange`, common helper libraries (`./common/preamble`, `./common/filter`), and the golden-output file `sources/test-tools/xfstests/tests/generic/725.out` (4 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_xfs_io_command exchangerange`, `_require_xfs_io_command startupdate '-e'`, `_require_scratch`, `_require_congruent_file_oplen $SCRATCH_MNT 65536`.

## Risks and Edge Cases

- Shared-extent and exchange operations can expose stale data, permission-bit, or log-ordering bugs that only appear after remount/recovery.

## Test Signals

The paired `.out` file has 4 line(s); its first visible signals are: 'QA output created by 725; 310f146ce52077fcd3308dcbe7632bb2  SCRATCH_MNT/a; commit; e9cbfe8489a68efaa5fcf40cf3106118  SCRATCH_MNT/a'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands, xfstests output filters, post-remount or failure-injection persistence checks. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/725 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/726 -->
# sources/test-tools/xfstests/tests/generic/726

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/726`. Functional test for dropping suid and sgid bits as part of an atomic file commit. It is registered with `_begin_fstest auto fiexchange quick`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 113 source line(s).
- Harness registration: `_begin_fstest auto fiexchange quick`.
- Imported common libraries: `./common/preamble`, `./common/filter`.
- Capability and skip gates: `_require_user`, `_require_xfs_io_command exchangerange`, `_require_xfs_io_command startupdate`, `_require_scratch`, `_require_congruent_file_oplen $SCRATCH_MNT 1048576`.
- Local shell functions: `setup_testfile`, `commit_and_check`.
- External `$here/src` helpers: none visible.

## Control Flow

- Capability gating runs first through `_require_user`, `_require_xfs_io_command exchangerange`, `_require_xfs_io_command startupdate`, `_require_scratch`, `_require_congruent_file_oplen $SCRATCH_MNT 1048576`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 59: echo`
- `line 64: echo "Test 1 - qa_user, non-exec file"`
- `line 70: echo "Test 2 - qa_user, group-exec file"`
- `line 76: echo "Test 3 - qa_user, user-exec file"`
- `line 82: echo "Test 4 - qa_user, all-exec file"`
- `line 88: echo "Test 5 - root, non-exec file"`
- `line 94: echo "Test 6 - root, group-exec file"`
- `line 100: echo "Test 7 - root, user-exec file"`
- Key operational lines include:
- `line 26: _require_xfs_io_command exchangerange`
- `line 27: _require_xfs_io_command startupdate`
- `line 30: _scratch_mkfs >> $seqres.full`
- `line 31: _scratch_mount`
- `line 38: _scratch_sync`
- `line 44: md5sum $SCRATCH_MNT/a | _filter_scratch`
- `line 45: stat -c '%a %A %n' $SCRATCH_MNT/a | _filter_scratch`
- `line 47: local cmd="$XFS_IO_PROG -c 'startupdate' -c 'pwrite -S 0x57 0 1m' -c 'commitupdate' $SCRATCH_MNT/a"`
- `line 54: _scratch_cycle_mount`
- `line 55: md5sum $SCRATCH_MNT/a | _filter_scratch`
- `line 56: stat -c '%a %A %n' $SCRATCH_MNT/a | _filter_scratch`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Shared extent or atomic-update state is exercised, so correctness depends on clone/dedupe/exchange persistence and metadata ordering. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto fiexchange quick`, common helper libraries (`./common/preamble`, `./common/filter`), and the golden-output file `sources/test-tools/xfstests/tests/generic/726.out` (49 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_user`, `_require_xfs_io_command exchangerange`, `_require_xfs_io_command startupdate`, `_require_scratch`, `_require_congruent_file_oplen $SCRATCH_MNT 1048576`.

## Risks and Edge Cases

- Shared-extent and exchange operations can expose stale data, permission-bit, or log-ordering bugs that only appear after remount/recovery.

## Test Signals

The paired `.out` file has 49 line(s); its first visible signals are: 'QA output created by 726; Test 1 - qa_user, non-exec file; 310f146ce52077fcd3308dcbe7632bb2  SCRATCH_MNT/a; 6666 -rwSrwSrw- SCRATCH_MNT/a; 3784de23efab7a2074c9ec66901e39e5  SCRATCH_MNT/a'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands, xfstests output filters, post-remount or failure-injection persistence checks. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/726 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/727 -->
# sources/test-tools/xfstests/tests/generic/727

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/727`. Functional test for dropping capability bits as part of an atomic file commit. It is registered with `_begin_fstest auto fiexchange quick`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 83 source line(s).
- Harness registration: `_begin_fstest auto fiexchange quick`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/attr`.
- Capability and skip gates: `_require_user`, `_require_command "$GETCAP_PROG" getcap`, `_require_command "$SETCAP_PROG" setcap`, `_require_xfs_io_command exchangerange`, `_require_xfs_io_command startupdate`, `_require_scratch`, `_require_attrs security`, `_require_congruent_file_oplen $SCRATCH_MNT 1048576`.
- Local shell functions: `setup_testfile`, `commit_and_check`.
- External `$here/src` helpers: none visible.

## Control Flow

- Capability gating runs first through `_require_user`, `_require_command "$GETCAP_PROG" getcap`, `_require_command "$SETCAP_PROG" setcap`, `_require_xfs_io_command exchangerange`, `_require_xfs_io_command startupdate`, plus 3 more.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 68: echo`
- `line 72: echo "Test 1 - qa_user"`
- `line 77: echo "Test 2 - root"`
- Key operational lines include:
- `line 29: _require_xfs_io_command exchangerange`
- `line 30: _require_xfs_io_command startupdate`
- `line 34: _scratch_mkfs >> $seqres.full`
- `line 35: _scratch_mount`
- `line 45: _scratch_sync`
- `line 51: md5sum $SCRATCH_MNT/a | _filter_scratch`
- `line 52: stat -c '%a %A %n' $SCRATCH_MNT/a | _filter_scratch`
- `line 55: local cmd="$XFS_IO_PROG -c 'startupdate' -c 'pwrite -S 0x57 0 1m' -c 'commitupdate' $SCRATCH_MNT/a"`
- `line 62: _scratch_cycle_mount`
- `line 63: md5sum $SCRATCH_MNT/a | _filter_scratch`
- `line 64: stat -c '%a %A %n' $SCRATCH_MNT/a | _filter_scratch`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Extended attributes are part of the persistent state being created, replayed, or verified. Shared extent or atomic-update state is exercised, so correctness depends on clone/dedupe/exchange persistence and metadata ordering. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto fiexchange quick`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/attr`), and the golden-output file `sources/test-tools/xfstests/tests/generic/727.out` (17 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_user`, `_require_command "$GETCAP_PROG" getcap`, `_require_command "$SETCAP_PROG" setcap`, `_require_xfs_io_command exchangerange`, `_require_xfs_io_command startupdate`, `_require_scratch`, `_require_attrs security`, `_require_congruent_file_oplen $SCRATCH_MNT 1048576`.

## Risks and Edge Cases

- Shared-extent and exchange operations can expose stale data, permission-bit, or log-ordering bugs that only appear after remount/recovery.

## Test Signals

The paired `.out` file has 17 line(s); its first visible signals are: 'QA output created by 727; Test 1 - qa_user; 310f146ce52077fcd3308dcbe7632bb2  SCRATCH_MNT/a; 666 -rw-rw-rw- SCRATCH_MNT/a; SCRATCH_MNT/a cap_setgid,cap_setuid=ep'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands, xfstests output filters, post-remount or failure-injection persistence checks. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/727 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/728 -->
# sources/test-tools/xfstests/tests/generic/728

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/728`. Test a bug where the NFS client wasn't sending a post-op GETATTR to the server after setting an xattr, resulting in `stat` reporting a stale ctime. It is registered with `_begin_fstest auto quick attr`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 41 source line(s).
- Harness registration: `_begin_fstest auto quick attr`.
- Imported common libraries: `./common/preamble`, `./common/attr`.
- Capability and skip gates: `_require_test`, `_require_attrs`.
- Local shell functions: `check_xattr_op`.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `what=$1`
- `before_ctime=$(stat -c %z $TEST_DIR/testfile)`
- `after_ctime=$(stat -c %z $TEST_DIR/testfile)`

## Control Flow

- Capability gating runs first through `_require_test`, `_require_attrs`.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 39: echo "Silence is golden"`
- Key operational lines include:
- `line 27: before_ctime=$(stat -c %z $TEST_DIR/testfile)`
- `line 31: after_ctime=$(stat -c %z $TEST_DIR/testfile)`

## State and Persistence Behavior

Uses the configured xfstests test area or an explicitly created loop/image mount rather than always reformatting the scratch device. Extended attributes are part of the persistent state being created, replayed, or verified. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick attr`, common helper libraries (`./common/preamble`, `./common/attr`), and the golden-output file `sources/test-tools/xfstests/tests/generic/728.out` (2 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_test`, `_require_attrs`.

## Risks and Edge Cases

- Most failures should surface as unexpected output, nonzero helper status, or harness `_fail`/`_notrun` behavior.

## Test Signals

The paired `.out` file has 2 line(s); its first visible signals are: 'QA output created by 728; Silence is golden'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/728 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/729 -->
# sources/test-tools/xfstests/tests/generic/729

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/729`. Trigger page faults in the same file during read and write This is generic/647 with an additional test that writes a memory-mapped page onto itself using direct I/O. The kernel will invalidate the page cache before carrying out the write, so filesystems that fault in the page and then carry out the direct I/O write with page faults disabled will never make any progress. It is registered with `_begin_fstest auto quick mmap`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 40 source line(s).
- Harness registration: `_begin_fstest auto quick mmap`.
- Imported common libraries: `./common/preamble`, `./common/filter`.
- Capability and skip gates: `_require_test`, `_require_odirect`, `_require_test_program mmap-rw-fault`.
- Local shell functions: `_cleanup`.
- External `$here/src` helpers: `$here/src/mmap-rw-fault -2 $TEST_DIR/mmap-rw-fault.tmp`.

## Control Flow

- Capability gating runs first through `_require_test`, `_require_odirect`, `_require_test_program mmap-rw-fault`.
- User-visible phase markers include:
- `line 35: echo "Silence is golden"`
- Key operational lines include:
- `line 17: _begin_fstest auto quick mmap`
- `line 24: rm -f $TEST_DIR/mmap-rw-fault.tmp`
- `line 33: _require_test_program mmap-rw-fault`
- `line 37: $here/src/mmap-rw-fault -2 $TEST_DIR/mmap-rw-fault.tmp`

## State and Persistence Behavior

Uses the configured xfstests test area or an explicitly created loop/image mount rather than always reformatting the scratch device. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick mmap`, common helper libraries (`./common/preamble`, `./common/filter`), and the golden-output file `sources/test-tools/xfstests/tests/generic/729.out` (2 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_test`, `_require_odirect`, `_require_test_program mmap-rw-fault`.

## Risks and Edge Cases

- Direct/AIO coverage depends on alignment, device logical block size, page size, and filesystem direct-I/O semantics.
- mmap/page-fault regressions are often race-prone and may manifest as hangs rather than clean command failures.

## Test Signals

The paired `.out` file has 2 line(s); its first visible signals are: 'QA output created by 729; Silence is golden'. Runtime pass/fail is primarily the command exit status plus golden-output comparison. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/729 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/730 -->
# sources/test-tools/xfstests/tests/generic/730

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/730`. Test proper file system shut down when the block device is removed underneath and there is dirty data. It is registered with `_begin_fstest auto quick`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 61 source line(s).
- Harness registration: `_begin_fstest auto quick`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/scsi_debug`.
- Capability and skip gates: `_require_test`, `_require_block_device $TEST_DEV`, `_require_scsi_debug`.
- Local shell functions: `_cleanup`.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `size=$(_small_fs_size_mb 256)`
- `SCSI_DEBUG_DEV=`_get_scsi_debug_dev 512 512 0 $size``
- `SCRATCH_DEV=$SCSI_DEBUG_DEV _require_scratch_shutdown`
- `SCSI_DEBUG_MNT="$TEST_DIR/scsi_debug_$seq"`

## Control Flow

- Capability gating runs first through `_require_test`, `_require_block_device $TEST_DEV`, `_require_scsi_debug`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- User-visible phase markers include:
- `line 36: echo "SCSI debug device $SCSI_DEBUG_DEV" >>$seqres.full`
- `line 52: echo 1 > /sys/block/$(_short_dev $SCSI_DEBUG_DEV)/device/delete`
- Key operational lines include:
- `line 15: _unmount $SCSI_DEBUG_MNT >>$seqres.full 2>&1`
- `line 30: _exclude_scratch_mount_option "dax"`
- `line 35: SCRATCH_DEV=$SCSI_DEBUG_DEV _require_scratch_shutdown`
- `line 38: run_check _mkfs_dev $SCSI_DEBUG_DEV`
- `line 43: run_check _mount $SCSI_DEBUG_DEV $SCSI_DEBUG_MNT`
- `line 46: $XFS_IO_PROG -f -c "pwrite 0 1M" $SCSI_DEBUG_MNT/testfile >>$seqres.full`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Synthetic block-device state can be introduced through device-mapper, loop, SCSI debug, or huge-device helpers and must be cleaned even on failure. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/scsi_debug`), and the golden-output file `sources/test-tools/xfstests/tests/generic/730.out` (2 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_test`, `_require_block_device $TEST_DEV`, `_require_scsi_debug`.

## Risks and Edge Cases

- Failure-injection paths can leave mounts or synthetic device tables behind if cleanup is interrupted.

## Test Signals

The paired `.out` file has 2 line(s); its first visible signals are: 'QA output created by 730; cat: -: Input/output error'. Runtime pass/fail is also signaled by post-remount or failure-injection persistence checks. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/730 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/731 -->
# sources/test-tools/xfstests/tests/generic/731

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/731`. Test proper file system shut down when the block device is removed underneath and it has no dirty data. It is registered with `_begin_fstest auto quick`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 58 source line(s).
- Harness registration: `_begin_fstest auto quick`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/scsi_debug`.
- Capability and skip gates: `_require_test`, `_require_block_device $TEST_DEV`, `_require_scsi_debug`.
- Local shell functions: `_cleanup`.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `size=$(_small_fs_size_mb 256)`
- `SCSI_DEBUG_DEV=`_get_scsi_debug_dev 512 512 0 $size``
- `SCSI_DEBUG_MNT="$TEST_DIR/scsi_debug_$seq"`

## Control Flow

- Capability gating runs first through `_require_test`, `_require_block_device $TEST_DEV`, `_require_scsi_debug`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- User-visible phase markers include:
- `line 32: echo "SCSI debug device $SCSI_DEBUG_DEV" >>$seqres.full`
- `line 48: echo 3 > /proc/sys/vm/drop_caches`
- `line 49: echo 1 > /sys/block/`_short_dev $SCSI_DEBUG_DEV`/device/delete`
- Key operational lines include:
- `line 16: _unmount $SCSI_DEBUG_MNT >>$seqres.full 2>&1`
- `line 34: run_check _mkfs_dev $SCSI_DEBUG_DEV`
- `line 39: run_check _mount $SCSI_DEBUG_DEV $SCSI_DEBUG_MNT`
- `line 42: $XFS_IO_PROG -f -c "pwrite 0 1M" -c "fsync" $SCSI_DEBUG_MNT/testfile >>$seqres.full`

## State and Persistence Behavior

Uses the configured xfstests test area or an explicitly created loop/image mount rather than always reformatting the scratch device. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Synthetic block-device state can be introduced through device-mapper, loop, SCSI debug, or huge-device helpers and must be cleaned even on failure. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/scsi_debug`), and the golden-output file `sources/test-tools/xfstests/tests/generic/731.out` (2 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_test`, `_require_block_device $TEST_DEV`, `_require_scsi_debug`.

## Risks and Edge Cases

- Failure-injection paths can leave mounts or synthetic device tables behind if cleanup is interrupted.

## Test Signals

The paired `.out` file has 2 line(s); its first visible signals are: 'QA output created by 731; cat: -: Input/output error'. Runtime pass/fail is primarily the command exit status plus golden-output comparison. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/731 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/732 -->
# sources/test-tools/xfstests/tests/generic/732

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/732`. Mount the same export to different mount points and move (rename) files among those mount points. This simple test recently unveils an ancient nfsd bug that is fixed by fdd2630a739819 ("nfsd: fix change_info in NFSv4 RENAME replies"). It is registered with `_begin_fstest auto quick rename`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 55 source line(s).
- Harness registration: `_begin_fstest auto quick rename`.
- Imported common libraries: `./common/preamble`.
- Capability and skip gates: `_exclude_fs nfs`, `_exclude_fs overlay`, `_exclude_fs tmpfs`, `_require_test`, `_require_scratch`.
- Local shell functions: `_cleanup`.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `testdir1=$TEST_DIR/mountpoint1-$seq`
- `testdir2=$TEST_DIR/mountpoint2-$seq`
- `SCRATCH_MNT=$testdir1 _scratch_mount`
- `SCRATCH_MNT=$testdir2 _scratch_mount`

## Control Flow

- Capability gating runs first through `_exclude_fs nfs`, `_exclude_fs overlay`, `_exclude_fs tmpfs`, `_require_test`, `_require_scratch`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- User-visible phase markers include:
- `line 34: echo "Silence is golden"`
- Key operational lines include:
- `line 18: _unmount $testdir1 2>/dev/null`
- `line 19: _unmount $testdir2 2>/dev/null`
- `line 36: _scratch_mkfs >> $seqres.full`
- `line 42: SCRATCH_MNT=$testdir1 _scratch_mount`
- `line 43: SCRATCH_MNT=$testdir2 _scratch_mount`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick rename`, common helper libraries (`./common/preamble`), and the golden-output file `sources/test-tools/xfstests/tests/generic/732.out` (2 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_exclude_fs nfs`, `_exclude_fs overlay`, `_exclude_fs tmpfs`, `_require_test`, `_require_scratch`.

## Risks and Edge Cases

- Feature gates depend on kernel, userspace tool, and filesystem support; unsupported features correctly produce `_notrun`.
- Directory mutation and rename races depend on dentry-cache timing and may need repeated attempts to expose regressions.

## Test Signals

The paired `.out` file has 2 line(s); its first visible signals are: 'QA output created by 732; Silence is golden'. Runtime pass/fail is primarily the command exit status plus golden-output comparison. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/732 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/733 -->
# sources/test-tools/xfstests/tests/generic/733

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/733`. Race file reads with a very slow reflink operation to see if the reads actually complete while the reflink is ongoing. This is a functionality test for XFS commit 14a537983b22 "xfs: allow read IO and FICLONE to run concurrently" and for BTRFS commit 5d6f0e9890ed "btrfs: stop locking the source extent range during reflink". It is registered with `_begin_fstest auto clone punch`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 93 source line(s).
- Harness registration: `_begin_fstest auto clone punch`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/attr`, `./common/reflink`.
- Capability and skip gates: `_require_scratch_reflink`, `_require_cp_reflink`, `_require_xfs_io_command "fpunch"`, `_require_test_program "punch-alternating"`, `_require_test_program "t_reflink_read_race"`, `_require_command "$TIMEOUT_PROG" timeout`, `_fixed_by_fs_commit btrfs 5d6f0e9890ed "btrfs: stop locking the source extent range during reflink"`, `_fixed_by_fs_commit xfs 14a537983b22 "xfs: allow read IO and FICLONE to run concurrently"`, `_notrun "Insufficient space for stress test; would only create $blocks_needed extents."`.
- Local shell functions: `calc_space`.
- External `$here/src` helpers: `"$here/src/punch-alternating" "$testdir/file1" >> "$seqres.full"`, `{ $here/src/t_reflink_read_race "$testdir/file1" "$testdir/file2" \`.
- Notable variables and constants:
- `testdir="$SCRATCH_MNT/test-$seq"`
- `blocks_needed=$(( 2 ** (fnr + 1) ))`
- `space_needed=$((blocks_needed * blksz * 5 / 4))`
- `free_blocks=$(stat -f -c '%a' "$testdir")`
- `blksz=$(_get_file_block_size "$testdir")`
- `space_avail=$((free_blocks * blksz))`
- `off=$(( (2 ** fnr) * blksz))`

## Control Flow

- Capability gating runs first through `_require_scratch_reflink`, `_require_cp_reflink`, `_require_xfs_io_command "fpunch"`, `_require_test_program "punch-alternating"`, `_require_test_program "t_reflink_read_race"`, plus 4 more.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 35: echo "Format and mount"`
- `line 49: echo "Create a many-block file"`
- `line 64: echo "fnr=$fnr" >> $seqres.full`
- `line 66: echo "Reflink the big file"`
- `line 84: echo "Could not set up program"`
- `line 86: echo "test completed successfully"`
- Key operational lines include:
- `line 21: _require_scratch_reflink`
- `line 22: _require_cp_reflink`
- `line 25: _require_test_program "t_reflink_read_race"`
- `line 26: _require_command "$TIMEOUT_PROG" timeout`
- `line 29: "btrfs: stop locking the source extent range during reflink"`
- `line 36: _scratch_mkfs > "$seqres.full" 2>&1`
- `line 37: _scratch_mount >> "$seqres.full" 2>&1`
- `line 51: free_blocks=$(stat -f -c '%a' "$testdir")`
- `line 59: $XFS_IO_PROG -f -c "pwrite -S 0x61 -b 4194304 $off $off" "$testdir/file1" >> "$seqres.full"`
- `line 62: $TIMEOUT_PROG 1s cp --reflink=always "$testdir/file1" "$testdir/garbage" || break`
- `line 80: { $here/src/t_reflink_read_race "$testdir/file1" "$testdir/file2" \`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Shared extent or atomic-update state is exercised, so correctness depends on clone/dedupe/exchange persistence and metadata ordering. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto clone punch`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/attr`, `./common/reflink`), and the golden-output file `sources/test-tools/xfstests/tests/generic/733.out` (5 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_scratch_reflink`, `_require_cp_reflink`, `_require_xfs_io_command "fpunch"`, `_require_test_program "punch-alternating"`, `_require_test_program "t_reflink_read_race"`, `_require_command "$TIMEOUT_PROG" timeout`, `_fixed_by_fs_commit btrfs 5d6f0e9890ed "btrfs: stop locking the source extent range during reflink"`, `_fixed_by_fs_commit xfs 14a537983b22 "xfs: allow read IO and FICLONE to run concurrently"`, plus 1 more.

## Risks and Edge Cases

- Shared-extent and exchange operations can expose stale data, permission-bit, or log-ordering bugs that only appear after remount/recovery.

## Test Signals

The paired `.out` file has 5 line(s); its first visible signals are: 'QA output created by 733; Format and mount; Create a many-block file; Reflink the big file; test completed successfully'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands, hang/race detection through background work, loops, or timeout windows. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/733 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/734 -->
# sources/test-tools/xfstests/tests/generic/734

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/734`. This is a regression test for the kernel commit noted below. The stale memory exposure can be exploited by creating a file with shared blocks, evicting the page cache for that file, and then funshareing at least one memory page's worth of data. iomap will mark the page uptodate and dirty without ever reading the ondisk contents. It is registered with `_begin_fstest auto quick unshare clone`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 85 source line(s).
- Harness registration: `_begin_fstest auto quick unshare clone`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/reflink`.
- Capability and skip gates: `_fixed_by_git_commit kernel 35d30c9cf127 "iomap: don't skip reading in !uptodate folios when unsharing a range"`, `_require_test_reflink`, `_require_cp_reflink`, `_require_xfs_io_command "funshare"`.
- Local shell functions: `_cleanup`.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `testdir=$TEST_DIR/test-$seq`
- `pagesz=$(_get_page_size)`
- `alloc_unit=$(_get_file_block_size $TEST_DIR)`
- `filesz=$(( ( (4 * pagesz) + alloc_unit - 1) / alloc_unit * alloc_unit))`

## Control Flow

- Capability gating runs first through `_fixed_by_git_commit kernel 35d30c9cf127 "iomap: don't skip reading in !uptodate folios when unsharing a range"`, `_require_test_reflink`, `_require_cp_reflink`, `_require_xfs_io_command "funshare"`.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 44: echo "Create the original file and a clone"`
- `line 54: echo "Funshare at least one pagecache page"`
- `line 59: echo "Check contents"`
- `line 63: echo "file2.chk does not match file2"`
- `line 65: echo "file2.chk contents" >> $seqres.full`
- `line 67: echo "file2 contents" >> $seqres.full`
- `line 69: echo "end bad contents" >> $seqres.full`
- `line 74: echo "file2.chk does not match file3"`
- Key operational lines include:
- `line 30: _require_test_reflink`
- `line 31: _require_cp_reflink`
- `line 47: _cp_reflink $testdir/file1 $testdir/file2`
- `line 48: _cp_reflink $testdir/file1 $testdir/file3`
- `line 55: $XFS_IO_PROG -c "funshare 0 $filesz" $testdir/file2`
- `line 56: $XFS_IO_PROG -c "funshare 0 $filesz" $testdir/file3`
- `line 62: if ! cmp -s $testdir/file2.chk $testdir/file2; then`
- `line 73: if ! cmp -s $testdir/file2.chk $testdir/file3; then`

## State and Persistence Behavior

Uses the configured xfstests test area or an explicitly created loop/image mount rather than always reformatting the scratch device. Shared extent or atomic-update state is exercised, so correctness depends on clone/dedupe/exchange persistence and metadata ordering. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick unshare clone`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/reflink`), and the golden-output file `sources/test-tools/xfstests/tests/generic/734.out` (4 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_fixed_by_git_commit kernel 35d30c9cf127 "iomap: don't skip reading in !uptodate folios when unsharing a range"`, `_require_test_reflink`, `_require_cp_reflink`, `_require_xfs_io_command "funshare"`.

## Risks and Edge Cases

- Shared-extent and exchange operations can expose stale data, permission-bit, or log-ordering bugs that only appear after remount/recovery.

## Test Signals

The paired `.out` file has 4 line(s); its first visible signals are: 'QA output created by 734; Create the original file and a clone; Funshare at least one pagecache page; Check contents'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/734 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/735 -->
# sources/test-tools/xfstests/tests/generic/735

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/735`. Append writes to a file with logical block numbers close to 0xffffffff and observe if a kernel crash is caused by ext4_lblk_t overflow triggering BUG_ON at ext4_mb_new_inode_pa(). This is a regression test for commit bc056e7163ac ("ext4: fix BUG in ext4_mb_new_inode_pa() due to overflow") commit 2dcf5fde6dff ("ext4: prevent the normalized size from exceeding EXT_MAX_BLOCKS") It is registered with `_begin_fstest auto quick insert prealloc`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 58 source line(s).
- Harness registration: `_begin_fstest auto quick insert prealloc`.
- Imported common libraries: `./common/preamble`, `./common/populate`.
- Capability and skip gates: `_fixed_by_kernel_commit bc056e7163ac "ext4: fix BUG in ext4_mb_new_inode_pa() due to overflow"`, `_fixed_by_kernel_commit 2dcf5fde6dff "ext4: prevent the normalized size from exceeding EXT_MAX_BLOCKS"`, `_require_odirect`, `_require_xfs_io_command "falloc"`, `_require_xfs_io_command "finsert"`, `_require_max_file_range_blocks $(( (1 << 32) - 1 ))`, `_require_congruent_file_oplen $SCRATCH_MNT 1048576	# finsert at 1M`.
- Local shell functions: none visible.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `dev_size=$((80 * 1024 * 1024))`
- `file_blksz="$(_get_file_block_size ${SCRATCH_MNT})"`
- `max_pos=$(( 0xffffffff * file_blksz ))`
- `finsert_len=$(( max_pos - ((10 + 2) << 20) ))`
- `nr_free=$(stat -f -c '%f' ${SCRATCH_MNT})`

## Control Flow

- Capability gating runs first through `_fixed_by_kernel_commit bc056e7163ac "ext4: fix BUG in ext4_mb_new_inode_pa() due to overflow"`, `_fixed_by_kernel_commit 2dcf5fde6dff "ext4: prevent the normalized size from exceeding EXT_MAX_BLOCKS"`, `_require_odirect`, `_require_xfs_io_command "falloc"`, `_require_xfs_io_command "finsert"`, plus 2 more.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 54: echo "Silence is golden"`
- Key operational lines include:
- `line 23: _require_xfs_io_command "falloc"`
- `line 24: _require_xfs_io_command "finsert"`
- `line 28: _scratch_mkfs_sized $dev_size >>$seqres.full 2>&1`
- `line 30: _scratch_mount`
- `line 31: _require_congruent_file_oplen $SCRATCH_MNT 1048576 # finsert at 1M`
- `line 35: $XFS_IO_PROG -f -c "falloc 0 1M" "${SCRATCH_MNT}/tmp" >> $seqres.full`
- `line 38: $XFS_IO_PROG -f -c "falloc 0 10M" "${SCRATCH_MNT}/file" >> $seqres.full`
- `line 40: finsert_len=$(( max_pos - ((10 + 2) << 20) ))`
- `line 41: $XFS_IO_PROG -f -c "finsert 1M ${finsert_len}" "${SCRATCH_MNT}/file" >> $seqres.full`
- `line 44: nr_free=$(stat -f -c '%f' ${SCRATCH_MNT})`
- `line 46: _scratch_sync`
- `line 52: $XFS_IO_PROG -c "open -ad ${SCRATCH_MNT}/file" -c "pwrite -S 0xff 0 $((2 * file_blksz))" >> $seqres.full`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick insert prealloc`, common helper libraries (`./common/preamble`, `./common/populate`), and the golden-output file `sources/test-tools/xfstests/tests/generic/735.out` (2 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_fixed_by_kernel_commit bc056e7163ac "ext4: fix BUG in ext4_mb_new_inode_pa() due to overflow"`, `_fixed_by_kernel_commit 2dcf5fde6dff "ext4: prevent the normalized size from exceeding EXT_MAX_BLOCKS"`, `_require_odirect`, `_require_xfs_io_command "falloc"`, `_require_xfs_io_command "finsert"`, `_require_max_file_range_blocks $(( (1 << 32) - 1 ))`, `_require_congruent_file_oplen $SCRATCH_MNT 1048576	# finsert at 1M`.

## Risks and Edge Cases

- Direct/AIO coverage depends on alignment, device logical block size, page size, and filesystem direct-I/O semantics.

## Test Signals

The paired `.out` file has 2 line(s); its first visible signals are: 'QA output created by 735; Silence is golden'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/735 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/736 -->
# sources/test-tools/xfstests/tests/generic/736

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/736`. Test that on a fairly large directory if we keep renaming files while holding the directory open and doing readdir(3) calls, we don't end up in an infinite loop. It is registered with `_begin_fstest auto quick dir rename`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 36 source line(s).
- Harness registration: `_begin_fstest auto quick dir rename`.
- Imported common libraries: `./common/preamble`.
- Capability and skip gates: `_require_test`, `_require_test_program readdir-while-renames`, `_fixed_by_fs_commit btrfs 9b378f6ad48c "btrfs: fix infinite directory reads"`.
- Local shell functions: `_cleanup`.
- External `$here/src` helpers: `$here/src/readdir-while-renames $target_dir`.
- Notable variables and constants:
- `target_dir="$TEST_DIR/test-$seq"`

## Control Flow

- Capability gating runs first through `_require_test`, `_require_test_program readdir-while-renames`, `_fixed_by_fs_commit btrfs 9b378f6ad48c "btrfs: fix infinite directory reads"`.
- User-visible phase markers include:
- `line 34: echo "Silence is golden"`

## State and Persistence Behavior

Uses the configured xfstests test area or an explicitly created loop/image mount rather than always reformatting the scratch device. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick dir rename`, common helper libraries (`./common/preamble`), and the golden-output file `sources/test-tools/xfstests/tests/generic/736.out` (2 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_test`, `_require_test_program readdir-while-renames`, `_fixed_by_fs_commit btrfs 9b378f6ad48c "btrfs: fix infinite directory reads"`.

## Risks and Edge Cases

- Directory mutation and rename races depend on dentry-cache timing and may need repeated attempts to expose regressions.

## Test Signals

The paired `.out` file has 2 line(s); its first visible signals are: 'QA output created by 736; Silence is golden'. Runtime pass/fail is primarily the command exit status plus golden-output comparison. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/736 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/737 -->
# sources/test-tools/xfstests/tests/generic/737

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/737`. Integrity test for O_SYNC with buff-io, dio, aio-dio with sudden shutdown. Based on a testcase reported by Gao Xiang <hsiangkao@linux.alibaba.com> It is registered with `_begin_fstest auto quick shutdown aio`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 52 source line(s).
- Harness registration: `_begin_fstest auto quick shutdown aio`.
- Imported common libraries: `./common/preamble`.
- Capability and skip gates: `_require_scratch`, `_require_scratch_shutdown`, `_require_aiodio aio-dio-write-verify`.
- Local shell functions: none visible.
- External `$here/src` helpers: none visible.

## Control Flow

- Capability gating runs first through `_require_scratch`, `_require_scratch_shutdown`, `_require_aiodio aio-dio-write-verify`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 24: echo "T-1: Create a 1M file using buff-io & O_SYNC"`
- `line 26: echo "T-1: Shutdown the fs suddenly"`
- `line 28: echo "T-1: Cycle mount"`
- `line 30: echo "T-1: File contents after cycle mount"`
- `line 33: echo "T-2: Create a 1M file using O_DIRECT & O_SYNC"`
- `line 35: echo "T-2: Shutdown the fs suddenly"`
- `line 37: echo "T-2: Cycle mount"`
- `line 39: echo "T-2: File contents after cycle mount"`
- Key operational lines include:
- `line 15: _require_scratch_shutdown`
- `line 21: _scratch_mkfs > $seqres.full 2>&1`
- `line 22: _scratch_mount`
- `line 25: $XFS_IO_PROG -fs -c "pwrite -S 0x5a 0 1M" $SCRATCH_MNT/testfile.t1 > /dev/null 2>&1`
- `line 27: _scratch_shutdown`
- `line 29: _scratch_cycle_mount`
- `line 31: _hexdump $SCRATCH_MNT/testfile.t1`
- `line 34: $XFS_IO_PROG -fsd -c "pwrite -S 0x5a 0 1M" $SCRATCH_MNT/testfile.t2 > /dev/null 2>&1`
- `line 36: _scratch_shutdown`
- `line 38: _scratch_cycle_mount`
- `line 40: _hexdump $SCRATCH_MNT/testfile.t2`
- `line 43: $AIO_TEST -a size=1048576 -S -N $SCRATCH_MNT/testfile.t3 > /dev/null 2>&1`
- `line 45: _scratch_shutdown`
- `line 47: _scratch_cycle_mount`
- `line 49: _hexdump $SCRATCH_MNT/testfile.t3`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick shutdown aio`, common helper libraries (`./common/preamble`), and the golden-output file `sources/test-tools/xfstests/tests/generic/737.out` (22 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_scratch`, `_require_scratch_shutdown`, `_require_aiodio aio-dio-write-verify`.

## Risks and Edge Cases

- Direct/AIO coverage depends on alignment, device logical block size, page size, and filesystem direct-I/O semantics.
- Failure-injection paths can leave mounts or synthetic device tables behind if cleanup is interrupted.

## Test Signals

The paired `.out` file has 22 line(s); its first visible signals are: 'QA output created by 737; T-1: Create a 1M file using buff-io & O_SYNC; T-1: Shutdown the fs suddenly; T-1: Cycle mount; T-1: File contents after cycle mount'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands, post-remount or failure-injection persistence checks. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/737 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/738 -->
# sources/test-tools/xfstests/tests/generic/738

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/738`. Test possible deadlock of umount and reclaim memory when there are EOF blocks in files. It is registered with `_begin_fstest auto quick freeze`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 54 source line(s).
- Harness registration: `_begin_fstest auto quick freeze`.
- Imported common libraries: `./common/preamble`.
- Capability and skip gates: `_fixed_by_fs_commit xfs ab23a7768739 "xfs: per-cpu deferred inode inactivation queues"`, `_require_scratch`, `_require_freeze`.
- Local shell functions: `_cleanup`, `create_eof_block_file`.
- External `$here/src` helpers: none visible.

## Control Flow

- Capability gating runs first through `_fixed_by_fs_commit xfs ab23a7768739 "xfs: per-cpu deferred inode inactivation queues"`, `_require_scratch`, `_require_freeze`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- User-visible phase markers include:
- `line 46: echo 3 > /proc/sys/vm/drop_caches &`
- `line 52: echo "Silence is golden"`
- Key operational lines include:
- `line 26: _scratch_mkfs >> $seqres.full`
- `line 27: _scratch_mount`
- `line 37: $XFS_IO_PROG -fc "pwrite 0 64k" $SCRATCH_MNT/testfile >> $seqres.full`
- `line 42: _scratch_sync`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick freeze`, common helper libraries (`./common/preamble`), and the golden-output file `sources/test-tools/xfstests/tests/generic/738.out` (2 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_fixed_by_fs_commit xfs ab23a7768739 "xfs: per-cpu deferred inode inactivation queues"`, `_require_scratch`, `_require_freeze`.

## Risks and Edge Cases

- Most failures should surface as unexpected output, nonzero helper status, or harness `_fail`/`_notrun` behavior.

## Test Signals

The paired `.out` file has 2 line(s); its first visible signals are: 'QA output created by 738; Silence is golden'. Runtime pass/fail is primarily the command exit status plus golden-output comparison. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/738 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/739 -->
# sources/test-tools/xfstests/tests/generic/739

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/739`. Verify the on-disk format of encrypted files that use a crypto data unit size that differs from the filesystem block size. This tests the functionality that was introduced in Linux 6.7 by kernel commit 5b1188847180 ("fscrypt: support crypto data unit size less than filesystem block size"). It is registered with `_begin_fstest auto quick encrypt`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 30 source line(s).
- Harness registration: `_begin_fstest auto quick encrypt`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/encrypt`.
- Capability and skip gates: `_wants_kernel_commit 5b1188847180 "fscrypt: support crypto data unit size less than filesystem block size"`.
- Local shell functions: none visible.
- External `$here/src` helpers: none visible.

## Control Flow

- Capability gating runs first through `_wants_kernel_commit 5b1188847180 "fscrypt: support crypto data unit size less than filesystem block size"`.
- Key operational lines include:
- `line 25: _verify_ciphertext_for_encryption_policy AES-256-XTS AES-256-CTS-CBC v2 log2_dusize=9`
- `line 26: _verify_ciphertext_for_encryption_policy AES-256-XTS AES-256-CTS-CBC v2 log2_dusize=10`

## State and Persistence Behavior

Uses the configured xfstests test area or an explicitly created loop/image mount rather than always reformatting the scratch device. Encryption policy/key state is created during the test and used to check no-key/key-present transitions. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick encrypt`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/encrypt`), and the golden-output file `sources/test-tools/xfstests/tests/generic/739.out` (11 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_wants_kernel_commit 5b1188847180 "fscrypt: support crypto data unit size less than filesystem block size"`.

## Risks and Edge Cases

- Feature gates depend on kernel, userspace tool, and filesystem support; unsupported features correctly produce `_notrun`.

## Test Signals

The paired `.out` file has 11 line(s); its first visible signals are: 'QA output created by 739; Verifying ciphertext with parameters:; contents_encryption_mode: AES-256-XTS; filenames_encryption_mode: AES-256-CTS-CBC'. Runtime pass/fail is primarily the command exit status plus golden-output comparison. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/739 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/740 -->
# sources/test-tools/xfstests/tests/generic/740

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/740`. cross check mkfs detection of foreign filesystems It is registered with `_begin_fstest mkfs auto quick`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 96 source line(s).
- Harness registration: `_begin_fstest mkfs auto quick`.
- Imported common libraries: `./common/preamble`, `./common/filter`.
- Capability and skip gates: `_exclude_fs ext2`, `_exclude_fs ext3`, `_exclude_fs ext4`, `_exclude_fs jfs`, `_exclude_fs ocfs2`, `_exclude_fs udf`, `_require_scratch_nocheck`, `_require_no_large_scratch_dev`, `_require_block_device "${SCRATCH_DEV}"`, `_require_non_zoned_device "${SCRATCH_DEV}"`.
- Local shell functions: none visible.
- External `$here/src` helpers: `$here/src/devzero -n 20 $SCRATCH_DEV >/dev/null`.
- Notable variables and constants:
- `preop="" # for special input needs (usually a prompt)`
- `preargs="" # for any special pre-device options`
- `postargs="" # for any special post-device options`
- `preargs="-F"`
- `preargs=/proc/fs`
- `preop="echo y |"`
- `preargs="-p lock_nolock -j 1"`
- `preop="echo Y |"`
- `postargs=2000`
- `postargs="--quick"`
- `preop="echo y |"`
- `preargs="-f"`

## Control Flow

- Capability gating runs first through `_exclude_fs ext2`, `_exclude_fs ext3`, `_exclude_fs ext4`, `_exclude_fs jfs`, `_exclude_fs ocfs2`, plus 5 more.
- User-visible phase markers include:
- `line 31: echo "Silence is golden."`
- `line 78: echo "=== Creating $fs filesystem..." >>$seqres.full`
- `line 79: echo " ( $preop mkfs -t $fs $preargs $SCRATCH_DEV $postargs )" >>$seqres.full`
- `line 85: echo "=== Attempting $FSTYP overwrite of $fs..." >>$seqres.full`
- `line 90: echo "mkfs of type ${fs} failed" >>$seqres.full`
- Key operational lines include:
- `line 24: _require_scratch_nocheck`
- `line 25: _require_no_large_scratch_dev`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest mkfs auto quick`, common helper libraries (`./common/preamble`, `./common/filter`), and the golden-output file `sources/test-tools/xfstests/tests/generic/740.out` (2 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_exclude_fs ext2`, `_exclude_fs ext3`, `_exclude_fs ext4`, `_exclude_fs jfs`, `_exclude_fs ocfs2`, `_exclude_fs udf`, `_require_scratch_nocheck`, `_require_no_large_scratch_dev`, plus 2 more.

## Risks and Edge Cases

- Most failures should surface as unexpected output, nonzero helper status, or harness `_fail`/`_notrun` behavior.

## Test Signals

The paired `.out` file has 2 line(s); its first visible signals are: 'QA output created by 740; Silence is golden.'. Runtime pass/fail is primarily the command exit status plus golden-output comparison. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/740 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/741 -->
# sources/test-tools/xfstests/tests/generic/741

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/741`. Attempt to mount both the DM physical device and the DM flakey device. Verify the returned error message. It is registered with `_begin_fstest auto quick volume tempfsid`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 62 source line(s).
- Harness registration: `_begin_fstest auto quick volume tempfsid`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/dmflakey`.
- Capability and skip gates: `_require_test`, `_require_scratch`, `_require_dm_target flakey`, `_fixed_by_fs_commit btrfs 2f1aeab9fca1 "btrfs: return accurate error code on open failure"`.
- Local shell functions: `_cleanup`.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `extra_mnt=$TEST_DIR/extra_mnt`

## Control Flow

- Capability gating runs first through `_require_test`, `_require_scratch`, `_require_dm_target flakey`, `_fixed_by_fs_commit btrfs 2f1aeab9fca1 "btrfs: return accurate error code on open failure"`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- Key operational lines include:
- `line 19: _unmount $extra_mnt &> /dev/null`
- `line 20: _unmount $extra_mnt &> /dev/null`
- `line 22: _scratch_unmount`
- `line 23: _cleanup_flakey`
- `line 39: _scratch_mkfs >> $seqres.full`
- `line 40: _init_flakey`
- `line 41: _scratch_mount`
- `line 49: _mount $NON_FLAKEY_DEV $extra_mnt 2>/dev/null && \`
- `line 53: _scratch_unmount`
- `line 54: _mount $NON_FLAKEY_DEV $extra_mnt 2>/dev/null && \`
- `line 58: _cleanup_flakey`
- `line 59: _scratch_mount`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Synthetic block-device state can be introduced through device-mapper, loop, SCSI debug, or huge-device helpers and must be cleaned even on failure. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick volume tempfsid`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/dmflakey`), and the golden-output file `sources/test-tools/xfstests/tests/generic/741.out` (1 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_test`, `_require_scratch`, `_require_dm_target flakey`, `_fixed_by_fs_commit btrfs 2f1aeab9fca1 "btrfs: return accurate error code on open failure"`.

## Risks and Edge Cases

- Failure-injection paths can leave mounts or synthetic device tables behind if cleanup is interrupted.

## Test Signals

The paired `.out` file has 1 line(s); its first visible signals are: 'QA output created by 741'. Runtime pass/fail is also signaled by hang/race detection through background work, loops, or timeout windows. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/741 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/742 -->
# sources/test-tools/xfstests/tests/generic/742

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/742`. Test fiemap into an mmaped buffer of the same file Create a reasonably large file, then run a program which mmaps it and uses that as a buffer for an fiemap call. This is a regression test for btrfs where we used to hold a lock for the duration of the fiemap call which would result in a deadlock if we page faulted. It is registered with `_begin_fstest quick auto fiemap mmap`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 49 source line(s).
- Harness registration: `_begin_fstest quick auto fiemap mmap`.
- Imported common libraries: `./common/preamble`.
- Capability and skip gates: `_fixed_by_fs_commit btrfs b0ad381fa769 "btrfs: fix deadlock with fiemap and extent locking"`, `_require_test`, `_require_test_program "fiemap-fault"`, `_require_test_program "punch-alternating"`, `_require_xfs_io_command "fpunch"`, `_require_xfs_io_command "fiemap"`.
- Local shell functions: `_cleanup`.
- External `$here/src` helpers: `$here/src/punch-alternating $dst`, `$here/src/fiemap-fault $dst`.
- Notable variables and constants:
- `dst=$TEST_DIR/$seq/fiemap-fault`
- `blksz=$(_get_file_block_size $TEST_DIR)`

## Control Flow

- Capability gating runs first through `_fixed_by_fs_commit btrfs b0ad381fa769 "btrfs: fix deadlock with fiemap and extent locking"`, `_require_test`, `_require_test_program "fiemap-fault"`, `_require_test_program "punch-alternating"`, `_require_xfs_io_command "fpunch"`, plus 1 more.
- User-visible phase markers include:
- `line 37: echo "Silence is golden"`
- Key operational lines include:
- `line 15: _begin_fstest quick auto fiemap mmap`
- `line 41: $XFS_IO_PROG -f -c "pwrite -q 0 $((blksz * 10000))" $dst`

## State and Persistence Behavior

Uses the configured xfstests test area or an explicitly created loop/image mount rather than always reformatting the scratch device. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest quick auto fiemap mmap`, common helper libraries (`./common/preamble`), and the golden-output file `sources/test-tools/xfstests/tests/generic/742.out` (2 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_fixed_by_fs_commit btrfs b0ad381fa769 "btrfs: fix deadlock with fiemap and extent locking"`, `_require_test`, `_require_test_program "fiemap-fault"`, `_require_test_program "punch-alternating"`, `_require_xfs_io_command "fpunch"`, `_require_xfs_io_command "fiemap"`.

## Risks and Edge Cases

- mmap/page-fault regressions are often race-prone and may manifest as hangs rather than clean command failures.

## Test Signals

The paired `.out` file has 2 line(s); its first visible signals are: 'QA output created by 742; Silence is golden'. Runtime pass/fail is primarily the command exit status plus golden-output comparison. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/742 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/743 -->
# sources/test-tools/xfstests/tests/generic/743

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/743`. This is a regression test for a kernel hang that I saw when creating a memory mapping, injecting EIO errors on the block device, and invoking MADV_POPULATE_READ on the mapping to fault in the pages. It is registered with `_begin_fstest auto rw eio mmap`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 65 source line(s).
- Harness registration: `_begin_fstest auto rw eio mmap`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/dmerror`.
- Capability and skip gates: `_fixed_by_kernel_commit 631426ba1d45 "mm/madvise: make MADV_POPULATE_(READ|WRITE) handle VM_FAULT_RETRY properly"`, `_require_xfs_io_command madvise -R`, `_require_scratch`, `_require_dm_target error`, `_require_command "$TIMEOUT_PROG" "timeout"`.
- Local shell functions: `_cleanup`.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `filesz=2m`

## Control Flow

- Capability gating runs first through `_fixed_by_kernel_commit 631426ba1d45 "mm/madvise: make MADV_POPULATE_(READ|WRITE) handle VM_FAULT_RETRY properly"`, `_require_xfs_io_command madvise -R`, `_require_scratch`, `_require_dm_target error`, `_require_command "$TIMEOUT_PROG" "timeout"`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 49: echo read with no errors`
- `line 57: echo read with IO errors`
- Key operational lines include:
- `line 12: _begin_fstest auto rw eio mmap`
- `line 19: _dmerror_unmount`
- `line 20: _dmerror_cleanup`
- `line 28: "mm/madvise: make MADV_POPULATE_(READ|WRITE) handle VM_FAULT_RETRY properly"`
- `line 32: _require_xfs_io_command madvise -R`
- `line 35: _require_command "$TIMEOUT_PROG" "timeout"`
- `line 37: _scratch_mkfs >> $seqres.full 2>&1`
- `line 38: _dmerror_init`
- `line 43: _dmerror_mount`
- `line 44: $XFS_IO_PROG -f -c "pwrite -S 0x58 0 $filesz" "$SCRATCH_MNT/a" >> $seqres.full`
- `line 45: _dmerror_unmount`
- `line 46: _dmerror_mount`
- `line 50: $TIMEOUT_PROG -s KILL 10s $XFS_IO_PROG -c "mmap -r 0 $filesz" -c "madvise -R 0 $filesz" "$SCRATCH_MNT/a"`
- `line 51: _dmerror_unmount`
- `line 52: _dmerror_mount`
- `line 56: stat "$SCRATCH_MNT/a" >> $seqres.full`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Synthetic block-device state can be introduced through device-mapper, loop, SCSI debug, or huge-device helpers and must be cleaned even on failure. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto rw eio mmap`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/dmerror`), and the golden-output file `sources/test-tools/xfstests/tests/generic/743.out` (4 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_fixed_by_kernel_commit 631426ba1d45 "mm/madvise: make MADV_POPULATE_(READ|WRITE) handle VM_FAULT_RETRY properly"`, `_require_xfs_io_command madvise -R`, `_require_scratch`, `_require_dm_target error`, `_require_command "$TIMEOUT_PROG" "timeout"`.

## Risks and Edge Cases

- Failure-injection paths can leave mounts or synthetic device tables behind if cleanup is interrupted.
- mmap/page-fault regressions are often race-prone and may manifest as hangs rather than clean command failures.

## Test Signals

The paired `.out` file has 4 line(s); its first visible signals are: 'QA output created by 743; read with no errors; read with IO errors; madvise: Bad address'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands, xfstests output filters, hang/race detection through background work, loops, or timeout windows, post-remount or failure-injection persistence checks. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/743 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/744 -->
# sources/test-tools/xfstests/tests/generic/744

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/744`. Set up a filesystem, create a clone, mount both, and verify if the cp reflink operation between these two mounts fails. It is registered with `_begin_fstest auto clone volume tempfsid`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 80 source line(s).
- Harness registration: `_begin_fstest auto clone volume tempfsid`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/reflink`.
- Capability and skip gates: `_require_duplicate_fsid`, `_require_test`, `_require_block_device $TEST_DEV`, `_require_test_reflink`, `_require_cp_reflink`, `_require_loop`.
- Local shell functions: `_cleanup`, `clone_filesystem`.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `mnt1=$TEST_DIR/$seq/mnt1`
- `mnt2=$TEST_DIR/$seq/mnt2`
- `loop_file1="$TEST_DIR/$seq/image1"`
- `loop_dev1=$(_create_loop_device "$loop_file1")`
- `loop_file2="$TEST_DIR/$seq/image2"`
- `loop_dev2=$(_create_loop_device "$loop_file2")`

## Control Flow

- Capability gating runs first through `_require_duplicate_fsid`, `_require_test`, `_require_block_device $TEST_DEV`, `_require_test_reflink`, `_require_cp_reflink`, plus 1 more.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- Key operational lines include:
- `line 18: _unmount $mnt2 &> /dev/null`
- `line 19: _unmount $mnt1 &> /dev/null`
- `line 20: [ -b "$loop_dev2" ] && _destroy_loop_device $loop_dev2`
- `line 21: [ -b "$loop_dev1" ] && _destroy_loop_device $loop_dev1`
- `line 32: _require_test_reflink`
- `line 33: _require_cp_reflink`
- `line 41: _mkfs_dev $dev1`
- `line 43: _mount $dev1 $mnt1`
- `line 44: $XFS_IO_PROG -fc 'pwrite -S 0x61 0 9000' $mnt1/foo >> $seqres.full`
- `line 45: _unmount $mnt1`
- `line 60: loop_dev1=$(_create_loop_device "$loop_file1")`
- `line 64: loop_dev2=$(_create_loop_device "$loop_file2")`
- `line 69: _mount $loop_dev1 $mnt1`
- `line 70: $XFS_IO_PROG -fc 'pwrite -S 0x61 0 9000' $mnt1/foo | _filter_xfs_io`
- `line 73: _mount $loop_dev2 $mnt2 || _fail "mount of cloned device failed"`
- `line 76: _cp_reflink $mnt1/foo $mnt2/bar 2>&1 | _filter_test_dir`

## State and Persistence Behavior

Uses the configured xfstests test area or an explicitly created loop/image mount rather than always reformatting the scratch device. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Synthetic block-device state can be introduced through device-mapper, loop, SCSI debug, or huge-device helpers and must be cleaned even on failure. Shared extent or atomic-update state is exercised, so correctness depends on clone/dedupe/exchange persistence and metadata ordering. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto clone volume tempfsid`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/reflink`), and the golden-output file `sources/test-tools/xfstests/tests/generic/744.out` (4 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_duplicate_fsid`, `_require_test`, `_require_block_device $TEST_DEV`, `_require_test_reflink`, `_require_cp_reflink`, `_require_loop`.

## Risks and Edge Cases

- Shared-extent and exchange operations can expose stale data, permission-bit, or log-ordering bugs that only appear after remount/recovery.

## Test Signals

The paired `.out` file has 4 line(s); its first visible signals are: "QA output created by 744; wrote 9000/9000 bytes at offset 0; XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec); cp: failed to clone 'TEST_DIR/744/mnt2/bar' from 'TEST_DIR/744/mnt1/foo': Invalid cross-device link". Runtime pass/fail is also signaled by xfstests output filters, hang/race detection through background work, loops, or timeout windows. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/744 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/745 -->
# sources/test-tools/xfstests/tests/generic/745

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/745`. Test that after syncing the filesystem, adding many xattrs to a file, syncing the filesystem again, writing to the file and then doing a fsync against that file, all the xattrs still exists after a power failure. That is, after the fsync log/journal is replayed, the xattrs still exist and with the correct values. This test is motivated by a bug found in btrfs. It is registered with `_begin_fstest auto metadata quick log`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 94 source line(s).
- Harness registration: `_begin_fstest auto metadata quick log`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/dmflakey`, `./common/attr`.
- Capability and skip gates: `_require_scratch`, `_require_dm_target flakey`, `_require_attrs`, `_notrun "Requires support for > 1000 xattrs"`, `_require_metadata_journaling $SCRATCH_DEV`.
- Local shell functions: `_cleanup`.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `num_xattrs=2000`
- `name="user.attr_$(printf "%04d" $i)"`
- `name="user.attr_$(printf "%04d" $i)"`

## Control Flow

- Capability gating runs first through `_require_scratch`, `_require_dm_target flakey`, `_require_attrs`, `_notrun "Requires support for > 1000 xattrs"`, `_require_metadata_journaling $SCRATCH_DEV`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- User-visible phase markers include:
- `line 82: echo "File content after crash and log replay:"`
- `line 85: echo "File xattrs after crash and log replay:"`
- `line 88: echo -n "$name="`
- `line 90: echo`
- Key operational lines include:
- `line 21: _cleanup_flakey`
- `line 46: _scratch_mkfs >> $seqres.full 2>&1`
- `line 48: _init_flakey`
- `line 49: _scratch_mount`
- `line 53: $XFS_IO_PROG -f -c "pwrite -S 0xaa 0 32k" $SCRATCH_MNT/foo | _filter_xfs_io`
- `line 54: _scratch_sync`
- `line 69: _scratch_sync`
- `line 76: $XFS_IO_PROG -c "pwrite -S 0xbb 8K 16K" \`
- `line 80: _flakey_drop_and_remount`
- `line 89: _getfattr --absolute-names -n $name --only-values $SCRATCH_MNT/foo`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Synthetic block-device state can be introduced through device-mapper, loop, SCSI debug, or huge-device helpers and must be cleaned even on failure. Extended attributes are part of the persistent state being created, replayed, or verified. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto metadata quick log`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/dmflakey`, `./common/attr`), and the golden-output file `sources/test-tools/xfstests/tests/generic/745.out` (2014 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_scratch`, `_require_dm_target flakey`, `_require_attrs`, `_notrun "Requires support for > 1000 xattrs"`, `_require_metadata_journaling $SCRATCH_DEV`.

## Risks and Edge Cases

- Failure-injection paths can leave mounts or synthetic device tables behind if cleanup is interrupted.
- The golden output is large, so formatting drift in helper output can create noisy failures even when the core behavior is correct.

## Test Signals

The paired `.out` file has 2014 line(s); its first visible signals are: 'QA output created by 745; wrote 32768/32768 bytes at offset 0; XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec); wrote 16384/16384 bytes at offset 8192; XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec)'. Runtime pass/fail is also signaled by xfstests output filters, post-remount or failure-injection persistence checks. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/745 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/746 -->
# sources/test-tools/xfstests/tests/generic/746

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/746`. Test that filesystem sends discard requests only on free blocks It is registered with `_begin_fstest auto trim fiemap`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 247 source line(s).
- Harness registration: `_begin_fstest auto trim fiemap`.
- Imported common libraries: `./common/preamble`.
- Capability and skip gates: `_require_test`, `_require_loop`, `_require_fstrim`, `_require_xfs_io_command "fiemap"`, `_require_fs_space $TEST_DIR 307200`, `_require_btrfs_command inspect-internal dump-super`, `_require_btrfs_command inspect-internal dump-tree`, `_require_fs_space $TEST_DIR 3145728`, `_require_dumpe2fs`, `_notrun "Requires fs-specific way to check discard ranges"`, plus 1 more.
- Local shell functions: `_cleanup`, `get_holes`, `get_free_sectors`, `merge_ranges`.
- External `$here/src` helpers: `$PYTHON3_PROG $here/src/parse-free-space.py -n $nodesize -b $tmp/bg_dump \`, `-f $here/src/parse-dev-tree.awk >> $tmp/unallocated`.
- Notable variables and constants:
- `fssize=$(_small_fs_size_mb 300) # 200m phys/virt size`
- `fssize=3000`
- `agsize=`$XFS_INFO_PROG $loop_mnt | $SED_PROG -n 's/.*agsize=\(.*\) blks.*/\1/p'``
- `file1=$1`
- `file2=$2`
- `tmp_file=$tmp/sectors.tmp`
- `start=${line% *}`
- `end=${line#* }`
- `curr_start=${line% *}`
- `curr_end=${line#* }`
- `end=$curr_end`
- `start=$curr_start`

## Control Flow

- Capability gating runs first through `_require_test`, `_require_loop`, `_require_fstrim`, `_require_xfs_io_command "fiemap"`, `_require_fs_space $TEST_DIR 307200`, plus 6 more.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 142: echo $start $end`
- `line 149: echo $start $end`
- `line 181: echo -n "Generating garbage on loop..."`
- `line 195: echo "done."`
- `line 197: echo -n "Running fstrim..."`
- `line 199: echo "done."`
- `line 201: echo -n "Detecting interesting holes in image..."`
- `line 205: echo "done."`
- Key operational lines include:
- `line 14: _require_fstrim`
- `line 41: _unmount $loop_mnt &> /dev/null`
- `line 42: [ -n "$loop_dev" ] && _destroy_loop_device $loop_dev`
- `line 56: _unmount $loop_mnt`
- `line 60: $XFS_IO_PROG -F -c fiemap $img_file | grep hole | \`
- `line 62: _mount $loop_dev $loop_mnt`
- `line 69: _unmount $loop_mnt`
- `line 70: $DUMPE2FS_PROG $loop_dev 2>&1 | grep " Free blocks" | cut -d ":" -f2- | \`
- `line 83: _unmount $loop_mnt`
- `line 84: $XFS_DB_PROG -r -c "freesp -d" $loop_dev | $SED_PROG '/^.*from/,$d'| \`
- `line 89: local device_size=$($BTRFS_UTIL_PROG filesystem show --raw $loop_mnt 2>&1 \`
- `line 92: local nodesize=$($BTRFS_UTIL_PROG inspect-internal dump-super $loop_dev \`
- `line 96: $BTRFS_UTIL_PROG inspect-internal dump-tree -t extent $loop_dev >> $tmp/extent_dump`
- `line 97: if $BTRFS_UTIL_PROG inspect-internal dump-super $loop_dev |\`
- `line 99: $BTRFS_UTIL_PROG inspect-internal dump-tree -t block-group $loop_dev \`
- `line 108: $BTRFS_UTIL_PROG inspect-internal dump-tree -t dev $loop_dev \`

## State and Persistence Behavior

Uses the configured xfstests test area or an explicitly created loop/image mount rather than always reformatting the scratch device. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Synthetic block-device state can be introduced through device-mapper, loop, SCSI debug, or huge-device helpers and must be cleaned even on failure. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto trim fiemap`, common helper libraries (`./common/preamble`), and the golden-output file `sources/test-tools/xfstests/tests/generic/746.out` (5 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_test`, `_require_loop`, `_require_fstrim`, `_require_xfs_io_command "fiemap"`, `_require_fs_space $TEST_DIR 307200`, `_require_btrfs_command inspect-internal dump-super`, `_require_btrfs_command inspect-internal dump-tree`, `_require_fs_space $TEST_DIR 3145728`, plus 3 more.

## Risks and Edge Cases

- Discard/free-space validation is sensitive to filesystem-specific layout tools and block-to-sector conversion assumptions.

## Test Signals

The paired `.out` file has 5 line(s); its first visible signals are: 'QA output created by 746; Generating garbage on loop...done.; Running fstrim...done.; Detecting interesting holes in image...done.; Comparing holes to the reported space from FS...done.'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands, hang/race detection through background work, loops, or timeout windows. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/746 -->
