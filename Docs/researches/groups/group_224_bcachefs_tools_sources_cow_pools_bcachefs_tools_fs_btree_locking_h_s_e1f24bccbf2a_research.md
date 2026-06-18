# Group Research: group_224_bcachefs_tools_sources_cow_pools_bcachefs_tools_fs_btree_locking_h_s_e1f24bccbf2a

Scope note: researched exactly the listed files under `sources/cow-pools/bcachefs-tools` from `Docs/research_subset_a.md`. Each source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/btree/locking.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/btree/locking.h

Read completeness: full file read, 503 lines.

Purpose: inline and exported locking helpers for bcachefs btree transactions. The file bridges `struct btree_trans`, `struct btree_path`, `struct btree_bkey_cached_common`, and the six-lock implementation, so iterator traversal code can record which node locks are held or wanted and can restart safely on contention or invalidation.

Key definitions:
- `enum btree_node_locked_type` maps btree path lock state onto six-lock read, intent, and write modes, plus `BTREE_NODE_UNLOCKED`.
- `trans_set_locked()` and `trans_set_unlocked()` wrap transaction lockdep state, pin execution to the current CPU while btree locks are held, and set `PF_MEMALLOC_NOFS` to avoid filesystem recursion during memory allocation.
- `btree_node_locked_type()`, `btree_node_*_locked()`, `mark_btree_node_locked*()`, `btree_lock_want()`, and level helpers encode per-level lock state into `path->nodes_locked`.
- Unlock helpers include `bch2_btree_node_unlock_write_inlined()`, `btree_node_unlock()`, `__bch2_btree_path_unlock()`, and `bch2_btree_node_unlock_with_path()`.
- Lock helpers include `btree_node_lock_nopath()`, `btree_node_lock()`, `__btree_node_lock_write()`, `bch2_btree_node_lock_write()`, `bch2_btree_node_lock_write_nofail()`, and `bch2_btree_node_lock_with_path()`.
- Relock and upgrade surface: `bch2_btree_path_relock()`, `bch2_btree_node_relock()`, `bch2_btree_node_relock_notrace()`, `bch2_btree_path_upgrade_norestart()`, and `bch2_btree_path_upgrade()`.

Control-flow and invariants:
- `bch2_btree_path_traverse()` refuses to traverse from an unlocked/restarting transaction and only calls the slow traversal path when no nodes are locked.
- Write-lock acquisition intentionally marks the path as write-locked before trying `six_trylock_write()`, because the deadlock detector must know this transaction is trying to block readers behind a pending write lock.
- Unlocking a write lock first downgrades transaction-visible state to intent, advances linked path lock sequence numbers when recursion is not active, then releases the six write lock.
- Relock helpers compare desired lock mode against saved path state and lock sequence values so stale paths restart rather than using reclaimed or modified nodes.
- `btree_path_set_should_be_locked()` records that a path must relock successfully or force a transaction restart.

Dependencies and integration:
- Depends on `btree/cache.h`, `btree/iter.h`, `btree/locking_types.h`, and `util/six.h`.
- Uses `struct btree_trans` and `struct btree_path` fields defined in `types.h`.
- Calls out to slow paths and diagnostics implemented elsewhere: `bch2_btree_node_lock_slowpath()`, `bch2_btree_node_lock_write_contended()`, `bch2_six_check_for_deadlock()`, `bch2_check_for_deadlock()`, and lock verification helpers.
- Interacts with write code through `bch2_btree_node_unlock_write()` and with traversal/update code through path relock, upgrade, and should-be-locked state.

Risks and validation notes:
- `nodes_locked` packs two bits per level; any new lock type or depth change must preserve the encoding assumptions and `BUILD_BUG_ON()` checks.
- Transaction code relies on CPU migration and `PF_MEMALLOC_NOFS` being restored exactly once in `trans_set_unlocked()`.
- Deadlock detection depends on callers setting `trans->locking_hash_val` before `btree_node_lock_nopath()` when the lock is looked up by hash.
- Debug coverage is mostly compile-time and runtime assert based: `EBUG_ON`, lockdep, event traces, optional lock time stats, and `bch2_trans_verify_locks()`.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/btree/locking.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/btree/locking_types.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/btree/locking_types.h

Read completeness: full file read, 39 lines.

Purpose: shared data structures for btree lock cycle detection. This header intentionally contains only state types, keeping the larger locking logic in `locking.h` and its implementation files.

Key definitions:
- `struct trans_waiting_for_lock` represents one transaction waiting for one node lock. It records the waiting transaction, wanted node, wanted six-lock mode, and cursor state for walking held locks.
- `waitlist` is a preallocated darray of conflicting `struct btree_trans *` entries, sized for 16 entries, used to snapshot waiter lists so recursive cycle-detection traversal is stable against concurrent wakeups.
- `struct lock_graph` is a small fixed-depth graph stack with eight `trans_waiting_for_lock` frames, a count, and a `printed_chain` diagnostic flag.

Dependencies and integration:
- Includes `util/darray.h`, `util/six.h`, and `btree/types.h`.
- Used by the per-CPU `bch2_lock_graph` declared in `locking.h`.
- The graph records `struct btree_bkey_cached_common` nodes, so it covers both btree nodes and cached bkeys that share the common lock header.

Risks and validation notes:
- The fixed graph depth is intentionally small; if future lock dependency chains become deeper, diagnostics or detection may need widening.
- `waitlist_idx`, `level`, and `path_idx` are iteration cursors and must stay consistent with the transaction path representation in `types.h`.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/btree/locking_types.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/btree/node_scan.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/btree/node_scan.c

Read completeness: full file read, 608 lines.

