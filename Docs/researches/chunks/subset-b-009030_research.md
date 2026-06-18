# sources/storage-engines/wiredtiger/test/3rdparty/sqlite3/sqlite3.c lines 137438-144608

## Chunk Scope

This chunk spans several logical SQLite amalgamation modules:

- The end of `insert.c`: final constraint recheck logic, `sqlite3CompleteInsertion()`, table/index cursor opening, and the `INSERT INTO ... SELECT * FROM ...` transfer optimization.
- `legacy.c`: the public `sqlite3_exec()` convenience wrapper.
- `loadext.c` plus embedded `sqlite3ext.h`: extension API dispatch table, dynamic extension loading, per-connection extension handle cleanup, load-extension enable flags, and global auto-extension registration/loading.
- The start and most of `pragma.c`: generated pragma metadata, helpers, `sqlite3Pragma()` dispatch, integrity checking code generation, pragma virtual table support, and `sqlite3PragmaVtabRegister()`.
- The start of `prepare.c`: schema initialization callback/loader, schema-cookie validation, parse object cleanup helpers, and the first part of `sqlite3Prepare()`/`sqlite3LockAndPrepare()`.

The source is third-party SQLite embedded under WiredTiger tests, so the code is vendor infrastructure rather than repository-native storage engine logic. Its integration surface is the SQLite C API and SQLite's internal VDBE, btree, schema, parser, pager, pragma, extension, and virtual table subsystems.

## Purpose

The chunk implements core database connection behavior around writes, execution, extension loading, pragmas, schema loading, and SQL preparation:

- Finish row insertion/update by emitting VDBE opcodes that insert index records and table records.
- Detect and fast-path compatible bulk table copies for `INSERT INTO dst SELECT * FROM src`.
- Provide `sqlite3_exec()` as a high-level loop over prepare/step/finalize for one or more SQL statements.
- Expose a stable ABI table for loadable SQLite extensions and manage loaded extension handles.
- Maintain process-wide auto-extension callbacks and invoke them for new database connections.
- Parse and compile PRAGMA statements into VDBE programs, including settings, schema introspection, integrity checks, WAL/checkpoint controls, heap/worker limits, and `PRAGMA optimize`.
- Represent PRAGMAs as eponymous virtual tables for queryable `pragma_*` table names.
- Load sqlite schema rows into internal `Table`, `Index`, `Trigger`, and `View` structures and start compiling SQL into VDBE statements.

## Important APIs, Types, and Functions

