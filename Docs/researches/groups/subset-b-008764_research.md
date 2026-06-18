# subset-b-008764 research

Grouped research for SQLite core sources under `sources/storage-engines/sqlite/src`. Each section is source-tree-aligned and delimited for reconciliation into per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/analyze.c -->
# sources/storage-engines/sqlite/src/analyze.c

## Purpose

`analyze.c` implements the SQL `ANALYZE` command and the runtime loading of persisted planner statistics. It creates and refreshes `sqlite_stat1` and, when `SQLITE_ENABLE_STAT4` and the `SQLITE_Stat4` optimization are active, `sqlite_stat4`. The file is the bridge between table/index scans, VDBE bytecode, the internal query planner estimates stored on `Table` and `Index`, and persisted statistics rows in ordinary database tables.

## Important APIs, Types, And Functions

The main parser entry point is `sqlite3Analyze(Parse*, Token*, Token*)`, which accepts whole-database, single-database, table, and index forms. It delegates to `analyzeDatabase()` and `analyzeTable()`, which open statistic tables with `openStatTable()`, emit VDBE code with `analyzeOneTable()`, and then add `OP_LoadAnalysis` through `loadAnalysis()`.

STAT collection uses internal SQL functions, not public SQL APIs. `stat_init()` allocates a `StatAccum` blob, `stat_push()` observes sorted index rows and updates cardinality counters and optional samples, and `stat_get()` emits `sqlite_stat1` text or STAT4 sample fields. `StatSample` stores `nEq`, `nLt`, `nDLt`, sampled rowid/key material, sample priority, and tie-break hashes. `StatAccum` stores row counts, scan limits, current counters, periodic sampling cadence, sample arrays, and best-sample candidates.

The load side is centered on `sqlite3AnalysisLoad(sqlite3*, int)`. It clears prior planner stats, reads `sqlite_stat1` through `sqlite3_exec()` and `analysisLoader()`, decodes integer arrays with `decodeIntArray()`, applies flags such as `unordered`, `noskipscan`, `sz=`, and optional `costmult=`, then loads STAT4 samples through `loadStat4()` and `loadStatTbl()`. `sqlite3DeleteIndexSamples()` owns cleanup of `Index.aSample`, and `initAvgEq()` derives average equality estimates from loaded samples.

## Control Flow

For an `ANALYZE` statement, schema mutexes must already be held and `sqlite3ReadSchema()` must succeed. Whole-database analysis skips TEMP, starts a write operation per target database, creates or clears `sqlite_stat1` and optionally `sqlite_stat4`, then iterates the schema table hash. Per-table or per-index analysis deletes only matching stat rows by `tbl` or `idx`.

`analyzeOneTable()` ignores views, virtual tables, and SQLite system tables. It opens the table and each selected index, builds bytecode that scans the index in key order, compares current key prefixes with saved previous prefix registers, calls `stat_push()` with the left-most changed column, then inserts one `sqlite_stat1` row. If STAT4 is enabled and the analysis limit is zero, it also loops over samples returned by `stat_get()`, seeks the table row, builds the sampled record, and inserts `sqlite_stat4` rows.

The runtime loader reverses the process: `sqlite3AnalysisLoad()` resets `TF_HasStat1`, `Index.hasStat1`, and STAT4 sample arrays, reads stat rows into schema objects, defaults indexes with missing stats, optionally loads STAT4 rows into contiguous `IndexSample` allocations, and frees temporary `aiRowEst` arrays after STAT4 initialization.

## State And Persistence Behavior

Persistent state is stored in `sqlite_stat1` and `sqlite_stat4` inside each analyzed database. `openStatTable()` either creates these tables, clears all rows, or deletes rows for one table/index. In-memory planner state is stored on `Table.nRowLogEst`, `Table.tabFlags`, `Index.aiRowLogEst`, `Index.hasStat1`, `Index.bUnordered`, `Index.noSkipScan`, `Index.szIdxRow`, optional `Index.aSample`, `Index.aAvgEq`, and `Index.nRowEst0`.

