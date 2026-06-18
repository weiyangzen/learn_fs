# Group Research: group_205_bcachefs_sources_cow_pools_bcachefs_fs_bcachefs_btree_check_h_source_d6e68046fd31

Scope checked against `Docs/research_subset_a.md`: `sources/cow-pools/bcachefs` is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/btree/check.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/btree/check.h

This header declares bcachefs btree checking and GC entry points, and defines inline helpers for ordering online garbage-collection progress against concurrent btree updates.

Core responsibilities:
- Declares full-btree consistency entry points: `bch2_check_topology()` and `bch2_check_allocations()`.
- Defines `gc_phase()` and `gc_pos_btree()` constructors for `struct gc_pos`.
- Defines `gc_btree_order()` so allocation and stripe btrees are ordered before ordinary btree IDs during GC.
- Defines `gc_pos_cmp()` as the total ordering for GC phases, btree IDs, levels, and key positions.
- Defines `gc_visited()` as a seqcount-protected check of whether a reference position is at or behind current GC progress.
- Declares GC diagnostics and operations: `bch2_gc_pos_to_text()`, `bch2_gc_gens()`, `bch2_gc_gens_async()`, `bch2_merge_btree_nodes()`, and early GC initialization.

Important invariants:
- Concurrent mark/sweep relies on a total order over all references GC walks.
- Callers that mark pointers must hold a lock preventing GC from passing their current reference position.
- Some references share the same GC position, so local object locking, such as btree-node write locks, is still required.
- GC progress is read under `c->gc.pos_lock` seqcount; writers can move the position while readers retry.

Dependencies:
- Includes btree key, GC type, and btree type declarations.
- Uses `struct bch_fs`, `struct printbuf`, `enum btree_id`, `struct bpos`, and `cmp_int()`/`bpos_cmp()` helpers from the wider bcachefs codebase.

Risk points:
- Correctness depends on every updater using the same GC position ordering as GC itself.
- If a pointer-marking path omits the relevant lock, GC can pass an update window and double-count or miss references.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/btree/check.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/btree/check_types.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/btree/check_types.h

This header defines the lightweight state types used by btree GC/checking code.

Core responsibilities:
- Defines `GC_PHASES()` and `enum gc_phase` with `not_running`, `start`, `sb`, and `btree`.
- Defines `struct gc_pos`, the ordered GC cursor: phase, btree ID, btree level, and btree position.
- Defines `struct reflink_gc` and `reflink_gc_table` for reflink reference tracking in a generic radix tree.
- Defines `struct bch_fs_gc`, which stores current GC position plus a read/write semaphore guarding periods where bucket `gc_mark` state is not globally reliable.
- Defines `struct bch_fs_gc_gens`, the async generation-GC cursor/work item state.

Important invariants:
- `gc_pos.phase` is the coarse phase ordering; btree, level, and `bpos` refine ordering only for btree scanning.
- `bch_fs_gc.lock` protects allocation code from trusting bucket GC marks while GC is in progress.
- `bch_fs_gc_gens` serializes async generation work with a mutex and work item.

Dependencies:
- Includes `btree/bbpos_types.h` for btree/bpos cursor typing.
- Uses Linux generic radix tree support for reflink GC tables.
- Assumes bcachefs core types such as `enum btree_id`, `struct bpos`, `seqcount_t`, `rw_semaphore`, `work_struct`, and `mutex`.

Risk points:
- The bitfield sizing in `gc_pos` is compact and tied to enum ranges.
- GC state is shared between online update paths and background checking, so lock discipline is part of the data model.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/btree/check_types.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/btree/commit.c -->
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
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/btree/commit.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/btree/init.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/btree/init.c

This file documents the bcachefs btree architecture and initializes/tears down the btree subsystem workqueues, pools, caches, iterators, key cache, write buffer, and interior-update support.

