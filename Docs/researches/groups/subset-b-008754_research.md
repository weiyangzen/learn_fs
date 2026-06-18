# subset-b-008754 Research

Grouped research report for the subset B work item. Each source section preserves the original source path and is wrapped for reconciliation into the final per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/session/sqlite3session.h -->
# sources/storage-engines/sqlite/ext/session/sqlite3session.h

## Purpose

This header is the public C API contract for SQLite's session extension when `SQLITE_ENABLE_SESSION` is enabled. It declares opaque session, changeset iterator, changegroup, and rebaser handles and documents the lifecycle and behavior of capturing database mutations, producing changesets or patchsets, iterating and applying them, merging them, rebasing local work after remote conflict resolution, and using streaming variants for large inputs. It is documentation-heavy and intentionally exposes behavior guarantees, memory ownership, conflict callback rules, and feature flags rather than implementation details.

## Important APIs, Types, and Constants

The main opaque types are `sqlite3_session`, `sqlite3_changeset_iter`, `sqlite3_changegroup`, and `sqlite3_rebaser`. Session lifecycle and capture APIs include `sqlite3session_create()`, `sqlite3session_delete()`, `sqlite3session_object_config()`, `sqlite3session_enable()`, `sqlite3session_indirect()`, `sqlite3session_attach()`, `sqlite3session_table_filter()`, `sqlite3session_changeset()`, `sqlite3session_patchset()`, `sqlite3session_diff()`, `sqlite3session_isempty()`, and `sqlite3session_memory_used()`.

Iterator APIs include `sqlite3changeset_start()`, `sqlite3changeset_start_v2()`, `sqlite3changeset_next()`, `sqlite3changeset_op()`, `sqlite3changeset_pk()`, `sqlite3changeset_old()`, `sqlite3changeset_new()`, `sqlite3changeset_conflict()`, `sqlite3changeset_fk_conflicts()`, and `sqlite3changeset_finalize()`. Transform and merge APIs include `sqlite3changeset_invert()`, `sqlite3changeset_concat()`, `sqlite3changegroup_new()`, `sqlite3changegroup_schema()`, `sqlite3changegroup_add()`, `sqlite3changegroup_add_change()`, `sqlite3changegroup_output()`, and `sqlite3changegroup_delete()`.

Apply APIs are `sqlite3changeset_apply()`, `sqlite3changeset_apply_v2()`, and `sqlite3changeset_apply_v3()`. The v2 and v3 forms add rebase output and flags. Key flags are `SQLITE_CHANGESETSTART_INVERT`, `SQLITE_CHANGESETAPPLY_NOSAVEPOINT`, `SQLITE_CHANGESETAPPLY_INVERT`, `SQLITE_CHANGESETAPPLY_IGNORENOOP`, `SQLITE_CHANGESETAPPLY_FKNOACTION`, and `SQLITE_CHANGESETAPPLY_NOUPDATELOOP`. Conflict reasons are `SQLITE_CHANGESET_DATA`, `SQLITE_CHANGESET_NOTFOUND`, `SQLITE_CHANGESET_CONFLICT`, `SQLITE_CHANGESET_CONSTRAINT`, and `SQLITE_CHANGESET_FOREIGN_KEY`; conflict handler return values are `SQLITE_CHANGESET_OMIT`, `SQLITE_CHANGESET_REPLACE`, and `SQLITE_CHANGESET_ABORT`.

Rebase APIs are `sqlite3rebaser_create()`, `sqlite3rebaser_configure()`, `sqlite3rebaser_rebase()`, and `sqlite3rebaser_delete()`. Streaming variants replace contiguous changeset buffers with `xInput` and `xOutput` callbacks for apply, concat, invert, start, session output, changegroup I/O, and rebase. Global/session configuration is exposed through `sqlite3session_config(SQLITE_SESSION_CONFIG_STRMSIZE, ...)`, and changegroup output mode can be set with `sqlite3changegroup_config(SQLITE_CHANGEGROUP_CONFIG_PATCHSET, ...)`.

The tail adds one-at-a-time change construction APIs for changegroups: `sqlite3changegroup_change_begin()`, typed value functions for int64, null, double, text, and blob, and `sqlite3changegroup_change_finish()`.

## Control Flow and Behavior

