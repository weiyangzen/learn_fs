# subset-b-008811 Research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/test/fuzzinvariants.c -->
# sources/storage-engines/sqlite/test/fuzzinvariants.c

## Purpose

`fuzzinvariants.c` is a support library used by SQLite `fuzzcheck` to validate query-result invariants. Given a prepared statement that has just returned `SQLITE_ROW`, it captures the current output row, synthesizes alternate SQL queries that should also contain that row, executes the alternate query, and reports a hard failure if the row cannot be found and the result cannot be explained by corruption, ambiguous ordering, collation, virtual-table behavior, or scalar-subquery behavior.

## Important APIs, Types, and Functions

- `int fuzz_invariant(sqlite3 *db, sqlite3_stmt *pStmt, int iCnt, int iRow, int nRow, int *pbCorrupt, int eVerbosity, unsigned int dbOpt)` is the exported entry point. It selects one invariant by `iCnt`, prepares the derived SQL, binds row values from `pStmt`, searches for a matching row, and returns `SQLITE_OK`, `SQLITE_DONE`, `SQLITE_CORRUPT`, or an SQLite error. Severe non-corruption invariant failures call `abort()` after diagnostics.
- `static char *fuzz_invariant_sql(sqlite3_stmt *pStmt, int iCnt)` builds alternate SELECT text around the original `sqlite3_sql(pStmt)`. It varies `DISTINCT`, `ORDER BY`, all-column predicates, and single-column predicates across `iCnt`.
- `static int sameValue(...)` compares column values across statements, including integer/float compatibility, bytewise BLOB/TEXT comparison, UTF-16 handling, and an optional SQLite comparison statement for collation-sensitive rechecks.
- `bindDebugParameters()` recognizes fuzz/debug parameters such as `$int_NNN`, `$text_TTTT`, and optional `SQLITE_ENABLE_CARRAY` arrays for colors and primes.
- `reportInvariantFailed()`, `printRow()`, and `printHex()` emit reproduction detail, expanded SQL, missing row content, and alternate-result rows before aborting.

## Control Flow

`fuzz_invariant()` exits early if the database is already marked corrupt, if the statement has more than 100 parameters, or if `fuzz_invariant_sql()` reports no more invariant variants. Every third invariant temporarily inverts optimization flags with `sqlite3_test_control(SQLITE_TESTCTRL_OPTIMIZATIONS, db, ~dbOpt)` while preparing the alternate query, then restores `dbOpt`.

After preparing the alternate statement, the function binds debug parameters and appends current-row column values after the original query parameters. It scans the alternate results with `sqlite3_step()` and `sameValue()`. If no matching row appears, it runs a cascade of false-positive filters: `PRAGMA integrity_check`, original-query re-execution with `SQLITE_DBCONFIG_REVERSE_SCANORDER` flipped, a collation-aware comparison query using binary/nocase/rtrim equality, and a `bytecode(?1)` query that ignores cases involving `VOpen` opcodes or scalar subqueries. Only after these filters does it call `reportInvariantFailed()`.

`fuzz_invariant_sql()` strips trailing whitespace and semicolons, refuses SQL containing `?` positional parameters, wraps the original query in a subquery, optionally adds `DISTINCT`, derives output column names from a prepared base statement, skips duplicate or randomized column names, adds `ISNULL` or equality predicates for selected columns, and may append `ORDER BY`.

## State and Persistence Behavior

The file does not persist data. It mutates process-local SQLite connection state temporarily through optimization test controls and reverse-scan-order db config, and allocates derived SQL through `sqlite3_str`/`sqlite3_malloc64`. It uses `*pbCorrupt` as caller-owned state to suppress later checks once database corruption is detected. Failures abort the process, which is intentional for fuzz triage.

## Dependencies and Integration Points

This file depends on SQLite public APIs plus test-only/internal facilities: `sqlite3_test_control()`, `SQLITE_TESTCTRL_OPTIMIZATIONS`, `SQLITE_DBCONFIG_REVERSE_SCANORDER`, `sqlite3_expanded_sql()`, `sqlite3_value_encoding()`, `bytecode(?)`, and optionally `sqlite3_carray_bind()`. It integrates with `fuzzcheck`, which supplies a live row statement, row counters, corruption state, verbosity, and optimizer flag baseline.

## Risks and Edge Cases