Core responsibilities:
- Contains a long `DOC_LATEX(btrees)` design document explaining bcachefs as a transactional key-value store over many btrees.
- Documents functional btree groups: core filesystem data, allocation/space management, snapshots/subvolumes, reconcile work, quotas/stripes/LRU/logged ops/accounting.
- Documents key invariants: no duplicate keys, deletion via whiteouts, preserved update ordering, log-structured node bsets, packed keys, and interior pointer semantics.
- Implements `bch2_fs_btree_exit()` to tear down node scan, write buffer, key cache, iterators, interior updates, evicted-size table, node cache, workqueues, mempools, and biosets.
- Implements `bch2_fs_btree_init_early()` for preallocation-free list/work structure initialization.
- Implements `bch2_fs_btree_init()` for read-side and common btree resources: read-complete workqueue, fill-iterator mempool, btree bio set, bounce buffer pool, cache, iterators, key cache, and read-error ratelimits.
- Implements `bch2_fs_btree_init_rw()` for write-side resources: write submit/complete workqueues, interior update machinery, write buffer, and evicted-size tracking.

Important invariants:
- Common btree initialization is split from read-write initialization; write-side workqueues and update machinery are only created when entering RW mode.
- Exit ordering unwinds higher-level services before destroying workqueues/pools they may use.
- The fill iterator size is derived from configured btree node blocks and sort iterator set counts.
- Btree node size drives bounce-pool allocation.

Dependencies:
- Uses btree cache, iterator, interior update, key cache, node scan, read/sort/write/write-buffer subsystems.
- Uses Linux workqueues, mempools, biosets, and ratelimit helpers.

Risk points:
- `bch2_fs_btree_init()` chains several allocations in one condition; partial initialization relies on the broader filesystem init error path calling exit cleanup.
- Workqueue names and flags are part of operational behavior; btree read completion is high priority/freezable/mem-reclaim, and write queues are single-threaded.
- The documented btree invariants are relied on by `commit.c` and `interior.c` rather than enforced locally.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/btree/init.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/btree/init.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/btree/init.h

This header declares the btree subsystem lifecycle API.

Core responsibilities:
- Declares `bch2_fs_btree_exit()` for teardown.
- Declares `bch2_fs_btree_init_early()` for early field/list/cache initialization.
- Declares `bch2_fs_btree_init()` for common btree resource allocation.
- Declares `bch2_fs_btree_init_rw()` for read-write btree resources.

Dependencies:
- Assumes `struct bch_fs` is declared by the including context.
- Implemented by `init.c` and called by broader filesystem initialization/shutdown code.

Risk points:
- The API split matters: callers must run early init before common init, and RW init only when writes are permitted.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/btree/init.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/btree/interior.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/btree/interior.c

This file implements bcachefs interior btree node maintenance: topology checking, node allocation/replacement, root changes, splits, compactions, foreground merges, async rewrites, parent-key updates, reserve caches, and completion of multi-node interior updates.

Core responsibilities:
- Validates interior topology with `bch2_btree_node_check_topology_msg()`: root bounds, child min-key continuity, non-empty interior nodes, and final child max-key coverage.
- Calculates ideal packed-key formats for rewritten nodes and checks whether repacking fits.
- Allocates and frees in-memory btree nodes, including replacement nodes with incremented sequence numbers and recalculated formats.
- Maintains a btree-node reserve cache of allocated open buckets to avoid allocator livelock during multi-level splits.
- Starts `struct btree_update` operations with disk reservations, allocator requests, GC read locking, preallocated replacement nodes, and update range metadata.
- Completes interior updates asynchronously after new nodes are written, marking superblock btree bitmaps, journaling old/new node visibility, updating allocation triggers, unblocking parent writes, flushing writes, and releasing open buckets.
- Transfers journal pins from old nodes being replaced to the enclosing update so old on-disk locations are not freed before replacement nodes become persistent and reachable.
- Updates roots in memory and records root updates for journal persistence.
- Inserts child pointer keys into interior nodes, validates inserted keys, and checks topology after insertion.
- Splits or compacts full nodes via `btree_split()`, including recursive parent insertion and root growth.
- Increases depth explicitly with `bch2_btree_increase_depth()`.
- Attempts foreground sibling merges with `__bch2_foreground_maybe_merge()`, including deferred sibling reads using evicted-size estimates.
- Computes balanced split/merge layouts, predicts packed sizes/formats, and packs source keys into one or two destination nodes.
- Rewrites individual nodes by key or position and schedules async rewrite/merge work.
- Updates a btree node's key in its parent or root journal entry, with special handling for nodes that are not yet reachable.
- Creates fake roots for bringup/new-filesystem initialization.
- Exposes diagnostics for active interior updates and reserve-cache contents.
- Initializes and tears down interior update and async node rewrite workers/mempools.

