# sources/storage-engines/wiredtiger/test/3rdparty/sqlite3/sqlite3.c lines 179063-186320

## Scope

This chunk starts inside the generated Lemon parser reduction switch and continues through parser acceptance/error handling, tokenizer keyword/token classification, SQL statement completeness checking, the beginning of `main.c`, global and per-connection configuration, connection close/rollback/error/hook APIs, collation and limit setup, URI filename parsing, and most of the `sqlite3_open*()` implementation. It is an amalgamation chunk, so the code is source-tree aligned to SQLite subsystems rather than to one hand-written C module.

The chunk ends inside `sqlite3_open16()` after converting the UTF-16 filename to UTF-8 and before that wrapper's cleanup/return tail.

## Purpose

- Translate SQL grammar reductions into parse-tree and schema-building side effects for DDL, DML, expressions, triggers, virtual tables, CTEs, window functions, pragmas, attach/detach, vacuum, analyze, alter table, and reindex statements.
- Provide the generated parser entry points used by SQLite's SQL compiler: syntax-error handling, parser failure/acceptance, stack shifting/reduction, and `sqlite3RunParser()`.
- Classify SQL text into tokens and keywords, including SQLite's generated compact keyword hash table and special disambiguation for `WINDOW`, `OVER`, and `FILTER`.
- Implement `sqlite3_complete()` / `sqlite3_complete16()` to decide whether a text buffer contains a complete SQL statement, with special handling for `CREATE TRIGGER ... END;`.
- Initialize and shut down process-global SQLite state: mutexes, malloc, page cache, VFS, memdb, builtin functions, compile-time extra init hooks, and global configuration options.
- Configure individual database handles, lookaside memory, busy/progress/trace/profile/commit/update/rollback/preupdate/autovacuum/WAL hooks, error reporting, limits, collations, and temporary-storage policy.
- Parse filenames and `file:` URIs into the internal filename-plus-URI-parameter format consumed by the VFS and URI accessors.
- Open a `sqlite3` connection by allocating the handle, setting defaults, selecting the VFS, opening the main b-tree, loading built-ins/extensions, registering per-connection functions/collations, and setting WAL autocheckpoint defaults.

## Important APIs, Types, And Functions

- Parser reduction actions call many semantic builders: `sqlite3AddDefaultValue`, `sqlite3AddPrimaryKey`, `sqlite3CreateIndex`, `sqlite3CreateForeignKey`, `sqlite3SelectNew`, `sqlite3ExprListAppend`, `sqlite3PExpr`, `sqlite3BeginTrigger`, `sqlite3Trigger*Step`, `sqlite3Attach`, `sqlite3Detach`, `sqlite3Alter*`, `sqlite3Vtab*`, `sqlite3CteNew`, and `sqlite3Window*`.
- Parser runtime functions include `yy_parse_failed()`, `yy_syntax_error()`, `yy_accept()`, `sqlite3Parser()`, `sqlite3ParserFallback()`, and `sqlite3RunParser()`.
- Tokenizer and keyword APIs include `keywordCode()`, `sqlite3KeywordCode()`, `sqlite3_keyword_name()`, `sqlite3_keyword_count()`, `sqlite3_keyword_check()`, `sqlite3IsIdChar()`, `getToken()`, `analyzeWindowKeyword()`, `analyzeOverKeyword()`, `analyzeFilterKeyword()`, `sqlite3GetToken()`, and optional `sqlite3Normalize()`.
- Statement-completeness APIs are `sqlite3_complete()` and, when UTF-16 is enabled, `sqlite3_complete16()`.
- Global lifecycle/configuration APIs include `sqlite3_initialize()`, `sqlite3_shutdown()`, `sqlite3_config()`, `sqlite3_libversion()`, `sqlite3_libversion_number()`, and `sqlite3_threadsafe()`.
- Per-connection configuration and cache APIs include `setupLookaside()`, `sqlite3_db_mutex()`, `sqlite3_db_release_memory()`, `sqlite3_db_cacheflush()`, `sqlite3_db_config()`, and `sqlite3_limit()`.
- Connection lifecycle helpers include `sqlite3Close()`, `sqlite3_close()`, `sqlite3_close_v2()`, `sqlite3LeaveMutexAndCloseZombie()`, `sqlite3RollbackAll()`, `sqlite3CloseSavepoints()`, `disconnectAllVtab()`, and `connectionIsBusy()`.
- Hook and callback APIs include `sqlite3_busy_handler()`, `sqlite3_busy_timeout()`, `sqlite3_setlk_timeout()`, `sqlite3_progress_handler()`, `sqlite3_interrupt()`, `sqlite3_is_interrupted()`, `sqlite3_trace()`, `sqlite3_trace_v2()`, `sqlite3_profile()`, `sqlite3_commit_hook()`, `sqlite3_update_hook()`, `sqlite3_rollback_hook()`, `sqlite3_preupdate_hook()`, `sqlite3_autovacuum_pages()`, `sqlite3_wal_hook()`, and `sqlite3_wal_autocheckpoint()`.
- Function and collation registration uses `sqlite3CreateFunc()`, `createFunctionApi()`, `sqlite3_create_function*()`, `sqlite3_create_window_function()`, `sqlite3_overload_function()`, `createCollation()`, `binCollFunc()`, `rtrimCollFunc()`, `nocaseCollatingFunc()`, and `sqlite3IsBinary()`.
- WAL/checkpoint and error APIs include `sqlite3_wal_checkpoint_v2()`, `sqlite3_wal_checkpoint()`, `sqlite3Checkpoint()`, `sqlite3_errmsg()`, `sqlite3_errmsg16()`, `sqlite3_error_offset()`, `sqlite3_errcode()`, `sqlite3_extended_errcode()`, `sqlite3_system_errno()`, `sqlite3_errstr()`, `sqlite3ErrStr()`, and optional `sqlite3ErrName()`.
- Open path functions include `sqlite3ParseUri()`, `uriParameter()`, `openDatabase()`, `sqlite3_open()`, `sqlite3_open_v2()`, and the beginning of `sqlite3_open16()`.

