# File Research: sources/cow-pools/bcachefs-tools/fs/journal/init.h

Public journal allocation and lifecycle header.

Key contents:
- Declares journal bucket management:
  - `bch2_set_nr_journal_buckets()`
  - `bch2_dev_journal_bucket_delete()`
- Declares allocation helpers:
  - `bch2_dev_journal_alloc()`
  - `bch2_fs_journal_alloc()`
- Declares shutdown/startup helpers:
  - `bch2_dev_journal_stop()`
  - `bch2_fs_journal_stop()`
  - `bch2_fs_journal_start()`
  - `bch2_journal_set_replay_done()`
- Declares per-device lifecycle:
  - `bch2_dev_journal_exit()`
  - `bch2_dev_journal_init_early()`
  - `bch2_dev_journal_init()`
- Declares filesystem journal lifecycle:
  - `bch2_fs_journal_exit()`
  - `bch2_fs_journal_init_early()`
  - `bch2_fs_journal_init()`

Role:
- Used by filesystem init/recovery/pass code and device management to allocate, start, stop, and tear down journal state.
