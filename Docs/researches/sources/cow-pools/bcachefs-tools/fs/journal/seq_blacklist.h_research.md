# File Research: sources/cow-pools/bcachefs-tools/fs/journal/seq_blacklist.h

This header declares journal sequence blacklist APIs and a helper for counting on-disk entries.

Key responsibilities:
- Provides `blacklist_nr_entries()` to count `journal_seq_blacklist_entry` records in a variable-length superblock field.
- Declares sequence lookup APIs:
  - `bch2_journal_seq_next_blacklisted()`
  - `bch2_journal_seq_next_nonblacklisted()`
  - `bch2_journal_seq_is_blacklisted()`
  - `bch2_journal_last_blacklisted_seq()`
- Declares mutation and initialization:
  - `bch2_journal_seq_blacklist_add()`
  - `bch2_blacklist_table_initialize()`
  - `bch2_blacklist_entries_gc()`
- Exposes `bch_sb_field_ops_journal_seq_blacklist`.

Important invariants:
- The count helper returns zero for a null field.
- Entry count is computed from `vstruct_end()` and the trailing entry array size.

Dependencies:
- Requires the on-disk blacklist format and superblock field ops types.

Research notes:
- This is the narrow public API between journal read/recovery, btree validation, and superblock persistence.
