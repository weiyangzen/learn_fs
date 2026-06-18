# subset-b-008813 Research

This grouped report covers the requested SQLite test and tool files. Each section is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/test/vt02.c -->
# sources/storage-engines/sqlite/test/vt02.c

## Purpose
`vt02.c` implements the `vt02` eponymous read-only virtual table used by SQLite and TH3 tests. It synthesizes 10,000 rows where `x` runs from 0 through 9999 and `a`, `b`, `c`, and `d` expose decimal digits of `x`. The file exists to exercise SQLite virtual table planning APIs, especially `xBestIndex`, RHS-value probing, batched `IN` constraints, `ORDER BY` consumption, `DISTINCT`/`GROUP BY` handling, `OFFSET`, `idxStr` ownership, and error paths.

## Important APIs, Types, and Functions
The core types are `vt02_vtab`, which embeds `sqlite3_vtab`, stores the owning `sqlite3 *db`, and tracks recursive `xBestIndex` use with `busy`; and `vt02_cur`, which embeds `sqlite3_vtab_cursor` and stores scan bounds, increment direction, and a digit mask for `d IN (...)`.

`vt02Connect()` declares the virtual table schema, optionally using an alternate schema passed through `pAux`. `vt02Disconnect()` frees the table object. `vt02Open()`, `vt02Close()`, `vt02Filter()`, `vt02Next()`, `vt02Eof()`, `vt02Column()`, and `vt02Rowid()` implement cursor execution. `vt02BestIndex()` is the main planner test surface. `sqlite3BestIndexLog()` and `sqlite3RunSql()` optionally create and populate a temp log table describing the `sqlite3_index_info` input and output. `vt02CoreInit()` registers `vt02`, `vt02pkx`, and `vt02pkabcd`; `sqlite3_vt02_init()` exposes the loadable-extension entry point when not compiled under TH3.

## Control Flow
Registration calls `vt02CoreInit()`, which creates three module names with different schemas. SQLite planning calls `vt02BestIndex()`. That function first reads usable literal RHS values for hidden `flags` and `logtab`, then scans constraints on rowid and visible digit columns, assigns `argvIndex` values, calculates `idxNum`, estimated cost, estimated rows, omit flags, optional `idxStr`, optional offset use, and optional order consumption. If `logtab` is supplied, it writes planner diagnostics before returning.

Execution calls `vt02Filter()` with `idxNum` and argv values from the chosen plan. `idxNum` encodes the base equality pattern, digit-step dedup optimization, optional offset, and reverse order. `vt02Filter()` initializes the cursor range and `mD` mask; for `d IN (...)`, it iterates SQLite's `sqlite3_vtab_in_first()` and `sqlite3_vtab_in_next()` APIs to build the allowed ones-digit mask. `vt02Next()` advances by the encoded increment and skips rows whose `d` digit is not in `mD`. `vt02Column()` derives requested columns from the current integer.

## State and Persistence
The virtual table itself has no persistent storage. Row data is computed from cursor state. Persistent or semi-persistent side effects are limited to the optional temp `logtab`, where `xBestIndex` diagnostics are inserted on the same database connection, and to module registration on the connection. The `busy` field prevents recursive planner logging from re-entering `vt02BestIndex()`.

## Dependencies and Integration Points
The file depends on SQLite's virtual table API, extension API, `sqlite3_vtab_rhs_value()`, `sqlite3_vtab_collation()`, `sqlite3_vtab_in()`, `sqlite3_vtab_in_first()`, `sqlite3_vtab_in_next()`, and `sqlite3_vtab_distinct()`. Under TH3 it integrates through `vt02_init(th3state*,...)`; otherwise it is a loadable extension using `sqlite3ext.h`. It is integrated by SQL tests that load or auto-register these virtual tables and compare planner behavior.

## Risks
Most risk is intentional test-surface risk. Flags can force invalid planner choices, invalid `idxNum`, ignored unusable constraints, and deliberately allocated `idxStr`. The logging path executes SQL from inside `xBestIndex`, so recursion and schema mismatch are guarded but still important. `logtab` is quoted with `%w`, reducing identifier injection risk. Constraint handling depends on correct `idxNum` encoding; malformed combinations are reported through `zErrMsg`. The generated data is deterministic, but planner assumptions around `DISTINCT`, `GROUP BY`, and omitted duplicates are subtle and regression-prone.

