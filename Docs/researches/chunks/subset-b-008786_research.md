# sources/storage-engines/sqlite/src/shell.c.in lines 1-8173

## Scope

This chunk covers the first half of SQLite's generated command-line shell source template. It starts with platform setup, included extension sources, global shell data structures, result-rendering mode definitions, prompt/input helpers, SQL functions installed by the shell, timer/statistics support, safe-mode authorization, dump/schema helpers, statement execution, parameter binding, database-open type detection, output redirection, archive and recovery helpers, and the opening documentation and parser support for `.import`.

The chunk is application-layer code for the `sqlite3` CLI rather than SQLite pager/B-tree/storage-engine internals. Its storage-engine relevance is indirect but important: it opens and configures database connections, registers shell-only virtual tables and scalar functions, exposes database inspection and dump/recovery flows, runs SQL through prepared statements, renders query results, and drives operational commands such as `.dump`, `.dbinfo`, `.dbtotxt`, `.lint`, `.archive`, `.recover`, `.clone`, and `.intck`.

## Purpose

- Build the portable foundation for the shell binary: compiler feature switches, large-file support, Windows/POSIX shims, line-editing integration, bundled extension inclusion, and global process state.
- Define `ShellState`, `Mode`, `ModeInfo`, `OpenSession`, `ExpertInfo`, `ImportCtx`, and `ArCommand`, which hold nearly all shell runtime state for connections, output modes, sessions, imports, archives, prompts, temporary files, progress/timer settings, and safety flags.
- Provide output wrappers (`cli_printf`, `cli_write`, `cli_puts`, `cli_exit`) that support normal file output plus an in-memory capture mode.
- Implement prompt construction and input-line reading, including readline/editline/linenoise/local `fgets()` paths and rich prompt escapes such as database file, host, user, version, transaction/read-only conditionals, ANSI coloring, date formatting, and continuation guidance.
- Register shell SQL functions used by dot commands and tests: `strtod`, `dtostr`, `shell_add_schema`, `shell_module_schema`, `shell_putsnl`, `shell_format_schema`, `shell_prompt_test`, `shell_temp_filename`, `usleep`, and optionally `edit`.
- Drive SQL execution through `shell_exec()`, including parameter binding, automatic EQP/EXPLAIN output, result formatting through the QRF extension, timers, stats, scanstats, `.expert` integration, and error-context reporting.
- Provide schema/data dump machinery: `dump_callback()`, `run_schema_dump_query()`, `run_table_dump_query()`, rowid preservation logic, virtual-table dump warnings, `sqlite_sequence` handling, corrupt-database retry paths, and formatted schema output.
- Implement helper commands and subsystems for `.dbinfo`, `.dbtotxt`, `.lint fkey-indexes`, `.archive`/`.ar`, `.recover`, `.intck`, `.clone`, safe-mode authorization, statement tracing, progress callbacks, self-tests, temporary-file cleanup, and database type deduction.
- Start the `.import` implementation by defining import context state, CSV/ascii field readers, auto-column naming support, and the user-facing `.import` option contract.

## Important APIs, Types, And Functions

