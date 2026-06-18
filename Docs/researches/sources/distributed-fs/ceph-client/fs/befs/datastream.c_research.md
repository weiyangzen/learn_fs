# sources/distributed-fs/ceph-client/fs/befs/datastream.c

Purpose: maps BeFS file-relative blocks and byte positions to disk block runs, reads datastream buffers, reads long symlinks, and counts data plus metadata blocks.

Important APIs/types/functions: `BAD_IADDR`, `befs_read_datastream`, `befs_fblock2brun`, `befs_read_lsymlink`, `befs_count_blocks`, and direct/indirect/double-indirect block-run search helpers.

Control flow: byte positions are converted to file blocks and offsets, then `befs_fblock2brun()` chooses direct, indirect, or double-indirect lookup based on datastream range limits. Direct lookup linearly scans inline runs; indirect lookup reads run arrays; double-indirect lookup computes indexes into fixed-size run groups and reads only the necessary mapping blocks.

State and persistence: consumes persistent `befs_data_stream` fields copied into inode-private state. No mutation occurs. Buffer_heads returned by reads are caller-owned and must be released.

Dependencies and integration: uses `befs_bread_iaddr()`/`sb_bread()`, endian conversion, BeFS block geometry, and feeds `linuxvfs.c` read_folio/bmap and `btree.c` node reads.

Risks: corrupt range limits or run lengths can produce bad reads or arithmetic mistakes. The double-indirect index calculation is especially sensitive, and comments note uncertainty about `BEFS_DBLINDIR_BRUN_LEN` units.

Test signals: read files spanning direct, indirect, and double-indirect extents; long symlinks of boundary lengths; corrupted run arrays; block count comparisons with known images.