## Test Signals
Strong test signals include query plans using `x=`, digit prefixes, `d IN (...)`, ascending and descending `ORDER BY`, `OFFSET`, `DISTINCT`, and `GROUP BY`; log table rows for constraints, order terms, RHS availability, collation, and `idxNum`; error tests using bad `idxNum`; OOM tests using the deliberate allocation in `vt02BestIndex()`; and extension-load tests for `sqlite3_vt02_init()`.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/test/vt02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/test/wordcount.c -->
# sources/storage-engines/sqlite/test/wordcount.c

## Purpose
`wordcount.c` is a standalone benchmark and behavior test utility that tokenizes alphabetic words from an input stream and applies one of several SQLite update strategies to a `wordcount(word TEXT PRIMARY KEY, cnt INTEGER)` table. It compares insert/update, replace, upsert, select/update, delete, and query paths, optionally across rowid and `WITHOUT ROWID` table layouts.

## Important APIs, Types, and Functions
The program uses the public SQLite C API: `sqlite3_open()`, `sqlite3_exec()`, `sqlite3_prepare_v2()`, `sqlite3_bind_text()`, `sqlite3_step()`, `sqlite3_reset()`, `sqlite3_finalize()`, `sqlite3_db_status()`, `sqlite3_status()`, and `sqlite3_create_function()`. `realTime()` uses the active VFS clock. `checksumStep()` and `checksumFinalize()` implement a small aggregate used by summary queries. `allLoop()` drives `--all` mode across all operation modes and both table layouts.

## Control Flow
`main()` parses options, deletes the target database unless it is empty or `:memory:`, opens the database and input file, configures pragmas, and enters the selected mode loop. Each loop creates the table inside `BEGIN IMMEDIATE`, prepares the SQL statements needed by that mode, reads lines into a fixed buffer, extracts alphabetic spans, binds each word using `SQLITE_STATIC` while the line buffer is still valid, and executes the appropriate statement sequence. It commits periodically if `--commit` is set, finalizes statements, then optionally prints query totals, timing, summary SQL, and memory/cache statistics.

## State and Persistence
The main persistent state is the target SQLite database and its `wordcount` table. The program unlinks an existing non-memory database at startup, except repeated `--all` iterations reuse the same connection and drop/vacuum the table between iterations. Options such as page size, cache size, journal mode, synchronous mode, collation, and `WITHOUT ROWID` affect database state when the table/database is newly created. `sumCnt`, timers, counters, and prepared statements are process-local.

## Dependencies and Integration Points
The file depends on `sqlite3.h`, the C runtime, and `unistd.h` or `io.h` for unlink behavior. It is integrated into SQLite testing and benchmarking as a command-line utility compiled with `sqlite3.c`. Its SQL mode variants exercise conflict handling, primary key updates, statement preparation, transaction behavior, status counters, and aggregate function registration.

## Risks
Input lines longer than 1999 bytes are processed in chunks, so words split across buffer boundaries are not treated as one word. `SQLITE_STATIC` bindings are safe only because statements are stepped and reset before the input buffer changes. `--all` requires a seekable input file and explicitly rejects stdin. The utility intentionally deletes the output database at startup, which is correct for benchmarks but destructive if used carelessly. Error handling exits immediately and may leave a partially processed database if failures occur mid-run.

## Test Signals
Useful signals include identical summaries across `--insert`, `--replace`, `--upsert`, `--select`, and `--update`; expected destructive behavior for `--delete`; stable `checksum()` output for a fixed corpus; timing output under `--timer` and `--all`; `PRAGMA integrity_check` in summary mode; and memory/status counters returning low or zero outstanding allocations after close.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/test/wordcount.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/tool/GetFile.cs -->
# sources/storage-engines/sqlite/tool/GetFile.cs

## Purpose
`GetFile.cs` is a small C# command-line tool that downloads one URI to the process temporary directory. It is a build/support helper for environments where SQLite scripts need to fetch a single external file with progress reporting and deterministic exit codes.

## Important APIs, Types, and Functions
`ExitCode` enumerates success and failure causes. `Program.Error()` prints usage and optional diagnostics. `Program.GetFileName()` extracts the final path segment from a URI. `DownloadProgressChanged()` serializes progress output with `syncRoot` and prevents percentage regression. `DownloadFileCompleted()` records `DownloadCanceled` or `DownloadError`, prints final status, and signals `doneEvent`. `Main()` validates arguments, resolves URI and output name, configures TLS 1.2 through `ServicePointManager.SecurityProtocol`, uses `WebClient.DownloadFileAsync()`, and waits on a `ManualResetEvent`.

## Control Flow
The entry point accepts `<uri> [fileName]`. It requires an absolute URI, chooses either the basename of the optional filename or the URI path basename, verifies `Path.GetTempPath()`, deletes any existing temp file with that basename, starts an async download, and blocks until the completion event fires. Event handlers update progress and final exit state.

