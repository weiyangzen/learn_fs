# sources/storage-engines/wiredtiger/test/3rdparty/sqlite3/sqlite3.c lines 122463-130124

## Scope

This chunk spans the tail of SQLite `attach.c`, all of `auth.c`, most of `build.c`, all of `callback.c`, and the beginning of `delete.c` within the SQLite amalgamation vendored under WiredTiger tests. It starts in ATTACH/DETACH code generation, covers schema name fixing for DDL expressions, authorization callbacks, table/index/view/foreign-key/schema construction and destruction helpers, collation and function lookup registries, schema cleanup/allocation, and ends in `sqlite3GenerateRowDelete()` immediately after the initial row seek for a generated single-row delete.

The covered range is parser/code-generator infrastructure, not the btree pager itself. It builds and maintains in-memory schema objects and emits VDBE opcodes that later mutate persistent database btrees and `sqlite_schema`.

## Purpose

The ATTACH/DETACH tail compiles `ATTACH` and `DETACH` statements into calls to internal SQL functions (`sqlite_attach`, `sqlite_detach`) after resolving arguments and checking authorization.

The DDL fixer code ensures views, triggers, and indexes stored in a specific schema do not contain persistent references to objects in a different schema, except for TEMP objects. It also marks DDL expressions and rejects host parameters outside schema initialization.

The authorization module implements `sqlite3_set_authorizer()` and the internal authorization checks used by parser actions and expression resolution. It gates schema changes, reads, writes, transactions, savepoints, ATTACH/DETACH, index rebuilds, and DELETE generation.

The large `build.c` portion is SQLite's parser action layer for schema construction and maintenance. It creates table, view, index, primary-key, CHECK, generated-column, foreign-key, and CTE structures; emits VDBE bytecode to update `sqlite_schema`, schema cookies, root pages, and statistics tables; manages schema reset and memory cleanup; and provides shared helpers for source lists, identifier lists, transactions, constraints, reindexing, and key metadata.

The `callback.c` portion manages application-defined collations/functions, built-in function lookup, text-encoding defaults, collation-needed callbacks, and schema object cleanup/allocation.

The `delete.c` prefix starts DELETE statement compilation: it locates the target table, rejects unsafe targets, handles view materialization and `DELETE ... ORDER BY ... LIMIT`, chooses truncate/one-pass/two-pass strategies, and invokes row-delete code generation.

## Important APIs, Types, and Functions

- ATTACH/DETACH and DDL fixing:
  - `codeAttach()`, `sqlite3Detach()`, `sqlite3Attach()` compile attach/detach statements into VDBE function calls and statement expiration.
  - `DbFixer`, `fixExprCb()`, `fixSelectCb()`, `sqlite3FixInit()`, `sqlite3FixSrcList()`, `sqlite3FixSelect()`, `sqlite3FixExpr()`, and `sqlite3FixTriggerStep()` walk parse trees for schema pinning and illegal cross-database references.
- Authorization:
  - `sqlite3_set_authorizer()` stores `db->xAuth`/`db->pAuthArg` and expires prepared statements when enabling authorization.
  - `sqlite3AuthReadCol()`, `sqlite3AuthRead()`, and `sqlite3AuthCheck()` call user authorization hooks and map `SQLITE_DENY`, `SQLITE_IGNORE`, and bad return codes into parse errors.
  - `sqlite3AuthContextPush()` and `sqlite3AuthContextPop()` manage `pParse->zAuthContext`, especially for views/triggers.
- Shared-cache and final VDBE coding:
  - `TableLock`, `lockTable()`, `sqlite3TableLock()`, and `codeTableLocks()` accumulate and emit `OP_TableLock`.
  - `sqlite3FinishCoding()` appends `OP_Halt`, emits transaction/schema-cookie checks, virtual-table `OP_VBegin`, table locks, autoincrement setup, constant-expression factoring, RETURNING cursor setup, and `sqlite3VdbeMakeReady()`.
  - `sqlite3NestedParse()` runs parser/codegen recursively for generated SQL used to update schema metadata.
