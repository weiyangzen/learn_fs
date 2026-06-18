# File Research: sources/cow-pools/bcachefs-tools/fs/data/move_types.h

## Purpose
Defines data structures shared by movement, scrub, and repair code.

## Main Interfaces
- `struct bch_move_stats` stores operation name, physical/logical position, return code, moved/raced/seen/error counters, and devices with uncorrected errors.
- `struct move_bucket_key` and `struct move_bucket` identify and track buckets currently in movement with hash linkage and refcount.
- `scrub_journal_repair` stores a btree id, bad device mask, and padded key for later repair.
- `DEFINE_DARRAY(scrub_journal_repair)` creates the dynamic array type used by journal scrub repair queues.

## Notes
The stats union supports both logical `bbpos` progress and physical `dev/offset` progress.
