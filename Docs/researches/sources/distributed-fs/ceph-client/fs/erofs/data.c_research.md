<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/erofs/data.c -->
# sources/distributed-fs/ceph-client/fs/erofs/data.c

## Purpose
`data.c` implements EROFS metadata buffering, logical-to-physical block mapping for uncompressed and chunked files, device mapping for multi-device images, online folio completion tracking, iomap integration, direct/DAX/buffered reads, fiemap, and regular file operations.

## Important APIs, types, and functions
Important functions include `erofs_bread`, `erofs_init_metabuf`, `erofs_read_metabuf`, `erofs_put_metabuf`, `erofs_map_blocks`, `erofs_map_dev`, online folio helpers, `erofs_fiemap`, `erofs_read_folio`, `erofs_readahead`, `erofs_file_read_iter`, `erofs_file_llseek`, and the exported `erofs_aops` and `erofs_file_fops`. It uses `struct erofs_buf`, `struct erofs_map_blocks`, and `struct erofs_map_dev`.

## Control flow
Metadata reads select the correct mapping from block device, file-backed image, fscache blob, or metabox inode, then cache and kmap the needed page. `erofs_map_blocks` handles flat plain, inline tail-packing, and chunk-based files, returning mapped, hole, meta, device id, logical length, and physical address data. `erofs_map_dev` resolves primary, flat, or external devices. The iomap callbacks translate maps into `IOMAP_MAPPED`, `IOMAP_HOLE`, or `IOMAP_INLINE`. Regular reads choose DAX, direct iomap DIO, or page-cache reads.

## State and persistence
Persistent state is on-disk EROFS metadata and data extents. Runtime state includes temporary metadata buffers, device idr mappings, folio private counters for multi-part read completion, and page cache contents. No writes to the filesystem image occur.

## Dependencies and integration points
It depends on iomap, DAX, buffer/page cache APIs, file-backed VFS reads, fscache mode selection, multi-device metadata, tracepoints, and optional inode sharing through `erofs_real_inode`.

## Risks and test signals
Risks include inline data crossing block boundaries, chunk index corruption, multi-device id resolution errors, stale metadata mappings, folio completion counter bugs, direct I/O alignment reporting mismatches, and DAX mapping mistakes. Test signals include flat, inline, sparse, chunked, 48-bit, multi-device, file-backed, fscache, DAX, direct I/O, fiemap, SEEK_DATA/SEEK_HOLE, and metabox metadata images.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/erofs/data.c -->
