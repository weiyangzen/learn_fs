# sources/distributed-fs/ceph-client/fs/udf/truncate.c

## Purpose
`truncate.c` shortens UDF extent lists, discards preallocation, trims the last extent to `i_size`, and frees no-longer-referenced data or indirect allocation extents.

## Important APIs, types, and functions
Public functions are `udf_truncate_tail_extent`, `udf_discard_prealloc`, and `udf_truncate_extents`. Internal helpers are `extent_trunc` and `udf_update_alloc_ext_desc`.

## Control flow
`extent_trunc` rewrites one allocation descriptor to a shorter length, converts preallocated but not recorded space to unallocated form when needed, and frees blocks beyond the new extent end. Tail truncation walks extents until logical bytes exceed `i_size`, rewinds to the containing descriptor, trims it, and warns if extents remain past EOF. Preallocation discard finds a trailing `EXT_NOT_RECORDED_ALLOCATED` extent, deletes it, and frees its blocks. Full truncation maps the first block after the new EOF, trims that extent to the byte offset, then iterates remaining descriptors; indirect extent descriptors switch traversal to the external allocation extent and are freed when emptied.

## State and persistence
The file mutates allocation descriptors in the inode entry or allocation extent blocks, `i_lenAlloc`, `i_lenExtents`, and dirty state. It frees blocks through UDF allocation code and updates allocation extent descriptor tags and dirty metadata buffers.

## Dependencies and integration points
It depends on `inode_bmap`, `udf_next_aext`, `udf_current_aext`, `udf_write_aext`, `udf_delete_aext`, `udf_free_blocks`, `udf_update_tag`, `mmb_mark_buffer_dirty`, and inode locking performed by callers in `inode.c`.

## Risks and test signals
Risks include freeing the wrong block range for partial extents, mishandling `EXT_NEXT_EXTENT_ALLOCDESCS`, stale `lenalloc`, leaked preallocation, and inconsistent `i_lenExtents` after iterator errors. Test signals include shrinking direct and indirect extent files, preallocated tail discard, AD short versus AD long, exact block-boundary truncates, inline AD-in-ICB bypass, and corrupted extent chains.
