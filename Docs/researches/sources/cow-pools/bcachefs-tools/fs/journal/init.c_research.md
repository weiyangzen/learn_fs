# File Research: sources/cow-pools/bcachefs-tools/fs/journal/init.c

Journal allocation, startup/shutdown, per-device journal initialization, and journal workqueue/buffer lifecycle.

Key responsibilities:
- Allocates additional journal buckets on a device:
  - `bch2_set_nr_journal_buckets_iter()` allocates buckets transactionally, marks them as journal metadata, inserts them into the device journal bucket ring near `discard_idx`, writes the superblock, and commits in-memory bucket/sequence/index updates under journal lock.
  - On failure after partial allocation, marks new buckets free and releases open buckets.
  - `bch2_set_nr_journal_buckets_loop()` repeats allocation until requested count is reached, with disk reservation for non-new filesystems.
  - `bch2_set_nr_journal_buckets()` is the public runtime resize entry and refuses removed devices.
- Deletes a journal bucket in `bch2_dev_journal_bucket_delete()`:
  - Finds bucket position.
  - Writes updated superblock bucket list.
  - Adjusts journal indices and arrays under journal lock.
  - Recomputes available space.
- Allocates default journal space:
  - `bch2_dev_journal_alloc()` skips devices that disallow journal data, rejects unresized small images, computes default as 1/128 device clamped by minimum and RAM/bucket size, and allocates.
  - `bch2_fs_journal_alloc()` ensures each online member has journal buckets.
- Stops journal writes to a device:
  - `bch2_journal_writing_to_device()` scans in-flight journal buffers for device references.
  - `bch2_dev_journal_stop()` waits until no in-flight journal write targets the device and cancels its discard work.
- Stops filesystem journal in `bch2_fs_journal_stop()`:
  - Stops reclaim.
  - Flushes all pins.
  - Writes metadata journal entry to synchronize clock hands.
  - Quiesces shutdown until write completion bookkeeping drains.
  - Cancels delayed write work.
  - Clears running flag if no journal error.
- Starts journal in `bch2_fs_journal_start()`:
  - Advances `cur_seq` beyond blacklisted sequences.
  - Allocates and initializes pin FIFO sized for replay window plus safety margin.
  - Initializes replay sequence, on-disk sequence, flushed sequence, pin front/back, atomic seq, and in-flight FIFO alignment.
  - Marks unreplayed pin entries.
  - Loads journal replay entries into pin lists, computes replicas from read pointers, validates superblock replica markings, and refs replica entries.
  - Tracks last empty sequence.
  - Initializes reservation index and reclaims referenced replicas.
- Marks replay done in `bch2_journal_set_replay_done()`:
  - Recomputes space.
  - Sets need-flush-write, running, and replay-done flags in the required order.
- Per-device lifecycle:
  - `bch2_dev_journal_init_early()` initializes discard lock/work.
  - `bch2_dev_journal_init()` reads journal bucket lists from v1 or v2 superblock fields, allocates `bucket_seq`, initializes bioset, and expands v2 ranges into the bucket array.
  - `bch2_dev_journal_exit()` frees bioset and arrays.
- Filesystem journal lifecycle:
  - `bch2_fs_journal_init_early()` initializes locks, delayed work, waitqueues, reclaim lock, lockdep map, and closed reservation state.
  - `bch2_fs_journal_init()` allocates free journal buffer, in-flight FIFO storage, journal write workqueue, and discard workqueue.
  - `bch2_fs_journal_exit()` destroys workqueues, frees early entries and rewind ranges, frees leftover in-flight buffers on error paths, and frees pin/free-buffer storage.

Important interactions:
- Journal bucket allocation uses allocator foreground APIs and btree transactional metadata marking.
- Superblock journal fields are updated through `bch2_journal_buckets_to_sb()` and `bch2_write_super()`.
- Startup depends on replay entries from `journal/read.c`.
- Shutdown depends on reclaim and journal write completion logic.
- Replica refs for journal entries integrate with allocation/accounting correctness.

Notable invariants:
- Journal bucket count reduction is not supported by `bch2_set_nr_journal_buckets_loop()` except explicit delete path.
- `bch2_fs_journal_start()` refuses sequence overflow and prevents reuse of blacklisted sequences.
- Pin FIFO front/back must align to journal sequence numbers.
- `JOURNAL_running` is not set until replay completion via `bch2_journal_set_replay_done()`.
