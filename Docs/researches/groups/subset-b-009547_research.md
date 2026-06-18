# subset-b-009547 Research

Grouped research for xfstests generic/367 through generic/486. Each section preserves the original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/367 -->
# sources/test-tools/xfstests/tests/generic/367

## Purpose
This test verifies that extent allocation hint setting works correctly on files with no extents allocated and non-empty files which are truncated. It also checks that the extent hints setting fails with non-empty file i.e, with any file with allocated extents or delayed allocation. We also check if the extsize value and the xflag bit actually got reflected after setting/re-setting the extsize value. It is registered as generic/367 with `_begin_fstest` tags `ioctl, quick`, making it part of the filesystem regression behavior coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: get_default_extsize, filter_extsz, setup, read_file_extsize, check_extsz_and_xflag, check_extsz_xflag_across_remount, reset_extsz_and_recheck_extsz_xflag, check_extsz_xflag_before_and_after_reset, test_empty_file, test_data_delayed, test_data_allocated, test_truncate_allocated, test_truncate_delayed. Important state variables and paths include FILE_DATA_SIZE=1M, NEW_FILE_NAME_PREFIX=$SCRATCH_MNT/new-file-. Topic focus: general filesystem semantics. Key helper behavior includes: formats a fresh scratch filesystem; mounts the scratch filesystem; forces unmount/remount persistence checks.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; creates deterministic file layout, data, or extent state; remounts or replays after simulated failure; wraps repeated scenarios in local helper functions get_default_extsize, filter_extsz, setup, read_file_extsize, check_extsz_and_xflag, check_extsz_xflag_across_remount.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; explicitly validates behavior across remount, crash replay, or log replay; depends on extent layout and size metadata remaining consistent.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble.

Prerequisite gates: _require_scratch_extsize.

Documented regression fixes: _fixed_by_fs_commit xfs 2a492ff66673 "xfs: Check for delayed allocations before setting extsize".

External/helper commands: $XFS_IO_PROG, mount, sed, truncate.

Representative `xfs_io` operations: extsize; extsize 0; open -f $filename; extsize $EXTSIZE; pwrite -q  0 $FILE_DATA_SIZE; pwrite -qW  0 $FILE_DATA_SIZE; truncate 0.

## Risks and Edge Cases
failures may reflect missing helper binaries or unsupported filesystem features rather than the target regression.

## Test Signals
The golden `.out` expects normalized signals such as: TEST: Set extsize on empty file; [EXTSIZE] SCRATCH_MNT/new-file-00; e flag set; Re-setting extsize hint to 0; [EXTSIZE] SCRATCH_MNT/new-file-00; e flag unset. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/367 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/368 -->
# sources/test-tools/xfstests/tests/generic/368

## Purpose
Verify the ciphertext for encryption policies that use a hardware-wrapped inline encryption key, the IV_INO_LBLK_64 flag, and AES-256-XTS. It is registered as generic/368 with `_begin_fstest` tags `auto, quick, encrypt`, making it part of the encryption coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: none. Important state variables and paths include no persistent shell variables beyond harness state. Topic focus: encryption. Key helper behavior includes: requires inline encryption support; verifies fscrypt ciphertext for a policy.

## Control Flow
runs a direct harness scenario and compares stdout to the golden output.

## State and Persistence Behavior
relies on the xfstests harness cleanup path and golden-output comparison.

## Dependencies and Integration Points
Common libraries: common/encrypt, common/filter, common/preamble.

Prerequisite gates: _require_scratch_inlinecrypt.

## Risks and Edge Cases
requires compatible fscrypt, inline encryption, and hardware-wrapped key support.

## Test Signals
The golden `.out` expects normalized signals such as: Verifying ciphertext with parameters:; 	contents_encryption_mode: AES-256-XTS; 	filenames_encryption_mode: AES-256-CTS-CBC; 	options: v2 iv_ino_lblk_64 hw_wrapped_key. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/368 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/369 -->
# sources/test-tools/xfstests/tests/generic/369

## Purpose
Verify the ciphertext for encryption policies that use a hardware-wrapped inline encryption key, the IV_INO_LBLK_32 flag, and AES-256-XTS. It is registered as generic/369 with `_begin_fstest` tags `auto, quick, encrypt`, making it part of the encryption coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: none. Important state variables and paths include no persistent shell variables beyond harness state. Topic focus: encryption. Key helper behavior includes: requires inline encryption support; verifies fscrypt ciphertext for a policy.

## Control Flow
runs a direct harness scenario and compares stdout to the golden output.

## State and Persistence Behavior
relies on the xfstests harness cleanup path and golden-output comparison.

## Dependencies and Integration Points
Common libraries: common/encrypt, common/filter, common/preamble.

Prerequisite gates: _require_scratch_inlinecrypt.

## Risks and Edge Cases
requires compatible fscrypt, inline encryption, and hardware-wrapped key support.

## Test Signals
The golden `.out` expects normalized signals such as: Verifying ciphertext with parameters:; 	contents_encryption_mode: AES-256-XTS; 	filenames_encryption_mode: AES-256-CTS-CBC; 	options: v2 iv_ino_lblk_32 hw_wrapped_key. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/369 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/370 -->
# sources/test-tools/xfstests/tests/generic/370

## Purpose
Test that we are able to create and activate a swap file on a file that used to have its extents shared multiple times. It is registered as generic/370 with `_begin_fstest` tags `auto, quick, clone, swap`, making it part of the swapfile activation, reflink/shared extents, ACL/permission semantics coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: _cleanup, run_test. Important state variables and paths include no persistent shell variables beyond harness state. Topic focus: swapfile activation, reflink/shared extents, ACL/permission semantics. Key helper behavior includes: formats a fresh scratch filesystem; mounts the scratch filesystem; unmounts the scratch filesystem; forces filesystem writeback/transaction commit; requires reflink support on scratch; creates a swapfile with valid swap layout; activates a swapfile through the helper.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; exercises clone/dedupe shared-extent operations; forces durability boundaries with sync/fsync operations; checks visible metadata, extent maps, hashes, or syscall output; wraps repeated scenarios in local helper functions _cleanup, run_test.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; uses sync-family calls as persistence barriers; persists extended-attribute namespace/value state; observes inode mode, ownership, ACL, and permission state; depends on extent layout and size metadata remaining consistent.

## Dependencies and Integration Points
Common libraries: common/preamble, common/reflink.

Prerequisite gates: _require_scratch_swapfile; _require_scratch_reflink; _require_cp_reflink.

Documented regression fixes: _fixed_by_fs_commit btrfs 03018e5d8508 "btrfs: fix swap file activation failure due to extents that used to be shared"; _fixed_by_fs_commit xfs 2d873efd174b "xfs: flush inodegc before swapon".

External/helper commands: $ATTR_PROG, $CHATTR_PROG, chmod, rm, swapoff, swapon, sync, touch.

## Risks and Edge Cases
results are sensitive to filesystem feature support and allocation alignment; depends on user/group identity setup and permission model details.

## Test Signals
The golden `.out` expects normalized signals such as: Test without sync after creating and removing clones; Creating swap file...; Cloning swap file...; Deleting original file and all clones except the last...; Activating swap file...; Test with sync after creating clones. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/370 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/371 -->
# sources/test-tools/xfstests/tests/generic/371

## Purpose
Run write(2) and fallocate(2) in parallel and the total needed data space for these operations don't exceed whole fs free data space, to see whether we will get any unexpected ENOSPC error. It is registered as generic/371 with `_begin_fstest` tags `auto, quick, enospc, prealloc`, making it part of the preallocation/range operations, ENOSPC/free-space handling coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: none. Important state variables and paths include testfile1=$SCRATCH_MNT/testfile1, testfile2=$SCRATCH_MNT/testfile2. Topic focus: preallocation/range operations, ENOSPC/free-space handling. Key helper behavior includes: formats a scratch filesystem with a controlled size; formats a fresh scratch filesystem; mounts the scratch filesystem.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; creates deterministic file layout, data, or extent state.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; depends on extent layout and size metadata remaining consistent.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble.

Prerequisite gates: _require_scratch; _require_xfs_io_command "falloc"; test "$FSTYP" = "xfs" && _require_xfs_io_command "extsize".

External/helper commands: $XFS_IO_PROG, rm.

Representative `xfs_io` operations: extsize $alloc_sz.

## Risks and Edge Cases
timing and workload races can expose intermittent kernel behavior; results are sensitive to filesystem feature support and allocation alignment.

## Test Signals
The golden `.out` expects normalized signals such as: Silence is golden. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/371 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/372 -->
# sources/test-tools/xfstests/tests/generic/372

## Purpose
Check that bmap/fiemap accurately report shared extents. It is registered as generic/372 with `_begin_fstest` tags `auto, quick, clone, fiemap, prealloc`, making it part of the reflink/shared extents, preallocation/range operations, fiemap/bmap reporting coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: _cleanup. Important state variables and paths include testdir=$SCRATCH_MNT/test-$seq, blocks=5, blksz=65536, sz=$((blocks * blksz)). Topic focus: reflink/shared extents, preallocation/range operations, fiemap/bmap reporting. Key helper behavior includes: formats a fresh scratch filesystem; mounts the scratch filesystem; forces unmount/remount persistence checks; creates shared extents through reflink range cloning; writes deterministic byte patterns; requires reflink support on scratch.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; creates deterministic file layout, data, or extent state; exercises clone/dedupe shared-extent operations; remounts or replays after simulated failure; checks visible metadata, extent maps, hashes, or syscall output; wraps repeated scenarios in local helper functions _cleanup.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; explicitly validates behavior across remount, crash replay, or log replay; depends on extent layout and size metadata remaining consistent.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble, common/reflink.

Prerequisite gates: _require_scratch_reflink; _require_xfs_io_command "falloc"; _require_xfs_io_command "fiemap"; _require_scratch_explicit_shared_extents; _require_congruent_file_oplen $SCRATCH_MNT $blksz.

External/helper commands: $XFS_IO_PROG, awk, grep, md5sum, mkdir, mount, rm.

Representative `xfs_io` operations: falloc 0 $sz; fiemap -v; 0x.*[2367aAbBfF]...$.

## Risks and Edge Cases
timing and workload races can expose intermittent kernel behavior; results are sensitive to filesystem feature support and allocation alignment.

## Test Signals
The golden `.out` expects normalized signals such as: Format and mount; Create the original files; file1 extents and holes; 1; 0; Compare files. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/372 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/373 -->
# sources/test-tools/xfstests/tests/generic/373

## Purpose
Check that cross-mountpoint reflink works. It is registered as generic/373 with `_begin_fstest` tags `auto, quick, clone`, making it part of the reflink/shared extents coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: _cleanup, filter_otherdir. Important state variables and paths include testdir=$SCRATCH_MNT/test-$seq, otherdir=$tmp.m.$seq, othertestdir=$otherdir/test-$seq, blocks=1, blksz=65536, sz=$((blksz * blocks)). Topic focus: reflink/shared extents. Key helper behavior includes: formats a fresh scratch filesystem; mounts the scratch filesystem; writes deterministic byte patterns; requires reflink support on scratch.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; creates deterministic file layout, data, or extent state; exercises clone/dedupe shared-extent operations; checks visible metadata, extent maps, hashes, or syscall output; wraps repeated scenarios in local helper functions _cleanup, filter_otherdir.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; depends on extent layout and size metadata remaining consistent.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble, common/reflink.

Prerequisite gates: _require_scratch_reflink; _require_cp_reflink.

External/helper commands: $MOUNT_PROG, md5sum, mkdir, mount, rm, sed.

## Risks and Edge Cases
timing and workload races can expose intermittent kernel behavior; results are sensitive to filesystem feature support and allocation alignment.

## Test Signals
The golden `.out` expects normalized signals such as: Format and mount; Mount otherdir; Create file; Reflink one file to another; Check output; 2d61aa54b58c2e94403fb092c3dbc027  SCRATCH_MNT/test-373/file. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/373 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/374 -->
# sources/test-tools/xfstests/tests/generic/374

## Purpose
Check that cross-mountpoint dedupe works. It is registered as generic/374 with `_begin_fstest` tags `auto, quick, clone, dedupe`, making it part of the reflink/shared extents, dedupe coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: _cleanup, filter_md5. Important state variables and paths include testdir=$SCRATCH_MNT/test-$seq, otherdir=$tmp.m.$seq, othertestdir=$otherdir/test-$seq, blocks=1, blksz=65536, sz=$((blocks * blksz)). Topic focus: reflink/shared extents, dedupe. Key helper behavior includes: formats a fresh scratch filesystem; mounts the scratch filesystem; deduplicates matching byte ranges; writes deterministic byte patterns; requires dedupe support on scratch.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; creates deterministic file layout, data, or extent state; exercises clone/dedupe shared-extent operations; checks visible metadata, extent maps, hashes, or syscall output; wraps repeated scenarios in local helper functions _cleanup, filter_md5.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; depends on extent layout and size metadata remaining consistent.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble, common/reflink.

Prerequisite gates: _require_scratch_dedupe.

External/helper commands: $MOUNT_PROG, md5sum, mkdir, mount, rm, sed.

## Risks and Edge Cases
timing and workload races can expose intermittent kernel behavior; results are sensitive to filesystem feature support and allocation alignment.

## Test Signals
The golden `.out` expects normalized signals such as: Format and mount; Mount otherdir; Create file; Dedupe one file to another; deduped 65536/65536 bytes at offset 0; XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec). Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/374 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/375 -->
# sources/test-tools/xfstests/tests/generic/375

## Purpose
Check if SGID is cleared upon chmod / setfacl when the owner is not in the owning group. It is registered as generic/375 with `_begin_fstest` tags `auto, quick, acl, perms`, making it part of the ACL/permission semantics, filename/directory semantics coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: none. Important state variables and paths include no persistent shell variables beyond harness state. Topic focus: ACL/permission semantics, filename/directory semantics. The script is mostly linear and relies on xfstests common helpers for setup, filtering, and cleanup.

## Control Flow
operates in the configured test filesystem; checks visible metadata, extent maps, hashes, or syscall output.

## State and Persistence Behavior
uses persistent files under TEST_DIR; observes inode mode, ownership, ACL, and permission state.

## Dependencies and Integration Points
Common libraries: common/attr, common/filter, common/preamble.

Prerequisite gates: _require_test; _require_runas; _require_acls.

External/helper commands: attr, chmod, chown, mkdir, rm, setfacl, stat, touch.

## Risks and Edge Cases
depends on user/group identity setup and permission model details.

## Test Signals
The golden `.out` expects normalized signals such as: *** SGID should remain set (twice); -rwxrwsrwx; -rwxrwsrwx; *** SGID should be cleared (twice); -rwxrwxrwx; -rwxrwxrwx. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/375 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/376 -->
# sources/test-tools/xfstests/tests/generic/376

## Purpose
Test that if we rename a file, without changing its parent directory, create a new file that has the old name of the file we renamed, doing an fsync against the file we renamed works correctly and after a power failure both files exists. It is registered as generic/376 with `_begin_fstest` tags `auto, quick, metadata, log`, making it part of the crash recovery/log replay, rename/link persistence, filename/directory semantics coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: _cleanup. Important state variables and paths include no persistent shell variables beyond harness state. Topic focus: crash recovery/log replay, rename/link persistence, filename/directory semantics. Key helper behavior includes: formats a fresh scratch filesystem; mounts the scratch filesystem; unmounts the scratch filesystem; forces filesystem writeback/transaction commit; requires a journal/log capable filesystem before crash replay; routes the scratch device through dm-flakey; simulates power loss and remounts for replay.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; initializes device-mapper or log-writes infrastructure; forces durability boundaries with sync/fsync operations; remounts or replays after simulated failure; wraps repeated scenarios in local helper functions _cleanup.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; explicitly validates behavior across remount, crash replay, or log replay; uses sync-family calls as persistence barriers.

## Dependencies and Integration Points
Common libraries: common/dmflakey, common/filter, common/preamble.

Prerequisite gates: _require_scratch; _require_dm_target flakey; _require_metadata_journaling $SCRATCH_DEV.

External/helper commands: $XFS_IO_PROG, ls, mkdir, mv, rm, touch.

Representative `xfs_io` operations: fsync.

## Risks and Edge Cases
device-mapper setup, replay ordering, or host capabilities can dominate failures.

## Test Signals
The golden `.out` expects normalized signals such as: Filesystem contents after log replay:; SCRATCH_MNT/dir:; bar; foo. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/376 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/377 -->
# sources/test-tools/xfstests/tests/generic/377

## Purpose
Test listxattr syscall behaviour with different buffer sizes. It is registered as generic/377 with `_begin_fstest` tags `attr, auto, quick, metadata`, making it part of the extended attributes coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: none. Important state variables and paths include listxattr=$here/src/listxattr, testfile=${SCRATCH_MNT}/testfile. Topic focus: extended attributes. Key helper behavior includes: formats a fresh scratch filesystem; mounts the scratch filesystem.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; checks visible metadata, extent maps, hashes, or syscall output.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; persists extended-attribute namespace/value state.

## Dependencies and Integration Points
Common libraries: common/attr, common/filter, common/preamble.

Prerequisite gates: _require_scratch; _require_attrs; _require_test_program "listxattr".

External/helper commands: $ATTR_PROG, $SETFATTR_PROG, attr, grep, sort, touch.

## Risks and Edge Cases
failures may reflect missing helper binaries or unsupported filesystem features rather than the target regression.

## Test Signals
The golden `.out` expects normalized signals such as: xattr: user.foo; xattr: user.hello; xattr: user.ping; listxattr: No such file or directory; listxattr: Numerical result out of range; listxattr: Numerical result out of range. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/377 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/378 -->
# sources/test-tools/xfstests/tests/generic/378

## Purpose
Simple permission check on hard links. Overlayfs had a bug that hardlinks don't share inode, if chmod/chown/etc. is performed on one of the links then the inode belonging to the other one won't be updated. The following patch fixed this issue 51f7e52 ovl: share inode for hard link. It is registered as generic/378 with `_begin_fstest` tags `auto, quick, metadata`, making it part of the ACL/permission semantics, rename/link persistence coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: none. Important state variables and paths include testfile=$TEST_DIR/testfile.$seq, testlink=$testfile.hardlink. Topic focus: ACL/permission semantics, rename/link persistence. The script is mostly linear and relies on xfstests common helpers for setup, filtering, and cleanup.

## Control Flow
operates in the configured test filesystem.

## State and Persistence Behavior
uses persistent files under TEST_DIR; observes inode mode, ownership, ACL, and permission state.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble.

Prerequisite gates: _require_test; _require_user; _require_hardlinks.

External/helper commands: chmod, ln, rm.

## Risks and Edge Cases
depends on user/group identity setup and permission model details.

## Test Signals
The golden `.out` expects normalized signals such as: Permission denied; Permission denied. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/378 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/379 -->
# sources/test-tools/xfstests/tests/generic/379

## Purpose
Check behavior of chown with both user and group quota enabled, and changing both user and group together via chown(2). It is registered as generic/379 with `_begin_fstest` tags `quota, auto, quick`, making it part of the ACL/permission semantics, quota accounting coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: _cleanup, _filter_stat, _exercise. Important state variables and paths include no persistent shell variables beyond harness state. Topic focus: ACL/permission semantics, quota accounting. Key helper behavior includes: formats a fresh scratch filesystem; unmounts the scratch filesystem.

## Control Flow
formats the scratch filesystem; wraps repeated scenarios in local helper functions _cleanup, _filter_stat, _exercise.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; observes inode mode, ownership, ACL, and permission state.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble, common/quota.

Prerequisite gates: _require_scratch; _require_quota; _require_xfs_quota_foreign.

External/helper commands: chmod, chown, cp, mount, rm, sed, touch.

## Risks and Edge Cases
depends on user/group identity setup and permission model details.

## Test Signals
The golden `.out` expects normalized signals such as: *** Default mount options;  File: "<MOUNT>/testfile";  Size: 0 Filetype: Regular File;  Mode: (0644/-rw-r--r--) Uid: (12345) Gid: (54321); Device: <DEVICE> Inode: <INODE> Links: 1;  File: "<MOUNT>/testfile". Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/379 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/380 -->
# sources/test-tools/xfstests/tests/generic/380

## Purpose
To test out pv#940675 crash in xfs_trans_brelse + quotas Without the fix, this will create an ASSERT failure in debug kernels and crash a non-debug kernel. It is registered as generic/380 with `_begin_fstest` tags `quota, auto, quick`, making it part of the ACL/permission semantics, quota accounting coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: _chowning_file. Important state variables and paths include no persistent shell variables beyond harness state. Topic focus: ACL/permission semantics, quota accounting. Key helper behavior includes: formats a fresh scratch filesystem; mounts the scratch filesystem.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; wraps repeated scenarios in local helper functions _chowning_file.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; observes inode mode, ownership, ACL, and permission state.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble, common/quota.

Prerequisite gates: _require_scratch; _require_quota; _require_xfs_quota_foreign.

External/helper commands: chown, ls, mount, sed, touch.

## Risks and Edge Cases
depends on user/group identity setup and permission model details.

## Test Signals
The golden `.out` expects normalized signals such as: mkfs on scratch; mount with quotas; creating quota file with holes; ..........; now fill in the holes; .................................................................................................................................................................................................................................................................. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/380 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/381 -->
# sources/test-tools/xfstests/tests/generic/381

## Purpose
Test xfs_quota when user or names beginning with digits. For example, create a 'limit' for a user or group named '12345678-abcd', then query this user and group. It is registered as generic/381 with `_begin_fstest` tags `auto, quick, quota`, making it part of the quota accounting coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: none. Important state variables and paths include no persistent shell variables beyond harness state. Topic focus: quota accounting. Key helper behavior includes: formats a fresh scratch filesystem.

## Control Flow
formats the scratch filesystem.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble, common/quota.

Prerequisite gates: _require_scratch; _require_quota; _require_xfs_quota_foreign; _require_user 123456-fsgqa; _require_group 123456-fsgqa.

External/helper commands: grep.

## Risks and Edge Cases
failures may reflect missing helper binaries or unsupported filesystem features rather than the target regression.

## Test Signals
The golden `.out` expects normalized signals such as: == user test ==; === quota command output ===; SCRATCH_DEV 0 102400 204800 00 [--------] SCRATCH_MNT; === report command output ===; 123456-fsgqa 0 102400 204800 00 [--------]; == group test ==. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/381 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/382 -->
# sources/test-tools/xfstests/tests/generic/382

## Purpose
When default quota is set, all different quota types inherits the same default value, include group quota. So if a user quota limit larger than the default user quota value, it will still be limited by the group default quota value. There's a patch from Upstream can fix this bug: [PATCH] xfs: Split default quota limits by quota type V4. It is registered as generic/382 with `_begin_fstest` tags `auto, quick, quota`, making it part of the quota accounting coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: do_test. Important state variables and paths include no persistent shell variables beyond harness state. Topic focus: quota accounting. Key helper behavior includes: formats a fresh scratch filesystem; unmounts the scratch filesystem; forces filesystem writeback/transaction commit.

## Control Flow
formats the scratch filesystem; creates deterministic file layout, data, or extent state; forces durability boundaries with sync/fsync operations; wraps repeated scenarios in local helper functions do_test.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; uses sync-family calls as persistence barriers.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble, common/quota.

