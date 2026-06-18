<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-bitset.h -->
# sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-bitset.h

## Purpose
Declares the persistent bitset API built on `dm_array`. It exposes bit-indexed operations with immutable root updates while documenting the one-word cache and caller-managed size contract.

## Important APIs, Types, And Functions
`struct dm_disk_bitset` embeds `struct dm_array_info` and stores cache fields `current_index`, `current_bits`, `current_index_set`, and `dirty`. `dm_disk_bitset_init()` prepares the instance. Lifecycle and construction APIs are `dm_bitset_empty()`, `dm_bitset_new()`, `dm_bitset_resize()`, and `dm_bitset_del()`. Access APIs are `dm_bitset_set_bit()`, `dm_bitset_clear_bit()`, `dm_bitset_test_bit()`, and `dm_bitset_flush()`.

`struct dm_bitset_cursor` wraps `struct dm_array_cursor` and tracks remaining entries, array index, bit index, and current word. Cursor APIs begin, end, advance, skip, and read the current boolean.

## Control Flow
The caller initializes a bitset object, obtains a root, resizes or creates contents, uses set/clear/test operations while updating any returned root, flushes cached updates, and then commits through the surrounding transaction manager. Cursor users should flush first, then begin iteration with the logical bit count.

## State And Persistence
The bitset stores words on disk, but the logical bit count is external. The final word may contain unused bits that are not automatically bounded by the library. Runtime cache state is part of `struct dm_disk_bitset`, so unlike `dm_array_info`, the object is not purely type-level metadata and should not be shared across independent bitset instances.

## Dependencies And Integration Points
The header depends on `dm-array.h` and indirectly on btree/transaction-manager APIs. It integrates with metadata users that need persistent boolean maps and ordered scans.

## Risks
The most important risk is failing to flush dirty cache state or failing to preserve `new_root` returned from operations. Sharing a `dm_disk_bitset` instance across roots would mix cache state. Callers must guard against out-of-range bits within the final word.

## Test Signals
Test signals include root update handling on set/clear/test, explicit flush before commit, cursor iteration after flush, boundary behavior at 63/64/65 bits, and independent cache state for multiple bitset instances.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-bitset.h -->
