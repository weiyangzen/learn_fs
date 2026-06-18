# Research Group subset-b-009541

This grouped report covers btrfs xfstests shell cases 118 through 219 under `sources/test-tools/xfstests/tests/btrfs`. Each section is delimited for reconciliation into the source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/118 -->
# sources/test-tools/xfstests/tests/btrfs/118

## Purpose

`sources/test-tools/xfstests/tests/btrfs/118` is btrfs fstests case `118`. It targets log-tree replay and fsync crash recovery, subvolume/snapshot metadata. Source comments describe the scenario as: Test that if we fsync a directory that had a snapshot entry in it that was deleted and crash, the next time we mount the filesystem, the log replay procedure will not fail and the snapshot is not present anymore. Create a snapshot at the root of our filesystem (mount point path), delete it, fsync the mount point path, crash and mount to replay the log. This should succeed and after the filesystem is mounted the snapshot should not be visible anymore. Similar scenario as above, but this time the snapshot is created inside a directory and not directly under the root (mount point path).

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick snapshot metadata log` declares tags `auto quick snapshot metadata log`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`. sourced helpers: `./common/preamble`, `./common/filter`, `./common/dmflakey`; requirements: `_require_scratch`, `_require_dm_target flakey`, `_require_metadata_journaling $SCRATCH_DEV`; local shell helpers: `_cleanup()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_cleanup_flakey`; `rm -f $tmp.*`; `_require_scratch`; `_require_dm_target flakey`; `_scratch_mkfs >>$seqres.full 2>&1`; `_init_flakey`; `_scratch_mount`; `_btrfs subvolume snapshot $SCRATCH_MNT $SCRATCH_MNT/snap1`; `_btrfs subvolume delete $SCRATCH_MNT/snap1`; `$XFS_IO_PROG -c "fsync" $SCRATCH_MNT`; `_flakey_drop_and_remount`; `mkdir $SCRATCH_MNT/testdir`; `_btrfs subvolume snapshot $SCRATCH_MNT $SCRATCH_MNT/testdir/snap2`; `_btrfs subvolume delete $SCRATCH_MNT/testdir/snap2`; `$XFS_IO_PROG -c "fsync" $SCRATCH_MNT/testdir`; `_scratch_unmount`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. The dm-flakey helper deliberately drops writes and remounts to force replay of whatever reached the btrfs log tree. Subvolume roots, read-only snapshots, deleted snapshot orphans, and directory entries are persisted across remounts. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick snapshot metadata log` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

The pass/fail signal depends on realistic crash semantics from dm-flakey and on metadata journaling being available.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. Most success is absence of unexpected output, ending with `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/118 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/119 -->
# sources/test-tools/xfstests/tests/btrfs/119

## Purpose

`sources/test-tools/xfstests/tests/btrfs/119` is btrfs fstests case `119`. It targets log-tree replay and fsync crash recovery, subvolume/snapshot metadata, quota-group accounting and limits. Source comments describe the scenario as: Test log tree replay when qgroups are enabled and orphan roots (deleted snapshots) exist. Create 2 directories with one file in one of them. We use these just to trigger a transaction commit later, moving the file from directory a to directory b and doing an fsync against directory a. Create our test file with 2 4K extents. Create a snapshot and delete it. This doesn't really delete the snapshot immediately, just makes it inaccessible and invisible to user space, the snapshot is deleted later by a dedicated kernel thread (cleaner kthread) which is woke up at the next transaction commit.

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick snapshot metadata qgroup log` declares tags `auto quick snapshot metadata qgroup log`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`. sourced helpers: `./common/preamble`, `./common/filter`, `./common/dmflakey`; requirements: `_require_scratch`, `_require_dm_target flakey`, `_require_metadata_journaling $SCRATCH_DEV`; local shell helpers: `_cleanup()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_cleanup_flakey`; `rm -f $tmp.*`; `_require_scratch`; `_require_dm_target flakey`; `_scratch_mkfs >>$seqres.full 2>&1`; `_init_flakey`; `_scratch_mount`; `_btrfs quota enable $SCRATCH_MNT`; `$XFS_IO_PROG -f -s -c "pwrite -S 0xaa 0 8K" $SCRATCH_MNT/foobar | _filter_xfs_io`; `_btrfs subvolume snapshot $SCRATCH_MNT $SCRATCH_MNT/snap`; `_btrfs subvolume delete $SCRATCH_MNT/snap`; `$XFS_IO_PROG -c "fsync" $SCRATCH_MNT/a`; `$XFS_IO_PROG -c "fsync" $SCRATCH_MNT/foobar`; `md5sum $SCRATCH_MNT/foobar | _filter_scratch`; `_flakey_drop_and_remount`; `_scratch_unmount`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. The dm-flakey helper deliberately drops writes and remounts to force replay of whatever reached the btrfs log tree. Subvolume roots, read-only snapshots, deleted snapshot orphans, and directory entries are persisted across remounts. Quota-group counters, limits, inherited qgroups, and rescan results are kernel-maintained metadata validated at unmount/check time. The script records user-visible checksums, listings, device counters, capabilities, or byte dumps as evidence. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick snapshot metadata qgroup log` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

The pass/fail signal depends on realistic crash semantics from dm-flakey and on metadata journaling being available. Qgroup tests are sensitive to delayed accounting, rescan completion, and checker support for quota validation.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. Before/after checksums must match across remount, balance, or receive.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/119 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/120 -->
# sources/test-tools/xfstests/tests/btrfs/120

## Purpose

`sources/test-tools/xfstests/tests/btrfs/120` is btrfs fstests case `120`. It targets log-tree replay and fsync crash recovery, subvolume/snapshot metadata. Source comments describe the scenario as: Test that if we delete a snapshot, delete its parent directory, create another directory with the same name as that parent and then fsync either the new directory or a file inside the new directory, the fsync succeeds, the fsync log is replayable and produces a correct result. Now do the same as before but instead of doing an fsync against the directory, do an fsync against a file inside the directory.

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick snapshot metadata log` declares tags `auto quick snapshot metadata log`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`. sourced helpers: `./common/preamble`, `./common/filter`, `./common/dmflakey`; requirements: `_require_scratch`, `_require_dm_target flakey`, `_require_metadata_journaling $SCRATCH_DEV`; local shell helpers: `_cleanup()`, `populate_testdir()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_cleanup_flakey`; `rm -f $tmp.*`; `_require_scratch`; `_require_dm_target flakey`; `_btrfs subvolume snapshot $SCRATCH_MNT \`; `_btrfs subvolume delete $SCRATCH_MNT/testdir/snap`; `mkdir $SCRATCH_MNT/testdir`; `_scratch_mkfs >>$seqres.full 2>&1`; `_init_flakey`; `_scratch_mount`; `$XFS_IO_PROG -c "fsync" $SCRATCH_MNT/testdir`; `_flakey_drop_and_remount`; `ls -R $SCRATCH_MNT | _filter_scratch`; `touch $SCRATCH_MNT/testdir/foobar`; `$XFS_IO_PROG -c "fsync" $SCRATCH_MNT/testdir/foobar`; `_scratch_unmount`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. The dm-flakey helper deliberately drops writes and remounts to force replay of whatever reached the btrfs log tree. Subvolume roots, read-only snapshots, deleted snapshot orphans, and directory entries are persisted across remounts. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick snapshot metadata log` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

The pass/fail signal depends on realistic crash semantics from dm-flakey and on metadata journaling being available.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/120 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/121 -->
# sources/test-tools/xfstests/tests/btrfs/121

## Purpose

`sources/test-tools/xfstests/tests/btrfs/121` is btrfs fstests case `121`. It targets subvolume/snapshot metadata, quota-group accounting and limits. Source comments describe the scenario as: Test that an invalid parent qgroup does not cause snapshot create to force the FS readonly. This issue is fixed by the following btrfs patch: [PATCH] btrfs: handle non-fatal errors in btrfs_qgroup_inherit() http://thread.gmane.org/gmane.comp.file-systems.btrfs/54755 The qgroup '1/10' does not exist. The kernel should either gives an error (newer kernel with invalid qgroup detection) or ignore it (older kernel with above fix). Either way, we just ignore the output completely, and we will check if the fs is still RW later.

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick snapshot qgroup` declares tags `auto quick snapshot qgroup`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_scratch`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_require_scratch`; `_scratch_mkfs >/dev/null`; `_scratch_mount`; `_btrfs quota enable $SCRATCH_MNT`; `$BTRFS_UTIL_PROG subvolume snapshot -i 1/10 $SCRATCH_MNT $SCRATCH_MNT/snap1 >> $seqres.full 2>&1`; `touch $SCRATCH_MNT/foobar`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Subvolume roots, read-only snapshots, deleted snapshot orphans, and directory entries are persisted across remounts. Quota-group counters, limits, inherited qgroups, and rescan results are kernel-maintained metadata validated at unmount/check time. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick snapshot qgroup` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Qgroup tests are sensitive to delayed accounting, rescan completion, and checker support for quota validation.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. Most success is absence of unexpected output, ending with `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/121 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/122 -->
# sources/test-tools/xfstests/tests/btrfs/122

## Purpose

`sources/test-tools/xfstests/tests/btrfs/122` is btrfs fstests case `122`. It targets subvolume/snapshot metadata, quota-group accounting and limits. Source comments describe the scenario as: Test that qgroup counts are valid after snapshot creation. This has been broken in btrfs since Linux v4.1 First make some simple snapshots - the bug was initially reproduced like this This forces the fs tree out past level 0, adding at least one tree block which must be properly accounted for when we make our next snapshots. Snapshot twice. qgroup will be checked by fstest at _check_scratch_fs()

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick snapshot qgroup` declares tags `auto quick snapshot qgroup`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_scratch`, `_require_btrfs_qgroup_report`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_require_scratch`; `_require_btrfs_qgroup_report`; `_scratch_mkfs >> $seqres.full`; `_scratch_mount`; `_btrfs quota enable $SCRATCH_MNT`; `mkdir "$SCRATCH_MNT/snaps"`; `_btrfs subvolume snapshot $SCRATCH_MNT "$SCRATCH_MNT/snaps/empty1"`; `_btrfs subvolume snapshot $SCRATCH_MNT "$SCRATCH_MNT/snaps/empty2"`; `mkdir "$SCRATCH_MNT/data"`; `$XFS_IO_PROG -f -c "pwrite 0 1M" "$SCRATCH_MNT/data/file$i" > /dev/null 2>&1`; `_btrfs subvolume snapshot $SCRATCH_MNT "$SCRATCH_MNT/snaps/snap1"`; `_btrfs subvolume snapshot $SCRATCH_MNT "$SCRATCH_MNT/snaps/snap2"`; `_scratch_unmount`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Subvolume roots, read-only snapshots, deleted snapshot orphans, and directory entries are persisted across remounts. Quota-group counters, limits, inherited qgroups, and rescan results are kernel-maintained metadata validated at unmount/check time. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick snapshot qgroup` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Qgroup tests are sensitive to delayed accounting, rescan completion, and checker support for quota validation.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. fstests scratch checking validates filesystem and qgroup consistency after unmount.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/122 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/123 -->
# sources/test-tools/xfstests/tests/btrfs/123

## Purpose

`sources/test-tools/xfstests/tests/btrfs/123` is btrfs fstests case `123`. It targets quota-group accounting and limits, balance relocation behavior. Source comments describe the scenario as: Test if btrfs leaks qgroup numbers for data extents Due to balance code is doing trick tree block swap, which doing non-standard extent reference update, qgroup can't handle it correctly, and leads to corrupted qgroup numbers. Need to use inline extents to fill metadata rapidly create 64K inlined metadata, which will ensure there is a 2-level metadata. Even for maximum nodesize(64K) then a large data write to make the quota corruption obvious enough enable quota and rescan to get correct number now balance data block groups to corrupt qgroup

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick qgroup balance` declares tags `auto quick qgroup balance`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_scratch`, `_require_btrfs_qgroup_report`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_require_scratch`; `_require_btrfs_qgroup_report`; `_scratch_mkfs >/dev/null`; `_scratch_mount "-o max_inline=2048"`; `_pwrite_byte 0xcdcdcdcd 0 2k $SCRATCH_MNT/small_$i | _filter_xfs_io`; `_pwrite_byte 0xcdcdcdcd 0 32m $SCRATCH_MNT/large | _filter_xfs_io`; `sync`; `_btrfs quota enable $SCRATCH_MNT`; `_qgroup_rescan $SCRATCH_MNT`; `_run_btrfs_balance_start -d $SCRATCH_MNT >> $seqres.full`; `_scratch_unmount`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Quota-group counters, limits, inherited qgroups, and rescan results are kernel-maintained metadata validated at unmount/check time. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick qgroup balance` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Qgroup tests are sensitive to delayed accounting, rescan completion, and checker support for quota validation.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. fstests scratch checking validates filesystem and qgroup consistency after unmount.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/123 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/124 -->
# sources/test-tools/xfstests/tests/btrfs/124

## Purpose

`sources/test-tools/xfstests/tests/btrfs/124` is btrfs fstests case `124`. It targets multi-device or RAID volume behavior, balance relocation behavior. Source comments describe the scenario as: This test verify the RAID1 reconstruction on the reappeared device. By using the following steps: Initialize a RAID1 with some data Re-mount RAID1 degraded with dev2 missing and write up to half of the FS capacity. Save md5sum checkpoint1 Re-mount healthy RAID1 Let balance re-silver. Save md5sum checkpoint2 Re-mount RAID1 degraded with dev1 missing

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto replace volume balance raid` declares tags `auto replace volume balance raid`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_scratch_dev_pool 2`, `_require_btrfs_forget_or_module_loadable`, `_require_non_zoned_device "$dev1"`, `_require_non_zoned_device "$dev2"`, `_notrun "Smallest dev size $max_fs_sz, Need at least 2G"`; local shell helpers: `_cleanup()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `rm -f $tmp.*`; `_btrfs_rescan_devices`; `_require_scratch_dev_pool 2`; `_test_unmount`; `_require_btrfs_forget_or_module_loadable`; `_require_non_zoned_device "$dev1"`; `_require_non_zoned_device "$dev2"`; `_test_mount`; `_scratch_mount >> $seqres.full 2>&1`; `_mount -o degraded $dev1 $SCRATCH_MNT >>$seqres.full 2>&1`; `checkpoint1=\`md5sum $SCRATCH_MNT/tf2\``; `echo "Inital sum does not match with after balance"`; `if [ "$checkpoint1" != "$checkpoint3" ]; then`; `echo $checkpoint3`; `echo "Inital sum does not match with data on dev2 written by balance"`; `$UMOUNT_PROG $dev2`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Device identity, missing-device state, degraded mounts, and balance/repair writes are part of the persistent test surface. The script records user-visible checksums, listings, device counters, capabilities, or byte dumps as evidence. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto replace volume balance raid` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

It may be slow or disruptive because it reformats scratch storage and may use fault injection or degraded-device mounts. Multi-device tests need enough disposable devices and can leave device scans cached if cleanup does not run.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. Before/after checksums must match across remount, balance, or receive.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/124 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/125 -->
# sources/test-tools/xfstests/tests/btrfs/125

## Purpose

`sources/test-tools/xfstests/tests/btrfs/125` is btrfs fstests case `125`. It targets multi-device or RAID volume behavior, balance relocation behavior. Source comments describe the scenario as: This test verify if the reconstructed data on the RAID5 is good. Steps: Initialize RAID5 with some data Re-mount RAID5 degraded with dev3 missing and write data Save md5sum checkpoint1 Re-mount healthy RAID5 Let balance fix the RAID5. Save md5sum checkpoint2 Re-mount RAID5 degraded with dev1 as missing. Save md5sum checkpoint3

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest replace volume balance auto quick raid` declares tags `replace volume balance auto quick raid`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_scratch_dev_pool 3`, `_require_btrfs_forget_or_module_loadable`, `_require_btrfs_raid_type raid5`, `_notrun "Smallest dev size $max_fs_sz, Need at least 2G"`; local shell helpers: `_cleanup()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `rm -f $tmp.*`; `_btrfs_rescan_devices`; `_require_scratch_dev_pool 3`; `_test_unmount`; `_require_btrfs_forget_or_module_loadable`; `_test_mount`; `_scratch_mount >> $seqres.full 2>&1`; `_mount -o degraded,device=$dev2 $dev1 $SCRATCH_MNT >>$seqres.full 2>&1`; `checkpoint1=\`md5sum $SCRATCH_MNT/tf2\``; `echo "Mount normal and balance"`; `_btrfs device scan`; `echo "Inital sum does not match with after balance"`; `if [ "$checkpoint1" != "$checkpoint3" ]; then`; `echo $checkpoint3`; `echo "Inital sum does not match with data on dev2 written by balance"`; `$UMOUNT_PROG $dev2`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Device identity, missing-device state, degraded mounts, and balance/repair writes are part of the persistent test surface. The script records user-visible checksums, listings, device counters, capabilities, or byte dumps as evidence. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `replace volume balance auto quick raid` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Multi-device tests need enough disposable devices and can leave device scans cached if cleanup does not run.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. Before/after checksums must match across remount, balance, or receive.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/125 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/126 -->
# sources/test-tools/xfstests/tests/btrfs/126

## Purpose

`sources/test-tools/xfstests/tests/btrfs/126` is btrfs fstests case `126`. It targets quota-group accounting and limits. Source comments describe the scenario as: Regression test for leaking data space after hitting EDQUOTA This test requires specific data space usage, skip if we have compression enabled. Use enospc_debug mount option to trigger restrict space info check The amount of written data may change due to different nodesize at mkfs time, so redirect stdout to seqres.full. Also, EDQUOTA is expected, which can't be redirected due to the limitation of _filter_xfs_io, so golden output will include EDQUOTA error message Fstests will umount the fs, and at umount time, kernel warning will be triggered

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick qgroup limit` declares tags `auto quick qgroup limit`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_scratch`, `_require_btrfs_qgroup_report`, `_require_no_compress`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_require_scratch`; `_require_btrfs_qgroup_report`; `_scratch_mkfs >/dev/null`; `_scratch_mount "-o enospc_debug"`; `_btrfs quota enable $SCRATCH_MNT`; `_qgroup_rescan $SCRATCH_MNT`; `_btrfs qgroup limit 512K 0/5 $SCRATCH_MNT`; `_pwrite_byte 0xcdcdcdcd 0 1M $SCRATCH_MNT/test_file 2>&1 >> $seqres.full | \`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Quota-group counters, limits, inherited qgroups, and rescan results are kernel-maintained metadata validated at unmount/check time. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick qgroup limit` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Qgroup tests are sensitive to delayed accounting, rescan completion, and checker support for quota validation.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. fstests scratch checking validates filesystem and qgroup consistency after unmount.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/126 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/127 -->
# sources/test-tools/xfstests/tests/btrfs/127

## Purpose

`sources/test-tools/xfstests/tests/btrfs/127` is btrfs fstests case `127`. It targets send/receive stream correctness. Source comments describe the scenario as: Test that an incremental send operation works after doing radical changes in the directory hierarchy that involve switching the inode that directory entries point to. case 1 case 2 case 3 case 4 Filesystem looks like: .                                                                  (ino 256) |--- case_1/                                                       (ino 257)

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick send` declares tags `auto quick send`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; snapshot equivalence is checked with `$FSSUM_PROG`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_test`, `_require_scratch`, `_require_fssum`; local shell helpers: `_cleanup()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `rm -fr $send_files_dir`; `rm -f $tmp.*`; `_require_scratch`; `_require_fssum`; `send_files_dir=$TEST_DIR/btrfs-test-$seq`; `mkdir $send_files_dir`; `_scratch_mount`; `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/mysnap1`; `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/mysnap2`; `run_check $FSSUM_PROG -A -f -w $send_files_dir/1.fssum $SCRATCH_MNT/mysnap1`; `run_check $FSSUM_PROG -A -f -w $send_files_dir/2.fssum \`; `_scratch_unmount`; `_btrfs receive -f $send_files_dir/1.snap $SCRATCH_MNT`; `run_check $FSSUM_PROG -r $send_files_dir/1.fssum $SCRATCH_MNT/mysnap1`; `_btrfs receive -f $send_files_dir/2.snap $SCRATCH_MNT`; `run_check $FSSUM_PROG -r $send_files_dir/2.fssum $SCRATCH_MNT/mysnap2`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Subvolume roots, read-only snapshots, deleted snapshot orphans, and directory entries are persisted across remounts. Send streams, fssum manifests, and received snapshots are temporary artifacts used to compare source and reconstructed filesystems. The script records user-visible checksums, listings, device counters, capabilities, or byte dumps as evidence. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick send` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Send tests can be fragile around inode-number ordering, rename dependencies, clone commands, xattrs, and receiver mount options.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. Most success is absence of unexpected output, ending with `Silence is golden`. `fssum` manifests are written on source snapshots and verified after receive.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/127 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/128 -->
# sources/test-tools/xfstests/tests/btrfs/128

## Purpose

`sources/test-tools/xfstests/tests/btrfs/128` is btrfs fstests case `128`. It targets send/receive stream correctness. Source comments describe the scenario as: Test that, under a particular scenario, an incremental send operation does not leak memory (which used to emit a warning in dmesg/syslog). Filesystem looks like: .                                                             (ino 256) |--- a/                                                       (ino 257) |    |--- c/                                                  (ino 260) |--- del/                                                     (ino 259) |--- tmp/                                               (ino 258) |--- x/                                                 (ino 261) |--- y/                                                 (ino 262)

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick send` declares tags `auto quick send`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; snapshot equivalence is checked with `$FSSUM_PROG`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_test`, `_require_scratch`, `_require_fssum`; local shell helpers: `_cleanup()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `rm -fr $send_files_dir`; `rm -f $tmp.*`; `_require_scratch`; `_require_fssum`; `send_files_dir=$TEST_DIR/btrfs-test-$seq`; `mkdir $send_files_dir`; `_scratch_mount`; `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/mysnap1`; `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/mysnap2`; `run_check $FSSUM_PROG -A -f -w $send_files_dir/1.fssum $SCRATCH_MNT/mysnap1`; `run_check $FSSUM_PROG -A -f -w $send_files_dir/2.fssum \`; `_scratch_unmount`; `_btrfs receive -f $send_files_dir/1.snap $SCRATCH_MNT`; `run_check $FSSUM_PROG -r $send_files_dir/1.fssum $SCRATCH_MNT/mysnap1`; `_btrfs receive -f $send_files_dir/2.snap $SCRATCH_MNT`; `run_check $FSSUM_PROG -r $send_files_dir/2.fssum $SCRATCH_MNT/mysnap2`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Subvolume roots, read-only snapshots, deleted snapshot orphans, and directory entries are persisted across remounts. Send streams, fssum manifests, and received snapshots are temporary artifacts used to compare source and reconstructed filesystems. The script records user-visible checksums, listings, device counters, capabilities, or byte dumps as evidence. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick send` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Send tests can be fragile around inode-number ordering, rename dependencies, clone commands, xattrs, and receiver mount options.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. Most success is absence of unexpected output, ending with `Silence is golden`. `fssum` manifests are written on source snapshots and verified after receive.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/128 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/129 -->
# sources/test-tools/xfstests/tests/btrfs/129

## Purpose

`sources/test-tools/xfstests/tests/btrfs/129` is btrfs fstests case `129`. It targets send/receive stream correctness. Source comments describe the scenario as: Test that an incremental send operation does not prematurely issues rmdir operations under a particular scenario (the rmdir operation is sent before the target directory is empty). Filesystem looks like: .                                                             (ino 256) |--- a/                                                       (ino 257) |    |--- c/                                                  (ino 260) |--- del/                                                     (ino 259) |--- tmp/                                               (ino 258) |--- x/                                                 (ino 261)

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick send` declares tags `auto quick send`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; snapshot equivalence is checked with `$FSSUM_PROG`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_test`, `_require_scratch`, `_require_fssum`; local shell helpers: `_cleanup()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `rm -fr $send_files_dir`; `rm -f $tmp.*`; `_require_scratch`; `_require_fssum`; `send_files_dir=$TEST_DIR/btrfs-test-$seq`; `mkdir $send_files_dir`; `_scratch_mount`; `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/mysnap1`; `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/mysnap2`; `run_check $FSSUM_PROG -A -f -w $send_files_dir/1.fssum $SCRATCH_MNT/mysnap1`; `run_check $FSSUM_PROG -A -f -w $send_files_dir/2.fssum \`; `_scratch_unmount`; `_btrfs receive -f $send_files_dir/1.snap $SCRATCH_MNT`; `run_check $FSSUM_PROG -r $send_files_dir/1.fssum $SCRATCH_MNT/mysnap1`; `_btrfs receive -f $send_files_dir/2.snap $SCRATCH_MNT`; `run_check $FSSUM_PROG -r $send_files_dir/2.fssum $SCRATCH_MNT/mysnap2`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Subvolume roots, read-only snapshots, deleted snapshot orphans, and directory entries are persisted across remounts. Send streams, fssum manifests, and received snapshots are temporary artifacts used to compare source and reconstructed filesystems. The script records user-visible checksums, listings, device counters, capabilities, or byte dumps as evidence. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick send` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Send tests can be fragile around inode-number ordering, rename dependencies, clone commands, xattrs, and receiver mount options.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. Most success is absence of unexpected output, ending with `Silence is golden`. `fssum` manifests are written on source snapshots and verified after receive.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/129 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/130 -->
# sources/test-tools/xfstests/tests/btrfs/130

## Purpose

`sources/test-tools/xfstests/tests/btrfs/130` is btrfs fstests case `130`. It targets send/receive stream correctness. Source comments describe the scenario as: Check if btrfs send can handle large deduped file, whose file extents are all pointing to one extent. Such file structure will cause quite large pressure to any operation which iterates all backref of one extent. And unfortunately, btrfs send is one of these operations, and will cause softlock or OOM on systems with small memory(<4G). Use 128K blocksize, the default value of both deduperemove or inband dedupe create the initial file, whose file extents are all point to one extent create a RO snapshot, so we can send out the snapshot

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick clone send` declares tags `auto quick clone send`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`. sourced helpers: `./common/preamble`, `./common/filter`, `./common/reflink`; requirements: `_require_scratch`, `_require_scratch_reflink`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_require_scratch`; `_require_scratch_reflink`; `_scratch_mkfs > /dev/null 2>&1`; `_scratch_mount`; `file=$SCRATCH_MNT/foobar`; `_pwrite_byte 0xcdcdcdcd 0 $blocksize  $file | _filter_xfs_io`; `_reflink_range $file 0 $file $(($i * $blocksize)) $blocksize \`; `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/ro_snap`; `echo "# $BTRFS_UTIL_PROG send $SCRATCH_MNT/ro_snap > /dev/null" >> $seqres.full`; `$BTRFS_UTIL_PROG send $SCRATCH_MNT/ro_snap > /dev/null 2>>$seqres.full`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Subvolume roots, read-only snapshots, deleted snapshot orphans, and directory entries are persisted across remounts. Send streams, fssum manifests, and received snapshots are temporary artifacts used to compare source and reconstructed filesystems. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick clone send` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Send tests can be fragile around inode-number ordering, rename dependencies, clone commands, xattrs, and receiver mount options.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/130 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/131 -->
# sources/test-tools/xfstests/tests/btrfs/131