Interior update model:
- Foreground split/merge/rewrite allocates replacement nodes and mutates in-memory topology under btree locks.
- New nodes are written before the parent/root update is allowed to become durable.
- Parent nodes that reference not-yet-written children are marked write-blocked and linked to the `btree_update`.
- Once child writes complete, worker-side transaction code journals old-node overwrites, new-node keys or roots, and allocation trigger effects.
- Only after new nodes are persistent and reachable are old node pins dropped and open buckets released.

Split/merge behavior:
- `btree_split()` may either compact a node into one replacement or split into two replacements, depending on live key count and whether the failed key would fit after compaction.
- Interior inserts are applied before splitting because child pointer updates must remain atomic and pivots must not bisect coalesced child ranges.
- Root splits allocate a new root and insert child pointers into it.
- Foreground merge considers previous/current/next siblings, first using cached `sib_u64s` or evicted-size estimates, then revalidating parent identity after locks are upgraded.
- Merges can produce one destination node or, for larger three-source merges, two balanced destination nodes.

Important invariants:
- Root nodes are protected from reclaim by the permanent flag while still participating in cache lists.
- Replacement nodes keep owned intent/write refs while reserved; consumed and unused reserves are cleaned through shared rollback/release paths.
- `will_make_reachable` gates writes and key updates for nodes that exist in memory but are not yet durable/reachable from an on-disk parent.
- Topology continuity is expressed by child `min_key` and parent key position as child `max_key`.
- Btree pointer keys must have `sectors_written` stamped before being consumed into parent updates or root records.
- Old nodes must be freed in memory before unlocking new nodes, so readers cannot reacquire stale nodes after a replacement becomes visible.
- Interior update completion uses `commit_lock` to synchronize with `bch2_btree_node_update_key()`.

Dependencies:
- Uses allocation/open-bucket/disk-reservation code, btree cache/locking/iter/read/sort/write helpers, journal pins/reclaim, superblock btree bitmaps, reconcile metadata, data write flags, keylists, and filesystem error handling.
- Interacts directly with `commit.c` through transaction commits and with `interior.h` inline capacity/whiteout helpers.

Risk points:
- Error cleanup is complex because preallocated nodes may be unused, consumed but uncommitted, or already handed to paths.
- Deferred sibling merge estimates must be revalidated after real traversal and parent locking.
- Journal error/read-only transitions are explicitly guarded because interior updates can otherwise run allocation triggers without a durable journal half.
- Parent/root updates involving not-yet-written nodes rely on write blocking and journal pins for crash consistency.
- Root updates, fake roots, and pending rewrites have separate lifecycle paths that must converge before shutdown.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/btree/interior.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/btree/interior.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/btree/interior.h

This header defines the public interface and key inline helpers for bcachefs interior btree updates, node split/merge/rewrite operations, btree root handling, and btree-node capacity accounting.

