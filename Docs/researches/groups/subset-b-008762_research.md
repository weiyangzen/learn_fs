# subset-b-008762 Research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/wasm/mkdist.sh -->
# sources/storage-engines/sqlite/ext/wasm/mkdist.sh

## Purpose
`mkdist.sh` builds the distributable SQLite JavaScript/WASM zip bundle from the wasm extension build directory. It drives the local Makefile to generate the demo, tester, worker, ESM, and optional 64-bit artifacts, copies the curated public files into a temporary distribution tree, strips comments from selected JavaScript files, then creates a versioned zip archive.

## Important APIs, Types, And Functions
This is a Bash release helper rather than a library. Important flags are `-64`, `-0`, `-1`, `--noclean`, `--snapshot`, and help. `die()` centralizes fatal exits. `fcp()` copies with preserved metadata and makes the destination writable. `scc()` invokes `tool/stripccomments`. The arrays `tgtFiles`, `fTop`, `fJ1`, `fJ2`, and `fW` define the release manifest and comment-stripping policy.

## Control Flow
The script parses arguments, locates `gmake` or `make`, applies default build name `sqlite-wasm`, and optionally appends a dated snapshot suffix. It optionally runs `make clean`, then builds version tooling, comment stripping, and the target files using `emcc_opt`. It recreates `d.dist`, copies top-level demos and common CSS/test utilities, copies wasm files from `jswasm/`, strips comments from selected generated JS/MJS files, asks `./version-info --download-version` for the release version, renames the temporary tree to `<buildName>-<version>`, zips sorted files, lists the archive, and prints the unzipped directory path.

## State And Persistence Behavior
The script deletes and recreates `d.dist`, the final versioned directory, and the final zip. It also invokes Make targets that may rewrite generated wasm/JS artifacts. `--snapshot` embeds the current date in the archive prefix. No source files are intentionally edited, but build outputs and release directories are replaced.

## Dependencies And Integration Points
Dependencies are Bash, GNU-compatible Make, `cp`, `chmod`, `rm`, `mkdir`, `find`, `sort`, `zip`, `unzip`, SQLite's wasm Makefile, `tool/stripccomments`, and `version-info`. It integrates with the canonical wasm build layout, including generated `jswasm` files, demos, `README-dist.txt`, `index-dist.html`, and optional 64-bit artifacts.

## Risks And Test Signals
Risks include unquoted array expansion for paths with spaces, destructive removal of local output directories, stale or missing Make targets, missing `zip`/`unzip`, and manifest drift when new distribution files are added elsewhere. Good validation is to run a normal and `-64` build, inspect `unzip -lv`, confirm no intended public file is missing, verify stripped JS remains loadable, and confirm the zip name uses the expected SQLite download version.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/wasm/mkdist.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/wasm/mkwasmbuilds.c -->
# sources/storage-engines/sqlite/ext/wasm/mkwasmbuilds.c

## Purpose
`mkwasmbuilds.c` is a Makefile-fragment generator for SQLite's canonical wasm build. It exists to keep complex generated GNU Make rules maintainable: instead of heavy `$(eval ...)` string construction inside Make, this C program emits the rules for library, speedtest, wasmfs, node, bundler, 64-bit, and fiddle builds.

## Important APIs, Types, And Functions
The central type is `BuildDef`, with base name, emoji log tag, wasm filename substitution target, c-pp defines, emcc flags, extra dependencies, environment, optional Make `ifeq`, and `BuildDefFlags`. `BuildDefs_map` enumerates `vanilla`, `vanilla64`, `esm`, `esm64`, `bundler`, `bundler64`, `speedtest1`, `speedtest164`, `node`, `node64`, and `wasmfs`. Important emitters are `mk_prologue()`, `mk_pre_post()`, `emit_compile_start()`, `emit_logtag()`, `emit_api_js()`, `mk_lib_mode()`, `emit_gz()`, `mk_fiddle()`, and `main()`.

