# sources/storage-engines/foundationdb/contrib/sqlite/sqlite3.amalgamation.c lines 60570-68379

## Chunk Scope

This chunk is a wide band of SQLite amalgamation code embedded under the FoundationDB storage-engine tree. It starts at the end of `analyze.c` statistics loading, covers complete embedded sections for `attach.c`, `auth.c`, `build.c`, `callback.c`, `delete.c`, and `func.c`, and ends part-way into `fkey.c` at the beginning of `fkScanChildren()`.

The source is not FoundationDB-specific glue in this range. It is SQLite core implementation code: parser actions, schema metadata management, SQL function registration, DELETE code generation, ATTACH/DETACH, authorizer hooks, collation/function lookup, and the start of foreign-key enforcement code.

## Purpose

The code in this chunk turns parsed SQL syntax into SQLite runtime state and VDBE bytecode. Its main responsibilities are:

- loading planner statistics from `sqlite_stat1` and optional `sqlite_stat2`;
- implementing `ATTACH`/`DETACH` and the database-name fixer used by views, triggers, and indexes;
- enforcing `sqlite3_set_authorizer()` decisions during parse/code generation;
- creating, dropping, and maintaining schema objects such as tables, views, indexes, foreign-key declarations, source lists, and transactions;
- maintaining in-memory schema hashes, table/index reference lifetimes, schema cookies, and shared-cache table locks;
- implementing DELETE statement code generation, row deletion, index-key deletion, and trigger/foreign-key hooks;
- defining SQLite built-in scalar and aggregate SQL functions and registering LIKE/GLOB optimization metadata;
- resolving parent indexes and generating early VDBE checks for foreign-key constraints.

## Important APIs, Types, And Functions

### Statistics Loading

- The opening tail of the `ANALYZE` implementation checks for `sqlite_stat1`, executes `SELECT tbl, idx, stat FROM %Q.sqlite_stat1`, and passes rows to `analysisLoader`.
- Under `SQLITE_ENABLE_STAT2`, it loads samples from `sqlite_stat2` into `Index.aSample`, allocating `SQLITE_INDEX_SAMPLES` `IndexSample` slots per index. Numeric samples store `u.r`; text/blob samples store up to 24 bytes.

### ATTACH, DETACH, And Database Fixing

- `resolveAttachExpr()` treats bare identifiers at the root of ATTACH/DETACH expressions as string literals and rejects non-constant resolved expressions.
- `attachFunc()` is the runtime SQL function behind compiled `ATTACH`. It validates attached database limits, autocommit state, duplicate database names, opens a Btree with `sqlite3BtreeOpen()`, obtains schema with `sqlite3SchemaGet()`, checks text encoding compatibility, applies locking/secure-delete settings, optionally attaches codec keys, initializes schema with `sqlite3Init()`, and rolls back the new `Db` entry on failure.
- `detachFunc()` validates that the named database exists, is not `main` or `temp`, is not inside a transaction, and has no active read transaction or backup before closing the Btree and resetting internal schema.
- `codeAttach()`, `sqlite3Attach()`, and `sqlite3Detach()` compile SQL syntax into an `OP_Function` call to the internal `sqlite_attach` or `sqlite_detach` function, followed by `OP_Expire`.
- `sqlite3FixInit()`, `sqlite3FixSrcList()`, `sqlite3FixSelect()`, `sqlite3FixExpr()`, `sqlite3FixExprList()`, and `sqlite3FixTriggerStep()` enforce that non-TEMP views, triggers, and indexes do not reference objects in other databases.

### Authorization

