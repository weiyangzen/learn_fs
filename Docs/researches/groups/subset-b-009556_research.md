# subset-b-009556 research

Grouped research for the assigned XFS fstests shard. Each section preserves the source path in its title and is wrapped with deterministic markers for source-tree-aligned splitting.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/603 -->
# sources/test-tools/xfstests/tests/xfs/603

## Purpose
`sources/test-tools/xfstests/tests/xfs/603` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair, quota enforcement, unlinked-inode repair, dump/restore behavior. Functional test of using online repair to fix unlinked inodes on a clean filesystem that never got cleaned up. The `_begin_fstest` declaration is `auto online_repair`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/preamble`, `./common/quota`. Local helper surface: `__repair_check_scratch`, `corrupt_scratch`, `exercise_scratch`, `final_check_scratch`, `format_scratch`. Requirement and regression gates include `_require_xfs_db_command iunlink`, `_require_xfs_io_command repair -R directory`, `_require_scratch_nocheck	# repair doesn't like single-AG fs`, `_require_scrub`. Important external or harness tools detected in the full source include `xfs_db`, `xfs_repair`, `mkfs.xfs`, `xfs_scrub`, `mount`, `stat`. Scenario variables and harness state referenced include `SCRATCH_MNT`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata, runs online scrub/repair or xfs_scrub in selected modes, runs offline repair or compares offline-repair findings against expected corruption, sets up quota state and validates accounting or enforcement, uses checksum/stat comparisons as the content oracle. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version; quota tests depend on user/group setup, mount options, and stable quota-tools output.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/603.out`; stable progress/output labels such as `echo "${corruption_bucket_depth}: Value must be between 1 and ${IUNLINK_BUCKETLEN}."`, `echo "grep -E \"${GREP_STR}\"" >> $seqres.full`, `echo "rm failed on inum ${inums[$i]}"`, `echo "scratch fs went offline?"`, `echo "+ Part 1: See if scrub can recover the unlinked list" | tee -a $seqres.full`, and 4 more; diagnostic detail appended to `$seqres.full`; feature-dependent skips through `_notrun`. The source has 214 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/603 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/604 -->
# sources/test-tools/xfstests/tests/xfs/604

## Purpose
`sources/test-tools/xfstests/tests/xfs/604` is an XFS fstests shell case focused on dump/restore behavior. Regression test for patch "xfs: fix internal error from AGFL exhaustion". The `_begin_fstest` declaration is `auto prealloc punch`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/preamble`. Local helper surface: no local shell helpers beyond the main script body. Requirement and regression gates include `_require_scratch`, `_require_xfs_io_command "falloc"`, `_require_xfs_io_command "fpunch"`, `_require_test_program punch-alternating`, `_fixed_by_kernel_commit f63a5b3769ad "xfs: fix internal error from AGFL exhaustion"`, `_notrun "Not enough space on device for falloc_size=$(echo "scale=2; $falloc_size / 1073741824" | $BC -q)GB and bs=$dbsize"`. Important external or harness tools detected in the full source include `xfs_io`, `xfs_db`, `mkfs.xfs`, `punch-alternating`, `mount`. Scenario variables and harness state referenced include `SCRATCH_MNT`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_io` commands for writes, fallocate/punch, bmap inspection, scrub, repair, exchange, or media verification, uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/604.out`; stable progress/output labels such as `echo "Silence is golden"`; feature-dependent skips through `_notrun`. The source has 71 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/604 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/605 -->
# sources/test-tools/xfstests/tests/xfs/605

## Purpose
`sources/test-tools/xfstests/tests/xfs/605` is an XFS fstests shell case focused on mount-option behavior, dump/restore behavior. Test metadump/mdrestore's ability to dump a dirty log and restore it correctly. The `_begin_fstest` declaration is `auto quick metadump log logprint punch`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/dmflakey`, `./common/inject`, `./common/metadump`, `./common/preamble`. Local helper surface: `_cleanup`. Requirement and regression gates include `_require_scratch`, `_require_test`, `_require_loop`, `_require_xfs_debug`, `_require_xfs_io_error_injection log_item_pin`, `_require_dm_target flakey`, `_require_xfs_io_command "pwrite"`, `_require_test_program "punch-alternating"`. Important external or harness tools detected in the full source include `xfs_io`, `mkfs.xfs`, `punch-alternating`, `mount`. Scenario variables and harness state referenced include `SCRATCH_MNT`, `SCRATCH_DEV`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_io` commands for writes, fallocate/punch, bmap inspection, scrub, repair, exchange, or media verification. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/605.out`; stable progress/output labels such as `echo "Format filesystem on scratch device"`, `echo "Initialize and mount filesystem on flakey device"`, `echo "Create test file"`, `echo "Punch alternative blocks of test file"`, `echo "Mount cycle the filesystem on flakey device"`, and 10 more; diagnostic detail appended to `$seqres.full`. The source has 92 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/605 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/606 -->
# sources/test-tools/xfstests/tests/xfs/606

## Purpose
`sources/test-tools/xfstests/tests/xfs/606` is an XFS fstests shell case focused on mount-option behavior. Test xfs_growfs with "too-small" size expansion, which lead to a delta of "0" in xfs_growfs_data_private. This's a regression test of 84712492e6da ("xfs: short circuit xfs_growfs_data_private() if delta is zero"). The `_begin_fstest` declaration is `auto quick growfs`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/preamble`. Local helper surface: `_cleanup`. Requirement and regression gates include `_fixed_by_kernel_commit 84712492e6da "xfs: short circuit xfs_growfs_data_private() if delta is zero"`, `_require_test`, `_require_loop`, `_require_xfs_io_command "truncate"`, `_require_command "$XFS_GROWFS_PROG" xfs_growfs`. Important external or harness tools detected in the full source include `xfs_io`, `mkfs.xfs`, `mount`. Scenario variables and harness state referenced include `TEST_DIR`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_io` commands for writes, fallocate/punch, bmap inspection, scrub, repair, exchange, or media verification, uses loop devices or configuration variants to cover mount/device geometry. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; loop-device setup must be cleaned reliably to avoid leaked mounts or stale backing files.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/606.out`; stable progress/output labels such as `echo "xfs_growfs fails!"`, `echo "Silence is golden"`; diagnostic detail appended to `$seqres.full`. The source has 58 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/606 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/607 -->
# sources/test-tools/xfstests/tests/xfs/607

## Purpose
`sources/test-tools/xfstests/tests/xfs/607` is an XFS fstests shell case focused on extent mapping and exchange. This is a regression test for "xfs: Fix false ENOSPC when performing direct write on a delalloc extent in cow fork". If there is a lot of free space but it is very fragmented, it's possible that a very large delalloc reservation could be created in the CoW fork by a buffered write. If a directio write tries to convert the delalloc reservation to a real extent, it's possible that the allocation will succeed but fail to convert even the first block of the directio write range. In this case, XFS will return ENOSPC even though all it needed to do was to keep converting until the allocator returns ENOSPC or the first block of the direct write got some space. The `_begin_fstest` declaration is `auto quick clone`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/inject`, `./common/preamble`, `./common/reflink`. Local helper surface: `_cleanup`. Requirement and regression gates include `_fixed_by_kernel_commit d62113303d69 "xfs: Fix false ENOSPC when performing direct write on a delalloc extent in cow fork"`, `_require_test_program "punch-alternating"`, `_require_test_reflink`, `_require_xfs_io_error_injection "bmap_alloc_minlen_extent"`, `_require_test_delalloc`. Important external or harness tools detected in the full source include `xfs_io`, `punch-alternating`, `stat`. Scenario variables and harness state referenced include `TEST_DIR`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow uses `xfs_io` commands for writes, fallocate/punch, bmap inspection, scrub, repair, exchange, or media verification. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/607.out`; stable progress/output labels such as `echo "Create source file"`, `echo "Create Reflinked file"`, `echo "Set cowextsize"`, `echo "Fragment FS"`, `echo "Allocate block sized extent from now onwards"`, and 2 more; diagnostic detail appended to `$seqres.full`. The source has 84 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/607 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/608 -->
# sources/test-tools/xfstests/tests/xfs/608

## Purpose
`sources/test-tools/xfstests/tests/xfs/608` is an XFS fstests shell case focused on online repair and scrub. Regression test for V1 inodes that have di_onlink and di_nlink set to 1. The `_begin_fstest` declaration is `auto`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/preamble`. Local helper surface: no local shell helpers beyond the main script body. Requirement and regression gates include `_fixed_by_kernel_commit e21fea4ac3cf "xfs: fix di_onlink checking for V1/V2 inodes",`, `_require_scratch_nocheck	# we'll do our own checking`, `_require_xfs_nocrc`. Important external or harness tools detected in the full source include `xfs_db`, `xfs_repair`, `mkfs.xfs`, `mount`. Scenario variables and harness state referenced include none.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata, runs offline repair or compares offline-repair findings against expected corruption. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/608.out`; diagnostic detail appended to `$seqres.full`. The source has 39 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/608 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/609 -->
# sources/test-tools/xfstests/tests/xfs/609

## Purpose
`sources/test-tools/xfstests/tests/xfs/609` is an XFS fstests shell case focused on stress concurrency, mount-option behavior. Test XFS online growfs log recovery. The `_begin_fstest` declaration is `auto growfs stress shutdown log recoveryloop`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/preamble`. Local helper surface: `_stress_scratch`. Requirement and regression gates include `_require_scratch`, `_require_command "$XFS_GROWFS_PROG" xfs_growfs`. Important external or harness tools detected in the full source include `mkfs.xfs`, `fsstress`, `mount`. Scenario variables and harness state referenced include `SCRATCH_MNT`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, mounts, unmounts, or cycle-mounts to test persistence across remounts, starts fsstress or stress-scrub helpers to exercise concurrency. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; stress timing is intentionally nondeterministic, so regressions may appear as hangs, livelocks, kernel warnings, or post-test fsck failures.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/609.out`; stable progress/output labels such as `echo "*** stressing a ${sizeb} block filesystem" >> $seqres.full`, `echo "*** growing to a ${sizeb} block filesystem" >> $seqres.full`, `echo Silence is golden.`; diagnostic detail appended to `$seqres.full`; hard failures through `_fail` assertions; feature-dependent skips through `_notrun`. The source has 65 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/609 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/610 -->
# sources/test-tools/xfstests/tests/xfs/610

## Purpose
`sources/test-tools/xfstests/tests/xfs/610` is an XFS fstests shell case focused on realtime-device coverage, stress concurrency, mount-option behavior. Test XFS online growfs log recovery. The `_begin_fstest` declaration is `auto growfs stress shutdown log recoveryloop`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/preamble`. Local helper surface: `_stress_scratch`. Requirement and regression gates include `_require_scratch`, `_require_realtime`, `_require_command "$XFS_GROWFS_PROG" xfs_growfs`. Important external or harness tools detected in the full source include `mkfs.xfs`, `fsstress`, `mount`. Scenario variables and harness state referenced include `SCRATCH_MNT`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, mounts, unmounts, or cycle-mounts to test persistence across remounts, starts fsstress or stress-scrub helpers to exercise concurrency. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; stress timing is intentionally nondeterministic, so regressions may appear as hangs, livelocks, kernel warnings, or post-test fsck failures; realtime-device paths depend on allocation unit and feature configuration, so tests skip or change behavior when geometry is unsuitable.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/610.out`; stable progress/output labels such as `echo "*** stressing a ${sizeb} block filesystem" >> $seqres.full`, `echo "*** growing to a ${sizeb} block filesystem" >> $seqres.full`, `echo Silence is golden.`; diagnostic detail appended to `$seqres.full`; hard failures through `_fail` assertions; feature-dependent skips through `_notrun`. The source has 67 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/610 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/612 -->
# sources/test-tools/xfstests/tests/xfs/612

## Purpose
`sources/test-tools/xfstests/tests/xfs/612` is an XFS fstests shell case focused on XFS regression coverage. Check that we can upgrade v5 only features on a v4 file system The `_begin_fstest` declaration is `auto quick`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/preamble`. Local helper surface: no local shell helpers beyond the main script body. Requirement and regression gates include `_require_scratch_xfs_inobtcount`, `_require_command "$XFS_ADMIN_PROG" "xfs_admin"`, `_require_xfs_repair_upgrade inobtcount`, `_require_xfs_nocrc`. Important external or harness tools detected in the full source include `mkfs.xfs`. Scenario variables and harness state referenced include none.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/612.out`; diagnostic detail appended to `$seqres.full`. The source has 31 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/612 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/613 -->
# sources/test-tools/xfstests/tests/xfs/613

## Purpose
`sources/test-tools/xfstests/tests/xfs/613` is an XFS fstests shell case focused on quota enforcement, mount-option behavior. XFS v4 mount options sanity check, refer to 'man 5 xfs'. The `_begin_fstest` declaration is `auto mount prealloc`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/preamble`. Local helper surface: `_cleanup`, `_do_test`, `do_mkfs`, `do_test`, `filter_loop`, `filter_xfs_opt`, `force_unmount`, `get_mount_info`, `is_dev_mounted`. Requirement and regression gates include `_fixed_by_kernel_commit 237d7887ae72 "xfs: show the proper user quota options"`, `_require_xfs_nocrc`, `_require_test`, `_require_loop`, `_require_xfs_io_command "falloc"`. Important external or harness tools detected in the full source include `xfs_io`, `mkfs.xfs`, `findmnt`, `mount`. Scenario variables and harness state referenced include `MKFS_OPTIONS`, `TEST_DIR`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_io` commands for writes, fallocate/punch, bmap inspection, scrub, repair, exchange, or media verification, uses loop devices or configuration variants to cover mount/device geometry. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; quota tests depend on user/group setup, mount options, and stable quota-tools output; loop-device setup must be cleaned reliably to avoid leaked mounts or stale backing files.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/613.out`; stable progress/output labels such as `echo "** create loop device"`, `echo "** create loop mount point"`, `echo "FORMAT: $@" | filter_loop | tee -a $seqres.full`, `echo "[FAILED]: mount $loop_dev $LOOP_MNT $opts"`, `echo "ERROR: expect mount to fail, but it succeeded"`, and 16 more; diagnostic detail appended to `$seqres.full`; hard failures through `_fail` assertions. The source has 180 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/613 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/614 -->
# sources/test-tools/xfstests/tests/xfs/614

## Purpose
`sources/test-tools/xfstests/tests/xfs/614` is an XFS fstests shell case focused on directory tree and parent-pointer repair, mount-option behavior. mkfs concurrency test - ensure the log and agsize scaling works for various concurrency= parameters The `_begin_fstest` declaration is `log metadata auto quick`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/preamble`, `./common/reflink`. Local helper surface: `_cleanup`. Requirement and regression gates include `_require_test`. Important external or harness tools detected in the full source include `mkfs.xfs`. Scenario variables and harness state referenced include `TEST_DIR`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes.

## Test Signals
stable progress/output labels such as `echo "sz $sz cpus $cpus" >> $seqres.full`, `echo "-----------------" >> $seqres.full`, `echo "sz $sz cpus $cpus agcount $agcount logblocks $lblocks"`, `echo "-----------------"`; diagnostic detail appended to `$seqres.full`; feature-dependent skips through `_notrun`. The source has 56 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/614 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/614.cfg -->
# sources/test-tools/xfstests/tests/xfs/614.cfg

## Purpose
`sources/test-tools/xfstests/tests/xfs/614.cfg` is the configuration matrix for the paired XFS fstest. It lists named local block-address geometry variants that the fstests harness can expand into separate test invocations.

## Important APIs, Types, And Functions
This is not executable shell code. Each non-empty line is a config label and argument pair consumed by the fstests runner. The entries are `lba512: lba512`, `lba1024: lba1024`, `lba2048: lba2048`, `lba4096: lba4096`, `lba512_parent: lba512_parent`, `lba1024_parent: lba1024_parent`, `lba2048_parent: lba2048_parent`, `lba4096_parent: lba4096_parent`.

## Control Flow
The file has no internal control flow. The harness reads the labels, schedules the paired test once per entry, and passes the selected geometry option into the test environment.

## State And Persistence Behavior
The file stores static test-variant metadata only. Runtime state is created by the corresponding shell test on scratch devices and is not persisted here.

## Dependencies And Integration Points
It integrates with fstests config-file handling and the adjacent `xfs/614` test. The labels encode logical block address sizes and parent-pointer variants that must remain synchronized with the shell test's option parsing.

## Risks
Stale labels or mismatched option names would silently reduce variant coverage or cause the paired test to skip/fail before reaching filesystem assertions.

## Test Signals
The source has 8 lines and was read completely. Successful reconciliation means every listed config variant is present and the paired shell test can be invoked with each label.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/614.cfg -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/615 -->
# sources/test-tools/xfstests/tests/xfs/615

## Purpose
`sources/test-tools/xfstests/tests/xfs/615` is an XFS fstests shell case focused on extent mapping and exchange, attribute fork repair, mount-option behavior. Verify that XFS does not cause inode fork's extent count to overflow when exchanging ranges between files The `_begin_fstest` declaration is `auto quick collapse fiexchange`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/inject`, `./common/preamble`. Local helper surface: no local shell helpers beyond the main script body. Requirement and regression gates include `_require_scratch`, `_require_xfs_debug`, `_require_xfs_scratch_rmapbt`, `_require_xfs_io_command "fcollapse"`, `_require_xfs_io_command "exchangerange"`, `_require_xfs_io_error_injection "reduce_max_iextents"`. Important external or harness tools detected in the full source include `xfs_io`, `mkfs.xfs`, `mount`. Scenario variables and harness state referenced include `SCRATCH_MNT`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_io` commands for writes, fallocate/punch, bmap inspection, scrub, repair, exchange, or media verification, sets extended attributes or validates attr-fork behavior. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/615.out`; stable progress/output labels such as `echo "* Exchange extent forks"`, `echo "Format and mount fs"`, `echo "Create \$donorfile having an extent of length 67 blocks"`, `echo "Fragment \$donorfile"`, `echo "Create \$srcfile having an extent of length 18 blocks"`, and 9 more; diagnostic detail appended to `$seqres.full`. The source has 87 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/615 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/616 -->
# sources/test-tools/xfstests/tests/xfs/616

## Purpose
`sources/test-tools/xfstests/tests/xfs/616` is an XFS fstests shell case focused on realtime-device coverage, extent mapping and exchange. Make sure that the XFS_EXCHANGE_RANGE_FILE1_WRITTEN actually skips holes and unwritten extents on the data device and the rt device when the rextsize is 1 fsblock. The `_begin_fstest` declaration is `auto fiexchange`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/preamble`. Local helper surface: `swap_and_check_contents`. Requirement and regression gates include `_require_xfs_io_command "falloc"`, `_require_xfs_io_command exchangerange`, `_require_scratch`. Important external or harness tools detected in the full source include `xfs_io`, `mkfs.xfs`, `md5sum`, `mount`. Scenario variables and harness state referenced include `SCRATCH_MNT`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_io` commands for writes, fallocate/punch, bmap inspection, scrub, repair, exchange, or media verification, uses checksum/stat comparisons as the content oracle. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; realtime-device paths depend on allocation unit and feature configuration, so tests skip or change behavior when geometry is unsuitable.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/616.out`; stable progress/output labels such as `echo "swap $tag" >> $seqres.full`, `echo "$a: md5 $a_md5_before -> $a_md5_after in $tag"`, `echo "$b: md5 $b_md5_before -> $b_md5_after in $tag"`, `echo Silence is golden`; diagnostic detail appended to `$seqres.full`; feature-dependent skips through `_notrun`; content/stat comparisons with md5sum or diff. The source has 71 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/616 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/617 -->
# sources/test-tools/xfstests/tests/xfs/617

## Purpose
`sources/test-tools/xfstests/tests/xfs/617` is an XFS fstests shell case focused on realtime-device coverage, extent mapping and exchange. Make sure that the XFS_EXCHANGE_RANGE_FILE1_WRITTEN actually skips holes and unwritten extents on the realtime device when the rextsize is larger than 1 fs block. The `_begin_fstest` declaration is `auto fiexchange`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/preamble`. Local helper surface: `swap_and_check_contents`. Requirement and regression gates include `_require_xfs_io_command "falloc"`, `_require_xfs_io_command exchangerange`, `_require_realtime`, `_require_scratch`. Important external or harness tools detected in the full source include `xfs_io`, `mkfs.xfs`, `md5sum`, `mount`. Scenario variables and harness state referenced include `SCRATCH_MNT`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_io` commands for writes, fallocate/punch, bmap inspection, scrub, repair, exchange, or media verification, uses checksum/stat comparisons as the content oracle. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; realtime-device paths depend on allocation unit and feature configuration, so tests skip or change behavior when geometry is unsuitable.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/617.out`; stable progress/output labels such as `echo "swap $tag" >> $seqres.full`, `echo "$a: md5 $a_md5_before -> $a_md5_after in $tag"`, `echo "$b: md5 $b_md5_before -> $b_md5_after in $tag"`, `echo "$a: md5 $a_md5_after, expected $a_md5_check in $tag" | tee -a $seqres.full`, `echo "$a contents" >> $seqres.full`, and 5 more; diagnostic detail appended to `$seqres.full`; feature-dependent skips through `_notrun`; content/stat comparisons with md5sum or diff. The source has 230 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/617 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/618 -->
# sources/test-tools/xfstests/tests/xfs/618

