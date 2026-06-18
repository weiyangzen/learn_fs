# sources/distributed-fs/ceph-client/fs/qnx4/qnx4.h

## Purpose
`qnx4.h` provides private QNX4 filesystem structures, helpers, operation declarations, and directory-entry interpretation.

## Important APIs, types, and functions
It defines `struct qnx4_sb_info`, `struct qnx4_inode_info`, `union qnx4_directory_entry`, inline accessors `qnx4_sb`, `qnx4_i`, `qnx4_raw_inode`, and `get_entry_fname`.

## Control flow
`get_entry_fname` validates the status byte, handles used versus link entries, picks the correct maximum name size, and returns a length-limited name pointer for lookup and readdir.

## State and persistence
The header describes per-superblock and per-inode runtime state, including a copied raw inode and bitmap inode pointer. It has no storage effects itself.

## Dependencies and integration points
It depends on VFS types and `linux/qnx4_fs.h`, and is shared by inode, dir, namei, and bitmap code.

## Risks and test signals
Risks include assumptions about union field layout, status-bit interpretation, name truncation, and stale debug macros. Test signals include compile-time `BUILD_BUG_ON` layout checks, direct/link entries, empty entries, and max-size names.
