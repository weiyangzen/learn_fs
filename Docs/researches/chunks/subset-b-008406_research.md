# sources/storage-engines/foundationdb/contrib/sqlite/sqlite3.amalgamation.c lines 1-6110

## Scope

This chunk covers the beginning of the FoundationDB-vendored SQLite 3.7.6 amalgamation. It includes the local compile-time settings, the embedded internal header stack (`sqliteInt.h`, `sqliteLimit.h`, `hash.h`, `parse.h`, `btree.h`, `vdbe.h`, `pager.h`, `pcache.h`, `os.h`, `mutex.h`), the main in-memory schema/parser/VDBE declarations, `global.c`, `ctime.c`, and the start of `status.c` through the early private VDBE runtime definitions.

## Purpose

The covered lines establish the compilation contract and most of the private type/API surface used by the rest of the amalgamation. They do not implement full SQL execution yet; instead they define the limits, tokens, opcodes, subsystem APIs, global configuration, and central runtime structures that later source sections consume.

The top of the file is FoundationDB-specific compared with a stock SQLite amalgamation:

- `NDEBUG` is force-defined before the normal SQLite debug negotiation.
- `SQLITE_THREADSAFE` is set to `0`, selecting a non-threadsafe/no-mutex build at compile time.
- `ENABLE_SCRATCHALLOC_CHECK` is set to `0`.
- `SQLITE_OMIT_SHARED_CACHE` is set to `1`.
- `SQLITE_FILE_HEADER` is changed to `"FoundationDB100"`, which affects database file identity and is a persistence compatibility boundary.
- `HAVE_USLEEP` is set to `1`.

The chunk then sets `SQLITE_CORE`, `SQLITE_AMALGAMATION`, `SQLITE_PRIVATE`, and `SQLITE_API`, making the rest of the file compile as SQLite core code in a single translation unit.

## Compile-Time Limits and Configuration

`sqliteLimit.h` defines the core size and complexity limits that later parser, VDBE, pager, and schema code enforce or assume:

- `SQLITE_MAX_LENGTH`, `SQLITE_MAX_SQL_LENGTH`, and `SQLITE_MAX_LIKE_PATTERN_LENGTH` bound input, row, and pattern sizes.
- `SQLITE_MAX_COLUMN`, `SQLITE_MAX_FUNCTION_ARG`, `SQLITE_MAX_VARIABLE_NUMBER`, `SQLITE_MAX_COMPOUND_SELECT`, and `SQLITE_MAX_EXPR_DEPTH` bound parse tree and VM complexity.
- `SQLITE_DEFAULT_CACHE_SIZE`, `SQLITE_DEFAULT_TEMP_CACHE_SIZE`, `SQLITE_DEFAULT_WAL_AUTOCHECKPOINT`, and page-size constants influence default pager/cache behavior.
- `SQLITE_MAX_PAGE_SIZE` is forcibly set to `65536` even if previously defined, preserving page-format compatibility assumptions.
- `SQLITE_MAX_ATTACHED` is capped at the default 10, with comments noting a hard 30 limit due to bitmaps.
- `SQLITE_DEFAULT_AUTOVACUUM`, `SQLITE_TEMP_STORE`, `SQLITE_DEFAULT_RECURSIVE_TRIGGERS`, file-format constants, and default page/count settings define initial database behavior.

The chunk also defines portability and instrumentation macros:

- Large-file support macros (`_FILE_OFFSET_BITS=64`, `_LARGEFILE_SOURCE`) unless disabled.
- `SQLITE_INT_TO_PTR` and `SQLITE_PTR_TO_INT` variants for compiler-specific pointer/integer casts.
- `ALWAYS`, `NEVER`, `testcase`, `TESTONLY`, and `VVA_ONLY` for defensive code and coverage/debug builds.
- Endianness macros, integer typedefs (`i64`, `u64`, `u32`, `u16`, `u8`, etc.), alignment macros, and integer bounds.
- `SQLITE_DEFAULT_MEMSTATUS` is locally defaulted to `0` with an explicit FIXME noting that enabling it would improve memory tracking for SQLite threads but causes mutex contention. In this build, `SQLITE_THREADSAFE=0` and omitted mutexes make that tradeoff especially important to validate against the wider FoundationDB integration.

