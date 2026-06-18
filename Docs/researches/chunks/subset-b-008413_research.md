# sources/storage-engines/foundationdb/contrib/sqlite/sqlite3.amalgamation.c lines 52796-60569

## Scope

This chunk covers a large middle section of the SQLite amalgamation embedded under the FoundationDB SQLite contribution. It begins in the final cases of the VDBE opcode interpreter, then spans complete or partial amalgamated modules:

- Tail of `vdbe.c`: virtual table update/rename opcodes, pager pragmas, tracing, interpreter profiling/debug epilogue, and error exits.
- `vdbeblob.c`: incremental BLOB handle implementation.
- `journal.c`: lazy on-disk journal wrapper used with `SQLITE_ENABLE_ATOMIC_WRITE`.
- `memjournal.c`: in-memory rollback journal implementation.
- `walker.c`: generic expression/SELECT tree traversal.
- `resolve.c`: identifier, alias, function, aggregate, and SELECT name resolution.
- Large part of `expr.c`: expression affinity/collation, expression allocation/duplication/deletion, `IN`/subquery code generation, boolean jump codegen, aggregate analysis, and temporary register management.
- `alter.c`: `ALTER TABLE RENAME` and `ALTER TABLE ADD COLUMN` implementation support.
- Start of `analyze.c`: `ANALYZE` code generation and the beginning of `sqlite3AnalysisLoad()`.

The chunk starts after earlier VDBE opcode cases and ends inside `sqlite3AnalysisLoad()`, after existing analysis statistics have been cleared and before the rest of sqlite_stat table loading is shown.

## Purpose

This range implements several core SQLite execution and compilation services:

- It finishes VDBE runtime behavior for virtual tables, page-count pragmas, tracing, and error unwinding.
- It exposes the public incremental BLOB APIs by borrowing a VDBE b-tree cursor while a prepared statement keeps the target row open.
- It provides journal file implementations used by pager rollback behavior, including pure memory journals and delayed materialization of journal files for atomic-write optimizations.
- It provides tree-walker infrastructure used by resolver, optimizer, code generator, and aggregate analyzer passes.
- It resolves SQL identifiers into table columns, trigger pseudo-table references, result aliases, functions, aggregate functions, and compound `ORDER BY` targets.
- It builds, copies, compares, deletes, and emits VDBE bytecode for expression trees.
- It implements schema-text rewrites and schema reloads for legacy SQLite `ALTER TABLE` operations.
- It generates and loads planner statistics for `ANALYZE` using `sqlite_stat1` and optionally `sqlite_stat2`.

## Important APIs, Types, and Functions

### VDBE Tail

Important opcodes in the opening section are:

- `OP_VRename` calls a virtual table module's `xRename()` implementation and imports any virtual-table error message.
- `OP_VUpdate` marshals memory cells into `sqlite3_value*` arguments for `xUpdate()`, updates `db->lastRowid` when requested, and increments the statement change counter.
- `OP_Pagecount` and `OP_MaxPgcnt` expose b-tree page count and maximum page-count behavior for pager pragmas.
- `OP_Trace` expands SQL text and invokes `db->xTrace`, with debug-only SQL trace logging.

The interpreter epilogue records VDBE profile counters, optionally prints register traces, funnels fatal exits through `vdbe_error_halt`, normal returns through `vdbe_return`, and maps `too_big`, `no_mem`, generic error, and interrupt labels into SQLite error codes.

### Incremental BLOB I/O

`Incrblob` is the handle behind `sqlite3_blob*`. It stores access flags, blob size, byte offset inside the record payload, column index, borrowed `BtCursor`, owning statement, and database handle.

Key functions:

