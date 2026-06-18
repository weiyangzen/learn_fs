<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/030 -->
# sources/test-tools/xfstests/tests/btrfs/030

## Purpose
Regression test for btrfs' incremental send feature: 1) Create several nested directories; 2) Create a read only snapshot; 3) Change the parentship of some of the deepest directories in a reverse way, so that parents become children and children become parents; 4) Create another read only snapshot and use it for an incremental send relative to the first snapshot. At step 4 btrfs' send entered an infinite loop, increasing the memory it used while building path strings until a krealloc was unable to allocate more memory, which caused a warning dump in dmesg. The script is categorized by `_begin_fstest` as `auto`, `quick`, `send`, and its main coverage is: Btrfs send/receive stream generation, including full sends, incremental parent sends, clone-source roots, received UUID handling, and replay on a freshly formatted scratch filesystem. Snapshot creation, readonly snapshot consistency, default subvolume behavior, and interactions between snapshot roots and live/orphaned metadata.

## Important APIs, Types, and Functions
local shell functions: `_cleanup` fstest tags: `auto`, `quick`, `send` requirement gates: `_require_scratch`, `_require_fssum`. The important external command surfaces are `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/mysnap1`; `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/mysnap2`; `_btrfs send -f $tmp/1.snap $SCRATCH_MNT/mysnap1`; `_btrfs send -f $tmp/2.snap -p $SCRATCH_MNT/mysnap1 \`; `_btrfs receive -f $tmp/1.snap $SCRATCH_MNT`; `_btrfs receive -f $tmp/2.snap $SCRATCH_MNT` for Btrfs control and standard shell/file utilities for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_mkfs >/dev/null 2>&1`; `_scratch_mount`; `_scratch_unmount`; `_check_btrfs_filesystem $SCRATCH_DEV`; plus 4 more source-matched operations. The core workload then performs these representative operations: `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/mysnap1`; `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/mysnap2`; `_btrfs send -f $tmp/1.snap $SCRATCH_MNT/mysnap1`; `_btrfs send -f $tmp/2.snap -p $SCRATCH_MNT/mysnap1 \`; `_btrfs receive -f $tmp/1.snap $SCRATCH_MNT`; `_btrfs receive -f $tmp/2.snap $SCRATCH_MNT`. It also uses background or repeated stress/control loops: `_scratch_mkfs >/dev/null 2>&1`; plus 1 more source-matched operations.

## State and Persistence Behavior
Creates snapshot roots and compares parent/child root state; persists send streams to temporary files and replays them on a reformatted scratch filesystem; records fssum manifests and validates received trees against them. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on scratch filesystem lifecycle helpers, fssum content manifests for send/receive equivalence, btrfs-progs command wrappers. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
send path ordering can emit invalid rename, rmdir, clone, or path records if inode identity, generation, or delayed-move state is mishandled The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
fssum replay must match original snapshot manifests explicit filesystem check must pass Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/030 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/031 -->
# sources/test-tools/xfstests/tests/btrfs/031

## Purpose
Testing cross-subvolume sparse copy on btrfs - Create two subvolumes, mount one of them - Create a file on each (sub/root)volume, reflink them on the other volumes - Change one original and two reflinked files - Move reflinked files between subvolumes The script is categorized by `_begin_fstest` as `auto`, `quick`, `subvol`, `clone`, and its main coverage is: Btrfs extent cloning/reflink semantics, including inline extents, same-file clones, holes, compressed extents, page-cache coherency, and fsync/log replay persistence. Subvolume creation, mounting, deletion, set-default behavior, and placeholder directory semantics.

## Important APIs, Types, and Functions
local shell functions: `_checksum_files` fstest tags: `auto`, `quick`, `subvol`, `clone` requirement gates: `_require_test`, `_require_scratch`, `_require_cp_reflink`. The important external command surfaces are `$BTRFS_UTIL_PROG subvolume create $subvol1 >> $seqres.full`; `$BTRFS_UTIL_PROG subvolume create $subvol2 >> $seqres.full`; `_mount -t btrfs -o subvol=subvol-$seq-1 $SCRATCH_DEV $cross_mount_test_dir` for Btrfs control and `$XFS_IO_PROG -f -c 'pwrite -S 0x61 0 10' $testdir1/file1 \`; `$XFS_IO_PROG -f -c 'pwrite -S 0x62 0 13000' $cross_mount_test_dir/file2 \`; `$XFS_IO_PROG -f -c 'pwrite -S 0x63 0 17000' $subvol2/file3 \`; `cp --reflink=always $testdir1/file1 $subvol1`; `cp --reflink=always $testdir1/file1 $subvol2`; `cp --reflink=always $subvol1/file2 $testdir1/`; plus 6 more source-matched operations for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_mkfs > /dev/null 2>&1`; `_scratch_mount`. The core workload then performs these representative operations: `$BTRFS_UTIL_PROG subvolume create $subvol1 >> $seqres.full`; `$BTRFS_UTIL_PROG subvolume create $subvol2 >> $seqres.full`; `_mount -t btrfs -o subvol=subvol-$seq-1 $SCRATCH_DEV $cross_mount_test_dir`; `$XFS_IO_PROG -f -c 'pwrite -S 0x61 0 10' $testdir1/file1 \`; `$XFS_IO_PROG -f -c 'pwrite -S 0x62 0 13000' $cross_mount_test_dir/file2 \`; `$XFS_IO_PROG -f -c 'pwrite -S 0x63 0 17000' $subvol2/file3 \`; `cp --reflink=always $testdir1/file1 $subvol1`; `cp --reflink=always $testdir1/file1 $subvol2`; `cp --reflink=always $subvol1/file2 $testdir1/`; `cp --reflink=always $subvol1/file2 $subvol2`; plus 5 more source-matched operations. It also uses background or repeated stress/control loops: `_scratch_mkfs > /dev/null 2>&1`.

## State and Persistence Behavior
Uses digest checks as durable content signals. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on external test directory storage, scratch filesystem lifecycle helpers, cp --reflink support, btrfs-progs command wrappers, xfs_io data-shaping commands. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
clone/reflink edge cases can corrupt inline extents, holes, compressed extents, page cache, or log replay metadata The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
digest output before and after remount/receive must match expected content Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/031 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/032 -->
# sources/test-tools/xfstests/tests/btrfs/032

## Purpose
Regression test for transaction abortion when remounting RW to RO with flushoncommit option enabled. The script is categorized by `_begin_fstest` as `auto`, `quick`, `remount`, and its main coverage is: Mount option transitions, especially flushoncommit, thread_pool resizing, and compression remount changes.

## Important APIs, Types, and Functions
fstest tags: `auto`, `quick`, `remount` requirement gates: `_require_scratch`. The important external command surfaces are `_btrfs`/`$BTRFS_UTIL_PROG` where present for Btrfs control and `$XFS_IO_PROG -f -c "pwrite 0 10M" "$SCRATCH_MNT/tmpfile" | _filter_xfs_io` for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_mkfs > /dev/null 2>&1`; `_scratch_mount "-o flushoncommit"`; `_scratch_mount "-o remount,ro"`. The core workload then performs these representative operations: `$XFS_IO_PROG -f -c "pwrite 0 10M" "$SCRATCH_MNT/tmpfile" | _filter_xfs_io`. It also uses background or repeated stress/control loops: `_scratch_mkfs > /dev/null 2>&1`.

## State and Persistence Behavior
Mutates a freshly formatted scratch filesystem and relies on command status plus fstests cleanup checks. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on scratch filesystem lifecycle helpers, xfs_io data-shaping commands. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
the test is sensitive to kernel, btrfs-progs, and fstests helper behavior because it verifies a narrow historical regression The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
successful command completion and fstests cleanup checks are the primary signal Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/032 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/033 -->
# sources/test-tools/xfstests/tests/btrfs/033

## Purpose
Regression test for iterating backrefs The script is categorized by `_begin_fstest` as `auto`, `quick`, `send`, `snapshot`, and its main coverage is: Btrfs send/receive stream generation, including full sends, incremental parent sends, clone-source roots, received UUID handling, and replay on a freshly formatted scratch filesystem. Snapshot creation, readonly snapshot consistency, default subvolume behavior, and interactions between snapshot roots and live/orphaned metadata. Subvolume creation, mounting, deletion, set-default behavior, and placeholder directory semantics.

## Important APIs, Types, and Functions
fstest tags: `auto`, `quick`, `send`, `snapshot` requirement gates: `_require_scratch`. The important external command surfaces are `$BTRFS_UTIL_PROG subvolume snapshot -r $SCRATCH_MNT \`; `$BTRFS_UTIL_PROG send -f $SCRATCH_MNT/send_file \` for Btrfs control and `$XFS_IO_PROG -f -d -c "pwrite $(($i * 4096)) 4096" \` for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_mkfs > /dev/null 2>&1`; `_scratch_mount`. The core workload then performs these representative operations: `$BTRFS_UTIL_PROG subvolume snapshot -r $SCRATCH_MNT \`; `$BTRFS_UTIL_PROG send -f $SCRATCH_MNT/send_file \`; `$XFS_IO_PROG -f -d -c "pwrite $(($i * 4096)) 4096" \`. It also uses background or repeated stress/control loops: `_scratch_mkfs > /dev/null 2>&1`; `for i in `seq 10240 -1 1`; do`; `for i in `seq 0 50`; do`; `$SCRATCH_MNT/snap_$i >> $seqres.full 2>&1`; `$SCRATCH_MNT/snap_1 >> $seqres.full 2>&1`.

## State and Persistence Behavior
Creates snapshot roots and compares parent/child root state. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on scratch filesystem lifecycle helpers, btrfs-progs command wrappers, xfs_io data-shaping commands. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
send path ordering can emit invalid rename, rmdir, clone, or path records if inode identity, generation, or delayed-move state is mishandled The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
prints `Silence is golden` when no explicit failure path is reached Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/033 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/034 -->
# sources/test-tools/xfstests/tests/btrfs/034

## Purpose
Test for a btrfs incremental send data corruption issue due to bad detection of file holes. The script is categorized by `_begin_fstest` as `auto`, `quick`, `send`, `prealloc`, and its main coverage is: Btrfs send/receive stream generation, including full sends, incremental parent sends, clone-source roots, received UUID handling, and replay on a freshly formatted scratch filesystem. Snapshot creation, readonly snapshot consistency, default subvolume behavior, and interactions between snapshot roots and live/orphaned metadata. Subvolume creation, mounting, deletion, set-default behavior, and placeholder directory semantics. Preallocated extent handling, fallocate/fpunch behavior, and distinguishing real data from holes during send or clone.

## Important APIs, Types, and Functions
local shell functions: `_cleanup` fstest tags: `auto`, `quick`, `send`, `prealloc` requirement gates: `_require_scratch`, `_require_xfs_io_command`. The important external command surfaces are `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/mysnap1`; `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/mysnap2`; `_btrfs send -f $tmp/1.snap $SCRATCH_MNT/mysnap1`; `_btrfs send -f $tmp/2.snap -p $SCRATCH_MNT/mysnap1 \`; `_btrfs receive -f $tmp/1.snap $SCRATCH_MNT`; `_btrfs receive -f $tmp/2.snap $SCRATCH_MNT` for Btrfs control and `$XFS_IO_PROG -f -c "truncate 104857600" $SCRATCH_MNT/foo`; `$XFS_IO_PROG -c "falloc -k $OFFSET $LEN" $SCRATCH_MNT/foo`; `$XFS_IO_PROG -c "pwrite -S 0xf0 $OFFSET 4096" \`; `$XFS_IO_PROG -c "truncate 3882008" $SCRATCH_MNT/foo`; `md5sum $SCRATCH_MNT/foo | _filter_scratch`; `md5sum $SCRATCH_MNT/mysnap1/foo | _filter_scratch`; plus 3 more source-matched operations for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_mkfs >/dev/null 2>&1`; `_scratch_mount`; `_scratch_unmount`; `_check_btrfs_filesystem $SCRATCH_DEV`; plus 4 more source-matched operations. The core workload then performs these representative operations: `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/mysnap1`; `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/mysnap2`; `_btrfs send -f $tmp/1.snap $SCRATCH_MNT/mysnap1`; `_btrfs send -f $tmp/2.snap -p $SCRATCH_MNT/mysnap1 \`; `_btrfs receive -f $tmp/1.snap $SCRATCH_MNT`; `_btrfs receive -f $tmp/2.snap $SCRATCH_MNT`; `$XFS_IO_PROG -f -c "truncate 104857600" $SCRATCH_MNT/foo`; `$XFS_IO_PROG -c "falloc -k $OFFSET $LEN" $SCRATCH_MNT/foo`; `$XFS_IO_PROG -c "pwrite -S 0xf0 $OFFSET 4096" \`; `$XFS_IO_PROG -c "truncate 3882008" $SCRATCH_MNT/foo`; plus 5 more source-matched operations. It also uses background or repeated stress/control loops: `_scratch_mkfs >/dev/null 2>&1`; `for ((i = 0; i < 940; i++))`; plus 1 more source-matched operations.

## State and Persistence Behavior
Creates snapshot roots and compares parent/child root state; persists send streams to temporary files and replays them on a reformatted scratch filesystem; uses digest checks as durable content signals. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on scratch filesystem lifecycle helpers, xfs_io subcommand availability, btrfs-progs command wrappers, xfs_io data-shaping commands. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
send path ordering can emit invalid rename, rmdir, clone, or path records if inode identity, generation, or delayed-move state is mishandled The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
digest output before and after remount/receive must match expected content explicit filesystem check must pass Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/034 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/035 -->
# sources/test-tools/xfstests/tests/btrfs/035

## Purpose
Regression test for overwriting clones The script is categorized by `_begin_fstest` as `auto`, `quick`, `clone`, and its main coverage is: Btrfs extent cloning/reflink semantics, including inline extents, same-file clones, holes, compressed extents, page-cache coherency, and fsync/log replay persistence.

## Important APIs, Types, and Functions
fstest tags: `auto`, `quick`, `clone` requirement gates: `_require_scratch`, `_require_cloner`. The important external command surfaces are `_btrfs`/`$BTRFS_UTIL_PROG` where present for Btrfs control and `$CLONER_PROG $SCRATCH_MNT/src $SCRATCH_MNT/src.clone1`; `$CLONER_PROG $SCRATCH_MNT/src $SCRATCH_MNT/src.clone2`; `$CLONER_PROG -s 0 -d 0 -l ${snap_src_sz} \`; `od -t x1 $SCRATCH_MNT/src`; plus 2 more source-matched operations for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_mkfs > /dev/null 2>&1`; `_scratch_mount`. The core workload then performs these representative operations: `$CLONER_PROG $SCRATCH_MNT/src $SCRATCH_MNT/src.clone1`; `$CLONER_PROG $SCRATCH_MNT/src $SCRATCH_MNT/src.clone2`; `$CLONER_PROG -s 0 -d 0 -l ${snap_src_sz} \`; `od -t x1 $SCRATCH_MNT/src`; plus 2 more source-matched operations. It also uses background or repeated stress/control loops: `_scratch_mkfs > /dev/null 2>&1`.

## State and Persistence Behavior
Mutates a freshly formatted scratch filesystem and relies on command status plus fstests cleanup checks. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on scratch filesystem lifecycle helpers, btrfs clone ioctl exerciser, Btrfs-specific output filters. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
clone/reflink edge cases can corrupt inline extents, holes, compressed extents, page cache, or log replay metadata The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
hex dumps expose exact byte-level clone or hole behavior Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/035 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/036 -->
# sources/test-tools/xfstests/tests/btrfs/036

## Purpose
Regression test for running snapshots and send concurrently. The script is categorized by `_begin_fstest` as `auto`, `quick`, `send`, `snapshot`, and its main coverage is: Btrfs send/receive stream generation, including full sends, incremental parent sends, clone-source roots, received UUID handling, and replay on a freshly formatted scratch filesystem. Snapshot creation, readonly snapshot consistency, default subvolume behavior, and interactions between snapshot roots and live/orphaned metadata. Subvolume creation, mounting, deletion, set-default behavior, and placeholder directory semantics.

## Important APIs, Types, and Functions
local shell functions: `_cleanup`, `do_snapshots` fstest tags: `auto`, `quick`, `send`, `snapshot` requirement gates: `_require_scratch`. The important external command surfaces are `$BTRFS_UTIL_PROG subvolume snapshot -r $SCRATCH_MNT/snap_1 \`; `$BTRFS_UTIL_PROG subvolume snapshot -r $SCRATCH_MNT \`; `$BTRFS_UTIL_PROG send -f /dev/null $SCRATCH_MNT/snap_1 2>&1 | _filter_scratch` for Btrfs control and `$XFS_IO_PROG -f -d -c "pwrite $(($i * 4096)) 4096" \` for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_mkfs > /dev/null 2>&1`; `_scratch_mount`. The core workload then performs these representative operations: `$BTRFS_UTIL_PROG subvolume snapshot -r $SCRATCH_MNT/snap_1 \`; `$BTRFS_UTIL_PROG subvolume snapshot -r $SCRATCH_MNT \`; `$BTRFS_UTIL_PROG send -f /dev/null $SCRATCH_MNT/snap_1 2>&1 | _filter_scratch`; `$XFS_IO_PROG -f -d -c "pwrite $(($i * 4096)) 4096" \`. It also uses background or repeated stress/control loops: `if [ $snapshots_pid -ne 0 ] && ps -p $snapshots_pid | grep -q $snapshots_pid; then`; `kill -TERM $snapshots_pid 2> /dev/null`; `wait $snapshots_pid`; `trap "wait; exit" SIGTERM`; `$SCRATCH_MNT/snap_$i >> $seqres.full 2>&1`; `_scratch_mkfs > /dev/null 2>&1`; plus 4 more source-matched operations.

## State and Persistence Behavior
Creates snapshot roots and compares parent/child root state. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on scratch filesystem lifecycle helpers, btrfs-progs command wrappers, xfs_io data-shaping commands. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
send path ordering can emit invalid rename, rmdir, clone, or path records if inode identity, generation, or delayed-move state is mishandled The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
successful command completion and fstests cleanup checks are the primary signal Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/036 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/037 -->
# sources/test-tools/xfstests/tests/btrfs/037

## Purpose
Test for a btrfs data corruption when using compressed files/extents. Under certain cases, it was possible for reads to return random data caused partial updates to those regions that were supposed to be filled with zeroes to save random (and invalid) data into the file extents. This is fixed by the commit for the linux kernel titled: The script is categorized by `_begin_fstest` as `auto`, `quick`, `compress`, `prealloc`, and its main coverage is: Compressed extent behavior across read, restore, clone, send, defrag, remount, and property inheritance paths. Preallocated extent handling, fallocate/fpunch behavior, and distinguishing real data from holes during send or clone.

## Important APIs, Types, and Functions
local shell functions: `_cleanup` fstest tags: `auto`, `quick`, `compress`, `prealloc` requirement gates: `_require_scratch`, `_require_xfs_io_command`. The important external command surfaces are `_btrfs`/`$BTRFS_UTIL_PROG` where present for Btrfs control and `$XFS_IO_PROG -f -c "pwrite -S 0x06 -b 18670 266978 18670" \`; `$XFS_IO_PROG -c "falloc 26450 665194" $SCRATCH_MNT/foobar | _filter_xfs_io`; `$XFS_IO_PROG -c "truncate 542872" $SCRATCH_MNT/foobar | _filter_xfs_io`; `$XFS_IO_PROG -c "fsync" $SCRATCH_MNT/foobar | _filter_xfs_io`; `MD5=`md5sum $SCRATCH_MNT/foobar | cut -f 1 -d ' '`` for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_mkfs >/dev/null 2>&1`; `_scratch_mount "-o compress-force=lzo"`; `_scratch_unmount`; `_check_btrfs_filesystem $SCRATCH_DEV`; `_scratch_mount "-o ro"`; plus 1 more source-matched operations. The core workload then performs these representative operations: `$XFS_IO_PROG -f -c "pwrite -S 0x06 -b 18670 266978 18670" \`; `$XFS_IO_PROG -c "falloc 26450 665194" $SCRATCH_MNT/foobar | _filter_xfs_io`; `$XFS_IO_PROG -c "truncate 542872" $SCRATCH_MNT/foobar | _filter_xfs_io`; `$XFS_IO_PROG -c "fsync" $SCRATCH_MNT/foobar | _filter_xfs_io`; `MD5=`md5sum $SCRATCH_MNT/foobar | cut -f 1 -d ' '``. It also uses background or repeated stress/control loops: `_scratch_mkfs >/dev/null 2>&1`; `for i in `seq 1 27``.

## State and Persistence Behavior
Uses digest checks as durable content signals; forces transaction or file-log persistence with sync/fsync. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on scratch filesystem lifecycle helpers, xfs_io subcommand availability, xfs_io data-shaping commands. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
compressed extents with non-zero offsets or shared references can return stale, zeroed, or mis-cloned data The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
digest output before and after remount/receive must match expected content explicit filesystem check must pass Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/037 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/038 -->
# sources/test-tools/xfstests/tests/btrfs/038

## Purpose
Test for a btrfs incremental send issue where we end up sending a wrong section of data from a file extent if the corresponding file extent is compressed and the respective file extent item has a non zero data offset. The script is categorized by `_begin_fstest` as `auto`, `quick`, `compress`, `send`, and its main coverage is: Btrfs send/receive stream generation, including full sends, incremental parent sends, clone-source roots, received UUID handling, and replay on a freshly formatted scratch filesystem. Btrfs extent cloning/reflink semantics, including inline extents, same-file clones, holes, compressed extents, page-cache coherency, and fsync/log replay persistence. Compressed extent behavior across read, restore, clone, send, defrag, remount, and property inheritance paths. Snapshot creation, readonly snapshot consistency, default subvolume behavior, and interactions between snapshot roots and live/orphaned metadata.

## Important APIs, Types, and Functions
local shell functions: `_cleanup` fstest tags: `auto`, `quick`, `compress`, `send` requirement gates: `_require_scratch`, `_require_fssum`. The important external command surfaces are `_btrfs subvolume snapshot -r $SCRATCH_MNT \`; `_btrfs filesystem sync $SCRATCH_MNT`; `_btrfs send -f $tmp/1.snap $SCRATCH_MNT/mysnap1`; `_btrfs send -f $tmp/clones.snap $SCRATCH_MNT/clones_snap`; `_btrfs send -p $SCRATCH_MNT/mysnap1 \`; `_btrfs receive -f $tmp/1.snap $SCRATCH_MNT`; plus 4 more source-matched operations for Btrfs control and `$XFS_IO_PROG -f -c "truncate 118811" $SCRATCH_MNT/foo`; `$XFS_IO_PROG -c "pwrite -S 0x0d -b 39987 92267 39987" \`; `$XFS_IO_PROG -c "pwrite -S 0x3e -b 80000 200000 80000" \`; `$XFS_IO_PROG -c "pwrite -S 0xdc -b 10000 250000 10000" \`; `$XFS_IO_PROG -c "pwrite -S 0xff -b 10000 300000 10000" \` for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_mkfs >/dev/null 2>&1`; `_scratch_mount "-o compress-force=lzo"`; `_scratch_unmount`; `_check_btrfs_filesystem $SCRATCH_DEV`; `_scratch_mount`; plus 3 more source-matched operations. The core workload then performs these representative operations: `_btrfs subvolume snapshot -r $SCRATCH_MNT \`; `_btrfs filesystem sync $SCRATCH_MNT`; `_btrfs send -f $tmp/1.snap $SCRATCH_MNT/mysnap1`; `_btrfs send -f $tmp/clones.snap $SCRATCH_MNT/clones_snap`; `_btrfs send -p $SCRATCH_MNT/mysnap1 \`; `_btrfs receive -f $tmp/1.snap $SCRATCH_MNT`; `_btrfs receive -f $tmp/clones.snap $SCRATCH_MNT`; `_btrfs receive -f $tmp/2.snap $SCRATCH_MNT`; `$XFS_IO_PROG -f -c "truncate 118811" $SCRATCH_MNT/foo`; `$XFS_IO_PROG -c "pwrite -S 0x0d -b 39987 92267 39987" \`; plus 5 more source-matched operations. It also uses background or repeated stress/control loops: `_scratch_mkfs >/dev/null 2>&1`; plus 1 more source-matched operations.

## State and Persistence Behavior
Creates snapshot roots and compares parent/child root state; persists send streams to temporary files and replays them on a reformatted scratch filesystem; records fssum manifests and validates received trees against them; forces transaction or file-log persistence with sync/fsync. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on scratch filesystem lifecycle helpers, fssum content manifests for send/receive equivalence, btrfs-progs command wrappers, xfs_io data-shaping commands. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
send path ordering can emit invalid rename, rmdir, clone, or path records if inode identity, generation, or delayed-move state is mishandled clone/reflink edge cases can corrupt inline extents, holes, compressed extents, page cache, or log replay metadata compressed extents with non-zero offsets or shared references can return stale, zeroed, or mis-cloned data The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
fssum replay must match original snapshot manifests explicit filesystem check must pass Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/038 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/039 -->
# sources/test-tools/xfstests/tests/btrfs/039

## Purpose
Regression test for a btrfs incremental send issue related to renaming of directories. If at the time of the initial send we have a directory that is a child of a directory with a higher inode number, and then later after the initial full send we rename both the child and parent directories, but without moving any of them, a subsequent incremental send would produce a rename instruction for the child directory that pointed to an invalid path. This made the btrfs receive operation fail. The script is categorized by `_begin_fstest` as `auto`, `quick`, `send`, and its main coverage is: Btrfs send/receive stream generation, including full sends, incremental parent sends, clone-source roots, received UUID handling, and replay on a freshly formatted scratch filesystem. Snapshot creation, readonly snapshot consistency, default subvolume behavior, and interactions between snapshot roots and live/orphaned metadata. Subvolume creation, mounting, deletion, set-default behavior, and placeholder directory semantics.

## Important APIs, Types, and Functions
local shell functions: `_cleanup` fstest tags: `auto`, `quick`, `send` requirement gates: `_require_scratch`, `_require_fssum`. The important external command surfaces are `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/mysnap1`; `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/mysnap2`; `_btrfs send -f $tmp/1.snap $SCRATCH_MNT/mysnap1`; `_btrfs send -p $SCRATCH_MNT/mysnap1 -f $tmp/2.snap \`; `_btrfs receive -f $tmp/1.snap $SCRATCH_MNT`; `_btrfs receive -f $tmp/2.snap $SCRATCH_MNT` for Btrfs control and standard shell/file utilities for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_mkfs >/dev/null 2>&1`; `_scratch_mount`; `_scratch_unmount`; `_check_btrfs_filesystem $SCRATCH_DEV`; plus 4 more source-matched operations. The core workload then performs these representative operations: `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/mysnap1`; `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/mysnap2`; `_btrfs send -f $tmp/1.snap $SCRATCH_MNT/mysnap1`; `_btrfs send -p $SCRATCH_MNT/mysnap1 -f $tmp/2.snap \`; `_btrfs receive -f $tmp/1.snap $SCRATCH_MNT`; `_btrfs receive -f $tmp/2.snap $SCRATCH_MNT`. It also uses background or repeated stress/control loops: `_scratch_mkfs >/dev/null 2>&1`; plus 1 more source-matched operations.

## State and Persistence Behavior
Creates snapshot roots and compares parent/child root state; persists send streams to temporary files and replays them on a reformatted scratch filesystem; records fssum manifests and validates received trees against them. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on scratch filesystem lifecycle helpers, fssum content manifests for send/receive equivalence, btrfs-progs command wrappers. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
send path ordering can emit invalid rename, rmdir, clone, or path records if inode identity, generation, or delayed-move state is mishandled The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
fssum replay must match original snapshot manifests explicit filesystem check must pass Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/039 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/040 -->
# sources/test-tools/xfstests/tests/btrfs/040

## Purpose
Regression test for btrfs incremental send issue where an rmdir instruction was sent multiple times for the same target directory. The number of times depended on the number of hardlinks against the same inode inside the target directory. That inode must have had the highest number of all the inodes that were children of the directory. This made the btrfs receive command fail immediately once it received the second rmdir instruction. The script is categorized by `_begin_fstest` as `auto`, `quick`, `send`, and its main coverage is: Btrfs send/receive stream generation, including full sends, incremental parent sends, clone-source roots, received UUID handling, and replay on a freshly formatted scratch filesystem. Snapshot creation, readonly snapshot consistency, default subvolume behavior, and interactions between snapshot roots and live/orphaned metadata. Subvolume creation, mounting, deletion, set-default behavior, and placeholder directory semantics.

## Important APIs, Types, and Functions
local shell functions: `_cleanup` fstest tags: `auto`, `quick`, `send` requirement gates: `_require_scratch`, `_require_fssum`. The important external command surfaces are `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/mysnap1`; `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/mysnap2`; `_btrfs send -f $tmp/1.snap $SCRATCH_MNT/mysnap1`; `_btrfs send -p $SCRATCH_MNT/mysnap1 -f $tmp/2.snap \`; `_btrfs receive -f $tmp/1.snap $SCRATCH_MNT`; `_btrfs receive -f $tmp/2.snap $SCRATCH_MNT` for Btrfs control and standard shell/file utilities for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_mkfs >/dev/null 2>&1`; `_scratch_mount`; `_scratch_unmount`; `_check_btrfs_filesystem $SCRATCH_DEV`; plus 4 more source-matched operations. The core workload then performs these representative operations: `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/mysnap1`; `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/mysnap2`; `_btrfs send -f $tmp/1.snap $SCRATCH_MNT/mysnap1`; `_btrfs send -p $SCRATCH_MNT/mysnap1 -f $tmp/2.snap \`; `_btrfs receive -f $tmp/1.snap $SCRATCH_MNT`; `_btrfs receive -f $tmp/2.snap $SCRATCH_MNT`. It also uses background or repeated stress/control loops: `_scratch_mkfs >/dev/null 2>&1`; plus 1 more source-matched operations.

## State and Persistence Behavior
Creates snapshot roots and compares parent/child root state; persists send streams to temporary files and replays them on a reformatted scratch filesystem; records fssum manifests and validates received trees against them. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on scratch filesystem lifecycle helpers, fssum content manifests for send/receive equivalence, btrfs-progs command wrappers. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
send path ordering can emit invalid rename, rmdir, clone, or path records if inode identity, generation, or delayed-move state is mishandled The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
fssum replay must match original snapshot manifests explicit filesystem check must pass Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/040 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/041 -->
# sources/test-tools/xfstests/tests/btrfs/041

## Purpose
Test that btrfs-progs' restore command is able to correctly recover files that have compressed extents, specially when the respective file extent items have a non-zero data offset field. Btrfs-progs: fix restore of files with compressed extents The script is categorized by `_begin_fstest` as `auto`, `quick`, `compress`, and its main coverage is: Compressed extent behavior across read, restore, clone, send, defrag, remount, and property inheritance paths.

## Important APIs, Types, and Functions
local shell functions: `_cleanup`, `test_btrfs_restore` fstest tags: `auto`, `quick`, `compress` requirement gates: `_require_test`, `_require_scratch`. The important external command surfaces are `_btrfs restore $SCRATCH_DEV $restore_dir` for Btrfs control and `$XFS_IO_PROG -f -c "pwrite -S 0xff -b 100000 0 100000" -c "fsync" \`; `$XFS_IO_PROG -c "pwrite -S 0xaa -b 100000 100000 100000" -c "fsync" \`; `$XFS_IO_PROG -c "pwrite -S 0x1e -b 2 10000 2" $SCRATCH_MNT/foo \`; `$XFS_IO_PROG -c "pwrite -S 0xd0 -b 11 33000 11" $SCRATCH_MNT/foo \`; `$XFS_IO_PROG -c "pwrite -S 0xbc -b 100 99000 100" $SCRATCH_MNT/foo \`; `md5sum $SCRATCH_MNT/foo | _filter_scratch`; plus 1 more source-matched operations for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_mkfs >/dev/null 2>&1`; `_scratch_mount $OPTIONS`; `_scratch_unmount`. The core workload then performs these representative operations: `_btrfs restore $SCRATCH_DEV $restore_dir`; `$XFS_IO_PROG -f -c "pwrite -S 0xff -b 100000 0 100000" -c "fsync" \`; `$XFS_IO_PROG -c "pwrite -S 0xaa -b 100000 100000 100000" -c "fsync" \`; `$XFS_IO_PROG -c "pwrite -S 0x1e -b 2 10000 2" $SCRATCH_MNT/foo \`; `$XFS_IO_PROG -c "pwrite -S 0xd0 -b 11 33000 11" $SCRATCH_MNT/foo \`; `$XFS_IO_PROG -c "pwrite -S 0xbc -b 100 99000 100" $SCRATCH_MNT/foo \`; `md5sum $SCRATCH_MNT/foo | _filter_scratch`; `md5sum $restore_dir/foo | cut -d ' ' -f 1`. It also uses background or repeated stress/control loops: `_scratch_mkfs >/dev/null 2>&1`.

## State and Persistence Behavior
Uses digest checks as durable content signals; forces transaction or file-log persistence with sync/fsync. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on external test directory storage, scratch filesystem lifecycle helpers, btrfs-progs command wrappers, xfs_io data-shaping commands. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
compressed extents with non-zero offsets or shared references can return stale, zeroed, or mis-cloned data The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
digest output before and after remount/receive must match expected content Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/041 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/042 -->
# sources/test-tools/xfstests/tests/btrfs/042

## Purpose
Test the basic functionality of Quota groups The script is categorized by `_begin_fstest` as `auto`, `quick`, `qgroup`, `limit`, and its main coverage is: Quota group enablement, rescan, limits, accounting of shared/exclusive extents, and crash or deletion paths that can leave qgroup state inconsistent. Subvolume creation, mounting, deletion, set-default behavior, and placeholder directory semantics.

## Important APIs, Types, and Functions
fstest tags: `auto`, `quick`, `qgroup`, `limit` requirement gates: `_require_scratch`, `_require_btrfs_qgroup_report`. The important external command surfaces are `_btrfs quota enable $SCRATCH_MNT`; `_btrfs qgroup create 1/1 $SCRATCH_MNT`; `_btrfs qgroup limit $LIMIT_SIZE 1/1 $SCRATCH_MNT`; `_btrfs subvolume create -i 1/1 \`; `_btrfs filesystem sync $SCRATCH_MNT \` for Btrfs control and `$XFS_IO_PROG -f -d -c 'pwrite -b 4k 0 10m' $SCRATCH_MNT/subv_$i/data \` for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `run_check _scratch_mkfs`; `_scratch_mount`. The core workload then performs these representative operations: `_btrfs quota enable $SCRATCH_MNT`; `_btrfs qgroup create 1/1 $SCRATCH_MNT`; `_btrfs qgroup limit $LIMIT_SIZE 1/1 $SCRATCH_MNT`; `_btrfs subvolume create -i 1/1 \`; `_btrfs filesystem sync $SCRATCH_MNT \`; `$XFS_IO_PROG -f -d -c 'pwrite -b 4k 0 10m' $SCRATCH_MNT/subv_$i/data \`. It also uses background or repeated stress/control loops: `for i in `seq 10 -1 1`; do`; `>> /dev/null 2>&1 &`; `wait`; `>>$seqres.full 2>&1`; plus 2 more source-matched operations.

## State and Persistence Behavior
Forces transaction or file-log persistence with sync/fsync; mutates qgroup metadata and relies on final accounting checks. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on scratch filesystem lifecycle helpers, qgroup reporting support, btrfs-progs command wrappers, xfs_io data-shaping commands. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
qgroup accounting can leak reservations or miscount shared/exclusive extents after snapshots, rescans, deletes, or limits The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
prints `Silence is golden` when no explicit failure path is reached fstests qgroup reporting/checking validates quota consistency Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/042 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/043 -->
# sources/test-tools/xfstests/tests/btrfs/043

## Purpose
Regression test for btrfs incremental send issue where a rmdir instruction is sent against an orphan directory inode which is not empty yet, causing btrfs receive to fail when it attempts to remove the directory. The script is categorized by `_begin_fstest` as `auto`, `quick`, `send`, and its main coverage is: Btrfs send/receive stream generation, including full sends, incremental parent sends, clone-source roots, received UUID handling, and replay on a freshly formatted scratch filesystem. Snapshot creation, readonly snapshot consistency, default subvolume behavior, and interactions between snapshot roots and live/orphaned metadata. Subvolume creation, mounting, deletion, set-default behavior, and placeholder directory semantics.

## Important APIs, Types, and Functions
local shell functions: `_cleanup` fstest tags: `auto`, `quick`, `send` requirement gates: `_require_scratch`, `_require_fssum`. The important external command surfaces are `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/mysnap1`; `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/mysnap2`; `_btrfs send -f $tmp/1.snap $SCRATCH_MNT/mysnap1`; `_btrfs send -p $SCRATCH_MNT/mysnap1 -f $tmp/2.snap \`; `_btrfs receive -f $tmp/1.snap $SCRATCH_MNT`; `_btrfs receive -f $tmp/2.snap $SCRATCH_MNT` for Btrfs control and standard shell/file utilities for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_mkfs >/dev/null 2>&1`; `_scratch_mount`; `_check_scratch_fs`; `_scratch_unmount`; plus 2 more source-matched operations. The core workload then performs these representative operations: `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/mysnap1`; `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/mysnap2`; `_btrfs send -f $tmp/1.snap $SCRATCH_MNT/mysnap1`; `_btrfs send -p $SCRATCH_MNT/mysnap1 -f $tmp/2.snap \`; `_btrfs receive -f $tmp/1.snap $SCRATCH_MNT`; `_btrfs receive -f $tmp/2.snap $SCRATCH_MNT`. It also uses background or repeated stress/control loops: `_scratch_mkfs >/dev/null 2>&1`; plus 1 more source-matched operations.

## State and Persistence Behavior
Creates snapshot roots and compares parent/child root state; persists send streams to temporary files and replays them on a reformatted scratch filesystem; records fssum manifests and validates received trees against them. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on scratch filesystem lifecycle helpers, fssum content manifests for send/receive equivalence, btrfs-progs command wrappers. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
send path ordering can emit invalid rename, rmdir, clone, or path records if inode identity, generation, or delayed-move state is mishandled The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
fssum replay must match original snapshot manifests explicit filesystem check must pass Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/043 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/044 -->
# sources/test-tools/xfstests/tests/btrfs/044

## Purpose
Regression test for a btrfs incremental send issue where under certain scenarios invalid paths for utimes, chown and chmod operations were sent to the send stream, causing btrfs receive to fail. If a directory had a move/rename operation delayed, and none of its parent directories, except for the immediate one, had delayed move/rename operations, after processing the directory's references, the incremental send code would issue invalid paths for utimes, chown and chmod operations. The script is categorized by `_begin_fstest` as `auto`, `quick`, `send`, and its main coverage is: Btrfs send/receive stream generation, including full sends, incremental parent sends, clone-source roots, received UUID handling, and replay on a freshly formatted scratch filesystem. Snapshot creation, readonly snapshot consistency, default subvolume behavior, and interactions between snapshot roots and live/orphaned metadata. Subvolume creation, mounting, deletion, set-default behavior, and placeholder directory semantics.

## Important APIs, Types, and Functions
local shell functions: `_cleanup` fstest tags: `auto`, `quick`, `send` requirement gates: `_require_scratch`, `_require_fssum`. The important external command surfaces are `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/mysnap1`; `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/mysnap2`; `_btrfs send -f $tmp/1.snap $SCRATCH_MNT/mysnap1`; `_btrfs send -p $SCRATCH_MNT/mysnap1 -f $tmp/2.snap \`; `_btrfs receive -f $tmp/1.snap $SCRATCH_MNT`; `_btrfs receive -f $tmp/2.snap $SCRATCH_MNT` for Btrfs control and standard shell/file utilities for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_mkfs >/dev/null 2>&1`; `_scratch_mount`; `_check_scratch_fs`; `_scratch_unmount`; plus 2 more source-matched operations. The core workload then performs these representative operations: `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/mysnap1`; `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/mysnap2`; `_btrfs send -f $tmp/1.snap $SCRATCH_MNT/mysnap1`; `_btrfs send -p $SCRATCH_MNT/mysnap1 -f $tmp/2.snap \`; `_btrfs receive -f $tmp/1.snap $SCRATCH_MNT`; `_btrfs receive -f $tmp/2.snap $SCRATCH_MNT`. It also uses background or repeated stress/control loops: `_scratch_mkfs >/dev/null 2>&1`; plus 1 more source-matched operations.

## State and Persistence Behavior
Creates snapshot roots and compares parent/child root state; persists send streams to temporary files and replays them on a reformatted scratch filesystem; records fssum manifests and validates received trees against them. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on scratch filesystem lifecycle helpers, fssum content manifests for send/receive equivalence, btrfs-progs command wrappers. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
send path ordering can emit invalid rename, rmdir, clone, or path records if inode identity, generation, or delayed-move state is mishandled The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
fssum replay must match original snapshot manifests explicit filesystem check must pass Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/044 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/045 -->
# sources/test-tools/xfstests/tests/btrfs/045

## Purpose
Regression test for a btrfs incremental send issue where the kernel failed to build paths strings. This resulted either in sending a wrong path string to the send stream or entering an infinite loop when building it. This happened in the following scenarios: 1) A directory was made a child of another directory which has a lower inode number and has a pending move/rename operation or there's some non-direct ancestor directory with a higher inode number that was renamed/moved too. This made the incremental send code go into an infinite loop when building a path string; 2) A directory was made a child of another directory which has a higher inode number, but the new parent wasn't moved nor renamed. Instead some other ancestor higher in the hierarchy, with an higher inode number too, was moved/renamed too. This made the incremental send code go into an infinite loop when building a path string; 3) An orphan directory is created and at least one of its non-immediate descendent directories have a pending move/rename operation. This made an incremental send issue to the send stream an invalid path string that didn't account for the orphan ancestor directory. The script is categorized by `_begin_fstest` as `auto`, `quick`, `send`, and its main coverage is: Btrfs send/receive stream generation, including full sends, incremental parent sends, clone-source roots, received UUID handling, and replay on a freshly formatted scratch filesystem.

## Important APIs, Types, and Functions
local shell functions: `_cleanup` fstest tags: `auto`, `quick`, `send` requirement gates: `_require_scratch`, `_require_fssum`. The important external command surfaces are `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/mysnap1`; `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/mysnap2`; `_btrfs send -f $tmp/1.snap $SCRATCH_MNT/mysnap1`; `_btrfs send -p $SCRATCH_MNT/mysnap1 -f $tmp/2.snap \`; `_btrfs receive -f $tmp/1.snap $SCRATCH_MNT`; `_btrfs receive -f $tmp/2.snap $SCRATCH_MNT` for Btrfs control and standard shell/file utilities for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_mkfs >/dev/null 2>&1`; `_scratch_mount`; `_check_scratch_fs`; `_scratch_unmount`; plus 2 more source-matched operations. The core workload then performs these representative operations: `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/mysnap1`; `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/mysnap2`; `_btrfs send -f $tmp/1.snap $SCRATCH_MNT/mysnap1`; `_btrfs send -p $SCRATCH_MNT/mysnap1 -f $tmp/2.snap \`; `_btrfs receive -f $tmp/1.snap $SCRATCH_MNT`; `_btrfs receive -f $tmp/2.snap $SCRATCH_MNT`. It also uses background or repeated stress/control loops: `_scratch_mkfs >/dev/null 2>&1`; plus 1 more source-matched operations.

## State and Persistence Behavior
Creates snapshot roots and compares parent/child root state; persists send streams to temporary files and replays them on a reformatted scratch filesystem; records fssum manifests and validates received trees against them. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on scratch filesystem lifecycle helpers, fssum content manifests for send/receive equivalence, btrfs-progs command wrappers. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
send path ordering can emit invalid rename, rmdir, clone, or path records if inode identity, generation, or delayed-move state is mishandled The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
fssum replay must match original snapshot manifests explicit filesystem check must pass Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/045 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/046 -->
# sources/test-tools/xfstests/tests/btrfs/046

## Purpose
Regression test for the btrfs incremental send feature, where the kernel would incorrectly consider a range of a file as a hole and send a stream of 0 bytes to the destination (send stream) that would overwrite the corresponding file region. The script is categorized by `_begin_fstest` as `auto`, `quick`, `send`, `preallocrw`, and its main coverage is: Btrfs send/receive stream generation, including full sends, incremental parent sends, clone-source roots, received UUID handling, and replay on a freshly formatted scratch filesystem. Snapshot creation, readonly snapshot consistency, default subvolume behavior, and interactions between snapshot roots and live/orphaned metadata. Subvolume creation, mounting, deletion, set-default behavior, and placeholder directory semantics. Preallocated extent handling, fallocate/fpunch behavior, and distinguishing real data from holes during send or clone.

## Important APIs, Types, and Functions
local shell functions: `_cleanup` fstest tags: `auto`, `quick`, `send`, `preallocrw` requirement gates: `_require_test`, `_require_scratch`, `_require_xfs_io_command`, `_require_fssum`. The important external command surfaces are `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/mysnap0`; `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/mysnap1`; `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/mysnap2`; `_btrfs send -f $send_files_dir/1.snap $SCRATCH_MNT/mysnap1`; `_btrfs send -p $SCRATCH_MNT/mysnap1 -f $send_files_dir/2.snap \`; `_btrfs receive -f $send_files_dir/1.snap $SCRATCH_MNT`; plus 1 more source-matched operations for Btrfs control and `$XFS_IO_PROG -f -c "falloc -k 0 268435456" $SCRATCH_MNT/foo`; `$XFS_IO_PROG -c "pwrite -S 0x01 -b 9216 16190218 9216" $SCRATCH_MNT/foo \`; `$XFS_IO_PROG -c "pwrite -S 0x02 -b 1121 198720104 1121" $SCRATCH_MNT/foo \`; `$XFS_IO_PROG -c "pwrite -S 0x05 -b 9216 107887439 9216" $SCRATCH_MNT/foo \`; `$XFS_IO_PROG -c "pwrite -S 0x06 -b 9216 225520207 9216" $SCRATCH_MNT/foo \`; `$XFS_IO_PROG -c "pwrite -S 0x07 -b 67584 102138300 67584" $SCRATCH_MNT/foo \`; plus 103 more source-matched operations for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_mkfs >/dev/null 2>&1`; `_scratch_mount`; `_check_scratch_fs`; `_scratch_unmount`; plus 2 more source-matched operations. The core workload then performs these representative operations: `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/mysnap0`; `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/mysnap1`; `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/mysnap2`; `_btrfs send -f $send_files_dir/1.snap $SCRATCH_MNT/mysnap1`; `_btrfs send -p $SCRATCH_MNT/mysnap1 -f $send_files_dir/2.snap \`; `_btrfs receive -f $send_files_dir/1.snap $SCRATCH_MNT`; `_btrfs receive -f $send_files_dir/2.snap $SCRATCH_MNT`; `$XFS_IO_PROG -f -c "falloc -k 0 268435456" $SCRATCH_MNT/foo`; `$XFS_IO_PROG -c "pwrite -S 0x01 -b 9216 16190218 9216" $SCRATCH_MNT/foo \`; `$XFS_IO_PROG -c "pwrite -S 0x02 -b 1121 198720104 1121" $SCRATCH_MNT/foo \`; plus 106 more source-matched operations. It also uses background or repeated stress/control loops: `_scratch_mkfs >/dev/null 2>&1`; plus 1 more source-matched operations.

## State and Persistence Behavior
Creates snapshot roots and compares parent/child root state; persists send streams to temporary files and replays them on a reformatted scratch filesystem; records fssum manifests and validates received trees against them; uses digest checks as durable content signals. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on external test directory storage, scratch filesystem lifecycle helpers, xfs_io subcommand availability, fssum content manifests for send/receive equivalence, btrfs-progs command wrappers, xfs_io data-shaping commands. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
send path ordering can emit invalid rename, rmdir, clone, or path records if inode identity, generation, or delayed-move state is mishandled The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
fssum replay must match original snapshot manifests digest output before and after remount/receive must match expected content explicit filesystem check must pass Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/046 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/047 -->
# sources/test-tools/xfstests/tests/btrfs/047

## Purpose
Test that we can't set xattrs on subvolume placeholder directories. Regression test for Btrfs: disable xattr operations on subvolume directories. The script is categorized by `_begin_fstest` as `auto`, `quick`, `snapshot`, `attr`, and its main coverage is: Snapshot creation, readonly snapshot consistency, default subvolume behavior, and interactions between snapshot roots and live/orphaned metadata. Subvolume creation, mounting, deletion, set-default behavior, and placeholder directory semantics.

## Important APIs, Types, and Functions
fstest tags: `auto`, `quick`, `snapshot`, `attr` requirement gates: `_require_attrs`, `_require_scratch`. The important external command surfaces are `$BTRFS_UTIL_PROG subvolume create "$SCRATCH_MNT/parent" >>$seqres.full`; `$BTRFS_UTIL_PROG subvolume create "$SCRATCH_MNT/parent/child" >>$seqres.full`; `$BTRFS_UTIL_PROG subvolume snapshot "$SCRATCH_MNT/parent" "$SCRATCH_MNT/snapshot" >>$seqres.full`; `$BTRFS_UTIL_PROG filesystem sync "$SCRATCH_MNT" >>$seqres.full` for Btrfs control and `$SETFATTR_PROG -n user.test -v foo "$SCRATCH_MNT/snapshot/child" |& _filter_scratch` for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_mkfs >/dev/null 2>&1`; `_scratch_mount`. The core workload then performs these representative operations: `$BTRFS_UTIL_PROG subvolume create "$SCRATCH_MNT/parent" >>$seqres.full`; `$BTRFS_UTIL_PROG subvolume create "$SCRATCH_MNT/parent/child" >>$seqres.full`; `$BTRFS_UTIL_PROG subvolume snapshot "$SCRATCH_MNT/parent" "$SCRATCH_MNT/snapshot" >>$seqres.full`; `$BTRFS_UTIL_PROG filesystem sync "$SCRATCH_MNT" >>$seqres.full`; `$SETFATTR_PROG -n user.test -v foo "$SCRATCH_MNT/snapshot/child" |& _filter_scratch`. It also uses background or repeated stress/control loops: `_scratch_mkfs >/dev/null 2>&1`; `$SETFATTR_PROG -n user.test -v foo "$SCRATCH_MNT/snapshot/child" |& _filter_scratch`.

