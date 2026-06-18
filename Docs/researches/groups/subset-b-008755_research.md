# subset-b-008755 research

Grouped research for SQLite WASM API bootstrapping, OPFS support, C API glue, and OO API files under `sources/storage-engines/sqlite/ext/wasm/api`. Each section is source-tree-aligned and delimited for reconciliation into per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/wasm/api/extern-post-js.c-pp.js -->
# sources/storage-engines/sqlite/ext/wasm/api/extern-post-js.c-pp.js

## Purpose

This extern post-JS fragment runs outside Emscripten's module initialization scope after the generated `sqlite3InitModule` has been defined. Its main job is to replace Emscripten's exported initializer with SQLite's public initializer: callers still invoke `sqlite3InitModule(...)`, but the resolved value is the `sqlite3` namespace rather than the raw Emscripten `Module` in normal builds.

## Important APIs and control flow

The file captures `originalInit = sqlite3InitModule`, creates `globalThis.sqlite3InitModuleState`, and installs a wrapper function `globalThis.sqlite3InitModule = function ff(...args)`. The state object records the current script, whether the environment is a worker, `location`, URL parameters, a build-substituted `wasmFilename`, optional debug logging, and script/sqlite3 directory hints. When the wrapper is called it preserves caller-supplied `locateFile` and `instantiateWasm` hooks in `sIMS`, calls `originalInit`, then invokes `EmscriptenModule.runSQLite3PostLoadInit(sIMS, EmscriptenModule, !!ff.__isUnderTest)`. That post-load function is supplied by the post-JS header/footer constellation and performs the real SQLite API bootstrap.

For non-ESM builds it rewrites CommonJS, AMD, and plain `exports` integration points to export the wrapper. For ESM builds it assigns `toExportForESM`, replaces `sqlite3InitModule`, and exports it as the module default. A wasmfs/PThread-specific branch returns the Emscripten module when called from generated pthread workers because those workers expect the raw module argument to flow through.

## State, persistence, dependencies, and risks

The key state is transient global initialization metadata. It is intentionally stored on `globalThis` because Emscripten currently prevents attaching it directly to the generated initializer in the needed way. `pre-js.c-pp.js` consumes and deletes this state. URL parameters such as `sqlite3.debugModule` and `sqlite3.dir` influence logging and resource location, and the build system must replace `@sqlite3.wasm@` with the actual wasm filename.

Dependencies include Emscripten's generated `sqlite3InitModule`, `Module.runSQLite3PostLoadInit`, browser globals, module-system globals, and build preprocessor flags. Risks cluster around load order and bundling: if the generated initializer is missing, the file throws immediately; if current script or URL discovery fails, wasm location must fall back to `pre-js` logic or caller overrides; ESM/bundler handling is deliberately different to avoid breaking bundlers. Test signals include successful initializer replacement, correct debug-state transfer into `pre-js`, correct wasm lookup under script-tag, worker, and ESM builds, and expected return type for wasmfs pthread workers.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/wasm/api/extern-post-js.c-pp.js -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/wasm/api/extern-pre-js.js -->
# sources/storage-engines/sqlite/ext/wasm/api/extern-pre-js.js

## Purpose

This extern pre-JS file is intentionally minimal. It exists as the file passed to Emscripten's `--extern-pre-js` position and currently serves as a placeholder for snippets used during test and development.

## Important APIs and control flow

There is no runtime API, function definition, or mutable state in the current file. Its comments document placement: it is prepended to the generated `sqlite3.js` outside the main Emscripten module init scope, in contrast to `pre-js.c-pp.js`, which runs inside the generated initializer after `Module` exists.

## State, persistence, dependencies, and risks

