# sources/storage-engines/wiredtiger/test/3rdparty/sqlite3/shell.c lines 25465-33482

## Scope and Purpose

This chunk is the operational core of SQLite's command-line shell as vendored under WiredTiger's SQLite test dependency. It starts in the static help text for dot commands, then defines helpers for opening databases, reading input files, importing delimited data, archive handling, recovery/introspection commands, output redirection, schema/dump utilities, and the large `do_meta_command()` dispatcher. It then covers SQL-line scanning and execution, startup rc-file processing, command-line option help, shell-state initialization, and the first pass of `main()` option parsing up to `-unsafe-testing`.

The code is not WiredTiger storage-engine logic directly. Its purpose in this tree is to provide the SQLite shell binary used by tests and tooling. The main integration surface is SQLite's public C API plus shell-only extensions such as `fileio`, `zipfile`, `sqlar`, `completion`, `dbpage`, recovery, sessions, and testing controls.

## Important APIs, Types, and Functions

- `showHelp(FILE *out, const char *zPattern)` searches the `azHelp[]` command documentation. It supports summary output, all documented commands, undocumented comma-prefixed commands, prefix matching, and LIKE matching.
- `readFile()`, `deduceDatabaseType()`, `readHexDb()`, `open_db()`, and `close_db()` handle file loading and database connection lifecycle. `open_db()` recognizes normal DB files, appendvfs payloads, zip archives, readonly opens, `--deserialize`, and `--hexdb`, then registers shell SQL functions and virtual-table extensions.
- Session helpers under `SQLITE_ENABLE_SESSION` (`session_close()`, `session_close_all()`, `session_filter()`) manage `OpenSession` arrays stored per auxiliary DB connection.
- Input/output helpers include `resolve_backslashes()`, `booleanValue()`, `setOrClearFlag()`, `output_file_open()`, `output_file_close()`, `output_redir()`, and `output_reset()`. These mutate `ShellState` fields such as separators, output streams, temporary files, trace streams, and safe-mode state.
- `sql_trace_callback()` bridges `.trace` to `sqlite3_trace_v2()`, producing plain, expanded, normalized, row, profile, and close traces depending on shell state.
- `ImportCtx`, `csv_read_one_field()`, and `ascii_read_one_field()` implement `.import` field parsing. CSV handling supports RFC4180-style quotes, UTF-8 BOM skipping, custom single-byte separators, line counting, and error messages for unterminated or unescaped quotes.
- Clone and dump helpers (`tryToCloneData()`, `tryToCloneSchema()`, `tryToClone()`, `outputDumpWarning()`) move schema/data or warn when dumps require defensive mode to be disabled.
- Archive support under `!SQLITE_OMIT_VIRTUALTABLE && SQLITE_HAVE_ZLIB` defines `ArCommand` and the `.archive`/`.ar` implementation: `arParseCommand()`, `arCheckEntries()`, `arWhereClause()`, `arListCommand()`, `arRemoveCommand()`, `arExtractCommand()`, `arCreateOrUpdateCommand()`, and `arDotCommand()`.
- Recovery and integrity helpers include `shell_dbinfo_command()`, `shell_dbtotxt_command()`, `recoverDatabaseCmd()`, and `intckDatabaseCmd()`. They use `sqlite_dbpage`, page-header parsing, `sqlite3_recover_*`, and `sqlite3_intck_*`.
- `.lint fkey-indexes` is implemented by `shellFkeyCollateClause()`, `lintFkeyIndexes()`, and `lintDotCommand()`, using PRAGMA table/foreign-key metadata and `EXPLAIN QUERY PLAN`.
- `zAutoColumn()` uses a transient SQLite database to generate duplicate-safe column definitions when `.import` creates a table from header rows.
- `faultsim_state` and `faultsim_callback()` back the `.testctrl fault_install` test hook.
- `do_meta_command()` is the central dot-command dispatcher. It tokenizes a line into up to 51 arguments, resolves quoted/backslash escapes, finishes active expert sessions, resets temporary output, then dispatches by first character and prefix.
- SQL-input helpers `quickscan()`, `line_is_command_terminator()`, `line_is_complete()`, `doAutoDetectRestore()`, `runOneSqlLine()`, `echo_group_input()`, and `process_input()` classify multi-line SQL, detect dot commands, execute SQL, and process nested `.read` input.
- Startup helpers `find_home_dir()`, `find_xdg_config()`, `process_sqliterc()`, `usage()`, `verify_uninitialized()`, `main_init()`, `printBold()`, `cmdline_option_value()`, `sayAbnormalExit()`, and `vfstraceOut()` support process setup and option handling.

