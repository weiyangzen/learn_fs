# sources/storage-engines/wiredtiger/test/3rdparty/sqlite3/shell.c lines 33483-34019

## Scope

This chunk covers the final portion of the SQLite command-line shell entrypoint and the optional `SQLITE_SHELL_FIDDLE` export surface. It starts in the first-pass command-line option scanner, immediately after handling `-unsafe-testing`, `-safe`, and `-escape`, then completes:

- SQLite initialization and optional VFS registration.
- Default database filename selection and delayed open behavior.
- `.sqliterc` processing and the second command-line option pass.
- Execution of `-cmd` input, positional SQL/dot-command arguments, or stdin.
- Interactive history setup and teardown.
- Normal native-shell cleanup.
- WASM/Fiddle helper functions that expose the live shell database to JavaScript/emscripten callers.

The adjacent setup before this chunk defines `main_init()`, `ShellState`, `open_db()`, `process_input()`, `globalDb`, and the `SQLITE_SHELL_FIDDLE` remapping of `main` to `fiddle_main`; this chunk is where those pieces are wired into the process lifecycle.

## Purpose

The native portion of this range is the shell's final startup and dispatch coordinator. It waits until all pre-initialization `sqlite3_config()` options have been processed, initializes SQLite, applies user-visible command-line settings after the init file, runs commands from the selected input source, and releases shell-owned resources before returning an exit code.

The Fiddle portion turns the same shell machinery into a persistent WASM-hosted service. In that build, `main` is compiled as `fiddle_main`, the global `shellState` remains alive after `fiddle_main()` returns, and exported helpers let browser-side code inspect, interrupt, reset, export, or feed SQL into the existing database.

## Important APIs, Types, and Functions

- `ShellState data` / `shellState`: the central mutable shell state. In native builds it is stack-local to `main`; in Fiddle builds `data` is a macro alias for static global `shellState`, which is intentionally not cleared at exit.
- `sqlite3_initialize()`: called after the first pass has completed all pre-initialization `sqlite3_config()` calls. If `SQLITE_SHELL_INIT_PROC` is defined, that external hook replaces the direct initialization call and can perform embedding-specific setup.
- `sqlite3_vfs_find()` and `sqlite3_vfs_register()`: implement `-vfs NAME` by locating and promoting the requested VFS after SQLite initialization.
- `open_db(&data, flags)`: lazily opens the active database according to `data.openMode`, `data.openFlags`, and `data.pAuxDb->zDbFilename`. In this chunk it is called for existing files, command SQL, archive mode, and positional SQL execution.
- `process_sqliterc(&data, zInitFile)`: applies `-init FILE` or default rc-file configuration before the second argument pass so explicit command-line options override rc-file settings.
- `do_meta_command()` and `shell_exec()`: dispatch dot-commands and SQL from `-cmd` arguments or positional command arguments.
- `process_input(&data)`: processes interactive or batch stdin. For Fiddle, it also consumes `shellState.wasm.zInput` through the alternate WASM input-line implementation.
- `shell_read_history()`, `shell_write_history()`, and `shell_stifle_history()`: manage interactive history, using `$SQLITE_HISTORY` or `$HOME/.sqlite_history`.
- `session_close_all()`, `close_db()`, `output_reset()`, `clearTempFile()`, and `find_home_dir(1)`: native cleanup hooks for sessions, database handles, output redirection, temporary files, and cached home-directory state.
- Fiddle exports:
  - `fiddle_experiment(int,int)`: trivial exported function used for emscripten experiments.
  - `fiddle_db_handle()`: returns `globalDb`.
  - `fiddle_db_vfs(const char*)`: returns the VFS for the named database using `SQLITE_FCNTL_VFS_POINTER`.
  - `fiddle_db_arg(sqlite3*)`: logs and returns a database pointer, also experimental.
  - `fiddle_interrupt()`: calls `sqlite3_interrupt(globalDb)`.
  - `fiddle_db_filename(const char*)`: returns `sqlite3_db_filename()` for the requested database name.
  - `fiddle_reset_db()`: rolls back active transactions, enables `SQLITE_DBCONFIG_RESET_DATABASE`, runs `VACUUM`, and disables reset mode.
  - `fiddle_export_db()`: streams the main database file through the VFS `xRead` method into a callback.
  - `fiddle_exec(const char*)`: feeds SQL or a dot-command string into `process_input(&shellState)`.

## Control Flow

