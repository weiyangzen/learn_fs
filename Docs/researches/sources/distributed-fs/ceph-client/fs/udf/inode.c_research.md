# sources/distributed-fs/ceph-client/fs/udf/inode.c

## Purpose

`sources/distributed-fs/ceph-client/fs/udf/inode.c` is the core UDF inode implementation. It owns page-cache address-space operations, in-ICB file handling, logical-to-physical block mapping, sparse extent creation, preallocation, extent merge/update/delete, inode read/write serialization, indirect allocation extents, inode lookup, and extent iteration. The source was read as a complete 2459-line implementation.

## Important APIs, Types, and Functions

Exported or cross-file functions include `udf_evict_inode`, `udf_expand_file_adinicb`, `udf_get_block`, `udf_bread`, `udf_setsize`, `udf_update_extra_perms`, `udf_write_inode`, `__udf_iget`, `udf_setup_indirect_aext`, `__udf_add_aext`, `udf_add_aext`, `udf_write_aext`, `udf_next_aext`, `udf_current_aext`, `udf_delete_aext`, and `inode_bmap`. The exported address-space table is `udf_aops`. Major internal helpers include extent cache helpers, `udf_write_failed`, `udf_handle_page_wb`, `udf_read_folio`, `udf_readahead`, write-begin/end, direct I/O, `udf_map_block`, `inode_getblk`, `udf_extend_file`, `udf_do_extend_file`, `udf_split_extents`, `udf_prealloc_extents`, `udf_merge_extents`, `udf_update_extents`, `udf_read_inode`, and `udf_update_inode`.

## Control Flow

Read/write flow starts at `udf_aops`. In-ICB files are read and written from `iinfo->i_data`; extent-backed files use mpage/block helpers and `udf_get_block`. `udf_map_block` either maps existing extents under a read lock or, for create, clears unsuitable preallocation, invalidates the extent cache, and calls `inode_getblk`. `inode_getblk` walks allocation descriptors to find the target logical block, extends sparse EOF holes if necessary, allocates or consumes a not-recorded allocated block, splits the current extent around the target block, optionally preallocates more blocks, merges adjacent extents, writes the resulting extent list back, updates allocation goals, and dirties or synchronizes the inode.

Inode read flow validates partition/block ranges, follows supported ICB indirection with a nesting limit, loads FE/EFE/USE data, converts uid/gid/mode/timestamps/lengths, validates allocation descriptor sizes, initializes operation tables based on UDF file type, and handles special-device extended attributes. Inode write flow builds a fresh FE/EFE/USE block, serializes ownership, permissions, sizes, timestamps, allocation descriptors, stream directory state, ICB flags, descriptor CRCs, and tag checksums, then marks or synchronously writes the buffer.

## State and Persistence Behavior

Runtime state includes extent cache entries, `i_data`, `i_lenEAttr`, `i_lenAlloc`, `i_lenExtents`, allocation goals, allocation descriptor type, FE/EFE/USE mode, hidden/use flags, stream directory metadata, checkpoints, unique IDs, creation time, metadata buffer tracking, and inode block counts. Persistent state is stored in FE/EFE/USE descriptors, allocation descriptors embedded in the inode or indirect allocation extent descriptors, data blocks, and UDF extended attributes. Truncate and eviction free extents and inode blocks when link count reaches zero.

## Dependencies and Integration Points

The file integrates with Linux page cache, writeback, mpage, direct I/O, buffer-head I/O, CRC helpers, VFS inode lifecycle, UDF block allocator, UDF descriptor/tag helpers, UDF time conversion, symlink/dir/file/namei operation tables, partition mapping, metadata buffer tracking, and mount flags for strict mode, descriptor type, uid/gid/mode overrides, and allocation descriptor choices.

## Risks and Edge Cases

This file has many corruption and consistency edges: in-ICB files must fit inside the file entry; extent lengths combine type bits with byte lengths; indirect extents are bounded by `UDF_MAX_INDIR_EXTS`; ICB indirection is bounded by `UDF_MAX_ICB_NESTING`; malformed descriptor lengths can overflow or exceed a block; block mapping beyond EOF must create sparse holes without preserving stale preallocation; failed extent insertion can leak blocks or partially corrupt extent lists; page writeback must not allocate blocks; FE/EFE differences must be preserved; and hidden inodes with zero link counts are treated differently from normal stale inodes.

## Test Signals

High-value tests include FE and EFE inode round trips, in-ICB read/write/expand/truncate paths, sparse file growth, block allocation near EOF, preallocation and discard, extent split/merge/delete, indirect allocation extents, direct I/O fallback for in-ICB files, mmap/writeback/truncate races, special device EAs, symlink and directory inode reads, corrupted descriptor length/ICB nesting/indirect extent fuzzing, and fsync/writeback error injection.
