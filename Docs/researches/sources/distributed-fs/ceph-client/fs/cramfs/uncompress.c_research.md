# sources/distributed-fs/ceph-client/fs/cramfs/uncompress.c

Purpose: wraps zlib inflate for Cramfs block decompression with a single reusable global stream.

Important APIs/functions: `cramfs_uncompress_init()` allocates zlib workspace with `vmalloc()` and initializes the stream on first user. `cramfs_uncompress_block()` resets the stream, inflates one compressed source buffer into the destination page-sized buffer, returns decompressed byte count, and logs/reset-recovers from reset errors. `cramfs_uncompress_exit()` ends the zlib stream and frees workspace when the final user exits.

Control flow: filesystem init initializes the stream. Each compressed block read sets `next_in`, `avail_in`, `next_out`, and `avail_out`, calls `zlib_inflateReset()`, then `zlib_inflate(..., Z_FINISH)`. Module exit tears down the stream.

State and persistence: global `z_stream stream` and `initialized` refcount persist while Cramfs is loaded. No filesystem data persists here.

Dependencies/integration: depends on `linux/zlib.h`, `vmalloc`, and Cramfs `internal.h`. `inode.c` serializes access with `read_mutex`.

Risks: decompression is explicitly single-threaded; using it without the external mutex would corrupt the global stream. Error logging includes kernel pointers with `%p`, subject to pointer formatting policy. `initialized` is not atomic because lifecycle is module-level.

Test signals: compressed block success, corrupt zlib stream returning `-EIO`, init allocation failure, repeated init/exit pairing, and concurrent file reads under lockdep or stress to verify serialization.
