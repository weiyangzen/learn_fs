# Group Research: group_223_bcachefs_tools_sources_cow_pools_bcachefs_tools_fs_btree_iter_c_sour_cff3bd9856c8

Scope checked against `Docs/research_subset_a.md`; all requested files are under `sources/cow-pools/bcachefs-tools`, which is included in subset A. Each listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/btree/iter.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/btree/iter.c

## Purpose
`iter.c` is the core bcachefs btree transaction and iterator implementation. It owns path allocation, path traversal from root to leaf, iterator peek/next/prev/slot semantics, transaction restart handling, transaction-local allocation, diagnostics, and filesystem-level transaction iterator initialization/teardown. The opening documentation frames the API around transaction-scoped btree iterators rather than one-off lookups.

## Main Responsibilities
- Maintains `struct btree_path` invariants: sorted transaction path list, reference and intent reference counts, preserved paths, lock state, cached vs real btree paths, and path position consistency with per-node iterators.
- Traverses paths down the btree with `bch2_btree_path_traverse_one()`, using root locking, child pointer lookup, topology checks, optional prefetch, journal overlay during replay, and recovery from stale or invalid cached levels.
- Exposes iterator operations: `bch2_btree_iter_peek_max()`, `bch2_btree_iter_next()`, `bch2_btree_iter_peek_prev_min()`, `bch2_btree_iter_prev()`, `bch2_btree_iter_peek_slot()`, slot next/prev, node iteration, and root-key peeking.
- Merges visible candidates from the on-disk btree, the journal overlay, transaction-local staged updates, and the btree key cache.
- Handles snapshot-aware filtering. Forward scans use `btree_iter_filter_snapshots()` to skip unrelated snapshot branches and whiteouts while maintaining monotonic progress; reverse scans keep a saved candidate path while searching for same-position overwrites.
- Provides path repair after btree mutation: `bch2_btree_path_fix_key_modified()`, `bch2_btree_node_iter_fix()`, `bch2_trans_node_add()`, `bch2_trans_node_reinit_iter()`, and update revalidation in modified nodes.
- Owns transaction lifecycle: `bch2_trans_begin()`, `__bch2_trans_get()`, `bch2_trans_put()`, transaction path cleanup, SRCU handling, mempool/per-CPU transaction reuse, and transaction stats.

## Important Behaviors
- Extent iterators are special: search keys use the successor of `iter->pos`, returned extents may straddle `iter->pos`, and `peek_slot()` synthesizes hole keys so slot iteration covers keyspace.
- `BTREE_ITER_all_snapshots`, `BTREE_ITER_filter_snapshots`, `BTREE_ITER_snapshot_field`, and `BTREE_ITER_is_extents` materially change ordering and position semantics.
- `bch2_path_get()` reuses compatible existing paths when possible, otherwise allocates and inserts a new sorted path. Path sorting uses a cocktail-shaker pass because paths are usually nearly sorted.
- Transaction restarts are represented by `trans->restarted`; callers use `bch2_trans_begin()`/`lockrestart_do()` patterns to reset transient state and retry.
- `__bch2_trans_kmalloc()` is a per-transaction bump allocator. Growth after an allocation exists triggers a transaction restart so callers retry with a larger buffer.
- During journal replay, long-lived transactions hold a journal-key reference and automatically drop it after replay completes on a later `bch2_trans_begin()`.

## Dependencies and Coupling
- Heavily coupled to `btree/locking.h` and `locking.c` for relock, upgrade, unlock, and deadlock-restart behavior.
- Calls into `journal_overlay.c` for replay-time journal-key peeking and btree-plus-journal child lookup.
- Integrates with `key_cache.c` for cached single-key paths and cached key lookups.
- Depends on btree node iterator primitives from `btree/bset.h`/cache/interior code, bkey packing/unpacking helpers, snapshot ancestry checks, journal validation/text helpers, and transaction commit/update paths.

## Research Notes
- This file is a central correctness choke point: path position, iterator cursor, lock state, journal overlay state, and transaction-local updates must stay mutually consistent.
- There is an explicit TODO/comment around reverse iteration: `peek_prev` may leave `path->pos` inconsistent with ancestor levels because it does not normalize with a trailing `set_pos()` like forward peeking. That is likely relevant for restart/fault-injection or node-split investigations.
- Debug-only verification is extensive but often static-branch gated; release behavior relies on the same invariants without continuous checking.

