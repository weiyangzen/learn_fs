# subset-b-009552 research

This grouped report covers XFS fstests scripts `xfs/042` through `xfs/157` plus `xfs/116.cfg`. Each section is wrapped with the required source-path markers for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/042 -->
# sources/test-tools/xfstests/tests/xfs/042

## Purpose
`sources/test-tools/xfstests/tests/xfs/042` is a metadata corruption and repair regression test. xfs_fsr QA tests create a large fragmented file and check that xfs_fsr doesn't corrupt it or the other contents of the filesystem The `_begin_fstest` declaration is `_begin_fstest fsr ioctl auto prealloc`, which places the test in the `fsr, ioctl, auto, prealloc` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`. Local helper surface: no local helper functions beyond optional `_cleanup`. Required capabilities: `_require_xfs_io_command "falloc"`; `_require_scratch`. External and harness commands observed in the full source include `xfs_fsr`, `xfs_bmap`, `xfs_io`, `mkfs`, `mount`, `fill2`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; runs XFS diagnostic or administrative tools; injects corruption, I/O failure, debug hooks, or log errors; compares generated state to expected output or filters nondeterminism. Observable progress/output points include `echo -n "Make a 96 megabyte filesystem on SCRATCH_DEV and mount... "`; `echo "done"`; `echo -n "Reserve 32 1Mb unfragmented regions... "`; `echo -n "Fill filesystem with fill file... "`; `echo -n "Use up any further available space... "`; `echo -n "Punch every second 4k block... "`; `echo -n "Create one very large file... "`; `echo -n "Check fill file... "`. It installs a custom `_cleanup` to tear down mounts/devices and remove temporary files.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
intentionally corrupts metadata, so failures can be expected until repair or mount rejection checks run. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/042.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo -n "Make a 96 megabyte filesystem on SCRATCH_DEV and mount... "`, `echo "done"`, `echo -n "Reserve 32 1Mb unfragmented regions... "`. The script has 126 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/042 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/043 -->
# sources/test-tools/xfstests/tests/xfs/043

## Purpose
`sources/test-tools/xfstests/tests/xfs/043` is a xfsdump/xfsrestore coverage test. Test out xfsdump/restore but rmv inventory prior to restore. This checks that the on-disk inventory can be successfully rebuilt from the on-tape inventory. The `_begin_fstest` declaration is `_begin_fstest dump ioctl tape`, which places the test in the `dump, ioctl, tape` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/dump`. Local helper surface: no local helper functions beyond optional `_cleanup`. Required capabilities: `_require_tape $TAPE_DEV`; `_require_scratch`. External and harness commands observed in the full source include `xfsdump`, `mkfs`, `mount`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; compares generated state to expected output or filters nondeterminism. Observable progress/output points include the expected-output oracle is mostly delegated to helper functions and companion output files. It installs a custom `_cleanup` to tear down mounts/devices and remove temporary files.

## State And Persistence Behavior
The test mutates or inspects dump inventory/dump files or tape state. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
dump/restore output is sensitive to inventory cleanup, timestamps, path filters, and optional tape or remote devices. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/043.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks. The script has 41 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/043 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/044 -->
# sources/test-tools/xfstests/tests/xfs/044

## Purpose
`sources/test-tools/xfstests/tests/xfs/044` is a XFS functional regression test. external log uuid/format tests (TODO - version 2 log format) The `_begin_fstest` declaration is `_begin_fstest other auto`, which places the test in the `other, auto` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`. Local helper surface: `_check_mount`, `_check_no_mount`, `_check_require_logdev`, `_unexpected`. Required capabilities: `_require_logdev`; `_require_scratch`; `_require_test_program "loggen"`. External and harness commands observed in the full source include `xfs_db`, `mkfs`, `mount`, `umount`, `loggen`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; runs XFS diagnostic or administrative tools; uses loop, realtime, external log, idmapped, or reflink devices; compares generated state to expected output or filters nondeterminism. Observable progress/output points include `echo " *** mount (expect success)"`; `echo " !!! mount failed (expecting success)"`; `echo " *** umount"`; `echo " !!! umount failed (expecting success)"`; `echo " *** mount (expect failure)"`; `echo " !!! mount succeeded (expecting failure)"`; `echo " *** mount without logdev (expect failure)"`; `echo " !!! unexpected XFS command failure"`. It relies primarily on the default fstests cleanup path.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents, journal/log metadata. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
loop/external-device cleanup must be reliable to avoid leaking mounts or loop devices. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/044.out`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo " *** mount (expect success)"`, `echo " !!! mount failed (expecting success)"`, `echo " *** umount"`. The script has 134 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/044 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/045 -->
# sources/test-tools/xfstests/tests/xfs/045

## Purpose
`sources/test-tools/xfstests/tests/xfs/045` is a XFS functional regression test. test mount of two FSes with identical UUID and mount with unknown option The `_begin_fstest` declaration is `_begin_fstest other auto quick`, which places the test in the `other, auto, quick` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`. Local helper surface: `_get_existing_uuid`. Required capabilities: `_require_test`; `_require_scratch_nocheck`. External and harness commands observed in the full source include `xfs_db`, `mkfs`, `mount`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; runs XFS diagnostic or administrative tools. Observable progress/output points include `echo "*** get uuid"`; `echo "*** mkfs"`; `echo "!!! failed to mkfs on $SCRATCH_DEV"`; `echo "*** mount fs with bad mount option (expect failure)"`; `echo "!!! mount succeeded (expecting failure)"`; `echo "*** duplicate uuid"`; `echo "*** mount fs with duplicate uuid (expect failure)"`; `echo "*** ok!"`. It relies primarily on the default fstests cleanup path.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
relies on fstests environment variables, scratch/test device hygiene, and filtered golden output remaining stable. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/045.out`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo "*** get uuid"`, `echo "*** mkfs"`, `echo "!!! failed to mkfs on $SCRATCH_DEV"`. The script has 57 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/045 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/046 -->
# sources/test-tools/xfstests/tests/xfs/046

## Purpose
`sources/test-tools/xfstests/tests/xfs/046` is a xfsdump/xfsrestore coverage test. check on symlinks permissions The `_begin_fstest` declaration is `_begin_fstest dump ioctl auto quick`, which places the test in the `dump, ioctl, auto, quick` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/dump`. Local helper surface: no local helper functions beyond optional `_cleanup`. Required capabilities: `_require_scratch`. External and harness commands observed in the full source include `mkfs`, `mount`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; compares generated state to expected output or filters nondeterminism. Observable progress/output points include the expected-output oracle is mostly delegated to helper functions and companion output files. It installs a custom `_cleanup` to tear down mounts/devices and remove temporary files.

## State And Persistence Behavior
The test mutates or inspects dump inventory/dump files or tape state. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
dump/restore output is sensitive to inventory cleanup, timestamps, path filters, and optional tape or remote devices. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/046.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks. The script has 34 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/046 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/047 -->
# sources/test-tools/xfstests/tests/xfs/047

## Purpose
`sources/test-tools/xfstests/tests/xfs/047` is a xfsdump/xfsrestore coverage test. invutil with interactive responses The `_begin_fstest` declaration is `_begin_fstest dump ioctl auto`, which places the test in the `dump, ioctl, auto` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/dump`. Local helper surface: no local helper functions beyond optional `_cleanup`. Required capabilities: `_require_scratch`. External and harness commands observed in the full source include `xfsinvutil`, `mkfs`, `mount`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas. Observable progress/output points include `echo "middate = $middate" >>$seqres.full`. It installs a custom `_cleanup` to tear down mounts/devices and remove temporary files.

## State And Persistence Behavior
The test mutates or inspects dump inventory/dump files or tape state. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
dump/restore output is sensitive to inventory cleanup, timestamps, path filters, and optional tape or remote devices. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/047.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo "middate = $middate" >>$seqres.full`. The script has 65 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/047 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/048 -->
# sources/test-tools/xfstests/tests/xfs/048

## Purpose
`sources/test-tools/xfstests/tests/xfs/048` is a XFS functional regression test. test return codes from xfsctl on bad userspace address The `_begin_fstest` declaration is `_begin_fstest other auto quick`, which places the test in the `other, auto, quick` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`. Local helper surface: no local helper functions beyond optional `_cleanup`. Required capabilities: `_require_test`. External and harness commands observed in the full source include `src/fault`, `fault`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow runs a linear fstests shell scenario against the configured scratch or test target. Observable progress/output points include the expected-output oracle is mostly delegated to helper functions and companion output files. It relies primarily on the default fstests cleanup path.

## State And Persistence Behavior
The test mutates or inspects test filesystem paths/devices. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
relies on fstests environment variables, scratch/test device hygiene, and filtered golden output remaining stable. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/048.out`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks. The script has 21 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/048 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/049 -->
# sources/test-tools/xfstests/tests/xfs/049

## Purpose
`sources/test-tools/xfstests/tests/xfs/049` is a XFS functional regression test. XFS on loop test The `_begin_fstest` declaration is `_begin_fstest rw auto quick`, which places the test in the `rw, auto, quick` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`. Local helper surface: `_log`. Required capabilities: `_require_nonexternal`; `_require_scratch_nocheck`; `_require_no_large_scratch_dev`; `_require_loop`; `_require_extra_fs ext2`; `_require_non_zoned_device $SCRATCH_DEV`. External and harness commands observed in the full source include `mkfs`, `mount`, `umount`, `fsstress`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; uses loop, realtime, external log, idmapped, or reflink devices. Observable progress/output points include `echo "--- mounts at end (after cleanup)" >> $seqres.full`; `echo "--- $*"`; `echo "--- $*" >> $seqres.full`; `echo "(dev=$SCRATCH_DEV, mount=$SCRATCH_MNT)" >> $seqres.full`; `echo "" >> $seqres.full`; `echo "--- mounts" >> $seqres.full`; `echo y | mkfs -t ext2 $loop_dev2 >> $seqres.full 2>&1 \`; `echo "--- mounts at end (before cleanup)" >> $seqres.full`. It installs a custom `_cleanup` to tear down mounts/devices and remove temporary files.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents, loop device mappings. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
loop/external-device cleanup must be reliable to avoid leaking mounts or loop devices. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/049.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo "--- mounts at end (after cleanup)" >> $seqres.full`, `echo "--- $*"`, `echo "--- $*" >> $seqres.full`. The script has 121 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/049 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/050 -->
# sources/test-tools/xfstests/tests/xfs/050

## Purpose
`sources/test-tools/xfstests/tests/xfs/050` is a quota/accounting regression test. Exercises basic XFS quota functionality uquota, gquota, uqnoenforce, gqnoenforce, pquota, pqnoenforce The `_begin_fstest` declaration is `_begin_fstest quota auto quick`, which places the test in the `quota, auto, quick` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`, `. ./common/quota`. Local helper surface: `_filter_and_check_blks`, `_exercise`. Required capabilities: `_require_scratch`; `_require_xfs_quota`. External and harness commands observed in the full source include `xfs_quota`, `mkfs`, `mount`, `quota`, `repquota`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; compares generated state to expected output or filters nondeterminism. Observable progress/output points include `echo "Using type=$type id=$id" >>$seqres.full`; `echo`; `echo "*** report no quota settings" | tee -a $seqres.full`; `echo "*** report initial settings" | tee -a $seqres.full`; `echo "ls -l $SCRATCH_MNT" >>$seqres.full`; `echo "*** push past the soft inode limit" | tee -a $seqres.full`; `echo "*** push past the soft block limit" | tee -a $seqres.full`; `echo "*** push past the hard inode limit (expect EDQUOT)" | tee -a $seqres.full`. It installs a custom `_cleanup` to tear down mounts/devices and remove temporary files.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents, quota accounting records and limits. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
quota results vary with block size, delayed allocation, mount options, and configured test users/groups/projects. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/050.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo "Using type=$type id=$id" >>$seqres.full`, `echo`, `echo "*** report no quota settings" | tee -a $seqres.full`. The script has 201 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/050 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/051 -->
# sources/test-tools/xfstests/tests/xfs/051

## Purpose
`sources/test-tools/xfstests/tests/xfs/051` is a log recovery/error-injection test. Simulate a buffer use after free race in XFS log recovery. The race triggers on I/O failures during log recovery. Note that this test is dangerous as it causes BUG() errors or a panic. The `_begin_fstest` declaration is `_begin_fstest shutdown auto log metadata`, which places the test in the `shutdown, auto, log, metadata` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/dmflakey`. Local helper surface: no local helper functions beyond optional `_cleanup`. Required capabilities: `_require_scratch`; `_require_dm_target flakey`; `_require_xfs_sysfs debug/log_recovery_delay`. External and harness commands observed in the full source include `mkfs`, `mount`, `fsstress`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; injects corruption, I/O failure, debug hooks, or log errors. Observable progress/output points include `echo "Silence is golden."`; `echo 10 > /sys/fs/xfs/debug/log_recovery_delay`; `echo 0 > /sys/fs/xfs/debug/log_recovery_delay`. It installs a custom `_cleanup` to tear down mounts/devices and remove temporary files.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents, journal/log metadata. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
depends on kernel log recovery/error-injection behavior and can expose kernel bugs or require debug facilities. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/051.out`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo "Silence is golden."`, `echo 10 > /sys/fs/xfs/debug/log_recovery_delay`, `echo 0 > /sys/fs/xfs/debug/log_recovery_delay`. The script has 69 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/051 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/052 -->
# sources/test-tools/xfstests/tests/xfs/052

## Purpose
`sources/test-tools/xfstests/tests/xfs/052` is a quota/accounting regression test. Ensure that quota(1) displays blocksizes matching ondisk dquots. MOUNT_OPTIONS can be set to gquota to test group quota, defaults to uquota if MOUNT_OPTIONS is not set. The `_begin_fstest` declaration is `_begin_fstest quota db auto quick`, which places the test in the `quota, db, auto, quick` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`, `. ./common/quota`. Local helper surface: no local helper functions beyond optional `_cleanup`. Required capabilities: `_require_scratch`; `_require_xfs_quota`; `_require_nobody`. External and harness commands observed in the full source include `xfs_quota`, `xfs_db`, `mkfs`, `mount`, `quota`, `feature`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; runs XFS diagnostic or administrative tools; compares generated state to expected output or filters nondeterminism. Observable progress/output points include `echo ===quota output >> $seqres.full`; `echo ===xfs_db output >> $seqres.full`; `echo Comparing out of xfs_quota and xfs_db`. It installs a custom `_cleanup` to tear down mounts/devices and remove temporary files.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents, quota accounting records and limits. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
quota results vary with block size, delayed allocation, mount options, and configured test users/groups/projects. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/052.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo ===quota output >> $seqres.full`, `echo ===xfs_db output >> $seqres.full`, `echo Comparing out of xfs_quota and xfs_db`. The script has 107 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/052 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/053 -->
# sources/test-tools/xfstests/tests/xfs/053

## Purpose
`sources/test-tools/xfstests/tests/xfs/053` is a xfs_repair regression test. Ensure that xfs_repair can properly spot SGI_ACL_FILE and SGI_ACL_DEFAULT in the root attr namespace. Due to bugs here and there, we sometimes matched on partial strings with those names, and threw off xfs_repair. The `_begin_fstest` declaration is `_begin_fstest attr acl repair quick auto`, which places the test in the `attr, acl, repair, quick, auto` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`. Local helper surface: no local helper functions beyond optional `_cleanup`. Required capabilities: `_require_scratch`; `_require_attrs`. External and harness commands observed in the full source include `xfs_repair`, `mkfs`, `mount`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; runs XFS diagnostic or administrative tools; injects corruption, I/O failure, debug hooks, or log errors; compares generated state to expected output or filters nondeterminism. Observable progress/output points include the expected-output oracle is mostly delegated to helper functions and companion output files. It relies primarily on the default fstests cleanup path.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents, extended attribute forks, ACL metadata. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
intentionally corrupts metadata, so failures can be expected until repair or mount rejection checks run; xfs_repair behavior and diagnostics are part of the oracle and may change across xfsprogs versions. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/053.out`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks. The script has 53 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/053 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/054 -->
# sources/test-tools/xfstests/tests/xfs/054

## Purpose
`sources/test-tools/xfstests/tests/xfs/054` is a XFS functional regression test. Exercise the xfs_io inode command The `_begin_fstest` declaration is `_begin_fstest auto quick`, which places the test in the `auto, quick` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`. Local helper surface: no local helper functions beyond optional `_cleanup`. Required capabilities: `_require_test`; `_require_xfs_io_command "inode"`. External and harness commands observed in the full source include `xfs_io`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow creates or mutates files, directories, links, xattrs, ACLs, or quotas; runs XFS diagnostic or administrative tools; compares generated state to expected output or filters nondeterminism. Observable progress/output points include the expected-output oracle is mostly delegated to helper functions and companion output files. It relies primarily on the default fstests cleanup path.

## State And Persistence Behavior
The test mutates or inspects test filesystem paths/devices. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
relies on fstests environment variables, scratch/test device hygiene, and filtered golden output remaining stable. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/054.out`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks. The script has 70 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/054 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/055 -->
# sources/test-tools/xfstests/tests/xfs/055

## Purpose
`sources/test-tools/xfstests/tests/xfs/055` is a xfsdump/xfsrestore coverage test. Test xfsdump/restore to a remote IRIX tape using RMT user The `_begin_fstest` declaration is `_begin_fstest dump ioctl remote tape`, which places the test in the `dump, ioctl, remote, tape` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/dump`. Local helper surface: no local helper functions beyond optional `_cleanup`. Required capabilities: `_require_tape $RMT_TAPE_USER@$RMT_IRIXTAPE_DEV`; `_require_scratch`. External and harness commands observed in the full source include `xfsdump`, `mkfs`, `mount`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; compares generated state to expected output or filters nondeterminism. Observable progress/output points include the expected-output oracle is mostly delegated to helper functions and companion output files. It installs a custom `_cleanup` to tear down mounts/devices and remove temporary files.

## State And Persistence Behavior
The test mutates or inspects dump inventory/dump files or tape state. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
dump/restore output is sensitive to inventory cleanup, timestamps, path filters, and optional tape or remote devices. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/055.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks. The script has 38 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/055 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/056 -->
# sources/test-tools/xfstests/tests/xfs/056

## Purpose
`sources/test-tools/xfstests/tests/xfs/056` is a xfsdump/xfsrestore coverage test. Test xfsdump/xfsrestore to a dump file (as opposed to a tape) and test restoring various permissions/modes The `_begin_fstest` declaration is `_begin_fstest dump ioctl auto quick`, which places the test in the `dump, ioctl, auto, quick` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/dump`. Local helper surface: no local helper functions beyond optional `_cleanup`. Required capabilities: `_require_scratch`. External and harness commands observed in the full source include `xfsdump`, `xfsrestore`, `mkfs`, `mount`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; compares generated state to expected output or filters nondeterminism. Observable progress/output points include the expected-output oracle is mostly delegated to helper functions and companion output files. It installs a custom `_cleanup` to tear down mounts/devices and remove temporary files.

## State And Persistence Behavior
The test mutates or inspects dump inventory/dump files or tape state. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
dump/restore output is sensitive to inventory cleanup, timestamps, path filters, and optional tape or remote devices. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/056.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks. The script has 36 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/056 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/057 -->
# sources/test-tools/xfstests/tests/xfs/057

## Purpose
`sources/test-tools/xfstests/tests/xfs/057` is a metadata corruption and repair regression test. Attempt to reproduce log recovery failure by writing corrupt log records over the last good tail in the log. The tail is force pinned while a workload runs the head as close as possible behind the tail. Once the head is pinned, corrupted log records are written to the log and the filesystem shuts down. While log recovery should handle the corrupted log records, it has historical problems dealing with the situation where the corrupted log records may have overwritten the tail of the previous good record in the log. If this occurs, log recovery may fail. This can be reproduced more reliably under non-default conditions such as with the smallest supported FSB sizes and/or largest supported log buffer sizes and counts (logbufs and logbsize mount options). Note that this test requires a DEBUG mode kernel. The `_begin_fstest` declaration is `_begin_fstest auto log recoveryloop`, which places the test in the `auto, log, recoveryloop` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/inject`. Local helper surface: no local helper functions beyond optional `_cleanup`. Required capabilities: `_require_xfs_io_error_injection log_item_pin`; `_require_xfs_io_error_injection log_bad_crc`; `_require_scratch`. External and harness commands observed in the full source include `xfs_io`, `mkfs`, `mount`, `fsstress`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; runs XFS diagnostic or administrative tools; injects corruption, I/O failure, debug hooks, or log errors; uses loop, realtime, external log, idmapped, or reflink devices. Observable progress/output points include `echo 0 > /sys/fs/xfs/$sdev/errortag/log_item_pin`; `echo "Silence is golden."`. It installs a custom `_cleanup` to tear down mounts/devices and remove temporary files.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents, loop device mappings, journal/log metadata. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
intentionally corrupts metadata, so failures can be expected until repair or mount rejection checks run; depends on kernel log recovery/error-injection behavior and can expose kernel bugs or require debug facilities; loop/external-device cleanup must be reliable to avoid leaking mounts or loop devices. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/057.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo 0 > /sys/fs/xfs/$sdev/errortag/log_item_pin`, `echo "Silence is golden."`. The script has 88 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/057 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/058 -->
# sources/test-tools/xfstests/tests/xfs/058

## Purpose
`sources/test-tools/xfstests/tests/xfs/058` is a metadata corruption and repair regression test. Ensure that xfs_db fuzz command works as advertised. The `_begin_fstest` declaration is `_begin_fstest auto quick fuzzers`, which places the test in the `auto, quick, fuzzers` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`, `. ./common/fuzzy`. Local helper surface: `do_xfs_db`. Required capabilities: `_require_scratch_nocheck`; `_require_command "$XFS_DB_PROG" "xfs_db"`; `_require_xfs_db_command "fuzz"`. External and harness commands observed in the full source include `xfs_db`, `mkfs`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; runs XFS diagnostic or administrative tools; injects corruption, I/O failure, debug hooks, or log errors; compares generated state to expected output or filters nondeterminism. Observable progress/output points include `echo "Format"`; `echo "Allowing $cmd of corrupted data with good CRC"`; `echo "Test verb ${verb}"`; `echo "Test verb random"`; `echo "Done"`. It relies primarily on the default fstests cleanup path.