## Dot-Command Control Flow

`do_meta_command()` is an ordered `if`/`else` chain, not a registration table. Command matching uses first character plus `cli_strncmp()` prefix checks, so ordering and minimum prefix lengths matter. The dispatcher returns `0` for success, `1` for error, and `2` for requested shell exit.

Major command families in this chunk include:

- Database and file lifecycle: `.open`, `.backup`, `.save`, `.restore`, `.clone`, `.databases`, `.dbconfig`, `.dbinfo`, `.dbtotxt`, `.filectrl`, `.vfsinfo`, `.vfslist`, `.vfsname`, `.timeout`.
- Input/output and presentation: `.mode`, `.headers`, `.separator`, `.nullvalue`, `.width`, `.output`, `.once`, `.excel`, `.www`, `.print`, `.prompt`, `.show`, `.stats`, `.timer`, `.trace`, `.log`.
- Schema and diagnostics: `.schema`, `.fullschema`, `.dump`, `.tables`, `.indexes`/`.indices`, `.lint fkey-indexes`, `.selftest`, `.sha3sum`, `.scanstats`.
- Data movement and format commands: `.import`, `.archive`/`.ar`, `.read`, `.recover`, `.intck`.
- Test and debug commands: `.imposter`, `.testctrl`, `.selecttrace`, `.treetrace`, `.wheretrace`, `.breakpoint`, `.auth`, `.iotrace`, `.unmodule`, internal `.selftest-*`.
- Potentially unsafe host operations: `.cd`, `.shell`/`.system`, `.load`, output pipes, archive file writes, session changeset writes, and disk-backed `.open`. These call `failIfSafeMode()` or check `p->bSafeMode`.

Most commands call `open_db(p, 0)` lazily only when they need a live SQLite connection. Commands that switch databases close sessions first, close the current handle, reset `p->pAuxDb` filename ownership, and reopen with the selected mode. Commands that write external files usually use `sqlite3_fopen()`, `sqlite3_popen()`, `writefile()`, SQLite backup APIs, or virtual tables.

## SQL Input and Execution Flow

`process_input()` owns the shell read/evaluate loop. It prevents recursive `.read` overflow with `MAX_INPUT_NESTING`, reads lines through `one_input_line()`, tracks `p->lineno`, and uses `quickscan()` to maintain a resumable state for strings, quoted identifiers, bracket identifiers, C comments, parentheses, and semicolon termination.

Single-line `.` commands and `#` comments are handled only when no SQL is accumulated. SQL Server-style `go` and Oracle-style `/` terminators are accepted if the scanner is in plain state and `sqlite3_complete()` agrees. Complete SQL is executed by `runOneSqlLine()`, which opens the DB, optionally resolves backslash escapes, resets progress counters, times execution, calls `shell_exec()`, reports parse/runtime errors with line numbers, prints `.changes` output, and calls `doAutoDetectRestore()`.

`doAutoDetectRestore()` recognizes the first two statements of a `.dump` restore into an empty database (`PRAGMA foreign_keys=OFF;` then `BEGIN TRANSACTION;`). Outside safe mode, it temporarily disables defensive mode and enables DQS DDL during the restore transaction, then restores prior `SQLITE_DBCONFIG_DEFENSIVE` and `SQLITE_DBCONFIG_DQS_DDL` when autocommit returns.

## State and Persistence Behavior

The central mutable state is `ShellState`. This chunk updates database handles, auxiliary connection slots, filenames and owned filename buffers, output streams, output mode, separators, width arrays, prompts, trace output, stats/scanstats/progress settings, safe-mode flags, restore detection state, temporary-file state, sessions, and test counters.

Persistent effects include:

- `.open`, `.backup`, `.save`, `.restore`, `.clone`, `.archive`, `.import`, `.dump` playback, `.read`, `.load`, `.session changeset/patchset`, `.output`, `.once`, `.excel`, `.www`, `.log`, `.shell`, and `.system` can read/write files or run host commands when not blocked by safe mode.
- `.parameter` persists bindings in `temp.sqlite_parameters`, scoped to the current SQLite connection.
- `.import` may create a new table using header-derived column names and then insert rows inside an implicit transaction if autocommit was active.
- `.archive` stores SQLAR rows in `sqlar` or manipulates zipfile virtual tables. Create/update/insert/remove operations are wrapped in a savepoint.
- `.session` stores in-memory session objects per aux DB and can write binary changeset or patchset files.
- `.dump` and `.recover` emit SQL scripts to the current output stream, not directly to a target DB.
- `.sqliterc` processing reads `$XDG_CONFIG_HOME/sqlite3/sqliterc`, `~/.config/sqlite3/sqliterc`, `~/.sqliterc`, or an override file, temporarily replacing `p->in`.
- `main_init()` configures SQLite logging, URI support, multithread mode, default prompts, default list mode, default separators, and shell flags before later option parsing opens a database.

Temporary state has several cleanup paths: output redirection closes files/pipes in `output_reset()`, `clearTempFile()` deletes temp output when no external opener is pending, import cleanup closes input and frees buffers, archive commands close separate DB handles, and `process_input()` frees accumulated SQL and line buffers.

## Dependencies and Integration Points

- SQLite public API: connection open/close, prepare/step/finalize/reset, backup, PRAGMA queries, `sqlite3_db_config()`, `sqlite3_file_control()`, limits, busy timeout, progress handler, trace v2, authorizer, table metadata, deserialize, config, VFS enumeration, test controls, and extension loading.
- SQLite shell extension entry points registered in `open_db()`: SHA/SHA3, uint, random, decimal, percentile, base64/base85, regexp, ieee754, series, fileio, completion, zipfile, sqlar, and optional custom `SQLITE_SHELL_EXTFUNCS`.
- Optional compile-time features: `SQLITE_ENABLE_SESSION`, `SQLITE_HAVE_ZLIB`, `SQLITE_SHELL_HAVE_RECOVER`, `SQLITE_OMIT_DESERIALIZE`, `SQLITE_OMIT_LOAD_EXTENSION`, `SQLITE_OMIT_VIRTUALTABLE`, `SQLITE_OMIT_PROGRESS_CALLBACK`, `SQLITE_ENABLE_IOTRACE`, `SQLITE_ENABLE_STMT_SCANSTATUS`, `SQLITE_ENABLE_NORMALIZE`, `SQLITE_DEBUG`, `SQLITE_SHELL_FIDDLE`, Windows UTF-16 `wmain`, readline/editline/linenoise completion, and platform VFS/system APIs.
- Host OS APIs: `access()`, `unlink()`/`_wunlink`, `chdir()`/`SetCurrentDirectoryW`, `system()`, `popen()`/`pclose()`, `isatty()`, `getpwuid()`, environment variables, signals or Windows console control handlers.
- SQL virtual tables and functions expected by commands: `sqlite_dbpage`, `fsdir`, `writefile`, `sqlar_compress`, `sqlar_uncompress`, `zipfile`, `completion`, `pragma_*` table-valued functions, `sha3_query`, and shell helper SQL functions such as `shell_add_schema`, `shell_module_schema`, and `shell_putsnl`.

## Risks and Edge Cases