- `ShellState` is the central CLI state object. It stores the active `sqlite3 *db`, current and auxiliary database descriptors, output/input streams, current `Mode`, saved mode stack, prompt strings, open flags, safe-mode flags, temp-file state, timers/progress counters, trace/log streams, current statement handle, session state, `.expert` state, parsed dot-command metadata, and output filename.
- `Mode` and `ModeInfo` model output rendering. `Mode` holds auto-EQP, auto-explain, scanstats, screen-width, flags, `eMode`, and a `sqlite3_qrf_spec`. `aModeInfo[]` maps built-in modes (`ascii`, `box`, `csv`, `insert`, `json`, `line`, `qbox`, `table`, `tabs`, etc.) to separators, NULL/text/blob encodings, headers, QRF style, and columnar behavior.
- `OpenSession` wraps `sqlite3_session` plus a shell name and filter globs when session support is enabled. `session_close()`, `session_close_all()`, and `session_filter()` manage cleanup and table filtering.
- `ExpertInfo` holds an active `sqlite3expert` handle plus verbosity. `expertDotCommand()`, `expertHandleSQL()`, and `expertFinish()` implement `.expert` setup and report generation.
- `ImportCtx` is the import parser state: source file/stream/string, closer, input and field buffers, allocation sizes, current line/row/error counters, terminator, separators, and escape characters. `csv_read_one_field()` and `ascii_read_one_field()` parse CSV/RFC-4180 and raw delimited fields.
- `ArCommand` captures `.archive` options and execution context: command kind, ZIP-vs-SQLAR mode, dry-run/debug/verbose/glob/append flags, source table, file/directory arguments, shell output, and the database handle used by the archive operation.
- `cli_printf()`, `cli_write()`, `cli_puts()`, and `cli_exit()` are the shell's output abstraction. They route stdout/stderr into `cli_output_capture` when active and otherwise write through SQLite stdio wrappers.
- `timeOfDay()`, `beginTimer()`, `endTimer()`, and `elapseTime()` provide wall/CPU timing on POSIX and Windows. The no-timer fallback compiles to no-ops.
- `openChrSource()` safely opens ordinary files, FIFOs, or character sources while avoiding Windows named-pipe stat side effects.
- `local_getline()` reads arbitrarily long lines with heap growth; `one_input_line()` chooses file input or interactive prompt/readline input and handles interrupted false EOFs.
- `expand_prompt()` implements prompt escape expansion and conditionals. `prompt_string()`, `prompt_filename()`, `prompt_hostname()`, `prompt_user()`, and `nAnsiEscape()` are supporting helpers.
- `integerValue()`, `booleanValue()`, `setOrClearFlag()`, `pickStr()`, `optionMatch()`, `hexDigitValue()`, `strlen30()`, and `shellFilenameFromUri()` are general shell parsers.
- `ShellText`, `initText()`, `appendText()`, and `freeText()` provide a small growable string abstraction for generated SQL fragments.
- `quoteChar()` decides whether an identifier needs quoting; `shellFakeSchema()` constructs a fake schema signature for virtual tables or table-valued functions using `PRAGMA table_info`.
- SQL UDFs:
  - `shellStrtod()` and `shellDtostr()` compare SQLite numeric conversion with C library conversion.
  - `shellAddSchemaName()` inserts attached-schema names into `CREATE` SQL and appends fake virtual-table schema comments.
  - `shellExpandPrompt()` exposes prompt expansion to SQL tests.
  - `shellPutsFunc()` prints and returns its argument, used by archive verbose output.
  - `shellFormatSchema()` appends semicolons or pretty-prints table/index schema for `.schema`, `.fullschema`, and `.dump`.
  - `editFunc()` writes a value to a temp file, launches `$VISUAL` or the supplied editor, reads the result back, and returns text/blob content.
  - `shellTempFilenameFunc()` returns a randomized temp filename.
  - `shellUSleepFunc()` calls `sqlite3_sleep()`.
  - `shellModuleSchema()` exposes fake schema comments for eponymous modules.
