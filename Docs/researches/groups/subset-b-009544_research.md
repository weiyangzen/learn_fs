# Research Group subset-b-009544

This grouped report covers selected xfstests ext4, f2fs, and generic shell tests. Each section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/061 -->

# sources/test-tools/xfstests/tests/ext4/061

## Purpose

This test does a lot of parallel RWF_ATOMIC IO on a preallocated file to stress the write and end-io unwritten conversion code paths. We brute force this for all possible blocksize and clustersizes and after each iteration we ensure the data was not torn or corrupted using fio crc verification. Note that in this test we use overlapping atomic writes of same io size. Although RWF_ATOMIC does not generally promise serialization of racing writes, the test relies on equal-sized overlapping atomic writes to stress ext4 and block-layer no-tear behavior under NVMe/SCSI-style power-fail atomicity.

## Important APIs, Types, and Functions

This is a bash xfstests case in the `ext4` suite. The harness entry and tags are `_begin_fstest auto rw stress atomicwrites`. Important local functions are `create_fio_aw_config`, `create_fio_configs`, `create_fio_verify_config`, `run_test`, `run_test_one`. Key xfstests/helper interfaces include `_require_scratch_write_atomic` (requires filesystem atomic-write capability), `_require_fio_atomic_writes` (checks fio atomic write support), `_scratch_mkfs_ext4` (formats scratch specifically as ext4), `_try_scratch_mount` (attempts to mount scratch and lets the test decide skip/fail behavior), `_scratch_unmount` (unmounts scratch to force persistence checks). External or helper commands visible in the body include `touch`. Significant variables include `FIO_LOAD`, `MKFS_OPTIONS`, `SIZE`, `bs`, `size`, `status`.

## Control Flow

The script sources `./common/preamble`, `./common/atomicwrites`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_require_scratch_write_atomic`; `_require_fio_atomic_writes`; `_require_aiodio`; `_scratch_mkfs > /dev/null 2>&1 || \`; `_notrun "mkfs failed"`; `_try_scratch_mount || \`; `_notrun "mount failed"`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state, fio verification state for direct/atomic I/O. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_aiodio`, `_require_fio`, `_require_fio_atomic_writes`, `_require_scratch_write_atomic`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/atomicwrites` and with suite-specific filesystem features selected by the `ext4` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent, stress-tool behavior and kernel timing can expose nondeterminism. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: prints `Silence is golden` after all checks pass; logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/061 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/062 -->

# sources/test-tools/xfstests/tests/ext4/062

## Purpose

This test does a parallel RWF_ATOMIC IO on a multiple truncated files in a small FS. The idea is to stress ext4 allocator to ensure we are able to handle low space scenarios correctly with atomic writes.. We brute force this for all possible blocksize and clustersizes and after each iteration we ensure the data was not torn or corrupted using fio crc verification. Note that in this test we use overlapping atomic writes of same io size. Although serializing racing writes is not guaranteed for RWF_ATOMIC, NVMe and.

## Important APIs, Types, and Functions

This is a bash xfstests case in the `ext4` suite. The harness entry and tags are `_begin_fstest auto rw stress atomicwrites`. Important local functions are `create_fio_aw_config`, `create_fio_configs`, `create_fio_verify_config`, `run_test`, `run_test_one`. Key xfstests/helper interfaces include `_require_scratch_write_atomic` (requires filesystem atomic-write capability), `_require_fio_atomic_writes` (checks fio atomic write support), `_scratch_mkfs_sized` (formats a scratch image/device of a requested size), `_try_scratch_mount` (attempts to mount scratch and lets the test decide skip/fail behavior), `_scratch_unmount` (unmounts scratch to force persistence checks). External or helper commands visible in the body include `touch`. Significant variables include `FIO_LOAD`, `FSSIZE`, `MKFS_OPTIONS`, `bs`, `size`, `status`.

## Control Flow

The script sources `./common/preamble`, `./common/atomicwrites`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_require_scratch_write_atomic`; `_require_fio_atomic_writes`; `_require_aiodio`; `_scratch_mkfs > /dev/null 2>&1 || \`; `_notrun "mkfs failed"`; `_try_scratch_mount || \`; `_notrun "mount failed"`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state, fio verification state for direct/atomic I/O. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_aiodio`, `_require_fio`, `_require_fio_atomic_writes`, `_require_scratch_write_atomic`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/atomicwrites` and with suite-specific filesystem features selected by the `ext4` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent, stress-tool behavior and kernel timing can expose nondeterminism. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: prints `Silence is golden` after all checks pass; logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/062 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/063 -->

# sources/test-tools/xfstests/tests/ext4/063

## Purpose

xfstests shell test ext4/063. Its tags are auto, atomicwrites, so it participates in the xfstests harness for filesystem behavior regression coverage.

## Important APIs, Types, and Functions

This is a bash xfstests case in the `ext4` suite. The harness entry and tags are `_begin_fstest auto atomicwrites`. Important local functions are `prep`. Key xfstests/helper interfaces include `_scratch_cycle_mount` (unmounts and remounts scratch to test persisted metadata), `_require_command` (checks availability of an external command), `_scratch_mount` (mounts the scratch filesystem), `_scratch_mkfs` (formats the scratch filesystem). External or helper commands visible in the body include `debugfs`, `od`, `sync`, `tail`, `touch`. Significant variables include `status`, `testfile`.

## Control Flow

The script sources `./common/preamble`, `./common/atomicwrites`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_require_scratch_write_atomic_multi_fsblock`; `_require_atomic_write_test_commands`; `_require_command "$DEBUGFS_PROG" debugfs`; `local bs=\`_get_block_size $SCRATCH_MNT\``; `for i in $(seq 0 $entries_per_blk)`; `$XFS_IO_PROG -fc "pwrite -b $bs $((i * 2 * bs)) $bs" $testfile > /dev/null`; `sync $testfile`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state, fio verification state for direct/atomic I/O. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_atomic_write_test_commands`, `_require_command`, `_require_scratch_write_atomic_multi_fsblock`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/atomicwrites` and with suite-specific filesystem features selected by the `ext4` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: prints `Silence is golden` after all checks pass; logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/063 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/271 -->

# sources/test-tools/xfstests/tests/ext4/271

## Purpose

xfstests shell test ext4/271. Its tags are auto, rw, quick, so it participates in the xfstests harness for filesystem behavior regression coverage.

## Important APIs, Types, and Functions

This is a bash xfstests case in the `ext4` suite. The harness entry and tags are `_begin_fstest auto rw quick`. No local shell functions are declared. Key xfstests/helper interfaces include `_scratch_mkfs_sized` (formats a scratch image/device of a requested size), `_scratch_unmount` (unmounts scratch to force persistence checks), `_require_scratch` (requires a disposable scratch filesystem), `_scratch_mount` (mounts the scratch filesystem). External or helper commands visible in the body include `dd`, `touch`. Significant variables include `status`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_exclude_fs ext2`; `_exclude_fs ext3`; `_require_scratch`; `_exclude_scratch_mount_option "data" "commit" "journal_checksum" \`; `_scratch_mkfs_sized $((128 * 1024 * 1024)) >> $seqres.full 2>&1`; `_scratch_mount -onoload`; `touch $SCRATCH_MNT/file`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_scratch`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter` and with suite-specific filesystem features selected by the `ext4` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/271 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/301 -->

# sources/test-tools/xfstests/tests/ext4/301

## Purpose

This ext4 defragmentation stress test runs e4defrag through fio while another fio job performs direct I/O with crc verification against the same file. It targets data integrity during extent movement under concurrent direct writes.

## Important APIs, Types, and Functions

This is a bash xfstests case in the `ext4` suite. The harness entry and tags are `_begin_fstest aio auto ioctl rw stress defrag`. Important local functions are `_workout`. Key xfstests/helper interfaces include `_scratch_unmount` (unmounts scratch to force persistence checks), `_require_scratch` (requires a disposable scratch filesystem), `_require_odirect` (requires O_DIRECT support), `_require_defrag` (requires filesystem defrag support), `_scratch_mount` (mounts the scratch filesystem). External or helper commands visible in the body include `blockdev`, `defrag`. Significant variables include `BLK_DEV_SIZE`, `FILE_SIZE`, `NUM_JOBS`, `bs`, `size`, `status`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, `./common/defrag`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_exclude_fs ext2`; `_exclude_fs ext3`; `_require_scratch`; `_require_defrag`; `_require_odirect`; `BLK_DEV_SIZE=\`blockdev --getsz $SCRATCH_DEV\``; `_workout()`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state, fio verification state for direct/atomic I/O. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_defrag`, `_require_fio`, `_require_odirect`, `_require_scratch`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter`, `./common/defrag` and with suite-specific filesystem features selected by the `ext4` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent, stress-tool behavior and kernel timing can expose nondeterminism. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/301 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/302 -->

# sources/test-tools/xfstests/tests/ext4/302

## Purpose

This ext4 defragmentation stress test defragments a buffered-I/O target file while a separate direct-I/O fio job writes the donor file and a verifier job checks the target. It stresses donor-file interaction, EBUSY handling, and data verification during e4defrag.

## Important APIs, Types, and Functions

This is a bash xfstests case in the `ext4` suite. The harness entry and tags are `_begin_fstest aio auto ioctl rw stress defrag`. Important local functions are `_workout`. Key xfstests/helper interfaces include `_scratch_unmount` (unmounts scratch to force persistence checks), `_require_scratch` (requires a disposable scratch filesystem), `_require_odirect` (requires O_DIRECT support), `_require_defrag` (requires filesystem defrag support), `_scratch_mount` (mounts the scratch filesystem). External or helper commands visible in the body include `blockdev`, `defrag`. Significant variables include `BLK_DEV_SIZE`, `FILE_SIZE`, `bs`, `size`, `status`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, `./common/defrag`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_exclude_fs ext2`; `_exclude_fs ext3`; `_require_scratch`; `_require_defrag`; `_require_odirect`; `BLK_DEV_SIZE=\`blockdev --getsz $SCRATCH_DEV\``; `_workout()`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state, fio verification state for direct/atomic I/O. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_defrag`, `_require_fio`, `_require_odirect`, `_require_scratch`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter`, `./common/defrag` and with suite-specific filesystem features selected by the `ext4` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent, stress-tool behavior and kernel timing can expose nondeterminism. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/302 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/303 -->

# sources/test-tools/xfstests/tests/ext4/303

## Purpose

This ext4 defragmentation stress test runs two defrag jobs that share a donor file while fio verifier jobs write and verify two target files. It exercises shared-donor coordination and data integrity across direct and buffered I/O paths.

## Important APIs, Types, and Functions

This is a bash xfstests case in the `ext4` suite. The harness entry and tags are `_begin_fstest aio auto ioctl rw stress defrag`. Important local functions are `_workout`. Key xfstests/helper interfaces include `_scratch_unmount` (unmounts scratch to force persistence checks), `_require_scratch` (requires a disposable scratch filesystem), `_require_odirect` (requires O_DIRECT support), `_require_defrag` (requires filesystem defrag support), `_scratch_mount` (mounts the scratch filesystem). External or helper commands visible in the body include `blockdev`, `defrag`. Significant variables include `BLK_DEV_SIZE`, `FILE_SIZE`, `bs`, `size`, `status`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, `./common/defrag`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_exclude_fs ext2`; `_exclude_fs ext3`; `_require_scratch`; `_require_defrag`; `_require_odirect`; `BLK_DEV_SIZE=\`blockdev --getsz $SCRATCH_DEV\``; `_workout()`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state, fio verification state for direct/atomic I/O. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_defrag`, `_require_fio`, `_require_odirect`, `_require_scratch`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter`, `./common/defrag` and with suite-specific filesystem features selected by the `ext4` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent, stress-tool behavior and kernel timing can expose nondeterminism. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/303 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/304 -->

# sources/test-tools/xfstests/tests/ext4/304

## Purpose

This ext4 defragmentation stress test runs random-position inplace e4defrag activity, forcing allocation and freeing inside defrag operations while a direct-I/O verifier writes crc-protected data. It pressures the block allocator and extent-move paths.

## Important APIs, Types, and Functions

This is a bash xfstests case in the `ext4` suite. The harness entry and tags are `_begin_fstest aio auto ioctl rw stress defrag`. Important local functions are `_workout`. Key xfstests/helper interfaces include `_scratch_unmount` (unmounts scratch to force persistence checks), `_require_scratch` (requires a disposable scratch filesystem), `_require_odirect` (requires O_DIRECT support), `_require_defrag` (requires filesystem defrag support), `_scratch_mount` (mounts the scratch filesystem). External or helper commands visible in the body include `blockdev`, `defrag`. Significant variables include `BLK_DEV_SIZE`, `FILE_SIZE`, `bs`, `size`, `status`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, `./common/defrag`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_exclude_fs ext2`; `_exclude_fs ext3`; `_require_scratch`; `_require_defrag`; `_require_odirect`; `BLK_DEV_SIZE=\`blockdev --getsz $SCRATCH_DEV\``; `_workout()`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state, fio verification state for direct/atomic I/O. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_defrag`, `_require_fio`, `_require_odirect`, `_require_scratch`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter`, `./common/defrag` and with suite-specific filesystem features selected by the `ext4` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent, stress-tool behavior and kernel timing can expose nondeterminism. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/304 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/305 -->

# sources/test-tools/xfstests/tests/ext4/305

## Purpose

Regression test for commit: 9559996 ext4: remove mb_groups before tearing down the buddy_cache

## Important APIs, Types, and Functions

This is a bash xfstests case in the `ext4` suite. The harness entry and tags are `_begin_fstest auto`. Important local functions are `_cleanup`. Key xfstests/helper interfaces include `_try_scratch_mount` (attempts to mount scratch and lets the test decide skip/fail behavior), `_scratch_unmount` (unmounts scratch to force persistence checks), `_require_scratch` (requires a disposable scratch filesystem), `_scratch_mkfs` (formats the scratch filesystem). No standalone external commands were extracted beyond shell builtins and xfstests helper calls.. Significant variables include `DEV_BASENAME`, `PIDS`, `status`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_cleanup()`; `_exclude_fs ext2`; `_exclude_fs ext3`; `_require_scratch`; `echo "Silence is golden"`; `DEV_BASENAME=$(_short_dev $SCRATCH_DEV)`; `echo "Start test on device $SCRATCH_DEV, basename $DEV_BASENAME" >$seqres.full`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_scratch`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter` and with suite-specific filesystem features selected by the `ext4` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: prints `Silence is golden` after all checks pass; logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/305 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/306 -->

# sources/test-tools/xfstests/tests/ext4/306

## Purpose

Test that blocks are available to non-extent files after a resize2fs Regression test for commit: c5c72d8 ext4: fix online resizing for ext3-compat file systems

## Important APIs, Types, and Functions

This is a bash xfstests case in the `ext4` suite. The harness entry and tags are `_begin_fstest auto rw resize quick`. Important local functions are `_cleanup`. Key xfstests/helper interfaces include `_scratch_unmount` (unmounts scratch to force persistence checks), `_require_scratch` (requires a disposable scratch filesystem), `_require_command` (checks availability of an external command), `_scratch_mount` (mounts the scratch filesystem), `_filter_xfs_io` (normalizes xfs_io output). External or helper commands visible in the body include `fill`, `grep`, `resize2fs`. Significant variables include `PIDS`, `status`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_cleanup()`; `_scratch_unmount`; `_exclude_fs ext2`; `_exclude_fs ext3`; `_require_scratch`; `_require_command "$RESIZE2FS_PROG" resize2fs`; `if grep -q 64bit /etc/mke2fs.conf ; then`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state, fscrypt keys, policies, nonces, and ciphertext blocks. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_command`, `_require_scratch`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter` and with suite-specific filesystem features selected by the `ext4` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent, encryption mode, nonce, and block-size assumptions must match kernel fscrypt behavior. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/306 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/307 -->

# sources/test-tools/xfstests/tests/ext4/307

## Purpose

This ext4 test checks data integrity during defrag compaction by generating files with fsstress, recording md5 checksums, allocating a donor file, running e4compact, and validating every checksum after compacting.

## Important APIs, Types, and Functions

This is a bash xfstests case in the `ext4` suite. The harness entry and tags are `_begin_fstest auto ioctl rw defrag prealloc`. Important local functions are `_workout`. Key xfstests/helper interfaces include `_require_xfs_io_command` (checks xfs_io subcommand support), `_scratch_mkfs_sized` (formats a scratch image/device of a requested size), `_require_scratch` (requires a disposable scratch filesystem), `_require_defrag` (requires filesystem defrag support), `_scratch_mount` (mounts the scratch filesystem). External or helper commands visible in the body include `awk`, `defrag`, `find`, `md5sum`. Significant variables include `FSSTRESS_AVOID`, `status`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, `./common/defrag`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_workout()`; `echo ""`; `echo "Run fsstress"`; `out=$SCRATCH_MNT/fsstress.$$`; `echo "fsstress $args" >> $seqres.full`; `_run_fsstress $args`; `echo "Allocate donor file"`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_defrag`, `_require_scratch`, `_require_xfs_io_command`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter`, `./common/defrag` and with suite-specific filesystem features selected by the `ext4` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent, stress-tool behavior and kernel timing can expose nondeterminism. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: uses checksums to detect data changes; logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/307 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/308 -->

# sources/test-tools/xfstests/tests/ext4/308

## Purpose

This ext4 test checks both data integrity and layout stability during e4compact. It creates fragmented preallocated files, records fiemap layout and md5 sums, runs compacting twice, and expects the second EXT4_IOC_MOVE_EXT pass to restore the original layout.

## Important APIs, Types, and Functions

This is a bash xfstests case in the `ext4` suite. The harness entry and tags are `_begin_fstest auto ioctl rw prealloc quick defrag fiemap`. Important local functions are `_workout`. Key xfstests/helper interfaces include `_require_xfs_io_command` (checks xfs_io subcommand support), `_require_scratch` (requires a disposable scratch filesystem), `_filter_scratch` (normalizes scratch paths in stdout), `_require_defrag` (requires filesystem defrag support), `_scratch_mount` (mounts the scratch filesystem). External or helper commands visible in the body include `defrag`, `diff`, `fiemap`, `ls`, `md5sum`. Significant variables include `PIDS`, `status`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, `./common/defrag`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_require_scratch`; `_require_defrag`; `_require_xfs_io_command "falloc"`; `_workout()`; `echo "Create file with $nr * 2 fragments"`; `for ((i=0;i<nr;i++))`; `$XFS_IO_PROG -f -c "falloc $((409600*i)) 4k"  \`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_defrag`, `_require_scratch`, `_require_xfs_io_command`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter`, `./common/defrag` and with suite-specific filesystem features selected by the `ext4` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent, extent layout assumptions can vary by filesystem feature and kernel version. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: uses byte-for-byte comparison of generated and expected data; uses checksums to detect data changes; logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/308 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/Makefile -->

# sources/test-tools/xfstests/tests/ext4/Makefile

## Purpose

This Makefile is the install/build manifest for the xfstests `ext4` test directory. It delegates to the shared `include/builddefs` and `$(BUILDRULES)` infrastructure and declares which numbered shell tests and companion files are part of this suite.

## Important APIs, Types, and Functions

The primary interface is GNU make metadata: `TOPDIR`, `include $(TOPDIR)/include/builddefs`, `TARGET_DIR`, `INSTALL_DIR`, `INSTALL_MODE`, `TESTS`, `MKFS_CONFIGS`, and `default: depend`. The `include $(BUILDRULES)` line supplies the common xfstests targets for dependency generation and installation.

## Control Flow

Make evaluates the top-level path variables, includes global build definitions, sets the destination directory to `$(PKG_LIB_DIR)/tests/ext4`, lists tests/configuration payloads, and lets the shared build rules implement `default`, `depend`, and install behavior. The file does not run filesystem tests itself; it makes the scripts available to the harness.

## State and Persistence Behavior

Persistent output is limited to build/install artifacts produced by the shared Make rules. The manifest itself records 4 numbered test references; it has no runtime scratch-device state.

## Dependencies and Integration Points

It depends on the repository-level `include/builddefs` and `$(BUILDRULES)`. It integrates with xfstests packaging by installing the declared scripts under the suite-specific tests directory.

## Risks and Edge Cases

The main risk is manifest drift: adding or removing a test script without updating `TESTS` or `MKFS_CONFIGS` can prevent the harness from installing or discovering the intended file. Shared Make variables must be available from the top-level xfstests build environment.

## Test Signals

Useful signals are successful `make` dependency/install runs and the presence of every declared test/config in the installed `ext4` tests directory.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/f2fs/001 -->

# sources/test-tools/xfstests/tests/f2fs/001

## Purpose

Test inline_data behaviors when filesystem is full. The inline_data feature was introduced in ext4 and f2fs as follows. ext4 : http://lwn.net/Articles/468678/ f2fs : http://lwn.net/Articles/573408/ The basic idea is embedding small-sized file's data into relatively large inode space. In ext4, up to 132 bytes of data can be stored in 256 bytes-sized inode. In f2fs, up to 3.4KB of data can be embedded into 4KB-sized inode block.

## Important APIs, Types, and Functions

This is a bash xfstests case in the `f2fs` suite. The harness entry and tags are `_begin_fstest auto quick rw prealloc`. No local shell functions are declared. Key xfstests/helper interfaces include `_require_xfs_io_command` (checks xfs_io subcommand support), `_scratch_cycle_mount` (unmounts and remounts scratch to test persisted metadata), `_scratch_mkfs_sized` (formats a scratch image/device of a requested size), `_require_scratch` (requires a disposable scratch filesystem), `_scratch_mount` (mounts the scratch filesystem). External or helper commands visible in the body include `rm`. Significant variables include `status`, `testfile`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_require_scratch`; `_require_xfs_io_command "falloc"`; `testfile=$SCRATCH_MNT/testfile`; `dummyfile=$SCRATCH_MNT/dummyfile`; `_scratch_mkfs_sized $((4 * 1024 * 1024 * 1024)) > /dev/null 2>&1`; `_scratch_mount`; `echo "==== create small file ===="`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_scratch`, `_require_xfs_io_command`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter` and with suite-specific filesystem features selected by the `f2fs` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: passes when required commands complete and the xfstests golden output matches. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/f2fs/001 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/f2fs/002 -->

