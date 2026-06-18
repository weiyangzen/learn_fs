# sources/storage-engines/foundationdb/contrib/sqlite/sqlite3.amalgamation.c lines 89545-96988

## Scope And Purpose

This chunk spans several consecutive SQLite amalgamation units in the FoundationDB repository: the tail of generated `parse.c`, all of `tokenize.c`, all of `complete.c`, most of `main.c`, all of `notify.c` behind `SQLITE_ENABLE_UNLOCK_NOTIFY`, and the opening portion of `fts3.c` through the beginning of phrase-position merge logic. The code forms the boundary between SQL text input and SQLite's core runtime APIs, then starts the FTS3/FTS4 virtual-table implementation.

The first section finishes parser reduction actions for common SQL grammar productions. It builds AST objects for `SELECT`, `FROM`, joins, `ORDER BY`, `GROUP BY`, `LIMIT`, DML statements, scalar expressions, `IN`, `BETWEEN`, `CASE`, `CREATE INDEX`, `PRAGMA`, triggers, and `RAISE()`, then closes the LEMON parser driver. These actions do not execute SQL directly; they allocate and link `Expr`, `ExprList`, `Select`, `SrcList`, `IdList`, `TriggerStep`, and related parse structures that later code generation consumes.

The tokenizer section implements SQL token classification, keyword lookup, parser driving, parser cleanup, and SQL completeness checks. It converts SQL bytes into token types, runs the generated parser with a `Parse` context, handles syntax/token errors, enforces SQL-length limits, frees parse-time scratch state, and implements the public `sqlite3_complete()` and `sqlite3_complete16()` APIs.

The main API section initializes and shuts down SQLite process-global subsystems, opens and closes database connections, manages global and per-connection configuration, registers functions/collations/hooks, exposes error/status APIs, drives WAL checkpoint requests, rolls back all btrees for a handle, and implements test-control and file-control entry points. This is the most externally visible part of the chunk.

The unlock-notify section tracks connections blocked on shared-cache locks and schedules callbacks when blocking transactions finish. The FTS3 section introduces the on-disk FTS segment/doclist format, tokenizer/hash APIs, key FTS3 table/cursor/query structs, virtual-table creation/connect/open planning, FTS shadow-table creation, varint/doclist helpers, and segment-interior traversal used to find leaf blocks for a term or prefix.

## Important APIs, Types, And Functions

Parser reduction helpers and generated parser entry points:

- `sqlite3Parser()` is the LEMON parser driver. It shifts/reduces tokens, invokes grammar action cases, handles syntax errors, and accepts or fails the parse.
- Grammar action cases in this range call builders such as `sqlite3ExprListAppend()`, `sqlite3ExprListSetName()`, `sqlite3ExprListSetSpan()`, `sqlite3PExpr()`, `sqlite3Expr()`, `sqlite3SrcListAppendFromTerm()`, `sqlite3SrcListIndexedBy()`, `sqlite3SelectNew()`, `sqlite3DeleteFrom()`, `sqlite3Update()`, `sqlite3Insert()`, `sqlite3CreateIndex()`, `sqlite3Pragma()`, `sqlite3BeginTrigger()`, `sqlite3FinishTrigger()`, and trigger-step constructors.
- Expression actions build `TK_DOT`, `TK_REGISTER`, `TK_VARIABLE`, `TK_CAST`, function calls, infix `LIKE`/`MATCH`, unary/binary operators, `TK_BETWEEN`, `TK_IN`, `TK_SELECT`, `TK_EXISTS`, `TK_CASE`, and `TK_RAISE` nodes. They also preserve token spans for error messages and column aliases.
- Parser error routines `yy_parse_failed()`, `yy_syntax_error()`, and `yy_accept()` close out failed or successful parser states.

Tokenizer and parser-runner APIs:

- `keywordCode()` and `sqlite3KeywordCode()` are generated keyword hash lookups. They map identifier text to parser token codes such as `TK_SELECT`, `TK_JOIN_KW`, `TK_PRAGMA`, `TK_MATCH`, or `TK_ID`.
- `sqlite3GetToken(const unsigned char *z, int *tokenType)` returns the byte length and token type of the next SQL token. It recognizes whitespace/comments, operators, quoted identifiers and strings, numeric literals, bracket identifiers, variables, internal `#NNN` registers, blob literals, identifiers, and keywords.
- `sqlite3RunParser(Parse *pParse, const char *zSql, char **pzErrMsg)` allocates the parser engine, feeds tokens from `sqlite3GetToken()`, appends implicit semicolon and EOF tokens, collects parse errors, deletes invalid VDBEs after top-level parse failure, and frees all parse scratch allocations.
- `sqlite3_complete()` and `sqlite3_complete16()` determine whether a SQL string contains a complete statement. The UTF-8 form is a small state machine with special `CREATE TRIGGER ... END;` handling; the UTF-16 form converts to UTF-8 through a transient `sqlite3_value`.

Core public and private APIs in `main.c`:

- Version and compile-mode APIs: `sqlite3_libversion()`, `sqlite3_sourceid()`, `sqlite3_libversion_number()`, and `sqlite3_threadsafe()`.
- Process lifecycle: `sqlite3_initialize()` initializes mutexes, malloc, global functions, page cache, OS/VFS, and page-cache buffers. `sqlite3_shutdown()` tears down OS, auto-extensions, pcache, malloc, and mutex subsystems.
- Configuration: `sqlite3_config()` mutates `sqlite3GlobalConfig` before initialization. `setupLookaside()` and `sqlite3_db_config()` configure connection lookaside memory. `sqlite3_limit()` returns and optionally changes per-connection limits bounded by `aHardLimit[]`.
- Connection lifecycle: `openDatabase()` backs `sqlite3_open()`, `sqlite3_open_v2()`, and `sqlite3_open16()`. It validates flags, selects mutex behavior, allocates `sqlite3`, initializes schemas/collations/builtins/extensions, opens the main btree, sets defaults, enables lookaside, and configures WAL autocheckpointing. `sqlite3_close()` closes btrees, virtual tables, statements/modules/collations/functions, extensions, lookaside, mutexes, and the database object.
- Transaction cleanup: `sqlite3RollbackAll()` rolls back every attached btree, rolls back virtual-table transactions, expires prepared statements if schema changed, clears deferred constraints, and invokes the rollback hook when applicable. `sqlite3CloseSavepoints()` clears connection-level savepoint structures.
- Function and collation registration: `sqlite3CreateFunc()`, `sqlite3_create_function*()`, `sqlite3_overload_function()`, `createCollation()`, and `sqlite3_create_collation*()` install per-connection `FuncDef` and `CollSeq` entries, manage destructors, and expire active prepared statements as needed.
- Status, hooks, and control APIs: `sqlite3_errmsg*()`, `sqlite3_errcode()`, `sqlite3_extended_errcode()`, `sqlite3_busy_handler()`, `sqlite3_busy_timeout()`, `sqlite3_progress_handler()`, `sqlite3_interrupt()`, `sqlite3_trace()`, `sqlite3_profile()`, commit/update/rollback hooks, WAL hook/autocheckpoint/checkpoint APIs, `sqlite3_get_autocommit()`, `sqlite3_sleep()`, `sqlite3_extended_result_codes()`, `sqlite3_file_control()`, and `sqlite3_test_control()`.
- Metadata and diagnostics: `sqlite3_table_column_metadata()` is compiled when column metadata is enabled. `sqlite3CorruptError()`, `sqlite3MisuseError()`, and `sqlite3CantopenError()` log source-line diagnostics for breakpoint-friendly error macros.

Unlock-notify APIs:

- `sqlite3_unlock_notify()` registers, cancels, immediately invokes, or rejects unlock-notify callbacks for a blocked connection.
- `sqlite3ConnectionBlocked()`, `sqlite3ConnectionUnlocked()`, and `sqlite3ConnectionClosed()` maintain the process-global blocked connection list and dispatch callbacks.
- `sqlite3BlockedList`, `pBlockingConnection`, `pUnlockConnection`, `xUnlockNotify`, `pUnlockArg`, and `pNextBlocked` are the core state for blocked connections. Access is serialized by `SQLITE_MUTEX_STATIC_MASTER`.

FTS3/FTS4 types and functions:

- `sqlite3_tokenizer_module`, `sqlite3_tokenizer`, and `sqlite3_tokenizer_cursor` define the tokenizer plugin ABI used by FTS tables.
- `Fts3Hash` and `Fts3HashElem` define a standalone hash table used by FTS3 for tokenizer registries and pending terms.
- `Fts3Table` is the virtual table instance. It stores the owning `sqlite3 *`, database/table names, user columns, tokenizer, cached statements, expression lists for compressed/uncompressed content access, node/page sizing, shadow-table capability flags, an optional `%_segments` blob handle, and pending terms buffered during transactions.
- `Fts3Cursor` stores the virtual table cursor state, including selected search strategy, current SQL statement, MATCH expression tree, doclist cursor state, deferred tokens, and matchinfo buffers.
- `Fts3PhraseToken`, `Fts3Phrase`, and `Fts3Expr` model MATCH query tokens, phrases, NEAR/AND/OR/NOT trees, loaded doclists, and current docid positions.
- `sqlite3Fts3PutVarint()`, `sqlite3Fts3GetVarint()`, `sqlite3Fts3GetVarint32()`, and `sqlite3Fts3VarintLen()` implement FTS3's little-endian varint encoding, distinct from SQLite btree varints.
- `sqlite3Fts3Dequote()`, `fts3GetDeltaVarint()`, `fts3GetDeltaVarint2()`, `fts3PutDeltaVarint()`, `fts3PoslistCopy()`, `fts3ColumnlistCopy()`, `fts3ReadNextPos()`, `fts3PutColNumber()`, `fts3PoslistMerge()`, and the beginning of `fts3PoslistPhraseMerge()` manipulate FTS doclist/position-list encodings.
- `fts3DisconnectMethod()`, `fts3DestroyMethod()`, `fts3DeclareVtab()`, `fts3CreateTables()`, `fts3DatabasePageSize()`, `fts3InitVtab()`, `fts3ConnectMethod()`, `fts3CreateMethod()`, `fts3BestIndexMethod()`, `fts3OpenMethod()`, `fts3CloseMethod()`, and `fts3CursorSeek()` implement early FTS3 virtual-table lifecycle, planning, cursor, and content-row seek behavior.
- `fts3ScanInteriorNode()` and `fts3SelectLeaf()` traverse serialized segment interior nodes to identify leaf block ranges that may contain a term or term prefix.

## Control Flow

SQL parsing begins with `sqlite3RunParser()`. It initializes `pParse`, allocates the LEMON parser, temporarily enables lookaside allocations when available, and loops over the SQL text. Each iteration calls `sqlite3GetToken()`, advances by the returned length, enforces `SQLITE_LIMIT_SQL_LENGTH`, ignores spaces/comments except for interrupt polling, reports `TK_ILLEGAL` tokens immediately, and sends all ordinary tokens to `sqlite3Parser()`. If the input ends without syntax or runtime parse error, it injects a semicolon if needed and then EOF token `0`.

`sqlite3GetToken()` is a switch-driven scanner. Single-character and two-character operators are returned directly; `--` and `/*...*/` comments become `TK_SPACE`; quote-delimited strings and identifiers are scanned with doubled-quote escaping; numeric tokens are classified as integer or float and become illegal if followed by identifier characters; bind parameters can be `?NNN`, `$name`, `@name`, `:name`, and Tcl-style `$name(...)`; `#NNN` is treated as an internal register reference for nested parses. Unquoted identifiers are handed to `keywordCode()`, which uses generated compact arrays and case-insensitive comparison to avoid a general-purpose hash table.

