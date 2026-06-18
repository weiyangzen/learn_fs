# File Research: sources/block-storage/thin-provisioning-tools/src/pdata/space_map/metadata.rs

Implements metadata-space-map index block format. `MetadataIndex` stores its own block number and up to 255 `IndexEntry` records in a single metadata index block. Loading verifies checksum/type and block number, then truncates entries to the number required by `nr_blocks`.

Helpers map blocks to bitmap indexes. `write_metadata_sm` writes bitmap/overflow data, allocates the metadata index block, patches bitmap counts for blocks consumed by the space map itself, writes checksum-tagged index data, flushes, and returns `SMRoot`. `core_metadata_sm` caps metadata maps at `MAX_METADATA_BLOCKS`.