A normal capture flow is: create a session for a database name, optionally configure rowid or size tracking before attaching tables, attach one table or all tables, perform writes while the session is enabled, and then emit a changeset or patchset. The header explains that sessions store primary-key information and original row values on first touch, then query current database state at output time to decide whether each tracked row is an INSERT, UPDATE, DELETE, or no-op. Primary key changes are represented as delete plus insert, and rows with NULL primary-key columns are ignored. Tables are grouped in attach order.

Apply flow validates compatible target tables, optionally filters by table or per-change iterator depending on API version, applies each operation inside a savepoint by default, and invokes conflict handlers for data mismatches, missing rows, duplicate primary keys, constraint failures, and final foreign-key violations. Conflict handlers may omit, replace where allowed, or abort. The v2/v3 APIs may also produce a rebase blob when conflicts occurred, which later configures a rebaser for local changesets.

Changegroups combine multiple changesets or patchsets by primary key. Rules are explicitly defined for every pair of existing and incoming operation types, such as insert plus delete canceling out, update plus update merging column changes, and delete plus insert becoming update or no-op. The schema API allows combining compatible but different-column-count changesets against a configured database schema.

## State and Persistence

The header itself persists no state, but it defines several stateful object lifecycles. A session is attached to a `sqlite3*` and uses the preupdate hook, so it must be deleted before the database handle closes and cannot coexist with another preupdate hook on the same connection. Session state includes enabled/disabled capture, indirect-change marking, attached tables, optional table filter, object configuration, and accumulated row records. Changeset and patchset buffers are heap allocations owned by callers and freed with `sqlite3_free()`. Iterators borrow their input buffers until finalized. Changegroups and rebasers own accumulated in-memory state until deleted. Streaming callbacks move persistence responsibility to caller-managed input/output contexts.

## Dependencies and Integration Points

The header includes `sqlite3.h` and is guarded by `SQLITE_ENABLE_SESSION`. It integrates deeply with SQLite preupdate hooks, SQLite value objects, database schema inspection, conflict callbacks, SQLite error codes, savepoints, `sqlite3_log()`, and foreign-key enforcement. It also defines compatibility expectations for downstream bindings, Tcl tests, WASM builds with session enabled, and applications that sync databases through changesets.

## Risks and Edge Cases

Major risks are misuse of object lifetimes, assuming sessions can coexist with arbitrary preupdate hooks, failing to free output buffers, using iterators after their input buffer has gone away, returning illegal conflict actions, or applying patchsets where old values are required for conflict detection. `sqlite3changeset_invert()` explicitly warns that invalid input has undefined results. Global `sqlite3session_config()` is not threadsafe and must run before session objects exist. `SQLITE_SESSION_OBJCONFIG_SIZE` and `SQLITE_SESSION_OBJCONFIG_ROWID` must be modified before table attachment. Streaming callbacks can leave iterators in persistent error states if they fail.

## Test Signals

The related `test_session.c` file exercises nearly all declared APIs through Tcl commands, including streaming and non-streaming paths, conflict handler behavior, range and misuse errors for iterator accessors, rebase flow, changegroup APIs, and constructed changes. The WASM makefile enables `SQLITE_ENABLE_SESSION` in full-featured builds, so this header is also part of the JS/WASM API build surface.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/session/sqlite3session.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/session/test_session.c -->
# sources/storage-engines/sqlite/ext/session/test_session.c

## Purpose

This file is a Tcl test extension for the SQLite session module, compiled only when `SQLITE_TEST`, `SQLITE_ENABLE_SESSION`, and `SQLITE_ENABLE_PREUPDATE_HOOK` are all defined. It wraps session, changeset, changegroup, apply, rebase, and streaming APIs as Tcl commands so the SQLite test suite can generate, inspect, mutate, apply, validate, and combine changesets from Tcl scripts.

## Important APIs, Types, and Functions

`TestSession` stores a `sqlite3_session*`, Tcl interpreter, and optional table-filter script. `TestStreamInput` models chunked input for streaming APIs using a byte buffer, current offset, and maximum chunk size. `TestSessionsBlob` accumulates streaming output into a reallocating buffer. `TestConflictHandler` keeps conflict and filter Tcl scripts for apply callbacks. `TestChangegroup` and `TestChangeIter` wrap changegroup and iterator handles as Tcl command objects.

