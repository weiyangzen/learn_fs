# subset-b-008758 Research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/wasm/common/whwasmutil.js -->
# sources/storage-engines/sqlite/ext/wasm/common/whwasmutil.js

## Purpose

`whwasmutil.js` installs a browser-oriented utility layer for arbitrary WebAssembly modules, with SQLite WASM as a primary consumer. It intentionally overlaps with useful parts of Emscripten glue while staying usable outside Emscripten-generated environments. The installer attaches memory, pointer, string, allocation-scope, indirect-function-table, and C export wrapper helpers to a caller-supplied target object.

The file also exposes `WhWasmUtilInstaller.yawl()`, a small loader factory for instantiating a WASM module and optionally installing these utilities onto a target.

## Important APIs, Types, and Functions

- `globalThis.WhWasmUtilInstaller(target)`: main installer. It configures pointer representation, heap views, string helpers, function table helpers, allocation scopes, and export wrappers.
- `target.ptr`: read-only pointer helper object with `size`, `ir`, `null`, `coerce()`, `add()`, and `addn()`. It hides whether pointers are JS `Number` or `BigInt`.
- Heap accessors: `heap8()`, `heap8u()`, `heap16()`, `heap16u()`, `heap32()`, `heap32u()`, and `heapForSize()`. They refresh typed-array views after memory growth.
- Function table helpers: `functionTable()`, `functionEntry()`, `jsFuncToWasm()`, `installFunction()`, `scopedInstallFunction()`, and `uninstallFunction()`.
- Memory value helpers: `peek()`, `poke()`, pointer variants, numeric width variants, and deprecated Emscripten-style aliases.
- String helpers: `cstrlen()`, `cstrToJs()`, `jstrlen()`, `jstrcpy()`, `cstrncpy()`, `jstrToUintArray()`, `allocCString()`, and `scopedAllocCString()`.
- Scoped allocation helpers: `scopedAllocPush()`, `scopedAllocPop()`, `scopedAlloc()`, `scopedAllocCall()`, `allocPtr()`, `scopedAllocPtr()`, `allocMainArgv()`, `scopedAllocMainArgv()`, and `cArgvToJs()`.
- Export wrappers: `xGet()`, `xCall()`, `xWrap()`, `xCallWrapped()`, `xWrap.argAdapter()`, `xWrap.resultAdapter()`, and `xWrap.FuncPtrAdapter`.
- `WhWasmUtilInstaller.yawl(config)`: WASM loader using `WebAssembly.instantiateStreaming()` when available and falling back to `arrayBuffer()` instantiation.

## Control Flow

Installer startup first derives `bigIntEnabled`, pointer size, and pointer IR from explicit config or, if allocation is already available, a probe allocation. It replaces `pointerSize` and `pointerIR` with the read-only `target.ptr` facade. It then installs a lazy `exports` getter if `target.exports` is not already present, creates the internal `cache`, and registers heap, function-table, memory, string, allocation, and wrapper helpers on `target`.

Heap access flows through `heapWrappers()`, which caches typed-array views over `WebAssembly.Memory.buffer` and rebuilds them when the buffer grows. Function installation uses the indirect function table, preferring reuse of indexes from `cache.freeFuncIndexes`, growing the table when needed, and compiling plain JS functions into tiny one-function WASM modules through `jsFuncToWasm()`.

`xWrap()` is the higher-level binding path. It resolves a WASM export, JS function, or indirect function pointer, validates arity and adapters, pushes a scoped allocation frame, converts arguments, calls the underlying function, converts the result, and finally pops the allocation frame so transient C strings and scoped function pointers are cleaned up.

`yawl()` returns a loader function. On load completion it installs `module`, `instance`, memory, and optional malloc/free wrappers onto `config.wasmUtilTarget`, runs `WhWasmUtilInstaller()` on that target, calls `config.onload`, and resolves with the load result plus `config`.

## State and Persistence

All runtime state is held in the closure-local `cache`: heap typed arrays, heap size, `WebAssembly.Memory`, reusable function table indexes, scoped allocation stacks, UTF-8 encoder/decoder, and `xWrap` adapter maps. It does not persist browser storage or files. It does manage WASM heap and indirect-function-table lifetime, so cleanup correctness depends on clients matching `alloc` with `dealloc`, `installFunction` with `uninstallFunction`, and `scopedAllocPush` with `scopedAllocPop`.

## Dependencies and Integration Points