## Important Types and Interfaces

### Hash Tables

The embedded `hash.h` defines:

- `Hash`, a generic hash table with a global doubly linked element list plus optional bucket table.
- `HashElem`, storing linked-list pointers, `data`, and key bytes.
- `sqlite3HashInit`, `sqlite3HashInsert`, `sqlite3HashFind`, and `sqlite3HashClear`.
- Iteration macros `sqliteHashFirst`, `sqliteHashNext`, and `sqliteHashData`.

These hash tables are later used for schemas, functions, collations, triggers, foreign keys, and virtual table modules.

### Parser Tokens and VDBE Opcodes

`parse.h` maps SQL grammar tokens (`TK_SELECT`, `TK_INSERT`, `TK_VARIABLE`, `TK_FUNCTION`, etc.) to integer constants. Expression nodes reuse these token numbers as expression opcodes.

`vdbe.h` defines the public-internal VDBE instruction surface:

- `Vdbe`, `VdbeOp`, `VdbeOpList`, `SubProgram`, `Mem`, `VdbeFunc`.
- `VdbeOp` fields: `opcode`, `p1`, `p2`, `p3`, `p4`, `p4type`, `p5`, and optional debug/profile fields.
- `P4_*` ownership/type constants, including dynamic/static strings, collations, function definitions, key info, memory cells, virtual tables, integer/real payloads, and trigger subprograms.
- `COLNAME_*` result metadata slots.
- `ADDR()` relative-address encoding used by `sqlite3VdbeAddOpList()`.
- `opcodes.h` constants from `OP_Goto` through `OP_Explain`, plus `OPFLG_*` metadata and `OPFLG_INITIALIZER`.
- VDBE construction and mutation APIs such as `sqlite3VdbeCreate`, `sqlite3VdbeAddOp*`, `sqlite3VdbeChangeP*`, `sqlite3VdbeMakeReady`, `sqlite3VdbeFinalize`, `sqlite3VdbeReset`, `sqlite3VdbeSetColName`, `sqlite3VdbeRecordUnpack`, and `sqlite3VdbeRecordCompare`.

The opcode list shows the control-flow bridge between parser/codegen and persistence: transaction opcodes (`OP_Transaction`, `OP_Savepoint`, `OP_AutoCommit`), B-tree cursor opcodes (`OP_OpenRead`, `OP_OpenWrite`, `OP_Seek*`, `OP_Insert`, `OP_Delete`), schema opcodes (`OP_CreateTable`, `OP_ParseSchema`, `OP_DropTable`), WAL/checkpoint opcodes, virtual table opcodes, and trigger/subprogram opcodes.

### B-tree, Pager, Page Cache, and VFS

`btree.h` exposes the logical storage layer:

- Open/close/configuration APIs: `sqlite3BtreeOpen`, `sqlite3BtreeClose`, `sqlite3BtreeSetCacheSize`, `sqlite3BtreeSetSafetyLevel`, `sqlite3BtreeSetPageSize`, `sqlite3BtreeMaxPageCount`.
- Transaction APIs: `sqlite3BtreeBeginTrans`, `sqlite3BtreeCommitPhaseOne`, `sqlite3BtreeCommitPhaseTwo`, `sqlite3BtreeCommit`, `sqlite3BtreeRollback`, `sqlite3BtreeBeginStmt`, `sqlite3BtreeSavepoint`.
- Schema/meta APIs: `sqlite3BtreeGetMeta`, `sqlite3BtreeUpdateMeta`, `sqlite3BtreeSchema`, `sqlite3BtreeSchemaLocked`, `BTREE_*` meta indices.
- Cursor APIs: `sqlite3BtreeCursor`, `sqlite3BtreeMovetoUnpacked`, `sqlite3BtreeInsert`, `sqlite3BtreeDelete`, `sqlite3BtreeFirst/Next/Last/Previous`, key/data fetch APIs, and rowid cache APIs.
- Integrity and vacuum APIs: `sqlite3BtreeIntegrityCheck`, `sqlite3BtreeIncrVacuum`, `sqlite3BtreeSetAutoVacuum`, `sqlite3BtreeGetAutoVacuum`.

