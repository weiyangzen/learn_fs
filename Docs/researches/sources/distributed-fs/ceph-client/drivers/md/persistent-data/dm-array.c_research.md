<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-array.c -->
# sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-array.c

## Purpose
Implements a persistent, immutable array abstraction on top of a single-level dm btree. Instead of storing one btree entry per logical array element, the btree maps packed array-block indexes to blocks containing many fixed-size values, reducing metadata space and lookup overhead for dense arrays.

## Important APIs, Types, And Functions
The on-disk leaf payload is `struct array_block`, containing checksum, max entry count, current entry count, value size, and expected block number. `array_validator` verifies checksum and block-location identity on read and refreshes both on write.

Public APIs are `dm_array_info_init()`, `dm_array_empty()`, `dm_array_resize()`, `dm_array_new()`, `dm_array_del()`, `dm_array_get_value()`, `dm_array_set_value()`, `dm_array_walk()`, and cursor functions. Internal helpers include `element_at()`, `fill_ablock()`, `trim_ablock()`, `lookup_ablock()`, `shadow_ablock()`, `insert_ablock()`, `insert_new_ablock()`, and resize helpers for grow/shrink operations.

The array btree stores `__le64` block pointers. Its value type uses `block_inc()`, `block_dec()`, and `block_equal()` so array block reference counts are managed through the transaction manager. When an array block's refcount drops to one and is about to be deleted, `__block_dec()` reads the block and decrements every contained value through the caller-supplied value type.

## Control Flow
Creation starts with an empty btree root. Resizing computes the number of full array blocks and tail entries before and after the operation. Growth shadows or adds tail blocks, fills new entries with the default value, increments value references, and inserts new array blocks into the btree. Shrink removes trailing btree entries and trims the new tail block, decrementing removed values.

Lookups compute `array_index = logical_index / max_entries`, resolve the array block through the btree, verify the entry is within `nr_entries`, copy the on-disk value, and unlock. Updates shadow the array block via the transaction manager, reinsert the shadow into the btree when the block location changes, compare/decrement/increment values as needed, and return a new root. Walking and cursors iterate the btree in order, loading each packed block and exposing values in index order.

## State And Persistence
The array is immutable between transactions: mutating calls return a new root, and callers may keep the old root alive by incrementing its reference. Array length is intentionally not stored in the array root; callers must persist the logical size elsewhere. Checksums and block numbers protect array-block reads from corruption or misplaced blocks.

## Dependencies And Integration Points
This file depends on `dm-btree`, `dm-transaction-manager`, `dm-space-map` semantics through refcounts, dm-bufio block validation via the block manager, and device-mapper logging. It is used by higher-level metadata such as bitsets and dm target metadata arrays.

## Risks
The array depends on correct caller-supplied value-type callbacks. Missing `inc`/`dec` callbacks for values that contain block references can leak or prematurely free metadata blocks. The size is external, so callers can read or write semantically out of bounds if they lose the stored length. Cache/transaction correctness depends on reinserting shadowed array blocks whenever the physical block changes. `trim_ablock()` and growth paths are sensitive to off-by-one errors in tail-block calculations.

## Test Signals
Focused tests should create, grow, shrink, delete, walk, and cursor-iterate arrays across empty, one-block, exact-block, and multi-block sizes. Reference-count tests should use value types that count `inc`/`dec` calls. Fault tests should corrupt checksums/block numbers and expect validator failures. Snapshot-style tests should retain an old root while updating a new root and verify both views remain valid.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-array.c -->
