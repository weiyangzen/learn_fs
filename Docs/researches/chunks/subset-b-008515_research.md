# sources/storage-engines/lmdb/libraries/liblmdb/mdb.c lines 8939-12845

## Scope

This chunk covers the tail of LMDB's write-path cursor insertion logic, the public cursor put/delete wrappers, low-level page/node mutation helpers, duplicate-data subcursor setup, cursor lifecycle APIs, B-tree delete rebalancing, B-tree page splitting, environment copy/dump/load helpers, environment metadata APIs, database-handle open/drop/stat APIs, comparator hooks, and reader-lock cleanup/recovery.

The range begins inside `_mdb_cursor_put()` after the caller has already found or prepared the insertion point. It ends at the final Windows UTF-8 to UTF-16 helper and the closing Doxygen marker. The code is therefore not a single feature boundary; it is the back half of the core LMDB engine implementation for mutation, maintenance, and exported environment/database management APIs.

## Purpose

The main purpose of this chunk is to keep LMDB's memory-mapped B+tree structurally correct while exposing the public mutation and maintenance APIs. Its responsibilities include:

- finishing cursor-based insertion into normal pages, duplicate-data subdatabases, fixed-size duplicate `P_LEAF2` pages, and overflow-page backed values;
- deleting keys, duplicate values, named-database records, overflow payloads, and entire database trees;
- maintaining page accounting in `MDB_db` (`md_depth`, branch/leaf/overflow page counts, root page, entry count);
- preserving cursor validity across page insertions, deletions, moves, merges, root collapse, and splits;
- splitting full leaf/branch pages and propagating separator keys upward, including recursive parent splits and root creation;
- exporting environments either as a raw file copy, a compacted page-renumbered copy, or an incremental dump of pages newer than a requested transaction ID;
- importing incremental dump records back to the environment file;
- exposing environment flags, user context, path/file descriptor, page-size, stats, info, and max-key APIs;
- opening, closing, dropping, and querying named database handles stored as `F_SUBDATA` records in the main DB;
- installing per-DB key/duplicate comparators and relocation callbacks;
- listing readers, clearing stale reader table slots, and recovering robust mutex state after a dead lock owner.

## Important APIs, Types, And Functions

### Cursor Put/Delete Entry Points

- `_mdb_cursor_put()` tail at the beginning of the chunk handles the actual node add/split and duplicate-subdatabase write after earlier lookup and flag validation. It computes node size, calls `mdb_page_split()` if the target page lacks space, calls `mdb_node_add()` otherwise, refreshes peer cursors, writes sorted duplicates through the xcursor, updates inline sub-DB metadata with `mdb_subdb_adjust()`, increments `md_entries`, handles `MDB_MULTIPLE`, and marks the transaction errored on late failures.
- `mdb_cursor_put()` is the public tracing wrapper around `_mdb_cursor_put()`.
- `_mdb_cursor_del()` validates write transaction state and cursor initialization, spills dirty pages unless `MDB_NOSPILL` is set, touches the current page for copy-on-write, handles sorted-duplicate deletion through an xcursor, frees overflow pages, drops child sub-DB pages when deleting `F_SUBDATA`, rejects `F_SUBDATA` mismatches, and delegates final node removal to `mdb_cursor_del0()`.
- `mdb_cursor_del()` is the public tracing wrapper around `_mdb_cursor_del()`.
- `mdb_put()` creates a stack cursor, tracks it in the transaction cursor list for fixups, and delegates to `_mdb_cursor_put()`.
- `mdb_del()` validates DBI/key/write state, ignores the data argument for non-`MDB_DUPSORT` DBs, and delegates to `mdb_del0()`.
- `mdb_del0()` initializes a stack cursor, searches by key or key+dupdata, temporarily tracks the cursor because delete rebalancing can split parent separator pages, and calls `_mdb_cursor_del()`.

### Page And Node Mutation