## Purpose

`sources/test-tools/xfstests/tests/btrfs/131` is btrfs fstests case `131`. It targets the btrfs feature area named by its fstests tags. Source comments describe the scenario as: Test free space tree mount options, 3 options involved: - No space cache - Old (deprecated) v1 space cache - New (default) v2 space cache Future proof against btrfs-progs making space_cache=v2 filesystems by default. Mount options might interfere. When the free space tree is not enabled: -o space_cache=v1: keep using the old free space cache -o space_cache=v2: enable the free space tree

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick` declares tags `auto quick`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_scratch`, `_require_btrfs_command inspect-internal dump-super`, `_require_btrfs_fs_feature free_space_tree`, `_require_btrfs_v1_cache`; local shell helpers: `mkfs_v1()`, `mkfs_v2()`, `check_fst_compat()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_require_scratch`; `_require_btrfs_command inspect-internal dump-super`; `_require_btrfs_fs_feature free_space_tree`; `_require_btrfs_v1_cache`; `_scratch_mkfs >/dev/null 2>&1`; `_scratch_mount -o clear_cache,space_cache=v1`; `_scratch_mount -o space_cache=v2`; `_scratch_mount -o space_cache=v1`; `_scratch_mount -o clear_cache,space_cache=v2`; `_try_scratch_mount -o nospace_cache >/dev/null 2>&1 || echo "mount failed"`; `_try_scratch_mount -o space_cache=v1 >/dev/null 2>&1 || echo "mount failed"`; `_scratch_mount`; `_scratch_mount -o clear_cache`; `_scratch_mount -o clear_cache,nospace_cache`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

The main risk is environmental: missing fstests helpers, unsupported btrfs features, or changed userspace output can turn the test into a notrun or golden-output mismatch.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/131 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/132 -->
# sources/test-tools/xfstests/tests/btrfs/132

## Purpose

`sources/test-tools/xfstests/tests/btrfs/132` is btrfs fstests case `132`. It targets the btrfs feature area named by its fstests tags. Source comments describe the scenario as: Check if false ENOSPC will happen when parallel buffer write happens The problem is caused by incorrect metadata reservation for any buffered write whose max extent size is not 128M (including compression and in-band dedupe). Use small filesystem to trigger the bug more easily It's highly recommened to run this test case with MKFS_OPTIONS="-n 64k" to further increase the possibility Since the false ENOSPC happens due to incorrect metadata reservation, larger nodesize and small fs will make it much easier to reproduce Recommended to use MOUNT_OPTIONS="-o compress" to trigger the bug

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto enospc` declares tags `auto enospc`; environment gates are expressed through `_require*` helpers; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_scratch`; local shell helpers: `_cleanup()`, `loop_writer()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `rm -f $tmp.*`; `_require_scratch`; `_scratch_mkfs_sized $((512 * 1024 * 1024)) >> $seqres.full 2>&1`; `_scratch_mount`; `loop_writer()`; `$XFS_IO_PROG -c "pwrite -b 8K $offset $len" $file > /dev/null`; `touch $SCRATCH_MNT/testfile`; `loop_writer 0 128M $SCRATCH_MNT/testfile &`; `loop_writer 128M 16M $SCRATCH_MNT/testfile &`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto enospc` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

It may be slow or disruptive because it reformats scratch storage and may use fault injection or degraded-device mounts.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. Most success is absence of unexpected output, ending with `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/132 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/133 -->
# sources/test-tools/xfstests/tests/btrfs/133

## Purpose

`sources/test-tools/xfstests/tests/btrfs/133` is btrfs fstests case `133`. It targets send/receive stream correctness. Source comments describe the scenario as: Test that an incremental send operation does not fail when a new inode replaces an old inode that has the same number but different generation, and both are direct children of the subvolume/snapshot root. Filesystem looks like: .                                                             (ino 256) |--- a1/                                                      (ino 257) |--- a2/                                                      (ino 258) Filesystem now looks like: .                                                             (ino 256) |--- a2                                                       (ino 257)

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick send` declares tags `auto quick send`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; snapshot equivalence is checked with `$FSSUM_PROG`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_test`, `_require_scratch`, `_require_fssum`; local shell helpers: `_cleanup()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `rm -fr $send_files_dir`; `rm -f $tmp.*`; `_require_scratch`; `_require_fssum`; `send_files_dir=$TEST_DIR/btrfs-test-$seq`; `mkdir $send_files_dir`; `_scratch_mount`; `$BTRFS_UTIL_PROG subvolume snapshot -r $SCRATCH_MNT \`; `$BTRFS_UTIL_PROG send -f $send_files_dir/1.snap \`; `$BTRFS_UTIL_PROG receive -f $send_files_dir/1.snap $SCRATCH_MNT > /dev/null`; `rm $send_files_dir/1.snap`; `$BTRFS_UTIL_PROG send -p $SCRATCH_MNT/mysnap1 -f $send_files_dir/2.snap \`; `$SCRATCH_MNT/mysnap2 2>&1 1>/dev/null | _filter_scratch`; `$FSSUM_PROG -r $send_files_dir/1.fssum $SCRATCH_MNT/mysnap1`; `$BTRFS_UTIL_PROG receive -f $send_files_dir/2.snap $SCRATCH_MNT > /dev/null`; `$FSSUM_PROG -r $send_files_dir/2.fssum $SCRATCH_MNT/mysnap2`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Subvolume roots, read-only snapshots, deleted snapshot orphans, and directory entries are persisted across remounts. Send streams, fssum manifests, and received snapshots are temporary artifacts used to compare source and reconstructed filesystems. The script records user-visible checksums, listings, device counters, capabilities, or byte dumps as evidence. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick send` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Send tests can be fragile around inode-number ordering, rename dependencies, clone commands, xattrs, and receiver mount options.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. `fssum` manifests are written on source snapshots and verified after receive.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/133 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/134 -->
# sources/test-tools/xfstests/tests/btrfs/134

## Purpose

`sources/test-tools/xfstests/tests/btrfs/134` is btrfs fstests case `134`. It targets send/receive stream correctness. Source comments describe the scenario as: Test that an incremental send operation works after moving a directory into a new parent directory, deleting its previous parent directory and creating a new inode that has the same inode number as the old parent. Filesystem looks like: .                                                             (ino 256, gen 3) |--- dir258/                                                  (ino 258, gen 7) |       |--- dir257/                                          (ino 257, gen 7) |--- dir259/                                                  (ino 259, gen 7) Remount the filesystem so that the next created inodes will have the numbers 258 and 259. This is because when a filesystem is mounted, btrfs sets the

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick send` declares tags `auto quick send`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; snapshot equivalence is checked with `$FSSUM_PROG`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_test`, `_require_scratch`, `_require_fssum`; local shell helpers: `_cleanup()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `rm -fr $send_files_dir`; `rm -f $tmp.*`; `_require_scratch`; `_require_fssum`; `send_files_dir=$TEST_DIR/btrfs-test-$seq`; `mkdir $send_files_dir`; `_scratch_mount`; `$BTRFS_UTIL_PROG subvolume snapshot -r $SCRATCH_MNT \`; `_scratch_cycle_mount`; `$FSSUM_PROG -A -f -w $send_files_dir/1.fssum $SCRATCH_MNT/mysnap1`; `$FSSUM_PROG -A -f -w $send_files_dir/2.fssum \`; `_scratch_unmount`; `$BTRFS_UTIL_PROG receive -f $send_files_dir/1.snap $SCRATCH_MNT > /dev/null`; `$FSSUM_PROG -r $send_files_dir/1.fssum $SCRATCH_MNT/mysnap1`; `$BTRFS_UTIL_PROG receive -f $send_files_dir/2.snap $SCRATCH_MNT > /dev/null`; `$FSSUM_PROG -r $send_files_dir/2.fssum $SCRATCH_MNT/mysnap2`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Subvolume roots, read-only snapshots, deleted snapshot orphans, and directory entries are persisted across remounts. Send streams, fssum manifests, and received snapshots are temporary artifacts used to compare source and reconstructed filesystems. The script records user-visible checksums, listings, device counters, capabilities, or byte dumps as evidence. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick send` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Send tests can be fragile around inode-number ordering, rename dependencies, clone commands, xattrs, and receiver mount options.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. `fssum` manifests are written on source snapshots and verified after receive.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/134 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/135 -->
# sources/test-tools/xfstests/tests/btrfs/135

## Purpose

`sources/test-tools/xfstests/tests/btrfs/135` is btrfs fstests case `135`. It targets send/receive stream correctness. Source comments describe the scenario as: Test that an incremental send operation works when in both snapshots there are two directory inodes that have the same number but different generations and have an entry with the same name that corresponds to different inodes in each snapshot. Filesystem looks like: .                                                             (ino 256) |--- f                                                        (ino 257) |--- d259_old/                                                (ino 259) |--- d1/                                              (ino 258) Filesystem now looks like:

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick send` declares tags `auto quick send`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; snapshot equivalence is checked with `$FSSUM_PROG`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_test`, `_require_scratch`, `_require_fssum`; local shell helpers: `_cleanup()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `rm -fr $send_files_dir`; `rm -f $tmp.*`; `_require_scratch`; `_require_fssum`; `send_files_dir=$TEST_DIR/btrfs-test-$seq`; `mkdir $send_files_dir`; `_scratch_mount`; `$BTRFS_UTIL_PROG subvolume snapshot -r $SCRATCH_MNT \`; `$BTRFS_UTIL_PROG send -f $send_files_dir/1.snap \`; `$BTRFS_UTIL_PROG receive -f $send_files_dir/1.snap $SCRATCH_MNT > /dev/null`; `rm $send_files_dir/1.snap`; `$BTRFS_UTIL_PROG send -p $SCRATCH_MNT/mysnap1 -f $send_files_dir/2.snap \`; `$SCRATCH_MNT/mysnap2 2>&1 1>/dev/null | _filter_scratch`; `$FSSUM_PROG -r $send_files_dir/1.fssum $SCRATCH_MNT/mysnap1`; `$BTRFS_UTIL_PROG receive -f $send_files_dir/2.snap $SCRATCH_MNT > /dev/null`; `$FSSUM_PROG -r $send_files_dir/2.fssum $SCRATCH_MNT/mysnap2`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Subvolume roots, read-only snapshots, deleted snapshot orphans, and directory entries are persisted across remounts. Send streams, fssum manifests, and received snapshots are temporary artifacts used to compare source and reconstructed filesystems. The script records user-visible checksums, listings, device counters, capabilities, or byte dumps as evidence. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick send` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Send tests can be fragile around inode-number ordering, rename dependencies, clone commands, xattrs, and receiver mount options.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. `fssum` manifests are written on source snapshots and verified after receive.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/135 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/136 -->
# sources/test-tools/xfstests/tests/btrfs/136

## Purpose

`sources/test-tools/xfstests/tests/btrfs/136` is btrfs fstests case `136`. It targets the btrfs feature area named by its fstests tags. Source comments describe the scenario as: Test btrfs-convert 1) create ext3 filesystem & populate it. 2) upgrade ext3 filesystem to ext4. 3) populate data. 4) source has combination of non-extent and extent files. 5) convert it to btrfs, mount and verify contents. ext4 does not support zoned block device Create & populate an ext3 filesystem mount and populate non-extent file Upgrade it to ext4.

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto convert` declares tags `auto convert`; environment gates are expressed through `_require*` helpers. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_scratch_nocheck`, `_require_non_zoned_device "${SCRATCH_DEV}"`, `_require_extra_fs ext3`, `_require_command "$BTRFS_CONVERT_PROG" btrfs-convert`, `_require_command "$MKFS_EXT4_PROG" mkfs.ext4`, `_require_command "$E2FSCK_PROG" e2fsck`, `_require_command "$TUNE2FS_PROG" tune2fs`, `_notrun "Could not create ext3 filesystem"`, `_notrun "block size $BLOCK_SIZE is not supported by ext3"`; local shell helpers: `populate_data()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_require_scratch_nocheck`; `_require_non_zoned_device "${SCRATCH_DEV}"`; `_require_command "$MKFS_EXT4_PROG" mkfs.ext4`; `mkdir -p $data_path`; `$MKFS_EXT4_PROG -F -t ext3 -b $BLOCK_SIZE $SCRATCH_DEV > $seqres.full 2>&1 || \`; `mount -t ext3 $SCRATCH_DEV $SCRATCH_MNT`; `_scratch_unmount`; `mount -t ext4 $SCRATCH_DEV $SCRATCH_MNT`; `_try_scratch_mount || _fail "Could not mount new btrfs fs"`; `btrfs_perm=\`md5sum "$BTRFS_MD5SUM" | cut -f1 -d' '\``; `ext_perm=\`md5sum "$EXT_MD5SUM" | cut -f1 -d' '\``; `echo "md5sum mismatch"`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. The script records user-visible checksums, listings, device counters, capabilities, or byte dumps as evidence. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto convert` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

It may be slow or disruptive because it reformats scratch storage and may use fault injection or degraded-device mounts.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. Most success is absence of unexpected output, ending with `Silence is golden`. Before/after checksums must match across remount, balance, or receive.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/136 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/137 -->
# sources/test-tools/xfstests/tests/btrfs/137

## Purpose

`sources/test-tools/xfstests/tests/btrfs/137` is btrfs fstests case `137`. It targets send/receive stream correctness. Source comments describe the scenario as: Test that both incremental and full send operations preserve file holes. Create the first test file. Create a second test file with a 1Mb hole. Now add one new extent to our first test file, increasing its size and leaving a 1Mb hole between the first extent and this new extent. Now overwrite the last extent of our second test file. Create the send streams to apply later on a new filesystem. Create a new filesystem, receive the send streams and verify that the file contents are the same as in the original filesystem and that the file holes exists in both snapshots.

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick send fiemap` declares tags `auto quick send fiemap`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`. sourced helpers: `./common/preamble`, `./common/filter`, `./common/punch`; requirements: `_require_test`, `_require_scratch`, `_require_xfs_io_command "fiemap"`, `_require_btrfs_no_compress`; local shell helpers: `_cleanup()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `rm -fr $send_files_dir`; `rm -f $tmp.*`; `_require_scratch`; `_require_btrfs_no_compress`; `send_files_dir=$TEST_DIR/btrfs-test-$seq`; `mkdir $send_files_dir`; `_scratch_mount`; `$XFS_IO_PROG -f -c "pwrite -S 0xaa -b 64k 0 64K" $SCRATCH_MNT/foo | _filter_xfs_io`; `-c "pwrite -S 0xaa -b 64k 0 64K" \`; `-c "pwrite -S 0xbb -b 64k 1088K 64K" \`; `$BTRFS_UTIL_PROG subvolume snapshot -r $SCRATCH_MNT \`; `$BTRFS_UTIL_PROG send -p $SCRATCH_MNT/snap1 -f $send_files_dir/2.snap \`; `$SCRATCH_MNT/snap2 2>&1 | _filter_scratch`; `_scratch_unmount`; `$BTRFS_UTIL_PROG receive -f $send_files_dir/1.snap $SCRATCH_MNT >/dev/null`; `$BTRFS_UTIL_PROG receive -f $send_files_dir/2.snap $SCRATCH_MNT >/dev/null`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Subvolume roots, read-only snapshots, deleted snapshot orphans, and directory entries are persisted across remounts. Send streams, fssum manifests, and received snapshots are temporary artifacts used to compare source and reconstructed filesystems. The script records user-visible checksums, listings, device counters, capabilities, or byte dumps as evidence. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick send fiemap` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Send tests can be fragile around inode-number ordering, rename dependencies, clone commands, xattrs, and receiver mount options. Compression, inline-extent thresholds, and page or sector size can change the exact layout being exercised.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. Before/after checksums must match across remount, balance, or receive.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/137 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/138 -->
# sources/test-tools/xfstests/tests/btrfs/138

## Purpose

`sources/test-tools/xfstests/tests/btrfs/138` is btrfs fstests case `138`. It targets compression interactions. Source comments describe the scenario as: Test decompression in the middle of large extents. Regression test for Linux kernel commit 6e78b3f7a193 ("Btrfs: fix btrfs_decompress_buf2page()"). Need 1GB for the uncompressed file plus <1GB for each compressed file. Checksum a piece in the middle of the file. This hits the unaligned case that caused the original bug. Create a large, uncompressed (but compressible) file. Copy the same data, but with compression enabled. The correct data is likely still cached. Cycle the mount to drop the cache and start fresh. Check the checksum.

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto compress` declares tags `auto compress`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_scratch`, `_require_btrfs_command property`, `_require_btrfs_no_nodatacow`, `_require_fs_space $SCRATCH_MNT $((1024 * 1024 * (1 + ${#algos[@]})))`; local shell helpers: `do_csum()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_require_scratch`; `_require_btrfs_command property`; `_require_btrfs_no_nodatacow`; `algos=($(_btrfs_compression_algos))`; `_scratch_mkfs >>$seqres.full 2>&1`; `_scratch_mount`; `dd if="$1" bs=4K skip=555 count=100 2>>$seqres.full| md5sum | cut -d ' ' -f 1`; `touch "${SCRATCH_MNT}/uncompressed"`; `$BTRFS_UTIL_PROG property set "${SCRATCH_MNT}/uncompressed" compression ""`; `_ddt of="${SCRATCH_MNT}/uncompressed" bs=1M count=1K 2>&1 | _filter_dd`; `csum="$(do_csum "${SCRATCH_MNT}/uncompressed")"`; `touch "${SCRATCH_MNT}/${algo}"`; `$BTRFS_UTIL_PROG property set "${SCRATCH_MNT}/${algo}" compression "${algo}"`; `dd if="${SCRATCH_MNT}/uncompressed" of="${SCRATCH_MNT}/${algo}" bs=1M 2>&1 | _filter_dd`; `_scratch_cycle_mount`; `compressed_csum="$(do_csum "${SCRATCH_MNT}/${algo}")"`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. The script records user-visible checksums, listings, device counters, capabilities, or byte dumps as evidence. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto compress` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

It may be slow or disruptive because it reformats scratch storage and may use fault injection or degraded-device mounts. Compression, inline-extent thresholds, and page or sector size can change the exact layout being exercised.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. Most success is absence of unexpected output, ending with `Silence is golden`. Before/after checksums must match across remount, balance, or receive.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/138 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/139 -->
# sources/test-tools/xfstests/tests/btrfs/139

## Purpose

`sources/test-tools/xfstests/tests/btrfs/139` is btrfs fstests case `139`. It targets quota-group accounting and limits. Source comments describe the scenario as: Check if btrfs quota limits are not reached when you constantly create and delete files within the exclusive qgroup limits. Finally we create files to exceed the quota. We at least need 2GB of free space on $SCRATCH_DEV This test requires specific data space usage, skip if we have compression enabled. Write and delete files within 1G limits, multiple times Exceed the limits here

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto qgroup limit` declares tags `auto qgroup limit`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_scratch_size $((2 * 1024 * 1024))`, `_require_no_compress`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_require_scratch_size $((2 * 1024 * 1024))`; `_scratch_mkfs > /dev/null 2>&1`; `_scratch_mount`; `SUBVOL=$SCRATCH_MNT/subvol`; `_btrfs subvolume create $SUBVOL`; `_btrfs quota enable $SCRATCH_MNT`; `_qgroup_rescan $SCRATCH_MNT`; `_btrfs qgroup limit -e 1G $SUBVOL`; `$XFS_IO_PROG -f -c "pwrite 0 4m" $SUBVOL/file_$j > /dev/null`; `rm -f $SUBVOL/file*`; `$XFS_IO_PROG -f -c "pwrite 0 128m" $SUBVOL/file_$j 2>&1 | _filter_xfs_io | _filter_xfs_io_error`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Subvolume roots, read-only snapshots, deleted snapshot orphans, and directory entries are persisted across remounts. Quota-group counters, limits, inherited qgroups, and rescan results are kernel-maintained metadata validated at unmount/check time. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto qgroup limit` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

It may be slow or disruptive because it reformats scratch storage and may use fault injection or degraded-device mounts. Qgroup tests are sensitive to delayed accounting, rescan completion, and checker support for quota validation.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/139 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/140 -->
# sources/test-tools/xfstests/tests/btrfs/140

## Purpose

`sources/test-tools/xfstests/tests/btrfs/140` is btrfs fstests case `140`. It targets multi-device or RAID volume behavior, checksum, scrub, or read-repair paths. Source comments describe the scenario as: Regression test for btrfs DIO read's repair during read. Commit 2dabb3248453 ("Btrfs: Direct I/O read: Work on sectorsized blocks") introduced the regression. The upstream fix is commit 2e949b0a5592 ("Btrfs: fix invalid dereference in btrfs_retry_endio") No data checksums for NOCOW and NODATACOW cases, so can't detect corruption and repair data. Overwriting data is forbidden on a zoned block device step 1, create a raid1 btrfs which contains one 128k file. make sure data is written to the start position of the data chunk

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick read_repair fiemap raid` declares tags `auto quick read_repair fiemap raid`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_scratch_dev_pool 2`, `_require_btrfs_no_nodatacow`, `_require_btrfs_no_nodatasum`, `_require_btrfs_command inspect-internal dump-tree`, `_require_odirect`, `_require_non_zoned_device "${SCRATCH_DEV}"`; local shell helpers: `get_physical()`, `get_devid()`, `get_device_path()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_require_scratch_dev_pool 2`; `_require_btrfs_no_nodatacow`; `_require_btrfs_no_nodatasum`; `_require_btrfs_command inspect-internal dump-tree`; `_require_non_zoned_device "${SCRATCH_DEV}"`; `get_device_path()`; `_scratch_mount $(_btrfs_no_v1_cache_opt)`; `$XFS_IO_PROG -f -d -c "pwrite -S 0xaa -b 128K 0 128K" "$SCRATCH_MNT/foobar" |\`; `devpath=$(get_device_path ${devid})`; `$XFS_IO_PROG -d -c "pread -v -b 512 $physical 512" $devpath |\`; `$XFS_IO_PROG -d -c "pwrite -S 0xbb -b 64K $physical 64K" $devpath > /dev/null`; `_btrfs_direct_read_on_mirror 1 2 "$SCRATCH_MNT/foobar" 0 128K`; `finalcsum=$(_md5_checksum $final)`; `rm -f $final`; `_scratch_dev_pool_put`; `[ "$origcsum" == "$finalcsum" ] || _fail "repair failed, csums don't match"`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Device identity, missing-device state, degraded mounts, and balance/repair writes are part of the persistent test surface. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick read_repair fiemap raid` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Multi-device tests need enough disposable devices and can leave device scans cached if cleanup does not run.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. Before/after checksums must match across remount, balance, or receive.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/140 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/141 -->
# sources/test-tools/xfstests/tests/btrfs/141

## Purpose