After the first command-line pass, native builds verify that SQLite has not been initialized too early, unless VFS tracing was enabled. The code then either calls `SQLITE_SHELL_INIT_PROC()` or `sqlite3_initialize()`. If `-vfs` was supplied, the named VFS is looked up and registered as default; failure is fatal with exit status 1.

If no database filename was found, the shell defaults to `:memory:` unless memory databases are omitted. With `SQLITE_OMIT_MEMORYDB`, no filename is a hard error. Output defaults to `stdout`, optional VFS tracing is registered, and native builds initialize appendvfs support.

The shell deliberately opens the database early only when the named file already exists. Otherwise creation is delayed until SQL or a dot-command needs the database. This avoids creating an empty file for a mistyped database name when the user only wanted to inspect options or run non-database commands.

The init file is processed before the second option pass. The second pass applies presentation and behavior settings such as output mode (`-html`, `-list`, `-quote`, `-line`, `-column`, `-json`, `-markdown`, `-table`, `-box`, `-csv`, `-ascii`, `-tabs`), separators, null display, headers, echo, automatic EQP, stats, scanstats, backslash decoding, open modes, safe mode, and interactive override. Options that were fully handled during the first pass are skipped by advancing `i` over their operands.

`-cmd ARG` executes during this second pass before positional commands. Dot-command strings go to `do_meta_command()`. SQL strings force a database open and go to `shell_exec()`. With `-bail`, command failures return immediately; otherwise errors are emitted and processing can continue.

When archive shorthand `-A...` is enabled, the shell rejects a mix of archive mode with regular positional commands, opens the database with `OPEN_DB_ZIPFILE`, forwards the remaining argv slice to `arDotCommand()`, disables stdin, and leaves the option loop.

After option processing, `readStdin` selects the execution lane:

- If false, each collected positional command is echoed as group input, dispatched as a dot-command or SQL, and aborts through `shell_main_exit` on any error.
- If true and interactive, the shell prints version/help text, optionally warns about a transient in-memory database, loads history, installs readline/editline/linenoise completion callbacks, sets `data.in = 0`, and calls `process_input()`.
- If true and non-interactive, it sets `data.in = stdin` and calls `process_input()`.

Native cleanup runs after input processing and also via the `shell_main_exit` label used by command errors. It finishes any active expert session, frees command storage, clears destination table state, closes the primary and auxiliary database handles with session cleanup, resets output state, removes temp files, frees Windows UTF-8 argv copies, column widths, and the nonce, then zeroes `data` to make leak detection stricter. Fiddle builds skip this cleanup so the browser binding can continue using `shellState` and `globalDb` after `fiddle_main()` returns.

## State and Persistence Behavior

The main persistent state in native builds is external: the database file, `.sqlite_history`, output files, temporary files, and any side effects of executed SQL or dot-commands. `ShellState` itself is process-local and is explicitly cleared before return in native builds. The database is not necessarily opened during startup; delayed open is used for nonexistent filenames.

The second pass intentionally overwrites rc-file defaults. For example, `.sqliterc` may set output modes or headers, but command-line flags in this chunk update `data.mode`, separators, `showHeader`, `statsOn`, `scanstatsOn`, and other fields afterward. `data.cMode` is synchronized to `data.mode` after each recognized option.

Safe mode persists through `data.bSafeModePersist` and is restored by `process_input()` after each complete SQL statement. In this chunk, `-safe` sets both the current and persistent safe-mode flags. Later `open_db()` uses that persistent flag to install the safe-mode authorizer and withhold zip/sqlar extension registration.

Fiddle builds have intentionally persistent in-memory/global process state: `shellState`, `globalDb`, and `shellState.wasm` survive across calls. `fiddle_exec()` temporarily sets `shellState.wasm.zInput` and `zPos`, processes input, and clears those pointers afterward. `fiddle_reset_db()` mutates the open database in place, keeping storage but deleting content through SQLite's reset-database protocol.

`fiddle_export_db()` persists nothing itself. It reads the current main database file directly through the underlying VFS file object and streams bytes to a caller callback. The buffer size starts at 8192 bytes and is reduced to 4096, 2048, 1024, or 512 if needed so callback chunks better match the file size.

## Dependencies and Integration Points

This chunk sits at the boundary between command-line parsing, SQLite core initialization, shell extension registration, interactive console support, and optional browser/WASM embedding.

Compile-time dependencies shape visible behavior:

- `SQLITE_SHELL_INIT_PROC` and `SQLITE_SHELL_DBNAME_PROC` are embedding hooks around initialization and database naming.
- `SQLITE_SHELL_FIDDLE` changes `main` into `fiddle_main`, uses global shell state, disables normal cleanup, and enables the exported `fiddle_*` functions.
- `SQLITE_OMIT_MEMORYDB`, `SQLITE_HAVE_ZLIB`, `SQLITE_OMIT_DESERIALIZE`, `SQLITE_ENABLE_MULTIPLEX`, `SQLITE_ENABLE_SORTER_REFERENCES`, `SQLITE_OMIT_VIRTUALTABLE`, readline/editline/linenoise macros, Windows UTF-8 conversion macros, and `SQLITE_DEBUG` all gate pieces of startup, option handling, command dispatch, or teardown.

Runtime dependencies include process environment variables and filesystem APIs: `access()` for delayed open decisions, `getenv("SQLITE_HISTORY")`, home-directory discovery for history, terminal detection from earlier setup, and VFS/file-control calls for selected VFS, Fiddle VFS lookup, and Fiddle export.

Within WiredTiger's vendored SQLite copy, this source is third-party test infrastructure. The code is not a WiredTiger storage-engine implementation path; it provides the SQLite shell used by the vendored SQLite test/tooling environment. Integration risk for WiredTiger is therefore mostly build compatibility, test behavior, and CLI utility semantics rather than runtime database engine behavior.

## Risks and Edge Cases

- Option parsing is split across two passes. Any option with operands must be skipped consistently in both passes; otherwise later options or positional commands can be misinterpreted. This chunk contains explicit skip logic for options configured earlier.
- `-nonce` is advanced by two positions in the second pass even though the first pass consumes one operand. That matches surrounding shell semantics but is easy to break if option arity changes.
- `-cmd` preserves historical ordering where all `-cmd` commands run before positional command arguments, even if argv order suggests otherwise. Tests may depend on this compatibility quirk.
- Unknown `-escape` modes print valid choices and exit immediately. This is fatal rather than routed through normal `shell_main_exit`, so resource ownership is minimal at that point but any future allocations before it would need care.
- Delayed open avoids accidental file creation, but options or dot-commands that call `open_db()` can still create the file later.
- `-A` archive mode takes over the remaining argument vector. Mixing it with collected regular commands is rejected, and `readStdin` is disabled after dispatch.
- Native cleanup is skipped in Fiddle builds by design. That preserves browser-visible DB state, but also means native leak-check assumptions do not apply to Fiddle.
- Fiddle exports expose raw `sqlite3*` and VFS/file pointers to the embedding boundary. Callers must respect lifetime and threading constraints.
- `fiddle_reset_db()` rolls back all active transactions before reset. If repeated rollback does not reduce `sqlite3_txn_state()`, the loop would continue; it relies on SQLite rollback behavior succeeding.
- `fiddle_export_db()` is explicitly not thread-friendly and reads through the VFS without coordinating with concurrent writers. It also calls the callback with a fixed `nBuf` for each iteration, so callers should treat the callback contract as chunk-oriented shell export behavior, not a general safe concurrent snapshot API.
- `fiddle_exec()` assumes `fiddle_main()` has already initialized `shellState`; otherwise its comments state behavior is undefined.

## Test Signals

Useful behavioral tests for this chunk include:

- CLI startup with no filename uses `:memory:` and interactive mode emits the transient database warning when no other arguments are supplied.
- A nonexistent filename is not created by startup alone, but is created once SQL requiring `open_db()` runs.
- `-init` settings are overridden by later command-line output-mode, separator, header, stats, and safe-mode flags.
- `-vfs` accepts an existing VFS name and rejects an unknown VFS with `no such VFS`.
- `-escape ascii|symbol|off` updates output escaping, while an invalid value exits and lists choices.
- `-cmd` dot-commands and SQL run before positional commands; with `-bail`, failures abort with a nonzero status.
- `-A` archive shorthand rejects mixing with positional SQL/dot-commands and forwards the remaining argv slice to archive handling.
- Batch stdin and interactive stdin both route through `process_input()`, with only interactive mode loading/saving history and installing completion callbacks.
- Native builds close all opened primary and auxiliary databases, clear temporary output state, and zero `ShellState` before return.
- Fiddle builds keep `shellState` alive after `fiddle_main()`, allow `fiddle_exec()` to process additional SQL, allow `fiddle_interrupt()` to interrupt the live DB, allow `fiddle_reset_db()` to clear contents, and allow `fiddle_export_db()` to stream the main database bytes through a callback.
