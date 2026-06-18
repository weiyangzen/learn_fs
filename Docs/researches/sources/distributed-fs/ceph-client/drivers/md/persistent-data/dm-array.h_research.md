<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-array.h -->
# sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-array.h

## Purpose
Declares the dm persistent array API. The array provides dense, fixed-size, on-disk values with btree-like immutable update semantics and more compact storage than a plain one-entry-per-value btree.

## Important APIs, Types, And Functions
`struct dm_array_info` binds an array type to a transaction manager and a `struct dm_btree_value_type`. The same info object can describe many arrays with identical value semantics. `dm_array_info_init()` fills this structure and wires array-block pointer reference counting into an internal btree info.

The main lifecycle APIs are `dm_array_empty()`, `dm_array_new()`, `dm_array_resize()`, and `dm_array_del()`. Access APIs are `dm_array_get_value()`, `dm_array_set_value()`, and `dm_array_walk()`. `value_fn` lets callers populate a new array efficiently through callbacks. The cursor API (`struct dm_array_cursor`, `dm_array_cursor_begin()`, `dm_array_cursor_next()`, `dm_array_cursor_skip()`, `dm_array_cursor_get_value()`, `dm_array_cursor_end()`) supports efficient ordered iteration without repeated lookup calls.

## Control Flow
Callers initialize `dm_array_info`, create or open a root saved in their own metadata, resize as needed, and then get/set values by zero-based index. Mutations return a `new_root`, preserving immutable update behavior. Walking and cursors traverse index order over packed array blocks.

## State And Persistence
The header explicitly states that the array does not expose or store its logical length in a standalone place; the caller must persist the size next to the root. Values passed into mutating APIs must be in on-disk little-endian format, and the Sparse annotations inherited from `dm-btree.h` express that contract. Old roots can remain valid if callers increment them through the transaction manager before update.

## Dependencies And Integration Points
The API is built on `dm-btree.h` and the transaction manager. It is a lower-level dependency for `dm-bitset` and can be used by dm target metadata that needs dense arrays such as mappings, hints, or compact counters.

## Risks
Misremembering the external size is the main API risk. The final partial array block will not independently know the total logical length beyond its stored entries. Callers must also pair values with correct value-type callbacks to keep referenced metadata blocks alive. Cursor users must not keep `value_le` pointers after moving or ending the cursor.

## Test Signals
Header-level contract tests should cover external size tracking, immutable root behavior, little-endian value handling, cursor lifetime rules, and value-type callback invocation during resize, overwrite, and delete.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-array.h -->
