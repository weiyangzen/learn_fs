# sources/storage-engines/wiredtiger/test/3rdparty/sqlite3/sqlite3.c lines 130125-137437

## Scope

This chunk spans the tail of SQLite's `delete.c`, the complete `func.c` section, the complete `fkey.c` section, and the beginning of `insert.c` through the first half of `sqlite3GenerateConstraintChecks()`. It is part of the amalgamated SQLite copy vendored under WiredTiger tests, so the visible units are static helpers and `SQLITE_PRIVATE`/`SQLITE_API` entry points used by other SQLite compiler/runtime sections in the same `sqlite3.c`.

## Purpose

The code in this span has three main responsibilities:

- Finish DELETE row code generation by deleting secondary-index entries, firing row triggers, and invoking foreign-key checks/actions.
- Define and register many built-in SQL scalar, aggregate, window-capable aggregate, LIKE/GLOB, diagnostic, and optional math functions.
- Generate VDBE bytecode for foreign-key validation/actions and for the front half of INSERT processing, including input source setup, row register assembly, trigger execution, rowid/autoincrement handling, foreign-key checks, and initial constraint/unique-conflict code.

The code is compiler-oriented: most routines do not directly mutate btrees at C runtime. Instead they append VDBE opcodes (`OP_Delete`, `OP_IdxDelete`, `OP_FkCounter`, `OP_NoConflict`, `OP_VUpdate`, `OP_NewRowid`, `OP_TypeCheck`, etc.) into `Parse->pVdbe`, which later executes the statement.

## Important APIs, Types, and Functions

### DELETE/index helper tail

- `sqlite3GenerateRowIndexDelete(Parse*, Table*, int iDataCur, int iIdxCur, int *aRegIdx, int iIdxNoSeek)` emits `OP_IdxDelete` for each non-primary secondary index that has an entry for the current table row. It skips indexes whose `aRegIdx[i]` is zero, the WITHOUT ROWID primary-key index, and the `iIdxNoSeek` optimization cursor. It uses `sqlite3GenerateIndexKey()` to build index records and resolves partial-index skip labels afterward.
- `sqlite3GenerateIndexKey(Parse*, Index*, int iDataCur, int regOut, int prefixOnly, int *piPartIdxLabel, Index *pPrior, int regPrior)` loads indexed columns or expressions from the data cursor into temporary registers, optionally emits `OP_MakeRecord`, handles partial-index predicates via `sqlite3ExprIfFalseDup()`, and avoids reloading shared columns from a prior index when safe.
- `sqlite3ResolvePartIdxLabel()` resolves the partial-index jump label returned by `sqlite3GenerateIndexKey()`.
- The visible tail of `sqlite3GenerateRowDelete()` populates `OLD.*` registers for triggers/FKs, runs BEFORE DELETE triggers, reseeks if triggers may have moved/deleted the row, calls `sqlite3FkCheck()`, deletes index/table entries, calls `sqlite3FkActions()` for cascade/set-null/set-default, and finally runs AFTER DELETE triggers.

### Built-in SQL functions

- Scalar function callbacks include `minmaxFunc`, `typeofFunc`, `subtypeFunc`, `lengthFunc`, `bytelengthFunc` (`octet_length`), `absFunc`, `instrFunc`, `printfFunc`/`format`, `substrFunc`/`substring`, `roundFunc`, `upperFunc`, `lowerFunc`, `randomFunc`, `randomBlob`, `last_insert_rowid`, `changes`, `total_changes`, `nullifFunc`, `versionFunc`, `sourceidFunc`, `errlogFunc`, `quoteFunc`, `unistrFunc`, `unicodeFunc`, `charFunc`, `hexFunc`, `unhexFunc`, `zeroblobFunc`, `replaceFunc`, `trimFunc`, `concatFunc`, `concatwsFunc`, `signFunc`, and optional `soundexFunc`, `loadExt`, math functions, and debug helpers.
- Pattern matching is implemented by `struct compareInfo`, `patternCompare()`, `sqlite3_strglob()`, `sqlite3_strlike()`, and `likeFunc()`. `sqlite3RegisterLikeFunctions()` installs case-sensitive or case-insensitive LIKE definitions, while `sqlite3IsLikeFunction()` exposes wildcard metadata for planner LIKE optimization.
- Aggregate/window state types include `SumCtx`, `CountCtx`, and `GroupConcatCtx`. Step/final/value/inverse callbacks implement `sum`, `total`, `avg`, `count`, `min`, `max`, `group_concat`, and `string_agg`.
- `sqlite3RegisterBuiltinFunctions()` builds the global `FuncDef aBuiltinFunc[]` array and registers regular, inline, deterministic, volatile, aggregate, LIKE, optional compile-option, optional extension-loading, optional math, debug, JSON/date/window/alter functions. `sqlite3RegisterPerConnectionBuiltinFunctions()` overloads `MATCH` per connection.

