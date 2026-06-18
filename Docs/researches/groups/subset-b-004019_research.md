# Research: subset-b-004019

This grouped report covers the bcache B-tree, journal, request, extent, debug, feature, I/O, moving-GC, and statistics files listed for subset B. Each section preserves the original source path and is bounded by reconciliation markers.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/bcache/btree.c -->
# sources/distributed-fs/ceph-client/drivers/md/bcache/btree.c

Purpose: implements bcache's persistent B+tree index, in-memory B-tree node cache, node I/O, insertion/splitting, garbage collection, initial consistency scan, traversal helpers, and key-buffer scans used by writeback, debug dumping, and moving GC. It is the central metadata engine connecting cached extents to cache buckets.

Important APIs/functions: `bkey_put()` drops bucket pins for key pointers. `bch_btree_node_read_done()`, `bch_btree_node_write()`, and `__bch_btree_node_write()` validate, sort, append, and persist bsets. `bch_btree_cache_alloc/free()` manage the memory cache and shrinker. `bch_btree_node_get()` resolves a child pointer into a locked cached node, reading from disk on miss. `__bch_btree_node_alloc()`, `btree_node_free()`, and `bch_btree_set_root()` allocate, retire, and publish nodes. `bch_btree_insert()`, `bch_btree_insert_check_key()`, `bch_btree_insert_node()`, and `btree_split()` insert keys and handle restarts when stronger locks or new root levels are needed. `bch_btree_check()`, `bch_initial_mark_key()`, `bch_initial_gc_finish()`, and the GC thread maintain bucket generation/mark state. `bch_btree_map_keys()` and `__bch_btree_map_nodes()` provide traversal, while `bch_refill_keybuf()` and `bch_keybuf_next_rescan()` build ordered work queues from B-tree extents.

Control flow: read paths usually enter through mapping macros in `btree.h`, which call `bch_btree_node_get()`, run a callback, and unlock. Insertions map leaf nodes, try to append into the current unwritten bset, mark leaves dirty with an optional journal pin, and restart from the root on split or lock-upgrade requirements. Split writes replacement nodes, updates parent keys, possibly creates a new root, journals metadata, and frees the old node through a zero-key freeing marker. GC starts by clearing bucket marks, walks from the root in bounded slices, marks live pointers, coalesces or rewrites sparse/stale nodes, flushes dirty leaves before finishing, then recomputes availability and optionally runs moving GC.

State and persistence: B-tree nodes are log-structured collections of bsets on cache buckets. Writes use `REQ_FUA` metadata bios and a double-buffered `struct btree_write` journal pin so old journal entries are not reclaimed until dirty leaf changes reach disk. The cache set stores root pointer state, bucket marks, sectors-to-GC counters, allocator reserve state, and shrinker-managed node memory. The memory cache reserves enough nodes to guarantee forward progress under allocation pressure; cannibalization is serialized by `btree_cache_alloc_lock`.

Dependencies/integration: depends on `bcache.h`, `btree.h`, `debug.h`, `extents.h`, block bios, closures, workqueues, Linux shrinkers, RCU hash lists, bucket allocation, journal metadata writes, and tracepoints. It is called by `request.c` for cache insert/lookups, `journal.c` for replay and metadata durability, `movinggc.c` and writeback through key buffers, and debug verification.

Risks: incorrect lock restart logic can deadlock or corrupt traversal; dirty-leaf journal pins must be paired or journal reclaim can lose data; split/freeing marker ordering is crash-sensitive; `current->bio_list` cases return `-EAGAIN` and must be retried on worker context; GC and journal flushing race through `BTREE_NODE_journal_flush`; stale pointer marking and bucket generation arithmetic are core data-integrity risks. Test signals include boot/replay after crash, btree split/root growth, memory pressure shrinker paths, GC with dirty writeback keys, cache miss collision tests, moving-GC replacement collisions, and debug `bch_btree_verify()` failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/bcache/btree.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/bcache/btree.h -->
# sources/distributed-fs/ceph-client/drivers/md/bcache/btree.h

Purpose: declares the B-tree data structures, locking/traversal contract, map callbacks, GC entry points, insertion APIs, and key-buffer interface used across bcache. The long file comment is the authoritative design note for bcache's B+tree, node cache, I/O, and lock restart behavior.

