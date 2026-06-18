# Group Research: group_206_bcachefs_sources_cow_pools_bcachefs_fs_bcachefs_btree_iter_c_sources_b86a3ff674ee

Scope: `Docs/research_subset_a.md` only. Files read completely: `sources/cow-pools/bcachefs/fs/bcachefs/btree/iter.c`, `iter.h`, `journal_overlay.c`, `journal_overlay.h`, `journal_overlay_types.h`, `key_cache.c`, `key_cache.h`, `key_cache_types.h`, and `locking.c`.

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/btree/iter.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/btree/iter.c

## Role

This file implements the core bcachefs btree transaction and iterator machinery. It is the main state machine for positioning btree paths, traversing from roots to nodes, peeking forward/backward/slot keys, composing staged transaction updates with on-disk btree keys, and managing `struct btree_trans` lifetime.

It sits at the center of the btree subsystem and depends on adjacent cache, locking, journal overlay, key cache, update, snapshot, and extent helpers.

## Major Responsibilities

- Maintain `struct btree_path` objects inside a transaction, including sorted ordering, refcounts, preservation, copy-on-write cloning, and lock expectations.
- Traverse btree paths root-to-leaf with restartable locking and topology checks.
- Keep node iterators valid after in-place btree node updates, key modifications, node replacement, or node drops.
- Implement public iterator operations: node iteration, forward key iteration, reverse key iteration, exact-slot lookup, root lookup, advance, rewind, and “peek and restart” wrappers.
- Merge possible key sources into iterator results: live btree nodes, current transaction updates, replay journal overlay keys, and cached keys.
- Handle snapshot filtering for btrees with snapshot fields, including whiteout behavior and saved reverse-iteration candidates.
- Allocate, initialize, recycle, and destroy btree transactions.
- Provide transaction-local bump allocation with restart-on-growth behavior.
- Emit diagnostic text for transactions, paths, updates, lock state, and leaks.

## Traversal Model

`bch2_btree_path_traverse_one()` is the main traversal engine. It ensures the transaction holds SRCU, reuses already-valid path nodes when sequence numbers still match, climbs until it finds a good ancestor, then walks down through child pointers until the requested depth is reached.

Key traversal helpers include:

- `btree_path_lock_root()` locks and validates the current btree root.
- `btree_path_down()` reads the child pointer at the current level, optionally through the journal overlay during replay, fetches the child node, updates mem-pointers, drops parent read locks when required, and initializes the next lower level.
- `btree_path_up_until_good_node()` climbs when a cached path is stale or no longer covers the requested position.
- `btree_path_prefetch()` and `btree_path_prefetch_j()` prefetch likely child nodes from ordinary btree contents or journal-overlaid contents.

Topology errors are reported by `btree_node_root_err()`, `btree_node_missing_err()`, and `btree_node_gap_err()`. These build detailed messages about broken root coverage, missing child pointers, or nodes that do not cover the expected range.

## Path Management

`bch2_path_get()` finds or creates a path for a btree ID, position, depth, lock target, and iterator flags. It reuses nearby compatible paths when possible, upgrades locks if needed, and otherwise allocates a new path slot through `btree_path_alloc()`.

Paths are sorted by btree ID, cached/non-cached state, position, and descending level. `__bch2_btree_trans_sort_paths()` uses cocktail shaker sort because paths are usually nearly sorted after small iterator moves.

Paths can be made mutable through `__bch2_btree_path_make_mut()`, which clones shared or preserved paths. Position changes go through `__bch2_btree_path_set_pos()`, which updates the path position, reuses node iterators for short forward moves, reinitializes for rewinds or large skips, and marks paths dirty when retraversal is needed.

`bch2_path_put()` releases refs, preserves duplicate paths when useful, transfers `should_be_locked` and preservation state to equivalent paths, and frees paths only when no longer required.

## Iterator Fixups

The file contains substantial logic to keep active iterators coherent while btree nodes mutate:

- `bch2_btree_path_fix_key_modified()` fixes iterators after a key’s deletedness changes.
- `bch2_btree_node_iter_fix()` adjusts node iterators after insertion/removal/replacement inside a bset and rewinds cross-bset iterator state when necessary.
- `bch2_trans_node_add()` repoints paths to a newly installed node and transfers locks.
- `bch2_trans_node_drop()` invalidates paths pointing at a dropped node.
- `bch2_trans_node_reinit_iter()` reinitializes node iterators after broad node modifications.
- `bch2_trans_revalidate_updates_in_node()` refreshes old values for transaction updates that target a modified node.

This is important because multiple transaction paths may share the same btree node at different levels.

## Forward Iteration

`__bch2_btree_iter_peek()` performs raw forward lookup from a search key. It traverses the path, peeks the current node iterator, optionally overlays key-cache entries, journal keys, and staged transaction updates, skips deleted keys, and advances to the next leaf if needed.

`bch2_btree_iter_peek_max()` wraps that with end-bound checking, snapshot filtering, whiteout filtering, update-path handling for intent iterators, transaction restart injection, and iterator position normalization. Extent iterators treat positions specially because extent keys are indexed by end position and may straddle `iter->pos`.

`bch2_btree_iter_next()` advances then peeks.

## Reverse Iteration

`__bch2_btree_iter_peek_prev()` traverses to a search key, makes the path mutable, peeks or steps backward inside the node iterator, overlays cached/journal/update keys, skips deleted keys, and moves to previous leaf nodes as needed.

`bch2_btree_iter_peek_prev_min()` adds lower-bound checks and snapshot filtering. For extents and snapshot-filtered iterators, it may use `peek_slot()` first because extent start positions are not monotonically ordered until after filtering. It also saves a candidate path when a visible ancestor snapshot key may be overwritten by a nearer snapshot key found later in the reverse scan.

`bch2_btree_iter_prev()` rewinds then peeks.

## Slot Lookup

`bch2_btree_iter_peek_slot()` returns the key at exactly `iter->pos`, synthesizing a deleted key or hole when no exact key exists. For extents and snapshot-filtered iterators, it uses a copied iterator with `BTREE_ITER_nofilter_whiteouts` and may synthesize hole extents spanning from `iter->pos` to the next key start.

`bch2_btree_path_peek_slot()` is the lower-level path form. It handles both ordinary btree leaf paths and cached key paths.

## Transaction Lifetime

`__bch2_trans_get()` allocates or reuses a transaction, attaches it to the filesystem transaction list, initializes path arrays, update arrays, lockdep state, transaction stats, SRCU state, and journal replay references.

`bch2_trans_begin()` resets a transaction for a fresh attempt or retry. It clears staged updates, reclaims unreferenced paths, drops stale replay journal references once replay finishes, handles delayed transaction memory reallocation, accounts lock-hold duration, releases locks/SRCU on long-held transactions, and retraverses paths after restart.

`bch2_trans_put()` requires no pending restart, unlocks the transaction, releases update path refs, checks leaked paths in debug builds, drops replay journal refs, releases RCU-visible transaction state, frees transaction memory, and returns the object to a per-CPU cache or mempool.

## Transaction Memory

`__bch2_trans_kmalloc()` backs transaction-local allocation. It uses an inline bump allocator in `trans->mem`, returns zeroed memory, restarts the transaction if the buffer must grow after allocations have already been made, and falls back to the transaction memory mempool if normal allocation fails.

This restart-on-growth design keeps transaction-local pointers valid within one attempt and avoids silently moving storage under active code.

## Debugging And Diagnostics

The file has extensive debug verification:

- path and node iterator invariants
- snapshot filtering correctness
- path lock coverage
- sorted path ordering
- leaked path refs
- unexpected unlocked or restarted transactions
- transaction path/update textual dumps
- per-transaction max path and max memory stats

Many invariant failures intentionally panic because corrupt iterator state can lead to btree corruption.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/btree/iter.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/btree/iter.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/btree/iter.h

