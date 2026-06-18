# subset-b-008756 Research

Grouped research for SQLite WASM API sources under `sources/storage-engines/sqlite/ext/wasm/api`.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/wasm/api/sqlite3-api-prologue.js -->
# sources/storage-engines/sqlite/ext/wasm/api/sqlite3-api-prologue.js

## Purpose
This file defines the one-time `globalThis.sqlite3ApiBootstrap()` entry point used by the generated SQLite WebAssembly JavaScript bundle. It builds the top-level `sqlite3` namespace, validates the WASM/environment configuration, seeds the C-style API namespace (`sqlite3.capi`), the WASM helper namespace (`sqlite3.wasm`), internal `sqlite3.util`, error classes, allocator wrappers, pseudo-stack helpers, and several JS convenience wrappers around C APIs. It also owns the initializer queues that later amalgamated fragments use to install OO APIs, VFSes, OPFS support, kvvfs, virtual table helpers, and worker APIs.

## Important APIs, Types, and Functions
`sqlite3ApiBootstrap(apiConfig)` is asynchronous and returns the initialized `sqlite3` namespace after synchronous initializers and `asyncPostInit()` complete. The config accepts delayed-function properties for `exports`, `memory`, `functionTable`, and `wasmfsOpfsDir`, supports allocator export names, logging functions, `bigIntEnabled`, and `disable.vfs` flags.

`SQLite3Error` and `WasmAllocError` are public exception types. `SQLite3Error.toss()` and `WasmAllocError.toss()` are expression-friendly throw helpers, and both attach SQLite-style result codes (`SQLITE_ERROR` and `SQLITE_NOMEM` respectively).

The file declares placeholders for wrapper APIs installed later by glue code: `sqlite3_bind_blob`, `sqlite3_bind_text`, `sqlite3_create_function_v2`, `sqlite3_create_function`, `sqlite3_create_window_function`, `sqlite3_prepare_v3`, `sqlite3_prepare_v2`, and `sqlite3_exec`. Its comments define the intended JS/WASM conversion semantics for those wrappers.

Directly implemented C-style helpers include `sqlite3_randomness()`, `sqlite3_wasmfs_opfs_dir()`, `sqlite3_wasmfs_filename_is_persistent()`, `sqlite3_js_db_uses_vfs()`, `sqlite3_js_vfs_list()`, `sqlite3_js_db_export()`, `sqlite3_js_db_vfs()`, `sqlite3_js_aggregate_context()`, `sqlite3_js_posix_create_file()`, deprecated `sqlite3_js_vfs_create_file()`, `sqlite3_js_sql_to_string()`, `sqlite3_db_config()`, `sqlite3_value_to_js()`, `sqlite3_values_to_js()`, `sqlite3_result_error_js()`, `sqlite3_result_js()`, `sqlite3_column_js()`, `sqlite3_preupdate_new_js()`, `sqlite3_preupdate_old_js()`, `sqlite3changeset_new_js()`, `sqlite3changeset_old_js()`, and `sqlite3_js_retry_busy()`.

The `wasm` namespace starts with `exports`, `memory`, `pointerSize`, `bigIntEnabled`, `functionTable`, `alloc`, `realloc`, `dealloc`, `allocFromTypedArray()`, `compileOptionUsed()`, and `pstack`. `pstack` exposes `restore`, `alloc`, `allocChunks`, `allocPtr`, `call`, and read-only `pointer`, `quota`, and `remaining` properties.

## Control Flow
The bootstrap function first short-circuits repeated calls by returning the previously initialized object and warning that later config and external initializers are ignored. On the first call it merges defaults with caller/global config, resolves delayed config properties, validates OPFS mount syntax, constructs `capi`, `wasm`, `util`, and error classes, then installs allocator wrappers around the configured exported malloc/free/realloc symbols.

It then installs early convenience functions that rely on WASM exports and helpers supplied by later glue. Synchronous fragments register callbacks in `sqlite3ApiBootstrap.initializers`; the bootstrap iterates that list in append order and passes each the partially built `sqlite3` object. After that, `asyncPostInit()` processes `initializersAsync`, deletes internal-only helpers outside test mode, stores script/instantiate metadata only in test mode, removes global/default config objects, deletes the bootstrap symbol, and resolves to the public `sqlite3` namespace with `asyncPostInit`, `scriptInfo`, and `emscripten` removed.