- `sqlite3CompleteInsertion()` at line 137593 emits final `OP_IdxInsert` and `OP_Insert` opcodes after constraint checks. It depends on `Table`, `Index`, index register array `aRegIdx`, cursor numbers, `OPFLAG_*` write flags, and preupdate hook support for WITHOUT ROWID tables.
- `sqlite3OpenTableAndIndices()` at line 137681 allocates/open cursors for a table and its indexes. It returns data and first-index cursor ids and treats rowid, WITHOUT ROWID, and virtual tables differently.
- `xferCompatibleIndex()` at line 137762 compares source/destination index metadata for transfer optimization compatibility: key/count shape, conflict behavior, columns or expressions, sort order, collation, and partial-index WHERE clause.
- `xferOptimization()` at line 137823 implements the raw-record transfer fast path for `INSERT INTO tab1 SELECT * FROM tab2`. It performs extensive syntax and schema compatibility checks, then emits VDBE copy loops for table and index btrees.
- `sqlite3_exec()` at line 138237 is the public convenience API that repeatedly calls `sqlite3_prepare_v2()`, `sqlite3_step()`, user callbacks, and `sqlite3VdbeFinalize()`.
- `struct sqlite3_api_routines` begins in the embedded extension header and is the loadable-extension ABI. New function pointers are appended to preserve binary compatibility.
- `sqlite3Apis` at line 139271 is the concrete static dispatch table passed into extensions. Compile-time omissions replace unavailable APIs with null pointers.
- `sqlite3LoadExtension()` at line 139623 opens a shared library through the VFS, finds an init symbol, calls it with `sqlite3Apis`, and appends the handle to `db->aExtension`.
- `sqlite3_load_extension()` at line 139784 is the public mutex-wrapped API for dynamic loading.
- `sqlite3CloseExtensions()` at line 139802 closes all dynamic-library handles owned by a database connection during connection close.
- `sqlite3_enable_load_extension()` at line 139815 toggles the connection flags `SQLITE_LoadExtension` and `SQLITE_LoadExtFunc`.
- `sqlite3_auto_extension()`, `sqlite3_cancel_auto_extension()`, `sqlite3_reset_auto_extension()`, and `sqlite3AutoLoadExtensions()` at lines 139864, 139914, 139942, and 139964 maintain and run a process-wide list of extension init callbacks protected by `SQLITE_MUTEX_STATIC_MAIN`.
- `PragmaName`, `pragCName[]`, and `aPragmaName[]` define the generated pragma lookup table and result column metadata.
- `sqlite3GetBoolean()` at line 140929 is a shared helper for boolean-like pragma values.
- `setPragmaResultColumnNames()`, `returnSingleInt()`, and `returnSingleText()` generate standard PRAGMA result metadata/rows.
- `sqlite3JournalModename()` and `pragmaLocate()` support journal-mode name mapping and binary search over the lexicographically sorted pragma table.
- `pragmaFunclistLine()` formats `PRAGMA function_list` output for built-in and connection-defined SQL functions.
- `integrityCheckResultRow()` is a VDBE codegen helper for integrity-check result emission and max-error limiting.
- `sqlite3Pragma()` at line 141077 is the central PRAGMA compiler. It normalizes schema/name/value tokens, calls authorization and VFS file-control hooks, resolves the pragma entry, optionally loads schema, then dispatches by `PragTyp_*`.
- `PragmaVtab` and `PragmaVtabCursor` model eponymous virtual tables that execute PRAGMA statements underneath.
- `pragmaVtabConnect()`, `pragmaVtabBestIndex()`, `pragmaVtabFilter()`, `pragmaVtabNext()`, `pragmaVtabColumn()`, and `sqlite3PragmaVtabRegister()` at lines 143453-143731 implement the virtual table facade over PRAGMAs.
- `corruptSchema()`, `sqlite3IndexHasDuplicateRootPage()`, `sqlite3InitCallback()`, `sqlite3InitOne()`, `sqlite3Init()`, and `sqlite3ReadSchema()` at lines 143761-144217 build and validate in-memory schema state from `sqlite_schema`.
- `schemaIsValid()` compares stored schema cookies with btree metadata and resets stale schemas.
- `sqlite3SchemaToIndex()` maps a `Schema *` back to `db->aDb[]`.
- `sqlite3ParseObjectReset()`, `sqlite3ParserAddCleanup()`, and `sqlite3ParseObjectInit()` manage parser-lifetime allocations and cleanup hooks.
- `sqlite3Prepare()` at line 144427 is the internal compiler entry point; this chunk includes setup, schema-lock checks, parser invocation, error handling, and parser cleanup.
- `sqlite3LockAndPrepare()` starts at line 144590 and wraps prepare under the connection mutex and all btree mutexes, retrying transient prepare errors.

## Control Flow

### Insert Completion and Transfer Optimization

The chunk begins in the tail of constraint checking. It copies previously emitted uniqueness-check opcodes to recheck constraints after `REPLACE` triggers, bypasses partial indexes when their predicate register is null, and emits aborts if a replacement trigger caused a new uniqueness violation. It then optionally generates a row record with `OP_MakeRecord` for rowid tables and sets null-trim metadata through `sqlite3SetMakeRecordP5()` when enabled.

`sqlite3CompleteInsertion()` assumes constraint checks and index key generation already happened. It loops over `pTab->pIndex`, skips unused index registers, bypasses partial indexes via `OP_IsNull`, sets `OPFLAG_USESEEKRESULT` when allowed, and adds `OP_IdxInsert`. For a WITHOUT ROWID primary key it adds change-count/save-position flags and may call `codeWithoutRowidPreupdate()` for INSERT preupdate hook delivery. Rowid tables finish with one `OP_Insert` into `iDataCur`, using flags for nested writes, change counting, last-rowid tracking, append bias, and seek-result reuse.

`sqlite3OpenTableAndIndices()` centralizes cursor allocation. Virtual tables are a no-op and output illegal cursor numbers for detection. Rowid tables open the base table first and then all indexes. WITHOUT ROWID tables treat the primary key index as the canonical data cursor. If shared cache is enabled and a rowid table is not opened, the function still emits table locks.