The code depends on browser-level `TextEncoder`, `TextDecoder`, `WebAssembly.Memory`, `WebAssembly.Table`, `WebAssembly.Module`, `WebAssembly.Instance`, `fetch`, and optionally `BigInt64Array`/`BigUint64Array`. The target object must expose `exports` or `instance.exports`, and most allocation APIs require `alloc()` and `dealloc()` with malloc/free semantics. SQLite integrates this layer as `sqlite3.wasm`, using `xWrap()` for C API bindings, `allocMainArgv()` for shell-like `main()` calls, and `FuncPtrAdapter` for callback-function pointer bindings.

## Risks and Edge Cases

- BigInt handling must match the compiled WASM module. Enabling BigInt in JS is not enough if the module lacks 64-bit integration.
- `peek()` and `poke()` coerce BigInt pointers to `Number` for typed-array indexing, so impossible or out-of-browser-range addresses can misbehave.
- `cstrncpy()` has a likely typo in the negative-length path: it refers to `strPtr` instead of `srcPtr`.
- Function table growth can fail if the table is not growable, for example in Emscripten builds without table growth.
- `scopedAllocPop()` decides whether a scoped pointer is a function pointer by checking `functionEntry(p)`. A heap pointer value colliding with a live function table index would be ambiguous, though typical address spaces make that unlikely.
- `xWrap()` is intentionally strict about arity. This catches binding mistakes but can reject exotic JS functions whose `length` does not reflect intended callable arity.

## Test Signals

Useful tests should cover 32-bit and 64-bit pointer modes, heap growth invalidating cached views, UTF-8 round trips including multibyte and empty strings, allocation-scope cleanup on exceptions, table slot reuse after `uninstallFunction()`, `FuncPtrAdapter` modes, and `xWrap()` conversions for string, JSON, pointer, numeric, and deallocating result adapters. SQLite's worker and fiddle demos exercise many of these paths indirectly through `xWrap()`, shell startup, callback handling, and database export/import.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/wasm/common/whwasmutil.js -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/wasm/config.make.in -->
# sources/storage-engines/sqlite/ext/wasm/config.make.in

## Purpose

`config.make.in` is a tiny configure-generated Makefile fragment for the SQLite WASM extension build. The top-level configure script substitutes tool paths into this template to produce `config.make`.

## Important APIs, Types, and Functions

This is make configuration rather than executable code. It defines:

- `bin.bash = @BIN_BASH@`
- `bin.emcc = @EMCC_WRAPPER@`
- `bin.wasm-strip = @BIN_WASM_STRIP@`
- `bin.wasm-opt = @BIN_WASM_OPT@`
- `SHELL = $(bin.bash)`

The commented-out override block is a local testing aid for Makefile validation and conditional branches.

## Control Flow

The configure phase replaces `@...@` tokens with discovered or configured executable paths. The generated `config.make` is then included by WASM build makefiles so they can invoke Bash, Emscripten, wasm-strip, and wasm-opt consistently.

## State and Persistence

The file itself has no runtime state. The generated `config.make` persists build configuration choices for a checkout or build directory until configure is rerun.

## Dependencies and Integration Points

It integrates the top-level SQLite configure script with the `ext/wasm` Makefile layer. It assumes configure has resolved the Bash path, an Emscripten compiler wrapper, and optional WebAssembly optimization/stripping tools.

## Risks and Edge Cases

- Empty substitutions can lead to later build failures unless downstream make logic validates them.
- `SHELL` is explicitly bound to `$(bin.bash)`, so an incorrect Bash path affects all shell command execution in included makefiles.
- The commented testing overrides can be useful locally but would break real builds if uncommented and committed.

## Test Signals

Build tests should verify that configure generates non-empty paths for required tools in normal WASM builds, that optional tool absence is handled by downstream logic, and that make targets fail clearly when `bin.bash` or `bin.emcc` is invalid.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/wasm/config.make.in -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/wasm/demo-123.js -->
# sources/storage-engines/sqlite/ext/wasm/demo-123.js

## Purpose

`demo-123.js` is a basic demonstration of SQLite's WASM OO API #1. It can run in the main browser thread or a worker thread and shows database creation, SQL execution, prepared statements, result row modes, scalar UDF registration, transactions, savepoints, and explicit cleanup.

## Important APIs, Types, and Functions

- `logHtml()`, `log()`, `warn()`, and `error()`: output abstraction. The main thread writes DOM nodes; the worker posts `type: "log"` messages.
- `demo1(sqlite3)`: main demonstration routine.
- `sqlite3.capi`: C-style API access, used for version/source ID output.
- `sqlite3.oo1.DB`: high-level database wrapper. The demo opens `new oo.DB("/mydb.sqlite3", "ct")`.
- `db.exec()`: demonstrated with SQL strings, option objects, bind arrays, named bind objects, callbacks, `resultRows`, `columnNames`, and multiple row modes.
- `db.prepare()`, `Stmt.bind()`, `Stmt.step()`, `Stmt.reset()`, `Stmt.stepReset()`, and `Stmt.finalize()`.
- `db.createFunction()`: registers a scalar UDF named `twice`.
- `db.transaction()` and `db.savepoint()`: demonstrate rollback through thrown `sqlite3.SQLite3Error`.

