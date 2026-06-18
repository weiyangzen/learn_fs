# subset-b-009553 research

This grouped report covers the XFS fstests files assigned to `subset-b-009553`. Each section preserves the source path in its title and is wrapped with `BEGIN_FILE_RESEARCH` / `END_FILE_RESEARCH` markers for deterministic reconciliation into source-tree-aligned per-file documents.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/158 -->
# sources/test-tools/xfstests/tests/xfs/158

## Purpose
`sources/test-tools/xfstests/tests/xfs/158` is a XFS feature-upgrade regression. Check that we can upgrade a filesystem to support inobtcount and that everything works properly after the upgrade. Make sure we can't format a filesystem with inobtcount and not finobt. Make sure we can't upgrade a filesystem to inobtcount without finobt. Format V5 filesystem without inode btree counter support and populate it. Upgrade filesystem to have the counters and inject failure into repair and make sure that the only path forward is to re-run repair on the filesystem. The `_begin_fstest` declaration is `auto quick inobtcount`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`. Local helper surface: no local helpers beyond the main shell flow. Requirement gates: `_require_scratch_xfs_inobtcount`, `_require_command "$XFS_ADMIN_PROG" "xfs_admin"`, `_require_xfs_repair_upgrade inobtcount`. Important external or harness commands observed in the full source include `mount`, `xfs_admin`. Notable scenario variables include `XFS_REPAIR_FAIL_AFTER_PHASE=2 _scratch_xfs_repair -c inobtcount=1 2>> $seqres.full`.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; uses xfs_admin to toggle or validate filesystem feature flags; runs xfs_repair in checking or fixing mode and treats repair output as part of the oracle; uses xfs_db to inspect or perturb low-level metadata; adds fsstress background load to expose races and ENOSPC boundaries. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, temporary `$tmp.*` files, diagnostic `$seqres.full` logs, on-disk metadata fields modified for corruption testing. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
intentional metadata corruption can leave the scratch device unmountable until repair or cleanup completes; stress subtests can expose timing-sensitive failures and require enough scratch space; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/158.out`; stable progress labels including `echo "Should not be able to format with inobtcount but not finobt."`, `echo moo > $SCRATCH_MNT/urk`, `echo "Fail partway through upgrading"`, `echo "needsrepair should have prevented mount"`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 76 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/158 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/159 -->
# sources/test-tools/xfstests/tests/xfs/159

## Purpose
`sources/test-tools/xfstests/tests/xfs/159` is a XFS feature-upgrade regression. Check that the xfs_db timelimit command prints the ranges that we expect. This in combination with an xfs_ondisk.h build time check in the kernel ensures that the kernel agrees with userspace. Override the default cleanup function. Format filesystem without bigtime support and populate it. The `_begin_fstest` declaration is `auto quick bigtime`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`. Local helper surface: `_cleanup`. Requirement gates: `_require_scratch`, `_require_xfs_db_command timelimit`. Important external or harness commands observed in the full source include `xfs_db`, `xfs_ondisk`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; uses xfs_db to inspect or perturb low-level metadata. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, diagnostic `$seqres.full` logs, on-disk metadata fields modified for corruption testing. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
intentional metadata corruption can leave the scratch device unmountable until repair or cleanup completes; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/159.out`; stable progress labels including `echo classic xfs timelimits`, `echo bigtime xfs timelimits`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 34 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/159 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/160 -->
# sources/test-tools/xfstests/tests/xfs/160