## State and Persistence Behavior
Persistent bootstrap state is intentionally narrow: `sqlite3ApiBootstrap.sqlite3` caches the first result, and the global bootstrap/config symbols are deleted after use to prevent configuration drift. `wasm.compileOptionUsed()` caches the all-options map for no-argument calls. `sqlite3_wasmfs_opfs_dir()` lazily detects and initializes WASMFS OPFS support once, then caches either the mount point or an empty string. `wasm.pstack` is transient stack-like WASM heap storage; callers must save and restore the pointer.

Database persistence is not implemented here directly, but this file exposes persistence-aware helpers. `sqlite3_js_db_export()` serializes a database into a `Uint8Array` using WASM heap pointers and frees SQLite-owned output with `sqlite3_free`. `sqlite3_wasmfs_filename_is_persistent()` reports whether a path falls under the configured WASMFS OPFS mount. `sqlite3_js_posix_create_file()` and deprecated `sqlite3_js_vfs_create_file()` import byte data into the active filesystem/VFS, allocating temporary WASM buffers for JS byte arrays.

## Dependencies and Integration Points
This file requires a WASM exports object with SQLite allocator exports, pstack exports, `sqlite3_libversion`, `sqlite3_randomness`, and later glue-provided symbols. It depends on `sqlite3-api-glue.c-pp.js`/`whwasmutil.js` style code to populate pointer utilities, heap views, `xWrap`, scoped allocation, string conversion, function table helpers, struct binders, and the many C API wrappers declared as placeholders.

The global initializer arrays are the central integration point for the rest of the amalgamation. VFS helpers, kvvfs, OO API, worker APIs, OPFS modules, and testing hooks all plug into this bootstrap through those queues. Script loading metadata from `post-js-header.js` may be attached as `sqlite3.scriptInfo` for async OPFS worker resolution before being removed from the final public object.

## Risks and Edge Cases
The bootstrap is single-use: later calls silently reuse the first environment except for a warning, so mismatched WASM/JS bundles or late config changes are not recoverable without reloading the JS realm. BigInt support controls int64 behavior; APIs such as `sqlite3_js_db_export()` throw without BigInt support.

Memory ownership is a major risk surface. Helpers allocate WASM memory for typed arrays, strings, output pointers, and SQL result values, and rely on correct destructor constants such as `SQLITE_WASM_DEALLOC` or explicit `wasm.dealloc()`/`sqlite3_free()`. Incorrect allocator selection via `useStdAlloc` or custom export names can break APIs such as serialize/deserialize.

`sqlite3_js_vfs_create_file()` is explicitly deprecated because its VFS usage can trigger debug-build assertions or C-level crashes. `sqlite3_js_sql_to_string()` appears to contain a source-level bug: it calls `flexibleString(v)` and compares `x===v`, but `v` is not defined in that scope; callers taking the non-string path would hit a `ReferenceError`. `sqlite3_result_js()` contains a typo in an error message ("Don't not") but the behavior is still to report an SQL error.

## Test Signals
Useful tests include bootstrapping with exported versus imported memory, missing allocator exports, invalid `wasmfsOpfsDir`, repeated bootstrap calls, BigInt disabled builds, `sqlite3_randomness()` with zero-length and large typed arrays, pstack save/restore under exceptions, `sqlite3_js_db_export()` for empty and non-empty schemas, `sqlite3_value_to_js()`/`sqlite3_result_js()` round trips for null/bool/int64/double/text/blob, `sqlite3_db_config()` variants, and exercising `sqlite3_js_sql_to_string()` with typed array and pointer inputs to catch the undefined-variable path.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/wasm/api/sqlite3-api-prologue.js -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/wasm/api/sqlite3-api-worker1.c-pp.js -->
# sources/storage-engines/sqlite/ext/wasm/api/sqlite3-api-worker1.c-pp.js

## Purpose
This file installs `sqlite3.initWorker1API()`, the initializer for SQLite WASM "Worker API #1". It exposes a small message-driven database API for Worker threads, implemented on top of `sqlite3.oo1.DB`, so main-window code can open databases, execute SQL, export database bytes, close handles, and inspect serializable configuration without directly sharing SQLite objects across thread boundaries.