- Schema lookup/lifecycle:
  - `sqlite3FindTable()`, `sqlite3LocateTable()`, `sqlite3LocateTableItem()`, `sqlite3PreferredTableName()`, `sqlite3FindIndex()`, `sqlite3FindDbName()`, `sqlite3FindDb()`, and `sqlite3TwoPartName()` resolve schema-qualified names.
  - `sqlite3FreeIndex()`, `sqlite3UnlinkAndDeleteIndex()`, `sqlite3DeleteColumnNames()`, `deleteTable()`, `sqlite3DeleteTable()`, `sqlite3UnlinkAndDeleteTable()`, `sqlite3SchemaClear()`, and `sqlite3SchemaGet()` clean schema-owned structures.
  - `sqlite3ResetOneSchema()`, `sqlite3ResetAllSchemasOfConnection()`, `sqlite3CollapseDatabaseArray()`, and `sqlite3CommitInternalChanges()` manage schema invalidation and attached-database array compaction.
- Table and column creation:
  - `sqlite3StartTable()` initializes `pParse->pNewTable`, checks names/authorization/collisions, allocates schema placeholder rows, and emits root-page allocation.
  - `sqlite3AddColumn()`, `sqlite3AddNotNull()`, `sqlite3AffinityType()`, `sqlite3AddDefaultValue()`, `sqlite3AddPrimaryKey()`, `sqlite3AddCheckConstraint()`, `sqlite3AddCollateType()`, and `sqlite3AddGenerated()` populate `Table`, `Column`, defaults, constraints, affinities, collations, and generated-column metadata.
  - `sqlite3ColumnSetExpr()`, `sqlite3ColumnExpr()`, `sqlite3ColumnSetColl()`, `sqlite3ColumnColl()`, `sqlite3StorageColumnToTable()`, and `sqlite3TableColumnToStorage()` support generated/default expression and virtual/stored column layout mapping.
- Table/view/drop behavior:
  - `sqlite3EndTable()` finalizes CREATE TABLE/CREATE TABLE AS SELECT, strict tables, generated columns, WITHOUT ROWID conversion, schema-table updates, autoincrement table creation, schema reparsing, and in-memory schema insertion.
  - `sqlite3CreateView()`, `viewGetColumnNames()`, `sqlite3ViewGetColumnNames()`, and `sqliteViewResetAll()` build views and lazily derive view column metadata.
  - `sqlite3RootPageMoved()`, `destroyRootPage()`, `destroyTable()`, `sqlite3ClearStatTables()`, `sqlite3CodeDropTable()`, `sqlite3DropTable()`, `sqlite3ReadOnlyShadowTables()`, and `tableMayNotBeDropped()` emit destructive schema changes and enforce protected-object rules.
- Index and key metadata:
  - `resizeIndexObject()`, `estimateTableWidth()`, `estimateIndexWidth()`, `isDupColumn()`, `recomputeColumnsNotIndexed()`, and `convertToWithoutRowidTable()` transform index metadata for rowid and WITHOUT ROWID tables.
  - `sqlite3RefillIndex()`, `sqlite3AllocateIndexObject()`, `sqlite3HasExplicitNulls()`, `sqlite3CreateIndex()`, `sqlite3DefaultRowEst()`, `sqlite3DropIndex()`, `sqlite3Reindex()`, and `sqlite3KeyInfoOfIndex()` allocate, validate, persist, rebuild, and describe indexes.
- Foreign keys, lists, transactions, and constraints:
  - `sqlite3CreateForeignKey()` and `sqlite3DeferForeignKey()` allocate `FKey` entries and link them into table and schema hashes.
  - `sqlite3ArrayAllocate()`, `sqlite3IdListAppend()`, `sqlite3IdListDelete()`, `sqlite3IdListIndex()`, and `sqlite3SrcList*()` helpers own parser list construction and cleanup.
  - `sqlite3BeginTransaction()`, `sqlite3EndTransaction()`, `sqlite3Savepoint()`, `sqlite3OpenTempDatabase()`, `sqlite3CodeVerifySchema()`, `sqlite3BeginWriteOperation()`, `sqlite3MultiWrite()`, and `sqlite3MayAbort()` set VDBE transaction, schema verification, and statement-journal requirements.
  - `sqlite3HaltConstraint()`, `sqlite3UniqueConstraint()`, and `sqlite3RowidConstraint()` emit constraint failure opcodes and messages.
