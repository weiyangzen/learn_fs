# Group Research: group_207_bcachefs_sources_cow_pools_bcachefs_fs_bcachefs_btree_locking_h_sour_9c8cd141c578

Scope: `Docs/research_subset_a.md`, focused on bcachefs B-tree locking, node scan/recovery, read/validation, sorting/compaction, transaction updates, node writeback, and write-buffer batching.

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/btree/locking.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/btree/locking.h

This header defines the internal B-tree iterator/path locking API. It maps `six_lock` modes onto path-level state in `btree_path.nodes_locked`, tracks what locks a path wants, and provides inline helpers for lock acquisition, unlock, relock, upgrade, and verification.

Key responsibilities:
- Encodes lock state per B-tree level as unlocked/read/intent/write.
- Wraps `six_lock` operations while keeping `btree_path` bookkeeping in sync.
- Pins transactions to the current CPU and sets `PF_MEMALLOC_NOFS` while B-tree locks are held.
- Supports no-path node locking by creating temporary paths for deadlock detection and release.
- Handles write-lock downgrades/unlocks with lock sequence updates so relock validation can detect modifications.
- Exposes debug verification hooks gated by `bch2_debug_check_btree_locking`.

Important invariants:
- A write lock is represented as an intent lock plus write state; unlock of write first calls `bch2_btree_node_unlock_write`.
- Lock ordering and lock wait state feed the transaction deadlock detector.
- `path->l[level].lock_seq` must match `six_lock_seq()` when upgrading to write.
- `should_be_locked` paths cause transaction restarts if relock fails.

Dependencies include `btree/cache.h`, `btree/iter.h`, `locking_types.h`, and `util/six.h`.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/btree/locking.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/btree/locking_types.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/btree/locking_types.h

This header declares the small data structures used by the B-tree lock cycle detector.

Key types:
- `struct trans_waiting_for_lock`: records a transaction waiting for a node, desired `six_lock_type`, iteration state over held locks, and a preallocated waitlist snapshot of conflicting transactions.
- `struct lock_graph`: fixed-depth graph workspace with up to eight wait-chain entries plus a flag for whether the chain was printed.

Important behavior:
- The waitlist is cached at snapshot time so traversal is stable against concurrent wakeups.
- It carries both the node wanted and the node currently held while walking dependency chains.

Dependencies include `util/darray.h`, `util/six.h`, and `btree/types.h`.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/btree/locking_types.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/btree/node_scan.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/btree/node_scan.c

This file implements recovery-time scanning for B-tree nodes on disk. It is used when normal topology or roots cannot fully recover a B-tree and the filesystem must discover valid node replicas directly from member devices.

Key flow:
- Worker threads scan devices that allow B-tree data, using the device B-tree bitmap when available.
- `try_read_btree_node()` reads candidate node headers, checks magic, decrypts enough header fields if needed, validates btree id/level bounds, then reads the full node and calls `bch2_btree_node_read_done()`.
- Found nodes are stored as `found_btree_node` records with btree id, level, sequence, journal sequence, cookie, key range, sectors written, and replica pointers.
- `bch2_scan_for_btree_nodes()` merges replicas by cookie, sorts by position, and resolves overwritten ranges by comparing node sequence/journal time.
- Final nodes are Eytzinger-sorted for range lookup.
- `bch2_get_scanned_nodes()` converts scanned nodes back into btree pointer keys and inserts them into the journal overlay for recovery.

Important invariants:
- Duplicate replicas are grouped by node cookie.
- Overlapping nodes at the same btree/level are trimmed or discarded using recency.
- Big-endian scanned nodes are rejected because this path cannot perform full endian conversion.
- Only btrees marked recoverable-from-scan are exposed through `bch2_get_scanned_nodes()`.

Dependencies include bucket generation lookup, B-tree read validation, journal overlay insertion, recovery passes, kthreads, and heap/sort helpers.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/btree/node_scan.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/btree/node_scan.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/btree/node_scan.h

This header exposes the B-tree node scan recovery interface.