Core responsibilities:
- Defines `BTREE_UPDATE_NODES_MAX`, update modes, `struct btree_update_node`, and the central `struct btree_update`.
- Describes the crash-consistency model for split/rewrite operations: new child nodes are written, then parent/root updates make them visible, then old nodes can be freed.
- Declares topology checking, split, merge, depth increase, node rewrite, async operation, node-key update, root setup, journal root serialization, flush, diagnostics, and lifecycle functions.
- Defines `btree_update_set_watermark_hipri()` to raise write watermarks for btree metadata paths.
- Defines `btree_update_reserve_required()` for worst-case split allocation requirements.
- Defines helpers for sibling-size reset, btree data bounds, unwritten whiteouts, write-block boundaries, written-address tests, and remaining key capacity.
- Defines `want_new_bset()` to decide when an append should start a new bset.
- Defines `push_whiteout()` to preserve deletion semantics when overwriting written keys.
- Defines `bch2_btree_node_insert_fits()` and `bch2_btree_node_compact_fits()` for insert/split decisions.
- Defines `btree_bkey_and_val_eq()`, intentionally ignoring the mutable `mem_ptr` field in `btree_ptr_v2` values.

Important invariants:
- `struct btree_update` owns replacement-node reserves, old/new node lists, journal pin state, disk reservation, write-blocked parent linkage, and inline parent key storage.
- `BTREE_RESERVE_MAX` and `BTREE_UPDATE_NODES_MAX` bound how many nodes a worst-case split/merge can allocate atomically.
- `bch2_btree_keys_u64s_remaining()` leaves one extra u64 for varint decode slack.
- `bch2_btree_node_insert_fits()` refuses inserts into nodes marked need-rewrite.
- `bch2_btree_node_compact_fits()` models write-path block rounding, preventing compact/retry loops where the follow-on key would still not fit.
- Whiteouts are stored at the end of node data and counted against remaining capacity.

Dependencies:
- Includes btree cache, locking, update declarations, and data write types.
- Uses btree node structures, bpos, key formats, journal pins, disk reservations, open buckets, closures, workqueues, and bcachefs transaction flags.

Risk points:
- The `struct btree_update` lifecycle is shared between foreground mutation and async completion; fields like `mode`, `nodes_written`, `b`, and `will_make_reachable` have synchronization requirements.
- Capacity helpers must stay aligned with the write path's exact rounding/slack behavior.
- `btree_bkey_and_val_eq()` deliberately skips `mem_ptr`; using a raw value comparison elsewhere would create false inequality for btree pointers.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/btree/interior.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/btree/interior_types.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/btree/interior_types.h

This header defines persistent filesystem-level state containers for btree interior node allocation reserves, in-flight interior updates, and async node rewrites.

Core responsibilities:
- Defines `struct btree_alloc`, pairing open buckets with a padded btree pointer key.
- Defines reserve sizing constants `BTREE_RESERVE_MAX` and `BTREE_NODE_RESERVE`.
- Defines `struct bch_fs_btree_reserve_cache`, a mutex-protected cache of allocated but unused btree nodes/open buckets.
- Defines `struct bch_fs_btree_interior_updates`, which owns the interior update mempool, active/unwritten lists, synchronization locks, waitlist, worker workqueue, and work item.
- Defines `struct bch_fs_btree_node_rewrites`, which tracks active and pending async rewrites/merges with a spinlock, waitlist, and worker.

Important invariants:
- The reserve cache exists to avoid livelock when btree reserve allocation fails after partially allocating nodes.
- Interior update list membership acts as a filesystem reference during async completion and shutdown synchronization.
- `commit_lock` serializes the transaction part of interior update completion with node-key updates.
- Pending node rewrites are held separately until journal replay/read-write state allows them to run.

Dependencies:
- Relies on `struct open_buckets`, padded bkey storage macros, mempools, lists, mutexes, spinlocks, closures, and workqueues defined elsewhere in bcachefs/Linux.

Risk points:
- Reserve-cache entries pin open buckets; shutdown and error paths must drain or release them.
- Active and unwritten lists must be updated under the correct mutex or flush/wait logic can miss work.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/btree/interior_types.h -->