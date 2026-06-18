# sources/distributed-fs/ceph-client/fs/udf/directory.c

## Purpose

`sources/distributed-fs/ceph-client/fs/udf/directory.c` provides low-level directory file-identifier iteration and modification helpers. It parses, validates, copies, writes, and appends UDF `fileIdentDesc` records, including entries that straddle block boundaries. The source was read as a complete 543-line implementation.

## Important APIs, Types, and Functions

Iterator APIs are `udf_fiiter_init`, `udf_fiiter_advance`, `udf_fiiter_release`, `udf_fiiter_write_fi`, `udf_fiiter_update_elen`, and `udf_fiiter_append_blk`. Descriptor extraction helpers are `udf_get_fileshortad` and `udf_get_filelongad`. Internal helpers include `udf_verify_fi`, `udf_copy_fi`, `udf_readahead_dir`, `udf_fiiter_bread_blk`, `udf_fiiter_advance_blk`, `udf_fiiter_load_bhs`, `udf_copy_to_bufs`, `udf_crc_fi_bufs`, and `udf_copy_fi_to_bufs`.

## Control Flow

Initialization handles in-ICB directories by copying directly from inode-resident data, or block-backed directories by mapping the starting logical block through `inode_bmap`, loading one or two buffer heads, and copying the current FID. Advancement adds the aligned FID length to `iter->pos`, rolls buffer heads when crossing blocks, advances allocation extents as needed, loads a second buffer when the header or name crosses a block boundary, and revalidates/copies the next FID. Writing copies a modified FID, implementation-use bytes, and optionally a temporary name buffer into one or two backing buffers, recomputes the descriptor CRC and tag checksum, marks buffers or the inode dirty, and increments directory i_version. Appending rounds the final extent length, allocates a new block through `udf_bread`, then refreshes mapping state.

## State and Persistence Behavior

Iterator state tracks the directory inode, current byte position, current extent, offset within the extent, up to two buffer heads, copied FID header, name pointer or scratch name buffer, and extent-position cursor. Persistent changes are made by rewriting inode-resident directory data or dirtying metadata buffer heads. Extent length updates change allocation descriptors and `i_lenExtents`.

## Dependencies and Integration Points

The file integrates with UDF extent walking (`inode_bmap`, `udf_next_aext`, `udf_write_aext`), block allocation/read (`udf_bread`), descriptor CRC helpers (`crc_itu_t`, `udf_tag_checksum`), metadata buffer tracking (`mmb_mark_buffer_dirty`), inode versioning, and directory/namei code that uses the iterator to scan or mutate entries.

## Risks and Edge Cases

Validation rejects wrong tags, unaligned implementation-use lengths, FIDs larger than one block, entries past directory size, and CRC-length mismatches. The code explicitly does not support very large implementation-use fields even if the spec allows them. Names can cross block boundaries and must be copied to `namebuf` before modification. Iterator initialization uses `__GFP_NOFAIL` for `namebuf` because later verified directory modifications are hard to roll back. Appending must restore the previous extent length if block allocation fails.

## Test Signals

Useful tests include reading and rewriting entries wholly within one block, header/name straddling block boundaries, in-ICB directories, malformed FID tags and CRC lengths, append-at-EOF, extent-boundary advancement, metadata dirty tracking, i_version changes, and fuzzed directory images.
