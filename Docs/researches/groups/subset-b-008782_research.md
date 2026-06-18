# subset-b-008782 Research

Grouped research for SQLite core sources under `sources/storage-engines/sqlite/src`.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/pragma.c -->
# sources/storage-engines/sqlite/src/pragma.c

## Purpose
`pragma.c` implements SQLite's `PRAGMA` statement compiler and the eponymous `pragma_*` virtual tables. Most of the file is not direct execution logic; it translates parsed PRAGMA syntax into VDBE bytecode, connection flag changes, pager/B-tree calls, schema metadata reads, or helper SQL such as `ANALYZE`. It is the central bridge between SQL-level operational knobs and low-level SQLite subsystems including the pager, WAL, schema cache, btree metadata, authorizer, VFS file controls, foreign-key checking, integrity checking, and virtual table modules.

The file is heavily feature-gated by compile-time options. `sqlite3GetBoolean()` remains available outside the PRAGMA build because other modules need SQLite's legacy boolean parser. The rest of the file is omitted when `SQLITE_OMIT_PRAGMA` is defined, and many individual handlers are removed by flags such as `SQLITE_OMIT_PAGER_PRAGMAS`, `SQLITE_OMIT_SCHEMA_PRAGMAS`, `SQLITE_OMIT_FOREIGN_KEY`, `SQLITE_OMIT_WAL`, and `SQLITE_OMIT_VIRTUALTABLE`.

## Important APIs, Types, and Functions
`sqlite3Pragma(Parse*, Token*, Token*, Token*, int)` is the main entry point used by the parser for `PRAGMA [schema.]name [= value]` and function-call-like variants. It resolves the schema/name tokens, authorizes the operation, gives the VFS first chance to handle the pragma through `SQLITE_FCNTL_PRAGMA`, locates generated metadata in `aPragmaName[]`, optionally loads schema, sets result-column names, then dispatches by `PragTyp_*`.

Small parser helpers normalize legacy input: `getSafetyLevel()` parses synchronous/boolean words and numbers, `sqlite3GetBoolean()` exposes boolean parsing, `getLockingMode()`, `getAutoVacuum()`, and `getTempStore()` parse specific option domains, and `sqlite3JournalModename()` maps pager journal-mode constants back to SQL-visible names. `pragmaLocate()` binary-searches the generated `pragma.h` table, which must stay lexicographically sorted by `mkpragmatab.tcl`.

Output helpers include `setPragmaResultColumnNames()`, `returnSingleInt()`, and `returnSingleText()`. Pager-state helpers include `invalidateTempStorage()`, `changeTempStorage()`, and `setAllPagerFlags()`. Foreign-key and introspection helpers include `actionName()` and `pragmaFunclistLine()`. Integrity checking uses `integrityCheckResultRow()` to emit bounded error rows and `tableSkipIntegrityCheck()` to support table-targeted checks and imposter-table skips.

The virtual table portion defines `PragmaVtab` and `PragmaVtabCursor`, plus module methods `pragmaVtabConnect()`, `pragmaVtabBestIndex()`, `pragmaVtabOpen()`, `pragmaVtabFilter()`, `pragmaVtabNext()`, `pragmaVtabColumn()`, `pragmaVtabRowid()`, and `sqlite3PragmaVtabRegister()`. These expose result-bearing pragmas as eponymous virtual tables named `pragma_<name>`.

## Control Flow
`sqlite3Pragma()` first obtains a VDBE with `sqlite3GetVdbe()` and marks it run-once. `sqlite3TwoPartName()` splits optional schema qualification. Explicit `temp` qualification opens the temporary database. The left and right tokens are copied into nul-terminated strings, with `minusFlag` preserving negative numeric values. The authorizer sees `SQLITE_PRAGMA` with the pragma name, value, and optional schema name before any built-in handler runs.

Before built-in dispatch, the function sends `SQLITE_FCNTL_PRAGMA` to the target VFS file. `SQLITE_OK` means the VFS handled the pragma and may return a single text result via `aFcntl[0]`. Any error other than `SQLITE_NOTFOUND` becomes a parse error. Unknown built-in names intentionally generate no error. For recognized names, flags in `PragmaName` control schema loading and result-column setup. Each `PragTyp_*` case either directly mutates connection state, emits VDBE opcodes, or calls subsystem APIs.

Pager and file-state pragmas cover default/current cache size, page size, secure delete, page/max page count, locking mode, journal mode/size, auto-vacuum, incremental vacuum, cache spill, mmap size, temporary/data directory handling, lock-proxy file, and synchronous level. Some handlers directly update connection fields such as `db->temp_store`, `db->dfltLockMode`, `db->szMmap`, or per-schema `cache_size`; others emit bytecode such as `OP_SetCookie`, `OP_Pagecount`, `OP_MaxPgcnt`, `OP_JournalMode`, `OP_IncrVacuum`, and `OP_Checkpoint`.

