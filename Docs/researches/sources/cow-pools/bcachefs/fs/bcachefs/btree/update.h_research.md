# File Research: sources/cow-pools/bcachefs/fs/bcachefs/btree/update.h

This header declares B-tree mutation and transaction commit APIs.

Key areas:
- Node write-preparation and leaf insertion declarations used by commit/write-buffer paths.
- Journal pin helpers for B-tree nodes.
- Transaction commit flags, including no-ENOSPC, no-RW-check, no-journal-reservation, journal reclaim, replay, and accounting-skip behavior.
- Insert/delete/delete-range/bit-update APIs.
- Snapshot whiteout helpers and `extent_whiteout_type()` policy.
- `bch2_trans_update()` wrappers that pass buffer size and call-site IP.
- Transaction subbuffer allocation for journal entries and accounting updates inside `btree_trans`.
- Commit wrappers `commit_do()` and `nested_commit_do()` around lock-restart loops.
- Mutable-key helpers for copying, modifying, getting, and allocating bkeys in the transaction arena.
- Buffered update helper that writes a key into a transaction journal entry for later write-buffer intake.

Important invariants:
- Transaction memory is restart-scoped and invalidated on restart.
- Buffered updates to non-write-buffer btrees are considered inconsistent.
- During journal replay, most write-buffered updates are inserted directly except accounting and `need_discard` deltas that must preserve ordered replay semantics.