## State and Persistence Behavior
Creates snapshot roots and compares parent/child root state; forces transaction or file-log persistence with sync/fsync. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on extended attribute tooling, scratch filesystem lifecycle helpers, btrfs-progs command wrappers. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
the test is sensitive to kernel, btrfs-progs, and fstests helper behavior because it verifies a narrow historical regression The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
successful command completion and fstests cleanup checks are the primary signal Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/047 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/048 -->
# sources/test-tools/xfstests/tests/btrfs/048

## Purpose
Btrfs properties test. The btrfs properties feature was introduced in the linux kernel 3.14. Fails without the kernel patches: The script is categorized by `_begin_fstest` as `auto`, `quick`, `compress`, `subvol`, `snapshot`, `send`, and its main coverage is: Btrfs send/receive stream generation, including full sends, incremental parent sends, clone-source roots, received UUID handling, and replay on a freshly formatted scratch filesystem. Compressed extent behavior across read, restore, clone, send, defrag, remount, and property inheritance paths. Snapshot creation, readonly snapshot consistency, default subvolume behavior, and interactions between snapshot roots and live/orphaned metadata. Subvolume creation, mounting, deletion, set-default behavior, and placeholder directory semantics.

## Important APIs, Types, and Functions
local shell functions: `_cleanup` fstest tags: `auto`, `quick`, `compress`, `subvol`, `snapshot`, `send` requirement gates: `_require_test`, `_require_scratch`, `_require_btrfs_command`, `_require_btrfs_command`, `_require_btrfs_no_nodatacow`, `_require_btrfs_no_nodatasum`. The important external command surfaces are `$BTRFS_UTIL_PROG property get $SCRATCH_MNT label`; `$BTRFS_UTIL_PROG property set $SCRATCH_MNT label foobar`; `$BTRFS_UTIL_PROG property get $SCRATCH_MNT`; `$BTRFS_UTIL_PROG property set $SCRATCH_MNT label ''`; `$BTRFS_UTIL_PROG property get $SCRATCH_MNT/testdir label 2>&1 |`; `_btrfs subvolume create $SCRATCH_MNT/sv1`; plus 71 more source-matched operations for Btrfs control and standard shell/file utilities for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_mkfs >/dev/null 2>&1`; `_scratch_mount`; `_scratch_unmount`; `_check_scratch_fs`; plus 12 more source-matched operations. The core workload then performs these representative operations: `$BTRFS_UTIL_PROG property get $SCRATCH_MNT label`; `$BTRFS_UTIL_PROG property set $SCRATCH_MNT label foobar`; `$BTRFS_UTIL_PROG property get $SCRATCH_MNT`; `$BTRFS_UTIL_PROG property set $SCRATCH_MNT label ''`; `$BTRFS_UTIL_PROG property get $SCRATCH_MNT/testdir label 2>&1 |`; `_btrfs subvolume create $SCRATCH_MNT/sv1`; `$BTRFS_UTIL_PROG property get $SCRATCH_MNT/sv1 ro`; `$BTRFS_UTIL_PROG property set $SCRATCH_MNT/sv1 ro foo 2>&1 |`; `$BTRFS_UTIL_PROG property set $SCRATCH_MNT/sv1 ro true`; `$BTRFS_UTIL_PROG property set $SCRATCH_MNT/sv1 ro false`; plus 67 more source-matched operations. It also uses background or repeated stress/control loops: `_scratch_mkfs >/dev/null 2>&1`; `$BTRFS_UTIL_PROG property get $SCRATCH_MNT/testdir label 2>&1 |`; `$BTRFS_UTIL_PROG property set $SCRATCH_MNT/sv1 ro foo 2>&1 |`; `touch $SCRATCH_MNT/sv1/foobar 2>&1 | _filter_scratch`; `foo 2>&1 | _filter_scratch |`; `$BTRFS_UTIL_PROG property set $SCRATCH_MNT compression 'lz' 2>&1 | _filter_scratch`; plus 10 more source-matched operations.

## State and Persistence Behavior
Creates snapshot roots and compares parent/child root state; persists send streams to temporary files and replays them on a reformatted scratch filesystem; forces transaction or file-log persistence with sync/fsync. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on external test directory storage, scratch filesystem lifecycle helpers, specific btrfs-progs subcommand availability, btrfs-progs command wrappers, Btrfs-specific output filters. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
send path ordering can emit invalid rename, rmdir, clone, or path records if inode identity, generation, or delayed-move state is mishandled compressed extents with non-zero offsets or shared references can return stale, zeroed, or mis-cloned data The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
explicit filesystem check must pass Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/048 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/049 -->
# sources/test-tools/xfstests/tests/btrfs/049

## Purpose
Ensure that it's possible to add a device when we have a paused balance and the filesystem is mounted with skip_balance. The issue is fixed by a patch titled "btrfs: allow device add if balance is paused" The script is categorized by `_begin_fstest` as `quick`, `balance`, `auto`, and its main coverage is: Multi-device balance stress, including mutual exclusion with replace/delete operations and post-stress scrub/fsck validation. Device replacement or deletion against RAID-style scratch device pools, including device-mapper error injection and filesystem show verification. Mount option transitions, especially flushoncommit, thread_pool resizing, and compression remount changes.

## Important APIs, Types, and Functions
local shell functions: `check_exclusive_ops` fstest tags: `quick`, `balance`, `auto` requirement gates: `_require_scratch_swapfile`, `_require_scratch_dev_pool`. The important external command surfaces are `$BTRFS_UTIL_PROG device remove 2 $SCRATCH_MNT &>/dev/null`; `$BTRFS_UTIL_PROG filesystem resize -5m $SCRATCH_MNT &> /dev/null`; `$BTRFS_UTIL_PROG replace start -B 2 $SPARE_DEV $SCRATCH_MNT &> /dev/null`; `$BTRFS_UTIL_PROG balance pause "$SCRATCH_MNT"`; `$BTRFS_UTIL_PROG balance status "$SCRATCH_MNT" | grep -q paused`; `$BTRFS_UTIL_PROG device add -K -f $SPARE_DEV "$SCRATCH_MNT"`; plus 4 more source-matched operations for Btrfs control and standard shell/file utilities for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_pool_mkfs >/dev/null`; `_scratch_mount`; `_scratch_cycle_mount "skip_balance"`. The core workload then performs these representative operations: `$BTRFS_UTIL_PROG device remove 2 $SCRATCH_MNT &>/dev/null`; `$BTRFS_UTIL_PROG filesystem resize -5m $SCRATCH_MNT &> /dev/null`; `$BTRFS_UTIL_PROG replace start -B 2 $SPARE_DEV $SCRATCH_MNT &> /dev/null`; `$BTRFS_UTIL_PROG balance pause "$SCRATCH_MNT"`; `$BTRFS_UTIL_PROG balance status "$SCRATCH_MNT" | grep -q paused`; `$BTRFS_UTIL_PROG device add -K -f $SPARE_DEV "$SCRATCH_MNT"`; `$BTRFS_UTIL_PROG balance resume "$SCRATCH_MNT" &>/dev/null`; plus 3 more source-matched operations. It also uses background or repeated stress/control loops: `$BTRFS_UTIL_PROG device remove 2 $SCRATCH_MNT &>/dev/null`; `$BTRFS_UTIL_PROG filesystem resize -5m $SCRATCH_MNT &> /dev/null`; `$BTRFS_UTIL_PROG replace start -B 2 $SPARE_DEV $SCRATCH_MNT &> /dev/null`; `swapon "$swapfile" &> /dev/null`; `_run_fsstress $args >>$seqres.full`; `$BTRFS_UTIL_PROG balance resume "$SCRATCH_MNT" &>/dev/null`; plus 2 more source-matched operations.

## State and Persistence Behavior
Mutates a freshly formatted scratch filesystem and relies on command status plus fstests cleanup checks. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on multi-device scratch pool, btrfs-progs command wrappers. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
multi-device operations can race with stress workers, mutually exclusive jobs, scrub, or injected device failure The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
prints `Silence is golden` when no explicit failure path is reached Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/049 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/050 -->
# sources/test-tools/xfstests/tests/btrfs/050

## Purpose
Regression for btrfs send when an inode only has extended references associated to it (no regular references present). This used to cause incorrect access to a b+tree leaf, where an extended reference item was accessed as if it were a regular reference item, causing unexpected and unpredictable behaviour such as producing a random/weird path string or a crash. The script is categorized by `_begin_fstest` as `auto`, `quick`, `send`, and its main coverage is: Btrfs send/receive stream generation, including full sends, incremental parent sends, clone-source roots, received UUID handling, and replay on a freshly formatted scratch filesystem. Snapshot creation, readonly snapshot consistency, default subvolume behavior, and interactions between snapshot roots and live/orphaned metadata. Subvolume creation, mounting, deletion, set-default behavior, and placeholder directory semantics.