## State And Persistence Behavior
The test mutates or inspects filesystem metadata and command output only. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
intentionally corrupts metadata, so failures can be expected until repair or mount rejection checks run. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/058.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo "Format"`, `echo "Allowing $cmd of corrupted data with good CRC"`, `echo "Test verb ${verb}"`. The script has 54 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/058 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/059 -->
# sources/test-tools/xfstests/tests/xfs/059

## Purpose
`sources/test-tools/xfstests/tests/xfs/059` is a xfsdump/xfsrestore coverage test. Test multi-stream xfsdump/xfsrestore. The `_begin_fstest` declaration is `_begin_fstest dump ioctl auto quick`, which places the test in the `dump, ioctl, auto, quick` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/dump`. Local helper surface: no local helper functions beyond optional `_cleanup`. Required capabilities: `_require_multi_stream`; `_require_scratch`. External and harness commands observed in the full source include `xfsdump`, `xfsrestore`, `mkfs`, `mount`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; compares generated state to expected output or filters nondeterminism. Observable progress/output points include the expected-output oracle is mostly delegated to helper functions and companion output files. It installs a custom `_cleanup` to tear down mounts/devices and remove temporary files.

## State And Persistence Behavior
The test mutates or inspects dump inventory/dump files or tape state. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
dump/restore output is sensitive to inventory cleanup, timestamps, path filters, and optional tape or remote devices. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/059.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks. The script has 38 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/059 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/060 -->
# sources/test-tools/xfstests/tests/xfs/060

## Purpose
`sources/test-tools/xfstests/tests/xfs/060` is a xfsdump/xfsrestore coverage test. Test multi-stream xfsdump and restoring one stream at a time. The `_begin_fstest` declaration is `_begin_fstest dump ioctl auto quick`, which places the test in the `dump, ioctl, auto, quick` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/dump`. Local helper surface: no local helper functions beyond optional `_cleanup`. Required capabilities: `_require_multi_stream`; `_require_scratch`. External and harness commands observed in the full source include `xfsdump`, `mkfs`, `mount`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; compares generated state to expected output or filters nondeterminism. Observable progress/output points include the expected-output oracle is mostly delegated to helper functions and companion output files. It installs a custom `_cleanup` to tear down mounts/devices and remove temporary files.

## State And Persistence Behavior
The test mutates or inspects dump inventory/dump files or tape state. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
dump/restore output is sensitive to inventory cleanup, timestamps, path filters, and optional tape or remote devices. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/060.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks. The script has 44 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/060 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/061 -->
# sources/test-tools/xfstests/tests/xfs/061

## Purpose
`sources/test-tools/xfstests/tests/xfs/061` is a xfsdump/xfsrestore coverage test. Test restoring a dump created in IRIX/XFS The `_begin_fstest` declaration is `_begin_fstest dump ioctl auto quick`, which places the test in the `dump, ioctl, auto, quick` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/dump`. Local helper surface: no local helper functions beyond optional `_cleanup`. Required capabilities: `_require_scratch`. External and harness commands observed in the full source include `mkfs`, `mount`, `quota`, `dumpfile`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; compares generated state to expected output or filters nondeterminism. Observable progress/output points include the expected-output oracle is mostly delegated to helper functions and companion output files. It installs a custom `_cleanup` to tear down mounts/devices and remove temporary files.

## State And Persistence Behavior
The test mutates or inspects dump inventory/dump files or tape state. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
dump/restore output is sensitive to inventory cleanup, timestamps, path filters, and optional tape or remote devices. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/061.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks. The script has 42 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/061 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/062 -->
# sources/test-tools/xfstests/tests/xfs/062

## Purpose
`sources/test-tools/xfstests/tests/xfs/062` is a XFS functional regression test. Use the bstat utility to verify bulkstat finds all inodes in a filesystem. Test under various inode counts, inobt record layouts and bulkstat batch sizes. The `_begin_fstest` declaration is `_begin_fstest auto ioctl quick`, which places the test in the `auto, ioctl, quick` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`. Local helper surface: `_bstat_count`, `_bstat_test`. Required capabilities: `_require_scratch`. External and harness commands observed in the full source include `mkfs`, `mount`, `bstat`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; compares generated state to expected output or filters nondeterminism. Observable progress/output points include `echo "expect $expect"`. It relies primarily on the default fstests cleanup path.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
relies on fstests environment variables, scratch/test device hygiene, and filtered golden output remaining stable. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/062.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo "expect $expect"`. The script has 78 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/062 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/063 -->
# sources/test-tools/xfstests/tests/xfs/063

## Purpose
`sources/test-tools/xfstests/tests/xfs/063` is a xfsdump/xfsrestore coverage test. xfsdump/xfsrestore with EAs The `_begin_fstest` declaration is `_begin_fstest dump attr auto quick`, which places the test in the `dump, attr, auto, quick` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`, `. ./common/dump`, `. ./common/attr`. Local helper surface: no local helper functions beyond optional `_cleanup`. Required capabilities: `_require_attrs trusted user`; `_require_scratch`. External and harness commands observed in the full source include `xfsdump`, `xfsrestore`, `mkfs`, `mount`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; compares generated state to expected output or filters nondeterminism. Observable progress/output points include the expected-output oracle is mostly delegated to helper functions and companion output files. It installs a custom `_cleanup` to tear down mounts/devices and remove temporary files.

## State And Persistence Behavior
The test mutates or inspects dump inventory/dump files or tape state, extended attribute forks. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
dump/restore output is sensitive to inventory cleanup, timestamps, path filters, and optional tape or remote devices. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/063.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks. The script has 43 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/063 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/064 -->
# sources/test-tools/xfstests/tests/xfs/064

## Purpose
`sources/test-tools/xfstests/tests/xfs/064` is a xfsdump/xfsrestore coverage test. test multilevel dump and restores with hardlinks The `_begin_fstest` declaration is `_begin_fstest dump auto`, which places the test in the `dump, auto` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`, `. ./common/dump`. Local helper surface: `_ls_size_filter`. Required capabilities: `_require_scratch`. External and harness commands observed in the full source include `xfsrestore`, `mkfs`, `mount`, `quota`, `lstat64`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; compares generated state to expected output or filters nondeterminism. Observable progress/output points include `echo "Do the incremental dumps"`; `echo "********* level $i ***********" >>$seqres.full`; `echo "Listing of what files we start with:"`; `echo "Look at what files are contained in the inc. dump"`; `echo ""`; `echo "restoring from df.level$i"`; `echo "Do the cumulative restores"`; `echo "ls -l restore_dir"`. It installs a custom `_cleanup` to tear down mounts/devices and remove temporary files.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents, dump inventory/dump files or tape state. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
dump/restore output is sensitive to inventory cleanup, timestamps, path filters, and optional tape or remote devices. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/064.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo "Do the incremental dumps"`, `echo "********* level $i ***********" >>$seqres.full`, `echo "Listing of what files we start with:"`. The script has 94 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/064 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/065 -->
# sources/test-tools/xfstests/tests/xfs/065

## Purpose
`sources/test-tools/xfstests/tests/xfs/065` is a xfsdump/xfsrestore coverage test. Testing incremental dumps and cumulative restores with "adding, deleting, renaming, linking, and unlinking files and directories". Do different operations for each level. The `_begin_fstest` declaration is `_begin_fstest dump auto`, which places the test in the `dump, auto` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`, `. ./common/dump`, `. ./common/quota`. Local helper surface: `_list_dir`. Required capabilities: `_require_scratch`. External and harness commands observed in the full source include `xfsdump`, `mkfs`, `mount`, `quota`, `lstat64`, `feature`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; compares generated state to expected output or filters nondeterminism. Observable progress/output points include `echo "Do the incremental dumps"`; `echo 'add0' >addedfile0`; `echo 'add1' >addedfile1`; `echo 'add2' >addedfile2`; `echo 'add3' >addedfile3`; `echo 'add4' >addeddir3/addedfile4`; `echo 'add5' >addeddir4/addedfile5`; `echo 'add6' >addedfile6`. It installs a custom `_cleanup` to tear down mounts/devices and remove temporary files.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents, dump inventory/dump files or tape state. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
dump/restore output is sensitive to inventory cleanup, timestamps, path filters, and optional tape or remote devices. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/065.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo "Do the incremental dumps"`, `echo 'add0' >addedfile0`, `echo 'add1' >addedfile1`. The script has 183 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/065 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/066 -->
# sources/test-tools/xfstests/tests/xfs/066

## Purpose
`sources/test-tools/xfstests/tests/xfs/066` is a xfsdump/xfsrestore coverage test. Test dumping of large files The `_begin_fstest` declaration is `_begin_fstest dump ioctl auto quick`, which places the test in the `dump, ioctl, auto, quick` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`, `. ./common/dump`. Local helper surface: `_my_stat_filter`. Required capabilities: `_require_test`; `_require_scratch`. External and harness commands observed in the full source include `mkfs`, `mount`, `feature`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; compares generated state to expected output or filters nondeterminism. Observable progress/output points include `echo "ls dumpdir/largefile"`; `echo "ls restoredir/largefile"`. It installs a custom `_cleanup` to tear down mounts/devices and remove temporary files.

## State And Persistence Behavior
The test mutates or inspects test filesystem paths/devices, dump inventory/dump files or tape state. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
dump/restore output is sensitive to inventory cleanup, timestamps, path filters, and optional tape or remote devices. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/066.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo "ls dumpdir/largefile"`, `echo "ls restoredir/largefile"`. The script has 53 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/066 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/067 -->
# sources/test-tools/xfstests/tests/xfs/067

## Purpose
`sources/test-tools/xfstests/tests/xfs/067` is a XFS functional regression test. Test out acl/dacls which fit in shortform in the inode The `_begin_fstest` declaration is `_begin_fstest acl attr auto quick`, which places the test in the `acl, attr, auto, quick` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`. Local helper surface: no local helper functions beyond optional `_cleanup`. Required capabilities: `_require_attrs`; `_require_acls`; `_require_scratch`. External and harness commands observed in the full source include `mkfs`, `mount`, `getfacl`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; compares generated state to expected output or filters nondeterminism. Observable progress/output points include `echo ""`; `echo "=== Test out large ACLs ==="`; `echo "try 20 aces for access acl"`; `echo "try 20 aces for default acl"`; `echo "try 21 aces for access acl"`; `echo "try 21 aces for default acl"`. It relies primarily on the default fstests cleanup path.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents, extended attribute forks, ACL metadata. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
relies on fstests environment variables, scratch/test device hygiene, and filtered golden output remaining stable. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/067.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo ""`, `echo "=== Test out large ACLs ==="`, `echo "try 20 aces for access acl"`. The script has 64 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/067 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/068 -->
# sources/test-tools/xfstests/tests/xfs/068

## Purpose
`sources/test-tools/xfstests/tests/xfs/068` is a xfsdump/xfsrestore coverage test. Test out a level 0 dump/restore of a subdir to a file Use fsstress to create a larger directory structure with a mix of files Test for regression caused by c7cb51d xfs: fix error handling at xfs_inumbers The `_begin_fstest` declaration is `_begin_fstest auto stress dump`, which places the test in the `auto, stress, dump` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/dump`. Local helper surface: no local helper functions beyond optional `_cleanup`. Required capabilities: `_require_scratch`. External and harness commands observed in the full source include `mkfs`, `mount`, `fsstress`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; compares generated state to expected output or filters nondeterminism. Observable progress/output points include `echo -n "Before: " >> $seqres.full`; `echo -n "After: " >> $seqres.full`. It installs a custom `_cleanup` to tear down mounts/devices and remove temporary files.

## State And Persistence Behavior
The test mutates or inspects dump inventory/dump files or tape state. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
dump/restore output is sensitive to inventory cleanup, timestamps, path filters, and optional tape or remote devices. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/068.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo -n "Before: " >> $seqres.full`, `echo -n "After: " >> $seqres.full`. The script has 46 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/068 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/069 -->
# sources/test-tools/xfstests/tests/xfs/069

## Purpose
`sources/test-tools/xfstests/tests/xfs/069` is a XFS functional regression test. Determine whether the extent size hint can be set on directories with allocated extents correctly. The `_begin_fstest` declaration is `_begin_fstest ioctl auto quick`, which places the test in the `ioctl, auto, quick` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`, `. ./common/punch`. Local helper surface: no local helper functions beyond optional `_cleanup`. Required capabilities: `_require_scratch`; `_require_congruent_file_oplen $SCRATCH_MNT 8388608`. External and harness commands observed in the full source include `mkfs`, `mount`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; compares generated state to expected output or filters nondeterminism. Observable progress/output points include the expected-output oracle is mostly delegated to helper functions and companion output files. It relies primarily on the default fstests cleanup path.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
relies on fstests environment variables, scratch/test device hygiene, and filtered golden output remaining stable. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/069.out`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks. The script has 53 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/069 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/070 -->
# sources/test-tools/xfstests/tests/xfs/070

## Purpose
`sources/test-tools/xfstests/tests/xfs/070` is a metadata corruption and repair regression test. As part of superblock verification, xfs_repair checks the primary sb and verifies all secondary sb's against the primary. In the event of geometry inconsistency, repair uses a heuristic that tracks the most frequently occurring settings across the set of N (agcount) superblocks. xfs_repair was subject to a bug that disregards this heuristic in the event that the last secondary superblock in the fs is corrupt. The side effect is an unnecessary and potentially time consuming brute force superblock scan. This is a regression test for the aforementioned xfs_repair bug. We intentionally corrupt the last superblock in the fs, run xfs_repair and verify it repairs the fs correctly. We explicitly detect a brute force scan and abort the repair to save time in the failure case. The `_begin_fstest` declaration is `_begin_fstest auto quick repair`, which places the test in the `auto, quick, repair` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`, `. ./common/repair`. Local helper surface: `_xfs_repair_noscan`. Required capabilities: `_require_scratch_nocheck`. External and harness commands observed in the full source include `xfs_db`, `xfs_repair`, `mkfs`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; runs XFS diagnostic or administrative tools; injects corruption, I/O failure, debug hooks, or log errors; compares generated state to expected output or filters nondeterminism. Observable progress/output points include the expected-output oracle is mostly delegated to helper functions and companion output files. It installs a custom `_cleanup` to tear down mounts/devices and remove temporary files.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
intentionally corrupts metadata, so failures can be expected until repair or mount rejection checks run; loop/external-device cleanup must be reliable to avoid leaking mounts or loop devices; xfs_repair behavior and diagnostics are part of the oracle and may change across xfsprogs versions. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/070.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks. The script has 91 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/070 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/071 -->
# sources/test-tools/xfstests/tests/xfs/071

## Purpose
`sources/test-tools/xfstests/tests/xfs/071` is a XFS functional regression test. Exercise IO at large file offsets. The `_begin_fstest` declaration is `_begin_fstest rw auto`, which places the test in the `rw, auto` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`. Local helper surface: `_filter_io`, `_filter_off`, `_filter_pwrite`, `_filter_pread`, `write_block`. Required capabilities: `_require_scratch`. External and harness commands observed in the full source include `xfs_bmap`, `xfs_io`, `mkfs`, `mount`, `feature`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; runs XFS diagnostic or administrative tools; compares generated state to expected output or filters nondeterminism. Observable progress/output points include `echo "Writing $bytes bytes, offset is $words (direct=$direct)" | _filter_io`; `echo "Writing $bytes bytes at $location $words (direct=$direct)" >>$seqres.full`; `echo "Reading $bytes bytes (direct=$direct)" | _filter_io`; `echo "Reading $bytes bytes at $location (direct=$direct)" >>$seqres.full`; `echo | tee -a $seqres.full`; `echo`; `echo === Iterating, `expr $upperbound - $count` remains`. It installs a custom `_cleanup` to tear down mounts/devices and remove temporary files.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
relies on fstests environment variables, scratch/test device hygiene, and filtered golden output remaining stable. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo "Writing $bytes bytes, offset is $words (direct=$direct)" | _filter_io`, `echo "Writing $bytes bytes at $location $words (direct=$direct)" >>$seqres.full`, `echo "Reading $bytes bytes (direct=$direct)" | _filter_io`. The script has 145 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/071 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/072 -->
# sources/test-tools/xfstests/tests/xfs/072

## Purpose
`sources/test-tools/xfstests/tests/xfs/072` is a XFS functional regression test. Check some unwritten extent boundary conditions The `_begin_fstest` declaration is `_begin_fstest rw auto prealloc quick`, which places the test in the `rw, auto, prealloc, quick` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`. Local helper surface: no local helper functions beyond optional `_cleanup`. Required capabilities: `_require_scratch`; `_require_xfs_io_command "falloc"`. External and harness commands observed in the full source include `xfs_io`, `mkfs`, `mount`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; runs XFS diagnostic or administrative tools. Observable progress/output points include `echo Silence is golden`. It installs a custom `_cleanup` to tear down mounts/devices and remove temporary files.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
relies on fstests environment variables, scratch/test device hygiene, and filtered golden output remaining stable. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/072.out`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo Silence is golden`. The script has 56 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/072 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/073 -->
# sources/test-tools/xfstests/tests/xfs/073

## Purpose
`sources/test-tools/xfstests/tests/xfs/073` is a XFS functional regression test. Test xfs_copy The `_begin_fstest` declaration is `_begin_fstest copy auto`, which places the test in the `copy, auto` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`. Local helper surface: `_filter_copy`, `_filter_path`, `_populate_scratch`, `_verify_copy`. Required capabilities: `_require_test`; `_require_attrs`; `_require_xfs_copy`; `_require_scratch`; `_require_loop`. External and harness commands observed in the full source include `xfs_copy`, `mkfs`, `mount`, `fill2attr`, `fill2fs`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; runs XFS diagnostic or administrative tools; uses loop, realtime, external log, idmapped, or reflink devices; compares generated state to expected output or filters nondeterminism. Observable progress/output points include `echo $SCRATCH_MNT/big+attr | $here/src/fill2attr`; `echo checking new image`; `echo mounting new image on loopback`; `echo retrying mount with nouuid option >>$seqres.full`; `echo mount failed - evil!`; `echo comparing new image files to old`; `echo comparing new image directories to old`; `echo comparing new image geometry to old`. It installs a custom `_cleanup` to tear down mounts/devices and remove temporary files.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents, test filesystem paths/devices, loop device mappings. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
loop/external-device cleanup must be reliable to avoid leaking mounts or loop devices. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/073.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo $SCRATCH_MNT/big+attr | $here/src/fill2attr`, `echo checking new image`, `echo mounting new image on loopback`. The script has 161 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/073 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/074 -->
# sources/test-tools/xfstests/tests/xfs/074

## Purpose
`sources/test-tools/xfstests/tests/xfs/074` is a XFS functional regression test. Check some extent size hint boundary conditions that can result in MAXEXTLEN overflows. In xfs_bmap_extsize_align(), we had, if ((temp = (align_alen % extsz))) { align_alen += extsz - temp; } align_alen had the value of 2097151 (i.e. MAXEXTLEN) blocks. extsz had the value of 4096 blocks. align_alen % extsz will be 4095. so align_alen will end up having 2097151 + (4096 - 4095) = 2097152 i.e. (MAXEXTLEN + 1). Thus the length of the new extent will be larger than MAXEXTLEN. This will later cause the bmbt leaf to have an entry whose length is set to zero block count. The `_begin_fstest` declaration is `_begin_fstest quick auto prealloc rw`, which places the test in the `quick, auto, prealloc, rw` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`. Local helper surface: no local helper functions beyond optional `_cleanup`. Required capabilities: `_require_test`; `_require_xfs_io_command "falloc"`; `_require_loop`. External and harness commands observed in the full source include `xfs_bmap`, `xfs_io`, `mkfs`, `mount`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; runs XFS diagnostic or administrative tools; uses loop, realtime, external log, idmapped, or reflink devices. Observable progress/output points include `echo "Silence is golden"`. It installs a custom `_cleanup` to tear down mounts/devices and remove temporary files.