## Important APIs, Types, and Functions
The public entry point is `sqlite3.initWorker1API()`. It must run in a Worker, must be called once per Worker, installs `globalThis.onmessage`, and posts `{type:'sqlite3-api', result:'worker1-ready'}` when initialized.

The message API supports `open`, `close`, `exec`, `export`, `config-get`, and a testing-only `toss`. Message envelopes may include `type`, `messageId`, `dbId`, and operation-specific `args`. Responses copy `messageId`, include a `dbId` when available, and place operation output under `result`. Errors are normalized to `{type:'error', result:{operation,message,errorClass,input,stack?}}`.

Internal state lives in `wState`: `dbList` tracks opened `DB` instances in least-recently-opened/default order, `idSeq` and `idMap` generate stable opaque database IDs per DB object, `xfer` accumulates transferable buffers for `postMessage`, and `dbs` maps IDs to live DB objects. `getDbId()`, `affirmDbOpen()`, `getMsgDb()`, and `getDefaultDbId()` implement ID lookup and default selection.

## Control Flow
When initialized, the code validates that it is running in a Worker, captures `sqlite3.oo1.DB`, defines state helpers, and assigns an async `onmessage` dispatcher. Each inbound `ev.data` is routed by `type` to a `wMsgHandler` method. The method returns a plain object or throws; the dispatcher wraps thrown errors, fills in the default DB ID if the request did not provide one, attaches timing fields (`workerReceivedTime`, `workerRespondTime`, `departureTime`), and posts the response with any accumulated transfer list.

`open` normalizes `args.filename` to `""` when absent, forwards `filename` and `vfs` to the DB constructor, stores the DB, returns the actual filename, new `dbId`, `db.dbVfsName()`, and a `persistent` boolean based on whether the DB uses the `opfs` VFS. `close` is idempotent for unknown/missing DB IDs and optionally unlinks the file through `sqlite3__wasm_vfs_unlink()` after closing. `exec` converts string args to `{sql}`, rejects `rowMode:'stmt'`, installs a callback proxy when `args.callback` is a string message type, optionally computes change counts and last insert rowid, and sends a sentinel callback row with `rowNumber:null` and `row:undefined`. `export` calls `sqlite3_js_db_export()` and transfers the resulting `Uint8Array` buffer. `config-get` returns `bigIntEnabled`, `sqlite3.version`, and `sqlite3_js_vfs_list()`.

## State and Persistence Behavior
Database lifetime is Worker-local. Multiple DBs may be open simultaneously, but all operations execute serially on the Worker event loop, and calls without `dbId` use the first open DB. IDs intentionally include random components because pointer values can be reused and separate Worker instances previously collided on generated IDs.

Persistence depends on the selected VFS and filename. This file does not implement storage itself; it delegates to `oo1.DB`, `sqlite3_js_db_uses_vfs()`, `sqlite3_js_db_export()`, and VFS unlink helpers. `close({unlink:true})` deletes the backing file only if there was a known filename and VFS pointer. `export` returns a snapshot byte array and marks its buffer as transferable to avoid copying.

## Dependencies and Integration Points
The file is compiled only when OO API #1 is not omitted. It requires `sqlite3.util`, `sqlite3.oo1.DB`, `sqlite3.capi.sqlite3_js_db_uses_vfs`, `sqlite3.capi.sqlite3_js_vfs_list`, `sqlite3.capi.sqlite3_js_db_export`, `sqlite3.capi.sqlite3_last_insert_rowid`, and internal WASM utility functions `sqlite3__wasm_db_vfs` and `sqlite3__wasm_vfs_unlink`.

Its primary client-facing integration is `sqlite3-worker1-promiser.js`, which wraps the message protocol in Promises and reduces ordering hazards. Row streaming integrates with `postMessage()` by treating a string `callback` option as a message type for row events. Blob transfer optimization is coordinated through `db._blobXfer`, which the OO API can populate during result creation.

## Risks and Edge Cases
The API is intentionally minimal and not safe for recursive use from row callbacks; a nested `exec` waits behind the current `exec` because the Worker thread is occupied. Message ordering can also be surprising: many messages can queue before an `open` failure is known, causing later operations to fail.

Defaulting to the first opened DB is convenient but can mask missing or stale `dbId`s in multi-DB clients. `close` treats an unknown DB as a no-op, so a client may believe it closed or unlinked a database when no live DB matched. `exec` mutates the input options object for results and callback restoration; structured-cloned inputs avoid sharing with the sender, but tests should still treat the response object as modified options, not a separate result envelope.