Public functions:
- `bch2_found_btree_node_to_text()` renders a scanned node and its replica pointers.
- `bch2_scan_for_btree_nodes()` performs the full device scan and normalizes the result list.
- `bch2_btree_node_is_stale()` checks whether a loaded node is older than a scanned overlapping node.
- `bch2_btree_has_scanned_nodes()` checks if scanned recovery data exists for a btree.
- `bch2_get_scanned_nodes()` emits scanned nodes into recovery output and the journal overlay.
- Init/exit helpers manage `struct find_btree_nodes`.

This is a narrow recovery API consumed by topology repair and node-read paths.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/btree/node_scan.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/btree/node_scan_types.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/btree/node_scan_types.h

This header defines the data model for scanned B-tree nodes.

Key types:
- `found_btree_node`: compact record for a discovered node, including range, btree id, level, sequence, journal sequence, cookie, written sectors, range-update flag, and up to `BCH_REPLICAS_MAX` extent pointers.
- `darray_found_btree_node`: dynamic array of discovered nodes.
- `find_btree_nodes`: scan state containing a return code, mutex, and node array.

The scan state is embedded in `struct bch_fs_btree` and shared between scan workers and recovery consumers. The mutex protects concurrent worker appends to the discovered node array.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/btree/node_scan_types.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/btree/read.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/btree/read.c

This file implements B-tree node read, validation, repair-on-read, read retry, root read, and scrub logic.

Major responsibilities:
- Manages `BTREE_NODE_read_in_flight` and `BTREE_NODE_write_in_flight` wait bits.
- Validates bset headers: metadata version, checksum type, sector offset, magic, btree id, level, sequence, min/max keys, and key format.
- Validates bset keys for size, format, order, key range, value semantics, and compatibility conversions.
- During read completion, walks all written bsets, verifies checksums, decrypts if needed, skips blacklisted journal sequences, and merges sorted keys into a single in-memory bset.
- Drops invalid keys when fsck permits repair and marks nodes needing rewrite.
- Retries failed reads against alternate replicas using `bch2_bkey_pick_read_device()`.
- Logs soft versus hard read errors and schedules rewrite/repair when needed.
- Reads roots synchronously into the B-tree cache.
- Scrubs individual B-tree node replicas by rereading and checksum-validating them, then scheduling rewrite on failure.

Important invariants:
- In-memory loaded nodes are normalized to one sorted bset with rebuilt auxiliary trees.
- `btree_ptr_v2.sectors_written` governs how much node data is expected from disk.
- Updated-range B-tree pointers can cause keys outside the adjusted node bounds to be dropped.
- Write-side validation failure forces emergency read-only rather than silent corruption.

Dependencies include checksum/encryption helpers, extent/device picking, journal sequence blacklist, async object tracking, B-tree sort, locking, update, and recovery error handling.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/btree/read.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/btree/read.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/btree/read.h

This header defines the B-tree read API and compatibility helpers.

Key elements:
- `btree_ptr_sectors_written()` extracts written-sector count from `btree_ptr_v2`.
- `bch2_bkey_in_btree_node()` validates key position against a node’s min/max range.
- `struct btree_read_bio` carries asynchronous read state, selected replica, work item, and bio.
- IO lock/wait declarations protect node read/write in-flight state.
- `btree_nonce()` and `bset_encrypt()` define metadata encryption/decryption nonce handling for first and subsequent bsets.
- Compatibility helpers transform old on-disk formats for inode btree changes, snapshot fields, endian conversion, and min/max key semantics.

The header connects read.c to B-tree cache, checksum, extents, fsck validation, and write/scrub consumers.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/btree/read.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/btree/sort.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/btree/sort.c

This file implements B-tree key sorting, repacking, whiteout handling, and node compaction.