Schema and introspection pragmas enumerate table columns, tables, indexes, attached databases, collations, SQL functions, virtual modules, pragma names, foreign keys, and compile options. These cases walk schema hash tables, function hash chains, module hashes, and table/index metadata while emitting rows through `sqlite3VdbeMultiLoad()` and `OP_ResultRow`. `table_list` can prepare dummy `SELECT * FROM table` statements to force view or virtual-table column counts to initialize, so it may perturb schema hashes and restart scans.

`foreign_key_check` builds VDBE loops over child tables, opens parent tables or indexes, skips rows with NULL child keys, probes parent keys, and emits four-column violation rows. `integrity_check` and `quick_check` are the largest handlers. They optionally target a single schema or table, collect root pages, run `OP_IntegrityCk`, compare index/table entry counts, verify table records, type constraints, strict-table types, CHECK constraints, index membership, rowid placement, non-binary-collation values, UNIQUE semantics, WITHOUT ROWID primary-key ordering, and virtual-table `xIntegrity()` callbacks when available. Quick check omits the expensive cross-index validations.

Header-value pragmas read or write btree cookies such as schema version, user version, application id, freelist count, and data version. Defensive mode converts schema-version writes into no-ops. WAL pragmas emit checkpoint bytecode or configure autocheckpoint callbacks. `optimize` scans ordinary non-system tables, decides whether `ANALYZE` is useful from missing/used statistics and size thresholds, optionally emits diagnostic SQL strings, otherwise emits `OP_SqlExec`, and scales `analysis_limit` when many btrees are candidates.

The pragma virtual table flow is a wrapper around the same PRAGMA compiler. `sqlite3PragmaVtabRegister()` accepts `pragma_` names for result-bearing pragmas, registers an eponymous module, and stores the `PragmaName` pointer as aux data. `xConnect` declares a virtual table schema with visible result columns and hidden `arg`/`schema` columns when supported. `xBestIndex` encourages equality constraints on hidden columns. `xFilter` constructs a quoted PRAGMA statement using supplied hidden values, prepares it, and `xNext` steps it. `xColumn` either returns an underlying pragma result column or echoes a hidden argument.

## State and Persistence Behavior
This file can modify both transient connection state and persistent database-header state. Transient changes include flags such as foreign keys, defer-foreign-keys, `writable_schema`, `count_changes`, cache spill, busy timeout, temp-store mode, mmap defaults, synchronous levels, locking defaults, analysis limits, worker-thread limits, and heap limits. Some changes expire existing statements with `OP_Expire` because they affect generated code or planner behavior.

Persistent or file-visible effects include `default_cache_size`, auto-vacuum cookies, header values (`schema_version`, `user_version`, `application_id`), journal mode, max page count, WAL checkpoints, secure-delete behavior as applied to btrees, incremental vacuum work, and `ANALYZE` changes from `PRAGMA optimize`. Several setters are deliberately constrained: synchronous cannot change inside a transaction, temp storage cannot change while the temp btree is in use by a transaction, journal mode OFF is blocked in defensive mode, and hard heap limits can only be activated or lowered through the pragma.

Schema state is both consumed and invalidated. Many pragmas require `sqlite3ReadSchema()`. `temp_store` and temp-directory changes close the temp btree and reset schemas. `writable_schema=RESET` disables writable schema and reloads schemas. Header-cookie writes, schema verification opcodes, and `OP_Expire` coordinate with prepared-statement invalidation. Integrity and foreign-key checks open read cursors but do not themselves repair corruption.

Virtual table cursors own a prepared PRAGMA statement and copied hidden-column arguments. `pragmaVtabCursorClear()` finalizes the statement, frees arguments, and resets rowid; it is called from close, filter reset, and end-of-scan paths.

## Dependencies and Integration Points
`pragma.c` depends on generated `pragma.h` for names, flags, column-name indices, and `PragTyp_*` values. Its primary internal dependencies are parser state (`Parse`, `Token`), VDBE bytecode APIs, btree/pager APIs, schema metadata (`Db`, `Schema`, `Table`, `Index`, `FKey`, `FuncDef`, `Module`), authorization, VFS file controls, mutexes for global temp/data directory state, and SQL memory formatting through `sqlite3MPrintf()` and `StrAccum`.

It integrates with `prepare.c` through `sqlite3ReadSchema()` and with the parser through `sqlite3Pragma()`. Pager and WAL integration flows through functions such as `sqlite3BtreeSetPagerFlags()`, `sqlite3BtreeSetPageSize()`, `sqlite3PagerLockingMode()`, `OP_JournalMode`, `OP_Checkpoint`, and `sqlite3_wal_autocheckpoint()`. Optimizer/statistics integration uses schema flags (`TF_MaybeReanalyze`, `Index.hasStat1`), `OP_IfSizeBetween`, and `OP_SqlExec` running `ANALYZE`.

