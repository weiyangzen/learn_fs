# File Research: sources/block-storage/thin-provisioning-tools/src/pdata/array_walker/tests.rs

Uses mock `ArrayVisitor` expectations to validate that `ArrayWalker` visits all undamaged array blocks in order. The fixture builds large arrays via `array_builder::test_utils`, tracks damaged btree nodes and array blocks, and computes expected surviving values.

Coverage includes clean arrays, trashed root, first/last damaged leaf, first/last damaged array block, damaged array-block ranges, and combined btree-node plus array-block damage. Tests emphasize partial traversal: good blocks are still delivered while affected ranges are skipped.