## Control Flow

The parser section is generated control flow. Each grammar rule number enters a `case`, consumes semantic stack values from `yymsp`, builds or updates SQLite AST/schema objects, stores the result back into the parser stack, then falls through to common reduce logic. The common reduce tail computes the left-hand nonterminal, finds the next reduce action, adjusts the stack, and returns the new parser action. Parse failure pops the stack and runs parse-failure hooks; syntax errors delegate to `parserSyntaxError()` or report incomplete input; acceptance pops the stack and stores parser context.

`sqlite3RunParser()` drives tokenization and parsing together. It repeatedly calls `sqlite3GetToken()`, adjusts tokens that depend on context, passes tokens to `sqlite3Parser()`, tracks parser errors and error offsets, and finalizes with an end-of-input token. Tokenization is table-driven by first-byte character class, with explicit branches for comments, operators, quoted identifiers/strings, numeric literals, bracket identifiers, variables, blob literals, and bare identifiers. Bare identifiers of length at least two are passed through the generated keyword hash, then special window-function keywords can be demoted to identifiers if their surrounding tokens make them aliases or ordinary names.

`sqlite3_complete()` uses a small finite-state machine over a simplified token stream. In normal statements, reaching the `START` state after a semicolon means complete. With trigger support, entering a trigger body changes the expected terminator to `;END;`, so internal semicolons do not mark the whole statement complete.

`sqlite3_initialize()` first ensures WSD, pointer-size sanity, mutex initialization, and malloc initialization. It then serializes process-wide initialization with `pInitMutex`, registers built-in SQL functions, initializes page cache, initializes OS/VFS, optionally initializes memdb and extra hooks, and marks `sqlite3GlobalConfig.isInit` only after the sequence succeeds. `sqlite3_shutdown()` unwinds VFS, auto extensions, page cache, malloc, mutexes, and directory globals in reverse-ish order.

`sqlite3_config()` mutates `sqlite3GlobalConfig` before initialization for most opcodes, while allowing only logging and page-cache header-size queries after initialization. It accepts varargs for mutex, allocator, page cache, heap, lookaside, URI, mmap, PMA, statement-journal spill, rowid-in-view, and optional build-specific controls.

Connection close runs in stages. `sqlite3Close()` validates the handle, enters the connection mutex, emits trace close events, disconnects virtual tables, rolls back vtab transactions, and either returns `SQLITE_BUSY` for legacy `sqlite3_close()` if statements/backups remain or marks the connection as zombie. `sqlite3LeaveMutexAndCloseZombie()` later completes cleanup only when no statements/backups remain: rollback all b-trees, close savepoints and b-trees, clear schemas, modules, functions, collations, extensions, lookaside memory, mutexes, and the `sqlite3` allocation itself.

