# File Research: sources/block-storage/thin-provisioning-tools/src/pdata/btree_iterator.rs

Implements sorted in-order iteration over btree leaf entries. `BTreeIterator<V>` keeps a traversal stack of `Frame<V>` objects plus a path, descends to the leftmost leaf at construction, exposes current `(key, &value)` via `get`, and advances with `step`.

It reads nodes from an `Arc<dyn IoEngine + Send + Sync>` and unpacks with non-fatal checks ignored. Embedded tests build btrees of 0, 16, and 10240 entries and assert iteration returns the original ordered mappings.