## Control Flow
With no arguments, `main()` emits a prologue, rules for every build in `BuildDefs_map`, and fiddle rules. With arguments, it emits only named build sections, plus `prologue` if requested, and reports unknown names to stderr. `mk_prologue()` emits sanity checks for required Make variables, wasm-strip and wasm-opt helper macros, and common emcc command macros. `mk_lib_mode()` emits one complete build rule: output path variables, c-pp defines, environment, generated API JS, pre/post JS inputs, emcc invocation, importScripts regression guard, ESM export patching, wasm stripping/optimization, JS binding stripping, deliverable copy rules, alias targets, and all/more target membership. `mk_fiddle()` emits normal and debug fiddle builds and gzip rules.

## State And Persistence Behavior
The program itself only writes Makefile text to stdout and errors to stderr. The emitted Makefile rules create per-build output directories, generated pre/post JS files, JS API bundles, JS/MJS/WASM outputs, copied deliverables, gzip files, and optional patched JS references. Build selection state is encoded in flags such as `CP_JS`, `CP_WASM`, `F_ESM`, `F_64BIT`, `F_UNSUPPORTED`, `F_NODEJS`, and `F_WASMFS`.

## Dependencies And Integration Points
Compile-time dependencies are standard C headers and the Makefile variables/functions referenced in emitted text. Runtime integration assumes Emscripten, `c-pp-lite`, wasm-strip, optional wasm-opt, generated SQLite API sources, sqlite3 wasm C input, speedtest inputs, fiddle inputs, and Make helpers such as `b.c-pp.target`, `b.cp`, `b.mkdir@`, and `b.call.patch-export-default`.

## Risks And Test Signals
Risks center on emitted Make syntax, duplicated or missing dependencies, JS/WASM filename substitution, unsupported builds silently diverging, and Emscripten behavior changes. The code has a specific guard against reintroducing `importScripts()` into ESM/bundler outputs. Validation should compile the generator, regenerate the Makefile fragment, diff expected rules, run representative `b-vanilla`, `b-esm`, `b-speedtest1`, `b-fiddle`, and optional `wasmfs`/64-bit targets, and verify copied deliverables load in browser and worker contexts.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/wasm/mkwasmbuilds.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/wasm/scratchpad-wasmfs.mjs -->
# sources/storage-engines/sqlite/ext/wasm/scratchpad-wasmfs.mjs

## Purpose
`scratchpad-wasmfs.mjs` is a small manual smoke test for the experimental `sqlite3-wasmfs.mjs` build. It loads the wasmfs module in the main JS thread, checks whether persistent wasmfs/OPFS storage is mounted, opens a persistent database, and inserts/tallies rows.

## Important APIs, Types, And Functions
It imports `sqlite3InitModule` from `./jswasm/sqlite3-wasmfs.mjs`. `test1(db)` creates table `t`, runs a transaction, inserts a timestamp, and logs the row count. `runTests(sqlite3)` logs module/version details, calls `capi.sqlite3_wasmfs_opfs_dir()`, opens `new sqlite3.oo1.DB(persistentDir + '/foo.db')`, runs the test list, closes the database, and reports elapsed time.

## Control Flow
Module initialization returns a promise. On success, `runTests()` reads the `capi`, `oo1`, and `wasm` namespaces, discovers the persistent directory, opens `foo.db`, runs each test function with timing banners, closes the DB in `finally`, and prints total runtime. If no persistent directory is available, it logs an error but still attempts to continue with the returned path, making this primarily a developer scratchpad.

## State And Persistence Behavior
The script persists data in `foo.db` under the wasmfs OPFS mount returned by `sqlite3_wasmfs_opfs_dir()`. Repeated runs append rows to table `t`; it does not unlink the database. All other state is transient console logging and local timing.

## Dependencies And Integration Points
It depends on a browser context with ESM support, the experimental wasmfs build artifact, SQLite's `capi` and `oo1` APIs, and browser OPFS capabilities when persistence is expected. It is not a formal harness; it integrates as a local diagnostic page/script alongside the wasm distribution.

## Risks And Test Signals
Risks include running in an environment without OPFS/wasmfs support, path concatenation after a falsey persistent directory, and persistent row counts hiding clean-run assumptions. Useful test signals are successful module load, non-empty persistent directory logging, successful `foo.db` open, monotonic `count(*)`, no leaked open DB after `finally`, and no browser console exceptions.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/wasm/scratchpad-wasmfs.mjs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/wasm/speedtest1-wasmfs.mjs -->
# sources/storage-engines/sqlite/ext/wasm/speedtest1-wasmfs.mjs