## State and Persistence
Persistent state is the downloaded file under the process temp directory. Global process state includes the static `doneEvent`, `previousPercent`, and `exitCode`; these are safe for the single-download process model. The tool also changes the process `ServicePointManager.SecurityProtocol` to TLS 1.2.

## Dependencies and Integration Points
The file uses .NET Framework-era APIs from `System.Net`, `System.Threading`, `System.IO`, and diagnostics/reflection namespaces. It integrates with SQLite build scripts as a standalone executable and reports failures by numeric process exit code.

## Risks
The output is forced into the temp directory and strips directory components from the optional file name, so callers cannot choose an arbitrary destination. Existing files with the same temp basename are deleted without prompting. `WebClient` and the hard-coded TLS numeric constant are legacy .NET patterns. The async workflow waits forever and has no timeout. URI-derived filenames include the full `PathAndQuery` suffix after the final slash, so unusual query strings can produce awkward names.

## Test Signals
Test with valid HTTP/HTTPS URIs, invalid URIs, URI paths without filenames, explicit filenames containing directories, unavailable temp directories where possible, existing temp files, and network failures. Progress should be monotonic and final exit codes should match the `ExitCode` enum.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/tool/GetFile.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/tool/Replace.cs -->
# sources/storage-engines/sqlite/tool/Replace.cs

## Purpose
`Replace.cs` is a C# standard-input filter that applies a regular expression replacement to each input line and writes either all transformed lines or only lines that changed. It is suitable for build pipelines and source-generation scripts needing regex substitutions without platform-specific shell tools.

## Important APIs, Types, and Functions
`ExitCode` captures argument, boolean parse, exception, and success outcomes. `Replace.Error()` prints usage and diagnostics. `Main()` constructs `Regex` from the first argument, uses the second argument as replacement, parses the third argument as `matchingOnly`, then loops over `Console.In.ReadLine()` and writes to `Console.Out`.

## Control Flow
The tool requires exactly three arguments: pattern, replacement, and a Boolean `matchingOnly` flag. For each input line it calls `regEx.Replace()`. When `matchingOnly` is false, every output line is written. When true, only lines whose replacement output differs by ordinal comparison are emitted.

## State and Persistence
The program has no persistent state and does not touch files directly. State is limited to the compiled `Regex`, replacement string, parsed flag, and one line at a time from stdin.

## Dependencies and Integration Points
The file uses `System.Text.RegularExpressions`, `System.IO`, `System.Diagnostics`, reflection metadata, and standard console streams. It integrates as a command-line build helper with numeric exit codes.

## Risks
User-supplied regex patterns can be expensive and there is no timeout, so catastrophic backtracking can stall a pipeline. Regex construction exceptions are caught and reported as generic `Exception`. Line-oriented processing means it cannot match across newline boundaries and preserves platform default console encoding behavior.

## Test Signals
Exercise replacements with and without matches, `matchingOnly=true` and `false`, invalid Boolean values, invalid regex syntax, empty input, replacement group syntax, and large inputs to confirm streaming behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/tool/Replace.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/tool/build-shell.sh -->
# sources/storage-engines/sqlite/tool/build-shell.sh

## Purpose
`build-shell.sh` demonstrates a full-featured Linux build of the SQLite command-line shell from an amalgamation build directory. It is a developer convenience script rather than a portable production build system.

## Important APIs, Types, and Functions
The script invokes `make sqlite3.c`, then calls `gcc` with SQLite feature defines and source files: `../sqlite/src/shell.c`, `../sqlite/ext/misc/vfstrace.c`, and generated `sqlite3.c`. It links against `dl`, `readline`, and `ncurses`.

## Control Flow
The script assumes it is run from a build directory adjacent to a source checkout named `sqlite`. It first creates or updates `sqlite3.c` through the current Makefile, then compiles `sqlite3` with debug symbols, size optimization, single-thread mode, VFSTRACE, STAT3, FTS4, RTREE, and readline support.

## State and Persistence
It writes the `sqlite3` executable in the current directory and may update generated amalgamation files via `make`. There is no internal state beyond shell process status.

## Dependencies and Integration Points
Dependencies include Bourne shell, make, gcc, a working SQLite build tree layout, readline/ncurses development libraries, and platform linker support for `-ldl`. The script integrates with the SQLite source tree and its generated amalgamation.

## Risks
Paths and libraries are Linux-specific and layout-specific. It does not set `set -e`, so a failed `make sqlite3.c` may still be followed by `gcc`. Feature flags are historical and may not match current recommended builds. STAT3 is obsolete in many modern SQLite configurations.

