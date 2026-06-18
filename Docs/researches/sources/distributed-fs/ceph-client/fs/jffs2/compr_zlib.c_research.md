# sources/distributed-fs/ceph-client/fs/jffs2/compr_zlib.c

## Purpose
`compr_zlib.c` implements the zlib compressor backend, historically the main JFFS2 compression method. It wraps kernel zlib deflate/inflate workspaces behind the `struct jffs2_compressor` interface.

## Important APIs, Types, And Functions
Important functions are `alloc_workspaces()`, `free_workspaces()`, `jffs2_zlib_compress()`, `jffs2_zlib_decompress()`, `jffs2_zlib_init()`, and `jffs2_zlib_exit()`. The static `z_stream` objects `def_strm` and `inf_strm` are protected by separate mutexes. `STREAM_END_SPACE` reserves trailing output room for final deflate completion.

## Control Flow
Init vmallocs deflate and inflate workspaces and registers `jffs2_zlib_comp`. Compression initializes deflate at level 3, repeatedly feeds bounded chunks with `Z_PARTIAL_FLUSH` while preserving stream-end space, then finalizes with `Z_FINISH`. It rejects results that are not smaller than input and returns updated source/destination lengths. Decompression optionally skips zlib wrapper/adler handling for plain deflate streams without preset dictionaries, initializes inflate with positive or negative window bits, inflates to `Z_STREAM_END`, and tears down the stream.

## State And Persistence Behavior
Global zlib streams and workspaces are reused across calls, serialized by mutexes. On-flash nodes are tagged `JFFS2_COMPR_ZLIB` and store deflate-compatible payload bytes.

## Dependencies And Integration Points
The backend depends on kernel zlib/zutil, vmalloc, mutex APIs, `nodelist.h`, and `compr.h`. It is registered during compressor initialization and called through `jffs2_compress()`/`jffs2_decompress()` from write, read, and GC paths.

## Risks And Test Signals
The decompressor logs non-`Z_STREAM_END` but still returns zero, so corrupt data detection may rely on lower-level CRC checks before decompression. Compression bounds and `STREAM_END_SPACE` are subtle. Tests should include zlib-compressed fixture images, corrupt data CRC paths, tiny destination buffers, concurrent compression/decompression, and mount configurations forcing zlib.
