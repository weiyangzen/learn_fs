# File Research: sources/cow-pools/bcachefs-tools/fs/init/recovery.h

Public recovery orchestration header.

Key contents:
- Declares btree lost-data handling:
  - `bch2_btree_lost_data()`
- Declares journal rewind error-silencing helper:
  - `bch2_ignore_journal_rewind_errors()`
- Declares recovery/RW/journal replay entry points:
  - `bch2_set_may_go_rw()`
  - `bch2_journal_replay()`
- Declares filesystem recovery and new-filesystem initialization:
  - `bch2_fs_recovery()`
  - `bch2_fs_initialize()`

Role:
- Consumed by filesystem startup, pass scheduling, journal-related repair code, and btree error paths that need to request recovery or report lost btree data.
