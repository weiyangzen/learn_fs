# File Research: sources/block-storage/thin-provisioning-tools/src/pdata/btree_builder/test_utils.rs

Provides test-only layout introspection for btrees. `NodeInfo` and `BTreeLayout` record block numbers, key ranges, entry ranges, and node heights as builders emit nodes.

Helpers build leaves and complete btrees from mappings, track root/leaf/node slices by height, calculate first leaf under a node, and expose `push_values`. This allows walker tests to know exact expected visitation and affected ranges after corrupting specific nodes.