<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/btree/iter.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/btree/iter.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/btree/iter.h

## Purpose
`iter.h` is the public/internal interface for bcachefs btree transactions, iterators, path helpers, restart loops, transaction-local allocation, and iterator convenience macros.

## Main Responsibilities
- Declares path and transaction diagnostic helpers such as `bch2_trans_paths_to_text()`, `bch2_dump_trans_paths_updates()`, and `bch2_btree_trans_to_text()`.
- Provides inline path reference management (`__btree_path_get()`, `__btree_path_put()`), sorted path iteration macros, and helpers for walking paths with a specific btree node.
- Declares path operations: make mutable, set position, traverse one path, get/release paths, peek exact slots, relock/upgrade/downgrade, node fixups, and transaction node update hooks.
- Declares iterator operations and implements small inline wrappers for `peek`, `peek_prev`, position setting, snapshot setting, common initialization, and RAII-style `CLASS()` wrappers.
- Defines `bch2_btree_iter_flags()`, which normalizes caller flags based on btree type, level, snapshot support, cache eligibility, extent semantics, and journal replay state.
- Provides restart and loop macros: `lockrestart_do()`, `nested_lockrestart_do()`, `for_each_btree_key*`, reverse iteration variants, commit variants, and no-restart variants.
- Provides transaction wait/allocation wrappers that know how to drop SRCU before long waits and how to drop/relock btree locks around blocking allocation.

## Important Behaviors
- Cached btree IDs are restricted to alloc, inodes, logged ops, and subvolumes. Leaf iterators over these can automatically use the key cache unless explicitly cached already.
- `bch2_trans_iter_init()` exits any existing iterator before initializing it; uninitialized/copy/node iterator classes wrap common cleanup.
- `bch2_btree_iter_set_pos()` also drops any `update_path`, because a saved update path is only valid for the previous iterator position.
- `lockrestart_do()` is a loop-form macro so cleanup attributes inside the body run on each retry.
- `drop_locks_do()` and allocation helpers are intentionally warned as not fast-path friendly unless a nonblocking attempt has already failed.

## Dependencies and Coupling
- Includes btree node/cache types, closure APIs, and counters.
- References functions implemented across `iter.c`, `locking.c`, `key_cache.c`, and update/commit code.
- Macro users throughout bcachefs depend on these exact restart semantics and cleanup behavior.

## Research Notes
- This header encodes much of the btree API contract. Research into call sites should treat iterator flags as part of behavior, not as minor options.
- The wait helpers are notable for SRCU memory-reclaim safety: code with a `btree_trans` in scope should use these wrappers instead of raw closure waits or bit waits when waits may be long.

<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/btree/iter.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/btree/journal_overlay.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/btree/journal_overlay.c

## Purpose
`journal_overlay.c` manages keys read from the journal before replay has completed. It lets normal btree traversal see journal keys as if they overlay the btree, supports insertion/deletion of replay keys, tracks overwritten journal keys, sorts/deduplicates replay entries, and frees replay data.

## Main Responsibilities
- Stores journal keys in a sorted gap buffer (`struct journal_keys`) for efficient sequential insertions during recovery.
- Provides binary search and peeking helpers: `bch2_journal_keys_peek_max()`, `bch2_journal_keys_peek_prev_min()`, and `bch2_journal_keys_peek_slot()`.
- Implements `bch2_journal_key_insert_take()`, `bch2_journal_key_insert()`, and `bch2_journal_key_delete()` for recovery-time mutation of the overlay.
- Tracks journal keys overwritten by replay using `overwritten` bits plus ranges in `journal_key_range_overwritten`, allowing peeking iterators to skip runs efficiently.
- Implements `struct btree_and_journal_iter`, which merges a btree node iterator with journal keys at the same btree ID/level.
- Sorts raw journal replay entries with `bch2_journal_keys_sort()`, including rewind support and compaction/deduplication of equal keys.
- Cleans up with `bch2_journal_keys_put()`, reset helpers, shoot-down by btree/range, dumping, and filesystem initialization.