The VFS integration point is unusually early: every parsed PRAGMA is offered to `sqlite3_file_control(..., SQLITE_FCNTL_PRAGMA, ...)` before built-in lookup. This allows VFS-specific pragmas or overrides but also means file-control error handling and returned text must follow the expected ownership contract.

## Risks and Edge Cases
The largest risk is the breadth of side effects hidden behind SQL syntax. Handlers mix immediate C mutations with generated bytecode, so transaction state, autocommit state, schema-loaded state, and statement expiration must remain consistent. A missed `sqlite3VdbeUsesBtree()`, schema verification opcode, or `OP_Expire` can create stale prepared statements or incorrect locking behavior.

Input compatibility is intentionally loose for historical reasons. Boolean and synchronous parsing accepts numeric and textual aliases, unknown pragmas are silent, and some invalid arguments degrade into queries. Tests must preserve legacy semantics even when behavior looks surprising. Defensive mode and transaction guards are critical safety boundaries around journal mode OFF, `schema_version`, synchronous, temp storage, and writable schema.

`integrity_check` has a high bug surface because it generates nested bytecode over many table shapes: rowid tables, WITHOUT ROWID tables, STRICT tables, generated columns, partial indexes, expression/default values, virtual tables, imposter tables, and collations. Register allocation (`pParse->nMem`, temp ranges, cursor numbers), labels, and dynamically allocated error strings must remain correct across all branches.

`pragma_*` virtual tables recursively prepare PRAGMA SQL built from hidden constraints. Quoting uses `%Q` for schema and argument values, but unsupported or unconstrained hidden columns intentionally produce high estimated cost rather than semantic errors. Cursor cleanup must handle prepare failures, EOF finalization, and repeated filters without leaking statements or copied arguments.

## Test Signals
Regression coverage should include query and setter forms for pager pragmas, schema-qualified and unqualified variants, attached databases, defensive mode, autocommit versus transaction contexts, and VFS `SQLITE_FCNTL_PRAGMA` handling for OK, NOTFOUND, and error returns. Schema-introspection tests should cover hidden/generated columns, STRICT tables, WITHOUT ROWID tables, views/virtual tables with delayed column initialization, shadow tables, expression/partial indexes, and internal-function visibility.

Integrity-check tests should include corrupt btrees, mismatched index counts, missing index entries, imprecise floating-point index values, non-binary collation mismatches, CHECK failures, NOT NULL failures including NaN cases, strict type failures, foreign-key violations, table-targeted checks, quick-check differences, and virtual table `xIntegrity()` results. `PRAGMA optimize` tests should cover missing `sqlite_stat1`, `TF_MaybeReanalyze`, 10x size thresholds, debug mask output, schema-qualified scans, analysis-limit scaling, and `OP_Expire`.

Virtual table tests should query `pragma_table_info`, `pragma_index_list`, and other result pragmas with and without hidden `arg` and `schema` constraints, verify planner costs/constraint omission, and exercise error propagation from the prepared PRAGMA statement.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/pragma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/prepare.c -->
# sources/storage-engines/sqlite/src/prepare.c

## Purpose
`prepare.c` implements SQLite's statement preparation APIs and schema-loading path. It is responsible for converting SQL text into VDBE statements, loading `sqlite_schema` rows into in-memory `Table`, `Index`, `Trigger`, and `View` structures, validating schema cookies, retrying after schema changes, and exposing the public UTF-8 and UTF-16 `sqlite3_prepare*()` entry points.

The file sits between the public API, the Lemon parser, the btree schema tables, and VDBE lifecycle. It is also used recursively while schema rows are being loaded: stored `CREATE` SQL is prepared while `db->init.busy` is set so the parser builds metadata without running the DDL.

## Important APIs, Types, and Functions
`sqlite3InitCallback()` is the callback used by `sqlite3_exec()` over `sqlite_schema`. It validates each schema row, prepares stored `CREATE` SQL, records root page numbers for implicit indexes, and reports malformed schema errors through `InitData`.

`sqlite3InitOne(sqlite3*, int, char**, u32)` initializes one database schema. It constructs the built-in schema table, opens a read transaction if needed, reads btree metadata cookies, validates text encoding and file format, applies default cache size, scans `sqlite_schema`, loads analysis statistics, and marks `DB_SchemaLoaded` on success. `sqlite3Init()` initializes main first, then attached schemas, then temp last. `sqlite3ReadSchema(Parse*)` is the parser-facing wrapper that records parse errors.

`schemaIsValid(Parse*)` checks btree schema cookies against cached schema cookies and resets stale schemas. `sqlite3SchemaToIndex()` maps a `Schema*` back to `db->aDb[]` index. `sqlite3IndexHasDuplicateRootPage()` detects corrupt schemas where sibling indexes share a root page.