- `mdb_page_new()` allocates one or more pages with `mdb_page_alloc()`, initializes header bounds, applies page flags, updates the owning DB's branch/leaf/overflow page counts, and stores overflow page count in `mp_pages`.
- `mdb_leaf_size()` computes the on-page node footprint for a leaf key/value pair, replacing large data with an `MDB_ovpage` descriptor when it exceeds `me_nodemax`.
- `mdb_branch_size()` computes branch-node footprint from key size; branch-key overflow is explicitly not implemented here.
- `mdb_node_add()` inserts a node into the page under the current cursor. It handles `P_LEAF2` fixed-size duplicate pages as a compact key array, allocates overflow pages for large leaf values, shifts pointer slots, writes `MDB_node` headers/key/data, supports `MDB_RESERVE` by returning the destination data pointer to the caller, and marks the transaction errored on impossible page-full conditions.
- `mdb_node_del()` removes a node or fixed-size duplicate key from a page, compacts the node payload area with `memmove()`, adjusts pointer offsets below the removed node, and updates `mp_lower`/`mp_upper`.
- `mdb_node_shrink()` compacts an inline duplicate subpage after duplicate deletion, reducing the enclosing node data size and shifting the containing page's payload area upward.
- `mdb_update_key()` replaces a branch separator key in place when possible. If the new key's even-aligned size grows beyond available page space, it deletes the branch node and calls `mdb_page_split()` with `MDB_SPLIT_REPLACE`.

### Duplicate Data And Cursor Setup

- `mdb_xcursor_init0()` initializes the duplicate-data subcursor fields that depend only on the parent cursor and database flags. Sorted duplicates are modeled as a child DB whose keys are duplicate values and whose data values are empty.
- `mdb_xcursor_init1()` initializes the subcursor from the current leaf node. For `F_SUBDATA`, it copies an `MDB_db` record out of the node. For inline duplicate subpages, it synthesizes an `MDB_db` rooted in the fake page stored inside node data, including `MDB_DUPFIXED` and `MDB_INTEGERDUP` handling.
- `mdb_xcursor_init2()` refreshes another cursor's xcursor after the authoritative cursor changed a duplicate-data item or converted a regular item to duplicate data.
- `mdb_cursor_init()` initializes an `MDB_cursor` for a transaction/DBI, sets DB and DBX pointers, copies read/write flags from the transaction, initializes an xcursor for `MDB_DUPSORT`, and refreshes stale DB roots through `mdb_page_search()`.
- `mdb_cursor_open()`, `mdb_cursor_renew()`, `mdb_cursor_close()`, `mdb_cursor_txn()`, `mdb_cursor_dbi()`, `mdb_cursor_count()`, and `mdb_cursor_is_db()` implement the public cursor lifecycle and inspection APIs.
- `mdb_cursor_copy()` is the internal shallow cursor-stack copy used for page move/merge/split/rebalance traversals.
- `WITH_CURSOR_TRACKING` temporarily inserts a stack cursor into the transaction's tracked cursor list so lower-level split/rebalance code can update it consistently.

### Rebalancing, Moving, Merging, Splitting

- `mdb_node_move()` moves one node from a source page to a destination sibling during rebalance. It touches both pages, extracts the correct key/data/child page, handles branch-page first-key separator semantics, adds the node to the destination, deletes it from the source, updates peer cursors, and updates parent separator keys.
- `mdb_page_merge()` moves all nodes from one page into a sibling, removes the source page's parent pointer, frees the source page with `mdb_page_loose()`, adjusts page counts, rewrites peer cursor stacks to point into the merged page, then rebalances the parent.
- `mdb_rebalance()` is the delete-side underflow handler. It checks fill thresholds and minimum key counts, handles empty root deletion, root branch collapse, neighbor selection, single-node borrow via `mdb_node_move()`, or full-page merge via `mdb_page_merge()`.
- `mdb_cursor_del0()` performs the final delete: it removes the node, decrements `md_entries`, marks or shifts peer cursors that pointed at the deleted key, calls `mdb_rebalance()`, and then fixes cursors that now point past page end or require xcursor reinitialization.
- `mdb_page_split()` splits a full page and inserts a new node. It creates a right sibling, optionally creates a new branch root, chooses a split index, handles append and `P_LEAF2` fast paths, uses a temporary page copy for normal leaf/branch redistribution, inserts the separator into the parent or recursively splits the parent, moves nodes into left/right pages, updates cursor position and `MDB_RESERVE` output pointers, and fixes every tracked cursor affected by the split.