## Important APIs, Types, and Functions
local shell functions: `_cleanup` fstest tags: `auto`, `quick`, `send` requirement gates: `_require_test`, `_require_scratch`, `_require_fssum`. The important external command surfaces are `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/mysnap1`; `_btrfs send -f $send_files_dir/1.snap $SCRATCH_MNT/mysnap1`; `_btrfs receive -f $send_files_dir/1.snap $SCRATCH_MNT` for Btrfs control and standard shell/file utilities for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_mkfs "-O extref" >/dev/null 2>&1`; `_scratch_mount`; `_scratch_unmount`; `_check_scratch_fs`; `_scratch_mkfs >/dev/null 2>&1`; plus 1 more source-matched operations. The core workload then performs these representative operations: `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/mysnap1`; `_btrfs send -f $send_files_dir/1.snap $SCRATCH_MNT/mysnap1`; `_btrfs receive -f $send_files_dir/1.snap $SCRATCH_MNT`. It also uses background or repeated stress/control loops: `_scratch_mkfs "-O extref" >/dev/null 2>&1`; `for i in `seq 1 $NUM_LINKS`; do`; `_scratch_mkfs >/dev/null 2>&1`; plus 1 more source-matched operations.

## State and Persistence Behavior
Creates snapshot roots and compares parent/child root state; persists send streams to temporary files and replays them on a reformatted scratch filesystem; records fssum manifests and validates received trees against them. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on external test directory storage, scratch filesystem lifecycle helpers, fssum content manifests for send/receive equivalence, btrfs-progs command wrappers. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
send path ordering can emit invalid rename, rmdir, clone, or path records if inode identity, generation, or delayed-move state is mishandled The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
fssum replay must match original snapshot manifests explicit filesystem check must pass Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/050 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/051 -->
# sources/test-tools/xfstests/tests/btrfs/051

## Purpose
Regression test for btrfs send where long paths (exceeding 230 characters) made send produce paths with random characters from a memory buffer returned by kmalloc, as send forgot to populate the new buffer with the path string. The script is categorized by `_begin_fstest` as `auto`, `quick`, `send`, and its main coverage is: Btrfs send/receive stream generation, including full sends, incremental parent sends, clone-source roots, received UUID handling, and replay on a freshly formatted scratch filesystem. Snapshot creation, readonly snapshot consistency, default subvolume behavior, and interactions between snapshot roots and live/orphaned metadata. Subvolume creation, mounting, deletion, set-default behavior, and placeholder directory semantics.

## Important APIs, Types, and Functions
local shell functions: `_cleanup` fstest tags: `auto`, `quick`, `send` requirement gates: `_require_test`, `_require_scratch`, `_require_fssum`. The important external command surfaces are `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/mysnap1`; `_btrfs send -f $send_files_dir/1.snap $SCRATCH_MNT/mysnap1`; `_btrfs receive -f $send_files_dir/1.snap $SCRATCH_MNT` for Btrfs control and standard shell/file utilities for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_mkfs >/dev/null 2>&1`; `_scratch_mount`; `_scratch_unmount`; `_check_scratch_fs`; plus 2 more source-matched operations. The core workload then performs these representative operations: `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/mysnap1`; `_btrfs send -f $send_files_dir/1.snap $SCRATCH_MNT/mysnap1`; `_btrfs receive -f $send_files_dir/1.snap $SCRATCH_MNT`. It also uses background or repeated stress/control loops: `_scratch_mkfs >/dev/null 2>&1`; plus 1 more source-matched operations.

## State and Persistence Behavior
Creates snapshot roots and compares parent/child root state; persists send streams to temporary files and replays them on a reformatted scratch filesystem; records fssum manifests and validates received trees against them. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on external test directory storage, scratch filesystem lifecycle helpers, fssum content manifests for send/receive equivalence, btrfs-progs command wrappers. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
send path ordering can emit invalid rename, rmdir, clone, or path records if inode identity, generation, or delayed-move state is mishandled The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
fssum replay must match original snapshot manifests explicit filesystem check must pass Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/051 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/052 -->
# sources/test-tools/xfstests/tests/btrfs/052

## Purpose
Verify that the btrfs ioctl clone operation can operate on the same file as a source and target. That is, clone extents within the same file. The script is categorized by `_begin_fstest` as `auto`, `quick`, `clone`, `compress`, and its main coverage is: Btrfs extent cloning/reflink semantics, including inline extents, same-file clones, holes, compressed extents, page-cache coherency, and fsync/log replay persistence. Compressed extent behavior across read, restore, clone, send, defrag, remount, and property inheritance paths.

## Important APIs, Types, and Functions
local shell functions: `_cleanup`, `test_btrfs_clone_same_file` fstest tags: `auto`, `quick`, `clone`, `compress` requirement gates: `_require_scratch`, `_require_cloner`. The important external command surfaces are `_btrfs filesystem defragment $SCRATCH_MNT/foo` for Btrfs control and `$XFS_IO_PROG -f -c "pwrite -S 0x01 -b $EXTENT_SIZE $OFFSET $EXTENT_SIZE" $SCRATCH_MNT/foo \`; `$XFS_IO_PROG -c "pwrite -S 0x02 -b $EXTENT_SIZE $OFFSET $EXTENT_SIZE" $SCRATCH_MNT/foo \`; `$XFS_IO_PROG -c "pwrite -S 0x03 -b $EXTENT_SIZE $OFFSET $EXTENT_SIZE" $SCRATCH_MNT/foo \`; `$XFS_IO_PROG -c "pwrite -S 0x04 -b $EXTENT_SIZE $OFFSET $EXTENT_SIZE" $SCRATCH_MNT/foo \`; `$XFS_IO_PROG -c "pwrite -S 0x05 -b $EXTENT_SIZE $OFFSET $EXTENT_SIZE" $SCRATCH_MNT/foo \`; `od -t x1 $SCRATCH_MNT/foo | _filter_od`; plus 13 more source-matched operations for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_mkfs >/dev/null 2>&1`; `_scratch_mount $MOUNT_OPTIONS`; `_scratch_cycle_mount`; `_check_scratch_fs`; `_scratch_unmount`; plus 4 more source-matched operations. The core workload then performs these representative operations: `_btrfs filesystem defragment $SCRATCH_MNT/foo`; `$XFS_IO_PROG -f -c "pwrite -S 0x01 -b $EXTENT_SIZE $OFFSET $EXTENT_SIZE" $SCRATCH_MNT/foo \`; `$XFS_IO_PROG -c "pwrite -S 0x02 -b $EXTENT_SIZE $OFFSET $EXTENT_SIZE" $SCRATCH_MNT/foo \`; `$XFS_IO_PROG -c "pwrite -S 0x03 -b $EXTENT_SIZE $OFFSET $EXTENT_SIZE" $SCRATCH_MNT/foo \`; `$XFS_IO_PROG -c "pwrite -S 0x04 -b $EXTENT_SIZE $OFFSET $EXTENT_SIZE" $SCRATCH_MNT/foo \`; `$XFS_IO_PROG -c "pwrite -S 0x05 -b $EXTENT_SIZE $OFFSET $EXTENT_SIZE" $SCRATCH_MNT/foo \`; `od -t x1 $SCRATCH_MNT/foo | _filter_od`; `$CLONER_PROG -s $((2 * $BLOCK_SIZE)) -d $((2 * $BLOCK_SIZE)) \`; `$CLONER_PROG -s $((1 * $BLOCK_SIZE)) -d $((2 * $BLOCK_SIZE)) \`; `$CLONER_PROG -s $((6 * $BLOCK_SIZE)) -d 0 -l $((2 * $BLOCK_SIZE)) \`; plus 10 more source-matched operations. It also uses background or repeated stress/control loops: `_scratch_mkfs >/dev/null 2>&1`.

## State and Persistence Behavior
Forces transaction or file-log persistence with sync/fsync. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on scratch filesystem lifecycle helpers, btrfs clone ioctl exerciser, btrfs-progs command wrappers, xfs_io data-shaping commands. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
clone/reflink edge cases can corrupt inline extents, holes, compressed extents, page cache, or log replay metadata compressed extents with non-zero offsets or shared references can return stale, zeroed, or mis-cloned data The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
hex dumps expose exact byte-level clone or hole behavior explicit filesystem check must pass Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/052 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/053 -->
# sources/test-tools/xfstests/tests/btrfs/053

## Purpose
Verify that btrfs send is able to replicate xattrs larger than PATH_MAX. This is possible if the b+tree leaf size is larger than 4Kb (mkfs.btrfs's default is max(16Kb, PAGE_SIZE) as of btrfs-progs v3.12, and max(4Kb, PAGE_SIZE in older versions). The script is categorized by `_begin_fstest` as `auto`, `quick`, `send`, and its main coverage is: Btrfs send/receive stream generation, including full sends, incremental parent sends, clone-source roots, received UUID handling, and replay on a freshly formatted scratch filesystem. Snapshot creation, readonly snapshot consistency, default subvolume behavior, and interactions between snapshot roots and live/orphaned metadata. Subvolume creation, mounting, deletion, set-default behavior, and placeholder directory semantics.

## Important APIs, Types, and Functions
local shell functions: `_cleanup` fstest tags: `auto`, `quick`, `send` requirement gates: `_require_test`, `_require_scratch`, `_require_fssum`, `_require_attrs`. The important external command surfaces are `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/mysnap1`; `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/mysnap2`; `_btrfs send -f $send_files_dir/1.snap $SCRATCH_MNT/mysnap1`; `_btrfs send -p $SCRATCH_MNT/mysnap1 -f $send_files_dir/2.snap \`; `_btrfs receive -f $send_files_dir/1.snap $SCRATCH_MNT`; `_btrfs receive -f $send_files_dir/2.snap $SCRATCH_MNT` for Btrfs control and `$SETFATTR_PROG -n user.xattr_name_1 -v `$PERL_PROG -e 'print "A" x 6000;'` \`; `$SETFATTR_PROG -n user.xattr_name_1 -v `$PERL_PROG -e 'print "Z" x 6666;'` \`; `$SETFATTR_PROG -n user.xattr_name_2 -v `$PERL_PROG -e 'print "U" x 5555;'` \` for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_mkfs "--nodesize $leaf_size" >> $seqres.full 2>&1 || _fail "mkfs failed"`; `_scratch_mount`; `_scratch_unmount`; `_check_scratch_fs`; plus 2 more source-matched operations. The core workload then performs these representative operations: `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/mysnap1`; `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/mysnap2`; `_btrfs send -f $send_files_dir/1.snap $SCRATCH_MNT/mysnap1`; `_btrfs send -p $SCRATCH_MNT/mysnap1 -f $send_files_dir/2.snap \`; `_btrfs receive -f $send_files_dir/1.snap $SCRATCH_MNT`; `_btrfs receive -f $send_files_dir/2.snap $SCRATCH_MNT`; `$SETFATTR_PROG -n user.xattr_name_1 -v `$PERL_PROG -e 'print "A" x 6000;'` \`; `$SETFATTR_PROG -n user.xattr_name_1 -v `$PERL_PROG -e 'print "Z" x 6666;'` \`; `$SETFATTR_PROG -n user.xattr_name_2 -v `$PERL_PROG -e 'print "U" x 5555;'` \`. It also uses background or repeated stress/control loops: `_scratch_mkfs "--nodesize $leaf_size" >> $seqres.full 2>&1 || _fail "mkfs failed"`; plus 1 more source-matched operations.

## State and Persistence Behavior
Creates snapshot roots and compares parent/child root state; persists send streams to temporary files and replays them on a reformatted scratch filesystem; records fssum manifests and validates received trees against them. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on external test directory storage, scratch filesystem lifecycle helpers, fssum content manifests for send/receive equivalence, extended attribute tooling, btrfs-progs command wrappers. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
send path ordering can emit invalid rename, rmdir, clone, or path records if inode identity, generation, or delayed-move state is mishandled The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
fssum replay must match original snapshot manifests explicit filesystem check must pass Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/053 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/054 -->
# sources/test-tools/xfstests/tests/btrfs/054

## Purpose
Regression test for a btrfs incremental send issue where the difference between the snapshots used by the incremental send consists of one of these cases: 1) First snapshot has a directory with name X and in the second snapshot that directory doesn't exist anymore but a subvolume/snapshot with the same name (X) exists; 2) First snapshot has a subvolume/snapshot with name X and in the second snapshot that subvolume/snapshot doesn't exist anymore (might have been replaced by a directory with the same name or not). The script is categorized by `_begin_fstest` as `auto`, `quick`, `send`, and its main coverage is: Btrfs send/receive stream generation, including full sends, incremental parent sends, clone-source roots, received UUID handling, and replay on a freshly formatted scratch filesystem. Device replacement or deletion against RAID-style scratch device pools, including device-mapper error injection and filesystem show verification. Snapshot creation, readonly snapshot consistency, default subvolume behavior, and interactions between snapshot roots and live/orphaned metadata. Subvolume creation, mounting, deletion, set-default behavior, and placeholder directory semantics.

## Important APIs, Types, and Functions
local shell functions: `_cleanup` fstest tags: `auto`, `quick`, `send` requirement gates: `_require_test`, `_require_scratch`. The important external command surfaces are `_btrfs subvolume create $SCRATCH_MNT/first_subvol`; `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/mysnap1`; `_btrfs subvolume create $SCRATCH_MNT/testdir`; `_btrfs subvolume delete $SCRATCH_MNT/first_subvol`; `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/mysnap2`; `_btrfs send -f $send_files_dir/1.snap $SCRATCH_MNT/mysnap1`; plus 3 more source-matched operations for Btrfs control and standard shell/file utilities for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_mkfs >/dev/null 2>&1`; `_scratch_mount`; `_scratch_unmount`; `_check_scratch_fs`; plus 2 more source-matched operations. The core workload then performs these representative operations: `_btrfs subvolume create $SCRATCH_MNT/first_subvol`; `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/mysnap1`; `_btrfs subvolume create $SCRATCH_MNT/testdir`; `_btrfs subvolume delete $SCRATCH_MNT/first_subvol`; `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/mysnap2`; `_btrfs send -f $send_files_dir/1.snap $SCRATCH_MNT/mysnap1`; `_btrfs send -p $SCRATCH_MNT/mysnap1 -f $send_files_dir/2.snap \`; `_btrfs receive -f $send_files_dir/1.snap $SCRATCH_MNT`; `_btrfs receive -f $send_files_dir/2.snap $SCRATCH_MNT`. It also uses background or repeated stress/control loops: `_scratch_mkfs >/dev/null 2>&1`; `[ -e $SCRATCH_MNT/first_subvol ] && \`; `[ -e $SCRATCH_MNT/testdir ] && \`; plus 1 more source-matched operations.

## State and Persistence Behavior
Creates snapshot roots and compares parent/child root state; persists send streams to temporary files and replays them on a reformatted scratch filesystem. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on external test directory storage, scratch filesystem lifecycle helpers, btrfs-progs command wrappers. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
send path ordering can emit invalid rename, rmdir, clone, or path records if inode identity, generation, or delayed-move state is mishandled multi-device operations can race with stress workers, mutually exclusive jobs, scrub, or injected device failure The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
explicit filesystem check must pass Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/054 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/055 -->
# sources/test-tools/xfstests/tests/btrfs/055

## Purpose
Regression test for the btrfs ioctl clone operation when the source range contains hole(s) and the FS has the NO_HOLES feature enabled (file holes don't need file extent items in the btree to represent them). The script is categorized by `_begin_fstest` as `auto`, `quick`, `clone`, and its main coverage is: Btrfs extent cloning/reflink semantics, including inline extents, same-file clones, holes, compressed extents, page-cache coherency, and fsync/log replay persistence.

## Important APIs, Types, and Functions
local shell functions: `_cleanup`, `test_btrfs_clone_with_holes` fstest tags: `auto`, `quick`, `clone` requirement gates: `_require_scratch`, `_require_cloner`, `_require_btrfs_fs_feature`, `_require_btrfs_mkfs_feature`. The important external command surfaces are `_btrfs`/`$BTRFS_UTIL_PROG` where present for Btrfs control and `$XFS_IO_PROG -s -f -c "pwrite -S 0x01 -b $EXTENT_SIZE $OFFSET $EXTENT_SIZE" \`; `$XFS_IO_PROG -s -f -c "pwrite -S 0x02 -b $EXTENT_SIZE $OFFSET $EXTENT_SIZE" \`; `$XFS_IO_PROG -s -f -c "pwrite -S 0x04 -b $EXTENT_SIZE $OFFSET $EXTENT_SIZE" \`; `$XFS_IO_PROG -s -f -c "pwrite -S 0x05 -b $EXTENT_SIZE $OFFSET $EXTENT_SIZE" \`; `$XFS_IO_PROG -s -f -c "pwrite -S 0xff -b $EXTENT_SIZE 0 $EXTENT_SIZE" \`; `$CLONER_PROG -s $((2 * $BLOCK_SIZE)) -d 0 -l $((6 * $BLOCK_SIZE)) \`; plus 15 more source-matched operations for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_mkfs "$1" >/dev/null 2>&1`; `_scratch_mount`; `_check_scratch_fs`; `_scratch_unmount`. The core workload then performs these representative operations: `$XFS_IO_PROG -s -f -c "pwrite -S 0x01 -b $EXTENT_SIZE $OFFSET $EXTENT_SIZE" \`; `$XFS_IO_PROG -s -f -c "pwrite -S 0x02 -b $EXTENT_SIZE $OFFSET $EXTENT_SIZE" \`; `$XFS_IO_PROG -s -f -c "pwrite -S 0x04 -b $EXTENT_SIZE $OFFSET $EXTENT_SIZE" \`; `$XFS_IO_PROG -s -f -c "pwrite -S 0x05 -b $EXTENT_SIZE $OFFSET $EXTENT_SIZE" \`; `$XFS_IO_PROG -s -f -c "pwrite -S 0xff -b $EXTENT_SIZE 0 $EXTENT_SIZE" \`; `$CLONER_PROG -s $((2 * $BLOCK_SIZE)) -d 0 -l $((6 * $BLOCK_SIZE)) \`; `od -t x1 $SCRATCH_MNT/bar | _filter_od`; `$CLONER_PROG -s $((5 * $BLOCK_SIZE)) -d $((8 * $BLOCK_SIZE)) \`; `$CLONER_PROG -s 0 -d $((16 * $BLOCK_SIZE)) -l $((5 * $BLOCK_SIZE)) \`; `$XFS_IO_PROG -c "truncate $((16 * $BLOCK_SIZE))" $SCRATCH_MNT/foo \`; plus 11 more source-matched operations. It also uses background or repeated stress/control loops: `_scratch_mkfs "$1" >/dev/null 2>&1`.

## State and Persistence Behavior
Forces transaction or file-log persistence with sync/fsync. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on scratch filesystem lifecycle helpers, btrfs clone ioctl exerciser, xfs_io data-shaping commands. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
clone/reflink edge cases can corrupt inline extents, holes, compressed extents, page cache, or log replay metadata The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
hex dumps expose exact byte-level clone or hole behavior explicit filesystem check must pass Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/055 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/056 -->
# sources/test-tools/xfstests/tests/btrfs/056

## Purpose
Regression test for btrfs ioctl clone operation + fsync + log recovery. The issue was that doing an fsync after cloning into a file didn't gave any persistence guarantees as it should. What happened was that the in memory metadata (extent maps) weren't updated, which made the fsync code not able to detect that file data has been changed. The script is categorized by `_begin_fstest` as `auto`, `quick`, `clone`, `log`, `compress`, and its main coverage is: Btrfs extent cloning/reflink semantics, including inline extents, same-file clones, holes, compressed extents, page-cache coherency, and fsync/log replay persistence. Compressed extent behavior across read, restore, clone, send, defrag, remount, and property inheritance paths. Metadata consistency, orphan items, delayed references, extent maps, checksums, trim boundaries, and filesystem check behavior. Fsync log tree replay and power-failure simulation through dm-flakey to verify durable metadata and checksum recovery.

## Important APIs, Types, and Functions
local shell functions: `_cleanup`, `test_btrfs_clone_fsync_log_recover` fstest tags: `auto`, `quick`, `clone`, `log`, `compress` requirement gates: `_require_scratch`, `_require_cloner`, `_require_btrfs_fs_feature`, `_require_btrfs_mkfs_feature`, `_require_dm_target`. The important external command surfaces are `_btrfs`/`$BTRFS_UTIL_PROG` where present for Btrfs control and `$XFS_IO_PROG -s -f -c "pwrite -S 0x01 -b $EXTENT_SIZE 0 $EXTENT_SIZE" \`; `$XFS_IO_PROG -f -c "pwrite -S 0xff -b $((24 * $BLOCK_SIZE)) 0 $((24 * $BLOCK_SIZE))" \`; `$CLONER_PROG -s $((3 * $BLOCK_SIZE)) -d 0 -l $((6 * $BLOCK_SIZE)) \`; `$XFS_IO_PROG -c "fsync" $SCRATCH_MNT/bar`; `$XFS_IO_PROG -f -c "pwrite -S 0x00 -b $EXTENT_SIZE 0 $EXTENT_SIZE" -c "fsync" \`; `$XFS_IO_PROG -f -c "pwrite -S 0xcc -b $EXTENT_SIZE 0 $EXTENT_SIZE" -c "fsync" \`; plus 4 more source-matched operations for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_cleanup_flakey`; `_scratch_mkfs "$1" >/dev/null 2>&1`; `_init_flakey`; `_scratch_mount`; `_flakey_drop_and_remount yes`; `_scratch_unmount`; `_check_scratch_fs`; plus 1 more source-matched operations. The core workload then performs these representative operations: `$XFS_IO_PROG -s -f -c "pwrite -S 0x01 -b $EXTENT_SIZE 0 $EXTENT_SIZE" \`; `$XFS_IO_PROG -f -c "pwrite -S 0xff -b $((24 * $BLOCK_SIZE)) 0 $((24 * $BLOCK_SIZE))" \`; `$CLONER_PROG -s $((3 * $BLOCK_SIZE)) -d 0 -l $((6 * $BLOCK_SIZE)) \`; `$XFS_IO_PROG -c "fsync" $SCRATCH_MNT/bar`; `$XFS_IO_PROG -f -c "pwrite -S 0x00 -b $EXTENT_SIZE 0 $EXTENT_SIZE" -c "fsync" \`; `$XFS_IO_PROG -f -c "pwrite -S 0xcc -b $EXTENT_SIZE 0 $EXTENT_SIZE" -c "fsync" \`; `$CLONER_PROG -s 0 -d 0 -l $EXTENT_SIZE $SCRATCH_MNT/foo2 $SCRATCH_MNT/bar2`; `$XFS_IO_PROG -c "fsync" $SCRATCH_MNT/bar2`; `od -t x1 $SCRATCH_MNT/bar | _filter_od`; `od -t x1 $SCRATCH_MNT/bar2 | _filter_od`. It also uses background or repeated stress/control loops: `_scratch_mkfs "$1" >/dev/null 2>&1`.

## State and Persistence Behavior
Forces transaction or file-log persistence with sync/fsync; injects block-layer failure to model crash or eio behavior. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on scratch filesystem lifecycle helpers, btrfs clone ioctl exerciser, device-mapper target support, xfs_io data-shaping commands, dm-flakey crash simulation. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
clone/reflink edge cases can corrupt inline extents, holes, compressed extents, page cache, or log replay metadata compressed extents with non-zero offsets or shared references can return stale, zeroed, or mis-cloned data metadata replay, delayed references, orphan cleanup, extent-map merging, or raw-device reserved ranges can regress without obvious user-visible errors The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
hex dumps expose exact byte-level clone or hole behavior explicit filesystem check must pass Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/056 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/057 -->
# sources/test-tools/xfstests/tests/btrfs/057

## Purpose
Quota rescan stress test, we run fsstress and quota rescan concurrently The script is categorized by `_begin_fstest` as `auto`, `quick`, and its main coverage is: Quota group enablement, rescan, limits, accounting of shared/exclusive extents, and crash or deletion paths that can leave qgroup state inconsistent. Snapshot creation, readonly snapshot consistency, default subvolume behavior, and interactions between snapshot roots and live/orphaned metadata. Subvolume creation, mounting, deletion, set-default behavior, and placeholder directory semantics.

## Important APIs, Types, and Functions
fstest tags: `auto`, `quick` requirement gates: `_require_scratch`, `_require_qgroup_rescan`. The important external command surfaces are `_btrfs subvolume snapshot $SCRATCH_MNT \`; `_btrfs quota enable $SCRATCH_MNT`; `_btrfs quota rescan -w $SCRATCH_MNT` for Btrfs control and standard shell/file utilities for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_mkfs_sized $((1024 * 1024 * 1024)) >> $seqres.full 2>&1`; `_scratch_mount`. The core workload then performs these representative operations: `_btrfs subvolume snapshot $SCRATCH_MNT \`; `_btrfs quota enable $SCRATCH_MNT`; `_btrfs quota rescan -w $SCRATCH_MNT`. It also uses background or repeated stress/control loops: `_scratch_mkfs_sized $((1024 * 1024 * 1024)) >> $seqres.full 2>&1`; `_run_fsstress -d $SCRATCH_MNT -w -p 5 -n 1000`; `_run_fsstress -d $SCRATCH_MNT/snap1 -w -p 5 -n 1000`.

## State and Persistence Behavior
Creates snapshot roots and compares parent/child root state; mutates qgroup metadata and relies on final accounting checks. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on scratch filesystem lifecycle helpers, qgroup rescan support, btrfs-progs command wrappers. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
qgroup accounting can leak reservations or miscount shared/exclusive extents after snapshots, rescans, deletes, or limits The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
prints `Silence is golden` when no explicit failure path is reached fstests qgroup reporting/checking validates quota consistency Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/057 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/058 -->
# sources/test-tools/xfstests/tests/btrfs/058

## Purpose
Regression test for a btrfs issue where we create a RO snapshot to use for a send operation which fails with a -ESTALE error, due to the presence of orphan inodes accessible through the snapshot's commit root but no longer present through the main root. The script is categorized by `_begin_fstest` as `auto`, `quick`, `send`, `snapshot`, and its main coverage is: Btrfs send/receive stream generation, including full sends, incremental parent sends, clone-source roots, received UUID handling, and replay on a freshly formatted scratch filesystem. Snapshot creation, readonly snapshot consistency, default subvolume behavior, and interactions between snapshot roots and live/orphaned metadata. Subvolume creation, mounting, deletion, set-default behavior, and placeholder directory semantics.

## Important APIs, Types, and Functions
local shell functions: `_cleanup` fstest tags: `auto`, `quick`, `send`, `snapshot` requirement gates: `_require_scratch`, `_require_xfs_io_command`, `_require_mknod`, `_require_btrfs_command`. The important external command surfaces are `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/mysnap`; `$BTRFS_UTIL_PROG inspect-internal dump-tree -t $snap_id $SCRATCH_DEV | \`; `$BTRFS_UTIL_PROG inspect-internal dump-tree -t $snap_id $SCRATCH_DEV`; `_btrfs send -f /dev/null $SCRATCH_MNT/mysnap` for Btrfs control and `tail -f $SCRATCH_MNT/fifo | $XFS_IO_PROG >>$seqres.full &` for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_mkfs >/dev/null 2>&1`; `_scratch_mount`. The core workload then performs these representative operations: `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/mysnap`; `$BTRFS_UTIL_PROG inspect-internal dump-tree -t $snap_id $SCRATCH_DEV | \`; `$BTRFS_UTIL_PROG inspect-internal dump-tree -t $snap_id $SCRATCH_DEV`; `_btrfs send -f /dev/null $SCRATCH_MNT/mysnap`; `tail -f $SCRATCH_MNT/fifo | $XFS_IO_PROG >>$seqres.full &`. It also uses background or repeated stress/control loops: `kill $XFS_IO_PID > /dev/null 2>&1`; `wait`; `_scratch_mkfs >/dev/null 2>&1`; `tail -f $SCRATCH_MNT/fifo | $XFS_IO_PROG >>$seqres.full &`.

## State and Persistence Behavior
Creates snapshot roots and compares parent/child root state. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on scratch filesystem lifecycle helpers, xfs_io subcommand availability, specific btrfs-progs subcommand availability, btrfs-progs command wrappers, xfs_io data-shaping commands. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
send path ordering can emit invalid rename, rmdir, clone, or path records if inode identity, generation, or delayed-move state is mishandled The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
successful command completion and fstests cleanup checks are the primary signal Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/058 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/059 -->
# sources/test-tools/xfstests/tests/btrfs/059

## Purpose
Regression test for btrfs where removing the flag FS_COMPR_FL (chattr -c) from an inode wouldn't clear its compression property. This was fixed in the following linux kernel patch: The script is categorized by `_begin_fstest` as `auto`, `quick`, `compress`, and its main coverage is: Compressed extent behavior across read, restore, clone, send, defrag, remount, and property inheritance paths.

## Important APIs, Types, and Functions
local shell functions: `_cleanup` fstest tags: `auto`, `quick`, `compress` requirement gates: `_require_test`, `_require_scratch`, `_require_btrfs_command`, `_require_btrfs_no_nodatacow`, `_require_btrfs_no_nodatasum`. The important external command surfaces are `$BTRFS_UTIL_PROG property get $SCRATCH_MNT/testdir compression | \`; `$BTRFS_UTIL_PROG property get $SCRATCH_MNT/testdir/file1 compression | \`; `$BTRFS_UTIL_PROG property get $SCRATCH_MNT/testdir/file2 compression | \`; plus 2 more source-matched operations for Btrfs control and `$CHATTR_PROG +c $SCRATCH_MNT/testdir`; `$CHATTR_PROG -c $SCRATCH_MNT/testdir` for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_mkfs >> $seqres.full 2>&1`; `_scratch_mount`. The core workload then performs these representative operations: `$BTRFS_UTIL_PROG property get $SCRATCH_MNT/testdir compression | \`; `$BTRFS_UTIL_PROG property get $SCRATCH_MNT/testdir/file1 compression | \`; `$BTRFS_UTIL_PROG property get $SCRATCH_MNT/testdir/file2 compression | \`; `$CHATTR_PROG +c $SCRATCH_MNT/testdir`; `$CHATTR_PROG -c $SCRATCH_MNT/testdir`; plus 2 more source-matched operations. It also uses background or repeated stress/control loops: `_scratch_mkfs >> $seqres.full 2>&1`.

## State and Persistence Behavior
Mutates a freshly formatted scratch filesystem and relies on command status plus fstests cleanup checks. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on external test directory storage, scratch filesystem lifecycle helpers, specific btrfs-progs subcommand availability, btrfs-progs command wrappers, Btrfs-specific output filters. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
compressed extents with non-zero offsets or shared references can return stale, zeroed, or mis-cloned data The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
successful command completion and fstests cleanup checks are the primary signal Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/059 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/060 -->
# sources/test-tools/xfstests/tests/btrfs/060

## Purpose
Run btrfs balance and subvolume create/mount/umount/delete simultaneously, with fsstress running in background. The script is categorized by `_begin_fstest` as `auto`, `balance`, `subvol`, `scrub`, `raid`, and its main coverage is: Multi-device balance stress, including mutual exclusion with replace/delete operations and post-stress scrub/fsck validation. Scrub as both a concurrent stress operation and a final integrity signal after multi-device or metadata-heavy workloads. Subvolume creation, mounting, deletion, set-default behavior, and placeholder directory semantics.

## Important APIs, Types, and Functions
local shell functions: `_cleanup`, `run_test` fstest tags: `auto`, `balance`, `subvol`, `scrub`, `raid` requirement gates: `_require_scratch_nocheck`, `_require_scratch_dev_pool`. The important external command surfaces are `$BTRFS_UTIL_PROG scrub start -B $SCRATCH_MNT >>$seqres.full 2>&1` for Btrfs control and standard shell/file utilities for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_pool_mkfs $mkfs_opts >>$seqres.full 2>&1`; `_scratch_mount >>$seqres.full 2>&1`; `_scratch_unmount`; `_check_scratch_fs`. The core workload then performs these representative operations: `$BTRFS_UTIL_PROG scrub start -B $SCRATCH_MNT >>$seqres.full 2>&1`. It also uses background or repeated stress/control loops: `if [ ! -z "$stop_file" ] && [ ! -z "$subvol_pid" ] && \`; `_scratch_pool_mkfs $mkfs_opts >>$seqres.full 2>&1`; `_scratch_mount >>$seqres.full 2>&1`; `_run_fsstress_bg $args`; `_btrfs_stress_balance $SCRATCH_MNT >/dev/null 2>&1 &`; `_btrfs_stress_subvolume $SCRATCH_DEV $SCRATCH_MNT subvol_$$ $subvol_mnt $stop_file >/dev/null 2>&1 &`; plus 4 more source-matched operations.

## State and Persistence Behavior
Uses scrub as an integrity check after stress. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on scratch filesystem lifecycle without automatic final check, multi-device scratch pool, btrfs-progs command wrappers. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
multi-device operations can race with stress workers, mutually exclusive jobs, scrub, or injected device failure The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
prints `Silence is golden` when no explicit failure path is reached explicit filesystem check must pass final scrub must not report block errors Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/060 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/061 -->
# sources/test-tools/xfstests/tests/btrfs/061

## Purpose
Run btrfs balance and scrub operations simultaneously with fsstress running in background. The script is categorized by `_begin_fstest` as `auto`, `balance`, `scrub`, `raid`, and its main coverage is: Multi-device balance stress, including mutual exclusion with replace/delete operations and post-stress scrub/fsck validation. Scrub as both a concurrent stress operation and a final integrity signal after multi-device or metadata-heavy workloads.

## Important APIs, Types, and Functions
local shell functions: `_cleanup`, `run_test` fstest tags: `auto`, `balance`, `scrub`, `raid` requirement gates: `_require_scratch_nocheck`, `_require_scratch_dev_pool`. The important external command surfaces are `$BTRFS_UTIL_PROG scrub start -B $SCRATCH_MNT >>$seqres.full 2>&1` for Btrfs control and standard shell/file utilities for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_pool_mkfs $mkfs_opts >>$seqres.full 2>&1`; `_scratch_mount >>$seqres.full 2>&1`; `_scratch_unmount`; `_check_scratch_fs`. The core workload then performs these representative operations: `$BTRFS_UTIL_PROG scrub start -B $SCRATCH_MNT >>$seqres.full 2>&1`. It also uses background or repeated stress/control loops: `_scratch_pool_mkfs $mkfs_opts >>$seqres.full 2>&1`; `_scratch_mount >>$seqres.full 2>&1`; `_run_fsstress_bg $args`; `_btrfs_stress_balance $SCRATCH_MNT >/dev/null 2>&1 &`; `_btrfs_stress_scrub $SCRATCH_MNT >/dev/null 2>&1 &`; `echo "Wait for fsstress to exit and kill all background workers" >>$seqres.full`; plus 2 more source-matched operations.