## Role

This header exposes the bcachefs btree transaction and iterator API. It provides inline path reference helpers, traversal wrappers, lock/restart helpers, iterator initialization classes, transaction-local allocation helpers, and high-level iteration macros used throughout the filesystem.

## Major Responsibilities

- Define `bkey_err()` and `bkey_try()` helpers for iterator-returned keys.
- Manage low-level path refs with `__btree_path_get()` and `__btree_path_put()`.
- Provide path dirtying, node access, sorting, and path iteration macros.
- Expose traversal, path acquisition, path mutation, and exact-slot helpers.
- Declare lock/relock/unlock/downgrade interfaces implemented in `locking.c`.
- Define transaction restart helpers and fault-injection hook points.
- Define iterator operations for node, forward, reverse, slot, and root iteration.
- Normalize iterator flags for cached btrees, extent btrees, snapshots, and journal replay.
- Provide RAII-style `CLASS()` constructors/destructors for transactions and iterators.
- Provide restart-aware iteration macros over keys and nodes.
- Provide transaction-local allocation wrappers and lock-dropping allocation helpers.
- Provide SRCU-aware wait wrappers for closures and bit waits.

## Path And Traversal API

The header defines the fast inline wrappers that most callers use:

- `bch2_btree_path_traverse()` verifies the transaction is locked and calls the full traversal path only when the path is stale.
- `bch2_btree_path_set_pos()` avoids full repositioning when the path already has the requested position.
- `bch2_btree_path_make_mut()` clones preserved/shared paths before mutation.
- `bch2_btree_path_peek_slot_exact()` ensures cached-path lookups synthesize an exact-position missing key when the cached entry belongs to another snapshot.

Path iteration macros include unordered path scans, sorted path scans, reverse sorted scans, and “paths with this node” scans.

## Transaction Restart Model

`btree_trans_restart_ip()` records the restart reason and caller IP, and in debug builds captures a backtrace. `bch2_trans_verify_not_restarted()` checks that a retry-sensitive section did not restart unexpectedly.

`lockrestart_do()` is the standard retry loop: it calls `bch2_trans_begin()`, runs the body, verifies no hidden restart on success, and retries while the result is a transaction restart. `nested_lockrestart_do()` is a nested variant that reports `transaction_restart_nested` if the inner operation succeeded only after restarting.

These macros are central to bcachefs’s restartable btree programming model.

## Iterator Initialization

`bch2_btree_iter_flags()` derives actual iterator flags from the requested flags and btree properties:

- key cache is only enabled for cached btree IDs at leaf level
- extent mode is enabled for extent btrees unless explicitly disabled
- all-snapshot iteration is cleared for btrees without snapshot fields
- snapshot filtering is enabled for snapshot-aware btrees unless all snapshots are requested
- journal overlay is enabled while journal replay is not finished

`bch2_trans_iter_init_common()` fills `struct btree_iter` and acquires the underlying path. The header then provides outlined and inline constructors plus RAII classes for ordinary iterators, uninitialized iterators, copied iterators, and node iterators.

## Iteration Macros

The file defines restart-aware loop macros such as:

- `for_each_btree_node()`
- `for_each_btree_key()`
- `for_each_btree_key_max()`
- `for_each_btree_key_reverse()`
- commit variants that call `bch2_trans_commit()`
- no-restart variants for callers that manage restarts externally

These macros preserve the transaction model by beginning transactions, checking restart counters, advancing/rewinding iterators, and retrying on restart errors.

## Transaction Allocation Helpers

`bch2_trans_kmalloc_ip()` and `bch2_trans_kmalloc_nomemzero_ip()` allocate from transaction-local bump storage and call into `__bch2_trans_kmalloc()` when the buffer must grow. The allocation is rounded to 8 bytes, optionally traced, and reset on every `bch2_trans_begin()`.