Because this file contains only comments, it has no persistence or control-flow effect in production output. Its primary dependency is build-system convention: the file path must remain valid for build scripts that pass `--extern-pre-js`. The main risk is future maintenance confusion between `extern-pre-js.js` and `pre-js.c-pp.js`; code that needs access to Emscripten's `Module` must not be placed here unless the author deliberately wants global-scope execution before generated initialization. Test signals are mostly build-level: the file can be prepended without syntax changes and without changing generated module behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/wasm/api/extern-pre-js.js -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/wasm/api/opfs-common-inline.c-pp.js -->
# sources/storage-engines/sqlite/ext/wasm/api/opfs-common-inline.c-pp.js

## Purpose

This inline include defines `initS11n()`, the shared serialization helper used by OPFS VFS implementations and their async proxy side. It is inlined into each consumer because the async proxy does not load the full API library and because the function closes over a file-local `state` object with nearly identical shape in each OPFS implementation.

## Important APIs and control flow

`initS11n()` lazily initializes and returns `state.s11n`. It builds `TextEncoder`, `TextDecoder`, `Uint8Array`, and `DataView` views over `state.sabIO` at the serialization region described by `state.sabS11nOffset` and `state.sabS11nSize`. The serialization format is compact and single-record: byte 0 is argument count, the following bytes are type IDs, and the remaining bytes are packed data. Supported types are `number` as Float64, `bigint` as BigInt64, `boolean` as Int32, and UTF-8 strings with a 32-bit length prefix.

`state.s11n.serialize(...args)` writes the header, type IDs, and values into the shared buffer. Calling it with no arguments clears the buffer by zeroing the count byte. `state.s11n.deserialize(clear=false)` reads the most recent serialized record and returns an array or `null`; if `clear` is truthy it clears the buffer after reading. In `opfs-async-proxy` builds the helper also installs `state.s11n.storeException(priority, e)`, which conditionally serializes a compact exception message depending on `state.asyncS11nExceptions`.

## State, persistence, dependencies, and risks

The state is transient cross-thread call data in a `SharedArrayBuffer`; it is not persistent filesystem state. Only one serialized dataset exists at a time, so callers must follow the OPFS request/response protocol and avoid overlapping use of the serialization region. Endianness comes from `state.littleEndian`, and metrics counters are conditionally updated when `vfs.metrics.enable` is defined.

Dependencies include a surrounding `state`, optional `metrics`, `performance.now()`, `TextEncoder/TextDecoder`, `DataView` BigInt accessors, and a `toss()` helper. The risks are buffer overflow if future VFS operations exceed `sabS11nSize`, unsupported argument types, accidental concurrent records, and cross-browser BigInt/DataView behavior. Test signals should include round-tripping all supported primitive types, clearing behavior, exception serialization priority, non-ASCII strings, and the OPFS sanity check in `opfs-common-shared.c-pp.js` that serializes and deserializes a string containing `ä`.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/wasm/api/opfs-common-inline.c-pp.js -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/wasm/api/opfs-common-shared.c-pp.js -->
# sources/storage-engines/sqlite/ext/wasm/api/opfs-common-shared.c-pp.js

## Purpose

This browser-only initializer builds the internal `sqlite3.opfs` namespace shared by the `opfs` and `opfs-wl` VFS implementations. It supplies OPFS feature detection, utility filesystem operations, database import helpers, VFS option normalization, and the common synchronous-to-async bridge used to expose SQLite's synchronous VFS methods on top of OPFS APIs and a worker proxy.

## Important APIs and control flow

The initializer exits if OPFS VFS installation is disabled. It then creates `sqlite3.opfs` with utilities such as `thisThreadHasOPFS()`, `getRootDir()`, `getResolvedPath()`, `getDirForFilename()`, `mkdir()`, `entryExists()`, `randomFilename()`, `treeList()`, `rmfr()`, `unlink()`, and `traverse()`. `importDb()` writes a verified SQLite database image into OPFS, either from a byte array or from async chunks, truncating the target first and rewriting header bytes 18 and 19 to force rollback-journal mode instead of WAL.