## State and Persistence Behavior
Uses scrub as an integrity check after stress. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on scratch filesystem lifecycle without automatic final check, multi-device scratch pool, btrfs-progs command wrappers. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
multi-device operations can race with stress workers, mutually exclusive jobs, scrub, or injected device failure The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
prints `Silence is golden` when no explicit failure path is reached explicit filesystem check must pass final scrub must not report block errors Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/061 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/062 -->
# sources/test-tools/xfstests/tests/btrfs/062

## Purpose
Run btrfs balance and defrag operations simultaneously with fsstress running in background. The script is categorized by `_begin_fstest` as `auto`, `balance`, `defrag`, `compress`, `scrub`, `raid`, and its main coverage is: Multi-device balance stress, including mutual exclusion with replace/delete operations and post-stress scrub/fsck validation. Scrub as both a concurrent stress operation and a final integrity signal after multi-device or metadata-heavy workloads. Compressed extent behavior across read, restore, clone, send, defrag, remount, and property inheritance paths.

## Important APIs, Types, and Functions
local shell functions: `_cleanup`, `run_test` fstest tags: `auto`, `balance`, `defrag`, `compress`, `scrub`, `raid` requirement gates: `_require_scratch_nocheck`, `_require_scratch_dev_pool`. The important external command surfaces are `$BTRFS_UTIL_PROG scrub start -B $SCRATCH_MNT >>$seqres.full 2>&1` for Btrfs control and standard shell/file utilities for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_pool_mkfs $mkfs_opts >>$seqres.full 2>&1`; `_scratch_mount >>$seqres.full 2>&1`; `_scratch_unmount`; `_check_scratch_fs`. The core workload then performs these representative operations: `$BTRFS_UTIL_PROG scrub start -B $SCRATCH_MNT >>$seqres.full 2>&1`. It also uses background or repeated stress/control loops: `_scratch_pool_mkfs $mkfs_opts >>$seqres.full 2>&1`; `_scratch_mount >>$seqres.full 2>&1`; `_run_fsstress_bg $args`; `_btrfs_stress_balance $SCRATCH_MNT >/dev/null 2>&1 &`; `_btrfs_stress_defrag $SCRATCH_MNT $with_compress >/dev/null 2>&1 &`; `echo "Wait for fsstress to exit and kill all background workers" >>$seqres.full`; plus 2 more source-matched operations.

## State and Persistence Behavior
Uses scrub as an integrity check after stress. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on scratch filesystem lifecycle without automatic final check, multi-device scratch pool, btrfs-progs command wrappers. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
multi-device operations can race with stress workers, mutually exclusive jobs, scrub, or injected device failure compressed extents with non-zero offsets or shared references can return stale, zeroed, or mis-cloned data The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
prints `Silence is golden` when no explicit failure path is reached explicit filesystem check must pass final scrub must not report block errors Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/062 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/063 -->
# sources/test-tools/xfstests/tests/btrfs/063

## Purpose
Run btrfs balance and remount with different compress algorithms simultaneously, with fsstress running in background. The script is categorized by `_begin_fstest` as `auto`, `balance`, `remount`, `compress`, `scrub`, `raid`, and its main coverage is: Multi-device balance stress, including mutual exclusion with replace/delete operations and post-stress scrub/fsck validation. Scrub as both a concurrent stress operation and a final integrity signal after multi-device or metadata-heavy workloads. Compressed extent behavior across read, restore, clone, send, defrag, remount, and property inheritance paths. Mount option transitions, especially flushoncommit, thread_pool resizing, and compression remount changes.

## Important APIs, Types, and Functions
local shell functions: `_cleanup`, `run_test` fstest tags: `auto`, `balance`, `remount`, `compress`, `scrub`, `raid` requirement gates: `_require_scratch_nocheck`, `_require_scratch_dev_pool`. The important external command surfaces are `$BTRFS_UTIL_PROG scrub start -B $SCRATCH_MNT >>$seqres.full 2>&1` for Btrfs control and standard shell/file utilities for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_pool_mkfs $mkfs_opts >>$seqres.full 2>&1`; `_scratch_mount >>$seqres.full 2>&1`; `_scratch_unmount`; `_check_scratch_fs`. The core workload then performs these representative operations: `$BTRFS_UTIL_PROG scrub start -B $SCRATCH_MNT >>$seqres.full 2>&1`. It also uses background or repeated stress/control loops: `_scratch_pool_mkfs $mkfs_opts >>$seqres.full 2>&1`; `_scratch_mount >>$seqres.full 2>&1`; `_run_fsstress_bg $args`; `_btrfs_stress_balance $SCRATCH_MNT >/dev/null 2>&1 &`; `_btrfs_stress_remount_compress $SCRATCH_MNT >/dev/null 2>&1 &`; `echo "Wait for fsstress to exit and kill all background workers" >>$seqres.full`; plus 2 more source-matched operations.

## State and Persistence Behavior
Uses scrub as an integrity check after stress. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on scratch filesystem lifecycle without automatic final check, multi-device scratch pool, btrfs-progs command wrappers. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
multi-device operations can race with stress workers, mutually exclusive jobs, scrub, or injected device failure compressed extents with non-zero offsets or shared references can return stale, zeroed, or mis-cloned data The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
prints `Silence is golden` when no explicit failure path is reached explicit filesystem check must pass final scrub must not report block errors Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/063 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/064 -->
# sources/test-tools/xfstests/tests/btrfs/064

## Purpose
Run btrfs balance and replace operations simultaneously with fsstress running in the background, check with the scrub if all the blocks are ok. Balance and replace operations are mutually exclusive operations they can't run simultaneously. One of them is expected to fail when the other is running. The script is categorized by `_begin_fstest` as `auto`, `balance`, `replace`, `volume`, `scrub`, `raid`, and its main coverage is: Multi-device balance stress, including mutual exclusion with replace/delete operations and post-stress scrub/fsck validation. Device replacement or deletion against RAID-style scratch device pools, including device-mapper error injection and filesystem show verification. Scrub as both a concurrent stress operation and a final integrity signal after multi-device or metadata-heavy workloads.

## Important APIs, Types, and Functions
local shell functions: `_cleanup`, `run_test` fstest tags: `auto`, `balance`, `replace`, `volume`, `scrub`, `raid` requirement gates: `_require_scratch_nocheck`, `_require_scratch_dev_pool`, `_require_scratch_dev_pool_equal_size`. The important external command surfaces are `$BTRFS_UTIL_PROG scrub start -B $SCRATCH_MNT >>$seqres.full 2>&1` for Btrfs control and standard shell/file utilities for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_pool_mkfs $mkfs_opts >>$seqres.full 2>&1`; `_scratch_mount >>$seqres.full 2>&1`; `_scratch_unmount`; `_check_scratch_fs`. The core workload then performs these representative operations: `$BTRFS_UTIL_PROG scrub start -B $SCRATCH_MNT >>$seqres.full 2>&1`. It also uses background or repeated stress/control loops: `_scratch_pool_mkfs $mkfs_opts >>$seqres.full 2>&1`; `_scratch_mount >>$seqres.full 2>&1`; `_run_fsstress_bg $args`; `_btrfs_stress_balance $SCRATCH_MNT >/dev/null 2>&1 &`; `_btrfs_stress_replace $SCRATCH_MNT >>$seqres.full 2>&1 &`; `echo "Wait for fsstress to exit and kill all background workers" >>$seqres.full`; plus 2 more source-matched operations.

## State and Persistence Behavior
Uses scrub as an integrity check after stress. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on scratch filesystem lifecycle without automatic final check, multi-device scratch pool, btrfs-progs command wrappers. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
multi-device operations can race with stress workers, mutually exclusive jobs, scrub, or injected device failure The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
prints `Silence is golden` when no explicit failure path is reached explicit filesystem check must pass final scrub must not report block errors Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/064 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/065 -->
# sources/test-tools/xfstests/tests/btrfs/065

## Purpose
Run btrfs subvolume create/mount/umount/delete and device replace operation simultaneously, with fsstress running in background. The script is categorized by `_begin_fstest` as `auto`, `subvol`, `replace`, `volume`, `scrub`, `raid`, and its main coverage is: Device replacement or deletion against RAID-style scratch device pools, including device-mapper error injection and filesystem show verification. Scrub as both a concurrent stress operation and a final integrity signal after multi-device or metadata-heavy workloads. Subvolume creation, mounting, deletion, set-default behavior, and placeholder directory semantics.

## Important APIs, Types, and Functions
local shell functions: `_cleanup`, `run_test` fstest tags: `auto`, `subvol`, `replace`, `volume`, `scrub`, `raid` requirement gates: `_require_scratch_nocheck`, `_require_scratch_dev_pool`, `_require_scratch_dev_pool_equal_size`. The important external command surfaces are `$BTRFS_UTIL_PROG scrub start -B $SCRATCH_MNT >>$seqres.full 2>&1` for Btrfs control and standard shell/file utilities for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_pool_mkfs $mkfs_opts >>$seqres.full 2>&1`; `_scratch_mount >>$seqres.full 2>&1`; `_scratch_unmount`; `_check_scratch_fs`. The core workload then performs these representative operations: `$BTRFS_UTIL_PROG scrub start -B $SCRATCH_MNT >>$seqres.full 2>&1`. It also uses background or repeated stress/control loops: `if [ ! -z "$stop_file" ] && [ ! -z "$subvol_pid" ] && \`; `_scratch_pool_mkfs $mkfs_opts >>$seqres.full 2>&1`; `_scratch_mount >>$seqres.full 2>&1`; `_run_fsstress_bg $args`; `_btrfs_stress_subvolume $SCRATCH_DEV $SCRATCH_MNT subvol_$$ $subvol_mnt $stop_file >/dev/null 2>&1 &`; `_btrfs_stress_replace $SCRATCH_MNT >>$seqres.full 2>&1 &`; plus 4 more source-matched operations.

## State and Persistence Behavior
Uses scrub as an integrity check after stress. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on scratch filesystem lifecycle without automatic final check, multi-device scratch pool, btrfs-progs command wrappers. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
multi-device operations can race with stress workers, mutually exclusive jobs, scrub, or injected device failure The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
prints `Silence is golden` when no explicit failure path is reached explicit filesystem check must pass final scrub must not report block errors Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/065 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/066 -->
# sources/test-tools/xfstests/tests/btrfs/066

## Purpose
Run btrfs subvolume create/mount/umount/delete and btrfs scrub operation simultaneously, with fsstress running in background. The script is categorized by `_begin_fstest` as `auto`, `subvol`, `scrub`, `raid`, and its main coverage is: Scrub as both a concurrent stress operation and a final integrity signal after multi-device or metadata-heavy workloads. Subvolume creation, mounting, deletion, set-default behavior, and placeholder directory semantics.

## Important APIs, Types, and Functions
local shell functions: `_cleanup`, `run_test` fstest tags: `auto`, `subvol`, `scrub`, `raid` requirement gates: `_require_scratch_nocheck`, `_require_scratch_dev_pool`. The important external command surfaces are `$BTRFS_UTIL_PROG scrub start -B $SCRATCH_MNT >>$seqres.full 2>&1` for Btrfs control and standard shell/file utilities for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_pool_mkfs $mkfs_opts >>$seqres.full 2>&1`; `_scratch_mount >>$seqres.full 2>&1`; `_scratch_unmount`; `_check_scratch_fs`. The core workload then performs these representative operations: `$BTRFS_UTIL_PROG scrub start -B $SCRATCH_MNT >>$seqres.full 2>&1`. It also uses background or repeated stress/control loops: `if [ ! -z "$stop_file" ] && [ ! -z "$subvol_pid" ] && \`; `_scratch_pool_mkfs $mkfs_opts >>$seqres.full 2>&1`; `_scratch_mount >>$seqres.full 2>&1`; `_run_fsstress_bg $args`; `_btrfs_stress_subvolume $SCRATCH_DEV $SCRATCH_MNT subvol_$$ $subvol_mnt $stop_file >/dev/null 2>&1 &`; `_btrfs_stress_scrub $SCRATCH_MNT >/dev/null 2>&1 &`; plus 4 more source-matched operations.

## State and Persistence Behavior
Uses scrub as an integrity check after stress. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on scratch filesystem lifecycle without automatic final check, multi-device scratch pool, btrfs-progs command wrappers. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
the test is sensitive to kernel, btrfs-progs, and fstests helper behavior because it verifies a narrow historical regression The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
prints `Silence is golden` when no explicit failure path is reached explicit filesystem check must pass final scrub must not report block errors Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/066 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/067 -->
# sources/test-tools/xfstests/tests/btrfs/067

## Purpose
Run btrfs subvolume create/mount/umount/delete and btrfs defrag operation simultaneously, with fsstress running in background. The script is categorized by `_begin_fstest` as `auto`, `subvol`, `defrag`, `compress`, `scrub`, `raid`, and its main coverage is: Scrub as both a concurrent stress operation and a final integrity signal after multi-device or metadata-heavy workloads. Compressed extent behavior across read, restore, clone, send, defrag, remount, and property inheritance paths. Subvolume creation, mounting, deletion, set-default behavior, and placeholder directory semantics.

## Important APIs, Types, and Functions
local shell functions: `_cleanup`, `run_test` fstest tags: `auto`, `subvol`, `defrag`, `compress`, `scrub`, `raid` requirement gates: `_require_scratch_nocheck`, `_require_scratch_dev_pool`. The important external command surfaces are `$BTRFS_UTIL_PROG scrub start -B $SCRATCH_MNT >>$seqres.full 2>&1` for Btrfs control and standard shell/file utilities for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_pool_mkfs $mkfs_opts >>$seqres.full 2>&1`; `_scratch_mount >>$seqres.full 2>&1`; `_scratch_unmount`; `_check_scratch_fs`. The core workload then performs these representative operations: `$BTRFS_UTIL_PROG scrub start -B $SCRATCH_MNT >>$seqres.full 2>&1`. It also uses background or repeated stress/control loops: `if [ ! -z "$stop_file" ] && [ ! -z "$subvol_pid" ] && \`; `_scratch_pool_mkfs $mkfs_opts >>$seqres.full 2>&1`; `_scratch_mount >>$seqres.full 2>&1`; `_run_fsstress_bg $args`; `_btrfs_stress_subvolume $SCRATCH_DEV $SCRATCH_MNT subvol_$$ $subvol_mnt $stop_file >/dev/null 2>&1 &`; `_btrfs_stress_defrag $SCRATCH_MNT $with_compress >/dev/null 2>&1 &`; plus 4 more source-matched operations.

## State and Persistence Behavior
Uses scrub as an integrity check after stress. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on scratch filesystem lifecycle without automatic final check, multi-device scratch pool, btrfs-progs command wrappers. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
compressed extents with non-zero offsets or shared references can return stale, zeroed, or mis-cloned data The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
prints `Silence is golden` when no explicit failure path is reached explicit filesystem check must pass final scrub must not report block errors Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/067 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/068 -->
# sources/test-tools/xfstests/tests/btrfs/068

## Purpose
Run btrfs subvolume create/mount/umount/delete and remount with different compress algorithms simultaneously, with fsstress running in background. The script is categorized by `_begin_fstest` as `auto`, `subvol`, `remount`, `compress`, `scrub`, `raid`, and its main coverage is: Scrub as both a concurrent stress operation and a final integrity signal after multi-device or metadata-heavy workloads. Compressed extent behavior across read, restore, clone, send, defrag, remount, and property inheritance paths. Subvolume creation, mounting, deletion, set-default behavior, and placeholder directory semantics. Mount option transitions, especially flushoncommit, thread_pool resizing, and compression remount changes.

## Important APIs, Types, and Functions
local shell functions: `_cleanup`, `run_test` fstest tags: `auto`, `subvol`, `remount`, `compress`, `scrub`, `raid` requirement gates: `_require_scratch_nocheck`, `_require_scratch_dev_pool`. The important external command surfaces are `$BTRFS_UTIL_PROG scrub start -B $SCRATCH_MNT >>$seqres.full 2>&1` for Btrfs control and standard shell/file utilities for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_pool_mkfs $mkfs_opts >>$seqres.full 2>&1`; `_scratch_mount >>$seqres.full 2>&1`; `_scratch_unmount`; `_check_scratch_fs`. The core workload then performs these representative operations: `$BTRFS_UTIL_PROG scrub start -B $SCRATCH_MNT >>$seqres.full 2>&1`. It also uses background or repeated stress/control loops: `if [ ! -z "$stop_file" ] && [ ! -z "$subvol_pid" ] && \`; `_scratch_pool_mkfs $mkfs_opts >>$seqres.full 2>&1`; `_scratch_mount >>$seqres.full 2>&1`; `_run_fsstress_bg $args`; `_btrfs_stress_subvolume $SCRATCH_DEV $SCRATCH_MNT subvol_$$ $subvol_mnt $stop_file >/dev/null 2>&1 &`; `_btrfs_stress_remount_compress $SCRATCH_MNT >/dev/null 2>&1 &`; plus 4 more source-matched operations.

## State and Persistence Behavior
Uses scrub as an integrity check after stress. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on scratch filesystem lifecycle without automatic final check, multi-device scratch pool, btrfs-progs command wrappers. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
compressed extents with non-zero offsets or shared references can return stale, zeroed, or mis-cloned data The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
prints `Silence is golden` when no explicit failure path is reached explicit filesystem check must pass final scrub must not report block errors Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/068 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/069 -->
# sources/test-tools/xfstests/tests/btrfs/069

## Purpose
Run btrfs replace operations and scrub simultaneously with fsstress running in background. The script is categorized by `_begin_fstest` as `auto`, `replace`, `scrub`, `volume`, `raid`, and its main coverage is: Device replacement or deletion against RAID-style scratch device pools, including device-mapper error injection and filesystem show verification. Scrub as both a concurrent stress operation and a final integrity signal after multi-device or metadata-heavy workloads.

## Important APIs, Types, and Functions
local shell functions: `_cleanup`, `run_test` fstest tags: `auto`, `replace`, `scrub`, `volume`, `raid` requirement gates: `_require_scratch_nocheck`, `_require_scratch_dev_pool`, `_require_scratch_dev_pool_equal_size`. The important external command surfaces are `$BTRFS_UTIL_PROG scrub start -B $SCRATCH_MNT >>$seqres.full 2>&1` for Btrfs control and standard shell/file utilities for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_pool_mkfs $mkfs_opts >>$seqres.full 2>&1`; `_scratch_mount >>$seqres.full 2>&1`; `_scratch_unmount`; `_check_scratch_fs`. The core workload then performs these representative operations: `$BTRFS_UTIL_PROG scrub start -B $SCRATCH_MNT >>$seqres.full 2>&1`. It also uses background or repeated stress/control loops: `_scratch_pool_mkfs $mkfs_opts >>$seqres.full 2>&1`; `_scratch_mount >>$seqres.full 2>&1`; `_run_fsstress_bg $args`; `_btrfs_stress_replace $SCRATCH_MNT >>$seqres.full 2>&1 &`; `_btrfs_stress_scrub $SCRATCH_MNT >/dev/null 2>&1 &`; `echo "Wait for fsstress to exit and kill all background workers" >>$seqres.full`; plus 2 more source-matched operations.

## State and Persistence Behavior
Uses scrub as an integrity check after stress. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on scratch filesystem lifecycle without automatic final check, multi-device scratch pool, btrfs-progs command wrappers. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
multi-device operations can race with stress workers, mutually exclusive jobs, scrub, or injected device failure The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
prints `Silence is golden` when no explicit failure path is reached explicit filesystem check must pass final scrub must not report block errors Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/069 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/070 -->
# sources/test-tools/xfstests/tests/btrfs/070

## Purpose
Run btrfs replace operations and defrag simultaneously with fsstress running in background. The script is categorized by `_begin_fstest` as `auto`, `replace`, `defrag`, `compress`, `volume`, `scrub`, `raid`, and its main coverage is: Device replacement or deletion against RAID-style scratch device pools, including device-mapper error injection and filesystem show verification. Scrub as both a concurrent stress operation and a final integrity signal after multi-device or metadata-heavy workloads. Compressed extent behavior across read, restore, clone, send, defrag, remount, and property inheritance paths.

## Important APIs, Types, and Functions
local shell functions: `_cleanup`, `run_test` fstest tags: `auto`, `replace`, `defrag`, `compress`, `volume`, `scrub`, `raid` requirement gates: `_require_scratch_nocheck`, `_require_scratch_dev_pool`, `_require_scratch_dev_pool_equal_size`. The important external command surfaces are `$BTRFS_UTIL_PROG scrub start -B $SCRATCH_MNT >>$seqres.full 2>&1` for Btrfs control and standard shell/file utilities for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_pool_mkfs $mkfs_opts >>$seqres.full 2>&1`; `_scratch_mount >>$seqres.full 2>&1`; `_scratch_unmount`; `_check_scratch_fs`. The core workload then performs these representative operations: `$BTRFS_UTIL_PROG scrub start -B $SCRATCH_MNT >>$seqres.full 2>&1`. It also uses background or repeated stress/control loops: `_scratch_pool_mkfs $mkfs_opts >>$seqres.full 2>&1`; `_scratch_mount >>$seqres.full 2>&1`; `_run_fsstress_bg $args`; `_btrfs_stress_replace $SCRATCH_MNT >>$seqres.full 2>&1 &`; `_btrfs_stress_defrag $SCRATCH_MNT $with_compress >/dev/null 2>&1 &`; `echo "Wait for fsstress to exit and kill all background workers" >>$seqres.full`; plus 2 more source-matched operations.

## State and Persistence Behavior
Uses scrub as an integrity check after stress. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on scratch filesystem lifecycle without automatic final check, multi-device scratch pool, btrfs-progs command wrappers. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
multi-device operations can race with stress workers, mutually exclusive jobs, scrub, or injected device failure compressed extents with non-zero offsets or shared references can return stale, zeroed, or mis-cloned data The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
prints `Silence is golden` when no explicit failure path is reached explicit filesystem check must pass final scrub must not report block errors Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/070 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/071 -->
# sources/test-tools/xfstests/tests/btrfs/071

## Purpose
Run btrfs replace operations and remount with different compress algorithms simultaneously with fsstress running in background. The script is categorized by `_begin_fstest` as `auto`, `replace`, `remount`, `compress`, `volume`, `scrub`, `raid`, and its main coverage is: Device replacement or deletion against RAID-style scratch device pools, including device-mapper error injection and filesystem show verification. Scrub as both a concurrent stress operation and a final integrity signal after multi-device or metadata-heavy workloads. Compressed extent behavior across read, restore, clone, send, defrag, remount, and property inheritance paths. Mount option transitions, especially flushoncommit, thread_pool resizing, and compression remount changes.

## Important APIs, Types, and Functions
local shell functions: `_cleanup`, `run_test` fstest tags: `auto`, `replace`, `remount`, `compress`, `volume`, `scrub`, `raid` requirement gates: `_require_scratch_nocheck`, `_require_scratch_dev_pool`, `_require_scratch_dev_pool_equal_size`. The important external command surfaces are `$BTRFS_UTIL_PROG scrub start -B $SCRATCH_MNT >>$seqres.full 2>&1` for Btrfs control and standard shell/file utilities for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_pool_mkfs $mkfs_opts >>$seqres.full 2>&1`; `_scratch_mount >>$seqres.full 2>&1`; `_scratch_unmount`; `_check_scratch_fs`. The core workload then performs these representative operations: `$BTRFS_UTIL_PROG scrub start -B $SCRATCH_MNT >>$seqres.full 2>&1`. It also uses background or repeated stress/control loops: `_scratch_pool_mkfs $mkfs_opts >>$seqres.full 2>&1`; `_scratch_mount >>$seqres.full 2>&1`; `_run_fsstress_bg $args`; `_btrfs_stress_replace $SCRATCH_MNT >>$seqres.full 2>&1 &`; `_btrfs_stress_remount_compress $SCRATCH_MNT >/dev/null 2>&1 &`; `echo "Wait for fsstress to exit and kill all background workers" >>$seqres.full`; plus 2 more source-matched operations.

## State and Persistence Behavior
Uses scrub as an integrity check after stress. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on scratch filesystem lifecycle without automatic final check, multi-device scratch pool, btrfs-progs command wrappers. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
multi-device operations can race with stress workers, mutually exclusive jobs, scrub, or injected device failure compressed extents with non-zero offsets or shared references can return stale, zeroed, or mis-cloned data The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
prints `Silence is golden` when no explicit failure path is reached explicit filesystem check must pass final scrub must not report block errors Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/071 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/072 -->
# sources/test-tools/xfstests/tests/btrfs/072

## Purpose
Run btrfs scrub and defrag operations simultaneously with fsstress running in background. The script is categorized by `_begin_fstest` as `auto`, `scrub`, `defrag`, `compress`, `raid`, and its main coverage is: Scrub as both a concurrent stress operation and a final integrity signal after multi-device or metadata-heavy workloads. Compressed extent behavior across read, restore, clone, send, defrag, remount, and property inheritance paths.

## Important APIs, Types, and Functions
local shell functions: `_cleanup`, `run_test` fstest tags: `auto`, `scrub`, `defrag`, `compress`, `raid` requirement gates: `_require_scratch_nocheck`, `_require_scratch_dev_pool`. The important external command surfaces are `$BTRFS_UTIL_PROG scrub start -B $SCRATCH_MNT >>$seqres.full 2>&1` for Btrfs control and standard shell/file utilities for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_pool_mkfs $mkfs_opts >>$seqres.full 2>&1`; `_scratch_mount >>$seqres.full 2>&1`; `_scratch_unmount`; `_check_scratch_fs`. The core workload then performs these representative operations: `$BTRFS_UTIL_PROG scrub start -B $SCRATCH_MNT >>$seqres.full 2>&1`. It also uses background or repeated stress/control loops: `_scratch_pool_mkfs $mkfs_opts >>$seqres.full 2>&1`; `_scratch_mount >>$seqres.full 2>&1`; `_run_fsstress_bg $args`; `_btrfs_stress_scrub $SCRATCH_MNT >/dev/null 2>&1 &`; `_btrfs_stress_defrag $SCRATCH_MNT $with_compress >/dev/null 2>&1 &`; `echo "Wait for fsstress to exit and kill all background workers" >>$seqres.full`; plus 2 more source-matched operations.

## State and Persistence Behavior
Uses scrub as an integrity check after stress. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on scratch filesystem lifecycle without automatic final check, multi-device scratch pool, btrfs-progs command wrappers. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
compressed extents with non-zero offsets or shared references can return stale, zeroed, or mis-cloned data The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
prints `Silence is golden` when no explicit failure path is reached explicit filesystem check must pass final scrub must not report block errors Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/072 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/073 -->
# sources/test-tools/xfstests/tests/btrfs/073

## Purpose
Run btrfs scrub and remount with different compress algorithms simultaneously with fsstress running in background. The script is categorized by `_begin_fstest` as `auto`, `scrub`, `remount`, `compress`, `raid`, and its main coverage is: Scrub as both a concurrent stress operation and a final integrity signal after multi-device or metadata-heavy workloads. Compressed extent behavior across read, restore, clone, send, defrag, remount, and property inheritance paths. Mount option transitions, especially flushoncommit, thread_pool resizing, and compression remount changes.

## Important APIs, Types, and Functions
local shell functions: `_cleanup`, `run_test` fstest tags: `auto`, `scrub`, `remount`, `compress`, `raid` requirement gates: `_require_scratch_nocheck`, `_require_scratch_dev_pool`. The important external command surfaces are `$BTRFS_UTIL_PROG scrub start -B $SCRATCH_MNT >>$seqres.full 2>&1` for Btrfs control and standard shell/file utilities for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_pool_mkfs $mkfs_opts >>$seqres.full 2>&1`; `_scratch_mount >>$seqres.full 2>&1`; `_scratch_unmount`; `_check_scratch_fs`. The core workload then performs these representative operations: `$BTRFS_UTIL_PROG scrub start -B $SCRATCH_MNT >>$seqres.full 2>&1`. It also uses background or repeated stress/control loops: `_scratch_pool_mkfs $mkfs_opts >>$seqres.full 2>&1`; `_scratch_mount >>$seqres.full 2>&1`; `_run_fsstress_bg $args`; `_btrfs_stress_scrub $SCRATCH_MNT >/dev/null 2>&1 &`; `_btrfs_stress_remount_compress $SCRATCH_MNT >/dev/null 2>&1 &`; `echo "Wait for fsstress to exit and kill all background workers" >>$seqres.full`; plus 2 more source-matched operations.

