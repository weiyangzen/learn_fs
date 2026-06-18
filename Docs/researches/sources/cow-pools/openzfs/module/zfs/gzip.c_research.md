# File Research: sources/cow-pools/openzfs/module/zfs/gzip.c

## Role

Implements the ZFS gzip compression and decompression backend, using kernel zlib wrappers in kernel builds, userspace zlib otherwise, and optional QAT hardware acceleration.

## Key Functions

- `zfs_gzip_compress_buf()` compresses a source buffer into a destination buffer at the requested gzip level.
  - Asserts destination length is no larger than source length.
  - Tries QAT compression when the buffer size qualifies.
  - Treats QAT incompressible status or software compression failure as uncompressed output when destination size equals source size.
  - Returns the compressed size or source length for incompressible/fallback-copy cases.
- `zfs_gzip_decompress_buf()` decompresses into an expected output size.
  - Tries QAT decompression when suitable.
  - Falls back to software decompression.
  - Requires the decompressed byte count to exactly match `d_len`.
- `ZFS_COMPRESS_WRAP_DECL(zfs_gzip_compress)` and `ZFS_DECOMPRESS_WRAP_DECL(zfs_gzip_decompress)` expose the level-specific compressor/decompressor wrapper set expected by the ZFS compression table.

## Build Differences

Kernel builds use `z_compress_level()` and `z_uncompress()` from `zmod`; userspace builds use zlib `compress2()` and `uncompress()`.

## Research Notes

The backend relies on the wider ZFS compression wrapper macros for the public entry points. The local logic is focused on accelerator fallback and strict decompressed-size validation.
