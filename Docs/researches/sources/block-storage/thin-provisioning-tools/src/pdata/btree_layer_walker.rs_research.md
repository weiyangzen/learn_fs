# File Research: sources/block-storage/thin-provisioning-tools/src/pdata/btree_layer_walker.rs

Provides batched/layered btree reading backed by `Aggregator`. `read_internal_nodes` walks internal levels breadth-first using `BufferPool`, marks nodes through `Aggregator::test_and_inc`, and avoids revisiting already-seen children. `LeafHandler` then reads leaf nodes and forwards them to a `NodeVisitor`.

`read_nodes` combines both phases, and `btree_to_map_with_aggregator` collects leaf key/value pairs using `ValueCollector`. This is optimized for loading space maps and large trees with fewer duplicate reads.
