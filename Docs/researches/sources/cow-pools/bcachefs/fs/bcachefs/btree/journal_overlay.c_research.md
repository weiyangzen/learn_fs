# File Research: sources/cow-pools/bcachefs/fs/bcachefs/btree/journal_overlay.c

## Role

This file implements the replay-time journal key overlay. Before journal replay has fully applied keys to btrees, normal btree iterators must see journal keys as if they overwrite btree contents. This module maintains a sorted journal-key array and provides lookup/iteration helpers that merge journal keys with ordinary btree node iterators.

## Major Responsibilities

- Store journal keys in a sorted gap-buffer representation.
- Search journal keys by btree ID, level, and position.
- Peek forward, reverse, or exact journal keys while skipping overwritten entries.
- Insert copied or owned keys during recovery before the filesystem is writable.
- Represent deleted journal keys by inserting whiteouts.
- Track journal keys overwritten during replay/rewind and skip overwritten ranges efficiently.
- Merge btree node iterator keys with journal overlay keys.
- Sort and compact raw journal entries read during recovery.
- Free journal key storage and replay journal entries when no longer needed.
- Remove journal keys covered by “shoot down” ranges.
- Dump journal keys for diagnostics.

## Gap Buffer

`journal_keys` uses `nr`, `size`, `data`, and `gap` so sequential insertions avoid O(n^2) behavior. Helpers translate between logical sorted indices and physical array positions:

- `pos_to_idx()`
- `idx_to_pos()`
- `idx_to_key()`

`bch2_journal_key_insert_take()` moves the gap, grows the array when full, updates active iterators around gap movement, and inserts the new key at the correct sorted position.

## Lookup And Peek

`__bch2_journal_key_search()` binary-searches logical keys by btree ID, level, and position. The sort order compares descending level first, then btree ID, then position.

Forward lookup uses `bch2_journal_keys_peek_max()`. Reverse lookup uses `bch2_journal_keys_peek_prev_min()`. Exact lookup uses `bch2_journal_keys_peek_slot()`.

Both forward and reverse lookup accept a caller-maintained index for efficient repeated iteration, but reset to binary search after too many local adjustments. They skip overwritten keys and can jump across overwritten ranges.

## Insert And Delete

`bch2_journal_key_insert()` copies a key and delegates to `bch2_journal_key_insert_take()`. `bch2_journal_key_delete()` inserts a whiteout key at the requested position.

Before the btree subsystem is running, inserts go to `keys->pre_sort` so they survive the reset performed by `bch2_journal_keys_sort()` and are merged afterward.

When inserting an accounting key over an allocated accounting key, the code can accumulate accounting values instead of replacing immediately.

## Overwrite Tracking

`__bch2_journal_key_overwritten()` marks a key overwritten and maintains compact contiguous overwrite ranges in `keys->overwrites`. Adjacent overwritten keys are merged into ranges, and RCU-published range arrays allow lockless skip by iterators.

`bch2_journal_key_check_or_overwrite()` checks whether an exact journal key exists or marks it overwritten. It is used during replay/rewind logic to avoid returning stale overlay entries.

## Btree And Journal Iteration

`struct btree_and_journal_iter` merges one btree node iterator with a journal iterator. `bch2_btree_and_journal_iter_peek()` advances either source to the current overlay position, picks the lower-position key from the journal or btree, skips deleted keys, enforces node max-key bounds, and returns the visible key.

`__bch2_btree_and_journal_iter_init_node_iter()` initializes the combined iterator for a node and, during recovery before multi-threaded RW operation, links journal iterators into `c->journal_iters` so gap movement can update them.

The prefetch path copies the iterator, walks ahead through the merged view, and issues btree node prefetches for child pointers.

## Sorting Replay Keys

`bch2_journal_keys_sort()` rebuilds sorted journal keys from `c->journal_entries`. It handles journal rewind ranges, validates that rewound sequences contain overwrite entries, includes only relevant `btree_keys` or `overwrite` journal entries, supports low-memory extra sorting/compaction passes, merges `pre_sort` keys, clears stale `mem_ptr` values in btree pointer keys, and logs key counts.

`journal_sort_key_cmp()` sorts equal keys so the newest applicable key survives compaction, with special handling for rewind mode and allocated synthetic keys.

## Cleanup And Diagnostics

`bch2_journal_keys_put()` decrements the journal key refcount and, on the final put, frees allocated keys, key arrays, pre-sort state, overwrite ranges, raw journal replay entries, and the genradix.

`bch2_journal_keys_reset()` frees only sorted key state, preserving raw journal entries for re-sort.

`bch2_shoot_down_journal_keys()` removes keys in a btree/level/position range. `bch2_journal_keys_dump()` prints all sorted keys. `bch2_fs_journal_keys_init()` initializes the initial ref and overwrite lock.
