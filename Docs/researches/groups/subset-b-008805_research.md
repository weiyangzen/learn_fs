# subset-b-008805 research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/vdbemem.c -->
# sources/storage-engines/sqlite/src/vdbemem.c research

## Purpose
`vdbemem.c` implements the VDBE `Mem`/`sqlite3_value` runtime value container. It owns conversions between SQLite manifest types, text encodings, dynamic/static/ephemeral ownership modes, aggregate accumulator finalization, rowset and pointer bindings, btree payload extraction, constant-expression value materialization, and STAT4 probe-value construction. This file is on the hot path for expression evaluation, binding/result APIs, record comparison, statistics planning, and VDBE register lifetime management.

## Important APIs, types, and functions
- `Mem` is defined in VDBE internals and represented here through flags such as `MEM_Null`, `MEM_Int`, `MEM_Real`, `MEM_IntReal`, `MEM_Str`, `MEM_Blob`, `MEM_Zero`, `MEM_Agg`, `MEM_Dyn`, `MEM_Ephem`, `MEM_Static`, `MEM_Term`, `MEM_Subtype`, and `MEM_Cleared`.
- Debug validation is concentrated in `sqlite3VdbeCheckMemInvariants()` and `sqlite3VdbeMemValidStrRep()`, including dynamic ownership exclusivity, numeric/string dual-representation correctness, termination, and allocation-size invariants.
- Allocation and writeability helpers include `sqlite3VdbeMemGrow()`, `sqlite3VdbeMemClearAndResize()`, `sqlite3VdbeMemZeroTerminateIfAble()`, `sqlite3VdbeMemMakeWriteable()`, `sqlite3VdbeMemExpandBlob()`, and `sqlite3VdbeMemNulTerminate()`.
- Conversion APIs include `sqlite3VdbeChangeEncoding()`, `sqlite3VdbeMemStringify()`, `sqlite3VdbeIntValue()`, `sqlite3MemRealValueRC()`, `sqlite3VdbeRealValue()`, `sqlite3VdbeBooleanValue()`, `sqlite3VdbeIntegerAffinity()`, `sqlite3VdbeMemIntegerify()`, `sqlite3VdbeMemRealify()`, `sqlite3VdbeMemNumerify()`, and `sqlite3VdbeMemCast()`.
- Set/copy/release APIs include `sqlite3VdbeMemInit()`, `sqlite3VdbeMemSetNull()`, `sqlite3VdbeMemSetZeroBlob()`, `sqlite3VdbeMemSetInt64()`, `sqlite3VdbeMemSetPointer()`, `sqlite3VdbeMemSetDouble()`, `sqlite3VdbeMemSetRowSet()`, `sqlite3VdbeMemRelease()`, `sqlite3VdbeMemReleaseMalloc()`, `sqlite3VdbeMemShallowCopy()`, `sqlite3VdbeMemCopy()`, `sqlite3VdbeMemMove()`, `sqlite3VdbeMemSetStr()`, and `sqlite3VdbeMemSetText()`.
- External/internal `sqlite3_value` APIs include `sqlite3ValueText()`, `sqlite3ValueBytes()`, `sqlite3ValueNew()`, `sqlite3ValueSetNull()`, `sqlite3ValueSetStr()`, `sqlite3ValueFree()`, and `sqlite3ValueIsOfClass()`.
- Aggregate/window support is handled by `sqlite3VdbeMemFinalize()` and, when enabled, `sqlite3VdbeMemAggValue()`.
- Btree and STAT4 support is handled by `sqlite3VdbeMemFromBtree()`, `sqlite3VdbeMemFromBtreeZeroOffset()`, `sqlite3ValueFromExpr()`, `sqlite3Stat4ProbeSetValue()`, `sqlite3Stat4ValueFromExpr()`, `sqlite3Stat4Column()`, and `sqlite3Stat4ProbeFree()`.

