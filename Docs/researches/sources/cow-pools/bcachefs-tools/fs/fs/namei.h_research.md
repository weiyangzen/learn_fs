# File Research: sources/cow-pools/bcachefs-tools/fs/fs/namei.h

## Purpose
Public declarations and small inline consistency helpers for bcachefs namespace operations.

## Main Contents
- Create flags for tmpfile, subvolume, snapshot, and read-only snapshot creation.
- Transactional operation declarations: `bch2_create_trans()`, `bch2_link_trans()`, `bch2_unlink_trans()`, and `bch2_rename_trans()`.
- Inherited attribute helper declaration `bch2_reinherit_attrs()`.
- Inode-to-path conversion declarations, including subvolume-bounded and snapshot-specific variants.
- Dirent target consistency helpers:
  - `dirent_points_to_inode_nowarn()` checks whether a dirent target matches an unpacked inode, including subvolume dirents.
  - `inode_points_to_dirent()` checks inode backpointer fields against a dirent position.
  - `bch2_check_dirent_target()` fast-paths matching type/backpointer and calls the full repair/check implementation otherwise.
- Casefold ancestry declarations.

## Integration Notes
VFS operation code, recovery, and fsck code call these transaction-level helpers rather than manipulating dirents/inodes directly. The inline dirent checks encode the expected relationship between `DT_SUBVOL`, child subvolume ids, ordinary inode numbers, inode `d_type`, and inode backpointer fields.

## Risks and Edge Cases
- `dirent_points_to_inode_nowarn()` returns a bcachefs typed ENOENT if a dirent and inode disagree; callers that use it during fsck should decide whether mismatch is repairable.
- The inline fast path in `bch2_check_dirent_target()` assumes both backpointer and `d_type` match; all other cases go through the heavier implementation in `namei.c`.