Key command implementations are `test_sqlite3session()`, `test_session_cmd()`, `testSqlite3changesetApply()`, `test_sqlite3changeset_invert()`, `test_sqlite3changeset_concat()`, `test_sqlite3session_foreach()`, `test_sqlite3rebaser_create()`, `test_rebaser_cmd()`, `test_changeset()`, `test_sqlite3session_config()`, `test_sqlite3changegroup()`, `test_changegroup_cmd()`, `test_sqlite3changeset_start()`, and `test_iter_cmd()`. `TestSession_Init()` registers the Tcl command surface.

The helper `sql_exec_changeset()` is copied from the session documentation and verifies that the documented example remains executable. `sqlite3_test_changeset()` performs structural sanity checks on changesets and patchsets, especially update old/new value presence rules.

## Control Flow

The session command flow starts with `sqlite3session CMD DB-HANDLE DB-NAME`, which resolves a Tcl SQLite database command into `sqlite3*`, creates a session, enables size accounting by default after verifying it is initially disabled, and registers a new Tcl object command. That object supports subcommands for `attach`, `changeset`, `patchset`, `delete`, `enable`, `indirect`, `isempty`, `table_filter`, `diff`, `memory_used`, `changeset_size`, and `object_config`. Changeset and patchset output can use either normal APIs or streaming APIs depending on the global Tcl variable `sqlite3session_streams`.

Apply flow is centralized in `testSqlite3changesetApply()`, parameterized by version 1, 2, or 3. It parses flags for v2/v3, copies the Tcl byte array into exact malloc-sized memory for ASAN-sensitive tests, wires optional filter scripts, and invokes normal or streaming apply APIs. The conflict callback builds a Tcl list containing operation type, table, conflict type, old/new rows, and conflicting row when available. It also deliberately calls accessor APIs in invalid modes or ranges to assert `SQLITE_MISUSE` and `SQLITE_RANGE`.

Iterator and foreach flow copies the changeset, starts an iterator with optional inversion and optional streaming, converts each change to a Tcl structure via `testIterData()`, and either drives a Tcl script or exposes a Tcl iterator command with `next`, `data`, and `finalize` subcommands. Rebaser flow wraps create/configure/rebase/delete and supports streaming rebase. Changegroup flow wraps schema, add, output, add_change, patchset config, and the one-at-a-time change construction APIs.

## State and Persistence

Most persistent state is attached to Tcl commands through `objClientData` and cleaned by destructors. `test_session_del()` decrements filter script references and deletes the session. `test_rebaser_del()`, `test_changegroup_del()`, and `test_iter_del()` release their SQLite handles. Streaming state is transient per command call, except a streaming iterator stores its own copy of the input bytes after the `TestChangeIter` struct so callbacks remain valid for the iterator lifetime. Several APIs intentionally allocate with plain `malloc()` instead of Tcl or SQLite allocators to make ASAN and valgrind catch small overreads.

## Dependencies and Integration Points

The file depends on `sqlite3session.h`, `tclsqlite.h`, Tcl object APIs, SQLite test helpers such as `sqlite3ErrName()`, and the session extension. It is tightly integrated with SQLite's Tcl test runner: database handles are looked up from Tcl command names, errors are surfaced as Tcl result strings, and callback scripts are evaluated in the global interpreter context. It also integrates with SQLite fault injection by allocating inside `testStreamInput()` so streaming callbacks can fail with `SQLITE_NOMEM`.

## Risks and Edge Cases

The test harness intentionally exercises undefined or edge behaviors, so it is not application code. Tcl script callbacks can background errors, conflict callbacks can return numeric values outside symbolic strings, and many paths assume assertions are active in debug tests. Streaming behavior depends on `sqlite3session_streams`; setting it changes the API path without changing Tcl commands. Exact-sized byte copies are important for memory-safety tests. `test_iter_del()` finalizes the iterator, while the `finalize` subcommand also finalizes and nulls it before deleting the Tcl command; this relies on Tcl deletion ordering not to double-finalize a live pointer.

## Test Signals

This file is itself the test signal for `sqlite3session.h`. It validates documented examples, normal and streaming changeset creation, inversion, concatenation, apply v1/v2/v3, rebase output, iterator inspection, conflict handler accessor legality, changegroup merging and construction, and session global configuration. The `assert_changeset_is_ok()` macro adds structural validation in debug builds after many generated outputs.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/session/test_session.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/wasm/GNUmakefile -->
# sources/storage-engines/sqlite/ext/wasm/GNUmakefile

## Purpose

