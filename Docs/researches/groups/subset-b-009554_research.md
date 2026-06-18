# Research Group subset-b-009554

This grouped report covers XFS xfstests shell tests `270` through `440` as assigned for subset B, excluding the unlisted `333`. Each section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/270 -->
# sources/test-tools/xfstests/tests/xfs/270

## Purpose
Today ro-compat features can't be mounted rw, but a bug allows an ro->rw remount transition. This bug has been fixed on linux kernel (d0a58e8 xfs: disallow rw remount on fs with unknown ro-compat features), and this case is the regression testcase. In this subset it exercises mount/remount acceptance and rejection paths. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto quick mount`. It imports common/preamble, common/filter. Local helpers are `set_bad_rocompat`. Requirement and fix gates include `_fixed_by_kernel_commit 74ad4693b647`; `_require_scratch_nocheck`; `_require_scratch_xfs_crc`; `_require_scratch_shutdown`. External tools and command surfaces visible in the source include `xfs_io`, `xfs_db`, `fsstress`, `mount`, `stat`, `grep`, `awk`, `file`. Key shell state is carried in `ro_compat`, `new_ro_compat`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 23: `_require_scratch_xfs_crc`; line 30: `ro_compat=$(_scratch_xfs_get_metadata_field "features_ro_compat" "sb 0")`; line 31: `echo $ro_compat | grep -q -E '^0x[[:xdigit:]]+$'`; line 32: `if [[ $? != 0  ]]; then`; line 33: `echo ":$ro_compat:"`; line 34: `echo "features_ro_compat has an invalid value."`; line 44: `_scratch_xfs_set_metadata_field "features_ro_compat" "$ro_compat" "sb 0" \`; line 48: `new_ro_compat=$(_scratch_xfs_get_metadata_field "features_ro_compat" "sb 0" \`; line 54: `if [ "$new_ro_compat" != "$ro_compat" ]; then`; plus 3 further source-derived command steps.. The main integration signal is the scripted xfstests workflow and its golden-output comparison. The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate; stress/race coverage is timing-sensitive and can expose hangs rather than clean assertion failures. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/270 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/271 -->
# sources/test-tools/xfstests/tests/xfs/271

## Purpose
Check that getfsmap reports the AG metadata we're expecting. In this subset it exercises filesystem space-map reporting and consistency with file block maps; reverse mapping metadata and owner-accounting validation. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto quick rmap fsmap`. It imports common/preamble, common/filter. Local helpers are `_cleanup`. Requirement and fix gates include `_require_xfs_scratch_rmapbt`; `_require_xfs_io_command "fsmap"`; `_require_xfs_has_feature "$SCRATCH_MNT" reflink`. External tools and command surfaces visible in the source include `xfs_io`, `mount`, `stat`, `grep`, `rm`. Key shell state is carried in `agcount`, `agcount_wiggle`, `has_reflink`, `perag_metadata_exts`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 16: `rm -rf "$tmp".* $TEST_DIR/fsmap $TEST_DIR/testout`; line 22: `_require_xfs_scratch_rmapbt`; line 23: `_require_xfs_io_command "fsmap"`; line 25: `rm -f "$seqres.full"`; line 27: `echo "Format and mount"`; line 28: `_scratch_mkfs > "$seqres.full" 2>&1`; line 29: `_scratch_mount`; line 31: `agcount=$(_xfs_mount_agcount $SCRATCH_MNT)`; line 33: `_xfs_has_feature $SCRATCH_MNT rtgroups && agcount_wiggle=1`; plus 3 further source-derived command steps.. compares GETFSMAP/xfs_io fsmap output against expected owners, devices, or bmap records creates shared extents and CoW/refcount state The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include shared extent and CoW accounting depends on reflink/refcount support. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/271 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/272 -->
# sources/test-tools/xfstests/tests/xfs/272

## Purpose
Check that getfsmap agrees with getbmap. In this subset it exercises filesystem space-map reporting and consistency with file block maps; reverse mapping metadata and owner-accounting validation. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto quick rmap fsmap`. It imports common/preamble, common/filter. Local helpers are `_cleanup`. Requirement and fix gates include `_require_xfs_scratch_rmapbt`; `_require_xfs_io_command "fsmap"`; `_require_test_program "punch-alternating"`; `_require_xfs_scratch_non_zoned`. External tools and command surfaces visible in the source include `xfs_io`, `mount`, `stat`, `grep`, `awk`, `file`, `rm`, `sync`, `punch-alternating`. Key shell state is carried in `ino`, `qstr`, `found`, `data_dev`, `rt_dev`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 16: `rm -rf "$tmp".* $TEST_DIR/fsmap $TEST_DIR/bmap`; line 22: `_require_xfs_scratch_rmapbt`; line 23: `_require_xfs_io_command "fsmap"`; line 26: `rm -f "$seqres.full"`; line 28: `echo "Format and mount"`; line 29: `_scratch_mkfs > "$seqres.full" 2>&1`; line 30: `_scratch_mount`; line 33: `if [ -z "$SCRATCH_RTDEV" ]; then`; line 34: `_require_xfs_scratch_non_zoned`; plus 3 further source-derived command steps.. compares GETFSMAP/xfs_io fsmap output against expected owners, devices, or bmap records The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include realtime device geometry and internal/external rt-device handling affect expected output. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/272 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/273 -->
# sources/test-tools/xfstests/tests/xfs/273

## Purpose
Populate filesystem, check that fsmap -n10000 matches fsmap -n1. In this subset it exercises filesystem space-map reporting and consistency with file block maps; reverse mapping metadata and owner-accounting validation. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto rmap fsmap`. It imports common/preamble, common/filter, common/populate. Local helpers are `_cleanup`. Requirement and fix gates include `_require_scratch`; `_require_populate_commands`; `_require_xfs_io_command "fsmap"`; `_fixed_by_kernel_commit a440a28ddbdc "xfs: fix off-by-one error in fsmap"`. External tools and command surfaces visible in the source include `xfs_io`, `dd`, `mount`, `stat`, `grep`, `awk`, `diff`, `file`, `rm`. Key shell state is carried in `ddev_fsblocks`, `rtdev_fsblocks`, `fsblock_bytes`, `ddev_daddrs`, `rtdev_daddrs`, `ddev_devno`, `rtdev_devno`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 16: `rm -rf "$tmp".* $TEST_DIR/a $TEST_DIR/b`; line 25: `_require_xfs_io_command "fsmap"`; line 29: `rm -f "$seqres.full"`; line 31: `echo "Format and mount"`; line 32: `_scratch_populate_cached nofill > $seqres.full 2>&1`; line 34: `echo "Compare fsmap" | tee -a $seqres.full`; line 35: `_scratch_mount`; line 36: `$XFS_IO_PROG -c 'fsmap -v -n 65536' $SCRATCH_MNT | grep -v 'EXT:' > $TEST_DIR/a`; line 37: `$XFS_IO_PROG -c 'fsmap -v -n 1' $SCRATCH_MNT | grep -v 'EXT:' > $TEST_DIR/b`; plus 3 further source-derived command steps.. compares GETFSMAP/xfs_io fsmap output against expected owners, devices, or bmap records The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include error-injection timing and shutdown/recovery behavior are kernel-sensitive. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/273 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/274 -->
# sources/test-tools/xfstests/tests/xfs/274

## Purpose
Check that getfsmap agrees with getbmap for reflinked files. In this subset it exercises filesystem space-map reporting and consistency with file block maps; reverse mapping metadata and owner-accounting validation. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto quick rmap fsmap`. It imports common/preamble, common/filter, common/reflink. Local helpers are `_cleanup`. Requirement and fix gates include `_require_scratch_reflink`; `_require_xfs_scratch_rmapbt`; `_require_xfs_io_command "fsmap"`; `_require_test_program "punch-alternating"`. External tools and command surfaces visible in the source include `xfs_io`, `mount`, `stat`, `grep`, `file`, `cp`, `rm`, `sync`, `punch-alternating`. Key shell state is carried in `ino`, `qstr`, `found`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 16: `rm -rf "$tmp".* $TEST_DIR/fsmap $TEST_DIR/bmap`; line 24: `_require_xfs_scratch_rmapbt`; line 25: `_require_xfs_io_command "fsmap"`; line 28: `rm -f "$seqres.full"`; line 30: `echo "Format and mount"`; line 31: `_scratch_mkfs > "$seqres.full" 2>&1`; line 32: `_scratch_mount`; line 34: `_pwrite_byte 0x80 0 737373 $SCRATCH_MNT/f1 >> $seqres.full`; line 35: `_scratch_sync`; plus 3 further source-derived command steps.. compares GETFSMAP/xfs_io fsmap output against expected owners, devices, or bmap records creates shared extents and CoW/refcount state The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include realtime device geometry and internal/external rt-device handling affect expected output; shared extent and CoW accounting depends on reflink/refcount support. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/274 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/275 -->
# sources/test-tools/xfstests/tests/xfs/275

## Purpose
Check that getfsmap reports external log devices In this subset it exercises filesystem space-map reporting and consistency with file block maps; reverse mapping metadata and owner-accounting validation; journal/log geometry or recovery behavior. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto quick rmap fsmap`. It imports common/preamble, common/filter. Local helpers are `_cleanup`. Requirement and fix gates include `_require_logdev`; `_require_scratch`; `_require_xfs_io_command "fsmap"`. External tools and command surfaces visible in the source include `xfs_io`, `mount`, `stat`, `grep`, `awk`, `rm`. Key shell state is carried in `data_dev`, `journal_dev`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 16: `rm -rf "$tmp".* $TEST_DIR/fsmap $TEST_DIR/testout`; line 24: `_require_xfs_io_command "fsmap"`; line 26: `rm -f "$seqres.full"`; line 28: `echo "Format and mount"`; line 29: `_scratch_mkfs > "$seqres.full" 2>&1`; line 30: `_scratch_mount`; line 32: `echo "Get fsmap" | tee -a $seqres.full`; line 33: `$XFS_IO_PROG -c 'fsmap -v' $SCRATCH_MNT >> $seqres.full`; line 34: `$XFS_IO_PROG -c 'fsmap -v' $SCRATCH_MNT | tr '[]()' '    ' > $TEST_DIR/fsmap`; plus 1 further source-derived command steps.. compares GETFSMAP/xfs_io fsmap output against expected owners, devices, or bmap records The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include expected-output drift, missing helper binaries, and unsupported scratch geometry are the main hazards. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/275 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/276 -->
# sources/test-tools/xfstests/tests/xfs/276

## Purpose
Check that getfsmap agrees with getbmap when realtime files are present. In this subset it exercises filesystem space-map reporting and consistency with file block maps; reverse mapping metadata and owner-accounting validation; realtime device allocation and realtime reverse-map behavior. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto quick rmap fsmap realtime`. It imports common/preamble, common/filter. Local helpers are `_cleanup`. Requirement and fix gates include `_require_realtime`; `_require_xfs_scratch_rmapbt`; `_require_xfs_io_command "fsmap"`; `_require_test_program "punch-alternating"`; `_require_xfs_scratch_non_zoned`. External tools and command surfaces visible in the source include `xfs_io`, `mount`, `stat`, `grep`, `awk`, `file`, `rm`, `sync`, `punch-alternating`. Key shell state is carried in `ino`, `qstr`, `found`, `data_dev`, `rt_dev`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 16: `rm -rf "$tmp".* $TEST_DIR/fsmap $TEST_DIR/bmap`; line 23: `_require_xfs_scratch_rmapbt`; line 24: `_require_xfs_io_command "fsmap"`; line 27: `rm -f "$seqres.full"`; line 29: `echo "Format and mount"`; line 30: `_scratch_mkfs | _filter_mkfs 2> "$tmp.mkfs" >/dev/null`; line 32: `cat "$tmp.mkfs" > $seqres.full`; line 33: `_scratch_mount`; line 36: `if [ -z "$SCRATCH_RTDEV" ]; then`; plus 3 further source-derived command steps.. compares GETFSMAP/xfs_io fsmap output against expected owners, devices, or bmap records The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include realtime device geometry and internal/external rt-device handling affect expected output. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/276 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/277 -->
# sources/test-tools/xfstests/tests/xfs/277

## Purpose
Check that getfsmap reports internal log devices In this subset it exercises filesystem space-map reporting and consistency with file block maps; reverse mapping metadata and owner-accounting validation; journal/log geometry or recovery behavior. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto quick rmap fsmap`. It imports common/preamble, common/filter. Local helpers are `_cleanup`. Requirement and fix gates include `_require_xfs_scratch_rmapbt`; `_require_xfs_io_command "fsmap"`; `_notrun "Cannot have external log device"`. External tools and command surfaces visible in the source include `xfs_io`, `mount`, `stat`, `grep`, `awk`, `rm`. Key shell state is carried in `data_dev`, `journal_dev`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 16: `rm -rf "$tmp".* $TEST_DIR/fsmap $TEST_DIR/testout`; line 22: `_require_xfs_scratch_rmapbt`; line 23: `_require_xfs_io_command "fsmap"`; line 24: `if [ "$USE_EXTERNAL" = "yes" ] && [ -n "$SCRATCH_LOGDEV" ]; then`; line 28: `rm -f "$seqres.full"`; line 30: `echo "Format and mount"`; line 31: `_scratch_mkfs > "$seqres.full" 2>&1`; line 32: `_scratch_mount`; line 34: `echo "Get fsmap" | tee -a $seqres.full`; plus 3 further source-derived command steps.. compares GETFSMAP/xfs_io fsmap output against expected owners, devices, or bmap records The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include expected-output drift, missing helper binaries, and unsupported scratch geometry are the main hazards. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/277 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/278 -->
# sources/test-tools/xfstests/tests/xfs/278

## Purpose
Test xfs_repair to ensure it fixes the lost+found link count at the first run. See also commit 198b747f255346bca64408875763b6ca0ed3d57d from xfsprogs tree. In this subset it exercises xfs_repair detection and correction of crafted metadata damage. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest repair auto`. It imports common/preamble, common/filter. Local helpers are `set_ifield`. Requirement and fix gates include `_require_scratch`. External tools and command surfaces visible in the source include `xfs_repair`, `mount`, `stat`, `awk`, `mkdir`, `rm`. Key shell state is carried in `DIR_INO`, `SUBDIR_INO`, `sfdir_prefix`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 21: `_scratch_mkfs >$seqres.full 2>&1`; line 22: `_scratch_mount`; line 24: `mkdir -p $SCRATCH_MNT/dir/subdir`; line 30: `_scratch_unmount`; line 32: `echo "Silence is goodness..."`; line 35: `_scratch_xfs_set_metadata_field "$1" 0 "inode $2" >> $seqres.full`; line 54: `echo "===== BEGIN of xfs_repair =====" >> $seqres.full`; line 55: `echo "" >>$seqres.full`; line 57: `_scratch_xfs_repair >> $seqres.full 2>&1`; plus 1 further source-derived command steps.. The main integration signal is the scripted xfstests workflow and its golden-output comparison. The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/278 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/279 -->
# sources/test-tools/xfstests/tests/xfs/279

## Purpose
Test mkfs.xfs against various types of devices with varying logical & physical sector sizes and offsets. In this subset it exercises mkfs.xfs formatting and geometry validation; journal/log geometry or recovery behavior. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto mkfs`. It imports common/preamble, common/filter, common/scsi_debug. Local helpers are `_cleanup`, `_wipe_device`, `_check_mkfs`. Requirement and fix gates include `_require_scsi_debug`. External tools and command surfaces visible in the source include `mkfs.xfs`, `dd`, `stat`, `awk`, `sed`, `rm`. Key shell state is carried in `size`, `device`, `SCSI_DEBUG_DEV`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 17: `rm -f $tmp.*`; line 33: `dd if=/dev/zero of=$device bs=4k count=1 &>/dev/null`; line 38: `echo "==================="`; line 39: `echo "mkfs with opts: $@" | sed -e "s,$SCSI_DEBUG_DEV,DEVICE,"`; line 40: `$MKFS_XFS_PROG $@ 2>/dev/null > $tmp.mkfs.full`; line 41: `if [ $? -ne 0 ]; then`; line 42: `echo "Failed."`; line 45: `echo "Passed."`; line 46: `cat $tmp.mkfs.full | _filter_mkfs >> $seqres.full 2>$tmp.mkfs`; plus 3 further source-derived command steps.. The main integration signal is the scripted xfstests workflow and its golden-output comparison. The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include expected-output drift, missing helper binaries, and unsupported scratch geometry are the main hazards. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/279 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/280 -->
# sources/test-tools/xfstests/tests/xfs/280

## Purpose
Check that GETBMAPX accurately report shared extents. In this subset it exercises reflink, CoW, refcount, and shared-extent behavior. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto quick clone prealloc`. It imports common/preamble, common/filter, common/reflink. Local helpers are `bmap`. Requirement and fix gates include `_require_scratch_reflink`; `_require_xfs_io_command "bmap"`; `_require_xfs_io_command "falloc"`; `_require_congruent_file_oplen $SCRATCH_MNT $blksz`. External tools and command surfaces visible in the source include `xfs_io`, `mount`, `stat`, `grep`, `file`, `mkdir`, `rm`. Key shell state is carried in `testdir`, `blocks`, `blksz`, `sz`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 19: `_require_xfs_io_command "bmap"`; line 20: `_require_xfs_io_command "falloc"`; line 22: `echo "Format and mount"`; line 23: `_scratch_mkfs > $seqres.full 2>&1`; line 24: `_scratch_mount >> $seqres.full 2>&1`; line 27: `mkdir $testdir`; line 34: `echo "Create the original files"`; line 35: `$XFS_IO_PROG -f -c "falloc 0 $sz" $testdir/file1 >> $seqres.full`; line 36: `_pwrite_byte 0x61 0 $sz $testdir/file1 >> $seqres.full`; plus 3 further source-derived command steps.. creates shared extents and CoW/refcount state The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include shared extent and CoW accounting depends on reflink/refcount support. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/280 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/281 -->
# sources/test-tools/xfstests/tests/xfs/281

## Purpose
Test that xfsdump can generate a format 2 dump. In this subset it exercises xfsdump/xfsrestore compatibility and metadata preservation. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest dump ioctl auto quick`. It imports common/preamble, common/dump. Local helpers are `_cleanup`. Requirement and fix gates include `_require_legacy_v2_format`; `_require_scratch`. External tools and command surfaces visible in the source include `xfsdump`, `mount`, `stat`, `diff`, `file`, `rm`. Key shell state is carried in mostly transient harness variables, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 17: `rm -f $tmp.*`; line 25: `_scratch_mkfs_xfs >>$seqres.full`; line 26: `_scratch_mount`; line 30: `echo "*** Dump using format 2"`; line 33: `echo "*** Verify it's a format 2 dump"`; line 36: `echo "*** Restoring format 2 dump"`. uses common/dump dump and restore helpers with content comparison The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include expected-output drift, missing helper binaries, and unsupported scratch geometry are the main hazards. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/281 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/282 -->
# sources/test-tools/xfstests/tests/xfs/282

## Purpose
Test incremental dumps containing a mix of dump formats. level 0 - format 2 level 1 - current format In this subset it exercises xfsdump/xfsrestore compatibility and metadata preservation. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest dump ioctl auto quick`. It imports common/preamble, common/dump. Local helpers are `_cleanup`. Requirement and fix gates include `_require_legacy_v2_format`; `_require_scratch`. External tools and command surfaces visible in the source include `mount`, `stat`, `diff`, `file`, `rm`, `bstat`. Key shell state is carried in mostly transient harness variables, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 19: `rm -f $tmp.*`; line 27: `_scratch_mkfs_xfs >>$seqres.full`; line 28: `_scratch_mount`; line 33: `$here/src/bstat $SCRATCH_MNT >>$seqres.full`; line 35: `echo "*** Level 0 dump, format 2"`; line 39: `$here/src/bstat $SCRATCH_MNT >>$seqres.full`; line 41: `echo "*** Level 1 dump, current format"`; line 44: `echo "*** Restore using format 2 level 0"`; line 48: `echo "*** Restore using current format level 1"`. uses common/dump dump and restore helpers with content comparison The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include expected-output drift, missing helper binaries, and unsupported scratch geometry are the main hazards. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/282 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/283 -->
# sources/test-tools/xfstests/tests/xfs/283

## Purpose
Test incremental dumps containing a mix of dump formats. level 0 - current format level 1 - format 2 In this subset it exercises xfsdump/xfsrestore compatibility and metadata preservation. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest dump ioctl auto quick`. It imports common/preamble, common/dump. Local helpers are `_cleanup`. Requirement and fix gates include `_require_legacy_v2_format`; `_require_scratch`. External tools and command surfaces visible in the source include `mount`, `stat`, `diff`, `file`, `rm`, `bstat`. Key shell state is carried in mostly transient harness variables, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 19: `rm -f $tmp.*`; line 27: `_scratch_mkfs_xfs >>$seqres.full`; line 28: `_scratch_mount`; line 33: `$here/src/bstat $SCRATCH_MNT >>$seqres.full`; line 35: `echo "*** Level 0 dump, current format"`; line 39: `$here/src/bstat $SCRATCH_MNT >>$seqres.full`; line 41: `echo "*** Level 1 dump, format 2"`; line 47: `echo "*** Restore using current format level 0"`; line 51: `echo "*** Restore using format 2 level 1"`. uses common/dump dump and restore helpers with content comparison The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include expected-output drift, missing helper binaries, and unsupported scratch geometry are the main hazards. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/283 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/284 -->
# sources/test-tools/xfstests/tests/xfs/284

## Purpose
Do xfs_metadump, xfs_mdrestore, xfs_copy, xfs_db, xfs_repair and mkfs.xfs on mounted XFS to make sure they refuse to proceed. In this subset it exercises xfsdump/xfsrestore compatibility and metadata preservation; xfs_metadump/xfs_mdrestore metadata image coverage; xfs_repair detection and correction of crafted metadata damage; mkfs.xfs formatting and geometry validation. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto quick dump copy db mkfs repair metadump`. It imports common/preamble, common/filter. Local helpers are `_cleanup`, `filter_mounted`. Requirement and fix gates include `_require_command "$XFS_MDRESTORE_PROG" "xfs_mdrestore"`; `_require_xfs_copy`; `_require_test`; `_require_scratch`; `_require_no_large_scratch_dev`; `_require_scratch_xfs_mdrestore`. External tools and command surfaces visible in the source include `xfs_db`, `xfs_repair`, `xfs_mdrestore`, `xfs_metadump`, `xfs_copy`, `mkfs.xfs`, `mount`, `stat`, `grep`, `file`, `rm`. Key shell state is carried in `METADUMP_FILE`, `COPY_FILE`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 17: `rm -f $tmp.*`; line 18: `rm -f $METADUMP_FILE 2>/dev/null`; line 19: `rm -f $COPY_FILE 2>/dev/null`; line 25: `_require_command "$XFS_MDRESTORE_PROG" "xfs_mdrestore"`; line 26: `_require_xfs_copy`; line 30: `_require_scratch_xfs_mdrestore`; line 34: `grep "mounted" | _filter_scratch | head -1`; line 42: `_scratch_mkfs >> $seqres.full 2>&1`; line 43: `_scratch_mount`; plus 3 further source-derived command steps.. verifies metadump/mdrestore behavior and image fidelity The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include expected-output drift, missing helper binaries, and unsupported scratch geometry are the main hazards. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/284 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/285 -->
# sources/test-tools/xfstests/tests/xfs/285

## Purpose
Race fsstress and xfs_scrub in read-only mode for a while to see if we crash or livelock. In this subset it exercises xfs_scrub online checking or repair of populated/fuzzed filesystems. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto scrub fsstress_scrub`. It imports common/preamble, common/filter, common/fuzzy, common/inject, common/xfs. Local helpers are `_cleanup`. Requirement and fix gates include `_require_scratch`; `_require_xfs_stress_scrub`. External tools and command surfaces visible in the source include `fsstress`, `xfs_scrub`, `mount`, `stat`, `rm`. Key shell state is carried in mostly transient harness variables, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 15: `_scratch_xfs_stress_scrub_cleanup &> /dev/null`; line 16: `rm -r -f $tmp.*`; line 27: `_require_xfs_stress_scrub`; line 29: `_scratch_mkfs > "$seqres.full" 2>&1`; line 30: `_scratch_mount`; line 31: `_scratch_xfs_stress_scrub -S '-n'`; line 34: `echo Silence is golden`. The main integration signal is the scripted xfstests workflow and its golden-output comparison. The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate; error-injection timing and shutdown/recovery behavior are kernel-sensitive; stress/race coverage is timing-sensitive and can expose hangs rather than clean assertion failures. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/285 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/286 -->
# sources/test-tools/xfstests/tests/xfs/286