`pager.h` exposes file-page persistence and rollback/WAL behavior:

- `Pager` and `DbPage` types.
- Journal mode constants `PAGER_JOURNALMODE_DELETE`, `PERSIST`, `OFF`, `TRUNCATE`, `MEMORY`, and `WAL`.
- Open/configuration APIs: `sqlite3PagerOpen`, `sqlite3PagerClose`, `sqlite3PagerSetBusyhandler`, `sqlite3PagerSetPagesize`, `sqlite3PagerSetCachesize`, `sqlite3PagerSetSafetyLevel`, `sqlite3PagerLockingMode`, `sqlite3PagerSetJournalMode`.
- Page access APIs: `sqlite3PagerAcquire`, `sqlite3PagerGet`, `sqlite3PagerLookup`, `sqlite3PagerRef`, `sqlite3PagerUnref`, `sqlite3PagerWrite`, `sqlite3PagerDontWrite`, `sqlite3PagerMovepage`, `sqlite3PagerGetData`, `sqlite3PagerGetExtra`.
- Transaction APIs: `sqlite3PagerBegin`, `sqlite3PagerCommitPhaseOne`, `sqlite3PagerCommitPhaseTwo`, `sqlite3PagerRollback`, savepoint APIs, shared/exclusive locking APIs, and checkpoint/WAL APIs.

`pcache.h` defines `PgHdr` and `PCache`:

- `PgHdr` stores `pData`, `pExtra`, dirty-list links, page number, owning `Pager`, flags, refcount, and cache pointer.
- Flags include `PGHDR_DIRTY`, `PGHDR_NEED_SYNC`, `PGHDR_NEED_READ`, `PGHDR_DONT_WRITE`, and a FoundationDB-visible addition `PGHDR_ZERO_COPY`, used for pages read through `xReadZeroCopy` and released with `xReleaseZeroCopy`.
- APIs cover page cache initialization, buffer setup, fetch/release/drop/dirty/clean/move/truncate, dirty-list retrieval, refcounting, cache-size hints, memory release, and test stats.

`os.h` abstracts platform I/O:

- Detects Unix, Windows, OS/2, or other VFS targets.
- Defines lock levels (`NO_LOCK`, `SHARED_LOCK`, `RESERVED_LOCK`, `PENDING_LOCK`, `EXCLUSIVE_LOCK`) and lock-byte layout (`PENDING_BYTE`, `RESERVED_BYTE`, `SHARED_FIRST`, `SHARED_SIZE`).
- Provides `sqlite3Os*` wrappers around `sqlite3_file` and `sqlite3_vfs` methods, including read/write/truncate/sync/lock/shm/randomness/sleep/time/open/delete/access/full-pathname/dlopen support.
- Defines `SQLITE_FCNTL_DB_UNCHANGED`, which is an integration hook for file-control behavior.

### Mutexes and Threading

Because this file sets `SQLITE_THREADSAFE 0`, `mutex.h` selects `SQLITE_MUTEX_OMIT`. In this mode all public/internal mutex operations become no-op macros and `sqlite3_mutex_alloc()` returns a sentinel pointer. Shared-cache enter/leave macros are also no-ops because `SQLITE_OMIT_SHARED_CACHE` is set.

This substantially narrows the valid embedding model: the same SQLite build must not be used concurrently through shared mutable state unless the caller provides stronger external serialization.

### Core Database and Schema Structures

The chunk defines central durable/in-memory metadata structures:

- `Db`: per-attached-database handle with `zName`, `Btree *pBt`, transaction state, safety level, and `Schema *pSchema`.
- `Schema`: schema cookie, table/index/trigger/foreign-key hash tables, autoincrement sequence table, file format, encoding, flags, and cache size.
- `sqlite3`: the database connection object. It stores VFS, `Db` array, flags, autocommit state, error state, limits, initialization state, active VDBEs, callbacks, lookaside allocator, authorization/progress/virtual table state, function/collation registries, busy handler, default backends, savepoints, deferred FK counters, and optional unlock-notify state.
- `Lookaside` and `LookasideSlot`: fixed-size per-connection allocator state.
- `BusyHandler`: pager-invoked busy callback state.
- `FuncDef`, `FuncDestructor`, `FuncDefHash`: SQL function definitions, aggregate/finalizer callbacks, collations-needed flag, destructor reference counting, and hash-chain layout.
- `Savepoint`: transaction savepoint list and deferred-constraint counter snapshot.
- `Module` and `VTable`: virtual table module registrations and per-connection virtual table handles.
- `Column`, `Table`, `Index`, `IndexSample`, `FKey`, and `KeyInfo`: schema objects used to map SQL definitions to B-tree roots, column affinity/collation, index key layouts, FK actions, ANALYZE samples, and record comparison behavior.

The connection flags define behavior toggles and test controls, including column naming, count rows, writable schema, omitted read locks, full fsync/checkpoint fsync, recovery mode, reverse order, recursive triggers, foreign keys, automatic indexes, preference to built-ins, and loadable extension enablement.

### Parse Tree, Planner, and Codegen Structures

The chunk defines parser and planner state used later by expression analysis and VDBE code generation:

- `Token`: lexer slice.
- `AggInfo`: aggregate-function and aggregate-column bookkeeping, including sorting-index use and accumulator registers.
- `Expr`: expression-tree nodes with token/int payloads, child pointers, function/list/select union, collation, cursor/column/register info, aggregate info, table pointer, and optional height tracking.
- `Expr` flags such as `EP_Agg`, `EP_Resolved`, `EP_Error`, `EP_Distinct`, `EP_VarSelect`, `EP_ExpCollate`, `EP_IntValue`, `EP_xIsSelect`, `EP_Reduced`, `EP_TokenOnly`, and `EP_Static`.
- `ExprList`, `ExprSpan`, and `IdList`: lists of expressions, spanned parse fragments, and identifier lists.
- `SrcList`: FROM clauses or target table references, including database/table/alias names, subquery pointer, join metadata, cursor number, ON/USING clauses, column-use bitmask, and `INDEXED BY` binding.
- Join type flags `JT_INNER`, `JT_CROSS`, `JT_NATURAL`, `JT_LEFT`, `JT_RIGHT`, `JT_OUTER`, and `JT_ERROR`.
- `WherePlan`, `WhereLevel`, and `WhereInfo`: selected lookup strategy, nested-loop VDBE addresses, IN-loop state, virtual-table index info, one-pass flags, and output cardinality estimates.
- `NameContext`: nested name-resolution scope with FROM sources, result aliases, aggregate allowance, aggregate info, and recursion depth.
- `Select` and `SelectDest`: SELECT tree representation and result disposition (`SRT_Output`, `SRT_Table`, `SRT_EphemTab`, `SRT_Set`, `SRT_Union`, `SRT_Except`, `SRT_Coroutine`, etc.).
- `AutoincInfo`: per-autoincrement-table codegen state.
- `Trigger`, `TriggerStep`, `TriggerPrg`: trigger metadata, program-step lists, generated subprogram cache, conflict policy, and old/new column masks.
- `Parse`: the main parser/codegen context, including VDBE pointer, temp registers, cursor and memory counters, schema cookie verification, write masks, trigger state, query-loop estimates, bind variable bookkeeping, virtual table declaration state, zombie table list, and EXPLAIN select IDs.
- `DbFixer`, `StrAccum`, `InitData`, `Walker`, and walk return codes for tree rewriting, string accumulation, schema initialization callbacks, and parse-tree traversal.

## Control Flow and Data Flow

This chunk defines the skeleton used by later implementation sections:

1. SQL text is tokenized into `Token` values whose numeric kinds are defined in `parse.h`.
2. The Lemon parser builds `Expr`, `ExprList`, `SrcList`, `Select`, `Table`, `Index`, `Trigger`, and related objects inside a `Parse` context.
3. Name resolution uses nested `NameContext` objects and records resolved columns in `Expr.iTable`, `Expr.iColumn`, `Expr.pTab`, and aggregate fields.
4. Code generation emits `VdbeOp` instructions using `sqlite3VdbeAddOp*` and edits operands with `sqlite3VdbeChangeP*`.
5. The VDBE runs opcodes against `VdbeCursor` objects, `Mem` registers, `Btree` cursors, and the pager/page-cache stack.
6. Persistent pages move through `Pager` and `PCache`; dirty pages, journals, savepoints, WAL checkpoints, and page-size/file-format metadata are all exposed through the declared APIs.
7. Schema changes update `Schema` hash tables, database cookies, B-tree metadata, and eventually `sqlite_master`/`sqlite_temp_master`.

No full algorithm implementations appear in most of this chunk; it is mostly declarations and data model. The implementations begin with `global.c`, `ctime.c`, and the start of `status.c`/`vdbeInt.h`.

## State and Persistence Behavior

Important stateful and persistent surfaces in this chunk include:

- `SQLITE_FILE_HEADER "FoundationDB100"` changes the on-disk database header string from stock SQLite, making file compatibility an explicit integration contract.
- `Db.inTrans`, `sqlite3.autoCommit`, savepoint fields, deferred FK counters, and VDBE statement fields coordinate transaction state.
- `Schema.schema_cookie`, `Schema.file_format`, `Schema.enc`, `Db.pSchema`, and B-tree metadata indices (`BTREE_SCHEMA_VERSION`, `BTREE_FILE_FORMAT`, etc.) describe persistent schema state.
- `Pager` journal modes, savepoints, WAL open/close/checkpoint functions, sync configuration, locking mode, and journal-size limits are the persistence safety layer exposed to later code.
- `PgHdr` flags track dirty/needs-sync/needs-read/do-not-write pages, and `PGHDR_ZERO_COPY` adds a special page ownership/release path.
- `sqlite3PendingByte` defaults to `0x40000000`; comments state changing it creates incompatible database files and undefined behavior while operating.
- `sqlite3Config` is writable-static global configuration unless `SQLITE_OMIT_WSD` is enabled. It stores memory, mutex, page-cache, scratch, lookaside, shared-cache, init-state, and logging hooks.
- `sqlite3GlobalFunctions` is the process-global function registry, initialized once then treated as read-only.
- `sqlite3UpperToLower`, `sqlite3CtypeMap`, `sqlite3OpcodeProperty`, and `sqlite3IntTokens` are global constant lookup tables used by lexer, expression, and VDBE machinery.

## Dependencies and Integration Points

Internal subsystem dependencies visible here:

- `sqliteInt.h` is the hub: it includes limits, hash, parser token definitions, B-tree, VDBE, pager, page cache, OS, and mutex declarations.
- `Btree` depends on `Pager` for page persistence and on `BtCursor`/`KeyInfo`/`UnpackedRecord` for logical table/index access.
- `Pager` depends on `sqlite3_vfs` and `sqlite3_file` for platform I/O and on `DbPage`/`PgHdr` for cache/page ownership.
- `PCache` depends on pager callbacks for stress/dirty page cleaning.
- `Vdbe` depends on parser/codegen structures, B-tree cursors, `Mem`, functions, collations, virtual table modules, and transaction state.
- Virtual table support integrates through `sqlite3_module`, `sqlite3_vtab`, `sqlite3_vtab_cursor`, `sqlite3_index_info`, and VDBE virtual table opcodes.
- Optional features are compiled in or out via macros: WAL, shared cache, virtual tables, triggers, foreign keys, authorization, load extensions, column metadata, floating point, memory management, unlock notify, and tests.
- The compile-option diagnostics API (`sqlite3_compileoption_used`, `sqlite3_compileoption_get`) exposes selected build macros to callers unless `SQLITE_OMIT_COMPILEOPTION_DIAGS` is defined. For this build it can report items such as `THREADSAFE=0`, `OMIT_SHARED_CACHE`, and `TEMP_STORE=...` when those macros are present.

FoundationDB-specific integration signals:

- The file header and zero-copy page flag suggest a custom storage/VFS compatibility layer elsewhere in the repository.
- The non-threadsafe build and omitted shared cache reduce SQLite internal synchronization cost, presumably relying on external scheduling/serialization in FoundationDB's usage.
- The memory-status FIXME is a known performance-observability tradeoff.