- `safeModeAuth()` blocks unsafe SQL in safe mode, including `ATTACH` outside Fiddle and functions such as `edit`, `load_extension`, `readfile`, `writefile`, and ZIP/file helpers. `shellAuth()` prints authorizer events and chains safe-mode enforcement when enabled.
- `shell_exec()` is the main SQL execution loop. It prepares one statement at a time, handles `.expert`, formats automatic EQP/EXPLAIN output, binds shell parameters, dispatches `sqlite3_format_query_result()`, prints stats/scanstats, finalizes statements, and returns SQLite result codes plus optional shell-owned error messages.
- `bind_table_init()` creates `temp.sqlite_parameters`; `bind_prepared_stmt()` binds named and numbered parameters from that table plus shell test pseudo-parameters such as `_NAN`, `_INF`, `$int_...`, `$text_...`, `$TIMER`, and optional carray demo bindings.
- `display_stats()` and `displayStatLine()` report global, connection, statement, page-cache, lookaside, temp-spill, scan, VM-step, and Linux `/proc/PID/io` metrics.
- Dump helpers include `printSchemaLine()`, `shell_error_context()`, `save_err_msg()`, `tableColumnList()`, `dump_callback()`, `run_schema_dump_query()`, `run_table_dump_query()`, `toggleSelectOrder()`, `outputDumpWarning()`, and `zAutoColumn()`.
- Database opening/type helpers include `fileSize()`, `isDatabaseFile()`, `deduceDatabaseType()`, `isScriptFile()`, `readFile()`, `readHexDb()`, `open_db()`, and `close_db()`.
- Output and trace helpers include `output_file_open()`, `output_redir()`, `output_reset()`, `sql_trace_callback()`, `shellDeleteFile()`, `clearTempFile()`, and `newTempFile()`.
- Command helpers in this chunk include `showHelp()`, `findUsage()`, `createSelftestTable()`, `tryToCloneData()`, `tryToCloneSchema()`, `tryToClone()`, `shell_dbinfo_command()`, `shell_dbtotxt_command()`, `lintFkeyIndexes()`, `lintDotCommand()`, archive command functions, `recoverDatabaseCmd()`, and `intckDatabaseCmd()`.
- Archive implementation functions include `arParseCommand()`, `arProcessSwitch()`, `arCheckEntries()`, `arWhereClause()`, `arListCommand()`, `arRemoveCommand()`, `arExtractCommand()`, `arCreateOrUpdateCommand()`, and `arDotCommand()`.

## Control Flow

Startup-related flow in this chunk is mostly declarative: platform macros are selected, extension source files are included, global shell flags are defined, and `ShellState`/mode tables establish defaults. Later startup code in the second chunk calls these helpers, but this chunk contains most of the components it will use.

Input flow goes through `one_input_line()` for non-Fiddle builds. If `ShellState.in` is non-null, input is read from that stream with `local_getline()`. Otherwise, the current raw prompt from `prompt_string()` is expanded by `expand_prompt()`, then input is read by local getline, readline/editline, or linenoise. Non-empty interactive lines are added to history when a line-editing backend exists. Ctrl-C increments `seenInterrupt` and interrupts `globalDb`; a second interrupt exits.

Prompt expansion scans the raw prompt string for slash escapes. Plain text is appended unless hidden by an active conditional. Escapes expand to application/version data, database filename variants, hostname, user, date formatting, ANSI escape bytes, continuation-completion text from `sqlite3_incomplete()`, or conditional display branches based on transaction/read-only/memory state. Continuation prompts may align with the main prompt using display width from `sqlite3_qrf_wcswidth()`.

Database opening flows through `open_db()`. It expands `~/`, deduces the open mode when unspecified, supplies read/write/create defaults, opens normal/appendvfs/ZIP/in-memory-deserialize connections, installs `globalDb`, configures scanstatus/trusted-schema/defensive settings, enables extension loading if available, registers bundled extension modules and shell UDFs, creates the `zip` virtual table or deserializes `--deserialize`/`--hexdb` content when requested, then installs safe-mode authorization and current scanstats configuration.

SQL execution in `shell_exec()` loops over a SQL buffer until no statements remain or an error occurs. Each iteration prepares the next statement, skips whitespace/comment-only input, stores `pArg->pStmt`, optionally runs automatic EQP/full EXPLAIN with debug tracing disabled, binds parameters, formats rows using QRF, displays stats/scanstats, finalizes the statement, and advances to the leftover tail. Prepare and step/finalize failures are converted to shell-owned error strings with context from `sqlite3_error_offset()`.

Dump flow starts with schema queries run by `run_schema_dump_query()` using `dump_callback()`. The callback emits special handling for `sqlite_sequence`, `sqlite_stat?`, virtual tables, system tables, and data-only/no-system flags. For ordinary tables, it builds a quoted SELECT column list, switches temporarily into insert mode with SQL text/blob quoting, and calls `shell_exec()` to emit INSERT statements. If corruption appears, schema dump retries in reverse rowid order and table dump toggles `reverse_unordered_selects` to try a second data pass.

