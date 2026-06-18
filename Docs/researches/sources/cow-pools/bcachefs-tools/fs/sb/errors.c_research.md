# File Research: sources/cow-pools/bcachefs-tools/fs/sb/errors.c

This file implements persistent fsck/superblock error counting and formatting.

Key responsibilities:
- Builds `bch2_sb_error_strs[]` from `BCH_SB_ERRS()`.
- Prints error IDs with `bch2_sb_error_id_to_text()`.
- Validates `BCH_SB_FIELD_errors` entries.
- Prints superblock errors sorted by most recent error time.
- Prints in-memory filesystem error counts.
- Increments in-memory error counters with timestamp updates.
- Serializes in-memory error counts back to the superblock.
- Loads superblock error counts into in-memory darray state.

Important behavior:
- Validation rejects zero-count entries and entries not sorted by increasing error ID.
- Text output sorts a temporary darray by descending `last_error_time`.
- Counting preserves sorted in-memory order by error ID and increments existing entries.
- If darray allocation fails during counting, the new error count is dropped.
- Serialization resizes the errors field to match current in-memory count.

Important invariants:
- Error entry ID is 16 bits and count is 48 bits in a packed le64.
- In-memory and on-disk error entries are sorted by ID for update/search.
- Error timestamps are seconds from `ktime_get_real_seconds()`.

Dependencies:
- Uses superblock field helpers, darrays, printbuf datetime formatting, mutex-protected error count state, and error format definitions.

Research notes:
- This file supplies the persistent accounting used by journal validation, fsck, and downgrade/upgrade silent-error policy.