Parser lifetime helpers include `sqlite3ParseObjectInit()`, `sqlite3ParseObjectReset()`, and `sqlite3ParserAddCleanup()`. These manage the active `db->pParse` chain, lookaside-disable counters, labels, table locks, constant expressions, trigger programs, and uncommon cleanup callbacks.

`sqlite3Prepare()` is the internal compiler. `sqlite3LockAndPrepare()` wraps it with API validation, connection mutex, all-btree mutex entry, schema-change retry, API-exit normalization, and busy-handler reset. `sqlite3Reprepare()` recompiles saved-SQL statements after schema change and swaps the new VDBE into the old handle. Public APIs are `sqlite3_prepare()`, `sqlite3_prepare_v2()`, `sqlite3_prepare_v3()`, and, when UTF-16 is enabled, `sqlite3_prepare16()`, `sqlite3_prepare16_v2()`, and `sqlite3_prepare16_v3()`.

## Control Flow
Schema loading starts in `sqlite3Init()`. The main database schema is initialized first because it fixes the connection text encoding; attached schemas follow in reverse index order, with temp last. `sqlite3InitOne()` synthesizes a `CREATE TABLE x(type text,name text,tbl_name text,rootpage int,sql text)` row for `sqlite_schema`/`sqlite_temp_schema` and passes it through `sqlite3InitCallback()` so the parser owns schema-table construction too.

For disk-backed schemas, `sqlite3InitOne()` enters the btree mutex, begins a read transaction if none exists, reads btree meta values, applies reset-database behavior, sets schema cookie, validates encoding compatibility, initializes cache size, checks file format, clears legacy file format for modern main databases, then runs `SELECT * FROM "<schema>".sqlite_schema ORDER BY rowid`. The authorizer is disabled during this internal scan. Each row is routed to `sqlite3InitCallback()`.

`sqlite3InitCallback()` rejects missing rootpage fields, validates rootpage integers when extra schema checks are enabled, and only prepares schema SQL that begins with `CREATE` by checking the first two letters. While `db->init.busy` is set, `sqlite3Prepare()` parses DDL into schema objects without executing VDBE bytecode. Blank SQL rows represent implicit PRIMARY KEY/UNIQUE indexes; the callback finds the existing `Index`, records its root page, and checks for invalid or duplicate root pages.

Statement preparation through the public API enters `sqlite3LockAndPrepare()`. It validates `ppStmt`, database handle, and SQL pointer, takes the database mutex, enters all btrees, and calls `sqlite3Prepare()` repeatedly for transient `SQLITE_ERROR_RETRY` or once after `SQLITE_SCHEMA` with a full schema reset. The retry loop is bounded by `SQLITE_MAX_PREPARE_RETRY`.

`sqlite3Prepare()` creates a stack `Parse`, links it into `db->pParse`, optionally sets reprepare/explain state, disables lookaside for persistent statements, checks schema locks in shared-cache mode, unlocks pending virtual-table disconnects, copies non-nul-terminated SQL slices when needed, runs the parser, returns the tail pointer, stores original SQL text on non-schema-loading VDBEs, validates schema if parser requested it after an error, finalizes failed VDBEs, transfers error messages to the database handle, frees trigger programs, and resets the `Parse` object.

UTF-16 prepare first normalizes the byte count to a complete UTF-16 string, converts to UTF-8 under the connection mutex, calls `sqlite3LockAndPrepare()`, then maps the UTF-8 tail pointer back to a UTF-16 byte offset by counting UTF-8 characters and UTF-16 bytes.

## State and Persistence Behavior
This file does not directly modify user table contents, but it controls persistent-schema interpretation. It reads header metadata including schema cookie, file format, cache size, largest root page, and text encoding. It updates in-memory schema fields such as `schema_cookie`, `enc`, `cache_size`, `file_format`, table/index root pages, loaded-statistics state, and `DB_SchemaLoaded`.

Schema-loading state is stored in `db->init`: `busy`, `iDb`, `newTnum`, `orphanTrigger`, and `azInit`. `busy==1` means schema scan; `busy==2` is used for stricter ALTER TABLE ADD COLUMN parsing. `DBFLAG_EncodingFixed`, `DBFLAG_SchemaKnownOk`, `DBFLAG_SchemaChange`, `SQLITE_NoSchemaError`, `SQLITE_ResetDatabase`, `SQLITE_WriteSchema`, and `SQLITE_LegacyFileFmt` all alter behavior.

Preparation state is transient but critical. `Parse` owns labels, cleanup callbacks, locks, constant expressions, trigger programs, error text, VDBE pointer, tail pointer, and lookaside-disable count. `sqlite3ParseObjectReset()` restores the outer parse pointer and lookaside sizing, so every prepare path must reach it. Successful `prepare_v2/v3` stores SQL text in the VDBE for later automatic reprepare; legacy `sqlite3_prepare()` does not.

`sqlite3Reprepare()` preserves statement identity by compiling a fresh VDBE, swapping it into the existing one, transferring bindings, resetting step result state, and finalizing the temporary VDBE. This makes schema-change recovery visible as continuation of the original statement handle.

