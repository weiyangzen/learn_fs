# File Research: sources/cow-pools/bcachefs-tools/fs/fs/namei.c

## Purpose
Implements bcachefs transactional namespace operations and related fsck/path helpers: create, link, unlink, rename, path reconstruction from inode backpointers, dirent target repair, inherited option propagation, and casefold ancestry tracking.

## Main Contents
- Helper functions `parent_inum()` and `is_subdir_for_nlink()` for subvolume-aware parent lookup and directory link accounting.
- `bch2_create_trans()`, which creates regular inodes, tmpfiles, subvolumes, and snapshots. It validates subvolume writability, initializes/allocates new inodes or snapshots an existing subvolume root, creates child subvolumes when requested, applies ACLs, creates dirents, updates parent nlink/ctime/mtime, records inode backpointers, sets directory depth, propagates casefold flags, and writes the final inode in the child snapshot.
- `bch2_link_trans()`, which hard-links within a subvolume, increments nlink, validates inherited attrs, creates the new dirent, updates backpointer fields, and writes both directory and target inode.
- `bch2_unlink_trans()`, which resolves the dirent under the right snapshot, verifies VFS-provided target identity, checks directory emptiness, handles subvolume unlinking, decrements nlink for ordinary files, clears matching backpointers, removes the dirent with hash whiteout semantics, and updates times/nlink.
- `bch2_reinherit_attrs()`, which copies inheritable inode options from a source directory to a destination inode unless explicitly set on the destination.
- `bch2_rename_trans()`, which performs dirent rename/exchange/overwrite, handles subvolume parent updates, cross-subvolume restrictions, backpointer rewrites, inherited-option changes, directory nlink/depth changes, destination unlink semantics, ctime/mtime updates, and casefold propagation after cross-directory movement.
- `bch2_inum_to_path*()` helpers, which reconstruct paths by walking inode backpointers and printing components in reverse before flipping the print buffer.
- Fsck helpers for dirent-to-inode consistency: `bch2_check_dirent_inode_dirent()` and `__bch2_check_dirent_target()`.
- Casefold ancestry helpers: `bch2_maybe_propagate_has_case_insensitive()` and `bch2_check_inode_has_case_insensitive()`.

## Integration Notes
This file sits on top of `inode.h`, `dirent.h`, `str_hash.h`, `xattr.h`, ACL handling, and subvolume/snapshot APIs. It performs all metadata changes inside `btree_trans` transactions. Dirent creation/lookup/delete uses hash info derived from the parent inode, so namespace correctness depends on stable inode hash seed/type/casefold state across snapshots. Subvolume roots are represented as directory-looking inodes with special `DT_SUBVOL` dirents and `bi_subvol`/`bi_parent_subvol` fields.

## Risks and Edge Cases
- Cross-subvolume rename is allowed only for subvolume roots; ordinary inodes cannot move across subvolumes.
- Reinheritance failures for directories return `-EXDEV` because moving a directory into a parent with different inherited options would require recursively updating descendants.
- Path reconstruction depends on inode backpointers and gracefully emits disconnected markers unless `INUM_TO_PATH_FAIL_ON_ERR` is set.
- Fsck repair can update inode backpointers, remove duplicate directory links, or rewrite wrong dirent `d_type`; callers must be prepared for transaction restarts.