## APIs and Functions Declared in This Chunk

The chunk declares many private APIs. The most important groups are:

- Memory: `sqlite3MallocInit`, `sqlite3Malloc`, `sqlite3DbMallocZero`, `sqlite3DbMallocRaw`, `sqlite3DbRealloc`, `sqlite3DbFree`, scratch/page allocators, heap pressure, benign malloc hooks, and memdebug type tracking.
- Parsing and schema: `sqlite3RunParser`, `sqlite3FinishCoding`, `sqlite3BeginParse`, `sqlite3Init`, `sqlite3InitCallback`, `sqlite3ReadSchema`, table/index/view/trigger creation and deletion APIs, `sqlite3Pragma`, `sqlite3NestedParse`.
- Expressions: `sqlite3ExprAlloc`, `sqlite3Expr`, `sqlite3PExpr`, `sqlite3ExprFunction`, `sqlite3ExprDelete`, duplication, affinity, collation, constant/null/integer checks, codegen, conditional jumps, and aggregate analysis.
- DML and query planning: `sqlite3Insert`, `sqlite3DeleteFrom`, `sqlite3Update`, `sqlite3Select`, `sqlite3WhereBegin`, `sqlite3WhereEnd`, `sqlite3GenerateConstraintChecks`, `sqlite3CompleteInsertion`, row/index delete and key generation helpers.
- Transactions: `sqlite3BeginTransaction`, `sqlite3CommitTransaction`, `sqlite3RollbackTransaction`, `sqlite3Savepoint`, `sqlite3CloseSavepoints`, `sqlite3RollbackAll`.
- Foreign keys/triggers/virtual tables: `sqlite3FkCheck`, `sqlite3FkActions`, `sqlite3Vtab*` APIs, `sqlite3CodeRowTrigger`, `sqlite3TriggerColmask`, and no-op macro replacements under omit flags.
- Utility: varint encode/decode, UTF-8 helpers, numeric conversion, string accumulation, error reporting, busy-handler invocation, schema/index lookup, compile-option diagnostics, backup update/restart, parser allocation/free/drive APIs.

## Runtime Structures in the `status.c` / `vdbeInt.h` Opening

The last part of the chunk enters `status.c` and includes private VDBE runtime definitions:

- `VdbeCursor`: VM cursor state over a B-tree or virtual table. It tracks cursor type, table/index flags, rowid validity, deferred seeks, pseudo-table register, key info, sequence counter, seek result, and a cached record header (`aType`, `aOffset`, `aRow`, `payloadSize`, `cacheStatus`).
- `VdbeFrame`: saved VM execution frame for trigger subprograms or `OP_Program`. It snapshots parent op array, memory cells, cursors, program counter, rowid/change counters, and parent frame link. Frame memory is embedded after the aligned `VdbeFrame` header.
- `Mem`: the core SQL value cell. It may hold NULL, string, integer, real, blob, rowset, frame, aggregate context, zero-blob count, encodings, destructor policy, malloc buffer, and debug shallow-copy tracking.
- `VdbeFunc`: wraps a `FuncDef` with per-argument auxdata destructors for `sqlite3_get_auxdata()` / `sqlite3_set_auxdata()` behavior.
- `sqlite3_context`: SQL function callback context containing the function definition, auxdata wrapper, return `Mem`, aggregate `Mem`, error code, and collation.
- `Vdbe`: complete statement state including program opcodes, registers, arguments, result columns, cursors, bindings, program counter, return code, error action, explain/read-only/expired flags, statement journal state, FK counters, SQL text, debug trace, trigger frames, variable invalidation mask, and linked subprograms.

These declarations are critical for later `sqlite3_step()` behavior: opcode execution mutates `Vdbe.aMem`, `Vdbe.apCsr`, `Vdbe.pc`, `Vdbe.rc`, transaction counters, and frame stacks while reading/writing B-tree pages through the pager.

## Risks and Edge Cases