`xferOptimization()` first rejects unsupported SELECT shapes: CTEs, multiple FROM entries, subqueries, WHERE/ORDER/GROUP/LIMIT/compound/DISTINCT, and anything other than a single `*` result expression. It then checks schema compatibility for rowid mode, ordinary-table status, column count, INTEGER PRIMARY KEY, STRICTness, hidden/generated columns, affinity, collation, NOT NULL strength, defaults, indexes, CHECK constraints, foreign keys, and `count_changes`. If accepted, it emits VDBE loops that copy raw table records or index records from source btrees to destination btrees, using faster `OP_RowCell`, `OP_SeekEnd`, `OPFLAG_PREFORMAT`, and `OPFLAG_APPEND` paths under VACUUM or sorted binary-collation cases. When safety requires an initially empty destination, it emits a runtime emptiness test and returns false so the caller can also compile the ordinary insertion fallback.

### `sqlite3_exec()`

`sqlite3_exec()` validates the database handle, converts null SQL to an empty string, takes `db->mutex`, clears prior error state, and loops until the SQL string is exhausted. Each statement is prepared with `sqlite3_prepare_v2()`. Whitespace/comment-only fragments advance to the returned tail. For real statements it steps until completion, lazily allocates `azCols` as a `2*nCol+1` array, stores column names in the first half and row text values in the second half, and calls the user callback for each row. If `SQLITE_NullCallback` is set and a statement returns no rows, it can invoke the callback once with column names but no values. Non-zero callback return aborts execution with `SQLITE_ABORT`. On exit it finalizes any active statement, frees callback column storage, maps the result through `sqlite3ApiExit()`, and optionally returns an allocated error string.

### Extension Loading

The embedded `sqlite3ext.h` section defines the ABI surface extensions use. The core build disables API macro redirection with `SQLITE_CORE`, while loadable extension builds map public names to `sqlite3_api->...`.

`sqlite3LoadExtension()` requires `SQLITE_LoadExtension` on the connection, rejects oversized and empty filenames, and opens the library via `sqlite3OsDlOpen()`. On Unix/Windows it retries with platform suffixes when the exact file name fails. It resolves the requested entry point or defaults to `sqlite3_extension_init`; if that default is absent, it derives `sqlite3_X_init` from the filename by dropping directory, optional `lib`, and suffix, lowercasing ASCII letters. It calls the entry point as `xInit(db, &zErrmsg, &sqlite3Apis)`. `SQLITE_OK_LOAD_PERMANENTLY` means success without retaining the handle. Other init failures close the handle. Successful loads append the handle to `db->aExtension`, replacing the old handle array.

Auto-extension registration uses the global `sqlite3Autoext` state vector, or an indirection macro when writable static data is omitted. Registration initializes SQLite, takes the static main mutex, deduplicates callbacks, and appends via `sqlite3_realloc64()`. Cancellation removes a matching callback by swapping with the last element. Reset frees the whole array. `sqlite3AutoLoadExtensions()` reads one callback at a time under the static mutex, releases the mutex while calling extension code, and stops on an error after storing a connection error message.

### PRAGMA Dispatch

The generated pragma table maps names to `PragTyp_*`, flags, result-column metadata, and type-specific arguments. `sqlite3Pragma()` compiles a PRAGMA into VDBE bytecode:

1. It creates a VDBE with `sqlite3GetVdbe()`, marks it run-once, parses optional schema qualification, opens temp schema if explicitly requested, and materializes left/right token strings.
2. It checks authorization with `SQLITE_PRAGMA`.
3. It gives the VFS first chance through `SQLITE_FCNTL_PRAGMA`; a successful VFS response becomes a one-column result, non-`SQLITE_NOTFOUND` errors become parse errors.
4. It binary-searches `aPragmaName[]`, optionally reads schema, and sets result column names unless the pragma suppresses columns.
5. It switches on the pragma type and emits code or directly mutates connection fields.