- `sqlite3_set_authorizer()` installs or clears the connection authorizer callback and expires prepared statements.
- `sqlite3AuthReadCol()` invokes `xAuth` for `SQLITE_READ`; `SQLITE_DENY` records an auth error, while malformed return codes become "authorizer malfunction".
- `sqlite3AuthRead()` maps a `TK_COLUMN` or trigger pseudo-column expression to a table/column name and converts it to `TK_NULL` when the authorizer returns `SQLITE_IGNORE`.
- `sqlite3AuthCheck()` is the general parse-time authorization gate for CREATE/DROP/INSERT/DELETE/TRANSACTION/SAVEPOINT/etc. It is skipped during schema initialization and inside `sqlite3_declare_vtab`.
- `sqlite3AuthContextPush()` and `sqlite3AuthContextPop()` track view/trigger context passed to the authorizer.

### Schema Build And Parser Actions

- `sqlite3BeginParse()` initializes parse flags for a new statement.
- `sqlite3TableLock()` and `codeTableLocks()` record and emit shared-cache `OP_TableLock` requirements.
- `sqlite3FinishCoding()` finalizes a statement VDBE: emits `OP_Halt`, fills the deferred schema-cookie/transaction prologue, starts virtual table transactions, emits table locks, starts AUTOINCREMENT tracking, jumps back to executable code, and calls `sqlite3VdbeMakeReady()`.
- `sqlite3NestedParse()` recursively parses generated SQL used for schema changes, preserving the outer parse state.
- Lookup and lifetime APIs include `sqlite3FindTable()`, `sqlite3LocateTable()`, `sqlite3FindIndex()`, `sqlite3UnlinkAndDeleteIndex()`, `sqlite3ResetInternalSchema()`, `sqlite3CommitInternalChanges()`, `sqlite3DeleteTable()`, and `sqlite3UnlinkAndDeleteTable()`.
- Name/schema helpers include `sqlite3NameFromToken()`, `sqlite3OpenMasterTable()`, `sqlite3FindDbName()`, `sqlite3FindDb()`, `sqlite3TwoPartName()`, and `sqlite3CheckObjectName()`.
- CREATE TABLE/VIEW helpers include `sqlite3StartTable()`, `sqlite3AddColumn()`, `sqlite3AddNotNull()`, `sqlite3AffinityType()`, `sqlite3AddColumnType()`, `sqlite3AddDefaultValue()`, `sqlite3AddPrimaryKey()`, `sqlite3AddCheckConstraint()`, `sqlite3AddCollateType()`, `sqlite3ChangeCookie()`, `createTableStmt()`, `sqlite3EndTable()`, `sqlite3CreateView()`, and `sqlite3ViewGetColumnNames()`.
- Drop and storage-maintenance helpers include `sqliteViewResetAll()`, `sqlite3RootPageMoved()`, `destroyRootPage()`, `destroyTable()`, and `sqlite3DropTable()`.
- Foreign-key declaration parser actions in this chunk are `sqlite3CreateForeignKey()` and `sqlite3DeferForeignKey()`.
- Index and source-list helpers include `sqlite3RefillIndex()`, `sqlite3CreateIndex()`, `sqlite3DefaultRowEst()`, `sqlite3DropIndex()`, `sqlite3ArrayAllocate()`, `sqlite3IdListAppend()`, `sqlite3IdListDelete()`, `sqlite3IdListIndex()`, `sqlite3SrcListEnlarge()`, `sqlite3SrcListAppend()`, `sqlite3SrcListAssignCursors()`, `sqlite3SrcListDelete()`, `sqlite3SrcListAppendFromTerm()`, `sqlite3SrcListIndexedBy()`, and `sqlite3SrcListShiftJoinType()`.
- Transaction/codegen helpers include `sqlite3BeginTransaction()`, `sqlite3CommitTransaction()`, `sqlite3RollbackTransaction()`, `sqlite3Savepoint()`, `sqlite3OpenTempDatabase()`, `sqlite3CodeVerifySchema()`, `sqlite3BeginWriteOperation()`, `sqlite3MultiWrite()`, `sqlite3MayAbort()`, `sqlite3HaltConstraint()`, `sqlite3Reindex()`, and `sqlite3IndexKeyinfo()`.

### Collations, Functions, And Schema Allocation

