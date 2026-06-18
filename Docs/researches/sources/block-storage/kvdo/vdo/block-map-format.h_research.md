# File Research: sources/block-storage/kvdo/vdo/block-map-format.h

## Purpose

Declares persisted block-map component format structures and sizing helpers.

## Contents

- `struct block_map_state_2_0`
  - flat page origin,
  - flat page count,
  - root origin,
  - root count.
- `struct boundary`
  - level page counts for `VDO_BLOCK_MAP_TREE_HEIGHT`.
- Extern declaration for `VDO_BLOCK_MAP_HEADER_2_0`.
- Decode, encode, encoded-size, page-count, and growth page-count APIs.

## Role

This is the storage-format contract between VDO layout metadata and the runtime block map.
