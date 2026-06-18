# subset-b-008732 Research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/configure -->
# sources/storage-engines/sqlite/configure

## Purpose
`configure` is the repository entrypoint for SQLite's autosetup-based configuration system. It is intentionally tiny: it finds the adjacent `autosetup` directory, exports the wrapper path, and replaces the shell process with the Tcl interpreter selected by `autosetup-find-tclsh` running the `autosetup` script.

## Important APIs, Types, And Functions
There are no shell functions or local option parsers in this wrapper. The important variables are `dir`, computed from `dirname "$0"` with `/autosetup` appended, and `WRAPPER`, exported as the original script path. The only command path it owns is the final `exec "\`"$dir/autosetup-find-tclsh"\`" "$dir/autosetup" "$@"`, which preserves all user arguments for autosetup.

The placeholder `#@@INITCHECK@@#` is an autosetup distribution marker rather than executable behavior in this checked-in file.

## Control Flow
Execution is linear. The shell resolves the autosetup directory relative to the invoked script, exports `WRAPPER`, asks `autosetup-find-tclsh` to locate an appropriate Tcl shell, and then `exec`s that Tcl shell with the autosetup program and original arguments. Because `exec` is used, no post-configure shell cleanup path exists in this wrapper.

## State And Persistence Behavior
The wrapper persists no files itself. Its only process-level state mutation is exporting `WRAPPER` for the autosetup Tcl code. All generated build files, cache behavior, compiler probing, and option persistence belong to `autosetup`, not this script.

## Dependencies
It depends on POSIX `/bin/sh`, `dirname`, the sibling `autosetup/autosetup-find-tclsh` helper, and the sibling `autosetup/autosetup` Tcl script. It also assumes the checked-out tree keeps the wrapper and `autosetup` directory in their expected relative layout.

## Integration Points
This is the command users or build automation run as `./configure`. It hands off to SQLite's autosetup infrastructure, which then configures Makefiles and feature options for the rest of the SQLite source tree.

## Risks And Edge Cases
The relative path computation follows the invocation path, so moving the wrapper away from its sibling `autosetup` directory breaks configuration. If `autosetup-find-tclsh` is missing, not executable, or cannot locate Tcl, the shell fails before any autosetup diagnostics can run. The wrapper deliberately does not validate arguments; unknown options are diagnosed by autosetup after handoff.

## Test Signals
Useful checks are execution-oriented: run `./configure --help` from the SQLite source root and from alternate working directories, verify it finds Tcl through `autosetup-find-tclsh`, and verify all arguments arrive unchanged at autosetup. There is no local unit-test seam in this four-line script.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/configure -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/expert/expert.c -->
# sources/storage-engines/sqlite/ext/expert/expert.c

## Purpose
`expert.c` is the standalone command-line frontend for SQLite's expert extension. It opens a database, feeds one or more SQL statements into `sqlite3expert`, runs index analysis, and prints candidate indexes, per-query recommended indexes, and query plans.

## Important APIs, Types, And Functions
`main()` owns the full program lifecycle: argument parsing, database open, expert-handle creation, SQL ingestion, analysis, reporting, and cleanup.

`readSqlFromFile()` reads an entire SQL file into an SQLite-allocated buffer, passes it to `sqlite3_expert_sql()`, and frees the buffer. It reports file-open and short-read failures through `sqlite3_mprintf()` strings owned by the caller.

`usage()`, `option_requires_argument()`, and `option_integer_arg()` are small CLI helpers. Options are matched by prefix using `sqlite3_strnicmp()`, with optional GNU-style `--` reduced to `-` by advancing `zArg` one character. Supported options are `-sql`, `-file`, `-verbose`, and `-sample`.

The SQLite expert API calls used here are `sqlite3_expert_new()`, `sqlite3_expert_sql()`, `sqlite3_expert_config(EXPERT_CONFIG_SAMPLE)`, `sqlite3_expert_analyze()`, `sqlite3_expert_count()`, `sqlite3_expert_report()`, and `sqlite3_expert_destroy()`.