- `sqlite3GetCollSeq()`, `sqlite3FindCollSeq()`, and `sqlite3CheckCollSeq()` resolve collations, call collation-needed callbacks, synthesize missing encodings where possible, and report unresolved collations.
- `sqlite3FuncDefInsert()` and `sqlite3FindFunction()` manage per-connection and global function-definition hash tables, including preferred encoding and arity matching.
- `sqlite3SchemaFree()` clears schema hash tables and deletes triggers, tables, indexes, and foreign-key hash content. `sqlite3SchemaGet()` obtains or initializes a `Schema` associated with a Btree.

### DELETE Code Generation

- `sqlite3SrcListLookup()` resolves the target table in a one-entry source list.
- `sqlite3IsReadOnly()` rejects writes to virtual tables without `xUpdate`, protected system tables without writable-schema mode, and views when triggers are not allowed.
- `sqlite3MaterializeView()` realizes a view into an ephemeral table for INSTEAD OF trigger processing.
- `sqlite3LimitWhere()` rewrites limited DELETE/UPDATE syntax into a `rowid IN (SELECT rowid ... ORDER BY ... LIMIT/OFFSET ...)` expression when enabled.
- `sqlite3DeleteFrom()` compiles DELETE: resolves target, checks triggers/views/read-only/auth, assigns cursors, optionally uses truncate optimization, otherwise collects rowids in a RowSet, opens write cursors, deletes rows, fires triggers, handles virtual tables, updates AUTOINCREMENT, and optionally returns a row count.
- `sqlite3GenerateRowDelete()` handles a single row delete with BEFORE/AFTER triggers, OLD register population, foreign-key checks/actions, index deletion, table row deletion, and skip labels for trigger-side row removal or `RAISE(IGNORE)`.
- `sqlite3GenerateRowIndexDelete()` and `sqlite3GenerateIndexKey()` build and delete index keys for the current table row.

### Built-In SQL Functions

The `func.c` section defines scalar functions such as `min/max` scalar variants, `typeof`, `length`, `abs`, `substr`, `round`, `upper`, `lower`, `random`, `randomblob`, `last_insert_rowid`, `changes`, `total_changes`, `like`, `glob`, `nullif`, `sqlite_version`, `sqlite_source_id`, compile-option diagnostics, `quote`, `hex`, `zeroblob`, `replace`, `trim/ltrim/rtrim`, optional `soundex`, and optional `load_extension`.

Aggregate state is implemented by `SumCtx` for `sum`, `total`, and `avg`, `CountCtx` for `count`, a `Mem` aggregate accumulator for aggregate `min/max`, and `StrAccum` for `group_concat`.

Registration functions are `sqlite3RegisterBuiltinFunctions()`, `sqlite3RegisterLikeFunctions()`, `sqlite3IsLikeFunction()`, and `sqlite3RegisterGlobalFunctions()`.

### Foreign-Key Enforcement Start

- `locateFkeyIndex()` finds the required parent key for a foreign key. It accepts a single-column INTEGER PRIMARY KEY parent without an index, otherwise requires a UNIQUE/PRIMARY KEY index with matching columns and default column collations. For composite keys it may allocate an `aiCol` map from parent-index order to child-column indexes.
- `fkLookupParent()` emits VDBE code for child-side INSERT/DELETE/UPDATE checks. It skips checks for NULL child key columns, looks up parent rows by rowid or unique index, handles self-referential insert matches, and either halts immediately for simple immediate single-row inserts or adjusts `OP_FkCounter`.
- `fkScanChildren()` begins parent-side scan code generation for DELETE/UPDATE checks and deferred insert resolution. This chunk ends while it is building and resolving the WHERE expression matching child rows to the parent key.

## Control Flow

ATTACH flow is parse-time compilation plus runtime execution. The parser calls `sqlite3Attach()` or `sqlite3Detach()`, which delegates to `codeAttach()`. `codeAttach()` resolves constant expressions, runs authorization, materializes function arguments into registers, emits `OP_Function`, and expires statements. At runtime, `attachFunc()` mutates `db->aDb` and opens/initializes the new Btree/schema; `detachFunc()` closes and removes a database after lock and transaction checks.