### Environment Copy, Dump, And Load

- `mdb_copy` carries state for compacting copies: source env/txn, mutex/condition, two write buffers, optional overflow buffers, next destination page number, output fd, toggle state, EOF signaling, and an atomic-ish error slot.
- `mdb_env_copythr()` is the writer thread for compacting copy. It waits for filled buffers, optionally applies checksums and encryption for remapped/read-page-cache builds, writes the main buffer and overflow tail with `DO_WRITE`, handles short writes, clears buffers, and signals the provider.
- `mdb_env_cthr_toggle()` hands a buffer and/or EOF to the writer thread, waits until at least one buffer is free, toggles provider state, and returns any writer error.
- `mdb_env_cwalk()` performs depth-first compacting traversal of a DB tree. It rewrites page numbers into a dense sequence starting after the meta pages, copies branch/leaf pages into output buffers, rewrites overflow-page references, recursively compacts named subdatabases, and writes overflow content contiguously when checksum/encryption/remapping requires it.
- `mdb_env_copyfd1()` creates a compacted environment image. It initializes new meta pages, starts a read transaction, computes the expected compacted root by subtracting free pages, walks the main DB with `mdb_env_cwalk()`, verifies the resulting root, signals EOF, joins the writer thread, and aborts the read transaction.
- `mdb_env_copyfd0()` performs an as-is copy. It starts a read transaction, briefly holds the write mutex to snapshot meta pages consistently, writes the meta pages, bounds copy length by both `mt_next_pgno` and actual file size, and writes the remainder of the mapped file or remapped chunks.
- `mdb_env_copyfd2()`, `mdb_env_copyfd()`, `mdb_env_copy2()`, and `mdb_env_copy()` expose compact/non-compact copy to file handles or paths.
- `mdb_env_incr_dumpfd()` writes only meta pages and data pages whose `mp_txnid` is greater than a caller-provided transaction ID. It snapshots meta pages under the write mutex, then scans pages from pgno 2 to `mt_next_pgno`, expanding overflow page writes as one record.
- `mdb_env_incr_dump()` opens an output file and delegates to `mdb_env_incr_dumpfd()`.
- `mdb_env_incr_loadfd()` reads page records from an incremental dump and writes them to the environment file at their page-number-derived offsets, handling overflow pages, optional encrypted headers, seeks over gaps, and short-write errors.

### Environment And DBI APIs