The included cases cover pager settings (`page_size`, `cache_size`, `cache_spill`, `mmap_size`, `secure_delete`, `journal_mode`, `journal_size_limit`, `locking_mode`, `synchronous`), vacuum/autovacuum controls, temp/data directory state, boolean connection flags, schema introspection (`table_info`, `table_list`, `index_info`, `index_list`, `database_list`, `collation_list`, `function_list`, `module_list`, `pragma_list`), foreign key introspection/checking, `case_sensitive_like`, integrity/quick checks, encoding, header cookies, compile options, WAL checkpoint/autocheckpoint, heap limits, worker thread limit, `analysis_limit`, debug lock status, and `PRAGMA optimize`.

`PRAGMA integrity_check` and `quick_check` generate one of the densest VDBE programs in this chunk. They collect btree root pages, run `OP_IntegrityCk`, compare table/index entry counts, verify WITHOUT ROWID primary key order, validate column storage classes and NOT NULL rules, evaluate CHECK constraints, verify index entries and UNIQUE keys, and invoke virtual-table `xIntegrity` for module version 4 tables. Quick check skips the more expensive index validation paths.

`PRAGMA optimize` scans eligible ordinary user tables, checks whether stats were used or missing, compares current table size against `sqlite_stat1` estimates, and emits either debug rows or `OP_SqlExec` ANALYZE statements. It bounds analysis work with `SQLITE_DEFAULT_OPTIMIZE_LIMIT` and scales the limit down for schemas with many btrees.

### PRAGMA Virtual Tables

`sqlite3PragmaVtabRegister()` recognizes `pragma_<name>` module names for pragmas that have queryable result forms. `pragmaVtabConnect()` declares a virtual table schema from the pragma's result columns plus hidden `arg` and/or `schema` columns. `pragmaVtabBestIndex()` encourages equality constraints on hidden parameters by assigning very high cost when the required first hidden argument is unconstrained. `pragmaVtabFilter()` builds a safe quoted PRAGMA SQL string from hidden arguments, prepares it, and advances to the first row. Columns before `iHidden` proxy `sqlite3_column_value()` from the prepared PRAGMA; hidden columns return captured argument text.

### Schema Loading and Prepare

`sqlite3InitCallback()` is the callback used by schema initialization. For CREATE statements from `sqlite_schema`, it runs `sqlite3Prepare()` while `db->init.busy` is set so parsing creates in-memory schema objects without executable VDBE output. For implicit indexes with blank SQL text, it finds the existing index and records its root page. `corruptSchema()` centralizes error text and respects malloc failure, ALTER TABLE context, `SQLITE_WriteSchema`, and extra schema checks.

`sqlite3InitOne()` creates the in-memory schema table definition, opens a read transaction if needed, reads btree metadata, sets schema cookie, encoding, cache size, file format, and legacy file-format flags, then executes `SELECT*FROM"<db>".sqlite_schema ORDER BY rowid` through `sqlite3_exec()` with `sqlite3InitCallback()`. It loads ANALYZE statistics on success and marks `DB_SchemaLoaded` when acceptable, including the special `SQLITE_NoSchemaError` path used to inspect corrupt schema tables.

`sqlite3Init()` loads main first, then attached schemas in reverse order with temp last, and commits internal schema changes when appropriate. `sqlite3ReadSchema()` is the parser-facing no-op-or-load wrapper. `schemaIsValid()` opens temporary read transactions if needed, compares btree schema cookies to in-memory schema cookies, resets stale schemas, and sets `SQLITE_SCHEMA`.

`sqlite3Prepare()` initializes a stack `Parse`, optionally disables lookaside for persistent statements, checks shared-cache schema locks across btrees, unlocks pending virtual-table disconnects, copies unterminated SQL when a byte count is provided, runs the parser, stores statement SQL text, finalizes failed VDBEs, transfers the compiled VDBE to `*ppStmt` on success, deletes trigger-program allocations, and resets parser-owned cleanup state. `sqlite3LockAndPrepare()` begins the public-facing lock wrapper, taking the database mutex and all btree mutexes and retrying through `sqlite3Prepare()`.

## State and Persistence Behavior