Prerequisite gates: _require_scratch; _require_quota; _require_xfs_quota_foreign; _require_user; _require_group.

External/helper commands: $XFS_IO_PROG, grep, rm.

## Risks and Edge Cases
depends on user/group identity setup and permission model details.

## Test Signals
The golden `.out` expects normalized signals such as: === user quota test ===; user blocks and inode limit; fsgqa 0 40960 40960 00 [--------] 0 40 40 00 [--------]; wrote 31457280/31457280 bytes at offset 0; XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec); === group quota test ===. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/382 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/383 -->
# sources/test-tools/xfstests/tests/generic/383

## Purpose
Test xfs_quota when project names beginning with digits. It is registered as generic/383 with `_begin_fstest` tags `auto, quick, quota`, making it part of the quota accounting, filename/directory semantics coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: do_project_test. Important state variables and paths include qa_user=. Topic focus: quota accounting, filename/directory semantics. Key helper behavior includes: formats a fresh scratch filesystem.

## Control Flow
formats the scratch filesystem; wraps repeated scenarios in local helper functions do_project_test.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble, common/quota.

Prerequisite gates: _require_scratch; _require_quota; _require_xfs_quota_foreign; _require_prjquota $SCRATCH_DEV.

External/helper commands: mkdir.

## Risks and Edge Cases
failures may reflect missing helper binaries or unsupported filesystem features rather than the target regression.

## Test Signals
The golden `.out` expects normalized signals such as: === quota command output ===; Disk quotas for Project 123456-project (10); Filesystem Files Quota Limit Warn/Time Mounted on; SCRATCH_DEV 1 100 200 00 [--------] SCRATCH_MNT; === report command output ===; 123456-project 1 100 200 00 [--------]. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/383 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/384 -->
# sources/test-tools/xfstests/tests/generic/384

## Purpose
test to reproduce PV951636: project quotas not updated if a file is mv'd into that directory. It is registered as generic/384 with `_begin_fstest` tags `quota, auto, quick`, making it part of the ACL/permission semantics, rename/link persistence, quota accounting, filename/directory semantics coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: _cleanup, report_quota. Important state variables and paths include dir=$SCRATCH_MNT/project. Topic focus: ACL/permission semantics, rename/link persistence, quota accounting, filename/directory semantics. Key helper behavior includes: formats a fresh scratch filesystem; unmounts the scratch filesystem.

## Control Flow
formats the scratch filesystem; creates deterministic file layout, data, or extent state; wraps repeated scenarios in local helper functions _cleanup, report_quota.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; uses persistent files under TEST_DIR; observes inode mode, ownership, ACL, and permission state.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble, common/quota.

Prerequisite gates: _require_test; _require_quota; _require_xfs_quota_foreign; _require_xfs_io_command "chproj"; _require_scratch; _require_prjquota $SCRATCH_DEV.

External/helper commands: $XFS_IO_PROG, chmod, cp, mkdir, mv, rm, touch.

Representative `xfs_io` operations: chproj -R 1; chattr -R +P; limit -p bsoft=100m bhard=100m 1.

## Risks and Edge Cases
depends on user/group identity setup and permission model details.

## Test Signals
The golden `.out` expects normalized signals such as: #1 1 0 0 00 [--------]; #1 4 0 0 00 [--------]; #1 5 0 0 00 [--------]; #1 6 0 0 00 [--------]. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/384 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/385 -->
# sources/test-tools/xfstests/tests/generic/385

## Purpose
Make sure renames accross project boundaries are properly rejected and that we don't use the wrong lock flags internally. Based on a report and testcase from Arkadiusz Miskiewicz <arekm@maven.pl>. It is registered as generic/385 with `_begin_fstest` tags `quota, auto, quick`, making it part of the rename/link persistence, quota accounting coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: _cleanup. Important state variables and paths include quota_cmd=$XFS_QUOTA_PROG -D $tmp.projects -P $tmp.projid. Topic focus: rename/link persistence, quota accounting. Key helper behavior includes: formats a fresh scratch filesystem; unmounts the scratch filesystem.

## Control Flow
formats the scratch filesystem; wraps repeated scenarios in local helper functions _cleanup.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble, common/quota.

Prerequisite gates: _require_scratch; _require_quota; _require_xfs_quota_foreign; _require_prjquota $SCRATCH_DEV.

External/helper commands: mkdir, rm, touch.

## Risks and Edge Cases
failures may reflect missing helper binaries or unsupported filesystem features rather than the target regression.

## Test Signals
The golden `.out` expects normalized signals such as: rename: No such file or directory; rename: No such file or directory; rename: No such file or directory; rename: No such file or directory; rename: No such file or directory; rename: No such file or directory. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/385 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/386 -->
# sources/test-tools/xfstests/tests/generic/386

## Purpose
This test checks the project quota values reported by the quota "df" and "report" subcommands to ensure they match what they should be. There was a bug (fixed by xfsprogs commit 7cb2d41b) where the values reported were double what they should have been. SGI PV 1015651. It is registered as generic/386 with `_begin_fstest` tags `auto, quick, quota`, making it part of the quota accounting coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: _filter_quota_rpt, _quota_cmd. Important state variables and paths include my_projects=$tmp.projects, my_projid=$tmp.projid, proj_name=test_project, proj_num=1, qlimit_meg=500, proj_dir=$SCRATCH_MNT/test. Topic focus: quota accounting. Key helper behavior includes: formats a fresh scratch filesystem; unmounts the scratch filesystem.

## Control Flow
formats the scratch filesystem; wraps repeated scenarios in local helper functions _filter_quota_rpt, _quota_cmd.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble, common/quota.

Prerequisite gates: _require_quota; _require_xfs_quota_foreign; _require_scratch; _require_prjquota $SCRATCH_DEV.

External/helper commands: awk, df, mkdir, rm.

## Risks and Edge Cases
failures may reflect missing helper binaries or unsupported filesystem features rather than the target regression.

## Test Signals
The golden `.out` expects normalized signals such as: Silence is golden.. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/386 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/387 -->
# sources/test-tools/xfstests/tests/generic/387

## Purpose
Create a heavily reflinked file, then check whether we can truncate it correctly. It is registered as generic/387 with `_begin_fstest` tags `auto, clone`, making it part of the reflink/shared extents, preallocation/range operations coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: none. Important state variables and paths include testfile=$SCRATCH_MNT/testfile, dummyfile=$SCRATCH_MNT/dummyfile, blocksize=$((128 * 1024)). Topic focus: reflink/shared extents, preallocation/range operations. Key helper behavior includes: formats a scratch filesystem with a controlled size; formats a fresh scratch filesystem; mounts the scratch filesystem; forces filesystem writeback/transaction commit; creates shared extents through reflink range cloning; writes deterministic byte patterns; requires reflink support on scratch.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; creates deterministic file layout, data, or extent state; exercises clone/dedupe shared-extent operations; forces durability boundaries with sync/fsync operations.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; uses sync-family calls as persistence barriers; depends on extent layout and size metadata remaining consistent.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble, common/reflink.

Prerequisite gates: _require_scratch_reflink.

External/helper commands: $XFS_IO_PROG, dd, rm, truncate.

Representative `xfs_io` operations: truncate 0.

## Risks and Edge Cases
results are sensitive to filesystem feature support and allocation alignment.

## Test Signals
The golden `.out` expects normalized signals such as: Silence is golden. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/387 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/388 -->
# sources/test-tools/xfstests/tests/generic/388

## Purpose
Test XFS log recovery ordering on v5 superblock filesystems. XFS had a problem where it would incorrectly replay older modifications from the log over more recent versions of metadata due to failure to update metadata LSNs during log recovery. This could result in false positive reports of corruption during log recovery and permanent mount failure. To test this situation, run frequent shutdowns immediately after log recovery. Ensure that log recovery does not recover stale modifications and cause spurious corruption reports and/or mount failures. It is registered as generic/388 with `_begin_fstest` tags `shutdown, auto, log, metadata, recoveryloop`, making it part of the crash recovery/log replay, fsstress/replay consistency coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: none. Important state variables and paths include no persistent shell variables beyond harness state. Topic focus: crash recovery/log replay, fsstress/replay consistency. Key helper behavior includes: formats a fresh scratch filesystem; mounts the scratch filesystem; forces unmount/remount persistence checks; requires a journal/log capable filesystem before crash replay; starts fsstress workload generation.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; remounts or replays after simulated failure.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; explicitly validates behavior across remount, crash replay, or log replay.

## Dependencies and Integration Points
Common libraries: common/preamble.

Prerequisite gates: _require_scratch; _require_local_device $SCRATCH_DEV; _require_scratch_shutdown; _require_metadata_journaling $SCRATCH_DEV.

External/helper commands: mount.

## Risks and Edge Cases
failures may reflect missing helper binaries or unsupported filesystem features rather than the target regression.

## Test Signals
The golden `.out` expects normalized signals such as: Silence is golden.. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/388 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/389 -->
# sources/test-tools/xfstests/tests/generic/389

## Purpose
Test if O_TMPFILE files inherit POSIX Default ACLs when they are linked into the namespace. It is registered as generic/389 with `_begin_fstest` tags `auto, quick, acl`, making it part of the ACL/permission semantics coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: none. Important state variables and paths include testdir=${TEST_DIR}/d.$seq, testfile=${testdir}/tst-tmpfile-flink. Topic focus: ACL/permission semantics. The script is mostly linear and relies on xfstests common helpers for setup, filtering, and cleanup.

## Control Flow
operates in the configured test filesystem; creates deterministic file layout, data, or extent state; checks visible metadata, extent maps, hashes, or syscall output.

## State and Persistence Behavior
uses persistent files under TEST_DIR; observes inode mode, ownership, ACL, and permission state.

## Dependencies and Integration Points
Common libraries: common/attr, common/filter, common/preamble.

Prerequisite gates: _require_test; _require_xfs_io_command "-T"; _require_xfs_io_command "flink"; _require_acls.

External/helper commands: $XFS_IO_PROG, attr, mkdir, rm, setfacl, stat.

Representative `xfs_io` operations: pwrite 0 4096; pread 0 4096; flink ${testfile}; %a.

## Risks and Edge Cases
depends on user/group identity setup and permission model details.

## Test Signals
The golden `.out` expects normalized signals such as: wrote 4096/4096 bytes at offset 0; XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec); read 4096/4096 bytes at offset 0; XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec); 664. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/389 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/390 -->
# sources/test-tools/xfstests/tests/generic/390