Purpose: recovery scanner for discovering valid btree nodes directly on member devices. It is used when topology/root information is missing or needs reconstruction. The scanner probes possible btree-node locations, validates candidate nodes through normal btree read validation, merges replicas, removes overwritten ranges, and can emit reconstructed btree pointer keys into the journal.

Key structures and helpers:
- `struct find_btree_nodes_worker` carries a closure, shared scan state, and one device for a scanning kthread.
- `bch2_found_btree_node_to_text()` and `found_btree_nodes_to_text()` format discovered nodes, key ranges, sequence/journal sequence, cookie, and extent pointers.
- `found_btree_node_to_key()` converts a `found_btree_node` into a `KEY_TYPE_btree_ptr_v2` key with min/max range, replica pointers, sectors written, and range-updated bit.
- Comparator families sort by cookie for replica merging, by btree/level/range/time for overwrite handling, and by range start for eytzinger lookup.

Control flow:
- `try_read_btree_node()` first reads one filesystem block at a candidate sector, checks magic, decrypts the header area if needed, rejects reconstructable/internal IDs and invalid level/id values, then builds a candidate pointer and reads the full btree node size.
- Full candidate validation delegates to `bch2_btree_node_read_done()`. Only candidates that pass normal btree-node validation are appended to `f->nodes`.
- `read_btree_nodes_worker()` allocates temporary btree memory and a bio, walks btree-marked buckets when the on-disk member bitmap is available, scans btree-node-sized offsets, and periodically logs progress.
- `read_btree_nodes()` starts one worker per online member that can contain btree data, waits with `closure_sync_unbounded()`, and returns the shared scan error.
- `bch2_scan_for_btree_nodes()` runs workers once, merges same-cookie replicas, sorts nodes by logical position, trims or drops overwritten ranges with a min-heap, verifies no overlaps remain, and stores the final array in eytzinger order.
- `bch2_btree_node_is_stale()` looks for newer scanned nodes overlapping a cached node.
- `bch2_btree_has_scanned_nodes()` and `bch2_get_scanned_nodes()` trigger the scan recovery pass and query discovered nodes; `bch2_get_scanned_nodes()` also validates generated pointer keys and inserts them into the journal.

Dependencies and integration:
- Uses allocation bucket metadata for generation numbers, btree cache memory allocation for temporary nodes, `read.h` validation, journal insertion, recovery pass orchestration, kthreads, bios, heaps, and eytzinger search.
- The output type `found_btree_node` is declared in `node_scan_types.h`; declarations are in `node_scan.h`.
- Recovery code calls these helpers when rebuilding roots/interior nodes from scanned leaf/interior node evidence.

Risks and validation notes:
- Encrypted metadata cannot be scanned without `c->chacha20_key_set`.
- Endian conversion is not handled in `try_read_btree_node()` after validation; mismatched endian marks the scan with `-EINVAL`.
- Replica merging assumes same cookie means the same logical node; more than `BCH_REPLICAS_MAX` replicas is a hard recovery error.
- Overwrite trimming depends on sequence and journal sequence ordering; equal-time leaf overlap handling keeps later ranges by positional trimming while interior equal-time overlap is dropped.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/btree/node_scan.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/btree/node_scan.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/btree/node_scan.h

Read completeness: full file read, 18 lines.

Purpose: public declarations for btree node scanning and scanned-node recovery queries.

Declared API:
- `bch2_found_btree_node_to_text()` formats one scanned node.
- `bch2_scan_for_btree_nodes()` performs the scan and normalizes discovered nodes.
- `bch2_btree_node_is_stale()` tests a loaded node against scan results.
- `bch2_btree_has_scanned_nodes()` and `bch2_get_scanned_nodes()` expose recovery queries over scanned nodes.
- `bch2_find_btree_nodes_init()` and `bch2_find_btree_nodes_exit()` manage `struct find_btree_nodes` lifetime.

Dependencies and integration:
- Expects `struct printbuf`, `struct bch_fs`, `struct found_btree_node`, `struct btree`, and `struct find_btree_nodes` from surrounding bcachefs headers.
- Implemented by `node_scan.c`; state types are in `node_scan_types.h`.

Risks and validation notes:
- This header does not include `node_scan_types.h` directly, so users must include appropriate type definitions before using the full signatures.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/btree/node_scan.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/btree/node_scan_types.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/btree/node_scan_types.h

Read completeness: full file read, 31 lines.

Purpose: type definitions for scanned btree-node recovery state.

Key definitions:
- `found_btree_node` stores the logical identity and physical replicas of one discovered node: btree id, level, sectors written, node sequence, journal sequence, cookie, min/max key range, replica count, and extent pointers.
- `range_updated` records that recovery trimmed the node's logical range because another discovered node overwrote part of it.
- `DEFINE_DARRAY(found_btree_node)` creates the dynamic array type used by the scanner.
- `struct find_btree_nodes` owns scan status, a mutex, and the discovered-node array.

Dependencies and integration:
- Includes `util/darray.h`; relies on `struct bpos` and `struct bch_extent_ptr` definitions from broader bcachefs type includes.
- Embedded in `struct bch_fs_btree` as `node_scan` via `types.h`.

Risks and validation notes:
- `ptrs` is capped at `BCH_REPLICAS_MAX`; scanner code treats overflow as a recovery error.
- `ret` is shared by worker threads and updated under broader scanner conventions; node insertion itself is protected by `lock`.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/btree/node_scan_types.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/btree/read.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/btree/read.c

Read completeness: full file read, 1320 lines.

