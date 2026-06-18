# sources/distributed-fs/ceph-client/crypto/lzo.c

Purpose: wraps the standard LZO1X safe compressor/decompressor as an scomp crypto algorithm named `lzo`.

Important APIs and functions: `lzo_alloc_ctx()`/`lzo_free_ctx()` manage `LZO1X_MEM_COMPRESS` workspace. `lzo_scompress()` calls `lzo1x_1_compress_safe()`, while `lzo_sdecompress()` calls `lzo1x_decompress_safe()`.

Control flow: module init registers a single `scomp_alg`. Compression and decompression each translate the crypto API `unsigned int` destination length into a library `size_t`, run the safe LZO primitive, return `-EINVAL` on non-OK status, and update `*dlen` with actual output length.

State and persistence: per-stream work memory is allocated with `kvmalloc()` and released with `kvfree()`. No dictionary or persistent stream state is stored in the wrapper.

Dependencies and integration points: depends on the kernel LZO library and the synchronous compression framework. The acomp compatibility path in `scompress.c` can use this implementation for asynchronous-style compression requests.

Risks: output buffer sizing is caller-owned. The wrapper compresses raw LZO blocks without framing metadata. All library errors collapse to `-EINVAL`, reducing failure detail.

Test signals: standard crypto compression vectors, round trips across empty/small/large buffers, boundary output sizes, malformed stream rejection, and module alias lookup for `lzo`.
