# sources/distributed-fs/ceph-client/fs/ocfs2/sysfile.c

Purpose: resolves and caches OCFS2 system file inodes, including global system inodes and slot-local system inodes such as journals, local allocators, quotas, and inode/extent allocators.

Important APIs and functions: public `ocfs2_get_system_file_inode` returns a referenced inode for a system inode type and slot. Helpers include `_ocfs2_get_system_file_inode`, `is_global_system_inode`, and `get_local_system_inode`. Under `CONFIG_DEBUG_LOCK_ALLOC`, per-system-inode lock class keys are installed for lockdep.

Control flow: lookup first identifies the cache slot: global array for global system inodes or lazily allocated `local_system_inodes` matrix for local types by slot. Under `system_file_mutex`, it returns an extra `igrab` reference if cached; otherwise it constructs the system inode name, looks up the block number in `sys_root_inode`, calls `ocfs2_iget`, stores an array reference when possible, and returns the caller reference.

State and persistence behavior: persistent state is the system directory entry naming scheme and dinode blocks. Runtime state is the cached inode pointer arrays in `struct ocfs2_super`, protected by `system_file_mutex`; the arrays hold their own inode references until `ocfs2_release_system_inodes` drops them. The local-system-inode array is allocated lazily under `osb_lock`.

Dependencies and integration points: depends on system inode name formatting, directory lookup, `ocfs2_iget`, OCFS2 superblock fields, inode lock resources, and lockdep. It is used by mount initialization, allocators, quotas, journals, statfs, local alloc, and truncate/recovery paths.

Risks: missing or corrupt system directory entries prevent mount or allocator operation. Lazy local array allocation can fail; the code falls back to uncached lookup for that attempt. Slot/type validation relies on BUG_ON for impossible callers. Cached references must be released in the matching superblock teardown path.

Test signals: global system inode lookup, local system inode lookup across all slots, lazy array allocation race, allocation failure fallback, missing system inode directory entry, lockdep class assignment for quota/journal versus other system files, and repeated lookup reference counts.
