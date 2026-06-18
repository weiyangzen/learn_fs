# File Research: sources/cow-pools/bcachefs/fs/bcachefs/alloc/accounting.c

This file implements bcachefs disk accounting: persistent accounting keys in the accounting btree plus fast in-memory per-CPU counters.

Core model:
- Persistent accounting uses `KEY_TYPE_accounting` entries in `BTREE_ID_accounting`.
- Updates are deltas queued through the btree write buffer.
- In-memory accounting stores selected accounting keys in an Eytzinger-sorted dynamic array of `accounting_mem_entry`, each with per-CPU counter arrays.
- Commit assigns each accounting delta a journal-position-derived `bversion`, allowing journal replay to distinguish already-applied updates from unapplied deltas.

Important functions:
- `bch2_disk_accounting_mod()` normalizes accounting keys, coalesces duplicate deltas in the transaction accounting buffer, removes zeroed deltas, or applies GC-mode updates directly to memory accounting.
- `bch2_mod_dev_cached_sectors()` is a helper for cached replicas accounting.
- `bch2_accounting_validate()` validates accounting key structure, replicas fields, zero padding, counter count, and nonzero versions at commit validation time.
- `bch2_accounting_key_to_text()` and `bch2_accounting_to_text()` render accounting keys and counters.
- `bch2_accounting_swab()` byte-swaps accounting values.
- `bch2_accounting_update_sb()` ensures replicas accounting keys being updated are represented in the superblock replicas table when needed.

Memory accounting:
- `__bch2_accounting_mem_insert()` inserts a new accounting memory entry, allocates per-CPU counters, and sorts the Eytzinger array.
- `bch2_accounting_mem_insert()` may temporarily drop the per-CPU read lock to take the write lock and insert.
- `bch2_accounting_mem_insert_locked()` assumes the caller already holds the relevant write lock.
- `__bch2_accounting_maybe_kill()` removes zero-valued replicas accounting entries and updates the superblock.
- `bch2_accounting_mem_gc()` removes zero in-memory entries.

Read APIs:
- `bch2_fs_replicas_usage_read()` emits replicas usage records for the existing userspace usage ioctl.
- `bch2_fs_accounting_read()` exports selected in-memory accounting keys as serialized accounting bkeys.
- `bch2_fs_accounting_read_key()` reads either from memory accounting or directly from the accounting btree for non-memory accounting types.

GC accounting:
- `bch2_gc_accounting_start()` allocates a second per-CPU counter set for GC-computed values.
- `bch2_gc_accounting_done()` compares normal counters with GC counters, reports mismatches, and can repair persistent accounting by writing corrective deltas.
- `bch2_accounting_gc_free()` frees GC counter arrays and clears `gc_running`.

Mount/replay initialization:
- `bch2_accounting_read()` rebuilds in-memory accounting from the accounting btree and journal keys. It walks btree and journal accounting together, discards old journal deltas based on `bversion`, accumulates newer deltas by key, compacts journal keys, sorts memory entries, asserts no duplicates, then runs fixups.
- `accounting_read_mem_fixups()` drops zero/invalid entries, validates late references to devices and replicas-superblock entries, populates aggregate filesystem and per-device counters, and schedules `check_allocations` if underflow is detected.

Repair and device removal:
- `disk_accounting_invalid_dev()` removes accounting entries pointing to invalid devices by adding a negated delta and committing it.
- `bch2_disk_accounting_validate_late()` handles validity checks that need live filesystem state.
- `bch2_dev_usage_remove()` removes all `dev_data_type` accounting for a device.
- `bch2_dev_usage_init()` initializes free bucket accounting for a device.
- `bch2_verify_accounting_clean()` debug-checks persistent accounting against in-memory counters and aggregate capacity usage.
- `bch2_fs_accounting_exit()` frees all memory accounting storage.

Key invariants:
- Accounting updates are deltas until write-buffer flush or journal replay resolves them.
- Accounting key versions must be strictly time ordered.
- Memory accounting is only maintained for selected types: not `snapshot` or `inum`.
- Replicas accounting may require superblock updates before insertion.
- Normal accounting updates also maintain aggregate `fs_usage_delta` and per-device usage counters.