This GNU makefile is SQLite's canonical JS/WASM build driver. It is aimed at SQLite project development and release packaging, not general application builds. It builds development and optimized WASM artifacts, JS API bundles, worker helper files, tester applications, speedtest builds, fiddle builds, distribution zips, testing deployments, documentation copies, and npm bundle artifacts. It assumes a Linux-like environment with GNU tools, bash, Emscripten, and optionally wabt `wasm-strip`.

## Important Targets, Variables, and Macros

Primary targets include `all`, optimization rebuild targets `o0`, `o1`, `o2`, `o3`, `os`, `oz`, release targets `dist` and `snapshot`, cleanup targets, `for-testing`, `push-testing`, `update-docs`, `httpd`, `push-fiddle`, and `npm`. Build directories are `dir.dout` for deliverables (`jswasm`) and `dir.tmp` for intermediates (`bld`). `sqlite3.c` defaults to the canonical amalgamation or SEE variant. `SQLITE_OPT.common` and `SQLITE_OPT.full-featured` define compile-time SQLite features; full builds include session, preupdate hook, FTS5, RTREE, metadata, dbstat, dbpage, bytecode, and other extensions.

Reusable build macros include `b.mkdir@`, `b.cp`, `b.c-pp.shcmd`, `b.c-pp.target`, `b.strip-js-emcc-bindings`, and `b.call.patch-export-default`. Generated build logic comes from the local `mkwasmbuilds` helper, which creates `.wasmbuilds.make` and fills in build names, output names, c-pp define sets, and many per-build rules.

Key Emscripten controls include `emcc.WASM_BIGINT`, `emcc.MEMORY64`, `emcc_opt`, `emcc_opt_full`, `emcc.jsflags`, `emcc.INITIAL_MEMORY`, `sqlite3.js.init-func`, exported function list generation, runtime method exports, imported memory, modularization, dynamic-execution disabling, table growth, stack size, and undefined symbol reporting.

## Control Flow

At startup the makefile determines whether it is cleaning. Non-clean builds require `config.make`, bash, `emcc`, and optionally `wasm-strip`. Optimized targets require `wasm-strip`; development builds warn but can continue without it. It then resolves source paths, detects SEE, chooses bare-bones or full-featured SQLite options, builds local tools such as `version-info`, `stripccomments`, `c-pp`, and `mkwasmbuilds`, and includes generated make rules.

The JS API assembly flow creates a license/version file, a JSON build-version initializer, concatenates ordered API JS components into a post-js input, preprocesses C-preprocessor-style JS sources with `c-pp`, and uses emcc pre/post JS hooks to produce module outputs. Supplementary worker/promiser/OPFS proxy files are generated separately for vanilla, ESM, and bundler-friendly forms.

Test and benchmark flow builds `speedtest1` variants and `tester1` variants covering main-thread script, worker script, ESM main thread, ESM worker, and 32/64-bit pointer modes. Fiddle flow compiles shell/fiddle-specific builds and optional jquery.terminal assets. Release flow runs distribution scripts or forces clean optimized npm builds and zips stable downstream filenames.

## State and Persistence

Persistent outputs are primarily under `ext/wasm/jswasm`, plus tester/demo/fiddle files in the wasm directory tree and distribution zip files. Intermediates live under `ext/wasm/bld` and generated local tools live in the build directory. `.wasmbuilds.make` is generated and made read-only until cleaned. `config.make` is a required configured state file and is removed by `distclean`. `clean` removes `CLEAN_FILES`, `dir.dout`, and `dir.tmp`; `distclean` also removes `DISTCLEAN_FILES`.

## Dependencies and Integration Points

The makefile integrates with the top-level SQLite tree for `sqlite3.c`, `sqlite3.h`, `shell.c`, `speedtest1.c`, `tool/version-info.c`, and `tool/stripccomments.c`. It depends on Emscripten settings semantics, wabt `wasm-strip`, bash, GNU sed/awk/grep, InfoZip, rsync/ssh for deployment, and optional local documentation or jquery.terminal checkouts. It also integrates with downstream `sqlite/sqlite-wasm` npm expectations by keeping npm filenames stable.

## Risks and Edge Cases

The file contains several explicit fragility points: Emscripten minification can break exported WASM names unless `-g3` plus `wasm-strip` are used; `b.strip-js-emcc-bindings` relies on generated JS text patterns; `b.call.patch-export-default` works around Emscripten ESM default export behavior; ordering around `.wasmbuilds.make` is fragile; high optimization levels are slow; `STRICT_JS` and `STRICT` are disabled or avoided due to Emscripten issues; missing `wasm-strip` makes optimized release-quality builds unusable. Bare-bones builds intentionally remove features including session support. Custom `sqlite3.c` paths must not contain spaces.

