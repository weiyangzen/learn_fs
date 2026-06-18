# File Research: sources/block-storage/kvdo/vdo/geometry.c

## Purpose
Computes and manages UDS index-volume geometry: chapter/page/record counts, delta-index sizing parameters, sparse/dense chapter behavior, and remapped chapter handling.

## Main Behavior
- `make_geometry()` allocates a geometry object, stores input parameters, and derives records/pages/volume bytes, chapter index pages, delta-list counts, address bits, and payload bits.
- `copy_geometry()` recreates an equivalent geometry.
- `map_to_physical_chapter()` maps virtual chapters to physical chapters, including reduced geometry with a remapped physical chapter 0.
- `has_sparse_chapters()` and `is_chapter_sparse()` decide whether sparse chapters are active for a virtual-chapter range.
- `chapters_to_expire()` decides how many chapters to expire when opening a new chapter, including remapped-chapter exceptions.

## Dependencies
Uses `delta-index` sizing, `compute_bits()`, geometry constants, allocation, and logging/assertion infrastructure.

## Invariants
Derived fields depend on record size, page size, record pages per chapter, and sparse chapter count. Reduced geometry is detected by an odd `chapters_per_volume`.