## State And Persistence Behavior
The test mutates or inspects test filesystem paths/devices, loop device mappings. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
intentionally corrupts metadata, so failures can be expected until repair or mount rejection checks run; loop/external-device cleanup must be reliable to avoid leaking mounts or loop devices. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/074.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo "Silence is golden"`. The script has 84 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/074 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/075 -->
# sources/test-tools/xfstests/tests/xfs/075

## Purpose
`sources/test-tools/xfstests/tests/xfs/075` is a XFS functional regression test. Commit bbe051c8 disallows ro->rw remount on norecovery mount This test makes sure the behavior is correct. The `_begin_fstest` declaration is `_begin_fstest auto quick mount`, which places the test in the `auto, quick, mount` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`, `. ./common/quota`. Local helper surface: no local helper functions beyond optional `_cleanup`. Required capabilities: `_require_scratch`. External and harness commands observed in the full source include `mkfs`, `mount`, `quota`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas. Observable progress/output points include `echo "Silence is golden"`. It relies primarily on the default fstests cleanup path.

## State And Persistence Behavior
The test mutates or inspects filesystem metadata and command output only. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
relies on fstests environment variables, scratch/test device hygiene, and filtered golden output remaining stable. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/075.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo "Silence is golden"`. The script has 34 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/075 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/076 -->
# sources/test-tools/xfstests/tests/xfs/076

## Purpose
`sources/test-tools/xfstests/tests/xfs/076` is a XFS functional regression test. Verify that a filesystem with sparse inode support can allocate inodes in the event of free space fragmentation. This test is generic in nature but primarily relevant to filesystems that implement dynamic inode allocation (e.g., XFS). The test is inspired by inode allocation limitations on XFS when available free space is fragmented. XFS allocates inodes 64 at a time and thus requires an extent of length that depends on inode size (64 * isize / blksize). The test creates a small, sparse inode enabled filesystem. It fragments free space, allocates inodes to ENOSPC and then verifies that most of the available inodes (.i.e., free space) have been consumed. The `_begin_fstest` declaration is `_begin_fstest auto enospc punch prealloc`, which places the test in the `auto, enospc, punch, prealloc` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`. Local helper surface: `_consume_freesp`, `_alloc_inodes`. Required capabilities: `_require_scratch_nocheck`; `_require_scratch`; `_require_xfs_io_command "falloc"`; `_require_xfs_io_command "fpunch"`; `_require_xfs_sparse_inodes`. External and harness commands observed in the full source include `xfs_io`, `mkfs`, `mount`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; runs XFS diagnostic or administrative tools; compares generated state to expected output or filters nondeterminism. Observable progress/output points include `echo -n > $dir/$i || break`. It installs a custom `_cleanup` to tear down mounts/devices and remove temporary files.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
relies on fstests environment variables, scratch/test device hygiene, and filtered golden output remaining stable. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/076.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo -n > $dir/$i || break`. The script has 113 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/076 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/077 -->
# sources/test-tools/xfstests/tests/xfs/077

## Purpose
`sources/test-tools/xfstests/tests/xfs/077` is a XFS functional regression test. test UUID modification of CRC-enabled filesystems CRC-enabled / V5 superblock filesystems have a UUID stamped into every piece of metadata, and a mechanism was added later to allow changing the user-visible UUID by copying the original UUID (which matches all the existing metadata) to a new superblock location. Exercise some of that behavior. The `_begin_fstest` declaration is `_begin_fstest auto quick copy`, which places the test in the `auto, quick, copy` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`. Local helper surface: `_test_uuid`, `_fs_has_META_UUID`. Required capabilities: `_require_xfs_copy`; `_require_scratch`; `_require_no_large_scratch_dev`. External and harness commands observed in the full source include `xfs_db`, `xfs_copy`, `mkfs`, `mount`, `fsstress`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; runs XFS diagnostic or administrative tools; injects corruption, I/O failure, debug hooks, or log errors; compares generated state to expected output or filters nondeterminism. Observable progress/output points include `echo "== Generate new UUID"`; `echo "== Rewrite UUID"`; `echo "== Restore old UUID"`; `echo "== xfs_copy with new UUID"`; `echo "== xfs_copy with duplicate UUID"`. It relies primarily on the default fstests cleanup path.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents, test filesystem paths/devices. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
intentionally corrupts metadata, so failures can be expected until repair or mount rejection checks run. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/077.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo "== Generate new UUID"`, `echo "== Rewrite UUID"`, `echo "== Restore old UUID"`. The script has 110 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/077 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/078 -->
# sources/test-tools/xfstests/tests/xfs/078

## Purpose
`sources/test-tools/xfstests/tests/xfs/078` is a online growfs behavior test. Check several growfs corner cases The `_begin_fstest` declaration is `_begin_fstest growfs auto quick`, which places the test in the `growfs, auto, quick` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`. Local helper surface: `_filter_io`, `_grow_loop`. Required capabilities: `_require_test`; `_require_loop`; `_require_xfs_io_command "truncate"`. External and harness commands observed in the full source include `xfs_io`, `mkfs`, `mount`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; runs XFS diagnostic or administrative tools; uses loop, realtime, external log, idmapped, or reflink devices; compares generated state to expected output or filters nondeterminism. Observable progress/output points include `echo "*** create loop mount point"`; `echo`; `echo "=== GROWFS (from $original to $new_size, $bsize blocksize)"`; `echo "*** mkfs loop file (size=$original)"`; `echo "*** extend loop file"`; `echo "*** mount loop filesystem"`; `echo "*** grow loop filesystem"`; `echo "*** unmount"`. It installs a custom `_cleanup` to tear down mounts/devices and remove temporary files.

## State And Persistence Behavior
The test mutates or inspects test filesystem paths/devices, loop device mappings. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
loop/external-device cleanup must be reliable to avoid leaking mounts or loop devices. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/078.out`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo "*** create loop mount point"`, `echo`, `echo "=== GROWFS (from $original to $new_size, $bsize blocksize)"`. The script has 136 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/078 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/079 -->
# sources/test-tools/xfstests/tests/xfs/079

## Purpose
`sources/test-tools/xfstests/tests/xfs/079` is a log recovery/error-injection test. Regression test for a bug in the log record checksum mechanism of XFS. Log records are checksummed during recovery and a warning or mount failure occurs on checksum verification failure. XFS had a bug where the checksum mechanism verified different parts of a record depending on the current log buffer size. This caused spurious checksum failures when a filesystem is recovered using a different log buffer size from when the filesystem crashed. Test that log recovery succeeds with a different log buffer size from when the filesystem crashed. The `_begin_fstest` declaration is `_begin_fstest shutdown auto log quick`, which places the test in the `shutdown, auto, log, quick` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/log`. Local helper surface: no local helper functions beyond optional `_cleanup`. Required capabilities: `_require_scratch`; `_require_v2log`. External and harness commands observed in the full source include `mkfs`, `mount`, `fsstress`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; compares generated state to expected output or filters nondeterminism. Observable progress/output points include `echo "Silence is golden."`. It relies primarily on the default fstests cleanup path.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents, journal/log metadata. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
depends on kernel log recovery/error-injection behavior and can expose kernel bugs or require debug facilities. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/079.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo "Silence is golden."`. The script has 52 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/079 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/080 -->
# sources/test-tools/xfstests/tests/xfs/080

## Purpose
`sources/test-tools/xfstests/tests/xfs/080` is a XFS functional regression test. rwtest (iogen|doio) The `_begin_fstest` declaration is `_begin_fstest rw ioctl auto quick`, which places the test in the `rw, ioctl, auto, quick` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`. Local helper surface: no local helper functions beyond optional `_cleanup`. Required capabilities: `_require_test`; `_require_xfs_io_command falloc	# iogen requires falloc`. External and harness commands observed in the full source include `xfs_io`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow creates or mutates files, directories, links, xattrs, ACLs, or quotas; runs XFS diagnostic or administrative tools. Observable progress/output points include `echo`; `echo Completed rwtest pass 1 successfully.`. It installs a custom `_cleanup` to tear down mounts/devices and remove temporary files.

## State And Persistence Behavior
The test mutates or inspects test filesystem paths/devices. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
relies on fstests environment variables, scratch/test device hygiene, and filtered golden output remaining stable. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/080.out`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo`, `echo Completed rwtest pass 1 successfully.`. The script has 42 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/080 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/081 -->
# sources/test-tools/xfstests/tests/xfs/081

## Purpose
`sources/test-tools/xfstests/tests/xfs/081` is a metadata corruption and repair regression test. This's a regression test for: a1de97fe296c ("xfs: Fix the free logic of state in xfs_attr_node_hasname") After we corrupted an attr leaf block (under node block), getxattr might hit EFSCORRUPTED in xfs_attr_node_get when it does xfs_attr_node_hasname. A bug cause xfs_attr_node_get won't do xfs_buf_trans release job, then a subsequent removexattr will hang. The `_begin_fstest` declaration is `_begin_fstest auto quick attr`, which places the test in the `auto, quick, attr` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`, `. ./common/populate`. Local helper surface: no local helper functions beyond optional `_cleanup`. Required capabilities: `_require_scratch_nocheck`; `_require_scratch_xfs_crc`; `_require_attrs`; `_require_populate_commands`; `_require_xfs_db_blocktrash_z_command`. External and harness commands observed in the full source include `xfs_db`, `mkfs`, `mount`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; runs XFS diagnostic or administrative tools; injects corruption, I/O failure, debug hooks, or log errors; compares generated state to expected output or filters nondeterminism. Observable progress/output points include `echo "Silence is golden"`. It relies primarily on the default fstests cleanup path.

## State And Persistence Behavior
The test mutates or inspects extended attribute forks, journal/log metadata. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
intentionally corrupts metadata, so failures can be expected until repair or mount rejection checks run. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/081.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo "Silence is golden"`. The script has 78 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/081 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/082 -->
# sources/test-tools/xfstests/tests/xfs/082

## Purpose
`sources/test-tools/xfstests/tests/xfs/082` is a XFS functional regression test. Regression test for xfsprogs commit: XXXXXXXX ("xfs_copy: don't use cached buffer reads until after libxfs_mount") It was discovered that passing xfs_copy a source device containing an ext4 filesystem would cause xfs_copy to crash.  Further investigation revealed that any readable path that didn't have a plausible XFS superblock in block zero would produce the same crash, so this regression test exploits that. The `_begin_fstest` declaration is `_begin_fstest auto copy quick`, which places the test in the `auto, copy, quick` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`. Local helper surface: `filter_copy`. Required capabilities: `_require_xfs_copy`; `_require_test`. External and harness commands observed in the full source include `xfs_copy`, `mount`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; runs XFS diagnostic or administrative tools; compares generated state to expected output or filters nondeterminism. Observable progress/output points include the expected-output oracle is mostly delegated to helper functions and companion output files. It relies primarily on the default fstests cleanup path.

## State And Persistence Behavior
The test mutates or inspects test filesystem paths/devices. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
relies on fstests environment variables, scratch/test device hygiene, and filtered golden output remaining stable. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/082.out`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks. The script has 36 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/082 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/083 -->
# sources/test-tools/xfstests/tests/xfs/083

## Purpose
`sources/test-tools/xfstests/tests/xfs/083` is a XFS functional regression test. Create and populate an XFS filesystem, fuzz the metadata, then see how the kernel reacts, how xfs_repair fares in fixing the mess, and then try more kernel accesses to see if it really fixed things. The `_begin_fstest` declaration is `_begin_fstest dangerous_fuzzers punch`, which places the test in the `dangerous_fuzzers, punch` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`, `. ./common/populate`, `. ./common/fuzzy`. Local helper surface: `scratch_repair`. Required capabilities: `_require_scratch`; `_require_attrs`; `_require_populate_commands`. External and harness commands observed in the full source include `xfs_db`, `xfs_repair`, `mkfs`, `mount`, `umount`, `chattr`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; runs XFS diagnostic or administrative tools; injects corruption, I/O failure, debug hooks, or log errors; uses loop, realtime, external log, idmapped, or reflink devices; compares generated state to expected output or filters nondeterminism. Observable progress/output points include `echo "++ fsck pass ${fsck_pass}" > "${FSCK_LOG}"`; `echo "++ allegedly fixed, reverify" >> "${FSCK_LOG}"`; `echo "++ fsck returns ${res}" >> "${FSCK_LOG}"`; `echo "++ fsck thinks we are done" >> "${FSCK_LOG}"`; `echo "+++ replaying log" >> "${FSCK_LOG}"`; `echo "+++ mount returns ${res}" >> "${FSCK_LOG}"`; `echo "+++ zeroing log" >> "${FSCK_LOG}"`; `echo "+++ returns $?" >> "${FSCK_LOG}"`. It installs a custom `_cleanup` to tear down mounts/devices and remove temporary files.

## State And Persistence Behavior
The test mutates or inspects loop device mappings. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
intentionally corrupts metadata, so failures can be expected until repair or mount rejection checks run; loop/external-device cleanup must be reliable to avoid leaking mounts or loop devices; xfs_repair behavior and diagnostics are part of the oracle and may change across xfsprogs versions. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/083.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo "++ fsck pass ${fsck_pass}" > "${FSCK_LOG}"`, `echo "++ allegedly fixed, reverify" >> "${FSCK_LOG}"`, `echo "++ fsck returns ${res}" >> "${FSCK_LOG}"`. The script has 151 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/083 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/084 -->
# sources/test-tools/xfstests/tests/xfs/084

## Purpose
`sources/test-tools/xfstests/tests/xfs/084` is a metadata corruption and repair regression test. Exercises unwritten extent reads and writes, looking for data corruption (zeroes read) near the end of file. The `_begin_fstest` declaration is `_begin_fstest ioctl rw auto prealloc`, which places the test in the `ioctl, rw, auto, prealloc` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`. Local helper surface: `_filter_resv`. Required capabilities: `_require_xfs_io_command "falloc"`; `_require_test`. External and harness commands observed in the full source include `xfs_io`, `feature`, `resvtest`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow creates or mutates files, directories, links, xattrs, ACLs, or quotas; runs XFS diagnostic or administrative tools; injects corruption, I/O failure, debug hooks, or log errors; compares generated state to expected output or filters nondeterminism. Observable progress/output points include `echo`; `echo "*** First case - I/O blocksize same as pagesize"`; `echo "*** Second case - 512 byte I/O blocksize"`. It relies primarily on the default fstests cleanup path.

## State And Persistence Behavior
The test mutates or inspects test filesystem paths/devices. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
intentionally corrupts metadata, so failures can be expected until repair or mount rejection checks run. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/084.out`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo`, `echo "*** First case - I/O blocksize same as pagesize"`, `echo "*** Second case - 512 byte I/O blocksize"`. The script has 49 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/084 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/085 -->
# sources/test-tools/xfstests/tests/xfs/085

## Purpose
`sources/test-tools/xfstests/tests/xfs/085` is a metadata corruption and repair regression test. Create and populate an XFS filesystem, corrupt a superblock, then see how the kernel and xfs_repair deal with it. The `_begin_fstest` declaration is `_begin_fstest fuzzers`, which places the test in the `fuzzers` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`, `. ./common/populate`. Local helper surface: no local helper functions beyond optional `_cleanup`. Required capabilities: `_require_scratch`; `_require_attrs`; `_require_populate_commands`; `_require_xfs_db_blocktrash_z_command`. External and harness commands observed in the full source include `xfs_db`, `xfs_repair`, `mkfs`, `mount`, `umount`, `chattr`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; runs XFS diagnostic or administrative tools; injects corruption, I/O failure, debug hooks, or log errors. Observable progress/output points include `echo "+ create scratch fs"`; `echo "+ mount fs image"`; `echo "+ make some files"`; `echo "+ check fs"`; `echo "+ corrupt image"`; `echo "+ mount image"`; `echo "+ repair fs"`; `echo "+ mount image (2)"`. It installs a custom `_cleanup` to tear down mounts/devices and remove temporary files.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
intentionally corrupts metadata, so failures can be expected until repair or mount rejection checks run; xfs_repair behavior and diagnostics are part of the oracle and may change across xfsprogs versions. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/085.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo "+ create scratch fs"`, `echo "+ mount fs image"`, `echo "+ make some files"`. The script has 91 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/085 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/086 -->
# sources/test-tools/xfstests/tests/xfs/086

## Purpose
`sources/test-tools/xfstests/tests/xfs/086` is a metadata corruption and repair regression test. Create and populate an XFS filesystem, corrupt an AGF, then see how the kernel and xfs_repair deal with it. The `_begin_fstest` declaration is `_begin_fstest fuzzers`, which places the test in the `fuzzers` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`, `. ./common/populate`. Local helper surface: no local helper functions beyond optional `_cleanup`. Required capabilities: `_require_scratch`; `_require_attrs`; `_require_populate_commands`; `_require_xfs_db_blocktrash_z_command`. External and harness commands observed in the full source include `xfs_db`, `xfs_repair`, `mkfs`, `mount`, `umount`, `chattr`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; runs XFS diagnostic or administrative tools; injects corruption, I/O failure, debug hooks, or log errors. Observable progress/output points include `echo "+ create scratch fs"`; `echo "+ mount fs image"`; `echo "+ make some files"`; `echo "+ check fs"`; `echo "+ corrupt image"`; `echo "+ mount image && modify files"`; `echo "+ repair fs"`; `echo "+ mount image"`. It installs a custom `_cleanup` to tear down mounts/devices and remove temporary files.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
intentionally corrupts metadata, so failures can be expected until repair or mount rejection checks run; xfs_repair behavior and diagnostics are part of the oracle and may change across xfsprogs versions. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/086.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo "+ create scratch fs"`, `echo "+ mount fs image"`, `echo "+ make some files"`. The script has 123 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/086 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/087 -->
# sources/test-tools/xfstests/tests/xfs/087

## Purpose
`sources/test-tools/xfstests/tests/xfs/087` is a metadata corruption and repair regression test. Create and populate an XFS filesystem, corrupt the AGI, then see how the kernel and xfs_repair deal with it. The `_begin_fstest` declaration is `_begin_fstest fuzzers`, which places the test in the `fuzzers` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`, `. ./common/populate`. Local helper surface: no local helper functions beyond optional `_cleanup`. Required capabilities: `_require_scratch`; `_require_attrs`; `_require_populate_commands`; `_require_xfs_db_blocktrash_z_command`. External and harness commands observed in the full source include `xfs_db`, `xfs_repair`, `mkfs`, `mount`, `umount`, `chattr`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; runs XFS diagnostic or administrative tools; injects corruption, I/O failure, debug hooks, or log errors. Observable progress/output points include `echo "+ create scratch fs"`; `echo "+ mount fs image"`; `echo "+ make some files"`; `echo "+ check fs"`; `echo "+ corrupt image"`; `echo "+ mount image && modify files"`; `echo "broken: ${broken}"`; `echo "+ repair fs"`. It installs a custom `_cleanup` to tear down mounts/devices and remove temporary files.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
intentionally corrupts metadata, so failures can be expected until repair or mount rejection checks run; xfs_repair behavior and diagnostics are part of the oracle and may change across xfsprogs versions. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/087.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo "+ create scratch fs"`, `echo "+ mount fs image"`, `echo "+ make some files"`. The script has 100 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/087 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/088 -->
# sources/test-tools/xfstests/tests/xfs/088