Purpose: btree node read, validation, retry, normalization, root read, and scrub logic. This file turns on-disk btree-node buffers into in-memory btree nodes with one sorted bset, handles checksum/encryption/version compatibility, retries readable replicas, logs hard and soft errors, and schedules repairs when needed.

Major components:
- IO lock and wait helpers: `bch2_btree_node_io_lock()`, `bch2_btree_node_io_unlock()`, `bch2_btree_node_wait_on_read()`, and `bch2_btree_node_wait_on_write()` coordinate node IO flags and submit queued write bios before sleeping.
- Error reporting: `btree_err_msg()` and `__btree_err()` attach device, node offset, bset offset, fsck error id, retry state, and read/write context to validation errors.
- Topology repair helper: `bch2_btree_node_drop_keys_outside_node()` removes keys outside a repaired node range and rebuilds aux search trees.
- Validation: `bch2_validate_bset()` validates bset version, checksum mode flags, offsets, header identity, min/max keys, and key format; `bch2_validate_bset_keys()` validates individual packed keys, ordering, compatibility conversion, and can drop damaged keys when fsck permits.
- Main read completion: `bch2_btree_node_read_done()` walks all bsets in a node, verifies checksum/decrypts, validates metadata, skips blacklisted non-first bsets, sorts and de-overlaps keys through `bch2_key_sort_fix_overlapping()`, rebuilds the node into one bset, validates values, clears in-memory btree pointer fields, and marks nodes for rewrite when needed.
- Asynchronous read path: `btree_node_read_endio()` queues `btree_node_read_work()`, which retries alternate replicas, records IO failures, schedules rewrite after soft errors, and queues merge work for very empty nodes.
- Public read entry: `bch2_btree_node_read()` chooses a read device, allocates a `btree_read_bio`, maps the btree node buffer, and submits sync or async IO.
- Root loading: `bch2_btree_root_read()` allocates a cache node, reads it synchronously, transitions cache state, and installs the root for reads.
- Scrub: `bch2_btree_node_scrub()` reads one pointer replica into a bounce buffer and `btree_node_scrub_work()` rewrites the btree pointer key if checksum/magic validation fails.

Control-flow and invariants:
- Read validation uses the same bset/key validation functions as write validation, with compatibility transforms applied before/after on-disk version checks.
- `bch2_btree_node_read_done()` always collapses read bsets into one sorted in-memory bset and sets aux trees and whiteout flags for normal in-memory operation.
- If `btree_ptr_v2.sectors_written` is zero, the node is accepted but marked `need_rewrite_ptr_written_zero`.
- Blacklisted journal sequence handling distinguishes first bset from later bsets and pointer-written from legacy full-node reads.
- Read retry tracks per-device failures in `struct bch_io_failures` and only reports hard lost data when no readable replica remains.

Dependencies and integration:
- Uses `btree/sort.h` for sorting and bounce allocation, `btree/update.h` for rewrite scheduling, `btree/write.h` for IO wait behavior, checksum/encryption helpers, journal sequence blacklist, recovery state, and device IO accounting.
- Exports functions declared in `read.h`; used by node scan, cache/root loading, scrub/fsck, and normal traversal paths.

Risks and validation notes:
- The file is deliberately fsck-aware: many corruptions can be fixed by truncating/dropping keys or updating superblock versions, but write-time corruption triggers emergency read-only.
- Compatibility transforms mutate bset/node/key fields during validation; callers must pass the correct read/write direction.
- Scrub only handles `KEY_TYPE_btree_ptr_v2` and does not fully rebuild the in-memory node; it checks magic/checksums and requests rewrite through transaction code.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/btree/read.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/btree/read.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/btree/read.h

Read completeness: full file read, 184 lines.

Purpose: public interface and inline helpers for btree node reads, bset encryption/decryption, validation, root reads, scrub, and metadata-version compatibility transforms.

Key definitions:
- `btree_ptr_sectors_written()` extracts `sectors_written` from `KEY_TYPE_btree_ptr_v2`.
- `bch2_bkey_in_btree_node()` validates a key position against a node's min/max range and reports fsck errors.
- `struct btree_read_bio` embeds a bio plus filesystem/device/node context, selected extent pointer, work item, timing, and async object-list index.
- `btree_nonce()` derives a metadata nonce from bset offset, bset sequence, journal sequence, and `BCH_NONCE_BTREE`.
- `bset_encrypt()` encrypts/decrypts the btree header region for offset zero and the bset data for all offsets.
- `compat_bformat()`, `compat_bpos()`, and `compat_btree_node()` implement on-disk compatibility for inode btree field order and pre-snapshot formats.

Declared API:
- IO coordination: `bch2_btree_node_io_lock()`, `bch2_btree_node_io_unlock()`, `bch2_btree_node_wait_on_read()`, `bch2_btree_node_wait_on_write()`, and the `btree_node_io_lock` guard.
- Validation: `bch2_validate_bset_keys()`, `bch2_validate_bset()`, and `bch2_btree_node_read_done()`.
- Read/scrub operations: `bch2_btree_node_read()`, `bch2_btree_root_read()`, `bch2_btree_node_scrub()`, and `bch2_btree_flush_all_reads()`.

Dependencies and integration:
- Includes bkey methods, bset helpers, locking, checksum, extents, and init error definitions.
- Used by `read.c`, `node_scan.c`, write validation, and recovery code.

Risks and validation notes:
- `bset_encrypt()` is symmetric and called for both encryption and decryption; nonce offset handling must match on-disk block layout.
- Compatibility helpers intentionally mutate positions and formats; applying them twice or in the wrong direction would corrupt interpretation.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/btree/read.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/btree/sort.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/btree/sort.c