## Purpose
`sources/test-tools/xfstests/tests/xfs/618` is an XFS fstests shell case focused on directory tree and parent-pointer repair. simple parent pointer test The `_begin_fstest` declaration is `auto quick parent`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/parent`, `./common/preamble`. Local helper surface: no local shell helpers beyond the main script body. Requirement and regression gates include `_require_scratch`, `_require_xfs_sysfs debug/larp`, `_require_xfs_parent`, `_require_xfs_io_command "parent"`. Important external or harness tools detected in the full source include `xfs_io`, `mkfs.xfs`, `mount`, `stat`. Scenario variables and harness state referenced include `SCRATCH_MNT`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_io` commands for writes, fallocate/punch, bmap inspection, scrub, repair, exchange, or media verification, uses checksum/stat comparisons as the content oracle. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/618.out`; stable progress/output labels such as `echo ""`, `echo ""`, `echo ""`, `echo ""`, `echo ""`, and 4 more; diagnostic detail appended to `$seqres.full`; hard failures through `_fail` assertions; post-test filesystem validation. The source has 114 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/618 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/619 -->
# sources/test-tools/xfstests/tests/xfs/619

## Purpose
`sources/test-tools/xfstests/tests/xfs/619` is an XFS fstests shell case focused on directory tree and parent-pointer repair. multi link parent pointer test The `_begin_fstest` declaration is `auto quick parent`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/parent`, `./common/preamble`. Local helper surface: no local shell helpers beyond the main script body. Requirement and regression gates include `_require_scratch`, `_require_xfs_sysfs debug/larp`, `_require_xfs_parent`, `_require_xfs_io_command "parent"`. Important external or harness tools detected in the full source include `mkfs.xfs`, `mount`, `stat`. Scenario variables and harness state referenced include `SCRATCH_MNT`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, mounts, unmounts, or cycle-mounts to test persistence across remounts, uses checksum/stat comparisons as the content oracle. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/619.out`; stable progress/output labels such as `echo ""`; diagnostic detail appended to `$seqres.full`; hard failures through `_fail` assertions; post-test filesystem validation. The source has 67 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/619 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/620 -->
# sources/test-tools/xfstests/tests/xfs/620

## Purpose
`sources/test-tools/xfstests/tests/xfs/620` is an XFS fstests shell case focused on directory tree and parent-pointer repair, attribute fork repair, dump/restore behavior. parent pointer inject test The `_begin_fstest` declaration is `auto quick parent`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/inject`, `./common/parent`, `./common/preamble`. Local helper surface: no local shell helpers beyond the main script body. Requirement and regression gates include `_require_scratch`, `_require_xfs_sysfs debug/larp`, `_require_xfs_io_error_injection "larp"`, `_require_xfs_parent`, `_require_xfs_io_command "parent"`. Important external or harness tools detected in the full source include `mkfs.xfs`, `mount`. Scenario variables and harness state referenced include `SCRATCH_MNT`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, mounts, unmounts, or cycle-mounts to test persistence across remounts, sets extended attributes or validates attr-fork behavior. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/620.out`; stable progress/output labels such as `echo ""`; diagnostic detail appended to `$seqres.full`; hard failures through `_fail` assertions; post-test filesystem validation. The source has 86 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/620 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/621 -->
# sources/test-tools/xfstests/tests/xfs/621

## Purpose
`sources/test-tools/xfstests/tests/xfs/621` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair, directory tree and parent-pointer repair, stress concurrency. Race fsstress and directory tree structure corruption detector for a while to see if we crash or livelock. The `_begin_fstest` declaration is `scrub fsstress_scrub`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/inject`, `./common/preamble`, `./common/xfs`. Local helper surface: `_cleanup`. Requirement and regression gates include `_require_scratch`, `_require_xfs_stress_scrub`. Important external or harness tools detected in the full source include `mkfs.xfs`, `fsstress`, `mount`. Scenario variables and harness state referenced include none.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata, runs online scrub/repair or xfs_scrub in selected modes, starts fsstress or stress-scrub helpers to exercise concurrency. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version; stress timing is intentionally nondeterministic, so regressions may appear as hangs, livelocks, kernel warnings, or post-test fsck failures.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/621.out`; stable progress/output labels such as `echo Silence is golden`; diagnostic detail appended to `$seqres.full`. The source has 36 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/621 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/622 -->
# sources/test-tools/xfstests/tests/xfs/622

## Purpose
`sources/test-tools/xfstests/tests/xfs/622` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair, directory tree and parent-pointer repair, stress concurrency. Race fsstress and directory tree structure repair for a while to see if we crash or livelock. The `_begin_fstest` declaration is `online_repair fsstress_online_repair`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/inject`, `./common/preamble`, `./common/xfs`. Local helper surface: `_cleanup`. Requirement and regression gates include `_require_scratch`, `_require_xfs_stress_online_repair`. Important external or harness tools detected in the full source include `mkfs.xfs`, `fsstress`, `mount`. Scenario variables and harness state referenced include none.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata, runs online scrub/repair or xfs_scrub in selected modes, starts fsstress or stress-scrub helpers to exercise concurrency. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version; stress timing is intentionally nondeterministic, so regressions may appear as hangs, livelocks, kernel warnings, or post-test fsck failures.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/622.out`; stable progress/output labels such as `echo Silence is golden`; diagnostic detail appended to `$seqres.full`. The source has 36 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/622 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/623 -->
# sources/test-tools/xfstests/tests/xfs/623

## Purpose
`sources/test-tools/xfstests/tests/xfs/623` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair, directory tree and parent-pointer repair, stress concurrency, mount-option behavior. Functional testing for online fsck of a directory loop that is not accessible from the root directory. The `_begin_fstest` declaration is `auto online_repair`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/inject`, `./common/populate`, `./common/preamble`. Local helper surface: `prepare_fs`, `simple_online_repair`. Requirement and regression gates include `_require_scrub`, `_require_xfs_db_command "link"`, `_require_xfs_db_command "unlink"`, `_require_scratch`, `_require_xfs_stress_online_repair`. Important external or harness tools detected in the full source include `xfs_io`, `xfs_db`, `mkfs.xfs`, `xfs_scrub`, `mount`, `stat`. Scenario variables and harness state referenced include `SCRATCH_MNT`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_io` commands for writes, fallocate/punch, bmap inspection, scrub, repair, exchange, or media verification, uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata, runs online scrub/repair or xfs_scrub in selected modes, uses checksum/stat comparisons as the content oracle. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/623.out`; stable progress/output labels such as `echo "root: $root_inum; a: $a_inum; b: $b_inum; c: $c_inum" >> $seqres.full`, `echo "check root"`, `echo "check A"`, `echo "check B"`, `echo "check C"`, and 9 more; diagnostic detail appended to `$seqres.full`; post-test filesystem validation. The source has 119 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/623 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/624 -->
# sources/test-tools/xfstests/tests/xfs/624

## Purpose
`sources/test-tools/xfstests/tests/xfs/624` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair, directory tree and parent-pointer repair, stress concurrency, mount-option behavior. Functional testing for online fsck of a directory loop that is accessible from the root directory. The `_begin_fstest` declaration is `auto online_repair`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/inject`, `./common/populate`, `./common/preamble`. Local helper surface: `prepare_fs`, `simple_online_repair`. Requirement and regression gates include `_require_scrub`, `_require_xfs_db_command "link"`, `_require_xfs_db_command "unlink"`, `_require_scratch`, `_require_xfs_stress_online_repair`. Important external or harness tools detected in the full source include `xfs_io`, `xfs_db`, `mkfs.xfs`, `xfs_scrub`, `mount`, `stat`. Scenario variables and harness state referenced include `SCRATCH_MNT`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_io` commands for writes, fallocate/punch, bmap inspection, scrub, repair, exchange, or media verification, uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata, runs online scrub/repair or xfs_scrub in selected modes, uses checksum/stat comparisons as the content oracle. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/624.out`; stable progress/output labels such as `echo "root: $root_inum; a: $a_inum; b: $b_inum; c: $c_inum; d: $d_inum" >> $seqres.full`, `echo "check root"`, `echo "check A"`, `echo "check B"`, `echo "check C"`, and 13 more; diagnostic detail appended to `$seqres.full`; post-test filesystem validation. The source has 130 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/624 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/625 -->
# sources/test-tools/xfstests/tests/xfs/625

## Purpose
`sources/test-tools/xfstests/tests/xfs/625` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair, directory tree and parent-pointer repair, stress concurrency. Functional testing for online fsck of a directory chain that is not accessible from the root directory. The `_begin_fstest` declaration is `auto online_repair`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/inject`, `./common/populate`, `./common/preamble`. Local helper surface: `prepare_fs`, `simple_online_repair`. Requirement and regression gates include `_require_scrub`, `_require_xfs_db_command "link"`, `_require_xfs_db_command "unlink"`, `_require_scratch`, `_require_xfs_stress_online_repair`. Important external or harness tools detected in the full source include `xfs_io`, `xfs_db`, `mkfs.xfs`, `xfs_scrub`, `mount`, `stat`. Scenario variables and harness state referenced include `SCRATCH_MNT`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_io` commands for writes, fallocate/punch, bmap inspection, scrub, repair, exchange, or media verification, uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata, runs online scrub/repair or xfs_scrub in selected modes, uses checksum/stat comparisons as the content oracle. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/625.out`; stable progress/output labels such as `echo "root: $root_inum; a: $a_inum; b: $b_inum; c: $c_inum" >> $seqres.full`, `echo "check root"`, `echo "check A"`, `echo "check B"`, `echo "check C"`, and 10 more; diagnostic detail appended to `$seqres.full`; post-test filesystem validation. The source has 118 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/625 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/626 -->
# sources/test-tools/xfstests/tests/xfs/626

## Purpose
`sources/test-tools/xfstests/tests/xfs/626` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair, directory tree and parent-pointer repair, stress concurrency. Functional testing for online fsck of a multiply-owned directory that is accessible from the root directory. The `_begin_fstest` declaration is `auto online_repair`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/inject`, `./common/populate`, `./common/preamble`. Local helper surface: `prepare_fs`, `simple_online_repair`. Requirement and regression gates include `_require_scrub`, `_require_xfs_db_command "link"`, `_require_xfs_db_command "unlink"`, `_require_scratch`, `_require_xfs_stress_online_repair`. Important external or harness tools detected in the full source include `xfs_io`, `xfs_db`, `mkfs.xfs`, `xfs_scrub`, `mount`, `stat`. Scenario variables and harness state referenced include `SCRATCH_MNT`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_io` commands for writes, fallocate/punch, bmap inspection, scrub, repair, exchange, or media verification, uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata, runs online scrub/repair or xfs_scrub in selected modes, uses checksum/stat comparisons as the content oracle. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/626.out`; stable progress/output labels such as `echo "root: $root_inum; a: $a_inum; b: $b_inum; c: $c_inum; d: $d_inum" >> $seqres.full`, `echo "root: $root_inum; z: $z_inum; y: $y_inum" >> $seqres.full`, `echo "check root"`, `echo "check A"`, `echo "check B"`, and 20 more; diagnostic detail appended to `$seqres.full`; post-test filesystem validation. The source has 154 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/626 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/627 -->
# sources/test-tools/xfstests/tests/xfs/627

## Purpose
`sources/test-tools/xfstests/tests/xfs/627` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair, directory tree and parent-pointer repair, stress concurrency, mount-option behavior. Functional testing for online fsck of a directory loop that is inaccessible from the root directory and has subdirectories. The `_begin_fstest` declaration is `auto online_repair`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/inject`, `./common/populate`, `./common/preamble`. Local helper surface: `prepare_fs`, `simple_online_repair`. Requirement and regression gates include `_require_scrub`, `_require_xfs_db_command "link"`, `_require_xfs_db_command "unlink"`, `_require_scratch`, `_require_xfs_stress_online_repair`. Important external or harness tools detected in the full source include `xfs_io`, `xfs_db`, `mkfs.xfs`, `xfs_scrub`, `mount`, `stat`. Scenario variables and harness state referenced include `SCRATCH_MNT`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_io` commands for writes, fallocate/punch, bmap inspection, scrub, repair, exchange, or media verification, uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata, runs online scrub/repair or xfs_scrub in selected modes, uses checksum/stat comparisons as the content oracle. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/627.out`; stable progress/output labels such as `echo "root: $root_inum; a: $a_inum; b: $b_inum; c: $c_inum; d: $d_inum; e: $e_inum" >> $seqres.full`, `echo "check root"`, `echo "check A"`, `echo "check B"`, `echo "check C"`, and 16 more; diagnostic detail appended to `$seqres.full`; post-test filesystem validation. The source has 143 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/627 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/628 -->
# sources/test-tools/xfstests/tests/xfs/628

## Purpose
`sources/test-tools/xfstests/tests/xfs/628` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair, directory tree and parent-pointer repair, unlinked-inode repair, stress concurrency, mount-option behavior. Race rename and directory tree structure corruption detector for a while to exercise the dirtree code's directory path invalidation and its ability to handle unlinked directories. The `_begin_fstest` declaration is `scrub fsstress_scrub`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/inject`, `./common/preamble`, `./common/xfs`. Local helper surface: `renamer`. Requirement and regression gates include `_require_scrub`, `_require_scratch`, `_require_xfs_stress_scrub`. Important external or harness tools detected in the full source include `xfs_io`, `mkfs.xfs`, `xfs_scrub`, `fsstress`, `mount`, `stat`. Scenario variables and harness state referenced include `XFS_SCRUB_PHASE`, `SCRATCH_MNT`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_io` commands for writes, fallocate/punch, bmap inspection, scrub, repair, exchange, or media verification, uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata, runs online scrub/repair or xfs_scrub in selected modes, starts fsstress or stress-scrub helpers to exercise concurrency, uses checksum/stat comparisons as the content oracle. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version; stress timing is intentionally nondeterministic, so regressions may appear as hangs, livelocks, kernel warnings, or post-test fsck failures.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/628.out`; stable progress/output labels such as `echo Silence is golden`; diagnostic detail appended to `$seqres.full`. The source has 77 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/628 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/629 -->
# sources/test-tools/xfstests/tests/xfs/629

## Purpose
`sources/test-tools/xfstests/tests/xfs/629` is an XFS fstests shell case focused on XFS regression coverage. Post-EOF preallocation defeat test for O_SYNC buffered I/O. The `_begin_fstest` declaration is `prealloc rw`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/preamble`. Local helper surface: `_cleanup`, `write_sync_file`. Requirement and regression gates include `_require_scratch`, `_require_xfs_io_command "fiemap"`. Important external or harness tools detected in the full source include `xfs_io`, `mkfs.xfs`, `mount`. Scenario variables and harness state referenced include `SCRATCH_MNT`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_io` commands for writes, fallocate/punch, bmap inspection, scrub, repair, exchange, or media verification. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/629.out`; diagnostic detail appended to `$seqres.full`. The source has 67 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/629 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/630 -->
# sources/test-tools/xfstests/tests/xfs/630

## Purpose
`sources/test-tools/xfstests/tests/xfs/630` is an XFS fstests shell case focused on XFS regression coverage. Post-EOF preallocation defeat test for buffered I/O with extent size hints. The `_begin_fstest` declaration is `prealloc rw`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/preamble`. Local helper surface: `_cleanup`, `write_extsz_file`. Requirement and regression gates include `_require_scratch`, `_require_xfs_io_command "fiemap"`, `_require_xfs_io_command "extsize"`. Important external or harness tools detected in the full source include `xfs_io`, `mkfs.xfs`, `mount`. Scenario variables and harness state referenced include `SCRATCH_MNT`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_io` commands for writes, fallocate/punch, bmap inspection, scrub, repair, exchange, or media verification. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/630.out`; diagnostic detail appended to `$seqres.full`. The source has 70 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/630 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/631 -->
# sources/test-tools/xfstests/tests/xfs/631

## Purpose
`sources/test-tools/xfstests/tests/xfs/631` is an XFS fstests shell case focused on XFS regression coverage. Post-EOF preallocation defeat test for direct I/O with extent size hints. The `_begin_fstest` declaration is `prealloc rw unreliable_in_parallel`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/preamble`. Local helper surface: `_cleanup`, `write_direct_file`. Requirement and regression gates include `_require_scratch`, `_require_xfs_io_command "fiemap"`, `_require_xfs_io_command "extsize"`. Important external or harness tools detected in the full source include `xfs_io`, `mkfs.xfs`, `mount`. Scenario variables and harness state referenced include `SCRATCH_MNT`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_io` commands for writes, fallocate/punch, bmap inspection, scrub, repair, exchange, or media verification. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/631.out`; diagnostic detail appended to `$seqres.full`. The source has 75 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/631 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/632 -->
# sources/test-tools/xfstests/tests/xfs/632

## Purpose
`sources/test-tools/xfstests/tests/xfs/632` is an XFS fstests shell case focused on XFS regression coverage. Post-EOF preallocation defeat test with O_SYNC buffered I/O that repeatedly closes and reopens the files. The `_begin_fstest` declaration is `prealloc rw`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/preamble`. Local helper surface: `_cleanup`, `read_file`, `write_file`. Requirement and regression gates include `_require_scratch`, `_require_xfs_io_command "fiemap"`. Important external or harness tools detected in the full source include `xfs_io`, `mkfs.xfs`, `mount`. Scenario variables and harness state referenced include `SCRATCH_MNT`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_io` commands for writes, fallocate/punch, bmap inspection, scrub, repair, exchange, or media verification. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/632.out`; diagnostic detail appended to `$seqres.full`. The source has 78 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/632 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/633 -->
# sources/test-tools/xfstests/tests/xfs/633

## Purpose
`sources/test-tools/xfstests/tests/xfs/633` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair, stress concurrency, dump/restore behavior. Populate a XFS filesystem, ensure that rdump can "recover" the contents to another directory, and compare the contents. The `_begin_fstest` declaration is `auto scrub`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/populate`, `./common/preamble`. Local helper surface: `_cleanup`, `cmp_md5`, `cmp_stat`, `cmp_stat_dir`, `cmp_stat_files`, `make_md5`, `make_stat`, `make_stat_dir`, `make_stat_files`. Requirement and regression gates include `_require_xfs_db_command "rdump"`, `_require_test`, `_require_scratch`, `_require_scrub`, `_require_populate_commands`. Important external or harness tools detected in the full source include `xfs_db`, `md5sum`, `fsstress`, `mount`, `stat`. Scenario variables and harness state referenced include `TEST_DIR`, `SCRATCH_MNT`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata, starts fsstress or stress-scrub helpers to exercise concurrency, uses checksum/stat comparisons as the content oracle. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version; stress timing is intentionally nondeterministic, so regressions may appear as hangs, livelocks, kernel warnings, or post-test fsck failures.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/633.out`; stable progress/output labels such as `echo "Format and populate"`, `echo "Recover filesystem"`, `echo "Check file contents"`, `echo "Check selected files contents"`, `echo "Check single dir extraction contents"`; diagnostic detail appended to `$seqres.full`; content/stat comparisons with md5sum or diff. The source has 153 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/633 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/634 -->
# sources/test-tools/xfstests/tests/xfs/634

## Purpose
`sources/test-tools/xfstests/tests/xfs/634` is an XFS fstests shell case focused on XFS regression coverage. Regression test for mount time accounting of an open zone with freed blocks. The `_begin_fstest` declaration is `auto quick zone`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/preamble`. Local helper surface: no local shell helpers beyond the main script body. Requirement and regression gates include `_require_scratch`, `_require_odirect`. Important external or harness tools detected in the full source include `mkfs.xfs`, `mount`. Scenario variables and harness state referenced include `SCRATCH_MNT`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, mounts, unmounts, or cycle-mounts to test persistence across remounts. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/634.out`; stable progress/output labels such as `echo "Check that df output matches after remount"`; diagnostic detail appended to `$seqres.full`; content/stat comparisons with md5sum or diff. The source has 40 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/634 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/635 -->
# sources/test-tools/xfstests/tests/xfs/635

## Purpose
`sources/test-tools/xfstests/tests/xfs/635` is an XFS fstests shell case focused on realtime-device coverage. growfs QA tests - repeatedly fill/grow the rt volume of the filesystem check the filesystem contents after each operation. This is the zoned equivalent of xfs/596 The `_begin_fstest` declaration is `growfs ioctl auto zone`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/preamble`, `./common/zoned`. Local helper surface: `_cleanup`, `fill_fs`. Requirement and regression gates include `_require_scratch`, `_require_realtime`, `_require_no_large_scratch_dev`, `_require_xfs_scratch_zoned`. Important external or harness tools detected in the full source include `mkfs.xfs`, `mount`. Scenario variables and harness state referenced include `SCRATCH_MNT`, `SCRATCH_DEV`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, mounts, unmounts, or cycle-mounts to test persistence across remounts. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; realtime-device paths depend on allocation unit and feature configuration, so tests skip or change behavior when geometry is unsuitable.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/635.out`; stable progress/output labels such as `echo -n "Make rt filesystem on SCRATCH_DEV and mount... "`, `echo "done"`, `echo -n "Flush filesystem... "`, `echo "done"`, `echo -n "Check files... "`, and 3 more; diagnostic detail appended to `$seqres.full`. The source has 78 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/635 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/636 -->
# sources/test-tools/xfstests/tests/xfs/636

## Purpose
`sources/test-tools/xfstests/tests/xfs/636` is an XFS fstests shell case focused on realtime-device coverage. Ensure that direct I/O writes are not pointlessly reordered on zoned devices. The `_begin_fstest` declaration is `quick auto rw zone`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/preamble`, `./common/zoned`. Local helper surface: no local shell helpers beyond the main script body. Requirement and regression gates include `_require_scratch`, `_require_realtime`, `_require_xfs_scratch_zoned`. Important external or harness tools detected in the full source include `mkfs.xfs`, `mount`. Scenario variables and harness state referenced include `SCRATCH_MNT`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, mounts, unmounts, or cycle-mounts to test persistence across remounts. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; realtime-device paths depend on allocation unit and feature configuration, so tests skip or change behavior when geometry is unsuitable.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/636.out`; stable progress/output labels such as `echo "Check extent counts"`, `echo "number of extents: $extents"`. The source has 37 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/636 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/637 -->
# sources/test-tools/xfstests/tests/xfs/637

## Purpose
`sources/test-tools/xfstests/tests/xfs/637` is an XFS fstests shell case focused on XFS regression coverage. Check that trying to grow a data device followed by the internal RT device fails gracefully with EINVAL. The `_begin_fstest` declaration is `quick auto growfs ioctl zone`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/preamble`. Local helper surface: no local shell helpers beyond the main script body. Requirement and regression gates include `_require_scratch`, `_require_zoned_device $SCRATCH_DEV`. Important external or harness tools detected in the full source include `mkfs.xfs`, `mount`. Scenario variables and harness state referenced include `SCRATCH_MNT`, `SCRATCH_DEV`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, mounts, unmounts, or cycle-mounts to test persistence across remounts. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/637.out`; stable progress/output labels such as `echo "Creating file system"`, `echo "Trying to grow file system (should fail)"`; diagnostic detail appended to `$seqres.full`. The source has 24 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/637 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/638 -->
# sources/test-tools/xfstests/tests/xfs/638

## Purpose
`sources/test-tools/xfstests/tests/xfs/638` is an XFS fstests shell case focused on extent mapping and exchange. Test data placement by write hints. The `_begin_fstest` declaration is `auto rw zone`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/preamble`, `./common/xfs`. Local helper surface: `test_placement`. Requirement and regression gates include `_require_scratch`, `_require_xfs_scratch_zoned 3`. Important external or harness tools detected in the full source include `xfs_io`, `mkfs.xfs`, `mount`. Scenario variables and harness state referenced include `SCRATCH_MNT`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_io` commands for writes, fallocate/punch, bmap inspection, scrub, repair, exchange, or media verification. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/638.out`; stable progress/output labels such as `echo "short RG mismatch for file $i: $short_rg/$rg"`, `echo "medium rg == short_rg"`, `echo "medium RG mismatch for file $i: $medium_rg/$rg"`, `echo "long file $i placed into short RG "`, `echo "long file $i placed into medium RG"`, and 3 more; diagnostic detail appended to `$seqres.full`. The source has 90 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/638 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/639 -->
# sources/test-tools/xfstests/tests/xfs/639

## Purpose
`sources/test-tools/xfstests/tests/xfs/639` is an XFS fstests shell case focused on extent mapping and exchange. Test that data is packed tighly for writeback after the files were closed. The `_begin_fstest` declaration is `auto quick rw zone`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/preamble`, `./common/xfs`. Local helper surface: no local shell helpers beyond the main script body. Requirement and regression gates include `_require_scratch`, `_require_xfs_scratch_zoned`. Important external or harness tools detected in the full source include `xfs_io`, `mkfs.xfs`, `mount`. Scenario variables and harness state referenced include `SCRATCH_MNT`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_io` commands for writes, fallocate/punch, bmap inspection, scrub, repair, exchange, or media verification. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/639.out`; stable progress/output labels such as `echo "RG mismatch for file $i: $short_rg/$rg"`; diagnostic detail appended to `$seqres.full`. The source has 41 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/639 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/640 -->
# sources/test-tools/xfstests/tests/xfs/640