## Control flow
The dominant flow is value replacement: callers first clear destructible external content with `sqlite3VdbeMemSetNull()` or release all owned memory with `sqlite3VdbeMemRelease()`, then install a new scalar/string/blob/pointer/rowset representation and update flags. String/blob assignment branches on `xDel`: transient data is copied into `zMalloc`, dynamic data is adopted, static/ephemeral data is referenced with flags, and over-limit data triggers destructor handling plus `SQLITE_TOOBIG`.

Conversion routines preserve SQLite's dual-representation rules. Numeric values can acquire a string representation through `sqlite3VdbeMemStringify()`; forced casts remove incompatible flags; `sqlite3VdbeMemNumerify()` parses text/blob values through `sqlite3MemRealValueRC()` and `sqlite3Atoi64()` and chooses integer if the parsed value is integer-exact. Encoding changes go through `sqlite3VdbeMemTranslate()` unless UTF16 is omitted.

Btree extraction first tries an ephemeral pointer for zero-offset payload available on the local page (`sqlite3VdbeMemFromBtreeZeroOffset()`), falling back to allocation and `sqlite3BtreePayload()` when the requested bytes are not contiguous. Expression materialization strips unary plus/span/collation wrappers, handles literals, casts, unary minus edge cases, blob literals, true/false, and selected constant functions for STAT4, then applies affinity and encoding.

## State and persistence behavior
`Mem` state is entirely in-memory and per connection/VDBE register, but it frequently points into persistent sources such as btree pages, SQL literal tokens, bound parameter storage, aggregate contexts, rowset objects, and dynamically owned buffers. The file enforces ownership transitions with `z`, `zMalloc`, `szMalloc`, `xDel`, and flags. Btree payload reads materialize on-page or copied bytes into a `Mem`; STAT4 helpers build `UnpackedRecord` values used by query planning, but they do not persist changes to schema tables themselves.

## Dependencies and integration points
This file depends on `sqliteInt.h` and `vdbeInt.h`, VDBE record/serial helpers, btree payload APIs, SQLite allocation APIs, UTF conversion, `sqlite3Atoi64()`/`sqlite3AtoF()`, expression and function metadata, `RowSet`, `FuncDef`, `Parse`, `Index`, `UnpackedRecord`, and compile-time feature switches such as `SQLITE_OMIT_UTF16`, `SQLITE_OMIT_INCRBLOB`, `SQLITE_OMIT_FLOATING_POINT`, `SQLITE_ENABLE_STAT4`, and `SQLITE_ENABLE_UNKNOWN_SQL_FUNCTION`. It is used by opcodes, SQL functions, binding/result APIs, sorter/record comparison, query planner STAT4 probing, and debug tracing.

## Risks and edge cases
- Ownership flags are tightly coupled; incorrect combinations can double-free, leak, or allow stale ephemeral pointers. The debug invariant checks are important but compiled out in release builds.
- String termination is subtle for UTF16 because the code adds three zero bytes and aligns double-zero terminators.
- Numeric conversion intentionally accepts partial numeric prefixes in some paths and exact integer round-trips in others; changing those rules can affect affinity, indexes, and query plans.
- `MEM_Zero` zeroblobs are lazy until expanded; callers that need actual bytes must call `ExpandBlob()`.
- `sqlite3VdbeMemFromBtree()` notes that failed reads can leave `pMem` inconsistent, so callers must obey return codes.
- STAT4 expression extraction can evaluate only constant/slow-changing scalar functions without collation/run-only requirements; expanding that set would risk planner side effects.

## Test signals
Useful coverage includes VDBE value API tests for all ownership modes, UTF8/UTF16 conversion and termination, zeroblob expansion, pointer bindings, rowset release, aggregate finalization and window `xValue`, `CAST` and affinity corner cases including `-9223372036854775808`, oversized strings/blobs against `SQLITE_LIMIT_LENGTH`, btree corrupt-record payload bounds, and STAT4 plans involving literals, bound variables on reprepare, vector probes, and constant functions. Debug builds should exercise `sqlite3VdbeCheckMemInvariants()`, shallow-copy invalidation, fault injection around allocation, and UTF16 builds.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/vdbemem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/vdbesort.c -->
# sources/storage-engines/sqlite/src/vdbesort.c research