Important APIs/types: `struct btree_write` tracks the journal pin and priority-blocking reference associated with one node write. `struct btree` stores the cached node key, level, locks, write state, delayed write work, btree key container, and hash/list membership. `enum btree_flags` exposes I/O error, dirty, write-index, and journal-flush bits with generated helpers. `struct btree_op` carries the traversal write-lock level, wait entry, and insertion-collision flag. `struct btree_check_state` and `struct btree_check_info` coordinate parallel initial B-tree checks. Public prototypes include `bch_btree_node_get()`, `bch_btree_insert()`, `bch_btree_insert_check_key()`, `bch_gc_thread_start()`, `bch_btree_check()`, and keybuf helpers.

Control flow: `bcache_btree()` obtains the child selected by a key, with read or write lock determined by `op->lock`, invokes the generated callback, and unlocks. `bcache_btree_root()` repeatedly locks the current root, invokes a root callback, releases the cannibalization lock, schedules on `-EINTR`, and finishes any wait entry. Map helpers distinguish all nodes from leaf-only walks and can request an end-key callback. `rw_lock()` and `rw_unlock()` increment the sequence around write locks, allowing cache-miss insertion to detect races after lock upgrade.

State and persistence: this header does not persist by itself, but defines the in-memory representation of persistent B-tree nodes and the flags that gate deferred writes, I/O errors, and journal flush selection. `set_gc_sectors()` sets the GC wake threshold to one sixteenth of cache capacity, coupling request insertion pressure to background GC.

Dependencies/integration: includes `bset.h` and `debug.h`, and forward-declares cache, closure, keylist, and keybuf concepts used by request, journal, moving GC, writeback, and debug code. Its macros shape most B-tree traversal call sites, so changes here affect almost every metadata path.

Risks: macro-based traversal hides blocking, lock ordering, retries, and implicit cannibalization unlocks; misuse of `op->lock` can cause missed write locks or unbounded restarts. The `force_wake_up_gc()` comment notes it cannot absolutely guarantee the GC thread runs because another writer may reset `sectors_to_gc`. Test signals should include lockdep under split/replay/writeback workloads, root replacement races, cache-miss placeholder collision behavior, and all map callback termination modes (`MAP_DONE`, `MAP_CONTINUE`, `MAP_END_KEY`).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/bcache/btree.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/bcache/debug.c -->
# sources/distributed-fs/ceph-client/drivers/md/bcache/debug.c

Purpose: provides optional bcache debug verification and debugfs dumping. Under `CONFIG_BCACHE_DEBUG`, it verifies in-memory B-tree contents against a disk reread and compares cached read data against backing storage. Under `CONFIG_DEBUG_FS`, it exposes a per-cache-set debugfs file that streams textual extent keys.

Important APIs/functions: `bch_btree_verify()` rereads a B-tree node, runs normal node read validation/sort on the debug copy, and panics with detailed dumps if the in-memory sorted keys differ from disk. `bch_data_verify()` reads the backing device for a completed bio and checks cache-returned data byte-for-byte. `bch_debug_init_cache_set()` creates a `bcache-<uuid>` debugfs file. `bch_debug_init()` creates the root `bcache` debugfs directory and `bch_debug_exit()` removes it.

Control flow: B-tree verification takes the node I/O mutex and cache-set verify mutex, reads the on-disk node into a scratch B-tree, calls `bch_btree_node_read_done()`, and compares sorted bsets. On mismatch it dumps in-memory, reread, and raw on-disk bsets before `panic()`. Data verification allocates a temporary bio with pages, reads the same backing-sector range, iterates both bios segment-by-segment, and reports cache-set errors on mismatches. The debugfs read path uses a `dump_iterator`, `bch_keybuf_next_rescan()`, and `bch_extent_to_text()` to refill a page buffer one key at a time.

State and persistence: debug code does not mutate persistent metadata, but it reads cache buckets and backing devices directly. `bch_btree_verify()` uses `c->verify_ondisk` and `c->verify_data` scratch storage allocated by B-tree cache setup. The debugfs iterator owns an independent keybuf whose `last_scanned` starts at key zero.

Dependencies/integration: depends on B-tree read validation, keybuf scanning, extent text formatting, `debugfs`, `seq_file` support, Linux bio helpers, and cache-set error handling. Request read completion can call `bch_data_verify()` when device verification is enabled.

Risks: debug verification is intentionally fatal on mismatch and can add high I/O and memory pressure. The debugfs implementation has a comment noting missing cache-set refcounting, so teardown while a dump file is open is a lifetime risk. Test signals include enabling `CONFIG_BCACHE_DEBUG` and `CONFIG_DEBUG_FS`, reading debugfs during active I/O, forced data mismatch detection, and ensuring non-debug builds compile to header stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/bcache/debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/bcache/debug.h -->
# sources/distributed-fs/ceph-client/drivers/md/bcache/debug.h

