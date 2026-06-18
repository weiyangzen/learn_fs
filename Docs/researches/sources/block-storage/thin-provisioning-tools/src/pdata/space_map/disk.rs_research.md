# File Research: sources/block-storage/thin-provisioning-tools/src/pdata/space_map/disk.rs

Serializes a data-space map. `write_disk_sm` calls `write_common`, builds a btree of `IndexEntry` values keyed by bitmap index, flushes writes, and returns `SMRoot` populated from the input `SpaceMap`.