# sources/test-tools/xfstests/tests/f2fs/002

## Purpose

Test that when a file is both compressed and encrypted, the encryption is done correctly. I.e., the correct ciphertext is written to disk. f2fs compression behaves as follows: the original data of a compressed file is divided into equal-sized clusters. The cluster size is configurable, but it must be a power-of-2 multiple of the filesystem block size. If the file size isn't a multiple of the cluster size, then the final cluster is "partial" and holds the remainder modulo the cluster size. Each cluster is compressed independently, encrypted after compression, read back from raw disk blocks, decrypted with fscrypt test tooling, decompressed as LZ4 data, and compared to the original bytes.

## Important APIs, Types, and Functions

This is a bash xfstests case in the `f2fs` suite. The harness entry and tags are `_begin_fstest auto quick rw encrypt compress fiemap`. Important local functions are `decompress_cluster`, `decrypt_blocks`. Key xfstests/helper interfaces include `_require_scratch_f2fs_compression` (requires f2fs compression support), `_require_scratch_encryption` (requires fscrypt support on scratch), `_get_ciphertext_block_list` (derives raw encrypted block locations), `_require_xfs_io_command` (checks xfs_io subcommand support), `_dump_ciphertext_blocks` (reads raw ciphertext blocks from the block device). External or helper commands visible in the body include `awk`, `chattr`, `cmp`, `cp`, `dd`, `fiemap`, `head`, `lz4`, `mkdir`, `od`, and others. Significant variables include `TEST_RAW_KEY_HEX`, `block_size`, `dir`, `file`, `status`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, `./common/encrypt`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_require_scratch_encryption -v 2`; `_require_scratch_f2fs_compression lz4`; `_require_command "$CHATTR_PROG" chattr`; `_require_get_encryption_nonce_support`; `_require_xfs_io_command "fiemap" # for _get_ciphertext_block_list()`; `_require_test_program "fscrypt-crypt-util"`; `_require_command "$LZ4_PROG" lz4`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state, fscrypt keys, policies, nonces, and ciphertext blocks, compressed extents or clusters. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_command`, `_require_get_encryption_nonce_support`, `_require_scratch_encryption`, `_require_scratch_f2fs_compression`, `_require_test_program`, `_require_xfs_io_command`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter`, `./common/encrypt` and with suite-specific filesystem features selected by the `f2fs` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, extent layout assumptions can vary by filesystem feature and kernel version, encryption mode, nonce, and block-size assumptions must match kernel fscrypt behavior, compression heuristics may change block layout while preserving user data. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: uses byte-for-byte comparison of generated and expected data; logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/f2fs/002 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/f2fs/003 -->

# sources/test-tools/xfstests/tests/f2fs/003

## Purpose

Test that we will simulate sqlite atomic write logic w/ below steps: 1. create a regular file, and initialize it w/ 0xff data 2. start transaction (via F2FS_IOC_START_ATOMIC_WRITE) on it 3. write transaction data 4. trigger foreground GC to migrate data block of the file 5. commit and end the transaction (via F2FS_IOC_COMMIT_ATOMIC_WRITE) 6. check consistency of transaction w/ in-memory and on-disk data This is a regression test to check handling of race condition in between atomic_write and GC.

## Important APIs, Types, and Functions

This is a bash xfstests case in the `f2fs` suite. The harness entry and tags are `_begin_fstest auto quick`. Important local functions are `_cleanup`. Key xfstests/helper interfaces include `_require_xfs_io_command` (checks xfs_io subcommand support), `_require_scratch` (requires a disposable scratch filesystem), `_scratch_mount` (mounts the scratch filesystem), `_scratch_mkfs` (formats the scratch filesystem). External or helper commands visible in the body include `rm`, `sync`. Significant variables include `status`.

## Control Flow

The script sources `./common/preamble`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_cleanup()`; `rm -r -f $tmp.*`; `_fixed_by_kernel_commit b40a2b003709 \`; `_require_scratch`; `_require_xfs_io_command "fpunch"`; `_scratch_mkfs >> $seqres.full`; `_scratch_mount >> $seqres.full`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state, fio verification state for direct/atomic I/O. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_scratch`, `_require_xfs_io_command`. The test integrates with common xfstests libraries through `./common/preamble` and with suite-specific filesystem features selected by the `f2fs` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/f2fs/003 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/f2fs/004 -->

# sources/test-tools/xfstests/tests/f2fs/004

## Purpose

Test that we will simulate race case in between sqlite atomic write and direct IO w/ below steps: 1. create a regular file, and initialize it w/ 0xff data 2. start transaction (via F2FS_IOC_START_ATOMIC_WRITE) on it 3. write transaction data 4. trigger direct read/write IO to check whether it fails or not 5. commit and end the transaction (via F2FS_IOC_COMMIT_ATOMIC_WRITE) This is a regression test to check handling of race condition in between atomic_write and direct IO.

## Important APIs, Types, and Functions

This is a bash xfstests case in the `f2fs` suite. The harness entry and tags are `_begin_fstest auto quick punch`. Important local functions are `_cleanup`. Key xfstests/helper interfaces include `_require_scratch` (requires a disposable scratch filesystem), `_require_odirect` (requires O_DIRECT support), `_scratch_mount` (mounts the scratch filesystem), `_scratch_mkfs` (formats the scratch filesystem). External or helper commands visible in the body include `rm`, `touch`. Significant variables include `status`.

## Control Flow

The script sources `./common/preamble`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_cleanup()`; `rm -r -f $tmp.*`; `_fixed_by_kernel_commit b2c160f4f3cf \`; `_require_scratch`; `_require_odirect`; `_scratch_mkfs >> $seqres.full`; `_scratch_mount >> $seqres.full`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state, fio verification state for direct/atomic I/O. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_odirect`, `_require_scratch`. The test integrates with common xfstests libraries through `./common/preamble` and with suite-specific filesystem features selected by the `f2fs` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/f2fs/004 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/f2fs/005 -->

# sources/test-tools/xfstests/tests/f2fs/005

## Purpose

This is a regression test to check whether f2fs handles dirty inode correctly when checkpoint is disabled, it may hang umount before the bug is fixed.

## Important APIs, Types, and Functions

This is a bash xfstests case in the `f2fs` suite. The harness entry and tags are `_begin_fstest auto quick`. No local shell functions are declared. Key xfstests/helper interfaces include `_scratch_mkfs_sized` (formats a scratch image/device of a requested size), `_scratch_unmount` (unmounts scratch to force persistence checks), `_require_scratch` (requires a disposable scratch filesystem), `_scratch_mount` (mounts the scratch filesystem). External or helper commands visible in the body include `dd`, `mkdir`, `mv`, `sync`, `touch`. Significant variables include `status`, `testfile`.

## Control Flow

The script sources `./common/preamble`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_fixed_by_kernel_commit d5c367ef8287 \`; `_require_scratch`; `_scratch_mkfs_sized $((1024*1024*50)) >> $seqres.full`; `_scratch_mount -o mode=lfs,checkpoint=disable:10%,noinline_dentry >> $seqres.full`; `testfile=$SCRATCH_MNT/testfile`; `tmpfile=$SCRATCH_MNT/tmpfile`; `tmpdir=$SCRATCH_MNT/tmpdir`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_scratch`. The test integrates with common xfstests libraries through `./common/preamble` and with suite-specific filesystem features selected by the `f2fs` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: prints `Silence is golden` after all checks pass; logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/f2fs/005 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/f2fs/006 -->

# sources/test-tools/xfstests/tests/f2fs/006

## Purpose

This is a regression test to check whether f2fs handles dirty data correctly when checkpoint is disabled, if lfs mode is on, it will trigger OPU for all overwritten data, this will cost free segments, so f2fs must account overwritten data as OPU data when calculating free space, otherwise, it may run out of free segments in f2fs' allocation function. If kernel config CONFIG_F2FS_CHECK_FS is on, it will cause system panic, otherwise, dd may encounter I/O error.

## Important APIs, Types, and Functions

This is a bash xfstests case in the `f2fs` suite. The harness entry and tags are `_begin_fstest auto quick`. No local shell functions are declared. Key xfstests/helper interfaces include `_scratch_mkfs_sized` (formats a scratch image/device of a requested size), `_require_scratch` (requires a disposable scratch filesystem), `_scratch_mount` (mounts the scratch filesystem). External or helper commands visible in the body include `dd`. Significant variables include `status`, `testfile`.

## Control Flow

The script sources `./common/preamble`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_fixed_by_kernel_commit 1acd73edbbfe \`; `_require_scratch`; `_scratch_mkfs_sized $((1024*1024*100)) >> $seqres.full`; `_scratch_mount -o mode=lfs,checkpoint=disable:10%,noinline_dentry >> $seqres.full`; `testfile=$SCRATCH_MNT/testfile`; `dd if=/dev/zero of=$testfile bs=1M count=50 2>/dev/null`; `dd if=/dev/zero of=$testfile bs=1M count=50 conv=notrunc conv=fsync >>$seqres.full 2>&1`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_scratch`. The test integrates with common xfstests libraries through `./common/preamble` and with suite-specific filesystem features selected by the `f2fs` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: prints `Silence is golden` after all checks pass; logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/f2fs/006 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/f2fs/007 -->

# sources/test-tools/xfstests/tests/f2fs/007

## Purpose

This is a regression test to check whether compressed metadata can become inconsistent after file compression, reservation releasement, and decompression.

## Important APIs, Types, and Functions

This is a bash xfstests case in the `f2fs` suite. The harness entry and tags are `_begin_fstest auto quick rw compress`. No local shell functions are declared. Key xfstests/helper interfaces include `_check_scratch_fs` (runs scratch filesystem consistency checking), `_scratch_unmount` (unmounts scratch to force persistence checks), `_require_scratch` (requires a disposable scratch filesystem), `_scratch_mount` (mounts the scratch filesystem), `_scratch_mkfs` (formats the scratch filesystem). External or helper commands visible in the body include `fio`. Significant variables include `bs`, `status`, `testfile`.

## Control Flow

The script sources `./common/preamble`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_fixed_by_kernel_commit 26413ce18e85 \`; `_require_scratch`; `testfile_prefix=$SCRATCH_MNT/testfile`; `_require_fio $fio_config`; `_scratch_mkfs "-f -O extra_attr,compression" >> $seqres.full || _fail "mkfs failed"`; `_scratch_mount "-o compress_mode=user,compress_extension=*" >> $seqres.full`; `echo -e "Run fio to initialize file w/ specified compress ratio" >> $seqres.full`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state, compressed extents or clusters, fio verification state for direct/atomic I/O. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_fio`, `_require_scratch`. The test integrates with common xfstests libraries through `./common/preamble` and with suite-specific filesystem features selected by the `f2fs` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, stress-tool behavior and kernel timing can expose nondeterminism, compression heuristics may change block layout while preserving user data. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: runs filesystem consistency checking; logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/f2fs/007 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/f2fs/008 -->

# sources/test-tools/xfstests/tests/f2fs/008

## Purpose

This is a regression test to check whether f2fs can handle discard correctly once underlying lvm device changes to not support discard after user creates snapshot on it.

## Important APIs, Types, and Functions

This is a bash xfstests case in the `f2fs` suite. The harness entry and tags are `_begin_fstest auto quick rw`. Important local functions are `_cleanup`. Key xfstests/helper interfaces include `_require_command` (checks availability of an external command). External or helper commands visible in the body include `dd`, `rm`, `sync`. Significant variables include `status`, `testfile`.

## Control Flow

The script sources `./common/preamble`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_fixed_by_kernel_commit bc8aeb04fd80 \`; `_require_scratch_nolvm`; `_require_block_device $SCRATCH_DEV`; `_require_command "$LVM_PROG" lvm`; `testfile=$SCRATCH_MNT/testfile`; `_cleanup()`; `_unmount $SCRATCH_MNT >>$seqres.full 2>&1`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_block_device`, `_require_command`, `_require_scratch_nolvm`. The test integrates with common xfstests libraries through `./common/preamble` and with suite-specific filesystem features selected by the `f2fs` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: prints `Silence is golden` after all checks pass; logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/f2fs/008 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/f2fs/009 -->

# sources/test-tools/xfstests/tests/f2fs/009

## Purpose

This is a regression test to check whether fsck can handle corrupted nlinks correctly, it uses inject.f2fs to inject nlinks w/ wrong value, and expects fsck.f2fs can detect such corruption and do the repair.

## Important APIs, Types, and Functions

This is a bash xfstests case in the `f2fs` suite. The harness entry and tags are `_begin_fstest auto quick`. Important local functions are `_cleanup`, `check_links`, `inject_and_check`. Key xfstests/helper interfaces include `_check_scratch_fs` (runs scratch filesystem consistency checking), `_scratch_unmount` (unmounts scratch to force persistence checks), `_require_scratch` (requires a disposable scratch filesystem), `_require_command` (checks availability of an external command), `_scratch_mount` (mounts the scratch filesystem). External or helper commands visible in the body include `find`, `ln`, `mkdir`, `rm`, `stat`, `touch`. Significant variables include `status`.

## Control Flow

The script sources `./common/preamble`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_require_scratch`; `_require_inject_f2fs_command node i_links`; `_require_command "$(type -P socket)" socket`; `_fixed_by_git_commit f2fs-tools 958cd6e \`; `filename=$SCRATCH_MNT/foo`; `hardlink=$SCRATCH_MNT/bar`; `_cleanup()`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state, fio verification state for direct/atomic I/O. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_command`, `_require_inject_f2fs_command`, `_require_scratch`. The test integrates with common xfstests libraries through `./common/preamble` and with suite-specific filesystem features selected by the `f2fs` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: prints `Silence is golden` after all checks pass; runs filesystem consistency checking; logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/f2fs/009 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/f2fs/010 -->

# sources/test-tools/xfstests/tests/f2fs/010

## Purpose