Purpose: exposes debug-only verification hooks and debug-mode feature macros while compiling them out cleanly for normal builds. It is the switch point between expensive debug instrumentation and zero-cost stubs.

Important APIs/macros: with `CONFIG_BCACHE_DEBUG`, declares `bch_btree_verify()` and `bch_data_verify()` and maps `expensive_debug_checks(c)`, `key_merging_disabled(c)`, and `bypass_torture_test(d)` to runtime cache-set/device fields. Without it, the functions become empty inline stubs and the macros return zero. With `CONFIG_DEBUG_FS`, declares `bch_debug_init_cache_set()`; otherwise that cache-set hook is an empty inline stub.

Control flow: callers can unconditionally invoke verification or query debug knobs. Preprocessor branches decide whether those calls do real work, so request, B-tree, and extent code avoid scattered `#ifdef` blocks.

State and persistence: no persistent state is declared here. The macros expose flags stored in `cache_set` or cached device structures, influencing runtime decisions such as expensive pointer validation, key merging, and randomized bypass torture.

Dependencies/integration: forward-declares `bio`, `cached_dev`, and `cache_set`; `btree.h` includes this header, and `debug.c`, `extents.c`, `request.c`, and B-tree write paths rely on the macros.

Risks: because debug macros alter behavior, tests should cover both debug and non-debug configurations. In particular, `key_merging_disabled()` changes extent merge decisions and `bypass_torture_test()` changes request bypass behavior, so debug-enabled test failures may not reproduce in production builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/bcache/debug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/bcache/extents.c -->
# sources/distributed-fs/ceph-client/drivers/md/bcache/extents.c

Purpose: defines the key operation policies used by `btree_keys` for both interior B-tree pointers and leaf data extents. It handles sorting order, overlap repair, validation, stale-pointer rejection, dirty-sector accounting, text dumping, and extent merging.

Important APIs/functions: exported ops tables `bch_btree_keys_ops` and `bch_extent_keys_ops` are consumed when `btree.c` initializes nodes by level. `bch_extent_to_text()` formats a bkey for logs/debugfs. `__bch_btree_ptr_invalid()` and `__bch_extent_invalid()` validate keys outside a `btree_keys` container. Internal callbacks include `bch_btree_ptr_bad()`, `bch_extent_sort_fixup()`, `bch_extent_insert_fixup()`, `bch_extent_bad()`, and `bch_extent_merge()`.

Control flow: B-tree pointer keys sort by normal key comparison and must have size, pointers, no dirty bit, valid bucket bounds, non-stale pointers, metadata priority, and metadata GC marks. Leaf extents sort by start key and newer set order, then `bch_extent_sort_fixup()` trims or splits overlapping older extents during sort. Insert fixup walks overlapping keys, validates replace operations, splits existing extents when an insertion lands in the middle, trims overwritten ranges, updates dirty accounting, and may shorten a replace insert if only part of the expected key is found. Merge checks contiguous pointer offsets in the same bucket and combines checksum state where possible.

State and persistence: no standalone state, but it mutates `struct bkey` contents inside B-tree nodes and updates dirty-sector counters with `bcache_dev_sectors_dirty_add()`. Pointer validation reads cache superblock bucket bounds, bucket generations, GC marks, bucket priorities, and dirty bits. Merge/trimming decisions directly shape what is persisted by later B-tree writes.

Dependencies/integration: depends on `bcache.h`, `btree.h`, `debug.h`, `writeback.h`, bucket generation helpers, bset search/insert/fixup helpers, and cache-set error reporting. B-tree read, sort, GC, insert, debug dump, journal replay, and request lookups all use these policies.

Risks: overlap repair is subtle and crash-sensitive because it decides which old cached data remains addressable. Replace validation protects cache-miss races; weakening it can overwrite fresh writes with stale backing data. Dirty accounting must match extent trimming or writeback state will drift. Test signals include overlapping writes, partial overwrite split of written and unwritten keys, checksum merge behavior, stale dirty pointer warnings, invalid bucket bounds, replace collision handling, and debug expensive checks for GC mark consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/bcache/extents.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/bcache/extents.h -->
# sources/distributed-fs/ceph-client/drivers/md/bcache/extents.h

Purpose: declares the extent and B-tree-pointer operation tables and public validation/formatting helpers implemented by `extents.c`.