## Purpose
`sources/test-tools/xfstests/tests/xfs/160` is a XFS feature-upgrade regression. Check that we can upgrade a filesystem to support bigtime and that inode timestamps work properly after the upgrade. Make sure we're required to specify a feature status Can we add bigtime and inobtcount at the same time? Format V5 filesystem without bigtime support and populate it Now upgrade to bigtime support Mount again, look at our files Bump one of the timestamps but stay under 2038. The `_begin_fstest` declaration is `auto quick bigtime`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`. Local helper surface: no local helpers beyond the main shell flow. Requirement gates: `_require_command "$XFS_ADMIN_PROG" "xfs_admin"`, `_require_scratch_xfs_bigtime`, `_require_xfs_repair_upgrade bigtime`. Important external or harness commands observed in the full source include `xfs_admin`. Notable scenario variables include `TZ=UTC stat -c '%Y' $SCRATCH_MNT/a`, `TZ=UTC stat -c '%Y' $SCRATCH_MNT/b`, `TZ=UTC stat -c '%Y' $SCRATCH_MNT/a`, `TZ=UTC stat -c '%Y' $SCRATCH_MNT/b`, `TZ=UTC stat -c '%Y' $SCRATCH_MNT/a`.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; uses xfs_admin to toggle or validate filesystem feature flags; runs xfs_repair in checking or fixing mode and treats repair output as part of the oracle; uses xfs_db to inspect or perturb low-level metadata. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, diagnostic `$seqres.full` logs, on-disk metadata fields modified for corruption testing. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
intentional metadata corruption can leave the scratch device unmountable until repair or cleanup completes; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/160.out`; stable progress labels including `echo before upgrade:`, `echo after upgrade:`, `echo after upgrade and bump:`, `echo after upgrade, bump, and remount:`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 95 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/160 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/161 -->
# sources/test-tools/xfstests/tests/xfs/161

## Purpose
`sources/test-tools/xfstests/tests/xfs/161` is a quota behavior regression. Check that we can upgrade a filesystem to support bigtime and that quota timers work properly after the upgrade.  You need a quota-tools containing commit 16b60cb9e315ed for this test to run properly; v4.06 should do. The word 'projectname' was added to quota(8)'s synopsis shortly after y2038+ support was added for XFS, so we use that to decide if we're going to run this test at all. Format V5 filesystem without bigtime support and populate it Write more than one block to exceed the soft block quota limit via. The `_begin_fstest` declaration is `auto quick bigtime quota`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`, `./common/quota`. Local helper surface: no local helpers beyond the main shell flow. Requirement gates: `_require_command "$XFS_ADMIN_PROG" "xfs_admin"`, `_require_command "$QUOTA_PROG" "quota"`, `_require_quota`, `_require_scratch_xfs_bigtime`, `_require_xfs_repair_upgrade bigtime`. Important external or harness commands observed in the full source include `quota`, `xfs_admin`, `xfs_quota`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; uses xfs_admin to toggle or validate filesystem feature flags; runs xfs_repair in checking or fixing mode and treats repair output as part of the oracle; uses xfs_db to inspect or perturb low-level metadata; configures or queries user/group/project quota state. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, temporary `$tmp.*` files, diagnostic `$seqres.full` logs, quota accounting and grace-period metadata, on-disk metadata fields modified for corruption testing. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
intentional metadata corruption can leave the scratch device unmountable until repair or cleanup completes; quota output and timer calculations are sensitive to quota-tools versions, current time, and 32-bit time support; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/161.out`; stable progress labels including `echo "Now is after February 2222?  Expect problems."`, `echo "setting expiration to $new_expiry - $now = $expiry_delta" >> $seqres.full`, `echo "grace2 is $grace2" >> $seqres.full`, `echo "grace2 is $grace2" >> $seqres.full`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 153 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/161 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/162 -->
# sources/test-tools/xfstests/tests/xfs/162

## Purpose
`sources/test-tools/xfstests/tests/xfs/162` is a metadata repair/corruption regression. Make sure that attrs are handled properly when repair has to reset the root directory. The `_begin_fstest` declaration is `auto quick attr repair`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`, `./common/populate`, `./common/fuzzy`. Local helper surface: no local helpers beyond the main shell flow. Requirement gates: `_require_scratch_nocheck`, `_require_populate_commands`, `_require_xfs_db_command "fuzz"`. Important external or harness commands observed in the full source include primarily fstests shell helpers. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; runs xfs_repair in checking or fixing mode and treats repair output as part of the oracle; uses xfs_db to inspect or perturb low-level metadata. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, diagnostic `$seqres.full` logs, on-disk metadata fields modified for corruption testing. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
intentional metadata corruption can leave the scratch device unmountable until repair or cleanup completes; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/162.out`; stable progress labels including `echo "Format and populate btree attr root dir"`, `echo "Break the root directory"`, `echo "Detect bad root directory"`, `echo "Should have detected bad root dir"`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 50 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/162 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/163 -->
# sources/test-tools/xfstests/tests/xfs/163

## Purpose
`sources/test-tools/xfstests/tests/xfs/163` is a online grow/shrink regression. XFS shrinkfs basic functionality test This test attempts to shrink with a small size (512K), half AG size and an out-of-bound size (agsize + 1) to observe if it works as expected. If we couldn't shrink the filesystem due to lack of space, we're done with this test. agcount = 1 is forbidden on purpose, and need to ensure shrinking to 2 AGs isn't feasible yet. So agcount = 3 is the minimum number now. The `_begin_fstest` declaration is `auto quick growfs shrinkfs`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`. Local helper surface: `test_shrink`. Requirement gates: `_require_scratch_xfs_shrink`. Important external or harness commands observed in the full source include `mkfs`, `mount`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, temporary `$tmp.*` files, diagnostic `$seqres.full` logs. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
online grow/shrink cases depend on free-space geometry and can skip or fail if ENOSPC behavior changes; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/163.out`; stable progress labels including `echo "Format and mount"`, `echo "Shrink fs (small size)"`, `echo "Shrink fs (small size) failure"`, `echo "Shrink fs (half AG)"`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 70 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/163 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/164 -->
# sources/test-tools/xfstests/tests/xfs/164

## Purpose
`sources/test-tools/xfstests/tests/xfs/164` is a preallocation/unwritten extent regression. To test for short dio reads on IRIX and Linux - pv#962005/962547 http://bugworks.engr.sgi.com/query.cgi/962005 In particular we are interested in dio_reads for the cases of: * eof on a hole * eof on an unwritten extent * eof on a sector boundary and not on a sector boundary on a BB boundary on an odd byte boundary => 1 short of boundary. The `_begin_fstest` declaration is `rw pattern auto prealloc quick`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`. Local helper surface: `_filter_io`, `_filter_bmap`, `_test_eof_hole`, `_test_eof_unwritten_extent`. Requirement gates: `_require_test`, `_require_xfs_io_command "falloc"`. Important external or harness commands observed in the full source include primarily fstests shell helpers. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow drives file layout with xfs_io operations such as fallocate, punch, zero, bmap, fiemap, fsync, direct I/O, or mmap. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, diagnostic `$seqres.full` logs. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
golden output can drift when xfsprogs diagnostics, filters, or common fstests helpers change; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/164.out`; stable progress labels including `echo ""`, `echo "boundary_minus1 = $boundary_minus1"`, `echo ""`, `echo "boundary_plus1 = $boundary_plus1"`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 125 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/164 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/165 -->
# sources/test-tools/xfstests/tests/xfs/165

## Purpose
`sources/test-tools/xfstests/tests/xfs/165` is a preallocation/unwritten extent regression. Test out prealloc, direct writes and buffered read Some experimentation when looking at pv#962014 - DMF 3.7 reading incorrect data Doesn't actually reproduce the problem but it tried to :-) io tests Other test... $XFS_IO_PROG -f -c "resvsp ${off}k ${end}k" $testfile write the initial file. The `_begin_fstest` declaration is `rw pattern auto prealloc quick`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`. Local helper surface: `_filter_io`, `_filter_bmap`. Requirement gates: `_require_test`, `_require_xfs_io_command "falloc"`. Important external or harness commands observed in the full source include `xfs_bmap`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow drives file layout with xfs_io operations such as fallocate, punch, zero, bmap, fiemap, fsync, direct I/O, or mmap. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, temporary `$tmp.*` files, diagnostic `$seqres.full` logs. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
golden output can drift when xfsprogs diagnostics, filters, or common fstests helpers change; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/165.out`; stable progress labels including `echo ""`, `echo "*** offset = $offset ***"`, `echo ""`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 96 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/165 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/166 -->
# sources/test-tools/xfstests/tests/xfs/166

## Purpose
`sources/test-tools/xfstests/tests/xfs/166` is a preallocation/unwritten extent regression. FSQA Test No. 166 ->page-mkwrite test - unwritten extents and mmap assumes 1st, 3rd and 5th blocks are single written blocks, the others are unwritten. is the extent unwritten? Beginning with 5.18, some filesystems support creating large folios for the page cache.  A system with 64k pages can create 256k folios, which means that with the old file size of 1M, the last half of the file is completely. The `_begin_fstest` declaration is `rw metadata auto quick prealloc mmap`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`. Local helper surface: `_filter_blocks`. Requirement gates: `_require_scratch`, `_require_xfs_io_command "falloc"`, `_require_congruent_file_oplen $SCRATCH_MNT $FILE_SIZE`. Important external or harness commands observed in the full source include `xfs_bmap`. Notable scenario variables include `TEST_FILE=$SCRATCH_MNT/test_file`, `TEST_PROG=$here/src/unwritten_mmap`, `FILE_SIZE=$((12 * 1048576))`.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; drives file layout with xfs_io operations such as fallocate, punch, zero, bmap, fiemap, fsync, direct I/O, or mmap. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, diagnostic `$seqres.full` logs. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
golden output can drift when xfsprogs diagnostics, filters, or common fstests helpers change; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/166.out`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 83 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/166 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/167 -->
# sources/test-tools/xfstests/tests/xfs/167

## Purpose
`sources/test-tools/xfstests/tests/xfs/167` is a preallocation/unwritten extent regression. FSQA Test No. 167 unwritten extent conversion test fast devices can consume disk space at a rate of 1GB every 5s via the background workload. With 50 test loops, at 1 second per loop, that means we need at least 10GB of disk space to ensure this test will not fail with ENOSPC errors. The `_begin_fstest` declaration is `rw metadata auto stress prealloc`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`. Local helper surface: `workout`. Requirement gates: `_require_xfs_io_command "falloc"`, `_require_scratch`, `_require_fs_space $SCRATCH_MNT 10485760`. Important external or harness commands observed in the full source include primarily fstests shell helpers. Notable scenario variables include `FSSTRESS_ARGS=`_scale_fsstress_args -d $SCRATCH_MNT -p $procs -n $nops``, `TEST_FILE=$SCRATCH_MNT/test_file`, `TEST_PROG=$here/src/unwritten_sync`, `LOOPS=$((5 * $TIME_FACTOR))`.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; drives file layout with xfs_io operations such as fallocate, punch, zero, bmap, fiemap, fsync, direct I/O, or mmap; adds fsstress background load to expose races and ENOSPC boundaries. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, loop devices and loop-mounted images. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
loop-device setup and teardown must be exact to avoid leaked mounts or stale devices; stress subtests can expose timing-sensitive failures and require enough scratch space; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/167.out`; stable progress labels including `echo "*** test unwritten extent conversion under heavy I/O"`, `echo "     *** test done"`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 49 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/167 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/168 -->
# sources/test-tools/xfstests/tests/xfs/168

## Purpose
`sources/test-tools/xfstests/tests/xfs/168` is a online grow/shrink regression. XFS online shrinkfs stress test This test attempts to shrink unused space as much as possible with background fsstress workload. It will decrease the shrink size if larger size fails. And totally repeat 2 * TIME_FACTOR times. fix the reserve block pool to a known size so that the enospc calculations work out correctly. -w ensures that the only ops are ones which cause write I/O shrink in chunks of this size at most. The `_begin_fstest` declaration is `auto growfs shrinkfs ioctl prealloc stress`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`. Local helper surface: `create_scratch`, `fill_scratch`, `stress_scratch`. Requirement gates: `_require_scratch_xfs_shrink`, `_require_xfs_io_command "falloc"`. Important external or harness commands observed in the full source include `fsstress`, `mkfs`, `xfs_repair`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; runs xfs_repair in checking or fixing mode and treats repair output as part of the oracle; drives file layout with xfs_io operations such as fallocate, punch, zero, bmap, fiemap, fsync, direct I/O, or mmap; adds fsstress background load to expose races and ENOSPC boundaries. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, temporary `$tmp.*` files, diagnostic `$seqres.full` logs. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
intentional metadata corruption can leave the scratch device unmountable until repair or cleanup completes; online grow/shrink cases depend on free-space geometry and can skip or fail if ENOSPC behavior changes; stress subtests can expose timing-sensitive failures and require enough scratch space; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/168.out`; stable progress labels including `echo "$out" | grep -q 'No space left on device' && continue`, `echo "Silence is golden"`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 112 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/168 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/169 -->
# sources/test-tools/xfstests/tests/xfs/169

## Purpose
`sources/test-tools/xfstests/tests/xfs/169` is a reflink and copy-on-write regression. Ensure that we can create enough distinct reflink entries to force creation of a multi-level refcount btree.  Delete and recreate a few times to exercise the refcount btree grow/shrink functions. Override the default cleanup function. The `_begin_fstest` declaration is `auto clone`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`, `./common/reflink`. Local helper surface: `_cleanup`. Requirement gates: `_require_scratch_reflink`. Important external or harness commands observed in the full source include `umount`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; creates shared extents and forces copy-on-write conversions. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, temporary `$tmp.*` files, diagnostic `$seqres.full` logs, shared extent/refcount and CoW fork metadata. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
intentional metadata corruption can leave the scratch device unmountable until repair or cleanup completes; extent-count and bmap/fiemap assertions can change with allocator behavior while data correctness remains stable; online grow/shrink cases depend on free-space geometry and can skip or fail if ENOSPC behavior changes; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/169.out`; stable progress labels including `echo "Create the original file blocks"`, `echo "$i: Reflink every other block"`, `echo "$i: Delete both files"`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 61 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/169 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/170 -->
# sources/test-tools/xfstests/tests/xfs/170

## Purpose
`sources/test-tools/xfstests/tests/xfs/170` is a reflink and copy-on-write regression. FSQA Test No. 170 Check the filestreams allocator is doing its job. Multi-file data streams should always write into seperate AGs. test small stream, multiple I/O per file, 30s timeout This test checks that the filestreams allocator never allocates space in any given AG into more than one stream when there's plenty of space on the filesystem.  Newer feature sets (e.g. reflink) have increased the size of the log for small filesystems, so we make sure there's one more AG than. The `_begin_fstest` declaration is `rw filestreams auto quick`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`, `./common/filestreams`. Local helper surface: no local helpers beyond the main shell flow. Requirement gates: `_require_scratch`. Important external or harness commands observed in the full source include primarily fstests shell helpers. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow creates shared extents and forces copy-on-write conversions. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, shared extent/refcount and CoW fork metadata. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
extent-count and bmap/fiemap assertions can change with allocator behavior while data correctness remains stable; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/170.out`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 39 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/170 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/171 -->
# sources/test-tools/xfstests/tests/xfs/171

## Purpose
`sources/test-tools/xfstests/tests/xfs/171` is a reflink and copy-on-write regression. FSQA Test No. 171 Check the filestreams allocator is doing its job. Multi-file data streams should always write into seperate AGs. test large numbers of files, single I/O per file, 120s timeout Get close to filesystem full. 128 = ENOSPC 120 = 93.75% full, gets repeatable failures 112 = 87.5% full, should reliably succeed but doesn't *FIXME*. The `_begin_fstest` declaration is `rw filestreams`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`, `./common/filestreams`. Local helper surface: no local helpers beyond the main shell flow. Requirement gates: `_require_scratch`. Important external or harness commands observed in the full source include primarily fstests shell helpers. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow creates shared extents and forces copy-on-write conversions. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, shared extent/refcount and CoW fork metadata. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
extent-count and bmap/fiemap assertions can change with allocator behavior while data correctness remains stable; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/171.out`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 45 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/171 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/172 -->
# sources/test-tools/xfstests/tests/xfs/172

## Purpose
`sources/test-tools/xfstests/tests/xfs/172` is a filestream allocator regression. FSQA Test No. 172 Check the filestreams allocator is doing its job. Multi-file data streams should always write into seperate AGs. The first _test_streams call sets up the filestreams allocator to fail and then checks that it actually failed.  It does this by creating a very small filesystem, writing a lot of data in parallel to separate streams, and then flushes the dirty data, also in parallel.  To trip the allocator, the test relies on writeback combining adjacent dirty ranges into large allocation. The `_begin_fstest` declaration is `rw filestreams`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`, `./common/filestreams`. Local helper surface: no local helpers beyond the main shell flow. Requirement gates: `_require_scratch`, `_require_scratch_delalloc`. Important external or harness commands observed in the full source include primarily fstests shell helpers. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow mounts, remounts, or deliberately rejects mounts through fstests helpers. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
golden output can drift when xfsprogs diagnostics, filters, or common fstests helpers change; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/172.out`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 49 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/172 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/173 -->
# sources/test-tools/xfstests/tests/xfs/173

## Purpose
`sources/test-tools/xfstests/tests/xfs/173` is a reflink and copy-on-write regression. FSQA Test No. 173 Check the filestreams allocator is doing its job. Multi-file data streams should always write into seperate AGs. test large number of streams, multiple I/O per file, 120s timeout Because each stream spills over an AG, the stream count needs to be less than or equal to half the AG count so we don't run out of AGs. This test checks the exact point at which the filestreams allocator will start to allocate space from some AG into more than one stream.  Newer. The `_begin_fstest` declaration is `rw filestreams`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`, `./common/filestreams`. Local helper surface: no local helpers beyond the main shell flow. Requirement gates: `_require_scratch`. Important external or harness commands observed in the full source include primarily fstests shell helpers. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow creates shared extents and forces copy-on-write conversions. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, shared extent/refcount and CoW fork metadata. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
extent-count and bmap/fiemap assertions can change with allocator behavior while data correctness remains stable; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/173.out`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 42 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/173 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/174 -->
# sources/test-tools/xfstests/tests/xfs/174

## Purpose
`sources/test-tools/xfstests/tests/xfs/174` is a filestream allocator regression. FSQA Test No. 174 Check the filestreams allocator is doing its job. Multi-file data streams should always write into seperate AGs. test number of streams greater than AGs. Expected to fail. The `_begin_fstest` declaration is `rw filestreams auto`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`, `./common/filestreams`. Local helper surface: no local helpers beyond the main shell flow. Requirement gates: `_require_scratch`. Important external or harness commands observed in the full source include primarily fstests shell helpers. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow runs a linear fstests shell scenario after requirement gating. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
golden output can drift when xfsprogs diagnostics, filters, or common fstests helpers change; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/174.out`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 30 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/174 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/175 -->
# sources/test-tools/xfstests/tests/xfs/175

## Purpose
`sources/test-tools/xfstests/tests/xfs/175` is a quota behavior regression. Regression test for xfsprogs commit d8a94546 ("xfs_quota: state command should report ugp grace times"). When give "-ugp" or "-a" options to xfs_quota state command, it should report grace times for all three types separately. Import common functions Format filesystem and set up quota limits xfs_quota state -ugp or -a should report times for all three types separately. The `_begin_fstest` declaration is `auto quick quota`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/quota`. Local helper surface: no local helpers beyond the main shell flow. Requirement gates: `_require_scratch`, `_require_quota`. Important external or harness commands observed in the full source include `quota`, `xfs_quota`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; configures or queries user/group/project quota state. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, diagnostic `$seqres.full` logs, quota accounting and grace-period metadata. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
quota output and timer calculations are sensitive to quota-tools versions, current time, and 32-bit time support; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/175.out`; stable progress labels including `echo "* state -ugp:"`, `echo "* state -a:"`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 35 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/175 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/176 -->
# sources/test-tools/xfstests/tests/xfs/176

## Purpose
`sources/test-tools/xfstests/tests/xfs/176` is a online grow/shrink regression. Ensure that online shrink does not let us shrink the fs such that the end of the filesystem is now in the middle of a sparse inode cluster. Figure out the next possible inode number after the log, since we can't shrink or relocate the log consume nearly all available space (leave ~1MB) Allocate inodes in a directory until failure. Find a sparse inode cluster after logend_agno/logend_agino. Calculate the fs inode chunk size based on the inode size and fixed 64-inode. The `_begin_fstest` declaration is `auto quick shrinkfs prealloc punch`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`. Local helper surface: `convert_units`, `_consume_freesp`, `_alloc_inodes`, `find_sparse_clusters`. Requirement gates: `_require_scratch`, `_require_xfs_sparse_inodes`, `_require_scratch_xfs_shrink`, `_require_xfs_io_command "falloc"`, `_require_xfs_io_command "fpunch"`. Important external or harness commands observed in the full source include `mkfs`. Notable scenario variables include `XFS_INODES_PER_CHUNK=64`, `CHUNK_SIZE=$((isize * XFS_INODES_PER_CHUNK))`.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; uses xfs_db to inspect or perturb low-level metadata; drives file layout with xfs_io operations such as fallocate, punch, zero, bmap, fiemap, fsync, direct I/O, or mmap. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, temporary `$tmp.*` files, diagnostic `$seqres.full` logs, loop devices and loop-mounted images, on-disk metadata fields modified for corruption testing. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
intentional metadata corruption can leave the scratch device unmountable until repair or cleanup completes; loop-device setup and teardown must be exact to avoid leaked mounts or stale devices; online grow/shrink cases depend on free-space geometry and can skip or fail if ENOSPC behavior changes; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/176.out`; stable progress labels including `echo -n > $dir/$i || break`, `echo clusters >> $seqres.full`, `echo "/save inode comes after target cluster, test may fail"`, `echo "Hope to fail at shrinking to $new_size" >> $seqres.full`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 188 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/176 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/177 -->
# sources/test-tools/xfstests/tests/xfs/177

## Purpose
`sources/test-tools/xfstests/tests/xfs/177` is a XFS fstests regression. Functional test for commit: f38a032b165d ("xfs: fix I_DONTCACHE") Functional testing for the I_DONTCACHE inode flag, as set by the BULKSTAT ioctl.  This flag neuters the inode cache's tendency to try to hang on to incore inodes for a while after the last program closes the file, which is helpful for filesystem scanners to avoid trashing the inode cache. However, the inode cache doesn't always honor the DONTCACHE behavior -- the only time it really applies is to cache misses from a bulkstat scan.  If. The `_begin_fstest` declaration is `auto ioctl unreliable_in_parallel`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`. Local helper surface: `_cleanup`, `count_xfs_inode_objs`, `dump_debug_info`. Requirement gates: `_require_xfs_io_command "bulkstat"`, `_require_scratch`, `_require_fs_sysfs stats/stats`. Important external or harness commands observed in the full source include `mount`, `xfs_centisecs_file`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; drives file layout with xfs_io operations such as fallocate, punch, zero, bmap, fiemap, fsync, direct I/O, or mmap. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, temporary `$tmp.*` files, diagnostic `$seqres.full` logs. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
golden output can drift when xfsprogs diagnostics, filters, or common fstests helpers change; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/177.out`; stable progress labels including `echo "round $1 baseline: $baseline_count high: $high_count fresh: $fresh_count post: $post_count end: $end_count" >> $seqres.full`, `echo 100 > "$xfs_centisecs_file" || _notrun "Cannot adjust xfssyncd_centisecs?"`, `echo "Will sleep $sleep_seconds seconds to expire inodes" >> $seqres.full`, `echo "created $new_files files" >> $seqres.full`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 206 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/177 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/178 -->
# sources/test-tools/xfstests/tests/xfs/178

## Purpose
`sources/test-tools/xfstests/tests/xfs/178` is a metadata repair/corruption regression. Reproduce PV#:967665 Test if mkfs.xfs wipes old AG headers when using -f option dd the 1st sector then repair dd first sector xfs_repair check repair From the PV o Summary of testing:. The `_begin_fstest` declaration is `mkfs other auto`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`, `./common/repair`. Local helper surface: `filter_repair`, `_dd_repair_check`. Requirement gates: `_require_scratch`. Important external or harness commands observed in the full source include `mkfs`, `xfs_repair`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; runs xfs_repair in checking or fixing mode and treats repair output as part of the oracle. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, temporary `$tmp.*` files. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
golden output can drift when xfsprogs diagnostics, filters, or common fstests helpers change; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/178.out`; stable progress labels including `echo "repair passed"`, `echo "repair failed!"`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 77 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/178 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/179 -->
# sources/test-tools/xfstests/tests/xfs/179

## Purpose
`sources/test-tools/xfstests/tests/xfs/179` is a reflink and copy-on-write regression. See how well reflink handles overflowing reflink counts. This test modifies the refcount btree on the data device, so we must force rtinherit off so that the test files are created there. Set the file size to 10x the block size to guarantee that the COW writes will touch multiple blocks and exercise the refcount extent merging code.  This is necessary to catch a bug in the refcount extent merging code that handles MAXREFCOUNT edge cases. For the last COW test, write single blocks at the start, middle, and end of. The `_begin_fstest` declaration is `auto quick clone`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`, `./common/attr`, `./common/reflink`. Local helper surface: no local helpers beyond the main shell flow. Requirement gates: `_require_scratch_reflink`, `_require_scratch_nocheck`, `_require_cp_reflink`, `_require_test_program "punch-alternating"`. Important external or harness commands observed in the full source include `mount`, `punch-alternating`, `xfs_repair`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; runs xfs_repair in checking or fixing mode and treats repair output as part of the oracle; uses xfs_db to inspect or perturb low-level metadata; creates shared extents and forces copy-on-write conversions. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, diagnostic `$seqres.full` logs, shared extent/refcount and CoW fork metadata, on-disk metadata fields modified for corruption testing. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
intentional metadata corruption can leave the scratch device unmountable until repair or cleanup completes; extent-count and bmap/fiemap assertions can change with allocator behavior while data correctness remains stable; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/179.out`; stable progress labels including `echo "Format and mount"`, `echo "Create original files"`, `echo "Change reference count"`, `echo "set refcount to -4" >> $seqres.full`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 112 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/179 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/180 -->
# sources/test-tools/xfstests/tests/xfs/180

## Purpose
`sources/test-tools/xfstests/tests/xfs/180` is a reflink and copy-on-write regression. Test fragmentation after a lot of random CoW: - Create two reflinked files.  Set extsz hint on second file. - Buffered write to random offsets to scatter CoW reservations. - Rewrite the whole file to use up reservations. - Check the number of extents. The `_begin_fstest` declaration is `auto quick clone fiemap`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`, `./common/reflink`. Local helper surface: no local helpers beyond the main shell flow. Requirement gates: `_require_scratch_reflink`, `_require_cp_reflink`, `_require_xfs_io_command "fiemap"`, `_require_xfs_io_command "cowextsize"`, `_require_no_xfs_always_cow`, `_require_congruent_file_oplen $SCRATCH_MNT $blksz`, `_require_fs_space $SCRATCH_MNT $((filesize / 1024 * 3 * 5 / 4))`. Important external or harness commands observed in the full source include `mount`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; drives file layout with xfs_io operations such as fallocate, punch, zero, bmap, fiemap, fsync, direct I/O, or mmap; creates shared extents and forces copy-on-write conversions. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, diagnostic `$seqres.full` logs, shared extent/refcount and CoW fork metadata. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
extent-count and bmap/fiemap assertions can change with allocator behavior while data correctness remains stable; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/180.out`; stable progress labels including `echo "Format and mount"`, `echo "Create the original files"`, `echo "Compare files"`, `echo "CoW and unmount"`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 76 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/180 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/181 -->
# sources/test-tools/xfstests/tests/xfs/181

## Purpose
`sources/test-tools/xfstests/tests/xfs/181` is a log recovery or log-geometry regression. Like 121 only creating large EAs As part of the iunlink processing in recovery it will call VN_RELE which will inactivate the inodes and if they have EAs (which they will here) also call xfs_inactive_attrs. We want to test out this xfs_inactive_attrs code being called in recovery. Override the default cleanup function. num_files must be greater than 64 (XFS_AGI_UNLINKED_BUCKETS) so that there will be at least one linked list from one of. The `_begin_fstest` declaration is `shutdown log auto quick`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`, `./common/log`. Local helper surface: `_cleanup`. Requirement gates: `_require_scratch`. Important external or harness commands observed in the full source include `mkfs`, `mount`, `xfs_inactive_attrs`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, temporary `$tmp.*` files, diagnostic `$seqres.full` logs. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
golden output can drift when xfsprogs diagnostics, filters, or common fstests helpers change; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/181.out`; stable progress labels including `echo "mkfs"`, `echo "mount"`, `echo "open and unlink $num_files files with EAs"`, `echo "godown"`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 98 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/181 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/182 -->
# sources/test-tools/xfstests/tests/xfs/182

## Purpose
`sources/test-tools/xfstests/tests/xfs/182` is a reflink and copy-on-write regression. Test fragmentation after a lot of random CoW: - Create two reflinked files.  Set extsz hint on second file. - Directio write to random offsets to scatter CoW reservations. - Rewrite the whole file to use up reservations. - Check the number of extents. The `_begin_fstest` declaration is `auto quick clone fiemap`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`, `./common/reflink`. Local helper surface: no local helpers beyond the main shell flow. Requirement gates: `_require_scratch_reflink`, `_require_cp_reflink`, `_require_xfs_io_command "fiemap"`, `_require_xfs_io_command "cowextsize"`, `_require_odirect`, `_require_no_xfs_always_cow	# writes have to converge to overwrites`, `_require_congruent_file_oplen $SCRATCH_MNT $blksz`, `_require_fs_space $SCRATCH_MNT $((filesize / 1024 * 3 * 5 / 4))`. Important external or harness commands observed in the full source include `mount`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; drives file layout with xfs_io operations such as fallocate, punch, zero, bmap, fiemap, fsync, direct I/O, or mmap; creates shared extents and forces copy-on-write conversions. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, diagnostic `$seqres.full` logs, shared extent/refcount and CoW fork metadata. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
extent-count and bmap/fiemap assertions can change with allocator behavior while data correctness remains stable; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/182.out`; stable progress labels including `echo "Format and mount"`, `echo "Create the original files"`, `echo "Compare files"`, `echo "CoW and unmount"`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 79 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/182 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/183 -->
# sources/test-tools/xfstests/tests/xfs/183

## Purpose
`sources/test-tools/xfstests/tests/xfs/183` is a XFS fstests regression. Test to check bulkstat returns unlinked-but-referenced inodes (PVs: 972128, 972004) Setup Filesystem run Mark Goodwin test here Usage: ./bulkstat_unlink_test iterations nfiles stride dir Create dir with nfiles, unlink each stride'th file, sync, bulkstat. The `_begin_fstest` declaration is `rw other auto quick`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`. Local helper surface: no local helpers beyond the main shell flow. Requirement gates: `_require_scratch`. Important external or harness commands observed in the full source include primarily fstests shell helpers. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
golden output can drift when xfsprogs diagnostics, filters, or common fstests helpers change; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/183.out`; stable progress labels including `echo "Start original bulkstat_unlink_test with -r switch"`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 33 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/183 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/184 -->
# sources/test-tools/xfstests/tests/xfs/184

## Purpose
`sources/test-tools/xfstests/tests/xfs/184` is a reflink and copy-on-write regression. Test fragmentation after a lot of random CoW: - Create two reflinked files.  Set extsz hint on second file. - Buffered write to random offsets to scatter CoW reservations. - falloc the whole file to unshare blocks. - Check the number of extents. The `_begin_fstest` declaration is `auto quick clone fiemap unshare`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`, `./common/reflink`. Local helper surface: no local helpers beyond the main shell flow. Requirement gates: `_require_scratch`, `_require_scratch_delalloc`, `_require_scratch_reflink`, `_require_cp_reflink`, `_require_xfs_io_command "fiemap"`, `_require_xfs_io_command "cowextsize"`, `_require_xfs_io_command "funshare"`, `_require_congruent_file_oplen $SCRATCH_MNT $blksz`, `_require_fs_space $SCRATCH_MNT $((filesize / 1024 * 3 * 5 / 4))`. Important external or harness commands observed in the full source include `mount`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; drives file layout with xfs_io operations such as fallocate, punch, zero, bmap, fiemap, fsync, direct I/O, or mmap; creates shared extents and forces copy-on-write conversions. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, diagnostic `$seqres.full` logs, shared extent/refcount and CoW fork metadata. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
extent-count and bmap/fiemap assertions can change with allocator behavior while data correctness remains stable; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/184.out`; stable progress labels including `echo "Format and mount"`, `echo "Create the original files"`, `echo "Compare files"`, `echo "CoW and unmount"`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 77 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/184 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/185 -->
# sources/test-tools/xfstests/tests/xfs/185

## Purpose
`sources/test-tools/xfstests/tests/xfs/185` is a preallocation/unwritten extent regression. Regression test for commits: c02f6529864a ("xfs: make xfs_rtalloc_query_range input parameters const") 9ab72f222774 ("xfs: fix off-by-one error when the last rt extent is in use") 7e1826e05ba6 ("xfs: make fsmap backend function key parameters const") These commits fix a bug in fsmap where the data device fsmap function would corrupt the high key passed to the rt fsmap function if the data device number is smaller than the rt device number and the data device itself is smaller than the rt device. The `_begin_fstest` declaration is `auto fsmap prealloc punch`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`. Local helper surface: `_cleanup`, `rtfile_exts`, `fsmap`. Requirement gates: `_require_test`, `_require_loop`, `_require_xfs_io_command "falloc"`, `_require_xfs_io_command "fpunch"`, `_require_xfs_io_command "fsmap"`. Important external or harness commands observed in the full source include `chattr`, `mount`, `umount`, `xfs_rtalloc_query_range`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow mounts, remounts, or deliberately rejects mounts through fstests helpers; drives file layout with xfs_io operations such as fallocate, punch, zero, bmap, fiemap, fsync, direct I/O, or mmap. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, temporary `$tmp.*` files, diagnostic `$seqres.full` logs, loop devices and loop-mounted images. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
intentional metadata corruption can leave the scratch device unmountable until repair or cleanup completes; loop-device setup and teardown must be exact to avoid leaked mounts or stale devices; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/185.out`; stable progress labels including `echo "data device ($ddbytes) has more bytes than rt ($rtbytes)"`, `echo "rtbytes $rtbytes rtfreebytes $rtfreebytes rtextsize $rtextsize" >> $seqres.full`, `echo "allocrtx $alloc_rtx falloc $((alloc_rtx * rtextsize))" >> $seqres.full`, `echo "$foff $fend $physoff $physend"`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 211 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/185 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/186 -->
# sources/test-tools/xfstests/tests/xfs/186

## Purpose
`sources/test-tools/xfstests/tests/xfs/186` is a XFS fstests regression. Test out: pv#979606: xfs bug in going from attr2 back to attr1 Test bug in going from attr2 back to attr1 where xfs (due to xfs_attr_shortform_bytesfit) would reset the di_forkoff to the m_offset instead of leaving the di_forkoff alone as was intended. We create enough dirents to push us past m_attroffset, and create an EA so we have a fork offset. The `_begin_fstest` declaration is `attr auto quick`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`, `./common/attr`. Local helper surface: `_create_dirents`, `_create_eas`, `_rmv_eas`, `_filter_inode`, `_filter_version`, `_print_inode`, `_do_eas`, `_do_dirents`, `_changeto_attr1`. Requirement gates: `_require_scratch`, `_require_attrs`, `_require_attr_v1`. Important external or harness commands observed in the full source include `mkfs`, `xfs_add_shortform_bytesfit`, `xfs_attr_shortform_bytesfit`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; uses xfs_db to inspect or perturb low-level metadata. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, temporary `$tmp.*` files, diagnostic `$seqres.full` logs, on-disk metadata fields modified for corruption testing. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
intentional metadata corruption can leave the scratch device unmountable until repair or cleanup completes; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/186.out`; stable progress labels including `echo ""`, `echo "================================="`, `echo "================================="`, `echo ""`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 167 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/186 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/187 -->
# sources/test-tools/xfstests/tests/xfs/187

## Purpose
`sources/test-tools/xfstests/tests/xfs/187` is a preallocation/unwritten extent regression. Regression test for commits: 9d5e8492eee0 ("xfs: adjust rt allocation minlen when extszhint > rtextsize") 676a659b60af ("xfs: retry allocations when locality-based search fails") The first bug occurs when an extent size hint is set on a realtime file. xfs_bmapi_rtalloc adjusts the offset and length of the allocation request to try to satisfy the hint, but doesn't adjust minlen to match.  If the allocator finds free space that isn't large enough to map even a single block of the original request, bmapi_write will return ENOSPC and the write fails. The `_begin_fstest` declaration is `auto quick rw realtime prealloc punch`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`. Local helper surface: `fill_rtdev`. Requirement gates: `_require_scratch`, `_require_realtime`, `_require_xfs_io_command "falloc"`, `_require_xfs_io_command "fpunch"`, `_require_test_program "punch-alternating"`. Important external or harness commands observed in the full source include `mount`, `punch-alternating`, `xfs_bmapi_rtalloc`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; drives file layout with xfs_io operations such as fallocate, punch, zero, bmap, fiemap, fsync, direct I/O, or mmap. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, diagnostic `$seqres.full` logs. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
golden output can drift when xfsprogs diagnostics, filters, or common fstests helpers change; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/187.out`; stable progress labels including `echo "$((f * chunksizemb)) file size $f / 20"`, `echo "$((f * chunksizemb)) file size $f / $chunks"`, `echo "Format and mount"`, `echo "rtextsize_blks=$rtextsize_blks extsize=$extsize" >> $seqres.full`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 158 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/187 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/188 -->
# sources/test-tools/xfstests/tests/xfs/188

## Purpose
`sources/test-tools/xfstests/tests/xfs/188` is a XFS fstests regression. drive the src/nametest program for CI mode which does a heap of open(create)/unlink/stat and checks that error codes make sense with its memory of the files created. All filenames generated map to the same hash value in XFS stressing leaf block traversal in node form directories as well. Override the default cleanup function. The `_begin_fstest` declaration is `ci dir auto`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`. Local helper surface: `_cleanup`. Requirement gates: `_require_scratch`, `_require_xfs_mkfs_ciname`, `_require_xfs_ciname`. Important external or harness commands observed in the full source include primarily fstests shell helpers. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, temporary `$tmp.*` files. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
golden output can drift when xfsprogs diagnostics, filters, or common fstests helpers change; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/188.out`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 60 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/188 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/189 -->
# sources/test-tools/xfstests/tests/xfs/189

## Purpose
`sources/test-tools/xfstests/tests/xfs/189` is a XFS fstests regression. Test remount behaviour Initial motivation was for pv#985710 and pv#983964 mount(8) adds all options from mtab and fstab to the mount command line.  So the filesystem either must not reject any option at all if it can't change it, or compare the value on the command line to the existing state and only reject it if it would change something that can't be changed. Test this behaviour by mounting a filesystem read-only with a non- default option and then try to remount it rw. The `_begin_fstest` declaration is `mount auto quick`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`, `./common/attr`. Local helper surface: `_cleanup`, `_scratch_filter`, `_check_mount`, `_test_remount_rw`, `_test_remount_write`, `_test_remount_barrier`, `_add_scratch_fstab`, `_modify_scratch_fstab`, `_putback_scratch_fstab`. Requirement gates: `_require_no_realtime`, `_require_scratch`, `_require_noattr2`. Important external or harness commands observed in the full source include `mount`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, temporary `$tmp.*` files, diagnostic `$seqres.full` logs. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
golden output can drift when xfsprogs diagnostics, filters, or common fstests helpers change; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/189.out`; stable progress labels including `echo -n "SCRATCH_DEV on SCRATCH_MNT type xfs ($rw_or_ro"`, `echo -n ",$2"`, `echo ")"`, `echo "try remount ro,filestreams -> rw,filestreams"`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 272 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/189 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/190 -->
# sources/test-tools/xfstests/tests/xfs/190

## Purpose
`sources/test-tools/xfstests/tests/xfs/190` is a XFS fstests regression. FSQA Test No. 190 This test uses xfs_io to unreserve space in a file at various different offsets and sizes. The script then verifies the holes are in the correct location. PV 985792 This is the list of holes to punch in the file limited to $filesize NOTE holes cannot overlap or this script will fail. filesize. The `_begin_fstest` declaration is `rw auto quick`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`. Local helper surface: no local helpers beyond the main shell flow. Requirement gates: `_require_scratch`. Important external or harness commands observed in the full source include `xfs_bmap`, `xfs_io`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; drives file layout with xfs_io operations such as fallocate, punch, zero, bmap, fiemap, fsync, direct I/O, or mmap. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, diagnostic `$seqres.full` logs. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
golden output can drift when xfsprogs diagnostics, filters, or common fstests helpers change; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/190.out`; stable progress labels including `echo Punching holes in file`, `echo Punching holes in file >> $seqres.full`, `echo $XFS_IO_PROG -c "unresvsp `echo $i |$SED_PROG 's/:/ /g'`" $SCRATCH_MNT/$filename >> $seqres.full`, `echo Verifying holes are in the correct spots:`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 84 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/190 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/191 -->
# sources/test-tools/xfstests/tests/xfs/191

## Purpose
`sources/test-tools/xfstests/tests/xfs/191` is a metadata repair/corruption regression. Make sure that XFS can handle empty leaf xattr blocks correctly.  These blocks can appear in files as a result of system crashes in the middle of xattr operations, which means that we /must/ handle them gracefully. Check that read and write verifiers won't trip, that the get/list/setxattr operations don't stumble over them, and that xfs_repair will offer to remove the entire xattr fork if the root xattr leaf block is empty. Regression test for kernel commit:. The `_begin_fstest` declaration is `auto quick attr`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`, `./common/attr`. Local helper surface: `make_empty_leaf`. Requirement gates: `_require_scratch`, `_require_scratch_xfs_crc # V4 is deprecated`. Important external or harness commands observed in the full source include `mkfs`, `xfs_db`, `xfs_repair`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; runs xfs_repair in checking or fixing mode and treats repair output as part of the oracle; uses xfs_db to inspect or perturb low-level metadata; drives file layout with xfs_io operations such as fallocate, punch, zero, bmap, fiemap, fsync, direct I/O, or mmap. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, temporary `$tmp.*` files, diagnostic `$seqres.full` logs, on-disk metadata fields modified for corruption testing. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
intentional metadata corruption can leave the scratch device unmountable until repair or cleanup completes; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/191.out`; stable progress labels including `echo "editing inode $inum" >> $seqres.full`, `echo "smallfile $smallfile_md5 does not match small attr $small_md5"`, `echo "largefile $largefile_md5 does not match large attr $large_md5"`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 131 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/191 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/192 -->
# sources/test-tools/xfstests/tests/xfs/192

## Purpose
`sources/test-tools/xfstests/tests/xfs/192` is a reflink and copy-on-write regression. Test fragmentation after a lot of random CoW: - Create two reflinked files.  Set extsz hint on second file. - Directio write to random offsets to scatter CoW reservations. - falloc the whole file to unshare blocks. - Check the number of extents. The `_begin_fstest` declaration is `auto quick clone fiemap unshare`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`, `./common/reflink`. Local helper surface: no local helpers beyond the main shell flow. Requirement gates: `_require_scratch`, `_require_scratch_delalloc`, `_require_scratch_reflink`, `_require_cp_reflink`, `_require_xfs_io_command "fiemap"`, `_require_xfs_io_command "cowextsize"`, `_require_xfs_io_command "funshare"`, `_require_odirect`, `_require_no_xfs_always_cow	# writes have to converge to overwrites`, `_require_congruent_file_oplen $SCRATCH_MNT $blksz`. Important external or harness commands observed in the full source include `mount`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; drives file layout with xfs_io operations such as fallocate, punch, zero, bmap, fiemap, fsync, direct I/O, or mmap; creates shared extents and forces copy-on-write conversions. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, diagnostic `$seqres.full` logs, shared extent/refcount and CoW fork metadata. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
extent-count and bmap/fiemap assertions can change with allocator behavior while data correctness remains stable; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/192.out`; stable progress labels including `echo "Format and mount"`, `echo "Create the original files"`, `echo "Compare files"`, `echo "CoW and unmount"`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 79 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/192 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/193 -->
# sources/test-tools/xfstests/tests/xfs/193

## Purpose
`sources/test-tools/xfstests/tests/xfs/193` is a reflink and copy-on-write regression. Test fragmentation after a lot of random CoW: - Create two reflinked files.  Set extsz hint on second file. - Buffered write to random offsets to scatter CoW reservations. - Check the number of extents. The `_begin_fstest` declaration is `auto quick clone fiemap`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`, `./common/reflink`. Local helper surface: no local helpers beyond the main shell flow. Requirement gates: `_require_scratch_reflink`, `_require_cp_reflink`, `_require_xfs_io_command "fiemap"`, `_require_xfs_io_command "cowextsize"`, `_require_congruent_file_oplen $SCRATCH_MNT $blksz`, `_require_fs_space $SCRATCH_MNT $((filesize / 1024 * 3 * 5 / 4))`. Important external or harness commands observed in the full source include `mount`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; drives file layout with xfs_io operations such as fallocate, punch, zero, bmap, fiemap, fsync, direct I/O, or mmap; creates shared extents and forces copy-on-write conversions. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, diagnostic `$seqres.full` logs, shared extent/refcount and CoW fork metadata. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
extent-count and bmap/fiemap assertions can change with allocator behavior while data correctness remains stable; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/193.out`; stable progress labels including `echo "Format and mount"`, `echo "Create the original files"`, `echo "Compare files"`, `echo "CoW and unmount"`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 71 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/193 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/194 -->
# sources/test-tools/xfstests/tests/xfs/194

## Purpose
`sources/test-tools/xfstests/tests/xfs/194` is a XFS fstests regression. Test mapping around/over holes for sub-page blocks Override the default cleanup function. Unmount the V4 filesystem we forcibly created to run this test so that the post-test wrapup checks won't try to remount the filesystem with different MOUNT_OPTIONS (specifically, the ones that get screened out by _force_xfsv4_mount_options) and fail. only xfs supported due to use of xfs_bmap This currently forces nocrc because only that can support 512 byte block size. The `_begin_fstest` declaration is `rw auto mmap`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`. Local helper surface: `_cleanup`, `_filter_bmap`, `_filter_od`. Requirement gates: `_require_scratch`, `_require_xfs_nocrc`. Important external or harness commands observed in the full source include `xfs_bmap`, `xfs_io`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; drives file layout with xfs_io operations such as fallocate, punch, zero, bmap, fiemap, fsync, direct I/O, or mmap. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, temporary `$tmp.*` files, diagnostic `$seqres.full` logs. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
golden output can drift when xfsprogs diagnostics, filters, or common fstests helpers change; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/194.out`; stable progress labels including `echo "== Test 1 =="`, `echo "== Test 2 =="`, `echo "== Test 3 =="`, `echo "== Test 4 =="`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 220 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/194 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/195 -->
# sources/test-tools/xfstests/tests/xfs/195

## Purpose
`sources/test-tools/xfstests/tests/xfs/195` is a xfsdump/xfsrestore coverage. Make sure the chattr dump flag gets picked up by xfsdump without a sync http://oss.sgi.com/bugzilla/show_bug.cgi?id=340 Override the default cleanup function. Perform a level 0 dump that respects the chattr dump exclude flag, and grep the output for the inode number we expect / do not expect to be skipped Only dump a subtree so we get away with a single partition for the subtree to be dumped and the dump file. The `_begin_fstest` declaration is `ioctl dump auto quick`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`. Local helper surface: `_cleanup`, `_do_dump`. Requirement gates: `_require_test`, `_require_user`, `_require_command "$XFSDUMP_PROG" xfsdump`. Important external or harness commands observed in the full source include `chattr`, `xfsdump`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow creates dump images or tape streams and verifies restore/inventory behavior. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, dump inventory, dump files, or tape media state. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
dump/restore output is sensitive to inventory state, media splitting, timestamp filtering, and quota special files; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/195.out`; stable progress labels including `echo "Preparing subtree"`, `echo "No dump exclude flag set (should not be skipped)"`, `echo "Dump exclude flag set, but no sync yet (should be skipped)"`, `echo "Dump exclude flag set, after sync (should be skipped)"`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 64 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/195 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/196 -->
# sources/test-tools/xfstests/tests/xfs/196

## Purpose
`sources/test-tools/xfstests/tests/xfs/196` is a XFS fstests regression. This test stresses indirect block reservation for delayed allocation extents. XFS reserves extra blocks for deferred allocation of delalloc extents. These reserved blocks can be divided among more extents than anticipated if the original extent for which the blocks were reserved is split into multiple delalloc extents. If this scenario repeats, eventually some extents are left without any indirect block reservation whatsoever. This leads to assert failures and possibly other problems in XFS. create sequential delayed allocation. The `_begin_fstest` declaration is `auto quick rw`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/punch`, `./common/inject`. Local helper surface: no local helpers beyond the main shell flow. Requirement gates: `_require_scratch`, `_require_xfs_io_error_injection "drop_writes"`. Important external or harness commands observed in the full source include primarily fstests shell helpers. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; drives file layout with xfs_io operations such as fallocate, punch, zero, bmap, fiemap, fsync, direct I/O, or mmap. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, diagnostic `$seqres.full` logs. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
golden output can drift when xfsprogs diagnostics, filters, or common fstests helpers change; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/196.out`; stable progress labels including `echo "Silence is golden."`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 80 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/196 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/197 -->
# sources/test-tools/xfstests/tests/xfs/197

## Purpose
`sources/test-tools/xfstests/tests/xfs/197` is a XFS fstests regression. Check that d_off can be represented in a 32 bit long type without truncation.  Note that this test will always succeed on a 64 bit systems where there is no smaller off_t. Based on a testcase from John Stanley <jpsinthemix@verizon.net>. http://oss.sgi.com/bugzilla/show_bug.cgi?id=808 Override the default cleanup function. The `_begin_fstest` declaration is `dir auto quick`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`. Local helper surface: `_cleanup`. Requirement gates: `_require_test`. Important external or harness commands observed in the full source include primarily fstests shell helpers. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow runs a linear fstests shell scenario after requirement gating. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
golden output can drift when xfsprogs diagnostics, filters, or common fstests helpers change; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/197.out`; stable progress labels including `echo "*** done"`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 42 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/197 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/198 -->
# sources/test-tools/xfstests/tests/xfs/198

## Purpose
`sources/test-tools/xfstests/tests/xfs/198` is a reflink and copy-on-write regression. Test fragmentation after a lot of random CoW: - Create two reflinked files.  Set extsz hint on second file. - Directio write to random offsets to scatter CoW reservations. - Check the number of extents. The `_begin_fstest` declaration is `auto quick clone fiemap`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`, `./common/reflink`. Local helper surface: no local helpers beyond the main shell flow. Requirement gates: `_require_scratch_reflink`, `_require_cp_reflink`, `_require_xfs_io_command "fiemap"`, `_require_xfs_io_command "cowextsize"`, `_require_odirect`, `_require_no_xfs_always_cow	# writes have to converge to overwrites`, `_require_congruent_file_oplen $SCRATCH_MNT $blksz`, `_require_fs_space $SCRATCH_MNT $((filesize / 1024 * 3 * 5 / 4))`. Important external or harness commands observed in the full source include `mount`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; drives file layout with xfs_io operations such as fallocate, punch, zero, bmap, fiemap, fsync, direct I/O, or mmap; creates shared extents and forces copy-on-write conversions. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, diagnostic `$seqres.full` logs, shared extent/refcount and CoW fork metadata. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
extent-count and bmap/fiemap assertions can change with allocator behavior while data correctness remains stable; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/198.out`; stable progress labels including `echo "Format and mount"`, `echo "Create the original files"`, `echo "Compare files"`, `echo "CoW and unmount"`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 73 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/198 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/199 -->
# sources/test-tools/xfstests/tests/xfs/199

## Purpose
`sources/test-tools/xfstests/tests/xfs/199` is a XFS fstests regression. Check that the features2 location fixups work correctly.  We check both a regular read-write mount of a filesystem and the case where the filesystem is first mounted read-only and then later remounted read-write, which is the usual case for the root filesystem. Override the default cleanup function. clear any mkfs options so that we can directly specify the options we need to be able to test the features bitmask behaviour correctly. Grab the initial configuration. This checks mkfs sets the fields properly, and. The `_begin_fstest` declaration is `mount auto quick`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`. Local helper surface: `_cleanup`. Requirement gates: `_require_scratch`, `_require_xfs_nocrc`. Important external or harness commands observed in the full source include `mkfs`, `mount`. Notable scenario variables include `MKFS_OPTIONS=`.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; uses xfs_db to inspect or perturb low-level metadata. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, on-disk metadata fields modified for corruption testing. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
intentional metadata corruption can leave the scratch device unmountable until repair or cleanup completes; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/199.out`; stable progress labels including `echo "Clearing features2:"`, `echo "Clearing features2:"`, `echo "*** done"`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 71 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/199 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/200 -->
# sources/test-tools/xfstests/tests/xfs/200

## Purpose
`sources/test-tools/xfstests/tests/xfs/200` is a reflink and copy-on-write regression. Test fragmentation after a lot of random CoW: - Create two reflinked files.  Set extsz hint on second file. - Read the whole file into memory. - Buffered write to random offsets to scatter CoW reservations. - fadvise(dontneed) the whole file to evict the pages. - falloc the whole fle to see if the extsz hints still apply. - Check the number of extents. The `_begin_fstest` declaration is `auto quick clone fiemap unshare`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`, `./common/reflink`. Local helper surface: no local helpers beyond the main shell flow. Requirement gates: `_require_scratch`, `_require_scratch_delalloc`, `_require_scratch_reflink`, `_require_cp_reflink`, `_require_xfs_io_command "fiemap"`, `_require_xfs_io_command "cowextsize"`, `_require_xfs_io_command "funshare"`, `_require_congruent_file_oplen $SCRATCH_MNT $blksz`, `_require_fs_space $SCRATCH_MNT $((filesize / 1024 * 3 * 5 / 4))`. Important external or harness commands observed in the full source include `mount`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; drives file layout with xfs_io operations such as fallocate, punch, zero, bmap, fiemap, fsync, direct I/O, or mmap; creates shared extents and forces copy-on-write conversions. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, diagnostic `$seqres.full` logs, shared extent/refcount and CoW fork metadata. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
extent-count and bmap/fiemap assertions can change with allocator behavior while data correctness remains stable; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/200.out`; stable progress labels including `echo "Format and mount"`, `echo "Create the original files"`, `echo "Compare files"`, `echo "CoW and unmount"`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 81 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/200 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/201 -->
# sources/test-tools/xfstests/tests/xfs/201

## Purpose
`sources/test-tools/xfstests/tests/xfs/201` is a XFS fstests regression. Test out the infamous xfs_btree_delrec corruption. Only happens on 32-bit kernels without CONFIG_LBD, but it should be harmless to run this everywhere. Override the default cleanup function. Create a fragmented file and truncate it again. The `_begin_fstest` declaration is `metadata auto quick`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`. Local helper surface: `_cleanup`, `do_pwrite`. Requirement gates: `_require_scratch`. Important external or harness commands observed in the full source include `xfs_btree_delrec`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; drives file layout with xfs_io operations such as fallocate, punch, zero, bmap, fiemap, fsync, direct I/O, or mmap. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
intentional metadata corruption can leave the scratch device unmountable until repair or cleanup completes; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/201.out`; stable progress labels including `echo "*** done"`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 75 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/201 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/202 -->
# sources/test-tools/xfstests/tests/xfs/202

## Purpose
`sources/test-tools/xfstests/tests/xfs/202` is a metadata repair/corruption regression. Test out the xfs_repair -o force_geometry option on single-AG filesystems. single AG will cause default xfs_repair to fail. This test is actually testing the special corner case option needed to repair a single AG fs. The AG size is limited to 1TB (or even less with historic xfsprogs), so chose a small enough filesystem to make sure we can actually create a single AG filesystem. The `_begin_fstest` declaration is `repair auto quick`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`, `./common/repair`. Local helper surface: no local helpers beyond the main shell flow. Requirement gates: `_require_scratch_nocheck`. Important external or harness commands observed in the full source include `xfs_repair`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; runs xfs_repair in checking or fixing mode and treats repair output as part of the oracle. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
golden output can drift when xfsprogs diagnostics, filters, or common fstests helpers change; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/202.out`; stable progress labels including `echo "== Creating single-AG filesystem =="`, `echo "== Trying to repair it (should fail) =="`, `echo "== Trying to repair it with -o force_geometry =="`, `echo "*** done"`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 37 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/202 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/203 -->
# sources/test-tools/xfstests/tests/xfs/203

## Purpose
`sources/test-tools/xfstests/tests/xfs/203` is a XFS fstests regression. Test out reallocation of the extent array in xfs_io. Based on a testcase from Tomasz Majkowski <moosh009@gmail.com>. prevent EOF preallocation from affecting results Override the default cleanup function. The xfs_bmap results in the golden output requires file allocations to align to 64k boundaries. The `_begin_fstest` declaration is `ioctl auto`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`. Local helper surface: `_write_holes`, `_filter_bmap`, `_cleanup`. Requirement gates: `_require_scratch`, `_require_congruent_file_oplen $SCRATCH_MNT 65536`. Important external or harness commands observed in the full source include `xfs_bmap`, `xfs_io`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; drives file layout with xfs_io operations such as fallocate, punch, zero, bmap, fiemap, fsync, direct I/O, or mmap. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
golden output can drift when xfsprogs diagnostics, filters, or common fstests helpers change; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/203.out`; stable progress labels including `echo "*** done"`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 68 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/203 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/204 -->
# sources/test-tools/xfstests/tests/xfs/204

## Purpose
`sources/test-tools/xfstests/tests/xfs/204` is a reflink and copy-on-write regression. Test fragmentation after a lot of random CoW: - Create two reflinked files.  Set extsz hint on second file. - Read the whole file into memory. - DIO write to random offsets to scatter CoW reservations. - fadvise(dontneed) the whole file to evict the pages. - falloc the whole fle to see if the extsz hints still apply. - Check the number of extents. The `_begin_fstest` declaration is `auto quick clone fiemap unshare`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`, `./common/reflink`. Local helper surface: no local helpers beyond the main shell flow. Requirement gates: `_require_scratch`, `_require_scratch_delalloc`, `_require_scratch_reflink`, `_require_cp_reflink`, `_require_xfs_io_command "fiemap"`, `_require_xfs_io_command "cowextsize"`, `_require_xfs_io_command "funshare"`, `_require_odirect`, `_require_no_xfs_always_cow	# writes have to converge to overwrites`, `_require_congruent_file_oplen $SCRATCH_MNT $blksz`. Important external or harness commands observed in the full source include `mount`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; drives file layout with xfs_io operations such as fallocate, punch, zero, bmap, fiemap, fsync, direct I/O, or mmap; creates shared extents and forces copy-on-write conversions. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, diagnostic `$seqres.full` logs, shared extent/refcount and CoW fork metadata. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
extent-count and bmap/fiemap assertions can change with allocator behavior while data correctness remains stable; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/204.out`; stable progress labels including `echo "Format and mount"`, `echo "Create the original files"`, `echo "Compare files"`, `echo "CoW and unmount"`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 83 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/204 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/205 -->
# sources/test-tools/xfstests/tests/xfs/205

## Purpose
`sources/test-tools/xfstests/tests/xfs/205` is a metadata repair/corruption regression. Test out ENOSPC flushing on small filesystems. single AG will cause xfs_repair to fail checks. Disable the scratch rt device to avoid test failures relating to the rt bitmap consuming all the free space in our small data device. fix the reserve block pool to a known size so that the enospc calculations work out correctly. on a 16MB filesystem, there's 32768x$fsblkszbyte blocks. used is: - 4944 in the log,. The `_begin_fstest` declaration is `metadata rw auto`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`. Local helper surface: no local helpers beyond the main shell flow. Requirement gates: `_require_scratch_nocheck`. Important external or harness commands observed in the full source include `xfs_repair`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; runs xfs_repair in checking or fixing mode and treats repair output as part of the oracle. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, diagnostic `$seqres.full` logs. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
golden output can drift when xfsprogs diagnostics, filters, or common fstests helpers change; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/205.out`; stable progress labels including `echo "blks: $blks b1: $b1 b2: $b2" >> $seqres.full`, `echo "*** one file"`, `echo "*** one file, a few bytes at a time"`, `echo space: $(_get_available_space $SCRATCH_MNT) >> $seqres.full`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 71 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/205 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/206 -->
# sources/test-tools/xfstests/tests/xfs/206

## Purpose
`sources/test-tools/xfstests/tests/xfs/206` is a reflink and copy-on-write regression. Test trim of last small AG for large filesystem resizes As reported at http://article.gmane.org/gmane.comp.file-systems.xfs.general/29187 this trimming may cause an overflow in the new size calculation. Patch and testcase at http://article.gmane.org/gmane.comp.file-systems.xfs.general/29193 Override the default cleanup function. Create a file w/ the offset we wish to resize to. The `_begin_fstest` declaration is `growfs auto quick`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`. Local helper surface: `_cleanup`, `mkfs_filter`. Requirement gates: `_require_test`, `_require_loop`. Important external or harness commands observed in the full source include `mkfs`, `mount`, `umount`, `xfs_growfs`, `xfs_info`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; creates shared extents and forces copy-on-write conversions. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, temporary `$tmp.*` files, loop devices and loop-mounted images, shared extent/refcount and CoW fork metadata. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
loop-device setup and teardown must be exact to avoid leaked mounts or stale devices; extent-count and bmap/fiemap assertions can change with allocator behavior while data correctness remains stable; online grow/shrink cases depend on free-space geometry and can skip or fail if ENOSPC behavior changes; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/206.out`; stable progress labels including `echo "=== truncate file ==="`, `echo "=== mkfs.xfs ==="`, `echo "=== xfs_growfs ==="`, `echo "=== xfs_info ==="`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 93 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/206 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/207 -->
# sources/test-tools/xfstests/tests/xfs/207

## Purpose
`sources/test-tools/xfstests/tests/xfs/207` is a reflink and copy-on-write regression. Test setting the extsz and cowextsz hints: - Ensure that we can set both on a zero-byte file. - Ensure that we can set only cowextsz on a many-byte file. - Ensure that whatever we set we get back later. The `_begin_fstest` declaration is `auto quick clone fiemap`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`, `./common/reflink`. Local helper surface: no local helpers beyond the main shell flow. Requirement gates: `_require_scratch_reflink`, `_require_cp_reflink`, `_require_xfs_io_command "fiemap"`, `_require_xfs_io_command "cowextsize"`. Important external or harness commands observed in the full source include `mount`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; drives file layout with xfs_io operations such as fallocate, punch, zero, bmap, fiemap, fsync, direct I/O, or mmap; creates shared extents and forces copy-on-write conversions. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, diagnostic `$seqres.full` logs, shared extent/refcount and CoW fork metadata. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
extent-count and bmap/fiemap assertions can change with allocator behavior while data correctness remains stable; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/207.out`; stable progress labels including `echo "Format and mount"`, `echo "Create the original files"`, `echo "Set extsz and cowextsz on zero byte file"`, `echo "Set extsz and cowextsz on 1Mbyte file"`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 72 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/207 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/208 -->
# sources/test-tools/xfstests/tests/xfs/208

## Purpose
`sources/test-tools/xfstests/tests/xfs/208` is a reflink and copy-on-write regression. Ensure that the effective cow extent allocation size hint is the maximum of the cowextsize and extsize inode fields. - Create two reflinked files.  Set extsz hint on second file to $blocksize and cowextsize hint to 1MB. - Buffered write to random offsets to scatter CoW reservations. - Rewrite the whole file to use up reservations. - Check the number of extents. - Repeat, but with extsz = 1MB and cowextsz = $blocksize. The `_begin_fstest` declaration is `auto quick clone fiemap`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`, `./common/reflink`. Local helper surface: no local helpers beyond the main shell flow. Requirement gates: `_require_scratch_reflink`, `_require_cp_reflink`, `_require_xfs_io_command "fiemap"`, `_require_xfs_io_command "cowextsize"`, `_require_no_xfs_always_cow`, `_require_congruent_file_oplen $SCRATCH_MNT $blksz`, `_require_fs_space $SCRATCH_MNT $((filesize / 1024 * 3 * 5 / 4))`. Important external or harness commands observed in the full source include `mount`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; drives file layout with xfs_io operations such as fallocate, punch, zero, bmap, fiemap, fsync, direct I/O, or mmap; creates shared extents and forces copy-on-write conversions. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, diagnostic `$seqres.full` logs, shared extent/refcount and CoW fork metadata. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
extent-count and bmap/fiemap assertions can change with allocator behavior while data correctness remains stable; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/208.out`; stable progress labels including `echo "Format and mount"`, `echo "Create the original files"`, `echo "Compare files"`, `echo "CoW and unmount"`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 108 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/208 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/209 -->
# sources/test-tools/xfstests/tests/xfs/209

## Purpose
`sources/test-tools/xfstests/tests/xfs/209` is a reflink and copy-on-write regression. Make sure setting cowextsz on a directory propagates it to subfiles. The `_begin_fstest` declaration is `auto quick clone fiemap`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`, `./common/reflink`. Local helper surface: no local helpers beyond the main shell flow. Requirement gates: `_require_scratch_reflink`, `_require_cp_reflink`, `_require_xfs_io_command "fiemap"`, `_require_xfs_io_command "cowextsize"`, `_require_congruent_file_oplen $SCRATCH_MNT 1048576`. Important external or harness commands observed in the full source include `mount`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; drives file layout with xfs_io operations such as fallocate, punch, zero, bmap, fiemap, fsync, direct I/O, or mmap; creates shared extents and forces copy-on-write conversions. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, diagnostic `$seqres.full` logs, shared extent/refcount and CoW fork metadata. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
extent-count and bmap/fiemap assertions can change with allocator behavior while data correctness remains stable; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/209.out`; stable progress labels including `echo "Format and mount"`, `echo "Set extsz and cowextsz on directory"`, `echo "Create a fake tree structure"`, `echo "Check cowextsize settings"`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 51 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/209 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/210 -->
# sources/test-tools/xfstests/tests/xfs/210

## Purpose
`sources/test-tools/xfstests/tests/xfs/210` is a reflink and copy-on-write regression. During reflink, XFS should carry the cowextsz setting to the destination file if the destination file size is less than the size of the source file, the length is the size of the source file, both offsets are zero, and the destination does not already have a cowextsz setting.  It should not do so otherwise. The `_begin_fstest` declaration is `auto quick clone fiemap`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`, `./common/reflink`. Local helper surface: no local helpers beyond the main shell flow. Requirement gates: `_require_scratch_reflink`, `_require_cp_reflink`, `_require_xfs_io_command "fiemap"`, `_require_xfs_io_command "cowextsize"`, `_require_congruent_file_oplen $SCRATCH_MNT 65536`. Important external or harness commands observed in the full source include `mount`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; drives file layout with xfs_io operations such as fallocate, punch, zero, bmap, fiemap, fsync, direct I/O, or mmap; creates shared extents and forces copy-on-write conversions. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, diagnostic `$seqres.full` logs, shared extent/refcount and CoW fork metadata. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
extent-count and bmap/fiemap assertions can change with allocator behavior while data correctness remains stable; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/210.out`; stable progress labels including `echo "Format and mount"`, `echo "Create initial file"`, `echo "Reflink to an empty file"`, `echo "Reflink to an empty file that already has cowextsz"`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 77 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/210 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/211 -->
# sources/test-tools/xfstests/tests/xfs/211

## Purpose
`sources/test-tools/xfstests/tests/xfs/211` is a reflink and copy-on-write regression. Test fragmentation in a big file after a lot of random CoW: - Create two reflinked files.  Set extsz hint on second file. - Directio write to random offsets to scatter CoW reservations. - Rewrite the whole file to use up reservations. - Check the number of extents. The `_begin_fstest` declaration is `clone_stress fiemap`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`, `./common/reflink`. Local helper surface: no local helpers beyond the main shell flow. Requirement gates: `_require_scratch_reflink`, `_require_cp_reflink`, `_require_xfs_io_command "fiemap"`, `_require_xfs_io_command "cowextsize"`, `_require_odirect`, `_require_no_xfs_always_cow	# writes have to converge to overwrites`, `_require_congruent_file_oplen $SCRATCH_MNT $blksz`, `_require_fs_space $SCRATCH_MNT $((filesize / 1024 * 2 * 5 / 4))`. Important external or harness commands observed in the full source include `mount`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; drives file layout with xfs_io operations such as fallocate, punch, zero, bmap, fiemap, fsync, direct I/O, or mmap; creates shared extents and forces copy-on-write conversions. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, diagnostic `$seqres.full` logs, shared extent/refcount and CoW fork metadata. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
extent-count and bmap/fiemap assertions can change with allocator behavior while data correctness remains stable; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/211.out`; stable progress labels including `echo "Format and mount"`, `echo "Create the original files"`, `echo "Compare files"`, `echo "CoW and unmount"`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 77 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/211 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/212 -->
# sources/test-tools/xfstests/tests/xfs/212

## Purpose
`sources/test-tools/xfstests/tests/xfs/212` is a reflink and copy-on-write regression. Test recovery of "lost" CoW blocks after a crash: - Create two reflinked files.  Set extsz hint on second file. - Dirty one byte on the second file and fsync. - Crash the FS to test recovery. The `_begin_fstest` declaration is `shutdown auto quick clone fiemap`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`, `./common/reflink`. Local helper surface: no local helpers beyond the main shell flow. Requirement gates: `_require_scratch_reflink`, `_require_cp_reflink`, `_require_xfs_io_command "fiemap"`, `_require_congruent_file_oplen $SCRATCH_MNT $blksz`, `_require_fs_space $SCRATCH_MNT $((filesize / 1024 * 3 * 5 / 4))`. Important external or harness commands observed in the full source include `mount`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; drives file layout with xfs_io operations such as fallocate, punch, zero, bmap, fiemap, fsync, direct I/O, or mmap; creates shared extents and forces copy-on-write conversions. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, diagnostic `$seqres.full` logs, shared extent/refcount and CoW fork metadata. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
extent-count and bmap/fiemap assertions can change with allocator behavior while data correctness remains stable; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/212.out`; stable progress labels including `echo "Format and mount"`, `echo "Create the original files"`, `echo "Compare files"`, `echo "CoW and leave leftovers"`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 68 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/212 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/213 -->
# sources/test-tools/xfstests/tests/xfs/213

## Purpose
`sources/test-tools/xfstests/tests/xfs/213` is a quota behavior regression. Ensure that quota charges us for reflnking a file and that we're not charged for buffered copy on write.  Same test as g/305, but we get to play with cowextsz. The `_begin_fstest` declaration is `auto quick clone fiemap`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`, `./common/reflink`, `./common/quota`. Local helper surface: no local helpers beyond the main shell flow. Requirement gates: `_require_scratch_reflink`, `_require_cp_reflink`, `_require_xfs_io_command "fiemap"`, `_require_quota`, `_require_nobody`, `_require_xfs_io_command "cowextsize"`, `_require_user`. Important external or harness commands observed in the full source include `mount`, `quota`, `quotacheck`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; drives file layout with xfs_io operations such as fallocate, punch, zero, bmap, fiemap, fsync, direct I/O, or mmap; configures or queries user/group/project quota state; creates shared extents and forces copy-on-write conversions. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, diagnostic `$seqres.full` logs, quota accounting and grace-period metadata, shared extent/refcount and CoW fork metadata. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
quota output and timer calculations are sensitive to quota-tools versions, current time, and 32-bit time support; extent-count and bmap/fiemap assertions can change with allocator behavior while data correctness remains stable; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/213.out`; stable progress labels including `echo "Format and mount"`, `echo "Create the original files"`, `echo "Change file ownership"`, `echo "CoW one of the files"`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 72 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/213 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/214 -->
# sources/test-tools/xfstests/tests/xfs/214

## Purpose
`sources/test-tools/xfstests/tests/xfs/214` is a quota behavior regression. Ensure that quota charges us for reflnking a file and that we're not charged for directio copy on write.  Same as g/326, but we get to play with cowextsz. The `_begin_fstest` declaration is `auto quick clone fiemap`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`, `./common/reflink`, `./common/quota`. Local helper surface: no local helpers beyond the main shell flow. Requirement gates: `_require_scratch_reflink`, `_require_cp_reflink`, `_require_xfs_io_command "fiemap"`, `_require_quota`, `_require_nobody`, `_require_xfs_io_command "cowextsize"`, `_require_odirect`, `_require_user`. Important external or harness commands observed in the full source include `mount`, `quota`, `quotacheck`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; drives file layout with xfs_io operations such as fallocate, punch, zero, bmap, fiemap, fsync, direct I/O, or mmap; configures or queries user/group/project quota state; creates shared extents and forces copy-on-write conversions. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, diagnostic `$seqres.full` logs, quota accounting and grace-period metadata, shared extent/refcount and CoW fork metadata. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
quota output and timer calculations are sensitive to quota-tools versions, current time, and 32-bit time support; extent-count and bmap/fiemap assertions can change with allocator behavior while data correctness remains stable; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/214.out`; stable progress labels including `echo "Format and mount"`, `echo "Create the original files"`, `echo "Change file ownership"`, `echo "CoW one of the files"`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 73 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/214 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/215 -->
# sources/test-tools/xfstests/tests/xfs/215

## Purpose
`sources/test-tools/xfstests/tests/xfs/215` is a reflink and copy-on-write regression. Ensuring that copy on write in direct-io mode works when the CoW range originally covers multiple extents, some unwritten, some not. - Set cowextsize hint. - Create a file and fallocate a second file. - Reflink the odd blocks of the first file into the second file. - directio CoW across the halfway mark, starting with the unwritten extent. - Check that the files are now different where we say they're different. The `_begin_fstest` declaration is `auto quick clone prealloc`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`, `./common/reflink`. Local helper surface: no local helpers beyond the main shell flow. Requirement gates: `_require_scratch_reflink`, `_require_xfs_io_command "falloc"`, `_require_xfs_io_command "cowextsize"`, `_require_odirect`, `_require_congruent_file_oplen $SCRATCH_MNT $blksz`. Important external or harness commands observed in the full source include `mount`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; drives file layout with xfs_io operations such as fallocate, punch, zero, bmap, fiemap, fsync, direct I/O, or mmap; creates shared extents and forces copy-on-write conversions. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, diagnostic `$seqres.full` logs, shared extent/refcount and CoW fork metadata. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
extent-count and bmap/fiemap assertions can change with allocator behavior while data correctness remains stable; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/215.out`; stable progress labels including `echo "Format and mount"`, `echo "Create the original files"`, `echo "Compare files"`, `echo "directio CoW across the transition"`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 73 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/215 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/216 -->
# sources/test-tools/xfstests/tests/xfs/216

## Purpose
`sources/test-tools/xfstests/tests/xfs/216` is a reflink and copy-on-write regression. log size mkfs test - ensure the log size scaling works for small filesystems Decide which golden output file we're using.  Starting with mkfs.xfs 5.15, the default minimum log size was raised to 64MB for all cases, so we detect that by test-formatting with a 512M filesystem.  This is a little handwavy, but it's the best we can do. make large holey file make loopback mount dir walk over standard sizes (up to 256GB). The `_begin_fstest` declaration is `log metadata auto quick`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`. Local helper surface: `_cleanup`, `choose_golden_output`, `_do_mkfs`. Requirement gates: `_require_scratch`, `_require_loop`. Important external or harness commands observed in the full source include `mkfs`, `mount`. Notable scenario variables include `LOOP_IMG=$SCRATCH_MNT/test_fs`, `LOOP_MNT=$SCRATCH_MNT/test_fs_dir`.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; drives file layout with xfs_io operations such as fallocate, punch, zero, bmap, fiemap, fsync, direct I/O, or mmap; creates shared extents and forces copy-on-write conversions. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, temporary `$tmp.*` files, loop devices and loop-mounted images, shared extent/refcount and CoW fork metadata. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
loop-device setup and teardown must be exact to avoid leaked mounts or stale devices; extent-count and bmap/fiemap assertions can change with allocator behavior while data correctness remains stable; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
variant configuration `sources/test-tools/xfstests/tests/xfs/216.cfg`; stable progress labels including `echo -n "fssize=${i}g "`, `echo "test write" > $LOOP_MNT/test`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 81 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/216 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/216.cfg -->
# sources/test-tools/xfstests/tests/xfs/216.cfg

