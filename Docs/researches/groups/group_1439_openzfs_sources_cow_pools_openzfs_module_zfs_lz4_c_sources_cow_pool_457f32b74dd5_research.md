# Group Research: group_1439_openzfs_sources_cow_pools_openzfs_module_zfs_lz4_c_sources_cow_pool_457f32b74dd5

Scope checked against `Docs/research_subset_a.md`: `sources/cow-pools/openzfs` is included in subset A. All three listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/lz4.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/lz4.c

## Role

`lz4.c` provides the modern LZ4 block decompressor used by OpenZFS. The file is BSD-2-Clause LZ4 code, noted as unmodified code from LZ4 1.9.3's decompressor plus compatibility macros/constants so it can satisfy the legacy `LZ4_uncompress_unknownOutputSize()` symbol expected by the OpenZFS LZ4 wrapper.

This file does not implement OpenZFS compression registration itself. Its exported integration point is the decompression routine called by `lz4_zfs.c`'s ZFS decompression wrapper.

## Public Interface

- `int LZ4_uncompress_unknownOutputSize(const char *source, char *dest, int compressedSize, int maxDecompressedSize)` is the only externally visible function in this file.
- The wrapper flattens upstream's current `LZ4_decompress_safe()` path by directly calling `LZ4_decompress_generic()` with `endOnInputSize`, `decode_full_block`, `noDict`, `lowPrefix = dest`, no external dictionary, and dictionary size zero.
- Return semantics are inherited from safe LZ4 decompression: nonnegative decoded byte count on success, negative value on malformed input or output-limit failure.

## Implementation Structure

The file starts with portability and tuning definitions: `COMPRESSIONLEVEL`, `NOTCOMPRESSIBLE_CONFIRMATION`, endian detection via `_ZFS_BIG_ENDIAN`, memory-access mode selection, forced software bitcount on illumos, `restrict` disabling, compiler version normalization, branch prediction macros, and optional ppc64le `-O2` annotations to avoid decompression regressions.

It defines LZ4 block constants and types, including match/literal bit widths, `MINMATCH`, `LASTLITERALS`, `MFLIMIT`, `MATCH_SAFEGUARD_DISTANCE`, `FASTLOOP_SAFE_DISTANCE`, and `LZ4_DISTANCE_MAX`. Memory access helpers use built-in `memcpy` when possible, packed unaligned access when selected, or portable `memcpy` reads otherwise. `LZ4_readLE16()` normalizes little-endian offset reads.

The core decompressor is `LZ4_decompress_generic()`. It is parameterized by end condition, early-end mode, dictionary mode, low-prefix/dictionary pointers, and dictionary size. OpenZFS uses the safe full-block, end-on-input, no-dictionary instantiation.

## Decompression Flow

`LZ4_decompress_generic()` validates null source and negative output size, initializes input/output bounds, and handles empty source/output special cases. If `LZ4_FAST_DEC_LOOP` is enabled and enough output room remains, it enters a fast loop that decodes common literal/match sequences using 16- or 32-byte wild copies guarded by distance and end checks.

Both fast and safe paths read a token, extend literal and match lengths through repeated `255` bytes, copy literals, read the 16-bit little-endian match offset, validate it, copy the match with short-offset overlap handling, and enforce LZ4 end-of-block restrictions. Malformed streams, invalid offsets, integer overflows, input overruns, or output overruns return a negative error.

## State And Dependencies

The decompressor is stateless across calls. It depends on `sys/zfs_context.h` for kernel/userland compatibility definitions such as `ASSERT`, `MIN`, memory helpers, and standard integer/memory facilities in non-kernel builds.

There is no OpenZFS-specific allocation, lock, cache, or global state in this file. Its ABI dependency is the legacy LZ4 symbol name consumed by `lz4_zfs.c`.

## Risks And Invariants

Callers must pass the exact compressed byte count and maximum decompressed block size. OpenZFS's wrapper enforces exact output length after this routine returns, so a short successful decode is treated as a ZFS decompression failure by the caller.

The file is performance-sensitive and heavily macro-driven. Correctness depends on preserving parsing restrictions, overflow checks, offset validation, and overlapping-copy cases.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/lz4.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/lz4_zfs.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/lz4_zfs.c

## Role

`lz4_zfs.c` is the OpenZFS-facing LZ4 compression module. It wraps LZ4 block compression/decompression in the `zio_compress` API, stores the exact compressed payload length in the on-disk compressed buffer, and provides the older LZ4 r85-derived compressor implementation used to produce ZFS LZ4 blocks.

The file declares `LZ4_uncompress_unknownOutputSize()` and relies on `lz4.c` for the newer safe decompressor.

## ZFS Compression API

- `zfs_lz4_compress_buf()` calls `real_LZ4_compress()` after a 32-bit size header. If compression returns zero, it reports failure by returning the source length. On success it writes the compressed byte count as big-endian and returns header plus payload size.
- `zfs_lz4_decompress_buf()` reads the big-endian compressed byte count, rejects sizes larger than the supplied compressed block, calls `LZ4_uncompress_unknownOutputSize()`, and requires the decoded byte count to equal `d_len`.
- `ZFS_COMPRESS_WRAP_DECL(zfs_lz4_compress)` and `ZFS_DECOMPRESS_WRAP_DECL(zfs_lz4_decompress)` expose the functions through OpenZFS's compression wrapper macros.