## State and Persistence Behavior
Uses scrub as an integrity check after stress. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on scratch filesystem lifecycle without automatic final check, multi-device scratch pool, btrfs-progs command wrappers. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
compressed extents with non-zero offsets or shared references can return stale, zeroed, or mis-cloned data The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
prints `Silence is golden` when no explicit failure path is reached explicit filesystem check must pass final scrub must not report block errors Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/073 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/074 -->
# sources/test-tools/xfstests/tests/btrfs/074

## Purpose
Run btrfs defrag operations and remount with different compress algorithms simultaneously with fsstress running in background. The script is categorized by `_begin_fstest` as `auto`, `defrag`, `remount`, `compress`, `scrub`, `raid`, and its main coverage is: Scrub as both a concurrent stress operation and a final integrity signal after multi-device or metadata-heavy workloads. Compressed extent behavior across read, restore, clone, send, defrag, remount, and property inheritance paths. Mount option transitions, especially flushoncommit, thread_pool resizing, and compression remount changes.

## Important APIs, Types, and Functions
local shell functions: `_cleanup`, `run_test` fstest tags: `auto`, `defrag`, `remount`, `compress`, `scrub`, `raid` requirement gates: `_require_scratch_nocheck`, `_require_scratch_dev_pool`. The important external command surfaces are `$BTRFS_UTIL_PROG scrub start -B $SCRATCH_MNT >>$seqres.full 2>&1` for Btrfs control and standard shell/file utilities for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_pool_mkfs $mkfs_opts >>$seqres.full 2>&1`; `_scratch_mount >>$seqres.full 2>&1`; `_scratch_unmount`; `_check_scratch_fs`. The core workload then performs these representative operations: `$BTRFS_UTIL_PROG scrub start -B $SCRATCH_MNT >>$seqres.full 2>&1`. It also uses background or repeated stress/control loops: `_scratch_pool_mkfs $mkfs_opts >>$seqres.full 2>&1`; `_scratch_mount >>$seqres.full 2>&1`; `_run_fsstress_bg $args`; `_btrfs_stress_defrag $SCRATCH_MNT $with_compress >/dev/null 2>&1 &`; `_btrfs_stress_remount_compress $SCRATCH_MNT >/dev/null 2>&1 &`; `echo "Wait for fsstress to exit and kill all background workers" >>$seqres.full`; plus 2 more source-matched operations.

## State and Persistence Behavior
Uses scrub as an integrity check after stress. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on scratch filesystem lifecycle without automatic final check, multi-device scratch pool, btrfs-progs command wrappers. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
compressed extents with non-zero offsets or shared references can return stale, zeroed, or mis-cloned data The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
prints `Silence is golden` when no explicit failure path is reached explicit filesystem check must pass final scrub must not report block errors Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/074 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/075 -->
# sources/test-tools/xfstests/tests/btrfs/075

## Purpose
If one subvolume was mounted with selinux context, other subvolumes should be able to be mounted with the same selinux context too. The script is categorized by `_begin_fstest` as `auto`, `quick`, `subvol`, and its main coverage is: Subvolume creation, mounting, deletion, set-default behavior, and placeholder directory semantics.

## Important APIs, Types, and Functions
local shell functions: `_cleanup` fstest tags: `auto`, `quick`, `subvol` requirement gates: `_require_scratch`. The important external command surfaces are `$BTRFS_UTIL_PROG subvolume create $SCRATCH_MNT/subvol >>$seqres.full 2>&1` for Btrfs control and standard shell/file utilities for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_mkfs >$seqres.full 2>&1`; `_scratch_mount`. The core workload then performs these representative operations: `$BTRFS_UTIL_PROG subvolume create $SCRATCH_MNT/subvol >>$seqres.full 2>&1`. It also uses background or repeated stress/control loops: `$UMOUNT_PROG $subvol_mnt >/dev/null 2>&1`; `_scratch_mkfs >$seqres.full 2>&1`; `$BTRFS_UTIL_PROG subvolume create $SCRATCH_MNT/subvol >>$seqres.full 2>&1`.

## State and Persistence Behavior
Mutates a freshly formatted scratch filesystem and relies on command status plus fstests cleanup checks. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on scratch filesystem lifecycle helpers, btrfs-progs command wrappers. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
the test is sensitive to kernel, btrfs-progs, and fstests helper behavior because it verifies a narrow historical regression The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
prints `Silence is golden` when no explicit failure path is reached Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/075 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/076 -->
# sources/test-tools/xfstests/tests/btrfs/076

## Purpose
Regression test for btrfs incorrect inode ratio detection. The script is categorized by `_begin_fstest` as `auto`, `quick`, `compress`, and its main coverage is: Compressed extent behavior across read, restore, clone, send, defrag, remount, and property inheritance paths.

## Important APIs, Types, and Functions
local shell functions: `_cleanup` fstest tags: `auto`, `quick`, `compress` requirement gates: `_require_test`, `_require_scratch`. The important external command surfaces are `_btrfs`/`$BTRFS_UTIL_PROG` where present for Btrfs control and `$XFS_IO_PROG -f -c "pwrite 0 10M" -c "fsync" \`; `$XFS_IO_PROG -f -c "pwrite 0 $((4096*33))" -c "fsync" \`; plus 1 more source-matched operations for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_mkfs >> $seqres.full 2>&1`; `_scratch_mount "-o compress=lzo"`. The core workload then performs these representative operations: `$XFS_IO_PROG -f -c "pwrite 0 10M" -c "fsync" \`; `$XFS_IO_PROG -f -c "pwrite 0 $((4096*33))" -c "fsync" \`; plus 1 more source-matched operations. It also uses background or repeated stress/control loops: `if [[ $zone_append_max -gt 0 && $zone_append_max -lt $max_extent_size ]]; then`; `_scratch_mkfs >> $seqres.full 2>&1`; `$SCRATCH_MNT/data >> $seqres.full 2>&1`; plus 2 more source-matched operations.

## State and Persistence Behavior
Forces transaction or file-log persistence with sync/fsync. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on external test directory storage, scratch filesystem lifecycle helpers, xfs_io data-shaping commands. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
compressed extents with non-zero offsets or shared references can return stale, zeroed, or mis-cloned data The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
prints `Silence is golden` when no explicit failure path is reached Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/076 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/077 -->
# sources/test-tools/xfstests/tests/btrfs/077

## Purpose
Regression test for a btrfs incremental send issue. If between two snapshots we rename an existing directory named X to Y and make it a child (direct or not) of a new inode named X, we were delaying the move/rename of the former directory unnecessarily, which would result in attempting to rename the new directory from its orphan name to name X prematurely. This made btrfs receive fail with an error message like the following: rename o261-7-0 -> merlin/RC/OSD failed This issue was a regression in the 3.16 kernel and got fixed by the following linux kernel btrfs patch: The script is categorized by `_begin_fstest` as `auto`, `quick`, `send`, `snapshot`, and its main coverage is: Btrfs send/receive stream generation, including full sends, incremental parent sends, clone-source roots, received UUID handling, and replay on a freshly formatted scratch filesystem. Snapshot creation, readonly snapshot consistency, default subvolume behavior, and interactions between snapshot roots and live/orphaned metadata.

## Important APIs, Types, and Functions
local shell functions: `_cleanup` fstest tags: `auto`, `quick`, `send`, `snapshot` requirement gates: `_require_scratch`, `_require_fssum`. The important external command surfaces are `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/mysnap1`; `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/mysnap2`; `_btrfs send -f $send_files_dir/1.snap $SCRATCH_MNT/mysnap1`; `_btrfs send -p $SCRATCH_MNT/mysnap1 -f $send_files_dir/2.snap \`; `_btrfs receive -f $send_files_dir/1.snap $SCRATCH_MNT`; `_btrfs receive -f $send_files_dir/2.snap $SCRATCH_MNT` for Btrfs control and standard shell/file utilities for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_mkfs >>$seqres.full 2>&1`; `_scratch_mount`; `_check_scratch_fs`; `_scratch_unmount`; plus 2 more source-matched operations. The core workload then performs these representative operations: `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/mysnap1`; `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/mysnap2`; `_btrfs send -f $send_files_dir/1.snap $SCRATCH_MNT/mysnap1`; `_btrfs send -p $SCRATCH_MNT/mysnap1 -f $send_files_dir/2.snap \`; `_btrfs receive -f $send_files_dir/1.snap $SCRATCH_MNT`; `_btrfs receive -f $send_files_dir/2.snap $SCRATCH_MNT`. It also uses background or repeated stress/control loops: `_scratch_mkfs >>$seqres.full 2>&1`; plus 1 more source-matched operations.

## State and Persistence Behavior
Creates snapshot roots and compares parent/child root state; persists send streams to temporary files and replays them on a reformatted scratch filesystem; records fssum manifests and validates received trees against them. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on scratch filesystem lifecycle helpers, fssum content manifests for send/receive equivalence, btrfs-progs command wrappers. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
send path ordering can emit invalid rename, rmdir, clone, or path records if inode identity, generation, or delayed-move state is mishandled The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
prints `Silence is golden` when no explicit failure path is reached fssum replay must match original snapshot manifests explicit filesystem check must pass Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/077 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/078 -->
# sources/test-tools/xfstests/tests/btrfs/078

## Purpose
Regression test for a btrfs issue where creation of readonly snapshots caused the filesystem to get into an inconsistent state. following linux kernel commit: 9c3b306e1c9e6be4be09e99a8fe2227d1005effc The script is categorized by `_begin_fstest` as `auto`, `snapshot`, and its main coverage is: Snapshot creation, readonly snapshot consistency, default subvolume behavior, and interactions between snapshot roots and live/orphaned metadata. Subvolume creation, mounting, deletion, set-default behavior, and placeholder directory semantics.

## Important APIs, Types, and Functions
local shell functions: `workout` fstest tags: `auto`, `snapshot` requirement gates: `_require_scratch`. The important external command surfaces are `snapshot_cmd="$BTRFS_UTIL_PROG subvolume snapshot -r $SCRATCH_MNT"` for Btrfs control and standard shell/file utilities for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_mkfs >> $seqres.full 2>&1`; `_scratch_mount`. The core workload then performs these representative operations: `snapshot_cmd="$BTRFS_UTIL_PROG subvolume snapshot -r $SCRATCH_MNT"`. It also uses background or repeated stress/control loops: `_scratch_mkfs >> $seqres.full 2>&1`; `_run_fsstress -p $procs -x "$snapshot_cmd" -X $num_snapshots \`.

## State and Persistence Behavior
Creates snapshot roots and compares parent/child root state. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on scratch filesystem lifecycle helpers, btrfs-progs command wrappers. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
the test is sensitive to kernel, btrfs-progs, and fstests helper behavior because it verifies a narrow historical regression The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
prints `Silence is golden` when no explicit failure path is reached explicit filesystem check must pass Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/078 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/079 -->
# sources/test-tools/xfstests/tests/btrfs/079

## Purpose
Do write along with fiemap ioctl. Regression test for the kernel comit: 51f395ad btrfs: Use right extent length when inserting overlap extent map. When calling fiemap(without SYNC flag) and btrfs fs is commiting, it will cause race condition and cause btrfs to generate a wrong extent whose len is overflow and fail to insert into the extent map tree, returning -EEXIST. The script is categorized by `_begin_fstest` as `auto`, `rw`, `metadata`, `fiemap`, `prealloc`, and its main coverage is: Metadata consistency, orphan items, delayed references, extent maps, checksums, trim boundaries, and filesystem check behavior. Preallocated extent handling, fallocate/fpunch behavior, and distinguishing real data from holes during send or clone.

## Important APIs, Types, and Functions
local shell functions: `_cleanup`, `dd_work`, `_filter_error`, `fiemap_work` fstest tags: `auto`, `rw`, `metadata`, `fiemap`, `prealloc` requirement gates: `_require_scratch`, `_require_command`, `_require_xfs_io_command`, `_require_fs_space`. The important external command surfaces are `_btrfs`/`$BTRFS_UTIL_PROG` where present for Btrfs control and `_require_command "$FILEFRAG_PROG" filefrag`; `$XFS_IO_PROG -f -c "falloc 0 $filesize" $testfile`; `dd if=/dev/zero of=$out bs=$buffersize count=$count \`; `$FILEFRAG_PROG $filename 2> $tmp.output 1> /dev/null` for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_mkfs >>$seqres.full 2>&1`; `_scratch_mount`. The core workload then performs these representative operations: `_require_command "$FILEFRAG_PROG" filefrag`; `$XFS_IO_PROG -f -c "falloc 0 $filesize" $testfile`; `dd if=/dev/zero of=$out bs=$buffersize count=$count \`; `$FILEFRAG_PROG $filename 2> $tmp.output 1> /dev/null`. It also uses background or repeated stress/control loops: `kill $dd_pid &> /dev/null`; `kill $fiemap_pid &> /dev/null`; `wait`; `_scratch_mkfs >>$seqres.full 2>&1`; `conv=notrunc &> /dev/null`; `trap "wait; exit" SIGTERM`; plus 7 more source-matched operations.

## State and Persistence Behavior
Mutates a freshly formatted scratch filesystem and relies on command status plus fstests cleanup checks. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on scratch filesystem lifecycle helpers, xfs_io subcommand availability, xfs_io data-shaping commands. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
metadata replay, delayed references, orphan cleanup, extent-map merging, or raw-device reserved ranges can regress without obvious user-visible errors The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
prints `Silence is golden` when no explicit failure path is reached Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/079 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/080 -->
# sources/test-tools/xfstests/tests/btrfs/080

## Purpose
Regression test for a btrfs issue where if right after the snapshot creation ioctl started, a file write followed by a file truncate happened, with both operations increasing the file's size, the created snapshot would capture an inconsistent state of the file system tree. That state reflected the file truncation but it didn't reflect the write operation, and left a gap between two file extent items (and that gap corresponded to the total or a partial area of the write operation's range). This issue was fixed by the following linux kernel patch: The script is categorized by `_begin_fstest` as `auto`, `snapshot`, and its main coverage is: Snapshot creation, readonly snapshot consistency, default subvolume behavior, and interactions between snapshot roots and live/orphaned metadata. Subvolume creation, mounting, deletion, set-default behavior, and placeholder directory semantics.

## Important APIs, Types, and Functions
local shell functions: `_cleanup`, `create_snapshot`, `create_file`, `workout` fstest tags: `auto`, `snapshot` requirement gates: `_require_scratch_nocheck`. The important external command surfaces are `_btrfs subvolume snapshot -r \` for Btrfs control and `run_check $XFS_IO_PROG -f \` for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_mkfs -O list-all 2>&1 | grep -q '\bno-holes\b'`; `_scratch_mkfs "$mkfs_options" >>$seqres.full 2>&1`; `_scratch_mount`; `_check_scratch_fs`. The core workload then performs these representative operations: `_btrfs subvolume snapshot -r \`; `run_check $XFS_IO_PROG -f \`. It also uses background or repeated stress/control loops: `kill $p &> /dev/null`; `create_file $name &`; `create_snapshot &`; `wait $fpid`; `wait $spid`; `_scratch_mkfs -O list-all 2>&1 | grep -q '\bno-holes\b'`; plus 7 more source-matched operations.

## State and Persistence Behavior
Creates snapshot roots and compares parent/child root state; uses digest checks as durable content signals; forces transaction or file-log persistence with sync/fsync. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on scratch filesystem lifecycle without automatic final check, btrfs-progs command wrappers, xfs_io data-shaping commands. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
the test is sensitive to kernel, btrfs-progs, and fstests helper behavior because it verifies a narrow historical regression The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
prints `Silence is golden` when no explicit failure path is reached digest output before and after remount/receive must match expected content explicit filesystem check must pass Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/080 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/081 -->
# sources/test-tools/xfstests/tests/btrfs/081

## Purpose
Regression test for a btrfs clone ioctl issue where races between a clone operation and concurrent target file reads would result in leaving stale data in the page cache. After the clone operation finished, reading from the clone target file would return the old and no longer valid data. This affected only buffered reads (i.e. didn't affect direct IO reads). This issue was fixed by the following linux kernel patch: The script is categorized by `_begin_fstest` as `auto`, `quick`, `clone`, and its main coverage is: Btrfs extent cloning/reflink semantics, including inline extents, same-file clones, holes, compressed extents, page-cache coherency, and fsync/log replay persistence.

## Important APIs, Types, and Functions
local shell functions: `create_source_file`, `create_target_file`, `reader_loop` fstest tags: `auto`, `quick`, `clone` requirement gates: `_require_scratch`, `_require_cloner`. The important external command surfaces are `_btrfs`/`$BTRFS_UTIL_PROG` where present for Btrfs control and `$XFS_IO_PROG \`; `$XFS_IO_PROG -f -c "pwrite -S 0xff 0 $file_size" \`; `$CLONER_PROG -s 0 -d 0 -l $(($num_extents * $extent_size)) \`; `md5sum $SCRATCH_MNT/foo | _filter_scratch`; `md5sum $SCRATCH_MNT/bar | _filter_scratch`; plus 1 more source-matched operations for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_mkfs >>$seqres.full 2>&1`; `_scratch_mount`; `_scratch_cycle_mount`. The core workload then performs these representative operations: `$XFS_IO_PROG \`; `$XFS_IO_PROG -f -c "pwrite -S 0xff 0 $file_size" \`; `$CLONER_PROG -s 0 -d 0 -l $(($num_extents * $extent_size)) \`; `md5sum $SCRATCH_MNT/foo | _filter_scratch`; `md5sum $SCRATCH_MNT/bar | _filter_scratch`; plus 1 more source-matched operations. It also uses background or repeated stress/control loops: `for ((i = 0; i < $num_extents; i++)); do`; `trap "wait; exit" SIGTERM`; `while true; do`; `_scratch_mkfs >>$seqres.full 2>&1`; `reader_loop "bar" &`; `kill $reader_pid > /dev/null 2>&1`; plus 1 more source-matched operations.

## State and Persistence Behavior
Uses digest checks as durable content signals; forces transaction or file-log persistence with sync/fsync. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on scratch filesystem lifecycle helpers, btrfs clone ioctl exerciser, xfs_io data-shaping commands. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
clone/reflink edge cases can corrupt inline extents, holes, compressed extents, page cache, or log replay metadata The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
digest output before and after remount/receive must match expected content Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/081 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/082 -->
# sources/test-tools/xfstests/tests/btrfs/082

## Purpose
Regression test for a btrfs issue of resizing 'thread_pool' when remount the fs. execution based on kernel workqueue 08a9ff3264181986d1d692a4e6fce3669700c9f8 And it was fixed by the following linux kernel commit: 800ee2247f483b6d05ed47ef3bbc90b56451746c The script is categorized by `_begin_fstest` as `auto`, `quick`, `remount`, and its main coverage is: Mount option transitions, especially flushoncommit, thread_pool resizing, and compression remount changes.

## Important APIs, Types, and Functions
fstest tags: `auto`, `quick`, `remount` requirement gates: `_require_scratch`. The important external command surfaces are `_btrfs`/`$BTRFS_UTIL_PROG` where present for Btrfs control and standard shell/file utilities for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_mkfs >$seqres.full 2>&1`; `_scratch_mount "-o thread_pool=6"`; `_scratch_mount "-o remount,thread_pool=10"`. The core workload then performs these representative operations: . It also uses background or repeated stress/control loops: `_scratch_mkfs >$seqres.full 2>&1`.

## State and Persistence Behavior
Mutates a freshly formatted scratch filesystem and relies on command status plus fstests cleanup checks. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on scratch filesystem lifecycle helpers. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
the test is sensitive to kernel, btrfs-progs, and fstests helper behavior because it verifies a narrow historical regression The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
prints `Silence is golden` when no explicit failure path is reached Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/082 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/083 -->
# sources/test-tools/xfstests/tests/btrfs/083

## Purpose
Test for incremental send where the difference between the parent and child snapshots is that a directory A was renamed and a directory B was renamed to the name directory A had before (in the parent snapshot), but directory A's rename must happen before some other directory C is renamed. This issue was fixed by the following linux kernel btrfs patch: The script is categorized by `_begin_fstest` as `auto`, `quick`, `send`, and its main coverage is: Btrfs send/receive stream generation, including full sends, incremental parent sends, clone-source roots, received UUID handling, and replay on a freshly formatted scratch filesystem. Snapshot creation, readonly snapshot consistency, default subvolume behavior, and interactions between snapshot roots and live/orphaned metadata. Subvolume creation, mounting, deletion, set-default behavior, and placeholder directory semantics.

## Important APIs, Types, and Functions
local shell functions: `_cleanup` fstest tags: `auto`, `quick`, `send` requirement gates: `_require_scratch`, `_require_fssum`. The important external command surfaces are `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/mysnap1`; `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/mysnap2`; `_btrfs send -f $send_files_dir/1.snap $SCRATCH_MNT/mysnap1`; `_btrfs send -p $SCRATCH_MNT/mysnap1 -f $send_files_dir/2.snap \`; `_btrfs receive -f $send_files_dir/1.snap $SCRATCH_MNT`; `_btrfs receive -f $send_files_dir/2.snap $SCRATCH_MNT` for Btrfs control and standard shell/file utilities for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_mkfs >>$seqres.full 2>&1`; `_scratch_mount`; `_scratch_unmount`; plus 2 more source-matched operations. The core workload then performs these representative operations: `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/mysnap1`; `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/mysnap2`; `_btrfs send -f $send_files_dir/1.snap $SCRATCH_MNT/mysnap1`; `_btrfs send -p $SCRATCH_MNT/mysnap1 -f $send_files_dir/2.snap \`; `_btrfs receive -f $send_files_dir/1.snap $SCRATCH_MNT`; `_btrfs receive -f $send_files_dir/2.snap $SCRATCH_MNT`. It also uses background or repeated stress/control loops: `_scratch_mkfs >>$seqres.full 2>&1`; plus 1 more source-matched operations.

## State and Persistence Behavior
Creates snapshot roots and compares parent/child root state; persists send streams to temporary files and replays them on a reformatted scratch filesystem; records fssum manifests and validates received trees against them. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on scratch filesystem lifecycle helpers, fssum content manifests for send/receive equivalence, btrfs-progs command wrappers. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
send path ordering can emit invalid rename, rmdir, clone, or path records if inode identity, generation, or delayed-move state is mishandled The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
prints `Silence is golden` when no explicit failure path is reached fssum replay must match original snapshot manifests Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/083 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/084 -->
# sources/test-tools/xfstests/tests/btrfs/084

## Purpose
Test for incremental send where the difference between the parent and send snapshots is that for a subtree with the same path in both snapshots (p1/p2), the root directories were swapped. This issue was fixed by the following linux kernel btrfs patch: The script is categorized by `_begin_fstest` as `auto`, `quick`, `send`, and its main coverage is: Btrfs send/receive stream generation, including full sends, incremental parent sends, clone-source roots, received UUID handling, and replay on a freshly formatted scratch filesystem. Snapshot creation, readonly snapshot consistency, default subvolume behavior, and interactions between snapshot roots and live/orphaned metadata. Subvolume creation, mounting, deletion, set-default behavior, and placeholder directory semantics.

## Important APIs, Types, and Functions
local shell functions: `_cleanup` fstest tags: `auto`, `quick`, `send` requirement gates: `_require_scratch`, `_require_fssum`. The important external command surfaces are `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/mysnap1`; `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/mysnap2`; `_btrfs send -f $send_files_dir/1.snap $SCRATCH_MNT/mysnap1`; `_btrfs send -p $SCRATCH_MNT/mysnap1 -f $send_files_dir/2.snap \`; `_btrfs receive -f $send_files_dir/1.snap $SCRATCH_MNT`; `_btrfs receive -f $send_files_dir/2.snap $SCRATCH_MNT` for Btrfs control and standard shell/file utilities for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_mkfs >>$seqres.full 2>&1`; `_scratch_mount`; `_scratch_unmount`; plus 2 more source-matched operations. The core workload then performs these representative operations: `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/mysnap1`; `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/mysnap2`; `_btrfs send -f $send_files_dir/1.snap $SCRATCH_MNT/mysnap1`; `_btrfs send -p $SCRATCH_MNT/mysnap1 -f $send_files_dir/2.snap \`; `_btrfs receive -f $send_files_dir/1.snap $SCRATCH_MNT`; `_btrfs receive -f $send_files_dir/2.snap $SCRATCH_MNT`. It also uses background or repeated stress/control loops: `_scratch_mkfs >>$seqres.full 2>&1`; plus 1 more source-matched operations.

## State and Persistence Behavior
Creates snapshot roots and compares parent/child root state; persists send streams to temporary files and replays them on a reformatted scratch filesystem; records fssum manifests and validates received trees against them. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on scratch filesystem lifecycle helpers, fssum content manifests for send/receive equivalence, btrfs-progs command wrappers. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
send path ordering can emit invalid rename, rmdir, clone, or path records if inode identity, generation, or delayed-move state is mishandled The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
prints `Silence is golden` when no explicit failure path is reached fssum replay must match original snapshot manifests Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/084 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/085 -->
# sources/test-tools/xfstests/tests/btrfs/085

## Purpose
Tests to ensure that orphan items are properly created and cleaned up on next mount. There are three cases where orphan items may be cleaned up: 1) Default subvolume is fs tree root (mkfs default) 2) Default subvolume is explicitly created subvolume 3) Non-default subvolume lookup The script is categorized by `_begin_fstest` as `auto`, `quick`, `metadata`, `subvol`, and its main coverage is: Subvolume creation, mounting, deletion, set-default behavior, and placeholder directory semantics. Metadata consistency, orphan items, delayed references, extent maps, checksums, trim boundaries, and filesystem check behavior.

## Important APIs, Types, and Functions
local shell functions: `_cleanup`, `has_orphan_item`, `test_orphan`, `new_subvolume`, `new_default` fstest tags: `auto`, `quick`, `metadata`, `subvol` requirement gates: `_require_scratch`, `_require_dm_target`, `_require_btrfs_command`. The important external command surfaces are `if $BTRFS_UTIL_PROG inspect-internal dump-tree $SCRATCH_DEV | \`; `_btrfs subvolume create $SCRATCH_MNT/testdir`; `SUB=$($BTRFS_UTIL_PROG subvolume list $SCRATCH_MNT | $AWK_PROG '{print $2}')`; `_btrfs subvolume set-default $SUB $SCRATCH_MNT` for Btrfs control and `run_check dd if=/dev/zero of=$TESTPATH bs=$SIZE count=1` for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_cleanup_flakey`; `_scratch_mkfs >> $seqres.full 2>&1`; `_init_flakey`; `_scratch_mount`; `_load_flakey_table $FLAKEY_DROP_WRITES`; `_scratch_unmount`; `_load_flakey_table $FLAKEY_ALLOW_WRITES`; plus 5 more source-matched operations. The core workload then performs these representative operations: `if $BTRFS_UTIL_PROG inspect-internal dump-tree $SCRATCH_DEV | \`; `_btrfs subvolume create $SCRATCH_MNT/testdir`; `SUB=$($BTRFS_UTIL_PROG subvolume list $SCRATCH_MNT | $AWK_PROG '{print $2}')`; `_btrfs subvolume set-default $SUB $SCRATCH_MNT`; `run_check dd if=/dev/zero of=$TESTPATH bs=$SIZE count=1`. It also uses background or repeated stress/control loops: `_scratch_mkfs >> $seqres.full 2>&1`; `exec 27>&-`.

## State and Persistence Behavior
Forces transaction or file-log persistence with sync/fsync; injects block-layer failure to model crash or eio behavior. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on scratch filesystem lifecycle helpers, device-mapper target support, specific btrfs-progs subcommand availability, btrfs-progs command wrappers, dm-flakey crash simulation. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
metadata replay, delayed references, orphan cleanup, extent-map merging, or raw-device reserved ranges can regress without obvious user-visible errors The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
successful command completion and fstests cleanup checks are the primary signal Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/085 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/086 -->
# sources/test-tools/xfstests/tests/btrfs/086

## Purpose
Test cloning a file range with a length of zero into a destination offset greater than zero. This made btrfs create an extent state record with a start offset greater than the end offset, resulting in chaos such as an infinite loop when evicting an inode. This issue was fixed by the following linux kernel patch: The script is categorized by `_begin_fstest` as `auto`, `quick`, `clone`, and its main coverage is: Btrfs extent cloning/reflink semantics, including inline extents, same-file clones, holes, compressed extents, page-cache coherency, and fsync/log replay persistence.

## Important APIs, Types, and Functions
fstest tags: `auto`, `quick`, `clone` requirement gates: `_require_scratch`, `_require_cloner`. The important external command surfaces are `_btrfs`/`$BTRFS_UTIL_PROG` where present for Btrfs control and `$CLONER_PROG -s 0 -d 65536 -l 0 $SCRATCH_MNT/foo $SCRATCH_MNT/bar` for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_mkfs >>$seqres.full 2>&1`; `_scratch_mount`. The core workload then performs these representative operations: `$CLONER_PROG -s 0 -d 65536 -l 0 $SCRATCH_MNT/foo $SCRATCH_MNT/bar`. It also uses background or repeated stress/control loops: `_scratch_mkfs >>$seqres.full 2>&1`.