Key behavior:
- `sort_iter` merges multiple already-sorted bset ranges.
- `bch2_key_sort_fix_overlapping()` builds a clean set from read bsets, dropping deleted keys and older duplicate-position keys.
- `bch2_sort_repack()` rewrites keys into a new key format, optionally filtering whiteouts.
- `bch2_sort_keys_keep_unwritten_whiteouts()` is used by writeback to preserve only whiteouts that still matter for unwritten data.
- `bch2_sort_keys()` compacts in-memory nodes and drops deleted keys.
- Bounce-buffer helpers allocate from `kvmalloc()` first and fall back to a mempool.
- `bch2_sort_whiteouts()`, `bch2_drop_whiteouts()`, and `bch2_compact_whiteouts()` clean whiteout storage.
- `bch2_btree_node_sort()` merges a range of bsets and updates `btree_nr_keys`, bset offsets, and aux-tree state.
- `bch2_btree_node_compact()` decides which written/unwritten bsets to merge when a node is near the `MAX_BSETS` limit.
- `bch2_btree_build_aux_trees()` rebuilds search trees for each bset.

Important invariants:
- Bsets are individually sorted; merge iterators exploit this.
- Whiteouts are treated differently for read normalization, in-memory compaction, and writeback.
- After compaction, key accounting and auxiliary trees must be rebuilt.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/btree/sort.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/btree/sort.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/btree/sort.h

This header declares B-tree sorting and compaction APIs.

Key definitions:
- `struct sort_iter` and `struct sort_iter_stack` hold multiple bset key ranges for merge-sort style processing.
- `sort_iter_add()` appends a non-empty key range.
- Sorting APIs cover read-time overlap repair, repacking, writeback sorting with unwritten whiteouts, and ordinary deleted-key filtering.
- Whiteout APIs support marking, sorting, dropping, lazy compaction, and full compaction.
- Node APIs support sorting selected bset ranges, sorting into another node, compacting a node, and rebuilding auxiliary search trees.

Important policy:
- Lazy whiteout compaction triggers when dead key space is both large and a substantial fraction of a bset.
- `should_compact_all()` uses a geometric-size heuristic to decide if `MAX_BSETS` should collapse to fewer sets.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/btree/sort.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/btree/types.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/btree/types.h

This is the central type definition header for bcachefs B-tree state.

Major structures:
- `btree_nr_keys`: live metadata and per-bset key accounting.
- `bset_tree`: offsets and aux-tree layout for one bset.
- `btree_bkey_cached_common`: shared lock/id/level/cached fields for B-tree nodes and cached keys.
- `struct btree`: cached B-tree node state, including cache membership, flags, format, data buffer, bsets, write pins, key pointer, async interior-update blockers, open buckets, and LRU/cache list links.
- `bch_fs_btree_cache`: root state, rhashtable, freeable/freed/live node lists, inflight counters, shrinker stats, allocation cannibalization state, and pinned-node metadata.
- `btree_path` and `btree_iter`: low-level locked traversal path and high-level key iterator.
- `btree_insert_entry`: pending transaction update entry.
- `btree_trans`: transaction context with paths, sorted lock order, updates, bump allocator, journal reservation/subbuffers, locks, restart state, hooks, and embedded initial storage.
- `bch_fs_btree`: filesystem-level B-tree subsystem including cache, key cache, write buffers, trans pool, reserve cache, interior updates, node rewrites, and node scan state.

Important flags and policy:
- Defines iterator/update/trigger flag bits, transaction path limits, write types, node flags, and rewrite reasons.
- Encodes btree id properties such as extent behavior, snapshots, data pointers, write-buffer usage, and trigger ordering.
- Provides inline accessors for bsets, keys, node offsets, live/dirty cache counts, current/previous write pins, and node rewrite reason.

This file is the shared contract for nearly every file in the B-tree subsystem.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/btree/types.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/btree/update.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/btree/update.c

This file implements transaction-facing B-tree mutation helpers.

