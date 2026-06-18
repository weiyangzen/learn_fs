# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/move_types.h

## Role

`move_types.h` defines shared data structures for movement stats, bucket tracking, and journal scrub repair records.

## Main Structures

- `struct bch_move_stats`: operation name, logical/physical progress position, return state, movement counters, read-error counters, and devices with uncorrected errors.
- `struct move_bucket_key`: device bucket plus generation.
- `struct move_bucket`: hashable bucket-in-flight record with sector count and atomic reference count.
- `scrub_journal_repair`: delayed repair item containing btree id, bad device mask, and padded extent key.

## Use

These types are used by copygc, scrub, journal scrub, bucket evacuation, and diagnostics.
