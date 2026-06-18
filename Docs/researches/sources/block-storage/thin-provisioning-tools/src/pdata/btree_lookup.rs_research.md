# File Research: sources/block-storage/thin-provisioning-tools/src/pdata/btree_lookup.rs

Implements simple point lookup. Starting at root, it unpacks each node, binary-searches internal keys to choose the greatest lower-bound child, and binary-searches leaf keys to return `Option<V>`.

It clones returned values and intentionally unpacks full nodes, which the comments call acceptable for low-frequency lookups such as device details.