## Test Signals
A successful run produces an executable `sqlite3` that starts, reports expected compile options through `PRAGMA compile_options`, and can run a basic query. Failure signals include missing sibling source paths, missing readline headers/libraries, and absent Makefile targets.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/tool/build-shell.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/tool/checkSpacing.c -->
# sources/storage-engines/sqlite/tool/checkSpacing.c

## Purpose
`checkSpacing.c` is a source-format checker that reports tab characters, optional carriage returns, optional trailing spaces, and blank lines at EOF. It is a lightweight style gate for SQLite source files.

## Important APIs, Types, and Functions
Flags `CR_OK` and `WSEOL_OK` control whether carriage returns and whitespace-at-end-of-line are tolerated. `checkSpacing()` opens a file in binary mode, scans lines with `fgets()`, tracks tabs, spaces, line numbers, and last non-space line, and prints findings. `main()` parses `--crok`, `--wseol`, and `--help`.

## Control Flow
The default allows trailing spaces but reports tabs, carriage returns, and trailing blank lines. `--crok` suppresses carriage-return reports. `--wseol` enables trailing-space reports by clearing `WSEOL_OK`. Non-option arguments are checked independently.

## State and Persistence
The tool has no persistent state and does not modify files. It reports all findings to stdout and returns zero regardless of violations.

## Dependencies and Integration Points
It depends only on the C runtime. It can be integrated into make/test scripts, though callers must parse output because the exit status does not indicate failure.

## Risks
Lines longer than 1999 bytes are read in fragments, which can affect trailing whitespace and line accounting. Because violations do not change the exit code, CI must treat non-empty output as failure. The default of allowing trailing spaces may surprise users expecting strict style checks.

## Test Signals
Use files containing tabs, CRLF line endings, trailing spaces, final blank lines, long lines, missing files, and combinations of `--crok` and `--wseol`. Expected output should include filename and line number.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/tool/checkSpacing.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/tool/cktclsh.sh -->
# sources/storage-engines/sqlite/tool/cktclsh.sh

## Purpose
`cktclsh.sh` checks that a given Tcl shell executable is at least a requested Tcl version. It is used by make targets that require a minimum Tcl version.

## Important APIs, Types, and Functions
The script writes a temporary Tcl file named `cktclsh$1.tcl` containing a version comparison against `$tcl_version`, runs it with the Tcl shell in `$2`, and removes the temp file. Its interface is positional: `$1` is minimum version and `$2` is the Tcl shell command.

## Control Flow
It creates the Tcl script, executes it, and if the interpreter exits unsuccessfully, prints an error, removes the temp script, and exits 1. On success it removes the temp file and exits with the shell's default success.

## State and Persistence
The only file-system state is the temporary script in the current directory. It is normally removed, but interruption could leave it behind.

## Dependencies and Integration Points
Dependencies are Bourne shell and a Tcl interpreter. It integrates with SQLite makefiles and build checks.

## Risks
The temp filename is predictable and based only on the version string, so concurrent runs in the same directory can race. There is no argument validation or shell quoting around `$2`, so callers must pass a safe command path. Version comparison uses Tcl string/numeric semantics through `$tcl_version<$vers`.

## Test Signals
Run with Tcl versions below and above the threshold, missing Tcl executable, malformed version strings, and concurrent invocations in the same directory.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/tool/cktclsh.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/tool/dbhash.c -->
# sources/storage-engines/sqlite/tool/dbhash.c

## Purpose
`dbhash.c` computes a SHA1 hash of logical SQLite database content rather than raw file bytes. The hash ignores free space and representation details such as page size, encoding, and auto-vacuum, making it useful for verifying semantic database equivalence across rebuilds or transformations.

## Important APIs, Types, and Functions
`SHA1Context` stores SHA1 state, bit counts, and a block buffer. `GlobalVars` holds program name, debug flags, the open SQLite handle, and hash context. `SHA1Transform()`, `hash_init()`, `hash_step()`, and `hash_finish()` implement SHA1. `db_prepare()` and `db_vprepare()` wrap `sqlite3_vmprintf()` and `sqlite3_prepare_v2()`. `hash_one_query()` steps a query and feeds typed column encodings into the hash. `main()` parses options and drives hashing for each database.

## Control Flow
The program parses `--debug`, `--like`, `--schema-only`, `--without-schema`, and filenames. For each database it opens read/write URI mode so hot journals can recover, validates the schema, initializes SHA1, optionally hashes table content for non-virtual, non-`sqlite_%` tables matching the LIKE pattern, optionally hashes schema rows, emits the digest and filename, and closes the connection.

