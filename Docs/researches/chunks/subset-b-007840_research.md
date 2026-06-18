# sources/distributed-fs/orangefs/src/common/lmdb/mdb.c lines 1-9097

## Purpose

This chunk is almost the complete LMDB engine implementation embedded under OrangeFS. It provides the memory-mapped, copy-on-write B+tree database core exposed by `lmdb.h`: environment creation/open/close, transaction lifecycle, MVCC reader tracking, page allocation and freelist persistence, cursor traversal, key/data lookup, insertion, deletion, sorted duplicate handling, page split/merge/rebalance logic, and the start of the environment-copy machinery.

The implementation is built around LMDB's single-writer/multiple-reader model. Readers use immutable snapshots chosen from alternating meta pages and publish their active transaction ID in a shared reader table. Writers hold the writer mutex, allocate or copy pages, persist dirty pages, save the freelist, and finally commit by publishing a new meta page with the next transaction ID. Because commit publication is only the final meta-page update, existing readers can continue using older pages until their reader slots age out of the freelist horizon.

## Important APIs, Types, and Functions

- Public environment APIs in this range include `mdb_version`, `mdb_strerror`, `mdb_env_create`, `mdb_env_open`, `mdb_env_close`, `mdb_env_sync`, `mdb_env_set_mapsize`, `mdb_env_set_maxdbs`, `mdb_env_set_maxreaders`, and `mdb_env_get_maxreaders`.
- Public transaction APIs include `mdb_txn_begin`, `mdb_txn_renew`, `mdb_txn_reset`, `mdb_txn_abort`, `mdb_txn_commit`, `mdb_txn_env`, and `mdb_txn_id`.
- Public data APIs include `mdb_get`, `mdb_put`, `mdb_del`, `mdb_cursor_open`, `mdb_cursor_renew`, `mdb_cursor_get`, `mdb_cursor_put`, `mdb_cursor_del`, `mdb_cursor_count`, `mdb_cursor_close`, `mdb_cursor_txn`, and `mdb_cursor_dbi`.
- `MDB_env` owns file descriptors, mmap pointers, meta-page pointers, lock-table mapping, DBI metadata arrays, reusable page buffers, writer transaction state, freelist IDLs, dirty-page lists, and platform mutex/semaphore handles.
- `MDB_txn` represents a read or write snapshot. It stores the transaction ID, root DB records, DBI flags, free pages, loose pages, spill pages, dirty pages, cursor lists, parent/child nested transaction linkage, and dirty-list capacity.
- `MDB_page`, `MDB_node`, `MDB_db`, and `MDB_meta` encode the on-disk format: two meta pages; branch/leaf/overflow/subpage page types; node flags for overflow data, sub-databases, and duplicate data; and per-database counts/root/depth.
- `MDB_cursor` stores a root-to-leaf page stack plus per-level indexes. `MDB_xcursor` adds a nested cursor for `MDB_DUPSORT` duplicate sets, where duplicate values are represented as keys in a subpage or sub-database.
- `mdb_page_alloc`, `mdb_page_new`, `mdb_page_touch`, `mdb_page_spill`, `mdb_page_unspill`, `mdb_page_flush`, and `mdb_page_loose` form the page ownership and copy-on-write machinery.
- `mdb_freelist_save`, `mdb_find_oldest`, `mdb_ovpage_free`, and the `FREE_DBI` cursor logic manage reclamation of pages no longer visible to active readers.
- `mdb_env_read_header`, `mdb_env_init_meta0`, `mdb_env_init_meta`, `mdb_env_write_meta`, and `mdb_env_pick_meta` implement database initialization and atomic commit metadata.
- `mdb_node_search`, `mdb_page_search`, `mdb_page_search_root`, `mdb_cursor_next`, `mdb_cursor_prev`, `mdb_cursor_set`, `mdb_cursor_first`, and `mdb_cursor_last` implement B+tree lookup and cursor navigation.
- `mdb_node_add`, `mdb_node_del`, `mdb_node_shrink`, `mdb_update_key`, `mdb_page_split`, `mdb_node_move`, `mdb_page_merge`, `mdb_rebalance`, and `mdb_cursor_del0` maintain page layout and B+tree invariants during mutation.
- `mdb_env_copythr` and `mdb_copy` begin the compacting-copy path; the helper that feeds this writer thread starts after the requested line range.