`openDatabase()` is the main open path. It autoinitializes the library, resolves mutex mode from global threading config and open flags, normalizes shared-cache flags, masks unsupported open flags, allocates and initializes the `sqlite3` object, installs default flags/limits/collations, rewrites optional `:localStorage:` and `:sessionStorage:` names, validates read/write/create flag combinations, parses the URI or filename, opens the main b-tree, attaches main/temp schemas, sets encoding and safety levels, registers per-connection built-ins and compiled-in/automatic extensions, applies optional default locking mode, enables lookaside, installs WAL autocheckpointing, and returns either an open handle, a sick handle, or NULL on allocation failure.

## State And Persistence Behavior

The parser and tokenizer mostly build in-memory `Parse`, `Expr`, `Select`, `SrcList`, `TriggerStep`, `With`, `Window`, and schema-related objects. Their side effects later become VDBE programs and schema changes, but this chunk itself is the construction and dispatch layer, not the b-tree writer for SQL statements.

Global state is concentrated in `sqlite3GlobalConfig`: initialization flags, mutex and malloc methods, page-cache buffers, lookaside defaults, URI defaults, mmap defaults, sorter and statement-journal settings, SQL logging, rowid-in-view policy, and VFS/pcache initialization state. Incorrect ordering matters because most `sqlite3_config()` opcodes are rejected after initialization.

Connection state lives in `sqlite3`: mutex, open state, error mask/code/message, flags, limits, lookaside freelists, schema array, b-tree pointers, registered functions/collations/modules, hooks, busy handler state, WAL callback state, temp-store mode, last rowid, change counters, deferred constraints, interrupt flag, and optional autovacuum callback. Close and rollback paths explicitly reset transactional, schema, savepoint, virtual table, hook-owned, and allocator-owned resources.

Persistence effects are indirect but important. URI `mode`, `cache`, and `vfs` options affect which database file is opened and with what access mode. Open flags decide read-only/read-write/create behavior and shared/private cache behavior. `openDatabase()` opens the main b-tree and initializes schemas; the pager/b-tree layers then own persistent database file state. Busy timeout, set-lock timeout, WAL hooks, WAL autocheckpoint, synchronous defaults, locking mode, and checkpoint APIs affect durability, locking, and WAL file lifecycle once transactions run.

Error state is persisted on the connection until overwritten. `sqlite3_errmsg*()`, `sqlite3_errcode()`, and `sqlite3_error_offset()` read `db->pErr`, `db->errCode`, `db->errMask`, and `db->errByteOffset`; extended result codes are masked unless the connection was opened with `SQLITE_OPEN_EXRESCODE`.

## Dependencies And Integration Points

- Generated Lemon parser tables and grammar symbols integrate with the surrounding SQLite parse subsystem and semantic constructors from create/select/expr/trigger/alter/vtab/window/with modules.
- Tokenization depends on character-class tables, `sqlite3CtypeMap`, `sqlite3Isdigit`, `sqlite3Isspace`, `sqlite3Isxdigit`, dequoting helpers, and compile-time ASCII/EBCDIC paths.
- Normalization depends on `sqlite3_str`, VDBE double-quoted-string tracking, token scanning, and SQLite allocation through the owning `sqlite3` handle.
- Initialization depends on mutex, memory, pcache, OS/VFS, memdb, builtin-function, and optional compile-time extension initialization hooks.
- Built-in extension loading integrates optional FTS3/FTS5, RTREE, ICU, DBPAGE, DBSTAT, JSON table functions, STMTVTAB, BYTECODE, and `SQLITE_EXTRA_AUTOEXT`.
- Database opening integrates with VFS lookup, URI filename format, b-tree open/schema APIs, pager locking mode, per-connection built-in function registration, automatic extensions, WAL autocheckpoint, and lookaside allocation.
- Hook APIs integrate external application callbacks into VDBE execution, pager/busy handling, commit/update/rollback notifications, preupdate processing, autovacuum page callbacks, tracing/profile callbacks, and WAL commit/checkpoint behavior.
- Configuration and limit APIs are public C API integration points used by embedders before initialization and by applications per connection.

## Risks And Edge Cases

