# File Research: sources/block-storage/linux-dm/drivers/md/persistent-data/dm-array.h

## Purpose
Public interface and documentation for persistent dense arrays.

## Main Definitions
- `struct dm_array_info`: describes array value type and transaction-manager binding. It is reusable across multiple array instances.
- `typedef value_fn`: callback used by `dm_array_new()` to populate initial values.
- `struct dm_array_cursor`: cursor state combining an array info, a btree cursor, current array block, current array-block header, and current entry index.

## API Contract
- Arrays are immutable between transactions. Update operations return a new root.
- Callers must store the logical array size outside the array root.
- Arrays are dense and indexed from zero; out-of-bounds access returns `-ENODATA`.
- Value types reuse `struct dm_btree_value_type` so array values can participate in reference counting.
- Values passed to write APIs must be in on-disk format and marked with the sparse disk annotations.
- Cursors provide efficient ordered iteration and are intended for cases that need lockstep traversal with another structure.

## Exposed Functions
`dm_array_info_init`, `dm_array_empty`, `dm_array_resize`, `dm_array_new`, `dm_array_del`, `dm_array_get_value`, `dm_array_set_value`, `dm_array_walk`, and cursor begin/end/next/skip/get.
