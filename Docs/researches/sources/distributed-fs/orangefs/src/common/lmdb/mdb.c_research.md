# Research: sources/distributed-fs/orangefs/src/common/lmdb/mdb.c

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-007840`: lines 1-9097, `Docs/researches/chunks/subset-b-007840_research.md`
- `subset-b-007841`: lines 9098-10257, `Docs/researches/chunks/subset-b-007841_research.md`

## Chunk Research

### subset-b-007840: lines 1-9097

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

### subset-b-007841: lines 9098-10257

# sources/distributed-fs/orangefs/src/common/lmdb/mdb.c lines 9098-10257

## Purpose

This chunk implements the tail of LMDB's environment copy machinery and a set of public maintenance/query APIs around environments, database handles, custom comparators, database dropping, and reader-lock cleanup. It starts at `mdb_env_cthr_toggle`, the producer-side synchronization helper used by compacting copy, then walks through compact and non-compact environment copy paths. The copy APIs are the durable backup/export surface for an opened LMDB environment: the default path copies the snapshot byte-for-byte, while the compact path rewrites reachable pages into a dense page-number sequence and rebuilds the output meta pages.

The middle of the chunk exposes lightweight environment metadata accessors (`mdb_env_get_flags`, `mdb_env_stat`, `mdb_env_info`, path/fd/user-context/assertion accessors), database-handle lifecycle (`mdb_dbi_open`, `mdb_dbi_close`, `mdb_dbi_flags`), database statistics (`mdb_stat`), and the drop/delete implementation (`mdb_drop0`, `mdb_drop`). These functions bridge LMDB's public API to the internal B+tree, meta-page, transaction, DBI table, and cursor representations.

The final block handles reader table diagnostics and cleanup. `mdb_reader_list` reports live reader slots from the lock file. `mdb_reader_check` and `mdb_reader_check0` detect dead process IDs in reader slots and clear them under the reader mutex. When robust mutexes are available, `mdb_mutex_failed` repairs mutex state after an owner dies and updates transaction metadata so later writers do not overwrite pages still referenced by the latest meta page. On Windows builds, the chunk ends with `utf8_to_utf16`, a path-conversion helper used by filename/opening code.

## Important APIs, Types, and Functions

- `mdb_env_cthr_toggle(mdb_copy *my, int adjust)` is the copy producer's synchronization primitive. It increments `mc_new` by `adjust`, signals the writer thread, waits while both copy buffers are outstanding, flips `mc_toggle` when handing off a buffer, resets the newly selected buffer length, and returns any sticky copy error.
- `mdb_env_cwalk(mdb_copy *my, pgno_t *pg, int flags)` performs a depth-first traversal of a database tree for `MDB_CP_COMPACT`. It rewrites branch, leaf, overflow, and nested subdatabase references into sequential output page numbers, streams pages through double buffers, and updates the root page number through the `pg` pointer.
- `mdb_env_copyfd1(MDB_env *env, HANDLE fd)` performs compacting copy to an already opened file descriptor. It initializes mutex/condition state, allocates two aligned `MDB_WBUF` buffers, starts `mdb_env_copythr`, opens a read-only transaction, writes fresh meta pages, calculates the compacted final page/root number, walks the main DB tree, signals EOF to the writer thread, joins it, and frees resources.
- `mdb_env_copyfd0(MDB_env *env, HANDLE fd)` performs a snapshot copy without compaction. It starts a read-only transaction, optionally blocks writers long enough to renew the read transaction and copy stable meta pages, writes the meta pages and then the mapped data pages up to the transaction's `mt_next_pgno` or actual file size, and aborts the read transaction.
- `mdb_env_copyfd2`, `mdb_env_copyfd`, `mdb_env_copy2`, and `mdb_env_copy` are the public wrapper stack. `MDB_CP_COMPACT` selects the compacting path; path-based copy opens an exclusive copy target via `mdb_fname_init` and `mdb_fopen`.
- `mdb_env_set_flags`, `mdb_env_get_flags`, `mdb_env_set_userctx`, `mdb_env_get_userctx`, `mdb_env_set_assert`, `mdb_env_get_path`, and `mdb_env_get_fd` are simple environment accessors/mutators. `mdb_env_set_flags` accepts only `CHANGEABLE` flags; `mdb_env_get_flags` reports changeable and changeless runtime flags.
- `mdb_stat0`, `mdb_env_stat`, `mdb_env_info`, and `mdb_stat` expose page size, B+tree depth, branch/leaf/overflow page counts, entry count, map address, last page number, last transaction id, map size, max readers, and active reader count. `mdb_stat` refreshes stale DBI state through cursor initialization when needed.
- `mdb_default_cmp(MDB_txn *txn, MDB_dbi dbi)` installs default key and duplicate-data comparison functions based on persistent DB flags such as `MDB_REVERSEKEY`, `MDB_INTEGERKEY`, `MDB_DUPSORT`, `MDB_INTEGERDUP`, `MDB_DUPFIXED`, and `MDB_REVERSEDUP`.
- `mdb_dbi_open(MDB_txn *txn, const char *name, unsigned int flags, MDB_dbi *dbi)` opens or creates a database handle. The main DB is handled specially; named DBs are looked up as `F_SUBDATA` records in the main DB, registered in an available DBI slot, given a duplicated name string, assigned sequence metadata, and configured with default comparators.
- `mdb_dbi_close(MDB_env *env, MDB_dbi dbi)` releases a named database handle slot by freeing the stored name, clearing flags, and incrementing its DBI sequence. It does not close core DBIs.
- `mdb_dbi_flags(MDB_txn *txn, MDB_dbi dbi, unsigned int *flags)` returns persistent database flags for an open user-visible DBI.
- `mdb_drop0(MDB_cursor *mc, int subs)` recursively adds a database's pages to the current write transaction's free list. It scans overflow pages and optional subdatabases from leaves, appends child branch page numbers, appends the DB root, and marks the transaction erroneous on failure.
- `mdb_drop(MDB_txn *txn, MDB_dbi dbi, int del)` is the public empty/delete operation. It validates write access and DBI freshness, opens a cursor, calls `mdb_drop0`, invalidates live cursors on that DBI, either removes the named DB record from the main DB or resets the DB's in-transaction `MDB_db` counters/root, then closes the cursor.
- `mdb_set_compare`, `mdb_set_dupsort`, `mdb_set_relfunc`, and `mdb_set_relctx` install application callbacks/context into the transaction's `MDB_dbx` slot after DBI validation.
- `mdb_env_get_maxkeysize(MDB_env *env)` returns `ENV_MAXKEY(env)`, respecting build-time or environment-dependent max-key sizing.
- `mdb_reader_list(MDB_env *env, MDB_msg_func *func, void *ctx)` emits formatted reader-lock rows through a caller callback, including PID, thread id, and transaction id, or a no-lock/no-active-readers message.
- `mdb_pid_insert(MDB_PID_T *ids, MDB_PID_T pid)` maintains a sorted process-id array and suppresses duplicate PID checks during stale-reader scanning.
- `mdb_reader_check(MDB_env *env, int *dead)` and `mdb_reader_check0(MDB_env *env, int rlocked, int *dead)` clear stale reader slots whose owning process no longer exists. They use `mdb_reader_pid(env, Pidcheck, pid)` and, when needed, lock `me_rmutex` before modifying shared reader slots.
- `mdb_mutex_failed(MDB_env *env, mdb_mutexref_t mutex, int rc)` is compiled under `MDB_ROBUST_SUPPORTED`. It handles `MDB_OWNERDEAD`, updates `mti_txnid` for dead writer mutex owners, marks this process's environment fatal if its own write transaction died, clears stale readers, calls `mdb_mutex_consistent`, and unlocks on unrecoverable failure.
- `utf8_to_utf16(const char *src, MDB_name *dst, int xtra)` is a Windows-only helper that allocates and fills a wide-character path buffer with optional extra capacity.

The central types visible or consumed here are `MDB_env`, `MDB_txn`, `MDB_cursor`, `MDB_xcursor`, `MDB_db`, `MDB_dbx`, `MDB_meta`, `MDB_page`, `MDB_node`, `MDB_stat`, `MDB_envinfo`, `MDB_reader`, `MDB_txninfo`, `MDB_PID_T`, and the local `mdb_copy` control object defined immediately before this chunk.

## Control Flow

Compacting copy is a two-thread pipeline. The producer, `mdb_env_copyfd1`, allocates two write buffers and starts `mdb_env_copythr` before opening a read-only transaction. It initializes output meta page 0 and meta page 1 in buffer 0, using `mdb_env_init_meta0` and the current environment fixed-map address. It then sets meta page 1 to transaction id 1 when there is either a non-empty main DB or persistent main-DB flags. For non-empty DBs, it counts freeDB entries and freeDB's own pages to predict the compacted last page number. That predicted number becomes both `mm_last_pg` and the temporary main DB root in the output meta. `my.mc_next_pgno` starts at `NUM_METAS`, so all copied data pages are assigned after the two meta pages.

`mdb_env_cwalk` performs the actual compacting traversal. It initializes a cursor at the source root, descends to the first leaf with `mdb_page_search_root(..., MDB_PS_FIRST)`, and creates writable copies of the cursor's branch stack. For each leaf page, it may also copy the leaf into a scratch page before mutating node payloads. Big-data nodes (`F_BIGDATA`) contain an overflow page number in their data payload; compacting copy replaces that payload with `mc_next_pgno`, copies the overflow page header into the output buffer with a rewritten page number, advances `mc_next_pgno` by the overflow span, and arranges for any overflow tail pages to be written directly by the writer thread. Subdatabase nodes (`F_SUBDATA`) contain an embedded `MDB_db`; compacting copy recurses into that `MDB_db.md_root`, then writes the updated DB record back into the copied leaf node. `F_DUPDATA` suppresses full sub-DB scanning for sorted-duplicate subdatabases where the tree shape is handled differently.

For branch traversal, `mdb_env_cwalk` increments the current branch index and descends into child pages. When a sibling branch is entered, it keeps descending to that branch's first leaf so pages are emitted depth-first. After writing a leaf or branch page to the current buffer, it rewrites the parent node's child page number to the new output page number and pops back up. When the root is written, `*pg` receives the new root page number and traversal ends. Any mismatch between the walked root and `mdb_env_copyfd1`'s predicted `new_root` is treated as `MDB_INCOMPATIBLE`, indicating a leak or corrupt reachability/accounting relationship.

The copy thread protocol is intentionally simple. `mdb_env_cthr_toggle` signals when the producer has filled a buffer, and the writer thread consumes buffers in alternating order. `mc_new` encodes the count of full buffers and may carry `MDB_EOF` on shutdown. The producer waits when `mc_new & 2` is true, meaning both buffers are in use. The writer drains `mc_wlen[toggle]`, then optional `mc_olen[toggle]` overflow tail bytes, clears the buffer length, flips its local toggle, decrements `mc_new`, and signals the producer. `mc_error` is sticky and can be set by either side.

The non-compacting copy path is a snapshot write. `mdb_env_copyfd0` begins a read-only transaction. If the environment has a lock table, it resets the temporary reader transaction, locks the writer mutex, renews the read transaction, writes the meta pages while writers are blocked, and then releases the writer mutex. This prevents the copied meta pages from racing with a writer while still avoiding a long writer lock during the bulk data write. The bulk copy writes from `env->me_map` after the two meta pages through `txn->mt_next_pgno * me_psize`, capped by `mdb_fsize(env->me_fd)` to avoid copying beyond the backing file. Short successful writes advance the pointer until complete; zero-length or failed writes become `EIO` or the platform error.

`mdb_dbi_open` first validates flags and transaction state. Opening the main DB (`name == NULL`) returns `MAIN_DBI`, may OR new persistent flags into `mt_dbs[MAIN_DBI].md_flags`, marks the transaction dirty if those flags changed, and installs default comparators. For named DBs, it ensures the main DB comparator is initialized, scans existing DBI slots for a matching name or free slot, enforces `me_maxdbs`, and rejects named databases when the main DB is configured as `MDB_DUPSORT` or `MDB_INTEGERKEY`. It then searches the main DB for a record named by `name`; if found, the record must be a subdatabase node. If not found and `MDB_CREATE` is set, it inserts a zeroed `MDB_db` record with `md_root = P_INVALID` and persistent flags. Only after successfully duplicating the name does creation proceed, so most allocation failures occur before persistent mutation. On success, the DBI slot records the name, relation callback state, DB validity flags, DBI sequence number, copied `MDB_db` contents, and default comparator functions.

`mdb_drop` funnels destructive work through cursor state. It refuses invalid `del` values, read-only transactions, and stale DBIs. After opening a cursor, `mdb_drop0` searches to the first page and frees reachable pages into `txn->mt_free_pgs`. The helper can avoid scanning leaf pages when duplicates or overflow/subdatabase checks are irrelevant. When it does scan leaves, it appends overflow page ranges for `F_BIGDATA` nodes and recursively drops nested subdatabases for `F_SUBDATA` nodes when requested. Branch pages contribute all child page numbers. At the end, the root page is appended. The public wrapper then invalidates all cursors for the DBI. With `del == 1` on named DBs, it deletes the subdatabase record from the main DB with `mdb_del0`, marks the DBI stale, and closes the environment handle slot. Otherwise, it resets the DB's counters and root to an empty state and marks the DBI and transaction dirty.

Reader cleanup starts without mutating anything. `mdb_reader_check0` snapshots `mti_numreaders`, allocates a temporary sorted PID list, and scans reader slots. It ignores empty slots and this process's PID, and checks each distinct external PID only once. If the PID is dead, the function locks `me_rmutex` unless the caller already owns it, rechecks the PID to reduce PID-reuse races, then clears every reader slot with that PID and counts each cleared slot. The robust mutex recovery path can call it with `rlocked` set when recovering the reader mutex itself.

## State and Persistence Behavior

The copy APIs are read-only with respect to the source environment. Their persistent output is an LMDB data file written to a caller-supplied descriptor or newly opened copy path; no lock file is copied because LMDB recreates it as needed. The compacting copy path does not preserve original page numbers. It emits two fresh meta pages, rewrites every reachable page to a dense sequence, changes branch child pointers, overflow payload pointers, nested `MDB_db.md_root` values, and the output meta's main DB root/last-page fields. Free pages are intentionally omitted. The non-compacting path preserves source page layout for pages in the selected snapshot, including free pages up to the copied end.

`mdb_env_copyfd1` uses a read-only transaction snapshot, so the main tree, freeDB accounting, and meta values are internally consistent for that transaction. It relies on freeDB counts plus current DB stats to predict the compacted last page. If the traversal reaches a root page number different from the predicted `new_root`, it reports `MDB_INCOMPATIBLE` rather than producing a silently inconsistent compacted copy. Empty DBs are handled specially: persistent main-DB flags can still cause meta page 1 to be used, but root walking is skipped for `P_INVALID`.

Environment flags and user context are in-memory fields on `MDB_env`; this chunk's setters do not themselves persist flags to disk. Database flags inside `MDB_db` records are persistent when committed as part of a write transaction. `mdb_dbi_open` can mark a transaction dirty by changing main-DB persistent flags or by inserting a named subdatabase record. `mdb_dbi_close` only releases local handle metadata and increments the handle sequence; it does not delete the on-disk subdatabase.

`mdb_drop0` and `mdb_drop` mutate only the active write transaction's state until commit. Pages are appended to `txn->mt_free_pgs`, database counters/root are reset in `txn->mt_dbs`, named DB records may be deleted from the main DB, and dirty flags are set. Durability and actual freeDB persistence happen later through transaction commit code outside this chunk. On errors while collecting pages, `MDB_TXN_ERROR` is set so the transaction must abort.

Reader table state lives in the lock-file mapping (`env->me_txns`). `mdb_reader_list` only observes it. `mdb_reader_check0` clears stale `mr_pid` fields in shared reader slots so old read transactions no longer pin pages. Robust mutex recovery can also update `env->me_txns->mti_txnid` from the latest meta page after a dead writer mutex owner; this is persistence-adjacent state because it prevents the next writer from basing allocation decisions on stale transaction ids.

## Dependencies and Integration Points

- Public declarations and API contracts for copy, stat, DBI, comparator, drop, and reader functions are in `sources/distributed-fs/orangefs/src/common/lmdb/lmdb.h`.
- Copy paths depend on lower-level environment and OS helpers from earlier in `mdb.c`: `mdb_fname_init`, `mdb_fopen`, `mdb_fsize`, `mdb_env_init_meta0`, `mdb_env_pick_meta`, platform `HANDLE`/`close`, and write abstractions.
- Compacting copy depends on cursor/page primitives: `mdb_page_get`, `mdb_page_search_root`, `mdb_page_copy`, `mdb_cursor_pop`, `NODEPTR`, `NODEDATA`, `NODEPGNO`, `SETPGNO`, page type predicates, and overflow-page metadata.
- DBI open/drop/stat operations depend on transaction and cursor machinery: `mdb_txn_begin`, `mdb_txn_abort`, `mdb_txn_end`, `mdb_txn_renew0`, `mdb_cursor_init`, `mdb_cursor_open`, `mdb_cursor_close`, `mdb_cursor_set`, `mdb_cursor_put`, `mdb_cursor_get`, `mdb_cursor_sibling`, `mdb_del0`, and xcursor initialization for nested subdatabases.
- Free-page accounting uses `MDB_IDL` helpers such as `mdb_midl_need`, `mdb_midl_append`, `mdb_midl_append_range`, and `mdb_midl_xappend`.
- Comparator setup selects internal comparison functions (`mdb_cmp_memn`, `mdb_cmp_memnr`, `mdb_cmp_int`, `mdb_cmp_cint`) that are later used by search, insert, delete, and cursor operations.
- Reader cleanup depends on platform-specific process liveness checks through `mdb_reader_pid(env, Pidcheck, pid)`, lock macros (`LOCK_MUTEX`, `LOCK_MUTEX0`, `UNLOCK_MUTEX`), robust mutex support, and `mdb_mutex_consistent`.
- Threading integration is abstracted by `THREAD_CREATE`, `THREAD_FINISH`, pthread mutex/condition primitives on POSIX, and Windows mutex/event/aligned allocation equivalents behind the same field names/macros in this OrangeFS LMDB vendored source.
- OrangeFS integrates this vendored LMDB implementation as `src/common/lmdb`; callers elsewhere in OrangeFS use the standard LMDB API surface rather than these static helpers directly.

## Risks and Edge Cases

- `mdb_env_cthr_toggle` relies on `mc_new` bit patterns: `MDB_EOF` is ORed into the same integer that tracks buffer count. Any future change to buffer-count values or EOF bits must preserve the writer thread's `mc_new == 0 + MDB_EOF` exit condition and the producer's `mc_new & 2` full-buffer wait.
- `mc_error` is intentionally a volatile int shared without mutex protection. That matches LMDB's compact copy design, but it assumes atomic-enough integer reads/writes on supported platforms and can still expose ordering subtleties around concurrent error observation.
- Compacting copy mutates copied page images while traversing source pages. It carefully switches to writable branch/leaf copies before rewriting page numbers; missing one of those copies would corrupt the source map under `MDB_WRITEMAP`-style assumptions or write into read-only mappings.
- Overflow handling writes the first overflow page header through the normal buffer but points `mc_over[toggle]` at the original mapped overflow tail. The writer must finish that tail before the read transaction is aborted and before the buffer slot is reused.
- `mdb_env_copyfd1` allocates only `me_psize * mc_snum` bytes for copied cursor pages plus one extra page-sized leaf scratch through the same allocation expression. The code relies on `mc_snum`/`mc_top` values after `mdb_page_search_root`; cursor stack depth and scratch use must remain within that allocated size.
- `mdb_env_copyfd0` can copy a large snapshot while a read-only transaction is open. As documented in `lmdb.h`, concurrent writers may grow the source file because the backup reader pins old pages until the copy completes.
- The non-compact path writes meta pages while holding the writer mutex but writes the rest after unlocking. That is correct for snapshot copy because the read transaction pins reachable pages, but the source file may still grow; the `mdb_fsize` cap prevents copying beyond actual file size if `mt_next_pgno` races with file truncation/extension behavior.
- `mdb_dbi_open` returns existing DBI slots without checking requested flags against already-open flags. This matches LMDB handle semantics, but callers should not expect a later `mdb_dbi_open` with different flags to reconfigure an existing handle.
- Named DB creation inserts an `F_SUBDATA` record into the main DB. After this point, failures can leave the write transaction in a dirty/error state that must be aborted; callers should not continue using a transaction after `MDB_TXN_ERROR`.
- `mdb_dbi_close` is not mutex-protected and invalidates the name pointer for future users. `lmdb.h` warns that closing handles while other threads or active transactions may reference them can cause bad DBI behavior or data corruption.
- `mdb_drop0` optimizes away leaf scanning when overflow/subdatabase checks are unnecessary. Any future page type or node flag that adds external page ownership must update this skip logic or dropped databases could leak pages.
- Dropping nested subdatabases uses xcursor state from the current leaf node. Incorrect `subs` propagation would either miss subdatabase pages or attempt to scan duplicate-data subtrees as full DBs.
- `mdb_drop` invalidates cursors by clearing `C_INITIALIZED|C_EOF`, but existing cursor objects still exist. Callers that keep using them after drop must expect reinitialization or errors.
- `mdb_reader_check0` has an unavoidable PID reuse race. It rechecks after taking the reader mutex, but a dead PID reused by a new process around the check could cause conservative non-cleanup or, in a narrower race, clearing a slot that appears to belong to a dead owner.
- Robust mutex recovery marks `MDB_FATAL_ERROR` and returns `MDB_PANIC` if a dead writer mutex owner was this process's own active write transaction. This protects file consistency but leaves the environment handle unusable for further normal writes.
- `utf8_to_utf16` allocates based on a first `MultiByteToWideChar` sizing pass and marks `MDB_name` as allocated. Callers must pair successful conversion with the normal `MDB_name` cleanup path.

## Test Signals

- `mdb_env_copyfd2(env, fd, 0)` should produce a byte-for-byte snapshot with valid meta pages and data pages through the transaction's visible end; injected short writes should be retried until complete, while zero-length writes should return `EIO`.
- `mdb_env_copyfd2(env, fd, MDB_CP_COMPACT)` should produce a readable environment whose `mm_last_pg` is smaller when free pages existed, whose main root equals the final compacted root, and whose data still matches source contents across regular, overflow, named-subdatabase, and sorted-duplicate records.
- A compacting copy of an empty DB should succeed, write valid meta pages, and avoid false `MDB_INCOMPATIBLE` failures. A deliberately inconsistent/free-page-leaking source image should hit the `root != new_root` check and return `MDB_INCOMPATIBLE`.
- Copy-to-path wrappers should fail if the destination already exists or cannot be opened, close the descriptor on success/failure, and propagate close errors only when the copy itself succeeded.
- `mdb_env_set_flags` should reject flags outside `CHANGEABLE`; `mdb_env_get_flags`, `mdb_env_get_path`, `mdb_env_get_fd`, and user-context accessors should return `EINVAL` for null required pointers where implemented.
- `mdb_env_stat` and `mdb_env_info` should reflect the currently selected meta page, including map address, last page, last transaction id, map size, max readers, and reader count.
- `mdb_dbi_open(NULL name)` should return `MAIN_DBI`, initialize default comparators, and mark the transaction dirty when persistent main DB flags are newly added.
- Named `mdb_dbi_open` tests should cover existing DB reuse, free slot reuse after `mdb_dbi_close`, `MDB_DBS_FULL`, incompatible main DB flags, creation with `MDB_CREATE`, `strdup` failure, and rejection of a main-DB record that exists but is not an `F_SUBDATA` node.
- Comparator tests should verify default key/data comparator selection for reverse keys, integer keys, sorted duplicates, fixed integer duplicates, and reverse duplicate sorting; custom comparator setters should take effect before data access.
- `mdb_stat` should refresh a `DB_STALE` DBI through cursor initialization and then return updated counts. Blocked transactions should return `MDB_BAD_TXN`.
- `mdb_drop(txn, dbi, 0)` should empty the DB, append all owned pages to `mt_free_pgs`, reset depth/page/entry counters, set `md_root = P_INVALID`, mark DB and transaction dirty, and leave the DBI open.
- `mdb_drop(txn, named_dbi, 1)` should delete the named subdatabase record from the main DB, mark the DBI stale, close the handle slot, and make later use of stale handles fail through DBI sequence checks.
- Drop tests should include overflow records, nested subdatabases, duplicate-sorted DBs, branch-only traversal, and error injection from page fetch or IDL growth to confirm `MDB_TXN_ERROR` is set.
- `mdb_reader_list` should emit `(no reader locks)` when no lock table is mapped, `(no active readers)` for an empty table, a header once for active readers, and stop early if the callback returns a negative value.
- `mdb_reader_check` should set `*dead = 0` before scanning, ignore this process's slots, check each external PID once, clear every slot for a dead PID under the reader mutex, and report the number of cleared slots.
- Robust mutex tests, where available, should simulate `MDB_OWNERDEAD` for reader and writer mutexes, verify stale readers are cleared, verify `mdb_mutex_consistent` is called on successful recovery, and verify same-process dead writer recovery marks the environment fatal.
- Windows path tests should exercise `utf8_to_utf16` with valid UTF-8, invalid conversion errors, allocation failure, and extra-capacity requests used by filename suffix handling.