- `fuzz_invariant_sql()` skips input SQL containing `?`, but named debug parameters are allowed and must be rebound consistently.
- Column-name based predicates can be unsafe with duplicate, randomized, or collation-sensitive names; the implementation explicitly filters duplicates/random suffixes and has a second collation-aware pass.
- The reverse-scan-order branch appears to compare `pStmt` against `pTestStmt` inside the `pCk` loop rather than against `pCk`; this is likely intentional historical behavior or a subtle false-positive filter, but it is worth treating carefully during modifications.
- The code aborts on final invariant failure and on impossible text-encoding mismatch, which is correct for a fuzz harness but unsuitable for library-style embedding.
- Virtual tables and scalar subqueries are known invariant hazards and are filtered using bytecode inspection.

## Test Signals

Expected signals are invariant success (`SQLITE_OK`), end of invariant space (`SQLITE_DONE`), corruption suppression (`SQLITE_CORRUPT` with `*pbCorrupt=1`), verbose expanded SQL when `eVerbosity>=2`, and a detailed abort report on genuine mismatches. Relevant tests exercise optimizer-on/off preparation, `DISTINCT`/`ORDER BY` variants, NULL and non-NULL column predicates, collation differences, corrupt database handling, virtual tables, scalar subqueries, and carray/debug parameter binding.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/test/fuzzinvariants.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/test/json/json-speed-check.sh -->
# sources/storage-engines/sqlite/test/json/json-speed-check.sh

## Purpose

`json-speed-check.sh` is a day-to-day SQLite JSON performance and size monitoring helper. It builds a local `jsonshell` from `shell.c` and `sqlite3.c`, runs a JSON or JSONB workload under Valgrind Cachegrind, annotates the profile, and optionally opens a Fossil graphical diff against a baseline result.

## Important APIs, Commands, and Variables

- Positional `NAME` selects the output basename: `summary-$NAME.txt` and `$TYPE-$NAME.txt`.
- Options include `--nodiff`, `--lean`, `--clang`, `--gcc7`, `--jsonb`, and arbitrary compiler flags beginning with `-`.
- `CC_OPTS`, `LEAN_OPTS`, `CC`, `BASELINE`, `TYPE`, `doDiff`, and `doJsonB` control build and comparison behavior.
- External commands include `$CC`, `valgrind --tool=cachegrind`, `cg_anno.tcl`, `sed`, `tee`, `ls`, and `fossil xdiff --tk`.

## Control Flow

The script requires an output name, shifts options, then parses flags. `--lean` appends a curated set of SQLite compile-time options that disable threads, status tracking, deprecated features, shared cache, and other overhead. `--jsonb` switches `TYPE=jsonb`.

It prints build metadata to `summary-$NAME.txt`, removes old Cachegrind output and `jsonshell`, compiles `./shell.c ./sqlite3.c`, logs the resulting binary size, computes the script directory, selects `$TYPE''100mb.db`, and runs `jsonshell` under Cachegrind with the query file `$home/$TYPE-q1.txt`. The Cachegrind annotation is written to `$TYPE-$NAME.txt`, followed by normalized summary output. If `NAME` differs from `BASELINE` and diffs are enabled, it opens a Fossil diff between baseline and current annotated output.

## State and Persistence Behavior

The script creates and overwrites local working artifacts: `jsonshell`, `cachegrind.out.*`, `summary-$NAME.txt`, and `$TYPE-$NAME.txt`. It reads workload databases such as `json100mb.db`/`jsonb100mb.db` and query files such as `json-q1.txt` or `jsonb-q1.txt`. It does not clean summary/profile outputs.

## Dependencies and Integration Points

It assumes an SQLite amalgamation checkout/build directory where `shell.c` and `sqlite3.c` exist, plus a JSON test data directory containing the query files and 100MB databases. It integrates with SQLite’s Fossil workflow by comparing annotated Cachegrind outputs with `fossil xdiff --tk`.

## Risks and Edge Cases

- The script echoes `$DB` but the Valgrind command currently hardcodes `json100mb_b.db`, so JSONB mode or renamed databases may not run the echoed target. This is a maintenance risk.
- Several variables (`doExplain`, `doCachegrind`, `doVdbeProfile`, `doWal`, `doJsonB`) are set but mostly unused in this script variant.
- Missing Valgrind, Tcl annotation tooling, Fossil/Tk, workload database, or query files cause runtime failure.
- Output files are overwritten without prompting, and Cachegrind output is globally removed with `rm -f cachegrind.out.*`.

## Test Signals

Primary signals are successful compilation of `jsonshell`, non-empty `summary-$NAME.txt`, non-empty `$TYPE-$NAME.txt`, stable Cachegrind instruction counts, and meaningful diffs versus `$TYPE-$BASELINE.txt`. Failures are usually shell command exits, missing files, or noisy performance deltas in Fossil diff.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/test/json/json-speed-check.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/test/kvtest.c -->
# sources/storage-engines/sqlite/test/kvtest.c

