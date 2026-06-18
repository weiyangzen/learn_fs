<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-bitset.c -->
# sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-bitset.c

## Purpose
Implements a persistent bitset as a thin wrapper over `dm_array` storing 64-bit little-endian words. It adds bit-level set, clear, test, resize, creation, deletion, flush, and cursor operations while using a one-word cache to reduce repeated array updates.

## Important APIs, Types, And Functions
The fixed value type `bitset_bvt` stores `__le64` words and has no reference-count callbacks because words do not reference blocks. `dm_disk_bitset_init()` initializes the embedded array info and resets cache state. `dm_bitset_new()` packs bit callback results into array words through `pack_bits()`. `dm_bitset_resize()` grows or shrinks the underlying array in units of 64-bit words, filling new words with all-zero or all-one defaults.

The cache is managed by `read_bits()`, `get_array_entry()`, and `dm_bitset_flush()`. Set, clear, and test operations compute the array word and bit offset; changing to a different word flushes a dirty cached word back through `dm_array_set_value()`. Cursor functions wrap `dm_array_cursor` and expose bit-by-bit iteration with skip support.

## Control Flow
A caller initializes one `dm_disk_bitset` per bitset instance, creates or opens a root, and resizes to the desired bit count. `dm_bitset_set_bit()` and `dm_bitset_clear_bit()` call `get_array_entry()`, possibly flushing the old cached word and reading the new word, then mutate `current_bits` and mark it dirty. `dm_bitset_test_bit()` may also flush if it must switch words, so even read-like operations can return a new root. `dm_bitset_flush()` writes the cached word and clears dirty state.

## State And Persistence
Persistent state is the underlying array of 64-bit words. Runtime state is the cached `current_index`, `current_bits`, and dirty flag in `struct dm_disk_bitset`. Like `dm_array`, the logical bit count is external; the implementation cannot detect out-of-range bits inside the final stored word. Dirty cached changes are not persisted until flushed or until an operation switches array entries and flushes implicitly.

## Dependencies And Integration Points
This file depends on `dm-array`, `dm-transaction-manager`, Linux bitops, and device-mapper logging. It is suitable for metadata that needs compact persistent booleans, with caller-managed transaction commits.

## Risks
The cache makes root handling subtle: a test or set that flushes a previous word may update the root even if the requested bit is read-only. Callers must pass and store returned roots consistently. Forgetting `dm_bitset_flush()` before committing, walking, or using a cursor can lose cached updates. Bounds are only checked at the array-word level, so caller-maintained bit counts remain critical.

## Test Signals
Tests should toggle multiple bits in the same word and across word boundaries, verify root changes on implicit flush, resize to non-64-bit-aligned sizes, create from a callback, iterate with cursors and skips, and confirm unflushed updates are not visible to cursor reads until flushed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-bitset.c -->