## Purpose
`sources/test-tools/xfstests/tests/xfs/088` is a metadata corruption and repair regression test. Create and populate an XFS filesystem, corrupt the AGFL, then see how the kernel and xfs_repair deal with it. The `_begin_fstest` declaration is `_begin_fstest fuzzers`, which places the test in the `fuzzers` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`, `. ./common/populate`. Local helper surface: no local helper functions beyond optional `_cleanup`. Required capabilities: `_require_scratch`; `_require_attrs`; `_require_populate_commands`; `_require_xfs_db_blocktrash_z_command`. External and harness commands observed in the full source include `xfs_db`, `xfs_repair`, `mkfs`, `mount`, `umount`, `chattr`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; runs XFS diagnostic or administrative tools; injects corruption, I/O failure, debug hooks, or log errors. Observable progress/output points include `echo "+ create scratch fs"`; `echo "+ mount fs image"`; `echo "+ make some files"`; `echo "+ check fs"`; `echo "+ corrupt image"`; `echo "+ mount image && modify files"`; `echo "+ repair fs"`; `echo "+ mount image"`. It installs a custom `_cleanup` to tear down mounts/devices and remove temporary files.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
intentionally corrupts metadata, so failures can be expected until repair or mount rejection checks run; xfs_repair behavior and diagnostics are part of the oracle and may change across xfsprogs versions. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/088.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo "+ create scratch fs"`, `echo "+ mount fs image"`, `echo "+ make some files"`. The script has 123 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/088 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/089 -->
# sources/test-tools/xfstests/tests/xfs/089

## Purpose
`sources/test-tools/xfstests/tests/xfs/089` is a metadata corruption and repair regression test. Create and populate an XFS filesystem, corrupt the bnobt, then see how the kernel and xfs_repair deal with it. The `_begin_fstest` declaration is `_begin_fstest fuzzers`, which places the test in the `fuzzers` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`, `. ./common/populate`. Local helper surface: no local helper functions beyond optional `_cleanup`. Required capabilities: `_require_scratch`; `_require_attrs`; `_require_populate_commands`; `_require_xfs_db_blocktrash_z_command`. External and harness commands observed in the full source include `xfs_db`, `xfs_repair`, `mkfs`, `mount`, `umount`, `chattr`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; runs XFS diagnostic or administrative tools; injects corruption, I/O failure, debug hooks, or log errors. Observable progress/output points include `echo "+ create scratch fs"`; `echo "+ mount fs image"`; `echo "+ make some files"`; `echo "+ check fs"`; `echo "+ corrupt image"`; `echo "+ mount image && modify files"`; `echo "+ repair fs"`; `echo "+ mount image"`. It installs a custom `_cleanup` to tear down mounts/devices and remove temporary files.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
intentionally corrupts metadata, so failures can be expected until repair or mount rejection checks run; xfs_repair behavior and diagnostics are part of the oracle and may change across xfsprogs versions. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/089.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo "+ create scratch fs"`, `echo "+ mount fs image"`, `echo "+ make some files"`. The script has 124 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/089 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/090 -->
# sources/test-tools/xfstests/tests/xfs/090

## Purpose
`sources/test-tools/xfstests/tests/xfs/090` is a realtime geometry/allocation regression test. Exercise IO on the realtime device (direct, buffered, mmapd) The `_begin_fstest` declaration is `_begin_fstest rw auto realtime mmap`, which places the test in the `rw, auto, realtime, mmap` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`. Local helper surface: `_filter_io`, `_create_scratch`, `realtime_direct_aligned`, `realtime_buffer_aligned`, `realtime_buffer_unaligned`, `realtime_mmap_unaligned`. Required capabilities: `_require_realtime`; `_require_scratch`. External and harness commands observed in the full source include `mkfs`, `mount`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; uses loop, realtime, external log, idmapped, or reflink devices; compares generated state to expected output or filters nondeterminism. Observable progress/output points include `echo "*** mkfs"`; `echo "failed to mkfs $SCRATCH_DEV"`; `echo "*** mount"`; `echo "failed to mount $SCRATCH_DEV"`; `echo direct realtime writes, 4 files, 2m each, increasing offsets.`; `echo buffered realtime writes, 4 files, 2m each, increasing offsets.`; `echo buffered realtime writes, 4 files, unaligned byte offsets/sizes.`. It relies primarily on the default fstests cleanup path.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents, realtime device geometry and allocation state. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
requires a valid realtime test configuration and exact extent-size alignment. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/090.out`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo "*** mkfs"`, `echo "failed to mkfs $SCRATCH_DEV"`, `echo "*** mount"`. The script has 101 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/090 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/091 -->
# sources/test-tools/xfstests/tests/xfs/091

## Purpose
`sources/test-tools/xfstests/tests/xfs/091` is a metadata corruption and repair regression test. Create and populate an XFS filesystem, corrupt the cntbt, then see how the kernel and xfs_repair deal with it. The `_begin_fstest` declaration is `_begin_fstest fuzzers`, which places the test in the `fuzzers` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`, `. ./common/populate`. Local helper surface: no local helper functions beyond optional `_cleanup`. Required capabilities: `_require_scratch`; `_require_attrs`; `_require_populate_commands`; `_require_xfs_db_blocktrash_z_command`. External and harness commands observed in the full source include `xfs_db`, `xfs_repair`, `mkfs`, `mount`, `umount`, `chattr`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; runs XFS diagnostic or administrative tools; injects corruption, I/O failure, debug hooks, or log errors. Observable progress/output points include `echo "+ create scratch fs"`; `echo "+ mount fs image"`; `echo "+ make some files"`; `echo "+ check fs"`; `echo "+ corrupt image"`; `echo "+ mount image && modify files"`; `echo "+ repair fs"`; `echo "+ mount image"`. It installs a custom `_cleanup` to tear down mounts/devices and remove temporary files.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
intentionally corrupts metadata, so failures can be expected until repair or mount rejection checks run; xfs_repair behavior and diagnostics are part of the oracle and may change across xfsprogs versions. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/091.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo "+ create scratch fs"`, `echo "+ mount fs image"`, `echo "+ make some files"`. The script has 124 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/091 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/092 -->
# sources/test-tools/xfstests/tests/xfs/092

## Purpose
`sources/test-tools/xfstests/tests/xfs/092` is a XFS functional regression test. Make sure that we can mount inode64 filesystems The `_begin_fstest` declaration is `_begin_fstest other auto quick`, which places the test in the `other, auto, quick` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`. Local helper surface: no local helper functions beyond optional `_cleanup`. Required capabilities: `_require_scratch`; `_require_no_large_scratch_dev`. External and harness commands observed in the full source include `mkfs`, `mount`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; compares generated state to expected output or filters nondeterminism. Observable progress/output points include `echo Silence is golden`. It relies primarily on the default fstests cleanup path.

## State And Persistence Behavior
The test mutates or inspects filesystem metadata and command output only. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
relies on fstests environment variables, scratch/test device hygiene, and filtered golden output remaining stable. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/092.out`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo Silence is golden`. The script has 29 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/092 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/093 -->
# sources/test-tools/xfstests/tests/xfs/093

## Purpose
`sources/test-tools/xfstests/tests/xfs/093` is a metadata corruption and repair regression test. Create and populate an XFS filesystem, corrupt the inobt, then see how the kernel and xfs_repair deal with it. The `_begin_fstest` declaration is `_begin_fstest fuzzers`, which places the test in the `fuzzers` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`, `. ./common/populate`. Local helper surface: no local helper functions beyond optional `_cleanup`. Required capabilities: `_require_scratch`; `_require_attrs`; `_require_populate_commands`; `_require_xfs_db_blocktrash_z_command`. External and harness commands observed in the full source include `xfs_db`, `xfs_repair`, `mkfs`, `mount`, `umount`, `chattr`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; runs XFS diagnostic or administrative tools; injects corruption, I/O failure, debug hooks, or log errors. Observable progress/output points include `echo "+ create scratch fs"`; `echo "+ mount fs image"`; `echo "+ make some files"`; `echo "+ check fs"`; `echo "+ corrupt image"`; `echo "+ mount image && modify files"`; `echo "broken: ${broken}"`; `echo "+ repair fs"`. It installs a custom `_cleanup` to tear down mounts/devices and remove temporary files.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
intentionally corrupts metadata, so failures can be expected until repair or mount rejection checks run; xfs_repair behavior and diagnostics are part of the oracle and may change across xfsprogs versions. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/093.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo "+ create scratch fs"`, `echo "+ mount fs image"`, `echo "+ make some files"`. The script has 103 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/093 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/094 -->
# sources/test-tools/xfstests/tests/xfs/094

## Purpose
`sources/test-tools/xfstests/tests/xfs/094` is a realtime geometry/allocation regression test. Exercising the inheritable realtime inode bit. The `_begin_fstest` declaration is `_begin_fstest metadata dir ioctl auto realtime`, which places the test in the `metadata, dir, ioctl, auto, realtime` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`. Local helper surface: `_filter_realtime_flag`, `_filter_rtinherit_flag`, `_create_scratch`. Required capabilities: `_require_realtime`; `_require_scratch`. External and harness commands observed in the full source include `mkfs`, `mount`, `chattr`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; uses loop, realtime, external log, idmapped, or reflink devices; compares generated state to expected output or filters nondeterminism. Observable progress/output points include `echo "--r-- SCRATCH_MNT/testdir/$1"`; `echo "----- SCRATCH_MNT/testdir/$1"`; `echo "--t-- SCRATCH_MNT/testdir"`; `echo "----- SCRATCH_MNT/testdir"`; `echo "*** mkfs"`; `echo "failed to mkfs $SCRATCH_DEV"`; `echo "*** mount"`; `echo "failed to mount $SCRATCH_DEV"`. It relies primarily on the default fstests cleanup path.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents, realtime device geometry and allocation state. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
requires a valid realtime test configuration and exact extent-size alignment. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/094.out`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo "--r-- SCRATCH_MNT/testdir/$1"`, `echo "----- SCRATCH_MNT/testdir/$1"`, `echo "--t-- SCRATCH_MNT/testdir"`. The script has 82 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/094 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/095 -->
# sources/test-tools/xfstests/tests/xfs/095

## Purpose
`sources/test-tools/xfstests/tests/xfs/095` is a log recovery/error-injection test. Test upgrading the XFS log to v2 The `_begin_fstest` declaration is `_begin_fstest log v2log auto`, which places the test in the `log, v2log, auto` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`, `. ./common/log`. Local helper surface: no local helper functions beyond optional `_cleanup`. Required capabilities: `_require_scratch`; `_require_v2log`; `_require_xfs_nocrc`. External and harness commands observed in the full source include `xfs_db`, `mkfs`, `mount`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; runs XFS diagnostic or administrative tools; compares generated state to expected output or filters nondeterminism. Observable progress/output points include the expected-output oracle is mostly delegated to helper functions and companion output files. It relies primarily on the default fstests cleanup path.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents, journal/log metadata. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
depends on kernel log recovery/error-injection behavior and can expose kernel bugs or require debug facilities. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/095.out`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks. The script has 41 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/095 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/096 -->
# sources/test-tools/xfstests/tests/xfs/096

## Purpose
`sources/test-tools/xfstests/tests/xfs/096` is a quota/accounting regression test. test xfs_quota state command (XFS v4 version) The `_begin_fstest` declaration is `_begin_fstest auto quick quota`, which places the test in the `auto, quick, quota` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`, `. ./common/quota`. Local helper surface: `option_string`, `filter_quota_state`, `filter_quota_state2`, `test_all_state`. Required capabilities: `_require_scratch`; `_require_xfs_quota`; `_require_xfs_nocrc`. External and harness commands observed in the full source include `xfs_quota`, `mkfs`, `mount`, `quota`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; compares generated state to expected output or filters nondeterminism. Observable progress/output points include `echo $OPT`; `echo "== Options: $OPTIONS =="`. It relies primarily on the default fstests cleanup path.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents, quota accounting records and limits. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
quota results vary with block size, delayed allocation, mount options, and configured test users/groups/projects; requires a valid realtime test configuration and exact extent-size alignment. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/096.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo $OPT`, `echo "== Options: $OPTIONS =="`. The script has 77 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/096 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/097 -->
# sources/test-tools/xfstests/tests/xfs/097

## Purpose
`sources/test-tools/xfstests/tests/xfs/097` is a metadata corruption and repair regression test. Create and populate an XFS filesystem, corrupt the finobt, then see how the kernel and xfs_repair deal with it. The `_begin_fstest` declaration is `_begin_fstest fuzzers`, which places the test in the `fuzzers` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`, `. ./common/populate`. Local helper surface: no local helper functions beyond optional `_cleanup`. Required capabilities: `_require_scratch`; `_require_xfs_mkfs_finobt`; `_require_xfs_finobt`; `_require_attrs`; `_require_populate_commands`; `_require_xfs_db_blocktrash_z_command`; `_require_xfs_has_feature "$SCRATCH_MNT" finobt`. External and harness commands observed in the full source include `xfs_db`, `xfs_repair`, `mkfs`, `mount`, `umount`, `chattr`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; runs XFS diagnostic or administrative tools; injects corruption, I/O failure, debug hooks, or log errors. Observable progress/output points include `echo "+ create scratch fs"`; `echo "+ mount fs image"`; `echo "+ make some files"`; `echo "+ check fs"`; `echo "+ corrupt image"`; `echo "+ mount image && modify files"`; `echo "broken: ${broken}"`; `echo "+ repair fs"`. It installs a custom `_cleanup` to tear down mounts/devices and remove temporary files.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
intentionally corrupts metadata, so failures can be expected until repair or mount rejection checks run; xfs_repair behavior and diagnostics are part of the oracle and may change across xfsprogs versions. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/097.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo "+ create scratch fs"`, `echo "+ mount fs image"`, `echo "+ make some files"`. The script has 102 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/097 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/098 -->
# sources/test-tools/xfstests/tests/xfs/098

## Purpose
`sources/test-tools/xfstests/tests/xfs/098` is a metadata corruption and repair regression test. Create and populate an XFS filesystem, corrupt the journal, then see how the kernel and xfs_repair deal with it. The `_begin_fstest` declaration is `_begin_fstest fuzzers`, which places the test in the `fuzzers` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`, `. ./common/populate`. Local helper surface: no local helper functions beyond optional `_cleanup`. Required capabilities: `_require_no_xfs_bug_on_assert`; `_require_scratch`; `_require_attrs`; `_require_populate_commands`; `_require_xfs_db_blocktrash_z_command`. External and harness commands observed in the full source include `xfs_db`, `xfs_repair`, `mkfs`, `mount`, `umount`, `chattr`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; runs XFS diagnostic or administrative tools; injects corruption, I/O failure, debug hooks, or log errors; uses loop, realtime, external log, idmapped, or reflink devices; compares generated state to expected output or filters nondeterminism. Observable progress/output points include `echo "+ create scratch fs"`; `echo "+ mount fs image"`; `echo "+ make some files"`; `echo "+ check fs"`; `echo "+ corrupt image"`; `echo "+ mount image"`; `echo "+ repair fs"`; `echo "+ mount image (2)"`. It installs a custom `_cleanup` to tear down mounts/devices and remove temporary files.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
intentionally corrupts metadata, so failures can be expected until repair or mount rejection checks run; loop/external-device cleanup must be reliable to avoid leaking mounts or loop devices; xfs_repair behavior and diagnostics are part of the oracle and may change across xfsprogs versions. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/098.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo "+ create scratch fs"`, `echo "+ mount fs image"`, `echo "+ make some files"`. The script has 107 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/098 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/099 -->
# sources/test-tools/xfstests/tests/xfs/099

## Purpose
`sources/test-tools/xfstests/tests/xfs/099` is a metadata corruption and repair regression test. Create and populate an XFS filesystem, corrupt a block directory, then see how the kernel and xfs_repair deal with it. The `_begin_fstest` declaration is `_begin_fstest fuzzers`, which places the test in the `fuzzers` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`, `. ./common/populate`. Local helper surface: no local helper functions beyond optional `_cleanup`. Required capabilities: `_require_scratch`; `_require_attrs`; `_require_populate_commands`; `_require_xfs_db_blocktrash_z_command`. External and harness commands observed in the full source include `xfs_db`, `xfs_repair`, `mkfs`, `mount`, `umount`, `chattr`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; runs XFS diagnostic or administrative tools; injects corruption, I/O failure, debug hooks, or log errors. Observable progress/output points include `echo "+ create scratch fs"`; `echo "+ mount fs image"`; `echo "+ make some files"`; `echo "+ check fs"`; `echo "+ check dir"`; `echo "+ corrupt dir"`; `echo "+ mount image && modify dir"`; `echo "+ repair fs"`. It installs a custom `_cleanup` to tear down mounts/devices and remove temporary files.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
intentionally corrupts metadata, so failures can be expected until repair or mount rejection checks run; xfs_repair behavior and diagnostics are part of the oracle and may change across xfsprogs versions. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/099.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo "+ create scratch fs"`, `echo "+ mount fs image"`, `echo "+ make some files"`. The script has 86 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/099 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/100 -->
# sources/test-tools/xfstests/tests/xfs/100

## Purpose
`sources/test-tools/xfstests/tests/xfs/100` is a metadata corruption and repair regression test. Create and populate an XFS filesystem, corrupt a leaf directory's data extent, then see how the kernel and xfs_repair deal with it. The `_begin_fstest` declaration is `_begin_fstest fuzzers`, which places the test in the `fuzzers` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`, `. ./common/populate`. Local helper surface: no local helper functions beyond optional `_cleanup`. Required capabilities: `_require_scratch`; `_require_attrs`; `_require_populate_commands`; `_require_xfs_db_blocktrash_z_command`. External and harness commands observed in the full source include `xfs_db`, `xfs_repair`, `mkfs`, `mount`, `umount`, `chattr`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; runs XFS diagnostic or administrative tools; injects corruption, I/O failure, debug hooks, or log errors; compares generated state to expected output or filters nondeterminism. Observable progress/output points include `echo "+ create scratch fs"`; `echo "+ mount fs image"`; `echo "+ make some files"`; `echo "+ check fs"`; `echo "+ check dir"`; `echo "+ corrupt dir"`; `echo "+ mount image && modify dir"`; `echo "+ repair fs"`. It installs a custom `_cleanup` to tear down mounts/devices and remove temporary files.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
intentionally corrupts metadata, so failures can be expected until repair or mount rejection checks run; xfs_repair behavior and diagnostics are part of the oracle and may change across xfsprogs versions. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/100.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo "+ create scratch fs"`, `echo "+ mount fs image"`, `echo "+ make some files"`. The script has 91 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/100 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/101 -->
# sources/test-tools/xfstests/tests/xfs/101

## Purpose
`sources/test-tools/xfstests/tests/xfs/101` is a metadata corruption and repair regression test. Create and populate an XFS filesystem, corrupt a leaf directory's leaf extent, then see how the kernel and xfs_repair deal with it. The `_begin_fstest` declaration is `_begin_fstest fuzzers`, which places the test in the `fuzzers` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`, `. ./common/populate`. Local helper surface: no local helper functions beyond optional `_cleanup`. Required capabilities: `_require_scratch`; `_require_attrs`; `_require_populate_commands`; `_require_xfs_db_blocktrash_z_command`. External and harness commands observed in the full source include `xfs_db`, `xfs_repair`, `mkfs`, `mount`, `umount`, `chattr`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; runs XFS diagnostic or administrative tools; injects corruption, I/O failure, debug hooks, or log errors. Observable progress/output points include `echo "+ create scratch fs"`; `echo "+ mount fs image"`; `echo "+ make some files"`; `echo "+ check fs"`; `echo "+ check dir"`; `echo "+ corrupt dir"`; `echo "+ mount image && modify dir"`; `echo "+ repair fs"`. It installs a custom `_cleanup` to tear down mounts/devices and remove temporary files.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
intentionally corrupts metadata, so failures can be expected until repair or mount rejection checks run; xfs_repair behavior and diagnostics are part of the oracle and may change across xfsprogs versions. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/101.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo "+ create scratch fs"`, `echo "+ mount fs image"`, `echo "+ make some files"`. The script has 86 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/101 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/102 -->
# sources/test-tools/xfstests/tests/xfs/102

## Purpose
`sources/test-tools/xfstests/tests/xfs/102` is a metadata corruption and repair regression test. Create and populate an XFS filesystem, corrupt a node directory's data extent, then see how the kernel and xfs_repair deal with it. The `_begin_fstest` declaration is `_begin_fstest fuzzers`, which places the test in the `fuzzers` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`, `. ./common/populate`. Local helper surface: no local helper functions beyond optional `_cleanup`. Required capabilities: `_require_scratch`; `_require_attrs`; `_require_populate_commands`; `_require_xfs_db_blocktrash_z_command`. External and harness commands observed in the full source include `xfs_db`, `xfs_repair`, `mkfs`, `mount`, `umount`, `chattr`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; runs XFS diagnostic or administrative tools; injects corruption, I/O failure, debug hooks, or log errors; compares generated state to expected output or filters nondeterminism. Observable progress/output points include `echo "+ create scratch fs"`; `echo "+ mount fs image"`; `echo "+ make some files"`; `echo "+ check fs"`; `echo "+ check dir"`; `echo "+ corrupt dir"`; `echo "+ mount image && modify dir"`; `echo "+ repair fs"`. It installs a custom `_cleanup` to tear down mounts/devices and remove temporary files.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
intentionally corrupts metadata, so failures can be expected until repair or mount rejection checks run; xfs_repair behavior and diagnostics are part of the oracle and may change across xfsprogs versions. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/102.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo "+ create scratch fs"`, `echo "+ mount fs image"`, `echo "+ make some files"`. The script has 91 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/102 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/103 -->
# sources/test-tools/xfstests/tests/xfs/103

## Purpose
`sources/test-tools/xfstests/tests/xfs/103` is a XFS functional regression test. Exercise the XFS nosymlinks inode flag The `_begin_fstest` declaration is `_begin_fstest metadata dir ioctl auto quick`, which places the test in the `metadata, dir, ioctl, auto, quick` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`. Local helper surface: `_create_scratch`, `_filter_noymlinks_flag`. Required capabilities: `_require_scratch`. External and harness commands observed in the full source include `mkfs`, `mount`, `chattr`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; compares generated state to expected output or filters nondeterminism. Observable progress/output points include `echo "*** mkfs"`; `echo "failed to mkfs $SCRATCH_DEV"`; `echo "*** mount"`; `echo "failed to mount $SCRATCH_DEV"`; `echo "--n-- SCRATCH_MNT/nosymlink"`; `echo "----- SCRATCH_MNT/nosymlink"`; `echo "*** testing nosymlinks directories"`; `echo "*** setting nosymlinks bit"`. It relies primarily on the default fstests cleanup path.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
relies on fstests environment variables, scratch/test device hygiene, and filtered golden output remaining stable. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/103.out`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo "*** mkfs"`, `echo "failed to mkfs $SCRATCH_DEV"`, `echo "*** mount"`. The script has 74 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/103 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/104 -->
# sources/test-tools/xfstests/tests/xfs/104