### Foreign-key code generation

- `sqlite3FkLocateIndex()` validates that a parent key maps to an INTEGER PRIMARY KEY or a UNIQUE/PRIMARY KEY index with matching columns and default collations. It returns an optional `Index*` and, for composite keys, an allocated child-column mapping.
- `fkLookupParent()` emits code for child-table changes (`I.1`/`D.1`): skip NULL child keys, search the parent table or index, and increment/decrement immediate or deferred FK counters or halt immediately for simple single-row immediate violations.
- `fkScanChildren()` emits a WHERE scan over child rows for parent-table changes (`I.2`/`D.2`), building expressions with parent-key affinity/collation and incrementing/decrementing FK counters for matches.
- `sqlite3FkCheck()` is the central INSERT/DELETE/UPDATE FK compiler. It loops over FKs where `pTab` is child and over FKs where `pTab` is parent, avoids unchanged UPDATE keys, honors disabled triggers/drop-table special cases, handles authorization `SQLITE_IGNORE`, and delegates to `fkLookupParent()`/`fkScanChildren()`.
- `sqlite3FkOldmask()` returns a bitmask of old-row columns needed for FK processing during UPDATE/DELETE.
- `sqlite3FkRequired()` tells UPDATE/DELETE code whether FK work is needed, returning `2` for cases that require stronger handling because parent actions or self-referential updates are involved.
- `fkActionTrigger()` synthesizes and caches internal `Trigger` objects that implement ON DELETE/ON UPDATE `CASCADE`, `SET NULL`, `SET DEFAULT`, and `RESTRICT`.
- `sqlite3FkActions()` invokes synthesized action triggers for affected parent rows.
- `sqlite3FkDropTable()`, `sqlite3FkClearTriggerCache()`, `fkTriggerDelete()`, and `sqlite3FkDelete()` handle drop-time FK checks, schema-change trigger-cache invalidation, and FK memory cleanup.

### INSERT and constraint code

- `sqlite3OpenTable()` emits read/write cursor opens for rowid tables or WITHOUT ROWID primary-key indexes and adds shared-cache table locks.
- `sqlite3IndexAffinityStr()`, `computeIndexAffStr()`, `sqlite3TableAffinityStr()`, and `sqlite3TableAffinity()` compute/apply index/table affinities or STRICT table `OP_TypeCheck`.
- `sqlite3ComputeGeneratedColumns()` computes generated column values, tracking loops among generated expressions and respecting virtual/stored column behavior.
- AUTOINCREMENT helpers `autoIncBegin()`, `sqlite3AutoincrementBegin()`, `autoIncStep()`, `autoIncrementEnd()`, and `sqlite3AutoincrementEnd()` read/update `sqlite_sequence` state through VDBE code.
- `sqlite3MultiValues()` optimizes multi-row `VALUES` input with a coroutine when safe, otherwise falls back to `UNION ALL`.
- `sqlite3Insert()` is the main INSERT compiler. It resolves the target, authorization, views/triggers, xfer optimization, autoincrement state, column-list mapping, SELECT/VALUES/default sources, temp-table materialization when the SELECT reads the destination, cursor opens, UPSERT target analysis, row register assembly, BEFORE/AFTER trigger calls, rowid generation, generated columns, virtual-table `OP_VUpdate`, ordinary-table constraints/FKs/insertion, row counting, and cleanup.
- `sqlite3ExprReferencesUpdatedColumn()` and its walker callback determine whether CHECK constraints or expression indexes reference columns changed by an UPDATE.
- `IndexIterator`/`IndexListTerm` allow `sqlite3GenerateConstraintChecks()` to visit indexes in UPSERT clause order instead of raw `Table.pIndex` order.
- The visible part of `sqlite3GenerateConstraintChecks()` handles NOT NULL constraints, CHECK constraints, table record generation, index ordering/UPSERT override selection, replace-trigger recheck setup, rowid uniqueness checks, index record generation, UNIQUE/PRIMARY KEY conflict detection, and conflict actions (`ROLLBACK`, `ABORT`, `FAIL`, `IGNORE`, `REPLACE`, `UPDATE`).

## Control Flow

DELETE code generation first materializes old-row registers only when triggers or FKs need them. BEFORE triggers may invalidate the cursor position, so the code reseeks and disables the `iIdxNoSeek` optimization before FK checks and physical deletes. It deletes secondary indexes before the table row, then runs FK actions and AFTER triggers.