`persistent` currently checks only the `opfs` VFS, so other persistent VFSes may not be reflected. `lastInsertRowId` returns whatever `sqlite3_last_insert_rowid()` reports after all SQL statements, even if no INSERT occurred. BigInt-related change counts or row IDs can throw in builds without BigInt support.

## Test Signals
Test from an actual Worker and verify the ready message, rejection when called on the main thread, `open` with memory and named VFS databases, default DB routing, unknown `dbId` errors for operations requiring a DB, idempotent close, unlink behavior, row callback streaming including the final sentinel, `countChanges` 32-bit and 64-bit modes, `lastInsertRowId`, export transferability, `config-get` VFS listing, error envelope stack capture, and queued-message behavior when `open` fails with `simulateError`.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/wasm/api/sqlite3-api-worker1.c-pp.js -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/wasm/api/sqlite3-license-version-header.js -->
# sources/storage-engines/sqlite/ext/wasm/api/sqlite3-license-version-header.js

## Purpose
This small preserved header documents licensing for the generated SQLite WebAssembly/JavaScript bundle, typically distributed as `sqlite3.js` or `sqlite3.mjs`. It is intended to survive minification or bundling via `/* @preserve */`.

## Important APIs, Types, and Functions
There are no executable APIs, types, functions, exports, or imports. The file is a comment-only source fragment.

## Control Flow
No runtime control flow exists. During amalgamation/build, the header is prepended to or included in the generated JS bundle so downstream users see the combined licensing notice.

## State and Persistence Behavior
The file holds no runtime state and performs no persistence. Its only durable effect is textual: it records that the bundle combines Emscripten glue code under MIT and University of Illinois/NCSA terms with SQLite-originated code/documentation under SQLite's public-domain-style terms.

## Dependencies and Integration Points
The integration point is the build/amalgamation pipeline for SQLite's WASM JS deliverables. The `@preserve` marker is relevant to minifiers or bundlers that honor preservation comments.

## Risks and Edge Cases
Because it is comment-only, functional risk is low. The main risk is distribution/compliance drift if build tooling drops the preserved comment, if the bundle content changes without updating the notice, or if downstream packagers strip license comments.

## Test Signals
Build-output tests should assert that minified and non-minified `sqlite3.js`/`sqlite3.mjs` artifacts retain the preserved license header. Source scans can confirm no executable code is introduced into this fragment.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/wasm/api/sqlite3-license-version-header.js -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/wasm/api/sqlite3-opfs-async-proxy.c-pp.js -->
# sources/storage-engines/sqlite/ext/wasm/api/sqlite3-opfs-async-proxy.c-pp.js

## Purpose
This file is the Worker-side asynchronous proxy for SQLite's OPFS VFS implementations (`opfs` and `opfs-wl`). The synchronous SQLite/WASM VFS half cannot directly await browser OPFS operations, so it communicates with this Worker using `postMessage`, `SharedArrayBuffer`, serialized arguments, and `Atomics`. The proxy translates SQLite VFS-style operations into Origin Private File System directory/file/sync-access-handle calls and reports SQLite result codes back through shared memory.

## Important APIs, Types, and Functions
The script expects a `vfs` URL parameter (`opfs` or `opfs-wl`) and posts availability/load/init messages such as `opfs-unavailable`, `opfs-async-loaded`, and `opfs-async-inited`. `installAsyncProxy()` owns setup after feature detection. `state` is populated by an `opfs-async-init` message and carries SQLite result codes, operation IDs, OPFS flags, shared buffers, serializer state, verbosity, idle wait timing, and root OPFS directory handle.

Key helpers include `getResolvedPath()`, `getDirForFilename()`, `closeSyncHandle()`, `closeSyncHandleNoThrow()`, `releaseImplicitLocks()`, `releaseImplicitLock()`, `getSyncHandle()`, `storeAndNotify()`, and `affirmNotRO()`. `GetSyncHandleError` wraps browser errors from `createSyncAccessHandle()` and `convertRc()` maps lock/not-found failures to SQLite codes such as `SQLITE_BUSY` or `SQLITE_CANTOPEN`.