Parameter binding flow starts with `.parameter init` in later code calling `bind_table_init()`, which temporarily disables defensive mode and enables writable schema to create `temp.sqlite_parameters` despite the `sqlite_` prefix. `bind_prepared_stmt()` then probes the temp table and binds matching values to every prepared statement parameter before execution; missing parameters become NULL or special test values.

Stats and progress flow is event-driven. `BEGIN_TIMER()` snapshots resource usage and wall clock before operations when timers or timeout progress are active. `progress_handler()` increments counters, optionally interrupts after elapsed timeout or a progress limit, and prints messages unless quiet. `END_TIMER()` prints real/user/sys times and resets one-shot timers. `display_stats()` can be invoked after statements to print connection and statement counters.

Safe-mode control flow uses two layers. Dot-command handlers call `failIfSafeMode()` for shell operations that should not run. SQL statements pass through `safeModeAuth()` when `bSafeModePersist` is active, blocking selected opcodes/functions. `.auth` output uses `shellAuth()` to print all authorizer callbacks and then invokes `safeModeAuth()` if safe mode is also enabled.

Archive flow begins in `arDotCommand()`, which parses tar-style or long/short options into `ArCommand`. It chooses ZIP versus SQLAR behavior from the target file/current open mode, opens a separate database for `--file` when needed, registers file/archive helper functions on that database, validates source table presence, and dispatches to create/update/insert/list/remove/extract/help. Create/update/insert run inside `SAVEPOINT ar`, build SQL against `fsdir()` and SQLAR/zipfile virtual tables, and release or rollback. Extract validates entries, builds a constrained SQL statement that rejects path traversal via `realpath()` and `name NOT GLOB '*..[/\\]*'`, then runs passes for files/directories, symlinks, and directory timestamp restoration.

Recovery and integrity flow uses extension APIs. `.recover` parses options, initializes `sqlite3_recover` with `recoverSqlCb()`, configures lost-and-found table, rowid recovery, freelist handling, and optional debug recovery DB, prints `.dbconfig defensive off`, runs recovery, reports extension errors, and finishes. `.intck` opens `sqlite3_intck`, steps until completion, prints messages, periodically unlocks if requested, reports the final step/error count, and closes.

Import parsing flow in this chunk is preparatory. `csv_read_one_field()` consumes quoted and unquoted CSV fields from `ImportCtx`, handles BOM removal on the first field, configurable quote/unquoted escapes, CRLF row handling, unterminated quotes, and line counting. `ascii_read_one_field()` reads raw byte-delimited fields. The actual `.import` command body continues after this chunk.

## State And Persistence Behavior

Most state is process-local or `ShellState`-local. `ShellState` persists for the shell lifetime and tracks the active DB, auxiliary DBs, stream redirection, current rendering mode, mode stack, temp files, sessions, trace/log state, active statement, timers, progress counters, safe-mode state, and current parsed dot-command arguments.

Persistent database effects include:

- `open_db()` opens or creates database files, may open appendvfs databases, may create in-memory ZIP virtual-table views, may deserialize database bytes into memory, and may set `SQLITE_FCNTL_SIZE_LIMIT`.
- Shell UDF/module registration mutates the connection's function/module namespace.
- `bind_table_init()` creates `temp.sqlite_parameters` and temporarily changes defensive/writable-schema dbconfig settings.
- `.archive` create/update/insert/remove mutates `sqlar` tables or ZIP files, often through a separate connection, and uses savepoints for rollback.
- `.clone` creates a new output database and copies schema/data using INSERT OR IGNORE.
- `.recover` emits SQL recovery text rather than directly creating a database in this code path.
- `.dbtotxt` reads `sqlite_dbpage` pages and writes textual page dumps; `readHexDb()` performs the inverse into a heap buffer later passed to `sqlite3_deserialize()`.
- `.lint fkey-indexes` creates a temporary scalar function `fkey_collate_clause` on the connection and prepares diagnostic EQP statements.
- `.selftest --init` creates and populates the `selftest` table in the main database.
- `edit()` and output redirection create, modify, read, and delete temporary files; `newTempFile()` places temp files under the home directory.

