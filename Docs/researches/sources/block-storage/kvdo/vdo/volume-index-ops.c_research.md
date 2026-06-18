# File Research: sources/block-storage/kvdo/vdo/volume-index-ops.c

## Purpose
Provides format-dispatch wrappers for UDS volume index creation, save/load sizing, save, load, and combined statistics.

## Key Behavior
- Sparse configurations use volume index 006 operations.
- Dense configurations use volume index 005 operations.
- `get_volume_index_combined_stats()` merges dense and sparse stats fields into one aggregate.
- `compute_volume_index_save_blocks()` computes format-specific save bytes, adds `delta_list_save_info`, rounds to blocks, and adds `MAX_ZONES` guard capacity.
- `save_volume_index()` saves each zone sequentially, writes guard delta lists, and flushes each writer.
- `load_volume_index()` starts restore, finishes restore, validates guard delta lists, and aborts restore on failure after start.

## Key Functions
- `make_volume_index()`
- `compute_volume_index_save_blocks()`
- `save_volume_index()`
- `load_volume_index()`
- `get_volume_index_combined_stats()`

## Important Invariant
Save/load correctness depends on the sparse/dense dispatch matching the geometry used to create the volume index.