- Collation/function/schema callbacks:
  - `callCollNeeded()`, `synthCollSeq()`, `sqlite3CheckCollSeq()`, `findCollSeqEntry()`, `sqlite3FindCollSeq()`, `sqlite3SetTextEncoding()`, `sqlite3GetCollSeq()`, and `sqlite3LocateCollSeq()` locate or synthesize collations and update default encoding state.
  - `matchQuality()`, `sqlite3FunctionSearch()`, `sqlite3InsertBuiltinFuncs()`, and `sqlite3FindFunction()` manage built-in and application-defined SQL functions.
- DELETE prefix:
  - `sqlite3SrcListLookup()`, `sqlite3CodeChangeCount()`, `sqlite3IsReadOnly()`, `sqlite3MaterializeView()`, `sqlite3LimitWhere()`, `sqlite3DeleteFrom()`, and the opening of `sqlite3GenerateRowDelete()` compile DELETE statements and begin single-row delete code.

## Control Flow

ATTACH/DETACH compilation first reads schema, resolves attach expressions using a `NameContext`, invokes authorization using either the literal auth string or NULL, then codes filename/dbname/key expressions into temporary registers. A VDBE function call dispatches to `attachFunc()` or `detachFunc()`, followed by `OP_Expire` to invalidate statements at the correct scope. All owned expressions are deleted on exit.

DDL fixing is walker-driven. `sqlite3FixInit()` binds a target schema and installs expression/select callbacks. Expression callbacks tag schema expressions with `EP_FromDDL` and reject variables unless schema initialization is in progress, where variables are converted to NULL. Select callbacks walk source lists, reject explicit cross-schema references, convert unresolved database names into fixed `Schema*` references, and recursively walk `ON` clauses and CTE subqueries.

Authorization control is callback-centered. Public registration is mutex-protected. Internal reads call `SQLITE_READ` with table/column/db/context; `SQLITE_IGNORE` rewrites readable expressions to NULL, while DENY sets `SQLITE_AUTH`. Generic checks skip during database initialization and special parses, call `db->xAuth`, and normalize illegal callback return values into an authorizer malfunction.

`sqlite3FinishCoding()` is the top-level closeout for one SQL statement. It short-circuits nested parses and earlier errors, ensures a VDBE exists, appends RETURNING result loops when needed, emits `OP_Halt`, rewinds to `OP_Init`, emits `OP_Transaction` and schema-cookie checks for every database in `cookieMask`, emits virtual-table and shared-cache lock setup, begins autoincrement state, evaluates factored constants, opens RETURNING ephemeral storage, jumps to executable code, then marks the program ready.

CREATE TABLE flows from `sqlite3StartTable()` through column/constraint routines into `sqlite3EndTable()`. Start-table resolves the target database, rejects illegal temp qualification and reserved names, checks auth and collisions, allocates a `Table`, and emits placeholder schema-table insertion and root-page allocation. End-table resolves CHECK and generated expressions, applies STRICT and WITHOUT ROWID transformations, estimates widths, generates CTAS population code if needed, updates the schema placeholder row with final SQL text, creates `sqlite_sequence` for AUTOINCREMENT, emits schema reparse and generated-column validation SQL, and inserts schema-loaded tables into the in-memory hash when reading existing schema.

WITHOUT ROWID conversion is an in-place metadata and bytecode rewrite. It marks primary-key columns NOT NULL, changes the table root btree from integer-key to blob-key, creates a primary-key index for former integer primary keys, removes duplicate PK columns, bypasses the separate PK btree/schema entry, points the PK index at the table root, appends missing PK columns to UNIQUE indexes, and makes the PK index covering by appending non-virtual table columns.