## Dependencies and Integration Points
`prepare.c` depends on the parser (`sqlite3RunParser()`), VDBE lifecycle (`sqlite3VdbeSetSql()`, finalize/swap/reset helpers), btree transactions and schema mutexes, schema hash structures, SQLite memory APIs, UTF conversion helpers, authorization hooks, virtual-table unlock handling, analysis-stat loading, and the public API exit/error normalization layer.

It is called by many subsystems that need schema availability through `sqlite3ReadSchema()`. `pragma.c` depends on that for schema-sensitive pragmas. Schema DDL execution depends back on `prepare.c` because parsing stored DDL creates in-memory objects. VDBE execution can invoke schema parsing through `OP_ParseSchema`, which also uses `sqlite3InitCallback()`.

The all-btree mutex discipline in `sqlite3LockAndPrepare()` is the concurrency boundary that makes schema-lock checks reliable. Shared-cache schema locks, schema cookies, and `sqlite3ResetOneSchema()` combine to prevent compiling statements against uncommitted or stale schema definitions.

## Risks and Edge Cases
Schema parsing is security- and corruption-sensitive. Malformed `sqlite_schema` rows can contain arbitrary text, so the callback only accepts SQL beginning with `CREATE` and treats other nonblank SQL as corruption. `SQLITE_WriteSchema` and `SQLITE_NoSchemaError` intentionally weaken normal corruption handling for recovery workflows and must not leak into ordinary prepare behavior.

Root-page validation has compatibility nuance. Some invalid root pages only become hard errors when `sqlite3Config.bExtraSchemaChecks` is enabled, while duplicate sibling index roots are always detected in that validation path. Reset-database mode zeros metadata and can bypass normal file state. Attached databases must match the main database encoding.

The prepare retry loop must distinguish transient parser retries, stale schema, OOM, locked schema, and permanent errors. Retrying too often risks hiding real errors; retrying too little breaks automatic schema-change recovery. The special `SQLITE_SCHEMA` branch resets all schemas only for the first schema failure.

Memory and ownership risks center on parser cleanup. `sqlite3ParserAddCleanup()` may run cleanup immediately on OOM; callers must not continue using freed pointers. `sqlite3Prepare()` may copy SQL text to ensure nul termination and then remap `sParse.zTail` back into the original buffer. UTF-16 tail mapping can be wrong if byte-length normalization or character counting changes.

## Test Signals
Preparation tests should cover legacy/v2/v3 APIs, persistent prep flags, tail pointers for nul-terminated and bounded SQL, SQL length limits, null API arguments under API armor, UTF-16 odd byte counts, UTF-16 tail mapping with multibyte characters, and saved-SQL automatic reprepare preserving bindings.

Schema tests should cover empty databases, attached database encoding mismatch, unsupported file format, reset-database mode, corrupt schema rows, non-`CREATE` schema SQL, orphan indexes, invalid and duplicate root pages, implicit unique/primary-key indexes with blank SQL, `SQLITE_WriteSchema`, `SQLITE_NoSchemaError`, and schema scans with authorizer callbacks disabled.

Concurrency tests should exercise shared-cache schema locks, schema cookie mismatch after another connection changes DDL, busy-handler reset after prepare, virtual-table disconnect unlocking before parse, and bounded retry behavior for `SQLITE_ERROR_RETRY` and `SQLITE_SCHEMA`.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/prepare.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/printf.c -->
# sources/storage-engines/sqlite/src/printf.c

## Purpose
`printf.c` implements SQLite's locale-independent printf engine, dynamic string accumulator API, logging formatter, error-offset helpers, and reference-counted string allocation helpers. It replaces libc formatting for SQLite-owned code so output is deterministic across locales, bounded by SQLite limits, aware of SQLite memory allocators, and extended with SQLite-specific conversions for SQL quoting, JSON strings, parser tokens, source items, and dynamic string ownership.

The central formatter is `sqlite3_str_vappendf()`, which appends formatted output to a `sqlite3_str`/`StrAccum`. Public wrappers expose `sqlite3_mprintf()`, `sqlite3_vmprintf()`, `sqlite3_snprintf()`, `sqlite3_vsnprintf()`, `sqlite3_str_appendf()`, and internal `sqlite3MPrintf()`/`sqlite3VMPrintf()`.

## Important APIs, Types, and Functions
The format-dispatch table `fmtinfo[]` maps conversion characters to conversion classes such as decimal/radix integers, floating point, strings, dynamic strings, SQL quoting, JSON escaping, `%T` tokens, `%S` source items, `%p` pointers, `%r` ordinals, `%n`, and `%%`. Internal-only conversions are guarded by `SQLITE_PRINTF_INTERNAL`; public `sqlite3_mprintf()` cannot use parser-token or source-item conversions.

