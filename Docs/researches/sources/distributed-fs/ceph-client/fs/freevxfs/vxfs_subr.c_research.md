# sources/distributed-fs/ceph-client/fs/freevxfs/vxfs_subr.c

## Purpose

`sources/distributed-fs/ceph-client/fs/freevxfs/vxfs_subr.c` provides shared FreeVxFS pagecache and block-read helpers plus normal address-space operations for mapped files. The complete 152-line file was read for this report.

## Important APIs, Types, and Functions

The external operation table is `vxfs_aops`, with `read_folio` and `bmap`. Exported internal helpers are `vxfs_get_page()`, `vxfs_put_page()`, and `vxfs_bread()`. Internal helpers are `vxfs_getblk()`, `vxfs_read_folio()`, and `vxfs_bmap()`.

## Control Flow

`vxfs_get_page()` calls `read_mapping_page()` and maps the page with `kmap()` for directory/inode-list consumers. `vxfs_bread()` maps a logical block through `vxfs_bmap1()` and reads the resulting physical block. `vxfs_getblk()` fills a buffer head via `map_bh()` for successful mappings. `vxfs_read_folio()` delegates to `block_read_full_folio()`, and `vxfs_bmap()` delegates to `generic_block_bmap()`.

## State and Persistence Behavior

The code reads persistent file data and metadata into pagecache or buffer cache. It does not allocate blocks or write metadata; `create` in `vxfs_getblk()` is ignored because the driver is read-only.

## Dependencies and Integration Points

It integrates with `vxfs_bmap1()`, VFS address-space operations, buffer-head I/O, pagecache helpers, directory lookup, inode-list reads, and fileset-header reads.

## Risks and Edge Cases

Physical block zero maps to `-EIO` in `vxfs_getblk()` but `vxfs_bread()` still calls `sb_bread()` even if `vxfs_bmap1()` returns zero. Page mapping uses legacy `kmap()`/`kunmap()` and depends on callers balancing `vxfs_put_page()`. Error propagation from lower-level mapping is limited.

## Test Signals

Tests include reading regular files, directories, symlinks, metadata inodes, block holes/unmapped extents, bmap ioctl paths, read errors, and highmem builds that exercise kmap balancing.
