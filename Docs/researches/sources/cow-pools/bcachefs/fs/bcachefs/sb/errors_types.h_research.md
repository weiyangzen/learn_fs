# File Research: sources/cow-pools/bcachefs/fs/bcachefs/sb/errors_types.h

This header defines in-memory persistent-error count types.

Key types:
- `struct bch_sb_error_entry_cpu`: 16-bit error ID, 48-bit count, and last-error timestamp.
- `bch_sb_errors_cpu`: dynamic array of CPU-format error entries.

This type is protected by `c->errors.counts_lock` in `errors.c`.