`sqlite3_str_vappendf(sqlite3_str*, const char*, va_list)` parses flags, width, precision, length modifiers, and conversion types. SQLite extensions include `%q` and `%Q` for SQL string escaping, `%w` for identifier-style double-quote escaping, `%j` and `%J` for JSON string literal escaping, `%z` for SQLite-owned dynamic strings, `%T`/`%#T` for tokens/expressions, `%S`/`%!S` for `SrcItem`, `%r` for English ordinals, `,` for thousands separators, and `!` for UTF-8 character-aware width/precision or alternate floating precision.

`StrAccum` management functions include `sqlite3StrAccumSetError()`, `sqlite3StrAccumEnlarge()`, `sqlite3StrAccumEnlargeIfNeeded()`, `sqlite3_str_appendchar()`, `sqlite3_str_append()`, `sqlite3_str_appendall()`, `sqlite3StrAccumFinish()`, `sqlite3ResultStrAccum()`, `sqlite3_str_finish()`, `sqlite3_str_errcode()`, `sqlite3_str_length()`, `sqlite3_str_truncate()`, `sqlite3_str_value()`, `sqlite3_str_reset()`, `sqlite3_str_free()`, `sqlite3StrAccumInit()`, and `sqlite3_str_new()`.

Error-offset helpers `sqlite3RecordErrorByteOffset()` and `sqlite3RecordErrorOffsetOfExpr()` record parser byte offsets for diagnostics when `%T`/`%#T` render tokens or expressions. `sqlite3_log()` formats bounded log messages via `renderLogMsg()`. `sqlite3DebugPrintf()` is available for debug/OS trace builds. `sqlite3RCStrRef()`, `sqlite3RCStrUnref()`, `sqlite3RCStrNew()`, and `sqlite3RCStrResize()` implement reference-counted strings/blobs.

## Control Flow
`sqlite3_str_vappendf()` scans literal text until `%`, appends literals directly, then parses flags (`-`, `+`, space, `#`, `!`, `0`, `,`), width (numeric or `*`), precision, and `l`/`ll`. It looks up the conversion type through an ASCII hash table or linear EBCDIC scan, then dispatches by conversion class.

Integer formatting fetches signed or unsigned values from either varargs or `PrintfArguments`, handles negative `SMALLEST_INT64` without overflow by two's-complement inversion, applies precision/zero padding, optional thousands separators, sign/prefix, radix conversion, and ordinal suffixes. Pointer formatting selects the length modifier based on pointer size and can be masked by trace flags.

Floating formatting decodes doubles through `sqlite3FpDecode()`, handles NaN/Inf specially, chooses fixed versus exponential for `%g/%G`, renders directly into the accumulator when possible, applies optional decimal points and trailing-zero trimming, and pads according to width and zero-fill rules. The formatter enforces `SQLITE_FP_PRECISION_LIMIT` and may allocate temporary buffers only when accumulator capacity cannot hold direct output.

String formatting handles `%s`, `%z`, and `%c`. `%z` either adopts the input allocation as the accumulator buffer for the special empty-output case or arranges to free it after appending. The `!` flag makes precision and width count UTF-8 characters rather than bytes. `%c` can duplicate the character according to precision using repeated doubling into the accumulator.

Escaping conversions append SQL, identifier, JSON, or `unistr()`-style escaped output. `%Q` wraps non-null strings in quotes and renders null pointers as SQL `NULL`; `%q` does not quote and renders null as `(NULL)`; `%w` doubles double quotes; `%j/%J` escape JSON control characters, quotes, and backslashes, with `%J` adding quotes or `null`. Alternate `#` on `%q/%Q` adds backslash control-character escaping, and `!` makes precision character-aware.

After each conversion, common width adjustment appends left/right padding and frees any temporary allocation. Accumulator growth is centralized in `sqlite3StrAccumEnlarge()`, which enforces maximum allocation, uses exponential growth where safe, copies static-base buffers into heap buffers, and sets `SQLITE_TOOBIG` or `SQLITE_NOMEM` error state on failure.

## State and Persistence Behavior
The formatter itself has no durable persistence, but it manages memory ownership across SQLite allocators. `StrAccum` can write into caller-provided fixed buffers (`mxAlloc==0`), database-aware allocations using `sqlite3DbRealloc()`, or global allocations using `sqlite3Realloc()`. Error state is sticky: once `accError` is set, append operations stop or reset owned memory. `sqlite3StrAccumSetError(SQLITE_TOOBIG)` also reports the error to the parser when a database handle is present.

`sqlite3_str_new()` returns a heap `sqlite3_str` with a length limit from the database or `SQLITE_MAX_LENGTH`. If allocation fails, it returns the static singleton `sqlite3OomStr`, which always reports `SQLITE_NOMEM` and must not be freed like a normal object. `sqlite3_str_finish()` transfers the final string to the caller and frees the accumulator object; `sqlite3ResultStrAccum()` transfers malloced text to an SQL function result with `SQLITE_DYNAMIC`.

