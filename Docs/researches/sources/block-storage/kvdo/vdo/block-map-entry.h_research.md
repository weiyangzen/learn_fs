# File Research: sources/block-storage/kvdo/vdo/block-map-entry.h

## Purpose

Defines the compact five-byte on-disk/in-memory block map entry format and conversion helpers.

## Data Format

A `struct block_map_entry` stores:
- 4 bits of mapping state,
- high 4 bits of a 36-bit physical block number,
- low 32 bits of the physical block number in little-endian order.

This addresses up to 256 TiB at 4 KiB block size while keeping each logical mapping entry at five bytes.

## Important Helpers

- `vdo_unpack_block_map_entry()` returns a `struct data_location`.
- `vdo_is_mapped_location()` checks for non-unmapped state.
- `vdo_is_valid_location()` validates zero-block and mapped-state combinations.
- `vdo_pack_pbn()` packs PBN and mapping state into an entry.

## Notable Details

Bitfield order is conditional on host byte order. Compressed states are invalid for `VDO_ZERO_BLOCK`, while non-zero PBNs must be mapped.