## Important Behaviors
- The main key array is a gap buffer: logical indexes are translated by `idx_to_pos()` and `pos_to_idx()` so insertions near the gap are cheap.
- Before `journal_keys_sort()` and before the btree is running, inserted keys go to `pre_sort` so they survive reset and later merge into the sorted array.
- Accounting keys are intentionally not accumulated during journal sort because replay must compare each individual accounting update against the btree version.
- `btree_and_journal_iter_peek()` returns the earlier of btree and journal keys at the current position, skips deleted keys, and can fail early when too many whiteouts are encountered during prefetch.
- Rewind ranges require overwrite entries; if rewind is requested but overwrite metadata is unavailable, sorting returns a journal rewind error.

## Dependencies and Coupling
- Uses journal replay structures from `journal/read.h`, bkey/bset helpers, allocation accounting accumulation, genradix journal entry storage, RCU-protected overwrite range access, and the btree node prefetch path.
- Called by `iter.c` during traversal when `trans->journal_replay_not_finished` or `BTREE_ITER_with_journal` is set.

## Research Notes
- This file is recovery-path critical. Normal multithreaded RW use is avoided until recovery has finished; comments explicitly restrict some operations to the recovery thread while still read-only.
- Correctness depends on comparisons by level, btree ID, and bpos matching the btree iterator ordering.

<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/btree/journal_overlay.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/btree/journal_overlay.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/btree/journal_overlay.h

## Purpose
`journal_overlay.h` declares the journal overlay iterator interface and inline comparison/access helpers used by btree iterators during journal replay.

## Main Responsibilities
- Defines `struct journal_iter` and `struct btree_and_journal_iter`.
- Provides `journal_entry_radix_idx()` and `journal_key_k()` to locate replay keys, whether they are separately allocated or embedded in a replayed journal entry.
- Defines journal-key ordering helpers: `__journal_key_btree_cmp()`, `__journal_key_cmp()`, and `journal_key_cmp()`.
- Declares peek, insert, delete, overwrite-check, overlay iteration, sort, shoot-down, dump, init, and put functions.
- Provides `bch2_journal_keys_put_initial()` to release the initial journal key reference once appropriate.

## Important Behaviors
- Ordering compares level in reverse priority before btree ID, then bpos. This must stay aligned with the overlay search/merge logic.
- `btree_and_journal_iter` carries both a btree node iterator and a journal iterator plus merge state (`pos`, `at_end`, prefetch flags).

## Dependencies and Coupling
- Includes btree key definitions and references `struct journal_keys`, `journal_replay`, btree node iterator state, btree transactions, and filesystem journal replay storage.
- Implemented by `journal_overlay.c` and consumed by `iter.c`, `key_cache.c`, and recovery code.

## Research Notes
- This header is small but defines the comparison contract that makes journal overlay binary search and btree merge iteration valid.

<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/btree/journal_overlay.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/btree/journal_overlay_types.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/btree/journal_overlay_types.h

## Purpose
`journal_overlay_types.h` contains the data structures backing journal replay entries and the journal-key overlay index.

## Main Types
- `struct journal_ptr`: records where a journal entry was found, including checksum status, device, bucket/offset, and sector.
- `struct journal_replay`: stores one replayed journal set plus its source pointers and flags for checksum/blacklist/dirty handling.
- `struct journal_key_range_overwritten`: represents a contiguous logical range of overwritten journal keys.
- `struct journal_key`: identifies one replay key by btree ID, level, location in `journal_replay`, optional allocated key pointer, overwrite state, and rewind state.
- `struct journal_keys`: sorted gap-buffer container for journal keys, including refcount, initial-ref flag, pre-sort staging array, overwrite lock, and RCU-visible overwrite ranges.

## Important Behaviors
- `journal_replay` keeps `struct jset j` last because it is variable sized.
- `journal_keys` intentionally mirrors darray layout at the front (`nr`, `size`, `data`, `preallocated`) while adding gap-buffer and replay-specific fields.
- `journal_key` can either point into stored journal replay data via sequence/offset or own an allocated `struct bkey_i`.

## Dependencies and Coupling
- Used by `journal_overlay.h/.c` and journal reading code. It depends on bcachefs bkey, checksum, darray, mutex, and atomic conventions.

