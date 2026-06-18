# File Research: sources/cow-pools/bcachefs-tools/fs/journal/write.h

This header declares journal write scheduling APIs and provides `jset_entry_init()`.

Key responsibilities:
- Declares closure callback `bch2_journal_write`.
- Declares:
  - `bch2_journal_do_writes_locked()`
  - `bch2_journal_do_writes()`
- Defines `jset_entry_init()` to append and zero a new variable-sized journal entry.

Important invariants:
- `jset_entry_init()` rounds entry size up to u64 alignment.
- `entry->u64s` counts payload u64s after shared entry fields, so it stores `u64s - 1`.
- The caller owns ensuring the target buffer has enough reserved space.

Dependencies:
- Requires vstruct helpers and journal entry format definitions.

Research notes:
- This helper is used by journal write preparation and clean-superblock entry construction.