## Purpose
`sources/test-tools/xfstests/tests/xfs/104` is a online growfs behavior test. XFS online growfs-while-allocating tests (data subvol variant) The `_begin_fstest` declaration is `_begin_fstest growfs ioctl prealloc auto stress`, which places the test in the `growfs, ioctl, prealloc, auto, stress` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`. Local helper surface: `create_scratch_sized`, `_fill_scratch`, `_stress_scratch`. Required capabilities: `_require_scratch`; `_require_xfs_io_command "falloc"`. External and harness commands observed in the full source include `xfs_io`, `xfs_growfs`, `mkfs`, `mount`, `fsstress`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; runs XFS diagnostic or administrative tools; compares generated state to expected output or filters nondeterminism. Observable progress/output points include `echo "*** mkfs"`; `echo "*** mount"`; `echo "failed to mount $SCRATCH_DEV"`; `echo "*** creating scratch filesystem"`; `echo "*** using some initial space on scratch filesystem"`; `echo "$out" | grep -q 'No space left on device' && continue`; `echo "*** stressing filesystem"`; `echo "*** stressing a ${sizeb} block filesystem" >> $seqres.full`. It relies primarily on the default fstests cleanup path.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
relies on fstests environment variables, scratch/test device hygiene, and filtered golden output remaining stable. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/104.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo "*** mkfs"`, `echo "*** mount"`, `echo "failed to mount $SCRATCH_DEV"`. The script has 95 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/104 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/105 -->
# sources/test-tools/xfstests/tests/xfs/105

## Purpose
`sources/test-tools/xfstests/tests/xfs/105` is a metadata corruption and repair regression test. Create and populate an XFS filesystem, corrupt a node directory's leaf extent, then see how the kernel and xfs_repair deal with it. The `_begin_fstest` declaration is `_begin_fstest fuzzers`, which places the test in the `fuzzers` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`, `. ./common/populate`. Local helper surface: no local helper functions beyond optional `_cleanup`. Required capabilities: `_require_scratch`; `_require_attrs`; `_require_populate_commands`; `_require_xfs_db_blocktrash_z_command`. External and harness commands observed in the full source include `xfs_db`, `xfs_repair`, `mkfs`, `mount`, `umount`, `chattr`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; runs XFS diagnostic or administrative tools; injects corruption, I/O failure, debug hooks, or log errors; compares generated state to expected output or filters nondeterminism. Observable progress/output points include `echo "+ create scratch fs"`; `echo "+ mount fs image"`; `echo "+ make some files"`; `echo "+ check fs"`; `echo "+ check dir"`; `echo "+ corrupt dir"`; `echo "+ mount image && modify dir"`; `echo "+ repair fs"`. It installs a custom `_cleanup` to tear down mounts/devices and remove temporary files.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
intentionally corrupts metadata, so failures can be expected until repair or mount rejection checks run; xfs_repair behavior and diagnostics are part of the oracle and may change across xfsprogs versions. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/105.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo "+ create scratch fs"`, `echo "+ mount fs image"`, `echo "+ make some files"`. The script has 91 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/105 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/106 -->
# sources/test-tools/xfstests/tests/xfs/106

## Purpose
`sources/test-tools/xfstests/tests/xfs/106` is a quota/accounting regression test. Exercise basic xfs_quota functionality (user/group/project quota) Use of "sync" mount option here is an attempt to get deterministic allocator behaviour. The `_begin_fstest` declaration is `_begin_fstest auto quick quota`, which places the test in the `auto, quick, quota` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`, `. ./common/quota`. Local helper surface: `create_files`, `clean_files`, `filter_quot`, `filter_report`, `filter_quota`, `filter_state`, `test_quot`, `test_report`, `test_quota`, `test_limit`, `test_timer`, `test_disable`, `test_enable`, `test_off`, `test_remove`, `test_state`, `test_dump`, `test_restore`, `test_xfs_quota`. Required capabilities: `_require_scratch`; `_require_xfs_quota`; `_require_user`; `_require_group`; `_require_prjquota $SCRATCH_DEV`. External and harness commands observed in the full source include `xfs_quota`, `mkfs`, `mount`, `quota`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; compares generated state to expected output or filters nondeterminism. Observable progress/output points include `echo "Using type=$type id=$id" >> $seqres.full`; `echo "checking quot command (type=$type)"`; `echo "checking report command (type=$type)"`; `echo "checking quota command (type=$type)"`; `echo "checking limit command (type=$type, bsoft=$bs, bhard=$bh, isoft=$is, ihard=$ih)"`; `echo "checking timer command (type=$type)"`; `echo "checking disable command (type=$type)"`; `echo "checking enable command (type=$type)"`. It relies primarily on the default fstests cleanup path.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents, quota accounting records and limits. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
quota results vary with block size, delayed allocation, mount options, and configured test users/groups/projects. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/106.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo "Using type=$type id=$id" >> $seqres.full`, `echo "checking quot command (type=$type)"`, `echo "checking report command (type=$type)"`. The script has 293 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/106 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/107 -->
# sources/test-tools/xfstests/tests/xfs/107

## Purpose
`sources/test-tools/xfstests/tests/xfs/107` is a XFS functional regression test. Regression test for commit: 983d8e60f508 ("xfs: map unwritten blocks in XFS_IOC_{ALLOC,FREE}SP just like fallocate") The `_begin_fstest` declaration is `_begin_fstest auto quick prealloc`, which places the test in the `auto, quick, prealloc` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`. Local helper surface: no local helper functions beyond optional `_cleanup`. Required capabilities: `_require_test`; `_require_scratch`; `_require_xfs_io_command allocsp		# detect presence of ALLOCSP ioctl`; `_require_test_program allocstale`. External and harness commands observed in the full source include `xfs_io`, `mkfs`, `mount`, `allocstale`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; runs XFS diagnostic or administrative tools. Observable progress/output points include `echo "Setting up $iterations runs for block size $blksz" >> $seqres.full`; `echo Silence is golden`. It relies primarily on the default fstests cleanup path.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
relies on fstests environment variables, scratch/test device hygiene, and filtered golden output remaining stable. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/107.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo "Setting up $iterations runs for block size $blksz" >> $seqres.full`, `echo Silence is golden`. The script has 60 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/107 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/108 -->
# sources/test-tools/xfstests/tests/xfs/108

## Purpose
`sources/test-tools/xfstests/tests/xfs/108` is a quota/accounting regression test. Simple quota accounting test for direct/buffered/mmap IO. The `_begin_fstest` declaration is `_begin_fstest quota auto quick mmap`, which places the test in the `quota, auto, quick, mmap` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`, `. ./common/quota`. Local helper surface: `test_files`, `filter_quota`, `test_accounting`. Required capabilities: `_require_scratch`; `_require_xfs_quota`; `_require_xfs_io_command "syncfs"`; `_require_prjquota $SCRATCH_DEV`. External and harness commands observed in the full source include `xfs_quota`, `xfs_io`, `mkfs`, `mount`, `quota`, `lstat64`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; runs XFS diagnostic or administrative tools; compares generated state to expected output or filters nondeterminism. Observable progress/output points include `echo; echo "### create files, setting up ownership (type=$type)"`; `echo "### some controlled buffered, direct and mmapd IO (type=$type)"`; `echo "--- initiating parallel IO..." >>$seqres.full`; `echo "--- completed parallel IO ($type)" >>$seqres.full`; `echo; echo "### test user accounting"`; `echo; echo "### test group accounting"`. It relies primarily on the default fstests cleanup path.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents, quota accounting records and limits. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
quota results vary with block size, delayed allocation, mount options, and configured test users/groups/projects. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/108.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo; echo "### create files, setting up ownership (type=$type)"`, `echo "### some controlled buffered, direct and mmapd IO (type=$type)"`, `echo "--- initiating parallel IO..." >>$seqres.full`. The script has 110 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/108 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/109 -->
# sources/test-tools/xfstests/tests/xfs/109

## Purpose
`sources/test-tools/xfstests/tests/xfs/109` is a XFS functional regression test. ENOSPC deadlock case from Asano Masahiro. The `_begin_fstest` declaration is `_begin_fstest metadata auto`, which places the test in the `metadata, auto` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`. Local helper surface: `populate`, `allocate`. Required capabilities: `_require_scratch`. External and harness commands observed in the full source include `mkfs`, `mount`, `umount`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; compares generated state to expected output or filters nondeterminism. Observable progress/output points include `echo "creating small files..."`; `echo "removing small files..."`; `echo "flushing changes via umount/mount."`; `echo "starting parallel allocators..."`; `echo "all done!"`. It relies primarily on the default fstests cleanup path.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
relies on fstests environment variables, scratch/test device hygiene, and filtered golden output remaining stable. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/109.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo "creating small files..."`, `echo "removing small files..."`, `echo "flushing changes via umount/mount."`. The script has 85 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/109 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/110 -->
# sources/test-tools/xfstests/tests/xfs/110

## Purpose
`sources/test-tools/xfstests/tests/xfs/110` is a xfs_repair regression test. Incorrect dir2 freetab warning case from Masanori Tsuda. The `_begin_fstest` declaration is `_begin_fstest repair auto`, which places the test in the `repair, auto` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`. Local helper surface: no local helper functions beyond optional `_cleanup`. Required capabilities: `_require_scratch`. External and harness commands observed in the full source include `mkfs`, `mount`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; compares generated state to expected output or filters nondeterminism. Observable progress/output points include `echo > $SCRATCH_MNT/test/${STR1}${STR2}${STR3}${I}`. It relies primarily on the default fstests cleanup path.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
xfs_repair behavior and diagnostics are part of the oracle and may change across xfsprogs versions. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/110.out`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo > $SCRATCH_MNT/test/${STR1}${STR2}${STR3}${I}`. The script has 58 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/110 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/111 -->
# sources/test-tools/xfstests/tests/xfs/111

## Purpose
`sources/test-tools/xfstests/tests/xfs/111` is a XFS functional regression test. Infinite xfs_bulkstat bad-inode loop case from Roger Willcocks. The `_begin_fstest` declaration is `_begin_fstest ioctl`, which places the test in the `ioctl` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`. Local helper surface: no local helper functions beyond optional `_cleanup`. Required capabilities: `_require_scratch`. External and harness commands observed in the full source include `xfs_fsr`, `xfs_db`, `xfs_repair`, `mkfs`, `mount`, `bstat`, `itrash`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; runs XFS diagnostic or administrative tools; injects corruption, I/O failure, debug hooks, or log errors; uses loop, realtime, external log, idmapped, or reflink devices; compares generated state to expected output or filters nondeterminism. Observable progress/output points include `echo Create some files`; `echo Blat inode clusters`; `echo Attempting bulkstat`. It relies primarily on the default fstests cleanup path.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents, loop device mappings. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
intentionally corrupts metadata, so failures can be expected until repair or mount rejection checks run; loop/external-device cleanup must be reliable to avoid leaking mounts or loop devices; xfs_repair behavior and diagnostics are part of the oracle and may change across xfsprogs versions. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/111.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo Create some files`, `echo Blat inode clusters`, `echo Attempting bulkstat`. The script has 55 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/111 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/112 -->
# sources/test-tools/xfstests/tests/xfs/112

## Purpose
`sources/test-tools/xfstests/tests/xfs/112` is a metadata corruption and repair regression test. Create and populate an XFS filesystem, corrupt a node directory's freeindex extent, then see how the kernel and xfs_repair deal with it. The `_begin_fstest` declaration is `_begin_fstest fuzzers`, which places the test in the `fuzzers` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`, `. ./common/populate`. Local helper surface: no local helper functions beyond optional `_cleanup`. Required capabilities: `_require_scratch`; `_require_attrs`; `_require_populate_commands`; `_require_xfs_db_blocktrash_z_command`. External and harness commands observed in the full source include `xfs_db`, `xfs_repair`, `mkfs`, `mount`, `umount`, `chattr`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; runs XFS diagnostic or administrative tools; injects corruption, I/O failure, debug hooks, or log errors; compares generated state to expected output or filters nondeterminism. Observable progress/output points include `echo "+ create scratch fs"`; `echo "+ mount fs image"`; `echo "+ make some files"`; `echo "+ check fs"`; `echo "+ check dir"`; `echo "+ corrupt dir"`; `echo "+ mount image && modify dir"`; `echo "+ repair fs"`. It installs a custom `_cleanup` to tear down mounts/devices and remove temporary files.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
intentionally corrupts metadata, so failures can be expected until repair or mount rejection checks run; xfs_repair behavior and diagnostics are part of the oracle and may change across xfsprogs versions. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/112.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo "+ create scratch fs"`, `echo "+ mount fs image"`, `echo "+ make some files"`. The script has 95 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/112 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/113 -->
# sources/test-tools/xfstests/tests/xfs/113

## Purpose
`sources/test-tools/xfstests/tests/xfs/113` is a metadata corruption and repair regression test. Create and populate an XFS filesystem, corrupt a btree directory's data extent, then see how the kernel and xfs_repair deal with it. The `_begin_fstest` declaration is `_begin_fstest fuzzers`, which places the test in the `fuzzers` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`, `. ./common/populate`. Local helper surface: `dir_data_offsets`. Required capabilities: `_require_scratch`; `_require_attrs`; `_require_populate_commands`; `_require_xfs_db_blocktrash_z_command`. External and harness commands observed in the full source include `xfs_db`, `xfs_repair`, `mkfs`, `mount`, `umount`, `chattr`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; runs XFS diagnostic or administrative tools; injects corruption, I/O failure, debug hooks, or log errors. Observable progress/output points include `echo "+ create scratch fs"`; `echo "+ mount fs image"`; `echo "+ make some files"`; `echo "+ check fs"`; `echo "+ check dir"`; `echo "+ corrupt dir"`; `echo "+ mount image && modify dir"`; `echo "+ repair fs"`. It installs a custom `_cleanup` to tear down mounts/devices and remove temporary files.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
intentionally corrupts metadata, so failures can be expected until repair or mount rejection checks run; xfs_repair behavior and diagnostics are part of the oracle and may change across xfsprogs versions. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/113.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo "+ create scratch fs"`, `echo "+ mount fs image"`, `echo "+ make some files"`. The script has 112 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/113 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/114 -->
# sources/test-tools/xfstests/tests/xfs/114

## Purpose
`sources/test-tools/xfstests/tests/xfs/114` is a reflink/refcount stress test. Make sure that we can handle insert-range followed by collapse-range. In particular, make sure that fcollapse works for rmap when the extents on either side of the collapse area are mergeable. The `_begin_fstest` declaration is `_begin_fstest auto quick clone rmap collapse insert prealloc`, which places the test in the `auto, quick, clone, rmap, collapse, insert, prealloc` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`. Local helper surface: no local helper functions beyond optional `_cleanup`. Required capabilities: `_require_test_program "punch-alternating"`; `_require_cp_reflink`; `_require_scratch_reflink`; `_require_xfs_scratch_rmapbt`; `_require_xfs_io_command "falloc"`; `_require_xfs_io_command "fcollapse"`; `_require_xfs_io_command "finsert"`; `_require_congruent_file_oplen $SCRATCH_MNT $blksz`. External and harness commands observed in the full source include `xfs_io`, `mkfs`, `mount`, `punch-alternating`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; runs XFS diagnostic or administrative tools; uses loop, realtime, external log, idmapped, or reflink devices; compares generated state to expected output or filters nondeterminism. Observable progress/output points include `echo "Format and mount"`; `echo "Create some files"`; `echo "Insert and write file range"`; `echo "f1 bmap" >> $seqres.full`; `echo "f2 bmap" >> $seqres.full`; `echo "fsmap" >> $seqres.full`; `echo "Remount"`; `echo "Collapse file"`. It relies primarily on the default fstests cleanup path.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
relies on fstests environment variables, scratch/test device hygiene, and filtered golden output remaining stable. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/114.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo "Format and mount"`, `echo "Create some files"`, `echo "Insert and write file range"`. The script has 107 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/114 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/115 -->
# sources/test-tools/xfstests/tests/xfs/115

## Purpose
`sources/test-tools/xfstests/tests/xfs/115` is a metadata corruption and repair regression test. Check if the filesystem will lockup when trying to allocate a new inode in an AG with no free inodes but with a corrupted agi->freecount showing free inodes. At the end of the test, the scratch device will purposely be in a corrupted state, so there is no need for checking that. The `_begin_fstest` declaration is `_begin_fstest auto quick fuzzers`, which places the test in the `auto, quick, fuzzers` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`. Local helper surface: no local helper functions beyond optional `_cleanup`. Required capabilities: `_require_scratch_nocheck`; `_require_no_xfs_bug_on_assert`. External and harness commands observed in the full source include `xfs_db`, `mkfs`, `mount`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; runs XFS diagnostic or administrative tools; injects corruption, I/O failure, debug hooks, or log errors; compares generated state to expected output or filters nondeterminism. Observable progress/output points include `echo "Silence is golden"`. It relies primarily on the default fstests cleanup path.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
intentionally corrupts metadata, so failures can be expected until repair or mount rejection checks run. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/115.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo "Silence is golden"`. The script has 54 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/115 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/116 -->
# sources/test-tools/xfstests/tests/xfs/116

## Purpose
`sources/test-tools/xfstests/tests/xfs/116` is a quota/accounting regression test. pv#940491 Test out resetting of sb_qflags when mounting with no quotas after having mounted with quotas. The `_begin_fstest` declaration is `_begin_fstest quota auto quick`, which places the test in the `quota, auto, quick` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`, `. ./common/quota`. Local helper surface: no local helper functions beyond optional `_cleanup`. Required capabilities: `_require_scratch`; `_require_xfs_quota`. External and harness commands observed in the full source include `xfs_quota`, `xfs_db`, `mkfs`, `mount`, `quota`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; runs XFS diagnostic or administrative tools; compares generated state to expected output or filters nondeterminism. Observable progress/output points include the expected-output oracle is mostly delegated to helper functions and companion output files. It relies primarily on the default fstests cleanup path.

## State And Persistence Behavior
The test mutates or inspects quota accounting records and limits. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
quota results vary with block size, delayed allocation, mount options, and configured test users/groups/projects. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks. The script has 47 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/116 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/117 -->
# sources/test-tools/xfstests/tests/xfs/117