## Purpose
Multi-threads freeze/unfreeze testing. This's a stress test case, it won't do functional check. It is registered as generic/390 with `_begin_fstest` tags `auto, freeze, stress`, making it part of the filesystem regression behavior coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: _cleanup. Important state variables and paths include num_cpus=`$here/src/feature -o`, procs=$num_cpus, nops=1000, stress_dir=$SCRATCH_MNT/fsstress_test_dir, fsstress_args=`_scale_fsstress_args -d $stress_dir -p $p..., result=$?. Topic focus: general filesystem semantics. Key helper behavior includes: formats a fresh scratch filesystem; mounts the scratch filesystem; starts fsstress workload generation.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; wraps repeated scenarios in local helper functions _cleanup.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble.

Prerequisite gates: _require_scratch; _require_freeze; _require_test_program "feature".

External/helper commands: mkdir, rm.

## Risks and Edge Cases
timing and workload races can expose intermittent kernel behavior.

## Test Signals
The golden `.out` expects normalized signals such as: Silence is golden. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/390 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/391 -->
# sources/test-tools/xfstests/tests/generic/391

## Purpose
Test two threads doing non-overlapping direct I/O in the same extents. Motivated by a bug in Btrfs' direct I/O get_block function which would lead to spurious -EEXIST failures from direct I/O reads. It is registered as generic/391 with `_begin_fstest` tags `auto, quick, rw, prealloc`, making it part of the preallocation/range operations coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: _cleanup. Important state variables and paths include extent_size=$(($(_get_block_size "$TEST_DIR") * 2)), num_extents=1024, testfile=$TEST_DIR/$$-testfile. Topic focus: preallocation/range operations. The script is mostly linear and relies on xfstests common helpers for setup, filtering, and cleanup.

## Control Flow
operates in the configured test filesystem; creates deterministic file layout, data, or extent state; wraps repeated scenarios in local helper functions _cleanup.

## State and Persistence Behavior
uses persistent files under TEST_DIR; depends on extent layout and size metadata remaining consistent.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble.

Prerequisite gates: _require_test; _require_xfs_io_command "falloc"; _require_test_program "dio-interleaved"; _require_odirect.

External/helper commands: $XFS_IO_PROG, rm, truncate.

Representative `xfs_io` operations: falloc $off $extent_size.

## Risks and Edge Cases
results are sensitive to filesystem feature support and allocation alignment.

## Test Signals
The golden `.out` expects normalized signals such as: Silence is golden. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/391 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/392 -->
# sources/test-tools/xfstests/tests/generic/392

## Purpose
Test inode's metadata after fsync or fdatasync calls. In the case of fsync, filesystem should recover all the inode metadata, while recovering for fdatasync it should at least recovery i_size. It is registered as generic/392 with `_begin_fstest` tags `shutdown, auto, quick, metadata, punch`, making it part of the crash recovery/log replay, preallocation/range operations coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: check_inode_metadata, test_i_size, test_i_time, test_punch. Important state variables and paths include testfile=$SCRATCH_MNT/testfile. Topic focus: crash recovery/log replay, preallocation/range operations. Key helper behavior includes: formats a fresh scratch filesystem; mounts the scratch filesystem; forces unmount/remount persistence checks; requires a journal/log capable filesystem before crash replay.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; creates deterministic file layout, data, or extent state; forces durability boundaries with sync/fsync operations; remounts or replays after simulated failure; checks visible metadata, extent maps, hashes, or syscall output; wraps repeated scenarios in local helper functions check_inode_metadata, test_i_size, test_i_time, test_punch.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; explicitly validates behavior across remount, crash replay, or log replay; uses sync-family calls as persistence barriers; depends on extent layout and size metadata remaining consistent.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble, common/punch.

Prerequisite gates: _require_scratch; _require_scratch_shutdown; _require_xfs_io_command "fpunch"; _require_metadata_journaling $SCRATCH_DEV.

External/helper commands: $XFS_IO_PROG, rm, stat, touch, truncate.

Representative `xfs_io` operations: $sync_mode; truncate 4M; pwrite 0 4M; fsync; pwrite 4M $2; truncate 4202496; pwrite 0 4202496; fpunch 4194304 $2.

## Risks and Edge Cases
results are sensitive to filesystem feature support and allocation alignment.

## Test Signals
The golden `.out` expects normalized signals such as: ==== i_size 1024 test with fsync ====; ==== i_size 4096 test with fsync ====; ==== i_time test with fsync ====; ==== fpunch 1024 test with fsync ====; ==== fpunch 4096 test with fsync ====; ==== i_size 1024 test with fdatasync ====. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/392 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/393 -->
# sources/test-tools/xfstests/tests/generic/393

## Purpose
Test some small truncations to check inline_data and its cached data are truncated correctly at the same time. The inline_data feature was introduced in ext4 and f2fs as follows. ext4 : http://lwn.net/Articles/468678/ f2fs : http://lwn.net/Articles/573408/ The basic idea is embedding small-sized file's data into relatively large inode space. In ext4, up to 132 bytes of data can be stored in 256 bytes-sized inode. In f2fs, up to 3.4KB of data can be embedded into 4KB-sized inode block. It is registered as generic/393 with `_begin_fstest` tags `auto, quick, rw`, making it part of the filesystem regression behavior coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: none. Important state variables and paths include testfile=$SCRATCH_MNT/testfile, OD_CMD=od -A x -t x1z. Topic focus: general filesystem semantics. Key helper behavior includes: formats a fresh scratch filesystem; mounts the scratch filesystem; forces unmount/remount persistence checks.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; creates deterministic file layout, data, or extent state; forces durability boundaries with sync/fsync operations; remounts or replays after simulated failure.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; explicitly validates behavior across remount, crash replay, or log replay; uses sync-family calls as persistence barriers; depends on extent layout and size metadata remaining consistent.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble.

Prerequisite gates: _require_scratch.

External/helper commands: $XFS_IO_PROG, rm, truncate.

Representative `xfs_io` operations: pwrite -S 0x58 0 40; fsync; truncate 0; truncate 50; truncate 4096; truncate 4.

## Risks and Edge Cases
failures may reflect missing helper binaries or unsupported filesystem features rather than the target regression.

## Test Signals
The golden `.out` expects normalized signals such as: wrote 40/40 bytes at offset 0; XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec); = truncate inline_data after #0 page was truncated entirely =; 000000 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  >................<; *; 000030 00 00                                            >..<. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/393 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/394 -->
# sources/test-tools/xfstests/tests/generic/394

## Purpose
Make sure fs honors file size resource limit. It is registered as generic/394 with `_begin_fstest` tags `auto, quick`, making it part of the filesystem regression behavior coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: _cleanup, do_truncate. Important state variables and paths include no persistent shell variables beyond harness state. Topic focus: general filesystem semantics. The script is mostly linear and relies on xfstests common helpers for setup, filtering, and cleanup.

## Control Flow
operates in the configured test filesystem; creates deterministic file layout, data, or extent state; wraps repeated scenarios in local helper functions _cleanup, do_truncate.

## State and Persistence Behavior
uses persistent files under TEST_DIR; depends on extent layout and size metadata remaining consistent.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble.

Prerequisite gates: _require_test.

External/helper commands: $XFS_IO_PROG, grep, rm, truncate.

## Risks and Edge Cases
failures may reflect missing helper binaries or unsupported filesystem features rather than the target regression.

## Test Signals
The golden `.out` expects normalized signals such as: File size limit exceeded. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/394 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/395 -->
# sources/test-tools/xfstests/tests/generic/395

## Purpose
Test setting and getting encryption policies. It is registered as generic/395 with `_begin_fstest` tags `auto, quick, encrypt`, making it part of the filesystem regression behavior coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: none. Important state variables and paths include empty_dir=$SCRATCH_MNT/empty_dir, nonempty_dir=$SCRATCH_MNT/nonempty_dir, nondirectory=$SCRATCH_MNT/nondirectory, unauthorized_dir=$SCRATCH_MNT/unauthorized_dir. Topic focus: general filesystem semantics. Key helper behavior includes: formats a fresh scratch filesystem; mounts the scratch filesystem.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem.

## Dependencies and Integration Points
Common libraries: common/encrypt, common/filter, common/preamble.

Prerequisite gates: _require_scratch_encryption; _require_xfs_io_command "get_encpolicy"; _require_user.

External/helper commands: mkdir, mount, touch.

## Risks and Edge Cases
requires compatible fscrypt, inline encryption, and hardware-wrapped key support; depends on user/group identity setup and permission model details.

## Test Signals
The golden `.out` expects normalized signals such as: *** Setting encryption policy on empty directory ***; SCRATCH_MNT/empty_dir: failed to get encryption policy: No data available; Encryption policy for SCRATCH_MNT/empty_dir:; 	Policy version: 0; 	Master key descriptor: 0000111122223333; 	Contents encryption mode: 1 (AES-256-XTS). Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/395 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/396 -->
# sources/test-tools/xfstests/tests/generic/396

## Purpose
Test that FS_IOC_SET_ENCRYPTION_POLICY correctly validates the fscrypt_policy structure that userspace passes to it. It is registered as generic/396 with `_begin_fstest` tags `auto, quick, encrypt`, making it part of the filename/directory semantics coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: none. Important state variables and paths include dir=$SCRATCH_MNT/dir. Topic focus: filename/directory semantics. Key helper behavior includes: formats a fresh scratch filesystem; mounts the scratch filesystem.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem.

## Dependencies and Integration Points
Common libraries: common/encrypt, common/filter, common/preamble.

Prerequisite gates: _require_scratch_encryption.

External/helper commands: mkdir.

## Risks and Edge Cases
requires compatible fscrypt, inline encryption, and hardware-wrapped key support.

## Test Signals
The golden `.out` expects normalized signals such as: *** Invalid contents encryption mode ***; SCRATCH_MNT/dir: failed to set encryption policy: Invalid argument; *** Invalid filenames encryption mode ***; SCRATCH_MNT/dir: failed to set encryption policy: Invalid argument; *** Invalid flags ***; SCRATCH_MNT/dir: failed to set encryption policy: Invalid argument. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/396 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/397 -->
# sources/test-tools/xfstests/tests/generic/397

## Purpose
Test accessing encrypted files and directories, both with and without the encryption key. Access with the encryption key is more of a sanity check and is not intended to fully test all the encrypted I/O paths; to do that you'd need to run all the xfstests with encryption enabled. Access without the encryption key, on the other hand, should result in some particular behaviors. It is registered as generic/397 with `_begin_fstest` tags `auto, quick, encrypt`, making it part of the preallocation/range operations, rename/link persistence, filename/directory semantics coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: none. Important state variables and paths include keydesc=$(_generate_session_encryption_key). Topic focus: preallocation/range operations, rename/link persistence, filename/directory semantics. Key helper behavior includes: formats a fresh scratch filesystem; mounts the scratch filesystem; forces unmount/remount persistence checks.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; creates deterministic file layout, data, or extent state; remounts or replays after simulated failure; checks visible metadata, extent maps, hashes, or syscall output.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; explicitly validates behavior across remount, crash replay, or log replay.

## Dependencies and Integration Points
Common libraries: common/encrypt, common/filter, common/preamble.

Prerequisite gates: _require_symlinks; _require_scratch_encryption; _require_command "$KEYCTL_PROG" keyctl.

External/helper commands: $XFS_IO_PROG, diff, find, ln, ls, md5sum, mkdir, rm, stat, touch.

Representative `xfs_io` operations: pwrite 0 4k; pwrite 0 33k; pwrite 0 1k.

## Risks and Edge Cases
requires compatible fscrypt, inline encryption, and hardware-wrapped key support.

## Test Signals
The golden `.out` expects normalized signals such as: stat: cannot statx 'SCRATCH_MNT/edir/empty': No such file or directory; stat: cannot statx 'SCRATCH_MNT/edir/symlink': No such file or directory; 8; 1; Required key not available; SCRATCH_MNT/edir/newfile: Required key not available. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/397 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/398 -->
# sources/test-tools/xfstests/tests/generic/398

## Purpose
Filesystem encryption is designed to enforce that a consistent encryption policy is used within a given encrypted directory tree and that an encrypted directory tree does not contain any unencrypted files. This test verifies that filesystem operations that would violate this constraint fail. This does not test enforcement of this constraint on lookup, which is still needed to detect offline changes. It is registered as generic/398 with `_begin_fstest` tags `auto, quick, encrypt`, making it part of the rename/link persistence coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: none. Important state variables and paths include edir1=$SCRATCH_MNT/edir1, edir2=$SCRATCH_MNT/edir2, udir=$SCRATCH_MNT/udir, keydesc1=$(_generate_session_encryption_key), keydesc2=$(_generate_session_encryption_key), efile1=$(find $edir1 -type f), efile2=$(find $edir2 -type f). Topic focus: rename/link persistence. Key helper behavior includes: formats a fresh scratch filesystem; mounts the scratch filesystem; forces unmount/remount persistence checks.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; remounts or replays after simulated failure.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; explicitly validates behavior across remount, crash replay, or log replay.

## Dependencies and Integration Points
Common libraries: common/encrypt, common/filter, common/preamble, common/renameat2.

Prerequisite gates: _require_scratch_encryption; _require_renameat2 exchange.

External/helper commands: find, ln, mkdir, mkfifo, rm, touch.

## Risks and Edge Cases
requires compatible fscrypt, inline encryption, and hardware-wrapped key support.

## Test Signals
The golden `.out` expects normalized signals such as: *** Link encrypted <= encrypted ***; ln: failed to create hard link 'SCRATCH_MNT/edir2/efile1' => 'SCRATCH_MNT/edir1/efile1': Invalid cross-device link; *** Rename encrypted => encrypted ***; Invalid cross-device link; *** Link unencrypted <= encrypted ***; ln: failed to create hard link 'SCRATCH_MNT/edir1/ufile' => 'SCRATCH_MNT/udir/ufile': Invalid cross.... Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/398 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/399 -->
# sources/test-tools/xfstests/tests/generic/399

## Purpose
Check for weaknesses in filesystem encryption involving the same ciphertext being repeated. For file contents, we fill a small filesystem with large files of 0's and verify the filesystem is incompressible. For filenames, we create an identical symlink in two different directories and verify the ciphertext filenames and symlink targets are different. This test can detect some basic cryptographic mistakes such as nonce reuse (across files), initialization vector reuse (across blocks), or data somehow being left in plaintext by accident. For example, it detects the initialization vector reuse bug fixed in commit 02fc59a0d28f ("f2fs/crypto: fix xts_tweak initialization"). It is registered as generic/399 with `_begin_fstest` tags `auto, encrypt`, making it part of the preallocation/range operations, rename/link persistence coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: none. Important state variables and paths include fs_size_in_mb=64, fs_size=$((fs_size_in_mb * 1024 * 1024)), keydesc=$(_generate_session_encryption_key), total_file_size=0, i=1, fs_compressed_size=$(head -c $fs_size $SCRATCH_DEV | \, link1=$(find $SCRATCH_MNT/encrypted_dir -type l ..., link2=$(find $SCRATCH_MNT/encrypted_dir -type l .... Topic focus: preallocation/range operations, rename/link persistence. Key helper behavior includes: formats a scratch filesystem with a controlled size; formats a fresh scratch filesystem; mounts the scratch filesystem; unmounts the scratch filesystem.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; creates deterministic file layout, data, or extent state.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem.

## Dependencies and Integration Points
Common libraries: common/encrypt, common/filter, common/preamble.

Prerequisite gates: _require_scratch_encryption; _require_symlinks; _require_command "$XZ_PROG" xz; _require_command "$KEYCTL_PROG" keyctl.

External/helper commands: $XFS_IO_PROG, dd, find, grep, ln, mkdir.

Representative `xfs_io` operations: pwrite 0 1M.

## Risks and Edge Cases
requires compatible fscrypt, inline encryption, and hardware-wrapped key support.

## Test Signals
The golden `.out` expects normalized signals such as: PASS: ciphertexts were not repeated for contents; 2. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/399 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/400 -->
# sources/test-tools/xfstests/tests/generic/400

## Purpose
test out high quota ids retrieved by Q_GETNEXTQUOTA Request for next ID near 2^32 should not wrap to 0 Designed to use the new Q_GETNEXTQUOTA quotactl. It is registered as generic/400 with `_begin_fstest` tags `auto, quick, quota`, making it part of the ACL/permission semantics, quota accounting coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: none. Important state variables and paths include MOUNT_OPTIONS=-o usrquota,grpquota, ID=4294967292. Topic focus: ACL/permission semantics, quota accounting. Key helper behavior includes: formats a fresh scratch filesystem; unmounts the scratch filesystem.

## Control Flow
formats the scratch filesystem.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; observes inode mode, ownership, ACL, and permission state.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble, common/quota.

Prerequisite gates: _require_quota; _require_scratch; _require_getnextquota.

External/helper commands: chown, touch.

## Risks and Edge Cases
depends on user/group identity setup and permission model details.

## Test Signals
The golden `.out` expects normalized signals such as: Launch all quotas; Ask for ID after 4294967293 expecting nothing; Q_GETNEXTQUOTA: No such file or directory; Q_XGETNEXTQUOTA: No such file or directory; Ask for ID after 4294967293 expecting nothing; Q_GETNEXTQUOTA: No such file or directory. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/400 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/401 -->
# sources/test-tools/xfstests/tests/generic/401

## Purpose
Test filetype feature This test does NOT require that file system support the d_type feature. It verifies that file types are reported as either DT_UNKNOWN or as the actual file type. For example, special dir entries . and .. MAY be reported as DT_UNKNOWN IF filetype feature is disabled (ext4), but MAY also be reported as DT_DIR in this case (xfs). For fs for which we know how to test the filetype feature (xfs|ext*) verify getting DT_UNKNOWN IFF feature is disabled. It is registered as generic/401 with `_begin_fstest` tags `auto, quick`, making it part of the rename/link persistence, filename/directory semantics coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: none. Important state variables and paths include testdir=$SCRATCH_MNT/find-by-type. Topic focus: rename/link persistence, filename/directory semantics. Key helper behavior includes: formats a fresh scratch filesystem; mounts the scratch filesystem.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble.

Prerequisite gates: _require_scratch; _require_symlinks; _require_mknod; _require_test_program "t_dir_type".

External/helper commands: ln, mkdir, mknod, sort, touch.

## Risks and Edge Cases
failures may reflect missing helper binaries or unsupported filesystem features rather than the target regression.

## Test Signals
The golden `.out` expects normalized signals such as: . d; .. d; b b; c c; d d; f f. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/401 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/402 -->
# sources/test-tools/xfstests/tests/generic/402

## Purpose
Test to verify filesystem timestamps for supported ranges. Exit status 1: test failed. Exit status 0: test passed. It is registered as generic/402 with `_begin_fstest` tags `auto, quick, rw, bigtime`, making it part of the filesystem regression behavior coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: check_stat, run_test_individual, run_test. Important state variables and paths include update_time=1, n=1, update_time=0. Topic focus: general filesystem semantics. Key helper behavior includes: formats a fresh scratch filesystem; mounts the scratch filesystem; forces unmount/remount persistence checks.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; remounts or replays after simulated failure; checks visible metadata, extent maps, hashes, or syscall output; wraps repeated scenarios in local helper functions check_stat, run_test_individual, run_test.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; explicitly validates behavior across remount, crash replay, or log replay.

## Dependencies and Integration Points
Common libraries: common/attr, common/filter, common/preamble.

Prerequisite gates: _require_scratch; _require_check_dmesg; _require_xfs_io_command utimes; _require_timestamp_range $SCRATCH_DEV.

External/helper commands: $XFS_IO_PROG, attr, grep, rm, stat.

Representative `xfs_io` operations: utimes $timestamp 0 $timestamp 0.

## Risks and Edge Cases
failures may reflect missing helper binaries or unsupported filesystem features rather than the target regression.

## Test Signals
The golden `.out` expects normalized signals such as: Silence is golden. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/402 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/403 -->
# sources/test-tools/xfstests/tests/generic/403

## Purpose
Test racing getxattr requests against large xattr add and remove loop. This reproduces a bug on XFS where a getxattr of an existing attribute spuriously returned failure due to races with attribute fork conversion. It is registered as generic/403 with `_begin_fstest` tags `auto, quick, attr`, making it part of the extended attributes coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: none. Important state variables and paths include runfile=$tmp.getfattr, getfattr_pid=$!, largeval=`for i in $(seq 0 511); do echo -n a; done`. Topic focus: extended attributes. Key helper behavior includes: formats a fresh scratch filesystem; mounts the scratch filesystem.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; checks visible metadata, extent maps, hashes, or syscall output.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; persists extended-attribute namespace/value state.

## Dependencies and Integration Points
Common libraries: common/attr, common/preamble.

Prerequisite gates: _require_scratch; _require_attrs trusted.

External/helper commands: $ATTR_PROG, $SETFATTR_PROG, attr, getfattr, rm, touch.

## Risks and Edge Cases
timing and workload races can expose intermittent kernel behavior.

## Test Signals
The golden `.out` expects normalized signals such as: Silence is golden. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/403 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/404 -->
# sources/test-tools/xfstests/tests/generic/404

## Purpose
Regression test which targets two nasty ext4 bugs in a logic which shifts extents: 1) 14d981f468a1 ("ext4: Include forgotten start block on fallocate insert range") An incorrect right shift (insert range) for the first extent in a range. Test tries to insert many blocks at the same offset to reproduce the following layout: block #0 block #1 |ext0 ext1|ext2 ext3 ...| ^ insert of a new block Because of an incorrect range first block is never reached, thus ext1 is untouched, resulting to a hole at a wrong offset: What we got: block #0 block #1 |ext0 ext1| ext2 ext3 ...| ^ hole at a wrong offset What we expect: block #0 block #1 |ext0 ext1|ext2 ext3 ...| ^ hole at a correct offset 2) 2b3864b32403 ("ext4: do not polute the extents cache while shifting extents") Extents status tree is filled in with outdated offsets while doing extents shift, that leads to wrong data blocks. That is why test writes unique block content and checks md5sum of a result file after each block insert. It is registered as generic/404 with `_begin_fstest` tags `auto, quick, insert, prealloc`, making it part of the preallocation/range operations, holes/sparse files coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: _cleanup. Important state variables and paths include testfile=$TEST_DIR/$seq.file, pattern=$tmp.pattern, blksize=`_get_file_block_size $TEST_DIR`. Topic focus: preallocation/range operations, holes/sparse files. The script is mostly linear and relies on xfstests common helpers for setup, filtering, and cleanup.

## Control Flow
operates in the configured test filesystem; creates deterministic file layout, data, or extent state; checks visible metadata, extent maps, hashes, or syscall output; wraps repeated scenarios in local helper functions _cleanup.

## State and Persistence Behavior
uses persistent files under TEST_DIR; depends on extent layout and size metadata remaining consistent.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble.

Prerequisite gates: _require_test; _require_xfs_io_command "falloc"; _require_xfs_io_command "finsert".

External/helper commands: $XFS_IO_PROG, awk, md5sum, rm.

Representative `xfs_io` operations: falloc 0 $(($blksize * 2)); pwrite -i $pattern        0 $blksize; pwrite -i $pattern $blksize $blksize; finsert $blksize $blksize.

## Risks and Edge Cases
results are sensitive to filesystem feature support and allocation alignment.

## Test Signals
The golden `.out` expects normalized signals such as: #3 d5562922bd01c2def22f4225aaacd1c2  -; #4 e5f7593f700782765f56f83bd355079b  -; #5 837132f2781fe2153853fba18f5767a2  -; #6 ff35d6b4461189846c6eb9e1fecfdda8  -; #7 c6da6180691decb6e365f5b5a222241c  -; #8 91f7aad51e10aafc550f0622d9662b2e  -. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/404 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/405 -->
# sources/test-tools/xfstests/tests/generic/405

## Purpose
Test mkfs against thin provision device, which has very small backing size, mkfs should return error when it hits EIO. It is registered as generic/405 with `_begin_fstest` tags `auto, mkfs, thin`, making it part of the writeback error reporting coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: _cleanup. Important state variables and paths include BACKING_SIZE=$((1 * 1024 * 1024 / 512)), VIRTUAL_SIZE=$((1 * 1024 * 1024 * 1024 * 1024 / 512)). Topic focus: writeback error reporting. Key helper behavior includes: sets up dm-thin backing storage.

## Control Flow
initializes device-mapper or log-writes infrastructure; wraps repeated scenarios in local helper functions _cleanup.

## State and Persistence Behavior
explicitly validates behavior across remount, crash replay, or log replay.

## Dependencies and Integration Points
Common libraries: common/dmthin, common/filter, common/preamble.

Prerequisite gates: _require_scratch_nocheck; _require_dm_target thin-pool.

External/helper commands: rm.

## Risks and Edge Cases
device-mapper setup, replay ordering, or host capabilities can dominate failures.

## Test Signals
The golden `.out` expects normalized signals such as: Silence is golden. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/405 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/406 -->
# sources/test-tools/xfstests/tests/generic/406

## Purpose
If a larger dio write (size >= 128M) got splitted, the assertion in endio would complain (CONFIG_BTRFS_ASSERT is required). Regression test for Btrfs: adjust outstanding_extents counter properly when dio write is split. It is registered as generic/406 with `_begin_fstest` tags `auto, quick`, making it part of the filesystem regression behavior coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: none. Important state variables and paths include blocksize=$(( (128 + 1) * 2 * 1024 * 1024)), fsblock=$(( (128 + 1) * 2 * 1024)). Topic focus: general filesystem semantics. Key helper behavior includes: formats a fresh scratch filesystem; mounts the scratch filesystem; unmounts the scratch filesystem.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; creates deterministic file layout, data, or extent state.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble.

Prerequisite gates: _require_scratch; _require_odirect; _require_fs_space $SCRATCH_MNT $fsblock.

External/helper commands: $XFS_IO_PROG.

Representative `xfs_io` operations: pwrite -b ${blocksize} 0 ${blocksize}.

## Risks and Edge Cases
failures may reflect missing helper binaries or unsupported filesystem features rather than the target regression.

## Test Signals
The golden `.out` expects normalized signals such as: Silence is golden. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/406 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/407 -->
# sources/test-tools/xfstests/tests/generic/407

## Purpose
Verify that mtime is updated when cloning files. It is registered as generic/407 with `_begin_fstest` tags `auto, quick, clone, metadata`, making it part of the reflink/shared extents coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: _cleanup. Important state variables and paths include sourcefile=$TEST_DIR/clone_mtime_sourcefile, destfile=$TEST_DIR/clone_mtime_destfile, mtime1=`stat -c %Y $destfile`, ctime1=`stat -c %Z $destfile`, mtime2=`stat -c %Y $destfile`, ctime2=`stat -c %Z $destfile`. Topic focus: reflink/shared extents. The script is mostly linear and relies on xfstests common helpers for setup, filtering, and cleanup.

## Control Flow
operates in the configured test filesystem; creates deterministic file layout, data, or extent state; exercises clone/dedupe shared-extent operations; forces durability boundaries with sync/fsync operations; checks visible metadata, extent maps, hashes, or syscall output; wraps repeated scenarios in local helper functions _cleanup.

## State and Persistence Behavior
uses persistent files under TEST_DIR; uses sync-family calls as persistence barriers; depends on extent layout and size metadata remaining consistent.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble, common/reflink.

Prerequisite gates: _require_test; _require_test_reflink.

External/helper commands: $XFS_IO_PROG, rm, stat, touch.

Representative `xfs_io` operations: pwrite 0 4k; reflink $sourcefile.

## Risks and Edge Cases
results are sensitive to filesystem feature support and allocation alignment.

## Test Signals
The golden `.out` expects normalized signals such as: Silence is golden.. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/407 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/408 -->
# sources/test-tools/xfstests/tests/generic/408

## Purpose
Verify that mtime is not updated when deduping files. It is registered as generic/408 with `_begin_fstest` tags `auto, quick, clone, dedupe, metadata`, making it part of the reflink/shared extents, dedupe coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: _cleanup. Important state variables and paths include sourcefile=$TEST_DIR/dedup_mtime_sourcefile, destfile=$TEST_DIR/dedup_mtime_destfile, mtime1=`stat -c %Y $destfile`, ctime1=`stat -c %Z $destfile`, mtime2=`stat -c %Y $destfile`, ctime2=`stat -c %Z $destfile`. Topic focus: reflink/shared extents, dedupe. Key helper behavior includes: deduplicates matching byte ranges.

## Control Flow
operates in the configured test filesystem; creates deterministic file layout, data, or extent state; exercises clone/dedupe shared-extent operations; forces durability boundaries with sync/fsync operations; checks visible metadata, extent maps, hashes, or syscall output; wraps repeated scenarios in local helper functions _cleanup.

## State and Persistence Behavior
uses persistent files under TEST_DIR; uses sync-family calls as persistence barriers; depends on extent layout and size metadata remaining consistent.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble, common/reflink.

Prerequisite gates: _require_test; _require_test_dedupe.

External/helper commands: $XFS_IO_PROG, rm, stat.

Representative `xfs_io` operations: pwrite 0 4k.

## Risks and Edge Cases
results are sensitive to filesystem feature support and allocation alignment.

## Test Signals
The golden `.out` expects normalized signals such as: Silence is golden.. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/408 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/409 -->
# sources/test-tools/xfstests/tests/generic/409

## Purpose
Test mount shared subtrees, verify the bind semantics: --------------------------------------------------------------------------- | BIND MOUNT OPERATION | |************************************************************************** |source(A)->| shared | private | slave | unbindable | | dest(B) | | | | | | | | | | | | | v | | | | | |************************************************************************** | shared | shared | shared | shared & slave | invalid | | | | | | | |non-shared| shared | private | slave | invalid | ***************************************************************************. It is registered as generic/409 with `_begin_fstest` tags `auto, quick, mount`, making it part of the ACL/permission semantics, fiemap/bmap reporting, rename/link persistence, filename/directory semantics coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: _cleanup, fs_stress, find_mnt, start_test, end_test, bind_run, bind_test. Important state variables and paths include MNTHEAD=$TEST_DIR/$seq, mpA=$MNTHEAD/"$$"_mpA, mpB=$MNTHEAD/"$$"_mpB, mpC=$MNTHEAD/"$$"_mpC, mpD=$MNTHEAD/"$$"_mpD. Topic focus: ACL/permission semantics, fiemap/bmap reporting, rename/link persistence, filename/directory semantics. Key helper behavior includes: formats a fresh scratch filesystem; starts fsstress workload generation.

## Control Flow
formats the scratch filesystem; creates deterministic file layout, data, or extent state; checks visible metadata, extent maps, hashes, or syscall output; wraps repeated scenarios in local helper functions _cleanup, fs_stress, find_mnt, start_test, end_test, bind_run.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; uses persistent files under TEST_DIR; observes inode mode, ownership, ACL, and permission state; depends on extent layout and size metadata remaining consistent.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble.

Prerequisite gates: _require_test; _require_scratch; _require_local_device $SCRATCH_DEV.

External/helper commands: $MOUNT_PROG, chown, mkdir, mount, rm, rmdir, sed, sort.

## Risks and Edge Cases
results are sensitive to filesystem feature support and allocation alignment; depends on user/group identity setup and permission model details.

## Test Signals
The golden `.out` expects normalized signals such as: bind shared on shared; ------; TEST_DIR/409 SCRATCH_DEV; mpA SCRATCH_DEV; mpA/dir SCRATCH_DEV; mpB SCRATCH_DEV. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/409 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/410 -->
# sources/test-tools/xfstests/tests/generic/410

## Purpose
Test mount shared subtrees, verify the state transition when use: --make-shared --make-slave --make-private --make-unbindable ------------------------------------------------------------------------ | |make-shared | make-slave | make-private |make-unbindab| --------------|------------|--------------|--------------|-------------| |shared |shared |*slave/private| private | unbindable | | | | | | | |-------------|------------|--------------|--------------|-------------| |slave |shared | **slave | private | unbindable | | |and slave | | | | |-------------|------------|--------------|--------------|-------------| |shared |shared | slave | private | unbindable | |and slave |and slave | | | | |-------------|------------|--------------|--------------|-------------| |private |shared | **private | private | unbindable | |-------------|------------|--------------|--------------|-------------| |unbindable |shared |**unbindable | private | unbindable | ------------------------------------------------------------------------. It is registered as generic/410 with `_begin_fstest` tags `auto, quick, mount`, making it part of the ACL/permission semantics, fiemap/bmap reporting, rename/link persistence, filename/directory semantics coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: _cleanup, fs_stress, find_mnt, start_test, end_test, run, do_test. Important state variables and paths include MNTHEAD=$TEST_DIR/$seq, mpA=$MNTHEAD/"$$"_mpA, mpB=$MNTHEAD/"$$"_mpB, mpC=$MNTHEAD/"$$"_mpC. Topic focus: ACL/permission semantics, fiemap/bmap reporting, rename/link persistence, filename/directory semantics. Key helper behavior includes: formats a fresh scratch filesystem; starts fsstress workload generation.

## Control Flow
formats the scratch filesystem; creates deterministic file layout, data, or extent state; checks visible metadata, extent maps, hashes, or syscall output; wraps repeated scenarios in local helper functions _cleanup, fs_stress, find_mnt, start_test, end_test, run.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; uses persistent files under TEST_DIR; observes inode mode, ownership, ACL, and permission state; depends on extent layout and size metadata remaining consistent.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble.

Prerequisite gates: _require_test; _require_scratch; _require_local_device $SCRATCH_DEV.

External/helper commands: $MOUNT_PROG, chown, mkdir, mount, rm, rmdir, sed, sort, umount.

## Risks and Edge Cases
results are sensitive to filesystem feature support and allocation alignment; depends on user/group identity setup and permission model details.

## Test Signals
The golden `.out` expects normalized signals such as: make-shared a shared mount; before make-shared run on shared; ------; TEST_DIR/410 SCRATCH_DEV; mpA SCRATCH_DEV; mpA/dir SCRATCH_DEV. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/410 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/411 -->
# sources/test-tools/xfstests/tests/generic/411

## Purpose
This test cover linux commit 7ae8fd0, kernel two mnt_group_id == 0 (no peer)vfsmount as peers. It case kernel dereference a NULL address. It is registered as generic/411 with `_begin_fstest` tags `auto, quick, mount`, making it part of the ACL/permission semantics, fiemap/bmap reporting, rename/link persistence coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: _cleanup, fs_stress, find_mnt, start_test, end_test, crash_test. Important state variables and paths include MNTHEAD=$TEST_DIR/$seq, mpA=$MNTHEAD/"$$"_mpA, mpB=$MNTHEAD/"$$"_mpB, mpC=$MNTHEAD/"$$"_mpC. Topic focus: ACL/permission semantics, fiemap/bmap reporting, rename/link persistence. Key helper behavior includes: formats a fresh scratch filesystem; starts fsstress workload generation.

## Control Flow
formats the scratch filesystem; creates deterministic file layout, data, or extent state; checks visible metadata, extent maps, hashes, or syscall output; wraps repeated scenarios in local helper functions _cleanup, fs_stress, find_mnt, start_test, end_test, crash_test.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; uses persistent files under TEST_DIR; observes inode mode, ownership, ACL, and permission state; depends on extent layout and size metadata remaining consistent.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble.

Prerequisite gates: _require_test; _require_scratch; _require_local_device $SCRATCH_DEV.

External/helper commands: $MOUNT_PROG, chown, mkdir, mount, rm, rmdir, sed, sort.

## Risks and Edge Cases
results are sensitive to filesystem feature support and allocation alignment; depends on user/group identity setup and permission model details.

## Test Signals
The golden `.out` expects normalized signals such as: ------; TEST_DIR/411 SCRATCH_DEV; mpA SCRATCH_DEV; mpA/mnt1 SCRATCH_DEV; mpB SCRATCH_DEV; mpB/mnt1 SCRATCH_DEV. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/411 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/412 -->
# sources/test-tools/xfstests/tests/generic/412

## Purpose
Test that if we have a file with a hole, do a mix of direct IO and buffered writes to it and truncate the file to a size that lies in the middle of the hole, after unmounting and mounting again the filesystem, the file has a correct size and no data loss happened. It is registered as generic/412 with `_begin_fstest` tags `auto, quick, metadata`, making it part of the holes/sparse files coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: none. Important state variables and paths include no persistent shell variables beyond harness state. Topic focus: holes/sparse files. Key helper behavior includes: formats a fresh scratch filesystem; mounts the scratch filesystem; forces unmount/remount persistence checks.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; creates deterministic file layout, data, or extent state; remounts or replays after simulated failure; checks visible metadata, extent maps, hashes, or syscall output.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; explicitly validates behavior across remount, crash replay, or log replay; depends on extent layout and size metadata remaining consistent.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble.

Prerequisite gates: _require_scratch; _require_odirect.

External/helper commands: $XFS_IO_PROG, md5sum, truncate.

Representative `xfs_io` operations: pwrite -S 0x01 0K 32K; pwrite -S 0x02 -b 32K 64K 32K; truncate 60K.

## Risks and Edge Cases
failures may reflect missing helper binaries or unsupported filesystem features rather than the target regression.

## Test Signals
The golden `.out` expects normalized signals such as: wrote 32768/32768 bytes at offset 0; XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec); wrote 32768/32768 bytes at offset 65536; XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec); File digest before unmounting the filesystem:; 3c5ca3c3ab42f4b04d7e7eb0b0d4d806  SCRATCH_MNT/foo. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/412 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/413 -->
# sources/test-tools/xfstests/tests/generic/413

## Purpose
mmap direct/buffered io between DAX and non-DAX mountpoints. It is registered as generic/413 with `_begin_fstest` tags `auto, quick, dax, prealloc, mmap`, making it part of the preallocation/range operations coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: prep_files, t_both_dax, t_nondax_to_dax, t_dax_to_nondax, t_both_nondax, t_mmap_dio_dax, do_tests. Important state variables and paths include tsize=$((128 * 1024 * 1024)). Topic focus: preallocation/range operations. Key helper behavior includes: formats a fresh scratch filesystem; mounts the scratch filesystem.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; creates deterministic file layout, data, or extent state; wraps repeated scenarios in local helper functions prep_files, t_both_dax, t_nondax_to_dax, t_dax_to_nondax, t_both_nondax, t_mmap_dio_dax.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; uses persistent files under TEST_DIR; depends on extent layout and size metadata remaining consistent.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble.

Prerequisite gates: _require_hugepages; _require_test; _require_scratch_dax_mountopt "dax"; _require_test_program "feature"; _require_test_program "t_mmap_dio"; _require_xfs_io_command "falloc".

External/helper commands: $XFS_IO_PROG, grep, mount, rm.

Representative `xfs_io` operations: falloc 0 $tsize.

## Risks and Edge Cases
results are sensitive to filesystem feature support and allocation alignment.

## Test Signals
The golden `.out` expects normalized signals such as: Silence is golden. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/413 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/414 -->
# sources/test-tools/xfstests/tests/generic/414

## Purpose
Check that reflinking adjacent blocks in a file produces a single block mapping extent. It is registered as generic/414 with `_begin_fstest` tags `auto, quick, clone, fiemap, prealloc`, making it part of the reflink/shared extents, preallocation/range operations, fiemap/bmap reporting coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: _cleanup. Important state variables and paths include testdir=$SCRATCH_MNT/test-$seq, blocks=32, blksz=65536, sz=$((blocks * blksz)), f1=$(_count_extents $testdir/file1), f2=$(_count_extents $testdir/file2), s1=$($XFS_IO_PROG -c 'fiemap -v' $testdir/fil..., s2=$($XFS_IO_PROG -c 'fiemap -v' $testdir/fil.... Topic focus: reflink/shared extents, preallocation/range operations, fiemap/bmap reporting. Key helper behavior includes: formats a fresh scratch filesystem; mounts the scratch filesystem; forces unmount/remount persistence checks; creates shared extents through reflink range cloning; writes deterministic byte patterns; requires reflink support on scratch.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; creates deterministic file layout, data, or extent state; exercises clone/dedupe shared-extent operations; remounts or replays after simulated failure; checks visible metadata, extent maps, hashes, or syscall output; wraps repeated scenarios in local helper functions _cleanup.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; explicitly validates behavior across remount, crash replay, or log replay; depends on extent layout and size metadata remaining consistent.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble, common/reflink.

Prerequisite gates: _require_scratch_reflink; _require_xfs_io_command "falloc"; _require_xfs_io_command "fiemap"; _require_congruent_file_oplen $SCRATCH_MNT $blksz.

External/helper commands: $XFS_IO_PROG, awk, grep, md5sum, mkdir, mount, rm.

Representative `xfs_io` operations: falloc 0 $sz; fiemap -v; 0x.*[2367aAbBfF]...$.

## Risks and Edge Cases
timing and workload races can expose intermittent kernel behavior; results are sensitive to filesystem feature support and allocation alignment.

## Test Signals
The golden `.out` expects normalized signals such as: Format and mount; Create the original files; Compare files; de89461b64701958984c95d1bfb0065a  SCRATCH_MNT/test-414/file1; de89461b64701958984c95d1bfb0065a  SCRATCH_MNT/test-414/file2; Check extent counts. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/414 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/415 -->
# sources/test-tools/xfstests/tests/generic/415

## Purpose
test for races between write or fpunch operations on reflinked files to read operations on the target file. It is registered as generic/415 with `_begin_fstest` tags `auto, clone, punch`, making it part of the reflink/shared extents, preallocation/range operations coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: none. Important state variables and paths include workfile=${SCRATCH_MNT}/workfile, light_clone=${SCRATCH_MNT}/light_clone, file_size=$((10 * 1024 * 1024)), bs=`_get_block_size $SCRATCH_MNT`, block_num=$((file_size / bs)), reflinks_num=20. Topic focus: reflink/shared extents, preallocation/range operations. Key helper behavior includes: formats a fresh scratch filesystem; mounts the scratch filesystem; requires reflink support on scratch.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; creates deterministic file layout, data, or extent state; exercises clone/dedupe shared-extent operations.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; depends on extent layout and size metadata remaining consistent.

## Dependencies and Integration Points
Common libraries: common/preamble, common/reflink.

Prerequisite gates: _require_scratch_reflink; _require_cp_reflink; _require_xfs_io_command "fpunch"; _require_fs_space $SCRATCH_MNT $((250 * 1024)).

External/helper commands: $XFS_IO_PROG, mount.

Representative `xfs_io` operations: pwrite 0 $file_size; pread $((block_index * bs)) $bs; pwrite $((block_index * bs)) $bs; fpunch $((block_index * bs)) $bs.

## Risks and Edge Cases
timing and workload races can expose intermittent kernel behavior; results are sensitive to filesystem feature support and allocation alignment.

## Test Signals
The golden `.out` expects normalized signals such as: Silence is golden. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/415 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/416 -->
# sources/test-tools/xfstests/tests/generic/416

## Purpose
Test fs behavior when large write request can't be met by one single extent Inspired by a bug in a btrfs fix, which doesn't get exposed by current test cases. It is registered as generic/416 with `_begin_fstest` tags `auto, enospc`, making it part of the preallocation/range operations, ENOSPC/free-space handling, filename/directory semantics coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: fill_fs. Important state variables and paths include fs_size=$((128 * 1024 * 1024)), page_size=$(_get_page_size), nr_files=$(($fs_size / $page_size)). Topic focus: preallocation/range operations, ENOSPC/free-space handling, filename/directory semantics. Key helper behavior includes: formats a scratch filesystem with a controlled size; formats a fresh scratch filesystem; mounts the scratch filesystem; forces filesystem writeback/transaction commit.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; creates deterministic file layout, data, or extent state; forces durability boundaries with sync/fsync operations; wraps repeated scenarios in local helper functions fill_fs.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; uses sync-family calls as persistence barriers.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble.

Prerequisite gates: _require_scratch.

External/helper commands: $XFS_IO_PROG, dd, rm.

Representative `xfs_io` operations: pwrite 0 $(($fs_size / 8)).

## Risks and Edge Cases
failures may reflect missing helper binaries or unsupported filesystem features rather than the target regression.

## Test Signals
The golden `.out` expects normalized signals such as: wrote 16777216/16777216 bytes at offset 0; XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec). Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/416 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/417 -->
# sources/test-tools/xfstests/tests/generic/417

## Purpose
Test orphan inode / unlinked list processing on RO mount & RW transition A filesystem that crashes with open but unlinked inodes should be consistent after a ro, ro->rw, or rw mount cycle. It is registered as generic/417 with `_begin_fstest` tags `auto, quick, shutdown, log`, making it part of the crash recovery/log replay coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: none. Important state variables and paths include no persistent shell variables beyond harness state. Topic focus: crash recovery/log replay. Key helper behavior includes: mounts the scratch filesystem; unmounts the scratch filesystem; requires a journal/log capable filesystem before crash replay.

## Control Flow
mounts the target through the relevant helper layer.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble.

Prerequisite gates: _require_scratch; _require_scratch_shutdown; _require_metadata_journaling $SCRATCH_DEV; _require_test_program "multi_open_unlink".

External/helper commands: mount.

## Risks and Edge Cases
timing and workload races can expose intermittent kernel behavior.

## Test Signals
The golden `.out` expects normalized signals such as: mount dirty orphans rw, then unmount; open and unlink 200 files with EAs; godown; check fs consistency; mount dirty orphans ro, then unmount; open and unlink 200 files with EAs. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/417 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/418 -->
# sources/test-tools/xfstests/tests/generic/418

## Purpose
Test pagecache invalidation in buffer/direct write/read combination. Fork N children, each child writes to and reads from its own region of the same test file, and check if what it reads is what it writes. The test region is determined by N * blksz. Write and read operation can be either direct or buffered. Regression test for commit c771c14baa33 ("iomap: invalidate page caches should be after iomap_dio_complete() in direct write"). It is registered as generic/418 with `_begin_fstest` tags `auto, rw`, making it part of the filesystem regression behavior coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: runtest. Important state variables and paths include diotest=$here/src/dio-invalidate-cache, testfile=$TEST_DIR/$seq-diotest, sectorsize=`$here/src/min_dio_alignment $TEST_DIR $TE..., pagesize=`$here/src/feature -s`, t_cases=(. Topic focus: general filesystem semantics. The script is mostly linear and relies on xfstests common helpers for setup, filtering, and cleanup.

## Control Flow
operates in the configured test filesystem; wraps repeated scenarios in local helper functions runtest.

## State and Persistence Behavior
uses persistent files under TEST_DIR.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble.

Prerequisite gates: _require_test; _require_odirect; _require_block_device $TEST_DEV; _require_test_program "dio-invalidate-cache"; _require_test_program "feature".

## Risks and Edge Cases
failures may reflect missing helper binaries or unsupported filesystem features rather than the target regression.

## Test Signals
The golden `.out` expects normalized signals such as: Silence is golden. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/418 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/419 -->
# sources/test-tools/xfstests/tests/generic/419

## Purpose
Try to rename files in an encrypted directory, without access to the encryption key. This should fail with ENOKEY. Test both a regular rename and a cross rename. This is a regression test for: 173b8439e1ba ("ext4: don't allow encrypted operations without keys") 363fa4e078cb ("f2fs: don't allow encrypted operations without keys"). It is registered as generic/419 with `_begin_fstest` tags `auto, quick, encrypt`, making it part of the rename/link persistence coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: none. Important state variables and paths include keydesc=$(_generate_session_encryption_key), efile1=$(find $SCRATCH_MNT/edir -maxdepth 1 -type..., efile2=$(find $SCRATCH_MNT/edir -maxdepth 1 -type.... Topic focus: rename/link persistence. Key helper behavior includes: formats a fresh scratch filesystem; mounts the scratch filesystem; forces unmount/remount persistence checks.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; remounts or replays after simulated failure.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; explicitly validates behavior across remount, crash replay, or log replay.

## Dependencies and Integration Points
Common libraries: common/encrypt, common/filter, common/preamble, common/renameat2.

Prerequisite gates: _require_scratch_encryption; _require_command "$KEYCTL_PROG" keyctl; _require_renameat2 exchange.

External/helper commands: find, mkdir, mv.

## Risks and Edge Cases
requires compatible fscrypt, inline encryption, and hardware-wrapped key support.

## Test Signals
The golden `.out` expects normalized signals such as: mv: cannot move 'SCRATCH_MNT/edir/NOKEY_NAME' to 'SCRATCH_MNT/edir/NOKEY_NAME': Required key not available; Required key not available. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/419 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/420 -->
# sources/test-tools/xfstests/tests/generic/420

## Purpose
Verify fallocate(mode=FALLOC_FL_KEEP_SIZE|FALLOC_FL_PUNCH_HOLE) does not alter the file size. It is registered as generic/420 with `_begin_fstest` tags `auto, quick, punch`, making it part of the preallocation/range operations coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: none. Important state variables and paths include testfile=${TEST_DIR}/testfile.$seq. Topic focus: preallocation/range operations. The script is mostly linear and relies on xfstests common helpers for setup, filtering, and cleanup.

## Control Flow
operates in the configured test filesystem; creates deterministic file layout, data, or extent state; checks visible metadata, extent maps, hashes, or syscall output.

## State and Persistence Behavior
uses persistent files under TEST_DIR.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble.

Prerequisite gates: _require_test; _require_xfs_io_command fpunch.

External/helper commands: $XFS_IO_PROG, fallocate, grep, stat.

Representative `xfs_io` operations: pwrite -b 2048 0 2048; fpunch 2048 2048; stat.

## Risks and Edge Cases
results are sensitive to filesystem feature support and allocation alignment.

## Test Signals
The golden `.out` expects normalized signals such as: Testing fallocate(mode=FALLOC_FL_KEEP_SIZE|FALLOC_FL_PUNCH_HOLE); wrote 2048/2048 bytes at offset 0; stat.size = 2048. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/420 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/421 -->
# sources/test-tools/xfstests/tests/generic/421

## Purpose
Test revoking an encryption key during concurrent I/O. Regression test for 1b53cf9815bb ("fscrypt: remove broken support for detecting keyring key revocation"). It is registered as generic/421 with `_begin_fstest` tags `auto, quick, encrypt, dangerous`, making it part of the encryption, filename/directory semantics coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: none. Important state variables and paths include dir=$SCRATCH_MNT/encrypted_dir, file=$dir/file, nproc=4, slice=2, keydesc=$(_generate_session_encryption_key), keyid=$(_revoke_session_encryption_key $keydesc). Topic focus: encryption, filename/directory semantics. Key helper behavior includes: formats a fresh scratch filesystem; mounts the scratch filesystem.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; creates deterministic file layout, data, or extent state; forces durability boundaries with sync/fsync operations.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; uses sync-family calls as persistence barriers.

## Dependencies and Integration Points
Common libraries: common/encrypt, common/filter, common/preamble.

Prerequisite gates: _require_scratch_encryption; _require_command "$KEYCTL_PROG" keyctl.

External/helper commands: $XFS_IO_PROG, find, mkdir, rm, touch.

Representative `xfs_io` operations: pwrite 0 $((nproc*slice))M; fsync; fadvise -d $range; pread $range.

## Risks and Edge Cases
timing and workload races can expose intermittent kernel behavior; requires compatible fscrypt, inline encryption, and hardware-wrapped key support.

## Test Signals
The golden `.out` expects normalized signals such as: Didn't crash!. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/421 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/422 -->
# sources/test-tools/xfstests/tests/generic/422

## Purpose
Test that a filesystem's implementation of the stat(2) system call reports correct values for the number of blocks allocated for a file when there are delayed allocations. It is registered as generic/422 with `_begin_fstest` tags `auto, quick, prealloc`, making it part of the preallocation/range operations coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: space_used. Important state variables and paths include no persistent shell variables beyond harness state. Topic focus: preallocation/range operations. Key helper behavior includes: formats a fresh scratch filesystem; mounts the scratch filesystem; forces filesystem writeback/transaction commit.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; creates deterministic file layout, data, or extent state; forces durability boundaries with sync/fsync operations; checks visible metadata, extent maps, hashes, or syscall output; wraps repeated scenarios in local helper functions space_used.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; uses persistent files under TEST_DIR; uses sync-family calls as persistence barriers; depends on extent layout and size metadata remaining consistent.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble.

Prerequisite gates: _require_test; _require_scratch; _require_xfs_io_command "falloc" "-k"; _require_odirect.

External/helper commands: $XFS_IO_PROG, diff, du, touch, truncate.

Representative `xfs_io` operations: pwrite -S 0xaa 0 64K; truncate 128K; falloc -k 0 128K; pwrite -S 0xff 0 64K; pwrite -S 0xff 64K 64K; pwrite -S 0x20 64K 64K; pwrite -S 0xab 0 64K; pwrite -S 0xef 0 64K.

## Risks and Edge Cases
results are sensitive to filesystem feature support and allocation alignment.

## Test Signals
The golden `.out` expects normalized signals such as: wrote 65536/65536 bytes at offset 0; XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec); wrote 65536/65536 bytes at offset 0; XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec); wrote 65536/65536 bytes at offset 0; XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec). Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/422 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/423 -->
# sources/test-tools/xfstests/tests/generic/423