`allocate_dropping_locks*` helpers first try nonblocking allocation and then drop transaction locks for blocking allocation. Variants either relock automatically, return an error code, or report that locks were dropped.

## Waiting And SRCU

The header contains SRCU-aware wait helpers:

- `bch2_trans_short_wait_budget()`
- `trans_closure_sync_timeout()`
- `trans_closure_sync()`
- `trans_wait_event_timeout()`
- `trans_wait_event()`
- `trans_wait_on_bit_io()`

They prevent long waits while holding the btree transaction SRCU read lock by using short wait budgets and dropping SRCU when needed.

## Public Interfaces

The header declares transaction lifecycle functions (`__bch2_trans_get()`, `bch2_trans_put()`, init/exit), iterator operations, path locking operations, transaction diagnostics, and filesystem-level btree iterator initialization/teardown.

It also provides `bch2_trans_get()` as a function-indexed macro keyed by `__func__`, enabling per-callsite transaction stats.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/btree/iter.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/btree/journal_overlay.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/btree/journal_overlay.c

## Role

This file implements the replay-time journal key overlay. Before journal replay has fully applied keys to btrees, normal btree iterators must see journal keys as if they overwrite btree contents. This module maintains a sorted journal-key array and provides lookup/iteration helpers that merge journal keys with ordinary btree node iterators.

## Major Responsibilities

- Store journal keys in a sorted gap-buffer representation.
- Search journal keys by btree ID, level, and position.
- Peek forward, reverse, or exact journal keys while skipping overwritten entries.
- Insert copied or owned keys during recovery before the filesystem is writable.
- Represent deleted journal keys by inserting whiteouts.
- Track journal keys overwritten during replay/rewind and skip overwritten ranges efficiently.
- Merge btree node iterator keys with journal overlay keys.
- Sort and compact raw journal entries read during recovery.
- Free journal key storage and replay journal entries when no longer needed.
- Remove journal keys covered by “shoot down” ranges.
- Dump journal keys for diagnostics.

## Gap Buffer

`journal_keys` uses `nr`, `size`, `data`, and `gap` so sequential insertions avoid O(n^2) behavior. Helpers translate between logical sorted indices and physical array positions:

- `pos_to_idx()`
- `idx_to_pos()`
- `idx_to_key()`

`bch2_journal_key_insert_take()` moves the gap, grows the array when full, updates active iterators around gap movement, and inserts the new key at the correct sorted position.

## Lookup And Peek

`__bch2_journal_key_search()` binary-searches logical keys by btree ID, level, and position. The sort order compares descending level first, then btree ID, then position.

Forward lookup uses `bch2_journal_keys_peek_max()`. Reverse lookup uses `bch2_journal_keys_peek_prev_min()`. Exact lookup uses `bch2_journal_keys_peek_slot()`.

Both forward and reverse lookup accept a caller-maintained index for efficient repeated iteration, but reset to binary search after too many local adjustments. They skip overwritten keys and can jump across overwritten ranges.

## Insert And Delete

`bch2_journal_key_insert()` copies a key and delegates to `bch2_journal_key_insert_take()`. `bch2_journal_key_delete()` inserts a whiteout key at the requested position.

Before the btree subsystem is running, inserts go to `keys->pre_sort` so they survive the reset performed by `bch2_journal_keys_sort()` and are merged afterward.

When inserting an accounting key over an allocated accounting key, the code can accumulate accounting values instead of replacing immediately.

## Overwrite Tracking

`__bch2_journal_key_overwritten()` marks a key overwritten and maintains compact contiguous overwrite ranges in `keys->overwrites`. Adjacent overwritten keys are merged into ranges, and RCU-published range arrays allow lockless skip by iterators.

`bch2_journal_key_check_or_overwrite()` checks whether an exact journal key exists or marks it overwritten. It is used during replay/rewind logic to avoid returning stale overlay entries.

## Btree And Journal Iteration

