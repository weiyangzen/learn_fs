# sources/distributed-fs/ceph-client/fs/jffs2/jffs2_fs_i.h

## Purpose
`jffs2_fs_i.h` defines `struct jffs2_inode_info`, the per-inode private state embedded in each VFS inode. It is the central in-core representation for JFFS2 file data layout, directory entries, metadata nodes, symlink targets, inode-cache linkage, and compression preference.

## Important APIs, Types, And Functions
The header defines one type: `struct jffs2_inode_info`. Key fields are `sem`, `highest_version`, `fragtree`, `metadata`, `dents`, `target`, `inocache`, `flags`, `usercompr`, and embedded `vfs_inode`.

## Control Flow
The structure is initialized by `jffs2_init_inode_info()` and populated by `jffs2_do_read_inode()` or `jffs2_new_inode()`. File reads traverse `fragtree`; writes and GC insert or replace fragments; directory operations scan and update `dents`; setattr and GC replace `metadata`; symlink creation and iget set `target`/`i_link`.

## State And Persistence Behavior
This is volatile state reconstructed from raw flash nodes. `highest_version` guides new node versions that become persistent, `fragtree` maps logical file offsets to raw nodes, `metadata` carries non-data or special-file nodes, and `usercompr` can influence future node compression metadata.

## Dependencies And Integration Points
It depends on rbtree, POSIX ACL, mutex, and VFS inode definitions. It is included by compression, nodelist, read/write, dir, fs, GC, and debug code.

## Risks And Test Signals
The private `sem` exists because using only `inode->i_rwsem` would deadlock with GC. Incorrect lock ordering or stale fragment/metadata pointers can corrupt reads and GC. Tests should cover concurrent read/write/GC on the same inode, clear/evict while refs remain, symlink target lifetime, directory dent replacement, and version monotonicity after remount.