## Purpose
`vdbesort.c` implements `VdbeSorter`, SQLite's VDBE sorter used for `CREATE INDEX` and SELECT `ORDER BY` operations that cannot be satisfied by an index and are not bounded by a LIMIT optimization. It provides an in-memory sort for small inputs and an external PMA-based merge sort for larger inputs, optionally using worker threads and memory-mapped temporary files.

## Important APIs, types, and functions
- Public internal entry points are `sqlite3VdbeSorterInit()`, `sqlite3VdbeSorterWrite()`, `sqlite3VdbeSorterRewind()`, `sqlite3VdbeSorterNext()`, `sqlite3VdbeSorterRowkey()`, `sqlite3VdbeSorterCompare()`, `sqlite3VdbeSorterReset()`, and `sqlite3VdbeSorterClose()`.
- Core structs are `VdbeSorter`, `SortSubtask`, `SorterList`, `SorterRecord`, `SorterFile`, `PmaReader`, `PmaWriter`, `MergeEngine`, and `IncrMerger`.
- PMA read/write helpers include `vdbePmaReadBlob()`, `vdbePmaReadVarint()`, `vdbePmaReaderSeek()`, `vdbePmaReaderNext()`, `vdbePmaReaderInit()`, `vdbePmaWriterInit()`, `vdbePmaWriteBlob()`, `vdbePmaWriteVarint()`, `vdbePmaWriterFinish()`, and `vdbeSorterListToPMA()`.
- Sort/compare helpers include `vdbeSorterCompare()`, `vdbeSorterCompareTail()`, optimized `vdbeSorterCompareText()` and `vdbeSorterCompareInt()`, `vdbeSorterGetCompare()`, `vdbeSorterMerge()`, and `vdbeSorterSort()`.
- Merge-tree helpers include `vdbeMergeEngineNew()`, `vdbeMergeEngineFree()`, `vdbeMergeEngineCompare()`, `vdbeMergeEngineStep()`, `vdbeMergeEngineLevel0()`, `vdbeSorterTreeDepth()`, `vdbeSorterAddToTree()`, `vdbeSorterMergeTreeBuild()`, and `vdbeSorterSetupMerge()`.
- Threaded/incremental merge support is in `vdbeSorterCreateThread()`, `vdbeSorterJoinThread()`, `vdbeSorterJoinAll()`, `vdbeSorterFlushThread()`, `vdbeSorterFlushPMA()`, `vdbeIncrPopulate()`, `vdbeIncrSwap()`, `vdbeIncrMergerNew()`, `vdbePmaReaderIncrMergeInit()`, and `vdbePmaReaderIncrInit()`.

## Control flow
The expected sequence is `Init`, repeated `Write`, `Rewind`, repeated `Rowkey`/`Compare` and `Next`, then `Reset` or `Close`. `sqlite3VdbeSorterInit()` copies `KeyInfo`, calculates PMA thresholds from page size, cache size, and `sqlite3GlobalConfig.szPma`, chooses worker-thread availability, and may allocate a bulk memory arena for records.

`sqlite3VdbeSorterWrite()` records each OP_MakeRecord blob in memory, tracking PMA size and largest key size. If memory exceeds the threshold, or the heap is nearly full, it flushes current records to a PMA. Flushing sorts the in-memory linked list using a bottom-up merge sort, writes a PMA length varint followed by sorted record-length/data pairs to a temp file, and may do this in a background `SortSubtask`.

`sqlite3VdbeSorterRewind()` either sorts the in-memory list directly if no PMAs were created, or flushes the final list, joins worker threads, and builds a merge structure. With a small single-threaded PMA count, a `MergeEngine` incrementally merges readers. With many PMAs, it builds a fanout tree of incremental mergers. With worker threads, top-level readers can be backed by double-buffered temp files populated in background threads.

