# subset-b-009543 grouped research

Grouped research for xfstests btrfs, ceph, cifs, and ext4 files. Each section preserves the original source path and is delimited for deterministic reconciliation into source-tree-aligned per-file documents.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/301 -->
# sources/test-tools/xfstests/tests/btrfs/301

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/btrfs/301_research.md`.

Source read: 504 lines, SHA256 prefix `30ec1e3a79f98792`.

Purpose: FS QA Test 301 Test common btrfs simple quotas scenarios involving sharing extents and removing them in various orders..

Important APIs/types/functions: test tags `auto quick qgroup clone subvol prealloc snapshot remount`; common harness imports `. ./common/preamble`, `. ./common/reflink`; requirements/fixed gates `_require_scratch_reflink`, `_require_cp_reflink`, `_require_btrfs_command inspect-internal dump-tree`, `_require_xfs_io_command "falloc"`, `_require_scratch_enable_simple_quota`, `_require_no_compress`, `_fixed_by_kernel_commit 7b632596188e \`, `_fixed_by_kernel_commit de134cb54c3a \`, `_require_fio $fio_config`; helper functions `get_qgroup_usage()`, `get_subvol_usage()`, `count_subvol_owned_metadata()`, `check_qgroup_usage()`, `check_subvol_usage()`, `set_subvol_limit()`, `trigger_cleaner()`, `cycle_mount_check_subvol_usage()`, `do_write()`, `do_enospc_write()`, `do_falloc()`, `do_enospc_falloc()`, `enable_quota()`, `get_subvid()`, `get_snapid()`, `get_nestedid()`, `prepare()`, `prepare_snapshotted()`; key variables `subv=$SCRATCH_MNT/subv`, `nested=$SCRATCH_MNT/subv/nested`, `snap=$SCRATCH_MNT/snap`, `nr_fill=512`, `fill_sz=$((64 * 1024))`, `total_fill=$(($nr_fill * $fill_sz))`, `nodesize=$($BTRFS_UTIL_PROG inspect-internal dump-super $SCRATCH_DEV | \`, `blocksize=$($BTRFS_UTIL_PROG inspect-internal dump-super $SCRATCH_DEV |\`, `ext_sz=$((128 * 1024 * 1024))`, `limit_nr=8`.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `get_qgroup_usage()`, `get_subvol_usage()`, `count_subvol_owned_metadata()`, `check_qgroup_usage()`, `check_subvol_usage()`, `set_subvol_limit()`, `trigger_cleaner()`, `cycle_mount_check_subvol_usage()`, `do_write()`, `do_enospc_write()`, `do_falloc()`, `do_enospc_falloc()`, `enable_quota()`, `get_subvid()`, `get_snapid()`, `get_nestedid()`, `prepare()`, `prepare_snapshotted()`, `prepare_nested()`, `basic_accounting()`, `reservation_accounting()`, `snapshot_accounting()`, `delete_snapshot_src_ref()`, `delete_snapshot_ref()`. Representative operation sequence: L15: _require_scratch_reflink; L17: _require_btrfs_command inspect-internal dump-tree; L18: _require_xfs_io_command "falloc"; L19: _require_scratch_enable_simple_quota; L33: nodesize=$($BTRFS_UTIL_PROG inspect-internal dump-super $SCRATCH_DEV | \; L35: blocksize=$($BTRFS_UTIL_PROG inspect-internal dump-super $SCRATCH_DEV |\; L60: output=$($BTRFS_UTIL_PROG qgroup show --sync --raw $SCRATCH_MNT | \; L87: count=$($BTRFS_UTIL_PROG inspect-internal dump-tree $SCRATCH_DEV | \; L121: $BTRFS_UTIL_PROG qgroup limit $2 0/$1 $SCRATCH_MNT; L130: _scratch_remount commit=1; L134: cycle_mount_check_subvol_usage(); L136: _scratch_cycle_mount; L145: $XFS_IO_PROG -fc "pwrite -q 0 $sz" $file; L156: do_falloc(); L161: $XFS_IO_PROG -fc "falloc 0 $sz" $file; L164: do_enospc_falloc(); L169: do_falloc $file $sz; L179: $BTRFS_UTIL_PROG quota enable $arg $SCRATCH_MNT.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; creates or manipulates btrfs subvolumes; persists snapshot roots and verifies their contents; changes quota/qgroup accounting state.

Dependencies and integration points: Depends on xfstests common libraries, btrfs-progs and btrfs kernel feature gates, xfs_io workload commands. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: contains timing-sensitive waits; quota accounting regressions can be silent until unmount or rescan; is tied to specific kernel-regression behavior noted by fixed-by annotations.

Test signals: byte-for-byte compare of copied or restored data; btrfs on-disk tree inspection; visible subtest labels include 0; basic accounting; reservation accounting; snapshot accounting; delete src ref first; delete snapshot ref first.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/301 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/302 -->
# sources/test-tools/xfstests/tests/btrfs/302

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/btrfs/302_research.md`.

Source read: 59 lines, SHA256 prefix `23a5bb5b911f2670`.

Purpose: FS QA Test 302 Test that snapshotting a new subvolume (created in the current transaction) that has a btree with a height > 1, works and does not result in a filesystem corruption. This exercises a regression introduced in kernel 6.5 by the kernel commit: 1b53e51a4a8f ("btrfs: don't commit transaction for every subvol create").

Important APIs/types/functions: test tags `auto quick snapshot subvol`; common harness imports `. ./common/preamble`, `. ./common/filter`; requirements/fixed gates `_require_scratch`, `_require_fssum`, `_fixed_by_kernel_commit eb96e221937a \`; key variables `fssum_file="$SCRATCH_MNT/checksum.fssum"`.

Control flow: The script is mostly straight-line after harness setup. Representative operation sequence: L30: _scratch_mkfs -n 64K >> $seqres.full 2>&1 || _fail "mkfs failed"; L31: _scratch_mount; L33: $BTRFS_UTIL_PROG subvolume create $SCRATCH_MNT/subvol | _filter_scratch; L43: $FSSUM_PROG -A -f -w $fssum_file $SCRATCH_MNT/subvol; L47: _btrfs subvolume snapshot -r $SCRATCH_MNT/subvol $SCRATCH_MNT/subvol/snap; L51: _scratch_cycle_mount; L55: $FSSUM_PROG -r $fssum_file $SCRATCH_MNT/subvol/snap.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; creates or manipulates btrfs subvolumes; persists snapshot roots and verifies their contents.

Dependencies and integration points: Depends on xfstests common libraries, btrfs-progs and btrfs kernel feature gates. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: is tied to specific kernel-regression behavior noted by fixed-by annotations.

Test signals: successful script exit with xfstests filtered output.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/302 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/303 -->
# sources/test-tools/xfstests/tests/btrfs/303

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/btrfs/303_research.md`.

Source read: 91 lines, SHA256 prefix `b24af37f206076dd`.

Purpose: FS QA Test 303 Test that an incremental send does not issue unnecessary writes for a sparse file that got one new extent between its previous extent and the file's size..

Important APIs/types/functions: test tags `auto quick snapshot send fiemap`; common harness imports `. ./common/preamble`, `. ./common/filter`, `. ./common/punch # for _filter_fiemap`; requirements/fixed gates `_require_test`, `_require_scratch`, `_require_xfs_io_command "fiemap"`, `_fixed_by_kernel_commit 5897710b28ca \`; helper functions `_cleanup()`; key variables `send_files_dir=$TEST_DIR/btrfs-test-$seq`.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `_cleanup()`. Representative operation sequence: L11: _begin_fstest auto quick snapshot send fiemap; L21: . ./common/punch # for _filter_fiemap; L25: _require_xfs_io_command "fiemap"; L35: _scratch_mkfs >> $seqres.full 2>&1 || _fail "mkfs failed"; L36: _scratch_mount; L38: $XFS_IO_PROG -f -c "truncate 1G" $SCRATCH_MNT/foobar; L42: $BTRFS_UTIL_PROG subvolume snapshot -r $SCRATCH_MNT \; L46: $BTRFS_UTIL_PROG send -f $send_files_dir/1.snap \; L52: $XFS_IO_PROG -c "pwrite -S 0xab -b 64K 0 64K" \; L58: $BTRFS_UTIL_PROG subvolume snapshot -r $SCRATCH_MNT \; L62: $BTRFS_UTIL_PROG send -p $SCRATCH_MNT/mysnap1 -f $send_files_dir/2.snap \; L68: _scratch_unmount; L69: _scratch_mkfs >> $seqres.full 2>&1 || _fail "mkfs failed"; L70: _scratch_mount; L72: $BTRFS_UTIL_PROG receive -f $send_files_dir/1.snap $SCRATCH_MNT > /dev/null; L73: $BTRFS_UTIL_PROG receive -f $send_files_dir/2.snap $SCRATCH_MNT > /dev/null; L85: $XFS_IO_PROG -r -c "fiemap -v" $SCRATCH_MNT/mysnap2/foobar | _filter_fiemap.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; creates or manipulates btrfs subvolumes; persists snapshot roots and verifies their contents; creates send streams and receives them into a fresh filesystem.

Dependencies and integration points: Depends on xfstests common libraries, btrfs-progs and btrfs kernel feature gates, xfs_io workload commands. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: is tied to specific kernel-regression behavior noted by fixed-by annotations.

Test signals: fiemap extent layout and flags; visible subtest labels include File content in the new filesystem:; File fiemap in the new filesystem:.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/303 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/304 -->
# sources/test-tools/xfstests/tests/btrfs/304

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/btrfs/304_research.md`.

Source read: 56 lines, SHA256 prefix `c5a89bcfff508cab`.

Purpose: FS QA Test 304 Test on-disk layout of RAID Stripe Tree Metadata writing 4k to a new file on a pristine file system..

Important APIs/types/functions: test tags `auto quick raid remount volume raid-stripe-tree`; common harness imports `. ./common/preamble`, `. ./common/filter`, `. ./common/filter.btrfs`; requirements/fixed gates `_require_btrfs_command inspect-internal dump-tree`, `_require_btrfs_mkfs_feature "raid-stripe-tree"`, `_require_scratch_dev_pool 4`, `_require_btrfs_fs_feature "raid_stripe_tree"`, `_require_btrfs_fs_feature "free_space_tree"`, `_require_btrfs_free_space_tree`, `_require_btrfs_no_compress`, `_require_btrfs_support_sectorsize 4096`; helper functions `test_4k_write()`.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `test_4k_write()`. Representative operation sequence: L16: _require_btrfs_command inspect-internal dump-tree; L17: _require_btrfs_mkfs_feature "raid-stripe-tree"; L18: _require_scratch_dev_pool 4; L19: _require_btrfs_fs_feature "raid_stripe_tree"; L20: _require_btrfs_fs_feature "free_space_tree"; L21: _require_btrfs_free_space_tree; L22: _require_btrfs_no_compress; L23: _require_btrfs_support_sectorsize 4096; L30: _scratch_dev_pool_get $ndevs; L33: _scratch_pool_mkfs -s 4k -d $profile -m $profile -O raid-stripe-tree; L34: _scratch_mount; L36: $XFS_IO_PROG -fc "pwrite 0 4k" "$SCRATCH_MNT/foo" | _filter_xfs_io; L38: _scratch_cycle_mount; L39: md5sum "$SCRATCH_MNT/foo" | _filter_scratch; L41: _scratch_unmount; L43: $BTRFS_UTIL_PROG inspect-internal dump-tree -t raid_stripe $SCRATCH_DEV_POOL |\; L46: _scratch_dev_pool_put.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems.

Dependencies and integration points: Depends on xfstests common libraries, btrfs-progs and btrfs kernel feature gates, xfs_io workload commands. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: depends on xfstests harness requirements and exact golden-output filtering.

Test signals: matching file digests before and after remount/send/receive; btrfs on-disk tree inspection; visible subtest labels include = Test basic 4k write =.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/304 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/305 -->
# sources/test-tools/xfstests/tests/btrfs/305

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/btrfs/305_research.md`.

Source read: 61 lines, SHA256 prefix `4e353a4554e60a0d`.

Purpose: FS QA Test 305 Test on-disk layout of RAID Stripe Tree Metadata by writing 8k to a new file with a filesystem prepropulated, so that 4k of the write are written to the 1st stripe and 4k start a new stripe..

Important APIs/types/functions: test tags `auto quick raid remount volume raid-stripe-tree`; common harness imports `. ./common/preamble`, `. ./common/filter`, `. ./common/filter.btrfs`; requirements/fixed gates `_require_btrfs_command inspect-internal dump-tree`, `_require_btrfs_mkfs_feature "raid-stripe-tree"`, `_require_scratch_dev_pool 4`, `_require_btrfs_fs_feature "raid_stripe_tree"`, `_require_btrfs_fs_feature "free_space_tree"`, `_require_btrfs_free_space_tree`, `_require_btrfs_no_compress`, `_require_btrfs_support_sectorsize 4096`; helper functions `test_8k_new_stripe()`.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `test_8k_new_stripe()`. Representative operation sequence: L17: _require_btrfs_command inspect-internal dump-tree; L18: _require_btrfs_mkfs_feature "raid-stripe-tree"; L19: _require_scratch_dev_pool 4; L20: _require_btrfs_fs_feature "raid_stripe_tree"; L21: _require_btrfs_fs_feature "free_space_tree"; L22: _require_btrfs_free_space_tree; L23: _require_btrfs_no_compress; L24: _require_btrfs_support_sectorsize 4096; L31: _scratch_dev_pool_get $ndevs; L34: _scratch_pool_mkfs -s 4k -d $profile -m $profile -O raid-stripe-tree; L35: _scratch_mount; L38: $XFS_IO_PROG -fc "pwrite 0 60k" -c fsync "$SCRATCH_MNT/bar" | _filter_xfs_io; L41: $XFS_IO_PROG -fc "pwrite 0 8k" "$SCRATCH_MNT/foo" | _filter_xfs_io; L43: _scratch_cycle_mount; L44: md5sum "$SCRATCH_MNT/foo" | _filter_scratch; L46: _scratch_unmount; L48: $BTRFS_UTIL_PROG inspect-internal dump-tree -t raid_stripe $SCRATCH_DEV_POOL |\; L51: _scratch_dev_pool_put.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems.

Dependencies and integration points: Depends on xfstests common libraries, btrfs-progs and btrfs kernel feature gates, xfs_io workload commands. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: depends on xfstests harness requirements and exact golden-output filtering.

Test signals: matching file digests before and after remount/send/receive; btrfs on-disk tree inspection; visible subtest labels include = Test 8k write to a new file so that 4k start a new stripe =.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/305 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/306 -->
# sources/test-tools/xfstests/tests/btrfs/306

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/btrfs/306_research.md`.

Source read: 59 lines, SHA256 prefix `582ac8f7990d34e0`.

Purpose: FS QA Test 306 Test on-disk layout of RAID Stripe Tree Metadata by writing 4k to an emppty file at offset 64k with one stripe pre-filled on an otherwise pristine filesystem..

Important APIs/types/functions: test tags `auto quick raid remount volume raid-stripe-tree`; common harness imports `. ./common/preamble`, `. ./common/filter`, `. ./common/filter.btrfs`; requirements/fixed gates `_require_btrfs_command inspect-internal dump-tree`, `_require_btrfs_mkfs_feature "raid-stripe-tree"`, `_require_scratch_dev_pool 4`, `_require_btrfs_fs_feature "raid_stripe_tree"`, `_require_btrfs_fs_feature "free_space_tree"`, `_require_btrfs_free_space_tree`, `_require_btrfs_no_compress`, `_require_btrfs_support_sectorsize 4096`; helper functions `test_4k_write_64koff()`.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `test_4k_write_64koff()`. Representative operation sequence: L17: _require_btrfs_command inspect-internal dump-tree; L18: _require_btrfs_mkfs_feature "raid-stripe-tree"; L19: _require_scratch_dev_pool 4; L20: _require_btrfs_fs_feature "raid_stripe_tree"; L21: _require_btrfs_fs_feature "free_space_tree"; L22: _require_btrfs_free_space_tree; L23: _require_btrfs_no_compress; L24: _require_btrfs_support_sectorsize 4096; L31: _scratch_dev_pool_get $ndevs; L34: _scratch_pool_mkfs -s 4k -d $profile -m $profile -O raid-stripe-tree; L35: _scratch_mount; L38: $XFS_IO_PROG -fc "pwrite 0 64k" "$SCRATCH_MNT/bar" | _filter_xfs_io; L40: $XFS_IO_PROG -fc "pwrite 64k 4k" "$SCRATCH_MNT/foo" | _filter_xfs_io; L42: _scratch_cycle_mount; L43: md5sum "$SCRATCH_MNT/foo" | _filter_scratch; L45: _scratch_unmount; L47: $BTRFS_UTIL_PROG inspect-internal dump-tree -t raid_stripe $SCRATCH_DEV_POOL |\; L50: _scratch_dev_pool_put.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems.

Dependencies and integration points: Depends on xfstests common libraries, btrfs-progs and btrfs kernel feature gates, xfs_io workload commands. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: depends on xfstests harness requirements and exact golden-output filtering.

Test signals: matching file digests before and after remount/send/receive; btrfs on-disk tree inspection; visible subtest labels include = Test 4k write to an empty file at offset 64k with one stripe prefilled =.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/306 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/307 -->
# sources/test-tools/xfstests/tests/btrfs/307

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/btrfs/307_research.md`.

Source read: 57 lines, SHA256 prefix `14240aaac6c3ccdf`.

Purpose: FS QA Test 307 Test on-disk layout of RAID Stripe Tree Metadata by writing 128k to a new file on a pristine filesystem.

Important APIs/types/functions: test tags `auto quick raid remount volume raid-stripe-tree`; common harness imports `. ./common/preamble`, `. ./common/filter`, `. ./common/filter.btrfs`; requirements/fixed gates `_require_btrfs_command inspect-internal dump-tree`, `_require_btrfs_mkfs_feature "raid-stripe-tree"`, `_require_scratch_dev_pool 4`, `_require_btrfs_fs_feature "raid_stripe_tree"`, `_require_btrfs_fs_feature "free_space_tree"`, `_require_btrfs_free_space_tree`, `_require_btrfs_no_compress`; helper functions `test_128k_write()`.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `test_128k_write()`. Representative operation sequence: L16: _require_btrfs_command inspect-internal dump-tree; L17: _require_btrfs_mkfs_feature "raid-stripe-tree"; L18: _require_scratch_dev_pool 4; L19: _require_btrfs_fs_feature "raid_stripe_tree"; L20: _require_btrfs_fs_feature "free_space_tree"; L21: _require_btrfs_free_space_tree; L22: _require_btrfs_no_compress; L31: _scratch_dev_pool_get $ndevs; L34: _scratch_pool_mkfs -d $profile -m $profile -O raid-stripe-tree; L35: _scratch_mount; L37: $XFS_IO_PROG -fc "pwrite 0 128k" "$SCRATCH_MNT/foo" | _filter_xfs_io; L39: _scratch_cycle_mount; L40: md5sum "$SCRATCH_MNT/foo" | _filter_scratch; L42: _scratch_unmount; L44: $BTRFS_UTIL_PROG inspect-internal dump-tree -t raid_stripe $SCRATCH_DEV_POOL |\; L47: _scratch_dev_pool_put.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems.

Dependencies and integration points: Depends on xfstests common libraries, btrfs-progs and btrfs kernel feature gates, xfs_io workload commands. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: depends on xfstests harness requirements and exact golden-output filtering.

Test signals: matching file digests before and after remount/send/receive; btrfs on-disk tree inspection; visible subtest labels include = Test 128k write to empty file =.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/307 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/308 -->
# sources/test-tools/xfstests/tests/btrfs/308

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/btrfs/308_research.md`.

Source read: 61 lines, SHA256 prefix `47905cfb3600e301`.

Purpose: FS QA Test 308 Test on-disk layout of RAID Stripe Tree Metadata by writing 128k to an empty file on a filesystem that has one stripe already pre-filled. Afterwards overwrite a portion of the file..

Important APIs/types/functions: test tags `auto quick raid remount volume raid-stripe-tree`; common harness imports `. ./common/preamble`, `. ./common/filter`, `. ./common/filter.btrfs`; requirements/fixed gates `_require_btrfs_command inspect-internal dump-tree`, `_require_btrfs_mkfs_feature "raid-stripe-tree"`, `_require_scratch_dev_pool 4`, `_require_btrfs_fs_feature "raid_stripe_tree"`, `_require_btrfs_fs_feature "free_space_tree"`, `_require_btrfs_free_space_tree`, `_require_btrfs_no_compress`, `_require_btrfs_no_nodatacow`; helper functions `test_128k_write_overwrite()`.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `test_128k_write_overwrite()`. Representative operation sequence: L17: _require_btrfs_command inspect-internal dump-tree; L18: _require_btrfs_mkfs_feature "raid-stripe-tree"; L19: _require_scratch_dev_pool 4; L20: _require_btrfs_fs_feature "raid_stripe_tree"; L21: _require_btrfs_fs_feature "free_space_tree"; L22: _require_btrfs_free_space_tree; L23: _require_btrfs_no_compress; L24: _require_btrfs_no_nodatacow; L33: _scratch_dev_pool_get $ndevs; L36: _scratch_pool_mkfs -d $profile -m $profile -O raid-stripe-tree; L37: _scratch_mount; L39: $XFS_IO_PROG -fc "pwrite -W 0 32k" "$SCRATCH_MNT/bar" | _filter_xfs_io; L40: $XFS_IO_PROG -fc "pwrite -W 0 128k" "$SCRATCH_MNT/foo" | _filter_xfs_io; L41: $XFS_IO_PROG -fc "pwrite -W 64k 8k" "$SCRATCH_MNT/foo" | _filter_xfs_io; L43: _scratch_cycle_mount; L44: md5sum "$SCRATCH_MNT/foo" | _filter_scratch; L46: _scratch_unmount; L48: $BTRFS_UTIL_PROG inspect-internal dump-tree -t raid_stripe $SCRATCH_DEV_POOL |\.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems.

Dependencies and integration points: Depends on xfstests common libraries, btrfs-progs and btrfs kernel feature gates, xfs_io workload commands. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: depends on xfstests harness requirements and exact golden-output filtering.

Test signals: matching file digests before and after remount/send/receive; btrfs on-disk tree inspection; visible subtest labels include = Test 128k write to empty file with 1st stripe partially prefilled then overwrite =.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/308 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/309 -->
# sources/test-tools/xfstests/tests/btrfs/309

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/btrfs/309_research.md`.

Source read: 26 lines, SHA256 prefix `6c07800c04cd00c2`.

Purpose: FS QA Test 309 Try to snapshot a deleted subvolume..

Important APIs/types/functions: test tags `auto quick snapshot subvol`; common harness imports `. ./common/preamble`; requirements/fixed gates `_require_scratch`, `_require_test_program t_snapshot_deleted_subvolume`, `_fixed_by_kernel_commit 7081929ab257 \`.

Control flow: The script is mostly straight-line after harness setup. Representative operation sequence: L17: _scratch_mkfs >> $seqres.full 2>&1 || _fail "mkfs failed"; L18: _scratch_mount.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; creates or manipulates btrfs subvolumes; persists snapshot roots and verifies their contents.

Dependencies and integration points: Depends on xfstests common libraries, btrfs-progs and btrfs kernel feature gates. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: is tied to specific kernel-regression behavior noted by fixed-by annotations.

Test signals: no unexpected stdout beyond the golden quiet marker; visible subtest labels include Silence is golden.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/309 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/310 -->
# sources/test-tools/xfstests/tests/btrfs/310

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/btrfs/310_research.md`.

Source read: 76 lines, SHA256 prefix `c46b17c703d27e4f`.

Purpose: FS QA Test 310 Make sure reading on an compressed inline extent is behaving correctly.

Important APIs/types/functions: test tags `auto quick compress`; common harness imports `. ./common/preamble`; requirements/fixed gates `_require_scratch`, `_require_btrfs_inline_extents_creation`, `_require_btrfs_support_sectorsize 4096`, `_fixed_by_kernel_commit e01a83e12604 \`; helper functions `workload()`; key variables `md5sum_correct="5fed275e7617a806f94c173746a2a723"`, `result=$(_md5_checksum "$SCRATCH_MNT/inline_file")`, `result=$(_md5_checksum "$SCRATCH_MNT/inline_file")`, `algo_list=($(_btrfs_compression_algos))`.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `workload()`. Representative operation sequence: L16: _require_btrfs_inline_extents_creation; L17: _require_btrfs_support_sectorsize 4096; L23: md5sum_correct="5fed275e7617a806f94c173746a2a723"; L30: _scratch_mkfs >> $seqres.full; L31: _scratch_mount -o compress=${algo}; L36: if [ "$result" != "$md5sum_correct" ]; then; L43: $XFS_IO_PROG -c "fiemap -v" $SCRATCH_MNT/inline_file | tail -n 1 > $tmp.fiemap; L44: cat $tmp.fiemap >> $seqres.full; L48: if ! grep -q "0x309" $tmp.fiemap; then; L49: rm -f -- $tmp.fiemap; L52: rm -f -- $tmp.fiemap; L55: _scratch_cycle_mount; L61: if [ "$result" != "$md5sum_correct" ]; then; L64: _scratch_unmount; L65: _check_scratch_fs; L68: algo_list=($(_btrfs_compression_algos)).

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems.

Dependencies and integration points: Depends on xfstests common libraries, btrfs-progs and btrfs kernel feature gates, xfs_io workload commands. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: is tied to specific kernel-regression behavior noted by fixed-by annotations.

Test signals: no unexpected stdout beyond the golden quiet marker; matching file digests before and after remount/send/receive; fiemap extent layout and flags; visible subtest labels include Silence is golden.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/310 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/311 -->
# sources/test-tools/xfstests/tests/btrfs/311

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/btrfs/311_research.md`.

Source read: 85 lines, SHA256 prefix `895ad85707e3147b`.

Purpose: FS QA Test 311 Mount the device twice check if the reflink works, this helps to ensure device is mounted as the same device. Override the default cleanup function..

Important APIs/types/functions: test tags `auto quick subvol tempfsid`; common harness imports `. ./common/preamble`, `. ./common/filter.btrfs`, `. ./common/reflink`; requirements/fixed gates `_require_cp_reflink`, `_require_scratch`, `_require_btrfs_fs_feature temp_fsid`; helper functions `_cleanup()`, `same_dev_mount()`, `same_dev_subvol_mount()`; key variables `mnt1=$TEST_DIR/$seq/mnt1`.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `_cleanup()`, `same_dev_mount()`, `same_dev_subvol_mount()`. Representative operation sequence: L27: _require_btrfs_fs_feature temp_fsid; L32: same_dev_mount(); L36: _scratch_mkfs >> $seqres.full 2>&1; L38: _scratch_mount; L39: $XFS_IO_PROG -fc 'pwrite -S 0x61 0 9000' $SCRATCH_MNT/foo | \; L43: _mount $SCRATCH_DEV $mnt1; L47: md5sum $SCRATCH_MNT/foo | _filter_scratch; L48: md5sum $mnt1/bar | _filter_test_dir; L50: _check_temp_fsid $SCRATCH_DEV; L53: same_dev_subvol_mount(); L56: _scratch_mkfs >> $seqres.full 2>&1; L58: _scratch_mount; L59: $BTRFS_UTIL_PROG subvolume create $SCRATCH_MNT/subvol | _filter_scratch; L61: $XFS_IO_PROG -fc 'pwrite -S 0x61 0 9000' $SCRATCH_MNT/subvol/foo | \; L65: _mount -o subvol=subvol $SCRATCH_DEV $mnt1; L69: md5sum $SCRATCH_MNT/subvol/foo | _filter_scratch; L70: md5sum $mnt1/bar | _filter_test_dir; L72: _check_temp_fsid $SCRATCH_DEV.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; creates or manipulates btrfs subvolumes.

Dependencies and integration points: Depends on xfstests common libraries, btrfs-progs and btrfs kernel feature gates, xfs_io workload commands. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: depends on xfstests harness requirements and exact golden-output filtering.

Test signals: matching file digests before and after remount/send/receive; visible subtest labels include Mount the device again to a different mount point; Checksum of reflinked files; Mounting a subvol; Checksum of reflinked files.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/311 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/312 -->
# sources/test-tools/xfstests/tests/btrfs/312

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/btrfs/312_research.md`.

Source read: 115 lines, SHA256 prefix `7c644e14f2baa7c4`.

Purpose: FS QA Test 312 Test a scenario of a compressed send stream that triggered a bug in the extent map merging code introduced in the merge window for 6.11..

Important APIs/types/functions: test tags `auto quick send compress`; common harness imports `. ./common/preamble`, `. ./common/filter`; requirements/fixed gates `_require_btrfs_send_version 2`, `_require_test`, `_require_scratch`, `_fixed_by_kernel_commit de9f46cb0044 \`; helper functions `_cleanup()`; key variables `send_files_dir=$TEST_DIR/btrfs-test-$seq`, `first_stream="$send_files_dir/1.send"`, `second_stream="$send_files_dir/2.send"`.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `_cleanup()`. Representative operation sequence: L22: _require_btrfs_send_version 2; L36: _scratch_mkfs >> $seqres.full 2>&1 || _fail "first mkfs failed"; L37: _scratch_mount -o compress; L42: $XFS_IO_PROG -f -c "pwrite -S 0xab 111K 30K" $SCRATCH_MNT/foo >> $seqres.full; L44: $BTRFS_UTIL_PROG subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/snap1 >> $seqres.full; L49: $XFS_IO_PROG -c "pwrite -S 0xcd 120K 8K" $SCRATCH_MNT/foo >> $seqres.full; L90: $XFS_IO_PROG -c "pwrite -S 0xef 160K 4K" $SCRATCH_MNT/foo >> $seqres.full; L92: $BTRFS_UTIL_PROG subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/snap2 >> $seqres.full; L98: $BTRFS_UTIL_PROG send --compressed-data -q -f $first_stream $SCRATCH_MNT/snap1; L99: $BTRFS_UTIL_PROG send --compressed-data -q -f $second_stream \; L102: _scratch_unmount; L103: _scratch_mkfs >> $seqres.full 2>&1 || _fail "second mkfs failed"; L104: _scratch_mount; L106: $BTRFS_UTIL_PROG receive -q -f $first_stream $SCRATCH_MNT; L107: $BTRFS_UTIL_PROG receive -q -f $second_stream $SCRATCH_MNT.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; creates or manipulates btrfs subvolumes; persists snapshot roots and verifies their contents; creates send streams and receives them into a fresh filesystem.

Dependencies and integration points: Depends on xfstests common libraries, btrfs-progs and btrfs kernel feature gates, xfs_io workload commands. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: is tied to specific kernel-regression behavior noted by fixed-by annotations.

Test signals: matching file digests before and after remount/send/receive; visible subtest labels include Checksums in the original filesystem:; Checksums in the new filesystem:.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/312 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/313 -->
# sources/test-tools/xfstests/tests/btrfs/313

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/btrfs/313_research.md`.

Source read: 51 lines, SHA256 prefix `5655a85fa60227bc`.

Purpose: FS QA Test 313 Functional test for the tempfsid, clone devices created using the mkfs option..

Important APIs/types/functions: test tags `auto quick clone tempfsid`; common harness imports `. ./common/preamble`, `. ./common/filter.btrfs`, `. ./common/reflink`; requirements/fixed gates `_require_cp_reflink`, `_require_scratch_dev_pool 2`, `_require_btrfs_fs_feature temp_fsid`; helper functions `_cleanup()`; key variables `mnt1=$TEST_DIR/$seq/mnt1`.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `_cleanup()`. Representative operation sequence: L24: _require_scratch_dev_pool 2; L25: _require_btrfs_fs_feature temp_fsid; L27: _scratch_dev_pool_get 2; L33: _btrfs_mkfs_clone ${SCRATCH_DEV_NAME[0]} ${SCRATCH_DEV_NAME[1]}; L36: _mount ${SCRATCH_DEV_NAME[0]} $SCRATCH_MNT; L37: _check_temp_fsid ${SCRATCH_DEV_NAME[0]}; L40: _mount ${SCRATCH_DEV_NAME[1]} $mnt1; L41: _check_temp_fsid ${SCRATCH_DEV_NAME[1]}; L43: $XFS_IO_PROG -fc 'pwrite -S 0x61 0 9000' $SCRATCH_MNT/foo | _filter_xfs_io; L47: _scratch_dev_pool_put.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems.

Dependencies and integration points: Depends on xfstests common libraries, btrfs-progs and btrfs kernel feature gates, xfs_io workload commands. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: depends on xfstests harness requirements and exact golden-output filtering.

Test signals: visible subtest labels include ---- clone_uuids_verify_tempfsid ----; Mounting original device; Mounting cloned device; cp reflink must fail.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/313 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/314 -->
# sources/test-tools/xfstests/tests/btrfs/314

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/btrfs/314_research.md`.

Source read: 76 lines, SHA256 prefix `aa76f986351a3531`.

Purpose: FS QA Test 314 Send and receive functionality test between a normal and tempfsid filesystem..

Important APIs/types/functions: test tags `auto quick snapshot send tempfsid`; common harness imports `. ./common/preamble`, `. ./common/filter.btrfs`; requirements/fixed gates `_require_scratch_dev_pool 2`, `_require_btrfs_fs_feature temp_fsid`; helper functions `_cleanup()`, `send_receive_tempfsid()`; key variables `tempfsid_mnt=$TEST_DIR/$seq/tempfsid_mnt`, `sendfile=$TEST_DIR/$seq/replicate.send`.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `_cleanup()`, `send_receive_tempfsid()`. Representative operation sequence: L24: _require_scratch_dev_pool 2; L25: _require_btrfs_fs_feature temp_fsid; L27: _scratch_dev_pool_get 2; L39: _btrfs_mkfs_clone ${SCRATCH_DEV} ${SCRATCH_DEV_NAME[1]}; L40: _scratch_mount; L41: _mount $(_common_dev_mount_options) ${SCRATCH_DEV_NAME[1]} ${tempfsid_mnt}; L43: $XFS_IO_PROG -fc 'pwrite -S 0x61 0 9000' ${src}/foo | _filter_xfs_io; L44: _btrfs subvolume snapshot -r ${src} ${src}/snap1; L47: $BTRFS_UTIL_PROG send -f ${sendfile} ${src}/snap1 2>&1 | \; L50: $BTRFS_UTIL_PROG receive -f ${sendfile} ${dst} | \; L53: md5sum ${src}/foo | _filter_testdir_and_scratch; L55: md5sum ${dst}/snap1/foo | _filter_testdir_and_scratch; L64: _scratch_unmount; L72: _scratch_dev_pool_put.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; creates or manipulates btrfs subvolumes; persists snapshot roots and verifies their contents; creates send streams and receives them into a fresh filesystem.

Dependencies and integration points: Depends on xfstests common libraries, btrfs-progs and btrfs kernel feature gates, xfs_io workload commands. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: depends on xfstests harness requirements and exact golden-output filtering.

Test signals: matching file digests before and after remount/send/receive.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/314 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/315 -->
# sources/test-tools/xfstests/tests/btrfs/315

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/btrfs/315_research.md`.

Source read: 76 lines, SHA256 prefix `23311af82c16a616`.

Purpose: FS QA Test 315 Verify if the seed and device add to a tempfsid filesystem fails and balance devices is successful..

Important APIs/types/functions: test tags `auto quick volume seed balance tempfsid`; common harness imports `. ./common/preamble`, `. ./common/filter`; requirements/fixed gates `_require_scratch_dev_pool 3`, `_require_btrfs_fs_feature temp_fsid`; helper functions `_cleanup()`, `seed_device_must_fail()`, `device_add_must_fail()`; key variables `tempfsid_mnt=$TEST_DIR/$seq/tempfsid_mnt`.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `_cleanup()`, `seed_device_must_fail()`, `device_add_must_fail()`. Representative operation sequence: L23: _require_scratch_dev_pool 3; L24: _require_btrfs_fs_feature temp_fsid; L26: _scratch_dev_pool_get 3; L35: _btrfs_mkfs_clone ${SCRATCH_DEV} ${SCRATCH_DEV_NAME[1]}; L37: $BTRFS_TUNE_PROG -S 1 ${SCRATCH_DEV}; L38: $BTRFS_TUNE_PROG -S 1 ${SCRATCH_DEV_NAME[1]}; L40: _scratch_mount 2>&1 | _filter_scratch; L41: _mount ${SCRATCH_DEV_NAME[1]} ${tempfsid_mnt} 2>&1 | _filter_error_mount; L48: _btrfs_mkfs_clone ${SCRATCH_DEV} ${SCRATCH_DEV_NAME[1]}; L49: _scratch_mount; L50: _mount ${SCRATCH_DEV_NAME[1]} ${tempfsid_mnt}; L52: $XFS_IO_PROG -fc 'pwrite -S 0x61 0 9000' $SCRATCH_MNT/foo | \; L55: $BTRFS_UTIL_PROG device add -f ${SCRATCH_DEV_NAME[2]} ${tempfsid_mnt} 2>&1 | \; L56: grep -v "Performing full device TRIM" | _filter_scratch_pool; L59: _run_btrfs_balance_start ${tempfsid_mnt}; L66: _scratch_unmount; L72: _scratch_dev_pool_put.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems.

Dependencies and integration points: Depends on xfstests common libraries, btrfs-progs and btrfs kernel feature gates, xfs_io workload commands. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: depends on xfstests harness requirements and exact golden-output filtering.

Test signals: visible subtest labels include Balance must be successful.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/315 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/316 -->
# sources/test-tools/xfstests/tests/btrfs/316

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/btrfs/316_research.md`.

Source read: 59 lines, SHA256 prefix `194649daaae65538`.

Purpose: FS QA Test 316 Make sure btrfs qgroup won't leak its reserved data space if qgroup is marked inconsistent. This exercises a regression introduced in v6.1 kernel by the following commit: e15e9f43c7ca ("btrfs: introduce BTRFS_QGROUP_RUNTIME_FLAG_NO_ACCOUNTING to skip qgroup accounting").

Important APIs/types/functions: test tags `auto quick qgroup`; common harness imports `. ./common/preamble`; requirements/fixed gates `_require_scratch`, `_require_qgroup_rescan`, `_fixed_by_kernel_commit d139ded8b9cd \`.

Control flow: The script is mostly straight-line after harness setup. Representative operation sequence: L23: _scratch_mkfs >> $seqres.full; L24: _scratch_mount; L26: $BTRFS_UTIL_PROG quota enable $SCRATCH_MNT; L29: $BTRFS_UTIL_PROG qgroup create 1/0 $SCRATCH_MNT >> $seqres.full; L30: $BTRFS_UTIL_PROG subvolume create $SCRATCH_MNT/subv1 >> $seqres.full; L36: $BTRFS_UTIL_PROG subvolume snapshot -i 1/0 $SCRATCH_MNT/subv1 $SCRATCH_MNT/snap1 >> $seqres.full; L44: _scratch_unmount.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; creates or manipulates btrfs subvolumes; persists snapshot roots and verifies their contents; changes quota/qgroup accounting state.

Dependencies and integration points: Depends on xfstests common libraries, btrfs-progs and btrfs kernel feature gates. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: quota accounting regressions can be silent until unmount or rescan; is tied to specific kernel-regression behavior noted by fixed-by annotations.

Test signals: no unexpected stdout beyond the golden quiet marker; absence or presence of expected dmesg warnings; visible subtest labels include Silence is golden.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/316 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/317 -->
# sources/test-tools/xfstests/tests/btrfs/317

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/btrfs/317_research.md`.

Source read: 66 lines, SHA256 prefix `9a025ce7549594ef`.

Purpose: FS QA Test 317 Test that btrfs convert can ony be run to convert to supported profiles on a zoned filesystem.

Important APIs/types/functions: test tags `auto volume raid convert`; common harness imports `. ./common/preamble`, `. common/filter.btrfs`; requirements/fixed gates `_fixed_by_kernel_commit 5906333cc4af \`, `_require_scratch_dev_pool 4`, `_require_zoned_device "$SCRATCH_DEV"`; key variables `devs=( $SCRATCH_DEV_POOL )`.

Control flow: The script is mostly straight-line after harness setup. Representative operation sequence: L18: _require_scratch_dev_pool 4; L24: _scratch_mkfs -msingle -dsingle 2>&1 >> $seqres.full || _fail "mkfs failed"; L25: _scratch_mount; L28: _run_btrfs_balance_start -f -mconvert=dup -sconvert=dup $SCRATCH_MNT 2>&1 |\; L32: _run_btrfs_balance_start -dconvert=dup $SCRATCH_MNT 2>&1 |\; L36: $BTRFS_UTIL_PROG device add ${devs[1]} $SCRATCH_MNT | _filter_device_add; L39: _run_btrfs_balance_start -dconvert=raid1 $SCRATCH_MNT 2>&1 |\; L43: _run_btrfs_balance_start -dconvert=raid0 $SCRATCH_MNT 2>&1 |\; L47: $BTRFS_UTIL_PROG device add ${devs[2]} $SCRATCH_MNT | _filter_device_add; L50: _run_btrfs_balance_start -f -dconvert=raid5 $SCRATCH_MNT 2>&1 |\; L54: $BTRFS_UTIL_PROG device add ${devs[3]} $SCRATCH_MNT | _filter_device_add; L57: _run_btrfs_balance_start -dconvert=raid10 $SCRATCH_MNT 2>&1 |\; L61: _run_btrfs_balance_start -f -dconvert=raid6 $SCRATCH_MNT 2>&1 |\.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems.

Dependencies and integration points: Depends on xfstests common libraries, btrfs-progs and btrfs kernel feature gates. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: is tied to specific kernel-regression behavior noted by fixed-by annotations.

Test signals: successful script exit with xfstests filtered output.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/317 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/318 -->
# sources/test-tools/xfstests/tests/btrfs/318

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/btrfs/318_research.md`.

Source read: 106 lines, SHA256 prefix `704df25a035adb9b`.

Purpose: FS QA Test No. 318 Test an edge case of multi device volume management in btrfs. If a device changes devt between mounts of a multi device fs, we can trick btrfs into mounting the same device twice fully (not as a bind mount). From there, it is trivial to induce corruption..

Important APIs/types/functions: test tags `auto quick volume scrub tempfsid`; common harness imports `. ./common/preamble`; requirements/fixed gates `_fixed_by_kernel_commit 9f7eb8405dcb \`, `_require_test`, `_require_command "$PARTED_PROG" parted`, `_require_batched_discard "$TEST_DIR"`, `_require_loop`; helper functions `_cleanup()`; key variables `IMG0=$TEST_DIR/$$.img0`, `IMG1=$TEST_DIR/$$.img1`, `IMG2=$TEST_DIR/$$.img2`, `DEV0=$(_create_loop_device $IMG0)`, `DEV1=$(_create_loop_device $IMG1)`, `DEV2=$(_create_loop_device $IMG2)`, `D0P1=$DEV0"p1"`, `D1P1=$DEV1"p1"`, `MNT=$TEST_DIR/mnt-${seq}`, `BIND=$TEST_DIR/bind-${seq}`.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `_cleanup()`. Representative operation sequence: L54: $MKFS_BTRFS_PROG -f -msingle -dsingle $D0P1 $DEV2 >>$seqres.full 2>&1 || _fail "failed to mkfs.btrfs"; L60: _mount $D0P1 $MNT; L70: _mount $D0P1 $MNT; L73: $BTRFS_UTIL_PROG device remove $DEV2 $MNT; L78: _mount $D0P1 $BIND; L79: mount_show=$($BTRFS_UTIL_PROG filesystem show $MNT); L80: bind_show=$($BTRFS_UTIL_PROG filesystem show $BIND); L86: $XFS_IO_PROG -f -c "pwrite 0 50M" $MNT/foo.$i >>$seqres.full 2>&1; L89: $XFS_IO_PROG -f -c "pwrite 0 50M" $BIND/foo.$i >>$seqres.full 2>&1; L103: $BTRFS_UTIL_PROG scrub start -B $MNT | grep "Error summary:".

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; creates loop devices or image-backed devices; drops page cache to force media-backed reads.

Dependencies and integration points: Depends on xfstests common libraries, btrfs-progs and btrfs kernel feature gates, xfs_io workload commands. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: requires privileged cache dropping and can perturb the host; loop-device cleanup must run to avoid leaked devices; device identity and partition node timing are important; is tied to specific kernel-regression behavior noted by fixed-by annotations.

Test signals: visible subtest labels include 3 > /proc/sys/vm/drop_caches.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/318 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/319 -->
# sources/test-tools/xfstests/tests/btrfs/319

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/btrfs/319_research.md`.

Source read: 91 lines, SHA256 prefix `3ab5bbd596fc3383`.

Purpose: FS QA Test 319 Test that a send operation will issue a clone operation for a shared extent of a file if the extent ends at the i_size of the file and the i_size is not sector size aligned. Override the default cleanup function..

Important APIs/types/functions: test tags `auto quick send clone fiemap`; common harness imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`, `. ./common/punch # for _filter_fiemap_flags`; requirements/fixed gates `_require_test`, `_require_scratch_reflink`, `_require_cp_reflink`, `_require_xfs_io_command "fiemap"`, `_require_odirect`, `_fixed_by_kernel_commit 46a6e10a1ab1 \`; helper functions `_cleanup()`, `check_all_extents_shared()`; key variables `fiemap_output=$($XFS_IO_PROG -r -c "fiemap -v" $file | _filter_fiemap_flags)`, `send_files_dir=$TEST_DIR/btrfs-test-$seq`, `send_stream=$send_files_dir/snap.stream`, `file_size=$((1024 * 1024 + 5))`.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `_cleanup()`, `check_all_extents_shared()`. Representative operation sequence: L12: _begin_fstest auto quick send clone fiemap; L24: . ./common/punch # for _filter_fiemap_flags; L27: _require_scratch_reflink; L29: _require_xfs_io_command "fiemap"; L38: local fiemap_output; L40: fiemap_output=$($XFS_IO_PROG -r -c "fiemap -v" $file | _filter_fiemap_flags); L54: _scratch_mkfs >> $seqres.full 2>&1 || _fail "first mkfs failed"; L55: _scratch_mount; L60: $XFS_IO_PROG -f -d -c "pwrite -S 0xab -b $file_size 0 $file_size" \; L67: _btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/snap; L68: $BTRFS_UTIL_PROG send -f $send_stream $SCRATCH_MNT/snap >> $seqres.full 2>&1; L71: md5sum $SCRATCH_MNT/snap/foo | _filter_scratch; L72: md5sum $SCRATCH_MNT/snap/bar | _filter_scratch; L77: _scratch_unmount; L78: _scratch_mkfs >> $seqres.full 2>&1 || _fail "second mkfs failed"; L79: _scratch_mount; L81: $BTRFS_UTIL_PROG receive -f $send_stream $SCRATCH_MNT; L84: md5sum $SCRATCH_MNT/snap/foo | _filter_scratch.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; creates or manipulates btrfs subvolumes; persists snapshot roots and verifies their contents; creates send streams and receives them into a fresh filesystem.

Dependencies and integration points: Depends on xfstests common libraries, btrfs-progs and btrfs kernel feature gates, xfs_io workload commands. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: is tied to specific kernel-regression behavior noted by fixed-by annotations.

Test signals: matching file digests before and after remount/send/receive; fiemap extent layout and flags; visible subtest labels include Creating snapshot and a send stream for it...; File digests in the original filesystem:; Creating a new filesystem to receive the send stream...; File digests in the new filesystem:.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/319 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/320 -->
# sources/test-tools/xfstests/tests/btrfs/320

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/btrfs/320_research.md`.

Source read: 105 lines, SHA256 prefix `3a3aa6d4f6fbbfbc`.

Purpose: FS QA Test No. 320 Test qgroups to validate the creation works, the counters are sane, rescan works, and we do not get failures when we write less than the limit amount..

Important APIs/types/functions: test tags `auto qgroup limit`; common harness imports `. ./common/preamble`, `. ./common/filter`; requirements/fixed gates `_require_scratch`, `_require_qgroup_rescan`, `_require_btrfs_qgroup_report`, `_require_scratch_qgroup`; helper functions `_basic_test()`, `_rescan_test()`, `_limit_test_noexceed()`; key variables `subvolid=$(_btrfs_get_subvolid $SCRATCH_MNT a)`, `a_shared=$($BTRFS_UTIL_PROG qgroup show $units $SCRATCH_MNT | grep "0/$subvolid")`, `a_shared=$(echo $a_shared | $AWK_PROG '{ print $2 }')`, `subvolid=$(_btrfs_get_subvolid $SCRATCH_MNT b)`, `b_shared=$($BTRFS_UTIL_PROG qgroup show $units $SCRATCH_MNT | grep "0/$subvolid")`, `b_shared=$(echo $b_shared | $AWK_PROG '{ print $2 }')`, `subvolid=$(_btrfs_get_subvolid $SCRATCH_MNT a)`, `output=$($BTRFS_UTIL_PROG qgroup show $units $SCRATCH_MNT | grep "0/$subvolid")`, `refer=$(echo $output | $AWK_PROG '{ print $2 }')`, `excl=$(echo $output | $AWK_PROG '{ print $3 }')`.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `_basic_test()`, `_rescan_test()`, `_limit_test_noexceed()`. Representative operation sequence: L17: _require_btrfs_qgroup_report; L18: _require_scratch_qgroup; L24: _btrfs subvolume create $SCRATCH_MNT/a; L25: _btrfs quota enable $SCRATCH_MNT/a; L27: subvolid=$(_btrfs_get_subvolid $SCRATCH_MNT a); L28: $BTRFS_UTIL_PROG qgroup show $units $SCRATCH_MNT | grep $subvolid >> \; L31: _run_fsstress -d $SCRATCH_MNT/a -w -p 1 -n 2000; L32: _btrfs subvolume snapshot $SCRATCH_MNT/a \; L37: a_shared=$($BTRFS_UTIL_PROG qgroup show $units $SCRATCH_MNT | grep "0/$subvolid"); L40: subvolid=$(_btrfs_get_subvolid $SCRATCH_MNT b); L42: b_shared=$($BTRFS_UTIL_PROG qgroup show $units $SCRATCH_MNT | grep "0/$subvolid"); L44: $BTRFS_UTIL_PROG qgroup show $units $SCRATCH_MNT >> $seqres.full; L54: _btrfs subvolume create $SCRATCH_MNT/a; L55: _btrfs quota enable $SCRATCH_MNT/a; L56: subvolid=$(_btrfs_get_subvolid $SCRATCH_MNT a); L57: _run_fsstress -d $SCRATCH_MNT/a -w -p 1 -n 2000; L59: output=$($BTRFS_UTIL_PROG qgroup show $units $SCRATCH_MNT | grep "0/$subvolid"); L64: output=$($BTRFS_UTIL_PROG qgroup show $units $SCRATCH_MNT | grep "0/$subvolid").

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; creates or manipulates btrfs subvolumes; persists snapshot roots and verifies their contents; changes quota/qgroup accounting state.

Dependencies and integration points: Depends on xfstests common libraries, btrfs-progs and btrfs kernel feature gates. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: quota accounting regressions can be silent until unmount or rescan.

Test signals: no unexpected stdout beyond the golden quiet marker; visible subtest labels include Silence is golden.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/320 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/321 -->
# sources/test-tools/xfstests/tests/btrfs/321

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/btrfs/321_research.md`.

Source read: 85 lines, SHA256 prefix `bca0fdf15b2b6ff7`.

Purpose: FS QA Test 321 Make sure there are no use-after-free, crashes, deadlocks etc, when reading data which has its data checksums in a corrupted csum tree block..

Important APIs/types/functions: test tags `auto quick raid dangerous`; common harness imports `. ./common/preamble`; requirements/fixed gates `_require_scratch_nocheck`, `_require_scratch_dev_pool 2`, `_require_btrfs_raid_type raid0`, `_require_btrfs_support_sectorsize 4096`, `_require_btrfs_command inspect-internal dump-tree`, `_fixed_by_kernel_commit 10d9d8c3512f \`; key variables `iterations=32`, `physical=$(_btrfs_get_physical "$target_bytenr" 1)`, `dev=$(_btrfs_get_device_path "$target_bytenr" 1)`.

Control flow: The script is mostly straight-line after harness setup. Representative operation sequence: L13: _require_scratch_nocheck; L14: _require_scratch_dev_pool 2; L18: _require_btrfs_raid_type raid0; L22: _require_btrfs_support_sectorsize 4096; L23: _require_btrfs_command inspect-internal dump-tree; L32: _scratch_pool_mkfs "-d raid0 -m single -n 4k -s 4k" >> $seqres.full 2>&1; L34: _scratch_mount -o datasum,datacow; L41: _scratch_unmount; L45: $BTRFS_UTIL_PROG inspect-internal dump-tree -t 7 $SCRATCH_DEV >> $seqres.full; L46: target_bytenr=$($BTRFS_UTIL_PROG inspect-internal dump-tree -t 7 $SCRATCH_DEV | grep "^leaf.*items" | sort | tail -n1 | cut -f2 -d\ ); L55: physical=$(_btrfs_get_physical "$target_bytenr" 1); L56: dev=$(_btrfs_get_device_path "$target_bytenr" 1); L65: _scratch_mount -o ro; L71: _scratch_unmount; L77: if _check_dmesg_for "BUG" ; then.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems.

Dependencies and integration points: Depends on xfstests common libraries, btrfs-progs and btrfs kernel feature gates. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: bypasses normal scratch checking because corruption is intentional; is tied to specific kernel-regression behavior noted by fixed-by annotations.

Test signals: no unexpected stdout beyond the golden quiet marker; absence or presence of expected dmesg warnings; btrfs on-disk tree inspection; visible subtest labels include Silence is golden.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/321 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/322 -->
# sources/test-tools/xfstests/tests/btrfs/322

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/btrfs/322_research.md`.

Source read: 109 lines, SHA256 prefix `68099fed857d6ba9`.

Purpose: FS QA Test 322 Test that doing an incremental send with a file that had its size decreased and became the destination for a clone operation of an extent with an unaligned end offset that matches the new file size, works correctly..

Important APIs/types/functions: test tags `auto quick send clone fiemap`; common harness imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`, `. ./common/punch # for _filter_fiemap_flags`; requirements/fixed gates `_require_test`, `_require_scratch_reflink`, `_require_xfs_io_command "fiemap"`, `_require_xfs_io_command "reflink"`, `_require_odirect`, `_fixed_by_kernel_commit fa630df665aa \`; helper functions `_cleanup()`, `check_all_extents_shared()`; key variables `fiemap_output=$($XFS_IO_PROG -r -c "fiemap -v" $file | _filter_fiemap_flags)`, `send_files_dir=$TEST_DIR/btrfs-test-$seq`, `full_send_stream=$send_files_dir/full_snap.stream`, `inc_send_stream=$send_files_dir/inc_snap.stream`, `last_extent_size=$((128 * 1024 + 5))`.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `_cleanup()`, `check_all_extents_shared()`. Representative operation sequence: L12: _begin_fstest auto quick send clone fiemap; L23: . ./common/punch # for _filter_fiemap_flags; L26: _require_scratch_reflink; L27: _require_xfs_io_command "fiemap"; L37: local fiemap_output; L39: fiemap_output=$($XFS_IO_PROG -r -c "fiemap -v" $file | _filter_fiemap_flags); L54: _scratch_mkfs >> $seqres.full 2>&1 || _fail "first mkfs failed"; L55: _scratch_mount; L60: $XFS_IO_PROG -f -d -c "pwrite -S 0xab -b 128K 0 128K" \; L66: $XFS_IO_PROG -f -c "pwrite -b 0xef 0 1M" $SCRATCH_MNT/bar | _filter_xfs_io; L69: _btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/snap1; L70: $BTRFS_UTIL_PROG send -f $full_send_stream $SCRATCH_MNT/snap1 >> $seqres.full 2>&1; L73: $XFS_IO_PROG -c "truncate 0" \; L77: _btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/snap2; L78: $BTRFS_UTIL_PROG send -p $SCRATCH_MNT/snap1 -f $inc_send_stream \; L82: md5sum $SCRATCH_MNT/snap1/foo | _filter_scratch; L83: md5sum $SCRATCH_MNT/snap1/bar | _filter_scratch; L84: md5sum $SCRATCH_MNT/snap2/foo | _filter_scratch.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; creates or manipulates btrfs subvolumes; persists snapshot roots and verifies their contents; creates send streams and receives them into a fresh filesystem.

Dependencies and integration points: Depends on xfstests common libraries, btrfs-progs and btrfs kernel feature gates, xfs_io workload commands. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: is tied to specific kernel-regression behavior noted by fixed-by annotations.

Test signals: matching file digests before and after remount/send/receive; fiemap extent layout and flags; visible subtest labels include Creating snapshot and the full send stream for it...; Creating another snapshot and the incremental send stream for it...; File digests in the original filesystem:; Creating a new filesystem to receive the send streams...; File digests in the new filesystem:.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/322 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/323 -->
# sources/test-tools/xfstests/tests/btrfs/323

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/btrfs/323_research.md`.

Source read: 47 lines, SHA256 prefix `3d466767befaafa3`.

Purpose: FS QA Test 323 Test that remounted seed/sprout device FS is fully functional. For example, that it can purge stale subvolumes..

Important APIs/types/functions: test tags `auto quick seed remount volume`; common harness imports `. ./common/preamble`, `. ./common/filter`; requirements/fixed gates `_require_command "$BTRFS_TUNE_PROG" btrfstune`, `_require_scratch_dev_pool 2`, `_fixed_by_kernel_commit 70958a949d85 \`.

Control flow: The script is mostly straight-line after harness setup. Representative operation sequence: L13: _require_command "$BTRFS_TUNE_PROG" btrfstune; L14: _require_scratch_dev_pool 2; L19: _scratch_dev_pool_get 1; L23: _scratch_mkfs >>$seqres.full; L24: $BTRFS_TUNE_PROG -S 1 $SCRATCH_DEV; L25: _scratch_mount 2>&1 | _filter_scratch; L26: _btrfs device add -f $SPARE_DEV $SCRATCH_MNT >>$seqres.full; L30: _mount -o remount,rw $SCRATCH_MNT; L34: _btrfs subvolume create $SCRATCH_MNT/subv; L35: _btrfs subvolume delete $SCRATCH_MNT/subv; L38: _btrfs filesystem sync $SCRATCH_MNT; L41: $BTRFS_UTIL_PROG subvolume list -d $SCRATCH_MNT.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; creates or manipulates btrfs subvolumes.

Dependencies and integration points: Depends on xfstests common libraries, btrfs-progs and btrfs kernel feature gates. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: is tied to specific kernel-regression behavior noted by fixed-by annotations.

Test signals: mount/statfs option visibility.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/323 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/324 -->
# sources/test-tools/xfstests/tests/btrfs/324

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/btrfs/324_research.md`.

Source read: 39 lines, SHA256 prefix `0edb3126cdb7de9f`.

Purpose: Test that remounting with the "compress" mount option clears the "compress-force" mount option previously specified..

Important APIs/types/functions: test tags `auto quick mount remount compress`; common harness imports `. ./common/preamble`; requirements/fixed gates `_require_scratch`, `_fixed_by_kernel_commit 3510e684b8f6 \`.

Control flow: The script is mostly straight-line after harness setup. Representative operation sequence: L16: _scratch_mkfs >>$seqres.full 2>&1 || _fail "mkfs failed"; L17: _scratch_mount -o compress-force=zlib:9; L28: _scratch_remount compress=zlib:4.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems.

Dependencies and integration points: Depends on xfstests common libraries, btrfs-progs and btrfs kernel feature gates. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: is tied to specific kernel-regression behavior noted by fixed-by annotations.

Test signals: no unexpected stdout beyond the golden quiet marker; mount/statfs option visibility; visible subtest labels include compress-force not set to zlib:9 after initial mount:; compress not set to zlib:4 after remount:; Silence is golden.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/324 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/325 -->
# sources/test-tools/xfstests/tests/btrfs/325

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/btrfs/325_research.md`.

Source read: 83 lines, SHA256 prefix `34d291795a4368ec`.

Purpose: FS QA Test 325 Test that defrag merges adjacent extents that are contiguous..

Important APIs/types/functions: test tags `auto quick preallocrw defrag`; common harness imports `. ./common/preamble`, `. ./common/filter`; requirements/fixed gates `_require_scratch`, `_require_btrfs_command inspect-internal dump-tree`, `_require_xfs_io_command "falloc"`, `_require_no_compress`, `_fixed_by_kernel_commit a0f062539085 \`, `_fixed_by_kernel_commit 77b0d113eec4 \`; helper functions `count_file_extent_items()`.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `count_file_extent_items()`. Representative operation sequence: L15: _require_btrfs_command inspect-internal dump-tree; L16: _require_xfs_io_command "falloc"; L33: _scratch_unmount; L34: $BTRFS_UTIL_PROG inspect-internal dump-tree -t 5 $SCRATCH_DEV | \; L36: _scratch_mount; L39: _scratch_mkfs >>$seqres.full 2>&1 || _fail "mkfs failed"; L40: _scratch_mount; L45: $XFS_IO_PROG -f -c "falloc 0 64K" \; L47: -c "falloc 64K 64K" \; L49: -c "falloc 128K 64K" \; L51: -c "falloc 192K 64K" \; L64: $BTRFS_UTIL_PROG filesystem defragment -t 128K $SCRATCH_MNT/foo; L73: $BTRFS_UTIL_PROG filesystem defragment -t 256K $SCRATCH_MNT/foo.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems.

Dependencies and integration points: Depends on xfstests common libraries, btrfs-progs and btrfs kernel feature gates, xfs_io workload commands. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: is tied to specific kernel-regression behavior noted by fixed-by annotations.

Test signals: fiemap extent layout and flags; btrfs on-disk tree inspection; visible subtest labels include File data after defrag:.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/325 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/326 -->
# sources/test-tools/xfstests/tests/btrfs/326

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/btrfs/326_research.md`.

Source read: 112 lines, SHA256 prefix `606edf534c02efa5`.

Purpose: FS QA Test No. 326 Test that mounting a subvolume read-write will success, with another subvolume being remounted RO/RW at background.

Important APIs/types/functions: test tags `auto quick mount remount`; common harness imports `. ./common/preamble`; requirements/fixed gates `_fixed_by_kernel_commit 951a3f59d268 \`, `_fixed_by_kernel_commit 344bac8f0d73 \`, `_require_test`, `_require_scratch`; helper functions `_cleanup()`, `remount_workload()`, `mount_workload()`; key variables `subv1_mount="$TEST_DIR/subvol1_mount"`, `subv2_mount="$TEST_DIR/subvol2_mount"`, `remount_pid=$!`, `mount_pid=$!`.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `_cleanup()`, `remount_workload()`, `mount_workload()`. Representative operation sequence: L28: $UMOUNT_PROG "$subv1_mount" &> /dev/null; L29: $UMOUNT_PROG "$subv2_mount" &> /dev/null; L30: rm -rf -- "$subv1_mount" "$subv2_mount"; L37: _scratch_mkfs >> $seqres.full 2>&1; L38: _scratch_mount; L39: $BTRFS_UTIL_PROG subvolume create $SCRATCH_MNT/subvol1 >> $seqres.full; L40: $BTRFS_UTIL_PROG subvolume create $SCRATCH_MNT/subvol2 >> $seqres.full; L41: _scratch_unmount; L43: subv1_mount="$TEST_DIR/subvol1_mount"; L44: subv2_mount="$TEST_DIR/subvol2_mount"; L45: rm -rf "$subv1_mount" "$subv2_mount"; L46: mkdir -p "$subv1_mount"; L47: mkdir -p "$subv2_mount"; L48: _mount "$SCRATCH_DEV" "$subv1_mount" -o subvol=subvol1; L56: _mount -o remount,ro "$subv1_mount"; L57: _mount -o remount,rw "$subv1_mount"; L82: _mount "$SCRATCH_DEV" "$subv2_mount"; L83: $UMOUNT_PROG "$subv2_mount".

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; creates or manipulates btrfs subvolumes.

Dependencies and integration points: Depends on xfstests common libraries, btrfs-progs and btrfs kernel feature gates. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: contains timing-sensitive waits; is tied to specific kernel-regression behavior noted by fixed-by annotations.

Test signals: no unexpected stdout beyond the golden quiet marker; visible subtest labels include Silence is golden.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/326 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/327 -->
# sources/test-tools/xfstests/tests/btrfs/327

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/btrfs/327_research.md`.

Source read: 56 lines, SHA256 prefix `3684c7e1ca1bd9f6`.

Purpose: FS QA Test 327 Make sure reading inlined extents doesn't cause any corruption. This is a preventive test case inspired by btrfs/149, which can cause data corruption when the following out-of-tree patches are applied and the sector size is smaller than page size: btrfs: allow inline data extents creation if sector size < page size btrfs: allow buffered write to skip full page if it's sector aligned Thankfully no upstream kernel is affected..

Important APIs/types/functions: test tags `auto quick compress`; common harness imports `. ./common/preamble`; requirements/fixed gates `_require_scratch`, `_require_btrfs_support_sectorsize 4096`.

Control flow: The script is mostly straight-line after harness setup. Representative operation sequence: L29: _require_btrfs_support_sectorsize 4096; L31: _scratch_mkfs >>$seqres.full 2>&1; L32: _scratch_mount "-o compress,max_inline=4095"; L39: $XFS_IO_PROG -f -c "pwrite 0 4k" "$SCRATCH_MNT/foobar" > /dev/null; L47: $XFS_IO_PROG -f -c "pwrite 8k 4k" "$SCRATCH_MNT/foobar" > /dev/null.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; drops page cache to force media-backed reads.

Dependencies and integration points: Depends on xfstests common libraries, btrfs-progs and btrfs kernel feature gates, xfs_io workload commands. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: requires privileged cache dropping and can perturb the host.

Test signals: matching file digests before and after remount/send/receive; visible subtest labels include 3 > /proc/sys/vm/drop_caches.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/327 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/328 -->
# sources/test-tools/xfstests/tests/btrfs/328

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/btrfs/328_research.md`.

Source read: 31 lines, SHA256 prefix `15998e3fcf20b951`.

Purpose: FS QA Test 328 Test that if we enable simple quotas on a filesystem and unmount it right after without doing any other changes to the filesystem, we are able to mount again the filesystem..

Important APIs/types/functions: test tags `auto quick qgroup`; common harness imports `. ./common/preamble`; requirements/fixed gates `_fixed_by_kernel_commit f2363e6fcc79 \`, `_require_scratch_enable_simple_quota`.

Control flow: The script is mostly straight-line after harness setup. Representative operation sequence: L17: _require_scratch_enable_simple_quota; L19: _scratch_mkfs >> $seqres.full 2>&1 || _fail "mkfs failed"; L20: _scratch_mount; L22: $BTRFS_UTIL_PROG quota enable --simple $SCRATCH_MNT; L27: _scratch_cycle_mount.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; changes quota/qgroup accounting state.

Dependencies and integration points: Depends on xfstests common libraries, btrfs-progs and btrfs kernel feature gates. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: quota accounting regressions can be silent until unmount or rescan; is tied to specific kernel-regression behavior noted by fixed-by annotations.

Test signals: no unexpected stdout beyond the golden quiet marker; visible subtest labels include Silence is golden.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/328 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/329 -->
# sources/test-tools/xfstests/tests/btrfs/329

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/btrfs/329_research.md`.

Source read: 21 lines, SHA256 prefix `ca56834329e887ea`.

Purpose: FS QA Test 329 Verify sysfs knob input syntax for read_policy round-robin.

Important APIs/types/functions: test tags `auto quick`; common harness imports `. ./common/preamble`, `. ./common/sysfs`, `. ./common/filter`; requirements/fixed gates `_require_test`, `_require_fs_sysfs_attr_policy $TEST_DEV read_policy round-robin`.

Control flow: The script is mostly straight-line after harness setup. The main operation is encoded through the xfstests helpers and shell builtins.

State and persistence behavior: mainly drives transient test files under TEST_DIR or SCRATCH_MNT.

Dependencies and integration points: Depends on xfstests common libraries, btrfs-progs and btrfs kernel feature gates. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: depends on xfstests harness requirements and exact golden-output filtering.

Test signals: successful script exit with xfstests filtered output.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/329 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/330 -->
# sources/test-tools/xfstests/tests/btrfs/330

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/btrfs/330_research.md`.

Source read: 54 lines, SHA256 prefix `b54447a997670636`.

Purpose: FS QA Test No. btrfs/330 Test mounting one subvolume as ro and another as rw.

Important APIs/types/functions: test tags `auto quick subvol`; common harness imports `. ./common/preamble`, `. ./common/filter.btrfs`; requirements/fixed gates `_fixed_by_kernel_commit cda7163d4e3d \`, `_require_scratch`; helper functions `_cleanup()`.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `_cleanup()`. Representative operation sequence: L28: _scratch_mkfs >> $seqres.full 2>&1 || _fail "mkfs failed"; L29: _scratch_mount; L32: $BTRFS_UTIL_PROG subvolume create $SCRATCH_MNT/foo | _filter_scratch; L33: $BTRFS_UTIL_PROG subvolume create $SCRATCH_MNT/bar | _filter_scratch; L35: _scratch_unmount; L40: _mount -t btrfs -o subvol=foo,ro $SCRATCH_DEV $TEST_DIR/$seq/foo; L41: _mount -t btrfs -o subvol=bar,rw $SCRATCH_DEV $TEST_DIR/$seq/bar.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; creates or manipulates btrfs subvolumes.

Dependencies and integration points: Depends on xfstests common libraries, btrfs-progs and btrfs kernel feature gates. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: is tied to specific kernel-regression behavior noted by fixed-by annotations.

Test signals: visible subtest labels include making sure foo is read only; making sure bar allows writes.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/330 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/331 -->
# sources/test-tools/xfstests/tests/btrfs/331

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/btrfs/331_research.md`.

Source read: 43 lines, SHA256 prefix `22a0a1276f6e1f6a`.

Purpose: FS QA Test 331 Test that btrfs does not recycle subvolume ids across remounts in a way that breaks squotas..

Important APIs/types/functions: test tags `auto quick qgroup snapshot`; common harness imports `. ./common/preamble`; requirements/fixed gates `_fixed_by_kernel_commit 2b8aa78cf127 \`, `_require_scratch_enable_simple_quota`; key variables `sv=$SCRATCH_MNT/sv`.

Control flow: The script is mostly straight-line after harness setup. Representative operation sequence: L16: _require_scratch_enable_simple_quota; L18: _scratch_mkfs >> $seqres.full; L19: _scratch_mount; L20: $BTRFS_UTIL_PROG quota enable --simple $SCRATCH_MNT; L25: $BTRFS_UTIL_PROG subvolume create $sv.$i >> $seqres.full; L28: $BTRFS_UTIL_PROG subvolume delete $sv.$i >> $seqres.full; L32: _scratch_cycle_mount; L35: $BTRFS_UTIL_PROG subvolume create $sv.BOOM >> $seqres.full; L37: $BTRFS_UTIL_PROG subvolume snapshot $sv.BOOM $sv.BOOM.$i >> $seqres.full.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; creates or manipulates btrfs subvolumes; persists snapshot roots and verifies their contents; changes quota/qgroup accounting state.

Dependencies and integration points: Depends on xfstests common libraries, btrfs-progs and btrfs kernel feature gates. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: quota accounting regressions can be silent until unmount or rescan; is tied to specific kernel-regression behavior noted by fixed-by annotations.

Test signals: no unexpected stdout beyond the golden quiet marker; visible subtest labels include Silence is golden.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/331 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/332 -->
# sources/test-tools/xfstests/tests/btrfs/332

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/btrfs/332_research.md`.

Source read: 66 lines, SHA256 prefix `7c5b8522659e7734`.

Purpose: FS QA Test No. btrfs/332 Test tune enabling and removing squotas on a live filesystem Import common functions. real QA test starts here.

Important APIs/types/functions: test tags `auto quick qgroup`; common harness imports `. ./common/preamble`, `. ./common/filter.btrfs`; requirements/fixed gates `_require_scratch_enable_simple_quota`, `_require_no_compress`, `_require_command "$BTRFS_TUNE_PROG" btrfstune`, `_require_fssum`, `_require_btrfs_dump_super`, `_require_btrfs_command inspect-internal dump-tree`; key variables `d1=$SCRATCH_MNT/d1`, `d2=$SCRATCH_MNT/d2`, `fssum_pre=$($FSSUM_PROG -A $SCRATCH_MNT)`, `fssum_post=$($FSSUM_PROG -A $SCRATCH_MNT)`, `fssum_pre=$($FSSUM_PROG -A $SCRATCH_MNT)`, `fssum_post=$($FSSUM_PROG -A $SCRATCH_MNT)`.

Control flow: The script is mostly straight-line after harness setup. Representative operation sequence: L16: _require_scratch_enable_simple_quota; L18: _require_command "$BTRFS_TUNE_PROG" btrfstune; L20: _require_btrfs_dump_super; L21: _require_btrfs_command inspect-internal dump-tree; L22: $BTRFS_TUNE_PROG --help 2>&1 | grep -wq -- '--enable-simple-quota' || \; L23: _notrun "$BTRFS_TUNE_PROG too old (must support --enable-simple-quota)"; L24: $BTRFS_TUNE_PROG --help 2>&1 | grep -wq -- '--remove-simple-quota' || \; L25: _notrun "$BTRFS_TUNE_PROG too old (must support --remove-simple-quota)"; L27: _scratch_mkfs >> $seqres.full 2>&1 || _fail "mkfs failed"; L28: _scratch_mount; L35: _run_fsstress -d $d1 -w -n 2000; L36: fssum_pre=$($FSSUM_PROG -A $SCRATCH_MNT); L39: _scratch_unmount; L40: $BTRFS_TUNE_PROG --enable-simple-quota $SCRATCH_DEV >> $seqres.full; L41: _check_btrfs_filesystem $SCRATCH_DEV; L42: _scratch_mount; L43: fssum_post=$($FSSUM_PROG -A $SCRATCH_MNT); L48: _run_fsstress -d $d2 -w -n 2000.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; changes quota/qgroup accounting state.

Dependencies and integration points: Depends on xfstests common libraries, btrfs-progs and btrfs kernel feature gates. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: quota accounting regressions can be silent until unmount or rescan.

Test signals: no unexpected stdout beyond the golden quiet marker; btrfs on-disk tree inspection; visible subtest labels include Silence is golden.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/332 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/333 -->
# sources/test-tools/xfstests/tests/btrfs/333

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/btrfs/333_research.md`.

Source read: 235 lines, SHA256 prefix `c6b6498241bd5937`.

Purpose: FS QA Test No. btrfs/333 Test btrfs encoded reads.

Important APIs/types/functions: test tags `auto quick compress rw io_uring ioctl`; common harness imports `. ./common/preamble`, `. ./common/filter`; requirements/fixed gates `_require_command src/btrfs_encoded_read`, `_require_command src/btrfs_encoded_write`, `_require_btrfs_iouring_encoded_read`, `_require_btrfs_no_nodatacow`, `_require_btrfs_no_nodatasum`; helper functions `do_encoded_read()`, `do_encoded_write()`, `test_file()`; key variables `sector_size=$(_scratch_btrfs_sectorsize)`.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `do_encoded_read()`, `do_encoded_write()`, `test_file()`. Representative operation sequence: L16: _require_btrfs_iouring_encoded_read; L20: _require_btrfs_no_nodatacow; L21: _require_btrfs_no_nodatasum; L82: local md5=`md5sum $datafile | cut -d ' ' -f 1`; L180: local md5=`md5sum $randfile | cut -d ' ' -f 1`; L198: _scratch_mkfs >> $seqres.full 2>&1 || _fail "mkfs failed"; L199: sector_size=$(_scratch_btrfs_sectorsize); L203: _scratch_mount "-o max_inline=2048".

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems.

Dependencies and integration points: Depends on xfstests common libraries, btrfs-progs and btrfs kernel feature gates. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: depends on xfstests harness requirements and exact golden-output filtering.

Test signals: no unexpected stdout beyond the golden quiet marker; matching file digests before and after remount/send/receive; visible subtest labels include btrfs encoded read failed with -EPERM; are you running as root?" \; btrfs encoded write failed with -EPERM; are you running as root?" \; Silence is golden.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/333 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/334 -->
# sources/test-tools/xfstests/tests/btrfs/334

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/btrfs/334_research.md`.

Source read: 21 lines, SHA256 prefix `af05f7193217a554`.

Purpose: FS QA Test 334 Verify sysfs knob input syntax for allocation/data/chunk_size.

Important APIs/types/functions: test tags `auto quick`; common harness imports `. ./common/preamble`, `. ./common/sysfs`, `. ./common/filter`; requirements/fixed gates `_require_test`, `_require_fs_sysfs_attr $TEST_DEV allocation/data/chunk_size`.

Control flow: The script is mostly straight-line after harness setup. The main operation is encoded through the xfstests helpers and shell builtins.

State and persistence behavior: mainly drives transient test files under TEST_DIR or SCRATCH_MNT.

Dependencies and integration points: Depends on xfstests common libraries, btrfs-progs and btrfs kernel feature gates. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: depends on xfstests harness requirements and exact golden-output filtering.

Test signals: successful script exit with xfstests filtered output.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/334 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/335 -->
# sources/test-tools/xfstests/tests/btrfs/335

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/btrfs/335_research.md`.

Source read: 62 lines, SHA256 prefix `8905db2d6754428a`.

Purpose: FS QA Test 335 Regression test for a kernel crash when converting a zoned BTRFS from metadata DUP to RAID1 and one of the devices has a non 0 write pointer position in the target zone..

Important APIs/types/functions: test tags `auto zone quick volume raid`; common harness imports `. ./common/preamble`, `. ./common/filter`; requirements/fixed gates `_fixed_by_kernel_commit b0c26f479926 \`, `_require_scratch_dev_pool 2`, `_require_zoned_device ${devs[0]}`, `_require_zoned_device ${devs[1]}`, `_require_command "$BLKZONE_PROG" blkzone`; key variables `zones=$($BLKZONE_PROG report ${devs[1]} | $AWK_PROG '/em/ { print $2 }' |\`.

Control flow: The script is mostly straight-line after harness setup. Representative operation sequence: L19: _require_scratch_dev_pool 2; L25: _scratch_mkfs >> $seqres.full 2>&1 || _fail "mkfs failed"; L26: _scratch_mount; L29: $XFS_IO_PROG -fc "pwrite 0 128M" $SCRATCH_MNT/test | _filter_xfs_io; L32: $BTRFS_UTIL_PROG device add ${devs[1]} $SCRATCH_MNT >> $seqres.full; L43: $XFS_IO_PROG -fdc "pwrite $(($zone << 9)) 4096" ${devs[1]} > /dev/null 2>&1; L47: $BTRFS_UTIL_PROG balance start -mconvert=raid1 $SCRATCH_MNT 2>&1 |\; L50: _scratch_unmount; L54: $BTRFS_UTIL_PROG device remove --force missing $SCRATCH_MNT >> $seqres.full; L55: $BTRFS_UTIL_PROG balance start --full-balance $SCRATCH_MNT >> $seqres.full; L58: $BTRFS_UTIL_PROG filesystem df $SCRATCH_MNT |\.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems.

Dependencies and integration points: Depends on xfstests common libraries, btrfs-progs and btrfs kernel feature gates, xfs_io workload commands. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: is tied to specific kernel-regression behavior noted by fixed-by annotations.

Test signals: successful script exit with xfstests filtered output.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/335 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/336 -->
# sources/test-tools/xfstests/tests/btrfs/336

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/btrfs/336_research.md`.

Source read: 35 lines, SHA256 prefix `320c67fc478158d2`.

Purpose: FS QA Test 336 Make sure read-only scrub won't cause NULL pointer dereference with rescue=idatacsums mount option.

Important APIs/types/functions: test tags `auto scrub quick`; common harness imports `. ./common/preamble`; requirements/fixed gates `_fixed_by_kernel_commit 6aecd91a5c5b \`, `_require_scratch`.

Control flow: The script is mostly straight-line after harness setup. Representative operation sequence: L17: _scratch_mkfs >> $seqres.full; L19: _try_scratch_mount "-o ro,rescue=ignoredatacsums" > /dev/null 2>&1 ||; L23: $BTRFS_UTIL_PROG scrub start -Br $SCRATCH_MNT >> $seqres.full 2>&1; L29: _scratch_unmount.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems.

Dependencies and integration points: Depends on xfstests common libraries, btrfs-progs and btrfs kernel feature gates. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: is tied to specific kernel-regression behavior noted by fixed-by annotations.

Test signals: no unexpected stdout beyond the golden quiet marker; visible subtest labels include read-only scrub should fail but didn't; Silence is golden.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/336 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/337 -->
# sources/test-tools/xfstests/tests/btrfs/337

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/btrfs/337_research.md`.

Source read: 53 lines, SHA256 prefix `632c209d0644be06`.

Purpose: FS QA Test 337 Test compressed read with shared extents, especially for bs < ps cases..

Important APIs/types/functions: test tags `auto quick compress clone`; common harness imports `. ./common/preamble`, `. ./common/reflink`; requirements/fixed gates `_fixed_by_kernel_commit 9786531399a6 \`, `_require_btrfs_support_sectorsize 4096`, `_require_scratch_reflink`.

Control flow: The script is mostly straight-line after harness setup. Representative operation sequence: L17: _require_btrfs_support_sectorsize 4096; L18: _require_scratch_reflink; L22: _scratch_mkfs -s 4k >> $seqres.full || _fail "make a btrfs with -s 4k"; L23: _scratch_mount "-o compress"; L26: $XFS_IO_PROG -f -c "pwrite -S 0x0f 0 32K" \; L37: $XFS_IO_PROG -f -c "reflink $SCRATCH_MNT/base 32K 0 32K" \; L46: _scratch_cycle_mount.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems.

Dependencies and integration points: Depends on xfstests common libraries, btrfs-progs and btrfs kernel feature gates, xfs_io workload commands. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: is tied to specific kernel-regression behavior noted by fixed-by annotations.

Test signals: visible subtest labels include Reflink source:; Before mount cycle:; After mount cycle:.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/337 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/338 -->
# sources/test-tools/xfstests/tests/btrfs/338

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/btrfs/338_research.md`.

Source read: 93 lines, SHA256 prefix `0e13ca2dcd364f49`.

Purpose: FS QA Test 338 Test that an incremental send works after we removed directories that have large number of hardlinks for the same file (so that we have extrefs)..

Important APIs/types/functions: test tags `auto quick send`; common harness imports `. ./common/preamble`; requirements/fixed gates `_require_test`, `_require_scratch`, `_require_fssum`, `_fixed_by_kernel_commit 1fabe43b4e1a \`; helper functions `_cleanup()`; key variables `send_files_dir=$TEST_DIR/btrfs-test-$seq`, `first_stream="$send_files_dir/1.send"`, `second_stream="$send_files_dir/2.send"`, `first_fssum="$send_files_dir/snap1.fssum"`, `second_fssum="$send_files_dir/snap2.fssum"`.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `_cleanup()`. Representative operation sequence: L37: _scratch_mkfs >> $seqres.full 2>&1 || _fail "first mkfs failed"; L38: _scratch_mount; L66: _btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/snap1; L72: _btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/snap2; L74: _btrfs send -f $first_stream $SCRATCH_MNT/snap1; L75: _btrfs send -f $second_stream -p $SCRATCH_MNT/snap1 $SCRATCH_MNT/snap2; L77: $FSSUM_PROG -A -f -w $first_fssum $SCRATCH_MNT/snap1; L78: $FSSUM_PROG -A -f -w $second_fssum -x $SCRATCH_MNT/snap2/snap1 \; L82: _scratch_unmount; L83: _scratch_mkfs >> $seqres.full 2>&1 || _fail "second mkfs failed"; L84: _scratch_mount; L86: _btrfs receive -f $first_stream $SCRATCH_MNT; L87: _btrfs receive -f $second_stream $SCRATCH_MNT; L89: $FSSUM_PROG -r $first_fssum $SCRATCH_MNT/snap1; L90: $FSSUM_PROG -r $second_fssum $SCRATCH_MNT/snap2.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; creates or manipulates btrfs subvolumes; persists snapshot roots and verifies their contents; creates send streams and receives them into a fresh filesystem.

Dependencies and integration points: Depends on xfstests common libraries, btrfs-progs and btrfs kernel feature gates. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: is tied to specific kernel-regression behavior noted by fixed-by annotations.

Test signals: successful script exit with xfstests filtered output.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/338 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/339 -->
# sources/test-tools/xfstests/tests/btrfs/339

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/btrfs/339_research.md`.

Source read: 32 lines, SHA256 prefix `a89b8cbbbda413db`.

Purpose: FS QA Test 339 Test btrfs receive dump stream from different user.

Important APIs/types/functions: test tags `auto quick send snapshot`; common harness imports `. ./common/preamble`, `. ./common/filter`; requirements/fixed gates `_require_scratch`, `_require_user`; key variables `stream=$tmp.fsv.ss`.

Control flow: The script is mostly straight-line after harness setup. Representative operation sequence: L20: _scratch_mkfs >> $seqres.full 2>&1 || _fail "mkfs failed"; L21: _scratch_mount; L25: _btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/snap; L26: _btrfs send -f $stream $SCRATCH_MNT/snap; L28: _su $qa_user -c "$BTRFS_UTIL_PROG receive --dump -f $stream" >> $seqres.full.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; creates or manipulates btrfs subvolumes; persists snapshot roots and verifies their contents; creates send streams and receives them into a fresh filesystem.

Dependencies and integration points: Depends on xfstests common libraries, btrfs-progs and btrfs kernel feature gates. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: depends on xfstests harness requirements and exact golden-output filtering.

Test signals: no unexpected stdout beyond the golden quiet marker; visible subtest labels include Silence is golden.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/339 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/340 -->
# sources/test-tools/xfstests/tests/btrfs/340

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/btrfs/340_research.md`.

Source read: 45 lines, SHA256 prefix `64efc1d6db416d08`.

Purpose: FS QA Test No. 340 Make sure when doing a quick inherit for snapshot, all parent qgroups including direct and indirect parents are properly updated..

Important APIs/types/functions: test tags `auto quick qgroup`; common harness imports `. ./common/preamble`; requirements/fixed gates `_fixed_by_kernel_commit 68d4b3fa18d7 \`, `_require_scratch`, `_require_btrfs_qgroup_report`, `_require_scratch_qgroup`; key variables `subvolid=$(_btrfs_get_subvolid $SCRATCH_MNT subv1)`.

Control flow: The script is mostly straight-line after harness setup. Representative operation sequence: L18: _require_btrfs_qgroup_report; L21: _require_scratch_qgroup; L22: _scratch_mount; L26: _btrfs subvolume create $SCRATCH_MNT/subv1; L27: subvolid=$(_btrfs_get_subvolid $SCRATCH_MNT subv1); L28: _btrfs qgroup create 1/1 $SCRATCH_MNT; L29: _btrfs qgroup create 2/1 $SCRATCH_MNT; L30: _btrfs qgroup assign 1/1 2/1 $SCRATCH_MNT; L31: _btrfs qgroup assign 0/$subvolid 1/1 $SCRATCH_MNT; L35: _btrfs qgroup show -p --sync $SCRATCH_MNT >> $seqres.full; L40: _btrfs subv snap -i 1/1 $SCRATCH_MNT/subv1 $SCRATCH_MNT/snap1; L42: _btrfs qgroup show -p --sync $SCRATCH_MNT >> $seqres.full.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; creates or manipulates btrfs subvolumes; persists snapshot roots and verifies their contents; changes quota/qgroup accounting state.

Dependencies and integration points: Depends on xfstests common libraries, btrfs-progs and btrfs kernel feature gates. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: quota accounting regressions can be silent until unmount or rescan; is tied to specific kernel-regression behavior noted by fixed-by annotations.

Test signals: no unexpected stdout beyond the golden quiet marker; visible subtest labels include Silence is golden.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/340 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/341 -->
# sources/test-tools/xfstests/tests/btrfs/341

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/btrfs/341_research.md`.

Source read: 73 lines, SHA256 prefix `e863503854b78d9d`.

Purpose: FS QA Test 341 Test renaming one directory over another one that has a subvolume inside it and fsync a file in the other directory that was previously renamed. We want to verify that after a power failure we are able to mount the filesystem and it has the correct content (all renames visible)..

Important APIs/types/functions: test tags `auto quick subvol rename log`; common harness imports `. ./common/preamble`, `. ./common/filter`, `. ./common/dmflakey`, `. ./common/renameat2`; requirements/fixed gates `_require_scratch`, `_require_dm_target flakey`, `_require_renameat2 exchange`, `_fixed_by_kernel_commit 7ba0b6461bc4 \`, `_require_metadata_journaling $SCRATCH_DEV`; helper functions `_cleanup()`.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `_cleanup()`. Representative operation sequence: L24: . ./common/renameat2; L28: _require_renameat2 exchange; L33: _scratch_mkfs >>$seqres.full 2>&1 || _fail "mkfs failed"; L36: _scratch_mount; L44: _btrfs subvolume create $SCRATCH_MNT/dir2/subvol; L47: _scratch_sync; L54: $here/src/renameat2 -x $SCRATCH_MNT/dir1 $SCRATCH_MNT/dir2; L63: $XFS_IO_PROG -c "fsync" $SCRATCH_MNT/dir2/bar.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; creates or manipulates btrfs subvolumes; uses dm-flakey to simulate power loss.

Dependencies and integration points: Depends on xfstests common libraries, btrfs-progs and btrfs kernel feature gates, xfs_io workload commands. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: is tied to specific kernel-regression behavior noted by fixed-by annotations.

Test signals: successful script exit with xfstests filtered output.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/341 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/342 -->
# sources/test-tools/xfstests/tests/btrfs/342

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/btrfs/342_research.md`.

Source read: 103 lines, SHA256 prefix `2b8b8103cd2bd655`.

Purpose: FS QA Test No. 342 Test free space tree mount options, for newer kernels with only 2 options involed: - No space cache - New (default) v2 space cache.

Important APIs/types/functions: test tags `auto quick`; common harness imports `. ./common/preamble`; requirements/fixed gates `_require_scratch`, `_require_btrfs_command inspect-internal dump-super`, `_require_btrfs_fs_feature free_space_tree`, `_require_btrfs_no_block_group_tree`; helper functions `mkfs_nocache()`, `mkfs_v2()`, `check_fst_compat()`; key variables `compat_ro="$($BTRFS_UTIL_PROG inspect-internal dump-super "$SCRATCH_DEV" | \`.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `mkfs_nocache()`, `mkfs_v2()`, `check_fst_compat()`. Representative operation sequence: L15: _require_btrfs_command inspect-internal dump-super; L16: _require_btrfs_fs_feature free_space_tree; L20: _require_btrfs_no_block_group_tree; L24: _scratch_mkfs >/dev/null 2>&1; L25: _scratch_mount -o clear_cache,nospace_cache; L26: _scratch_unmount; L31: _scratch_mkfs >/dev/null 2>&1; L32: _scratch_mount -o space_cache=v2; L33: _scratch_unmount; L38: compat_ro="$($BTRFS_UTIL_PROG inspect-internal dump-super "$SCRATCH_DEV" | \; L58: _scratch_mount -o nospace_cache; L60: _scratch_unmount; L64: _scratch_mount -o space_cache=v2; L66: _scratch_unmount; L76: _try_scratch_mount -o nospace_cache >/dev/null 2>&1 || echo "mount failed"; L80: _scratch_mount; L82: _scratch_unmount; L83: _scratch_mount -o space_cache=v2.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems.

Dependencies and integration points: Depends on xfstests common libraries, btrfs-progs and btrfs kernel feature gates. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: depends on xfstests harness requirements and exact golden-output filtering.

Test signals: visible subtest labels include free space tree is enabled; free space tree is disabled; Using no space cache; Enabling free space tree; Trying to mount without free space tree; Mounting existing free space tree.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/342 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/343 -->
# sources/test-tools/xfstests/tests/btrfs/343

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/btrfs/343_research.md`.

Source read: 48 lines, SHA256 prefix `83f0a776d34a2d77`.

Purpose: FS QA Test 343 A regression test to make sure a single-block write at file offset 0 won't incorrectly mark the inode incompressible..

Important APIs/types/functions: test tags `auto quick compress`; common harness imports `. ./common/preamble`; requirements/fixed gates `_require_scratch`, `_require_btrfs_command inspect-internal dump-tree`, `_fixed_by_kernel_commit xxxxxxxxxxxx \`; key variables `blocksize=$(_get_file_block_size $SCRATCH_MNT)`, `ino=$(stat -c "%i" $SCRATCH_MNT/foobar)`.

Control flow: The script is mostly straight-line after harness setup. Representative operation sequence: L14: _require_btrfs_command inspect-internal dump-tree; L19: _scratch_mkfs >>$seqres.full 2>&1; L20: _scratch_mount "-o compress,max_inline=2048"; L28: $XFS_IO_PROG -f -c "truncate $((2 * $blocksize))" -c "pwrite 0 2k" -c sync \; L31: _scratch_unmount; L34: $BTRFS_UTIL_PROG inspect-internal dump-tree -t 5 $SCRATCH_DEV >> $seqres.full; L37: $BTRFS_UTIL_PROG inspect-internal dump-tree -t 5 $SCRATCH_DEV |\; L42: $BTRFS_UTIL_PROG inspect-internal dump-tree -t 5 $SCRATCH_DEV |\.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems.

Dependencies and integration points: Depends on xfstests common libraries, btrfs-progs and btrfs kernel feature gates, xfs_io workload commands. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: has a placeholder fixed-by commit annotation; parses btrfs-progs textual dump output; is tied to specific kernel-regression behavior noted by fixed-by annotations.

Test signals: no unexpected stdout beyond the golden quiet marker; btrfs on-disk tree inspection; visible subtest labels include Silence is golden.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/343 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/344 -->
# sources/test-tools/xfstests/tests/btrfs/344

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/btrfs/344_research.md`.

Source read: 53 lines, SHA256 prefix `2d87e04304d90d16`.

Purpose: FS QA Test 344 Check if a failed inline attempt for compression write will mark the whole inode as incompressible.

Important APIs/types/functions: test tags `auto quick compress`; common harness imports `. ./common/preamble`; requirements/fixed gates `_require_scratch`, `_require_btrfs_command inspect-internal dump-tree`, `_fixed_by_kernel_commit xxxxxxxxxxxx \`; key variables `blocksize=$(_get_file_block_size $SCRATCH_MNT)`, `ino=$(stat -c "%i" $SCRATCH_MNT/foobar)`.

Control flow: The script is mostly straight-line after harness setup. Representative operation sequence: L14: _require_btrfs_command inspect-internal dump-tree; L19: _scratch_mkfs >>$seqres.full 2>&1; L23: _scratch_mount "-o compress,max_inline=4"; L34: $XFS_IO_PROG -f -c "pwrite 0 $(( $blocksize / 2 ))" -c sync \; L37: _scratch_unmount; L40: $BTRFS_UTIL_PROG inspect-internal dump-tree -t 5 $SCRATCH_DEV >> $seqres.full; L43: $BTRFS_UTIL_PROG inspect-internal dump-tree -t 5 $SCRATCH_DEV |\; L48: $BTRFS_UTIL_PROG inspect-internal dump-tree -t 5 $SCRATCH_DEV |\.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems.

Dependencies and integration points: Depends on xfstests common libraries, btrfs-progs and btrfs kernel feature gates, xfs_io workload commands. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: has a placeholder fixed-by commit annotation; parses btrfs-progs textual dump output; is tied to specific kernel-regression behavior noted by fixed-by annotations.

Test signals: no unexpected stdout beyond the golden quiet marker; btrfs on-disk tree inspection; visible subtest labels include Silence is golden.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/344 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/345 -->
# sources/test-tools/xfstests/tests/btrfs/345

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/btrfs/345_research.md`.

Source read: 73 lines, SHA256 prefix `4844a985a6e23c7d`.

Purpose: FS QA Test 345 Test that we can create a large number of snapshots of a received subvolume without triggering a transaction abort due to leaf item overflow. Also check that we are able to delete the snapshots and use the last one for an incremental send/receive despite an item overflow when updating the uuid tree to insert a BTRFS_UUID_KEY_RECEIVED_SUBVOL item..

Important APIs/types/functions: test tags `auto quick subvol send snapshot`; common harness imports `. ./common/preamble`; requirements/fixed gates `_require_scratch`, `_require_btrfs_support_sectorsize 4096`, `_require_btrfs_command "property"`, `_fixed_by_kernel_commit e1b18b959025 \`; key variables `total=$(( 1000 * LOAD_FACTOR ))`, `last_snap="${SCRATCH_MNT}/snaps/sv_${total}"`.

Control flow: The script is mostly straight-line after harness setup. Representative operation sequence: L17: _require_btrfs_support_sectorsize 4096; L18: _require_btrfs_command "property"; L24: _scratch_mkfs -n 4K >> $seqres.full 2>&1 || _fail "mkfs failed"; L25: _scratch_mount; L28: _btrfs subvolume create $SCRATCH_MNT/sv; L32: _btrfs property set $SCRATCH_MNT/sv ro true; L38: _btrfs send -f $SCRATCH_MNT/send.stream $SCRATCH_MNT/sv; L39: _btrfs receive -f $SCRATCH_MNT/send.stream $SCRATCH_MNT/snaps; L46: _btrfs subvolume snapshot -r $SCRATCH_MNT/snaps/sv $SCRATCH_MNT/snaps/sv_$i; L52: _btrfs subvolume snapshot $last_snap $SCRATCH_MNT/snaps/sv_last_as_parent; L54: _btrfs property set $SCRATCH_MNT/snaps/sv_last_as_parent ro true; L59: _btrfs send -f $SCRATCH_MNT/inc_send.stream -p $last_snap \; L61: _btrfs receive -f $SCRATCH_MNT/inc_send.stream $SCRATCH_MNT/; L64: diff $SCRATCH_MNT/snaps/sv_last_as_parent/bar $SCRATCH_MNT/sv_last_as_parent/bar; L68: _btrfs subvolume delete $SCRATCH_MNT/snaps/sv_$i.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; creates or manipulates btrfs subvolumes; persists snapshot roots and verifies their contents; creates send streams and receives them into a fresh filesystem.

Dependencies and integration points: Depends on xfstests common libraries, btrfs-progs and btrfs kernel feature gates. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: runtime and object count scale with the harness load factor; is tied to specific kernel-regression behavior noted by fixed-by annotations.

Test signals: no unexpected stdout beyond the golden quiet marker; byte-for-byte compare of copied or restored data; visible subtest labels include Silence is golden.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/345 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/346 -->
# sources/test-tools/xfstests/tests/btrfs/346

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/btrfs/346_research.md`.

Source read: 95 lines, SHA256 prefix `cd6c498889f7b8b0`.

Purpose: FS QA Test 346 Test that if we create a high number of files with a name that results in a hash collision, the filesystem is not turned to RO due to a transaction abort. This could be exploited by malicious users to disrupt a system..

Important APIs/types/functions: test tags `auto quick subvol`; common harness imports `. ./common/preamble`; requirements/fixed gates `_require_scratch`, `_require_btrfs_support_sectorsize 4096`, `_fixed_by_kernel_commit 2d1ababdedd4 \`.

Control flow: The script is mostly straight-line after harness setup. Representative operation sequence: L15: _require_btrfs_support_sectorsize 4096; L22: _scratch_mkfs -n 4K >> $seqres.full 2>&1 || _fail "mkfs failed"; L23: _scratch_mount; L76: _scratch_cycle_mount; L82: $BTRFS_UTIL_PROG subvolume create \; L92: _scratch_cycle_mount.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; creates or manipulates btrfs subvolumes.

Dependencies and integration points: Depends on xfstests common libraries, btrfs-progs and btrfs kernel feature gates. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: is tied to specific kernel-regression behavior noted by fixed-by annotations.

Test signals: successful script exit with xfstests filtered output.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/346 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/347 -->
# sources/test-tools/xfstests/tests/btrfs/347

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/btrfs/347_research.md`.

Source read: 66 lines, SHA256 prefix `b81a86da86bc9d6d`.

Purpose: FS QA Test 347 Test that using the received subvol ioctl to set a received UUID on a root does not trigger a transaction abort (and turn the filesystem to RO mode) if a user abuses by assigning the same received UUID to a large number of subvolumes..

Important APIs/types/functions: test tags `auto quick subvol`; common harness imports `. ./common/preamble`; requirements/fixed gates `_require_test_program t_btrfs_received_uuid_ioctl`, `_require_scratch`, `_require_btrfs_support_sectorsize 4096`, `_fixed_by_kernel_commit 87f2c46003fc \`; key variables `num_subvols=496`.

Control flow: The script is mostly straight-line after harness setup. Representative operation sequence: L15: _require_test_program t_btrfs_received_uuid_ioctl; L17: _require_btrfs_support_sectorsize 4096; L23: _scratch_mkfs -n 4K >> $seqres.full 2>&1 || _fail "mkfs failed"; L24: _scratch_mount; L41: _btrfs subvolume create $SCRATCH_MNT/sv_$i; L45: $here/src/t_btrfs_received_uuid_ioctl \; L51: _btrfs subvolume create $SCRATCH_MNT/sv_last; L52: $here/src/t_btrfs_received_uuid_ioctl \; L62: _scratch_cycle_mount.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; creates or manipulates btrfs subvolumes; creates send streams and receives them into a fresh filesystem.

Dependencies and integration points: Depends on xfstests common libraries, btrfs-progs and btrfs kernel feature gates. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: is tied to specific kernel-regression behavior noted by fixed-by annotations.

Test signals: successful script exit with xfstests filtered output.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/347 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/Makefile -->
# sources/test-tools/xfstests/tests/btrfs/Makefile

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/btrfs/Makefile_research.md`.

Source read: 24 lines, SHA256 prefix `bf36f162ed492618`.

Purpose: package-install rules for the xfstests `btrfs` test directory. It builds the local `group.list` metadata and installs runnable tests plus expected output files into the package test tree.

Important APIs/types/functions: the file includes `include/builddefs`, `include/buildgrouplist`, and `$(BUILDRULES)`. Important variables are `TOPDIR`, `TARGET_DIR`, and `DIRT`. The exported targets are `default`, `install`, `install-dev`, and `install-lib`.

Control flow: `default` depends on `$(DIRT)`, which is the generated `group.list`. The `install` target creates `$(TARGET_DIR)`, installs `$(TESTS)` executable, installs `group.list` read-only, and installs `$(OUTFILES)` as read-only golden-output files. `install-dev` and `install-lib` are intentionally empty.

State and persistence behavior: persists directory contents under `$(PKG_LIB_DIR)/$(TESTS_DIR)/...` during package installation and leaves `group.list` as a build artifact. It does not run tests or touch scratch devices.

Dependencies and integration: integrated with the xfstests build system through `builddefs`, `buildgrouplist`, and common build rules. It depends on the harness variables that enumerate tests and `.out` files.

Risks: install permissions are fixed at 0755 for tests and 0644 for metadata/output; missing generated group lists or stale `$(TESTS)` expansion would omit cases from packaged runs.

Test signals: `make -C tests/btrfs install DESTDIR=...` should create the expected tree with executable test scripts, `group.list`, and output files.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ceph/001 -->
# sources/test-tools/xfstests/tests/ceph/001

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ceph/001_research.md`.

Source read: 288 lines, SHA256 prefix `a59e8c1e779b43a7`.

Purpose: FS QA Test No. ceph/001 Test remote copy operation (CEPH_OSD_OP_COPY_FROM) with several combinations of both object sizes and copy sizes. It also uses several combinations of copy ranges. For example, copying the 1st object in the src file into 1) the beginning (1st object) of dst file, 2) the end (last object) of dst file and 3) the middle of the dst file. get standard environment.

Important APIs/types/functions: test tags `auto quick copy_range`; common harness imports `. ./common/preamble`, `. common/filter`, `. common/attr`, `. common/reflink`; requirements/fixed gates `_require_debugfs`, `_require_xfs_io_command "copy_range"`, `_exclude_test_mount_option "test_dummy_encryption"`, `_require_attrs`, `_require_test`; helper functions `check_range()`, `get_copyfrom_total_copies()`, `get_copyfrom_total_size()`, `check_copyfrom_metrics()`, `run_copy_range_tests()`; key variables `workdir=$TEST_DIR/test-$seq`, `cluster_fsid=$(_ceph_get_cluster_fsid)`, `client_id=$(_ceph_get_client_id)`, `metrics_dir="$DEBUGFS_MNT/ceph/$cluster_fsid.$client_id/metrics"`, `total=$(grep copyfrom $metrics_dir/size | tr -s '[:space:]' | cut -d ' ' -f 2)`, `total=$(grep copyfrom $metrics_dir/size | tr -s '[:space:]' | cut -d ' ' -f 6)`, `sum=$(($c0+$copies))`, `sum=$(($s0+$copies*$objsz))`, `total_copies=$(get_copyfrom_total_copies)`, `total_size=$(get_copyfrom_total_size)`.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `check_range()`, `get_copyfrom_total_copies()`, `get_copyfrom_total_size()`, `check_copyfrom_metrics()`, `run_copy_range_tests()`. Representative operation sequence: L14: _begin_fstest auto quick copy_range; L21: _require_debugfs; L22: _require_xfs_io_command "copy_range"; L23: _exclude_test_mount_option "test_dummy_encryption"; L31: cluster_fsid=$(_ceph_get_cluster_fsid); L32: client_id=$(_ceph_get_client_id); L91: return # skip metrics check if debugfs isn't mounted; L107: run_copy_range_tests(); L119: _ceph_create_file_layout $file $objsz 1 $objsz; L120: _ceph_create_file_layout $copy $objsz 1 $objsz; L121: _ceph_create_file_layout $dest $objsz 1 $objsz; L124: $XFS_IO_PROG -c "pwrite -S 0x61 0 $objsz" $file >> $seqres.full 2>&1; L125: $XFS_IO_PROG -c "pwrite -S 0x62 $objsz $objsz" $file >> $seqres.full 2>&1; L126: $XFS_IO_PROG -c "pwrite -S 0x63 $(($objsz * 2)) $objsz" $file >> $seqres.full 2>&1; L130: $XFS_IO_PROG -c "copy_range -s 0 -d 0 -l $(($objsz * 3)) $file" "$copy"; L131: cmp $file $copy; L135: $XFS_IO_PROG -c "pwrite -S 0x64 0 $(($objsz * 3))" $dest >> $seqres.full 2>&1; L138: $XFS_IO_PROG -c "copy_range -s 0 -d 0 -l $objsz $file" "$dest".

State and persistence behavior: edits or inspects ext metadata directly.

Dependencies and integration points: Depends on xfstests common libraries, xfs_io workload commands, CephFS mount, xattrs, debugfs metrics, or snapshot helpers. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: depends on xfstests harness requirements and exact golden-output filtering.

Test signals: byte-for-byte compare of copied or restored data; visible subtest labels include Copy whole file (3 objects):; aaaa|bbbb|cccc => aaaa|bbbb|cccc; Copy single object to beginning:; dddd|dddd|dddd => aaaa|dddd|dddd; aaaa|dddd|dddd => bbbb|dddd|dddd; bbbb|dddd|dddd => cccc|dddd|dddd.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ceph/001 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ceph/002 -->
# sources/test-tools/xfstests/tests/ceph/002

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ceph/002_research.md`.

Source read: 64 lines, SHA256 prefix `525809cd9a60fcc5`.

Purpose: FS QA Test No. ceph/002 Test bug found while testing copy_file_range. This bug was an issue with how the OSDs handled the truncate_seq, copying it from the original object into the destination object. This test ensures the kernel client correctly handles fixed/non-fixed OSDs. The bug was tracked here: https://tracker.ceph.com/issues/37378 The most relevant commits are: ceph OSD: dcd6a99ef9f5 ("osd: add new 'copy-from2' operation") linux kernel: 78beb0ff2fec ("ceph: use copy-from2 op in copy_file_range") get standard environment.

Important APIs/types/functions: test tags `auto quick copy_range`; common harness imports `. ./common/preamble`, `. common/filter`, `. common/attr`; requirements/fixed gates `_require_xfs_io_command "copy_range"`, `_exclude_test_mount_option "test_dummy_encryption"`, `_require_attrs`, `_require_test`; key variables `workdir=$TEST_DIR/test-$seq`, `objsz=4194304`, `file="$workdir/file-$objsz"`, `dest="$workdir/dest-$objsz"`.

Control flow: The script is mostly straight-line after harness setup. Representative operation sequence: L23: _begin_fstest auto quick copy_range; L30: _require_xfs_io_command "copy_range"; L31: _exclude_test_mount_option "test_dummy_encryption"; L45: _ceph_create_file_layout $file $objsz 1 $objsz; L46: _ceph_create_file_layout $dest $objsz 1 $objsz; L49: $XFS_IO_PROG -c "pwrite -S 0x61 0 $objsz" $file >> $seqres.full 2>&1; L50: $XFS_IO_PROG -c "pwrite -S 0x62 $objsz $objsz" $file >> $seqres.full 2>&1; L51: $XFS_IO_PROG -c "pwrite -S 0x63 $(($objsz * 2)) $objsz" $file >> $seqres.full 2>&1; L53: $XFS_IO_PROG -c "pwrite -S 0x64 0 $(($objsz * 3))" $dest >> $seqres.full 2>&1; L55: $XFS_IO_PROG -c "truncate 0" $dest >> $seqres.full 2>&1; L58: $XFS_IO_PROG -c "copy_range -s 0 -d 0 -l $(($objsz * 3)) $file" "$dest".

State and persistence behavior: mainly drives transient test files under TEST_DIR or SCRATCH_MNT.

Dependencies and integration points: Depends on xfstests common libraries, xfs_io workload commands, CephFS mount, xattrs, debugfs metrics, or snapshot helpers. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: depends on xfstests harness requirements and exact golden-output filtering.

Test signals: successful script exit with xfstests filtered output.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ceph/002 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ceph/003 -->
# sources/test-tools/xfstests/tests/ceph/003

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ceph/003_research.md`.

Source read: 101 lines, SHA256 prefix `eeb5f0cada77df0b`.

Purpose: FS QA Test No. ceph/005 Test copy_file_range with infile = outfile get standard environment.

Important APIs/types/functions: test tags `auto quick copy_range`; common harness imports `. ./common/preamble`, `. common/filter`, `. common/attr`, `. common/reflink`; requirements/fixed gates `_require_xfs_io_command "copy_range"`, `_exclude_test_mount_option "test_dummy_encryption"`, `_require_attrs`, `_require_test`; helper functions `check_range()`; key variables `workdir=$TEST_DIR/test-$seq`, `objsz=4194304`, `halfobj=$(($objsz / 2))`, `file="$workdir/file-$objsz"`, `copy="$workdir/copy-$objsz"`, `dest="$workdir/dest-$objsz"`, `backup="$file.backup"`.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `check_range()`. Representative operation sequence: L10: _begin_fstest auto quick copy_range; L18: _require_xfs_io_command "copy_range"; L19: _exclude_test_mount_option "test_dummy_encryption"; L45: _ceph_create_file_layout $file $objsz 1 $objsz; L46: _ceph_create_file_layout $backup $objsz 1 $objsz; L48: $XFS_IO_PROG -c "pwrite -S 0x61 0 $objsz" $file >> $seqres.full 2>&1; L49: $XFS_IO_PROG -c "pwrite -S 0x62 $objsz $objsz" $file >> $seqres.full 2>&1; L50: $XFS_IO_PROG -c "pwrite -S 0x63 $(($objsz * 2)) $objsz" $file >> $seqres.full 2>&1; L56: $XFS_IO_PROG -c "copy_range -s 0 -d $(($objsz * 2)) -l $objsz $file" "$file"; L63: $XFS_IO_PROG -c "copy_range -s $objsz -d 0 -l $objsz $file" "$file"; L69: $XFS_IO_PROG -c "copy_range -s $(($objsz * 2)) -d $objsz -l $objsz $file" "$file"; L76: $XFS_IO_PROG -c "copy_range -s 0 -d $(($objsz + $halfobj)) -l $objsz $file" "$file"; L84: $XFS_IO_PROG -c "copy_range -s $halfobj -d $(($objsz + $halfobj)) -l $objsz $file" "$file"; L93: $XFS_IO_PROG -c "copy_range -s $halfobj -d $(($objsz * 2)) -l $objsz $file" "$file".

State and persistence behavior: mainly drives transient test files under TEST_DIR or SCRATCH_MNT.

Dependencies and integration points: Depends on xfstests common libraries, xfs_io workload commands, CephFS mount, xattrs, debugfs metrics, or snapshot helpers. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: depends on xfstests harness requirements and exact golden-output filtering.

Test signals: visible subtest labels include Copy single object to the end:; aaaa|bbbb|cccc => aaaa|bbbb|aaaa; Copy single object to the beginning:; aaaa|bbbb|aaaa => bbbb|bbbb|aaaa; Copy single object to the middle:; bbbb|bbbb|aaaa => bbbb|aaaa|aaaa.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ceph/003 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ceph/004 -->
# sources/test-tools/xfstests/tests/ceph/004

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ceph/004_research.md`.

Source read: 101 lines, SHA256 prefix `4dcb0f762b1cdb20`.

Purpose: FS QA Test 004 Tests a bug fix found in cephfs quotas handling. Here's a simplified testcase that *should* fail: mkdir files limit truncate files/file -s 10G setfattr limit -n ceph.quota.max_bytes -v 1048576 mv files limit/ Because we're creating a new file and truncating it, we have Fx caps and thus the truncate operation will be cached. This prevents the MDSs from updating the quota realms and thus the client will allow the above rename(2) to happen. The bug resulted in dropping support for cross quota-realms renames, reverting kernel commit dffdcd71458e ("ceph: allow rename operation under different quota realms"). So, the above test will now fail with a -EXDEV or, in the future (when we have a proper fix), with -EDQUOT. This bug was tracker here: https://tracker.ceph.com/issues/48203 Import common functions..

Important APIs/types/functions: test tags `auto quick quota`; common harness imports `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`; requirements/fixed gates `_require_attrs`, `_require_test`, `_require_test_program "rename"`, `_require_ceph_vxattr_caps # we need to get file capabilities`; helper functions `get_ceph_caps()`, `check_Fs_caps()`; key variables `workdir=$TEST_DIR/test-$seq`, `orig1=$workdir/orig1`, `orig2=$workdir/orig2`, `file1=$orig1/file`, `file2=$orig2/file`, `dest=$workdir/dest`, `caps=`get_ceph_caps $1``, `Fs=$((1 << 8))`.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `get_ceph_caps()`, `check_Fs_caps()`. Representative operation sequence: L41: _require_ceph_vxattr_caps # we need to get file capabilities; L58: get_ceph_caps(); L67: caps=`get_ceph_caps $1`; L86: $XFS_IO_PROG -f -c "truncate 10G" $file1; L92: $XFS_IO_PROG -f -c "truncate 10G" $file2.

State and persistence behavior: changes quota/qgroup accounting state.

Dependencies and integration points: Depends on xfstests common libraries, xfs_io workload commands, CephFS mount, xattrs, debugfs metrics, or snapshot helpers. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: quota accounting regressions can be silent until unmount or rescan.

Test signals: no unexpected stdout beyond the golden quiet marker; visible subtest labels include Silence is golden.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ceph/004 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ceph/005 -->
# sources/test-tools/xfstests/tests/ceph/005

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ceph/005_research.md`.

Source read: 39 lines, SHA256 prefix `b749236e468d972d`.

Purpose: FS QA Test 005 Make sure statfs reports correct total size when: 1. using a directory with 'max_byte' quota as base for a mount 2. using a subdirectory of the above directory with 'max_files' quota.

Important APIs/types/functions: test tags `auto quick quota`; common harness imports `. ./common/preamble`; requirements/fixed gates `_require_scratch`, `_exclude_test_mount_option "test_dummy_encryption"`; key variables `quota=$((2 ** 30)) # 1G`, `SCRATCH_DEV_ORIG="$SCRATCH_DEV"`, `SCRATCH_DEV="$SCRATCH_DEV/quota-dir" _scratch_mount`, `SCRATCH_DEV="$SCRATCH_DEV_ORIG/quota-dir" _scratch_unmount`, `SCRATCH_DEV="$SCRATCH_DEV_ORIG/quota-dir/subdir" _scratch_mount`, `SCRATCH_DEV="$SCRATCH_DEV_ORIG/quota-dir/subdir" _scratch_unmount`.

Control flow: The script is mostly straight-line after harness setup. Representative operation sequence: L15: _exclude_test_mount_option "test_dummy_encryption"; L17: _scratch_mount; L24: _scratch_unmount; L27: SCRATCH_DEV="$SCRATCH_DEV/quota-dir" _scratch_mount; L29: SCRATCH_DEV="$SCRATCH_DEV_ORIG/quota-dir" _scratch_unmount; L31: SCRATCH_DEV="$SCRATCH_DEV_ORIG/quota-dir/subdir" _scratch_mount; L33: SCRATCH_DEV="$SCRATCH_DEV_ORIG/quota-dir/subdir" _scratch_unmount.

State and persistence behavior: mounts and unmounts test filesystems; changes quota/qgroup accounting state.

Dependencies and integration points: Depends on xfstests common libraries, CephFS mount, xattrs, debugfs metrics, or snapshot helpers. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: quota accounting regressions can be silent until unmount or rescan.

Test signals: no unexpected stdout beyond the golden quiet marker; visible subtest labels include Silence is golden.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ceph/005 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ceph/006 -->
# sources/test-tools/xfstests/tests/ceph/006

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ceph/006_research.md`.

Source read: 63 lines, SHA256 prefix `5130c04380365b91`.

Purpose: FS QA Test No. 006 Test that snapshot data remains intact after punch hole operations on the original file. Override the default cleanup function.

Important APIs/types/functions: test tags `auto quick snapshot`; common harness imports `. ./common/preamble`, `. common/ceph`; requirements/fixed gates `_require_test`, `_require_xfs_io_command "fpunch"`, `_require_ceph_snapshot`, `_exclude_test_mount_option "test_dummy_encryption"`, `_fixed_by_kernel_commit xxxxxxxxxxxx \`; helper functions `_cleanup()`; key variables `workdir=$TEST_DIR/test-$seq`, `snapdir=$(_ceph_create_snapshot $workdir snap1)`, `original_md5=$(md5sum $snapdir/foo | cut -d' ' -f1)`, `snapshot_md5=$(md5sum $snapdir/foo | cut -d' ' -f1)`.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `_cleanup()`. Representative operation sequence: L18: _ceph_remove_snapshot $workdir snap1; L24: _require_xfs_io_command "fpunch"; L25: _require_ceph_snapshot; L26: _exclude_test_mount_option "test_dummy_encryption"; L33: _ceph_remove_snapshot $workdir snap1; L37: $XFS_IO_PROG -f -c "pwrite -S 0xab 0 1048576" $workdir/foo > /dev/null; L39: snapdir=$(_ceph_create_snapshot $workdir snap1); L41: original_md5=$(md5sum $snapdir/foo | cut -d' ' -f1); L43: $XFS_IO_PROG -c "fpunch 0 65536" $workdir/foo; L44: $XFS_IO_PROG -c "fpunch 131072 65536" $workdir/foo; L45: $XFS_IO_PROG -c "fpunch 262144 65536" $workdir/foo; L46: $XFS_IO_PROG -c "fpunch 393216 65536" $workdir/foo; L51: snapshot_md5=$(md5sum $snapdir/foo | cut -d' ' -f1).

State and persistence behavior: persists snapshot roots and verifies their contents; drops page cache to force media-backed reads.

Dependencies and integration points: Depends on xfstests common libraries, xfs_io workload commands, CephFS mount, xattrs, debugfs metrics, or snapshot helpers. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: requires privileged cache dropping and can perturb the host; has a placeholder fixed-by commit annotation; is tied to specific kernel-regression behavior noted by fixed-by annotations.

Test signals: no unexpected stdout beyond the golden quiet marker; matching file digests before and after remount/send/receive; visible subtest labels include 3 > /proc/sys/vm/drop_caches; FAIL: Snapshot data changed after punch hole operations; Silence is golden.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ceph/006 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ceph/Makefile -->
# sources/test-tools/xfstests/tests/ceph/Makefile

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ceph/Makefile_research.md`.

Source read: 22 lines, SHA256 prefix `70f84e5e0733790b`.

Purpose: package-install rules for the xfstests `ceph` test directory. It builds the local `group.list` metadata and installs runnable tests plus expected output files into the package test tree.

Important APIs/types/functions: the file includes `include/builddefs`, `include/buildgrouplist`, and `$(BUILDRULES)`. Important variables are `TOPDIR`, `TARGET_DIR`, and `DIRT`. The exported targets are `default`, `install`, `install-dev`, and `install-lib`.

Control flow: `default` depends on `$(DIRT)`, which is the generated `group.list`. The `install` target creates `$(TARGET_DIR)`, installs `$(TESTS)` executable, installs `group.list` read-only, and installs `$(OUTFILES)` as read-only golden-output files. `install-dev` and `install-lib` are intentionally empty.

State and persistence behavior: persists directory contents under `$(PKG_LIB_DIR)/$(TESTS_DIR)/...` during package installation and leaves `group.list` as a build artifact. It does not run tests or touch scratch devices.

Dependencies and integration: integrated with the xfstests build system through `builddefs`, `buildgrouplist`, and common build rules. It depends on the harness variables that enumerate tests and `.out` files.

Risks: install permissions are fixed at 0755 for tests and 0644 for metadata/output; missing generated group lists or stale `$(TESTS)` expansion would omit cases from packaged runs.

Test signals: `make -C tests/ceph install DESTDIR=...` should create the expected tree with executable test scripts, `group.list`, and output files.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ceph/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/cifs/001 -->
# sources/test-tools/xfstests/tests/cifs/001

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/cifs/001_research.md`.

Source read: 43 lines, SHA256 prefix `e625e6eb69c95677`.

Purpose: FS QA Test No. cifs/001 Sanity test for server-side copies initiated via CIFS_IOC_COPYCHUNK_FILE Override the default cleanup function..

Important APIs/types/functions: test tags `auto quick`; common harness imports `. ./common/preamble`, `. ./common/filter`; requirements/fixed gates `_require_cloner`, `_require_test`; helper functions `_cleanup()`; key variables `len=$(($i * 1024))`.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `_cleanup()`. Representative operation sequence: L31: $XFS_IO_PROG -f -c "pwrite -S $i 0 $len" $TEST_DIR/$$/src/${i} \; L38: $CLONER_PROG $TEST_DIR/$$/src/${i} $TEST_DIR/$$/dest/${i}; L39: diff $TEST_DIR/$$/src/${i} $TEST_DIR/$$/dest/${i}.

State and persistence behavior: mainly drives transient test files under TEST_DIR or SCRATCH_MNT.

Dependencies and integration points: Depends on xfstests common libraries, xfs_io workload commands, CIFS/SMB clone helper. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: depends on xfstests harness requirements and exact golden-output filtering.

Test signals: byte-for-byte compare of copied or restored data.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/cifs/001 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/cifs/Makefile -->
# sources/test-tools/xfstests/tests/cifs/Makefile

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/cifs/Makefile_research.md`.

Source read: 24 lines, SHA256 prefix `686f987daf811055`.

Purpose: package-install rules for the xfstests `cifs` test directory. It builds the local `group.list` metadata and installs runnable tests plus expected output files into the package test tree.

Important APIs/types/functions: the file includes `include/builddefs`, `include/buildgrouplist`, and `$(BUILDRULES)`. Important variables are `TOPDIR`, `TARGET_DIR`, and `DIRT`. The exported targets are `default`, `install`, `install-dev`, and `install-lib`.

Control flow: `default` depends on `$(DIRT)`, which is the generated `group.list`. The `install` target creates `$(TARGET_DIR)`, installs `$(TESTS)` executable, installs `group.list` read-only, and installs `$(OUTFILES)` as read-only golden-output files. `install-dev` and `install-lib` are intentionally empty.

State and persistence behavior: persists directory contents under `$(PKG_LIB_DIR)/$(TESTS_DIR)/...` during package installation and leaves `group.list` as a build artifact. It does not run tests or touch scratch devices.

Dependencies and integration: integrated with the xfstests build system through `builddefs`, `buildgrouplist`, and common build rules. It depends on the harness variables that enumerate tests and `.out` files.

Risks: install permissions are fixed at 0755 for tests and 0644 for metadata/output; missing generated group lists or stale `$(TESTS)` expansion would omit cases from packaged runs.

Test signals: `make -C tests/cifs install DESTDIR=...` should create the expected tree with executable test scripts, `group.list`, and output files.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/cifs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/001 -->
# sources/test-tools/xfstests/tests/ext4/001

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ext4/001_research.md`.

Source read: 41 lines, SHA256 prefix `e0ee3c18b085f592`.

Purpose: FS QA Test No. 001 Test fallocate FALLOC_FL_ZERO_RANGE.

Important APIs/types/functions: test tags `auto prealloc quick zero fiemap`; common harness imports `. ./common/preamble`, `. ./common/filter`, `. ./common/punch`; requirements/fixed gates `_exclude_fs ext2`, `_exclude_fs ext3`, `_require_xfs_io_command "falloc"`, `_require_xfs_io_command "fzero"`, `_require_test`; key variables `seqfull=$0`, `testfile=$TEST_DIR/001.$$`.

Control flow: The script is mostly straight-line after harness setup. Representative operation sequence: L11: _begin_fstest auto prealloc quick zero fiemap; L20: _require_xfs_io_command "falloc"; L30: _test_generic_punch falloc fzero fzero fiemap _filter_fiemap $testfile; L33: _test_generic_punch -d falloc fzero fzero fiemap _filter_fiemap $testfile; L36: _test_generic_punch -k falloc fzero fzero fiemap _filter_fiemap $testfile; L39: _test_generic_punch -d -k falloc fzero fzero fiemap _filter_fiemap $testfile.

State and persistence behavior: mainly drives transient test files under TEST_DIR or SCRATCH_MNT.

Dependencies and integration points: Depends on xfstests common libraries. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: depends on xfstests harness requirements and exact golden-output filtering.

Test signals: fiemap extent layout and flags.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/001 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/001.cfg -->
# sources/test-tools/xfstests/tests/ext4/001.cfg

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ext4/001.cfg_research.md`.

Source read: 4 lines, SHA256 prefix `df93e660d259dd6c`.

Purpose: mount-option to golden-output mapping for `sources/test-tools/xfstests/tests/ext4/001.cfg`. It tells the xfstests output-linking helper which alternate `.out` expectation should be used for `ext4/001` under specific ext4 mount options.

Important APIs/types/functions: declarative key/value entries are `dax: nodelalloc`, `dioread_nolock: nozero`, `nodelalloc: nodelalloc`, `data=journal: nodelalloc`. The consumer is `_link_out_file` from the xfstests common harness.

Control flow: no executable control flow lives here. The test harness reads the mapping before running `ext4/001`; when the current mount option matches a key, it selects the named output variant.

State and persistence behavior: it changes expected-output selection only for the test run. It does not mutate filesystem state.

Dependencies and integration: coupled to `sources/test-tools/xfstests/tests/ext4/001`, generic punch/zero-range output filtering, and ext4 mount options such as `dax`, `dioread_nolock`, `nodelalloc`, and `data=journal`.

Risks: stale mappings cause false failures even when filesystem behavior is correct. Adding new mount-option variants for `ext4/001` requires extending this file in lockstep with golden outputs.

Test signals: running `ext4/001` with each mapped mount option should select the intended alternate expected output and avoid spurious diffs.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/001.cfg -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/003 -->
# sources/test-tools/xfstests/tests/ext4/003

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ext4/003_research.md`.

Source read: 42 lines, SHA256 prefix `6137112860cd0958`.

Purpose: FS QA Test No. ext4/003 Regression test for commit: b5b6077 ext4: fix wrong assert in ext4_mb_normalize_request() This testcase checks whether this bug has been fixed. Override the default cleanup function..

Important APIs/types/functions: test tags `auto quick`; common harness imports `. ./common/preamble`, `. ./common/filter`; requirements/fixed gates `_exclude_fs ext2`, `_exclude_fs ext3`, `_require_scratch`, `_require_scratch_ext4_feature "bigalloc"`; helper functions `_cleanup()`; key variables `BLOCK_SIZE=$(_get_page_size)`, `features=bigalloc`.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `_cleanup()`. Representative operation sequence: L17: _scratch_unmount; L27: _require_scratch_ext4_feature "bigalloc"; L36: _scratch_mount; L38: $XFS_IO_PROG -f -c "pwrite 0 256m -b 1M" $SCRATCH_MNT/testfile 2>&1 | \.

State and persistence behavior: mounts and unmounts test filesystems.

Dependencies and integration points: Depends on xfstests common libraries, xfs_io workload commands, ext-family mkfs/tune utilities. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: depends on xfstests harness requirements and exact golden-output filtering.

Test signals: successful script exit with xfstests filtered output.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/003 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/004 -->
# sources/test-tools/xfstests/tests/ext4/004

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ext4/004_research.md`.

Source read: 65 lines, SHA256 prefix `08c7271b472efda6`.

Purpose: FSQA Test No. 004 Test "dump | restore"(as opposed to a tape) Override the default cleanup function..

Important APIs/types/functions: test tags `auto dump`; common harness imports `. ./common/preamble`, `. ./common/filter`; requirements/fixed gates `_exclude_fs ext2`, `_exclude_fs ext3`, `_require_test`, `_require_scratch`, `_require_command "$DUMP_PROG" dump`, `_require_command "$RESTORE_PROG" restore`; helper functions `_cleanup()`, `workout()`; key variables `dump_dir=$SCRATCH_MNT/dump_restore_dir`, `restore_dir=$TEST_DIR/dump_restore_dir`, `args=`_scale_fsstress_args -z -f creat=5 -f write=20 -f mkdir=5 -n 100 -p 15 -d $dump_dir``.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `_cleanup()`, `workout()`. Representative operation sequence: L15: _kill_fsstress; L31: args=`_scale_fsstress_args -z -f creat=5 -f write=20 -f mkdir=5 -n 100 -p 15 -d $dump_dir`; L33: _run_fsstress $args; L38: $DUMP_PROG -0 -f - $dump_dir 2>/dev/null | $RESTORE_PROG -urvf - >> $seqres.full 2>&1; L52: _require_command "$DUMP_PROG" dump; L53: _require_command "$RESTORE_PROG" restore; L57: _scratch_mkfs_sized $((512 * 1024 * 1024)) >> $seqres.full 2>&1; L58: _scratch_mount; L62: diff -r $dump_dir $restore_dir.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems.

Dependencies and integration points: Depends on xfstests common libraries. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: depends on xfstests harness requirements and exact golden-output filtering.

Test signals: no unexpected stdout beyond the golden quiet marker; byte-for-byte compare of copied or restored data; visible subtest labels include Silence is golden.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/004 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/005 -->
# sources/test-tools/xfstests/tests/ext4/005

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ext4/005_research.md`.

Source read: 53 lines, SHA256 prefix `d2438bb20986971e`.

Purpose: FS QA Test 005 Test corruption issue in converting file with a hole at the beginning to non-extent based format These two commits fixed the corruption: ext4: be more strict when migrating to non-extent based file ext4: correctly migrate a file with a hole at the beginning Import common functions..

Important APIs/types/functions: test tags `auto quick metadata ioctl rw`; common harness imports `. ./common/preamble`, `. ./common/filter`; requirements/fixed gates `_exclude_fs ext2`, `_exclude_fs ext3`, `_require_scratch`, `_require_command "$CHATTR_PROG" chattr`; key variables `testfile=$SCRATCH_MNT/$seq.attrtest`.

Control flow: The script is mostly straight-line after harness setup. Representative operation sequence: L28: _scratch_mkfs >>$seqres.full 2>&1; L29: _scratch_mount; L40: $XFS_IO_PROG -fc "pwrite 4k 4k" -c "fsync" $testfile >>$seqres.full 2>&1; L49: $XFS_IO_PROG -c "pwrite 0 4k" $testfile >>$seqres.full 2>&1.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems.

Dependencies and integration points: Depends on xfstests common libraries, xfs_io workload commands. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: depends on xfstests harness requirements and exact golden-output filtering.

Test signals: no unexpected stdout beyond the golden quiet marker; visible subtest labels include Silence is golden.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/005 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/006 -->
# sources/test-tools/xfstests/tests/ext4/006

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ext4/006_research.md`.

Source read: 140 lines, SHA256 prefix `30dac6d3712a9ce2`.

Purpose: FS QA Test No. 006 Create and populate an ext4 filesystem, fuzz the metadata, then see how the kernel reacts, how e2fsck fares in fixing the mess, and then try more kernel accesses to see if it really fixed things. Override the default cleanup function..

Important APIs/types/functions: test tags `dangerous_fuzzers`; common harness imports `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`, `. ./common/populate`, `. ./common/fuzzy`; requirements/fixed gates `_exclude_fs ext2`, `_exclude_fs ext3`, `_require_scratch`, `_require_attrs`, `_require_populate_commands`; helper functions `_cleanup()`, `repair_scratch()`; key variables `fsck_pass="$1"`, `FSCK_LOG="${tmp}-fuzz-${fsck_pass}.log"`, `SRCDIR=`pwd``, `BLK_SZ=4096`, `ROUND2_LOG="${tmp}-round2-${fsck_pass}.log"`.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `_cleanup()`, `repair_scratch()`. Representative operation sequence: L43: e2fsck -f -y "${SCRATCH_DEV}"; L47: e2fsck -n "${SCRATCH_DEV}" >> "${FSCK_LOG}" 2>&1; L62: cmp -s "${tmp}-fuzz-$((fsck_pass - 1)).log" "${FSCK_LOG}"; L80: _scratch_mkfs_ext4 >> $seqres.full 2>&1; L83: _scratch_populate >> $seqres.full; L86: _check_scratch_fs >> $seqres.full 2>&1 || _fail "should pass initial fsck"; L92: _try_scratch_mount >> $seqres.full 2>&1; L95: _scratch_fuzz_test >> $seqres.full 2>&1; L98: _scratch_fuzz_modify >> $seqres.full 2>&1; L110: _check_scratch_fs >> $seqres.full 2>&1; L114: _try_scratch_mount >> $ROUND2_LOG 2>&1; L120: _scratch_fuzz_test >> $ROUND2_LOG 2>&1; L123: _scratch_fuzz_modify >> $ROUND2_LOG 2>&1; L131: _check_scratch_fs >> $seqres.full 2>&1; L133: grep -E -q '(did not fix|makes no progress)' $seqres.full && echo "e2fsck failed" | tee -a $seqres.full.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; uses fsck as the final persistence/integrity oracle; creates loop devices or image-backed devices.

Dependencies and integration points: Depends on xfstests common libraries. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: deliberately corrupts metadata and can trigger kernel failure paths; loop-device cleanup must run to avoid leaked devices.

Test signals: clean e2fsck verification; byte-for-byte compare of copied or restored data; visible subtest labels include ++ fsck makes no progress.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/006 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/007 -->
# sources/test-tools/xfstests/tests/ext4/007

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ext4/007_research.md`.

Source read: 99 lines, SHA256 prefix `58ed2ad9c6136691`.

Purpose: FS QA Test No. 007 Create and populate an ext4 filesystem, corrupt the primary superblock, then see how the kernel and e2fsck deal with it. Override the default cleanup function..

Important APIs/types/functions: test tags `fuzzers`; common harness imports `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`; requirements/fixed gates `_exclude_fs ext2`, `_exclude_fs ext3`, `_require_scratch`, `_require_attrs`; helper functions `_cleanup()`; key variables `TESTDIR="${SCRATCH_MNT}/scratchdir"`, `TESTFILE="${TESTDIR}/testfile"`, `blksz="$(stat -f -c '%s' "${SCRATCH_MNT}")"`, `nr_groups="$(dumpe2fs -g "${SCRATCH_DEV}" 2> /dev/null | tail -n 1 | cut -d : -f 1)"`, `inode="$(stat -c '%i' "${SCRATCH_MNT}/junk.${x}")"`, `broken=0`.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `_cleanup()`. Representative operation sequence: L28: test -n "${FORCE_FUZZ}" || _require_scratch_ext4_crc; L35: _scratch_mkfs_ext4 > /dev/null 2>&1; L36: dumpe2fs -g "${SCRATCH_DEV}" > /dev/null 2>&1 || _notrun "dumpe2fs -g not supported"; L39: _scratch_mount; L41: nr_groups="$(dumpe2fs -g "${SCRATCH_DEV}" 2> /dev/null | tail -n 1 | cut -d : -f 1)"; L43: backup_sb="$(dumpe2fs -g "${SCRATCH_DEV}" 2> /dev/null | awk -F ':' 'BEGIN {x = 0;} {if (x == 0 && int($3) > 1) {print $3; x++;}}')"; L61: e2fsck -fn "${SCRATCH_DEV}" >> $seqres.full 2>&1 || _fail "fsck should not fail"; L64: dumpe2fs -g "${SCRATCH_DEV}" 2>/dev/null | awk -F ':' '{if ($1 == 0) {print $3}}' | while read blk; do; L65: debugfs -w -R "zap_block ${blk}" "${SCRATCH_DEV}" >> $seqres.full 2>&1 || _fail "primary sb fuzz failed"; L69: _try_scratch_mount 2> /dev/null && _fail "mount should not succeed"; L75: e2fsck -f -y -B "${blksz}" -b "${backup_sb}" "${SCRATCH_DEV}" >> $seqres.full 2>&1; L78: _scratch_mount; L96: e2fsck -fn "${SCRATCH_DEV}" >> $seqres.full 2>&1 || _fail "fsck should not fail".

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; edits or inspects ext metadata directly; uses fsck as the final persistence/integrity oracle.

Dependencies and integration points: Depends on xfstests common libraries. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: depends on exact e2fsck/kernel reactions to damaged ext4 metadata.

Test signals: clean e2fsck verification; mount/statfs option visibility; visible subtest labels include + create scratch fs; + mount fs image; + make some files; + check fs; + corrupt image; + mount image.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/007 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/008 -->
# sources/test-tools/xfstests/tests/ext4/008

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ext4/008_research.md`.

Source read: 80 lines, SHA256 prefix `ba4f76838f1a7667`.

Purpose: FS QA Test No. 008 Create and populate an ext4 filesystem, corrupt a group descriptor, then see how the kernel and e2fsck deal with it. Override the default cleanup function..

Important APIs/types/functions: test tags `fuzzers`; common harness imports `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`; requirements/fixed gates `_exclude_fs ext2`, `_exclude_fs ext3`, `_require_scratch`, `_require_attrs`; helper functions `_cleanup()`; key variables `TESTDIR="${SCRATCH_MNT}/scratchdir"`, `TESTFILE="${TESTDIR}/testfile"`, `inode="$(stat -c '%i' "${SCRATCH_MNT}/junk.${x}")"`.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `_cleanup()`. Representative operation sequence: L28: test -n "${FORCE_FUZZ}" || _require_scratch_ext4_crc; L35: _scratch_mkfs_ext4 > /dev/null 2>&1; L36: dumpe2fs -g "${SCRATCH_DEV}" > /dev/null 2>&1 || _notrun "dumpe2fs -g not supported"; L39: _scratch_mount; L57: e2fsck -fn "${SCRATCH_DEV}" >> $seqres.full 2>&1 || _fail "fsck should not fail"; L60: dumpe2fs -g "${SCRATCH_DEV}" 2>/dev/null | awk -F ':' '{if (int($4) != -1) {print $4}}' | sed -e 's/-.*$//g' | awk '{if (int($1) > 0) {print $1}}' | while read blk; do; L61: debugfs -w -R "zap_block ${blk}" "${SCRATCH_DEV}" >> $seqres.full 2>&1 || _fail "group descriptor fuzz failed"; L65: _try_scratch_mount 2> /dev/null && _fail "mount should not succeed"; L68: e2fsck -fy "${SCRATCH_DEV}" >> $seqres.full 2>&1; L69: e2fsck -fy "${SCRATCH_DEV}" >> $seqres.full 2>&1; L72: _scratch_mount; L77: e2fsck -fn "${SCRATCH_DEV}" >> $seqres.full 2>&1 || _fail "fsck should not fail".

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; edits or inspects ext metadata directly; uses fsck as the final persistence/integrity oracle.

Dependencies and integration points: Depends on xfstests common libraries. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: depends on exact e2fsck/kernel reactions to damaged ext4 metadata.

Test signals: clean e2fsck verification; visible subtest labels include + create scratch fs; + mount fs image; + make some files; + check fs; + corrupt image; + mount image.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/008 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/009 -->
# sources/test-tools/xfstests/tests/ext4/009

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ext4/009_research.md`.

Source read: 90 lines, SHA256 prefix `1bf5fc3e97887ff5`.

Purpose: FS QA Test No. 009 Create and populate an ext4 filesystem, corrupt a block bitmap, then see how the kernel and e2fsck deal with it. Override the default cleanup function..

Important APIs/types/functions: test tags `fuzzers prealloc`; common harness imports `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`; requirements/fixed gates `_exclude_fs ext2`, `_exclude_fs ext3`, `_require_xfs_io_command "falloc"`, `_require_scratch`, `_require_attrs`; helper functions `_cleanup()`; key variables `TESTDIR="${SCRATCH_MNT}/scratchdir"`, `TESTFILE="${TESTDIR}/testfile"`, `nr_groups="$(dumpe2fs -g "${SCRATCH_DEV}" 2> /dev/null | tail -n 1 | cut -d : -f 1)"`, `blksz="$(stat -f -c '%s' "${SCRATCH_MNT}")"`, `freeblks="$(stat -f -c '%a' "${SCRATCH_MNT}")"`, `b_bytes="$(stat -c '%B' "${SCRATCH_MNT}/bigfile")"`, `after="$(stat -c '%b' "${SCRATCH_MNT}/bigfile")"`.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `_cleanup()`. Representative operation sequence: L27: _require_xfs_io_command "falloc"; L29: test -n "${FORCE_FUZZ}" || _require_scratch_ext4_crc; L36: _scratch_mkfs_ext4 > /dev/null 2>&1; L37: dumpe2fs -g "${SCRATCH_DEV}" > /dev/null 2>&1 || _notrun "dumpe2fs -g not supported"; L38: nr_groups="$(dumpe2fs -g "${SCRATCH_DEV}" 2> /dev/null | tail -n 1 | cut -d : -f 1)"; L41: _scratch_mount; L48: $XFS_IO_PROG -f -c "falloc 0 $((blksz * freeblks))" "${SCRATCH_MNT}/bigfile2" >> $seqres.full; L52: _scratch_mount; L58: e2fsck -fn "${SCRATCH_DEV}" >> $seqres.full 2>&1 || _fail "fsck should not fail"; L61: dumpe2fs -g "${SCRATCH_DEV}" 2>/dev/null | awk -F ':' '{if (int($5) > 0) {print $5}}' | while read blk; do; L62: debugfs -w -n -R "zap_block -p 0xff ${blk}" "${SCRATCH_DEV}" >> $seqres.full 2>&1 || _fail "block bitmap fuzz failed"; L66: _scratch_mount; L70: $XFS_IO_PROG -f -c "falloc 0 $((blksz * freeblks))" "${SCRATCH_MNT}/bigfile" >> $seqres.full 2> /dev/null; L73: test "$((after * b_bytes))" -lt "$((blksz * freeblks / 4))" || _fail "falloc should fail"; L77: e2fsck -fy "${SCRATCH_DEV}" >> $seqres.full 2>&1; L80: _scratch_mount; L83: $XFS_IO_PROG -f -c "falloc 0 $((blksz * freeblks))" "${SCRATCH_MNT}/bigfile" >> $seqres.full; L87: e2fsck -fn "${SCRATCH_DEV}" >> $seqres.full 2>&1 || _fail "fsck should not fail".

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; edits or inspects ext metadata directly; uses fsck as the final persistence/integrity oracle.

Dependencies and integration points: Depends on xfstests common libraries, xfs_io workload commands. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: depends on exact e2fsck/kernel reactions to damaged ext4 metadata.

Test signals: clean e2fsck verification; mount/statfs option visibility; visible subtest labels include + create scratch fs; + mount fs image; + make some files; + check fs; + corrupt image; + mount image.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/009 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/010 -->
# sources/test-tools/xfstests/tests/ext4/010

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ext4/010_research.md`.

Source read: 81 lines, SHA256 prefix `22e54a012dea45ad`.

Purpose: FS QA Test No. 010 Create and populate an ext4 filesystem, corrupt an inode bitmap, then see how the kernel and e2fsck deal with it. Override the default cleanup function..

Important APIs/types/functions: test tags `fuzzers`; common harness imports `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`; requirements/fixed gates `_exclude_fs ext2`, `_exclude_fs ext3`, `_require_scratch`, `_require_dumpe2fs`, `_require_attrs`, `_require_command "$RESIZE2FS_PROG" resize2fs`; helper functions `_cleanup()`; key variables `TESTDIR="${SCRATCH_MNT}/scratchdir"`, `TESTFILE="${TESTDIR}/testfile"`, `nr_groups="$($DUMPE2FS_PROG -g "${SCRATCH_DEV}" 2> /dev/null | tail -n 1 | cut -d : -f 1)"`.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `_cleanup()`. Representative operation sequence: L28: _require_dumpe2fs; L29: test -n "${FORCE_FUZZ}" || _require_scratch_ext4_crc; L31: _require_command "$RESIZE2FS_PROG" resize2fs; L37: _scratch_mkfs_ext4 > /dev/null 2>&1; L38: $DUMPE2FS_PROG -g "${SCRATCH_DEV}" > /dev/null 2>&1 || _notrun "dumpe2fs -g not supported"; L39: $RESIZE2FS_PROG -M "${SCRATCH_DEV}" >> $seqres.full 2>&1; L40: nr_groups="$($DUMPE2FS_PROG -g "${SCRATCH_DEV}" 2> /dev/null | tail -n 1 | cut -d : -f 1)"; L43: _scratch_mount; L53: e2fsck -fn "${SCRATCH_DEV}" >> $seqres.full 2>&1 || _fail "fsck should not fail"; L56: $DUMPE2FS_PROG -g "${SCRATCH_DEV}" 2>/dev/null | awk -F ':' '{if (int($6) > 0) {print $6}}' | while read blk; do; L57: debugfs -w -n -R "zap_block ${blk}" "${SCRATCH_DEV}" >> $seqres.full 2>&1 || _fail "inode bitmap fuzz failed"; L61: _scratch_mount; L68: e2fsck -fy "${SCRATCH_DEV}" >> $seqres.full 2>&1; L71: _scratch_mount; L78: e2fsck -fn "${SCRATCH_DEV}" >> $seqres.full 2>&1 || _fail "fsck should not fail".

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; edits or inspects ext metadata directly; uses fsck as the final persistence/integrity oracle; resizes filesystem images or online filesystems.

Dependencies and integration points: Depends on xfstests common libraries, e2fsprogs debug/fsck utilities. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: depends on exact e2fsck/kernel reactions to damaged ext4 metadata.

Test signals: clean e2fsck verification; visible subtest labels include + create scratch fs; + mount fs image; + make some files; + check fs; + corrupt image; + mount image.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/010 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/011 -->
# sources/test-tools/xfstests/tests/ext4/011

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ext4/011_research.md`.

Source read: 65 lines, SHA256 prefix `f14db5c336495922`.

Purpose: FS QA Test No. 011 Create and populate an ext4 filesystem, corrupt the MMP block, then see how the kernel and e2fsck deal with it. Override the default cleanup function..

Important APIs/types/functions: test tags `fuzzers`; common harness imports `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`; requirements/fixed gates `_exclude_fs ext2`, `_exclude_fs ext3`, `_require_scratch`, `_require_attrs`; helper functions `_cleanup()`; key variables `TESTDIR="${SCRATCH_MNT}/scratchdir"`, `TESTFILE="${TESTDIR}/testfile"`, `blksz="$(stat -f -c '%s' "${SCRATCH_MNT}")"`.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `_cleanup()`. Representative operation sequence: L28: test -n "${FORCE_FUZZ}" || _require_scratch_ext4_crc; L35: _scratch_mkfs_ext4 -O mmp -E mmp_update_interval=2 > /dev/null 2>&1; L38: _scratch_mount; L46: e2fsck -fn "${SCRATCH_DEV}" >> $seqres.full 2>&1 || _fail "fsck should not fail"; L49: blk="$(dumpe2fs "${SCRATCH_DEV}" 2> /dev/null | grep 'MMP block number' | sed -e 's/^MMP block number: *\([0-9]*\)$/\1/g')"; L50: $XFS_IO_PROG -f -c "pwrite -S 0x62 $((blk * blksz + 16)) 8" "${SCRATCH_DEV}" >> $seqres.full; L53: _try_scratch_mount 2> /dev/null && _fail "mount should fail due to bad MMP"; L56: e2fsck -fy "${SCRATCH_DEV}" >> $seqres.full 2>&1; L59: _try_scratch_mount || _fail "mount should not fail; MMP has been fixed"; L62: e2fsck -fn "${SCRATCH_DEV}" >> $seqres.full 2>&1 || _fail "fsck should not fail".

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; uses fsck as the final persistence/integrity oracle.

Dependencies and integration points: Depends on xfstests common libraries, xfs_io workload commands. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: depends on exact e2fsck/kernel reactions to damaged ext4 metadata.

Test signals: clean e2fsck verification; mount/statfs option visibility; visible subtest labels include + create scratch fs; + mount fs image; + make some files; + check fs; + corrupt image; + mount image.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/011 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/012 -->
# sources/test-tools/xfstests/tests/ext4/012

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ext4/012_research.md`.

Source read: 64 lines, SHA256 prefix `2cb2ecede8e989fe`.

Purpose: FS QA Test No. 012 Create and populate an ext4 filesystem, corrupt the journal, then see how the kernel and e2fsck deal with it. Override the default cleanup function..

Important APIs/types/functions: test tags `fuzzers`; common harness imports `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`; requirements/fixed gates `_exclude_fs ext2`, `_exclude_fs ext3`, `_require_scratch`, `_require_attrs`; helper functions `_cleanup()`; key variables `TESTDIR="${SCRATCH_MNT}/scratchdir"`, `TESTFILE="${TESTDIR}/testfile"`, `blksz="$(stat -f -c '%s' "${SCRATCH_MNT}")"`.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `_cleanup()`. Representative operation sequence: L28: test -n "${FORCE_FUZZ}" || _require_scratch_ext4_crc; L35: _scratch_mkfs -O has_journal >> $seqres.full 2>&1; L38: _scratch_mount; L46: e2fsck -fn "${SCRATCH_DEV}" >> $seqres.full 2>&1 || _fail "fsck should not fail"; L49: debugfs -w -R 'zap -f <8> 0' "${SCRATCH_DEV}" 2> /dev/null; L52: _try_scratch_mount 2> /dev/null && _fail "mount should fail due to bad journal"; L55: e2fsck -fy "${SCRATCH_DEV}" >> $seqres.full 2>&1; L58: _try_scratch_mount || _fail "mount should not fail; journal has been fixed"; L61: e2fsck -fn "${SCRATCH_DEV}" >> $seqres.full 2>&1 || _fail "fsck should not fail".

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; edits or inspects ext metadata directly; uses fsck as the final persistence/integrity oracle.

Dependencies and integration points: Depends on xfstests common libraries. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: depends on exact e2fsck/kernel reactions to damaged ext4 metadata.

Test signals: clean e2fsck verification; mount/statfs option visibility; visible subtest labels include + create scratch fs; + mount fs image; + make some files; + check fs; + corrupt image; + mount image.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/012 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/013 -->
# sources/test-tools/xfstests/tests/ext4/013

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ext4/013_research.md`.

Source read: 103 lines, SHA256 prefix `ac7300fe9852d908`.

Purpose: FS QA Test No. 013 Create and populate an ext4 filesystem, corrupt an inode, then see how the kernel and e2fsck deal with it. Override the default cleanup function..

Important APIs/types/functions: test tags `fuzzers`; common harness imports `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`; requirements/fixed gates `_exclude_fs ext2`, `_exclude_fs ext3`, `_require_scratch`, `_require_attrs`; helper functions `_cleanup()`; key variables `TESTDIR="${SCRATCH_MNT}/scratchdir"`, `TESTFILE="${TESTDIR}/testfile"`, `inode="$(stat -c '%i' "${SCRATCH_MNT}/junk.${x}")"`, `inode="$(stat -c '%i' "${TESTFILE}.1")"`, `broken=0`, `broken=0`.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `_cleanup()`. Representative operation sequence: L28: test -n "${FORCE_FUZZ}" || _require_scratch_ext4_crc; L35: _scratch_mkfs_ext4 > /dev/null 2>&1; L38: _scratch_mount; L57: e2fsck -fn "${SCRATCH_DEV}" >> $seqres.full 2>&1 || _fail "fsck should not fail"; L60: blk="$(debugfs -R "imap <$inode>" "${SCRATCH_DEV}" 2> /dev/null | grep located | sed -e 's/^.*block \([0-9]*\),.*$/\1/g')"; L61: debugfs -w -R "zap_block ${blk}" "${SCRATCH_DEV}" >> $seqres.full 2>&1 || _fail "inode fuzz failed"; L64: _scratch_mount; L79: e2fsck -fy "${SCRATCH_DEV}" >> $seqres.full 2>&1; L82: _scratch_mount; L100: e2fsck -fn "${SCRATCH_DEV}" >> $seqres.full 2>&1 || _fail "fsck should not fail".

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; edits or inspects ext metadata directly; uses fsck as the final persistence/integrity oracle.

Dependencies and integration points: Depends on xfstests common libraries. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: depends on exact e2fsck/kernel reactions to damaged ext4 metadata.

Test signals: clean e2fsck verification; visible subtest labels include + create scratch fs; + mount fs image; + make some files; + check fs; + corrupt image; + mount image.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/013 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/014 -->
# sources/test-tools/xfstests/tests/ext4/014

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ext4/014_research.md`.

Source read: 101 lines, SHA256 prefix `03fd1e0f5080ab5d`.

Purpose: FS QA Test No. 014 Create and populate an ext4 filesystem, corrupt root directory, then see how the kernel and e2fsck deal with it. Override the default cleanup function..

Important APIs/types/functions: test tags `fuzzers`; common harness imports `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`; requirements/fixed gates `_exclude_fs ext2`, `_exclude_fs ext3`, `_require_scratch`, `_require_attrs`; helper functions `_cleanup()`; key variables `TESTDIR="${SCRATCH_MNT}/scratchdir"`, `TESTFILE="${TESTDIR}/testfile"`, `inode="$(stat -c '%i' "${SCRATCH_MNT}/junk.${x}")"`, `broken=0`, `broken=0`.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `_cleanup()`. Representative operation sequence: L28: test -n "${FORCE_FUZZ}" || _require_scratch_ext4_crc; L35: _scratch_mkfs_ext4 > /dev/null 2>&1; L38: _scratch_mount; L56: e2fsck -fn "${SCRATCH_DEV}" >> $seqres.full 2>&1 || _fail "fsck should not fail"; L59: debugfs -w -R "zap -f / 0" "${SCRATCH_DEV}" >> $seqres.full 2>&1; L62: _scratch_mount; L77: e2fsck -fy "${SCRATCH_DEV}" >> $seqres.full 2>&1 && _fail "e2fsck should not succeed"; L80: _scratch_mount; L98: e2fsck -fn "${SCRATCH_DEV}" >> $seqres.full 2>&1 || _fail "fsck should not fail".

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; edits or inspects ext metadata directly; uses fsck as the final persistence/integrity oracle.

Dependencies and integration points: Depends on xfstests common libraries. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: depends on exact e2fsck/kernel reactions to damaged ext4 metadata.

Test signals: clean e2fsck verification; visible subtest labels include + create scratch fs; + mount fs image; + make some files; + check fs; + corrupt image; + mount image.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/014 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/015 -->
# sources/test-tools/xfstests/tests/ext4/015

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ext4/015_research.md`.

Source read: 80 lines, SHA256 prefix `9137a12c18acb5bc`.

Purpose: FS QA Test No. 015 Create and populate an ext4 filesystem, corrupt an extent tree block, then see how the kernel and e2fsck deal with it. Override the default cleanup function..

Important APIs/types/functions: test tags `fuzzers punch prealloc`; common harness imports `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`; requirements/fixed gates `_exclude_fs ext2`, `_exclude_fs ext3`, `_require_xfs_io_command "falloc"`, `_require_xfs_io_command "fpunch"`, `_require_scratch`, `_require_attrs`; helper functions `_cleanup()`; key variables `TESTDIR="${SCRATCH_MNT}/scratchdir"`, `TESTFILE="${TESTDIR}/testfile"`, `blksz="$(stat -f -c '%s' "${SCRATCH_MNT}")"`, `freeblks="$((3 * blksz / 12))"`.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `_cleanup()`. Representative operation sequence: L27: _require_xfs_io_command "falloc"; L28: _require_xfs_io_command "fpunch"; L30: test -n "${FORCE_FUZZ}" || _require_scratch_ext4_crc; L37: _scratch_mkfs_ext4 > /dev/null 2>&1; L40: _scratch_mount; L45: $XFS_IO_PROG -f -c "falloc 0 $((blksz * freeblks))" "${SCRATCH_MNT}/bigfile" >> $seqres.full; L47: $XFS_IO_PROG -f -c "fpunch $((lblk * blksz)) ${blksz}" "${SCRATCH_MNT}/bigfile" >> $seqres.full; L52: e2fsck -fn "${SCRATCH_DEV}" >> $seqres.full 2>&1 || _fail "fsck should not fail"; L55: debugfs "${SCRATCH_DEV}" -R 'ex /bigfile' 2> /dev/null | grep '^ 0' | awk '{print $8}' | while read blk; do; L56: $XFS_IO_PROG -f -c "pwrite -S 0x62 $((blk * blksz + 8)) 8" "${SCRATCH_DEV}" >> $seqres.full; L60: _scratch_mount; L67: e2fsck -fy "${SCRATCH_DEV}" >> $seqres.full 2>&1; L70: _scratch_mount; L73: $XFS_IO_PROG -f -c "pwrite ${blksz} ${blksz}" "${SCRATCH_MNT}/bigfile" >> $seqres.full; L77: e2fsck -fn "${SCRATCH_DEV}" >> $seqres.full 2>&1 || _fail "fsck should not fail".

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; edits or inspects ext metadata directly; uses fsck as the final persistence/integrity oracle.

Dependencies and integration points: Depends on xfstests common libraries, xfs_io workload commands. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: depends on exact e2fsck/kernel reactions to damaged ext4 metadata.

Test signals: clean e2fsck verification; mount/statfs option visibility; visible subtest labels include + create scratch fs; + mount fs image; + make some files; + check fs; + corrupt image; + mount image.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/015 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/016 -->
# sources/test-tools/xfstests/tests/ext4/016

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ext4/016_research.md`.

Source read: 73 lines, SHA256 prefix `eea1153e7ca2c2dd`.

Purpose: FS QA Test No. 016 Create and populate an ext4 filesystem, corrupt a dirent block, then see how the kernel and e2fsck deal with it. Override the default cleanup function..

Important APIs/types/functions: test tags `fuzzers`; common harness imports `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`; requirements/fixed gates `_exclude_fs ext2`, `_exclude_fs ext3`, `_require_scratch`, `_require_attrs`; helper functions `_cleanup()`; key variables `TESTDIR="${SCRATCH_MNT}/scratchdir"`, `TESTFILE="${TESTDIR}/testfile"`.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `_cleanup()`. Representative operation sequence: L28: test -n "${FORCE_FUZZ}" || _require_scratch_ext4_crc; L35: _scratch_mkfs_ext4 > /dev/null 2>&1; L38: _scratch_mount; L47: e2fsck -fn "${SCRATCH_DEV}" >> $seqres.full 2>&1 || _fail "fsck should not fail"; L50: debugfs -w -R "zap -f /test 0" "${SCRATCH_DEV}" 2> /dev/null; L53: _scratch_mount; L60: e2fsck -fy "${SCRATCH_DEV}" >> $seqres.full 2>&1; L63: _scratch_mount; L70: e2fsck -fn "${SCRATCH_DEV}" >> $seqres.full 2>&1 || _fail "fsck should not fail".

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; edits or inspects ext metadata directly; uses fsck as the final persistence/integrity oracle.

Dependencies and integration points: Depends on xfstests common libraries. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: depends on exact e2fsck/kernel reactions to damaged ext4 metadata.

Test signals: clean e2fsck verification; visible subtest labels include + create scratch fs; + mount fs image; + make some files; + check fs; + corrupt image; + mount image.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/016 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/017 -->
# sources/test-tools/xfstests/tests/ext4/017

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ext4/017_research.md`.

Source read: 76 lines, SHA256 prefix `ee6976acdc778f19`.

Purpose: FS QA Test No. 017 Create and populate an ext4 filesystem, corrupt a htree block, then see how the kernel and e2fsck deal with it. Override the default cleanup function..

Important APIs/types/functions: test tags `fuzzers`; common harness imports `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`; requirements/fixed gates `_exclude_fs ext2`, `_exclude_fs ext3`, `_require_scratch`, `_require_attrs`; helper functions `_cleanup()`; key variables `TESTDIR="${SCRATCH_MNT}/scratchdir"`, `TESTFILE="${TESTDIR}/testfile"`, `blksz="$(stat -f -c '%s' "${SCRATCH_MNT}")"`, `fname="$(printf "%.255s\n" "$(perl -e "print \"${x}_\" x 500;")")"`.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `_cleanup()`. Representative operation sequence: L28: test -n "${FORCE_FUZZ}" || _require_scratch_ext4_crc; L35: _scratch_mkfs_ext4 > /dev/null 2>&1; L38: _scratch_mount; L50: e2fsck -fn "${SCRATCH_DEV}" >> $seqres.full 2>&1 || _fail "fsck should not fail"; L53: debugfs -w -R "zap -f /test 0" "${SCRATCH_DEV}" 2> /dev/null; L56: _scratch_mount; L63: e2fsck -fy "${SCRATCH_DEV}" >> $seqres.full 2>&1; L66: _scratch_mount; L73: e2fsck -fn "${SCRATCH_DEV}" >> $seqres.full 2>&1 || _fail "fsck should not fail".

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; edits or inspects ext metadata directly; uses fsck as the final persistence/integrity oracle.

Dependencies and integration points: Depends on xfstests common libraries. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: depends on exact e2fsck/kernel reactions to damaged ext4 metadata.

Test signals: clean e2fsck verification; mount/statfs option visibility; visible subtest labels include + create scratch fs; + mount fs image; + make some files; + check fs; + corrupt image; + mount image.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/017 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/018 -->
# sources/test-tools/xfstests/tests/ext4/018

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ext4/018_research.md`.

Source read: 74 lines, SHA256 prefix `a09cfdba0a6b9f30`.

Purpose: FS QA Test No. 018 Create and populate an ext4 filesystem, corrupt a xattr block, then see how the kernel and e2fsck deal with it. Override the default cleanup function..

Important APIs/types/functions: test tags `fuzzers`; common harness imports `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`; requirements/fixed gates `_exclude_fs ext2`, `_exclude_fs ext3`, `_require_scratch`, `_require_attrs`; helper functions `_cleanup()`; key variables `TESTDIR="${SCRATCH_MNT}/scratchdir"`, `TESTFILE="${TESTDIR}/testfile"`, `blksz="$(stat -f -c '%s' "${SCRATCH_MNT}")"`.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `_cleanup()`. Representative operation sequence: L28: test -n "${FORCE_FUZZ}" || _require_scratch_ext4_crc; L35: _scratch_mkfs_ext4 > /dev/null 2>&1; L38: _scratch_mount; L42: $XFS_IO_PROG -f -c "pwrite -S 0x62 0 ${blksz}" "${SCRATCH_MNT}/attrfile" >> $seqres.full; L47: e2fsck -fn "${SCRATCH_DEV}" >> $seqres.full 2>&1 || _fail "fsck should not fail"; L50: blk="$(debugfs -R 'stat /attrfile' "${SCRATCH_DEV}" 2> /dev/null | grep 'File ACL:' | sed -e 's/^.*File ACL: \([0-9]*\).*/\1/g')"; L51: $XFS_IO_PROG -f -c "pwrite -S 0x62 $((blk * blksz + 20)) 8" "${SCRATCH_DEV}" >> $seqres.full; L54: _scratch_mount; L61: e2fsck -fy "${SCRATCH_DEV}" >> $seqres.full 2>&1; L64: _scratch_mount; L71: e2fsck -fn "${SCRATCH_DEV}" >> $seqres.full 2>&1 || _fail "fsck should not fail".

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; edits or inspects ext metadata directly; uses fsck as the final persistence/integrity oracle.

Dependencies and integration points: Depends on xfstests common libraries, xfs_io workload commands. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: depends on exact e2fsck/kernel reactions to damaged ext4 metadata.

Test signals: clean e2fsck verification; mount/statfs option visibility; visible subtest labels include + create scratch fs; + mount fs image; + make some files; + check fs; + corrupt image; + mount image.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/018 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/019 -->
# sources/test-tools/xfstests/tests/ext4/019

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ext4/019_research.md`.

Source read: 72 lines, SHA256 prefix `961386c7f65c7293`.

Purpose: FS QA Test No. 019 Create and populate an ext4 filesystem, corrupt a big symlink, then see how the kernel and e2fsck deal with it. (They won't) Override the default cleanup function..

Important APIs/types/functions: test tags `fuzzers`; common harness imports `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`; requirements/fixed gates `_exclude_fs ext2`, `_exclude_fs ext3`, `_require_scratch`, `_require_attrs`; helper functions `_cleanup()`; key variables `TESTDIR="${SCRATCH_MNT}/scratchdir"`, `TESTFILE="${TESTDIR}/testfile"`, `blksz="$(stat -f -c '%s' "${SCRATCH_MNT}")"`, `str="$(perl -e "print './' x $(( (blksz / 2) - 16));")x"`.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `_cleanup()`. Representative operation sequence: L28: test -n "${FORCE_FUZZ}" || _require_scratch_ext4_crc; L35: _scratch_mkfs -O has_journal >> $seqres.full 2>&1; L38: _scratch_mount; L50: e2fsck -fn "${SCRATCH_DEV}" >> $seqres.full 2>&1 || _fail "fsck should not fail"; L53: debugfs -w -R 'zap -f /long_symlink -p 0x62 0' "${SCRATCH_DEV}" 2> /dev/null; L56: _scratch_mount 2> /dev/null; L61: e2fsck -fy "${SCRATCH_DEV}" >> $seqres.full 2>&1; L64: _scratch_mount; L69: e2fsck -fn "${SCRATCH_DEV}" >> $seqres.full 2>&1 || _fail "fsck should not fail".

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; edits or inspects ext metadata directly; uses fsck as the final persistence/integrity oracle.

Dependencies and integration points: Depends on xfstests common libraries. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: depends on exact e2fsck/kernel reactions to damaged ext4 metadata.

Test signals: clean e2fsck verification; mount/statfs option visibility; visible subtest labels include + create scratch fs; + mount fs image; + make some files; + check fs; + corrupt image; + mount image.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/019 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/020 -->
# sources/test-tools/xfstests/tests/ext4/020

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ext4/020_research.md`.

Source read: 56 lines, SHA256 prefix `984bc16f71969320`.

Purpose: FS QA Test 020 Test partial blocksize defrag integrity issue. Calling EXT4_IOC_MOVE_EXTENT on file not aligned with block size and block size is smaller than page size would cause integrity issue on the partial-blocksize part when copying data between orign file and donor file. Import common functions..

Important APIs/types/functions: test tags `auto quick ioctl rw defrag`; common harness imports `. ./common/preamble`, `. ./common/filter`, `. ./common/defrag`; requirements/fixed gates `_exclude_fs ext2`, `_exclude_fs ext3`, `_require_scratch`, `_require_defrag`, `_require_test_program "e4compact"`; key variables `e4compact=$here/src/e4compact`, `testfile=$SCRATCH_MNT/$seq.orig`, `donorfile=$SCRATCH_MNT/$seq.donor`.

Control flow: The script is mostly straight-line after harness setup. Representative operation sequence: L31: _scratch_mkfs >>$seqres.full 2>&1; L32: _scratch_mount; L36: $XFS_IO_PROG -fc "pwrite -S 0xaa 0 1m" -c "fsync" $donorfile | _filter_xfs_io; L40: $XFS_IO_PROG -fc "pwrite -S 0xbb 0 1023" -c "fsync" $testfile | _filter_xfs_io; L43: md5sum $testfile > $tmp.md5sum; L52: md5sum -c $tmp.md5sum | _filter_scratch.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; drops page cache to force media-backed reads.

Dependencies and integration points: Depends on xfstests common libraries, xfs_io workload commands. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: requires privileged cache dropping and can perturb the host.

Test signals: matching file digests before and after remount/send/receive; visible subtest labels include 3 > /proc/sys/vm/drop_caches.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/020 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/021 -->
# sources/test-tools/xfstests/tests/ext4/021

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ext4/021_research.md`.

Source read: 84 lines, SHA256 prefix `ac51163ed08dbe9a`.

Purpose: FS QA Test 021 Regression test for commit: 688f869 ext4: Initialize fsync transaction ids in ext4_new_inode() Import common functions..

Important APIs/types/functions: test tags `auto quick`; common harness imports `. ./common/preamble`; requirements/fixed gates `_exclude_fs ext2`, `_exclude_fs ext3`, `_require_scratch`, `_require_dumpe2fs`, `_require_metadata_journaling $SCRATCH_DEV`; helper functions `do_fdatasync_work()`; key variables `blocksize=$(_get_block_size $SCRATCH_MNT)`, `fssize=$((2560 * $blocksize))`, `offset=0`, `found=0`, `magic="c0 3b 39 98"`, `found=1`, `offset=$((offset + blocksize))`, `trans_id=`$DUMPE2FS_PROG $SCRATCH_DEV 2>/dev/null | grep "Journal sequence" | \`, `datasync_work_pid=$!`.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `do_fdatasync_work()`. Representative operation sequence: L19: _require_dumpe2fs; L21: _scratch_mkfs >> $seqres.full 2>&1; L22: _scratch_mount; L24: _scratch_unmount; L28: _scratch_mkfs_sized $fssize >> $seqres.full 2>&1; L55: $XFS_IO_PROG -c "pwrite -S 0x81 $((offset+24)) 1" \; L60: trans_id=`$DUMPE2FS_PROG $SCRATCH_DEV 2>/dev/null | grep "Journal sequence" | \; L63: _scratch_mount; L72: $XFS_IO_PROG -f -c "fdatasync" $SCRATCH_MNT/testfile.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems.

Dependencies and integration points: Depends on xfstests common libraries, xfs_io workload commands, e2fsprogs debug/fsck utilities. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: contains timing-sensitive waits.

Test signals: visible subtest labels include Found no journal.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/021 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/022 -->
# sources/test-tools/xfstests/tests/ext4/022

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ext4/022_research.md`.

Source read: 155 lines, SHA256 prefix `01fe9436de61bcef`.

Purpose: FS QA Test 022 Test extending of i_extra_isize code.

Important APIs/types/functions: test tags `auto quick attr dangerous`; common harness imports `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`; requirements/fixed gates `_exclude_fs ext2`, `_exclude_fs ext3`, `_require_scratch`, `_require_dumpe2fs`, `_require_command "$DEBUGFS_PROG" debugfs`, `_require_attrs`, `_exclude_scratch_mount_option dax`; helper functions `do_setfattr()`, `create_xattr_file()`; key variables `BLOCK_SIZE=4096`, `INODE_SIZE=1024`, `XATTR_SPACE=256`, `GROW_EXTRA_ISIZE=80`, `GROW_MIN_EXTRA_ISIZE=16`, `ISIZE=$($DUMPE2FS_PROG -h $SCRATCH_DEV 2>/dev/null |`, `BLOCK_XATTR_SPACE=$(($BLOCK_SIZE - 36))`, `GOOD_OLD_ISIZE=128`, `WANT_ISIZE=$(($INODE_SIZE-$GOOD_OLD_ISIZE-$XATTR_SPACE))`, `NEW_ISIZE=$(($WANT_ISIZE+$GROW_EXTRA_ISIZE))`.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `do_setfattr()`, `create_xattr_file()`. Representative operation sequence: L25: _require_dumpe2fs; L26: _require_command "$DEBUGFS_PROG" debugfs; L32: _exclude_scratch_mount_option dax; L44: _scratch_mkfs >> $seqres.full 2>&1; L46: ISIZE=$($DUMPE2FS_PROG -h $SCRATCH_DEV 2>/dev/null |; L59: $DEBUGFS_PROG -w -R "ssv want_extra_isize $WANT_ISIZE" $SCRATCH_DEV >> $seqres.full 2>&1; L60: $DEBUGFS_PROG -w -R "ssv min_extra_isize $WANT_ISIZE" $SCRATCH_DEV >> $seqres.full 2>&1; L62: _scratch_mount; L125: _scratch_unmount; L129: $DEBUGFS_PROG -w -R "ssv want_extra_isize $NEW_ISIZE" $SCRATCH_DEV >> $seqres.full 2>&1; L130: $DEBUGFS_PROG -w -R "ssv min_extra_isize $NEW_MIN_ISIZE" $SCRATCH_DEV >> $seqres.full 2>&1; L132: _scratch_mount; L145: _scratch_unmount; L149: $DEBUGFS_PROG -R "stat $FILE" $SCRATCH_DEV 2>/dev/null | \.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; edits or inspects ext metadata directly.

Dependencies and integration points: Depends on xfstests common libraries, e2fsprogs debug/fsck utilities. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: depends on xfstests harness requirements and exact golden-output filtering.

Test signals: successful script exit with xfstests filtered output.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/022 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/023 -->
# sources/test-tools/xfstests/tests/ext4/023

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ext4/023_research.md`.

Source read: 34 lines, SHA256 prefix `dd2bcedac4a0d644`.

Purpose: FS QA Test No. 023 Ensure that the populate helpers actually /can/ populate a ext4 filesystem with all types of metadata and create an image of the metadata. Check that fsck is happy with the resulting fs..

Important APIs/types/functions: test tags `auto quick scrub`; common harness imports `. ./common/preamble`, `. ./common/filter`, `. ./common/populate`, `. ./common/fuzzy`; requirements/fixed gates `_exclude_fs ext2`, `_exclude_fs ext3`, `_require_scratch`.

Control flow: The script is mostly straight-line after harness setup. Representative operation sequence: L27: _scratch_populate_cached > $seqres.full 2>&1; L30: _scratch_mount >> $seqres.full 2>&1.

State and persistence behavior: mounts and unmounts test filesystems.

Dependencies and integration points: Depends on xfstests common libraries. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: depends on xfstests harness requirements and exact golden-output filtering.

Test signals: visible subtest labels include Format and populate; Mount.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/023 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/024 -->
# sources/test-tools/xfstests/tests/ext4/024

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ext4/024_research.md`.

Source read: 53 lines, SHA256 prefix `5e45cbcfd70b7ac9`.

Purpose: FS QA Test ext4/024 Regression test for 0d06863f903a ("ext4: don't BUG when truncating encrypted inodes on the orphan list"). get standard environment and checks.

Important APIs/types/functions: test tags `auto quick encrypt dangerous`; common harness imports `. ./common/preamble`, `. ./common/encrypt`; requirements/fixed gates `_exclude_fs ext2`, `_exclude_fs ext3`, `_require_scratch_encryption`, `_require_command "$KEYCTL_PROG" keyctl`; key variables `keydesc=$(_generate_session_encryption_key)`, `inum=$(stat -c '%i' $SCRATCH_MNT/edir/file)`.

Control flow: The script is mostly straight-line after harness setup. Representative operation sequence: L19: _require_scratch_encryption; L37: _scratch_mkfs_encrypted &>>$seqres.full; L38: _scratch_mount; L44: _scratch_unmount; L45: debugfs -w -R "set_super_value s_last_orphan $inum" $SCRATCH_DEV &>>$seqres.full; L48: _try_scratch_mount.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; edits or inspects ext metadata directly.

Dependencies and integration points: Depends on xfstests common libraries. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: depends on xfstests harness requirements and exact golden-output filtering.

Test signals: visible subtest labels include Didn't crash!.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/024 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/025 -->
# sources/test-tools/xfstests/tests/ext4/025

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ext4/025_research.md`.

Source read: 35 lines, SHA256 prefix `0d1e497a91c27891`.

Purpose: FS QA Test ext4/025 Regression test for commit: 3a4b77c ("ext4: validate s_first_meta_bg at mount time"). get standard environment and checks.

Important APIs/types/functions: test tags `auto quick fuzzers dangerous`; common harness imports `. ./common/preamble`, `. ./common/filter`; requirements/fixed gates `_exclude_fs ext2`, `_exclude_fs ext3`, `_require_scratch_nocheck`, `_require_command "$DEBUGFS_PROG" debugfs`, `_require_scratch_ext4_feature "bigalloc,meta_bg,^resize_inode"`.

Control flow: The script is mostly straight-line after harness setup. Representative operation sequence: L19: _require_scratch_nocheck; L20: _require_command "$DEBUGFS_PROG" debugfs; L21: _require_scratch_ext4_feature "bigalloc,meta_bg,^resize_inode"; L24: _scratch_mkfs "-O bigalloc,meta_bg,^resize_inode" >> $seqres.full 2>&1; L28: $DEBUGFS_PROG -w -R "ssv first_meta_bg 842150400" $SCRATCH_DEV >> $seqres.full 2>&1; L31: _try_scratch_mount >> $seqres.full 2>&1 || echo "Fail to mount ext4 fs expectedly".

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; edits or inspects ext metadata directly.

Dependencies and integration points: Depends on xfstests common libraries, e2fsprogs debug/fsck utilities. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: depends on exact e2fsck/kernel reactions to damaged ext4 metadata; bypasses normal scratch checking because corruption is intentional.

Test signals: visible subtest labels include Create ext4 fs and modify first_meta_bg's value; Try to mount a modified ext4 fs.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/025 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/026 -->
# sources/test-tools/xfstests/tests/ext4/026

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ext4/026_research.md`.

Source read: 108 lines, SHA256 prefix `2425678ae6864fa0`.

Purpose: FS QA Test 026 Test for ea_inode feature in ext4. Without ea_inode feature, an extended attribute in ext4 cannot be larger than the fs block size. ea_inode feature allows storing xattr values in external inodes and so raises xattr value size limit to 64k. Import common functions..

Important APIs/types/functions: test tags `auto quick attr`; common harness imports `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`; requirements/fixed gates `_exclude_fs ext2`, `_exclude_fs ext3`, `_require_scratch`, `_require_attrs`, `_require_scratch_ext4_feature "ea_inode"`; helper functions `attr_set()`, `attr_list()`, `attr_remove()`; key variables `tmp=$(_getfattr --absolute-names --only-values -n $name $file)`, `y=$SCRATCH_MNT/y`, `z=$SCRATCH_MNT/z`, `name_in_ibody=user.i`, `name_in_block=user.$(perl -e 'print "b" x 100;')`.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `attr_set()`, `attr_list()`, `attr_remove()`. Representative operation sequence: L24: _require_scratch_ext4_feature "ea_inode"; L26: _scratch_mkfs_ext4 -O ea_inode >/dev/null 2>&1; L27: _scratch_mount.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems.

Dependencies and integration points: Depends on xfstests common libraries. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: depends on xfstests harness requirements and exact golden-output filtering.

Test signals: successful script exit with xfstests filtered output.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/026 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/027 -->
# sources/test-tools/xfstests/tests/ext4/027

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ext4/027_research.md`.

Source read: 56 lines, SHA256 prefix `9387b3e7bbd2242d`.

Purpose: FS QA Test No. 027 Check that getfsmap reports the BG metadata we're expecting. Override the default cleanup function..

Important APIs/types/functions: test tags `auto quick fsmap`; common harness imports `. ./common/preamble`, `. ./common/filter`; requirements/fixed gates `_exclude_fs ext2`, `_exclude_fs ext3`, `_require_scratch`, `_require_xfs_io_command "fsmap"`; helper functions `_cleanup()`.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `_cleanup()`. Representative operation sequence: L31: _scratch_mkfs > "$seqres.full" 2>&1; L32: _scratch_mount; L35: $XFS_IO_PROG -c 'fsmap' $SCRATCH_MNT > $TEST_DIR/fsmap.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems.

Dependencies and integration points: Depends on xfstests common libraries, xfs_io workload commands. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: depends on xfstests harness requirements and exact golden-output filtering.

Test signals: visible subtest labels include Format and mount.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/027 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/028 -->
# sources/test-tools/xfstests/tests/ext4/028

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ext4/028_research.md`.

Source read: 46 lines, SHA256 prefix `5281742b759a3368`.

Purpose: FS QA Test No. 028 Populate filesystem, check that fsmap -n10000 matches fsmap -n1. Override the default cleanup function..

Important APIs/types/functions: test tags `auto quick fsmap`; common harness imports `. ./common/preamble`, `. ./common/filter`, `. ./common/populate`; requirements/fixed gates `_exclude_fs ext2`, `_exclude_fs ext3`, `_require_scratch`, `_require_scratch_ext4_feature_enabled "extent"`, `_require_populate_commands`, `_require_xfs_io_command "fsmap"`; helper functions `_cleanup()`.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `_cleanup()`. Representative operation sequence: L27: _require_scratch_ext4_feature_enabled "extent"; L34: _scratch_populate_cached nofill > $seqres.full 2>&1; L37: _scratch_mount; L38: $XFS_IO_PROG -c 'fsmap -n 65536' $SCRATCH_MNT | grep -v 'EXT:' > $TEST_DIR/a; L39: $XFS_IO_PROG -c 'fsmap -n 1' $SCRATCH_MNT | grep -v 'EXT:' > $TEST_DIR/b; L42: diff -uw $TEST_DIR/a $TEST_DIR/b.

State and persistence behavior: mounts and unmounts test filesystems.

Dependencies and integration points: Depends on xfstests common libraries, xfs_io workload commands. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: depends on xfstests harness requirements and exact golden-output filtering.

Test signals: byte-for-byte compare of copied or restored data; visible subtest labels include Format and mount.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/028 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/029 -->
# sources/test-tools/xfstests/tests/ext4/029

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ext4/029_research.md`.

Source read: 46 lines, SHA256 prefix `9758db059032daa9`.

Purpose: FS QA Test No. 029 Check that getfsmap reports external log devices Override the default cleanup function..

Important APIs/types/functions: test tags `auto quick fsmap`; common harness imports `. ./common/preamble`, `. ./common/filter`; requirements/fixed gates `_exclude_fs ext2`, `_exclude_fs ext3`, `_require_logdev`, `_require_scratch`, `_require_xfs_io_command "fsmap"`; helper functions `_cleanup()`; key variables `data_dev=$(grep 'static fs metadata' $TEST_DIR/fsmap | head -n 1 | awk '{print $2}')`, `journal_dev=$(grep 'journalling log' $TEST_DIR/fsmap | head -n 1 | awk '{print $2}')`.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `_cleanup()`. Representative operation sequence: L32: _scratch_mkfs > "$seqres.full" 2>&1; L33: _scratch_mount; L36: $XFS_IO_PROG -c 'fsmap' $SCRATCH_MNT >> $seqres.full; L37: $XFS_IO_PROG -c 'fsmap' $SCRATCH_MNT | tr '[]()' ' ' > $TEST_DIR/fsmap.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems.

Dependencies and integration points: Depends on xfstests common libraries, xfs_io workload commands. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: depends on xfstests harness requirements and exact golden-output filtering.

Test signals: visible subtest labels include Format and mount; Check device field of FS metadata and journalling log.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/029 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/030 -->
# sources/test-tools/xfstests/tests/ext4/030

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ext4/030_research.md`.

Source read: 43 lines, SHA256 prefix `b6f283063578cf24`.

Purpose: FS QA Test ext4/030 This is a regression test for kernel patch: ext4: prevent data corruption with journaling + DAX created by Ross Zwisler <ross.zwisler@linux.intel.com> Import common functions. Modify as appropriate..

Important APIs/types/functions: test tags `auto quick dax`; common harness imports `. ./common/preamble`, `. ./common/filter`; requirements/fixed gates `_exclude_fs ext2`, `_exclude_fs ext3`, `_require_scratch_dax_mountopt "dax"`, `_require_test_program "t_ext4_dax_journal_corruption"`, `_require_command "$CHATTR_PROG" chattr`.

Control flow: The script is mostly straight-line after harness setup. Representative operation sequence: L21: _require_scratch_dax_mountopt "dax"; L25: _scratch_mkfs > $seqres.full 2>&1; L31: _scratch_mount "-o dax,nodelalloc" >> $seqres.full 2>&1.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems.

Dependencies and integration points: Depends on xfstests common libraries. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: depends on xfstests harness requirements and exact golden-output filtering.

Test signals: no unexpected stdout beyond the golden quiet marker; visible subtest labels include Silence is golden.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/030 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/031 -->
# sources/test-tools/xfstests/tests/ext4/031

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ext4/031_research.md`.

Source read: 55 lines, SHA256 prefix `a3b69874fcf1238f`.

Purpose: FS QA Test ext4/031 This is a regression test for kernel patch: ext4: prevent data corruption with inline data + DAX created by Ross Zwisler <ross.zwisler@linux.intel.com> Import common functions. DAX needs to be off so we can create an inode with inline data.

Important APIs/types/functions: test tags `auto quick dax`; common harness imports `. ./common/preamble`, `. ./common/filter`; requirements/fixed gates `_exclude_fs ext2`, `_exclude_fs ext3`, `_require_scratch_dax_mountopt "dax"`, `_require_test_program "t_ext4_dax_inline_corruption"`, `_require_scratch_ext4_feature "inline_data"`; key variables `SAVE_MOUNT_OPTIONS="$MOUNT_OPTIONS"`, `MOUNT_OPTIONS=""`, `TESTFILE=$SCRATCH_MNT/testfile`.

Control flow: The script is mostly straight-line after harness setup. Representative operation sequence: L25: _require_scratch_dax_mountopt "dax"; L27: _require_scratch_ext4_feature "inline_data"; L29: _scratch_mkfs_ext4 -O inline_data > $seqres.full 2>&1; L33: _scratch_mount >> $seqres.full 2>&1; L39: _scratch_unmount >> $seqres.full 2>&1; L40: _try_scratch_mount "-o dax" >> $seqres.full 2>&1.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems.

Dependencies and integration points: Depends on xfstests common libraries. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: depends on xfstests harness requirements and exact golden-output filtering.

Test signals: no unexpected stdout beyond the golden quiet marker; visible subtest labels include Silence is golden; Silence is golden.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/031 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/032 -->
# sources/test-tools/xfstests/tests/ext4/032

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ext4/032_research.md`.

Source read: 149 lines, SHA256 prefix `17fd1e3b6ab7ef6e`.

Purpose: FS QA Test ext4/032 Ext4 online resize tests of small and crucial resizes with bigalloc feature..

Important APIs/types/functions: test tags `auto quick ioctl resize`; common harness imports `. ./common/preamble`; requirements/fixed gates `_fixed_by_kernel_commit 6121258c2b33 \`, `_exclude_fs ext2`, `_exclude_fs ext3`, `_require_loop`, `_require_scratch`, `_require_scratch_ext4_feature "bigalloc,resize_inode"`, `_require_command "$RESIZE2FS_PROG" resize2fs`; helper functions `c2b()`, `ext4_online_resize()`, `_cleanup()`; key variables `BLK_SIZ=4096`, `CLUSTER_SIZ=4096`, `IMG_FILE=$SCRATCH_MNT/$seq.fs`, `IMG_MNT=$SCRATCH_MNT/$seq.mnt`, `LOOP_DEVICE=`_create_loop_device $IMG_FILE``.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `c2b()`, `ext4_online_resize()`, `_cleanup()`. Representative operation sequence: L40: $XFS_IO_PROG -f -c "truncate $(($final_size * $BLK_SIZ))" ${IMG_FILE}; L56: $RESIZE2FS_PROG -f ${LOOP_DEVICE} $final_size >$tmp.resize2fs 2>&1; L59: grep -iq "operation not supported" $tmp.resize2fs \; L64: cat $tmp.resize2fs >> $seqres.full; L69: _check_dev_fs $LOOP_DEVICE >> $seqres.full 2>&1 || \; L93: _require_scratch_ext4_feature "bigalloc,resize_inode"; L94: _require_command "$RESIZE2FS_PROG" resize2fs; L96: _scratch_mkfs >>$seqres.full 2>&1; L97: _scratch_mount.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; resizes filesystem images or online filesystems; creates loop devices or image-backed devices.

Dependencies and integration points: Depends on xfstests common libraries, xfs_io workload commands. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: loop-device cleanup must run to avoid leaked devices; is tied to specific kernel-regression behavior noted by fixed-by annotations.

Test signals: successful script exit with xfstests filtered output.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/032 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/033 -->
# sources/test-tools/xfstests/tests/ext4/033

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ext4/033_research.md`.

Source read: 105 lines, SHA256 prefix `f267fdf9b05dfbd1`.

Purpose: FS QA Test 033 Test s_inodes_count overflow for huge filesystems. This bug was fixed by commit 4f2f76f75143 ("ext4: Forbid overflowing inode count when resizing".) Override the default cleanup function..

Important APIs/types/functions: test tags `auto ioctl resize`; common harness imports `. ./common/preamble`, `. ./common/filter`, `. ./common/dmhugedisk`; requirements/fixed gates `_exclude_fs ext2`, `_exclude_fs ext3`, `_require_scratch_nocheck`, `_require_dmhugedisk`, `_require_dumpe2fs`, `_require_test_program ext4_resize`; helper functions `_cleanup()`; key variables `EXT4_RESIZE=$here/src/ext4_resize`, `devsize=$(blockdev --getsize64 $SCRATCH_DEV)`, `blksz="$(_get_block_size $SCRATCH_MNT)"`, `inodes_per_group=$((blksz*8))`, `group_blocks=$((blksz*8))`, `limit_groups=$(((1<<32)/inodes_per_group))`, `group_count=$((limit_groups - 16))`.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `_cleanup()`. Representative operation sequence: L30: _require_scratch_nocheck; L32: _require_dumpe2fs; L45: _scratch_mkfs >/dev/null 2>&1; L46: _scratch_mount >> $seqres.full; L48: _scratch_unmount; L68: _mount $DMHUGEDISK_DEV $SCRATCH_MNT; L71: $DUMPE2FS_PROG -h $DMHUGEDISK_DEV >> $seqres.full 2>&1; L92: $DUMPE2FS_PROG -h $DMHUGEDISK_DEV >> $seqres.full 2>&1.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; resizes filesystem images or online filesystems.

Dependencies and integration points: Depends on xfstests common libraries, e2fsprogs debug/fsck utilities. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: bypasses normal scratch checking because corruption is intentional.

Test signals: visible subtest labels include Figure out block size; Format huge device; Resizing to inode limit + 1...; Resizing succeeded but it should fail!; Resizing to max group count...; Resizing failed!.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/033 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/034 -->
# sources/test-tools/xfstests/tests/ext4/034

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ext4/034_research.md`.

Source read: 63 lines, SHA256 prefix `ea6edeb791a61d44`.

Purpose: FS QA Test 034 Regression test for a ENOSPC warning when both quota and "-o dioread_nolock,nodelalloc" is used. The bug was fixed by commit "ext4: make sure enough credits are reserved for dioread_nolock writes" Import common functions. Modify as appropriate..

Important APIs/types/functions: test tags `auto quick quota fiemap prealloc`; common harness imports `. ./common/preamble`, `. ./common/filter`, `. ./common/quota`; requirements/fixed gates `_exclude_fs ext2`, `_exclude_fs ext3`, `_require_scratch`, `_require_quota`, `_require_nobody`, `_require_xfs_io_command "falloc"`, `_require_xfs_io_command "fiemap"`, `_require_xfs_io_command "syncfs"`.

Control flow: The script is mostly straight-line after harness setup. Representative operation sequence: L14: _begin_fstest auto quick quota fiemap prealloc; L27: _require_xfs_io_command "falloc"; L28: _require_xfs_io_command "fiemap"; L32: _scratch_mkfs "-O quota" > $seqres.full 2>&1; L33: _scratch_mount "-o dioread_nolock,nodelalloc" > $seqres.full 2>&1; L44: $XFS_IO_PROG -f -c "pwrite 0 4k" -c "falloc 4k 4k" -c "pwrite 8k 4k" \; L48: $XFS_IO_PROG -c "fiemap -v" $SCRATCH_MNT/foobar >> $seqres.full; L51: $XFS_IO_PROG -c "pwrite 4k 4k" $SCRATCH_MNT/foobar >> $seqres.full; L54: $XFS_IO_PROG -f -c "pwrite 0 4k" -c "fsync" $SCRATCH_MNT/dummy >> $seqres.full; L59: $XFS_IO_PROG -c "syncfs" $SCRATCH_MNT >> $seqres.full.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; changes quota/qgroup accounting state.

Dependencies and integration points: Depends on xfstests common libraries, xfs_io workload commands, quota userspace tools. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: quota accounting regressions can be silent until unmount or rescan.

Test signals: fiemap extent layout and flags; visible subtest labels include Format and mount; Create the original file; Set hard quota; Create 2 level extent tree (btree) for foobar with a unwritten extent; Convert unwritten extent to written and collapse extent tree to inode; Create a new file and do fsync to force a jbd2 commit.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/034 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/035 -->
# sources/test-tools/xfstests/tests/ext4/035

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ext4/035_research.md`.

Source read: 46 lines, SHA256 prefix `04b30048289a9420`.

Purpose: FSQA Test No. 035 Regression test for commit: f96c3ac8dfc2 ("ext4: fix crash during online resizing") This case tests a loss s_first_data_block on ext4 when computing maximum size with given number of group descriptor blocks. Filesystem with non-zero s_first_data_block can happen that computed maximum size lower than current size and leads to a BUG_ON in in ext4_alloc_group_tables() hitting on flex_gd->count == 0. Import common functions..

Important APIs/types/functions: test tags `auto quick resize`; common harness imports `. ./common/preamble`, `. ./common/filter`; requirements/fixed gates `_exclude_fs ext2`, `_exclude_fs ext3`, `_require_scratch`, `_exclude_scratch_mount_option dax`, `_require_command "$RESIZE2FS_PROG" resize2fs`; key variables `encrypt="-O encrypt"`.

Control flow: The script is mostly straight-line after harness setup. Representative operation sequence: L25: _exclude_scratch_mount_option dax; L26: _require_command "$RESIZE2FS_PROG" resize2fs; L36: _scratch_mount; L39: $RESIZE2FS_PROG $SCRATCH_DEV 262145 >> $seqres.full 2>&1; L42: $RESIZE2FS_PROG $SCRATCH_DEV 300000 >> $seqres.full 2>&1.

State and persistence behavior: mounts and unmounts test filesystems; resizes filesystem images or online filesystems.

Dependencies and integration points: Depends on xfstests common libraries, ext-family mkfs/tune utilities. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: depends on xfstests harness requirements and exact golden-output filtering.

Test signals: visible subtest labels include Resizing to 262145 blocks; Resizing to 300000 blocks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/035 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/036 -->
# sources/test-tools/xfstests/tests/ext4/036

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ext4/036_research.md`.

Source read: 41 lines, SHA256 prefix `9e59dd851e40bb6f`.

Purpose: FS QA Test No. ext4/036 Test truncate orphan inodes when mounting ext4 ext4 used to hit WARNING, this commit fixed the issue 721e3eb ext4: lock i_mutex when truncating orphan inodes Import common functions..

Important APIs/types/functions: test tags `auto quick`; common harness imports `. ./common/preamble`, `. ./common/filter`; requirements/fixed gates `_exclude_fs ext2`, `_require_scratch`; key variables `testfile=$SCRATCH_MNT/testfile`, `inode=`ls -i $testfile | awk '{print $1}'``.

Control flow: The script is mostly straight-line after harness setup. Representative operation sequence: L24: _scratch_mkfs_sized $((16*1024*1024)) >>$seqres.full 2>&1; L25: _scratch_mount; L33: _scratch_unmount; L34: debugfs -w -R "set_super_value last_orphan $inode" $SCRATCH_DEV \; L38: _scratch_mount.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; edits or inspects ext metadata directly.

Dependencies and integration points: Depends on xfstests common libraries. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: depends on xfstests harness requirements and exact golden-output filtering.

Test signals: no unexpected stdout beyond the golden quiet marker; absence or presence of expected dmesg warnings; visible subtest labels include Silence is golden.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/036 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/037 -->
# sources/test-tools/xfstests/tests/ext4/037

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ext4/037_research.md`.

Source read: 36 lines, SHA256 prefix `649a5f1ba0976202`.

Purpose: FS QA Test ext4/037 Test mount a needs_recovery partition with noload option. ext4 used to Oops until part of this commit: 744692d ext4: use ext4_get_block_write in buffer write Import common functions..

Important APIs/types/functions: test tags `auto quick`; common harness imports `. ./common/preamble`, `. ./common/filter`; requirements/fixed gates `_exclude_fs ext2`, `_require_scratch_nocheck`.

Control flow: The script is mostly straight-line after harness setup. Representative operation sequence: L21: _require_scratch_nocheck; L25: _scratch_mkfs >>$seqres.full 2>&1; L28: debugfs -w -R "feature +needs_recovery" $SCRATCH_DEV \; L32: _try_scratch_mount "-o noload" >>$seqres.full 2>&1.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; edits or inspects ext metadata directly.

Dependencies and integration points: Depends on xfstests common libraries. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: bypasses normal scratch checking because corruption is intentional.

Test signals: no unexpected stdout beyond the golden quiet marker; visible subtest labels include Silence is golden.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/037 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/038 -->
# sources/test-tools/xfstests/tests/ext4/038

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ext4/038_research.md`.

Source read: 32 lines, SHA256 prefix `ebceae985522ea8b`.

Purpose: FS QA Test ext4/038 Regression test for commit: c9eb13a ext4: fix hang when processing corrupted orphaned inode list.

Important APIs/types/functions: test tags `auto quick`; common harness imports `. ./common/preamble`; requirements/fixed gates `_exclude_fs ext2`, `_require_scratch`, `_require_command "$DEBUGFS_PROG" debugfs`.

Control flow: The script is mostly straight-line after harness setup. Representative operation sequence: L16: _require_command "$DEBUGFS_PROG" debugfs; L24: _scratch_mkfs_sized $((16 * 1024 * 1024)) >>$seqres.full 2>&1; L25: $DEBUGFS_PROG -w -R "ssv last_orphan $i" $SCRATCH_DEV >>$seqres.full 2>&1; L26: _scratch_mount; L27: _scratch_unmount.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; edits or inspects ext metadata directly.

Dependencies and integration points: Depends on xfstests common libraries, e2fsprogs debug/fsck utilities. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: depends on xfstests harness requirements and exact golden-output filtering.

Test signals: no unexpected stdout beyond the golden quiet marker; visible subtest labels include Silence is golden.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/038 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/039 -->
# sources/test-tools/xfstests/tests/ext4/039

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ext4/039_research.md`.

Source read: 81 lines, SHA256 prefix `8673ecea49839ecc`.

Purpose: FSQA Test No. ext4/039 Test data journaling flag switch for a single file ext3 and ext4 don't support direct IO in journalling mode.

Important APIs/types/functions: test tags `auto enospc rw`; common harness imports `. ./common/preamble`, `. ./common/filter`; requirements/fixed gates `_exclude_fs ext2`, `_require_scratch`, `_exclude_scratch_mount_option dax`; helper functions `_workout()`; key variables `write_opt_list="iflag=noatime conv=notrunc conv=fsync"`, `chattr_opt_list="+j -j +jS -j"`, `idx=0`, `idx=$((idx + 1))`, `bs=1M count=4 $write_opt \`, `idx=$((idx + 1))`, `bs=1M $write_opt >> $seqres.full 2>&1`.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `_workout()`. Representative operation sequence: L62: _exclude_scratch_mount_option dax; L64: _scratch_mkfs_sized $((64 * 1024 * 1024)) >> $seqres.full 2>&1; L65: _scratch_mount; L69: _scratch_unmount; L74: if ! _scratch_unmount; then.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems.

Dependencies and integration points: Depends on xfstests common libraries. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: depends on xfstests harness requirements and exact golden-output filtering.

Test signals: no unexpected stdout beyond the golden quiet marker; visible subtest labels include Switch data journalling mode. Silence is golden.; workout failed; failed to umount; Check filesystem.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/039 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/040 -->
# sources/test-tools/xfstests/tests/ext4/040

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ext4/040_research.md`.

Source read: 50 lines, SHA256 prefix `59d5ae4aec4157b0`.

Purpose: FSQA Test No. ext4/040 (was shared/005) Since loff_t is a signed type, it is invalid for a filesystem to load an inode with i_size = -1ULL. Unfortunately, nobody checks this, which means that we can trivially DoS the VFS by creating such a file and appending to it. This causes an integer overflow in the routines underlying writeback, which results in the kernel locking up. So, create this malformed inode and try a buffered append to make sure we catch this situation..

Important APIs/types/functions: test tags `dangerous_fuzzers`; common harness imports `. ./common/preamble`, `. ./common/filter`; requirements/fixed gates `_require_scratch_nocheck`, `_require_command "$DEBUGFS_PROG"`; key variables `PIDS=""`, `testdir=$SCRATCH_MNT`.

Control flow: The script is mostly straight-line after harness setup. Representative operation sequence: L24: _require_scratch_nocheck; L26: _require_command "$DEBUGFS_PROG"; L29: _scratch_mkfs >> $seqres.full 2>&1; L30: _scratch_mount; L36: _scratch_unmount; L37: $DEBUGFS_PROG -w -R "sif /a size -1" $SCRATCH_DEV >> $seqres.full 2>&1; L40: $DEBUGFS_PROG -R "stat /a" $SCRATCH_DEV 2>&1 | grep -q "Size: 18446744073709551615" || \; L44: _scratch_mount.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; edits or inspects ext metadata directly.

Dependencies and integration points: Depends on xfstests common libraries, e2fsprogs debug/fsck utilities. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: deliberately corrupts metadata and can trigger kernel failure paths; bypasses normal scratch checking because corruption is intentional.

Test signals: visible subtest labels include Format and mount; Corrupt filesystem; Remount, try to append.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/040 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/041 -->
# sources/test-tools/xfstests/tests/ext4/041

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ext4/041_research.md`.

Source read: 52 lines, SHA256 prefix `e3ea2245c25168f9`.

Purpose: FSQA Test No. ext4/041 (was shared/007) Since loff_t is a signed type, it is invalid for a filesystem to load an inode with i_size = -1ULL. Unfortunately, nobody checks this, which means that we can trivially DoS the VFS by creating such a file and appending to it. This causes an integer overflow in the routines underlying writeback, which results in the kernel locking up. So, create this malformed inode and try a dio append to make sure we catch this situation..

Important APIs/types/functions: test tags `dangerous_fuzzers`; common harness imports `. ./common/preamble`, `. ./common/filter`; requirements/fixed gates `_require_scratch_nocheck`, `_require_command "$DEBUGFS_PROG"`; key variables `PIDS=""`, `testdir=$SCRATCH_MNT`.

Control flow: The script is mostly straight-line after harness setup. Representative operation sequence: L24: _require_scratch_nocheck; L26: _require_command "$DEBUGFS_PROG"; L29: _scratch_mkfs >> $seqres.full 2>&1; L30: _scratch_mount; L36: _scratch_unmount; L39: $DEBUGFS_PROG -w -R "sif /a size 0xFFFFFFFFFFFFFE00" $SCRATCH_DEV >> $seqres.full 2>&1; L42: $DEBUGFS_PROG -R "stat /a" $SCRATCH_DEV 2>&1 | grep -q "Size: 18446744073709551104" || \; L46: _scratch_mount.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; edits or inspects ext metadata directly.

Dependencies and integration points: Depends on xfstests common libraries, e2fsprogs debug/fsck utilities. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: deliberately corrupts metadata and can trigger kernel failure paths; bypasses normal scratch checking because corruption is intentional.

Test signals: visible subtest labels include Format and mount; Corrupt filesystem; Remount, try to append.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/041 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/042 -->
# sources/test-tools/xfstests/tests/ext4/042

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ext4/042_research.md`.

Source read: 64 lines, SHA256 prefix `034a2729c4fa5aee`.

Purpose: FS QA Test No. ext4/042 (was shared/289) Test overhead & df output for extN filesystems Import common functions..

Important APIs/types/functions: test tags `auto quick`; common harness imports `. ./common/preamble`, `. ./common/filter`; requirements/fixed gates `_require_scratch`; key variables `TOTAL_BLOCKS=`dumpe2fs -h $SCRATCH_DEV 2>/dev/null \`, `FREE_BLOCKS=`dumpe2fs -h $SCRATCH_DEV 2>/dev/null \`, `OVERHEAD=$(($TOTAL_BLOCKS-$FREE_BLOCKS))`, `MINIX_F_BLOCKS=`stat -f $SCRATCH_MNT | awk '/^Blocks/{print $3}'``, `BSD_F_BLOCKS=`stat -f $SCRATCH_MNT | awk '/^Blocks/{print $3}'``.

Control flow: The script is mostly straight-line after harness setup. Representative operation sequence: L17: _scratch_mkfs >> $seqres.full 2>&1; L20: TOTAL_BLOCKS=`dumpe2fs -h $SCRATCH_DEV 2>/dev/null \; L23: FREE_BLOCKS=`dumpe2fs -h $SCRATCH_DEV 2>/dev/null \; L44: _scratch_mount "-o minixdf"; L46: _scratch_unmount; L48: _scratch_mount "-o bsddf"; L50: _scratch_unmount.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems.

Dependencies and integration points: Depends on xfstests common libraries. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: depends on xfstests harness requirements and exact golden-output filtering.

Test signals: mount/statfs option visibility.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/042 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/043 -->
# sources/test-tools/xfstests/tests/ext4/043

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ext4/043_research.md`.

Source read: 38 lines, SHA256 prefix `958ee187e7f81945`.

Purpose: FS QA Test No. 043 Test file timestamps are only precise to seconds with 128-byte inodes." Import common functions..

Important APIs/types/functions: test tags `auto quick`; common harness imports `. ./common/preamble`, `. ./common/filter`; requirements/fixed gates `_exclude_fs ext2`, `_require_scratch`, `_require_test_program "t_get_file_time"`; key variables `atime=`$here/src/t_get_file_time $SCRATCH_MNT/tmp_file atime nsec``, `mtime=`$here/src/t_get_file_time $SCRATCH_MNT/tmp_file mtime nsec``, `ctime=`$here/src/t_get_file_time $SCRATCH_MNT/tmp_file ctime nsec``.

Control flow: The script is mostly straight-line after harness setup. Representative operation sequence: L23: _scratch_mkfs -I 128 >> $seqres.full 2>&1; L24: _scratch_mount.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems.

Dependencies and integration points: Depends on xfstests common libraries. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: depends on xfstests harness requirements and exact golden-output filtering.

Test signals: no unexpected stdout beyond the golden quiet marker; visible subtest labels include Silence is golden; nsec should be zero when extended timestamps are disabled.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/043 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/044 -->
# sources/test-tools/xfstests/tests/ext4/044

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ext4/044_research.md`.

Source read: 72 lines, SHA256 prefix `5b283443dcfccf33`.

Purpose: FS QA Test No. 044 Test file timestamps are precise to nanoseconds with 256-byte inodes Import common functions..

Important APIs/types/functions: test tags `auto quick`; common harness imports `. ./common/preamble`, `. ./common/filter`; requirements/fixed gates `_exclude_fs ext2`, `_exclude_fs ext3`, `_require_scratch`, `_require_test_program "t_get_file_time"`, `_require_metadata_journaling`; key variables `cur_time=`date '+%s %N'``, `sec=`echo $cur_time | $AWK_PROG {'print $1'}``, `nsec=`echo $cur_time | $AWK_PROG {'print $2'}``, `sec_atime=`$here/src/t_get_file_time $SCRATCH_MNT/tmp_file atime sec``, `sec_mtime=`$here/src/t_get_file_time $SCRATCH_MNT/tmp_file mtime sec``, `sec_ctime=`$here/src/t_get_file_time $SCRATCH_MNT/tmp_file ctime sec``, `nsec_atime=`$here/src/t_get_file_time $SCRATCH_MNT/tmp_file atime nsec``, `nsec_mtime=`$here/src/t_get_file_time $SCRATCH_MNT/tmp_file mtime nsec``, `nsec_ctime=`$here/src/t_get_file_time $SCRATCH_MNT/tmp_file ctime nsec``, `nsec_atime2=`$here/src/t_get_file_time $SCRATCH_MNT/tmp_file atime nsec``.

Control flow: The script is mostly straight-line after harness setup. Representative operation sequence: L23: _scratch_mkfs -t ext3 -I 256 >> $seqres.full 2>&1; L24: _scratch_mount; L55: _scratch_unmount >> $seqres.full 2>&1; L60: _mount -t ext3 `_scratch_mount_options $*` >> $seqres.full 2>&1 && _scratch_unmount >> $seqres.full 2>&1; L61: _scratch_mount.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems.

Dependencies and integration points: Depends on xfstests common libraries. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: contains timing-sensitive waits.

Test signals: successful script exit with xfstests filtered output.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/044 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/045 -->
# sources/test-tools/xfstests/tests/ext4/045

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ext4/045_research.md`.

Source read: 95 lines, SHA256 prefix `7a00ee40792aba1c`.

Purpose: FS QA Test No. 045 Test subdirectory limit of ext4. We create more than 65000 subdirectories on the ext4 filesystem..

Important APIs/types/functions: test tags `auto dir`; common harness imports `. ./common/preamble`, `. ./common/filter`; requirements/fixed gates `_exclude_fs ext2`, `_exclude_fs ext3`, `_require_scratch`, `_require_scratch_ext4_feature large_dir`, `_require_test_program "t_create_short_dirs"`, `_require_test_program "t_create_long_dirs"`, `_require_dumpe2fs`; helper functions `workout()`; key variables `SHORT_DIR=1`, `LONG_DIR=2`, `dir_name_len="short name"`, `dir_name_len="long name"`, `nr_dirs=`ls $3 | wc -l``, `DIR_NUM=65537`, `DIR_LEN=( $SHORT_DIR $LONG_DIR )`, `PARENT_DIR="$SCRATCH_MNT/subdir"`.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `workout()`. Representative operation sequence: L23: _require_scratch_ext4_feature large_dir; L26: _require_dumpe2fs; L46: _scratch_mkfs "-O extent,dir_nlink,dir_index,large_dir -I 256" >> $seqres.full 2>&1; L47: _scratch_mount; L61: _scratch_unmount; L71: _scratch_unmount; L75: _scratch_unmount; L78: $DUMPE2FS_PROG -h $SCRATCH_DEV 2>> $seqres.full | grep '^Filesystem features' | grep -q dir_nlink.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems.

Dependencies and integration points: Depends on xfstests common libraries, e2fsprogs debug/fsck utilities. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: depends on xfstests harness requirements and exact golden-output filtering.

Test signals: no unexpected stdout beyond the golden quiet marker; visible subtest labels include Silence is golden.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/045 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/046 -->
# sources/test-tools/xfstests/tests/ext4/046

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ext4/046_research.md`.

Source read: 78 lines, SHA256 prefix `58ab61897c8da679`.

Purpose: FS QA Test No. ext4/046 Test writes to falloc file with filesize > 4GB and make sure to verify the file checksum both before and after mount. This test is to check whether unwritten extents gets properly converted to written extent on a filesystem with bs < ps with dioread_nolock. Import common functions..

Important APIs/types/functions: test tags `auto prealloc quick`; common harness imports `. ./common/preamble`, `. ./common/filter`; requirements/fixed gates `_require_check_dmesg`, `_exclude_fs ext2`, `_exclude_fs ext3`, `_require_scratch`, `_require_xfs_io_command "falloc"`, `_require_scratch_size $((6 * 1024 * 1024)) #kB`; key variables `err_str="can't mount with dioread_nolock if block size != PAGE_SIZE"`, `blksz=$(_get_file_block_size $SCRATCH_MNT)`, `testfile=$SCRATCH_MNT/testfile-$seq`, `fsize=$((5 * 1024 * 1024 * 1024))`, `off=$((3 * 1024 * 1024 * 1024))`, `off=$(($off + (2*$blksz)))`, `off=$((4 * 1024 * 1024 * 1024))`, `off=$(($off + (2*$blksz)))`, `md5_pre=`md5sum $testfile | cut -d' ' -f1``, `md5_post=`md5sum $testfile | cut -d' ' -f1``.

Control flow: The script is mostly straight-line after harness setup. Representative operation sequence: L18: _require_check_dmesg; L22: _require_xfs_io_command "falloc"; L23: _require_scratch_size $((6 * 1024 * 1024)) #kB; L25: _scratch_mkfs >> $seqres.full 2>&1; L26: if ! _try_scratch_mount "-o dioread_nolock" >> $seqres.full 2>&1; then; L28: _check_dmesg_for ${err_str}; L43: $XFS_IO_PROG -f -c "falloc 0 $fsize" $testfile >> $seqres.full 2>&1; L48: $XFS_IO_PROG -f \; L58: $XFS_IO_PROG -f \; L65: md5_pre=`md5sum $testfile | cut -d' ' -f1`; L68: _scratch_cycle_mount; L71: md5_post=`md5sum $testfile | cut -d' ' -f1`; L73: test $md5_pre != $md5_post && echo "md5sum mismatch".

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems.

Dependencies and integration points: Depends on xfstests common libraries, xfs_io workload commands. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: depends on xfstests harness requirements and exact golden-output filtering.

Test signals: no unexpected stdout beyond the golden quiet marker; matching file digests before and after remount/send/receive; absence or presence of expected dmesg warnings; visible subtest labels include Silence is golden.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/046 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/047 -->
# sources/test-tools/xfstests/tests/ext4/047

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ext4/047_research.md`.

Source read: 41 lines, SHA256 prefix `77b44652b02b384b`.

Purpose: FS QA Test 047 This is a regression test for kernel patch: commit aa2f77920b74 ("ext4: disallow modifying DAX inode flag if inline_data has been set") Import common functions..

Important APIs/types/functions: test tags `auto quick dax`; common harness imports `. ./common/preamble`, `. ./common/filter`; requirements/fixed gates `_exclude_fs ext2`, `_exclude_fs ext3`, `_require_scratch_dax_mountopt "dax=always"`, `_require_dax_iflag`, `_require_scratch_ext4_feature "inline_data"`; key variables `TESTFILE=$SCRATCH_MNT/testfile`.

Control flow: The script is mostly straight-line after harness setup. Representative operation sequence: L19: _require_scratch_dax_mountopt "dax=always"; L21: _require_scratch_ext4_feature "inline_data"; L25: _scratch_mkfs_ext4 -O inline_data > $seqres.full 2>&1; L27: _scratch_mount "-o dax=inode" >> $seqres.full 2>&1; L33: if $XFS_IO_PROG -c "chattr +x" $TESTFILE >> $seqres.full 2>&1; then; L34: _scratch_cycle_mount "dax=inode".

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems.

Dependencies and integration points: Depends on xfstests common libraries, xfs_io workload commands. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: depends on xfstests harness requirements and exact golden-output filtering.

Test signals: no unexpected stdout beyond the golden quiet marker; visible subtest labels include Silence is golden.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/047 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/048 -->
# sources/test-tools/xfstests/tests/ext4/048

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ext4/048_research.md`.

Source read: 208 lines, SHA256 prefix `42c20d9891305069`.

Purpose: FS QA Test No. 048 Test wiping of ext4_dir_entry2 data upon file removal, conversion to htree, and splitting of htree nodes Import common functions..

Important APIs/types/functions: test tags `auto quick dir`; common harness imports `. ./common/preamble`, `. ./common/filter`; requirements/fixed gates `_exclude_fs ext2`, `_exclude_fs ext3`, `_require_scratch`, `_require_command "$DEBUGFS_PROG" debugfs`, `_require_od_endian_flag`; helper functions `get_block()`, `get_offset()`, `get_reclen()`, `read_dir_ent()`, `induce_node_split()`; key variables `big_endian=$(echo -ne '\x11' | od -tx2 | head -1 | cut -f2 -d' ' | cut -c1)`, `testdir="${SCRATCH_MNT}/testdir"`, `dir_size="$(stat --printf="%s" $testdir)"`, `file_num=$(($file_num + 1))`, `test_file1="test0001"`, `test_file2="test0002"`, `test_file3="test0003"`, `blocksize="$(_get_block_size $SCRATCH_MNT)"`, `file_num=1`, `block1=$(get_block $test_file1)`.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `get_block()`, `get_offset()`, `get_reclen()`, `read_dir_ent()`, `induce_node_split()`. Representative operation sequence: L20: _require_command "$DEBUGFS_PROG" debugfs; L67: _scratch_mount >> $seqres.full 2>&1; L78: _scratch_unmount >> $seqres.full 2>&1; L89: _scratch_mkfs_sized $((1 * 1024 * 1024 * 1024)) >> $seqres.full 2>&1; L93: _scratch_mount >> $seqres.full 2>&1; L97: if test -x $here/src/checkpoint_journal && \; L98: ! $here/src/checkpoint_journal $SCRATCH_MNT --dry-run ; then; L108: _scratch_unmount >> $seqres.full 2>&1; L119: _scratch_mount >> $seqres.full 2>&1; L121: _scratch_unmount >> $seqres.full 2>&1; L135: _scratch_mount >> $seqres.full 2>&1; L137: _scratch_unmount >> $seqres.full 2>&1; L154: check_htree=$($DEBUGFS_PROG $SCRATCH_DEV -R "htree_dump /testdir" 2>&1); L163: check_htree=$($DEBUGFS_PROG $SCRATCH_DEV -R "htree_dump /testdir" 2>&1); L182: hdump=$($DEBUGFS_PROG $SCRATCH_DEV -R "htree_dump /testdir" 2>> $seqres.full).

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; edits or inspects ext metadata directly.

Dependencies and integration points: Depends on xfstests common libraries, e2fsprogs debug/fsck utilities. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: depends on xfstests harness requirements and exact golden-output filtering.

Test signals: visible subtest labels include Test 1 part 1 passed.; Test 3 passed..
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/048 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/049 -->
# sources/test-tools/xfstests/tests/ext4/049

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ext4/049_research.md`.

Source read: 51 lines, SHA256 prefix `1b655cd30fb270d5`.

Purpose: FS QA Test 049 Regression test for kernel commit a149d2a5cabb (ext4: fix check to prevent false positive report of incorrect used inodes) Import common functions..

Important APIs/types/functions: test tags `auto quick`; common harness imports `. ./common/preamble`, `. ./common/filter`; requirements/fixed gates `_exclude_fs ext2`, `_exclude_fs ext3`, `_require_scratch`; key variables `sdev=$(_short_dev ${SCRATCH_DEV})`, `sleep_time=5`.

Control flow: The script is mostly straight-line after harness setup. Representative operation sequence: L25: _scratch_mkfs_ext4 -b 4096 -g 8192 -N 1024 -I 4096 >> $seqres.full 2>&1; L28: _scratch_mount -o errors=remount-ro; L46: _check_dmesg_for "\(${sdev}\): Remounting filesystem read-only" && \.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems.

Dependencies and integration points: Depends on xfstests common libraries. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: contains timing-sensitive waits.

Test signals: absence or presence of expected dmesg warnings; visible subtest labels include + create scratch fs; + mount fs; + check mountpoint status; + check mountpoint writability; + check dmesg; scratch dev should not be remounted to read-only.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/049 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/050 -->
# sources/test-tools/xfstests/tests/ext4/050

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ext4/050_research.md`.

Source read: 59 lines, SHA256 prefix `6d3e2ad7d8a30b00`.

Purpose: FS QA Test No. 050 Test checkpoint and zeroout of journal via ioctl EXT4_IOC_CHECKPOINT Import common functions..

Important APIs/types/functions: test tags `auto ioctl quick`; common harness imports `. ./common/preamble`, `. ./common/filter`; requirements/fixed gates `_exclude_fs ext2`, `_exclude_fs ext3`, `_require_scratch`, `_require_command "$DEBUGFS_PROG" debugfs`, `_require_test_program "checkpoint_journal"`, `_require_metadata_journaling $SCRATCH_DEV`; key variables `checkpoint_journal=$here/src/checkpoint_journal`, `testdir="${SCRATCH_MNT}/testdir"`, `blocksize=$(_get_block_size $SCRATCH_MNT)`, `check=$($DEBUGFS_PROG $SCRATCH_DEV -R "cat <8>" 2> /dev/null | \`.

Control flow: The script is mostly straight-line after harness setup. Representative operation sequence: L20: _require_command "$DEBUGFS_PROG" debugfs; L22: checkpoint_journal=$here/src/checkpoint_journal; L23: _require_test_program "checkpoint_journal"; L27: _scratch_mkfs_sized $((64 * 1024 * 1024)) >> $seqres.full 2>&1; L29: _scratch_mount >> $seqres.full 2>&1; L34: $checkpoint_journal $SCRATCH_MNT --dry-run || _notrun "journal checkpoint ioctl not present on device"; L45: $checkpoint_journal $SCRATCH_MNT --erase=zeroout || _fail "ioctl returned error"; L48: $DEBUGFS_PROG $SCRATCH_DEV -R "cat <8>" 2> /dev/null | od >> $seqres.full; L49: check=$($DEBUGFS_PROG $SCRATCH_DEV -R "cat <8>" 2> /dev/null | \; L54: _scratch_unmount >> $seqres.full 2>&1.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; edits or inspects ext metadata directly.

Dependencies and integration points: Depends on xfstests common libraries, e2fsprogs debug/fsck utilities. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: depends on xfstests harness requirements and exact golden-output filtering.

Test signals: no unexpected stdout beyond the golden quiet marker; visible subtest labels include Silence is golden.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/050 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/051 -->
# sources/test-tools/xfstests/tests/ext4/051

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ext4/051_research.md`.

Source read: 31 lines, SHA256 prefix `967c4afa1240b3ba`.

Purpose: FS QA Test No. 051 Test that tune2fs doesn't fail after ext4 shutdown Regression test for kernel commit: 4274f516d4bc ext4: recalucate superblock checksum after updating free blocks/inodes b2bbb92f7042 ext4: fix e2fsprogs checksum failure for mounted filesystem.

Important APIs/types/functions: test tags `auto rw quick`; common harness imports `. ./common/preamble`; requirements/fixed gates `_exclude_fs ext2`, `_exclude_fs ext3`, `_require_scratch`, `_require_scratch_shutdown`, `_require_metadata_journaling`, `_require_command "$TUNE2FS_PROG" tune2fs`.

Control flow: The script is mostly straight-line after harness setup. Representative operation sequence: L18: _require_scratch_shutdown; L20: _require_command "$TUNE2FS_PROG" tune2fs; L24: _scratch_mkfs >/dev/null 2>&1; L25: _scratch_mount; L27: _scratch_shutdown; L28: _scratch_cycle_mount; L29: $TUNE2FS_PROG -l $SCRATCH_DEV >> $seqres.full.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems.

Dependencies and integration points: Depends on xfstests common libraries, ext-family mkfs/tune utilities. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: depends on xfstests harness requirements and exact golden-output filtering.

Test signals: no unexpected stdout beyond the golden quiet marker; visible subtest labels include Silence is golden.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/051 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/052 -->
# sources/test-tools/xfstests/tests/ext4/052

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ext4/052_research.md`.

Source read: 71 lines, SHA256 prefix `1576b286468276f4`.

Purpose: FS QA Test 052 Test ext4's large_dir feature Create a directory with enough entries that we can exercise the large_dir code paths, and then verify that the resulting file system is valid using e2fsck. Override the default cleanup function..

Important APIs/types/functions: test tags `auto quick dir`; common harness imports `. ./common/preamble`; requirements/fixed gates `_exclude_fs ext2`, `_exclude_fs ext3`, `_require_test`, `_require_loop`, `_require_test_program "dirstress"`, `_require_scratch_ext4_feature "large_dir"`; helper functions `_cleanup()`; key variables `loop_mnt=$TEST_DIR/$seq.mnt`, `fs_img=$TEST_DIR/$seq.img`.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `_cleanup()`. Representative operation sequence: L36: _require_test_program "dirstress"; L37: _require_scratch_ext4_feature "large_dir"; L45: $XFS_IO_PROG -f -c "truncate 20G" $fs_img >>$seqres.full 2>&1; L56: _mount -o loop $fs_img $loop_mnt > /dev/null 2>&1 || \; L59: if ! $here/src/dirstress -c -d $loop_mnt -p 1 -f 400000 -C >$tmp.out 2>&1; L70: $E2FSCK_PROG -fn $fs_img >> $seqres.full 2>&1 || _fail "file system corrupted".

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; uses fsck as the final persistence/integrity oracle; creates loop devices or image-backed devices.

Dependencies and integration points: Depends on xfstests common libraries, xfs_io workload commands, e2fsprogs debug/fsck utilities. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: loop-device cleanup must run to avoid leaked devices.

Test signals: no unexpected stdout beyond the golden quiet marker; clean e2fsck verification; visible subtest labels include Silence is golden; dirstress failed.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/052 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/053 -->
# sources/test-tools/xfstests/tests/ext4/053

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ext4/053_research.md`.

Source read: 691 lines, SHA256 prefix `7942cca85862c6cc`.

Purpose: FS QA Test 053 Sanity check of ext4 mount options.

Important APIs/types/functions: test tags `auto mount`; common harness imports `. ./common/preamble`, `. ./common/filter`, `. ./common/quota`; requirements/fixed gates `_require_scratch_size $SIZE`, `_require_quota`, `_require_loop`, `_require_command "$TUNE2FS_PROG" tune2fs`, `_require_command "$MKE2FS_PROG" mke2fs`; helper functions `_cleanup()`, `print_log()`, `kernel_gte()`, `test_mnt()`, `fail()`, `ok()`, `simple_mount()`, `do_mnt()`, `not_mnt()`, `mnt_only()`, `mnt()`, `remount()`, `not_remount()`, `mnt_then_not_remount()`, `do_mkfs()`, `not_ext2()`, `only_ext4()`; key variables `SIZE=$((1024 * 1024)) # 1GB in KB`, `LOGSIZE=$((10 *1024)) # 10MB in KB`, `MKE2FS_PROG=$(type -P mke2fs)`, `LOG=""`, `LOG="$LOG $@"`, `KERNEL_VERSION=`uname -r | cut -d'.' -f1,2``, `KERNEL_MAJ=${KERNEL_VERSION%.*}`, `KERNEL_MIN=${KERNEL_VERSION#*.}`, `major=${1%.*}`, `minor=${1#*.}`.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `_cleanup()`, `print_log()`, `kernel_gte()`, `test_mnt()`, `fail()`, `ok()`, `simple_mount()`, `do_mnt()`, `not_mnt()`, `mnt_only()`, `mnt()`, `remount()`, `not_remount()`, `mnt_then_not_remount()`, `do_mkfs()`, `not_ext2()`, `only_ext4()`. Representative operation sequence: L32: _require_scratch_size $SIZE; L35: _require_command "$TUNE2FS_PROG" tune2fs; L133: simple_mount() {; L134: _mount $* >> $seqres.full 2>&1; L150: simple_mount $device $SCRATCH_MNT; L153: simple_mount -o $1 $device $SCRATCH_MNT; L189: simple_mount -o remount,$1 $SCRATCH_MNT; L202: simple_mount -o remount $SCRATCH_MNT; L225: if simple_mount -o $1 $SCRATCH_DEV $SCRATCH_MNT; then; L233: if ! simple_mount $SCRATCH_DEV $SCRATCH_MNT; then; L278: $TUNE2FS_PROG -o $op_set $SCRATCH_DEV > /dev/null 2>&1; L286: $TUNE2FS_PROG -o $op_set $SCRATCH_DEV > /dev/null 2>&1; L328: if simple_mount -o remount,$1 $SCRATCH_DEV $SCRATCH_MNT; then; L337: if simple_mount -o remount,$1 $SCRATCH_MNT; then; L541: simple_mount -o dax=always $SCRATCH_DEV $SCRATCH_MNT > /dev/null 2>&1.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; creates loop devices or image-backed devices.

Dependencies and integration points: Depends on xfstests common libraries, ext-family mkfs/tune utilities, quota userspace tools. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: loop-device cleanup must run to avoid leaked devices.

Test signals: no unexpected stdout beyond the golden quiet marker; mount/statfs option visibility; visible subtest labels include Silence is golden..
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/053 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/054 -->
# sources/test-tools/xfstests/tests/ext4/054

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ext4/054_research.md`.

Source read: 85 lines, SHA256 prefix `98c983a19ec7c248`.

Purpose: FS QA Test 054 Regression test for kernel commit: 1. 0f2f87d51aebc (ext4: prevent partial update of the extent blocks) 2. 9c6e071913792 (ext4: check for inconsistent extents between index \ and leaf block) 3. 8dd27fecede55 (ext4: check for out-of-order index extents in \ ext4_valid_extent_entries()) Import common functions.

Important APIs/types/functions: test tags `auto quick dangerous_fuzzers prealloc punch`; common harness imports `. ./common/preamble`, `. ./common/filter`; requirements/fixed gates `_exclude_fs ext2`, `_exclude_fs ext3`, `_require_scratch_nocheck`, `_require_xfs_io_command "falloc"`, `_require_xfs_io_command "pwrite"`, `_require_xfs_io_command "fsync"`, `_require_xfs_io_command "fpunch"`, `_require_command "$DEBUGFS_PROG" debugfs`; key variables `TEST_FILE="${SCRATCH_MNT}/testfile"`, `offset=$((1024 * 128 * i))`, `offset=$((offset + 1024 * 64))`.

Control flow: The script is mostly straight-line after harness setup. Representative operation sequence: L23: _require_scratch_nocheck; L24: _require_xfs_io_command "falloc"; L27: _require_xfs_io_command "fpunch"; L28: _require_command "$DEBUGFS_PROG" debugfs; L32: _scratch_mkfs_blocksized 1024 >> $seqres.full 2>&1; L33: _scratch_mount; L49: $XFS_IO_PROG -c "falloc $offset $((1024 * 64))" $TEST_FILE >> $seqres.full; L51: $XFS_IO_PROG -c "pwrite $offset $((1024 * 64))" $TEST_FILE >> $seqres.full; L52: $XFS_IO_PROG -c "fsync" $TEST_FILE >> $seqres.full; L55: $XFS_IO_PROG -c "fpunch $((1024 * 5376)) $((1024 * 256))" $TEST_FILE \; L57: $XFS_IO_PROG -c "fsync" $TEST_FILE >> $seqres.full; L58: $XFS_IO_PROG -c "falloc $((1024 * 5376)) $((1024 * 64))" $TEST_FILE \; L60: $XFS_IO_PROG -c "fsync" $TEST_FILE >> $seqres.full; L62: _scratch_unmount >> $seqres.full 2>&1; L64: $DEBUGFS_PROG -w -R "set_inode_field testfile block[6] 0x1600" $SCRATCH_DEV \; L75: _scratch_mount "-o nodelalloc"; L76: $XFS_IO_PROG -c "pwrite $((1024 * 5568)) $((1024 * 64))" $TEST_FILE \.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; edits or inspects ext metadata directly.

Dependencies and integration points: Depends on xfstests common libraries, xfs_io workload commands, e2fsprogs debug/fsck utilities. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: deliberately corrupts metadata and can trigger kernel failure paths; bypasses normal scratch checking because corruption is intentional.

Test signals: no unexpected stdout beyond the golden quiet marker; visible subtest labels include Silence is golden.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/054 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/055 -->
# sources/test-tools/xfstests/tests/ext4/055

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ext4/055_research.md`.

Source read: 58 lines, SHA256 prefix `17858b6a6929750d`.

Purpose: FS QA Test 055 The preceding illegal memory access problem occurs due to tampering with the quota index information in the image. Regression test for kernel commit 9bf3d2033129 quota: check block number when reading the block in quota file commit d0e36a62bd4c quota: correct error number in free_dqentry() The test is based on a testcase from Zhang Yi <yi.zhang@huawei.com>..

Important APIs/types/functions: test tags `auto quota`; common harness imports `. ./common/preamble`, `. ./common/quota`; requirements/fixed gates `_exclude_fs ext2`, `_exclude_fs ext3`, `_require_scratch_nocheck`, `_require_user fsgqa`, `_require_user fsgqa2`, `_require_command "$DEBUGFS_PROG" debugfs`, `_require_quota`, `_exclude_scratch_mount_option dax`.

Control flow: The script is mostly straight-line after harness setup. Representative operation sequence: L23: _require_scratch_nocheck; L26: _require_command "$DEBUGFS_PROG" debugfs; L32: _exclude_scratch_mount_option dax; L33: _scratch_mkfs "-F -O quota -b 1024" > $seqres.full 2>&1; L37: $DEBUGFS_PROG -w -R "zap_block -o 0 -l 1 -p 6 -f <3> 1" $SCRATCH_DEV >> $seqres.full 2>&1; L38: _scratch_mount >> $seqres.full 2>&1.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; changes quota/qgroup accounting state; edits or inspects ext metadata directly.

Dependencies and integration points: Depends on xfstests common libraries, e2fsprogs debug/fsck utilities, quota userspace tools. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: bypasses normal scratch checking because corruption is intentional; quota accounting regressions can be silent until unmount or rescan.

Test signals: no unexpected stdout beyond the golden quiet marker; visible subtest labels include Silence is golden.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/055 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/056 -->
# sources/test-tools/xfstests/tests/ext4/056

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ext4/056_research.md`.

Source read: 101 lines, SHA256 prefix `fe4a7b44e03a994b`.

Purpose: We don't currently support resize of EXT4 filesystems mounted with sparse_super2 option enabled. Earlier, kernel used to leave the resize incomplete and the fs would be left into an incomplete state, however commit b1489186cc83[1] fixed this to avoid the fs corruption by clearly returning -ENOTSUPP. This test ensures that kernel handles resizing with sparse_super2 correctly Related commit in mainline: [1] commit b1489186cc8391e0c1e342f9fbc3eedf6b944c61 ext4: add check to prevent attempting to resize an fs with sparse_super2.

Important APIs/types/functions: test tags `auto ioctl resize quick`; common harness imports `. ./common/preamble`; requirements/fixed gates `_exclude_fs ext2`, `_exclude_fs ext3`, `_require_scratch_size $(($RESIZED_FS_SIZE/1024))`, `_require_test_program "ext4_resize"`; helper functions `log()`, `do_resize()`, `run_test()`; key variables `INITIAL_FS_SIZE=1G`, `RESIZED_FS_SIZE=$((2*1024*1024*1024)) # 2G`, `ONLINE_RESIZE_BLOCK_LIMIT=$((256*1024*1024))`, `STOP_ITER=255 # Arbitrary return code`, `RESIZE_RET=$?`, `RET=$?`.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `log()`, `do_resize()`, `run_test()`. Representative operation sequence: L32: _require_scratch_size $(($RESIZED_FS_SIZE/1024)); L46: _scratch_mount || _fail "Failed to mount scratch partition. Exiting"; L74: _scratch_unmount >> $seqres.full 2>&1 \; L94: _check_scratch_fs.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; resizes filesystem images or online filesystems.

Dependencies and integration points: Depends on xfstests common libraries. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: contains timing-sensitive waits.

Test signals: no unexpected stdout beyond the golden quiet marker; visible subtest labels include Silence is golden.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/056 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/057 -->
# sources/test-tools/xfstests/tests/ext4/057

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ext4/057_research.md`.

Source read: 57 lines, SHA256 prefix `f612e1cc234825b3`.

Purpose: Test the set/get UUID ioctl. Import common functions..

Important APIs/types/functions: test tags `auto ioctl`; common harness imports `. ./common/preamble`, `. ./common/filter`; requirements/fixed gates `_exclude_fs ext2`, `_exclude_fs ext3`, `_require_scratch`, `_require_test_program uuid_ioctl`, `_require_command $UUIDGEN_PROG uuidgen`; key variables `UUID_IOCTL=$here/src/uuid_ioctl`, `current_uuid=$($UUID_IOCTL get $SCRATCH_MNT 2>&1)`, `fsstress_args=$(_scale_fsstress_args -d $SCRATCH_MNT -p 15 -n 999999)`, `new_uuid=$($UUIDGEN_PROG)`, `current_uuid=$($UUID_IOCTL get $SCRATCH_MNT)`.

Control flow: The script is mostly straight-line after harness setup. Representative operation sequence: L32: _scratch_mkfs_ext4 -O metadata_csum_seed >> $seqres.full 2>&1; L33: _scratch_mount; L36: fsstress_args=$(_scale_fsstress_args -d $SCRATCH_MNT -p 15 -n 999999); L37: _run_fsstress_bg $fsstress_args; L52: _kill_fsstress.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems.

Dependencies and integration points: Depends on xfstests common libraries. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: depends on xfstests harness requirements and exact golden-output filtering.

Test signals: no unexpected stdout beyond the golden quiet marker; visible subtest labels include Silence is golden.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/057 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/058 -->
# sources/test-tools/xfstests/tests/ext4/058

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ext4/058_research.md`.

Source read: 33 lines, SHA256 prefix `94aa14b7eaf22662`.

Purpose: FS QA Test 058 Set 256 blocks in a block group, then inject I/O pressure, it will trigger off kernel BUG in ext4_mb_mark_diskspace_used Regression test for commit a08f789d2ab5 ext4: fix bug_on ext4_mb_use_inode_pa.

Important APIs/types/functions: test tags `auto quick`; common harness imports `. ./common/preamble`; requirements/fixed gates `_exclude_fs ext2`, `_exclude_fs ext3`, `_fixed_by_kernel_commit a08f789d2ab5 \`, `_require_scratch`.

Control flow: The script is mostly straight-line after harness setup. Representative operation sequence: L24: _scratch_mkfs -g 256 >> $seqres.full 2>&1 || _fail "mkfs failed"; L25: _scratch_mount; L27: _run_fsstress -d $SCRATCH_MNT/stress -n 1000.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems.

Dependencies and integration points: Depends on xfstests common libraries. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: is tied to specific kernel-regression behavior noted by fixed-by annotations.

Test signals: no unexpected stdout beyond the golden quiet marker; visible subtest labels include Silence is golden.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/058 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/059 -->
# sources/test-tools/xfstests/tests/ext4/059

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ext4/059_research.md`.

Source read: 47 lines, SHA256 prefix `5c74bc2a23bc9193`.

Purpose: FS QA Test No. 059 A regression test for b55c3cd102a6 ("ext4: add reserved GDT blocks check"). Make sure there's not kernel crash, if resize an ext4 which resize_inode feature is disabled but has reserved GDT blocks..

Important APIs/types/functions: test tags `auto resize quick`; common harness imports `. ./common/preamble`; requirements/fixed gates `_exclude_fs ext2`, `_exclude_fs ext3`, `_fixed_by_kernel_commit b55c3cd102a6 \`, `_require_command "$RESIZE2FS_PROG" resize2fs`, `_require_command "$DEBUGFS_PROG" debugfs`, `_require_scratch_size_nocheck $((1024 * 1024))`; key variables `dev_size=$((512 * 1024 * 1024))`, `MKFS_OPTIONS="-O ^resize_inode $MKFS_OPTIONS" _scratch_mkfs_sized $dev_size \`, `MOUNT_OPTIONS="$MOUNT_OPTIONS -o noblock_validity"`.

Control flow: The script is mostly straight-line after harness setup. Representative operation sequence: L20: _require_command "$RESIZE2FS_PROG" resize2fs; L21: _require_command "$DEBUGFS_PROG" debugfs; L22: _require_scratch_size_nocheck $((1024 * 1024)); L26: MKFS_OPTIONS="-O ^resize_inode $MKFS_OPTIONS" _scratch_mkfs_sized $dev_size \; L30: $DEBUGFS_PROG -w -R "set_super_value s_reserved_gdt_blocks 100" $SCRATCH_DEV \; L32: $DEBUGFS_PROG -R "show_super_stats -h" $SCRATCH_DEV 2>/dev/null | \; L40: _scratch_mount; L43: $RESIZE2FS_PROG $SCRATCH_DEV 1G >> $seqres.full 2>&1.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; edits or inspects ext metadata directly; resizes filesystem images or online filesystems.

Dependencies and integration points: Depends on xfstests common libraries, e2fsprogs debug/fsck utilities. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: is tied to specific kernel-regression behavior noted by fixed-by annotations.

Test signals: successful script exit with xfstests filtered output.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/059 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/060 -->
# sources/test-tools/xfstests/tests/ext4/060

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ext4/060_research.md`.

Source read: 51 lines, SHA256 prefix `0a8ce18c4c8ca457`.

Purpose: FS QA Test 060 This test ensures that kernel avoids FS corruption while online resizing an ext4 filesystem with disabled resize_inode feature. The commit a6b3bfe176e8 ("ext4: fix corruption during on-line resize") stops the corruption..

Important APIs/types/functions: test tags `auto resize quick`; common harness imports `. ./common/preamble`; requirements/fixed gates `_exclude_fs ext2`, `_exclude_fs ext3`, `_fixed_by_kernel_commit a6b3bfe176e8 \`, `_require_command "$RESIZE2FS_PROG" resize2fs`, `_require_command "$E2FSCK_PROG" e2fsck`, `_require_scratch_size_nocheck $((9* 1024 * 1024))`; key variables `dev_size=$((8* 1024 * 1024 * 1024 - 128 * 1024 * 1024))`, `MKFS_OPTIONS="-O ^resize_inode" _scratch_mkfs_sized $dev_size \`.

Control flow: The script is mostly straight-line after harness setup. Representative operation sequence: L20: if __scratch_uses_fsdax && [[ $(_get_page_size) -ne 4096 ]]; then; L27: _require_command "$RESIZE2FS_PROG" resize2fs; L28: _require_command "$E2FSCK_PROG" e2fsck; L29: _require_scratch_size_nocheck $((9* 1024 * 1024)); L36: MKFS_OPTIONS="-O ^resize_inode" _scratch_mkfs_sized $dev_size \; L39: _scratch_mount; L42: $RESIZE2FS_PROG $SCRATCH_DEV 9G >> $seqres.full 2>&1; L44: _scratch_unmount; L46: $E2FSCK_PROG -fn $SCRATCH_DEV >> $seqres.full 2>&1 || _fail "Filesystem corrupted".

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; uses fsck as the final persistence/integrity oracle; resizes filesystem images or online filesystems.

Dependencies and integration points: Depends on xfstests common libraries, e2fsprogs debug/fsck utilities. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: is tied to specific kernel-regression behavior noted by fixed-by annotations.

Test signals: no unexpected stdout beyond the golden quiet marker; clean e2fsck verification; visible subtest labels include Silence is golden.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/060 -->
