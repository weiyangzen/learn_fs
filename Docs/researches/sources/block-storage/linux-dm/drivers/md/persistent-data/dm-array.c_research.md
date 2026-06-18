# File Research: sources/block-storage/linux-dm/drivers/md/persistent-data/dm-array.c

## Purpose
Implementation of persistent dense arrays on top of the persistent btree and transaction manager. The design packs many fixed-size values into “array blocks” and indexes those blocks from a one-level btree, reducing space overhead versus one btree key per value.

## Main Structures
- `struct array_block`: on-disk block header containing checksum, maximum entries, current entries, value size, and expected block number.
- `struct resize`: helper state for resize operations.

## Important Behavior
- Array blocks are validated by `array_validator`; write preparation stamps the block number and CRC32C-derived checksum, and read validation checks both.
- `calc_max_entries()` computes how many fixed-size values fit after the array header.
- `dm_array_info_init()` embeds the user value type and sets up a btree whose leaf values are `__le64` references to array blocks.
- Btree leaf values use `block_inc`, `block_dec`, and `block_equal` so array-block references are reference counted by the transaction manager.
- `__block_dec()` checks the referenced array block’s refcount. If the block is about to lose its last reference, it decrements all contained values before decrementing the block itself.
- Updates are copy-on-write:
  - `shadow_ablock()` looks up the backing array block, shadows it through `dm_tm_shadow_block()`, increments contained values if required, and reinserts the new block reference into the btree when a real copy occurred.
  - `dm_array_set_value()` decrements the overwritten value unless the value type says old and new are equal, increments the new value if needed, and returns a new root.
- Resize supports both growth and shrink:
  - Growth fills existing tail blocks, inserts full new array blocks, and optionally inserts a final partial block.
  - Shrink removes whole trailing blocks and trims the final block, invoking value decrement callbacks.
- `dm_array_new()` bulk-populates a new array via a callback and is more efficient than repeated resize/set calls.
- `dm_array_walk()` walks the btree, then each packed array block in index order.
- Cursor API wraps a btree cursor and keeps the current array block locked while iterating values.

## Public API Implemented
`dm_array_info_init`, `dm_array_empty`, `dm_array_resize`, `dm_array_new`, `dm_array_del`, `dm_array_get_value`, `dm_array_set_value`, `dm_array_walk`, `dm_array_cursor_begin`, `dm_array_cursor_end`, `dm_array_cursor_next`, `dm_array_cursor_skip`, `dm_array_cursor_get_value`.

## Dependencies
Uses `dm-btree`, `dm-space-map`, and `dm-transaction-manager`. On-disk values are little-endian and use sparse annotations through `__dm_bless_for_disk` / `__dm_unbless_for_disk`.
