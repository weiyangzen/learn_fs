# File Research: sources/block-storage/kvdo/vdo/geometry.h

## Purpose
Defines UDS index geometry fields, defaults, and helper predicates.

## Main Structure
`struct geometry` stores primary layout inputs plus derived values: pages per volume/chapter, bytes per volume, records per page/chapter/volume, delta lists, mean delta, payload/address bits, sparse/dense chapter counts, and remap metadata.

## Constants
Defines default page size, records per page/chapter, chapters per volume, sparse chapter defaults, delta-list bits, mean delta bits, and open-chapter load ratio.

## API
- `make_geometry()`, `copy_geometry()`, `free_geometry()`
- `map_to_physical_chapter()`
- `is_reduced_geometry()`, `is_sparse_geometry()`
- `has_sparse_chapters()`, `is_chapter_sparse()`
- `chapters_to_expire()`

## Integration
Consumed by hash utilities, chapter index logic, and index volume layout code.