`vfsAsyncImpls` implements the proxied operations: `opfs-async-shutdown`, `mkdir`, `xAccess`, `xClose`, `xDelete`, `xDeleteNoWait`, `xFileSize`, `xOpen`, `xRead`, `xSync`, `xTruncate`, `xWrite`, and VFS-specific `xLock`/`xUnlock` variants. The `opfs-wl` path uses `navigator.locks` Web Locks plus sync access handles; the legacy `opfs` path uses sync access handle ownership as the lock.

## Control Flow
At load time the script validates that it is not on the main thread and that `SharedArrayBuffer`, `Atomics`, OPFS handles, and `createSyncAccessHandle()` are available. `opfs-wl` additionally requires `Atomics.waitAsync`. If requirements are met, `navigator.storage.getDirectory()` resolves the OPFS root, the Worker posts `opfs-async-loaded`, and `onmessage` waits for `opfs-async-init`.

Initialization copies sync-side options into `state`, constructs typed views over `sabOP` and `sabIO`, validates that every async implementation has an operation ID, initializes the shared serializer from `opfs-common-inline.c-pp.js`, posts `opfs-async-inited`, and starts `waitLoop()`. `waitLoop()` waits for a non-zero operation ID in the shared op slot, clears it, deserializes arguments, dispatches to the corresponding async handler, and each handler eventually calls `storeAndNotify()` to place the SQLite result code in the shared `rc` slot and wake the synchronous side.

File operations look up metadata in `__openFiles` by opaque sqlite3_file pointer IDs. `xOpen` resolves/creates directories, optionally unlinks before open, creates a file handle, records read-only/delete-on-close/unlock policy metadata, and stores it by fid. `xRead` and `xWrite` move bytes through the shared file buffer view. Size, truncate, sync, and close operations use or release sync access handles as required. Idle waits release implicit locks to reduce cross-tab contention.

## State and Persistence Behavior
The real persistent data lives in OPFS. Worker state tracks open handles in `__openFiles`, implicit lock fids in `__implicitLocks`, and for Web Locks builds active locks in `__activeWebLocks`. Each open file record stores the absolute path, directory handle, file handle, shared byte buffer view, read-only flag, delete-on-close flag, current sync handle, and lock metadata.

Sync access handles are acquired lazily by `getSyncHandle()`. If an operation acquires a handle without an explicit SQLite lock, the fid is marked as implicitly locked and can be released during idle time or immediately when `OPFS_UNLOCK_ASAP` is active. Explicit Web Lock mode keeps the invariant that a held Web Lock also has a held sync access handle. `xClose` deletes files marked `SQLITE_OPEN_DELETEONCLOSE`, and `xDeleteNoWait` can recursively remove empty parent directories when invoked with the special sync flag `0x1234`.

## Dependencies and Integration Points
This Worker is not a public API and does not load SQLite JS/WASM directly. It relies on the synchronous OPFS VFS half (`sqlite3-vfs-opfs.js` style generated code) to provide shared buffers, operation IDs, SQLite constants, OPFS flags, serialized arguments, and retry/idle settings. It includes `opfs-common-inline.c-pp.js` under an `opfs-async-proxy` define for shared serialization logic.

Browser dependencies are strong: Worker context, OPFS (`navigator.storage.getDirectory` and file/directory handles), `FileSystemFileHandle.prototype.createSyncAccessHandle`, `SharedArrayBuffer`, `Atomics`, and optionally `Atomics.waitAsync`/`navigator.locks` for `opfs-wl`. Deployments need cross-origin isolation headers for shared memory.

## Risks and Edge Cases
The proxy is timing-sensitive. It relies on Atomics slots being cleared and notified in the right order; spurious wakeups are explicitly handled. OPFS sync access handle acquisition can fail due to cross-tab locks, deletion races, or browser-specific exception names. The retry loop maps known lock errors to `SQLITE_BUSY`, but some browser failures fall back to generic I/O codes.

Implicit lock retention improves benchmark performance but can worsen concurrency; `OPFS_UNLOCK_ASAP` trades performance for earlier release. Web Lock upgrades from shared to exclusive are not atomic, and the code carefully releases/reacquires to avoid deadlocks. `xAccess` cannot fully model SQLite xAccess semantics because OPFS lacks read-only and cheap lock-state checks. `Number(offset64)` and `Number(sz)` conversions assume offsets/sizes are within JS safe numeric range for practical OPFS use.