## Purpose
`sources/test-tools/xfstests/tests/xfs/640` is an XFS fstests shell case focused on extent mapping and exchange. Test that multiple direct I/O write streams are directed to separate zones. The `_begin_fstest` declaration is `quick auto rw zone`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/preamble`, `./common/xfs`. Local helper surface: no local shell helpers beyond the main script body. Requirement and regression gates include `_require_scratch`, `_require_odirect`, `_require_aio`, `_require_xfs_scratch_zoned 3`, `_require_fio $fio_config`. Important external or harness tools detected in the full source include `mkfs.xfs`, `mount`. Scenario variables and harness state referenced include `SCRATCH_MNT`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, mounts, unmounts, or cycle-mounts to test persistence across remounts. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/640.out`; stable progress/output labels such as `echo "number of file 1 extents: $extents1"`, `echo "number of file 2 extents: $extents2"`, `echo "same RG used for both files"`; diagnostic detail appended to `$seqres.full`. The source has 65 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/640 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/641 -->
# sources/test-tools/xfstests/tests/xfs/641

## Purpose
`sources/test-tools/xfstests/tests/xfs/641` is an XFS fstests shell case focused on extent mapping and exchange. Test that multiple buffered I/O write streams are directed to separate zones when written back with the file still open. The `_begin_fstest` declaration is `quick auto rw zone`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/preamble`, `./common/xfs`. Local helper surface: no local shell helpers beyond the main script body. Requirement and regression gates include `_require_scratch`, `_require_odirect`, `_require_aio`, `_require_xfs_scratch_zoned 3`, `_require_fio $fio_config`. Important external or harness tools detected in the full source include `mkfs.xfs`, `mount`. Scenario variables and harness state referenced include `SCRATCH_MNT`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, mounts, unmounts, or cycle-mounts to test persistence across remounts. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/641.out`; stable progress/output labels such as `echo "number of file 1 extents: $extents1"`, `echo "number of file 2 extents: $extents2"`, `echo "same RG used for both files"`; diagnostic detail appended to `$seqres.full`. The source has 65 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/641 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/642 -->
# sources/test-tools/xfstests/tests/xfs/642

## Purpose
`sources/test-tools/xfstests/tests/xfs/642` is an XFS fstests shell case focused on XFS regression coverage. Test that multiple parallel writers can't accidentally dip into the reserved space pool. The `_begin_fstest` declaration is `quick auto rw zone enospc`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/preamble`, `./common/zoned`. Local helper surface: no local shell helpers beyond the main script body. Requirement and regression gates include `_require_scratch`, `_require_odirect`, `_require_aio`, `_require_xfs_scratch_zoned`, `_require_fio $fio_config`. Important external or harness tools detected in the full source include `mkfs.xfs`, `mount`. Scenario variables and harness state referenced include `MOUNT_OPTIONS`, `SCRATCH_MNT`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, mounts, unmounts, or cycle-mounts to test persistence across remounts. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/642.out`; diagnostic detail appended to `$seqres.full`; hard failures through `_fail` assertions; feature-dependent skips through `_notrun`. The source has 85 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/642 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/643 -->
# sources/test-tools/xfstests/tests/xfs/643

## Purpose
`sources/test-tools/xfstests/tests/xfs/643` is an XFS fstests shell case focused on XFS regression coverage. Test that GC defragments sequentially written files. The `_begin_fstest` declaration is `auto rw zone`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/preamble`, `./common/zoned`. Local helper surface: no local shell helpers beyond the main script body. Requirement and regression gates include `_require_scratch`, `_require_odirect`, `_require_aio`, `_require_xfs_scratch_zoned`, `_require_fio $fio_config`. Important external or harness tools detected in the full source include `xfs_io`, `mkfs.xfs`, `mount`. Scenario variables and harness state referenced include `MOUNT_OPTIONS`, `SCRATCH_MNT`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_io` commands for writes, fallocate/punch, bmap inspection, scrub, repair, exchange, or media verification. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/643.out`; stable progress/output labels such as `echo "number of file 2 extents: $extents2" >>$seqres.full`, `echo "number of file 4 extents: $extents4" >>$seqres.full`, `echo "number of file 6 extents: $extents6" >>$seqres.full`, `echo "number of file 8 extents: $extents8" >>$seqres.full`; diagnostic detail appended to `$seqres.full`; hard failures through `_fail` assertions; feature-dependent skips through `_notrun`. The source has 119 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/643 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/644 -->
# sources/test-tools/xfstests/tests/xfs/644

## Purpose
`sources/test-tools/xfstests/tests/xfs/644` is an XFS fstests shell case focused on XFS regression coverage. Test that GC defragments randomly written files. The `_begin_fstest` declaration is `auto rw zone`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/preamble`, `./common/zoned`. Local helper surface: no local shell helpers beyond the main script body. Requirement and regression gates include `_require_scratch`, `_require_odirect`, `_require_aio`, `_require_xfs_scratch_zoned`, `_require_fio $fio_config`. Important external or harness tools detected in the full source include `xfs_io`, `mkfs.xfs`, `mount`. Scenario variables and harness state referenced include `MOUNT_OPTIONS`, `SCRATCH_MNT`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_io` commands for writes, fallocate/punch, bmap inspection, scrub, repair, exchange, or media verification. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/644.out`; stable progress/output labels such as `echo "number of file 2 extents: $extents2" >>$seqres.full`, `echo "number of file 4 extents: $extents4" >>$seqres.full`, `echo "number of file 6 extents: $extents6" >>$seqres.full`, `echo "number of file 8 extents: $extents8" >>$seqres.full`; diagnostic detail appended to `$seqres.full`; hard failures through `_fail` assertions; feature-dependent skips through `_notrun`. The source has 124 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/644 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/645 -->
# sources/test-tools/xfstests/tests/xfs/645

## Purpose
`sources/test-tools/xfstests/tests/xfs/645` is an XFS fstests shell case focused on online repair and scrub. Regression test for xfs_repair messing up the per-zone used counter. The `_begin_fstest` declaration is `auto quick zone repair`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/preamble`. Local helper surface: no local shell helpers beyond the main script body. Requirement and regression gates include `_require_scratch`, `_require_odirect`. Important external or harness tools detected in the full source include `xfs_repair`, `mkfs.xfs`, `mount`. Scenario variables and harness state referenced include `SCRATCH_MNT`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, mounts, unmounts, or cycle-mounts to test persistence across remounts, runs offline repair or compares offline-repair findings against expected corruption. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/645.out`; stable progress/output labels such as `echo "Repairing"`, `echo "Removing file after repair"`; diagnostic detail appended to `$seqres.full`. The source has 32 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/645 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/646 -->
# sources/test-tools/xfstests/tests/xfs/646

## Purpose
`sources/test-tools/xfstests/tests/xfs/646` is an XFS fstests shell case focused on XFS regression coverage. Ensure that a truncate that needs to zero the EOFblock doesn't get ENOSPC when another thread is waiting for space to become available through GC. The `_begin_fstest` declaration is `auto rw zone`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/preamble`, `./common/zoned`. Local helper surface: no local shell helpers beyond the main script body. Requirement and regression gates include `_require_scratch`, `_require_xfs_scratch_zoned`. Important external or harness tools detected in the full source include `xfs_io`, `mkfs.xfs`, `mount`. Scenario variables and harness state referenced include `SCRATCH_MNT`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_io` commands for writes, fallocate/punch, bmap inspection, scrub, repair, exchange, or media verification. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/646.out`; diagnostic detail appended to `$seqres.full`. The source has 37 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/646 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/647 -->
# sources/test-tools/xfstests/tests/xfs/647

## Purpose
`sources/test-tools/xfstests/tests/xfs/647` is an XFS fstests shell case focused on realtime-device coverage. Test that we can gracefully handle spurious zone write pointer advancements while unmounted. The `_begin_fstest` declaration is `auto quick zone`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/preamble`, `./common/zoned`. Local helper surface: no local shell helpers beyond the main script body. Requirement and regression gates include `_require_scratch`, `_require_realtime`, `_require_zoned_device $zdev`, `_require_command "$BLKZONE_PROG" blkzone`. Important external or harness tools detected in the full source include `mkfs.xfs`, `mount`. Scenario variables and harness state referenced include `SCRATCH_MNT`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, mounts, unmounts, or cycle-mounts to test persistence across remounts. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; realtime-device paths depend on allocation unit and feature configuration, so tests skip or change behavior when geometry is unsuitable.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/647.out`; stable progress/output labels such as `echo "Number of open zones: $nr_open"`; diagnostic detail appended to `$seqres.full`; hard failures through `_fail` assertions. The source has 63 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/647 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/648 -->
# sources/test-tools/xfstests/tests/xfs/648

## Purpose
`sources/test-tools/xfstests/tests/xfs/648` is an XFS fstests shell case focused on quota enforcement. Test that XFS can set quota project ID on special files The `_begin_fstest` declaration is `auto quota`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/preamble`, `./common/quota`. Local helper surface: `create_af_unix`, `filter_quota`. Requirement and regression gates include `_require_scratch`, `_require_xfs_quota`, `_require_test_program "af_unix"`, `_require_test_program "file_attr"`, `_require_symlinks`, `_require_mknod`, `_require_file_attr`, `_require_file_attr_special`. Important external or harness tools detected in the full source include `mkfs.xfs`, `xfs_quota`, `mount`. Scenario variables and harness state referenced include `SCRATCH_MNT`, `SCRATCH_DEV`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, mounts, unmounts, or cycle-mounts to test persistence across remounts, sets up quota state and validates accounting or enforcement. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; quota tests depend on user/group setup, mount options, and stable quota-tools output.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/648.out`; diagnostic detail appended to `$seqres.full`. The source has 74 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/648 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/649 -->
# sources/test-tools/xfstests/tests/xfs/649

## Purpose
`sources/test-tools/xfstests/tests/xfs/649` is an XFS fstests shell case focused on extent mapping and exchange, attribute fork repair, dump/restore behavior. Regression test for panic following IO error when reading extended attribute blocks The `_begin_fstest` declaration is `auto quick attr`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/attr`, `./common/preamble`, `./common/scsi_debug`. Local helper surface: `_cleanup`, `test_attr`. Requirement and regression gates include `_fixed_by_kernel_commit ae668cd567a6 "xfs: do not propagate ENODATA disk errors into xattr code"`, `_require_scratch_nocheck`, `_require_scsi_debug "medium_error_start"`, `_require_attrs user`. Important external or harness tools detected in the full source include `xfs_io`, `xfs_db`, `mkfs.xfs`, `setfattr`, `mount`, `stat`. Scenario variables and harness state referenced include `MOUNT_OPTIONS`, `SCRATCH_MNT`, `SCRATCH_DEV`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_io` commands for writes, fallocate/punch, bmap inspection, scrub, repair, exchange, or media verification, uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata, sets extended attributes or validates attr-fork behavior, uses checksum/stat comparisons as the content oracle. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/649.out`; stable progress/output labels such as `echo "SCSI debug device $scsi_debug_dev" >>$seqres.full`, `echo Block size $block_size >> $seqres.full`, `echo Inode size $inode_size >> $seqres.full`, `echo $scsi_debug_opt_noerror > /sys/module/scsi_debug/parameters/opts`, `echo -e "\nTesting : $test" >> $seqres.full`, and 10 more; diagnostic detail appended to `$seqres.full`; feature-dependent skips through `_notrun`. The source has 140 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/649 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/650 -->
# sources/test-tools/xfstests/tests/xfs/650

## Purpose
`sources/test-tools/xfstests/tests/xfs/650` is an XFS fstests shell case focused on realtime-device coverage. ! /bin/bash Test commit 0c4da70c83d4 ("xfs: fix realtime file data space leak") and 69ffe5960df1 ("xfs: don't check for AG deadlock for realtime files in bunmapi"). On XFS without the fixes, truncate will hang forever. The `_begin_fstest` declaration is `auto prealloc preallocrw realtime`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/preamble`. Local helper surface: no local shell helpers beyond the main script body. Requirement and regression gates include `_require_realtime`, `_require_xfs_io_command "falloc"`, `_require_fs_space "$SCRATCH_MNT" $((filesz / 1024))`. Important external or harness tools detected in the full source include `xfs_io`, `mkfs.xfs`, `mount`. Scenario variables and harness state referenced include `SCRATCH_MNT`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_io` commands for writes, fallocate/punch, bmap inspection, scrub, repair, exchange, or media verification. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; realtime-device paths depend on allocation unit and feature configuration, so tests skip or change behavior when geometry is unsuitable.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/650.out`; stable progress/output labels such as `echo "Silence is golden"`; diagnostic detail appended to `$seqres.full`; post-test filesystem validation. The source has 66 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/650 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/651 -->
# sources/test-tools/xfstests/tests/xfs/651

## Purpose
`sources/test-tools/xfstests/tests/xfs/651` is an XFS fstests shell case focused on XFS regression coverage. Test that the sb verifier rejects zoned file system with rump RTGs. The `_begin_fstest` declaration is `auto quick zone`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/preamble`, `./common/zoned`. Local helper surface: no local shell helpers beyond the main script body. Requirement and regression gates include `_require_scratch_nocheck`. Important external or harness tools detected in the full source include `mkfs.xfs`, `mount`. Scenario variables and harness state referenced include none.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, mounts, unmounts, or cycle-mounts to test persistence across remounts. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/651.out`; stable progress/output labels such as `echo "Mounted rump RTG file system (bad)"`, `echo "Can't mount rump RTG file system (good)"`; diagnostic detail appended to `$seqres.full`; feature-dependent skips through `_notrun`. The source has 34 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/651 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/652 -->
# sources/test-tools/xfstests/tests/xfs/652

## Purpose
`sources/test-tools/xfstests/tests/xfs/652` is an XFS fstests shell case focused on realtime-device coverage, mount-option behavior. Tests that xfs_growfs to a realtime volume size that is not zone aligned is rejected. The `_begin_fstest` declaration is `auto quick realtime growfs zone`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/preamble`, `./common/zoned`. Local helper surface: `_cleanup`. Requirement and regression gates include `_require_realtime`, `_require_zloop`, `_require_scratch`, `_require_scratch_size $((16 * 1024 * 1024)) # 16GiB in kiB units`. Important external or harness tools detected in the full source include `mkfs.xfs`, `mount`, `umount`. Scenario variables and harness state referenced include `SCRATCH_MNT`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, mounts, unmounts, or cycle-mounts to test persistence across remounts. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; realtime-device paths depend on allocation unit and feature configuration, so tests skip or change behavior when geometry is unsuitable.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/652.out`; stable progress/output labels such as `echo "Format and mount zloop file system"`, `echo "Try to grow file system to a not zone aligned size"`, `echo "Remount file system"`; diagnostic detail appended to `$seqres.full`; hard failures through `_fail` assertions; feature-dependent skips through `_notrun`. The source has 58 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/652 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/653 -->
# sources/test-tools/xfstests/tests/xfs/653

## Purpose
`sources/test-tools/xfstests/tests/xfs/653` is an XFS fstests shell case focused on realtime-device coverage, mount-option behavior. Tests that mkfs for a zoned file system rounds realtime subvolume sizes up to the zone size to create mountable file systems. The `_begin_fstest` declaration is `auto quick realtime growfs zone`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/preamble`, `./common/zoned`. Local helper surface: `_cleanup`. Requirement and regression gates include `_require_test`, `_require_loop`, `_require_xfs_io_command "truncate"`, `_require_fs_space $TEST_DIR $((aligned_size / 1024))`. Important external or harness tools detected in the full source include `xfs_io`, `mount`, `umount`. Scenario variables and harness state referenced include `TEST_DIR`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_io` commands for writes, fallocate/punch, bmap inspection, scrub, repair, exchange, or media verification, uses loop devices or configuration variants to cover mount/device geometry. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; realtime-device paths depend on allocation unit and feature configuration, so tests skip or change behavior when geometry is unsuitable; loop-device setup must be cleaned reliably to avoid leaked mounts or stale backing files.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/653.out`; stable progress/output labels such as `echo "Formatting file system (unaligned specified size)"`, `echo "Formatting file system (unaligned device)"`; diagnostic detail appended to `$seqres.full`; feature-dependent skips through `_notrun`. The source has 66 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/653 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/654 -->
# sources/test-tools/xfstests/tests/xfs/654

## Purpose
`sources/test-tools/xfstests/tests/xfs/654` is an XFS fstests shell case focused on XFS regression coverage. Make sure that healthmon handles module refcount correctly. The `_begin_fstest` declaration is `auto selfhealing quick`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/module`, `./common/preamble`. Local helper surface: `_cleanup`. Requirement and regression gates include `_require_test`, `_require_xfs_io_command healthmon`, `_require_module_refcount xfs`. Important external or harness tools detected in the full source include `xfs_io`, `mount`. Scenario variables and harness state referenced include `TEST_DIR`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_io` commands for writes, fallocate/punch, bmap inspection, scrub, repair, exchange, or media verification. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; device-mapper error injection is sensitive to logical block size, realtime/zoned layout, and async writeback or readahead retries.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/654.out`; diagnostic detail appended to `$seqres.full`. The source has 60 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/654 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/655 -->
# sources/test-tools/xfstests/tests/xfs/655

## Purpose
`sources/test-tools/xfstests/tests/xfs/655` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair, realtime-device coverage, I/O or media-error handling, directory tree and parent-pointer repair. Corrupt some metadata and try to access it with the health monitoring program running. Check that healthmon observes a metadata error. The `_begin_fstest` declaration is `auto quick eio selfhealing`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/preamble`. Local helper surface: `_cleanup`, `check_healthmon`. Requirement and regression gates include `_require_scratch_nocheck`, `_require_scratch_xfs_crc # can't detect minor corruption w/o crc`, `_require_xfs_io_command healthmon`. Important external or harness tools detected in the full source include `xfs_io`, `xfs_db`, `mkfs.xfs`, `xfs_scrub`, `mount`, `stat`. Scenario variables and harness state referenced include `SCRATCH_MNT`, `SCRATCH_DEV`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_io` commands for writes, fallocate/punch, bmap inspection, scrub, repair, exchange, or media verification, uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata, runs online scrub/repair or xfs_scrub in selected modes, uses checksum/stat comparisons as the content oracle. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version; device-mapper error injection is sensitive to logical block size, realtime/zoned layout, and async writeback or readahead retries.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/655.out`; stable progress/output labels such as `echo "Format and mount"`, `echo "Runtime corruption detection"`, `echo "Scrub corruption detection"`; diagnostic detail appended to `$seqres.full`. The source has 98 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/655 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/656 -->
# sources/test-tools/xfstests/tests/xfs/656

## Purpose
`sources/test-tools/xfstests/tests/xfs/656` is an XFS fstests shell case focused on realtime-device coverage, I/O or media-error handling. Attempt to read and write a file in buffered and directio mode with the health monitoring program running. Check that healthmon observes all four types of IO errors. The `_begin_fstest` declaration is `auto quick eio selfhealing`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/dmerror`, `./common/filter`, `./common/preamble`. Local helper surface: `_cleanup`, `filter_healer_errors`. Requirement and regression gates include `_require_scratch_nocheck`, `_require_xfs_io_command healthmon`, `_require_dm_target error`, `_require_fs_space $SCRATCH_MNT 65536`. Important external or harness tools detected in the full source include `xfs_io`, `mkfs.xfs`, `dm-error`, `mount`. Scenario variables and harness state referenced include `SCRATCH_MNT`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_io` commands for writes, fallocate/punch, bmap inspection, scrub, repair, exchange, or media verification, uses dm-error or healer/systemd helpers to inject and observe I/O failures. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; device-mapper error injection is sensitive to logical block size, realtime/zoned layout, and async writeback or readahead retries.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/656.out`; stable progress/output labels such as `echo "Format and mount"`; diagnostic detail appended to `$seqres.full`. The source has 98 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/656 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/657 -->
# sources/test-tools/xfstests/tests/xfs/657

## Purpose
`sources/test-tools/xfstests/tests/xfs/657` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair. Make sure that xfs_healer correctly handles all the reports that it gets from the kernel. We simulate this by using the --everything mode so we get all the events, not just the sickness reports. The `_begin_fstest` declaration is `auto selfhealing`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/populate`, `./common/preamble`, `./common/systemd`. Local helper surface: no local shell helpers beyond the main script body. Requirement and regression gates include `_require_scrub`, `_require_xfs_io_command "scrub"		# online check support`, `_require_command "$XFS_HEALER_PROG" "xfs_healer"`, `_require_scratch`, `_require_xfs_healer $SCRATCH_MNT`. Important external or harness tools detected in the full source include `mkfs.xfs`, `xfs_scrub`, `xfs_healer`, `mount`. Scenario variables and harness state referenced include `SCRATCH_MNT`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata, runs online scrub/repair or xfs_scrub in selected modes, uses dm-error or healer/systemd helpers to inject and observe I/O failures. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version; device-mapper error injection is sensitive to logical block size, realtime/zoned layout, and async writeback or readahead retries.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/657.out`; stable progress/output labels such as `echo Silence is golden`; diagnostic detail appended to `$seqres.full`. The source has 43 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/657 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/658 -->
# sources/test-tools/xfstests/tests/xfs/658

## Purpose
`sources/test-tools/xfstests/tests/xfs/658` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair, extent mapping and exchange, directory tree and parent-pointer repair. Ensure that autonomous self healing fixes the filesystem correctly. The `_begin_fstest` declaration is `auto selfhealing`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/preamble`, `./common/systemd`. Local helper surface: no local shell helpers beyond the main script body. Requirement and regression gates include `_require_scrub`, `_require_xfs_io_command "repair"	# online repair support`, `_require_xfs_db_command "blocktrash"`, `_require_command "$XFS_HEALER_PROG" "xfs_healer"`, `_require_command "$XFS_PROPERTY_PROG" "xfs_property"`, `_require_scratch`, `_require_xfs_healer $SCRATCH_MNT --repair`. Important external or harness tools detected in the full source include `xfs_db`, `mkfs.xfs`, `xfs_healer`, `xfs_property`, `mount`, `stat`. Scenario variables and harness state referenced include `SCRATCH_MNT`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata, uses dm-error or healer/systemd helpers to inject and observe I/O failures, uses checksum/stat comparisons as the content oracle. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version; device-mapper error injection is sensitive to logical block size, realtime/zoned layout, and async writeback or readahead retries.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/658.out`; stable progress/output labels such as `echo testdata > $SCRATCH_MNT/a`, `echo "try $try saw corruption" >> $seqres.full`, `echo "try $try no longer saw corruption or gave up" >> $seqres.full`, `echo "retry $try still saw corruption" >> $seqres.full`, `echo "retry $try no longer saw corruption or gave up" >> $seqres.full`; diagnostic detail appended to `$seqres.full`; feature-dependent skips through `_notrun`. The source has 88 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/658 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/659 -->
# sources/test-tools/xfstests/tests/xfs/659

## Purpose
`sources/test-tools/xfstests/tests/xfs/659` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair, realtime-device coverage, extent mapping and exchange, I/O or media-error handling. Check that xfs_healer can report file IO errors. The `_begin_fstest` declaration is `auto quick scrub eio selfhealing`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/dmerror`, `./common/filter`, `./common/fuzzy`, `./common/preamble`, `./common/systemd`. Local helper surface: `_cleanup`, `filter_healer_errors`. Requirement and regression gates include `_require_scratch`, `_require_scrub`, `_require_command "$XFS_HEALER_PROG" "xfs_healer"`, `_require_command "$XFS_PROPERTY_PROG" "xfs_property"`, `_require_dm_target error`, `_require_no_xfs_always_cow	# no out of place writes`, `_require_xfs_scratch_non_zoned`, `_require_xfs_healer $SCRATCH_MNT`. Important external or harness tools detected in the full source include `xfs_io`, `mkfs.xfs`, `xfs_healer`, `xfs_property`, `dm-error`, `mount`. Scenario variables and harness state referenced include `DMERROR_TABLE`, `DMERROR_RTTABLE`, `SCRATCH_MNT`, `SCRATCH_DEV`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_io` commands for writes, fallocate/punch, bmap inspection, scrub, repair, exchange, or media verification, uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata, uses dm-error or healer/systemd helpers to inject and observe I/O failures. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version; device-mapper error injection is sensitive to logical block size, realtime/zoned layout, and async writeback or readahead retries; realtime-device paths depend on allocation unit and feature configuration, so tests skip or change behavior when geometry is unsuitable.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/659.out`; stable progress/output labels such as `echo "$errordev:$bmap_str" >> $seqres.full`, `echo "file_blksz:$file_blksz:fs_blksz:$fs_blksz" >> $seqres.full`, `echo "$errordev:$phys:$len:$fs_blksz:$phys_start" >> $seqres.full`, `echo "victim file:" >> $seqres.full`, `echo "bad_sector $bad_sector not congruent with device logical block size $logical_block_size"`, and 12 more; diagnostic detail appended to `$seqres.full`; hard failures through `_fail` assertions. The source has 212 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/659 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/660 -->
# sources/test-tools/xfstests/tests/xfs/660

