# File Research: sources/cow-pools/bcachefs/fs/bcachefs/journal/seq_blacklist.c

## Role

Implements persisted journal sequence blacklisting and the runtime lookup table used during recovery and btree reads.

## Major Responsibilities

- Adds blacklisted sequence ranges to the superblock, merging overlapping/contiguous entries.
- Sets the `journal_seq_blacklist_v3` feature bit when adding entries.
- Builds an Eytzinger-sorted runtime table from the superblock field.
- Finds next blacklisted and next non-blacklisted sequence.
- Tests whether a sequence is blacklisted and marks an entry dirty if queried in dirty context.
- Returns the last blacklisted sequence.
- Validates and formats the superblock blacklist field.
- Garbage-collects blacklist entries that are neither dirty nor needed for oldest on-disk journal state.

## Notable Details

The blacklist exists so btree node updates carrying sequence numbers newer than durable journal entries are ignored after crash, and so the journal never reuses those sequence numbers before affected btree nodes are rewritten.