Iteration reads the smallest current key either from the in-memory list, from `pMerger->aTree[1]`, or from threaded `pReader`. `sqlite3VdbeSorterCompare()` unpacks the current sorter key, treats NULL in the sorter key as less for UNIQUE-index enforcement, and compares against a candidate key ignoring the rowid tail through the supplied key-column count.

## State and persistence behavior
Sorter state is per VDBE cursor and transient. It may allocate memory through SQLite's heap, open temp files with `SQLITE_OPEN_TEMP_JOURNAL | READWRITE | CREATE | EXCLUSIVE | DELETEONCLOSE`, and optionally map sorter files using `sqlite3OsFetch()` subject to `db->nMaxSorterMmap`. `db->nSpill` is updated on close with bytes written by all subtasks. PMA files are deleted on close by VFS semantics. Worker threads own `SortSubtask` fields until joined; `bDone` is a lightweight completion flag used for scheduling and debug messages.

## Dependencies and integration points
This file depends on `sqliteInt.h`, `vdbeInt.h`, VDBE cursor/key APIs, record unpack/compare functions, SQLite VFS temp-file methods, optional mmap, the SQLite thread wrapper, page-cache configuration, database limits, and compile-time switches such as `SQLITE_MAX_WORKER_THREADS`, `SQLITE_MAX_MMAP_SIZE`, and `SQLITE_DEBUG_SORTER_THREADS`. It is driven by VDBE sorter opcodes and integrates with CREATE INDEX uniqueness checking through `sqlite3VdbeSorterCompare()`.

## Risks and edge cases
- PMA format and read offsets are sensitive to varint size, EOF values, and page-size buffering. Any off-by-one can corrupt sorted output or cause IO errors.
- Thread joins are carefully ordered to avoid races when the final subtask may be joining other workers during rewind.
- Incremental merge double-buffering uses two temp files and swaps file descriptors; incorrect EOF or size handling can loop forever or skip data.
- Optimized integer/text comparators assume specific record serial-type layouts, default binary collation, no `KEYINFO_ORDER_BIGNULL`, and limited key-field counts. Type-mask detection in `Write()` must stay aligned with record encoding.
- Stable-sort behavior is guaranteed only in single-threaded mode; `sqlite3VdbeSorterInit()` conditionally reduces compared fields for CREATE INDEX only when stable.
- The code has many OOM and IO return paths. Callers must propagate errors from `Rewind`, `Next`, `Rowkey`, and `Compare`.

## Test signals
High-value tests include ORDER BY on small in-memory inputs and large spill-to-disk inputs, CREATE INDEX and CREATE UNIQUE INDEX with duplicates/NULLs, multi-column collations and DESC order, text/integer first-key optimized paths, huge records near PMA thresholds, heap-nearly-full behavior, temp-store in memory vs disk, mmap enabled/disabled, worker-thread settings from zero to the merge-count cap, fault injection around temp-file open/read/write and allocation, and cleanup/reset reuse of a sorter cursor.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/vdbesort.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/vdbetrace.c -->
# sources/storage-engines/sqlite/src/vdbetrace.c research

## Purpose
`vdbetrace.c` expands bound host parameters into SQL text for tracing (`sqlite3_trace()`/VDBE trace consumers) when tracing is enabled. It renders the SQL statement with current bound values as SQL literals, or comments nested statements when a VDBE is executing recursively.

## Important APIs, types, and functions
- `findNextHostParameter()` tokenizes SQL text with `sqlite3GetToken()` and returns the byte prefix before the next `TK_VARIABLE`, ignoring variables inside quoted strings, identifiers, or comments because tokenization classifies those as non-variable tokens.
- `sqlite3VdbeExpandSql()` is the main exported internal function. It scans raw SQL, maps positional and named parameters to VDBE variable slots, renders `Mem` values as SQL text, and returns a `sqlite3DbMalloc`/`StrAccum` string owned by the caller.
- Rendering uses `Mem` flags: NULL becomes `NULL`, integer/intreal is decimal, real uses `%!.15g`, text is quoted with `%q`, zeroblob uses `zeroblob(N)`, and blob bytes are hexadecimal in `x'...'`.