## Purpose
`sources/test-tools/xfstests/tests/xfs/117` is a metadata corruption and repair regression test. Create and populate an XFS filesystem, corrupt an inode, then see how the kernel and xfs_repair deal with it. The `_begin_fstest` declaration is `_begin_fstest fuzzers`, which places the test in the `fuzzers` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`, `. ./common/populate`. Local helper surface: no local helper functions beyond optional `_cleanup`. Required capabilities: `_require_scratch`; `_require_attrs`; `_require_populate_commands`; `_require_xfs_db_blocktrash_z_command`. External and harness commands observed in the full source include `xfs_db`, `xfs_repair`, `mkfs`, `mount`, `umount`, `chattr`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; runs XFS diagnostic or administrative tools; injects corruption, I/O failure, debug hooks, or log errors. Observable progress/output points include `echo "+ create scratch fs"`; `echo "+ mount fs image"`; `echo "+ make some files"`; `echo "First victim inode is: " >> $seqres.full`; `echo "+ check fs"`; `echo "+ corrupt image"`; `echo "+ mount image && modify files"`; `echo "broken: ${broken}"`. It installs a custom `_cleanup` to tear down mounts/devices and remove temporary files.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
intentionally corrupts metadata, so failures can be expected until repair or mount rejection checks run; xfs_repair behavior and diagnostics are part of the oracle and may change across xfsprogs versions. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/117.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo "+ create scratch fs"`, `echo "+ mount fs image"`, `echo "+ make some files"`. The script has 119 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/117 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/118 -->
# sources/test-tools/xfstests/tests/xfs/118

## Purpose
`sources/test-tools/xfstests/tests/xfs/118` is a metadata corruption and repair regression test. Test xfs_fsr's handling of 2-extent files with preallocation An error in xfs_swap_extent_forks() incorrectly set up the temporary inode's if_extents pointer to inline, leading to in-memory corruption when the temporary inode was released and torn down; i_itemp and d_ops got overwritten with zeros, which led to an oops in xfs_trans_log_inode down the fput path. Fixed upstream by proper nextents counting using ip->i_df.if_bytes not ip->i_d.di_nextents in xfs_swap_extent_forks The `_begin_fstest` declaration is `_begin_fstest auto quick fsr prealloc`, which places the test in the `auto, quick, fsr, prealloc` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`. Local helper surface: no local helper functions beyond optional `_cleanup`. Required capabilities: `_require_scratch`; `_require_command "$XFS_FSR_PROG" "xfs_fsr"`; `_require_xfs_io_command "falloc"`. External and harness commands observed in the full source include `xfs_fsr`, `xfs_io`, `mkfs`, `mount`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; runs XFS diagnostic or administrative tools; injects corruption, I/O failure, debug hooks, or log errors; compares generated state to expected output or filters nondeterminism. Observable progress/output points include `echo "Silence is golden"`. It relies primarily on the default fstests cleanup path.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents, journal/log metadata. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
intentionally corrupts metadata, so failures can be expected until repair or mount rejection checks run. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/118.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo "Silence is golden"`. The script has 67 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/118 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/119 -->
# sources/test-tools/xfstests/tests/xfs/119

## Purpose
`sources/test-tools/xfstests/tests/xfs/119` is a log recovery/error-injection test. Leaking reservation space in the GRH Test out pv#942130 This can hang when things aren't working The `_begin_fstest` declaration is `_begin_fstest log v2log auto freeze`, which places the test in the `log, v2log, auto, freeze` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`. Local helper surface: no local helper functions beyond optional `_cleanup`. Required capabilities: `_require_scratch`; `_require_freeze`. External and harness commands observed in the full source include `mkfs`, `mount`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas. Observable progress/output points include `echo "start freezing and unfreezing"`; `echo -n .`; `echo "done"`. It installs a custom `_cleanup` to tear down mounts/devices and remove temporary files.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents, journal/log metadata. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
depends on kernel log recovery/error-injection behavior and can expose kernel bugs or require debug facilities. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/119.out`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo "start freezing and unfreezing"`, `echo -n .`, `echo "done"`. The script has 56 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/119 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/120 -->
# sources/test-tools/xfstests/tests/xfs/120

## Purpose
`sources/test-tools/xfstests/tests/xfs/120` is a metadata corruption and repair regression test. Create and populate an XFS filesystem, corrupt the bmbt, then see how the kernel and xfs_repair deal with it. The `_begin_fstest` declaration is `_begin_fstest fuzzers`, which places the test in the `fuzzers` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`, `. ./common/populate`. Local helper surface: no local helper functions beyond optional `_cleanup`. Required capabilities: `_require_scratch`; `_require_attrs`; `_require_populate_commands`; `_require_xfs_db_blocktrash_z_command`. External and harness commands observed in the full source include `xfs_db`, `xfs_repair`, `mkfs`, `mount`, `umount`, `chattr`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; runs XFS diagnostic or administrative tools; injects corruption, I/O failure, debug hooks, or log errors. Observable progress/output points include `echo "+ create scratch fs"`; `echo "+ mount fs image"`; `echo "+ make some files"`; `echo "+ check fs"`; `echo "+ corrupt image"`; `echo "+ mount image && modify files"`; `echo "+ repair fs"`; `echo "+ mount image (2)"`. It installs a custom `_cleanup` to tear down mounts/devices and remove temporary files.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
intentionally corrupts metadata, so failures can be expected until repair or mount rejection checks run; xfs_repair behavior and diagnostics are part of the oracle and may change across xfsprogs versions. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/120.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo "+ create scratch fs"`, `echo "+ mount fs image"`, `echo "+ make some files"`. The script has 87 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/120 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/121 -->
# sources/test-tools/xfstests/tests/xfs/121

## Purpose
`sources/test-tools/xfstests/tests/xfs/121` is a log recovery/error-injection test. To test log replay for the unlinked list. So we create unlinked and still referenced inodes and make sure that no clearing of the unlinked AGI buckets are happening. See pv#953263. The `_begin_fstest` declaration is `_begin_fstest shutdown log auto quick`, which places the test in the `shutdown, log, auto, quick` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`, `. ./common/log`. Local helper surface: no local helper functions beyond optional `_cleanup`. Required capabilities: `_require_scratch`. External and harness commands observed in the full source include `mkfs`, `mount`, `multi_open_unlink`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; compares generated state to expected output or filters nondeterminism. Observable progress/output points include `echo "mkfs"`; `echo "mount"`; `echo "open and unlink $num_files files"`; `echo "godown"`; `echo "unmount"`; `echo "logprint after going down..."`; `echo "mount with replay"`; `echo "logprint to check for CLEAR_AGI_BUCKET..."`. It relies primarily on the default fstests cleanup path.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents, journal/log metadata. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
depends on kernel log recovery/error-injection behavior and can expose kernel bugs or require debug facilities. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/121.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo "mkfs"`, `echo "mount"`, `echo "open and unlink $num_files files"`. The script has 81 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/121 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/122 -->
# sources/test-tools/xfstests/tests/xfs/122

## Purpose
`sources/test-tools/xfstests/tests/xfs/122` is a realtime geometry/allocation regression test. pv#952498 Keep an eye on some of the xfs type sizes Motivation from differing ondisk types for 32 and 64 bit word versions. The `_begin_fstest` declaration is `_begin_fstest other auto quick clone realtime`, which places the test in the `other, auto, quick, clone, realtime` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`. Local helper surface: `_type_size_filter`, `_type_name_filter`, `_attribute_filter`. Required capabilities: `_require_command "$INDENT_PROG" indent`. External and harness commands observed in the full source include `xfs_bmap`, `xfs_io`, `xfs_growfs`, `mkfs`, `mount`, `bstat`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; runs XFS diagnostic or administrative tools; uses loop, realtime, external log, idmapped, or reflink devices; compares generated state to expected output or filters nondeterminism. Observable progress/output points include `echo "#include <$(echo "$hdr" | sed -e 's|/usr/include/||g')>" >> $cprog`; `echo 'int main(int argc, char *argv[]) {' >>$cprog`; `echo 'return 0; }' >>$cprog`. It relies primarily on the default fstests cleanup path.

## State And Persistence Behavior
The test mutates or inspects realtime device geometry and allocation state. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
requires a valid realtime test configuration and exact extent-size alignment. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/122.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo "#include <$(echo "$hdr" | sed -e 's|/usr/include/||g')>" >> $cprog`, `echo 'int main(int argc, char *argv[]) {' >>$cprog`, `echo 'return 0; }' >>$cprog`. The script has 239 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/122 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/123 -->
# sources/test-tools/xfstests/tests/xfs/123

## Purpose
`sources/test-tools/xfstests/tests/xfs/123` is a metadata corruption and repair regression test. Create and populate an XFS filesystem, corrupt a long symlink, then see how the kernel and xfs_repair deal with it. The `_begin_fstest` declaration is `_begin_fstest fuzzers`, which places the test in the `fuzzers` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`, `. ./common/populate`. Local helper surface: no local helper functions beyond optional `_cleanup`. Required capabilities: `_require_scratch`; `_require_attrs`; `_require_populate_commands`; `_require_xfs_db_blocktrash_z_command`. External and harness commands observed in the full source include `xfs_db`, `xfs_repair`, `mkfs`, `mount`, `umount`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; runs XFS diagnostic or administrative tools; injects corruption, I/O failure, debug hooks, or log errors. Observable progress/output points include `echo "+ create scratch fs"`; `echo "+ mount fs image"`; `echo "+ make some files"`; `echo "file contents: moo" > "${SCRATCH_MNT}/x"`; `echo "+ check fs"`; `echo "+ corrupt image"`; `echo "+ mount image"`; `echo "+ repair fs"`. It installs a custom `_cleanup` to tear down mounts/devices and remove temporary files.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
intentionally corrupts metadata, so failures can be expected until repair or mount rejection checks run; xfs_repair behavior and diagnostics are part of the oracle and may change across xfsprogs versions. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/123.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo "+ create scratch fs"`, `echo "+ mount fs image"`, `echo "+ make some files"`. The script has 73 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/123 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/124 -->
# sources/test-tools/xfstests/tests/xfs/124

## Purpose
`sources/test-tools/xfstests/tests/xfs/124` is a metadata corruption and repair regression test. Create and populate an XFS filesystem, corrupt a block xattr, then see how the kernel and xfs_repair deal with it. The `_begin_fstest` declaration is `_begin_fstest fuzzers`, which places the test in the `fuzzers` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`, `. ./common/populate`. Local helper surface: no local helper functions beyond optional `_cleanup`. Required capabilities: `_require_scratch`; `_require_attrs`; `_require_populate_commands`; `_require_xfs_db_blocktrash_z_command`. External and harness commands observed in the full source include `xfs_db`, `xfs_repair`, `mkfs`, `mount`, `umount`, `chattr`, `setfattr`, `getfattr`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; runs XFS diagnostic or administrative tools; injects corruption, I/O failure, debug hooks, or log errors; compares generated state to expected output or filters nondeterminism. Observable progress/output points include `echo "+ create scratch fs"`; `echo "+ mount fs image"`; `echo "+ make some files"`; `echo "+ check fs"`; `echo "+ check xattr"`; `echo "+ corrupt xattr"`; `echo "+ mount image && modify xattr"`; `echo "+ repair fs"`. It installs a custom `_cleanup` to tear down mounts/devices and remove temporary files.

## State And Persistence Behavior
The test mutates or inspects extended attribute forks. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
intentionally corrupts metadata, so failures can be expected until repair or mount rejection checks run; xfs_repair behavior and diagnostics are part of the oracle and may change across xfsprogs versions. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/124.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo "+ create scratch fs"`, `echo "+ mount fs image"`, `echo "+ make some files"`. The script has 89 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/124 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/125 -->
# sources/test-tools/xfstests/tests/xfs/125

## Purpose
`sources/test-tools/xfstests/tests/xfs/125` is a metadata corruption and repair regression test. Create and populate an XFS filesystem, corrupt a leaf xattr's index extent, then see how the kernel and xfs_repair deal with it. The `_begin_fstest` declaration is `_begin_fstest fuzzers`, which places the test in the `fuzzers` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`, `. ./common/populate`. Local helper surface: no local helper functions beyond optional `_cleanup`. Required capabilities: `_require_scratch`; `_require_attrs`; `_require_populate_commands`; `_require_xfs_db_blocktrash_z_command`. External and harness commands observed in the full source include `xfs_db`, `xfs_repair`, `mkfs`, `mount`, `umount`, `chattr`, `setfattr`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; runs XFS diagnostic or administrative tools; injects corruption, I/O failure, debug hooks, or log errors; compares generated state to expected output or filters nondeterminism. Observable progress/output points include `echo "+ create scratch fs"`; `echo "+ mount fs image"`; `echo "+ make some files"`; `echo "+ check fs"`; `echo "+ check xattr"`; `echo "+ corrupt xattr"`; `echo "+ mount image && modify xattr"`; `echo "+ repair fs"`. It installs a custom `_cleanup` to tear down mounts/devices and remove temporary files.

## State And Persistence Behavior
The test mutates or inspects extended attribute forks. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
intentionally corrupts metadata, so failures can be expected until repair or mount rejection checks run; xfs_repair behavior and diagnostics are part of the oracle and may change across xfsprogs versions. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/125.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo "+ create scratch fs"`, `echo "+ mount fs image"`, `echo "+ make some files"`. The script has 89 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/125 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/126 -->
# sources/test-tools/xfstests/tests/xfs/126

## Purpose
`sources/test-tools/xfstests/tests/xfs/126` is a metadata corruption and repair regression test. Create and populate an XFS filesystem, corrupt a leaf xattr's data extent, then see how the kernel and xfs_repair deal with it. The `_begin_fstest` declaration is `_begin_fstest fuzzers`, which places the test in the `fuzzers` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`, `. ./common/populate`. Local helper surface: no local helper functions beyond optional `_cleanup`. Required capabilities: `_require_scratch`; `_require_attrs`; `_require_populate_commands`; `_require_xfs_db_blocktrash_z_command`. External and harness commands observed in the full source include `xfs_db`, `xfs_repair`, `mkfs`, `mount`, `umount`, `chattr`, `setfattr`, `getfattr`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; runs XFS diagnostic or administrative tools; injects corruption, I/O failure, debug hooks, or log errors; compares generated state to expected output or filters nondeterminism. Observable progress/output points include `echo "+ create scratch fs"`; `echo "+ mount fs image"`; `echo "+ make some files"`; `echo "+ check fs"`; `echo "+ check xattr"`; `echo "+ corrupt xattr"`; `echo "+ mount image && modify xattr"`; `echo "+ repair fs"`. It installs a custom `_cleanup` to tear down mounts/devices and remove temporary files.

## State And Persistence Behavior
The test mutates or inspects extended attribute forks. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
intentionally corrupts metadata, so failures can be expected until repair or mount rejection checks run; xfs_repair behavior and diagnostics are part of the oracle and may change across xfsprogs versions. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/126.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo "+ create scratch fs"`, `echo "+ mount fs image"`, `echo "+ make some files"`. The script has 93 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/126 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/127 -->
# sources/test-tools/xfstests/tests/xfs/127

## Purpose
`sources/test-tools/xfstests/tests/xfs/127` is a online growfs behavior test. Tests xfs_growfs on a reflinked filesystem The `_begin_fstest` declaration is `_begin_fstest auto quick clone growfs`, which places the test in the `auto, quick, clone, growfs` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`. Local helper surface: no local helper functions beyond optional `_cleanup`. Required capabilities: `_require_scratch_reflink`; `_require_no_large_scratch_dev`; `_require_cp_reflink`. External and harness commands observed in the full source include `xfs_growfs`, `mkfs`, `mount`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; runs XFS diagnostic or administrative tools; uses loop, realtime, external log, idmapped, or reflink devices; compares generated state to expected output or filters nondeterminism. Observable progress/output points include `echo "Format and mount"`; `echo "Create the original file and reflink to copy1, copy2"`; `echo "Grow fs"`; `echo "Create more reflink copies"`. It relies primarily on the default fstests cleanup path.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
relies on fstests environment variables, scratch/test device hygiene, and filtered golden output remaining stable. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/127.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo "Format and mount"`, `echo "Create the original file and reflink to copy1, copy2"`, `echo "Grow fs"`. The script has 44 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/127 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/128 -->
# sources/test-tools/xfstests/tests/xfs/128

## Purpose
`sources/test-tools/xfstests/tests/xfs/128` is a reflink/refcount stress test. Ensure that xfs_fsr un-reflinks files while defragmenting The `_begin_fstest` declaration is `_begin_fstest auto quick clone fsr prealloc`, which places the test in the `auto, quick, clone, fsr, prealloc` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`. Local helper surface: no local helper functions beyond optional `_cleanup`. Required capabilities: `_require_test_lsattr`; `_require_scratch_reflink`; `_require_cp_reflink`; `_require_xfs_io_command "falloc"`. External and harness commands observed in the full source include `xfs_fsr`, `xfs_io`, `mkfs`, `mount`, `fsx`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; runs XFS diagnostic or administrative tools; uses loop, realtime, external log, idmapped, or reflink devices; compares generated state to expected output or filters nondeterminism. Observable progress/output points include `echo "Format and mount"`; `echo "Create the original file and reflink to file2, file3"`; `echo "CoW the reflink copies"`; `echo "Defragment"`; `echo "Check files"`; `echo "free space checks probably failed because file1 nextents was $nextents"`. It relies primarily on the default fstests cleanup path.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents, extended attribute forks. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
relies on fstests environment variables, scratch/test device hygiene, and filtered golden output remaining stable. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/128.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo "Format and mount"`, `echo "Create the original file and reflink to file2, file3"`, `echo "CoW the reflink copies"`. The script has 140 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/128 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/129 -->
# sources/test-tools/xfstests/tests/xfs/129

## Purpose
`sources/test-tools/xfstests/tests/xfs/129` is a reflink/refcount stress test. Ensure that we can create enough distinct reflink entries to force creation of a multi-level refcount btree, and that metadump will successfully copy said block. The `_begin_fstest` declaration is `_begin_fstest auto quick clone metadump`, which places the test in the `auto, quick, clone, metadump` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`, `. ./common/metadump`. Local helper surface: no local helper functions beyond optional `_cleanup`. Required capabilities: `_require_command "$XFS_MDRESTORE_PROG" "xfs_mdrestore"`; `_require_loop`; `_require_scratch_reflink`. External and harness commands observed in the full source include `mkfs`, `mount`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; uses loop, realtime, external log, idmapped, or reflink devices. Observable progress/output points include `echo "Create the original file blocks"`; `echo "Reflink every other block"`; `echo "Create metadump file, restore it and check restored fs"`. It installs a custom `_cleanup` to tear down mounts/devices and remove temporary files.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents, loop device mappings. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
loop/external-device cleanup must be reliable to avoid leaking mounts or loop devices. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/129.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo "Create the original file blocks"`, `echo "Reflink every other block"`, `echo "Create metadump file, restore it and check restored fs"`. The script has 57 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/129 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/130 -->
# sources/test-tools/xfstests/tests/xfs/130

## Purpose
`sources/test-tools/xfstests/tests/xfs/130` is a metadata corruption and repair regression test. Create and populate an XFS filesystem, corrupt the refcount btree, then see how the kernel and xfs_repair deal with it. The `_begin_fstest` declaration is `_begin_fstest fuzzers clone`, which places the test in the `fuzzers, clone` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`, `. ./common/reflink`. Local helper surface: no local helper functions beyond optional `_cleanup`. Required capabilities: `_require_scratch_reflink`; `_require_cp_reflink`. External and harness commands observed in the full source include `xfs_db`, `xfs_repair`, `mkfs`, `mount`, `umount`, `chattr`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; runs XFS diagnostic or administrative tools; injects corruption, I/O failure, debug hooks, or log errors; uses loop, realtime, external log, idmapped, or reflink devices. Observable progress/output points include `echo "+ create scratch fs"`; `echo "+ mount fs image"`; `echo "+ make some files"`; `echo "+ check fs"`; `echo "+ force log recovery"`; `echo "+ corrupt image"`; `echo "+ mount image"`; `echo "Should not be able to mount with broken refcountbt."`. It installs a custom `_cleanup` to tear down mounts/devices and remove temporary files.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
intentionally corrupts metadata, so failures can be expected until repair or mount rejection checks run; xfs_repair behavior and diagnostics are part of the oracle and may change across xfsprogs versions. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/130.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo "+ create scratch fs"`, `echo "+ mount fs image"`, `echo "+ make some files"`. The script has 88 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/130 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/131 -->
# sources/test-tools/xfstests/tests/xfs/131

## Purpose
`sources/test-tools/xfstests/tests/xfs/131` is a XFS functional regression test. Run fsx with XFS force_zero_range error injection enabled. This is a proxy test for iomap zero range. Zero range is used in limited cases by default, such as EOF zeroing on file extension, etc. This error tag forces use of iomap zero range for fallocate zero range operations. The `_begin_fstest` declaration is `_begin_fstest auto quick zero`, which places the test in the `auto, quick, zero` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/inject`. Local helper surface: no local helper functions beyond optional `_cleanup`. Required capabilities: `_require_test`; `_require_xfs_io_error_injection "force_zero_range"`. External and harness commands observed in the full source include `xfs_io`, `fsx`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow runs XFS diagnostic or administrative tools; compares generated state to expected output or filters nondeterminism. Observable progress/output points include the expected-output oracle is mostly delegated to helper functions and companion output files. It relies primarily on the default fstests cleanup path.