## Purpose
Test the statx system call. It is registered as generic/423 with `_begin_fstest` tags `auto, quick`, making it part of the preallocation/range operations, rename/link persistence, filename/directory semantics coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: _cleanup. Important state variables and paths include target=$TEST_DIR/$seq-nowhere. Topic focus: preallocation/range operations, rename/link persistence, filename/directory semantics. The script is mostly linear and relies on xfstests common helpers for setup, filtering, and cleanup.

## Control Flow
operates in the configured test filesystem; creates deterministic file layout, data, or extent state; wraps repeated scenarios in local helper functions _cleanup.

## State and Persistence Behavior
uses persistent files under TEST_DIR.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble.

Prerequisite gates: _require_test; _require_test_program "stat_test"; _require_test_program "af_unix"; _require_statx; _require_symlinks; _require_mknod.

External/helper commands: dd, ln, mkdir, mkfifo, mknod, rm.

## Risks and Edge Cases
failures may reflect missing helper binaries or unsupported filesystem features rather than the target regression.

## Test Signals
The golden `.out` expects normalized signals such as: Test statx on a fifo; Test statx on a chardev; Test statx on a directory; Test statx on a blockdev; Test statx on a file; 20+0 records in. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/423 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/424 -->
# sources/test-tools/xfstests/tests/generic/424

## Purpose
Test the statx stx_attribute flags that can be set with chattr. It is registered as generic/424 with `_begin_fstest` tags `auto, quick`, making it part of the filesystem regression behavior coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: _cleanup. Important state variables and paths include testfile=$TEST_DIR/$seq-file, a_supported=, c_supported=, d_supported=, i_supported=, a_list=0, c_list=0, d_list=0, i_list=0. Topic focus: general filesystem semantics. The script is mostly linear and relies on xfstests common helpers for setup, filtering, and cleanup.

## Control Flow
operates in the configured test filesystem; checks visible metadata, extent maps, hashes, or syscall output; wraps repeated scenarios in local helper functions _cleanup.

## State and Persistence Behavior
uses persistent files under TEST_DIR; persists extended-attribute namespace/value state.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble.

Prerequisite gates: _require_test; _require_test_program stat_test; _require_statx; _require_command "$CHATTR_PROG" chattr.

External/helper commands: $ATTR_PROG, $CHATTR_PROG, attr, rm, touch.

## Risks and Edge Cases
failures may reflect missing helper binaries or unsupported filesystem features rather than the target regression.

## Test Signals
The golden `.out` expects normalized signals such as: Silence is golden. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/424 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/425 -->
# sources/test-tools/xfstests/tests/generic/425

## Purpose
Check that FIEMAP produces some output when we require an external block to hold extended attributes. It is registered as generic/425 with `_begin_fstest` tags `auto, quick, attr, fiemap`, making it part of the extended attributes, fiemap/bmap reporting coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: _cleanup. Important state variables and paths include testdir=$SCRATCH_MNT/test-$seq, testfile=$testdir/attrfile, blk_sz=$(_get_file_block_size $SCRATCH_MNT), max_attrs=$((2 * blk_sz / 20)), i=0, f1=$(_count_attr_extents $testfile). Topic focus: extended attributes, fiemap/bmap reporting. Key helper behavior includes: formats a fresh scratch filesystem; mounts the scratch filesystem; forces unmount/remount persistence checks; forces filesystem writeback/transaction commit.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; forces durability boundaries with sync/fsync operations; remounts or replays after simulated failure; checks visible metadata, extent maps, hashes, or syscall output; wraps repeated scenarios in local helper functions _cleanup.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; explicitly validates behavior across remount, crash replay, or log replay; uses sync-family calls as persistence barriers; persists extended-attribute namespace/value state; depends on extent layout and size metadata remaining consistent.

## Dependencies and Integration Points
Common libraries: common/attr, common/filter, common/preamble.

Prerequisite gates: _require_scratch; _require_attrs; _require_xfs_io_command "fiemap" "-a".

External/helper commands: $ATTR_PROG, $SETFATTR_PROG, $XFS_IO_PROG, attr, mkdir, mount, rm, touch.

Representative `xfs_io` operations: fiemap -a -v.

## Risks and Edge Cases
timing and workload races can expose intermittent kernel behavior; results are sensitive to filesystem feature support and allocation alignment.

## Test Signals
The golden `.out` expects normalized signals such as: Format and mount; Create the original files; Check attr extent counts; Check attr extent counts after remount. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/425 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/426 -->
# sources/test-tools/xfstests/tests/generic/426

## Purpose
Check stale handles pointing to unlinked files and non-stale handles pointing to linked files. It is registered as generic/426 with `_begin_fstest` tags `auto, quick, exportfs`, making it part of the filename/directory semantics coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: create_test_files, test_file_handles. Important state variables and paths include NUMFILES=1024, testdir=$TEST_DIR/$seq-dir. Topic focus: filename/directory semantics. The script is mostly linear and relies on xfstests common helpers for setup, filtering, and cleanup.

## Control Flow
operates in the configured test filesystem; wraps repeated scenarios in local helper functions create_test_files, test_file_handles.

## State and Persistence Behavior
uses persistent files under TEST_DIR.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble.

Prerequisite gates: _require_test; _require_test_program "open_by_handle"; _require_exportfs.

External/helper commands: mkdir, rm.

## Risks and Edge Cases
failures may reflect missing helper binaries or unsupported filesystem features rather than the target regression.

## Test Signals
The golden `.out` expects normalized signals such as: test_file_handles TEST_DIR/426-dir -d; test_file_handles TEST_DIR/426-dir; test_file_handles TEST_DIR/426-dir -l; test_file_handles TEST_DIR/426-dir -u. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/426 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/427 -->
# sources/test-tools/xfstests/tests/generic/427

## Purpose
Try to trigger a race of free eofblocks and file extending dio writes. A known bug of XFS has been fixed by "e4229d6 xfs: fix eofblocks race with file extending async dio writes". It is registered as generic/427 with `_begin_fstest` tags `auto, quick, aio, rw`, making it part of the filesystem regression behavior coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: none. Important state variables and paths include open_close_pid=$!, nr_cpu=`$here/src/feature -o`, fsize=$((nr_cpu * 10)). Topic focus: general filesystem semantics. Key helper behavior includes: formats a scratch filesystem with a controlled size; formats a fresh scratch filesystem; mounts the scratch filesystem.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; creates deterministic file layout, data, or extent state.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble.