- The `SQLITE_FILE_HEADER` change makes this SQLite build incompatible with default SQLite database files unless surrounding code intentionally handles the custom header.
- `SQLITE_THREADSAFE=0` and `SQLITE_MUTEX_OMIT` remove SQLite's internal mutex protection. Any accidental cross-thread use of a connection, global config, pager, or shared structures can become undefined behavior.
- `SQLITE_OMIT_SHARED_CACHE=1` compiles shared-cache locks and enter/leave calls away. Code paths that assume shared-cache semantics must be disabled or externally guarded.
- `SQLITE_DEFAULT_MEMSTATUS=0` suppresses default memory-status tracking. This can hide memory accounting details while improving performance.
- Page-size and pending-byte constants are on-disk compatibility boundaries. The comments explicitly warn that changing `PENDING_BYTE` creates incompatible files and undefined behavior.
- `PGHDR_ZERO_COPY` adds an ownership constraint: pages read through zero-copy I/O must be released through the matching VFS method. Bugs here risk leaks, use-after-release, or stale page contents.
- Many structures use flexible trailing arrays (`a[1]`, `aCol[1]`, `aColl[1]`, `apAux[1]`). Allocation size calculations must be exact.
- `Expr` supports reduced/token-only allocation forms. Accessing fields beyond the allocated prefix when `EP_Reduced` or `EP_TokenOnly` is set is explicitly unsafe.
- `VdbeOp.p4` ownership is encoded by negative `P4_*` constants. Mismatches can leak memory, double-free dynamic strings/key info, or retain ephemeral pointers.
- `Mem` string/blob ownership is encoded with flags (`MEM_Dyn`, `MEM_Static`, `MEM_Ephem`, `MEM_Term`, `MEM_Zero`). Incorrect flag transitions in later code can corrupt SQL values.
- The parser limits and VM op limits are compile-time values; raising them affects memory layout choices such as `ynVar` width and expression tree depth handling.
- Compile-option diagnostics rely on a manually sorted conditional array. Build flags not listed here are not visible through `sqlite3_compileoption_*`.

## Test Signals

Useful validation signals for this chunk and the surrounding amalgamation include:

- Compile the amalgamation with the repository's intended flags and confirm the top-level forced macros produce expected diagnostics.
- Call `sqlite3_compileoption_used("THREADSAFE")`, `sqlite3_compileoption_used("OMIT_SHARED_CACHE")`, and `sqlite3_compileoption_get()` in a smoke test when compile-option diagnostics are enabled.
- Verify that new database files created by this build use the `FoundationDB100` header and that stock SQLite files are rejected or converted only through intentional compatibility code.
- Exercise page-cache paths that set or observe `PGHDR_ZERO_COPY`, especially error, eviction, dirty-page, and release paths in the VFS integration.
- Run SQL parser/codegen smoke tests covering tokens and opcodes declared here: simple SELECT, INSERT/UPDATE/DELETE, transactions, savepoints, triggers, foreign keys, virtual tables if enabled, and WAL/checkpoint if enabled.
- Stress lookaside allocation and `Mem` ownership transitions with strings, blobs, zeroblobs, aggregate functions, user functions with auxdata, and malloc failure injection.
- Test expression-reduction paths under debug builds to catch invalid access beyond reduced/token-only `Expr` sizes.
- Run single-thread and accidental concurrent-access tests around the FoundationDB embedding boundary to confirm external serialization is effective for this `SQLITE_THREADSAFE=0` build.
- Confirm schema-cookie and file-format behavior using CREATE/DROP/ALTER, attached databases, temp databases, autovacuum, and savepoints.

## Unresolved Cross-Chunk References

This chunk mostly declares APIs. Implementations are expected later in the amalgamation:

- B-tree, pager, page-cache, OS/VFS, WAL, and journal behavior are declared here but implemented in later chunks.
- Parser actions, expression codegen, query planning, and VDBE opcode execution are declared here but implemented later.
- `sqlite3_status()` implementation begins after this chunk; only its include of `vdbeInt.h` and early private VDBE data structures are visible here.
- FoundationDB-specific behavior behind `SQLITE_FILE_HEADER`, `PGHDR_ZERO_COPY`, and any custom VFS/file-control methods must be reconciled with later source chunks.
