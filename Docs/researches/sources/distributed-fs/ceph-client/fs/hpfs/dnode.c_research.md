# sources/distributed-fs/ceph-client/fs/hpfs/dnode.c

Purpose: this file maintains HPFS directory dnode B-trees. It inserts, removes, searches, balances, counts, and maps directory entries while preserving active readdir positions.

Important APIs and functions: `hpfs_add_pos()`/`hpfs_del_pos()` track live directory offsets. `hpfs_add_de()` inserts a dirent into one dnode. `hpfs_add_dirent()` descends the dnode tree and inserts, calling `hpfs_add_to_dnode()` for split handling. `hpfs_remove_dirent()` deletes entries and rebalances through `move_to_top()` and `delete_empty_dnode()`. `map_pos_dirent()`, `map_dirent()`, and `map_fnode_dirent()` locate entries by encoded position, name, or fnode. `hpfs_count_dnodes()` and `hpfs_remove_dtree()` traverse directory trees.

Control flow: insertion descends by case-folded name order. If the target dnode has space, it inserts in-place and adjusts tracked positions. If full, it builds a temporary oversized dnode, splits entries around the midpoint into a new dnode, promotes a separator upward, and creates a new root when needed. Removal deletes the target dirent, pulls a replacement from a subtree if necessary, deletes empty dnodes, and updates parent/down pointers. Search and readdir mapping walk down/up through dnode pointers and sentinel entries.

State and persistence: dnode contents, parent pointers, root flags, fnode root-dnode pointers, directory inode size/blocks, and bitmap allocation are mutated. Active `f_pos` pointers stored in `hpfs_inode_info->i_rddir_off` are updated to keep directory streams coherent across changes.

Dependencies and integration: it depends on allocation, quad-buffer mapping, name comparison, fnode mapping, and strict corruption checks. `dir.c` uses mapping functions; `namei.c` uses add/remove; `inode.c` uses count and map-by-fnode when writing metadata.

Risks: this is one of the highest-risk HPFS areas. Mid-split ENOSPC can corrupt trees, so callers preflight with `hpfs_check_free_dnodes()`. Pointer and position substitutions use magic temporary positions `4` and `5`; mistakes can break readdir. Balancing code handles obscure dnode shapes and logs but may proceed on unbalanced trees.

Test signals: insert until dnode splits, split root and non-root dnodes, delete leaf/internal entries, delete empty directories with nested empty dnodes, rename while readdir is active, strict-check bad up/down pointers, map by fnode with long truncated names, and fsck validation after create/delete storms.
