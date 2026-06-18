# Research Group subset-b-009551

This grouped report covers the requested xfstests overlay, perf, selftest, tmpfs, udf, and xfs source files. Each file section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/054 -->
# sources/test-tools/xfstests/tests/overlay/054

## Purpose
Regression test for overlayfs NFS-export file handles when a merge directory or its ancestors were created before directory indexes existed. It creates lower and upper merge state, encodes handles for the merge dir, child, grandchild, and sibling child, renames the non-indexed merge dir, and checks that stored handles still decode/read or fail only in the expected lower-ancestor cases.

## Important APIs, Types, And Functions
`_begin_fstest auto quick copyup redirect exportfs` declares xfstests groups/tags: auto, quick, copyup, redirect, exportfs. Imports `common/preamble`, `common/filter`. Local helpers: `create_test_files()`, `test_file_handles()`, `create_dirs()`, `mount_dirs()`, `unmount_dirs()`. Feature gates/fix annotations include `_fixed_by_kernel_commit`, `_require_scratch`, `_require_test_program`, `_require_scratch_overlay_features`. External helper programs used include `open_by_handle`, `$here/src/open_by_handle`, `$UMOUNT_PROG`.

## Control Flow
The test is a overlayfs export/file-handle regression test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 60: `mkdir -p $dir`; line 61: `$here/src/open_by_handle -cp $opt $dir $NUMFILES`; line 72: `$here/src/open_by_handle $* $dir $NUMFILES`; line 78: `_scratch_mkfs`; line 84: `_scratch_mount -o "index=on,nfs_export=on,redirect_dir=on"`; line 90: `$UMOUNT_PROG $SCRATCH_MNT`; line 100: `mkdir $upper/merged`; line 119: `mv $SCRATCH_MNT/merged $SCRATCH_MNT/merged.new/`.

## State And Persistence
State is kept in shell variables such as `lower`, `upper`, `work`, `NUMFILES`. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; overlayfs layer directories, mount options, xattrs, and scratch/test filesystem capabilities.

## Risks And Test Signals
Risks: file-handle behavior is sensitive to dcache warmth, inode identity, stale-handle semantics, and export feature availability; xattr and overlay metadata assertions depend on trusted/user xattr support and exact kernel on-disk semantics. Test signals: volatile paths, ids, device names, or tool output are filtered before golden comparison.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/054 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/055 -->
# sources/test-tools/xfstests/tests/overlay/055

## Purpose
Variant of overlay/054 for a lower redirected merge directory in a multi-lower, non-samefs setup. It verifies that file handles for lower directories below a lower-layer redirect are encoded with the right copy-up/index behavior and remain decodable after the redirected ancestor is renamed.

## Important APIs, Types, And Functions
`_begin_fstest auto quick copyup redirect exportfs nonsamefs` declares xfstests groups/tags: auto, quick, copyup, redirect, exportfs, nonsamefs. Imports `common/preamble`, `common/filter`. Local helpers: `_cleanup()`, `create_test_files()`, `test_file_handles()`, `create_dirs()`, `mount_dirs()`, `unmount_dirs()`. Feature gates/fix annotations include `_fixed_by_kernel_commit`, `_require_test`, `_require_test_program`, `_require_scratch_nocheck`, `_require_scratch_overlay_features`. External helper programs used include `$UMOUNT_PROG`, `open_by_handle`, `$here/src/open_by_handle`.