## State and Persistence Behavior
Mutates a freshly formatted scratch filesystem and relies on command status plus fstests cleanup checks. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on scratch filesystem lifecycle helpers, btrfs clone ioctl exerciser. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
clone/reflink edge cases can corrupt inline extents, holes, compressed extents, page cache, or log replay metadata The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
successful command completion and fstests cleanup checks are the primary signal Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/086 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/087 -->
# sources/test-tools/xfstests/tests/btrfs/087

## Purpose
Test a very complex scenario for a btrfs incremental send operation where a large directory hierarchy had many subtrees moved between parent directories, preserving the names of some directories and inverting the parent-child relationship between some directories (a child in the parent snapshot became a parent, in the send snapshot, of the directory that is its parent in the parent snapshot). This test made the incremental send fail with -ENOMEM because it entered an infinite loop when building path strings that are used as operands of the rename operations issued in the send stream. This issue was fixed by the following linux kernel btrfs patch: The script is categorized by `_begin_fstest` as `auto`, `quick`, `send`, and its main coverage is: Btrfs send/receive stream generation, including full sends, incremental parent sends, clone-source roots, received UUID handling, and replay on a freshly formatted scratch filesystem. Snapshot creation, readonly snapshot consistency, default subvolume behavior, and interactions between snapshot roots and live/orphaned metadata.

## Important APIs, Types, and Functions
local shell functions: `_cleanup` fstest tags: `auto`, `quick`, `send` requirement gates: `_require_scratch`, `_require_fssum`. The important external command surfaces are `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/mysnap1`; `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/mysnap2`; `_btrfs send -f $send_files_dir/1.snap $SCRATCH_MNT/mysnap1`; `_btrfs send -p $SCRATCH_MNT/mysnap1 -f $send_files_dir/2.snap \`; `_btrfs receive -f $send_files_dir/1.snap $SCRATCH_MNT`; `_btrfs receive -f $send_files_dir/2.snap $SCRATCH_MNT` for Btrfs control and standard shell/file utilities for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_mkfs >>$seqres.full 2>&1`; `_scratch_mount`; `_scratch_unmount`; plus 2 more source-matched operations. The core workload then performs these representative operations: `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/mysnap1`; `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/mysnap2`; `_btrfs send -f $send_files_dir/1.snap $SCRATCH_MNT/mysnap1`; `_btrfs send -p $SCRATCH_MNT/mysnap1 -f $send_files_dir/2.snap \`; `_btrfs receive -f $send_files_dir/1.snap $SCRATCH_MNT`; `_btrfs receive -f $send_files_dir/2.snap $SCRATCH_MNT`. It also uses background or repeated stress/control loops: `_scratch_mkfs >>$seqres.full 2>&1`; plus 1 more source-matched operations.

## State and Persistence Behavior
Creates snapshot roots and compares parent/child root state; persists send streams to temporary files and replays them on a reformatted scratch filesystem; records fssum manifests and validates received trees against them. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on scratch filesystem lifecycle helpers, fssum content manifests for send/receive equivalence, btrfs-progs command wrappers. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
send path ordering can emit invalid rename, rmdir, clone, or path records if inode identity, generation, or delayed-move state is mishandled The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
prints `Silence is golden` when no explicit failure path is reached fssum replay must match original snapshot manifests Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/087 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/088 -->
# sources/test-tools/xfstests/tests/btrfs/088

## Purpose
Test that btrfs' transaction abortion does not corrupt a filesystem mounted with -o discard nor allows a subsequent fstrim to corrupt the filesystem This issue was fixed by the following linux kernel patch: The script is categorized by `_begin_fstest` as `auto`, `quick`, `metadata`, and its main coverage is: Metadata consistency, orphan items, delayed references, extent maps, checksums, trim boundaries, and filesystem check behavior.

## Important APIs, Types, and Functions
local shell functions: `enable_io_failure`, `disable_io_failure` fstest tags: `auto`, `quick`, `metadata` requirement gates: `_require_scratch`, `_require_fail_make_request`, `_require_batched_discard`. The important external command surfaces are `_btrfs`/`$BTRFS_UTIL_PROG` where present for Btrfs control and `$XFS_IO_PROG -f -c "pwrite -S 0xaa 0 1M" $SCRATCH_MNT/foo | _filter_xfs_io`; `$XFS_IO_PROG -c "pwrite -S 0xbb 512K 1M" $SCRATCH_MNT/foo | _filter_xfs_io`; `$FSTRIM_PROG $SCRATCH_MNT`; `od -t x1 $SCRATCH_MNT/foo` for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_mkfs >>$seqres.full 2>&1`; `_scratch_mount "-o discard"`; `_scratch_cycle_mount`. The core workload then performs these representative operations: `$XFS_IO_PROG -f -c "pwrite -S 0xaa 0 1M" $SCRATCH_MNT/foo | _filter_xfs_io`; `$XFS_IO_PROG -c "pwrite -S 0xbb 512K 1M" $SCRATCH_MNT/foo | _filter_xfs_io`; `$FSTRIM_PROG $SCRATCH_MNT`; `od -t x1 $SCRATCH_MNT/foo`. It also uses background or repeated stress/control loops: `_scratch_mkfs >>$seqres.full 2>&1`; `touch $SCRATCH_MNT/abc >>$seqres.full 2>&1 && \`.

## State and Persistence Behavior
Forces transaction or file-log persistence with sync/fsync; verifies discard persistence at raw device offsets. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on scratch filesystem lifecycle helpers, xfs_io data-shaping commands. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
metadata replay, delayed references, orphan cleanup, extent-map merging, or raw-device reserved ranges can regress without obvious user-visible errors The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
hex dumps expose exact byte-level clone or hole behavior Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/088 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/089 -->
# sources/test-tools/xfstests/tests/btrfs/089

## Purpose
Test deleting the default subvolume, making sure that submounts under it are not unmounted prematurely. This is a regression test for Linux commit "Btrfs: don't invalidate root dentry when subvolume deletion fails". The script is categorized by `_begin_fstest` as `auto`, `quick`, `subvol`, and its main coverage is: Subvolume creation, mounting, deletion, set-default behavior, and placeholder directory semantics.

## Important APIs, Types, and Functions
fstest tags: `auto`, `quick`, `subvol` requirement gates: `_require_scratch`. The important external command surfaces are `$BTRFS_UTIL_PROG subvolume create "$SCRATCH_MNT/testvol" >>$seqres.full 2>&1 \`; `$BTRFS_UTIL_PROG subvolume set-default $testvol_id "$SCRATCH_MNT" >>$seqres.full 2>&1 \`; `$BTRFS_UTIL_PROG subvolume delete "$SCRATCH_MNT/testvol" >>$seqres.full 2>&1` for Btrfs control and standard shell/file utilities for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_mkfs >>$seqres.full 2>&1`; `_scratch_mount`. The core workload then performs these representative operations: `$BTRFS_UTIL_PROG subvolume create "$SCRATCH_MNT/testvol" >>$seqres.full 2>&1 \`; `$BTRFS_UTIL_PROG subvolume set-default $testvol_id "$SCRATCH_MNT" >>$seqres.full 2>&1 \`; `$BTRFS_UTIL_PROG subvolume delete "$SCRATCH_MNT/testvol" >>$seqres.full 2>&1`. It also uses background or repeated stress/control loops: `_scratch_mkfs >>$seqres.full 2>&1`; `$BTRFS_UTIL_PROG subvolume create "$SCRATCH_MNT/testvol" >>$seqres.full 2>&1 \`; `$BTRFS_UTIL_PROG subvolume set-default $testvol_id "$SCRATCH_MNT" >>$seqres.full 2>&1 \`; `$BTRFS_UTIL_PROG subvolume delete "$SCRATCH_MNT/testvol" >>$seqres.full 2>&1`.

## State and Persistence Behavior
Mutates a freshly formatted scratch filesystem and relies on command status plus fstests cleanup checks. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on scratch filesystem lifecycle helpers, btrfs-progs command wrappers, Btrfs-specific output filters. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
the test is sensitive to kernel, btrfs-progs, and fstests helper behavior because it verifies a narrow historical regression The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
prints `Silence is golden` when no explicit failure path is reached Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/089 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/090 -->
# sources/test-tools/xfstests/tests/btrfs/090

## Purpose
Check return value of "btrfs filesystem show" command executed on umounted device. It should return 0 if nothing wrong happens. btrfs-progs: Fix wrong return value when executing 'fi show' on umounted device. The script is categorized by `_begin_fstest` as `auto`, `quick`, `metadata`, and its main coverage is: Metadata consistency, orphan items, delayed references, extent maps, checksums, trim boundaries, and filesystem check behavior.

## Important APIs, Types, and Functions
fstest tags: `auto`, `quick`, `metadata` requirement gates: `_require_scratch`, `_require_scratch_dev_pool`. The important external command surfaces are `_btrfs filesystem show $FIRST_POOL_DEV | \` for Btrfs control and standard shell/file utilities for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_pool_mkfs >> $seqres.full 2>&1 || _fail "mkfs failed"`. The core workload then performs these representative operations: `_btrfs filesystem show $FIRST_POOL_DEV | \`. It also uses background or repeated stress/control loops: `_scratch_pool_mkfs >> $seqres.full 2>&1 || _fail "mkfs failed"`.

## State and Persistence Behavior
Mutates a freshly formatted scratch filesystem and relies on command status plus fstests cleanup checks. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on scratch filesystem lifecycle helpers, multi-device scratch pool, btrfs-progs command wrappers, Btrfs-specific output filters. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
metadata replay, delayed references, orphan cleanup, extent-map merging, or raw-device reserved ranges can regress without obvious user-visible errors The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
prints `Silence is golden` when no explicit failure path is reached Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/090 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/091 -->
# sources/test-tools/xfstests/tests/btrfs/091

## Purpose
Test for incorrect exclusive reference count after cloning file between subvolumes. The script is categorized by `_begin_fstest` as `auto`, `quick`, `qgroup`, and its main coverage is: Quota group enablement, rescan, limits, accounting of shared/exclusive extents, and crash or deletion paths that can leave qgroup state inconsistent. Compressed extent behavior across read, restore, clone, send, defrag, remount, and property inheritance paths. Subvolume creation, mounting, deletion, set-default behavior, and placeholder directory semantics.

## Important APIs, Types, and Functions
fstest tags: `auto`, `quick`, `qgroup` requirement gates: `_require_scratch`, `_require_cp_reflink`, `_require_scratch_qgroup`. The important external command surfaces are `_btrfs subvolume create $SCRATCH_MNT/subv1`; `_btrfs subvolume create $SCRATCH_MNT/subv2`; `_btrfs subvolume create $SCRATCH_MNT/subv3`; `_btrfs quota enable $SCRATCH_MNT`; `$BTRFS_UTIL_PROG qgroup show $units $SCRATCH_MNT | $SED_PROG -n '/[0-9]/p' | \` for Btrfs control and `$XFS_IO_PROG -f -c "pwrite 0 256K" $SCRATCH_MNT/subv1/file1 | _filter_xfs_io`; `cp --reflink $SCRATCH_MNT/subv1/file1 $SCRATCH_MNT/subv2/file1`; `cp --reflink $SCRATCH_MNT/subv1/file1 $SCRATCH_MNT/subv3/file1` for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `run_check _scratch_mkfs "--nodesize $NODESIZE"`; `_try_scratch_mount "-o compress=no,compress-force=no" 2> /dev/null`. The core workload then performs these representative operations: `_btrfs subvolume create $SCRATCH_MNT/subv1`; `_btrfs subvolume create $SCRATCH_MNT/subv2`; `_btrfs subvolume create $SCRATCH_MNT/subv3`; `_btrfs quota enable $SCRATCH_MNT`; `$BTRFS_UTIL_PROG qgroup show $units $SCRATCH_MNT | $SED_PROG -n '/[0-9]/p' | \`; `$XFS_IO_PROG -f -c "pwrite 0 256K" $SCRATCH_MNT/subv1/file1 | _filter_xfs_io`; `cp --reflink $SCRATCH_MNT/subv1/file1 $SCRATCH_MNT/subv2/file1`; `cp --reflink $SCRATCH_MNT/subv1/file1 $SCRATCH_MNT/subv3/file1`. The workload is mostly sequential, so failure attribution is tied to the exact command that exits non-zero.

## State and Persistence Behavior
Forces transaction or file-log persistence with sync/fsync; mutates qgroup metadata and relies on final accounting checks. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on scratch filesystem lifecycle helpers, cp --reflink support, btrfs-progs command wrappers, xfs_io data-shaping commands. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
qgroup accounting can leak reservations or miscount shared/exclusive extents after snapshots, rescans, deletes, or limits compressed extents with non-zero offsets or shared references can return stale, zeroed, or mis-cloned data The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
fstests qgroup reporting/checking validates quota consistency Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/091 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/092 -->
# sources/test-tools/xfstests/tests/btrfs/092

## Purpose
Test btrfs incremental send after renaming and moving directories around in a way that ends up making a directory have different dentries with the same name but pointing to different inodes in the parent and send snapshots, and also inverting the ancestor-descendent relationship between one of those inodes and some other inode. Cases like this made an incremental send enter an infinite lopp when building path strings, leading to -ENOMEM errors when the path string reached a length of PATH_MAX. This issue was fixed by the following linux kernel btrfs patch: The script is categorized by `_begin_fstest` as `auto`, `quick`, `send`, and its main coverage is: Btrfs send/receive stream generation, including full sends, incremental parent sends, clone-source roots, received UUID handling, and replay on a freshly formatted scratch filesystem. Snapshot creation, readonly snapshot consistency, default subvolume behavior, and interactions between snapshot roots and live/orphaned metadata.

## Important APIs, Types, and Functions
local shell functions: `_cleanup` fstest tags: `auto`, `quick`, `send` requirement gates: `_require_scratch`, `_require_fssum`. The important external command surfaces are `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/mysnap1`; `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/mysnap2`; `_btrfs send -f $send_files_dir/1.snap $SCRATCH_MNT/mysnap1`; `_btrfs send -p $SCRATCH_MNT/mysnap1 -f $send_files_dir/2.snap \`; `_btrfs receive -f $send_files_dir/1.snap $SCRATCH_MNT`; `_btrfs receive -f $send_files_dir/2.snap $SCRATCH_MNT` for Btrfs control and standard shell/file utilities for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_mkfs >>$seqres.full 2>&1`; `_scratch_mount`; `_scratch_unmount`; plus 2 more source-matched operations. The core workload then performs these representative operations: `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/mysnap1`; `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/mysnap2`; `_btrfs send -f $send_files_dir/1.snap $SCRATCH_MNT/mysnap1`; `_btrfs send -p $SCRATCH_MNT/mysnap1 -f $send_files_dir/2.snap \`; `_btrfs receive -f $send_files_dir/1.snap $SCRATCH_MNT`; `_btrfs receive -f $send_files_dir/2.snap $SCRATCH_MNT`. It also uses background or repeated stress/control loops: `_scratch_mkfs >>$seqres.full 2>&1`; plus 1 more source-matched operations.

## State and Persistence Behavior
Creates snapshot roots and compares parent/child root state; persists send streams to temporary files and replays them on a reformatted scratch filesystem; records fssum manifests and validates received trees against them. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on scratch filesystem lifecycle helpers, fssum content manifests for send/receive equivalence, btrfs-progs command wrappers. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
send path ordering can emit invalid rename, rmdir, clone, or path records if inode identity, generation, or delayed-move state is mishandled The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
prints `Silence is golden` when no explicit failure path is reached fssum replay must match original snapshot manifests Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/092 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/093 -->
# sources/test-tools/xfstests/tests/btrfs/093

## Purpose
Test btrfs file range cloning with the same file as a source and destination. This tests a specific scenario where the extent layout of the file confused the clone ioctl implementation making it return -EEXIST to userspace. This issue was fixed by the following linux kernel patch: The script is categorized by `_begin_fstest` as `auto`, `quick`, `clone`, and its main coverage is: Btrfs extent cloning/reflink semantics, including inline extents, same-file clones, holes, compressed extents, page-cache coherency, and fsync/log replay persistence.

## Important APIs, Types, and Functions
local shell functions: `test_clone` fstest tags: `auto`, `quick`, `clone` requirement gates: `_require_scratch`, `_require_cloner`. The important external command surfaces are `_btrfs`/`$BTRFS_UTIL_PROG` where present for Btrfs control and `$XFS_IO_PROG -f -c "pwrite -S 0xaa $((2 * $bs)) $((2 * $bs))" \`; `$CLONER_PROG -s $((3 * $bs)) -d $((267 * $bs)) -l 0 $SCRATCH_MNT/foo \`; `$CLONER_PROG -s $((217 * $bs)) -d $((95 * $bs)) -l 0 $SCRATCH_MNT/foo \`; `md5sum $SCRATCH_MNT/foo | _filter_scratch`; `$CLONER_PROG -s $((3 * $bs)) -d $((267 * $bs)) -l 0 $SCRATCH_MNT/a \`; `$CLONER_PROG -s $((217 * $bs)) -d $((95 * $bs)) -l 0 $SCRATCH_MNT/b \`; plus 2 more source-matched operations for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_mkfs "-O ^no-holes -n $bs" >>$seqres.full 2>&1`; `_scratch_mount`; `_check_scratch_fs`; `_scratch_unmount`; `_scratch_mkfs "-O no-holes -n $bs" >>$seqres.full 2>&1`; plus 1 more source-matched operations. The core workload then performs these representative operations: `$XFS_IO_PROG -f -c "pwrite -S 0xaa $((2 * $bs)) $((2 * $bs))" \`; `$CLONER_PROG -s $((3 * $bs)) -d $((267 * $bs)) -l 0 $SCRATCH_MNT/foo \`; `$CLONER_PROG -s $((217 * $bs)) -d $((95 * $bs)) -l 0 $SCRATCH_MNT/foo \`; `md5sum $SCRATCH_MNT/foo | _filter_scratch`; `$CLONER_PROG -s $((3 * $bs)) -d $((267 * $bs)) -l 0 $SCRATCH_MNT/a \`; `$CLONER_PROG -s $((217 * $bs)) -d $((95 * $bs)) -l 0 $SCRATCH_MNT/b \`; `md5sum $SCRATCH_MNT/foo2 | _filter_scratch`; plus 1 more source-matched operations. It also uses background or repeated stress/control loops: `_scratch_mkfs "-O ^no-holes -n $bs" >>$seqres.full 2>&1`; `_scratch_mkfs "-O no-holes -n $bs" >>$seqres.full 2>&1`.

## State and Persistence Behavior
Uses digest checks as durable content signals. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on scratch filesystem lifecycle helpers, btrfs clone ioctl exerciser, xfs_io data-shaping commands. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
clone/reflink edge cases can corrupt inline extents, holes, compressed extents, page cache, or log replay metadata The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
digest output before and after remount/receive must match expected content explicit filesystem check must pass Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/093 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/094 -->
# sources/test-tools/xfstests/tests/btrfs/094

## Purpose
Test that an incremental send issues valid clone operations for compressed file extents. For some compressed extents, namely those referred by a file extent item with a non-zero data offset, btrfs could issue a clone operation in the send stream with an offset and length pair that were not entirely contained in the source file's range, causing the receiving side to get -EINVAL errors from the clone ioctl when attempting to perform the clone operations. This issue was fixed by the following linux kernel btrfs patch: The script is categorized by `_begin_fstest` as `auto`, `quick`, `send`, `compress`, and its main coverage is: Btrfs send/receive stream generation, including full sends, incremental parent sends, clone-source roots, received UUID handling, and replay on a freshly formatted scratch filesystem. Btrfs extent cloning/reflink semantics, including inline extents, same-file clones, holes, compressed extents, page-cache coherency, and fsync/log replay persistence. Compressed extent behavior across read, restore, clone, send, defrag, remount, and property inheritance paths. Metadata consistency, orphan items, delayed references, extent maps, checksums, trim boundaries, and filesystem check behavior.

## Important APIs, Types, and Functions
local shell functions: `_cleanup` fstest tags: `auto`, `quick`, `send`, `compress` requirement gates: `_require_scratch`, `_require_cloner`. The important external command surfaces are `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/mysnap1`; `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/mysnap2`; `_btrfs send -f $send_files_dir/1.snap $SCRATCH_MNT/mysnap1`; `_btrfs send -p $SCRATCH_MNT/mysnap1 -f $send_files_dir/2.snap \`; `_btrfs receive -f $send_files_dir/1.snap $SCRATCH_MNT`; `_btrfs receive -f $send_files_dir/2.snap $SCRATCH_MNT` for Btrfs control and `$XFS_IO_PROG -f -c "pwrite -S 0xaa $((16 * $BLOCK_SIZE)) $((32 * $BLOCK_SIZE))" \`; `$XFS_IO_PROG -c "pwrite -S 0xbb $((16 * $BLOCK_SIZE)) $((28 * $BLOCK_SIZE))" \`; `$XFS_IO_PROG -c "pwrite -S 0xcc $((45 * $BLOCK_SIZE)) $((3 * $BLOCK_SIZE))" \`; `$CLONER_PROG -s $((44 * $BLOCK_SIZE)) -d $((44 * $BLOCK_SIZE)) -l $BLOCK_SIZE \`; `od -t x1 $SCRATCH_MNT/mysnap1/foo | _filter_od`; `od -t x1 $SCRATCH_MNT/mysnap2/foo | _filter_od`; plus 4 more source-matched operations for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_mkfs >>$seqres.full 2>&1`; `_scratch_mount "-o compress"`; `_scratch_unmount`; `_scratch_mount`; plus 1 more source-matched operations. The core workload then performs these representative operations: `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/mysnap1`; `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/mysnap2`; `_btrfs send -f $send_files_dir/1.snap $SCRATCH_MNT/mysnap1`; `_btrfs send -p $SCRATCH_MNT/mysnap1 -f $send_files_dir/2.snap \`; `_btrfs receive -f $send_files_dir/1.snap $SCRATCH_MNT`; `_btrfs receive -f $send_files_dir/2.snap $SCRATCH_MNT`; `$XFS_IO_PROG -f -c "pwrite -S 0xaa $((16 * $BLOCK_SIZE)) $((32 * $BLOCK_SIZE))" \`; `$XFS_IO_PROG -c "pwrite -S 0xbb $((16 * $BLOCK_SIZE)) $((28 * $BLOCK_SIZE))" \`; `$XFS_IO_PROG -c "pwrite -S 0xcc $((45 * $BLOCK_SIZE)) $((3 * $BLOCK_SIZE))" \`; `$CLONER_PROG -s $((44 * $BLOCK_SIZE)) -d $((44 * $BLOCK_SIZE)) -l $BLOCK_SIZE \`; plus 6 more source-matched operations. It also uses background or repeated stress/control loops: `_scratch_mkfs >>$seqres.full 2>&1`; plus 1 more source-matched operations.

## State and Persistence Behavior
Creates snapshot roots and compares parent/child root state; persists send streams to temporary files and replays them on a reformatted scratch filesystem; forces transaction or file-log persistence with sync/fsync. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on scratch filesystem lifecycle helpers, btrfs clone ioctl exerciser, btrfs-progs command wrappers, xfs_io data-shaping commands. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
send path ordering can emit invalid rename, rmdir, clone, or path records if inode identity, generation, or delayed-move state is mishandled clone/reflink edge cases can corrupt inline extents, holes, compressed extents, page cache, or log replay metadata compressed extents with non-zero offsets or shared references can return stale, zeroed, or mis-cloned data metadata replay, delayed references, orphan cleanup, extent-map merging, or raw-device reserved ranges can regress without obvious user-visible errors The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
hex dumps expose exact byte-level clone or hole behavior Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/094 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/095 -->
# sources/test-tools/xfstests/tests/btrfs/095

## Purpose
Regression test for adding and dropping an equal number of references for file extents. Verify that if we drop N references for a file extent and we add too N new references for that same file extent in the same transaction, running the delayed references (always happens at transaction commit time) does not fail. The regression was introduced in the 4.2-rc1 Linux kernel. The script is categorized by `_begin_fstest` as `auto`, `quick`, `metadata`, `log`, `preallocrw`, and its main coverage is: Btrfs extent cloning/reflink semantics, including inline extents, same-file clones, holes, compressed extents, page-cache coherency, and fsync/log replay persistence. Metadata consistency, orphan items, delayed references, extent maps, checksums, trim boundaries, and filesystem check behavior. Preallocated extent handling, fallocate/fpunch behavior, and distinguishing real data from holes during send or clone. Fsync log tree replay and power-failure simulation through dm-flakey to verify durable metadata and checksum recovery.

## Important APIs, Types, and Functions
local shell functions: `_cleanup` fstest tags: `auto`, `quick`, `metadata`, `log`, `preallocrw` requirement gates: `_require_scratch`, `_require_dm_target`, `_require_cloner`, `_require_xfs_io_command`, `_require_metadata_journaling`. The important external command surfaces are `_btrfs`/`$BTRFS_UTIL_PROG` where present for Btrfs control and `$XFS_IO_PROG -f -c "falloc $((40 * $BLOCK_SIZE)) $((115 * $BLOCK_SIZE))" \`; `$XFS_IO_PROG -c "pwrite -S 0xaa $((135 * $BLOCK_SIZE)) $((30 * $BLOCK_SIZE))" \`; `$CLONER_PROG -s $((40 * $BLOCK_SIZE)) -d $((512 * $BLOCK_SIZE)) -l 0 \`; `$XFS_IO_PROG -c "pwrite -S 0xbb $((768 * $BLOCK_SIZE)) $((25 * $BLOCK_SIZE))" \`; `$CLONER_PROG -s $((768 * $BLOCK_SIZE)) -d $((150 * $BLOCK_SIZE)) -l $((25 * $BLOCK_SIZE)) \`; `$XFS_IO_PROG -c "fsync" $SCRATCH_MNT/foo`; plus 2 more source-matched operations for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_cleanup_flakey`; `_scratch_mkfs >>$seqres.full 2>&1`; `_init_flakey`; `_scratch_mount`; `_flakey_drop_and_remount`; `_scratch_unmount`. The core workload then performs these representative operations: `$XFS_IO_PROG -f -c "falloc $((40 * $BLOCK_SIZE)) $((115 * $BLOCK_SIZE))" \`; `$XFS_IO_PROG -c "pwrite -S 0xaa $((135 * $BLOCK_SIZE)) $((30 * $BLOCK_SIZE))" \`; `$CLONER_PROG -s $((40 * $BLOCK_SIZE)) -d $((512 * $BLOCK_SIZE)) -l 0 \`; `$XFS_IO_PROG -c "pwrite -S 0xbb $((768 * $BLOCK_SIZE)) $((25 * $BLOCK_SIZE))" \`; `$CLONER_PROG -s $((768 * $BLOCK_SIZE)) -d $((150 * $BLOCK_SIZE)) -l $((25 * $BLOCK_SIZE)) \`; `$XFS_IO_PROG -c "fsync" $SCRATCH_MNT/foo`; `od -t x1 $SCRATCH_MNT/foo | _filter_od`; plus 1 more source-matched operations. It also uses background or repeated stress/control loops: `_scratch_mkfs >>$seqres.full 2>&1`.

## State and Persistence Behavior
Forces transaction or file-log persistence with sync/fsync; injects block-layer failure to model crash or eio behavior. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on scratch filesystem lifecycle helpers, device-mapper target support, btrfs clone ioctl exerciser, xfs_io subcommand availability, xfs_io data-shaping commands, dm-flakey crash simulation. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
clone/reflink edge cases can corrupt inline extents, holes, compressed extents, page cache, or log replay metadata metadata replay, delayed references, orphan cleanup, extent-map merging, or raw-device reserved ranges can regress without obvious user-visible errors The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
hex dumps expose exact byte-level clone or hole behavior Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/095 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/096 -->
# sources/test-tools/xfstests/tests/btrfs/096

## Purpose
Test that we can not clone an inline extent into a non-zero file offset. The script is categorized by `_begin_fstest` as `auto`, `quick`, `clone`, and its main coverage is: Btrfs extent cloning/reflink semantics, including inline extents, same-file clones, holes, compressed extents, page-cache coherency, and fsync/log replay persistence.

## Important APIs, Types, and Functions
fstest tags: `auto`, `quick`, `clone` requirement gates: `_require_scratch`, `_require_cloner`. The important external command surfaces are `_btrfs`/`$BTRFS_UTIL_PROG` where present for Btrfs control and `$XFS_IO_PROG -f -s -c "pwrite -S 0xaa 0 $BLOCK_SIZE" \`; `$XFS_IO_PROG -f -s -c "pwrite -S 0xbb 0 2k" \`; `$CLONER_PROG -s 0 -d $BLOCK_SIZE -l 2048 \`; `$XFS_IO_PROG -c "pwrite -S 0xdd $(($BLOCK_SIZE + 2048)) 2k" \` for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_mkfs >>$seqres.full 2>&1`; `_scratch_mount`. The core workload then performs these representative operations: `$XFS_IO_PROG -f -s -c "pwrite -S 0xaa 0 $BLOCK_SIZE" \`; `$XFS_IO_PROG -f -s -c "pwrite -S 0xbb 0 2k" \`; `$CLONER_PROG -s 0 -d $BLOCK_SIZE -l 2048 \`; `$XFS_IO_PROG -c "pwrite -S 0xdd $(($BLOCK_SIZE + 2048)) 2k" \`. It also uses background or repeated stress/control loops: `_scratch_mkfs >>$seqres.full 2>&1`.

## State and Persistence Behavior
Mutates a freshly formatted scratch filesystem and relies on command status plus fstests cleanup checks. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on scratch filesystem lifecycle helpers, btrfs clone ioctl exerciser, xfs_io data-shaping commands, Btrfs-specific output filters. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
clone/reflink edge cases can corrupt inline extents, holes, compressed extents, page cache, or log replay metadata The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
successful command completion and fstests cleanup checks are the primary signal Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/096 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/097 -->
# sources/test-tools/xfstests/tests/btrfs/097

## Purpose
Test that an incremental send works after a file gets one of its extents cloned/deduplicated into lower file offsets. The script is categorized by `_begin_fstest` as `auto`, `quick`, `send`, `clone`, and its main coverage is: Btrfs send/receive stream generation, including full sends, incremental parent sends, clone-source roots, received UUID handling, and replay on a freshly formatted scratch filesystem. Btrfs extent cloning/reflink semantics, including inline extents, same-file clones, holes, compressed extents, page-cache coherency, and fsync/log replay persistence. Snapshot creation, readonly snapshot consistency, default subvolume behavior, and interactions between snapshot roots and live/orphaned metadata. Subvolume creation, mounting, deletion, set-default behavior, and placeholder directory semantics.

## Important APIs, Types, and Functions
local shell functions: `_cleanup` fstest tags: `auto`, `quick`, `send`, `clone` requirement gates: `_require_scratch`, `_require_cloner`. The important external command surfaces are `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/mysnap1`; `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/mysnap2`; `_btrfs send -f $send_files_dir/1.snap $SCRATCH_MNT/mysnap1`; `_btrfs send -p $SCRATCH_MNT/mysnap1 -f $send_files_dir/2.snap \`; `_btrfs receive -f $send_files_dir/1.snap $SCRATCH_MNT`; `_btrfs receive -f $send_files_dir/2.snap $SCRATCH_MNT` for Btrfs control and `$XFS_IO_PROG -f -c "pwrite -S 0xaa $((32 * $BLOCK_SIZE)) $((16 * $BLOCK_SIZE))" \`; `$CLONER_PROG -s $(((32 + 4) * $BLOCK_SIZE)) -d 0 -l $((4 * $BLOCK_SIZE)) \`; `$CLONER_PROG -s $(((32 + 12) * $BLOCK_SIZE)) -d $((4 * $BLOCK_SIZE)) \`; `od -t x1 $SCRATCH_MNT/mysnap2/foo | _filter_od`; plus 1 more source-matched operations for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_mkfs >>$seqres.full 2>&1`; `_scratch_mount`; `_scratch_unmount`; plus 2 more source-matched operations. The core workload then performs these representative operations: `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/mysnap1`; `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/mysnap2`; `_btrfs send -f $send_files_dir/1.snap $SCRATCH_MNT/mysnap1`; `_btrfs send -p $SCRATCH_MNT/mysnap1 -f $send_files_dir/2.snap \`; `_btrfs receive -f $send_files_dir/1.snap $SCRATCH_MNT`; `_btrfs receive -f $send_files_dir/2.snap $SCRATCH_MNT`; `$XFS_IO_PROG -f -c "pwrite -S 0xaa $((32 * $BLOCK_SIZE)) $((16 * $BLOCK_SIZE))" \`; `$CLONER_PROG -s $(((32 + 4) * $BLOCK_SIZE)) -d 0 -l $((4 * $BLOCK_SIZE)) \`; `$CLONER_PROG -s $(((32 + 12) * $BLOCK_SIZE)) -d $((4 * $BLOCK_SIZE)) \`; `od -t x1 $SCRATCH_MNT/mysnap2/foo | _filter_od`; plus 1 more source-matched operations. It also uses background or repeated stress/control loops: `_scratch_mkfs >>$seqres.full 2>&1`; plus 1 more source-matched operations.

## State and Persistence Behavior
Creates snapshot roots and compares parent/child root state; persists send streams to temporary files and replays them on a reformatted scratch filesystem. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on scratch filesystem lifecycle helpers, btrfs clone ioctl exerciser, btrfs-progs command wrappers, xfs_io data-shaping commands. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
send path ordering can emit invalid rename, rmdir, clone, or path records if inode identity, generation, or delayed-move state is mishandled clone/reflink edge cases can corrupt inline extents, holes, compressed extents, page cache, or log replay metadata The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
hex dumps expose exact byte-level clone or hole behavior Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/097 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/098 -->
# sources/test-tools/xfstests/tests/btrfs/098

## Purpose
Test that if we fsync a file that got one extent partially cloned into a lower file offset, after a power failure our file has the same content it had before the power failure and after the extent cloning operation. The script is categorized by `_begin_fstest` as `auto`, `quick`, `metadata`, `clone`, `log`, and its main coverage is: Btrfs extent cloning/reflink semantics, including inline extents, same-file clones, holes, compressed extents, page-cache coherency, and fsync/log replay persistence. Metadata consistency, orphan items, delayed references, extent maps, checksums, trim boundaries, and filesystem check behavior. Fsync log tree replay and power-failure simulation through dm-flakey to verify durable metadata and checksum recovery.

## Important APIs, Types, and Functions
local shell functions: `_cleanup` fstest tags: `auto`, `quick`, `metadata`, `clone`, `log` requirement gates: `_require_scratch`, `_require_dm_target`, `_require_cloner`, `_require_metadata_journaling`. The important external command surfaces are `_btrfs`/`$BTRFS_UTIL_PROG` where present for Btrfs control and `$XFS_IO_PROG -f -c "pwrite -S 0xaa $((200 * $BLOCK_SIZE)) $((25 * $BLOCK_SIZE))" \`; `$CLONER_PROG -s $(((200 * $BLOCK_SIZE) + (5 * $BLOCK_SIZE))) \`; `$XFS_IO_PROG -c "fsync" $SCRATCH_MNT/foo`; `od -t x1 $SCRATCH_MNT/foo | _filter_od`; plus 1 more source-matched operations for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_cleanup_flakey`; `_scratch_mkfs >>$seqres.full 2>&1`; `_init_flakey`; `_scratch_mount`; `_flakey_drop_and_remount`; `_scratch_unmount`. The core workload then performs these representative operations: `$XFS_IO_PROG -f -c "pwrite -S 0xaa $((200 * $BLOCK_SIZE)) $((25 * $BLOCK_SIZE))" \`; `$CLONER_PROG -s $(((200 * $BLOCK_SIZE) + (5 * $BLOCK_SIZE))) \`; `$XFS_IO_PROG -c "fsync" $SCRATCH_MNT/foo`; `od -t x1 $SCRATCH_MNT/foo | _filter_od`; plus 1 more source-matched operations. It also uses background or repeated stress/control loops: `_scratch_mkfs >>$seqres.full 2>&1`.

## State and Persistence Behavior
Forces transaction or file-log persistence with sync/fsync; injects block-layer failure to model crash or eio behavior. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on scratch filesystem lifecycle helpers, device-mapper target support, btrfs clone ioctl exerciser, xfs_io data-shaping commands, dm-flakey crash simulation. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
clone/reflink edge cases can corrupt inline extents, holes, compressed extents, page cache, or log replay metadata metadata replay, delayed references, orphan cleanup, extent-map merging, or raw-device reserved ranges can regress without obvious user-visible errors The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
hex dumps expose exact byte-level clone or hole behavior Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/098 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/099 -->
# sources/test-tools/xfstests/tests/btrfs/099

## Purpose
Check for qgroup reserved space leaks caused by re-writing dirty ranges The script is categorized by `_begin_fstest` as `auto`, `quick`, `qgroup`, `limit`, and its main coverage is: Quota group enablement, rescan, limits, accounting of shared/exclusive extents, and crash or deletion paths that can leave qgroup state inconsistent. Metadata consistency, orphan items, delayed references, extent maps, checksums, trim boundaries, and filesystem check behavior.

## Important APIs, Types, and Functions
fstest tags: `auto`, `quick`, `qgroup`, `limit` requirement gates: `_require_scratch`, `_require_btrfs_qgroup_report`, `_require_fs_space`. The important external command surfaces are `_btrfs quota enable $SCRATCH_MNT`; `_btrfs qgroup limit $FILESIZE 0/5 $SCRATCH_MNT` for Btrfs control and `$XFS_IO_PROG -f -c "pwrite -b $BLOCKSIZE 0 $(($FILESIZE / 4))" \`; `$XFS_IO_PROG -f -c "pwrite -b $BLOCKSIZE 0 $(($FILESIZE - $BLOCKSIZE))" \` for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_mkfs >> $seqres.full 2>&1`; `_scratch_mount`. The core workload then performs these representative operations: `_btrfs quota enable $SCRATCH_MNT`; `_btrfs qgroup limit $FILESIZE 0/5 $SCRATCH_MNT`; `$XFS_IO_PROG -f -c "pwrite -b $BLOCKSIZE 0 $(($FILESIZE / 4))" \`; `$XFS_IO_PROG -f -c "pwrite -b $BLOCKSIZE 0 $(($FILESIZE - $BLOCKSIZE))" \`. It also uses background or repeated stress/control loops: `_scratch_mkfs >> $seqres.full 2>&1`; `for i in `seq 1 5`; do`.

## State and Persistence Behavior
Forces transaction or file-log persistence with sync/fsync; mutates qgroup metadata and relies on final accounting checks. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on scratch filesystem lifecycle helpers, qgroup reporting support, btrfs-progs command wrappers, xfs_io data-shaping commands. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
qgroup accounting can leak reservations or miscount shared/exclusive extents after snapshots, rescans, deletes, or limits metadata replay, delayed references, orphan cleanup, extent-map merging, or raw-device reserved ranges can regress without obvious user-visible errors The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
fstests qgroup reporting/checking validates quota consistency Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/099 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/100 -->
# sources/test-tools/xfstests/tests/btrfs/100

## Purpose
Test device replace works when the source device has EIO The script is categorized by `_begin_fstest` as `auto`, `replace`, `volume`, `eio`, `raid`, and its main coverage is: Device replacement or deletion against RAID-style scratch device pools, including device-mapper error injection and filesystem show verification. Snapshot creation, readonly snapshot consistency, default subvolume behavior, and interactions between snapshot roots and live/orphaned metadata. Subvolume creation, mounting, deletion, set-default behavior, and placeholder directory semantics. I/O error injection through device-mapper targets to validate degraded multi-device behavior.

## Important APIs, Types, and Functions
local shell functions: `_cleanup` fstest tags: `auto`, `replace`, `volume`, `eio`, `raid` requirement gates: `_require_scratch_dev_pool`, `_require_dm_target`. The important external command surfaces are `_btrfs filesystem show -m $SCRATCH_MNT`; `$BTRFS_UTIL_PROG filesystem show -m $SCRATCH_MNT | _filter_btrfs_filesystem_show`; `error_devid=`$BTRFS_UTIL_PROG filesystem show -m $SCRATCH_MNT |\`; `snapshot_cmd="$BTRFS_UTIL_PROG subvolume snapshot -r $SCRATCH_MNT"`; `_btrfs replace start -B $error_devid $dev2 $SCRATCH_MNT`; plus 2 more source-matched operations for Btrfs control and standard shell/file utilities for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_dmerror_cleanup`; `_dmerror_init`; `_dmerror_mount`; `_dmerror_load_error_table`. The core workload then performs these representative operations: `_btrfs filesystem show -m $SCRATCH_MNT`; `$BTRFS_UTIL_PROG filesystem show -m $SCRATCH_MNT | _filter_btrfs_filesystem_show`; `error_devid=`$BTRFS_UTIL_PROG filesystem show -m $SCRATCH_MNT |\`; `snapshot_cmd="$BTRFS_UTIL_PROG subvolume snapshot -r $SCRATCH_MNT"`; `_btrfs replace start -B $error_devid $dev2 $SCRATCH_MNT`; plus 2 more source-matched operations. It also uses background or repeated stress/control loops: `_run_fsstress -d $SCRATCH_MNT -n 200 -p 8 -x "$snapshot_cmd" -X 50`.

## State and Persistence Behavior
Creates snapshot roots and compares parent/child root state; injects block-layer failure to model crash or eio behavior. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on multi-device scratch pool, device-mapper target support, btrfs-progs command wrappers, Btrfs-specific output filters, dm-error I/O failure simulation. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
multi-device operations can race with stress workers, mutually exclusive jobs, scrub, or injected device failure The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
successful command completion and fstests cleanup checks are the primary signal Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/100 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/101 -->
# sources/test-tools/xfstests/tests/btrfs/101

## Purpose
Test device delete when the source device has EIO The script is categorized by `_begin_fstest` as `auto`, `replace`, `volume`, `eio`, `raid`, and its main coverage is: Device replacement or deletion against RAID-style scratch device pools, including device-mapper error injection and filesystem show verification. Snapshot creation, readonly snapshot consistency, default subvolume behavior, and interactions between snapshot roots and live/orphaned metadata. Subvolume creation, mounting, deletion, set-default behavior, and placeholder directory semantics. I/O error injection through device-mapper targets to validate degraded multi-device behavior.

## Important APIs, Types, and Functions
local shell functions: `_cleanup` fstest tags: `auto`, `replace`, `volume`, `eio`, `raid` requirement gates: `_require_scratch_dev_pool`, `_require_btrfs_dev_del_by_devid`, `_require_dm_target`. The important external command surfaces are `_btrfs filesystem show -m $SCRATCH_MNT`; `$BTRFS_UTIL_PROG filesystem show -m $SCRATCH_MNT | _filter_btrfs_filesystem_show`; `error_devid=`$BTRFS_UTIL_PROG filesystem show -m $SCRATCH_MNT |\`; `snapshot_cmd="$BTRFS_UTIL_PROG subvolume snapshot -r $SCRATCH_MNT"`; `_btrfs device delete $error_devid $SCRATCH_MNT`; plus 2 more source-matched operations for Btrfs control and standard shell/file utilities for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_dmerror_cleanup`; `_dmerror_init`; `_dmerror_mount`; `_dmerror_load_error_table`. The core workload then performs these representative operations: `_btrfs filesystem show -m $SCRATCH_MNT`; `$BTRFS_UTIL_PROG filesystem show -m $SCRATCH_MNT | _filter_btrfs_filesystem_show`; `error_devid=`$BTRFS_UTIL_PROG filesystem show -m $SCRATCH_MNT |\`; `snapshot_cmd="$BTRFS_UTIL_PROG subvolume snapshot -r $SCRATCH_MNT"`; `_btrfs device delete $error_devid $SCRATCH_MNT`; plus 2 more source-matched operations. It also uses background or repeated stress/control loops: `_run_fsstress -d $SCRATCH_MNT -n 200 -p 8 -x "$snapshot_cmd" -X 50`.

## State and Persistence Behavior
Creates snapshot roots and compares parent/child root state; injects block-layer failure to model crash or eio behavior. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on multi-device scratch pool, device-mapper target support, btrfs-progs command wrappers, Btrfs-specific output filters, dm-error I/O failure simulation. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
multi-device operations can race with stress workers, mutually exclusive jobs, scrub, or injected device failure The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
successful command completion and fstests cleanup checks are the primary signal Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/101 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/102 -->
# sources/test-tools/xfstests/tests/btrfs/102

## Purpose
Regression test for an ENOSPC issue when attempting to write to a file in a filesystem without any data block groups allocated. The script is categorized by `_begin_fstest` as `auto`, `quick`, `metadata`, `enospc`, `balance`, and its main coverage is: Multi-device balance stress, including mutual exclusion with replace/delete operations and post-stress scrub/fsck validation. Metadata consistency, orphan items, delayed references, extent maps, checksums, trim boundaries, and filesystem check behavior.

## Important APIs, Types, and Functions
fstest tags: `auto`, `quick`, `metadata`, `enospc`, `balance` requirement gates: `_require_scratch`, `_require_fs_space`. The important external command surfaces are `_btrfs`/`$BTRFS_UTIL_PROG` where present for Btrfs control and standard shell/file utilities for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_mkfs >>$seqres.full 2>&1`; `_scratch_mount $(_btrfs_no_v1_cache_opt)`; `_scratch_cycle_mount`. The core workload then performs these representative operations: . It also uses background or repeated stress/control loops: `_scratch_mkfs >>$seqres.full 2>&1`.

