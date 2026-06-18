# File Research: sources/cow-pools/bcachefs/fs/bcachefs/fs/namei.h

This header exposes namespace transaction helpers and inline consistency checks.

Key elements:
- Creation flags:
  - `BCH_CREATE_TMPFILE`
  - `BCH_CREATE_SUBVOL`
  - `BCH_CREATE_SNAPSHOT`
  - `BCH_CREATE_SNAPSHOT_RO`
- Declares transaction entry points for create, link, unlink, rename, inherited attribute repair, path reconstruction, dirent-target checks, and casefold propagation.
- `dirent_points_to_inode_nowarn()` verifies that a dirent target matches an inode, handling both subvolume dirents and normal inode dirents.
- `inode_points_to_dirent()` checks inode backpointer fields against a dirent key position.
- `bch2_check_dirent_target()` fast-paths valid dirents and calls `__bch2_check_dirent_target()` only when backpointer or `d_type` mismatches are detected.

Role:
- Used by VFS operations, fsck, dirent checking, and error reporting code that needs inode-to-path translation.
