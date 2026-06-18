# File Research: sources/cow-pools/bcachefs-tools/fs/journal/seq_blacklist_format.h

This header defines the on-disk journal sequence blacklist superblock field.

Key definitions:
- `struct journal_seq_blacklist_entry`
  - `start`: little-endian inclusive range start.
  - `end`: little-endian exclusive range end.
- `struct bch_sb_field_journal_seq_blacklist`
  - Standard superblock field header.
  - Flexible array of blacklist entries.

Important invariants:
- Ranges are validated elsewhere as sorted, non-empty, and non-overlapping.
- Fields are endian-stable on disk.

Research notes:
- This is pure persistent format. Changes affect mount/recovery compatibility.