## Test Signals

The build produces the `tester1` suite, worker tester pages, speedtest builds, `for-testing` deployment bundle, fiddle debug builds, and npm bundle zip listing. Full-featured WASM builds define `SQLITE_ENABLE_SESSION` and `SQLITE_ENABLE_PREUPDATE_HOOK`, connecting this build file to the session header and Tcl test surface. Build success across `all`, `for-testing`, `dist`, and `npm` is the primary signal, while browser execution of tester pages validates runtime behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/wasm/GNUmakefile -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/wasm/SQLTester/GNUmakefile -->
# sources/storage-engines/sqlite/ext/wasm/SQLTester/GNUmakefile

## Purpose

This small GNU makefile compiles SQLTester-format `.test` files into a JavaScript module that can be imported by the browser or worker test runner. It converts each test script into a byte array literal, aggregates all scripts into `test-list.mjs`, and gzips that module for delivery.

## Important Targets and Variables

The default `all` target depends on `test-list.mjs.gz` when test inputs are present. `tests.dir` is the first existing directory among local `tests` and `../../jni/src/tests`. `tests.all` is all `*.test` files in that directory. `bin.touint8array` is a local C helper compiled from `touint8array.c`. Outputs are `test-list.mjs` and `test-list.mjs.gz`; both are cleaned by `clean`.

## Control Flow

If test files exist, make first builds `touint8array`, then writes `test-list.mjs` by emitting `export default [` followed by one object per sorted test file. Each object contains the base filename and a `content` property generated by piping the test file through `touint8array`. The gzip target compresses the module. If no test inputs exist, the makefile prints guidance to symlink `./tests` to a SQLTester-format test directory and exits with failure.

## State and Persistence

The generated `test-list.mjs` embeds test file content as byte arrays, so the runtime test runner does not need to fetch individual `.test` files. `test-list.mjs.gz` is the compressed deployable form. `clean` removes generated outputs and the helper binary; `distclean` also removes dummy/distclean patterns and editor backups.

## Dependencies and Integration Points

The makefile depends on bash, the system C compiler, the local `touint8array.c`, gzip, and either local SQLTester tests or the SQLite JNI SQLTester test directory. Its output is imported by `SQLTester.run.mjs`, which creates `TestScript` instances from the generated object list.

## Risks and Edge Cases

The generated JavaScript is built with shell `echo` and assumes test filenames do not contain characters needing JSON escaping beyond the simple base-name insertion. Test file ordering is lexical via `sort`, making runs deterministic. If `tests.dir` is empty, the recipe fails at make-parse recipe context as intended. Very large test suites produce large JS modules because every byte is materialized as decimal text.

## Test Signals

A successful `all` build proves that the helper compiled, input tests were found, `test-list.mjs` was generated, and gzip succeeded. Runtime validation comes from `SQLTester.run.mjs` importing `test-list.mjs` and executing each generated `TestScript`.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/wasm/SQLTester/GNUmakefile -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/wasm/SQLTester/SQLTester.mjs -->
# sources/storage-engines/sqlite/ext/wasm/SQLTester/SQLTester.mjs

## Purpose

This ES module is a JavaScript/WASM port of SQLite's SQLTester framework. It imports the SQLite WASM module, defines a parser and executor for SQLTester `.test` scripts, manages SQLite database handles, executes SQL through the C API, compares result buffers against expected command output, and exports a namespace used by `SQLTester.run.mjs` and other test harnesses.

## Important APIs, Classes, and Functions

The exported namespace contains `SQLTester`, `TestScript`, `Command`, `Outer`, exception classes, `Util`, and the initialized `sqlite3` object. `tryInstallVfs()` can install a registered VFS as the default, though OPFS installation is currently behind disabled conditionals. `Util` provides `unlink()`, `argvToString()`, UTF-8 encode/decode helpers, and a WASM-wrapped `sqlite3__wasm_SQLTester_strglob()` glob matcher.

`Outer` is a buffered output/logger abstraction with verbosity support. `SQLTester` owns test scripts, input and result buffers, metrics, the current null rendering, column-name output mode, database slots, default database initialization SQL, and execution helpers. `TestScript` owns byte content, parser cursor state, module/testcase metadata, directive handling, command body fetching, line decoding, and command dispatch.

