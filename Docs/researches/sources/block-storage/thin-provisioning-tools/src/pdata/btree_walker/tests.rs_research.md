# File Research: sources/block-storage/thin-provisioning-tools/src/pdata/btree_walker/tests.rs

Uses a mock `NodeVisitor` plus `BTreeLayout` metadata to verify traversal and error reporting. The fixture builds large btrees, corrupts selected blocks with `trash_block`, computes unaffected leaves, and checks visited key ranges, headers, and mappings.

Coverage includes empty tree, clean large tree, trashed root, first/last leaf damage, damaged leaf sequence, damaged internal node, and combined internal/leaf damage. Error assertions inspect aggregate structure, key context, path last block, and node-error wrapping.