## Control Flow

The script first detects whether it is running on the window or worker global object and installs the correct logging path. In worker mode it may import `sqlite3.js` after honoring a `sqlite3.dir` query parameter. It calls `sqlite3InitModule({print, printErr})`, then executes `demo1(sqlite3)` once initialization resolves.

Inside `demo1()`, the code opens a transient database, creates a table, inserts rows through `exec()` and a prepared statement, queries through all supported row modes, collects results without a callback, creates and exercises a UDF, checks expected UDF argument-count failure, demonstrates transaction rollback, demonstrates nested savepoint rollback, and closes the database in `finally`.

## State and Persistence

The database filename is `/mydb.sqlite3` with flags `"ct"`, meaning a create/truncate style transient database in the active VFS. It is closed at the end. Prepared statement lifetime is explicitly managed with `try/finally` and `finalize()`. The script intentionally warns users not to rely on garbage collection for DB or statement cleanup.

## Dependencies and Integration Points

The script requires `sqlite3InitModule` and the SQLite WASM build. In the main thread it expects DOM access for logging; in worker mode it expects the embedding page to handle posted log messages. It integrates with Emscripten-style `print` and `printErr` module options for stdout/stderr routing.

## Risks and Edge Cases

- If run in a worker from a different directory than `sqlite3.js`, callers must pass `sqlite3.dir` or WASM resolution can fail.
- Errors in the expected rollback/UDF-failure paths are swallowed only if they are `sqlite3.SQLite3Error`; other exceptions are rethrown.
- The demo is not a persistence test. The database is closed and intended as transient demonstration state.
- DOM logging assumes `document.body` exists in main-thread mode.

## Test Signals

The demo's own observable signals are successful log output for version, inserts, query rows in each row mode, expected UDF arity exception, expected transaction rollback count, expected nested savepoint rollback count, and final close without leaked statements. A harness can run it in both main-thread and worker modes to verify loader and logging paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/wasm/demo-123.js -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/wasm/demo-jsstorage.js -->
# sources/storage-engines/sqlite/ext/wasm/demo-jsstorage.js

## Purpose

`demo-jsstorage.js` is a main-thread test/demo for SQLite WASM builds with `kvvfs` support. It exercises `sqlite3.oo1.JsStorageDb`, showing how a database can persist through browser `localStorage` or `sessionStorage`.

## Important APIs, Types, and Functions

- `runTests(sqlite3)`: initializes the module state, checks VFS support, opens a JS storage-backed database, and wires DOM controls.
- `capi.sqlite3_vfs_find()`: validates that SQLite is initialized and that the `kvvfs` VFS is available.
- `new oo.JsStorageDb(dbStorage)`: opens a DB backed by `localStorage` or `sessionStorage`.
- `db.storageSize()` and `db.clearStorage()`: report and clear storage used by the backing VFS.
- `db.exec()` and `db.selectValue()`: initialize and query the demo table.
- DOM buttons: `#btn-clear-storage`, `#btn-clear-log`, `#btn-init-db`, `#btn-select1`, and `#btn-storage-size`.

## Control Flow

After `sqlite3InitModule(globalThis.sqlite3TestModule)` resolves, `runTests()` validates `kvvfs`, chooses `local` storage by default, creates the `JsStorageDb`, and attaches button handlers. The init button drops and recreates table `t`, inserts three time-derived integers, and logs saved SQL. The select button prints sorted rows. On startup, the script checks `sqlite_master`; if the database already has schema entries it reports previous-session data and triggers a select.

## State and Persistence

The key state is the browser storage backing `kvvfs`. With the current `dbStorage = "local"` choice, data persists across page reloads and browser restarts subject to browser storage policy. Switching to `"session"` would scope data to the tab/session. The code exposes clear and size operations so test runs can reset storage.

## Dependencies and Integration Points

The script must run in the main JS thread because it uses `document`, browser storage APIs, and the `kvvfs` implementation. It requires `sqlite3.js` to be loaded before the script and requires `SqliteTestUtil` for assertions. The page must provide the expected output element and buttons.

## Risks and Edge Cases