## Control Flow
The test is a overlayfs export/file-handle regression test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 36: `rm -f $tmp.*`; line 40: `$UMOUNT_PROG $SCRATCH_MNT 2>/dev/null`; line 74: `mkdir -p $dir`; line 75: `$here/src/open_by_handle -cp $opt $dir $NUMFILES`; line 86: `$here/src/open_by_handle $* $dir $NUMFILES`; line 93: `rm -rf $lower`; line 94: `mkdir $lower`; line 97: `_scratch_mkfs`; line 104: `_overlay_scratch_mount_dirs $middle:$lower $upper $work \`; line 112: `$UMOUNT_PROG $SCRATCH_MNT`.

## State And Persistence
State is kept in shell variables such as `lower`, `middle`, `upper`, `work`, `NUMFILES`. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; overlayfs layer directories, mount options, xattrs, and scratch/test filesystem capabilities.

## Risks And Test Signals
Risks: file-handle behavior is sensitive to dcache warmth, inode identity, stale-handle semantics, and export feature availability; xattr and overlay metadata assertions depend on trusted/user xattr support and exact kernel on-disk semantics. Test signals: volatile paths, ids, device names, or tool output are filtered before golden comparison.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/055 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/056 -->
# sources/test-tools/xfstests/tests/overlay/056

## Purpose
Validates `fsck.overlay` repair of missing `trusted.overlay.impure` xattrs. It removes impure xattrs from upper directories that contain origin targets, redirected children, or merge directories, runs non-destructive fsck with `-p`, and confirms the xattr is restored.

## Important APIs, Types, And Functions
`_begin_fstest auto quick fsck` declares xfstests groups/tags: auto, quick, fsck. Imports `common/preamble`, `common/filter`, `common/attr`. Local helpers: `make_redirect_dir()`, `remove_impure()`, `check_impure()`, `make_test_dirs()`. Feature gates/fix annotations include `_require_scratch_nocheck`, `_require_attrs`, `_require_command`. External helper programs used include `$FSCK_OVERLAY_PROG`, `$SETFATTR_PROG`, `$UMOUNT_PROG`.

## Control Flow
The test is a overlayfs xattr/redirect/whiteout behavior test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 23: `_scratch_mkfs`; line 31: `mkdir -p $target`; line 32: `$SETFATTR_PROG -n $OVL_XATTR_REDIRECT -v $value $target`; line 40: `$SETFATTR_PROG -x $OVL_XATTR_IMPURE $target`; line 62: `rm -rf $lowerdir $lowerdir2 $upperdir $workdir`; line 63: `mkdir -p $lowerdir $lowerdir2 $upperdir $workdir`; line 69: `mkdir $lowerdir/{testdir1,testdir2}`; line 70: `mkdir $upperdir/{testdir1,testdir2}`; line 71: `touch $lowerdir/testdir1/foo`; line 72: `mkdir $lowerdir/testdir2/subdir`.

## State And Persistence
State is kept in shell variables such as `OVL_XATTR_IMPURE_VAL`, `value`, `lowerdir`, `lowerdir2`, `upperdir`, `workdir`. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; overlayfs layer directories, mount options, xattrs, and scratch/test filesystem capabilities.

## Risks And Test Signals
Risks: xattr and overlay metadata assertions depend on trusted/user xattr support and exact kernel on-disk semantics. Test signals: exit status and golden stdout comparison.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/056 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/057 -->
# sources/test-tools/xfstests/tests/overlay/057

## Purpose
Checks absolute redirect lookup through an opaque ancestor. The setup creates an opaque middle-layer parent and a child redirect to a lower layer; the overlay should still merge and list the redirected lower content before and after a mount cycle.

## Important APIs, Types, And Functions
`_begin_fstest auto quick redirect` declares xfstests groups/tags: auto, quick, redirect. Imports `common/preamble`, `common/filter`. Feature gates/fix annotations include `_require_scratch_nocheck`, `_require_scratch_overlay_features`. External helper programs used include `$UMOUNT_PROG`.

## Control Flow
The test is a overlayfs xattr/redirect/whiteout behavior test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 34: `_scratch_mkfs`; line 43: `mkdir -p $lowerdir $lowerdir2 $upperdir $workdir $workdir2`; line 44: `mkdir -p $lowerdir/origin`; line 45: `touch $lowerdir/origin/foo`; line 46: `_overlay_scratch_mount_dirs $lowerdir $lowerdir2 $workdir2 -o redirect_dir=on`; line 49: `mkdir $SCRATCH_MNT/pure`; line 50: `mv $SCRATCH_MNT/origin $SCRATCH_MNT/pure/redirect`; line 51: `$UMOUNT_PROG $SCRATCH_MNT`; line 52: `_overlay_scratch_mount_dirs $lowerdir2:$lowerdir $upperdir $workdir -o redirect_dir=on`; line 53: `mv $SCRATCH_MNT/pure/redirect $SCRATCH_MNT/redirect`.

## State And Persistence
State is kept in shell variables such as `lowerdir`, `lowerdir2`, `upperdir`, `workdir`, `workdir2`. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; overlayfs layer directories, mount options, xattrs, and scratch/test filesystem capabilities.

## Risks And Test Signals
Risks: xattr and overlay metadata assertions depend on trusted/user xattr support and exact kernel on-disk semantics. Test signals: exit status and golden stdout comparison.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/057 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/058 -->
# sources/test-tools/xfstests/tests/overlay/058

## Purpose
Exercises overlayfs NFS-export decoding with warm and cold dentry caches, including disconnected non-directory dentries kept alive by background `open_by_handle` sleepers. It verifies upper and lower file handles before and after cache dropping.

## Important APIs, Types, And Functions
`_begin_fstest auto quick exportfs` declares xfstests groups/tags: auto, quick, exportfs. Imports `common/preamble`, `common/filter`. Local helpers: `_cleanup()`, `create_test_files()`, `test_file_handles()`. Feature gates/fix annotations include `_require_scratch`, `_require_test_program`, `_require_scratch_overlay_features`. External helper programs used include `open_by_handle`, `$here/src/open_by_handle`.

## Control Flow
The test is a overlayfs export/file-handle regression test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 29: `rm -f $tmp.*`; line 57: `mkdir -p $dir`; line 58: `$here/src/open_by_handle -cp $opt $dir $NUMFILES`; line 69: `$here/src/open_by_handle $* $dir $NUMFILES`; line 73: `_scratch_mkfs`; line 76: `_scratch_mount -o "index=on,nfs_export=on"`; line 91: `_scratch_cycle_mount "index=on,nfs_export=on"`.

## State And Persistence
State is kept in shell variables such as `lower`, `upper`, `work`, `NUMFILES`, `pids`. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; overlayfs layer directories, mount options, xattrs, and scratch/test filesystem capabilities.

## Risks And Test Signals
Risks: file-handle behavior is sensitive to dcache warmth, inode identity, stale-handle semantics, and export feature availability. Test signals: volatile paths, ids, device names, or tool output are filtered before golden comparison.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/058 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/059 -->
# sources/test-tools/xfstests/tests/overlay/059

## Purpose
Checks that duplicated upper origin references to the same lower file do not produce identical overlay `st_dev/st_ino` for distinct files. The failure signal is `diff` thinking diverged copies are the same.

## Important APIs, Types, And Functions
`_begin_fstest auto quick copyup` declares xfstests groups/tags: auto, quick, copyup. Imports `common/preamble`, `common/filter`. Local helpers: `create_origin_ref()`. Feature gates/fix annotations include `_require_scratch_nocheck`, `_require_scratch_feature`. External helper programs used include `$UMOUNT_PROG`.

## Control Flow
The test is a overlayfs metadata-only copy-up behavior test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 28: `touch $lowerdir/origin`; line 33: `_scratch_mount -o redirect_dir=on`; line 34: `mv $SCRATCH_MNT/origin $SCRATCH_MNT/$ref`; line 36: `$UMOUNT_PROG $SCRATCH_MNT`; line 46: `_scratch_mkfs`; line 54: `cp -a $upperdir/ref1 $upperdir/ref2`; line 61: `_scratch_mount -o redirect_dir=on`; line 65: `diff -q $SCRATCH_MNT/ref1 $SCRATCH_MNT/ref2 &>/dev/null && \`.

## State And Persistence
State is kept in shell variables such as `upperdir`, `lowerdir`. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; overlayfs layer directories, mount options, xattrs, and scratch/test filesystem capabilities.

## Risks And Test Signals
Risks: xattr and overlay metadata assertions depend on trusted/user xattr support and exact kernel on-disk semantics. Test signals: quiet success usually prints `Silence is golden`; content or output comparison is a primary failure signal.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/059 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/060 -->
# sources/test-tools/xfstests/tests/overlay/060

## Purpose
Comprehensive metadata-only copy-up test. It covers lower files, midlayer metacopy files, rename redirects, link redirects, hardlink absolute redirects, read-only follow of lowerdata, and transition from metacopy xattr to full data copy-up after fallocate.

## Important APIs, Types, And Functions
`_begin_fstest auto quick metacopy redirect prealloc` declares xfstests groups/tags: auto, quick, metacopy, redirect, prealloc. Imports `common/preamble`, `common/filter`, `common/attr`. Local helpers: `check_metacopy()`, `check_redirect()`, `check_file_size()`, `check_file_blocks()`, `check_file_contents()`, `check_file_size_contents()`, `mount_overlay()`, `mount_ro_overlay()`, `umount_overlay()`, `test_common()`, `create_basic_files()`, `create_lower_link()`, `prepare_midlayer()`. Feature gates/fix annotations include `_require_scratch_nocheck`, `_require_scratch_overlay_features`, `_require_xfs_io_command`. External helper programs used include `$UMOUNT_PROG`, `$XFS_IO_PROG`.

## Control Flow
The test is a overlayfs data-only lower-layer behavior test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 23: `_scratch_mkfs`; line 121: `_overlay_scratch_mount_dirs "$_lowerdir" $upperdir $workdir -o redirect_dir=on,index=on,metacopy=on`; line 128: `_overlay_scratch_mount_dirs "$_lowerdir" "-" "-" -o ro,redirect_dir=follow,metacopy=on`; line 133: `$UMOUNT_PROG $SCRATCH_MNT`; line 155: `chmod 400 $SCRATCH_MNT/$_target`; line 163: `$XFS_IO_PROG -c "falloc 0 1" $SCRATCH_MNT/$_target >> $seqres.full`; line 173: `_scratch_mkfs`; line 174: `mkdir -p $lowerdir/subdir $lowerdir2 $upperdir $workdir $workdir2`; line 175: `mkdir -p $upperdir/$udirname`; line 177: `chmod 600 $lowerdir/$lowername`.

## State And Persistence
State is kept in shell variables such as `lowername`, `lowerlink`, `lowerdata`, `lowersize`, `lowerblocks`, `udirname`, `ufile`, `out_f`, `target_f`, `msg`, `value`, `actual_size`, and 6 more. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; overlayfs layer directories, mount options, xattrs, and scratch/test filesystem capabilities.

## Risks And Test Signals
Risks: xattr and overlay metadata assertions depend on trusted/user xattr support and exact kernel on-disk semantics. Test signals: volatile paths, ids, device names, or tool output are filtered before golden comparison.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/060 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/061 -->
# sources/test-tools/xfstests/tests/overlay/061

## Purpose
Demonstrates the known overlayfs mmap copy-up incoherency pattern using `xfs_io`: one read-only shared mapping and one writable shared mapping of the same file can observe different data until remount; the test documents and checks persistence after a mount cycle.

## Important APIs, Types, And Functions
`_begin_fstest posix copyup mmap` declares xfstests groups/tags: posix, copyup, mmap. Imports `common/preamble`, `common/filter`. Local helpers: `filter_xfs_io_mmap()`. Feature gates/fix annotations include `_require_scratch`, `_require_xfs_io_command`. External helper programs used include `$XFS_IO_PROG`.

## Control Flow
The test is a overlayfs regression test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 26: `_scratch_mkfs >>$seqres.full 2>&1`; line 30: `mkdir -p $lowerdir`; line 33: `_scratch_mount`; line 48: `$XFS_IO_PROG -r $SCRATCH_MNT/foo \`; line 59: `_scratch_cycle_mount`; line 63: `$XFS_IO_PROG -r $SCRATCH_MNT/foo \`.

## State And Persistence
State is kept in shell variables such as `lowerdir`. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; overlayfs layer directories, mount options, xattrs, and scratch/test filesystem capabilities.

## Risks And Test Signals
Risks: main risk is environmental: missing helper binaries, unsupported mount options, insufficient scratch space, or expected-output drift. Test signals: volatile paths, ids, device names, or tool output are filtered before golden comparison.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/061 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/062 -->
# sources/test-tools/xfstests/tests/overlay/062

## Purpose
Regression test for decoding file handles from multiple lower layers on the same filesystem when the underlying lower dentry is pinned in dcache by a bind mount and is not from the uppermost lower layer.

## Important APIs, Types, And Functions
`_begin_fstest auto quick exportfs` declares xfstests groups/tags: auto, quick, exportfs. Imports `common/preamble`, `common/filter`. Local helpers: `_cleanup()`, `create_test_files()`, `test_file_handles()`. Feature gates/fix annotations include `_require_scratch`, `_require_test_program`, `_require_scratch_overlay_features`. External helper programs used include `$UMOUNT_PROG`, `open_by_handle`, `$here/src/open_by_handle`, `$MOUNT_PROG`.

## Control Flow
The test is a overlayfs export/file-handle regression test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 20: `rm -f $tmp.*`; line 21: `$UMOUNT_PROG $lowertestdir`; line 41: `mkdir -p $dir`; line 42: `$here/src/open_by_handle -cwp $dir $NUMFILES`; line 50: `$here/src/open_by_handle -rp $dir $NUMFILES`; line 53: `_scratch_mkfs`; line 63: `$MOUNT_PROG --bind $lowertestdir $lowertestdir`; line 66: `_overlay_scratch_mount_opts \`.

## State And Persistence
State is kept in shell variables such as `NUMFILES`, `lower`, `lower2`, `lowertestdir`. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; overlayfs layer directories, mount options, xattrs, and scratch/test filesystem capabilities.

## Risks And Test Signals
Risks: file-handle behavior is sensitive to dcache warmth, inode identity, stale-handle semantics, and export feature availability; xattr and overlay metadata assertions depend on trusted/user xattr support and exact kernel on-disk semantics. Test signals: quiet success usually prints `Silence is golden`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/062 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/063 -->
# sources/test-tools/xfstests/tests/overlay/063

## Purpose
Whiteout/negative-dentry regression test. It removes a lower file through overlay to create a whiteout, populates a cached negative dentry, deletes the upper whiteout behind the overlay, and creates a directory at the same name to ensure no crash.

## Important APIs, Types, And Functions
`_begin_fstest auto quick whiteout` declares xfstests groups/tags: auto, quick, whiteout. Imports `common/preamble`, `common/filter`. Feature gates/fix annotations include `_fixed_by_kernel_commit`, `_require_scratch`. External helper programs used include `$UMOUNT_PROG`.

## Control Flow
The test is a overlayfs xattr/redirect/whiteout behavior test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 24: `_scratch_mkfs`; line 29: `mkdir -p $lowerdir`; line 30: `touch ${lowerdir}/file`; line 32: `_scratch_mount`; line 35: `rm ${SCRATCH_MNT}/file`; line 39: `rm ${upperdir}/file`; line 40: `mkdir ${SCRATCH_MNT}/file > /dev/null 2>&1`; line 43: `$UMOUNT_PROG $SCRATCH_MNT`.

## State And Persistence
State is kept in shell variables such as `lowerdir`, `upperdir`. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; overlayfs layer directories, mount options, xattrs, and scratch/test filesystem capabilities.

## Risks And Test Signals
Risks: xattr and overlay metadata assertions depend on trusted/user xattr support and exact kernel on-disk semantics. Test signals: quiet success usually prints `Silence is golden`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/063 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/064 -->
# sources/test-tools/xfstests/tests/overlay/064

## Purpose
Verifies that `cap_setuid` file capabilities survive both ordinary copy-up and metacopy-triggered copy-up under overlayfs.

## Important APIs, Types, And Functions
`_begin_fstest auto quick copyup` declares xfstests groups/tags: auto, quick, copyup. Imports `common/preamble`, `common/filter`. Feature gates/fix annotations include `_require_scratch`, `_require_command`, `_require_scratch_overlay_features`. External helper programs used include `$SETCAP_PROG`, `$GETCAP_PROG`, `xfs_io`, `$XFS_IO_PROG`.

## Control Flow
The test is a overlayfs metadata-only copy-up behavior test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 21: `_scratch_mkfs`; line 29: `$SETCAP_PROG cap_setuid+ep ${lowerdir}/file1`; line 30: `$SETCAP_PROG cap_setuid+ep ${lowerdir}/file2`; line 32: `_scratch_mount "-o metacopy=on"`; line 37: `$XFS_IO_PROG -c "stat" ${SCRATCH_MNT}/file1 >>$seqres.full`; line 43: `chmod 000 ${SCRATCH_MNT}/file2`; line 46: `$XFS_IO_PROG -c "stat" ${SCRATCH_MNT}/file2 >>$seqres.full`.

## State And Persistence
State is kept in shell variables such as `lowerdir`. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; overlayfs layer directories, mount options, xattrs, and scratch/test filesystem capabilities.

## Risks And Test Signals
Risks: xattr and overlay metadata assertions depend on trusted/user xattr support and exact kernel on-disk semantics. Test signals: volatile paths, ids, device names, or tool output are filtered before golden comparison.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/064 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/065 -->
# sources/test-tools/xfstests/tests/overlay/065

## Purpose
Mount and lookup regression test for overlapping overlay layers. It checks same/overlapping upper, work, and lower directories, duplicate lower layers, overlap with another mounted overlay upper/work dir with index on/off, and post-mount overlap detection.

## Important APIs, Types, And Functions
`_begin_fstest auto quick mount` declares xfstests groups/tags: auto, quick, mount. Imports `common/preamble`, `common/filter`. Local helpers: `_cleanup()`. Feature gates/fix annotations include `_fixed_in_kernel_version`, `_fixed_by_kernel_commit`, `_require_scratch_nocheck`, `_require_scratch_feature`. External helper programs used include `$UMOUNT_PROG`.

## Control Flow
The test is a overlayfs mount option validation test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 32: `rm -f $tmp.*`; line 33: `$UMOUNT_PROG $mnt2 2>/dev/null`; line 49: `_scratch_mkfs`; line 60: `mkdir -p $lowerdir/lower $upperdir $workdir`; line 64: `_overlay_scratch_mount_dirs $upperdir $upperdir $workdir \`; line 66: `$UMOUNT_PROG $SCRATCH_MNT 2>/dev/null`; line 70: `rm -rf $upperdir $workdir`; line 71: `mkdir $upperdir $workdir`; line 76: `_overlay_scratch_mount_dirs $workdir $upperdir $workdir \`; line 78: `$UMOUNT_PROG $SCRATCH_MNT 2>/dev/null`.

## State And Persistence
State is kept in shell variables such as `basedir`, `lowerdir`, `upperdir`, `workdir`, `upperdir2`, `workdir2`, `mnt2`. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; overlayfs layer directories, mount options, xattrs, and scratch/test filesystem capabilities.

## Risks And Test Signals
Risks: main risk is environmental: missing helper binaries, unsupported mount options, insufficient scratch space, or expected-output drift. Test signals: volatile paths, ids, device names, or tool output are filtered before golden comparison.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/065 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/066 -->
# sources/test-tools/xfstests/tests/overlay/066

## Purpose
Sparse-file copy-up coverage. It creates empty, patterned-hole, and random-hole lower files of varied sizes, triggers copy-up by opening through overlay, and compares upper and lower trees while logging filefrag details on mismatch.

## Important APIs, Types, And Functions
`_begin_fstest auto quick copyup fiemap` declares xfstests groups/tags: auto, quick, copyup, fiemap. Imports `common/preamble`, `common/filter`. Local helpers: `do_cmd()`. Feature gates/fix annotations include `_require_test`, `_require_scratch`, `_require_fs_space`. External helper programs used include `$XFS_IO_PROG`, `$FILEFRAG_PROG`.

## Control Flow
The test is a overlayfs regression test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 23: `_scratch_mkfs`; line 131: `_scratch_mount`; line 142: `diff -qr ${upperdir} ${lowerdir} | tee -a $seqres.full`.

## State And Persistence
State is kept in shell variables such as `lowerdir`, `upperdir`, `testfile`, `file_size`, `min_iosize`, `max_iosize`, `iosize`, `max_pos`, `pos`, `min_hole`, `max_hole`. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; overlayfs layer directories, mount options, xattrs, and scratch/test filesystem capabilities.

## Risks And Test Signals
Risks: space/quota tests are sensitive to scratch capacity, mkfs geometry, and background reclaim. Test signals: quiet success usually prints `Silence is golden`; content or output comparison is a primary failure signal.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/066 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/067 -->
# sources/test-tools/xfstests/tests/overlay/067

## Purpose
Non-samefs inode identity regression test. It ensures a middle-layer file on the same filesystem as upper does not export a real inode identity that causes `diff` to confuse the copied-up overlay file with the original lower file.

## Important APIs, Types, And Functions
`_begin_fstest auto quick copyup nonsamefs` declares xfstests groups/tags: auto, quick, copyup, nonsamefs. Imports `common/preamble`, `common/filter`. Feature gates/fix annotations include `_fixed_by_kernel_commit`, `_require_scratch_nocheck`, `_require_test`. External helper programs used include `$UMOUNT_PROG`.

## Control Flow
The test is a overlayfs regression test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 36: `rm -rf $lower`; line 37: `mkdir $lower`; line 39: `_scratch_mkfs >>$seqres.full 2>&1`; line 50: `_overlay_scratch_mount_dirs $middle:$lower $upper $work -o xino=off || \`; line 53: `stat $realfile >>$seqres.full`; line 54: `stat $testfile >>$seqres.full`; line 59: `stat $testfile >>$seqres.full`; line 62: `diff -q $realfile $testfile >>$seqres.full &&`; line 67: `stat $testfile >>$seqres.full`; line 70: `diff -q $realfile $testfile >>$seqres.full &&`.

## State And Persistence
State is kept in shell variables such as `lower`, `middle`, `upper`, `work`, `realfile`, `testfile`. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; overlayfs layer directories, mount options, xattrs, and scratch/test filesystem capabilities.

## Risks And Test Signals
Risks: uses disruptive kernel/storage state such as cache dropping, shutdown, dm-error, error injection, or crash/hang triggers. Test signals: quiet success usually prints `Silence is golden`; content or output comparison is a primary failure signal; unsupported environments are skipped with `_notrun`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/067 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/068 -->
# sources/test-tools/xfstests/tests/overlay/068

## Purpose
Large nested-overlay file-handle test for samefs layers. It mounts overlay-on-overlay with NFS export enabled and exercises encode/decode/read/write across copy-up, unlink, hardlink, rename, directory rename, stored handle input/output, and dcache-pinned ancestors.

## Important APIs, Types, And Functions
`_begin_fstest auto quick copyup hardlink exportfs nested` declares xfstests groups/tags: auto, quick, copyup, hardlink, exportfs, nested. Imports `common/preamble`, `common/filter`. Local helpers: `_cleanup()`, `create_test_files()`, `test_file_handles()`, `create_dirs()`, `mount_dirs()`, `unmount_dirs()`. Feature gates/fix annotations include `_require_scratch`, `_require_test_program`, `_require_scratch_overlay_features`. External helper programs used include `$UMOUNT_PROG`, `open_by_handle`, `$here/src/open_by_handle`.

## Control Flow
The test is a overlayfs export/file-handle regression test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 29: `rm -f $tmp.*`; line 31: `$UMOUNT_PROG $mnt2 2>/dev/null`; line 62: `$here/src/open_by_handle -cp $opt $dir $NUMFILES`; line 73: `$here/src/open_by_handle $* $dir $NUMFILES`; line 80: `_scratch_mkfs`; line 83: `mkdir -p $upper2 $work2 $mnt2`; line 90: `_scratch_mount -o "index=on,nfs_export=on,redirect_dir=on"`; line 93: `_overlay_mount_dirs $SCRATCH_MNT $upper2 $work2 overlay2 $mnt2 \`; line 96: `_check_overlay_feature nfs_export overlay2 $mnt2`; line 103: `$UMOUNT_PROG $mnt2`.

## State And Persistence
State is kept in shell variables such as `upper2`, `work2`, `mnt2`, `lowerdir`, `upperdir`, `lowertestdir`, `uppertestdir`, `NUMFILES`. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; overlayfs layer directories, mount options, xattrs, and scratch/test filesystem capabilities.

## Risks And Test Signals
Risks: file-handle behavior is sensitive to dcache warmth, inode identity, stale-handle semantics, and export feature availability; xattr and overlay metadata assertions depend on trusted/user xattr support and exact kernel on-disk semantics. Test signals: volatile paths, ids, device names, or tool output are filtered before golden comparison; unsupported environments are skipped with `_notrun`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/068 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/069 -->
# sources/test-tools/xfstests/tests/overlay/069

## Purpose
Non-samefs variant of overlay/068. The lower overlay lower layer lives on the test filesystem while upper/work live on scratch; the nested overlay then repeats the same file-handle, copy-up, link, unlink, move, and rename scenarios.

## Important APIs, Types, And Functions
`_begin_fstest auto quick copyup hardlink exportfs nested nonsamefs` declares xfstests groups/tags: auto, quick, copyup, hardlink, exportfs, nested, nonsamefs. Imports `common/preamble`, `common/filter`. Local helpers: `_cleanup()`, `create_test_files()`, `test_file_handles()`, `create_dirs()`, `mount_dirs()`, `unmount_dirs()`. Feature gates/fix annotations include `_require_test`, `_require_scratch_nocheck`, `_require_test_program`, `_require_scratch_overlay_features`. External helper programs used include `$UMOUNT_PROG`, `open_by_handle`, `$here/src/open_by_handle`.

## Control Flow
The test is a overlayfs export/file-handle regression test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 29: `rm -f $tmp.*`; line 31: `$UMOUNT_PROG $mnt2 2>/dev/null`; line 68: `$here/src/open_by_handle -cp $opt $dir $NUMFILES`; line 79: `$here/src/open_by_handle $* $dir $NUMFILES`; line 86: `_scratch_mkfs`; line 89: `rm -rf $lower $upper2 $work2 $mnt2`; line 90: `mkdir $lower $upper2 $work2 $mnt2`; line 97: `_overlay_mount_dirs $lower $upper $work overlay1 $SCRATCH_MNT \`; line 101: `_overlay_mount_dirs $SCRATCH_MNT $upper2 $work2 overlay2 $mnt2 \`; line 104: `_check_overlay_feature nfs_export overlay2 $mnt2`.

## State And Persistence
State is kept in shell variables such as `lower`, `upper`, `work`, `upper2`, `work2`, `mnt2`, `lowerdir`, `upperdir`, `lowertestdir`, `uppertestdir`, `NUMFILES`. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; overlayfs layer directories, mount options, xattrs, and scratch/test filesystem capabilities.

## Risks And Test Signals
Risks: file-handle behavior is sensitive to dcache warmth, inode identity, stale-handle semantics, and export feature availability; xattr and overlay metadata assertions depend on trusted/user xattr support and exact kernel on-disk semantics. Test signals: volatile paths, ids, device names, or tool output are filtered before golden comparison; unsupported environments are skipped with `_notrun`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/069 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/070 -->
# sources/test-tools/xfstests/tests/overlay/070

## Purpose
Nested samefs xino/stable-inode regression test. It records inode numbers for directories, files, symlinks, links, device nodes, fifo, and socket, copies them up, renames them, drops caches, cycles mounts, and verifies `st_ino`, readdir `d_ino`, and `/proc/locks` identity remain consistent.

## Important APIs, Types, And Functions
`_begin_fstest auto quick copyup redirect nested` declares xfstests groups/tags: auto, quick, copyup, redirect, nested. Imports `common/preamble`, `common/filter`. Local helpers: `_cleanup()`, `create_dirs()`, `mount_dirs()`, `unmount_dirs()`, `create_test_files()`, `record_inode_numbers()`, `check_inode_numbers()`. Feature gates/fix annotations include `_fixed_in_kernel_version`, `_require_scratch_nocheck`, `_require_test_program`, `_require_command`, `_require_scratch_overlay_features`, `_require_loop`. External helper programs used include `$UMOUNT_PROG`, `af_unix`, `t_dir_type`, `$FLOCK_PROG`, `$XFS_IO_PROG`, `$here/src/af_unix`, `$here/src/t_dir_type`.

## Control Flow
The test is a overlayfs export/file-handle regression test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 27: `rm -f $tmp.*`; line 29: `$UMOUNT_PROG $mnt2 2>/dev/null`; line 63: `_scratch_mkfs`; line 66: `mkdir -p $upper2 $work2 $mnt2`; line 69: `$XFS_IO_PROG -f -c "truncate 128k" $lower/img >> $seqres.full 2>&1`; line 77: `_scratch_mount -o "index=on,nfs_export=on"`; line 85: `_overlay_mount_dirs $SCRATCH_MNT $upper2 $work2 overlay2 $mnt2 \`; line 96: `$UMOUNT_PROG $mnt2`; line 97: `_overlay_check_dirs $SCRATCH_MNT $upper2 $work2 \`; line 101: `$UMOUNT_PROG $SCRATCH_MNT`.

## State And Persistence
State is kept in shell variables such as `lower`, `upper`, `work`, `upper2`, `work2`, `mnt2`, `lowerdir`, `upperdir`, `lowertestdir`, `uppertestdir`, `loopdev`, `FILES`, and 1 more. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; overlayfs layer directories, mount options, xattrs, and scratch/test filesystem capabilities.

## Risks And Test Signals
Risks: uses disruptive kernel/storage state such as cache dropping, shutdown, dm-error, error injection, or crash/hang triggers; file-handle behavior is sensitive to dcache warmth, inode identity, stale-handle semantics, and export feature availability; xattr and overlay metadata assertions depend on trusted/user xattr support and exact kernel on-disk semantics. Test signals: quiet success usually prints `Silence is golden`; content or output comparison is a primary failure signal; unsupported environments are skipped with `_notrun`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/070 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/071 -->
# sources/test-tools/xfstests/tests/overlay/071

## Purpose
Nested non-samefs xino/stable-inode variant. It excludes directories because nested xino cannot guarantee persistent directory inode numbers, then validates inode identity for non-directory file types across copy-up, rename, cache drop, and mount cycle.

## Important APIs, Types, And Functions
`_begin_fstest auto quick copyup redirect nested nonsamefs` declares xfstests groups/tags: auto, quick, copyup, redirect, nested, nonsamefs. Imports `common/preamble`, `common/filter`. Local helpers: `_cleanup()`, `create_dirs()`, `mount_dirs()`, `unmount_dirs()`, `create_test_files()`, `record_inode_numbers()`, `check_inode_numbers()`. Feature gates/fix annotations include `_fixed_in_kernel_version`, `_require_test`, `_require_scratch_nocheck`, `_require_test_program`, `_require_command`, `_require_scratch_overlay_features`, `_require_loop`. External helper programs used include `$UMOUNT_PROG`, `af_unix`, `t_dir_type`, `$FLOCK_PROG`, `$XFS_IO_PROG`, `$here/src/af_unix`, `$here/src/t_dir_type`.

## Control Flow
The test is a overlayfs export/file-handle regression test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 30: `rm -f $tmp.*`; line 32: `$UMOUNT_PROG $mnt2 2>/dev/null`; line 68: `_scratch_mkfs`; line 71: `rm -rf $lower $upper2 $work2 $mnt2`; line 72: `mkdir $lower $upper2 $work2 $mnt2`; line 75: `$XFS_IO_PROG -f -c "truncate 128k" $lower/img >> $seqres.full 2>&1`; line 83: `_overlay_mount_dirs $lower $upper $work overlay1 $SCRATCH_MNT \`; line 95: `_overlay_mount_dirs $SCRATCH_MNT $upper2 $work2 overlay2 $mnt2 \`; line 106: `$UMOUNT_PROG $mnt2`; line 107: `_overlay_check_dirs $SCRATCH_MNT $upper2 $work2 \`.

## State And Persistence
State is kept in shell variables such as `lower`, `upper`, `work`, `upper2`, `work2`, `mnt2`, `lowerdir`, `upperdir`, `lowertestdir`, `uppertestdir`, `loopdev`, `FILES`, and 1 more. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; overlayfs layer directories, mount options, xattrs, and scratch/test filesystem capabilities.

## Risks And Test Signals
Risks: uses disruptive kernel/storage state such as cache dropping, shutdown, dm-error, error injection, or crash/hang triggers; file-handle behavior is sensitive to dcache warmth, inode identity, stale-handle semantics, and export feature availability; xattr and overlay metadata assertions depend on trusted/user xattr support and exact kernel on-disk semantics. Test signals: quiet success usually prints `Silence is golden`; content or output comparison is a primary failure signal; unsupported environments are skipped with `_notrun`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/071 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/072 -->
# sources/test-tools/xfstests/tests/overlay/072

## Purpose
Hardlink nlink regression test for upper hardlinks added behind a mounted overlay. It verifies overlay inode link counts do not underflow to zero when unaccounted hardlinks are later removed through the overlay.

## Important APIs, Types, And Functions
`_begin_fstest auto quick copyup hardlink` declares xfstests groups/tags: auto, quick, copyup, hardlink. Imports `common/preamble`, `common/filter`. Feature gates/fix annotations include `_fixed_by_kernel_commit`, `_require_scratch`.

## Control Flow
The test is a overlayfs regression test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 36: `_scratch_mkfs`; line 39: `mkdir -p $upperdir`; line 40: `touch $upperdir/0`; line 41: `ln $upperdir/0 $upperdir/1`; line 43: `_scratch_mount`; line 46: `stat -c '%h' $SCRATCH_MNT/0`; line 50: `ln $upperdir/0 $upperdir/2`; line 51: `ln $upperdir/0 $upperdir/3`; line 55: `rm $SCRATCH_MNT/2`; line 56: `rm $SCRATCH_MNT/3`.

## State And Persistence
State is kept in shell variables such as `upperdir`. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; overlayfs layer directories, mount options, xattrs, and scratch/test filesystem capabilities.

## Risks And Test Signals
Risks: main risk is environmental: missing helper binaries, unsupported mount options, insufficient scratch space, or expected-output drift. Test signals: quiet success usually prints `Silence is golden`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/072 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/073 -->
# sources/test-tools/xfstests/tests/overlay/073

## Purpose
Whiteout inode sharing test. It deletes lower files/dirs through overlay, expects shared whiteout hardlinks in upper/index, and validates a single temporary whiteout object rather than one inode per whiteout.

## Important APIs, Types, And Functions
`_begin_fstest auto quick whiteout` declares xfstests groups/tags: auto, quick, whiteout. Imports `common/preamble`, `common/filter`. Local helpers: `make_lower_files()`, `make_whiteout_files()`, `check_whiteout_files()`, `run_test_case()`. Feature gates/fix annotations include `_require_scratch`, `_require_scratch_overlay_features`.

## Control Flow
The test is a overlayfs export/file-handle regression test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 38: `mkdir $lowerdir/dir`; line 40: `touch $lowerdir/${name} &>/dev/null`; line 53: `rm $SCRATCH_MNT/* &>/dev/null`; line 81: `_scratch_mkfs`; line 85: `_scratch_mount -o "index=on,nfs_export=off"`; line 88: `_scratch_unmount`.

## State And Persistence
State is kept in shell variables such as `lowerdir`, `upperdir`, `workdir`, `file_count`, `link_count`. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; overlayfs layer directories, mount options, xattrs, and scratch/test filesystem capabilities.

## Risks And Test Signals
Risks: file-handle behavior is sensitive to dcache warmth, inode identity, stale-handle semantics, and export feature availability; xattr and overlay metadata assertions depend on trusted/user xattr support and exact kernel on-disk semantics. Test signals: quiet success usually prints `Silence is golden`; unsupported environments are skipped with `_notrun`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/073 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/074 -->
# sources/test-tools/xfstests/tests/overlay/074

## Purpose
Dangerous malformed file-handle regression test. It verifies handle-size query support, validates a normal exported handle, then crafts malformed v0/v1 overlay file handles and expects open-by-handle failure instead of kernel crash or bounds warning.

## Important APIs, Types, And Functions
`_begin_fstest auto quick exportfs dangerous` declares xfstests groups/tags: auto, quick, exportfs, dangerous. Imports `common/preamble`, `common/filter`. Feature gates/fix annotations include `_fixed_by_kernel_commit`, `_require_scratch`, `_require_test_program`, `_require_scratch_overlay_features`. External helper programs used include `open_by_handle`, `$here/src/open_by_handle`, `$XFS_IO_PROG`.

## Control Flow
The test is a overlayfs export/file-handle regression test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 34: `_scratch_mkfs`; line 35: `_scratch_mount -o "index=on,nfs_export=on"`; line 40: `$here/src/open_by_handle -cp $testdir`; line 43: `$here/src/open_by_handle -pz $testdir`; line 46: `$here/src/open_by_handle -o $tmp.file_handle $testdir`; line 49: `$here/src/open_by_handle -i $tmp.file_handle $testdir`; line 58: `cp $tmp.file_handle $tmp.file_handle_v0`; line 59: `$XFS_IO_PROG -c "pwrite -S 0 0 8" -c "pwrite -S 1 0 1" -c "pwrite -S 0xfb 4 1" \`; line 65: `cp $tmp.file_handle $tmp.file_handle_v1`; line 66: `$XFS_IO_PROG -c "pwrite -S 0 0 8" -c "pwrite -S 1 0 1" -c "pwrite -S 0xf8 4 1" \`.

## State And Persistence
State is kept in shell variables such as `testdir`. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; overlayfs layer directories, mount options, xattrs, and scratch/test filesystem capabilities.

## Risks And Test Signals
Risks: marked dangerous, so it can crash, hang, or exercise kernel failure paths; file-handle behavior is sensitive to dcache warmth, inode identity, stale-handle semantics, and export feature availability. Test signals: quiet success usually prints `Silence is golden`; content or output comparison is a primary failure signal; explicit `_fail` calls mark invariant violations.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/074 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/075 -->
# sources/test-tools/xfstests/tests/overlay/075

## Purpose
Runs `t_immutable` against immutable and append-only files prepared in the lower layer. It observes behavior before copy-up, triggers directory/file copy-up, cycles the mount, and verifies flags lost during copy-up do not leave undeletable overlay state.

## Important APIs, Types, And Functions
`_begin_fstest auto quick perms` declares xfstests groups/tags: auto, quick, perms. Imports `common/preamble`, `common/filter`. Local helpers: `_cleanup()`. Feature gates/fix annotations include `_require_chattr`, `_require_test_program`, `_require_scratch`. External helper programs used include `t_immutable`, `$here/src/t_immutable`.

## Control Flow
The test is a overlayfs regression test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 30: `rm -f $tmp.*`; line 41: `_scratch_mkfs`; line 44: `mkdir -p $lowerdir`; line 45: `mkdir -p $upperdir`; line 56: `mkdir $dir/subdir`; line 61: `_scratch_mount`; line 72: `touch $dir/subdir`; line 80: `touch $file > /dev/null 2>&1`; line 85: `_scratch_cycle_mount`; line 89: `rm -rf $SCRATCH_MNT/testdir.before`.

## State And Persistence
State is kept in shell variables such as `timmutable`, `lowerdir`, `upperdir`. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; overlayfs layer directories, mount options, xattrs, and scratch/test filesystem capabilities.

## Risks And Test Signals
Risks: main risk is environmental: missing helper binaries, unsupported mount options, insufficient scratch space, or expected-output drift. Test signals: unsupported environments are skipped with `_notrun`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/075 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/076 -->
# sources/test-tools/xfstests/tests/overlay/076

## Purpose
Dangerous regression test for directory `chattr +i` ioctl deadlock. It mounts a lower directory through overlay and runs `chattr +i`; failure is acceptable on unsupported kernels, but hanging indicates the v5.10 regression.

## Important APIs, Types, And Functions
`_begin_fstest auto quick perms dangerous` declares xfstests groups/tags: auto, quick, perms, dangerous. Imports `common/preamble`, `common/filter`. Local helpers: `_cleanup()`. Feature gates/fix annotations include `_require_scratch`, `_require_chattr`. External helper programs used include `$CHATTR_PROG`, `$UMOUNT_PROG`.

## Control Flow
The test is a overlayfs regression test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 21: `$CHATTR_PROG -i $lowerdir/foo > /dev/null 2>&1`; line 22: `$CHATTR_PROG -i $upperdir/foo > /dev/null 2>&1`; line 23: `rm -f $tmp.*`; line 33: `_scratch_mkfs`; line 39: `mkdir -p $lowerdir`; line 40: `mkdir $lowerdir/foo`; line 43: `_scratch_mount`; line 48: `$CHATTR_PROG +i $SCRATCH_MNT/foo > /dev/null 2>&1`; line 50: `$UMOUNT_PROG $SCRATCH_MNT`.

## State And Persistence
State is kept in shell variables such as `lowerdir`, `upperdir`, `workdir`. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; overlayfs layer directories, mount options, xattrs, and scratch/test filesystem capabilities.

## Risks And Test Signals
Risks: marked dangerous, so it can crash, hang, or exercise kernel failure paths. Test signals: quiet success usually prints `Silence is golden`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/076 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/077 -->
# sources/test-tools/xfstests/tests/overlay/077

## Purpose
Readdir cache invalidation test. It uses `t_dir_offset2` with a small getdents buffer on pure upper, impure upper, merge, and former-merge directories to catch stale cached entries after create/remove operations.

## Important APIs, Types, And Functions
`_begin_fstest auto quick dir` declares xfstests groups/tags: auto, quick, dir. Imports `common/preamble`, `common/filter`. Local helpers: `create_files()`. Feature gates/fix annotations include `_fixed_by_kernel_commit`, `_require_scratch_nocheck`. External helper programs used include `$UMOUNT_PROG`, `$here/src/t_dir_offset2`.

## Control Flow
The test is a overlayfs regression test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 35: `touch ${1}/${2}${n}`; line 40: `_scratch_mkfs`; line 48: `mkdir -p $lowerdir/merge $lowerdir/former $upperdir/pure $upperdir/impure`; line 54: `touch $lowerdir/f100`; line 56: `_scratch_mount`; line 61: `touch $SCRATCH_MNT/merge/m100`; line 63: `mv $SCRATCH_MNT/o* $SCRATCH_MNT/impure/`; line 64: `mv $SCRATCH_MNT/f100 $SCRATCH_MNT/former/`; line 68: `$UMOUNT_PROG $SCRATCH_MNT`; line 69: `rm -rf $lowerdir/former`.

## State And Persistence
State is kept in shell variables such as `bufsize`, `lowerdir`, `upperdir`. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; overlayfs layer directories, mount options, xattrs, and scratch/test filesystem capabilities.

## Risks And Test Signals
Risks: main risk is environmental: missing helper binaries, unsupported mount options, insufficient scratch space, or expected-output drift. Test signals: quiet success usually prints `Silence is golden`; content or output comparison is a primary failure signal.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/077 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/078 -->
# sources/test-tools/xfstests/tests/overlay/078

## Purpose
Copy-up of lower file attributes. It toggles `A`, `S`, `a`, and `i` flags on lower files, triggers copy-up with append writes or expected immutable write failure, optionally shuts down the scratch fs, cycles mounts, and confirms attribute preservation/removal.

## Important APIs, Types, And Functions
`_begin_fstest auto quick copyup perms shutdown` declares xfstests groups/tags: auto, quick, copyup, perms, shutdown. Imports `common/preamble`, `common/filter`. Local helpers: `_cleanup()`, `do_check()`. Feature gates/fix annotations include `_fixed_in_kernel_version`, `_require_command`, `_require_chattr`, `_require_xfs_io_command`, `_require_scratch`, `_require_scratch_shutdown`. External helper programs used include `$CHATTR_PROG`, `$LSATTR_PROG`, `$UMOUNT_PROG`, `$XFS_IO_PROG`.

## Control Flow
The test is a overlayfs regression test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 26: `$CHATTR_PROG -ai $lowertestfile &> /dev/null`; line 27: `$CHATTR_PROG -ai $uppertestfile &> /dev/null`; line 28: `rm -f $tmp.*`; line 51: `_scratch_mkfs`; line 52: `mkdir -p $lowerdir`; line 53: `touch $lowertestfile`; line 54: `_scratch_mount`; line 64: `$UMOUNT_PROG $SCRATCH_MNT`; line 67: `$CHATTR_PROG +$attr $lowertestfile`; line 70: `$CHATTR_PROG -ai $uppertestfile &> /dev/null`.

## State And Persistence
State is kept in shell variables such as `lowerdir`, `upperdir`, `workdir`, `lowertestfile`, `uppertestfile`, `testfile`, `attr`, `before`, `expect`, `result`, `after`, `opts`. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; overlayfs layer directories, mount options, xattrs, and scratch/test filesystem capabilities.

## Risks And Test Signals
Risks: uses disruptive kernel/storage state such as cache dropping, shutdown, dm-error, error injection, or crash/hang triggers. Test signals: quiet success usually prints `Silence is golden`; volatile paths, ids, device names, or tool output are filtered before golden comparison.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/078 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/079 -->
# sources/test-tools/xfstests/tests/overlay/079

## Purpose
Data-only lower layer test using `lowerdir=...::datadir` syntax. It builds midlayer metacopy redirects to data layers, verifies no access without absolute redirects, validates data follow with absolute redirects, checks upper data selection for shared files, and tests lazy metadata lookup after data removal.

## Important APIs, Types, And Functions
`_begin_fstest auto quick metacopy redirect prealloc` declares xfstests groups/tags: auto, quick, metacopy, redirect, prealloc. Imports `common/preamble`, `common/filter`, `common/attr`. Local helpers: `check_metacopy()`, `check_redirect()`, `check_file_size()`, `check_file_blocks()`, `check_file_contents()`, `check_no_file_contents()`, `check_file_size_contents()`, `mount_overlay()`, `mount_ro_overlay()`, `umount_overlay()`, `test_no_access()`, `test_common()`, `test_lazy()`, `create_basic_files()`, and 1 more. Feature gates/fix annotations include `_require_scratch_nocheck`, `_require_scratch_overlay_features`, `_require_scratch_overlay_lowerdata_layers`, `_require_xfs_io_command`. External helper programs used include `$UMOUNT_PROG`, `$XFS_IO_PROG`.

## Control Flow
The test is a overlayfs data-only lower-layer behavior test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 25: `_scratch_mkfs`; line 142: `_overlay_scratch_mount_opts \`; line 152: `_overlay_scratch_mount_opts \`; line 159: `$UMOUNT_PROG $SCRATCH_MNT`; line 168: `stat $SCRATCH_MNT/$_target >> $seqres.full 2>&1 || \`; line 174: `stat $SCRATCH_MNT/$_target >> $seqres.full 2>&1 || \`; line 204: `chmod 400 $SCRATCH_MNT/$_target`; line 211: `$XFS_IO_PROG -c "falloc 0 1" $SCRATCH_MNT/$_target >> $seqres.full`; line 237: `_scratch_mkfs`; line 238: `mkdir -p $datadir/subdir $datadir2/subdir $lowerdir $lowerdir2 $upperdir $workdir $workdir2`.

## State And Persistence
State is kept in shell variables such as `dataname`, `sharedname`, `datacontent`, `dataname2`, `datacontent2`, `datasize`, `datarblocks`, `datarblocksize`, `estimated_datablocks`, `udirname`, `ufile`, `out_f`, and 13 more. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; overlayfs layer directories, mount options, xattrs, and scratch/test filesystem capabilities.

## Risks And Test Signals
Risks: xattr and overlay metadata assertions depend on trusted/user xattr support and exact kernel on-disk semantics. Test signals: volatile paths, ids, device names, or tool output are filtered before golden comparison.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/079 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/080 -->
# sources/test-tools/xfstests/tests/overlay/080

## Purpose
Overlayfs fs-verity test for metacopy and data-only layers. It creates verity, no-verity, wrong-digest, and missing-digest data files, verifies `verity=off/on/require` behavior, checks I/O errors for invalid data, and verifies verity digest propagation/removal during metacopy and data copy-up.

## Important APIs, Types, And Functions
`_begin_fstest auto quick metacopy redirect verity` declares xfstests groups/tags: auto, quick, metacopy, redirect, verity. Imports `common/preamble`, `common/filter`, `common/attr`, `common/verity`. Local helpers: `check_metacopy()`, `check_verity()`, `check_redirect()`, `check_file_size()`, `check_file_contents()`, `check_file_size_contents()`, `check_io_error()`, `create_basic_files()`, `prepare_midlayer()`, `test_common()`, `mount_overlay()`, `umount_overlay()`. Feature gates/fix annotations include `_require_scratch_nocheck`, `_require_scratch_overlay_features`, `_require_scratch_overlay_lowerdata_layers`, `_require_scratch_overlay_verity`. External helper programs used include `$UMOUNT_PROG`.

## Control Flow
The test is a overlayfs fs-verity behavior test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 26: `_scratch_mkfs`; line 157: `_scratch_mkfs`; line 158: `mkdir -p $lowerdir $lowerdir2 $upperdir $workdir $workdir2`; line 161: `mkdir $lowerdir/$subdir`; line 170: `chmod 600 $lowerdir/$subdir$f`; line 173: `_fsv_enable $lowerdir/$subdir$f`; line 189: `_overlay_scratch_mount_dirs $lowerdir $lowerdir2 $workdir2 -o redirect_dir=on,index=on,verity=on,metacopy=on`; line 192: `mv $SCRATCH_MNT/base/$f $SCRATCH_MNT/$f`; line 194: `chmod 400 $SCRATCH_MNT/$f`; line 200: `rm -rf $lowerdir2/base`.

## State And Persistence
State is kept in shell variables such as `verityname`, `noverityname`, `wrongverityname`, `missingverityname`, `lowerdata`, `lowerdata2`, `lowerdata3`, `lowerdata4`, `lowersize`, `lowerdir`, `lowerdir2`, `upperdir`, and 10 more. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; overlayfs layer directories, mount options, xattrs, and scratch/test filesystem capabilities.

## Risks And Test Signals
Risks: xattr and overlay metadata assertions depend on trusted/user xattr support and exact kernel on-disk semantics. Test signals: volatile paths, ids, device names, or tool output are filtered before golden comparison.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/080 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/081 -->
# sources/test-tools/xfstests/tests/overlay/081

## Purpose
Persistent and unique overlay fsid test for `uuid=null`, `uuid=auto`, and `uuid=on`. It compares `stat -f` fsids against base fsids for existing impure overlays, explicit opt-in/out, read-only non-upper overlays, and freshly created overlays.

## Important APIs, Types, And Functions
`_begin_fstest auto quick` declares xfstests groups/tags: auto, quick. Imports `common/preamble`, `common/filter`, `common/attr`. External helper programs used include `$UMOUNT_PROG`.

## Control Flow
The test is a overlayfs regression test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 18: `_scratch_mkfs >>$seqres.full 2>&1`; line 24: `mkdir -p $upperdir/test_dir`; line 25: `mkdir -p $lowerdir/test_dir`; line 39: `_overlay_scratch_mount_dirs $lowerdir $upperdir $workdir -o uuid=null 2>/dev/null || \`; line 49: `$UMOUNT_PROG $SCRATCH_MNT`; line 52: `_scratch_mount`; line 58: `$UMOUNT_PROG $SCRATCH_MNT`; line 61: `_scratch_mount -o uuid=on`; line 68: `$UMOUNT_PROG $SCRATCH_MNT`; line 71: `_scratch_mount`.

## State And Persistence
State is kept in shell variables such as `upperdir`, `workdir`, `lowerdir`, `test_dir`, `upper_fsid`, `lower_fsid`, `ovl_fsid`, `ovl_unique_fsid`. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; overlayfs layer directories, mount options, xattrs, and scratch/test filesystem capabilities.

## Risks And Test Signals
Risks: main risk is environmental: missing helper binaries, unsupported mount options, insufficient scratch space, or expected-output drift. Test signals: quiet success usually prints `Silence is golden`; content or output comparison is a primary failure signal; unsupported environments are skipped with `_notrun`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/081 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/082 -->
# sources/test-tools/xfstests/tests/overlay/082

## Purpose
Regression test for copying up a symlink that inherited the noatime inode attribute from a lower directory. It first proves the base filesystem exhibits symlink noatime inheritance, then moves the symlink through overlay to trigger symlink flag copy-up.

## Important APIs, Types, And Functions
`_begin_fstest auto quick copyup symlink atime` declares xfstests groups/tags: auto, quick, copyup, symlink, atime. Imports `common/preamble`. Feature gates/fix annotations include `_fixed_by_kernel_commit`, `_require_scratch`, `_require_chattr`. External helper programs used include `$CHATTR_PROG`, `$LSATTR_PROG`.

## Control Flow
The test is a overlayfs regression test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 23: `_scratch_mkfs`; line 27: `mkdir -p $lowerdir/testdir`; line 28: `$CHATTR_PROG +A $lowerdir/testdir >> $seqres.full 2>&1 ||`; line 41: `touch $lowerdir/testdir/foo`; line 42: `ln -sf foo $lowerdir/testdir/lnk`; line 43: `$LSATTR_PROG -l $lowerdir/testdir/foo >> $seqres.full`; line 56: `_scratch_mount`; line 60: `mv $SCRATCH_MNT/testdir/lnk $SCRATCH_MNT/`.

## State And Persistence
State is kept in shell variables such as `lowerdir`, `before`, `after`. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; overlayfs layer directories, mount options, xattrs, and scratch/test filesystem capabilities.

## Risks And Test Signals
Risks: main risk is environmental: missing helper binaries, unsupported mount options, insufficient scratch space, or expected-output drift. Test signals: quiet success usually prints `Silence is golden`; unsupported environments are skipped with `_notrun`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/082 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/083 -->
# sources/test-tools/xfstests/tests/overlay/083

## Purpose
Mount-option escaping regression test for lower paths containing spaces, colons, and commas. It mounts directly rather than via helpers, checks escaped colon parsing and displayed lowerdir escaping, and forces mount(2) for escaped comma parsing.

## Important APIs, Types, And Functions
`_begin_fstest auto quick mount` declares xfstests groups/tags: auto, quick, mount. Imports `common/preamble`, `common/filter`. Feature gates/fix annotations include `_fixed_by_kernel_commit`, `_require_scratch_nocheck`. External helper programs used include `$MOUNT_PROG`, `$UMOUNT_PROG`.

## Control Flow
The test is a overlayfs mount option validation test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 29: `_scratch_mkfs`; line 39: `mkdir -p "$lowerdir_spaces" "$lowerdir_colons" "$lowerdir_commas"`; line 43: `$MOUNT_PROG -t overlay ovl_esc_test $SCRATCH_MNT \`; line 50: `$MOUNT_PROG -t overlay | grep ovl_esc_test | tee -a $seqres.full | grep -v spaces && \`; line 55: `$UMOUNT_PROG $SCRATCH_MNT`; line 56: `rm -rf "$upperdir" "$workdir"`; line 57: `mkdir -p "$upperdir" "$workdir"`.

## State And Persistence
State is kept in shell variables such as `lowerdir_spaces`, `lowerdir_colons`, `lowerdir_commas`, `lowerdir_colons_esc`, `lowerdir_commas_esc`, `upperdir`, `workdir`, `LIBMOUNT_FORCE_MOUNT2`. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; overlayfs layer directories, mount options, xattrs, and scratch/test filesystem capabilities.

## Risks And Test Signals
Risks: main risk is environmental: missing helper binaries, unsupported mount options, insufficient scratch space, or expected-output drift. Test signals: quiet success usually prints `Silence is golden`; content or output comparison is a primary failure signal.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/083 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/084 -->
# sources/test-tools/xfstests/tests/overlay/084

## Purpose
Advanced nested overlay xattr/whiteout test. It validates trusted/user overlay xattr escaping, nested mounts over escaped opaque directories, copy-up propagation of escaped xattrs, normal xwhiteouts, and escaped xwhiteouts inside nested overlay mounts.

## Important APIs, Types, And Functions
`_begin_fstest auto quick nested` declares xfstests groups/tags: auto, quick, nested. Imports `common/preamble`, `common/filter`, `common/attr`. Local helpers: `_cleanup()`, `umount_overlay()`, `test_escape()`, `do_test_xwhiteout()`, `test_xwhiteout()`, `test_escaped_xwhiteout()`. Feature gates/fix annotations include `_fixed_by_kernel_commit`, `_require_scratch_nocheck`, `_require_scratch_overlay_xattr_escapes`. External helper programs used include `$UMOUNT_PROG`.

## Control Flow
The test is a overlayfs export/file-handle regression test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 18: `$UMOUNT_PROG $OVL_BASE_SCRATCH_MNT/nested 2>/dev/null`; line 19: `rm -rf $tmp`; line 37: `_scratch_mkfs`; line 47: `$UMOUNT_PROG $SCRATCH_MNT`; line 62: `_scratch_mkfs`; line 63: `mkdir -p $lowerdir $middir $upperdir $workdir $nesteddir`; line 65: `_overlay_scratch_mount_dirs $lowerdir $middir $workdir $extra_options`; line 67: `mkdir -p $SCRATCH_MNT/layer1/dir/ $SCRATCH_MNT/layer2/dir`; line 69: `touch $SCRATCH_MNT/layer1/dir/file`; line 73: `setfattr -n user.overlay.opaque -v "y" $SCRATCH_MNT/layer2/dir`.

## State And Persistence
State is kept in shell variables such as `lowerdir`, `middir`, `upperdir`, `workdir`, `nesteddir`, `extra_options`. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; overlayfs layer directories, mount options, xattrs, and scratch/test filesystem capabilities.

## Risks And Test Signals
Risks: file-handle behavior is sensitive to dcache warmth, inode identity, stale-handle semantics, and export feature availability; xattr and overlay metadata assertions depend on trusted/user xattr support and exact kernel on-disk semantics. Test signals: volatile paths, ids, device names, or tool output are filtered before golden comparison.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/084 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/085 -->
# sources/test-tools/xfstests/tests/overlay/085

## Purpose
Variant of overlay/079 using the new `lowerdir+=` and `datadir+=` mount option syntax. It repeats no-access, absolute redirect follow, shared data-layer precedence, metacopy-to-data-copy transition, and lazy lowerdata lookup checks.

## Important APIs, Types, And Functions
`_begin_fstest auto quick metacopy redirect prealloc` declares xfstests groups/tags: auto, quick, metacopy, redirect, prealloc. Imports `common/preamble`, `common/filter`, `common/attr`. Local helpers: `check_metacopy()`, `check_redirect()`, `check_file_size()`, `check_file_blocks()`, `check_file_contents()`, `check_no_file_contents()`, `check_file_size_contents()`, `mount_overlay()`, `mount_ro_overlay()`, `umount_overlay()`, `test_no_access()`, `test_common()`, `test_lazy()`, `create_basic_files()`, and 1 more. Feature gates/fix annotations include `_require_scratch_nocheck`, `_require_scratch_overlay_features`, `_require_scratch_overlay_lowerdir_add_layers`, `_require_xfs_io_command`. External helper programs used include `$UMOUNT_PROG`, `$XFS_IO_PROG`.

## Control Flow
The test is a overlayfs data-only lower-layer behavior test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 26: `_scratch_mkfs`; line 143: `_overlay_scratch_mount_opts \`; line 153: `_overlay_scratch_mount_opts \`; line 160: `$UMOUNT_PROG $SCRATCH_MNT`; line 169: `stat $SCRATCH_MNT/$_target >> $seqres.full 2>&1 || \`; line 175: `stat $SCRATCH_MNT/$_target >> $seqres.full 2>&1 || \`; line 205: `chmod 400 $SCRATCH_MNT/$_target`; line 212: `$XFS_IO_PROG -c "falloc 0 1" $SCRATCH_MNT/$_target >> $seqres.full`; line 238: `_scratch_mkfs`; line 239: `mkdir -p $datadir/subdir $datadir2/subdir $lowerdir $lowerdir2 $upperdir $workdir $workdir2`.

## State And Persistence
State is kept in shell variables such as `dataname`, `sharedname`, `datacontent`, `dataname2`, `datacontent2`, `datasize`, `datarblocks`, `datarblocksize`, `estimated_datablocks`, `udirname`, `ufile`, `out_f`, and 13 more. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; overlayfs layer directories, mount options, xattrs, and scratch/test filesystem capabilities.

## Risks And Test Signals
Risks: xattr and overlay metadata assertions depend on trusted/user xattr support and exact kernel on-disk semantics. Test signals: volatile paths, ids, device names, or tool output are filtered before golden comparison.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/085 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/086 -->
# sources/test-tools/xfstests/tests/overlay/086

## Purpose
Mount-option restriction test for `lowerdir+`/`datadir+`. It checks invalid combinations with legacy `lowerdir=`, invalid ordering of datadir before lowerdir, escaped-colon rejection for `lowerdir+`, successful unescaped colon handling, and displayed escaping for spaces.

## Important APIs, Types, And Functions
`_begin_fstest auto quick mount` declares xfstests groups/tags: auto, quick, mount. Imports `common/preamble`, `common/filter`. Feature gates/fix annotations include `_require_scratch_nocheck`, `_require_scratch_overlay_lowerdir_add_layers`. External helper programs used include `$MOUNT_PROG`, `$UMOUNT_PROG`.

## Control Flow
The test is a overlayfs data-only lower-layer behavior test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 22: `_scratch_mkfs`; line 31: `mkdir -p "$lowerdir_spaces" "$lowerdir_colons"`; line 36: `$MOUNT_PROG -t overlay none $SCRATCH_MNT \`; line 41: `$UMOUNT_PROG $SCRATCH_MNT 2>/dev/null`; line 43: `$MOUNT_PROG -t overlay none $SCRATCH_MNT \`; line 48: `$UMOUNT_PROG $SCRATCH_MNT 2>/dev/null`; line 50: `$MOUNT_PROG -t overlay none $SCRATCH_MNT \`; line 55: `$UMOUNT_PROG $SCRATCH_MNT 2>/dev/null`; line 58: `$MOUNT_PROG -t overlay none $SCRATCH_MNT \`; line 63: `$UMOUNT_PROG $SCRATCH_MNT 2>/dev/null`.

## State And Persistence
State is kept in shell variables such as `lowerdir_spaces`, `lowerdir_colons`, `lowerdir_colons_esc`, `lowerdir`, `upperdir`, `workdir`. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; overlayfs layer directories, mount options, xattrs, and scratch/test filesystem capabilities.

## Risks And Test Signals
Risks: xattr and overlay metadata assertions depend on trusted/user xattr support and exact kernel on-disk semantics. Test signals: quiet success usually prints `Silence is golden`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/086 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/087 -->
# sources/test-tools/xfstests/tests/overlay/087

## Purpose
Overlayfs variant of an XFS syncfs-after-shutdown regression test. It checks that syncfs reports shutdown errors on a normal overlay over XFS, then repeats with `volatile` overlay where syncfs after shutdown is expected not to report the same error.

## Important APIs, Types, And Functions
`_begin_fstest auto quick mount shutdown` declares xfstests groups/tags: auto, quick, mount, shutdown. Imports `common/preamble`. Feature gates/fix annotations include `_require_scratch_nocheck`, `_require_scratch_shutdown_and_syncfs`, `_require_metadata_journaling`. External helper programs used include `xfs_fs_sync_fs`.

## Control Flow
The test is a overlayfs mount option validation test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 45: `_scratch_mount`; line 46: `_scratch_shutdown_and_syncfs`; line 49: `_scratch_unmount`; line 51: `_scratch_mount -o volatile`; line 52: `_scratch_shutdown_and_syncfs`.

## State And Persistence
State is mostly external to the script. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; overlayfs layer directories, mount options, xattrs, and scratch/test filesystem capabilities.

## Risks And Test Signals
Risks: uses disruptive kernel/storage state such as cache dropping, shutdown, dm-error, error injection, or crash/hang triggers. Test signals: unsupported environments are skipped with `_notrun`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/087 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/088 -->
# sources/test-tools/xfstests/tests/overlay/088

## Purpose
Userxattr/no-metacopy variant of data-only layer tests. It converts trusted overlay xattrs to user xattrs, mounts with `userxattr` and no redirect_dir/metacopy options, and validates lowerdata access, absolute redirects, copy-up contents, and lazy lookup.

## Important APIs, Types, And Functions
`_begin_fstest auto quick metacopy redirect prealloc attr` declares xfstests groups/tags: auto, quick, metacopy, redirect, prealloc, attr. Imports `common/preamble`, `common/filter`, `common/attr`. Local helpers: `check_redirect()`, `check_file_size()`, `check_file_blocks()`, `check_file_contents()`, `check_no_file_contents()`, `check_file_size_contents()`, `mount_overlay()`, `mount_ro_overlay()`, `umount_overlay()`, `test_no_access()`, `test_common()`, `test_lazy()`, `create_basic_files()`, `prepare_midlayer()`. Feature gates/fix annotations include `_require_scratch_nocheck`, `_require_attrs`, `_require_scratch_overlay_features`, `_require_scratch_overlay_lowerdir_add_layers`, `_require_scratch_overlay_datadir_without_metacopy`, `_require_xfs_io_command`. External helper programs used include `$UMOUNT_PROG`, `$XFS_IO_PROG`.

## Control Flow
The test is a overlayfs data-only lower-layer behavior test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 29: `_scratch_mkfs`; line 118: `_overlay_scratch_mount_opts \`; line 128: `_overlay_scratch_mount_opts \`; line 135: `$UMOUNT_PROG $SCRATCH_MNT`; line 144: `stat $SCRATCH_MNT/$_target >> $seqres.full 2>&1 || \`; line 150: `stat $SCRATCH_MNT/$_target >> $seqres.full 2>&1 || \`; line 180: `chmod 400 $SCRATCH_MNT/$_target`; line 203: `_scratch_mkfs`; line 204: `mkdir -p $datadir/subdir $datadir2/subdir $lowerdir $lowerdir2 $upperdir $workdir $workdir2`; line 205: `mkdir -p $upperdir/$udirname`.

## State And Persistence
State is kept in shell variables such as `dataname`, `sharedname`, `datacontent`, `dataname2`, `datacontent2`, `datasize`, `datarblocks`, `datarblocksize`, `estimated_datablocks`, `udirname`, `ufile`, `value`, and 13 more. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; overlayfs layer directories, mount options, xattrs, and scratch/test filesystem capabilities.

## Risks And Test Signals
Risks: xattr and overlay metadata assertions depend on trusted/user xattr support and exact kernel on-disk semantics. Test signals: volatile paths, ids, device names, or tool output are filtered before golden comparison.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/088 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/089 -->
# sources/test-tools/xfstests/tests/overlay/089

## Purpose
Userxattr/no-metacopy variant of the fs-verity lowerdata test. It verifies user.overlay metacopy/redirect metadata and `verity=off/on/require` behavior for verity, no-verity, wrong-digest, and missing-digest files in a data-only layer setup.

## Important APIs, Types, And Functions
`_begin_fstest auto quick metacopy redirect verity attr` declares xfstests groups/tags: auto, quick, metacopy, redirect, verity, attr. Imports `common/preamble`, `common/filter`, `common/attr`, `common/verity`. Local helpers: `check_metacopy()`, `check_verity()`, `check_redirect()`, `check_file_size()`, `check_file_contents()`, `check_file_size_contents()`, `check_io_error()`, `create_basic_files()`, `prepare_midlayer()`, `test_common()`, `mount_overlay()`, `umount_overlay()`. Feature gates/fix annotations include `_require_scratch_nocheck`, `_require_attrs`, `_require_scratch_overlay_features`, `_require_scratch_overlay_lowerdata_layers`, `_require_scratch_overlay_datadir_without_metacopy`, `_require_scratch_overlay_verity`. External helper programs used include `$UMOUNT_PROG`.

## Control Flow
The test is a overlayfs fs-verity behavior test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 30: `_scratch_mkfs`; line 161: `_scratch_mkfs`; line 162: `mkdir -p $lowerdir $lowerdir2 $upperdir $workdir $workdir2`; line 165: `mkdir $lowerdir/$subdir`; line 174: `chmod 600 $lowerdir/$subdir$f`; line 177: `_fsv_enable $lowerdir/$subdir$f`; line 188: `_overlay_scratch_mount_dirs $lowerdir $lowerdir2 $workdir2 -o redirect_dir=on,index=on,verity=on,metacopy=on`; line 190: `mv $SCRATCH_MNT/base/$f $SCRATCH_MNT/$f`; line 194: `_overlay_trusted_to_user $lowerdir2`; line 196: `rm -rf $lowerdir2/base`.

## State And Persistence
State is kept in shell variables such as `verityname`, `noverityname`, `wrongverityname`, `missingverityname`, `lowerdata`, `lowerdata2`, `lowerdata3`, `lowerdata4`, `lowersize`, `lowerdir`, `lowerdir2`, `upperdir`, and 10 more. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; overlayfs layer directories, mount options, xattrs, and scratch/test filesystem capabilities.

## Risks And Test Signals
Risks: xattr and overlay metadata assertions depend on trusted/user xattr support and exact kernel on-disk semantics. Test signals: volatile paths, ids, device names, or tool output are filtered before golden comparison.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/089 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/100 -->
# sources/test-tools/xfstests/tests/overlay/100

## Purpose
Runs the unionmount testsuite against overlayfs for single lower layer on the same filesystem as upper. The script is intentionally small: it registers unionmount cleanup, gates on scratch/test/tmpfs requirements as needed, and delegates behavioral coverage to `_unionmount_testsuite_run` with topology-specific flags.

## Important APIs, Types, And Functions
`_begin_fstest auto quick union samefs` declares xfstests groups/tags: auto, quick, union, samefs. Imports `common/preamble`, `common/filter`. Feature gates/fix annotations include `_register_cleanup`, `_require_scratch`, `_require_unionmount_testsuite`. External helper programs used include `unionmount`.

## Control Flow
The test is a overlay unionmount suite wrapper. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: no imperative commands beyond harness declarations.

## State And Persistence
State is mostly external to the script. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; overlayfs layer directories, mount options, xattrs, and scratch/test filesystem capabilities.

## Risks And Test Signals
Risks: main risk is environmental: missing helper binaries, unsupported mount options, insufficient scratch space, or expected-output drift. Test signals: quiet success usually prints `Silence is golden`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/100 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/101 -->
# sources/test-tools/xfstests/tests/overlay/101

## Purpose
Runs the unionmount testsuite against overlayfs for single lower layer not on the same filesystem as upper. The script is intentionally small: it registers unionmount cleanup, gates on scratch/test/tmpfs requirements as needed, and delegates behavioral coverage to `_unionmount_testsuite_run` with topology-specific flags.

## Important APIs, Types, And Functions
`_begin_fstest auto quick union nonsamefs` declares xfstests groups/tags: auto, quick, union, nonsamefs. Imports `common/preamble`, `common/filter`. Feature gates/fix annotations include `_register_cleanup`, `_require_test`, `_require_scratch`, `_require_unionmount_testsuite`. External helper programs used include `unionmount`.

## Control Flow
The test is a overlay unionmount suite wrapper. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: no imperative commands beyond harness declarations.

## State And Persistence
State is mostly external to the script. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; overlayfs layer directories, mount options, xattrs, and scratch/test filesystem capabilities.

## Risks And Test Signals
Risks: main risk is environmental: missing helper binaries, unsupported mount options, insufficient scratch space, or expected-output drift. Test signals: quiet success usually prints `Silence is golden`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/101 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/102 -->
# sources/test-tools/xfstests/tests/overlay/102

## Purpose
Runs the unionmount testsuite against overlayfs for single non-samefs lower layer with xino enabled. The script is intentionally small: it registers unionmount cleanup, gates on scratch/test/tmpfs requirements as needed, and delegates behavioral coverage to `_unionmount_testsuite_run` with topology-specific flags.

## Important APIs, Types, And Functions
`_begin_fstest auto quick union nonsamefs xino` declares xfstests groups/tags: auto, quick, union, nonsamefs, xino. Imports `common/preamble`, `common/filter`. Feature gates/fix annotations include `_register_cleanup`, `_require_test`, `_require_scratch`, `_require_unionmount_testsuite`. External helper programs used include `unionmount`.

## Control Flow
The test is a overlay unionmount suite wrapper. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: no imperative commands beyond harness declarations.

## State And Persistence
State is mostly external to the script. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; overlayfs layer directories, mount options, xattrs, and scratch/test filesystem capabilities.

## Risks And Test Signals
Risks: main risk is environmental: missing helper binaries, unsupported mount options, insufficient scratch space, or expected-output drift. Test signals: quiet success usually prints `Silence is golden`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/102 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/103 -->
# sources/test-tools/xfstests/tests/overlay/103

## Purpose
Runs the unionmount testsuite against overlayfs for multiple lower layers on the same filesystem as upper. The script is intentionally small: it registers unionmount cleanup, gates on scratch/test/tmpfs requirements as needed, and delegates behavioral coverage to `_unionmount_testsuite_run` with topology-specific flags.

## Important APIs, Types, And Functions
`_begin_fstest auto union rotate samefs` declares xfstests groups/tags: auto, union, rotate, samefs. Imports `common/preamble`, `common/filter`. Feature gates/fix annotations include `_register_cleanup`, `_require_scratch`, `_require_unionmount_testsuite`. External helper programs used include `unionmount`.

## Control Flow
The test is a overlay unionmount suite wrapper. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: no imperative commands beyond harness declarations.

## State And Persistence
State is mostly external to the script. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; overlayfs layer directories, mount options, xattrs, and scratch/test filesystem capabilities.

## Risks And Test Signals
Risks: main risk is environmental: missing helper binaries, unsupported mount options, insufficient scratch space, or expected-output drift. Test signals: quiet success usually prints `Silence is golden`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/103 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/104 -->
# sources/test-tools/xfstests/tests/overlay/104

## Purpose
Runs the unionmount testsuite against overlayfs for multiple lower layers with lowermost on a unique filesystem. The script is intentionally small: it registers unionmount cleanup, gates on scratch/test/tmpfs requirements as needed, and delegates behavioral coverage to `_unionmount_testsuite_run` with topology-specific flags.

## Important APIs, Types, And Functions
`_begin_fstest auto union rotate nonsamefs` declares xfstests groups/tags: auto, union, rotate, nonsamefs. Imports `common/preamble`, `common/filter`. Feature gates/fix annotations include `_register_cleanup`, `_require_test`, `_require_scratch`, `_require_unionmount_testsuite`. External helper programs used include `unionmount`.

## Control Flow
The test is a overlay unionmount suite wrapper. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: no imperative commands beyond harness declarations.

## State And Persistence
State is mostly external to the script. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; overlayfs layer directories, mount options, xattrs, and scratch/test filesystem capabilities.

## Risks And Test Signals
Risks: main risk is environmental: missing helper binaries, unsupported mount options, insufficient scratch space, or expected-output drift. Test signals: quiet success usually prints `Silence is golden`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/104 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/105 -->
# sources/test-tools/xfstests/tests/overlay/105

## Purpose
Runs the unionmount testsuite against overlayfs for multiple non-samefs lower layers with xino enabled. The script is intentionally small: it registers unionmount cleanup, gates on scratch/test/tmpfs requirements as needed, and delegates behavioral coverage to `_unionmount_testsuite_run` with topology-specific flags.

## Important APIs, Types, And Functions
`_begin_fstest auto union rotate nonsamefs xino` declares xfstests groups/tags: auto, union, rotate, nonsamefs, xino. Imports `common/preamble`, `common/filter`. Feature gates/fix annotations include `_register_cleanup`, `_require_test`, `_require_scratch`, `_require_unionmount_testsuite`. External helper programs used include `unionmount`.

## Control Flow
The test is a overlay unionmount suite wrapper. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: no imperative commands beyond harness declarations.

## State And Persistence
State is mostly external to the script. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; overlayfs layer directories, mount options, xattrs, and scratch/test filesystem capabilities.

## Risks And Test Signals
Risks: main risk is environmental: missing helper binaries, unsupported mount options, insufficient scratch space, or expected-output drift. Test signals: quiet success usually prints `Silence is golden`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/105 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/106 -->
# sources/test-tools/xfstests/tests/overlay/106

## Purpose
Runs the unionmount testsuite against overlayfs for multiple lower layers with some unique layers and one tmpfs layer. The script is intentionally small: it registers unionmount cleanup, gates on scratch/test/tmpfs requirements as needed, and delegates behavioral coverage to `_unionmount_testsuite_run` with topology-specific flags.

## Important APIs, Types, And Functions
`_begin_fstest auto union rotate nonsamefs` declares xfstests groups/tags: auto, union, rotate, nonsamefs. Imports `common/preamble`, `common/filter`. Feature gates/fix annotations include `_register_cleanup`, `_require_extra_fs`, `_require_test`, `_require_scratch`, `_require_unionmount_testsuite`. External helper programs used include `unionmount`.

## Control Flow
The test is a overlay unionmount suite wrapper. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: no imperative commands beyond harness declarations.

## State And Persistence
State is mostly external to the script. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; overlayfs layer directories, mount options, xattrs, and scratch/test filesystem capabilities.

## Risks And Test Signals
Risks: main risk is environmental: missing helper binaries, unsupported mount options, insufficient scratch space, or expected-output drift. Test signals: quiet success usually prints `Silence is golden`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/106 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/107 -->
# sources/test-tools/xfstests/tests/overlay/107

## Purpose
Runs the unionmount testsuite against overlayfs for the same tmpfs/unique-layer topology with xino enabled. The script is intentionally small: it registers unionmount cleanup, gates on scratch/test/tmpfs requirements as needed, and delegates behavioral coverage to `_unionmount_testsuite_run` with topology-specific flags.

## Important APIs, Types, And Functions
`_begin_fstest auto union rotate nonsamefs xino` declares xfstests groups/tags: auto, union, rotate, nonsamefs, xino. Imports `common/preamble`, `common/filter`. Feature gates/fix annotations include `_register_cleanup`, `_require_extra_fs`, `_require_test`, `_require_scratch`, `_require_unionmount_testsuite`. External helper programs used include `unionmount`.

## Control Flow
The test is a overlay unionmount suite wrapper. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: no imperative commands beyond harness declarations.

## State And Persistence
State is mostly external to the script. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; overlayfs layer directories, mount options, xattrs, and scratch/test filesystem capabilities.

## Risks And Test Signals
Risks: main risk is environmental: missing helper binaries, unsupported mount options, insufficient scratch space, or expected-output drift. Test signals: quiet success usually prints `Silence is golden`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/107 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/108 -->
# sources/test-tools/xfstests/tests/overlay/108

## Purpose
Runs the unionmount testsuite against overlayfs for multiple lower layers all on unique filesystems, with tmpfs participants. The script is intentionally small: it registers unionmount cleanup, gates on scratch/test/tmpfs requirements as needed, and delegates behavioral coverage to `_unionmount_testsuite_run` with topology-specific flags.

## Important APIs, Types, And Functions
`_begin_fstest auto union rotate nonsamefs` declares xfstests groups/tags: auto, union, rotate, nonsamefs. Imports `common/preamble`, `common/filter`. Feature gates/fix annotations include `_register_cleanup`, `_require_extra_fs`, `_require_test`, `_require_scratch`, `_require_unionmount_testsuite`. External helper programs used include `unionmount`.

## Control Flow
The test is a overlay unionmount suite wrapper. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: no imperative commands beyond harness declarations.

## State And Persistence
State is mostly external to the script. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; overlayfs layer directories, mount options, xattrs, and scratch/test filesystem capabilities.

## Risks And Test Signals
Risks: main risk is environmental: missing helper binaries, unsupported mount options, insufficient scratch space, or expected-output drift. Test signals: quiet success usually prints `Silence is golden`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/108 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/109 -->
# sources/test-tools/xfstests/tests/overlay/109

## Purpose
Runs the unionmount testsuite against overlayfs for the all-unique/tmpfs topology with xino enabled. The script is intentionally small: it registers unionmount cleanup, gates on scratch/test/tmpfs requirements as needed, and delegates behavioral coverage to `_unionmount_testsuite_run` with topology-specific flags.

## Important APIs, Types, And Functions
`_begin_fstest auto union rotate nonsamefs xino` declares xfstests groups/tags: auto, union, rotate, nonsamefs, xino. Imports `common/preamble`, `common/filter`. Feature gates/fix annotations include `_register_cleanup`, `_require_extra_fs`, `_require_test`, `_require_scratch`, `_require_unionmount_testsuite`. External helper programs used include `unionmount`.

## Control Flow
The test is a overlay unionmount suite wrapper. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: no imperative commands beyond harness declarations.

## State And Persistence
State is mostly external to the script. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; overlayfs layer directories, mount options, xattrs, and scratch/test filesystem capabilities.

## Risks And Test Signals
Risks: main risk is environmental: missing helper binaries, unsupported mount options, insufficient scratch space, or expected-output drift. Test signals: quiet success usually prints `Silence is golden`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/109 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/110 -->
# sources/test-tools/xfstests/tests/overlay/110

## Purpose
Runs the unionmount testsuite against overlayfs for nested overlay with one lower overlay and samefs underlying layers. The script is intentionally small: it registers unionmount cleanup, gates on scratch/test/tmpfs requirements as needed, and delegates behavioral coverage to `_unionmount_testsuite_run` with topology-specific flags.

## Important APIs, Types, And Functions
`_begin_fstest auto quick union nested samefs` declares xfstests groups/tags: auto, quick, union, nested, samefs. Imports `common/preamble`, `common/filter`. Feature gates/fix annotations include `_register_cleanup`, `_require_scratch`, `_require_unionmount_testsuite`. External helper programs used include `unionmount`.

## Control Flow
The test is a overlay unionmount suite wrapper. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: no imperative commands beyond harness declarations.

## State And Persistence
State is mostly external to the script. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; overlayfs layer directories, mount options, xattrs, and scratch/test filesystem capabilities.

## Risks And Test Signals
Risks: main risk is environmental: missing helper binaries, unsupported mount options, insufficient scratch space, or expected-output drift. Test signals: quiet success usually prints `Silence is golden`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/110 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/111 -->
# sources/test-tools/xfstests/tests/overlay/111

## Purpose
Runs the unionmount testsuite against overlayfs for nested samefs overlay with xino enabled. The script is intentionally small: it registers unionmount cleanup, gates on scratch/test/tmpfs requirements as needed, and delegates behavioral coverage to `_unionmount_testsuite_run` with topology-specific flags.

## Important APIs, Types, And Functions
`_begin_fstest auto quick union nested samefs xino` declares xfstests groups/tags: auto, quick, union, nested, samefs, xino. Imports `common/preamble`, `common/filter`. Feature gates/fix annotations include `_register_cleanup`, `_require_scratch`, `_require_unionmount_testsuite`. External helper programs used include `unionmount`.

## Control Flow
The test is a overlay unionmount suite wrapper. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: no imperative commands beyond harness declarations.

## State And Persistence
State is mostly external to the script. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; overlayfs layer directories, mount options, xattrs, and scratch/test filesystem capabilities.

## Risks And Test Signals
Risks: main risk is environmental: missing helper binaries, unsupported mount options, insufficient scratch space, or expected-output drift. Test signals: quiet success usually prints `Silence is golden`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/111 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/112 -->
# sources/test-tools/xfstests/tests/overlay/112

## Purpose
Runs the unionmount testsuite against overlayfs for nested overlay with one lower overlay and non-samefs underlying layers. The script is intentionally small: it registers unionmount cleanup, gates on scratch/test/tmpfs requirements as needed, and delegates behavioral coverage to `_unionmount_testsuite_run` with topology-specific flags.

## Important APIs, Types, And Functions
`_begin_fstest auto quick union nested nonsamefs` declares xfstests groups/tags: auto, quick, union, nested, nonsamefs. Imports `common/preamble`, `common/filter`. Feature gates/fix annotations include `_register_cleanup`, `_require_test`, `_require_scratch`, `_require_unionmount_testsuite`. External helper programs used include `unionmount`.

## Control Flow
The test is a overlay unionmount suite wrapper. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: no imperative commands beyond harness declarations.

## State And Persistence
State is mostly external to the script. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; overlayfs layer directories, mount options, xattrs, and scratch/test filesystem capabilities.

## Risks And Test Signals
Risks: main risk is environmental: missing helper binaries, unsupported mount options, insufficient scratch space, or expected-output drift. Test signals: quiet success usually prints `Silence is golden`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/112 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/113 -->
# sources/test-tools/xfstests/tests/overlay/113

## Purpose
Runs the unionmount testsuite against overlayfs for nested non-samefs overlay with xino enabled and expected xino overflow cases. The script is intentionally small: it registers unionmount cleanup, gates on scratch/test/tmpfs requirements as needed, and delegates behavioral coverage to `_unionmount_testsuite_run` with topology-specific flags.

## Important APIs, Types, And Functions
`_begin_fstest auto quick union nested nonsamefs xino` declares xfstests groups/tags: auto, quick, union, nested, nonsamefs, xino. Imports `common/preamble`, `common/filter`. Feature gates/fix annotations include `_register_cleanup`, `_require_test`, `_require_scratch`, `_require_unionmount_testsuite`. External helper programs used include `unionmount`.

## Control Flow
The test is a overlay unionmount suite wrapper. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: no imperative commands beyond harness declarations.

## State And Persistence
State is mostly external to the script. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; overlayfs layer directories, mount options, xattrs, and scratch/test filesystem capabilities.

## Risks And Test Signals
Risks: main risk is environmental: missing helper binaries, unsupported mount options, insufficient scratch space, or expected-output drift. Test signals: quiet success usually prints `Silence is golden`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/113 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/114 -->
# sources/test-tools/xfstests/tests/overlay/114

## Purpose
Runs the unionmount testsuite against overlayfs for nested overlay with multiple lower layers and lowermost lower as an overlay on samefs layers. The script is intentionally small: it registers unionmount cleanup, gates on scratch/test/tmpfs requirements as needed, and delegates behavioral coverage to `_unionmount_testsuite_run` with topology-specific flags.

## Important APIs, Types, And Functions
`_begin_fstest auto union rotate nested samefs` declares xfstests groups/tags: auto, union, rotate, nested, samefs. Imports `common/preamble`, `common/filter`. Feature gates/fix annotations include `_register_cleanup`, `_require_scratch`, `_require_unionmount_testsuite`. External helper programs used include `unionmount`.

## Control Flow
The test is a overlay unionmount suite wrapper. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: no imperative commands beyond harness declarations.

## State And Persistence
State is mostly external to the script. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; overlayfs layer directories, mount options, xattrs, and scratch/test filesystem capabilities.

## Risks And Test Signals
Risks: main risk is environmental: missing helper binaries, unsupported mount options, insufficient scratch space, or expected-output drift. Test signals: quiet success usually prints `Silence is golden`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/114 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/115 -->
# sources/test-tools/xfstests/tests/overlay/115

## Purpose
Runs the unionmount testsuite against overlayfs for nested multi-lower samefs overlay with xino enabled. The script is intentionally small: it registers unionmount cleanup, gates on scratch/test/tmpfs requirements as needed, and delegates behavioral coverage to `_unionmount_testsuite_run` with topology-specific flags.

## Important APIs, Types, And Functions
`_begin_fstest auto union rotate nested samefs xino` declares xfstests groups/tags: auto, union, rotate, nested, samefs, xino. Imports `common/preamble`, `common/filter`. Feature gates/fix annotations include `_register_cleanup`, `_require_scratch`, `_require_unionmount_testsuite`. External helper programs used include `unionmount`.

## Control Flow
The test is a overlay unionmount suite wrapper. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: no imperative commands beyond harness declarations.

## State And Persistence
State is mostly external to the script. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; overlayfs layer directories, mount options, xattrs, and scratch/test filesystem capabilities.

## Risks And Test Signals
Risks: main risk is environmental: missing helper binaries, unsupported mount options, insufficient scratch space, or expected-output drift. Test signals: quiet success usually prints `Silence is golden`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/115 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/116 -->
# sources/test-tools/xfstests/tests/overlay/116

## Purpose
Runs the unionmount testsuite against overlayfs for nested overlay with multiple lower layers and lowermost lower as an overlay on non-samefs layers. The script is intentionally small: it registers unionmount cleanup, gates on scratch/test/tmpfs requirements as needed, and delegates behavioral coverage to `_unionmount_testsuite_run` with topology-specific flags.

## Important APIs, Types, And Functions
`_begin_fstest auto union rotate nested nonsamefs` declares xfstests groups/tags: auto, union, rotate, nested, nonsamefs. Imports `common/preamble`, `common/filter`. Feature gates/fix annotations include `_register_cleanup`, `_require_test`, `_require_scratch`, `_require_unionmount_testsuite`. External helper programs used include `unionmount`.

## Control Flow
The test is a overlay unionmount suite wrapper. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: no imperative commands beyond harness declarations.

## State And Persistence
State is mostly external to the script. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; overlayfs layer directories, mount options, xattrs, and scratch/test filesystem capabilities.

## Risks And Test Signals
Risks: main risk is environmental: missing helper binaries, unsupported mount options, insufficient scratch space, or expected-output drift. Test signals: quiet success usually prints `Silence is golden`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/116 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/117 -->
# sources/test-tools/xfstests/tests/overlay/117

## Purpose
Runs the unionmount testsuite against overlayfs for nested multi-lower non-samefs overlay with xino enabled and expected overflow cases. The script is intentionally small: it registers unionmount cleanup, gates on scratch/test/tmpfs requirements as needed, and delegates behavioral coverage to `_unionmount_testsuite_run` with topology-specific flags.

## Important APIs, Types, And Functions
`_begin_fstest auto union rotate nested nonsamefs xino` declares xfstests groups/tags: auto, union, rotate, nested, nonsamefs, xino. Imports `common/preamble`, `common/filter`. Feature gates/fix annotations include `_register_cleanup`, `_require_test`, `_require_scratch`, `_require_unionmount_testsuite`. External helper programs used include `unionmount`.

## Control Flow
The test is a overlay unionmount suite wrapper. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: no imperative commands beyond harness declarations.

## State And Persistence
State is mostly external to the script. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; overlayfs layer directories, mount options, xattrs, and scratch/test filesystem capabilities.

## Risks And Test Signals
Risks: main risk is environmental: missing helper binaries, unsupported mount options, insufficient scratch space, or expected-output drift. Test signals: quiet success usually prints `Silence is golden`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/117 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/Makefile -->
# sources/test-tools/xfstests/tests/overlay/Makefile

## Purpose
Build/install metadata for this xfstests directory. It includes xfstests shared build definitions, derives the package target directory, generates `group.list`, installs executable tests and expected-output files, and leaves development/library install targets empty.

## Important APIs, Types, And Functions
Make variables include `TOPDIR`, directory-specific `*_DIR`, `TARGET_DIR`, and `DIRT`; targets include `default`, `install`, `install-dev`, and `install-lib`; included rule files are `include/builddefs`, `include/buildgrouplist`, and `$(BUILDRULES)`.

## Control Flow
The makefile imports xfstests shared build rules, declares `group.list` as generated dirt, and installs tests, `group.list`, and expected output files into the package tests directory. Development and library install targets are intentionally empty.

## State And Persistence
State is build/install metadata only. Generated state is `group.list`; install state is the packaged test directory populated by `$(INSTALL)`.

## Dependencies And Integration Points
Depends on xfstests top-level make fragments and the `TESTS`/`OUTFILES` lists supplied by the build system.

## Risks And Test Signals
Risks are packaging omissions: wrong target directory names, missing group-list generation, or mode mismatches on installed executable tests. A successful `make install` and populated target directory are the main test signals.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/perf/001 -->
# sources/test-tools/xfstests/tests/perf/001

## Purpose
Buffered random-write performance benchmark. It generates a fio psync randwrite job sized by `LOAD_FACTOR`, verifies the scratch filesystem has enough capacity, captures JSON fio output, and compares the result through xfstests performance helpers.

## Important APIs, Types, And Functions
`_begin_fstest auto` declares xfstests groups/tags: auto. Imports `common/preamble`, `common/filter`, `common/perf`. Feature gates/fix annotations include `_require_scratch`, `_require_block_device`, `_require_fio_results`, `_require_fio`, `_require_fs_space`. External helper programs used include `fio`, `$FIO_PROG`.

## Control Flow
The test is a xfstests performance benchmark. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 42: `_scratch_mkfs >> $seqres.full 2>&1`; line 43: `_scratch_mount`; line 47: `$FIO_PROG --output-format=json --output=$fio_results $fio_config`; line 49: `_scratch_unmount`.

## State And Persistence
State is kept in shell variables such as `fio_config`, `fio_results`, `_size`, `directory`, `allrandrepeat`, `readwrite`, `size`, `ioengine`, `end_fsync`, `fallocate`. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; fio plus xfstests performance result initialization and comparison helpers.

## Risks And Test Signals
Risks: space/quota tests are sensitive to scratch capacity, mkfs geometry, and background reclaim. Test signals: quiet success usually prints `Silence is golden`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/perf/001 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/perf/Makefile -->
# sources/test-tools/xfstests/tests/perf/Makefile

## Purpose
Build/install metadata for this xfstests directory. It includes xfstests shared build definitions, derives the package target directory, generates `group.list`, installs executable tests and expected-output files, and leaves development/library install targets empty.

## Important APIs, Types, And Functions
Make variables include `TOPDIR`, directory-specific `*_DIR`, `TARGET_DIR`, and `DIRT`; targets include `default`, `install`, `install-dev`, and `install-lib`; included rule files are `include/builddefs`, `include/buildgrouplist`, and `$(BUILDRULES)`.

## Control Flow
The makefile imports xfstests shared build rules, declares `group.list` as generated dirt, and installs tests, `group.list`, and expected output files into the package tests directory. Development and library install targets are intentionally empty.

## State And Persistence
State is build/install metadata only. Generated state is `group.list`; install state is the packaged test directory populated by `$(INSTALL)`.

## Dependencies And Integration Points
Depends on xfstests top-level make fragments and the `TESTS`/`OUTFILES` lists supplied by the build system.

## Risks And Test Signals
Risks are packaging omissions: wrong target directory names, missing group-list generation, or mode mismatches on installed executable tests. A successful `make install` and populated target directory are the main test signals.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/perf/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/selftest/001 -->
# sources/test-tools/xfstests/tests/selftest/001

## Purpose
Harness selftest that should always pass by printing the canonical quiet success message and exiting zero.

## Important APIs, Types, And Functions
`_begin_fstest selftest` declares xfstests groups/tags: selftest. Imports `common/preamble`.

## Control Flow
The test is a xfstests harness selftest. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: no imperative commands beyond harness declarations.

## State And Persistence
State is mostly external to the script. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; the xfstests runner status, output comparison, crash, timeout, and flake handling paths.

## Risks And Test Signals
Risks: main risk is environmental: missing helper binaries, unsupported mount options, insufficient scratch space, or expected-output drift. Test signals: quiet success usually prints `Silence is golden`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/selftest/001 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/selftest/002 -->
# sources/test-tools/xfstests/tests/selftest/002

## Purpose
Harness selftest that intentionally produces unexpected output while exiting zero, exercising output-mismatch failure handling.

## Important APIs, Types, And Functions
`_begin_fstest selftest` declares xfstests groups/tags: selftest. Imports `common/preamble`.

## Control Flow
The test is a xfstests harness selftest. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: no imperative commands beyond harness declarations.

## State And Persistence
State is mostly external to the script. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; the xfstests runner status, output comparison, crash, timeout, and flake handling paths.

## Risks And Test Signals
Risks: main risk is environmental: missing helper binaries, unsupported mount options, insufficient scratch space, or expected-output drift. Test signals: exit status and golden stdout comparison.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/selftest/002 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/selftest/003 -->
# sources/test-tools/xfstests/tests/selftest/003

## Purpose
Harness selftest that calls `_fail`, exercising explicit test-failure reporting.

## Important APIs, Types, And Functions
`_begin_fstest selftest` declares xfstests groups/tags: selftest. Imports `common/preamble`.

## Control Flow
The test is a xfstests harness selftest. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: no imperative commands beyond harness declarations.

## State And Persistence
State is mostly external to the script. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; the xfstests runner status, output comparison, crash, timeout, and flake handling paths.

## Risks And Test Signals
Risks: main risk is environmental: missing helper binaries, unsupported mount options, insufficient scratch space, or expected-output drift. Test signals: explicit `_fail` calls mark invariant violations.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/selftest/003 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/selftest/004 -->
# sources/test-tools/xfstests/tests/selftest/004

## Purpose
Harness selftest that always calls `_notrun`, exercising skip handling and ensuring later commands are not treated as executed test output.

## Important APIs, Types, And Functions
`_begin_fstest selftest` declares xfstests groups/tags: selftest. Imports `common/preamble`.

## Control Flow
The test is a xfstests harness selftest. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: no imperative commands beyond harness declarations.

## State And Persistence
State is mostly external to the script. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; the xfstests runner status, output comparison, crash, timeout, and flake handling paths.

## Risks And Test Signals
Risks: main risk is environmental: missing helper binaries, unsupported mount options, insufficient scratch space, or expected-output drift. Test signals: unsupported environments are skipped with `_notrun`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/selftest/004 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/selftest/005 -->
# sources/test-tools/xfstests/tests/selftest/005

## Purpose
Dangerous harness selftest that enables sysrq and triggers a kernel crash, used only to validate crash handling in controlled runner environments.

## Important APIs, Types, And Functions
`_begin_fstest dangerous_selftest` declares xfstests groups/tags: dangerous_selftest. Imports `common/preamble`.

## Control Flow
The test is a xfstests harness selftest. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: no imperative commands beyond harness declarations.

## State And Persistence
State is mostly external to the script. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; the xfstests runner status, output comparison, crash, timeout, and flake handling paths.

## Risks And Test Signals
Risks: marked dangerous, so it can crash, hang, or exercise kernel failure paths; uses disruptive kernel/storage state such as cache dropping, shutdown, dm-error, error injection, or crash/hang triggers. Test signals: exit status and golden stdout comparison.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/selftest/005 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/selftest/006 -->
# sources/test-tools/xfstests/tests/selftest/006

## Purpose
Dangerous harness selftest that sleeps forever in a loop, exercising timeout/hang handling.

## Important APIs, Types, And Functions
`_begin_fstest dangerous_selftest` declares xfstests groups/tags: dangerous_selftest. Imports `common/preamble`.

## Control Flow
The test is a xfstests harness selftest. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: no imperative commands beyond harness declarations.

## State And Persistence
State is mostly external to the script. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; the xfstests runner status, output comparison, crash, timeout, and flake handling paths.

## Risks And Test Signals
Risks: marked dangerous, so it can crash, hang, or exercise kernel failure paths. Test signals: exit status and golden stdout comparison.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/selftest/006 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/selftest/007 -->
# sources/test-tools/xfstests/tests/selftest/007

## Purpose
Harness selftest for flaky-output behavior. It randomly prints either the golden success line or a different line while exiting zero.

## Important APIs, Types, And Functions
`_begin_fstest selftest` declares xfstests groups/tags: selftest. Imports `common/preamble`.

## Control Flow
The test is a xfstests harness selftest. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: no imperative commands beyond harness declarations.

## State And Persistence
State is mostly external to the script. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; the xfstests runner status, output comparison, crash, timeout, and flake handling paths.

## Risks And Test Signals
Risks: main risk is environmental: missing helper binaries, unsupported mount options, insufficient scratch space, or expected-output drift. Test signals: quiet success usually prints `Silence is golden`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/selftest/007 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/selftest/Makefile -->
# sources/test-tools/xfstests/tests/selftest/Makefile

## Purpose
Build/install metadata for this xfstests directory. It includes xfstests shared build definitions, derives the package target directory, generates `group.list`, installs executable tests and expected-output files, and leaves development/library install targets empty.

## Important APIs, Types, And Functions
Make variables include `TOPDIR`, directory-specific `*_DIR`, `TARGET_DIR`, and `DIRT`; targets include `default`, `install`, `install-dev`, and `install-lib`; included rule files are `include/builddefs`, `include/buildgrouplist`, and `$(BUILDRULES)`.

## Control Flow
The makefile imports xfstests shared build rules, declares `group.list` as generated dirt, and installs tests, `group.list`, and expected output files into the package tests directory. Development and library install targets are intentionally empty.

## State And Persistence
State is build/install metadata only. Generated state is `group.list`; install state is the packaged test directory populated by `$(INSTALL)`.

## Dependencies And Integration Points
Depends on xfstests top-level make fragments and the `TESTS`/`OUTFILES` lists supplied by the build system.

## Risks And Test Signals
Risks are packaging omissions: wrong target directory names, missing group-list generation, or mode mismatches on installed executable tests. A successful `make install` and populated target directory are the main test signals.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/selftest/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/tmpfs/001 -->
# sources/test-tools/xfstests/tests/tmpfs/001

## Purpose
tmpfs idmapped mount test. It requires idmapped mount support and invokes `src/vfs/vfstest --test-tmpfs` against the configured test device, mountpoint, and fstyp.

## Important APIs, Types, And Functions
`_begin_fstest auto quick idmapped` declares xfstests groups/tags: auto, quick, idmapped. Imports `common/preamble`, `common/filter`. Feature gates/fix annotations include `_require_idmapped_mounts`, `_require_test`. External helper programs used include `$here/src/vfs/vfstest`.

## Control Flow
The test is a tmpfs VFS behavior test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 21: `$here/src/vfs/vfstest --test-tmpfs --device "$TEST_DEV" \`.

## State And Persistence
State is mostly external to the script. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; the `src/vfs/vfstest` binary and kernel idmapped mount support.

## Risks And Test Signals
Risks: main risk is environmental: missing helper binaries, unsupported mount options, insufficient scratch space, or expected-output drift. Test signals: quiet success usually prints `Silence is golden`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/tmpfs/001 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/tmpfs/Makefile -->
# sources/test-tools/xfstests/tests/tmpfs/Makefile

## Purpose
Build/install metadata for this xfstests directory. It includes xfstests shared build definitions, derives the package target directory, generates `group.list`, installs executable tests and expected-output files, and leaves development/library install targets empty.

## Important APIs, Types, And Functions
Make variables include `TOPDIR`, directory-specific `*_DIR`, `TARGET_DIR`, and `DIRT`; targets include `default`, `install`, `install-dev`, and `install-lib`; included rule files are `include/builddefs`, `include/buildgrouplist`, and `$(BUILDRULES)`.

## Control Flow
The makefile imports xfstests shared build rules, declares `group.list` as generated dirt, and installs tests, `group.list`, and expected output files into the package tests directory. Development and library install targets are intentionally empty.

## State And Persistence
State is build/install metadata only. Generated state is `group.list`; install state is the packaged test directory populated by `$(INSTALL)`.

## Dependencies And Integration Points
Depends on xfstests top-level make fragments and the `TESTS`/`OUTFILES` lists supplied by the build system.

## Risks And Test Signals
Risks are packaging omissions: wrong target directory names, missing group-list generation, or mode mismatches on installed executable tests. A successful `make install` and populated target directory are the main test signals.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/tmpfs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/udf/102 -->
# sources/test-tools/xfstests/tests/udf/102

## Purpose
UDF mkfs/check test derived from UDFQA. It prepares a UDF scratch directory/device and runs the UDF filesystem checker against the scratch device.

## Important APIs, Types, And Functions
`_begin_fstest udf` declares xfstests groups/tags: udf. Imports `common/preamble`, `common/filter`. Local helpers: `_cleanup()`. Feature gates/fix annotations include `_require_scratch`.

## Control Flow
The test is a UDF filesystem utility test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 16: `rm -f $tmp.*`; line 26: `_check_udf_filesystem $SCRATCH_DEV`.

## State And Persistence
State is mostly external to the script. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; UDF scratch setup plus mkfs/check utilities.

## Risks And Test Signals
Risks: main risk is environmental: missing helper binaries, unsupported mount options, insufficient scratch space, or expected-output drift. Test signals: exit status and golden stdout comparison.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/udf/102 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/udf/Makefile -->
# sources/test-tools/xfstests/tests/udf/Makefile

## Purpose
Build/install metadata for this xfstests directory. It includes xfstests shared build definitions, derives the package target directory, generates `group.list`, installs executable tests and expected-output files, and leaves development/library install targets empty.

## Important APIs, Types, And Functions
Make variables include `TOPDIR`, directory-specific `*_DIR`, `TARGET_DIR`, and `DIRT`; targets include `default`, `install`, `install-dev`, and `install-lib`; included rule files are `include/builddefs`, `include/buildgrouplist`, and `$(BUILDRULES)`.

## Control Flow
The makefile imports xfstests shared build rules, declares `group.list` as generated dirt, and installs tests, `group.list`, and expected output files into the package tests directory. Development and library install targets are intentionally empty.

## State And Persistence
State is build/install metadata only. Generated state is `group.list`; install state is the packaged test directory populated by `$(INSTALL)`.

## Dependencies And Integration Points
Depends on xfstests top-level make fragments and the `TESTS`/`OUTFILES` lists supplied by the build system.

## Risks And Test Signals
Risks are packaging omissions: wrong target directory names, missing group-list generation, or mode mismatches on installed executable tests. A successful `make install` and populated target directory are the main test signals.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/udf/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/001 -->
# sources/test-tools/xfstests/tests/xfs/001

## Purpose
Tests writable `xfs_db` handling of XFS BMBT extent fields. It creates a file with an extent, finds the inode BMBT prefix, writes zero, every bit value, and beyond-maximum values into extent fields, and also checks core generation writes including hex syntax.

## Important APIs, Types, And Functions
`_begin_fstest db auto quick` declares xfstests groups/tags: db, auto, quick. Imports `common/preamble`, `common/filter`. Local helpers: `_do_bit_test()`, `filter_output()`. Feature gates/fix annotations include `_require_scratch_nocheck`. External helper programs used include `xfs_db`.

## Control Flow
The test is a XFS metadata inspection/editing test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 14: `_do_bit_test()`; line 20: `_scratch_xfs_db -x -c "inode $FILE_INO" -c "write $field 0"`; line 23: `_scratch_xfs_db -x -c "inode $FILE_INO" \`; line 37: `_scratch_mkfs >/dev/null 2>&1`; line 38: `_scratch_mount`; line 46: `_scratch_unmount`; line 62: `_do_bit_test "${prefix}[0].extentflag" $BMBT_EXNTFLAG_BITLEN | filter_output`; line 63: `_do_bit_test "${prefix}[0].startoff" $BMBT_STARTOFF_BITLEN | filter_output`; line 64: `_do_bit_test "${prefix}[0].startblock" $BMBT_STARTBLOCK_BITLEN | filter_output`; line 65: `_do_bit_test "${prefix}[0].blockcount" $BMBT_BLOCKCOUNT_BITLEN | filter_output`.

## State And Persistence
State is kept in shell variables such as `field`, `bits`, `num`, `FILE_INO`, `BMBT_EXNTFLAG_BITLEN`, `BMBT_STARTOFF_BITLEN`, `BMBT_STARTBLOCK_BITLEN`, `BMBT_BLOCKCOUNT_BITLEN`, `prefix`. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; XFS tools and kernel interfaces exercised by the scenario, such as `xfs_db`, `xfs_io`, `xfs_repair`, `xfs_growfs`, `xfs_quota`, log sysfs/debugfs knobs, dump/restore tools, or repair filters.

## Risks And Test Signals
Risks: main risk is environmental: missing helper binaries, unsupported mount options, insufficient scratch space, or expected-output drift. Test signals: volatile paths, ids, device names, or tool output are filtered before golden comparison; explicit `_fail` calls mark invariant violations.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/001 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/002 -->
# sources/test-tools/xfstests/tests/xfs/002

## Purpose
Regression test for v4 secondary superblocks with junk in unused v5 CRC fields. It creates a non-CRC filesystem, writes garbage at the CRC offset in secondary superblocks, mounts, and expects `xfs_growfs` to tolerate the junk.

## Important APIs, Types, And Functions
`_begin_fstest auto quick growfs` declares xfstests groups/tags: auto, quick, growfs. Imports `common/preamble`, `common/filter`. Feature gates/fix annotations include `_require_scratch_nocheck`, `_require_no_large_scratch_dev`, `_require_xfs_nocrc`. External helper programs used include `$XFS_GROWFS_PROG`.

## Control Flow
The test is a XFS online growfs test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 27: `_scratch_mkfs_xfs -m crc=0 -d size=128m >> $seqres.full 2>&1`; line 32: `_scratch_xfs_db -x -c "sb 1" -c "type data" -c "write fill 0xff 224 4"`; line 33: `_scratch_xfs_db -x -c "sb 2" -c "type data" -c "write fill 0xff 224 4"`; line 35: `_scratch_mount`; line 38: `$XFS_GROWFS_PROG $SCRATCH_MNT >> $seqres.full 2>&1 || _fail "growfs failed"`.

## State And Persistence
State is mostly external to the script. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; XFS tools and kernel interfaces exercised by the scenario, such as `xfs_db`, `xfs_io`, `xfs_repair`, `xfs_growfs`, `xfs_quota`, log sysfs/debugfs knobs, dump/restore tools, or repair filters.

## Risks And Test Signals
Risks: main risk is environmental: missing helper binaries, unsupported mount options, insufficient scratch space, or expected-output drift. Test signals: explicit `_fail` calls mark invariant violations.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/002 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/003 -->
# sources/test-tools/xfstests/tests/xfs/003

## Purpose
Historical `xfs_db` stack/type command regression test. It runs several read-only command sequences (`pop`, `push`, `type`, `print`, `ring`) and fails on core files or unexpected nonzero status.

## Important APIs, Types, And Functions
`_begin_fstest db auto quick` declares xfstests groups/tags: db, auto, quick. Imports `common/preamble`, `common/filter`. Local helpers: `test_done()`. Feature gates/fix annotations include `_require_test`. External helper programs used include `xfs_db`.

## Control Flow
The test is a XFS metadata inspection/editing test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 27: `rm -f core`.

## State And Persistence
State is kept in shell variables such as `sts`. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; XFS tools and kernel interfaces exercised by the scenario, such as `xfs_db`, `xfs_io`, `xfs_repair`, `xfs_growfs`, `xfs_quota`, log sysfs/debugfs knobs, dump/restore tools, or repair filters.

## Risks And Test Signals
Risks: main risk is environmental: missing helper binaries, unsupported mount options, insufficient scratch space, or expected-output drift. Test signals: exit status and golden stdout comparison.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/003 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/004 -->
# sources/test-tools/xfstests/tests/xfs/004

## Purpose
`xfs_db freesp` accounting test. It populates a scratch filesystem, compares free-space totals against `df` plus reserved blocks, and verifies percentage columns sum to 100 after filtering volatile values.

## Important APIs, Types, And Functions
`_begin_fstest db auto quick` declares xfstests groups/tags: db, auto, quick. Imports `common/preamble`, `common/filter`. Local helpers: `_cleanup()`, `_populate_scratch()`. Feature gates/fix annotations include `_require_scratch`, `_require_no_large_scratch_dev`. External helper programs used include `xfs_db`, `$DF_PROG`, `$AWK_PROG`, `$XFS_IO_PROG`.

## Control Flow
The test is a XFS metadata inspection/editing test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 17: `_scratch_unmount`; line 18: `rm -f $tmp.*`; line 24: `_try_scratch_mkfs_xfs | tee -a $seqres.full | _filter_mkfs 2>$tmp.mkfs`; line 26: `_scratch_mount`; line 31: `dd if=/dev/zero of=$SCRATCH_MNT/foo count=200 bs=4096 >/dev/null 2>&1 &`; line 32: `dd if=/dev/zero of=$SCRATCH_MNT/goo count=400 bs=4096 >/dev/null 2>&1 &`; line 33: `dd if=/dev/zero of=$SCRATCH_MNT/moo count=800 bs=4096 >/dev/null 2>&1 &`; line 35: `_scratch_unmount # flush everything`; line 36: `_scratch_mount # and then remount`; line 53: `_scratch_xfs_db -r -c "freesp -s" >$tmp.xfs_db`.

## State And Persistence
State is kept in shell variables such as `ans`. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; XFS tools and kernel interfaces exercised by the scenario, such as `xfs_db`, `xfs_io`, `xfs_repair`, `xfs_growfs`, `xfs_quota`, log sysfs/debugfs knobs, dump/restore tools, or repair filters.

## Risks And Test Signals
Risks: main risk is environmental: missing helper binaries, unsupported mount options, insufficient scratch space, or expected-output drift. Test signals: volatile paths, ids, device names, or tool output are filtered before golden comparison.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/004 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/005 -->
# sources/test-tools/xfstests/tests/xfs/005

## Purpose
Primary v5 superblock CRC mount-failure test. It creates a CRC-enabled XFS filesystem, directly corrupts the primary superblock CRC with `xfs_io`, and expects scratch mount to fail.

## Important APIs, Types, And Functions
`_begin_fstest auto quick` declares xfstests groups/tags: auto, quick. Imports `common/preamble`, `common/filter`. Feature gates/fix annotations include `_require_scratch_nocheck`. External helper programs used include `xfs_db`, `$XFS_IO_PROG`.

## Control Flow
The test is a XFS metadata inspection/editing test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 23: `_scratch_mkfs_xfs -m crc=1 >> $seqres.full 2>&1`; line 26: `$XFS_IO_PROG -c "pwrite 224 4" -c fsync $SCRATCH_DEV | _filter_xfs_io`; line 29: `_try_scratch_mount 2>&1 | _filter_error_mount`.

## State And Persistence
State is mostly external to the script. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; XFS tools and kernel interfaces exercised by the scenario, such as `xfs_db`, `xfs_io`, `xfs_repair`, `xfs_growfs`, `xfs_quota`, log sysfs/debugfs knobs, dump/restore tools, or repair filters.

## Risks And Test Signals
Risks: main risk is environmental: missing helper binaries, unsupported mount options, insufficient scratch space, or expected-output drift. Test signals: volatile paths, ids, device names, or tool output are filtered before golden comparison.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/005 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/006 -->
# sources/test-tools/xfstests/tests/xfs/006

## Purpose
XFS fail-at-unmount error-handling test. It uses dm-error, resets XFS sysfs error handling, runs metadata fsstress, loads an error table with lockfs, and verifies unmount does not retry forever and the filesystem can replay after restoring the working table.

## Important APIs, Types, And Functions
`_begin_fstest auto quick mount eio` declares xfstests groups/tags: auto, quick, mount, eio. Imports `common/preamble`, `common/filter`, `common/dmerror`. Local helpers: `_cleanup()`. Feature gates/fix annotations include `_require_scratch`, `_require_dm_target`, `_require_fs_sysfs`. External helper programs used include `fsstress`.

## Control Flow
The test is a XFS functional regression test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 17: `_dmerror_cleanup`; line 19: `rm -f $tmp.*`; line 30: `_scratch_mkfs > $seqres.full 2>&1`; line 31: `_dmerror_init`; line 32: `_dmerror_mount`; line 49: `_run_fsstress -z -n 5000 -p 10 \`; line 66: `_dmerror_load_error_table lockfs`; line 67: `_dmerror_unmount`; line 71: `_dmerror_load_working_table`; line 72: `_dmerror_mount`.

## State And Persistence
State is kept in shell variables such as `attr`. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; XFS tools and kernel interfaces exercised by the scenario, such as `xfs_db`, `xfs_io`, `xfs_repair`, `xfs_growfs`, `xfs_quota`, log sysfs/debugfs knobs, dump/restore tools, or repair filters.

## Risks And Test Signals
Risks: uses disruptive kernel/storage state such as cache dropping, shutdown, dm-error, error injection, or crash/hang triggers. Test signals: explicit `_fail` calls mark invariant violations.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/006 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/007 -->
# sources/test-tools/xfstests/tests/xfs/007

## Purpose
Quota removal (`Q_XQUOTARM`) test. It mounts with user/group and user/project quotas, turns accounting off, runs xfs_quota remove commands, and compares quota metadata inode block counts before and after removal.

## Important APIs, Types, And Functions
`_begin_fstest auto quota quick` declares xfstests groups/tags: auto, quota, quick. Imports `common/preamble`, `common/filter`, `common/quota`. Local helpers: `get_qfile_nblocks()`, `do_test()`. Feature gates/fix annotations include `_require_scratch`, `_require_xfs_quota`, `_require_prjquota`. External helper programs used include `$XFS_QUOTA_PROG`, `xfs_quota`.

## Control Flow
The test is a XFS quota behavior test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 21: `_scratch_mkfs_xfs | _filter_mkfs > /dev/null 2> $tmp.mkfs`; line 26: `_scratch_xfs_db -c "$selector" -c "p core.nblocks"`; line 36: `_scratch_unmount`; line 42: `_qmount`; line 44: `$XFS_QUOTA_PROG -x -c "off -$off_opts" $SCRATCH_MNT`; line 49: `_scratch_unmount`; line 50: `_qmount_option "noquota"`; line 51: `_scratch_mount`; line 64: `$XFS_QUOTA_PROG "${rm_commands[@]}" $SCRATCH_MNT`; line 67: `_scratch_unmount`.

## State And Persistence
State is kept in shell variables such as `qino_1`, `qino_2`, `off_opts`, `rm_commands`, `PQUOTINO`. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; XFS tools and kernel interfaces exercised by the scenario, such as `xfs_db`, `xfs_io`, `xfs_repair`, `xfs_growfs`, `xfs_quota`, log sysfs/debugfs knobs, dump/restore tools, or repair filters.

## Risks And Test Signals
Risks: space/quota tests are sensitive to scratch capacity, mkfs geometry, and background reclaim. Test signals: volatile paths, ids, device names, or tool output are filtered before golden comparison.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/007 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/008 -->
# sources/test-tools/xfstests/tests/xfs/008

## Purpose
Random-hole file layout test. It runs `src/randholes` with buffered and direct I/O parameters, counts holes with `xfs_bmap`, and accepts tolerance for random distribution and extent-size/realtime flags.

## Important APIs, Types, And Functions
`_begin_fstest rw ioctl auto quick` declares xfstests groups/tags: rw, ioctl, auto, quick. Imports `common/preamble`, `common/filter`. Local helpers: `_cleanup()`, `_filter()`, `_do_test()`. Feature gates/fix annotations include `_require_test`. External helper programs used include `$here/src/randholes`, `xfs_bmap`.

## Control Flow
The test is a XFS functional regression test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 17: `rm -f $tmp.*`; line 18: `rm -rf $TEST_DIR/randholes.$$.*`; line 30: `_do_test()`; line 61: `xfs_bmap -vvv $out >>$seqres.full`; line 77: `_do_test 1 50 "-l `expr 200 \* $blksize` -c 50 -b $blksize"`; line 78: `_do_test 2 100 "-l `expr 400 \* $blksize` -c 100 -b $blksize"`; line 79: `_do_test 3 100 "-l `expr 400 \* $blksize` -c 100 -b 512" # test partial blocks`; line 82: `_do_test 4 50 "-d -l `expr 200 \* $blksize` -c 50 -b $blksize"`; line 83: `_do_test 5 100 "-d -l `expr 400 \* $blksize` -c 100 -b $blksize"`.

## State And Persistence
State is kept in shell variables such as `blksize`, `_n`, `_holes`, `_param`, `out`, `count`. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; XFS tools and kernel interfaces exercised by the scenario, such as `xfs_db`, `xfs_io`, `xfs_repair`, `xfs_growfs`, `xfs_quota`, log sysfs/debugfs knobs, dump/restore tools, or repair filters.

## Risks And Test Signals
Risks: main risk is environmental: missing helper binaries, unsupported mount options, insufficient scratch space, or expected-output drift. Test signals: volatile paths, ids, device names, or tool output are filtered before golden comparison.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/008 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/009 -->
# sources/test-tools/xfstests/tests/xfs/009

## Purpose
XFS allocator/preallocation command test using `src/alloc`. It exercises reserve, allocate, unreserve, adjacent reservations, truncate, and O_TRUNC behavior while normalizing block maps and file sizes.

## Important APIs, Types, And Functions
`_begin_fstest rw ioctl auto prealloc quick` declares xfstests groups/tags: rw, ioctl, auto, prealloc, quick. Imports `common/preamble`, `common/filter`. Local helpers: `_cleanup()`, `_init()`, `_filesize()`, `_block_filter()`, `dump_blockrange()`. Feature gates/fix annotations include `_require_scratch`, `_require_xfs_io_command`. External helper programs used include `$AWK_PROG`, `xfs_alloc_file_space`, `$here/src/alloc`.

## Control Flow
The test is a XFS functional regression test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 16: `_scratch_unmount`; line 51: `$AWK_PROG -v bsize="$bsize" '`; line 160: `rm -f $out`; line 173: `rm -f $out`; line 181: `rm -f $out`; line 189: `rm -f $out`; line 201: `rm -f $out`; line 211: `rm -f $out`; line 219: `rm -f $out`; line 230: `rm -f $out`.

## State And Persistence
State is kept in shell variables such as `out`, `bsize`. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; XFS tools and kernel interfaces exercised by the scenario, such as `xfs_db`, `xfs_io`, `xfs_repair`, `xfs_growfs`, `xfs_quota`, log sysfs/debugfs knobs, dump/restore tools, or repair filters.

## Risks And Test Signals
Risks: space/quota tests are sensitive to scratch capacity, mkfs geometry, and background reclaim. Test signals: volatile paths, ids, device names, or tool output are filtered before golden comparison.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/009 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/010 -->
# sources/test-tools/xfstests/tests/xfs/010

## Purpose
Free inode btree repair test. It sparsely populates inodes to build finobt records, corrupts freecount and non-free records, repairs, then corrupts the finobt root in AGI and verifies repair regeneration.

## Important APIs, Types, And Functions
`_begin_fstest auto quick repair` declares xfstests groups/tags: auto, quick, repair. Imports `common/preamble`, `common/filter`, `common/repair`. Local helpers: `_cleanup()`, `_sparse_inode_populate()`, `_filter_dbval()`, `_corrupt_finobt_records()`, `_corrupt_finobt_root()`, `filter_finobt_repair()`. Feature gates/fix annotations include `_require_scratch`, `_require_xfs_mkfs_finobt`, `_require_xfs_finobt`. External helper programs used include `xfs_repair`, `$XFS_DB_PROG`.

## Control Flow
The test is a XFS repair regression test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 22: `_scratch_unmount 2>/dev/null`; line 23: `rm -f $tmp.*`; line 33: `touch $dir/$i`; line 42: `rm -f $dir/$i`; line 60: `$XFS_DB_PROG -x -c "fsb $free_root" -c "type finobt" \`; line 65: `$XFS_DB_PROG -x -c "fsb $free_root" -c "type finobt" \`; line 67: `$XFS_DB_PROG -x -c "fsb $free_root" -c "type finobt" \`; line 76: `$XFS_DB_PROG -x \`; line 88: `_scratch_mkfs_xfs "-m crc=1,finobt=1 -d agcount=2" | _filter_mkfs 2>$seqres.full`; line 91: `_scratch_mount`.

## State And Persistence
State is kept in shell variables such as `dir`, `count`, `dev`, `free_root`. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; XFS tools and kernel interfaces exercised by the scenario, such as `xfs_db`, `xfs_io`, `xfs_repair`, `xfs_growfs`, `xfs_quota`, log sysfs/debugfs knobs, dump/restore tools, or repair filters.

## Risks And Test Signals
Risks: main risk is environmental: missing helper binaries, unsupported mount options, insufficient scratch space, or expected-output drift. Test signals: volatile paths, ids, device names, or tool output are filtered before golden comparison.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/010 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/011 -->
# sources/test-tools/xfstests/tests/xfs/011

## Purpose
XFS log reservation leak test. It freezes the filesystem before and during fsstress and checks sysfs log grant head state against expected zero/minimum reservation ranges.

## Important APIs, Types, And Functions
`_begin_fstest auto freeze log metadata quick` declares xfstests groups/tags: auto, freeze, log, metadata, quick. Imports `common/preamble`, `common/filter`. Local helpers: `_cleanup()`, `_check_scratch_log_state_new()`, `_check_scratch_log_state_old()`, `_check_scratch_log_state()`. Feature gates/fix annotations include `_require_scratch`, `_require_freeze`, `_require_xfs_sysfs`. External helper programs used include `fsstress`, `xfs_freeze`.

## Control Flow
The test is a XFS log behavior test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 27: `xfs_freeze -u $SCRATCH_MNT 2>/dev/null`; line 30: `rm -f $tmp.*`; line 46: `_check_scratch_log_state_new()`; line 58: `_check_scratch_log_state_old()`; line 80: `_check_scratch_log_state()`; line 85: `xfs_freeze -f $SCRATCH_MNT`; line 88: `_check_scratch_log_state_new`; line 90: `_check_scratch_log_state_old`; line 93: `xfs_freeze -u $SCRATCH_MNT`; line 98: `_scratch_mkfs_xfs >> $seqres.full 2>&1`.

## State And Persistence
State is kept in shell variables such as `devname`, `attrprefix`, `space`, `log_head_cycle`, `log_head_bytes`, `cycle`, `bytes`, `iters`. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; XFS tools and kernel interfaces exercised by the scenario, such as `xfs_db`, `xfs_io`, `xfs_repair`, `xfs_growfs`, `xfs_quota`, log sysfs/debugfs knobs, dump/restore tools, or repair filters.

## Risks And Test Signals
Risks: main risk is environmental: missing helper binaries, unsupported mount options, insufficient scratch space, or expected-output drift. Test signals: quiet success usually prints `Silence is golden`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/011 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/012 -->
# sources/test-tools/xfstests/tests/xfs/012

## Purpose
Deterministic hole creation test using `src/holes`. It creates dense, sparse, and no-hole file patterns, counts holes with `xfs_bmap`, and dumps diagnostics on mismatch.

## Important APIs, Types, And Functions
`_begin_fstest rw auto quick` declares xfstests groups/tags: rw, auto, quick. Imports `common/preamble`, `common/filter`. Local helpers: `_cleanup()`, `_filesize()`, `_do_test()`. Feature gates/fix annotations include `_require_test`. External helper programs used include `$AWK_PROG`, `$here/src/holes`, `xfs_bmap`.

## Control Flow
The test is a XFS functional regression test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 18: `rm -f $tmp.*`; line 19: `rm -rf $TEST_DIR/holes.$$.*`; line 30: `_do_test()`; line 75: `xfs_bmap -vvv $out >>$seqres.full`; line 87: `_do_test 1 "-l 40960000 -b 40960 -i 10 -c 1" 100`; line 90: `_do_test 2 "-l 409600000 -b 40960 -i 1000 -c 1" 10`; line 93: `_do_test 3 "-l 40960000 -b 40960 -i 10 -c 10" 0`.

## State And Persistence
State is kept in shell variables such as `_n`, `_param`, `_count`, `failed`, `out`, `count`. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; XFS tools and kernel interfaces exercised by the scenario, such as `xfs_db`, `xfs_io`, `xfs_repair`, `xfs_growfs`, `xfs_quota`, log sysfs/debugfs knobs, dump/restore tools, or repair filters.

## Risks And Test Signals
Risks: main risk is environmental: missing helper binaries, unsupported mount options, insufficient scratch space, or expected-output drift. Test signals: exit status and golden stdout comparison.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/012 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/013 -->
# sources/test-tools/xfstests/tests/xfs/013

## Purpose
Free inode btree workload/stress test. It creates large hardlinked directory clones, randomly replaces files to generate sparse free inode chunks, runs fsstress concurrently, and lets finobt allocation/reuse problems surface as workload or cleanup failures.

## Important APIs, Types, And Functions
`_begin_fstest auto metadata stress` declares xfstests groups/tags: auto, metadata, stress. Imports `common/preamble`, `common/filter`. Local helpers: `filter_enospc()`, `_create()`, `_rand_replace()`, `_cleaner()`. Feature gates/fix annotations include `_require_scratch`, `_require_xfs_mkfs_finobt`, `_require_xfs_finobt`. External helper programs used include `fsstress`.

## Control Flow
The test is a XFS functional regression test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 28: `mkdir -p $dir`; line 44: `rm -f $dir/$file`; line 69: `rm -rf $dir/dir$i`; line 78: `_scratch_mkfs_xfs "-m crc=1,finobt=1 -d agcount=2" | \`; line 80: `_scratch_mount`; line 95: `_run_fsstress_bg -d $SCRATCH_MNT/fsstress -n 9999999 -p 2 -S t`; line 110: `cp -Rl $SCRATCH_MNT/dir$i $SCRATCH_MNT/dir$((i+1)) 2>&1 | \`; line 121: `rm -rf $SCRATCH_MNT/fsstress`; line 122: `rm -rf $SCRATCH_MNT/dir*`; line 125: `_scratch_unmount`.

## State And Persistence
State is kept in shell variables such as `dir`, `count`, `file`, `iters`, `mindirs`, `need`, `COUNT`, `LOOPS`, `MINDIRS`. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; XFS tools and kernel interfaces exercised by the scenario, such as `xfs_db`, `xfs_io`, `xfs_repair`, `xfs_growfs`, `xfs_quota`, log sysfs/debugfs knobs, dump/restore tools, or repair filters.

## Risks And Test Signals
Risks: main risk is environmental: missing helper binaries, unsupported mount options, insufficient scratch space, or expected-output drift. Test signals: volatile paths, ids, device names, or tool output are filtered before golden comparison.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/013 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/014 -->
# sources/test-tools/xfstests/tests/xfs/014

## Purpose
Speculative preallocation reclaim test for ENOSPC and EDQUOT. It creates files with post-EOF preallocations, forces low-space and quota-hard-limit conditions, and verifies new writers reclaim speculative preallocations instead of failing prematurely.

## Important APIs, Types, And Functions
`_begin_fstest auto enospc quick quota prealloc` declares xfstests groups/tags: auto, enospc, quick, quota, prealloc. Imports `common/preamble`, `common/filter`, `common/quota`. Local helpers: `_cleanup()`, `_spec_prealloc_file()`, `_consume_free_space()`, `_test_enospc()`, `_test_edquot()`. Feature gates/fix annotations include `_require_scratch`, `_require_xfs_io_command`, `_require_loop`, `_require_quota`, `_require_user`, `_require_group`. External helper programs used include `$XFS_IO_PROG`, `$DF_PROG`, `$AWK_PROG`, `$XFS_QUOTA_PROG`, `$MKFS_XFS_PROG`.

## Control Flow
The test is a XFS quota behavior test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 27: `_scratch_unmount 2>/dev/null`; line 28: `rm -f $tmp.*`; line 45: `rm -f $file`; line 51: `$XFS_IO_PROG -f -c "pwrite $i 32k" $file >> $seqres.full`; line 56: `$XFS_IO_PROG -c "pwrite 0 128m" $file >> $seqres.full`; line 80: `$XFS_IO_PROG -f -c "falloc 0 ${freesp}M" $dir/spc`; line 91: `rm -rf $dir/*`; line 103: `touch $dir/file.$i`; line 106: `$XFS_IO_PROG -f -c "pwrite 0 $write_size" $dir/file.$i \`; line 120: `rm -rf $dir/*`.

## State And Persistence
State is kept in shell variables such as `size`, `blocks`, `blocksize`, `prealloc_size`, `TOTAL_PREALLOC`, `dir`, `freesp`, `write_size`, `blks`, `orig_sp_time`, `LOOP_FILE`, `LOOP_MNT`, and 1 more. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; XFS tools and kernel interfaces exercised by the scenario, such as `xfs_db`, `xfs_io`, `xfs_repair`, `xfs_growfs`, `xfs_quota`, log sysfs/debugfs knobs, dump/restore tools, or repair filters.

## Risks And Test Signals
Risks: space/quota tests are sensitive to scratch capacity, mkfs geometry, and background reclaim. Test signals: quiet success usually prints `Silence is golden`; explicit `_fail` calls mark invariant violations.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/014 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/015 -->
# sources/test-tools/xfstests/tests/xfs/015

## Purpose
Online growfs inode-allocation test. Background workers exhaust inodes while the filesystem grows at least 4x; after growth, they must allocate inodes in the new space until the expanded inode pool is nearly full.

## Important APIs, Types, And Functions
`_begin_fstest auto enospc growfs` declares xfstests groups/tags: auto, enospc, growfs. Imports `common/preamble`, `common/filter`. Local helpers: `create_file()`. Feature gates/fix annotations include `_require_scratch`, `_require_xfs_scratch_non_zoned`, `_require_fs_space`. External helper programs used include `xfs_growfs`, `$XFS_GROWFS_PROG`, `$DF_PROG`.

## Control Flow
The test is a XFS online growfs test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 39: `_scratch_mkfs >/dev/null 2>&1`; line 40: `_scratch_mount`; line 49: `_scratch_unmount`; line 51: `_scratch_mkfs_sized $((96 * 1024 * 1024)) > $tmp.mkfs.raw`; line 55: `_scratch_mount`; line 62: `mkdir $SCRATCH_MNT/testdir_$i`; line 72: `$XFS_GROWFS_PROG -D $((dblocks * 4)) $SCRATCH_MNT >>$seqres.full`; line 75: `touch $tmp.growfs`; line 82: `$DF_PROG -i $SCRATCH_MNT >>$seqres.full`.

## State And Persistence
State is kept in shell variables such as `nr_worker`, `i`, `total_inode`, `used_inode`. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; XFS tools and kernel interfaces exercised by the scenario, such as `xfs_db`, `xfs_io`, `xfs_repair`, `xfs_growfs`, `xfs_quota`, log sysfs/debugfs knobs, dump/restore tools, or repair filters.

## Risks And Test Signals
Risks: space/quota tests are sensitive to scratch capacity, mkfs geometry, and background reclaim. Test signals: volatile paths, ids, device names, or tool output are filtered before golden comparison.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/015 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/016 -->
# sources/test-tools/xfstests/tests/xfs/016

## Purpose
End-of-log overwrite regression test. It seeds the block after the internal log with a pattern, drives controlled log traffic to near wraparound, advances across the wrap, and repeatedly verifies the block after the log remains unchanged.

## Important APIs, Types, And Functions
`_begin_fstest rw auto quick` declares xfstests groups/tags: rw, auto, quick. Imports `common/preamble`, `common/filter`, `common/quota`. Local helpers: `_cleanup()`, `_block_filter()`, `_init()`, `_log_traffic()`, `_log_size()`, `_log_head()`, `_log_sunit()`, `_after_log()`, `_check_corrupt()`. Feature gates/fix annotations include `_require_scratch`. External helper programs used include `$here/src/devzero`, `$here/src/feature`, `$AWK_PROG`.

## Control Flow
The test is a XFS metadata inspection/editing test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 29: `rm -f $tmp.*`; line 31: `_scratch_unmount 2>/dev/null`; line 46: `_scratch_mkfs_xfs $force_opts >> $seqres.full 2>&1`; line 54: `$here/src/devzero -b 2048 -n $sz_mb -v 198 $SCRATCH_DEV # write 0xc6`; line 66: `_scratch_mkfs_xfs $force_opts >$tmp.mkfs0 2>&1`; line 75: `_qmount_option noquota`; line 93: `$here/src/feature -U $SCRATCH_DEV && \`; line 95: `$here/src/feature -G $SCRATCH_DEV && \`; line 97: `$here/src/feature -P $SCRATCH_DEV && \`; line 103: `touch $out`.

## State And Persistence
State is kept in shell variables such as `log_size_bb`, `log_size`, `force_opts`, `count`, `out`, `f`, `block`, `actual_log_size`, `head`, `lsunit`, `sample_size_ops`, `head1`, and 5 more. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; XFS tools and kernel interfaces exercised by the scenario, such as `xfs_db`, `xfs_io`, `xfs_repair`, `xfs_growfs`, `xfs_quota`, log sysfs/debugfs knobs, dump/restore tools, or repair filters.

## Risks And Test Signals
Risks: space/quota tests are sensitive to scratch capacity, mkfs geometry, and background reclaim. Test signals: volatile paths, ids, device names, or tool output are filtered before golden comparison; unsupported environments are skipped with `_notrun`; explicit `_fail` calls mark invariant violations.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/016 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/017 -->
# sources/test-tools/xfstests/tests/xfs/017

## Purpose
Remount read-only stress test. After each fsstress pass it remounts the scratch filesystem read-only, verifies the log is clean with `xfs_logprint`, runs `xfs_repair -n`, and remounts read-write.

## Important APIs, Types, And Functions
`_begin_fstest mount auto quick stress` declares xfstests groups/tags: mount, auto, quick, stress. Imports `common/preamble`, `common/filter`. Feature gates/fix annotations include `_require_scratch`, `_require_no_large_scratch_dev`. External helper programs used include `xfs_db`, `xfs_logprint`, `xfs_repair`.

## Control Flow
The test is a XFS repair regression test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 24: `_scratch_unmount >/dev/null 2>&1`; line 27: `_scratch_mkfs_xfs >>$seqres.full 2>&1`; line 28: `_scratch_mount`; line 36: `_run_fsstress $FSSTRESS_ARGS`; line 38: `_try_scratch_mount -o remount,ro \`; line 44: `_scratch_xfs_logprint -tb | tee -a $seqres.full \`; line 50: `_scratch_xfs_repair -n >>$seqres.full 2>&1 \`; line 52: `_try_scratch_mount -o remount,rw \`.

## State And Persistence
State is kept in shell variables such as `FSSTRESS_ARGS`. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; XFS tools and kernel interfaces exercised by the scenario, such as `xfs_db`, `xfs_io`, `xfs_repair`, `xfs_growfs`, `xfs_quota`, log sysfs/debugfs knobs, dump/restore tools, or repair filters.

## Risks And Test Signals
Risks: main risk is environmental: missing helper binaries, unsupported mount options, insufficient scratch space, or expected-output drift. Test signals: explicit `_fail` calls mark invariant violations.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/017 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/018 -->
# sources/test-tools/xfstests/tests/xfs/018

## Purpose
Log attribute replay (LARP) test. It enables `/sys/fs/xfs/debug/larp`, uses error injection during xattr set/remove operations across internal, leaf, node, remote, zero-length, and transition cases, remounts to replay the log, and verifies recovered attribute contents by checksum.

## Important APIs, Types, And Functions
`_begin_fstest auto quick attr` declares xfstests groups/tags: auto, quick, attr. Imports `common/preamble`, `common/filter`, `common/attr`, `common/inject`. Local helpers: `_cleanup()`, `test_attr_replay()`, `create_test_file()`, `require_larp()`. Feature gates/fix annotations include `_require_scratch`, `_require_scratch_xfs_crc`, `_require_attrs`, `_require_xfs_io_error_injection`, `_require_xfs_sysfs`. External helper programs used include `$ATTR_PROG`.

## Control Flow
The test is a XFS extended-attribute/log-replay test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 19: `rm -rf $tmp.*`; line 34: `_scratch_inject_error $error_tag`; line 50: `touch $testfile 2>&1 | _filter_scratch`; line 53: `_scratch_remount_dump_log >> $seqres.full`; line 56: `touch $testfile`; line 59: `$ATTR_PROG -l $testfile >> $seqres.full`; line 62: `$ATTR_PROG -q -g $attr_name $testfile 2> /dev/null | md5sum;`; line 73: `touch $filename`; line 77: `$ATTR_PROG -s "attr_name$i" -V $attr_value $filename >> \`; line 84: `touch $SCRATCH_MNT/a`.

## State And Persistence
State is kept in shell variables such as `testfile`, `attr_name`, `attr_value`, `flag`, `error_tag`, `filename`, `count`, `ORIG_XFS_LARP`, `attr16`, `attr17`, `attr64`, `attr256`, and 11 more. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; XFS tools and kernel interfaces exercised by the scenario, such as `xfs_db`, `xfs_io`, `xfs_repair`, `xfs_growfs`, `xfs_quota`, log sysfs/debugfs knobs, dump/restore tools, or repair filters.

## Risks And Test Signals
Risks: uses disruptive kernel/storage state such as cache dropping, shutdown, dm-error, error injection, or crash/hang triggers; xattr and overlay metadata assertions depend on trusted/user xattr support and exact kernel on-disk semantics. Test signals: content or output comparison is a primary failure signal; volatile paths, ids, device names, or tool output are filtered before golden comparison; unsupported environments are skipped with `_notrun`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/018 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/019 -->
# sources/test-tools/xfstests/tests/xfs/019

## Purpose
mkfs protofile test. It builds a prototype file containing directories, special files, symlink, setuid/setgid modes, a real data file, and a reserved file, then creates, checks, mounts, and verifies the resulting filesystem.

## Important APIs, Types, And Functions
`_begin_fstest mkfs auto quick` declares xfstests groups/tags: mkfs, auto, quick. Imports `common/preamble`, `common/filter`. Local helpers: `_cleanup()`, `_full()`, `_filter_stat()`, `_verify_fs()`. Feature gates/fix annotations include `_require_scratch`. External helper programs used include `$here/src/devzero`, `$here/src/lstat64`.

## Control Flow
The test is a XFS functional regression test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 13: `rm -f $seqfull`; line 21: `_scratch_unmount 2>/dev/null`; line 22: `rm -f $tmp.*`; line 56: `$here/src/devzero -b 2048 -n 2 -c -v 44 $tempfile.2`; line 100: `_scratch_unmount >/dev/null 2>&1`; line 103: `_scratch_mkfs_xfs $VERSION -p $protofile >>$seqfull 2>&1`; line 106: `_check_scratch_fs`; line 110: `_scratch_mount >>$seqfull 2>&1`; line 116: `diff -q $SCRATCH_MNT/bigfile $tempfile.2 \`; line 118: `diff -q $SCRATCH_MNT/symlink $tempfile.2 \`.

## State And Persistence
State is kept in shell variables such as `protofile`, `tempfile`, `VERSION`, `rsvblocks`. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; XFS tools and kernel interfaces exercised by the scenario, such as `xfs_db`, `xfs_io`, `xfs_repair`, `xfs_growfs`, `xfs_quota`, log sysfs/debugfs knobs, dump/restore tools, or repair filters.

## Risks And Test Signals
Risks: main risk is environmental: missing helper binaries, unsupported mount options, insufficient scratch space, or expected-output drift. Test signals: content or output comparison is a primary failure signal; volatile paths, ids, device names, or tool output are filtered before golden comparison; unsupported environments are skipped with `_notrun`; explicit `_fail` calls mark invariant violations.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/019 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/020 -->
# sources/test-tools/xfstests/tests/xfs/020

## Purpose
Large sparse filesystem repair regression. It creates a 60TB file-backed XFS image and runs `xfs_repair -f -o ag_stride=32 -t 1`, checking for the historical progress-reporting segfault.

## Important APIs, Types, And Functions
`_begin_fstest auto repair` declares xfstests groups/tags: auto, repair. Imports `common/preamble`, `common/filter`. Local helpers: `_cleanup()`. Feature gates/fix annotations include `_require_test`, `_require_fs_space`. External helper programs used include `xfs_repair`, `xfs_io`, `$MKFS_PROG`, `$XFS_REPAIR_PROG`.

## Control Flow
The test is a XFS repair regression test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 19: `rm -f $tmp.*`; line 20: `rm -f $fsfile`; line 35: `rm -f $fsfile`; line 38: `truncate -s 60t $fsfile || _notrun "Cannot create 60T sparse file for test."`; line 39: `rm -f $fsfile`; line 41: `$MKFS_PROG -t xfs -d size=60t,file,name=$fsfile >/dev/null`; line 42: `$XFS_REPAIR_PROG -f -o ag_stride=32 -t 1 $fsfile >/dev/null 2>&1`.

## State And Persistence
State is kept in shell variables such as `fsfile`. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; XFS tools and kernel interfaces exercised by the scenario, such as `xfs_db`, `xfs_io`, `xfs_repair`, `xfs_growfs`, `xfs_quota`, log sysfs/debugfs knobs, dump/restore tools, or repair filters.

## Risks And Test Signals
Risks: space/quota tests are sensitive to scratch capacity, mkfs geometry, and background reclaim. Test signals: quiet success usually prints `Silence is golden`; unsupported environments are skipped with `_notrun`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/020 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/021 -->
# sources/test-tools/xfstests/tests/xfs/021

## Purpose
`xfs_db` attribute fork format test. It creates small and large extended attributes, records inode numbers, unmounts, and dumps shortform and remote/block attribute structures with filtering for CRC/parent variants.

## Important APIs, Types, And Functions
`_begin_fstest db attr auto quick` declares xfstests groups/tags: db, attr, auto, quick. Imports `common/preamble`, `common/filter`, `common/attr`. Local helpers: `_cleanup()`, `_attr()`, `do_getfattr()`. Feature gates/fix annotations include `_require_scratch`, `_require_attrs`. External helper programs used include `xfs_db`, `$AWK_PROG`.

## Control Flow
The test is a XFS extended-attribute/log-replay test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 21: `_scratch_unmount 2>/dev/null`; line 22: `rm -f $tmp.*`; line 59: `_scratch_unmount >/dev/null 2>&1`; line 62: `_scratch_mkfs_xfs >/dev/null`; line 65: `_scratch_mount`; line 77: `touch $testfile.1`; line 85: `touch $testfile.2`; line 109: `_scratch_unmount >>$seqres.full 2>&1 \`; line 114: `_scratch_xfs_db -r -c "inode $inum_1" -c "print a.sfattr" | \`; line 124: `_scratch_xfs_db -r -c "inode $inum_2" -c "a a.bmx[0].startblock" -c print \`.

## State And Persistence
State is kept in shell variables such as `exit`, `testfile`, `inum_1`, `inum_2`. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; XFS tools and kernel interfaces exercised by the scenario, such as `xfs_db`, `xfs_io`, `xfs_repair`, `xfs_growfs`, `xfs_quota`, log sysfs/debugfs knobs, dump/restore tools, or repair filters.

## Risks And Test Signals
Risks: xattr and overlay metadata assertions depend on trusted/user xattr support and exact kernel on-disk semantics. Test signals: content or output comparison is a primary failure signal; explicit `_fail` calls mark invariant violations.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/021 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/021.cfg -->
# sources/test-tools/xfstests/tests/xfs/021.cfg

## Purpose
Expected-output variant selector for xfs/021. The mapping `parent: parent` tells the harness to use the parent-pointer golden output variant when parent-pointer support is active.

## Important APIs, Types, And Functions
No shell APIs are defined. The file is consumed as data by xfstests expected-output selection.

## Control Flow
There is no runtime control flow. The single mapping line selects a named expected-output variant when the adjacent test links feature-specific output.

## State And Persistence
Persistent state is the literal mapping content; it affects output reconciliation, not filesystem state.

## Dependencies And Integration Points
Integrated by the xfstests harness alongside the adjacent numbered test and its `.out` files.

## Risks And Test Signals
Risk is stale variant labeling: if feature detection changes, the harness can compare against the wrong golden output. The signal is whether the adjacent test links to the intended output file.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/021.cfg -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/022 -->
# sources/test-tools/xfstests/tests/xfs/022

## Purpose
Level-0 xfsdump/xfsrestore-to-tape subdirectory test using an fsstress-created tree. It dumps a subtree, restores it, normalizes variable entry counts, and compares restored listing/content.

## Important APIs, Types, And Functions
`_begin_fstest dump ioctl tape` declares xfstests groups/tags: dump, ioctl, tape. Imports `common/preamble`, `common/dump`. Local helpers: `_cleanup()`. Feature gates/fix annotations include `_require_tape`, `_require_scratch`. External helper programs used include `fsstress`.

## Control Flow
The test is a XFS dump/restore utility test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 23: `rm -f $tmp.*`; line 31: `_scratch_mkfs_xfs >>$seqres.full`; line 32: `_scratch_mount`; line 38: `_do_dump_sub`; line 40: `_do_restore | sed -e "/entries processed$/s/[0-9][0-9]*/NUM/g"`.