## Purpose

`kvtest.c` implements a standalone key/value BLOB benchmark. It compares the speed of storing and accessing large BLOBs in SQLite against storing the same content as individual filesystem files. It supports creating a test database, exporting BLOBs to flat or tree directory layouts, reporting database statistics, and running read/write performance tests through SQL, SQLite incremental BLOB I/O, or direct filesystem I/O.

## Important APIs, Types, and Functions

- CLI commands: `init`, `export`, `stat`, and `run`.
- `initMain()` creates `kv(k INTEGER PRIMARY KEY, v BLOB)` with configurable row count, BLOB size/variance, and page size.
- `exportMain()` reads all `kv` rows and writes one file per key to either `DIRECTORY/000001` style or `DIRECTORY/00/00/01` tree style.
- `statMain()` reports row count, min/max/avg BLOB length, page size, page count, freelist count, and `PRAGMA integrity_check(10)`.
- `runMain()` performs timed reads or updates across SQLite DBs or exported directories. It supports SQL access, incremental `sqlite3_blob` access, direct file reads/writes, order modes, journaling/cache/mmap/sync options, optional integrity check, and stats.
- Helpers include `pathType()`, `fileSize()`, `randInt()`, `readFile()`, `updateFile()`, `timeOfDay()`, `display_stats()`, and `rememberFunc()`.

## Control Flow

`main()` dispatches by the first command. `init` parses numeric options with suffix support, opens the target DB, sets page size, vacuums, and bulk inserts recursive CTE-generated `randomblob()` rows in one transaction. `export` creates the output directory, determines flat/tree mode, scans `SELECT k, v FROM kv ORDER BY k`, formats filenames from keys, creates tree subdirectories as needed, and writes raw BLOB bytes.

`run` first classifies its target as DB, flat directory, or tree directory. For DB targets it pre-opens once to recover any crash state before timing, then opens again, applies `mmap_size`, `cache_size`, `synchronous`, journal mode, and optional WAL auto-checkpoint settings. It determines `iMax`, begins a transaction unless `--multitrans` is requested, and loops until it has completed the requested number of non-missing BLOB operations. Each iteration either reads/updates a filesystem file, reads/writes via `sqlite3_blob_open()`/`sqlite3_blob_reopen()`, or executes SQL (`SELECT v FROM kv WHERE k=?1` or `UPDATE kv SET v=randomblob(remember(length(v),?2)) WHERE k=?1`). It advances keys ascending, descending, or deterministically random, accumulates bytes processed, finalizes handles, commits/closes, optionally runs integrity check, and prints timing and throughput.

## State and Persistence Behavior

`init` rewrites the target database schema and data. `export` creates directories and files representing BLOB values. `run --update` mutates either the SQLite DB or exported files in place while preserving BLOB sizes. DB runs can alter connection-local pragmas, journal mode, cache size, mmap size, synchronous mode, WAL checkpoint behavior, and transaction boundaries. Temporary heap buffers are managed with SQLite allocation APIs.

## Dependencies and Integration Points

The program compiles with SQLite amalgamation and standard C/POSIX or Windows filesystem APIs. Linux builds can read `/proc/PID/io` for I/O stats. It integrates with SQLite benchmark workflows by exercising pager cache, mmap, WAL/rollback journal modes, incremental BLOB API, SQL update/read paths, and filesystem comparison baselines.

## Risks and Edge Cases

- `pathType()` classifies any readable file whose size is a multiple of 512 as a database, so non-SQLite files can reach SQLite open logic.
- `readFile()` allocates `nIn` bytes despite documenting a nul terminator; callers use it as binary data and free immediately, so the missing terminator is not currently harmful but the comment is inaccurate.
- `runMain()` checks `if( nCount<0 )` after parsing `--mmap`, which appears to intend `mmapSize<0`.
- `--multitrans` is documented as per-operation transactions, but the loop does not explicitly begin/commit per operation in the visible implementation; changes here need care against intended benchmark semantics.
- Filesystem update fsync behavior differs by platform and only flushes the file handle, not necessarily containing directories.
- Missing keys increase `nCount` and `nExtra`, so sparse key ranges can extend runs significantly.

## Test Signals