`sqlite3RecordErrorByteOffset()` stores `db->errByteOffset` only if no offset has already been recorded and the token pointer falls within the current parse text. `sqlite3RecordErrorOffsetOfExpr()` walks through ON-clause wrapper expressions to find a usable expression offset and skips DDL-origin expressions. These offsets persist on the connection until the next error-state reset.

Reference-counted strings store an `RCStr` header immediately before the returned char pointer. `sqlite3RCStrRef()` increments, `sqlite3RCStrUnref()` decrements and frees at zero, and `sqlite3RCStrResize()` requires unique ownership (`nRCRef==1`) and frees on realloc failure.

## Dependencies and Integration Points
The file depends on `sqliteInt.h` for SQLite memory APIs, limits, parser and expression structures, UTF-8 helpers, floating decode helpers, result APIs, global configuration, logging callbacks, and compile-time feature flags. It is used pervasively by SQL construction, parser diagnostics, error messages, VDBE/debug tracing, JSON/SQL literal rendering, pragmas, schema loading, and any component using `sqlite3MPrintf()` or `sqlite3_str`.

Public API wrappers initialize SQLite automatically when autoinit is enabled. Internal wrappers use the database limit `SQLITE_LIMIT_LENGTH` and set OOM state on the database. `renderLogMsg()` intentionally uses a fixed stack buffer and `mxAlloc==0` because logging may happen while allocator mutexes are held.

The SQL function form uses `SQLITE_PRINTF_SQLFUNC` and `PrintfArguments` to fetch values from `sqlite3_value` arrays rather than varargs. This makes the same formatting engine available to SQL-level formatting while preserving type conversion semantics.

## Risks and Edge Cases
The highest-risk areas are allocation limits, ownership, and precision/width arithmetic. The code must avoid integer overflow while computing buffer sizes, enforce `SQLITE_PRINTF_PRECISION_LIMIT`/`SQLITE_FP_PRECISION_LIMIT`, and avoid large allocations from untrusted SQL formatting. `printfTempBuf()` checks requested temporary size against accumulator limits before allocation.

`%z` ownership is subtle: the input must be freed exactly once unless it is adopted as the accumulator buffer. Callers must only pass SQLite-allocated strings. `sqlite3_str_reset()` frees only buffers marked `SQLITE_PRINTF_MALLOCED`, so incorrect flag transitions can leak or double-free.

UTF-8 character-aware width and precision rely on byte scanning and continuation-byte counting, not full Unicode validation. Invalid UTF-8 can produce surprising widths but should not overrun buffers. `%c` with large precision uses repeated self-append; it relies on accumulator growth checks to prevent runaway memory.

Floating-point output has special behavior for NaN/Inf and alternate flags, including rendering NaN as `null` when zero-padded and substituting a large numeric representation for Inf under zero padding. Tests must preserve these SQLite-specific semantics. `sqlite3_log()` cannot safely use formats that allocate temporary memory while the allocator mutex is held.

Parser diagnostic integrations are pointer-sensitive. `%T` records offsets only when token pointers still refer into the current parse input. `%#T` skips expressions marked from DDL. Misuse outside active parse contexts should be harmless but will not produce useful offsets.

## Test Signals
Formatter tests should cover all public and internal conversion types, flags, width/precision combinations, `*` width/precision, `l`/`ll`, `SMALLEST_INT64`, alternate integer prefixes, thousands separators, pointer formatting, ordinal suffixes, NaN/Inf, `%g` fixed/exponential switching, locale independence of decimal points, and precision-limit clipping.

Escaping tests should cover null inputs, embedded quotes, backslashes, control characters, UTF-8 with `!`, precision truncation at character boundaries, `%#q/%#Q` `unistr()` output, JSON control escapes, `%J` null versus quoted string, and width padding after escaped output.

Accumulator tests should exercise fixed buffers (`sqlite3_snprintf()` truncation), dynamic growth, `SQLITE_TOOBIG`, OOM paths, adoption/freeing of `%z`, `sqlite3_str_truncate()`, `sqlite3_str_value()` on empty and non-empty strings, `sqlite3OomStr`, `sqlite3ResultStrAccum()` ownership transfer, and RC string ref/unref/resize behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/printf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/random.c -->
# sources/storage-engines/sqlite/src/random.c

## Purpose
`random.c` implements SQLite's process-wide pseudo-random byte generator. SQLite uses these bytes for internal needs such as random rowids, temporary filenames, and other backend randomness. The generator is based on the RFC 7539 ChaCha20 block function, seeded from the active VFS randomness source on first use, and protected by SQLite's static PRNG mutex in threadsafe builds.

This is not exposed as a cryptographic API contract to applications, but it is security-sensitive because poor randomness can affect filename unpredictability and rowid collision behavior.