## Purpose
`speedtest1-wasmfs.mjs` runs the native SQLite `speedtest1` wasm build against the experimental wasmfs OPFS mount. It is meant for browser/worker-style benchmarking of persistent storage and forwards log/error messages to the parent via `postMessage()`.

## Important APIs, Types, And Functions
It imports `sqlite3InitModule` from `./jswasm/sqlite3-wasmfs.mjs`. `wMsg()`, `log()`, and `logErr()` wrap parent messages. `wasmfsDir(wasmUtil, dirName='/opfs')` caches OPFS availability and calls `sqlite3__wasm_init_wasmfs`. `runTests(sqlite3)` wraps `sqlite3__wasm_vfs_unlink`, builds speedtest argv from URL `flags`, removes any supplied `--vfs`, adds default flags when no URL flags exist, appends `--big-transactions` and a persistent DB filename, then invokes `wasm_main`.

## Control Flow
After module initialization with print hooks, `runTests()` checks the wasmfs OPFS directory. If unavailable, it reports an error and exits. Otherwise it prepares argv, unlinks the benchmark DB before and after execution, logs warnings about long runtime, and invokes `wasm.xCall('wasm_main', argc, argv)` inside a short `setTimeout()` so initial messages reach the UI before the synchronous benchmark begins.

## State And Persistence Behavior
The benchmark database is `/opfs/speedtest1.db` when persistence is available. The script intentionally unlinks the file before execution and again after completion to keep benchmark runs isolated. Scoped WASM allocations for argv are pushed before building arguments and popped after `wasm_main()` returns.

## Dependencies And Integration Points
It depends on the wasmfs build exporting `sqlite3__wasm_init_wasmfs`, `sqlite3__wasm_vfs_unlink`, and `wasm_main`, browser OPFS interfaces, URL query parameters, and a parent page that understands `log` and `logErr` message types. It integrates with SQLite's speedtest1 wasm Make target and browser benchmarking pages.

## Risks And Test Signals
Risks include symbol-name drift (`sqlite3__wasm_init_wasmfs` versus older spellings), blocking the browser during `wasm_main`, URL flags overriding benchmark comparability, `--memdb` making the DB filename irrelevant, and cleanup failures masking persistence bugs. Good signals are successful persistent mount logging, clean DB unlinking, expected speedtest stdout/stderr, correct argv in logs, scoped allocation cleanup, and no leftover DB file after completion.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/wasm/speedtest1-wasmfs.mjs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/wasm/speedtest1-worker.js -->
# sources/storage-engines/sqlite/ext/wasm/speedtest1-worker.js

## Purpose
`speedtest1-worker.js` is a classic worker wrapper for running the `speedtest1` wasm application from a browser UI. It imports the generated `speedtest1.js`, initializes the SQLite module, optionally installs the OPFS SAHPool VFS, runs `wasm_main()` with requested CLI flags, and posts structured status/log/results back to the page.

## Important APIs, Types, And Functions
`wasmfsDir(wasmUtil)` probes browser OPFS handles and calls `sqlite3_wasm_init_wasmfs('/opfs')` when available. `mPost()` posts `{type,data}` messages. `runSpeedtest(cliFlagsArray)` builds `argv`, rewrites `--vfs opfs-sahpool` to the configured real SAHPool VFS name, installs `sqlite3.installOpfsSAHPoolVfs()` when needed, invokes `App.wasm.xCall('wasm_main', ...)`, and sends `run-start`/`run-end`. `globalThis.onmessage` accepts `run`.

## Control Flow
The worker chooses the speedtest JS URL from `sqlite3.dir`, imports it, wires logging into `App.logBuffer`, initializes the Emscripten module with print/status hooks, stores `App.sqlite3`, `App.wasm`, and `App.pDir`, posts `ready`, and lists registered VFSes. Each `run` message executes one benchmark with isolated scoped allocations and reports errors through `error` messages.