- The script exits early if the build lacks `kvvfs`.
- Browser storage quotas, privacy modes, or disabled storage can affect persistence and storage-size results.
- The selected storage backend is hard-coded with a ternary-like `0 ? "session" : "local"` pattern, so tests may need source modification to cover session storage.
- `saveSql` and `theStore` are logged for debugging but not otherwise validated.

## Test Signals

Expected signals include successful `sqlite3_vfs_find(null)`, presence of `kvvfs`, non-throwing `JsStorageDb` construction, a meaningful `storageSize()` value, successful table initialization, repeatable select output, visible previous-session data on reload, and clear-storage reducing/removing entries.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/wasm/demo-jsstorage.js -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/wasm/demo-worker1-promiser.c-pp.js -->
# sources/storage-engines/sqlite/ext/wasm/demo-worker1-promiser.c-pp.js

## Purpose

`demo-worker1-promiser.c-pp.js` demonstrates the Promise-based `sqlite3` Worker API #1 promiser wrapper. It exercises worker message types through `await` and promise chaining instead of manually managing `postMessage()` response queues.

## Important APIs, Types, and Functions

- `promiserFactory`: imported as an ES module in module builds or read from `globalThis.sqlite3Worker1Promiser.v2` in non-module builds.
- `promiserConfig`: configures optional `onready`, debug routing, `onunhandled`, and `onerror`.
- `workerPromise`: the resolved promiser function used to send worker commands.
- `wtest(msgType, msgArgs, callback)`: helper that sends a worker request and optionally validates the result.
- Worker message types: `config-get`, `open`, `exec`, `export`, and `close`.
- Test utilities: `globalThis.SqliteTestUtil` assertion counter and `sqlite3TestModule.setStatus(null)` for hiding loading UI.

## Control Flow

The script awaits `promiserFactory(promiserConfig)`, hides the loading spinner, then starts `runTests()`. It first requests `config-get` and records whether BigInt support is enabled. It opens `/testing2.sqlite3`, records the returned `dbId` into `promiserConfig`, then runs a sequence of `exec()` tests that create data, query in array/object/scalar row modes, intentionally trigger a SQL error, receive callback rows from the worker, test multi-statement result selection, delete rows, count rows, export the database, and close it twice.

The helper `wtest()` supports both `{type,args}` call style and the older two-argument style behind a disabled branch. Every callback validation is chained through promises, and many validations call `testCount()` in `finally`.

## State and Persistence

The database is worker-owned and identified by the `dbId` returned from `open`. The demo uses `/testing2.sqlite3`, then closes it at the end. It transfers data back during `export` as a `Uint8Array`, but it does not persist exported data in browser storage. The promiser config retains `dbId` after open so subsequent calls target the same DB.

## Dependencies and Integration Points

The code depends on the generated worker promiser artifact under `jswasm/`, `SqliteTestUtil`, DOM element `#test-output`, and `sqlite3TestModule`. It tests the higher-level wrapper around `sqlite3-worker1.js`, so it is an integration test between the main UI thread, worker message protocol, SQLite OO API running in the worker, and structured-clone transfer of result data.

## Risks and Edge Cases

- The source is preprocessed by `c-pp`; ES module and non-module branches differ. A build-mode mismatch can break the import/global path.
- The test expects `lastInsertRowId` to be a BigInt and adapts `changeCount` checks based on worker config.
- Callback row tests rely on end-of-result-set notifications with `rowNumber === null`.
- `promiserConfig.dbId` is mutated after open. Concurrent tests sharing that config could target the wrong DB.
- The intentional SQL error must reject the promise without breaking later worker requests.

## Test Signals

Strong signals include successful promiser initialization, `config-get` returning a boolean `bigIntEnabled`, `open` returning `dbId`, `messageId`, and VFS name, correct insert/change/last-row-id metadata, expected query rows and column names, caught intentional error, callback row counters reaching expected values, exported byte array larger than a minimal SQLite database, correct MIME type, and idempotent close behavior where the second close lacks a filename.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/wasm/demo-worker1-promiser.c-pp.js -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/wasm/demo-worker1.js -->
# sources/storage-engines/sqlite/ext/wasm/demo-worker1.js

## Purpose

`demo-worker1.js` is a lower-level demonstration and test script for `sqlite3-worker1.js`. Unlike the promiser demo, it shows the raw message-passing mechanics needed to coordinate worker requests and asynchronous responses.

## Important APIs, Types, and Functions

