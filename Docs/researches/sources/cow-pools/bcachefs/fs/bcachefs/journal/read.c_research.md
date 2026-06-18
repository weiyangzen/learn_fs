# File Research: sources/cow-pools/bcachefs/fs/bcachefs/journal/read.c

## Role

Reads journal buckets from devices, validates and deduplicates journal entries, computes the replay window, handles blacklist/drop policy, and supports rewind rereads.

## Major Responsibilities

- Persists/resumes last journal bucket position in member info.
- Formats journal pointers and sequence datetimes.
- Verifies journal checksums and decrypts journal entries.
- Adds journal entries to the replay radix, deduplicating replicas.
- Drops overwrite/log entries unless recovery info, rewind, or scrub needs them.
- Reads buckets fully or peeks headers first for large journals.
- Detects checksum errors, duplicate mismatches, same-device duplicates, missing sequences, blacklisted entries, and non-monotonic bucket sequences.
- Re-reads older journal entries required for rewind.
- Produces `journal_start_info` with `last_seq`, `replay_end`, `cur_seq`, and clean state.

## Read Strategy

For large journals outside fsck/full-read mode, each device first peeks the first block of each bucket to collect sequence numbers, sorts buckets by descending sequence, and fully reads only buckets likely to contain live entries. Otherwise it scans every bucket.

## Replay Window Selection

`bch2_journal_read()` reverse-iterates entries. `cur_seq` is one greater than the highest on-disk entry of any kind. It skips no-flush entries and an initial torn flush write, then chooses the most recent valid flush entry as `replay_end`; that entry’s `last_seq` becomes the replay start. Entries after `replay_end` are later blacklisted by recovery.

## Notable Details

- `journal_entries_base_seq` maps 64-bit journal sequences into genradix indices and requires all replayed sequences to fit within a roughly 32-bit span.
- Rewind can lower `drop_before`, but refuses rewinds earlier than persisted `rewind_seq`.
- `bch2_journal_reread_for_rewind()` un-ignores entries previously dropped as not dirty when rewind requires them.