## State and Persistence Behavior
Mutates a freshly formatted scratch filesystem and relies on command status plus fstests cleanup checks. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on scratch filesystem lifecycle helpers. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
multi-device operations can race with stress workers, mutually exclusive jobs, scrub, or injected device failure metadata replay, delayed references, orphan cleanup, extent-map merging, or raw-device reserved ranges can regress without obvious user-visible errors The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
prints `Silence is golden` when no explicit failure path is reached Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/102 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/103 -->
# sources/test-tools/xfstests/tests/btrfs/103

## Purpose
Regression test for file read corruption when using compressed extents that are shared by multiple consecutive ranges of the same file. The script is categorized by `_begin_fstest` as `auto`, `quick`, `clone`, `compress`, and its main coverage is: Btrfs extent cloning/reflink semantics, including inline extents, same-file clones, holes, compressed extents, page-cache coherency, and fsync/log replay persistence. Compressed extent behavior across read, restore, clone, send, defrag, remount, and property inheritance paths.

## Important APIs, Types, and Functions
local shell functions: `test_clone_and_read_compressed_extent` fstest tags: `auto`, `quick`, `clone`, `compress` requirement gates: `_require_scratch`, `_require_cloner`. The important external command surfaces are `_btrfs`/`$BTRFS_UTIL_PROG` where present for Btrfs control and `$XFS_IO_PROG -f -c "pwrite -S 0xaa 0K $((1 * $BLOCK_SIZE))" \`; `$CLONER_PROG -s $((1 * $BLOCK_SIZE)) -d $((4 * $BLOCK_SIZE)) \`; `$XFS_IO_PROG -f \`; `$CLONER_PROG -s $((3 * $BLOCK_SIZE)) -d 0 -l $((2 * $BLOCK_SIZE)) \`; `od -t x1 $SCRATCH_MNT/foo | _filter_od`; `od -t x1 $SCRATCH_MNT/bar | _filter_od`; plus 2 more source-matched operations for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_mkfs >>$seqres.full 2>&1`; `_scratch_mount $mount_opts`; `_scratch_cycle_mount`; `_scratch_unmount`. The core workload then performs these representative operations: `$XFS_IO_PROG -f -c "pwrite -S 0xaa 0K $((1 * $BLOCK_SIZE))" \`; `$CLONER_PROG -s $((1 * $BLOCK_SIZE)) -d $((4 * $BLOCK_SIZE)) \`; `$XFS_IO_PROG -f \`; `$CLONER_PROG -s $((3 * $BLOCK_SIZE)) -d 0 -l $((2 * $BLOCK_SIZE)) \`; `od -t x1 $SCRATCH_MNT/foo | _filter_od`; `od -t x1 $SCRATCH_MNT/bar | _filter_od`; plus 2 more source-matched operations. It also uses background or repeated stress/control loops: `_scratch_mkfs >>$seqres.full 2>&1`.

## State and Persistence Behavior
Mutates a freshly formatted scratch filesystem and relies on command status plus fstests cleanup checks. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on scratch filesystem lifecycle helpers, btrfs clone ioctl exerciser, xfs_io data-shaping commands. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
clone/reflink edge cases can corrupt inline extents, holes, compressed extents, page cache, or log replay metadata compressed extents with non-zero offsets or shared references can return stale, zeroed, or mis-cloned data The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
hex dumps expose exact byte-level clone or hole behavior Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/103 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/104 -->
# sources/test-tools/xfstests/tests/btrfs/104

## Purpose
Test btrfs quota group consistency operations during snapshot delete. Btrfs has had long standing issues with drop snapshot failing to properly account for quota groups. This test crafts several snapshot trees with shared and exclusive elements. One of the trees is removed and then quota group consistency is checked. The script is categorized by `_begin_fstest` as `auto`, `qgroup`, and its main coverage is: Quota group enablement, rescan, limits, accounting of shared/exclusive extents, and crash or deletion paths that can leave qgroup state inconsistent. Snapshot creation, readonly snapshot consistency, default subvolume behavior, and interactions between snapshot roots and live/orphaned metadata. Metadata consistency, orphan items, delayed references, extent maps, checksums, trim boundaries, and filesystem check behavior.

## Important APIs, Types, and Functions
fstest tags: `auto`, `qgroup` requirement gates: `_require_scratch`, `_require_btrfs_qgroup_report`. The important external command surfaces are `_btrfs subvolume snapshot $SCRATCH_MNT $SCRATCH_MNT/snap1`; `_btrfs subvolume snapshot $SCRATCH_MNT/snap1 $SCRATCH_MNT/snap2`; `_btrfs quota enable $SCRATCH_MNT`; `_btrfs subvolume delete $SCRATCH_MNT/snap1`; `_btrfs filesystem sync $SCRATCH_MNT` for Btrfs control and `$XFS_IO_PROG -f -c "pwrite 0 4095" $loc/file$i > /dev/null 2>&1`; `$XFS_IO_PROG -f -c "pwrite 0 128k" $loc/extentfile > /dev/null 2>&1` for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_mkfs "--nodesize 16384" >> $seqres.full 2>&1`; `_scratch_mount`; `_scratch_cycle_mount`. The core workload then performs these representative operations: `_btrfs subvolume snapshot $SCRATCH_MNT $SCRATCH_MNT/snap1`; `_btrfs subvolume snapshot $SCRATCH_MNT/snap1 $SCRATCH_MNT/snap2`; `_btrfs quota enable $SCRATCH_MNT`; `_btrfs subvolume delete $SCRATCH_MNT/snap1`; `_btrfs filesystem sync $SCRATCH_MNT`; `$XFS_IO_PROG -f -c "pwrite 0 4095" $loc/file$i > /dev/null 2>&1`; `$XFS_IO_PROG -f -c "pwrite 0 128k" $loc/extentfile > /dev/null 2>&1`. It also uses background or repeated stress/control loops: `for i in `seq -w 1 $n`; do`; `$XFS_IO_PROG -f -c "pwrite 0 4095" $loc/file$i > /dev/null 2>&1`; `$XFS_IO_PROG -f -c "pwrite 0 128k" $loc/extentfile > /dev/null 2>&1`; `_scratch_mkfs "--nodesize 16384" >> $seqres.full 2>&1`.

## State and Persistence Behavior
Creates snapshot roots and compares parent/child root state; forces transaction or file-log persistence with sync/fsync; mutates qgroup metadata and relies on final accounting checks. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on scratch filesystem lifecycle helpers, qgroup reporting support, btrfs-progs command wrappers, xfs_io data-shaping commands. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
qgroup accounting can leak reservations or miscount shared/exclusive extents after snapshots, rescans, deletes, or limits metadata replay, delayed references, orphan cleanup, extent-map merging, or raw-device reserved ranges can regress without obvious user-visible errors The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
explicit filesystem check must pass fstests qgroup reporting/checking validates quota consistency Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/104 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/105 -->
# sources/test-tools/xfstests/tests/btrfs/105

## Purpose
Test that an incremental send works after a file from the parent snapshot gets replaced in the send snapshot by another one at the same exact location, with the same name and with the same inode number. The script is categorized by `_begin_fstest` as `auto`, `quick`, `send`, and its main coverage is: Btrfs send/receive stream generation, including full sends, incremental parent sends, clone-source roots, received UUID handling, and replay on a freshly formatted scratch filesystem. Device replacement or deletion against RAID-style scratch device pools, including device-mapper error injection and filesystem show verification. Snapshot creation, readonly snapshot consistency, default subvolume behavior, and interactions between snapshot roots and live/orphaned metadata. Subvolume creation, mounting, deletion, set-default behavior, and placeholder directory semantics.

## Important APIs, Types, and Functions
local shell functions: `_cleanup` fstest tags: `auto`, `quick`, `send` requirement gates: `_require_scratch`. The important external command surfaces are `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/mysnap1`; `_btrfs subvolume snapshot $SCRATCH_MNT $SCRATCH_MNT/mysnap2`; `_btrfs subvolume snapshot -r $SCRATCH_MNT/mysnap2 \`; `_btrfs send -f $send_files_dir/1.snap $SCRATCH_MNT/mysnap1`; `_btrfs send -p $SCRATCH_MNT/mysnap1 -f $send_files_dir/2.snap \`; `_btrfs receive -f $send_files_dir/1.snap $SCRATCH_MNT`; plus 1 more source-matched operations for Btrfs control and `$XFS_IO_PROG -f -c "pwrite -S 0xaa 0 64K" $SCRATCH_MNT/foo/bar | _filter_xfs_io`; `md5sum $SCRATCH_MNT/mysnap1/foo/bar | _filter_scratch`; `$XFS_IO_PROG -f -c "pwrite -S 0xbb 0 96K" \`; `md5sum $SCRATCH_MNT/mysnap2_ro/foo/bar | _filter_scratch`; plus 1 more source-matched operations for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_mkfs >>$seqres.full 2>&1`; `_scratch_mount`; `_scratch_unmount`; plus 2 more source-matched operations. The core workload then performs these representative operations: `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/mysnap1`; `_btrfs subvolume snapshot $SCRATCH_MNT $SCRATCH_MNT/mysnap2`; `_btrfs subvolume snapshot -r $SCRATCH_MNT/mysnap2 \`; `_btrfs send -f $send_files_dir/1.snap $SCRATCH_MNT/mysnap1`; `_btrfs send -p $SCRATCH_MNT/mysnap1 -f $send_files_dir/2.snap \`; `_btrfs receive -f $send_files_dir/1.snap $SCRATCH_MNT`; `_btrfs receive -f $send_files_dir/2.snap $SCRATCH_MNT`; `$XFS_IO_PROG -f -c "pwrite -S 0xaa 0 64K" $SCRATCH_MNT/foo/bar | _filter_xfs_io`; `md5sum $SCRATCH_MNT/mysnap1/foo/bar | _filter_scratch`; `$XFS_IO_PROG -f -c "pwrite -S 0xbb 0 96K" \`; plus 2 more source-matched operations. It also uses background or repeated stress/control loops: `_scratch_mkfs >>$seqres.full 2>&1`; plus 1 more source-matched operations.

## State and Persistence Behavior
Creates snapshot roots and compares parent/child root state; persists send streams to temporary files and replays them on a reformatted scratch filesystem; uses digest checks as durable content signals. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on scratch filesystem lifecycle helpers, btrfs-progs command wrappers, xfs_io data-shaping commands. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
send path ordering can emit invalid rename, rmdir, clone, or path records if inode identity, generation, or delayed-move state is mishandled multi-device operations can race with stress workers, mutually exclusive jobs, scrub, or injected device failure The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
digest output before and after remount/receive must match expected content Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/105 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/106 -->
# sources/test-tools/xfstests/tests/btrfs/106

## Purpose
Regression test for file read corruption when using compressed extents that represent file ranges with a length that is a multiple of 16 pages and that are shared by multiple consecutive ranges of the same file. The script is categorized by `_begin_fstest` as `auto`, `quick`, `clone`, `compress`, and its main coverage is: Btrfs extent cloning/reflink semantics, including inline extents, same-file clones, holes, compressed extents, page-cache coherency, and fsync/log replay persistence. Compressed extent behavior across read, restore, clone, send, defrag, remount, and property inheritance paths. Mount option transitions, especially flushoncommit, thread_pool resizing, and compression remount changes.

## Important APIs, Types, and Functions
local shell functions: `test_clone_and_read_compressed_extent` fstest tags: `auto`, `quick`, `clone`, `compress` requirement gates: `_require_scratch`, `_require_cloner`. The important external command surfaces are `_btrfs`/`$BTRFS_UTIL_PROG` where present for Btrfs control and `$XFS_IO_PROG -f -c "pwrite -S 0xaa 0K $((16 * $PAGE_SIZE))" \`; `$CLONER_PROG -s 0 -d $((16 * $PAGE_SIZE)) -l $((16 * $PAGE_SIZE)) \` for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_mkfs >>$seqres.full 2>&1`; `_scratch_mount $mount_opts`; `_scratch_cycle_mount`; `_scratch_unmount`. The core workload then performs these representative operations: `$XFS_IO_PROG -f -c "pwrite -S 0xaa 0K $((16 * $PAGE_SIZE))" \`; `$CLONER_PROG -s 0 -d $((16 * $PAGE_SIZE)) -l $((16 * $PAGE_SIZE)) \`. It also uses background or repeated stress/control loops: `_scratch_mkfs >>$seqres.full 2>&1`.

## State and Persistence Behavior
Uses digest checks as durable content signals. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on scratch filesystem lifecycle helpers, btrfs clone ioctl exerciser, xfs_io data-shaping commands. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
clone/reflink edge cases can corrupt inline extents, holes, compressed extents, page cache, or log replay metadata compressed extents with non-zero offsets or shared references can return stale, zeroed, or mis-cloned data The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
digest output before and after remount/receive must match expected content Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/106 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/107 -->
# sources/test-tools/xfstests/tests/btrfs/107

## Purpose
Test that calling fallocate against a range which is already allocated does not truncate beyond EOF The script is categorized by `_begin_fstest` as `auto`, `quick`, `prealloc`, and its main coverage is: Preallocated extent handling, fallocate/fpunch behavior, and distinguishing real data from holes during send or clone.

## Important APIs, Types, and Functions
fstest tags: `auto`, `quick`, `prealloc` requirement gates: `_require_scratch`, `_require_xfs_io_command`. The important external command surfaces are `_btrfs`/`$BTRFS_UTIL_PROG` where present for Btrfs control and `$XFS_IO_PROG -f -c "pwrite 0 $filesize" $SCRATCH_MNT/foo | _filter_xfs_io`; `$XFS_IO_PROG -f -c "falloc 0 $fallocrange" $SCRATCH_MNT/foo` for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_mkfs > /dev/null 2>&1`; `_scratch_mount`. The core workload then performs these representative operations: `$XFS_IO_PROG -f -c "pwrite 0 $filesize" $SCRATCH_MNT/foo | _filter_xfs_io`; `$XFS_IO_PROG -f -c "falloc 0 $fallocrange" $SCRATCH_MNT/foo`. It also uses background or repeated stress/control loops: `_scratch_mkfs > /dev/null 2>&1`.

## State and Persistence Behavior
Forces transaction or file-log persistence with sync/fsync. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on scratch filesystem lifecycle helpers, xfs_io subcommand availability, xfs_io data-shaping commands. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
the test is sensitive to kernel, btrfs-progs, and fstests helper behavior because it verifies a narrow historical regression The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
successful command completion and fstests cleanup checks are the primary signal Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/107 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/108 -->
# sources/test-tools/xfstests/tests/btrfs/108

## Purpose
Test that a send operation works correctly with reflinked files (cloned extents which multiple files point to). The script is categorized by `_begin_fstest` as `auto`, `quick`, `send`, `clone`, `punch`, and its main coverage is: Btrfs send/receive stream generation, including full sends, incremental parent sends, clone-source roots, received UUID handling, and replay on a freshly formatted scratch filesystem. Btrfs extent cloning/reflink semantics, including inline extents, same-file clones, holes, compressed extents, page-cache coherency, and fsync/log replay persistence. Snapshot creation, readonly snapshot consistency, default subvolume behavior, and interactions between snapshot roots and live/orphaned metadata. Subvolume creation, mounting, deletion, set-default behavior, and placeholder directory semantics.