## Control flow
`sqlite3VdbeExpandSql()` initializes a `StrAccum` capped by `SQLITE_LIMIT_LENGTH`. If `db->nVdbeExec > 1`, it prefixes each SQL line with `-- ` to avoid recursively traced SQL being executable as normal statements. If no variables are present, it copies the raw SQL. Otherwise it repeatedly calls `findNextHostParameter()`, appends non-parameter text, resolves `?`, `?NNN`, `:name`, `$name`, `@name`, or `#name` to a 1-based bind index, advances the implicit positional counter, and renders the corresponding `p->aVar[idx-1]`.

UTF16 database encodings are converted into a temporary UTF8 `Mem` before text rendering. If `SQLITE_TRACE_SIZE_LIMIT` is defined, text and blob output are truncated and annotated with omitted byte counts; text truncation avoids splitting UTF8 continuation bytes. Accumulation errors reset the output and return the finished accumulator result.

## State and persistence behavior
The file does not persist state. It reads bound values from the prepared statement's `aVar` array and allocates a transient expanded SQL string. A temporary `Mem utf8` may be allocated/released for UTF16 text conversion. It does not mutate the statement except through any helper conversion side effects needed for rendering.

## Dependencies and integration points
The file is compiled only when `SQLITE_OMIT_TRACE` is not defined. It depends on tokenization, VDBE parameter lookup (`sqlite3VdbeParameterIndex()`), `Mem` flags and text conversion from `vdbemem.c`, `StrAccum`, SQLite printf extensions, and optional `SQLITE_TRACE_SIZE_LIMIT`. It is used by trace/profile/debug paths rather than normal query execution semantics.

## Risks and edge cases
- The expansion is diagnostic, not a SQL serialization contract; values are rendered for trace output and may be truncated.
- Parameter mapping must preserve SQLite positional semantics: bare `?` uses the next available index, while named parameters search VDBE parameter metadata.
- Very large strings/blobs can create large trace strings unless `SQLITE_TRACE_SIZE_LIMIT` is configured.
- UTF16 conversion OOM sets accumulator error and suppresses output.
- Since trace output includes bound values, applications may expose sensitive data if trace callbacks are logged.

## Test signals
Trace tests should cover all parameter syntaxes, repeated named parameters, no-variable statements, nested VDBE execution comment prefixing, NULL/int/intreal/real/text/blob/zeroblob rendering, embedded quotes and binary bytes, UTF16 database encoding, trace size limiting with UTF8 multi-byte boundaries, and OOM paths in accumulator or UTF conversion.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/vdbetrace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/vdbevtab.c -->
# sources/storage-engines/sqlite/src/vdbevtab.c research

## Purpose
`vdbevtab.c` implements diagnostic virtual table modules for inspecting prepared statement bytecode. When `SQLITE_ENABLE_BYTECODE_VTAB` and virtual tables are enabled, it registers `bytecode` and `tables_used` table-valued functions/modules. `bytecode` exposes VDBE opcodes, operands, comments, subprogram labels, and optional scan-status counters. `tables_used` exposes btree roots opened by the bytecode and maps them back to table/index names.

## Important APIs, types, and functions
- `bytecodevtab` stores the database handle and a mode flag (`bTablesUsed`) distinguishing `bytecode()` from `tables_used()`.
- `bytecodevtab_cursor` stores the inspected `sqlite3_stmt`, ownership flag, current row/address, subprogram display mode, current opcode array, cached P4 rendering, table metadata cache, and `Mem sub` for subprogram traversal state.
- Virtual table callbacks are `bytecodevtabConnect()`, `bytecodevtabDisconnect()`, `bytecodevtabOpen()`, `bytecodevtabClose()`, `bytecodevtabFilter()`, `bytecodevtabNext()`, `bytecodevtabEof()`, `bytecodevtabColumn()`, `bytecodevtabRowid()`, and `bytecodevtabBestIndex()`.
- `sqlite3VdbeBytecodeVtabInit()` registers `bytecode` and `tables_used` via `sqlite3_create_module()`.

