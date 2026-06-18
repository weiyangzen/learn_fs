# File Research: sources/block-storage/thin-provisioning-tools/src/pdata/btree_error.rs

Centralizes btree error context. `KeyRange` models half-open key ranges and can split around child keys. `split_key_ranges` derives child ranges for internal nodes.

Also implements compact encoded node paths using VM-packed u64s plus base64 for diagnostics. `NodeError` covers IO, checksum/type, block mismatch, value-size, occupancy, ordering, and incomplete-data errors. `BTreeError` wraps node/value/context errors with key range, path, or aggregate context. Embedded tests cover key-range splitting and path encode/decode round trips.
