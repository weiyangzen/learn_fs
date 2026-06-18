<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/erofs/decompressor_lzma.c -->
# sources/distributed-fs/ceph-client/fs/erofs/decompressor_lzma.c

## Purpose
`decompressor_lzma.c` implements microLZMA decompression for EROFS compressed files.

## Important APIs, types, and functions
The exported decompressor is `z_erofs_lzma_decomp`. Important functions are `z_erofs_lzma_init`, `z_erofs_lzma_exit`, `z_erofs_load_lzma_config`, and `z_erofs_lzma_decompress`. Runtime state is `struct z_erofs_lzma`, global stream list, max dictionary size, spinlock, waitqueue, and `lzma_streams` module parameter.

## Control flow
Init allocates a stream pool defaulting to possible CPUs. Config validates format and dictionary size, isolates available streams under a resize mutex, reallocates each xz microLZMA decoder for the larger dictionary if needed, returns streams to the pool, updates max dictionary size, and wakes waiters. Decompression fixes input size, waits for a stream, resets the microLZMA decoder for the request, then repeatedly uses common stream buffer switching and `xz_dec_microlzma_run` until output is complete or an error/end condition occurs.

## State and persistence
Runtime state is the decoder pool and maximum dictionary size observed from mounted filesystems. Persistent state is the read-only on-disk LZMA config and compressed clusters.

## Dependencies and integration points
It depends on XZ microLZMA, EROFS stream switching, pagepool, waitqueues, spinlocks, and decompressor config parsing.

## Risks and test signals
Risks include stream isolation races during dictionary resize, waiting while all streams are active, invalid dictionary bounds, partial decoding semantics, and decoder allocation failures. Test signals include LZMA images with minimum/maximum dictionaries, concurrent reads, config resize across mounts, corrupt streams, partial reads, and module unload after all mounts are gone.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/erofs/decompressor_lzma.c -->
