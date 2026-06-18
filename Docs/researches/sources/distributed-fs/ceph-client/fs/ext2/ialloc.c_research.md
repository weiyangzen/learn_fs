# sources/distributed-fs/ceph-client/fs/ext2/ialloc.c

Purpose: Implements ext2 inode bitmap allocation/freeing, directory-placement policies, inode counter maintenance, and free-inode/free-directory counting.

Important APIs/types/functions: Public functions are `ext2_new_inode`, `ext2_free_inode`, `ext2_count_free_inodes`, and `ext2_count_dirs`. Internal helpers are `read_inode_bitmap`, `ext2_release_inode`, `ext2_preread_inode`, `find_group_dir`, `find_group_orlov`, and `find_group_other`.

Control flow: New inode allocation chooses a block group: directories use old allocator or Orlov allocator; non-directories prefer parent group, then quadratic probing, then linear search. It scans inode bitmaps with atomic set-bit operations, handles races by retrying groups, updates bitmap and group descriptor counters, initializes ownership, timestamps, inherited flags, generation, inode state, quota, ACL, and security xattrs, then returns a locked new inode. Freeing validates the inode number, frees quota first, clears the inode bitmap bit, updates group/percpu counters, dirties/syncs the bitmap, and releases buffers.

State and persistence behavior: Persistent state includes inode bitmaps and group descriptor free-inode/used-directory counts. In-memory state includes percpu counters, `s_debts` for Orlov placement, inode generation counter, and newly allocated `ext2_inode_info` fields. `ext2_preread_inode` asynchronously reads the inode table block expected to be written soon.

Dependencies and integration points: Used by `namei.c` create/link/mkdir/mknod/symlink/tmpfile flows and by `inode.c` eviction/freeing. Depends on blockgroup locks, quota, xattrs, ACL initialization, security xattrs, random starting group for top-level directories, and superblock geometry.

Risks: Bitmap/counter mismatch can leak or double-allocate inode numbers. Failure after bitmap allocation but before inode insertion relies on VFS discard paths; quota/ACL/security failures must drop quota and discard the inode. Orlov uses approximate counters, so allocation must tolerate stale group choices. Reserved inode bounds are enforced after bitmap selection.

Test signals: Massive file and directory creation under concurrency; oldalloc vs Orlov placement; quota failures; ACL/security initialization failures; reserved inode/corrupt bitmap images; free-inode counter verification; synchronous mount bitmap writes.