Built-in functions follow the SQLite callback contract: read arguments with `sqlite3_value_*`, allocate through SQLite allocators or aggregate contexts, report via `sqlite3_result_*`, and signal OOM/toobig/errors on the context. Registration is centralized in `sqlite3RegisterBuiltinFunctions()` so parser/function lookup later sees a uniform `FuncDef` table.

FK checking has two mirrored flows. For child-row insert/delete/update, it searches for the parent key and adjusts counters if the parent is absent. For parent-row insert/delete/update, it scans matching child rows and adjusts counters. UPDATEs call the same machinery twice, once as a deletion of old values and once as an insertion of new values, and helper predicates skip FKs whose key columns are unchanged.

INSERT compilation chooses one of several templates. Single-row VALUES compiles straight-line expression code. INSERT FROM SELECT either yields rows directly from a coroutine or spools them into an ephemeral table when the SELECT also reads the destination or triggers require isolation. After each source row is mapped into storage-order registers, the compiler runs BEFORE triggers, computes rowids and generated columns, checks constraints/FKs, emits the insertion, increments row counts, and loops or cleans up.

Constraint checks are layered. NOT NULL and CHECK constraints run before UNIQUE probing. For rowid tables with an explicit rowid/IPK, `OP_NotExists` checks the table btree. For indexes and WITHOUT ROWID primary keys, index records are assembled in `aRegIdx[]` registers, partial indexes may skip via their WHERE predicate, and `OP_NoConflict` probes uniqueness. Conflict handling may call UPSERT update code, jump to ignore, halt with constraint errors, or delete conflicting rows for REPLACE.

## State and Persistence Behavior

- Persistent database state changes are represented as VDBE bytecode, not direct C writes in this chunk. Table/index btree modifications later occur through opcodes such as `OP_Delete`, `OP_IdxDelete`, `OP_Insert`, `OP_VUpdate`, `OP_FkCounter`, and generated trigger subprograms.
- FK deferred state is tracked by counters: connection-level counters for deferred constraints and statement-level counters for immediate constraints. `OP_FkCounter` and `OP_FkIfZero` maintain and test this state.
- AUTOINCREMENT persistence uses `AutoincInfo` structures during compilation and emits reads/writes against `sqlite_sequence` at statement start/end.
- Built-in aggregate state persists per aggregate invocation in `sqlite3_aggregate_context()`. `SumCtx` tracks integer vs approximate Kahan-Babuska-Neumaier accumulation and overflow; `GroupConcatCtx` owns a `StrAccum` plus separator-length tracking for window inverse support; `CountCtx` tracks count and debug inverse use.
- FK action triggers are cached on `FKey.apTrigger[2]` and invalidated on schema changes or freed with the FK/table. They are heap objects that mimic real triggers but are generated internally.
- Function registration mutates global/per-connection function hash tables. Many callbacks are pure for a single invocation, but volatile functions (`random`, `randomblob`, `changes`, `last_insert_rowid`, `total_changes`) depend on connection/runtime state.

## Dependencies and Integration Points

- Heavy dependence on SQLite internals: `Parse`, `Vdbe`, `VdbeOp`, `Table`, `Column`, `Index`, `FKey`, `Trigger`, `TriggerStep`, `Expr`, `ExprList`, `Select`, `SrcList`, `NameContext`, `WhereInfo`, `FuncDef`, `sqlite3_value`, `sqlite3_context`, `StrAccum`, and memory helpers.
- VDBE opcode integration is central: the compiler emits opcodes through `sqlite3VdbeAddOp*`, labels through `sqlite3VdbeMakeLabel()`/`sqlite3VdbeResolveLabel()`, P4 payloads such as `P4_TABLE`, `P4_COLLSEQ`, `P4_VTAB`, and coverage/test macros.
- The query planner is used by FK parent scans through `sqlite3WhereBegin()`/`sqlite3WhereEnd()`.
- Triggers integrate through `sqlite3CodeRowTrigger()`, `sqlite3CodeRowTriggerDirect()`, `sqlite3TriggersExist()`, and trigger-program cursor locking during REPLACE-on-UPDATE.
- UPSERT integrates through `sqlite3UpsertAnalyzeTarget()`, `sqlite3UpsertOfIndex()`, and `sqlite3UpsertDoUpdate()`.
- Virtual tables integrate through `sqlite3GetVTable()`, `sqlite3VtabMakeWritable()`, and `OP_VUpdate`; UPSERT is explicitly rejected for virtual tables in this span.
- Optional compile-time features shape the compiled surface: `SQLITE_OMIT_FLOATING_POINT`, `SQLITE_OMIT_WINDOWFUNC`, `SQLITE_OMIT_TRIGGER`, `SQLITE_OMIT_FOREIGN_KEY`, `SQLITE_OMIT_LOAD_EXTENSION`, `SQLITE_SOUNDEX`, `SQLITE_ENABLE_MATH_FUNCTIONS`, `SQLITE_ENABLE_PREUPDATE_HOOK`, `SQLITE_ENABLE_UNKNOWN_SQL_FUNCTION`, `SQLITE_DEBUG`, and others.

