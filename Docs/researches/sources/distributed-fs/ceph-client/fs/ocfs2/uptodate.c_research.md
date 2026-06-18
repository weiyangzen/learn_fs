# sources/distributed-fs/ceph-client/fs/ocfs2/uptodate.c

Purpose: implements OCFS2's cluster-aware metadata buffer uptodate cache. Standard `buffer_uptodate` is insufficient because another node can change metadata after a local buffer was read, so this file tracks trusted metadata block numbers per caching object without pinning buffer_heads.

Important APIs and functions: public functions include `ocfs2_metadata_cache_init`, `ocfs2_metadata_cache_exit`, `ocfs2_metadata_cache_purge`, `ocfs2_metadata_cache_owner`, `ocfs2_metadata_cache_io_lock`, `ocfs2_metadata_cache_io_unlock`, `ocfs2_buffer_uptodate`, `ocfs2_buffer_read_ahead`, `ocfs2_set_buffer_uptodate`, `ocfs2_set_new_buffer_uptodate`, `ocfs2_remove_from_cache`, `ocfs2_remove_xattr_clusters_from_cache`, `init_ocfs2_uptodate_cache`, and `exit_ocfs2_uptodate_cache`. Internally it uses inline arrays for small caches and an rb-tree of `struct ocfs2_meta_cache_item` after expansion.

Control flow: cache initialization installs owner/super/lock/io-lock callbacks and starts in inline-array mode. Lookup checks local buffer uptodate first, trusts journaled buffers, then searches the per-object cache. Insertion avoids duplicates, appends to the inline array when possible, expands to an rb-tree when full, and tolerates allocation failure as a performance loss. Purge swaps out the tree under the cache lock and frees nodes outside it. Removal deletes a block from either array or tree and frees rb-tree nodes.

State and persistence behavior: the cache is runtime-only and stores block numbers plus transaction tracking fields in `struct ocfs2_caching_info`. It never pins buffer_heads and is only a strong hint paired with buffer flags and journal state. A slab cache named `ocfs2_uptodate` owns rb-tree items. New buffers are marked buffer-uptodate and inserted under the caching object's I/O lock.

Dependencies and integration points: depends on caching operations supplied by inode/system objects, buffer_head state, JBD2 `buffer_jbd`, OCFS2 cluster lock invalidation, xattr cluster removal, tracepoints, and superblock geometry for xattr cluster-to-block removal. It is used by metadata read, journal access, inode eviction, allocation group creation/removal, and xattr deletion.

Risks: cache validity relies on callers purging/removing entries when cluster locks are dropped or metadata is deleted. Inline-to-tree expansion allocates several objects and must handle concurrent purge/removal between allocation and insertion. Missing cache insertion is nonfatal but can increase disk I/O; stale cache retention is dangerous. Count mismatches during purge are logged because they indicate internal accounting bugs.

Test signals: metadata read after remote invalidation, journaled buffer trust, inline cache fill and rb-tree expansion, purge during concurrent insertion, remove from array and tree, xattr cluster removal across multiple blocks, allocation failure in slow insertion path, and slab init/exit leak checks.
