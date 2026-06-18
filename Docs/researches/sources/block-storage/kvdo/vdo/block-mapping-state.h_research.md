# File Research: sources/block-storage/kvdo/vdo/block-mapping-state.h

## Purpose

Defines the four-bit mapping state values stored in each block map entry.

## Contents

- `VDO_MAPPING_STATE_UNMAPPED = 0`.
- `VDO_MAPPING_STATE_UNCOMPRESSED = 1`.
- `VDO_MAPPING_STATE_COMPRESSED_BASE = 2`.
- `VDO_MAPPING_STATE_COMPRESSED_MAX = 15`.
- `VDO_MAX_COMPRESSION_SLOTS`, derived from compressed state range.
- Inline conversion helpers:
  - slot to state,
  - state to slot,
  - compressed-state test.

## Role

This header defines how VDO distinguishes unmapped, normal, and compressed logical mappings inside compact block map entries.