- `SW = new Worker("jswasm/sqlite3-worker1.js")`: worker instance under test.
- `DbState.id`: records the active database ID returned by `open`.
- `MsgHandlerQueue`: FIFO callback queue keyed by generated `messageId` values.
- `runOneTest(eventType, eventArgs, callback)`: constructs a worker message with type, args, dbId, messageId, and departure time.
- `dbMsgHandler`: handlers for `open`, `exec`, `export`, `error`, and callback row messages such as `resultRowTest1`.
- `runTests()` and `runTests2()`: open sequencing and post-open test sequence.
- `SW.onmessage`: central dispatcher for readiness, queued responses, error messages, and callback result rows.

## Control Flow

The script creates a worker immediately and waits for a `sqlite3-api` message with result `worker1-ready`. On readiness it clears the loading spinner and calls `runTests()`. `runTests()` posts an `open` command and, with `waitForOpen` enabled, delays `runTests2()` until the open callback has set the `dbId`.

`runTests2()` posts a fixed sequence of worker commands: create/insert, query arrays, query objects, intentional SQL error, follow-up query to prove queue recovery, callback-based row streaming, multi-statement row mode selection, delete, count, export, and two closes. Responses with `messageId` shift one callback off `MsgHandlerQueue`; errors with `messageId` route through `dbMsgHandler.error`.

## State and Persistence

Worker-side database state persists for the life of the worker and the open DB. Main-thread state is `DbState.id`, the message handler queue, counters inside callback functions, and visible log DOM nodes. The database filename is `testing2.sqlite3`; close commands use `{unlink:true}` to remove it at the end.

## Dependencies and Integration Points

The demo depends on `jswasm/sqlite3-worker1.js`, `SqliteTestUtil`, `sqlite3TestModule`, the browser Worker API, `performance.now()`, and a `#test-output` element. It directly validates the worker API contract: readiness message, db IDs, message IDs, callback names, exported database payload shape, and error routing.

## Risks and Edge Cases

- The FIFO queue assumes worker messages for queued commands arrive in the same order as posted. The comments call out that errors can otherwise disrupt queue handling.
- If `waitForOpen` is disabled and open fails, all queued post-open work can fail because the messages cannot be canceled after posting.
- Callback dispatch by string name requires the worker response to match keys in `dbMsgHandler`.
- The first close unlinks the database; the second close tests no-op behavior but can mask bugs if the first close did not actually release state.

## Test Signals

Expected signals include the `worker1-ready` startup event, `open` returning `testing2.sqlite3`, a populated `dbId`, expected rows and column names for array/object modes, a handled intentional error with queue recovery, `resultRowTest1.counter === 3`, exported `Uint8Array` with SQLite MIME type and nontrivial length, first close returning a filename, and second close returning no filename.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/wasm/demo-worker1.js -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/wasm/example_extra_init.c -->
# sources/storage-engines/sqlite/ext/wasm/example_extra_init.c

## Purpose

`example_extra_init.c` is a minimal example of the optional extra initialization hook for canonical SQLite WASM builds. If a file named `sqlite3_wasm_extra_init.c` is present in the main WASM build directory, the build arranges for SQLite to define `SQLITE_EXTRA_INIT=sqlite3_wasm_extra_init` and call it during `sqlite3_initialize()`.

## Important APIs, Types, and Functions

- `int sqlite3_wasm_extra_init(const char *z)`: required hook signature.
- `sqlite3.h`: included so the hook is compiled in the SQLite build context.
- `fprintf(stderr, "%s: %s()\n", __FILE__, __func__)`: observable example side effect.

## Control Flow

During SQLite initialization, the library calls `sqlite3_wasm_extra_init(NULL)` once. This example writes a diagnostic line to stderr and returns `0`, allowing initialization to continue. A nonzero return would make SQLite initialization fail.

## State and Persistence

The example maintains no state and makes no persistent changes. Its only side effect is stderr output during initialization.

## Dependencies and Integration Points

The hook integrates with SQLite's `SQLITE_EXTRA_INIT` mechanism and the WASM build system convention for detecting `sqlite3_wasm_extra_init.c`. It must be compiled into the SQLite WASM module. Stderr routing depends on the embedding module, usually Emscripten `printErr` or a worker stdout/stderr bridge.

## Risks and Edge Cases

- Returning nonzero from a real hook prevents SQLite initialization.
- Heavy work in this hook can affect every SQLite initialization path.
- Hook code must be valid in the WASM build environment and should avoid platform APIs unavailable under Emscripten or the target runtime.

## Test Signals

A build including this hook should emit one stderr line naming the file and function during `sqlite3_initialize()`, then continue to report successful SQLite startup. A negative test can return nonzero and assert that module initialization fails clearly.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/wasm/example_extra_init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/wasm/fiddle/fiddle-worker.js -->
# sources/storage-engines/sqlite/ext/wasm/fiddle/fiddle-worker.js