`vfsInstallationFeatureCheck(vfsName)` enforces `SharedArrayBuffer`, `Atomics`, worker context, OPFS sync access handles, and `Atomics.waitAsync()` for `opfs-wl`. `initOptions(vfsName, options)` reads URL flags, sets verbosity and sanity-check options, derives the async proxy URI, and returns a normalized options object or falsy when installation should be skipped.

`createVfsState()` builds the central VFS state. It constructs `capi.sqlite3_vfs` and `capi.sqlite3_io_methods`, allocates the VFS name, creates metrics, shared file and serialization buffers, operation IDs, exported SQLite result/open/lock constants for the async proxy, and OPFS-specific flags. `opfsVfs.opRun(op, ...args)` serializes arguments, writes an operation ID into a shared Int32 buffer, notifies the async worker, blocks with `Atomics.wait()` until a result appears, logs serialized exceptions, and returns the SQLite result code.

The synchronous IO wrappers implement `xClose`, `xFileSize`, `xRead`, `xSync`, `xTruncate`, and `xWrite`; VFS wrappers implement `xAccess`, time methods, `xDelete`, `xFullPathname`, `xGetLastError`, and `xOpen`. `xOpen` parses URI flags such as `opfs-unlock-asap=1` and `delete-before-open=1`, allocates per-file tracking, forwards open to the async side, installs `sqlite3_file` methods, and records open files. `bindVfs(ioMethods, callback)` merges VFS-specific methods, starts `sqlite3-opfs-async-proxy.js`, transfers cloneable state, handles worker init messages, installs the VFS through `sqlite3.vfs.installVfs`, initializes serialization, optionally runs sanity checks, and resolves to `sqlite3`.

## State, persistence, dependencies, and risks

Persistent state lives in the browser origin's OPFS tree. The VFS bridge state itself is volatile: `SharedArrayBuffer` instances hold file I/O buffers, serialized arguments, return codes, and operation notifications; `__openFiles` maps SQLite file pointers to per-file metadata; metrics counters track operation time and wait time. `importDb()` directly persists bytes to OPFS and deletes partial files on many errors.

Dependencies include browser OPFS APIs, worker execution, cross-origin isolation for `SharedArrayBuffer`, `Atomics.wait()`, the async proxy script, `sqlite3.capi`, `sqlite3.wasm`, `sqlite3.vfs.installVfs`, and the inline serializer. Key risks are environment gating failures, worker script resolution/404 timeouts, deadlocks or spurious wakeups in wait/notify handling, stale file-pointer bookkeeping, lock contention across tabs, partial import cleanup, and undefined behavior when deleting files used by another instance. Test signals include feature-check outcomes, byte-for-byte import plus WAL-mode header rewrite, `treeList/traverse/unlink` behavior, VFS install success, the optional sanity test's access/open/sync/truncate/write/read/close/delete sequence, metrics dumps, and multi-tab lock-contention tests for both `opfs` and `opfs-wl`.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/wasm/api/opfs-common-shared.c-pp.js -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/wasm/api/post-js-footer.js -->
# sources/storage-engines/sqlite/ext/wasm/api/post-js-footer.js

## Purpose

This footer closes the `Module.runSQLite3PostLoadInit()` function opened by `post-js-header.js`. It assembles bootstrap configuration after the wasm module is loaded, calls `globalThis.sqlite3ApiBootstrap()`, deletes the bootstrap helper, and returns the promise that becomes the public `sqlite3InitModule()` result.

## Important APIs and control flow

The footer runs inside `Module.runSQLite3PostLoadInit(sqlite3InitScriptInfo, EmscriptenModule, sqlite3IsUnderTest)`, so those arguments and Emscripten-generated locals are in scope. It builds `bootstrapConfig` by combining the detected wasm memory and exports, `globalThis.sqlite3ApiBootstrap.defaultConfig`, and optional `globalThis.sqlite3ApiConfig`. Export detection handles newer Emscripten globals (`wasmExports`), module properties (`EmscriptenModule.wasmExports`), and older `EmscriptenModule.asm`.