## Control flow
Connection declares one of two schemas. `bytecode` exposes `addr`, `opcode`, `p1`-`p5`, `p4`, `comment`, `subprog`, `nexec`, `ncycle`, and hidden `stmt`. `tables_used` exposes `type`, `schema`, `name`, `wr`, `subprog`, and hidden `stmt`.

`xBestIndex` requires an equality constraint on the hidden `stmt` argument and can use `subprog IS NULL` to set `idxNum=1`, meaning only the main bytecode is shown. `xFilter` clears prior cursor state, accepts either SQL text (prepared internally and finalized by the cursor) or a pointer value of type `"stmt-pointer"`, then calls `bytecodevtabNext()` to position on the first row. `xNext` calls `sqlite3VdbeNextOpcode()` with optional subprogram state and mode bits. EOF is represented by `aOp == 0`.

`xColumn` renders opcode columns directly from `Op`. P4 and explain comments are lazily cached. For subprograms it inspects the OP_Init P4 marker and reports NULL for the main program, the label after `"-- "` for named subprograms, or `(FK)` for foreign-key subprograms. In `tables_used` mode, it maps `OP_OpenRead`/`OP_OpenWrite` root pages through schema table/index hashes and reports whether the open is writable.

## State and persistence behavior
The module is read-only and diagnostic. Cursor state owns optional prepared statements and cached strings and releases them on clear/close. It reads live VDBE opcode arrays from the target statement; those arrays must remain valid while scanning. It does not modify the inspected statement's bytecode or schema, but preparing SQL text as the input can run normal prepare-time parsing and schema lookup.

## Dependencies and integration points
This file depends on `sqliteInt.h`, `vdbeInt.h`, the virtual table subsystem (`vtab.c`), VDBE introspection helpers (`sqlite3VdbeNextOpcode()`, `sqlite3OpcodeName()`, `sqlite3VdbeDisplayP4()`, `sqlite3VdbeDisplayComment()`), schema hashes, `sqlite3_value_pointer()`, optional `SQLITE_ENABLE_EXPLAIN_COMMENTS`, and optional `SQLITE_ENABLE_STMT_SCANSTATUS`. It is integrated as eponymous-style diagnostic modules registered per connection.

## Risks and edge cases
- The hidden `stmt` argument is mandatory; without a usable equality constraint, planning returns `SQLITE_CONSTRAINT`.
- Pointer input must be a valid `"stmt-pointer"` or an error is reported. SQL text input creates a statement owned by the cursor.
- `tables_used` relies on opcode root-page operands and schema hash lookup; virtual tables are skipped in table lookup and root-page collisions or stale schema assumptions would affect names.
- P4/comment rendering allocates memory lazily and must be freed on each row advance.
- Scan counters are zero unless built with `SQLITE_ENABLE_STMT_SCANSTATUS`.

## Test signals
Tests should cover `bytecode('SELECT ...')`, bytecode over a statement pointer, subprogram filtering with and without `subprog IS NULL`, triggers/foreign keys that generate subprograms, `tables_used()` for reads and writes, invalid or NULL `stmt` arguments, hidden-column planning behavior, explain comments on/off, scanstatus on/off, and repeated cursor reuse/finalization.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/vdbevtab.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/vtab.c -->
# sources/storage-engines/sqlite/src/vtab.c research

## Purpose
`vtab.c` is SQLite's core virtual table implementation layer. It registers modules, parses `CREATE VIRTUAL TABLE`, invokes module constructors/destructors, implements `sqlite3_declare_vtab()` and `sqlite3_vtab_config()`, manages per-connection `VTable` objects, coordinates virtual table transaction callbacks, supports function overloading, and handles eponymous virtual tables.