Generated parser reductions build tree state bottom-up. For example, `FROM` terms accumulate in `SrcList`, join modifiers flow through `sqlite3JoinType()` and `sqlite3SrcListShiftJoinType()`, sort/group/expression lists accumulate through `ExprList`, and DML/DDL grammar rules dispatch to higher-level parse routines. `IN ()` is simplified during parsing into constant true/false depending on `NOT`; `IN (SELECT ...)` and scalar subqueries set `EP_xIsSelect`; function calls enforce the per-connection function-argument limit; trigger grammar rejects qualified target table names and `INDEXED BY` inside trigger DML.

Parser shutdown is centralized in `sqlite3RunParser()`. It exports parse error text through `pzErrMsg`, logs parse errors, deletes an invalid top-level VDBE when parsing failed, releases shared-cache table locks and virtual-table locks, deletes partially constructed tables/triggers unless ownership has moved to virtual-table declaration code, frees variable-expression arrays and aliases, drains autoincrement and zombie-table lists, restores the saved lookaside state, and normalizes the return code.

`sqlite3_complete()` does not invoke the full parser. It tokenizes just enough to recognize semicolon completion and trigger bodies. With triggers enabled, it uses an eight-state transition table over `SEMI`, whitespace, ordinary tokens, `EXPLAIN`, `CREATE`, `TEMP`, `TRIGGER`, and `END`. It returns true only in the `START` state after at least one complete statement. Unterminated comments, quoted identifiers, strings, and bracket identifiers return false.

`sqlite3_initialize()` first initializes WSD if needed, then returns immediately if `isInit` is already true. Otherwise it initializes the mutex subsystem, uses the static master mutex to initialize malloc and allocate a recursive init mutex, enters the recursive init mutex to register global SQL functions, initialize pcache, initialize OS/VFS, install page-cache buffers, and finally set `isInit`. The recursive mutex allows `sqlite3_os_init()` paths to call back into initialization safely. Afterward, the temporary init mutex is freed when its reference count drops to zero.

`openDatabase()` is the central connection-open path. It autoinitializes SQLite, rejects nonsensical open flag combinations, derives thread-safety and shared-cache flags, masks internal-only flags, allocates the `sqlite3` object and optional recursive mutex, initializes limits and defaults, registers built-in collations, resolves the VFS, opens the main btree, obtains schemas, registers built-in functions and automatic extensions, initializes optional extensions such as FTS3/ICU/RTREE, sets default locking mode, configures lookaside, and installs the default WAL autocheckpoint hook. On error it keeps a "sick" handle for many errors but fully closes and nulls the handle on `SQLITE_NOMEM`.

`sqlite3_close()` enters the connection mutex, resets schema state, rolls back virtual-table transactions, rejects close while VDBEs or backup operations remain active, closes savepoints and all btrees, resets schemas again, notifies unlock-notify code that the connection is gone, destroys function/collation/module registrations with their destructors, clears error objects and extensions, frees temp schema and lookaside memory, destroys the mutex, marks the handle closed, and frees `sqlite3`.

`sqlite3_wal_checkpoint_v2()` validates checkpoint mode, resolves a named attached database if supplied, and delegates to `sqlite3Checkpoint()`. `sqlite3Checkpoint()` iterates either one database or all attached databases, calls `sqlite3BtreeCheckpoint()`, and converts any encountered per-btree `SQLITE_BUSY` into a final `SQLITE_BUSY` after continuing through eligible databases.

