# File Research: sources/block-storage/thin-provisioning-tools/src/pdata/btree/tests.rs

Tests `pack_node` and `unpack_node` round trips for empty and fully populated leaf nodes with random keys/values. It verifies header preservation, key preservation, and value preservation for `u64` leaves.