## Purpose
`sources/test-tools/xfstests/tests/xfs/660` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair, realtime-device coverage, extent mapping and exchange, I/O or media-error handling. Check that xfs_healer can report media errors. The `_begin_fstest` declaration is `auto quick scrub eio selfhealing`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/dmerror`, `./common/filter`, `./common/fuzzy`, `./common/preamble`, `./common/systemd`. Local helper surface: `_cleanup`, `filter_healer`, `filter_verify`. Requirement and regression gates include `_require_scratch`, `_require_scrub`, `_require_dm_target error`, `_require_command "$XFS_HEALER_PROG" "xfs_healer"`, `_require_command "$XFS_PROPERTY_PROG" "xfs_property"`, `_require_xfs_io_command verifymedia`, `_require_xfs_scratch_non_zoned`, `_require_xfs_healer $SCRATCH_MNT`. Important external or harness tools detected in the full source include `xfs_io`, `mkfs.xfs`, `xfs_healer`, `xfs_property`, `dm-error`, `mount`. Scenario variables and harness state referenced include `DMERROR_TABLE`, `DMERROR_RTTABLE`, `SCRATCH_MNT`, `SCRATCH_DEV`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_io` commands for writes, fallocate/punch, bmap inspection, scrub, repair, exchange, or media verification, uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata, uses dm-error or healer/systemd helpers to inject and observe I/O failures. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version; device-mapper error injection is sensitive to logical block size, realtime/zoned layout, and async writeback or readahead retries; realtime-device paths depend on allocation unit and feature configuration, so tests skip or change behavior when geometry is unsuitable.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/660.out`; stable progress/output labels such as `echo "$errordev:$bmap_str" >> $seqres.full`, `echo "file_blksz:$file_blksz:fs_blksz:$fs_blksz" >> $seqres.full`, `echo "$errordev:$phys:$len:$fs_blksz:$phys_start" >> $seqres.full`, `echo "victim file:" >> $seqres.full`, `echo "bad_sector $bad_sector not congruent with device logical block size $logical_block_size"`, and 6 more; diagnostic detail appended to `$seqres.full`; hard failures through `_fail` assertions. The source has 174 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/660 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/661 -->
# sources/test-tools/xfstests/tests/xfs/661

## Purpose
`sources/test-tools/xfstests/tests/xfs/661` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair, I/O or media-error handling. Check that xfs_healer can report filesystem shutdowns. The `_begin_fstest` declaration is `auto quick scrub eio selfhealing shutdown`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/preamble`, `./common/systemd`. Local helper surface: no local shell helpers beyond the main script body. Requirement and regression gates include `_require_scratch_nocheck`, `_require_scrub`, `_require_command "$XFS_HEALER_PROG" "xfs_healer"`, `_require_command "$XFS_PROPERTY_PROG" "xfs_property"`, `_require_xfs_healer $SCRATCH_MNT`. Important external or harness tools detected in the full source include `xfs_io`, `mkfs.xfs`, `xfs_healer`, `xfs_property`, `mount`. Scenario variables and harness state referenced include `SCRATCH_MNT`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_io` commands for writes, fallocate/punch, bmap inspection, scrub, repair, exchange, or media verification, uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata, uses dm-error or healer/systemd helpers to inject and observe I/O failures. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version; device-mapper error injection is sensitive to logical block size, realtime/zoned layout, and async writeback or readahead retries.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/661.out`; stable progress/output labels such as `echo "Start healer and shut down"`, `echo "Kill healer"`; diagnostic detail appended to `$seqres.full`. The source has 40 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/661 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/662 -->
# sources/test-tools/xfstests/tests/xfs/662

## Purpose
`sources/test-tools/xfstests/tests/xfs/662` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair, extent mapping and exchange, directory tree and parent-pointer repair. Ensure that autonomous self healing works fixes the filesystem correctly even if the spot repair doesn't work and it falls back to a full fsck. The `_begin_fstest` declaration is `auto selfhealing`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/preamble`, `./common/systemd`. Local helper surface: `filter_healer`. Requirement and regression gates include `_require_scrub`, `_require_xfs_io_command "repair"	# online repair support`, `_require_xfs_db_command "blocktrash"`, `_require_command "$XFS_HEALER_PROG" "xfs_healer"`, `_require_command "$XFS_PROPERTY_PROG" "xfs_property"`, `_require_scratch`, `_require_systemd_unit_defined "xfs_scrub@.service"`, `_require_xfs_healer $SCRATCH_MNT --repair`. Important external or harness tools detected in the full source include `xfs_io`, `xfs_db`, `mkfs.xfs`, `xfs_healer`, `xfs_property`, `mount`, `stat`. Scenario variables and harness state referenced include `SCRATCH_MNT`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_io` commands for writes, fallocate/punch, bmap inspection, scrub, repair, exchange, or media verification, uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata, uses dm-error or healer/systemd helpers to inject and observe I/O failures, uses checksum/stat comparisons as the content oracle. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version; device-mapper error injection is sensitive to logical block size, realtime/zoned layout, and async writeback or readahead retries.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/662.out`; stable progress/output labels such as `echo testdata > $SCRATCH_MNT/a`, `echo "try $try saw corruption" >> $seqres.full`, `echo "try $try no longer saw corruption or gave up" >> $seqres.full`, `echo "retry $try still saw corruption" >> $seqres.full`, `echo "retry $try no longer saw corruption or gave up" >> $seqres.full`; diagnostic detail appended to `$seqres.full`; feature-dependent skips through `_notrun`. The source has 107 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/662 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/663 -->
# sources/test-tools/xfstests/tests/xfs/663

## Purpose
`sources/test-tools/xfstests/tests/xfs/663` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair, extent mapping and exchange, directory tree and parent-pointer repair, stress concurrency. Ensure that autonomous self healing fixes the filesystem correctly even if the original mount has moved somewhere else. The `_begin_fstest` declaration is `auto selfhealing mount`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/preamble`, `./common/systemd`. Local helper surface: `_cleanup`, `new_dir_unmount`. Requirement and regression gates include `_require_test`, `_require_scrub`, `_require_xfs_io_command "repair"	# online repair support`, `_require_xfs_db_command "blocktrash"`, `_require_command "$XFS_HEALER_PROG" "xfs_healer"`, `_require_command "$XFS_PROPERTY_PROG" "xfs_property"`, `_require_scratch`, `_require_xfs_healer $SCRATCH_MNT --repair`. Important external or harness tools detected in the full source include `xfs_db`, `mkfs.xfs`, `xfs_healer`, `xfs_property`, `fsstress`, `mount`, `stat`. Scenario variables and harness state referenced include `TEST_DIR`, `SCRATCH_MNT`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata, starts fsstress or stress-scrub helpers to exercise concurrency, uses dm-error or healer/systemd helpers to inject and observe I/O failures, uses checksum/stat comparisons as the content oracle. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version; stress timing is intentionally nondeterministic, so regressions may appear as hangs, livelocks, kernel warnings, or post-test fsck failures; device-mapper error injection is sensitive to logical block size, realtime/zoned layout, and async writeback or readahead retries.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/663.out`; stable progress/output labels such as `echo testdata > $SCRATCH_MNT/a`, `echo "try $try saw corruption" >> $seqres.full`, `echo "try $try no longer saw corruption or gave up" >> $seqres.full`, `echo "retry $try still saw corruption" >> $seqres.full`, `echo "retry $try no longer saw corruption or gave up" >> $seqres.full`; diagnostic detail appended to `$seqres.full`; feature-dependent skips through `_notrun`. The source has 114 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/663 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/664 -->
# sources/test-tools/xfstests/tests/xfs/664

## Purpose
`sources/test-tools/xfstests/tests/xfs/664` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair, extent mapping and exchange, directory tree and parent-pointer repair, stress concurrency, mount-option behavior. Ensure that autonomous self healing won't fix the wrong filesystem if a snapshot of the original filesystem is now mounted on the same directory as the original. The `_begin_fstest` declaration is `auto selfhealing`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/preamble`, `./common/systemd`. Local helper surface: `_cleanup`, `filter_mntpt`, `new_dir_unmount`. Requirement and regression gates include `_require_test`, `_require_scrub`, `_require_xfs_io_command "repair"	# online repair support`, `_require_xfs_db_command "blocktrash"`, `_require_command "$XFS_HEALER_PROG" "xfs_healer"`, `_require_command "$XFS_PROPERTY_PROG" "xfs_property"`, `_require_xfs_healer $mntpt --repair`. Important external or harness tools detected in the full source include `xfs_io`, `xfs_db`, `xfs_healer`, `xfs_property`, `fsstress`, `mount`, `stat`. Scenario variables and harness state referenced include `TEST_DIR`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_io` commands for writes, fallocate/punch, bmap inspection, scrub, repair, exchange, or media verification, uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata, starts fsstress or stress-scrub helpers to exercise concurrency, uses dm-error or healer/systemd helpers to inject and observe I/O failures, uses checksum/stat comparisons as the content oracle, uses loop devices or configuration variants to cover mount/device geometry. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version; stress timing is intentionally nondeterministic, so regressions may appear as hangs, livelocks, kernel warnings, or post-test fsck failures; device-mapper error injection is sensitive to logical block size, realtime/zoned layout, and async writeback or readahead retries; loop-device setup must be cleaned reliably to avoid leaked mounts or stale backing files.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/664.out`; stable progress/output labels such as `echo testdata > $mntpt/a`, `echo "LOG $XFS_HEALER_PID SO FAR:" >> $seqres.full`, `echo "LOG AFTER TRYING TO POKE:" >> $seqres.full`, `echo "LOG AFTER FAILURE" >> $seqres.full`, `echo "Should have seen stale file handle complaints"`; diagnostic detail appended to `$seqres.full`; hard failures through `_fail` assertions; feature-dependent skips through `_notrun`. The source has 135 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/664 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/665 -->
# sources/test-tools/xfstests/tests/xfs/665

## Purpose
`sources/test-tools/xfstests/tests/xfs/665` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair, extent mapping and exchange, directory tree and parent-pointer repair. Ensure that autonomous self healing fixes the filesystem correctly when running in a systemd service The `_begin_fstest` declaration is `auto selfhealing unreliable_in_parallel`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/preamble`, `./common/systemd`. Local helper surface: `_cleanup`. Requirement and regression gates include `_require_systemd_is_running`, `_require_systemd_unit_defined xfs_healer@.service`, `_require_scrub`, `_require_xfs_io_command "repair"	# online repair support`, `_require_xfs_db_command "blocktrash"`, `_require_command "$XFS_HEALER_PROG" "xfs_healer"`, `_require_command "$XFS_PROPERTY_PROG" "xfs_property"`, `_require_scratch`, `_require_xfs_healer $SCRATCH_MNT --repair`. Important external or harness tools detected in the full source include `xfs_db`, `mkfs.xfs`, `xfs_healer`, `xfs_property`, `mount`, `stat`. Scenario variables and harness state referenced include `SCRATCH_MNT`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata, uses dm-error or healer/systemd helpers to inject and observe I/O failures, uses checksum/stat comparisons as the content oracle. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version; device-mapper error injection is sensitive to logical block size, realtime/zoned layout, and async writeback or readahead retries.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/665.out`; stable progress/output labels such as `echo testdata > $SCRATCH_MNT/a`, `echo "systemd service \"$new_healer_svc\" not running??"`, `echo "try $try saw corruption" >> $seqres.full`, `echo "try $try no longer saw corruption or gave up" >> $seqres.full`, `echo "retry $try still saw corruption" >> $seqres.full`, and 1 more; diagnostic detail appended to `$seqres.full`; feature-dependent skips through `_notrun`. The source has 152 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/665 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/666 -->
# sources/test-tools/xfstests/tests/xfs/666

## Purpose
`sources/test-tools/xfstests/tests/xfs/666` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair. Check that the xfs_healer startup service starts the per-mount xfs_healer service for the scratch filesystem. IOWs, this is basic testing for the xfs_healer systemd background services. The `_begin_fstest` declaration is `auto selfhealing unreliable_in_parallel`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/populate`, `./common/preamble`, `./common/systemd`. Local helper surface: `_cleanup`, `find_healer_trace`. Requirement and regression gates include `_require_systemd_is_running`, `_require_systemd_unit_defined xfs_healer@.service`, `_require_systemd_unit_defined xfs_healer_start.service`, `_require_scratch`, `_require_scrub`, `_require_xfs_io_command "scrub"`, `_require_xfs_spaceman_command "health"`, `_require_populate_commands`, `_require_command "$XFS_HEALER_PROG" "xfs_healer"`, `_require_command $ATTR_PROG "attr"`, `_require_xfs_healer $SCRATCH_MNT`. Important external or harness tools detected in the full source include `mkfs.xfs`, `xfs_healer`, `mount`. Scenario variables and harness state referenced include `SCRATCH_MNT`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata, uses dm-error or healer/systemd helpers to inject and observe I/O failures. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version; device-mapper error injection is sensitive to logical block size, realtime/zoned layout, and async writeback or readahead retries.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/666.out`; stable progress/output labels such as `echo "cannot find evidence that xfs_healer is running for $path"`, `echo "Format and populate"`, `echo "Start healer on scratch FS"`, `echo "Start healer for everything"`, `echo "Restart healer for scratch FS"`, and 1 more; diagnostic detail appended to `$seqres.full`; feature-dependent skips through `_notrun`. The source has 123 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/666 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/667 -->
# sources/test-tools/xfstests/tests/xfs/667

## Purpose
`sources/test-tools/xfstests/tests/xfs/667` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair, extent mapping and exchange, directory tree and parent-pointer repair, stress concurrency, mount-option behavior. Ensure that autonomous self healing fixes the filesystem correctly even if the original mount has moved somewhere else via --move. The `_begin_fstest` declaration is `auto selfhealing mount`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/preamble`, `./common/systemd`. Local helper surface: `_cleanup`, `new_dir_unmount`. Requirement and regression gates include `_require_unshare`, `_require_test`, `_require_scrub`, `_require_xfs_io_command "repair"	# online repair support`, `_require_xfs_db_command "blocktrash"`, `_require_command "$XFS_HEALER_PROG" "xfs_healer"`, `_require_command "$XFS_PROPERTY_PROG" "xfs_property"`, `_require_scratch`, `_require_xfs_healer $SCRATCH_MNT --repair`. Important external or harness tools detected in the full source include `xfs_db`, `mkfs.xfs`, `xfs_healer`, `xfs_property`, `fsstress`, `findmnt`, `mount`, `stat`. Scenario variables and harness state referenced include `TEST_DIR`, `SCRATCH_MNT`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata, starts fsstress or stress-scrub helpers to exercise concurrency, uses dm-error or healer/systemd helpers to inject and observe I/O failures, uses checksum/stat comparisons as the content oracle. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version; stress timing is intentionally nondeterministic, so regressions may appear as hangs, livelocks, kernel warnings, or post-test fsck failures; device-mapper error injection is sensitive to logical block size, realtime/zoned layout, and async writeback or readahead retries.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/667.out`; stable progress/output labels such as `echo "try $try saw corruption" >> $seqres.full`, `echo "try $try no longer saw corruption or gave up" >> $seqres.full`, `echo "retry $try still saw corruption" >> $seqres.full`, `echo "retry $try no longer saw corruption or gave up" >> $seqres.full`, `echo testdata > $SCRATCH_MNT/a`; diagnostic detail appended to `$seqres.full`; feature-dependent skips through `_notrun`. The source has 128 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/667 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/668 -->
# sources/test-tools/xfstests/tests/xfs/668

## Purpose
`sources/test-tools/xfstests/tests/xfs/668` is an XFS fstests shell case focused on realtime-device coverage. Tests that writes to zonegc_low_space will trigger start of garbage collection for rw (but not ro) file systems The `_begin_fstest` declaration is `auto rw zone quick`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/preamble`, `./common/zoned`. Local helper surface: no local shell helpers beyond the main script body. Requirement and regression gates include `_require_scratch`, `_require_odirect`, `_require_zoned_device "$zdev"`, `_require_xfs_scratch_zoned`. Important external or harness tools detected in the full source include `mkfs.xfs`, `mount`. Scenario variables and harness state referenced include `MOUNT_OPTIONS`, `SCRATCH_MNT`, `SCRATCH_DEV`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, mounts, unmounts, or cycle-mounts to test persistence across remounts. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; realtime-device paths depend on allocation unit and feature configuration, so tests skip or change behavior when geometry is unsuitable.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/668.out`; stable progress/output labels such as `echo "Silence is golden"`; diagnostic detail appended to `$seqres.full`; hard failures through `_fail` assertions; feature-dependent skips through `_notrun`. The source has 72 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/668 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/669 -->
# sources/test-tools/xfstests/tests/xfs/669

## Purpose
`sources/test-tools/xfstests/tests/xfs/669` is an XFS fstests shell case focused on XFS regression coverage. Test that mounts of zoned file systems on conventional devices don't create more open zones than allowed when the last blocks in one or more zones have been invalidated. The `_begin_fstest` declaration is `auto quick zone`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/preamble`. Local helper surface: no local shell helpers beyond the main script body. Requirement and regression gates include `_require_scratch_nocheck`, `_require_odirect`, `_require_non_zoned_device $SCRATCH_DEV`. Important external or harness tools detected in the full source include `mkfs.xfs`, `mount`. Scenario variables and harness state referenced include `SCRATCH_MNT`, `SCRATCH_DEV`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, mounts, unmounts, or cycle-mounts to test persistence across remounts. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/669.out`; stable progress/output labels such as `echo "zone size: $zone_size_mib" >>$seqres.full`, `echo "file size: $file_size_mib" >>$seqres.full`, `echo "nr files: $nr_files" >>$seqres.full`; diagnostic detail appended to `$seqres.full`; hard failures through `_fail` assertions; feature-dependent skips through `_notrun`. The source has 68 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/669 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/708 -->
# sources/test-tools/xfstests/tests/xfs/708

## Purpose
`sources/test-tools/xfstests/tests/xfs/708` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair, stress concurrency. Race fsstress and bnobt repair for a while to see if we crash or livelock. The `_begin_fstest` declaration is `online_repair fsstress_online_repair`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/inject`, `./common/preamble`, `./common/xfs`. Local helper surface: `_cleanup`. Requirement and regression gates include `_require_scratch`, `_require_xfs_stress_online_repair`. Important external or harness tools detected in the full source include `mkfs.xfs`, `fsstress`, `mount`. Scenario variables and harness state referenced include none.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata, runs online scrub/repair or xfs_scrub in selected modes, starts fsstress or stress-scrub helpers to exercise concurrency. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version; stress timing is intentionally nondeterministic, so regressions may appear as hangs, livelocks, kernel warnings, or post-test fsck failures.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/708.out`; stable progress/output labels such as `echo Silence is golden`; diagnostic detail appended to `$seqres.full`. The source has 35 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/708 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/709 -->
# sources/test-tools/xfstests/tests/xfs/709

## Purpose
`sources/test-tools/xfstests/tests/xfs/709` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair, stress concurrency. Race fsstress and inobt repair for a while to see if we crash or livelock. The `_begin_fstest` declaration is `online_repair fsstress_online_repair`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/inject`, `./common/preamble`, `./common/xfs`. Local helper surface: `_cleanup`. Requirement and regression gates include `_require_scratch`, `_require_xfs_stress_online_repair`. Important external or harness tools detected in the full source include `mkfs.xfs`, `fsstress`, `mount`. Scenario variables and harness state referenced include none.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata, runs online scrub/repair or xfs_scrub in selected modes, starts fsstress or stress-scrub helpers to exercise concurrency. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version; stress timing is intentionally nondeterministic, so regressions may appear as hangs, livelocks, kernel warnings, or post-test fsck failures.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/709.out`; stable progress/output labels such as `echo Silence is golden`; diagnostic detail appended to `$seqres.full`. The source has 35 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/709 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/710 -->
# sources/test-tools/xfstests/tests/xfs/710

## Purpose
`sources/test-tools/xfstests/tests/xfs/710` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair, stress concurrency. Race fsstress and refcountbt repair for a while to see if we crash or livelock. The `_begin_fstest` declaration is `online_repair fsstress_online_repair`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/inject`, `./common/preamble`, `./common/xfs`. Local helper surface: `_cleanup`. Requirement and regression gates include `_require_scratch`, `_require_xfs_stress_online_repair`, `_require_xfs_has_feature "$SCRATCH_MNT" reflink`. Important external or harness tools detected in the full source include `mkfs.xfs`, `fsstress`, `mount`. Scenario variables and harness state referenced include `SCRATCH_MNT`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata, runs online scrub/repair or xfs_scrub in selected modes, starts fsstress or stress-scrub helpers to exercise concurrency. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version; stress timing is intentionally nondeterministic, so regressions may appear as hangs, livelocks, kernel warnings, or post-test fsck failures.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/710.out`; stable progress/output labels such as `echo Silence is golden`; diagnostic detail appended to `$seqres.full`. The source has 36 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/710 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/711 -->
# sources/test-tools/xfstests/tests/xfs/711

## Purpose
`sources/test-tools/xfstests/tests/xfs/711` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair, stress concurrency. Race fsstress and superblock repair for a while to see if we crash or livelock. The `_begin_fstest` declaration is `online_repair fsstress_online_repair`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/inject`, `./common/preamble`, `./common/xfs`. Local helper surface: `_cleanup`. Requirement and regression gates include `_require_scratch`, `_require_xfs_stress_online_repair`. Important external or harness tools detected in the full source include `mkfs.xfs`, `fsstress`, `mount`. Scenario variables and harness state referenced include none.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata, runs online scrub/repair or xfs_scrub in selected modes, starts fsstress or stress-scrub helpers to exercise concurrency. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version; stress timing is intentionally nondeterministic, so regressions may appear as hangs, livelocks, kernel warnings, or post-test fsck failures.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/711.out`; stable progress/output labels such as `echo Silence is golden`; diagnostic detail appended to `$seqres.full`. The source has 35 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/711 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/712 -->
# sources/test-tools/xfstests/tests/xfs/712