Unlock-notify flow begins when `sqlite3ConnectionBlocked()` records that a connection is blocked by another and adds it to `sqlite3BlockedList`. `sqlite3_unlock_notify()` either cancels state, immediately invokes the callback if there is no blocker, rejects deadlock when following `pUnlockConnection` reaches the registering connection, or records the callback and groups the connection in the blocked list by callback pointer. `sqlite3ConnectionUnlocked()` scans the blocked list when a transaction releases locks, clears blocker references, batches callback arguments for matching callback functions, grows the argument array when needed, invokes callbacks, and removes entries with no remaining block/unlock relation.

FTS3 virtual-table creation and connection flow goes through `fts3InitVtab()`. It parses module arguments, initializes a tokenizer from `tokenize=...` or the default `simple` tokenizer, interprets FTS4 options such as `matchinfo=fts3`, `compress=...`, and `uncompress=...`, derives column names, allocates a single `Fts3Table` block holding struct, column pointer array, table/database names, and copied column-name strings, validates paired compression options, builds read/write expression lists, creates shadow tables for `xCreate`, reads database page size for cost estimates, and declares the virtual table schema with hidden MATCH and `docid` columns. On failure it destroys either the partially built table or tokenizer.

FTS3 planning in `fts3BestIndexMethod()` chooses among full scan, rowid/docid lookup, and MATCH search. It defaults to a costly full scan, lowers cost for rowid/docid equality, and prefers the first usable MATCH constraint over rowid lookup so the core will not leave MATCH as an unusable scalar function. The selected constraint is assigned `argvIndex = 1` and marked omitted.

FTS3 segment lookup uses serialized interior nodes. `fts3ScanInteriorNode()` skips height and leftmost child varints, reconstructs delta-encoded separator terms into a growable buffer, compares each separator with the requested term, and returns first/last child blockids that can contain the exact term or prefix range. `fts3SelectLeaf()` reads child interior blocks through `sqlite3Fts3ReadBlock()` and recurses until leaf-level blockids are selected.

FTS3 doclist helpers operate on tightly packed buffers. Delta varints encode increasing docids or positions. Position lists are terminated by `POS_END` and column changes by `POS_COLUMN`. `fts3PoslistCopy()` advances and optionally copies an entire position list, `fts3ColumnlistCopy()` handles one column list without copying the terminator, `fts3PoslistMerge()` merges two position lists by column and by sorted positions while suppressing duplicates, and `fts3PutColNumber()` emits nonzero column headers.

## State And Persistence Behavior

Parser and tokenizer state is transient. `sqlite3RunParser()` mutates `Parse`, temporary AST allocations, temporary VDBE state, `db->lookaside.bEnabled`, `db->u1.isInterrupted`, and error fields. It does not persist database changes by itself. Persistence occurs later when parse routines generate VDBE programs and those programs execute.

`sqlite3_complete()` has no durable side effects. It scans input and returns a boolean based on its local state machine. `sqlite3_complete16()` allocates a temporary `sqlite3_value`, converts the string, and frees it before return.

Global SQLite state is persistent for the process. `sqlite3_initialize()` mutates `sqlite3GlobalConfig` subsystem flags, mutex pointers, registered global functions, page-cache configuration, and VFS/OS state. `sqlite3_shutdown()` clears those same process-global subsystems and must only be called when SQLite is otherwise unused.

Connection state is durable for the lifetime of `sqlite3 *`. `openDatabase()` initializes limits, flags, default schemas, function/collation registries, btree pointers, lookaside buffers, hooks, and extension state. `sqlite3_close()` tears all of this down. `setupLookaside()` may free a previous lookaside buffer and install a caller-supplied or malloc-owned replacement; it refuses changes while lookaside allocations are outstanding.

Disk persistence in this chunk is mostly indirect. `openDatabase()` opens the main btree file and may create or initialize extension state, but it does not necessarily write schema data. `sqlite3RollbackAll()` rolls back btree and virtual-table transactions, which reverts durable changes made elsewhere. WAL checkpoint APIs can persist checkpoint progress by delegating to btree/pager/WAL layers. `sqlite3_file_control()` may invoke VFS-specific operations that can mutate file-control state outside SQLite's portable abstraction.