## State And Persistence
State is mostly external to the script. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; XFS tools and kernel interfaces exercised by the scenario, such as `xfs_db`, `xfs_io`, `xfs_repair`, `xfs_growfs`, `xfs_quota`, log sysfs/debugfs knobs, dump/restore tools, or repair filters.

## Risks And Test Signals
Risks: dump/restore tape tests depend on configured local or remote tape devices and inventory state. Test signals: content or output comparison is a primary failure signal.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/022 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/023 -->
# sources/test-tools/xfstests/tests/xfs/023

## Purpose
xfsdump/xfsrestore-to-tape subdirectory test using deterministic `src/fill` data. It dumps, restores, diffs content, and compares listings.

## Important APIs, Types, And Functions
`_begin_fstest dump ioctl tape` declares xfstests groups/tags: dump, ioctl, tape. Imports `common/preamble`, `common/dump`. Local helpers: `_cleanup()`. Feature gates/fix annotations include `_require_tape`, `_require_scratch`.

## Control Flow
The test is a XFS dump/restore utility test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 21: `rm -f $tmp.*`; line 30: `_scratch_mkfs_xfs >>$seqres.full`; line 31: `_scratch_mount`; line 34: `_do_dump_sub`; line 35: `_do_restore`.

## State And Persistence
State is mostly external to the script. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; XFS tools and kernel interfaces exercised by the scenario, such as `xfs_db`, `xfs_io`, `xfs_repair`, `xfs_growfs`, `xfs_quota`, log sysfs/debugfs knobs, dump/restore tools, or repair filters.