## State and Persistence
Logical hash state is in `g.cx`. The database is opened read/write, so SQLite may perform recovery as a side effect. No application tables are modified. The process prints one digest per input file.

## Dependencies and Integration Points
It depends on SQLite and the C runtime. It is a SQLite test tool for comparing databases independent of physical layout. It uses `sqlite_schema`, type-specific `sqlite3_column_*()` accessors, and SQLite identifier quoting through `%w`.

## Risks
The content query omits explicit `ORDER BY`, relying on historical primary-key order for full table scans, which is called out in the comments but is not a SQL guarantee. It excludes virtual tables and `sqlite_%` system tables from content hashing. Floating point hashing uses in-memory binary representation, which is stable within supported platforms but still low-level. The diagnostic check for mutually exclusive options mentions `--omit-schema` although the actual option is `--schema-only`.

## Test Signals
Equivalent databases with different page sizes should hash identically. Data changes, schema changes, and `--like` filters should change or limit the digest. `--schema-only` and `--without-schema` should isolate schema/content differences. Debug mode should trace typed values to stderr.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/tool/dbhash.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/tool/dbtotxt.c -->
# sources/storage-engines/sqlite/tool/dbtotxt.c

## Purpose
`dbtotxt.c` converts a binary SQLite database or raw file into a compact textual hex dump, suppressing all-zero 16-byte lines. The output is designed for human-readable test fixtures and can optionally include `.open --hexdb` headers for the SQLite CLI.

## Important APIs, Types, and Functions
`allZero()` detects zero-filled 16-byte lines. `main()` parses `--for-cli`, `--script`, `--pagesize N`, and `--raw`, loads the whole file, derives page size from the SQLite header unless overridden or raw, prints page/offset records, hex bytes, safe ASCII rendering, and an end marker.

## Control Flow
The utility validates arguments, reads the full file into memory with 16 bytes of zero padding, optionally splits a zero-terminated SQL prefix from `--script`, validates SQLite minimum size and page size unless raw, derives the basename, prints optional `.open --hexdb`, then loops in 16-byte increments skipping zero lines and printing page headers when the page number changes. If a SQL prefix was present, it prints that script after the hex database.

## State and Persistence
It has no persistent output except stdout redirection chosen by the caller. It reads the entire input into heap memory and frees it before exit.

## Dependencies and Integration Points
Dependencies are only C runtime headers. It integrates with SQLite CLI hex database workflows, test data minimization, and fixture generation.

## Risks
The entire input file is loaded into memory, so very large databases can exhaust memory. `ftell()` and `long` limit portability for huge files. The `--script` prefix expects a zero terminator. Without `--raw`, files shorter than 100 bytes or with invalid page sizes are rejected. It suppresses zero lines, so consumers must understand the custom format.

## Test Signals
Round-trip a small SQLite database through CLI hex import, check `--for-cli` and `--script` headers, verify invalid page sizes fail, compare `--raw` handling of short files, and confirm zero-filled pages are compacted.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/tool/dbtotxt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/tool/emcc.sh.in -->
# sources/storage-engines/sqlite/tool/emcc.sh.in

## Purpose
`emcc.sh.in` is a configure-time template for a shell wrapper around Emscripten's `emcc`. It locates `emcc` directly or via an EMSDK installation and then execs the compiler with the caller's arguments.

## Important APIs, Types, and Functions
Template variables `@EMSDK_HOME@`, `@EMSDK_ENV_SH@`, and `@BIN_EMCC@` are substituted by configure. The script uses `which emcc`, environment variable checks, optional sourcing of `emsdk_env.sh`, and `exec $emcc "$@"`.

## Control Flow
The generated script first uses configured `emcc`, then PATH. If not found, it requires `EMSDK_HOME`, determines `EMSDK_ENV_SH`, validates that file, sources it quietly if `$EMSDK` is not already set, looks for `emcc` again, and exits with distinct error codes for missing configuration or compiler. On success it replaces itself with `emcc`.

## State and Persistence
It does not persist files. It mutates the current shell process environment only until `exec`, primarily through sourced EMSDK variables.

## Dependencies and Integration Points
It depends on Bourne-like shell behavior, though it uses `source`, which is not strictly POSIX `sh`. It integrates with SQLite's configure output and WebAssembly/Emscripten build path.

## Risks
The `source` keyword can fail under shells that only support `.`. `exec $emcc "$@"` leaves `$emcc` unquoted, so paths containing spaces are unsafe. The wrapper trusts configure substitutions and the EMSDK environment script. Error codes are meaningful but only if callers preserve them.

