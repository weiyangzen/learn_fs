# File Research: sources/block-storage/vdo/utils/vdo/messageStatsReader.c

Parses text-form VDO statistics into `struct vdo_statistics`.

Key details:
- Uses small helpers `skip_string()`, `read_u64()`, `read_u32()`, `read_block_count_t()`, `read_string()`, `read_bool()`, and `read_u8()`.
- Contains generated-style readers for nested stats groups: allocator, commit, recovery journal, packer, slab journal, slab summary, ref counts, block map, hash lock, errors, bio stats, memory usage, and index stats.
- `read_vdo_statistics()` walks the complete expected stats message in order and populates all fields in `struct vdo_statistics`.
- Public entry point is `read_vdo_stats(char *buf, struct vdo_statistics *stats)`.

Risk notes:
- Parsing is tightly coupled to exact field labels and expected order; missing or renamed fields return `VDO_UNEXPECTED_EOF`.
- `skip_string()` uses `strstr` from the current pointer, so it can skip over unexpected intervening text rather than enforcing immediate field adjacency.
- Some integer readers use `%lu` for `u64`/`block_count_t`, which assumes the typedef layout matches `unsigned long` on the build target.
