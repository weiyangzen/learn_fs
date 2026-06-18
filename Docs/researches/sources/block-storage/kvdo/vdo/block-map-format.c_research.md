# File Research: sources/block-storage/kvdo/vdo/block-map-format.c

## Purpose

Implements encode/decode and size calculations for the persisted VDO block map component state.

## Main Responsibilities

- Defines `VDO_BLOCK_MAP_HEADER_2_0`.
- Decodes block map state version 2.0 from a `struct buffer`.
- Encodes block map state version 2.0 into a `struct buffer`.
- Computes encoded block map component size.
- Computes number of block map leaf pages needed for a logical entry count.
- Computes additional forest pages needed when growing the block map.

## Important Functions

- `vdo_decode_block_map_state_2_0()` validates header, reads flat/root fields, asserts flat-page invariants, and fills state.
- `vdo_get_block_map_encoded_size()` returns encoded header plus state size.
- `vdo_encode_block_map_state_2_0()` writes header and state fields.
- `vdo_compute_block_map_page_count()` rounds logical entries to block map pages.
- `vdo_compute_new_forest_pages()` calculates per-level tree sizes and total new non-leaf pages.

## Behavior Details

The decoded flat-page origin must equal `VDO_BLOCK_MAP_FLAT_PAGE_ORIGIN`, and flat-page count must be zero. The code comments note the flat-page count has effectively always been zero.

Forest growth uses leaf page count, root count, and `VDO_BLOCK_MAP_ENTRIES_PER_PAGE` to compute page counts at each interior level, optionally subtracting old level sizes.

## Dependencies

Uses the generic `buffer` little-endian helpers, VDO headers, constants, and assertion/status helpers.