Function and collation registration persist in the connection's in-memory registries. Replacing an existing function or collation expires prepared statements if no VM is active, and returns `SQLITE_BUSY` if active VMs would make replacement unsafe. Registered destructors are retained and invoked only when the final function copy or collation registration is destroyed or replaced.

Error and hook state lives on the connection. Busy, progress, trace, profile, commit, update, rollback, WAL, collation-needed, and extended-result-code APIs install callback pointers and callback arguments under the connection mutex. `sqlite3_interrupt()` sets `db->u1.isInterrupted`, which the parser notices while consuming whitespace and VDBE execution paths observe elsewhere.

Unlock-notify state is process-global plus per-connection. The blocked-list links and callback state are memory-only and protected by the static master mutex. `sqlite3ConnectionClosed()` releases callbacks and removes a closing connection so no later unlock dispatch references freed memory.

FTS3 `xCreate` persists five possible shadow tables: `%_content`, `%_segments`, `%_segdir`, and for FTS4 `%_docsize` and `%_stat`. `xDestroy` drops those tables. `Fts3Table.pendingTerms` buffers transaction-local index updates in memory until flush paths outside this chunk create new segment rows. Segment/doclist helpers define the durable binary format stored in `%_segments`, `%_segdir.root`, and doclist blobs.

## Dependencies And Integration Points

The parser reduction code depends on parser token definitions, AST structures, allocation helpers, expression/list/source builders, DML/DDL parse routines, trigger constructors, and VDBE generation later in the pipeline. It is generated from SQLite grammar but embedded directly in the amalgamation.

Tokenizer and parser-runner code integrates with character classification tables (`sqlite3CtypeMap`, `sqlite3UpperToLower`, EBCDIC maps), keyword token constants, `sqlite3ParserAlloc()`, `sqlite3ParserFree()`, `sqlite3Parser()`, parse error helpers, lookaside allocation, shared-cache table-lock cleanup, virtual-table lock cleanup, autoincrement bookkeeping, and statement deletion.

Main API code integrates with nearly every SQLite subsystem: mutex, malloc, scratch/pagecache, OS/VFS, btree, pager, WAL, schema, virtual tables, extension autoloading, FTS/ICU/RTREE optional modules, collation/function lookup, prepared statement invalidation, error reporting, test hooks, and file-control dispatch.

`openDatabase()` calls `sqlite3BtreeOpen()` for the main database, `sqlite3SchemaGet()` for main and temp schemas, `sqlite3RegisterBuiltinFunctions()`, `sqlite3AutoLoadExtensions()`, optional `sqlite3Fts3Init()`, `sqlite3IcuInit()`, and `sqlite3RtreeInit()`, then `setupLookaside()` and `sqlite3_wal_autocheckpoint()`. This makes it the registration point for several compile-time feature modules covered later in the file.

WAL functions integrate with btree checkpointing through `sqlite3BtreeCheckpoint()`, and with commit-time WAL hooks through `db->xWalCallback` and `sqlite3WalDefaultHook()`. Busy handlers depend on the VFS `xSleep` implementation through `sqlite3OsSleep()`.

Unlock-notify depends on shared-cache lock conflict paths setting `db->pBlockingConnection` through `sqlite3ConnectionBlocked()`, and on transaction close paths calling `sqlite3ConnectionUnlocked()`. It is compiled only when `SQLITE_ENABLE_UNLOCK_NOTIFY` is enabled.

FTS3 integrates with SQLite's virtual-table module API (`sqlite3_vtab`, `sqlite3_vtab_cursor`, `sqlite3_index_info`, `sqlite3_declare_vtab()`), tokenizer registration (`sqlite3Fts3InitTokenizer()` and tokenizer modules), SQL execution (`sqlite3_exec`, `sqlite3_prepare`, `sqlite3_step`, `sqlite3_finalize`), blob/statement APIs, shadow tables, and later FTS3 read/write/query modules declared in this chunk (`sqlite3Fts3UpdateMethod()`, `sqlite3Fts3PendingTermsFlush()`, `sqlite3Fts3SegReader*()`, `sqlite3Fts3Expr*()`, snippet/offset/matchinfo functions).