- `mdb_env_set_flags()` and `mdb_env_get_flags()` mutate/query changeable exposed environment flags.
- `mdb_env_set_userctx()` and `mdb_env_get_userctx()` store caller context on the environment.
- `mdb_env_set_assert()` installs a debug assertion callback when assertions are enabled.
- Under `MDB_RPAGE_CACHE`, `mdb_env_set_encrypt()` and `mdb_env_set_checksum()` install encryption/checksum callbacks before the environment is active.
- `mdb_env_get_path()`, `mdb_env_get_fd()`, and `mdb_env_set_pagesize()` expose path/fd and configure page size before mapping.
- `mdb_stat0()`, `mdb_env_stat()`, `mdb_env_info()`, and `mdb_stat()` fill `MDB_stat`/`MDB_envinfo` from current meta or transaction DB records.
- `mdb_default_cmp()` selects default key and duplicate comparator functions from persistent DB flags (`MDB_REVERSEKEY`, `MDB_INTEGERKEY`, `MDB_DUPSORT`, `MDB_INTEGERDUP`, `MDB_DUPFIXED`, `MDB_REVERSEDUP`).
- `mdb_dbi_open()` opens the main DB or a named DB. Named DBs are stored as `F_SUBDATA` records in the main DB, may be created with `MDB_CREATE`, are limited by `me_maxdbs`, cannot coexist with certain main-DB flags, and register name/sequence/flags/comparators in the transaction DBI arrays.
- `mdb_dbi_close()` clears an environment DBI slot and frees its name.
- `mdb_dbi_flags()` returns persistent flags for an open user DBI.
- `mdb_drop0()` walks a DB tree and appends its pages, overflow ranges, and optional sub-DB pages to the transaction free-page list.
- `mdb_drop()` empties or deletes a DBI. Dropping `MAIN_DBI` resets core DB records for the whole environment if no named DBIs are still valid; dropping named DBs uses `mdb_drop0()`, invalidates tracked cursors, optionally deletes the named DB record from the main DB, or resets the `MDB_db` record in-place.
- `mdb_set_compare()`, `mdb_set_dupsort()`, `mdb_set_relfunc()`, and `mdb_set_relctx()` install per-DB key/duplicate comparators and relocation callbacks/context.
- `mdb_env_get_maxkeysize()` returns the current environment key-size limit.

### Reader Table And Mutex Recovery

- `mdb_reader_list()` reports active reader slots through a callback, formatting pid, thread ID, and transaction ID.
- `mdb_pid_insert()` maintains a sorted unique PID list used to avoid checking the same process repeatedly.
- `mdb_reader_check()` and `mdb_reader_check0()` find stale reader slots by probing process liveness, optionally locking the reader mutex, rechecking after lock acquisition to avoid PID reuse races, clearing dead slots, and returning the cleared count.
- Under `MDB_ROBUST_SUPPORTED`, `mdb_mutex_failed()` handles robust mutex owner death. It updates shared txnid state for writer-mutex recovery, marks the environment fatal if the dead writer was this process, runs stale-reader cleanup, calls `mdb_mutex_consistent()`, and unlocks on recovery failure.
- On Windows, `utf8_to_utf16()` converts path strings to wide strings with optional extra space for suffixes.

## Control Flow

Insertion flow in this chunk starts after `_mdb_cursor_put()` has established `insert_key`, `insert_data`, duplicate flags, and the target cursor slot. It computes the required leaf size and either splits the page or inserts directly with `mdb_node_add()`. Direct insertions immediately walk `mt_cursors[dbi]` to bump cursor indexes and refresh xcursor pointers for cursors that point into the same page. If the value is a sorted duplicate, the code initializes or refreshes the xcursor, writes any converted original duplicate first, updates peer xcursor state, writes the requested duplicate value into the child DB, copies persistent sub-DB metadata back into the parent node when required, and increments the parent DB entry count only if a real new data item was added.

Delete flow begins in `_mdb_cursor_del()`. The function refuses read-only or blocked transactions, requires an initialized cursor, spills dirty pages unless explicitly suppressed, and touches the current page before modifying it. If the current node owns duplicate data, it either deletes all duplicates (`MDB_NODUPDATA`) or recursively deletes the current duplicate through the xcursor. When a duplicate sub-DB still has entries, the parent node is updated or inline subpage storage is shrunk and peer xcursor pages are refreshed. When the duplicate sub-DB becomes empty, the parent node falls through to normal deletion. Overflow values are freed before `mdb_cursor_del0()` removes the node, adjusts cursors, and invokes `mdb_rebalance()`.