Prerequisite gates: _require_scratch; _require_test_program "feature"; _require_aiodio aio-dio-eof-race; _require_no_compress; _require_inplace_writes $SCRATCH_MNT.

External/helper commands: $XFS_IO_PROG, rm.

Representative `xfs_io` operations: pwrite -S 0x55 0 $((256 * 1024 * 1024 * 2)).

## Risks and Edge Cases
timing and workload races can expose intermittent kernel behavior.

## Test Signals
The golden `.out` expects normalized signals such as: Success, all done.. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/427 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/428 -->
# sources/test-tools/xfstests/tests/generic/428

## Purpose
This is a regression test for kernel patch: dax: fix data corruption due to stale mmap reads created by Ross Zwisler <ross.zwisler@linux.intel.com>. It is registered as generic/428 with `_begin_fstest` tags `auto, quick, dax, mmap`, making it part of the filesystem regression behavior coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: none. Important state variables and paths include no persistent shell variables beyond harness state. Topic focus: general filesystem semantics. The script is mostly linear and relies on xfstests common helpers for setup, filtering, and cleanup.

## Control Flow
operates in the configured test filesystem.

## State and Persistence Behavior
uses persistent files under TEST_DIR.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble.

Prerequisite gates: _require_test; _require_test_program "t_mmap_stale_pmd".

## Risks and Edge Cases
failures may reflect missing helper binaries or unsupported filesystem features rather than the target regression.

## Test Signals
The golden `.out` expects normalized signals such as: Silence is golden. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/428 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/429 -->
# sources/test-tools/xfstests/tests/generic/429

## Purpose
Test that no-key dentries are revalidated after adding a key. Regression test for: 28b4c263961c ("ext4 crypto: revalidate dentry after adding or removing the key") Furthermore, test that no-key dentries are *not* revalidated after "revoking" a key. This used to be done, but it was broken and was removed by: 1b53cf9815bb ("fscrypt: remove broken support for detecting keyring key revocation") Also test for a race condition bug in 28b4c263961c, fixed by: 03a8bb0e53d9 ("ext4/fscrypto: avoid RCU lookup in d_revalidate") Note: the following fix for another race in 28b4c263961c should be applied as well, though we don't test for it because it's very difficult to reproduce: 3d43bcfef5f0 ("ext4 crypto: use dget_parent() in ext4_d_revalidate()"). It is registered as generic/429 with `_begin_fstest` tags `auto, encrypt`, making it part of the encryption, filename/directory semantics coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: show_file_contents, show_directory_with_key. Important state variables and paths include keydesc=$(_generate_key_descriptor), raw_key=$(_generate_raw_encryption_key), nokey_names=( $(find $SCRATCH_MNT/edir -mindepth 1 | s.... Topic focus: encryption, filename/directory semantics. Key helper behavior includes: formats a fresh scratch filesystem; mounts the scratch filesystem; forces unmount/remount persistence checks.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; remounts or replays after simulated failure; wraps repeated scenarios in local helper functions show_file_contents, show_directory_with_key.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; explicitly validates behavior across remount, crash replay, or log replay.

## Dependencies and Integration Points
Common libraries: common/encrypt, common/filter, common/preamble.

Prerequisite gates: _require_scratch_encryption; _require_command "$KEYCTL_PROG" keyctl; _require_test_program "t_encrypted_d_revalidate".

External/helper commands: find, mkdir, rm, sort.

## Risks and Edge Cases
requires compatible fscrypt, inline encryption, and hardware-wrapped key support.

## Test Signals
The golden `.out` expects normalized signals such as: ***** Without encryption key *****; --- Directory listing:; SCRATCH_MNT/edir/NOKEY_NAME; SCRATCH_MNT/edir/NOKEY_NAME; --- Contents of files using plaintext names:; cat: SCRATCH_MNT/edir/@@@: No such file or directory. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/429 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/430 -->
# sources/test-tools/xfstests/tests/generic/430

## Purpose
Tests vfs_copy_file_range(): - Copy a file - Copy beginning of original to new file - Copy middle of original to a new file - Copy end of original to new file - Copy middle of original to a new file, creating a hole. It is registered as generic/430 with `_begin_fstest` tags `auto, quick, copy_range`, making it part of the holes/sparse files coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: none. Important state variables and paths include testdir=$TEST_DIR/test-$seq. Topic focus: holes/sparse files. The script is mostly linear and relies on xfstests common helpers for setup, filtering, and cleanup.

## Control Flow
operates in the configured test filesystem; creates deterministic file layout, data, or extent state; checks visible metadata, extent maps, hashes, or syscall output.

## State and Persistence Behavior
uses persistent files under TEST_DIR.

## Dependencies and Integration Points
Common libraries: common/preamble.

Prerequisite gates: _require_xfs_io_command "copy_range"; _require_test.

External/helper commands: $XFS_IO_PROG, cmp, md5sum, mkdir, rm.

Representative `xfs_io` operations: copy_range $testdir/file; pwrite -S 0x61 0    1000; pwrite -S 0x62 1000 1000; pwrite -S 0x63 2000 1000; pwrite -S 0x64 3000 1000; pwrite -S 0x65 4000 1000; copy_range -l 1000 $testdir/file; copy_range -s 1000 -l 3000 $testdir/file; copy_range -s 4000 -l 1000 $testdir/file; copy_range -s 4000 -l 2000 $testdir/file.

## Risks and Edge Cases
failures may reflect missing helper binaries or unsupported filesystem features rather than the target regression.

## Test Signals
The golden `.out` expects normalized signals such as: Create the original file and then copy; Original md5sums:; e11fbace556cba26bf0076e74cab90a3  TEST_DIR/test-430/file; e11fbace556cba26bf0076e74cab90a3  TEST_DIR/test-430/copy; Copy beginning of original file; md5sums after copying beginning:. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/430 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/431 -->
# sources/test-tools/xfstests/tests/generic/431

## Purpose
Tests vfs_copy_file_range(): - Copy a small file - Small copies from various points in the original file. It is registered as generic/431 with `_begin_fstest` tags `auto, quick, copy_range`, making it part of the filesystem regression behavior coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: none. Important state variables and paths include testdir=$TEST_DIR/test-$seq. Topic focus: general filesystem semantics. The script is mostly linear and relies on xfstests common helpers for setup, filtering, and cleanup.

## Control Flow
operates in the configured test filesystem; checks visible metadata, extent maps, hashes, or syscall output.

## State and Persistence Behavior
uses persistent files under TEST_DIR.

## Dependencies and Integration Points
Common libraries: common/preamble.

Prerequisite gates: _require_xfs_io_command "copy_range"; _require_test.

External/helper commands: $XFS_IO_PROG, cmp, md5sum, mkdir, rm.

Representative `xfs_io` operations: copy_range $testdir/file; copy_range -s 0 -l 1      $testdir/file; copy_range -s 1 -l 1      $testdir/file; copy_range -s 2 -l 1      $testdir/file; copy_range -s 3 -l 1      $testdir/file; copy_range -s 4 -l 1      $testdir/file; copy_range -s 4 -l 1 -d 1 $testdir/file; copy_range -s 5 -l 1      $testdir/file.

## Risks and Edge Cases
failures may reflect missing helper binaries or unsupported filesystem features rather than the target regression.

## Test Signals
The golden `.out` expects normalized signals such as: Create the original file and then copy; Original md5sums:; ab56b4d92b40713acc5af89985d4b786  TEST_DIR/test-431/file; ab56b4d92b40713acc5af89985d4b786  TEST_DIR/test-431/copy; Small copies from various points in the original file; md5sums after small copies. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/431 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/432 -->
# sources/test-tools/xfstests/tests/generic/432

## Purpose
Tests vfs_copy_file_range(): - Copy a file - Use copy to swap data at beginning and end - Use copy to swap data in the middle - Use copy to simultaneously overwrite and append to destination file. It is registered as generic/432 with `_begin_fstest` tags `auto, quick, copy_range`, making it part of the swapfile activation coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: none. Important state variables and paths include testdir=$TEST_DIR/test-$seq. Topic focus: swapfile activation. The script is mostly linear and relies on xfstests common helpers for setup, filtering, and cleanup.

## Control Flow
operates in the configured test filesystem; creates deterministic file layout, data, or extent state; checks visible metadata, extent maps, hashes, or syscall output.

## State and Persistence Behavior
uses persistent files under TEST_DIR.

## Dependencies and Integration Points
Common libraries: common/preamble.

Prerequisite gates: _require_xfs_io_command "copy_range"; _require_test.

External/helper commands: $XFS_IO_PROG, cmp, md5sum, mkdir, rm.

Representative `xfs_io` operations: copy_range $testdir/file; pwrite -S 0x61 0    1000; pwrite -S 0x62 1000 1000; pwrite -S 0x63 2000 1000; pwrite -S 0x64 3000 1000; pwrite -S 0x65 4000 1000; copy_range -s 4000 -l 1000 $testdir/file; copy_range -d 4000 -l 1000 $testdir/file; copy_range -s 1000 -d 3000 -l 1000 $testdir/file; copy_range -s 3000 -d 1000 -l 1000 $testdir/file.

## Risks and Edge Cases
failures may reflect missing helper binaries or unsupported filesystem features rather than the target regression.

## Test Signals
The golden `.out` expects normalized signals such as: Create the original file and then copy; Original md5sums:; e11fbace556cba26bf0076e74cab90a3  TEST_DIR/test-432/file; e11fbace556cba26bf0076e74cab90a3  TEST_DIR/test-432/copy; Swap beginning and end of original file; md5sums after swapping beginning and end:. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/432 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/433 -->
# sources/test-tools/xfstests/tests/generic/433

## Purpose
Tests vfs_copy_file_range(): - Copy a small file - Use copy to swap data at beginning and end - Use copy to swap data in the middle - Use copy to swap data in a small file. It is registered as generic/433 with `_begin_fstest` tags `auto, quick, copy_range`, making it part of the swapfile activation coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: none. Important state variables and paths include testdir=$TEST_DIR/test-$seq. Topic focus: swapfile activation. The script is mostly linear and relies on xfstests common helpers for setup, filtering, and cleanup.

## Control Flow
operates in the configured test filesystem; checks visible metadata, extent maps, hashes, or syscall output.

## State and Persistence Behavior
uses persistent files under TEST_DIR.

## Dependencies and Integration Points
Common libraries: common/preamble.

Prerequisite gates: _require_xfs_io_command "copy_range"; _require_test.

External/helper commands: $XFS_IO_PROG, cmp, md5sum, mkdir, rm.

Representative `xfs_io` operations: copy_range $testdir/file; copy_range -s 0 -d 4 -l 1 $testdir/file; copy_range -s 4 -d 0 -l 1 $testdir/file; copy_range -s 1 -d 3 -l 1 $testdir/file; copy_range -s 3 -d 1 -l 1 $testdir/file; copy_range -s 1 -d 3 -l 4 $testdir/file.

## Risks and Edge Cases
failures may reflect missing helper binaries or unsupported filesystem features rather than the target regression.

## Test Signals
The golden `.out` expects normalized signals such as: Create the original file and then copy; Original md5sums:; ab56b4d92b40713acc5af89985d4b786  TEST_DIR/test-433/file; ab56b4d92b40713acc5af89985d4b786  TEST_DIR/test-433/copy; Swap beginning and end of original file; md5sums after swapping beginning and end:. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/433 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/434 -->
# sources/test-tools/xfstests/tests/generic/434

## Purpose
Tests vfs_copy_file_range() error checking. It is registered as generic/434 with `_begin_fstest` tags `auto, quick, copy_range`, making it part of the filesystem regression behavior coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: none. Important state variables and paths include testdir=$TEST_DIR/test-$seq. Topic focus: general filesystem semantics. The script is mostly linear and relies on xfstests common helpers for setup, filtering, and cleanup.

## Control Flow
operates in the configured test filesystem; creates deterministic file layout, data, or extent state; checks visible metadata, extent maps, hashes, or syscall output.

## State and Persistence Behavior
uses persistent files under TEST_DIR.

## Dependencies and Integration Points
Common libraries: common/preamble.

Prerequisite gates: _require_xfs_io_command "copy_range"; _require_test; _require_mknod.

External/helper commands: $XFS_IO_PROG, md5sum, mkdir, mkfifo, mknod, rm.

Representative `xfs_io` operations: copy_range -s 1000 -l 100 $testdir/file; pwrite -S 0x61 0 1000; copy_range -s 0 -l 100 $testdir/file.

## Risks and Edge Cases
failures may reflect missing helper binaries or unsupported filesystem features rather than the target regression.

## Test Signals
The golden `.out` expects normalized signals such as: Create the original files; Try to copy when source pos > source size; d41d8cd98f00b204e9800998ecf8427e  TEST_DIR/test-434/copy; Try to copy to a read-only file; copy_range: Bad file descriptor; d41d8cd98f00b204e9800998ecf8427e  TEST_DIR/test-434/copy. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/434 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/435 -->
# sources/test-tools/xfstests/tests/generic/435

## Purpose
Test that without the encryption key for a directory, long filenames are presented in a way which avoids collisions, even though they are abbreviated in order to support names up to NAME_MAX bytes. Regression test for: 6332cd32c829 ("f2fs: check entire encrypted bigname when finding a dentry") 6b06cdee81d6 ("fscrypt: avoid collisions when presenting long encrypted filenames") Even with these two fixes it's still possible to create intentional collisions. For now this test covers "accidental" collisions only. It is registered as generic/435 with `_begin_fstest` tags `auto, encrypt`, making it part of the encryption coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: none. Important state variables and paths include keydesc=$(_generate_session_encryption_key). Topic focus: encryption. Key helper behavior includes: formats a fresh scratch filesystem; mounts the scratch filesystem; forces unmount/remount persistence checks.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; remounts or replays after simulated failure; checks visible metadata, extent maps, hashes, or syscall output.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; explicitly validates behavior across remount, crash replay, or log replay.

## Dependencies and Integration Points
Common libraries: common/encrypt, common/filter, common/preamble.

Prerequisite gates: _require_scratch_encryption; _require_command "$KEYCTL_PROG" keyctl.

External/helper commands: find, mkdir, rm, sort, stat, touch.

## Risks and Edge Cases
requires compatible fscrypt, inline encryption, and hardware-wrapped key support.

## Test Signals
The golden `.out` expects normalized signals such as: 100000; 100000; stat: cannot statx 'SCRATCH_MNT/edir': No such file or directory. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/435 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/436 -->
# sources/test-tools/xfstests/tests/generic/436

## Purpose
More SEEK_DATA/SEEK_HOLE sanity tests. It is registered as generic/436 with `_begin_fstest` tags `auto, quick, rw, seek, prealloc`, making it part of the preallocation/range operations, holes/sparse files coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: _cleanup. Important state variables and paths include tmp=$$, BASE_TEST_FILE=$TEST_DIR/seek_sanity_testfile. Topic focus: preallocation/range operations, holes/sparse files. The script is mostly linear and relies on xfstests common helpers for setup, filtering, and cleanup.

## Control Flow
operates in the configured test filesystem; creates deterministic file layout, data, or extent state; wraps repeated scenarios in local helper functions _cleanup.

## State and Persistence Behavior
uses persistent files under TEST_DIR; depends on extent layout and size metadata remaining consistent.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble.

Prerequisite gates: _require_test; _require_seek_data_hole; _require_xfs_io_command "falloc"; _require_test_program "seek_sanity_test".

External/helper commands: rm.

## Risks and Edge Cases
results are sensitive to filesystem feature support and allocation alignment.

## Test Signals
The golden `.out` expects normalized signals such as: Silence is golden. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/436 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/437 -->
# sources/test-tools/xfstests/tests/generic/437

## Purpose
This is a regression test for kernel patches: mm: avoid spurious 'bad pmd' warning messages dax: Fix race between colliding PMD & PTE entries created by Ross Zwisler <ross.zwisler@linux.intel.com>. It is registered as generic/437 with `_begin_fstest` tags `auto, quick, dax, mmap`, making it part of the filesystem regression behavior coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: none. Important state variables and paths include no persistent shell variables beyond harness state. Topic focus: general filesystem semantics. The script is mostly linear and relies on xfstests common helpers for setup, filtering, and cleanup.

## Control Flow
operates in the configured test filesystem.

## State and Persistence Behavior
uses persistent files under TEST_DIR.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble.

Prerequisite gates: _require_test; _require_test_program "t_mmap_cow_race".

## Risks and Edge Cases
failures may reflect missing helper binaries or unsupported filesystem features rather than the target regression.

## Test Signals
The golden `.out` expects normalized signals such as: Silence is golden. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/437 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/438 -->
# sources/test-tools/xfstests/tests/generic/438

## Purpose
This is a regression test for kernel patch "ext4: Fix data corruption for mmap writes" The problem this test checks for is when too much is zeroed in the tail page that gets written out just while the file gets extended and written to through mmap. Based on test program by Michael Zimmer <michael@swarm64.com>. It is registered as generic/438 with `_begin_fstest` tags `auto, mmap`, making it part of the filesystem regression behavior coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: _cleanup. Important state variables and paths include FILE=$TEST_DIR/testfile_fallocate, SYNCPID=$!. Topic focus: general filesystem semantics. The script is mostly linear and relies on xfstests common helpers for setup, filtering, and cleanup.

## Control Flow
operates in the configured test filesystem; forces durability boundaries with sync/fsync operations; wraps repeated scenarios in local helper functions _cleanup.

## State and Persistence Behavior
uses persistent files under TEST_DIR; uses sync-family calls as persistence barriers.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble.

Prerequisite gates: _require_test; _require_test_program "t_mmap_fallocate".

External/helper commands: $XFS_IO_PROG, rm.

## Risks and Edge Cases
timing and workload races can expose intermittent kernel behavior.

## Test Signals
The golden `.out` expects normalized signals such as: Silence is golden. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/438 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/439 -->
# sources/test-tools/xfstests/tests/generic/439

## Purpose
Test that if we punch a hole in a file, with either a range that goes beyond the file's size or covers a file range that is already a hole, and that if after we do some buffered write operations that cover different parts of the hole, no warnings are emmitted in syslog/dmesg and the file's content is correct after remounting the filesystem. It is registered as generic/439 with `_begin_fstest` tags `auto, quick, punch`, making it part of the preallocation/range operations, holes/sparse files coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: none. Important state variables and paths include no persistent shell variables beyond harness state. Topic focus: preallocation/range operations, holes/sparse files. Key helper behavior includes: formats a fresh scratch filesystem; mounts the scratch filesystem; forces unmount/remount persistence checks.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; creates deterministic file layout, data, or extent state; remounts or replays after simulated failure.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; uses persistent files under TEST_DIR; explicitly validates behavior across remount, crash replay, or log replay.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble.

Prerequisite gates: _require_test; _require_scratch; _require_xfs_io_command "fpunch".

External/helper commands: $XFS_IO_PROG.

Representative `xfs_io` operations: pwrite -S 0xaa 0 100K; fpunch 60K 90K; pwrite -S 0xbb -b 100K 50K 100K; pwrite -S 0xcc -b 50K 100K 50K; fpunch 695K 820K; pwrite -S 0xaa 1008K 307K; pwrite -S 0xbb -b 630K 1073K 630K; pwrite -S 0xcc -b 459K 1068K 459K.

## Risks and Edge Cases
results are sensitive to filesystem feature support and allocation alignment.

## Test Signals
The golden `.out` expects normalized signals such as: wrote 102400/102400 bytes at offset 0; XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec); wrote 102400/102400 bytes at offset 51200; XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec); wrote 51200/51200 bytes at offset 102400; XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec). Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/439 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/440 -->
# sources/test-tools/xfstests/tests/generic/440

## Purpose
Test that when the filesystem tries to enforce that all files in a directory tree use the same encryption policy, it doesn't get confused and incorrectly return EPERM in cases where the parent's key is cached but not the child's, or vice versa. Such situations can arise following removal of the master key from the keyring. Regression test for: 272f98f68462 ("fscrypt: fix context consistency check when key(s) unavailable"). It is registered as generic/440 with `_begin_fstest` tags `auto, quick, encrypt`, making it part of the encryption, rename/link persistence coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: none. Important state variables and paths include keydesc=$(_generate_key_descriptor), raw_key=$(_generate_raw_encryption_key). Topic focus: encryption, rename/link persistence. Key helper behavior includes: formats a fresh scratch filesystem; mounts the scratch filesystem; forces unmount/remount persistence checks.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; remounts or replays after simulated failure; checks visible metadata, extent maps, hashes, or syscall output.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; explicitly validates behavior across remount, crash replay, or log replay.

## Dependencies and Integration Points
Common libraries: common/encrypt, common/filter, common/preamble.

Prerequisite gates: _require_scratch_encryption; _require_symlinks; _require_command "$KEYCTL_PROG" keyctl.

External/helper commands: find, ln, ls, mkdir, sort, stat.

## Risks and Edge Cases
requires compatible fscrypt, inline encryption, and hardware-wrapped key support.

## Test Signals
The golden `.out` expects normalized signals such as: ***** Parent has key, but child doesn't *****; file; subdir; symlink; cat: SCRATCH_MNT/edir/file: Required key not available; cat: SCRATCH_MNT/edir/symlink: No such file or directory. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/440 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/441 -->
# sources/test-tools/xfstests/tests/generic/441

## Purpose
Open a file several times, write to it, fsync on all fds and make sure that they all return 0. Change the device to start throwing errors. Write again on all fds and fsync on all fds. Ensure that we get errors on all of them. Then fsync on all one last time and verify that all return 0. It is registered as generic/441 with `_begin_fstest` tags `auto, quick, eio`, making it part of the writeback error reporting coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: _cleanup. Important state variables and paths include sflag='-s', testfile=$SCRATCH_MNT/fsync-err-test. Topic focus: writeback error reporting. Key helper behavior includes: formats a fresh scratch filesystem; sets up dm-error for I/O fault injection.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; initializes device-mapper or log-writes infrastructure; forces durability boundaries with sync/fsync operations; wraps repeated scenarios in local helper functions _cleanup.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; uses sync-family calls as persistence barriers.

## Dependencies and Integration Points
Common libraries: common/dmerror, common/filter, common/preamble.

Prerequisite gates: _require_scratch; _require_dm_target error; _require_test_program fsync-err; _require_test_program dmerror; _require_fs_space $SCRATCH_MNT 65536.

External/helper commands: mount, rm.

## Risks and Edge Cases
device-mapper setup, replay ordering, or host capabilities can dominate failures; writeback error propagation is asynchronous and must be checked at the intended boundary.

## Test Signals
The golden `.out` expects normalized signals such as: Format and mount; Test passed!. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/441 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/442 -->
# sources/test-tools/xfstests/tests/generic/442

## Purpose
Test writeback error handling when writing to block devices via pagecache. See src/fsync-err.c for details of what test actually does. It is registered as generic/442 with `_begin_fstest` tags `blockdev, eio`, making it part of the writeback error reporting coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: _cleanup. Important state variables and paths include no persistent shell variables beyond harness state. Topic focus: writeback error reporting. Key helper behavior includes: formats a fresh scratch filesystem; sets up dm-error for I/O fault injection.

