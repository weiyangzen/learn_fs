# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_rtbitmap.c

## Purpose
`xfs_rtbitmap.c` implements realtime allocator bitmap and summary manipulation shared with userspace libxfs. It reads and verifies realtime metadata buffers, searches and mutates free/allocated realtime extent bits, updates summary counters, frees realtime extents, queries free ranges, computes bitmap/summary geometry, and initializes realtime bitmap/summary files during creation or growfs.

## Important APIs and functions
Buffer APIs are `xfs_rtbuf_cache_relse`, `xfs_rtbitmap_read_buf`, and `xfs_rtsummary_read_buf`. Search/check/mutation APIs include `xfs_rtfind_back`, `xfs_rtfind_forw`, `xfs_rtcheck_range`, `xfs_rtmodify_range`, `xfs_rtmodify_summary`, `xfs_rtget_summary`, and `xfs_rtfree_range`. Higher-level exported operations are `xfs_rtfree_extent`, `xfs_rtfree_blocks`, `xfs_rtalloc_query_range`, `xfs_rtalloc_query_all`, `xfs_rtalloc_extent_is_free`, geometry helpers, `xfs_rtfile_initialize_blocks`, `xfs_rtbitmap_create`, and `xfs_rtsummary_create`.

The file defines buffer ops for legacy rt metadata and rtgroup-aware bitmap/summary metadata. Rtgroup format adds a header with magic, owner inode, block address, LSN, UUID, and CRC.

## Control flow
Bitmap/summary access goes through `xfs_rtbuf_get`, which maps the hidden metadata inode block with `xfs_bmapi_read`, reads the backing device buffer, verifies type/owner, marks the transaction buffer type, and caches one bitmap and one summary buffer in `struct xfs_rtalloc_args`. Bit searches operate word-by-word with masks across metadata file blocks. `xfs_rtmodify_range` sets or clears bits and logs only changed word spans.

Freeing a range first marks bitmap bits free, then uses backward/forward searches to find the complete newly free extent. It decrements summary counters for split-off fragments that are no longer free extents and increments the counter for the combined free run. `xfs_rtfree_extent` wraps this in transaction/superblock updates and legacy bitmap inode sequence reset behavior; `xfs_rtfree_blocks` validates realtime-block alignment, converts to realtime extents, and for rtgroups records the freed range as busy.

Queries scan the bitmap for state transitions, invoke callbacks for free records, and release cached buffers at the end. Initialization allocates file blocks with metadata bmap writes, then zeroes or copies content one block per transaction, installing rtgroup headers when needed.

## State and persistence behavior
Persistent state lives in hidden realtime bitmap and summary inodes, the superblock free realtime extent counter, and optionally rtgroup metadata headers. Bitmap bits use 1 for free and 0 for allocated. Summary counters are indexed by `log2(extent length)` and bitmap block number. Mutations are transaction-logged at buffer byte ranges; creation/growfs paths log entire initialized buffers and inode core size changes.

## Dependencies and integration points
This file depends on xfs bmap, transactions, realtime group inodes, mount geometry, health marking, buffer verifiers, superblock accounting, busy extent tracking, and error tags. Allocation code uses the check/search/summary APIs; free-space scrub and reporting use query helpers; growfs and mkfs-style initialization use the create/initialize helpers.

## Risks and invariants
Risks include bitmap/summary counter mismatch, alignment mistakes converting realtime blocks to realtime extents, stale cached buffers after switching blocks, header verification differences between legacy and rtgroup formats, and partial-word mask errors. Invariants include valid bitmap/summary file block bounds, written metadata mappings, correct owner inode in rtgroup headers, no zoned mode for bitmap operations, and exclusive lock ownership on the bitmap inode during frees.

## Test signals
Useful tests include freeing aligned and misaligned realtime ranges, boundary ranges crossing bitmap blocks, summary counter updates for splitting/merging free runs, rtgroup CRC/header verification, legacy no-rtgroups behavior, query-all/query-range callback coverage, and growfs initialization of bitmap/summary file blocks.