`struct btree_and_journal_iter` merges one btree node iterator with a journal iterator. `bch2_btree_and_journal_iter_peek()` advances either source to the current overlay position, picks the lower-position key from the journal or btree, skips deleted keys, enforces node max-key bounds, and returns the visible key.

`__bch2_btree_and_journal_iter_init_node_iter()` initializes the combined iterator for a node and, during recovery before multi-threaded RW operation, links journal iterators into `c->journal_iters` so gap movement can update them.

The prefetch path copies the iterator, walks ahead through the merged view, and issues btree node prefetches for child pointers.

## Sorting Replay Keys

`bch2_journal_keys_sort()` rebuilds sorted journal keys from `c->journal_entries`. It handles journal rewind ranges, validates that rewound sequences contain overwrite entries, includes only relevant `btree_keys` or `overwrite` journal entries, supports low-memory extra sorting/compaction passes, merges `pre_sort` keys, clears stale `mem_ptr` values in btree pointer keys, and logs key counts.

`journal_sort_key_cmp()` sorts equal keys so the newest applicable key survives compaction, with special handling for rewind mode and allocated synthetic keys.

## Cleanup And Diagnostics

`bch2_journal_keys_put()` decrements the journal key refcount and, on the final put, frees allocated keys, key arrays, pre-sort state, overwrite ranges, raw journal replay entries, and the genradix.

`bch2_journal_keys_reset()` frees only sorted key state, preserving raw journal entries for re-sort.

`bch2_shoot_down_journal_keys()` removes keys in a btree/level/position range. `bch2_journal_keys_dump()` prints all sorted keys. `bch2_fs_journal_keys_init()` initializes the initial ref and overwrite lock.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/btree/journal_overlay.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/btree/journal_overlay.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/btree/journal_overlay.h

## Role

This header declares the journal overlay iterator API and provides inline helpers for journal key addressing and comparison.

## Major Contents

- `struct journal_iter`: a list-linked iterator over `journal_keys` for one btree ID and level.
- `struct btree_and_journal_iter`: a combined iterator over one btree node iterator plus journal overlay entries.
- `journal_entry_radix_idx()`: maps a journal sequence to the genradix index.
- `journal_key_k()`: resolves a `journal_key` either to an allocated key or to a key embedded in a replay journal entry.
- `__journal_key_btree_cmp()`, `__journal_key_cmp()`, and `journal_key_cmp()`: shared ordering helpers.

## Exported Operations

The header exports forward, reverse, and slot journal peek helpers; key insertion/deletion helpers; overwrite checking; combined btree+journal iterator advance/peek/init/exit helpers; journal key ref release; journal key sorting; range shoot-down; dumping; and filesystem journal key initialization.

It also includes `bch2_journal_keys_put_initial()`, which drops the initial replay-key reference once replay consumers no longer need it.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/btree/journal_overlay.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/btree/journal_overlay_types.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/btree/journal_overlay_types.h

## Role

This header defines the data structures backing journal replay key storage and overlay iteration.

## Data Structures

- `struct journal_ptr`: records the physical journal location, device, bucket, offset, sector, checksum, and checksum validity.
- `struct journal_replay`: stores pointers for one replayed journal entry, checksum status, ignore flags, and the variable-sized `struct jset`.
- `struct journal_key_range_overwritten`: stores a half-open logical range of overwritten journal-key indices.
- `struct journal_key`: stores either a journal sequence/offset pair into replay data or an allocated key pointer, plus btree ID, level, allocated/overwritten/rewind flags, and overwrite-range index.
- `struct journal_keys`: owns the gap-buffer key array, initial/refcount state, pre-sort keys, overwrite mutex, and RCU-managed overwrite ranges.

## Notable Design

The `journal_keys` layout intentionally starts like a darray (`nr`, `size`, `data`) but adds a gap-buffer index. This lets the recovery path insert ordered keys efficiently while still allowing bulk sort/compact behavior after reading raw journal entries.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/btree/journal_overlay_types.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/btree/key_cache.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/btree/key_cache.c

## Role