## Control Flow
formats the scratch filesystem; initializes device-mapper or log-writes infrastructure; forces durability boundaries with sync/fsync operations; wraps repeated scenarios in local helper functions _cleanup.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; uses sync-family calls as persistence barriers.

## Dependencies and Integration Points
Common libraries: common/dmerror, common/filter, common/preamble.

Prerequisite gates: _require_scratch; _require_dm_target error; _require_test_program fsync-err; _require_test_program dmerror.

External/helper commands: rm.

## Risks and Edge Cases
device-mapper setup, replay ordering, or host capabilities can dominate failures; writeback error propagation is asynchronous and must be checked at the intended boundary.

## Test Signals
The golden `.out` expects normalized signals such as: Test passed!. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/442 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/443 -->
# sources/test-tools/xfstests/tests/generic/443

## Purpose
Takes page fault while writev is iterating over the vectors in the IOV. It is registered as generic/443 with `_begin_fstest` tags `auto, quick, rw`, making it part of the filesystem regression behavior coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: none. Important state variables and paths include no persistent shell variables beyond harness state. Topic focus: general filesystem semantics. The script is mostly linear and relies on xfstests common helpers for setup, filtering, and cleanup.

## Control Flow
operates in the configured test filesystem.

## State and Persistence Behavior
uses persistent files under TEST_DIR.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble.

Prerequisite gates: _require_test; _require_test_program "writev_on_pagefault".

## Risks and Edge Cases
failures may reflect missing helper binaries or unsupported filesystem features rather than the target regression.

## Test Signals
The golden `.out` expects normalized signals such as: wrote 3 bytes. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/443 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/444 -->
# sources/test-tools/xfstests/tests/generic/444

## Purpose
Check if SGID is inherited when creating a subdirectory when the owner is not in the owning group and directory has default ACLs. It is registered as generic/444 with `_begin_fstest` tags `auto, quick, acl, perms`, making it part of the ACL/permission semantics coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: none. Important state variables and paths include TDIR=testdir.$seq. Topic focus: ACL/permission semantics. The script is mostly linear and relies on xfstests common helpers for setup, filtering, and cleanup.

## Control Flow
operates in the configured test filesystem; checks visible metadata, extent maps, hashes, or syscall output.

## State and Persistence Behavior
uses persistent files under TEST_DIR; observes inode mode, ownership, ACL, and permission state.

## Dependencies and Integration Points
Common libraries: common/attr, common/filter, common/preamble.

Prerequisite gates: _require_test; _require_runas; _require_acls.

External/helper commands: attr, chmod, chown, mkdir, rm, setfacl, stat.

## Risks and Edge Cases
depends on user/group identity setup and permission model details.

## Test Signals
The golden `.out` expects normalized signals such as: drwxrwsr-x; drwxrwsr-x. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/444 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/445 -->
# sources/test-tools/xfstests/tests/generic/445

## Purpose
Another SEEK_DATA/SEEK_HOLE sanity test. It is registered as generic/445 with `_begin_fstest` tags `auto, quick, rw, seek, prealloc`, making it part of the preallocation/range operations, holes/sparse files coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: _cleanup. Important state variables and paths include tmp=$$, BASE_TEST_FILE=$TEST_DIR/seek_sanity_testfile. Topic focus: preallocation/range operations, holes/sparse files. The script is mostly linear and relies on xfstests common helpers for setup, filtering, and cleanup.

## Control Flow
operates in the configured test filesystem; creates deterministic file layout, data, or extent state; wraps repeated scenarios in local helper functions _cleanup.

## State and Persistence Behavior
uses persistent files under TEST_DIR; depends on extent layout and size metadata remaining consistent.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble.

Prerequisite gates: _require_test; _require_seek_data_hole; _require_xfs_io_command "falloc"; _require_test_program "seek_sanity_test".

External/helper commands: rm.

## Risks and Edge Cases
results are sensitive to filesystem feature support and allocation alignment.

## Test Signals
The golden `.out` expects normalized signals such as: Silence is golden. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/445 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/446 -->
# sources/test-tools/xfstests/tests/generic/446

## Purpose
Regression test for commit: 04197b3 ("xfs: don't BUG() on mixed direct and mapped I/O") This case tests a race between a direct I/O read and a mapped write to a hole in a file. On xfs filesystem, it will trigger a BUG_ON(). It is registered as generic/446 with `_begin_fstest` tags `auto, quick, rw, punch, mmap`, making it part of the preallocation/range operations, holes/sparse files coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: none. Important state variables and paths include filesz=$((65536 * 2)), dread_pid=$!. Topic focus: preallocation/range operations, holes/sparse files. Key helper behavior includes: formats a fresh scratch filesystem; mounts the scratch filesystem; unmounts the scratch filesystem.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; creates deterministic file layout, data, or extent state.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; depends on extent layout and size metadata remaining consistent.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble.

Prerequisite gates: _require_scratch; _require_xfs_io_command "truncate"; _require_xfs_io_command "fpunch"; _require_odirect.

External/helper commands: $XFS_IO_PROG, truncate.

Representative `xfs_io` operations: truncate $((filesz * 2)); pread 0 $filesz; mmap 0 $filesz; mwrite 0 $filesz; fpunch 0 $filesz.

## Risks and Edge Cases
timing and workload races can expose intermittent kernel behavior; results are sensitive to filesystem feature support and allocation alignment.

## Test Signals
The golden `.out` expects normalized signals such as: Silence is golden. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/446 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/447 -->
# sources/test-tools/xfstests/tests/generic/447

## Purpose
See how well we handle deleting a file with a million refcount extents. It is registered as generic/447 with `_begin_fstest` tags `auto, clone, punch`, making it part of the reflink/shared extents, preallocation/range operations coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: _cleanup, calc_space. Important state variables and paths include testdir=$SCRATCH_MNT/test-$seq, fnr=20, free_blocks=$(stat -f -c '%a' "$testdir"), blksz=$(_get_block_size "$testdir"), space_avail=$((free_blocks * blksz)). Topic focus: reflink/shared extents, preallocation/range operations. Key helper behavior includes: formats a fresh scratch filesystem; mounts the scratch filesystem; forces unmount/remount persistence checks; requires reflink support on scratch.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; creates deterministic file layout, data, or extent state; exercises clone/dedupe shared-extent operations; remounts or replays after simulated failure; checks visible metadata, extent maps, hashes, or syscall output; wraps repeated scenarios in local helper functions _cleanup, calc_space.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; explicitly validates behavior across remount, crash replay, or log replay; depends on extent layout and size metadata remaining consistent.

## Dependencies and Integration Points
Common libraries: common/attr, common/filter, common/preamble, common/reflink.

Prerequisite gates: _require_scratch_reflink; _require_cp_reflink; _require_test_program "punch-alternating"; _require_xfs_io_command "fpunch".

External/helper commands: $XFS_IO_PROG, attr, mkdir, mount, rm, stat.

Representative `xfs_io` operations: pwrite -S 0x61 -b 4194304 0 $((2 ** (fnr + 1) * blksz)).

## Risks and Edge Cases
results are sensitive to filesystem feature support and allocation alignment.

## Test Signals
The golden `.out` expects normalized signals such as: Format and mount; Create a many-block file; Reflinking file; Punch file2; Delete file1. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/447 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/448 -->
# sources/test-tools/xfstests/tests/generic/448

## Purpose
Check what happens when SEEK_HOLE/SEEK_DATA are fed negative offsets. It is registered as generic/448 with `_begin_fstest` tags `auto, quick, rw, seek`, making it part of the holes/sparse files coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: _cleanup. Important state variables and paths include BASE_TEST_FILE=$TEST_DIR/seek_sanity_testfile_$seq. Topic focus: holes/sparse files. The script is mostly linear and relies on xfstests common helpers for setup, filtering, and cleanup.

## Control Flow
operates in the configured test filesystem; wraps repeated scenarios in local helper functions _cleanup.

## State and Persistence Behavior
uses persistent files under TEST_DIR.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble.

Prerequisite gates: _require_test; _require_seek_data_hole; _require_test_program "seek_sanity_test".

External/helper commands: rm.

## Risks and Edge Cases
failures may reflect missing helper binaries or unsupported filesystem features rather than the target regression.

## Test Signals
The golden `.out` expects normalized signals such as: Silence is golden. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/448 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/449 -->
# sources/test-tools/xfstests/tests/generic/449

## Purpose
Fill the device and set as many extended attributes to a file as possible. Then call setfacl on it and, if this fails for lack of space, test that the permissions remain the same. It is registered as generic/449 with `_begin_fstest` tags `auto, quick, acl, attr, enospc`, making it part of the ACL/permission semantics, ENOSPC/free-space handling coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: none. Important state variables and paths include TFILE=$SCRATCH_MNT/testfile.$seq, i=1, j=1, ret=0. Topic focus: ACL/permission semantics, ENOSPC/free-space handling. Key helper behavior includes: formats a scratch filesystem with a controlled size; formats a fresh scratch filesystem; mounts the scratch filesystem.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; creates deterministic file layout, data, or extent state; checks visible metadata, extent maps, hashes, or syscall output.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; uses persistent files under TEST_DIR; persists extended-attribute namespace/value state; observes inode mode, ownership, ACL, and permission state.

## Dependencies and Integration Points
Common libraries: common/attr, common/filter, common/preamble.

Prerequisite gates: _require_scratch; _require_test; _require_acls; _require_attrs trusted.

External/helper commands: $ATTR_PROG, $SETFATTR_PROG, $XFS_IO_PROG, attr, chmod, mount, setfacl, stat, touch.

Representative `xfs_io` operations: pwrite 0 256m.

## Risks and Edge Cases
depends on user/group identity setup and permission model details.

## Test Signals
The golden `.out` expects normalized signals such as: -rwx------. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/449 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/450 -->
# sources/test-tools/xfstests/tests/generic/450

## Purpose
Test read around EOF. If the file offset is at or past the end of file, no bytes are read, and read() returns zero. There was a bug, when DIO read offset is just past the EOF a little, but in the same block with EOF, read returns different negative values. The following two kernel commits fixed this bug: 74cedf9b6c60 direct-io: Fix negative return from dio read beyond eof 2d4594acbf6d fix the regression from "direct-io: Fix negative return from dio read beyond eof". It is registered as generic/450 with `_begin_fstest` tags `auto, quick, rw`, making it part of the preallocation/range operations coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: _cleanup, check_xfs_io_read, read_test. Important state variables and paths include tfile=$TEST_DIR/testfile_${seq}, ssize=`$here/src/min_dio_alignment $TEST_DIR $TE..., bsize=`_get_block_size $TEST_DIR`, asize=$((bsize * 2)), tsize=$((asize - ssize * 2)). Topic focus: preallocation/range operations. The script is mostly linear and relies on xfstests common helpers for setup, filtering, and cleanup.

## Control Flow
operates in the configured test filesystem; creates deterministic file layout, data, or extent state; forces durability boundaries with sync/fsync operations; wraps repeated scenarios in local helper functions _cleanup, check_xfs_io_read, read_test.

## State and Persistence Behavior
uses persistent files under TEST_DIR; uses sync-family calls as persistence barriers.

## Dependencies and Integration Points
Common libraries: common/preamble.

Prerequisite gates: _require_test; _require_odirect.

External/helper commands: $XFS_IO_PROG, rm.

Representative `xfs_io` operations: pread 0 $ssize; pread $bsize $bsize; pread $tsize $ssize; pread $((tsize + ssize)) $ssize; pread $((bsize * 100)) $ssize; pwrite 0 ${tsize}; fsync.

## Risks and Edge Cases
failures may reflect missing helper binaries or unsupported filesystem features rather than the target regression.

## Test Signals
The golden `.out` expects normalized signals such as: buffer read the first sector within EOF; buffer read the second block contains EOF; buffer read a sector at (after) EOF; buffer read the last sector past EOF; buffer read at far away from EOF; direct read the first sector within EOF. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/450 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/451 -->
# sources/test-tools/xfstests/tests/generic/451

## Purpose
Test data integrity when mixing buffered reads and asynchronous direct writes a file. It is registered as generic/451 with `_begin_fstest` tags `auto, quick, rw, aio`, making it part of the filesystem regression behavior coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: none. Important state variables and paths include TESTFILE=$TEST_DIR/tst-aio-dio-cycle-write.$seq, FSIZE=655360, nr_cpu=`$here/src/feature -o`, loops=$((nr_cpu / 2)), keep_reading=$tmp.reading. Topic focus: general filesystem semantics. The script is mostly linear and relies on xfstests common helpers for setup, filtering, and cleanup.

## Control Flow
operates in the configured test filesystem; creates deterministic file layout, data, or extent state.

## State and Persistence Behavior
uses persistent files under TEST_DIR.

## Dependencies and Integration Points
Common libraries: common/preamble.

Prerequisite gates: _require_test; _require_test_program "feature"; _require_aiodio aio-dio-cycle-write; _require_command "$TIMEOUT_PROG" timeout.

External/helper commands: $XFS_IO_PROG, rm, touch.

Representative `xfs_io` operations: pread 0 $FSIZE.

## Risks and Edge Cases
timing and workload races can expose intermittent kernel behavior.

## Test Signals
The golden `.out` expects normalized signals such as: Silence is golden. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/451 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/452 -->
# sources/test-tools/xfstests/tests/generic/452

## Purpose
This is a regression test for kernel patch: commit fd96b8da68d3 ("ext4: fix fault handling when mounted with -o dax,ro") created by Ross Zwisler <ross.zwisler@linux.intel.com>. It is registered as generic/452 with `_begin_fstest` tags `auto, quick, dax`, making it part of the filesystem regression behavior coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: none. Important state variables and paths include LS=$(type -P ls), SCRATCH_LS=$SCRATCH_MNT/ls_on_scratch. Topic focus: general filesystem semantics. Key helper behavior includes: formats a fresh scratch filesystem; mounts the scratch filesystem.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble.

Prerequisite gates: _require_scratch.

External/helper commands: cp, ls.

## Risks and Edge Cases
failures may reflect missing helper binaries or unsupported filesystem features rather than the target regression.

## Test Signals
The golden `.out` expects normalized signals such as: SCRATCH_MNT/ls_on_scratch; SCRATCH_MNT/ls_on_scratch. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/452 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/453 -->
# sources/test-tools/xfstests/tests/generic/453

## Purpose
Create a directory with multiple filenames that all appear the same (in unicode, anyway) but point to different inodes. In theory all Linux filesystems should allow this (filenames are a sequence of arbitrary bytes) even if the user implications are horrifying. It is registered as generic/453 with `_begin_fstest` tags `auto, quick, dir`, making it part of the filename/directory semantics coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: hexbytes, setf, setchild, setd, testf, testchild, testd, filter_scrub. Important state variables and paths include testdir=${SCRATCH_MNT}/test-${seq}. Topic focus: filename/directory semantics. Key helper behavior includes: formats a fresh scratch filesystem; mounts the scratch filesystem.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; creates byte-distinct pathname fixtures with confusable Unicode renderings; checks stored values, inode uniqueness, and optional xfs_scrub Unicode diagnostics; wraps repeated scenarios in local helper functions hexbytes, setf, setchild, setd, testf, testchild.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem.

## Dependencies and Integration Points
Common libraries: common/preamble.

Prerequisite gates: _require_scratch; _require_names_are_bytes.

External/helper commands: grep, ls, mkdir, mount, sed, sort, stat.

## Risks and Edge Cases
depends on byte-oriented pathname handling and locale-safe output filtering.

## Test Signals
The golden `.out` expects normalized signals such as: Format and mount; Create files; Test files; Uniqueness of inodes?; Test XFS online scrub, if applicable. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/453 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/454 -->
# sources/test-tools/xfstests/tests/generic/454

## Purpose
Create xattrs with multiple keys that all appear the same (in unicode, anyway) but point to different values. In theory all Linux filesystems should allow this (filenames are a sequence of arbitrary bytes) even if the user implications are horrifying. It is registered as generic/454 with `_begin_fstest` tags `auto, quick, attr`, making it part of the preallocation/range operations, filename/directory semantics coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: hexbytes, setf, testf, filter_scrub. Important state variables and paths include testdir=${SCRATCH_MNT}/test-${seq}, testfile=${testdir}/attrfile, crazy_keys=$(_getfattr --absolute-names -d "${testfil..., expected_keys=11. Topic focus: preallocation/range operations, filename/directory semantics. Key helper behavior includes: formats a fresh scratch filesystem; mounts the scratch filesystem.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; creates deterministic file layout, data, or extent state; checks visible metadata, extent maps, hashes, or syscall output; wraps repeated scenarios in local helper functions hexbytes, setf, testf, filter_scrub.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; persists extended-attribute namespace/value state.

## Dependencies and Integration Points
Common libraries: common/attr, common/preamble.

Prerequisite gates: _require_scratch; _require_attrs; _require_names_are_bytes.

External/helper commands: $ATTR_PROG, $SETFATTR_PROG, attr, grep, mkdir, mount, sed, touch.

## Risks and Edge Cases
depends on byte-oriented pathname handling and locale-safe output filtering.

## Test Signals
The golden `.out` expects normalized signals such as: Format and mount; Create files; Test files; Uniqueness of keys?; Test XFS online scrub, if applicable. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/454 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/455 -->
# sources/test-tools/xfstests/tests/generic/455

## Purpose
Run fsx with log writes to verify power fail safeness. It is registered as generic/455 with `_begin_fstest` tags `auto, log, replay, recoveryloop`, making it part of the crash recovery/log replay, ENOSPC/free-space handling, fsstress/replay consistency coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: _cleanup, check_files. Important state variables and paths include SANITY_DIR=$TEST_DIR/fsxtests, size=$(_small_fs_size_mb 200), devsize=$((1024*1024*size / 512)), csize=$((1024*64 / 512)), lowspace=$((1024*1024 / 512)), NUM_FILES=4, NUM_OPS=200, FSX_OPTS=-N $NUM_OPS -d -P $SANITY_DIR -i $LOGWRITES_DMDEV, seeds=(0 0 0 0), test_md5=(). Topic focus: crash recovery/log replay, ENOSPC/free-space handling, fsstress/replay consistency. Key helper behavior includes: requires a journal/log capable filesystem before crash replay; sets up dm-thin backing storage; captures block writes for replay testing.

## Control Flow
operates in the configured test filesystem; mounts the target through the relevant helper layer; initializes device-mapper or log-writes infrastructure; checks visible metadata, extent maps, hashes, or syscall output; wraps repeated scenarios in local helper functions _cleanup, check_files.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; uses persistent files under TEST_DIR; explicitly validates behavior across remount, crash replay, or log replay.

## Dependencies and Integration Points
Common libraries: common/dmlogwrites, common/dmthin, common/filter, common/preamble.

Prerequisite gates: _require_test; _require_scratch_nocheck; _require_no_logdev; _require_log_writes; _require_dm_target thin-pool; _require_metadata_journaling "$LOGWRITES_DMDEV".

External/helper commands: $FSX_PROG, find, grep, md5sum, mkdir, rm, umount.

## Risks and Edge Cases
timing and workload races can expose intermittent kernel behavior; device-mapper setup, replay ordering, or host capabilities can dominate failures.

## Test Signals
The golden `.out` expects normalized signals such as: Silence is golden. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/455 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/456 -->
# sources/test-tools/xfstests/tests/generic/456

## Purpose
This test is motivated by a bug found in ext4 during random crash consistency tests. Fixed by commit 51e3ae81ec58 ("ext4: fix interaction between i_size, fallocate, and delalloc after a crash") This is also a regression test for ext4 bug that zero range can beyond i_disksize and fixed by commit 801674f34ecf ("ext4: do not zeroout extents beyond i_disksize"). It is registered as generic/456 with `_begin_fstest` tags `auto, quick, metadata, collapse, zero, prealloc`, making it part of the crash recovery/log replay, preallocation/range operations coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: _cleanup. Important state variables and paths include fsxops=$tmp.fsxops. Topic focus: crash recovery/log replay, preallocation/range operations. Key helper behavior includes: formats a fresh scratch filesystem; mounts the scratch filesystem; unmounts the scratch filesystem; requires a journal/log capable filesystem before crash replay; routes the scratch device through dm-flakey; simulates power loss and remounts for replay.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; initializes device-mapper or log-writes infrastructure; creates deterministic file layout, data, or extent state; remounts or replays after simulated failure; wraps repeated scenarios in local helper functions _cleanup.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; explicitly validates behavior across remount, crash replay, or log replay; depends on extent layout and size metadata remaining consistent.

## Dependencies and Integration Points
Common libraries: common/dmflakey, common/filter, common/preamble.

Prerequisite gates: _require_scratch; _require_xfs_io_command "falloc"; _require_dm_target flakey; _require_xfs_io_command "falloc" "-k"; _require_xfs_io_command "fzero"; _require_xfs_io_command "fcollapse"; _require_metadata_journaling $SCRATCH_DEV.

External/helper commands: $FSX_PROG, fallocate, rm.

## Risks and Edge Cases
device-mapper setup, replay ordering, or host capabilities can dominate failures; results are sensitive to filesystem feature support and allocation alignment.

## Test Signals
The golden `.out` expects normalized signals such as: Silence is golden. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/456 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/457 -->
# sources/test-tools/xfstests/tests/generic/457

## Purpose
Run fsx with log writes on cloned files to verify power fail safeness. It is registered as generic/457 with `_begin_fstest` tags `auto, log, replay, clone, recoveryloop`, making it part of the reflink/shared extents, crash recovery/log replay, ENOSPC/free-space handling, fsstress/replay consistency coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: _cleanup, check_files. Important state variables and paths include SANITY_DIR=$TEST_DIR/fsxtests, size=$(_small_fs_size_mb 200), devsize=$((1024*1024*size / 512)), csize=$((1024*64 / 512)), lowspace=$((1024*1024 / 512)), NUM_FILES=10, NUM_OPS=10, FSX_OPTS=-N $NUM_OPS -d -k -P $SANITY_DIR -i $LOGWRITES_DMDEV, test_md5=(). Topic focus: reflink/shared extents, crash recovery/log replay, ENOSPC/free-space handling, fsstress/replay consistency. Key helper behavior includes: sets up dm-thin backing storage; captures block writes for replay testing; requires reflink support on scratch.

## Control Flow
operates in the configured test filesystem; mounts the target through the relevant helper layer; initializes device-mapper or log-writes infrastructure; creates deterministic file layout, data, or extent state; exercises clone/dedupe shared-extent operations; forces durability boundaries with sync/fsync operations; checks visible metadata, extent maps, hashes, or syscall output; wraps repeated scenarios in local helper functions _cleanup, check_files.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; uses persistent files under TEST_DIR; explicitly validates behavior across remount, crash replay, or log replay; uses sync-family calls as persistence barriers; depends on extent layout and size metadata remaining consistent.

## Dependencies and Integration Points
Common libraries: common/dmlogwrites, common/dmthin, common/filter, common/preamble, common/reflink.

Prerequisite gates: _require_test; _require_scratch_reflink; _require_no_logdev; _require_cp_reflink; _require_log_writes; _require_dm_target thin-pool.

External/helper commands: $FSX_PROG, $XFS_IO_PROG, find, grep, md5sum, mkdir, rm, umount.

Representative `xfs_io` operations: pwrite -S 0xff 0 256k; fsync.

## Risks and Edge Cases
timing and workload races can expose intermittent kernel behavior; device-mapper setup, replay ordering, or host capabilities can dominate failures; results are sensitive to filesystem feature support and allocation alignment.

## Test Signals
The golden `.out` expects normalized signals such as: Silence is golden. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/457 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/458 -->
# sources/test-tools/xfstests/tests/generic/458

## Purpose
Regression test for xfs leftover CoW extents after truncate and umount Fixed by commit 3af423b03435 ("xfs: evict CoW fork extents when performing finsert/fcollapse"). It is registered as generic/458 with `_begin_fstest` tags `auto, quick, clone, collapse, insert, zero`, making it part of the reflink/shared extents, preallocation/range operations coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: none. Important state variables and paths include no persistent shell variables beyond harness state. Topic focus: reflink/shared extents, preallocation/range operations. Key helper behavior includes: formats a fresh scratch filesystem; mounts the scratch filesystem; requires reflink support on scratch.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; creates deterministic file layout, data, or extent state; exercises clone/dedupe shared-extent operations.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; depends on extent layout and size metadata remaining consistent.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble, common/reflink.

Prerequisite gates: _require_scratch_reflink; _require_cp_reflink; _require_xfs_io_command "fzero"; _require_xfs_io_command "fcollapse"; _require_xfs_io_command "finsert"; _require_xfs_io_command "truncate".

External/helper commands: $XFS_IO_PROG, truncate.

Representative `xfs_io` operations: pwrite 0 0x40000; fzero -k 0x169f 0x387c; fcollapse 0x29000 0xd000; finsert 0 0x8000; truncate 0x8000.

## Risks and Edge Cases
results are sensitive to filesystem feature support and allocation alignment.

## Test Signals
The golden `.out` expects normalized signals such as: Silence is golden. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/458 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/459 -->
# sources/test-tools/xfstests/tests/generic/459

## Purpose
Test buffer filesystem error recovery during a full overcommited dm-thin device. When a dm-thin device reaches its full capacity, but the virtual device still shows available space, the filesystem should be able to handle such cases failing its operation without locking up. This test has been created first to cover a XFS problem where it loops indefinitely in xfsaild due items still in AIL. The buffers containing such items couldn't be resubmitted because the items were flush locked. But, once this doesn't require any special filesystem feature to be executed, this has been integrated as a generic test. This test might hang the filesystem when ran on an unpatched kernel. It is registered as generic/459 with `_begin_fstest` tags `auto, freeze, thin`, making it part of the preallocation/range operations coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: _cleanup, is_shutdown_or_ro. Important state variables and paths include lvmsuffix=${seq}_$(hostname -s | tr '-' '_')_$$, vgname=vg_$lvmsuffix, lvname=lv_$lvmsuffix, poolname=pool_$lvmsuffix, snapname=snap_$lvmsuffix, origpsize=200, virtsize=300, newpsize=300, freezeid=$!, ret=$?. Topic focus: preallocation/range operations. Key helper behavior includes: formats a scratch filesystem with a controlled size; formats a fresh scratch filesystem.

## Control Flow
formats the scratch filesystem; creates deterministic file layout, data, or extent state; wraps repeated scenarios in local helper functions _cleanup, is_shutdown_or_ro.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem.

## Dependencies and Integration Points
Common libraries: common/preamble.

Prerequisite gates: _require_scratch_nolvm; _require_dm_target thin-pool; _require_dm_target snapshot; _require_command $LVM_PROG lvm; _require_command "$THIN_CHECK_PROG" thin_check; _require_freeze; _require_odirect.

External/helper commands: $XFS_IO_PROG, grep, mount, rm, touch.

Representative `xfs_io` operations: pwrite -b 1m 0 220m.

## Risks and Edge Cases
timing and workload races can expose intermittent kernel behavior.

## Test Signals
The golden `.out` expects normalized signals such as: Test OK. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/459 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/460 -->
# sources/test-tools/xfstests/tests/generic/460

## Purpose
Test that XFS reserves reasonable indirect blocks for delalloc and speculative allocation, and doesn't cause any fdblocks corruption. This was inspired by an XFS but that too large 'indlen' was returned by xfs_bmap_worst_indlen() which can't fit in a 17 bits value (STARTBLOCKVALBITS is defined as 17), then leaked 1 << 17 blocks in sb_fdblocks. This was only seen on XFS with rmapbt feature enabled, but nothing prevents the test from being a generic test. It is registered as generic/460 with `_begin_fstest` tags `auto, quick, rw`, making it part of the filesystem regression behavior coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: save_dirty_ratio, set_dirty_ratio, restore_dirty_ratio, _cleanup. Important state variables and paths include testfile=$SCRATCH_MNT/1G_file.$seq, file_size=$((1024 * 1024 * 1024)), saved_dirty_background_ratio=0, saved_dirty_ratio=0. Topic focus: general filesystem semantics. Key helper behavior includes: formats a fresh scratch filesystem; mounts the scratch filesystem.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; creates deterministic file layout, data, or extent state; wraps repeated scenarios in local helper functions save_dirty_ratio, set_dirty_ratio, restore_dirty_ratio, _cleanup.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble.

Prerequisite gates: _require_scratch; _require_fs_space $SCRATCH_MNT $((1024 * 1024)).

External/helper commands: $XFS_IO_PROG, rm.

## Risks and Edge Cases
failures may reflect missing helper binaries or unsupported filesystem features rather than the target regression.

## Test Signals
The golden `.out` expects normalized signals such as: Silence is golden. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/460 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/461 -->
# sources/test-tools/xfstests/tests/generic/461

## Purpose
Shutdown stress test - exercise shutdown codepath with fsstress, make sure we don't BUG/WARN. Coverage for all fs with shutdown. It is registered as generic/461 with `_begin_fstest` tags `auto, shutdown, stress`, making it part of the fsstress/replay consistency coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: none. Important state variables and paths include SLEEP_TIME=$((10 * $TIME_FACTOR)), PROCS=$((4 * LOAD_FACTOR)), load_dir=$SCRATCH_MNT/test. Topic focus: fsstress/replay consistency. Key helper behavior includes: formats a fresh scratch filesystem; mounts the scratch filesystem; unmounts the scratch filesystem; forces filesystem writeback/transaction commit; starts fsstress workload generation.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; forces durability boundaries with sync/fsync operations.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; uses sync-family calls as persistence barriers.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble.

Prerequisite gates: _require_scratch_nocheck; _require_scratch_shutdown.

## Risks and Edge Cases
failures may reflect missing helper binaries or unsupported filesystem features rather than the target regression.

## Test Signals
The golden `.out` expects normalized signals such as: Silence is golden. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/461 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/462 -->
# sources/test-tools/xfstests/tests/generic/462

## Purpose
This is a regression test for kernel commit ef947b2 x86, mm: fix gup_pte_range() vs DAX mappings created by Jeffrey Moyer <jmoyer@redhat.com> This is reproducible only when testing on pmem device which is configured in "memory mode", not in "raw mode". It is registered as generic/462 with `_begin_fstest` tags `auto, quick, dax, mmap`, making it part of the ACL/permission semantics coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: none. Important state variables and paths include md5_1=$(_md5_checksum $SCRATCH_MNT/readonlyfile), md5_2=$(_md5_checksum $SCRATCH_MNT/readonlyfile). Topic focus: ACL/permission semantics. Key helper behavior includes: formats a fresh scratch filesystem; mounts the scratch filesystem.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; creates deterministic file layout, data, or extent state.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; uses persistent files under TEST_DIR; observes inode mode, ownership, ACL, and permission state.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble.

Prerequisite gates: _require_test; _require_scratch_dax_mountopt "dax"; _require_test_program "t_mmap_write_ro"; _require_user.

External/helper commands: $XFS_IO_PROG, chmod, chown.

Representative `xfs_io` operations: pwrite -S 0xFF 0 4096; pwrite -S 0x00 0 4096.

## Risks and Edge Cases
depends on user/group identity setup and permission model details.

## Test Signals
The golden `.out` expects normalized signals such as: read: Bad address. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/462 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/463 -->
# sources/test-tools/xfstests/tests/generic/463

## Purpose
Test racy COW AIO write completions. It is registered as generic/463 with `_begin_fstest` tags `auto, quick, clone`, making it part of the reflink/shared extents coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: _cleanup. Important state variables and paths include no persistent shell variables beyond harness state. Topic focus: reflink/shared extents. The script is mostly linear and relies on xfstests common helpers for setup, filtering, and cleanup.

## Control Flow
operates in the configured test filesystem; exercises clone/dedupe shared-extent operations; wraps repeated scenarios in local helper functions _cleanup.

## State and Persistence Behavior
uses persistent files under TEST_DIR; depends on extent layout and size metadata remaining consistent.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble, common/reflink.

Prerequisite gates: _require_test; _require_test_reflink; _require_aiodio aio-dio-cow-race.

External/helper commands: rm.

## Risks and Edge Cases
results are sensitive to filesystem feature support and allocation alignment.

## Test Signals
The golden `.out` expects normalized signals such as: Silence is golden. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/463 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/464 -->
# sources/test-tools/xfstests/tests/generic/464

## Purpose
Run delalloc writes & append writes & non-data-integrity syncs concurrently to test the race between block map change vs writeback. It is registered as generic/464 with `_begin_fstest` tags `auto, rw`, making it part of the filesystem regression behavior coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: getfile, do_write, do_append, do_writeback. Important state variables and paths include MAXFILES=200, BLOCK_SZ=65536, LOOP_CNT=10, LOOP_TIME=5, PROC_CNT=16, stop=$tmp.stop. Topic focus: general filesystem semantics. Key helper behavior includes: formats a fresh scratch filesystem; mounts the scratch filesystem; unmounts the scratch filesystem.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; creates deterministic file layout, data, or extent state; wraps repeated scenarios in local helper functions getfile, do_write, do_append, do_writeback.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble.

Prerequisite gates: _require_scratch_nocheck; _require_xfs_io_command "sync_range".

External/helper commands: $XFS_IO_PROG, rm, touch.

Representative `xfs_io` operations: sync_range -w 0 0.

## Risks and Edge Cases
timing and workload races can expose intermittent kernel behavior.

## Test Signals
The golden `.out` expects normalized signals such as: Silence is golden. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/464 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/465 -->
# sources/test-tools/xfstests/tests/generic/465

## Purpose
Test i_size is updated properly under dio read/write. It is registered as generic/465 with `_begin_fstest` tags `auto, rw, quick, aio`, making it part of the filesystem regression behavior coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: _cleanup. Important state variables and paths include testfile=$TEST_DIR/$seq.$$, min_dio_align=`$here/src/min_dio_alignment $TEST_DIR $TE..., page_size=`$here/src/feature -s`, align=$min_dio_align. Topic focus: general filesystem semantics. The script is mostly linear and relies on xfstests common helpers for setup, filtering, and cleanup.