## Risks And Edge Cases

The parser action section is generated, dense, and type-indexed through `yygotominor`/`yymsp` union fields. Edits are risky unless regenerated from grammar, because one wrong minor-type assumption can corrupt parse state. The chunk also contains many ownership transfers; failed allocation paths rely on later parser cleanup to free partially built structures.

`sqlite3GetToken()` must avoid overreading while classifying malformed input. It returns `TK_ILLEGAL` for unterminated quotes, malformed blob literals, variables with no name, numeric literals followed by identifier characters, and unsupported characters. Changes to identifier rules can affect keyword recognition, bind parameter parsing, and `sqlite3_complete()` consistency.

`sqlite3RunParser()` temporarily changes `db->lookaside.bEnabled`. Any future early return must restore it and free the parser engine. The current implementation funnels through cleanup, but maintenance edits in this function can easily create leaks of `pParse->pNewTable`, trigger state, table locks, virtual-table locks, alias arrays, autoincrement info, or zombie tables.

`sqlite3_complete()` is intentionally approximate and independent of the full parser. Its quote handling scans to the next matching quote and does not implement doubled quote escaping like `sqlite3GetToken()` does. It is designed for statement-boundary detection, so tests should not assume full syntax validation.

`sqlite3_initialize()` and `sqlite3_shutdown()` are process-global and have strict call-order assumptions. Calling `sqlite3_config()` after initialization returns misuse. Calling shutdown while connections, memory allocations, or threads are active is documented unsafe. Recursive initialization relies on `inProgress`, `pInitMutex`, and reference counting remaining consistent.

`openDatabase()` returns a non-null sick handle for many open failures. Callers must inspect the return code and may still need to close the handle. The function also masks unsupported open flags silently after validating the access-mode combination, which can surprise callers expecting all flag bits to be honored.

Function and collation replacement is blocked while VMs are active, but only when replacing an existing matching entry. Destructor reference counts are subtle when `SQLITE_ANY` creates multiple encoded variants. A destructor passed to `sqlite3_create_function_v2()` is invoked immediately on allocation failure or later when the final function copy is destroyed.

`sqlite3_close()` returns `SQLITE_BUSY` if statements or backups remain. It also rolls virtual-table state before checking active statements so virtual table implementations can release internally held statements. Tests should cover both user-visible busy cases and cleanup after modules with `xDestroy` callbacks.

`sqlite3CorruptError()` in this FoundationDB copy prints directly with `printf("database corruption line %d\n", lineno)` in addition to `sqlite3_log()`. That is unusual for SQLite library code and can leak diagnostics to stdout in embedders.

Unlock-notify invokes callbacks while holding the static master mutex in this version. Callback implementations must avoid re-entering APIs that could deadlock on the same global mutex. The code has special handling for OOM while growing the callback-argument array, but it can split one logical callback group into multiple invocations.

FTS3 varint parsing assumes buffers are valid enough for the caller's context. Some comments document padding guarantees for segment blocks, but corruption can still return `SQLITE_CORRUPT` only after partial decoding. Position-list routines such as `fts3PoslistCopy()` and `fts3ColumnlistCopy()` rely on well-formed terminators and are unsafe for arbitrary untrusted buffers without surrounding integrity checks.

FTS3 `fts3InitVtab()` parses `tokenize` by checking the first eight bytes and then passes `&z[9]`, assuming the ninth character separates the option name and tokenizer arguments. Option syntax changes can break compatibility. FTS4 compression options must be paired; missing `compress` or `uncompress` is a hard constructor error.

FTS3 `xConnect()` in this chunk does not verify that shadow tables already exist; the comment marks this as a TODO. A malformed schema can therefore connect successfully and fail later during reads or writes.

