# File Research: sources/block-storage/linux-dm/drivers/md/persistent-data/dm-bitset.h

## Purpose
Public interface and usage documentation for persistent bitsets.

## Main Definitions
- `struct dm_disk_bitset`: per-bitset object containing embedded `dm_array_info` and a one-word mutable cache.
- `typedef bit_value_fn`: callback used by `dm_bitset_new()` to populate bits.
- `struct dm_bitset_cursor`: bit iterator over the packed array words.

## API Contract
- Bitsets are immutable between transactions; updates return a new root.
- The caller must store the logical number of bits outside the root.
- Reads may flush cached writes and therefore may also return a new root.
- Callers should flush cached changes before using a cursor.
- Final-word unused bits are not bounds checked by the persistent array layer.

## Exposed Functions
Initialization, create/new/resize/delete, set/clear/test/flush, and cursor begin/end/next/skip/get.