## Control Flow
operates in the configured test filesystem; creates deterministic file layout, data, or extent state; wraps repeated scenarios in local helper functions _cleanup.

## State and Persistence Behavior
uses persistent files under TEST_DIR.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble.

Prerequisite gates: _require_aiodio aio-dio-append-write-read-race; _require_test_program "feature".

External/helper commands: rm.

## Risks and Edge Cases
failures may reflect missing helper binaries or unsupported filesystem features rather than the target regression.

## Test Signals
The golden `.out` expects normalized signals such as: non-aio dio test; aio-dio test. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/465 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/466 -->
# sources/test-tools/xfstests/tests/generic/466

## Purpose
Check that high-offset reads and writes work. It is registered as generic/466 with `_begin_fstest` tags `auto, quick, rw`, making it part of the filesystem regression behavior coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: none. Important state variables and paths include devsize=$(blockdev --getsize64 $SCRATCH_DEV). Topic focus: general filesystem semantics. Key helper behavior includes: formats a scratch filesystem with a controlled size; formats a fresh scratch filesystem; mounts the scratch filesystem; forces unmount/remount persistence checks; unmounts the scratch filesystem; writes deterministic byte patterns.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; creates deterministic file layout, data, or extent state; remounts or replays after simulated failure; checks visible metadata, extent maps, hashes, or syscall output.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; explicitly validates behavior across remount, crash replay, or log replay; depends on extent layout and size metadata remaining consistent.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble.

Prerequisite gates: _require_scratch_nocheck; _require_block_device $SCRATCH_DEV.

External/helper commands: $XFS_IO_PROG, mkdir, mount, stat, truncate.

Representative `xfs_io` operations: truncate $len; pread -v -q $bigoff 1.

## Risks and Edge Cases
failures may reflect missing helper binaries or unsupported filesystem features rather than the target regression.

## Test Signals
The golden `.out` expects normalized signals such as: Silence is golden. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/466 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/467 -->
# sources/test-tools/xfstests/tests/generic/467

## Purpose
Check open by file handle. This is a variant of test generic/426 that tests with less files and more use cases: - open directory by file handle - verify content integrity of file after opening by file handle - open by file handle of unlinked open files - open by file handle of renamed files. It is registered as generic/467 with `_begin_fstest` tags `auto, quick, exportfs`, making it part of the rename/link persistence, filename/directory semantics coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: create_test_files, test_file_handles. Important state variables and paths include NUMFILES=10, testdir=$TEST_DIR/$seq-dir. Topic focus: rename/link persistence, filename/directory semantics. The script is mostly linear and relies on xfstests common helpers for setup, filtering, and cleanup.

## Control Flow
operates in the configured test filesystem; wraps repeated scenarios in local helper functions create_test_files, test_file_handles.

## State and Persistence Behavior
uses persistent files under TEST_DIR.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble.

Prerequisite gates: _require_test; _require_test_program "open_by_handle"; _require_exportfs.

External/helper commands: mkdir, mv, rm.

## Risks and Edge Cases
failures may reflect missing helper binaries or unsupported filesystem features rather than the target regression.

## Test Signals
The golden `.out` expects normalized signals such as: test_file_handles TEST_DIR/467-dir -dp; test_file_handles TEST_DIR/467-dir -rp; test_file_handles TEST_DIR/467-dir -dkr; test_file_handles TEST_DIR/467-dir -lr; test_file_handles TEST_DIR/467-dir -ur; test_file_handles TEST_DIR/467-dir -mr. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/467 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/468 -->
# sources/test-tools/xfstests/tests/generic/468

## Purpose
This testcase is a fallocate variant of generic/392, it expands to test block preallocation functionality of fallocate. In this case, we are trying to execute: 1. fallocate {,-k} 2. f{data,}sync 3. power-cuts 4. recovery filesystem during mount 5. check inode's metadata In the case of fsync, filesystem should recover all the inode metadata, while recovering i_blocks and i_size at least for fdatasync, so this testcase excepts that inode metadata will be unchanged after recovery. It is registered as generic/468 with `_begin_fstest` tags `shutdown, auto, quick, metadata, prealloc`, making it part of the crash recovery/log replay, preallocation/range operations coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: check_inode_metadata, test_falloc. Important state variables and paths include testfile=$SCRATCH_MNT/testfile. Topic focus: crash recovery/log replay, preallocation/range operations. Key helper behavior includes: formats a fresh scratch filesystem; mounts the scratch filesystem; forces unmount/remount persistence checks; requires a journal/log capable filesystem before crash replay.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; creates deterministic file layout, data, or extent state; forces durability boundaries with sync/fsync operations; remounts or replays after simulated failure; checks visible metadata, extent maps, hashes, or syscall output; wraps repeated scenarios in local helper functions check_inode_metadata, test_falloc.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; explicitly validates behavior across remount, crash replay, or log replay; uses sync-family calls as persistence barriers; depends on extent layout and size metadata remaining consistent.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble.

Prerequisite gates: _require_scratch; _require_scratch_shutdown; _require_xfs_io_command "falloc" "-k"; _require_metadata_journaling $SCRATCH_DEV.

External/helper commands: $XFS_IO_PROG, rm, stat, truncate.

Representative `xfs_io` operations: $sync_mode; truncate 4202496; pwrite 0 4202496; fsync; falloc $2 4202496 $3.

## Risks and Edge Cases
results are sensitive to filesystem feature support and allocation alignment.

## Test Signals
The golden `.out` expects normalized signals such as: ==== falloc 1024 test with fsync ====; ==== falloc 4096 test with fsync ====; ==== falloc 104857600 test with fsync ====; ==== falloc -k 1024 test with fsync ====; ==== falloc -k 4096 test with fsync ====; ==== falloc -k 104857600 test with fsync ====. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/468 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/469 -->
# sources/test-tools/xfstests/tests/generic/469

## Purpose
Test that mmap read doesn't see non-zero data past EOF on truncate down. This is inspired by an XFS bug that truncate down fails to zero page cache beyond new EOF and causes stale data written to disk unexpectedly and a subsequent mmap reads and sees non-zeros post EOF. Patch "xfs: truncate pagecache before writeback in xfs_setattr_size()" fixed the bug on XFS. It is registered as generic/469 with `_begin_fstest` tags `auto, quick, punch, zero, prealloc, mmap`, making it part of the preallocation/range operations coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: _cleanup, run_fsx, test_fsx. Important state variables and paths include file=$TEST_DIR/$seq.fsx. Topic focus: preallocation/range operations. The script is mostly linear and relies on xfstests common helpers for setup, filtering, and cleanup.

## Control Flow
operates in the configured test filesystem; creates deterministic file layout, data, or extent state; wraps repeated scenarios in local helper functions _cleanup, run_fsx, test_fsx.

## State and Persistence Behavior
uses persistent files under TEST_DIR; depends on extent layout and size metadata remaining consistent.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble.

Prerequisite gates: _require_test; _require_xfs_io_command "falloc" "-k"; _require_xfs_io_command "fpunch"; _require_xfs_io_command "fzero".

External/helper commands: $FSX_PROG, fallocate, fsx, rm, truncate.

## Risks and Edge Cases
results are sensitive to filesystem feature support and allocation alignment.

## Test Signals
The golden `.out` expects normalized signals such as: fsx --replay-ops fsxops.0; fsx -y --replay-ops fsxops.0; fsx --replay-ops fsxops.1; fsx -y --replay-ops fsxops.1; fsx --replay-ops fsxops.2; fsx -y --replay-ops fsxops.2. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/469 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/470 -->
# sources/test-tools/xfstests/tests/generic/470

## Purpose
Use dm-log-writes to verify that MAP_SYNC actually syncs metadata during page faults. It is registered as generic/470 with `_begin_fstest` tags `auto, quick, dax, mmap`, making it part of the fsstress/replay consistency coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: _cleanup. Important state variables and paths include MAPPED_LEN=$((512 * 1024 * 1024)), LEN=$((1024 * 1024)). Topic focus: fsstress/replay consistency. Key helper behavior includes: formats a fresh scratch filesystem; mounts the scratch filesystem; captures block writes for replay testing.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; initializes device-mapper or log-writes infrastructure; creates deterministic file layout, data, or extent state; wraps repeated scenarios in local helper functions _cleanup.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; depends on extent layout and size metadata remaining consistent.

## Dependencies and Integration Points
Common libraries: common/dmlogwrites, common/filter, common/preamble.

Prerequisite gates: _require_scratch; _require_no_logdev; _require_log_writes_dax_mountopt "dax"; _require_xfs_io_command "mmap" "-S"; _require_xfs_io_command "log_writes"; _require_command "$BLKDISCARD_PROG" blkdiscard.

External/helper commands: $XFS_IO_PROG, du, rm, truncate.

Representative `xfs_io` operations: truncate $LEN; mmap -S 0 $LEN; mwrite 0 $LEN; log_writes -d $LOGWRITES_NAME -m preunmap.

## Risks and Edge Cases
device-mapper setup, replay ordering, or host capabilities can dominate failures.

## Test Signals
The golden `.out` expects normalized signals such as: 1.0M SCRATCH_MNT/test. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/470 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/471 -->
# sources/test-tools/xfstests/tests/generic/471

## Purpose
Test that if names are added to a directory after an opendir(3) call and before a rewinddir(3) call, future readdir(3) calls will return the names. This is mandated by POSIX: https://pubs.opengroup.org/onlinepubs/007904875/functions/rewinddir.html. It is registered as generic/471 with `_begin_fstest` tags `auto, quick, dir`, making it part of the filename/directory semantics coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: _cleanup. Important state variables and paths include target_dir=$TEST_DIR/test-$seq. Topic focus: filename/directory semantics. The script is mostly linear and relies on xfstests common helpers for setup, filtering, and cleanup.

## Control Flow
operates in the configured test filesystem; wraps repeated scenarios in local helper functions _cleanup.

## State and Persistence Behavior
uses persistent files under TEST_DIR.

## Dependencies and Integration Points
Common libraries: common/preamble.

Prerequisite gates: _require_test; _require_test_program rewinddir-test.

Documented regression fixes: _fixed_by_fs_commit btrfs e60aa5da14d0 "btrfs: refresh dir last index during a rewinddir(3) call".

External/helper commands: mkdir, rm.

## Risks and Edge Cases
failures may reflect missing helper binaries or unsupported filesystem features rather than the target regression.

## Test Signals
The golden `.out` expects normalized signals such as: Silence is golden. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/471 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/472 -->
# sources/test-tools/xfstests/tests/generic/472

## Purpose
Test various swapfile activation oddities. It is registered as generic/472 with `_begin_fstest` tags `auto, quick, swap`, making it part of the swapfile activation coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: _cleanup, swapfile_cycle. Important state variables and paths include swapfile=$SCRATCH_MNT/swap, len=$((2 * 1048576)). Topic focus: swapfile activation. Key helper behavior includes: formats a fresh scratch filesystem; mounts the scratch filesystem; writes deterministic byte patterns.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; creates deterministic file layout, data, or extent state; checks visible metadata, extent maps, hashes, or syscall output; wraps repeated scenarios in local helper functions _cleanup, swapfile_cycle.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; persists extended-attribute namespace/value state.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble.

Prerequisite gates: _require_scratch_swapfile; _require_test_program mkswap; _require_test_program swapon.

External/helper commands: $ATTR_PROG, $CHATTR_PROG, rm, swapoff, swapon, touch.

## Risks and Edge Cases
failures may reflect missing helper binaries or unsupported filesystem features rather than the target regression.

## Test Signals
The golden `.out` expects normalized signals such as: regular swap; too long swap; tiny swap. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/472 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/473 -->
# sources/test-tools/xfstests/tests/generic/473

## Purpose
Test for the new ranged query functionality in xfs_io's fiemap command. This tests various combinations of hole + data layout being printed. Also the test used 16k holes to be compatible with 16k block filesystems. It is registered as generic/473 with `_begin_fstest` tags `broken, fiemap`, making it part of the fiemap/bmap reporting, holes/sparse files coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: none. Important state variables and paths include file=$TEST_DIR/fiemap.$seq. Topic focus: fiemap/bmap reporting, holes/sparse files. The script is mostly linear and relies on xfstests common helpers for setup, filtering, and cleanup.

## Control Flow
operates in the configured test filesystem; creates deterministic file layout, data, or extent state; checks visible metadata, extent maps, hashes, or syscall output.

## State and Persistence Behavior
uses persistent files under TEST_DIR; depends on extent layout and size metadata remaining consistent.

## Dependencies and Integration Points
Common libraries: common/preamble, common/punch.

Prerequisite gates: _require_test; _require_xfs_io_command "truncate"; _require_xfs_io_command "fiemap" "ranged".