## Purpose
`sources/test-tools/xfstests/tests/xfs/712` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair, stress concurrency. Race fsstress and agf repair for a while to see if we crash or livelock. The `_begin_fstest` declaration is `online_repair fsstress_online_repair`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/inject`, `./common/preamble`, `./common/xfs`. Local helper surface: `_cleanup`. Requirement and regression gates include `_require_scratch`, `_require_xfs_stress_online_repair`. Important external or harness tools detected in the full source include `mkfs.xfs`, `fsstress`, `mount`. Scenario variables and harness state referenced include none.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata, runs online scrub/repair or xfs_scrub in selected modes, starts fsstress or stress-scrub helpers to exercise concurrency. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version; stress timing is intentionally nondeterministic, so regressions may appear as hangs, livelocks, kernel warnings, or post-test fsck failures.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/712.out`; stable progress/output labels such as `echo Silence is golden`; diagnostic detail appended to `$seqres.full`. The source has 35 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/712 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/713 -->
# sources/test-tools/xfstests/tests/xfs/713

## Purpose
`sources/test-tools/xfstests/tests/xfs/713` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair, stress concurrency. Race fsstress and agfl repair for a while to see if we crash or livelock. The `_begin_fstest` declaration is `online_repair fsstress_online_repair`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/inject`, `./common/preamble`, `./common/xfs`. Local helper surface: `_cleanup`. Requirement and regression gates include `_require_scratch`, `_require_xfs_stress_online_repair`. Important external or harness tools detected in the full source include `mkfs.xfs`, `fsstress`, `mount`. Scenario variables and harness state referenced include none.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata, runs online scrub/repair or xfs_scrub in selected modes, starts fsstress or stress-scrub helpers to exercise concurrency. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version; stress timing is intentionally nondeterministic, so regressions may appear as hangs, livelocks, kernel warnings, or post-test fsck failures.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/713.out`; stable progress/output labels such as `echo Silence is golden`; diagnostic detail appended to `$seqres.full`. The source has 35 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/713 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/714 -->
# sources/test-tools/xfstests/tests/xfs/714

## Purpose
`sources/test-tools/xfstests/tests/xfs/714` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair, stress concurrency. Race fsstress and agi repair for a while to see if we crash or livelock. The `_begin_fstest` declaration is `online_repair fsstress_online_repair`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/inject`, `./common/preamble`, `./common/xfs`. Local helper surface: `_cleanup`. Requirement and regression gates include `_require_scratch`, `_require_xfs_stress_online_repair`. Important external or harness tools detected in the full source include `mkfs.xfs`, `fsstress`, `mount`. Scenario variables and harness state referenced include none.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata, runs online scrub/repair or xfs_scrub in selected modes, starts fsstress or stress-scrub helpers to exercise concurrency. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version; stress timing is intentionally nondeterministic, so regressions may appear as hangs, livelocks, kernel warnings, or post-test fsck failures.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/714.out`; stable progress/output labels such as `echo Silence is golden`; diagnostic detail appended to `$seqres.full`. The source has 35 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/714 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/715 -->
# sources/test-tools/xfstests/tests/xfs/715

## Purpose
`sources/test-tools/xfstests/tests/xfs/715` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair, stress concurrency. Race fsstress and inode record repair for a while to see if we crash or livelock. The `_begin_fstest` declaration is `online_repair fsstress_online_repair`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/inject`, `./common/preamble`, `./common/xfs`. Local helper surface: `_cleanup`. Requirement and regression gates include `_require_scratch`, `_require_xfs_stress_online_repair`. Important external or harness tools detected in the full source include `mkfs.xfs`, `fsstress`, `mount`. Scenario variables and harness state referenced include none.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata, runs online scrub/repair or xfs_scrub in selected modes, starts fsstress or stress-scrub helpers to exercise concurrency. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version; stress timing is intentionally nondeterministic, so regressions may appear as hangs, livelocks, kernel warnings, or post-test fsck failures.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/715.out`; stable progress/output labels such as `echo Silence is golden`; diagnostic detail appended to `$seqres.full`. The source has 36 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/715 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/716 -->
# sources/test-tools/xfstests/tests/xfs/716

