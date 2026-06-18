# sources/distributed-fs/ceph-client/fs/jffs2/compr_lzo.c

## Purpose
`compr_lzo.c` implements the optional LZO compressor backend for JFFS2. LZO provides fast compression/decompression and is favored by the `JFFS2_COMPR_MODE_FAVOURLZO` and force-LZO policies when configured.

## Important APIs, Types, And Functions
The module-local entry points are `jffs2_lzo_compress()`, `jffs2_lzo_decompress()`, `alloc_workspace()`, `free_workspace()`, `jffs2_lzo_init()`, and `jffs2_lzo_exit()`. `jffs2_lzo_comp` registers priority `JFFS2_LZO_PRIORITY`, name `lzo`, id `JFFS2_COMPR_LZO`, and the compress/decompress callbacks.

## Control Flow
Init allocates an LZO work memory buffer sized by `LZO1X_MEM_COMPRESS` and a worst-case page compression buffer, then registers the compressor. Compression locks `deflate_mutex`, compresses from caller input to the shared intermediate buffer using `lzo1x_1_compress()`, fails if the result exceeds caller capacity, copies the compressed bytes to `cpage_out`, updates `*dstlen`, and unlocks. Decompression calls `lzo1x_decompress_safe()` and requires the produced length to exactly match the requested destination length.

## State And Persistence Behavior
The only in-core state is the two vmalloc workspaces and their mutex. Persistent state is limited to raw inode nodes tagged with `JFFS2_COMPR_LZO`; the compressed payload is produced by this backend and later validated by exact-length decompression.

## Dependencies And Integration Points
It depends on Linux LZO helpers, vmalloc, mutexes, and the compressor registry in `compr.c`. It is invoked indirectly by `jffs2_compress()` and `jffs2_decompress()` and participates in GC rewrite compression.

## Risks And Test Signals
Shared workspace serialization is essential; missing locks would corrupt concurrent compression. The backend also assumes page-sized worst-case temporary output is enough for the inputs JFFS2 supplies. Tests should exercise force-LZO mounts, concurrent writers, incompressible pages, truncated/corrupt LZO nodes, and init failure cleanup when only one workspace allocation succeeds.