- This is generated and amalgamated code; hand edits to parser reductions, keyword tables, or tokenizer tables can desynchronize generated metadata and grammar behavior.
- Parser reductions transfer ownership among AST objects by direct pointer assignment. Error paths depend on later destructors and explicit deletes; missing a delete or clearing the wrong semantic value can leak or double-free parse objects.
- Token classification has many context-sensitive exceptions. `WINDOW`, `OVER`, and `FILTER` disambiguation is especially sensitive because changing fallback behavior can silently alter valid SQL parses.
- `sqlite3_complete()` is a lightweight scanner, not a full parser. It intentionally ignores many SQL details and can only answer statement completeness, so callers must still prepare/parse the SQL for correctness.
- Most `sqlite3_config()` operations are unsafe after initialization and return misuse/error if called too late. Embedders that call `sqlite3_open()` first may find later allocator/mutex/page-cache configuration ignored or rejected.
- `setupLookaside()` refuses to reconfigure while lookaside slots are in use. It also clamps slot size/count, so requested settings may be reduced or disabled.
- Closing semantics differ between `sqlite3_close()` and `sqlite3_close_v2()`: the first returns busy with active statements/backups, while the second zombie-closes and defers final deallocation. Code that assumes immediate finalizers can mis-handle `close_v2()`.
- Hook setters store raw callback pointers and user data. SQLite does not own that memory, so application lifetime discipline is required.
- `sqlite3CreateFunc()` rejects modifications while VDBEs are active and invalidates prepared statements when overriding functions. Destructor reference counting is subtle for `SQLITE_ANY`, which creates multiple encoding-specific `FuncDef` entries sharing one destructor object.
- URI parsing has security-sensitive behavior: authority handling depends on `SQLITE_ALLOW_URI_AUTHORITY`; `%00` either truncates the current URI component or errors depending on `SQLITE_ENABLE_URI_00_ERROR`; query parameters can alter VFS, access mode, and shared-cache behavior.
- Open flag validation only allows sensible read-only/read-write/create combinations after masking internal bits. Invalid combinations return `SQLITE_MISUSE_BKPT` before reaching lower b-tree assertions.
- Error-message APIs can allocate while converting UTF-16 messages and may clear OOM flags in controlled ways; callers must not assume error strings survive after later API calls.
- WAL checkpointing over all attached databases collapses multiple busy results into one final `SQLITE_BUSY`, and output counters are only meaningful for the first checkpointed database because the pointers are nulled after the first use.

## Test Signals

- Parser tests should cover DDL constraints, defaults, generated columns, foreign keys, compound SELECTs, VALUES, nested FROM terms, joins, triggers, CTEs, window frames, virtual tables, ALTER TABLE variants, `RAISE()`, `ATTACH`, `DETACH`, `VACUUM`, `PRAGMA`, and `IN`/`BETWEEN` expression rewrites.
- Tokenizer tests should cover comments, bracket/backtick/double/single-quoted tokens, blob literals, variables, digit separators, hex integers, floating-point exponents, JSON pointer operators, illegal tokens, keyword fallback, and `WINDOW`/`OVER`/`FILTER` ambiguity.
- `sqlite3_complete()` tests should include whitespace-only input, comments, unterminated comments/quotes/brackets, simple semicolon termination, and trigger bodies requiring `;END;`.
- Initialization/configuration tests should verify pre-init versus post-init `sqlite3_config()` behavior, custom mutex/malloc/pcache hooks, URI global defaults, mmap clamping, lookaside defaults, page-cache header-size queries, and shutdown/reinitialize cycles.
- Connection lifecycle tests should cover `sqlite3_open`, `sqlite3_open_v2`, invalid flag combinations, NULL filename memory databases, URI `mode/cache/vfs`, invalid URI authorities, `%00` behavior under both compile options, missing VFS errors, OOM during open, and sick-handle return behavior.
- Close tests should exercise `sqlite3_close()` busy returns with unfinalized statements/backups, `sqlite3_close_v2()` zombie cleanup after finalization, virtual table disconnect/rollback, open transaction rollback, function/collation destructor invocation, and lookaside deallocation.
- Hook tests should cover busy timeout backoff, progress callbacks, interrupts, trace/profile callbacks, commit/update/rollback/preupdate hooks, autovacuum page callbacks, WAL hooks, autocheckpoint setup, and checkpoint modes including busy attached databases.
- Error and limit tests should cover extended result-code masking, UTF-8/UTF-16 error messages, error offsets from parse failures, system errno retrieval, hard-limit clamping, invalid limit IDs, and per-connection config flags expiring prepared statements.