Rebalance flow is threshold-driven. Pages above the fill threshold and with enough keys return immediately. Empty or single-child roots are special: an empty root invalidates cursors and sets `md_root = P_INVALID`, while a one-child branch root collapses the tree height by promoting its child. Non-root underflows choose a left neighbor if available, otherwise a right neighbor. A sufficiently full neighbor lends one node through `mdb_node_move()`. Otherwise pages merge through `mdb_page_merge()`, which frees the source page and recursively rebalances the parent.

Split flow in `mdb_page_split()` is the write-side counterpart. The function allocates a right sibling, creates a new root branch if splitting the old root, builds an internal cursor for the right side, chooses a separator key, and ensures the parent has room for a branch pointer. If the parent is full, it recursively splits the parent first. For append inserts, the new node goes straight to the right page. For normal `P_LEAF2` pages, the key array is divided by copying fixed-size key regions. For normal branch/leaf pages, a temporary page copy is used to preserve original node order while redistributing nodes through `mdb_node_add()`. After the split, tracked cursors are shifted to the new root or right sibling as needed, and duplicate subcursors are refreshed for leaf-page moves.

Compacting copy flow starts in `mdb_env_copyfd1()`. The producer allocates two write buffers, starts the writer thread, begins a read transaction, fabricates fresh meta pages, estimates the compacted root from the free-page count, and calls `mdb_env_cwalk()` on the main DB root. The walker traverses from first leaf onward, copies pages into a dense output page-number sequence, rewrites branch child pgnos and overflow descriptors, and recurses into named subdatabases. The writer thread drains buffers to the output descriptor and applies checksum/encryption transformations when compiled in. Completion is signaled by `MDB_EOF`, after which the thread is joined and the read transaction is aborted.

Raw copy flow in `mdb_env_copyfd0()` is simpler but still requires synchronization. It starts a read transaction, and if lock-table support exists it resets the txn, takes the write mutex, renews the read txn to get a consistent meta snapshot, writes the two meta pages, then releases the writer lock. The rest of the database image is copied up to the lesser of the read transaction's next page and the current file size.

Named DBI open flow treats the main DB as the namespace for other DBs. `mdb_dbi_open()` returns `MAIN_DBI` immediately for a null name, otherwise it searches existing DBI slots by stored name, enforces the max-DB limit, searches the main DB for a matching key, validates that the found node is `F_SUBDATA`, optionally creates a zeroed `MDB_db` subrecord with `_mdb_cursor_put()`, then registers the slot name, flags, DB sequence, copied DB record, and default comparators.

Drop flow first distinguishes main DB reset from named DB drop. Main DB reset requires all named DBIs to be closed/invalid, then clears core DB records and marks the transaction dropped. Named DB drop opens a cursor, calls `mdb_drop0()` to add pages to the free list, invalidates cursors on that DBI, and either deletes the DB record from the main DB (`del != 0`) or leaves the named DBI present but empty.

Reader cleanup flow lists or checks shared reader slots. `mdb_reader_check0()` avoids duplicate PID probes, verifies process liveness, locks the reader mutex only when needed, rechecks after acquiring it, clears all slots for a stale PID, and reports how many were cleared. Robust mutex failure recovery uses this same reader cleanup path before marking the mutex consistent.

## State And Persistence Behavior

This chunk mutates the durable B+tree representation and the transaction-local metadata that will be committed into LMDB meta pages:

- page headers (`mp_pgno`, `mp_flags`, `mp_lower`, `mp_upper`, `mp_pages`, `mp_pad`, `mp_txnid`);
- leaf and branch nodes (`mn_ksize`, `mn_flags`, node data size, child pgno, overflow descriptors);
- overflow pages and `MDB_ovpage` descriptors;
- database records (`MDB_db`) for main, free, duplicate, and named DBs;
- `MDB_db` counters for depth, branch pages, leaf pages, overflow pages, entries, flags, pad, and root page;
- transaction free-page list `mt_free_pgs`;
- dirty/loose/spilled page state managed through page allocation, touch, loose, and overflow-free helpers;
- meta-page data when copying, compacting, dumping, and loading environments.

