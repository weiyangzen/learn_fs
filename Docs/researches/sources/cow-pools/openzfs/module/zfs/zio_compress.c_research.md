# File Research: sources/cow-pools/openzfs/module/zfs/zio_compress.c

Read coverage: complete file, 181 lines.

Purpose: compression algorithm registry and helper selection/wrapper functions for ZIO compression and decompression.

Main responsibilities:
- Defines `zio_compress_table[]`, mapping compression IDs to names, default levels, compression functions, decompression functions, and optional decompression-with-level functions.
- Implements policy selection for inherited/on compression and compression levels.
- Provides generic `zio_compress_data()` and `zio_decompress_data()` wrappers used by `zio.c`.
- Maps compression algorithms to required SPA features with `zio_compress_to_feature()`.

Compression table:
- Policy/non-compression entries: `inherit`, `on`, `uncompressed`, `empty`.
- Algorithms: `lzjb`, `gzip-1` through `gzip-9`, `zle`, `lz4`, `zstd`.
- `zle` uses level/parameter `64`.
- `zstd` uses `ZIO_ZSTD_LEVEL_DEFAULT` and supports a level-aware decompressor.

Selection behavior:
- `zio_compress_select()` resolves `inherit` to parent and `on` to LZ4 if `SPA_FEATURE_LZ4_COMPRESS` is active, otherwise legacy LZJB.
- `zio_complevel_select()` returns zero for algorithms without levels; otherwise resolves level inheritance.

Compression wrapper:
- `zio_compress_data()` asserts an executable compressor, resolves ZSTD levels, allocates a destination ABD matching source layout when needed, calls the compressor, and returns original size when compression fails to fit the requested maximum.
- `zio_decompress_data()` validates the algorithm and dispatches to either a level-aware decompressor or the ordinary decompressor.

Key dependencies:
- Used by `zio_write_compress()` for write-side compression and by read/decrypt paths for decompression.
- Algorithm functions are supplied by OpenZFS compression modules, including ZLE from `zle.c`.