Schema creation flows through parser actions. `sqlite3StartTable()` resolves the target database, checks authorization and namespace collisions, allocates a `Table`, and reserves a placeholder row in `sqlite_master` when not initializing. Column/constraint helpers mutate `pParse->pNewTable`. `sqlite3EndTable()` resolves CHECK constraints, creates/populates CTAS output if needed, updates the placeholder `sqlite_master` row with final SQL text, bumps the schema cookie, creates `sqlite_sequence` if needed, schedules schema reparse, or inserts the table directly into in-memory hashes during initialization.

Index creation follows a similar two-mode path. `sqlite3CreateIndex()` resolves table and database names, blocks system/view/virtual-table indexing, derives or invents an index name, authorizes the operation, builds an `Index` object with column mappings/collations/sort order, suppresses duplicate automatic constraints, inserts initialization-time indexes into schema hashes, or emits VDBE to create/refill/persist a new index and parse the schema. `sqlite3DropIndex()` deletes `sqlite_master` and `sqlite_stat1` rows, changes the schema cookie, destroys the root page, and emits `OP_DropIndex`.

DROP TABLE resolves the object, checks type compatibility (`DROP TABLE` vs `DROP VIEW`), authorizes deletes from schema and table, rejects `sqlite_` system tables, begins a write operation, drops triggers, foreign-key side effects, AUTOINCREMENT rows, master-table entries, optional analyze stats, table/index root pages, virtual-table storage, schema cookies, and in-memory view column caches.

DELETE compilation first resolves the target table/view and associated triggers. It uses a fast `OP_Clear` path only when there is no WHERE clause, no triggers, no virtual table, and no required foreign-key work. Otherwise it scans matching rows into a RowSet, then performs row deletes after the scan to avoid changing scan order. Per-row deletion calls trigger and foreign-key code around physical index/table deletion.

Built-in function flow is callback-based. Scalar functions inspect `sqlite3_value` arguments and return via `sqlite3_result_*`. Aggregate steps allocate state with `sqlite3_aggregate_context()` and finalizers produce the final result. Function lookup uses hash buckets keyed by case-folded first character plus name length, then scores arity and encoding compatibility.

Foreign-key flow starts by validating the parent key with `locateFkeyIndex()`. Child-row changes use `fkLookupParent()` to find the referenced parent or adjust immediate/deferred counters. Parent-row changes use `fkScanChildren()` to generate a WHERE scan over child rows that reference the old/new parent key.

## State And Persistence Behavior

Persistent database state touched by this chunk includes:

- attached database files and their Btree/Pager handles;
- `sqlite_master` / `sqlite_temp_master` records for tables, views, indexes, triggers, and schema SQL text;
- table and index root pages created, cleared, destroyed, or moved by auto-vacuum;
- `sqlite_sequence` rows for AUTOINCREMENT tables;
- `sqlite_stat1` rows and optional `sqlite_stat2` samples;
- schema cookies (`BTREE_SCHEMA_VERSION`), file format cookies, and text-encoding cookies.

Important in-memory state includes:

- `sqlite3.aDb[]`, including dynamic expansion beyond `aDbStatic` and compaction after detach/reset;
- `Schema` hash tables for tables, indexes, triggers, and foreign keys;
- `Table`, `Column`, `Index`, `FKey`, `FuncDef`, `CollSeq`, `KeyInfo`, `SrcList`, `IdList`, `Expr`, `Select`, and `Vdbe` structures;
- parse flags such as `cookieMask`, `writeMask`, `isMultiWrite`, `mayAbort`, `nTab`, `nMem`, `pNewTable`, and authorization context;
- per-statement and deferred foreign-key counters stored in VDBE/database state;
- aggregate contexts and function result buffers for SQL functions.

