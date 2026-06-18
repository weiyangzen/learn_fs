# File Research: sources/block-storage/kvdo/vdo/reference-count-rebuild.h

Small public interface for block-map-based reference-count rebuild.

Exports:
- `vdo_rebuild_reference_counts(struct vdo *vdo, struct vdo_completion *parent, block_count_t *logical_blocks_used, block_count_t *block_map_data_blocks)`

The function asynchronously rebuilds refcounts and reports:
- number of mapped logical blocks observed,
- number of block-map data/tree blocks referenced,
- completion result through the parent completion.