Important APIs: `bch_btree_keys_ops` configures `btree_keys` for interior-node child pointers. `bch_extent_keys_ops` configures leaf nodes for data extents. `bch_extent_to_text()` formats keys for diagnostics. `__bch_btree_ptr_invalid()` and `__bch_extent_invalid()` validate keys against a cache set when a full `btree_keys` wrapper is not available.

Control flow: this header is included by B-tree, journal, debug, and request-adjacent code so they can initialize key containers or perform direct validation before marking/replaying keys.

State and persistence: no local state. The declared ops determine how on-disk bsets are canonicalized after reads and before writes, so changing them changes persistent B-tree semantics.

Dependencies/integration: forward-declares `struct bkey` and `struct cache_set`; relies on `struct btree_keys_ops` being visible to includers through the bcache headers.

Risks/test signals: because the header exports only a small set of contracts, ABI drift is mostly semantic: callers must choose the correct ops table for node level. Tests should assert leaf nodes use extent ops and interior nodes use pointer ops, and that journal replay rejects invalid extents through `__bch_extent_invalid()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/bcache/extents.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/bcache/features.c -->
# sources/distributed-fs/ceph-client/drivers/md/bcache/features.c

Purpose: converts cache-set feature bits into human-readable sysfs strings. The current feature table exposes the incompatible `large_bucket` feature for log-encoded large bucket sizes.

Important APIs/functions: `bch_print_cache_set_feature_compat()`, `bch_print_cache_set_feature_ro_compat()`, and `bch_print_cache_set_feature_incompat()` each build a feature list into a caller-provided buffer. The local `feature_list` maps feature class, bit mask, and printable name. `compose_feature_string()` marks enabled features by wrapping their names in brackets.

Control flow: each print function initializes `out = buf`, invokes the macro for its feature class, and returns the byte count. The macro iterates the feature table, filters by class, tests the corresponding feature bits in `c->cache->sb`, and appends a newline if at least one feature in that class exists in the table.

State and persistence: reads persistent superblock feature fields through `cache_set->cache->sb`; it does not modify them. Output reflects only entries present in `feature_list`, so supported but unlisted bits would not print by name.

Dependencies/integration: includes `bcache_ondisk.h`, `bcache.h`, and `features.h`. These functions are intended for cache-set sysfs display paths.

Risks/test signals: `snprintf(out, buf + size - out, ...)` relies on pointer arithmetic for remaining length; tests should use small buffers and all feature classes. The feature table sentinel uses `compat == 0`, so a future compatible feature with class value zero cannot be represented without changing the sentinel scheme. Test with enabled and disabled large-bucket incompat bits and legacy superblock versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/bcache/features.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/bcache/features.h -->
# sources/distributed-fs/ceph-client/drivers/md/bcache/features.h

Purpose: defines bcache on-disk feature classes, supported feature masks, feature-bit accessors, generated per-feature helpers, unknown-feature checks, and string-printing prototypes.

Important APIs/macros: feature classes are `BCH_FEATURE_COMPAT`, `BCH_FEATURE_RO_COMPAT`, and `BCH_FEATURE_INCOMPAT`. Incompat bits include obsolete large bucket and log-encoded large bucket size. `BCH_FEATURE_*_SUPP` masks define what this implementation supports. `BCH_HAS_*_FEATURE()` tests raw superblock fields. `BCH_FEATURE_*_FUNCS()` generates `bch_has_feature_*`, `bch_set_feature_*`, and `bch_clear_feature_*`; this file instantiates helpers for `obso_large_bucket` and `large_bucket`. Unknown-feature helpers detect unsupported bits.

Control flow: generated `has` functions return false for superblocks older than `BCACHE_SB_VERSION_CDEV_WITH_FEATURES`, preserving compatibility with legacy layouts. Set/clear functions directly mutate the relevant feature field in `struct cache_sb`.

State and persistence: feature bits live in the on-disk cache superblock. These macros control mount/registration compatibility decisions and superblock mutation for feature enable/disable operations.

Dependencies/integration: includes Linux kernel/types headers and `bcache_ondisk.h`; print functions are implemented in `features.c` and used by sysfs-style reporting.

Risks/test signals: unknown incompatible features must prevent unsafe use elsewhere in registration code; this header only provides detection. The macro names concatenate `BCH##_FEATURE...`, which depends on exact token construction. Tests should cover legacy-version false returns, unknown masks for all classes, setting/clearing each known bit, and large-bucket superblock compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/bcache/features.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/bcache/io.c -->
# sources/distributed-fs/ceph-client/drivers/md/bcache/io.c