## Important APIs, Types, and Functions
local shell functions: `_cleanup` fstest tags: `auto`, `quick`, `send`, `clone`, `punch` requirement gates: `_require_scratch`, `_require_cp_reflink`, `_require_xfs_io_command`. The important external command surfaces are `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/snap`; `_btrfs send -f $send_files_dir/1.snap $SCRATCH_MNT/snap`; `_btrfs receive -f $send_files_dir/1.snap $SCRATCH_MNT` for Btrfs control and `$XFS_IO_PROG -f -c "pwrite -S 0xaa 0K 100K" $SCRATCH_MNT/foo | _filter_xfs_io`; `cp --reflink=always $SCRATCH_MNT/foo $SCRATCH_MNT/bar`; `$XFS_IO_PROG -c "pwrite -S 0xbb 50K 10K" \`; `md5sum $SCRATCH_MNT/snap/foo | _filter_scratch`; `md5sum $SCRATCH_MNT/snap/bar | _filter_scratch`; plus 2 more source-matched operations for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_mkfs >>$seqres.full 2>&1`; `_scratch_mount`; `_scratch_unmount`; plus 2 more source-matched operations. The core workload then performs these representative operations: `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/snap`; `_btrfs send -f $send_files_dir/1.snap $SCRATCH_MNT/snap`; `_btrfs receive -f $send_files_dir/1.snap $SCRATCH_MNT`; `$XFS_IO_PROG -f -c "pwrite -S 0xaa 0K 100K" $SCRATCH_MNT/foo | _filter_xfs_io`; `cp --reflink=always $SCRATCH_MNT/foo $SCRATCH_MNT/bar`; `$XFS_IO_PROG -c "pwrite -S 0xbb 50K 10K" \`; `md5sum $SCRATCH_MNT/snap/foo | _filter_scratch`; `md5sum $SCRATCH_MNT/snap/bar | _filter_scratch`; plus 2 more source-matched operations. It also uses background or repeated stress/control loops: `_scratch_mkfs >>$seqres.full 2>&1`; plus 1 more source-matched operations.

## State and Persistence Behavior
Creates snapshot roots and compares parent/child root state; persists send streams to temporary files and replays them on a reformatted scratch filesystem; uses digest checks as durable content signals. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on scratch filesystem lifecycle helpers, cp --reflink support, xfs_io subcommand availability, btrfs-progs command wrappers, xfs_io data-shaping commands. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
send path ordering can emit invalid rename, rmdir, clone, or path records if inode identity, generation, or delayed-move state is mishandled clone/reflink edge cases can corrupt inline extents, holes, compressed extents, page cache, or log replay metadata The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
digest output before and after remount/receive must match expected content Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/108 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/109 -->
# sources/test-tools/xfstests/tests/btrfs/109

## Purpose
Test that a send operation works correctly with reflinked files (cloned extents which multiple files point to) that have compressed extents. The script is categorized by `_begin_fstest` as `auto`, `quick`, `send`, `clone`, `compress`, and its main coverage is: Btrfs send/receive stream generation, including full sends, incremental parent sends, clone-source roots, received UUID handling, and replay on a freshly formatted scratch filesystem. Btrfs extent cloning/reflink semantics, including inline extents, same-file clones, holes, compressed extents, page-cache coherency, and fsync/log replay persistence. Compressed extent behavior across read, restore, clone, send, defrag, remount, and property inheritance paths. Snapshot creation, readonly snapshot consistency, default subvolume behavior, and interactions between snapshot roots and live/orphaned metadata.

## Important APIs, Types, and Functions
local shell functions: `_cleanup` fstest tags: `auto`, `quick`, `send`, `clone`, `compress` requirement gates: `_require_scratch`, `_require_cp_reflink`. The important external command surfaces are `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/snap`; `_btrfs send -f $send_files_dir/1.snap $SCRATCH_MNT/snap`; `_btrfs receive -f $send_files_dir/1.snap $SCRATCH_MNT` for Btrfs control and `$XFS_IO_PROG -f -c "pwrite -S 0xaa 0K 100K" \`; `$XFS_IO_PROG -c "pwrite -S 0xbb 0K 40K" \`; `cp --reflink=always $SCRATCH_MNT/foo $SCRATCH_MNT/bar`; `md5sum $SCRATCH_MNT/snap/foo | _filter_scratch`; `md5sum $SCRATCH_MNT/snap/bar | _filter_scratch`; plus 2 more source-matched operations for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_mkfs >>$seqres.full 2>&1`; `_scratch_mount "-o compress"`; `_scratch_unmount`; plus 2 more source-matched operations. The core workload then performs these representative operations: `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/snap`; `_btrfs send -f $send_files_dir/1.snap $SCRATCH_MNT/snap`; `_btrfs receive -f $send_files_dir/1.snap $SCRATCH_MNT`; `$XFS_IO_PROG -f -c "pwrite -S 0xaa 0K 100K" \`; `$XFS_IO_PROG -c "pwrite -S 0xbb 0K 40K" \`; `cp --reflink=always $SCRATCH_MNT/foo $SCRATCH_MNT/bar`; `md5sum $SCRATCH_MNT/snap/foo | _filter_scratch`; `md5sum $SCRATCH_MNT/snap/bar | _filter_scratch`; plus 2 more source-matched operations. It also uses background or repeated stress/control loops: `_scratch_mkfs >>$seqres.full 2>&1`; plus 1 more source-matched operations.

## State and Persistence Behavior
Creates snapshot roots and compares parent/child root state; persists send streams to temporary files and replays them on a reformatted scratch filesystem; uses digest checks as durable content signals; forces transaction or file-log persistence with sync/fsync. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on scratch filesystem lifecycle helpers, cp --reflink support, btrfs-progs command wrappers, xfs_io data-shaping commands. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
send path ordering can emit invalid rename, rmdir, clone, or path records if inode identity, generation, or delayed-move state is mishandled clone/reflink edge cases can corrupt inline extents, holes, compressed extents, page cache, or log replay metadata compressed extents with non-zero offsets or shared references can return stale, zeroed, or mis-cloned data metadata replay, delayed references, orphan cleanup, extent-map merging, or raw-device reserved ranges can regress without obvious user-visible errors The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
digest output before and after remount/receive must match expected content Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/109 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/110 -->
# sources/test-tools/xfstests/tests/btrfs/110

## Purpose
Test that sending and receiving snapshots across different filesystems works for full and incremental send operations. The script is categorized by `_begin_fstest` as `auto`, `quick`, `send`, and its main coverage is: Btrfs send/receive stream generation, including full sends, incremental parent sends, clone-source roots, received UUID handling, and replay on a freshly formatted scratch filesystem. Snapshot creation, readonly snapshot consistency, default subvolume behavior, and interactions between snapshot roots and live/orphaned metadata. Subvolume creation, mounting, deletion, set-default behavior, and placeholder directory semantics.

## Important APIs, Types, and Functions
local shell functions: `_cleanup` fstest tags: `auto`, `quick`, `send` requirement gates: `_require_scratch`. The important external command surfaces are `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/snap1`; `_btrfs send -f $send_files_dir/1.snap $SCRATCH_MNT/snap1`; `_btrfs receive -f $send_files_dir/1.snap $SCRATCH_MNT`; `_btrfs subvolume snapshot $SCRATCH_MNT/snap1 $SCRATCH_MNT/snap2_rw`; `_btrfs subvolume snapshot -r $SCRATCH_MNT/snap2_rw \`; `_btrfs send -p $SCRATCH_MNT/snap1 -f $send_files_dir/2.snap \`; plus 2 more source-matched operations for Btrfs control and `$XFS_IO_PROG -f -c "pwrite -S 0xaa 0K 32K" $SCRATCH_MNT/foo | _filter_xfs_io`; `md5sum $SCRATCH_MNT/snap1/foo | _filter_scratch`; `$XFS_IO_PROG -c "pwrite -S 0xbb 4K 4K" \`; `md5sum $SCRATCH_MNT/snap2/foo | _filter_scratch`; plus 3 more source-matched operations for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_mkfs >>$seqres.full 2>&1`; `_scratch_mount`; `_scratch_unmount`; plus 5 more source-matched operations. The core workload then performs these representative operations: `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/snap1`; `_btrfs send -f $send_files_dir/1.snap $SCRATCH_MNT/snap1`; `_btrfs receive -f $send_files_dir/1.snap $SCRATCH_MNT`; `_btrfs subvolume snapshot $SCRATCH_MNT/snap1 $SCRATCH_MNT/snap2_rw`; `_btrfs subvolume snapshot -r $SCRATCH_MNT/snap2_rw \`; `_btrfs send -p $SCRATCH_MNT/snap1 -f $send_files_dir/2.snap \`; `_btrfs receive -f $send_files_dir/2.snap $SCRATCH_MNT`; `$XFS_IO_PROG -f -c "pwrite -S 0xaa 0K 32K" $SCRATCH_MNT/foo | _filter_xfs_io`; `md5sum $SCRATCH_MNT/snap1/foo | _filter_scratch`; `$XFS_IO_PROG -c "pwrite -S 0xbb 4K 4K" \`; plus 5 more source-matched operations. It also uses background or repeated stress/control loops: `_scratch_mkfs >>$seqres.full 2>&1`; plus 2 more source-matched operations.

## State and Persistence Behavior
Creates snapshot roots and compares parent/child root state; persists send streams to temporary files and replays them on a reformatted scratch filesystem; uses digest checks as durable content signals. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on scratch filesystem lifecycle helpers, btrfs-progs command wrappers, xfs_io data-shaping commands. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
send path ordering can emit invalid rename, rmdir, clone, or path records if inode identity, generation, or delayed-move state is mishandled The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
digest output before and after remount/receive must match expected content Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/110 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/111 -->
# sources/test-tools/xfstests/tests/btrfs/111

## Purpose
Test that resending snapshots from a different filesystem is possible for both full and incremental send operations. The script is categorized by `_begin_fstest` as `auto`, `quick`, `send`, and its main coverage is: Btrfs send/receive stream generation, including full sends, incremental parent sends, clone-source roots, received UUID handling, and replay on a freshly formatted scratch filesystem. Snapshot creation, readonly snapshot consistency, default subvolume behavior, and interactions between snapshot roots and live/orphaned metadata. Subvolume creation, mounting, deletion, set-default behavior, and placeholder directory semantics.

## Important APIs, Types, and Functions
local shell functions: `_cleanup` fstest tags: `auto`, `quick`, `send` requirement gates: `_require_scratch`. The important external command surfaces are `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/snap1`; `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/snap2`; `_btrfs send -f $send_files_dir/1.snap $SCRATCH_MNT/snap1`; `_btrfs send -p $SCRATCH_MNT/snap1 -f $send_files_dir/2.snap \`; `_btrfs receive -vv -f $send_files_dir/1.snap $SCRATCH_MNT`; `_btrfs receive -vv -f $send_files_dir/2.snap $SCRATCH_MNT`; plus 4 more source-matched operations for Btrfs control and `$XFS_IO_PROG -f -c "pwrite -S 0xaa 0K 32K" $SCRATCH_MNT/foo | _filter_xfs_io`; `$XFS_IO_PROG -c "pwrite -S 0xbb 4K 4K" $SCRATCH_MNT/foo | _filter_xfs_io`; `md5sum $SCRATCH_MNT/snap1/foo | _filter_scratch`; `md5sum $SCRATCH_MNT/snap2/foo | _filter_scratch`; plus 4 more source-matched operations for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_mkfs >>$seqres.full 2>&1`; `_scratch_mount`; `_scratch_unmount`; plus 5 more source-matched operations. The core workload then performs these representative operations: `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/snap1`; `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/snap2`; `_btrfs send -f $send_files_dir/1.snap $SCRATCH_MNT/snap1`; `_btrfs send -p $SCRATCH_MNT/snap1 -f $send_files_dir/2.snap \`; `_btrfs receive -vv -f $send_files_dir/1.snap $SCRATCH_MNT`; `_btrfs receive -vv -f $send_files_dir/2.snap $SCRATCH_MNT`; `_btrfs send -f $send_files_dir/1_2.snap $SCRATCH_MNT/snap1`; `_btrfs send -p $SCRATCH_MNT/snap1 -f $send_files_dir/2_2.snap \`; `_btrfs receive -vv -f $send_files_dir/1_2.snap $SCRATCH_MNT`; `_btrfs receive -vv -f $send_files_dir/2_2.snap $SCRATCH_MNT`; plus 8 more source-matched operations. It also uses background or repeated stress/control loops: `_scratch_mkfs >>$seqres.full 2>&1`; plus 2 more source-matched operations.

## State and Persistence Behavior
Creates snapshot roots and compares parent/child root state; persists send streams to temporary files and replays them on a reformatted scratch filesystem; uses digest checks as durable content signals; forces transaction or file-log persistence with sync/fsync. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on scratch filesystem lifecycle helpers, btrfs-progs command wrappers, xfs_io data-shaping commands. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
send path ordering can emit invalid rename, rmdir, clone, or path records if inode identity, generation, or delayed-move state is mishandled The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
digest output before and after remount/receive must match expected content Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/111 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/112 -->
# sources/test-tools/xfstests/tests/btrfs/112

## Purpose
Test several cases of cloning inline extents that used to lead to file corruption or data loss. The script is categorized by `_begin_fstest` as `auto`, `quick`, `clone`, `prealloc`, `compress`, and its main coverage is: Btrfs extent cloning/reflink semantics, including inline extents, same-file clones, holes, compressed extents, page-cache coherency, and fsync/log replay persistence. Compressed extent behavior across read, restore, clone, send, defrag, remount, and property inheritance paths. Preallocated extent handling, fallocate/fpunch behavior, and distinguishing real data from holes during send or clone. I/O error injection through device-mapper targets to validate degraded multi-device behavior.

## Important APIs, Types, and Functions
local shell functions: `test_cloning_inline_extents` fstest tags: `auto`, `quick`, `clone`, `prealloc`, `compress` requirement gates: `_require_scratch`, `_require_cloner`, `_require_btrfs_fs_feature`, `_require_btrfs_mkfs_feature`, `_require_xfs_io_command`. The important external command surfaces are `_btrfs`/`$BTRFS_UTIL_PROG` where present for Btrfs control and `$XFS_IO_PROG -f -c "pwrite -S 0xbb 0 50" $SCRATCH_MNT/bar \`; `$XFS_IO_PROG -f -c "pwrite -S 0xaa 0K 16K" $SCRATCH_MNT/foo \`; `$CLONER_PROG -s 0 -d 0 -l 0 $SCRATCH_MNT/bar $SCRATCH_MNT/foo \`; `od -t x1 $SCRATCH_MNT/foo`; `$XFS_IO_PROG -c "pwrite -S 0xcc 0 100" $SCRATCH_MNT/foo | _filter_xfs_io`; `$XFS_IO_PROG -f -c "pwrite -S 0xdd 4K 12K" $SCRATCH_MNT/foo2 \`; plus 16 more source-matched operations for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_mkfs $mkfs_opts >>$seqres.full 2>&1`; `_scratch_mount $mount_opts`; `_scratch_unmount`. The core workload then performs these representative operations: `$XFS_IO_PROG -f -c "pwrite -S 0xbb 0 50" $SCRATCH_MNT/bar \`; `$XFS_IO_PROG -f -c "pwrite -S 0xaa 0K 16K" $SCRATCH_MNT/foo \`; `$CLONER_PROG -s 0 -d 0 -l 0 $SCRATCH_MNT/bar $SCRATCH_MNT/foo \`; `od -t x1 $SCRATCH_MNT/foo`; `$XFS_IO_PROG -c "pwrite -S 0xcc 0 100" $SCRATCH_MNT/foo | _filter_xfs_io`; `$XFS_IO_PROG -f -c "pwrite -S 0xdd 4K 12K" $SCRATCH_MNT/foo2 \`; `$CLONER_PROG -s 0 -d 0 -l 0 $SCRATCH_MNT/bar $SCRATCH_MNT/foo2 \`; `od -t x1 $SCRATCH_MNT/foo2`; `$XFS_IO_PROG -c "pwrite -S 0xee 0 90" $SCRATCH_MNT/foo2 | _filter_xfs_io`; `$XFS_IO_PROG -f -c "pwrite -S 0x01 0 40" $SCRATCH_MNT/foo4 \`; plus 12 more source-matched operations. It also uses background or repeated stress/control loops: `_scratch_mkfs $mkfs_opts >>$seqres.full 2>&1`.

## State and Persistence Behavior
Mutates a freshly formatted scratch filesystem and relies on command status plus fstests cleanup checks. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on scratch filesystem lifecycle helpers, btrfs clone ioctl exerciser, xfs_io subcommand availability, xfs_io data-shaping commands, Btrfs-specific output filters. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
clone/reflink edge cases can corrupt inline extents, holes, compressed extents, page cache, or log replay metadata compressed extents with non-zero offsets or shared references can return stale, zeroed, or mis-cloned data The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
hex dumps expose exact byte-level clone or hole behavior Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/112 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/113 -->
# sources/test-tools/xfstests/tests/btrfs/113

## Purpose
Test that truncating a file that consists of a compressed and inlined extent to a smaller size and then cloning it into another file is not possible and does not result in leaking stale data (data past the truncation offset) nor losing data in the clone operation's destination file. The script is categorized by `_begin_fstest` as `auto`, `quick`, `compress`, `clone`, and its main coverage is: Btrfs extent cloning/reflink semantics, including inline extents, same-file clones, holes, compressed extents, page-cache coherency, and fsync/log replay persistence. Compressed extent behavior across read, restore, clone, send, defrag, remount, and property inheritance paths. Metadata consistency, orphan items, delayed references, extent maps, checksums, trim boundaries, and filesystem check behavior.

## Important APIs, Types, and Functions
fstest tags: `auto`, `quick`, `compress`, `clone` requirement gates: `_require_scratch`, `_require_cloner`. The important external command surfaces are `_btrfs`/`$BTRFS_UTIL_PROG` where present for Btrfs control and `$XFS_IO_PROG -f -c "pwrite -S 0xa1 0 128" \`; `$XFS_IO_PROG -f -c "pwrite -S 0xbb 0 256" $SCRATCH_MNT/bar | _filter_xfs_io`; `$XFS_IO_PROG -c "truncate 128" $SCRATCH_MNT/foo`; `$CLONER_PROG -s 0 -d 0 -l 0 $SCRATCH_MNT/foo $SCRATCH_MNT/bar \`; `od -t x1 $SCRATCH_MNT/bar` for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_mkfs >>$seqres.full 2>&1`; `_scratch_mount "-o compress"`. The core workload then performs these representative operations: `$XFS_IO_PROG -f -c "pwrite -S 0xa1 0 128" \`; `$XFS_IO_PROG -f -c "pwrite -S 0xbb 0 256" $SCRATCH_MNT/bar | _filter_xfs_io`; `$XFS_IO_PROG -c "truncate 128" $SCRATCH_MNT/foo`; `$CLONER_PROG -s 0 -d 0 -l 0 $SCRATCH_MNT/foo $SCRATCH_MNT/bar \`; `od -t x1 $SCRATCH_MNT/bar`. It also uses background or repeated stress/control loops: `_scratch_mkfs >>$seqres.full 2>&1`.

## State and Persistence Behavior
Forces transaction or file-log persistence with sync/fsync. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on scratch filesystem lifecycle helpers, btrfs clone ioctl exerciser, xfs_io data-shaping commands, Btrfs-specific output filters. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
clone/reflink edge cases can corrupt inline extents, holes, compressed extents, page cache, or log replay metadata compressed extents with non-zero offsets or shared references can return stale, zeroed, or mis-cloned data metadata replay, delayed references, orphan cleanup, extent-map merging, or raw-device reserved ranges can regress without obvious user-visible errors The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
hex dumps expose exact byte-level clone or hole behavior Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/113 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/114 -->
# sources/test-tools/xfstests/tests/btrfs/114

## Purpose
btrfs quota scan/unmount sanity test Make sure that unmounting during a quota rescan doesn't crash The script is categorized by `_begin_fstest` as `auto`, `qgroup`, and its main coverage is: Quota group enablement, rescan, limits, accounting of shared/exclusive extents, and crash or deletion paths that can leave qgroup state inconsistent.

## Important APIs, Types, and Functions
fstest tags: `auto`, `qgroup` requirement gates: `_require_scratch`. The important external command surfaces are `$BTRFS_UTIL_PROG quota enable $SCRATCH_MNT` for Btrfs control and standard shell/file utilities for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_mkfs >>$seqres.full 2>&1`; `_scratch_mount`; `_scratch_unmount`. The core workload then performs these representative operations: `$BTRFS_UTIL_PROG quota enable $SCRATCH_MNT`. It also uses background or repeated stress/control loops: `_scratch_mkfs >>$seqres.full 2>&1`; `for i in `seq 0 1 450000`; do`.

## State and Persistence Behavior
Mutates qgroup metadata and relies on final accounting checks. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on scratch filesystem lifecycle helpers, btrfs-progs command wrappers. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
qgroup accounting can leak reservations or miscount shared/exclusive extents after snapshots, rescans, deletes, or limits The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
prints `Silence is golden` when no explicit failure path is reached fstests qgroup reporting/checking validates quota consistency Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/114 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/115 -->
# sources/test-tools/xfstests/tests/btrfs/115

## Purpose
btrfs quota scan/disable sanity test Make sure that disabling quotas during a quota rescan doesn't crash The script is categorized by `_begin_fstest` as `auto`, `qgroup`, and its main coverage is: Quota group enablement, rescan, limits, accounting of shared/exclusive extents, and crash or deletion paths that can leave qgroup state inconsistent.

## Important APIs, Types, and Functions
fstest tags: `auto`, `qgroup` requirement gates: `_require_scratch`. The important external command surfaces are `$BTRFS_UTIL_PROG quota enable $SCRATCH_MNT`; `$BTRFS_UTIL_PROG quota disable $SCRATCH_MNT` for Btrfs control and standard shell/file utilities for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_mkfs >>$seqres.full 2>&1`; `_scratch_mount`. The core workload then performs these representative operations: `$BTRFS_UTIL_PROG quota enable $SCRATCH_MNT`; `$BTRFS_UTIL_PROG quota disable $SCRATCH_MNT`. It also uses background or repeated stress/control loops: `_scratch_mkfs >>$seqres.full 2>&1`; `for i in `seq 0 1 450000`; do`.

## State and Persistence Behavior
Mutates qgroup metadata and relies on final accounting checks. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on scratch filesystem lifecycle helpers, btrfs-progs command wrappers. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
qgroup accounting can leak reservations or miscount shared/exclusive extents after snapshots, rescans, deletes, or limits The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
prints `Silence is golden` when no explicit failure path is reached fstests qgroup reporting/checking validates quota consistency Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/115 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/116 -->
# sources/test-tools/xfstests/tests/btrfs/116

## Purpose
Verify that when a fitrim operation is made against a btrfs filesystem, the ranges [0, 64Kb[ and [68Kb, 1Mb[ of the device are not discarded, they remain with the content they had before the fitrim operation. These regions of the device are reserved for a boot loader to use at its will. The script is categorized by `_begin_fstest` as `auto`, `quick`, `metadata`, and its main coverage is: Metadata consistency, orphan items, delayed references, extent maps, checksums, trim boundaries, and filesystem check behavior.

## Important APIs, Types, and Functions
fstest tags: `auto`, `quick`, `metadata` requirement gates: `_require_scratch`, `_require_non_zoned_device`, `_require_batched_discard`. The important external command surfaces are `_btrfs`/`$BTRFS_UTIL_PROG` where present for Btrfs control and `$XFS_IO_PROG -c "pwrite -S 0xfd 0 64K" $SCRATCH_DEV | _filter_xfs_io`; `$XFS_IO_PROG -c "pwrite -S 0xfd 68K 956K" $SCRATCH_DEV | _filter_xfs_io`; `$FSTRIM_PROG $SCRATCH_MNT`; `od -t x1 -N $((64 * 1024)) $SCRATCH_DEV`; `od -t x1 -j $((68 * 1024)) -N $((956 * 1024)) $SCRATCH_DEV` for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_mkfs >>$seqres.full 2>&1`; `_scratch_mount`; `_scratch_unmount`. The core workload then performs these representative operations: `$XFS_IO_PROG -c "pwrite -S 0xfd 0 64K" $SCRATCH_DEV | _filter_xfs_io`; `$XFS_IO_PROG -c "pwrite -S 0xfd 68K 956K" $SCRATCH_DEV | _filter_xfs_io`; `$FSTRIM_PROG $SCRATCH_MNT`; `od -t x1 -N $((64 * 1024)) $SCRATCH_DEV`; `od -t x1 -j $((68 * 1024)) -N $((956 * 1024)) $SCRATCH_DEV`. It also uses background or repeated stress/control loops: `_scratch_mkfs >>$seqres.full 2>&1`.

## State and Persistence Behavior
Verifies discard persistence at raw device offsets. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on scratch filesystem lifecycle helpers, non-zoned device semantics, xfs_io data-shaping commands. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
metadata replay, delayed references, orphan cleanup, extent-map merging, or raw-device reserved ranges can regress without obvious user-visible errors The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
hex dumps expose exact byte-level clone or hole behavior Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/116 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/117 -->
# sources/test-tools/xfstests/tests/btrfs/117

## Purpose
Test that an incremental send operation which issues clone operations works for files that have a full path containing more than one parent directory component. The script is categorized by `_begin_fstest` as `auto`, `quick`, `send`, `clone`, and its main coverage is: Btrfs send/receive stream generation, including full sends, incremental parent sends, clone-source roots, received UUID handling, and replay on a freshly formatted scratch filesystem. Btrfs extent cloning/reflink semantics, including inline extents, same-file clones, holes, compressed extents, page-cache coherency, and fsync/log replay persistence. Snapshot creation, readonly snapshot consistency, default subvolume behavior, and interactions between snapshot roots and live/orphaned metadata. Subvolume creation, mounting, deletion, set-default behavior, and placeholder directory semantics.

## Important APIs, Types, and Functions
fstest tags: `auto`, `quick`, `send`, `clone` requirement gates: `_require_scratch`, `_require_cp_reflink`. The important external command surfaces are `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/snap1`; `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/clones_snap`; `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/snap2`; `_btrfs send -f $tmp/1.snap $SCRATCH_MNT/snap1`; `_btrfs send -f $tmp/clones.snap $SCRATCH_MNT/clones_snap`; `_btrfs send -p $SCRATCH_MNT/snap1 \`; plus 3 more source-matched operations for Btrfs control and `$XFS_IO_PROG -f -c "pwrite -S 0xfd 0 128K" $SCRATCH_MNT/a/b/c/x | _filter_xfs_io`; `cp --reflink=always $SCRATCH_MNT/a/b/c/x $SCRATCH_MNT/a/b/c/y`; `$XFS_IO_PROG -c "pwrite -S 0xab 32K 16K" $SCRATCH_MNT/a/b/c/y | _filter_xfs_io`; `md5sum $SCRATCH_MNT/snap1/a/b/c/x | _filter_scratch`; `md5sum $SCRATCH_MNT/snap2/a/b/c/x | _filter_scratch`; `md5sum $SCRATCH_MNT/snap2/a/b/c/y | _filter_scratch`; plus 3 more source-matched operations for data shaping and verification. Shared xfstests globals include `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$seqres.full`, `$XFS_IO_PROG`, and `$BTRFS_UTIL_PROG`.

## Control Flow
The file sources `common/preamble`, declares the test with `_begin_fstest`, installs any local `_cleanup` hook, sources common filters/helpers, and enforces capability gates before touching the scratch filesystem. Scratch lifecycle and check operations are: `_scratch_mkfs >>$seqres.full 2>&1`; `_scratch_mount`; `_scratch_unmount`; plus 2 more source-matched operations. The core workload then performs these representative operations: `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/snap1`; `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/clones_snap`; `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/snap2`; `_btrfs send -f $tmp/1.snap $SCRATCH_MNT/snap1`; `_btrfs send -f $tmp/clones.snap $SCRATCH_MNT/clones_snap`; `_btrfs send -p $SCRATCH_MNT/snap1 \`; `_btrfs receive -f $tmp/1.snap $SCRATCH_MNT`; `_btrfs receive -f $tmp/clones.snap $SCRATCH_MNT`; `_btrfs receive -f $tmp/2.snap $SCRATCH_MNT`; `$XFS_IO_PROG -f -c "pwrite -S 0xfd 0 128K" $SCRATCH_MNT/a/b/c/x | _filter_xfs_io`; plus 8 more source-matched operations. It also uses background or repeated stress/control loops: `_scratch_mkfs >>$seqres.full 2>&1`; `for ((i = 1; i <= 1000; i++)); do`; plus 1 more source-matched operations.

## State and Persistence Behavior
Creates snapshot roots and compares parent/child root state; persists send streams to temporary files and replays them on a reformatted scratch filesystem; uses digest checks as durable content signals. Temporary send streams, fssum manifests, restore directories, or mounted subvolume directories are cleaned by the local cleanup hook when the script creates them. The test intentionally reformats/remounts/cycles scratch state when needed to distinguish in-memory success from on-disk persistence.

## Dependencies and Integration Points
The script depends on scratch filesystem lifecycle helpers, cp --reflink support, btrfs-progs command wrappers, xfs_io data-shaping commands. It integrates with fstests output filtering so expected output remains stable across devices, mount paths, and btrfs-progs formatting differences. Kernel integration points are the Btrfs ioctls and transaction paths exercised by the selected tags rather than reusable library code in this repository.

## Risks and Edge Cases
send path ordering can emit invalid rename, rmdir, clone, or path records if inode identity, generation, or delayed-move state is mishandled clone/reflink edge cases can corrupt inline extents, holes, compressed extents, page cache, or log replay metadata The test may also be sensitive to filesystem block size, nodesize, compression algorithm, mkfs feature defaults, device-pool geometry, or helper availability, depending on its requirement gates and mount options.

## Test Signals
digest output before and after remount/receive must match expected content Any mismatch, unexpected command failure, explicit `_fail`, missing orphan/qgroup/device state, or non-zero filesystem check is a regression signal for this source file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/117 -->