`sources/test-tools/xfstests/tests/btrfs/141` is btrfs fstests case `141`. It targets multi-device or RAID volume behavior, checksum, scrub, or read-repair paths. Source comments describe the scenario as: Regression test for btrfs buffered read's repair during read. Commit 20a7db8ab3f2 ("btrfs: add dummy callback for readpage_io_failed and drop checks") introduced the regression. The upstream fix is Commit 9d0d1c8b1c9d ("Btrfs: bring back repair during read") No data checksums for NOCOW and NODATACOW cases, so can't detect corruption and repair data. step 1, create a raid1 btrfs which contains one 128k file. make sure data is written to the start position of the data chunk step 2, corrupt the first 64k of one copy (on SCRATCH_DEV which is the first

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick read_repair raid` declares tags `auto quick read_repair raid`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_btrfs_no_nodatacow`, `_require_btrfs_no_nodatasum`, `_require_scratch_dev_pool 2`, `_require_btrfs_command inspect-internal dump-tree`; local shell helpers: `get_physical()`, `get_devid()`, `get_device_path()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_require_btrfs_no_nodatacow`; `_require_btrfs_no_nodatasum`; `_require_scratch_dev_pool 2`; `_require_btrfs_command inspect-internal dump-tree`; `$BTRFS_UTIL_PROG inspect-internal dump-tree -t 3 $SCRATCH_DEV | \`; `get_device_path()`; `_scratch_mount $(_btrfs_no_v1_cache_opt)`; `$XFS_IO_PROG -f -d -c "pwrite -S 0xaa -b 128K 0 128K" "$SCRATCH_MNT/foobar" |\`; `devpath=$(get_device_path ${devid})`; `$XFS_IO_PROG -c "pread -v -b 512 $physical 512" $devpath |\`; `$XFS_IO_PROG -d -c "pwrite -S 0xbb -b 64K $physical 64K" $devpath > /dev/null`; `_btrfs_buffered_read_on_mirror 1 2 "$SCRATCH_MNT/foobar" 0 128K`; `finalcsum=$(_md5_checksum $final)`; `rm -f $final`; `_scratch_dev_pool_put`; `[ "$origcsum" == "$finalcsum" ] || _fail "repair failed, csums don't match"`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Device identity, missing-device state, degraded mounts, and balance/repair writes are part of the persistent test surface. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick read_repair raid` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Multi-device tests need enough disposable devices and can leave device scans cached if cleanup does not run.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. Before/after checksums must match across remount, balance, or receive.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/141 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/142 -->
# sources/test-tools/xfstests/tests/btrfs/142

## Purpose

`sources/test-tools/xfstests/tests/btrfs/142` is btrfs fstests case `142`. It targets multi-device or RAID volume behavior, checksum, scrub, or read-repair paths. Source comments describe the scenario as: Regression test for btrfs DIO read's repair during read without checksum. Commit 2dabb3248453 ("Btrfs: Direct I/O read: Work on sectorsized blocks") introduced this regression.  It'd cause 'Segmentation fault' error. The upstream fix is commit 97bf5a5589aa ("Btrfs: fix segmentation fault when doing dio read") step 1, create a raid1 btrfs which contains one 128k file. make sure data is written to the start position of the data chunk step 2, corrupt the first 64k of stripe #1 step 3, 128k dio read (this read can repair bad copy) check if the repair works

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick read_repair raid` declares tags `auto quick read_repair raid`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`. sourced helpers: `./common/preamble`, `./common/filter`, `./common/dmdust`; requirements: `_require_scratch_dev_pool 2`, `_require_dm_target dust`, `_require_btrfs_command inspect-internal dump-tree`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_require_scratch_dev_pool 2`; `_require_dm_target dust`; `_require_btrfs_command inspect-internal dump-tree`; `_scratch_dev_pool_get 2`; `echo "step 1......mkfs.btrfs" >>$seqres.full`; `_scratch_mount -o nodatasum $(_btrfs_no_v1_cache_opt)`; `$XFS_IO_PROG -f -d -c "pwrite -S 0xaa -b 128K 0 128K" "$SCRATCH_MNT/foobar" |\`; `$XFS_IO_PROG -d -c "pwrite -S 0xbb -b 64K $physical 64K" "$SCRATCH_DEV" > /dev/null`; `_mount_dust`; `$DMSETUP_PROG message dust-test.$seq 0 enable`; `_btrfs_direct_read_on_mirror $stripe 2 "$SCRATCH_MNT/foobar" 0 128K`; `_cleanup_dust`; `$XFS_IO_PROG -c "pread -v -b 512 $physical 512" "$SCRATCH_DEV" |`; `_scratch_dev_pool_put`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Device identity, missing-device state, degraded mounts, and balance/repair writes are part of the persistent test surface. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick read_repair raid` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Multi-device tests need enough disposable devices and can leave device scans cached if cleanup does not run. Fault-injection timing must hit the intended mirror or stripe; otherwise the bug path may not execute.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/142 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/143 -->
# sources/test-tools/xfstests/tests/btrfs/143

## Purpose

`sources/test-tools/xfstests/tests/btrfs/143` is btrfs fstests case `143`. It targets multi-device or RAID volume behavior, checksum, scrub, or read-repair paths. Source comments describe the scenario as: Regression test for btrfs buffered read's repair during read without checksum. This is to test whether buffered read retry-repair code is able to work in raid1 case as expected. Please note that without checksum, btrfs doesn't know if the data used to repair is correct, so repair is more of resync which makes sure that both of the copy has the same content. Commit 20a7db8ab3f2 ("btrfs: add dummy callback for readpage_io_failed and drop checks") introduced the regression. The upstream fix is commit 9d0d1c8b1c9d ("Btrfs: bring back repair during read")

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick read_repair raid` declares tags `auto quick read_repair raid`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`. sourced helpers: `./common/preamble`, `./common/filter`, `./common/dmdust`; requirements: `_require_scratch_dev_pool 2`, `_require_dm_target dust`, `_require_btrfs_command inspect-internal dump-tree`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_require_scratch_dev_pool 2`; `_require_dm_target dust`; `_require_btrfs_command inspect-internal dump-tree`; `_scratch_dev_pool_get 2`; `echo "step 1......mkfs.btrfs" >>$seqres.full`; `_scratch_mount -o nodatasum $(_btrfs_no_v1_cache_opt)`; `$XFS_IO_PROG -f -d -c "pwrite -S 0xaa -b 128K 0 128K" "$SCRATCH_MNT/foobar" |\`; `$XFS_IO_PROG -d -c "pwrite -S 0xbb -b 64K $physical 64K" "$SCRATCH_DEV" > /dev/null`; `_mount_dust`; `$DMSETUP_PROG message dust-test.$seq 0 enable`; `_btrfs_buffered_read_on_mirror $stripe 2 "$SCRATCH_MNT/foobar" 0 128K`; `_cleanup_dust`; `$XFS_IO_PROG -c "pread -v -b 512 $physical 512" "$SCRATCH_DEV" |`; `_scratch_dev_pool_put`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Device identity, missing-device state, degraded mounts, and balance/repair writes are part of the persistent test surface. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick read_repair raid` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Multi-device tests need enough disposable devices and can leave device scans cached if cleanup does not run. Fault-injection timing must hit the intended mirror or stripe; otherwise the bug path may not execute.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/143 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/144 -->
# sources/test-tools/xfstests/tests/btrfs/144

## Purpose

`sources/test-tools/xfstests/tests/btrfs/144` is btrfs fstests case `144`. It targets send/receive stream correctness. Source comments describe the scenario as: Test that an incremental send operation works correctly when an inode A is renamed, a new hard link added to it and some other inode B is renamed to the old name of inode A. Filesystem looks like: .                                                             (ino 256) |--- f1                                                       (ino 257) |--- f2                                                       (ino 258) |--- f3                                                       (ino 259) Filesystem now looks like: .                                                             (ino 256)

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick send` declares tags `auto quick send`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; snapshot equivalence is checked with `$FSSUM_PROG`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_test`, `_require_scratch`, `_require_fssum`; local shell helpers: `_cleanup()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `rm -fr $send_files_dir`; `rm -f $tmp.*`; `_require_scratch`; `_require_fssum`; `send_files_dir=$TEST_DIR/btrfs-test-$seq`; `mkdir $send_files_dir`; `_scratch_mount`; `$BTRFS_UTIL_PROG subvolume snapshot -r $SCRATCH_MNT \`; `$BTRFS_UTIL_PROG send -f $send_files_dir/1.snap \`; `$BTRFS_UTIL_PROG send -p $SCRATCH_MNT/mysnap1 -f $send_files_dir/2.snap \`; `$FSSUM_PROG -A -f -w $send_files_dir/1.fssum $SCRATCH_MNT/mysnap1`; `_scratch_unmount`; `$BTRFS_UTIL_PROG receive -f $send_files_dir/1.snap $SCRATCH_MNT > /dev/null`; `$BTRFS_UTIL_PROG receive -f $send_files_dir/2.snap $SCRATCH_MNT > /dev/null`; `$FSSUM_PROG -r $send_files_dir/1.fssum $SCRATCH_MNT/mysnap1`; `$FSSUM_PROG -r $send_files_dir/2.fssum $SCRATCH_MNT/mysnap2`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Subvolume roots, read-only snapshots, deleted snapshot orphans, and directory entries are persisted across remounts. Send streams, fssum manifests, and received snapshots are temporary artifacts used to compare source and reconstructed filesystems. The script records user-visible checksums, listings, device counters, capabilities, or byte dumps as evidence. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick send` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Send tests can be fragile around inode-number ordering, rename dependencies, clone commands, xattrs, and receiver mount options.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. `fssum` manifests are written on source snapshots and verified after receive.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/144 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/145 -->
# sources/test-tools/xfstests/tests/btrfs/145

## Purpose

`sources/test-tools/xfstests/tests/btrfs/145` is btrfs fstests case `145`. It targets send/receive stream correctness. Source comments describe the scenario as: Test that an incremental send works if we rename some directory inode A and then rename some file inode B to the name inode A had, for the case where the directory inode A is an ancestor of inode B in the parent snapshot. Filesystem looks like: .                                                      (ino 256) |--- dir1/                                             (ino 257) |--- dir2/                                       (ino 258) |     |--- file1                                 (ino 259) |     |--- file3                                 (ino 261) |--- dir3/                                       (ino 262)

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick send` declares tags `auto quick send`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; snapshot equivalence is checked with `$FSSUM_PROG`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_test`, `_require_scratch`, `_require_fssum`; local shell helpers: `_cleanup()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `rm -fr $send_files_dir`; `rm -f $tmp.*`; `_require_scratch`; `_require_fssum`; `send_files_dir=$TEST_DIR/btrfs-test-$seq`; `mkdir $send_files_dir`; `_scratch_mount`; `$BTRFS_UTIL_PROG subvolume snapshot -r $SCRATCH_MNT \`; `$BTRFS_UTIL_PROG send -f $send_files_dir/1.snap \`; `$BTRFS_UTIL_PROG send -p $SCRATCH_MNT/mysnap1 -f $send_files_dir/2.snap \`; `$FSSUM_PROG -A -f -w $send_files_dir/1.fssum $SCRATCH_MNT/mysnap1`; `_scratch_unmount`; `$BTRFS_UTIL_PROG receive -f $send_files_dir/1.snap $SCRATCH_MNT > /dev/null`; `$BTRFS_UTIL_PROG receive -f $send_files_dir/2.snap $SCRATCH_MNT > /dev/null`; `$FSSUM_PROG -r $send_files_dir/1.fssum $SCRATCH_MNT/mysnap1`; `$FSSUM_PROG -r $send_files_dir/2.fssum $SCRATCH_MNT/mysnap2`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Subvolume roots, read-only snapshots, deleted snapshot orphans, and directory entries are persisted across remounts. Send streams, fssum manifests, and received snapshots are temporary artifacts used to compare source and reconstructed filesystems. The script records user-visible checksums, listings, device counters, capabilities, or byte dumps as evidence. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick send` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Send tests can be fragile around inode-number ordering, rename dependencies, clone commands, xattrs, and receiver mount options.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. `fssum` manifests are written on source snapshots and verified after receive.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/145 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/146 -->
# sources/test-tools/xfstests/tests/btrfs/146

## Purpose

`sources/test-tools/xfstests/tests/btrfs/146` is btrfs fstests case `146`. It targets multi-device or RAID volume behavior. Source comments describe the scenario as: Open a file several times, write to it, fsync on all fds and make sure that they all return 0. Change the device to start throwing errors. Write again on all fds and fsync on all fds. Ensure that we get errors on all of them. Then fsync on all one last time and verify that all return 0. bring up dmerror device Replace first device with error-test device Build a filesystem with 2 devices that stripes the data across both devices, but mirrors metadata across both. Then, make one of the devices fail and test what it does. How much do we need to write? We need to hit all of the stripes. btrfs uses a

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick eio raid` declares tags `auto quick eio raid`; environment gates are expressed through `_require*` helpers. sourced helpers: `./common/preamble`, `./common/filter`, `./common/dmerror`; requirements: `_require_scratch`, `_require_scratch_dev_pool`, `_require_dm_target error`, `_require_test_program fsync-err`, `_require_test_program dmerror`, `_require_fs_space $SCRATCH_MNT $write_kb`; local shell helpers: `_cleanup()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `rm -rf $tmp.* $testdir`; `_dmerror_cleanup`; `_require_scratch`; `_require_scratch_dev_pool`; `_require_test_program fsync-err`; `_require_test_program dmerror`; `_dmerror_init`; `_scratch_mount`; `number_of_devices=\`echo $SCRATCH_DEV_POOL | wc -w\``; `write_kb=$(($number_of_devices * 2048))`; `testfile=$SCRATCH_MNT/fsync-err-test`; `SCRATCH_DEV=$old_SCRATCH_DEV`; `$here/src/fsync-err -b $(($write_kb * 1024)) -d "$here/src/dmerror $seq" $testfile`; `_dmerror_load_working_table`; `_repair_scratch_fs >> $seqres.full`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Device identity, missing-device state, degraded mounts, and balance/repair writes are part of the persistent test surface. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick eio raid` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Multi-device tests need enough disposable devices and can leave device scans cached if cleanup does not run. Fault-injection timing must hit the intended mirror or stripe; otherwise the bug path may not execute.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/146 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/147 -->
# sources/test-tools/xfstests/tests/btrfs/147

## Purpose

`sources/test-tools/xfstests/tests/btrfs/147` is btrfs fstests case `147`. It targets send/receive stream correctness. Source comments describe the scenario as: Test that an incremental send/receive operation works correctly after moving some directory inode A, renaming a regular file inode B into the old name of inode A and finally creating a new hard link for inode B at directory inode A. Filesystem looks like: .                                                      (ino 256) |--- dir1/                                             (ino 257) |      |--- dir2/                                      (ino 258) |             |--- dir3/                               (ino 259) |                   |--- file1                         (ino 261) |                   |--- dir4/                         (ino 262)

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick send` declares tags `auto quick send`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; snapshot equivalence is checked with `$FSSUM_PROG`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_test`, `_require_scratch`, `_require_fssum`; local shell helpers: `_cleanup()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `rm -fr $send_files_dir`; `rm -f $tmp.*`; `_require_scratch`; `_require_fssum`; `send_files_dir=$TEST_DIR/btrfs-test-$seq`; `mkdir $send_files_dir`; `_scratch_mount`; `$BTRFS_UTIL_PROG subvolume snapshot -r $SCRATCH_MNT \`; `$BTRFS_UTIL_PROG send -f $send_files_dir/1.snap \`; `$BTRFS_UTIL_PROG send -p $SCRATCH_MNT/mysnap1 -f $send_files_dir/2.snap \`; `$FSSUM_PROG -A -f -w $send_files_dir/1.fssum $SCRATCH_MNT/mysnap1`; `_scratch_unmount`; `$BTRFS_UTIL_PROG receive -f $send_files_dir/1.snap $SCRATCH_MNT > /dev/null`; `$BTRFS_UTIL_PROG receive -f $send_files_dir/2.snap $SCRATCH_MNT > /dev/null`; `$FSSUM_PROG -r $send_files_dir/1.fssum $SCRATCH_MNT/mysnap1`; `$FSSUM_PROG -r $send_files_dir/2.fssum $SCRATCH_MNT/mysnap2`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Subvolume roots, read-only snapshots, deleted snapshot orphans, and directory entries are persisted across remounts. Send streams, fssum manifests, and received snapshots are temporary artifacts used to compare source and reconstructed filesystems. The script records user-visible checksums, listings, device counters, capabilities, or byte dumps as evidence. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick send` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Send tests can be fragile around inode-number ordering, rename dependencies, clone commands, xattrs, and receiver mount options.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. `fssum` manifests are written on source snapshots and verified after receive.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/147 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/148 -->
# sources/test-tools/xfstests/tests/btrfs/148

## Purpose

`sources/test-tools/xfstests/tests/btrfs/148` is btrfs fstests case `148`. It targets multi-device or RAID volume behavior, checksum, scrub, or read-repair paths. Source comments describe the scenario as: Test that direct IO writes work on RAID5 and RAID6 filesystems. Now read back the same data, we expect to get what we wrote before.

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick rw scrub raid` declares tags `auto quick rw scrub raid`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_scratch`, `_require_scratch_dev_pool 4`, `_require_odirect`, `_require_btrfs_raid_type raid5`, `_require_btrfs_raid_type raid6`; local shell helpers: `test_direct_io_write()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_require_scratch`; `_require_scratch_dev_pool 4`; `_require_btrfs_raid_type raid5`; `_require_btrfs_raid_type raid6`; `_scratch_dev_pool_get 4`; `_scratch_mount`; `$XFS_IO_PROG -f -d -c "pwrite -S 0xab 0 1M" $SCRATCH_MNT/foo \`; `_scratch_cycle_mount`; `$BTRFS_UTIL_PROG scrub start -B $SCRATCH_MNT >>$seqres.full 2>&1`; `_scratch_unmount`; `test_direct_io_write "-m raid5 -d raid5"`; `test_direct_io_write "-m raid6 -d raid6"`; `_scratch_dev_pool_put`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Device identity, missing-device state, degraded mounts, and balance/repair writes are part of the persistent test surface. The script records user-visible checksums, listings, device counters, capabilities, or byte dumps as evidence. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick rw scrub raid` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Multi-device tests need enough disposable devices and can leave device scans cached if cleanup does not run.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. A foreground scrub must complete without reported errors.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/148 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/149 -->
# sources/test-tools/xfstests/tests/btrfs/149

## Purpose

`sources/test-tools/xfstests/tests/btrfs/149` is btrfs fstests case `149`. It targets send/receive stream correctness, compression interactions. Source comments describe the scenario as: Test that an incremental send/receive operation will not fail when the destination filesystem has compression enabled and the source filesystem has an extent at a file offset 0 that is not compressed and that is shared. On 64K pagesize systems the compression is more efficient, so max_inline helps to create regular (non inline) extent irrespective of the final write size. Write to our file using direct IO, so that this way the write ends up not getting compressed, that is, we get a regular extent which is neither inlined nor compressed.

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick send compress` declares tags `auto quick send compress`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`. sourced helpers: `./common/preamble`, `./common/filter`, `./common/reflink`; requirements: `_require_test`, `_require_scratch`, `_require_scratch_reflink`, `_require_odirect`, `_require_btrfs_command inspect-internal dump-super`; local shell helpers: `_cleanup()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `rm -fr $send_files_dir`; `rm -f $tmp.*`; `_require_scratch`; `_require_scratch_reflink`; `_require_btrfs_command inspect-internal dump-super`; `send_files_dir=$TEST_DIR/btrfs-test-$seq`; `mkdir $send_files_dir`; `_scratch_mount "-o compress -o max_inline=0"`; `$XFS_IO_PROG -f -d -c "pwrite -S 0xab 0 $sectorsize" $SCRATCH_MNT/foobar |\`; `$BTRFS_UTIL_PROG subvolume snapshot -r $SCRATCH_MNT \`; `"reflink $SCRATCH_MNT/foobar 0 $((2 * $sectorsize)) $sectorsize" \`; `$BTRFS_UTIL_PROG receive -f $send_files_dir/2.snap $SCRATCH_MNT > /dev/null`; `sum_dest_snap1=$(md5sum $SCRATCH_MNT/mysnap1/foobar | $AWK_PROG '{print $1}')`; `sum_dest_snap2=$(md5sum $SCRATCH_MNT/mysnap2/foobar | $AWK_PROG '{print $1}')`; `[[ $sum_src_snap1 == $sum_dest_snap1 ]] && echo "src and dest 'mysnap1' checksum matched"`; `[[ $sum_src_snap2 == $sum_dest_snap2 ]] && echo "src and dest 'mysnap2' checksum matched"`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Subvolume roots, read-only snapshots, deleted snapshot orphans, and directory entries are persisted across remounts. Send streams, fssum manifests, and received snapshots are temporary artifacts used to compare source and reconstructed filesystems. The script records user-visible checksums, listings, device counters, capabilities, or byte dumps as evidence. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick send compress` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Send tests can be fragile around inode-number ordering, rename dependencies, clone commands, xattrs, and receiver mount options. Compression, inline-extent thresholds, and page or sector size can change the exact layout being exercised.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. Before/after checksums must match across remount, balance, or receive.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/149 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/150 -->
# sources/test-tools/xfstests/tests/btrfs/150

## Purpose

`sources/test-tools/xfstests/tests/btrfs/150` is btrfs fstests case `150`. It targets multi-device or RAID volume behavior, compression interactions, checksum, scrub, or read-repair paths, fault-injection or destructive-device conditions. Source comments describe the scenario as: This is a regression test which ends up with a kernel oops in btrfs. It occurs when btrfs's read repair happens while reading a compressed extent. The patch to fix it is Btrfs: fix kernel oops while reading compressed data It doesn't matter which compression algorithm we use. Create a file with all data being compressed Raid1 consists of two copies and btrfs decides which copy to read by reader's %pid.  Now we inject errors to copy #1 and copy #0 is good.  We want to read the bad copy to trigger read-repair.

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick dangerous read_repair compress raid` declares tags `auto quick dangerous read_repair compress raid`; environment gates are expressed through `_require*` helpers; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`. sourced helpers: `./common/preamble`, `./common/filter`, `./common/fail_make_request`; requirements: `_require_debugfs`, `_require_scratch`, `_require_fail_make_request`, `_require_scratch_dev_pool 2`; local shell helpers: `enable_io_failure()`, `disable_io_failure()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_require_scratch`; `_require_fail_make_request`; `_require_scratch_dev_pool 2`; `_scratch_dev_pool_get 2`; `_allow_fail_make_request 100 1000 > /dev/null`; `_scratch_mount -ocompress`; `$XFS_IO_PROG -f -c "pwrite -W 0 8K" $SCRATCH_MNT/foobar | _filter_xfs_io`; `$XFS_IO_PROG -f -c "fadvise -d 0 8K" $SCRATCH_MNT/foobar`; `echo 1 > /proc/\$\$/make-it-fail`; `exec $XFS_IO_PROG -c \"pread 0 8K\" \$SCRATCH_MNT/foobar`; `_scratch_dev_pool_put`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Device identity, missing-device state, degraded mounts, and balance/repair writes are part of the persistent test surface. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick dangerous read_repair compress raid` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

It may be slow or disruptive because it reformats scratch storage and may use fault injection or degraded-device mounts. Multi-device tests need enough disposable devices and can leave device scans cached if cleanup does not run. Compression, inline-extent thresholds, and page or sector size can change the exact layout being exercised. Fault-injection timing must hit the intended mirror or stripe; otherwise the bug path may not execute.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/150 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/151 -->
# sources/test-tools/xfstests/tests/btrfs/151

## Purpose

`sources/test-tools/xfstests/tests/btrfs/151` is btrfs fstests case `151`. It targets multi-device or RAID volume behavior. Source comments describe the scenario as: Test if it's losing data chunk's raid profile after 'btrfs device remove'. The fix is Btrfs: avoid losing data raid profile when deleting a device We need exactly 3 disks to form a fixed stripe layout for this test. create raid1 for data we need an empty data chunk, so $(_btrfs_no_v1_cache_opt) is required. if data chunk is empty, 'btrfs device remove' can change raid1 to single. save btrfs filesystem df output for debug purpose

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick volume raid` declares tags `auto quick volume raid`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_scratch`, `_require_scratch_dev_pool 3`, `_require_btrfs_dev_del_by_devid`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_require_scratch`; `_require_scratch_dev_pool 3`; `_require_btrfs_dev_del_by_devid`; `_check_minimal_fs_size $(( 1024 * 1024 * 1024 ))`; `_scratch_dev_pool_get 3`; `_scratch_pool_mkfs "-d raid1 -b 1G" >> $seqres.full 2>&1`; `_scratch_mount $(_btrfs_no_v1_cache_opt)`; `$BTRFS_UTIL_PROG device delete 2 $SCRATCH_MNT >> $seqres.full 2>&1`; `$BTRFS_UTIL_PROG filesystem df $SCRATCH_MNT 2>&1 | \`; `_scratch_dev_pool_put`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Device identity, missing-device state, degraded mounts, and balance/repair writes are part of the persistent test surface. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick volume raid` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Multi-device tests need enough disposable devices and can leave device scans cached if cleanup does not run.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/151 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/152 -->
# sources/test-tools/xfstests/tests/btrfs/152

## Purpose

`sources/test-tools/xfstests/tests/btrfs/152` is btrfs fstests case `152`. It targets quota-group accounting and limits, send/receive stream correctness. Source comments describe the scenario as: Test that incremental send/receive operations don't corrupt metadata when qgroups are enabled. Enable quotas Create 2 source and 4 destination subvolumes Create base snapshots and send them Now do 10 loops of concurrent incremental send/receives

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick metadata qgroup send` declares tags `auto quick metadata qgroup send`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_scratch`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_require_scratch`; `_scratch_mkfs >>$seqres.full 2>&1`; `_scratch_mount`; `$BTRFS_UTIL_PROG quota enable $SCRATCH_MNT`; `$BTRFS_UTIL_PROG subvolume create $SCRATCH_MNT/$subvol | _filter_scratch`; `mkdir $SCRATCH_MNT/subvol{1,2}/.snapshots`; `_btrfs subvolume snapshot -r $SCRATCH_MNT/subvol1 $SCRATCH_MNT/subvol1/.snapshots/1`; `_btrfs subvolume snapshot -r $SCRATCH_MNT/subvol2 $SCRATCH_MNT/subvol2/.snapshots/1`; `$BTRFS_UTIL_PROG send $SCRATCH_MNT/subvol1/.snapshots/1 2> /dev/null | \`; `$BTRFS_UTIL_PROG receive $SCRATCH_MNT/${recv} | _filter_scratch`; `_btrfs subvolume snapshot -r $SCRATCH_MNT/subvol1 \`; `($BTRFS_UTIL_PROG send -p $SCRATCH_MNT/subvol2/.snapshots/${prev} \`; `$SCRATCH_MNT/subvol2/.snapshots/${curr} 2> /dev/null | \`; `$BTRFS_UTIL_PROG receive $SCRATCH_MNT/recv2_1) > /dev/null &`; `$BTRFS_UTIL_PROG receive $SCRATCH_MNT/recv2_2) > /dev/null &`; `_scratch_unmount`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Subvolume roots, read-only snapshots, deleted snapshot orphans, and directory entries are persisted across remounts. Quota-group counters, limits, inherited qgroups, and rescan results are kernel-maintained metadata validated at unmount/check time. Send streams, fssum manifests, and received snapshots are temporary artifacts used to compare source and reconstructed filesystems. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick metadata qgroup send` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Qgroup tests are sensitive to delayed accounting, rescan completion, and checker support for quota validation. Send tests can be fragile around inode-number ordering, rename dependencies, clone commands, xattrs, and receiver mount options.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/152 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/153 -->
# sources/test-tools/xfstests/tests/btrfs/153

## Purpose

`sources/test-tools/xfstests/tests/btrfs/153` is btrfs fstests case `153`. It targets quota-group accounting and limits. Source comments describe the scenario as: Test for leaking quota reservations on preallocated files.

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick qgroup limit preallocrw` declares tags `auto quick qgroup limit preallocrw`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_scratch`, `_require_btrfs_qgroup_report`, `_require_xfs_io_command "falloc"`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_require_scratch`; `_require_btrfs_qgroup_report`; `_require_xfs_io_command "falloc"`; `_scratch_mkfs >/dev/null`; `_scratch_mount`; `_btrfs quota enable $SCRATCH_MNT`; `_qgroup_rescan $SCRATCH_MNT`; `_btrfs qgroup limit 100M 0/5 $SCRATCH_MNT`; `testfile1=$SCRATCH_MNT/testfile1`; `testfile2=$SCRATCH_MNT/testfile2`; `$XFS_IO_PROG -fc "falloc 0 80M" $testfile1`; `$XFS_IO_PROG -fc "pwrite 0 80M" $testfile1 > /dev/null`; `$XFS_IO_PROG -fc "falloc 0 19M" $testfile2`; `$XFS_IO_PROG -fc "pwrite 0 19M" $testfile2 > /dev/null`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Quota-group counters, limits, inherited qgroups, and rescan results are kernel-maintained metadata validated at unmount/check time. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick qgroup limit preallocrw` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Qgroup tests are sensitive to delayed accounting, rescan completion, and checker support for quota validation.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. Most success is absence of unexpected output, ending with `Silence is golden`. fstests scratch checking validates filesystem and qgroup consistency after unmount.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/153 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/154 -->
# sources/test-tools/xfstests/tests/btrfs/154

## Purpose

`sources/test-tools/xfstests/tests/btrfs/154` is btrfs fstests case `154`. It targets the btrfs feature area named by its fstests tags. Source comments describe the scenario as: Test if btrfs rename handle dir item collision correctly Without patch fix, rename will fail with EOVERFLOW, and filesystem is forced readonly. This bug is going to be fixed by a patch for kernel titled "btrfs: correctly calculate item size used when item key collision happens" Currently in btrfs the node/leaf size can not be smaller than the page size (but it can be greater than the page size). So use the largest supported node/leaf size (64Kb) so that the test can run on any platform that Linux supports. In the following for loop, we'll create a leaf fully occupied by

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick` declares tags `auto quick`; environment gates are expressed through `_require*` helpers. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_scratch`, `_require_command $PYTHON3_PROG python3`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_require_scratch`; `_scratch_mkfs "--nodesize 65536" >>$seqres.full 2>&1`; `_scratch_mount`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

The main risk is environmental: missing fstests helpers, unsupported btrfs features, or changed userspace output can turn the test into a notrun or golden-output mismatch.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. Most success is absence of unexpected output, ending with `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/154 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/155 -->
# sources/test-tools/xfstests/tests/btrfs/155

## Purpose

