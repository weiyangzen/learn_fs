<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/erofs/decompressor_zstd.c -->
# sources/distributed-fs/ceph-client/fs/erofs/decompressor_zstd.c

## Purpose
`decompressor_zstd.c` implements Zstandard decompression for EROFS compressed data.

## Important APIs, types, and functions
The exported decompressor is `z_erofs_zstd_decomp`. Important functions are `z_erofs_zstd_init`, `z_erofs_zstd_exit`, `z_erofs_load_zstd_config`, `z_erofs_zstd_decompress`, and stream isolation helper `z_erofs_isolate_strms`. Runtime state is `struct z_erofs_zstd`, workspace size, max dictionary size, stream list, waitqueue, spinlock, and `zstd_streams` module parameter.

## Control flow
Init allocates stream records. Config validates ZSTD format/window log, computes dictionary size, isolates all streams under a resize mutex, allocates larger workspaces with `kvmalloc` as needed, restores the stream list, updates max dictionary size, and wakes waiters. Decompression fixes compressed input size, takes one stream, initializes a zstd dstream with the max dictionary/workspace, uses common stream buffer switching for page transitions and overlap handling, calls `zstd_decompress_stream` until all output is produced, then returns the stream.

## State and persistence
Runtime state is the reusable workspace pool and maximum dictionary size. Persistent on-disk state is the ZSTD compression config and compressed clusters.

## Dependencies and integration points
It depends on the in-kernel ZSTD library, EROFS stream switching, pagepool, waitqueues, and the common decompressor registry.

## Risks and test signals
Risks include workspace resize races, incomplete stream-end detection, ZSTD error-name propagation, excessive memory footprint with high stream counts, and blocked readers when streams are exhausted. Test signals include ZSTD images at varied window logs, concurrent reads, corrupt streams, partial reads, low-memory resize failure, and mount/unmount after ZSTD config parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/erofs/decompressor_zstd.c -->