Read completeness: full file read, 609 lines.

Purpose: sorting, repacking, duplicate/whiteout filtering, compaction, and aux-tree rebuild logic for btree node bsets. It is used after reads, before writes, during node compaction, and when copying keys between nodes.

Major components:
- `sort_iter_*()` implements a small multi-run merge iterator over sorted bsets. It keeps the smallest current key at `data[0]` by local sifting instead of a heap.
- `bch2_key_sort_fix_overlapping()` sorts read bsets, drops deleted keys and older same-position keys, and returns live key accounting.
- `bch2_sort_repack()` walks a `btree_node_iter`, optionally drops whiteouts, transforms keys into a new bkey format, and accounts packed/unpacked keys.
- `bch2_sort_keys_keep_unwritten_whiteouts()` sorts write-output keys while preserving unwritten whiteouts that still matter and dropping overwritten whiteouts.
- `bch2_sort_keys()` is the normal in-memory compaction sorter that drops all deleted keys.
- Bounce allocation helpers allocate temporary node-sized buffers from fast kvmalloc or the btree bounce mempool.
- Whiteout helpers include `bch2_set_bset_needs_whiteout()`, `bch2_sort_whiteouts()`, `bch2_drop_whiteouts()`, and `bch2_compact_whiteouts()`.
- Node compaction and copying helpers include `bch2_btree_node_sort()`, `bch2_btree_sort_into()`, `bch2_btree_node_compact()`, and `bch2_btree_build_aux_trees()`.

Control-flow and invariants:
- Read-time sorting uses pointer order as a tie breaker so newer/older bsets can be resolved deterministically by later logic.
- Write-time sorting explicitly adds the unwritten whiteout range into the sort iterator before outputting a disk bset.
- `bch2_btree_node_sort()` can sort the entire node into a bounce buffer and swap node buffers to avoid a full copy when memory profiling is disabled.
- `bch2_drop_whiteouts()` may also move unwritten bset entries down in memory so the write block area remains contiguous.
- After compaction/sort, the code rebuilds aux trees and verifies key accounting with `bch2_verify_btree_nr_keys()`.

Dependencies and integration:
- Depends on packed key comparison, bset helpers, btree interior layout, extents, scheduler/memalloc flags, and node-size options.
- Read path uses `bch2_key_sort_fix_overlapping()`.
- Write path uses `bch2_sort_whiteouts()` and `bch2_sort_keys_keep_unwritten_whiteouts()`.
- Update/insert paths rely on compaction helpers to maintain `MAX_BSETS` constraints.

Risks and validation notes:
- Some unpack helpers read before key memory for optimized field extraction; `bch2_sort_whiteouts()` pads its bounce allocation to keep that valid.
- Whiteout compaction relies on `needs_whiteout` semantics; dropping the wrong deleted key can alter snapshot/extent overwrite semantics.
- `should_compact_all()` encodes a geometric-size heuristic between full node size and write-set buffer size; tuning affects write amplification and insert cost.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/btree/sort.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/btree/sort.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/btree/sort.h

Read completeness: full file read, 113 lines.

Purpose: public declarations and small inline helpers for btree bset sorting and compaction.

Key definitions:
- `struct sort_iter` stores a target btree, used/size counts, and an array of sorted key ranges.
- `struct sort_iter_stack` provides stack storage for `MAX_BSETS + 1` ranges.
- `sort_iter_init()`, `sort_iter_stack_init()`, and `sort_iter_add()` initialize and populate the merge iterator.
- `enum compact_mode` distinguishes lazy whiteout compaction from complete compaction.
- `should_compact_bset_lazy()` and `bch2_maybe_compact_whiteouts()` encode the lazy dead-key threshold.
- `should_compact_all()` decides whether a node with `MAX_BSETS` should be sorted down to one bset based on the middle bset's size.

Declared API:
- Sorting/repacking: `bch2_key_sort_fix_overlapping()`, `bch2_sort_repack()`, `bch2_sort_keys_keep_unwritten_whiteouts()`, and `bch2_sort_keys()`.
- Bounce buffers: `bch2_btree_bounce_alloc()` and `bch2_btree_bounce_free()`.
- Whiteouts/compaction: `bch2_set_bset_needs_whiteout()`, `bch2_sort_whiteouts()`, `bch2_drop_whiteouts()`, `bch2_compact_whiteouts()`, `bch2_btree_node_sort()`, `bch2_btree_sort_into()`, `bch2_btree_node_compact()`, and `bch2_btree_build_aux_trees()`.

Dependencies and integration:
- Includes `btree/interior.h` for btree node/bset layout helpers.
- Used by read, write, split/interior update, and cache maintenance paths.

Risks and validation notes:
- `sort_iter_add()` asserts capacity but skips empty ranges, so callers must size the iterator for the maximum number of non-empty ranges they may add.
- Compaction thresholds directly influence node write frequency and insert latency.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/btree/sort.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/btree/types.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/btree/types.h

Read completeness: full file read, 1205 lines.

Purpose: central type and flag definitions for bcachefs btree nodes, cache state, iterators, transaction state, key cache, write types, filesystem-level btree state, bset accessors, and btree-id property helpers.

