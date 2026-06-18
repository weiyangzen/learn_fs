# sources/distributed-fs/ceph-client/crypto/lz4hc.c

Purpose: registers the high-compression LZ4HC library as an scomp crypto algorithm named `lz4hc`.

Important APIs and functions: `lz4hc_alloc_ctx()` allocates `LZ4HC_MEM_COMPRESS` workspace, `lz4hc_scompress()` calls `LZ4_compress_HC()` using `LZ4HC_DEFAULT_CLEVEL`, and `lz4hc_sdecompress()` uses `LZ4_decompress_safe()` because LZ4HC output is standard LZ4 format.

Control flow: module initialization registers one `scomp_alg`. Compression receives source, destination, length pointer, and stream context; a zero return from the library maps to `-EINVAL`. Decompression maps negative returns to `-EINVAL` and records the actual decompressed size.

State and persistence: per-stream workspace is vmalloc-backed and released at stream teardown. No compressed data or dictionaries are persisted by the wrapper.

Dependencies and integration points: depends on Linux LZ4HC library functions and the scomp framework. It integrates with users that select `lz4hc` when trading CPU time for better compression.

Risks: high-compression work memory is larger than regular LZ4 and allocation failure is possible. As with `lz4.c`, there is no container framing; consumers must know expected output limits. Decompression accepts ordinary LZ4 data, so tests should not assume an LZ4HC-only decompressor.

Test signals: round trips for compressible and incompressible data, small destination buffer failure, malformed input failure, allocation failure paths, and algorithm registration/alias lookup.
