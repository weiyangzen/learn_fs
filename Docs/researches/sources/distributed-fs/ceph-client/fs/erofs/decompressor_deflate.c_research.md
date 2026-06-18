<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/erofs/decompressor_deflate.c -->
# sources/distributed-fs/ceph-client/fs/erofs/decompressor_deflate.c

## Purpose
`decompressor_deflate.c` implements EROFS DEFLATE compressed-data support using in-kernel zlib, with optional crypto acceleration for full decodes.

## Important APIs, types, and functions
The exported decompressor is `z_erofs_deflate_decomp`. Important functions are `z_erofs_deflate_init`, `z_erofs_deflate_exit`, `z_erofs_load_deflate_config`, `z_erofs_deflate_decompress`, and internal `__z_erofs_deflate_decompress`. Runtime stream state is `struct z_erofs_deflate`, with a zlib stream, workspace, bounce page, global stream list, spinlock, waitqueue, and `deflate_streams` module parameter.

## Control flow
Init chooses a stream count defaulting to possible CPUs. Config validates the on-disk deflate config and lazily allocates zlib workspaces once. Decompression fixes compressed input size, optionally tries crypto acceleration when not partial, waits for an available stream, initializes raw deflate inflate, uses `z_erofs_stream_switch_bufs` to feed multi-page input/output with overlap protection, inflates until output is satisfied or stream ends, ends zlib state, returns the stream to the global list, and wakes waiters.

## State and persistence
Runtime state is the global stream pool and allocated zlib workspaces. Persistent state is the on-disk DEFLATE config and compressed data read only.

## Dependencies and integration points
It depends on zlib inflate, EROFS stream switching, crypto acceleration when enabled, waitqueues, spinlocks, and decompressor config parsing.

## Risks and test signals
Risks include stream-pool deadlocks, ignoring unsupported windowbits because kernel zlib cannot customize it, partial decode termination mistakes, workspace allocation failure, and missed wakeups. Test signals include DEFLATE images, concurrent reads exceeding stream count, partial and full reads, crypto fallback, corrupt compressed streams, and low-memory config initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/erofs/decompressor_deflate.c -->
