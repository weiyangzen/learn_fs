# File Research: sources/cow-pools/bcachefs-tools/fs/journal/validate.h

This header declares journal validation APIs and defines the journal validation error macro.

Key responsibilities:
- Declares `bch2_journal_entry_err_msg()`.
- Defines `journal_entry_err()` and `journal_entry_err_on()`.
- Declares:
  - `bch2_journal_entry_validate()`
  - `bch2_journal_entry_to_text()`
  - `bch2_jset_validate()`
  - `bch2_jset_validate_early()`
- Defines `JOURNAL_ENTRY_NONE` and `JOURNAL_ENTRY_BAD`.

Important behavior:
- On read validation, errors are routed through `mustfix_fsck_err()`.
- On write validation, errors increment superblock fsck error counters and can mark the filesystem inconsistent, returning `fsck_errors_not_fixed`.
- Error messages include journal version, jset sequence, entry type, and entry offset when available.

Dependencies:
- Requires fsck validation flags, superblock error IDs, journal format types, and printbuf utilities.

Research notes:
- The macro centralizes policy differences between accepting/repairing on read and refusing corrupt metadata on write.