## Test Signals

Parser/tokenizer tests should cover all token classes in `sqlite3GetToken()`: comments as whitespace, nested-looking but non-nested C comments, doubled quotes in string and identifier tokens, unterminated quotes, numeric integer/float/exponent forms, invalid numeric suffixes, blob literal even-length enforcement, `?NNN`/`$name`/`@name`/`:name` variables, internal `#NNN` registers in nested and non-nested parses, bracket identifiers, and all generated keywords exposed through `sqlite3KeywordCode()`.

SQL parse tests should exercise the grammar actions present in this range: joins with `ON` and `USING`, table and subquery `FROM` terms, `ORDER BY` sort directions, `GROUP BY`/`HAVING`, both `LIMIT ... OFFSET ...` syntaxes, `DELETE`, `UPDATE`, `INSERT ... VALUES`, `INSERT ... SELECT`, `DEFAULT VALUES`, collations, casts, function calls with too many args, empty `IN ()` and `NOT IN ()`, subquery `IN`, `EXISTS`, `CASE`, `CREATE INDEX`, `PRAGMA` forms, trigger creation, trigger DML restrictions, and `RAISE()`.

Completeness tests should include whitespace-only strings, ordinary semicolon-terminated statements, statements with semicolons inside strings/comments/quoted identifiers, unterminated comments/quotes, `EXPLAIN CREATE TEMP TRIGGER ... BEGIN ...; END;`, and builds with `SQLITE_OMIT_TRIGGER`.

Core API tests should verify initialization idempotence, shutdown after initialization, rejection of `sqlite3_config()` after initialization, legal and illegal `sqlite3_open_v2()` flag combinations, sick-handle behavior on open errors, lookaside reconfiguration returning `SQLITE_BUSY` while slots are checked out, limit clamping to hard limits, close returning `SQLITE_BUSY` for unfinalized statements and unfinished backups, rollback-hook behavior in `sqlite3RollbackAll()`, and destructor behavior for functions/collations.

WAL and hook tests should cover `sqlite3_wal_autocheckpoint()` installing and disabling the default hook, invalid checkpoint modes returning misuse, unknown database names returning error, all-database checkpoint iteration, and `SQLITE_BUSY` propagation when one checkpoint target is busy. Busy-timeout tests should validate retry counts and timeout boundaries with the configured VFS sleep path.

Error API tests should cover null handles, sick handles, malloc-failure paths in `sqlite3_errmsg()` and `sqlite3_errmsg16()`, extended result-code masking, `sqlite3_interrupt()` visibility during parse and execution, and `sqlite3_file_control()` for unknown database names, null btrees, `SQLITE_FCNTL_FILE_POINTER`, VFS-handled controls, and no-method `SQLITE_NOTFOUND`.

Unlock-notify tests should require shared-cache builds. They should cover immediate callback when no blocker remains, replacing a prior callback on the same connection, cancellation with `xNotify == NULL`, deadlock detection through blocker chains, grouped callback delivery for same `xUnlockNotify`, closing a blocked or blocking connection, and OOM simulation while growing the callback argument array.

FTS3/FTS4 tests should create FTS3 and FTS4 tables with default and explicit tokenizers, quoted column names, no explicit columns, `matchinfo=fts3`, paired and unpaired `compress`/`uncompress`, and verify shadow-table creation/destruction. Query-planner tests should inspect `xBestIndex` choices for full scan, docid equality, column MATCH, table-wide MATCH, unusable constraints, and MATCH preferred over docid equality when both are present.

FTS3 format tests should round-trip `sqlite3Fts3PutVarint()`/`sqlite3Fts3GetVarint()` across boundary values, decode invalid or truncated segment interiors as corruption where checked, verify `fts3SelectLeaf()` leaf ranges for exact and prefix searches across multi-level segment trees, and validate position-list union/phrase merge behavior across columns, duplicate positions, empty lists, and terminators.