CREATE INDEX first resolves the table and index database, rejects views/virtual tables/system tables, invents automatic names for constraints, checks authorization, resolves and validates each indexed expression, computes collations and sort order, appends rowid or WITHOUT ROWID primary-key columns, suppresses duplicate automatic constraints, links schema structures, emits root-page creation and `sqlite_schema` insertion for explicit indexes, optionally refills the index from table contents, reparses schema, and reorders REPLACE-conflict indexes to the end of the table index list.

DROP TABLE/INDEX flows are destructive code-generation paths. They read schema, locate target objects, validate object kind and protected status, perform authorization, clear statistics rows, emit foreign-key/drop-trigger work, delete schema rows through generated SQL, destroy btree root pages in descending order to avoid auto-vacuum relocation hazards, emit `OP_DropTable`/`OP_DropIndex`/virtual-table destroy opcodes, change schema cookies, and reset view column caches.

The collation and function callback code uses hash tables and best-match scoring. Collation lookup first finds or creates a per-name triplet for UTF-8/UTF-16LE/UTF-16BE, invokes collation-needed callbacks if no comparator exists, and can copy a comparator from another encoding as a fallback. Function lookup searches application-defined functions first, then built-ins unless built-ins are preferred or a new function is being created; `matchQuality()` ranks arity and encoding compatibility.

DELETE compilation starts by resolving the single source table, collecting triggers and foreign-key complexity, optionally rewriting `ORDER BY/LIMIT` into a `rowid IN (SELECT ...)` or composite-PK `IN` expression, initializing view column names, rejecting read-only targets, checking delete authorization, assigning cursors, materializing views for INSTEAD OF triggers, resolving the WHERE clause, optionally using the truncate optimization, otherwise choosing rowid RowSet or WITHOUT ROWID ephemeral-PK collection plus WHERE one-pass planning, opening write cursors, and delegating each row to virtual-table `OP_VUpdate` or `sqlite3GenerateRowDelete()`.

## State and Persistence Behavior

This code mutates parser state (`Parse`), connection state (`sqlite3`), schema state (`Schema`, `Table`, `Index`, `FKey`, `Trigger`, `With`, `Cte`), and generated VDBE programs. Persistent disk effects are usually deferred into emitted opcodes and nested SQL: `sqlite_schema` rows are inserted/updated/deleted, root pages are created/destroyed, schema cookies are incremented, autoincrement state may create or update `sqlite_sequence`, and index refill/delete operations modify table/index btrees.

Schema caches are explicit and fragile. `sqlite3ResetOneSchema()` and `sqlite3ResetAllSchemasOfConnection()` clear table/index/trigger/fkey hashes or defer reset with `DB_ResetWanted` while schema locks are held. `sqlite3SchemaClear()` deletes triggers first, indexes, tables, foreign-key hashes, and bumps `iGeneration` only for loaded schemas. `sqlite3CollapseDatabaseArray()` removes detached database slots after schema reset.

Memory ownership is distributed through parser structures. Many routines consume `Expr*`, `ExprList*`, `SrcList*`, `Token`-derived strings, and schema objects even on error. Common exit labels free partially owned objects. `sqlite3DeleteTable()` uses `nTabRef`; `deleteTable()` unlinks indexes from hashes when not in byte-counting mode, frees foreign keys/virtual table/view select state, column names, checks, and table storage.

Name, type, and collation data are compacted inside column and index allocations. Column name storage may contain nul-separated type and collation strings. Index allocations pack `Index`, collation pointer array, row estimates, column numbers, sort-order bytes, name, and extra collation names into one allocation unless resized later.

DDL safety state is encoded in flags such as `TF_HasPrimaryKey`, `TF_WithoutRowid`, `TF_NoVisibleRowid`, `TF_Strict`, `TF_HasGenerated`, `TF_HasVirtual`, `TF_HasStored`, `TF_Shadow`, `COLFLAG_*`, `DBFLAG_SchemaChange`, `DBFLAG_SchemaKnownOk`, `DB_ResetWanted`, and per-parse `isMultiWrite`, `mayAbort`, `writeMask`, and `cookieMask`.