## Control Flow
The final positional argument is treated as the database path. The program rejects missing arguments and a database argument beginning with `-`, opens the database with `sqlite3_open()`, and constructs an expert handle. It then scans all preceding arguments. `-file` consumes the next token and loads SQL from disk, `-sql` consumes the next token as SQL text, `-sample` clamps indirectly through the library config call, and `-verbose` controls how much report text is printed.

After all inputs are loaded, `sqlite3_expert_analyze()` performs the expensive work. On success, verbosity above zero prints the global candidate index list, then each analyzed query is reported. For each query it optionally prints the original SQL, prints recommended `CREATE INDEX` statements or `(no new indexes)`, and prints the post-candidate `EXPLAIN QUERY PLAN` output. On any non-OK return, the program prints the expert error string.

## State And Persistence Behavior
Program state is process-local except for opening and reading the target database and any SQL file. The frontend itself does not create indexes in the user's database; candidate indexes are created inside the expert implementation's in-memory analysis database. The sample percentage controls how much table data the expert library scans to synthesize `sqlite_stat1`.

The error string `zErr` is SQLite-allocated and freed at exit. The expert object and database connection lifetimes are cleanly bounded, although `sqlite3_close(db)` is not called explicitly after `sqlite3_expert_destroy()`.

## Dependencies
The file depends on the SQLite C API, standard C file and memory headers, and `sqlite3expert.h`. It assumes the expert extension was built with virtual table support, because the implementation is compiled out under `SQLITE_OMIT_VIRTUALTABLE`.

## Integration Points
This frontend is the executable wrapper around `ext/expert/sqlite3expert.c`. Build systems can compile it with the SQLite library and expert implementation to provide a `sqlite3_expert`-style utility. Its output format directly reflects `EXPERT_REPORT_CANDIDATES`, `EXPERT_REPORT_INDEXES`, `EXPERT_REPORT_SQL`, and `EXPERT_REPORT_PLAN`.

## Risks And Edge Cases
Option matching is prefix-based, so short prefixes such as `-ver` are accepted and future option names could become ambiguous. `option_integer_arg()` uses `atoi()`, so malformed numeric options silently become zero. `readSqlFromFile()` allocates `nIn+1` bytes based on `ftell()` without validating negative `ftell()` results or allocation failure before `fread()`, which makes unusual file errors or very large files riskier. The CLI does not enforce that at least one SQL statement was supplied; an empty analysis simply reports zero query sections if the library accepts it.

## Test Signals
CLI tests should cover `-sql`, `-file`, single-dash and double-dash spellings, missing option arguments, invalid database paths, sample values below zero and above one hundred, and verbosity zero versus default output. Behavioral tests can compare recommended index output against known queries using the Tcl expert test bindings or the standalone executable.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/expert/expert.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/expert/sqlite3expert.c -->
# sources/storage-engines/sqlite/ext/expert/sqlite3expert.c

## Purpose
`sqlite3expert.c` implements SQLite's index-advisor engine. Given a live database connection and SQL workload, it mirrors schema into in-memory databases, compiles workload statements against instrumented virtual tables to observe constraints and ordering, generates candidate indexes, optionally synthesizes `sqlite_stat1`, asks SQLite's planner which candidates it would use, and exposes reports through the public `sqlite3expert` API.

## Important APIs, Types, And Functions
The exported API is `sqlite3_expert_new()`, `sqlite3_expert_config()`, `sqlite3_expert_sql()`, `sqlite3_expert_analyze()`, `sqlite3_expert_count()`, `sqlite3_expert_report()`, and `sqlite3_expert_destroy()`.

`struct sqlite3expert` holds the user database `db`, two in-memory databases `dbm` and `dbv`, table metadata, observed scans, observed writes, loaded statements, candidate-index hash state, the sample percentage, and the final candidate report string. `dbv` hosts expert virtual tables that observe planner constraints during prepare. `dbm` hosts a copied schema plus proposed indexes and statistics for final query-plan evaluation.