The code relies on LMDB's copy-on-write transaction model. Mutating functions touch pages before editing, allocate new pages from the transaction allocator, and mark the transaction with `MDB_TXN_ERROR` when a structural operation fails after partial modification. Public APIs reject read-only or blocked transactions before writes.

Cursor state is a major in-memory persistence concern. `MDB_cursor` stacks (`mc_pg[]`, `mc_ki[]`, `mc_snum`, `mc_top`, flags) are treated as live references into mutable pages. Every page insert/delete/move/merge/split walks tracked cursors in `mt_cursors[dbi]` and updates page pointers, indices, EOF/delete flags, and xcursor roots. The sorted-duplicate xcursor state mirrors child DB metadata and must be refreshed whenever inline subpage memory moves.

Named database state is persisted as records in the main DB with `F_SUBDATA`. Opening a named DB copies its `MDB_db` record into transaction arrays; creating one writes an empty `MDB_db` with `md_root = P_INVALID`. Dropping with deletion removes the main-DB record and closes the environment DBI slot, while emptying keeps the DBI and marks its transaction DB record dirty.

Copy/export behavior has two different persistence models. Raw copy preserves original page numbers and file layout up to the read transaction snapshot. Compact copy creates a new logical environment image with dense page numbers, fresh meta pages, transaction ID 1, and rewritten roots/branch pointers/overflow descriptors. Incremental dump preserves original page numbers but emits only pages newer than a threshold transaction ID; incremental load writes those page records back to their absolute file offsets.

Reader-lock state lives outside the data file in the lock region (`me_txns->mti_readers`). This chunk can clear stale reader slots but does not modify database pages during reader cleanup. Robust mutex recovery can update `mti_txnid` and set `MDB_FATAL_ERROR` on the environment if a dead writer belongs to the current process.

## Dependencies And Integration Points

This chunk is tightly coupled to the rest of `mdb.c` and LMDB's public API surface:

- Page access/allocation: `mdb_page_alloc()`, `mdb_page_malloc()`, `mdb_page_free()`, `mdb_page_touch()`, `mdb_page_loose()`, `MDB_PAGE_GET()`, `MDB_PAGE_UNREF()`, `MDB_CURSOR_UNREF()`, `mdb_ovpage_free()`, and page-copy helpers.
- Cursor navigation/search: `mdb_page_search()`, `mdb_page_search_root()`, `mdb_page_search_lowest()`, `mdb_cursor_set()`, `mdb_cursor_get()`, `mdb_cursor_first()`, `mdb_cursor_sibling()`, `mdb_cursor_pop()`, and prior parts of `_mdb_cursor_put()`.
- Node/page macros: `IS_LEAF`, `IS_BRANCH`, `IS_LEAF2`, `IS_OVERFLOW`, `IS_SUBP`, `NUMKEYS`, `NODEPTR`, `NODEKEY`, `NODEDATA`, `NODEDSZ`, `NODEPGNO`, `SETPGNO`, `SETDSZ`, `LEAF2KEY`, `METADATA`, `SIZELEFT`, `PAGEFILL`, `MP_PTRS`, `MP_LOWER`, `MP_UPPER`, and page-size constants.
- Duplicate-data support: `MDB_DUPSORT`, `MDB_DUPFIXED`, `MDB_INTEGERDUP`, `F_DUPDATA`, `F_SUBDATA`, `mdb_subdb_adjust()`, and xcursor initialization/refresh macros.
- Free-list support: `mdb_midl_append()`, `mdb_midl_append_range()`, `mdb_midl_need()`, and `mdb_midl_xappend()`.
- Transaction state: `MDB_txn` flags, `mt_dbs`, `mt_dbxs`, `mt_dbflags`, `mt_dbiseqs`, `mt_numdbs`, `mt_next_pgno`, `mt_cursors`, `mt_free_pgs`, `mt_txnid`, and transaction begin/abort/renew/reset functions.
- Environment/file I/O: `mdb_env_pick_meta()`, `mdb_env_init_meta0()`, `mdb_env_copy_open()`, `mdb_fname_init()`, `mdb_fopen()`, `mdb_fsize()`, `MAP()`, `munmap()`, `DO_WRITE`, `read`, `write`, `lseek`, Windows `ReadFile`/`WriteFile`/`SetFilePointerEx`, and close/error wrappers.
- Threading/locking: pthread mutexes/condition variables, Windows mutex/event abstractions, `THREAD_CREATE`, `THREAD_FINISH`, `LOCK_MUTEX`, `LOCK_MUTEX0`, `UNLOCK_MUTEX`, robust mutex consistency, and reader PID liveness probes.
- Optional read-page-cache/encryption/checksum support: `MDB_RPAGE_CACHE`, `MDB_REMAPPING`, `mdb_page_set_checksum()`, `mdb_page_encrypt()`, `mdb_rpage_get()`, `MDB_enc_func`, and `MDB_sum_func`.
- Public DB configuration: comparator functions (`mdb_cmp_memn`, `mdb_cmp_memnr`, `mdb_cmp_cint`, `mdb_cmp_int`, `mdb_cmp_clong`), relocation callback storage, persistent flag validation, and `me_dbiseqs` DBI invalidation.