After debug logging, it calls `globalThis.sqlite3ApiBootstrap(bootstrapConfig)`, deletes `globalThis.sqlite3ApiBootstrap`, and returns the resulting promise. Any exception is logged as a bootstrap error and rethrown.

## State, persistence, dependencies, and risks

The file mutates only bootstrap-time global state. No database persistence occurs here. It depends on the header-created function scope, Emscripten's wasm memory/export shape, `sqlite3ApiBootstrap.defaultConfig`, optional client config, and the initializer chain populated by earlier post-JS fragments.

Risks include Emscripten export-shape drift, clients supplying incompatible `sqlite3ApiConfig`, bootstrap deletion preventing later re-bootstrap attempts in the same JS realm, and errors in any initializer surfacing only after wasm load. Test signals include successful bootstrap under supported Emscripten versions, custom config merging, debug output when enabled, cleanup of `globalThis.sqlite3ApiBootstrap`, and rejection propagation when an initializer throws.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/wasm/api/post-js-footer.js -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/wasm/api/post-js-header.js -->
# sources/storage-engines/sqlite/ext/wasm/api/post-js-header.js

## Purpose

This header opens `Module.runSQLite3PostLoadInit()`, the intentionally verbose post-load entry point called by `extern-post-js.c-pp.js` after Emscripten has loaded the wasm module. It creates the scope into which the full SQLite JavaScript API constellation is concatenated.

## Important APIs and control flow

The file assigns `Module.runSQLite3PostLoadInit = async function(sqlite3InitScriptInfo, EmscriptenModule, sqlite3IsUnderTest) { ... }`. On entry it deletes `EmscriptenModule.runSQLite3PostLoadInit` to avoid exposing the hook after use. The opened function scope is then filled by the prologue, wasm utilities, struct binder, C API glue, OO API, worker API, VFS/vtab helpers, OPFS VFSes, and finally closed by `post-js-footer.js`.

The design explicitly avoids `Module.postRun` because its timing changed across Emscripten versions. The function name is deliberately unlikely to collide with Emscripten symbols.

## State, persistence, dependencies, and risks

This file creates bootstrap-time control state rather than database state. Its correctness depends on concatenation order: the footer must close the function, and all intermediate files must run in this scope after wasm load but before `sqlite3ApiBootstrap()` is called. It also depends on `extern-post-js.c-pp.js` invoking this function on the Emscripten module returned by the original initializer.

Risks are mostly build-order and integration risks: missing footer syntax would break the generated JS, `postRun`-like timing assumptions must not be reintroduced, and future Emscripten symbol collisions are mitigated only by naming. Test signals are parse success of the generated amalgam, one-shot deletion of the hook, correct visibility of `sqlite3InitScriptInfo` and `EmscriptenModule` to the footer, and successful bootstrap of downstream API initializers.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/wasm/api/post-js-header.js -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/wasm/api/pre-js.c-pp.js -->
# sources/storage-engines/sqlite/ext/wasm/api/pre-js.c-pp.js

## Purpose

This pre-JS fragment runs inside Emscripten's generated `sqlite3InitModule()` after `Module` exists but before Emscripten's main wasm-loading work. It customizes file location and, for supported builds, wasm instantiation so SQLite can reliably find the sidecar `.wasm` file across script-tag, worker, URL-parameter, and ESM scenarios.

## Important APIs and control flow

For non-bundler-friendly targets the file wraps its work in `(function(Module){ ... })(Module)`. It consumes `globalThis.sqlite3InitModuleState` from `extern-post-js.c-pp.js` or creates a diagnostic fallback, then deletes the global. It installs `Module.locateFile(path, prefix)` bound to that state. The resolver delegates to caller-provided `emscriptenLocateFile` when present, uses `new URL(path, import.meta.url).href` for ESM, or otherwise checks a URL parameter matching the resource name, `sqlite3Dir`, `scriptDir`, and finally `prefix + path`. Debug logging records the decision when `sqlite3.debugModule` is set.

