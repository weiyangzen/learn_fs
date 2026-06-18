# File Research: sources/block-storage/kvdo/vdo/compressed-block.c

## Purpose

Implements compressed block header initialization, fragment lookup, and fragment insertion.

## Main Responsibilities

- Defines compressed block format version 1.0.
- Initializes a compressed block header and first fragment size.
- Validates and locates a compressed fragment by mapping state.
- Copies a fragment into a compressed block and records its size.

## Important Functions

- `vdo_initialize_compressed_block()` asserts header layout size, writes version, and sets slot 0 size.
- `vdo_get_compressed_block_fragment()` validates compressed state, version, slot number, accumulated offsets, and size bounds.
- `vdo_put_compressed_block_fragment()` records fragment size and copies data into the data area.

## Behavior Details

Fragment offsets are computed by summing sizes of earlier slots. If the computed offset or fragment extent exceeds the compressed block data area, lookup returns `VDO_INVALID_FRAGMENT`.

## Notable Edge Cases

- Non-compressed mapping states are invalid for fragment lookup.
- `vdo_put_compressed_block_fragment()` intentionally performs no bounds checking; callers must ensure the fragment fits.
