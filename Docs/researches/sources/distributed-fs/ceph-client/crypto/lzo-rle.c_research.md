# sources/distributed-fs/ceph-client/crypto/lzo-rle.c

Purpose: wraps the LZO-RLE safe compressor as an scomp crypto algorithm named `lzo-rle`.

Important APIs and functions: `lzorle_alloc_ctx()`/`lzorle_free_ctx()` allocate `LZO1X_MEM_COMPRESS` workspace with `kvmalloc()`/`kvfree()`. `lzorle_scompress()` calls `lzorle1x_1_compress_safe()`. `lzorle_sdecompress()` calls `lzo1x_decompress_safe()`.

Control flow: crypto registration exposes a single `scomp_alg`. Compression converts `unsigned int *dlen` to a `size_t` temporary required by LZO, maps non-`LZO_E_OK` to `-EINVAL`, and writes the resulting size back. Decompression follows the same size conversion pattern.

State and persistence: only the compression workspace persists per stream. There is no global runtime state beyond the registered algorithm.

Dependencies and integration points: depends on `<linux/lzo.h>` and the scomp framework. It shares decompression with standard LZO because RLE is an encoding variant of the LZO1X stream.

Risks: size conversion comments highlight the `size_t` versus `unsigned int` boundary on 64-bit systems. Destination length must be supplied by callers. The wrapper returns only generic `-EINVAL` for library failures, so diagnostics depend on tests.

Test signals: round trips containing long repeated runs, ordinary small inputs, too-small output buffers, invalid compressed streams, and successful crypto lookup by `lzo-rle`.