Core internal data types are `IdxTable` and `IdxColumn` for schema metadata, `IdxScan` for one observed table scan, `IdxConstraint` for equality, range, and order terms, `IdxWrite` for DML operations that may fire triggers, `IdxStatement` for each workload statement, and `IdxHash`/`IdxHashEntry` for deduplicating candidate indexes and mapping generated index names to SQL text and optional stat strings.

The virtual table module uses `expertConnect()`, `expertBestIndex()`, `expertFilter()`, cursor methods, and `idxRegisterVtab()`. `expertBestIndex()` is the instrumentation point: it records usable equality/range constraints and ORDER BY columns into `IdxScan` whenever SQLite prepares workload SQL against `dbv`.

Candidate generation is centered on `idxCreateCandidates()`, `idxCreateFromWhere()`, `idxCreateFromCons()`, and `idxFindCompatible()`. The code builds equality-prefix indexes, variants with range terms, and variants extended with ORDER BY terms, while avoiding candidates compatible with existing indexes in `dbm`.

Statistics and reporting are handled by `idxPopulateStat1()`, `idxPopulateOneStat1()`, `idxFindIndexes()`, and `idxAppendText()`. `idxFindIndexes()` parses `EXPLAIN QUERY PLAN` detail strings to identify which generated candidate index names the planner selected for each statement.

## Control Flow
`sqlite3_expert_new()` allocates the handle, opens `dbv` and `dbm` as `:memory:` databases, enables trigger EQP on `dbm`, registers dummy collation callbacks, optionally mirrors user-defined scalar/aggregate/window functions, copies the user's schema into `dbm`, creates an instrumented virtual-table schema in `dbv`, and installs an authorizer on `dbv` to notice writes.

`sqlite3_expert_sql()` may be called repeatedly before analysis. For each complete SQL statement, it first prepares against the real database to validate syntax and dependencies, then prepares against `dbv`. Preparing against expert virtual tables invokes `xBestIndex`, which appends `IdxScan` objects describing equality constraints, range constraints, ORDER BY columns, collations, and non-primary-key columns. The statement text returned by `sqlite3_sql()` is copied into an `IdxStatement`. If any statement in the supplied buffer fails, newly added scans and statements from that call are rolled back to the saved list heads.

`sqlite3_expert_analyze()` first processes writes and triggers. The authorizer records direct INSERT/UPDATE/DELETE operations as `IdxWrite` entries. `idxProcessTriggers()` recreates affected tables and triggers in `dbv`, renames the table to a unique temporary name, prepares synthetic DML, and thereby discovers scans inside trigger bodies. It loops because trigger processing may discover more writes.

After scan collection, `idxCreateCandidates()` walks every `IdxScan`. Equality constraints are collected without duplicate columns; range and ORDER BY tails are appended when useful; `idxCreateFromCons()` renders a `CREATE INDEX` statement, generates a deterministic hash-derived name, checks for collisions against schema object names, creates the index in `dbm`, and records the candidate in `hIdx`.

If sampling is enabled, `idxPopulateStat1()` runs `ANALYZE`, enables writable schema, creates helper SQL functions, and computes stat1 rows for all indexes in `dbm`. With `iSample==100`, it scans real user tables. With partial sampling, `idxBuildSampleTable()` creates a temp table in `dbv` using `sqlite_expert_sample()` to keep an approximate percentage of rows, then statistics are derived from the sample. `idxPopulateOneStat1()` sorts values according to each index key, uses `sqlite_expert_rem()` to compare current and previous key values, computes cardinality estimates, writes rows to `sqlite_stat1`, and stores candidate stat strings back into `hIdx`.