Purpose: provides low-level bcache metadata bio allocation/submission helpers and shared I/O error/congestion accounting for cache and backing devices.

Important APIs/functions: `bch_bbio_alloc()` and `bch_bbio_free()` allocate/free `struct bbio` objects from the cache-set metadata bio mempool. `bch_submit_bbio()` copies a single pointer from a key into the bbio and submits it; `__bch_submit_bbio()` submits an already-prepared bbio. `bch_count_backing_io_errors()` counts backing-device failures and ignores failed read-ahead as non-media failures. `bch_count_io_errors()` applies decayed cache-device error accounting and can fail the cache set. `bch_bbio_count_io_errors()` adds latency-based congestion tracking around cache I/O. `bch_bbio_endio()` combines accounting, `bio_put()`, and closure completion.

Control flow: metadata callers allocate an inline bio sized for metadata bucket pages, map pages, set end I/O, and call `bch_submit_bbio()` with the key pointer to target. End I/O paths typically call `bch_bbio_endio()`, which updates errors and releases the closure reference. Cache error accounting decays historical errors every `error_decay` operations by multiplying by 127/128, then adds new errors scaled by `IO_ERROR_SHIFT`.

State and persistence: tracks `bbio->key` and `submit_time_us`, cache-set congestion fields, cache `io_count`/`io_errors`, and backing-device `io_errors`. It does not persist metadata itself, but it is used by B-tree, journal, moving-GC, and request paths that do.

Dependencies/integration: depends on `bcache.h`, `bset.h`, `debug.h`, Linux block APIs, closures, mempools, and cache-set/device error handlers. `btree.c`, `journal.c`, `movinggc.c`, and `request.c` rely on these helpers for consistent metadata I/O behavior.

Risks/test signals: incorrect closure/bio ref handling can hang metadata writes or free bios early. Congestion uses signed deltas from microsecond timestamps and negative counters, so wrap and threshold behavior should be stressed. Backing read-ahead error suppression should be tested with md degraded arrays. Cache set failure thresholds, latency bypass feedback, and `REQ_OP_READ` vs write error messages are important test signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/bcache/io.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/bcache/journal.c -->
# sources/distributed-fs/ceph-client/drivers/md/bcache/journal.c

Purpose: implements bcache's journal for leaf B-tree insertions and frequently updated metadata. It reads and orders on-disk journal entries during registration, marks buckets before replay, replays keys into the B-tree, writes new journal entries, reclaims circular journal buckets, and flushes B-tree nodes that pin old journal entries.

Important APIs/functions: `bch_journal_read()` scans journal buckets, builds an ordered replay list, and initializes current/last bucket indexes. `bch_journal_mark()` pins and marks buckets referenced by replayed keys. `bch_journal_replay()` reinserts journaled keys with `bch_btree_insert()`. `bch_journal()` appends keys to the current journal write and returns a pin ref. `bch_journal_meta()` journals metadata-only state. `bch_journal_next()`, `journal_reclaim()`, `journal_wait_for_write()`, `journal_try_write()`, and `journal_write_unlocked()` drive the circular write pipeline. `btree_flush_write()` flushes dirty nodes referencing the oldest journal pin.

Control flow: recovery reads journal buckets using a golden-ratio probe, falls back to linear scan, then binary-searches and reverse-reads to find the wrapped sequence. Entries with bad magic, checksum, or size terminate bucket reading. Replay verifies no sequence gaps between `last_seq` and newest `seq`, inserts each key in order, and drops pins. Runtime insertion waits until the staged jset has room, copies keys to `cur->data`, increments the newest pin, and either schedules delayed write or forces a write for flush callers. Actual writes fill root/uuid/prio metadata, checksum the jset, issue `REQ_PREFLUSH|REQ_FUA` metadata bios, advances the journal key offset, decrements the initial sequence pin, switches buffers, and reclaims space.

State and persistence: `struct journal` stores lock state, two write buffers, sequence number, open-entry pin FIFO, current journal key, blocks remaining, and delayed work. `struct journal_device` stores per-bucket newest sequence and current/last circular indexes. On disk, `struct jset` records keys plus root, UUID bucket, prio bucket, `last_seq`, checksum, magic, and version.

Dependencies/integration: depends on B-tree insertion, extent validation, cache bucket/pointer helpers, closure workqueues, metadata bios, tracepoints, and `btree.c` dirty-node journal pins. Request insertion uses `bch_journal()` unless doing replace operations; B-tree root changes call `bch_journal_meta()`.

