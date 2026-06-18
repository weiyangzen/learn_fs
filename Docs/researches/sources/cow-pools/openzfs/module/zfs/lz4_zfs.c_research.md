# File Research: sources/cow-pools/openzfs/module/zfs/lz4_zfs.c

## Role

`lz4_zfs.c` is the OpenZFS-facing LZ4 compression module. It wraps LZ4 block compression/decompression in the `zio_compress` API, stores the exact compressed payload length in the on-disk compressed buffer, and provides the older LZ4 r85-derived compressor implementation used to produce ZFS LZ4 blocks.

The file deliberately separates compression from decompression implementation: it declares `LZ4_uncompress_unknownOutputSize()` and relies on `lz4.c` for the newer safe decompressor.

## ZFS Compression API

- `zfs_lz4_compress_buf()` calls `real_LZ4_compress()` into the destination buffer after a 32-bit size header. If compression returns zero, it reports failure by returning the source length, matching ZFS compressor convention for "store uncompressed instead". On success it writes the compressed byte count as big-endian at the front of the destination and returns `sizeof (uint32_t) + bufsiz`.
- `zfs_lz4_decompress_buf()` reads the big-endian compressed byte count from the buffer, rejects encoded sizes larger than the supplied compressed block, calls `LZ4_uncompress_unknownOutputSize()` on the payload, and requires the decoded byte count to equal the requested destination length exactly.
- `ZFS_COMPRESS_WRAP_DECL(zfs_lz4_compress)` and `ZFS_DECOMPRESS_WRAP_DECL(zfs_lz4_decompress)` expose the functions through OpenZFS's compression wrapper macros.

The `n` compression parameter is unused in both wrapper functions.

## Compressor Implementation

The embedded compressor is based on old LZ4 code with illumos/OpenZFS adjustments. It defines architecture, endian, unaligned-access, bitcount, compiler, hash-table, and block-format macros. The key constants are `COMPRESSIONLEVEL 12`, `NOTCOMPRESSIBLE_CONFIRMATION 6`, `MINMATCH 4`, `MAX_DISTANCE 65535`, `RUN_MASK`, `ML_MASK`, and the LZ4 literal/match limits.

Two compression paths share the same high-level algorithm:

- `LZ4_compressCtx()` uses a hash table of `HTYPE` entries and supports inputs beyond the 64 KiB small-block limit. On 64-bit builds table entries are stored relative to a base pointer; on 32-bit builds they are pointers.
- `LZ4_compress64kCtx()` is selected for `isize < LZ4_64KLIMIT` and uses a `U16` hash table optimized for offsets within the 64 KiB LZ4 window.

Both paths search for repeated four-byte sequences, progressively skip ahead on incompressible data, catch up matches backward when possible, encode literal runs and match lengths with extension bytes, write 16-bit little-endian match offsets, and finish by emitting the last literal run. They return zero if the destination limit would be exceeded.

## Allocation And Lifecycle

`real_LZ4_compress()` allocates a `struct refTables` context from the global `lz4_cache`, zeroes it for deterministic hash-table state, chooses the 64 KiB or general compression routine, frees the context, and returns the compressed length or zero. A null allocation gently disables compression for that block by returning zero.

`lz4_init()` creates the reclaimable `kmem_cache_t` named `lz4_cache`, sized to `struct refTables`. `lz4_fini()` destroys the cache and nulls the global pointer if it exists.

## State And Dependencies

This file depends on `sys/zfs_context.h` for kernel/userland compatibility primitives, allocation/cache APIs, assertions, endian helpers, memory functions, and integer types. It depends on `sys/zio_compress.h` for ZFS compressor wrapper declarations and return conventions. It depends on `lz4.c` for `LZ4_uncompress_unknownOutputSize()`.

The only persistent mutable state is the global `lz4_cache`. Compression contexts are per-call and returned to the cache before exit.

## On-Disk Format Notes

The first four bytes of each ZFS LZ4 compressed payload store the exact compressed size in big-endian form. The LZ4 payload itself uses little-endian 16-bit match offsets per the LZ4 block format. The stored size is necessary because ZFS compressed physical block sizes may be rounded to sector alignment and therefore can be larger than the actual LZ4 stream.

Changing the compressor output format, size-header encoding, match-offset encoding, or final-literal behavior would affect on-disk compatibility. The decompressor side is stricter than raw LZ4 success: OpenZFS requires exact full-block expansion to `d_len`.

## Risks And Invariants

`lz4_cache` must be initialized before compression, and contexts must be zeroed for deterministic output. `LZ4_compress64kCtx()` must only be used below `LZ4_64KLIMIT`; the dispatcher enforces that. All compressor paths rely on careful output-limit checks before token, literal, match-length, and final-literal writes.

The compressor uses packed/unaligned memory access macros and architecture-specific word comparisons. Portability changes need particular care around big-endian compatibility, strict-alignment CPUs, and kernel compiler builtins.
