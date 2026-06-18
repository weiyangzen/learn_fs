# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/compress.c

Implements data compression/decompression for extents, plus compression option parsing and workspace initialization. Supported algorithms are lz4, gzip, and zstd, with incompressible tagging.

Key entry points:
- `bch2_bio_compress()` maps or bounces source/destination bios, compresses, and returns on-disk compression type.
- `bch2_bio_uncompress()` and `bch2_bio_uncompress_inplace()` decompress encoded extents into target bios.
- `bch2_fs_compress_init()` and `bch2_fs_compress_exit()` manage bounce/workspace mempools.
- `bch2_opt_compression_parse()` parses `type[:level]` option strings.

Important details:
- `bio_map_or_bounce()` prefers direct contiguous mapping, then vmap, then bounce buffers.
- Zstd stores exact compressed length in the first 4 bytes because sector padding cannot be passed to the zstd decompressor.
- Compression retries with smaller source sizes when output does not fit, aligned to filesystem block size.
- Optional `verify_compress` immediately decompresses and compares output for debugging.
- Superblock compression feature bits are lazily set when compressed data is encountered or configured.

Dependencies and interactions:
- Uses checksum/extent CRC fields to describe encoded extents.
- Uses filesystem `encoded_extent_max`, block size, and compression feature flags.
- On missing workspace for an on-disk compression type, may invoke fsck-style repair to mark the feature in the superblock.