Risks: missing sequence detection returns `-EIO`; journal full handling depends on flushing exactly the oldest pinned nodes; `BTREE_REPLACE` is not journaled, so moving GC/writeback rely on explicit B-tree flushing before GC updates. The code comments flag oversized keylists as a deadlock risk mitigated by request keylist sizing. Test signals include crash recovery with wrapped journals, checksum corruption, missing entries, journal full under dirty leaves, metadata-only root updates, sync versus delayed writes, and concurrent reclaim/flush races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/bcache/journal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/bcache/journal.h -->
# sources/distributed-fs/ceph-client/drivers/md/bcache/journal.h

Purpose: documents and declares the journal subsystem data structures and APIs. The design comment explains the circular bucket journal, ordered key replay, superblock-like metadata in journal headers, open-entry pin FIFO, reclaim rules, and full-journal flushing strategy.

Important APIs/types: `struct journal_replay` holds variable-size jsets read during registration plus an optional pin. `struct journal_write` is one of two staged/in-flight write buffers and has a closure waitlist for synchronous callers. `struct journal` lives in `cache_set` and contains locks, flush state, delayed work, sequence number, pin FIFO, current journal pointer, and write buffers. `struct journal_device` lives in `cache` and tracks per-bucket sequence, current and last journal bucket indexes, and a reusable bio. Macros include `journal_pin_cmp()`, `journal_full()`, `JOURNAL_PIN`, and `BTREE_FLUSH_NR`.

Control flow: callers append keys through `bch_journal()` and receive an `atomic_t` pin used by B-tree dirty writes. `bch_journal_next()` advances the sequence and switches write buffers. Recovery uses `bch_journal_read()`, `bch_journal_mark()`, and `bch_journal_replay()`. Allocation/free are handled by `bch_journal_alloc()` and `bch_journal_free()`.

State and persistence: the header defines the in-memory state that protects journal persistence. The pin FIFO length determines the oldest needed sequence, which becomes `last_seq` in new journal entries and prevents circular overwrite of unreplayed changes.

Dependencies/integration: forward-declares closure, cache set, B-tree op, and keylist; relies on on-disk `struct jset`, `BKEY_PADDED`, and superblock journal bucket constants from bcache headers.

Risks/test signals: the header notes that non-journaled `BTREE_REPLACE` is fragile for incremental GC. Since refcounts are decremented without resizing locks, `JOURNAL_PIN` capacity is a correctness constraint. Tests should stress pin FIFO exhaustion, old-entry reclaim, sync flush waiters, and B-tree writes holding the oldest pin.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/bcache/journal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/bcache/movinggc.c -->
# sources/distributed-fs/ceph-client/drivers/md/bcache/movinggc.c

Purpose: implements moving/copying garbage collection. After normal GC identifies partially used buckets, this code selects the least-full movable buckets, scans matching extents, reads their data, reinserts it elsewhere with replace semantics, and frees the old references through normal B-tree update behavior.

Important APIs/functions: `bch_moving_gc()` is the main entry point called after B-tree GC. `bch_moving_init_cache_set()` initializes the moving-GC keybuf and in-flight semaphore. `moving_pred()` selects keys whose cache bucket has `GC_MOVE` set. `read_moving()` drives the scan/read/insert pipeline. `read_moving_submit()`, `read_moving_endio()`, `write_moving()`, and `write_moving_finish()` are closure stages for each moved extent.

Control flow: `bch_moving_gc()` builds a heap of non-metadata, non-full, unpinned buckets with live sectors, trims the selected set so it fits `RESERVE_MOVINGGC` capacity, marks selected buckets with `GC_MOVE`, resets the keybuf scan to zero, and calls `read_moving()`. For each matching key, `read_moving()` skips already stale pointers, allocates a `moving_io`, reads the old data at idle priority, and chains into `write_moving()`. The write stage sets `replace`, copies the original key as `replace_key`, preserves dirty and checksum flags, and calls `bch_data_insert()`. Completion logs replace collisions, deletes the keybuf entry, releases the in-flight semaphore, and frees the operation.

State and persistence: uses `cache_set->moving_gc_keys`, `moving_in_flight`, `moving_gc_wq`, bucket `GC_MOVE` flags, and normal data insertion/B-tree replacement persistence. Dirty moved extents remain dirty by setting `op->writeback` from the original key.