`sources/test-tools/xfstests/tests/btrfs/155` is btrfs fstests case `155`. It targets send/receive stream correctness. Source comments describe the scenario as: Test that an incremental send operation works if a file that has multiple hard links has some of its hard links renamed in the send snapshot, with one of them getting the same path that some other inode had in the send snapshot. Filesystem looks like: .                                                      (ino 256) |---- a/                                               (ino 257) |     |---- b/                                         (ino 259) |     |     |---- c/                                   (ino 260) |     |     |---- f2                                   (ino 261) |     |

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick send` declares tags `auto quick send`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; snapshot equivalence is checked with `$FSSUM_PROG`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_test`, `_require_scratch`, `_require_fssum`; local shell helpers: `_cleanup()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `rm -fr $send_files_dir`; `rm -f $tmp.*`; `_require_scratch`; `_require_fssum`; `send_files_dir=$TEST_DIR/btrfs-test-$seq`; `mkdir $send_files_dir`; `_scratch_mount`; `$BTRFS_UTIL_PROG subvolume snapshot -r $SCRATCH_MNT \`; `$BTRFS_UTIL_PROG send -f $send_files_dir/1.snap \`; `$BTRFS_UTIL_PROG send -p $SCRATCH_MNT/mysnap1 -f $send_files_dir/2.snap \`; `$FSSUM_PROG -A -f -w $send_files_dir/1.fssum $SCRATCH_MNT/mysnap1`; `_scratch_unmount`; `$BTRFS_UTIL_PROG receive -f $send_files_dir/1.snap $SCRATCH_MNT > /dev/null`; `$BTRFS_UTIL_PROG receive -f $send_files_dir/2.snap $SCRATCH_MNT > /dev/null`; `$FSSUM_PROG -r $send_files_dir/1.fssum $SCRATCH_MNT/mysnap1`; `$FSSUM_PROG -r $send_files_dir/2.fssum $SCRATCH_MNT/mysnap2`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Subvolume roots, read-only snapshots, deleted snapshot orphans, and directory entries are persisted across remounts. Send streams, fssum manifests, and received snapshots are temporary artifacts used to compare source and reconstructed filesystems. The script records user-visible checksums, listings, device counters, capabilities, or byte dumps as evidence. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick send` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Send tests can be fragile around inode-number ordering, rename dependencies, clone commands, xattrs, and receiver mount options.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. `fssum` manifests are written on source snapshots and verified after receive.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/155 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/156 -->
# sources/test-tools/xfstests/tests/btrfs/156

## Purpose

`sources/test-tools/xfstests/tests/btrfs/156` is btrfs fstests case `156`. It targets balance relocation behavior. Source comments describe the scenario as: Check if btrfs can correctly trim free space in block groups An ancient regression prevent btrfs from trimming free space inside existing block groups, if bytenr of block group starts beyond btrfs_super_block->total_bytes. However all bytenr in btrfs is in btrfs logical address space, where any bytenr in range [0, U64_MAX] is valid. Fixed by patch named "btrfs: Ensure btrfs_trim_fs can trim the whole fs". We need the allocated space to actually use that amount so the trim amount comes out correctly.  Because we mark free extents as TRIMMED we won't trim the free extents on the second fstrim and thus we'll get a trimmed bytes at <

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick trim balance` declares tags `auto quick trim balance`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_scratch`, `_require_fstrim`, `_require_no_compress`, `_require_batched_discard "$SCRATCH_MNT"`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_require_scratch`; `_require_fstrim`; `_check_minimal_fs_size $fs_size`; `_scratch_mkfs -b $fs_size -m single -d single > /dev/null`; `_scratch_mount`; `$XFS_IO_PROG -f -c "pwrite 0 $file_size" "$SCRATCH_MNT/file_$n" \`; `sync`; `_run_btrfs_balance_start $SCRATCH_MNT >> $seqres.full`; `rm $SCRATCH_MNT/file_*[13579] -f`; `trimmed=$($FSTRIM_PROG -v "$SCRATCH_MNT" | _filter_fstrim)`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick trim balance` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

The main risk is environmental: missing fstests helpers, unsupported btrfs features, or changed userspace output can turn the test into a notrun or golden-output mismatch.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. Most success is absence of unexpected output, ending with `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/156 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/157 -->
# sources/test-tools/xfstests/tests/btrfs/157

## Purpose

`sources/test-tools/xfstests/tests/btrfs/157` is btrfs fstests case `157`. It targets multi-device or RAID volume behavior, checksum, scrub, or read-repair paths. Source comments describe the scenario as: The test case is to reproduce a bug in raid6 reconstruction process that would end up with read failure if there is data corruption on two disks in the same horizontal stripe, e.g.  due to bitrot. The bug happens when a) all disks are good to read, b) there is corrupted data on two disks in the same horizontal stripe due to something like bitrot, c) when rebuilding data after crc fails, btrfs is not able to tell whether other copies are good or corrupted because btrfs doesn't have crc for unallocated blocks.

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick raid read_repair` declares tags `auto quick raid read_repair`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_btrfs_no_nodatacow`, `_require_btrfs_no_nodatasum`, `_require_scratch_dev_pool 4`, `_require_btrfs_command inspect-internal dump-tree`, `_require_btrfs_raid_type raid6`; local shell helpers: `get_physical()`, `get_devid()`, `get_device_path()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_require_btrfs_no_nodatacow`; `_require_btrfs_no_nodatasum`; `_require_scratch_dev_pool 4`; `_require_btrfs_command inspect-internal dump-tree`; `_require_btrfs_raid_type raid6`; `get_device_path()`; `_scratch_mount $(_btrfs_no_v1_cache_opt)`; `$XFS_IO_PROG -f -d -c "pwrite -S 0xaa 0 128K" -c "fsync" \`; `devpath0=$(get_device_path $devid0)`; `devpath1=$(get_device_path $devid1)`; `$XFS_IO_PROG -f -d -c "pwrite -S 0xbb $phy0 64K" $devpath0 > /dev/null`; `$XFS_IO_PROG -f -d -c "pwrite -S 0xbb $phy1 64K" $devpath1 > /dev/null`; `echo "step 3......repair the bitrot" >> $seqres.full`; `od -x -j 64K $SCRATCH_MNT/foobar`; `_scratch_dev_pool_put`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Device identity, missing-device state, degraded mounts, and balance/repair writes are part of the persistent test surface. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick raid read_repair` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Multi-device tests need enough disposable devices and can leave device scans cached if cleanup does not run.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/157 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/158 -->
# sources/test-tools/xfstests/tests/btrfs/158

## Purpose

`sources/test-tools/xfstests/tests/btrfs/158` is btrfs fstests case `158`. It targets multi-device or RAID volume behavior, checksum, scrub, or read-repair paths. Source comments describe the scenario as: The test case is check if scrub is able fix raid6 data corruption, ie. if there is data corruption on two disks in the same horizontal stripe, e.g.  due to bitrot. The kernel fixes are Btrfs: make raid6 rebuild retry more Btrfs: fix scrub to repair raid6 corruption No data checksums for NOCOW and NODATACOW cases, so can't detect corruption and repair data. step 1: create a raid6 btrfs and create a 128K file make sure data is written to the start position of the data chunk

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick raid scrub` declares tags `auto quick raid scrub`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_btrfs_no_nodatacow`, `_require_btrfs_no_nodatasum`, `_require_scratch_dev_pool 4`, `_require_btrfs_command inspect-internal dump-tree`, `_require_btrfs_raid_type raid5`; local shell helpers: `get_physical()`, `get_devid()`, `get_device_path()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_require_btrfs_no_nodatacow`; `_require_btrfs_no_nodatasum`; `_require_scratch_dev_pool 4`; `_require_btrfs_command inspect-internal dump-tree`; `_require_btrfs_raid_type raid5`; `get_device_path()`; `_scratch_mount $(_btrfs_no_v1_cache_opt)`; `$XFS_IO_PROG -f -d -c "pwrite -S 0xaa 0 128K" -c "fsync" \`; `devpath0=$(get_device_path $devid0)`; `devpath1=$(get_device_path $devid1)`; `$XFS_IO_PROG -f -d -c "pwrite -S 0xbb $phy0 64K" $devpath0 > /dev/null`; `$XFS_IO_PROG -f -d -c "pwrite -S 0xbb $phy1 64K" $devpath1 > /dev/null`; `echo "step 3......repair the bitrot" >> $seqres.full`; `$BTRFS_UTIL_PROG scrub start -B $SCRATCH_MNT >> $seqres.full 2>&1`; `od -x $SCRATCH_MNT/foobar`; `_scratch_dev_pool_put`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Device identity, missing-device state, degraded mounts, and balance/repair writes are part of the persistent test surface. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick raid scrub` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Multi-device tests need enough disposable devices and can leave device scans cached if cleanup does not run.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. A foreground scrub must complete without reported errors.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/158 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/159 -->
# sources/test-tools/xfstests/tests/btrfs/159

## Purpose

`sources/test-tools/xfstests/tests/btrfs/159` is btrfs fstests case `159`. It targets log-tree replay and fsync crash recovery. Source comments describe the scenario as: Test that when we have the no-holes mode enabled and a specific metadata layout, if we punch a hole and fsync the file, at replay time the whole hole was preserved. We create the filesystem with a node size of 64Kb because we need to create a specific metadata layout in order to trigger the bug we are testing. At the moment the node size can not be smaller then the system's page size, so given that the largest possible page size is 64Kb and by default the node size is set to the system's page size value, we explicitly create a filesystem with a 64Kb node size. Create our test file with 832 extents of 256Kb each. Before each

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick punch log` declares tags `auto quick punch log`; environment gates are expressed through `_require*` helpers; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`. sourced helpers: `./common/preamble`, `./common/filter`, `./common/dmflakey`; requirements: `_require_scratch`, `_require_dm_target flakey`, `_require_xfs_io_command "fpunch"`, `_require_odirect`, `_require_metadata_journaling $SCRATCH_DEV`; local shell helpers: `_cleanup()`, `run_test()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_cleanup_flakey`; `rm -f $tmp.*`; `_require_scratch`; `_require_dm_target flakey`; `_scratch_mkfs -O no-holes -n $((64 * 1024)) >>$seqres.full 2>&1`; `_init_flakey`; `_scratch_mount`; `$XFS_IO_PROG -f -d -c "pwrite -S 0xab -b 256K $offset 256K" \`; `sync`; `$XFS_IO_PROG -c "fpunch $((punch_offset + 128 * 1024 - 4000)) 256K" \`; `-c "fsync" \`; `md5sum $SCRATCH_MNT/foobar | _filter_scratch`; `_flakey_drop_and_remount`; `_scratch_unmount`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. The dm-flakey helper deliberately drops writes and remounts to force replay of whatever reached the btrfs log tree. The script records user-visible checksums, listings, device counters, capabilities, or byte dumps as evidence. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick punch log` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

The pass/fail signal depends on realistic crash semantics from dm-flakey and on metadata journaling being available.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. Before/after checksums must match across remount, balance, or receive.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/159 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/160 -->
# sources/test-tools/xfstests/tests/btrfs/160

## Purpose

`sources/test-tools/xfstests/tests/btrfs/160` is btrfs fstests case `160`. It targets multi-device or RAID volume behavior. Source comments describe the scenario as: Open a file and write to it and fsync. Then flip the data device to throw errors, write to it again and call sync. Close the file, reopen it and then call fsync on it. Is the error reported? bring up dmerror device Replace first device with error-test device How much do we need to write? We need to hit all of the stripes. btrfs uses a fixed 64k stripesize, so write enough to hit each one. In the case of compression, each 128K input data chunk will be compressed to 4K (because of the characters written are duplicate). Therefore we have to write (128K * 16) = 2048K to make sure every stripe can be hit.

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick eio raid` declares tags `auto quick eio raid`; environment gates are expressed through `_require*` helpers; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`. sourced helpers: `./common/preamble`, `./common/filter`, `./common/dmerror`; requirements: `_require_scratch_dev_pool`, `_require_dm_target error`, `_require_fs_space $SCRATCH_MNT $write_kb`; local shell helpers: `_cleanup()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `rm -f $tmp.*`; `_dmerror_cleanup`; `_require_scratch_dev_pool`; `_dmerror_init`; `old_SCRATCH_DEV=$SCRATCH_DEV`; `_scratch_mount`; `number_of_devices=\`echo $SCRATCH_DEV_POOL | wc -w\``; `write_kb=$(($number_of_devices * 2048))`; `testfile=$SCRATCH_MNT/fsync-open-after-err`; `$XFS_IO_PROG -c "pwrite -q 0 $datalen" -c fsync $testfile`; `_dmerror_load_error_table`; `$XFS_IO_PROG -c "pwrite -q 0 $datalen" -c sync $testfile`; `_dmerror_load_working_table`; `echo "The following fsync should fail with EIO:"`; `$XFS_IO_PROG -c fsync $testfile |& \`; `_filter_flakey_EIO "fsync: Input/output error"`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. The dm-flakey helper deliberately drops writes and remounts to force replay of whatever reached the btrfs log tree. Device identity, missing-device state, degraded mounts, and balance/repair writes are part of the persistent test surface. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick eio raid` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

The pass/fail signal depends on realistic crash semantics from dm-flakey and on metadata journaling being available. Multi-device tests need enough disposable devices and can leave device scans cached if cleanup does not run. Fault-injection timing must hit the intended mirror or stripe; otherwise the bug path may not execute.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/160 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/161 -->
# sources/test-tools/xfstests/tests/btrfs/161

## Purpose

`sources/test-tools/xfstests/tests/btrfs/161` is btrfs fstests case `161`. It targets multi-device or RAID volume behavior. Source comments describe the scenario as: seed sprout functionality test Create a seed device, mount it and, add a new device to create a sprout filesystem.

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick volume seed` declares tags `auto quick volume seed`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_command "$BTRFS_TUNE_PROG" btrfstune`, `_require_scratch_dev_pool 2`; local shell helpers: `create_seed()`, `create_sprout()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_require_scratch_dev_pool 2`; `_scratch_dev_pool_get 2`; `dev_seed=$(echo $SCRATCH_DEV_POOL | $AWK_PROG '{print $1}')`; `dev_sprout=$(echo $SCRATCH_DEV_POOL | $AWK_PROG '{print $2}')`; `_mkfs_dev $dev_seed`; `run_check _mount $dev_seed $SCRATCH_MNT`; `$XFS_IO_PROG -f -d -c "pwrite -S 0xab 0 256K" $SCRATCH_MNT/foobar >\`; `od -x $SCRATCH_MNT/foobar`; `_btrfs filesystem show -m $SCRATCH_MNT`; `_scratch_unmount`; `_btrfs device add -f $dev_sprout $SCRATCH_MNT >> \`; `run_check _mount $dev_sprout $SCRATCH_MNT`; `_scratch_dev_pool_put`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Device identity, missing-device state, degraded mounts, and balance/repair writes are part of the persistent test surface. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick volume seed` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Multi-device tests need enough disposable devices and can leave device scans cached if cleanup does not run.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/161 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/162 -->
# sources/test-tools/xfstests/tests/btrfs/162

## Purpose

`sources/test-tools/xfstests/tests/btrfs/162` is btrfs fstests case `162`. It targets multi-device or RAID volume behavior. Source comments describe the scenario as: Nested seed device test Create a seed device Create a sprout device Make the sprout device a seed device and create a sprout device again

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick volume seed` declares tags `auto quick volume seed`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`. sourced helpers: `./common/preamble`, `./common/filter`, `./common/filter.btrfs`; requirements: `_require_command "$BTRFS_TUNE_PROG" btrfstune`, `_require_scratch_dev_pool 3`; local shell helpers: `create_seed()`, `create_sprout_seed()`, `create_next_sprout()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_require_scratch_dev_pool 3`; `_scratch_dev_pool_get 3`; `dev_seed=$(echo $SCRATCH_DEV_POOL | $AWK_PROG '{print $1}')`; `dev_sprout_seed=$(echo $SCRATCH_DEV_POOL | $AWK_PROG '{print $2}')`; `dev_sprout=$(echo $SCRATCH_DEV_POOL | $AWK_PROG '{print $3}')`; `_mkfs_dev $dev_seed`; `run_check _mount $dev_seed $SCRATCH_MNT`; `$XFS_IO_PROG -f -d -c "pwrite -S 0xab 0 256K" $SCRATCH_MNT/foobar >\`; `od -x $SCRATCH_MNT/foobar`; `_btrfs filesystem show -m $SCRATCH_MNT`; `_scratch_unmount`; `_btrfs device add -f $dev_sprout_seed $SCRATCH_MNT >>\`; `run_check _mount $dev_sprout_seed $SCRATCH_MNT`; `_btrfs device add -f $dev_sprout $SCRATCH_MNT >>\`; `run_check _mount $dev_sprout $SCRATCH_MNT`; `_scratch_dev_pool_put`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Device identity, missing-device state, degraded mounts, and balance/repair writes are part of the persistent test surface. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick volume seed` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Multi-device tests need enough disposable devices and can leave device scans cached if cleanup does not run.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/162 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/163 -->
# sources/test-tools/xfstests/tests/btrfs/163

## Purpose

`sources/test-tools/xfstests/tests/btrfs/163` is btrfs fstests case `163`. It targets multi-device or RAID volume behavior. Source comments describe the scenario as: Test case to verify that a sprouted device can be replaced Create a seed device Create a sprout device Remount RW Run device replace on the sprout device Depends on the kernel patch c6a5d954950c btrfs: fail replace of seed device

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick volume seed remount` declares tags `auto quick volume seed remount`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`. sourced helpers: `./common/preamble`, `./common/filter`, `./common/filter.btrfs`; requirements: `_require_command "$BTRFS_TUNE_PROG" btrfstune`, `_require_scratch_dev_pool 3`, `_require_btrfs_forget_or_module_loadable`; local shell helpers: `_cleanup()`, `create_seed()`, `add_sprout()`, `replace_sprout()`, `seed_is_mountable()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `rm -f $tmp.*`; `_btrfs_rescan_devices`; `_require_scratch_dev_pool 3`; `_require_btrfs_forget_or_module_loadable`; `_scratch_dev_pool_get 3`; `dev_replace_tgt=$(echo $SCRATCH_DEV_POOL | $AWK_PROG '{print $3}')`; `run_check _mount $dev_seed $SCRATCH_MNT`; `$XFS_IO_PROG -f -d -c "pwrite -S 0xab 0 4M" $SCRATCH_MNT/foobar >\`; `_btrfs device add -f $dev_sprout $SCRATCH_MNT >>\`; `_mount -o remount,rw $dev_sprout $SCRATCH_MNT`; `$XFS_IO_PROG -f -c "pwrite -S 0xcd 0 4M" $SCRATCH_MNT/foobar2 >\`; `od -x $SCRATCH_MNT/foobar2`; `seed_is_mountable()`; `replace_sprout`; `seed_is_mountable`; `_scratch_dev_pool_put`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Device identity, missing-device state, degraded mounts, and balance/repair writes are part of the persistent test surface. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick volume seed remount` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Multi-device tests need enough disposable devices and can leave device scans cached if cleanup does not run.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/163 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/164 -->
# sources/test-tools/xfstests/tests/btrfs/164

## Purpose

`sources/test-tools/xfstests/tests/btrfs/164` is btrfs fstests case `164`. It targets multi-device or RAID volume behavior. Source comments describe the scenario as: Test case to verify that a seed device can be deleted Create a seed device Create a sprout device Remount RW Run device delete on the seed device

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick volume remount` declares tags `auto quick volume remount`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`. sourced helpers: `./common/preamble`; requirements: `_require_btrfs_forget_or_module_loadable`, `_require_scratch_dev_pool 2`; local shell helpers: `_cleanup()`, `create_seed()`, `add_sprout()`, `delete_seed()`, `seed_is_mountable()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `rm -f $tmp.*`; `_btrfs_rescan_devices`; `_require_btrfs_forget_or_module_loadable`; `_require_scratch_dev_pool 2`; `_scratch_dev_pool_get 2`; `run_check _mount $dev_seed $SCRATCH_MNT`; `$XFS_IO_PROG -f -d -c "pwrite -S 0xab 0 256K" $SCRATCH_MNT/foobar >\`; `_btrfs device add -f $dev_sprout $SCRATCH_MNT >>\`; `run_check mount -o rw,remount $dev_seed $SCRATCH_MNT`; `_btrfs device delete $dev_seed $SCRATCH_MNT`; `_btrfs_forget_or_module_reload`; `run_check _mount $dev_sprout $SCRATCH_MNT`; `seed_is_mountable()`; `seed_is_mountable`; `_scratch_dev_pool_put`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Device identity, missing-device state, degraded mounts, and balance/repair writes are part of the persistent test surface. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick volume remount` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Multi-device tests need enough disposable devices and can leave device scans cached if cleanup does not run.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/164 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/165 -->
# sources/test-tools/xfstests/tests/btrfs/165

## Purpose

`sources/test-tools/xfstests/tests/btrfs/165` is btrfs fstests case `165`. It targets subvolume/snapshot metadata. Source comments describe the scenario as: QA test that checks rmdir(2) works for subvolumes like ordinary directories. This behavior has been restricted long time but becomes allowed by kernel commit a79a464d5675 ("btrfs: Allow rmdir(2) to delete an empty subvolume") Check that an empty subvolume can be deleted by rmdir Check that non-empty subvolume cannot be deleted by rmdir Check that read-only empty subvolume can be deleted by rmdir Check that the default subvolume cannot be deleted by rmdir Check that subvolume stub (created by snapshot) can be deleted by rmdir (Note: this has been always allowed) Check that rm -r works for both non-snapshot subvolume and snapshot

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick subvol` declares tags `auto quick subvol`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_scratch`, `_require_btrfs_fs_feature "rmdir_subvol"`; local shell helpers: `create_subvol()`, `create_snapshot()`, `rmdir_subvol()`, `rm_r_subvol()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `$BTRFS_UTIL_PROG subvolume create $1 >> $seqres.full 2>&1`; `create_snapshot()`; `$BTRFS_UTIL_PROG subvolume snapshot $@ >> $seqres.full 2>&1`; `rm -r $1 >> $seqres.full 2>&1`; `_require_scratch`; `_scratch_mount`; `echo "rmdir should delete an empty subvolume"`; `echo "rmdir should fail for non-empty subvolume"`; `create_snapshot -r $SCRATCH_MNT/sub3 $SCRATCH_MNT/snap`; `echo "rmdir should delete a readonly empty subvolume"`; `$BTRFS_UTIL_PROG subvolume set-default $subvolid $SCRATCH_MNT \`; `create_snapshot $SCRATCH_MNT/sub7 $SCRATCH_MNT/snap3`; `create_snapshot -r $SCRATCH_MNT/sub7 $SCRATCH_MNT/snap4`; `echo "rm -r should delete subvolumes recursively"`; `echo "rm -r should fail for non-empty readonly subvolume"`; `$BTRFS_UTIL_PROG property set $SCRATCH_MNT/snap4 ro false >> $seqres.full 2>&1`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Subvolume roots, read-only snapshots, deleted snapshot orphans, and directory entries are persisted across remounts. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick subvol` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

The main risk is environmental: missing fstests helpers, unsupported btrfs features, or changed userspace output can turn the test into a notrun or golden-output mismatch.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. Most success is absence of unexpected output, ending with `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/165 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/166 -->
# sources/test-tools/xfstests/tests/btrfs/166

## Purpose

`sources/test-tools/xfstests/tests/btrfs/166` is btrfs fstests case `166`. It targets quota-group accounting and limits. Source comments describe the scenario as: Test that if a power failure happens on a filesystem with quotas (qgroups) enabled while the quota rescan kernel thread is running, we will be able to mount the filesystem after the power failure. Enable qgroups on the filesystem. This will start the qgroup rescan kernel thread. Simulate a power failure, while the qgroup rescan kernel thread is running, and then mount the filesystem to check that mounting the filesystem does not fail.

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick qgroup` declares tags `auto quick qgroup`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`. sourced helpers: `./common/preamble`, `./common/filter`, `./common/dmflakey`; requirements: `_require_scratch`, `_require_dm_target flakey`, `_require_metadata_journaling $SCRATCH_DEV`; local shell helpers: `_cleanup()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_cleanup_flakey`; `rm -f $tmp.*`; `_require_scratch`; `_require_dm_target flakey`; `_scratch_mkfs  >>$seqres.full 2>&1`; `_init_flakey`; `_scratch_mount`; `_btrfs quota enable $SCRATCH_MNT`; `_flakey_drop_and_remount`; `_scratch_unmount`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. The dm-flakey helper deliberately drops writes and remounts to force replay of whatever reached the btrfs log tree. Quota-group counters, limits, inherited qgroups, and rescan results are kernel-maintained metadata validated at unmount/check time. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick qgroup` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

The pass/fail signal depends on realistic crash semantics from dm-flakey and on metadata journaling being available. Qgroup tests are sensitive to delayed accounting, rescan completion, and checker support for quota validation.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. Most success is absence of unexpected output, ending with `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/166 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/167 -->
# sources/test-tools/xfstests/tests/btrfs/167

## Purpose

`sources/test-tools/xfstests/tests/btrfs/167` is btrfs fstests case `167`. It targets multi-device or RAID volume behavior, compression interactions. Source comments describe the scenario as: Test if btrfs will corrupt compressed data extent without data csum by replacing it with uncompressed data, when doing device replace. This could be fixed by the following kernel commit: ac0b4145d662 ("btrfs: scrub: Don't use inode pages for device replace") Create nodatasum inode Write the compressed data back to disk Replace the device Unmount to drop all cache so next read will read from disk Now the EXTENT_DATA item still marks the extent as compressed, but the on-disk data is uncompressed, thus reading it as compressed

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick replace volume remount compress` declares tags `auto quick replace volume remount compress`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_scratch_dev_pool 2`, `_require_scratch_dev_pool_equal_size`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_require_scratch_dev_pool 2`; `_require_scratch_dev_pool_equal_size`; `_scratch_dev_pool_get 1`; `_scratch_pool_mkfs >> $seqres.full 2>&1`; `_scratch_mount "-o nodatasum"`; `touch $SCRATCH_MNT/nodatasum_file`; `_scratch_remount "datasum,compress"`; `_pwrite_byte 0xcd 0 128K $SCRATCH_MNT/nodatasum_file > /dev/null`; `sync`; `_btrfs replace start -Bf 1 $SPARE_DEV $SCRATCH_MNT`; `_scratch_unmount`; `_mount $SPARE_DEV $SCRATCH_MNT`; `_scratch_dev_pool_put`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Device identity, missing-device state, degraded mounts, and balance/repair writes are part of the persistent test surface. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick replace volume remount compress` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Multi-device tests need enough disposable devices and can leave device scans cached if cleanup does not run. Compression, inline-extent thresholds, and page or sector size can change the exact layout being exercised.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. Most success is absence of unexpected output, ending with `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/167 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/168 -->
# sources/test-tools/xfstests/tests/btrfs/168

## Purpose

