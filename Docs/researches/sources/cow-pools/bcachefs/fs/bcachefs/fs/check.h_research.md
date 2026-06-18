# File Research: sources/cow-pools/bcachefs/fs/bcachefs/fs/check.h

Declares fsck shared state types and public checker/repair APIs.

Key elements:
- `struct snapshots_seen` stores the current btree position and a list of snapshot IDs observed there.
- `struct inode_walker_entry` stores an unpacked inode or whiteout plus accumulated counts.
- `struct inode_walker` tracks inode versions, delete snapshots, current inode position, and whether aggregate counts need recalculation.
- RAII-style `DEFINE_CLASS` helpers clean up dynamic arrays for `snapshots_seen` and `inode_walker`.
- Declares snapshot visibility helpers, inode walking, mismatch text formatting, inode reattachment, backpointer update, key-has-inode checking, fsck passes, reflink fixup, fsck errcode conversion, and online/offline fsck ioctl handlers.

Filesystem relevance:
- This header is the shared contract between fsck passes in `check.c`, `check_extents.c`, `check_dir_structure.c`, and `check_nlinks.c`.
