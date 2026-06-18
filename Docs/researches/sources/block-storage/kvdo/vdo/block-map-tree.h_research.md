# File Research: sources/block-storage/kvdo/vdo/block-map-tree.h

## Purpose

Declares block map tree page structures and tree-zone APIs.

## Contents

- `struct tree_page`
  - waiter,
  - dirty-list entry,
  - generation,
  - writing state/generation,
  - recovery lock and writing recovery lock,
  - page buffer.
- Extern `VDO_INVALID_PBN`.
- Inline `vdo_as_block_map_page()`.
- Declarations for:
  - page validation/copy,
  - tree-zone init/uninit,
  - period management,
  - active/drain checks,
  - PBN lookup,
  - page PBN lookup,
  - tree page write scheduling.

## Role

This header exposes interior tree management to the broader block map subsystem.
