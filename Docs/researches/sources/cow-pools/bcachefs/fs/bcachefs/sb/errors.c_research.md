# File Research: sources/cow-pools/bcachefs/fs/bcachefs/sb/errors.c

This file implements persistent filesystem/fsck error counting in the superblock.

Key responsibilities:
- Generates error-name strings from the stable error catalog.
- Renders error IDs and unknown error fallback text.
- Validates the superblock errors field for nonzero counts and strictly increasing error IDs.
- Renders persisted errors sorted by most recent error time.
- Renders in-memory error counts.
- Increments an in-memory error count with last-error timestamp, preserving sorted-by-ID order.
- Serializes in-memory error counts back to the superblock.
- Loads superblock error counts into memory.

Important invariants:
- Persistent entries are sorted by error ID for validation/storage.
- Human-readable output sorts by `last_error_time` descending.
- Counts are stored as 48-bit values packed with 16-bit error IDs in the on-disk entry word.
- Allocation failure while counting a new error silently drops that new count rather than destabilizing error handling.