## Control Flow

Environment setup starts with `mdb_env_create`, which allocates an `MDB_env`, sets default reader and DB counts, records the process ID and OS page size, and initializes file handles. `mdb_env_open` validates flags, builds data and lock file names, allocates DBI arrays and write-side IDLs for writable environments, sets up locks unless `MDB_NOLOCK`, opens the data file, calls `mdb_env_open2`, opens a synchronous meta fd for non-writemap writable environments, downgrades any exclusive lock to shared, and preallocates the reusable top-level write transaction.

`mdb_env_open2` either reads and validates both meta pages or initializes an empty environment. It computes page size, mapsize, max page number, node-size limits, and mmap pointers to both meta pages. On Linux builds where `fdatasync` may be unreliable on older ext filesystems, it detects the filesystem/kernel combination and sets `MDB_FSYNCONLY` to force full `fsync`.

Transaction start flows through `mdb_txn_begin` and `mdb_txn_renew0`. Read transactions either choose the newest meta directly when there is no lock table, or claim/reuse a reader slot and copy the lock table transaction ID into the transaction snapshot. Write transactions acquire `me_wmutex`, increment the previous transaction ID, initialize dirty/free/spill state from the environment, and copy the two core DB records from the selected meta page. Nested write transactions allocate independent dirty/free lists, copy the parent's DB records, save the environment page-reclaim state, and shadow parent cursors so cursor fixups can still track page movements.

Reads use a cursor initialized for the target DBI. `mdb_page_search` refreshes stale named-DB roots through the main DB when needed, loads the root page, and descends branch pages through `mdb_page_search_root`, using `mdb_node_search` binary search on each page. `mdb_get` is a thin wrapper over `mdb_cursor_set`, while `mdb_cursor_get` dispatches the full cursor operation set: current, exact/range set, first/last, next/previous, duplicate navigation, and fixed-duplicate multi-value batch reads.

Writes call `mdb_put` or `mdb_cursor_put`. They reject readonly or blocked transactions, enforce key/data size limits, position the cursor, optionally spill dirty pages, touch the cursor stack so every page on the write path is private to the transaction, then insert, replace, or split as needed. Large data values become overflow pages. `MDB_DUPSORT` records either stay inline as duplicate subpages or convert to full duplicate sub-databases once they no longer fit in a single node.

Deletes use `mdb_del0` to position a temporary tracked cursor, then `mdb_cursor_del`. Duplicate-aware deletion can remove one duplicate, all duplicates for a key, or a whole sub-database. Overflow pages are returned through `mdb_ovpage_free`; the leaf node is removed by `mdb_cursor_del0`; then `mdb_rebalance` borrows from a sibling, merges pages, collapses a one-child root, or marks the DB empty.

Commit of a top-level writer is ordered carefully. `mdb_txn_commit` writes dirty named-DB records back into the main DB, saves the current freelist into `FREE_DBI`, flushes dirty pages to the map/file, syncs according to environment flags, and finally calls `mdb_env_write_meta`. The meta writer alternates between the two meta pages using `txnid & 1`; only after database roots, freelist root, last page, mapsize, and flags are prepared does it publish `mm_txnid`. Transaction end then releases cursors, dirty pages, free-page buffers, reader slots, DBI name state, and writer locks.

## State and Persistence Behavior

The durable database state is the mmap-backed data file. Pages 0 and 1 are meta pages; all other pages are branch, leaf, overflow, or freeDB pages reachable from the current meta snapshot. The newest valid meta page is chosen by highest `mm_txnid`, and a writer publishes a transaction by updating the alternate meta page. This provides crash resilience as long as at least one meta page remains valid.

Read state is mostly outside the B+tree. The lock file maps an `MDB_txninfo` header followed by cacheline-aligned `MDB_reader` slots. Readers write their PID, thread ID, and transaction ID into a slot, optionally cached in thread-specific storage. Writers scan this table with `mdb_find_oldest` to determine which freeDB records are old enough to reclaim.