## Risks And Test Signals
Risks: dump/restore tape tests depend on configured local or remote tape devices and inventory state. Test signals: content or output comparison is a primary failure signal.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/023 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/024 -->
# sources/test-tools/xfstests/tests/xfs/024

## Purpose
Incremental xfsdump test. It records bstat output, takes a full dump, appends more data, takes a level-1 dump, restores, and compares the final tree.

## Important APIs, Types, And Functions
`_begin_fstest dump ioctl tape` declares xfstests groups/tags: dump, ioctl, tape. Imports `common/preamble`, `common/dump`. Local helpers: `_cleanup()`. Feature gates/fix annotations include `_require_tape`, `_require_scratch`. External helper programs used include `$here/src/bstat`.

## Control Flow
The test is a XFS dump/restore utility test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 19: `rm -f $tmp.*`; line 28: `_scratch_mkfs_xfs >>$seqres.full`; line 29: `_scratch_mount`; line 33: `$here/src/bstat $SCRATCH_MNT >>$seqres.full`; line 35: `_do_dump`; line 37: `$here/src/bstat $SCRATCH_MNT >>$seqres.full`; line 39: `_do_dump -l 1`; line 40: `_do_restore`.

## State And Persistence
State is mostly external to the script. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; XFS tools and kernel interfaces exercised by the scenario, such as `xfs_db`, `xfs_io`, `xfs_repair`, `xfs_growfs`, `xfs_quota`, log sysfs/debugfs knobs, dump/restore tools, or repair filters.