## Important APIs, types, and functions
- `VtabCtx` tracks the active `xCreate`/`xConnect` call so `sqlite3_declare_vtab()` and `sqlite3_vtab_config()` can apply to the table being constructed.
- Module registration is handled by `sqlite3VtabCreateModule()`, `sqlite3_create_module()`, `sqlite3_create_module_v2()`, `sqlite3_drop_modules()`, and `sqlite3VtabModuleUnref()`.
- Per-connection virtual table lifetime is handled by `sqlite3GetVTable()`, `sqlite3VtabLock()`, `sqlite3VtabUnlock()`, `vtabDisconnectAll()`, `sqlite3VtabDisconnect()`, `sqlite3VtabUnlockList()`, and `sqlite3VtabClear()`.
- CREATE VIRTUAL TABLE parsing is handled by `sqlite3VtabBeginParse()`, `sqlite3VtabArgInit()`, `sqlite3VtabArgExtend()`, `sqlite3VtabFinishParse()`, and `addModuleArgument()`.
- Constructor/destructor entry points include `vtabCallConstructor()`, `sqlite3VtabCallConnect()`, `sqlite3VtabCallCreate()`, `sqlite3_declare_vtab()`, and `sqlite3VtabCallDestroy()`.
- Transaction/savepoint integration is handled by `sqlite3VtabBegin()`, `sqlite3VtabSync()`, `sqlite3VtabCommit()`, `sqlite3VtabRollback()`, `sqlite3VtabSavepoint()`, `growVTrans()`, `addToVTrans()`, and `callFinaliser()`.
- Extension behavior APIs include `sqlite3VtabOverloadFunction()`, `sqlite3VtabMakeWritable()`, `sqlite3VtabEponymousTableInit()`, `sqlite3VtabEponymousTableClear()`, `sqlite3_vtab_on_conflict()`, and `sqlite3_vtab_config()`.

## Control flow
Module registration installs or removes a `Module` in `db->aModule` under the connection mutex. Replacing a module clears any eponymous table and unreferences the old module, calling its destroy callback when references drop to zero.

Parsing `CREATE VIRTUAL TABLE` starts an SQLite schema table entry, marks the `Table` as `TABTYP_VTAB`, records module arguments, performs authorization, and finally either updates `sqlite_schema` plus emits `OP_VCreate` for real DDL, or inserts an in-memory table while reading schema. Constructor calls allocate a `VTable`, set `db->pVtabCtx`, call module `xCreate` or `xConnect`, require `sqlite3_declare_vtab()` to define columns, link the `VTable` into the table's per-connection list, and post-process hidden columns by stripping the `hidden` token from type strings.

`sqlite3_declare_vtab()` validates that the supplied SQL starts with `CREATE TABLE`, parses it in `PARSE_MODE_DECLARE_VTAB`, transfers columns and optional primary key/index metadata to the virtual table, enforces writable WITHOUT ROWID virtual tables to have a single-column primary key, and marks the active context as declared.

Transaction flow adds vtabs to `db->aVTrans` on successful `xBegin`, calls `xSync` before commit, calls `xCommit` or `xRollback` through `callFinaliser()`, and dispatches savepoint/release/rollback-to callbacks for module version >= 2. Writes during virtual-table sync are rejected via `sqlite3VtabInSync()`.

## State and persistence behavior
Module state lives in `db->aModule` with reference-counted `Module` objects. Schema-level `Table` objects store virtual table arguments and a linked list of per-connection `VTable` objects. `sqlite3_schema` persistence is updated during actual CREATE VIRTUAL TABLE DDL; the module's own storage is managed externally through `xCreate`/`xDestroy`. Active virtual table transactions are tracked in `db->aVTrans` and are cleared on commit/rollback. Deferred disconnects are queued in each connection's `pDisconnect` list until mutex-safe cleanup.

## Dependencies and integration points
The file depends on the parser, schema and hash tables, VDBE DDL opcodes, authorization callbacks, mutex/shared-cache discipline, module APIs in `sqlite3_module`, `Table`/`VTable`/`Module` internals, function lookup and `FuncDef`, savepoint constants, defensive-mode flags, and API armor. It integrates with planner name resolution for eponymous tables, DML code generation through `sqlite3VtabMakeWritable()`, expression function resolution through `xFindFunction`, and extension APIs exposed to module authors.