Major type groups:
- Node/key accounting: `MAX_BSETS`, `struct btree_nr_keys`, `struct bset_tree`, and `struct btree_write`.
- Common lock identity: `struct btree_bkey_cached_common` is shared by real btree nodes and cached bkeys.
- Node cache state: `enum btree_node_cache_state` defines NONE, FREED, FREEABLE, CLEAN, and DIRTY membership states.
- `struct btree` contains the common lock header, rhashtable linkage, state flags, on-disk format/unpack metadata, node data buffers, bset trees, key counts, sibling estimates, whiteouts, current/previous write pins, node key, async write-blocking lists, open buckets, LRU list, and cache state.
- Cache/root state: `struct btree_root` and `struct bch_fs_btree_cache` hold packed root pointers, known/extra roots, rhashtable, free/live lists, in-flight counters, shrinker stats, alloc/cannibalize state, and pinned-node ranges.
- Iterator/update/trigger flags: `BTREE_ITER_FLAGS`, `STR_HASH_FLAGS`, `BTREE_UPDATE_FLAGS`, and `BTREE_TRIGGER_FLAGS` generate the shared `enum btree_iter_update_trigger_flags`.
- Path/iterator types: `struct btree_path`, `struct btree_iter`, and `struct get_locks_fail` model low-level locked paths and high-level key iterators.
- Key cache: `struct bkey_cached` stores cached non-leaf? key values with dirty/immediate flush flags, rhashtable linkage, journal pin, sequence, and RCU.
- Transaction staging: `struct btree_insert_entry`, `struct btree_trans_subbuf`, and `struct btree_trans` store path arrays, sorted path order, pending updates, bump allocation, restart/debug state, queued write bios, journal/accounting subbuffers, hooks, journal reservations, disk reservations, and inline initial storage.
- Transaction infrastructure: `struct btree_transaction_stats`, `struct bch_fs_btree_trans`, per-CPU buffers, mempools, SRCU barrier, and stats.
- Write state: `BCH_BTREE_WRITE_TYPES`, `enum btree_write_type`, `BTREE_FLAGS`, generated flag accessors, and rewrite reasons.
- Filesystem-level state: `struct bch_fs_btree` aggregates write stats, biosets, read/write workqueues, cache, evicted-size sidecar, key cache, per-btree write buffers, write-buffer workqueues, transaction state, reserve cache, interior updates, rewrites, and node scan state.

Important inline helpers:
- Cache counts: `btree_cache_nr_live()` and `btree_cache_nr_dirty()`.
- Iterator path access: `btree_iter_path()` and `btree_iter_key_cache_path()`.
- Node position: `btree_node_pos()`.
- Bset/node pointer conversion and accessors: `bset()`, `set_btree_bset_end()`, `set_btree_bset()`, `btree_bset_first()`, `btree_bset_last()`, `btree_bkey_first()`, `btree_bkey_last()`, `bset_u64s()`, `bset_dead_u64s()`, and `bset_byte_offset()`.
- Node type and btree property helpers: `__btree_node_type()`, `btree_node_type()`, `btree_node_type_has_*_triggers()`, `btree_id_is_extents()`, `btree_type_has_snapshots()`, `btree_id_is_extents_snapshots()`, `btree_type_has_snapshot_field()`, `btree_type_has_data_ptrs()`, `btree_type_uses_write_buffer()`, and `btree_trigger_order()`.

Dependencies and integration:
- Pulls in allocation, replica, bbpos, bkey, interior, key-cache, node-scan, write-buffer, journal, darray, and six-lock types.
- Almost every other file in this group depends on this header directly or indirectly.
- `struct bch_fs_btree` is the aggregation point tying node read/write, write buffer, transactions, cache, and recovery scanning together.

Risks and validation notes:
- This header carries many bitfield and packed-layout assumptions: lock state bits, root pointer low-bit packing, bkey unpack byte alignment, write type bits embedded in node flags, and `wb_key_ref` ordering in related write-buffer types.
- Transaction memory is capped by 16-bit offsets and `BTREE_TRANS_MEM_MAX`; subbuffer allocation depends on arena offsets fitting in `u16`.
- `BTREE_ITER_FLAG_BIT_*` is intended to fit in a `u16`; adding flags can break iterator flag storage if not audited.
- Many invariants are checked by `BUG_ON`/`EBUG_ON` in users rather than by this header itself.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/btree/types.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/btree/update.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/btree/update.c

Read completeness: full file read, 944 lines.

Purpose: transaction update staging for btree key modifications. This file handles extent overwrite splitting/merging, snapshot whiteout insertion, key-cache update routing, sorted pending-update insertion, transaction subbuffer allocation, delete/range-delete helpers, bit updates, and journal log entries.

Major components:
- `btree_insert_entry_cmp()` orders pending updates by trigger order, cached state, level, and position so commit can run updates deterministically.
- Extent merge helpers `extent_front_merge()` and `extent_back_merge()` coalesce adjacent mergable extents when journal replay is complete and snapshot overwrite checks permit it.
- Snapshot whiteout helpers `need_whiteout_for_snapshot()`, `__bch2_insert_snapshot_whiteouts()`, and `bch2_trans_update_extent_overwrite()` preserve visibility semantics when overwriting or splitting keys across snapshots.
- `bch2_trans_update_extent()` handles extent insertions by walking overlapping keys, front/back merging, converting whiteout types, splitting overwritten extents, and finally staging the non-deleted insert.
- `btree_trans_update_by_path()` is the core staging helper. It asserts path/position invariants, builds a `btree_insert_entry`, replaces an existing same-position pending update if present, snapshots the old btree key/value, consults journal overlay during replay, refs the path, and emits trace data.
- Key-cache handling uses `bch2_trans_update_get_key_cache()` and `flush_new_cached_update()` to ensure cached btrees update the key cache while preserving the invariant that a cached key also exists in the backing btree.
- `bch2_trans_update_ip()` is the public low-level update entry: it validates memory, dispatches extent updates, turns snapshot deletes into whiteouts when needed, routes cached btrees through the key cache, and triggers immediate key-cache flush when required.
- `bch2_trigger_get_mutable_new()` lets triggers grow the buffer for an in-flight inserted key before atomic trigger phase.
- Transaction arena helpers `__bch2_trans_subbuf_alloc()` and `bch2_trans_subbuf_reserve()` manage journal/accounting subbuffers inside `trans->mem`.
- Public insert/delete helpers include `bch2_btree_insert_nonextent()`, `bch2_btree_insert_trans()`, `bch2_btree_insert()`, `bch2_btree_delete_at()`, `bch2_btree_delete()`, `bch2_btree_delete_range_trans()`, and `bch2_btree_delete_range()`.
- Bitset-like helpers include `bch2_btree_bit_mod_iter()`, `bch2_btree_bit_mod()`, and `bch2_btree_bit_mod_buffered()`.
- Logging helpers append log strings and bkeys to journal entries, including early-journal storage before the journal is running.