This file implements the btree key cache: an rhashtable-backed cache for frequently accessed single keys in selected btrees. Cached keys behave like lockable synthetic leaf nodes and are integrated with the normal btree transaction, lock, journal pin, and shrinker systems.

The main user called out in the file is the alloc btree, where extent operations repeatedly read/update bucket allocation keys.

## Major Responsibilities

- Lookup cached keys by `(btree_id, bpos)`.
- Fill cache entries from ordinary btree lookups and replay journal overlay keys.
- Represent cached entries as `struct bkey_cached` objects protected by SIX locks.
- Integrate cached entries with `struct btree_path` traversal.
- Track dirty cached keys and pin journal sequences until flushed.
- Flush dirty cached keys to real btrees for journal reclaim and read-only transition.
- Drop stale cache entries when updates bypass the key cache.
- Reclaim clean cache entries through a shrinker.
- Reuse freed cache objects after SRCU-safe pending callbacks.
- Initialize and destroy per-filesystem cache state and the global slab cache.

## Lookup And Fill

`bch2_btree_key_cache_find()` performs rhashtable lookup using `struct bkey_cached_key`.

`bch2_btree_path_traverse_cached()` first tries `btree_path_traverse_cached_fast()`. The fast path finds the cached key, takes the desired SIX lock, verifies the key still matches after locking, marks it accessed, and installs it into the btree path.

On miss, `btree_key_cache_fill()` performs a real btree slot lookup with flags that avoid recursive cache fill, optionally overlays a journal replay key, marks deleted entries for immediate flush, then calls `btree_key_cache_create()`.

`btree_key_cache_create()` allocates or reuses a cache object, sizes its key buffer with slack to avoid transaction commit reallocations, copies the key, write-locks the underlying btree node to serialize insertion, inserts into the rhashtable, and converts the cached path to point at the new cached key.

## Allocation And Reuse

Cache objects are allocated from a global `bkey_cached` slab plus a separately allocated key buffer. Freed objects are not immediately reused: `bkey_cached_free_noassert()` queues them through `rcu_pending`, with separate queues for normal and per-CPU-reader locks.

`bkey_cached_alloc()` first tries to claim pending objects whose locks are idle, then attempts fresh allocation using the transaction lock-dropping allocation helper, and finally can steal from all pending queues. `bkey_cached_reuse()` scans the hashtable for clean, unaccessed, lockable entries to evict when allocation fails.

## Dirty Tracking And Journal Pins

`bch2_btree_insert_key_cached()` copies an inserted key into the cached object, marks it dirty if needed, increments `nr_dirty`, records or updates the journal sequence, adds a journal pin, and kicks journal reclaim if the dirty ratio is too high.

The comments are explicit that nojournal commits must not advance `ck->seq` unless the pin is inactive, otherwise a crash could lose a dirty cached update.

`bch2_btree_key_cache_journal_flush()` is the journal reclaim callback. It uses a lockless bailout when the key is already clean or pinned past the requested sequence, then locks the cached key through a transaction path, handles races with pin sequence updates, and flushes the key if appropriate.

## Flushing

`btree_key_cache_flush_pos()` is the core flush routine. It opens an ordinary btree slot iterator and a cached iterator, traverses the cached key, and if the key is dirty and sequence-matched, stages an internal update to the real btree, commits it with reclaim/no-ENOSPC/no-skip-noops flags, drops the journal pin, and clears dirty state or evicts the entry.

When evicting, it unlocks unrelated transaction paths, takes a nofail write lock on the cached entry, clears dirty state, removes it from the hashtable, and frees it.

`bch2_btree_key_cache_flush_going_ro()` directly walks dirty entries while going read-only. It forces `BCH_TRANS_COMMIT_no_journal_res` so flushing drops existing pins without creating fresh ones, allowing read-only cleanup loops to converge.

## Dropping Stale Entries