## Test Signals
Test configured `@BIN_EMCC@`, PATH-only `emcc`, EMSDK discovery with and without pre-set `$EMSDK`, missing `EMSDK_HOME`, missing `emsdk_env.sh`, and compiler paths containing spaces.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/tool/emcc.sh.in -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/tool/enlargedb.c -->
# sources/storage-engines/sqlite/tool/enlargedb.c

## Purpose
`enlargedb.c` appends unused pages to an SQLite database by increasing the database-size header field and extending the file with zeros. It intentionally creates databases that fail `PRAGMA integrity_check` because the appended pages are not valid allocated structures, while remaining useful for boundary and file-size tests.

## Important APIs, Types, and Functions
The program is a single `main()` using `strtoll()`, binary file I/O, SQLite header validation, page-size decoding, database page-count field updates at header bytes 28-31, `fseek()`, and `fwrite()`.

## Control Flow
It requires `DATABASE N`, parses `N`, opens the database read/write, reads the first 100 bytes, validates the SQLite signature and page size, reads the current page count, clamps the new count to `0xffffffff`, writes the new count back to the header, seeks to the last byte of the enlarged database, writes one zero byte, and exits.

## State and Persistence
The target database file is modified in place. Header page count and file length change permanently. No journal or SQLite API is used.

## Dependencies and Integration Points
It depends only on the C runtime and SQLite file format knowledge. It integrates with low-level SQLite tests for oversized files, page-count limits, and corruption/integrity behavior.

## Risks
This intentionally corrupts integrity semantics and should only be used on disposable databases. It has limited error checking for `fseek()`/`fwrite()`, uses `long` seek casts that may be non-portable for very large files, and does not coordinate with active SQLite connections.

## Test Signals
Run on a copy of a valid database and verify file size and header page count increase. `PRAGMA integrity_check` should report problems, while basic open/read scenarios may still work depending on access pattern. Invalid signatures, invalid page sizes, missing args, and non-positive `N` should fail.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/tool/enlargedb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/tool/extract.c -->
# sources/storage-engines/sqlite/tool/extract.c

## Purpose
`extract.c` copies a byte range from a file to stdout. It is a minimal helper for constructing binary fixtures or isolating sections of database files.

## Important APIs, Types, and Functions
The program consists of `main()` using `fopen()`, `atoi()`, `malloc()`, `fseek()`, `fread()`, `fclose()`, and `fwrite()`.

## Control Flow
It requires `FILENAME OFFSET AMOUNT`, opens the file in binary mode, allocates `AMOUNT` bytes, seeks to `OFFSET`, reads the requested amount, and writes it to stdout if the full read succeeds. Errors print to stderr and return non-zero.

## State and Persistence
It does not modify input files. Output is raw binary on stdout. Heap state is not explicitly freed before process exit.

## Dependencies and Integration Points
Only the C runtime is required. The tool can be used by SQLite scripts that need deterministic byte slices from database files.

## Risks
`atoi()` provides weak validation and cannot report overflow or negative values cleanly. Negative or very large amounts can lead to bad allocations or undefined behavior through conversion to `size_t`. `fseek()` status is not checked. The diagnostic for short reads prints `size_t` with `%d`, which is type-incorrect.

## Test Signals
Test exact extraction, offset past EOF, short reads, zero amount, negative arguments, binary data containing NUL bytes, and stdout redirection.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/tool/extract.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/tool/fast_vacuum.c -->
# sources/storage-engines/sqlite/tool/fast_vacuum.c

## Purpose
`fast_vacuum.c` demonstrates a high-speed alternative to SQLite `VACUUM` that copies schema and table content into a temporary attached database, then renames files. It is explicitly demonstration code with operational restrictions.

## Important APIs, Types, and Functions
`vacuumFinalize()` finalizes statements and exits on errors. `execSql()` prepares, prints, steps, and finalizes one SQL statement. `execExecSql()` runs a query that returns SQL text and executes each returned statement. `main()` opens the database, generates random temp/backup names, attaches the temp database, copies schema/content, commits, closes, and renames files.

## Control Flow
After validating one database argument, the program opens the database, builds random names ending in `-vacuum-...` and `-backup-...`, attaches the temp DB as `vacuum_db`, enables `writable_schema`, begins a transaction, creates mirror tables and indexes by transforming `sqlite_schema.sql`, copies table rows, handles `sqlite_sequence`, inserts view/trigger/virtual-table schema rows directly, commits, closes, renames the original to backup, and renames the temp database to the original name.

