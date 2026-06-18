# sources/distributed-fs/ceph-client/fs/jffs2/read.c

## Purpose

`read.c` implements data reads from JFFS2 raw inode nodes and logical inode ranges. It validates node and data CRCs, handles compression and historical hole-node quirks, fills holes with zeroes, and walks the in-core fragment tree to satisfy reads.

## Important APIs, Types, And Functions

`jffs2_read_dnode()` reads one `struct jffs2_full_dnode` into a caller buffer. It allocates a temporary `struct jffs2_raw_inode`, reads the node header through `jffs2_flash_read()`, verifies `node_crc`, reads compressed or raw data, verifies `data_crc`, decompresses through `jffs2_decompress()` when needed, and copies the requested slice.

`jffs2_read_inode_range()` reads a logical byte range from an inode by walking `struct jffs2_node_frag` entries in `f->fragtree`. It uses `jffs2_lookup_node_frag()`, `frag_next()`, and `jffs2_read_dnode()`, filling both missing fragment gaps and explicit hole fragments with zeroes.

## Control Flow

A range read starts by locating the fragment overlapping the requested offset. While `offset < end`, the code handles three cases: no fragment or a gap before the next fragment, a fragment with no node, or a data fragment. Gaps and node-less fragments are zero-filled. Data fragments compute the offset within the physical dnode and delegate to `jffs2_read_dnode()`. On read error, the corresponding output range is zeroed and the error is returned.

Inside `jffs2_read_dnode()`, uncompressed whole-node reads can target the caller buffer directly. Partial or compressed reads allocate a compressed read buffer and, for partial compressed nodes, a full decompression buffer. `JFFS2_COMPR_ZERO` is optimized as a memset. Historical nodes with swapped `csize`/`dsize` for zero compression are normalized before use.

## State And Persistence Behavior

This file does not mutate persistent flash state. It trusts the in-core fragment tree built by `readinode.c` but independently validates medium contents with CRCs at read time. The returned data model preserves sparse regions as zeroes, matching filesystem hole semantics.

## Dependencies And Integration Points

The read path depends on flash IO from `jffs2_flash_read()`, compression from `compr.h`, CRC32, allocation helpers for raw inode headers, and fragment-tree helpers from `nodelist.h`. It is consumed by VFS page/folio read paths and by any internal code that needs logical inode data.

## Risks And Edge Cases

Memory allocation failures can occur for compressed or partial reads. Short MTD reads are mapped to `-EIO`. CRC mismatches also produce `-EIO`. The range loop notes a known inefficiency: if one physical node appears in multiple fragments, it may be read more than once. Offset arithmetic must remain consistent between fragment offsets and raw node offsets, especially after truncation or overlapping-node replay.

## Test Signals

Read tests should cover uncompressed full-node reads, uncompressed partial reads, compressed full and partial reads, zero-compression hole nodes, sparse ranges before/between/after fragments, bad node CRC, bad data CRC, short reads, and allocation failure injection. Fragment-tree overlap cases from `readinode.c` are important integration tests.