## State And Persistence Behavior
The worker keeps module state in the `App` object, including cached wasm utilities, a log buffer, the persistent directory, and a cached `$SAHPoolUtil` on the sqlite3 namespace. Benchmark DB files are placed under the wasmfs OPFS mount. SAHPool installation uses a named VFS, `initialCapacity: 3`, `clearOnInit: true`, and verbosity. Scoped argv memory is popped in `finally`.

## Dependencies And Integration Points
It depends on generated `speedtest1.js`, browser Workers, Emscripten's module initialization, SQLite wasm exports, OPFS browser APIs, optional `installOpfsSAHPoolVfs`, and a UI controller that sends `run` and handles `ready`, `stdout`, `stderr`, `load-status`, `run-start`, `run-end`, and `error`.

## Risks And Test Signals
Risks include missing OPFS, stale `sqlite3.dir`, unsupported SAHPool installation, CLI flag ordering, cross-run retained SAHPool state, and long synchronous `wasm_main` calls blocking the worker. Strong test signals are `ready`, correct pointer/heap logs, successful VFS list, benchmark start/end messages, proper SAHPool rename/install logs when requested, and no unhandled worker message types.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/wasm/speedtest1-worker.js -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/wasm/split-speedtest1-script.sh -->
# sources/storage-engines/sqlite/ext/wasm/split-speedtest1-script.sh

## Purpose
`split-speedtest1-script.sh` converts a single `speedtest1 --script` SQL output file into one SQL file per test block. It is a developer utility for inspecting or replaying individual speedtest1 tests.

## Important APIs, Types, And Functions
The script is a compact Bash pipeline. It requires one positional argument, extracts test numbers with `grep -e '^-- begin test'` and `cut -d' ' -f4`, computes an output directory from the input file path, then loops over test numbers. Each output file is named `speedtest1-%03d.sql`, and `sed -n` extracts from the matching `-- begin test N` line through the exact `-- end test N` line.

## Control Flow
If the input argument is missing, Bash parameter expansion aborts. If no begin markers are parsed, it prints an error and exits 1. Otherwise it writes each extracted block and prints a tab-separated mapping of test number to generated SQL file.

## State And Persistence Behavior
The script writes output SQL files next to the input file, overwriting existing files with matching names. It does not modify the input. Output content is fully determined by begin/end marker pairs in the speedtest script.

## Dependencies And Integration Points
Dependencies are Bash, `grep`, `cut`, `printf`, and `sed`. It integrates with `speedtest1 --script` output format and any downstream SQL replay or diff tooling that consumes the generated per-test files.

## Risks And Test Signals
Risks include marker-format drift, missing end markers, input paths whose first component is not the desired output directory, and unescaped test numbers in the sed address if the format changes. Test by running it against a known speedtest script, verifying the reported file count matches begin markers, checking a few extracted files include both boundary comments, and confirming generated SQL executes independently where expected.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/wasm/split-speedtest1-script.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/wasm/test-opfs-vfs.js -->
# sources/storage-engines/sqlite/ext/wasm/test-opfs-vfs.js

## Purpose
`test-opfs-vfs.js` is a browser worker-style testing ground for SQLite's OPFS VFS. It loads `jswasm/sqlite3.js`, opens an OPFS database, verifies persistence, exercises basic transactions, and sanity-checks internal OPFS utility helpers.

## Important APIs, Types, And Functions
The main function is `tryOpfsVfs(sqlite3)`. It checks `sqlite3.opfs`, finds the `opfs` VFS via `sqlite3_vfs_find`, wraps it as `sqlite3_vfs`, optionally unlinks the DB when URL parameter `delete` is present, opens `new sqlite3.oo1.OpfsDb(dbFile,'ct')`, executes table setup/inserts, and uses `sqlite3.opfs` utilities: `unlink`, `entryExists`, `randomFilename`, `mkdir`, and recursive unlink.

## Control Flow
The script imports the generated sqlite3 loader with `importScripts()`, initializes the module, then calls `tryOpfsVfs()`. The test deletes the database only when requested, checks for existing persistent content, performs a transaction inserting three timestamp-derived values, logs row count, runs OPFS utility filesystem checks under a random temporary directory, and closes the DB in `finally`.