Useful signals include successful command help, deterministic `init` row counts, `stat` integrity-check output, byte-for-byte export size checks, `run` throughput output for SQL/BLOB/filesystem modes, update mode preserving sizes, `--integrity-check` returning `ok`, and `--stats` reporting cache and memory counters. Cross-mode comparisons should preserve total logical BLOB counts and expose expected timing differences without crashes or leaks.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/test/kvtest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/test/lemon-test01.y -->
# sources/storage-engines/sqlite/test/lemon-test01.y

## Purpose

`lemon-test01.y` is a historical Lemon parser-generator testcase for error recovery and parser lifecycle callbacks. Its header says it was made obsolete by SQLite check-in `7cca80808cef192f` on 2021-08-17 and no longer works, but it is retained as a reference for previous Lemon behavior.

## Important APIs, Types, and Grammar Elements

- Lemon directives: `%token_prefix TK_`, `%token_type int`, `%default_type int`, `%include`, `%syntax_error`, `%parse_accept`, `%parse_failure`, and `%code`.
- Grammar rules: `all ::= A B.` and `all ::= error B.`.
- Generated parser APIs expected by the embedded C code: `ParseInit()`, `Parse()`, `ParseFinalize()`, `yyParser`, and generated token macros from `lemon-test01.h`.
- Test counters: `nSyntaxError`, `nAccept`, `nFailure`, `nTest`, and `nErr`.

## Control Flow

The generated parser includes global counters and callback actions that increment syntax-error, accept, and failure counts. The embedded `main()` initializes a parser instance, feeds three token sequences, finalizes after end-of-input, and checks counters with `testCase()`.

The first sequence `A B EOF` expects no syntax errors, one accept, and no failures. The second sequence `B B EOF` expects one syntax error followed by successful recovery through `error B`. The third sequence `A A EOF` expects one syntax error, no accept, and no failure according to the historical expected behavior.

## State and Persistence Behavior

The file has no persistence. State is limited to parser stack state and process-global counters in the generated parser/test program.

## Dependencies and Integration Points

It is consumed by the SQLite Lemon parser generator: `lemon lemon-test01.y && gcc -g lemon-test01.c && ./a.out`. It depends on generated `lemon-test01.c` and `lemon-test01.h`, standard C `assert.h`, and Lemon’s generated parser API. It is a test asset rather than production SQLite runtime code.

## Risks and Edge Cases

- The file explicitly states it no longer works with current Lemon behavior, so it should not be treated as an active pass/fail regression test without understanding the historical check-in.
- It tests very narrow error-recovery semantics that may have changed intentionally.
- The third test reuses test IDs `200`, `210`, and `220`, which can make output less distinct.

## Test Signals

Historical success would print nine `ok` lines and a final all-tests-pass message. In current trees, failure may be expected because the testcase is obsolete. Its useful signal is documenting the old parser callback/recovery contract.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/test/lemon-test01.y -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/test/optfuzz-db01.c -->
# sources/storage-engines/sqlite/test/optfuzz-db01.c

## Purpose

`optfuzz-db01.c` embeds the byte-for-byte content of `testdb01.db` as a C array named `data001`. It is the fixed read-only database fixture used by `optfuzz.c` to run optimizer correctness fuzz tests without requiring an external database file.

## Important APIs, Types, and Data

- `unsigned char data001[]` is the only top-level symbol.
- The byte stream begins with the SQLite database header and contains schema/data for optimizer fuzzing.
- Visible schema strings in the image include tables such as `t1`, `t2`, `t3`, `t4`, `t5`, autoindexes, explicit indexes such as `t1e`, `t2ed`, `t3x1`, and many views (`v00`, `v10`, `v20`, `v30`, `v40`, `v50`, `v60`, `v61`, `v62`, `v70`, and aggregate/compound-query variants).

## Control Flow

There is no executable control flow in this file. It is included directly by `optfuzz.c`, then passed to `sqlite3_deserialize(dbRun, "main", data001, sizeof(data001), sizeof(data001), SQLITE_DESERIALIZE_READONLY)` to initialize an in-memory database.

## State and Persistence Behavior

The array is static program data. `optfuzz.c` treats it as a read-only deserialized database; no external files are created by this fixture. Because it is not copied before deserialization in `optfuzz.c`, the read-only flag is important.

## Dependencies and Integration Points

This file integrates tightly with `optfuzz.c` and SQLite’s deserialize API. The embedded database is designed to cover optimizer-sensitive constructs: rowid and WITHOUT ROWID tables, primary keys, unique constraints, text and numeric affinity cases, indexes, views, aggregate views, `ORDER BY`/`LIMIT`, compound queries, joins, left joins, and recursive CTEs.

