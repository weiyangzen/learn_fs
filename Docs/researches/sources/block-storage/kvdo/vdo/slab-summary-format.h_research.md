# File Research: sources/block-storage/kvdo/vdo/slab-summary-format.h

Defines the compact on-disk per-slab summary entry.

Key type:
- `tail_block_offset_t`: `uint8_t`, offset of the slab journal tail block.

`struct slab_summary_entry` packs:
- tail block offset,
- 6-bit fullness hint,
- `load_ref_counts` bit,
- `is_dirty` bit.

Helpers:
- `vdo_get_slab_summary_zone_size()` computes blocks per summary zone as `MAX_VDO_SLABS / entries_per_block`.
- `vdo_get_slab_summary_size()` multiplies zone size by `MAX_VDO_PHYSICAL_ZONES`.
- `vdo_get_slab_summary_hint_shift()` computes how much to shift free-block counts down to fit in the 6-bit fullness hint.

The summary is used by allocator load, slab journal decode, scrub decisions, and fast approximate free-space ordering.
