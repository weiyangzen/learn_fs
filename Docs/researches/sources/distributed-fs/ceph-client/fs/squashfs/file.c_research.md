# sources/distributed-fs/ceph-client/fs/squashfs/file.c

## Purpose

`file.c` implements regular file reads, readahead, sparse block handling, fragment-tail reads, large-file block-list indexing, page-cache population, and `SEEK_DATA`/`SEEK_HOLE` support for SquashFS.

## Important APIs, Types, and Functions

Public objects/functions are `squashfs_aops`, `squashfs_file_operations`, and `squashfs_copy_cache()`. Important internals include `locate_meta_index()`, `empty_meta_index()`, `release_meta_index()`, `read_indexes()`, `calculate_skip()`, `fill_meta_index()`, `read_blocklist_ptrs()`, `read_blocklist()`, `squashfs_readpage_fragment()`, `squashfs_readpage_sparse()`, `squashfs_read_folio()`, `squashfs_readahead_fragment()`, `squashfs_readahead()`, `seek_hole_data()`, and `squashfs_llseek()`.

## Control Flow

For a folio read, the file offset is mapped to a SquashFS block index. If the target is a normal data block, `read_blocklist()` finds its compressed size and on-disk address; zero size means a sparse block, nonzero means `squashfs_readpage_block()` from the selected file strategy. If the final partial block is packed in a fragment, it reads from the fragment cache. Readahead expands requests to SquashFS block boundaries and fills batches directly through a page actor. Large-file mapping uses a small meta-index cache to avoid rescanning block lists from the inode for every random read.

## State and Persistence Behavior

Per-inode state in `squashfs_inode_info` stores start block, block-list metadata location, fragment location, and fragment offset. Per-mount mutable state includes the lazily allocated `msblk->meta_index` array guarded by `meta_index_mutex`. Page-cache pages become persistent VFS cache state after successful reads.

## Dependencies and Integration Points

It depends on `cache.c`, `block.c`, `fragment.c`, `page_actor`, and the file strategy implementation in `file_cache.c` or `file_direct.c`. `inode.c` assigns these address-space and file operations to regular file inodes.

## Risks and Edge Cases

The meta-index cache has locking and reuse complexity. Sparse blocks must be zero-filled and reported correctly to `SEEK_DATA`/`SEEK_HOLE`. Fragment tails cannot coincide with block-aligned file sizes. Readahead error paths must unlock and put every page. Corrupt block sizes from metadata must abort safely.

## Test Signals

Sequential and random reads of small, large, sparse, and fragment-tailed files; mmap reads; readahead-heavy workloads; `lseek(SEEK_DATA/SEEK_HOLE)` conformance; corruption tests for block lists; and parallel reads that exercise meta-index locking.