## State And Persistence Behavior
The database `my-persistent.db` persists in OPFS across runs unless `?delete` is supplied. Temporary OPFS directories named `/sqlite3-opfs-<random>` are created and removed during utility checks. The test uses SQLite transactions for table writes and explicitly closes the database.

## Dependencies And Integration Points
It depends on Worker globals, `importScripts`, `jswasm/sqlite3.js`, OPFS-capable browser APIs, the private `sqlite3.opfs` namespace retained for tests, and `sqlite3.oo1.OpfsDb`. It integrates as a standalone manual test page/worker for the OPFS VFS.

## Risks And Test Signals
Risks include relying on private `sqlite3.opfs` APIs, browser OPFS availability and permissions, stale persistent DB content, and cleanup failures in nested directory deletion. Passing signals are an `opfs` VFS pointer, successful `OpfsDb` open, persistent schema count on second run, increasing row count, successful mkdir/idempotent mkdir, failed unlink of non-empty directory, successful recursive cleanup, and no unclosed DB.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/wasm/test-opfs-vfs.js -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/wasm/tester1.c-pp.js -->
# sources/storage-engines/sqlite/ext/wasm/tester1.c-pp.js

## Purpose
`tester1.c-pp.js` is the main functional and regression harness for the SQLite WASM JavaScript API. It is preprocessed by `c-pp` so the same source can produce classic script and ES module variants. It can run in the UI thread or a worker, and it validates core C API bindings, WASM utility helpers, `oo1` DB/Stmt wrappers, VFSes, UDFs, virtual tables, storage backends, hooks, sessions, OPFS, SAHPool, SEE-gated paths, and selected bug reports.

## Important APIs, Types, And Functions
The file defines a mini framework in `TestUtil`: `assert`, `mustThrow`, `mustThrowMatching`, `throwIf`, `throwUnless`, `TestGroup`, `addGroup`, `addTest`, `runTests`, and `checkHeapSize`. Predicate helpers include `isUIThread()`, `isWorker()`, `haveWasmCTests()`, and `hasOpfs()`. Shared test helpers include `T.seeBaseCheck()` for SEE encryption checks and `T.opfsCommon` methods for OPFS/OPFS-WL sanity, import/export, and utility APIs. It initializes `sqlite3InitModule`, sets `__isUnderTest`, stores `capi` and `wasm`, and exposes `S` for local debugging.

## Control Flow
Startup configures logging to DOM nodes or `postMessage`, defines all test groups, imports/initializes sqlite3, logs version/VFS/pointer information, then runs groups sequentially. Each group can be skipped by predicate; each test receives the sqlite3 namespace and a per-group state object. Failures abort the queue, mark the UI or worker result as failed, and force a heap-size report. The groups cover basic config/error constants, WASM allocators and typed memory helpers, struct binding, pstack, randomness, DB/Stmt lifecycle, `exec`/select helpers, authorizer, metadata, db export/import, scalar/aggregate/window UDFs, ATTACH and read-only behavior, C-side test exports, JS virtual-table modules, collations, kvvfs, hooks, auto-extension, session changesets, OPFS/OPFS-WL, OPFS SAHPool, miscellaneous statement APIs, interrupt/error-message APIs, and specific regression reports.

## State And Persistence Behavior
Most tests use transient DBs, but some touch persistent browser stores: kvvfs in session/local/transient storage, OPFS files, OPFS-WL files, SAHPool file pools, and optional SEE-encrypted files. The harness carefully closes DBs/statements in `finally`, uses `db.onclose` cleanup callbacks for installed functions/structs/modules, restores pstack/scoped allocations, removes temporary VFSes, and unlinks OPFS/kvvfs files where appropriate. `localStorage` stores the UI log-order checkbox state.

## Dependencies And Integration Points
It depends on the generated sqlite3 JS/WASM loader, browser DOM or Worker APIs, c-pp substitution (`@sqlite3.js@`, `target:es6-module`, query expansion), optional BigInt/MEMORY64 support, optional compile flags (`SQLITE_WASM_ENABLE_C_TESTS`, FTS5, vtab, session, window, hooks, OPFS, SAHPool, SEE), and many SQLite JS API namespaces: `capi`, `wasm`, `oo1`, `vtab`, `kvvfs`, `opfs`, and `installOpfsSAHPoolVfs`.