## Purpose

`fiddle-worker.js` is the worker-side controller for the SQLite WASM fiddle app. It loads the fiddle WASM module, runs the SQLite shell entry point, exposes shell execution to the main thread, and handles database reset, interrupt, export, and uploaded database open requests.

## Important APIs, Types, and Functions

- `wMsg(type, data, transferables)`: posts structured `{type,data}` messages back to the UI.
- `stdout()` and `stderr()`: route shell/module output to worker messages.
- `self.onerror`: detects fatal Emscripten `ExitStatus`, marks the module dead, and reports errors.
- `Sqlite3Shell.dbFilename()`, `dbHandle()`, `dbIsOpfs()`: wrappers around exported C helpers.
- `Sqlite3Shell.runMain()`: initializes the shell by calling `sqlite3_shutdown()`, building argv, and invoking `fiddle_main(argc, argv)`.
- `Sqlite3Shell.exec(sql)`: runs shell input through exported `fiddle_exec`, emits `working` start/end, and posts `wasm-info`.
- `Sqlite3Shell.resetDb()` and `interrupt()`: wrappers around exported reset/interrupt helpers.
- `self.onmessage`: dispatches `shellExec`, `db-reset`, `interrupt`, `db-export`, and `open`.
- `fiddleModule`: Emscripten module config with `print`, `printErr`, and `setStatus`.

## Control Flow

On load, the worker defines the message protocol and imports `fiddle-module.js` with the current query string. It calls `sqlite3InitModule(fiddleModule)`, stores the resolved `sqlite3` object globally for debugging, wires a filesystem unlink helper, and posts `fiddle-ready`.

The first shell execution lazily calls `runMain()`, which initializes the shell against `/fiddle.sqlite3` and posts version and welcome messages. Each subsequent `shellExec` runs through `fiddle_exec` unless the module is dead or another command is already running. After every command it posts heap/prompt info.

Database export fetches the current DB filename and handle, calls `sqlite3_js_db_export()`, and transfers the resulting `ArrayBuffer` to the main thread. Database open accepts an uploaded `ArrayBuffer` or `Uint8Array`, forces bytes 18 and 19 to `1` to disable WAL mode, sanitizes the filename, writes the file into the Emscripten FS, opens it through the shell, and unlinks the old file where possible.

## State and Persistence

State is worker-local: `sqlite3`, `fiddleModule.isDead`, cached `xWrap()` functions, shell argv, current shell DB, Emscripten virtual filesystem files, and transient `_running` flags. OPFS can provide persistent DB storage when opened with the OPFS VFS from the shell, but upload/export paths explicitly warn that OPFS-over-VFS has limitations. Uploaded DBs are copied into the virtual filesystem.

## Dependencies and Integration Points

The worker depends on generated `fiddle-module.js`, `sqlite3InitModule`, exported C symbols such as `fiddle_main`, `fiddle_exec`, `fiddle_db_filename`, `fiddle_db_handle`, `fiddle_reset_db`, and `fiddle_interrupt`, plus SQLite JS helpers such as `sqlite3_js_db_export()` and `sqlite3_js_db_uses_vfs()`. It integrates with the main-thread `fiddle.js` message handlers through message types documented at the top of the file.

## Risks and Edge Cases

- Interrupt cannot be effective while the worker is busy because the same worker event loop must receive the interrupt message.
- The upload path can temporarily hold both old and new DB files, risking quota failures.
- Forcing bytes 18 and 19 out of WAL mode is pragmatic but assumes the uploaded file is a SQLite database and mutable.
- Filename sanitization strips directories and replaces quotes/whitespace, but all opened files are still user-controlled content.
- There is a declared but unused `dbVfs` wrapper after initialization.
- OPFS limitations are surfaced as warnings but not fully prevented by the UI.

## Test Signals

Useful tests should observe `module` status messages, `fiddle-ready`, `sqlite-version`, shell stdout/stderr, `working` start/end around each command, `wasm-info` prompt/heap updates, successful `.help` or SQL execution, export with transferable buffer and SQLite MIME handling on the UI side, uploaded DB replacement, reset output, and fatal `ExitStatus` behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/wasm/fiddle/fiddle-worker.js -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/wasm/fiddle/fiddle.js -->
# sources/storage-engines/sqlite/ext/wasm/fiddle/fiddle.js

## Purpose

`fiddle.js` is the main-thread entry point for the SQLite WASM fiddle application. It sets up browser storage-backed UI configuration, creates the worker, dispatches worker messages, manages views, routes shell input/output, handles import/export controls, and optionally integrates `jquery.terminal`.

## Important APIs, Types, and Functions