## State And Persistence Behavior
The test mutates or inspects filesystem metadata and command output only. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
relies on fstests environment variables, scratch/test device hygiene, and filtered golden output remaining stable. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/131.out`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks. The script has 26 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/131 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/132 -->
# sources/test-tools/xfstests/tests/xfs/132

## Purpose
`sources/test-tools/xfstests/tests/xfs/132` is a XFS functional regression test. Catch inobt/on disk inode free state mismatches on V4 filesystems The `_begin_fstest` declaration is `_begin_fstest auto quick`, which places the test in the `auto, quick` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`, `. ./common/quota`. Local helper surface: no local helper functions beyond optional `_cleanup`. Required capabilities: `_require_scratch_nocheck`; `_require_xfs_nocrc`. External and harness commands observed in the full source include `mkfs`, `mount`, `quota`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; injects corruption, I/O failure, debug hooks, or log errors; compares generated state to expected output or filters nondeterminism. Observable progress/output points include the expected-output oracle is mostly delegated to helper functions and companion output files. It relies primarily on the default fstests cleanup path.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
intentionally corrupts metadata, so failures can be expected until repair or mount rejection checks run. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/132.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks. The script has 44 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/132 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/133 -->
# sources/test-tools/xfstests/tests/xfs/133

## Purpose
`sources/test-tools/xfstests/tests/xfs/133` is a XFS functional regression test. FS QA test 133 The `_begin_fstest` declaration is `_begin_fstest dangerous_fuzzers`, which places the test in the `dangerous_fuzzers` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`. Local helper surface: no local helper functions beyond optional `_cleanup`. Required capabilities: `_require_scratch_nocheck`. External and harness commands observed in the full source include `xfs_db`, `mkfs`, `mount`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; runs XFS diagnostic or administrative tools; injects corruption, I/O failure, debug hooks, or log errors. Observable progress/output points include `echo "Format and mount"`; `echo m > $testdir/a`; `echo "Corrupt filesystem"`; `echo "Remount, try to append"`. It relies primarily on the default fstests cleanup path.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
intentionally corrupts metadata, so failures can be expected until repair or mount rejection checks run. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/133.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo "Format and mount"`, `echo m > $testdir/a`, `echo "Corrupt filesystem"`. The script has 56 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/133 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/134 -->
# sources/test-tools/xfstests/tests/xfs/134

## Purpose
`sources/test-tools/xfstests/tests/xfs/134` is a XFS functional regression test. FS QA test 134 The `_begin_fstest` declaration is `_begin_fstest dangerous_fuzzers`, which places the test in the `dangerous_fuzzers` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`. Local helper surface: no local helper functions beyond optional `_cleanup`. Required capabilities: `_require_scratch_nocheck`. External and harness commands observed in the full source include `xfs_db`, `mkfs`, `mount`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; runs XFS diagnostic or administrative tools; injects corruption, I/O failure, debug hooks, or log errors. Observable progress/output points include `echo "Format and mount"`; `echo "Corrupt filesystem"`; `echo "Remount, try to append"`. It relies primarily on the default fstests cleanup path.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
intentionally corrupts metadata, so failures can be expected until repair or mount rejection checks run. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/134.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo "Format and mount"`, `echo "Corrupt filesystem"`, `echo "Remount, try to append"`. The script has 59 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/134 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/135 -->
# sources/test-tools/xfstests/tests/xfs/135

## Purpose
`sources/test-tools/xfstests/tests/xfs/135` is a XFS functional regression test. This test verifies that the xfsprogs log formatting infrastructure works correctly for various log stripe unit values. The log is formatted with xfs_db and verified with xfs_logprint. The `_begin_fstest` declaration is `_begin_fstest auto logprint quick v2log`, which places the test in the `auto, logprint, quick, v2log` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/log`. Local helper surface: no local helper functions beyond optional `_cleanup`. Required capabilities: `_require_scratch`; `_require_v2log`; `_require_xfs_db_command "logformat"`. External and harness commands observed in the full source include `xfs_db`, `mkfs`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; runs XFS diagnostic or administrative tools. Observable progress/output points include the expected-output oracle is mostly delegated to helper functions and companion output files. It relies primarily on the default fstests cleanup path.

## State And Persistence Behavior
The test mutates or inspects journal/log metadata. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
relies on fstests environment variables, scratch/test device hygiene, and filtered golden output remaining stable. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/135.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks. The script has 38 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/135 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/136 -->
# sources/test-tools/xfstests/tests/xfs/136

## Purpose
`sources/test-tools/xfstests/tests/xfs/136` is a XFS functional regression test. Test the attr2 code Let's look, xfs_db, at the inode and its literal area for the extents and the attributes The `_begin_fstest` declaration is `_begin_fstest attr2`, which places the test in the `attr2` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`. Local helper surface: `_filter`, `add_eas`, `rm_eas`, `do_extents`, `_print_inode`, `_print_inode_u`, `_print_inode_a`, `_test_add_eas`, `_test_add_extents`, `_test_extents_eas`, `_test_eas_extents`, `_test_initial_sf_ea`. Required capabilities: `_require_scratch`; `_require_attrs`. External and harness commands observed in the full source include `xfs_db`, `mkfs`, `mount`, `makeextents`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; runs XFS diagnostic or administrative tools; uses loop, realtime, external log, idmapped, or reflink devices; compares generated state to expected output or filters nondeterminism. Observable progress/output points include `echo "inum=$inum"`; `echo ""; echo "** add $start..$end EAs **"`; `echo ""; echo "** rm $start..$end EAs **"`; `echo ""; echo "** $num extents **"`; `echo "--- extents: $i ---"`; `echo ""`; `echo "*** Extent differences before and after EAs added ***"`; `echo "Data extents magically changed"`. It relies primarily on the default fstests cleanup path.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents, loop device mappings. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
loop/external-device cleanup must be reliable to avoid leaking mounts or loop devices. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/136.out`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo "inum=$inum"`, `echo ""; echo "** add $start..$end EAs **"`, `echo ""; echo "** rm $start..$end EAs **"`. The script has 328 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/136 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/137 -->
# sources/test-tools/xfstests/tests/xfs/137

## Purpose
`sources/test-tools/xfstests/tests/xfs/137` is a XFS functional regression test. XFS v5 supers carry an LSN in various on-disk structures to track when associated metadata was last written to disk. These metadata LSNs must always be behind the current LSN as dictated by the log to ensure log recovery correctness after a potential crash. This test uses xfs_db to intentionally put the current LSN behind metadata LSNs and verifies that the kernel and xfs_repair detect the problem. The `_begin_fstest` declaration is `_begin_fstest auto metadata v2log`, which places the test in the `auto, metadata, v2log` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`. Local helper surface: no local helper functions beyond optional `_cleanup`. Required capabilities: `_require_scratch`; `_require_scratch_xfs_crc`; `_require_xfs_db_command "logformat"`. External and harness commands observed in the full source include `xfs_db`, `xfs_repair`, `mkfs`, `mount`, `fsstress`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; runs XFS diagnostic or administrative tools. Observable progress/output points include `echo mount failure detected`; `echo repair failure detected`. It relies primarily on the default fstests cleanup path.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents, journal/log metadata. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
xfs_repair behavior and diagnostics are part of the oracle and may change across xfsprogs versions. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/137.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo mount failure detected`, `echo repair failure detected`. The script has 57 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/137 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/138 -->
# sources/test-tools/xfstests/tests/xfs/138

## Purpose
`sources/test-tools/xfstests/tests/xfs/138` is a XFS functional regression test. Test nesting the 'source' command in xfs_db via -c and interactive. The `_begin_fstest` declaration is `_begin_fstest auto quick`, which places the test in the `auto, quick` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`. Local helper surface: no local helper functions beyond optional `_cleanup`. Required capabilities: `_require_scratch`. External and harness commands observed in the full source include `xfs_db`, `mkfs`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; runs XFS diagnostic or administrative tools; compares generated state to expected output or filters nondeterminism. Observable progress/output points include `echo This is file A`; `echo This is file B`; `echo "Test with -c"`; `echo "Test with interactive"`; `echo "p magicnum"; sleep 0.5;`; `echo "source $tmp.a"; sleep 0.5;`; `echo "p magicnum"; sleep 0.5) | _scratch_xfs_db 2>&1 | sed -e 's/xfs_db> //g' -e 's/0x58465342/XFS_MAGIC/g' | grep -E '(This is...`. It relies primarily on the default fstests cleanup path.

## State And Persistence Behavior
The test mutates or inspects filesystem metadata and command output only. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
relies on fstests environment variables, scratch/test device hygiene, and filtered golden output remaining stable. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/138.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo This is file A`, `echo This is file B`, `echo "Test with -c"`. The script has 38 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/138 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/139 -->
# sources/test-tools/xfstests/tests/xfs/139

## Purpose
`sources/test-tools/xfstests/tests/xfs/139` is a reflink/refcount stress test. Try to ENOSPC while expanding the refcntbt by CoWing every block of a file that eats the whole AG. The `_begin_fstest` declaration is `_begin_fstest auto quick clone`, which places the test in the `auto, quick, clone` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`. Local helper surface: no local helper functions beyond optional `_cleanup`. Required capabilities: `_require_no_large_scratch_dev`; `_require_scratch_reflink`; `_require_cp_reflink`. External and harness commands observed in the full source include `mkfs`, `mount`, `filefrag`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; uses loop, realtime, external log, idmapped, or reflink devices; compares generated state to expected output or filters nondeterminism. Observable progress/output points include `echo "Format and mount"`; `echo "Create the original files"`; `echo "CoW every other block"`; `echo "Compare files"`. It installs a custom `_cleanup` to tear down mounts/devices and remove temporary files.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
relies on fstests environment variables, scratch/test device hygiene, and filtered golden output remaining stable. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/139.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo "Format and mount"`, `echo "Create the original files"`, `echo "CoW every other block"`. The script has 61 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/139 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/140 -->
# sources/test-tools/xfstests/tests/xfs/140

## Purpose
`sources/test-tools/xfstests/tests/xfs/140` is a reflink/refcount stress test. Try to ENOSPC while expanding the refcntbt by CoWing every other block of a file that eats the whole AG. The `_begin_fstest` declaration is `_begin_fstest auto clone`, which places the test in the `auto, clone` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`. Local helper surface: no local helper functions beyond optional `_cleanup`. Required capabilities: `_require_no_large_scratch_dev`; `_require_scratch_reflink`; `_require_cp_reflink`. External and harness commands observed in the full source include `mkfs`, `mount`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; uses loop, realtime, external log, idmapped, or reflink devices; compares generated state to expected output or filters nondeterminism. Observable progress/output points include `echo "Format and mount"`; `echo "Create the original files"`; `echo "Compare files"`; `echo "CoW every other block"`. It installs a custom `_cleanup` to tear down mounts/devices and remove temporary files.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
relies on fstests environment variables, scratch/test device hygiene, and filtered golden output remaining stable. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/140.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo "Format and mount"`, `echo "Create the original files"`, `echo "Compare files"`. The script has 72 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/140 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/141 -->
# sources/test-tools/xfstests/tests/xfs/141

## Purpose
`sources/test-tools/xfstests/tests/xfs/141` is a log recovery/error-injection test. Use the XFS log record CRC error injection mechanism to test torn writes to the log. The error injection mechanism writes an invalid CRC and shuts down the filesystem. The test verifies that a subsequent remount recovers the log and that the filesystem is consistent. Note that this test requires a DEBUG mode kernel. The `_begin_fstest` declaration is `_begin_fstest auto log metadata`, which places the test in the `auto, log, metadata` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/inject`. Local helper surface: no local helper functions beyond optional `_cleanup`. Required capabilities: `_require_xfs_io_error_injection "log_bad_crc"`; `_require_scratch`. External and harness commands observed in the full source include `xfs_io`, `mkfs`, `mount`, `fsstress`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; runs XFS diagnostic or administrative tools; injects corruption, I/O failure, debug hooks, or log errors. Observable progress/output points include `echo "Silence is golden."`; `echo iteration $i log_badcrc_factor: $factor >> $seqres.full 2>&1`. It relies primarily on the default fstests cleanup path.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents, journal/log metadata. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
depends on kernel log recovery/error-injection behavior and can expose kernel bugs or require debug facilities. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/141.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo "Silence is golden."`, `echo iteration $i log_badcrc_factor: $factor >> $seqres.full 2>&1`. The script has 52 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/141 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/142 -->
# sources/test-tools/xfstests/tests/xfs/142

## Purpose
`sources/test-tools/xfstests/tests/xfs/142` is a realtime geometry/allocation regression test. This is a regression test for commit d0c20d38af13 "xfs: fix xfs_bmap_validate_extent_raw when checking attr fork of rt files", which fixes the bmap record validator so that it will not check the attr fork extent mappings of a realtime file against the size of the realtime volume. The `_begin_fstest` declaration is `_begin_fstest auto quick rw attr realtime`, which places the test in the `auto, quick, rw, attr, realtime` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`. Local helper surface: no local helper functions beyond optional `_cleanup`. Required capabilities: `_require_scratch`; `_require_realtime`. External and harness commands observed in the full source include `xfs_bmap`, `mkfs`, `mount`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; runs XFS diagnostic or administrative tools; uses loop, realtime, external log, idmapped, or reflink devices. Observable progress/output points include `echo Silence is golden.`. It relies primarily on the default fstests cleanup path.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents, extended attribute forks, realtime device geometry and allocation state. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
requires a valid realtime test configuration and exact extent-size alignment. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/142.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo Silence is golden.`. The script has 42 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/142 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/143 -->
# sources/test-tools/xfstests/tests/xfs/143

## Purpose
`sources/test-tools/xfstests/tests/xfs/143` is a realtime geometry/allocation regression test. Make sure mkfs sets up enough of the rt geometry that we can compute the correct min log size for formatting the fs. This is a regression test for the xfsprogs commit 31409f48 ("mkfs: set required parts of the realtime geometry before computing log geometry"). The `_begin_fstest` declaration is `_begin_fstest auto quick realtime mount`, which places the test in the `auto, quick, realtime, mount` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`. Local helper surface: no local helper functions beyond optional `_cleanup`. Required capabilities: `_require_scratch`; `_require_realtime`. External and harness commands observed in the full source include `mkfs`, `mount`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; uses loop, realtime, external log, idmapped, or reflink devices. Observable progress/output points include `echo "Silence is golden"`. It relies primarily on the default fstests cleanup path.

## State And Persistence Behavior
The test mutates or inspects journal/log metadata, realtime device geometry and allocation state. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
requires a valid realtime test configuration and exact extent-size alignment. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/143.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo "Silence is golden"`. The script has 29 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/143 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/144 -->
# sources/test-tools/xfstests/tests/xfs/144

## Purpose
`sources/test-tools/xfstests/tests/xfs/144` is a XFS functional regression test. Now that we've increased the default log size calculation, test mkfs with various stripe units and filesystem sizes to see if we can provoke mkfs into breaking. The `_begin_fstest` declaration is `_begin_fstest auto mkfs`, which places the test in the `auto, mkfs` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`. Local helper surface: `test_format`. Required capabilities: `_require_test`; `_require_fs_space $TEST_DIR $((3 * 1048576))`. External and harness commands observed in the full source include `mkfs`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; compares generated state to expected output or filters nondeterminism. Observable progress/output points include `echo Silence is golden`; `echo "$tag" >> $seqres.full`. It relies primarily on the default fstests cleanup path.

## State And Persistence Behavior
The test mutates or inspects test filesystem paths/devices, journal/log metadata. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
relies on fstests environment variables, scratch/test device hygiene, and filtered golden output remaining stable. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/144.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo Silence is golden`, `echo "$tag" >> $seqres.full`. The script has 53 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/144 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/145 -->
# sources/test-tools/xfstests/tests/xfs/145

## Purpose
`sources/test-tools/xfstests/tests/xfs/145` is a quota/accounting regression test. Regression test for failing to undo delalloc quota reservations when changing project id but we fail some other part of FSSETXATTR validation.  If we fail the test, we trip debugging assertions in dmesg.  This is a regression test for commit 1aecf3734a95 ("xfs: fix chown leaking delalloc quota blocks when fssetxattr fails"). The `_begin_fstest` declaration is `_begin_fstest auto quick quota`, which places the test in the `auto, quick, quota` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/quota`. Local helper surface: no local helper functions beyond optional `_cleanup`. Required capabilities: `_require_command "$FILEFRAG_PROG" filefrag`; `_require_test_program "chprojid_fail"`; `_require_quota`; `_require_scratch`; `_require_prjquota $SCRATCH_DEV`. External and harness commands observed in the full source include `mkfs`, `mount`, `filefrag`, `quota`, `chprojid_fail`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; compares generated state to expected output or filters nondeterminism. Observable progress/output points include `echo "Format filesystem" | tee -a $seqres.full`; `echo "Run test program"`; `echo "file didn't get delalloc extents, test invalid?"`. It relies primarily on the default fstests cleanup path.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents, quota accounting records and limits, extended attribute forks. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
quota results vary with block size, delayed allocation, mount options, and configured test users/groups/projects. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/145.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo "Format filesystem" | tee -a $seqres.full`, `echo "Run test program"`, `echo "file didn't get delalloc extents, test invalid?"`. The script has 57 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/145 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/146 -->
# sources/test-tools/xfstests/tests/xfs/146

## Purpose
`sources/test-tools/xfstests/tests/xfs/146` is a metadata corruption and repair regression test. This is a regression test for commit 2a6ca4baed62 ("xfs: make sure the rt allocator doesn't run off the end") which fixes an overflow error in the _near realtime allocator.  If the rt bitmap ends exactly at the end of a block and the number of rt extents is large enough to allow an allocation request larger than the maximum extent size, it's possible that during a large allocation request, the allocator will fail to constrain maxlen on the second run through the loop, and the rt bitmap range check will run right off the end of the rtbitmap file.  When this happens, xfs triggers a verifier error and returns EFSCORRUPTED. The `_begin_fstest` declaration is `_begin_fstest auto quick rw realtime prealloc`, which places the test in the `auto, quick, rw, realtime, prealloc` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`. Local helper surface: no local helper functions beyond optional `_cleanup`. Required capabilities: `_require_scratch`; `_require_realtime`; `_require_xfs_io_command "falloc"`; `_require_test_program "punch-alternating"`. External and harness commands observed in the full source include `xfs_io`, `mkfs`, `mount`, `punch-alternating`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; runs XFS diagnostic or administrative tools; uses loop, realtime, external log, idmapped, or reflink devices. Observable progress/output points include `echo "blksz $blksz rextsize $rextsize rextblks $rextblks" >> $seqres.full`; `echo "rtsize1 $rtsize1 rtsize2 $rtsize2 rtsize $rtsize" >> $seqres.full`; `echo "rt size will be $rtsize" >> $seqres.full`. It relies primarily on the default fstests cleanup path.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents, loop device mappings, realtime device geometry and allocation state. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
intentionally corrupts metadata, so failures can be expected until repair or mount rejection checks run; requires a valid realtime test configuration and exact extent-size alignment; loop/external-device cleanup must be reliable to avoid leaking mounts or loop devices. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/146.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo "blksz $blksz rextsize $rextsize rextblks $rextblks" >> $seqres.full`, `echo "rtsize1 $rtsize1 rtsize2 $rtsize2 rtsize $rtsize" >> $seqres.full`, `echo "rt size will be $rtsize" >> $seqres.full`. The script has 86 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/146 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/147 -->
# sources/test-tools/xfstests/tests/xfs/147

## Purpose
`sources/test-tools/xfstests/tests/xfs/147` is a realtime geometry/allocation regression test. Make sure we validate realtime extent size alignment for fallocate modes. This is a regression test for fe341eb151ec ("xfs: ensure that fpunch, fcollapse, and finsert operations are aligned to rt extent size") The `_begin_fstest` declaration is `_begin_fstest auto quick rw realtime collapse insert unshare zero prealloc`, which places the test in the `auto, quick, rw, realtime, collapse, insert, unshare, zero, prealloc` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`. Local helper surface: no local helper functions beyond optional `_cleanup`. Required capabilities: `_require_scratch`; `_require_realtime`; `_require_xfs_io_command "fcollapse"`; `_require_xfs_io_command "finsert"`; `_require_xfs_io_command "funshare"`; `_require_xfs_io_command "fzero"`; `_require_xfs_io_command "falloc"`. External and harness commands observed in the full source include `xfs_io`, `mkfs`, `mount`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; runs XFS diagnostic or administrative tools; uses loop, realtime, external log, idmapped, or reflink devices; compares generated state to expected output or filters nondeterminism. Observable progress/output points include `echo "blksz $blksz rextsize $rextsize rextblks $rextblks" >> $seqres.full`; `echo "test $verb"`. It relies primarily on the default fstests cleanup path.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents, realtime device geometry and allocation state. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
requires a valid realtime test configuration and exact extent-size alignment. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/147.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo "blksz $blksz rextsize $rextsize rextblks $rextblks" >> $seqres.full`, `echo "test $verb"`. The script has 51 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/147 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/148 -->
# sources/test-tools/xfstests/tests/xfs/148

## Purpose
`sources/test-tools/xfstests/tests/xfs/148` is a metadata corruption and repair regression test. See if we catch corrupt directory names or attr names with nulls or slashes in them. The `_begin_fstest` declaration is `_begin_fstest auto quick fuzzers`, which places the test in the `auto, quick, fuzzers` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`. Local helper surface: `access_stuff`. Required capabilities: `_require_test`; `_require_attrs`; `_require_xfs_nocrc`. External and harness commands observed in the full source include `xfs_db`, `xfs_scrub`, `mkfs`, `mount`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; runs XFS diagnostic or administrative tools; injects corruption, I/O failure, debug hooks, or log errors; uses loop, realtime, external log, idmapped, or reflink devices; compares generated state to expected output or filters nondeterminism. Observable progress/output points include `echo "creating entries" >> $seqres.full`; `echo "++ ACCESSING GOOD METADATA" | tee -a $seqres.full`; `echo "++ ACCESSING BAD METADATA" | tee -a $seqres.full`; `echo "does scrub complain?" >> $seqres.full`; `echo "scrub failed to report corruption ($res)"`; `echo "does repair complain?" >> $seqres.full`; `echo "repair failed to report corruption ($res)"`. It installs a custom `_cleanup` to tear down mounts/devices and remove temporary files.

