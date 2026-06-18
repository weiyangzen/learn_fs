# File Research: sources/block-storage/thin-provisioning-tools/src/checksum.rs

Central checksum helper for identifying and writing thin-provisioning metadata block checksums.

Key behavior:
- Computes CRC32C over bytes after the first checksum word and XORs with `0xffffffff`.
- Defines salted XOR constants for thin, cache, era superblocks, bitmap, index, btree node, and array blocks.
- `BT` enum classifies block types: thin/cache/era superblock, node, index, bitmap, array, unknown.
- `metadata_block_type` reads the on-disk first `u32`, recomputes checksum, XORs to identify the salt, and returns `BT`.
- `write_checksum` writes the checksum for a requested `BT` into the first word of a 4 KiB block.

Notable details:
- Requires exact 4096-byte buffers for both read classification and checksum writing.
- Rejects `BT::UNKNOWN` when writing.