- Command dispatch is prefix-based and order-sensitive. Adding a command can unintentionally change abbreviation behavior or collide with existing prefixes.
- `do_meta_command()` mutates the input line in place while tokenizing. Callers must pass writable buffers, and quoted-argument parsing only handles backslash escapes inside double quotes.
- Several SQL strings are assembled dynamically. Most object names use `%w`/quoting helpers, but archive WHERE clauses interpolate member names as SQL literals and rely on `%q`; future edits must preserve correct quoting.
- `.import` supports only single-byte row and column separators. Multi-character separators are explicitly rejected, and CSV parsing depends on `p->mode` unless `--csv` or `--ascii` is supplied.
- `.import` returns immediately if the target has zero columns without running shared cleanup in that local branch; changes around this path must be careful not to leak or skip diagnostics.
- Safe mode is reset at `meta_command_exit`, but `.nonce` returns early to keep safe mode disabled for the next command. This is intentional and sensitive security behavior.
- External command and pipe construction quotes arguments only by wrapping words containing spaces. It is not a general shell-escaping library, so safe mode must remain the main mitigation for untrusted input.
- `deduceDatabaseType()` seeks near EOF to detect appendvfs and zip files. Very small or non-seekable files fall through based on `fread()`/`fseek()` results; callers should not assume strong validation.
- `readFile()` uses `ftell()` into `long` and then allocates `nIn+1`; it is intended for shell-sized files, not arbitrary huge inputs.
- `.archive` extraction explicitly filters names containing `..` path components with `name NOT GLOB '*..[/\\]*'`, but any change to extraction SQL must preserve traversal protections.
- `.dump`/restore auto-detection toggles defensive/DQS modes based on exact first statements. Formatting or comments before restore scripts disable this convenience path.
- Many sections are conditional. Builds without zlib, virtual tables, recovery, session, loadable extensions, trace, or test controls have materially different command availability and test surface.
- The chunk ends while `main()` is still in its first option-parse pass, so later startup behavior, second-pass option handling, command execution, shutdown, and cleanup must be reconciled from the next chunk.

## Test Signals

- Build the shell with representative feature matrices: default, `SQLITE_HAVE_ZLIB`, `SQLITE_ENABLE_SESSION`, `SQLITE_SHELL_HAVE_RECOVER`, `SQLITE_DEBUG`, and omission flags for load-extension/progress/deserialize/virtual-table paths.
- Exercise `.help` with no pattern, `--all`, `0`, exact prefixes, ambiguous prefixes, and LIKE text matches to catch help-table or prefix-dispatch regressions.
- Run shell command tests for `.open` modes: normal, readonly, appendvfs, zip, deserialize, hexdb, nofollow, failed-open keepalive, and safe-mode disk-file rejection.
- Validate `.import` with CSV quotes, embedded separators/newlines, BOM input, `--skip`, `--schema`, auto-created tables with duplicate/empty headers, ASCII separators, too few fields, too many fields, and interrupt handling.
- Test `.archive` create/list/extract/update/insert/remove for SQLAR and zipfile sources, including `--dryrun`, `--glob`, `--directory`, `--append`, missing entries, changed-file detection, and path traversal attempts.
- Test `.backup`, `.restore`, `.dump`, `.recover`, `.dbinfo`, `.dbtotxt`/`--hexdb`, `.intck`, `.sha3sum`, `.lint fkey-indexes`, `.schema --indent/--nosys`, and `.fullschema` against normal, empty, corrupt, attached, and virtual-table databases.
- Verify `.parameter` binds SQL literals and fallback text values, persists in `temp.sqlite_parameters`, and is applied by later SQL execution.
- Check safe-mode denials for `.cd`, `.shell`, `.system`, `.load`, `.archive`, `.backup`, `.restore`, `.read`, `.import`, disk `.open`, output pipes/files, and session file output, plus `.nonce` behavior.
- Exercise `process_input()` with multi-line strings, bracket/backtick/double/single quotes, C comments, trailing semicolons, `go`, `/`, blank lines, `#` comments, nested `.read`, `bail_on_error`, interrupts, `.once` cleanup, and echo mode.
- On startup, verify rc-file discovery order, `-batch` suppressing interactive rc messages, missing `-init` behavior under bail, Windows UTF-16 argument conversion where applicable, early SQLite config options, and signal/interrupt exit reporting.

## Cross-Chunk Notes

This chunk starts inside `azHelp[]` and ends inside the first `main()` command-line option pass immediately after handling `-unsafe-testing`. The final merged research for `shell.c` should combine this with adjacent chunks for the earlier `ShellState` definitions, output callbacks, safe-mode helpers, extension implementations, `shell_exec()`, and the rest of `main()` including second-pass option handling, stdin/command execution, shutdown, and memory cleanup.