Command subclasses implement SQLTester directives: `--close`, `--column-names`, `--db`, `--glob`, `--notglob`, `--open`, `--new`, `--null`, `--print`, `--result`, `--json`, `--run`, `--tableresult`, `--json-block`, `--testcase`, and `--verbosity`. `CommandDispatcher` lazily instantiates and caches command handlers by name.

## Control Flow

Module initialization awaits `sqlite3ApiInit()` from `/jswasm/sqlite3.mjs`, then prepares helper enums and classes. A caller creates `SQLTester`, adds `TestScript` instances, and calls `runTests()`. For each script, `SQLTester` resets buffers and database handles, runs the script, catches `SQLTesterException` subclasses, updates metrics, reports per-file timing and pass/fail state, then deletes the default test database.

`TestScript.run()` decodes lines from a `Uint8Array`, checks for unsupported directives, dispatches command lines beginning with `--`, and appends non-command lines to the SQL input buffer. Commands generally consume the accumulated SQL with `takeInputBuffer()`, execute it through `SQLTester.execSql()`, and compare or ignore results depending on command type.

`execSql()` prepares and steps one or more SQL statements using low-level SQLite WASM C APIs. It encodes SQL to UTF-8, allocates scoped WASM memory for statement and tail pointers, repeatedly calls `sqlite3_prepare_v3()`, steps rows, appends escaped or raw column text to the result buffer, optionally includes column names, finalizes statements, and returns the SQLite result code. Table-result commands fetch a body up to `--end` and compare each output row to a glob or JSON string.

## State and Persistence

Runtime state is held in JavaScript private fields. Database state uses up to seven SQLite handles stored in `#db.list`, with slot 0 as the default `test.db`. `reset()` clears SQL buffers, closes all databases, resets metrics for the current script, restores null output to `nil`, disables column names, and resets the current DB slot. `#setupInitialDb()` deletes and recreates `test.db` on demand. `Util.unlink()` calls `sqlite3__wasm_vfs_unlink` through WASM. No browser storage is used unless the disabled OPFS VFS block is re-enabled.

## Dependencies and Integration Points

The module depends on `/jswasm/sqlite3.mjs`, Web APIs `TextDecoder` and `TextEncoder`, SQLite WASM helpers (`wasm.xWrap`, `pstack`, `scopedAllocCall`, pointer helpers), SQLite C APIs, and the C-side helper symbols `sqlite3__wasm_vfs_unlink` and `sqlite3__wasm_SQLTester_strglob`. It integrates with `SQLTester.run.mjs`, generated `test-list.mjs`, and the broader wasm build that must export the required C symbols and JSON functionality used by the tests.

## Risks and Edge Cases

The parser rejects C-preprocessor lines, triple-dash directives, mixed module directives, unsupported required properties, and newline-pipe combinations. Required-property support is effectively disabled because `#checkRequiredProperties()` currently returns false immediately, making such directives incompatible. `currentDb(...args)` appears to reference an undefined `id` variable when setting the current DB from arguments; most command paths use `currentDbId()` instead. `ResultRowMode` defines `ONLINE`, but command code passes `ResultRowMode.ONELINE`; because `execSql()` only checks for `NEWLINE`, this still behaves as one-line output but is a naming mismatch. Output comparison only uses text values via `sqlite3_column_text()`, so binary result fidelity is not represented. Large scripts are decoded line by line and large generated test modules can increase memory pressure.

## Test Signals

`SQLTester.run.mjs` includes a sanity script that exercises most commands and then runs generated tests from `test-list.mjs`. Successful execution reports SQLite version, pointer size, per-script test counts, failures, and total time. The module also exposes detailed verbosity output for parser and SQL execution diagnostics.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/wasm/SQLTester/SQLTester.mjs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/wasm/SQLTester/SQLTester.run.mjs -->
# sources/storage-engines/sqlite/ext/wasm/SQLTester/SQLTester.run.mjs

## Purpose

This module is the executable harness for `SQLTester.mjs`. It imports the SQLTester namespace and the generated test list, creates a tester, runs an embedded sanity-check script, loads all generated SQLTester scripts, and supports both direct main-thread execution and worker-driven execution.

## Important APIs and Functions