## Risks And Test Signals
This file is intentionally broad, so risks include environment-sensitive skips hiding regressions, reliance on private test-only APIs, long synchronous tests in browsers, persistent browser state contaminating results, incomplete cleanup after early failure, and c-pp query/conditional output drift. Strong signals are a final PASS in both UI and worker modes, expected skip messages for unavailable optional features, stable assertion counts for a given build, no leaked statements or open DBs, no unexpected heap growth reports, successful OPFS/SAHPool cleanup, and regression tests passing for referenced forum/issues.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/wasm/tester1.c-pp.js -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/wasm/tests/opfs/concurrency/test.js -->
# sources/storage-engines/sqlite/ext/wasm/tests/opfs/concurrency/test.js

## Purpose
`tests/opfs/concurrency/test.js` is the UI coordinator for OPFS concurrency stress testing. It launches multiple workers against the same OPFS database, collects progress and pass/fail messages, and renders test output into the page.

## Important APIs, Types, And Functions
The script defines DOM logging helpers, `wait()`, URL-derived `options`, a `workers` array with `post()` and `counts`, `calcTime()`, `checkFinished()`, `workers.onmessage()`, and the launch button handler. It builds quick links for common combinations of `interval`, `iterations`, `workers`, `vfs`, `opfsVerbose`, and `unlock-asap`.

## Control Flow
On load, it prepares log rendering and option parsing from script and page URL arguments. Clicking `#gogogo` removes the button, constructs `worker.js` URL arguments, launches the requested number of workers, gives the first worker responsibility for optional DB unlinking unless `no-unlink` is set, then assigns a shared message handler. Once all workers report `loaded`, it records start time and broadcasts `run`. It records `finished` and `failed` counts and reports aggregate status when all workers are done.

## State And Persistence Behavior
The UI stores no database state itself. It persists log-order preference in `localStorage`. Test state is worker count, loaded/pass/fail counters, start time, and DOM output. The shared database state is created and mutated by workers in OPFS.

## Dependencies And Integration Points
It depends on a browser DOM containing `#gogogo`, `#test-output`, `#cb-log-reverse`, and `#testlinks`, plus `worker.js` in the same directory. It integrates with the worker message protocol: `loaded`, `stdout`, `stderr`, `error`, `finished`, and `failed`.

## Risks And Test Signals
Risks include too many workers/short intervals causing legitimate busy contention, option parsing defaults hiding invalid values, early worker messages before handler assignment, and first-worker unlink races if startup order changes. Passing signals are all workers loaded, periodic insert logs, retry logs only within expected contention, all workers finished, and no failed messages for tested VFS/iteration combinations.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/wasm/tests/opfs/concurrency/test.js -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/wasm/tests/opfs/concurrency/worker.js -->
# sources/storage-engines/sqlite/ext/wasm/tests/opfs/concurrency/worker.js

## Purpose
`tests/opfs/concurrency/worker.js` is the worker-side OPFS concurrency stress participant. Each worker opens the same database through either `OpfsDb` or `OpfsWlDb`, creates shared tables, then repeatedly writes its worker id and timestamp while retrying SQLITE_BUSY.

## Important APIs, Types, And Functions
It parses `workerId`, `opfs-unlock-asap`, `vfs`, `interval`, `iterations`, and `unlink-db` URL arguments. It imports sqlite3 from `sqlite3.dir` with a unique `opfs-async-proxy-id`, sets `sqlite3InitModule.__isUnderTest`, initializes sqlite3, and defines `wPost()`, `stdout()`, `stderr()`, `wait()`, `finish()`, `run()`, and `doWork()`.

## Control Flow
After initialization, it verifies the private `sqlite3.opfs` namespace, optionally unlinks `concurrency-tester.db`, posts `loaded`, and waits for a `run` message. `run()` chooses the DB constructor from `options.vfs`, loops on open while SQLITE_BUSY occurs, sets `sqlite3_busy_timeout`, creates tables inside `sqlite3_js_retry_busy`, then schedules interval work. Each interval inserts or replaces a row for the worker in table `t1`, using retry callbacks to log busy attempts. It finishes after `iterations` or failure.