## Risks And Test Signals
Risks: dump/restore tape tests depend on configured local or remote tape devices and inventory state. Test signals: content or output comparison is a primary failure signal.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/024 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/025 -->
# sources/test-tools/xfstests/tests/xfs/025

## Purpose
xfsdump/xfsrestore tape test for the `-m` minimum strategy helpers.

## Important APIs, Types, And Functions
`_begin_fstest dump ioctl tape` declares xfstests groups/tags: dump, ioctl, tape. Imports `common/preamble`, `common/dump`. Local helpers: `_cleanup()`. Feature gates/fix annotations include `_require_tape`, `_require_scratch`.

## Control Flow
The test is a XFS dump/restore utility test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 19: `rm -f $tmp.*`; line 28: `_scratch_mkfs_xfs >>$seqres.full`; line 29: `_scratch_mount`; line 32: `_do_dump_min`; line 33: `_do_restore_min`.

## State And Persistence
State is mostly external to the script. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; XFS tools and kernel interfaces exercised by the scenario, such as `xfs_db`, `xfs_io`, `xfs_repair`, `xfs_growfs`, `xfs_quota`, log sysfs/debugfs knobs, dump/restore tools, or repair filters.

## Risks And Test Signals
Risks: dump/restore tape tests depend on configured local or remote tape devices and inventory state. Test signals: content or output comparison is a primary failure signal.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/025 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/026 -->
# sources/test-tools/xfstests/tests/xfs/026

