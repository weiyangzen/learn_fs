# File Research: sources/cow-pools/bcachefs-tools/fs/data/compress.h

Public interface and packed option representation for compression.

Key responsibilities:
- Maps compression option enum values to on-disk compression types.
- Defines `union bch_compression_opt` as an 8-bit value split into 4-bit type and 4-bit level, endian-aware.
- Validates compression options, rejecting nonzero level with `none`.
- Declares bio compression/decompression APIs, workspace init/exit, feature-setting helper, and option parse/format/validate APIs.
- Defines `bch2_opt_compression` option function table.

Important interactions:
- The 4-bit level field matches the `0..15` parser limit in `compress.c`.
- Compression option-to-type mapping feeds checksum/extent metadata and compression workspaces.