Finally, candidate report text is assembled, `idxFindIndexes()` runs `EXPLAIN QUERY PLAN` for each workload statement against `dbm`, matches `USING INDEX` and `USING COVERING INDEX` names back to generated candidates, and records per-statement recommended index SQL plus plan detail. A successful analyze sets `bRun`, after which `sqlite3_expert_report()` can return report buffers.

## State And Persistence Behavior
The expert object owns all analysis state. It never creates recommended indexes in the caller's database. It does read real schema and, depending on sample mode, may read real table data. Schema copies, candidate indexes, sampled rows, helper functions, and generated `sqlite_stat1` data live in the in-memory `dbm` or `dbv` connections.

`sqlite3_expert_sql()` is transactional with respect to each input buffer's internal lists: on error, it frees scans/statements added by that call and restores prior list heads. After `sqlite3_expert_analyze()` runs, `bRun` prevents further SQL additions. On analysis error, the public header documents the handle as no longer useful except for destruction.

Memory ownership is manual and SQLite-allocator-based. Table, scan, constraint, write, statement, hash, candidate, and statistics buffers are released by `sqlite3_expert_destroy()` or by local cleanup helpers. Returned report strings are borrowed pointers owned by the expert handle and remain valid until destruction.

## Dependencies
This implementation depends deeply on SQLite internals exposed through the public extension API: virtual tables, `sqlite3_index_info`, `sqlite3_vtab_collation()`, authorizer callbacks, schema pragmas, introspection pragmas, `pragma_function_list()`, `PRAGMA table_xinfo`, `PRAGMA index_list`, `PRAGMA index_xinfo`, `EXPLAIN QUERY PLAN`, `ANALYZE`, writable `sqlite_stat1`, custom collations, and user-defined SQL functions.

Compilation is excluded when `SQLITE_OMIT_VIRTUALTABLE` is defined. User-defined function mirroring is compiled only when schema and introspection pragmas are available. The file also uses SQLite allocation, formatting, randomness, and keyword APIs.

## Integration Points
The public header and standalone CLI call this API directly. The test harness in `test_expert.c` wraps the same API for Tcl. Inside SQLite, the code integrates with the query planner by deliberately preparing SQL against virtual tables and letting normal `xBestIndex` calls expose planner-visible constraints. It integrates with trigger analysis through SQLite's authorizer and prepare-time trigger compilation.

The candidate indexes and plans are ordinary SQLite SQL text and EQP detail strings, so downstream tools can present them without linking to private data structures.

## Risks And Edge Cases
`idxNewConstraint()` allocates `sizeof(IdxConstraint) * nColl + 1` instead of `sizeof(IdxConstraint) + nColl + 1`, which overallocates for non-empty collation names and is wasteful but generally safe. Candidate index naming retries at most fifty schema-name collisions and maps failure to `SQLITE_BUSY_TIMEOUT` with a specific public error path. EQP parsing is string-based and depends on detail text containing `USING INDEX` or `USING COVERING INDEX`, so changes to planner output wording can hide selected candidates.

The unique temporary table name is assumed not to collide with user objects; the file documents that conflicting user names can cause trigger analysis to ignore triggers on that table. Sampling uses randomness and approximate target ratios, so partial-stat recommendations may be nondeterministic. Dummy collations and dummy UDFs assert if executed; the design assumes they are needed only for prepare-time compatibility, not VDBE execution. Some file-local helper functions such as `dummyCompare`, `useDummyCS`, and UDF registration functions are not `static`, which widens symbol visibility in non-amalgamation builds.

## Test Signals
Strong tests should cover equality, range, ORDER BY, DESC, collation, covering-index, and existing-index compatibility cases; plans with no new indexes; partial and zero sampling; views; triggers fired by INSERT/UPDATE/DELETE; custom collations; user-defined scalar, aggregate, and window functions; virtual tables with missing modules; quoted identifiers and SQL keywords; and candidate-name collision handling. Existing direct test signal comes from the Tcl wrapper in `test_expert.c`, which allows SQLite's Tcl test suite to create expert handles, add SQL, analyze, count statements, and inspect each report channel.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/expert/sqlite3expert.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/expert/sqlite3expert.h -->
# sources/storage-engines/sqlite/ext/expert/sqlite3expert.h