`db->nAnalysisLimit` changes behavior substantially. With a limit, `stat_push()` can request skip-ahead behavior and STAT4 collection is disabled by setting `StatAccum.mxSample` to zero. Without a limit, the full scan can collect histogram samples. Memory ownership is delicate: `StatAccum` is returned as a blob with `statAccumDestructor`, STAT4 sample rowids may allocate per sample, and loaded sample blobs allocate eight zero guard bytes to protect corrupted-record comparisons from small overreads.

## Dependencies And Integration Points

This file depends on parser and schema services (`sqlite3ReadSchema`, `sqlite3FindTable`, `sqlite3FindIndex`, `sqlite3LocateTable`), VDBE construction (`OP_OpenRead`, `OP_OpenWrite`, `OP_Count`, `OP_Insert`, `OP_LoadAnalysis`), btree/schema mutex assertions, table/index metadata, collations, rowid and WITHOUT ROWID primary-key handling, authorization checks for `SQLITE_ANALYZE`, and optional preupdate-hook support. Planner consumers rely on loaded `Table` and `Index` estimates during query planning.

Compile-time and runtime gates include `SQLITE_OMIT_ANALYZE`, `SQLITE_ENABLE_STAT4`, `SQLITE_ENABLE_PREUPDATE_HOOK`, `SQLITE_ENABLE_COSTMULT`, `SQLITE_ENABLE_EXPLAIN_COMMENTS`, `SQLITE_DEBUG`, and the `SQLITE_Stat4` optimization flag.

## Risks And Edge Cases

The highest-risk areas are register lifetime in generated VDBE, prefix-change detection for unique, partial, expression, rowid, and WITHOUT ROWID indexes, and consistency between persisted stat text and planner fields. STAT4 sample ranking is subtle: it mixes periodic samples, high-cardinality duplicate prefixes, tie-break hashes, and delayed filling of zero `anEq` slots. Corrupt or manually edited `sqlite_stat` tables must not crash the loader. Duplicate stat rows are tolerated by clobbering or skipping, but they can change estimates. Analysis limits intentionally trade accuracy for speed and disable histogram generation.

## Test Signals

Useful signals include sqllogictest or TCL tests for `ANALYZE` forms, partial indexes, WITHOUT ROWID tables, expression indexes, `analysis_limit`, generated `sqlite_stat1` text, STAT4 sample counts, query-plan changes after `OP_LoadAnalysis`, malformed stat tables, OOM paths, and compile variants with and without STAT4. Assertions around schema mutexes, temp-register ranges, and `sqlite3NoTempsInRange()` are important debug-only signals for bytecode safety.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/analyze.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/attach.c -->
# sources/storage-engines/sqlite/src/attach.c

## Purpose

`attach.c` implements SQL `ATTACH` and `DETACH` plus the database-name fixing logic used when compiling persistent views, triggers, and indexes. It manages the `sqlite3.aDb[]` array, opens and closes attached btrees, validates schema compatibility, and prevents non-TEMP schema objects from referencing objects in a different attached database.

## Important APIs, Types, And Functions

Parser-facing entry points are `sqlite3Attach()` and `sqlite3Detach()`. They both call `codeAttach()`, which resolves expressions, runs authorization with `SQLITE_ATTACH` or `SQLITE_DETACH`, emits calls to internal SQL functions, and expires prepared statements. Runtime work happens in `attachFunc()` and `detachFunc()`, registered as `sqlite_attach` and `sqlite_detach` function definitions.

`sqlite3DbIsNamed()` compares a schema index with a requested name, treating database zero as both its stored schema name and `main`. The DDL fixer API is `sqlite3FixInit()`, `sqlite3FixSrcList()`, `sqlite3FixSelect()`, `sqlite3FixExpr()`, and `sqlite3FixTriggerStep()`. These use a `Walker` embedded in `DbFixer`, with `fixExprCb()` rejecting variables in normal DDL and `fixSelectCb()` pinning source items to the target schema.