Write state is transaction-local until commit. Non-`MDB_WRITEMAP` writers allocate private dirty page copies and store them in a sorted `MDB_ID2L`; `MDB_WRITEMAP` writers modify mmap pages directly but still track dirty pages and rely on meta publication for visibility. `mt_free_pgs` records pages freed in the current transaction, `me_pghead` caches reclaimed pages read from older freeDB records, `mt_loose_pgs` allows immediate reuse of single pages dirtied and freed in the same transaction, and `mt_spill_pgs` records dirty pages temporarily flushed before commit to avoid `MDB_TXN_FULL`.

The freelist itself is persistent data in `FREE_DBI`, keyed by transaction ID and storing an IDL of pages freed by that transaction. `mdb_page_alloc` consumes old enough freeDB records by merging their IDLs into `me_pghead`, preferring contiguous ranges large enough for overflow allocations. `mdb_freelist_save` deletes consumed freeDB records, writes pages freed by the current transaction under the current transaction ID, and reserves records for any still-cached reusable pages so the allocator state remains stable across commit.

Named DB state is split between in-memory DBI arrays and persisted `MDB_db` records stored in the main DB. DBI handles have sequence numbers to detect closed or recreated handles. Stale named DB roots are lazily refreshed from the main DB, and dirty named DB records are written during commit before the freelist and meta page.

## Dependencies and Integration Points

- `lmdb.h` supplies the public API types, flags, cursor operations, error codes, and function declarations consumed by OrangeFS callers.
- `midl.h` supplies ID list and ID-to-pointer-list primitives such as `mdb_midl_alloc`, `mdb_midl_need`, `mdb_midl_append`, `mdb_midl_append_range`, `mdb_midl_xmerge`, `mdb_midl_sort`, `mdb_mid2l_search`, and `mdb_mid2l_insert`.
- The code depends directly on platform mmap/file APIs: `mmap`, `munmap`, `pread`, `pwrite`, `writev`, `fsync`/`fdatasync`, `fcntl` locks, `ftruncate`, POSIX threads, POSIX semaphores, and Windows file mapping, mutex, TLS, and overlapped I/O equivalents.
- Shared lock behavior is selected at compile time among Windows mutexes, POSIX semaphores, and process-shared POSIX mutexes. Robust mutex support can recover reader or writer locks after owner death through `mdb_mutex_failed`, which appears later in the file.
- Optional Valgrind hooks mark the custom page reuse pool as a mempool, helping memory-checking tools understand page allocation and reuse.
- Environment-copy support in this chunk sets up the `mdb_copy` structure and writer thread. The traversal and public copy entry points continue after line 9097.
- OrangeFS integrates this as a bundled third-party storage component under `src/common/lmdb`; local build choices for platform macros, sync flags, and lock implementation materially affect behavior.

## Risks and Edge Cases

- Commit correctness depends on the precise ordering of page writes, syncs, and meta-page publication. `MDB_NOSYNC`, `MDB_NOMETASYNC`, `MDB_MAPASYNC`, and `MDB_WRITEMAP` intentionally relax parts of that sequence and must be treated as durability tradeoffs.
- `mdb_env_write_meta` marks `MDB_FATAL_ERROR` if meta writing fails after page data may already be in the OS cache. Future transaction starts return `MDB_PANIC`, so callers must close/reopen or rebuild rather than continuing.
- The reader table is deliberately scanned without taking reader-slot locks. This is safe for reclaim conservatism but means stale reader slots from dead processes can pin free pages until `mdb_reader_check` later cleans them.
- `MDB_NOLOCK` and readonly-on-readonly-filesystem operation skip the lock table, which removes cross-process reader tracking. Those modes rely on external discipline and are unsafe with concurrent writers.
- The allocator has several intertwined sources of pages: loose pages, reclaimed freeDB records, spilled dirty pages, and new map pages. Bugs in `me_pghead`, `me_pglast`, or freeDB record reservation could cause page leaks, double allocation, or freelist self-growth loops.
- Dirty-page spilling is an optimization, not a full solution for all large transactions. The comments note `MDB_TXN_FULL` can still happen when estimates are low or nested transactions inherit a nearly full dirty list.
- Nested write transactions are not supported with `MDB_WRITEMAP` and require careful dirty/spill merging. Failure while appending a child's spill list to a parent can mark the parent transaction erroneous.
- Cursor fixups after `mdb_page_touch`, `mdb_cursor_put`, `mdb_node_move`, `mdb_page_merge`, `mdb_rebalance`, and `mdb_page_split` are complex. Any new mutation path that misses tracked cursor updates can leave active cursors pointing at moved pages, stale subpages, or wrong indexes.
- `MDB_DUPSORT` is a major complexity source. A duplicate set can transition from a single data item to a subpage and then to a sub-database; `MDB_DUPFIXED` uses `P_LEAF2` packed keys; duplicate values are constrained by max key size because they are stored as sub-DB keys.
- Large data is stored in contiguous overflow pages. Replacing overflow data tries to reuse dirty overflow pages when possible, but can free and reallocate when the new value no longer fits. Multi-page allocation depends on finding contiguous free ranges.
- Key and value size checks are strict. Integer-key comparators assume fixed sizes and alignment properties; branch-page comparator shortcuts rely on keys being stored in compatible formats.
- `mdb_env_set_mapsize` can remap an open environment only when no write transaction is active. Other processes may still grow the database beyond a reader's mapsize, yielding `MDB_MAP_RESIZED`.
- `mdb_env_open2`'s broken-`fdatasync` detection is platform-specific and dated. Build environments that define or omit `MDB_FDATASYNC_WORKS` change durability behavior.
- The compact-copy thread in this range treats `mc_error` as an atomically writable `int` without mutex protection, matching LMDB assumptions but still depending on platform-level atomicity for normal int stores.