## Purpose
`sqlite3expert.h` is the public C API for SQLite's expert extension. It declares the opaque expert handle, configuration entrypoint, SQL-loading and analysis functions, report accessors, report/config constants, and destructor used by both the standalone CLI and test bindings.

## Important APIs, Types, And Functions
`typedef struct sqlite3expert sqlite3expert;` keeps implementation details private.

`sqlite3_expert_new(sqlite3 *db, char **pzErr)` constructs an analysis object over an existing SQLite connection and returns an SQLite-allocated error string on failure.

`sqlite3_expert_config(sqlite3expert *p, int op, ...)` currently supports `EXPERT_CONFIG_SAMPLE`, an integer percentage controlling whether analysis uses no stat1 data, full table scans, or sampled table rows.

`sqlite3_expert_sql(sqlite3expert *p, const char *zSql, char **pzErr)` parses complete SQL statements from a buffer and adds them to the workload. It must be called before analysis and is all-or-nothing for each buffer.

`sqlite3_expert_analyze(sqlite3expert *p, char **pzErr)` performs candidate generation, statistics synthesis, and planner evaluation. After it runs, no more SQL can be added.

`sqlite3_expert_count()` returns the number of loaded statements. `sqlite3_expert_report()` returns one of `EXPERT_REPORT_SQL`, `EXPERT_REPORT_INDEXES`, `EXPERT_REPORT_PLAN`, or `EXPERT_REPORT_CANDIDATES`. `sqlite3_expert_destroy()` frees the handle.

## Control Flow
The intended lifecycle is explicit: create with `sqlite3_expert_new()`, optionally configure sampling, add SQL with one or more `sqlite3_expert_sql()` calls, run `sqlite3_expert_analyze()`, inspect counts and reports, then destroy the handle. Report calls are meaningful only after successful analysis. Statement-indexed report modes use zero-based statement numbers and return NULL for out-of-range indexes.

## State And Persistence Behavior
The header documents borrowed report-string ownership and SQLite-allocated error-string ownership. Callers free errors with `sqlite3_free()`, but must not free report pointers. The expert object owns all internal analysis state until `sqlite3_expert_destroy()`.

Sampling controls performance and recommendation fidelity. Values less than or equal to zero disable stat1 generation, values greater than or equal to one hundred use complete stat1 data, and intermediate values sample that percentage of rows. The API does not promise deterministic output for sampled analysis.

## Dependencies
The only required include is `sqlite3.h`. The API uses SQLite result codes, `sqlite3*`, SQLite memory allocation conventions, and variadic C calls for configuration.

## Integration Points
`expert.c` uses this API to implement the command-line tool. `test_expert.c` exposes it to Tcl tests. Embedders can call it directly when they want index recommendations for a workload without creating proposed indexes in the production database.

## Risks And Edge Cases
The variadic config function requires callers to pass the exact expected argument type for each op; misuse is not type-checked by the compiler. After `sqlite3_expert_analyze()` fails, the object is documented as no longer useful except for destruction. `sqlite3_expert_count()` may count statements rather than calls, so callers should not assume one SQL buffer maps to one report slot.

The comment for `sqlite3_expert_destroy()` says `sqlite3-expert_new()` instead of `sqlite3_expert_new()`, a documentation typo only. The report constants are stable integer values used by tests and wrappers.

## Test Signals
Header-level contract tests should verify lifecycle misuse (`sqlite3_expert_sql()` after analysis returns `SQLITE_MISUSE`), sample clamping through config, out-of-range report indexes returning NULL, NULL index reports for statements needing no new indexes, and error-message ownership on invalid SQL.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/expert/sqlite3expert.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/expert/test_expert.c -->
# sources/storage-engines/sqlite/ext/expert/test_expert.c