- Table and index writes are persisted through VDBE btree opcodes (`OP_Insert`, `OP_IdxInsert`) emitted by insert codegen, not directly by these C functions.
- Transfer optimization copies raw btree cells/records and can update autoincrement state with `autoIncBegin()` and `autoIncStep()`. It emits an `sqlite3AutoincrementEnd()` call path when an empty-destination fallback is needed.
- PRAGMA handlers modify a mix of in-memory connection state and persistent database header cookies. Persistent examples include default cache size, autovacuum metadata, and header values such as schema/user/application ids. In-memory examples include `db->temp_store`, `db->flags`, `db->busyTimeout`, `db->nAnalysisLimit`, `db->dfltLockMode`, mmap limit, heap limits, and WAL autocheckpoint callbacks.
- Dynamic extension handles persist for the lifetime of a connection in `db->aExtension` and are closed by `sqlite3CloseExtensions()`.
- Auto-extension callbacks are process-global mutable state in `sqlite3Autoext`, guarded by the static main mutex.
- Schema initialization persists no new database content during normal reads, but builds in-memory schema state and may load stats. It uses btree metadata to set `Schema` fields and schema loaded flags.
- `sqlite3_exec()` owns temporary callback arrays and error message allocations. Returned error strings are allocated outside the connection db allocator (`sqlite3DbStrDup(0, ...)`) for caller ownership.
- Parser cleanup state is explicit through `ParseCleanup` links and is guaranteed to run in `sqlite3ParseObjectReset()`, including immediate cleanup on allocation failure in `sqlite3ParserAddCleanup()`.

## Dependencies and Integration Points

- VDBE opcode generation is pervasive: `sqlite3VdbeAddOp*`, labels, P4 payloads, `VdbeCoverage`, result rows, `OP_SqlExec`, `OP_Checkpoint`, `OP_IntegrityCk`, and many cursor operations.
- Btree/pager integration includes table/index opens, schema metadata reads/writes, transactions, page size, auto-vacuum, cache, mmap, locking, journaling, WAL, and secure-delete controls.
- Parser integration includes `Parse`, token/name conversion, schema reads, authorization, self-table expression codegen, and statement preparation.
- Extension loading depends on VFS dynamic-link methods (`sqlite3OsDlOpen`, `sqlite3OsDlSym`, `sqlite3OsDlError`, `sqlite3OsDlClose`) and ABI stability of `sqlite3_api_routines`.
- Virtual table integration appears both in extension/module APIs and in PRAGMA virtual table support, including `sqlite3_declare_vtab`, `sqlite3VtabCreateModule`, and virtual table integrity callbacks.
- Shared-cache and mutex behavior is central: connection mutexes, btree mutexes, schema locks, tempdir mutex, and static main mutex protect different state classes.
- Compile-time feature flags heavily alter behavior and ABI slots, including `SQLITE_OMIT_*`, `SQLITE_ENABLE_PREUPDATE_HOOK`, `SQLITE_ENABLE_COLUMN_METADATA`, `SQLITE_ENABLE_NORMALIZE`, `SQLITE_ENABLE_CEROD`, `SQLITE_DEBUG`, and platform macros.
- WiredTiger integration is indirect: this file provides the bundled SQLite implementation used by test third-party code, so behavioral changes here can affect any tests or helper tools using SQLite APIs.

## Risks and Edge Cases

- Insert REPLACE recheck logic copies existing VDBE opcodes after possible opcode-array reallocations; the code explicitly copies whole `VdbeOp` values to avoid dangling pointers. Any edit here risks constraint enforcement regressions.
- `sqlite3CompleteInsertion()` relies on the caller's `aRegIdx` layout and assumes all REPLACE indexes are ordered at the end of `pTab->pIndex`. Violating those invariants could corrupt index writes or change conflict behavior.
- Transfer optimization is intentionally conservative. Relaxing compatibility checks can silently bypass column decoding, generated-column omission semantics, triggers, FK behavior, uniqueness checks, or rowid remapping requirements.
- The transfer path has separate VACUUM and non-VACUUM behavior. `OPFLAG_PREFORMAT`, `OP_RowCell`, and `OP_SeekEnd` are only safe when the source cell format/order assumptions hold.
- `sqlite3_exec()` callbacks receive pointers into statement-owned memory and column-name storage. Finalization invalidates those pointers. Callback abort and OOM paths must finalize exactly once and free `azCols`.
- Extension loading is security-sensitive. Loading is disabled by default, empty filenames are rejected, path length is bounded to avoid `dlopen()` crashes, and fallback entry point derivation must not overflow.
- `sqlite3Apis` order is ABI-critical. New extension APIs must be appended, never inserted, and omitted features must leave compatible null slots.
- Auto-extension callbacks are global and run outside the static mutex. This avoids deadlocks but means registration/cancellation can race with iteration in controlled ways; the loop rereads under mutex each iteration.
- PRAGMA handlers mix direct connection mutation and deferred VDBE effects. Transaction restrictions, defensive mode restrictions, schema reloads, and `OP_Expire` invalidation are important for correctness.
- `PRAGMA temp_store_directory` and `data_store_directory` mutate global directory pointers under a static mutex and are disabled under `SQLITE_OMIT_WSD`; they can invalidate temp storage and reset schemas.
- Integrity-check code has many generated jumps and temp registers. Type-check masks, virtual/generated columns, default handling, STRICT semantics, and WITHOUT ROWID primary-key order are easy regression points.
- Schema loading parses SQL from `sqlite_schema` while `db->init.busy` changes parser behavior. Corrupt schema handling varies under `SQLITE_WriteSchema`, ALTER TABLE contexts, and `SQLITE_NoSchemaError`.
- `sqlite3Prepare()` must reset parser state on every exit. Early cleanup on OOM is deliberate to avoid leaked parser-owned objects but creates use-after-free risk if callers keep using a cleaned pointer.