Dependencies/integration: depends on keybuf scanning in `btree.c`, data insertion in `request.c`, bbio helpers in `io.c`, bucket marks from GC, and tracepoints. It is invoked by `bch_btree_gc()` after bucket marks are finalized.

Risks: the source comment warns that background writeback could stall indefinitely on errors. Moving uses non-journaled replace operations, so correctness depends on collision detection and surrounding GC flush behavior. Reading clean data checks for stale pointers after I/O, but dirty data handling is more sensitive. Test signals include copy-GC enable/disable, bucket-selection reserve math, replace collisions during concurrent writes, stale pointer after read, checksum-preserving moves, dirty writeback moves, and in-flight semaphore throttling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/bcache/movinggc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/bcache/request.c -->
# sources/distributed-fs/ceph-client/drivers/md/bcache/request.c

Purpose: implements bcache's block request path for cached backing devices and flash-only cache devices. It decides bypass/writeback behavior, performs cache lookup reads, fills cache misses, writes data into the cache, journals/indexes inserted keys, submits backing I/O, handles errors, and records cache accounting.

Important APIs/functions: `cached_dev_submit_bio()` and `flash_dev_submit_bio()` are block-layer entry points. `bch_data_insert()` is the shared data-to-cache pipeline used by normal writes, read-miss fills, writeback, flash writes, and moving GC. `bch_get_congested()` returns a bypass threshold based on measured cache latency. `check_should_bypass()` applies cache mode, GC fullness, readahead policy, alignment, sequential I/O, and congestion rules. `cache_lookup()` and `cache_lookup_fn()` traverse B-tree keys and split bios into cache hits/misses. `cached_dev_cache_miss()`, `cached_dev_read()`, and `cached_dev_write()` implement backing-device flows. `bch_request_init/exit()` manage the search slab.

Control flow: a cached bio is remapped by `data_offset`, wrapped in `struct search`, then either handled as flush/no-data, read, or write. Reads perform B-tree lookup; hits submit cache bbios, misses read backing data and optionally allocate a bounce bio plus check key so the miss fill can replace only if no race occurred. Completion copies filled data into the original bio, optionally verifies against backing storage, then calls `bch_data_insert()` for the miss fill. Writes choose bypass, writeback, or writethrough. Bypass writes backing and inserts invalidation keys; writeback writes only cache and marks dirty; writethrough clones to backing and inserts clean cache data. `bch_data_insert_start()` allocates cache sectors, splits the bio into key-sized writes, writes cache data, computes checksums if requested, then `bch_data_insert_keys()` journals and inserts keys unless the op is a replace.

State and persistence: uses `struct search` for per-request lifetime and `struct data_insert_op` for cache insertion state. Persistent changes are cache data writes plus B-tree key insertions and optional journal entries. Bypass invalidation inserts zero-pointer keys. Writeback updates dirty marks and writeback queues. Cache miss fills use a random check pointer with `PTR_CHECK_DEV` to detect races.

Dependencies/integration: depends on B-tree traversal/insertion, journal, extent fixups, writeback policy, moving-GC keybuf collision checks, statistics, bbio helpers, closures, mempools, block-layer cloning/splitting, and tracepoints.

Risks: the read-miss check-key sequence is critical to avoid stale backing data overwriting fresh writes. Error recovery is allowed only for clean cache reads or cache-read races; dirty-data read failures are not recoverable. Flush/FUA handling differs between journal, backing, and writeback paths. Keylist sizing protects journal writes from oversized entries. Test signals include cache modes none/writearound/writeback/writethrough, discard handling, unaligned I/O bypass, readahead policy, sequential/congested bypass, cache read race, replace collision accounting, backing error thresholds, flush-only bios, and flash-device zero-fill misses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/bcache/request.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/bcache/request.h -->
# sources/distributed-fs/ceph-client/drivers/md/bcache/request.h

Purpose: declares the request-layer insertion operation, public submit hooks, congestion helper, and request slab symbol.

Important APIs/types: `struct data_insert_op` embeds a closure, cache set, bio, target workqueue, inode, write point, priority, status, flags, keylist, and padded replace key. Flags distinguish bypass, writeback, flush-journal, checksum, replace, replace collision, and insertion completion. `CLOSURE_CALLBACK(bch_data_insert)` is the shared cache insertion entry point. `cached_dev_submit_bio()` and `flash_dev_submit_bio()` are installed as block make-request style handlers through init functions. `bch_get_congested()` is used by bypass policy. `bch_search_cache` is the slab for `struct search` from `request.c`.