- `blobSeekToRow()` binds/seeks the hidden VDBE statement to a rowid, verifies the target column has TEXT or BLOB serial type, records payload offset/size, caches overflow pages, and invalidates the handle on error by finalizing the statement.
- `sqlite3_blob_open()` validates the target table and column, rejects virtual tables/views, rejects writable handles on indexed or foreign-key child columns, builds a small VDBE program (`OP_Transaction`, `OP_VerifyCookie`, `OP_TableLock`, `OP_OpenRead`/`OP_OpenWrite`, `OP_NotExists`, `OP_Column`, `OP_ResultRow`), and seeks to the requested row.
- `blobReadWrite()` enforces bounds, checks invalidated handles, calls `sqlite3BtreeData()` or `sqlite3BtreePutData()` under cursor mutex discipline, and propagates b-tree errors through the VDBE and db error state.
- Public APIs `sqlite3_blob_close()`, `sqlite3_blob_read()`, `sqlite3_blob_write()`, `sqlite3_blob_bytes()`, and `sqlite3_blob_reopen()` wrap that state.

### Journal Implementations

With `SQLITE_ENABLE_ATOMIC_WRITE`, `JournalFile` subclasses `sqlite3_file` and starts with an in-memory buffer. `createFile()` lazily opens the real VFS file and flushes buffered bytes. `jrnlRead()`, `jrnlWrite()`, `jrnlTruncate()`, `jrnlSync()`, and `jrnlFileSize()` dispatch either to the real file or the buffer. `sqlite3JournalOpen()`, `sqlite3JournalCreate()`, and `sqlite3JournalSize()` are the external hooks used by pager code.

`MemJournal` is also a `sqlite3_file` subclass. It stores rollback journal bytes in a linked list of `FileChunk` blocks and keeps `FilePoint` cursors for end-of-file and sequential read optimization. `memjrnlRead()` walks/caches chunk positions, `memjrnlWrite()` only appends and allocates chunks, `memjrnlTruncate()` frees all chunks and reopens the handle, and `sqlite3MemJournalOpen()`, `sqlite3IsMemJournal()`, and `sqlite3MemJournalSize()` expose the implementation.

### Walker and Name Resolution

`sqlite3WalkExpr()`, `sqlite3WalkExprList()`, `sqlite3WalkSelectExpr()`, `sqlite3WalkSelectFrom()`, and `sqlite3WalkSelect()` implement the `Walker` callback protocol with `WRC_Continue`, `WRC_Prune`, and `WRC_Abort`.

Resolution is centered on:

- `lookupName()`: resolves `Z`, `Y.Z`, or `X.Y.Z` against `NameContext` source lists, trigger `old`/`new` pseudo-tables, rowid aliases, and result-set aliases. It sets `Expr` fields such as `op`, `iDb`, `iTable`, `iColumn`, `pTab`, affinity, `colUsed`, and authorization read state.
- `resolveExprStep()`: walker callback for identifiers, dotted names, functions, aggregates, subqueries, `IN`, and CHECK-constraint restrictions.
- `resolveSelectStep()`: resolves SELECT result expressions, FROM subqueries, WHERE/HAVING, GROUP BY, ORDER BY, LIMIT/OFFSET, aggregate flags, and compound SELECT ordering.
- `sqlite3ResolveExprNames()` and `sqlite3ResolveSelectNames()`: public resolver entry points for expression trees and SELECT trees.

Alias handling is intentionally nuanced: non-column aliases may be wrapped in `TK_AS` so they are evaluated once for alias reuse, but GROUP BY suppresses that behavior, preserving older SQLite semantics where expressions such as `random()` can be evaluated separately.

### Expression Analysis and Code Generation

This chunk includes many expression helpers:

