# File Research: sources/block-storage/linux-dm/drivers/md/persistent-data/dm-bitset.c

## Purpose
Persistent bitset implementation built as a thin wrapper around `dm_array` of 64-bit little-endian words.

## Main Behavior
- `BITS_PER_ARRAY_ENTRY` is 64.
- `dm_disk_bitset_init()` initializes an embedded `dm_array_info` with a simple 64-bit value type.
- `dm_bitset_new()` packs callback-provided bits into 64-bit words and creates the underlying array in bulk.
- `dm_bitset_resize()` converts bit counts to word counts and grows new words as all-zero or all-one depending on `default_value`.
- A one-word cache is maintained in `struct dm_disk_bitset`:
  - `current_index`
  - `current_bits`
  - `current_index_set`
  - `dirty`
- `get_array_entry()` flushes the cached dirty word when switching to another word. This means even test/read operations can return a new root if a previous mutation was cached.
- `dm_bitset_flush()` writes the dirty cached word to the underlying array and clears cache state.
- `set`, `clear`, and `test` operate on the cached word after loading/flushing as needed.
- Cursor API wraps `dm_array_cursor` and presents bit-by-bit iteration across the packed words.

## Public API Implemented
`dm_disk_bitset_init`, `dm_bitset_empty`, `dm_bitset_new`, `dm_bitset_resize`, `dm_bitset_del`, `dm_bitset_flush`, `dm_bitset_set_bit`, `dm_bitset_clear_bit`, `dm_bitset_test_bit`, `dm_bitset_cursor_begin`, `dm_bitset_cursor_end`, `dm_bitset_cursor_next`, `dm_bitset_cursor_skip`, `dm_bitset_cursor_get_value`.

## Edge Cases
- The underlying array detects out-of-bounds word access, but the final word may contain unused bits; the caller must track the bitset’s true logical size.
- `dm_bitset_cursor_begin()` returns `-ENODATA` for an empty bitset.