## Risks And Edge Cases

- `_mdb_cursor_put()` failure after inserting a parent duplicate node but before writing the child duplicate must mark the transaction errored. Otherwise a partially created empty sub-DB or mismatched entry count could be committed.
- Sorted duplicates are represented as child DB keys with empty data. Size limits, comparator selection, `MDB_APPENDDUP`, `MDB_NODUPDATA`, and inline-vs-`F_SUBDATA` transitions all depend on xcursor state staying synchronized.
- `mdb_node_add()` returns a writable pointer for `MDB_RESERVE`. After page split, the code must update `newdata->mv_data` to the final node location or overflow payload, not the temporary page copy.
- Overflow descriptors are copied into leaf nodes while payload pages are separately allocated/freed. Any mismatch in `op_pgno`, `op_pages`, or DB overflow counters risks leaks or dangling page references.
- `mdb_node_del()` and `mdb_node_shrink()` perform manual page compaction with offset arithmetic. Alignment mistakes can corrupt every node after the edited slot.
- Branch first-key handling is special: the first key in a branch page is often empty/implicit, and moving/merging/splitting branch pages must recalculate separators from the lowest descendant key.
- `mdb_update_key()` can call `mdb_page_split()` while delete rebalancing is in progress. The temporary cursor tracking macro exists because otherwise stack cursors would not be fixed up by recursive split code.
- Root deletion and root collapse mutate tree height. Peer cursor stacks must be invalidated or shifted exactly once; missed cursors could later dereference freed pages or wrong levels.
- `mdb_page_split()` uses a temporary page as both source and destination during redistribution. The loop that switches from right page to temp copy is subtle, and failure paths must free the temp page and mark `MDB_TXN_ERROR`.
- Splits during append mode intentionally bias new data into the right page. Incorrect separator or cursor-index updates would mostly surface under sequential insert workloads.
- `mdb_drop0()` can skip leaf scanning when it knows there are no overflow/sub-DB pages. Incorrect page-count metadata could make it skip needed overflow frees.
- Dropping `MAIN_DBI` is destructive for the whole environment and is only valid when no named DBIs are open. The code leaves the transaction only committable or abortable afterward via `MDB_TXN_DROPPED`.
- `mdb_dbi_open()` allocates and stores a duplicated name before creating a DB record to avoid failing after persistent creation. Reordering this could leave an unregistered persistent named DB.
- Main DB flags are constrained when named databases are used. Mixing `MDB_DUPSORT` or `MDB_INTEGERKEY` on the main DB with named DB records would make namespace lookup semantics incompatible.
- Compact copy rewrites page numbers and expects the final root to equal `txn->mt_next_pgno - 1 - freecount`. A mismatch is treated as `MDB_INCOMPATIBLE`, signaling page leak or corruption.
- Copy paths must handle short writes and nonblocking descriptors as errors. Returning success after a zero-length write would create truncated backups.
- Compacting copy with encryption/checksums has extra ownership hazards: overflow tails may be malloc-backed or mapped, and encrypted temporary buffers must be freed on each toggle.
- Raw copy briefly blocks writers to snapshot meta pages. If that critical section is weakened, the copy can contain old meta pages pointing at newer or missing data pages.
- Incremental load trusts page numbers from the dump stream enough to seek the environment file. Corrupt or malicious dump input can write sparse/gapped page regions; callers need to treat it as a privileged recovery/replication input.
- `mdb_env_set_pagesize()` only validates before mapping. Changing page size after `me_map` exists would invalidate every page-layout macro, so it is rejected.
- Reader cleanup must avoid PID reuse races. The code rechecks process liveness after taking the reader mutex; removing that can clear a valid reader that reused a PID.
- Robust mutex recovery marks the environment fatal if the dead writer was this process. Continuing to use the same environment after in-process writer death risks data loss.