## Control Flow

`resolveAttachExpr()` treats a top-level bare identifier in `ATTACH` or `DETACH` as a string literal, while still resolving more complex expressions normally. `codeAttach()` reads the schema, resolves file/name/key expressions, checks authorization using the original file/name expression when available, evaluates arguments into registers, invokes the internal function, and emits `OP_Expire`; ATTACH expires only the current statement, while DETACH expires all statements.

`attachFunc()` handles two paths. The special deserialize path, gated by `db->init.reopenMemdb`, replaces an existing database slot with a new `memdb` btree after verifying no transaction or backup is active. The normal path checks the attached database limit, rejects duplicate schema names, grows `db->aDb`, parses URI flags, applies `SQLITE_AttachWrite` and `SQLITE_AttachCreate` restrictions, opens a btree, installs a schema, applies pager settings, validates text encoding, initializes the attached schema, and rolls back all state on any error.

`detachFunc()` resolves the schema by name, rejects unknown, `main`, and `temp` detach attempts, rejects active transactions or backups, retargets TEMP triggers that referenced the detached schema, closes the btree, clears the schema pointer, and collapses the database array.

## State And Persistence Behavior

ATTACH modifies only connection-local state until the attached file is opened and its schema read. It updates `db->aDb`, `db->nDb`, `Db.pBt`, `Db.pSchema`, `Db.zDbSName`, safety level, pager locking mode, secure-delete behavior, synchronous flags, `db->noSharedCache`, `db->init.iDb`, and `DBFLAG_SchemaKnownOk`. The attached database file itself persists independently through the btree/pager layer. DETACH removes the connection's handle to that file but does not delete the file.

DDL fixing persists indirectly by rewriting parse-tree source items: it sets fixed schema metadata, records `fromDDL`, rewrites variables to NULL during initialization, and rejects cross-database references for non-TEMP objects before those definitions are stored in schema tables.

## Dependencies And Integration Points

This file integrates parser expressions, authorization, VDBE code generation, URI parsing, VFS lookup, btree open/close, pager pragmas, shared-cache mutex entry, schema initialization, trigger/view walkers, UPSERT trigger steps, and optional deserialize support. It is conditionally compiled by `SQLITE_OMIT_ATTACH`, with DDL-fixer pieces still present because schema object validation is needed outside normal ATTACH support.

## Risks And Edge Cases

Risk is concentrated in partial state transitions. `attachFunc()` increments `db->nDb` before all validation succeeds, so the cleanup path must close btrees, reset schemas, decrement `nDb`, and preserve useful error messages. Duplicate names, read-only attach flags, create suppression, URI parse errors, incompatible encodings, schema-init errors, active backups, and memory failures all have distinct behavior. DDL fixing must correctly allow TEMP objects to reference any schema while preventing persistent cross-schema dependencies. Bare identifiers are stringified only at the root of ATTACH/DETACH expressions, so concatenated identifiers still resolve normally and may fail.

## Test Signals

Signals include ATTACH/DETACH success across URI, readonly, create/no-create, and encrypted-key syntaxes; duplicate schema-name rejection; attached database limit enforcement; incompatible encoding errors; rollback after schema-init failure; DETACH rejection for main/temp, active transactions, and backup state; prepared-statement expiry semantics; TEMP trigger retargeting after detach; and DDL tests proving non-TEMP views, triggers, and indexes cannot reference objects in another database.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/attach.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/auth.c -->
# sources/storage-engines/sqlite/src/auth.c

## Purpose

`auth.c` implements the optional `sqlite3_set_authorizer()` facility. It stores a user callback on the database handle and invokes it during SQL compilation to approve, deny, or ignore operations such as reading columns, updating tables, creating objects, running pragmas, transactions, ATTACH, and DETACH.

## Important APIs, Types, And Functions