Key behavior:
- Maintains sorted pending updates by trigger order, cached/noncached status, level, and key position.
- Handles extent insertion by merging with adjacent compatible extents and splitting overwritten extents into front/middle/back fragments.
- Emits snapshot whiteouts when deletes or splits would otherwise expose ancestor snapshot keys incorrectly.
- Routes cached-btree leaf updates through the key cache when required for coherency.
- Records old overwritten keys from either the B-tree path or journal overlay during replay.
- Provides helpers to grow trigger-mutated new keys safely before atomic trigger phase.
- Implements public insert, delete, delete-range, bit-set/clear, and buffered bit update operations.
- Provides transaction log entries for strings and bkeys, with early-journal fallback before the journal is running.

Important invariants:
- Pending updates own path references until reset.
- Extent overwrite handling preserves snapshot visibility and reserves extra disk space for compressed extent splits.
- Cached key updates must ensure the key also exists in the underlying B-tree.
- Write-buffered updates are journaled as `BCH_JSET_ENTRY_write_buffer_keys` unless replay rules require direct insertion.

Dependencies include iterators, journal overlay, locking, keylist/data extent helpers, snapshot logic, and journal transaction commit.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/btree/update.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/btree/update.h -->
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
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/btree/update.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/btree/write.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/btree/write.c

This file implements low-level B-tree node writeback.

Key flow:
- `__bch2_btree_node_write()` atomically claims dirty nodes, builds a bounce buffer containing sorted unwritten keys and required whiteouts, validates metadata, encrypts/checksums the bset, and submits replica writes.
- Write completion updates IO accounting, records device failures, frees bounce buffers, and queues post-write work.
- Post-write work updates the B-tree pointer after first writes or degraded writes and then clears/rearms node write state.
- `__btree_node_write_done()` drops journal pins, handles `will_make_reachable`, re-arms writes if the node was dirtied again, or transitions the node clean.
- `bch2_btree_post_write_cleanup()` compacts written bsets, drops whiteouts, initializes the next writable bset, and rebuilds aux trees under write lock.
- `bch2_btree_init_next()` creates a new unwritten bset, compacting or writing first if the node is full.
- Flush helpers wait for all read/write in-flight bits, including freeable nodes no longer in the rhashtable.
- Cancel logic clears dirty nodes and drains writes when journal error/emergency read-only prevents clean shutdown.

Important invariants:
- First writes correspond to nodes not yet reachable; later writes must not run while `will_make_reachable` is set.
- A write may be rearmed if the node became dirty again before completion.
- Journal errors prevent submitting further B-tree writes to avoid exposing unjournaled updates.
- Writeback validation failure marks the node no-evict and can force emergency read-only.

Dependencies include read/checksum compatibility, sort/whiteout compaction, data write submission, reconciliation triggers, journal reclaim, cache state transitions, and async object tracking.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/btree/write.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/btree/write.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/btree/write.h

This header defines the B-tree writeback interface.

Key elements:
- `struct btree_write_bio`: write work item with copied btree pointer key, bounce data, byte/sector offsets, timing, optional async-object index, and embedded `bch_write_bio`.
- Write flags for “only if need” and “already started”.
- Declarations for node write submission, transaction-aware write, initializing the next bset, post-write cleanup, write stats rendering, flushing all writes, and cancelling writes.

This is consumed by cache, update/commit, node writeback, shutdown, and diagnostic paths.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/btree/write.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/btree/write_buffer.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/btree/write_buffer.c

This file implements the B-tree write buffer: a batching layer for btrees that receive many small updates, such as backpointers, LRU, discard, reconcile, stripe backpointers, deleted inodes, and accounting.

Key flow:
- Journal entries of type `BCH_JSET_ENTRY_write_buffer_keys` are fetched and staged into per-btree write-buffer instances.
- Each per-btree buffer has incoming (`inc`) and flushing buffers, both journal-pinned.
- Intake eagerly locks all per-btree buffers in ascending index order, accumulates accounting deltas, and adds journal pins.
- Flush moves incoming keys to the flushing buffer, builds compact key-position references, sorts them, collapses duplicate positions, and accumulates accounting duplicates.
- Fast path traverses the target leaf once per key range, keeps a write lock while keys stay in the same leaf, and inserts directly when the key fits.
- Slow path commits in journal sequence order when fast insertion would deadlock reclaim, when the key does not fit, or when accounting replay is not ready.
- Large sorted flushes shard across CPUs using a separate shard workqueue.
- Sync flushers fetch journal keys up to a target sequence, queue all relevant per-btree workers, and wait for pins at or below that sequence.
- Journal pin callbacks only queue the appropriate per-btree worker; they do not perform flushes inline.
- Startup/init allocate per-btree arrays and workqueues; exit asserts no buffered keys remain unless the journal is in error.

