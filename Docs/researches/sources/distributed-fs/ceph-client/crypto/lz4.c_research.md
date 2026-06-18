# sources/distributed-fs/ceph-client/crypto/lz4.c

Purpose: registers the LZ4 compression library as a synchronous compression (`scomp`) crypto algorithm named `lz4`.

Important APIs and functions: `lz4_alloc_ctx()` and `lz4_free_ctx()` manage the LZ4 work memory. `lz4_scompress()` calls `LZ4_compress_default()`, and `lz4_sdecompress()` calls `LZ4_decompress_safe()`. `lz4_mod_init()` and `lz4_mod_fini()` register and unregister the single `scomp_alg`.

Control flow: crypto users allocate an scomp stream, which receives a vmalloc-backed context sized by `LZ4_MEM_COMPRESS`. Compression returns `-EINVAL` if the library reports zero output, otherwise updates `*dlen`. Decompression returns `-EINVAL` on negative library status and updates `*dlen` with the actual output size.

State and persistence: the only state is per-stream work memory allocated with `vmalloc()` and freed with `vfree()`. The registered algorithm object persists while the module is loaded.

Dependencies and integration points: depends on `<linux/lz4.h>` and `crypto/internal/scompress.h`; consumed by crypto compression callers and the acomp wrapper in `scompress.c`.

Risks: callers must provide adequate destination space through `*dlen`. Compression context allocation can fail under memory pressure. This wrapper does not store frame headers or original length metadata, so users must manage those format details externally.

Test signals: scomp compression/decompression round trips, too-small destination buffers, malformed compressed input, zero-length input handling, and module alias lookup for `lz4`.