Shutdown/restart exists mainly for debugging. A fatal exception inside `waitLoop()` is logged but does not necessarily notify the synchronous side for the failed operation unless the handler already serialized a result.

## Test Signals
Coverage should include feature-detection failure messages, successful `opfs-async-init`, mkdir and nested xOpen creation, unlink-before-open, read short-fill behavior, write/truncate/sync/read-only failures, delete-on-close, recursive cleanup flag, implicit lock release timing, contention mapping to `SQLITE_BUSY`, NotFound mapping during handle acquisition, legacy `opfs` lock/unlock, Web Locks shared/exclusive/downgrade paths for `opfs-wl`, operation dispatch with both `Atomics.wait` and `Atomics.waitAsync`, and browser deployment with required COOP/COEP headers.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/wasm/api/sqlite3-opfs-async-proxy.c-pp.js -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/wasm/api/sqlite3-vfs-helper.c-pp.js -->
# sources/storage-engines/sqlite/ext/wasm/api/sqlite3-vfs-helper.c-pp.js

## Purpose
This file installs `sqlite3.vfs`, a small helper namespace for JavaScript implementations of `sqlite3_vfs` and `sqlite3_io_methods`. It reduces the boilerplate for binding JS methods into SQLite struct fields and registering a VFS with the core library.

## Important APIs, Types, and Functions
`capi.sqlite3_vfs.prototype.registerVfs(asDefault=false)` validates that `this` is a `sqlite3_vfs` struct wrapper, calls `sqlite3_vfs_register()`, verifies `sqlite3_vfs_find(this.$zName)` returns the same pointer, and returns the struct wrapper on success.

`sqlite3.vfs.installVfs(opt)` accepts an object with optional `io` and `vfs` entries. Each entry contains a StructBinder struct wrapper and a map of JS methods. It calls `struct.installMethods(methods, applyArgcCheck)` for each entry. For a `vfs` entry it also fills `$zName` from `name` when needed, arranges that allocated name string for disposal via `addOnDispose()`, and registers the VFS with optional `asDefault`.

## Control Flow
The file adds one synchronous bootstrap initializer. During bootstrap it captures `sqlite3.wasm`, `sqlite3.capi`, and `sqlite3.util.toss3`, creates a null-prototype `sqlite3.vfs` namespace, extends the `sqlite3_vfs` prototype, and defines `installVfs()`.

`installVfs()` loops over `['io','vfs']`, installs methods for each present entry, handles VFS name allocation and registration for the `vfs` entry, tracks whether any work was done, and throws if neither `io` nor `vfs` was provided.

## State and Persistence Behavior
The helper itself stores only the `sqlite3.vfs` namespace and prototype method. Persistent process state changes occur when `registerVfs()` calls into SQLite's VFS registry. If `installVfs()` allocates a C string for a VFS name, that pointer is attached to the struct's disposal list so it lives as long as the struct wrapper.

## Dependencies and Integration Points
This file depends on the bootstrap-created `sqlite3.capi`, `sqlite3.wasm`, `sqlite3.util`, StructBinder-generated struct wrappers, `sqlite3_vfs_register()`, `sqlite3_vfs_find()`, and each struct wrapper's `installMethods()`, `memberSignature()`, and disposal machinery.

It is used by VFS implementations that need to bind JavaScript callbacks to SQLite's C VFS structs. It is a convenience layer over lower-level StructBinder and C API calls; it does not implement file storage itself.

## Risks and Edge Cases
The helper assumes the caller has already populated struct fields other than methods and optional `$zName`. Registering a malformed VFS can still fail inside SQLite or produce broken runtime behavior. The post-registration pointer check catches name/registry mismatches but not semantic bugs in the method implementations.

If callers allocate structs and then dispose them while SQLite may still call the registered VFS, dangling function pointers or freed name strings are possible. `applyArgcCheck` can detect wrong JavaScript callback arity when requested, but disabling it may hide signature drift.

## Test Signals
Tests should register a minimal VFS with explicit `$zName`, register with `name` requiring C-string allocation, verify `asDefault` behavior, ensure `installVfs({})` throws, ensure non-`sqlite3_vfs` receivers for `registerVfs()` throw, verify `sqlite3_vfs_find()` returns the registered pointer, and run method callbacks with and without argument-count checks.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/wasm/api/sqlite3-vfs-helper.c-pp.js -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/wasm/api/sqlite3-vfs-kvvfs.c-pp.js -->
# sources/storage-engines/sqlite/ext/wasm/api/sqlite3-vfs-kvvfs.c-pp.js

