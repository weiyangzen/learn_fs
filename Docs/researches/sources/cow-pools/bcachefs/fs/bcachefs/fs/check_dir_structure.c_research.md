# File Research: sources/cow-pools/bcachefs/fs/bcachefs/fs/check_dir_structure.c

Implements fsck passes for subvolume path structure and directory loop/depth validation.

Key entry points:
- `bch2_check_subvolume_structure()` walks the subvolumes btree and validates parent path chains.
- `bch2_check_directory_structure()` walks directory inodes and checks parent-backpointer chains for loops.
- `check_subvol_path()` detects subvolume parent loops or unreachable parent subvolume links and reattaches broken subvolumes.
- `check_path_loop()` follows inode dirent backpointers toward a subvolume/root, detects loops, repairs by removing bad backpointers and reattaching, and renumbers `bi_depth` where needed.

Core mechanics:
- Subvolume path checking follows `fs_path_parent` through the subvolume btree until `BCACHEFS_ROOT_SUBVOL`.
- Directory loop checking follows each directory inode’s `bi_dir`/`bi_dir_offset` dirent backpointer and parent inode chain.
- `remove_backpointer()` verifies the dirent points back to the inode, removes the dirent, and clears namespace attachment before reattachment.
- `bch2_bi_depth_renumber()` walks the remembered path in reverse and updates directory `bi_depth` to maintain increasing depth from root.

Important invariants:
- Subvolume parent chains must terminate at the root subvolume without cycles.
- Directory parent chains must not loop and must converge to a subvolume root or a valid root path.
- `bi_depth` should be monotonic along parent chains; bad depths are repaired after traversal.
- Full fsck assumes earlier dirent checks already fixed missing or bad dirent backpointers.

Filesystem relevance:
- Protects namespace tree topology: directories and subvolumes must form an acyclic reachable hierarchy for path lookup and fsck repair to be meaningful.
