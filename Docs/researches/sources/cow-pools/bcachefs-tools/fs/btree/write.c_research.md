# File Research: sources/cow-pools/bcachefs-tools/fs/btree/write.c

Read completeness: full file read, 852 lines.

Purpose: btree node write serialization, metadata validation, checksum/encryption, bio submission, completion processing, post-write cleanup, write flushing, cancellation, and write statistics.

Major components:
- `__btree_node_write_done()` drops previous write journal pins, clears or rearms dirty/write flags atomically, releases reachability closures for first writes, updates in-flight counters, and wakes waiters.
- `btree_node_write_update_key()` updates the parent/interior btree pointer after a write, copying new `sectors_written`, dropping failed pointers, marking keys needing reconcile after degraded writes, and committing with reclaim-safe flags.
- `btree_node_write_work()` runs after IO completion, optionally updates the parent key, logs hard/degraded write failures, updates timing stats, then takes a read lock on the node to call `__btree_node_write_done()`.
- `btree_node_write_endio()` records device write failures, releases device refs, frees bounce data, clears inner in-flight state, and queues completion work.
- `validate_bset_for_write()` validates the node key, bset keys, and bset header in write mode before/after checksum depending on encryption/version requirements.
- `__bch2_btree_node_write()` is the core writer. It atomically claims dirty state, sorts whiteouts, builds a disk bset in a bounce buffer, validates, encrypts/checksums, checks journal/nochanges constraints, allocates a `btree_write_bio`, updates `b->written` and pointer sectors, updates stats, and queues the bio on `trans->queued_write_bios`.
- `bch2_trans_submit_write_bios()` submits queued write bios after locks are dropped or before a wait.
- `bch2_btree_post_write_cleanup()` compacts/sorts in-memory bsets after a write, resets whiteout flags, initializes a new bset if space policy wants one, and rebuilds aux trees.
- `bch2_btree_node_write_trans()` handles write attempts under read/intent/write locks, including opportunistic cleanup under write lock.
- `bch2_btree_init_next()` ensures an unwritten bset exists for future inserts, writing or compacting the node first if it hit `MAX_BSETS`.
- Flush/cancel helpers wait for all reads/writes across hashed and freeable nodes, and `bch2_btree_cancel_all_writes()` clears dirty state during journal-error shutdown.

Control-flow and invariants:
- Writes are never submitted to the block layer while btree node locks are held; bios are queued on the transaction and submitted on unlock/wait.
- `write_in_flight` and `write_in_flight_inner` distinguish whole write lifecycle from lower-level IO completion.
- Initial writes require `b->written == 0`; later writes append btree node entries at block-aligned offsets.
- Journal errors or `nochanges` prevent issuing the write after the in-memory node has been serialized enough to keep lifecycle expectations consistent.
- Completion can rearm another write if the node was redirtied and still needs a write.

Dependencies and integration:
- Uses interior update helpers, read validation, sort/whiteout helpers, data write submission, reconcile triggers, async object tracking, journal reclaim, and cache state transitions.
- Public declarations are in `write.h`; read code calls flush-all-read declaration through this implementation file.

Risks and validation notes:
- The write lifecycle invariant ties `b->will_make_reachable` to initial writes; violations trigger a diagnostic and `BUG()`.
- Failure handling currently does not retry failed btree writes like normal data writes; severe failures can force emergency read-only.
- Parent-key update must not run when the journal is dead, because publishing unjournaled interior updates would break recovery.
