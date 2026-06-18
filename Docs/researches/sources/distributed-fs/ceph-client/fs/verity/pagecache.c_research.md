<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/verity/pagecache.c -->
# sources/distributed-fs/ceph-client/fs/verity/pagecache.c

Purpose: Provides generic filesystem helpers for reading and readahead of Merkle tree pages stored in an inode’s pagecache.

Important APIs, types, and functions: Exports `generic_read_merkle_tree_page()` and `generic_readahead_merkle_tree()`.

Control flow: The read helper calls `read_mapping_folio()` for the adjusted pagecache index and returns the corresponding page within the folio. The readahead helper asserts the mapping invalidate lock is held, checks whether the starting folio is missing or not uptodate, and triggers unbounded pagecache readahead for the requested Merkle tree range.

State and persistence: Reads and populates pagecache state for Merkle tree pages. Persistent Merkle tree placement is filesystem-specific; callers must translate fs-verity-relative indices to actual pagecache indices before using these helpers.

Dependencies and integration points: Used by filesystems that store Merkle tree data in their own pagecache address space. Depends on folio/pagecache APIs, readahead control, and filesystem locking around invalidation.

Risks and test signals: Risks include incorrect index adjustment by callers, readahead without invalidate lock, stale or non-uptodate hash pages, and folio/page reference mistakes. Test filesystems using the generic helpers with shifted Merkle-tree offsets, cache hits/misses, readahead under concurrent invalidation, and large tree ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/verity/pagecache.c -->