## Test Signals

- Environment open should create two valid meta pages for a new database, map both meta pointers correctly, reject bad magic/version data, and preserve configured mapsize when reopening.
- Opening with and without `MDB_NOLOCK`, `MDB_RDONLY`, `MDB_WRITEMAP`, `MDB_NOSUBDIR`, and `MDB_FIXEDMAP` should exercise the filename, lock setup, mapping, and meta-fd branches.
- Reader tests should cover TLS reader slot reuse, `MDB_NOTLS` owned slots, reader slot exhaustion (`MDB_READERS_FULL`), stale process cleanup in later reader-check code, and readonly environments with no lock table.
- Transaction tests should verify read snapshot stability across a concurrent writer commit, single-writer exclusion, abort cleanup, reset/renew of readonly transactions, nested writer commit/abort, and parent transaction blocking while a child exists.
- Freelist tests should insert and delete enough data to create freeDB records, verify old pages are not reused while an old reader is active, and verify reuse after the reader ends.
- Dirty-list pressure tests should force page spilling and then read/write spilled pages so both `mdb_page_spill` and `mdb_page_unspill` paths are exercised.
- Basic cursor tests should cover exact lookup, range lookup, first/last, next/previous across sibling pages, EOF handling, current item retrieval, and cursor renewal.
- Mutation tests should cover root creation, sequential `MDB_APPEND`, duplicate-key rejection with `MDB_NOOVERWRITE`, same-size overwrite, smaller/larger replacement, overflow value creation/replacement/freeing, and map-full/transaction-full errors.
- B+tree shape tests should force leaf splits, branch splits, root splits, sibling borrowing, page merges, root collapse, and complete DB emptying after deletes.
- Duplicate tests should cover single value to duplicate-subpage conversion, subpage to sub-DB conversion, `MDB_DUPFIXED`/`P_LEAF2` packed duplicates, `MDB_MULTIPLE`, `MDB_APPENDDUP`, `MDB_NODUPDATA`, duplicate count, and deletion of one duplicate versus all duplicates.
- Named DB tests should cover `mdb_env_set_maxdbs`, named DB creation/opening in later code, stale DBI refresh through the main DB, DBI sequence mismatch (`MDB_BAD_DBI`), and incompatible flag changes (`MDB_INCOMPATIBLE`).
- Durability tests should compare normal sync, `MDB_NOMETASYNC`, `MDB_NOSYNC`, `MDB_MAPASYNC`, and `MDB_WRITEMAP` behavior under simulated crashes or injected write failures, with particular attention to meta-page selection after restart.
- Cursor-stability tests should keep multiple cursors open during inserts, deletes, splits, merges, and duplicate conversions, then assert each cursor's key/data and traversal behavior remain coherent.
- Copy-thread tests for this chunk should force partial writes, zero-length writes, write errors, SIGPIPE/EPIPE on POSIX, and final EOF handoff once the later copy traversal code is included.