## Purpose
xfsdump/xfsrestore dump-file test instead of tape. It writes a dump file, restores it, and compares content.

## Important APIs, Types, And Functions
`_begin_fstest dump ioctl auto quick` declares xfstests groups/tags: dump, ioctl, auto, quick. Imports `common/preamble`, `common/dump`. Local helpers: `_cleanup()`. Feature gates/fix annotations include `_require_scratch`.

## Control Flow
The test is a XFS dump/restore utility test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 19: `rm -f $tmp.*`; line 26: `_scratch_mkfs_xfs >>$seqres.full`; line 27: `_scratch_mount`; line 30: `_do_dump_file`; line 31: `_do_restore_file`.

## State And Persistence
State is mostly external to the script. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; XFS tools and kernel interfaces exercised by the scenario, such as `xfs_db`, `xfs_io`, `xfs_repair`, `xfs_growfs`, `xfs_quota`, log sysfs/debugfs knobs, dump/restore tools, or repair filters.

## Risks And Test Signals
Risks: dump/restore tape tests depend on configured local or remote tape devices and inventory state. Test signals: content or output comparison is a primary failure signal.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/026 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/027 -->
# sources/test-tools/xfstests/tests/xfs/027

## Purpose
Pipeline dump/restore test for `xfsdump | xfsrestore`, comparing a restored subdirectory tree.