Control flow: callers initialize `data_insert_op` fields, set `bio`, `inode`, `c`, and workqueue, then call `bch_data_insert()` as a closure. Cached and flash device init functions install the appropriate cache-miss and ioctl hooks into device structs.

State and persistence: this header defines the state container that eventually writes cache data and B-tree keys. The `replace_key` member is the persistence guard for read-miss fills and moving GC replacements.

Dependencies/integration: relies on closure callbacks, Linux `bio`, `blk_status_t`, `struct keylist`, and B-tree key layout macros. It is included by moving GC and other request users.

Risks/test signals: bitfield layout is packed through a `union` with `uint16_t flags`; any new flags must fit and preserve initializer expectations. Tests should cover initialization of all public request hooks, data insertion with replace and non-replace modes, and flag combinations such as bypass plus flush journal or checksum plus writeback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/bcache/request.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/bcache/stats.c -->
# sources/distributed-fs/ceph-client/drivers/md/bcache/stats.c

Purpose: implements cache accounting and sysfs exposure for total and rolling cache hit/miss, bypass, collision, and bypassed-sector statistics.

Important APIs/functions: `bch_cache_accounting_init()` initializes kobjects, closure, and periodic timer. `bch_cache_accounting_add_kobjs()` adds `stats_total`, `stats_five_minute`, `stats_hour`, and `stats_day` under a parent kobject. `bch_cache_accounting_destroy()` removes kobjects and synchronizes timer shutdown. `bch_cache_accounting_clear()` clears totals. `bch_mark_cache_accounting()`, `bch_mark_cache_miss_collision()`, and `bch_mark_sectors_bypassed()` increment per-device and per-cache-set collectors. The sysfs `SHOW(bch_stats)` method prints counters, hit ratio, and human-readable bypassed bytes.

Control flow: request paths increment cheap atomic counters in `acc->collector`. Every `accounting_delay`, `scale_accounting()` atomically drains collectors, left-shifts values by 16, adds them into total and rolling windows, rescales five-minute/hour/day windows at configured intervals using EWMA decay, and rearms the timer unless closing. Destroy sets `closing`, deletes the timer synchronously, and returns the accounting closure if it stopped a pending timer.

State and persistence: all state is in memory under `struct cache_accounting`; no on-disk persistence. Counters are exported through sysfs kobjects and are reset on device lifecycle or explicit clear of totals. Rolling statistics use shifted fixed-point representation to reduce rounding error.

Dependencies/integration: depends on `bcache.h`, `stats.h`, `btree.h`, `sysfs.h`, kobjects, timers, atomics, closures, and request accounting calls. Both cached device and cache set accounting are updated for each relevant event.

Risks/test signals: timer shutdown and closure return ordering matter during device teardown. `scale_stats(&acc->total, 0)` relies on the preincrement comparison never matching zero, so totals do not decay; this should be intentional and tested. Concurrent sysfs reads during timer updates are not heavily synchronized. Test hit/miss/bypass accounting, five-minute/hour/day decay, clear semantics, destroy while timer pending, and byte conversion for bypassed sectors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/bcache/stats.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/bcache/stats.h -->
# sources/distributed-fs/ceph-client/drivers/md/bcache/stats.h

Purpose: defines the in-memory accounting structures and public stat update/lifecycle APIs for bcache request accounting.

Important APIs/types: `struct cache_stat_collector` is a set of atomic fast-path counters for hits, misses, bypass hits/misses, cache-miss collisions, and sectors bypassed. `struct cache_stats` is a sysfs-visible snapshot with a kobject, shifted counters, and rescale counter. `struct cache_accounting` owns a closure, timer, closing flag, collector, and four exported stat windows: total, five-minute, hour, and day. Public functions initialize, add kobjects, clear totals, destroy, and mark accounting events.

Control flow: users call `bch_cache_accounting_init()` during object setup, add the kobjects once sysfs parentage exists, mark events from request paths, and call destroy during teardown. The implementation handles periodic rollup from collector to snapshots.

State and persistence: all fields are volatile kernel memory. The structures provide observability rather than recovery-critical state.

Dependencies/integration: forward-declares `cache_set`, `cached_dev`, and `bcache_device` to avoid including the full bcache type graph. Implementation integrates with sysfs and timers in `stats.c`.

Risks/test signals: every accounting instance owns timer and kobject lifecycle, so initialization/add/destroy order must be consistent. Tests should verify per-device and aggregate cache-set updates, teardown without timer leaks, sysfs object names, and clear behavior limited to totals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/bcache/stats.h -->