## Purpose
`sources/test-tools/xfstests/tests/xfs/216.cfg` is the golden-output selector configuration for `xfs/216`. It maps mkfs log-size behavior variants to the named expected-output streams `64mblog` and `classic`, allowing the test to choose the correct oracle for newer mkfs.xfs defaults versus older classic log sizing.

## Important APIs, Types, And Functions
This is a tiny fstests `.cfg` data file, not an executable shell test. It exposes two labels, `64mblog` and `classic`, which are consumed by `xfs/216` through `_link_out_file_named` after the script probes mkfs.xfs behavior.

## Control Flow
There is no runtime control flow in the cfg file itself. The integration point is `xfs/216`'s `choose_golden_output` helper, which runs a trial mkfs, detects whether a 512MiB filesystem receives a 64MiB log, and links the corresponding expected output name.

## State And Persistence Behavior
The file has no persistent state of its own. It affects which expected-output stream the harness compares against for the loop-backed mkfs log-size test.

## Dependencies And Integration Points
It depends on fstests named-output handling and on `xfs/216` keeping the `64mblog` and `classic` names in sync with the cfg entries.

## Risks
If mkfs.xfs changes log-size defaults again, this cfg may need another output variant or the detection in `xfs/216` may choose an outdated oracle.

## Test Signals
The validation signal is indirect: `xfs/216` links one of these named outputs and then compares its emitted mkfs log lines to the selected golden output. The source has 2 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/216.cfg -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/217 -->
# sources/test-tools/xfstests/tests/xfs/217

