# File Research: sources/block-storage/thin-provisioning-tools/src/cache/superblock.rs

Defines cache superblock layout, parsing, validation by checksum type, and writing.

Key constants:
- `SPACE_MAP_ROOT_SIZE = 128`.
- `SUPERBLOCK_LOCATION = 0`.
- Cache metadata magic `0o6142003`.
- policy name size 16 bytes and UUID size 16 bytes.

Main types:
- `SuperblockFlags { clean_shutdown, needs_check }`.
- `Superblock`: flags, block/version, policy data, space-map root, mapping/dirty/hint/discard roots, discard geometry, block counts, compatibility flags, and hit/miss counters.

Read path:
- Reads a 4 KiB block.
- Requires `metadata_block_type` to report `BT::CACHE_SUPERBLOCK`.
- Parses little-endian fields with `nom`.
- Includes `dirty_root` only for version >= 2.
- Trims policy name at the first NUL byte.

Write path:
- Packs fields into a zeroed block at superblock location.
- Writes flags, zero UUID, magic, policy name, roots, geometry, counters, policy version.
- Writes optional dirty root if present.
- Computes cache superblock checksum and writes the block.

Notable detail: the read path checks checksum-derived block type but does not explicitly compare the parsed magic field.
