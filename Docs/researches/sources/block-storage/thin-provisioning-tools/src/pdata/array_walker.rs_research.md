# File Research: sources/block-storage/thin-provisioning-tools/src/pdata/array_walker.rs

Implements `ArrayWalker` and `ArrayVisitor<V>`. It walks the btree that maps array indices to array-block locations, then reads and unpacks each `ArrayBlock<V>` through `BlockValueVisitor`.

The walker verifies contiguous array indices, validates array block checksum type, increments a supplied or restricted metadata space map for visited array blocks, and accumulates array plus btree errors into `ArrayError::Aggregate` when needed. It also provides `collect_array_blocks_with_path`, which returns index-to-`(path, block)` mappings without reading array block payloads.
