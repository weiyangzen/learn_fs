# File Research: sources/block-storage/thin-provisioning-tools/src/pdata/btree_merge.rs

Skeleton for non-destructive btree merge. It defines a private leaf-summary collector that walks multiple roots with `BTreeWalker`, verifies subtree ordering, and records leaf block, entry count, and low/high keys.

The intended algorithm is documented: collect all leaves, optimize/merge underpacked leaves, then rebuild upper layers. `optimise_leaves` is currently a pass-through and `merge` ends in `todo!()`, so this module is not complete production behavior.
