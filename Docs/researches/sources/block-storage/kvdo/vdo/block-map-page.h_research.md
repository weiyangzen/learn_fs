# File Research: sources/block-storage/kvdo/vdo/block-map-page.h

## Purpose

Defines the block map page layout and validation API.

## Contents

- `struct block_map_page_header`
  - nonce,
  - PBN,
  - unused fields,
  - initialized bit.
- `struct block_map_page`
  - packed version,
  - page header,
  - flexible array of block map entries.
- `enum block_map_page_validity`.
- Inline helpers:
  - check initialized bit,
  - set initialized bit,
  - get page PBN.
- Declarations for page formatting and validation.

## Role

This header defines the per-page storage unit used by both block map leaf pages and interior tree pages.
