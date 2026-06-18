# File Research: sources/cow-pools/bcachefs-tools/fs/journal/seq_blacklist.c

This file implements persistent and in-memory journal sequence blacklisting.

Purpose:
- Prevents reuse of journal sequence numbers associated with btree bsets that were flushed newer than the newest reliable journal entry.
- Lets recovery ignore bsets whose newest journal sequence was not safely committed.
- Records blacklisted ranges in the superblock so future mounts preserve the decision.

Key responsibilities:
- Adds and merges blacklist ranges in `bch2_journal_seq_blacklist_add()`.
- Builds an in-memory Eytzinger-ordered lookup table with `bch2_blacklist_table_initialize()`.
- Finds the next blacklisted or nonblacklisted sequence.
- Tests whether a sequence is blacklisted and optionally marks its table entry dirty.
- Reports the last blacklisted sequence.
- Validates and prints the superblock blacklist field.
- Garbage-collects obsolete blacklist entries with `bch2_blacklist_entries_gc()`.

Important behavior:
- Added ranges merge with overlapping or contiguous existing ranges.
- Superblock resize happens under `sb_lock` with `PF_MEMALLOC_NOFS`.
- Adding a blacklist range sets the `journal_seq_blacklist_v3` feature bit, writes the superblock, and rebuilds the table.
- Lookup uses Eytzinger search by range start or end for fast queries.
- GC keeps entries that were dirtied in memory or whose end is newer than `oldest_seq_found_ondisk`.

Important invariants:
- Superblock blacklist entries must be sorted, non-empty ranges with `start < end`, and non-overlapping.
- The in-memory table count must match the superblock field count during GC.
- Blacklist range `end` is exclusive in lookup logic.

Dependencies:
- Uses journal state, superblock field resize/write helpers, Eytzinger array utilities, and darray/array insertion helpers.

Research notes:
- The long file comment documents the correctness reason: journal sequence ordering must dominate btree node flush ordering after crash recovery.