## Risks and Edge Cases

- Manual edits are unsafe because the array must remain a valid SQLite database image.
- The symbol is non-`static`, so including this file in more than one translation unit would create duplicate global definitions.
- The fixture’s test value depends on matching `optfuzz.c` expectations; schema changes in SQLite optimizer tests may require regenerating the whole byte image.
- The database has intentionally diverse and odd SQL objects; failures may come from fixture corruption, SQLite deserialize changes, or optimizer behavior.

## Test Signals

The main signal is `optfuzz.c` successfully deserializing `data001` and executing fuzz SQL against it. Valid fixture behavior is observed indirectly through optimizer/no-optimizer comparison results, statement/row counts, and absence of deserialize or schema errors.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/test/optfuzz-db01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/test/optfuzz.c -->
# sources/storage-engines/sqlite/test/optfuzz.c

## Purpose

`optfuzz.c` is a standalone optimizer correctness fuzzer harness. It executes fuzzer-generated SQL scripts twice against a fixed database: once with normal optimizations and once with optimizations disabled. It records normalized outputs from both runs and fails if the outputs differ.

## Important APIs, Types, and Functions

- The file includes `sqlite3.c` directly with `SQLITE_THREADSAFE=0` and `SQLITE_OMIT_LOAD_EXTENSION=1`, then includes `optfuzz-db01.c`.
- `prepare_sql()` formats and prepares SQL or exits with diagnostics.
- `run_sql()` formats and executes SQL or exits with diagnostics.
- `optfuzz_exec()` prepares and steps through one or more SQL statements, converts each result row into a textual comma-separated representation, sorts row strings for each statement, and stores statement markers plus grouped output in an output database table.
- `readFile()` loads input SQL files into SQLite-allocated memory.
- `main()` parses options, initializes `dbOut` and `dbRun`, deserializes `data001`, runs opt/noopt comparisons, and checks for SQLite memory leaks.

## Control Flow

For each input file, `main()` reads SQL text and rolls back any prior transaction on `dbRun`. With `--valid-sql`, it simply executes the file and prints filenames that succeed. Otherwise it disables optimization flags via `sqlite3_test_control(SQLITE_TESTCTRL_OPTIMIZATIONS, dbRun, 0)`, runs `optfuzz_exec()` into table `opt`, then enables a broad optimization mask with `0xffff` and runs into table `noopt`.

`optfuzz_exec()` starts a transaction on `dbOut`, creates output tables if needed, and iterates over every statement in the SQL script using `sqlite3_prepare_v2()` and the leftover tail pointer. For each statement, it clears a staging table, steps result rows, renders NULL as `NULL`, quotes text, renders other values through column text, rejects excessively long row lines, inserts row lines into staging, then inserts the original SQL marker and a sorted `group_concat()` of staging rows into the named output table. After both runs, `main()` compares `group_concat(x,char(10))` across `opt` and `noopt`; on mismatch it prints both outputs and exits non-zero.

## State and Persistence Behavior

All runtime databases are in-memory. `dbRun` is initialized from the embedded read-only fixture. `dbOut` accumulates `staging`, `opt`, and `noopt` rows for comparisons; the code does not drop old `opt`/`noopt` rows between input files, so a long multi-file run compares cumulative output unless process state is otherwise reset. Heap allocations use SQLite memory APIs for SQL buffers and input file content; `azIn` uses libc `realloc`/`free`.

## Dependencies and Integration Points

The harness depends on SQLite amalgamation internals, `sqlite3_deserialize()`, `sqlite3_test_control()`, and the embedded `data001` fixture. It integrates with fuzzing workflows that generate SQL scripts and expect a deterministic oracle for optimizer transformations. It also relies on SQLite result conversion semantics via `sqlite3_column_text()`.

## Risks and Edge Cases

- The optimization toggles are easy to misread: the first pass passes mask `0`, and the second pass passes `0xffff`; behavior depends on SQLite’s test-control semantics.
- Result normalization sorts rows within each statement, making the oracle insensitive to row ordering. That is useful for many optimizer checks but can hide order-dependent regressions unless SQL has explicit output that captures order.
- Row rendering truncation/limit at `zLine[4000]` intentionally converts very wide outputs into harness failures.
- The output tables are not cleared between input files, so per-file isolation is limited.
- The fixture is read-only, but fuzz SQL may attempt writes and transactions; rollback before each file reduces cross-case contamination.

## Test Signals