Mode and output state are mutable. `modeChange()`, `modeDefault()`, `modePush()`, and `modePop()` allocate/free separators, width/alignment arrays, table names, null strings, and saved custom modes. `output_redir()` replaces `p->out`, and `output_reset()` closes files/pipes, emits WWW closing HTML, optionally launches `start`/`open`/`xdg-open`, and schedules delayed unlink.

Global process state includes `bail_on_error`, `stdin_is_interactive`, `stdout_is_console`, `stdout_tty_width`, `globalDb`, `globalShellState`, `seenInterrupt`, `Argv0`, optional `iotrace`, `cli_output_capture`, timer globals, debug trace saved flags, and `faultsim_state`. Signal handlers and readline completion depend on these globals.

Memory ownership is mixed. SQLite allocations use `sqlite3_malloc`/`sqlite3_mprintf`/`sqlite3_free`; mode strings and saved arrays often use system `malloc`/`free`/`strdup`; `local_getline()` uses system `realloc`/`free`; `ShellText` uses SQLite allocation. Functions generally document ownership for returned strings and cleanup helpers exist for modes, sessions, columns, import context, temp files, and archive strings.

## Dependencies And Integration Points

- Core dependency is the SQLite C API: connection open/close, prepare/step/finalize, db config, authorizer, trace, status APIs, backup-friendly pragmas, file control, deserialization, statement explain, scanstatus, sessions, carray, and extension initialization.
- The shell relies on included extension sources: stdio wrapper, QRF query-result formatter, memtrace, pcachetrace, SHA1/SHA3, uint, decimal, base64/base85, IEEE754, series, regexp, fileio, completion, appendvfs, zipfile/sqlar, expert, intck, stmtrand, vfstrace, diskused, and optionally recover/dbdata and custom shell extensions.
- `sqlite3_format_query_result()` and `sqlite3_qrf_spec` are central integration points for all output modes. The shell maps legacy `.mode` concepts into QRF style, escaping, quoting, separators, limits, and screen width.
- Line editing integrates with readline/editline/linenoise when present; completion uses the bundled `completion` virtual table against `globalDb`.
- Platform APIs include POSIX `stat`, `gettimeofday`, `getrusage`, `ioctl`, `gethostname`, `unlink`, `popen`/`pclose`, `access`, and Windows `GetSystemTimePreciseAsFileTime`, `GetProcessTimes`, console handlers, UTF-8/UTF-16 conversion, `_stat64`, `_wunlink`, `_waccess`, and file mode controls.
- Safe mode integrates shell-level command checks with SQLite's authorizer callback.
- `.archive` depends on fileio functions (`fsdir`, `writefile`, `realpath`, `lsmode`), SQLAR compression helpers, and the zipfile virtual table.
- `.recover` depends on `sqlite3_recover_*`; `.intck` depends on `sqlite3_intck_*`; `.expert` depends on `sqlite3expert_*`; `.dbinfo` and `.dbtotxt` depend on `sqlite_dbpage`.
- The generated shell template contains placeholders such as `INSERT-USAGE-TEXT-HERE`; the build script fills those when producing final shell source.
- The chunk ends at the `.import` user contract. The command implementation and main command dispatcher continue in the following chunk, so several functions defined here are invoked later.

## Risks And Edge Cases

