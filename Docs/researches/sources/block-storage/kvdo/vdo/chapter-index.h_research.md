# File Research: sources/block-storage/kvdo/vdo/chapter-index.h

## Purpose

Declares chapter index structures and APIs for UDS deduplication metadata.

## Contents

- `NO_CHAPTER_INDEX_ENTRY = -1`.
- `struct open_chapter_index`
  - geometry,
  - delta index,
  - virtual chapter number,
  - volume nonce,
  - memory allocation count.
- APIs to create/free/reset open chapter indexes.
- APIs to insert records, pack pages, initialize/validate packed pages, and search pages.

## Role

This header is the interface between chapter-building code and delta-index-backed chapter index storage.
