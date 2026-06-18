# File Research: sources/cow-pools/bcachefs/fs/bcachefs/fs/check_nlinks.c

Implements fsck reconciliation of hardlink counts for non-directory inodes.

Key entry point:
- `bch2_check_nlinks()` iteratively builds a table of candidate hardlinked inodes, counts dirent references, and updates inode nlink values.

Core mechanics:
- `check_nlinks_find_hardlinks()` scans inode records and records non-directory inodes with stored `bi_nlink` values.
- `check_nlinks_walk_dirents()` scans all dirents, using snapshot visibility to increment target link counts for non-directory/non-subvolume dirents.
- `check_nlinks_update_hardlinks()` walks matching inode ranges and calls `check_nlinks_update_inode()` to repair wrong nlink counts.
- The nlink table is dynamically grown with `kvmalloc_array()` and sorted/searched by inode number.
- The pass processes ranges so memory allocation failure can cap the current range and resume later.

Important invariants:
- Directories are excluded because directory backpointer and subdir count checks cover them.
- Snapshot visibility determines whether a dirent contributes to a given inode version.
- `bch2_inode_nlink_get()` / set semantics include bcachefs’s directory/non-directory bias and unlinked flag behavior.

Filesystem relevance:
- Keeps inode hardlink counts consistent with the dirent graph, affecting link/unlink correctness and deletion eligibility.
