# File Research: sources/block-storage/thin-provisioning-tools/src/pdata/btree_leaf_walker.rs

Walks only btree leaf blocks while tracking references in a mutable `SpaceMap`. `LeafVisitor<V>` receives key ranges and leaf block locations, with a `visit_again` hook for shared nodes.

`LeafWalker` computes tree depth, increments metadata counts, avoids repeated leaf IO via a `FixedBitSet`, validates node checksum and structure, and returns the collected leaf bitset. It is stricter about uniform depth and reports contextual btree errors on IO/checksum/layout failures.
