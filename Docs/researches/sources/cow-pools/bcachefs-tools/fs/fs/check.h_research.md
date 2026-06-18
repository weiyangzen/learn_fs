# File Research: sources/cow-pools/bcachefs-tools/fs/fs/check.h

## Purpose

Declares fsck/check pass APIs and shared data structures for snapshot-aware metadata walking.

## Main Interfaces

- `struct snapshots_seen`: current position plus snapshot ID list for overwrites.
- `struct inode_walker_entry`: unpacked inode/whiteout plus accumulated counts.
- `struct inode_walker`: cached inode versions/deletes for one inode number.
- RAII classes for snapshots and inode walkers.
- Shared helper declarations for snapshot visibility, inode walking, reattach, backpointer updates, key-has-inode validation, all check passes, fsck error-code translation, and fsck ioctls.

## Notes

The header exposes exactly the shared machinery needed by `check.c`, `check_extents.c`, `check_dir_structure.c`, and `check_nlinks.c`.
