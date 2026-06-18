# File Research: sources/cow-pools/bcachefs-tools/fs/alloc/accounting.c

This file implements bcachefs disk accounting: persistent accounting keys in the accounting btree plus fast in-memory percpu counters indexed by sorted/Eytzinger `struct bpos` accounting positions.

Core responsibilities:
- Defines accounting type strings and expected counter counts from `BCH_DISK_ACCOUNTING_TYPES()`.
- Builds accounting btree keys from `struct disk_accounting_pos` and counter deltas.
- Implements `bch2_disk_accounting_mod()`, which queues normal accounting updates in `trans->accounting` and applies GC-mode updates directly to in-memory accounting.
- Maintains superblock replica entries for accounting keys that represent replicas, via `bch2_accounting_update_sb()`.
- Validates, byte-swaps, and prints `KEY_TYPE_accounting` keys.
- Owns the in-memory accounting table lifecycle, insertion, GC shadow counters, cleanup, and readout APIs.
- Reconstructs accounting from the accounting btree plus journal overlay during mount/recovery.

Important mechanisms:
- Persistent accounting updates are deltas, not replacement values. The btree write buffer or journal replay later accumulates them into the accounting btree.
- Every accounting delta gets a unique `bversion` derived from journal sequence and offset; replay uses this to avoid applying stale deltas.
- In-memory counters use `struct accounting_mem_entry`, with `v[0]` for live counters and `v[1]` for GC verification counters.
- `bch2_accounting_read()` merges btree accounting keys and journal accounting keys in key order, drops overwritten journal entries, accumulates same-position deltas, sorts the in-memory table, then runs fixups.
- `accounting_read_mem_fixups()` removes zero/invalid entries, validates device references, populates filesystem usage and per-device usage percpu counters, and schedules allocation checking if counter underflow is detected.
- `bch2_gc_accounting_start()` allocates GC counter arrays and `bch2_gc_accounting_done()` compares rebuilt GC accounting against live counters, optionally committing correction deltas.

External interfaces:
- `bch2_disk_accounting_mod()`
- `bch2_mod_dev_cached_sectors()`
- `bch2_accounting_update_sb()`
- `bch2_fs_replicas_usage_read()`
- `bch2_fs_accounting_read()`
- `bch2_fs_accounting_read_key()`
- `bch2_gc_accounting_start()` / `bch2_gc_accounting_done()`
- `bch2_accounting_read()`
- `bch2_dev_usage_remove()` / `bch2_dev_usage_init()`
- `bch2_verify_accounting_clean()`
- `bch2_accounting_gc_free()` / `bch2_fs_accounting_exit()`

Correctness notes:
- Replica accounting keys are normalized by sorting device IDs.
- In-memory accounting insertion may request `btree_insert_need_mark_replicas` if a replicas entry is not yet marked in the superblock.
- Zero replicas accounting entries can remove now-unused replica entries from the superblock, gated by metadata-version compatibility.
- Invalid device accounting can be repaired by negating the current counters and committing a removal delta.
- Startup accounting intentionally resets prior in-memory state because recovery can rewind and rerun with different repaired topology.
