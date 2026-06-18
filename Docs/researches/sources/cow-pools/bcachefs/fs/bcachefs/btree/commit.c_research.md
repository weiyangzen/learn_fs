# File Research: sources/cow-pools/bcachefs/fs/bcachefs/btree/commit.c

This file implements the btree transaction commit path: update validation, write locking, journal reservation and logging, trigger execution, leaf/key-cache mutation, split/merge recovery, and replay-mode commit handling.

Core responsibilities:
- Formats transaction commit flags via `bch2_trans_commit_flags_to_text()`.
- Verifies cached old-key state in debug builds with `verify_update_old_key()`, including journal replay overlay checks.
- Acquires write locks for all updated nodes with `bch2_trans_lock_write()` and rolls them back on would-deadlock restarts.
- Prepares nodes for append by running post-write cleanup and opening a new bset when `want_new_bset()` says the current append area is full.
- Implements `bch2_btree_bset_insert_key()`, the core non-extent insert/delete/overwrite routine for a node bset.
- Adds journal pins to dirty btree nodes and supplies flush callbacks for journal reclaim.
- Implements `bch2_btree_insert_key_leaf()`, which applies a committed leaf update, sets dirty/write state, records journal sequence, updates sibling-size estimates, and compacts whiteouts opportunistically.
- Handles cached btree-key insertion capacity, including a slow path that drops locks to allocate larger cached-key storage.
- Runs transactional, atomic, and GC triggers in the correct order through `bch2_trans_commit_run_triggers()`, `run_one_mem_trigger()`, and `run_one_trans_trigger()`.
- Builds journal entries for overwrites, btree keys, write-buffer/accounting keys, and optional transaction-name logs.
- Validates journal entries and bkeys before making in-memory changes.
- Coordinates journal replay overwrite dropping via `bch2_check_drop_overwrites_from_journal()`.
- Handles retryable commit failures: node full, journal reservation blocking, key-cache flush pressure, accounting replica marking, and split races.
- Provides `do_bch2_trans_commit_to_journal_replay()` for early fsck/recovery updates before the filesystem has gone read-write.
- Implements writeback pressure throttling for excessive dirty/in-flight btree nodes.
- Exposes `__bch2_trans_commit()`, the top-level commit state machine.

Commit flow:
- Skip empty transactions and optionally throttle on dirty/in-flight btree write pressure.
- Run transactional triggers; they may append more updates.
- Drop no-op updates except inode no-ops, because inode fsync depends on updated journal sequence behavior.
- Acquire the filesystem write reference unless disabled by flags.
- Calculate journal reservation size from btree updates, accounting deltas, extra journal entries, and optional overwrite logging.
- Upgrade paths to the required intent depth.
- Add extra disk reservation if requested.
- Retry `do_bch2_trans_commit()` until success or a non-recoverable error.
- On success, downgrade transaction locks, reset updates, and trace the commit.

Important invariants:
- Once a journal reservation is acquired, the commit path is structured so normal failures are no longer allowed; the reservation must be consumed or explicitly unwound.
- Write locks are taken once per distinct leaf for grouped updates.
- Inserted keys must match the transaction path position, cached state, level, btree ID, and expected bkey type.
- Atomic trigger failures that imply filesystem inconsistency are fatal.
- GC triggers run only for updates whose GC position has already been visited.
- Journal replay commits synchronize with `c->journal_keys.overwrite_lock` so replay overlays and real btree state do not diverge.
- Key-cache dirty pressure can force journal reclaim waits before cached updates are accepted.

Dependencies:
- Deeply depends on bcachefs allocation/accounting, journal, btree iterator/path, interior split/merge, key cache, write buffer, snapshot, and validation subsystems.
- Calls into `interior.c` via `bch2_btree_split_leaf()` and `bch2_foreground_maybe_merge()` when a node is full or should be merged.
- Uses `check.h` GC ordering to decide whether to run GC-trigger variants.

Risk points:
- Trigger ordering is subtle: for a given btree, insert triggers are intentionally run before overwrite triggers to avoid transient reference drops during moves.
- The path after journal reservation has very limited tolerance for ordinary errors.
- Cached key reallocation mutates pointers that existing update entries may reference; the code updates `old_v` aliases explicitly.
- Replay-mode overwrite handling must stay synchronized with the journal overlay or recovery can duplicate/drop updates.
- Node split error handling can restart transactions; callers must tolerate path array relocation and restart semantics.
