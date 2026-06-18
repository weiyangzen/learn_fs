# File Research: sources/block-storage/thin-provisioning-tools/src/cache/mapping.rs

Defines the on-disk cache mapping entry. Each entry packs an origin block and low-bit flags into one little-endian `u64`.

Key elements:
- `MAX_ORIGIN_BLOCKS = 1 << 48`.
- `MappingFlags`: `Valid = 1`, `Dirty = 2`.
- `Mapping { oblock: u64, flags: u32 }`.
- `is_valid`, `is_dirty`, and `set_dirty` helpers.

Encoding:
- On unpack, low 16 bits become flags and upper bits become `oblock`.
- On pack, writes `(oblock << 16) | flags`.
- `disk_size() == 8`.

This type is central to cache check, dump, restore, and writeback.
