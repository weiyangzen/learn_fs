# File Research: sources/block-storage/kvdo/vdo/forest.c

## Purpose
Builds, expands, replaces, frees, and traverses the VDO block-map forest, which is a set of segmented block-map trees.

## Main Behavior
- `vdo_make_forest()` computes needed tree pages for a requested entry count and builds a new segment if expansion is required.
- `make_segment()` allocates boundaries, page arrays, segment arrays per root, formats root pages, and links each level’s contiguous page region.
- `vdo_abandon_forest()` discards prepared-but-unused expansion.
- `vdo_replace_forest()` swaps a prepared larger forest into active use.
- `vdo_get_tree_page_by_index()` locates a tree page by root, height, and page index across forest segments.
- `vdo_traverse_forest()` launches one cursor per root and walks block-map tree pages asynchronously via metadata VIOs.
- Traversal repairs invalid or out-of-range mapped entries by marking them unmapped and writing the tree page.

## Dependencies
Uses block-map tree/page helpers, dirty lists, recovery/slab journal dependencies, VIO pool, metadata submitter, constants, and VDO completion callbacks.

## Invariants
The forest may have multiple segments from expansion. Traversal uses boundary calculations to avoid keeping mappings past current logical space and calls a supplied callback for allocated non-leaf node PBNs.