- Affinity/collation: `sqlite3ExprAffinity()`, `sqlite3ExprSetColl()`, `sqlite3ExprSetCollByToken()`, `sqlite3ExprCollSeq()`, `sqlite3CompareAffinity()`, `sqlite3IndexAffinityOk()`, `sqlite3BinaryCompareCollSeq()`, and `codeCompare()`.
- Expression lifetime: `sqlite3ExprAlloc()`, `sqlite3Expr()`, `sqlite3ExprAttachSubtrees()`, `sqlite3PExpr()`, `sqlite3ExprAnd()`, `sqlite3ExprFunction()`, `sqlite3ExprAssignVarNumber()`, `sqlite3ExprDelete()`, reduced/tree duplication helpers, `sqlite3ExprDup()`, `sqlite3ExprListDup()`, `sqlite3SrcListDup()`, `sqlite3IdListDup()`, `sqlite3SelectDup()`, `sqlite3ExprListAppend()`, name/span setters, length checks, and `sqlite3ExprListDelete()`.
- Constant and nullability checks: `sqlite3ExprIsConstant()`, `sqlite3ExprIsConstantNotJoin()`, `sqlite3ExprIsConstantOrFunction()`, `sqlite3ExprIsInteger()`, `sqlite3ExprCanBeNull()`, `sqlite3ExprCodeIsNullJump()`, and `sqlite3ExprNeedsNoAffinityChange()`.
- `IN`/subquery paths: `isCandidateForInOpt()`, `sqlite3FindInIndex()`, `sqlite3CodeSubselect()`, and `sqlite3ExprCodeIN()` choose existing rowid/index cursors where safe or build ephemeral tables and handle RHS NULL tracking.
- Codegen: `sqlite3ExprCodeTarget()`, `sqlite3ExprCodeTemp()`, `sqlite3ExprCode()`, `sqlite3ExprCodeAndCache()`, `sqlite3ExprCodeConstants()`, `sqlite3ExprCodeExprList()`, `sqlite3ExprIfTrue()`, and `sqlite3ExprIfFalse()` emit VDBE bytecode for literals, columns, variables, functions, CASE, BETWEEN, trigger references, `RAISE()`, subqueries, and boolean jumps.
- Comparison/aggregate analysis: `sqlite3ExprCompare()`, `sqlite3ExprListCompare()`, `sqlite3ExprAnalyzeAggregates()`, and `sqlite3ExprAnalyzeAggList()` identify equivalent expressions, aggregate columns, aggregate functions, DISTINCT aggregate cursors, and sorter columns.
- Register management: `sqlite3GetTempReg()`, `sqlite3ReleaseTempReg()`, `sqlite3GetTempRange()`, and `sqlite3ReleaseTempRange()` manage temporary VDBE registers while respecting the column cache.

### ALTER TABLE

`alter.c` registers built-in SQL helper functions through `sqlite3AlterFunctions()`:

- `sqlite_rename_table()` rewrites table names in CREATE TABLE/INDEX SQL.
- `sqlite_rename_trigger()` rewrites the target table in CREATE TRIGGER SQL.
- `sqlite_rename_parent()` rewrites parent table references in foreign-key clauses.

`sqlite3AlterRenameTable()` validates the target, rejects system tables/views and conflicting names, invokes virtual-table `xRename()` when present, rewrites rows in `sqlite_master` and `sqlite_temp_master`, updates `sqlite_sequence`, rewrites affected foreign-key child CREATE TABLE SQL when foreign keys are enabled, changes schema cookies, and reloads affected schema objects.

`sqlite3AlterBeginAddColumn()` creates a temporary `Table` copy prefixed with `sqlite_altertab_` for parser mutation. `sqlite3AlterFinishAddColumn()` validates ADD COLUMN restrictions, verifies constant defaults, rewrites the CREATE TABLE SQL text, raises the minimum file format to 2 or 3 depending on the default, and reloads the schema.

### ANALYZE

The covered start of `analyze.c` includes:

- `openStatTable()`: creates or clears `sqlite_stat1` and optionally `sqlite_stat2`, opens them for writing, and deletes rows for a single table when requested.
- `analyzeOneTable()`: skips views, virtual tables, and system tables; scans each index; counts total rows and distinct prefixes; optionally records `SQLITE_INDEX_SAMPLES` stat2 samples; writes `sqlite_stat1` rows; and emits table-only row-count stats for unindexed tables.
- `loadAnalysis()`, `analyzeDatabase()`, `analyzeTable()`, and `sqlite3Analyze()`: route the SQL `ANALYZE` forms across all databases, one database, or one table.
- `analysisLoader()`: parses sqlite_stat1 strings back into `Table.nRowEst` and `Index.aiRowEst`.
- `sqlite3DeleteIndexSamples()`: frees stat2 sample memory when enabled.
- Start of `sqlite3AnalysisLoad()`: clears prior index estimates and stat2 samples before reading sqlite_stat tables.

## Control Flow