The public API is `sqlite3_set_authorizer(sqlite3*, xAuth, void*)`, which installs or clears `db->xAuth` and `db->pAuthArg` under the connection mutex and expires existing prepared statements. `sqlite3AuthCheck()` is the common fast path used by parser/compiler code. It returns `SQLITE_OK` when no callback is installed or initialization is active, otherwise delegates to `realAuthCheck()`.

Column-read authorization is split into `sqlite3AuthRead()` and `sqlite3AuthReadCol()`. `sqlite3AuthRead()` maps a `TK_COLUMN` or trigger pseudo-column expression to a table, column name, schema index, and rowid/primary-key spelling. `sqlite3AuthReadCol()` invokes the callback with `SQLITE_READ` and writes detailed errors for denial. Authorization context is managed with `sqlite3AuthContextPush()` and `sqlite3AuthContextPop()`, which temporarily set `Parse.zAuthContext`.

## Control Flow

Installing a callback is straightforward: optional API armor checks the database handle, the database mutex is entered, callback fields are assigned, prepared statements are expired, and the mutex is released. During compilation, callers first hit `sqlite3AuthCheck()`. If authorization is disabled or `db->init.busy` is true, it returns success without invoking user code. Otherwise `realAuthCheck()` skips special parser modes, calls `db->xAuth(pAuthArg, code, zArg1, zArg2, zArg3, zAuthContext)`, converts `SQLITE_DENY` into a parse error and `SQLITE_AUTH`, preserves `SQLITE_IGNORE`, and treats invalid return codes as an authorizer malfunction.

For column reads, denial records "access to ..." with table/column and optional database prefix. `SQLITE_IGNORE` changes a resolvable expression from `TK_COLUMN` to `TK_NULL`; if `sqlite3AuthReadCol()` is used without an expression to rewrite, callers must treat ignore as denial.

## State And Persistence Behavior

This file does not persist database content. Its state is connection-local: `sqlite3.xAuth`, `sqlite3.pAuthArg`, `Parse.zAuthContext`, `Parse.rc`, and parse error text. Installing or clearing the callback invalidates prepared statements so future compilation observes the new policy. Authorization is intentionally a compile-time gate; it does not recheck each row at execution time except through decisions baked into the compiled expression tree.

## Dependencies And Integration Points

The implementation depends on parser state, expression and source-list metadata, schemas, trigger compilation, connection mutexes, prepared-statement expiration, error formatting, and the constants published by the SQLite C API. It is entirely omitted under `SQLITE_OMIT_AUTHORIZATION` and contains API armor under `SQLITE_ENABLE_API_ARMOR`.

## Risks And Edge Cases

The main semantic risk is confusing compile-time authorization with runtime access control. Existing prepared statements are expired after policy changes, but applications that cache statements must handle reprepare. `SQLITE_IGNORE` has special read-column behavior: a denied read can silently become NULL rather than failing the statement. Initialization and special parse modes intentionally bypass callbacks to avoid blocking schema loading, virtual table declaration, and rename internals. Invalid callback return values deliberately become errors to surface buggy authorizers.

## Test Signals

Useful tests set callbacks that return each allowed and invalid result for `SQLITE_READ`, DDL, DML, PRAGMA, ATTACH, and transaction actions. Column tests should verify NULL substitution for ignored reads, error text for denied reads, trigger/view auth contexts, rowid and INTEGER PRIMARY KEY naming, statement expiration after changing the callback, and no callback during schema initialization or special parser modes.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/auth.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/backup.c -->
# sources/storage-engines/sqlite/src/backup.c

## Purpose

`backup.c` implements the `sqlite3_backup_*` online backup API and the internal btree copy path used by VACUUM-like operations. It copies pages from a source database btree to a destination btree incrementally, keeps copied pages current while the source changes, and finalizes destination schema and file-size state when the copy completes.

## Important APIs, Types, And Functions

The central type is `struct sqlite3_backup`, which records source and destination database handles and `Db` slots, destination schema cookie, destination transaction state, next source page, result code, remaining/pagecount counters, pager attachment state, and linked-list membership on the source pager.

