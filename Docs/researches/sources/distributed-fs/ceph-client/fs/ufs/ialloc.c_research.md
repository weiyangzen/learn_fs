# sources/distributed-fs/ceph-client/fs/ufs/ialloc.c

## Purpose
`ialloc.c` implements UFS inode allocation and freeing, including inode bitmap updates, cylinder group/free summary counters, UFS2 lazy inode chunk initialization, and new in-core inode initialization.

## Important APIs, types, and functions
Public functions are `ufs_free_inode` and `ufs_new_inode`; internal `ufs2_init_inodes_chunk` zeroes newly initialized UFS2 inode blocks and advances `cg_initediblk`.

## Control flow
Freeing locks `s_lock`, validates inode range, loads the containing cylinder group, verifies bitmap state, clears the inode-used bit, updates free inode and directory counters, writes rotors/summaries dirty, and optionally syncs. Allocation rejects deleted parent directories, allocates a VFS inode, then searches the parent cylinder group, quadratic fallback groups, and linear fallback groups for free inodes. It sets the bitmap bit, initializes UFS2 inode disk chunks when the chosen bit is beyond initialized inode blocks, updates counters, assigns inode number, owner, timestamps, flags, and UFS private fields, inserts the inode into the hash, marks it dirty, and for UFS2 writes birthtime directly to disk.

## State and persistence
Persistent state includes inode-used bitmaps, cylinder group counters, superblock summary totals, UFS2 initialized inode block marker, birthtime fields, and new inode records on writeback. Runtime state includes newly allocated `struct inode` and `ufs_inode_info`.

## Dependencies and integration points
It depends on `ufs_load_cylinder`, bitmap helpers, endian helpers, `insert_inode_locked`, `inode_init_owner`, and `ufs_mark_sb_dirty`. `namei.c` calls `ufs_new_inode`; `ufs_evict_inode` calls `ufs_free_inode`.

## Risks and test signals
Risks include alias races if free ordering changes, counter drift on failure after bitmap set, UFS2 chunk zeroing errors, directory counter mismatches, and inode range boundary mistakes. Test signals include create/unlink stress, directory creation/removal, allocation after deleted parent, UFS2 new inode birthtime, ENOSPC on inode exhaustion, and fsck validation of inode bitmaps/counters.