Dependencies and integration:
- Includes iterator, journal overlay, locking, update declarations, keylist, debug, counters, and snapshot helpers.
- Depends on `update.h` for public wrappers and commit macros.
- Feeds commit logic implemented outside this file through `__bch2_trans_commit()` and transaction update arrays.
- Uses write-buffer insertion through `bch2_trans_update_buffered()` in the header and `bch2_btree_bit_mod_buffered()` here.

Risks and validation notes:
- Snapshot and extent overwrite paths are sensitive: wrong whiteout type or split boundaries can expose stale extents in descendant snapshots.
- During journal replay, normal write-buffer use is mostly bypassed except accounting and need-discard cases because replay synchronization depends on locked btree nodes.
- Pending update replacement assumes triggers have not run on the overwritten pending entry.
- Key-cache coherency requires immediate backing-btree flush when a new cached update would otherwise have no old btree key.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/btree/update.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/btree/update.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/btree/update.h

Read completeness: full file read, 484 lines.

Purpose: public transaction update API, commit flag definitions, buffered-update helpers, transaction subbuffer helpers, commit wrappers, and mutable-key allocation helpers.

Key declarations and flags:
- Node write/update declarations: `bch2_btree_node_prep_for_write()`, `bch2_btree_bset_insert_key()`, journal pin flush callbacks, `bch2_btree_add_journal_pin()`, and `bch2_btree_insert_key_leaf()`.
- `BCH_TRANS_COMMIT_FLAGS()` defines commit flags for ENOSPC checking, write refs, journal reservation handling, noop skipping, journal reclaim, journal replay, and accounting application.
- Update operations include delete, insert, range delete, bit modification, snapshot whiteout insertion, extent overwrite handling, empty slot lookup, and trigger mutable-new access.
- `bch2_trans_update_ip()`, `bch2_trans_update_buf()`, and `bch2_trans_update()` are the core update staging APIs.
- Transaction subbuffer helpers expose typed allocation for `trans->journal_entries` and `trans->accounting`.
- `bch2_trans_commit()` sets disk reservation and journal sequence output before calling `__bch2_trans_commit()`.
- Retry wrappers `commit_do`, `nested_commit_do`, and deprecated `bch2_trans_commit_do` integrate with lock-restart loops.

Buffered update logic:
- `bch2_btree_write_buffer_insert_checks()` rejects write-buffer updates for btrees not marked `BTREE_IS_write_buffer`.
- `bch2_trans_update_buffered()` validates memory, uses direct clone insert during most journal replay, and otherwise appends a `BCH_JSET_ENTRY_write_buffer_keys` journal entry. Accounting updates remain buffered during replay because they are deltas requiring strict flush order.

Mutable key helpers:
- `__bch2_bkey_make_mut_noupdate()` reassembles an immutable key into transaction memory, optionally type-checking and padding to a minimum size.
- `bch2_bkey_make_mut*()` variants also stage the updated key through an iterator.
- `bch2_bkey_get_mut*()` variants initialize an intent iterator, fetch a key, copy it into transaction memory, and stage it.
- `bch2_bkey_alloc()` allocates and initializes a new typed key at the iterator position and stages it.

Dependencies and integration:
- Includes iterator, journal, superblock IO, and snapshot helpers.
- Implemented by `update.c` and commit code elsewhere.
- Used widely by filesystem metadata operations that modify btrees.

Risks and validation notes:
- `bch2_trans_reset_updates()` drops path refs and zeroes subbuffer sizes; callers must not hold pointers into transaction memory across restarts.
- `bch2_trans_commit_lazy()` returns a transaction restart after a successful commit when updates existed, forcing callers in lazy contexts to restart.
- Buffered update journal entries preserve original ordering; re-journaling write-buffered keys later would break recovery order.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/btree/update.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/btree/write.c -->
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
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/btree/write.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/btree/write.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/btree/write.h

Read completeness: full file read, 45 lines.

Purpose: public declarations and data structure for btree node write IO.

Key definitions:
- `struct btree_write_bio` wraps a work item, copied btree pointer key, bounce data pointer and size, sector offset, timing, optional async object-list index, and embedded `struct bch_write_bio`.
- `enum btree_write_flags` extends write type bits with `BTREE_WRITE_only_if_need` and `BTREE_WRITE_already_started`.
- `btree_node_write_if_need()` is a convenience wrapper around `bch2_btree_node_write_trans()`.

Declared API:
- `bch2_btree_post_write_cleanup()`
- `__bch2_btree_node_write()`
- `bch2_trans_submit_write_bios()`
- `bch2_btree_node_write_trans()`
- `bch2_btree_init_next()`
- `bch2_btree_write_stats_to_text()`
- `bch2_btree_flush_all_writes()`
- `bch2_btree_cancel_all_writes()`