When enabled by preprocessor flags, and not in wasmfs or node builds, it overrides `Module.instantiateWasm(imports, onSuccess)`. The override delegates to caller-provided `emscriptenInstantiateWasm` if present. Otherwise it resolves `sIMS.wasmFilename`, fetches it with same-origin credentials, uses `WebAssembly.instantiateStreaming()` when available, falls back to `arrayBuffer()` instantiation for older Safari, stores the instantiated metadata on `sIMS.instantiateWasm`, and calls Emscripten's `onSuccess(instance, module)`.

## State, persistence, dependencies, and risks

The primary state is initialization metadata and the installed `Module` hooks. No database persistence occurs. Dependencies include `globalThis.sqlite3InitModuleState`, `Module`, Emscripten's optional `scriptDirectory`, `fetch`, `WebAssembly.instantiateStreaming`, `import.meta.url` in ESM builds, and build-time preprocessor substitutions.

Risks include fragile resource-location heuristics, server MIME or credential issues for streaming wasm instantiation, unsupported node/bundler/wasmfs combinations, and caller override hooks being explicitly unsupported back doors that may break if Emscripten changes. Test signals include loading from a script tag, `importScripts()`/Worker contexts with `sqlite3.dir`, query-parameter overrides for the wasm filename, Safari fallback behavior, user-supplied `locateFile` and `instantiateWasm` hooks, and debug logs showing the resolved URI.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/wasm/api/pre-js.c-pp.js -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/wasm/api/sqlite3-api-glue.c-pp.js -->
# sources/storage-engines/sqlite/ext/wasm/api/sqlite3-api-glue.c-pp.js

## Purpose

This initializer is the core glue layer between the wasm exports, generic wasm utilities, the struct binder, and the public `sqlite3.capi`, `sqlite3.wasm`, and `sqlite3.util` surfaces. It installs typed wrappers for exported C APIs, imports constants and struct layouts from wasm, adds pointer and string adapters, implements hand-written wrappers for APIs needing JS-specific behavior, and extends struct-bound types with method installation helpers.

## Important APIs and control flow

The initializer first installs `WhWasmUtilInstaller(wasm)` and defines `bindingSignatures` for three groups: `core` C APIs, `int64` APIs requiring BigInt support, and `wasmInternal` helpers exposed under `sqlite3.util`. The core signatures cover statement binding/stepping, columns, hooks, open/close, config/status, result/value APIs, VFS registration, URI helpers, and more. Optional blocks add progress, explain, authorizer, column-origin, SEE encryption, virtual table, preupdate, and session/changeset APIs when the wasm exports and BigInt support are present.

It creates `sqlite3.StructBinder` from `Jaccwabyt`, then configures `wasm.xWrap` adapters. `string:flexible` accepts arrays and SQL-capable typed arrays; `string:static` allocates long-lived C strings for pointer subtype names; pointer aliases accept raw pointers and, for `sqlite3*` and `sqlite3_stmt*`, OO API `DB` and `Stmt` objects when available. `sqlite3_vfs*` can resolve VFS names via `sqlite3_vfs_find`. Result adapters alias typed pointers back to raw pointer values.

The wrapper generation loop binds `bindingSignatures.core` into `capi`, internal helpers into `util`, and BigInt-sensitive APIs either into real wrappers or throwing stubs. It then imports SQLite constants and struct metadata via `sqlite3__wasm_enum_json`, populates `capi.SQLITE_*` values, builds `capi.sqlite3_js_rc_str()`, binds struct types, nests virtual table inner structs under `sqlite3_index_info`, and defines `capi.sqlite3_vtab_config`.