- `cli_output_capture` captures both stdout and stderr but `cli_exit()` flushes captured text only to stdout. Tests that rely on stream separation may need to account for capture mode.
- `timeOfDay()` on the Win64 precise path adds the Windows epoch offset where conversion typically subtracts it; this should be checked against the surrounding SQLite version because timer/reporting correctness depends on that arithmetic.
- `modeDup()` uses `malloc()`/`strdup()` and does not call `shell_check_oom()` for every duplicated string. Later code may see partially duplicated modes after allocation failure.
- `expand_prompt()` supports nested conditionals via a bitmask. Very deep or malformed prompt conditional nesting can shift bits out of range or leave display suppressed until the end of the prompt.
- `expand_prompt()` appends `UNKNOWN("/x")`-style text for bad escapes even inside inactive branches, by design. Prompt tests should pin this behavior.
- `local_getline()` refuses lines near 1 GiB and returns NULL, which is indistinguishable from EOF to callers.
- `integerValue()` saturates on overflow and supports suffixes, but it treats unmatched suffix text as acceptable once suffix lookup fails. Callers needing strict numeric validation must do their own checks.
- `editFunc()` constructs the editor command as `%s "%s"` and invokes `system()`. A hostile editor string or temp filename environment could be unsafe; safe mode blocks `edit()`.
- `safeModeAuth()` only prohibits a fixed list of functions and selected opcodes. New file/network-affecting functions registered by extensions need explicit coverage or external controls.
- `shellFormatSchema()` is a SQL text formatter, not a full parser. Complex quoting/comments/triggers/views are intentionally bypassed or best-effort.
- `shell_exec()` temporarily changes statement explain mode and trigger EQP settings. Any new early-return path in that block must restore debug trace modes, trigger EQP, statement explain, and timer state.
- `bind_prepared_stmt()` calls `sqlite3_bind_text(pQ,...)` even when `pQ` is NULL if the parameters table is absent. The SQLite API tolerates NULL statement pointers poorly; in practice this branch relies on `pQ` being checked by later conditions but the bind/reset calls are a sharp edge.
- Parameter pseudo-bindings (`$int_`, `$text_`, `$carray_`) are test conveniences that can affect ordinary SQL if users accidentally choose matching parameter names.
- Dump logic for virtual tables writes directly to `sqlite_schema` under `PRAGMA writable_schema=ON`; generated scripts require defensive mode off, and `outputDumpWarning()` exists to warn about this.
- Rowid preservation in `tableColumnList()` is necessarily heuristic around INTEGER PRIMARY KEY, WITHOUT ROWID, `rowid` aliases, and hidden/inaccessible rowids.
- Corruption retry paths intentionally continue after certain failures and may emit partial dumps with error comments; automation should inspect `p->nErr`.
- `readFile()` uses `long ftell()` and reads the whole file at once; very large files or non-seekable streams fail.
- `readHexDb()` parses page offsets and hex bytes from text and silently ignores lines outside bounds; malformed but partially valid input can produce a zero-filled or partial database image before error detection.
- `deduceDatabaseType()` reads fixed trailers for appendvfs and ZIP. Small, unusual, or non-seekable files may fall back by filename/default rather than content.
- `output_file_open()` returns NULL for `"off"` and for any output file in safe mode; callers must handle a NULL output stream.
- `output_reset()` schedules delayed deletion after launching an external opener. The temporary file may be deleted too soon or left behind depending on platform behavior and process lifetime.
- `csv_read_one_field()` permits configurable escape behavior but reports some quote errors while continuing. Import callers must decide how many parse errors are acceptable.
- `.archive` extraction includes path traversal defenses, but it depends on SQL `realpath()` and name filtering. Symlinks and platform-specific path normalization remain sensitive.
- `arWhereClause()` builds SQL text from command arguments using `%q` but produces potentially large WHERE clauses for many archive members.
- `arRemoveCommand()` prints SQL errors to stdout with a comment questioning that choice; scripts expecting errors on stderr may be surprised.
- `zAutoColumn()` opens a transient SQLite database solely to generate unique column names. It asserts on unexpected rc values and may exit on OOM; duplicate-name behavior changes under `SHELL_COLUMN_RENAME_CLEAN`.
- `faultsim_callback()` uses global mutable state and stdout diagnostics, so it is unsuitable for concurrent shell executions inside one process.

