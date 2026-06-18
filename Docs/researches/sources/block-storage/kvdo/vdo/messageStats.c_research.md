# File Research: sources/block-storage/kvdo/vdo/messageStats.c

## Purpose
Serializes a fetched `struct vdo_statistics` snapshot into a text buffer.

## Structure
The file is a hierarchy of writer helpers:
- Primitive writers: `write_uint64_t`, `write_uint32_t`, `write_block_count_t`, `write_string`, `write_bool`, `write_uint8_t`.
- Nested statistics writers for allocator, commits, recovery journal, packer, slab journal, slab summary, ref counts, block map, hash lock, errors, bios, memory usage, index, and full VDO stats.
- Public entry point: `vdo_write_stats`.

## Output Model
Writers emit a brace-delimited, field-name text representation such as `field : value`. Each helper takes `char **buf` and `unsigned int *maxlen`, writes with `scnprintf`, advances the buffer pointer, decrements remaining length, and returns `VDO_UNEXPECTED_EOF` on truncation/error.

## Data Coverage
`write_vdo_statistics` serializes core capacity, logical/physical block counts, recovery state, mode, packer stats, allocator stats, journal stats, block-map stats, dedupe/hash-lock stats, error stats, VIO counts, flush counts, logical block size, many bio counters, memory usage, and UDS index stats.

## Integration Notes
`vdo_write_stats` allocates a temporary `struct vdo_statistics`, calls `vdo_fetch_statistics`, serializes it, then frees it. This file depends on `statistics.h`, `thread-device.h`, `vdo.h`, and the allocation wrappers.

## Risk Note
The truncation pattern compares `count` after decrementing `*maxlen`; that can report `VDO_UNEXPECTED_EOF` when a write consumes more than half of the remaining buffer, even if `scnprintf` did not truncate. If this file is behaviorally important, that check deserves review against intended kernel `scnprintf` semantics.