## State And Persistence Behavior
Workers share `concurrency-tester.db` in OPFS. Each keeps its own DB handle, interval count, delay, and possible error. The DB is closed in `finish()`. Optional `opfs-unlock-asap` is propagated in the file URI to exercise lock-release behavior.

## Dependencies And Integration Points
It depends on Worker globals, generated sqlite3 JS, OPFS private test APIs, `sqlite3.oo1.OpfsDb`, `sqlite3.oo1.OpfsWlDb`, busy timeout/retry helpers, and the UI coordinator's message protocol. It requires unique async proxy ids so OPFS worker plumbing does not collide.

## Risks And Test Signals
Risks include invalid VFS names, indefinite busy-open loops under severe contention, private OPFS API changes, and missed `finish()` if asynchronous errors occur after scheduling. Good signals are `loaded`, successful constructor selection, bounded BUSY retry logs, exact requested interval count, successful close, and no `failed` messages across repeated multi-worker runs.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/wasm/tests/opfs/concurrency/worker.js -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/wasm/tests/opfs/sahpool/digest-worker.js -->
# sources/storage-engines/sqlite/ext/wasm/tests/opfs/sahpool/digest-worker.js

## Purpose
`tests/opfs/sahpool/digest-worker.js` is a worker used by the SAHPool digest test. It verifies that the OPFS SyncAccessHandle Pool VFS can reopen and distinguish persisted databases after the `computeDigest()` fix.

## Important APIs, Types, And Functions
It defines `wPost()`, `log()`, `hasOpfs()`, and `runTests(sqlite3, poolUtil)`. `hasOpfs()` checks browser OPFS and `createSyncAccessHandle` availability. The worker imports sqlite3 from the `sqlite3.dir` URL parameter, initializes the module, installs `sqlite3.installOpfsSAHPoolVfs()` with name `opfs-sahpool-digest`, `clearOnInit: false`, and `initialCapacity: 6`, then opens databases through `poolUtil.OpfsSAHPoolDb`.

## Control Flow
The worker first aborts if OPFS SAH prerequisites are missing. It imports sqlite3, logs version, installs/acquires the named SAHPool VFS, and runs three DB operations: create/insert/close `/my.db`, reopen `/my.db` and insert again, then create/insert `/my2.db`. It logs record counts to both console and parent.

## State And Persistence Behavior
SAHPool storage is intentionally not cleared on init, so `/my.db` and `/my2.db` may persist across runs depending on pool state. The test closes each DB promptly. It does not remove the VFS or unlink files, because the digest test is concerned with persistent identity and digest behavior.

## Dependencies And Integration Points
Dependencies are Worker globals, browser OPFS SAH support, generated sqlite3 JS, and `installOpfsSAHPoolVfs`. It integrates with a parent digest test page that handles `log` and `error` messages.

## Risks And Test Signals
Risks include environment lack of SAH, stale persistent pool contents affecting counts, missing cleanup causing cross-test interference, and install failures when another worker holds the same pool. Passing signals are `vfs acquired`, successful reopen of `/my.db`, increasing counts across reopen, separate count for `/my2.db`, and no OPFS-not-detected error.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/wasm/tests/opfs/sahpool/digest-worker.js -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/wasm/tests/opfs/sahpool/sahpool-pausing.js -->
# sources/storage-engines/sqlite/ext/wasm/tests/opfs/sahpool/sahpool-pausing.js

## Purpose
`tests/opfs/sahpool/sahpool-pausing.js` is the UI coordinator for demonstrating SAHPool VFS pause/unpause behavior across two workers. It sequences operations so one worker creates and pauses the VFS, then another worker acquires it and reads/removes it.