Public entry points are `sqlite3_backup_init()`, `sqlite3_backup_step()`, `sqlite3_backup_finish()`, `sqlite3_backup_remaining()`, and `sqlite3_backup_pagecount()`. Pager callbacks enter through `sqlite3BackupUpdate()` and `sqlite3BackupRestart()`. Internal helpers include `findDatabase()`, `setDestPgsz()`, `checkReadTransaction()`, `isFatalError()`, `backupOnePage()`, `backupTruncateFile()`, and `attachBackupObject()`. `sqlite3BtreeCopyFile()` wraps the same machinery for complete btree-to-btree copies when VACUUM support is compiled in.

## Control Flow

`sqlite3_backup_init()` validates distinct source and destination handles, locks both connection mutexes, resolves database names, opens TEMP if requested, rejects an active destination read transaction, initializes `iNext` to page 1, and increments the source btree backup count.

`sqlite3_backup_step()` locks the source connection, source btree, and destination connection. If no fatal error has occurred, it rejects source write transactions, opens a source read transaction if needed, sets destination page size before the first write, opens a destination write transaction, rejects incompatible WAL or memdb page-size combinations, reads the source page count, and copies up to `nPage` pages with `backupOnePage()`. On completion, it handles empty source databases, bumps the destination schema cookie, resets destination schemas, sets WAL version if needed, truncates or pads the destination image for differing page sizes, commits the destination transaction, and returns `SQLITE_DONE`. If not complete, it attaches the backup object to the source pager so later source changes can repair already copied pages.

`sqlite3_backup_finish()` removes the backup from the pager list, decrements backup count, rolls back any open destination btree transaction, reports final status on the destination handle, frees heap-backed backup handles, and leaves/possibly closes zombie connections.

## State And Persistence Behavior

Destination database pages are persisted through pager writes and btree commits. `backupOnePage()` writes source page bytes into destination page spans, invalidates btree page extra state, and patches the database-size field on page 1 during normal copy. The source remains readable through a read transaction while pages are copied. Once attached to the pager backup list, already-copied pages are updated in place by `backupUpdate()` if the source connection modifies them; external source changes call `sqlite3BackupRestart()` to reset `iNext` to 1.

`nRemaining` and `nPagecount` are updated by `backup_step()` and are explicitly not thread-safe to read concurrently. `p->rc` preserves fatal errors across calls while allowing retry on `SQLITE_BUSY` and `SQLITE_LOCKED`.

## Dependencies And Integration Points

This file is tightly coupled to btree and pager internals: page sizes, page counts, pending-byte pages, journal modes, memdb handling, transaction phases, schema cookies, pager backup linked lists, pager file controls, OS file truncate/write/sync, and shared-cache btree mutexes. It also integrates with API armor, TEMP database opening, connection error state, zombie close handling, and optional `SQLITE_OMIT_VACUUM`.

## Risks And Edge Cases

Important risks include deadlocks from incorrect mutex order, copying page 1 metadata incorrectly, pending-byte page handling, differing page-size truncation, WAL destination restrictions, source writes racing with incremental copy, and failure during the commit/truncate path. `sqlite3BtreeCopyFile()` uses a stack `sqlite3_backup` with `pDestDb == 0`, so API code has branches where ownership and locking differ from public backup handles. Destination use by another thread during backup is documented as unsafe even though source-side APIs take locks.

## Test Signals

Tests should cover incremental and all-at-once backups, backup retry after busy source write transactions, source updates to already copied pages, restart after external source modification, page-size mismatch behavior, WAL and memdb restrictions, empty databases, schema cookie changes, progress counters, finish status mapping from `SQLITE_DONE` to `SQLITE_OK`, TEMP source/destination names, OOM and IO errors, and VACUUM copy behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/backup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/bitvec.c -->
# sources/storage-engines/sqlite/src/bitvec.c

## Purpose

