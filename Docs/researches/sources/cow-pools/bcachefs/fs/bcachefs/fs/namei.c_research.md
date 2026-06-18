# File Research: sources/cow-pools/bcachefs/fs/bcachefs/fs/namei.c

This file implements core namespace mutation transactions and several namespace fsck/path helpers.

Main transaction operations:
- `bch2_create_trans()` creates regular inodes, tmpfiles, subvolumes, and snapshots. It initializes inode metadata, creates subvolume records when requested, applies ACLs, creates dirents, updates parent link counts/timestamps, propagates casefold state, and writes the new inode in the proper snapshot.
- `bch2_link_trans()` creates a hardlink within the same subvolume, increments nlink, checks inherited attribute compatibility, creates the new dirent, updates backpointer fields, and writes both directory and target inode.
- `bch2_unlink_trans()` validates the VFS-provided target against the dirent, checks empty directories, handles subvolume unlink/removal semantics, decrements nlink when appropriate, clears matching inode backpointers, deletes the hash entry, and updates both inodes.
- `bch2_rename_trans()` performs rename, exchange, and overwrite. It updates dirent hashes, inode backpointers, subvolume parents, inherited attributes, directory depths, nlink accounting, timestamps, and overwritten target nlink.

Subvolume and inheritance behavior:
- `parent_inum()` resolves the logical parent, using `bi_parent_subvol` when crossing subvolume roots.
- `is_subdir_for_nlink()` excludes subvolume roots from normal directory nlink increments.
- `bch2_reinherit_attrs()` copies inherited inode options from a new parent unless explicitly set; directory casefold changes can reject cross-directory moves with `-EXDEV`.

Path reconstruction:
- Reverse-print helpers build paths from inode backpointers.
- `bch2_inum_to_path_reversed()` walks inode `bi_dir`/`bi_dir_offset` backpointers, follows parent subvolume snapshots, detects loops, and emits disconnected markers unless `INUM_TO_PATH_FAIL_ON_ERR` is set.
- Public wrappers include `bch2_inum_to_path()`, `bch2_inum_to_path_in_subvol()`, and `bch2_inum_snapshot_to_path()`.

Fsck helpers:
- `bch2_check_dirent_inode_dirent()` verifies target inode backpointers, repairs missing/wrong backpointers, handles unlinked inodes with dirents, and flags multiple links to directories/subvolumes.
- `__bch2_check_dirent_target()` repairs dirent `d_type` and target encoding when inconsistent with the inode.
- Casefold propagation helpers maintain `BCH_INODE_has_case_insensitive` on casefolded directories and ancestors.

Important invariants:
- Directory entries, inode backpointers, nlink counts, timestamps, and subvolume parent metadata are updated together inside btree transactions.
- Cross-subvolume moves are rejected except for subvolume-root cases explicitly handled.
- Directory casefold state is propagated up the tree for overlayfs expectations.