## Important APIs, Types, And Functions
The file defines UI logging (`mapToString`, `normalizeArgs`, `logClass`, `log`, `warn`, `error`), `toss()`, `endOfWork()`, a callback queue, `nextHandler()`, `postThen()`, `runPyramidOfDoom(W1,W2)`, and `runTests()`. `runPyramidOfDoom()` is the core sequence: W1 `vfs-acquire`, W1 `db-init`, W1 `db-query`, W1 `vfs-pause`, W2 `vfs-acquire`, W2 `db-query`, W2 `vfs-remove`.

## Control Flow
`runTests()` starts two `sahpool-worker.js` workers with distinct worker ids. It waits for both to report `initialized`, then runs the callback queue sequence. Incoming worker messages map to queue advancement, log rendering, final pass marking, or failure marking. The UI title and `#color-target` are updated on success/failure.

## State And Persistence Behavior
The coordinator stores only DOM log state, callback queue state, and worker handles. The database and VFS state live in the workers. The sequence depends on `pauseVfs()` unregistering the VFS from one worker while leaving pool contents available for another acquire/unpause path.

## Dependencies And Integration Points
It depends on a browser DOM with log controls and `sahpool-worker.js` in the same directory. It integrates with the worker protocol: `initialized`, `vfs-acquired`, `vfs-paused`, `vfs-unpaused`, `vfs-removed`, `db-inited`, `query-result`, `log`, and `error`.

## Risks And Test Signals
Risks include callback-queue deadlock if any worker message is missed, pass/fail being driven by message order rather than promises, OPFS SAH unavailability, and residual VFS state from prior failed runs. Passing signals are both workers initialized, W1 query returning rows, W1 paused, W2 acquired and queried the same data, VFS removed, and title/header marked PASS.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/wasm/tests/opfs/sahpool/sahpool-pausing.js -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/wasm/tests/opfs/sahpool/sahpool-worker.js -->
# sources/storage-engines/sqlite/ext/wasm/tests/opfs/sahpool/sahpool-worker.js

## Purpose
`tests/opfs/sahpool/sahpool-worker.js` is the worker counterpart for the SAHPool pausing demo. It imports sqlite3, optionally installs or unpauses a named SAHPool VFS, initializes/query/removes a small database, and reports each state transition to the coordinator.

## Important APIs, Types, And Functions
It parses `workerId` and `sqlite3.dir`, defines `wPost()` and `log()`, and stores `capi`, `wasm`, `S`, and `poolUtil`. `sahPoolConfig` names the VFS `opfs-sahpool-pausable` with `clearOnInit: false` and `initialCapacity: 3`. `sqlExec(sql)` opens `/my.db` with `poolUtil.OpfsSAHPoolDb`, executes SQL, returns results, and closes the DB. `onmessage` handles `vfs-acquire`, `db-init`, `db-query`, `vfs-remove`, and `vfs-pause`.

## Control Flow
The worker imports sqlite3, checks OPFS SAH prerequisites, initializes sqlite3, logs version/source id, and posts `initialized`. On `vfs-acquire`, it either installs the VFS or unpauses an existing `poolUtil`. `db-init` drops/creates/fills `mytable`. `db-query` returns ordered rows. `vfs-pause` calls `pauseVfs()` synchronously and reports paused. `vfs-remove` awaits `removeVfs()` and reports removed.

## State And Persistence Behavior
The named SAHPool VFS and `/my.db` persist inside the worker's pool utility until paused or removed. `clearOnInit: false` lets data survive across pause/unpause and between workers in the demo sequence. Each SQL operation opens and closes a short-lived DB handle, avoiding pause attempts while a DB is open.

## Dependencies And Integration Points
It depends on Worker globals, generated sqlite3 JS, OPFS SAH APIs, `installOpfsSAHPoolVfs`, and the coordinator's message protocol. It is tightly coupled to `sahpool-pausing.js` ordering and message names.

## Risks And Test Signals
Risks include missing OPFS, unhandled async rejection in VFS acquire/remove, attempting pause with open DBs if `sqlExec` changes, and stale pool state after failed runs. Passing signals are `initialized`, version log, `vfs-acquired`, `db-inited`, query result `[[11],[22],[33]]` style rows, `vfs-paused`, second-worker acquire/unpause, and final `vfs-removed`.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/wasm/tests/opfs/sahpool/sahpool-worker.js -->