The code is careful to distinguish initialization (`db->init.busy`) from user-issued DDL. During schema loading it avoids writing disk state and instead populates in-memory hashes from existing `sqlite_master` rows. During user DDL it emits VDBE bytecode to update persistent schema tables, then schedules schema reparse and expires prepared statements where needed.

Memory ownership is explicit and local. Most parser helper APIs consume token-derived strings or expression/source-list objects and clean them on exit. Several structures pack variable-length arrays and strings into one allocation (`Index`, `FKey`, `KeyInfo`). OOM generally sets `db->mallocFailed` and propagates `SQLITE_NOMEM` or parse errors.

## Dependencies And Integration Points

This chunk integrates with most core SQLite subsystems:

- Btree/Pager: `sqlite3BtreeOpen`, `sqlite3BtreeClose`, `sqlite3BtreePager`, `sqlite3BtreeSecureDelete`, `sqlite3BtreeSchema`, `sqlite3BtreeSetPageSize`, root-page creation/destruction, schema cookies.
- VDBE: emits opcodes including `OP_Function`, `OP_Expire`, `OP_TableLock`, `OP_Halt`, `OP_Transaction`, `OP_VerifyCookie`, `OP_VBegin`, `OP_OpenWrite`, `OP_CreateTable`, `OP_CreateIndex`, `OP_Insert`, `OP_ParseSchema`, `OP_Destroy`, `OP_DropTable`, `OP_DropIndex`, `OP_Clear`, `OP_RowSetAdd`, `OP_RowSetRead`, `OP_Delete`, `OP_IdxDelete`, `OP_FkCounter`, and `OP_FkIfZero`.
- Parser/name resolver: `Parse`, `NameContext`, `Expr`, `ExprList`, `Select`, `SrcList`, token dequoting, expression resolution, and nested parser entry.
- Authorization: all DDL, transaction, savepoint, read-column, and DELETE paths can invoke the user authorizer.
- Virtual tables: CREATE/DROP and read-only checks use `sqlite3VtabCallConnect`, `sqlite3GetVTable`, `OP_VBegin`, `OP_VDestroy`, and `OP_VUpdate`.
- Triggers/views: view column derivation, view materialization, trigger-list lookup, trigger execution, and trigger old-row masks.
- Foreign keys: declaration storage in `Schema.fkeyHash`, parent lookup/index validation, child/parent scan code generation, and delete/drop-table integration.
- Collations/functions: collation-needed callbacks, global and per-connection function hash tables, LIKE optimizer flags, date/time and ALTER TABLE function registration.
- Optional compile-time features: `SQLITE_OMIT_ATTACH`, `SQLITE_OMIT_AUTHORIZATION`, `SQLITE_OMIT_VIEW`, `SQLITE_OMIT_TRIGGER`, `SQLITE_OMIT_FOREIGN_KEY`, `SQLITE_ENABLE_STAT2`, `SQLITE_OMIT_AUTOVACUUM`, `SQLITE_OMIT_REINDEX`, `SQLITE_ENABLE_UPDATE_DELETE_LIMIT`, `SQLITE_SOUNDEX`, `SQLITE_OMIT_LOAD_EXTENSION`, and `SQLITE_HAS_CODEC`.

## Risks And Edge Cases

