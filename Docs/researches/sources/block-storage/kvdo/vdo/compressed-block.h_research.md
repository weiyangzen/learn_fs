# File Research: sources/block-storage/kvdo/vdo/compressed-block.h

## Purpose

Defines the compressed block on-disk overlay and compressed-fragment API.

## Contents

- `struct compressed_block_header`
  - packed version,
  - little-endian fragment sizes for all compression slots.
- `VDO_COMPRESSED_BLOCK_DATA_SIZE`.
- `VDO_MAX_COMPRESSED_FRAGMENT_SIZE`.
- `struct compressed_block`
  - header,
  - data area.
- APIs for fragment lookup, initialization, clearing unused slots, and fragment insertion.

## Role

This header defines how multiple compressed logical fragments are packed into one VDO block.

## Notable Details

A compressed block is only worthwhile if at least two fragments fit, so a fragment that fills the entire data area is considered too large.