The module imports `ns` from `./SQLTester.mjs` and `allTests` from `./test-list.mjs`. It exposes `ns.sqlite3` on `globalThis.sqlite3` for debugging. Local helpers include `log()`, buffered `out`/`outln` backed by `ns.Outer`, `affirm()`, and `runTests()`. The `sqt` instance is a configured `ns.SQLTester` with console logging, verbosity 1, and an initial embedded `TestScript`.

## Control Flow

At load time, the module builds a sanity-check SQLTester script covering print, close, OOM no-op, database selection, new database creation, null rendering, result comparison, glob/notglob, non-fatal run errors, JSON comparison, table-result comparison, JSON block comparison, column-name toggling, and close behavior. `runTests()` then either runs a disabled direct-debug branch or, in normal operation, appends every generated test object from `allTests` as a `TestScript`, clears the imported array, and calls `sqt.runTests()`. A `finally` block resets tester state after the run.

If running in a worker global scope, the module installs an `onmessage` handler. On `run-tests`, it runs tests and posts `tests-end` with metrics. It redirects tester logs to `stdout` messages and sends an initial `is-ready` message. Outside a worker, it runs tests immediately.

## State and Persistence

State is primarily the singleton `sqt` tester and its metrics. Generated test content is released by setting `allTests.length = 0` after scripts are added. Worker mode communicates state through structured messages: `is-ready`, `stdout`, and `tests-end`. Database files and SQLite state are owned by `SQLTester.mjs` and reset after execution.

## Dependencies and Integration Points

This file depends on `SQLTester.mjs`, generated `test-list.mjs`, browser or worker globals, and console logging. It is the runtime counterpart to `SQLTester/GNUmakefile`, which creates the imported test list. In worker mode it integrates with whichever test page or controller posts `run-tests` and consumes stdout and metrics messages.

## Risks and Edge Cases

Because it imports `test-list.mjs` statically, the generated module must exist before this runner loads. The sanity script uses some disabled incompatible directive examples in comments, not as active commands. In worker mode, unknown messages are only logged. If `runTests()` throws before posting metrics, the `finally` in the worker case still posts `tests-end`, but fatal module-load errors before handler setup would not. Main-thread mode runs immediately on import, which is appropriate for a test application but surprising for library-style reuse.

## Test Signals

The embedded sanity script is the first signal that command parsing and basic SQL execution work. Running generated tests from `allTests` is the main regression signal. Worker clients can treat `is-ready` as load success, `stdout` as progress, and `tests-end` metrics as completion evidence.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/wasm/SQLTester/SQLTester.run.mjs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/wasm/SQLTester/touint8array.c -->
# sources/storage-engines/sqlite/ext/wasm/SQLTester/touint8array.c

## Purpose

This tiny C utility converts stdin bytes into a JavaScript array literal of decimal byte values. It is used by `SQLTester/GNUmakefile` to embed `.test` files into `test-list.mjs` as `Uint8Array`-compatible content.

## Important Functions

The only function is `main()`. It reads stdin with `fgetc()`, prints an opening `[`, prints each byte as an unsigned decimal-style integer separated by commas, inserts a newline every 30 bytes for readability, prints the closing `]`, and returns zero.

## Control Flow

The program initializes a byte counter, return code, column width, and current character. It loops until `fgetc(stdin)` returns `EOF`. For each byte, it emits a comma unless this is the first value, emits a newline at each `colWidth` boundary, and prints the byte value. There is no option parsing and command-line arguments are ignored.

## State and Persistence

The utility maintains only local process state and writes all output to stdout. It creates no files itself. Persistence is provided by the makefile redirecting stdout into `test-list.mjs`.

## Dependencies and Integration Points

It depends only on the C standard I/O header. It is compiled by `SQLTester/GNUmakefile` into `./touint8array` and used in a shell loop over sorted test files. Its output is embedded directly into JavaScript object literals consumed by `SQLTester.run.mjs` and `SQLTester.mjs`.

## Risks and Edge Cases

The code uses `int ch` so it can distinguish all byte values from `EOF`. It prints byte values as `%d`, which is valid for the `fgetc()` result range. It does not report read errors separately from EOF, does not escape or annotate data, and does not wrap output in `new Uint8Array(...)`; callers must use it in a context where a plain array is acceptable. Extremely large inputs produce very large decimal-text output.

## Test Signals

A simple signal is that piping any file through the utility yields syntactically valid bracketed comma-separated numbers. The makefile's successful generation of `test-list.mjs` and subsequent import by `SQLTester.run.mjs` validates integration.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/wasm/SQLTester/touint8array.c -->