## Purpose
Race fsstress and xfs_scrub in force-repair mode for a while to see if we crash or livelock. In this subset it exercises xfs_repair detection and correction of crafted metadata damage; xfs_scrub online checking or repair of populated/fuzzed filesystems. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto online_repair fsstress_online_repair`. It imports common/preamble, common/filter, common/fuzzy, common/inject, common/xfs. Local helpers are `_cleanup`. Requirement and fix gates include `_require_scratch`; `_require_xfs_stress_online_repair`. External tools and command surfaces visible in the source include `fsstress`, `xfs_scrub`, `mount`, `stat`, `rm`. Key shell state is carried in mostly transient harness variables, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 15: `_scratch_xfs_stress_scrub_cleanup &> /dev/null`; line 16: `rm -r -f $tmp.*`; line 27: `_require_xfs_stress_online_repair`; line 29: `_scratch_mkfs > "$seqres.full" 2>&1`; line 30: `_scratch_mount`; line 31: `_scratch_xfs_stress_online_repair -S '-k'`; line 34: `echo Silence is golden`. The main integration signal is the scripted xfstests workflow and its golden-output comparison. The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate; error-injection timing and shutdown/recovery behavior are kernel-sensitive; stress/race coverage is timing-sensitive and can expose hangs rather than clean assertion failures. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/286 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/287 -->
# sources/test-tools/xfstests/tests/xfs/287

## Purpose
Test to verify project quota xfs_admin, xfsdump/xfsrestore and xfs_db functionality In this subset it exercises quota accounting, dquot metadata, and quota mount mode handling; xfsdump/xfsrestore compatibility and metadata preservation; xfs_fsr defragmentation and exchangerange recovery. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto dump quota quick`. It imports common/preamble, common/quota, common/dump. Local helpers are `_cleanup`, `_print_projid`. Requirement and fix gates include `_require_xfs_quota`; `_require_scratch`; `_require_projid32bit`; `_require_projid16bit`; `_require_prjquota $SCRATCH_DEV`. External tools and command surfaces visible in the source include `xfs_io`, `xfs_db`, `xfsdump`, `xfsrestore`, `xfs_quota`, `dd`, `mount`, `stat`, `diff`, `file`, `touch`, `mkdir`. Key shell state is carried in `dir`, `inode16a`, `inode32a`, `restore_dir`, `inode16b`, `inode32b`, `inode32v2`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 22: `rm -rf $tmp.*`; line 27: `_scratch_xfs_db -r -c "inode $1" \`; line 32: `_require_xfs_quota`; line 38: `_scratch_mkfs_xfs -i projid32bit=0 -d size=200m >> $seqres.full`; line 48: `mkdir -p $dir`; line 49: `touch $dir/{16,32}bit`; line 52: `$XFS_QUOTA_PROG -x -c "project -s -p $dir/16bit 1234" $SCRATCH_DEV \`; line 54: `$XFS_QUOTA_PROG -x -c "project -s -p $dir/32bit 2123456789" $SCRATCH_DEV \`; line 57: `echo "No 32bit project quotas:"`; plus 3 further source-derived command steps.. uses common/dump dump and restore helpers with content comparison mounts or inspects quota state and dquot accounting The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include quota state can persist through remounts and is sensitive to mount options. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/287 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/288 -->
# sources/test-tools/xfstests/tests/xfs/288

## Purpose
When an attribute leaf block count is 0, xfs_repair should junk that leaf directly (as xfsprogs commit f714016). In this subset it exercises xfs_repair detection and correction of crafted metadata damage; metadata fuzzing through common/fuzzy helper paths; extended attribute metadata behavior; directory metadata layout and traversal behavior. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto quick repair fuzzers attr`. It imports common/preamble, common/filter, common/attr. Local helpers are no local shell helpers. Requirement and fix gates include `_require_scratch`; `_require_attrs`; `_notrun "xfs_db can't set attr hdr.count to 0"`. External tools and command surfaces visible in the source include `xfs_db`, `xfs_repair`, `setfattr`, `mount`, `stat`, `grep`, `sed`, `file`, `touch`, `rm`. Key shell state is carried in `inum`, `maxisize`, `count`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 23: `_xfs_force_no_pptrs`; line 26: `_scratch_mkfs_xfs 2>/dev/null | _filter_mkfs 2>$tmp.mkfs >/dev/null`; line 29: `_scratch_mount`; line 31: `touch $SCRATCH_MNT/$seq.attrfile`; line 39: `$SETFATTR_PROG -n "user.testattr${seq}" \`; line 41: `$SCRATCH_MNT/$seq.attrfile`; line 43: `_scratch_unmount`; line 45: `_scratch_xfs_set_metadata_field "hdr.count" "0" \`; line 50: `count=$(_scratch_xfs_get_metadata_field "hdr.count" \`; plus 3 further source-derived command steps.. The main integration signal is the scripted xfstests workflow and its golden-output comparison. The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate; stress/race coverage is timing-sensitive and can expose hangs rather than clean assertion failures. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/288 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/289 -->
# sources/test-tools/xfstests/tests/xfs/289

## Purpose
Test to ensure xfs_growfs command rejects non-existent mount points and accepts mounted targets. In this subset it exercises mount/remount acceptance and rejection paths. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest growfs auto quick`. It imports common/preamble, common/filter. Local helpers are `_cleanup`. Requirement and fix gates include `_require_test`; `_require_loop`. External tools and command surfaces visible in the source include `xfs_io`, `xfs_growfs`, `mkfs.xfs`, `mount`, `stat`, `file`, `mkdir`, `ln`, `rm`, `truncate`. Key shell state is carried in `tmpfile`, `tmpdir`, `tmpsymlink`, `tmpbind`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 19: `rm -f $tmpsymlink`; line 21: `rm -f $tmpfile`; line 37: `mkdir -p $tmpdir || _fail "!!! failed to create temp mount dir"`; line 39: `echo "=== mkfs.xfs ==="`; line 40: `$MKFS_XFS_PROG -d file,name=$tmpfile,size=16m -f >/dev/null 2>&1`; line 42: `echo "=== truncate ==="`; line 43: `$XFS_IO_PROG -fc "truncate 256m" $tmpfile`; line 45: `echo "=== xfs_growfs - unmounted, command should be rejected ==="`; line 46: `$XFS_GROWFS_PROG $tmpdir 2>&1 |  _filter_test_dir`; plus 3 further source-derived command steps.. The main integration signal is the scripted xfstests workflow and its golden-output comparison. The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include expected-output drift, missing helper binaries, and unsupported scratch geometry are the main hazards. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/289 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/290 -->
# sources/test-tools/xfstests/tests/xfs/290

## Purpose
Makes calls to XFS_IOC_ZERO_RANGE and checks tossed ranges Nothing should be tossed unless the range includes a page boundry Primarily tests page boundries and boundries that are off-by-one to ensure we're only tossing what's expected In this subset it exercises XFS regression behavior exercised through the xfstests harness. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto rw prealloc quick ioctl zero`. It imports common/preamble, common/filter, common/punch. Local helpers are no local shell helpers. Requirement and fix gates include `_require_test`; `_require_xfs_io_command "zero"`. External tools and command surfaces visible in the source include `xfs_io`, `stat`, `sed`, `file`. Key shell state is carried in `testfile`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 25: `_require_xfs_io_command "zero"`; line 29: `_test_block_boundaries 4096 zero _filter_xfs_io_unique $testfile`. The main integration signal is the scripted xfstests workflow and its golden-output comparison. The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include expected-output drift, missing helper binaries, and unsupported scratch geometry are the main hazards. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/290 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/291 -->
# sources/test-tools/xfstests/tests/xfs/291

## Purpose
Test xfs_repair on fragmented multi-block dir2 fs In this subset it exercises xfsdump/xfsrestore compatibility and metadata preservation; xfs_metadump/xfs_mdrestore metadata image coverage; xfs_repair detection and correction of crafted metadata damage; directory metadata layout and traversal behavior. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto repair metadump`. It imports common/preamble, common/filter, common/metadump. Local helpers are `_cleanup`. Requirement and fix gates include `_require_command "$XFS_MDRESTORE_PROG" "xfs_mdrestore"`; `_require_scratch`. External tools and command surfaces visible in the source include `xfs_io`, `xfs_db`, `xfs_repair`, `xfs_mdrestore`, `xfs_metadump`, `dd`, `mount`, `stat`, `diff`, `file`, `touch`, `mkdir`. Key shell state is carried in `logblks`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 16: `rm -r -f $tmp.*`; line 17: `_xfs_cleanup_verify_metadump`; line 24: `_require_command "$XFS_MDRESTORE_PROG" "xfs_mdrestore"`; line 25: `_xfs_setup_verify_metadump`; line 28: `logblks=$(_scratch_find_xfs_min_logblocks -n size=16k -d size=133m)`; line 29: `_scratch_mkfs_sized $((133 * 1048576)) '' -n size=16k -l size=${logblks}b >> $seqres.full 2>&1`; line 30: `_scratch_mount`; line 40: `mkdir $SCRATCH_MNT/fragdir`; line 41: `for I in `seq 0 26200`; do`; plus 3 further source-derived command steps.. verifies metadump/mdrestore behavior and image fidelity The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include expected-output drift, missing helper binaries, and unsupported scratch geometry are the main hazards. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/291 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/292 -->
# sources/test-tools/xfstests/tests/xfs/292

## Purpose
Ensure mkfs with stripe geometry goes into multidisk mode which results in more AGs In this subset it exercises mkfs.xfs formatting and geometry validation. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto mkfs quick`. It imports common/preamble, common/filter. Local helpers are no local shell helpers. Requirement and fix gates include `_require_test`. External tools and command surfaces visible in the source include `xfs_io`, `mkfs.xfs`, `dd`, `stat`, `grep`, `sed`, `file`, `rm`, `truncate`. Key shell state is carried in `fsfile`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 22: `rm -f $fsfile`; line 23: `$XFS_IO_PROG -f -c "truncate 256g" $fsfile`; line 25: `echo "mkfs.xfs without geometry"`; line 26: `mkfs.xfs -f $fsfile | _filter_mkfs 2> $tmp.mkfs > /dev/null`; line 27: `grep -E 'ddev|agcount|agsize' $tmp.mkfs | \`; line 30: `echo "mkfs.xfs with cmdline geometry"`; line 31: `mkfs.xfs -f -d su=16k,sw=5 $fsfile | _filter_mkfs 2> $tmp.mkfs > /dev/null`; line 32: `grep -E 'ddev|agcount|agsize' $tmp.mkfs | \`; line 35: `rm -f $fsfile`. The main integration signal is the scripted xfstests workflow and its golden-output comparison. The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include expected-output drift, missing helper binaries, and unsupported scratch geometry are the main hazards. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/292 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/293 -->
# sources/test-tools/xfstests/tests/xfs/293

## Purpose
Ensure all xfs_io commands are documented In this subset it exercises XFS regression behavior exercised through the xfstests harness. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto quick`. It imports common/preamble, common/filter. Local helpers are no local shell helpers. Requirement and fix gates include `_require_command "$MAN_PROG" man`; `_require_command "$(type -P $CAT)" $CAT`. External tools and command surfaces visible in the source include `xfs_io`, `stat`, `grep`, `awk`. Key shell state is carried in `MANPAGE`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 20: `echo "Silence is golden"`; line 22: `MANPAGE=`$MAN_PROG --path xfs_io``; line 33: `for COMMAND in `$XFS_IO_PROG -c help | awk '{print $1}' | grep -v "^Use"`; do`; line 34: `$CAT "$MANPAGE" | grep -E -q "^\.B.*$COMMAND" || \`; line 35: `echo "$COMMAND not documented in the xfs_io manpage"`. The main integration signal is the scripted xfstests workflow and its golden-output comparison. The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include expected-output drift, missing helper binaries, and unsupported scratch geometry are the main hazards. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/293 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/294 -->
# sources/test-tools/xfstests/tests/xfs/294

## Purpose
Test readdir on fragmented multi-fsb dir blocks If the readahead map ends with a partial multi-fsb dir block, the loop at the end of xfs_dir2_leaf_readbuf() may walk off the end of the mapping array, read garbage, corrupt the loop control counter, and never return. Failure is a hang; KASAN should also catch this. In this subset it exercises directory metadata layout and traversal behavior. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto dir metadata prealloc punch`. It imports common/preamble, common/filter. Local helpers are no local shell helpers. Requirement and fix gates include `_require_scratch`; `_require_test_program "punch-alternating"`; `_require_xfs_io_command "falloc"`; `_require_xfs_io_command "fpunch"`. External tools and command surfaces visible in the source include `xfs_io`, `dd`, `mount`, `stat`, `file`, `touch`, `mkdir`, `rm`, `sync`, `punch-alternating`. Key shell state is carried in `MKFS_OPTIONS`, `space`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 26: `_require_xfs_io_command "falloc"`; line 27: `_require_xfs_io_command "fpunch"`; line 31: `_scratch_mkfs "-d size=512m -n size=8192 -i size=1024" >> $seqres.full 2>&1 \`; line 33: `_scratch_mount`; line 37: `mkdir $SCRATCH_MNT/tmp`; line 38: `for I in `seq 1 10000`; do touch $SCRATCH_MNT/tmp/$I; done`; line 41: `mkdir $SCRATCH_MNT/clusters`; line 42: `for I in `seq 1 32 10000`; do`; line 45: `rm -rf $SCRATCH_MNT/tmp`; plus 3 further source-derived command steps.. The main integration signal is the scripted xfstests workflow and its golden-output comparison. The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/294 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/295 -->
# sources/test-tools/xfstests/tests/xfs/295

## Purpose
Test xfs_logprint w/ multiply-logged inodes & continued transactions In this subset it exercises journal/log geometry or recovery behavior. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto logprint quick`. It imports common/preamble, common/filter, common/attr. Local helpers are no local shell helpers. Requirement and fix gates include `_require_scratch`; `_require_attrs`. External tools and command surfaces visible in the source include `xfs_logprint`, `setfattr`, `mount`, `stat`, `sed`, `touch`, `rm`. Key shell state is carried in `logblks`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 21: `logblks=$(_scratch_find_xfs_min_logblocks)`; line 22: `_scratch_mkfs -l size=${logblks}b >/dev/null 2>&1`; line 27: `_scratch_mount`; line 28: `echo hello > $SCRATCH_MNT/hello; setfattr -n user.name -v value $SCRATCH_MNT/hello`; line 29: `_scratch_unmount`; line 30: `_scratch_xfs_logprint 2>&1 >> $seqres.full`; line 39: `_scratch_mkfs -l size=${logblks}b >/dev/null 2>&1`; line 40: `_scratch_mount`; line 41: `for I in `seq 0 8192`; do`; plus 3 further source-derived command steps.. The main integration signal is the scripted xfstests workflow and its golden-output comparison. The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include expected-output drift, missing helper binaries, and unsupported scratch geometry are the main hazards. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/295 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/296 -->
# sources/test-tools/xfstests/tests/xfs/296

## Purpose
Test that xfsdump/restore preserves file capabilities In this subset it exercises xfsdump/xfsrestore compatibility and metadata preservation. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest dump auto quick`. It imports common/preamble, common/filter, common/dump. Local helpers are `_cleanup`. Requirement and fix gates include `_require_scratch`; `_require_command "$SETCAP_PROG" setcap`; `_require_command "$GETCAP_PROG" getcap`. External tools and command surfaces visible in the source include `xfsdump`, `setfattr`, `getfattr`, `setcap`, `getcap`, `mount`, `stat`, `diff`, `file`, `mkdir`, `rm`. Key shell state is carried in mostly transient harness variables, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 17: `rm -f $tmp.*`; line 29: `_scratch_mkfs_xfs >>$seqres.full`; line 30: `_scratch_mount`; line 32: `mkdir -p $dump_dir`; line 33: `echo test > $dump_dir/testfile`; line 37: `$SETCAP_PROG cap_setgid,cap_setuid+ep $dump_dir/testfile`; line 39: `echo "Checking for xattr on source file"`; line 41: `echo "Checking for capability on source file"`; line 52: `echo "Checking for xattr on restored file"`; plus 1 further source-derived command steps.. uses common/dump dump and restore helpers with content comparison The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include expected-output drift, missing helper binaries, and unsupported scratch geometry are the main hazards. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/296 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/297 -->
# sources/test-tools/xfstests/tests/xfs/297

## Purpose
Test freeze/unfreeze file system randomly under fsstress Regression test for commit: 437a255 xfs: fix direct IO nested transaction deadlock. In this subset it exercises filesystem freeze/unfreeze behavior under stress or error injection; directory metadata layout and traversal behavior. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto freeze`. It imports common/preamble, common/filter. Local helpers are `_cleanup`. Requirement and fix gates include `_require_scratch`; `_require_freeze`. External tools and command surfaces visible in the source include `fsstress`, `xfs_freeze`, `mount`, `stat`, `file`, `mkdir`, `rm`, `sync`. Key shell state is carried in `logblks`, `STRESS_DIR`, `LOOP`, `TIMEOUT`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 18: `xfs_freeze -u $SCRATCH_MNT 2>/dev/null`; line 21: `rm -f $tmp.*`; line 30: `logblks=$(_scratch_find_xfs_min_logblocks -d agcount=16,su=256k,sw=12 -l su=256k)`; line 31: `_scratch_mkfs_xfs -d agcount=16,su=256k,sw=12 -l su=256k,size=${logblks}b >/dev/null 2>&1`; line 32: `_scratch_mount`; line 35: `mkdir -p $STRESS_DIR`; line 39: `_run_fsstress_bg -d $STRESS_DIR -f sync=0 -n 1000 -p 1000 $FSSTRESS_AVOID`; line 42: `echo "Start freeze/unfreeze randomly" | tee -a $seqres.full`; line 44: `while [ $LOOP -gt 0 ];do`; plus 3 further source-derived command steps.. The main integration signal is the scripted xfstests workflow and its golden-output comparison. The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include error-injection timing and shutdown/recovery behavior are kernel-sensitive; stress/race coverage is timing-sensitive and can expose hangs rather than clean assertion failures. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/297 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/298 -->
# sources/test-tools/xfstests/tests/xfs/298

## Purpose
Test that inline symlinks are removed from the inode when an extended attributes forces it into being remote symlink. Warning: this test will ASSERT on unpatched DEBUG XFS. In this subset it exercises extended attribute metadata behavior. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto attr symlink quick`. It imports common/preamble, common/filter. Local helpers are no local shell helpers. Requirement and fix gates include `_require_scratch`. External tools and command surfaces visible in the source include `xfs_db`, `dd`, `mount`, `umount`, `stat`, `awk`, `ln`, `rm`. Key shell state is carried in `SYMLINK_FILE`, `SYMLINK`, `SYMLINK_ADD`, `SIZE`, `inode`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 23: `_scratch_mkfs_xfs >/dev/null 2>&1`; line 32: `while [ $SIZE -lt 1024 ];do`; line 33: `_scratch_mount >/dev/null 2>&1`; line 35: `echo "Testing symlink size $SIZE"`; line 37: `ln -s $SYMLINK $SYMLINK_FILE > /dev/null 2>&1`; line 49: `rm $SYMLINK_FILE`; line 52: `_scratch_unmount >/dev/null 2>&1`; line 53: `_scratch_xfs_db  -c "inode $inode" -c "p core.nextents"`. The main integration signal is the scripted xfstests workflow and its golden-output comparison. The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include expected-output drift, missing helper binaries, and unsupported scratch geometry are the main hazards. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/298 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/299 -->
# sources/test-tools/xfstests/tests/xfs/299

## Purpose
Exercises basic XFS quota functionality, with all 3 quotas together uquota, gquota, pquota uqnoenforce, gqnoenforce, pqnoenforce In this subset it exercises quota accounting, dquot metadata, and quota mount mode handling. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto quota`. It imports common/preamble, common/filter, common/quota. Local helpers are `_cleanup`, `_filter_and_check_blks`, `_exercise`. Requirement and fix gates include `_require_scratch`; `_require_xfs_quota`; `_notrun "Extent size hint is too large ($extsize bytes)"`. External tools and command surfaces visible in the source include `xfs_quota`, `dd`, `mount`, `stat`, `sed`, `file`, `cp`, `rm`. Key shell state is carried in `noextsz`, `extsize`, `projid_file`, `bsize`, `HIDDEN_QUOTA_FILES`, `bsoft`, `bhard`, `isoft`, `ihard`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 22: `_scratch_unmount 2>/dev/null`; line 23: `rm -f $tmp.*`; line 31: `_require_xfs_quota`; line 42: `if (/^\#'$id'\s+(\d+)/ && '$enforce') {`; line 43: `$maximum = '$bhard';`; line 44: `$minimum = '$bhard' * 85/100;`; line 45: `$used = $1 * 1024;`; line 46: `if (($used < $minimum || $used > $maximum) && '$noextsz') {`; line 68: `echo "Using type=$type id=$id" >>$seqres.full`; plus 3 further source-derived command steps.. mounts or inspects quota state and dquot accounting The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include quota state can persist through remounts and is sensitive to mount options. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/299 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/300 -->
# sources/test-tools/xfstests/tests/xfs/300

## Purpose
Test xfs_fsr / exchangerange management of di_forkoff w/ selinux unreliable_in_parallel: file layout appears to be perturbed by load related timing issues. Not 100% sure, but the backwards write does not reliably fragment the source file under heavy external load In this subset it exercises xfs_fsr defragmentation and exchangerange recovery. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto fsr unreliable_in_parallel`. It imports common/preamble, common/filter. Local helpers are no local shell helpers. Requirement and fix gates include `_require_scratch`; `_require_xfs_nocrc`. External tools and command surfaces visible in the source include `xfs_io`, `xfs_fsr`, `dd`, `mount`, `stat`, `grep`, `file`, `touch`, `rm`. Key shell state is carried in `bs`, `oflag`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 20: `_require_xfs_nocrc`; line 25: `[ "$XFS_FSR_PROG" = "" ] && _notrun "xfs_fsr not found"`; line 27: `_scratch_mkfs_xfs -m crc=0 -i size=256 >> $seqres.full 2>&1`; line 30: `mount $SCRATCH_DEV $SCRATCH_MNT`; line 32: `touch $SCRATCH_MNT/$seq.test`; line 35: `$XFS_IO_PROG -f -c "pwrite -S 0x63 0 4096" $SCRATCH_MNT/attrvals >> $seqres.full 2>&1`; line 36: `cat $SCRATCH_MNT/attrvals | attr -s name $SCRATCH_MNT/$seq.test >> $seqres.full 2>&1`; line 40: `for I in `seq 6 -1 0`; do`; line 41: `dd if=/dev/zero of=$SCRATCH_MNT/$seq.test seek=$I bs=${bs} \`; plus 1 further source-derived command steps.. drives xfs_fsr defragmentation paths The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include expected-output drift, missing helper binaries, and unsupported scratch geometry are the main hazards. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/300 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/301 -->
# sources/test-tools/xfstests/tests/xfs/301

## Purpose
Verify multi-stream xfsdump/restore preserves extended attributes In this subset it exercises xfsdump/xfsrestore compatibility and metadata preservation; extended attribute metadata behavior. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto dump`. It imports common/preamble, common/filter, common/dump, common/attr. Local helpers are `_cleanup`. Requirement and fix gates include `_require_scratch`. External tools and command surfaces visible in the source include `xfs_io`, `xfsdump`, `dd`, `mount`, `stat`, `diff`, `file`, `rm`, `truncate`. Key shell state is carried in `attr_name`, `attr_value`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 17: `rm -f $tmp.*`; line 28: `_scratch_mkfs_xfs >>$seqres.full`; line 29: `_scratch_mount`; line 38: `$XFS_IO_PROG -f -c "truncate 1t" $dump_dir/sparsefile >> $seqres.full 2>&1 \`; line 42: `$ATTR_PROG -s $attr_name -V $attr_value $dump_dir/sparsefile >> $seqres.full 2>&1 \`. uses common/dump dump and restore helpers with content comparison The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include expected-output drift, missing helper binaries, and unsupported scratch geometry are the main hazards. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/301 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/302 -->
# sources/test-tools/xfstests/tests/xfs/302

## Purpose
Dump and restore partialmax + 1 wholly-sparse files In this subset it exercises xfsdump/xfsrestore compatibility and metadata preservation. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto dump`. It imports common/preamble, common/filter, common/dump. Local helpers are `_cleanup`. Requirement and fix gates include `_require_scratch`. External tools and command surfaces visible in the source include `xfs_io`, `xfsdump`, `xfsrestore`, `mount`, `stat`, `file`, `mkdir`, `rm`, `truncate`. Key shell state is carried in mostly transient harness variables, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 17: `rm -f $tmp.*`; line 27: `_scratch_mkfs_xfs >>$seqres.full`; line 28: `_scratch_mount`; line 30: `echo "Silence is golden."`; line 31: `mkdir $dump_dir >> $seqres.full 2>&1 || _fail "mkdir \"$dump_dir\" failed"`; line 32: `for i in `seq 1 4`; do`; line 33: `$XFS_IO_PROG -f -c "truncate 1t" $dump_dir/sparsefile$i \`; line 38: `$XFSDUMP_PROG -L session -M label1 -M label2 -f $tmp.stream1 \`; line 41: `$XFSRESTORE_PROG -F -f $tmp.stream1 -f $tmp.stream2 $restore_dir \`. The main integration signal is the scripted xfstests workflow and its golden-output comparison. The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include expected-output drift, missing helper binaries, and unsupported scratch geometry are the main hazards. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/302 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/303 -->
# sources/test-tools/xfstests/tests/xfs/303

## Purpose
Test to verify xfs_quota(8) administrator commands can deal with invalid storage mount point without NULL pointer dereference problem. In this subset it exercises quota accounting, dquot metadata, and quota mount mode handling; mount/remount acceptance and rejection paths. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto quick quota`. It imports common/preamble, common/filter. Local helpers are no local shell helpers. Requirement and fix gates include the script relies on harness defaults and explicit runtime checks instead of `_require_*` gates. External tools and command surfaces visible in the source include `xfs_quota`, `mount`, `stat`. Key shell state is carried in `INVALID_PATH`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 17: `echo "Silence is golden"`; line 25: `$XFS_QUOTA_PROG -x -c 'report -a' $INVALID_PATH	2>/dev/null`; line 26: `$XFS_QUOTA_PROG -x -c 'state -a' $INVALID_PATH	2>/dev/null`; line 27: `$XFS_QUOTA_PROG -x -c 'free -h' $INVALID_PATH		2>/dev/null`; line 28: `$XFS_QUOTA_PROG -x -c 'quot -v' $INVALID_PATH		2>/dev/null`; line 29: `$XFS_QUOTA_PROG -x -c 'remove' $INALID_PATH		2>/dev/null`; line 30: `$XFS_QUOTA_PROG -x -c 'disable' $INVALID_PATH		2>/dev/null`; line 31: `$XFS_QUOTA_PROG -x -c 'enable' $INVALID_PATH		2>/dev/null`. mounts or inspects quota state and dquot accounting The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include quota state can persist through remounts and is sensitive to mount options. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/303 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/304 -->
# sources/test-tools/xfstests/tests/xfs/304

## Purpose
Test to verify that turn group/project quotas off while user quotas are left on. In this subset it exercises quota accounting, dquot metadata, and quota mount mode handling. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto quick quota`. It imports common/preamble, common/filter, common/quota. Local helpers are no local shell helpers. Requirement and fix gates include `_require_scratch`; `_require_xfs_quota`. External tools and command surfaces visible in the source include `xfs_quota`, `mount`, `umount`, `stat`, `mkdir`, `rm`. Key shell state is carried in `QUOTA_DIR`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 20: `_require_xfs_quota`; line 22: `_scratch_mkfs_xfs -m crc=1 >/dev/null 2>&1`; line 29: `mkdir -p $QUOTA_DIR`; line 30: `echo "*** turn off group quotas"`; line 31: `$XFS_QUOTA_PROG -x -c 'disable -g' $SCRATCH_MNT`; line 33: `echo "*** umount"`; line 34: `_scratch_unmount`; line 37: `mkdir -p $QUOTA_DIR`; line 38: `echo "*** turn off project quotas"`; plus 3 further source-derived command steps.. mounts or inspects quota state and dquot accounting The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include quota state can persist through remounts and is sensitive to mount options. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/304 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/305 -->
# sources/test-tools/xfstests/tests/xfs/305

## Purpose
Test to verify that turn group/project quotas off while fsstress and user quotas are left on. In this subset it exercises quota accounting, dquot metadata, and quota mount mode handling. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto quota`. It imports common/preamble, common/filter, common/quota. Local helpers are `_exercise`. Requirement and fix gates include `_require_scratch`; `_require_xfs_quota`. External tools and command surfaces visible in the source include `fsstress`, `xfs_quota`, `mount`, `stat`, `mkdir`. Key shell state is carried in `QUOTA_DIR`, `type`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 20: `_require_xfs_quota`; line 22: `_scratch_mkfs_xfs -m crc=1 >/dev/null 2>&1`; line 33: `mkdir -p $QUOTA_DIR`; line 35: `_run_fsstress_bg -d $QUOTA_DIR -n 1000000 -p 100`; line 37: `$XFS_QUOTA_PROG -x -c "disable -$type" $SCRATCH_DEV`; line 42: `echo "*** turn off group quotas"`; line 44: `echo "*** done"`; line 46: `echo "*** turn off project quotas"`; line 48: `echo "*** done"`; plus 2 further source-derived command steps.. mounts or inspects quota state and dquot accounting The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include quota state can persist through remounts and is sensitive to mount options; stress/race coverage is timing-sensitive and can expose hangs rather than clean assertion failures. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/305 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/306 -->
# sources/test-tools/xfstests/tests/xfs/306

## Purpose
Regression test for an XFS multi-block buffer logging bug. The XFS bug results in a panic when a non-contiguous multi-block buffer is mapped and logged in a particular manner, such that only regions beyond the first fsb-sized mapping are logged. The crash occurs asynchronous to transaction submission, when the associated buffer log item is pushed from the CIL (i.e., when the log is subsequently flushed). In this subset it exercises journal/log geometry or recovery behavior. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto quick punch`. It imports common/preamble. Local helpers are no local shell helpers. Requirement and fix gates include `_require_scratch_nocheck	# check complains about single AG fs`; `_require_xfs_io_command "fpunch"`; `_require_command $UUIDGEN_PROG uuidgen`; `_require_test_program "punch-alternating"`; `_require_xfs_scratch_non_zoned`. External tools and command surfaces visible in the source include `xfs_io`, `dd`, `mount`, `stat`, `file`, `touch`, `mkdir`, `ln`, `sync`, `punch-alternating`. Key shell state is carried in `i`, `f`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 23: `_require_xfs_io_command "fpunch"`; line 33: `_scratch_mkfs_xfs -d size=100m -n size=64k >> $seqres.full 2>&1`; line 34: `_scratch_mount`; line 38: `_require_xfs_scratch_non_zoned`; line 42: `mkdir $SCRATCH_MNT/src`; line 43: `for i in $(seq 0 1023); do`; line 44: `touch $SCRATCH_MNT/src/`$UUIDGEN_PROG``; line 48: `for i in $(seq 0 3); do`; line 49: `mkdir $SCRATCH_MNT/$i`; plus 3 further source-derived command steps.. The main integration signal is the scripted xfstests workflow and its golden-output comparison. The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/306 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/307 -->
# sources/test-tools/xfstests/tests/xfs/307

## Purpose
Test recovery of "lost" CoW blocks: - Use the debugger to fake a leftover CoW extent - See if xfs_repair fixes it In this subset it exercises reflink, CoW, refcount, and shared-extent behavior; xfs_repair detection and correction of crafted metadata damage. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto quick clone`. It imports common/preamble, common/filter, common/reflink. Local helpers are `_get_agf_data`, `_set_agf_data`, `_get_sb_data`, `_set_sb_data`, `_filter_leftover`, `_dump_status`. Requirement and fix gates include `_require_scratch_reflink`. External tools and command surfaces visible in the source include `xfs_db`, `xfs_repair`, `dd`, `mount`, `stat`, `grep`, `awk`, `sed`, `file`, `rm`. Key shell state is carried in `is_rmap`, `field`, `value`, `bno_lvl`, `bno_nr`, `refc_lvl`, `refc_nr`, `rmap_lvl`, `rmap_nr`, `bno`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 20: `echo "Format"`; line 21: `_scratch_mkfs > $seqres.full 2>&1`; line 22: `_scratch_mount >> $seqres.full`; line 23: `is_rmap=$(_xfs_has_feature $SCRATCH_MNT rmapbt -v)`; line 24: `_scratch_unmount`; line 30: `_scratch_xfs_db -c 'agf 1' "$@" -c "p $field"  | awk '{print $3}'`; line 38: `_scratch_xfs_db -x -c 'agf 1' "$@" -c "write $field -- $value"  >> $seqres.full`; line 42: `_scratch_xfs_get_sb_field "$@"`; line 46: `_scratch_xfs_set_sb_field "$@" >> $seqres.full`; plus 3 further source-derived command steps.. creates shared extents and CoW/refcount state The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include shared extent and CoW accounting depends on reflink/refcount support. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/307 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/308 -->
# sources/test-tools/xfstests/tests/xfs/308

## Purpose
Test recovery of "lost" CoW blocks: - Use the debugger to fake a leftover CoW extent - See if mount/umount fixes it In this subset it exercises reflink, CoW, refcount, and shared-extent behavior; mount/remount acceptance and rejection paths. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto quick clone`. It imports common/preamble, common/filter, common/reflink. Local helpers are `_get_agf_data`, `_set_agf_data`, `_get_sb_data`, `_set_sb_data`, `_filter_leftover`, `_dump_status`. Requirement and fix gates include `_require_scratch_reflink`. External tools and command surfaces visible in the source include `xfs_db`, `xfs_repair`, `dd`, `mount`, `umount`, `stat`, `grep`, `awk`, `sed`, `file`, `rm`. Key shell state is carried in `is_rmap`, `field`, `value`, `bno_lvl`, `bno_nr`, `refc_lvl`, `refc_nr`, `rmap_lvl`, `rmap_nr`, `bno`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 20: `echo "Format"`; line 21: `_scratch_mkfs > $seqres.full 2>&1`; line 22: `_scratch_mount >> $seqres.full`; line 23: `is_rmap=$(_xfs_has_feature $SCRATCH_MNT rmapbt -v)`; line 24: `_scratch_xfs_unmount_dirty`; line 30: `_scratch_xfs_db -c 'agf 1' "$@" -c "p $field"  | awk '{print $3}'`; line 38: `_scratch_xfs_db -x -c 'agf 1' "$@" -c "write $field -- $value"  >> $seqres.full`; line 42: `_scratch_xfs_get_sb_field "$@"`; line 46: `_scratch_xfs_set_sb_field "$@" >> $seqres.full`; plus 3 further source-derived command steps.. creates shared extents and CoW/refcount state The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include shared extent and CoW accounting depends on reflink/refcount support. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/308 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/309 -->
# sources/test-tools/xfstests/tests/xfs/309

## Purpose
Ensure that we can create enough distinct reflink entries to force creation of a multi-level refcount btree by reflinking a file a number of times and truncating the copies at successively lower sizes. Delete and recreate a few times to exercise the refcount btree grow/shrink functions. In this subset it exercises reflink, CoW, refcount, and shared-extent behavior. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto clone`. It imports common/preamble, common/filter, common/reflink. Local helpers are `_cleanup`. Requirement and fix gates include `_require_scratch_reflink`; `_require_cp_reflink`. External tools and command surfaces visible in the source include `mount`, `stat`, `file`, `mkdir`, `cp`, `rm`, `sync`, `truncate`. Key shell state is carried in `testdir`, `blksz`, `nr_blks`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 19: `_scratch_unmount > /dev/null 2>&1`; line 20: `rm -rf $tmp.*`; line 30: `_scratch_mkfs >/dev/null 2>&1`; line 31: `_scratch_mount`; line 34: `mkdir $testdir`; line 36: `echo "Create the original file blocks"`; line 40: `for i in 1 2 x; do`; line 41: `_pwrite_byte 0x61 0 $((blksz * nr_blks)) $testdir/file1 >> $seqres.full`; line 43: `echo "$i: Reflink a bunch of times"`; plus 3 further source-derived command steps.. creates shared extents and CoW/refcount state The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include shared extent and CoW accounting depends on reflink/refcount support. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/309 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/310 -->
# sources/test-tools/xfstests/tests/xfs/310

## Purpose
Create a file with more than 2^21 blocks (the max length of a bmbt record). In this subset it exercises reverse mapping metadata and owner-accounting validation; reflink, CoW, refcount, and shared-extent behavior. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto clone rmap prealloc`. It imports common/preamble, common/filter, common/dmhugedisk. Local helpers are `_cleanup`. Requirement and fix gates include `_require_xfs_scratch_rmapbt`; `_require_scratch_nocheck`; `_require_xfs_io_command "falloc"`. External tools and command surfaces visible in the source include `xfs_io`, `xfs_db`, `xfs_repair`, `dd`, `mount`, `umount`, `stat`, `grep`, `file`, `mkdir`, `rm`. Key shell state is carried in `testdir`, `blksz`, `nr_blks`, `sectors`, `inum`, `nr_bmaps`, `nr_rmaps`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 16: `umount $SCRATCH_MNT > /dev/null 2>&1`; line 18: `rm -rf $tmp.*`; line 25: `_require_xfs_scratch_rmapbt`; line 27: `_require_xfs_io_command "falloc"`; line 30: `echo "Figure out block size"`; line 31: `_scratch_mkfs >/dev/null 2>&1`; line 32: `_scratch_mount >> $seqres.full`; line 37: `_scratch_unmount`; line 39: `echo "Format huge device"`; plus 3 further source-derived command steps.. The main integration signal is the scripted xfstests workflow and its golden-output comparison. The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/310 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/311 -->
# sources/test-tools/xfstests/tests/xfs/311

## Purpose
Test to reproduce an XFS unmount crash due to races with directory readahead. XFS had a bug in which unmount would proceed with a readahead I/O in flight. If the unmount deconstructed the log by the time I/O completion occurs, certain metadata read verifier checks could access invalid memory and cause a panic. In this subset it exercises mount/remount acceptance and rejection paths; directory metadata layout and traversal behavior; journal/log geometry or recovery behavior. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto quick`. It imports common/preamble, common/dmdelay. Local helpers are `_cleanup`. Requirement and fix gates include `_require_scratch`; `_require_dm_target delay`. External tools and command surfaces visible in the source include `xfs_io`, `mount`, `stat`, `mkdir`, `rm`, `sync`. Key shell state is carried in mostly transient harness variables, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 20: `rm -f $tmp.*`; line 21: `_scratch_unmount > /dev/null 2>&1`; line 33: `echo "Silence is golden."`; line 35: `_scratch_mkfs_xfs >> $seqres.full 2>&1`; line 42: `mkdir $SCRATCH_MNT/dir`; line 43: `for i in $(seq 0 999); do`; line 44: `echo > $SCRATCH_MNT/dir/$i`; line 59: `$XFS_IO_PROG -c "bmap -v" $SCRATCH_MNT/dir >> $seqres.full 2>&1`. The main integration signal is the scripted xfstests workflow and its golden-output comparison. The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include stress/race coverage is timing-sensitive and can expose hangs rather than clean assertion failures. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/311 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/312 -->
# sources/test-tools/xfstests/tests/xfs/312

## Purpose
Reflink a file with a few dozen extents, CoW a few blocks, and rm. Inject an error during block remap to test log recovery. In this subset it exercises reflink, CoW, refcount, and shared-extent behavior; journal/log geometry or recovery behavior. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto quick clone punch`. It imports common/preamble, common/filter, common/reflink, common/inject. Local helpers are `_cleanup`. Requirement and fix gates include `_require_cp_reflink`; `_require_scratch_reflink`; `_require_xfs_io_command "fpunch"`; `_require_xfs_io_error_injection "bmap_finish_one"`; `_require_congruent_file_oplen $SCRATCH_MNT $blksz`. External tools and command surfaces visible in the source include `xfs_io`, `mount`, `stat`, `file`, `touch`, `cp`, `rm`, `sync`. Key shell state is carried in `blksz`, `blks`, `sz`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 17: `_scratch_unmount > /dev/null 2>&1`; line 18: `rm -rf $tmp.*`; line 28: `_require_xfs_io_command "fpunch"`; line 29: `_require_xfs_io_error_injection "bmap_finish_one"`; line 34: `echo "Format filesystem"`; line 35: `_scratch_mkfs >/dev/null 2>&1`; line 36: `_scratch_mount >> $seqres.full`; line 39: `echo "Create files"`; line 40: `_pwrite_byte 0x66 0 $sz $SCRATCH_MNT/file1 >> $seqres.full`; plus 3 further source-derived command steps.. error injection knobs: bmap_finish_one creates shared extents and CoW/refcount state The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include shared extent and CoW accounting depends on reflink/refcount support; error-injection timing and shutdown/recovery behavior are kernel-sensitive. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/312 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/313 -->
# sources/test-tools/xfstests/tests/xfs/313

## Purpose
Reflink a file with a few dozen extents, CoW a few blocks, and rm. Inject an error during refcount updates to test log recovery. In this subset it exercises reflink, CoW, refcount, and shared-extent behavior; journal/log geometry or recovery behavior. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto quick clone punch`. It imports common/preamble, common/filter, common/reflink, common/inject. Local helpers are `_cleanup`. Requirement and fix gates include `_require_cp_reflink`; `_require_scratch_reflink`; `_require_xfs_io_command "fpunch"`; `_require_xfs_io_error_injection "refcount_finish_one"`. External tools and command surfaces visible in the source include `xfs_io`, `mount`, `stat`, `file`, `touch`, `cp`, `rm`, `sync`. Key shell state is carried in `blksz`, `blks`, `sz`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 17: `_scratch_unmount > /dev/null 2>&1`; line 18: `rm -rf $tmp.*`; line 28: `_require_xfs_io_command "fpunch"`; line 29: `_require_xfs_io_error_injection "refcount_finish_one"`; line 34: `echo "Format filesystem"`; line 35: `_scratch_mkfs >/dev/null 2>&1`; line 36: `_scratch_mount >> $seqres.full`; line 38: `echo "Create files"`; line 39: `_pwrite_byte 0x66 0 $sz $SCRATCH_MNT/file1 >> $seqres.full`; plus 3 further source-derived command steps.. error injection knobs: refcount_finish_one creates shared extents and CoW/refcount state The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include shared extent and CoW accounting depends on reflink/refcount support; error-injection timing and shutdown/recovery behavior are kernel-sensitive. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/313 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/314 -->
# sources/test-tools/xfstests/tests/xfs/314

## Purpose
Reflink a file with a few dozen extents, CoW a few blocks, and rm. Inject an error during rmap updates to test log recovery. In this subset it exercises reverse mapping metadata and owner-accounting validation; reflink, CoW, refcount, and shared-extent behavior; journal/log geometry or recovery behavior. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto quick clone`. It imports common/preamble, common/filter, common/reflink, common/inject. Local helpers are `_cleanup`. Requirement and fix gates include `_require_cp_reflink`; `_require_scratch_reflink`; `_require_xfs_scratch_rmapbt`; `_require_error_injection`; `_require_xfs_io_error_injection "rmap_finish_one"`. External tools and command surfaces visible in the source include `xfs_io`, `mount`, `stat`, `file`, `touch`, `cp`, `rm`, `sync`. Key shell state is carried in `blksz`, `blks`, `sz`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 17: `_scratch_unmount > /dev/null 2>&1`; line 18: `rm -rf $tmp.*`; line 28: `_require_xfs_scratch_rmapbt`; line 30: `_require_xfs_io_error_injection "rmap_finish_one"`; line 35: `echo "Format filesystem"`; line 36: `_scratch_mkfs >/dev/null 2>&1`; line 37: `_scratch_mount >> $seqres.full`; line 39: `echo "Create files"`; line 40: `_pwrite_byte 0x66 0 $sz $SCRATCH_MNT/file1 >> $seqres.full`; plus 3 further source-derived command steps.. error injection knobs: rmap_finish_one creates shared extents and CoW/refcount state The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include shared extent and CoW accounting depends on reflink/refcount support; error-injection timing and shutdown/recovery behavior are kernel-sensitive. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/314 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/315 -->
# sources/test-tools/xfstests/tests/xfs/315

## Purpose
Reflink a file with a few dozen extents and CoW a few blocks. Inject an error during extent freeing to test log recovery. In this subset it exercises reflink, CoW, refcount, and shared-extent behavior; journal/log geometry or recovery behavior. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto quick clone`. It imports common/preamble, common/filter, common/reflink, common/inject. Local helpers are `_cleanup`. Requirement and fix gates include `_require_cp_reflink`; `_require_scratch_reflink`; `_require_error_injection`; `_require_xfs_io_command "cowextsize"`; `_require_xfs_io_error_injection "free_extent"`; `_require_congruent_file_oplen $SCRATCH_MNT $blksz`. External tools and command surfaces visible in the source include `xfs_io`, `mount`, `stat`, `file`, `touch`, `cp`, `rm`, `sync`. Key shell state is carried in `blksz`, `blks`, `sz`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 17: `_scratch_unmount > /dev/null 2>&1`; line 18: `rm -rf $tmp.*`; line 29: `_require_xfs_io_command "cowextsize"`; line 30: `_require_xfs_io_error_injection "free_extent"`; line 35: `echo "Format filesystem"`; line 36: `_scratch_mkfs >/dev/null 2>&1`; line 37: `_scratch_mount >> $seqres.full`; line 40: `$XFS_IO_PROG -c "cowextsize $sz" $SCRATCH_MNT`; line 42: `echo "Create files"`; plus 3 further source-derived command steps.. error injection knobs: free_extent creates shared extents and CoW/refcount state The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include shared extent and CoW accounting depends on reflink/refcount support; error-injection timing and shutdown/recovery behavior are kernel-sensitive. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/315 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/316 -->
# sources/test-tools/xfstests/tests/xfs/316

## Purpose
Reflink a file with a few dozen extents, CoW a few blocks, and rm. Force XFS into "two refcount updates per transaction" mode. In this subset it exercises reflink, CoW, refcount, and shared-extent behavior. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto quick clone punch`. It imports common/preamble, common/filter, common/reflink, common/inject. Local helpers are `_cleanup`. Requirement and fix gates include `_require_cp_reflink`; `_require_scratch_reflink`; `_require_error_injection`; `_require_xfs_io_command "fpunch"`; `_require_xfs_io_error_injection "refcount_continue_update"`. External tools and command surfaces visible in the source include `xfs_io`, `mount`, `stat`, `file`, `touch`, `cp`, `rm`, `sync`. Key shell state is carried in `blksz`, `blks`, `sz`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 17: `_scratch_unmount > /dev/null 2>&1`; line 18: `rm -rf $tmp.*`; line 29: `_require_xfs_io_command "fpunch"`; line 30: `_require_xfs_io_error_injection "refcount_continue_update"`; line 35: `echo "Format filesystem"`; line 36: `_scratch_mkfs >/dev/null 2>&1`; line 37: `_scratch_mount >> $seqres.full`; line 39: `echo "Create files"`; line 40: `_pwrite_byte 0x66 0 $sz $SCRATCH_MNT/file1 >> $seqres.full`; plus 3 further source-derived command steps.. error injection knobs: refcount_continue_update creates shared extents and CoW/refcount state The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include shared extent and CoW accounting depends on reflink/refcount support; error-injection timing and shutdown/recovery behavior are kernel-sensitive. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/316 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/317 -->
# sources/test-tools/xfstests/tests/xfs/317

## Purpose
Simulate rmap update errors with a file write and a file remove. In this subset it exercises reverse mapping metadata and owner-accounting validation. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto quick rmap`. It imports common/preamble, common/filter, common/inject. Local helpers are `_cleanup`. Requirement and fix gates include `_require_scratch`; `_require_xfs_scratch_rmapbt`; `_require_error_injection`; `_require_xfs_io_error_injection "rmap_finish_one"`. External tools and command surfaces visible in the source include `xfs_io`, `mount`, `stat`, `file`, `touch`, `rm`, `sync`. Key shell state is carried in `blksz`, `blks`, `sz`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 16: `_scratch_unmount > /dev/null 2>&1`; line 17: `rm -rf $tmp.*`; line 25: `_require_xfs_scratch_rmapbt`; line 27: `_require_xfs_io_error_injection "rmap_finish_one"`; line 32: `echo "Format filesystem"`; line 33: `_scratch_mkfs >/dev/null 2>&1`; line 34: `_scratch_mount >> $seqres.full`; line 36: `echo "Create files"`; line 37: `touch $SCRATCH_MNT/file1`; plus 3 further source-derived command steps.. error injection knobs: rmap_finish_one The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include error-injection timing and shutdown/recovery behavior are kernel-sensitive. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/317 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/318 -->
# sources/test-tools/xfstests/tests/xfs/318

## Purpose
Simulate free extent errors with a file write and a file remove. In this subset it exercises filesystem freeze/unfreeze behavior under stress or error injection. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto quick rw freeze`. It imports common/preamble, common/filter, common/inject. Local helpers are `_cleanup`. Requirement and fix gates include `_require_scratch`; `_require_error_injection`; `_require_xfs_io_error_injection "rmap_finish_one"`; `_require_freeze`. External tools and command surfaces visible in the source include `xfs_io`, `xfs_freeze`, `mount`, `stat`, `file`, `touch`, `rm`, `sync`. Key shell state is carried in `blksz`, `blks`, `sz`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 16: `xfs_freeze -u $SCRATCH_MNT 2>/dev/null`; line 18: `rm -rf $tmp.*`; line 27: `_require_xfs_io_error_injection "rmap_finish_one"`; line 33: `echo "Format filesystem"`; line 34: `_scratch_mkfs >/dev/null 2>&1`; line 35: `_scratch_mount >> $seqres.full`; line 39: `_xfs_force_bdev data $SCRATCH_MNT`; line 41: `echo "Create files"`; line 42: `touch $SCRATCH_MNT/file1`; plus 3 further source-derived command steps.. error injection knobs: free_extent The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include error-injection timing and shutdown/recovery behavior are kernel-sensitive. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/318 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/319 -->
# sources/test-tools/xfstests/tests/xfs/319

## Purpose
Reflink a file. Inject an error during block remap to test log recovery. In this subset it exercises reflink, CoW, refcount, and shared-extent behavior; journal/log geometry or recovery behavior. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto quick clone`. It imports common/preamble, common/filter, common/reflink, common/inject. Local helpers are `_cleanup`. Requirement and fix gates include `_require_cp_reflink`; `_require_scratch_reflink`; `_require_xfs_io_error_injection "bmap_finish_one"`. External tools and command surfaces visible in the source include `xfs_io`, `mount`, `stat`, `file`, `touch`, `cp`, `rm`, `sync`. Key shell state is carried in `blksz`, `blks`, `sz`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 17: `_scratch_unmount > /dev/null 2>&1`; line 18: `rm -rf $tmp.*`; line 28: `_require_xfs_io_error_injection "bmap_finish_one"`; line 33: `echo "Format filesystem"`; line 34: `_scratch_mkfs >/dev/null 2>&1`; line 35: `_scratch_mount >> $seqres.full`; line 37: `echo "Create files"`; line 38: `_pwrite_byte 0x66 0 $sz $SCRATCH_MNT/file1 >> $seqres.full`; line 39: `_cp_reflink $SCRATCH_MNT/file1 $SCRATCH_MNT/file2`; plus 3 further source-derived command steps.. error injection knobs: bmap_finish_one creates shared extents and CoW/refcount state The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include shared extent and CoW accounting depends on reflink/refcount support; error-injection timing and shutdown/recovery behavior are kernel-sensitive. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/319 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/320 -->
# sources/test-tools/xfstests/tests/xfs/320

## Purpose
Reflink a file. Inject an error during block remap to test log recovery. In this subset it exercises reflink, CoW, refcount, and shared-extent behavior; journal/log geometry or recovery behavior. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto quick clone`. It imports common/preamble, common/filter, common/reflink, common/inject. Local helpers are `_cleanup`. Requirement and fix gates include `_require_cp_reflink`; `_require_scratch_reflink`; `_require_xfs_io_error_injection "bmap_finish_one"`. External tools and command surfaces visible in the source include `xfs_io`, `mount`, `stat`, `file`, `touch`, `cp`, `rm`, `sync`. Key shell state is carried in `blksz`, `blks`, `sz`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 17: `_scratch_unmount > /dev/null 2>&1`; line 18: `rm -rf $tmp.*`; line 28: `_require_xfs_io_error_injection "bmap_finish_one"`; line 33: `echo "Format filesystem"`; line 34: `_scratch_mkfs >/dev/null 2>&1`; line 35: `_scratch_mount >> $seqres.full`; line 37: `echo "Create files"`; line 38: `_pwrite_byte 0x66 0 $sz $SCRATCH_MNT/file1 >> $seqres.full`; line 39: `_cp_reflink $SCRATCH_MNT/file1 $SCRATCH_MNT/file2`; plus 3 further source-derived command steps.. error injection knobs: bmap_finish_one creates shared extents and CoW/refcount state The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include shared extent and CoW accounting depends on reflink/refcount support; error-injection timing and shutdown/recovery behavior are kernel-sensitive. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/320 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/321 -->
# sources/test-tools/xfstests/tests/xfs/321

## Purpose
Reflink a file. Inject an error during refcount update to test log recovery. In this subset it exercises reflink, CoW, refcount, and shared-extent behavior; journal/log geometry or recovery behavior. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto quick clone`. It imports common/preamble, common/filter, common/reflink, common/inject. Local helpers are `_cleanup`. Requirement and fix gates include `_require_cp_reflink`; `_require_scratch_reflink`; `_require_xfs_io_error_injection "refcount_finish_one"`. External tools and command surfaces visible in the source include `xfs_io`, `mount`, `stat`, `file`, `touch`, `cp`, `rm`, `sync`, `truncate`. Key shell state is carried in `blksz`, `blks`, `sz`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 17: `_scratch_unmount > /dev/null 2>&1`; line 18: `rm -rf $tmp.*`; line 28: `_require_xfs_io_error_injection "refcount_finish_one"`; line 33: `echo "Format filesystem"`; line 34: `_scratch_mkfs >/dev/null 2>&1`; line 35: `_scratch_mount >> $seqres.full`; line 37: `echo "Create files"`; line 38: `_pwrite_byte 0x66 0 $sz $SCRATCH_MNT/file1 >> $seqres.full`; line 39: `$XFS_IO_PROG -f -c "truncate $sz" $SCRATCH_MNT/file3 >> $seqres.full`; plus 3 further source-derived command steps.. error injection knobs: refcount_finish_one creates shared extents and CoW/refcount state The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include shared extent and CoW accounting depends on reflink/refcount support; error-injection timing and shutdown/recovery behavior are kernel-sensitive. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/321 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/322 -->
# sources/test-tools/xfstests/tests/xfs/322

## Purpose
Reflink a file. Inject an error during rmap update to test log recovery. In this subset it exercises reverse mapping metadata and owner-accounting validation; reflink, CoW, refcount, and shared-extent behavior; journal/log geometry or recovery behavior. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto quick clone`. It imports common/preamble, common/filter, common/reflink, common/inject. Local helpers are `_cleanup`. Requirement and fix gates include `_require_cp_reflink`; `_require_scratch_reflink`; `_require_xfs_scratch_rmapbt`; `_require_xfs_io_error_injection "rmap_finish_one"`; `_require_congruent_file_oplen $SCRATCH_MNT $blksz`. External tools and command surfaces visible in the source include `xfs_io`, `mount`, `stat`, `file`, `touch`, `cp`, `rm`, `sync`, `truncate`. Key shell state is carried in `blksz`, `blks`, `sz`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 17: `_scratch_unmount > /dev/null 2>&1`; line 18: `rm -rf $tmp.*`; line 28: `_require_xfs_scratch_rmapbt`; line 29: `_require_xfs_io_error_injection "rmap_finish_one"`; line 34: `echo "Format filesystem"`; line 35: `_scratch_mkfs >/dev/null 2>&1`; line 36: `_scratch_mount >> $seqres.full`; line 39: `echo "Create files"`; line 40: `_pwrite_byte 0x66 0 $sz $SCRATCH_MNT/file1 >> $seqres.full`; plus 3 further source-derived command steps.. error injection knobs: rmap_finish_one creates shared extents and CoW/refcount state The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include shared extent and CoW accounting depends on reflink/refcount support; error-injection timing and shutdown/recovery behavior are kernel-sensitive. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/322 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/323 -->
# sources/test-tools/xfstests/tests/xfs/323

## Purpose
Reflink a file. Inject an error during extent free to test log recovery. In this subset it exercises reflink, CoW, refcount, and shared-extent behavior; journal/log geometry or recovery behavior. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto quick clone`. It imports common/preamble, common/filter, common/reflink, common/inject. Local helpers are `_cleanup`. Requirement and fix gates include `_require_cp_reflink`; `_require_scratch_reflink`; `_require_xfs_io_error_injection "free_extent"`. External tools and command surfaces visible in the source include `xfs_io`, `mount`, `stat`, `file`, `touch`, `cp`, `rm`, `sync`. Key shell state is carried in `blksz`, `blks`, `sz`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 17: `_scratch_unmount > /dev/null 2>&1`; line 18: `rm -rf $tmp.*`; line 28: `_require_xfs_io_error_injection "free_extent"`; line 33: `echo "Format filesystem"`; line 34: `_scratch_mkfs >/dev/null 2>&1`; line 35: `_scratch_mount >> $seqres.full`; line 37: `echo "Create files"`; line 38: `_pwrite_byte 0x66 0 $sz $SCRATCH_MNT/file1 >> $seqres.full`; line 39: `_pwrite_byte 0x67 0 $sz $SCRATCH_MNT/file3 >> $seqres.full`; plus 3 further source-derived command steps.. error injection knobs: free_extent creates shared extents and CoW/refcount state The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include shared extent and CoW accounting depends on reflink/refcount support; error-injection timing and shutdown/recovery behavior are kernel-sensitive. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/323 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/324 -->
# sources/test-tools/xfstests/tests/xfs/324

## Purpose
Reflink a file with a few dozen extents. Force XFS into "two refcount updates per transaction" mode. In this subset it exercises reflink, CoW, refcount, and shared-extent behavior. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto quick clone punch`. It imports common/preamble, common/filter, common/reflink, common/inject. Local helpers are `_cleanup`. Requirement and fix gates include `_require_cp_reflink`; `_require_scratch_reflink`; `_require_error_injection`; `_require_xfs_io_command "fpunch"`; `_require_xfs_io_error_injection "refcount_continue_update"`. External tools and command surfaces visible in the source include `xfs_io`, `mount`, `stat`, `file`, `touch`, `cp`, `rm`, `sync`. Key shell state is carried in `blksz`, `blks`, `sz`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 17: `_scratch_unmount > /dev/null 2>&1`; line 18: `rm -rf $tmp.*`; line 29: `_require_xfs_io_command "fpunch"`; line 30: `_require_xfs_io_error_injection "refcount_continue_update"`; line 35: `echo "Format filesystem"`; line 36: `_scratch_mkfs >/dev/null 2>&1`; line 37: `_scratch_mount >> $seqres.full`; line 39: `echo "Create files"`; line 40: `_pwrite_byte 0x66 0 $sz $SCRATCH_MNT/file1 >> $seqres.full`; plus 3 further source-derived command steps.. error injection knobs: refcount_continue_update creates shared extents and CoW/refcount state The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include shared extent and CoW accounting depends on reflink/refcount support; error-injection timing and shutdown/recovery behavior are kernel-sensitive. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/324 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/325 -->
# sources/test-tools/xfstests/tests/xfs/325

## Purpose
Reflink a file with a few dozen extents, CoW a few blocks, and rm. Inject an error during extent freeing to test log recovery. In this subset it exercises reflink, CoW, refcount, and shared-extent behavior; filesystem freeze/unfreeze behavior under stress or error injection; journal/log geometry or recovery behavior. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto quick clone freeze`. It imports common/preamble, common/filter, common/reflink, common/inject. Local helpers are `_cleanup`. Requirement and fix gates include `_require_cp_reflink`; `_require_scratch_reflink`; `_require_error_injection`; `_require_xfs_io_error_injection "free_extent"`; `_require_freeze`. External tools and command surfaces visible in the source include `xfs_io`, `xfs_freeze`, `mount`, `stat`, `file`, `touch`, `cp`, `rm`, `sync`. Key shell state is carried in `blksz`, `blks`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 17: `xfs_freeze -u $SCRATCH_MNT 2>/dev/null`; line 19: `rm -rf $tmp.*`; line 30: `_require_xfs_io_error_injection "free_extent"`; line 35: `echo "Format filesystem"`; line 36: `_scratch_mkfs >/dev/null 2>&1`; line 37: `_scratch_mount >> $seqres.full`; line 39: `echo "Create files"`; line 40: `_pwrite_byte 0x66 0 $((blksz * blks)) $SCRATCH_MNT/file1 >> $seqres.full`; line 41: `_cp_reflink $SCRATCH_MNT/file1 $SCRATCH_MNT/file2`; plus 3 further source-derived command steps.. error injection knobs: free_extent creates shared extents and CoW/refcount state The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include shared extent and CoW accounting depends on reflink/refcount support; error-injection timing and shutdown/recovery behavior are kernel-sensitive. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/325 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/326 -->
# sources/test-tools/xfstests/tests/xfs/326

## Purpose
Reflink a file with a few dozen extents, CoW a few blocks, and rm. Inject an error during refcount updates to test log recovery. Use cowextsize so that the refcount failure is somewhere in the CoW remap instead of when we're stashing the CoW orphan record. In this subset it exercises reflink, CoW, refcount, and shared-extent behavior; journal/log geometry or recovery behavior. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto quick clone punch`. It imports common/preamble, common/filter, common/reflink, common/inject. Local helpers are `_cleanup`. Requirement and fix gates include `_require_cp_reflink`; `_require_scratch_reflink`; `_require_xfs_io_command "cowextsize"`; `_require_xfs_io_command "fpunch"`; `_require_xfs_io_error_injection "refcount_finish_one"`; `_require_congruent_file_oplen $SCRATCH_MNT $blksz`; `_require_no_xfs_always_cow`. External tools and command surfaces visible in the source include `xfs_io`, `mount`, `stat`, `file`, `touch`, `cp`, `rm`, `sync`. Key shell state is carried in `blksz`, `blks`, `sz`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 19: `_scratch_unmount > /dev/null 2>&1`; line 20: `rm -rf $tmp.*`; line 30: `_require_xfs_io_command "cowextsize"`; line 31: `_require_xfs_io_command "fpunch"`; line 32: `_require_xfs_io_error_injection "refcount_finish_one"`; line 37: `echo "Format filesystem"`; line 38: `_scratch_mkfs >/dev/null 2>&1`; line 39: `_scratch_mount >> $seqres.full`; line 42: `$XFS_IO_PROG -c "cowextsize $sz" $SCRATCH_MNT`; plus 3 further source-derived command steps.. error injection knobs: refcount_finish_one creates shared extents and CoW/refcount state The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include shared extent and CoW accounting depends on reflink/refcount support; error-injection timing and shutdown/recovery behavior are kernel-sensitive. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/326 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/327 -->
# sources/test-tools/xfstests/tests/xfs/327

## Purpose
Create 100 reflinked files, CoW them all, and see if xfs_repair will clear the reflink flag. There was a buffer handling bug in xfs_repair that (fortunately) triggered asserts in the rmap code when clearing the reflink flag. In this subset it exercises reverse mapping metadata and owner-accounting validation; reflink, CoW, refcount, and shared-extent behavior; xfs_repair detection and correction of crafted metadata damage. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto quick clone`. It imports common/preamble, common/filter, common/reflink. Local helpers are `_cleanup`. Requirement and fix gates include `_require_cp_reflink`; `_require_scratch_reflink`. External tools and command surfaces visible in the source include `xfs_io`, `xfs_db`, `xfs_repair`, `mount`, `stat`, `grep`, `sed`, `file`, `cp`, `rm`, `sync`. Key shell state is carried in `nr`, `ino_0`, `ino_64`, `ino_128`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 19: `_scratch_unmount > /dev/null 2>&1`; line 20: `rm -rf $tmp.*`; line 30: `nr=128 # spanning at least one inode chunk tickles a bug in xfs_repair`; line 31: `echo "Format filesystem"`; line 32: `_scratch_mkfs >/dev/null 2>&1`; line 33: `_scratch_mount >> $seqres.full`; line 35: `echo "Create files"`; line 36: `_pwrite_byte 0x66 0 1 $SCRATCH_MNT/file.0 >> $seqres.full`; line 37: `seq 1 $nr | while read i; do`; plus 3 further source-derived command steps.. creates shared extents and CoW/refcount state The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include shared extent and CoW accounting depends on reflink/refcount support. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/327 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/328 -->
# sources/test-tools/xfstests/tests/xfs/328

## Purpose
See how well xfs_fsr handles "defragging" a file with a hojillion extents. In this subset it exercises reflink, CoW, refcount, and shared-extent behavior; xfs_fsr defragmentation and exchangerange recovery. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto quick clone fsr prealloc`. It imports common/preamble, common/filter, common/attr, common/reflink. Local helpers are `calc_space`. Requirement and fix gates include `_require_scratch_reflink`; `_require_cp_reflink`; `_require_test_program "punch-alternating"`; `_require_xfs_io_command "falloc" # used in FSR`; `_require_command "$XFS_FSR_PROG" "xfs_fsr"`. External tools and command surfaces visible in the source include `xfs_io`, `xfs_fsr`, `mount`, `stat`, `sed`, `file`, `mkdir`, `cp`, `rm`, `punch-alternating`. Key shell state is carried in `testdir`, `fnr`, `free_blocks`, `blksz`, `space_avail`, `blocks_needed`, `space_needed`, `bytes`, `old_nextents`, `new_nextents`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 20: `_require_xfs_io_command "falloc" # used in FSR`; line 21: `_require_command "$XFS_FSR_PROG" "xfs_fsr"`; line 23: `rm -f "$seqres.full"`; line 25: `echo "Format and mount"`; line 26: `_scratch_mkfs > "$seqres.full" 2>&1`; line 27: `_scratch_mount >> "$seqres.full" 2>&1`; line 30: `mkdir "$testdir"`; line 44: `while test $space_needed -gt $space_avail; do`; line 51: `echo "Create a many-block file"`; plus 3 further source-derived command steps.. drives xfs_fsr defragmentation paths creates shared extents and CoW/refcount state The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include shared extent and CoW accounting depends on reflink/refcount support. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/328 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/329 -->
# sources/test-tools/xfstests/tests/xfs/329

## Purpose
Ensure that xfs_fsr handles errors correctly while defragging files. In this subset it exercises reflink, CoW, refcount, and shared-extent behavior; xfs_fsr defragmentation and exchangerange recovery. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto quick clone fsr`. It imports common/preamble, common/filter, common/attr, common/reflink, common/inject. Local helpers are no local shell helpers. Requirement and fix gates include `_require_scratch_reflink`; `_require_cp_reflink`; `_require_command "$XFS_FSR_PROG" "xfs_fsr"`; `_require_xfs_io_error_injection "bmap_finish_one"`; `_require_xfs_scratch_rmapbt`; `_require_xfs_io_command falloc	# fsr requires support for preallocation`; `_require_congruent_file_oplen $SCRATCH_MNT $blksz`. External tools and command surfaces visible in the source include `xfs_io`, `xfs_fsr`, `mount`, `stat`, `file`, `touch`, `mkdir`, `cp`, `rm`. Key shell state is carried in `testdir`, `blksz`, `blks`, `old_nextents`, `new_nextents`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 20: `_require_command "$XFS_FSR_PROG" "xfs_fsr"`; line 21: `_require_xfs_io_error_injection "bmap_finish_one"`; line 22: `_require_xfs_scratch_rmapbt`; line 23: `_require_xfs_io_command falloc	# fsr requires support for preallocation`; line 25: `rm -f "$seqres.full"`; line 27: `echo "Format and mount"`; line 28: `_scratch_mkfs > "$seqres.full" 2>&1`; line 29: `_scratch_mount >> "$seqres.full" 2>&1`; line 35: `mkdir "$testdir"`; plus 3 further source-derived command steps.. error injection knobs: bmap_finish_one drives xfs_fsr defragmentation paths creates shared extents and CoW/refcount state The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include shared extent and CoW accounting depends on reflink/refcount support; error-injection timing and shutdown/recovery behavior are kernel-sensitive. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/329 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/330 -->
# sources/test-tools/xfstests/tests/xfs/330

## Purpose
Ensure that xfs_fsr handles quota correctly while defragging files. In this subset it exercises reflink, CoW, refcount, and shared-extent behavior; quota accounting, dquot metadata, and quota mount mode handling; xfs_fsr defragmentation and exchangerange recovery. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto quick clone fsr quota prealloc`. It imports common/preamble, common/filter, common/attr, common/reflink, common/quota. Local helpers are `do_repquota`. Requirement and fix gates include `_require_scratch_reflink`; `_require_cp_reflink`; `_require_xfs_io_command "falloc" # used in FSR`; `_require_command "$XFS_FSR_PROG" "xfs_fsr"`; `_require_quota`; `_require_nobody`. External tools and command surfaces visible in the source include `xfs_io`, `xfs_fsr`, `dd`, `mount`, `stat`, `grep`, `sed`, `file`, `touch`, `mkdir`, `cp`, `rm`. Key shell state is carried in `HIDDEN_QUOTA_FILES`, `testdir`, `blksz`, `blks`, `old_nextents`, `new_nextents`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 20: `_require_xfs_io_command "falloc" # used in FSR`; line 21: `_require_command "$XFS_FSR_PROG" "xfs_fsr"`; line 29: `$val = '"$HIDDEN_QUOTA_FILES"';`; line 33: `rm -f "$seqres.full"`; line 35: `echo "Format and mount"`; line 36: `_scratch_mkfs > "$seqres.full" 2>&1`; line 38: `_scratch_mount >> "$seqres.full" 2>&1`; line 40: `HIDDEN_QUOTA_FILES=$(_xfs_calc_hidden_quota_files $SCRATCH_MNT)`; line 47: `mkdir "$testdir"`; plus 3 further source-derived command steps.. drives xfs_fsr defragmentation paths mounts or inspects quota state and dquot accounting creates shared extents and CoW/refcount state The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include quota state can persist through remounts and is sensitive to mount options; shared extent and CoW accounting depends on reflink/refcount support. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/330 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/331 -->
# sources/test-tools/xfstests/tests/xfs/331

## Purpose
Create a big enough rmapbt that we tickle a fdblocks accounting bug. In this subset it exercises reverse mapping metadata and owner-accounting validation; reflink, CoW, refcount, and shared-extent behavior. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto quick rmap clone prealloc`. It imports common/preamble, common/filter, common/reflink. Local helpers are no local shell helpers. Requirement and fix gates include `_require_scratch`; `_require_xfs_scratch_rmapbt`; `_require_scratch_reflink`; `_require_xfs_io_command "falloc"`; `_require_test_program "punch-alternating"`; `_require_xfs_io_command "falloc"`; `_require_fs_space $SCRATCH_MNT $(( (2 * blocks * blksz) * 5 / 4096 ))`. External tools and command surfaces visible in the source include `xfs_io`, `mount`, `stat`, `file`, `rm`, `punch-alternating`. Key shell state is carried in `blksz`, `bt_ptrs`, `bt_recs`, `blocks`, `len`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 17: `_require_xfs_scratch_rmapbt`; line 19: `_require_xfs_io_command "falloc"`; line 21: `_require_xfs_io_command "falloc"`; line 23: `rm -f "$seqres.full"`; line 25: `echo "+ create scratch fs"`; line 26: `_scratch_mkfs > "$seqres.full" 2>&1`; line 28: `echo "+ mount fs image"`; line 29: `_scratch_mount`; line 42: `echo "+ make some files"`; plus 3 further source-derived command steps.. creates shared extents and CoW/refcount state The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include shared extent and CoW accounting depends on reflink/refcount support. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/331 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/332 -->
# sources/test-tools/xfstests/tests/xfs/332

## Purpose
Make sure query_range returns -EINVAL if lowkey > highkey. In this subset it exercises reverse mapping metadata and owner-accounting validation; reflink, CoW, refcount, and shared-extent behavior. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto quick rmap clone collapse punch insert zero prealloc`. It imports common/preamble, common/filter, common/attr. Local helpers are no local shell helpers. Requirement and fix gates include `_require_xfs_scratch_rmapbt`; `_require_command "$XFS_DB_PROG" "xfs_db"`; `_require_xfs_io_command "falloc"`; `_require_xfs_io_command "fpunch"`; `_require_xfs_io_command "fzero"`; `_require_xfs_io_command "fcollapse"`; `_require_xfs_io_command "finsert"`. External tools and command surfaces visible in the source include `xfs_io`, `xfs_db`, `mount`, `stat`, `file`, `rm`, `sync`. Key shell state is carried in `blksz`, `blocks`, `len`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 16: `_require_xfs_scratch_rmapbt`; line 17: `_require_command "$XFS_DB_PROG" "xfs_db"`; line 18: `_require_xfs_io_command "falloc"`; line 19: `_require_xfs_io_command "fpunch"`; line 20: `_require_xfs_io_command "fzero"`; line 21: `_require_xfs_io_command "fcollapse"`; line 22: `_require_xfs_io_command "finsert"`; line 24: `rm -f "$seqres.full"`; line 26: `echo "Format and mount"`; plus 3 further source-derived command steps.. compares GETFSMAP/xfs_io fsmap output against expected owners, devices, or bmap records The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include expected-output drift, missing helper binaries, and unsupported scratch geometry are the main hazards. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/332 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/334 -->
# sources/test-tools/xfstests/tests/xfs/334

## Purpose
Ensure that we can create a few realtime files on a rmapbt filesystem. In this subset it exercises reverse mapping metadata and owner-accounting validation; realtime device allocation and realtime reverse-map behavior. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto quick rmap realtime`. It imports common/preamble, common/filter. Local helpers are no local shell helpers. Requirement and fix gates include `_require_realtime`; `_require_xfs_scratch_rmapbt`. External tools and command surfaces visible in the source include `xfs_io`, `mount`, `stat`, `file`, `rm`, `sync`. Key shell state is carried in mostly transient harness variables, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 16: `_require_xfs_scratch_rmapbt`; line 18: `rm -f "$seqres.full"`; line 20: `echo "Format and mount"`; line 21: `_scratch_mkfs > "$seqres.full" 2>&1`; line 22: `_scratch_mount`; line 24: `echo "Create a few files"`; line 25: `$XFS_IO_PROG -f -R -c 'pwrite -S 0x67 0 50000' -c fsync $SCRATCH_MNT/f1 >> $seqres.full`; line 26: `$XFS_IO_PROG -f -R -c 'pwrite -S 0x67 0 50000' -c fsync $SCRATCH_MNT/f2 >> $seqres.full`; line 27: `_scratch_cycle_mount`; plus 3 further source-derived command steps.. The main integration signal is the scripted xfstests workflow and its golden-output comparison. The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include realtime device geometry and internal/external rt-device handling affect expected output. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/334 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/335 -->
# sources/test-tools/xfstests/tests/xfs/335

## Purpose
Exercise expanding and shrinking the realtime rmap btree. In this subset it exercises reverse mapping metadata and owner-accounting validation; realtime device allocation and realtime reverse-map behavior. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto rmap realtime prealloc`. It imports common/preamble, common/filter. Local helpers are no local shell helpers. Requirement and fix gates include `_require_realtime`; `_require_xfs_scratch_rmapbt`; `_require_test_program "punch-alternating"`; `_require_xfs_io_command "falloc"`; `_require_fs_space $SCRATCH_MNT $(( (2 * blocks * blksz) * 5 / 4096 ))`. External tools and command surfaces visible in the source include `xfs_io`, `mount`, `stat`, `file`, `rm`, `punch-alternating`. Key shell state is carried in `blksz`, `i_core_size`, `i_ptrs`, `bt_ptrs`, `bt_recs`, `blocks`, `len`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 16: `_require_xfs_scratch_rmapbt`; line 18: `_require_xfs_io_command "falloc"`; line 20: `rm -f "$seqres.full"`; line 22: `echo "Format and mount"`; line 23: `_scratch_mkfs | _filter_mkfs 2>$tmp.mkfs >/dev/null`; line 25: `cat $tmp.mkfs > "$seqres.full" 2>&1`; line 26: `_scratch_mount`; line 29: `echo "Create a three-level rtrmapbt"`; line 32: `i_core_size="$(_xfs_get_inode_core_bytes $SCRATCH_MNT)"`; plus 3 further source-derived command steps.. The main integration signal is the scripted xfstests workflow and its golden-output comparison. The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include realtime device geometry and internal/external rt-device handling affect expected output. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/335 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/336 -->
# sources/test-tools/xfstests/tests/xfs/336

## Purpose
Exercise metadump on realtime rmapbt preservation. In this subset it exercises reverse mapping metadata and owner-accounting validation; realtime device allocation and realtime reverse-map behavior; xfsdump/xfsrestore compatibility and metadata preservation; xfs_metadump/xfs_mdrestore metadata image coverage. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto rmap realtime metadump prealloc`. It imports common/preamble, common/filter, common/metadump. Local helpers are `_cleanup`. Requirement and fix gates include `_require_command "$XFS_MDRESTORE_PROG" "xfs_mdrestore"`; `_require_realtime`; `_require_xfs_scratch_rmapbt`; `_require_test_program "punch-alternating"`; `_require_xfs_io_command "falloc"`; `_require_fs_space $SCRATCH_MNT $(( (2 * blocks * blksz) * 5 / 4096 ))`. External tools and command surfaces visible in the source include `xfs_io`, `xfs_mdrestore`, `mount`, `stat`, `file`, `rm`, `punch-alternating`. Key shell state is carried in `blksz`, `i_core_size`, `i_ptrs`, `bt_ptrs`, `bt_recs`, `blocks`, `len`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 15: `rm -rf "$tmp".*`; line 16: `_xfs_cleanup_verify_metadump`; line 22: `_require_command "$XFS_MDRESTORE_PROG" "xfs_mdrestore"`; line 24: `_require_xfs_scratch_rmapbt`; line 26: `_require_xfs_io_command "falloc"`; line 27: `_xfs_setup_verify_metadump`; line 29: `rm -f "$seqres.full"`; line 31: `echo "Format and mount"`; line 32: `_scratch_mkfs | _filter_mkfs 2>$tmp.mkfs >/dev/null`; plus 3 further source-derived command steps.. verifies metadump/mdrestore behavior and image fidelity The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include realtime device geometry and internal/external rt-device handling affect expected output. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/336 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/337 -->
# sources/test-tools/xfstests/tests/xfs/337

## Purpose
Corrupt the realtime rmapbt and see how the kernel and xfs_repair deal. In this subset it exercises reverse mapping metadata and owner-accounting validation; realtime device allocation and realtime reverse-map behavior; xfs_repair detection and correction of crafted metadata damage; metadata fuzzing through common/fuzzy helper paths. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest fuzzers rmap realtime prealloc repair`. It imports common/preamble, common/filter. Local helpers are no local shell helpers. Requirement and fix gates include `_require_realtime`; `_require_xfs_scratch_rmapbt`; `_require_test_program "punch-alternating"`; `_require_xfs_io_command "falloc"`; `_disable_dmesg_check`; `_require_fs_space $SCRATCH_MNT $(( (2 * blocks * blksz) * 5 / 4096 ))`. External tools and command surfaces visible in the source include `xfs_io`, `xfs_db`, `xfs_repair`, `dd`, `mount`, `stat`, `file`, `rm`, `punch-alternating`. Key shell state is carried in `blksz`, `i_core_size`, `i_ptrs`, `bt_ptrs`, `bt_recs`, `blocks`, `len`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 16: `_require_xfs_scratch_rmapbt`; line 18: `_require_xfs_io_command "falloc"`; line 21: `rm -f "$seqres.full"`; line 23: `echo "+ create scratch fs"`; line 24: `_scratch_mkfs | _filter_mkfs 2>$tmp.mkfs >/dev/null`; line 26: `cat $tmp.mkfs > "$seqres.full" 2>&1`; line 28: `echo "+ mount fs image"`; line 29: `_scratch_mount`; line 34: `i_core_size="$(_xfs_get_inode_core_bytes $SCRATCH_MNT)"`; plus 3 further source-derived command steps.. The main integration signal is the scripted xfstests workflow and its golden-output comparison. The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate; realtime device geometry and internal/external rt-device handling affect expected output. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/337 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/338 -->
# sources/test-tools/xfstests/tests/xfs/338

## Purpose
Set rrmapino to zero on an rtrmap fs and see if repair fixes it. In this subset it exercises reverse mapping metadata and owner-accounting validation; realtime device allocation and realtime reverse-map behavior; xfs_repair detection and correction of crafted metadata damage. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto quick rmap realtime repair`. It imports common/preamble, common/filter. Local helpers are no local shell helpers. Requirement and fix gates include `_require_realtime`; `_require_xfs_scratch_rmapbt`; `_disable_dmesg_check`. External tools and command surfaces visible in the source include `xfs_io`, `xfs_db`, `mount`, `stat`, `file`, `rm`. Key shell state is carried in `rtrmap_accessors`, `rtrmap_path_len`, `rtrmap_entry`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 16: `_require_xfs_scratch_rmapbt`; line 18: `rm -f "$seqres.full"`; line 20: `echo "Format and mount"`; line 21: `_scratch_mkfs > "$seqres.full" 2>&1`; line 22: `_scratch_mount`; line 24: `echo "Create some files"`; line 25: `$XFS_IO_PROG -f -R -c "pwrite -S 0x68 0 9999" $SCRATCH_MNT/f1 >> $seqres.full`; line 26: `$XFS_IO_PROG -f -R -c "pwrite -S 0x68 0 9999" $SCRATCH_MNT/f2 >> $seqres.full`; line 27: `_scratch_unmount`; plus 3 further source-derived command steps.. The main integration signal is the scripted xfstests workflow and its golden-output comparison. The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate; realtime device geometry and internal/external rt-device handling affect expected output. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/338 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/339 -->
# sources/test-tools/xfstests/tests/xfs/339

## Purpose
Link rrmapino into the rootdir on an rtrmap fs and see if repair fixes it. In this subset it exercises reverse mapping metadata and owner-accounting validation; realtime device allocation and realtime reverse-map behavior; xfs_repair detection and correction of crafted metadata damage; directory metadata layout and traversal behavior. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto quick rmap realtime repair`. It imports common/preamble, common/filter. Local helpers are no local shell helpers. Requirement and fix gates include `_require_realtime`; `_require_xfs_scratch_rmapbt`. External tools and command surfaces visible in the source include `xfs_io`, `dd`, `mount`, `stat`, `file`, `ln`, `rm`. Key shell state is carried in `rrmapino`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 16: `_require_xfs_scratch_rmapbt`; line 18: `rm -f "$seqres.full"`; line 20: `echo "Format and mount"`; line 21: `_scratch_mkfs > "$seqres.full" 2>&1`; line 22: `_scratch_mount`; line 24: `echo "Create some files"`; line 25: `$XFS_IO_PROG -f -R -c "pwrite -S 0x68 0 9999" $SCRATCH_MNT/f1 >> $seqres.full`; line 26: `$XFS_IO_PROG -f -R -c "pwrite -S 0x68 0 9999" $SCRATCH_MNT/f2 >> $seqres.full`; line 27: `echo garbage > $SCRATCH_MNT/f3`; plus 3 further source-derived command steps.. The main integration signal is the scripted xfstests workflow and its golden-output comparison. The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate; realtime device geometry and internal/external rt-device handling affect expected output. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/339 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/340 -->
# sources/test-tools/xfstests/tests/xfs/340

## Purpose
Set rrmapino to another inode on an rtrmap fs and see if repair fixes it. In this subset it exercises reverse mapping metadata and owner-accounting validation; realtime device allocation and realtime reverse-map behavior; xfs_repair detection and correction of crafted metadata damage. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto quick rmap realtime repair`. It imports common/preamble, common/filter. Local helpers are no local shell helpers. Requirement and fix gates include `_require_realtime`; `_require_xfs_scratch_rmapbt`. External tools and command surfaces visible in the source include `xfs_io`, `xfs_db`, `dd`, `mount`, `stat`, `file`, `rm`. Key shell state is carried in `ino`, `rtrmap_accessors`, `rtrmap_path_len`, `rtrmap_entry`, `rrmapino`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 16: `_require_xfs_scratch_rmapbt`; line 18: `rm -f "$seqres.full"`; line 20: `echo "Format and mount"`; line 21: `_scratch_mkfs > "$seqres.full" 2>&1`; line 22: `_scratch_mount`; line 24: `echo "Create some files"`; line 25: `$XFS_IO_PROG -f -R -c "pwrite -S 0x68 0 9999" $SCRATCH_MNT/f1 >> $seqres.full`; line 26: `$XFS_IO_PROG -f -R -c "pwrite -S 0x68 0 9999" $SCRATCH_MNT/f2 >> $seqres.full`; line 27: `echo garbage > $SCRATCH_MNT/f3`; plus 3 further source-derived command steps.. The main integration signal is the scripted xfstests workflow and its golden-output comparison. The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate; realtime device geometry and internal/external rt-device handling affect expected output. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/340 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/341 -->
# sources/test-tools/xfstests/tests/xfs/341

## Purpose
Cross-link file block into rtrmapbt and see if repair fixes it. In this subset it exercises reverse mapping metadata and owner-accounting validation; realtime device allocation and realtime reverse-map behavior; xfs_repair detection and correction of crafted metadata damage. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto quick rmap realtime prealloc repair`. It imports common/preamble, common/filter. Local helpers are no local shell helpers. Requirement and fix gates include `_require_realtime`; `_require_xfs_scratch_rmapbt`; `_require_test_program "punch-alternating"`; `_disable_dmesg_check`; `_require_xfs_io_command "falloc"`. External tools and command surfaces visible in the source include `xfs_io`, `xfs_db`, `mount`, `stat`, `grep`, `sed`, `file`, `rm`, `punch-alternating`. Key shell state is carried in `blksz`, `rtextsz_blks`, `i_core_size`, `i_ptrs`, `bt_recs`, `blocks`, `len`, `ino`, `fsbno`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 16: `_require_xfs_scratch_rmapbt`; line 19: `_require_xfs_io_command "falloc"`; line 21: `rm -f "$seqres.full"`; line 23: `echo "Format and mount"`; line 24: `_scratch_mkfs | _filter_mkfs 2>$tmp.mkfs >/dev/null`; line 26: `cat $tmp.mkfs > "$seqres.full" 2>&1`; line 27: `_scratch_mount`; line 34: `i_core_size="$(_xfs_get_inode_core_bytes $SCRATCH_MNT)"`; line 41: `echo "Create some files"`; plus 3 further source-derived command steps.. The main integration signal is the scripted xfstests workflow and its golden-output comparison. The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate; realtime device geometry and internal/external rt-device handling affect expected output. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/341 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/342 -->
# sources/test-tools/xfstests/tests/xfs/342

## Purpose
Cross-link rtrmapbt block into a file and see if repair fixes it. In this subset it exercises reverse mapping metadata and owner-accounting validation; realtime device allocation and realtime reverse-map behavior; xfs_repair detection and correction of crafted metadata damage. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto quick rmap realtime prealloc repair`. It imports common/preamble, common/filter. Local helpers are no local shell helpers. Requirement and fix gates include `_require_realtime`; `_require_xfs_scratch_rmapbt`; `_require_test_program "punch-alternating"`; `_require_xfs_io_command "falloc"`. External tools and command surfaces visible in the source include `xfs_io`, `xfs_db`, `mount`, `stat`, `sed`, `file`, `rm`, `punch-alternating`. Key shell state is carried in `blksz`, `i_core_size`, `i_ptrs`, `bt_recs`, `blocks`, `len`, `ino`, `fsbno`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 16: `_require_xfs_scratch_rmapbt`; line 18: `_require_xfs_io_command "falloc"`; line 20: `rm -f "$seqres.full"`; line 22: `echo "Format and mount"`; line 23: `_scratch_mkfs | _filter_mkfs 2>$tmp.mkfs >/dev/null`; line 25: `cat $tmp.mkfs > "$seqres.full" 2>&1`; line 26: `_scratch_mount`; line 31: `i_core_size="$(_xfs_get_inode_core_bytes $SCRATCH_MNT)"`; line 38: `echo "Create some files"`; plus 3 further source-derived command steps.. The main integration signal is the scripted xfstests workflow and its golden-output comparison. The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate; realtime device geometry and internal/external rt-device handling affect expected output. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/342 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/343 -->
# sources/test-tools/xfstests/tests/xfs/343

## Purpose
Basic rmap manipulation tests for realtime files. In this subset it exercises reverse mapping metadata and owner-accounting validation; realtime device allocation and realtime reverse-map behavior. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto quick rmap collapse punch insert zero realtime prealloc`. It imports common/preamble, common/filter. Local helpers are no local shell helpers. Requirement and fix gates include `_require_realtime`; `_require_xfs_scratch_rmapbt`; `_require_xfs_io_command "falloc"`; `_require_xfs_io_command "fpunch"`; `_require_xfs_io_command "fzero"`; `_require_xfs_io_command "fcollapse"`; `_require_xfs_io_command "finsert"`; `_require_congruent_file_oplen $SCRATCH_MNT $blksz`. External tools and command surfaces visible in the source include `xfs_io`, `mount`, `stat`, `file`, `rm`, `sync`. Key shell state is carried in `blksz`, `blocks`, `len`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 16: `_require_xfs_scratch_rmapbt`; line 17: `_require_xfs_io_command "falloc"`; line 18: `_require_xfs_io_command "fpunch"`; line 19: `_require_xfs_io_command "fzero"`; line 20: `_require_xfs_io_command "fcollapse"`; line 21: `_require_xfs_io_command "finsert"`; line 23: `rm -f "$seqres.full"`; line 25: `echo "Format and mount"`; line 26: `_scratch_mkfs > "$seqres.full" 2>&1`; plus 3 further source-derived command steps.. The main integration signal is the scripted xfstests workflow and its golden-output comparison. The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include realtime device geometry and internal/external rt-device handling affect expected output. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/343 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/344 -->
# sources/test-tools/xfstests/tests/xfs/344

## Purpose
Test fragmentation after a lot of random CoW: - Create two reflinked files. Set zero extsz hint on second file. - Directio write to random offsets to scatter CoW reservations. - falloc the whole file to unshare blocks. - Check the number of extents. In this subset it exercises reflink, CoW, refcount, and shared-extent behavior; directory metadata layout and traversal behavior. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto quick clone fiemap unshare`. It imports common/preamble, common/filter, common/reflink. Local helpers are no local shell helpers. Requirement and fix gates include `_require_scratch_reflink`; `_require_cp_reflink`; `_require_xfs_io_command "fiemap"`; `_require_xfs_io_command "cowextsize"`; `_require_xfs_io_command "funshare"`; `_require_odirect`; `_require_fs_space $SCRATCH_MNT $((filesize / 1024 * 3 * 5 / 4))`. External tools and command surfaces visible in the source include `xfs_io`, `mount`, `stat`, `file`, `mkdir`, `cp`, `rm`. Key shell state is carried in `testdir`, `blksz`, `nr`, `filesize`, `bufnr`, `bufsize`, `real_blksz`, `internal_blks`, `old_extents`, `new_extents`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 22: `_require_xfs_io_command "fiemap"`; line 23: `_require_xfs_io_command "cowextsize"`; line 24: `_require_xfs_io_command "funshare"`; line 27: `echo "Format and mount"`; line 28: `_scratch_mkfs > $seqres.full 2>&1`; line 29: `_scratch_mount >> $seqres.full 2>&1`; line 32: `mkdir $testdir`; line 44: `echo "Create the original files"`; line 45: `$XFS_IO_PROG -f -c "pwrite -S 0x61 -b $bufsize 0 $((filesize + 1))" $testdir/file1 >> $seqres.full`; plus 3 further source-derived command steps.. creates shared extents and CoW/refcount state The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include shared extent and CoW accounting depends on reflink/refcount support. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/344 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/345 -->
# sources/test-tools/xfstests/tests/xfs/345

## Purpose
Test fragmentation after a lot of random CoW: - Create two reflinked files. Set zero extsz hint on second file. - Buffered write to random offsets to scatter CoW reservations. - Check the number of extents. In this subset it exercises reflink, CoW, refcount, and shared-extent behavior. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto quick clone fiemap unshare`. It imports common/preamble, common/filter, common/reflink. Local helpers are no local shell helpers. Requirement and fix gates include `_require_scratch_reflink`; `_require_cp_reflink`; `_require_xfs_io_command "fiemap"`; `_require_xfs_io_command "cowextsize"`; `_require_xfs_io_command "funshare"`; `_require_fs_space $SCRATCH_MNT $((filesize / 1024 * 3 * 5 / 4))`. External tools and command surfaces visible in the source include `xfs_io`, `mount`, `stat`, `file`, `mkdir`, `cp`, `rm`, `sync`. Key shell state is carried in `testdir`, `blksz`, `nr`, `filesize`, `bufnr`, `bufsize`, `real_blksz`, `internal_blks`, `old_extents`, `new_extents`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 21: `_require_xfs_io_command "fiemap"`; line 22: `_require_xfs_io_command "cowextsize"`; line 23: `_require_xfs_io_command "funshare"`; line 25: `echo "Format and mount"`; line 26: `_scratch_mkfs > $seqres.full 2>&1`; line 27: `_scratch_mount >> $seqres.full 2>&1`; line 30: `mkdir $testdir`; line 42: `echo "Create the original files"`; line 43: `$XFS_IO_PROG -f -c "pwrite -S 0x61 -b $bufsize 0 $((filesize + 1))" $testdir/file1 >> $seqres.full`; plus 3 further source-derived command steps.. creates shared extents and CoW/refcount state The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include shared extent and CoW accounting depends on reflink/refcount support. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/345 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/346 -->
# sources/test-tools/xfstests/tests/xfs/346

## Purpose
Test fragmentation after writing and dropping CoW extent hint reservation: - Create two reflinked files. Set extsz hint on second file. - Directio write to random offsets to scatter CoW reservations. - Unmount, remount, repeat (twice more). - Check the number of extents. In this subset it exercises reflink, CoW, refcount, and shared-extent behavior; mount/remount acceptance and rejection paths; directory metadata layout and traversal behavior. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto quick clone fiemap unshare`. It imports common/preamble, common/filter, common/reflink. Local helpers are no local shell helpers. Requirement and fix gates include `_require_scratch_reflink`; `_require_cp_reflink`; `_require_xfs_io_command "fiemap"`; `_require_xfs_io_command "cowextsize"`; `_require_xfs_io_command "funshare"`; `_require_odirect`; `_require_congruent_file_oplen $SCRATCH_MNT $blksz`; `_require_fs_space $SCRATCH_MNT $((filesize / 1024 * 3 * 5 / 4))`. External tools and command surfaces visible in the source include `xfs_io`, `mount`, `stat`, `file`, `mkdir`, `cp`, `rm`. Key shell state is carried in `testdir`, `blksz`, `nr`, `filesize`, `bufnr`, `bufsize`, `real_blksz`, `internal_blks`, `old_extents`, `new_extents`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 22: `_require_xfs_io_command "fiemap"`; line 23: `_require_xfs_io_command "cowextsize"`; line 24: `_require_xfs_io_command "funshare"`; line 27: `echo "Format and mount"`; line 28: `_scratch_mkfs > $seqres.full 2>&1`; line 29: `_scratch_mount >> $seqres.full 2>&1`; line 32: `mkdir $testdir`; line 45: `echo "Create the original files"`; line 46: `$XFS_IO_PROG -f -c "pwrite -S 0x61 -b $bufsize 0 $((filesize + 1))" $testdir/file1 >> $seqres.full`; plus 3 further source-derived command steps.. creates shared extents and CoW/refcount state The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include shared extent and CoW accounting depends on reflink/refcount support. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/346 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/347 -->
# sources/test-tools/xfstests/tests/xfs/347

## Purpose
Test fragmentation after writing and dropping CoW extent hint reservation: - Create two reflinked files. Set extsz hint on second file. - Buffered write to random offsets to scatter CoW reservations. - Unmount, remount, repeat (twice more). - Check the number of extents. In this subset it exercises reflink, CoW, refcount, and shared-extent behavior; mount/remount acceptance and rejection paths. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto quick clone fiemap unshare`. It imports common/preamble, common/filter, common/reflink. Local helpers are no local shell helpers. Requirement and fix gates include `_require_scratch_reflink`; `_require_cp_reflink`; `_require_xfs_io_command "fiemap"`; `_require_xfs_io_command "cowextsize"`; `_require_xfs_io_command "funshare"`; `_require_congruent_file_oplen $SCRATCH_MNT $blksz`; `_require_fs_space $SCRATCH_MNT $((filesize / 1024 * 3 * 5 / 4))`. External tools and command surfaces visible in the source include `xfs_io`, `mount`, `stat`, `file`, `mkdir`, `cp`, `rm`. Key shell state is carried in `testdir`, `blksz`, `nr`, `filesize`, `bufnr`, `bufsize`, `real_blksz`, `internal_blks`, `old_extents`, `new_extents`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 22: `_require_xfs_io_command "fiemap"`; line 23: `_require_xfs_io_command "cowextsize"`; line 24: `_require_xfs_io_command "funshare"`; line 26: `echo "Format and mount"`; line 27: `_scratch_mkfs > $seqres.full 2>&1`; line 28: `_scratch_mount >> $seqres.full 2>&1`; line 31: `mkdir $testdir`; line 44: `echo "Create the original files"`; line 45: `$XFS_IO_PROG -f -c "pwrite -S 0x61 -b $bufsize 0 $((filesize + 1))" $testdir/file1 >> $seqres.full`; plus 3 further source-derived command steps.. creates shared extents and CoW/refcount state The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include shared extent and CoW accounting depends on reflink/refcount support. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/347 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/348 -->
# sources/test-tools/xfstests/tests/xfs/348

## Purpose
FSQA Test No. 348 Test handling of invalid inode modes Set all possible file type values for different types of files and verify that xfs_repair detects the correct errors. In this subset it exercises xfs_repair detection and correction of crafted metadata damage; metadata fuzzing through common/fuzzy helper paths. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto quick fuzzers repair`. It imports common/preamble, common/filter, common/repair. Local helpers are no local shell helpers. Requirement and fix gates include `_require_scratch`; `_disable_dmesg_check`. External tools and command surfaces visible in the source include `xfs_db`, `xfs_repair`, `mount`, `stat`, `grep`, `awk`, `sed`, `diff`, `file`, `touch`, `mkdir`, `ln`. Key shell state is carried in `testdir`, `inode_filter`, `pino`, `inodes`, `ino`, `dtypes`, `ftype`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 32: `_scratch_mkfs >>$seqres.full 2>&1`; line 34: `_scratch_mount`; line 38: `mkdir -p $testdir`; line 39: `mkdir $testdir/DIR`; line 40: `echo 123 > $testdir/DATA`; line 41: `touch $testdir/EMPTY`; line 42: `ln -s $testdir/DATA $testdir/SYMLINK`; line 47: `_xfs_has_feature $SCRATCH_MNT ftype && FTYPE_FEATURE=1`; line 51: `rm -f $inode_filter`; plus 3 further source-derived command steps.. The main integration signal is the scripted xfstests workflow and its golden-output comparison. The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate; error-injection timing and shutdown/recovery behavior are kernel-sensitive. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/348 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/349 -->
# sources/test-tools/xfstests/tests/xfs/349

## Purpose
Populate a XFS filesystem and ensure that scrub and repair are happy. In this subset it exercises xfs_repair detection and correction of crafted metadata damage; xfs_scrub online checking or repair of populated/fuzzed filesystems. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto scrub`. It imports common/preamble, common/filter, common/populate, common/fuzzy. Local helpers are no local shell helpers. Requirement and fix gates include `_require_scratch`; `_require_scrub`; `_require_xfs_stress_scrub`; `_require_populate_commands`. External tools and command surfaces visible in the source include `mount`, `stat`, `file`, `rm`. Key shell state is carried in mostly transient harness variables, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 21: `_require_xfs_stress_scrub`; line 24: `echo "Format and populate"`; line 25: `_scratch_populate_cached nofill > $seqres.full 2>&1`; line 27: `echo "Scrub"`; line 28: `_scratch_mount >> $seqres.full 2>&1`; line 29: `_scratch_scrub >> $seqres.full`. The main integration signal is the scripted xfstests workflow and its golden-output comparison. The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/349 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/350 -->
# sources/test-tools/xfstests/tests/xfs/350

## Purpose
Populate a XFS filesystem and fuzz every superblock field. Use xfs_repair to fix the corruption. In this subset it exercises xfs_repair detection and correction of crafted metadata damage; metadata fuzzing through common/fuzzy helper paths. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest dangerous_fuzzers repair fuzzers_repair`. It imports common/preamble, common/filter, common/populate, common/fuzzy. Local helpers are no local shell helpers. Requirement and fix gates include `_require_scratch_xfs_fuzz_fields`. External tools and command surfaces visible in the source include `xfs_repair`, `stat`, `file`, `rm`. Key shell state is carried in mostly transient harness variables, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 20: `_require_scratch_xfs_fuzz_fields`; line 22: `echo "Format and populate"`; line 23: `_scratch_populate_cached nofill > $seqres.full 2>&1`; line 25: `echo "Fuzz superblock"`; line 26: `_scratch_xfs_fuzz_metadata '' 'offline' 'sb 0' >> $seqres.full`; line 27: `echo "Done fuzzing superblock"`. metadata fuzzing target: _scratch_xfs_fuzz_metadata '' 'offline' 'sb 0' >> $seqres.full The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/350 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/351 -->
# sources/test-tools/xfstests/tests/xfs/351

## Purpose
Populate a XFS filesystem and fuzz every superblock field. Use xfs_scrub to fix the corruption. In this subset it exercises xfs_repair detection and correction of crafted metadata damage; xfs_scrub online checking or repair of populated/fuzzed filesystems; metadata fuzzing through common/fuzzy helper paths. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest dangerous_fuzzers scrub fuzzers_online_repair`. It imports common/preamble, common/filter, common/populate, common/fuzzy. Local helpers are no local shell helpers. Requirement and fix gates include `_require_scratch_xfs_fuzz_fields`. External tools and command surfaces visible in the source include `xfs_scrub`, `stat`, `file`, `rm`. Key shell state is carried in mostly transient harness variables, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 20: `_require_scratch_xfs_fuzz_fields`; line 22: `echo "Format and populate"`; line 23: `_scratch_populate_cached nofill > $seqres.full 2>&1`; line 25: `echo "Fuzz superblock"`; line 26: `_scratch_xfs_fuzz_metadata '' 'online' 'sb 1' >> $seqres.full`; line 27: `echo "Done fuzzing superblock"`. metadata fuzzing target: _scratch_xfs_fuzz_metadata '' 'online' 'sb 1' >> $seqres.full The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/351 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/352 -->
# sources/test-tools/xfstests/tests/xfs/352

## Purpose
Populate a XFS filesystem and fuzz every AGF field. Use xfs_repair to fix the corruption. In this subset it exercises xfs_repair detection and correction of crafted metadata damage; metadata fuzzing through common/fuzzy helper paths. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest dangerous_fuzzers repair fuzzers_repair`. It imports common/preamble, common/filter, common/populate, common/fuzzy. Local helpers are no local shell helpers. Requirement and fix gates include `_require_scratch_xfs_fuzz_fields`. External tools and command surfaces visible in the source include `xfs_repair`, `stat`, `file`, `rm`. Key shell state is carried in mostly transient harness variables, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 20: `_require_scratch_xfs_fuzz_fields`; line 22: `echo "Format and populate"`; line 23: `_scratch_populate_cached nofill > $seqres.full 2>&1`; line 25: `echo "Fuzz AGF"`; line 26: `_scratch_xfs_fuzz_metadata '' 'offline' 'agf 0' >> $seqres.full`; line 27: `echo "Done fuzzing AGF"`. metadata fuzzing target: _scratch_xfs_fuzz_metadata '' 'offline' 'agf 0' >> $seqres.full The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/352 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/353 -->
# sources/test-tools/xfstests/tests/xfs/353

## Purpose
Populate a XFS filesystem and fuzz every AGF field. Use xfs_scrub to fix the corruption. In this subset it exercises xfs_repair detection and correction of crafted metadata damage; xfs_scrub online checking or repair of populated/fuzzed filesystems; metadata fuzzing through common/fuzzy helper paths. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest dangerous_fuzzers scrub fuzzers_online_repair`. It imports common/preamble, common/filter, common/populate, common/fuzzy. Local helpers are no local shell helpers. Requirement and fix gates include `_require_scratch_xfs_fuzz_fields`. External tools and command surfaces visible in the source include `xfs_scrub`, `stat`, `file`, `rm`. Key shell state is carried in mostly transient harness variables, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 20: `_require_scratch_xfs_fuzz_fields`; line 22: `echo "Format and populate"`; line 23: `_scratch_populate_cached nofill > $seqres.full 2>&1`; line 25: `echo "Fuzz AGF"`; line 26: `_scratch_xfs_fuzz_metadata '' 'online' 'agf 0' >> $seqres.full`; line 27: `echo "Done fuzzing AGF"`. metadata fuzzing target: _scratch_xfs_fuzz_metadata '' 'online' 'agf 0' >> $seqres.full The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/353 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/354 -->
# sources/test-tools/xfstests/tests/xfs/354

## Purpose
Populate a XFS filesystem and fuzz every AGFL field. Use xfs_repair to fix the corruption. In this subset it exercises xfs_repair detection and correction of crafted metadata damage; metadata fuzzing through common/fuzzy helper paths. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest dangerous_fuzzers repair fuzzers_repair`. It imports common/preamble, common/filter, common/populate, common/fuzzy. Local helpers are no local shell helpers. Requirement and fix gates include `_require_scratch_xfs_fuzz_fields`. External tools and command surfaces visible in the source include `xfs_db`, `xfs_repair`, `stat`, `sed`, `file`, `rm`. Key shell state is carried in `flfirst`, `SCRATCH_XFS_LIST_METADATA_FIELDS`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 20: `_require_scratch_xfs_fuzz_fields`; line 22: `echo "Format and populate"`; line 23: `_scratch_populate_cached nofill > $seqres.full 2>&1`; line 25: `echo "Fuzz AGFL"`; line 26: `_scratch_xfs_fuzz_metadata '' 'offline' 'agfl 0' >> $seqres.full`; line 27: `echo "Done fuzzing AGFL"`; line 32: `__scratch_xfs_fuzz_mdrestore`; line 33: `flfirst=$(_scratch_xfs_db -c 'agf 0' -c 'p flfirst' | sed -e 's/flfirst = //g')`; line 35: `echo "Fuzz AGFL flfirst"`; plus 2 further source-derived command steps.. metadata fuzzing target: _scratch_xfs_fuzz_metadata '' 'offline' 'agfl 0' >> $seqres.full The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate; error-injection timing and shutdown/recovery behavior are kernel-sensitive. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/354 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/355 -->
# sources/test-tools/xfstests/tests/xfs/355

## Purpose
Populate a XFS filesystem and fuzz every AGFL field. Use xfs_scrub to fix the corruption. In this subset it exercises xfs_repair detection and correction of crafted metadata damage; xfs_scrub online checking or repair of populated/fuzzed filesystems; metadata fuzzing through common/fuzzy helper paths. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest dangerous_fuzzers scrub fuzzers_online_repair`. It imports common/preamble, common/filter, common/populate, common/fuzzy. Local helpers are no local shell helpers. Requirement and fix gates include `_require_scratch_xfs_fuzz_fields`. External tools and command surfaces visible in the source include `xfs_db`, `xfs_scrub`, `stat`, `sed`, `file`, `rm`. Key shell state is carried in `flfirst`, `SCRATCH_XFS_LIST_METADATA_FIELDS`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 20: `_require_scratch_xfs_fuzz_fields`; line 22: `echo "Format and populate"`; line 23: `_scratch_populate_cached nofill > $seqres.full 2>&1`; line 25: `echo "Fuzz AGFL"`; line 26: `_scratch_xfs_fuzz_metadata '' 'online' 'agfl 0' >> $seqres.full`; line 27: `echo "Done fuzzing AGFL"`; line 32: `__scratch_xfs_fuzz_mdrestore`; line 33: `flfirst=$(_scratch_xfs_db -c 'agf 0' -c 'p flfirst' | sed -e 's/flfirst = //g')`; line 35: `echo "Fuzz AGFL flfirst"`; plus 2 further source-derived command steps.. metadata fuzzing target: _scratch_xfs_fuzz_metadata '' 'online' 'agfl 0' >> $seqres.full The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate; error-injection timing and shutdown/recovery behavior are kernel-sensitive. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/355 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/356 -->
# sources/test-tools/xfstests/tests/xfs/356

## Purpose
Populate a XFS filesystem and fuzz every AGI field. Use xfs_repair to fix the corruption. In this subset it exercises xfs_repair detection and correction of crafted metadata damage; metadata fuzzing through common/fuzzy helper paths. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest dangerous_fuzzers repair fuzzers_repair`. It imports common/preamble, common/filter, common/populate, common/fuzzy. Local helpers are no local shell helpers. Requirement and fix gates include `_require_scratch_xfs_fuzz_fields`. External tools and command surfaces visible in the source include `xfs_repair`, `stat`, `file`, `rm`. Key shell state is carried in mostly transient harness variables, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 20: `_require_scratch_xfs_fuzz_fields`; line 22: `echo "Format and populate"`; line 23: `_scratch_populate_cached nofill > $seqres.full 2>&1`; line 25: `echo "Fuzz AGI"`; line 26: `_scratch_xfs_fuzz_metadata '' 'offline' 'agi 0' >> $seqres.full`; line 27: `echo "Done fuzzing AGI"`. metadata fuzzing target: _scratch_xfs_fuzz_metadata '' 'offline' 'agi 0' >> $seqres.full The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/356 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/357 -->
# sources/test-tools/xfstests/tests/xfs/357

## Purpose
Populate a XFS filesystem and fuzz every AGI field. Use xfs_scrub to fix the corruption. In this subset it exercises xfs_repair detection and correction of crafted metadata damage; xfs_scrub online checking or repair of populated/fuzzed filesystems; metadata fuzzing through common/fuzzy helper paths. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest dangerous_fuzzers scrub fuzzers_online_repair`. It imports common/preamble, common/filter, common/populate, common/fuzzy. Local helpers are no local shell helpers. Requirement and fix gates include `_require_scratch_xfs_fuzz_fields`. External tools and command surfaces visible in the source include `xfs_scrub`, `stat`, `file`, `rm`. Key shell state is carried in mostly transient harness variables, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 20: `_require_scratch_xfs_fuzz_fields`; line 22: `echo "Format and populate"`; line 23: `_scratch_populate_cached nofill > $seqres.full 2>&1`; line 25: `echo "Fuzz AGI"`; line 26: `_scratch_xfs_fuzz_metadata '' 'online' 'agi 1' >> $seqres.full`; line 27: `echo "Done fuzzing AGI"`. metadata fuzzing target: _scratch_xfs_fuzz_metadata '' 'online' 'agi 1' >> $seqres.full The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/357 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/358 -->
# sources/test-tools/xfstests/tests/xfs/358

## Purpose
Populate a XFS filesystem and fuzz every bnobt field. Use xfs_repair to fix the corruption. In this subset it exercises xfs_repair detection and correction of crafted metadata damage; metadata fuzzing through common/fuzzy helper paths. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest dangerous_fuzzers repair fuzzers_repair`. It imports common/preamble, common/filter, common/populate, common/fuzzy. Local helpers are no local shell helpers. Requirement and fix gates include `_require_scratch_xfs_fuzz_fields`. External tools and command surfaces visible in the source include `xfs_repair`, `dd`, `stat`, `file`, `rm`. Key shell state is carried in `path`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 20: `_require_scratch_xfs_fuzz_fields`; line 22: `echo "Format and populate"`; line 23: `_scratch_populate_cached nofill > $seqres.full 2>&1`; line 25: `path="$(_scratch_xfs_find_agbtree_height 'bno' 2)" || \`; line 28: `echo "Fuzz bnobt recs"`; line 29: `_scratch_xfs_fuzz_metadata '' 'offline'  "$path" 'addr bnoroot' 'addr ptrs[1]' >> $seqres.full`; line 30: `echo "Done fuzzing bnobt recs"`. metadata fuzzing target: _scratch_xfs_fuzz_metadata '' 'offline'  "$path" 'addr bnoroot' 'addr ptrs[1]' >> $seqres.full The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/358 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/359 -->
# sources/test-tools/xfstests/tests/xfs/359

## Purpose
Populate a XFS filesystem and fuzz every bnobt field. Use xfs_scrub to fix the corruption. In this subset it exercises xfs_repair detection and correction of crafted metadata damage; xfs_scrub online checking or repair of populated/fuzzed filesystems; metadata fuzzing through common/fuzzy helper paths. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest dangerous_fuzzers scrub fuzzers_online_repair`. It imports common/preamble, common/filter, common/populate, common/fuzzy. Local helpers are no local shell helpers. Requirement and fix gates include `_require_scratch_xfs_fuzz_fields`. External tools and command surfaces visible in the source include `xfs_scrub`, `dd`, `stat`, `file`, `rm`. Key shell state is carried in `path`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 20: `_require_scratch_xfs_fuzz_fields`; line 22: `echo "Format and populate"`; line 23: `_scratch_populate_cached nofill > $seqres.full 2>&1`; line 25: `path="$(_scratch_xfs_find_agbtree_height 'bno' 2)" || \`; line 28: `echo "Fuzz bnobt recs"`; line 29: `_scratch_xfs_fuzz_metadata '' 'online'  "$path" 'addr bnoroot' 'addr ptrs[1]' >> $seqres.full`; line 30: `echo "Done fuzzing bnobt recs"`. metadata fuzzing target: _scratch_xfs_fuzz_metadata '' 'online'  "$path" 'addr bnoroot' 'addr ptrs[1]' >> $seqres.full The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/359 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/360 -->
# sources/test-tools/xfstests/tests/xfs/360

## Purpose
Populate a XFS filesystem and fuzz every bnobt key/pointer. Use xfs_repair to fix the corruption. In this subset it exercises xfs_repair detection and correction of crafted metadata damage; metadata fuzzing through common/fuzzy helper paths. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest dangerous_fuzzers repair fuzzers_repair`. It imports common/preamble, common/filter, common/populate, common/fuzzy. Local helpers are no local shell helpers. Requirement and fix gates include `_require_scratch_xfs_fuzz_fields`. External tools and command surfaces visible in the source include `xfs_repair`, `dd`, `stat`, `file`, `rm`. Key shell state is carried in `path`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 20: `_require_scratch_xfs_fuzz_fields`; line 22: `echo "Format and populate"`; line 23: `_scratch_populate_cached nofill > $seqres.full 2>&1`; line 25: `path="$(_scratch_xfs_find_agbtree_height 'bno' 2)" || \`; line 28: `echo "Fuzz bnobt keyptr"`; line 29: `_scratch_xfs_fuzz_metadata '' 'offline'  "$path" 'addr bnoroot' >> $seqres.full`; line 30: `echo "Done fuzzing bnobt keyptr"`. metadata fuzzing target: _scratch_xfs_fuzz_metadata '' 'offline'  "$path" 'addr bnoroot' >> $seqres.full The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/360 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/361 -->
# sources/test-tools/xfstests/tests/xfs/361

## Purpose
Populate a XFS filesystem and fuzz every bnobt key/pointer. Use xfs_scrub to fix the corruption. In this subset it exercises xfs_repair detection and correction of crafted metadata damage; xfs_scrub online checking or repair of populated/fuzzed filesystems; metadata fuzzing through common/fuzzy helper paths. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest dangerous_fuzzers scrub fuzzers_online_repair`. It imports common/preamble, common/filter, common/populate, common/fuzzy. Local helpers are no local shell helpers. Requirement and fix gates include `_require_scratch_xfs_fuzz_fields`. External tools and command surfaces visible in the source include `xfs_scrub`, `dd`, `stat`, `file`, `rm`. Key shell state is carried in `path`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 20: `_require_scratch_xfs_fuzz_fields`; line 22: `echo "Format and populate"`; line 23: `_scratch_populate_cached nofill > $seqres.full 2>&1`; line 25: `path="$(_scratch_xfs_find_agbtree_height 'bno' 2)" || \`; line 28: `echo "Fuzz bnobt keyptr"`; line 29: `_scratch_xfs_fuzz_metadata '' 'online'  "$path" 'addr bnoroot' >> $seqres.full`; line 30: `echo "Done fuzzing bnobt keyptr"`. metadata fuzzing target: _scratch_xfs_fuzz_metadata '' 'online'  "$path" 'addr bnoroot' >> $seqres.full The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/361 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/362 -->
# sources/test-tools/xfstests/tests/xfs/362

## Purpose
Populate a XFS filesystem and fuzz every cntbt field. Use xfs_repair to fix the corruption. In this subset it exercises xfs_repair detection and correction of crafted metadata damage; metadata fuzzing through common/fuzzy helper paths. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest dangerous_fuzzers repair fuzzers_repair`. It imports common/preamble, common/filter, common/populate, common/fuzzy. Local helpers are no local shell helpers. Requirement and fix gates include `_require_scratch_xfs_fuzz_fields`. External tools and command surfaces visible in the source include `xfs_repair`, `dd`, `stat`, `file`, `rm`. Key shell state is carried in `path`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 20: `_require_scratch_xfs_fuzz_fields`; line 22: `echo "Format and populate"`; line 23: `_scratch_populate_cached nofill > $seqres.full 2>&1`; line 25: `path="$(_scratch_xfs_find_agbtree_height 'cnt' 2)" || \`; line 28: `echo "Fuzz cntbt"`; line 29: `_scratch_xfs_fuzz_metadata '' 'offline'  "$path" 'addr cntroot' 'addr ptrs[1]' >> $seqres.full`; line 30: `echo "Done fuzzing cntbt"`. metadata fuzzing target: _scratch_xfs_fuzz_metadata '' 'offline'  "$path" 'addr cntroot' 'addr ptrs[1]' >> $seqres.full The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/362 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/363 -->
# sources/test-tools/xfstests/tests/xfs/363

## Purpose
Populate a XFS filesystem and fuzz every cntbt field. Use xfs_scrub to fix the corruption. In this subset it exercises xfs_repair detection and correction of crafted metadata damage; xfs_scrub online checking or repair of populated/fuzzed filesystems; metadata fuzzing through common/fuzzy helper paths. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest dangerous_fuzzers scrub fuzzers_online_repair`. It imports common/preamble, common/filter, common/populate, common/fuzzy. Local helpers are no local shell helpers. Requirement and fix gates include `_require_scratch_xfs_fuzz_fields`. External tools and command surfaces visible in the source include `xfs_scrub`, `dd`, `stat`, `file`, `rm`. Key shell state is carried in `path`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 20: `_require_scratch_xfs_fuzz_fields`; line 22: `echo "Format and populate"`; line 23: `_scratch_populate_cached nofill > $seqres.full 2>&1`; line 25: `path="$(_scratch_xfs_find_agbtree_height 'cnt' 2)" || \`; line 28: `echo "Fuzz cntbt"`; line 29: `_scratch_xfs_fuzz_metadata '' 'online'  "$path" 'addr cntroot' 'addr ptrs[1]' >> $seqres.full`; line 30: `echo "Done fuzzing cntbt"`. metadata fuzzing target: _scratch_xfs_fuzz_metadata '' 'online'  "$path" 'addr cntroot' 'addr ptrs[1]' >> $seqres.full The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/363 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/364 -->
# sources/test-tools/xfstests/tests/xfs/364

## Purpose
Populate a XFS filesystem and fuzz every inobt field. Use xfs_repair to fix the corruption. In this subset it exercises xfs_repair detection and correction of crafted metadata damage; metadata fuzzing through common/fuzzy helper paths. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest dangerous_fuzzers repair fuzzers_repair`. It imports common/preamble, common/filter, common/populate, common/fuzzy. Local helpers are no local shell helpers. Requirement and fix gates include `_require_scratch_xfs_fuzz_fields`. External tools and command surfaces visible in the source include `xfs_repair`, `dd`, `stat`, `file`, `rm`. Key shell state is carried in `path`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 20: `_require_scratch_xfs_fuzz_fields`; line 22: `echo "Format and populate"`; line 23: `_scratch_populate_cached nofill > $seqres.full 2>&1`; line 25: `path="$(_scratch_xfs_find_agbtree_height 'ino' 2)" || \`; line 28: `echo "Fuzz inobt"`; line 29: `_scratch_xfs_fuzz_metadata '' 'offline'  "$path" 'addr root' 'addr ptrs[1]' >> $seqres.full`; line 30: `echo "Done fuzzing inobt"`. metadata fuzzing target: _scratch_xfs_fuzz_metadata '' 'offline'  "$path" 'addr root' 'addr ptrs[1]' >> $seqres.full The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/364 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/365 -->
# sources/test-tools/xfstests/tests/xfs/365

## Purpose
Populate a XFS filesystem and fuzz every inobt field. Use xfs_scrub to fix the corruption. In this subset it exercises xfs_repair detection and correction of crafted metadata damage; xfs_scrub online checking or repair of populated/fuzzed filesystems; metadata fuzzing through common/fuzzy helper paths. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest dangerous_fuzzers scrub fuzzers_online_repair`. It imports common/preamble, common/filter, common/populate, common/fuzzy. Local helpers are no local shell helpers. Requirement and fix gates include `_require_scratch_xfs_fuzz_fields`. External tools and command surfaces visible in the source include `xfs_scrub`, `dd`, `stat`, `file`, `rm`. Key shell state is carried in `path`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 20: `_require_scratch_xfs_fuzz_fields`; line 22: `echo "Format and populate"`; line 23: `_scratch_populate_cached nofill > $seqres.full 2>&1`; line 25: `path="$(_scratch_xfs_find_agbtree_height 'ino' 2)" || \`; line 28: `echo "Fuzz inobt"`; line 29: `_scratch_xfs_fuzz_metadata '' 'online'  "$path" 'addr root' 'addr ptrs[1]' >> $seqres.full`; line 30: `echo "Done fuzzing inobt"`. metadata fuzzing target: _scratch_xfs_fuzz_metadata '' 'online'  "$path" 'addr root' 'addr ptrs[1]' >> $seqres.full The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/365 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/366 -->
# sources/test-tools/xfstests/tests/xfs/366

## Purpose
Populate a XFS filesystem and fuzz every finobt field. Use xfs_repair to fix the corruption. In this subset it exercises xfs_repair detection and correction of crafted metadata damage; metadata fuzzing through common/fuzzy helper paths. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest dangerous_fuzzers repair fuzzers_repair`. It imports common/preamble, common/filter, common/populate, common/fuzzy. Local helpers are no local shell helpers. Requirement and fix gates include `_require_scratch_xfs_fuzz_fields`; `_require_xfs_finobt`. External tools and command surfaces visible in the source include `xfs_repair`, `dd`, `stat`, `file`, `rm`. Key shell state is carried in `path`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 20: `_require_scratch_xfs_fuzz_fields`; line 21: `_require_xfs_finobt`; line 23: `echo "Format and populate"`; line 24: `_scratch_populate_cached nofill > $seqres.full 2>&1`; line 26: `path="$(_scratch_xfs_find_agbtree_height 'fino' 2)" || \`; line 29: `echo "Fuzz finobt"`; line 30: `_scratch_xfs_fuzz_metadata '' 'offline'  "$path" 'addr free_root' 'addr ptrs[1]' >> $seqres.full`; line 31: `echo "Done fuzzing finobt"`. metadata fuzzing target: _scratch_xfs_fuzz_metadata '' 'offline'  "$path" 'addr free_root' 'addr ptrs[1]' >> $seqres.full The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/366 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/367 -->
# sources/test-tools/xfstests/tests/xfs/367

## Purpose
Populate a XFS filesystem and fuzz every finobt field. Use xfs_scrub to fix the corruption. In this subset it exercises xfs_repair detection and correction of crafted metadata damage; xfs_scrub online checking or repair of populated/fuzzed filesystems; metadata fuzzing through common/fuzzy helper paths. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest dangerous_fuzzers scrub fuzzers_online_repair`. It imports common/preamble, common/filter, common/populate, common/fuzzy. Local helpers are no local shell helpers. Requirement and fix gates include `_require_scratch_xfs_fuzz_fields`; `_require_xfs_finobt`. External tools and command surfaces visible in the source include `xfs_scrub`, `dd`, `stat`, `file`, `rm`. Key shell state is carried in `path`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 20: `_require_scratch_xfs_fuzz_fields`; line 21: `_require_xfs_finobt`; line 23: `echo "Format and populate"`; line 24: `_scratch_populate_cached nofill > $seqres.full 2>&1`; line 26: `path="$(_scratch_xfs_find_agbtree_height 'fino' 2)" || \`; line 29: `echo "Fuzz finobt"`; line 30: `_scratch_xfs_fuzz_metadata '' 'online'  "$path" 'addr free_root' 'addr ptrs[1]' >> $seqres.full`; line 31: `echo "Done fuzzing finobt"`. metadata fuzzing target: _scratch_xfs_fuzz_metadata '' 'online'  "$path" 'addr free_root' 'addr ptrs[1]' >> $seqres.full The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/367 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/368 -->
# sources/test-tools/xfstests/tests/xfs/368

## Purpose
Populate a XFS filesystem and fuzz every rmapbt field. Use xfs_repair to fix the corruption. In this subset it exercises reverse mapping metadata and owner-accounting validation; xfs_repair detection and correction of crafted metadata damage; metadata fuzzing through common/fuzzy helper paths. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest dangerous_fuzzers repair fuzzers_repair`. It imports common/preamble, common/filter, common/populate, common/fuzzy. Local helpers are no local shell helpers. Requirement and fix gates include `_require_xfs_scratch_rmapbt`; `_require_scratch_xfs_fuzz_fields`. External tools and command surfaces visible in the source include `xfs_repair`, `dd`, `stat`, `file`, `rm`. Key shell state is carried in `path`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 20: `_require_xfs_scratch_rmapbt`; line 21: `_require_scratch_xfs_fuzz_fields`; line 23: `echo "Format and populate"`; line 24: `_scratch_populate_cached nofill > $seqres.full 2>&1`; line 26: `path="$(_scratch_xfs_find_agbtree_height 'rmap' 2)" || \`; line 29: `echo "Fuzz rmapbt recs"`; line 30: `_scratch_xfs_fuzz_metadata '' 'offline' "$path" 'addr rmaproot' 'addr ptrs[1]' >> $seqres.full`; line 31: `echo "Done fuzzing rmapbt recs"`. metadata fuzzing target: _scratch_xfs_fuzz_metadata '' 'offline' "$path" 'addr rmaproot' 'addr ptrs[1]' >> $seqres.full The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/368 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/369 -->
# sources/test-tools/xfstests/tests/xfs/369

## Purpose
Populate a XFS filesystem and fuzz every rmapbt field. Use xfs_scrub to fix the corruption. In this subset it exercises reverse mapping metadata and owner-accounting validation; xfs_repair detection and correction of crafted metadata damage; xfs_scrub online checking or repair of populated/fuzzed filesystems; metadata fuzzing through common/fuzzy helper paths. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest dangerous_fuzzers scrub fuzzers_online_repair`. It imports common/preamble, common/filter, common/populate, common/fuzzy. Local helpers are no local shell helpers. Requirement and fix gates include `_require_xfs_scratch_rmapbt`; `_require_scratch_xfs_fuzz_fields`. External tools and command surfaces visible in the source include `xfs_scrub`, `dd`, `stat`, `file`, `rm`. Key shell state is carried in `path`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 20: `_require_xfs_scratch_rmapbt`; line 21: `_require_scratch_xfs_fuzz_fields`; line 23: `echo "Format and populate"`; line 24: `_scratch_populate_cached nofill > $seqres.full 2>&1`; line 26: `path="$(_scratch_xfs_find_agbtree_height 'rmap' 2)" || \`; line 29: `echo "Fuzz rmapbt recs"`; line 30: `_scratch_xfs_fuzz_metadata '' 'online' "$path" 'addr rmaproot' 'addr ptrs[1]' >> $seqres.full`; line 31: `echo "Done fuzzing rmapbt recs"`. metadata fuzzing target: _scratch_xfs_fuzz_metadata '' 'online' "$path" 'addr rmaproot' 'addr ptrs[1]' >> $seqres.full The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/369 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/370 -->
# sources/test-tools/xfstests/tests/xfs/370

## Purpose
Populate a XFS filesystem and fuzz every rmapbt key/pointer field. Use xfs_repair to fix the corruption. Use xfs_repair to repair the problems. In this subset it exercises reverse mapping metadata and owner-accounting validation; xfs_repair detection and correction of crafted metadata damage; metadata fuzzing through common/fuzzy helper paths. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest dangerous_fuzzers repair fuzzers_repair`. It imports common/preamble, common/filter, common/populate, common/fuzzy. Local helpers are no local shell helpers. Requirement and fix gates include `_require_xfs_scratch_rmapbt`; `_require_scratch_xfs_fuzz_fields`. External tools and command surfaces visible in the source include `xfs_repair`, `dd`, `stat`, `file`, `rm`. Key shell state is carried in `path`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 21: `_require_xfs_scratch_rmapbt`; line 22: `_require_scratch_xfs_fuzz_fields`; line 24: `echo "Format and populate"`; line 25: `_scratch_populate_cached nofill > $seqres.full 2>&1`; line 27: `path="$(_scratch_xfs_find_agbtree_height 'rmap' 2)" || \`; line 30: `echo "Fuzz rmapbt keyptr"`; line 31: `_scratch_xfs_fuzz_metadata '' 'offline' "$path" 'addr rmaproot' >> $seqres.full`; line 32: `echo "Done fuzzing rmapbt keyptr"`. metadata fuzzing target: _scratch_xfs_fuzz_metadata '' 'offline' "$path" 'addr rmaproot' >> $seqres.full The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/370 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/371 -->
# sources/test-tools/xfstests/tests/xfs/371

## Purpose
Populate a XFS filesystem and fuzz every rmapbt key/pointer field. Use xfs_scrub to fix the corruption. Use xfs_scrub to repair the problems. In this subset it exercises reverse mapping metadata and owner-accounting validation; xfs_repair detection and correction of crafted metadata damage; xfs_scrub online checking or repair of populated/fuzzed filesystems; metadata fuzzing through common/fuzzy helper paths. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest dangerous_fuzzers scrub fuzzers_online_repair`. It imports common/preamble, common/filter, common/populate, common/fuzzy. Local helpers are no local shell helpers. Requirement and fix gates include `_require_xfs_scratch_rmapbt`; `_require_scratch_xfs_fuzz_fields`. External tools and command surfaces visible in the source include `xfs_scrub`, `dd`, `stat`, `file`, `rm`. Key shell state is carried in `path`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 21: `_require_xfs_scratch_rmapbt`; line 22: `_require_scratch_xfs_fuzz_fields`; line 24: `echo "Format and populate"`; line 25: `_scratch_populate_cached nofill > $seqres.full 2>&1`; line 27: `path="$(_scratch_xfs_find_agbtree_height 'rmap' 2)" || \`; line 30: `echo "Fuzz rmapbt keyptr"`; line 31: `_scratch_xfs_fuzz_metadata '' 'online' "$path" 'addr rmaproot' >> $seqres.full`; line 32: `echo "Done fuzzing rmapbt keyptr"`. metadata fuzzing target: _scratch_xfs_fuzz_metadata '' 'online' "$path" 'addr rmaproot' >> $seqres.full The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/371 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/372 -->
# sources/test-tools/xfstests/tests/xfs/372

## Purpose
Populate a XFS filesystem and fuzz every refcountbt field. Use xfs_repair to fix the corruption. In this subset it exercises xfs_repair detection and correction of crafted metadata damage; metadata fuzzing through common/fuzzy helper paths. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest dangerous_fuzzers repair fuzzers_repair`. It imports common/preamble, common/filter, common/populate, common/fuzzy, common/reflink. Local helpers are no local shell helpers. Requirement and fix gates include `_require_scratch_reflink`; `_require_scratch_xfs_fuzz_fields`. External tools and command surfaces visible in the source include `xfs_repair`, `dd`, `stat`, `file`, `rm`. Key shell state is carried in `path`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 22: `_require_scratch_xfs_fuzz_fields`; line 24: `echo "Format and populate"`; line 25: `_scratch_populate_cached nofill > $seqres.full 2>&1`; line 27: `path="$(_scratch_xfs_find_agbtree_height 'refcnt' 2)" || \`; line 30: `echo "Fuzz refcountbt"`; line 31: `_scratch_xfs_fuzz_metadata '' 'offline'  "$path" 'addr refcntroot' >> $seqres.full`; line 32: `echo "Done fuzzing refcountbt"`. metadata fuzzing target: _scratch_xfs_fuzz_metadata '' 'offline'  "$path" 'addr refcntroot' >> $seqres.full creates shared extents and CoW/refcount state The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate; shared extent and CoW accounting depends on reflink/refcount support. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/372 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/373 -->
# sources/test-tools/xfstests/tests/xfs/373

## Purpose
Populate a XFS filesystem and fuzz every refcountbt key/pointer field. Use xfs_scrub to fix the corruption. In this subset it exercises xfs_repair detection and correction of crafted metadata damage; xfs_scrub online checking or repair of populated/fuzzed filesystems; metadata fuzzing through common/fuzzy helper paths. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest dangerous_fuzzers scrub fuzzers_online_repair`. It imports common/preamble, common/filter, common/populate, common/fuzzy, common/reflink. Local helpers are no local shell helpers. Requirement and fix gates include `_require_scratch_reflink`; `_require_scratch_xfs_fuzz_fields`. External tools and command surfaces visible in the source include `xfs_scrub`, `dd`, `stat`, `file`, `rm`. Key shell state is carried in `path`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 22: `_require_scratch_xfs_fuzz_fields`; line 24: `echo "Format and populate"`; line 25: `_scratch_populate_cached nofill > $seqres.full 2>&1`; line 27: `path="$(_scratch_xfs_find_agbtree_height 'refcnt' 2)" || \`; line 30: `echo "Fuzz refcountbt"`; line 31: `_scratch_xfs_fuzz_metadata '' 'online'  "$path" 'addr refcntroot' >> $seqres.full`; line 32: `echo "Done fuzzing refcountbt"`. metadata fuzzing target: _scratch_xfs_fuzz_metadata '' 'online'  "$path" 'addr refcntroot' >> $seqres.full creates shared extents and CoW/refcount state The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate; shared extent and CoW accounting depends on reflink/refcount support. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/373 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/374 -->
# sources/test-tools/xfstests/tests/xfs/374

## Purpose
Populate a XFS filesystem and fuzz every btree-format directory inode field. Use xfs_repair to fix the corruption. In this subset it exercises xfs_repair detection and correction of crafted metadata damage; metadata fuzzing through common/fuzzy helper paths; directory metadata layout and traversal behavior. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest dangerous_fuzzers repair fuzzers_repair`. It imports common/preamble, common/filter, common/populate, common/fuzzy. Local helpers are no local shell helpers. Requirement and fix gates include `_require_scratch_xfs_fuzz_fields`. External tools and command surfaces visible in the source include `xfs_repair`, `mount`, `stat`, `file`, `rm`. Key shell state is carried in `inum`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 20: `_require_scratch_xfs_fuzz_fields`; line 22: `echo "Format and populate"`; line 23: `_scratch_populate_cached nofill > $seqres.full 2>&1`; line 25: `echo "Find btree-format dir inode"`; line 26: `_scratch_mount`; line 28: `_scratch_unmount`; line 30: `echo "Fuzz inode"`; line 31: `_scratch_xfs_fuzz_metadata '' 'offline'  "inode ${inum}" >> $seqres.full`; line 32: `echo "Done fuzzing inode"`. metadata fuzzing target: _scratch_xfs_fuzz_metadata '' 'offline'  "inode ${inum}" >> $seqres.full The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/374 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/375 -->
# sources/test-tools/xfstests/tests/xfs/375

## Purpose
Populate a XFS filesystem and fuzz every btree-format directory inode field. Use xfs_scrub to fix the corruption. In this subset it exercises xfs_repair detection and correction of crafted metadata damage; xfs_scrub online checking or repair of populated/fuzzed filesystems; metadata fuzzing through common/fuzzy helper paths; directory metadata layout and traversal behavior. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest dangerous_fuzzers scrub fuzzers_online_repair`. It imports common/preamble, common/filter, common/populate, common/fuzzy. Local helpers are no local shell helpers. Requirement and fix gates include `_require_scratch_xfs_fuzz_fields`. External tools and command surfaces visible in the source include `xfs_scrub`, `mount`, `stat`, `file`, `rm`. Key shell state is carried in `inum`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 20: `_require_scratch_xfs_fuzz_fields`; line 22: `echo "Format and populate"`; line 23: `_scratch_populate_cached nofill > $seqres.full 2>&1`; line 25: `echo "Find btree-format dir inode"`; line 26: `_scratch_mount`; line 28: `_scratch_unmount`; line 30: `echo "Fuzz inode"`; line 31: `_scratch_xfs_fuzz_metadata '' 'online'  "inode ${inum}" >> $seqres.full`; line 32: `echo "Done fuzzing inode"`. metadata fuzzing target: _scratch_xfs_fuzz_metadata '' 'online'  "inode ${inum}" >> $seqres.full The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/375 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/376 -->
# sources/test-tools/xfstests/tests/xfs/376

## Purpose
Populate a XFS filesystem and fuzz every extents-format file inode field. Use xfs_repair to fix the corruption. In this subset it exercises xfs_repair detection and correction of crafted metadata damage; metadata fuzzing through common/fuzzy helper paths. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest dangerous_fuzzers repair fuzzers_repair`. It imports common/preamble, common/filter, common/populate, common/fuzzy. Local helpers are no local shell helpers. Requirement and fix gates include `_require_scratch_xfs_fuzz_fields`. External tools and command surfaces visible in the source include `xfs_repair`, `mount`, `stat`, `file`, `rm`. Key shell state is carried in `inum`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 20: `_require_scratch_xfs_fuzz_fields`; line 22: `echo "Format and populate"`; line 23: `_scratch_populate_cached nofill > $seqres.full 2>&1`; line 25: `echo "Find extents-format file inode"`; line 26: `_scratch_mount`; line 28: `_scratch_unmount`; line 30: `echo "Fuzz inode"`; line 31: `_scratch_xfs_fuzz_metadata '' 'offline'  "inode ${inum}" >> $seqres.full`; line 32: `echo "Done fuzzing inode"`. metadata fuzzing target: _scratch_xfs_fuzz_metadata '' 'offline'  "inode ${inum}" >> $seqres.full The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/376 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/377 -->
# sources/test-tools/xfstests/tests/xfs/377

## Purpose
Populate a XFS filesystem and fuzz every extents-format file inode field. Use xfs_scrub to fix the corruption. In this subset it exercises xfs_repair detection and correction of crafted metadata damage; xfs_scrub online checking or repair of populated/fuzzed filesystems; metadata fuzzing through common/fuzzy helper paths. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest dangerous_fuzzers scrub fuzzers_online_repair`. It imports common/preamble, common/filter, common/populate, common/fuzzy. Local helpers are no local shell helpers. Requirement and fix gates include `_require_scratch_xfs_fuzz_fields`. External tools and command surfaces visible in the source include `xfs_scrub`, `mount`, `stat`, `file`, `rm`. Key shell state is carried in `inum`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 20: `_require_scratch_xfs_fuzz_fields`; line 22: `echo "Format and populate"`; line 23: `_scratch_populate_cached nofill > $seqres.full 2>&1`; line 25: `echo "Find extents-format file inode"`; line 26: `_scratch_mount`; line 28: `_scratch_unmount`; line 30: `echo "Fuzz inode"`; line 31: `_scratch_xfs_fuzz_metadata '' 'online'  "inode ${inum}" >> $seqres.full`; line 32: `echo "Done fuzzing inode"`. metadata fuzzing target: _scratch_xfs_fuzz_metadata '' 'online'  "inode ${inum}" >> $seqres.full The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/377 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/378 -->
# sources/test-tools/xfstests/tests/xfs/378

## Purpose
Populate a XFS filesystem and fuzz every btree-format file inode field. Use xfs_repair to fix the corruption. In this subset it exercises xfs_repair detection and correction of crafted metadata damage; metadata fuzzing through common/fuzzy helper paths. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest dangerous_fuzzers repair fuzzers_repair`. It imports common/preamble, common/filter, common/populate, common/fuzzy. Local helpers are no local shell helpers. Requirement and fix gates include `_require_scratch_xfs_fuzz_fields`. External tools and command surfaces visible in the source include `xfs_repair`, `mount`, `stat`, `file`, `rm`. Key shell state is carried in `inum`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 20: `_require_scratch_xfs_fuzz_fields`; line 22: `echo "Format and populate"`; line 23: `_scratch_populate_cached nofill > $seqres.full 2>&1`; line 25: `echo "Find btree-format file inode"`; line 26: `_scratch_mount`; line 28: `_scratch_unmount`; line 30: `echo "Fuzz inode"`; line 31: `_scratch_xfs_fuzz_metadata '' 'offline'  "inode ${inum}" >> $seqres.full`; line 32: `echo "Done fuzzing inode"`. metadata fuzzing target: _scratch_xfs_fuzz_metadata '' 'offline'  "inode ${inum}" >> $seqres.full The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/378 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/379 -->
# sources/test-tools/xfstests/tests/xfs/379

## Purpose
Populate a XFS filesystem and fuzz every btree-format file inode field. Use xfs_scrub to fix the corruption. In this subset it exercises xfs_repair detection and correction of crafted metadata damage; xfs_scrub online checking or repair of populated/fuzzed filesystems; metadata fuzzing through common/fuzzy helper paths. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest dangerous_fuzzers scrub fuzzers_online_repair`. It imports common/preamble, common/filter, common/populate, common/fuzzy. Local helpers are no local shell helpers. Requirement and fix gates include `_require_scratch_xfs_fuzz_fields`. External tools and command surfaces visible in the source include `xfs_scrub`, `mount`, `stat`, `file`, `rm`. Key shell state is carried in `inum`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 20: `_require_scratch_xfs_fuzz_fields`; line 22: `echo "Format and populate"`; line 23: `_scratch_populate_cached nofill > $seqres.full 2>&1`; line 25: `echo "Find btree-format file inode"`; line 26: `_scratch_mount`; line 28: `_scratch_unmount`; line 30: `echo "Fuzz inode"`; line 31: `_scratch_xfs_fuzz_metadata '' 'online'  "inode ${inum}" >> $seqres.full`; line 32: `echo "Done fuzzing inode"`. metadata fuzzing target: _scratch_xfs_fuzz_metadata '' 'online'  "inode ${inum}" >> $seqres.full The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/379 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/380 -->
# sources/test-tools/xfstests/tests/xfs/380

## Purpose
Populate a XFS filesystem and fuzz every bmbt block field. Use xfs_repair to fix the corruption. In this subset it exercises xfs_repair detection and correction of crafted metadata damage; metadata fuzzing through common/fuzzy helper paths. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest dangerous_fuzzers repair fuzzers_repair`. It imports common/preamble, common/filter, common/populate, common/fuzzy. Local helpers are no local shell helpers. Requirement and fix gates include `_require_scratch_xfs_fuzz_fields`. External tools and command surfaces visible in the source include `xfs_repair`, `dd`, `mount`, `stat`, `file`, `rm`. Key shell state is carried in `inum`, `inode_ver`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 20: `_require_scratch_xfs_fuzz_fields`; line 22: `echo "Format and populate"`; line 23: `_scratch_populate_cached nofill > $seqres.full 2>&1`; line 25: `echo "Find bmbt block"`; line 26: `_scratch_mount`; line 28: `_scratch_unmount`; line 30: `inode_ver=$(_scratch_xfs_get_metadata_field "core.version" "inode ${inum}")`; line 32: `echo "Fuzz bmbt"`; line 33: `_scratch_xfs_fuzz_metadata '' 'offline'  "inode ${inum}" "addr u${inode_ver}.bmbt.ptrs[1]" >> $seqres.full`; plus 1 further source-derived command steps.. metadata fuzzing target: _scratch_xfs_fuzz_metadata '' 'offline'  "inode ${inum}" "addr u${inode_ver}.bmbt.ptrs[1]" >> $seqres.full The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/380 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/381 -->
# sources/test-tools/xfstests/tests/xfs/381

## Purpose
Populate a XFS filesystem and fuzz every bmbt block field. Use xfs_scrub to fix the corruption. In this subset it exercises xfs_repair detection and correction of crafted metadata damage; xfs_scrub online checking or repair of populated/fuzzed filesystems; metadata fuzzing through common/fuzzy helper paths. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest dangerous_fuzzers scrub fuzzers_online_repair`. It imports common/preamble, common/filter, common/populate, common/fuzzy. Local helpers are no local shell helpers. Requirement and fix gates include `_require_scratch_xfs_fuzz_fields`. External tools and command surfaces visible in the source include `xfs_scrub`, `dd`, `mount`, `stat`, `file`, `rm`. Key shell state is carried in `inum`, `inode_ver`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 20: `_require_scratch_xfs_fuzz_fields`; line 22: `echo "Format and populate"`; line 23: `_scratch_populate_cached nofill > $seqres.full 2>&1`; line 25: `echo "Find bmbt block"`; line 26: `_scratch_mount`; line 28: `_scratch_unmount`; line 30: `inode_ver=$(_scratch_xfs_get_metadata_field "core.version" "inode ${inum}")`; line 32: `echo "Fuzz bmbt"`; line 33: `_scratch_xfs_fuzz_metadata '' 'online'  "inode ${inum}" "addr u${inode_ver}.bmbt.ptrs[1]" >> $seqres.full`; plus 1 further source-derived command steps.. metadata fuzzing target: _scratch_xfs_fuzz_metadata '' 'online'  "inode ${inum}" "addr u${inode_ver}.bmbt.ptrs[1]" >> $seqres.full The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/381 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/382 -->
# sources/test-tools/xfstests/tests/xfs/382

## Purpose
Populate a XFS filesystem and fuzz every symlink remote block field. Use xfs_repair to fix the corruption. In this subset it exercises xfs_repair detection and correction of crafted metadata damage; metadata fuzzing through common/fuzzy helper paths. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest dangerous_fuzzers repair fuzzers_repair`. It imports common/preamble, common/filter, common/populate, common/fuzzy. Local helpers are no local shell helpers. Requirement and fix gates include `_require_scratch_xfs_fuzz_fields`. External tools and command surfaces visible in the source include `xfs_repair`, `mount`, `stat`, `file`, `rm`. Key shell state is carried in `inum`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 20: `_require_scratch_xfs_fuzz_fields`; line 22: `echo "Format and populate"`; line 23: `_scratch_populate_cached nofill > $seqres.full 2>&1`; line 25: `echo "Find symlink remote block"`; line 26: `_scratch_mount`; line 28: `_scratch_unmount`; line 30: `echo "Fuzz symlink remote block"`; line 31: `_scratch_xfs_fuzz_metadata '' 'offline' "inode ${inum}" 'dblock 0' >> $seqres.full`; line 32: `echo "Done fuzzing symlink remote block"`. metadata fuzzing target: _scratch_xfs_fuzz_metadata '' 'offline' "inode ${inum}" 'dblock 0' >> $seqres.full The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/382 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/383 -->
# sources/test-tools/xfstests/tests/xfs/383

## Purpose
Populate a XFS filesystem and fuzz every symlink remote block field. Use xfs_scrub to fix the corruption. In this subset it exercises xfs_repair detection and correction of crafted metadata damage; xfs_scrub online checking or repair of populated/fuzzed filesystems; metadata fuzzing through common/fuzzy helper paths. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest dangerous_fuzzers scrub fuzzers_online_repair`. It imports common/preamble, common/filter, common/populate, common/fuzzy. Local helpers are no local shell helpers. Requirement and fix gates include `_require_scratch_xfs_fuzz_fields`. External tools and command surfaces visible in the source include `xfs_scrub`, `mount`, `stat`, `file`, `rm`. Key shell state is carried in `inum`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 20: `_require_scratch_xfs_fuzz_fields`; line 22: `echo "Format and populate"`; line 23: `_scratch_populate_cached nofill > $seqres.full 2>&1`; line 25: `echo "Find symlink remote block"`; line 26: `_scratch_mount`; line 28: `_scratch_unmount`; line 30: `echo "Fuzz symlink remote block"`; line 31: `_scratch_xfs_fuzz_metadata '' 'online' "inode ${inum}" 'dblock 0' >> $seqres.full`; line 32: `echo "Done fuzzing symlink remote block"`. metadata fuzzing target: _scratch_xfs_fuzz_metadata '' 'online' "inode ${inum}" 'dblock 0' >> $seqres.full The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/383 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/384 -->
# sources/test-tools/xfstests/tests/xfs/384

## Purpose
Populate a XFS filesystem and fuzz every inline directory inode field. Use xfs_repair to fix the corruption. In this subset it exercises xfs_repair detection and correction of crafted metadata damage; metadata fuzzing through common/fuzzy helper paths; directory metadata layout and traversal behavior. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest dangerous_fuzzers repair fuzzers_repair`. It imports common/preamble, common/filter, common/populate, common/fuzzy. Local helpers are no local shell helpers. Requirement and fix gates include `_require_scratch_xfs_fuzz_fields`. External tools and command surfaces visible in the source include `xfs_repair`, `mount`, `stat`, `file`, `rm`. Key shell state is carried in `inum`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 20: `_require_scratch_xfs_fuzz_fields`; line 22: `echo "Format and populate"`; line 23: `_scratch_populate_cached nofill > $seqres.full 2>&1`; line 25: `echo "Find inline-format dir inode"`; line 26: `_scratch_mount`; line 28: `_scratch_unmount`; line 30: `echo "Fuzz inline-format dir inode"`; line 31: `_scratch_xfs_fuzz_metadata '' 'offline'  "inode ${inum}" >> $seqres.full`; line 32: `echo "Done fuzzing inline-format dir inode"`. metadata fuzzing target: _scratch_xfs_fuzz_metadata '' 'offline'  "inode ${inum}" >> $seqres.full The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/384 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/385 -->
# sources/test-tools/xfstests/tests/xfs/385

## Purpose
Populate a XFS filesystem and fuzz every inline directory inode field. Use xfs_scrub to fix the corruption. In this subset it exercises xfs_repair detection and correction of crafted metadata damage; xfs_scrub online checking or repair of populated/fuzzed filesystems; metadata fuzzing through common/fuzzy helper paths; directory metadata layout and traversal behavior. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest dangerous_fuzzers scrub fuzzers_online_repair`. It imports common/preamble, common/filter, common/populate, common/fuzzy. Local helpers are no local shell helpers. Requirement and fix gates include `_require_scratch_xfs_fuzz_fields`. External tools and command surfaces visible in the source include `xfs_scrub`, `mount`, `stat`, `file`, `rm`. Key shell state is carried in `inum`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 20: `_require_scratch_xfs_fuzz_fields`; line 22: `echo "Format and populate"`; line 23: `_scratch_populate_cached nofill > $seqres.full 2>&1`; line 25: `echo "Find inline-format dir inode"`; line 26: `_scratch_mount`; line 28: `_scratch_unmount`; line 30: `echo "Fuzz inline-format dir inode"`; line 31: `_scratch_xfs_fuzz_metadata '' 'online'  "inode ${inum}" >> $seqres.full`; line 32: `echo "Done fuzzing inline-format dir inode"`. metadata fuzzing target: _scratch_xfs_fuzz_metadata '' 'online'  "inode ${inum}" >> $seqres.full The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/385 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/386 -->
# sources/test-tools/xfstests/tests/xfs/386

## Purpose
Populate a XFS filesystem and fuzz every block-format dir block field. Use xfs_repair to fix the corruption. In this subset it exercises xfs_repair detection and correction of crafted metadata damage; metadata fuzzing through common/fuzzy helper paths; directory metadata layout and traversal behavior. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest dangerous_fuzzers repair fuzzers_repair`. It imports common/preamble, common/filter, common/populate, common/fuzzy. Local helpers are no local shell helpers. Requirement and fix gates include `_require_scratch_xfs_fuzz_fields`. External tools and command surfaces visible in the source include `xfs_repair`, `mount`, `stat`, `file`, `rm`. Key shell state is carried in `inum`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 20: `_require_scratch_xfs_fuzz_fields`; line 22: `echo "Format and populate"`; line 23: `_scratch_populate_cached nofill > $seqres.full 2>&1`; line 25: `echo "Find data-format dir block"`; line 26: `_scratch_mount`; line 28: `_scratch_unmount`; line 30: `echo "Fuzz data-format dir block"`; line 31: `_scratch_xfs_fuzz_metadata '' 'offline'  "inode ${inum}" 'dblock 0' >> $seqres.full`; line 32: `echo "Done fuzzing data-format dir block"`. metadata fuzzing target: _scratch_xfs_fuzz_metadata '' 'offline'  "inode ${inum}" 'dblock 0' >> $seqres.full The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/386 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/387 -->
# sources/test-tools/xfstests/tests/xfs/387

## Purpose
Populate a XFS filesystem and fuzz every block-format dir block field. Use xfs_scrub to fix the corruption. In this subset it exercises xfs_repair detection and correction of crafted metadata damage; xfs_scrub online checking or repair of populated/fuzzed filesystems; metadata fuzzing through common/fuzzy helper paths; directory metadata layout and traversal behavior. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest dangerous_fuzzers scrub fuzzers_online_repair`. It imports common/preamble, common/filter, common/populate, common/fuzzy. Local helpers are no local shell helpers. Requirement and fix gates include `_require_scratch_xfs_fuzz_fields`. External tools and command surfaces visible in the source include `xfs_scrub`, `mount`, `stat`, `file`, `rm`. Key shell state is carried in `inum`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 20: `_require_scratch_xfs_fuzz_fields`; line 22: `echo "Format and populate"`; line 23: `_scratch_populate_cached nofill > $seqres.full 2>&1`; line 25: `echo "Find data-format dir block"`; line 26: `_scratch_mount`; line 28: `_scratch_unmount`; line 30: `echo "Fuzz data-format dir block"`; line 31: `_scratch_xfs_fuzz_metadata '' 'online'  "inode ${inum}" 'dblock 0' >> $seqres.full`; line 32: `echo "Done fuzzing data-format dir block"`. metadata fuzzing target: _scratch_xfs_fuzz_metadata '' 'online'  "inode ${inum}" 'dblock 0' >> $seqres.full The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/387 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/388 -->
# sources/test-tools/xfstests/tests/xfs/388

## Purpose
Populate a XFS filesystem and fuzz every data-format dir block field. Use xfs_repair to fix the corruption. In this subset it exercises xfs_repair detection and correction of crafted metadata damage; metadata fuzzing through common/fuzzy helper paths; directory metadata layout and traversal behavior. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest dangerous_fuzzers repair fuzzers_repair`. It imports common/preamble, common/filter, common/populate, common/fuzzy. Local helpers are no local shell helpers. Requirement and fix gates include `_require_scratch_xfs_fuzz_fields`. External tools and command surfaces visible in the source include `xfs_repair`, `mount`, `stat`, `file`, `rm`. Key shell state is carried in `inum`, `blk_sz`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 20: `_require_scratch_xfs_fuzz_fields`; line 22: `echo "Format and populate"`; line 23: `_scratch_populate_cached nofill > $seqres.full 2>&1`; line 25: `echo "Find data-format dir block"`; line 26: `_scratch_mount`; line 29: `_scratch_unmount`; line 31: `echo "Fuzz data-format dir block"`; line 32: `_scratch_xfs_fuzz_metadata '' 'offline'  "inode ${inum}" "dblock 0" >> $seqres.full`; line 33: `echo "Done fuzzing data-format dir block"`. metadata fuzzing target: _scratch_xfs_fuzz_metadata '' 'offline'  "inode ${inum}" "dblock 0" >> $seqres.full The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/388 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/389 -->
# sources/test-tools/xfstests/tests/xfs/389

## Purpose
Populate a XFS filesystem and fuzz every data-format dir block field. Use xfs_scrub to fix the corruption. In this subset it exercises xfs_repair detection and correction of crafted metadata damage; xfs_scrub online checking or repair of populated/fuzzed filesystems; metadata fuzzing through common/fuzzy helper paths; directory metadata layout and traversal behavior. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest dangerous_fuzzers scrub fuzzers_online_repair`. It imports common/preamble, common/filter, common/populate, common/fuzzy. Local helpers are no local shell helpers. Requirement and fix gates include `_require_scratch_xfs_fuzz_fields`. External tools and command surfaces visible in the source include `xfs_scrub`, `mount`, `stat`, `file`, `rm`. Key shell state is carried in `inum`, `blk_sz`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 20: `_require_scratch_xfs_fuzz_fields`; line 22: `echo "Format and populate"`; line 23: `_scratch_populate_cached nofill > $seqres.full 2>&1`; line 25: `echo "Find data-format dir block"`; line 26: `_scratch_mount`; line 29: `_scratch_unmount`; line 31: `echo "Fuzz data-format dir block"`; line 32: `_scratch_xfs_fuzz_metadata '' 'online'  "inode ${inum}" "dblock 0" >> $seqres.full`; line 33: `echo "Done fuzzing data-format dir block"`. metadata fuzzing target: _scratch_xfs_fuzz_metadata '' 'online'  "inode ${inum}" "dblock 0" >> $seqres.full The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/389 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/390 -->
# sources/test-tools/xfstests/tests/xfs/390

## Purpose
Populate a XFS filesystem and fuzz every leaf1-format dir block field. Use xfs_repair to fix the corruption. In this subset it exercises xfs_repair detection and correction of crafted metadata damage; metadata fuzzing through common/fuzzy helper paths; directory metadata layout and traversal behavior. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest dangerous_fuzzers repair fuzzers_repair`. It imports common/preamble, common/filter, common/populate, common/fuzzy. Local helpers are no local shell helpers. Requirement and fix gates include `_require_scratch_xfs_fuzz_fields`. External tools and command surfaces visible in the source include `xfs_repair`, `mount`, `stat`, `file`, `rm`. Key shell state is carried in `inum`, `blk_sz`, `leaf_offset`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 20: `_require_scratch_xfs_fuzz_fields`; line 22: `echo "Format and populate"`; line 23: `_scratch_populate_cached nofill > $seqres.full 2>&1`; line 25: `echo "Find leaf1-format dir block"`; line 26: `_scratch_mount`; line 29: `_scratch_unmount`; line 32: `echo "Fuzz leaf1-format dir block"`; line 33: `_scratch_xfs_fuzz_metadata '' 'offline'  "inode ${inum}" "dblock ${leaf_offset}" >> $seqres.full`; line 34: `echo "Done fuzzing leaf1-format dir block"`. metadata fuzzing target: _scratch_xfs_fuzz_metadata '' 'offline'  "inode ${inum}" "dblock ${leaf_offset}" >> $seqres.full The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/390 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/391 -->
# sources/test-tools/xfstests/tests/xfs/391

## Purpose
Populate a XFS filesystem and fuzz every leaf1-format dir block field. Use xfs_scrub to fix the corruption. In this subset it exercises xfs_repair detection and correction of crafted metadata damage; xfs_scrub online checking or repair of populated/fuzzed filesystems; metadata fuzzing through common/fuzzy helper paths; directory metadata layout and traversal behavior. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest dangerous_fuzzers scrub fuzzers_online_repair`. It imports common/preamble, common/filter, common/populate, common/fuzzy. Local helpers are no local shell helpers. Requirement and fix gates include `_require_scratch_xfs_fuzz_fields`. External tools and command surfaces visible in the source include `xfs_scrub`, `mount`, `stat`, `file`, `rm`. Key shell state is carried in `inum`, `blk_sz`, `leaf_offset`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 20: `_require_scratch_xfs_fuzz_fields`; line 22: `echo "Format and populate"`; line 23: `_scratch_populate_cached nofill > $seqres.full 2>&1`; line 25: `echo "Find leaf1-format dir block"`; line 26: `_scratch_mount`; line 29: `_scratch_unmount`; line 32: `echo "Fuzz leaf1-format dir block"`; line 33: `_scratch_xfs_fuzz_metadata '' 'online'  "inode ${inum}" "dblock ${leaf_offset}" >> $seqres.full`; line 34: `echo "Done fuzzing leaf1-format dir block"`. metadata fuzzing target: _scratch_xfs_fuzz_metadata '' 'online'  "inode ${inum}" "dblock ${leaf_offset}" >> $seqres.full The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/391 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/392 -->
# sources/test-tools/xfstests/tests/xfs/392

## Purpose
Populate a XFS filesystem and fuzz every leafn-format dir block field. Use xfs_repair to fix the corruption. In this subset it exercises xfs_repair detection and correction of crafted metadata damage; metadata fuzzing through common/fuzzy helper paths; directory metadata layout and traversal behavior. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest dangerous_fuzzers repair fuzzers_repair`. It imports common/preamble, common/filter, common/populate, common/fuzzy. Local helpers are no local shell helpers. Requirement and fix gates include `_require_scratch_xfs_fuzz_fields`. External tools and command surfaces visible in the source include `xfs_repair`, `mount`, `stat`, `file`, `rm`. Key shell state is carried in `inum`, `blk_sz`, `leaf_offset`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 20: `_require_scratch_xfs_fuzz_fields`; line 22: `echo "Format and populate"`; line 23: `_scratch_populate_cached nofill > $seqres.full 2>&1`; line 25: `echo "Find leafn-format dir block"`; line 26: `_scratch_mount`; line 29: `_scratch_unmount`; line 32: `echo "Fuzz leafn-format dir block"`; line 33: `_scratch_xfs_fuzz_metadata '' 'offline'  "inode ${inum}" "dblock ${leaf_offset}" >> $seqres.full`; line 34: `echo "Done fuzzing leafn-format dir block"`. metadata fuzzing target: _scratch_xfs_fuzz_metadata '' 'offline'  "inode ${inum}" "dblock ${leaf_offset}" >> $seqres.full The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/392 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/393 -->
# sources/test-tools/xfstests/tests/xfs/393

## Purpose
Populate a XFS filesystem and fuzz every leafn-format dir block field. Use xfs_scrub to fix the corruption. In this subset it exercises xfs_repair detection and correction of crafted metadata damage; xfs_scrub online checking or repair of populated/fuzzed filesystems; metadata fuzzing through common/fuzzy helper paths; directory metadata layout and traversal behavior. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest dangerous_fuzzers scrub fuzzers_online_repair`. It imports common/preamble, common/filter, common/populate, common/fuzzy. Local helpers are no local shell helpers. Requirement and fix gates include `_require_scratch_xfs_fuzz_fields`. External tools and command surfaces visible in the source include `xfs_scrub`, `mount`, `stat`, `file`, `rm`. Key shell state is carried in `inum`, `blk_sz`, `leaf_offset`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 20: `_require_scratch_xfs_fuzz_fields`; line 22: `echo "Format and populate"`; line 23: `_scratch_populate_cached nofill > $seqres.full 2>&1`; line 25: `echo "Find leafn-format dir block"`; line 26: `_scratch_mount`; line 29: `_scratch_unmount`; line 32: `echo "Fuzz leafn-format dir block"`; line 33: `_scratch_xfs_fuzz_metadata '' 'online'  "inode ${inum}" "dblock ${leaf_offset}" >> $seqres.full`; line 34: `echo "Done fuzzing leafn-format dir block"`. metadata fuzzing target: _scratch_xfs_fuzz_metadata '' 'online'  "inode ${inum}" "dblock ${leaf_offset}" >> $seqres.full The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/393 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/394 -->
# sources/test-tools/xfstests/tests/xfs/394

## Purpose
Populate a XFS filesystem and fuzz every node-format dir block field. Use xfs_repair to fix the corruption. In this subset it exercises xfs_repair detection and correction of crafted metadata damage; metadata fuzzing through common/fuzzy helper paths; directory metadata layout and traversal behavior. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest dangerous_fuzzers repair fuzzers_repair`. It imports common/preamble, common/filter, common/populate, common/fuzzy. Local helpers are no local shell helpers. Requirement and fix gates include `_require_scratch_xfs_fuzz_fields`. External tools and command surfaces visible in the source include `xfs_repair`, `mount`, `stat`, `file`, `rm`. Key shell state is carried in `inum`, `blk_sz`, `leaf_offset`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 20: `_require_scratch_xfs_fuzz_fields`; line 22: `echo "Format and populate"`; line 23: `_scratch_populate_cached nofill > $seqres.full 2>&1`; line 25: `echo "Find node-format dir block"`; line 26: `_scratch_mount`; line 29: `_scratch_unmount`; line 32: `echo "Fuzz node-format dir block"`; line 33: `_scratch_xfs_fuzz_metadata '' 'offline'  "inode ${inum}" "dblock ${leaf_offset}" >> $seqres.full`; line 34: `echo "Done fuzzing node-format dir block"`. metadata fuzzing target: _scratch_xfs_fuzz_metadata '' 'offline'  "inode ${inum}" "dblock ${leaf_offset}" >> $seqres.full The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/394 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/395 -->
# sources/test-tools/xfstests/tests/xfs/395

## Purpose
Populate a XFS filesystem and fuzz every node-format dir block field. Use xfs_scrub to fix the corruption. In this subset it exercises xfs_repair detection and correction of crafted metadata damage; xfs_scrub online checking or repair of populated/fuzzed filesystems; metadata fuzzing through common/fuzzy helper paths; directory metadata layout and traversal behavior. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest dangerous_fuzzers scrub fuzzers_online_repair`. It imports common/preamble, common/filter, common/populate, common/fuzzy. Local helpers are no local shell helpers. Requirement and fix gates include `_require_scratch_xfs_fuzz_fields`. External tools and command surfaces visible in the source include `xfs_scrub`, `mount`, `stat`, `file`, `rm`. Key shell state is carried in `inum`, `blk_sz`, `leaf_offset`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 20: `_require_scratch_xfs_fuzz_fields`; line 22: `echo "Format and populate"`; line 23: `_scratch_populate_cached nofill > $seqres.full 2>&1`; line 25: `echo "Find node-format dir block"`; line 26: `_scratch_mount`; line 29: `_scratch_unmount`; line 32: `echo "Fuzz node-format dir block"`; line 33: `_scratch_xfs_fuzz_metadata '' 'online'  "inode ${inum}" "dblock ${leaf_offset}" >> $seqres.full`; line 34: `echo "Done fuzzing node-format dir block"`. metadata fuzzing target: _scratch_xfs_fuzz_metadata '' 'online'  "inode ${inum}" "dblock ${leaf_offset}" >> $seqres.full The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/395 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/396 -->
# sources/test-tools/xfstests/tests/xfs/396

## Purpose
Populate a XFS filesystem and fuzz every freeindex-format dir block field. Use xfs_repair to fix the corruption. In this subset it exercises xfs_repair detection and correction of crafted metadata damage; metadata fuzzing through common/fuzzy helper paths; directory metadata layout and traversal behavior. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest dangerous_fuzzers repair fuzzers_repair`. It imports common/preamble, common/filter, common/populate, common/fuzzy. Local helpers are no local shell helpers. Requirement and fix gates include `_require_scratch_xfs_fuzz_fields`. External tools and command surfaces visible in the source include `xfs_repair`, `mount`, `stat`, `file`, `rm`. Key shell state is carried in `inum`, `blk_sz`, `leaf_offset`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 20: `_require_scratch_xfs_fuzz_fields`; line 22: `echo "Format and populate"`; line 23: `_scratch_populate_cached nofill > $seqres.full 2>&1`; line 25: `echo "Find freeindex-format dir block"`; line 26: `_scratch_mount`; line 29: `_scratch_unmount`; line 32: `echo "Fuzz freeindex-format dir block"`; line 33: `_scratch_xfs_fuzz_metadata '' 'offline'  "inode ${inum}" "dblock ${leaf_offset}" >> $seqres.full`; line 34: `echo "Done fuzzing freeindex-format dir block"`. metadata fuzzing target: _scratch_xfs_fuzz_metadata '' 'offline'  "inode ${inum}" "dblock ${leaf_offset}" >> $seqres.full The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/396 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/397 -->
# sources/test-tools/xfstests/tests/xfs/397

## Purpose
Populate a XFS filesystem and fuzz every freeindex-format dir block field. Use xfs_scrub to fix the corruption. In this subset it exercises xfs_repair detection and correction of crafted metadata damage; xfs_scrub online checking or repair of populated/fuzzed filesystems; metadata fuzzing through common/fuzzy helper paths; directory metadata layout and traversal behavior. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest dangerous_fuzzers scrub fuzzers_online_repair`. It imports common/preamble, common/filter, common/populate, common/fuzzy. Local helpers are no local shell helpers. Requirement and fix gates include `_require_scratch_xfs_fuzz_fields`. External tools and command surfaces visible in the source include `xfs_scrub`, `mount`, `stat`, `file`, `rm`. Key shell state is carried in `inum`, `blk_sz`, `leaf_offset`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 20: `_require_scratch_xfs_fuzz_fields`; line 22: `echo "Format and populate"`; line 23: `_scratch_populate_cached nofill > $seqres.full 2>&1`; line 25: `echo "Find freeindex-format dir block"`; line 26: `_scratch_mount`; line 29: `_scratch_unmount`; line 32: `echo "Fuzz freeindex-format dir block"`; line 33: `_scratch_xfs_fuzz_metadata '' 'online'  "inode ${inum}" "dblock ${leaf_offset}" >> $seqres.full`; line 34: `echo "Done fuzzing freeindex-format dir block"`. metadata fuzzing target: _scratch_xfs_fuzz_metadata '' 'online'  "inode ${inum}" "dblock ${leaf_offset}" >> $seqres.full The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/397 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/398 -->
# sources/test-tools/xfstests/tests/xfs/398

## Purpose
Populate a XFS filesystem and fuzz every inline attr inode field. Use xfs_repair to fix the corruption. In this subset it exercises xfs_repair detection and correction of crafted metadata damage; metadata fuzzing through common/fuzzy helper paths; extended attribute metadata behavior. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest dangerous_fuzzers repair fuzzers_repair`. It imports common/preamble, common/filter, common/populate, common/fuzzy. Local helpers are no local shell helpers. Requirement and fix gates include `_require_scratch_xfs_fuzz_fields`. External tools and command surfaces visible in the source include `xfs_repair`, `mount`, `stat`, `file`, `rm`. Key shell state is carried in `inum`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 20: `_require_scratch_xfs_fuzz_fields`; line 22: `echo "Format and populate"`; line 23: `_scratch_populate_cached nofill > $seqres.full 2>&1`; line 25: `echo "Find inline-format attr inode"`; line 26: `_scratch_mount`; line 28: `_scratch_unmount`; line 30: `echo "Fuzz inline-format attr inode"`; line 31: `_scratch_xfs_fuzz_metadata '' 'offline'  "inode ${inum}" >> $seqres.full`; line 32: `echo "Done fuzzing inline-format attr inode"`. metadata fuzzing target: _scratch_xfs_fuzz_metadata '' 'offline'  "inode ${inum}" >> $seqres.full The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/398 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/399 -->
# sources/test-tools/xfstests/tests/xfs/399

## Purpose
Populate a XFS filesystem and fuzz every inline attr inode field. Use xfs_scrub to fix the corruption. In this subset it exercises xfs_repair detection and correction of crafted metadata damage; xfs_scrub online checking or repair of populated/fuzzed filesystems; metadata fuzzing through common/fuzzy helper paths; extended attribute metadata behavior. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest dangerous_fuzzers scrub fuzzers_online_repair`. It imports common/preamble, common/filter, common/populate, common/fuzzy. Local helpers are no local shell helpers. Requirement and fix gates include `_require_scratch_xfs_fuzz_fields`. External tools and command surfaces visible in the source include `xfs_scrub`, `mount`, `stat`, `file`, `rm`. Key shell state is carried in `inum`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 20: `_require_scratch_xfs_fuzz_fields`; line 22: `echo "Format and populate"`; line 23: `_scratch_populate_cached nofill > $seqres.full 2>&1`; line 25: `echo "Find inline-format attr inode"`; line 26: `_scratch_mount`; line 28: `_scratch_unmount`; line 30: `echo "Fuzz inline-format attr inode"`; line 31: `_scratch_xfs_fuzz_metadata '' 'online'  "inode ${inum}" >> $seqres.full`; line 32: `echo "Done fuzzing inline-format attr inode"`. metadata fuzzing target: _scratch_xfs_fuzz_metadata '' 'online'  "inode ${inum}" >> $seqres.full The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/399 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/400 -->
# sources/test-tools/xfstests/tests/xfs/400

## Purpose
Populate a XFS filesystem and fuzz every leaf-format attr block field. Use xfs_repair to fix the corruption. In this subset it exercises xfs_repair detection and correction of crafted metadata damage; metadata fuzzing through common/fuzzy helper paths; extended attribute metadata behavior. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest dangerous_fuzzers repair fuzzers_repair`. It imports common/preamble, common/filter, common/populate, common/fuzzy. Local helpers are no local shell helpers. Requirement and fix gates include `_require_scratch_xfs_fuzz_fields`. External tools and command surfaces visible in the source include `xfs_repair`, `mount`, `stat`, `file`, `rm`. Key shell state is carried in `inum`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 20: `_require_scratch_xfs_fuzz_fields`; line 22: `echo "Format and populate"`; line 23: `_scratch_populate_cached nofill > $seqres.full 2>&1`; line 25: `echo "Find leaf-format attr block"`; line 26: `_scratch_mount`; line 28: `_scratch_unmount`; line 30: `echo "Fuzz leaf-format attr block"`; line 31: `_scratch_xfs_fuzz_metadata '' 'offline'  "inode ${inum}" 'ablock 0' >> $seqres.full`; line 32: `echo "Done fuzzing leaf-format attr block"`. metadata fuzzing target: _scratch_xfs_fuzz_metadata '' 'offline'  "inode ${inum}" 'ablock 0' >> $seqres.full The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/400 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/401 -->
# sources/test-tools/xfstests/tests/xfs/401

## Purpose
Populate a XFS filesystem and fuzz every leaf-format attr block field. Use xfs_scrub to fix the corruption. In this subset it exercises xfs_repair detection and correction of crafted metadata damage; xfs_scrub online checking or repair of populated/fuzzed filesystems; metadata fuzzing through common/fuzzy helper paths; extended attribute metadata behavior. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest dangerous_fuzzers scrub fuzzers_online_repair`. It imports common/preamble, common/filter, common/populate, common/fuzzy. Local helpers are no local shell helpers. Requirement and fix gates include `_require_scratch_xfs_fuzz_fields`. External tools and command surfaces visible in the source include `xfs_scrub`, `mount`, `stat`, `file`, `rm`. Key shell state is carried in `inum`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 20: `_require_scratch_xfs_fuzz_fields`; line 22: `echo "Format and populate"`; line 23: `_scratch_populate_cached nofill > $seqres.full 2>&1`; line 25: `echo "Find leaf-format attr block"`; line 26: `_scratch_mount`; line 28: `_scratch_unmount`; line 30: `echo "Fuzz leaf-format attr block"`; line 31: `_scratch_xfs_fuzz_metadata '' 'online'  "inode ${inum}" 'ablock 0' >> $seqres.full`; line 32: `echo "Done fuzzing leaf-format attr block"`. metadata fuzzing target: _scratch_xfs_fuzz_metadata '' 'online'  "inode ${inum}" 'ablock 0' >> $seqres.full The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/401 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/402 -->
# sources/test-tools/xfstests/tests/xfs/402

## Purpose
Populate a XFS filesystem and fuzz every node-format attr block field. Use xfs_repair to fix the corruption. In this subset it exercises xfs_repair detection and correction of crafted metadata damage; metadata fuzzing through common/fuzzy helper paths; extended attribute metadata behavior. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest dangerous_fuzzers repair fuzzers_repair`. It imports common/preamble, common/filter, common/populate, common/fuzzy. Local helpers are no local shell helpers. Requirement and fix gates include `_require_scratch_xfs_fuzz_fields`. External tools and command surfaces visible in the source include `xfs_repair`, `mount`, `stat`, `file`, `rm`. Key shell state is carried in `inum`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 20: `_require_scratch_xfs_fuzz_fields`; line 22: `echo "Format and populate"`; line 23: `_scratch_populate_cached nofill > $seqres.full 2>&1`; line 25: `echo "Find node-format attr block"`; line 26: `_scratch_mount`; line 28: `_scratch_unmount`; line 30: `echo "Fuzz node-format attr block"`; line 31: `_scratch_xfs_fuzz_metadata '' 'offline'  "inode ${inum}" "ablock 0" >> $seqres.full`; line 32: `echo "Done fuzzing node-format attr block"`. metadata fuzzing target: _scratch_xfs_fuzz_metadata '' 'offline'  "inode ${inum}" "ablock 0" >> $seqres.full The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/402 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/403 -->
# sources/test-tools/xfstests/tests/xfs/403

## Purpose
Populate a XFS filesystem and fuzz every node-format attr block field. Use xfs_scrub to fix the corruption. In this subset it exercises xfs_repair detection and correction of crafted metadata damage; xfs_scrub online checking or repair of populated/fuzzed filesystems; metadata fuzzing through common/fuzzy helper paths; extended attribute metadata behavior. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest dangerous_fuzzers scrub fuzzers_online_repair`. It imports common/preamble, common/filter, common/populate, common/fuzzy. Local helpers are no local shell helpers. Requirement and fix gates include `_require_scratch_xfs_fuzz_fields`. External tools and command surfaces visible in the source include `xfs_scrub`, `mount`, `stat`, `file`, `rm`. Key shell state is carried in `inum`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 20: `_require_scratch_xfs_fuzz_fields`; line 22: `echo "Format and populate"`; line 23: `_scratch_populate_cached nofill > $seqres.full 2>&1`; line 25: `echo "Find node-format attr block"`; line 26: `_scratch_mount`; line 28: `_scratch_unmount`; line 30: `echo "Fuzz node-format attr block"`; line 31: `_scratch_xfs_fuzz_metadata '' 'online'  "inode ${inum}" "ablock 0" >> $seqres.full`; line 32: `echo "Done fuzzing node-format attr block"`. metadata fuzzing target: _scratch_xfs_fuzz_metadata '' 'online'  "inode ${inum}" "ablock 0" >> $seqres.full The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/403 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/404 -->
# sources/test-tools/xfstests/tests/xfs/404

## Purpose
Populate a XFS filesystem and fuzz every external attr block field. Use xfs_repair to fix the corruption. In this subset it exercises xfs_repair detection and correction of crafted metadata damage; metadata fuzzing through common/fuzzy helper paths; extended attribute metadata behavior. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest dangerous_fuzzers repair fuzzers_repair`. It imports common/preamble, common/filter, common/populate, common/fuzzy. Local helpers are no local shell helpers. Requirement and fix gates include `_require_scratch_xfs_fuzz_fields`. External tools and command surfaces visible in the source include `xfs_repair`, `mount`, `stat`, `file`, `rm`. Key shell state is carried in `inum`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 20: `_require_scratch_xfs_fuzz_fields`; line 22: `echo "Format and populate"`; line 23: `_scratch_populate_cached nofill > $seqres.full 2>&1`; line 25: `echo "Find external attr block"`; line 26: `_scratch_mount`; line 28: `_scratch_unmount`; line 30: `echo "Fuzz external attr block"`; line 31: `_scratch_xfs_fuzz_metadata '' 'offline'  "inode ${inum}" "ablock 1" >> $seqres.full`; line 32: `echo "Done fuzzing external attr block"`. metadata fuzzing target: _scratch_xfs_fuzz_metadata '' 'offline'  "inode ${inum}" "ablock 1" >> $seqres.full The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/404 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/405 -->
# sources/test-tools/xfstests/tests/xfs/405

## Purpose
Populate a XFS filesystem and fuzz every external attr block field. Use xfs_scrub to fix the corruption. In this subset it exercises xfs_repair detection and correction of crafted metadata damage; xfs_scrub online checking or repair of populated/fuzzed filesystems; metadata fuzzing through common/fuzzy helper paths; extended attribute metadata behavior. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest dangerous_fuzzers scrub fuzzers_online_repair`. It imports common/preamble, common/filter, common/populate, common/fuzzy. Local helpers are no local shell helpers. Requirement and fix gates include `_require_scratch_xfs_fuzz_fields`. External tools and command surfaces visible in the source include `xfs_scrub`, `mount`, `stat`, `file`, `rm`. Key shell state is carried in `inum`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 20: `_require_scratch_xfs_fuzz_fields`; line 22: `echo "Format and populate"`; line 23: `_scratch_populate_cached nofill > $seqres.full 2>&1`; line 25: `echo "Find external attr block"`; line 26: `_scratch_mount`; line 28: `_scratch_unmount`; line 30: `echo "Fuzz external attr block"`; line 31: `_scratch_xfs_fuzz_metadata '' 'online'  "inode ${inum}" "ablock 1" >> $seqres.full`; line 32: `echo "Done fuzzing external attr block"`. metadata fuzzing target: _scratch_xfs_fuzz_metadata '' 'online'  "inode ${inum}" "ablock 1" >> $seqres.full The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/405 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/406 -->
# sources/test-tools/xfstests/tests/xfs/406

## Purpose
Populate a XFS filesystem and fuzz every rtrmapbt record field. Use xfs_repair to fix the corruption. In this subset it exercises reverse mapping metadata and owner-accounting validation; realtime device allocation and realtime reverse-map behavior; xfs_repair detection and correction of crafted metadata damage; metadata fuzzing through common/fuzzy helper paths. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest dangerous_fuzzers repair fuzzers_repair realtime`. It imports common/preamble, common/filter, common/populate, common/fuzzy. Local helpers are no local shell helpers. Requirement and fix gates include `_require_realtime`; `_require_xfs_scratch_rmapbt`; `_require_scratch_xfs_fuzz_fields`. External tools and command surfaces visible in the source include `xfs_repair`, `dd`, `stat`, `file`, `rm`. Key shell state is carried in `path`, `inode_ver`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 21: `_require_xfs_scratch_rmapbt`; line 22: `_require_scratch_xfs_fuzz_fields`; line 24: `echo "Format and populate"`; line 25: `_scratch_populate_cached nofill > $seqres.full 2>&1`; line 27: `path="$(_scratch_xfs_find_rgbtree_height 'rmap' 2)" || \`; line 29: `inode_ver=$(_scratch_xfs_get_metadata_field "core.version" "path -m $path")`; line 31: `echo "Fuzz rtrmapbt recs"`; line 32: `_scratch_xfs_fuzz_metadata '' 'offline' "path -m $path" "addr u${inode_ver}.rtrmapbt.ptrs[1]" >> $seqres.full`; line 33: `echo "Done fuzzing rtrmapbt recs"`. metadata fuzzing target: _scratch_xfs_fuzz_metadata '' 'offline' "path -m $path" "addr u${inode_ver}.rtrmapbt.ptrs[1]" >> $seqres.full The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate; realtime device geometry and internal/external rt-device handling affect expected output. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/406 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/407 -->
# sources/test-tools/xfstests/tests/xfs/407

## Purpose
Populate a XFS filesystem and fuzz every rtrmapbt record field. Use xfs_scrub to fix the corruption. In this subset it exercises reverse mapping metadata and owner-accounting validation; realtime device allocation and realtime reverse-map behavior; xfs_repair detection and correction of crafted metadata damage; xfs_scrub online checking or repair of populated/fuzzed filesystems. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest dangerous_fuzzers scrub fuzzers_online_repair realtime`. It imports common/preamble, common/filter, common/populate, common/fuzzy. Local helpers are no local shell helpers. Requirement and fix gates include `_require_realtime`; `_require_xfs_scratch_rmapbt`; `_require_scratch_xfs_fuzz_fields`. External tools and command surfaces visible in the source include `xfs_scrub`, `dd`, `stat`, `file`, `rm`. Key shell state is carried in `path`, `inode_ver`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 21: `_require_xfs_scratch_rmapbt`; line 22: `_require_scratch_xfs_fuzz_fields`; line 24: `echo "Format and populate"`; line 25: `_scratch_populate_cached nofill > $seqres.full 2>&1`; line 27: `path="$(_scratch_xfs_find_rgbtree_height 'rmap' 2)" || \`; line 29: `inode_ver=$(_scratch_xfs_get_metadata_field "core.version" "path -m $path")`; line 31: `echo "Fuzz rtrmapbt recs"`; line 32: `_scratch_xfs_fuzz_metadata '' 'online' "path -m $path" "addr u${inode_ver}.rtrmapbt.ptrs[1]" >> $seqres.full`; line 33: `echo "Done fuzzing rtrmapbt recs"`. metadata fuzzing target: _scratch_xfs_fuzz_metadata '' 'online' "path -m $path" "addr u${inode_ver}.rtrmapbt.ptrs[1]" >> $seqres.full The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate; realtime device geometry and internal/external rt-device handling affect expected output. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/407 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/408 -->
# sources/test-tools/xfstests/tests/xfs/408

## Purpose
Populate a XFS filesystem and fuzz every rtrmapbt key/pointer field. Use xfs_repair to fix the corruption. In this subset it exercises reverse mapping metadata and owner-accounting validation; realtime device allocation and realtime reverse-map behavior; xfs_repair detection and correction of crafted metadata damage; metadata fuzzing through common/fuzzy helper paths. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest dangerous_fuzzers repair fuzzers_repair realtime`. It imports common/preamble, common/filter, common/populate, common/fuzzy. Local helpers are no local shell helpers. Requirement and fix gates include `_require_realtime`; `_require_xfs_scratch_rmapbt`; `_require_scratch_xfs_fuzz_fields`. External tools and command surfaces visible in the source include `xfs_repair`, `stat`, `file`, `rm`. Key shell state is carried in `path`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 21: `_require_xfs_scratch_rmapbt`; line 22: `_require_scratch_xfs_fuzz_fields`; line 24: `echo "Format and populate"`; line 25: `_scratch_populate_cached nofill > $seqres.full 2>&1`; line 27: `path="$(_scratch_xfs_find_rgbtree_height 'rmap' 2)" || \`; line 30: `echo "Fuzz rtrmapbt keyptrs"`; line 31: `_scratch_xfs_fuzz_metadata '(rtrmapbt)' 'offline' "path -m $path" >> $seqres.full`; line 32: `echo "Done fuzzing rtrmapbt keyptrs"`. metadata fuzzing target: _scratch_xfs_fuzz_metadata '(rtrmapbt)' 'offline' "path -m $path" >> $seqres.full The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate; realtime device geometry and internal/external rt-device handling affect expected output. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/408 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/409 -->
# sources/test-tools/xfstests/tests/xfs/409

## Purpose
Populate a XFS filesystem and fuzz every rtrmapbt key/pointer field. Use xfs_scrub to fix the corruption. In this subset it exercises reverse mapping metadata and owner-accounting validation; realtime device allocation and realtime reverse-map behavior; xfs_repair detection and correction of crafted metadata damage; xfs_scrub online checking or repair of populated/fuzzed filesystems. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest dangerous_fuzzers scrub fuzzers_online_repair realtime`. It imports common/preamble, common/filter, common/populate, common/fuzzy. Local helpers are no local shell helpers. Requirement and fix gates include `_require_realtime`; `_require_xfs_scratch_rmapbt`; `_require_scratch_xfs_fuzz_fields`. External tools and command surfaces visible in the source include `xfs_scrub`, `stat`, `file`, `rm`. Key shell state is carried in `path`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 21: `_require_xfs_scratch_rmapbt`; line 22: `_require_scratch_xfs_fuzz_fields`; line 24: `echo "Format and populate"`; line 25: `_scratch_populate_cached nofill > $seqres.full 2>&1`; line 27: `path="$(_scratch_xfs_find_rgbtree_height 'rmap' 2)" || \`; line 30: `echo "Fuzz rtrmapbt keyptrs"`; line 31: `_scratch_xfs_fuzz_metadata '(rtrmapbt)' 'online' "path -m $path" >> $seqres.full`; line 32: `echo "Done fuzzing rtrmapbt keyptrs"`. metadata fuzzing target: _scratch_xfs_fuzz_metadata '(rtrmapbt)' 'online' "path -m $path" >> $seqres.full The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate; realtime device geometry and internal/external rt-device handling affect expected output. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/409 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/410 -->
# sources/test-tools/xfstests/tests/xfs/410

## Purpose
Populate a XFS filesystem and fuzz every refcountbt field. Use xfs_repair to fix the corruption. In this subset it exercises xfs_repair detection and correction of crafted metadata damage; metadata fuzzing through common/fuzzy helper paths. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest dangerous_fuzzers repair fuzzers_repair`. It imports common/preamble, common/filter, common/populate, common/fuzzy, common/reflink. Local helpers are no local shell helpers. Requirement and fix gates include `_require_scratch_reflink`; `_require_scratch_xfs_fuzz_fields`. External tools and command surfaces visible in the source include `xfs_repair`, `dd`, `stat`, `file`, `rm`. Key shell state is carried in `path`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 22: `_require_scratch_xfs_fuzz_fields`; line 24: `echo "Format and populate"`; line 25: `_scratch_populate_cached nofill > $seqres.full 2>&1`; line 27: `path="$(_scratch_xfs_find_agbtree_height 'refcnt' 2)" || \`; line 30: `echo "Fuzz refcountbt"`; line 31: `_scratch_xfs_fuzz_metadata '' 'offline'  "$path" 'addr refcntroot' 'addr ptrs[1]' >> $seqres.full`; line 32: `echo "Done fuzzing refcountbt"`. metadata fuzzing target: _scratch_xfs_fuzz_metadata '' 'offline'  "$path" 'addr refcntroot' 'addr ptrs[1]' >> $seqres.full creates shared extents and CoW/refcount state The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate; shared extent and CoW accounting depends on reflink/refcount support. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/410 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/411 -->
# sources/test-tools/xfstests/tests/xfs/411

## Purpose
Populate a XFS filesystem and fuzz every refcountbt field. Use xfs_scrub to fix the corruption. In this subset it exercises xfs_repair detection and correction of crafted metadata damage; xfs_scrub online checking or repair of populated/fuzzed filesystems; metadata fuzzing through common/fuzzy helper paths. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest dangerous_fuzzers scrub fuzzers_online_repair`. It imports common/preamble, common/filter, common/populate, common/fuzzy, common/reflink. Local helpers are no local shell helpers. Requirement and fix gates include `_require_scratch_reflink`; `_require_scratch_xfs_fuzz_fields`. External tools and command surfaces visible in the source include `xfs_scrub`, `dd`, `stat`, `file`, `rm`. Key shell state is carried in `path`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 22: `_require_scratch_xfs_fuzz_fields`; line 24: `echo "Format and populate"`; line 25: `_scratch_populate_cached nofill > $seqres.full 2>&1`; line 27: `path="$(_scratch_xfs_find_agbtree_height 'refcnt' 2)" || \`; line 30: `echo "Fuzz refcountbt"`; line 31: `_scratch_xfs_fuzz_metadata '' 'online'  "$path" 'addr refcntroot' 'addr ptrs[1]' >> $seqres.full`; line 32: `echo "Done fuzzing refcountbt"`. metadata fuzzing target: _scratch_xfs_fuzz_metadata '' 'online'  "$path" 'addr refcntroot' 'addr ptrs[1]' >> $seqres.full creates shared extents and CoW/refcount state The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate; shared extent and CoW accounting depends on reflink/refcount support. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/411 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/412 -->
# sources/test-tools/xfstests/tests/xfs/412

## Purpose
Populate a XFS filesystem and fuzz every btree-format attr inode field. Use xfs_repair to fix the corruption. In this subset it exercises xfs_repair detection and correction of crafted metadata damage; metadata fuzzing through common/fuzzy helper paths; extended attribute metadata behavior. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest dangerous_fuzzers repair fuzzers_repair`. It imports common/preamble, common/filter, common/populate, common/fuzzy. Local helpers are no local shell helpers. Requirement and fix gates include `_require_scratch_xfs_fuzz_fields`. External tools and command surfaces visible in the source include `xfs_repair`, `mount`, `stat`, `file`, `rm`. Key shell state is carried in `inum`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 20: `_require_scratch_xfs_fuzz_fields`; line 22: `echo "Format and populate"`; line 23: `_scratch_populate_cached nofill > $seqres.full 2>&1`; line 25: `echo "Find btree-format attr inode"`; line 26: `_scratch_mount`; line 28: `_scratch_unmount`; line 30: `echo "Fuzz inode"`; line 31: `_scratch_xfs_fuzz_metadata '' 'offline'  "inode ${inum}" >> $seqres.full`; line 32: `echo "Done fuzzing inode"`. metadata fuzzing target: _scratch_xfs_fuzz_metadata '' 'offline'  "inode ${inum}" >> $seqres.full The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/412 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/413 -->
# sources/test-tools/xfstests/tests/xfs/413

## Purpose
Populate a XFS filesystem and fuzz every btree-format attr inode field. Use xfs_scrub to fix the corruption. In this subset it exercises xfs_repair detection and correction of crafted metadata damage; xfs_scrub online checking or repair of populated/fuzzed filesystems; metadata fuzzing through common/fuzzy helper paths; extended attribute metadata behavior. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest dangerous_fuzzers scrub fuzzers_online_repair`. It imports common/preamble, common/filter, common/populate, common/fuzzy. Local helpers are no local shell helpers. Requirement and fix gates include `_require_scratch_xfs_fuzz_fields`. External tools and command surfaces visible in the source include `xfs_scrub`, `mount`, `stat`, `file`, `rm`. Key shell state is carried in `inum`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 20: `_require_scratch_xfs_fuzz_fields`; line 22: `echo "Format and populate"`; line 23: `_scratch_populate_cached nofill > $seqres.full 2>&1`; line 25: `echo "Find btree-format attr inode"`; line 26: `_scratch_mount`; line 28: `_scratch_unmount`; line 30: `echo "Fuzz inode"`; line 31: `_scratch_xfs_fuzz_metadata '' 'online'  "inode ${inum}" >> $seqres.full`; line 32: `echo "Done fuzzing inode"`. metadata fuzzing target: _scratch_xfs_fuzz_metadata '' 'online'  "inode ${inum}" >> $seqres.full The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/413 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/414 -->
# sources/test-tools/xfstests/tests/xfs/414

## Purpose
Populate a XFS filesystem and fuzz every blockdev inode field. Use xfs_repair to fix the corruption. In this subset it exercises xfs_repair detection and correction of crafted metadata damage; metadata fuzzing through common/fuzzy helper paths. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest dangerous_fuzzers repair fuzzers_repair`. It imports common/preamble, common/filter, common/populate, common/fuzzy. Local helpers are no local shell helpers. Requirement and fix gates include `_require_scratch_xfs_fuzz_fields`. External tools and command surfaces visible in the source include `xfs_repair`, `mount`, `stat`, `file`, `rm`, `blockdev`. Key shell state is carried in `inum`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 20: `_require_scratch_xfs_fuzz_fields`; line 22: `echo "Format and populate"`; line 23: `_scratch_populate_cached nofill > $seqres.full 2>&1`; line 25: `echo "Find blockdev inode"`; line 26: `_scratch_mount`; line 28: `_scratch_unmount`; line 30: `echo "Fuzz inode"`; line 31: `_scratch_xfs_fuzz_metadata '' 'offline'  "inode ${inum}" >> $seqres.full`; line 32: `echo "Done fuzzing inode"`. metadata fuzzing target: _scratch_xfs_fuzz_metadata '' 'offline'  "inode ${inum}" >> $seqres.full The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/414 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/415 -->
# sources/test-tools/xfstests/tests/xfs/415

## Purpose
Populate a XFS filesystem and fuzz every blockdev inode field. Use xfs_scrub to fix the corruption. In this subset it exercises xfs_repair detection and correction of crafted metadata damage; xfs_scrub online checking or repair of populated/fuzzed filesystems; metadata fuzzing through common/fuzzy helper paths. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest dangerous_fuzzers scrub fuzzers_online_repair`. It imports common/preamble, common/filter, common/populate, common/fuzzy. Local helpers are no local shell helpers. Requirement and fix gates include `_require_scratch_xfs_fuzz_fields`. External tools and command surfaces visible in the source include `xfs_scrub`, `mount`, `stat`, `file`, `rm`, `blockdev`. Key shell state is carried in `inum`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 20: `_require_scratch_xfs_fuzz_fields`; line 22: `echo "Format and populate"`; line 23: `_scratch_populate_cached nofill > $seqres.full 2>&1`; line 25: `echo "Find blockdev inode"`; line 26: `_scratch_mount`; line 28: `_scratch_unmount`; line 30: `echo "Fuzz inode"`; line 31: `_scratch_xfs_fuzz_metadata '' 'online'  "inode ${inum}" >> $seqres.full`; line 32: `echo "Done fuzzing inode"`. metadata fuzzing target: _scratch_xfs_fuzz_metadata '' 'online'  "inode ${inum}" >> $seqres.full The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/415 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/416 -->
# sources/test-tools/xfstests/tests/xfs/416

## Purpose
Populate a XFS filesystem and fuzz every local-format symlink inode field. Use xfs_repair to fix the corruption. In this subset it exercises xfs_repair detection and correction of crafted metadata damage; metadata fuzzing through common/fuzzy helper paths. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest dangerous_fuzzers repair fuzzers_repair`. It imports common/preamble, common/filter, common/populate, common/fuzzy. Local helpers are no local shell helpers. Requirement and fix gates include `_require_scratch_xfs_fuzz_fields`. External tools and command surfaces visible in the source include `xfs_repair`, `mount`, `stat`, `file`, `rm`. Key shell state is carried in `inum`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 20: `_require_scratch_xfs_fuzz_fields`; line 22: `echo "Format and populate"`; line 23: `_scratch_populate_cached nofill > $seqres.full 2>&1`; line 25: `echo "Find local-format symlink inode"`; line 26: `_scratch_mount`; line 28: `_scratch_unmount`; line 30: `echo "Fuzz inode"`; line 31: `_scratch_xfs_fuzz_metadata '' 'offline'  "inode ${inum}" >> $seqres.full`; line 32: `echo "Done fuzzing inode"`. metadata fuzzing target: _scratch_xfs_fuzz_metadata '' 'offline'  "inode ${inum}" >> $seqres.full The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/416 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/417 -->
# sources/test-tools/xfstests/tests/xfs/417

## Purpose
Populate a XFS filesystem and fuzz every local-format symlink inode field. Use xfs_scrub to fix the corruption. In this subset it exercises xfs_repair detection and correction of crafted metadata damage; xfs_scrub online checking or repair of populated/fuzzed filesystems; metadata fuzzing through common/fuzzy helper paths. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest dangerous_fuzzers scrub fuzzers_online_repair`. It imports common/preamble, common/filter, common/populate, common/fuzzy. Local helpers are no local shell helpers. Requirement and fix gates include `_require_scratch_xfs_fuzz_fields`. External tools and command surfaces visible in the source include `xfs_scrub`, `mount`, `stat`, `file`, `rm`. Key shell state is carried in `inum`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 20: `_require_scratch_xfs_fuzz_fields`; line 22: `echo "Format and populate"`; line 23: `_scratch_populate_cached nofill > $seqres.full 2>&1`; line 25: `echo "Find local-format symlink inode"`; line 26: `_scratch_mount`; line 28: `_scratch_unmount`; line 30: `echo "Fuzz inode"`; line 31: `_scratch_xfs_fuzz_metadata '' 'online'  "inode ${inum}" >> $seqres.full`; line 32: `echo "Done fuzzing inode"`. metadata fuzzing target: _scratch_xfs_fuzz_metadata '' 'online'  "inode ${inum}" >> $seqres.full The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/417 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/418 -->
# sources/test-tools/xfstests/tests/xfs/418

## Purpose
Populate a XFS filesystem and fuzz every AG1 superblock field. Use xfs_repair to fix the corruption. In this subset it exercises xfs_repair detection and correction of crafted metadata damage; metadata fuzzing through common/fuzzy helper paths. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest dangerous_fuzzers repair fuzzers_repair`. It imports common/preamble, common/filter, common/populate, common/fuzzy. Local helpers are no local shell helpers. Requirement and fix gates include `_require_scratch_xfs_fuzz_fields`. External tools and command surfaces visible in the source include `xfs_repair`, `stat`, `file`, `rm`. Key shell state is carried in mostly transient harness variables, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 20: `_require_scratch_xfs_fuzz_fields`; line 22: `echo "Format and populate"`; line 23: `_scratch_populate_cached nofill > $seqres.full 2>&1`; line 25: `echo "Fuzz superblock"`; line 26: `_scratch_xfs_fuzz_metadata '' 'offline' 'sb 1' >> $seqres.full`; line 27: `echo "Done fuzzing superblock"`. metadata fuzzing target: _scratch_xfs_fuzz_metadata '' 'offline' 'sb 1' >> $seqres.full The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/418 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/419 -->
# sources/test-tools/xfstests/tests/xfs/419

## Purpose
Regression test for kernel commits: 6b69e485894b ("xfs: standardize extent size hint validation") 603f000b15f2 ("xfs: validate extsz hints against rt extent size when rtinherit is set") Regression test for xfsprogs commit: 1e8afffb ("mkfs: validate rt extent size hint when rtinherit is set") Collectively, these patches ensure that we cannot set the extent size hint on a directory when the directory is configured to propagate its realtime and extent size hint to newly created files when the hint size isn't aligned to the size of a realtime extent. If the patches aren't applied, the write will fail and xfs_repair will say that the fs is corrupt. In this subset it exercises realtime device allocation and realtime reverse-map behavior; xfs_repair detection and correction of crafted metadata damage; mkfs.xfs formatting and geometry validation; directory metadata layout and traversal behavior. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto quick realtime mkfs`. It imports common/preamble, common/filter. Local helpers are no local shell helpers. Requirement and fix gates include `_require_realtime`; `_require_scratch`; `_require_xfs_scratch_non_zoned`; `_notrun "cannot set rt extent size ($rtextsz) larger than fs block size ($dbsize)"`. External tools and command surfaces visible in the source include `xfs_io`, `xfs_repair`, `mkfs.xfs`, `mount`, `stat`, `grep`, `file`. Key shell state is carried in `mkfs_args`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 36: `$MKFS_XFS_PROG -d rtinherit=1 "${mkfs_args[@]}" &>> $seqres.full && \`; line 37: `echo "mkfs should not succeed with heritable rtext-unaligned extent hint"`; line 38: `$MKFS_XFS_PROG -d rtinherit=0 "${mkfs_args[@]}" &>> $seqres.full || \`; line 39: `echo "mkfs should succeed with uninheritable rtext-unaligned extent hint"`; line 42: `_scratch_mkfs_xfs -r extsize=7b | _filter_mkfs >> $seqres.full 2> $tmp.mkfs`; line 43: `cat $tmp.mkfs >> $seqres.full`; line 45: `_scratch_mount`; line 48: `_require_xfs_scratch_non_zoned`; line 55: `$XFS_IO_PROG -c 'extsize 0' -c 'chattr +t' $SCRATCH_MNT`; plus 3 further source-derived command steps.. The main integration signal is the scripted xfstests workflow and its golden-output comparison. The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate; realtime device geometry and internal/external rt-device handling affect expected output. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/419 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/420 -->
# sources/test-tools/xfstests/tests/xfs/420

## Purpose
Test SEEK_HOLE/SEEK_DATA into a region that is marked CoW'd for speculative preallocation in the CoW fork and isn't backed by data fork extents. - Set a huge cowextsize hint. - Create a file "DD " (two data blocks, six hole blocks) - Reflink copy this file to a second file. - Write to the first block of the second file to create a single large CoW reservation covering the whole file. - Write to block 3, which should be a hole in the data fork. - Display the SEEK_HOLE/SEEK_DATA info for the second file to confirm that we see the data in blocks 0-1, the hole at block 2, the data at block 3, and the hole for the rest of the file. Basically we want to create a file with the following data/CoW forks: data: DD------ cow: dddddddd ^--^---------- these blocks are dirty And then check that SEEK_HOLE and SEEK_DATA actually find that second dirty block even though we've never had a data fork extent mapping the second dirty block. We need the huge cowextsize so that the hole area receives preallocation in the CoW fork. In this subset it exercises reflink, CoW, refcount, and shared-extent behavior; directory metadata layout and traversal behavior. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto quick clone punch seek`. It imports common/preamble, common/filter, common/reflink. Local helpers are `exercise_lseek`. Requirement and fix gates include `_require_scratch_reflink`; `_require_cp_reflink`; `_require_xfs_io_command "cowextsize"`; `_require_xfs_io_command "fpunch"`. External tools and command surfaces visible in the source include `xfs_io`, `dd`, `mount`, `stat`, `sed`, `file`, `mkdir`, `cp`, `rm`, `sync`, `truncate`. Key shell state is carried in `testdir`, `blksz`, `nr`, `filesize`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 41: `_require_xfs_io_command "cowextsize"`; line 42: `_require_xfs_io_command "fpunch"`; line 44: `echo "Format and mount"`; line 45: `_scratch_mkfs > $seqres.full 2>&1`; line 46: `_scratch_mount >> $seqres.full 2>&1`; line 49: `mkdir $testdir`; line 59: `echo "Seek holes and data in file1"`; line 60: `$XFS_IO_PROG -c "seek -d 0" $testdir/file1`; line 61: `$XFS_IO_PROG -c "seek -h $((2 * blksz))" $testdir/file1 | sed -e '/Whence/d'`; plus 3 further source-derived command steps.. creates shared extents and CoW/refcount state The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include shared extent and CoW accounting depends on reflink/refcount support. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/420 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/421 -->
# sources/test-tools/xfstests/tests/xfs/421

## Purpose
Test SEEK_HOLE/SEEK_DATA into a region that is marked CoW'd for speculative preallocation in the CoW fork and isn't backed by data fork extents. - Set a huge cowextsize hint. - Create a file "DD " (two data blocks, six hole blocks) - Reflink copy this file to a second file. - dio write to the first block of the second file to create a single large CoW reservation covering the whole file. - dio write to block 3, which should be a hole in the data fork. - Display the SEEK_HOLE/SEEK_DATA info for the second file to confirm that we see the data in blocks 0-1, the hole at block 2, the data at block 3, and the hole for the rest of the file. Basically we want to create a file with the following data/CoW forks: data: DD------ cow: dddddddd ^--^---------- these blocks are dirty And then check that SEEK_HOLE and SEEK_DATA actually find that second dirty block even though we've never had a data fork extent mapping the second dirty block. We need the huge cowextsize so that the hole area receives preallocation in the CoW fork. In this subset it exercises reflink, CoW, refcount, and shared-extent behavior; directory metadata layout and traversal behavior. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto quick clone punch seek`. It imports common/preamble, common/filter, common/reflink. Local helpers are no local shell helpers. Requirement and fix gates include `_require_scratch_reflink`; `_require_cp_reflink`; `_require_xfs_io_command "cowextsize"`; `_require_xfs_io_command "fpunch"`. External tools and command surfaces visible in the source include `xfs_io`, `dd`, `mount`, `stat`, `file`, `mkdir`, `cp`, `rm`, `sync`, `truncate`. Key shell state is carried in `testdir`, `blksz`, `nr`, `filesize`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 41: `_require_xfs_io_command "cowextsize"`; line 42: `_require_xfs_io_command "fpunch"`; line 44: `echo "Format and mount"`; line 45: `_scratch_mkfs > $seqres.full 2>&1`; line 46: `_scratch_mount >> $seqres.full 2>&1`; line 49: `mkdir $testdir`; line 55: `echo "Create the original files"`; line 56: `$XFS_IO_PROG -c "cowextsize" $testdir >> $seqres.full`; line 57: `$XFS_IO_PROG -c "cowextsize $filesize" $testdir >> $seqres.full`; plus 3 further source-derived command steps.. creates shared extents and CoW/refcount state The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include shared extent and CoW accounting depends on reflink/refcount support. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/421 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/422 -->
# sources/test-tools/xfstests/tests/xfs/422

## Purpose
Race fsstress and rmapbt repair for a while to see if we crash or livelock. In this subset it exercises reverse mapping metadata and owner-accounting validation; xfs_repair detection and correction of crafted metadata damage; filesystem freeze/unfreeze behavior under stress or error injection. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest online_repair fsstress_online_repair freeze`. It imports common/preamble, common/filter, common/fuzzy, common/inject. Local helpers are `_cleanup`. Requirement and fix gates include `_require_scratch`; `_require_xfs_stress_online_repair`; `_require_xfs_has_feature "$SCRATCH_MNT" rmapbt`. External tools and command surfaces visible in the source include `fsstress`, `mount`, `stat`, `rm`. Key shell state is carried in mostly transient harness variables, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 13: `_scratch_xfs_stress_scrub_cleanup &> /dev/null`; line 15: `rm -r -f $tmp.*`; line 25: `_require_xfs_stress_online_repair`; line 27: `_scratch_mkfs > "$seqres.full" 2>&1`; line 28: `_scratch_mount`; line 29: `_require_xfs_has_feature "$SCRATCH_MNT" rmapbt`; line 30: `_scratch_xfs_stress_online_repair -s "repair rmapbt %agno%"`; line 33: `echo Silence is golden`. The main integration signal is the scripted xfstests workflow and its golden-output comparison. The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate; error-injection timing and shutdown/recovery behavior are kernel-sensitive; stress/race coverage is timing-sensitive and can expose hangs rather than clean assertion failures. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/422 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/423 -->
# sources/test-tools/xfstests/tests/xfs/423

## Purpose
Race scrubbing the inode record while appending to a file. This exposes a bug in xfs_bmap_count_blocks where we count delalloc extents for di_nblocks if the fork is in extents format, but we don't count them if the fork is in btree format. In this subset it exercises xfs_scrub online checking or repair of populated/fuzzed filesystems. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest scrub prealloc`. It imports common/preamble, common/filter, common/fuzzy, common/inject. Local helpers are no local shell helpers. Requirement and fix gates include `_require_test_program "punch-alternating"`; `_require_xfs_io_command "scrub"`; `_require_xfs_io_command "falloc"`; `_require_scratch`. External tools and command surfaces visible in the source include `xfs_io`, `mount`, `stat`, `diff`, `file`, `rm`, `sync`, `punch-alternating`. Key shell state is carried in mostly transient harness variables, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 23: `_require_xfs_io_command "scrub"`; line 24: `_require_xfs_io_command "falloc"`; line 27: `echo "Format and populate"`; line 28: `_scratch_mkfs > "$seqres.full" 2>&1`; line 29: `_scratch_mount`; line 31: `$XFS_IO_PROG -f -c 'falloc 0 10m' $SCRATCH_MNT/a >> $seqres.full`; line 32: `$XFS_IO_PROG -f -c 'falloc 0 10m' $SCRATCH_MNT/b >> $seqres.full`; line 33: `$here/src/punch-alternating $SCRATCH_MNT/b`; line 34: `_scratch_sync`; plus 3 further source-derived command steps.. The main integration signal is the scripted xfstests workflow and its golden-output comparison. The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate; error-injection timing and shutdown/recovery behavior are kernel-sensitive; stress/race coverage is timing-sensitive and can expose hangs rather than clean assertion failures. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/423 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/424 -->
# sources/test-tools/xfstests/tests/xfs/424

## Purpose
This case checks if setting type causes error. On crc filesystems, xfs_db doesn't take sector size into account when setting type, and this can result in an errant crc. This issue has been fixed in xfsprogs-dev: '55f224b ("xfs_db: update buffer size when new type is set")' On crc filesystems, when setting the type to "inode" the verifier validates multiple inodes in the current fs block, so setting the buffer size to that of just one inode is not sufficient and it'll emit spurious verifier errors for all but the first. This issue has been fixed in xfsprogs-dev: '533d1d2 ("xfs_db: properly set inode type")' In this subset it exercises XFS regression behavior exercised through the xfstests harness. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto quick db`. It imports common/preamble, common/filter. Local helpers are `filter_dbval`. Requirement and fix gates include `_require_scratch_nocheck`. External tools and command surfaces visible in the source include `xfs_db`, `mkfs.xfs`, `dd`, `stat`, `grep`, `awk`, `diff`, `file`, `blockdev`. Key shell state is carried in `sec_sz`, `sector_sizes`, `finobt_enabled`, `DADDR`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 34: `echo "Silence is golden."`; line 48: `while [ $sec_sz -le 4096 ]; do`; line 53: `for SECTOR_SIZE in $sector_sizes; do`; line 55: `$MKFS_XFS_PROG -f -s size=$SECTOR_SIZE $SCRATCH_DEV | \`; line 56: `grep -q 'finobt=1' && finobt_enabled=1`; line 58: `for TYPE in agf agi agfl sb; do`; line 61: `$XFS_DB_PROG -c "daddr $DADDR" -c "type $TYPE" $SCRATCH_DEV`; line 66: `$XFS_DB_PROG -c "daddr $DADDR" -c "type inode" $SCRATCH_DEV`; line 69: `$XFS_DB_PROG -c "daddr $DADDR" -c "type bnobt" $SCRATCH_DEV`; plus 3 further source-derived command steps.. The main integration signal is the scripted xfstests workflow and its golden-output comparison. The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate; error-injection timing and shutdown/recovery behavior are kernel-sensitive. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/424 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/425 -->
# sources/test-tools/xfstests/tests/xfs/425

## Purpose
Populate a XFS filesystem and fuzz every user dquot field. Use xfs_repair to fix the corruption. In this subset it exercises xfs_repair detection and correction of crafted metadata damage; metadata fuzzing through common/fuzzy helper paths. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest dangerous_fuzzers repair fuzzers_repair`. It imports common/preamble, common/filter, common/populate, common/fuzzy, common/quota. Local helpers are no local shell helpers. Requirement and fix gates include `_require_scratch_xfs_fuzz_fields`; `_require_quota`. External tools and command surfaces visible in the source include `xfs_repair`, `mount`, `stat`, `file`, `rm`. Key shell state is carried in mostly transient harness variables, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 21: `_require_scratch_xfs_fuzz_fields`; line 24: `echo "Format and populate"`; line 25: `_scratch_populate_cached nofill > $seqres.full 2>&1`; line 27: `_scratch_mount`; line 28: `$here/src/feature -U $SCRATCH_DEV || _notrun "user quota disabled"`; line 29: `_scratch_unmount`; line 31: `_scratch_xfs_set_quota_fuzz_ids`; line 33: `for id in "${SCRATCH_XFS_QUOTA_FUZZ_IDS[@]}"; do`; line 34: `echo "Fuzz user $id dquot"`; plus 2 further source-derived command steps.. metadata fuzzing target: _scratch_xfs_fuzz_metadata '' 'offline'  "dquot -u $id" >> $seqres.full mounts or inspects quota state and dquot accounting The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate; quota state can persist through remounts and is sensitive to mount options. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/425 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/426 -->
# sources/test-tools/xfstests/tests/xfs/426

## Purpose
Populate a XFS filesystem and fuzz every user dquot field. Use xfs_scrub to fix the corruption. In this subset it exercises xfs_repair detection and correction of crafted metadata damage; xfs_scrub online checking or repair of populated/fuzzed filesystems; metadata fuzzing through common/fuzzy helper paths. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest dangerous_fuzzers scrub fuzzers_online_repair`. It imports common/preamble, common/filter, common/populate, common/fuzzy, common/quota. Local helpers are no local shell helpers. Requirement and fix gates include `_require_scratch_xfs_fuzz_fields`; `_require_quota`. External tools and command surfaces visible in the source include `xfs_scrub`, `mount`, `stat`, `file`, `rm`. Key shell state is carried in mostly transient harness variables, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 21: `_require_scratch_xfs_fuzz_fields`; line 24: `echo "Format and populate"`; line 25: `_scratch_populate_cached nofill > $seqres.full 2>&1`; line 27: `_scratch_mount`; line 28: `$here/src/feature -U $SCRATCH_DEV || _notrun "user quota disabled"`; line 29: `_scratch_unmount`; line 31: `_scratch_xfs_set_quota_fuzz_ids`; line 33: `for id in "${SCRATCH_XFS_QUOTA_FUZZ_IDS[@]}"; do`; line 34: `echo "Fuzz user $id dquot"`; plus 2 further source-derived command steps.. metadata fuzzing target: _scratch_xfs_fuzz_metadata '' 'online'  "dquot -u $id" >> $seqres.full mounts or inspects quota state and dquot accounting The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate; quota state can persist through remounts and is sensitive to mount options. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/426 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/427 -->
# sources/test-tools/xfstests/tests/xfs/427

## Purpose
Populate a XFS filesystem and fuzz every group dquot field. Use xfs_repair to fix the corruption. In this subset it exercises xfs_repair detection and correction of crafted metadata damage; metadata fuzzing through common/fuzzy helper paths. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest dangerous_fuzzers repair fuzzers_repair`. It imports common/preamble, common/filter, common/populate, common/fuzzy, common/quota. Local helpers are no local shell helpers. Requirement and fix gates include `_require_scratch_xfs_fuzz_fields`; `_require_quota`. External tools and command surfaces visible in the source include `xfs_repair`, `mount`, `stat`, `file`, `rm`. Key shell state is carried in mostly transient harness variables, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 21: `_require_scratch_xfs_fuzz_fields`; line 24: `echo "Format and populate"`; line 25: `_scratch_populate_cached nofill > $seqres.full 2>&1`; line 27: `_scratch_mount`; line 28: `$here/src/feature -G $SCRATCH_DEV || _notrun "group quota disabled"`; line 29: `_scratch_unmount`; line 31: `_scratch_xfs_set_quota_fuzz_ids`; line 33: `for id in "${SCRATCH_XFS_QUOTA_FUZZ_IDS[@]}"; do`; line 34: `echo "Fuzz group $id dquot"`; plus 2 further source-derived command steps.. metadata fuzzing target: _scratch_xfs_fuzz_metadata '' 'offline'  "dquot -g $id" >> $seqres.full mounts or inspects quota state and dquot accounting The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate; quota state can persist through remounts and is sensitive to mount options. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/427 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/428 -->
# sources/test-tools/xfstests/tests/xfs/428

## Purpose
Populate a XFS filesystem and fuzz every group dquot field. Use xfs_scrub to fix the corruption. In this subset it exercises xfs_repair detection and correction of crafted metadata damage; xfs_scrub online checking or repair of populated/fuzzed filesystems; metadata fuzzing through common/fuzzy helper paths. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest dangerous_fuzzers scrub fuzzers_online_repair`. It imports common/preamble, common/filter, common/populate, common/fuzzy, common/quota. Local helpers are no local shell helpers. Requirement and fix gates include `_require_scratch_xfs_fuzz_fields`; `_require_quota`. External tools and command surfaces visible in the source include `xfs_scrub`, `mount`, `stat`, `file`, `rm`. Key shell state is carried in mostly transient harness variables, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 21: `_require_scratch_xfs_fuzz_fields`; line 24: `echo "Format and populate"`; line 25: `_scratch_populate_cached nofill > $seqres.full 2>&1`; line 27: `_scratch_mount`; line 28: `$here/src/feature -G $SCRATCH_DEV || _notrun "group quota disabled"`; line 29: `_scratch_unmount`; line 31: `_scratch_xfs_set_quota_fuzz_ids`; line 33: `for id in "${SCRATCH_XFS_QUOTA_FUZZ_IDS[@]}"; do`; line 34: `echo "Fuzz group $id dquot"`; plus 2 further source-derived command steps.. metadata fuzzing target: _scratch_xfs_fuzz_metadata '' 'online'  "dquot -g $id" >> $seqres.full mounts or inspects quota state and dquot accounting The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate; quota state can persist through remounts and is sensitive to mount options. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/428 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/429 -->
# sources/test-tools/xfstests/tests/xfs/429

## Purpose
Populate a XFS filesystem and fuzz every project dquot field. Use xfs_repair to fix the corruption. In this subset it exercises xfs_repair detection and correction of crafted metadata damage; metadata fuzzing through common/fuzzy helper paths. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest dangerous_fuzzers repair fuzzers_repair`. It imports common/preamble, common/filter, common/populate, common/fuzzy, common/quota. Local helpers are no local shell helpers. Requirement and fix gates include `_require_scratch_xfs_fuzz_fields`; `_require_quota`. External tools and command surfaces visible in the source include `xfs_repair`, `mount`, `stat`, `file`, `rm`. Key shell state is carried in mostly transient harness variables, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 21: `_require_scratch_xfs_fuzz_fields`; line 24: `echo "Format and populate"`; line 25: `_scratch_populate_cached nofill > $seqres.full 2>&1`; line 27: `_scratch_mount`; line 28: `$here/src/feature -P $SCRATCH_DEV || _notrun "project quota disabled"`; line 29: `_scratch_unmount`; line 31: `_scratch_xfs_set_quota_fuzz_ids`; line 33: `for id in "${SCRATCH_XFS_QUOTA_FUZZ_IDS[@]}"; do`; line 34: `echo "Fuzz project $id dquot"`; plus 2 further source-derived command steps.. metadata fuzzing target: _scratch_xfs_fuzz_metadata '' 'offline'  "dquot -p $id" >> $seqres.full mounts or inspects quota state and dquot accounting The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate; quota state can persist through remounts and is sensitive to mount options. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/429 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/430 -->
# sources/test-tools/xfstests/tests/xfs/430

## Purpose
Populate a XFS filesystem and fuzz every project dquot field. Use xfs_scrub to fix the corruption. In this subset it exercises xfs_repair detection and correction of crafted metadata damage; xfs_scrub online checking or repair of populated/fuzzed filesystems; metadata fuzzing through common/fuzzy helper paths. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest dangerous_fuzzers scrub fuzzers_online_repair`. It imports common/preamble, common/filter, common/populate, common/fuzzy, common/quota. Local helpers are no local shell helpers. Requirement and fix gates include `_require_scratch_xfs_fuzz_fields`; `_require_quota`. External tools and command surfaces visible in the source include `xfs_scrub`, `mount`, `stat`, `file`, `rm`. Key shell state is carried in mostly transient harness variables, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 21: `_require_scratch_xfs_fuzz_fields`; line 24: `echo "Format and populate"`; line 25: `_scratch_populate_cached nofill > $seqres.full 2>&1`; line 27: `_scratch_mount`; line 28: `$here/src/feature -P $SCRATCH_DEV || _notrun "project quota disabled"`; line 29: `_scratch_unmount`; line 31: `_scratch_xfs_set_quota_fuzz_ids`; line 33: `for id in "${SCRATCH_XFS_QUOTA_FUZZ_IDS[@]}"; do`; line 34: `echo "Fuzz project $id dquot"`; plus 2 further source-derived command steps.. metadata fuzzing target: _scratch_xfs_fuzz_metadata '' 'online'  "dquot -p $id" >> $seqres.full mounts or inspects quota state and dquot accounting The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate; quota state can persist through remounts and is sensitive to mount options. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/430 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/431 -->
# sources/test-tools/xfstests/tests/xfs/431

## Purpose
Verify kernel doesn't panic when user attempts to set realtime flags on non-realtime FS, using kernel compiled with CONFIG_XFS_RT. Unpatched kernels will panic during this test. Kernels not compiled with CONFIG_XFS_RT should pass test. See CVE-2017-14340 for more information. In this subset it exercises realtime device allocation and realtime reverse-map behavior. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto quick`. It imports common/preamble, common/filter. Local helpers are no local shell helpers. Requirement and fix gates include `_require_xfs_io_command "chattr" "t"`; `_require_xfs_io_command "fsync"`; `_require_xfs_io_command "pwrite"`; `_require_scratch`. External tools and command surfaces visible in the source include `xfs_io`, `xfs_repair`, `mount`, `stat`, `grep`, `file`, `rm`, `sync`. Key shell state is carried in mostly transient harness variables, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 22: `_require_xfs_io_command "chattr" "t"`; line 23: `_require_xfs_io_command "fsync"`; line 24: `_require_xfs_io_command "pwrite"`; line 27: `_scratch_mkfs >/dev/null 2>&1`; line 28: `_scratch_mount`; line 32: `_xfs_force_bdev realtime $SCRATCH_MNT &> /dev/null`; line 37: `if $XFS_IO_PROG -c 'lsattr' $SCRATCH_MNT | grep -q 't'; then`; line 39: `$XFS_IO_PROG -fc 'pwrite 0 1m' -c fsync $SCRATCH_MNT/testfile |`; line 40: `tee -a $seqres.full | _filter_xfs_io`; plus 2 further source-derived command steps.. The main integration signal is the scripted xfstests workflow and its golden-output comparison. The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include realtime device geometry and internal/external rt-device handling affect expected output; error-injection timing and shutdown/recovery behavior are kernel-sensitive. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/431 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/432 -->
# sources/test-tools/xfstests/tests/xfs/432

## Purpose
Ensure that metadump copies large directory extents Metadump helpfully discards directory (and xattr) extents that are longer than 1000 blocks. This is a little silly since a hardlink farm can easily create such a monster. Now that we've upped metadump's default too-long-extent discard threshold to 2^21 blocks, make sure we never do that again. In this subset it exercises xfsdump/xfsrestore compatibility and metadata preservation; xfs_metadump/xfs_mdrestore metadata image coverage; extended attribute metadata behavior; directory metadata layout and traversal behavior. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto quick dir metadata metadump`. It imports common/preamble, common/filter, common/metadump. Local helpers are `_cleanup`, `check_for_long_extent`. Requirement and fix gates include `_require_command "$XFS_MDRESTORE_PROG" "xfs_mdrestore"`; `_require_scratch`. External tools and command surfaces visible in the source include `xfs_db`, `xfs_mdrestore`, `mount`, `stat`, `awk`, `sed`, `file`, `touch`, `mkdir`, `ln`, `rm`. Key shell state is carried in `testdir`, `max_fname_len`, `blksz`, `blocks`, `names`, `name`, `dir_inum`, `inum`, `extlen`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 23: `rm -f "$tmp".*`; line 24: `_xfs_cleanup_verify_metadump`; line 31: `_require_command "$XFS_MDRESTORE_PROG" "xfs_mdrestore"`; line 33: `_xfs_setup_verify_metadump`; line 35: `rm -f "$seqres.full"`; line 37: `echo "Format and mount"`; line 55: `_scratch_mkfs_xfs -b size=1k -n size=64k > "$seqres.full" 2>&1`; line 56: `_scratch_mount >> "$seqres.full" 2>&1`; line 65: `echo "Create huge dir"`; plus 3 further source-derived command steps.. verifies metadump/mdrestore behavior and image fidelity The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include expected-output drift, missing helper binaries, and unsupported scratch geometry are the main hazards. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/432 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/433 -->
# sources/test-tools/xfstests/tests/xfs/433

## Purpose
Regression test for an XFS NULL xattr buffer problem during unlink. XFS had a bug where the attr fork walk during file removal could go off the rails due to a stale reference to content of a released buffer. Memory pressure could cause this reference to point to free or reused memory and cause subsequent attribute fork lookups to fail, return a NULL buffer and possibly crash. This test emulates this behavior using an error injection knob to explicitly disable buffer LRU caching. This forces the attr walk to execute under conditions where each buffer is immediately freed on release. Commit f35c5e10c6ed ("xfs: reinit btree pointer on attr tree inactivation walk") fixed the bug. In this subset it exercises extended attribute metadata behavior. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto quick attr`. It imports common/preamble, common/attr, common/inject. Local helpers are no local shell helpers. Requirement and fix gates include `_require_xfs_io_error_injection buf_lru_ref`; `_require_scratch`; `_require_attrs`. External tools and command surfaces visible in the source include `xfs_io`, `setfattr`, `mount`, `stat`, `sed`, `file`, `touch`, `rm`. Key shell state is carried in `file`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 29: `_require_xfs_io_error_injection buf_lru_ref`; line 33: `_scratch_mkfs > $seqres.full 2>&1`; line 34: `_scratch_mount`; line 39: `touch $file`; line 40: `for i in $(seq 0 499); do`; line 41: `$SETFATTR_PROG -n trusted.user.$i -v 0 $file`; line 45: `_scratch_cycle_mount || _fail "cycle mount failure"`; line 48: `_scratch_inject_error buf_lru_ref 1`; line 49: `rm -f $file`; plus 2 further source-derived command steps.. error injection knobs: buf_lru_ref The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include error-injection timing and shutdown/recovery behavior are kernel-sensitive. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/433 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/434 -->
# sources/test-tools/xfstests/tests/xfs/434

## Purpose
Ensure that we don't leak quota inodes when CoW recovery fails. Use xfs_fsr to inject bmap redo items in the log for a linked file and an unlinked file; enable quota so that we always mount with the quota inodes; and then corrupt the refcount btree to ensure that the CoW garbage collection (and therefore the mount) fail. On a subsequent mount attempt, we should be able to replay the bmap items for the linked and unlinked files without prematurely truncating the unlinked inode and without leaking the linked inode, and we should be able to release the quota inodes when we're aborting the mount. We also should not leak dquots. In this subset it exercises reflink, CoW, refcount, and shared-extent behavior; quota accounting, dquot metadata, and quota mount mode handling; mount/remount acceptance and rejection paths; xfs_fsr defragmentation and exchangerange recovery. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto quick clone fsr`. It imports common/preamble, common/filter, common/attr, common/reflink, common/inject, common/quota, common/module. Local helpers are no local shell helpers. Requirement and fix gates include `_require_quota`; `_require_scratch_reflink`; `_require_cp_reflink`; `_require_command "$XFS_FSR_PROG" "xfs_fsr"`; `_require_xfs_io_command falloc # fsr requires support for preallocation`; `_require_xfs_io_error_injection "bmap_finish_one"`; `_require_xfs_scratch_rmapbt`; `_require_congruent_file_oplen $SCRATCH_MNT $blksz`. External tools and command surfaces visible in the source include `xfs_io`, `xfs_db`, `xfs_fsr`, `dd`, `mount`, `stat`, `file`, `touch`, `mkdir`, `cp`, `rm`. Key shell state is carried in `testdir`, `blksz`, `blks`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 34: `_require_command "$XFS_FSR_PROG" "xfs_fsr"`; line 35: `_require_xfs_io_command falloc # fsr requires support for preallocation`; line 36: `_require_xfs_io_error_injection "bmap_finish_one"`; line 37: `_require_xfs_scratch_rmapbt`; line 39: `rm -f "$seqres.full"`; line 41: `echo "Format and mount"`; line 42: `_scratch_mkfs > "$seqres.full" 2>&1`; line 43: `_scratch_mount -o noquota >> "$seqres.full" 2>&1`; line 49: `mkdir "$testdir"`; plus 3 further source-derived command steps.. error injection knobs: bmap_finish_one drives xfs_fsr defragmentation paths mounts or inspects quota state and dquot accounting creates shared extents and CoW/refcount state The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate; quota state can persist through remounts and is sensitive to mount options; shared extent and CoW accounting depends on reflink/refcount support; error-injection timing and shutdown/recovery behavior are kernel-sensitive. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/434 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/435 -->
# sources/test-tools/xfstests/tests/xfs/435

## Purpose
Ensure that we don't leak dquots when CoW recovery fails. Corrupt the refcount btree to ensure that the CoW garbage collection (and therefore the mount) fail. On a subsequent mount attempt, we should be able to release the quota inodes when we're aborting the mount. We also should not leak dquots. In this subset it exercises reflink, CoW, refcount, and shared-extent behavior; quota accounting, dquot metadata, and quota mount mode handling; mount/remount acceptance and rejection paths. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto quick clone`. It imports common/preamble, common/filter, common/attr, common/reflink, common/quota, common/module. Local helpers are no local shell helpers. Requirement and fix gates include `_require_quota`; `_require_scratch_reflink`; `_require_cp_reflink`; `_disable_dmesg_check`; `_require_congruent_file_oplen $SCRATCH_MNT $blksz`. External tools and command surfaces visible in the source include `xfs_db`, `dd`, `mount`, `stat`, `file`, `mkdir`, `cp`, `rm`. Key shell state is carried in `testdir`, `blksz`, `blks`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 30: `rm -f "$seqres.full"`; line 32: `echo "Format and mount"`; line 33: `_scratch_mkfs > "$seqres.full" 2>&1`; line 34: `_scratch_mount -o quota >> "$seqres.full" 2>&1`; line 40: `mkdir "$testdir"`; line 42: `echo "Create a many-block file"`; line 43: `_pwrite_byte 0x62 0 $((blksz * blks)) $testdir/file1 >> $seqres.full`; line 44: `_pwrite_byte 0x63 0 $blksz $testdir/file2 >> $seqres.full`; line 45: `_reflink_range $testdir/file2 0 $testdir/file1 $blksz $blksz >> $seqres.full`; plus 3 further source-derived command steps.. mounts or inspects quota state and dquot accounting creates shared extents and CoW/refcount state The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate; quota state can persist through remounts and is sensitive to mount options; shared extent and CoW accounting depends on reflink/refcount support. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/435 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/436 -->
# sources/test-tools/xfstests/tests/xfs/436

## Purpose
Ensure that we don't leak inodes when CoW recovery fails. Use xfs_fsr to inject bmap redo items in the log for a linked file and an unlinked file; and then corrupt the refcount btree to ensure that the CoW garbage collection (and therefore the mount) fail. On a subsequent mount attempt, we should be able to replay the bmap items for the linked and unlinked files without prematurely truncating the unlinked inode and without leaking the linked inode, and we should be able to release all the inodes when we're aborting the mount. In this subset it exercises reflink, CoW, refcount, and shared-extent behavior; mount/remount acceptance and rejection paths; xfs_fsr defragmentation and exchangerange recovery; journal/log geometry or recovery behavior. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto quick clone fsr`. It imports common/preamble, common/filter, common/attr, common/reflink, common/inject, common/module. Local helpers are no local shell helpers. Requirement and fix gates include `_require_scratch_reflink`; `_require_cp_reflink`; `_require_xfs_io_command falloc # fsr requires support for preallocation`; `_require_command "$XFS_FSR_PROG" "xfs_fsr"`; `_require_xfs_io_error_injection "bmap_finish_one"`; `_require_xfs_scratch_rmapbt`; `_require_congruent_file_oplen $SCRATCH_MNT $blksz`. External tools and command surfaces visible in the source include `xfs_io`, `xfs_db`, `xfs_fsr`, `dd`, `mount`, `stat`, `file`, `touch`, `mkdir`, `cp`, `rm`. Key shell state is carried in `testdir`, `blksz`, `blks`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 30: `_require_xfs_io_command falloc # fsr requires support for preallocation`; line 31: `_require_command "$XFS_FSR_PROG" "xfs_fsr"`; line 32: `_require_xfs_io_error_injection "bmap_finish_one"`; line 33: `_require_xfs_scratch_rmapbt`; line 35: `rm -f "$seqres.full"`; line 37: `echo "Format and mount"`; line 38: `_scratch_mkfs > "$seqres.full" 2>&1`; line 39: `_scratch_mount -o noquota >> "$seqres.full" 2>&1`; line 45: `mkdir "$testdir"`; plus 3 further source-derived command steps.. error injection knobs: bmap_finish_one drives xfs_fsr defragmentation paths creates shared extents and CoW/refcount state The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate; quota state can persist through remounts and is sensitive to mount options; shared extent and CoW accounting depends on reflink/refcount support; error-injection timing and shutdown/recovery behavior are kernel-sensitive. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/436 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/437 -->
# sources/test-tools/xfstests/tests/xfs/437

## Purpose
find-api-violations test The purpose of this test is ensure that the xfsprogs programs use the libxfs_ symbols (in libxfs-api-defs.h) instead of raw xfs_ functions. This is for the maintainers; it's not a functionality test. In this subset it exercises XFS regression behavior exercised through the xfstests harness. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto quick other`. It imports common/preamble, common/filter. Local helpers are no local shell helpers. Requirement and fix gates include `_notrun "Can't run find-api-violations.sh without WORKAREA set"`; `_notrun "Can't find find-api-violations.sh tool under \"$WORKAREA\""`. External tools and command surfaces visible in the source include `stat`, `grep`. Key shell state is carried in mostly transient harness variables, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 24: `echo "Silence is golden."`. The main integration signal is the scripted xfstests workflow and its golden-output comparison. The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include expected-output drift, missing helper binaries, and unsupported scratch geometry are the main hazards. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/437 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/438 -->
# sources/test-tools/xfstests/tests/xfs/438

## Purpose
Test for XFS umount hang problem caused by the unceasing push of dquot log item in AIL. Because xfs_qm_dqflush_done() will not be invoked, so each time xfsaild initiates the push, the push will return early after checking xfs_dqflock_nowait(). xfs_qm_dqflush_done() should be invoked by xfs_buf_do_callbacks(). However after the first write and the retried write of dquota buffer get the same IO error, XFS will let xfsaild to restart the write and xfs_buf_do_callbacks() will not be inovked. This test emulates the write error by using dm-flakey. The log area of the XFS filesystem is excluded from the range covered by dm-flakey, so the XFS will not be shutdown prematurely. Fixed by upstream commit 373b058 ("xfs: Properly retry failed dquot items in case of error during buffer writeback") In this subset it exercises quota accounting, dquot metadata, and quota mount mode handling; mount/remount acceptance and rejection paths; filesystem freeze/unfreeze behavior under stress or error injection; journal/log geometry or recovery behavior. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto quick quota freeze`. It imports common/preamble, common/dmflakey, common/quota. Local helpers are `_cleanup`, `make_xfs_scratch_flakey_table`. Requirement and fix gates include `_require_scratch_nocheck`; `_require_flakey_with_error_writes`; `_require_user`; `_require_xfs_quota`; `_require_freeze`. External tools and command surfaces visible in the source include `xfs_db`, `dmsetup`, `xfs_freeze`, `xfs_quota`, `dd`, `mount`, `umount`, `stat`, `awk`, `sed`, `file`, `rm`. Key shell state is carried in `log_ofs`, `table`, `FLAKEY_TABLE_NON_LOG_ERROR`, `FLAKEY_TABLE_ERROR`, `interval`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 30: `xfs_freeze -u $SCRATCH_MNT 2>/dev/null`; line 32: `sysctl -w fs.xfs.xfssyncd_centisecs=${interval} >/dev/null 2>&1`; line 34: `rm -f $tmp.*`; line 35: `_scratch_unmount >/dev/null 2>&1`; line 40: `make_xfs_scratch_flakey_table()`; line 49: `if [ "${USE_EXTERNAL}" = "yes" -a ! -z "$SCRATCH_LOGDEV" ]; then`; line 50: `echo "0 ${dev_sz} $tgt $dev 0 $opt"`; line 54: `local blk_sz=$(_scratch_xfs_get_sb_field blocksize)`; line 55: `local log_ofs=$(_scratch_xfs_get_sb_field logstart)`; plus 3 further source-derived command steps.. mounts or inspects quota state and dquot accounting The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate; quota state can persist through remounts and is sensitive to mount options; error-injection timing and shutdown/recovery behavior are kernel-sensitive. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/438 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/439 -->
# sources/test-tools/xfstests/tests/xfs/439

## Purpose
Regression test for commit: 9c92ee2 ("xfs: validate sb_logsunit is a multiple of the fs blocksize") If log stripe unit isn't a multiple of the fs blocksize and mounting, the invalid sb_logsunit leads to crash as soon as we try to write to the log. In this subset it exercises metadata fuzzing through common/fuzzy helper paths; mount/remount acceptance and rejection paths; journal/log geometry or recovery behavior. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto quick fuzzers log`. It imports common/preamble, common/filter. Local helpers are no local shell helpers. Requirement and fix gates include `_require_scratch_nocheck`; `_fixed_by_kernel_commit 9c92ee208b1f`; `_fixed_by_kernel_commit f1e1765aad7d`. External tools and command surfaces visible in the source include `mount`, `stat`, `sed`, `rm`. Key shell state is carried in `blksz`, `lsunit`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 32: `rm -f "$seqres.full"`; line 35: `_scratch_mkfs > $seqres.full 2>&1 || _fail "mkfs failed"`; line 38: `blksz=$(_scratch_xfs_get_sb_field blocksize)`; line 39: `_scratch_xfs_set_sb_field logsunit $((blksz - 1)) >> $seqres.full 2>&1`; line 42: `lsunit=$(_scratch_xfs_get_sb_field logsunit 2>/dev/null)`; line 48: `if _try_scratch_mount >> $seqres.full 2>&1; then`; line 49: `for i in $(seq 1 1000); do`; line 50: `echo > ${SCRATCH_MNT}/$i`; line 52: `_scratch_unmount`; plus 1 further source-derived command steps.. The main integration signal is the scripted xfstests workflow and its golden-output comparison. The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/439 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/440 -->
# sources/test-tools/xfstests/tests/xfs/440

## Purpose
Regression test for a quota accounting bug when changing the owner of a file that has CoW reservations and no dirty pages. The reservations should shift over to the new owner, but they do not. unreliable_in_parallel: external sync(1) and/or drop caches can reclaim inodes and free post-eof space, resulting in lower than expected block counts. In this subset it exercises reflink, CoW, refcount, and shared-extent behavior; quota accounting, dquot metadata, and quota mount mode handling; directory metadata layout and traversal behavior. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto quick clone quota unreliable_in_parallel`. It imports common/preamble, common/reflink, common/quota, common/filter. Local helpers are no local shell helpers. Requirement and fix gates include `_require_quota`; `_require_scratch_delalloc`; `_require_scratch_reflink`; `_require_cp_reflink`; `_require_user`. External tools and command surfaces visible in the source include `xfs_io`, `mount`, `stat`, `grep`, `file`, `touch`, `cp`, `rm`, `chown`, `sync`. Key shell state is carried in mostly transient harness variables, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 31: `echo "Format and mount"`; line 32: `_scratch_mkfs > "$seqres.full" 2>&1`; line 33: `_scratch_mount "-o usrquota,grpquota" >> "$seqres.full" 2>&1`; line 36: `_xfs_force_bdev data $SCRATCH_MNT`; line 38: `echo "Create files"`; line 39: `$XFS_IO_PROG -c "cowextsize 1m" $SCRATCH_MNT`; line 40: `touch $SCRATCH_MNT/a $SCRATCH_MNT/force_fsgqa`; line 41: `chown $qa_user $SCRATCH_MNT/a $SCRATCH_MNT/force_fsgqa`; line 42: `_pwrite_byte 0x58 0 64k $SCRATCH_MNT/a >> $seqres.full`; plus 3 further source-derived command steps.. mounts or inspects quota state and dquot accounting creates shared extents and CoW/refcount state The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include quota state can persist through remounts and is sensitive to mount options; shared extent and CoW accounting depends on reflink/refcount support. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/440 -->