Hand-written wrappers handle important semantic gaps. `util.sqlite3__wasm_db_error()` sets database error state from result codes or JS errors. `sqlite3_close_v2()` runs `__dbCleanupMap.cleanup()` before closing to uninstall auto-converted callbacks. Collation and scalar/window UDF wrappers enforce UTF-8, convert JS callbacks to wasm function pointers, translate exceptions into SQLite errors, and register cleanup metadata. `sqlite3_prepare_v2/v3()` support JS strings, SQLable typed arrays, arrays, and raw SQL pointers with tail handling. `sqlite3_bind_text/blob()` accept JS strings and typed arrays by allocating wasm memory and using `SQLITE_WASM_DEALLOC`. Text-return proxies preserve embedded NULs for `sqlite3_column_text()` and `sqlite3_value_text()`. `sqlite3_config()` exposes a bounded subset of config operations. Auto-extension wrappers install and later uninstall JS function pointers.

Finally, it adds `installMethod()` and `installMethods()` to `StructBinder.StructType.prototype` for installing JS or wasm-pointer callbacks into struct function-pointer members, with disposal-time cleanup for installed proxies.

## State, persistence, dependencies, and risks

Most state is runtime binding state: C constants, struct constructors, wrapper functions, static string allocations, callback function-table entries, `__dbCleanupMap`, and auto-extension pointer sets. Persistent database state is affected indirectly through exposed C APIs, UDFs, collations, hooks, sessions, and VFS operations. Memory ownership is critical: static strings intentionally leak for application lifetime, bind wrappers pass allocated buffers to SQLite with `SQLITE_WASM_DEALLOC`, and callback wrappers must be uninstalled on close or reset where possible.

Dependencies include wasm exports, Emscripten function tables, BigInt support, `WhWasmUtilInstaller`, `Jaccwabyt`, `sqlite3__wasm_enum_json`, SQLite compile options, and optional exported APIs. Risks include callback leaks when clients bypass `capi.sqlite3_close_v2()` and call raw wasm close exports, unsupported non-UTF-8 encodings, BigInt-disabled stubs in untested builds, allocator mismatch around serialize/deserialize APIs in custom builds, function-table behavior differences in Safari, and subtle typed-array/string conversion bugs. A concrete maintenance hazard is the `sqlite3_bind_text()` branch that references `pMem` in an `Array.isArray(pMem)` check even though the parameter is named `text`; tests should cover array input or the branch should be reviewed.

Test signals should include wrapper availability matching exports, constant/struct import sanity, UDF/collation creation and cleanup on close, hook callback argument conversion, prepare tail handling for multi-statement SQL, typed-array SQL and bind inputs, embedded-NUL text reads, BigInt integer paths, auto-extension reset cleanup, VFS method installation disposal, and optional API gates for SEE, vtab, preupdate, and session builds.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/wasm/api/sqlite3-api-glue.c-pp.js -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/wasm/api/sqlite3-api-oo1.c-pp.js -->
# sources/storage-engines/sqlite/ext/wasm/api/sqlite3-api-oo1.c-pp.js

## Purpose

This initializer installs the same-thread object-oriented SQLite API as `sqlite3.oo1`. It wraps `sqlite3*` handles with `DB` objects and `sqlite3_stmt*` handles with `Stmt` objects, providing ergonomic open/close, prepare, exec, bind, row retrieval, transaction, savepoint, UDF, and handle-wrapping operations on top of the C API glue.

## Important APIs and control flow

The initializer maintains private ownership state in `WeakMap` and `Set` instances: `__ptrMap` hides raw pointers behind read-only `pointer` accessors; `__doesNotOwnHandle` tracks non-owning wrappers; `__stmtMap` tracks statements owned by each DB. `DB.checkRc()` throws `SQLite3Error` from SQLite result codes and error messages. A trace callback is installed in the wasm function table for DBs opened with the `t` flag. `dbCtorHelper()` normalizes constructor arguments, opens databases with `sqlite3_open_v2()`, enables extended result codes, optionally installs SQL tracing, applies SEE keys in SEE builds, and runs VFS post-open callbacks registered by VFS implementations.