## State and Persistence
It creates a new temporary database file, creates a backup name for the original, and ultimately replaces the original database path. The original database remains under the backup name if renames succeed. It does not use SQLite's normal `VACUUM` machinery.

## Dependencies and Integration Points
It depends on `sqlite3.h`, `sqlite3.c` at link time, C runtime file rename behavior, and SQLite schema table format. It is a sample for developers and a test utility for vacuum-like copying.

## Risks
The comments identify major risks: callers must ensure exclusive external access; page-size and auto-vacuum changes are unsupported; crashes during rename can leave unexpected filenames. Additional risks include fragile SQL string slicing for schema recreation, limited support for newer schema objects, direct `writable_schema` writes, no checking of `rename()` results, and possible leftover temp/backup files.

## Test Signals
Use disposable databases with tables, indexes, unique indexes, views, triggers, virtual tables, and `sqlite_sequence`; compare content before and after with `dbhash`; verify file size reduction; test interrupted runs manually in a sandbox; confirm concurrent access is not allowed by policy rather than code.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/tool/fast_vacuum.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/tool/fuzzershell.c -->
# sources/storage-engines/sqlite/tool/fuzzershell.c

## Purpose
`fuzzershell.c` is a specialized SQLite shell for fuzzing. It reads SQL test cases from stdin or files, executes them against isolated in-memory SQLite databases by default, supports multi-case corpus files, adds fuzzing-friendly SQL helpers, detects memory leaks after each case, and can run simulated OOM loops.

## Important APIs, Types, and Functions
`GlobalVars` stores program name, original and OOM memory methods, OOM counters, and current test name. `oomMalloc()` and `oomRealloc()` wrap SQLite memory allocation to simulate failures. `abendError()` aborts to signal fuzzer crashes; `fatalError()` exits normally. `sqlexec()` executes required setup SQL. Logging, trace, and exec callbacks provide verbose or quiet output.

The `Str` accumulator supports dynamic SQL text from `autoexec`. The embedded `eval()` implementation uses `EvalResult`, `callback()`, and `sqlEvalFunc()` to run recursive SQL. The embedded `generate_series` virtual table uses `series_cursor`, `seriesConnect()`, `seriesBestIndex()`, `seriesFilter()`, and related cursor methods. `integerValue()` parses decimal, hex, and size-suffixed options. `main()` owns option parsing, SQLite global configuration, input loading, test-case splitting, per-case database setup, execution, OOM iteration, unique-case storage, and cleanup.

## Control Flow
Startup shuts SQLite down, parses options such as memory heap/pagecache/lookaside/scratch settings, `--database`, `--oom`, `--unique-cases`, encodings, verbosity, and input files. It configures SQLite before initialization, optionally installs OOM memory methods, opens an in-memory database for unique-case deduplication, and reads each input file fully into memory. It skips leading `#` header lines and splits test cases on `/****<...>****/` markers.

For each test case, it opens either the named on-disk database or an in-memory `main.db`, configures lookaside, trace, `eval()`, `generate_series`, length limits, encoding, page size, and autovacuum, then optionally replaces the SQL with concatenated `autoexec.sql` rows from the database. It executes the SQL with verbose row output or a no-op callback, closes the database, asserts no leaked SQLite memory unless collecting unique cases, and repeats with different OOM countdowns when `--oom` is active. At the end it can write unique cases ordered by execution time.

## State and Persistence
Default database state is per-test in memory and discarded after each case. `--database` uses a caller-supplied database file and may persist mutations. `--unique-cases` stores unique SQL blobs and timings in a temporary in-memory SQLite database, then writes a compact corpus file. Global SQLite allocator, pagecache, scratch, and log configuration are process-wide. The OOM counters mutate around each SQLite execution.

## Dependencies and Integration Points
The file depends on SQLite's C API, optional trace API, virtual table API, SQLite memory configuration API, and the C runtime. It integrates with external fuzzers such as AFL, SQLite test corpora, OOM testing, and regression minimization workflows.

## Risks
Input files are loaded fully into memory. OOM simulation only wraps `xMalloc` and `xRealloc`, leaving other allocator methods from the original structure. `--database` allows persistent disk writes, unlike the default memory mode. The shell intentionally omits dot commands for safety, but arbitrary SQL can still exercise expensive or recursive behavior. `source` of SQL from an `autoexec` table means fuzzed databases can control executed SQL. The leak check depends on SQLite memory accounting and is skipped when unique-case collection is enabled.