- Internal `storage` module: wrapper around `localStorage`, `sessionStorage`, or a transient in-memory fallback with a per-app key prefix.
- `window.SqliteFiddle` / `SF`: main app object.
- `SF.config`: UI preferences such as auto-scroll, auto-clear, echo-to-console, side-by-side layout, and input/output swapping.
- `SF.echo()`: writes output to the textarea and optional terminal.
- `SF.addMsgHandler()`, `runMsgHandlers()`, `clearMsgHandlers()`, and `wMsg()`: worker message dispatch and send helpers.
- `SF.resetDb()`, `storeConfig()`, `setMainView()`, `toggleAbout()`, and `dbExec()`.
- `effectiveHeight()`, `debounce()`, and `SF.ForceResizeKludge()`: layout helpers.
- `self.onSFLoaded()`: delayed UI wiring after the worker reports readiness.

## Control Flow

The script initializes the storage wrapper, restores stored config into `SF.config`, starts `new Worker("fiddle-worker.js" + location.search)`, and wires message handlers for stdout/stderr, SQLite version, WASM info, module load status, and `fiddle-ready`. On `fiddle-ready`, it runs `onSFLoaded()`.

`onSFLoaded()` unhides the app, establishes the active view, wires reset/about/clear/execute buttons, maps Ctrl-Enter and Shift-Enter to shell execution, tracks working state for execute and interrupt buttons, binds checkboxes to CSS targets and persisted config, adds canned command buttons, wires database export/import controls, builds the examples dropdown, optionally initializes the terminal view, executes any `?sql=` URL parameter, enables resize handling, and exposes `globalThis.fiddle`.

Export disables mutating controls, asks the worker for `db-export`, builds a `Blob`, and auto-clicks a download link. Import reads a selected file as an `ArrayBuffer`, transfers it to the worker with an `open` message, and re-enables controls on load/error/abort.

## State and Persistence

Persistent UI state is stored under `sqlite3-fiddle-config` using the storage wrapper and a prefix derived from project config or `window.location.pathname`. If browser storage is unavailable, settings are transient. Runtime state includes `SF.worker`, handler maps, cached DOM references, output textarea content, terminal instance, active view, pending clear flag, and temporary object URLs for exports. Database state itself lives in the worker.

## Dependencies and Integration Points

The script depends on the DOM structure of the fiddle page, browser Worker/FileReader/Blob/ObjectURL APIs, optional `window.jQuery.terminal`, and `fiddle-worker.js` message types. It integrates with the worker protocol for `stdout`, `stderr`, `sqlite-version`, `wasm-info`, `module`, `fiddle-ready`, `working`, and `db-export`, and sends `shellExec`, `db-reset`, `interrupt`, `db-export`, and `open`.

## Risks and Edge Cases

- In the module status handler there is a typo-like check `f.ui.progres` while later code uses `f.ui.progress`, so progress value/max updates may never run.
- `preStartWork()` is called even when `dbExec(null)` is used at startup, which can briefly toggle working UI before the worker receives a no-op shell command.
- Import/export disabling is separate from shell `working` state and can race if operations overlap in unexpected order.
- Storage keys are origin scoped with a path/project prefix; multiple apps on the same origin can still coexist only if prefixes remain unique.
- Terminal integration modifies formatter behavior globally in `jquery.terminal`.
- The layout workaround manually sizes views and may need browser-specific testing.

## Test Signals

Tests should verify config restore/store, worker startup and `fiddle-ready`, module status visibility, stdout/stderr echo, version link generation, WASM info text and terminal prompt updates, Ctrl/Shift-Enter execution, selection-only execution, working state toggles, checkbox CSS/config sync, examples dropdown execution, export download object URL cleanup, file import transfer to worker, terminal mode toggle, and `?sql=` startup execution.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/wasm/fiddle/fiddle.js -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/wasm/jaccwabyt/jaccwabyt.js -->
# sources/storage-engines/sqlite/ext/wasm/jaccwabyt/jaccwabyt.js

## Purpose

`jaccwabyt.js` exposes `globalThis.Jaccwabyt`, a struct-binding factory for WASM memory. Given allocation functions, heap access, pointer settings, and struct descriptions, it generates JS constructor classes whose properties read and write native C struct fields through `DataView`.

SQLite uses this to bind C structs in its WASM layer, especially where JS needs structured access to memory layouts produced by C.

## Important APIs, Types, and Functions

