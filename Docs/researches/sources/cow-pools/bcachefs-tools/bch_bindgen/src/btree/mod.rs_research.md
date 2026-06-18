# File Research: sources/cow-pools/bcachefs-tools/bch_bindgen/src/btree/mod.rs

- Rust wrappers for bcachefs btree transactions, iterators, node iteration, and display.
- `BtreeTrans` owns a raw C transaction and drops by restarting/putting it to avoid pending restart BUG_ONs.
- Implements retry loops for transaction restarts and commit helpers analogous to C transaction macros.
- `BtreeIter` wraps C iter initialization, peeking, reverse peeking, slot-aware peeking, advancing, and `for_each` traversal with restart handling.
- `BtreeNodeIter` iterates btree nodes and advances by setting position to successor of node max key.
- Extends generated `btree` with fake-node checks, key iteration through unpacked node iterators, and text renderers.
