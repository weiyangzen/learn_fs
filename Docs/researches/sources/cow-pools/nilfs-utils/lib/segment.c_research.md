# File Research: sources/cow-pools/nilfs-utils/lib/segment.c

## Scope

Provides iterators and validation for NILFS segment buffers: partial segment summaries, per-file summary records, and per-block binfo records.

## APIs And Behavior

- `nilfs_psegment_init()`, `nilfs_psegment_is_end()`, and `nilfs_psegment_next()` walk partial segments inside a full segment buffer.
- `nilfs_psegment_is_valid()` checks segment summary magic, summary checksum, summary byte bounds, 8-byte header alignment, partial segment block count bounds, and summary-block sizing.
- `nilfs_file_init()`, `nilfs_file_is_end()`, and `nilfs_file_next()` walk `nilfs_finfo` records inside a partial segment summary, accounting for block-boundary padding.
- `nilfs_file_info_size()` calculates combined finfo and binfo footprint using different binfo formats for DAT versus non-DAT files.
- `nilfs_block_init()`, `nilfs_block_is_end()`, and `nilfs_block_next()` walk binfo entries for data and node blocks, again respecting padding at block boundaries.
- `nilfs_psegment_strerror()` and `nilfs_file_strerror()` expose stable messages for iterator error codes.

## State And Dependencies

The iterators operate over caller-owned `struct nilfs_segment` memory, store offsets and logical block numbers in `nilfs_psegment`, `nilfs_file`, and `nilfs_block`, and depend on NILFS on-disk summary formats plus CRC32.

## Risks And Invariants

All bounds checks depend on `sumbytes`, `ss_nblocks`, `fi_nblocks`, and `fi_ndatablk` being validated before consumers dereference deeper records. DAT files use real block offsets while other files use virtual block numbers; mixing those binfo formats would corrupt traversal. The code reports malformed data by setting iterator error fields and `errno=EINVAL`.