## Important APIs, Types, And Functions
`_begin_fstest dump ioctl auto quick` declares xfstests groups/tags: dump, ioctl, auto, quick. Imports `common/preamble`, `common/dump`. Local helpers: `_cleanup()`. Feature gates/fix annotations include `_require_scratch`.

## Control Flow
The test is a XFS dump/restore utility test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 19: `rm -f $tmp.*`; line 26: `_scratch_mkfs_xfs >>$seqres.full`; line 27: `_scratch_mount`; line 30: `_do_dump_restore`.

## State And Persistence
State is mostly external to the script. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; XFS tools and kernel interfaces exercised by the scenario, such as `xfs_db`, `xfs_io`, `xfs_repair`, `xfs_growfs`, `xfs_quota`, log sysfs/debugfs knobs, dump/restore tools, or repair filters.

## Risks And Test Signals
Risks: main risk is environmental: missing helper binaries, unsupported mount options, insufficient scratch space, or expected-output drift. Test signals: content or output comparison is a primary failure signal.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/027 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/028 -->
# sources/test-tools/xfstests/tests/xfs/028

## Purpose
xfsinvutil inventory pruning test. It creates five dump sessions, records a midpoint date after the third, runs inventory utility pruning, and compares inventory before/after.

## Important APIs, Types, And Functions
`_begin_fstest dump ioctl auto quick` declares xfstests groups/tags: dump, ioctl, auto, quick. Imports `common/preamble`, `common/dump`. Local helpers: `_cleanup()`. Feature gates/fix annotations include `_require_scratch`.