Success prints `<file>: <nStmt> stmts <nRow> rows ok` and exits with no SQLite memory leak. Failure signals include prepare/exec errors, optimized/non-optimized run failures, comparison mismatch with printed `opt` and `noopt` outputs, excessively long row output, and final memory-leak diagnostics.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/test/optfuzz.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/test/ossfuzz.c -->
# sources/storage-engines/sqlite/test/ossfuzz.c

## Purpose

`ossfuzz.c` is SQLite’s adapter for Google OSS-Fuzz. Its `LLVMFuzzerTestOneInput()` entry point interprets fuzz input as SQL, executes it against an in-memory SQLite database, and imposes resource limits to turn random inputs into useful engine coverage without unbounded time, memory, or output.

## Important APIs, Types, and Functions

- `LLVMFuzzerTestOneInput(const uint8_t *data, size_t size)` is the fuzz target entry point.
- `ossfuzz_set_debug_flags(unsigned x)` allows `ossshell.c` to enable optional debug output.
- Debug flags: `FUZZ_SQL_TRACE`, `FUZZ_SHOW_MAX_DELAY`, and `FUZZ_SHOW_ERRORS`. In this file, errors and max-delay are used; SQL trace is defined for interface compatibility but no trace callback is installed in the visible code.
- `FuzzCtx` holds the SQLite connection, cutoff time, progress-callback timing, callback count, and remaining exec callback row budget.
- `progress_handler()` stops execution after the cutoff time and records progress interval metrics.
- `block_debug_pragmas()` denies `PRAGMA vdbe_*` and `PRAGMA parser_trace`.
- `exec_handler()` consumes result values, frees formatted copies to exercise allocation paths, limits output rows, and delegates timeout checks.

## Control Flow

Inputs shorter than three bytes are ignored. If the second byte is newline, the first byte is a selector and the SQL begins after the newline; otherwise selector defaults to `0xfd`. The harness initializes SQLite and opens `fuzz.db` with `SQLITE_OPEN_MEMORY`, so no disk database is used.

It installs a progress handler every ten virtual-machine instructions, sets a ten-second cutoff, caps VDBE op count, caps LIKE/GLOB pattern length to 250, applies a 20MB hard heap limit, caps value length to 50KB, enables or disables foreign keys from selector bit 0, denies debug pragmas with an authorizer, and derives the maximum number of result rows from remaining selector bits. It then copies the fuzz bytes into a nul-terminated SQL string, optionally calls `sqlite3_complete()`, executes the SQL with `sqlite3_exec()`, optionally prints errors, clears `temp_store_directory`, closes the connection, and optionally prints progress statistics.

## State and Persistence Behavior

State is process-local and per-input except for the global debug bitmask and SQLite global hard heap limit. The database is memory-only. The harness intentionally resets `PRAGMA temp_store_directory` before close to avoid fuzz SQL leaving global temp-directory state behind.

## Dependencies and Integration Points

It uses the libFuzzer/OSS-Fuzz `LLVMFuzzerTestOneInput` ABI and SQLite public APIs. `ossshell.c` links against this file for local replay. It depends on progress callbacks unless SQLite is built with `SQLITE_OMIT_PROGRESS_CALLBACK`; it conditionally calls `sqlite3_complete()` unless omitted.

## Risks and Edge Cases

- `sqlite3_hard_heap_limit64(20000000)` is global; embedding this harness in a larger process can affect later SQLite users.
- The selector protocol means corpus inputs can encode both SQL and harness settings; tools that strip leading bytes can change behavior.
- The SQL trace debug flag is exposed but not implemented in this file, so local users may expect more tracing than they get.
- The progress callback depends on wall-clock VFS time, which can vary across environments.
- Resource limits are deliberately low enough to avoid timeouts, so they may mask bugs that require larger values.

## Test Signals

OSS-Fuzz treats crashes, sanitizer findings, leaks, assertion failures, and timeouts as failures. Local replay signals include optional SQL errors, progress callback counts, max callback delay, and successful return from `LLVMFuzzerTestOneInput()` without process failure.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/test/ossfuzz.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/test/ossshell.c -->
# sources/storage-engines/sqlite/test/ossshell.c

## Purpose

`ossshell.c` is a local replay shell for `ossfuzz.c`. It reads one or more files from the command line and passes their bytes to `LLVMFuzzerTestOneInput()`, making it possible to reproduce OSS-Fuzz corpus entries or crashes outside the OSS-Fuzz infrastructure.

## Important APIs, Types, and Functions