Dependencies and integration:
- Includes data write types for `struct bch_write_bio`.
- Implemented by `write.c` and used by traversal, update, cache reclaim, journal reclaim, and read wait paths.

Risks and validation notes:
- `BTREE_WRITE_only_if_need` and write-type bits share the same integer namespace; additions must preserve the `BTREE_WRITE_TYPE_BITS` offset convention from `types.h`.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/btree/write.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/btree/write_buffer.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/btree/write_buffer.c

Read completeness: full file read, 1488 lines.

Purpose: batching layer for btrees with many small updates, especially accounting, LRU, backpointer, discard, deleted-inode, reconcile, and stripe-backpointer btrees. It moves journaled write-buffer entries into per-btree buffers, sorts and deduplicates them, flushes them to btree leaves with a fast path when possible, and preserves journal ordering with pins and slowpath commits when required.

Major components:
- Compile-time consistency check ensures the dense `BCH_WRITE_BUFFER_BTREES()` list matches all `BTREE_IS_write_buffer` btree ids.
- `wb_key_ref_cmp()`, `wb_key_eq()`, `wb_key_seq_cmp()`, and `wb_sort()` implement compact position/index sorting for buffered keys, including an x86_64 carry-chain comparator.
- `wb_flush_one()` traverses to the target leaf, optionally accumulates accounting deltas into an existing accounting key, takes a write lock, prepares the node for write, fast-inserts if the key fits, and schedules merge work if needed.
- `wb_flush_one_slowpath()` drops the leaf write lock and commits one key using the original journal sequence and reclaim-safe/no-journal-reservation flags.
- `btree_write_buffered_insert()` stages a write-buffered key into a transaction without re-journaling it, preserving original recovery order.
- Buffer management helpers resize darrays, move keys from `inc` to `flushing`, update/drop journal pins, and trigger journal watermark recalculation when low-on-write-buffer pressure clears.
- `wb_flush_sorted_range()` flushes one sorted slice with its own transaction and iterator, counting fast/noop/slowpath outcomes.
- `wb_flush_sorted_sharded()` splits large sorted arrays into CPU-bounded shards on `write_buffer_shard_wq`, joins with closures, and aggregates errors/counters.
- `bch2_btree_write_buffer_flush_locked()` is the main per-btree flush: moves intake keys, builds `wb->sorted`, sorts by position, deduplicates adjacent same-position runs, accumulates accounting duplicates, runs sharded fastpath, and then slowpath flushes remaining keys in journal sequence order.
- Journal intake helpers lock every per-btree instance in ascending order, convert `BCH_JSET_ENTRY_write_buffer_keys` to buffered entries, manage accounting accumulator arrays, pin non-empty buffers, and unlock/queue flush/resize work.
- `fetch_wb_keys_from_journal()` pulls pending write-buffer journal buffers up to a target sequence.
- Sync flush dispatch `btree_write_buffer_flush_seq()` fetches journal keys, queues all per-btree workers with pins at or below the target sequence, and waits for `write_buffer_flush_wait`.
- Journal pin callback `bch2_btree_write_buffer_journal_flush()` queues the owning per-btree flush worker.
- Public flush surfaces include `bch2_btree_write_buffer_flush_sync()`, `bch2_btree_write_buffer_flush_going_ro()`, `bch2_btree_write_buffer_tryflush()`, and `bch2_btree_write_buffer_maybe_flush()`.
- Lifecycle/stat helpers include flush worker function, accounting slowpath insertion, journal key slowpath insertion, resize, text reporting, stop/start, early init, full init, and exit.

Control-flow and invariants:
- The write buffer has per-btree `inc` and `flushing` buffers. Intake goes to `inc` unless `flushing` is locked and has room; flushing workers drain `flushing` and opportunistically move `inc`.
- Journal pins are attached when keys enter buffers and only dropped after the relevant buffered keys are flushed or retained for a later accounting-replay pass.
- Same-position dedup runs before sharding so no duplicate key run can straddle shard boundaries and flush out of order.
- Accounting keys are deltas. Duplicate accounting keys are accumulated, and accounting flushing is deferred until `BCH_FS_accounting_replay_done` when necessary.
- Fastpath leaf insertion does not re-journal the key; slowpath commits use `BCH_TRANS_COMMIT_no_journal_res` with `trans->journal_res.seq` set to the original buffered sequence.
- Flush workers drain everything once queued, not just threshold-triggered work, and wake sync flush waiters afterward.

Dependencies and integration:
- Depends on accounting accumulation, btree locking/update/interior helpers, extents, journal read/reclaim, counters, enumerated write refs, workqueues, sorting, closures, and transaction restart handling.
- Public inline helpers and declarations live in `write_buffer.h`; data structures live in `write_buffer_types.h`.
- Integrated with journal replay/read paths by converting journal entries from write-buffer form back to normal btree keys once staged.

Risks and validation notes:
- Ordering is the central correctness risk: re-journaling buffered keys or flushing same-position duplicates out of order can make crash recovery replay the wrong value.
- Memory pressure can force partial moves from `inc` to `flushing`; pin updates must match the first remaining sequence in each buffer.
- Accounting replay deferral is a special case that can leave keys in `flushing`; compaction keeps only non-zero live deltas.
- The x86_64 comparator is checked against the generic comparator under `EBUG_ON`, but any layout change to `struct wb_key_ref` must preserve its assumptions.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/btree/write_buffer.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/btree/write_buffer.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/btree/write_buffer.h

Read completeness: full file read, 208 lines.