`DB` supports constructor forms using positional arguments or an options object. Open flags are represented as letters: `c` create/read-write, `w` read-write, implicit read-only otherwise, and `t` tracing. `DB.prototype.close()` invokes optional `onclose` callbacks, finalizes tracked statements, removes pointer bookkeeping, and closes the underlying handle unless it is a non-owning wrapper. Other DB methods include `changes()`, `dbFilename()`, `dbName()`, `dbVfsName()`, `prepare()`, `exec()`, `createFunction()`, `selectValue(s)`, `selectArray(s)`, `selectObject(s)`, `openStatementCount()`, `transaction()`, `savepoint()`, and `checkRc()`. `DB.wrapHandle()` creates an OO wrapper around an existing `sqlite3*`, optionally taking ownership.

`DB.exec()` is the largest control-flow path. It parses SQL and options, allocates a scoped SQL buffer plus statement and tail pointers, loops through all statements with `sqlite3_prepare_v3()`, optionally saves SQL text, binds one value to the first parameterized statement, steps non-result statements once, and for the first result-producing statement can collect column names, invoke callbacks, fill `resultRows`, and honor row modes (`array`, `object`, `stmt`, column index, or `$columnName`). It resets before finalizing to surface `INSERT ... RETURNING` errors.

`Stmt` objects are created only by `DB.prepare()` or `Stmt.wrapHandle()`. Statement methods include `finalize()`, `clearBindings()`, `reset()`, `bind()`, `bindAsBlob()`, `step()`, `stepReset()`, `stepFinalize()`, `get()`, typed getters, `getJSON()`, column-name helpers, parameter-name/index helpers, `isBusy()`, and `isReadOnly()`. Binding supports null/undefined, numbers, BigInt when available, booleans, strings, arrays, named-parameter objects, `ArrayBuffer`, `Uint8Array`, and `Int8Array`. Retrieval converts SQLite NULL, integer, float, text, and blob values to JS values, using BigInt only outside JS safe integer range when available.

`createFunction()` accepts scalar, aggregate, and window UDF definitions, derives arity from callback length unless specified, applies deterministic/directOnly/innocuous flags, validates `pApp` and `xDestroy`, and calls the C API wrappers from `sqlite3-api-glue.c-pp.js`.

## State, persistence, dependencies, and risks

Persistent state is SQLite database content managed by the selected VFS. Runtime state includes DB/Stmt pointer ownership, tracked statements, exec locks, get-permission tracking after successful `step()`, VFS post-open callbacks, optional SEE key state, and blob transfer buffers used by the worker API. The API deliberately does not rely on garbage collection for native cleanup; callers must close DBs and finalize statements, though DB close finalizes tracked statements.

Dependencies include `sqlite3.capi`, `sqlite3.wasm`, utility type predicates, BigInt support, optional SEE exports, VFS helper `sqlite3_js_db_vfs`, and C API wrappers for UDF/collation cleanup. Risks include stale non-owning wrappers if the underlying handle is closed elsewhere, leaked handles when clients forget `close()`/`finalize()`, callback misuse in `exec({rowMode:'stmt'})`, SQL buffer tail-loop correctness, BigInt precision behavior, duplicate result-column names overwriting object fields, and transaction rollback behavior if rollback itself fails. The preprocessor-disabled experimental `forEachStmt()` block contains apparent typos (`callaback`, inconsistent SQL variable use), but it is behind `#if 0` and not part of normal output.

Test signals should cover constructor modes and VFS selection, post-open callbacks, close finalizing outstanding statements, non-owning wrap semantics, prepare of empty and invalid SQL, multi-statement `exec()` with bind/saveSql/columnNames/resultRows/callback combinations, row modes and duplicate column names, statement lock enforcement during callbacks, all bind and get type conversions, `INSERT ... RETURNING` reset error paths, scalar/aggregate/window UDFs, transactions and savepoints, BigInt-safe integer boundaries, blob transfer collection, and read-only/busy statement predicates.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/wasm/api/sqlite3-api-oo1.c-pp.js -->