## Purpose
`sources/test-tools/xfstests/tests/xfs/716` is an XFS fstests shell case focused on online repair and scrub, extent mapping and exchange, attribute fork repair. Make sure online repair can handle rebuilding xattrs when the data fork is in btree format and we cannot just zap the attr fork. The `_begin_fstest` declaration is `auto quick online_repair`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/inject`, `./common/preamble`. Local helper surface: `_cleanup`. Requirement and regression gates include `_require_scratch`, `_require_xfs_io_error_injection "force_repair"`, `_require_xfs_io_command "falloc"`, `_require_xfs_io_command "repair"`, `_require_test_program "punch-alternating"`, `_require_scratch_xfs_scrub`. Important external or harness tools detected in the full source include `xfs_io`, `xfs_db`, `mkfs.xfs`, `setfattr`, `punch-alternating`, `mount`, `umount`, `stat`. Scenario variables and harness state referenced include `SCRATCH_MNT`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_io` commands for writes, fallocate/punch, bmap inspection, scrub, repair, exchange, or media verification, uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata, sets extended attributes or validates attr-fork behavior, uses checksum/stat comparisons as the content oracle. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/716.out`; stable progress/output labels such as `echo "data fork not in btree format?"`, `echo "about to start test" >> $seqres.full`, `echo "Silence is golden."`; diagnostic detail appended to `$seqres.full`; feature-dependent skips through `_notrun`; post-test filesystem validation. The source has 83 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/716 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/717 -->
# sources/test-tools/xfstests/tests/xfs/717

## Purpose
`sources/test-tools/xfstests/tests/xfs/717` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair, extent mapping and exchange, stress concurrency. Race fsstress and data fork repair for a while to see if we crash or livelock. The `_begin_fstest` declaration is `online_repair fsstress_online_repair`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/inject`, `./common/preamble`, `./common/xfs`. Local helper surface: `_cleanup`. Requirement and regression gates include `_require_scratch`, `_require_xfs_stress_online_repair`. Important external or harness tools detected in the full source include `mkfs.xfs`, `fsstress`, `mount`. Scenario variables and harness state referenced include none.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata, runs online scrub/repair or xfs_scrub in selected modes, starts fsstress or stress-scrub helpers to exercise concurrency. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version; stress timing is intentionally nondeterministic, so regressions may appear as hangs, livelocks, kernel warnings, or post-test fsck failures.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/717.out`; stable progress/output labels such as `echo Silence is golden`; diagnostic detail appended to `$seqres.full`. The source has 35 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/717 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/718 -->
# sources/test-tools/xfstests/tests/xfs/718

## Purpose
`sources/test-tools/xfstests/tests/xfs/718` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair, extent mapping and exchange, attribute fork repair, stress concurrency. Race fsstress and attr fork repair for a while to see if we crash or livelock. The `_begin_fstest` declaration is `online_repair fsstress_online_repair`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/attr`, `./common/filter`, `./common/fuzzy`, `./common/inject`, `./common/preamble`, `./common/xfs`. Local helper surface: `_cleanup`. Requirement and regression gates include `_require_scratch`, `_require_attrs`, `_require_xfs_stress_online_repair`. Important external or harness tools detected in the full source include `mkfs.xfs`, `fsstress`, `mount`. Scenario variables and harness state referenced include none.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata, runs online scrub/repair or xfs_scrub in selected modes, starts fsstress or stress-scrub helpers to exercise concurrency, sets extended attributes or validates attr-fork behavior. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version; stress timing is intentionally nondeterministic, so regressions may appear as hangs, livelocks, kernel warnings, or post-test fsck failures.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/718.out`; stable progress/output labels such as `echo Silence is golden`; diagnostic detail appended to `$seqres.full`. The source has 37 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/718 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/719 -->
# sources/test-tools/xfstests/tests/xfs/719

## Purpose
`sources/test-tools/xfstests/tests/xfs/719` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair, extent mapping and exchange, stress concurrency. Race fsstress and CoW fork repair for a while to see if we crash or livelock. The `_begin_fstest` declaration is `online_repair fsstress_online_repair`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/inject`, `./common/preamble`, `./common/reflink`, `./common/xfs`. Local helper surface: `_cleanup`. Requirement and regression gates include `_require_scratch`, `_require_xfs_stress_online_repair`, `_require_xfs_has_feature "$SCRATCH_MNT" reflink`. Important external or harness tools detected in the full source include `mkfs.xfs`, `fsstress`, `mount`. Scenario variables and harness state referenced include `SCRATCH_MNT`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata, runs online scrub/repair or xfs_scrub in selected modes, starts fsstress or stress-scrub helpers to exercise concurrency. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version; stress timing is intentionally nondeterministic, so regressions may appear as hangs, livelocks, kernel warnings, or post-test fsck failures.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/719.out`; stable progress/output labels such as `echo Silence is golden`; diagnostic detail appended to `$seqres.full`. The source has 37 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/719 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/720 -->
# sources/test-tools/xfstests/tests/xfs/720

## Purpose
`sources/test-tools/xfstests/tests/xfs/720` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair, quota enforcement, extent mapping and exchange, stress concurrency. Ensure that the sysadmin won't hit EDQUOT while repairing file data forks even if the file's quota limits have been exceeded. This tests the quota reservation handling inside the bmap btree rebuilding code. The `_begin_fstest` declaration is `online_repair`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/inject`, `./common/preamble`, `./common/quota`. Local helper surface: no local shell helpers beyond the main script body. Requirement and regression gates include `_require_xfs_io_command "falloc"`, `_require_quota`, `_require_user`, `_require_test_program "punch-alternating"`, `_require_scratch`, `_require_xfs_stress_online_repair`. Important external or harness tools detected in the full source include `xfs_io`, `mkfs.xfs`, `xfs_quota`, `punch-alternating`, `mount`. Scenario variables and harness state referenced include `SCRATCH_MNT`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, uses `xfs_io` commands for writes, fallocate/punch, bmap inspection, scrub, repair, exchange, or media verification, uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata, sets up quota state and validates accounting or enforcement. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version; quota tests depend on user/group setup, mount options, and stable quota-tools output.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/720.out`; stable progress/output labels such as `echo "set up quota" >> $seqres.full`, `echo "repairs" >> $seqres.full`, `echo "fail quota" >> $seqres.full`, `echo Silence is golden`; diagnostic detail appended to `$seqres.full`. The source has 75 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/720 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/721 -->
# sources/test-tools/xfstests/tests/xfs/721

## Purpose
`sources/test-tools/xfstests/tests/xfs/721` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair, stress concurrency. Race fsstress and symlink repair for a while to see if we crash or livelock. We can't open special files directly for scrubbing, so we use xfs_scrub(8). The `_begin_fstest` declaration is `online_repair fsstress_online_repair`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/inject`, `./common/preamble`, `./common/xfs`. Local helper surface: `_cleanup`. Requirement and regression gates include `_require_scratch`, `_require_xfs_stress_online_repair`. Important external or harness tools detected in the full source include `mkfs.xfs`, `fsstress`, `mount`. Scenario variables and harness state referenced include `XFS_SCRUB_PHASE`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata, runs online scrub/repair or xfs_scrub in selected modes, starts fsstress or stress-scrub helpers to exercise concurrency. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version; stress timing is intentionally nondeterministic, so regressions may appear as hangs, livelocks, kernel warnings, or post-test fsck failures.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/721.out`; stable progress/output labels such as `echo Silence is golden`; diagnostic detail appended to `$seqres.full`. The source has 36 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/721 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/722 -->
# sources/test-tools/xfstests/tests/xfs/722

## Purpose
`sources/test-tools/xfstests/tests/xfs/722` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair, stress concurrency. Race fsstress and special file repair for a while to see if we crash or livelock. We can't open special files directly for scrubbing, so we use xfs_scrub(8). The `_begin_fstest` declaration is `online_repair fsstress_online_repair`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/inject`, `./common/preamble`, `./common/xfs`. Local helper surface: `_cleanup`. Requirement and regression gates include `_require_scratch`, `_require_xfs_stress_online_repair`. Important external or harness tools detected in the full source include `mkfs.xfs`, `fsstress`, `mount`. Scenario variables and harness state referenced include `XFS_SCRUB_PHASE`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata, runs online scrub/repair or xfs_scrub in selected modes, starts fsstress or stress-scrub helpers to exercise concurrency. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version; stress timing is intentionally nondeterministic, so regressions may appear as hangs, livelocks, kernel warnings, or post-test fsck failures.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/722.out`; stable progress/output labels such as `echo Silence is golden`; diagnostic detail appended to `$seqres.full`. The source has 37 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/722 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/723 -->
# sources/test-tools/xfstests/tests/xfs/723

## Purpose
`sources/test-tools/xfstests/tests/xfs/723` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair, quota enforcement, stress concurrency. Race fsstress and user quota repair for a while to see if we crash or livelock. The `_begin_fstest` declaration is `online_repair fsstress_online_repair`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/inject`, `./common/preamble`, `./common/quota`, `./common/xfs`. Local helper surface: `_cleanup`. Requirement and regression gates include `_require_scratch`, `_require_xfs_stress_online_repair`, `_require_xfs_quota_acct_enabled "$SCRATCH_DEV" usrquota`. Important external or harness tools detected in the full source include `mkfs.xfs`, `fsstress`, `mount`. Scenario variables and harness state referenced include `SCRATCH_DEV`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata, runs online scrub/repair or xfs_scrub in selected modes, starts fsstress or stress-scrub helpers to exercise concurrency. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version; stress timing is intentionally nondeterministic, so regressions may appear as hangs, livelocks, kernel warnings, or post-test fsck failures; quota tests depend on user/group setup, mount options, and stable quota-tools output.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/723.out`; stable progress/output labels such as `echo Silence is golden`; diagnostic detail appended to `$seqres.full`. The source has 38 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/723 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/724 -->
# sources/test-tools/xfstests/tests/xfs/724

## Purpose
`sources/test-tools/xfstests/tests/xfs/724` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair, quota enforcement, stress concurrency. Race fsstress and group quota repair for a while to see if we crash or livelock. The `_begin_fstest` declaration is `online_repair fsstress_online_repair`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/inject`, `./common/preamble`, `./common/quota`, `./common/xfs`. Local helper surface: `_cleanup`. Requirement and regression gates include `_require_scratch`, `_require_xfs_stress_online_repair`, `_require_xfs_quota_acct_enabled "$SCRATCH_DEV" grpquota`. Important external or harness tools detected in the full source include `mkfs.xfs`, `fsstress`, `mount`. Scenario variables and harness state referenced include `SCRATCH_DEV`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata, runs online scrub/repair or xfs_scrub in selected modes, starts fsstress or stress-scrub helpers to exercise concurrency. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version; stress timing is intentionally nondeterministic, so regressions may appear as hangs, livelocks, kernel warnings, or post-test fsck failures; quota tests depend on user/group setup, mount options, and stable quota-tools output.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/724.out`; stable progress/output labels such as `echo Silence is golden`; diagnostic detail appended to `$seqres.full`. The source has 38 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/724 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/725 -->
# sources/test-tools/xfstests/tests/xfs/725

## Purpose
`sources/test-tools/xfstests/tests/xfs/725` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair, quota enforcement, stress concurrency. Race fsstress and project quota repair for a while to see if we crash or livelock. The `_begin_fstest` declaration is `online_repair fsstress_online_repair`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/inject`, `./common/preamble`, `./common/quota`, `./common/xfs`. Local helper surface: `_cleanup`. Requirement and regression gates include `_require_scratch`, `_require_xfs_stress_online_repair`, `_require_xfs_quota_acct_enabled "$SCRATCH_DEV" prjquota`. Important external or harness tools detected in the full source include `mkfs.xfs`, `fsstress`, `mount`. Scenario variables and harness state referenced include `SCRATCH_DEV`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata, runs online scrub/repair or xfs_scrub in selected modes, starts fsstress or stress-scrub helpers to exercise concurrency. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version; stress timing is intentionally nondeterministic, so regressions may appear as hangs, livelocks, kernel warnings, or post-test fsck failures; quota tests depend on user/group setup, mount options, and stable quota-tools output.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/725.out`; stable progress/output labels such as `echo Silence is golden`; diagnostic detail appended to `$seqres.full`. The source has 38 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/725 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/726 -->
# sources/test-tools/xfstests/tests/xfs/726

## Purpose
`sources/test-tools/xfstests/tests/xfs/726` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair, quota enforcement, stress concurrency. Race fsstress and quotacheck repair for a while to see if we crash or livelock. The `_begin_fstest` declaration is `online_repair fsstress_online_repair`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/inject`, `./common/preamble`, `./common/quota`, `./common/xfs`. Local helper surface: `_cleanup`. Requirement and regression gates include `_require_scratch`, `_require_xfs_stress_online_repair`, `_require_xfs_quota_acct_enabled "$SCRATCH_DEV" any`. Important external or harness tools detected in the full source include `mkfs.xfs`, `fsstress`, `mount`. Scenario variables and harness state referenced include `SCRATCH_DEV`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata, runs online scrub/repair or xfs_scrub in selected modes, starts fsstress or stress-scrub helpers to exercise concurrency. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version; stress timing is intentionally nondeterministic, so regressions may appear as hangs, livelocks, kernel warnings, or post-test fsck failures; quota tests depend on user/group setup, mount options, and stable quota-tools output.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/726.out`; stable progress/output labels such as `echo Silence is golden`; diagnostic detail appended to `$seqres.full`. The source has 38 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/726 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/727 -->
# sources/test-tools/xfstests/tests/xfs/727

## Purpose
`sources/test-tools/xfstests/tests/xfs/727` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair, quota enforcement, stress concurrency. Race fsstress and quotacheck scrub for a while to see if we crash or livelock. The `_begin_fstest` declaration is `scrub fsstress_scrub`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/inject`, `./common/preamble`, `./common/quota`, `./common/xfs`. Local helper surface: `_cleanup`. Requirement and regression gates include `_require_scratch`, `_require_xfs_stress_scrub`, `_require_xfs_quota_acct_enabled "$SCRATCH_DEV" any`. Important external or harness tools detected in the full source include `mkfs.xfs`, `fsstress`, `mount`. Scenario variables and harness state referenced include `SCRATCH_DEV`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata, runs online scrub/repair or xfs_scrub in selected modes, starts fsstress or stress-scrub helpers to exercise concurrency. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version; stress timing is intentionally nondeterministic, so regressions may appear as hangs, livelocks, kernel warnings, or post-test fsck failures; quota tests depend on user/group setup, mount options, and stable quota-tools output.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/727.out`; stable progress/output labels such as `echo Silence is golden`; diagnostic detail appended to `$seqres.full`. The source has 38 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/727 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/728 -->
# sources/test-tools/xfstests/tests/xfs/728

## Purpose
`sources/test-tools/xfstests/tests/xfs/728` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair, stress concurrency. Race fsstress and inode link count repair for a while to see if we crash or livelock. The `_begin_fstest` declaration is `online_repair fsstress_online_repair`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/inject`, `./common/preamble`, `./common/xfs`. Local helper surface: `_cleanup`. Requirement and regression gates include `_require_scratch`, `_require_xfs_stress_online_repair`. Important external or harness tools detected in the full source include `mkfs.xfs`, `fsstress`, `mount`. Scenario variables and harness state referenced include none.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata, runs online scrub/repair or xfs_scrub in selected modes, starts fsstress or stress-scrub helpers to exercise concurrency. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version; stress timing is intentionally nondeterministic, so regressions may appear as hangs, livelocks, kernel warnings, or post-test fsck failures.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/728.out`; stable progress/output labels such as `echo Silence is golden`; diagnostic detail appended to `$seqres.full`. The source has 36 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/728 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/729 -->
# sources/test-tools/xfstests/tests/xfs/729

## Purpose
`sources/test-tools/xfstests/tests/xfs/729` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair, stress concurrency. Race fsstress and nlinks scrub for a while to see if we crash or livelock. The `_begin_fstest` declaration is `scrub fsstress_scrub`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/inject`, `./common/preamble`, `./common/xfs`. Local helper surface: `_cleanup`. Requirement and regression gates include `_require_scratch`, `_require_xfs_stress_scrub`. Important external or harness tools detected in the full source include `mkfs.xfs`, `fsstress`, `mount`. Scenario variables and harness state referenced include none.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata, runs online scrub/repair or xfs_scrub in selected modes, starts fsstress or stress-scrub helpers to exercise concurrency. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version; stress timing is intentionally nondeterministic, so regressions may appear as hangs, livelocks, kernel warnings, or post-test fsck failures.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/729.out`; stable progress/output labels such as `echo Silence is golden`; diagnostic detail appended to `$seqres.full`. The source has 35 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/729 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/730 -->
# sources/test-tools/xfstests/tests/xfs/730

## Purpose
`sources/test-tools/xfstests/tests/xfs/730` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair. Populate a XFS filesystem and fuzz every fscounter field. Use xfs_scrub to fix the corruption. The `_begin_fstest` declaration is `dangerous_fuzzers scrub fuzzers_online_repair`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/populate`, `./common/preamble`. Local helper surface: no local shell helpers beyond the main script body. Requirement and regression gates include `_require_scratch_xfs_fuzz_fields`. Important external or harness tools detected in the full source include none. Scenario variables and harness state referenced include `SCRATCH_XFS_LIST_METADATA_FIELDS`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/730.out`; stable progress/output labels such as `echo "Format and populate"`, `echo "Fuzz fscounters"`, `echo "Done fuzzing fscounters"`; diagnostic detail appended to `$seqres.full`. The source has 34 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/730 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/731 -->
# sources/test-tools/xfstests/tests/xfs/731

## Purpose
`sources/test-tools/xfstests/tests/xfs/731` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair, stress concurrency. Race fsstress and fscounter repair for a while to see if we crash or livelock. Summary counter repair requires us to freeze the filesystem to stop all filesystem activity, so we can't have userspace wandering in and thawing it. The `_begin_fstest` declaration is `online_repair fsstress_online_repair`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/inject`, `./common/preamble`, `./common/xfs`. Local helper surface: `_cleanup`. Requirement and regression gates include `_require_scratch`, `_require_xfs_stress_online_repair`. Important external or harness tools detected in the full source include `mkfs.xfs`, `fsstress`, `mount`. Scenario variables and harness state referenced include none.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata, runs online scrub/repair or xfs_scrub in selected modes, starts fsstress or stress-scrub helpers to exercise concurrency. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version; stress timing is intentionally nondeterministic, so regressions may appear as hangs, livelocks, kernel warnings, or post-test fsck failures.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/731.out`; stable progress/output labels such as `echo Silence is golden`; diagnostic detail appended to `$seqres.full`. The source has 39 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/731 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/732 -->
# sources/test-tools/xfstests/tests/xfs/732

## Purpose
`sources/test-tools/xfstests/tests/xfs/732` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair, realtime-device coverage, stress concurrency. Race fsstress and fscounter repair on the realtime device for a while to see if we crash or livelock. Summary counter repair requires us to freeze the filesystem to stop all filesystem activity, so we can't have userspace wandering in and thawing it. The `_begin_fstest` declaration is `auto quick rw scrub realtime`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/inject`, `./common/preamble`, `./common/xfs`. Local helper surface: `_cleanup`. Requirement and regression gates include `_require_scratch`, `_require_realtime`, `_require_xfs_stress_scrub`, `_require_xfs_has_feature "$SCRATCH_MNT" realtime`. Important external or harness tools detected in the full source include `mkfs.xfs`, `fsstress`, `mount`. Scenario variables and harness state referenced include `SCRATCH_MNT`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata, runs online scrub/repair or xfs_scrub in selected modes, starts fsstress or stress-scrub helpers to exercise concurrency. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version; stress timing is intentionally nondeterministic, so regressions may appear as hangs, livelocks, kernel warnings, or post-test fsck failures; realtime-device paths depend on allocation unit and feature configuration, so tests skip or change behavior when geometry is unsuitable.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/732.out`; stable progress/output labels such as `echo Silence is golden`; diagnostic detail appended to `$seqres.full`. The source has 44 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/732 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/733 -->
# sources/test-tools/xfstests/tests/xfs/733

## Purpose
`sources/test-tools/xfstests/tests/xfs/733` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair, dump/restore behavior. Populate a XFS filesystem and fuzz the data mappings of every directory type. Use xfs_scrub to fix the corruption. The `_begin_fstest` declaration is `dangerous_fuzzers scrub fuzzers_online_repair`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/populate`, `./common/preamble`. Local helper surface: no local shell helpers beyond the main script body. Requirement and regression gates include `_require_scratch_xfs_fuzz_fields`. Important external or harness tools detected in the full source include `mount`, `stat`. Scenario variables and harness state referenced include `SCRATCH_MNT`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata, uses checksum/stat comparisons as the content oracle. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/733.out`; stable progress/output labels such as `echo "Format and populate"`, `echo "Fuzz block map for ${dirtype}" | tee -a $seqres.full`, `echo "Done fuzzing dir map ${dirtype}"`; diagnostic detail appended to `$seqres.full`. The source has 46 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/733 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/734 -->
# sources/test-tools/xfstests/tests/xfs/734

## Purpose
`sources/test-tools/xfstests/tests/xfs/734` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair, dump/restore behavior. Populate a XFS filesystem and fuzz the data mappings of every directory type. Use xfs_repair to fix the corruption. The `_begin_fstest` declaration is `dangerous_fuzzers repair fuzzers_repair`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/populate`, `./common/preamble`. Local helper surface: no local shell helpers beyond the main script body. Requirement and regression gates include `_require_scratch_xfs_fuzz_fields`. Important external or harness tools detected in the full source include `mount`, `stat`. Scenario variables and harness state referenced include `SCRATCH_MNT`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata, uses checksum/stat comparisons as the content oracle. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/734.out`; stable progress/output labels such as `echo "Format and populate"`, `echo "Fuzz block map for ${dirtype}" | tee -a $seqres.full`, `echo "Done fuzzing dir map ${dirtype}"`; diagnostic detail appended to `$seqres.full`. The source has 46 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/734 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/735 -->
# sources/test-tools/xfstests/tests/xfs/735

## Purpose
`sources/test-tools/xfstests/tests/xfs/735` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair, dump/restore behavior. Populate a XFS filesystem and fuzz the data mappings of every directory type. Do not fix the filesystem, to test metadata verifiers. The `_begin_fstest` declaration is `dangerous_fuzzers fuzzers_norepair`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/populate`, `./common/preamble`. Local helper surface: no local shell helpers beyond the main script body. Requirement and regression gates include `_require_scratch_xfs_fuzz_fields`. Important external or harness tools detected in the full source include `mount`, `stat`. Scenario variables and harness state referenced include `SCRATCH_MNT`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata, uses checksum/stat comparisons as the content oracle. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/735.out`; stable progress/output labels such as `echo "Format and populate"`, `echo "Fuzz block map for ${dirtype}" | tee -a $seqres.full`, `echo "Done fuzzing dir map ${dirtype}"`; diagnostic detail appended to `$seqres.full`. The source has 46 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/735 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/736 -->
# sources/test-tools/xfstests/tests/xfs/736

## Purpose
`sources/test-tools/xfstests/tests/xfs/736` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair, attribute fork repair, dump/restore behavior. Populate a XFS filesystem and fuzz the attr mappings of every xattr type. Use xfs_scrub to fix the corruption. The `_begin_fstest` declaration is `dangerous_fuzzers scrub fuzzers_online_repair`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/populate`, `./common/preamble`. Local helper surface: no local shell helpers beyond the main script body. Requirement and regression gates include `_require_scratch_xfs_fuzz_fields`. Important external or harness tools detected in the full source include `mount`, `stat`. Scenario variables and harness state referenced include `SCRATCH_MNT`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata, sets extended attributes or validates attr-fork behavior, uses checksum/stat comparisons as the content oracle. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/736.out`; stable progress/output labels such as `echo "Format and populate"`, `echo "Fuzz block map for ${attrtype}" | tee -a $seqres.full`, `echo "Done fuzzing attr map ${attrtype}"`; diagnostic detail appended to `$seqres.full`. The source has 46 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/736 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/737 -->
# sources/test-tools/xfstests/tests/xfs/737

## Purpose
`sources/test-tools/xfstests/tests/xfs/737` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair, attribute fork repair, dump/restore behavior. Populate a XFS filesystem and fuzz the attr mappings of every xattr type. Use xfs_repair to fix the corruption. The `_begin_fstest` declaration is `dangerous_fuzzers repair fuzzers_repair`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/populate`, `./common/preamble`. Local helper surface: no local shell helpers beyond the main script body. Requirement and regression gates include `_require_scratch_xfs_fuzz_fields`. Important external or harness tools detected in the full source include `mount`, `stat`. Scenario variables and harness state referenced include `SCRATCH_MNT`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata, sets extended attributes or validates attr-fork behavior, uses checksum/stat comparisons as the content oracle. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/737.out`; stable progress/output labels such as `echo "Format and populate"`, `echo "Fuzz block map for ${attrtype}" | tee -a $seqres.full`, `echo "Done fuzzing attr map ${attrtype}"`; diagnostic detail appended to `$seqres.full`. The source has 46 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/737 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/738 -->
# sources/test-tools/xfstests/tests/xfs/738

## Purpose
`sources/test-tools/xfstests/tests/xfs/738` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair, attribute fork repair, dump/restore behavior. Populate a XFS filesystem and fuzz the attr mappings of every xattr type. Do not fix the filesystem, to test metadata verifiers. The `_begin_fstest` declaration is `dangerous_fuzzers fuzzers_norepair`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/populate`, `./common/preamble`. Local helper surface: no local shell helpers beyond the main script body. Requirement and regression gates include `_require_scratch_xfs_fuzz_fields`. Important external or harness tools detected in the full source include `mount`, `stat`. Scenario variables and harness state referenced include `SCRATCH_MNT`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata, sets extended attributes or validates attr-fork behavior, uses checksum/stat comparisons as the content oracle. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/738.out`; stable progress/output labels such as `echo "Format and populate"`, `echo "Fuzz block map for ${attrtype}" | tee -a $seqres.full`, `echo "Done fuzzing attr map ${attrtype}"`; diagnostic detail appended to `$seqres.full`. The source has 46 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/738 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/739 -->
# sources/test-tools/xfstests/tests/xfs/739

## Purpose
`sources/test-tools/xfstests/tests/xfs/739` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair, realtime-device coverage. Populate a XFS filesystem and fuzz every realtime bitmap field. Use xfs_scrub to fix the corruption. The `_begin_fstest` declaration is `dangerous_fuzzers scrub fuzzers_online_repair realtime`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/populate`, `./common/preamble`. Local helper surface: no local shell helpers beyond the main script body. Requirement and regression gates include `_require_realtime`, `_require_scratch_xfs_fuzz_fields`. Important external or harness tools detected in the full source include none. Scenario variables and harness state referenced include `SCRATCH_DEV`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version; realtime-device paths depend on allocation unit and feature configuration, so tests skip or change behavior when geometry is unsuitable.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/739.out`; stable progress/output labels such as `echo "Format and populate"`, `echo "Fuzz rtbitmap"`, `echo "Done fuzzing rtbitmap"`; diagnostic detail appended to `$seqres.full`. The source has 38 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/739 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/740 -->
# sources/test-tools/xfstests/tests/xfs/740

## Purpose
`sources/test-tools/xfstests/tests/xfs/740` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair, realtime-device coverage. Populate a XFS filesystem and fuzz every realtime summary field. Use xfs_scrub to fix the corruption. The `_begin_fstest` declaration is `dangerous_fuzzers scrub fuzzers_online_repair realtime`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/populate`, `./common/preamble`. Local helper surface: no local shell helpers beyond the main script body. Requirement and regression gates include `_require_realtime`, `_require_scratch_xfs_fuzz_fields`. Important external or harness tools detected in the full source include none. Scenario variables and harness state referenced include `SCRATCH_DEV`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version; realtime-device paths depend on allocation unit and feature configuration, so tests skip or change behavior when geometry is unsuitable.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/740.out`; stable progress/output labels such as `echo "Format and populate"`, `echo "Fuzz rtsummary"`, `echo "Done fuzzing rtsummary"`; diagnostic detail appended to `$seqres.full`. The source has 38 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/740 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/741 -->
# sources/test-tools/xfstests/tests/xfs/741

## Purpose
`sources/test-tools/xfstests/tests/xfs/741` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair, realtime-device coverage. Populate a XFS filesystem and fuzz every realtime bitmap field. Use xfs_repair to fix the corruption. The `_begin_fstest` declaration is `dangerous_fuzzers repair fuzzers_repair realtime`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/populate`, `./common/preamble`. Local helper surface: no local shell helpers beyond the main script body. Requirement and regression gates include `_require_realtime`, `_require_scratch_xfs_fuzz_fields`. Important external or harness tools detected in the full source include none. Scenario variables and harness state referenced include `SCRATCH_DEV`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version; realtime-device paths depend on allocation unit and feature configuration, so tests skip or change behavior when geometry is unsuitable.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/741.out`; stable progress/output labels such as `echo "Format and populate"`, `echo "Fuzz rtbitmap"`, `echo "Done fuzzing rtbitmap"`; diagnostic detail appended to `$seqres.full`. The source has 38 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/741 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/742 -->
# sources/test-tools/xfstests/tests/xfs/742

## Purpose
`sources/test-tools/xfstests/tests/xfs/742` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair, realtime-device coverage. Populate a XFS filesystem and fuzz every realtime summary field. Use xfs_repair to fix the corruption. The `_begin_fstest` declaration is `dangerous_fuzzers repair fuzzers_repair realtime`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/populate`, `./common/preamble`. Local helper surface: no local shell helpers beyond the main script body. Requirement and regression gates include `_require_realtime`, `_require_scratch_xfs_fuzz_fields`. Important external or harness tools detected in the full source include none. Scenario variables and harness state referenced include `SCRATCH_DEV`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version; realtime-device paths depend on allocation unit and feature configuration, so tests skip or change behavior when geometry is unsuitable.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/742.out`; stable progress/output labels such as `echo "Format and populate"`, `echo "Fuzz rtsummary"`, `echo "Done fuzzing rtsummary"`; diagnostic detail appended to `$seqres.full`. The source has 38 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/742 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/743 -->
# sources/test-tools/xfstests/tests/xfs/743

## Purpose
`sources/test-tools/xfstests/tests/xfs/743` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair, realtime-device coverage. Populate a XFS filesystem and fuzz every realtime bitmap field. Try online repair and, if necessary, offline repair, to test the most likely usage pattern. The `_begin_fstest` declaration is `dangerous_fuzzers scrub repair fuzzers_bothrepair realtime`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/populate`, `./common/preamble`. Local helper surface: no local shell helpers beyond the main script body. Requirement and regression gates include `_require_realtime`, `_require_scratch_xfs_fuzz_fields`. Important external or harness tools detected in the full source include none. Scenario variables and harness state referenced include `SCRATCH_DEV`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version; realtime-device paths depend on allocation unit and feature configuration, so tests skip or change behavior when geometry is unsuitable.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/743.out`; stable progress/output labels such as `echo "Format and populate"`, `echo "Fuzz rtbitmap"`, `echo "Done fuzzing rtbitmap"`; diagnostic detail appended to `$seqres.full`. The source has 39 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/743 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/744 -->
# sources/test-tools/xfstests/tests/xfs/744

## Purpose
`sources/test-tools/xfstests/tests/xfs/744` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair, realtime-device coverage. Populate a XFS filesystem and fuzz every realtime summary field. Try online repair and, if necessary, offline repair, to test the most likely usage pattern. The `_begin_fstest` declaration is `dangerous_fuzzers scrub repair fuzzers_bothrepair realtime`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/populate`, `./common/preamble`. Local helper surface: no local shell helpers beyond the main script body. Requirement and regression gates include `_require_realtime`, `_require_scratch_xfs_fuzz_fields`. Important external or harness tools detected in the full source include none. Scenario variables and harness state referenced include `SCRATCH_DEV`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version; realtime-device paths depend on allocation unit and feature configuration, so tests skip or change behavior when geometry is unsuitable.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/744.out`; stable progress/output labels such as `echo "Format and populate"`, `echo "Fuzz rtsummary"`, `echo "Done fuzzing rtsummary"`; diagnostic detail appended to `$seqres.full`. The source has 39 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/744 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/745 -->
# sources/test-tools/xfstests/tests/xfs/745

## Purpose
`sources/test-tools/xfstests/tests/xfs/745` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair, realtime-device coverage. Populate a XFS filesystem and fuzz every realtime bitmap field. Do not fix the filesystem, to test metadata verifiers. The `_begin_fstest` declaration is `dangerous_fuzzers fuzzers_norepair realtime`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/populate`, `./common/preamble`. Local helper surface: no local shell helpers beyond the main script body. Requirement and regression gates include `_require_realtime`, `_require_scratch_xfs_fuzz_fields`. Important external or harness tools detected in the full source include none. Scenario variables and harness state referenced include `SCRATCH_DEV`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version; realtime-device paths depend on allocation unit and feature configuration, so tests skip or change behavior when geometry is unsuitable.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/745.out`; stable progress/output labels such as `echo "Format and populate"`, `echo "Fuzz rtbitmap"`, `echo "Done fuzzing rtbitmap"`; diagnostic detail appended to `$seqres.full`. The source has 38 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/745 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/746 -->
# sources/test-tools/xfstests/tests/xfs/746

## Purpose
`sources/test-tools/xfstests/tests/xfs/746` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair, realtime-device coverage. Populate a XFS filesystem and fuzz every realtime summary field. Do not fix the filesystem, to test metadata verifiers. The `_begin_fstest` declaration is `dangerous_fuzzers fuzzers_norepair realtime`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/populate`, `./common/preamble`. Local helper surface: no local shell helpers beyond the main script body. Requirement and regression gates include `_require_realtime`, `_require_scratch_xfs_fuzz_fields`. Important external or harness tools detected in the full source include none. Scenario variables and harness state referenced include `SCRATCH_DEV`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version; realtime-device paths depend on allocation unit and feature configuration, so tests skip or change behavior when geometry is unsuitable.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/746.out`; stable progress/output labels such as `echo "Format and populate"`, `echo "Fuzz rtsummary"`, `echo "Done fuzzing rtsummary"`; diagnostic detail appended to `$seqres.full`. The source has 38 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/746 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/747 -->
# sources/test-tools/xfstests/tests/xfs/747

## Purpose
`sources/test-tools/xfstests/tests/xfs/747` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair. Populate a XFS filesystem and fuzz every superblock field. Try online repair and, if necessary, offline repair, to test the most likely usage pattern. The `_begin_fstest` declaration is `dangerous_fuzzers scrub repair fuzzers_bothrepair`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/populate`, `./common/preamble`. Local helper surface: no local shell helpers beyond the main script body. Requirement and regression gates include `_require_scratch_xfs_fuzz_fields`. Important external or harness tools detected in the full source include none. Scenario variables and harness state referenced include none.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/747.out`; stable progress/output labels such as `echo "Format and populate"`, `echo "Fuzz superblock"`, `echo "Done fuzzing superblock"`; diagnostic detail appended to `$seqres.full`. The source has 33 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/747 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/748 -->
# sources/test-tools/xfstests/tests/xfs/748

## Purpose
`sources/test-tools/xfstests/tests/xfs/748` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair. Populate a XFS filesystem and fuzz every AGF field. Try online repair and, if necessary, offline repair, to test the most likely usage pattern. The `_begin_fstest` declaration is `dangerous_fuzzers scrub repair fuzzers_bothrepair`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/populate`, `./common/preamble`. Local helper surface: no local shell helpers beyond the main script body. Requirement and regression gates include `_require_scratch_xfs_fuzz_fields`. Important external or harness tools detected in the full source include none. Scenario variables and harness state referenced include none.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/748.out`; stable progress/output labels such as `echo "Format and populate"`, `echo "Fuzz AGF"`, `echo "Done fuzzing AGF"`; diagnostic detail appended to `$seqres.full`. The source has 33 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/748 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/749 -->
# sources/test-tools/xfstests/tests/xfs/749

## Purpose
`sources/test-tools/xfstests/tests/xfs/749` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair, dump/restore behavior. Populate a XFS filesystem and fuzz every AGFL field. Try online repair and, if necessary, offline repair, to test the most likely usage pattern. The `_begin_fstest` declaration is `dangerous_fuzzers scrub repair fuzzers_bothrepair`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/populate`, `./common/preamble`. Local helper surface: no local shell helpers beyond the main script body. Requirement and regression gates include `_require_scratch_xfs_fuzz_fields`. Important external or harness tools detected in the full source include `xfs_db`. Scenario variables and harness state referenced include `SCRATCH_XFS_LIST_METADATA_FIELDS`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/749.out`; stable progress/output labels such as `echo "Format and populate"`, `echo "Fuzz AGFL"`, `echo "Done fuzzing AGFL"`, `echo "Fuzz AGFL flfirst"`, `echo "Done fuzzing AGFL flfirst"`; diagnostic detail appended to `$seqres.full`. The source has 43 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/749 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/750 -->
# sources/test-tools/xfstests/tests/xfs/750

## Purpose
`sources/test-tools/xfstests/tests/xfs/750` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair. Populate a XFS filesystem and fuzz every AGI field. Try online repair and, if necessary, offline repair, to test the most likely usage pattern. The `_begin_fstest` declaration is `dangerous_fuzzers scrub repair fuzzers_bothrepair`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/populate`, `./common/preamble`. Local helper surface: no local shell helpers beyond the main script body. Requirement and regression gates include `_require_scratch_xfs_fuzz_fields`. Important external or harness tools detected in the full source include none. Scenario variables and harness state referenced include none.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/750.out`; stable progress/output labels such as `echo "Format and populate"`, `echo "Fuzz AGI"`, `echo "Done fuzzing AGI"`; diagnostic detail appended to `$seqres.full`. The source has 33 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/750 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/751 -->
# sources/test-tools/xfstests/tests/xfs/751

## Purpose
`sources/test-tools/xfstests/tests/xfs/751` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair. Populate a XFS filesystem and fuzz every bnobt field. Try online repair and, if necessary, offline repair, to test the most likely usage pattern. The `_begin_fstest` declaration is `dangerous_fuzzers scrub repair fuzzers_bothrepair`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/populate`, `./common/preamble`. Local helper surface: no local shell helpers beyond the main script body. Requirement and regression gates include `_require_scratch_xfs_fuzz_fields`. Important external or harness tools detected in the full source include none. Scenario variables and harness state referenced include none.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/751.out`; stable progress/output labels such as `echo "Format and populate"`, `echo "Fuzz bnobt recs"`, `echo "Done fuzzing bnobt recs"`; diagnostic detail appended to `$seqres.full`; hard failures through `_fail` assertions. The source has 36 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/751 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/752 -->
# sources/test-tools/xfstests/tests/xfs/752

## Purpose
`sources/test-tools/xfstests/tests/xfs/752` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair. Populate a XFS filesystem and fuzz every bnobt key/pointer. Try online repair and, if necessary, offline repair, to test the most likely usage pattern. The `_begin_fstest` declaration is `dangerous_fuzzers scrub repair fuzzers_bothrepair`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/populate`, `./common/preamble`. Local helper surface: no local shell helpers beyond the main script body. Requirement and regression gates include `_require_scratch_xfs_fuzz_fields`. Important external or harness tools detected in the full source include none. Scenario variables and harness state referenced include none.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/752.out`; stable progress/output labels such as `echo "Format and populate"`, `echo "Fuzz bnobt keyptr"`, `echo "Done fuzzing bnobt keyptr"`; diagnostic detail appended to `$seqres.full`; hard failures through `_fail` assertions. The source has 36 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/752 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/753 -->
# sources/test-tools/xfstests/tests/xfs/753

## Purpose
`sources/test-tools/xfstests/tests/xfs/753` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair. Populate a XFS filesystem and fuzz every cntbt field. Try online repair and, if necessary, offline repair, to test the most likely usage pattern. The `_begin_fstest` declaration is `dangerous_fuzzers scrub repair fuzzers_bothrepair`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/populate`, `./common/preamble`. Local helper surface: no local shell helpers beyond the main script body. Requirement and regression gates include `_require_scratch_xfs_fuzz_fields`. Important external or harness tools detected in the full source include none. Scenario variables and harness state referenced include none.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/753.out`; stable progress/output labels such as `echo "Format and populate"`, `echo "Fuzz cntbt"`, `echo "Done fuzzing cntbt"`; diagnostic detail appended to `$seqres.full`; hard failures through `_fail` assertions. The source has 36 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/753 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/754 -->
# sources/test-tools/xfstests/tests/xfs/754

## Purpose
`sources/test-tools/xfstests/tests/xfs/754` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair. Populate a XFS filesystem and fuzz every inobt field. Try online repair and, if necessary, offline repair, to test the most likely usage pattern. The `_begin_fstest` declaration is `dangerous_fuzzers scrub repair fuzzers_bothrepair`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/populate`, `./common/preamble`. Local helper surface: no local shell helpers beyond the main script body. Requirement and regression gates include `_require_scratch_xfs_fuzz_fields`. Important external or harness tools detected in the full source include none. Scenario variables and harness state referenced include none.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/754.out`; stable progress/output labels such as `echo "Format and populate"`, `echo "Fuzz inobt"`, `echo "Done fuzzing inobt"`; diagnostic detail appended to `$seqres.full`; hard failures through `_fail` assertions. The source has 36 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/754 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/755 -->
# sources/test-tools/xfstests/tests/xfs/755

## Purpose
`sources/test-tools/xfstests/tests/xfs/755` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair. Populate a XFS filesystem and fuzz every finobt field. Try online repair and, if necessary, offline repair, to test the most likely usage pattern. The `_begin_fstest` declaration is `dangerous_fuzzers scrub repair fuzzers_bothrepair`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/populate`, `./common/preamble`. Local helper surface: no local shell helpers beyond the main script body. Requirement and regression gates include `_require_scratch_xfs_fuzz_fields`, `_require_xfs_finobt`. Important external or harness tools detected in the full source include none. Scenario variables and harness state referenced include none.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/755.out`; stable progress/output labels such as `echo "Format and populate"`, `echo "Fuzz finobt"`, `echo "Done fuzzing finobt"`; diagnostic detail appended to `$seqres.full`; hard failures through `_fail` assertions. The source has 37 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/755 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/756 -->
# sources/test-tools/xfstests/tests/xfs/756

## Purpose
`sources/test-tools/xfstests/tests/xfs/756` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair. Populate a XFS filesystem and fuzz every rmapbt field. Try online repair and, if necessary, offline repair, to test the most likely usage pattern. The `_begin_fstest` declaration is `dangerous_fuzzers scrub repair fuzzers_bothrepair`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/populate`, `./common/preamble`. Local helper surface: no local shell helpers beyond the main script body. Requirement and regression gates include `_require_xfs_scratch_rmapbt`, `_require_scratch_xfs_fuzz_fields`. Important external or harness tools detected in the full source include none. Scenario variables and harness state referenced include none.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/756.out`; stable progress/output labels such as `echo "Format and populate"`, `echo "Fuzz rmapbt recs"`, `echo "Done fuzzing rmapbt recs"`; diagnostic detail appended to `$seqres.full`; hard failures through `_fail` assertions. The source has 37 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/756 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/757 -->
# sources/test-tools/xfstests/tests/xfs/757

## Purpose
`sources/test-tools/xfstests/tests/xfs/757` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair. Populate a XFS filesystem and fuzz every rmapbt key/pointer field. Try online repair and, if necessary, offline repair, to test the most likely usage pattern. The `_begin_fstest` declaration is `dangerous_fuzzers scrub repair fuzzers_bothrepair`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/populate`, `./common/preamble`. Local helper surface: no local shell helpers beyond the main script body. Requirement and regression gates include `_require_xfs_scratch_rmapbt`, `_require_scratch_xfs_fuzz_fields`. Important external or harness tools detected in the full source include none. Scenario variables and harness state referenced include none.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/757.out`; stable progress/output labels such as `echo "Format and populate"`, `echo "Fuzz rmapbt keyptr"`, `echo "Done fuzzing rmapbt keyptr"`; diagnostic detail appended to `$seqres.full`; hard failures through `_fail` assertions. The source has 37 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/757 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/758 -->
# sources/test-tools/xfstests/tests/xfs/758

## Purpose
`sources/test-tools/xfstests/tests/xfs/758` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair. Populate a XFS filesystem and fuzz every refcountbt key/pointer field. Try online repair and, if necessary, offline repair, to test the most likely usage pattern. The `_begin_fstest` declaration is `dangerous_fuzzers scrub repair fuzzers_bothrepair`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/populate`, `./common/preamble`, `./common/reflink`. Local helper surface: no local shell helpers beyond the main script body. Requirement and regression gates include `_require_scratch_reflink`, `_require_scratch_xfs_fuzz_fields`. Important external or harness tools detected in the full source include none. Scenario variables and harness state referenced include none.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/758.out`; stable progress/output labels such as `echo "Format and populate"`, `echo "Fuzz refcountbt"`, `echo "Done fuzzing refcountbt"`; diagnostic detail appended to `$seqres.full`; hard failures through `_fail` assertions. The source has 38 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/758 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/759 -->
# sources/test-tools/xfstests/tests/xfs/759

## Purpose
`sources/test-tools/xfstests/tests/xfs/759` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair. Populate a XFS filesystem and fuzz every btree-format directory inode field. Try online repair and, if necessary, offline repair, to test the most likely usage pattern. The `_begin_fstest` declaration is `dangerous_fuzzers scrub repair fuzzers_bothrepair`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/populate`, `./common/preamble`. Local helper surface: no local shell helpers beyond the main script body. Requirement and regression gates include `_require_scratch_xfs_fuzz_fields`. Important external or harness tools detected in the full source include `mount`, `stat`. Scenario variables and harness state referenced include `SCRATCH_MNT`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata, uses checksum/stat comparisons as the content oracle. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/759.out`; stable progress/output labels such as `echo "Format and populate"`, `echo "Find btree-format dir inode"`, `echo "Fuzz inode"`, `echo "Done fuzzing inode"`; diagnostic detail appended to `$seqres.full`. The source has 38 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/759 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/760 -->
# sources/test-tools/xfstests/tests/xfs/760

## Purpose
`sources/test-tools/xfstests/tests/xfs/760` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair. Populate a XFS filesystem and fuzz every extents-format file inode field. Try online repair and, if necessary, offline repair, to test the most likely usage pattern. The `_begin_fstest` declaration is `dangerous_fuzzers scrub repair fuzzers_bothrepair`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/populate`, `./common/preamble`. Local helper surface: no local shell helpers beyond the main script body. Requirement and regression gates include `_require_scratch_xfs_fuzz_fields`. Important external or harness tools detected in the full source include `mount`, `stat`. Scenario variables and harness state referenced include `SCRATCH_MNT`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata, uses checksum/stat comparisons as the content oracle. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/760.out`; stable progress/output labels such as `echo "Format and populate"`, `echo "Find extents-format file inode"`, `echo "Fuzz inode"`, `echo "Done fuzzing inode"`; diagnostic detail appended to `$seqres.full`. The source has 38 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/760 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/761 -->
# sources/test-tools/xfstests/tests/xfs/761

## Purpose
`sources/test-tools/xfstests/tests/xfs/761` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair. Populate a XFS filesystem and fuzz every btree-format file inode field. Try online repair and, if necessary, offline repair, to test the most likely usage pattern. The `_begin_fstest` declaration is `dangerous_fuzzers scrub repair fuzzers_bothrepair`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/populate`, `./common/preamble`. Local helper surface: no local shell helpers beyond the main script body. Requirement and regression gates include `_require_scratch_xfs_fuzz_fields`. Important external or harness tools detected in the full source include `mount`, `stat`. Scenario variables and harness state referenced include `SCRATCH_MNT`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata, uses checksum/stat comparisons as the content oracle. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/761.out`; stable progress/output labels such as `echo "Format and populate"`, `echo "Find btree-format file inode"`, `echo "Fuzz inode"`, `echo "Done fuzzing inode"`; diagnostic detail appended to `$seqres.full`. The source has 38 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/761 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/762 -->
# sources/test-tools/xfstests/tests/xfs/762

## Purpose
`sources/test-tools/xfstests/tests/xfs/762` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair, extent mapping and exchange. Populate a XFS filesystem and fuzz every bmbt block field. Try online repair and, if necessary, offline repair, to test the most likely usage pattern. The `_begin_fstest` declaration is `dangerous_fuzzers scrub repair fuzzers_bothrepair`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/populate`, `./common/preamble`. Local helper surface: no local shell helpers beyond the main script body. Requirement and regression gates include `_require_scratch_xfs_fuzz_fields`. Important external or harness tools detected in the full source include `mount`, `stat`. Scenario variables and harness state referenced include `SCRATCH_MNT`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata, uses checksum/stat comparisons as the content oracle. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/762.out`; stable progress/output labels such as `echo "Format and populate"`, `echo "Find bmbt block"`, `echo "Fuzz bmbt"`, `echo "Done fuzzing bmbt"`; diagnostic detail appended to `$seqres.full`. The source has 40 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/762 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/763 -->
# sources/test-tools/xfstests/tests/xfs/763

## Purpose
`sources/test-tools/xfstests/tests/xfs/763` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair. Populate a XFS filesystem and fuzz every symlink remote block field. Try online repair and, if necessary, offline repair, to test the most likely usage pattern. The `_begin_fstest` declaration is `dangerous_fuzzers scrub repair fuzzers_bothrepair`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/populate`, `./common/preamble`. Local helper surface: no local shell helpers beyond the main script body. Requirement and regression gates include `_require_scratch_xfs_fuzz_fields`. Important external or harness tools detected in the full source include `mount`, `stat`. Scenario variables and harness state referenced include `SCRATCH_MNT`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata, uses checksum/stat comparisons as the content oracle. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/763.out`; stable progress/output labels such as `echo "Format and populate"`, `echo "Find symlink remote block"`, `echo "Fuzz symlink remote block"`, `echo "Done fuzzing symlink remote block"`; diagnostic detail appended to `$seqres.full`. The source has 38 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/763 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/764 -->
# sources/test-tools/xfstests/tests/xfs/764

## Purpose
`sources/test-tools/xfstests/tests/xfs/764` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair. Populate a XFS filesystem and fuzz every inline directory inode field. Try online repair and, if necessary, offline repair, to test the most likely usage pattern. The `_begin_fstest` declaration is `dangerous_fuzzers scrub repair fuzzers_bothrepair`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/populate`, `./common/preamble`. Local helper surface: no local shell helpers beyond the main script body. Requirement and regression gates include `_require_scratch_xfs_fuzz_fields`. Important external or harness tools detected in the full source include `mount`, `stat`. Scenario variables and harness state referenced include `SCRATCH_MNT`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata, uses checksum/stat comparisons as the content oracle. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/764.out`; stable progress/output labels such as `echo "Format and populate"`, `echo "Find inline-format dir inode"`, `echo "Fuzz inline-format dir inode"`, `echo "Done fuzzing inline-format dir inode"`; diagnostic detail appended to `$seqres.full`. The source has 38 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/764 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/765 -->
# sources/test-tools/xfstests/tests/xfs/765

## Purpose
`sources/test-tools/xfstests/tests/xfs/765` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair, directory tree and parent-pointer repair. Populate a XFS filesystem and fuzz every block-format dir block field. Try online repair and, if necessary, offline repair, to test the most likely usage pattern. The `_begin_fstest` declaration is `dangerous_fuzzers scrub repair fuzzers_bothrepair`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/populate`, `./common/preamble`. Local helper surface: no local shell helpers beyond the main script body. Requirement and regression gates include `_require_scratch_xfs_fuzz_fields`. Important external or harness tools detected in the full source include `mount`, `stat`. Scenario variables and harness state referenced include `SCRATCH_MNT`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata, uses checksum/stat comparisons as the content oracle. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/765.out`; stable progress/output labels such as `echo "Format and populate"`, `echo "Find data-format dir block"`, `echo "Fuzz data-format dir block"`, `echo "Done fuzzing data-format dir block"`; diagnostic detail appended to `$seqres.full`. The source has 38 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/765 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/766 -->
# sources/test-tools/xfstests/tests/xfs/766

## Purpose
`sources/test-tools/xfstests/tests/xfs/766` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair, directory tree and parent-pointer repair. Populate a XFS filesystem and fuzz every data-format dir block field. Try online repair and, if necessary, offline repair, to test the most likely usage pattern. The `_begin_fstest` declaration is `dangerous_fuzzers scrub repair fuzzers_bothrepair`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/populate`, `./common/preamble`. Local helper surface: no local shell helpers beyond the main script body. Requirement and regression gates include `_require_scratch_xfs_fuzz_fields`. Important external or harness tools detected in the full source include `mount`, `stat`. Scenario variables and harness state referenced include `SCRATCH_MNT`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata, uses checksum/stat comparisons as the content oracle. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/766.out`; stable progress/output labels such as `echo "Format and populate"`, `echo "Find data-format dir block"`, `echo "Fuzz data-format dir block"`, `echo "Done fuzzing data-format dir block"`; diagnostic detail appended to `$seqres.full`. The source has 39 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/766 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/767 -->
# sources/test-tools/xfstests/tests/xfs/767

## Purpose
`sources/test-tools/xfstests/tests/xfs/767` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair, directory tree and parent-pointer repair. Populate a XFS filesystem and fuzz every leaf1-format dir block field. Try online repair and, if necessary, offline repair, to test the most likely usage pattern. The `_begin_fstest` declaration is `dangerous_fuzzers scrub repair fuzzers_bothrepair`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/populate`, `./common/preamble`. Local helper surface: no local shell helpers beyond the main script body. Requirement and regression gates include `_require_scratch_xfs_fuzz_fields`. Important external or harness tools detected in the full source include `mount`, `stat`. Scenario variables and harness state referenced include `SCRATCH_MNT`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata, uses checksum/stat comparisons as the content oracle. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/767.out`; stable progress/output labels such as `echo "Format and populate"`, `echo "Find leaf1-format dir block"`, `echo "Fuzz leaf1-format dir block"`, `echo "Done fuzzing leaf1-format dir block"`; diagnostic detail appended to `$seqres.full`. The source has 40 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/767 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/768 -->
# sources/test-tools/xfstests/tests/xfs/768

## Purpose
`sources/test-tools/xfstests/tests/xfs/768` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair, directory tree and parent-pointer repair. Populate a XFS filesystem and fuzz every leafn-format dir block field. Try online repair and, if necessary, offline repair, to test the most likely usage pattern. The `_begin_fstest` declaration is `dangerous_fuzzers scrub repair fuzzers_bothrepair`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/populate`, `./common/preamble`. Local helper surface: no local shell helpers beyond the main script body. Requirement and regression gates include `_require_scratch_xfs_fuzz_fields`. Important external or harness tools detected in the full source include `mount`, `stat`. Scenario variables and harness state referenced include `SCRATCH_MNT`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata, uses checksum/stat comparisons as the content oracle. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/768.out`; stable progress/output labels such as `echo "Format and populate"`, `echo "Find leafn-format dir block"`, `echo "Fuzz leafn-format dir block"`, `echo "Done fuzzing leafn-format dir block"`; diagnostic detail appended to `$seqres.full`. The source has 40 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/768 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/769 -->
# sources/test-tools/xfstests/tests/xfs/769

## Purpose
`sources/test-tools/xfstests/tests/xfs/769` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair, directory tree and parent-pointer repair. Populate a XFS filesystem and fuzz every node-format dir block field. Try online repair and, if necessary, offline repair, to test the most likely usage pattern. The `_begin_fstest` declaration is `dangerous_fuzzers scrub repair fuzzers_bothrepair`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/populate`, `./common/preamble`. Local helper surface: no local shell helpers beyond the main script body. Requirement and regression gates include `_require_scratch_xfs_fuzz_fields`. Important external or harness tools detected in the full source include `mount`, `stat`. Scenario variables and harness state referenced include `SCRATCH_MNT`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata, uses checksum/stat comparisons as the content oracle. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/769.out`; stable progress/output labels such as `echo "Format and populate"`, `echo "Find node-format dir block"`, `echo "Fuzz node-format dir block"`, `echo "Done fuzzing node-format dir block"`; diagnostic detail appended to `$seqres.full`. The source has 40 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/769 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/770 -->
# sources/test-tools/xfstests/tests/xfs/770

## Purpose
`sources/test-tools/xfstests/tests/xfs/770` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair, directory tree and parent-pointer repair. Populate a XFS filesystem and fuzz every freeindex-format dir block field. Try online repair and, if necessary, offline repair, to test the most likely usage pattern. The `_begin_fstest` declaration is `dangerous_fuzzers scrub repair fuzzers_bothrepair`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/populate`, `./common/preamble`. Local helper surface: no local shell helpers beyond the main script body. Requirement and regression gates include `_require_scratch_xfs_fuzz_fields`. Important external or harness tools detected in the full source include `mount`, `stat`. Scenario variables and harness state referenced include `SCRATCH_MNT`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata, uses checksum/stat comparisons as the content oracle. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/770.out`; stable progress/output labels such as `echo "Format and populate"`, `echo "Find freeindex-format dir block"`, `echo "Fuzz freeindex-format dir block"`, `echo "Done fuzzing freeindex-format dir block"`; diagnostic detail appended to `$seqres.full`. The source has 40 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/770 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/771 -->
# sources/test-tools/xfstests/tests/xfs/771

## Purpose
`sources/test-tools/xfstests/tests/xfs/771` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair. Populate a XFS filesystem and fuzz every inline attr inode field. Try online repair and, if necessary, offline repair, to test the most likely usage pattern. The `_begin_fstest` declaration is `dangerous_fuzzers scrub repair fuzzers_bothrepair`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/populate`, `./common/preamble`. Local helper surface: no local shell helpers beyond the main script body. Requirement and regression gates include `_require_scratch_xfs_fuzz_fields`. Important external or harness tools detected in the full source include `mount`, `stat`. Scenario variables and harness state referenced include `SCRATCH_MNT`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata, uses checksum/stat comparisons as the content oracle. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/771.out`; stable progress/output labels such as `echo "Format and populate"`, `echo "Find inline-format attr inode"`, `echo "Fuzz inline-format attr inode"`, `echo "Done fuzzing inline-format attr inode"`; diagnostic detail appended to `$seqres.full`. The source has 38 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/771 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/772 -->
# sources/test-tools/xfstests/tests/xfs/772

## Purpose
`sources/test-tools/xfstests/tests/xfs/772` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair. Populate a XFS filesystem and fuzz every leaf-format attr block field. Try online repair and, if necessary, offline repair, to test the most likely usage pattern. The `_begin_fstest` declaration is `dangerous_fuzzers scrub repair fuzzers_bothrepair`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/populate`, `./common/preamble`. Local helper surface: no local shell helpers beyond the main script body. Requirement and regression gates include `_require_scratch_xfs_fuzz_fields`. Important external or harness tools detected in the full source include `mount`, `stat`. Scenario variables and harness state referenced include `SCRATCH_MNT`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata, uses checksum/stat comparisons as the content oracle. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/772.out`; stable progress/output labels such as `echo "Format and populate"`, `echo "Find leaf-format attr block"`, `echo "Fuzz leaf-format attr block"`, `echo "Done fuzzing leaf-format attr block"`; diagnostic detail appended to `$seqres.full`. The source has 38 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/772 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/773 -->
# sources/test-tools/xfstests/tests/xfs/773

## Purpose
`sources/test-tools/xfstests/tests/xfs/773` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair. Populate a XFS filesystem and fuzz every node-format attr block field. Try online repair and, if necessary, offline repair, to test the most likely usage pattern. The `_begin_fstest` declaration is `dangerous_fuzzers scrub repair fuzzers_bothrepair`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/populate`, `./common/preamble`. Local helper surface: no local shell helpers beyond the main script body. Requirement and regression gates include `_require_scratch_xfs_fuzz_fields`. Important external or harness tools detected in the full source include `mount`, `stat`. Scenario variables and harness state referenced include `SCRATCH_MNT`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata, uses checksum/stat comparisons as the content oracle. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/773.out`; stable progress/output labels such as `echo "Format and populate"`, `echo "Find node-format attr block"`, `echo "Fuzz node-format attr block"`, `echo "Done fuzzing node-format attr block"`; diagnostic detail appended to `$seqres.full`. The source has 38 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/773 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/774 -->
# sources/test-tools/xfstests/tests/xfs/774

## Purpose
`sources/test-tools/xfstests/tests/xfs/774` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair. Populate a XFS filesystem and fuzz every external attr block field. Try online repair and, if necessary, offline repair, to test the most likely usage pattern. The `_begin_fstest` declaration is `dangerous_fuzzers scrub repair fuzzers_bothrepair`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/populate`, `./common/preamble`. Local helper surface: no local shell helpers beyond the main script body. Requirement and regression gates include `_require_scratch_xfs_fuzz_fields`. Important external or harness tools detected in the full source include `mount`, `stat`. Scenario variables and harness state referenced include `SCRATCH_MNT`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata, uses checksum/stat comparisons as the content oracle. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/774.out`; stable progress/output labels such as `echo "Format and populate"`, `echo "Find external attr block"`, `echo "Fuzz external attr block"`, `echo "Done fuzzing external attr block"`; diagnostic detail appended to `$seqres.full`. The source has 38 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/774 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/775 -->
# sources/test-tools/xfstests/tests/xfs/775

## Purpose
`sources/test-tools/xfstests/tests/xfs/775` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair. Populate a XFS filesystem and fuzz every refcountbt field. Try online repair and, if necessary, offline repair, to test the most likely usage pattern. The `_begin_fstest` declaration is `dangerous_fuzzers scrub repair fuzzers_bothrepair`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/populate`, `./common/preamble`, `./common/reflink`. Local helper surface: no local shell helpers beyond the main script body. Requirement and regression gates include `_require_scratch_reflink`, `_require_scratch_xfs_fuzz_fields`. Important external or harness tools detected in the full source include none. Scenario variables and harness state referenced include none.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/775.out`; stable progress/output labels such as `echo "Format and populate"`, `echo "Fuzz refcountbt"`, `echo "Done fuzzing refcountbt"`; diagnostic detail appended to `$seqres.full`; hard failures through `_fail` assertions. The source has 38 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/775 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/776 -->
# sources/test-tools/xfstests/tests/xfs/776

## Purpose
`sources/test-tools/xfstests/tests/xfs/776` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair. Populate a XFS filesystem and fuzz every btree-format attr inode field. Try online repair and, if necessary, offline repair, to test the most likely usage pattern. The `_begin_fstest` declaration is `dangerous_fuzzers scrub repair fuzzers_bothrepair`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/populate`, `./common/preamble`. Local helper surface: no local shell helpers beyond the main script body. Requirement and regression gates include `_require_scratch_xfs_fuzz_fields`. Important external or harness tools detected in the full source include `mount`, `stat`. Scenario variables and harness state referenced include `SCRATCH_MNT`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata, uses checksum/stat comparisons as the content oracle. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/776.out`; stable progress/output labels such as `echo "Format and populate"`, `echo "Find btree-format attr inode"`, `echo "Fuzz inode"`, `echo "Done fuzzing inode"`; diagnostic detail appended to `$seqres.full`. The source has 38 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/776 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/777 -->
# sources/test-tools/xfstests/tests/xfs/777

## Purpose
`sources/test-tools/xfstests/tests/xfs/777` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair. Populate a XFS filesystem and fuzz every blockdev inode field. Try online repair and, if necessary, offline repair, to test the most likely usage pattern. The `_begin_fstest` declaration is `dangerous_fuzzers scrub repair fuzzers_bothrepair`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/populate`, `./common/preamble`. Local helper surface: no local shell helpers beyond the main script body. Requirement and regression gates include `_require_scratch_xfs_fuzz_fields`. Important external or harness tools detected in the full source include `mount`, `stat`. Scenario variables and harness state referenced include `SCRATCH_MNT`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata, uses checksum/stat comparisons as the content oracle. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/777.out`; stable progress/output labels such as `echo "Format and populate"`, `echo "Find blockdev inode"`, `echo "Fuzz inode"`, `echo "Done fuzzing inode"`; diagnostic detail appended to `$seqres.full`. The source has 38 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/777 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/778 -->
# sources/test-tools/xfstests/tests/xfs/778

## Purpose
`sources/test-tools/xfstests/tests/xfs/778` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair. Populate a XFS filesystem and fuzz every local-format symlink inode field. Try online repair and, if necessary, offline repair, to test the most likely usage pattern. The `_begin_fstest` declaration is `dangerous_fuzzers scrub repair fuzzers_bothrepair`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/populate`, `./common/preamble`. Local helper surface: no local shell helpers beyond the main script body. Requirement and regression gates include `_require_scratch_xfs_fuzz_fields`. Important external or harness tools detected in the full source include `mount`, `stat`. Scenario variables and harness state referenced include `SCRATCH_MNT`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata, uses checksum/stat comparisons as the content oracle. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/778.out`; stable progress/output labels such as `echo "Format and populate"`, `echo "Find local-format symlink inode"`, `echo "Fuzz inode"`, `echo "Done fuzzing inode"`; diagnostic detail appended to `$seqres.full`. The source has 38 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/778 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/779 -->
# sources/test-tools/xfstests/tests/xfs/779

## Purpose
`sources/test-tools/xfstests/tests/xfs/779` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair, quota enforcement. Populate a XFS filesystem and fuzz every user dquot field. Try online repair and, if necessary, offline repair, to test the most likely usage pattern. The `_begin_fstest` declaration is `dangerous_fuzzers scrub repair fuzzers_bothrepair`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/populate`, `./common/preamble`, `./common/quota`. Local helper surface: no local shell helpers beyond the main script body. Requirement and regression gates include `_require_scratch_xfs_fuzz_fields`, `_require_quota`. Important external or harness tools detected in the full source include `mount`. Scenario variables and harness state referenced include `SCRATCH_DEV`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata, sets up quota state and validates accounting or enforcement. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version; quota tests depend on user/group setup, mount options, and stable quota-tools output.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/779.out`; stable progress/output labels such as `echo "Format and populate"`, `echo "Fuzz user $id dquot"`, `echo "Done fuzzing dquot"`; diagnostic detail appended to `$seqres.full`; feature-dependent skips through `_notrun`. The source has 43 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/779 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/780 -->
# sources/test-tools/xfstests/tests/xfs/780

## Purpose
`sources/test-tools/xfstests/tests/xfs/780` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair, quota enforcement. Populate a XFS filesystem and fuzz every group dquot field. Try online repair and, if necessary, offline repair, to test the most likely usage pattern. The `_begin_fstest` declaration is `dangerous_fuzzers scrub repair fuzzers_bothrepair`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/populate`, `./common/preamble`, `./common/quota`. Local helper surface: no local shell helpers beyond the main script body. Requirement and regression gates include `_require_scratch_xfs_fuzz_fields`, `_require_quota`. Important external or harness tools detected in the full source include `mount`. Scenario variables and harness state referenced include `SCRATCH_DEV`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata, sets up quota state and validates accounting or enforcement. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version; quota tests depend on user/group setup, mount options, and stable quota-tools output.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/780.out`; stable progress/output labels such as `echo "Format and populate"`, `echo "Fuzz group $id dquot"`, `echo "Done fuzzing dquot"`; diagnostic detail appended to `$seqres.full`; feature-dependent skips through `_notrun`. The source has 43 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/780 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/781 -->
# sources/test-tools/xfstests/tests/xfs/781

## Purpose
`sources/test-tools/xfstests/tests/xfs/781` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair, quota enforcement. Populate a XFS filesystem and fuzz every project dquot field. Try online repair and, if necessary, offline repair, to test the most likely usage pattern. The `_begin_fstest` declaration is `dangerous_fuzzers scrub repair fuzzers_bothrepair`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/populate`, `./common/preamble`, `./common/quota`. Local helper surface: no local shell helpers beyond the main script body. Requirement and regression gates include `_require_scratch_xfs_fuzz_fields`, `_require_quota`. Important external or harness tools detected in the full source include `mount`. Scenario variables and harness state referenced include `SCRATCH_DEV`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata, sets up quota state and validates accounting or enforcement. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version; quota tests depend on user/group setup, mount options, and stable quota-tools output.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/781.out`; stable progress/output labels such as `echo "Format and populate"`, `echo "Fuzz project $id dquot"`, `echo "Done fuzzing dquot"`; diagnostic detail appended to `$seqres.full`; feature-dependent skips through `_notrun`. The source has 43 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/781 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/782 -->
# sources/test-tools/xfstests/tests/xfs/782

## Purpose
`sources/test-tools/xfstests/tests/xfs/782` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair, directory tree and parent-pointer repair. Populate a XFS filesystem and fuzz every single-leafn-format dir block field. Try online repair and, if necessary, offline repair, to test the most likely usage pattern. The `_begin_fstest` declaration is `dangerous_fuzzers scrub repair fuzzers_bothrepair`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/populate`, `./common/preamble`. Local helper surface: no local shell helpers beyond the main script body. Requirement and regression gates include `_require_scratch_xfs_fuzz_fields`. Important external or harness tools detected in the full source include `mount`, `stat`. Scenario variables and harness state referenced include `SCRATCH_MNT`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata, uses checksum/stat comparisons as the content oracle. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/782.out`; stable progress/output labels such as `echo "Format and populate"`, `echo "Find single-leafn-format dir block"`, `echo "Fuzz single-leafn-format dir block"`, `echo "Done fuzzing single-leafn-format dir block"`; diagnostic detail appended to `$seqres.full`. The source has 39 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/782 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/783 -->
# sources/test-tools/xfstests/tests/xfs/783

## Purpose
`sources/test-tools/xfstests/tests/xfs/783` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair, dump/restore behavior. Populate a XFS filesystem and fuzz the data mappings of every directory type. Try online repair and, if necessary, offline repair, to test the most likely usage pattern. The `_begin_fstest` declaration is `dangerous_fuzzers scrub repair fuzzers_bothrepair`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/populate`, `./common/preamble`. Local helper surface: no local shell helpers beyond the main script body. Requirement and regression gates include `_require_scratch_xfs_fuzz_fields`. Important external or harness tools detected in the full source include `mount`, `stat`. Scenario variables and harness state referenced include `SCRATCH_MNT`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata, uses checksum/stat comparisons as the content oracle. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/783.out`; stable progress/output labels such as `echo "Format and populate"`, `echo "Fuzz block map for ${dirtype}" | tee -a $seqres.full`, `echo "Done fuzzing dir map ${dirtype}"`; diagnostic detail appended to `$seqres.full`. The source has 47 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/783 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/784 -->
# sources/test-tools/xfstests/tests/xfs/784

## Purpose
`sources/test-tools/xfstests/tests/xfs/784` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair, attribute fork repair, dump/restore behavior. Populate a XFS filesystem and fuzz the attr mappings of every xattr type. Try online repair and, if necessary, offline repair, to test the most likely usage pattern. The `_begin_fstest` declaration is `dangerous_fuzzers scrub repair fuzzers_bothrepair`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/populate`, `./common/preamble`. Local helper surface: no local shell helpers beyond the main script body. Requirement and regression gates include `_require_scratch_xfs_fuzz_fields`. Important external or harness tools detected in the full source include `mount`, `stat`. Scenario variables and harness state referenced include `SCRATCH_MNT`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata, sets extended attributes or validates attr-fork behavior, uses checksum/stat comparisons as the content oracle. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/784.out`; stable progress/output labels such as `echo "Format and populate"`, `echo "Fuzz block map for ${attrtype}" | tee -a $seqres.full`, `echo "Done fuzzing attr map ${attrtype}"`; diagnostic detail appended to `$seqres.full`. The source has 47 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/784 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/785 -->
# sources/test-tools/xfstests/tests/xfs/785

## Purpose
`sources/test-tools/xfstests/tests/xfs/785` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair. Populate a XFS filesystem and fuzz every inobt key/pointer field. Use xfs_repair to fix the corruption. The `_begin_fstest` declaration is `dangerous_fuzzers repair fuzzers_repair`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/populate`, `./common/preamble`. Local helper surface: no local shell helpers beyond the main script body. Requirement and regression gates include `_require_scratch_xfs_fuzz_fields`. Important external or harness tools detected in the full source include none. Scenario variables and harness state referenced include none.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/785.out`; stable progress/output labels such as `echo "Format and populate"`, `echo "Fuzz inobt"`, `echo "Done fuzzing inobt"`; diagnostic detail appended to `$seqres.full`; hard failures through `_fail` assertions. The source has 34 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/785 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/786 -->
# sources/test-tools/xfstests/tests/xfs/786

## Purpose
`sources/test-tools/xfstests/tests/xfs/786` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair. Populate a XFS filesystem and fuzz every inobt key/pointer field. Use xfs_scrub to fix the corruption. The `_begin_fstest` declaration is `dangerous_fuzzers scrub fuzzers_online_repair`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/populate`, `./common/preamble`. Local helper surface: no local shell helpers beyond the main script body. Requirement and regression gates include `_require_scratch_xfs_fuzz_fields`. Important external or harness tools detected in the full source include none. Scenario variables and harness state referenced include none.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/786.out`; stable progress/output labels such as `echo "Format and populate"`, `echo "Fuzz inobt"`, `echo "Done fuzzing inobt"`; diagnostic detail appended to `$seqres.full`; hard failures through `_fail` assertions. The source has 34 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/786 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/787 -->
# sources/test-tools/xfstests/tests/xfs/787

## Purpose
`sources/test-tools/xfstests/tests/xfs/787` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair. Populate a XFS filesystem and fuzz every inobt key/pointer field. Try online repair and, if necessary, offline repair, to test the most likely usage pattern. The `_begin_fstest` declaration is `dangerous_fuzzers scrub repair fuzzers_bothrepair`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/populate`, `./common/preamble`. Local helper surface: no local shell helpers beyond the main script body. Requirement and regression gates include `_require_scratch_xfs_fuzz_fields`. Important external or harness tools detected in the full source include none. Scenario variables and harness state referenced include none.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/787.out`; stable progress/output labels such as `echo "Format and populate"`, `echo "Fuzz inobt"`, `echo "Done fuzzing inobt"`; diagnostic detail appended to `$seqres.full`; hard failures through `_fail` assertions. The source has 36 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/787 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/788 -->
# sources/test-tools/xfstests/tests/xfs/788

## Purpose
`sources/test-tools/xfstests/tests/xfs/788` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair. Populate a XFS filesystem and fuzz every inobt key/pointer field. Do not fix the filesystem, to test metadata verifiers. The `_begin_fstest` declaration is `dangerous_fuzzers fuzzers_norepair`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/populate`, `./common/preamble`. Local helper surface: no local shell helpers beyond the main script body. Requirement and regression gates include `_require_scratch_xfs_fuzz_fields`. Important external or harness tools detected in the full source include none. Scenario variables and harness state referenced include none.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/788.out`; stable progress/output labels such as `echo "Format and populate"`, `echo "Fuzz inobt"`, `echo "Done fuzzing inobt"`; diagnostic detail appended to `$seqres.full`; hard failures through `_fail` assertions. The source has 35 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/788 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/789 -->
# sources/test-tools/xfstests/tests/xfs/789

## Purpose
`sources/test-tools/xfstests/tests/xfs/789` is an XFS fstests shell case focused on realtime-device coverage, extent mapping and exchange. Simple tests of the old xfs swapext ioctl The `_begin_fstest` declaration is `auto quick swapext`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/preamble`. Local helper surface: `_cleanup`. Requirement and regression gates include `_require_xfs_io_command swapext`, `_require_test`. Important external or harness tools detected in the full source include `xfs_io`, `md5sum`. Scenario variables and harness state referenced include `TEST_DIR`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow uses `xfs_io` commands for writes, fallocate/punch, bmap inspection, scrub, repair, exchange, or media verification, uses checksum/stat comparisons as the content oracle. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; realtime-device paths depend on allocation unit and feature configuration, so tests skip or change behavior when geometry is unsuitable.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/789.out`; stable progress/output labels such as `echo swap`, `echo fail swap`; diagnostic detail appended to `$seqres.full`; feature-dependent skips through `_notrun`; content/stat comparisons with md5sum or diff. The source has 57 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/789 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/790 -->
# sources/test-tools/xfstests/tests/xfs/790

## Purpose
`sources/test-tools/xfstests/tests/xfs/790` is an XFS fstests shell case focused on extent mapping and exchange. Make sure an atomic exchangerange actually runs to completion even if we shut down the filesystem midway through. The `_begin_fstest` declaration is `auto quick fiexchange`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/inject`, `./common/preamble`, `./common/reflink`. Local helper surface: `_cleanup`, `filesnap`. Requirement and regression gates include `_require_xfs_io_command exchangerange`, `_require_test_program "punch-alternating"`, `_require_xfs_io_command startupdate`, `_require_xfs_io_error_injection "bmap_finish_one"`, `_require_test`. Important external or harness tools detected in the full source include `xfs_io`, `md5sum`, `punch-alternating`, `mount`. Scenario variables and harness state referenced include `TEST_DIR`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_io` commands for writes, fallocate/punch, bmap inspection, scrub, repair, exchange, or media verification, uses checksum/stat comparisons as the content oracle. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/790.out`; stable progress/output labels such as `echo "$1"`; diagnostic detail appended to `$seqres.full`; content/stat comparisons with md5sum or diff. The source has 60 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/790 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/791 -->
# sources/test-tools/xfstests/tests/xfs/791