## Test Signals

- Build matrix should cover POSIX, Windows, Fiddle, readline/editline/linenoise/no-lineedit, zlib/no-zlib, session/no-session, expert/no-expert, recover/no-recover, deserialize/no-deserialize, debug/test-control, and safe-mode builds.
- Prompt tests should use `shell_prompt_test()` for default prompts, environment overrides, `/f`/`/F`/`/~`, host/user/version/date escapes, transaction/read-only/memory conditionals, `/C` continuation completions, `/B` alignment, ANSI delimiter flags, unknown escapes, and `NO_COLOR`.
- Input tests should cover long lines, CRLF stripping, interrupted readline/local-getline behavior, file streams versus interactive stdin, and history addition under line-editing backends.
- Mode tests should cover every built-in mode's separators, NULL/text/blob quoting, headers, auto screen width, mode push/pop, saved custom modes, `.crlf` on Windows, and allocation cleanup on repeated mode changes.
- SQL execution tests should cover multi-statement input, comment-only statements, prepare/step/finalize errors with `sqlite3_error_offset()`, automatic EQP modes, EXPLAIN formatting, `.www`, stats, scanstats modes, timer once/on/off, and restoration after EQP failures.
- Parameter tests should cover `temp.sqlite_parameters`, anonymous `?N` names, missing values becoming NULL, `$int_`, `$text_`, `$TIMER`, `_NAN`, `_INF`, and optional carray bindings with and without unsafe testing.
- Safe-mode tests should cover blocked `ATTACH`, `edit()`, `load_extension()`, `readfile()`, `writefile()`, `zipfile()` functions, allowed harmless SQL, `.auth` output interaction, and Fiddle's ATTACH exception.
- Dump/schema tests should cover ordinary tables, virtual tables, FTS shadow tables, `sqlite_sequence`, `sqlite_stat?`, `--data-only`, `--nosys`, `--preserve-rowids`, comments without terminators, `--indent`, corrupt database retries, generated defensive-mode warnings, and rowid alias edge cases.
- Database open tests should cover normal DBs, empty/missing `.zip`, appendvfs trailer files, `--deserialize`, `--hexdb`, `--maxsize`, `~/` expansion, read-only/read-write/create flags, nofollow flags, failed open with keepalive, and substitute in-memory fallback.
- UDF tests should cover `strtod`, `dtostr` precision bounds, `shell_add_schema` for all CREATE forms, virtual-table fake schema comments, `shell_format_schema`, `shell_temp_filename`, `usleep`, and `edit()` text/blob CRLF behavior when system calls are enabled.
- `.dbinfo` and `.dbtotxt` tests should validate page-header decoding, attached schema names, invalid page sizes, empty DB handling, `sqlite_dbpage` availability, and round-tripping `dbtotxt` through `--hexdb`.
- `.lint fkey-indexes` tests should cover single/composite foreign keys, collation mismatches, existing covering indexes, INTEGER PRIMARY KEY plans, verbose output, grouping by parent, malformed schemas, and prepare/finalize errors.
- `.archive` tests should cover tar-style and long-option parsing, ambiguous options, create/insert/update/list/remove/extract, SQLAR versus ZIP, `--file`, `--append`, `--directory`, `--glob`, `--dryrun`, `--debug`, missing archive members, recursive directories, symlinks, mtime restoration, path traversal rejection, and rollback on errors.
- `.recover` tests should cover lost-and-found naming, rowid/no-rowid output, freelist handling, safe-mode suppression of debug recovery DB, extension error reporting, and SQL callback semicolon output.
- `.intck` tests should cover clean DBs, detected errors, unlock cadence, open/step/error API failures, and final step/error counts.
- Import parser tests should cover BOM stripping, quoted fields, doubled quotes, custom quote/unquoted escapes, CRLF and bare LF rows, custom separators, unterminated quotes, unescaped quote diagnostics, EOF handling, interrupt handling, ascii-mode separators, and duplicate/blank column auto-renaming through `zAutoColumn()`.
