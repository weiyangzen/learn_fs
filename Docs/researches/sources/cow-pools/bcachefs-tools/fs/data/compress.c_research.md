# File Research: sources/cow-pools/bcachefs-tools/fs/data/compress.c

Implements extent-level compression/decompression for lz4, gzip, and zstd, plus compression option parsing and workspace initialization.

Key responsibilities:
- Documents compression behavior: per-file/per-directory, extent granularity up to encoded extent max, random-read tradeoffs, and background recompression.
- Implements bounce-buffer handling for bio memory that may be non-contiguous or highmem-backed.
- Implements `buf_uncompress()` for lz4, gzip, and zstd, including workspace-pool lookup and superblock feature repair paths.
- Implements `bch2_bio_uncompress_inplace()` and `bch2_bio_uncompress()` to decompress into bios and normalize extent CRC metadata after in-place decompression.
- Implements `attempt_compress()` and `bch2_compress()` for lz4/lz4hc, gzip, and zstd.
- Pads compressed output to block size and marks data incompressible when compression does not shrink enough.
- Optional `verify_compress` immediately decompresses and compares compressed output.
- Tracks compression feature bits and lazily initializes missing compression workspaces if fsck allows repairing the superblock feature set.
- Initializes/exits compression workspace and bounce mempools.
- Parses and formats compression options in `type[:level]` form with levels up to 15.

Important interactions:
- Uses `bch2_check_set_has_compressed_data()` to set compression feature bits in the superblock and allocate workspace pools.
- Compression is limited by `c->opts.encoded_extent_max`.
- zstd stores the exact compressed byte length in the first 4 bytes because sector-rounded compressed size is insufficient for decompression.

Notable concerns:
- zstd compression subtracts a 7-byte “fudge factor” for a noted zstd overrun behavior.
- If compression workspace is not initialized and fsck repair is declined, compression/decompression returns bcachefs-specific errors.
- `bch2_bio_uncompress_inplace()` assumes caller allocated enough bio vectors; comment notes the assertion is indirect.