## Purpose
`sources/test-tools/xfstests/tests/xfs/791` is an XFS fstests shell case focused on extent mapping and exchange. Test scatter-gather atomic file writes. We create a temporary file, write sparsely to it, then use XFS_EXCHANGE_RANGE_FILE1_WRITTEN flag to swap atomicallly only the ranges that we wrote. Inject an error so that we can test that log recovery finishes the swap. The `_begin_fstest` declaration is `auto quick fiexchange`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/inject`, `./common/preamble`. Local helper surface: `_cleanup`. Requirement and regression gates include `_require_xfs_io_command exchangerange`, `_require_xfs_scratch_atomicswap`, `_require_xfs_io_error_injection "bmap_finish_one"`, `_require_congruent_file_oplen $SCRATCH_MNT 65536`. Important external or harness tools detected in the full source include `xfs_io`, `mkfs.xfs`, `md5sum`, `mount`. Scenario variables and harness state referenced include `SCRATCH_MNT`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_io` commands for writes, fallocate/punch, bmap inspection, scrub, repair, exchange, or media verification, uses checksum/stat comparisons as the content oracle. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/791.out`; stable progress/output labels such as `echo swap | tee -a $seqres.full`; diagnostic detail appended to `$seqres.full`; content/stat comparisons with md5sum or diff. The source has 57 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/791 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/792 -->
# sources/test-tools/xfstests/tests/xfs/792

## Purpose
`sources/test-tools/xfstests/tests/xfs/792` is an XFS fstests shell case focused on extent mapping and exchange. Test scatter-gather atomic file commits. Use the startupdate command to create a temporary file, write sparsely to it, then commitupdate -h to perform the scattered update. Inject an error so that we can test that log recovery finishes the swap. The `_begin_fstest` declaration is `auto quick fiexchange`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/inject`, `./common/preamble`. Local helper surface: `_cleanup`. Requirement and regression gates include `_require_xfs_io_command exchangerange`, `_require_xfs_io_command startupdate '-e'`, `_require_xfs_scratch_atomicswap`, `_require_xfs_io_error_injection "bmap_finish_one"`, `_require_congruent_file_oplen $SCRATCH_MNT 65536`. Important external or harness tools detected in the full source include `xfs_io`, `mkfs.xfs`, `md5sum`, `mount`. Scenario variables and harness state referenced include `SCRATCH_MNT`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_io` commands for writes, fallocate/punch, bmap inspection, scrub, repair, exchange, or media verification, uses checksum/stat comparisons as the content oracle. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/792.out`; stable progress/output labels such as `echo commit | tee -a $seqres.full`; diagnostic detail appended to `$seqres.full`; content/stat comparisons with md5sum or diff. The source has 60 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/792 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/793 -->
# sources/test-tools/xfstests/tests/xfs/793

