# File Research: sources/cow-pools/bcachefs-tools/fs/btree/commit.c

## Purpose

`commit.c` implements btree transaction commit. It is the core path that turns staged `btree_insert_entry` updates into journal records, accounting changes, trigger side effects, btree/key-cache mutations, and retryable structural changes such as splits and merges.

The file coordinates ordering between locks, journal reservation, triggers, disk accounting, GC interaction, and recovery/journal replay.

## Main Flow

The top-level function is `__bch2_trans_commit()`:

1. Validate transaction state and maybe inject a restart.
2. Return early if there are no updates.
3. Run transactional triggers, which may append more updates.
4. Compute journal space requirements.
5. Drop no-op updates unless flags require keeping them.
6. Upgrade relevant paths to intent locks.
7. Possibly perform foreground merges before inserting.
8. Acquire extra disk reservation if requested.
9. If filesystem cannot take a write ref and commit is allowed during recovery, route to journal-replay overlay commit.
10. Retry the real commit loop:
   - lock update nodes for write,
   - reserve journal space,
   - run hooks/accounting/atomic triggers/GC triggers,
   - validate in debug builds,
   - fill journal entries,
   - mutate btree leaves or cached keys,
   - handle retryable errors.
11. Release write ref, downgrade transaction locks, and reset updates.

## Commit Flags

`bch2_trans_commit_flags_to_text()` prints the watermark and named commit flags for diagnostics.

Flags influence:

- journal reservation requirements,
- ENOSPC behavior,
- journal replay behavior,
- whether no-op updates are skipped,
- watermark escalation for btree structural work,
- whether journal reclaim paths are allowed.

## Write Locking

- `bch2_trans_lock_write_inlined()` takes write locks for update target nodes, skipping duplicate locks when consecutive updates hit the same leaf.
- `bch2_trans_unlock_updates_write()` releases write locks for all updated nodes.
- `bch2_btree_node_prep_for_write()` handles post-write cleanup and starts a new bset when the current append area is written or too large.

The file carefully separates intent locks already held by paths from write locks needed for final mutation.

## Leaf Insertion

`bch2_btree_bset_insert_key_inlined()` performs the final in-node insert/delete for non-extent overwrites:

- Validates position, node range, and space.
- Finds an existing key at the insert position.
- Marks overwritten keys deleted.
- Preserves whiteout needs when deleting already-written keys.
- Inserts into the writable current bset or appends if the old key is in a written bset.
- Fixes node iterators when key size changes.

`bch2_btree_insert_key_leaf()` wraps this with topology checks for interior nodes, journal sequence stamping, journal pinning, dirty marking, sibling size estimate updates, and whiteout compaction.

## Journal Pinning and Flush

- `__btree_node_flush()` is called when journal reclaim needs a pinned btree node written.
- `bch2_btree_node_flush0()` and `bch2_btree_node_flush1()` dispatch by write slot.
- `bch2_btree_add_journal_pin()` pins the current btree write slot to a journal sequence.

Pinned journal entries prevent reclaim until the corresponding btree write is durable.

## Insert Feasibility

- `btree_key_can_insert()` checks whether a normal btree node can fit pending updates and may wait for btree writeback pressure to drop.
- `btree_key_can_insert_cached()` handles key-cache sizing and journal reclaim pressure.
- `btree_key_can_insert_cached_slowpath()` can allocate a larger cached-key buffer after dropping locks, then relock.

Failure with `btree_insert_btree_node_full` is handled by splitting the leaf in the commit error path.

## Triggers

Two trigger classes are handled:

### Transactional Triggers

`bch2_trans_commit_run_triggers()` runs transactional triggers before the final commit. They may append further updates, so the code loops through sort-order groups until all insert/overwrite trigger halves have run.

The insert-before-overwrite ordering for a given btree avoids transiently dropping references before re-adding them, important for extent moves.

### Atomic and Memory Triggers

During final commit:

- `run_one_mem_trigger()` runs non-transactional memory/accounting triggers.
- `run_one_trans_trigger()` runs transactional trigger halves.
- `bch2_trans_commit_run_gc_triggers()` runs GC triggers only for positions GC has already visited, preserving concurrent GC correctness.

## Accounting

Accounting entries in `trans->accounting` are applied under `capacity.mark_lock`.

- `bch2_accounting_trans_commit_hook()` applies accounting.
- `trans_commit_accounting_revert()` rolls back applied accounting on failure.
- `bch2_trans_account_disk_usage_change()` applies accumulated disk usage deltas.

In early fsck/recovery, `do_bch2_trans_commit_to_journal_replay()` applies accounting and inserts updates into the journal overlay rather than the live btree.

## Journal Construction

`bch2_trans_commit_write_locked()` fills the journal reservation after all non-fatal failure points have passed:

- Optional transaction-name log entry.
- Optional overwrite records when transaction names are enabled.
- `BCH_JSET_ENTRY_btree_keys` for normal updates.
- Prebuilt transaction journal entries.
- Accounting updates as `BCH_JSET_ENTRY_write_buffer_keys`.
- Optional external journal sequence return.
- Optional journal pin.

After journal fill, it applies updates to btree leaves or key cache.

## Journal Replay Path

When recovery has not completed, commits go through:

- `trans_commit_to_journal_replay_pre()`
- `bch2_check_drop_overwrites_from_journal()`
- `do_bch2_trans_commit_to_journal_replay()`
- `trans_commit_to_journal_replay_post()`

This path inserts updates into the journal-key overlay and handles root journal entries without performing normal RW btree mutation.

## Error Handling and Retries

`bch2_trans_commit_error()` handles retryable failures:

- Journal reservation blocked: drop locks and acquire/wait.
- Btree node full: split leaf and restart if needed.
- Need mark replicas: update superblock accounting.
- Need journal reclaim: unlock, wait for key-cache/journal reclaim, relock.
- Nested commits with `no_journal_res`: force transaction restart.

Fatal errors call `bch2_fs_fatal_error()` or emergency read-only paths.

## Structural Merge Integration

During no-op compaction and update preparation, the commit path can call `trans_commit_merge()` when a target btree node is below merge threshold. This escalates watermarks, invokes `__bch2_foreground_maybe_merge()`, and then repairs update-array pointers because path-table reallocations can move `trans->updates`.

## Important Invariants

- No journal reservation is taken until the code believes inserts can fit.
- After journal reservation, failures are treated as fatal or must be handled without abandoning the reservation.
- Trigger execution must be complete before journal fill and in-memory mutation.
- No-op inode updates are retained because fsync depends on updated journal sequence state.
- GC triggers run only for GC-visited positions.
- Btree structural changes are retryable and expressed as transaction restarts.
- Commit must leave locks verifiable after every retry path.