## Important APIs, Types, and Functions
`sqlite3_randomness(int N, void *pBuf)` is the public/internal entry point. It fills `pBuf` with `N` bytes, initializes the global PRNG if needed, and resets the generator when called with `N<=0` or `pBuf==NULL`.

`chacha_block(u32 *out, const u32 *in)` implements the 20-round ChaCha block function using the `QR` quarter-round macro and `ROTL()` rotations. It copies the 16-word input state, performs 10 double rounds over columns and diagonals, then adds the original input words into the output words.

The global state is `sqlite3Prng`, a `sqlite3PrngType` containing `s[16]` ChaCha state words, `out[64]` cached output bytes, and `n` remaining cached bytes. With `SQLITE_OMIT_WSD`, the `GLOBAL()` macro locates writable static data at runtime; otherwise the static object is used directly.

When `SQLITE_UNTESTABLE` is not defined, `sqlite3PrngSaveState()` and `sqlite3PrngRestoreState()` copy the PRNG state to/from `sqlite3SavedPrng` for `sqlite3_test_control()` determinism.

## Control Flow
`sqlite3_randomness()` optionally auto-initializes SQLite, obtains `SQLITE_MUTEX_STATIC_PRNG` in threadsafe builds, and treats invalid or non-positive requests as a reset by setting `s[0]=0`. On the next real request, `s[0]==0` triggers initialization.

Initialization writes the ChaCha constants into `s[0..3]`, obtains 44 bytes of entropy from `sqlite3OsRandomness()` into `s[4]` onward when a VFS is available, or zero-fills those words in the unreachable no-VFS case. It then copies `s[12]` into `s[15]`, resets `s[12]` to zero as the block counter, and marks the cached output empty.

For output, the function first consumes any cached bytes from `out`. If the request fits in the cache, it copies from `&out[n-N]`, decrements `n`, and returns. Otherwise it copies remaining cached bytes from the start of `out`, advances the destination, increments `s[12]`, generates a new 64-byte ChaCha block into `out`, sets `n=64`, and repeats. The mutex is held for the entire request so state updates and cached-byte accounting are serialized.

## State and Persistence Behavior
The PRNG state is global to the process or SQLite library instance, not per database connection. It persists between calls until explicitly reset with `sqlite3_randomness(N<=0, NULL/non-NULL)` or restored by test controls. The cached output buffer is consumed from the end for partial reads and from the start when draining the remainder before a new block, so output order depends on `n` accounting.

The initial seed depends on the default VFS returned by `sqlite3_vfs_find(0)` and its `xRandomness` implementation via `sqlite3OsRandomness()`. The code requests 44 seed bytes beyond the 16-byte ChaCha constant. The block counter uses `s[12]` after moving the original seeded word into `s[15]`, preserving all seed material while making room for a counter.

Test save/restore snapshots include state words, cached output bytes, and remaining-byte count. They do not take the PRNG mutex themselves in this file, so callers must use them through the test-control path with appropriate external serialization expectations.

## Dependencies and Integration Points
The file depends on SQLite initialization, the VFS registry/randomness method, static mutex allocation, global writable static data support, and test-control infrastructure. `sqlite3_randomness()` is part of SQLite's public C API and is also used internally by subsystems that need random bytes.

Threading integration is simple but important: in `SQLITE_THREADSAFE` builds the static PRNG mutex serializes both initialization and output generation. In non-threadsafe builds, callers rely on the global SQLite threading mode contract.

## Risks and Edge Cases
Reset behavior is triggered by `N<=0` or `pBuf==NULL`; callers that accidentally pass a null buffer clear the PRNG state instead of getting an error. Initialization failure from `sqlite3_initialize()` returns without filling the output buffer, leaving caller-provided memory unchanged.

The no-VFS path zero-fills seed material, which would make output deterministic, but it is guarded by `NEVER(pVfs==0)` because normal SQLite initialization should always provide a VFS. VFS randomness quality directly affects PRNG unpredictability.

Counter overflow is not explicitly handled. The 32-bit `s[12]` counter increments once per 64-byte block. Exhausting the counter would require very large output volume from one seed; still, tests or analysis of long-running processes should be aware of the absence of a reseed or multiword counter increment.

The output cache accounting is non-obvious because partial fits copy from the tail of `out`, while draining cached bytes copies from the head. Changes to this logic can silently alter deterministic test expectations and should be tested through save/restore.

## Test Signals
Tests should cover reset followed by deterministic test-control save/restore, requests of 1 byte, 63 bytes, 64 bytes, 65 bytes, and multiple blocks; calls that exactly consume cached bytes; calls that partially consume cached bytes; `N<=0` reset; `pBuf==NULL` reset; auto-initialization failure handling where injectable; and concurrent calls in threadsafe builds.

ChaCha block tests can compare against known RFC 7539 block outputs for a fixed state if exposed through a test harness. VFS integration tests should verify that first use calls the VFS randomness provider and that saved/restored PRNG state reproduces byte streams exactly.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/random.c -->
