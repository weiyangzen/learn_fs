# sources/distributed-fs/ceph-client/fs/squashfs/file_direct.c

## Purpose

`file_direct.c` implements the direct file-data strategy, decompressing a compressed SquashFS block directly into page-cache pages covered by that filesystem block.

## Important APIs, Types, and Functions

It defines `squashfs_readpage_block()`. Important local state includes the target folio, grabbed sibling pages, a `struct squashfs_page_actor`, and the last page returned by the actor.

## Control Flow

The function computes all page indexes covered by the SquashFS block, grabs non-target pages opportunistically, skips already-uptodate pages, creates a direct page actor, and calls `squashfs_read_data()`. On exact expected byte count, it zero-fills the tail of the final file page when needed, marks pages uptodate, unlocks them, and releases non-target pages. On failure, it leaves the target page for the caller and unlocks/releases other pages.

## State and Persistence Behavior

No private persistent state is created. Successful decompression populates page-cache pages directly. Temporary page arrays and actor state are freed before return.

## Dependencies and Integration Points

Selected by `CONFIG_SQUASHFS_FILE_DIRECT`. It depends on `page_actor`, `block.c`, and `file.c`. Backend `alloc_buffer` flags affect whether direct actor gaps can use a temporary buffer.

## Risks and Edge Cases

Page grabbing can fail for sibling pages; the actor must handle gaps without corrupting output ordering. The return count must match `expected` or pages are treated as errored. Tail zeroing is required for the last page of a file.

## Test Signals

Direct-mode read, mmap, readahead, partial-cache, memory-pressure, and compressed backend coverage; tests should include holes in grabbed page ranges and final partial pages.
