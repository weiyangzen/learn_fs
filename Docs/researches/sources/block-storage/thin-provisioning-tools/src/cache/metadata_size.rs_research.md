# File Research: sources/block-storage/thin-provisioning-tools/src/cache/metadata_size.rs

Estimates cache metadata device size and validates cache block size constraints.

Key behavior:
- Accepts `CacheMetadataSizeOptions { nr_blocks, max_hint_width }`.
- `check_cache_block_size` requires block size to be a nonzero multiple of 32 KiB and at most 1 GiB.
- `metadata_size` estimates:
  - 16 bytes per mapped cache block.
  - 4 MiB transaction overhead.
  - hint size as `nr_blocks * (max_hint_width + 8)`.
- Caps estimate at `MAX_METADATA_BLOCKS * BLOCK_SIZE`.

This is calculation-only and does no device I/O.