## Purpose
`sources/test-tools/xfstests/tests/xfs/793` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair, realtime-device coverage, stress concurrency. Race fsstress and realtime summary repair for a while to see if we crash or livelock. The `_begin_fstest` declaration is `online_repair fsstress_online_repair`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/inject`, `./common/preamble`, `./common/xfs`. Local helper surface: `_cleanup`. Requirement and regression gates include `_require_realtime`, `_require_scratch`, `_require_xfs_stress_online_repair`, `_require_xfs_has_feature "$SCRATCH_MNT" realtime`. Important external or harness tools detected in the full source include `mkfs.xfs`, `fsstress`, `mount`. Scenario variables and harness state referenced include `SCRATCH_MNT`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata, runs online scrub/repair or xfs_scrub in selected modes, starts fsstress or stress-scrub helpers to exercise concurrency. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version; stress timing is intentionally nondeterministic, so regressions may appear as hangs, livelocks, kernel warnings, or post-test fsck failures; realtime-device paths depend on allocation unit and feature configuration, so tests skip or change behavior when geometry is unsuitable.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/793.out`; stable progress/output labels such as `echo Silence is golden`; diagnostic detail appended to `$seqres.full`. The source has 46 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/793 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/794 -->
# sources/test-tools/xfstests/tests/xfs/794

## Purpose
`sources/test-tools/xfstests/tests/xfs/794` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair, attribute fork repair, stress concurrency. Race fsstress and extended attributes repair for a while to see if we crash or livelock. The `_begin_fstest` declaration is `online_repair fsstress_online_repair`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/attr`, `./common/filter`, `./common/fuzzy`, `./common/inject`, `./common/preamble`, `./common/xfs`. Local helper surface: `_cleanup`. Requirement and regression gates include `_require_attrs`, `_require_scratch`, `_require_xfs_stress_online_repair`. Important external or harness tools detected in the full source include `mkfs.xfs`, `fsstress`, `mount`. Scenario variables and harness state referenced include none.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata, runs online scrub/repair or xfs_scrub in selected modes, starts fsstress or stress-scrub helpers to exercise concurrency, sets extended attributes or validates attr-fork behavior. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version; stress timing is intentionally nondeterministic, so regressions may appear as hangs, livelocks, kernel warnings, or post-test fsck failures.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/794.out`; stable progress/output labels such as `echo Silence is golden`; diagnostic detail appended to `$seqres.full`. The source has 38 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/794 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/795 -->
# sources/test-tools/xfstests/tests/xfs/795

## Purpose
`sources/test-tools/xfstests/tests/xfs/795` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair, quota enforcement, extent mapping and exchange, stress concurrency. Ensure that the sysadmin won't hit EDQUOT while repairing file data contents even if the file's quota limits have been exceeded. This tests the quota reservation handling inside the exchangerange code used by repair. The `_begin_fstest` declaration is `online_repair`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/inject`, `./common/preamble`, `./common/quota`. Local helper surface: no local shell helpers beyond the main script body. Requirement and regression gates include `_require_quota`, `_require_user`, `_require_scratch`, `_require_xfs_stress_online_repair`. Important external or harness tools detected in the full source include `xfs_io`, `mkfs.xfs`, `xfs_quota`, `mount`. Scenario variables and harness state referenced include `SCRATCH_MNT`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, uses `xfs_io` commands for writes, fallocate/punch, bmap inspection, scrub, repair, exchange, or media verification, uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata, sets up quota state and validates accounting or enforcement. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version; quota tests depend on user/group setup, mount options, and stable quota-tools output.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/795.out`; stable progress/output labels such as `echo "set up quota" >> $seqres.full`, `echo "repairs" >> $seqres.full`, `echo "fail quota" >> $seqres.full`, `echo Silence is golden`; diagnostic detail appended to `$seqres.full`. The source has 75 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/795 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/796 -->
# sources/test-tools/xfstests/tests/xfs/796

## Purpose
`sources/test-tools/xfstests/tests/xfs/796` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair, stress concurrency. Race fsstress and directory repair for a while to see if we crash or livelock. The `_begin_fstest` declaration is `online_repair fsstress_online_repair`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/inject`, `./common/preamble`, `./common/xfs`. Local helper surface: `_cleanup`. Requirement and regression gates include `_require_scratch`, `_require_xfs_stress_online_repair`. Important external or harness tools detected in the full source include `mkfs.xfs`, `fsstress`, `mount`. Scenario variables and harness state referenced include none.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata, runs online scrub/repair or xfs_scrub in selected modes, starts fsstress or stress-scrub helpers to exercise concurrency. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version; stress timing is intentionally nondeterministic, so regressions may appear as hangs, livelocks, kernel warnings, or post-test fsck failures.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/796.out`; stable progress/output labels such as `echo Silence is golden`; diagnostic detail appended to `$seqres.full`. The source has 35 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/796 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/797 -->
# sources/test-tools/xfstests/tests/xfs/797

## Purpose
`sources/test-tools/xfstests/tests/xfs/797` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair, directory tree and parent-pointer repair, stress concurrency. Race fsstress and parent pointers repair for a while to see if we crash or livelock. The `_begin_fstest` declaration is `online_repair fsstress_online_repair`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/inject`, `./common/preamble`, `./common/xfs`. Local helper surface: `_cleanup`. Requirement and regression gates include `_require_scratch`, `_require_xfs_stress_online_repair`. Important external or harness tools detected in the full source include `mkfs.xfs`, `fsstress`, `mount`. Scenario variables and harness state referenced include none.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata, runs online scrub/repair or xfs_scrub in selected modes, starts fsstress or stress-scrub helpers to exercise concurrency. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version; stress timing is intentionally nondeterministic, so regressions may appear as hangs, livelocks, kernel warnings, or post-test fsck failures.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/797.out`; stable progress/output labels such as `echo Silence is golden`; diagnostic detail appended to `$seqres.full`. The source has 36 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/797 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/798 -->
# sources/test-tools/xfstests/tests/xfs/798

## Purpose
`sources/test-tools/xfstests/tests/xfs/798` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair. Make sure that xfs_scrub dry run, preen, and repair modes only modify the things that they're allowed to touch. The `_begin_fstest` declaration is `auto quick online_repair`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/preamble`. Local helper surface: `test_scrub`. Requirement and regression gates include `_require_scratch_nocheck`, `_require_scrub`, `_require_xfs_db_command "fuzz"`, `_require_xfs_io_command "repair"`. Important external or harness tools detected in the full source include `xfs_io`, `xfs_db`, `mkfs.xfs`, `xfs_scrub`, `mount`. Scenario variables and harness state referenced include `SCRATCH_MNT`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_io` commands for writes, fallocate/punch, bmap inspection, scrub, repair, exchange, or media verification, uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata, runs online scrub/repair or xfs_scrub in selected modes. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/798.out`; stable progress/output labels such as `echo "testing mode? $mode scrub_arg $scrub_arg"`, `echo "db_args:${db_args[@]}:scrub_arg:$scrub_arg:$mode:" >> $seqres.full`, `echo "----------------" >> $seqres.full`; diagnostic detail appended to `$seqres.full`; feature-dependent skips through `_notrun`. The source has 103 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/798 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/799 -->
# sources/test-tools/xfstests/tests/xfs/799

## Purpose
`sources/test-tools/xfstests/tests/xfs/799` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair, directory tree and parent-pointer repair, stress concurrency. Race fsstress doing mostly renames and xfs_scrub in force-repair mode for a while to see if we crash or livelock. The `_begin_fstest` declaration is `online_repair fsstress_online_repair`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/inject`, `./common/preamble`, `./common/xfs`. Local helper surface: `_cleanup`. Requirement and regression gates include `_require_scratch`, `_require_xfs_stress_online_repair`. Important external or harness tools detected in the full source include `mkfs.xfs`, `fsstress`, `mount`. Scenario variables and harness state referenced include none.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata, runs online scrub/repair or xfs_scrub in selected modes, starts fsstress or stress-scrub helpers to exercise concurrency. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version; stress timing is intentionally nondeterministic, so regressions may appear as hangs, livelocks, kernel warnings, or post-test fsck failures.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/799.out`; stable progress/output labels such as `echo Silence is golden`; diagnostic detail appended to `$seqres.full`. The source has 36 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/799 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/800 -->
# sources/test-tools/xfstests/tests/xfs/800

## Purpose
`sources/test-tools/xfstests/tests/xfs/800` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair, directory tree and parent-pointer repair, stress concurrency. Race fsstress doing mostly renames and xfs_scrub in read-only mode for a while to see if we crash or livelock. The `_begin_fstest` declaration is `scrub fsstress_scrub`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/inject`, `./common/preamble`, `./common/xfs`. Local helper surface: `_cleanup`. Requirement and regression gates include `_require_scratch`, `_require_xfs_stress_scrub`. Important external or harness tools detected in the full source include `mkfs.xfs`, `fsstress`, `mount`. Scenario variables and harness state referenced include none.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata, runs online scrub/repair or xfs_scrub in selected modes, starts fsstress or stress-scrub helpers to exercise concurrency. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version; stress timing is intentionally nondeterministic, so regressions may appear as hangs, livelocks, kernel warnings, or post-test fsck failures.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/800.out`; stable progress/output labels such as `echo Silence is golden`; diagnostic detail appended to `$seqres.full`. The source has 36 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/800 -->