External/helper commands: $XFS_IO_PROG, rm, truncate.

Representative `xfs_io` operations: truncate 4m; pwrite $(($i*128+64))k 64k; fiemap -v 64k 64k; fiemap -v 64k 80k; fiemap -v 0 65k; fiemap -v 0k 130k; fiemap -v 64k 192k; fiemap -v 0 3k; fiemap -v 0 3m; fiemap -v 0 5m.

## Risks and Edge Cases
results are sensitive to filesystem feature support and allocation alignment.

## Test Signals
The golden `.out` expects normalized signals such as: Basic data extent; 0: [128..255]: data; Data + Hole; 0: [128..255]: data; 1: [256..287]: hole; Hole + Data. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/473 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/474 -->
# sources/test-tools/xfstests/tests/generic/474

## Purpose
Inspired by syncfs bug of overlayfs which does not sync dirty inodes in underlying filesystem. Create a small file then run syncfs and shutdown filesystem(or underlying filesystem of overlayfs) to check syncfs result. Test will be skipped if filesystem(or underlying filesystem of overlayfs) does not support shutdown. It is registered as generic/474 with `_begin_fstest` tags `auto, quick, shutdown, metadata`, making it part of the writeback error reporting, filename/directory semantics coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: none. Important state variables and paths include localdir=$SCRATCH_MNT/dir. Topic focus: writeback error reporting, filename/directory semantics. Key helper behavior includes: formats a fresh scratch filesystem; mounts the scratch filesystem; forces unmount/remount persistence checks; forces filesystem writeback/transaction commit.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; creates deterministic file layout, data, or extent state; forces durability boundaries with sync/fsync operations; remounts or replays after simulated failure.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; explicitly validates behavior across remount, crash replay, or log replay; uses sync-family calls as persistence barriers.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble.

Prerequisite gates: _require_fssum; _require_scratch; _require_scratch_shutdown; _require_xfs_io_command "syncfs".

External/helper commands: $XFS_IO_PROG, mkdir.

Representative `xfs_io` operations: pwrite 0 4K.

## Risks and Edge Cases
failures may reflect missing helper binaries or unsupported filesystem features rather than the target regression.

## Test Signals
The golden `.out` expects normalized signals such as: OK. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/474 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/475 -->
# sources/test-tools/xfstests/tests/generic/475

## Purpose
Test log recovery with repeated (simulated) disk failures. We kick off fsstress on the scratch fs, then switch out the underlying device with dm-error to see what happens when the disk goes down. Having taken down the fs in this manner, remount it and repeat. This test is a Good Enough (tm) simulation of our internal multipath failure testing efforts. It is registered as generic/475 with `_begin_fstest` tags `shutdown, auto, log, metadata, eio, recoveryloop, smoketest`, making it part of the crash recovery/log replay, writeback error reporting, fsstress/replay consistency coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: _cleanup. Important state variables and paths include no persistent shell variables beyond harness state. Topic focus: crash recovery/log replay, writeback error reporting, fsstress/replay consistency. Key helper behavior includes: formats a fresh scratch filesystem; requires a journal/log capable filesystem before crash replay; sets up dm-error for I/O fault injection; starts fsstress workload generation.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; initializes device-mapper or log-writes infrastructure; wraps repeated scenarios in local helper functions _cleanup.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem.

## Dependencies and Integration Points
Common libraries: common/dmerror, common/preamble.

Prerequisite gates: _require_scratch; _require_dm_target error; _require_metadata_journaling $SCRATCH_DEV.

External/helper commands: mount, rm.

## Risks and Edge Cases
device-mapper setup, replay ordering, or host capabilities can dominate failures; writeback error propagation is asynchronous and must be checked at the intended boundary.

## Test Signals
The golden `.out` expects normalized signals such as: Silence is golden.. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/475 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/476 -->
# sources/test-tools/xfstests/tests/generic/476

## Purpose
Run an all-writes fsstress run with multiple threads to shake out bugs in the write path. It is registered as generic/476 with `_begin_fstest` tags `auto, rw, long_rw, stress, soak, smoketest`, making it part of the fsstress/replay consistency coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: none. Important state variables and paths include nr_cpus=$((LOAD_FACTOR * 4)), nr_ops=$((25000 * TIME_FACTOR)), fsstress_args=(-w -d $SCRATCH_MNT -n $nr_ops -p $nr_cpus). Topic focus: fsstress/replay consistency. Key helper behavior includes: formats a fresh scratch filesystem; mounts the scratch filesystem; starts fsstress workload generation.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem.

## Dependencies and Integration Points
Common libraries: common/preamble.

Prerequisite gates: _require_scratch.

## Risks and Edge Cases
failures may reflect missing helper binaries or unsupported filesystem features rather than the target regression.

## Test Signals
The golden `.out` expects normalized signals such as: Silence is golden.. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/476 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/477 -->
# sources/test-tools/xfstests/tests/generic/477

## Purpose
Check open by file handle after cycle mount. This test uses load and store of file handles from a temp file to test decoding file handles after cycle mount and after directory renames. It is registered as generic/477 with `_begin_fstest` tags `auto, quick, exportfs`, making it part of the rename/link persistence, filename/directory semantics coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: create_test_files, test_file_handles. Important state variables and paths include NUMFILES=10, testroot=$TEST_DIR/$seq-dir, testdir=$testroot/testdir. Topic focus: rename/link persistence, filename/directory semantics. The script is mostly linear and relies on xfstests common helpers for setup, filtering, and cleanup.

## Control Flow
operates in the configured test filesystem; wraps repeated scenarios in local helper functions create_test_files, test_file_handles.

## State and Persistence Behavior
uses persistent files under TEST_DIR.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble.

Prerequisite gates: _require_test; _require_test_program "open_by_handle"; _require_exportfs.

External/helper commands: mkdir, mount, mv, rm.

## Risks and Edge Cases
failures may reflect missing helper binaries or unsupported filesystem features rather than the target regression.

## Test Signals
The golden `.out` expects normalized signals such as: test_file_handles after cycle mount; test_file_handles after rename parent; test_file_handles after rename grandparent; test_file_handles after move to new parent. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/477 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/478 -->
# sources/test-tools/xfstests/tests/generic/478

## Purpose
Test OFD lock. fcntl F_OFD_SETLK to set lock, then F_OFD_GETLK to verify we are being given correct advice by kernel. OFD lock combines POSIX lock and BSD flock: + does not share between threads + byte granularity (both tested by LTP/fcntl3{4,6}) + only release automatically after all open fd closed This test target the third one and expand a little bit. The basic idea is one setlk routine setting locks via fcntl *_SETLK, followed by operations like clone, dup then close fd; another routine getlk getting locks via fcntl *_GETLK. Firstly in setlk routine process P0, place a lock L0 on an opened testfile, then + clone() a child P1 to close the fd then tell getlk to go, parent P0 wait getlk done then close fd. or + dup() fd to a newfd then close newfd then tell getlk to go, then wait getlk done then close fd. In getlk process P2, do fcntl *_GETLK with lock L1 after get notified by setlk routine. In the end, getlk routine check the returned struct flock.l_type to see if the lock mechanism works fine. When testing with clone, + CLONE_FILES set, close releases all locks; + CLONE_FILES not set, locks remain in P0; If L0 is a POSIX lock, + it is not inherited into P1 + it is released after dup & close If L0 is a OFD lock, + it is inherited into P1 + it is not released after dup & close setlk routine: * getlk routine: start * start | * | open file * open file | * | init sem * | | * | wait init sem done * wait init sem done | * | setlk L0 * | | * | |---------clone()--------| * | | | * | |(child P1) (parent P0)| * | (P2) | | * | | close fd * | | | * | | set sem0=0 * wait sem0==0 | | * | | | * getlk L1 | | * | wait sem1==0 | * set sem1=0 | | * | exit wait child * | | * check result cleanup * | | * | exit * exit We can test combainations of: + shared or exclusive lock + these locks are conflicting or not + one OFD lock and one POSIX lock + that open testfile RDONLY or RDWR + clone with CLONE_FILES or not + dup and close newfd. It is registered as generic/478 with `_begin_fstest` tags `auto, quick`, making it part of the locking semantics coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: mk_sem, rm_sem, do_test. Important state variables and paths include no persistent shell variables beyond harness state. Topic focus: locking semantics. The script is mostly linear and relies on xfstests common helpers for setup, filtering, and cleanup.

## Control Flow
operates in the configured test filesystem; creates deterministic file layout, data, or extent state; wraps repeated scenarios in local helper functions mk_sem, rm_sem, do_test.

## State and Persistence Behavior
uses persistent files under TEST_DIR.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble.

Prerequisite gates: _require_test; _require_ofd_locks.

External/helper commands: $XFS_IO_PROG, grep.

Representative `xfs_io` operations: pwrite -S 0xFF 0 4096.

## Risks and Edge Cases
timing and workload races can expose intermittent kernel behavior.

## Test Signals
The golden `.out` expects normalized signals such as: get wrlck; lock could be placed; get wrlck; get wrlck; lock could be placed; get wrlck. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/478 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/479 -->
# sources/test-tools/xfstests/tests/generic/479

## Purpose
Test that when a fsync journal/log exists, if we rename a special file (fifo, symbolic link or device), create a hard link for it with its old name and then commit the journal/log, if a power loss happens the filesystem will not fail to replay the journal/log when it is mounted the next time. It is registered as generic/479 with `_begin_fstest` tags `auto, quick, metadata, log`, making it part of the crash recovery/log replay, rename/link persistence coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: _cleanup, run_test. Important state variables and paths include no persistent shell variables beyond harness state. Topic focus: crash recovery/log replay, rename/link persistence. Key helper behavior includes: formats a fresh scratch filesystem; mounts the scratch filesystem; unmounts the scratch filesystem; forces filesystem writeback/transaction commit; requires a journal/log capable filesystem before crash replay; routes the scratch device through dm-flakey; simulates power loss and remounts for replay.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; initializes device-mapper or log-writes infrastructure; forces durability boundaries with sync/fsync operations; remounts or replays after simulated failure; wraps repeated scenarios in local helper functions _cleanup, run_test.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; explicitly validates behavior across remount, crash replay, or log replay; uses sync-family calls as persistence barriers.

## Dependencies and Integration Points
Common libraries: common/dmflakey, common/filter, common/preamble.

Prerequisite gates: _require_scratch; _require_symlinks; _require_mknod; _require_dm_target flakey; _require_metadata_journaling $SCRATCH_DEV.

External/helper commands: $XFS_IO_PROG, ln, mkdir, mkfifo, mknod, mv, rm, touch.

Representative `xfs_io` operations: fsync.

## Risks and Edge Cases
device-mapper setup, replay ordering, or host capabilities can dominate failures.

## Test Signals
The golden `.out` expects normalized signals such as: Silence is golden. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/479 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/480 -->
# sources/test-tools/xfstests/tests/generic/480

## Purpose
Test that if we have a file with two hard links in the same parent directory, then remove of the links, create a new file in the same parent directory and with the name of the link removed, fsync the new file and have a power loss, mounting the filesystem succeeds. It is registered as generic/480 with `_begin_fstest` tags `auto, quick, metadata, log`, making it part of the crash recovery/log replay, rename/link persistence coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: _cleanup. Important state variables and paths include no persistent shell variables beyond harness state. Topic focus: crash recovery/log replay, rename/link persistence. Key helper behavior includes: formats a fresh scratch filesystem; mounts the scratch filesystem; unmounts the scratch filesystem; forces filesystem writeback/transaction commit; requires a journal/log capable filesystem before crash replay; routes the scratch device through dm-flakey; simulates power loss and remounts for replay.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; initializes device-mapper or log-writes infrastructure; forces durability boundaries with sync/fsync operations; remounts or replays after simulated failure; wraps repeated scenarios in local helper functions _cleanup.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; explicitly validates behavior across remount, crash replay, or log replay; uses sync-family calls as persistence barriers.

## Dependencies and Integration Points
Common libraries: common/dmflakey, common/filter, common/preamble.

Prerequisite gates: _require_scratch; _require_hardlinks; _require_dm_target flakey; _require_metadata_journaling $SCRATCH_DEV.

External/helper commands: $XFS_IO_PROG, ln, mkdir, rm, touch.

Representative `xfs_io` operations: fsync.

## Risks and Edge Cases
device-mapper setup, replay ordering, or host capabilities can dominate failures.

## Test Signals
The golden `.out` expects normalized signals such as: Silence is golden. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/480 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/481 -->
# sources/test-tools/xfstests/tests/generic/481

## Purpose
Reproduce a regression of btrfs that leads to -EEXIST on creating new files after log replay. The kernel fix is Btrfs: fix unexpected -EEXIST when creating new inode. It is registered as generic/481 with `_begin_fstest` tags `auto, quick, log, metadata`, making it part of the crash recovery/log replay coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: _cleanup. Important state variables and paths include no persistent shell variables beyond harness state. Topic focus: crash recovery/log replay. Key helper behavior includes: formats a fresh scratch filesystem; mounts the scratch filesystem; unmounts the scratch filesystem; requires a journal/log capable filesystem before crash replay; routes the scratch device through dm-flakey; simulates power loss and remounts for replay.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; initializes device-mapper or log-writes infrastructure; forces durability boundaries with sync/fsync operations; remounts or replays after simulated failure; wraps repeated scenarios in local helper functions _cleanup.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; explicitly validates behavior across remount, crash replay, or log replay; uses sync-family calls as persistence barriers.

## Dependencies and Integration Points
Common libraries: common/dmflakey, common/filter, common/preamble.

Prerequisite gates: _require_scratch; _require_dm_target flakey; _require_metadata_journaling $SCRATCH_DEV.

External/helper commands: $XFS_IO_PROG, rm, touch.

Representative `xfs_io` operations: fsync.

## Risks and Edge Cases
device-mapper setup, replay ordering, or host capabilities can dominate failures.

## Test Signals
The golden `.out` expects normalized signals such as: Silence is golden. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/481 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/482 -->
# sources/test-tools/xfstests/tests/generic/482

## Purpose
Test filesystem consistency after each FUA operation Will do log replay and check the filesystem. It is registered as generic/482 with `_begin_fstest` tags `auto, metadata, replay, thin, recoveryloop`, making it part of the crash recovery/log replay, ENOSPC/free-space handling, fsstress/replay consistency coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: _cleanup. Important state variables and paths include nr_cpus=$("$here/src/feature" -o), fsstress_args=$(_scale_fsstress_args -w -d $SCRATCH_MNT ..., size=$(_small_fs_size_mb 200), devsize=$((1024*1024*size / 512)), csize=$((1024*64 / 512)), lowspace=$((1024*1024 / 512)), prev=$(_log_writes_mark_to_entry_number mkfs), cur=$(_log_writes_find_next_fua $prev). Topic focus: crash recovery/log replay, ENOSPC/free-space handling, fsstress/replay consistency. Key helper behavior includes: sets up dm-thin backing storage; captures block writes for replay testing; starts fsstress workload generation.

## Control Flow
mounts the target through the relevant helper layer; initializes device-mapper or log-writes infrastructure; creates deterministic file layout, data, or extent state; remounts or replays after simulated failure; wraps repeated scenarios in local helper functions _cleanup.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; explicitly validates behavior across remount, crash replay, or log replay.

## Dependencies and Integration Points
Common libraries: common/dmlogwrites, common/dmthin, common/filter, common/preamble.

Prerequisite gates: _require_no_logdev; _require_scratch_nocheck; _require_log_writes; _require_dm_target thin-pool.

External/helper commands: rm.

## Risks and Edge Cases
device-mapper setup, replay ordering, or host capabilities can dominate failures.

## Test Signals
The golden `.out` expects normalized signals such as: Silence is golden. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/482 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/483 -->
# sources/test-tools/xfstests/tests/generic/483

## Purpose
Test that fsync operations preserve extents allocated with fallocate(2) that are placed beyond a file's size. It is registered as generic/483 with `_begin_fstest` tags `auto, quick, log, metadata, fiemap, prealloc`, making it part of the crash recovery/log replay, preallocation/range operations, fiemap/bmap reporting coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: _cleanup. Important state variables and paths include no persistent shell variables beyond harness state. Topic focus: crash recovery/log replay, preallocation/range operations, fiemap/bmap reporting. Key helper behavior includes: formats a fresh scratch filesystem; mounts the scratch filesystem; unmounts the scratch filesystem; forces filesystem writeback/transaction commit; requires a journal/log capable filesystem before crash replay; routes the scratch device through dm-flakey; simulates power loss and remounts for replay.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; initializes device-mapper or log-writes infrastructure; creates deterministic file layout, data, or extent state; forces durability boundaries with sync/fsync operations; remounts or replays after simulated failure; checks visible metadata, extent maps, hashes, or syscall output; wraps repeated scenarios in local helper functions _cleanup.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; explicitly validates behavior across remount, crash replay, or log replay; uses sync-family calls as persistence barriers; depends on extent layout and size metadata remaining consistent.

## Dependencies and Integration Points
Common libraries: common/dmflakey, common/filter, common/preamble, common/punch.

Prerequisite gates: _require_scratch; _require_dm_target flakey; _require_xfs_io_command "falloc" "-k"; _require_xfs_io_command "fiemap"; _require_metadata_journaling $SCRATCH_DEV; _require_congruent_file_oplen $SCRATCH_MNT 262144.

External/helper commands: $XFS_IO_PROG, rm, stat, truncate.

Representative `xfs_io` operations: pwrite -S 0xea 0 256K; pwrite -S 0xcf $offset 4K; pwrite -S 0xf1 0 256K; falloc -k 256K 768K; fsync; falloc -k 256K 1M; truncate 256K; falloc -k 1M 2M; fiemap -v.

## Risks and Edge Cases
device-mapper setup, replay ordering, or host capabilities can dominate failures; results are sensitive to filesystem feature support and allocation alignment.

## Test Signals
The golden `.out` expects normalized signals such as: File foo fiemap:; 0: [0..2559]: extent; File foo size:; 262144; File bar fiemap:; 0: [0..2559]: extent. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/483 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/484 -->
# sources/test-tools/xfstests/tests/generic/484

## Purpose
Open a file and write to it and fsync. Then, flip the data device to throw errors, write to it again and do an fdatasync. Then open an O_RDONLY fd on the same file and call syncfs against it and ensure that an error is reported. Then call syncfs again and ensure that no error is reported. Finally, repeat the open and syncfs and ensure that there is no error reported. Kernel with the following patches should pass the test: vfs: track per-sb writeback errors and report them to syncfs buffer: record blockdev write errors in super_block that it backs. It is registered as generic/484 with `_begin_fstest` tags `auto, quick, eio`, making it part of the writeback error reporting coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: _cleanup. Important state variables and paths include testfile=$SCRATCH_MNT/syncfs-reports-errors, datalen=$(getconf PAGE_SIZE). Topic focus: writeback error reporting. Key helper behavior includes: formats a fresh scratch filesystem; sets up dm-error for I/O fault injection.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; initializes device-mapper or log-writes infrastructure; creates deterministic file layout, data, or extent state; forces durability boundaries with sync/fsync operations; wraps repeated scenarios in local helper functions _cleanup.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; uses sync-family calls as persistence barriers.

## Dependencies and Integration Points
Common libraries: common/dmerror, common/filter, common/preamble.

Prerequisite gates: _require_scratch_nocheck; _require_dm_target error; _require_xfs_io_command "syncfs".

External/helper commands: $XFS_IO_PROG, mount, rm, touch.

Representative `xfs_io` operations: pwrite -W -q 0 $datalen; pwrite -w -q 0 $datalen.

## Risks and Edge Cases
device-mapper setup, replay ordering, or host capabilities can dominate failures; writeback error propagation is asynchronous and must be checked at the intended boundary.

## Test Signals
The golden `.out` expects normalized signals such as: Format and mount; fdatasync: Input/output error; One of the following syncfs calls should fail with EIO:; syncfs: Input/output error; done; This syncfs call should succeed:. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/484 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/485 -->
# sources/test-tools/xfstests/tests/generic/485

## Purpose
Regression test for: 349fa7d6e193 ("ext4: prevent right-shifting extents beyond EXT_MAX_BLOCKS") 7d83fb14258b ("xfs: prevent creating negative-sized file via INSERT_RANGE"). It is registered as generic/485 with `_begin_fstest` tags `auto, quick, insert, prealloc`, making it part of the preallocation/range operations coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: _cleanup. Important state variables and paths include block_size=$(_get_file_block_size $TEST_DIR), max_file_size=$(_get_max_file_size $TEST_DIR), max_blocks=$((max_file_size / block_size)), testfile=$TEST_DIR/testfile.$seq. Topic focus: preallocation/range operations. The script is mostly linear and relies on xfstests common helpers for setup, filtering, and cleanup.

## Control Flow
operates in the configured test filesystem; creates deterministic file layout, data, or extent state; wraps repeated scenarios in local helper functions _cleanup.

## State and Persistence Behavior
uses persistent files under TEST_DIR; depends on extent layout and size metadata remaining consistent.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble.

Prerequisite gates: _require_test; _require_math; _require_xfs_io_command "falloc" "-k"; _require_xfs_io_command "finsert"; _require_xfs_io_command "truncate".

External/helper commands: $XFS_IO_PROG, rm, truncate.

Representative `xfs_io` operations: falloc 0 $((2 * block_size)); falloc -k $(( (max_blocks - 1) * $block_size )) $block_size; finsert 0 $((2 * block_size)); falloc $(( (max_blocks - 1) * $block_size )) $block_size.

## Risks and Edge Cases
results are sensitive to filesystem feature support and allocation alignment.

## Test Signals
The golden `.out` expects normalized signals such as: # With KEEP_SIZE; # Without KEEP_SIZE; fallocate: File too large. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/485 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/486 -->
# sources/test-tools/xfstests/tests/generic/486

## Purpose
Ensure that we can XATTR_REPLACE a tiny attr into a large attr. Kanda Motohiro <kanda.motohiro@gmail.com> reports that XATTR_REPLACE'ing a single-byte attr with a 2048-byte attr causes a fs shutdown because we remove the shortform attr, convert the attr fork to long format, and then try to re-add the attr having not cleared ATTR_REPLACE. Commit 7b38460dc8e4 ("xfs: don't fail when converting shortform attr to long form during ATTR_REPLACE") fixed the xfs bug. It is registered as generic/486 with `_begin_fstest` tags `auto, quick, attr`, making it part of the extended attributes coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: _cleanup, filter_attr_output. Important state variables and paths include max_attr_size=65536. Topic focus: extended attributes. Key helper behavior includes: formats a fresh scratch filesystem; mounts the scratch filesystem.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; checks visible metadata, extent maps, hashes, or syscall output; wraps repeated scenarios in local helper functions _cleanup, filter_attr_output.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; persists extended-attribute namespace/value state.

## Dependencies and Integration Points
Common libraries: common/attr, common/filter, common/preamble.

Prerequisite gates: _require_test_program "attr_replace_test"; _require_attrs; _require_scratch.

External/helper commands: $ATTR_PROG, attr, grep, rm, sed.

## Risks and Edge Cases
failures may reflect missing helper binaries or unsupported filesystem features rather than the target regression.

## Test Signals
The golden `.out` expects normalized signals such as: Attribute "world" has a NNNN byte value for SCRATCH_MNT/hello. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/generic/486 -->