The `n` compression parameter is unused in both wrapper functions.

## Compressor Implementation

The embedded compressor defines architecture, endian, unaligned-access, bitcount, compiler, hash-table, and block-format macros. Key constants include `COMPRESSIONLEVEL 12`, `NOTCOMPRESSIBLE_CONFIRMATION 6`, `MINMATCH 4`, `MAX_DISTANCE 65535`, `RUN_MASK`, and `ML_MASK`.

Two compression paths share the same high-level algorithm:

- `LZ4_compressCtx()` uses a hash table of `HTYPE` entries and supports inputs beyond the 64 KiB small-block limit.
- `LZ4_compress64kCtx()` is selected for `isize < LZ4_64KLIMIT` and uses a `U16` hash table optimized for offsets within the 64 KiB LZ4 window.

Both paths search for repeated four-byte sequences, skip ahead on incompressible data, catch up matches backward when possible, encode literal runs and match lengths with extension bytes, write 16-bit little-endian match offsets, and finish by emitting the last literal run. They return zero if the destination limit would be exceeded.

## Allocation And Lifecycle

`real_LZ4_compress()` allocates a `struct refTables` context from global `lz4_cache`, zeroes it for deterministic hash-table state, chooses the 64 KiB or general compression routine, frees the context, and returns the compressed length or zero.

`lz4_init()` creates the reclaimable `kmem_cache_t` named `lz4_cache`. `lz4_fini()` destroys it and nulls the global pointer.

## State And Dependencies

This file depends on `sys/zfs_context.h` for kernel/userland compatibility primitives, allocation/cache APIs, assertions, endian helpers, memory functions, and integer types. It depends on `sys/zio_compress.h` for ZFS compressor wrapper declarations and return conventions. It depends on `lz4.c` for `LZ4_uncompress_unknownOutputSize()`.

The only persistent mutable state is global `lz4_cache`. Compression contexts are per-call.

## On-Disk Format Notes

The first four bytes of each ZFS LZ4 compressed payload store the exact compressed size in big-endian form. The LZ4 payload itself uses little-endian 16-bit match offsets. The stored size is necessary because ZFS compressed physical block sizes may be rounded to sector alignment.

Changing the compressor output format, size-header encoding, match-offset encoding, or final-literal behavior would affect on-disk compatibility. OpenZFS also requires exact full-block expansion to `d_len`.

## Risks And Invariants

`lz4_cache` must be initialized before compression, and contexts must be zeroed for deterministic output. `LZ4_compress64kCtx()` must only be used below `LZ4_64KLIMIT`; the dispatcher enforces that. Compressor paths rely on careful output-limit checks before token, literal, match-length, and final-literal writes.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/lz4_zfs.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/lzjb.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/lzjb.c

## Role

`lzjb.c` implements OpenZFS's private LZJB compressor and decompressor. The file keeps a ZFS-owned copy of the algorithm to protect the on-disk format from changes in shared platform compression code, remove checks unnecessary for ZFS's use case, and initialize the Lempel table deterministically so identical input blocks produce identical compressed output for deduplication.

## Compression API

`zfs_lzjb_compress_buf()` receives source and destination buffers, source and destination lengths, and an unused compression level parameter. It allocates a zeroed 1024-entry `uint16_t` Lempel table, then encodes the source as groups controlled by one-byte copy maps.

For each source position, it opens a copy-map byte every eight items, checks destination space, emits literals near the source end, hashes the next three bytes, looks up and updates the Lempel table, computes a bounded offset, verifies a valid three-byte match, and encodes matches as two-byte back-references. On destination overflow it frees the table and returns the source length.

## Decompression API

`zfs_lzjb_decompress_buf()` expands an LZJB stream into exactly `d_len` bytes. It reads copy-map bytes, copies literals directly, and decodes match entries into match length and offset. If a match offset points before the destination start, it returns `-1`; otherwise it copies from already produced output until the requested destination length is filled. The compressed input length and compression level parameters are unused.

`ZFS_COMPRESS_WRAP_DECL(zfs_lzjb_compress)` and `ZFS_DECOMPRESS_WRAP_DECL(zfs_lzjb_decompress)` expose the routines through OpenZFS's compressor framework.

## Constants And Format

The file defines `MATCH_BITS 6`, `MATCH_MIN 3`, `MATCH_MAX 66`, a 10-bit offset mask derived from a 16-bit encoded match word, and `LEMPEL_SIZE 1024`. The compressed stream alternates copy-map bytes with up to eight literal or match entries. A set copy-map bit means a two-byte back-reference; a clear bit means a one-byte literal.

## State And Dependencies

The implementation is stateless across calls. Compression allocates and frees a temporary zeroed Lempel table with `kmem_zalloc()` and `kmem_free()`. Decompression allocates no memory. The file depends on `sys/zfs_context.h` and `sys/zio_compress.h`.

## Risks And Invariants

The compressor intentionally returns `s_len` on destination overflow so the caller can treat the block as uncompressed. Deterministic output depends on the zeroed Lempel table at the start of every compression call.

The decompressor ignores `s_len` and stops only when `d_len` bytes have been produced. Its explicit corruption check is limited to rejecting back-references before `d_start`, so caller-level bounds and checksum validation are important for malformed-data handling.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/lzjb.c -->