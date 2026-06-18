# File Research: sources/cow-pools/bcachefs-tools/fs/btree/journal_overlay.c

## Purpose
`journal_overlay.c` manages keys read from the journal before replay has completed. It lets normal btree traversal see journal keys as if they overlay the btree, supports insertion/deletion of replay keys, tracks overwritten journal keys, sorts/deduplicates replay entries, and frees replay data.

## Main Responsibilities
- Stores journal keys in a sorted gap buffer (`struct journal_keys`) for efficient sequential insertions during recovery.
- Provides binary search and peeking helpers: `bch2_journal_keys_peek_max()`, `bch2_journal_keys_peek_prev_min()`, and `bch2_journal_keys_peek_slot()`.
- Implements `bch2_journal_key_insert_take()`, `bch2_journal_key_insert()`, and `bch2_journal_key_delete()` for recovery-time mutation of the overlay.
- Tracks journal keys overwritten by replay using `overwritten` bits plus ranges in `journal_key_range_overwritten`, allowing peeking iterators to skip runs efficiently.
- Implements `struct btree_and_journal_iter`, which merges a btree node iterator with journal keys at the same btree ID/level.
- Sorts raw journal replay entries with `bch2_journal_keys_sort()`, including rewind support and compaction/deduplication of equal keys.
- Cleans up with `bch2_journal_keys_put()`, reset helpers, shoot-down by btree/range, dumping, and filesystem initialization.

## Important Behaviors
- The main key array is a gap buffer: logical indexes are translated by `idx_to_pos()` and `pos_to_idx()` so insertions near the gap are cheap.
- Before `journal_keys_sort()` and before the btree is running, inserted keys go to `pre_sort` so they survive reset and later merge into the sorted array.
- Accounting keys are intentionally not accumulated during journal sort because replay must compare each individual accounting update against the btree version.
- `btree_and_journal_iter_peek()` returns the earlier of btree and journal keys at the current position, skips deleted keys, and can fail early when too many whiteouts are encountered during prefetch.
- Rewind ranges require overwrite entries; if rewind is requested but overwrite metadata is unavailable, sorting returns a journal rewind error.

## Dependencies and Coupling
- Uses journal replay structures from `journal/read.h`, bkey/bset helpers, allocation accounting accumulation, genradix journal entry storage, RCU-protected overwrite range access, and the btree node prefetch path.
- Called by `iter.c` during traversal when `trans->journal_replay_not_finished` or `BTREE_ITER_with_journal` is set.

## Research Notes
- This file is recovery-path critical. Normal multithreaded RW use is avoided until recovery has finished; comments explicitly restrict some operations to the recovery thread while still read-only.
- Correctness depends on comparisons by level, btree ID, and bpos matching the btree iterator ordering.
