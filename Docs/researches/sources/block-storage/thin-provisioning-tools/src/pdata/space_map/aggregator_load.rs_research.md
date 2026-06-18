# File Research: sources/block-storage/thin-provisioning-tools/src/pdata/space_map/aggregator_load.rs

Loads serialized disk or metadata space maps into `Aggregator`. `SmType` selects data-space-map index gathering through a btree or metadata-space-map index gathering through the metadata index block.

`read_space_map` gathers index entries, reads bitmap blocks with `BufferPool` and `IndexHandler`, sets nonzero small counts in an aggregator, then walks the overflow ref-count btree with layered `read_nodes` to patch large counts. It also increments metadata-sm counts for index/bitmap metadata blocks. Public wrappers are `read_data_space_map` and `read_metadata_space_map`.