## Purpose
`sources/test-tools/xfstests/tests/xfs/217` is a log recovery or log-geometry regression. large log size mkfs test - ensure the log size scaling works 16T mkfs requires a bit over 2G free punch out the previous blocks so that we keep the amount of disk space the test requires down to a minimum. make large holey file make loopback mount dir test if large logs are supported walk over "new" sizes supported by recent xfsprogs. The `_begin_fstest` declaration is `log metadata auto`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`. Local helper surface: `_cleanup`, `_do_mkfs`. Requirement gates: `_require_scratch`, `_require_fs_space $SCRATCH_MNT 2202000`, `_require_loop`. Important external or harness commands observed in the full source include `mkfs`, `mount`. Notable scenario variables include `LOOP_IMG=$SCRATCH_MNT/test_fs`, `LOOP_MNT=$SCRATCH_MNT/test_fs_dir`.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; drives file layout with xfs_io operations such as fallocate, punch, zero, bmap, fiemap, fsync, direct I/O, or mmap. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, temporary `$tmp.*` files, loop devices and loop-mounted images. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
loop-device setup and teardown must be exact to avoid leaked mounts or stale devices; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/217.out`; stable progress labels including `echo -n "fssize=${i}g "`, `echo "test write" > $LOOP_MNT/test`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 71 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/217 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/218 -->
# sources/test-tools/xfstests/tests/xfs/218

