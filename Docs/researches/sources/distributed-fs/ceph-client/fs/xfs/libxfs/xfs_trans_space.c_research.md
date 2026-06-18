# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_trans_space.c

Purpose: Computes filesystem block reservations for namespace operations, factoring directory edits, inode allocation, symlink target blocks, and optional parent pointer attributes.

Important APIs, types, and functions: Exports `xfs_parent_calc_space_res`, `xfs_create_space_res`, `xfs_mkdir_space_res`, `xfs_link_space_res`, `xfs_symlink_space_res`, `xfs_remove_space_res`, and `xfs_rename_space_res`.

Control flow: Each helper sums lower-level reservation macros from `xfs_trans_space.h`. Create and mkdir include inode allocation plus directory entry insertion. Link includes directory entry insertion. Symlink includes inode allocation, directory insertion, and remote symlink blocks. Remove includes directory removal. Rename includes removal plus target insertion and conditionally extra parent pointer work for whiteouts, target replacement, and source/destination parent updates.

State and persistence: No state is stored. Returned block counts reserve data-device metadata space so transactions can allocate directory, bmap, attr, and inode metadata blocks safely.

Dependencies and integration points: Used by high-level create/link/symlink/remove/rename transaction setup. Depends on directory/attribute reservation macros, bmap split costs, inode allocation geometry, and `xfs_has_parent`.

Risks and test signals: Risks include underestimating parent-pointer attr space, rename target/whiteout combinations, and mismatches with log reservations. Test create/mkdir/link/symlink/remove/rename with parent pointers on/off, long names, whiteouts, target replacement, ENOSPC injection, and directory btree split cases.