- Declares `int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size)` from `ossfuzz.c`.
- Declares `ossfuzz_set_debug_flags(unsigned)` and mirrors the debug flag constants from `ossfuzz.c`.
- `main()` parses debug options, reads files into a reusable heap buffer, invokes the fuzz target, and reports `ok` per file.
- Supported options: `--show-errors`, `--show-max-delay`, and `--sql-trace`.

## Control Flow

The command line is scanned left to right. Options update `mDebug` and call `ossfuzz_set_debug_flags()` immediately. Non-option arguments are opened, sized with `fseek()`/`ftell()`, read into `zBuf` via `realloc()`, and passed to `LLVMFuzzerTestOneInput()`. The shell prints `<filename>... ok` around each successful replay. File open/read failures increment `nErr` or exit on allocation failure.

## State and Persistence Behavior

The program itself does not persist data. It allocates and reuses a single input buffer and delegates all SQLite/fuzzer state to `ossfuzz.c`. Debug flags persist across later file arguments once enabled.

## Dependencies and Integration Points

It links with `ossfuzz.c` and SQLite headers. It is a developer tool for corpus minimization/replay workflows and for debugging with optional error and timing output.

## Risks and Edge Cases

- `--sql-trace` sets a flag that `ossfuzz.c` does not visibly act on, so it may be a compatibility stub.
- `realloc(zBuf, sz)` with `sz==0` can return NULL and be treated as fatal, though zero-length files are not useful fuzz cases.
- `ftell()` is stored in `size_t` after file sizing; extremely large files are not guarded beyond allocation failure.
- Files are read as raw bytes, so no text encoding or nul-termination is applied by this shell.

## Test Signals

Success prints `ok` for each input and returns zero if all files were read. Non-zero exit indicates unknown options, unreadable files, read errors, allocation failure, or a crash/failure inside `LLVMFuzzerTestOneInput()`. Debug options should produce additional diagnostics from `ossfuzz.c`.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/test/ossshell.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/test/run-wordcount.sh -->
# sources/storage-engines/sqlite/test/run-wordcount.sh

## Purpose

`run-wordcount.sh` is a regression/performance comparison wrapper for SQLite’s `wordcount` test program. It runs the same input through multiple mutation/query modes and compares summarized output between rowid and WITHOUT ROWID database variants.

## Important APIs, Commands, and Files

- Requires a source text filename plus optional additional `wordcount` arguments.
- Invokes `./wordcount --timer --summary` with database files `wcdb1.db` and `wcdb2.db`.
- Exercises `--insert`, `--replace`, `--select`, `--query`, and `--delete`, with and without `--without-rowid`.
- Uses `cmp -s`, `diff -u`, `mv`, `rm`, and shell redirection.
- Temporary outputs: `wc-out.txt` and `wc-baseline.txt`.

## Control Flow

The script validates that at least one argument was supplied. It creates a baseline summary using rowid `--insert`, then repeats the same input using WITHOUT ROWID `--insert` and reports a diff if summaries differ. It then repeats rowid/WITHOUT ROWID comparisons for `--replace` and `--select` against the original insert baseline.

For `--query`, it first runs against `wcdb1.db` and makes that the query baseline, then compares a WITHOUT ROWID query against `wcdb2.db`. For `--delete`, it similarly builds a rowid delete baseline and compares WITHOUT ROWID delete output. It removes temp DBs and output files at the end.

## State and Persistence Behavior

The script creates and deletes `wcdb1.db`, `wcdb2.db`, `wc-out.txt`, and `wc-baseline.txt` in the current directory. It repeatedly deletes DBs before build-style operations but preserves them across query/delete comparison pairs where needed.

## Dependencies and Integration Points

It depends on a built `wordcount` executable in the current directory and on the caller supplying input text/options accepted by that program. It integrates with SQLite’s test/performance tooling by checking that rowid and WITHOUT ROWID implementations produce identical summaries across supported operation modes.

## Risks and Edge Cases

- The script compares full summary output while `--timer` is enabled; if timings are included in the compared summary, nondeterministic runtime differences can cause false diffs unless `wordcount --summary` omits variable timing from stdout.
- It prints no success message; successful comparisons write `hi` to `/dev/null`.
- Temporary filenames are fixed and can collide with concurrent runs.
- Cleanup only happens on the normal path; early command failures can leave temporary files.

## Test Signals

The primary failure signal is `ERROR:` followed by a unified diff. Silence indicates success. Useful tests cover representative text input, each operation mode, rowid versus WITHOUT ROWID summaries, and cleanup of temporary files.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/test/run-wordcount.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/test/sessionfuzz.c -->
# sources/storage-engines/sqlite/test/sessionfuzz.c