- `StructBinderFactory(config)`: top-level factory. Validates `heap`, `alloc`, `dealloc`, optional `realloc`, pointer config, BigInt availability, and debug settings.
- Signature helpers: `isFuncSig()`, `isPtrSig()`, `sigLetter()`, `sigIR()`, `sigSize()`, `sigDVGetter()`, `sigDVSetter()`, and `sigDVSetWrapper()`.
- Instance handle storage: `getInstanceHandle()` uses a `WeakMap` to associate JS struct wrappers with pointer metadata.
- Lifetime helpers: `__allocStruct()`, `__freeStruct()`, `__addOnDispose()`, `__allocCString()`, and `__setMemberCString()`.
- `StructType`: base prototype for all generated struct wrappers. It provides `dispose()`, `lookupMember()`, `memberToJsString()`, `memberIsString()`, `memberKey()`, `memberKeys()`, `memberSignature()`, `memoryDump()`, `extraBytes`, `zeroOnDispose`, `pointer`, `setMemberCString()`, and `addOnDispose()`.
- Adapters: `StructBinder.adaptGet()`, `adaptSet()`, and `adaptStruct()` register reusable member/struct conversion proxies.
- `makeMemberStructWrapper()` and `makeMemberWrapper()`: generate property accessors for nested structs and scalar/pointer fields.
- `StructBinderImpl()` / `StructBinder()`: produce concrete struct constructors from struct descriptions.

## Control Flow

Factory initialization normalizes `config.heap` into a function returning a `Uint8Array`, validates allocation callbacks, determines pointer size and representation, sets up debug flags, and defines helper functions. Calling `StructBinder(name, structInfo)` creates a concrete constructor. The struct description is normalized, optional adapters are installed, offsets and sizes are validated or auto-calculated, and one accessor is generated per member.

Constructing a generated struct either wraps an external pointer or allocates new heap memory, optionally with extra bytes, ownership transfer, zero-on-dispose, and on-dispose callbacks. Reading a member creates a `DataView` over the current heap buffer at `this.pointer + offset`, calls the signature-specific getter, and applies optional getter proxies. Writing validates pointer/null/struct values as needed, applies optional setter proxies, coerces to `Number` or `BigInt`, and calls the signature-specific setter. Disposing runs on-dispose callbacks, clears optional memory, frees owned memory, and removes the weak-map handle.

Nested structs are represented by generated child constructors. Accessing a nested member returns a wrapper over the parent memory at the nested offset, caches it by parent pointer and member key, and arranges cleanup when the parent or child is disposed.

## State and Persistence

State is in closure-local config, debug flag objects, adapter weak maps, the instance handle `WeakMap`, and nested-struct caches. Native state lives in WASM heap memory allocated by `config.alloc` or externally supplied pointers. The library has no browser persistence. Memory ownership is explicit: generated instances either own allocated memory and free it on `dispose()`, or wrap external memory and leave freeing to the external owner unless ownership is transferred.

## Dependencies and Integration Points

The factory requires a WASM heap as `WebAssembly.Memory` or a heap-returning function, `alloc()` and `dealloc()`, and optionally `realloc()`, `log`, pointer size/IR, and BigInt support. It depends on `DataView`, `TextEncoder`, `TextDecoder`, `WeakMap`, `Map`, and optionally `BigInt64Array`. It is designed to pair with `whwasmutil`-style allocation and pointer helpers but can run with any compatible WASM environment.

## Risks and Edge Cases

- Struct descriptions must match the C ABI exactly unless `autoCalcSizeOffset` is being used for pure-JS/test structures. Incorrect offsets or sizes cause silent memory corruption or wrong reads before validation can catch all cases.
- `autoCalcSizeOffset` is explicitly dangerous for real C structs because JS cannot infer compiler padding and alignment.
- Pointer-size and BigInt configuration must match the compiled module.
- Property access after `dispose()` can fail or read invalid memory depending on the member path; setters explicitly reject disposed objects.
- On-dispose callbacks intentionally do not propagate exceptions, so cleanup failures are warnings rather than thrown failures.
- Nested struct caching keys combine pointer and property name. Reuse of native addresses after disposal can make cleanup discipline important.
- Signature/adaptor names are checked to avoid collisions with data type signatures, but misuse of custom adapters can still corrupt values.

## Test Signals

Tests should create generated structs with explicit offsets and with auto-calculated test layouts, read/write all scalar signatures, exercise 32-bit and 64-bit pointer modes, verify string allocation and `setMemberCString()` disposal, validate nested struct wrappers and cleanup, wrap external pointers with and without ownership transfer, test `extraBytes` and `zeroOnDispose`, confirm read-only setters throw, confirm invalid signatures and unaligned sizes throw, and verify debug flags do not alter behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/wasm/jaccwabyt/jaccwabyt.js -->
