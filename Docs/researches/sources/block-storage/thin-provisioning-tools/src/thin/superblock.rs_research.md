# File Research: sources/block-storage/thin-provisioning-tools/src/thin/superblock.rs

## Purpose
Defines binary parsing and writing for thin-provisioning metadata superblocks.

## Main Components
- Constants:
  - `MAGIC = 27022010`
  - `SUPERBLOCK_LOCATION = 0`
  - `UUID_SIZE = 16`
  - `SPACE_MAP_ROOT_SIZE = 128`
- `SuperblockFlags` currently exposes the `needs_check` bit and implements `Display`.
- `Superblock` contains decoded superblock fields used by the tooling: flags, block number, version, time, transaction ID, metadata snapshot block, data/metadata space-map roots, mapping/details roots, data block size, and metadata block count.
- `unpack()` uses `nom` little-endian parsers to decode the on-disk layout.
- `read_superblock()` reads a block through `IoEngine`, validates checksum block type `BT::THIN_SUPERBLOCK`, and unpacks it.
- `read_superblock_snap()` follows `metadata_snap` from the live superblock and reads the snapshot superblock.
- `pack_superblock()` writes the on-disk layout with a placeholder checksum.
- `write_superblock()` serializes, checksums, and writes a superblock.

## Behavior
The parser reads but does not expose the UUID. On write, UUID bytes are emitted as zeros. The metadata block size is not stored from the struct; it is written as the fixed library `BLOCK_SIZE >> SECTOR_SHIFT`.

`read_superblock()` treats an unexpected checksum block type as a bad checksum in the superblock, then reports unpack failure separately. `read_superblock_snap()` requires a nonzero `metadata_snap` pointer.

## Dependencies and Interactions
This file is central to thin commands that need binary metadata roots. It depends on checksum helpers, block constants, and the `IoEngine` block abstraction.

## Research Notes
The write API accepts a `_loc` parameter but always writes `SUPERBLOCK_LOCATION` by constructing `Block::zeroed(SUPERBLOCK_LOCATION)`. Callers should not expect arbitrary-location superblock writes from this function.