`sources/test-tools/xfstests/tests/btrfs/168` is btrfs fstests case `168`. It targets send/receive stream correctness. Source comments describe the scenario as: Test that we are able to do send operations when one of the source snapshots (or subvolume) has a file that is deleted while there is still a open file descriptor for that file. Create a subvolume used for first full send test and used to create two snapshots for the incremental send test. Create some test files. Flush the previous buffered writes, since setting a subvolume to RO mode does not do it and we want to check if the data is correctly transmitted by the send operations. Keep an open file descriptor on file bar.

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick send` declares tags `auto quick send`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`; snapshot equivalence is checked with `$FSSUM_PROG`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_test`, `_require_scratch`, `_require_btrfs_command "property"`, `_require_fssum`; local shell helpers: `_cleanup()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `rm -f $tmp.*`; `rm -fr $send_files_dir`; `_require_scratch`; `_require_btrfs_command "property"`; `_require_fssum`; `send_files_dir=$TEST_DIR/btrfs-test-$seq`; `mkdir $send_files_dir`; `_scratch_mount`; `$BTRFS_UTIL_PROG subvolume create $SCRATCH_MNT/sv1 | _filter_scratch`; `$XFS_IO_PROG -f -c "pwrite -S 0xf1 0 64K" $SCRATCH_MNT/sv1/foo >>$seqres.full`; `$XFS_IO_PROG -f -c "pwrite -S 0x7b 0 90K" $SCRATCH_MNT/sv1/bar >>$seqres.full`; `$FSSUM_PROG -r $send_files_dir/sv1.fssum $SCRATCH_MNT/sv1`; `$BTRFS_UTIL_PROG receive -f $send_files_dir/snap1.send $SCRATCH_MNT`; `$FSSUM_PROG -r $send_files_dir/snap1.fssum $SCRATCH_MNT/snap1`; `$BTRFS_UTIL_PROG receive -f $send_files_dir/snap2.send $SCRATCH_MNT`; `$FSSUM_PROG -r $send_files_dir/snap2.fssum $SCRATCH_MNT/snap2`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Subvolume roots, read-only snapshots, deleted snapshot orphans, and directory entries are persisted across remounts. Send streams, fssum manifests, and received snapshots are temporary artifacts used to compare source and reconstructed filesystems. The script records user-visible checksums, listings, device counters, capabilities, or byte dumps as evidence. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick send` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Send tests can be fragile around inode-number ordering, rename dependencies, clone commands, xattrs, and receiver mount options.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. `fssum` manifests are written on source snapshots and verified after receive.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/168 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/169 -->
# sources/test-tools/xfstests/tests/btrfs/169

## Purpose

`sources/test-tools/xfstests/tests/btrfs/169` is btrfs fstests case `169`. It targets send/receive stream correctness. Source comments describe the scenario as: Test that an incremental send operation produces correct results if a file that has a prealloc (unwritten) extent beyond its EOF gets a hole punched in a section of that prealloc extent. Create our test file with a prealloc extent of 4Mb starting at offset 0, then write 1Mb of data into offset 0. Now punch a hole starting at an offset that corresponds to the file's current size (1Mb) and ends at an offset smaller then the end offset of the prealloc extent we allocated earlier (3Mb < 4Mb). Now recreate the filesystem by receiving both send streams and verify we get the same file content that the original filesystem had.

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick send prealloc punch` declares tags `auto quick send prealloc punch`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_test`, `_require_scratch`, `_require_xfs_io_command "fpunch"`, `_require_xfs_io_command "falloc" "-k"`; local shell helpers: `_cleanup()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `rm -f $tmp.*`; `rm -fr $send_files_dir`; `_require_scratch`; `_require_xfs_io_command "falloc" "-k"`; `send_files_dir=$TEST_DIR/btrfs-test-$seq`; `mkdir $send_files_dir`; `_scratch_mount`; `$XFS_IO_PROG -f -c "falloc -k 0 4M" \`; `-c "pwrite -S 0xea 0 1M" \`; `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/snap1`; `$BTRFS_UTIL_PROG send -f $send_files_dir/1.snap $SCRATCH_MNT/snap1 2>&1 \`; `$SCRATCH_MNT/snap2 2>&1 | _filter_scratch`; `md5sum $SCRATCH_MNT/snap2/foobar | _filter_scratch`; `_scratch_unmount`; `$BTRFS_UTIL_PROG receive -f $send_files_dir/1.snap $SCRATCH_MNT`; `$BTRFS_UTIL_PROG receive -f $send_files_dir/2.snap $SCRATCH_MNT`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Subvolume roots, read-only snapshots, deleted snapshot orphans, and directory entries are persisted across remounts. Send streams, fssum manifests, and received snapshots are temporary artifacts used to compare source and reconstructed filesystems. The script records user-visible checksums, listings, device counters, capabilities, or byte dumps as evidence. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick send prealloc punch` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Send tests can be fragile around inode-number ordering, rename dependencies, clone commands, xattrs, and receiver mount options.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. Before/after checksums must match across remount, balance, or receive.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/169 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/170 -->
# sources/test-tools/xfstests/tests/btrfs/170

## Purpose

`sources/test-tools/xfstests/tests/btrfs/170` is btrfs fstests case `170`. It targets subvolume/snapshot metadata. Source comments describe the scenario as: Test that if we write into an unwritten extent of a file when there is no more space left to allocate in the filesystem and then snapshot the file's subvolume, after a clean shutdown the data was not lost. Use a fixed size filesystem so that we can precisely fill the data block group mkfs.btrfs creates and allocate all unused space for a new data block group. It's important to not use the mixed block groups feature as well because we later want to not have more space available for allocating data extents but still have enough metadata space free for creating the snapshot. Mount without space cache so that we can precisely fill all data space and unallocated space later (space cache v1 uses data block groups).

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick snapshot prealloc` declares tags `auto quick snapshot prealloc`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_scratch`, `_require_xfs_io_command "falloc" "-k"`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_require_scratch`; `_require_xfs_io_command "falloc" "-k"`; `_scratch_mkfs_sized $fs_size >>$seqres.full 2>&1`; `_scratch_mount $(_btrfs_no_v1_cache_opt)`; `$XFS_IO_PROG -f -c "falloc -k 0 1914961920" $SCRATCH_MNT/foobar`; `$XFS_IO_PROG -c "pwrite -S 0xea -b 128K 0 128K" $SCRATCH_MNT/foobar | _filter_xfs_io`; `md5sum $SCRATCH_MNT/foobar | _filter_scratch`; `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/snap`; `_scratch_unmount`; `_scratch_mount`; `echo "File digest after mounting the filesystem again:"`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Subvolume roots, read-only snapshots, deleted snapshot orphans, and directory entries are persisted across remounts. The script records user-visible checksums, listings, device counters, capabilities, or byte dumps as evidence. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick snapshot prealloc` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

The main risk is environmental: missing fstests helpers, unsupported btrfs features, or changed userspace output can turn the test into a notrun or golden-output mismatch.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. Before/after checksums must match across remount, balance, or receive.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/170 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/171 -->
# sources/test-tools/xfstests/tests/btrfs/171

## Purpose

`sources/test-tools/xfstests/tests/btrfs/171` is btrfs fstests case `171`. It targets quota-group accounting and limits. Source comments describe the scenario as: Test if btrfs can clear high level childless qgroup's accounting numbers during rescan. Fixed by the following kernel patch: "btrfs: qgroup: Dirty all qgroups before rescan" Populate the fs Ensure that buffered file data is persisted, so we won't have an empty file in the snapshot. Create high level qgroup Above assignment will mark qgroup inconsistent due to the shared extents between subvol/snapshot/high level qgroup, do rescan here.

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick qgroup` declares tags `auto quick qgroup`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`. sourced helpers: `./common/preamble`, `./common/filter`, `./common/filter.btrfs`; requirements: `_require_scratch`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_require_scratch`; `_scratch_mkfs > /dev/null 2>&1`; `_scratch_mount`; `$BTRFS_UTIL_PROG subvolume create "$SCRATCH_MNT/subvol" > /dev/null`; `_pwrite_byte 0xcdcd 0 1M "$SCRATCH_MNT/subvol/file1" > /dev/null`; `sync`; `$BTRFS_UTIL_PROG subvolume snapshot "$SCRATCH_MNT/subvol" \`; `"$SCRATCH_MNT/snapshot" > /dev/null`; `$BTRFS_UTIL_PROG quota enable "$SCRATCH_MNT" > /dev/null`; `_qgroup_rescan $SCRATCH_MNT > /dev/null`; `$BTRFS_UTIL_PROG qgroup create 1/0 "$SCRATCH_MNT"`; `$BTRFS_UTIL_PROG qgroup assign "$SCRATCH_MNT/snapshot" 1/0 "$SCRATCH_MNT" \`; `2>&1 | _filter_btrfs_qgroup_assign_warnings`; `$BTRFS_UTIL_PROG qgroup remove "$SCRATCH_MNT/snapshot" 1/0 "$SCRATCH_MNT" \`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Subvolume roots, read-only snapshots, deleted snapshot orphans, and directory entries are persisted across remounts. Quota-group counters, limits, inherited qgroups, and rescan results are kernel-maintained metadata validated at unmount/check time. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick qgroup` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Qgroup tests are sensitive to delayed accounting, rescan completion, and checker support for quota validation.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. Most success is absence of unexpected output, ending with `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/171 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/172 -->
# sources/test-tools/xfstests/tests/btrfs/172

## Purpose

`sources/test-tools/xfstests/tests/btrfs/172` is btrfs fstests case `172`. It targets log-tree replay and fsync crash recovery. Source comments describe the scenario as: Validate that without no-holes we do not get an i_size that is after a gap in the file extents on disk.  This is fixed by the following patches btrfs: use the file extent tree infrastructure btrfs: replace all uses of btrfs_ordered_update_i_size block-group-tree requires no-holes There's not a straightforward way to commit the transaction without also flushing dirty pages, so shorten the commit interval to 1 so we're sure to get a commit with our broken file Now wait for a transaction commit to happen, wait 2x just to be super sure We only care about the fs consistency, so just run fsck, we don't have

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick log replay recoveryloop` declares tags `auto quick log replay recoveryloop`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`. sourced helpers: `./common/preamble`, `./common/filter`, `./common/dmlogwrites`; requirements: `_require_scratch`, `_require_log_writes`, `_require_xfs_io_command "sync_range"`, `_require_btrfs_no_block_group_tree`; local shell helpers: `_cleanup()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `rm -f $tmp.*`; `_require_scratch`; `_require_xfs_io_command "sync_range"`; `_require_btrfs_no_block_group_tree`; `_log_writes_mkfs "-O ^no-holes" >> $seqres.full 2>&1`; `_log_writes_mount -o commit=1`; `$XFS_IO_PROG -f -c "pwrite 0 5m" $SCRATCH_MNT/file | _filter_xfs_io`; `$XFS_IO_PROG -f -c "sync_range -abw 4m 1m" $SCRATCH_MNT/file | _filter_xfs_io`; `_log_writes_unmount`; `_check_scratch_fs`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick log replay recoveryloop` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

The main risk is environmental: missing fstests helpers, unsupported btrfs features, or changed userspace output can turn the test into a notrun or golden-output mismatch.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. fstests scratch checking validates filesystem and qgroup consistency after unmount.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/172 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/173 -->
# sources/test-tools/xfstests/tests/btrfs/173

## Purpose

`sources/test-tools/xfstests/tests/btrfs/173` is btrfs fstests case `173`. It targets compression interactions. Source comments describe the scenario as: Test swap file activation restrictions specific to Btrfs, swap file can't be CoW file nor compressed file. We can't use _format_swapfile because we don't want chattr +C, and we can't unset it after the swap file has been created. Make sure we have a COW file if we were mounted with "-o nodatacow".

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick swap compress` declares tags `auto quick swap compress`; environment gates are expressed through `_require*` helpers; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_scratch_swapfile`, `_require_chattr C`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_require_scratch_swapfile`; `_scratch_mkfs >> $seqres.full 2>&1`; `_scratch_mount`; `rm -f "$SCRATCH_MNT/swap"`; `touch "$SCRATCH_MNT/swap"`; `if _normalize_mount_options "$MOUNT_OPTIONS" | grep -q "nodatacow"; then`; `_require_chattr C`; `chmod 0600 "$SCRATCH_MNT/swap"`; `_pwrite_byte 0x61 0 $(($(_get_page_size) * 10)) "$SCRATCH_MNT/swap" >> $seqres.full`; `swapon "$SCRATCH_MNT/swap" 2>&1 | _filter_scratch`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick swap compress` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Compression, inline-extent thresholds, and page or sector size can change the exact layout being exercised.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/173 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/174 -->
# sources/test-tools/xfstests/tests/btrfs/174

## Purpose

`sources/test-tools/xfstests/tests/btrfs/174` is btrfs fstests case `174`. It targets compression interactions. Source comments describe the scenario as: Test restrictions on operations that can be done on an active swap file specific to Btrfs. Turning off nocow doesn't do anything because the file is not empty, not because the file is a swap file, but make sure this works anyways. Compression we reject outright. We pass the -c (compress) flag to force defrag even if the file isn't fragmented.

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick swap compress` declares tags `auto quick swap compress`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_scratch_swapfile`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_require_scratch_swapfile`; `_scratch_mkfs >> $seqres.full 2>&1`; `_scratch_mount`; `$BTRFS_UTIL_PROG subvolume create "$SCRATCH_MNT/swapvol" >> $seqres.full`; `swapfile="$SCRATCH_MNT/swapvol/swap"`; `$LSATTR_PROG -l "$swapfile" | _filter_scratch | _filter_spaces`; `$BTRFS_UTIL_PROG subvolume snapshot "$SCRATCH_MNT/swapvol" \`; `$BTRFS_UTIL_PROG filesystem defrag -c "$swapfile" 2>&1 | grep -o "Text file busy"`; `_scratch_unmount`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Subvolume roots, read-only snapshots, deleted snapshot orphans, and directory entries are persisted across remounts. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick swap compress` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Compression, inline-extent thresholds, and page or sector size can change the exact layout being exercised.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/174 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/175 -->
# sources/test-tools/xfstests/tests/btrfs/175

## Purpose

`sources/test-tools/xfstests/tests/btrfs/175` is btrfs fstests case `175`. It targets multi-device or RAID volume behavior. Source comments describe the scenario as: Test swap file activation on multiple devices. Each device is only 1 GB, so 1.5 GB must be split across multiple devices. Create the swap file, then add the device. That way we know it's all on one device.

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick swap volume raid` declares tags `auto quick swap volume raid`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_scratch_dev_pool 2`, `_require_scratch_swapfile`; local shell helpers: `cycle_swapfile()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_require_scratch_dev_pool 2`; `_require_scratch_swapfile`; `_check_minimal_fs_size $((1024 * 1024 * 1024))`; `swapon "$SCRATCH_MNT/swap" 2>&1 | _filter_scratch`; `_scratch_pool_mkfs -d raid1 -m raid1 >> $seqres.full 2>&1`; `_scratch_mount`; `_scratch_unmount`; `_scratch_pool_mkfs -d dup -m dup >> $seqres.full 2>&1`; `echo "Single on multiple devices"`; `_scratch_pool_mkfs -d single -m raid1 -b $((1024 * 1024 * 1024)) >> $seqres.full 2>&1`; `echo "Single on one device"`; `_scratch_mkfs >> $seqres.full 2>&1`; `scratch_dev2="$(echo "${SCRATCH_DEV_POOL}" | $AWK_PROG '{ print $2 }')"`; `$BTRFS_UTIL_PROG device add -f "$scratch_dev2" "$SCRATCH_MNT" >> $seqres.full`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Device identity, missing-device state, degraded mounts, and balance/repair writes are part of the persistent test surface. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick swap volume raid` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Multi-device tests need enough disposable devices and can leave device scans cached if cleanup does not run.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/175 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/176 -->
# sources/test-tools/xfstests/tests/btrfs/176

## Purpose

`sources/test-tools/xfstests/tests/btrfs/176` is btrfs fstests case `176`. It targets multi-device or RAID volume behavior. Source comments describe the scenario as: Test device remove/replace with an active swap file. We check the filesystem manually because we move devices around. We know the swap file is on device 1 because we added device 2 after it was already created. Deleting/readding device 2 should still work. Deleting device 1 should work again after swapoff. Again, we know the swap file is on device 1. Replacing device 2 should still work. Replacing device 1 should work again after swapoff.

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick swap volume` declares tags `auto quick swap volume`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_scratch_dev_pool 3`, `_require_scratch_swapfile`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_require_scratch_dev_pool 3`; `_require_scratch_swapfile`; `rm -f "${RESULT_DIR}/require_scratch"`; `scratch_dev1="$(echo "${SCRATCH_DEV_POOL}" | $AWK_PROG '{ print $1 }')"`; `scratch_dev2="$(echo "${SCRATCH_DEV_POOL}" | $AWK_PROG '{ print $2 }')"`; `echo "Remove device"`; `_scratch_mount`; `$BTRFS_UTIL_PROG device add -f "$scratch_dev2" "$SCRATCH_MNT" >> $seqres.full`; `$BTRFS_UTIL_PROG device delete "$scratch_dev1" "$SCRATCH_MNT" 2>&1 | grep -o "Text file busy"`; `$BTRFS_UTIL_PROG device delete "$scratch_dev2" "$SCRATCH_MNT"`; `$BTRFS_UTIL_PROG device delete "$scratch_dev1" "$SCRATCH_MNT"`; `_check_dev_fs "$scratch_dev2"`; `echo "Replace device"`; `$BTRFS_UTIL_PROG replace start -fB "$scratch_dev1" "$scratch_dev3" "$SCRATCH_MNT" 2>&1 | grep -o "Text file busy"`; `$BTRFS_UTIL_PROG replace start -fB "$scratch_dev2" "$scratch_dev3" "$SCRATCH_MNT" \`; `$BTRFS_UTIL_PROG replace start -fB "$scratch_dev1" "$scratch_dev2" "$SCRATCH_MNT" \`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Device identity, missing-device state, degraded mounts, and balance/repair writes are part of the persistent test surface. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick swap volume` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Multi-device tests need enough disposable devices and can leave device scans cached if cleanup does not run.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/176 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/177 -->
# sources/test-tools/xfstests/tests/btrfs/177

## Purpose

`sources/test-tools/xfstests/tests/btrfs/177` is btrfs fstests case `177`. It targets balance relocation behavior. Source comments describe the scenario as: Test relocation (balance and resize) with an active swap file. Eliminate the differences between the old and new output formats Old format: Resize 'SCRATCH_MNT' of '1073741824' New format: Resize device id 1 (SCRATCH_DEV) from 3.00GiB to 1.00GiB Convert both outputs to: Resized to 1073741824 remove trailing zeroes get the first unit char, for example return G in case we have GiB

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick swap balance` declares tags `auto quick swap balance`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_scratch_swapfile`, `_require_scratch_size $((3 * 1024 * 1024)) #kB`; local shell helpers: `convert_resize_output()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_require_scratch_swapfile`; `convert_resize_output()`; `swapfile="$SCRATCH_MNT/swap"`; `_require_scratch_size $((3 * 1024 * 1024)) #kB`; `_scratch_mkfs_sized $fssize >> $seqres.full 2>&1`; `_scratch_mount`; `dd if=/dev/zero of="$SCRATCH_MNT/fill" bs=4096 count=1 >> $seqres.full 2>&1`; `_run_btrfs_balance_start "$SCRATCH_MNT" >>$seqres.full`; `dd if=/dev/zero of="$SCRATCH_MNT/refill" bs=4096 >> $seqres.full 2>&1`; `$BTRFS_UTIL_PROG filesystem resize $((3 * fssize)) "$SCRATCH_MNT" | convert_resize_output`; `rm -f "$SCRATCH_MNT/fill"`; `rm -f "$SCRATCH_MNT/refill"`; `$BTRFS_UTIL_PROG filesystem resize 1G "$SCRATCH_MNT" 2>&1 | grep -o "Text file busy"`; `$BTRFS_UTIL_PROG filesystem resize $fssize "$SCRATCH_MNT" | convert_resize_output`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick swap balance` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

The main risk is environmental: missing fstests helpers, unsupported btrfs features, or changed userspace output can turn the test into a notrun or golden-output mismatch.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/177 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/178 -->
# sources/test-tools/xfstests/tests/btrfs/178

## Purpose

`sources/test-tools/xfstests/tests/btrfs/178` is btrfs fstests case `178`. It targets send/receive stream correctness. Source comments describe the scenario as: Test an incremental send operation in a scenario where the relationship of ancestor-descendant between multiple directories is inversed, and where multiple directories that were previously ancestors of another directory now become descendents of multiple directories that used to be their ancestors in the parent snapshot. This used to trigger an infinite loop in the kernel code. The name of each directory corresponds to its inode number, to make it easier to debug since btrfs' send processes inodes in ascending order according to their number. Filesystem looks like: .

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick send` declares tags `auto quick send`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; snapshot equivalence is checked with `$FSSUM_PROG`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_test`, `_require_scratch`, `_require_fssum`; local shell helpers: `_cleanup()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `rm -fr $send_files_dir`; `rm -f $tmp.*`; `_require_scratch`; `_require_fssum`; `send_files_dir=$TEST_DIR/btrfs-test-$seq`; `mkdir $send_files_dir`; `_scratch_mount`; `$BTRFS_UTIL_PROG subvolume snapshot -r $SCRATCH_MNT \`; `$BTRFS_UTIL_PROG send -f $send_files_dir/1.snap \`; `$BTRFS_UTIL_PROG send -p $SCRATCH_MNT/mysnap1 -f $send_files_dir/2.snap \`; `$FSSUM_PROG -A -f -w $send_files_dir/1.fssum $SCRATCH_MNT/mysnap1`; `_scratch_unmount`; `$BTRFS_UTIL_PROG receive -f $send_files_dir/1.snap $SCRATCH_MNT > /dev/null`; `$BTRFS_UTIL_PROG receive -f $send_files_dir/2.snap $SCRATCH_MNT > /dev/null`; `$FSSUM_PROG -r $send_files_dir/1.fssum $SCRATCH_MNT/mysnap1`; `$FSSUM_PROG -r $send_files_dir/2.fssum $SCRATCH_MNT/mysnap2`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Subvolume roots, read-only snapshots, deleted snapshot orphans, and directory entries are persisted across remounts. Send streams, fssum manifests, and received snapshots are temporary artifacts used to compare source and reconstructed filesystems. The script records user-visible checksums, listings, device counters, capabilities, or byte dumps as evidence. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick send` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Send tests can be fragile around inode-number ordering, rename dependencies, clone commands, xattrs, and receiver mount options.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. `fssum` manifests are written on source snapshots and verified after receive.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/178 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/179 -->
# sources/test-tools/xfstests/tests/btrfs/179

## Purpose

`sources/test-tools/xfstests/tests/btrfs/179` is btrfs fstests case `179`. It targets quota-group accounting and limits, fault-injection or destructive-device conditions. Source comments describe the scenario as: Test if btrfs will lockup at subvolume deletion when qgroups are enabled. This bug is going to be fixed by a patch for the kernel titled "btrfs: qgroup: Don't trigger backref walk at delayed ref insert time". default sleep interval stress test runtime Randomly remove some files for every 5 loop No snapshots available, sleep and retry later. By the async nature of qgroup tree scan and subvolume delete, the latest qgroup counts at the time of umount might not be upto date, if it isn't then the check will report the difference in count. The difference in

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto qgroup dangerous` declares tags `auto qgroup dangerous`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_scratch`; local shell helpers: `fill_workload()`, `snapshot_workload()`, `delete_workload()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_require_scratch`; `_scratch_mkfs > /dev/null 2>&1`; `_scratch_mount`; `mkdir -p "$SCRATCH_MNT/snapshots"`; `$BTRFS_UTIL_PROG subvolume create "$SCRATCH_MNT/src" > /dev/null`; `$BTRFS_UTIL_PROG quota enable "$SCRATCH_MNT" > /dev/null`; `_qgroup_rescan "$SCRATCH_MNT" > /dev/null`; `_pwrite_byte 0xcd 0 8K "$SCRATCH_MNT/src/large_$i" > /dev/null`; `_pwrite_byte 0xcd 0 2K "$SCRATCH_MNT/src/inline_$i" > /dev/null`; `snapshot_workload()`; `$BTRFS_UTIL_PROG subvolume snapshot "$SCRATCH_MNT/src" \`; `snapshot_workload &`; `snapshot_pid=$!`; `kill $snapshot_pid`; `wait $snapshot_pid`; `$BTRFS_UTIL_PROG subvolume sync $SCRATCH_MNT >> $seqres.full`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Subvolume roots, read-only snapshots, deleted snapshot orphans, and directory entries are persisted across remounts. Quota-group counters, limits, inherited qgroups, and rescan results are kernel-maintained metadata validated at unmount/check time. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto qgroup dangerous` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

