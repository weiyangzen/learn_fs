# File Research: sources/cow-pools/bcachefs/fs/bcachefs/journal/seq_blacklist_format.h

## Role

Defines the on-disk superblock format for journal sequence blacklist ranges.

## Contents

- `struct journal_seq_blacklist_entry` stores half-open `[start, end)` sequence ranges as little-endian u64s.
- `struct bch_sb_field_journal_seq_blacklist` embeds the generic superblock field header followed by variable entries.

## Notable Details

The implementation treats `end` as exclusive; validation rejects `start >= end`.