## Purpose
`sources/test-tools/xfstests/tests/xfs/218` is a reflink and copy-on-write regression. Ensuring that copy on write in buffered mode works when the CoW range originally covers multiple extents, some unwritten, some not. - Set cowextsize hint. - Create a file and fallocate a second file. - Reflink the odd blocks of the first file into the second file. - CoW across the halfway mark, starting with the unwritten extent. - Check that the files are now different where we say they're different. The `_begin_fstest` declaration is `auto quick clone prealloc`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`, `./common/reflink`. Local helper surface: no local helpers beyond the main shell flow. Requirement gates: `_require_scratch_reflink`, `_require_xfs_io_command "falloc"`, `_require_xfs_io_command "cowextsize"`, `_require_congruent_file_oplen $SCRATCH_MNT $blksz`. Important external or harness commands observed in the full source include `mount`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; drives file layout with xfs_io operations such as fallocate, punch, zero, bmap, fiemap, fsync, direct I/O, or mmap; creates shared extents and forces copy-on-write conversions. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, diagnostic `$seqres.full` logs, shared extent/refcount and CoW fork metadata. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
extent-count and bmap/fiemap assertions can change with allocator behavior while data correctness remains stable; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/218.out`; stable progress labels including `echo "Format and mount"`, `echo "Create the original files"`, `echo "Compare files"`, `echo "CoW across the transition"`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 72 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/218 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/219 -->
# sources/test-tools/xfstests/tests/xfs/219

## Purpose
`sources/test-tools/xfstests/tests/xfs/219` is a reflink and copy-on-write regression. Ensuring that copy on write in direct-io mode works when the CoW range originally covers multiple extents, some holes, some not. - Set cowextsize hint. - Create a file and truncate a second file. - Reflink the odd blocks of the first file into the second file. - directio CoW across the halfway mark, starting with the unwritten extent. - Check that the files are now different where we say they're different. The `_begin_fstest` declaration is `auto quick clone prealloc`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`, `./common/reflink`. Local helper surface: no local helpers beyond the main shell flow. Requirement gates: `_require_scratch_reflink`, `_require_xfs_io_command "falloc"`, `_require_xfs_io_command "cowextsize"`, `_require_odirect`, `_require_congruent_file_oplen $SCRATCH_MNT $blksz`. Important external or harness commands observed in the full source include `mount`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; drives file layout with xfs_io operations such as fallocate, punch, zero, bmap, fiemap, fsync, direct I/O, or mmap; creates shared extents and forces copy-on-write conversions. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, diagnostic `$seqres.full` logs, shared extent/refcount and CoW fork metadata. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
extent-count and bmap/fiemap assertions can change with allocator behavior while data correctness remains stable; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/219.out`; stable progress labels including `echo "Format and mount"`, `echo "Create the original files"`, `echo "Compare files"`, `echo "directio CoW across the transition"`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 73 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/219 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/220 -->
# sources/test-tools/xfstests/tests/xfs/220

## Purpose
`sources/test-tools/xfstests/tests/xfs/220` is a quota behavior regression. Test quota off handling. Based on bug reports from Utako Kusaka <u-kusaka@wm.jp.nec.com> and Ryota Yamauchi <r-yamauchi@vf.jp.nec.com>. Override the default cleanup function. Only mount with the specific quota options mentioned below create scratch filesystem mount  with quotas enabled turn off quota. The `_begin_fstest` declaration is `auto quota quick`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`, `./common/quota`. Local helper surface: `_cleanup`. Requirement gates: `_require_scratch`, `_require_quota`. Important external or harness commands observed in the full source include `mount`, `quota`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; configures or queries user/group/project quota state. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, diagnostic `$seqres.full` logs, quota accounting and grace-period metadata. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
quota output and timer calculations are sensitive to quota-tools versions, current time, and 32-bit time support; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/220.out`; stable progress labels including `echo "Silence is golden."`, `echo "freesp $before_freesp -> $after_freesp ($delta)" >> $seqres.full`, `echo "expected Q_XQUOTARM to free space"`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 84 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/220 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/221 -->
# sources/test-tools/xfstests/tests/xfs/221

## Purpose
`sources/test-tools/xfstests/tests/xfs/221` is a reflink and copy-on-write regression. Ensuring that copy on write in buffered mode works when the CoW range originally covers multiple extents, some holes, some not. - Set cowextsize hint. - Create a file and truncate a second file. - Reflink the odd blocks of the first file into the second file. - CoW across the halfway mark, starting with the unwritten extent. - Check that the files are now different where we say they're different. The `_begin_fstest` declaration is `auto quick clone prealloc`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`, `./common/reflink`. Local helper surface: no local helpers beyond the main shell flow. Requirement gates: `_require_scratch_reflink`, `_require_xfs_io_command "falloc"`, `_require_xfs_io_command "cowextsize"`, `_require_congruent_file_oplen $SCRATCH_MNT $blksz`. Important external or harness commands observed in the full source include `mount`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; drives file layout with xfs_io operations such as fallocate, punch, zero, bmap, fiemap, fsync, direct I/O, or mmap; creates shared extents and forces copy-on-write conversions. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, diagnostic `$seqres.full` logs, shared extent/refcount and CoW fork metadata. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
extent-count and bmap/fiemap assertions can change with allocator behavior while data correctness remains stable; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/221.out`; stable progress labels including `echo "Format and mount"`, `echo "Create the original files"`, `echo "Compare files"`, `echo "CoW across the transition"`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 72 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/221 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/222 -->
# sources/test-tools/xfstests/tests/xfs/222

## Purpose
`sources/test-tools/xfstests/tests/xfs/222` is a XFS fstests regression. xfs_fsr QA tests run xfs_fsr over the test filesystem to give it a wide and varied set of inodes to try to defragment. This is effectively a crash/assert failure test looking for corruption induced by xfs_fsr runs. The `_begin_fstest` declaration is `auto fsr ioctl quick`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`. Local helper surface: no local helpers beyond the main shell flow. Requirement gates: `_require_test`. Important external or harness commands observed in the full source include `xfs_fsr`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow runs a linear fstests shell scenario after requirement gating. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, diagnostic `$seqres.full` logs. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
intentional metadata corruption can leave the scratch device unmountable until repair or cleanup completes; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/222.out`; stable progress labels including `echo "--- silence is golden ---"`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 25 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/222 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/223 -->
# sources/test-tools/xfstests/tests/xfs/223

## Purpose
`sources/test-tools/xfstests/tests/xfs/223` is a reflink and copy-on-write regression. Ensuring that copy on write in direct-io mode works when the CoW range originally covers multiple extents, some delalloc, some not. - Set cowextsize hint. - Create a file. - Reflink the odd blocks of the first file into the second file. - Buffered write the even blocks of the second file. - directio CoW across the halfway mark, starting with the unwritten extent. - Check that the files are now different where we say they're different. The `_begin_fstest` declaration is `auto quick clone prealloc`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`, `./common/reflink`. Local helper surface: no local helpers beyond the main shell flow. Requirement gates: `_require_scratch_reflink`, `_require_scratch_delalloc`, `_require_xfs_io_command "falloc"`, `_require_xfs_io_command "cowextsize"`, `_require_odirect`, `_require_congruent_file_oplen $SCRATCH_MNT $blksz`. Important external or harness commands observed in the full source include `mount`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; drives file layout with xfs_io operations such as fallocate, punch, zero, bmap, fiemap, fsync, direct I/O, or mmap; creates shared extents and forces copy-on-write conversions. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, diagnostic `$seqres.full` logs, shared extent/refcount and CoW fork metadata. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
extent-count and bmap/fiemap assertions can change with allocator behavior while data correctness remains stable; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/223.out`; stable progress labels including `echo "Format and mount"`, `echo "Create the original files"`, `echo "Compare files"`, `echo "directio CoW across the transition"`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 76 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/223 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/224 -->
# sources/test-tools/xfstests/tests/xfs/224

## Purpose
`sources/test-tools/xfstests/tests/xfs/224` is a reflink and copy-on-write regression. Ensuring that copy on write in buffered mode works when the CoW range originally covers multiple extents, some delalloc, some not. - Set cowextsize hint. - Create a file. - Reflink the odd blocks of the first file into the second file. - Buffered write the even blocks of the second file. - CoW across the halfway mark, starting with the unwritten extent. - Check that the files are now different where we say they're different. The `_begin_fstest` declaration is `auto quick clone prealloc`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`, `./common/reflink`. Local helper surface: no local helpers beyond the main shell flow. Requirement gates: `_require_scratch_reflink`, `_require_scratch_delalloc`, `_require_xfs_io_command "falloc"`, `_require_xfs_io_command "cowextsize"`, `_require_congruent_file_oplen $SCRATCH_MNT $blksz`. Important external or harness commands observed in the full source include `mount`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; drives file layout with xfs_io operations such as fallocate, punch, zero, bmap, fiemap, fsync, direct I/O, or mmap; creates shared extents and forces copy-on-write conversions. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, diagnostic `$seqres.full` logs, shared extent/refcount and CoW fork metadata. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
extent-count and bmap/fiemap assertions can change with allocator behavior while data correctness remains stable; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/224.out`; stable progress labels including `echo "Format and mount"`, `echo "Create the original files"`, `echo "Compare files"`, `echo "CoW across the transition"`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 75 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/224 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/225 -->
# sources/test-tools/xfstests/tests/xfs/225

## Purpose
`sources/test-tools/xfstests/tests/xfs/225` is a reflink and copy-on-write regression. Ensuring that copy on write in direct-io mode works when the CoW range originally covers multiple extents, some regular, some not. - Set cowextsize hint. - Create two files. - Reflink the odd blocks of the first file into the second file. - directio CoW across the halfway mark, starting with the unwritten extent. - Check that the files are now different where we say they're different. The `_begin_fstest` declaration is `auto quick clone prealloc`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`, `./common/reflink`. Local helper surface: no local helpers beyond the main shell flow. Requirement gates: `_require_scratch_reflink`, `_require_xfs_io_command "falloc"`, `_require_xfs_io_command "cowextsize"`, `_require_odirect`, `_require_congruent_file_oplen $SCRATCH_MNT $blksz`. Important external or harness commands observed in the full source include `mount`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; drives file layout with xfs_io operations such as fallocate, punch, zero, bmap, fiemap, fsync, direct I/O, or mmap; creates shared extents and forces copy-on-write conversions. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, diagnostic `$seqres.full` logs, shared extent/refcount and CoW fork metadata. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
extent-count and bmap/fiemap assertions can change with allocator behavior while data correctness remains stable; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/225.out`; stable progress labels including `echo "Format and mount"`, `echo "Create the original files"`, `echo "Compare files"`, `echo "directio CoW across the transition"`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 73 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/225 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/226 -->
# sources/test-tools/xfstests/tests/xfs/226

## Purpose
`sources/test-tools/xfstests/tests/xfs/226` is a reflink and copy-on-write regression. Ensuring that copy on write in buffered mode works when the CoW range originally covers multiple extents, some regular, some not. - Set cowextsize hint. - Create two files. - Reflink the odd blocks of the first file into the second file. - CoW across the halfway mark, starting with the unwritten extent. - Check that the files are now different where we say they're different. The `_begin_fstest` declaration is `auto quick clone prealloc`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`, `./common/reflink`. Local helper surface: no local helpers beyond the main shell flow. Requirement gates: `_require_scratch_reflink`, `_require_xfs_io_command "falloc"`, `_require_xfs_io_command "cowextsize"`, `_require_congruent_file_oplen $SCRATCH_MNT $blksz`. Important external or harness commands observed in the full source include `mount`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; drives file layout with xfs_io operations such as fallocate, punch, zero, bmap, fiemap, fsync, direct I/O, or mmap; creates shared extents and forces copy-on-write conversions. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, diagnostic `$seqres.full` logs, shared extent/refcount and CoW fork metadata. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
extent-count and bmap/fiemap assertions can change with allocator behavior while data correctness remains stable; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/226.out`; stable progress labels including `echo "Format and mount"`, `echo "Create the original files"`, `echo "Compare files"`, `echo "CoW across the transition"`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 72 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/226 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/227 -->
# sources/test-tools/xfstests/tests/xfs/227

## Purpose
`sources/test-tools/xfstests/tests/xfs/227` is a XFS fstests regression. xfs_fsr QA tests run xfs_fsr over the test filesystem to give it a wide and varied set of inodes to try to defragment. This is effectively a crash/assert failure test looking for corruption induced by the kernel inadequately checking the indoes to be swapped. It also is good for validating fsr's attribute fork generation code. create freespace holes of 1-3 blocks in length This is done to ensure that defragmented files have roughly 1/3 the. The `_begin_fstest` declaration is `auto fsr`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`. Local helper surface: `fragment_freespace`, `create_attrs`, `create_data`, `create_target_attr_first`, `create_target_attr_last`, `do_fsr`. Requirement gates: `_require_scratch`. Important external or harness commands observed in the full source include `xfs_bmap`, `xfs_fsr`. Notable scenario variables include `FSRXFSTEST=true xfs_fsr -d -v -C $n $targ.$i.* >> $seqres.full 2>&1`, `FSRXFSTEST=true xfs_fsr -d -v -C $n $targ.$i.* >> $seqres.full 2>&1`.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; drives file layout with xfs_io operations such as fallocate, punch, zero, bmap, fiemap, fsync, direct I/O, or mmap. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, temporary `$tmp.*` files, diagnostic `$seqres.full` logs. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
intentional metadata corruption can leave the scratch device unmountable until repair or cleanup completes; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/227.out`; stable progress labels including `echo -n > $_file.$i`, `echo "user.$foo=\"0xbabe\""`, `echo "*** n == $n ***" >> $seqres.full`, `echo "--- silence is golden ---"`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 189 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/227 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/228 -->
# sources/test-tools/xfstests/tests/xfs/228

## Purpose
`sources/test-tools/xfstests/tests/xfs/228` is a reflink and copy-on-write regression. Ensuring that copy on write in direct-io mode works when the CoW range originally covers multiple extents, some unwritten, some not. - Set cowextsize hint. - Create a file with the following repeating sequence of blocks: 1. reflinked 2. unwritten 3. hole 4. regular block. The `_begin_fstest` declaration is `auto quick clone punch prealloc`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`, `./common/reflink`. Local helper surface: no local helpers beyond the main shell flow. Requirement gates: `_require_scratch_reflink`, `_require_scratch_delalloc`, `_require_xfs_io_command "falloc"`, `_require_xfs_io_command "cowextsize"`, `_require_xfs_io_command "fpunch"`, `_require_cp_reflink`, `_require_odirect`, `_require_congruent_file_oplen $SCRATCH_MNT $blksz`. Important external or harness commands observed in the full source include `mount`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; drives file layout with xfs_io operations such as fallocate, punch, zero, bmap, fiemap, fsync, direct I/O, or mmap; creates shared extents and forces copy-on-write conversions. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, diagnostic `$seqres.full` logs, shared extent/refcount and CoW fork metadata. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
extent-count and bmap/fiemap assertions can change with allocator behavior while data correctness remains stable; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/228.out`; stable progress labels including `echo "Format and mount"`, `echo "Create the original files"`, `echo "Compare files"`, `echo "directio CoW across the transition"`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 82 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/228 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/229 -->
# sources/test-tools/xfstests/tests/xfs/229

## Purpose
`sources/test-tools/xfstests/tests/xfs/229` is a XFS fstests regression. Check for file corruption when using the extent size hint on the normal data subvolume. http://oss.sgi.com/bugzilla/show_bug.cgi?id=874 Based on a bug report and testcase from Geoffrey Wehrman <gwehrman@sgi.com>. Override the default cleanup function. Create the test directory Per-directory extent size hints aren't particularly useful for files that are created on the realtime section.  Force the test file to be created on. The `_begin_fstest` declaration is `auto rw`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`. Local helper surface: `_cleanup`. Requirement gates: `_require_test`, `_require_fs_space $TDIR 3200000`. Important external or harness commands observed in the full source include primarily fstests shell helpers. Notable scenario variables include `TDIR="${TEST_DIR}/t_holes"`, `NFILES="10"`, `EXTSIZE="256k"`.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow drives file layout with xfs_io operations such as fallocate, punch, zero, bmap, fiemap, fsync, direct I/O, or mmap. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
intentional metadata corruption can leave the scratch device unmountable until repair or cleanup completes; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/229.out`; stable progress labels including `echo "generating ${NFILES} files"`, `echo "comparing files"`, `echo "got ${errcnt} errors"`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 71 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/229 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/230 -->
# sources/test-tools/xfstests/tests/xfs/230

## Purpose
`sources/test-tools/xfstests/tests/xfs/230` is a reflink and copy-on-write regression. Ensuring that copy on write in buffered mode works when the CoW range originally covers multiple extents, some unwritten, some not. - Set cowextsize hint. - Create a file with the following repeating sequence of blocks: 1. reflinked 2. unwritten 3. hole 4. regular block. The `_begin_fstest` declaration is `auto quick clone punch prealloc`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`, `./common/reflink`. Local helper surface: no local helpers beyond the main shell flow. Requirement gates: `_require_scratch_reflink`, `_require_scratch_delalloc`, `_require_xfs_io_command "falloc"`, `_require_xfs_io_command "cowextsize"`, `_require_xfs_io_command "fpunch"`, `_require_cp_reflink`, `_require_odirect`, `_require_congruent_file_oplen $SCRATCH_MNT $blksz`. Important external or harness commands observed in the full source include `mount`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; drives file layout with xfs_io operations such as fallocate, punch, zero, bmap, fiemap, fsync, direct I/O, or mmap; creates shared extents and forces copy-on-write conversions. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, diagnostic `$seqres.full` logs, shared extent/refcount and CoW fork metadata. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
extent-count and bmap/fiemap assertions can change with allocator behavior while data correctness remains stable; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/230.out`; stable progress labels including `echo "Format and mount"`, `echo "Create the original files"`, `echo "Compare files"`, `echo "directio CoW across the transition"`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 82 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/230 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/231 -->
# sources/test-tools/xfstests/tests/xfs/231

## Purpose
`sources/test-tools/xfstests/tests/xfs/231` is a reflink and copy-on-write regression. Test recovery of unused CoW reservations: - Create two reflinked files.  Set extsz hint on second file. - Dirty a single byte on a number of CoW reservations in the second file. - Fsync to flush out the dirty pages. - Wait for the reclaim to run. - Write more and see how bad fragmentation is. Override the default cleanup function. The `_begin_fstest` declaration is `auto quick clone fiemap prealloc`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`, `./common/reflink`. Local helper surface: `_cleanup`. Requirement gates: `_require_scratch_reflink`, `_require_cp_reflink`, `_require_xfs_io_command "cowextsize"`, `_require_xfs_io_command "falloc"`, `_require_xfs_io_command "fiemap"`, `_require_congruent_file_oplen $SCRATCH_MNT $blksz`, `_require_fs_space $SCRATCH_MNT $((filesize / 1024 * 3 * 5 / 4))`. Important external or harness commands observed in the full source include `mount`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; drives file layout with xfs_io operations such as fallocate, punch, zero, bmap, fiemap, fsync, direct I/O, or mmap; creates shared extents and forces copy-on-write conversions. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, temporary `$tmp.*` files, diagnostic `$seqres.full` logs, shared extent/refcount and CoW fork metadata. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
extent-count and bmap/fiemap assertions can change with allocator behavior while data correctness remains stable; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/231.out`; stable progress labels including `echo "Format and mount"`, `echo "Create the original files"`, `echo "Compare files"`, `echo "CoW and leave leftovers"`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 109 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/231 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/232 -->
# sources/test-tools/xfstests/tests/xfs/232

## Purpose
`sources/test-tools/xfstests/tests/xfs/232` is a reflink and copy-on-write regression. Test non-recovery of unused CoW reservations for dirty files: - Create two reflinked files.  Set extsz hint on second file. - Dirty a single byte on a number of CoW reservations in the second file. - Fsync to flush out the dirty pages. - Dirty a single byte anywhere in the second file. - Wait for the reclaim to run. - Write more and see how bad fragmentation is. unreliable_in_parallel: external sync operations affect what happens while. The `_begin_fstest` declaration is `auto quick clone fiemap prealloc unreliable_in_parallel`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`, `./common/reflink`. Local helper surface: `_cleanup`. Requirement gates: `_require_scratch`, `_require_scratch_delalloc`, `_require_xfs_io_command "cowextsize"`, `_require_scratch_reflink`, `_require_cp_reflink`, `_require_xfs_io_command "falloc"`, `_require_xfs_io_command "fiemap"`, `_require_congruent_file_oplen $SCRATCH_MNT $blksz`, `_require_fs_space $SCRATCH_MNT $((filesize / 1024 * 3 * 5 / 4))`. Important external or harness commands observed in the full source include `mount`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; drives file layout with xfs_io operations such as fallocate, punch, zero, bmap, fiemap, fsync, direct I/O, or mmap; creates shared extents and forces copy-on-write conversions. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, temporary `$tmp.*` files, diagnostic `$seqres.full` logs, shared extent/refcount and CoW fork metadata. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
extent-count and bmap/fiemap assertions can change with allocator behavior while data correctness remains stable; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/232.out`; stable progress labels including `echo "Format and mount"`, `echo "Create the original files"`, `echo "Compare files"`, `echo "CoW and leave leftovers"`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 117 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/232 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/233 -->
# sources/test-tools/xfstests/tests/xfs/233

## Purpose
`sources/test-tools/xfstests/tests/xfs/233` is a online grow/shrink regression. Tests xfs_growfs starting with a really small file system. The `_begin_fstest` declaration is `auto quick rmap growfs`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`. Local helper surface: no local helpers beyond the main shell flow. Requirement gates: `_require_no_large_scratch_dev`. Important external or harness commands observed in the full source include `mount`, `xfs_growfs`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, diagnostic `$seqres.full` logs. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
online grow/shrink cases depend on free-space geometry and can skip or fail if ENOSPC behavior changes; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/233.out`; stable progress labels including `echo "Format and mount"`, `echo "Create the original files"`, `echo "Grow fs"`, `echo "Create more copies"`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 41 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/233 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/234 -->
# sources/test-tools/xfstests/tests/xfs/234

## Purpose
`sources/test-tools/xfstests/tests/xfs/234` is a xfsdump/xfsrestore coverage. Ensure that we can create enough distinct rmap entries to force creation of a multi-level rmap btree, and that metadump will successfully copy said block. Override the default cleanup function. The `_begin_fstest` declaration is `auto quick rmap punch metadump`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`, `./common/metadump`. Local helper surface: `_cleanup`. Requirement gates: `_require_command "$XFS_MDRESTORE_PROG" "xfs_mdrestore"`, `_require_loop`, `_require_xfs_scratch_rmapbt`, `_require_xfs_io_command "fpunch"`. Important external or harness commands observed in the full source include `xfs_mdrestore`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; drives file layout with xfs_io operations such as fallocate, punch, zero, bmap, fiemap, fsync, direct I/O, or mmap. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, temporary `$tmp.*` files, diagnostic `$seqres.full` logs, loop devices and loop-mounted images. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
loop-device setup and teardown must be exact to avoid leaked mounts or stale devices; dump/restore output is sensitive to inventory state, media splitting, timestamp filtering, and quota special files; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/234.out`; stable progress labels including `echo "Create the original file blocks"`, `echo "Punch every other block"`, `echo "Create metadump file, restore it and check restored fs"`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 56 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/234 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/235 -->
# sources/test-tools/xfstests/tests/xfs/235

## Purpose
`sources/test-tools/xfstests/tests/xfs/235` is a metadata repair/corruption regression. Create and populate an XFS filesystem, corrupt the rmap btree, then see how the kernel and xfs_repair deal with it. The `_begin_fstest` declaration is `auto fuzzers rmap`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`, `./common/attr`. Local helper surface: no local helpers beyond the main shell flow. Requirement gates: `_require_xfs_scratch_rmapbt`. Important external or harness commands observed in the full source include `chattr`, `mount`, `umount`, `xfs_repair`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; runs xfs_repair in checking or fixing mode and treats repair output as part of the oracle; uses xfs_db to inspect or perturb low-level metadata; drives file layout with xfs_io operations such as fallocate, punch, zero, bmap, fiemap, fsync, direct I/O, or mmap. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, diagnostic `$seqres.full` logs, on-disk metadata fields modified for corruption testing. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
intentional metadata corruption can leave the scratch device unmountable until repair or cleanup completes; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/235.out`; stable progress labels including `echo "+ create scratch fs"`, `echo "+ mount fs image"`, `echo "+ make some files"`, `echo "+ check fs"`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 76 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/235 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/236 -->
# sources/test-tools/xfstests/tests/xfs/236

## Purpose
`sources/test-tools/xfstests/tests/xfs/236` is a reflink and copy-on-write regression. Ensure that we can create enough distinct rmapbt entries to force creation of a multi-level rmap btree.  Delete and recreate a few times to exercise the rmap btree grow/shrink functions. Override the default cleanup function. The `_begin_fstest` declaration is `auto rmap punch`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`. Local helper surface: `_cleanup`. Requirement gates: `_require_xfs_scratch_rmapbt`, `_require_xfs_io_command "fpunch"`. Important external or harness commands observed in the full source include `umount`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; drives file layout with xfs_io operations such as fallocate, punch, zero, bmap, fiemap, fsync, direct I/O, or mmap. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, temporary `$tmp.*` files, diagnostic `$seqres.full` logs, shared extent/refcount and CoW fork metadata. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
intentional metadata corruption can leave the scratch device unmountable until repair or cleanup completes; extent-count and bmap/fiemap assertions can change with allocator behavior while data correctness remains stable; online grow/shrink cases depend on free-space geometry and can skip or fail if ENOSPC behavior changes; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/236.out`; stable progress labels including `echo "Create the original file blocks"`, `echo "$i: Reflink every other block"`, `echo "$i: Delete both files"`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 62 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/236 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/237 -->
# sources/test-tools/xfstests/tests/xfs/237

## Purpose
`sources/test-tools/xfstests/tests/xfs/237` is a reflink and copy-on-write regression. Test AIO DIO CoW behavior when the write temporarily fails. unreliable_in_parallel: external drop caches can co-incide with the error table being loaded, so the test being run fails with EIO trying to load the inode from disk instead of whatever operation it is supposed to fail on when the inode is already cached in memory. Override the default cleanup function. The `_begin_fstest` declaration is `auto quick clone eio unreliable_in_parallel`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`, `./common/reflink`, `./common/dmerror`. Local helper surface: `_cleanup`. Requirement gates: `_require_scratch_reflink`, `_require_cp_reflink`, `_require_dm_target error`, `_require_xfs_io_command "cowextsize"`, `_require_aiodio "aiocp"`, `_require_fs_space $SCRATCH_MNT $((filesize / 1024 * 3 * 5 / 4))`, `_require_congruent_file_oplen $SCRATCH_MNT $blksz`. Important external or harness commands observed in the full source include `mount`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; drives file layout with xfs_io operations such as fallocate, punch, zero, bmap, fiemap, fsync, direct I/O, or mmap; creates shared extents and forces copy-on-write conversions. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, temporary `$tmp.*` files, diagnostic `$seqres.full` logs, shared extent/refcount and CoW fork metadata. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
extent-count and bmap/fiemap assertions can change with allocator behavior while data correctness remains stable; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/237.out`; stable progress labels including `echo "Format and mount"`, `echo "Create the original files"`, `echo "Compare files"`, `echo "CoW and unmount"`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 88 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/237 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/238 -->
# sources/test-tools/xfstests/tests/xfs/238

## Purpose
`sources/test-tools/xfstests/tests/xfs/238` is a XFS fstests regression. Check stale handles pointing to unlinked files are detected correctly. The `_begin_fstest` declaration is `auto quick metadata ioctl`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`. Local helper surface: no local helpers beyond the main shell flow. Requirement gates: `_require_scratch`. Important external or harness commands observed in the full source include primarily fstests shell helpers. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
golden output can drift when xfsprogs diagnostics, filters, or common fstests helpers change; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/238.out`; stable progress labels including `echo "Silence is golden"`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 25 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/238 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/239 -->
# sources/test-tools/xfstests/tests/xfs/239

## Purpose
`sources/test-tools/xfstests/tests/xfs/239` is a reflink and copy-on-write regression. Test AIO DIO CoW behavior. Override the default cleanup function. The `_begin_fstest` declaration is `auto quick clone`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`, `./common/reflink`. Local helper surface: `_cleanup`. Requirement gates: `_require_scratch_reflink`, `_require_cp_reflink`, `_require_xfs_io_command "cowextsize"`, `_require_aiodio "aiocp"`, `_require_congruent_file_oplen $SCRATCH_MNT $blksz`, `_require_fs_space $SCRATCH_MNT $((filesize / 1024 * 3 * 5 / 4))`. Important external or harness commands observed in the full source include `mount`, `umount`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; drives file layout with xfs_io operations such as fallocate, punch, zero, bmap, fiemap, fsync, direct I/O, or mmap; creates shared extents and forces copy-on-write conversions. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, temporary `$tmp.*` files, diagnostic `$seqres.full` logs, shared extent/refcount and CoW fork metadata. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
extent-count and bmap/fiemap assertions can change with allocator behavior while data correctness remains stable; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/239.out`; stable progress labels including `echo "Format and mount"`, `echo "Create the original files"`, `echo "Compare files"`, `echo "CoW and unmount"`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 74 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/239 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/240 -->
# sources/test-tools/xfstests/tests/xfs/240

## Purpose
`sources/test-tools/xfstests/tests/xfs/240` is a reflink and copy-on-write regression. Test AIO CoW behavior when the write temporarily fails. Override the default cleanup function. If the filesystem supports delalloc, then the fdatasync will report an IO error.  If the write goes directly to disk, then aiocp will return nonzero. The `_begin_fstest` declaration is `auto quick clone eio`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`, `./common/reflink`, `./common/dmerror`. Local helper surface: `_cleanup`. Requirement gates: `_require_scratch_reflink`, `_require_cp_reflink`, `_require_dm_target error`, `_require_xfs_io_command "cowextsize"`, `_require_aiodio "aiocp"`, `_require_congruent_file_oplen $SCRATCH_MNT $blksz`, `_require_fs_space $SCRATCH_MNT $((filesize / 1024 * 3 * 5 / 4))`. Important external or harness commands observed in the full source include `mount`. Notable scenario variables include `AIO_TEST="$here/src/aio-dio-regress/aiocp"`.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; drives file layout with xfs_io operations such as fallocate, punch, zero, bmap, fiemap, fsync, direct I/O, or mmap; creates shared extents and forces copy-on-write conversions. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, temporary `$tmp.*` files, diagnostic `$seqres.full` logs, shared extent/refcount and CoW fork metadata. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
extent-count and bmap/fiemap assertions can change with allocator behavior while data correctness remains stable; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/240.out`; stable progress labels including `echo "Format and mount"`, `echo "Create the original files"`, `echo "Compare files"`, `echo "CoW and unmount"`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 93 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/240 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/241 -->
# sources/test-tools/xfstests/tests/xfs/241

## Purpose
`sources/test-tools/xfstests/tests/xfs/241` is a reflink and copy-on-write regression. Test AIO CoW behavior. Override the default cleanup function. The `_begin_fstest` declaration is `auto quick clone`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`, `./common/reflink`. Local helper surface: `_cleanup`. Requirement gates: `_require_scratch_reflink`, `_require_cp_reflink`, `_require_xfs_io_command "cowextsize"`, `_require_aiodio "aiocp"`, `_require_congruent_file_oplen $SCRATCH_MNT $blksz`, `_require_fs_space $SCRATCH_MNT $((filesize / 1024 * 3 * 5 / 4))`. Important external or harness commands observed in the full source include `mount`, `umount`. Notable scenario variables include `AIO_TEST="$here/src/aio-dio-regress/aiocp"`.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; drives file layout with xfs_io operations such as fallocate, punch, zero, bmap, fiemap, fsync, direct I/O, or mmap; creates shared extents and forces copy-on-write conversions. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, temporary `$tmp.*` files, diagnostic `$seqres.full` logs, shared extent/refcount and CoW fork metadata. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
extent-count and bmap/fiemap assertions can change with allocator behavior while data correctness remains stable; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/241.out`; stable progress labels including `echo "Format and mount"`, `echo "Create the original files"`, `echo "Compare files"`, `echo "CoW and unmount"`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 74 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/241 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/242 -->
# sources/test-tools/xfstests/tests/xfs/242

## Purpose
`sources/test-tools/xfstests/tests/xfs/242` is a preallocation/unwritten extent regression. Test XFS_IOC_ZERO_RANGE. The `_begin_fstest` declaration is `auto quick prealloc zero`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`, `./common/punch`. Local helper surface: no local helpers beyond the main shell flow. Requirement gates: `_require_test`, `_require_xfs_io_command "falloc"`, `_require_xfs_io_command "zero"`. Important external or harness commands observed in the full source include primarily fstests shell helpers. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow drives file layout with xfs_io operations such as fallocate, punch, zero, bmap, fiemap, fsync, direct I/O, or mmap. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
golden output can drift when xfsprogs diagnostics, filters, or common fstests helpers change; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/242.out`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 25 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/242 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/243 -->
# sources/test-tools/xfstests/tests/xfs/243

## Purpose
`sources/test-tools/xfstests/tests/xfs/243` is a reflink and copy-on-write regression. Ensuring that copy on write in buffered mode works when the CoW range originally covers multiple extents, some unwritten, some not. - Set cowextsize hint. - Create a file with the following repeating sequence of blocks: 1. reflinked 2. unwritten 3. hole 4. regular block. The `_begin_fstest` declaration is `auto quick clone punch prealloc unreliable_in_parallel`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`, `./common/reflink`. Local helper surface: no local helpers beyond the main shell flow. Requirement gates: `_require_xfs_debug`, `_require_scratch_reflink`, `_require_scratch_delalloc`, `_require_xfs_io_command "falloc"`, `_require_xfs_io_command "cowextsize"`, `_require_xfs_io_command "fpunch"`, `_require_xfs_io_command "bmap" "-c"`, `_require_cp_reflink`. Important external or harness commands observed in the full source include `mount`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; drives file layout with xfs_io operations such as fallocate, punch, zero, bmap, fiemap, fsync, direct I/O, or mmap; creates shared extents and forces copy-on-write conversions. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, diagnostic `$seqres.full` logs, shared extent/refcount and CoW fork metadata. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
extent-count and bmap/fiemap assertions can change with allocator behavior while data correctness remains stable; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/243.out`; stable progress labels including `echo "Format and mount"`, `echo "Create the original files"`, `echo "Compare files"`, `echo "Dump extents"`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 140 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/243 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/244 -->
# sources/test-tools/xfstests/tests/xfs/244

## Purpose
`sources/test-tools/xfstests/tests/xfs/244` is a quota behavior regression. test to verify that proper project quota id is correctly set Override the default cleanup function. make fs with no projid32bit make sure project quota is supported Do testing on filesystem with projid32bit feature disabled below 16bit value 32bit value, should fail over 32bit value, should fail. The `_begin_fstest` declaration is `auto quota quick`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`, `./common/quota`. Local helper surface: `_cleanup`. Requirement gates: `_require_xfs_quota`, `_require_scratch`, `_require_projid32bit`, `_require_projid16bit`, `_require_prjquota ${SCRATCH_DEV}`. Important external or harness commands observed in the full source include `quota`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; drives file layout with xfs_io operations such as fallocate, punch, zero, bmap, fiemap, fsync, direct I/O, or mmap; configures or queries user/group/project quota state. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, temporary `$tmp.*` files, diagnostic `$seqres.full` logs, quota accounting and grace-period metadata. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
quota output and timer calculations are sensitive to quota-tools versions, current time, and 32-bit time support; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/244.out`; stable progress labels including `echo "Silence is golden"`, `echo "FAIL: projid32bit disabled: returned projid value ($projid)"`, `echo "      doesn't match set one (projid = 3422)"`, `echo "FAIL: projid32bit disabled: setting 32bit projid succeeded"`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 114 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/244 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/245 -->
# sources/test-tools/xfstests/tests/xfs/245

## Purpose
`sources/test-tools/xfstests/tests/xfs/245` is a reflink and copy-on-write regression. Make sure that reflink deals with extents going beyond EOF. - fallocate 256k in file1 - pwrite 252-257k to cause it to speculatively prealloc file1 - reflink file1 to file2 - compare file[12]. The `_begin_fstest` declaration is `auto quick clone prealloc`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`, `./common/reflink`. Local helper surface: no local helpers beyond the main shell flow. Requirement gates: `_require_xfs_debug`, `_require_scratch_reflink`, `_require_xfs_io_command "falloc"`, `_require_xfs_io_command "bmap" "-c"`, `_require_cp_reflink`. Important external or harness commands observed in the full source include `mount`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; drives file layout with xfs_io operations such as fallocate, punch, zero, bmap, fiemap, fsync, direct I/O, or mmap; creates shared extents and forces copy-on-write conversions. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, diagnostic `$seqres.full` logs, shared extent/refcount and CoW fork metadata. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
extent-count and bmap/fiemap assertions can change with allocator behavior while data correctness remains stable; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/245.out`; stable progress labels including `echo "Format and mount"`, `echo "Create the original files"`, `echo "Compare files"`, `echo "Unwritten data extents"`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 65 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/245 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/246 -->
# sources/test-tools/xfstests/tests/xfs/246

## Purpose
`sources/test-tools/xfstests/tests/xfs/246` is a reflink and copy-on-write regression. Create an empty file and try to query the (nonexistant) CoW fork. The `_begin_fstest` declaration is `auto quick clone`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`. Local helper surface: no local helpers beyond the main shell flow. Requirement gates: `_require_xfs_debug`, `_require_xfs_io_command "bmap" "-c"`, `_require_scratch`. Important external or harness commands observed in the full source include `mount`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; drives file layout with xfs_io operations such as fallocate, punch, zero, bmap, fiemap, fsync, direct I/O, or mmap; creates shared extents and forces copy-on-write conversions. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, diagnostic `$seqres.full` logs, shared extent/refcount and CoW fork metadata. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
extent-count and bmap/fiemap assertions can change with allocator behavior while data correctness remains stable; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/246.out`; stable progress labels including `echo "Format and mount"`, `echo "Create the original files"`, `echo "Dump extents after sync"`, `echo "Hole CoW extents:"`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 36 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/246 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/247 -->
# sources/test-tools/xfstests/tests/xfs/247

## Purpose
`sources/test-tools/xfstests/tests/xfs/247` is a reflink and copy-on-write regression. Mount a reflink/rmap filesystem ro (so the per-AG reservation isn't created) and unmount, to ensure that we free correctly. The `_begin_fstest` declaration is `auto quick clone`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`, `./common/reflink`. Local helper surface: no local helpers beyond the main shell flow. Requirement gates: `_require_scratch_reflink`. Important external or harness commands observed in the full source include `mount`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; creates shared extents and forces copy-on-write conversions. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, diagnostic `$seqres.full` logs, shared extent/refcount and CoW fork metadata. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
extent-count and bmap/fiemap assertions can change with allocator behavior while data correctness remains stable; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/247.out`; stable progress labels including `echo "Format and mount"`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 25 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/247 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/248 -->
# sources/test-tools/xfstests/tests/xfs/248

## Purpose
`sources/test-tools/xfstests/tests/xfs/248` is a reflink and copy-on-write regression. Ensuring that copy on write in buffered mode to the source file when the CoW range covers regular unshared and regular shared blocks. - Set cowextsz. - Create two files. - Reflink the odd blocks of the first file into the second file. - CoW the first file across the halfway mark, starting with the regular extent. - Check that the files are now different where we say they're different. The `_begin_fstest` declaration is `auto quick clone prealloc`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`, `./common/reflink`. Local helper surface: no local helpers beyond the main shell flow. Requirement gates: `_require_scratch_reflink`, `_require_xfs_io_command "falloc"`, `_require_xfs_io_command "cowextsize"`, `_require_congruent_file_oplen $SCRATCH_MNT $blksz`. Important external or harness commands observed in the full source include `mount`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; drives file layout with xfs_io operations such as fallocate, punch, zero, bmap, fiemap, fsync, direct I/O, or mmap; creates shared extents and forces copy-on-write conversions. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, diagnostic `$seqres.full` logs, shared extent/refcount and CoW fork metadata. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
extent-count and bmap/fiemap assertions can change with allocator behavior while data correctness remains stable; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/248.out`; stable progress labels including `echo "Format and mount"`, `echo "Create the original files"`, `echo "Compare files"`, `echo "CoW across the transition"`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 62 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/248 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/249 -->
# sources/test-tools/xfstests/tests/xfs/249

## Purpose
`sources/test-tools/xfstests/tests/xfs/249` is a reflink and copy-on-write regression. Ensuring that copy on write in directio mode to the source file when the CoW range covers regular unshared and regular shared blocks. - Set cowextsz. - Create two files. - Reflink the odd blocks of the first file into the second file. - dio CoW the first file across the halfway mark, starting with the regular extent. - Check that the files are now different where we say they're different. The `_begin_fstest` declaration is `auto quick clone prealloc`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`, `./common/reflink`. Local helper surface: no local helpers beyond the main shell flow. Requirement gates: `_require_scratch_reflink`, `_require_xfs_io_command "falloc"`, `_require_xfs_io_command "cowextsize"`, `_require_odirect`, `_require_congruent_file_oplen $SCRATCH_MNT $blksz`. Important external or harness commands observed in the full source include `mount`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; drives file layout with xfs_io operations such as fallocate, punch, zero, bmap, fiemap, fsync, direct I/O, or mmap; creates shared extents and forces copy-on-write conversions. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, diagnostic `$seqres.full` logs, shared extent/refcount and CoW fork metadata. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
extent-count and bmap/fiemap assertions can change with allocator behavior while data correctness remains stable; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/249.out`; stable progress labels including `echo "Format and mount"`, `echo "Create the original files"`, `echo "Compare files"`, `echo "CoW across the transition"`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 63 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/249 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/250 -->
# sources/test-tools/xfstests/tests/xfs/250

## Purpose
`sources/test-tools/xfstests/tests/xfs/250` is a preallocation/unwritten extent regression. Bmap btree corruption regression test Override the default cleanup function. The `_begin_fstest` declaration is `auto quick rw prealloc metadata`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`. Local helper surface: `_cleanup`, `_filter_io`, `_test_loop`. Requirement gates: `_require_test`, `_require_loop`, `_require_xfs_io_command "falloc"`. Important external or harness commands observed in the full source include `mkfs`, `mount`. Notable scenario variables include `LOOP_IMG=$TEST_DIR/$seq.fs`, `LOOP_MNT=$TEST_DIR/$seq.mnt`.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; drives file layout with xfs_io operations such as fallocate, punch, zero, bmap, fiemap, fsync, direct I/O, or mmap. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, temporary `$tmp.*` files, loop devices and loop-mounted images. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
intentional metadata corruption can leave the scratch device unmountable until repair or cleanup completes; loop-device setup and teardown must be exact to avoid leaked mounts or stale devices; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/250.out`; stable progress labels including `echo "*** create loop mount point"`, `echo "*** mkfs loop file (size=$size)"`, `echo "*** mount loop filesystem"`, `echo "*** preallocate large file"`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 77 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/250 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/251 -->
# sources/test-tools/xfstests/tests/xfs/251

## Purpose
`sources/test-tools/xfstests/tests/xfs/251` is a reflink and copy-on-write regression. Ensuring that copy on write in buffered mode to the source file when the CoW range covers unwritten and regular shared blocks. - Set cowextsz. - Create two files. - fallocate the first file. - Write the odd blocks of the first file. - Reflink the odd blocks of the first file into the second file. - CoW the first file across the halfway mark, starting with the. The `_begin_fstest` declaration is `auto quick clone prealloc`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`, `./common/reflink`. Local helper surface: no local helpers beyond the main shell flow. Requirement gates: `_require_scratch_reflink`, `_require_xfs_io_command "falloc"`, `_require_xfs_io_command "cowextsize"`, `_require_congruent_file_oplen $SCRATCH_MNT $blksz`. Important external or harness commands observed in the full source include `mount`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; drives file layout with xfs_io operations such as fallocate, punch, zero, bmap, fiemap, fsync, direct I/O, or mmap; creates shared extents and forces copy-on-write conversions. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, diagnostic `$seqres.full` logs, shared extent/refcount and CoW fork metadata. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
extent-count and bmap/fiemap assertions can change with allocator behavior while data correctness remains stable; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/251.out`; stable progress labels including `echo "Format and mount"`, `echo "Create the original files"`, `echo "Compare files"`, `echo "CoW across the transition"`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 64 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/251 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/252 -->
# sources/test-tools/xfstests/tests/xfs/252

## Purpose
`sources/test-tools/xfstests/tests/xfs/252` is a preallocation/unwritten extent regression. Test fallocate hole punching Standard punch hole tests Delayed allocation punch hole tests Multi hole punch tests Delayed allocation multi punch hole tests. The `_begin_fstest` declaration is `auto quick prealloc punch fiemap`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`, `./common/punch`. Local helper surface: no local helpers beyond the main shell flow. Requirement gates: `_require_test`, `_require_xfs_io_command "falloc"`, `_require_xfs_io_command "fpunch"`, `_require_xfs_io_command "fiemap"`. Important external or harness commands observed in the full source include primarily fstests shell helpers. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow drives file layout with xfs_io operations such as fallocate, punch, zero, bmap, fiemap, fsync, direct I/O, or mmap. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
golden output can drift when xfsprogs diagnostics, filters, or common fstests helpers change; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/252.out`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 35 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/252 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/253 -->
# sources/test-tools/xfstests/tests/xfs/253

## Purpose
`sources/test-tools/xfstests/tests/xfs/253` is a xfsdump/xfsrestore coverage. Test xfs_db metadump functionality. This test was created to verify fixes for problems where metadump would never complete due to an inability to find a suitable obfuscated name to use.  It also verifies a few other things, including ensuring the "lost+found" directory and orphaned files in it do not get obfuscated. This test also creates a number of files that are effectively duplicates of existing files; this can happen in certain rare. The `_begin_fstest` declaration is `auto quick metadump`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`, `./common/metadump`. Local helper surface: `_cleanup`, `extra_test`. Requirement gates: `_require_command "$XFS_MDRESTORE_PROG" "xfs_mdrestore"`, `_require_test`, `_require_scratch`. Important external or harness commands observed in the full source include `mount`, `xfs_db`, `xfs_mdrestore`, `xfs_metadump`. Notable scenario variables include `OUTPUT_DIR="${SCRATCH_MNT}/test_${seq}"`, `ORPHANAGE="lost+found"`, `TEMP_ORPHAN="${ORPHANAGE}/__orphan__"`, `NON_ORPHAN="${ORPHANAGE}/__should_be_obfuscated__"`, `INUM=$(ls -i "${TEMP_ORPHAN}" | awk '{ print $1; }')`.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; uses xfs_db to inspect or perturb low-level metadata. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, temporary `$tmp.*` files, diagnostic `$seqres.full` logs, on-disk metadata fields modified for corruption testing. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
intentional metadata corruption can leave the scratch device unmountable until repair or cleanup completes; dump/restore output is sensitive to inventory state, media splitting, timestamp filtering, and quota special files; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/253.out`; stable progress labels including `echo "Metadump v1" >> $seqres.full`, `echo "Disciplyne of silence is goed."`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 170 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/253 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/254 -->
# sources/test-tools/xfstests/tests/xfs/254

## Purpose
`sources/test-tools/xfstests/tests/xfs/254` is a reflink and copy-on-write regression. Ensuring that copy on write in directio mode to the source file when the CoW range covers unwritten and regular shared blocks. - Set cowextsz. - Create two files. - fallocate the first file. - Write the odd blocks of the first file. - Reflink the odd blocks of the first file into the second file. - DIO CoW the first file across the halfway mark, starting with the. The `_begin_fstest` declaration is `auto quick clone prealloc`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`, `./common/reflink`. Local helper surface: no local helpers beyond the main shell flow. Requirement gates: `_require_scratch_reflink`, `_require_xfs_io_command "falloc"`, `_require_xfs_io_command "cowextsize"`, `_require_odirect`, `_require_congruent_file_oplen $SCRATCH_MNT $blksz`. Important external or harness commands observed in the full source include `mount`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; drives file layout with xfs_io operations such as fallocate, punch, zero, bmap, fiemap, fsync, direct I/O, or mmap; creates shared extents and forces copy-on-write conversions. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, diagnostic `$seqres.full` logs, shared extent/refcount and CoW fork metadata. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
extent-count and bmap/fiemap assertions can change with allocator behavior while data correctness remains stable; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/254.out`; stable progress labels including `echo "Format and mount"`, `echo "Create the original files"`, `echo "Compare files"`, `echo "CoW across the transition"`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 65 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/254 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/255 -->
# sources/test-tools/xfstests/tests/xfs/255

## Purpose
`sources/test-tools/xfstests/tests/xfs/255` is a reflink and copy-on-write regression. Ensuring that copy on write in buffered mode to the source file when the CoW range covers holes and regular shared blocks. - Set cowextsz. - Create two files. - Truncate the first file. - Write the odd blocks of the first file. - Reflink the odd blocks of the first file into the second file. - CoW the first file across the halfway mark, starting with the. The `_begin_fstest` declaration is `auto quick clone prealloc`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`, `./common/reflink`. Local helper surface: no local helpers beyond the main shell flow. Requirement gates: `_require_scratch_reflink`, `_require_xfs_io_command "falloc"`, `_require_xfs_io_command "cowextsize"`, `_require_congruent_file_oplen $SCRATCH_MNT $blksz`. Important external or harness commands observed in the full source include `mount`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; drives file layout with xfs_io operations such as fallocate, punch, zero, bmap, fiemap, fsync, direct I/O, or mmap; creates shared extents and forces copy-on-write conversions. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, diagnostic `$seqres.full` logs, shared extent/refcount and CoW fork metadata. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
extent-count and bmap/fiemap assertions can change with allocator behavior while data correctness remains stable; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/255.out`; stable progress labels including `echo "Format and mount"`, `echo "Create the original files"`, `echo "Compare files"`, `echo "CoW across the transition"`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 64 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/255 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/256 -->
# sources/test-tools/xfstests/tests/xfs/256

## Purpose
`sources/test-tools/xfstests/tests/xfs/256` is a reflink and copy-on-write regression. Ensuring that copy on write in directio mode to the source file when the CoW range covers holes and regular shared blocks. - Set cowextsz. - Create two files. - Truncate the first file. - Write the odd blocks of the first file. - Reflink the odd blocks of the first file into the second file. - DIO CoW the first file across the halfway mark, starting with the. The `_begin_fstest` declaration is `auto quick clone prealloc`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`, `./common/reflink`. Local helper surface: no local helpers beyond the main shell flow. Requirement gates: `_require_scratch_reflink`, `_require_xfs_io_command "falloc"`, `_require_xfs_io_command "cowextsize"`, `_require_odirect`, `_require_congruent_file_oplen $SCRATCH_MNT $blksz`. Important external or harness commands observed in the full source include `mount`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; drives file layout with xfs_io operations such as fallocate, punch, zero, bmap, fiemap, fsync, direct I/O, or mmap; creates shared extents and forces copy-on-write conversions. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, diagnostic `$seqres.full` logs, shared extent/refcount and CoW fork metadata. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
extent-count and bmap/fiemap assertions can change with allocator behavior while data correctness remains stable; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/256.out`; stable progress labels including `echo "Format and mount"`, `echo "Create the original files"`, `echo "Compare files"`, `echo "CoW across the transition"`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 65 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/256 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/257 -->
# sources/test-tools/xfstests/tests/xfs/257

## Purpose
`sources/test-tools/xfstests/tests/xfs/257` is a reflink and copy-on-write regression. Ensuring that copy on write in buffered mode to the source file when the CoW range covers delalloc blocks and regular shared blocks. - Set cowextsz. - Create two files. - Truncate the first file. - Write the odd blocks of the first file. - Reflink the odd blocks of the first file into the second file. - Write the even blocks of the first file. The `_begin_fstest` declaration is `auto quick clone prealloc`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`, `./common/reflink`. Local helper surface: no local helpers beyond the main shell flow. Requirement gates: `_require_scratch_reflink`, `_require_scratch_delalloc`, `_require_xfs_io_command "falloc"`, `_require_xfs_io_command "cowextsize"`, `_require_congruent_file_oplen $SCRATCH_MNT $blksz`. Important external or harness commands observed in the full source include `mount`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; drives file layout with xfs_io operations such as fallocate, punch, zero, bmap, fiemap, fsync, direct I/O, or mmap; creates shared extents and forces copy-on-write conversions. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, diagnostic `$seqres.full` logs, shared extent/refcount and CoW fork metadata. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
extent-count and bmap/fiemap assertions can change with allocator behavior while data correctness remains stable; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/257.out`; stable progress labels including `echo "Format and mount"`, `echo "Create the original files"`, `echo "Compare files"`, `echo "CoW across the transition"`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 67 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/257 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/258 -->
# sources/test-tools/xfstests/tests/xfs/258

## Purpose
`sources/test-tools/xfstests/tests/xfs/258` is a reflink and copy-on-write regression. Ensuring that copy on write in directio mode to the source file when the CoW range covers delalloc blocks and regular shared blocks. - Set cowextsz. - Create two files. - Truncate the first file. - Write the odd blocks of the first file. - Reflink the odd blocks of the first file into the second file. - Write the even blocks of the first file. The `_begin_fstest` declaration is `auto quick clone prealloc`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`, `./common/reflink`. Local helper surface: no local helpers beyond the main shell flow. Requirement gates: `_require_scratch_reflink`, `_require_scratch_delalloc`, `_require_xfs_io_command "falloc"`, `_require_xfs_io_command "cowextsize"`, `_require_odirect`, `_require_congruent_file_oplen $SCRATCH_MNT $blksz`. Important external or harness commands observed in the full source include `mount`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; drives file layout with xfs_io operations such as fallocate, punch, zero, bmap, fiemap, fsync, direct I/O, or mmap; creates shared extents and forces copy-on-write conversions. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, diagnostic `$seqres.full` logs, shared extent/refcount and CoW fork metadata. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
extent-count and bmap/fiemap assertions can change with allocator behavior while data correctness remains stable; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/258.out`; stable progress labels including `echo "Format and mount"`, `echo "Create the original files"`, `echo "Compare files"`, `echo "CoW across the transition"`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 68 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/258 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/259 -->
# sources/test-tools/xfstests/tests/xfs/259

## Purpose
`sources/test-tools/xfstests/tests/xfs/259` is a XFS fstests regression. Test fs creation on 4 TB minus few bytes partition Override the default cleanup function. Test various sizes slightly less than 4 TB. Need to handle different minimum block sizes for CRC enabled filesystems, but use a small log so we don't write lots of zeros unnecessarily. The `_begin_fstest` declaration is `auto quick`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`. Local helper surface: `_cleanup`. Requirement gates: `_require_test`, `_require_loop`, `_require_math`. Important external or harness commands observed in the full source include `mkfs`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, temporary `$tmp.*` files, diagnostic `$seqres.full` logs, loop devices and loop-mounted images. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
loop-device setup and teardown must be exact to avoid leaked mounts or stale devices; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/259.out`; stable progress labels including `echo "Trying to make (4TB - ${del}B) long xfs, block size $bs" | \`, `echo "mkfs failed!"`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 54 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/259 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/260 -->
# sources/test-tools/xfstests/tests/xfs/260

## Purpose
`sources/test-tools/xfstests/tests/xfs/260` is a mkfs option/geometry regression. Verify that an attempt to create a too-small device with stripe geometry, is handled gracefully instead of hitting an assert in align_ag_geometry() This test verifies the problem fixed in xfsprogs with commit (mkfs.xfs: fix ASSERT on too-small device with stripe geometry) Override the default cleanup function. The `_begin_fstest` declaration is `auto quick mkfs`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`. Local helper surface: `_cleanup`. Requirement gates: `_require_test`. Important external or harness commands observed in the full source include `mkfs`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; drives file layout with xfs_io operations such as fallocate, punch, zero, bmap, fiemap, fsync, direct I/O, or mmap. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, temporary `$tmp.*` files, diagnostic `$seqres.full` logs. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
golden output can drift when xfsprogs diagnostics, filters, or common fstests helpers change; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/260.out`; stable progress labels including `echo 'Silence is golden'`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 41 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/260 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/261 -->
# sources/test-tools/xfstests/tests/xfs/261

## Purpose
`sources/test-tools/xfstests/tests/xfs/261` is a quota behavior regression. This test exercises an issue in libxcmd where a problem with any mount point or project quota directory causes the program to exit complete.  The effect of this is that one cannot operate on any directory, even if the problem directory is completely unrelated to the directory one wants to operate on. Override the default cleanup function. Just use the current mount table as an example mtab file.  Odds are good there's nothing wrong with it. The `_begin_fstest` declaration is `auto quick quota`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`, `./common/quota`. Local helper surface: `_cleanup`, `_setup_my_mtab`, `_perturb_my_mtab`, `_check`. Requirement gates: `_require_quota`, `_require_scratch`. Important external or harness commands observed in the full source include `mount`, `quota`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; configures or queries user/group/project quota state. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, diagnostic `$seqres.full` logs, quota accounting and grace-period metadata. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
quota output and timer calculations are sensitive to quota-tools versions, current time, and 32-bit time support; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/261.out`; stable progress labels including `echo "Silence is golden."`, `echo print | $XFS_QUOTA_PROG -t "${my_mtab}" > /dev/null || exit`, `echo print | $XFS_QUOTA_PROG -t "${my_mtab}" > /dev/null || exit`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 95 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/261 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/262 -->
# sources/test-tools/xfstests/tests/xfs/262

## Purpose
`sources/test-tools/xfstests/tests/xfs/262` is a metadata repair/corruption regression. Copy xfs_scrub to the scratch device, then run xfs_scrub in forced repair mode (which will rebuild the data forks of the running scrub executable and libraries!) to see what happens. xfs_scrub will turn on error injection itself. The `_begin_fstest` declaration is `fuzzers scrub online_repair`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`, `./common/fuzzy`, `./common/inject`. Local helper surface: no local helpers beyond the main shell flow. Requirement gates: `_require_command "$LDD_PROG" ldd`, `_require_scrub`, `_require_scratch`, `_require_xfs_io_error_injection "force_repair"`, `_require_scratch_xfs_scrub`. Important external or harness commands observed in the full source include `xfs_scrub`. Notable scenario variables include `LD_LIBRARY_PATH=$SCRATCH_MNT $LDD_PROG $SCRATCH_MNT/xfs_scrub >> $seqres.full`, `XFS_SCRUB_FORCE_REPAIR=1 LD_LIBRARY_PATH=$SCRATCH_MNT $SCRATCH_MNT/xfs_scrub -dTv $SCRATCH_MNT >> $seqres.full`.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; drives file layout with xfs_io operations such as fallocate, punch, zero, bmap, fiemap, fsync, direct I/O, or mmap. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, diagnostic `$seqres.full` logs, on-disk metadata fields modified for corruption testing. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
intentional metadata corruption can leave the scratch device unmountable until repair or cleanup completes; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/262.out`; stable progress labels including `echo "Format and populate"`, `echo "Force online repairs"`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 44 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/262 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/263 -->
# sources/test-tools/xfstests/tests/xfs/263

## Purpose
`sources/test-tools/xfstests/tests/xfs/263` is a quota behavior regression. test xfs_quota state command Treat 3 options as a bit field, prjquota|grpquota|usrquota Some combinations won't mount on V4 supers (grp + prj). The `_begin_fstest` declaration is `auto quick quota`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`, `./common/quota`. Local helper surface: `filter_quota_state`, `filter_quota_state2`. Requirement gates: `_require_scratch`, `_require_xfs_quota`. Important external or harness commands observed in the full source include `mount`, `quota`, `xfs_quota`. Notable scenario variables include `VAL=$1`, `OPT="rw"`, `OPTIONS=`option_string $I``.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; configures or queries user/group/project quota state. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, diagnostic `$seqres.full` logs, quota accounting and grace-period metadata. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
quota output and timer calculations are sensitive to quota-tools versions, current time, and 32-bit time support; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/263.out`; stable progress labels including `echo $OPT`, `echo "== Options: $OPTIONS =="`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 72 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/263 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/264 -->
# sources/test-tools/xfstests/tests/xfs/264

## Purpose
`sources/test-tools/xfstests/tests/xfs/264` is a XFS fstests regression. Test XFS EIO error handling configuration. Stop XFS from retrying to writeback forever when hit EIO. Override the default cleanup function. Disable fail_at_unmount before test EIO error handling _fail the test if we fail to set $attr to 1, because the test probably will hang in such case and block subsequent tests. start a metadata-intensive workload, but no data allocation operation. Because uncompleted new space allocation I/Os may cause XFS to shutdown. The `_begin_fstest` declaration is `auto quick mount eio`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`, `./common/dmerror`. Local helper surface: `_cleanup`, `do_test`. Requirement gates: `_require_scratch`, `_require_dm_target error`, `_require_fs_sysfs error/fail_at_unmount`, `_require_fs_sysfs error/metadata/EIO/max_retries`, `_require_fs_sysfs error/metadata/EIO/retry_timeout_seconds`. Important external or harness commands observed in the full source include `fsstress`, `mount`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; adds fsstress background load to expose races and ENOSPC boundaries. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, temporary `$tmp.*` files, diagnostic `$seqres.full` logs. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
stress subtests can expose timing-sensitive failures and require enough scratch space; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/264.out`; stable progress labels including `echo -n "error/fail_at_unmount="`, `echo "$attr=$num"`, `echo "=== Test EIO/max_retries ==="`, `echo "=== Test EIO/retry_timeout_seconds ==="`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 99 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/264 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/265 -->
# sources/test-tools/xfstests/tests/xfs/265

## Purpose
`sources/test-tools/xfstests/tests/xfs/265` is a reflink and copy-on-write regression. Ensure that we can create enough distinct reflink entries to force creation of a multi-level refcount btree by reflinking a file a number of times and truncating the copies at successively lower sizes.  Delete and recreate a few times to exercise the refcount btree grow/shrink functions. Override the default cleanup function. The `_begin_fstest` declaration is `auto clone`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`, `./common/reflink`. Local helper surface: `_cleanup`. Requirement gates: `_require_scratch_reflink`, `_require_cp_reflink`. Important external or harness commands observed in the full source include `umount`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; creates shared extents and forces copy-on-write conversions. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, temporary `$tmp.*` files, diagnostic `$seqres.full` logs, shared extent/refcount and CoW fork metadata. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
intentional metadata corruption can leave the scratch device unmountable until repair or cleanup completes; extent-count and bmap/fiemap assertions can change with allocator behavior while data correctness remains stable; online grow/shrink cases depend on free-space geometry and can skip or fail if ENOSPC behavior changes; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/265.out`; stable progress labels including `echo "Create the original file blocks"`, `echo "$i: Reflink a bunch of times"`, `echo "$i: Truncate files"`, `echo "$i: Delete both files"`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 70 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/265 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/266 -->
# sources/test-tools/xfstests/tests/xfs/266

## Purpose
`sources/test-tools/xfstests/tests/xfs/266` is a xfsdump/xfsrestore coverage. Test incremental dumps with -D (skip unchanged dirs) Override the default cleanup function. Add a new file and append a subset of the fill'ed files So we can see if just these get dumped on an incremental Quota files are stored as special files in the dumpdir of the incremental backup.  This throws off the directory/file count reported because xfsrestore includes the dumpdir in the restore summary counts. ensure file/dir timestamps precede dump timestamp. The `_begin_fstest` declaration is `dump ioctl auto quick`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/dump`. Local helper surface: `_cleanup`, `_add_and_append_dumpdir_fill`, `filter_cumulative_quota_updates`. Requirement gates: `_require_scratch`. Important external or harness commands observed in the full source include `quota`, `xfsdump`, `xfsrestore`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; configures or queries user/group/project quota state; creates dump images or tape streams and verifies restore/inventory behavior. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, temporary `$tmp.*` files, diagnostic `$seqres.full` logs, quota accounting and grace-period metadata, dump inventory, dump files, or tape media state. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
quota output and timer calculations are sensitive to quota-tools versions, current time, and 32-bit time support; dump/restore output is sensitive to inventory state, media splitting, timestamp filtering, and quota special files; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/266.out`; stable progress labels including `echo 'New file' >> newfile`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 73 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/266 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/267 -->
# sources/test-tools/xfstests/tests/xfs/267

## Purpose
`sources/test-tools/xfstests/tests/xfs/267` is a xfsdump/xfsrestore coverage. Test xfsdump with a file spanning multiple media files. Override the default cleanup function. create a 40 MiB file with an extended attr. xfsdump writes file data in "extent groups", currently 16 MiB in size. After writing an extent group or finishing a file, xfsdump will start a new media file if it is over the suggested size. With a single 40 MiB file and using a suggested media file size of 12 MiB below, this dump will be contained in 3 media files. The `_begin_fstest` declaration is `dump ioctl tape`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/dump`, `./common/attr`. Local helper surface: `_cleanup`, `_create_files`. Requirement gates: `_require_tape $TAPE_DEV`, `_require_attrs trusted`, `_require_scratch`. Important external or harness commands observed in the full source include `xfsdump`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; creates dump images or tape streams and verifies restore/inventory behavior. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, temporary `$tmp.*` files, diagnostic `$seqres.full` logs, dump inventory, dump files, or tape media state. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
dump/restore output is sensitive to inventory state, media splitting, timestamp filtering, and quota special files; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/267.out`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 61 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/267 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/268 -->
# sources/test-tools/xfstests/tests/xfs/268

## Purpose
`sources/test-tools/xfstests/tests/xfs/268` is a xfsdump/xfsrestore coverage. Test xfsdump with multiple media files where a file ends at the end of the first media file (i.e., no file is split across media files). Override the default cleanup function. create two 12 MiB files with extended attrs. xfsdump writes file data in "extent groups", currently 16 MiB in size. After writing an extent group or finishing a file, xfsdump will start a new media file if it is over the suggested size. A media file size of 8 MiB is used. The `_begin_fstest` declaration is `dump ioctl tape`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/dump`, `./common/attr`. Local helper surface: `_cleanup`, `_create_files`. Requirement gates: `_require_tape $TAPE_DEV`, `_require_attrs trusted user`, `_require_scratch`. Important external or harness commands observed in the full source include `xfsdump`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; creates dump images or tape streams and verifies restore/inventory behavior. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, temporary `$tmp.*` files, diagnostic `$seqres.full` logs, dump inventory, dump files, or tape media state. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
dump/restore output is sensitive to inventory state, media splitting, timestamp filtering, and quota special files; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/268.out`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 64 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/268 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/269 -->
# sources/test-tools/xfstests/tests/xfs/269

## Purpose
`sources/test-tools/xfstests/tests/xfs/269` is a XFS fstests regression. Check that attr_list_by_handle copies the cursor back to userspace. Override the default cleanup function. The `_begin_fstest` declaration is `auto quick ioctl`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`, `./common/attr`, `./common/populate`. Local helper surface: `_cleanup`. Requirement gates: `_require_scratch`, `_require_populate_commands`, `_require_test_program "attr-list-by-handle-cursor-test"`. Important external or harness commands observed in the full source include `attr-list-by-handle-cursor-test`, `mount`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, temporary `$tmp.*` files, diagnostic `$seqres.full` logs. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
golden output can drift when xfsprogs diagnostics, filters, or common fstests helpers change; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/269.out`; stable progress labels including `echo "Format and mount"`, `echo "Stuff file with xattrs"`, `echo "Run test program"`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 43 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/269 -->