DELETE code may use transient RowSets or ephemeral btrees to store rowids/primary keys before deletion. For simple whole-table deletes, the truncate path emits `OP_Clear` directly for the table and indexes and can count changes. For complex deletes, state must preserve WHERE cursors, one-pass cursor positions, trigger/FK context, and autoincrement end-of-statement work.

## Dependencies and Integration Points

This chunk integrates with SQLite's parser, expression walker, resolver, VDBE code emitter, btree layer, virtual table layer, trigger/foreign-key modules, schema hashes, SQL function/collation registries, and memory allocator. Important dependencies include `sqlite3ReadSchema()`, `sqlite3RunParser()`, `sqlite3NestedParse()`, `sqlite3VdbeAddOp*()`, `sqlite3Btree*()`, `sqlite3Hash*()`, `sqlite3Walk*()`, `sqlite3Resolve*()`, `sqlite3Select*()`, `sqlite3Vtab*()`, `sqlite3Fk*()`, `sqlite3Trigger*()`, `sqlite3WhereBegin()`, `sqlite3WhereOkOnePass()`, and `sqlite3OpenTableAndIndices()`.

Compile-time feature gates heavily affect behavior: `SQLITE_OMIT_ATTACH`, `SQLITE_OMIT_AUTHORIZATION`, `SQLITE_OMIT_SHARED_CACHE`, `SQLITE_OMIT_VIEW`, `SQLITE_OMIT_TRIGGER`, `SQLITE_OMIT_UPSERT`, `SQLITE_OMIT_VIRTUALTABLE`, `SQLITE_OMIT_GENERATED_COLUMNS`, `SQLITE_OMIT_CHECK`, `SQLITE_OMIT_AUTOINCREMENT`, `SQLITE_OMIT_ALTERTABLE`, `SQLITE_OMIT_AUTOVACUUM`, `SQLITE_OMIT_FOREIGN_KEY`, `SQLITE_OMIT_TEMPDB`, `SQLITE_OMIT_REINDEX`, `SQLITE_OMIT_CTE`, `SQLITE_OMIT_UTF16`, `SQLITE_ENABLE_HIDDEN_COLUMNS`, `SQLITE_ENABLE_SORTER_REFERENCES`, `SQLITE_ENABLE_UPDATE_DELETE_LIMIT`, `SQLITE_ENABLE_PREUPDATE_HOOK`, and debug/test macros.

Authorization hooks are public API integration points and affect parse-time behavior rather than run-time btree checks. Collation-needed callbacks and application-defined SQL function registration are also public extension points.

In this repository, the code is part of a vendored SQLite amalgamation under `sources/storage-engines/wiredtiger/test/3rdparty/sqlite3`. It affects tests or tooling that compile this SQLite copy; it is not part of WiredTiger's storage engine implementation itself.

## Risks and Edge Cases