`bch2_btree_key_cache_drop()` handles updates that bypass the key cache. It clears dirty state and journal pins, evicts and frees the cached key, unlocks or invalidates every transaction path that points at it, marks those paths for retraversal, and verifies transaction locks.

## Shrinker

`bch2_btree_key_cache_scan()` scans the rhashtable under SRCU and RCU. It skips dirty entries, clears recently accessed entries on first pass, skips entries it cannot lock, evicts clean lockable entries, records skip/free stats, and advances `shrink_iter`.

`bch2_btree_key_cache_count()` reports reclaimable clean keys minus a small reserve to avoid excessive shrinker pressure and lock contention when the cache is nearly empty.

## Init, Exit, Diagnostics

`bch2_fs_btree_key_cache_init()` initializes pending queues, the rhashtable, and the shrinker. `bch2_fs_btree_key_cache_exit()` frees shrinker state, drains/evicts all hashtable entries while handling rehash races, asserts dirty/key counters are zero when required, destroys the rhashtable, pending queues, and percpu counters.

`bch2_btree_key_cache_to_text()` prints counters and shrinker stats. `bch2_btree_key_cache_init()` and `bch2_btree_key_cache_exit()` create/destroy the global slab cache.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/btree/key_cache.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/btree/key_cache.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/btree/key_cache.h

## Role

This header declares the btree key cache API and defines dirty-cache pressure thresholds.

## Dirty Pressure Helpers

- `bch2_nr_btree_keys_need_flush()` returns the dirty count above `1024 + nr_keys / 2`; this is used to decide when to kick journal reclaim.
- `bch2_btree_key_cache_must_wait()` uses a higher threshold of `4096 + 3/4 nr_keys` for mandatory throttling.
- `bch2_btree_key_cache_wait_done()` uses a lower threshold of `2048 + 5/8 nr_keys` as the hysteresis condition for wait completion.

## Exported Operations

The header exports journal flush, read-only flush, cache lookup, cached path traversal, cached insert, cache drop, filesystem init/exit, diagnostic text output, and global slab init/exit.

These declarations connect the cache to iterator traversal, update commit, journal reclaim, and filesystem lifecycle code.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/btree/key_cache.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/btree/key_cache_types.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/btree/key_cache_types.h

## Role

This header defines the per-filesystem state and hashtable key type for the btree key cache.

## Data Structures

`struct bch_fs_btree_key_cache` contains:

- the rhashtable and initialization flag
- shrinker pointer and scan cursor
- two `rcu_pending` queues for normal locks and per-CPU-reader locks
- per-CPU pending object counters
- atomic key and dirty-key counters
- shrinker stats for requested/free/skipped cases

`struct bkey_cached_key` is the packed rhashtable lookup key: btree ID plus btree position, aligned to 4 bytes.

## Notable Design

The two pending queues correspond to cached entries with different SIX-lock reader implementations. This avoids reusing an object with the wrong lock flavor after SRCU-delayed free.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/btree/key_cache_types.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/btree/locking.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/btree/locking.c

## Role

This file implements bcachefs btree node locking and transaction relocking. It uses SIX locks with shared, intent, and write states, plus a transaction-level deadlock detector that breaks cycles by restarting one transaction.

It is the locking companion to `iter.c`: iterators decide what locks they need, while this file acquires, upgrades, downgrades, releases, verifies, and deadlock-checks them.

## Major Responsibilities

- Initialize and destroy per-CPU lock graph state.
- Initialize btree node/key-cache SIX locks.
- Count locks held by a transaction on a node.
- Acquire write locks from intent locks while accounting for self-held read locks.
- Relock paths optimistically using SIX lock sequence numbers.
- Upgrade paths from read to intent locks when updates need stronger locks.
- Downgrade paths and transactions after commit or when stronger locks are no longer needed.
- Unlock transactions, including cache cannibalize lock and long-held SRCU state.
- Detect deadlock cycles among transactions waiting on btree locks.
- Abort selected transactions in a cycle by forcing transaction restart.
- Provide debug verification that path lock state matches lock expectations.

