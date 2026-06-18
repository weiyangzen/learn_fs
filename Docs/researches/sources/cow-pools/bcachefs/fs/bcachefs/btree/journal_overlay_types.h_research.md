# File Research: sources/cow-pools/bcachefs/fs/bcachefs/btree/journal_overlay_types.h

## Role

This header defines the data structures backing journal replay key storage and overlay iteration.

## Data Structures

- `struct journal_ptr`: records the physical journal location, device, bucket, offset, sector, checksum, and checksum validity.
- `struct journal_replay`: stores pointers for one replayed journal entry, checksum status, ignore flags, and the variable-sized `struct jset`.
- `struct journal_key_range_overwritten`: stores a half-open logical range of overwritten journal-key indices.
- `struct journal_key`: stores either a journal sequence/offset pair into replay data or an allocated key pointer, plus btree ID, level, allocated/overwritten/rewind flags, and overwrite-range index.
- `struct journal_keys`: owns the gap-buffer key array, initial/refcount state, pre-sort keys, overwrite mutex, and RCU-managed overwrite ranges.

## Notable Design

The `journal_keys` layout intentionally starts like a darray (`nr`, `size`, `data`) but adds a gap-buffer index. This lets the recovery path insert ordered keys efficiently while still allowing bulk sort/compact behavior after reading raw journal entries.