- Schema mutation code relies on exact ordering. For CREATE TABLE, the table schema row placeholder must exist before implicit index rows. For DROP under auto-vacuum, root pages must be destroyed from largest to smallest.
- DDL fixer behavior is security-sensitive. Missing `fixedSchema` tagging or cross-schema checks could allow persistent view/trigger/index definitions to bind to objects outside their intended schema.
- Authorization handling must preserve `SQLITE_IGNORE` semantics. In read expressions it becomes NULL; for some operations such as DELETE it disables optimizations rather than denying the operation.
- `sqlite3FinishCoding()` appends initialization/transaction code after the main program and patches `OP_Init`; incorrect cookie/write mask handling can miss schema-change detection or statement-journal requirements.
- `sqlite3NestedParse()` is reentrant and temporarily changes parser tail state plus `DBFLAG_PreferBuiltin`; missing restoration would corrupt the outer parse.
- STRICT tables, generated columns, WITHOUT ROWID, INTEGER PRIMARY KEY, AUTOINCREMENT, and DESC primary-key handling interact. Small changes can alter persistent record layout, index coverage, or legacy compatibility.
- Column storage layout is compact and non-obvious: name, optional type, and optional collation share one allocation. Offset mistakes would corrupt schema metadata.
- `sqlite3CreateIndex()` has many special cases: automatic constraint index deduplication, rename-object retention, partial-index resolution, expression index ownership, WITHOUT ROWID PK suffixes, missing collation deactivation, and REPLACE-index list ordering.
- Public callback lookup is mutable. Collation fallback copies a comparator but not its destructor. Function creation must never return read-only built-in `FuncDef` objects for overwrite.
- `sqlite3ShadowTableName()` temporarily writes into the supplied name string to split at the final underscore; callers must provide mutable strings.
- DELETE one-pass mode must preserve cursor positioning around triggers and index deletes. `aToOpen` cursor elision is sensitive to `aiCurOnePass` offsets.
- View DELETE requires INSTEAD OF triggers and materializes view rows into an ephemeral table; read-only checks must distinguish views with RETURNING triggers from modifiable trigger-backed views.
- Many paths deliberately continue on `ifNotExists`, `noErr`, or schema initialization with silent or empty errors. Tests need to distinguish OOM, corrupt schema, suppressed errors, and accepted no-op DDL.

## Test Signals

- ATTACH/DETACH tests with literal and expression arguments, authorization DENY, invalid authorizer return values, and statement expiration behavior.
- Authorizer tests for `SQLITE_READ` returning OK/IGNORE/DENY, DELETE returning IGNORE disabling truncate optimization, schema DDL permissions, transaction/savepoint auth strings, and view auth context names.
- DDL fixer tests for views/triggers/indexes referencing attached schemas, TEMP exemptions, host parameters in schema definitions, CTEs and `ON` clauses inside view definitions, and schema initialization behavior.
- CREATE TABLE tests covering existing table `IF NOT EXISTS`, TEMP qualification errors, reserved `sqlite_` names, shadow table protection, STRICT datatype enforcement, CTAS schema text generation, generated-column cycles/illegal expressions, and CHECK resolution failures.
- Primary-key and generated-column tests for INTEGER PRIMARY KEY, DESC primary key, duplicate primary keys, AUTOINCREMENT constraints, generated column primary-key rejection, WITHOUT ROWID conversion, and duplicate PK column pruning.
- Index tests for named and automatic indexes, duplicate automatic constraints with conflicting `ON CONFLICT`, expression and partial indexes, `NULLS FIRST/LAST` rejection, collation lookup failures, covering-index flags, WITHOUT ROWID suffix columns, CREATE INDEX schema rows, DROP INDEX restrictions, and REINDEX by database/table/index/collation.
- DROP TABLE/VIEW tests for protected system tables, shadow tables under defensive mode, eponymous virtual tables, wrong DROP TABLE vs DROP VIEW command, trigger cleanup, `sqlite_sequence` cleanup, statistics cleanup, virtual-table destroy, and auto-vacuum root-page movement.
- Foreign-key tests for inline and table-level FK definitions, mismatched column counts, unknown child columns, referenced-column storage, ON DELETE/ON UPDATE action flags, and deferred/immediate toggling.
- Source-list and CTE tests for FROM-list growth limits, JOIN type shifting including RIGHT JOIN `JT_LTORJ`, subquery attach/detach ownership, table-valued function args, INDEXED BY/NOT INDEXED flags, duplicate CTE names, and CTE cleanup.
- Collation/function registry tests for UTF-8/UTF-16 variants, collation-needed callbacks, fallback to alternate encodings, missing collation deactivating indexes through `sqlite3KeyInfoOfIndex()`, built-in preference during nested parse, and application function creation/overload resolution.
- DELETE tests for truncate optimization, row-by-row delete, WITHOUT ROWID composite PK deletes, one-pass single and multi deletes, virtual-table deletes, view deletes via INSTEAD OF triggers, `ORDER BY/LIMIT` rewrites, count-changes result rows, FK/trigger complexity, RETURNING interactions, and autoincrement end-state handling.
