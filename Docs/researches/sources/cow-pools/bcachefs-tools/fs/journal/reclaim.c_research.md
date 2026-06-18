# File Research: sources/cow-pools/bcachefs-tools/fs/journal/reclaim.c

This file implements journal space accounting, discard advancement, journal entry pin management, and journal reclaim for bcachefs-tools.

Key responsibilities:
- Computes per-device and aggregate journal availability through `bch2_journal_dev_buckets_available()`, `journal_dev_space_available()`, `__journal_space_available()`, and `bch2_journal_space_available()`.
- Maintains journal pressure flags and write watermark state in `bch2_journal_set_watermark()`.
- Drives discard of no-longer-dirty journal buckets with `bch2_journal_discard_work()`, `bch2_journal_do_discards()`, and per-device discard work.
- Tracks pinned journal sequences and advances `last_seq` / `last_seq_ondisk`.
- Provides APIs for pin set, add, update, copy, drop, replay put, and flush synchronization.
- Implements background and direct reclaim, including the reclaim kthread lifecycle.
- Exposes diagnostic text for pins, reclaim counters, blocked time stats, and reclaim thread backtraces.

Important control flow:
- Space accounting advances `dirty_idx` and `dirty_idx_ondisk` based on `last_seq` and `last_seq_ondisk`.
- Available space is calculated from the top `metadata_replicas` journal devices, then constrained by the smallest aligned bucket size.
- Dirty journal space is capped by a RAM-derived budget for soft throttling, while `next_entry` remains uncapped to avoid self-deadlock.
- Reclaim chooses a `seq_to_flush` from half-full journal devices and pin FIFO pressure.
- `journal_flush_pins()` selects eligible unflushed pins by type and sequence, calls the pin flush callback, then moves pins to flushed lists unless they were dropped or rearmed.
- `bch2_journal_flush_pins()` loops through pin types from lower priority to higher order so shutdown flushing can converge even when pin flushing generates more pins.

Important invariants:
- Journal bucket ring indexes obey `discard_idx <= dirty_idx_ondisk <= dirty_idx <= cur_idx` modulo the ring.
- The last bucket is held back unless writing a new `last_seq` will free another bucket.
- Pin FIFO entries hold a count for the journal entry itself, btree nodes, key cache entries, and replay references.
- `pin->seq == 0` means inactive.
- Pin list locks are acquired in sequence order when moving/copying pins across lists.
- Reclaim holds `j->reclaim_lock` and uses `PF_MEMALLOC_NOFS` to avoid recursion through memory reclaim.
- Flush callbacks must be present because diagnostics identify pins by callback function.

Dependencies:
- Uses allocator/device membership helpers, replica accounting, btree key cache and write buffer flush hooks, journal core state, counters, and member device APIs.
- Uses kernel workqueues, kthreads, closures, wait queues, RCU, spinlocks, mutexes, and printbuf diagnostics.

Research notes:
- This is one of the main liveness files for the journal. Incorrect space accounting can stall journal writers or cause premature throttling.
- The RAM/4 dirty budget comments document a subtle design: it influences the watermark ratio but must not clamp hard entry reservation capacity.
- Pin flushing order is part of clean shutdown correctness because btree writes can recursively create more journal dependencies.
