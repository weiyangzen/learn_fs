<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mpage.h -->
# sources/distributed-fs/ceph-client/include/linux/mpage.h

## Purpose
`mpage.h` declares multipage block I/O helpers for filesystems that map page-cache folios to disk blocks through `get_block_t`.

## Important APIs, Types, and Functions
Under `CONFIG_BLOCK`, it declares `mpage_readahead()`, `mpage_read_folio()`, `__mpage_writepages()`, and inline `mpage_writepages()` which calls `__mpage_writepages()` with no custom write-folio callback.

## Control Flow and State
Read paths use readahead or single-folio helpers to build BIOs containing multiple page-cache pages. Writeback calls `mpage_writepages()` or `__mpage_writepages()` to walk dirty folios, translate blocks with `get_block`, and submit block I/O.

## State and Persistence Behavior
The header owns no state. Its helpers operate on page-cache and mapping/writeback state and persist data through the block device/filesystem.

## Dependencies and Integration Points
It depends on block layer support, `address_space`, `folio`, `writeback_control`, `readahead_control`, and filesystem block mapping callbacks.

## Risks
Incorrect `get_block` behavior can corrupt I/O ranges. Filesystems with complex extents, holes, or delayed allocation may need custom write callbacks. It is absent when `CONFIG_BLOCK` is disabled.

## Test Signals
Filesystem read/writeback tests using mpage helpers, readahead behavior, sparse file reads, writeback under memory pressure, and no-block configuration builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mpage.h -->