Important invariants:
- Write-buffer btree list is compile-time checked against `BTREE_IS_write_buffer` flags.
- Once a key enters the write buffer, it must flush using its original journal sequence to preserve recovery order.
- Duplicate same-position entries must be collapsed before sharded flush so older updates cannot race newer updates across shard boundaries.
- Accounting updates are deltas, so duplicates are accumulated rather than overwritten.
- `inc.pin` and `flushing.pin` ordering uses acquire/release care so sync flushers do not miss in-flight pins.

Dependencies include B-tree locking/update/interior APIs, journal read/reclaim, accounting accumulation, closure work, workqueues, Eytzinger sorting, and transaction restart handling.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/btree/write_buffer.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/btree/write_buffer.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/btree/write_buffer.h

This header exposes write-buffer indexing, intake, flush, accounting, diagnostics, lifecycle, and helper APIs.

Key elements:
- `bch_wb_btree_idx()` maps write-buffer-enabled `btree_id` values to dense `enum bch_wb_btree` indices.
- `bch_wb_btree_to_btree_id()` maps back to real B-tree IDs.
- Flush pressure helpers check per-btree and global buffer fullness.
- Public flush APIs cover sync flush, going-read-only flush, tryflush, and maybe-flush for check/repair code.
- `wb_maybe_flush` tracks the last key that triggered a repair-time flush to prevent repeated useless flushes.
- `journal_keys_to_wb` batches one journal buffer’s keys across all per-btree buffers.
- Accounting helpers use an Eytzinger-sorted accumulator array for fast delta coalescing.
- Write-buffered key iteration helpers treat the underlying darray as variable-sized records.

Important invariants:
- Buffered key entries do not store a btree id because the containing write buffer implies it.
- `wb_key_u64s()` includes the journal-sequence header plus the actual bkey.
- Journal intake reserves room per btree and falls back to slowpath when the selected buffer lacks capacity.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/btree/write_buffer.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/btree/write_buffer_types.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/btree/write_buffer_types.h

This header defines the core write-buffer data structures.

Key types:
- `BCH_WRITE_BUFFER_BTREES()` lists the dense set of write-buffer-enabled btrees.
- `enum bch_wb_btree` gives compact array indices for those btrees.
- `struct wb_key_ref` stores a sortable packed reference made from key position plus darray index.
- `struct btree_write_buffered_key` stores original journal sequence plus a padded bkey.
- `struct btree_write_buffer_keys` owns a darray of variable-sized key records, a journal pin, a mutex, and backrefs identifying the btree and whether this is the flushing side.
- `enum wb_flush_caller` records why a flush was requested.
- `struct bch_fs_btree_write_buffer` is the per-btree state: sorted references, incoming/flushing buffers, flush work item, diagnostics counters, and accounting accumulator array.

Important design:
- The per-btree split avoids storing btree id in each key.
- Accounting keys get a small fixed padded value limit for in-memory accumulation.
- Backrefs let journal-pin callbacks recover the owning buffer from only the pin pointer.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/btree/write_buffer_types.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/closure.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/closure.h

This tiny compatibility wrapper includes `vendor/closure.h` and aliases generic closure symbols to bcachefs-prefixed names.

Aliases:
- `closure_wait` to `bch2_closure_wait`
- `closure_return_sync` to `bch2_closure_return_sync`
- `__closure_wake_up` to `__bch2_closure_wake_up`
- `closure_sync_unbounded` to `bch2_closure_sync_unbounded`

It lets local bcachefs code use closure-style APIs while avoiding symbol collisions with external or vendored closure implementations.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/closure.h -->