`bitvec.c` implements SQLite's fixed-size sparse-or-dense bitmap abstraction for page-number sets. It is used by pager and transaction code to remember pages that have been journaled or marked with properties such as "dont-write". Bits are numbered from 1, while the implementation normalizes internally to zero-based offsets.

## Important APIs, Types, And Functions

The public internal API consists of `sqlite3BitvecCreate()`, `sqlite3BitvecTest()`, `sqlite3BitvecTestNotNull()`, `sqlite3BitvecSet()`, `sqlite3BitvecClear()`, `sqlite3BitvecDestroy()`, and `sqlite3BitvecSize()`. Debug builds also expose `sqlite3ShowBitvec()`, and testable builds include `sqlite3BitvecBuiltinTest()`.

`struct Bitvec` is exactly `BITVEC_SZ` bytes, normally 512. It stores `iSize`, `nSet`, `iDivisor`, and a union with three representations: `aBitmap` for small dense vectors up to `BITVEC_NBIT`, `aHash` for sparse large vectors up to `BITVEC_MXHASH` entries, and `apSub` for recursive sub-bitmaps once the hash fills.

## Control Flow

Creation zeroes one fixed-size object and records its maximum bit. Test operations return false for NULL or out-of-range inputs, then descend through recursive sub-bitmaps when `iDivisor` is nonzero. Leaf tests either inspect a byte bitmap or probe the open-addressed hash table.

Set operations accept NULL as success, require valid one-based indexes by assertion, descend or allocate sub-bitmaps as needed, set a direct bitmap bit for small leaves, or insert the one-based value into the hash table. If hash occupancy reaches `BITVEC_MXHASH`, the node converts to recursive form: it stack-copies the old hash table, clears the union as sub-pointers, computes `iDivisor`, inserts the new bit, reinserts all old bits, and frees the stack allocation.

Clear operations are optimized for rarity. They descend to a leaf, clear direct bitmap bits in place, or rebuild the hash table from a caller-supplied temporary `BITVEC_SZ` buffer while omitting the cleared value. Destruction recursively frees sub-bitmaps and then the current node.

## State And Persistence Behavior

Bitvec state is in-memory only and is owned by callers. It records membership but not ordering. `nSet` is valid only for hash leaves. Recursive nodes divide the original bit range into fixed-size bins; sub-bitmaps are lazily allocated. Because clear requires external scratch storage, callers must provide a buffer large enough to hold the hash snapshot. No state is written directly to disk, but incorrect membership can affect pager journaling decisions and therefore durability.

## Dependencies And Integration Points

The file depends on SQLite allocation helpers (`sqlite3MallocZero`, `sqlite3_free`, `sqlite3StackAllocRaw`, `sqlite3StackFree`), integer typedefs, randomness and malloc for the built-in test, and debug printing. Pager users rely on the abstraction to efficiently handle common sparse sets and rare dense sets without allocating memory proportional to the database page count.

## Risks And Edge Cases

Key risks are one-based versus zero-based indexing, maximum `u32` sizes, hash-table wraparound, preserving values during hash-to-recursive conversion, and the unusual clear API that requires temporary storage from the caller. `sqlite3BitvecSet()` ORs reinsertion return codes during rehash, so OOM must be propagated without corrupting enough state to break cleanup. Very large databases exercise recursive `iDivisor` math and pending dense cases such as dropping a large table.

## Test Signals

`sqlite3BitvecBuiltinTest()` is the primary local signal. It compares the Bitvec against a linear byte-array reference across scripted set, clear, random set, random clear, induced mismatch, debug print, and compile-parameter operations. Additional pager-level tests should stress journaled-page tracking for small databases, sparse large databases, dense page sets, OOM during sub-bitmap allocation, and clears after rehash.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/bitvec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/btmutex.c -->
# sources/storage-engines/sqlite/src/btmutex.c

## Purpose