## Purpose
This file installs the JavaScript side of SQLite's `kvvfs` key/value VFS. The native `os_kv.c` and `sqlite3-wasm.c` pieces provide the SQLite VFS and encoding primitives; this file replaces selected record, VFS, and I/O methods so database pages and metadata can be stored in JavaScript `Storage`-like objects such as `localStorage`, `sessionStorage`, or transient in-memory stores. Version 2 adds named transient storage objects, import/export, listeners, and Worker-thread availability for the `sqlite3.kvvfs` interface.

## Important APIs, Types, and Functions
The initializer exits if `sqlite3.config.disable?.vfs?.kvvfs` is set or if `sqlite3_vfs_find("kvvfs")` fails. It consumes and deletes JS plumbing structs `capi.sqlite3_kvvfs_methods` and `capi.KVVfsFile`, then wraps the native singleton returned by `sqlite3__wasm_kvvfs_methods()`.

`KVVfsStorage` implements the Storage interface over a prototype-less object with `key()`, `getItem()`, `setItem()`, `removeItem()`, `clear()`, and `length`. `cache` holds regexes, common C strings (`jrnl`, `sz`), key size, reusable WASM page encode/decode buffers, `storagePool`, builtin storage names, and last-error state. `newStorageObj()`, `installStorageAndJournal()`, `deleteStorage()`, `validateStorageName()`, `storageForZClass()`, `zKeyForStorage()`, and `jsKeyForStorage()` manage storage records and kvvfs key naming.

The low-level override groups are `methodOverrides.recordHandler` (`xRcrdRead`, `xRcrdWrite`, `xRcrdDelete`), `methodOverrides.vfs` (`xOpen`, `xDelete`, `xAccess`, `xRandomness`, `xGetLastError`), `methodOverrides.ioDb` (`xClose`, `xFileControl`, `xSync`, plus disabled debug read/write wrappers), and `methodOverrides.ioJrnl` (mostly copies DB methods). Original native callbacks are retained in `originalMethods` and called where JS only augments behavior.

Public v2 APIs are attached under `sqlite3.kvvfs`: `reserve`, `import`, `export`, `unlink`, `listen`, `unlisten`, `exists`, `estimateSize`, and `clear`. Main-thread Storage builds also expose v1-compatible `capi.sqlite3_js_kvvfs_size()` and `capi.sqlite3_js_kvvfs_clear()`. When OO API #1 is present, `sqlite3.oo1.JsStorageDb` is installed as a DB subclass/wrapper that forces `vfs:'kvvfs'` and validates storage names.

In test builds with vtab support, `sqlite3.kvvfs.create_module()` registers an eponymous inspection virtual table exposing storage name, refcount, open count, transient flag, and db size.

## Control Flow
During bootstrap the file builds the cache, installs builtin storage objects (`.` always, plus `local`/`session` if available), adds `-journal` aliases to the same storage objects, and installs JS function pointers over native struct fields with `wasm.installFunction()`. It disposes the temporary struct wrappers after patching the underlying native structs.

At runtime, `xOpen` validates or synthesizes a storage name, rejects database names ending in `-journal`, creates storage on `SQLITE_OPEN_CREATE`, maps the database and journal name to one shared storage object, increments refcounts for existing storage, wraps the sqlite3_file pointer in `KVVfsFile`, records it in `pFileHandles`, sets output flags, and notifies listeners. `xClose` removes the file handle, decrements refcount, optionally deletes transient storage at refcount zero, calls the original native close, disposes the wrapper, and emits close events.

Record reads and writes are the actual key/value bridge. `xRcrdRead` finds a Storage object by zClass, maps zKey into the correct JS key, reads an ASCII kvvfs-encoded string, copies it through a reusable WASM buffer into the caller buffer, and returns size/status conventions expected by `os_kv.c`. `xRcrdWrite` converts the C string to JS text, stores it, and notifies listeners. `xRcrdDelete` removes the key and notifies listeners. `xGetLastError` pops cached JS exceptions into SQLite's error buffer.