## State And Persistence Behavior
The test mutates or inspects test filesystem paths/devices, loop device mappings, extended attribute forks. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
intentionally corrupts metadata, so failures can be expected until repair or mount rejection checks run; loop/external-device cleanup must be reliable to avoid leaking mounts or loop devices. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/148.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo "creating entries" >> $seqres.full`, `echo "++ ACCESSING GOOD METADATA" | tee -a $seqres.full`, `echo "++ ACCESSING BAD METADATA" | tee -a $seqres.full`. The script has 137 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/148 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/149 -->
# sources/test-tools/xfstests/tests/xfs/149

## Purpose
`sources/test-tools/xfstests/tests/xfs/149` is a online growfs behavior test. Test to ensure xfs_growfs command accepts device nodes if & only if they are mounted. This functionality, though undocumented, worked until xfsprogs v4.12 It was added back and documented after xfsprogs v5.2 via 7e8275f8 xfs_growfs: allow mounted device node as argument Based on xfs/289 The `_begin_fstest` declaration is `_begin_fstest auto quick growfs`, which places the test in the `auto, quick, growfs` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`. Local helper surface: no local helper functions beyond optional `_cleanup`. Required capabilities: `_require_test`; `_require_loop`. External and harness commands observed in the full source include `xfs_growfs`, `mkfs.xfs`, `mkfs`, `mount`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; runs XFS diagnostic or administrative tools; uses loop, realtime, external log, idmapped, or reflink devices; compares generated state to expected output or filters nondeterminism. Observable progress/output points include `echo "=== mkfs.xfs ==="`; `echo "=== truncate ==="`; `echo "=== create loop device ==="`; `echo "=== create loop device symlink ==="`; `echo "loop device is $loop_dev" >> $seqres.full`; `echo "=== xfs_growfs - unmounted device, command should be rejected ==="`; `echo "=== xfs_growfs - check symlinked dev, unmounted ==="`; `echo "=== mount ==="`. It installs a custom `_cleanup` to tear down mounts/devices and remove temporary files.

## State And Persistence Behavior
The test mutates or inspects test filesystem paths/devices, loop device mappings. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
loop/external-device cleanup must be reliable to avoid leaking mounts or loop devices. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/149.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo "=== mkfs.xfs ==="`, `echo "=== truncate ==="`, `echo "=== create loop device ==="`. The script has 93 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/149 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/150 -->
# sources/test-tools/xfstests/tests/xfs/150

## Purpose
`sources/test-tools/xfstests/tests/xfs/150` is a xfs_db command behavior test. Make sure the xfs_db path command works the way the author thinks it does. This means that it can navigate to random inodes, fails on paths that don't resolve. The `_begin_fstest` declaration is `_begin_fstest auto quick db`, which places the test in the `auto, quick, db` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`. Local helper surface: no local helper functions beyond optional `_cleanup`. Required capabilities: `_require_xfs_db_command "path"`; `_require_scratch`. External and harness commands observed in the full source include `xfs_db`, `mkfs`, `mount`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; runs XFS diagnostic or administrative tools; compares generated state to expected output or filters nondeterminism. Observable progress/output points include `echo "Format filesystem and populate"`; `echo "Check xfs_db path on directories"`; `echo "Did not find directory /a"`; `echo "Did not find empty sf directory /a/b"`; `echo "Check xfs_db path on files"`; `echo "Did not find 61-byte file /a/c"`; `echo "Check xfs_db path on file symlinks"`; `echo "Did not find symlink /a/d"`. It relies primarily on the default fstests cleanup path.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
relies on fstests environment variables, scratch/test device hygiene, and filtered golden output remaining stable. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/150.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo "Format filesystem and populate"`, `echo "Check xfs_db path on directories"`, `echo "Did not find directory /a"`. The script has 83 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/150 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/151 -->
# sources/test-tools/xfstests/tests/xfs/151

## Purpose
`sources/test-tools/xfstests/tests/xfs/151` is a xfs_db command behavior test. Make sure the xfs_db ls command works the way the author thinks it does. This means that we can list the current directory, list an arbitrary path, and we can't list things that aren't directories. The `_begin_fstest` declaration is `_begin_fstest auto quick db`, which places the test in the `auto, quick, db` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`. Local helper surface: `filter_ls`. Required capabilities: `_require_xfs_db_command "path"`; `_require_xfs_db_command "ls"`; `_require_scratch`; `_require_xfs_has_feature "$SCRATCH_MNT" ftype`. External and harness commands observed in the full source include `xfs_db`, `mkfs`, `mount`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; runs XFS diagnostic or administrative tools; compares generated state to expected output or filters nondeterminism. Observable progress/output points include `echo "Format filesystem and populate"`; `echo "Manually navigate to root dir then list"`; `echo "Use path to navigate to root dir then list"`; `echo "Use path to navigate to /a then list"`; `echo "Use path to navigate to /a/b then list"`; `echo "Use path to navigate to /a/c (non-dir) then list"`. It relies primarily on the default fstests cleanup path.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
relies on fstests environment variables, scratch/test device hygiene, and filtered golden output remaining stable. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/151.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo "Format filesystem and populate"`, `echo "Manually navigate to root dir then list"`, `echo "Use path to navigate to root dir then list"`. The script has 91 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/151 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/152 -->
# sources/test-tools/xfstests/tests/xfs/152

## Purpose
`sources/test-tools/xfstests/tests/xfs/152` is a quota/accounting regression test. Exercise basic xfs_quota functionality (user/group/project quota) Use of "sync" mount option here is an attempt to get deterministic allocator behaviour. The `_begin_fstest` declaration is `_begin_fstest auto quick quota idmapped`, which places the test in the `auto, quick, quota, idmapped` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`, `. ./common/quota`. Local helper surface: `wipe_mounts`, `create_files_unmapped`, `create_files_idmapped`, `clean_files`, `filter_quot`, `filter_report`, `filter_quota`, `filter_state`, `test_quot`, `test_report`, `test_quota`, `test_limit`, `test_timer`, `test_disable`, `test_enable`, `test_off`, `test_remove`, `test_state`, `test_dump`, `test_restore`, `wipe_scratch`, `qmount_idmapped`, `test_xfs_quota`. Required capabilities: `_require_idmapped_mounts`; `_require_test_program "vfs/mount-idmapped"`; `_require_scratch`; `_require_xfs_quota`; `_require_user fsgqa`; `_require_user fsgqa2`; `_require_group fsgqa`; `_require_group fsgqa2`. External and harness commands observed in the full source include `xfs_quota`, `mkfs`, `mount`, `umount`, `quota`, `vfs/mount-idmapped`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; uses loop, realtime, external log, idmapped, or reflink devices; compares generated state to expected output or filters nondeterminism. Observable progress/output points include `echo "Using type=$type id=$id" >> $seqres.full`; `echo "Using type=$type id=$id2" >> $seqres.full`; `echo "checking quot command (type=$type)"`; `echo "checking report command (type=$type)"`; `echo "checking quota command (type=$type)"`; `echo "checking limit command (type=$type, bsoft=$bs, bhard=$bh, isoft=$is, ihard=$ih)"`; `echo "checking timer command (type=$type)"`; `echo "checking disable command (type=$type)"`. It installs a custom `_cleanup` to tear down mounts/devices and remove temporary files.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents, quota accounting records and limits. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
quota results vary with block size, delayed allocation, mount options, and configured test users/groups/projects. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/152.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo "Using type=$type id=$id" >> $seqres.full`, `echo "Using type=$type id=$id2" >> $seqres.full`, `echo "checking quot command (type=$type)"`. The script has 373 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/152 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/153 -->
# sources/test-tools/xfstests/tests/xfs/153

## Purpose
`sources/test-tools/xfstests/tests/xfs/153` is a quota/accounting regression test. Exercises basic XFS quota functionality uquota, gquota, uqnoenforce, gqnoenforce The `_begin_fstest` declaration is `_begin_fstest auto quick quota idmapped`, which places the test in the `auto, quick, quota, idmapped` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`, `. ./common/quota`. Local helper surface: `_filter_and_check_blks`, `run_tests`. Required capabilities: `_require_scratch`; `_require_xfs_quota`; `_require_user fsgqa`; `_require_idmapped_mounts`; `_require_test_program "vfs/mount-idmapped"`. External and harness commands observed in the full source include `xfs_quota`, `mkfs`, `mount`, `umount`, `quota`, `repquota`, `vfs/mount-idmapped`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; uses loop, realtime, external log, idmapped, or reflink devices; compares generated state to expected output or filters nondeterminism. Observable progress/output points include `echo "Using type=$type id=$id" >>$seqres.full`; `echo`; `echo "*** report no quota settings" | tee -a $seqres.full`; `echo "*** report initial settings" | tee -a $seqres.full`; `echo "ls -l $SCRATCH_MNT" >>$seqres.full`; `echo "*** push past the soft inode limit" | tee -a $seqres.full`; `echo "*** push past the soft block limit" | tee -a $seqres.full`; `echo "*** push past the hard inode limit (expect EDQUOT)" | tee -a $seqres.full`. It installs a custom `_cleanup` to tear down mounts/devices and remove temporary files.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents, quota accounting records and limits. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
quota results vary with block size, delayed allocation, mount options, and configured test users/groups/projects. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/153.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo "Using type=$type id=$id" >>$seqres.full`, `echo`, `echo "*** report no quota settings" | tee -a $seqres.full`. The script has 203 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/153 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/154 -->
# sources/test-tools/xfstests/tests/xfs/154

## Purpose
`sources/test-tools/xfstests/tests/xfs/154` is a metadata corruption and repair regression test. Make sure that the kernel won't mount a filesystem if repair forcibly sets NEEDSREPAIR while fixing metadata.  Corrupt a directory in such a way as to force repair to write an invalid dirent value as a sentinel to trigger a repair activity in a later phase.  Use a debug knob in xfs_repair to abort the repair immediately after forcing the flag on. The `_begin_fstest` declaration is `_begin_fstest auto quick repair`, which places the test in the `auto, quick, repair` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`. Local helper surface: no local helper functions beyond optional `_cleanup`. Required capabilities: `_require_scratch_nocheck`; `_require_scratch_xfs_crc		# needsrepair only exists for v5`; `_require_libxfs_debug_flag LIBXFS_DEBUG_WRITE_CRASH`. External and harness commands observed in the full source include `xfs_db`, `xfs_repair`, `mkfs`, `mount`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; runs XFS diagnostic or administrative tools; injects corruption, I/O failure, debug hooks, or log errors; compares generated state to expected output or filters nondeterminism. Observable progress/output points include `echo "Should not be able to mount after needsrepair crash"`. It relies primarily on the default fstests cleanup path.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
intentionally corrupts metadata, so failures can be expected until repair or mount rejection checks run; xfs_repair behavior and diagnostics are part of the oracle and may change across xfsprogs versions. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/154.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo "Should not be able to mount after needsrepair crash"`. The script has 64 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/154 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/155 -->
# sources/test-tools/xfstests/tests/xfs/155

## Purpose
`sources/test-tools/xfstests/tests/xfs/155` is a xfs_repair regression test. Populate a filesystem with all types of metadata, then run repair with the libxfs write failure trigger set to go after a single write.  Check that the injected error trips, causing repair to abort, that needsrepair is set on the fs, the kernel won't mount; and that a non-injecting repair run clears needsrepair and makes the filesystem mountable again. Repeat with the trip point set to successively higher numbers of writes until we hit ~200 writes or repair manages to run to completion without tripping. The `_begin_fstest` declaration is `_begin_fstest auto repair`, which places the test in the `auto, repair` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/populate`, `. ./common/filter`. Local helper surface: no local helper functions beyond optional `_cleanup`. Required capabilities: `_require_scratch_nocheck`; `_require_scratch_xfs_crc		# needsrepair only exists for v5`; `_require_populate_commands`; `_require_libxfs_debug_flag LIBXFS_DEBUG_WRITE_CRASH`; `_require_command "$TIMEOUT_PROG" timeout`. External and harness commands observed in the full source include `xfs_repair`, `mount`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow mounts and unmounts scratch/test filesystems; runs XFS diagnostic or administrative tools; injects corruption, I/O failure, debug hooks, or log errors; uses loop, realtime, external log, idmapped, or reflink devices; compares generated state to expected output or filters nondeterminism. Observable progress/output points include `echo "Setting debug hook to crash after $allowed_writes writes." >> $seqres.full`; `echo "repair failed with $res??"`; `echo "ran to completion on the first try?"`; `echo "NEEDSREPAIR should be set on corrupt fs"`; `echo "Checking filesystem one last time after $allowed_writes writes." >> $seqres.full`; `echo "Clearing NEEDSREPAIR" >> $seqres.full`; `echo "Repair failed to clear NEEDSREPAIR on the $allowed_writes writes test"`; `echo Silence is golden.`. It relies primarily on the default fstests cleanup path.

## State And Persistence Behavior
The test mutates or inspects loop device mappings. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
intentionally corrupts metadata, so failures can be expected until repair or mount rejection checks run; loop/external-device cleanup must be reliable to avoid leaking mounts or loop devices; xfs_repair behavior and diagnostics are part of the oracle and may change across xfsprogs versions. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/155.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo "Setting debug hook to crash after $allowed_writes writes." >> $seqres.full`, `echo "repair failed with $res??"`, `echo "ran to completion on the first try?"`. The script has 80 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/155 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/156 -->
# sources/test-tools/xfstests/tests/xfs/156

## Purpose
`sources/test-tools/xfstests/tests/xfs/156` is a xfs_admin option parsing test. Functional testing for xfs_admin to make sure that it handles option parsing correctly for functionality that's relevant to V5 filesystems.  It doesn't test the options that apply only to V4 filesystems because that disk format is deprecated. The `_begin_fstest` declaration is `_begin_fstest auto quick admin`, which places the test in the `auto, quick, admin` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`. Local helper surface: `note`. Required capabilities: `_require_scratch`; `_require_command "$XFS_ADMIN_PROG" "xfs_admin"`. External and harness commands observed in the full source include `xfs_db`, `xfs_repair`, `xfs_admin`, `mkfs`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; runs XFS diagnostic or administrative tools. Observable progress/output points include `echo "$@" | tee -a $seqres.full`; `echo "UUID randomization failed? $old_uuid == $new_uuid"`; `echo "UUID = babababa-baba-baba-baba-babababababa"`. It relies primarily on the default fstests cleanup path.

## State And Persistence Behavior
The test mutates or inspects filesystem metadata and command output only. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
xfs_repair behavior and diagnostics are part of the oracle and may change across xfsprogs versions. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/156.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo "$@" | tee -a $seqres.full`, `echo "UUID randomization failed? $old_uuid == $new_uuid"`, `echo "UUID = babababa-baba-baba-baba-babababababa"`. The script has 76 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/156 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/157 -->
# sources/test-tools/xfstests/tests/xfs/157

## Purpose
`sources/test-tools/xfstests/tests/xfs/157` is a xfs_admin option parsing test. Functional testing for xfs_admin to ensure that it parses arguments correctly with regards to data devices that are files, external logs, and realtime devices. Because this test synthesizes log and rt devices (by modifying the test run configuration), it does /not/ require the ability to mount the scratch filesystem.  This increases test coverage while isolating the weird bits to a single test. This is partially a regression test for "xfs_admin: pick up log arguments correctly", insofar as the issue fixed by that patch was discovered with an earlier revision of this test. The `_begin_fstest` declaration is `_begin_fstest auto quick admin`, which places the test in the `auto, quick, admin` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`. Local helper surface: `scenario`, `_fake_mkfs`, `_fake_xfs_db_options`, `_fake_xfs_db`, `_fake_xfs_admin`, `_fake_xfs_repair`, `check_label`. Required capabilities: `_require_test`; `_require_scratch_nocheck`; `_require_command "$XFS_ADMIN_PROG" "xfs_admin"`. External and harness commands observed in the full source include `xfs_db`, `xfs_repair`, `xfs_admin`, `mkfs`, `mount`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; runs XFS diagnostic or administrative tools; uses loop, realtime, external log, idmapped, or reflink devices; compares generated state to expected output or filters nondeterminism. Observable progress/output points include `echo "$@" | tee -a $seqres.full`; `echo $OPTIONS $* $dev`. It installs a custom `_cleanup` to tear down mounts/devices and remove temporary files.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents, test filesystem paths/devices, journal/log metadata. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
requires a valid realtime test configuration and exact extent-size alignment; loop/external-device cleanup must be reliable to avoid leaking mounts or loop devices; xfs_repair behavior and diagnostics are part of the oracle and may change across xfsprogs versions. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/157.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo "$@" | tee -a $seqres.full`, `echo $OPTIONS $* $dev`. The script has 159 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/157 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/116.cfg -->
# sources/test-tools/xfstests/tests/xfs/116.cfg

## Purpose
`sources/test-tools/xfstests/tests/xfs/116.cfg` is a one-line fstests configuration sidecar for `xfs/116`. It enables the `metadir` configuration profile by mapping `metadir` to `metadir`, so the test can be scheduled with the metadata-directory feature variant.

## Important APIs, Types, And Functions
There are no shell functions or executable APIs. The important datum is the `metadir: metadir` key/value entry consumed by the fstests configuration machinery.

## Control Flow
The file is read by the fstests runner before executing the associated test. It does not run commands; it selects a configuration lane for the paired script.

## State And Persistence
No runtime state is created directly. Its persistent effect is test selection/configuration metadata in the source tree.

## Dependencies And Integration Points
It integrates with `sources/test-tools/xfstests/tests/xfs/116` and the fstests config parser that recognizes `.cfg` files beside test scripts.

## Risks
The sidecar is intentionally minimal; misspelling the key or value would silently move coverage away from the intended metadir variant.

## Test Signals
Validation is structural: the file exists, is non-empty, and contains exactly `metadir: metadir` for the metadir lane.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/116.cfg -->
