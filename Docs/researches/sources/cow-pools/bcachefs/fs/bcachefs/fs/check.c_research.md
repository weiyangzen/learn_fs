# File Research: sources/cow-pools/bcachefs/fs/bcachefs/fs/check.c

Implements the central bcachefs fsck logic for inode, dirent, xattr, root, subvolume, snapshot-visibility, backpointer, reflink migration, and online/offline fsck ioctl handling.

Key entry points:
- `bch2_check_inodes()` validates inode records, snapshot hash info, dirent backpointers, unlinked state, child-snapshot flags, subvolume links, and journal sequence bounds.
- `bch2_check_unreachable_inodes()` reattaches reachable-but-disconnected inodes to `lost+found`.
- `bch2_check_dirents()` validates dirents, hash-table placement, target inode/subvolume links, directory subdir counts, and overwritten snapshot targets.
- `bch2_check_xattrs()` validates xattr hash placement and inode ownership.
- `bch2_check_key_has_inode()` is shared by extents/dirents/xattrs to ensure a key belongs to an existing inode of the right mode, reconstructing or deleting when repair policy allows.
- `bch2_check_root()` recreates missing root subvolume/root directory metadata.
- `bch2_fix_reflink_p()` migrates old reflink pointer padding fields for pre-fix metadata versions.
- `bch2_fs_fsck_errcode()` translates fixed/unfixed/fatal filesystem flags into fsck command return bits.
- `bch2_ioctl_fsck_offline()` and `bch2_ioctl_fsck_online()` run fsck through `thread_with_stdio`.

Core mechanics:
- `snapshots_seen` tracks snapshot IDs already seen at a btree position so visibility through snapshot ancestry can be evaluated.
- `inode_walker` caches all inode versions/whiteouts for an inode number and supports cross-pass checking by extents, dirents, and xattrs.
- Missing `lost+found` directories are created in the root snapshot of a snapshot tree before reattaching inodes.
- `bch2_reattach_inode()` creates a lost+found dirent, updates inode backpointers, adjusts lost+found nlink, fixes subvolume parent metadata, and handles child snapshots with backpointer updates or whiteouts.
- Missing inodes may be reconstructed from extents, dirents, or xattrs, with mode inferred from the btree and size inferred from extent end.
- Missing subvolume records may be reconstructed when the subvolume btree lost data and a leaf snapshot/root inode context exists.
- Dirent checks distinguish normal inode targets from `DT_SUBVOL` targets, repairing parent subvolumes and subvolume root backpointers separately.
- Online fsck restricts recovery passes to those marked online-capable and temporarily switches fsck options/stdout state under the recovery run lock.

Important invariants:
- Snapshot visibility is ancestry-based and also considers overwrites already seen at the same logical position.
- Keys in extents/dirents/xattrs must have matching inode versions in the same snapshot or a valid visible ancestor, otherwise the checker repairs by writing missing versions, reconstructing, or deleting.
- Subvolume root handling is special because older versions of renamed subvolume roots may intentionally lack valid dirents.
- Unlinked inodes are not always deleted offline; they may be preserved on the deleted list until logged operations resume.
- Repair commits often deliberately return transaction restart errors to force callers to rescan after structural changes.
- `lost+found` is created in one transaction because creation can force restart behavior.

Filesystem relevance:
- This is the fsck coordination layer for bcachefs namespace and inode consistency. It ties together inodes, dirents, xattrs, subvolumes, snapshots, and repair policy.

Notable risks:
- Online fsck is explicitly racy with some concurrent namespace operations, including hardlink removal comments.
- Some repairs are unimplemented for interior snapshot subvolume reconstruction or missing subvolume roots.
- Wrong inode mode with both extents and dirents is treated as unrecoverable.
- Stdio and option state are temporarily installed on the live filesystem during online fsck and must be restored on exit.