## Purpose
`test_expert.c` exposes the SQLite expert extension to SQLite's Tcl test harness when `SQLITE_TEST` is enabled. It lets Tcl tests create an expert handle from an existing Tcl SQLite connection and invoke the public expert API through Tcl subcommands.

## Important APIs, Types, And Functions
`TestExpert_Init()` registers the top-level Tcl command `sqlite3_expert_new` unless virtual table support is omitted.

`test_sqlite3_expert_new()` validates the Tcl argument count, resolves a Tcl database command to an `sqlite3*`, creates a unique Tcl command name like `sqlite3expert1`, calls `sqlite3_expert_new()`, and installs the command with `testExpertCmd()` as its dispatcher and `testExpertDel()` as its deletion callback.

`testExpertCmd()` implements `$expert sql SQL`, `$expert analyze`, `$expert count`, `$expert report STMT EREPORT`, and `$expert destroy`. It maps Tcl report names `sql`, `indexes`, `plan`, and `candidates` onto the public `EXPERT_REPORT_*` constants.

`dbHandleFromObj()` extracts the underlying `sqlite3*` from a Tcl SQLite command by reading `Tcl_CmdInfo.objClientData`. `testExpertDel()` destroys the expert handle when the Tcl command is deleted.

## Control Flow
Tcl creates a normal SQLite database command first. A test then calls `sqlite3_expert_new DB`, which creates an expert object and returns a new expert command name. Subsequent Tcl subcommands dispatch through `testExpertCmd()`. Successful `sql` and `analyze` calls return normal Tcl OK status with no additional result unless a report or count is requested. `count` sets an integer result. `report` validates both the statement number and report enum, calls `sqlite3_expert_report()`, and sets the Tcl result to that string. `destroy` deletes the command, which triggers `testExpertDel()` to free C state.

If an expert API returns a non-Tcl-OK code, `testExpertCmd()` prefers the expert error string; otherwise it uses `sqlite3ErrName(rc)` for a symbolic SQLite error. All expert error strings are freed after dispatch.

## State And Persistence Behavior
The Tcl command owns one `sqlite3expert*` through its client data. Deleting the Tcl command is the lifetime boundary. The static `iCmd` counter only ensures unique command names during a test process. The wrapper itself persists no files and does not mutate the database beyond whatever the underlying expert analysis reads or prepares.

## Dependencies
The file is compiled only under `SQLITE_TEST`. Most code is additionally excluded under `SQLITE_OMIT_VIRTUALTABLE`, matching the expert implementation's dependency on virtual tables. It depends on `sqlite3expert.h`, Tcl headers and APIs provided through `tclsqlite.h`, `assert.h`, `string.h`, and SQLite's test-only `sqlite3ErrName()` symbol for fallback error names.

## Integration Points
This is the bridge between SQLite's C expert API and Tcl-based regression tests. Test scripts can create real database schemas with the Tcl SQLite command, instantiate expert analysis against the same handle, add SQL, run analysis, and assert on report text without invoking the standalone `expert.c` program.

## Risks And Edge Cases
`dbHandleFromObj()` assumes the Tcl SQLite command's `objClientData` layout contains an `sqlite3**`, so it is coupled to SQLite's Tcl binding internals. `report` passes a possibly NULL `sqlite3_expert_report()` result to `Tcl_NewStringObj(zReport, -1)`; if Tcl does not tolerate NULL there, out-of-range reports or pre-analysis reports could crash rather than return an empty result. The wrapper has no subcommand for `sqlite3_expert_config()`, so Tcl tests using this binding cannot directly exercise sample configuration through the exposed command set.

## Test Signals
Direct tests should cover creation failure for nonexistent DB handles, subcommand arity errors, invalid report enum names, `count` after loading multiple statements, report values after analysis, destroy cleanup, and behavior when virtual table support is omitted. Broader signal comes from any SQLite Tcl tests that assert recommended indexes and plans through these commands.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/expert/test_expert.c -->
