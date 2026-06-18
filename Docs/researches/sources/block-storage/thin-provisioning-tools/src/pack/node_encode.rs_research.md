# File Research: sources/block-storage/thin-provisioning-tools/src/pack/node_encode.rs

This file packs recognized metadata block layouts into the pack VM format.

Important behavior:
- Defines `PackError` for parse and write failures.
- Parses B-tree node headers enough to identify leaf/internal node, max entries, and value size.
- `pack_btree_node()` emits:
  - literal header,
  - packed u64 keys,
  - packed shifted u64 values for leaf nodes with u64 values,
  - packed u64 values for internal nodes,
  - literal tail data when needed.
- Superblock, bitmap, index, and array packers currently emit literal bytes.

Integration points:
- Used by pack toplevel and spindle metadata cache packing.
- Delegates numeric compression to `pack::vm`.

Risks and notes:
- Non-u64 leaf values are not semantically packed; their tail is emitted literally.
- Parse failures are generic `ParseError`.