## Research Notes
- The gap-buffer and overwrite-range fields explain much of the complexity in `journal_overlay.c`: logical ordering and physical storage position are deliberately separate.

<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/btree/journal_overlay_types.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/btree/key_cache.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/btree/key_cache.c

## Purpose
`key_cache.c` implements the btree key cache: a hash-table-backed cache for frequently accessed single keys, especially alloc-btree keys touched by extent updates. It supports cached path traversal, fill/reuse/eviction, dirty-key flushing through journal reclaim, read-only transition flushing, and shrinker integration.

## Main Responsibilities
- Allocates, initializes, reuses, and frees `struct bkey_cached` objects, including separate pending queues for normal and per-CPU-reader SIX locks.
- Implements cached traversal with `bch2_btree_path_traverse_cached()`: find a cached key, lock it as a cached btree path, or fill from the underlying btree/journal.
- Creates cache entries with `btree_key_cache_create()`, sizing the key buffer with extra room to avoid commit-time realloc restarts.
- Flushes dirty cached entries back to the real btree with `btree_key_cache_flush_pos()` and journal pin callback `bch2_btree_key_cache_journal_flush()`.
- Provides `bch2_btree_key_cache_flush_going_ro()` to force dirty cache entries out during read-only transition without creating new journal pins.
- Applies cached updates in `bch2_btree_insert_key_cached()` and drops stale cache entries in `bch2_btree_key_cache_drop()` when the underlying btree is updated directly.
- Registers a memory shrinker that evicts clean, unaccessed, lockable cache entries and records shrinker statistics.
- Initializes and tears down global and per-filesystem key-cache state.

## Important Behaviors
- Dirty cached keys are journal-pinned. The flush path may re-journal in normal reclaim but the going-read-only path forces `no_journal_res` so cleanup converges.
- Cache fill uses a normal iterator with key-cache fill flags and disables journal overlay after it has explicitly checked replay keys.
- Eviction only takes clean entries. Dirty entries must be flushed first and have their journal pins dropped.
- Cached btree paths use the same lock/path infrastructure as btree nodes, with the cached object stored in `path->l[0].b` and marked cached.
- Pending freed entries are RCU/SRCU delayed; reuse tries to claim intent+write locks without blocking so entries are not reused while readers may still observe them.

## Dependencies and Coupling
- Depends on `iter.c` path management, `locking.c` SIX lock helpers, journal reclaim/pin APIs, rhashtable, shrinker APIs, and update/commit paths.
- `iter.c` consults this file through `bch2_btree_path_traverse_cached()`, `bch2_btree_key_cache_find()`, and cached path semantics.

## Research Notes
- This is a high-performance coherency layer. Bugs are likely to involve stale cache entries, journal pin sequencing, dirty count accounting, direct btree updates bypassing cache, or lock/SRCU lifetime interactions.

<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/btree/key_cache.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/btree/key_cache.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/btree/key_cache.h

## Purpose
`key_cache.h` declares the btree key-cache API and inline policy helpers for dirty-cache pressure.

## Main Responsibilities
- Defines thresholds for when dirty cached keys should trigger flush pressure (`bch2_nr_btree_keys_need_flush()`), when callers must wait, and when wait is complete.
- Defines rhashtable comparison parameters for cache lookup keyed by btree ID and bpos.
- Provides inline `bch2_btree_key_cache_find()`.
- Declares cached traversal, cached insert/drop, journal flush, read-only flush, filesystem init/exit, text reporting, and global slab init/exit functions.

## Important Behaviors
- Dirty limits scale with total cache size and have hysteresis: kick threshold, must-wait threshold, and wait-done threshold differ.
- The rhashtable key is `struct bkey_cached_key`, and matching requires both identical btree ID and exact bpos equality.

## Dependencies and Coupling
- Includes btree key definitions and references journal, transaction, path, insert-entry, and filesystem key-cache structures.
- Implemented by `key_cache.c`; called by iterator and update/commit paths.

## Research Notes
- The threshold helpers are part of writeback/reclaim behavior, not just telemetry; changes can affect journal pressure and transaction latency.

<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/btree/key_cache.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/btree/key_cache_types.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/btree/key_cache_types.h