This is a regression testcase to check whether we will handle database inode dirty status correctly: 1. create a regular file, and write data into the file 2. start transaction on the file (via F2FS_IOC_START_ATOMIC_WRITE) 3. write transaction data to the file 4. rename the file 5. commit and end the transaction (via F2FS_IOC_COMMIT_ATOMIC_WRITE) 6. drop caches in order to call f2fs_evict_inode() It expects kernel panic will gone after we apply commit 03511e936916 ("f2fs: fix inconsistent dirty state of atomic.

## Important APIs, Types, and Functions

This is a bash xfstests case in the `f2fs` suite. The harness entry and tags are `_begin_fstest auto quick`. Important local functions are `_cleanup`. Key xfstests/helper interfaces include `_require_scratch` (requires a disposable scratch filesystem), `_require_command` (checks availability of an external command), `_scratch_mount` (mounts the scratch filesystem), `_scratch_mkfs` (formats the scratch filesystem). External or helper commands visible in the body include `f2fs_io`, `mv`, `rm`, `sync`. Significant variables include `status`.

## Control Flow

The script sources `./common/preamble`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_cleanup()`; `rm -r -f $tmp.*`; `_fixed_by_kernel_commit 03511e936916 \`; `_require_scratch`; `_require_command "$F2FS_IO_PROG" f2fs_io`; `_scratch_mkfs >> $seqres.full`; `_scratch_mount >> $seqres.full`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state, fio verification state for direct/atomic I/O. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_command`, `_require_scratch`. The test integrates with common xfstests libraries through `./common/preamble` and with suite-specific filesystem features selected by the `f2fs` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: prints `Silence is golden` after all checks pass; logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/f2fs/010 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/f2fs/011 -->

# sources/test-tools/xfstests/tests/f2fs/011

## Purpose

This is a regression testcase to check whether we will handle out-of-space case correctly during fallocate() on pinned file once we disable checkpoint. 1. mount f2fs w/ checkpoint=disable option 2. create fragmented file data 3. set flag w/ pinned flag 4. fallocate space for pinned file, expects panic due to running out of space We should apply both commit ("f2fs: fix to avoid panic once fallocation fails for pinfile") and commit ("f2fs: fix to avoid running out of free segments") to avoid system panic. Note that.

## Important APIs, Types, and Functions

This is a bash xfstests case in the `f2fs` suite. The harness entry and tags are `_begin_fstest auto quick`. No local shell functions are declared. Key xfstests/helper interfaces include `_scratch_mkfs_sized` (formats a scratch image/device of a requested size), `_require_scratch` (requires a disposable scratch filesystem), `_require_command` (checks availability of an external command), `_scratch_mount` (mounts the scratch filesystem). External or helper commands visible in the body include `f2fs_io`, `rm`, `sync`, `touch`. Significant variables include `status`.

## Control Flow

The script sources `./common/preamble`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_fixed_by_kernel_commit 48ea8b200414 \`; `_fixed_by_kernel_commit f7f8932ca6bb \`; `_require_scratch`; `_require_command "$F2FS_IO_PROG" f2fs_io`; `_scratch_mkfs_sized $((1*1024*1024*1024)) >> $seqres.full`; `_scratch_mount -o checkpoint=disable:10%`; `pinfile=$SCRATCH_MNT/file`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_command`, `_require_scratch`. The test integrates with common xfstests libraries through `./common/preamble` and with suite-specific filesystem features selected by the `f2fs` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/f2fs/011 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/f2fs/012 -->

# sources/test-tools/xfstests/tests/f2fs/012

## Purpose

This testcase checks whether linear lookup fallback works well or not as below: 1.create file w/ red heart as its filename 2.inject wrong hash code to the file 3.disable linear lookup, expect lookup failure 4.enable linear lookup, expect lookup succeed

## Important APIs, Types, and Functions

This is a bash xfstests case in the `f2fs` suite. The harness entry and tags are `_begin_fstest auto quick casefold`. Important local functions are `check_lookup`. Key xfstests/helper interfaces include `_require_scratch_nocheck` (requires scratch without pre-run fsck validation), `_try_scratch_mount` (attempts to mount scratch and lets the test decide skip/fail behavior), `_scratch_unmount` (unmounts scratch to force persistence checks), `_require_command` (checks availability of an external command), `_scratch_mount` (mounts the scratch filesystem). External or helper commands visible in the body include `f2fs_io`, `grep`, `mkdir`, `stat`, `touch`. Significant variables include `status`.

## Control Flow

The script sources `./common/preamble`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_fixed_by_kernel_commit 91b587ba79e1 \`; `_require_scratch_nocheck`; `_require_command "$F2FS_IO_PROG" f2fs_io`; `_require_inject_f2fs_command dent d_hash`; `_scratch_mkfs -O casefold -C utf8 >> $seqres.full`; `_try_scratch_mount "-o lookup_mode=auto" >> $seqres.full 2>&1`; `if [ $? == 0 ]; then`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state, device-mapper target state. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_command`, `_require_inject_f2fs_command`, `_require_scratch_nocheck`. The test integrates with common xfstests libraries through `./common/preamble` and with suite-specific filesystem features selected by the `f2fs` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: prints `Silence is golden` after all checks pass; logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/f2fs/012 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/f2fs/013 -->

# sources/test-tools/xfstests/tests/f2fs/013

## Purpose

This is a regression testcase to check whether we will handle database inode dirty status correctly: 1. mount f2fs image w/ timeout fault injection option 2. create a regular file, and write data into the file 3. start transaction on the file (via F2FS_IOC_START_ATOMIC_WRITE) 4. write transaction data to the file 5. commit and end the transaction (via F2FS_IOC_COMMIT_ATOMIC_WRITE) 6. meanwhile loop call fsync in parallel Before f098aeba04c9 ("f2fs: fix to avoid atomicity corruption of atomic file"), database file.

## Important APIs, Types, and Functions

This is a bash xfstests case in the `f2fs` suite. The harness entry and tags are `_begin_fstest auto quick`. Important local functions are `_cleanup`. Key xfstests/helper interfaces include `_require_scratch` (requires a disposable scratch filesystem), `_require_command` (checks availability of an external command), `_scratch_mount` (mounts the scratch filesystem), `_scratch_mkfs` (formats the scratch filesystem). External or helper commands visible in the body include `f2fs_io`, `fsync`, `rm`, `stat`, `sync`. Significant variables include `status`.

## Control Flow

The script sources `./common/preamble`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_require_kernel_config CONFIG_F2FS_FAULT_INJECTION`; `_require_command "$F2FS_IO_PROG" f2fs_io`; `_cleanup()`; `rm -r -f $tmp.*`; `_fixed_by_kernel_commit f098aeba04c9 \`; `_require_scratch`; `_scratch_mkfs >> $seqres.full`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state, fio verification state for direct/atomic I/O. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_command`, `_require_kernel_config`, `_require_scratch`. The test integrates with common xfstests libraries through `./common/preamble` and with suite-specific filesystem features selected by the `f2fs` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/f2fs/013 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/f2fs/014 -->

# sources/test-tools/xfstests/tests/f2fs/014

## Purpose

This is a regression test case to verify whether the CP_TRIMMED_FLAG is properly set after performing the following steps: 1. mount the f2fs filesystem 2. create a file, write data to it, then delete the file 3. unmount the filesystem 4. verify that the 'trimmed' flag is set in the checkpoint state We should apply the commit ("f2fs: fix missing discard for active segments") to resolve the issue where the 'trimmed' flag is missing.

## Important APIs, Types, and Functions

This is a bash xfstests case in the `f2fs` suite. The harness entry and tags are `_begin_fstest auto quick trim`. No local shell functions are declared. Key xfstests/helper interfaces include `_scratch_unmount` (unmounts scratch to force persistence checks), `_require_scratch` (requires a disposable scratch filesystem), `_require_command` (checks availability of an external command), `_scratch_mount` (mounts the scratch filesystem), `_scratch_mkfs` (formats the scratch filesystem). External or helper commands visible in the body include `dump.f2fs`, `grep`, `rm`, `sync`. Significant variables include `status`.

## Control Flow

The script sources `./common/preamble`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_fixed_by_kernel_commit 21263d035ff2 \`; `_require_scratch`; `_require_command "$DUMP_F2FS_PROG" dump.f2fs`; `_scratch_mkfs >> $seqres.full`; `_scratch_mount >> $seqres.full`; `_require_batched_discard $SCRATCH_MNT`; `foo=$SCRATCH_MNT/foo`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_batched_discard`, `_require_command`, `_require_scratch`. The test integrates with common xfstests libraries through `./common/preamble` and with suite-specific filesystem features selected by the `f2fs` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/f2fs/014 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/f2fs/015 -->

# sources/test-tools/xfstests/tests/f2fs/015

## Purpose

This testcase tries to check stability of mount result w/ common mount option and their combination.

## Important APIs, Types, and Functions

This is a bash xfstests case in the `f2fs` suite. The harness entry and tags are `_begin_fstest auto quick mount`. No local shell functions are declared. Key xfstests/helper interfaces include `_try_scratch_mount` (attempts to mount scratch and lets the test decide skip/fail behavior), `_scratch_unmount` (unmounts scratch to force persistence checks), `_scratch_mkfs` (formats the scratch filesystem). External or helper commands visible in the body include `mount`. Significant variables include `status`.

## Control Flow

The script sources `./common/preamble`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_require_kernel_config CONFIG_F2FS_FS_XATTR`; `_require_kernel_config CONFIG_F2FS_FS_POSIX_ACL`; `_require_kernel_config CONFIG_F2FS_FAULT_INJECTION`; `for ((i=0;i<${#options[@]};i=i+2))`; `echo "Option#$i: ${options[$i]} : ${options[$((i+1))]}"`; `if [ "${options[$((i+1))]}" ]; then`; `_scratch_mkfs "-O ${options[$((i+1))]}" >> $seqres.full || _fail "mkfs failed"`.

## State and Persistence Behavior

The test mutates mount/unmount state, fscrypt keys, policies, nonces, and ciphertext blocks, compressed extents or clusters, quota/project-id metadata. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_kernel_config`. The test integrates with common xfstests libraries through `./common/preamble` and with suite-specific filesystem features selected by the `f2fs` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent, encryption mode, nonce, and block-size assumptions must match kernel fscrypt behavior. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/f2fs/015 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/f2fs/016 -->

# sources/test-tools/xfstests/tests/f2fs/016

## Purpose

This testcase tries to check stability of mount result w/ f2fs special mount options and their combination.

## Important APIs, Types, and Functions

This is a bash xfstests case in the `f2fs` suite. The harness entry and tags are `_begin_fstest auto quick mount`. No local shell functions are declared. Key xfstests/helper interfaces include `_try_scratch_mount` (attempts to mount scratch and lets the test decide skip/fail behavior), `_scratch_unmount` (unmounts scratch to force persistence checks), `_scratch_mkfs` (formats the scratch filesystem). External or helper commands visible in the body include `mount`. Significant variables include `status`.

## Control Flow

The script sources `./common/preamble`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_require_kernel_config CONFIG_F2FS_FS_COMPRESSION`; `_require_kernel_config CONFIG_F2FS_FS_LZO`; `_require_kernel_config CONFIG_F2FS_FS_LZORLE`; `_require_kernel_config CONFIG_F2FS_FS_LZ4`; `_require_kernel_config CONFIG_F2FS_FS_LZ4HC`; `_require_kernel_config CONFIG_F2FS_FS_ZSTD`; `for ((i=0;i<${#options[@]};i=i+2))`.

## State and Persistence Behavior

The test mutates mount/unmount state, fscrypt keys, policies, nonces, and ciphertext blocks, compressed extents or clusters. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_kernel_config`. The test integrates with common xfstests libraries through `./common/preamble` and with suite-specific filesystem features selected by the `f2fs` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent, encryption mode, nonce, and block-size assumptions must match kernel fscrypt behavior, compression heuristics may change block layout while preserving user data. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/f2fs/016 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/f2fs/017 -->

# sources/test-tools/xfstests/tests/f2fs/017

## Purpose

This testcase tries to check stability of mount result w/ mount options for zoned device and their combination.

## Important APIs, Types, and Functions

This is a bash xfstests case in the `f2fs` suite. The harness entry and tags are `_begin_fstest auto quick mount`. No local shell functions are declared. Key xfstests/helper interfaces include No high-level helper call beyond the standard harness is dominant.. External or helper commands visible in the body include `mount`. Significant variables include `status`.

## Control Flow

The script sources `./common/preamble`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_require_zoned_device "$TEST_DEV"`; `_test_unmount >> $seqres.full 2>&1`; `for ((i=0;i<${#options[@]};i=i+2))`; `echo "Option#$i: ${options[$i]} : ${options[$((i+1))]}"`; `_test_mkfs "-m" >> $seqres.full || _fail "mkfs failed"`; `_test_mount "-o ${options[$i]}" >> $seqres.full 2>&1`; `echo $?`.

## State and Persistence Behavior

The test mutates mount/unmount state. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_zoned_device`. The test integrates with common xfstests libraries through `./common/preamble` and with suite-specific filesystem features selected by the `f2fs` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include timing or background-process races can make failures intermittent. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/f2fs/017 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/f2fs/018 -->

# sources/test-tools/xfstests/tests/f2fs/018

## Purpose

This is a regression test to check whether page eof will be zero or not after we truncate partial data in compressed cluster.

## Important APIs, Types, and Functions

This is a bash xfstests case in the `f2fs` suite. The harness entry and tags are `_begin_fstest auto quick rw compress`. Important local functions are `build_fio_config`, `check_data_eof`. Key xfstests/helper interfaces include `_require_xfs_io_command` (checks xfs_io subcommand support), `_require_scratch` (requires a disposable scratch filesystem), `_scratch_mount` (mounts the scratch filesystem), `_scratch_mkfs` (formats the scratch filesystem), `_require_fio` (checks fio support for generated job options). External or helper commands visible in the body include `rm`. Significant variables include `size`, `status`, `testfile`.

## Control Flow

The script sources `./common/preamble`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_fixed_by_kernel_commit ba8dac350faf \`; `_fixed_by_kernel_commit 0b2cd5092139 \`; `_require_xfs_io_command "truncate"`; `_require_scratch`; `testfile=$SCRATCH_MNT/testfile`; `_require_fio $fio_config`; `_scratch_mkfs "-O extra_attr,compression" >> $seqres.full || _fail "mkfs failed"`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state, compressed extents or clusters, fio verification state for direct/atomic I/O. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_fio`, `_require_scratch`, `_require_xfs_io_command`. The test integrates with common xfstests libraries through `./common/preamble` and with suite-specific filesystem features selected by the `f2fs` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent, stress-tool behavior and kernel timing can expose nondeterminism, compression heuristics may change block layout while preserving user data. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: prints `Silence is golden` after all checks pass; logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/f2fs/018 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/f2fs/019 -->

# sources/test-tools/xfstests/tests/f2fs/019

## Purpose

This is a regression test: 1. create a file 2. write file to create a direct node at special offset 3. use inject.f2fs to inject nid of direct node w/ ino of the inode 4. check whether f2fs kernel module will detect and report such corruption in the file

## Important APIs, Types, and Functions

This is a bash xfstests case in the `f2fs` suite. The harness entry and tags are `_begin_fstest auto quick rw`. No local shell functions are declared. Key xfstests/helper interfaces include `_require_scratch_nocheck` (requires scratch without pre-run fsck validation), `_scratch_unmount` (unmounts scratch to force persistence checks), `_scratch_mount` (mounts the scratch filesystem), `_scratch_mkfs` (formats the scratch filesystem). No standalone external commands were extracted beyond shell builtins and xfstests helper calls.. Significant variables include `status`, `testfile`.

## Control Flow

The script sources `./common/preamble`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_fixed_by_kernel_commit 77de19b6867f \`; `_require_scratch_nocheck`; `_require_inject_f2fs_command node addr`; `testfile=$SCRATCH_MNT/testfile`; `_scratch_mkfs >> $seqres.full`; `_scratch_mount`; `$XFS_IO_PROG -f -c "pwrite 3738M 1M" -c "fsync" $testfile >> $seqres.full`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_inject_f2fs_command`, `_require_scratch_nocheck`. The test integrates with common xfstests libraries through `./common/preamble` and with suite-specific filesystem features selected by the `f2fs` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/f2fs/019 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/f2fs/020 -->

# sources/test-tools/xfstests/tests/f2fs/020

## Purpose

This is a regression test: 1. create directory 2. add a new xattr entry to create xattr node 3. use inject.f2fs to inject nid of xattr node w/ ino in a file 4. check whether f2fs kernel module will detect and report such corruption in the file

## Important APIs, Types, and Functions

This is a bash xfstests case in the `f2fs` suite. The harness entry and tags are `_begin_fstest auto quick rw`. No local shell functions are declared. Key xfstests/helper interfaces include `_require_scratch_nocheck` (requires scratch without pre-run fsck validation), `_scratch_unmount` (unmounts scratch to force persistence checks), `_scratch_mount` (mounts the scratch filesystem), `_require_attrs` (requires extended attribute support), `_scratch_mkfs` (formats the scratch filesystem). External or helper commands visible in the body include `mkdir`. Significant variables include `status`.

## Control Flow

The script sources `./common/preamble`, `./common/attr`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_fixed_by_kernel_commit 061cf3a84bde \`; `_require_scratch_nocheck`; `_require_inject_f2fs_command node i_xattr_nid`; `_require_attrs user`; `testdir=$SCRATCH_MNT/testdir`; `_scratch_mkfs >> $seqres.full`; `_scratch_mount "-o user_xattr,noinline_xattr"`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_attrs`, `_require_inject_f2fs_command`, `_require_scratch_nocheck`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/attr` and with suite-specific filesystem features selected by the `f2fs` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: prints `Silence is golden` after all checks pass; logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/f2fs/020 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/f2fs/021 -->

# sources/test-tools/xfstests/tests/f2fs/021

## Purpose

This testcase tries to check whether f2fs can handle "usrjquota=" during remount correctly

## Important APIs, Types, and Functions

This is a bash xfstests case in the `f2fs` suite. The harness entry and tags are `_begin_fstest auto quick mount quota remount`. No local shell functions are declared. Key xfstests/helper interfaces include `_scratch_unmount` (unmounts scratch to force persistence checks), `_require_scratch` (requires a disposable scratch filesystem), `_scratch_mount` (mounts the scratch filesystem), `_scratch_mkfs` (formats the scratch filesystem). External or helper commands visible in the body include `mount`. Significant variables include `status`.

## Control Flow

The script sources `./common/preamble`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_fixed_by_kernel_commit 930a9a6ee8e7 \`; `_require_scratch`; `_scratch_mkfs >> $seqres.full`; `_scratch_mount "-o usrquota"`; `quotacheck -uc $SCRATCH_MNT`; `_scratch_unmount`; `_scratch_mount "-o usrjquota=aquota.user,jqfmt=vfsold"`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state, quota/project-id metadata. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_scratch`. The test integrates with common xfstests libraries through `./common/preamble` and with suite-specific filesystem features selected by the `f2fs` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: prints `Silence is golden` after all checks pass; logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/f2fs/021 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/f2fs/022 -->

# sources/test-tools/xfstests/tests/f2fs/022

## Purpose

This is a regression test: 1. create foo & bar 2. write 8M data to foo 3. use inject.f2fs to inject i_nid[0] of foo w/ ino of bar 4. fpunch in foo w/ specified range

## Important APIs, Types, and Functions

This is a bash xfstests case in the `f2fs` suite. The harness entry and tags are `_begin_fstest auto quick rw`. No local shell functions are declared. Key xfstests/helper interfaces include `_require_scratch_nocheck` (requires scratch without pre-run fsck validation), `_scratch_unmount` (unmounts scratch to force persistence checks), `_scratch_mount` (mounts the scratch filesystem), `_scratch_mkfs` (formats the scratch filesystem). External or helper commands visible in the body include `stat`, `sync`, `touch`. Significant variables include `status`.

## Control Flow

The script sources `./common/preamble`, `./common/attr`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_fixed_by_kernel_commit c18ecd99e0c7 \`; `_require_scratch_nocheck`; `_require_inject_f2fs_command node i_nid`; `foo_path=$SCRATCH_MNT/foo`; `bar_path=$SCRATCH_MNT/bar`; `_scratch_mkfs >> $seqres.full`; `_scratch_mount`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_inject_f2fs_command`, `_require_scratch_nocheck`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/attr` and with suite-specific filesystem features selected by the `f2fs` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/f2fs/022 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/f2fs/023 -->

# sources/test-tools/xfstests/tests/f2fs/023

## Purpose

This testcase tries to inject fault into inode.i_inline_xattr_size, and check whether sanity check of f2fs can handle fault correctly.

## Important APIs, Types, and Functions

This is a bash xfstests case in the `f2fs` suite. The harness entry and tags are `_begin_fstest auto quick rw attr`. No local shell functions are declared. Key xfstests/helper interfaces include `_require_scratch_nocheck` (requires scratch without pre-run fsck validation), `_scratch_unmount` (unmounts scratch to force persistence checks), `_filter_scratch` (normalizes scratch paths in stdout), `_scratch_mount` (mounts the scratch filesystem), `_require_attrs` (requires extended attribute support). External or helper commands visible in the body include `grep`, `touch`. Significant variables include `status`, `testfile`.

## Control Flow

The script sources `./common/preamble`, `./common/attr`, `./common/filter`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_fixed_by_kernel_commit 5c1768b67250 \`; `_require_attrs`; `_require_scratch_nocheck`; `_require_inject_f2fs_command node i_inline`; `_require_inject_f2fs_command node i_inline_xattr_size`; `testfile=$SCRATCH_MNT/testfile`; `_scratch_mkfs "-O extra_attr,flexible_inline_xattr" >> $seqres.full || _fail "mkfs failed"`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_attrs`, `_require_inject_f2fs_command`, `_require_scratch_nocheck`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/attr`, `./common/filter` and with suite-specific filesystem features selected by the `f2fs` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/f2fs/023 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/f2fs/024 -->

# sources/test-tools/xfstests/tests/f2fs/024

## Purpose

This test case tries to check whether resize.f2fs can correctly zero out ssa blocks without corrupting the main area blocks.

## Important APIs, Types, and Functions

This is a bash xfstests case in the `f2fs` suite. The harness entry and tags are `_begin_fstest auto quick`. No local shell functions are declared. Key xfstests/helper interfaces include `_scratch_mkfs_sized` (formats a scratch image/device of a requested size), `_require_command` (checks availability of an external command), `_scratch_mount` (mounts the scratch filesystem). External or helper commands visible in the body include `blockdev`, `dump.f2fs`, `grep`, `sed`. Significant variables include `status`.

## Control Flow

The script sources `./common/preamble`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_fixed_by_git_commit f2fs-tools xxxxxxxxxxxx \`; `_require_scratch_size_nocheck $(($target_fs_size/1024))`; `_require_command "$F2FS_RESIZE_PROG" resize.f2fs`; `_require_command "$DUMP_F2FS_PROG" dump.f2fs`; `_scratch_mkfs_sized $((512*1024*1024)) "" "-g android" >> $seqres.full`; `sector_size=$(blockdev --getss $SCRATCH_DEV)`; `$F2FS_RESIZE_PROG -F $SCRATCH_DEV -t $target_sectors >> $seqres.full 2>&1 || \`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_command`, `_require_scratch_size_nocheck`. The test integrates with common xfstests libraries through `./common/preamble` and with suite-specific filesystem features selected by the `f2fs` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/f2fs/024 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/f2fs/Makefile -->

# sources/test-tools/xfstests/tests/f2fs/Makefile

## Purpose

This Makefile is the install/build manifest for the xfstests `f2fs` test directory. It delegates to the shared `include/builddefs` and `$(BUILDRULES)` infrastructure and declares which numbered shell tests and companion files are part of this suite.

## Important APIs, Types, and Functions

The primary interface is GNU make metadata: `TOPDIR`, `include $(TOPDIR)/include/builddefs`, `TARGET_DIR`, `INSTALL_DIR`, `INSTALL_MODE`, `TESTS`, `MKFS_CONFIGS`, and `default: depend`. The `include $(BUILDRULES)` line supplies the common xfstests targets for dependency generation and installation.

## Control Flow

Make evaluates the top-level path variables, includes global build definitions, sets the destination directory to `$(PKG_LIB_DIR)/tests/f2fs`, lists tests/configuration payloads, and lets the shared build rules implement `default`, `depend`, and install behavior. The file does not run filesystem tests itself; it makes the scripts available to the harness.

## State and Persistence Behavior

Persistent output is limited to build/install artifacts produced by the shared Make rules. The manifest itself records 4 numbered test references; it has no runtime scratch-device state.

## Dependencies and Integration Points

It depends on the repository-level `include/builddefs` and `$(BUILDRULES)`. It integrates with xfstests packaging by installing the declared scripts under the suite-specific tests directory.

## Risks and Edge Cases

The main risk is manifest drift: adding or removing a test script without updating `TESTS` or `MKFS_CONFIGS` can prevent the harness from installing or discovering the intended file. Shared Make variables must be available from the top-level xfstests build environment.

## Test Signals

Useful signals are successful `make` dependency/install runs and the presence of every declared test/config in the installed `f2fs` tests directory.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/f2fs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/001 -->

# sources/test-tools/xfstests/tests/generic/001

## Purpose

Random file copier to produce chains of identical files so the head and the tail can be diff'd at the end of each iteration. Exercises creat, write and unlink for a variety of directory sizes, and checks for data corruption. config has one line per file with filename and byte size, else use the default one below.

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest rw dir udf auto quick`. Important local functions are `_chain`, `_check`, `_cleanup`, `_mark_iteration`, `_setup`. Key xfstests/helper interfaces include `_require_test` (requires the configured TEST_DIR filesystem). External or helper commands visible in the body include `cmp`, `cp`, `diff`, `mkdir`, `mv`, `rm`, `sed`, `touch`. Significant variables include `dir`, `status`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_require_test`; `if [ $# -eq 0 ]`; `if [ -f $1 ]`; `cp $1 $tmp.config`; `echo "Error: cannot open config \"$1\""`; `echo "Usage: run [config]"`; `_setup()`.

## State and Persistence Behavior

The test mutates files under `TEST_DIR`. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_test`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include timing or background-process races can make failures intermittent. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: uses byte-for-byte comparison of generated and expected data; logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/001 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/002 -->

# sources/test-tools/xfstests/tests/generic/002

## Purpose

simple inode link count test for a regular file

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest metadata udf auto quick`. No local shell functions are declared. Key xfstests/helper interfaces include `_require_test` (requires the configured TEST_DIR filesystem). External or helper commands visible in the body include `ln`, `mkdir`, `rm`, `sed`, `touch`. Significant variables include `status`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_require_test`; `_require_hardlinks`; `echo "Silence is goodness ..."`; `mkdir \`dirname $TEST_DIR/tmp\` 2>/dev/null`; `touch $TEST_DIR/tmp.1`; `for l in 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20`; `ln $TEST_DIR/tmp.1 $TEST_DIR/tmp.$l`.

## State and Persistence Behavior

The test mutates files under `TEST_DIR`. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_hardlinks`, `_require_test`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include golden-output drift or unsupported prerequisite handling are the main maintenance risks. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: passes when required commands complete and the xfstests golden output matches. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/002 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/003 -->

# sources/test-tools/xfstests/tests/generic/003

## Purpose

Tests the noatime, relatime, strictatime and nodiratime mount options. There is an extra check for Btrfs to ensure that the access time is never updated on read-only subvolumes. (Regression test for bug fixed with commit 93fd63c2f001ca6797c6b15b696a484b165b4800)

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest atime auto quick`. Important local functions are `_compare_stat_times`, `_stat`. Key xfstests/helper interfaces include `_scratch_cycle_mount` (unmounts and remounts scratch to test persisted metadata), `_scratch_unmount` (unmounts scratch to force persistence checks), `_require_scratch` (requires a disposable scratch filesystem), `_scratch_mount` (mounts the scratch filesystem), `_scratch_mkfs` (formats the scratch filesystem). External or helper commands visible in the body include `ls`, `mkdir`, `mv`, `stat`. Significant variables include `IFS`, `SPATH`, `TPATH`, `status`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_require_scratch`; `_require_atime`; `_require_relatime`; `if [ "$FSTYP" = "exfat" ]; then`; `_stat() {`; `_compare_stat_times() {`; `for i in 0 1 2; do`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_atime`, `_require_relatime`, `_require_scratch`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: prints `Silence is golden` after all checks pass; logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/003 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/004 -->

# sources/test-tools/xfstests/tests/generic/004

## Purpose

Test O_TMPFILE opens, and linking them back into the namespace.

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest auto quick`. Important local functions are `_cleanup`. Key xfstests/helper interfaces include `_require_xfs_io_command` (checks xfs_io subcommand support), `_filter_xfs_io` (normalizes xfs_io output), `_require_test` (requires the configured TEST_DIR filesystem). External or helper commands visible in the body include `rm`. Significant variables include `status`, `testfile`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_cleanup()`; `rm -f ${testfile}`; `_require_test`; `_require_xfs_io_command "-T"`; `_require_xfs_io_command "flink"`; `$XFS_IO_PROG -T \`; `rm ${testfile}`.

## State and Persistence Behavior

The test mutates temporary files under `$tmp.*` and harness result files. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_test`, `_require_xfs_io_command`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include timing or background-process races can make failures intermittent. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: passes when required commands complete and the xfstests golden output matches. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/004 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/005 -->

# sources/test-tools/xfstests/tests/generic/005

## Purpose

Test symlinks & ELOOP Note: On Linux, ELOOP limit used to be 32 but changed to 8, and lately its become 5. Who knows what it might be next. What we are looking for here is: no panic due to blowing the stack; and that the ELOOP error code is returned at some point (the actual limit point is unimportant, just checking that we do hit it).

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest dir udf auto quick`. Important local functions are `_cleanup`, `_touch`. Key xfstests/helper interfaces include `_require_test` (requires the configured TEST_DIR filesystem). External or helper commands visible in the body include `grep`, `ln`, `rm`, `touch`. Significant variables include `status`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_cleanup()`; `cd $TEST_DIR`; `rm -f symlink_{0,1,2,3,4}{0,1,2,3,4,5,6,7,8,9} symlink_self empty_file`; `_touch()`; `touch $@ 2>&1 | grep -q 'Too many levels of symbolic links'`; `if [ $? -eq 0 ]; then`; `echo "ELOOP returned.  Good."`.

## State and Persistence Behavior

The test mutates files under `TEST_DIR`. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_symlinks`, `_require_test`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include timing or background-process races can make failures intermittent. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: passes when required commands complete and the xfstests golden output matches. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/005 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/006 -->

# sources/test-tools/xfstests/tests/generic/006

## Purpose

permname

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest dir udf auto quick`. Important local functions are `_cleanup`, `_count`. Key xfstests/helper interfaces include `_require_test` (requires the configured TEST_DIR filesystem). External or helper commands visible in the body include `find`, `mkdir`, `rm`. Significant variables include `status`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_cleanup()`; `rm -f $tmp.*`; `rm -rf $TEST_DIR/permname.$$`; `_count()`; `_require_test`; `mkdir $TEST_DIR/permname.$$`; `echo ""`.

## State and Persistence Behavior

The test mutates files under `TEST_DIR`. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_test`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include golden-output drift or unsupported prerequisite handling are the main maintenance risks. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: passes when required commands complete and the xfstests golden output matches. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/006 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/007 -->

# sources/test-tools/xfstests/tests/generic/007

## Purpose

drive the src/nametest program which does a heap of open(create)/unlink/stat and checks that error codes make sense with its memory of the files created.

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest dir udf auto quick`. Important local functions are `_cleanup`. Key xfstests/helper interfaces include `_require_test` (requires the configured TEST_DIR filesystem). External or helper commands visible in the body include `mkdir`, `rm`. Significant variables include `status`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_cleanup()`; `rm -f $tmp.*`; `rm -rf $TEST_DIR/$seq`; `_require_test`; `while [ $i -le $num_filenames ]; do`; `echo "nametest.$i" >>$sourcefile`; `rm -rf $TEST_DIR/$seq`.

## State and Persistence Behavior

The test mutates files under `TEST_DIR`. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_test`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include golden-output drift or unsupported prerequisite handling are the main maintenance risks. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: passes when required commands complete and the xfstests golden output matches. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/007 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/008 -->

# sources/test-tools/xfstests/tests/generic/008

## Purpose

Makes calls to fallocate zero range and checks tossed ranges Primarily tests page boundries and boundries that are off-by-one to ensure we're only tossing what's expected

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest auto quick prealloc zero`. No local shell functions are declared. Key xfstests/helper interfaces include `_require_xfs_io_command` (checks xfs_io subcommand support), `_require_test` (requires the configured TEST_DIR filesystem). No standalone external commands were extracted beyond shell builtins and xfstests helper calls.. Significant variables include `status`, `testfile`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, `./common/punch`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_require_xfs_io_command "fzero"`; `_require_test`; `testfile=$TEST_DIR/008.$$`; `_test_block_boundaries 1024 fzero _filter_xfs_io_unique $testfile`; `_test_block_boundaries 2048 fzero _filter_xfs_io_unique $testfile`; `_test_block_boundaries 4096 fzero _filter_xfs_io_unique $testfile`; `_test_block_boundaries 65536 fzero _filter_xfs_io_unique $testfile`.

## State and Persistence Behavior

The test mutates files under `TEST_DIR`. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_test`, `_require_xfs_io_command`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter`, `./common/punch` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include golden-output drift or unsupported prerequisite handling are the main maintenance risks. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: passes when required commands complete and the xfstests golden output matches. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/008 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/009 -->

# sources/test-tools/xfstests/tests/generic/009

## Purpose

Test fallocate FALLOC_FL_ZERO_RANGE

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest auto quick prealloc zero fiemap`. No local shell functions are declared. Key xfstests/helper interfaces include `_require_xfs_io_command` (checks xfs_io subcommand support), `_filter_fiemap` (normalizes fiemap output), `_require_test` (requires the configured TEST_DIR filesystem). External or helper commands visible in the body include `fiemap`. Significant variables include `status`, `testfile`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, `./common/punch`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_require_xfs_io_command "fzero"`; `_require_xfs_io_command "fiemap"`; `_require_xfs_io_command "falloc"`; `_require_test`; `testfile=$TEST_DIR/009.$$`; `if [ "$FSTYP" = "ext4" ]; then`; `_ext4_disable_extent_zeroout`.

## State and Persistence Behavior

The test mutates files under `TEST_DIR`. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_test`, `_require_xfs_io_command`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter`, `./common/punch` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include extent layout assumptions can vary by filesystem feature and kernel version. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: passes when required commands complete and the xfstests golden output matches. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/009 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/010 -->

# sources/test-tools/xfstests/tests/generic/010

## Purpose

dbtest

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest other udf auto`. Important local functions are `_cleanup`, `_filter_dbtest`. Key xfstests/helper interfaces include `_require_test_program` (checks availability of an xfstests helper binary), `_require_test` (requires the configured TEST_DIR filesystem). External or helper commands visible in the body include `rm`, `sed`. Significant variables include `status`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_cleanup()`; `rm -f $tmp.*`; `rm -f $TEST_DIR/DBtest*.{pag,dir}`; `_filter_dbtest()`; `_require_test_program "dbtest"`; `_require_test`; `cd $TEST_DIR`.

## State and Persistence Behavior

The test mutates files under `TEST_DIR`. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_test`, `_require_test_program`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include timing or background-process races can make failures intermittent. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/010 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/011 -->

# sources/test-tools/xfstests/tests/generic/011

## Purpose

dirstress

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest dir udf auto quick`. Important local functions are `_cleanup`, `_test`. Key xfstests/helper interfaces include `_require_test` (requires the configured TEST_DIR filesystem). External or helper commands visible in the body include `mkdir`, `rm`. Significant variables include `status`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_cleanup()`; `rm -f $tmp.*`; `_require_test`; `out=$TEST_DIR/dirstress.$$`; `_test()`; `echo "*** TEST $test $args -f <count>"`; `if ! $here/src/dirstress -d $out -f $count $args >$tmp.out 2>&1`.

## State and Persistence Behavior

The test mutates files under `TEST_DIR`. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_test`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include timing or background-process races can make failures intermittent. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/011 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/012 -->

# sources/test-tools/xfstests/tests/generic/012

## Purpose

Multi collapse range tests This testcase is one of the 4 testcases which tries to test various corner cases for fcollapse range functionality over different type of extents. These tests are based on generic/255 test case. For the type of tests, check the description of _test_generic_punch in common/rc.

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest auto quick prealloc punch collapse fiemap`. No local shell functions are declared. Key xfstests/helper interfaces include `_require_xfs_io_command` (checks xfs_io subcommand support), `_require_test` (requires the configured TEST_DIR filesystem). External or helper commands visible in the body include `fiemap`. Significant variables include `status`, `testfile`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, `./common/punch`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_require_test`; `_require_xfs_io_command "fpunch"`; `_require_xfs_io_command "falloc"`; `_require_xfs_io_command "fiemap"`; `_require_xfs_io_command "fcollapse"`; `testfile=$TEST_DIR/$seq.$$`; `_test_generic_punch -k falloc fpunch fcollapse fiemap _filter_hole_fiemap $testfile`.

## State and Persistence Behavior

The test mutates files under `TEST_DIR`. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_test`, `_require_xfs_io_command`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter`, `./common/punch` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include extent layout assumptions can vary by filesystem feature and kernel version. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: passes when required commands complete and the xfstests golden output matches. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/012 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/013 -->

# sources/test-tools/xfstests/tests/generic/013

## Purpose

fsstress

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest other ioctl udf auto quick`. Important local functions are `_do_test`. Key xfstests/helper interfaces include `_require_test` (requires the configured TEST_DIR filesystem). External or helper commands visible in the body include `fsstress`, `mkdir`, `rm`. Significant variables include `status`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_do_test()`; `_n="$1"`; `_param="$2"`; `_count="$3"`; `out=$TEST_DIR/fsstress.$seq.$_n`; `rm -rf $out`; `if ! mkdir $out`.

## State and Persistence Behavior

The test mutates files under `TEST_DIR`. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_test`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include stress-tool behavior and kernel timing can expose nondeterminism. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/013 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/014 -->

# sources/test-tools/xfstests/tests/generic/014

## Purpose

truncfile

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest rw udf auto quick`. Important local functions are `_cleanup`. Key xfstests/helper interfaces include `_require_test` (requires the configured TEST_DIR filesystem). External or helper commands visible in the body include `rm`. Significant variables include `status`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_cleanup()`; `rm -f $tmp.*`; `rm -rf $TEST_DIR/truncfile.$$.*`; `_require_test`; `_require_sparse_files`; `if [ "$FSTYP" == "xfs" ]; then`; `_test_unmount`.

## State and Persistence Behavior

The test mutates files under `TEST_DIR`, mount/unmount state. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_sparse_files`, `_require_test`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include timing or background-process races can make failures intermittent. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: passes when required commands complete and the xfstests golden output matches. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/014 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/015 -->

# sources/test-tools/xfstests/tests/generic/015

## Purpose

check out-of-space behaviour

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest other auto quick enospc`. Important local functions are `_cleanup`, `_free`. Key xfstests/helper interfaces include `_scratch_mkfs_sized` (formats a scratch image/device of a requested size), `_scratch_unmount` (unmounts scratch to force persistence checks), `_require_scratch` (requires a disposable scratch filesystem), `_scratch_mount` (mounts the scratch filesystem). External or helper commands visible in the body include `dd`, `fill`, `ls`, `rm`. Significant variables include `POSIXLY_CORRECT`, `status`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_cleanup()`; `_scratch_unmount`; `_free()`; `_df_dir $SCRATCH_MNT | $AWK_PROG '{ print $5 }'`; `_require_scratch`; `_require_no_large_scratch_dev`; `_scratch_mkfs_sized $((256 * 1024 * 1024)) >> $seqres.full 2>&1`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_no_large_scratch_dev`, `_require_scratch`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/015 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/016 -->

# sources/test-tools/xfstests/tests/generic/016

## Purpose

Delayed allocation multi collapse range tests This testcase is one of the 4 testcases which tries to test various corner cases for fcollapse range functionality over different type of extents. These tests are based on generic/255 test case. For the type of tests, check the description of _test_generic_punch in common/rc.

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest auto quick prealloc punch collapse fiemap`. No local shell functions are declared. Key xfstests/helper interfaces include `_require_xfs_io_command` (checks xfs_io subcommand support), `_require_test` (requires the configured TEST_DIR filesystem). External or helper commands visible in the body include `fiemap`. Significant variables include `status`, `testfile`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, `./common/punch`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_require_test`; `_require_xfs_io_command "fpunch"`; `_require_xfs_io_command "falloc"`; `_require_xfs_io_command "fiemap"`; `_require_xfs_io_command "fcollapse"`; `testfile=$TEST_DIR/$seq.$$`; `_test_generic_punch -d -k falloc fpunch fcollapse fiemap _filter_hole_fiemap $testfile`.

## State and Persistence Behavior

The test mutates files under `TEST_DIR`. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_test`, `_require_xfs_io_command`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter`, `./common/punch` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include extent layout assumptions can vary by filesystem feature and kernel version. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: passes when required commands complete and the xfstests golden output matches. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/016 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/017 -->

# sources/test-tools/xfstests/tests/generic/017

## Purpose

Test multiple fallocate collapse range calls on same file. For different blocksizes, collapse a single alternate block multiple times until the file is left with 80 blocks and as much number of extents. Also check for file system consistency after completing this operation for each blocksize.

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest auto prealloc collapse fiemap`. No local shell functions are declared. Key xfstests/helper interfaces include `_require_xfs_io_command` (checks xfs_io subcommand support), `_require_scratch` (requires a disposable scratch filesystem), `_scratch_mount` (mounts the scratch filesystem), `_scratch_mkfs` (formats the scratch filesystem). External or helper commands visible in the body include `fiemap`, `fsync`, `grep`. Significant variables include `BLOCKS`, `BSIZE`, `status`, `testfile`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_require_scratch`; `_require_xfs_io_command "fiemap"`; `_require_xfs_io_command "fcollapse"`; `_do_die_on_error=y`; `_scratch_mkfs > /dev/null 2>&1`; `_scratch_mount`; `testfile=$SCRATCH_MNT/$seq.$$`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_scratch`, `_require_xfs_io_command`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent, extent layout assumptions can vary by filesystem feature and kernel version. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: passes when required commands complete and the xfstests golden output matches. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/017 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/018 -->

# sources/test-tools/xfstests/tests/generic/018

## Purpose

Basic defragmentation sanity tests

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest auto fsr quick defrag`. No local shell functions are declared. Key xfstests/helper interfaces include `_require_scratch` (requires a disposable scratch filesystem), `_require_defrag` (requires filesystem defrag support), `_scratch_mount` (mounts the scratch filesystem), `_scratch_mkfs` (formats the scratch filesystem). External or helper commands visible in the body include `defrag`, `rm`, `sync`, `touch`. Significant variables include `status`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, `./common/defrag`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_require_scratch`; `_scratch_mkfs >/dev/null 2>&1`; `_scratch_mount`; `_require_defrag`; `fragfile=$SCRATCH_MNT/fragfile.$$`; `rm -f $fragfile`; `bsize=$(_get_file_block_size $SCRATCH_MNT)`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_defrag`, `_require_scratch`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter`, `./common/defrag` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/018 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/019 -->

# sources/test-tools/xfstests/tests/generic/019

## Purpose

xfstests shell test generic/019. Its tags are aio, dangerous, enospc, rw, stress, recoveryloop, mmap, so it participates in the xfstests harness for filesystem behavior regression coverage.

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest aio dangerous enospc rw stress recoveryloop mmap`. Important local functions are `_cleanup`, `_workout`. Key xfstests/helper interfaces include `_scratch_unmount` (unmounts scratch to force persistence checks), `_require_scratch` (requires a disposable scratch filesystem), `_scratch_mount` (mounts the scratch filesystem), `_scratch_mkfs` (formats the scratch filesystem), `_require_fio` (checks fio support for generated job options). External or helper commands visible in the body include `blockdev`, `dd`, `fio`, `fsync`, `rm`. Significant variables include `BLK_DEV_SIZE`, `FILE_SIZE`, `FSSTRESS_AVOID`, `NUM_JOBS`, `RUN_TIME`, `bs`, `size`, `status`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, `./common/fail_make_request`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_require_scratch`; `_require_block_device $SCRATCH_DEV`; `_require_fail_make_request`; `_cleanup()`; `_kill_fsstress`; `_disallow_fail_make_request`; `rm -r -f $tmp.*`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state, fio verification state for direct/atomic I/O. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_block_device`, `_require_fail_make_request`, `_require_fio`, `_require_metadata_journaling`, `_require_scratch`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter`, `./common/fail_make_request` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent, stress-tool behavior and kernel timing can expose nondeterminism. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/019 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/020 -->

# sources/test-tools/xfstests/tests/generic/020

## Purpose

extended attributes

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest metadata attr udf auto quick`. Important local functions are `_attr`, `_attr_get_max`, `_attr_get_maxval_size`, `_attr_list`, `_filter`, `do_getfattr`, and others. Key xfstests/helper interfaces include `_require_attrs` (requires extended attribute support), `_require_test` (requires the configured TEST_DIR filesystem). External or helper commands visible in the body include `awk`, `dd`, `od`, `rm`, `sed`, `touch`. Significant variables include `BLOCK_SIZE`, `LEB_SIZE`, `OCTAL_SIZE`, `file`, `size`, `status`, `testfile`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, `./common/attr`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_filter()`; `sed "s#$TEST_DIR[^ :]*#<TESTFILE>#g;`; `_attr()`; `_filter $tmp.out`; `_filter $tmp.err 1>&2`; `_getfattr $* 2>$tmp.err >$tmp.out`; `_filter $tmp.out`.

## State and Persistence Behavior

The test mutates files under `TEST_DIR`. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_attrs`, `_require_btrfs_command`, `_require_test`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter`, `./common/attr` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include timing or background-process races can make failures intermittent. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/020 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/021 -->

# sources/test-tools/xfstests/tests/generic/021

## Purpose

Standard collapse range tests This testcase is one of the 4 testcases which tries to test various corner cases for fcollapse range functionality over different type of extents. These tests are based on generic/255 test case. For the type of tests, check the description of _test_generic_punch in common/rc.

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest auto quick prealloc punch collapse fiemap`. No local shell functions are declared. Key xfstests/helper interfaces include `_require_xfs_io_command` (checks xfs_io subcommand support), `_require_test` (requires the configured TEST_DIR filesystem). External or helper commands visible in the body include `fiemap`. Significant variables include `status`, `testfile`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, `./common/punch`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_require_test`; `_require_xfs_io_command "fpunch"`; `_require_xfs_io_command "falloc"`; `_require_xfs_io_command "fiemap"`; `_require_xfs_io_command "fcollapse"`; `testfile=$TEST_DIR/$seq.$$`; `_test_generic_punch falloc fpunch fcollapse fiemap _filter_hole_fiemap $testfile`.

## State and Persistence Behavior

The test mutates files under `TEST_DIR`. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_test`, `_require_xfs_io_command`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter`, `./common/punch` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include extent layout assumptions can vary by filesystem feature and kernel version. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: passes when required commands complete and the xfstests golden output matches. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/021 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/022 -->

# sources/test-tools/xfstests/tests/generic/022

## Purpose

Delayed allocation collapse range tests This testcase is one of the 4 testcases which tries to test various corner cases for fcollapse range functionality over different type of extents. These tests are based on generic/255 test case. For the type of tests, check the description of _test_generic_punch in common/rc.

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest auto quick prealloc punch collapse fiemap`. No local shell functions are declared. Key xfstests/helper interfaces include `_require_xfs_io_command` (checks xfs_io subcommand support), `_require_test` (requires the configured TEST_DIR filesystem). External or helper commands visible in the body include `fiemap`. Significant variables include `status`, `testfile`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, `./common/punch`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_require_test`; `_require_xfs_io_command "fpunch"`; `_require_xfs_io_command "falloc"`; `_require_xfs_io_command "fiemap"`; `_require_xfs_io_command "fcollapse"`; `testfile=$TEST_DIR/$seq.$$`; `_test_generic_punch -d falloc fpunch fcollapse fiemap _filter_hole_fiemap $testfile`.

## State and Persistence Behavior

The test mutates files under `TEST_DIR`. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_test`, `_require_xfs_io_command`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter`, `./common/punch` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include extent layout assumptions can vary by filesystem feature and kernel version. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: passes when required commands complete and the xfstests golden output matches. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/022 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/023 -->

# sources/test-tools/xfstests/tests/generic/023

## Purpose

Check renameat2 syscall without flags

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest auto quick`. No local shell functions are declared. Key xfstests/helper interfaces include `_require_test` (requires the configured TEST_DIR filesystem). External or helper commands visible in the body include `mkdir`. Significant variables include `status`.

## Control Flow

The script sources `./common/preamble`, `./common/renameat2`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_require_test`; `_require_renameat2`; `_require_symlinks`; `rename_dir=$TEST_DIR/$$`; `mkdir -p $rename_dir`; `_rename_tests $rename_dir`.

## State and Persistence Behavior

The test mutates files under `TEST_DIR`. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_renameat2`, `_require_symlinks`, `_require_test`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/renameat2` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include golden-output drift or unsupported prerequisite handling are the main maintenance risks. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: passes when required commands complete and the xfstests golden output matches. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/023 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/024 -->

# sources/test-tools/xfstests/tests/generic/024

## Purpose

Check renameat2 syscall with RENAME_NOREPLACE flag

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest auto quick`. No local shell functions are declared. Key xfstests/helper interfaces include `_require_test` (requires the configured TEST_DIR filesystem). External or helper commands visible in the body include `mkdir`. Significant variables include `status`.

## Control Flow

The script sources `./common/preamble`, `./common/renameat2`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_require_test`; `_require_renameat2 noreplace`; `_require_symlinks`; `rename_dir=$TEST_DIR/$$`; `mkdir $rename_dir`; `_rename_tests $rename_dir -n`.

## State and Persistence Behavior

The test mutates files under `TEST_DIR`. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_renameat2`, `_require_symlinks`, `_require_test`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/renameat2` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include golden-output drift or unsupported prerequisite handling are the main maintenance risks. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: passes when required commands complete and the xfstests golden output matches. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/024 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/025 -->

# sources/test-tools/xfstests/tests/generic/025

## Purpose

Check renameat2 syscall with RENAME_EXCHANGE flag

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest auto quick`. No local shell functions are declared. Key xfstests/helper interfaces include `_require_test` (requires the configured TEST_DIR filesystem). External or helper commands visible in the body include `mkdir`. Significant variables include `status`.

## Control Flow

The script sources `./common/preamble`, `./common/renameat2`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_require_test`; `_require_renameat2 exchange`; `_require_symlinks`; `rename_dir=$TEST_DIR/$$`; `mkdir $rename_dir`; `_rename_tests $rename_dir -x`.

## State and Persistence Behavior

The test mutates files under `TEST_DIR`. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_renameat2`, `_require_symlinks`, `_require_test`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/renameat2` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include golden-output drift or unsupported prerequisite handling are the main maintenance risks. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: passes when required commands complete and the xfstests golden output matches. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/025 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/026 -->

# sources/test-tools/xfstests/tests/generic/026

## Purpose

Test out ACL count limits

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest acl quick auto`. Important local functions are `_cleanup`, `_filter_acls`, `_filter_largeacl`, `check_acls`. Key xfstests/helper interfaces include `_require_test` (requires the configured TEST_DIR filesystem). External or helper commands visible in the body include `grep`, `mkdir`, `rm`, `sed`, `touch`. Significant variables include `ACL_MAX_ENTRIES`, `status`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, `./common/attr`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_cleanup()`; `rm -f $tmp.*`; `[ -n "$TEST_DIR" ] && rm -rf $TEST_DIR/$seq.dir1`; `_require_test`; `_acl_setup_ids`; `_require_acls`; `_require_acl_get_max`.

## State and Persistence Behavior

The test mutates files under `TEST_DIR`. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_acl_get_max`, `_require_acls`, `_require_test`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter`, `./common/attr` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include timing or background-process races can make failures intermittent. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/026 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/027 -->

# sources/test-tools/xfstests/tests/generic/027

## Purpose

Run 8 processes writing 1k files to seperate files in seperate dirs to hit ENOSPC on small fs with little free space. Loop for 100 iterations. Regression test for 34cf865 ext4: fix deadlock when writing in ENOSPC conditions

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest auto enospc`. Important local functions are `create_file`. Key xfstests/helper interfaces include `_scratch_mkfs_sized` (formats a scratch image/device of a requested size), `_scratch_unmount` (unmounts scratch to force persistence checks), `_require_scratch` (requires a disposable scratch filesystem), `_scratch_mount` (mounts the scratch filesystem). External or helper commands visible in the body include `mkdir`, `rm`. Significant variables include `dir`, `loop`, `status`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `mkdir -p $dir >/dev/null 2>&1`; `while $XFS_IO_PROG -f $direct -c "pwrite 0 1k" $dir/file_$i >/dev/null 2>&1; do`; `_require_scratch`; `_require_no_compress`; `echo "Silence is golden"`; `_scratch_mkfs_sized $((256 * 1024 * 1024)) >>$seqres.full 2>&1`; `_scratch_mount`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state, compressed extents or clusters. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_no_compress`, `_require_scratch`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent, compression heuristics may change block layout while preserving user data. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: prints `Silence is golden` after all checks pass; logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/027 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/028 -->

# sources/test-tools/xfstests/tests/generic/028

## Purpose

The following commit introduced a race condition that causes getcwd(2) to return "/" instead of correct path 232d2d6 dcache: Translating dentry into pathname without taking rename_lock These commits fixed the bug ede4ceb prepend_path() needs to reinitialize dentry/vfsmount/mnt on restarts f650080 __dentry_path() fixes

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest auto quick`. No local shell functions are declared. Key xfstests/helper interfaces include `_require_test` (requires the configured TEST_DIR filesystem). No standalone external commands were extracted beyond shell builtins and xfstests helper calls.. Significant variables include `status`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_require_test`; `echo "Silence is golden"`; `$here/src/t_getcwd $TEST_DIR`.

## State and Persistence Behavior

The test mutates files under `TEST_DIR`, mount/unmount state. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_test`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include golden-output drift or unsupported prerequisite handling are the main maintenance risks. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: prints `Silence is golden` after all checks pass. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/028 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/029 -->

# sources/test-tools/xfstests/tests/generic/029

## Purpose

Test mapped writes against truncate down/up to ensure we get the data correctly written. This can expose data corruption bugs on filesystems where the block size is smaller than the page size.

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest auto quick rw mmap`. No local shell functions are declared. Key xfstests/helper interfaces include `_scratch_cycle_mount` (unmounts and remounts scratch to test persisted metadata), `_require_scratch` (requires a disposable scratch filesystem), `_scratch_mount` (mounts the scratch filesystem), `_filter_xfs_io` (normalizes xfs_io output), `_scratch_mkfs` (formats the scratch filesystem). External or helper commands visible in the body include `rm`, `truncate`. Significant variables include `status`, `testfile`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_require_scratch`; `testfile=$SCRATCH_MNT/testfile`; `_scratch_mkfs > /dev/null 2>&1`; `_scratch_mount`; `$XFS_IO_PROG -t -f \`; `echo "==== Pre-Remount ==="`; `_hexdump $testfile`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_scratch`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: passes when required commands complete and the xfstests golden output matches. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/029 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/030 -->

# sources/test-tools/xfstests/tests/generic/030

## Purpose

Test mapped writes against remap+truncate down/up to ensure we get the data correctly written. This can expose data corruption bugs on filesystems where the block size is smaller than the page size.

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest auto quick rw mmap`. No local shell functions are declared. Key xfstests/helper interfaces include `_require_xfs_io_command` (checks xfs_io subcommand support), `_scratch_cycle_mount` (unmounts and remounts scratch to test persisted metadata), `_require_scratch` (requires a disposable scratch filesystem), `_scratch_mount` (mounts the scratch filesystem), `_filter_xfs_io` (normalizes xfs_io output). External or helper commands visible in the body include `rm`, `truncate`. Significant variables include `status`, `testfile`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_require_scratch`; `_require_xfs_io_command "mremap"`; `testfile=$SCRATCH_MNT/testfile`; `_scratch_mkfs > /dev/null 2>&1`; `_scratch_mount`; `$XFS_IO_PROG -t -f \`; `echo "==== Pre-Remount ==="`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_scratch`, `_require_xfs_io_command`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: passes when required commands complete and the xfstests golden output matches. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/030 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/031 -->

# sources/test-tools/xfstests/tests/generic/031

## Purpose

Test non-aligned writes against fcollapse to ensure that partial pages are correctly written and aren't left behind causing invalidation or data corruption issues.

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest auto quick prealloc rw collapse`. No local shell functions are declared. Key xfstests/helper interfaces include `_require_xfs_io_command` (checks xfs_io subcommand support), `_scratch_cycle_mount` (unmounts and remounts scratch to test persisted metadata), `_require_scratch` (requires a disposable scratch filesystem), `_scratch_mount` (mounts the scratch filesystem), `_filter_xfs_io` (normalizes xfs_io output). No standalone external commands were extracted beyond shell builtins and xfstests helper calls.. Significant variables include `status`, `testfile`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_require_scratch`; `_require_xfs_io_command "fcollapse"`; `testfile=$SCRATCH_MNT/testfile`; `_scratch_mkfs > /dev/null 2>&1`; `_scratch_mount`; `_require_congruent_file_oplen $SCRATCH_MNT 4096`; `$XFS_IO_PROG -f \`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_congruent_file_oplen`, `_require_scratch`, `_require_xfs_io_command`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: passes when required commands complete and the xfstests golden output matches. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/031 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/032 -->

# sources/test-tools/xfstests/tests/generic/032

## Purpose

This test implements a data corruption scenario on XFS filesystems with sub-page sized blocks and unwritten extents. Inode lock contention during writeback of pages to unwritten extents leads to failure to convert those extents on I/O completion. This causes data corruption as unwritten extents are always read back as zeroes.

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest auto quick rw fiemap prealloc`. Important local functions are `_cleanup`, `_syncloop`. Key xfstests/helper interfaces include `_require_xfs_io_command` (checks xfs_io subcommand support), `_scratch_cycle_mount` (unmounts and remounts scratch to test persisted metadata), `_require_scratch` (requires a disposable scratch filesystem), `_scratch_mount` (mounts the scratch filesystem), `_filter_fiemap` (normalizes fiemap output). External or helper commands visible in the body include `awk`, `fiemap`, `grep`, `rm`. Significant variables include `status`.

## Control Flow

The script sources `./common/preamble`, `./common/punch`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_cleanup()`; `rm -f $tmp.*`; `_syncloop()`; `while [ true ]; do`; `_scratch_sync`; `_require_scratch`; `_require_xfs_io_command "falloc"`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_scratch`, `_require_xfs_io_command`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/punch` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent, extent layout assumptions can vary by filesystem feature and kernel version. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/032 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/033 -->

# sources/test-tools/xfstests/tests/generic/033

## Purpose

This test stresses indirect block reservation for delayed allocation extents. XFS reserves extra blocks for deferred allocation of delalloc extents. These reserved blocks can be divided among more extents than anticipated if the original extent for which the blocks were reserved is split into multiple delalloc extents. If this scenario repeats, eventually some extents are left without any indirect block reservation whatsoever. This leads to assert failures and possibly other problems in XFS.

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest auto quick rw zero`. No local shell functions are declared. Key xfstests/helper interfaces include `_require_xfs_io_command` (checks xfs_io subcommand support), `_scratch_cycle_mount` (unmounts and remounts scratch to test persisted metadata), `_require_scratch` (requires a disposable scratch filesystem), `_scratch_mount` (mounts the scratch filesystem), `_scratch_mkfs` (formats the scratch filesystem). No standalone external commands were extracted beyond shell builtins and xfstests helper calls.. Significant variables include `file`, `status`.

## Control Flow

The script sources `./common/preamble`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_require_scratch`; `_require_xfs_io_command "fzero"`; `_scratch_mkfs >/dev/null 2>&1`; `_scratch_mount`; `file=$SCRATCH_MNT/file.$seq`; `$XFS_IO_PROG -f -c "pwrite 0 $bytes" $file >> $seqres.full 2>&1`; `for i in $(seq 0 8192 $endoff); do`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_scratch`, `_require_xfs_io_command`. The test integrates with common xfstests libraries through `./common/preamble` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/033 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/034 -->

# sources/test-tools/xfstests/tests/generic/034

## Purpose

This test is motivated by a bug found in btrfs when replaying a directory from the fsync log. The issue was that if a directory entry is both found in the persisted metadata and in the fsync log, at log replay time the directory got set with a wrong i_size. This had the consequence of not being able to rmdir empty directories (failed with errno ENOTEMPTY). This was fixed in btrfs with the following linux kernel patch: Btrfs: fix directory recovery from fsync log

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest auto quick metadata log`. Important local functions are `_cleanup`. Key xfstests/helper interfaces include `_require_dm_target` (requires a device-mapper target), `_scratch_unmount` (unmounts scratch to force persistence checks), `_require_scratch` (requires a disposable scratch filesystem), `_scratch_mount` (mounts the scratch filesystem), `_scratch_mkfs` (formats the scratch filesystem). External or helper commands visible in the body include `mkdir`, `rm`, `touch`. Significant variables include `status`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, `./common/dmflakey`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_cleanup()`; `_cleanup_flakey`; `_require_scratch`; `_require_dm_target flakey`; `_scratch_mkfs >> $seqres.full 2>&1`; `_require_metadata_journaling $SCRATCH_DEV`; `_init_flakey`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state, device-mapper target state. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_dm_target`, `_require_metadata_journaling`, `_require_scratch`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter`, `./common/dmflakey` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: prints `Silence is golden` after all checks pass; logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/034 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/035 -->

# sources/test-tools/xfstests/tests/generic/035

## Purpose

Check overwriting rename system call

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest auto quick`. No local shell functions are declared. Key xfstests/helper interfaces include `_require_test` (requires the configured TEST_DIR filesystem). External or helper commands visible in the body include `mkdir`, `rm`, `touch`. Significant variables include `status`.

## Control Flow

The script sources `./common/preamble`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_require_test`; `_link_out_file`; `rename_dir=$TEST_DIR/$$`; `mkdir -p $rename_dir`; `echo "overwriting regular file:"`; `touch $file1`; `touch $file2`.

## State and Persistence Behavior

The test mutates files under `TEST_DIR`. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_test`. The test integrates with common xfstests libraries through `./common/preamble` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include golden-output drift or unsupported prerequisite handling are the main maintenance risks. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: passes when required commands complete and the xfstests golden output matches. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/035 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/035.cfg -->

# sources/test-tools/xfstests/tests/generic/035.cfg

## Purpose

This small config file supplies extra runtime parameters for `generic/035`. Its complete content is `nfs: nfs`, so it is data rather than executable shell logic.

## Important APIs, Types, and Functions

The interface is the xfstests configuration-file convention for numbered tests. The adjacent shell test reads the file through the harness or direct path handling to select a mount/options variant.

## Control Flow

There is no control flow in this file. The consuming test interprets the single-line option set when it builds its mount or scenario matrix.

## State and Persistence Behavior

The file persists only static test parameters. It creates no scratch files and has no cleanup logic.

## Dependencies and Integration Points

It integrates with `sources/test-tools/xfstests/tests/generic/035` and with the suite Makefile/install process that keeps `.cfg` files beside their matching tests.

## Risks and Edge Cases

Because the content is terse, whitespace or option-name changes can alter the scenario selected by the consuming test. Missing installation of the `.cfg` file can silently reduce coverage for that numbered test.

## Test Signals

The signal is indirect: `generic/035` should run the expected variant and either produce the golden output or skip/fail clearly when the configured option is unsupported.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/035.cfg -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/036 -->

# sources/test-tools/xfstests/tests/generic/036

## Purpose

CVE-2014-8086 Run aio-dio-fcntl-race - test aio write race with O_DIRECT toggle

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest auto aio rw stress`. No local shell functions are declared. Key xfstests/helper interfaces include `_require_test` (requires the configured TEST_DIR filesystem). No standalone external commands were extracted beyond shell builtins and xfstests helper calls.. No prominent persistent shell variables were extracted..

## Control Flow

The script sources `./common/preamble`, `./common/filter`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_require_test`; `_run_aiodio aio-dio-fcntl-race`; `_check_dmesg _filter_aiodio_dmesg`.

## State and Persistence Behavior

The test mutates temporary files under `$tmp.*` and harness result files. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_test`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include golden-output drift or unsupported prerequisite handling are the main maintenance risks. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: passes when required commands complete and the xfstests golden output matches. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/036 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/037 -->

# sources/test-tools/xfstests/tests/generic/037

## Purpose

xfstests shell test generic/037. Its tags are auto, quick, attr, metadata, so it participates in the xfstests harness for filesystem behavior regression coverage.

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest auto quick attr metadata`. Important local functions are `_cleanup`, `set_xattr_loop`, `value_filter`. Key xfstests/helper interfaces include `_require_scratch` (requires a disposable scratch filesystem), `_scratch_mount` (mounts the scratch filesystem), `_require_attrs` (requires extended attribute support), `_scratch_mkfs` (formats the scratch filesystem). External or helper commands visible in the body include `grep`, `rm`, `sed`, `touch`. Significant variables include `status`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, `./common/attr`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_cleanup()`; `rm -f $tmp.*`; `_require_scratch`; `_require_attrs`; `while true; do`; `$SETFATTR_PROG -n $xattr_name -v $cur_val $SCRATCH_MNT/$name`; `if [ "$cur_val" == "$xattr_value1" ]; then`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state, fio verification state for direct/atomic I/O. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_attrs`, `_require_scratch`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter`, `./common/attr` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/037 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/038 -->

# sources/test-tools/xfstests/tests/generic/038

## Purpose

xfstests shell test generic/038. Its tags are auto, stress, trim, prealloc, so it participates in the xfstests harness for filesystem behavior regression coverage.

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest auto stress trim prealloc`. Important local functions are `_cleanup`, `create_files`, `fallocate_loop`, `trim_loop`. Key xfstests/helper interfaces include `_require_xfs_io_command` (checks xfs_io subcommand support), `_require_scratch` (requires a disposable scratch filesystem), `_scratch_mount` (mounts the scratch filesystem), `_scratch_mkfs` (formats the scratch filesystem). External or helper commands visible in the body include `mkdir`, `rm`. Significant variables include `status`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_cleanup()`; `rm -fr $tmp`; `_require_scratch`; `_require_xfs_io_command "falloc"`; `echo "Silence is golden"`; `while true; do`; `$XFS_IO_PROG -f -c "falloc -k 0 1G" \`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_batched_discard`, `_require_fs_space`, `_require_scratch`, `_require_xfs_io_command`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: prints `Silence is golden` after all checks pass; logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/038 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/039 -->

# sources/test-tools/xfstests/tests/generic/039

## Purpose

This test is motivated by an fsync issue discovered in btrfs. The issue was that after fsyncing an inode that got its link count decremented, and the new link count is greater than zero, after the fsync log replay the inode's parent directory metadata became inconsistent - it had a wrong i_size and dangling index entries which prevented the directory from ever being removed (rmdir always failed with -ENOTEMPTY, even if the directory had no more child inodes). The btrfs issue was fixed by the following linux kernel.

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest metadata auto quick log`. Important local functions are `_cleanup`. Key xfstests/helper interfaces include `_require_dm_target` (requires a device-mapper target), `_require_scratch` (requires a disposable scratch filesystem), `_scratch_mount` (mounts the scratch filesystem), `_scratch_mkfs` (formats the scratch filesystem). External or helper commands visible in the body include `ln`, `mkdir`, `rm`. Significant variables include `status`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, `./common/dmflakey`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_cleanup()`; `_cleanup_flakey`; `_require_scratch`; `_require_hardlinks`; `_require_dm_target flakey`; `_scratch_mkfs >> $seqres.full 2>&1`; `_require_metadata_journaling $SCRATCH_DEV`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state, device-mapper target state. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_dm_target`, `_require_hardlinks`, `_require_metadata_journaling`, `_require_scratch`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter`, `./common/dmflakey` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: prints `Silence is golden` after all checks pass; logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/039 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/040 -->

# sources/test-tools/xfstests/tests/generic/040

## Purpose

This test is motivated by an fsync issue discovered in btrfs. The issue in btrfs was that adding a new hard link to an inode that already had a large number of hardlinks and fsync the inode, would make the fsync log replay code update the inode with a wrong link count (smaller than the correct value). This resulted later in dangling directory index entries, after removing most of the hard links (correct_value - wrong_value), that were visible to user space but it was impossible to delete them or do any other.

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest metadata auto quick log`. Important local functions are `_cleanup`. Key xfstests/helper interfaces include `_require_dm_target` (requires a device-mapper target), `_require_scratch` (requires a disposable scratch filesystem), `_scratch_mount` (mounts the scratch filesystem), `_scratch_mkfs` (formats the scratch filesystem). External or helper commands visible in the body include `ln`, `rm`, `stat`. Significant variables include `status`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, `./common/dmflakey`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_cleanup()`; `_cleanup_flakey`; `_require_scratch`; `_require_hardlinks`; `_require_dm_target flakey`; `if [ "$FSTYP" = "btrfs" ]; then`; `_scratch_mkfs "-O extref" >> $seqres.full 2>&1`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state, device-mapper target state. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_dm_target`, `_require_hardlinks`, `_require_metadata_journaling`, `_require_scratch`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter`, `./common/dmflakey` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/040 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/041 -->

# sources/test-tools/xfstests/tests/generic/041

## Purpose

This test is motivated by an fsync issue discovered in btrfs. The steps to trigger the issue were: 1) remove an hard link from an inode with a large number of hard links; 2) add a new hard link; 3) add another hard link with the same name as the one removed in step 1; 4) fsync the inode. These steps made the btrfs fsync log replay fail (with the -EOVERFLOW error), making the filesystem unmountable, requiring the use of btrfs-zero-log (it wipes the fsync log) in order to make the filesystem mountable again (but.

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest metadata auto quick log`. Important local functions are `_cleanup`. Key xfstests/helper interfaces include `_require_dm_target` (requires a device-mapper target), `_require_scratch` (requires a disposable scratch filesystem), `_scratch_mount` (mounts the scratch filesystem), `_scratch_mkfs` (formats the scratch filesystem). External or helper commands visible in the body include `ln`, `rm`, `stat`. Significant variables include `status`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, `./common/dmflakey`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_cleanup()`; `_cleanup_flakey`; `_require_scratch`; `_require_hardlinks`; `_require_dm_target flakey`; `if [ "$FSTYP" = "btrfs" ]; then`; `_scratch_mkfs "-O extref" >> $seqres.full 2>&1`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state, device-mapper target state. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_dm_target`, `_require_hardlinks`, `_require_metadata_journaling`, `_require_scratch`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter`, `./common/dmflakey` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/041 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/042 -->

# sources/test-tools/xfstests/tests/generic/042

## Purpose

Test stale data exposure via writeback using various file allocation modification commands. The presumption is that such commands result in partial writeback and can convert a delayed allocation extent, that might be larger than the ranged affected by fallocate, to a normal extent. If the fs happens to crash sometime between when the extent modification is logged and writeback occurs for dirty pages within the extent but outside of the fallocated range, stale data exposure can occur.

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest shutdown rw punch zero prealloc auto quick`. Important local functions are `_crashtest`. Key xfstests/helper interfaces include `_require_xfs_io_command` (checks xfs_io subcommand support), `_require_scratch` (requires a disposable scratch filesystem), `_scratch_mount` (mounts the scratch filesystem), `_filter_xfs_io` (normalizes xfs_io output), `_scratch_mkfs` (formats the scratch filesystem). External or helper commands visible in the body include `grep`, `mkdir`, `od`. Significant variables include `file`, `size`, `status`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, `./common/punch`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_crashtest()`; `img=$SCRATCH_MNT/$seq.img`; `mnt=$SCRATCH_MNT/$seq.mnt`; `$XFS_IO_PROG -f -c "truncate 0" -c "pwrite -S 0xCD 0 $size" $img \`; `_mkfs_dev $img >> $seqres.full 2>&1`; `mkdir -p $mnt`; `_mount $img $mnt`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_local_device`, `_require_metadata_journaling`, `_require_scratch`, `_require_scratch_shutdown`, `_require_xfs_io_command`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter`, `./common/punch` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/042 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/043 -->

# sources/test-tools/xfstests/tests/generic/043

## Purpose

xfstests shell test generic/043. Its tags are shutdown, metadata, log, auto, fiemap, so it participates in the xfstests harness for filesystem behavior regression coverage.

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest shutdown metadata log auto fiemap`. No local shell functions are declared. Key xfstests/helper interfaces include `_require_xfs_io_command` (checks xfs_io subcommand support), `_check_scratch_fs` (runs scratch filesystem consistency checking), `_scratch_unmount` (unmounts scratch to force persistence checks), `_require_scratch` (requires a disposable scratch filesystem), `_scratch_mount` (mounts the scratch filesystem). External or helper commands visible in the body include `fiemap`, `rm`. Significant variables include `file`, `status`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_require_scratch`; `_require_scratch_shutdown`; `_require_xfs_io_command "fiemap"`; `_scratch_mkfs >/dev/null 2>&1`; `_require_metadata_journaling $SCRATCH_DEV`; `_scratch_mount`; `while [ $i -lt 1000 ]`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_metadata_journaling`, `_require_scratch`, `_require_scratch_shutdown`, `_require_xfs_io_command`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent, extent layout assumptions can vary by filesystem feature and kernel version. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: runs filesystem consistency checking. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/043 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/044 -->

# sources/test-tools/xfstests/tests/generic/044

## Purpose

xfstests shell test generic/044. Its tags are shutdown, metadata, log, auto, fiemap, so it participates in the xfstests harness for filesystem behavior regression coverage.

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest shutdown metadata log auto fiemap`. No local shell functions are declared. Key xfstests/helper interfaces include `_require_xfs_io_command` (checks xfs_io subcommand support), `_check_scratch_fs` (runs scratch filesystem consistency checking), `_scratch_unmount` (unmounts scratch to force persistence checks), `_require_scratch` (requires a disposable scratch filesystem), `_scratch_mount` (mounts the scratch filesystem). External or helper commands visible in the body include `fiemap`, `rm`. Significant variables include `file`, `status`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_require_scratch`; `_require_scratch_shutdown`; `_require_xfs_io_command "fiemap"`; `_scratch_mkfs >/dev/null 2>&1`; `_require_metadata_journaling $SCRATCH_DEV`; `_scratch_mount`; `while [ $i -lt 1000 ]`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_metadata_journaling`, `_require_scratch`, `_require_scratch_shutdown`, `_require_xfs_io_command`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent, extent layout assumptions can vary by filesystem feature and kernel version. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: runs filesystem consistency checking. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/044 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/045 -->

# sources/test-tools/xfstests/tests/generic/045

## Purpose

xfstests shell test generic/045. Its tags are shutdown, metadata, log, auto, fiemap, so it participates in the xfstests harness for filesystem behavior regression coverage.

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest shutdown metadata log auto fiemap`. No local shell functions are declared. Key xfstests/helper interfaces include `_require_xfs_io_command` (checks xfs_io subcommand support), `_check_scratch_fs` (runs scratch filesystem consistency checking), `_scratch_unmount` (unmounts scratch to force persistence checks), `_require_scratch` (requires a disposable scratch filesystem), `_scratch_mount` (mounts the scratch filesystem). External or helper commands visible in the body include `fiemap`, `rm`. Significant variables include `file`, `status`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_require_scratch`; `_require_scratch_shutdown`; `_require_xfs_io_command "fiemap"`; `_scratch_mkfs >/dev/null 2>&1`; `_require_metadata_journaling $SCRATCH_DEV`; `_scratch_mount`; `while [ $i -lt 1000 ]`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_metadata_journaling`, `_require_scratch`, `_require_scratch_shutdown`, `_require_xfs_io_command`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent, extent layout assumptions can vary by filesystem feature and kernel version. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: runs filesystem consistency checking. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/045 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/046 -->

# sources/test-tools/xfstests/tests/generic/046

## Purpose

xfstests shell test generic/046. Its tags are shutdown, metadata, log, auto, fiemap, so it participates in the xfstests harness for filesystem behavior regression coverage.

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest shutdown metadata log auto fiemap`. No local shell functions are declared. Key xfstests/helper interfaces include `_require_xfs_io_command` (checks xfs_io subcommand support), `_check_scratch_fs` (runs scratch filesystem consistency checking), `_scratch_unmount` (unmounts scratch to force persistence checks), `_require_scratch` (requires a disposable scratch filesystem), `_scratch_mount` (mounts the scratch filesystem). External or helper commands visible in the body include `fiemap`, `rm`. Significant variables include `file`, `status`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_require_scratch`; `_require_scratch_shutdown`; `_require_xfs_io_command "fiemap"`; `_scratch_mkfs >/dev/null 2>&1`; `_require_metadata_journaling $SCRATCH_DEV`; `_scratch_mount`; `while [ $i -lt 1000 ]`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_metadata_journaling`, `_require_scratch`, `_require_scratch_shutdown`, `_require_xfs_io_command`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent, extent layout assumptions can vary by filesystem feature and kernel version. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: runs filesystem consistency checking. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/046 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/047 -->

# sources/test-tools/xfstests/tests/generic/047

## Purpose

xfstests shell test generic/047. Its tags are shutdown, metadata, rw, auto, fiemap, so it participates in the xfstests harness for filesystem behavior regression coverage.

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest shutdown metadata rw auto fiemap`. Important local functions are `_check_files`. Key xfstests/helper interfaces include `_require_xfs_io_command` (checks xfs_io subcommand support), `_check_scratch_fs` (runs scratch filesystem consistency checking), `_scratch_unmount` (unmounts scratch to force persistence checks), `_require_scratch` (requires a disposable scratch filesystem), `_scratch_mount` (mounts the scratch filesystem). External or helper commands visible in the body include `fiemap`, `fsync`, `ls`, `rm`. Significant variables include `file`, `status`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_require_scratch`; `_require_scratch_shutdown`; `_require_xfs_io_command "fiemap"`; `_scratch_mkfs >/dev/null 2>&1`; `_require_metadata_journaling $SCRATCH_DEV`; `_scratch_mount`; `_check_files()`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_metadata_journaling`, `_require_scratch`, `_require_scratch_shutdown`, `_require_xfs_io_command`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent, extent layout assumptions can vary by filesystem feature and kernel version. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: runs filesystem consistency checking. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/047 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/048 -->

# sources/test-tools/xfstests/tests/generic/048

## Purpose

xfstests shell test generic/048. Its tags are shutdown, metadata, rw, auto, fiemap, so it participates in the xfstests harness for filesystem behavior regression coverage.

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest shutdown metadata rw auto fiemap`. Important local functions are `_check_files`. Key xfstests/helper interfaces include `_require_xfs_io_command` (checks xfs_io subcommand support), `_check_scratch_fs` (runs scratch filesystem consistency checking), `_scratch_unmount` (unmounts scratch to force persistence checks), `_require_scratch` (requires a disposable scratch filesystem), `_scratch_mount` (mounts the scratch filesystem). External or helper commands visible in the body include `fiemap`, `ls`, `rm`, `sync`. Significant variables include `file`, `status`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_require_scratch`; `_require_scratch_shutdown`; `_require_xfs_io_command "fiemap"`; `_scratch_mkfs >/dev/null 2>&1`; `_require_metadata_journaling $SCRATCH_DEV`; `_scratch_mount`; `_require_fs_space $SCRATCH_MNT 10485760`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_fs_space`, `_require_metadata_journaling`, `_require_scratch`, `_require_scratch_shutdown`, `_require_xfs_io_command`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent, extent layout assumptions can vary by filesystem feature and kernel version. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: runs filesystem consistency checking. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/048 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/049 -->

# sources/test-tools/xfstests/tests/generic/049

## Purpose

xfstests shell test generic/049. Its tags are shutdown, metadata, rw, auto, fiemap, so it participates in the xfstests harness for filesystem behavior regression coverage.

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest shutdown metadata rw auto fiemap`. Important local functions are `_check_files`. Key xfstests/helper interfaces include `_require_xfs_io_command` (checks xfs_io subcommand support), `_check_scratch_fs` (runs scratch filesystem consistency checking), `_scratch_unmount` (unmounts scratch to force persistence checks), `_require_scratch` (requires a disposable scratch filesystem), `_scratch_mount` (mounts the scratch filesystem). External or helper commands visible in the body include `fiemap`, `ls`, `rm`, `sync`. Significant variables include `file`, `status`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_require_scratch`; `_require_scratch_shutdown`; `_require_xfs_io_command "fiemap"`; `_scratch_mkfs >/dev/null 2>&1`; `_require_metadata_journaling $SCRATCH_DEV`; `_scratch_mount`; `_check_files()`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_metadata_journaling`, `_require_scratch`, `_require_scratch_shutdown`, `_require_xfs_io_command`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent, extent layout assumptions can vary by filesystem feature and kernel version. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: runs filesystem consistency checking; logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/049 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/050 -->

# sources/test-tools/xfstests/tests/generic/050

## Purpose

Check out various mount/remount/unmount scenarious on a read-only blockdev.

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest shutdown mount auto quick`. Important local functions are `_cleanup`. Key xfstests/helper interfaces include `_require_scratch_nocheck` (requires scratch without pre-run fsck validation), `_try_scratch_mount` (attempts to mount scratch and lets the test decide skip/fail behavior), `_scratch_unmount` (unmounts scratch to force persistence checks), `_filter_scratch` (normalizes scratch paths in stdout), `_scratch_mkfs` (formats the scratch filesystem). External or helper commands visible in the body include `blockdev`, `grep`, `mount`, `touch`. Significant variables include `status`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_cleanup()`; `blockdev --setrw $SCRATCH_DEV`; `_require_scratch_nocheck`; `_require_scratch_shutdown`; `_require_local_device $SCRATCH_DEV`; `_require_norecovery`; `if ! _has_metadata_journaling $SCRATCH_DEV >/dev/null; then`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state, quota/project-id metadata. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_local_device`, `_require_norecovery`, `_require_scratch_nocheck`, `_require_scratch_shutdown`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: passes when required commands complete and the xfstests golden output matches. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/050 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/050.cfg -->

# sources/test-tools/xfstests/tests/generic/050.cfg

## Purpose

This small config file supplies extra runtime parameters for `generic/050`. Its complete content is `nojournal: nojournal; xfsquota: xfsquota`, so it is data rather than executable shell logic.

## Important APIs, Types, and Functions

The interface is the xfstests configuration-file convention for numbered tests. The adjacent shell test reads the file through the harness or direct path handling to select a mount/options variant.

## Control Flow

There is no control flow in this file. The consuming test interprets the single-line option set when it builds its mount or scenario matrix.

## State and Persistence Behavior

The file persists only static test parameters. It creates no scratch files and has no cleanup logic.

## Dependencies and Integration Points

It integrates with `sources/test-tools/xfstests/tests/generic/050` and with the suite Makefile/install process that keeps `.cfg` files beside their matching tests.

## Risks and Edge Cases

Because the content is terse, whitespace or option-name changes can alter the scenario selected by the consuming test. Missing installation of the `.cfg` file can silently reduce coverage for that numbered test.

## Test Signals

The signal is indirect: `generic/050` should run the expected variant and either produce the golden output or skip/fail clearly when the configured option is unsupported.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/050.cfg -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/051 -->

# sources/test-tools/xfstests/tests/generic/051

## Purpose

Basic log recovery stress test - do lots of stuff, shut down in the middle of it and check that recovery runs to completion and everything can be successfully removed afterwards..

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest shutdown auto stress log metadata repair`. No local shell functions are declared. Key xfstests/helper interfaces include `_check_scratch_fs` (runs scratch filesystem consistency checking), `_scratch_unmount` (unmounts scratch to force persistence checks), `_require_scratch` (requires a disposable scratch filesystem), `_scratch_mount` (mounts the scratch filesystem), `_scratch_mkfs` (formats the scratch filesystem). External or helper commands visible in the body include `rm`. Significant variables include `PROCS`, `SLEEP_TIME`, `status`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_require_scratch`; `_require_scratch_shutdown`; `_scratch_mkfs > $seqres.full 2>&1`; `_require_metadata_journaling $SCRATCH_DEV`; `_scratch_mount`; `load_dir=$SCRATCH_MNT/test`; `_run_fsstress_bg -n 10000000 -p $PROCS -d $load_dir`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_metadata_journaling`, `_require_scratch`, `_require_scratch_shutdown`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent, stress-tool behavior and kernel timing can expose nondeterminism. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: runs filesystem consistency checking; logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/051 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/052 -->

# sources/test-tools/xfstests/tests/generic/052

## Purpose

To test log replay by shutdown of file system This is the first simple initial test to ensure that the goingdown ioctl is working and recovery of create transactions is working.

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest shutdown log auto quick`. No local shell functions are declared. Key xfstests/helper interfaces include `_try_scratch_mount` (attempts to mount scratch and lets the test decide skip/fail behavior), `_check_scratch_fs` (runs scratch filesystem consistency checking), `_scratch_unmount` (unmounts scratch to force persistence checks), `_require_scratch` (requires a disposable scratch filesystem), `_scratch_mount` (mounts the scratch filesystem). External or helper commands visible in the body include `ls`, `mount`, `rm`, `touch`. Significant variables include `status`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, `./common/log`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `rm -f $tmp.log`; `_require_scratch`; `_require_scratch_shutdown`; `_require_logstate`; `echo "mkfs"`; `_scratch_mkfs >>$seqres.full 2>&1 \`; `_require_metadata_journaling $SCRATCH_DEV`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_logstate`, `_require_metadata_journaling`, `_require_scratch`, `_require_scratch_shutdown`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter`, `./common/log` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: runs filesystem consistency checking; logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/052 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/053 -->

# sources/test-tools/xfstests/tests/generic/053

## Purpose

xfs_repair breaks acls

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest acl repair auto quick`. Important local functions are `list_acls`. Key xfstests/helper interfaces include `_try_scratch_mount` (attempts to mount scratch and lets the test decide skip/fail behavior), `_check_scratch_fs` (runs scratch filesystem consistency checking), `_require_scratch` (requires a disposable scratch filesystem), `_scratch_mkfs` (formats the scratch filesystem). External or helper commands visible in the body include `sed`. Significant variables include `status`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, `./common/attr`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_require_scratch`; `_require_acls`; `_acl_setup_ids`; `_do_die_on_error=y`; `test=$SCRATCH_MNT/test`; `_do 'make filesystem on $SCRATCH_DEV' '_scratch_mkfs'`; `_do 'mount filesytem' '_try_scratch_mount'`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_acls`, `_require_scratch`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter`, `./common/attr` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: runs filesystem consistency checking. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/053 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/054 -->

# sources/test-tools/xfstests/tests/generic/054

## Purpose

To test log replay with version 2 logs Initially keep this simple with just creates. In another qa test we can do more e.g. use fsstress.

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest shutdown log v2log auto`. No local shell functions are declared. Key xfstests/helper interfaces include `_try_scratch_mount` (attempts to mount scratch and lets the test decide skip/fail behavior), `_check_scratch_fs` (runs scratch filesystem consistency checking), `_scratch_unmount` (unmounts scratch to force persistence checks), `_require_scratch` (requires a disposable scratch filesystem), `_scratch_mkfs` (formats the scratch filesystem). External or helper commands visible in the body include `ls`, `mkfs`, `mount`, `sync`, `touch`. Significant variables include `status`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, `./common/log`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_require_scratch`; `_require_scratch_shutdown`; `_require_logstate`; `echo "*** init FS"`; `_scratch_unmount >/dev/null 2>&1`; `_scratch_mkfs >/dev/null 2>&1`; `_require_metadata_journaling $SCRATCH_DEV`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_logstate`, `_require_metadata_journaling`, `_require_scratch`, `_require_scratch_shutdown`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter`, `./common/log` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent, stress-tool behavior and kernel timing can expose nondeterminism. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: runs filesystem consistency checking; logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/054 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/055 -->

# sources/test-tools/xfstests/tests/generic/055

## Purpose

* like 054 but want to create more/different kinds of metadata and so will use fsstress * also can interrupt metadata with godown

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest shutdown log v2log auto quota stress`. Important local functions are `_do_meta`, `_get_quota_option`. Key xfstests/helper interfaces include `_try_scratch_mount` (attempts to mount scratch and lets the test decide skip/fail behavior), `_check_scratch_fs` (runs scratch filesystem consistency checking), `_scratch_unmount` (unmounts scratch to force persistence checks), `_require_scratch` (requires a disposable scratch filesystem), `_scratch_mkfs` (formats the scratch filesystem). External or helper commands visible in the body include `diff`, `fsstress`, `ls`, `mkfs`, `mount`, `sed`. Significant variables include `FSSTRESS_ARGS`, `QUOTA_OPTION`, `status`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, `./common/log`, `./common/quota`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_do_meta()`; `out=$SCRATCH_MNT/fsstress`; `_echofull "calling fsstress $param -m8 -n $count"`; `_run_fsstress $FSSTRESS_ARGS`; `if [ $? -ne 0 ]; then`; `_echofull "fsstress failed"`; `_get_quota_option()`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state, quota/project-id metadata. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_logstate`, `_require_metadata_journaling`, `_require_scratch`, `_require_scratch_shutdown`, `_require_xfs_quota`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter`, `./common/log`, `./common/quota` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent, stress-tool behavior and kernel timing can expose nondeterminism. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: uses byte-for-byte comparison of generated and expected data; runs filesystem consistency checking; logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/055 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/056 -->

# sources/test-tools/xfstests/tests/generic/056

## Purpose

This test is motivated by an fsync issue discovered in btrfs. The issue was that we could lose file data, that was previously fsync'ed successfully, if we end up adding a hard link to our inode and then persist the fsync log later via an fsync of other inode for example. The btrfs issue was fixed by the following linux kernel patch: Btrfs: fix fsync data loss after adding hard link to inode

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest metadata auto quick log`. Important local functions are `_cleanup`. Key xfstests/helper interfaces include `_require_dm_target` (requires a device-mapper target), `_require_scratch` (requires a disposable scratch filesystem), `_scratch_mount` (mounts the scratch filesystem), `_filter_xfs_io` (normalizes xfs_io output), `_scratch_mkfs` (formats the scratch filesystem). External or helper commands visible in the body include `ln`, `od`, `rm`, `touch`. Significant variables include `status`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, `./common/dmflakey`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_cleanup()`; `_cleanup_flakey`; `rm -f $tmp.*`; `_require_scratch`; `_require_hardlinks`; `_require_dm_target flakey`; `_scratch_mkfs >> $seqres.full 2>&1`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state, device-mapper target state. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_dm_target`, `_require_hardlinks`, `_require_metadata_journaling`, `_require_scratch`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter`, `./common/dmflakey` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/056 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/057 -->

# sources/test-tools/xfstests/tests/generic/057

## Purpose

This test is motivated by an fsync issue discovered in btrfs. The issue was that we could lose file data, that was previously fsync'ed successfully, if we end up adding a hard link to our inode and then persist the fsync log later via an fsync of other inode for example. The btrfs issue was fixed by the following linux kernel patch: Btrfs: fix fsync data loss after adding hard link to inode

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest metadata auto quick log`. Important local functions are `_cleanup`. Key xfstests/helper interfaces include `_require_dm_target` (requires a device-mapper target), `_require_scratch` (requires a disposable scratch filesystem), `_scratch_mount` (mounts the scratch filesystem), `_filter_xfs_io` (normalizes xfs_io output), `_scratch_mkfs` (formats the scratch filesystem). External or helper commands visible in the body include `ln`, `od`, `rm`, `touch`. Significant variables include `status`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, `./common/dmflakey`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_cleanup()`; `_cleanup_flakey`; `rm -f $tmp.*`; `_require_scratch`; `_require_hardlinks`; `_require_dm_target flakey`; `_scratch_mkfs >> $seqres.full 2>&1`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state, device-mapper target state. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_dm_target`, `_require_hardlinks`, `_require_metadata_journaling`, `_require_scratch`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter`, `./common/dmflakey` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/057 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/058 -->

# sources/test-tools/xfstests/tests/generic/058

## Purpose

Standard insert range tests This testcase is one of the 4 testcases which tries to test various corner cases for finsert range functionality over different type of extents. These tests are based on generic/255 test case. For the type of tests, check the description of _test_generic_punch in common/rc.

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest auto quick prealloc punch insert fiemap`. No local shell functions are declared. Key xfstests/helper interfaces include `_require_xfs_io_command` (checks xfs_io subcommand support). External or helper commands visible in the body include `fiemap`. Significant variables include `status`, `testfile`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, `./common/punch`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_require_xfs_io_command "fpunch"`; `_require_xfs_io_command "falloc"`; `_require_xfs_io_command "fiemap"`; `_require_xfs_io_command "finsert"`; `testfile=$TEST_DIR/$seq.$$`; `_test_generic_punch falloc fpunch finsert fiemap _filter_hole_fiemap $testfile`; `_check_test_fs`.

## State and Persistence Behavior

The test mutates files under `TEST_DIR`. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_xfs_io_command`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter`, `./common/punch` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include extent layout assumptions can vary by filesystem feature and kernel version. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: passes when required commands complete and the xfstests golden output matches. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/058 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/059 -->

# sources/test-tools/xfstests/tests/generic/059

## Purpose

This test is motivated by an fsync issue discovered in btrfs. The issue was that after punching a hole for a small range, which affected only a partial page, an fsync operation would have no effect at all. This was because for this particular case the btrfs hole punching implementation did not update some btrfs specific inode metadata that is required to determine if an fsync operation needs to update the fsync log. For this to happen, it was also necessary that in the transaction where the hole punching was.

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest metadata auto quick punch log`. Important local functions are `_cleanup`. Key xfstests/helper interfaces include `_require_xfs_io_command` (checks xfs_io subcommand support), `_require_dm_target` (requires a device-mapper target), `_require_scratch` (requires a disposable scratch filesystem), `_scratch_mount` (mounts the scratch filesystem), `_filter_xfs_io` (normalizes xfs_io output). External or helper commands visible in the body include `od`, `rm`, `stat`. Significant variables include `status`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, `./common/dmflakey`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_cleanup()`; `_cleanup_flakey`; `rm -f $tmp.*`; `_require_scratch`; `_require_dm_target flakey`; `_require_xfs_io_command "fpunch"`; `_scratch_mkfs >> $seqres.full 2>&1`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state, device-mapper target state. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_dm_target`, `_require_metadata_journaling`, `_require_scratch`, `_require_xfs_io_command`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter`, `./common/dmflakey` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/059 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/060 -->

# sources/test-tools/xfstests/tests/generic/060

## Purpose

Delayed allocation insert range tests This testcase is one of the 4 testcases which tries to test various corner cases for finsert range functionality over different type of extents. These tests are based on generic/255 test case. For the type of tests, check the description of _test_generic_punch in common/rc.

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest auto quick prealloc punch insert fiemap`. No local shell functions are declared. Key xfstests/helper interfaces include `_require_xfs_io_command` (checks xfs_io subcommand support). External or helper commands visible in the body include `fiemap`. Significant variables include `status`, `testfile`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, `./common/punch`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_require_xfs_io_command "fpunch"`; `_require_xfs_io_command "falloc"`; `_require_xfs_io_command "fiemap"`; `_require_xfs_io_command "finsert"`; `testfile=$TEST_DIR/$seq.$$`; `_test_generic_punch -d falloc fpunch finsert fiemap _filter_hole_fiemap $testfile`; `_check_test_fs`.

## State and Persistence Behavior

The test mutates files under `TEST_DIR`. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_xfs_io_command`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter`, `./common/punch` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include extent layout assumptions can vary by filesystem feature and kernel version. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: passes when required commands complete and the xfstests golden output matches. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/060 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/061 -->

# sources/test-tools/xfstests/tests/generic/061

## Purpose

Multi insert range tests This testcase is one of the 4 testcases which tries to test various corner cases for finsert range functionality over different type of extents. These tests are based on generic/255 test case. For the type of tests, check the description of _test_generic_punch in common/rc.

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest auto quick prealloc punch insert fiemap`. No local shell functions are declared. Key xfstests/helper interfaces include `_require_xfs_io_command` (checks xfs_io subcommand support). External or helper commands visible in the body include `fiemap`. Significant variables include `status`, `testfile`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, `./common/punch`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_require_xfs_io_command "fpunch"`; `_require_xfs_io_command "falloc"`; `_require_xfs_io_command "fiemap"`; `_require_xfs_io_command "finsert"`; `testfile=$TEST_DIR/$seq.$$`; `_test_generic_punch -k falloc fpunch finsert fiemap _filter_hole_fiemap $testfile`; `_check_test_fs`.

## State and Persistence Behavior

The test mutates files under `TEST_DIR`. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_xfs_io_command`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter`, `./common/punch` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include extent layout assumptions can vary by filesystem feature and kernel version. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: passes when required commands complete and the xfstests golden output matches. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/061 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/062 -->

# sources/test-tools/xfstests/tests/generic/062

## Purpose

Exercises the getfattr/setfattr tools Derived from tests originally written by Andreas Gruenbacher for ext2

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest attr udf auto quick`. Important local functions are `_backup`, `_cleanup`, `_create_test_bed`, `_extend_test_bed`, `getfattr`, `invalid_attribute_filter`, and others. Key xfstests/helper interfaces include `_scratch_unmount` (unmounts scratch to force persistence checks), `_require_scratch` (requires a disposable scratch filesystem), `_filter_scratch` (normalizes scratch paths in stdout), `_scratch_mount` (mounts the scratch filesystem), `_require_attrs` (requires extended attribute support). External or helper commands visible in the body include `cp`, `diff`, `find`, `grep`, `ln`, `mkdir`, `rm`, `sed`, `touch`. Significant variables include `ATTR_FILTER`, `ATTR_MODES`, `status`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, `./common/attr`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_cleanup()`; `echo; echo "*** unmount"`; `_scratch_unmount 2>/dev/null`; `rm -f $tmp.*`; `_getfattr --absolute-names -dh $@ 2>&1 | _filter_scratch`; `_create_test_bed()`; `echo "*** create test bed"`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_attrs`, `_require_mknod`, `_require_scratch`, `_require_symlinks`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter`, `./common/attr` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: uses byte-for-byte comparison of generated and expected data; logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/062 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/063 -->

# sources/test-tools/xfstests/tests/generic/063

## Purpose

Delayed allocation multi insert range tests This testcase is one of the 4 testcases which tries to test various corner cases for finsert range functionality over different type of extents. These tests are based on generic/255 test case. For the type of tests, check the description of _test_generic_punch in common/rc.

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest auto quick prealloc punch insert fiemap`. No local shell functions are declared. Key xfstests/helper interfaces include `_require_xfs_io_command` (checks xfs_io subcommand support). External or helper commands visible in the body include `fiemap`. Significant variables include `status`, `testfile`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, `./common/punch`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_require_xfs_io_command "fpunch"`; `_require_xfs_io_command "falloc"`; `_require_xfs_io_command "fiemap"`; `_require_xfs_io_command "finsert"`; `testfile=$TEST_DIR/$seq.$$`; `_test_generic_punch -d -k falloc fpunch finsert fiemap _filter_hole_fiemap $testfile`; `_check_test_fs`.

## State and Persistence Behavior

The test mutates files under `TEST_DIR`. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_xfs_io_command`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter`, `./common/punch` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include extent layout assumptions can vary by filesystem feature and kernel version. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: passes when required commands complete and the xfstests golden output matches. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/063 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/064 -->

# sources/test-tools/xfstests/tests/generic/064

## Purpose

Test multiple fallocate insert/collapse range calls on same file. Call insert range on alternate blocks multiple times until the file is left with 50 extents and as many holes. Then call collapse range on the previously inserted ranges to test merge code of collapse range. Also check for data integrity and file system consistency.

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest auto quick prealloc collapse insert fiemap`. No local shell functions are declared. Key xfstests/helper interfaces include `_require_xfs_io_command` (checks xfs_io subcommand support), `_check_scratch_fs` (runs scratch filesystem consistency checking), `_require_scratch` (requires a disposable scratch filesystem), `_scratch_mount` (mounts the scratch filesystem), `_scratch_mkfs` (formats the scratch filesystem). External or helper commands visible in the body include `cmp`, `cp`, `fiemap`, `fsync`. Significant variables include `BLOCKS`, `BSIZE`, `status`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_require_scratch`; `_require_xfs_io_command "fiemap"`; `_require_xfs_io_command "finsert"`; `_require_xfs_io_command "fcollapse"`; `_scratch_mkfs >> $seqres.full 2>&1 || _fail "mkfs failed"`; `_scratch_mount`; `src=$SCRATCH_MNT/testfile`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_scratch`, `_require_xfs_io_command`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent, extent layout assumptions can vary by filesystem feature and kernel version. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: uses byte-for-byte comparison of generated and expected data; runs filesystem consistency checking; logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/064 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/065 -->

# sources/test-tools/xfstests/tests/generic/065

## Purpose

Test fsync on directories that got new hardlinks added to them and that point to existing inodes. The goal is to verify that after the fsync log is replayed the new hardlinks exist and the inodes have a correct link count. Also test that new hardlinks pointing to new inodes are logged and exist as well after the fsync log is replayed. This test is motivated by an issue discovered in btrfs, where the inode link counts were incorrect after the fsync log was replayed and the hardlinks for new inodes were not logged.

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest metadata auto quick log`. Important local functions are `_cleanup`. Key xfstests/helper interfaces include `_require_dm_target` (requires a device-mapper target), `_require_scratch` (requires a disposable scratch filesystem), `_scratch_mount` (mounts the scratch filesystem), `_filter_xfs_io` (normalizes xfs_io output), `_scratch_mkfs` (formats the scratch filesystem). External or helper commands visible in the body include `ln`, `mkdir`, `od`, `rm`, `stat`, `touch`. Significant variables include `status`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, `./common/dmflakey`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_cleanup()`; `_cleanup_flakey`; `rm -f $tmp.*`; `_require_scratch`; `_require_hardlinks`; `_require_dm_target flakey`; `_scratch_mkfs >> $seqres.full 2>&1`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state, device-mapper target state. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_dm_target`, `_require_hardlinks`, `_require_metadata_journaling`, `_require_scratch`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter`, `./common/dmflakey` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/065 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/066 -->

# sources/test-tools/xfstests/tests/generic/066

## Purpose

This test is motivated by an fsync issue discovered in btrfs. The issue was that the fsync log replay code did not remove xattrs that were deleted before the inode was fsynced. So verify that if we delete a xattr from a file and then fsync the file, after log replay the file does not have that xattr anymore. Also test the case where a file is fsynced, one of its xattrs is removed, a hard link to that file is created and the fsync log is committed by issuing an fsync on another file. This indirect case should also.

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest auto quick attr metadata log`. Important local functions are `_cleanup`. Key xfstests/helper interfaces include `_require_dm_target` (requires a device-mapper target), `_scratch_unmount` (unmounts scratch to force persistence checks), `_require_scratch` (requires a disposable scratch filesystem), `_filter_scratch` (normalizes scratch paths in stdout), `_scratch_mount` (mounts the scratch filesystem). External or helper commands visible in the body include `fsync`, `ln`, `rm`, `touch`. Significant variables include `status`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, `./common/dmflakey`, `./common/attr`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_cleanup()`; `_cleanup_flakey`; `rm -f $tmp.*`; `_require_scratch`; `_require_dm_target flakey`; `_require_attrs`; `_scratch_mkfs >> $seqres.full 2>&1`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state, device-mapper target state. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_attrs`, `_require_dm_target`, `_require_metadata_journaling`, `_require_scratch`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter`, `./common/dmflakey`, `./common/attr` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/066 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/067 -->

# sources/test-tools/xfstests/tests/generic/067

## Purpose

Some random mount/umount corner case tests - mount at a nonexistent mount point - mount a free loop device - mount with a wrong fs type specified - umount an symlink to device which is not mounted - umount a path with too long name - lazy umount a symlink

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest auto quick mount`. Important local functions are `lazy_umount_symlink`, `mount_free_loopdev`, `mount_nonexistent_mnt`, `mount_wrong_fstype`, `umount_symlink_device`, `umount_toolong_name`, and others. Key xfstests/helper interfaces include `_scratch_unmount` (unmounts scratch to force persistence checks), `_require_scratch` (requires a disposable scratch filesystem), `_scratch_mount` (mounts the scratch filesystem), `_scratch_mkfs` (formats the scratch filesystem), `_require_test` (requires the configured TEST_DIR filesystem). External or helper commands visible in the body include `ln`, `losetup`, `mkdir`, `mount`, `rm`, `umount`. Significant variables include `status`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_require_symlinks`; `_require_test`; `_require_scratch`; `_require_loop`; `_require_block_device $SCRATCH_DEV`; `_scratch_mkfs >>$seqres.full 2>&1`; `echo "# mount to nonexistent mount point" >>$seqres.full`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, files under `TEST_DIR`, mount/unmount state. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_block_device`, `_require_loop`, `_require_scratch`, `_require_symlinks`, `_require_test`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: prints `Silence is golden` after all checks pass; logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/067 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/068 -->

# sources/test-tools/xfstests/tests/generic/068

## Purpose

xfstests shell test generic/068. Its tags are other, auto, freeze, stress, mmap, so it participates in the xfstests harness for filesystem behavior regression coverage.

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest other auto freeze stress mmap`. Important local functions are `_cleanup`. Key xfstests/helper interfaces include `_scratch_unmount` (unmounts scratch to force persistence checks), `_require_scratch` (requires a disposable scratch filesystem), `_scratch_mount` (mounts the scratch filesystem), `_scratch_mkfs` (formats the scratch filesystem). External or helper commands visible in the body include `mkdir`, `rm`, `touch`. Significant variables include `FSSTRESS_ARGS`, `FSTEST_DIR`, `ITERATIONS`, `STRESS_DIR`, `status`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_cleanup()`; `xfs_freeze -u $SCRATCH_MNT 2>/dev/null`; `_kill_fsstress`; `rm -f $tmp.*`; `_require_scratch`; `_require_freeze`; `echo "*** init FS"`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_freeze`, `_require_scratch`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent, stress-tool behavior and kernel timing can expose nondeterminism. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/068 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/069 -->

# sources/test-tools/xfstests/tests/generic/069

## Purpose

Test out writes with O_APPEND flag sets.

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest rw udf auto quick`. No local shell functions are declared. Key xfstests/helper interfaces include `_scratch_unmount` (unmounts scratch to force persistence checks), `_require_scratch` (requires a disposable scratch filesystem), `_scratch_mount` (mounts the scratch filesystem), `_scratch_mkfs` (formats the scratch filesystem). External or helper commands visible in the body include `ls`, `mount`. Significant variables include `status`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_require_scratch`; `_scratch_unmount >/dev/null 2>&1`; `echo "*** mkfs"`; `_scratch_mkfs >/dev/null 2>&1 || _fail "mkfs failed"`; `echo "*** mount FS"`; `_scratch_mount`; `cd $SCRATCH_MNT`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_scratch`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/069 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/070 -->

# sources/test-tools/xfstests/tests/generic/070

## Purpose

fsstress incarnation testing extended attributes writes

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest attr udf auto quick stress`. No local shell functions are declared. Key xfstests/helper interfaces include `_require_attrs` (requires extended attribute support), `_require_test` (requires the configured TEST_DIR filesystem). External or helper commands visible in the body include `rm`. Significant variables include `FSSTRESS_ARGS`, `status`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, `./common/attr`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_require_test`; `_require_attrs`; `-d $TEST_DIR/fsstress \`; `_run_fsstress $FSSTRESS_ARGS`; `rm -rf $TEST_DIR/fsstress`.

## State and Persistence Behavior

The test mutates files under `TEST_DIR`. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_attrs`, `_require_test`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter`, `./common/attr` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include stress-tool behavior and kernel timing can expose nondeterminism. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: passes when required commands complete and the xfstests golden output matches. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/070 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/071 -->

# sources/test-tools/xfstests/tests/generic/071

## Purpose

Test extent pre-allocation (using fallocate) into a region that already has a pre-allocated extent that ends beyond the file's size. Verify that if the fs is unmounted immediately after, the file's size and content are not lost.

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest auto quick prealloc`. No local shell functions are declared. Key xfstests/helper interfaces include `_require_xfs_io_command` (checks xfs_io subcommand support), `_scratch_cycle_mount` (unmounts and remounts scratch to test persisted metadata), `_require_scratch` (requires a disposable scratch filesystem), `_scratch_mount` (mounts the scratch filesystem), `_filter_xfs_io` (normalizes xfs_io output). External or helper commands visible in the body include `od`. Significant variables include `status`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_require_scratch`; `_require_xfs_io_command "falloc" "-k"`; `_scratch_mkfs >> $seqres.full 2>&1`; `_scratch_mount`; `$XFS_IO_PROG -f -c "falloc -k 0 1M" $SCRATCH_MNT/foo`; `$XFS_IO_PROG -c "pwrite -S 0xaa 0 256K" $SCRATCH_MNT/foo | _filter_xfs_io`; `$XFS_IO_PROG -c "falloc 0 512K" $SCRATCH_MNT/foo`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_scratch`, `_require_xfs_io_command`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/071 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/072 -->

# sources/test-tools/xfstests/tests/generic/072

## Purpose

Test truncate/collapse range race. And this test is also a regression test for kernel commit 23fffa9, fs: move falloc collapse range check into the filesystem methods If the race occurs, it will trigger a BUG_ON().

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest auto metadata stress collapse`. No local shell functions are declared. Key xfstests/helper interfaces include `_require_xfs_io_command` (checks xfs_io subcommand support), `_require_test` (requires the configured TEST_DIR filesystem). No standalone external commands were extracted beyond shell builtins and xfstests helper calls.. Significant variables include `INNER_LOOPS`, `NCPUS`, `OUTER_LOOPS`, `status`, `testfile`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_require_test`; `_require_xfs_io_command "fcollapse"`; `testfile=$TEST_DIR/testfile.$seq`; `if [ $NCPUS -gt 8 ]; then`; `for ((i=1; i <= OUTER_LOOPS; i++)); do`; `for ((i=1; i <= INNER_LOOPS; i++)); do`; `$XFS_IO_PROG -f -c 'truncate 100k' \`.

## State and Persistence Behavior

The test mutates files under `TEST_DIR`. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_test`, `_require_xfs_io_command`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include timing or background-process races can make failures intermittent. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: prints `Silence is golden` after all checks pass. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/072 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/073 -->

# sources/test-tools/xfstests/tests/generic/073

## Purpose

Test file A fsync after moving one other unrelated file B between directories and fsyncing B's old parent directory before fsyncing the file A. Check that after a crash all the file A data we fsynced is available. This test is motivated by an issue discovered in btrfs which caused the file data to be lost (despite fsync returning success to user space). That btrfs bug was fixed by the following linux kernel patch: Btrfs: fix data loss in the fast fsync path

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest metadata auto quick log`. Important local functions are `_cleanup`. Key xfstests/helper interfaces include `_require_dm_target` (requires a device-mapper target), `_require_scratch` (requires a disposable scratch filesystem), `_scratch_mount` (mounts the scratch filesystem), `_filter_xfs_io` (normalizes xfs_io output), `_scratch_mkfs` (formats the scratch filesystem). External or helper commands visible in the body include `mkdir`, `mv`, `od`, `rm`, `touch`. Significant variables include `status`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, `./common/dmflakey`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_cleanup()`; `_cleanup_flakey`; `rm -f $tmp.*`; `_require_scratch`; `_require_dm_target flakey`; `_scratch_mkfs >> $seqres.full 2>&1`; `_require_metadata_journaling $SCRATCH_DEV`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state, device-mapper target state. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_dm_target`, `_require_metadata_journaling`, `_require_scratch`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter`, `./common/dmflakey` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/073 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/074 -->

# sources/test-tools/xfstests/tests/generic/074

## Purpose

fstest

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest rw udf auto mmap`. Important local functions are `_cleanup`, `_do_test`, `_process_args`, `_usage`. Key xfstests/helper interfaces include `_require_test` (requires the configured TEST_DIR filesystem). External or helper commands visible in the body include `grep`, `mkdir`, `rm`. Significant variables include `OPTIND`, `status`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `fstest_dir=$TEST_DIR/fstest`; `_cleanup()`; `rm -rf $fstest_dir.* $tmp.*`; `_require_test`; `_do_test()`; `_n="$1"`; `_param="$2"`.

## State and Persistence Behavior

The test mutates files under `TEST_DIR`. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_test`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include golden-output drift or unsupported prerequisite handling are the main maintenance risks. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/074 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/075 -->

# sources/test-tools/xfstests/tests/generic/075

## Purpose

fsx (non-AIO variant)

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest rw udf auto quick`. Important local functions are `_cleanup`, `_do_test`, `_process_args`, `_usage`. Key xfstests/helper interfaces include `_require_test` (requires the configured TEST_DIR filesystem). External or helper commands visible in the body include `fsx`, `mkdir`, `mv`, `od`, `rm`. Significant variables include `OPTIND`, `status`, `testfile`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_cleanup()`; `rm -rf $TEST_DIR/fsx.* $tmp.*`; `_do_test()`; `_n="$1"`; `_param="$2"`; `out=$TEST_DIR/fsx`; `rm -rf $out`.

## State and Persistence Behavior

The test mutates files under `TEST_DIR`. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_test`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include timing or background-process races can make failures intermittent, stress-tool behavior and kernel timing can expose nondeterminism. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/075 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/076 -->

# sources/test-tools/xfstests/tests/generic/076

## Purpose

Test blockdev reads in parallel with filesystem reads/writes

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest metadata rw udf auto quick stress`. Important local functions are `_cleanup`, `_lets_get_pidst`. Key xfstests/helper interfaces include `_scratch_unmount` (unmounts scratch to force persistence checks), `_require_scratch` (requires a disposable scratch filesystem), `_scratch_mount` (mounts the scratch filesystem), `_scratch_mkfs` (formats the scratch filesystem). External or helper commands visible in the body include `fsstress`, `rm`. Significant variables include `FSSTRESS_ARGS`, `status`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_lets_get_pidst()`; `if [ -n "$pid" ]; then`; `_cleanup()`; `_lets_get_pidst`; `rm -f $tmp.*`; `_require_scratch`; `_require_local_device $SCRATCH_DEV`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_local_device`, `_require_scratch`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent, stress-tool behavior and kernel timing can expose nondeterminism. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/076 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/077 -->

# sources/test-tools/xfstests/tests/generic/077

## Purpose

Check use of ACLs (extended attributes) on a full filesystem

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest acl attr auto enospc`. Important local functions are `_cleanup`. Key xfstests/helper interfaces include `_scratch_mkfs_sized` (formats a scratch image/device of a requested size), `_check_scratch_fs` (runs scratch filesystem consistency checking), `_scratch_unmount` (unmounts scratch to force persistence checks), `_require_scratch` (requires a disposable scratch filesystem), `_scratch_mount` (mounts the scratch filesystem). External or helper commands visible in the body include `cp`, `mkdir`, `rm`, `tail`. Significant variables include `status`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, `./common/attr`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_cleanup()`; `echo "*** unmount"`; `_scratch_unmount 2>/dev/null`; `_require_scratch`; `_require_attrs`; `_require_acls`; `_require_user`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_acls`, `_require_attrs`, `_require_scratch`, `_require_user`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter`, `./common/attr` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: runs filesystem consistency checking; logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/077 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/078 -->

# sources/test-tools/xfstests/tests/generic/078

## Purpose

Check renameat2 syscall with RENAME_WHITEOUT flag

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest auto quick metadata`. No local shell functions are declared. Key xfstests/helper interfaces include `_require_test` (requires the configured TEST_DIR filesystem). External or helper commands visible in the body include `mkdir`. Significant variables include `status`.

## Control Flow

The script sources `./common/preamble`, `./common/renameat2`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_require_test`; `_require_renameat2 whiteout`; `_require_symlinks`; `rename_dir=$TEST_DIR/$$`; `mkdir $rename_dir`; `_rename_tests $rename_dir -w`.

## State and Persistence Behavior

The test mutates files under `TEST_DIR`. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_renameat2`, `_require_symlinks`, `_require_test`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/renameat2` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include golden-output drift or unsupported prerequisite handling are the main maintenance risks. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: passes when required commands complete and the xfstests golden output matches. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/078 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/079 -->

# sources/test-tools/xfstests/tests/generic/079

## Purpose

Run the t_immutable test program for immutable/append-only files.

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest auto quick ioctl metadata`. Important local functions are `_cleanup`. Key xfstests/helper interfaces include `_require_test_program` (checks availability of an xfstests helper binary), `_require_scratch` (requires a disposable scratch filesystem), `_scratch_mount` (mounts the scratch filesystem), `_scratch_mkfs` (formats the scratch filesystem). External or helper commands visible in the body include `grep`, `rm`. Significant variables include `status`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, `./common/attr`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_cleanup()`; `echo "*** cleaning up"`; `$timmutable -r $SCRATCH_MNT/$seq`; `_require_chattr ia`; `_require_user_exists "nobody"`; `_require_user_exists "daemon"`; `_require_test_program "t_immutable"`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_chattr`, `_require_scratch`, `_require_test_program`, `_require_user_exists`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter`, `./common/attr` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: passes when required commands complete and the xfstests golden output matches. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/079 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/080 -->

# sources/test-tools/xfstests/tests/generic/080

## Purpose

Verify that mtime is updated when writing to mmap-ed pages

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest auto quick mmap`. Important local functions are `_cleanup`. Key xfstests/helper interfaces include `_require_test` (requires the configured TEST_DIR filesystem). External or helper commands visible in the body include `fsync`, `rm`, `stat`. Significant variables include `status`, `testfile`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_cleanup()`; `rm -f $tmp.*`; `rm -f $testfile`; `_require_test`; `echo "Silence is golden."`; `testfile=$TEST_DIR/mmap_mtime_testfile`; `$XFS_IO_PROG -f -c "pwrite 0 4k" -c fsync $testfile >> $seqres.full`.

## State and Persistence Behavior

The test mutates files under `TEST_DIR`. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_test`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include timing or background-process races can make failures intermittent. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: prints `Silence is golden` after all checks pass; logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/080 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/081 -->

# sources/test-tools/xfstests/tests/generic/081

## Purpose

Test I/O error path by fully filling an dm snapshot.

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest auto quick`. Important local functions are `_cleanup`. Key xfstests/helper interfaces include `_scratch_mkfs_sized` (formats a scratch image/device of a requested size), `_require_dm_target` (requires a device-mapper target), `_require_command` (checks availability of an external command), `_require_test` (requires the configured TEST_DIR filesystem). External or helper commands visible in the body include `fsync`, `mkdir`, `rm`. Significant variables include `size`, `status`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_cleanup()`; `rm -f $tmp.*`; `while test -e /dev/mapper/$vgname-$snapname || \`; `_unmount $mnt >> $seqres.full 2>&1`; `$LVM_PROG pvremove -f $SCRATCH_DEV >>$seqres.full 2>&1`; `_udev_wait --removed /dev/mapper/$vgname-$lvname`; `_require_test`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, files under `TEST_DIR`, mount/unmount state. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_command`, `_require_dm_target`, `_require_scratch_nolvm`, `_require_test`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: prints `Silence is golden` after all checks pass; logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/081 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/082 -->

# sources/test-tools/xfstests/tests/generic/082

## Purpose

Test quota handling on remount ro failure

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest auto quick quota`. Important local functions are `filter_project_quota_line`. Key xfstests/helper interfaces include `_try_scratch_mount` (attempts to mount scratch and lets the test decide skip/fail behavior), `_require_scratch` (requires a disposable scratch filesystem), `_filter_scratch` (normalizes scratch paths in stdout), `_scratch_mount` (mounts the scratch filesystem), `_scratch_mkfs` (formats the scratch filesystem). External or helper commands visible in the body include `grep`. Significant variables include `status`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, `./common/quota`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_require_test`; `_require_scratch`; `_require_quota`; `_scratch_mkfs >>$seqres.full 2>&1`; `_scratch_mount "-o usrquota,grpquota"`; `quotacheck -ug $SCRATCH_MNT >>$seqres.full 2>&1`; `quotaon $SCRATCH_MNT >>$seqres.full 2>&1`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state, quota/project-id metadata. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_quota`, `_require_scratch`, `_require_test`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter`, `./common/quota` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/082 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/083 -->

# sources/test-tools/xfstests/tests/generic/083

## Purpose

Exercise filesystem full behaviour - run numerous fsstress processes in write mode on a small filesystem. NB: delayed allocate flushing is quite deadlock prone at the filesystem full boundary due to the fact that we will retry allocation several times after flushing, before giving back ENOSPC. Note that this test will intentionally cause console msgs of form: dksc0d1s4: Process [fsstress] ran out of disk space dksc0d1s4: Process [fsstress] ran out of disk space dksc0d1s4: Process [fsstress] ran out of disk space

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest rw auto enospc stress`. Important local functions are `workout`. Key xfstests/helper interfaces include `_scratch_mkfs_sized` (formats a scratch image/device of a requested size), `_scratch_unmount` (unmounts scratch to force persistence checks), `_require_scratch` (requires a disposable scratch filesystem), `_scratch_mount` (mounts the scratch filesystem). External or helper commands visible in the body include `mkfs`. Significant variables include `FSSTRESS_ARGS`, `status`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_require_scratch`; `_require_no_large_scratch_dev`; `_scratch_unmount >/dev/null 2>&1`; `echo "*** mkfs -dsize=$fsz,agcount=$ags"    >>$seqres.full`; `echo ""                                     >>$seqres.full`; `if [ $FSTYP = xfs ]`; `_scratch_mkfs_xfs -dsize=$fsz,agcount=$ags  >>$seqres.full 2>&1`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_no_large_scratch_dev`, `_require_scratch`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent, stress-tool behavior and kernel timing can expose nondeterminism. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/083 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/084 -->

# sources/test-tools/xfstests/tests/generic/084

## Purpose

Test hardlink to unlinked file. Regression test for commit: aae8a97 fs: Don't allow to create hardlink for deleted file

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest auto metadata quick`. Important local functions are `_cleanup`, `link_unlink_storm`. Key xfstests/helper interfaces include `_require_scratch` (requires a disposable scratch filesystem), `_scratch_mount` (mounts the scratch filesystem), `_scratch_mkfs` (formats the scratch filesystem). External or helper commands visible in the body include `ln`, `rm`, `touch`. Significant variables include `status`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_cleanup()`; `rm -f $tmp.*`; `_require_scratch`; `while true; do`; `rm -f $target.$i >/dev/null 2>&1`; `echo "Silence is golden"`; `_scratch_mkfs >>$seqres.full 2>&1`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_scratch`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: prints `Silence is golden` after all checks pass; logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/084 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/085 -->

# sources/test-tools/xfstests/tests/generic/085

## Purpose

Exercise fs freeze/unfreeze and mount/umount race, which could lead to use-after-free oops. This commit fixed the issue: 1494583 fix get_active_super()/umount() race

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest auto freeze mount`. Important local functions are `_cleanup`, `cleanup_dmdev`, `setup_dmdev`. Key xfstests/helper interfaces include `_scratch_mkfs_sized` (formats a scratch image/device of a requested size), `_require_dm_target` (requires a device-mapper target), `_require_scratch` (requires a disposable scratch filesystem). External or helper commands visible in the body include `mount`, `rm`. Significant variables include `size`, `status`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_cleanup()`; `rm -f $tmp.*`; `if [ -n "$pid" ]; then`; `_unmount -q $SCRATCH_MNT >/dev/null 2>&1`; `_dmsetup_remove $node`; `_require_scratch`; `_require_block_device $SCRATCH_DEV`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state, device-mapper target state. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_block_device`, `_require_dm_target`, `_require_freeze`, `_require_scratch`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: prints `Silence is golden` after all checks pass; logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/085 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/086 -->

# sources/test-tools/xfstests/tests/generic/086

## Purpose

This test excercises the problem with unwritten and delayed extents in ext4 extent status tree where we might in some cases lose a block worth of data. Even though this was a ext4 specific problem the reproducer can be easily tun on any file system so let's do that just in case. This tests excercises the problem fixed in kernel with commit "ext4: Fix data corruption caused by unwritten and delayed extents"

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest auto prealloc preallocrw quick`. No local shell functions are declared. Key xfstests/helper interfaces include `_require_xfs_io_command` (checks xfs_io subcommand support), `_require_test` (requires the configured TEST_DIR filesystem). External or helper commands visible in the body include `rm`. Significant variables include `status`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_require_test`; `_require_xfs_io_command "falloc"`; `rm -f $test_file`; `$XFS_IO_PROG -f -c "pwrite -S 0xaa 4096 2048" \`; `echo 3 > /proc/sys/vm/drop_caches`; `$XFS_IO_PROG -c "pwrite -S 0xdd 67584 2048" $test_file >> $seqres.full 2>&1`; `_hexdump $test_file`.

## State and Persistence Behavior

The test mutates temporary files under `$tmp.*` and harness result files. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_test`, `_require_xfs_io_command`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include timing or background-process races can make failures intermittent. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/086 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/087 -->

# sources/test-tools/xfstests/tests/generic/087

## Purpose

xfstests shell test generic/087. Its tags are perms, auto, quick, so it participates in the xfstests harness for filesystem behavior regression coverage.

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest perms auto quick`. Important local functions are `_cleanup`. Key xfstests/helper interfaces include `_require_test` (requires the configured TEST_DIR filesystem). External or helper commands visible in the body include `cp`, `rm`. Significant variables include `QA_FS_PERMS`, `status`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_cleanup()`; `_require_test`; `_require_chown`; `cd $TEST_DIR`; `cp $here/src/testx ./testx.file`; `rm -f ./testx.file`.

## State and Persistence Behavior

The test mutates files under `TEST_DIR`. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_chown`, `_require_test`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include golden-output drift or unsupported prerequisite handling are the main maintenance risks. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: passes when required commands complete and the xfstests golden output matches. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/087 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/088 -->

# sources/test-tools/xfstests/tests/generic/088

## Purpose

test out CAP_DAC_OVERRIDE and CAP_DAC_SEARCH code in xfs_iaccess(ip,mode,cr)

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest perms auto quick`. Important local functions are `_filter`. Key xfstests/helper interfaces include `_require_test` (requires the configured TEST_DIR filesystem). External or helper commands visible in the body include `sed`. Significant variables include `status`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_filter()`; `_filter_test_dir | sed -e '/----------/d'`; `_require_test`; `_require_chown`; `path=$TEST_DIR/t_access`.

## State and Persistence Behavior

The test mutates files under `TEST_DIR`. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_chown`, `_require_test`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include golden-output drift or unsupported prerequisite handling are the main maintenance risks. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/088 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/089 -->

# sources/test-tools/xfstests/tests/generic/089

## Purpose

Emulate the way Linux mount manipulates /etc/mtab to attempt to reproduce a possible bug in rename (see src/t_mtab.c).

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest metadata auto`. Important local functions are `addentries`, `mtab`. Key xfstests/helper interfaces include `_require_test` (requires the configured TEST_DIR filesystem). External or helper commands visible in the body include `grep`, `ls`, `mkdir`, `mount`, `rm`, `touch`. Significant variables include `status`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `mtab_output=$TEST_DIR/mtab_output`; `while [ $count -gt 0 ]; do`; `touch \`printf $pattern $count\``; `_require_test`; `_require_hardlinks`; `[ "X$TEST_DIR" = "X" ] && exit 1`; `cd $TEST_DIR`.

## State and Persistence Behavior

The test mutates files under `TEST_DIR`, mount/unmount state. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_hardlinks`, `_require_test`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include timing or background-process races can make failures intermittent. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/089 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/090 -->

# sources/test-tools/xfstests/tests/generic/090

## Purpose

Test that after syncing the filesystem, adding a hard link to a file, syncing the filesystem again, doing a write to the file that increases its size and then doing a fsync against that file, durably persists the data written to the file. That is, after log/journal replay, the data is available. This test is motivated by a bug found in btrfs.

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest metadata auto quick log`. Important local functions are `_cleanup`. Key xfstests/helper interfaces include `_require_dm_target` (requires a device-mapper target), `_require_scratch` (requires a disposable scratch filesystem), `_scratch_mount` (mounts the scratch filesystem), `_filter_xfs_io` (normalizes xfs_io output), `_scratch_mkfs` (formats the scratch filesystem). External or helper commands visible in the body include `fsync`, `ln`, `od`, `rm`. Significant variables include `status`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, `./common/dmflakey`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_cleanup()`; `_cleanup_flakey`; `rm -f $tmp.*`; `_require_scratch`; `_require_hardlinks`; `_require_dm_target flakey`; `_scratch_mkfs >> $seqres.full 2>&1`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state, device-mapper target state. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_dm_target`, `_require_hardlinks`, `_require_metadata_journaling`, `_require_scratch`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter`, `./common/dmflakey` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/090 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/091 -->

# sources/test-tools/xfstests/tests/generic/091

## Purpose

fsx exercising direct IO -- sub-block sizes and concurrent buffered IO

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest rw auto quick`. No local shell functions are declared. Key xfstests/helper interfaces include `_require_odirect` (requires O_DIRECT support), `_require_test` (requires the configured TEST_DIR filesystem). No standalone external commands were extracted beyond shell builtins and xfstests helper calls.. Significant variables include `status`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_require_test`; `_require_odirect`; `bsize=\`$here/src/min_dio_alignment $TEST_DIR $TEST_DEV\``.

## State and Persistence Behavior

The test mutates files under `TEST_DIR`. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_odirect`, `_require_test`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include stress-tool behavior and kernel timing can expose nondeterminism. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: passes when required commands complete and the xfstests golden output matches. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/091 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/092 -->

# sources/test-tools/xfstests/tests/generic/092

## Purpose

fallocate/truncate tests with FALLOC_FL_KEEP_SIZE option. Verify if the disk space is released after truncating a file to i_size after writing to a portion of a preallocated range. This also verifies that truncat'ing up past i_size doesn't remove the preallocated space.

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest auto quick prealloc fiemap`. No local shell functions are declared. Key xfstests/helper interfaces include `_require_xfs_io_command` (checks xfs_io subcommand support), `_filter_xfs_io` (normalizes xfs_io output), `_filter_fiemap` (normalizes fiemap output), `_require_test` (requires the configured TEST_DIR filesystem). External or helper commands visible in the body include `fiemap`. Significant variables include `status`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, `./common/punch`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_require_test`; `_require_xfs_io_command "falloc"`; `_require_xfs_io_command "fiemap"`; `_require_congruent_file_oplen $TEST_DIR $((5 * 1048576))`; `_require_congruent_file_oplen $TEST_DIR $((7 * 1048576))`; `$XFS_IO_PROG -f -c "falloc -k 0 10M" -c "pwrite 0 5M" -c "truncate 5M"\`; `$TEST_DIR/testfile.$seq | _filter_xfs_io`.

## State and Persistence Behavior

The test mutates files under `TEST_DIR`. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_congruent_file_oplen`, `_require_test`, `_require_xfs_io_command`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter`, `./common/punch` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include extent layout assumptions can vary by filesystem feature and kernel version. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: passes when required commands complete and the xfstests golden output matches. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/092 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/093 -->

# sources/test-tools/xfstests/tests/generic/093

## Purpose

Test clearing of capabilities on write.

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest attr cap auto`. Important local functions are `_cleanup`, `filefilter`. Key xfstests/helper interfaces include `_require_test_program` (checks availability of an xfstests helper binary), `_require_command` (checks availability of an external command), `_require_attrs` (requires extended attribute support), `_require_test` (requires the configured TEST_DIR filesystem). External or helper commands visible in the body include `rm`, `sed`, `touch`. Significant variables include `file`, `status`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, `./common/attr`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_cleanup()`; `[ -n "$TEST_DIR" ] && rm -f $file`; `_require_test`; `_require_attrs security`; `_require_user`; `_require_test_program "writemod"`; `_require_command "$SETCAP_PROG" "setcap"`.

## State and Persistence Behavior

The test mutates files under `TEST_DIR`. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_attrs`, `_require_command`, `_require_test`, `_require_test_program`, `_require_user`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter`, `./common/attr` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include timing or background-process races can make failures intermittent. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: passes when required commands complete and the xfstests golden output matches. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/093 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/094 -->

# sources/test-tools/xfstests/tests/generic/094

## Purpose

Run the fiemap (file extent mapping) tester with preallocation enabled

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest auto quick prealloc fiemap`. Important local functions are `_cleanup`. Key xfstests/helper interfaces include `_require_xfs_io_command` (checks xfs_io subcommand support), `_require_test_program` (checks availability of an xfstests helper binary), `_require_odirect` (requires O_DIRECT support), `_require_test` (requires the configured TEST_DIR filesystem). External or helper commands visible in the body include `fiemap`, `rm`. Significant variables include `status`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_cleanup()`; `rm -fr $tmp.*`; `rm -f $fiemapfile`; `_require_test`; `_require_odirect`; `_require_xfs_io_command "fiemap"`; `_require_xfs_io_command "falloc"`.

## State and Persistence Behavior

The test mutates files under `TEST_DIR`. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_odirect`, `_require_test`, `_require_test_program`, `_require_xfs_io_command`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include extent layout assumptions can vary by filesystem feature and kernel version. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/094 -->