## Test Signals

Useful test coverage for this chunk includes:

- INSERT/UPDATE tests covering rowid and WITHOUT ROWID tables, partial indexes, UNIQUE conflicts, `ON CONFLICT REPLACE`, triggers that perform replacement, generated columns, STRICT tables, preupdate hooks, and `last_insert_rowid`/change-count behavior.
- Transfer optimization tests using `sqlite3_xferopt_count` under `SQLITE_TEST`, including accepted simple copies, fallback when destination is non-empty, and rejection for mismatched indexes, collations, defaults, generated expressions, CHECK constraints, FKs, STRICTness, hidden columns, CTEs, WHERE/ORDER/GROUP/LIMIT/DISTINCT, and virtual tables.
- `sqlite3_exec()` tests for multi-statement SQL, whitespace/comment tails, row callbacks, empty-result callbacks, callback abort, OOM in callback column allocation, prepare errors, step errors, and returned error message ownership.
- Extension tests for disabled loading, enabling/disabling C API and SQL-function loading, suffix fallback, alternate entry point derivation, init failure cleanup, permanent extensions, close-time handle cleanup, and omitted API null slots.
- Auto-extension tests for deduplication, cancellation, reset, initialization failure propagation, and thread-safety under concurrent registration/loading.
- PRAGMA tests for every table entry in `aPragmaName[]`, unknown pragma no-op behavior, VFS `SQLITE_FCNTL_PRAGMA` override behavior, authorization denial, schema-qualified forms, result column names, and `PragFlg_NoColumns1` debug assertions.
- Pager/state PRAGMA tests for transaction restrictions, defensive-mode restrictions, persistence of header cookies, WAL checkpoint modes, mmap limits, temp store invalidation, lock status, heap limits, worker thread limits, and statement expiration after flag changes.
- Integrity-check tests with corrupt btrees, missing index entries, wrong index counts, duplicate UNIQUE entries, rowid encoding errors, non-BINARY collation mismatch, STRICT type violations, NOT NULL/NaN handling, CHECK failures, WITHOUT ROWID order violations, quick-check omissions, and virtual-table `xIntegrity`.
- Schema loading/prepare tests for malformed `sqlite_schema`, orphan indexes/triggers, duplicate index root pages, invalid root pages with extra checks, encoding mismatch on ATTACH, schema cookie mismatch, shared-cache schema lock failures, SQL length limit, persistent prepare lookaside disabling, retry-on-`SQLITE_ERROR_RETRY`, and parser cleanup under OOM fault injection.

## Cross-Chunk Notes

- The line range starts in the middle of the function that generated constraint checks before insertion; earlier setup for registers, conflict policy, and labels is outside this chunk.
- `sqlite3LockAndPrepare()` continues beyond line 144608, so retry completion, btree leave/unlock behavior, and public prepare wrappers are covered by later chunks.
- Many PRAGMA cases depend on helper functions and VDBE opcodes defined elsewhere in the amalgamation; this chunk contains their dispatch and code generation, not the lower-level pager/btree implementations.