## Test Signals

Useful test coverage for this chunk includes:

- Cursor put: insert into page with room, insert requiring leaf split, insert requiring parent split, root split, branch split, append inserts, `MDB_RESERVE`, overflow-value insert, and `MDB_MULTIPLE` partial success count.
- Sorted duplicates: first duplicate creation, conversion from single value to duplicate sub-DB, duplicate insertion with `MDB_NODUPDATA`, `MDB_APPENDDUP`, fixed-size duplicates, integer duplicates, deleting one duplicate, deleting all duplicates, and transition from inline subpage to `F_SUBDATA`.
- Cursor validity: multiple live cursors on the same page during insert/delete/split/merge, cursors on xcursor subpages, cursors at EOF, cursors pointing to the deleted slot, and stack cursors tracked through delete-induced parent splits.
- Node/page mutation: large value overflow allocation/free, page-full error injection, `MDB_RESERVE` pointer location after split, `P_LEAF2` insert/delete ordering, branch separator key growth that forces split, and odd-sized inline subpage shrink avoidance.
- Rebalance: delete to empty root, collapse single-child root, borrow from left/right neighbor, merge into left/right neighbor, branch-page minimum-key enforcement, and duplicate-data xcursor refresh after rebalance.
- DBI management: open main DB with persistent flags, create named DB, reopen existing named DB, exceed `me_maxdbs`, attempt named DB under incompatible main DB flags, open non-DB record as DB, create in read-only txn, close DBI and observe sequence invalidation, and query DB flags.
- Drop: empty named DB, delete named DB record, drop DB with overflow pages, drop DB containing sub-DB records, drop `MAIN_DBI` with/without open named DBIs, and cursor invalidation after drop.
- Environment copy: raw copy with active readers/writers, compact copy of empty DB, compact copy with free pages, compact copy with named DBs and overflow pages, compact copy under checksum/encryption/remapping builds, output fd short-write failures, and expected-root mismatch on intentionally corrupted page accounting.
- Incremental dump/load: threshold at current txnid (no data pages), threshold below current txnid, overflow pages, meta-page-only changes, encrypted page headers, load with noncontiguous page numbers, and short read/write failure paths.
- Environment APIs: invalid flag bits, exposed flag filtering, page-size power-of-two bounds, set encryption/checksum after env active rejection, null argument validation, and stats/info values after mutations.
- Reader APIs: no lock table, no active readers, multiple slots with same PID, stale PID cleanup count, reader mutex already held path, PID reuse recheck, and robust mutex owner-death recovery for reader and writer mutexes.
