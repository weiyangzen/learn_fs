# File Research: sources/block-storage/kvdo/vdo/forest.h

## Purpose
Declares block-map forest operations.

## API
- `vdo_entry_callback`: called for each allocated tree-node PBN during traversal.
- `vdo_get_tree_page_by_index()`
- `vdo_make_forest()`
- `vdo_free_forest()`
- `vdo_abandon_forest()`
- `vdo_replace_forest()`
- `vdo_traverse_forest()`

## Integration
The block map owns active and next forests and uses this API during growth, load/recovery, and metadata traversal.