## Purpose

`sessionfuzz.c` is a standalone fuzzing program for SQLite’s session/changeset module. It can generate seed changesets and apply fuzzed changesets, including all entries in a SQL Archive, against a deterministic in-memory database while checking for crashes, corruption, and memory leaks.

## Important APIs, Types, and Functions

- The file includes `sqlite3.c` directly with `SQLITE_DEBUG=1`, `SQLITE_THREADSAFE=0`, `SQLITE_ENABLE_SESSION=1`, `SQLITE_ENABLE_PREUPDATE_HOOK=1`, and `SQLITE_ENABLE_DESERIALIZE=1`.
- `zFillSql` populates the base tables with varied integer, real, text, blob, NULL, and WITHOUT ROWID data.
- `aDbBytes[]` embeds the base SQLite database containing tables `t1`, `t2`, `t3`, and `t4`.
- `sqlarUncompressFunc()` implements SQL Archive decompression with zlib unless `OMIT_ZLIB` is defined.
- `runSql()`, `writeFile()`, `readFile()`, `makeChangeset()`, `db_reset()`, and `fileTail()` provide harness I/O and database reset utilities.
- `conflictCall()` always returns `SQLITE_CHANGESET_OMIT`, causing conflicting changes to be skipped during apply.
- Session APIs used include `sqlite3session_create()`, `sqlite3session_attach()`, `sqlite3session_changeset()`, `sqlite3session_delete()`, and `sqlite3changeset_apply()`.

## Control Flow

`main()` opens a `memdb` in-memory SQLite connection and resets it from `aDbBytes`. In `setup` mode, it runs `zFillSql`, creates a session on `main`, attaches all tables, then performs a sequence of modifications and writes cumulative changesets `c1.txt`, `c2.txt`, and `c3.txt`.

In `run` mode, it loops over input files. Ordinary files are read as raw changesets, applied inside a transaction with `sqlite3changeset_apply()`, reported by return code, and rolled back. Files that look like SQLite databases (`nChgset >= 512` and header `SQLite format 3`) are treated as SQL Archives: they are deserialized into a second in-memory DB, `sqlar_uncompress()` is registered, every `sqlar` entry is selected and applied to the primary DB inside a transaction, and each case is rolled back. Verbose mode prints per-entry status; non-verbose mode prints case counts.

After setup or run work, the program executes `PRAGMA integrity_check`, reports integrity failures, closes the database, and exits non-zero on SQLite memory leaks.

## State and Persistence Behavior

The base DB lives in process memory via `sqlite3_deserialize()`. `setup` mode persists seed files `c1.txt`, `c2.txt`, and `c3.txt` in the current directory. `run` mode does not persist applied changes because every apply occurs inside `BEGIN`/`ROLLBACK`. SQL Archive input buffers are handed to a read-only deserialized DB with `SQLITE_DESERIALIZE_FREEONCLOSE`; ordinary changeset buffers are freed after use.

## Dependencies and Integration Points

The harness depends on SQLite session, preupdate hook, deserialize, debug, and optional zlib support. It integrates with AFL-style workflows: generate seeds with `sessionfuzz setup`, run `sessionfuzz run @@`, minimize corpora, and optionally package cases into SQL Archive databases for replay. It uses SQLite’s `memdb` VFS name for in-memory deserialize behavior.

## Risks and Edge Cases

- `SQLITE_DEBUG` is forced on while user-provided `SQLITE_DEBUG` is undefined first, so assertions are part of fuzz signal.
- SQL Archive detection is heuristic and based on size plus header; a malformed SQLite-looking file can reach deserialize/query code.
- `conflictCall()` omits all conflicts, so the harness prioritizes parser/apply robustness over semantic conflict resolution coverage.
- In the SQL Archive branch, `pChgset` is reassigned to SQLite-owned column blob memory; ownership differs from ordinary-file inputs and must not be freed manually in that path.
- zlib omission changes SQL Archive behavior by returning compressed data directly, which may reduce coverage for compressed archives.
- `setup` changesets are cumulative from one session, so later seed files include earlier changes unless session semantics reset internally.

## Test Signals

Expected setup output is creation of `c1.txt`, `c2.txt`, and `c3.txt` with no errors. Expected run output is one return code per changeset or `<n> cases, 0 crashes` for archives, followed by successful integrity check and zero SQLite memory usage. Fuzz failures include crashes/assertions, non-`ok` integrity checks, unexpected SQL errors, zlib decompression failures, changeset apply crashes, and memory leak reports.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/test/sessionfuzz.c -->
