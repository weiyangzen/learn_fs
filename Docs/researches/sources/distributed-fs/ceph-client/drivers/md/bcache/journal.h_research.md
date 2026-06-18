# sources/distributed-fs/ceph-client/drivers/md/bcache/journal.h

Purpose: documents and declares the journal subsystem data structures and APIs. The design comment explains the circular bucket journal, ordered key replay, superblock-like metadata in journal headers, open-entry pin FIFO, reclaim rules, and full-journal flushing strategy.

Important APIs/types: `struct journal_replay` holds variable-size jsets read during registration plus an optional pin. `struct journal_write` is one of two staged/in-flight write buffers and has a closure waitlist for synchronous callers. `struct journal` lives in `cache_set` and contains locks, flush state, delayed work, sequence number, pin FIFO, current journal pointer, and write buffers. `struct journal_device` lives in `cache` and tracks per-bucket sequence, current and last journal bucket indexes, and a reusable bio. Macros include `journal_pin_cmp()`, `journal_full()`, `JOURNAL_PIN`, and `BTREE_FLUSH_NR`.

Control flow: callers append keys through `bch_journal()` and receive an `atomic_t` pin used by B-tree dirty writes. `bch_journal_next()` advances the sequence and switches write buffers. Recovery uses `bch_journal_read()`, `bch_journal_mark()`, and `bch_journal_replay()`. Allocation/free are handled by `bch_journal_alloc()` and `bch_journal_free()`.

State and persistence: the header defines the in-memory state that protects journal persistence. The pin FIFO length determines the oldest needed sequence, which becomes `last_seq` in new journal entries and prevents circular overwrite of unreplayed changes.

Dependencies/integration: forward-declares closure, cache set, B-tree op, and keylist; relies on on-disk `struct jset`, `BKEY_PADDED`, and superblock journal bucket constants from bcache headers.

Risks/test signals: the header notes that non-journaled `BTREE_REPLACE` is fragile for incremental GC. Since refcounts are decremented without resizing locks, `JOURNAL_PIN` capacity is a correctness constraint. Tests should stress pin FIFO exhaustion, old-entry reclaim, sync flush waiters, and B-tree writes holding the oldest pin.
