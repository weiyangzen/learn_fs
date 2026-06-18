# File Research: sources/cow-pools/bcachefs-tools/fs/btree/journal_overlay_types.h

## Purpose
`journal_overlay_types.h` contains the data structures backing journal replay entries and the journal-key overlay index.

## Main Types
- `struct journal_ptr`: records where a journal entry was found, including checksum status, device, bucket/offset, and sector.
- `struct journal_replay`: stores one replayed journal set plus its source pointers and flags for checksum/blacklist/dirty handling.
- `struct journal_key_range_overwritten`: represents a contiguous logical range of overwritten journal keys.
- `struct journal_key`: identifies one replay key by btree ID, level, location in `journal_replay`, optional allocated key pointer, overwrite state, and rewind state.
- `struct journal_keys`: sorted gap-buffer container for journal keys, including refcount, initial-ref flag, pre-sort staging array, overwrite lock, and RCU-visible overwrite ranges.

## Important Behaviors
- `journal_replay` keeps `struct jset j` last because it is variable sized.
- `journal_keys` intentionally mirrors darray layout at the front (`nr`, `size`, `data`, `preallocated`) while adding gap-buffer and replay-specific fields.
- `journal_key` can either point into stored journal replay data via sequence/offset or own an allocated `struct bkey_i`.

## Dependencies and Coupling
- Used by `journal_overlay.h/.c` and journal reading code. It depends on bcachefs bkey, checksum, darray, mutex, and atomic conventions.

## Research Notes
- The gap-buffer and overwrite-range fields explain much of the complexity in `journal_overlay.c`: logical ordering and physical storage position are deliberately separate.