## Risks and edge cases
- Constructor recursion is explicitly rejected to avoid a virtual table recursively initializing itself.
- Failure to call `sqlite3_declare_vtab()` from a successful constructor is an error and forces disconnect/unref cleanup.
- Hidden-column parsing mutates type strings in place; malformed or unusual declared types can expose edge cases.
- Shared-cache and disconnect ordering relies on strict mutex assumptions around `pDisconnect` and schema mutexes.
- `sqlite3VtabCallDestroy()` refuses to destroy a vtab if any `sqlite3_vtab.nRef` is positive, returning `SQLITE_LOCKED`.
- `sqlite3_vtab_config()` is valid only inside constructor context and controls risk classification (`INNOCUOUS`, `DIRECTONLY`) and all-schema usage.
- Transaction arrays hold locked `VTable` references and must always be finalized to avoid leaks and dangling module state.

## Test signals
Tests should cover module create/replace/drop, xDestroy callback invocation, CREATE VIRTUAL TABLE DDL and schema reload, constructor failure and missing declare errors, recursive constructor lockout, hidden columns and out-of-order hidden flags, WITHOUT ROWID declaration constraints, xConnect reuse per connection, DROP TABLE with active cursor returning `SQLITE_LOCKED`, xBegin/xSync/xCommit/xRollback and savepoint callback order, writes during xSync returning locked, overloaded MATCH/LIKE/GLOB/REGEXP functions, eponymous table initialization/cleanup, `sqlite3_vtab_on_conflict()`, and all `sqlite3_vtab_config()` operations with API armor misuse cases.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/vtab.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/vxworks.h -->
# sources/storage-engines/sqlite/src/vxworks.h research

## Purpose
`vxworks.h` centralizes SQLite compile-time platform defines for Wind River VxWorks. It detects VxWorks RTP or kernel builds and sets OS feature macros so the rest of SQLite selects the correct mutex, extension-loading, locking-style, and POSIX capability paths.

## Important APIs, types, and functions
This header does not declare functions or types of its own. On VxWorks (`__RTP__` or `_WRS_KERNEL`) it includes `<vxWorks.h>` and `<pthread.h>`, defines `OS_VXWORKS 1`, disables the generic `SQLITE_OS_OTHER` selection, enables `SQLITE_HOMEGROWN_RECURSIVE_MUTEX`, omits loadable extensions with `SQLITE_OMIT_LOAD_EXTENSION`, disables `SQLITE_ENABLE_LOCKING_STYLE`, and marks `HAVE_UTIME`.

For non-VxWorks builds, it defines `OS_VXWORKS 0` if not already defined and advertises `HAVE_FCHOWN`, `HAVE_READLINK`, and `HAVE_LSTAT`.

## Control flow
The only control flow is preprocessor selection. The VxWorks branch is selected when either runtime-process or kernel macros are defined. Otherwise, default non-VxWorks POSIX feature macros are supplied. The `OS_VXWORKS` guard allows an external build configuration to define it before inclusion.

## State and persistence behavior
There is no runtime state or persistence. The header affects compilation of platform-specific SQLite code, especially OS abstraction and feature availability.

## Dependencies and integration points
The header integrates with SQLite's OS layer (`os_unix.c`, mutex configuration, extension loading, and file-locking style code) by setting macros consumed elsewhere. On VxWorks it depends on the platform headers being available. In the amalgamation process, the pthread include is marked not to be cached.

## Risks and edge cases
- Incorrect platform detection can compile SQLite with the wrong filesystem and mutex assumptions.
- VxWorks builds forcibly omit loadable extensions and disable locking-style support; applications expecting those features need build-time awareness.
- Non-VxWorks fallback defines POSIX capabilities that may not exist on every unusual non-VxWorks platform unless overridden by the build system.

## Test signals
Build-matrix coverage should compile with `__RTP__`, `_WRS_KERNEL`, and neither macro. Tests should verify the resulting `OS_VXWORKS`, extension loading availability, recursive mutex behavior, file timestamp support, and non-VxWorks feature macro interactions with the OS layer.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/vxworks.h -->
