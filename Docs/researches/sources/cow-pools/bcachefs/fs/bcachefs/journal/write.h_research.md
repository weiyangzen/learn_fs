# File Research: sources/cow-pools/bcachefs/fs/bcachefs/journal/write.h

This header declares the journal write closure callback and a helper for appending journal-set entries.

Key elements:
- `CLOSURE_CALLBACK(bch2_journal_write)` is the async journal write entry point.
- `jset_entry_init()` zeroes a new fixed-size entry, stores its `u64s` payload length, advances the caller’s end pointer, and returns the initialized entry.

Important invariant:
- `entry->u64s` counts from the start of the entry data area and excludes the shared header fields, so callers pass total structure size and the helper stores `DIV_ROUND_UP(size, 8) - 1`.