## Test Signals
Signals include zero errors across multi-case corpora, crash/abort on SQLite API misuse or leaks, deterministic `--unique-cases` output, `--oom` completion across single-failure and repeated-failure modes, verbose trace and row output, `generate_series` query behavior, `eval()` recursion behavior, and `TEST_FAILURE` environment simulation.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/tool/fuzzershell.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/tool/getlock.c -->
# sources/storage-engines/sqlite/tool/getlock.c

## Purpose
`getlock.c` inspects POSIX advisory locks on an SQLite database and, for WAL databases, the associated `-shm` file. It reports lock type and owning process ID when a conflicting lock is found.

## Important APIs, Types, and Functions
`usage()` prints the command form. `isLocked()` builds a `struct flock`, calls `fcntl(F_GETLK)`, and reports a lock if the kernel returns a conflicting lock. Constants encode SQLite rollback-lock bytes (`PENDING_BYTE`, `RESERVED_BYTE`, `SHARED_FIRST`, `SHARED_SIZE`) and WAL shared-memory lock offsets (`SHM_WRITE`, `SHM_CHECKPOINT`, `SHM_RECOVER`, read locks).

## Control Flow
`main()` opens the database read-only, reads and validates the 100-byte SQLite header, first checks for an exclusive lock over the shared-lock range, then branches on header byte 18 to distinguish rollback and WAL modes. Rollback mode checks pending, reserved, and shared locks on the database file. WAL mode opens `DATABASE-shm`, checks recovery, checkpoint, write, and read locks. If no locks are found, it prints `file is not locked`.

## State and Persistence
The tool is read-only. It opens file descriptors but does not modify database or shm files. It prints observations to stdout and errors to stderr.

## Dependencies and Integration Points
It is Unix-specific and depends on POSIX `open()`, `read()`, `fcntl()`, advisory locking semantics, and SQLite's default lock byte layout. It integrates with debugging and test workflows around database locking.

## Risks
It only works with Unix POSIX advisory locking and the usual `PENDING_BYTE`. WAL detection from the database header may be stale if mode changes are in flight. Missing `-shm` files are treated as errors for WAL-mode headers. Some early returns do not close descriptors or free `zShm`, which is acceptable for process exit but not library-style reuse.

## Test Signals
Run against unlocked rollback and WAL databases, databases with active readers/writers/checkpointers, invalid files, missing `-shm` files, and non-POSIX VFS scenarios. Reported lock names and PIDs should match known holding processes.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/tool/getlock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/tool/index_usage.c -->
# sources/storage-engines/sqlite/tool/index_usage.c

## Purpose
`index_usage.c` analyzes a workload log and reports how often each index in a database schema is selected by SQLite's query planner. It helps identify unused or heavily used indexes for a given SQL corpus.

## Important APIs, Types, and Functions
`usage()` prints expected database and log schema. `main()` uses SQLite APIs to open the schema database, create a temp `idxu` table of indexes and counters, attach the log database, prepare `EXPLAIN QUERY PLAN` for each logged statement, parse detail text for `USING INDEX`, increment counters, and print a report with indexed columns from `pragma_index_info()`.

## Control Flow
The program parses `--progress N`, `-q`, `--using NAME`, and positional `DATABASE LOG`. It opens the database read-only, validates schema access, creates temp tracking state, attaches `LOG`, selects non-transaction/non-pragma SQL from `log.sqllog`, and for each compilable statement walks the EQP rows. When an index use is detected, it optionally prints the SQL for `--using`, increments the counter, and continues. Finally it prints indexes ordered by count descending.

## State and Persistence
The main database is opened read-only, but SQLite temp state is created on the connection. The log database is attached read-only only if SQLite enforces it from the main open flags and VFS; the code itself just uses `ATTACH %Q`. No persistent schema or log changes are intended.

## Dependencies and Integration Points
It depends on SQLite, `sqlite_schema`, `EXPLAIN QUERY PLAN` output text, and a log database with `sqllog(sql TEXT)`. It integrates with workload capture and schema tuning workflows.

## Risks
The parser depends on human-readable EQP detail text containing `USING INDEX`, which can change across SQLite versions and misses covering-index or automatic-index text variants if wording differs. It filters statements by the first five uppercase characters, a simple heuristic. Statements with side effects are only prepared as `EXPLAIN QUERY PLAN`, not run, but invalid SQL is counted as an error unless quiet. Index-name extraction scans until a character before `(` in a fragile way.

## Test Signals
Use a known schema and log where specific queries should use specific indexes, compare `--using NAME` output, verify progress messages, test invalid SQL with and without `-q`, and run across SQLite versions to detect EQP text drift.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/tool/index_usage.c -->