The VDBE tail is runtime switch-dispatch code. It calls external module or b-tree APIs, sets `rc`, and exits through common halt labels. The important invariant is that all exits leave b-tree mutex arrays via `sqlite3BtreeMutexArrayLeave()`.

Incremental BLOB control flow is statement-backed. `sqlite3_blob_open()` builds a VDBE program and calls `blobSeekToRow()`. Once `OP_ResultRow` has positioned the VDBE cursor, read/write calls bypass SQL evaluation and operate directly on the borrowed b-tree cursor. If the row disappears, the value has a non-BLOB/TEXT type, an out-of-range request occurs, or b-tree returns `SQLITE_ABORT`, the handle is either rejected or invalidated so later operations fail predictably.

Journal control flow is delegated through `sqlite3_io_methods`. Lazy journals remain memory-only until a write exceeds `nBuf` or `sqlite3JournalCreate()` forces creation. Memory journals are append-only except for truncate-to-zero, which frees all chunks.

Resolver control flow is a top-down tree walk. Name contexts chain from inner to outer SELECTs; a successful match prunes the subtree after rewriting the expression node. SELECT resolution expands unresolved subqueries when needed, resolves result columns before WHERE/HAVING alias references, and handles compound ORDER BY only after all terms are resolved.

Expression codegen control flow emits VDBE jumps rather than computing every boolean into a register. `sqlite3ExprIfTrue()` and `sqlite3ExprIfFalse()` use short-circuit labels for AND/OR/NOT, direct comparison opcodes for relational operators, and special handling for NULL-sensitive `IS`, `IS NOT`, `BETWEEN`, and `IN`. Subquery and `IN` code may be guarded by a one-time `OP_If` unless correlated, trigger-dependent, or variable-containing.

ALTER and ANALYZE do not directly mutate all state in C. They generate nested SQL and VDBE programs that perform schema table updates, stat table writes, schema cookie changes, schema reparsing, and planner-stat reloads at statement execution time.

## State and Persistence Behavior

Persistent database state touched by this chunk includes:

- Rollback journals and memory journals, via pager-facing `sqlite3_file` implementations.
- Table row payload bytes modified by `sqlite3_blob_write()` through `sqlite3BtreePutData()`.
- `sqlite_master`/`sqlite_temp_master` SQL text, table names, index names, trigger metadata, and `sqlite_sequence` rows during ALTER TABLE.
- Database header file-format cookies during ADD COLUMN.
- `sqlite_stat1` and optional `sqlite_stat2` contents during ANALYZE.
- In-memory schema and planner state, including dropped/reparsed table/trigger definitions, `Table.nRowEst`, `Index.aiRowEst`, and optional `Index.aSample`.

Important transient state includes VDBE registers, expression flags (`EP_Resolved`, `EP_Agg`, `EP_xIsSelect`, `EP_IntValue`, `EP_Reduced`, `EP_TokenOnly`, `EP_Static`, `EP_FixedDest`), column-cache entries, parse counters (`nTab`, `nMem`, `nVar`, alias counters), name-context aggregate/reference counters, trigger old/new bitmasks, and incremental BLOB cursor state.

## Dependencies and Integration Points

This code depends heavily on internal SQLite layers:

- VDBE opcodes and builders (`sqlite3VdbeAddOp*`, `sqlite3VdbeChange*`, labels, P4 ownership modes).
- B-tree and pager APIs for page count, cursor data, blob writes, table/index opens, locks, schema cookies, and journal use.
- VFS APIs via `sqlite3_file`, `sqlite3_io_methods`, and `sqlite3Os*` wrappers.
- Parser structures (`Parse`, `Expr`, `ExprList`, `Select`, `SrcList`, `NameContext`, `AggInfo`, `Table`, `Index`, `FKey`, `Trigger`).
- Schema, authorization, virtual table, foreign-key, trigger, collation, function registry, and memory allocation helpers.

FoundationDB integration risk is mostly indirect: this vendored SQLite amalgamation defines SQL semantics and pager behavior used by the FoundationDB SQLite layer. Any local changes to VFS, pager, b-tree, virtual table modules, or tests around SQL compatibility can surface through these code paths.

## Risks