The high-level export path walks matching Storage keys, extracts `sz`, optional `jrnl`, and page records, optionally decodes page strings to `Uint8Array`s using `sqlite3__wasm_kvvfs_decode`, sorts numeric page keys, and returns a JSON-friendly object. Import validates the export object, creates or clears a storage object, writes size/journal/page records, encoding raw `Uint8Array` pages through `sqlite3__wasm_kvvfs_encode`, and installs new storage aliases on success.

## State and Persistence Behavior
`local` and `session` storage names map to browser `localStorage` and `sessionStorage` when available and use keys prefixed as `kvvfs-local-` or `kvvfs-session-` for v1 compatibility and coexistence with unrelated client keys. Other storage names use transient `KVVfsStorage` instances with shorter keys (`sz`, `jrnl`, page numbers). The special `.` storage is a per-thread transient store and is the default fallback for `JsStorageDb` when `sessionStorage` is absent.

Storage objects are reference counted and keep a `files` list so DB and journal handles share the same backing store and so transient stores are not deleted while open. `reserve()` increments or creates storage to keep it alive, `unlink()` decrements/removes non-builtin transient storage when safe, and `deleteAtRefc0` supports delete-on-close semantics. `clear()` wipes matching keys and refuses to clear in-use non-local/session storage.

Listeners are stored per storage object and receive asynchronous `open`, `close`, `write`, `delete`, and `sync` events. Write listeners may request decoded page bytes. Listener exceptions are caught and warned, not propagated into SQLite calls.

## Dependencies and Integration Points
This file depends on native kvvfs structs/functions exposed through `sqlite3-wasm.c`: `sqlite3__wasm_kvvfs_methods()`, `sqlite3__wasm_kvvfs_decode`, `sqlite3__wasm_kvvfs_encode`, and `sqlite3__wasm_kvvfsMakeKey`. It depends on StructBinder wrappers for `sqlite3_vfs`, `sqlite3_io_methods`, `sqlite3_kvvfs_methods`, and `KVVfsFile`, plus WASM helpers for C strings, heap access, function installation, scoped allocation, pointer reads/writes, and pstack.

It integrates with browser `Storage`, the OO `DB` constructor via `JsStorageDb`, the SQLite VFS registry via the preexisting `kvvfs` VFS, `sqlite3_file_control()`/PRAGMA handling, optional virtual table helpers for tests, and the bootstrap `disable.vfs.kvvfs` configuration.

## Risks and Edge Cases
The file documents that kvvfs is for small databases that fit within Web Storage limits, roughly a few megabytes, and is malloc/conversion heavy. Browser storage quotas, synchronous localStorage/sessionStorage behavior, and per-entry overhead can cause failures outside SQLite's direct control.

Storage name validation is strict because native key buffers are fixed-size. Names cannot be empty, too long, contain control characters, or end in `-wal`/`-shm`; `-journal` is only accepted internally during open. `xAccess` intentionally uses behavior that appears inverted relative to the native implementation because it matches observed SQLite expectations; this deserves regression coverage.

The code works around a known corruption issue by intercepting `PRAGMA page_size` changes and effectively disabling page-size mutation before VACUUM. That avoids corruption but can surprise callers expecting page-size changes to take effect. `xRandomness` uses `Math.random()`, not cryptographic randomness. Reusable WASM buffers are intentionally leaked for VFS lifetime because SQLite VFS lacks a JS finalizer hook.

Import has an apparent bug-risk path: its `catch` clears existing storage on failure but does not rethrow the caught exception, so callers may receive success despite a failed import after cleanup. Event listener page decoding uses shared temporary buffers and async callback scheduling; listener code must not assume a stable object beyond copied data. Clearing local/session storage while a DB is open remains allowed for backwards compatibility even though it can disrupt active use.

## Test Signals
Tests should cover bootstrap with kvvfs disabled and unavailable, builtin storage discovery in main thread versus Worker, storage name validation boundaries, opening/closing DB and journal pairs, refcount and delete-on-close behavior, `reserve()`/`unlink()` lifecycle, v1 key compatibility for local/session, transient key format, record read/write/delete error codes, `xAccess` existence semantics, page-size PRAGMA interception, clear refusal for in-use transient storage, import/export with encoded and decoded pages, malformed import cleanup and exception behavior, listener events with and without journal/page decoding, `JsStorageDb` filename normalization, and the test-only virtual table when `sqlite3.__isUnderTest` and vtab support are present.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/wasm/api/sqlite3-vfs-kvvfs.c-pp.js -->
