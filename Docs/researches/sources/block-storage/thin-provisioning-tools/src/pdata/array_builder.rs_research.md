# File Research: sources/block-storage/thin-provisioning-tools/src/pdata/array_builder.rs

This file builds persistent arrays from ordered sparse/indexed values.

Important components:
- `ArrayBlockBuilder<V>` buffers values into array blocks.
- `ArrayBuilder<V>` builds array blocks plus a B-tree mapping array-block indexes to block locations.
- `ArrayIO<V>` writes packed array blocks through `WriteBatcher`.

Important behavior:
- `push_value()` enforces bounds and increasing array index order.
- Gaps within the current block are filled with `Default::default()`.
- `complete()` emits all remaining blocks, including default-filled trailing blocks.
- `ArrayBuilder::complete()` builds a B-tree index over emitted array block locations and returns its root.
- `write_array_block()` allocates a metadata block, packs the array block, writes it with checksum type `BT::ARRAY`, and returns its location.

Integration points:
- Used by era restore to build writeset bitset arrays and era arrays.
- Depends on `WriteBatcher`, B-tree builder, checksum, math, and array packing.

Risks and notes:
- Out-of-order insertion is rejected.
- Empty arrays may produce no array blocks depending on capacity; callers should understand expected array size semantics.
