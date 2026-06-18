# File Research: sources/cow-pools/bcachefs-tools/fs/sb/clean.h

This header declares clean-superblock section APIs.

Key responsibilities:
- Declares validation, verification, read, and common-entry append helpers:
  - `bch2_sb_clean_validate_late()`
  - `bch2_verify_superblock_clean()`
  - `bch2_read_superblock_clean()`
  - `bch2_journal_super_entries_add_common()`
- Exposes `bch_sb_field_ops_clean`.
- Declares dirty/clean state mutators:
  - `bch2_fs_mark_dirty()`
  - `bch2_fs_mark_clean()`

Important invariants:
- The clean section is represented as journal entries and must be validated by journal entry validators.
- Mark clean/dirty operate on superblock state.

Research notes:
- The header is the interface used by journal write, recovery, and superblock I/O paths.