Purpose: public API and inline helpers for btree write-buffer indexing, insertion into journal write-buffer entries, accounting accumulation, maybe-flush state, and lifecycle/stat operations.

Key definitions and helpers:
- `bch_wb_btree_idx()` maps a `BTREE_ID_*` that uses the write buffer to dense `BCH_WB_BTREE_*` indexes.
- `bch_wb_btree_to_btree_id()` maps dense write-buffer indexes back to btree ids.
- `bch2_btree_write_buffer_must_wait()` reports pressure when total buffered keys exceed three quarters of allocated intake size.
- `struct wb_maybe_flush` tracks the last key that caused a maybe-flush, flush count, processed count, and whether an error was seen.
- `struct journal_keys_to_wb_btree` and `struct journal_keys_to_wb` track per-btree intake locks/room for converting one journal sequence into write buffers.
- `wb_key_cmp()` compares buffered keys by bpos for accounting eytzinger lookup.
- `bch2_accounting_key_to_wb()` fast-finds an existing accounting accumulator and adds a delta, falling back to `bch2_accounting_key_to_wb_slowpath()`.
- Low-level key layout helpers compute variable buffered-key size and iterate packed buffered-key arrays.
- `bch2_journal_key_to_wb_reserved()`, `__bch2_journal_key_to_wb()`, and `bch2_journal_key_to_wb()` append journal keys into the correct per-btree write buffer with validation and accounting special handling.

Declared API:
- Flush: `bch2_btree_write_buffer_flush_sync()`, `bch2_btree_write_buffer_flush_going_ro()`, `bch2_btree_write_buffer_tryflush()`, and `bch2_btree_write_buffer_maybe_flush()`.
- Journal conversion: `bch2_journal_keys_to_write_buffer_start()` and `bch2_journal_keys_to_write_buffer_end()`.
- Sizing/stats/lifecycle: `bch2_btree_write_buffer_resize()`, `bch2_btree_write_buffer_to_text()`, `bch2_btree_write_buffer_stop()`, `bch2_btree_write_buffer_start()`, `bch2_fs_btree_write_buffer_exit()`, `bch2_fs_btree_write_buffer_init_early()`, and `bch2_fs_btree_write_buffer_init()`.

Dependencies and integration:
- Includes bkey buffers and accounting helpers; relies on `write_buffer_types.h` through `types.h`.
- Used by journal replay/intake, transaction buffered updates, fsck maybe-flush checks, and write-buffer lifecycle code.

Risks and validation notes:
- `bch_wb_btree_idx()` intentionally `BUG()`s on non-write-buffer btrees; callers should use `bch2_btree_write_buffer_insert_checks()` before converting arbitrary btree ids.
- Buffered key arrays are stored as raw `u64` darrays with variable-size records; iterator helpers must be used consistently to avoid misalignment.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/btree/write_buffer.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/btree/write_buffer_types.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/btree/write_buffer_types.h

Read completeness: full file read, 128 lines.

Purpose: shared data structures for the btree write-buffer subsystem.

Key definitions:
- `BCH_WRITE_BUFFER_BTREES()` lists the dense subset of btrees that use write buffering: accounting, lru, need_discard, backpointers, deleted_inodes, reconcile variants, physical reconcile variants, and stripe_backpointers.
- `enum bch_wb_btree` generates dense indexes and `BCH_WB_BTREE_NR`.
- `BTREE_WRITE_BUFERED_VAL_U64s_MAX` caps inline value size for accounting buffered keys.
- `struct wb_key_ref` is a compact sort reference containing a buffer index plus serialized `struct bpos` bytes, overlaid with three 64-bit words for fast comparison.
- `struct btree_write_buffered_key` stores the original journal sequence and padded key payload.
- `struct btree_write_buffer_keys` owns a raw `darray_u64`, a journal pin, a mutex, and back-references identifying which btree and whether this is the flushing buffer.
- `WB_FLUSH_CALLERS()` and `enum wb_flush_caller` classify flush sources for diagnostics: thread, journal pin, sync, maybe, and tryflush.
- `struct bch_fs_btree_write_buffer` owns per-btree write-buffer state: filesystem/index backrefs, sorted refs, `inc` and `flushing` key arrays, flush work, caller, counters, shard stats, and accounting accumulator array.

Dependencies and integration:
- Includes Linux workqueue, darray, and journal pin types.
- Embedded as an array in `struct bch_fs_btree` from `types.h`.
- Consumed by `write_buffer.c` and `write_buffer.h`.

Risks and validation notes:
- The dense btree list must stay synchronized with `BCH_BTREE_IDS()` flags; `write_buffer.c` has a static assertion for this.
- `wb_key_ref` layout depends on endianness and `struct bpos` size; comparator code assumes the index occupies the low bits excluded by same-position equality.
- The macro name `BTREE_WRITE_BUFERED_VAL_U64s_MAX` is misspelled as "BUFERED" in the source and must be referenced exactly.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/btree/write_buffer_types.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/closure.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/closure.h

Read completeness: full file read, 6 lines.

Purpose: bcachefs-local compatibility wrapper around `vendor/closure.h`.

Definitions:
- Includes `vendor/closure.h`.
- Renames generic closure helper symbols to bcachefs-prefixed symbols through macros: `closure_wait`, `closure_return_sync`, `__closure_wake_up`, and `closure_sync_unbounded`.

Dependencies and integration:
- Used by bcachefs code that wants closure APIs without exporting or colliding with generic names.
- In this group, closure synchronization appears in node scan, write buffer shard flushing, and btree cache/write wait paths.

Risks and validation notes:
- This file is intentionally tiny but globally visible; macro renames can affect any later include order that expects the unprefixed names.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/closure.h -->