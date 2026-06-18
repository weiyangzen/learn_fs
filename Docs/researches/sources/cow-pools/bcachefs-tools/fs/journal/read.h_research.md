# File Research: sources/cow-pools/bcachefs-tools/fs/journal/read.h

Public journal read/replay helper header.

Key contents:
- Includes checksum and darray helpers.
- Declares member-info journal position helpers:
  - `bch2_journal_pos_from_member_info_set()`
  - `bch2_journal_pos_from_member_info_resume()`
- Defines `journal_replay_ignore()` for entries ignored due to blacklist or not-dirty filtering.
- Provides typed journal-entry iteration helpers:
  - `__jset_entry_type_next()`
  - `for_each_jset_entry_type`
  - `jset_entry_for_each_key`
  - `for_each_jset_key`
- Defines `jset_datetime()` to extract `BCH_JSET_ENTRY_datetime`.
- Defines `journal_nonce()` for checksum/encryption nonce generation from journal sequence and journal nonce type.
- Declares journal pointer formatting:
  - `bch2_journal_ptrs_to_text()`
- Defines `u64_range` and darray type for sequence ranges.
- Declares missing-range, datetime, reread, and read APIs:
  - `bch2_journal_entry_missing_range()`
  - `bch2_journal_seq_datetime_to_text()`
  - `bch2_journal_reread_for_rewind()`
  - `bch2_journal_read()`

Role:
- Shared by recovery, journal reader, journal validators, and diagnostics for iterating and interpreting read journal entries.
