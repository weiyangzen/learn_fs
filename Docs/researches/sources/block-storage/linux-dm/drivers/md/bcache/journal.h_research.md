# File Research: sources/block-storage/linux-dm/drivers/md/bcache/journal.h

`journal.h` documents and declares bcache's journal model. The comments explain the circular bucket journal, ordered-key replay, open journal entry tracking via a refcount FIFO, and reclaim policy based on the oldest still-pinned journal entry. It also records a known fragility: `BTREE_REPLACE` operations are not journaled, so writeback and moving GC rely on flushing btree state around related metadata updates.

The replay data structure is `struct journal_replay`, a list node plus optional pin pointer and an inline variable-sized `jset`. The write-side staging unit is `struct journal_write`, which owns a `jset` buffer, waitlist, dirty flag, and need-write flag.

`struct journal` is embedded in `struct cache_set`; it contains the spinlocks, full-journal waitlist, I/O closure, delayed flush work, free block count, sequence counter, pin FIFO, current journal key, and two alternating `journal_write` buffers. `struct journal_device` is embedded in each `struct cache`; it records sequence numbers per journal bucket, current/last/discard bucket indexes, discard state, discard work/bio, and a reusable bio for journal I/O.

Important constants include `JSET_BITS` for journal buffer order, `BTREE_FLUSH_NR` for bounded old-entry flush work, `JOURNAL_PIN` for pin FIFO capacity, and `journal_full()` for the write path's full condition. Public functions cover journaling keys, advancing entries, marking/replaying journal lists, metadata journaling, reading replay lists, allocation, and free.