## Risks and Edge Cases

- Register layout is fragile. Many routines rely on row registers being `rowid, col0, col1, ...` with storage-order remapping via `sqlite3TableColumnToStorage()`. Generated/hidden/virtual columns and BEFORE triggers make this especially sensitive.
- Partial-index code must resolve labels after index-key generation. Incorrect label handling could skip deletes or uniqueness checks.
- `sqlite3GenerateIndexKey()` deliberately drops `OP_RealAffinity` before rebuilding index keys. Changes here could corrupt index representation for REAL-affinity columns stored compactly as integers.
- `patternCompare()` can be O(N^2) and recursive for wildcard-heavy LIKE/GLOB patterns; `likeFunc()` mitigates via `SQLITE_LIMIT_LIKE_PATTERN_LENGTH`.
- Text/blob functions frequently rely on `sqlite3_value_text()` followed by `sqlite3_value_bytes()` without invalidating pointers. Assertions document assumptions, but encoding conversions and OOM paths are critical.
- `absFunc()` handles `SMALLEST_INT64` as an overflow error; random integer generation masks that same impossible absolute-value case.
- `replaceFunc()`, `concatFuncCore()`, `quoteFunc()`, and aggregate accumulation must respect `SQLITE_LIMIT_LENGTH` and propagate OOM/toobig through result contexts.
- FK mismatch detection depends on parent-key uniqueness, column count, and default collation. Accepting an expression or partial index for FK enforcement would be invalid and is deliberately rejected.
- Drop-table FK handling disables triggers but keeps FK actions active; schema changes cannot be rolled back by statement transactions, so immediate FK violations must be detected before schema mutation.
- Internal FK action triggers are cached and must be cleared on schema change to avoid stale expression/table metadata.
- REPLACE conflict handling can fire delete triggers or FK actions, requiring uniqueness rechecks after triggers because side effects may create new conflicts. The visible code sets up `regTrigCnt`, `addrRecheck`, and `lblRecheckOk` for that later second pass.
- UPSERT ordering is non-trivial: IPK conflicts may be delayed behind targeted ON CONFLICT clauses, and duplicate conflict targets are ignored in the custom index iterator.
- WITHOUT ROWID tables share primary-key cursor semantics with index cursors; REPLACE optimization can skip explicit conflict detection only under narrow conditions and not with pre-update hooks.

## Test Signals

- Existing instrumentation uses `assert()`, `testcase()`, `VdbeCoverage()`, `VdbeCoverageIf()`, `VdbeModuleComment()`, and `VdbeNoopComment()` heavily. These are strong signals that SQLite's TH3/TCL test suites exercise branch coverage and opcode paths.
- Comments reference specific evidence/test requirements, including API behavior requirements (`IMP:`/`EVIDENCE-OF:`) and `TH3 withoutrowid04.test` for WITHOUT ROWID update conflict handling.
- Important behavior to validate around this span includes DELETE with BEFORE/AFTER triggers and FK actions, partial-index delete/update, generated column INSERT, STRICT table type checks, AUTOINCREMENT sequence updates, INSERT SELECT self-read temp-table materialization, UPSERT target ordering, REPLACE with recursive triggers/FKs, deferred vs immediate FK counters, LIKE/GLOB escape and pattern-length failures, aggregate window inverse behavior, and scalar edge cases such as `abs(-9223372036854775808)`, malformed `unistr()`, invalid `unhex()`, and length/encoding conversions.

## Chunk Boundary Notes

- The chunk begins in the middle of `sqlite3GenerateRowDelete()` and therefore inherits setup from previous lines, including cursor/opening assumptions and `iPk`/`nPk`/`opSeek` initialization.
- The chunk ends in the middle of `sqlite3GenerateConstraintChecks()`, immediately after generating REPLACE conflict logic for UNIQUE indexes and before the later recheck/finalization portions of that routine. The later chunk should verify how `addrRecheck`, `lblRecheckOk`, `seenReplace`, `pbMayReplace`, generated table records, and `aRegIdx[]` outputs are finalized.