## Control Flow
The test is a XFS dump/restore utility test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 19: `rm -f $tmp.*`; line 26: `_scratch_mkfs_xfs >>$seqres.full`; line 27: `_scratch_mount`; line 36: `_do_dump_file -L "session.$i"`; line 41: `rm $dump_file`; line 54: `_do_invutil -F`.

## State And Persistence
State is kept in shell variables such as `i`, `middate`. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; XFS tools and kernel interfaces exercised by the scenario, such as `xfs_db`, `xfs_io`, `xfs_repair`, `xfs_growfs`, `xfs_quota`, log sysfs/debugfs knobs, dump/restore tools, or repair filters.

## Risks And Test Signals
Risks: main risk is environmental: missing helper binaries, unsupported mount options, insufficient scratch space, or expected-output drift. Test signals: exit status and golden stdout comparison.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/028 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/029 -->
# sources/test-tools/xfstests/tests/xfs/029

## Purpose
mkfs log zeroing/logprint test. It creates a scratch XFS filesystem and filters `xfs_logprint` output to verify log zeroing information without volatile device/uuid values.

## Important APIs, Types, And Functions
`_begin_fstest mkfs logprint log auto quick` declares xfstests groups/tags: mkfs, logprint, log, auto, quick. Imports `common/preamble`, `common/filter`. Local helpers: `filter_logprint()`. Feature gates/fix annotations include `_require_scratch`.

## Control Flow
The test is a XFS log behavior test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 37: `_scratch_mkfs_xfs | _filter_mkfs 2>/dev/null`; line 40: `_scratch_xfs_logprint | filter_logprint`.

## State And Persistence
State is mostly external to the script. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; XFS tools and kernel interfaces exercised by the scenario, such as `xfs_db`, `xfs_io`, `xfs_repair`, `xfs_growfs`, `xfs_quota`, log sysfs/debugfs knobs, dump/restore tools, or repair filters.

## Risks And Test Signals
Risks: main risk is environmental: missing helper binaries, unsupported mount options, insufficient scratch space, or expected-output drift. Test signals: volatile paths, ids, device names, or tool output are filtered before golden comparison.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/029 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/030 -->
# sources/test-tools/xfstests/tests/xfs/030

## Purpose
XFS repair test for damaged AG headers. It clears stale regions, creates a controlled 6-AG filesystem, corrupts superblock/AGF/AGI/AGFL structures with all-zero and all-one patterns, and filters repair output.

## Important APIs, Types, And Functions
`_begin_fstest repair auto quick` declares xfstests groups/tags: repair, auto, quick. Imports `common/preamble`, `common/filter`, `common/repair`, `common/quota`. Local helpers: `_cleanup()`, `_check_ag()`. Feature gates/fix annotations include `_require_scratch`, `_require_no_large_scratch_dev`. External helper programs used include `xfs_repair`, `$here/src/feature`, `$here/src/devzero`.

## Control Flow
The test is a XFS repair regression test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 17: `_scratch_unmount 2>/dev/null`; line 18: `rm -f $tmp.*`; line 28: `_check_ag()`; line 33: `_check_repair $1 "$structure" | uniq |`; line 51: `_scratch_xfs_force_no_metadir`; line 60: `_try_scratch_mkfs_xfs $DSIZE >/dev/null 2>&1`; line 65: `_qmount_option noquota`; line 66: `_scratch_mount`; line 67: `$here/src/feature -U $SCRATCH_DEV && \`; line 69: `$here/src/feature -G $SCRATCH_DEV && \`.

## State And Persistence
State is kept in shell variables such as `DSIZE`, `clear`. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; XFS tools and kernel interfaces exercised by the scenario, such as `xfs_db`, `xfs_io`, `xfs_repair`, `xfs_growfs`, `xfs_quota`, log sysfs/debugfs knobs, dump/restore tools, or repair filters.

## Risks And Test Signals
Risks: space/quota tests are sensitive to scratch capacity, mkfs geometry, and background reclaim. Test signals: volatile paths, ids, device names, or tool output are filtered before golden comparison; unsupported environments are skipped with `_notrun`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/030 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/031 -->
# sources/test-tools/xfstests/tests/xfs/031

## Purpose
Idempotent xfs_repair test. It creates protofile filesystems with shortform, block-form, and leaf-form root directories, runs repair multiple times, and checks later repair output matches the first pass.

## Important APIs, Types, And Functions
`_begin_fstest repair mkfs auto quick` declares xfstests groups/tags: repair, mkfs, auto, quick. Imports `common/preamble`, `common/repair`, `common/filter`. Local helpers: `_check_repair()`, `_create_proto()`. Feature gates/fix annotations include `_require_scratch`, `_require_no_large_scratch_dev`. External helper programs used include `xfs_repair`.

## Control Flow
The test is a XFS repair regression test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 17: `_check_repair()`; line 20: `_scratch_xfs_repair 2>&1 | _filter_repair | tee -a $seqres.full >$tmp.0`; line 24: `_scratch_xfs_repair 2>&1 | _filter_repair >$tmp.$i`; line 25: `diff $tmp.0 $tmp.$i >> $seqres.full`; line 82: `_scratch_mkfs_xfs -p $tmp.proto >$tmp.mkfs0 2>&1`; line 85: `_check_repair`; line 90: `_scratch_mkfs_xfs -p $tmp.proto | _filter_mkfs >/dev/null 2>&1`; line 91: `_check_repair`; line 96: `_scratch_mkfs_xfs -p $tmp.proto | _filter_mkfs >/dev/null 2>&1`; line 97: `_check_repair`.

## State And Persistence
State is kept in shell variables such as `total`, `count`. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; XFS tools and kernel interfaces exercised by the scenario, such as `xfs_db`, `xfs_io`, `xfs_repair`, `xfs_growfs`, `xfs_quota`, log sysfs/debugfs knobs, dump/restore tools, or repair filters.

## Risks And Test Signals
Risks: main risk is environmental: missing helper binaries, unsupported mount options, insufficient scratch space, or expected-output drift. Test signals: content or output comparison is a primary failure signal; volatile paths, ids, device names, or tool output are filtered before golden comparison; unsupported environments are skipped with `_notrun`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/031 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/032 -->
# sources/test-tools/xfstests/tests/xfs/032

## Purpose
xfs_copy coverage for sector/block size combinations. It formats each supported geometry, lightly populates with fsstress, copies with duplicate and normal modes, and validates copied images with `xfs_repair -n -f`.

## Important APIs, Types, And Functions
`_begin_fstest copy auto quick` declares xfstests groups/tags: copy, auto, quick. Imports `common/preamble`. Local helpers: `do_copy()`. Feature gates/fix annotations include `_require_scratch`, `_require_test_program`, `_require_xfs_copy`. External helper programs used include `xfs_copy`, `$here/src/feature`, `$XFS_COPY_PROG`, `xfs_repair`, `$XFS_REPAIR_PROG`.

## Control Flow
The test is a XFS repair regression test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 32: `$XFS_COPY_PROG $opts $SCRATCH_DEV $IMGFILE >> $seqres.full 2>&1 || \`; line 35: `$XFS_REPAIR_PROG -n -f $IMGFILE >> $seqres.full 2>&1 || \`; line 42: `_scratch_mkfs -s size=$SECTORSIZE -b size=$BLOCKSIZE -d size=1g >> $seqres.full 2>&1`; line 58: `_run_fsstress -n 100 -d $SCRATCH_MNT`; line 59: `_scratch_unmount`.

## State And Persistence
State is kept in shell variables such as `SECTORSIZE`, `PAGESIZE`, `IMGFILE`. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; XFS tools and kernel interfaces exercised by the scenario, such as `xfs_db`, `xfs_io`, `xfs_repair`, `xfs_growfs`, `xfs_quota`, log sysfs/debugfs knobs, dump/restore tools, or repair filters.

## Risks And Test Signals
Risks: main risk is environmental: missing helper binaries, unsupported mount options, insufficient scratch space, or expected-output drift. Test signals: quiet success usually prints `Silence is golden`; explicit `_fail` calls mark invariant violations.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/032 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/033 -->
# sources/test-tools/xfstests/tests/xfs/033

## Purpose
XFS repair test for root, realtime bitmap, and realtime summary inode corruption. It selects CRC-specific output variants, disables quota side effects, corrupts target inodes with zero/all-one patterns, and filters known ID/nlink noise.

## Important APIs, Types, And Functions
`_begin_fstest repair auto quick` declares xfstests groups/tags: repair, auto, quick. Imports `common/preamble`, `common/filter`, `common/repair`, `common/quota`. Local helpers: `_cleanup()`, `_check_root_inos()`, `_filter_bad_ids()`, `filter_repair()`. Feature gates/fix annotations include `_require_scratch`, `_require_no_large_scratch_dev`. External helper programs used include `xfs_repair`, `$here/src/feature`.

## Control Flow
The test is a XFS repair regression test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 17: `_scratch_unmount 2>/dev/null`; line 18: `rm -f $tmp.*`; line 28: `_check_root_inos()`; line 31: `_check_repair $1 "inode $rootino"`; line 33: `_check_repair $1 "inode $rbmino"`; line 35: `_check_repair $1 "inode $rsumino"`; line 54: `_scratch_xfs_force_no_metadir`; line 57: `_scratch_mkfs_xfs | _filter_mkfs 2>$tmp.mkfs >/dev/null`; line 60: `_scratch_mkfs_xfs -isize=512 | _filter_mkfs 2>$tmp.mkfs >/dev/null`; line 75: `_qmount_option noquota`.

## State And Persistence
State is kept in shell variables such as `FEATURES`. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; XFS tools and kernel interfaces exercised by the scenario, such as `xfs_db`, `xfs_io`, `xfs_repair`, `xfs_growfs`, `xfs_quota`, log sysfs/debugfs knobs, dump/restore tools, or repair filters.

## Risks And Test Signals
Risks: space/quota tests are sensitive to scratch capacity, mkfs geometry, and background reclaim. Test signals: volatile paths, ids, device names, or tool output are filtered before golden comparison; unsupported environments are skipped with `_notrun`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/033 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/033.cfg -->
# sources/test-tools/xfstests/tests/xfs/033.cfg

## Purpose
Expected-output variant selector for xfs/033. The mapping `crc: crc` tells the harness to use CRC-specific golden output when CRC-enabled XFS metadata is present.

## Important APIs, Types, And Functions
No shell APIs are defined. The file is consumed as data by xfstests expected-output selection.

## Control Flow
There is no runtime control flow. The single mapping line selects a named expected-output variant when the adjacent test links feature-specific output.

## State And Persistence
Persistent state is the literal mapping content; it affects output reconciliation, not filesystem state.

## Dependencies And Integration Points
Integrated by the xfstests harness alongside the adjacent numbered test and its `.out` files.

## Risks And Test Signals
Risk is stale variant labeling: if feature detection changes, the harness can compare against the wrong golden output. The signal is whether the adjacent test links to the intended output file.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/033.cfg -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/034 -->
# sources/test-tools/xfstests/tests/xfs/034

## Purpose
Reference leak regression for handle xfsctls. It creates a file, runs the `src/xfsctl` test program, removes the file, and relies on later filesystem checking to catch unlinked-list corruption.

## Important APIs, Types, And Functions
`_begin_fstest other auto quick` declares xfstests groups/tags: other, auto, quick. Imports `common/preamble`, `common/filter`. Local helpers: `_cleanup()`. Feature gates/fix annotations include `_require_scratch`. External helper programs used include `$here/src/xfsctl`.

## Control Flow
The test is a XFS functional regression test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 16: `rm -f $tmp.*`; line 18: `_scratch_unmount 2>/dev/null`; line 29: `_scratch_unmount >/dev/null 2>&1`; line 32: `_scratch_mkfs_xfs >>$seqres.full`; line 33: `_scratch_mount`; line 37: `_check_scratch_fs`.

## State And Persistence
State is mostly external to the script. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; XFS tools and kernel interfaces exercised by the scenario, such as `xfs_db`, `xfs_io`, `xfs_repair`, `xfs_growfs`, `xfs_quota`, log sysfs/debugfs knobs, dump/restore tools, or repair filters.

## Risks And Test Signals
Risks: main risk is environmental: missing helper binaries, unsupported mount options, insufficient scratch space, or expected-output drift. Test signals: exit status and golden stdout comparison.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/034 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/035 -->
# sources/test-tools/xfstests/tests/xfs/035

## Purpose
Multiple tape dump test. It writes one dump session, rewinds, reformats and writes a second session, restores by the second label, and compares content.

## Important APIs, Types, And Functions
`_begin_fstest dump ioctl tape auto` declares xfstests groups/tags: dump, ioctl, tape, auto. Imports `common/preamble`, `common/dump`. Local helpers: `_cleanup()`. Feature gates/fix annotations include `_require_tape`, `_require_scratch`.

## Control Flow
The test is a XFS dump/restore utility test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 18: `rm -f $tmp.*`; line 27: `_scratch_mkfs_xfs >>$seqres.full`; line 28: `_scratch_mount`; line 31: `_do_dump -L $seq.1`; line 33: `_scratch_unmount`; line 35: `_scratch_mkfs_xfs >>$seqres.full`; line 36: `_scratch_mount`; line 38: `_do_dump -L $seq.2`; line 39: `_do_restore -L $seq.2`.

## State And Persistence
State is mostly external to the script. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; XFS tools and kernel interfaces exercised by the scenario, such as `xfs_db`, `xfs_io`, `xfs_repair`, `xfs_growfs`, `xfs_quota`, log sysfs/debugfs knobs, dump/restore tools, or repair filters.

## Risks And Test Signals
Risks: dump/restore tape tests depend on configured local or remote tape devices and inventory state. Test signals: content or output comparison is a primary failure signal.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/035 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/036 -->
# sources/test-tools/xfstests/tests/xfs/036

## Purpose
Remote IRIX tape minrmt dump/restore test using minimum dump strategy and soft erase.

## Important APIs, Types, And Functions
`_begin_fstest dump ioctl remote tape` declares xfstests groups/tags: dump, ioctl, remote, tape. Imports `common/preamble`, `common/dump`. Local helpers: `_cleanup()`. Feature gates/fix annotations include `_require_tape`, `_require_scratch`.

## Control Flow
The test is a XFS dump/restore utility test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 18: `rm -f $tmp.*`; line 27: `_scratch_mkfs_xfs >>$seqres.full`; line 28: `_scratch_mount`; line 31: `_do_dump_min -o -F`; line 32: `_do_restore_min`.

## State And Persistence
State is mostly external to the script. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; XFS tools and kernel interfaces exercised by the scenario, such as `xfs_db`, `xfs_io`, `xfs_repair`, `xfs_growfs`, `xfs_quota`, log sysfs/debugfs knobs, dump/restore tools, or repair filters.

## Risks And Test Signals
Risks: dump/restore tape tests depend on configured local or remote tape devices and inventory state. Test signals: content or output comparison is a primary failure signal.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/036 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/037 -->
# sources/test-tools/xfstests/tests/xfs/037

## Purpose
Remote Linux tape minrmt dump/restore test using minimum dump strategy and soft erase.

## Important APIs, Types, And Functions
`_begin_fstest dump ioctl remote tape` declares xfstests groups/tags: dump, ioctl, remote, tape. Imports `common/preamble`, `common/dump`. Local helpers: `_cleanup()`. Feature gates/fix annotations include `_require_tape`, `_require_scratch`.

## Control Flow
The test is a XFS dump/restore utility test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 17: `rm -f $tmp.*`; line 26: `_scratch_mkfs_xfs >>$seqres.full`; line 27: `_scratch_mount`; line 30: `_do_dump_min -o -F`; line 31: `_do_restore_min`.

## State And Persistence
State is mostly external to the script. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; XFS tools and kernel interfaces exercised by the scenario, such as `xfs_db`, `xfs_io`, `xfs_repair`, `xfs_growfs`, `xfs_quota`, log sysfs/debugfs knobs, dump/restore tools, or repair filters.

## Risks And Test Signals
Risks: dump/restore tape tests depend on configured local or remote tape devices and inventory state. Test signals: content or output comparison is a primary failure signal.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/037 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/038 -->
# sources/test-tools/xfstests/tests/xfs/038

## Purpose
Remote Linux tape xfsdump/xfsrestore test using normal dump/restore helpers.

## Important APIs, Types, And Functions
`_begin_fstest dump ioctl remote tape` declares xfstests groups/tags: dump, ioctl, remote, tape. Imports `common/preamble`, `common/dump`. Local helpers: `_cleanup()`. Feature gates/fix annotations include `_require_tape`, `_require_scratch`.

## Control Flow
The test is a XFS dump/restore utility test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 17: `rm -f $tmp.*`; line 26: `_scratch_mkfs_xfs >>$seqres.full`; line 27: `_scratch_mount`; line 30: `_do_dump`; line 31: `_do_restore`.

## State And Persistence
State is mostly external to the script. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; XFS tools and kernel interfaces exercised by the scenario, such as `xfs_db`, `xfs_io`, `xfs_repair`, `xfs_growfs`, `xfs_quota`, log sysfs/debugfs knobs, dump/restore tools, or repair filters.

## Risks And Test Signals
Risks: dump/restore tape tests depend on configured local or remote tape devices and inventory state. Test signals: content or output comparison is a primary failure signal.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/038 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/039 -->
# sources/test-tools/xfstests/tests/xfs/039

## Purpose
Remote IRIX tape xfsdump/xfsrestore test using normal dump/restore helpers with remote options.

## Important APIs, Types, And Functions
`_begin_fstest dump ioctl remote tape` declares xfstests groups/tags: dump, ioctl, remote, tape. Imports `common/preamble`, `common/dump`. Local helpers: `_cleanup()`. Feature gates/fix annotations include `_require_tape`, `_require_scratch`.

## Control Flow
The test is a XFS dump/restore utility test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 18: `rm -f $tmp.*`; line 27: `_scratch_mkfs_xfs >>$seqres.full`; line 28: `_scratch_mount`; line 31: `_do_dump -o -F`; line 32: `_do_restore`.

## State And Persistence
State is mostly external to the script. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; XFS tools and kernel interfaces exercised by the scenario, such as `xfs_db`, `xfs_io`, `xfs_repair`, `xfs_growfs`, `xfs_quota`, log sysfs/debugfs knobs, dump/restore tools, or repair filters.

## Risks And Test Signals
Risks: dump/restore tape tests depend on configured local or remote tape devices and inventory state. Test signals: content or output comparison is a primary failure signal.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/039 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/040 -->
# sources/test-tools/xfstests/tests/xfs/040

## Purpose
xfsprogs maintainer comparison test for libxfs. It requires kernel and xfsprogs workareas and runs `tools/libxfs-diff` against the kernel libxfs tree with hunk headers normalized.

## Important APIs, Types, And Functions
`_begin_fstest other auto` declares xfstests groups/tags: other, auto. Imports `common/preamble`, `common/filter`. Local helpers: `filter_libxfs_diff()`.

## Control Flow
The test is a XFS functional regression test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: no imperative commands beyond harness declarations.

## State And Persistence
State is mostly external to the script. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; XFS tools and kernel interfaces exercised by the scenario, such as `xfs_db`, `xfs_io`, `xfs_repair`, `xfs_growfs`, `xfs_quota`, log sysfs/debugfs knobs, dump/restore tools, or repair filters.

## Risks And Test Signals
Risks: main risk is environmental: missing helper binaries, unsupported mount options, insufficient scratch space, or expected-output drift. Test signals: content or output comparison is a primary failure signal; volatile paths, ids, device names, or tool output are filtered before golden comparison; unsupported environments are skipped with `_notrun`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/040 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/041 -->
# sources/test-tools/xfstests/tests/xfs/041

## Purpose
Online growfs QA test. It repeatedly fills the filesystem, grows from 32MB through partial/full allocation-group sizes, remounts, and verifies all generated files against a manifest after each grow.

## Important APIs, Types, And Functions
`_begin_fstest growfs ioctl auto` declares xfstests groups/tags: growfs, ioctl, auto. Imports `common/preamble`, `common/filter`. Local helpers: `_cleanup()`, `_fill()`. Feature gates/fix annotations include `_require_scratch`, `_require_no_large_scratch_dev`, `_require_xfs_scratch_non_zoned`. External helper programs used include `$here/src/fill2fs`, `xfs_growfs`, `$here/src/fill2fs_check`.

## Control Flow
The test is a XFS online growfs test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 19: `_scratch_unmount`; line 20: `rm -f $tmp.*`; line 29: `_scratch_unmount 2>/dev/null`; line 38: `_do_die_on_error=message_only`; line 41: `_scratch_mkfs_xfs -dsize=${agsize}m,agcount=1 2>&1 >/dev/null`; line 45: `_scratch_mount`.

## State And Persistence
State is kept in shell variables such as `_do_die_on_error`, `agsize`, `bsize`, `onemeginblocks`, `grow_size`. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; XFS tools and kernel interfaces exercised by the scenario, such as `xfs_db`, `xfs_io`, `xfs_repair`, `xfs_growfs`, `xfs_quota`, log sysfs/debugfs knobs, dump/restore tools, or repair filters.

## Risks And Test Signals
Risks: main risk is environmental: missing helper binaries, unsupported mount options, insufficient scratch space, or expected-output drift. Test signals: volatile paths, ids, device names, or tool output are filtered before golden comparison.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/041 -->