`btmutex.c` implements mutex entry and leave helpers for `Btree` and `BtShared` objects when shared cache is available. Its job is to make non-recursive `BtShared` mutexes appear recursively enterable at the `Btree` API boundary, while enforcing a global lock order across all btrees on a connection to avoid deadlocks.

## Important APIs, Types, And Functions

The main entry points are `sqlite3BtreeEnter()`, `sqlite3BtreeLeave()`, `sqlite3BtreeEnterAll()`, `sqlite3BtreeLeaveAll()`, `sqlite3BtreeEnterCursor()`, and, for threadsafe incremental blob builds, `sqlite3BtreeLeaveCursor()`. Debug-only assertions use `sqlite3BtreeHoldsMutex()`, `sqlite3BtreeHoldsAllMutexes()`, and `sqlite3SchemaMutexHeld()`.

Internal helpers are `lockBtreeMutex()`, `unlockBtreeMutex()`, `btreeLockCarefully()`, `btreeEnterAll()`, and `btreeLeaveAll()`. The key fields are `Btree.sharable`, `Btree.locked`, `Btree.wantToLock`, sorted `Btree.pNext/pPrev` links, `Btree.pBt`, `Btree.db`, `BtShared.mutex`, and `BtShared.db`.

## Control Flow

`sqlite3BtreeEnter()` first asserts that the connection mutex is already held and that the per-connection sharable btree list is sorted by `BtShared` address. Non-sharable btrees are no-ops. Sharable btrees increment `wantToLock`; if already locked, recursive entry returns immediately. Otherwise `btreeLockCarefully()` tries a nonblocking mutex acquire. On success it records the owning db and marks the btree locked.

If the try-lock fails, `btreeLockCarefully()` releases all currently held later locks in the same connection's sorted list, blocks on the requested lock, then reacquires later btrees that still have nonzero `wantToLock`. This preserves ascending `BtShared` lock order. `sqlite3BtreeLeave()` decrements `wantToLock` and releases the underlying mutex when the recursive count reaches zero.

`sqlite3BtreeEnterAll()` locks every sharable btree on the connection and sets `db->noSharedCache` when there were none, allowing future enter-all calls to skip the slow path. Leave-all mirrors this over all attached databases. In non-threadsafe shared-cache builds, only `BtShared.db` is assigned because mutex operations are compiled out.

## State And Persistence Behavior

The file manages synchronization state only; it does not persist database content. It mutates `Btree.wantToLock`, `Btree.locked`, `BtShared.db`, and `sqlite3.noSharedCache`. These fields protect schema and btree access elsewhere. Correctness depends on the connection mutex being held before these helpers run, because the shared-cache btree list and recursive counters are connection-local coordination structures.

## Dependencies And Integration Points

This code is compiled only when `SQLITE_OMIT_SHARED_CACHE` is not defined, with major branches for `SQLITE_THREADSAFE`. It depends on btree internal structures, SQLite mutex primitives, connection `aDb` entries, schema-to-index mapping, and incremental blob cursor ownership. Parser and schema code use enter-all before reading schemas across attached databases; pager/btree operations use enter/leave around individual shared btrees.

## Risks And Edge Cases

The central risk is deadlock or unlock imbalance. The sorted `pNext/pPrev` invariant, `wantToLock` reference count, and release/reacquire logic must remain consistent for all attached sharable btrees. Forgetting to hold the database mutex invalidates assumptions. `sqlite3SchemaMutexHeld()` treats TEMP schema specially because TEMP is connection-local. Non-threadsafe shared-cache builds still need `BtShared.db` updates even without mutexes, so replacing these functions with no-ops would break code that expects the owning db pointer.

## Test Signals

Signals include debug assertion coverage under shared-cache and threadsafe builds, concurrent connections sharing multiple btrees, enter-all/leave-all around schema parsing, recursive enter/leave nesting, incremental blob cursor entry, schema mutex assertions for main, temp, and attached schemas, and stress tests where two connections lock overlapping btree sets in different call orders without deadlock.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/btmutex.c -->
