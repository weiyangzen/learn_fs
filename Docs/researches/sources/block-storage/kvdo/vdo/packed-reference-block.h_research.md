# File Research: sources/block-storage/kvdo/vdo/packed-reference-block.h

## Purpose
Defines the on-disk packed layout for reference count blocks.

## Key Definitions
- `typedef uint8_t vdo_refcount_t`.
- Special values:
  - `EMPTY_REFERENCE_COUNT = 0`
  - `MAXIMUM_REFERENCE_COUNT = 254`
  - `PROVISIONAL_REFERENCE_COUNT = 255`

## Layout
- `COUNTS_PER_SECTOR`: sector capacity after `packed_journal_point`.
- `COUNTS_PER_BLOCK`: sector count times VDO sectors per block.
- `struct packed_reference_sector`: journal commit point plus refcount array.
- `struct packed_reference_block`: array of packed sectors.

## Integration Notes
Used by block reference management and PBN lock logic. The provisional value is referenced by write/allocation paths to reserve references before they become durable.
