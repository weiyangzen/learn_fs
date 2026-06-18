# File Research: sources/block-storage/vdo/utils/vdo/parseUtils.c

Implements CLI/config parsing helpers for VDO user tools.

Key details:
- `parseUInt()` parses unsigned integers with inclusive lower/upper bounds.
- `parseInt()` parses signed integers.
- `parseUInt64()` parses base-10 unsigned 64-bit values.
- `parseSize()` parses byte sizes with optional binary unit suffixes `B`, `K`, `M`, `G`, `T`, `P`; LVM mode defaults unitless values to MiB, otherwise bytes.
- `parseIndexConfig()` converts sparse and memory-size strings into UDS `index_config`, defaulting memory to 256 MB.
- Memory parser accepts fractional strings `0.25`, `0.5`/`0.50`, and `0.75` plus integer values.

Risk notes:
- `parseUInt64()` does not explicitly check `endPtr == arg`, so an empty/non-numeric string can depend on `strtoull` behavior rather than a direct empty-input check.