- Incremental BLOB handles rely on a live VDBE statement and borrowed b-tree cursor. Incorrect finalization, cursor invalidation, or mutex handling can cause stale cursor access, aborted handles, or lock-order bugs.
- Writable blob handles deliberately reject indexed and foreign-key child columns. Relaxing this would bypass constraint/index maintenance because writes mutate payload bytes directly.
- `blobReadWrite()` bounds checks use `iOffset+n`; integer overflow or signedness mistakes would be high impact for memory safety, though this implementation uses SQLite's established integer assumptions.
- Lazy journal materialization must preserve all bytes already written before switching to the real file. Errors in `createFile()` or offset handling can break rollback durability.
- `memjrnlRead()` assumes SQLite never reads past journal EOF and asserts append-only writes. External use outside pager assumptions would be unsafe.
- Name resolution changes can silently alter SQL semantics, especially alias visibility, NATURAL/USING duplicate suppression, trigger `old`/`new`, rowid aliases, aggregate misuse detection, and compound ORDER BY matching.
- Expression duplication/deletion uses reduced/token-only/static flags and mixed inline/allocated token storage. Incorrect flag propagation can cause leaks, double frees, or use-after-free.
- `IN` optimization depends on affinity, collation, uniqueness, nullability, and correlation checks. Choosing an existing index incorrectly can produce wrong answers, especially with NULL-sensitive `IN` semantics.
- Boolean codegen assumes token constants align with VDBE opcode constants for comparison operators. Any opcode renumbering must preserve the asserted relationships.
- ALTER TABLE rewrites raw CREATE SQL text using token scanning. Quoting, unusual whitespace, triggers, foreign-key references, and temp triggers are compatibility-sensitive.
- ANALYZE statistics are planner inputs. Bad distinct-count math, stat-table schema handling, collation use, or stat loading can produce poor or incorrect query plans.
- The chunk ends before `sqlite3AnalysisLoad()` completes, so stat1/stat2 readback behavior must be reconciled with the next chunk before drawing full conclusions about planner-stat loading.

## Test and Validation Signals

Useful validation signals for this range include:

- SQLite core tests for incremental blob APIs: open/read/write/bytes/reopen/close, nonexistent rowid, non-BLOB/TEXT columns, schema invalidation, writable indexed columns, foreign-key child columns, and concurrent row changes.
- Pager/journal tests across rollback modes, `journal_mode=MEMORY`, atomic-write VFS behavior, forced journal creation, short reads, truncation, sync, and OOM during chunk allocation.
- Resolver tests for ambiguous columns, aliases in WHERE/ORDER/GROUP, compound SELECT ORDER BY, subquery correlation, CHECK constraint restrictions, aggregate misuse, HAVING without GROUP BY, trigger `old`/`new`, rowid aliases, and authorization callbacks.
- Expression-codegen tests for affinity/collation comparisons, `IN` with lists/subqueries/NULLs, rowid and index-backed `IN`, correlated subqueries, EXISTS/scalar SELECT, CASE, BETWEEN, COALESCE/IFNULL short-circuiting, virtual-table function overloading, RAISE in and out of triggers, and expression-depth limits.
- ALTER TABLE tests for renaming tables with indexes, triggers, temp triggers, autoincrement sequence rows, virtual tables with/without `xRename`, foreign-key parent references, quoted identifiers, reserved/system names, views, and ADD COLUMN constraints/defaults/file-format behavior.
- ANALYZE tests for creating/clearing stat tables, per-table and per-database analyze forms, unindexed tables, multi-column index statistics, stat2 sample generation when enabled, authorization, system-table skipping, OOM paths, and subsequent query-plan changes after `OP_LoadAnalysis`.
- Build matrix coverage with feature flags such as `SQLITE_OMIT_INCRBLOB`, `SQLITE_ENABLE_ATOMIC_WRITE`, `SQLITE_OMIT_SUBQUERY`, `SQLITE_OMIT_TRIGGER`, `SQLITE_OMIT_FOREIGN_KEY`, `SQLITE_OMIT_ALTERTABLE`, `SQLITE_OMIT_ANALYZE`, and `SQLITE_ENABLE_STAT2`.
