# File Research: sources/block-storage/thin-provisioning-tools/src/era/superblock.rs

This file defines era superblock on-disk packing and unpacking.

Important structures and constants:
- `SPACE_MAP_ROOT_SIZE = 128`
- `SUPERBLOCK_LOCATION = 0`
- `SuperblockFlags`
- `Superblock`

Important behavior:
- `unpack()` parses the on-disk superblock fields with `nom`.
- `read_superblock()` reads a metadata block, verifies checksum type `BT::ERA_SUPERBLOCK`, and parses it.
- `read_superblock_snap()` follows `metadata_snap` from the actual superblock.
- `pack_superblock()` serializes fields with little-endian layout.
- `write_superblock()` writes to block zero, calculates checksum, and writes through `IoEngine`.

Integration points:
- Used by era check, dump, invalidate, repair, restore, and metadata generator.
- Uses `Writeset` for current writeset fields.

Risks and notes:
- UUID is parsed but not stored in the returned production `Superblock`.
- `write_superblock()` ignores its `_loc` parameter and always writes `SUPERBLOCK_LOCATION`.