## SIX Lock Policy

The file’s documentation explains why bcachefs uses SIX locks:

- Shared locks allow ordinary readers.
- Intent locks exclude other intent lockers but coexist with shared readers.
- Write locks exclude everything and are held for short in-memory modifications.

Intent locks prevent classic read-to-write upgrade deadlocks during btree splits. Parent read locks may be dropped before taking child intent locks; sequence numbers allow optimistic relock if the node did not change.

## Deadlock Detector

`bch2_check_for_deadlock()` walks a graph of transactions blocked on locks. It starts from the current transaction’s `trans->locking`, then for each lock held by that transaction, snapshots conflicting waiters from the SIX lock wait FIFO and descends into those transactions.

Important helpers:

- `lock_graph_down()` pushes a transaction wait frame.
- `lock_graph_remove_non_waiters()` revalidates that recorded wait edges are still current.
- `lock_graph_descend()` detects cycles or recursion limit.
- `break_cycle()` selects a transaction to abort unless called only for debug cycle printing.
- `btree_trans_abort_preference()` chooses a restart victim, respecting `lock_may_not_fail`.
- `abort_lock()` either restarts the original transaction or wakes a foreign transaction with `lock_must_abort`.

The detector runs under RCU and preempt disable, uses per-frame darrays to snapshot waiters, and reports allocation failure with a dedicated restart reason instead of silently missing cycles.

## Relock And Upgrade

`__bch2_btree_node_relock()` attempts to reacquire a node lock by sequence number. It succeeds through `six_relock_type()` or by incrementing the lock when the saved sequence still matches. Failure can emit trace events.

`bch2_btree_node_upgrade()` converts a path level to intent locking. It handles already-unlocked/read/intent states, tries lock upgrade or relock, and emits trace diagnostics on failure.

`btree_path_get_locks()` walks from the path level up to `locks_want`, relocking or upgrading each node. On failure it records the failing level/node, optionally restarts the transaction, unlocks the path, marks it stale, and poisons lower levels so traversal climbs to the correct ancestor.

## Path And Transaction Locking

- `bch2_btree_path_relock_intent()` relocks intent locks for cache code and restarts on failure.
- `bch2_btree_path_relock_norestart()` tries relock without forcing restart.
- `__bch2_btree_path_relock()` restarts if relock fails.
- `__bch2_btree_path_upgrade_norestart()` and `__bch2_btree_path_upgrade()` request stronger locks.
- `__bch2_btree_path_downgrade()` lowers `locks_want`, unlocks unneeded ancestors, and downgrades intent locks to reads where possible.
- `bch2_trans_downgrade()` downgrades all referenced paths.
- `bch2_trans_relock()` reacquires all paths marked `should_be_locked`.
- `bch2_trans_unlock()` unlocks all btree paths and releases the btree-cache cannibalize lock.
- `bch2_trans_unlock_long()` additionally drops transaction SRCU and resets unlocked cached paths.

## Write Locking

`__bch2_btree_node_lock_write()` temporarily subtracts self-held read locks before taking a write lock, because SIX unlock wakeups depend on reader counts. It then restores the reader count. If the write lock fails, it restores the path as intent-locked.

`bch2_btree_node_lock_write_nofail()` wraps this and asserts success.

## Mutex Integration

`__bch2_trans_mutex_lock()` drops btree transaction locks before blocking on a regular mutex, then relocks afterward. If relock fails, it unlocks the mutex and returns the transaction restart/error result.

## Verification

`__bch2_btree_path_verify_locks()` checks that path lock state is internally consistent:

- an uptodate path with no locks must not claim `should_be_locked`
- each locked level must reference a valid btree node
- wanted lock type must match the held type, ignoring write-lock refinement where appropriate
- saved lock sequence must match the node lock sequence

`__bch2_trans_verify_locks()` checks every path when the transaction is marked locked, and asserts no path locks remain when the transaction is marked unlocked.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/btree/locking.c -->