It may be slow or disruptive because it reformats scratch storage and may use fault injection or degraded-device mounts. Qgroup tests are sensitive to delayed accounting, rescan completion, and checker support for quota validation.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. Most success is absence of unexpected output, ending with `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/179 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/180 -->
# sources/test-tools/xfstests/tests/btrfs/180

## Purpose

`sources/test-tools/xfstests/tests/btrfs/180` is btrfs fstests case `180`. It targets quota-group accounting and limits. Source comments describe the scenario as: Test if btrfs hits EDQUOT without reclaiming already freed extents when quota is enabled. This bug is going to be fxied by a patch for kernel titled "btrfs: qgroup: Make qgroup async transaction commit more aggressive" Commit transaction to reflect the quota usage Without the kernel fix, this will trigger EDQUOT.

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick qgroup limit prealloc` declares tags `auto quick qgroup limit prealloc`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_scratch`, `_require_xfs_io_command falloc`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_require_scratch`; `_require_xfs_io_command falloc`; `_scratch_mkfs > /dev/null`; `_scratch_mount`; `$BTRFS_UTIL_PROG quota enable "$SCRATCH_MNT" > /dev/null`; `_qgroup_rescan "$SCRATCH_MNT" > /dev/null`; `$BTRFS_UTIL_PROG qgroup limit -e 1G "$SCRATCH_MNT"`; `$XFS_IO_PROG -f -c "falloc 0 900M" "$SCRATCH_MNT/padding"`; `sync`; `rm -f "$SCRATCH_MNT/padding"`; `_pwrite_byte 0xcd 0 512M "$SCRATCH_MNT/real_file" | _filter_xfs_io`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Quota-group counters, limits, inherited qgroups, and rescan results are kernel-maintained metadata validated at unmount/check time. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick qgroup limit prealloc` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Qgroup tests are sensitive to delayed accounting, rescan completion, and checker support for quota validation.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/180 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/181 -->
# sources/test-tools/xfstests/tests/btrfs/181

## Purpose

`sources/test-tools/xfstests/tests/btrfs/181` is btrfs fstests case `181`. It targets balance relocation behavior. Source comments describe the scenario as: Test if btrfs will commit too many transactions for nothing and cause performance regression during balance. This bug is going to be fixed by a patch for kernel title "btrfs: don't end the transaction for delayed refs in throttle" Create some small files to take up enough metadata reserved space Commit the fs so we can get a stable super generation Since the fs is pretty small, we should have only 1 small metadata chunk and one tiny system chunk. Relocating such small chunks only needs 6 commits for each, thus 12 commits for 2 chunks.

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick balance` declares tags `auto quick balance`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_scratch`, `_require_btrfs_command inspect-internal dump-super`; local shell helpers: `get_super_gen()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_require_scratch`; `_require_btrfs_command inspect-internal dump-super`; `_scratch_mkfs > /dev/null`; `_scratch_mount`; `local ret=$($BTRFS_UTIL_PROG inspect dump-super "$SCRATCH_DEV" |\`; `$BTRFS_UTIL_PROG subvolume create "$SCRATCH_MNT/subvol" > /dev/null`; `_pwrite_byte 0xcd 0 1K "$SCRATCH_MNT/subvol/file_$i" > /dev/null`; `sync`; `_run_btrfs_balance_start -m $SCRATCH_MNT >> $seqres.full`; `echo "balance committed too many transactions"`; `echo "super generation before balance: ${before_gen}"`; `echo "super generation after balance:  ${after_gen}"`; `echo "super generation before balance: ${before_gen}" >> $seqres.full`; `echo "super generation after balance:  ${after_gen}" >> $seqres.full`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Subvolume roots, read-only snapshots, deleted snapshot orphans, and directory entries are persisted across remounts. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick balance` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

The main risk is environmental: missing fstests helpers, unsupported btrfs features, or changed userspace output can turn the test into a notrun or golden-output mismatch.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. Most success is absence of unexpected output, ending with `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/181 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/182 -->
# sources/test-tools/xfstests/tests/btrfs/182

## Purpose

`sources/test-tools/xfstests/tests/btrfs/182` is btrfs fstests case `182`. It targets balance relocation behavior. Source comments describe the scenario as: Test if balance will report false ENOSPC error This is a long existing bug, caused by over-estimated metadata space_info::bytes_may_use. There is one proposed patch for btrfs-progs to fix it, titled: "btrfs-progs: balance: Sync the fs before balancing metadata chunks" Create some small files to take up enough metadata reserved space

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick balance` declares tags `auto quick balance`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_scratch`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_require_scratch`; `_scratch_mkfs > /dev/null`; `_scratch_mount`; `$BTRFS_UTIL_PROG subvolume create "$SCRATCH_MNT/subvol" > /dev/null`; `_pwrite_byte 0xcd 0 1K "$SCRATCH_MNT/subvol/file_$i" > /dev/null`; `_run_btrfs_balance_start -m $SCRATCH_MNT >> $seqres.full`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Subvolume roots, read-only snapshots, deleted snapshot orphans, and directory entries are persisted across remounts. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick balance` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

The main risk is environmental: missing fstests helpers, unsupported btrfs features, or changed userspace output can turn the test into a notrun or golden-output mismatch.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. Most success is absence of unexpected output, ending with `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/182 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/183 -->
# sources/test-tools/xfstests/tests/btrfs/183

## Purpose

`sources/test-tools/xfstests/tests/btrfs/183` is btrfs fstests case `183`. It targets compression interactions. Source comments describe the scenario as: Regression test for read corruption of compressed and shared extents after punching holes into a file. Create a file with 3 consecutive compressed extents, each corresponds to 128Kb of data (uncompressed size) and each is stored on disk as a 4Kb extent (compressed size, regardless of compression algorithm used). Each extent starts with 4Kb of zeroes, while the remaining bytes all have a value of 0xff. Clone the first extent into offsets 128K and 256K. Punch holes into the regions that are already full of zeroes.

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick clone compress punch` declares tags `auto quick clone compress punch`; environment gates are expressed through `_require*` helpers; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`. sourced helpers: `./common/preamble`, `./common/filter`, `./common/reflink`; requirements: `_require_scratch_reflink`, `_require_xfs_io_command "fpunch"`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_require_scratch_reflink`; `_scratch_mkfs >>$seqres.full 2>&1`; `_scratch_mount "-o compress"`; `$XFS_IO_PROG -f -c "pwrite -S 0xff 0 384K" \`; `-c "pwrite -S 0x00 0 4K" \`; `-c "pwrite -S 0x00 128K 4K" \`; `-c "pwrite -S 0x00 256K 4K" \`; `md5sum $SCRATCH_MNT/foobar | _filter_scratch`; `$XFS_IO_PROG -c "reflink $SCRATCH_MNT/foobar 0 128K 128K" \`; `-c "reflink $SCRATCH_MNT/foobar 0 256K 128K" \`; `echo "File digest after reflinking:"`; `$XFS_IO_PROG -c "fpunch 0 4K" \`; `echo 1 > /proc/sys/vm/drop_caches`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. The script records user-visible checksums, listings, device counters, capabilities, or byte dumps as evidence. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick clone compress punch` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Compression, inline-extent thresholds, and page or sector size can change the exact layout being exercised.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. Before/after checksums must match across remount, balance, or receive.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/183 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/184 -->
# sources/test-tools/xfstests/tests/btrfs/184

## Purpose

`sources/test-tools/xfstests/tests/btrfs/184` is btrfs fstests case `184`. It targets multi-device or RAID volume behavior. Source comments describe the scenario as: Verify that when a device is removed from a multi-device filesystem its superblock copies are correctly deleted Explicitly use raid0 mode to ensure at least one of the devices can be removed. pick last dev in the list

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick volume raid` declares tags `auto quick volume raid`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_scratch`, `_require_scratch_dev_pool 2`, `_require_btrfs_command inspect-internal dump-super`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_require_scratch`; `_require_scratch_dev_pool 2`; `_require_btrfs_command inspect-internal dump-super`; `_scratch_dev_pool_get 2`; `_scratch_pool_mkfs "-d raid0 -m raid0" >> $seqres.full 2>&1 || _fail "mkfs failed"`; `_scratch_mount`; `dev_del=\`echo ${SCRATCH_DEV_POOL} | $AWK_PROG '{print $NF}'\``; `$BTRFS_UTIL_PROG device delete $dev_del $SCRATCH_MNT || _fail "btrfs device delete failed"`; `output=$($BTRFS_UTIL_PROG inspect-internal dump-super -s $i $dev_del 2>&1)`; `$BTRFS_UTIL_PROG inspect-internal dump-super -s $i $dev_del 2>&1 | grep -q "bad magic"`; `_scratch_unmount`; `_scratch_dev_pool_put`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Device identity, missing-device state, degraded mounts, and balance/repair writes are part of the persistent test surface. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick volume raid` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Multi-device tests need enough disposable devices and can leave device scans cached if cleanup does not run.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. Most success is absence of unexpected output, ending with `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/184 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/185 -->
# sources/test-tools/xfstests/tests/btrfs/185

## Purpose

`sources/test-tools/xfstests/tests/btrfs/185` is btrfs fstests case `185`. It targets multi-device or RAID volume behavior. Source comments describe the scenario as: Fuzzy test for FS image duplication. Could be fixed by a9261d4125c9 ("btrfs: harden agaist duplicate fsid on scanned devices") Original device is mounted, scan of its clone must not alter the filesystem device path Original device scan should be successful

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest volume auto quick` declares tags `volume auto quick`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_scratch_dev_pool 2`; local shell helpers: `_cleanup()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `$UMOUNT_PROG $mnt > /dev/null 2>&1`; `rm -rf $mnt > /dev/null 2>&1`; `rm -f $tmp.*`; `_require_scratch_dev_pool 2`; `_scratch_dev_pool_get 2`; `"btrfs: harden agaist duplicate fsid on scanned devices"`; `device_1=$(echo $SCRATCH_DEV_POOL | $AWK_PROG '{print $1}')`; `device_2=$(echo $SCRATCH_DEV_POOL | $AWK_PROG '{print $2}')`; `echo device_1=$device_1 device_2=$device_2 >> $seqres.full`; `_mkfs_dev $device_1`; `_mount $device_1 $mnt`; `skip=$sb_bytenr count=4096 > /dev/null 2>&1`; `$BTRFS_UTIL_PROG device scan $device_2 >> $seqres.full 2>&1`; `$BTRFS_UTIL_PROG device scan $device_1 >> $seqres.full 2>&1`; `_fail "if it fails here, then it means subvolume mount at boot may fail "\`; `_scratch_dev_pool_put`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Subvolume roots, read-only snapshots, deleted snapshot orphans, and directory entries are persisted across remounts. Device identity, missing-device state, degraded mounts, and balance/repair writes are part of the persistent test surface. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `volume auto quick` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Multi-device tests need enough disposable devices and can leave device scans cached if cleanup does not run.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. Most success is absence of unexpected output, ending with `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/185 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/186 -->
# sources/test-tools/xfstests/tests/btrfs/186

## Purpose

`sources/test-tools/xfstests/tests/btrfs/186` is btrfs fstests case `186`. It targets send/receive stream correctness, multi-device or RAID volume behavior. Source comments describe the scenario as: Test that if we have a subvolume/snapshot that is writable, has a file with unflushed delalloc (buffered writes not yet flushed), turn the subvolume to readonly mode and then use it for send a operation, the send stream will contain the delalloc data - that is, no data loss happens. Create our test subvolume. Create our test file with some delalloc data. Turn our subvolume to RO so that it can be used for a send operation. Create the send stream. Recreate the filesystem and apply the send stream and verify no data was lost.

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick send volume` declares tags `auto quick send volume`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_test`, `_require_scratch`, `_require_btrfs_command "property"`; local shell helpers: `_cleanup()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `rm -f $tmp.*`; `rm -fr $send_files_dir`; `_require_scratch`; `_require_btrfs_command "property"`; `send_files_dir=$TEST_DIR/btrfs-test-$seq`; `mkdir $send_files_dir`; `_scratch_mkfs >>$seqres.full 2>&1`; `_scratch_mount`; `$BTRFS_UTIL_PROG subvolume create $SCRATCH_MNT/sv | _filter_scratch`; `$XFS_IO_PROG -f -c "pwrite -S 0xea 0 108K" $SCRATCH_MNT/sv/foo | _filter_xfs_io`; `$BTRFS_UTIL_PROG property set $SCRATCH_MNT/sv ro true`; `$BTRFS_UTIL_PROG send -f $send_files_dir/sv.send $SCRATCH_MNT/sv 2>&1 \`; `| _filter_scratch`; `od -t x1 -A d $SCRATCH_MNT/sv/foo`; `_scratch_unmount`; `$BTRFS_UTIL_PROG receive -f $send_files_dir/sv.send $SCRATCH_MNT`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Subvolume roots, read-only snapshots, deleted snapshot orphans, and directory entries are persisted across remounts. Send streams, fssum manifests, and received snapshots are temporary artifacts used to compare source and reconstructed filesystems. The script records user-visible checksums, listings, device counters, capabilities, or byte dumps as evidence. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick send volume` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Send tests can be fragile around inode-number ordering, rename dependencies, clone commands, xattrs, and receiver mount options. Multi-device tests need enough disposable devices and can leave device scans cached if cleanup does not run.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/186 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/187 -->
# sources/test-tools/xfstests/tests/btrfs/187

## Purpose

`sources/test-tools/xfstests/tests/btrfs/187` is btrfs fstests case `187`. It targets send/receive stream correctness, balance relocation behavior. Source comments describe the scenario as: Stress send running in parallel with balance and deduplication against files that belong to the snapshots used by send. The goal is to verify that these operations running in parallel do not lead to send crashing (trigger assertion failures and BUG_ONs), or send finding an inconsistent snapshot that leads to a failure (reported in dmesg/syslog). The test needs big trees (snapshots) with large differences between the parent and send snapshots in order to hit such issues with a good probability. We at least need 8GB of free space on $SCRATCH_DEV Ignore errors from dedupe. We just want to test for crashes and deadlocks.

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto send dedupe clone balance` declares tags `auto send dedupe clone balance`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`. sourced helpers: `./common/preamble`, `./common/attr`, `./common/filter`, `./common/reflink`; requirements: `_require_scratch_dedupe`, `_require_attrs`, `_require_scratch_size $((8 * 1024 * 1024))`; local shell helpers: `dedupe_two_files()`, `dedupe_files_loop()`, `balance_loop()`, `full_send_loop()`, `inc_send_loop()`, `write_files_loop()`, `set_xattrs_loop()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_require_scratch_dedupe`; `_require_attrs`; `_require_scratch_size $((8 * 1024 * 1024))`; `_scratch_mkfs >>$seqres.full 2>&1`; `_scratch_mount`; `dedupe_files_loop()`; `balance_loop()`; `_run_btrfs_balance_start -f -m $SCRATCH_MNT &> /dev/null`; `full_send_loop()`; `$BTRFS_UTIL_PROG send -f /dev/null \`; `inc_send_loop()`; `wait $full_send_pid`; `wait $inc_send_pid`; `kill $balance_pid`; `wait $balance_pid`; `_dmesg_since_test_start | grep -E -e '\bBTRFS error \(device .*?\):'`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Subvolume roots, read-only snapshots, deleted snapshot orphans, and directory entries are persisted across remounts. Send streams, fssum manifests, and received snapshots are temporary artifacts used to compare source and reconstructed filesystems. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto send dedupe clone balance` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

It may be slow or disruptive because it reformats scratch storage and may use fault injection or degraded-device mounts. Send tests can be fragile around inode-number ordering, rename dependencies, clone commands, xattrs, and receiver mount options.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/187 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/188 -->
# sources/test-tools/xfstests/tests/btrfs/188

## Purpose

`sources/test-tools/xfstests/tests/btrfs/188` is btrfs fstests case `188`. It targets send/receive stream correctness. Source comments describe the scenario as: Test that an incremental send with not corrupt data when the source filesystem has the no-holes feature enabled, a file has prealloc (unwritten) extents that start after its size and hole is punched (after the first snapshot is made) that removes all extents from some offset up to the file's size. Create our test file with a prealloc extent that starts beyond its size. Now punch a hole that drops all the extents within the file's size. Now recreate the filesystem by receiving both send streams and verify we get the same file content that the original filesystem had.

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick send prealloc punch` declares tags `auto quick send prealloc punch`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_test`, `_require_scratch`, `_require_btrfs_fs_feature "no_holes"`, `_require_btrfs_mkfs_feature "no-holes"`, `_require_xfs_io_command "fpunch"`, `_require_xfs_io_command "falloc" "-k"`; local shell helpers: `_cleanup()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `rm -f $tmp.*`; `rm -fr $send_files_dir`; `_require_scratch`; `_require_btrfs_fs_feature "no_holes"`; `_require_btrfs_mkfs_feature "no-holes"`; `_require_xfs_io_command "falloc" "-k"`; `send_files_dir=$TEST_DIR/btrfs-test-$seq`; `mkdir $send_files_dir`; `_scratch_mount`; `$XFS_IO_PROG -f -c "pwrite -S 0xab 0 500K" $SCRATCH_MNT/foobar | _filter_xfs_io`; `$XFS_IO_PROG -c "falloc -k 1200K 800K" $SCRATCH_MNT/foobar`; `md5sum $SCRATCH_MNT/incr/foobar | _filter_scratch`; `_scratch_unmount`; `_scratch_mkfs >>$seqres.full 2>&1`; `$BTRFS_UTIL_PROG receive -f $send_files_dir/1.snap $SCRATCH_MNT`; `$BTRFS_UTIL_PROG receive -f $send_files_dir/2.snap $SCRATCH_MNT`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Subvolume roots, read-only snapshots, deleted snapshot orphans, and directory entries are persisted across remounts. Send streams, fssum manifests, and received snapshots are temporary artifacts used to compare source and reconstructed filesystems. The script records user-visible checksums, listings, device counters, capabilities, or byte dumps as evidence. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick send prealloc punch` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Send tests can be fragile around inode-number ordering, rename dependencies, clone commands, xattrs, and receiver mount options.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. Before/after checksums must match across remount, balance, or receive.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/188 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/189 -->
# sources/test-tools/xfstests/tests/btrfs/189

## Purpose

`sources/test-tools/xfstests/tests/btrfs/189` is btrfs fstests case `189`. It targets send/receive stream correctness. Source comments describe the scenario as: Test that an incremental send receive does not issue clone operations that attempt to clone the last block of a file, with a size not aligned to the filesystem's sector size, into the middle of some other file. Such clone request causes the receiver to fail (with EINVAL), for kernels that include commit ac765f83f1397646 ("Btrfs: fix data corruption due to cloning of eof block"), or cause silent data corruption for older kernels. Clone part of the extent from a higher offset to a lower offset of the same file. Now clone from the previous file, same range, into the middle of another file, such that the end offset at the destination is smaller than the destination's

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick send clone` declares tags `auto quick send clone`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`; snapshot equivalence is checked with `$FSSUM_PROG`. sourced helpers: `./common/preamble`, `./common/filter`, `./common/reflink`; requirements: `_require_fssum`, `_require_test`, `_require_scratch_reflink`; local shell helpers: `_cleanup()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `rm -f $tmp.*`; `rm -fr $send_files_dir`; `_require_fssum`; `_require_scratch_reflink`; `send_files_dir=$TEST_DIR/btrfs-test-$seq`; `mkdir $send_files_dir`; `_scratch_mount`; `$XFS_IO_PROG -f -c "pwrite -S 0xb1 0 2M" $SCRATCH_MNT/foo | _filter_xfs_io`; `$XFS_IO_PROG -f -c "pwrite -S 0xc7 0 2M" $SCRATCH_MNT/bar | _filter_xfs_io`; `$XFS_IO_PROG -f -c "pwrite -S 0x4d 0 2M" $SCRATCH_MNT/baz | _filter_xfs_io`; `$XFS_IO_PROG -f -c "pwrite -S 0xe2 0 2M" $SCRATCH_MNT/zoo | _filter_xfs_io`; `_scratch_unmount`; `$BTRFS_UTIL_PROG receive -f $send_files_dir/1.snap $SCRATCH_MNT`; `$BTRFS_UTIL_PROG receive -f $send_files_dir/2.snap $SCRATCH_MNT`; `$FSSUM_PROG -r $send_files_dir/base.fssum $SCRATCH_MNT/base`; `$FSSUM_PROG -r $send_files_dir/incr.fssum $SCRATCH_MNT/incr`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Subvolume roots, read-only snapshots, deleted snapshot orphans, and directory entries are persisted across remounts. Send streams, fssum manifests, and received snapshots are temporary artifacts used to compare source and reconstructed filesystems. The script records user-visible checksums, listings, device counters, capabilities, or byte dumps as evidence. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick send clone` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Send tests can be fragile around inode-number ordering, rename dependencies, clone commands, xattrs, and receiver mount options.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. `fssum` manifests are written on source snapshots and verified after receive.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/189 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/190 -->
# sources/test-tools/xfstests/tests/btrfs/190

## Purpose

`sources/test-tools/xfstests/tests/btrfs/190` is btrfs fstests case `190`. It targets quota-group accounting and limits, balance relocation behavior. Source comments describe the scenario as: A general test to validate that balance and qgroups work correctly when balance needs to be resumed on mount. and we need extra device as log device Create enough metadata for later balance Flush delalloc so that balance has work to do. Balance metadata so we will have at least one transaction committed with valid reloc tree, and hopefully another commit with orphan reloc tree. Test that no crashes happen or any other kind of failure. Don't trigger fsck here, as relocation get paused, at that transistent state, qgroup number may differ

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick replay balance qgroup recoveryloop` declares tags `auto quick replay balance qgroup recoveryloop`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`. sourced helpers: `./common/preamble`, `./common/filter`, `./common/dmlogwrites`; requirements: `_require_scratch`, `_require_log_writes`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_require_scratch`; `_log_writes_mkfs >> $seqres.full 2>&1`; `_log_writes_mount`; `$BTRFS_UTIL_PROG quota enable $SCRATCH_MNT >> $seqres.full`; `_qgroup_rescan $SCRATCH_MNT >> $seqres.full`; `_pwrite_byte 0xcd 0 $file_size $SCRATCH_MNT/file_$i > /dev/null`; `sync`; `_run_btrfs_balance_start -f -m $SCRATCH_MNT >> $seqres.full`; `_log_writes_unmount`; `_scratch_mount`; `_scratch_unmount`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Quota-group counters, limits, inherited qgroups, and rescan results are kernel-maintained metadata validated at unmount/check time. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick replay balance qgroup recoveryloop` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Qgroup tests are sensitive to delayed accounting, rescan completion, and checker support for quota validation.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. Most success is absence of unexpected output, ending with `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/190 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/191 -->
# sources/test-tools/xfstests/tests/btrfs/191

## Purpose

`sources/test-tools/xfstests/tests/btrfs/191` is btrfs fstests case `191`. It targets send/receive stream correctness. Source comments describe the scenario as: Test that an incremental send operation works after deduplicating into the same file in both the parent and send snapshots. Create our first file. The first half of the file has several 64Kb extents while the second half as a single 512Kb extent. Create the base snapshot and the parent send stream from it. Create our second file, that has exactly the same data as the first file. Create the second snapshot, used for the incremental send, before doing the file deduplication. Now before creating the incremental send stream: 1) Deduplicate into a subrange of file foo in snapshot mysnap1. This will drop

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick send dedupe` declares tags `auto quick send dedupe`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`; snapshot equivalence is checked with `$FSSUM_PROG`. sourced helpers: `./common/preamble`, `./common/filter`, `./common/reflink`; requirements: `_require_test`, `_require_scratch_dedupe`, `_require_fssum`; local shell helpers: `_cleanup()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `rm -fr $send_files_dir`; `rm -f $tmp.*`; `_require_scratch_dedupe`; `_require_fssum`; `send_files_dir=$TEST_DIR/btrfs-test-$seq`; `mkdir $send_files_dir`; `_scratch_mount`; `$XFS_IO_PROG -f -s -c "pwrite -S 0xb8 -b 64K 0 512K" $SCRATCH_MNT/foo \`; `$XFS_IO_PROG -c "pwrite -S 0xb8 512K 512K" $SCRATCH_MNT/foo | _filter_xfs_io`; `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/mysnap1`; `$BTRFS_UTIL_PROG send -f $send_files_dir/1.snap $SCRATCH_MNT/mysnap1 2>&1 \`; `_scratch_unmount`; `$BTRFS_UTIL_PROG receive -f $send_files_dir/1.snap $SCRATCH_MNT`; `$BTRFS_UTIL_PROG receive -f $send_files_dir/2.snap $SCRATCH_MNT`; `$FSSUM_PROG -r $send_files_dir/1.fssum $SCRATCH_MNT/mysnap1`; `$FSSUM_PROG -r $send_files_dir/2.fssum $SCRATCH_MNT/mysnap2`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Subvolume roots, read-only snapshots, deleted snapshot orphans, and directory entries are persisted across remounts. Send streams, fssum manifests, and received snapshots are temporary artifacts used to compare source and reconstructed filesystems. The script records user-visible checksums, listings, device counters, capabilities, or byte dumps as evidence. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick send dedupe` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Send tests can be fragile around inode-number ordering, rename dependencies, clone commands, xattrs, and receiver mount options.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. `fssum` manifests are written on source snapshots and verified after receive.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/191 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/192 -->
# sources/test-tools/xfstests/tests/btrfs/192

## Purpose

`sources/test-tools/xfstests/tests/btrfs/192` is btrfs fstests case `192`. It targets subvolume/snapshot metadata. Source comments describe the scenario as: Test btrfs consistency after each FUA for a workload with snapshot creation and removal cap nr_cpus to 8 to avoid spending too much time on hosts with many cpus Discard the whole devices so when some tree pointer is wrong, it won't point to some older valid tree blocks, so we can detect it. Use no-holes to avoid warnings of missing file extent items (expected for holes due to mix of buffered and direct IO writes). And use 4K nodesize to bump tree height. Do something small to make snapshots different Replay and check each fua/flush (specified by $2) point.

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto replay snapshot stress recoveryloop` declares tags `auto replay snapshot stress recoveryloop`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`. sourced helpers: `./common/preamble`, `./common/filter`, `./common/attr`, `./common/dmlogwrites`; requirements: `_require_command "$BLKDISCARD_PROG" blkdiscard`, `_require_btrfs_fs_feature "no_holes"`, `_require_btrfs_mkfs_feature "no-holes"`, `_require_log_writes`, `_require_scratch`, `_require_attrs`, `_require_btrfs_support_sectorsize 4096`; local shell helpers: `_cleanup()`, `snapshot_workload()`, `delete_workload()`, `log_writes_fast_replay_check()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `rm -f $tmp.*`; `_require_btrfs_fs_feature "no_holes"`; `_require_btrfs_mkfs_feature "no-holes"`; `_require_scratch`; `_require_attrs`; `_log_writes_mount`; `$BTRFS_UTIL_PROG subvolume create $SCRATCH_MNT/src > /dev/null`; `mkdir -p $SCRATCH_MNT/snapshots`; `snapshot_workload()`; `$BTRFS_UTIL_PROG subvolume snapshot \`; `$SCRATCH_MNT/src $SCRATCH_MNT/snapshots/$i \`; `touch "$SCRATCH_MNT/src/padding/$i"`; `$SETFATTR_PROG -n 'user.x1' -v $xattr_value "$SCRATCH_MNT/src/padding/$i"`; `snapshot_workload &`; `_log_writes_unmount`; `log_writes_fast_replay_check fua "$SCRATCH_DEV"`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Subvolume roots, read-only snapshots, deleted snapshot orphans, and directory entries are persisted across remounts. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto replay snapshot stress recoveryloop` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

It may be slow or disruptive because it reformats scratch storage and may use fault injection or degraded-device mounts.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. Most success is absence of unexpected output, ending with `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/192 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/193 -->
# sources/test-tools/xfstests/tests/btrfs/193

## Purpose

`sources/test-tools/xfstests/tests/btrfs/193` is btrfs fstests case `193`. It targets quota-group accounting and limits. Source comments describe the scenario as: Test if btrfs is going to leak qgroup reserved data space when falloc on multiple holes fails. The fix is titled: "btrfs: qgroup: Fix the wrong target io_tree when freeing reserved data space" Create a file with the following layout: 0         128M      256M      384M |  Hole   |4K| Hole |4K| Hole | The total hole size will be 384M - 8k Falloc 0~384M range, it's going to fail due to the qgroup limit Ensure above delete reaches disk and free some space

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick qgroup enospc limit prealloc` declares tags `auto quick qgroup enospc limit prealloc`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_scratch`, `_require_xfs_io_command falloc`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_require_scratch`; `_require_xfs_io_command falloc`; `_scratch_mkfs > /dev/null`; `_scratch_mount`; `$BTRFS_UTIL_PROG quota enable "$SCRATCH_MNT" > /dev/null`; `_qgroup_rescan "$SCRATCH_MNT" > /dev/null`; `$BTRFS_UTIL_PROG qgroup limit -e 256M "$SCRATCH_MNT"`; `truncate -s 384m "$SCRATCH_MNT/file"`; `$XFS_IO_PROG -c "pwrite 128m 4k" -c "pwrite 256m 4k" \`; `$XFS_IO_PROG -c "falloc 0 384m" "$SCRATCH_MNT/file" | _filter_xfs_io_error`; `rm -f "$SCRATCH_MNT/file"`; `sync`; `$XFS_IO_PROG -f -c "pwrite 0 192m" "$SCRATCH_MNT/file" | _filter_xfs_io`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Quota-group counters, limits, inherited qgroups, and rescan results are kernel-maintained metadata validated at unmount/check time. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick qgroup enospc limit prealloc` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Qgroup tests are sensitive to delayed accounting, rescan completion, and checker support for quota validation.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/193 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/194 -->
# sources/test-tools/xfstests/tests/btrfs/194

## Purpose

`sources/test-tools/xfstests/tests/btrfs/194` is btrfs fstests case `194`. It targets multi-device or RAID volume behavior. Source comments describe the scenario as: Test if btrfs can handle large device ids. The regression is introduced by kernel commit ab4ba2e13346 ("btrfs: tree-checker: Verify dev item"). The fix is titled: "btrfs: tree-checker: Fix wrong check on max devid" Here we use 4k node size to reduce runtime (explained near _scratch_mkfs call) To use the minimal node size (4k) we need 4K page size. The wrong check limit is based on the max item size (BTRFS_MAX_DEVS() macro), and max item size is based on node size, so smaller node size will result much shorter runtime. So here we use minimal node size (4K) to reduce runtime. For 4k nodesize, the wrong limit is calculated by:

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto volume` declares tags `auto volume`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_scratch_dev_pool 2`, `_require_btrfs_support_sectorsize 4096`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_require_scratch_dev_pool 2`; `_scratch_dev_pool_get 2`; `_require_btrfs_support_sectorsize 4096`; `device_1=$(echo $SCRATCH_DEV_POOL | $AWK_PROG '{print $1}')`; `device_2=$(echo $SCRATCH_DEV_POOL | $AWK_PROG '{print $2}')`; `echo device_1=$device_1 device_2=$device_2 >> $seqres.full`; `_scratch_mkfs -n 4k -s 4k >> $seqres.full`; `_scratch_mount`; `$BTRFS_UTIL_PROG device add -f $device_2 $SCRATCH_MNT >> $seqres.full`; `$BTRFS_UTIL_PROG device del $device_1 $SCRATCH_MNT`; `$BTRFS_UTIL_PROG device add -f $device_1 $SCRATCH_MNT >> $seqres.full`; `$BTRFS_UTIL_PROG device del $device_2 $SCRATCH_MNT`; `done | grep -v 'Resetting device zone'`; `_scratch_dev_pool_put`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Device identity, missing-device state, degraded mounts, and balance/repair writes are part of the persistent test surface. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto volume` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

It may be slow or disruptive because it reformats scratch storage and may use fault injection or degraded-device mounts. Multi-device tests need enough disposable devices and can leave device scans cached if cleanup does not run.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. Most success is absence of unexpected output, ending with `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/194 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/195 -->
# sources/test-tools/xfstests/tests/btrfs/195

## Purpose

`sources/test-tools/xfstests/tests/btrfs/195` is btrfs fstests case `195`. It targets multi-device or RAID volume behavior, balance relocation behavior, checksum, scrub, or read-repair paths. Source comments describe the scenario as: Test raid profile conversion. It's sufficient to test all dest profiles as source profiles just rely on being able to read the data and metadata. Zoned btrfs only supports SINGLE profile Load up the available configs $nr_dev_min:$data:$metadata:$data_convert:$metadata_convert Create random filesystem with 20k write ops

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto volume balance scrub raid` declares tags `auto volume balance scrub raid`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_scratch_dev_pool 4`, `_require_non_zoned_device "${SCRATCH_DEV}"`; local shell helpers: `run_testcase()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_require_scratch_dev_pool 4`; `_require_non_zoned_device "${SCRATCH_DEV}"`; `_btrfs_get_profile_configs`; `"4:single:raid1"`; `"4:single:raid0"`; `_scratch_mount`; `_run_btrfs_balance_start -f -dconvert=$dst_type $SCRATCH_MNT >> $seqres.full`; `$BTRFS_UTIL_PROG scrub start -B $SCRATCH_MNT >>$seqres.full 2>&1`; `_scratch_unmount`; `_check_btrfs_filesystem $SCRATCH_DEV`; `_scratch_dev_pool_put`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Device identity, missing-device state, degraded mounts, and balance/repair writes are part of the persistent test surface. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto volume balance scrub raid` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

It may be slow or disruptive because it reformats scratch storage and may use fault injection or degraded-device mounts. Multi-device tests need enough disposable devices and can leave device scans cached if cleanup does not run.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. Most success is absence of unexpected output, ending with `Silence is golden`. A foreground scrub must complete without reported errors.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/195 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/196 -->
# sources/test-tools/xfstests/tests/btrfs/196

## Purpose

`sources/test-tools/xfstests/tests/btrfs/196` is btrfs fstests case `196`. It targets log-tree replay and fsync crash recovery, multi-device or RAID volume behavior. Source comments describe the scenario as: Test multi subvolume fsync to test a bug where we'd end up pointing at a block we haven't written.  This was fixed by the patch btrfs: fix incorrect updating of log root tree Will do log replay and check the filesystem. Use thin device as replay device, which requires $SCRATCH_DEV and we need extra device as log device Use a thin device to provide deterministic discard behavior. Discards are used by the log replay tool for fast zeroing to prevent out-of-order replay issues. First create all the subvolumes We need to mount the fs because btrfsck won't bother checking the log.

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto metadata log volume` declares tags `auto metadata log volume`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`. sourced helpers: `./common/preamble`, `./common/filter`, `./common/dmthin`, `./common/dmlogwrites`; requirements: `_require_scratch_nocheck`, `_require_log_writes`, `_require_dm_target thin-pool`, `_require_fio $fio_config`; local shell helpers: `_cleanup()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `rm -f $tmp.*`; `_require_scratch_nocheck`; `fallocate=none`; `fsync=1`; `echo "filename=$SCRATCH_MNT/$i/file" >> $fio_config`; `_log_writes_mkfs >> $seqres.full 2>&1`; `_log_writes_mark mkfs`; `_log_writes_mount`; `$BTRFS_UTIL_PROG subvolume create "$SCRATCH_MNT/$i" > /dev/null`; `_log_writes_unmount`; `prev=$(_log_writes_mark_to_entry_number mkfs)`; `[ -z "$prev" ] && _fail "failed to locate entry mark 'mkfs'"`; `_dmthin_mount`; `_dmthin_check_fs`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Subvolume roots, read-only snapshots, deleted snapshot orphans, and directory entries are persisted across remounts. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto metadata log volume` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

It may be slow or disruptive because it reformats scratch storage and may use fault injection or degraded-device mounts. Multi-device tests need enough disposable devices and can leave device scans cached if cleanup does not run.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. Most success is absence of unexpected output, ending with `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/196 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/197 -->
# sources/test-tools/xfstests/tests/btrfs/197

## Purpose

`sources/test-tools/xfstests/tests/btrfs/197` is btrfs fstests case `197`. It targets multi-device or RAID volume behavior. Source comments describe the scenario as: Test stale and alien btrfs-device in the fs devices list. Bug fixed in the kernel patch: btrfs: include non-missing as a qualifier for the latest_bdev btrfs: remove identified alien btrfs device in open_fs_devices We require at least one raid setup, raid1 is the easiest, use this to gate on wether or not we run this test Make device # 2 an alien btrfs device for the raid created above by adding it to the $TEST_DIR/$seq.mnt don't test with the first device as auto fs check (_check_scratch_fs) picks the first device

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick volume raid` declares tags `auto quick volume raid`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`. sourced helpers: `./common/preamble`, `./common/filter.btrfs`; requirements: `_require_test`, `_require_scratch`, `_require_scratch_dev_pool 5`, `_require_btrfs_raid_type raid1`; local shell helpers: `_cleanup()`, `workout()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `$UMOUNT_PROG $TEST_DIR/$seq.mnt >/dev/null 2>&1`; `rm -rf $TEST_DIR/$seq.mnt`; `rm -f $tmp.*`; `_require_scratch`; `_require_scratch_dev_pool 5`; `device_nr=$2`; `_scratch_dev_pool_get $device_nr`; `_mount $SPARE_DEV $TEST_DIR/$seq.mnt`; `$BTRFS_UTIL_PROG device add -f "${SCRATCH_DEV_NAME[1]}" "$TEST_DIR/$seq.mnt" >> \`; `_mount -o degraded ${SCRATCH_DEV_NAME[0]} $SCRATCH_MNT`; `grep -q "${SCRATCH_DEV_NAME[1]}" $tmp.output && _fail "found stale device"`; `_scratch_dev_pool_put`; `workout "raid1" "2"`; `workout "raid5" "3"`; `workout "raid6" "4"`; `workout "raid10" "4"`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Device identity, missing-device state, degraded mounts, and balance/repair writes are part of the persistent test surface. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick volume raid` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Multi-device tests need enough disposable devices and can leave device scans cached if cleanup does not run.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. Most success is absence of unexpected output, ending with `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/197 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/198 -->
# sources/test-tools/xfstests/tests/btrfs/198

## Purpose

`sources/test-tools/xfstests/tests/btrfs/198` is btrfs fstests case `198`. It targets multi-device or RAID volume behavior. Source comments describe the scenario as: Test outdated and foreign non-btrfs devices in the device listing. We require at least one raid setup, raid1 is the easiest, use this to gate on wether or not we run this test Make ${SCRATCH_DEV_NAME[1]} a free btrfs device for the raid created above by clearing its superblock don't test with the first device as auto fs check (_check_scratch_fs) picks the first device Check if missing device is reported as in the 196.out

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick volume raid` declares tags `auto quick volume raid`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`. sourced helpers: `./common/preamble`, `./common/filter`, `./common/filter.btrfs`; requirements: `_require_command "$WIPEFS_PROG" wipefs`, `_require_scratch`, `_require_scratch_dev_pool 4`, `_require_btrfs_raid_type raid1`; local shell helpers: `workout()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_require_scratch`; `_require_scratch_dev_pool 4`; `_require_btrfs_raid_type raid1`; `"btrfs: skip devices without magic signature when mounting"`; `raid=$1`; `device_nr=$2`; `_scratch_dev_pool_get $device_nr`; `_mount -o degraded ${SCRATCH_DEV_NAME[0]} $SCRATCH_MNT`; `grep -q "${SCRATCH_DEV_NAME[1]}" $tmp.output && _fail "found stale device"`; `_scratch_dev_pool_put`; `workout "raid1" "2"`; `workout "raid5" "3"`; `workout "raid6" "4"`; `workout "raid10" "4"`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Device identity, missing-device state, degraded mounts, and balance/repair writes are part of the persistent test surface. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick volume raid` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Multi-device tests need enough disposable devices and can leave device scans cached if cleanup does not run.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. Most success is absence of unexpected output, ending with `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/198 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/199 -->
# sources/test-tools/xfstests/tests/btrfs/199

## Purpose

`sources/test-tools/xfstests/tests/btrfs/199` is btrfs fstests case `199`. It targets the btrfs feature area named by its fstests tags. Source comments describe the scenario as: Test if btrfs discard mount option is trimming adjacent extents across block groups boundary. The test case uses loopback device and file used space to detect trimmed bytes. There is a long existing bug that btrfs doesn't discard all space for above mentioned case. We need less than 2G data write, consider it 2G and double it just in case The margin when checking trimmed size. The margin is for tree blocks, calculated by 3 * max_tree_block_size

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick trim fiemap` declares tags `auto quick trim fiemap`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_loop`, `_require_xfs_io_command "fiemap"`, `_require_scratch_size	$((4 * 1024 * 1024))`, `_notrun "Non-continuous extent bytenr detected"`; local shell helpers: `_cleanup()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `umount $loop_mnt &> /dev/null`; `_destroy_loop_device $loop_dev &> /dev/null`; `rm -rf $tmp.*`; `_require_loop`; `_require_scratch_size	$((4 * 1024 * 1024))`; `loop_file="$SCRATCH_MNT/image"`; `_scratch_mount`; `truncate -s 10G "$loop_file"`; `_mkfs_dev -d SINGLE "$loop_file"`; `loop_dev=$(_create_loop_device "$loop_file")`; `loop_mnt=$tmp/loop_mnt`; `size1_kb=$(du $loop_file| cut -f1)`; `rm -f $loop_mnt/cross_boundary`; `size2_kb=$(du $loop_file | cut -f1)`; `echo "loopback file size before discard: $size1_kb KiB" >> $seqres.full`; `echo "loopback file size after discard:  $size2_kb KiB" >> $seqres.full`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. The script records user-visible checksums, listings, device counters, capabilities, or byte dumps as evidence. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick trim fiemap` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

The main risk is environmental: missing fstests helpers, unsupported btrfs features, or changed userspace output can turn the test into a notrun or golden-output mismatch.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. Most success is absence of unexpected output, ending with `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/199 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/200 -->
# sources/test-tools/xfstests/tests/btrfs/200

## Purpose

`sources/test-tools/xfstests/tests/btrfs/200` is btrfs fstests case `200`. It targets send/receive stream correctness. Source comments describe the scenario as: Check that send operations (full and incremental) are able to issue clone operations for extents that are shared between the same file. Create our first test file, which has an extent that is shared only with itself and no other files. We want to verify a full send operation will clone the extent. Create out second test file which initially, for the first send operation, only has a single extent that is not shared. Now clone the existing extent in file bar to itself at a different offset. We want to verify the incremental send operation below will issue a clone operation instead of a write operation.

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick send clone fiemap` declares tags `auto quick send clone fiemap`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`; snapshot equivalence is checked with `$FSSUM_PROG`. sourced helpers: `./common/preamble`, `./common/filter`, `./common/reflink`, `./common/punch`; requirements: `_require_fssum`, `_require_test`, `_require_scratch_reflink`, `_require_xfs_io_command "fiemap"`; local shell helpers: `_cleanup()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `rm -f $tmp.*`; `rm -fr $send_files_dir`; `_require_fssum`; `_require_scratch_reflink`; `send_files_dir=$TEST_DIR/btrfs-test-$seq`; `mkdir $send_files_dir`; `_scratch_mount`; `$XFS_IO_PROG -f -c "pwrite -S 0xb1 -b 128K 0 128K" $SCRATCH_MNT/foo \`; `$XFS_IO_PROG -c "reflink $SCRATCH_MNT/foo 0 128K 128K" $SCRATCH_MNT/foo \`; `$XFS_IO_PROG -f -c "pwrite -S 0xc7 -b 128K 0 128K" $SCRATCH_MNT/bar \`; `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/base`; `$XFS_IO_PROG -r -c "fiemap" $SCRATCH_MNT/incr/foo`; `num_extents=$(_count_extents $SCRATCH_MNT/incr/bar)`; `num_exclusive_extents=$(_count_exclusive_extents $SCRATCH_MNT/incr/bar)`; `echo "File bar does not have 2 shared extents in the incr snapshot"`; `$XFS_IO_PROG -r -c "fiemap" $SCRATCH_MNT/incr/bar`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Subvolume roots, read-only snapshots, deleted snapshot orphans, and directory entries are persisted across remounts. Send streams, fssum manifests, and received snapshots are temporary artifacts used to compare source and reconstructed filesystems. The script records user-visible checksums, listings, device counters, capabilities, or byte dumps as evidence. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick send clone fiemap` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Send tests can be fragile around inode-number ordering, rename dependencies, clone commands, xattrs, and receiver mount options.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. `fssum` manifests are written on source snapshots and verified after receive.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/200 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/201 -->
# sources/test-tools/xfstests/tests/btrfs/201

## Purpose

`sources/test-tools/xfstests/tests/btrfs/201` is btrfs fstests case `201`. It targets log-tree replay and fsync crash recovery. Source comments describe the scenario as: Test that when we have the no-holes feature enabled and a specific metadata layout, if we punch a hole that starts at file offset 0 and fsync the file, after replaying the log the hole exists. We create the filesystem with a node size of 64Kb because we need to create a specific metadata layout in order to trigger the bug we are testing. At the moment the node size can not be smaller then the system's page size, so given that the largest possible page size is 64Kb and by default the node size is set to the system's page size value, we explicitly create a filesystem with a 64Kb node size, so that the test can run reliably independently of the system's page size.

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick punch log` declares tags `auto quick punch log`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`. sourced helpers: `./common/preamble`, `./common/attr`, `./common/filter`, `./common/dmflakey`; requirements: `_require_scratch`, `_require_dm_target flakey`, `_require_attrs`, `_require_xfs_io_command "fpunch"`, `_require_btrfs_fs_feature "no_holes"`, `_require_btrfs_mkfs_feature "no-holes"`, `_require_odirect`, `_require_metadata_journaling $SCRATCH_DEV`, `_require_metadata_journaling $SCRATCH_DEV`; local shell helpers: `_cleanup()`, `run_test_leading_hole()`, `run_test_middle_hole()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_cleanup_flakey`; `rm -f $tmp.*`; `_require_scratch`; `_require_dm_target flakey`; `_require_attrs`; `_init_flakey`; `_scratch_mount`; `$XFS_IO_PROG -f -d -c "pwrite -S 0xab -b 64K $offset 64K" \`; `$XFS_IO_PROG -c "fpunch 0 64K" -c "fsync" $SCRATCH_MNT/bar`; `md5sum $SCRATCH_MNT/bar | _filter_scratch`; `_flakey_drop_and_remount`; `_scratch_unmount`; `$XFS_IO_PROG -c "fpunch $hole_offset $hole_len" \`; `-c "pwrite -S 0xf1 131072000 64K" \`; `-c "fsync" $SCRATCH_MNT/bar >/dev/null`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. The dm-flakey helper deliberately drops writes and remounts to force replay of whatever reached the btrfs log tree. The script records user-visible checksums, listings, device counters, capabilities, or byte dumps as evidence. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick punch log` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

The pass/fail signal depends on realistic crash semantics from dm-flakey and on metadata journaling being available.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. Before/after checksums must match across remount, balance, or receive.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/201 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/202 -->
# sources/test-tools/xfstests/tests/btrfs/202

## Purpose

`sources/test-tools/xfstests/tests/btrfs/202` is btrfs fstests case `202`. It targets subvolume/snapshot metadata. Source comments describe the scenario as: Regression test for fix "btrfs: fix invalid removal of root ref" Create a subvol b under a and then snapshot a into c.  This create's a stub entry in c for b because c doesn't have a reference for b. But when we rename b c/foo it creates a ref for b in c.  However if we go to remove c/b btrfs used to depend on not finding the root ref to handle the unlink properly, but we now have a ref for that root.  We also had a bug that would allow us to remove mis-matched refs if the keys matched, so we'd end up removing too many entries which would cause a transaction abort. Need the dummy entry created so that we get the invalid removal when we rmdir

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick subvol snapshot` declares tags `auto quick subvol snapshot`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_scratch`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_require_scratch`; `_scratch_mkfs >> $seqres.full 2>&1`; `_scratch_mount`; `$BTRFS_UTIL_PROG subvolume create $SCRATCH_MNT/a | _filter_scratch`; `$BTRFS_UTIL_PROG subvolume create $SCRATCH_MNT/a/b | _filter_scratch`; `_btrfs subvolume snapshot $SCRATCH_MNT/a $SCRATCH_MNT/c`; `mkdir $SCRATCH_MNT/c/foo`; `mv $SCRATCH_MNT/a/b $SCRATCH_MNT/c/foo`; `rm -rf $SCRATCH_MNT/*`; `touch $SCRATCH_MNT/blah`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Subvolume roots, read-only snapshots, deleted snapshot orphans, and directory entries are persisted across remounts. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick subvol snapshot` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

The main risk is environmental: missing fstests helpers, unsupported btrfs features, or changed userspace output can turn the test into a notrun or golden-output mismatch.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/202 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/203 -->
# sources/test-tools/xfstests/tests/btrfs/203

## Purpose

`sources/test-tools/xfstests/tests/btrfs/203` is btrfs fstests case `203`. It targets send/receive stream correctness. Source comments describe the scenario as: Test that an incremental send operation works correctly when a file has shared extents with itself in the send snapshot, with a hole between them, and the file size has increased in the send snapshot. Create our test file with a size of 64K in the parent snapshot. After the parent snapshot is created, we will increase its size and then clone one of its extents into a different offset and leave a hole between the shared extents. The shared extents will be located at offsets greater then size of the file in the parent snapshot. Create a 320K extent at file offset 512K, with chunks of 64K having different content (to check cloning operations from send refer to the correct ranges).

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick send clone` declares tags `auto quick send clone`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`. sourced helpers: `./common/preamble`, `./common/filter`, `./common/reflink`; requirements: `_require_test`, `_require_scratch_reflink`; local shell helpers: `_cleanup()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `rm -f $tmp.*`; `rm -fr $send_files_dir`; `_require_scratch_reflink`; `send_files_dir=$TEST_DIR/btrfs-test-$seq`; `mkdir $send_files_dir`; `_scratch_mount`; `$XFS_IO_PROG -f -c "pwrite -S 0xf1 0 64K" $SCRATCH_MNT/foobar | _filter_xfs_io`; `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/base`; `$BTRFS_UTIL_PROG send -f $send_files_dir/1.snap $SCRATCH_MNT/base 2>&1 \`; `$XFS_IO_PROG -c "pwrite -S 0xab 512K 64K" \`; `-c "pwrite -S 0xcd 576K 64K" \`; `$SCRATCH_MNT/incr 2>&1 | _filter_scratch`; `_md5_checksum $SCRATCH_MNT/incr/foobar`; `_scratch_unmount`; `$BTRFS_UTIL_PROG receive -f $send_files_dir/1.snap $SCRATCH_MNT`; `$BTRFS_UTIL_PROG receive -f $send_files_dir/2.snap $SCRATCH_MNT`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Subvolume roots, read-only snapshots, deleted snapshot orphans, and directory entries are persisted across remounts. Send streams, fssum manifests, and received snapshots are temporary artifacts used to compare source and reconstructed filesystems. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick send clone` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Send tests can be fragile around inode-number ordering, rename dependencies, clone commands, xattrs, and receiver mount options.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. Before/after checksums must match across remount, balance, or receive.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/203 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/204 -->
# sources/test-tools/xfstests/tests/btrfs/204

## Purpose

`sources/test-tools/xfstests/tests/btrfs/204` is btrfs fstests case `204`. It targets the btrfs feature area named by its fstests tags. Source comments describe the scenario as: Test if the unaligned (by size and offset) punch hole is successful when FS is at ENOSPC. max_inline ensures data is not inlined within metadata extents

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick punch` declares tags `auto quick punch`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_scratch`, `_require_xfs_io_command "fpunch"`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_require_scratch`; `_scratch_mkfs_sized $((256 * 1024 *1024)) >> $seqres.full`; `_scratch_mount "-o max_inline=0,nodatacow"`; `cat /proc/self/mounts | grep $SCRATCH_DEV >> $seqres.full`; `$BTRFS_UTIL_PROG filesystem df $SCRATCH_MNT >> $seqres.full`; `extent_size=$(_scratch_btrfs_sectorsize)`; `$XFS_IO_PROG -f -c "pwrite -S 0xab 0 $((extent_size * 10))" \`; `dd status=none if=/dev/zero of=$SCRATCH_MNT/filler bs=512 >> $seqres.full 2>&1`; `$XFS_IO_PROG -c "fpunch $hole_offset $hole_len" $SCRATCH_MNT/testfile`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick punch` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

The main risk is environmental: missing fstests helpers, unsupported btrfs features, or changed userspace output can turn the test into a notrun or golden-output mismatch.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. Most success is absence of unexpected output, ending with `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/204 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/205 -->
# sources/test-tools/xfstests/tests/btrfs/205

## Purpose

`sources/test-tools/xfstests/tests/btrfs/205` is btrfs fstests case `205`. It targets compression interactions. Source comments describe the scenario as: Test several scenarios of cloning operations where the source range includes inline extents. They used to not be supported on btrfs because their implementation was not straightforward, and therefore these operations used to fail with errno EOPNOTSUPP on older kernels. Support for this was added by a patch with the following subject: "Btrfs: implement full reflink support for inline extents" We want to create a compressed inline extent representing 4K of data for file foo1 and then clone it into a file without compression, and since compression implies datasum, cloning fails if the destination file has nodatasum. So skip the test if nodatasum is present in MOUNT_OPTIONS.

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick clone compress prealloc` declares tags `auto quick clone compress prealloc`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`. sourced helpers: `./common/preamble`, `./common/filter`, `./common/reflink`; requirements: `_require_scratch_reflink`, `_require_xfs_io_command "falloc" "-k"`, `_require_command "$CHATTR_PROG" chattr`, `_require_btrfs_fs_feature "no_holes"`, `_require_btrfs_mkfs_feature "no-holes"`, `_require_btrfs_no_nodatasum`; local shell helpers: `run_tests()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_require_scratch_reflink`; `_require_xfs_io_command "falloc" "-k"`; `_require_command "$CHATTR_PROG" chattr`; `_require_btrfs_fs_feature "no_holes"`; `_require_btrfs_mkfs_feature "no-holes"`; `$XFS_IO_PROG -c "pwrite -S 0xab 0 4K" \`; `-c "fsync" \`; `-c "pwrite -S 0xab 4K 124K" \`; `$XFS_IO_PROG -f -c "pwrite -S 0xcd 0 128K" $SCRATCH_MNT/bar1 | _filter_xfs_io`; `$XFS_IO_PROG -c "reflink $SCRATCH_MNT/foo1 0 128K 128K" $SCRATCH_MNT/bar1 \`; `$XFS_IO_PROG -f -c "pwrite -S 0xab 0 1000" \`; `_scratch_mount`; `_scratch_cycle_mount "compress"`; `_scratch_cycle_mount "nodatacow"`; `_scratch_unmount`; `_scratch_mkfs "-O no-holes" >>$seqres.full 2>&1`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick clone compress prealloc` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Compression, inline-extent thresholds, and page or sector size can change the exact layout being exercised.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. Before/after checksums must match across remount, balance, or receive.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/205 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/206 -->
# sources/test-tools/xfstests/tests/btrfs/206

## Purpose

`sources/test-tools/xfstests/tests/btrfs/206` is btrfs fstests case `206`. It targets log-tree replay and fsync crash recovery. Source comments describe the scenario as: Validate that without no-holes we do not get a i_size that is after a gap in the file extents on disk when punching a hole past i_size.  This is fixed by the following patches btrfs: use the file extent tree infrastructure btrfs: replace all uses of btrfs_ordered_update_i_size block-group-tree requires no-holes There's not a straightforward way to commit the transaction without also flushing dirty pages, so shorten the commit interval to 1 so we're sure to get a commit with our broken file This creates a gap extent because fpunch doesn't insert hole extents past

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick log replay recoveryloop punch prealloc` declares tags `auto quick log replay recoveryloop punch prealloc`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`. sourced helpers: `./common/preamble`, `./common/filter`, `./common/dmlogwrites`; requirements: `_require_test`, `_require_scratch`, `_require_log_writes`, `_require_xfs_io_command "falloc" "-k"`, `_require_xfs_io_command "fpunch"`, `_require_btrfs_no_block_group_tree`; local shell helpers: `_cleanup()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `rm -f $tmp.*`; `_require_scratch`; `_require_xfs_io_command "falloc" "-k"`; `_require_btrfs_no_block_group_tree`; `_log_writes_mkfs "-O ^no-holes" >> $seqres.full 2>&1`; `_log_writes_mount -o commit=1`; `$XFS_IO_PROG -f -c "falloc -k 4k 8k" $SCRATCH_MNT/file`; `$XFS_IO_PROG -f -c "fpunch 4k 4k" $SCRATCH_MNT/file`; `$XFS_IO_PROG -f -c "pwrite 0 4k" $SCRATCH_MNT/file | _filter_xfs_io`; `$XFS_IO_PROG -f -c "pwrite 0 8k" $SCRATCH_MNT/file | _filter_xfs_io`; `$XFS_IO_PROG -f -c "truncate 12k" $SCRATCH_MNT/file`; `_log_writes_unmount`; `_check_scratch_fs`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick log replay recoveryloop punch prealloc` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

The main risk is environmental: missing fstests helpers, unsupported btrfs features, or changed userspace output can turn the test into a notrun or golden-output mismatch.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. fstests scratch checking validates filesystem and qgroup consistency after unmount.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/206 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/207 -->
# sources/test-tools/xfstests/tests/btrfs/207

## Purpose

`sources/test-tools/xfstests/tests/btrfs/207` is btrfs fstests case `207`. It targets multi-device or RAID volume behavior. Source comments describe the scenario as: Test large DIO reads and writes with various profiles. Regression test for patch "btrfs: fix RAID direct I/O reads with alternate csums". we check scratch dev after each loop

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto rw raid` declares tags `auto rw raid`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_scratch_nocheck`, `_require_scratch_dev_pool 4`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_require_scratch_nocheck`; `_require_scratch_dev_pool 4`; `_btrfs_get_profile_configs`; `for mkfs_opts in "${_btrfs_profile_configs[@]}"; do`; `echo "Test $mkfs_opts" >>$seqres.full`; `_scratch_pool_mkfs $mkfs_opts >>$seqres.full 2>&1`; `_scratch_mount >>$seqres.full 2>&1`; `dd if=/dev/urandom of="$SCRATCH_MNT/$seq" \`; `bs=1M count=64 conv=fsync status=none`; `dd if="$SCRATCH_MNT/$seq" of="$SCRATCH_MNT/$seq.dioread" \`; `dd if="$SCRATCH_MNT/$seq" of="$SCRATCH_MNT/$seq.diowrite" \`; `_scratch_unmount`; `_check_scratch_fs`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Device identity, missing-device state, degraded mounts, and balance/repair writes are part of the persistent test surface. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto rw raid` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

It may be slow or disruptive because it reformats scratch storage and may use fault injection or degraded-device mounts. Multi-device tests need enough disposable devices and can leave device scans cached if cleanup does not run.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. Most success is absence of unexpected output, ending with `Silence is golden`. fstests scratch checking validates filesystem and qgroup consistency after unmount.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/207 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/208 -->
# sources/test-tools/xfstests/tests/btrfs/208

## Purpose

`sources/test-tools/xfstests/tests/btrfs/208` is btrfs fstests case `208`. It targets subvolume/snapshot metadata. Source comments describe the scenario as: Test subvolume deletion using the subvolume id, even when the subvolume in question is in a different mount space. Test creating a normal subvolumes Delete the subvolume subvol1, and list the remaining two subvolumes Now we mount the subvol2, which makes subvol3 not accessible for this mount point, but we should be able to delete it using it's subvolume id now mount the rootfs Delete the subvol2

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick subvol` declares tags `auto quick subvol`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`. sourced helpers: `./common/preamble`, `./common/filter`, `./common/filter.btrfs`; requirements: `_require_scratch`, `_require_btrfs_command subvolume delete --subvolid`; local shell helpers: `_delete_and_list()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_require_scratch`; `_require_btrfs_command subvolume delete --subvolid`; `_scratch_mkfs > /dev/null 2>&1`; `_scratch_mount`; `SUBVOLID=$(_btrfs_get_subvolid $SCRATCH_MNT "$subvol_name")`; `$BTRFS_UTIL_PROG subvolume delete --subvolid $SUBVOLID $SCRATCH_MNT | _filter_btrfs_subvol_delete`; `$BTRFS_UTIL_PROG subvolume list $SCRATCH_MNT | $AWK_PROG '{ print $NF }'`; `$BTRFS_UTIL_PROG subvolume create $SCRATCH_MNT/subvol1 | _filter_scratch`; `$BTRFS_UTIL_PROG subvolume create $SCRATCH_MNT/subvol2 | _filter_scratch`; `$BTRFS_UTIL_PROG subvolume create $SCRATCH_MNT/subvol3 | _filter_scratch`; `echo "Current subvolume ids:"`; `_delete_and_list subvol1 "After deleting one subvolume:"`; `_scratch_unmount`; `$MOUNT_PROG -o subvol=subvol2 $SCRATCH_DEV $SCRATCH_MNT`; `_delete_and_list subvol3 "Last remaining subvolume:"`; `_delete_and_list subvol2 "All subvolumes removed."`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Subvolume roots, read-only snapshots, deleted snapshot orphans, and directory entries are persisted across remounts. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick subvol` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

The main risk is environmental: missing fstests helpers, unsupported btrfs features, or changed userspace output can turn the test into a notrun or golden-output mismatch.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/208 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/209 -->
# sources/test-tools/xfstests/tests/btrfs/209

## Purpose

`sources/test-tools/xfstests/tests/btrfs/209` is btrfs fstests case `209`. It targets log-tree replay and fsync crash recovery, mmap/msync persistence. Source comments describe the scenario as: Test a scenario were we fsync a range of a file and have a power failure. We want to check that after a power failure and mounting the filesystem, we do not end up with a missing file extent representing a hole. This applies only when not using the NO_HOLES feature. Create a 256K file with a single extent and fsync it to clear the full sync bit from the inode - we want the msync below to trigger a fast fsync. Force a transaction commit and wipe out the log tree. Dirty 768K of data, increasing the file size to 1Mb, and flush only the range from 256K to 512K without updating the log tree (sync_file_range() does not trigger fsync, it only starts writeback and waits for it to finish).

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick log mmap` declares tags `auto quick log mmap`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`. sourced helpers: `./common/preamble`, `./common/attr`, `./common/filter`, `./common/dmflakey`; requirements: `_require_scratch`, `_require_dm_target flakey`, `_require_btrfs_fs_feature "no_holes"`, `_require_btrfs_mkfs_feature "no-holes"`, `_require_xfs_io_command "sync_range"`, `_require_metadata_journaling $SCRATCH_DEV`; local shell helpers: `_cleanup()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_cleanup_flakey`; `rm -f $tmp.*`; `_require_scratch`; `_require_dm_target flakey`; `_require_btrfs_fs_feature "no_holes"`; `_init_flakey`; `_scratch_mount`; `-c "pwrite -S 0xab 0 256K" \`; `-c "fsync" \`; `$XFS_IO_PROG -c "pwrite -S 0xcd 256K 768K" \`; `-c "msync -s 768K 256K"       \`; `echo "File digest before power failure: $(_md5_checksum $SCRATCH_MNT/foo)"`; `_flakey_drop_and_remount`; `echo "File digest after power failure: $(_md5_checksum $SCRATCH_MNT/foo)"`; `_scratch_unmount`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. The dm-flakey helper deliberately drops writes and remounts to force replay of whatever reached the btrfs log tree. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick log mmap` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

The pass/fail signal depends on realistic crash semantics from dm-flakey and on metadata journaling being available.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. Before/after checksums must match across remount, balance, or receive.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/209 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/210 -->
# sources/test-tools/xfstests/tests/btrfs/210

## Purpose

`sources/test-tools/xfstests/tests/btrfs/210` is btrfs fstests case `210`. It targets subvolume/snapshot metadata, quota-group accounting and limits. Source comments describe the scenario as: Test that a new snapshot created with qgroup inherit passed should mark qgroup numbers inconsistent. Sync the fs to ensure data written to disk so that they can be accounted by qgroup Create a snapshot with qgroup inherit If qgroup is not marked inconsistent automatically, btrfs check would report error.

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick qgroup snapshot` declares tags `auto quick qgroup snapshot`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_scratch`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_require_scratch`; `_scratch_mkfs >/dev/null`; `_scratch_mount`; `$BTRFS_UTIL_PROG subvolume create "$SCRATCH_MNT/src" > /dev/null`; `_pwrite_byte 0xcd 0 16M "$SCRATCH_MNT/src/file" > /dev/null`; `sync`; `$BTRFS_UTIL_PROG quota enable "$SCRATCH_MNT"`; `_qgroup_rescan "$SCRATCH_MNT" > /dev/null`; `$BTRFS_UTIL_PROG qgroup create 1/0 "$SCRATCH_MNT"`; `$BTRFS_UTIL_PROG subvolume snapshot -i 1/0 "$SCRATCH_MNT/src" \`; `"$SCRATCH_MNT/snapshot" > /dev/null`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Subvolume roots, read-only snapshots, deleted snapshot orphans, and directory entries are persisted across remounts. Quota-group counters, limits, inherited qgroups, and rescan results are kernel-maintained metadata validated at unmount/check time. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick qgroup snapshot` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Qgroup tests are sensitive to delayed accounting, rescan completion, and checker support for quota validation.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. Most success is absence of unexpected output, ending with `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/210 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/211 -->
# sources/test-tools/xfstests/tests/btrfs/211

## Purpose

`sources/test-tools/xfstests/tests/btrfs/211` is btrfs fstests case `211`. It targets log-tree replay and fsync crash recovery. Source comments describe the scenario as: Test that if we fsync a file with prealloc extents that start before and after the file's size, we don't end up with missing parts of the extents and implicit file holes after a power failure. Test both without and with the NO_HOLES feature. fiemap needed by _count_extents() Create our test file with 2 consecutive prealloc extents, each with a size of 128Kb, and covering the range from 0 to 256Kb, with a file size of 0. Then fsync the file to record both extents in a log tree. Now do a redudant extent allocation for the range from 0 to 64Kb. This will merely increase the file size from 0 to 64Kb. Instead we could also do a

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick log prealloc fiemap` declares tags `auto quick log prealloc fiemap`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`. sourced helpers: `./common/preamble`, `./common/filter`, `./common/dmflakey`; requirements: `_require_scratch`, `_require_xfs_io_command "falloc" "-k"`, `_require_xfs_io_command "fiemap"`, `_require_btrfs_fs_feature "no_holes"`, `_require_btrfs_mkfs_feature "no-holes"`, `_require_dm_target flakey`, `_require_metadata_journaling $SCRATCH_DEV`, `_require_metadata_journaling $SCRATCH_DEV`; local shell helpers: `_cleanup()`, `run_test()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_cleanup_flakey`; `rm -f $tmp.*`; `_require_scratch`; `_require_xfs_io_command "falloc" "-k"`; `_require_btrfs_fs_feature "no_holes"`; `_require_dm_target flakey`; `$XFS_IO_PROG -f -c "falloc -k 0 128K" $SCRATCH_MNT/foo`; `$XFS_IO_PROG -c "falloc -k 128K 128K" $SCRATCH_MNT/foo`; `$XFS_IO_PROG -c "fsync" $SCRATCH_MNT/foo`; `$XFS_IO_PROG -c "falloc 0 64K" $SCRATCH_MNT/foo`; `$XFS_IO_PROG -c "truncate 256K" -c "fsync" $SCRATCH_MNT/foo`; `_scratch_mount`; `$XFS_IO_PROG -c "pwrite -S 0xab 0 128K" $SCRATCH_MNT/foo | _filter_xfs_io`; `_scratch_mkfs -O ^no-holes >>$seqres.full 2>&1`; `_init_flakey`; `_scratch_mkfs -O no-holes >>$seqres.full 2>&1`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. The dm-flakey helper deliberately drops writes and remounts to force replay of whatever reached the btrfs log tree. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick log prealloc fiemap` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

The pass/fail signal depends on realistic crash semantics from dm-flakey and on metadata journaling being available.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. fstests scratch checking validates filesystem and qgroup consistency after unmount.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/211 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/212 -->
# sources/test-tools/xfstests/tests/btrfs/212

## Purpose

`sources/test-tools/xfstests/tests/btrfs/212` is btrfs fstests case `212`. It targets balance relocation behavior, fault-injection or destructive-device conditions. Source comments describe the scenario as: Test if unmounting a fs with balance canceled can lead to crash. This needs CONFIG_BTRFS_DEBUG compiled, which adds extra unmount time self-test

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto balance dangerous` declares tags `auto balance dangerous`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_scratch`; local shell helpers: `_cleanup()`, `balance_workload()`, `cancel_workload()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `kill $balance_pid &> /dev/null`; `$BTRFS_UTIL_PROG balance cancel $SCRATCH_MNT &> /dev/null`; `rm -f $tmp.*`; `_require_scratch`; `_scratch_mkfs >> $seqres.full`; `_scratch_mount`; `balance_workload()`; `_run_btrfs_balance_start &> /dev/null`; `balance_workload &`; `balance_pid=$!`; `kill $balance_pid`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto balance dangerous` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

It may be slow or disruptive because it reformats scratch storage and may use fault injection or degraded-device mounts.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. Most success is absence of unexpected output, ending with `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/212 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/213 -->
# sources/test-tools/xfstests/tests/btrfs/213

## Purpose

`sources/test-tools/xfstests/tests/btrfs/213` is btrfs fstests case `213`. It targets balance relocation behavior. Source comments describe the scenario as: Test if canceling a running balance can lead to dead looping balance Create enough IO so that we need around 8 seconds to relocate it. Unmount and mount again the fs to clear any cached data and metadata, so that it's less likely balance has already finished when we try to cancel it below. Now balance should take at least $runtime seconds, we can cancel it at $runtime/4 to ensure a success cancel. It's possible that balance has already completed. It's unlikely but often it may happen due to virtualization, caching and other factors, so ignore any error about no balance currently running. Now check if we can finish relocating metadata, which should finish very

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto balance` declares tags `auto balance`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_scratch`, `_require_xfs_io_command pwrite -D`, `_notrun "balance finished before we could cancel it"`; local shell helpers: `_cleanup()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `rm -f $tmp.*`; `_require_scratch`; `_require_xfs_io_command pwrite -D`; `"btrfs: reloc: clear DEAD_RELOC_TREE bit for orphan roots to prevent runaway balance"`; `_scratch_mkfs >> $seqres.full`; `_scratch_mount`; `max_space=$(_get_total_space $SCRATCH_MNT)`; `$TIMEOUT_PROG 8s $XFS_IO_PROG -f -c "pwrite -D -b 1M 0 $max_space" \`; `_scratch_cycle_mount`; `_run_btrfs_balance_start -d --bg "$SCRATCH_MNT"`; `$BTRFS_UTIL_PROG balance cancel "$SCRATCH_MNT" 2>&1 | grep -iq 'not in progress'`; `_notrun "balance finished before we could cancel it"`; `$BTRFS_UTIL_PROG balance start -m "$SCRATCH_MNT" >> $seqres.full`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto balance` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

It may be slow or disruptive because it reformats scratch storage and may use fault injection or degraded-device mounts.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. Most success is absence of unexpected output, ending with `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/213 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/214 -->
# sources/test-tools/xfstests/tests/btrfs/214

## Purpose

`sources/test-tools/xfstests/tests/btrfs/214` is btrfs fstests case `214`. It targets subvolume/snapshot metadata, send/receive stream correctness. Source comments describe the scenario as: Test if the file capabilities aren't lost after full and incremental send Test full send containing a file without capabilities ensure that we don't have capabilities set Test if incremental send brings the newly added capability files should include foo.bar create files on fs1, must contain foo.bar Test full send, checking if the receiving side keeps the capabilities Test incremental send with different owner/group but same capabilities Test capabilities after incremental send with different group and capabilities

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick send snapshot` declares tags `auto quick send snapshot`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_scratch`, `_require_command "$SETCAP_PROG" setcap`, `_require_command "$GETCAP_PROG" getcap`; local shell helpers: `cleanup()`, `check_capabilities()`, `setup()`, `full_nocap_inc_withcap_send()`, `roundtrip_send()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_require_scratch`; `_require_command "$SETCAP_PROG" setcap`; `_require_command "$GETCAP_PROG" getcap`; `FS1="$SCRATCH_MNT/fs1"`; `FS2="$SCRATCH_MNT/fs2"`; `ret=$(_getcap "$file")`; `_scratch_mount`; `$BTRFS_UTIL_PROG subvolume create "$FS1" > /dev/null`; `$BTRFS_UTIL_PROG subvolume create "$FS2" > /dev/null`; `full_nocap_inc_withcap_send()`; `$BTRFS_UTIL_PROG subvolume snapshot -r "$FS1" "$FS1/snap_init" >/dev/null`; `full_nocap_inc_withcap_send`; `roundtrip_send "foo.bar"`; `roundtrip_send "foo.bar foo.bax foo.baz"`; `roundtrip_send "foo1 foo.bar foo3"`; `roundtrip_send "foo1 foo2 foo.bar"`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Subvolume roots, read-only snapshots, deleted snapshot orphans, and directory entries are persisted across remounts. Send streams, fssum manifests, and received snapshots are temporary artifacts used to compare source and reconstructed filesystems. The script records user-visible checksums, listings, device counters, capabilities, or byte dumps as evidence. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick send snapshot` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Send tests can be fragile around inode-number ordering, rename dependencies, clone commands, xattrs, and receiver mount options.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. Linux file capability xattrs must survive the send/receive sequence.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/214 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/215 -->
# sources/test-tools/xfstests/tests/btrfs/215

## Purpose

`sources/test-tools/xfstests/tests/btrfs/215` is btrfs fstests case `215`. It targets checksum, scrub, or read-repair paths. Source comments describe the scenario as: Test that reading corrupted files would correctly increment device status counters. This is fixed by the following linux kernel commit: 814723e0a55a ("btrfs: increment device corruption error in case of checksum error") No data checksums for NOCOW and NODATACOW cases, so can't detect corruption and repair data. Overwriting data is forbidden on a zoned block device We need to ensure a fixed amount of written blocks to trigger a specific number of read errors and we corrupt by writing directly to the device, so skip if compression is enabled. disable freespace inode to ensure file is the first thing in the data

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick read_repair` declares tags `auto quick read_repair`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_scratch`, `_require_btrfs_no_nodatacow`, `_require_btrfs_no_nodatasum`, `_require_non_zoned_device $SCRATCH_DEV`, `_require_no_compress`, `_notrun "this test doesn't support sectorsize $blocksize with page size $pagesize yet"`, `_notrun "bdi link not found"`; local shell helpers: `get_physical()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `$BTRFS_UTIL_PROG inspect-internal dump-tree -t 3 $SCRATCH_DEV | \`; `_require_scratch`; `_require_btrfs_no_nodatacow`; `_require_btrfs_no_nodatasum`; `_require_non_zoned_device $SCRATCH_DEV`; `_scratch_mount $(_btrfs_no_v1_cache_opt)`; `uuid=$(findmnt -n -o UUID "$SCRATCH_MNT")`; `$XFS_IO_PROG -d -f -c "pwrite -S 0xbb -b $filesize 0 $filesize" "$SCRATCH_MNT/foobar" > /dev/null`; `$XFS_IO_PROG -d -c "pwrite -S 0xaa -b $pagesize $physical_extent $((4 * $pagesize))" $SCRATCH_DEV > /dev/null`; `_scratch_mount`; `echo 0 > /sys/fs/btrfs/$uuid/bdi/read_ahead_kb`; `$XFS_IO_PROG -c "pread -b $filesize 0 $filesize" "$SCRATCH_MNT/foobar" > /dev/null 2>&1`; `errs=$($BTRFS_UTIL_PROG device stats $SCRATCH_DEV | $AWK_PROG '/corruption_errs/ { print $2 }')`; `$XFS_IO_PROG -d -c "pread -b $filesize 0 $filesize" "$SCRATCH_MNT/foobar" > /dev/null 2>&1`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. The script records user-visible checksums, listings, device counters, capabilities, or byte dumps as evidence. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick read_repair` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

The main risk is environmental: missing fstests helpers, unsupported btrfs features, or changed userspace output can turn the test into a notrun or golden-output mismatch.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. Most success is absence of unexpected output, ending with `Silence is golden`. `btrfs device stats` counters are inspected for expected readable/corruption accounting.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/215 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/216 -->
# sources/test-tools/xfstests/tests/btrfs/216

## Purpose

`sources/test-tools/xfstests/tests/btrfs/216` is btrfs fstests case `216`. It targets multi-device or RAID volume behavior. Source comments describe the scenario as: Test if the show_devname() returns sprout device instead of seed device. check if the show_devname() returns the sprout device instead of seed device.

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick seed` declares tags `auto quick seed`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_scratch_dev_pool 2`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `"btrfs: don't traverse into the seed devices in show_devname"`; `_require_scratch_dev_pool 2`; `_scratch_dev_pool_get 2`; `seed=$(echo $SCRATCH_DEV_POOL | $AWK_PROG '{print $1}')`; `sprout=$(echo $SCRATCH_DEV_POOL | $AWK_PROG '{print $2}')`; `_mkfs_dev $seed`; `_mount $seed $SCRATCH_MNT >> $seqres.full 2>&1`; `cat /proc/self/mounts | grep $seed >> $seqres.full`; `$BTRFS_UTIL_PROG device add -f $sprout $SCRATCH_MNT >> $seqres.full`; `cat /proc/self/mounts | grep $sprout >> $seqres.full`; `dev=$(grep $SCRATCH_MNT /proc/self/mounts | $AWK_PROG '{print $1}')`; `if [ "$sprout" != "$dev" ]; then`; `echo "Unexpected device: $dev, expected $sprout"`; `_scratch_dev_pool_put`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Device identity, missing-device state, degraded mounts, and balance/repair writes are part of the persistent test surface. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick seed` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Multi-device tests need enough disposable devices and can leave device scans cached if cleanup does not run.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. Most success is absence of unexpected output, ending with `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/216 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/217 -->
# sources/test-tools/xfstests/tests/btrfs/217

## Purpose

`sources/test-tools/xfstests/tests/btrfs/217` is btrfs fstests case `217`. It targets fault-injection or destructive-device conditions. Source comments describe the scenario as: Test if the following workload would cause problem: - fstrim - shrink device - fstrim Create a 5G fs Fstrim to populate the device->alloc_status CHUNK_TRIMMED bits Shrink the fs to 4G, so the existing CHUNK_TRIMMED bits are beyond device boundary Do fstrim again to trigger the bug

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick trim dangerous` declares tags `auto quick trim dangerous`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_scratch_size $((5 * 1024 * 1024)) #kB`, `_require_fstrim`, `_notrun "FSTRIM not supported"`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_require_scratch_size $((5 * 1024 * 1024)) #kB`; `_require_fstrim`; `_scratch_mkfs_sized $((5 * 1024 * 1024 * 1024)) >> $seqres.full`; `_scratch_mount`; `$BTRFS_UTIL_PROG filesystem resize 1:-1G "$SCRATCH_MNT" >> $seqres.full`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick trim dangerous` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

It may be slow or disruptive because it reformats scratch storage and may use fault injection or degraded-device mounts.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. Most success is absence of unexpected output, ending with `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/217 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/218 -->
# sources/test-tools/xfstests/tests/btrfs/218

## Purpose

`sources/test-tools/xfstests/tests/btrfs/218` is btrfs fstests case `218`. It targets multi-device or RAID volume behavior. Source comments describe the scenario as: Make a seed device, add a sprout to it, and then make sure we can still read the device stats for both devices after we remount with the new sprout device. Create the seed device Mount the seed device and add the rw device Now remount, validate the device stats do not fail

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick volume` declares tags `auto quick volume`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`. sourced helpers: `./common/preamble`, `./common/filter`, `./common/filter.btrfs`; requirements: `_require_test`, `_require_scratch_dev_pool 2`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `"btrfs: init device stats for seed devices"`; `_require_scratch_dev_pool 2`; `_scratch_dev_pool_get 2`; `dev_seed=$(echo $SCRATCH_DEV_POOL | $AWK_PROG '{print $1}')`; `dev_sprout=$(echo $SCRATCH_DEV_POOL | $AWK_PROG '{print $2}')`; `_mkfs_dev $dev_seed`; `_mount $dev_seed $SCRATCH_MNT`; `$XFS_IO_PROG -f -d -c "pwrite -S 0xab 0 1M" $SCRATCH_MNT/foo > /dev/null`; `$BTRFS_UTIL_PROG filesystem show -m $SCRATCH_MNT | \`; `_filter_btrfs_filesystem_show`; `_scratch_unmount`; `_mount -o ro $dev_seed $SCRATCH_MNT`; `_btrfs device add -f $dev_sprout $SCRATCH_MNT >> $seqres.full`; `$BTRFS_UTIL_PROG device stats $SCRATCH_MNT | _filter_scratch_pool`; `_mount $dev_sprout $SCRATCH_MNT`; `_scratch_dev_pool_put`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Device identity, missing-device state, degraded mounts, and balance/repair writes are part of the persistent test surface. The script records user-visible checksums, listings, device counters, capabilities, or byte dumps as evidence. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick volume` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Multi-device tests need enough disposable devices and can leave device scans cached if cleanup does not run.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. `btrfs device stats` counters are inspected for expected readable/corruption accounting.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/218 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/219 -->
# sources/test-tools/xfstests/tests/btrfs/219

## Purpose

`sources/test-tools/xfstests/tests/btrfs/219` is btrfs fstests case `219`. It targets multi-device or RAID volume behavior. Source comments describe the scenario as: Test a variety of stale device usecases.  We cache the device and generation to make sure we do not allow stale devices, which can end up with some wonky behavior for loop back devices. And, added a few other test cases so it's clear what we expect to happen currently. The variables are set before the test case can fail. Normal single device case, should pass just fine Now mount the new version again to get the higher generation cached, umount and try to mount the old version.  Mount the new version again just for good measure.

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick volume` declares tags `auto quick volume`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_test`, `_require_loop`, `_require_btrfs_fs_sysfs`, `_require_btrfs_forget_or_module_loadable`; local shell helpers: `_cleanup()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `rm -f $tmp.*`; `$UMOUNT_PROG ${loop_mnt1} &> /dev/null`; `$UMOUNT_PROG ${loop_mnt2} &> /dev/null`; `rm -rf $loop_mnt1`; `rm -rf $loop_mnt2`; `[ ! -z $loop_dev1 ] && _destroy_loop_device $loop_dev1`; `[ ! -z $loop_dev1 ] && _destroy_loop_device $loop_dev2`; `_btrfs_rescan_devices`; `loop_mnt1=$TEST_DIR/$seq/mnt1`; `loop_mnt2=$TEST_DIR/$seq/mnt2`; `loop_dev1=""`; `$UMOUNT_PROG $loop_mnt2`; `_fail "Failed to mount the third time"`; `if ! _has_btrfs_sysfs_feature_attr temp_fsid; then`; `_mount $loop_dev2 $loop_mnt2 > /dev/null 2>&1 && \`; `_fail "We were allowed to mount when we should have failed"`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick volume` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Multi-device tests need enough disposable devices and can leave device scans cached if cleanup does not run.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. Most success is absence of unexpected output, ending with `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/219 -->
