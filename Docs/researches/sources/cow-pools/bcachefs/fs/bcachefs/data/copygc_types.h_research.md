# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/copygc_types.h

Defines persistent in-memory copygc state in `struct bch_fs_copygc`.

Key fields:
- RCU-protected copygc kthread pointer.
- Dedicated `write_point` for relocation writes.
- Wait accounting (`wait_at`, `wait`), running flag, run count, kick count.
- Waitqueue for observers waiting on running state.
- Dedicated workqueue for btree updates.

Dependencies and interactions:
- Embedded in `struct bch_fs`; initialized by `bch2_fs_copygc_init()`.