## Purpose
`key_cache_types.h` defines the persistent per-filesystem key-cache container and its hash key type.

## Main Types
- `struct bch_fs_btree_key_cache`: owns the rhashtable, shrinker, shrink iterator, two RCU pending queues, per-CPU pending counters, atomic key/dirty counts, and shrinker statistics.
- `struct bkey_cached_key`: packed/aligned hash key consisting of btree ID and bpos.

## Important Behaviors
- Pending queues are split by whether cached locks use per-CPU readers.
- `nr_keys` and `nr_dirty` are atomics used for cache pressure decisions and shutdown validation.
- Shrinker stats distinguish freed entries from dirty, recently accessed, and lock-failed skips.

## Dependencies and Coupling
- Includes `util/rcu_pending.h` and is consumed by `key_cache.h/.c` and broader filesystem btree state.

## Research Notes
- The type file makes clear that key-cache lifecycle is both hash-table based and RCU-delayed; readers of `key_cache.c` should track both dimensions.

<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/btree/key_cache_types.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/btree/locking.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/btree/locking.c

## Purpose
`locking.c` implements bcachefs btree node/key-cache locking on top of SIX locks, transaction deadlock detection, path relock/upgrade/downgrade, transaction unlock/relock, and lock-state debug verification.

## Main Responsibilities
- Initializes btree node locks and a per-CPU lock graph used by the deadlock detector.
- Counts locks held by the current transaction on a btree node/common cached object.
- Implements cycle detection with `bch2_check_for_deadlock()`: walks transactions waiting on locks, snapshots conflicting waiters, detects cycles, chooses an abort victim, and restarts transactions to break cycles.
- Provides SIX-lock deadlock callback `bch2_six_check_for_deadlock()`, including memory-ordering barriers and stale-node reuse detection.
- Implements node lock slow paths, write-lock contention handling, and off-path locking via `bch2_btree_node_lock_with_path()`.
- Implements relock and upgrade paths: `__bch2_btree_node_relock()`, `bch2_btree_node_upgrade()`, `bch2_btree_path_relock_norestart()`, `__bch2_btree_path_relock()`, `__bch2_btree_path_upgrade_norestart()`, and `__bch2_btree_path_upgrade()`.
- Implements downgrading/unlocking: `__bch2_btree_path_downgrade()`, `bch2_trans_downgrade()`, `bch2_trans_unlock()`, `bch2_trans_unlock_long()`, and write-lock-only unlock.
- Provides lock-aware mutex acquisition (`__bch2_trans_mutex_lock()`) and debug verification for path/transaction locks.

## Important Behaviors
- SIX locks have shared, intent, and write states. Intent locks prevent upgrade deadlocks by allowing readers while serializing would-be writers.
- Deadlock detection is database-style: when a transaction would block, it follows wait edges through locks held by other transactions. On a cycle, one transaction is restarted instead of waiting indefinitely.
- Cycle detection tolerates races by revalidating frames before acting and by RCU-protecting transaction/path memory while walking wait lists.
- `bch2_six_check_for_deadlock()` checks for node reuse races before sleeping on a btree node lock; if a node identity changed, it returns a restart so traversal can be redone.
- Upgrades may update linked paths in the same transaction so restart traversal can reacquire the needed ancestor locks.
- `bch2_trans_unlock()` also releases the btree cache cannibalize lock to avoid resource deadlocks across sleeps.
- `bch2_trans_unlock_long()` drops SRCU and resets unlocked cached paths that cannot safely retain cached object pointers across SRCU release.

## Dependencies and Coupling
- Depends on `btree/locking.h` inline helpers, btree cache/node structures, SIX lock internals, wait FIFO state, transaction/path arrays from `iter.c`, btree write submission, counters, and trace events.
- Called from iterator traversal, key-cache flush/reclaim, btree update/split code, transaction wait/allocation wrappers, and debugfs-style diagnostics.

## Research Notes
- This file is the core concurrency layer for btree operations. Any investigation into transaction restarts, lock contention, unexplained latency, or path invalidation should include this file with `iter.c`.
- Memory ordering in the deadlock detector is intentional: the explicit `smp_mb()` pairs with wait-list publishing to avoid missing cycles after all participants are parked.

<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/btree/locking.c -->