- ATTACH/DETACH mutates `db->aDb` and global schema state. Failure cleanup must close partially opened Btrees, reset schema hashes, preserve `main`/`temp`, restore `nDb`, and avoid leaking `zName`; regressions here can leave corrupt connection-local schema state.
- ATTACH is forbidden inside explicit transactions and requires attached database encodings to match. Codec key handling adds a security-sensitive extension point when encryption is enabled.
- `sqlite3ResetInternalSchema(db, 0)` frees all schema hashes and compacts closed attached DB slots. Callers must hold Btree mutexes as asserted; misuse risks stale `Table`/`Index` pointers.
- Schema cookie logic is central to prepared statement invalidation. Missing `sqlite3ChangeCookie()` or `OP_Expire` after DDL can allow stale query plans or stale schema reads.
- `sqlite3NestedParse()` generates SQL strings that mutate `sqlite_master`; quoting and `%Q` usage are security- and correctness-relevant.
- Object-name restrictions around `sqlite_` are intentionally bypassed during initialization, nested parse, or writable-schema mode. This is a privileged path and can corrupt internal tables if misused.
- Index creation deliberately allows duplicate indexed columns for backward compatibility, but only the first instance is useful to the optimizer. This can surprise callers and is called out by a TODO.
- Automatic index de-duplication ignores sort-order differences when comparing equivalent UNIQUE/PRIMARY KEY constraints but respects collation and column order.
- DELETE truncate optimization is bypassed when triggers, virtual tables, or foreign keys are involved. An incorrect `sqlite3FkRequired()` result could silently skip required FK processing.
- Trigger and FK delete paths depend on OLD register masks. Missing a required old column can make triggers or FK actions read wrong/default data.
- LIKE/GLOB matching can be quadratic and recursive; `likeFunc()` enforces `SQLITE_LIMIT_LIKE_PATTERN_LENGTH` to limit abuse.
- `replace`, `quote`, `hex`, `zeroblob`, `group_concat`, and `randomblob` all enforce or rely on length limits. Integer overflow and allocation checks are important for hostile SQL inputs.
- Aggregate `sum()` tracks integer overflow only while all inputs are integer-like; once approximate inputs appear, result semantics change to floating point.
- Foreign-key parent lookup requires parent unique indexes to use default collations for explicit parent columns. Non-default collations can produce "foreign key mismatch" even when a unique index exists.
- The chunk ends in the middle of `fkScanChildren()`, so parent-side FK scan resolution and action emission continue in the next chunk.

## Test Signals

Useful behavioral tests for this chunk include:

- ATTACH/DETACH: attach duplicate names, too many databases, attach inside transaction, detach `main`/`temp`, detach locked/read-transaction/backup databases, attach encoding mismatch, and schema-init failure cleanup.
- Authorization: callbacks returning `SQLITE_OK`, `SQLITE_DENY`, `SQLITE_IGNORE`, and invalid codes for read columns, DDL, DELETE, transactions, and savepoints.
- DDL/schema: CREATE TABLE with duplicate columns, too many columns, invalid defaults, multiple primary keys, AUTOINCREMENT on non-INTEGER PK, CHECK name resolution, reserved `sqlite_` names, CREATE VIEW with parameters, circular view column derivation, DROP TABLE vs DROP VIEW mismatch, and writable-schema/system-table protection.
- Indexes: explicit index name collisions with tables/indexes, missing columns, collation lookup failure, UNIQUE conflict clause conflicts, automatic index de-duplication, DROP automatic index rejection, REINDEX by database/table/index/collation, and `sqlite_stat1` cleanup.
- Source lists and transactions: malformed `ON`/`USING` without JOIN, `INDEXED BY`/`NOT INDEXED`, temp database open failures, schema-cookie verification, BEGIN/COMMIT/ROLLBACK/SAVEPOINT authorizer behavior.
- DELETE: fast truncate vs row-by-row delete, count-changes result row, DELETE from views with INSTEAD OF triggers, virtual-table delete through `xUpdate`, BEFORE trigger deleting the same row, AFTER triggers, index-entry removal, limited DELETE rewrite, and FK-required bypass of truncate.
- Functions: NULL behavior for scalar functions, UTF-8 length/substr/trim cases, LIKE/GLOB escape validation and pattern length limits, abs integer overflow, random minimum bound, zeroblob/hex/quote length limits, replace growth/OOM, load-extension errors, aggregate empty-input behavior, sum overflow, min/max collation behavior, and group-concat separator behavior.
- Foreign keys: parent INTEGER PRIMARY KEY match, composite parent unique index match, missing parent key, wrong parent key cardinality, non-default parent collation mismatch, NULL child-key satisfaction, self-referential insert, immediate single-row insert halt path, and deferred/immediate counter changes.
