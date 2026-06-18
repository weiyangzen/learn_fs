# File Research: sources/block-storage/thin-provisioning-tools/src/pdata/btree_walker.rs

General recursive btree walker. `NodeVisitor<V>` receives leaf path, key range, header, keys, values, repeated-node callbacks, and end-walk callback. `BTreeWalker` tracks visited blocks through a `SpaceMap`, caches failures by block, batches child reads, and aggregates child errors.

Utility collectors convert btrees to maps, maps with paths, key sets, value vectors, or just block counts. Shared nodes are not reread; visitors receive `visit_again` if clean, or cached errors if bad. Error paths and key ranges are preserved for diagnostics.
